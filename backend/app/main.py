import csv,io,json,time,uuid,os,secrets,urllib.parse
from contextlib import asynccontextmanager
from datetime import datetime,timedelta,timezone
import jwt,httpx
from fastapi import FastAPI,Depends,HTTPException,status,UploadFile,File,Form,Request
from fastapi.responses import FileResponse,Response
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from pydantic import BaseModel,Field
from sqlalchemy import select,func
from sqlalchemy.orm import Session
from .database import Base,engine,session
from .models import *
from .seed import bootstrap
from .config import settings
from .storage import storage
security=HTTPBearer(auto_error=False)
@asynccontextmanager
async def lifespan(app):
 with next(session()) as db: bootstrap(db)
 yield
app=FastAPI(title='海智产品中心正式版',version='1.0.0',lifespan=lifespan)
login_failures={}
@app.middleware('http')
async def security_headers(request:Request,call_next):
 response=await call_next(request)
 response.headers['X-Content-Type-Options']='nosniff'
 response.headers['X-Frame-Options']='SAMEORIGIN'
 response.headers['Referrer-Policy']='strict-origin-when-cross-origin'
 response.headers['Permissions-Policy']='camera=(), microphone=(), geolocation=()'
 response.headers['Content-Security-Policy']="default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'self'; base-uri 'self'; object-src 'none'"
 if request.url.path.startswith('/api/') or request.url.path.startswith('/v1/'):
  response.headers['Cache-Control']='no-store'
 return response
class Login(BaseModel): username:str;password:str
class ProductIn(BaseModel): name:str=Field(min_length=2);product_type:str='HARDWARE';model_code:str;category_id:int;summary:str='';status:str='ON_SALE';main_image:str=''
class ProductPatch(BaseModel): name:str|None=None;product_type:str|None=None;model_code:str|None=None;category_id:int|None=None;summary:str|None=None;status:str|None=None;main_image:str|None=None;dynamic_fields:dict[str,str]|None=None;data_status:str|None=None
class CatalogIn(BaseModel): name:str=Field(min_length=2);summary:str='';code:str='';version:str='v1.0';category:str='通用';software_type:str='PLATFORM';vendor:str='海智科技';deployment_mode:str='PRIVATE';supported_os:list[str]=[];scene_id:int|None=None;tier:str='标准型';status:str='SUPPORTED'
class CatalogPatch(BaseModel): name:str|None=None;summary:str|None=None;code:str|None=None;version:str|None=None;category:str|None=None;software_type:str|None=None;vendor:str|None=None;deployment_mode:str|None=None;supported_os:list[str]|None=None;scene_id:int|None=None;tier:str|None=None;status:str|None=None
class BomIn(BaseModel): scene:str=Field(min_length=2);upstream_km:float=Field(default=3,ge=0,le=1000);downstream_km:float=Field(default=3,ge=0,le=1000);ptz_count:int=Field(default=4,ge=0,le=1000);ais:bool=True;yaw:bool=True;ocr:bool=True;overheight:bool=False;vhf:bool=False
class ProjectIn(BaseModel): name:str;customer:str;region:str;scene_id:int;requirements_json:dict={};bom_json:list=[]
class ProjectPatch(BaseModel): name:str|None=None;customer:str|None=None;region:str|None=None;scene_id:int|None=None;requirements_json:dict|None=None;bom_json:list|None=None
class TenderIn(BaseModel): name:str=Field(min_length=2);customer:str=Field(min_length=2);deadline:datetime|None=None;status:str='PREPARING';summary:str=''
class TenderPatch(BaseModel): name:str|None=None;customer:str|None=None;deadline:datetime|None=None;status:str|None=None;summary:str|None=None
class GatewayChat(BaseModel): model:str;messages:list[dict];max_tokens:int=512
class EmbeddingIn(BaseModel): input:str|list[str];model:str='local-hash-embedding-v1'
class RagIn(BaseModel): text:str;document_id:int|None=None;metadata:dict={}
class RagSearch(BaseModel): query:str;limit:int=5
class TrainingCourseIn(BaseModel): external_course_id:str;name:str=Field(min_length=2);summary:str='';launch_url:str;status:str='ACTIVE'
def user(c:HTTPAuthorizationCredentials|None=Depends(security),db:Session=Depends(session)):
 if not c:raise HTTPException(401,'请先登录')
 try:data=jwt.decode(c.credentials,settings.jwt_secret,algorithms=['HS256'])
 except jwt.PyJWTError:raise HTTPException(401,'登录已失效')
 u=db.scalar(select(User).where(User.id==data['uid'],User.enabled==True))
 if not u:raise HTTPException(401,'用户不可用')
 return u
def permission_codes(u:User):
 normalized={link.permission.code for link in u.role.permission_links}
 return normalized or {code for code in u.role.permissions.split(',') if code}
def permit(code):
 def dep(u:User=Depends(user)):
  if code not in permission_codes(u):raise HTTPException(403,'缺少权限：'+code)
  return u
 return dep
def gateway_client(c:HTTPAuthorizationCredentials|None=Depends(security),db:Session=Depends(session)):
 if not c: raise HTTPException(401,'missing gateway credential')
 if settings.ai_gateway_api_key and secrets.compare_digest(c.credentials,settings.ai_gateway_api_key):
  service_user=db.scalar(select(User).join(Role).where(Role.code=='admin',User.enabled==True))
  if not service_user: raise HTTPException(503,'gateway service account unavailable')
  return service_user
 return user(c,db)
def dto(p):return {'id':p.id,'name':p.name,'productType':p.product_type,'modelCode':p.model_code,'categoryId':p.category_id,'category':p.category.name,'summary':p.summary,'status':p.status,'mainImage':p.main_image,'dataStatus':p.data_status,'updatedAt':p.updated_at.isoformat()}
def product_detail_dto(p,db):
 caps=db.scalars(select(Capability).join(ProductCapability,Capability.id==ProductCapability.capability_id).where(ProductCapability.product_id==p.id)).all()
 return dto(p)|{'dynamicFields':json.loads(p.dynamic_fields_json or '{}'),'capabilities':[{'id':c.id,'type':'model-capabilities','name':c.name,'category':c.category,'meta':c.category,'summary':c.description} for c in caps]}
def audit(db,u,action,resource_type,resource_id,detail=None):
 db.add(AuditLog(user_id=u.id,action=action,resource_type=resource_type,resource_id=str(resource_id),detail_json=json.dumps(detail or {},ensure_ascii=False)))
def normalize_chat_payload(payload):
 for choice in payload.get('choices',[]):
  message=choice.get('message') or {}
  if not message.get('content'):
   message['content']=message.get('reasoning_content') or message.get('reasoning') or ''
 return payload
@app.get('/api/health')
def health():return {'status':'ok','version':'1.0.0','runtime':'fastapi-postgresql'}
@app.get('/api/ai/gateway/health')
def gateway_health(u:User=Depends(user)): return {'status':'ok','provider':'governed-gateway','allowedModels':[settings.ai_model]}
@app.post('/api/ai/gateway/chat')
async def gateway_chat(x:GatewayChat,u:User=Depends(permit('AI_MANAGE')),db:Session=Depends(session)):
 if x.model != settings.ai_model: raise HTTPException(400,'模型未被治理网关允许')
 rid=uuid.uuid4().hex; started=time.time()
 try:
  async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as c:r=await c.post(settings.ai_base_url.rstrip('/')+'/v1/chat/completions',json=x.model_dump());r.raise_for_status(); payload=normalize_chat_payload(r.json())
  db.add(AiInteractionLog(request_id=rid,user_id=u.id,provider='governed-gateway',model_id=x.model,latency_ms=int((time.time()-started)*1000),success=True));db.commit();return payload|{'gatewayRequestId':rid}
 except Exception as e:
  db.add(AiInteractionLog(request_id=rid,user_id=u.id,provider='governed-gateway',model_id=x.model,latency_ms=int((time.time()-started)*1000),success=False,failure_reason=str(e)[:300]));db.commit();raise HTTPException(503,'AI网关上游不可用')
@app.post('/v1/chat/completions')
async def dify_compatible_chat(x:GatewayChat,u:User=Depends(gateway_client),db:Session=Depends(session)):
 if x.model != settings.ai_model: raise HTTPException(400,'model is not allowed')
 return await gateway_chat(x,u,db)
@app.get('/v1/models')
def dify_compatible_models(u:User=Depends(gateway_client)):
 return {'object':'list','data':[{'id':settings.ai_model,'object':'model','owned_by':'haizhi-governed-gateway'}]}
@app.post('/api/ai/embeddings')
def embeddings(x:EmbeddingIn,u:User=Depends(user)):
 values=[x.input] if isinstance(x.input,str) else x.input
 def vector(s):
  import hashlib
  raw=hashlib.sha256(s.encode()).digest(); return [round((b/255)*2-1,6) for b in raw[:32]]
 return {'object':'list','model':x.model,'data':[{'object':'embedding','index':i,'embedding':vector(v)} for i,v in enumerate(values)],'usage':{'prompt_tokens':sum(len(v) for v in values),'total_tokens':sum(len(v) for v in values)}}
def hash_vector(value):
 import hashlib
 return [(b/255)*2-1 for b in hashlib.sha256(value.encode()).digest()[:32]]
@app.post('/api/rag/chunks',status_code=201)
def create_rag_chunk(x:RagIn,db:Session=Depends(session),u:User=Depends(permit('DOCUMENT_EDIT'))):
 if x.document_id and not db.get(DocumentAsset,x.document_id): raise HTTPException(404,'文档不存在')
 rec=DocumentChunk(document_id=x.document_id,content=x.text,embedding_json=json.dumps(hash_vector(x.text)),metadata_json=json.dumps(x.metadata,ensure_ascii=False));db.add(rec);db.commit();db.refresh(rec);return {'id':rec.id,'documentId':rec.document_id}
@app.post('/api/rag/search')
def rag_search(x:RagSearch,db:Session=Depends(session),u:User=Depends(permit('DOCUMENT_VIEW'))):
 q=hash_vector(x.query)
 def score(row):
  v=json.loads(row.embedding_json); dot=sum(a*b for a,b in zip(q,v)); nq=sum(a*a for a in q)**.5; nv=sum(a*a for a in v)**.5; return dot/(nq*nv) if nq and nv else 0
 rows=list(db.scalars(select(DocumentChunk)))
 ranked=sorted(((score(r),r) for r in rows),key=lambda p:p[0],reverse=True)[:min(max(x.limit,1),20)]
 return [{'id':r.id,'documentId':r.document_id,'content':r.content,'score':round(s,6),'metadata':json.loads(r.metadata_json)} for s,r in ranked]
@app.get('/api/storage/health')
def storage_health(u:User=Depends(user)):
 try:
  storage.ensure_bucket(); return {'status':'ok','provider':'minio','bucket':storage.bucket}
 except Exception as e:
  raise HTTPException(503,'对象存储不可用') from e
@app.get('/api/documents')
def documents(db:Session=Depends(session),u:User=Depends(permit('DOCUMENT_VIEW'))):
 return [{'id':x.id,'name':x.name,'mimeType':x.mime_type,'path':x.path,'productId':x.product_id,'sceneId':x.scene_id,'tenderId':x.tender_id,'updatedAt':x.updated_at.isoformat()} for x in db.scalars(select(DocumentAsset).order_by(DocumentAsset.updated_at.desc()))]
@app.post('/api/documents',status_code=201)
async def upload_document(file:UploadFile=File(...),product_id:int|None=Form(None),scene_id:int|None=Form(None),tender_id:int|None=Form(None),db:Session=Depends(session),u:User=Depends(permit('DOCUMENT_EDIT'))):
 data=await file.read()
 if not data or len(data)>50*1024*1024: raise HTTPException(413,'文件为空或超过50MB')
 if product_id and not db.get(Product,product_id):raise HTTPException(422,'产品不存在')
 if scene_id and not db.get(Scene,scene_id):raise HTTPException(422,'场景不存在')
 if tender_id and not db.get(Tender,tender_id):raise HTTPException(422,'投标项目不存在')
 object_name=f'{uuid.uuid4().hex}-{os.path.basename(file.filename or "document")}'
 try: path=storage.put(object_name,data,file.content_type or 'application/octet-stream')
 except Exception as e: raise HTTPException(503,'对象存储不可用') from e
 rec=DocumentAsset(name=file.filename or object_name,path=path,mime_type=file.content_type or 'application/octet-stream',product_id=product_id,scene_id=scene_id,tender_id=tender_id);db.add(rec);db.flush();audit(db,u,'CREATE','document',rec.id,{'name':rec.name});db.commit();db.refresh(rec)
 return {'id':rec.id,'name':rec.name,'path':rec.path,'mimeType':rec.mime_type,'productId':rec.product_id,'sceneId':rec.scene_id,'tenderId':rec.tender_id}
@app.get('/api/documents/{did}/download')
def download_document(did:int,db:Session=Depends(session),u:User=Depends(permit('DOCUMENT_VIEW'))):
 rec=db.get(DocumentAsset,did)
 if not rec:raise HTTPException(404,'文件不存在')
 try:
  response=storage.get(rec.path.split('/',1)[1]);data=response.read();response.close();response.release_conn()
 except Exception as exc:raise HTTPException(503,'对象存储不可用') from exc
 return Response(data,media_type=rec.mime_type,headers={'Content-Disposition':f"attachment; filename*=UTF-8''{urllib.parse.quote(rec.name)}",'Cache-Control':'no-store'})
@app.delete('/api/documents/{did}',status_code=204)
def delete_document(did:int,db:Session=Depends(session),u:User=Depends(permit('DOCUMENT_EDIT'))):
 rec=db.get(DocumentAsset,did)
 if not rec:raise HTTPException(404,'文件不存在')
 try:storage.delete(rec.path.split('/',1)[1])
 except Exception as exc:raise HTTPException(503,'对象存储不可用') from exc
 db.query(DocumentChunk).filter(DocumentChunk.document_id==did).delete();audit(db,u,'DELETE','document',did,{'name':rec.name});db.delete(rec);db.commit()
@app.get('/api/tenders')
def tenders(db:Session=Depends(session),u:User=Depends(permit('TENDER_VIEW'))):
 return [{'id':x.id,'name':x.name,'customer':x.customer,'deadline':x.deadline.isoformat() if x.deadline else None,'status':x.status,'summary':x.summary,'documentCount':db.scalar(select(func.count(DocumentAsset.id)).where(DocumentAsset.tender_id==x.id)),'updatedAt':x.updated_at.isoformat()} for x in db.scalars(select(Tender).order_by(Tender.updated_at.desc()))]
@app.post('/api/tenders',status_code=201)
def create_tender(x:TenderIn,db:Session=Depends(session),u:User=Depends(permit('TENDER_EDIT'))):
 rec=Tender(**x.model_dump());db.add(rec);db.flush();audit(db,u,'CREATE','tender',rec.id,x.model_dump(mode='json'));db.commit();db.refresh(rec);return {'id':rec.id,'name':rec.name,'status':rec.status}
@app.get('/api/tenders/{tid}')
def tender_detail(tid:int,db:Session=Depends(session),u:User=Depends(permit('TENDER_VIEW'))):
 rec=db.get(Tender,tid)
 if not rec:raise HTTPException(404,'投标项目不存在')
 docs=db.scalars(select(DocumentAsset).where(DocumentAsset.tender_id==tid).order_by(DocumentAsset.updated_at.desc())).all()
 return {'id':rec.id,'name':rec.name,'customer':rec.customer,'deadline':rec.deadline.isoformat() if rec.deadline else None,'status':rec.status,'summary':rec.summary,'documents':[{'id':x.id,'name':x.name,'mimeType':x.mime_type} for x in docs]}
@app.patch('/api/tenders/{tid}')
def update_tender(tid:int,x:TenderPatch,db:Session=Depends(session),u:User=Depends(permit('TENDER_EDIT'))):
 rec=db.get(Tender,tid)
 if not rec:raise HTTPException(404,'投标项目不存在')
 values=x.model_dump(exclude_none=True)
 for key,value in values.items():setattr(rec,key,value)
 audit(db,u,'UPDATE','tender',tid,x.model_dump(exclude_none=True,mode='json'));db.commit();return {'id':rec.id,'name':rec.name,'status':rec.status}
@app.delete('/api/tenders/{tid}',status_code=204)
def delete_tender(tid:int,db:Session=Depends(session),u:User=Depends(permit('TENDER_EDIT'))):
 rec=db.get(Tender,tid)
 if not rec:raise HTTPException(404,'投标项目不存在')
 db.query(DocumentAsset).filter(DocumentAsset.tender_id==tid).update({'tender_id':None});audit(db,u,'DELETE','tender',tid,{'name':rec.name});db.delete(rec);db.commit()
@app.post('/api/auth/login')
def login(x:Login,request:Request,db:Session=Depends(session)):
 from .seed import pwd
 key=request.client.host if request.client else 'unknown';now=time.monotonic()
 attempts=[stamp for stamp in login_failures.get(key,[]) if now-stamp<300]
 if len(attempts)>=5:raise HTTPException(429,'登录失败次数过多，请稍后重试')
 u=db.scalar(select(User).where(User.username==x.username))
 if not u or not pwd.verify(x.password,u.password_hash):
  login_failures[key]=attempts+[now];raise HTTPException(401,'账号或密码错误')
 login_failures.pop(key,None)
 token=jwt.encode({'uid':u.id,'exp':datetime.now(timezone.utc)+timedelta(hours=8)},settings.jwt_secret,algorithm='HS256')
 return {'access_token':token,'user':{'username':u.username,'displayName':u.display_name,'role':u.role.code,'permissions':sorted(permission_codes(u))}}
@app.get('/api/auth/me')
def me(u:User=Depends(user)):return {'username':u.username,'displayName':u.display_name,'role':u.role.code,'permissions':sorted(permission_codes(u))}
@app.get('/api/dashboard')
def dashboard(u:User=Depends(user),db:Session=Depends(session)):
 return {'metrics':{'products':db.scalar(select(func.count(Product.id))),'algorithms':db.scalar(select(func.count(Algorithm.id))),'capabilities':db.scalar(select(func.count(Capability.id))),'scenes':db.scalar(select(func.count(Scene.id))),'solutions':db.scalar(select(func.count(Solution.id))),'projects':db.scalar(select(func.count(Project.id)))}}
@app.get('/api/products')
def products(q:str='',db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_VIEW'))):
 st=select(Product).order_by(Product.updated_at.desc())
 if q:st=st.where(Product.name.ilike('%'+q+'%')|Product.model_code.ilike('%'+q+'%'))
 return [dto(x) for x in db.scalars(st)]
@app.get('/api/product-categories')
def product_categories(db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_VIEW'))):
 return [{'id':x.id,'name':x.name} for x in db.scalars(select(ProductCategory).order_by(ProductCategory.name))]
@app.get('/api/products/{pid}')
def product(pid:int,db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_VIEW'))):
 p=db.get(Product,pid)
 if not p:raise HTTPException(404,'产品不存在')
 result=product_detail_dto(p,db)|{'source':p.source,'owner':p.owner,'lastVerifiedAt':p.last_verified_at.isoformat()}
 if 'PRICE_VIEW' in permission_codes(u):
  price=db.scalar(select(ProductPrice).where(ProductPrice.product_id==pid))
  result['price']={'referencePrice':float(price.reference_price),'currency':price.currency} if price else None
 return result
@app.post('/api/admin/products',status_code=201)
def create_product(x:ProductIn,db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_MANAGE'))):
 p=Product(**x.model_dump(),source='后台维护',owner=u.display_name);db.add(p);db.flush();audit(db,u,'CREATE','product',p.id,x.model_dump());db.commit();db.refresh(p);return dto(p)
@app.patch('/api/admin/products/{pid}')
def update_product(pid:int,x:ProductPatch,db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_MANAGE'))):
 p=db.get(Product,pid)
 if not p: raise HTTPException(404,'产品不存在')
 values=x.model_dump(exclude_none=True)
 if 'dynamic_fields' in values:values['dynamic_fields_json']=json.dumps(values.pop('dynamic_fields'),ensure_ascii=False)
 for k,v in values.items(): setattr(p,k,v)
 p.owner=u.display_name;audit(db,u,'UPDATE','product',p.id,values);db.commit();db.refresh(p);return product_detail_dto(p,db)
@app.delete('/api/admin/products/{pid}',status_code=204)
def delete_product(pid:int,db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_MANAGE'))):
 p=db.get(Product,pid)
 if not p: raise HTTPException(404,'产品不存在')
 db.query(ProductCapability).filter(ProductCapability.product_id==pid).delete();audit(db,u,'DELETE','product',pid,{'name':p.name,'modelCode':p.model_code});db.delete(p);db.commit()
@app.get('/api/admin/audit-logs')
def audit_logs(limit:int=100,db:Session=Depends(session),u:User=Depends(permit('SYSTEM_MANAGE'))):
 rows=db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(min(max(limit,1),500)))
 return [{'id':x.id,'userId':x.user_id,'action':x.action,'resourceType':x.resource_type,'resourceId':x.resource_id,'detail':json.loads(x.detail_json),'createdAt':x.created_at.isoformat()} for x in rows]
@app.get('/api/products/{pid}/capabilities')
def product_capabilities(pid:int,db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_VIEW'))):
 if not db.get(Product,pid): raise HTTPException(404,'产品不存在')
 return product_detail_dto(db.get(Product,pid),db)['capabilities']
@app.get('/api/catalog/{kind}')
def catalog(kind:str,db:Session=Depends(session),u:User=Depends(user)):
 meta={'model-capabilities':Capability,'capabilities':Capability,'algorithms':Algorithm,'software':Software,'scenes':Scene,'solutions':Solution}.get(kind)
 if not meta:raise HTTPException(404,'模块不存在')
 if 'KNOWLEDGE_VIEW' not in permission_codes(u):raise HTTPException(403,'缺少权限：KNOWLEDGE_VIEW')
 m=meta
 rows=[]
 for x in db.scalars(select(m).order_by(m.updated_at.desc())):
  row={'id':x.id,'name':x.name,'summary':getattr(x,'summary',getattr(x,'description','')),'status':getattr(x,'status','SUPPORTED'),'updatedAt':x.updated_at.isoformat()}
  for attr,key in [('code','code'),('version','version'),('category','category'),('software_type','softwareType'),('vendor','vendor'),('deployment_mode','deploymentMode'),('tier','tier'),('scene_id','sceneId')]:
   if hasattr(x,attr):row[key]=getattr(x,attr)
  if isinstance(x,Software):row['supportedOs']=json.loads(x.supported_os_json or '[]')
  if isinstance(x,Solution):row['scene']=x.scene.name
  rows.append(row)
 return rows
def center_rows(kind:str,db:Session,u:User):return catalog(kind,db,u)
@app.get('/api/software')
def software_center(db:Session=Depends(session),u:User=Depends(user)):return center_rows('software',db,u)
@app.get('/api/algorithms')
def algorithm_center(db:Session=Depends(session),u:User=Depends(user)):return center_rows('algorithms',db,u)
@app.get('/api/model-capabilities')
def model_capability_center(db:Session=Depends(session),u:User=Depends(user)):return center_rows('model-capabilities',db,u)
@app.get('/api/scenes')
def scene_center(db:Session=Depends(session),u:User=Depends(user)):return center_rows('scenes',db,u)
@app.get('/api/solutions')
def solution_center(db:Session=Depends(session),u:User=Depends(user)):return center_rows('solutions',db,u)

def center_detail(kind:str,rid:int,db:Session,u:User):
 if 'KNOWLEDGE_VIEW' not in permission_codes(u):raise HTTPException(403,'缺少权限：KNOWLEDGE_VIEW')
 model={'software':Software,'algorithms':Algorithm,'model-capabilities':Capability,'scenes':Scene,'solutions':Solution}.get(kind)
 if not model:raise HTTPException(404,'模块不存在')
 rec=db.get(model,rid)
 if not rec:raise HTTPException(404,'知识条目不存在')
 result={'id':rec.id,'name':rec.name,'summary':getattr(rec,'summary',getattr(rec,'description','')),'status':getattr(rec,'status','SUPPORTED'),'updatedAt':rec.updated_at.isoformat(),'relations':[]}
 for attr,key in [('code','code'),('version','version'),('category','category'),('software_type','softwareType'),('vendor','vendor'),('deployment_mode','deploymentMode'),('tier','tier'),('pain_points','painPoints')]:
  if hasattr(rec,attr):result[key]=getattr(rec,attr)
 if isinstance(rec,Software):result['supportedOs']=json.loads(rec.supported_os_json or '[]')
 if isinstance(rec,Scene):
  solutions=db.scalars(select(Solution).where(Solution.scene_id==rid).order_by(Solution.tier,Solution.name)).all()
  result['relations']=[{'id':x.id,'type':'solutions','name':x.name,'meta':x.tier,'summary':x.summary} for x in solutions]
 if isinstance(rec,Solution):
  result['sceneId']=rec.scene_id;result['scene']=rec.scene.name
  result['relations']=[{'id':rec.scene.id,'type':'scenes','name':rec.scene.name,'meta':'适用场景','summary':rec.scene.summary}]
 return result

@app.get('/api/software/{rid}')
def software_detail(rid:int,db:Session=Depends(session),u:User=Depends(user)):return center_detail('software',rid,db,u)
@app.get('/api/algorithms/{rid}')
def algorithm_detail(rid:int,db:Session=Depends(session),u:User=Depends(user)):return center_detail('algorithms',rid,db,u)
@app.get('/api/model-capabilities/{rid}')
def model_capability_detail(rid:int,db:Session=Depends(session),u:User=Depends(user)):return center_detail('model-capabilities',rid,db,u)
@app.get('/api/solutions/{rid}')
def solution_detail(rid:int,db:Session=Depends(session),u:User=Depends(user)):return center_detail('solutions',rid,db,u)
@app.get('/api/scenes/{sid}')
def scene_detail(sid:int,db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_VIEW'))):
 rec=db.get(Scene,sid)
 if not rec:raise HTTPException(404,'场景不存在')
 solutions=db.scalars(select(Solution).where(Solution.scene_id==sid).order_by(Solution.tier,Solution.name)).all()
 relation_rows=[{'id':x.id,'name':x.name,'tier':x.tier,'summary':x.summary} for x in solutions]
 return {'id':rec.id,'name':rec.name,'summary':rec.summary,'painPoints':rec.pain_points,'status':rec.status,'updatedAt':rec.updated_at.isoformat(),'solutions':relation_rows,'relations':[{'id':x['id'],'type':'solutions','name':x['name'],'meta':x['tier'],'summary':x['summary']} for x in relation_rows]}
def catalog_model(kind):
 meta={'model-capabilities':Capability,'capabilities':Capability,'algorithms':Algorithm,'software':Software,'scenes':Scene,'solutions':Solution}.get(kind)
 if not meta:raise HTTPException(404,'模块不存在')
 return meta
def catalog_values(kind,x):
 d=x.model_dump(exclude_none=True)
 if 'summary' in d:
  summary=d.pop('summary')
  if kind in {'model-capabilities','capabilities','algorithms','software'}:d['description']=summary
  else:d['summary']=summary
 if 'supported_os' in d:d['supported_os_json']=json.dumps(d.pop('supported_os'),ensure_ascii=False)
 allowed={'model-capabilities':{'name','description','category','status'},'capabilities':{'name','description','category','status'},'algorithms':{'name','description','version','category','status'},'software':{'name','description','code','software_type','vendor','version','deployment_mode','supported_os_json','status'},'scenes':{'name','summary','status'},'solutions':{'name','summary','scene_id','tier'}}[kind]
 return {k:v for k,v in d.items() if k in allowed}
@app.post('/api/admin/catalog/{kind}',status_code=201)
def create_catalog(kind:str,x:CatalogIn,db:Session=Depends(session),u:User=Depends(user)):
 m=catalog_model(kind)
 if 'KNOWLEDGE_MANAGE' not in permission_codes(u):raise HTTPException(403,'缺少权限：KNOWLEDGE_MANAGE')
 values=catalog_values(kind,x)
 if kind=='solutions' and not values.get('scene_id'):raise HTTPException(422,'方案必须关联场景')
 rec=m(**values);db.add(rec);db.flush();audit(db,u,'CREATE',kind,rec.id,values);db.commit();db.refresh(rec);return {'id':rec.id,'name':rec.name}
@app.patch('/api/admin/catalog/{kind}/{rid}')
def update_catalog(kind:str,rid:int,x:CatalogPatch,db:Session=Depends(session),u:User=Depends(user)):
 m=catalog_model(kind)
 if 'KNOWLEDGE_MANAGE' not in permission_codes(u):raise HTTPException(403,'缺少权限：KNOWLEDGE_MANAGE')
 rec=db.get(m,rid)
 if not rec:raise HTTPException(404,'记录不存在')
 values=catalog_values(kind,x)
 for k,v in values.items():setattr(rec,k,v)
 audit(db,u,'UPDATE',kind,rid,values);db.commit();return {'id':rec.id,'name':rec.name}
@app.delete('/api/admin/catalog/{kind}/{rid}',status_code=204)
def delete_catalog(kind:str,rid:int,db:Session=Depends(session),u:User=Depends(user)):
 m=catalog_model(kind)
 if 'KNOWLEDGE_MANAGE' not in permission_codes(u):raise HTTPException(403,'缺少权限：KNOWLEDGE_MANAGE')
 rec=db.get(m,rid)
 if not rec:raise HTTPException(404,'记录不存在')
 if kind in {'model-capabilities','capabilities'}:db.query(ProductCapability).filter(ProductCapability.capability_id==rid).delete()
 audit(db,u,'DELETE',kind,rid,{'name':rec.name});db.delete(rec)
 try:db.commit()
 except Exception as exc:db.rollback();raise HTTPException(409,'记录仍被业务数据引用') from exc
@app.post('/api/bom/recommend')
def recommend(x:BomIn,u:User=Depends(permit('BOM_EDIT'))):
 items=[{'model':'HZ-BC-400','name':'桥梁防撞综合系统','quantity':1,'unit':'套','reason':'桥梁防撞基础平台'}]
 if x.ptz_count:items.append({'model':'HZ-VC-700','name':'航道视频联动终端','quantity':x.ptz_count,'unit':'台','reason':'球机联动数量来自需求'})
 if x.ais:items.append({'model':'HZ-AS-900','name':'AIS融合服务器','quantity':1,'unit':'套','reason':'AIS融合'})
 if x.ocr:items.append({'model':'HZ-OCR-1000','name':'船名OCR识别服务','quantity':1,'unit':'套','reason':'船名识别'})
 if x.yaw:items.append({'model':'HZ-YW-1100','name':'偏航预警分析服务','quantity':1,'unit':'套','reason':'偏航预警'})
 if x.overheight:items.append({'model':'HZ-OH-1200','name':'超高预警分析服务','quantity':1,'unit':'套','reason':'超高预警'})
 if x.vhf:items.append({'model':'HZ-VHF-01','name':'VHF通信终端','quantity':1,'unit':'套','reason':'VHF通信'})
 coverage=['船舶探测']+(['AIS融合'] if x.ais else [])+(['船名OCR'] if x.ocr else [])+(['偏航预警'] if x.yaw else [])+(['球机联动'] if x.ptz_count else [])+(['超高预警'] if x.overheight else [])+(['VHF通信'] if x.vhf else [])
 return {'items':items,'validation':{'status':'PASS','coverage':coverage}}
@app.get('/api/projects')
def projects(db:Session=Depends(session),u:User=Depends(permit('BOM_VIEW'))):
 return [{'id':x.id,'name':x.name,'customer':x.customer,'region':x.region,'scene':x.scene.name,'bomVersion':x.bom_version,'updatedAt':x.updated_at.isoformat()} for x in db.scalars(select(Project).order_by(Project.updated_at.desc()))]
@app.post('/api/projects',status_code=201)
def create_project(x:ProjectIn,db:Session=Depends(session),u:User=Depends(permit('BOM_EDIT'))):
 if not db.get(Scene,x.scene_id):raise HTTPException(422,'场景不存在')
 if not x.bom_json:raise HTTPException(422,'BOM不能为空')
 rec=Project(name=x.name,customer=x.customer,region=x.region,scene_id=x.scene_id,requirements_json=json.dumps(x.requirements_json,ensure_ascii=False),bom_json=json.dumps(x.bom_json,ensure_ascii=False));db.add(rec);db.commit();db.refresh(rec);return {'id':rec.id,'name':rec.name,'bomVersion':rec.bom_version}
@app.get('/api/projects/{pid}')
def project_detail(pid:int,db:Session=Depends(session),u:User=Depends(permit('BOM_VIEW'))):
 rec=db.get(Project,pid)
 if not rec:raise HTTPException(404,'项目不存在')
 return {'id':rec.id,'name':rec.name,'customer':rec.customer,'region':rec.region,'sceneId':rec.scene_id,'scene':rec.scene.name,'requirements':json.loads(rec.requirements_json),'bom':json.loads(rec.bom_json),'bomVersion':rec.bom_version,'updatedAt':rec.updated_at.isoformat()}
@app.patch('/api/projects/{pid}')
def update_project(pid:int,x:ProjectPatch,db:Session=Depends(session),u:User=Depends(permit('BOM_EDIT'))):
 rec=db.get(Project,pid)
 if not rec:raise HTTPException(404,'项目不存在')
 values=x.model_dump(exclude_none=True)
 if values.get('scene_id') and not db.get(Scene,values['scene_id']):raise HTTPException(422,'场景不存在')
 for key,value in values.items():setattr(rec,key,json.dumps(value,ensure_ascii=False) if key in {'requirements_json','bom_json'} else value)
 rec.bom_version+=1;audit(db,u,'UPDATE','project',pid,{'bomVersion':rec.bom_version});db.commit();return {'id':rec.id,'name':rec.name,'bomVersion':rec.bom_version}
@app.delete('/api/projects/{pid}',status_code=204)
def delete_project(pid:int,db:Session=Depends(session),u:User=Depends(permit('BOM_EDIT'))):
 rec=db.get(Project,pid)
 if not rec:raise HTTPException(404,'项目不存在')
 audit(db,u,'DELETE','project',pid,{'name':rec.name});db.delete(rec);db.commit()
@app.get('/api/admin/roles')
def roles(db:Session=Depends(session),u:User=Depends(permit('USER_MANAGE'))):
 return [{'code':x.code,'name':x.name,'permissions':sorted({p.permission.code for p in x.permission_links} or {p for p in x.permissions.split(',') if p})} for x in db.scalars(select(Role).order_by(Role.code))]
@app.get('/api/training/courses')
def training_courses(db:Session=Depends(session),u:User=Depends(permit('TRAINING_VIEW'))):
 return [{'id':x.id,'externalCourseId':x.external_course_id,'name':x.name,'summary':x.summary,'launchUrl':x.launch_url,'status':x.status,'updatedAt':x.updated_at.isoformat()} for x in db.scalars(select(TrainingCourse).order_by(TrainingCourse.updated_at.desc()))]
@app.post('/api/admin/training/courses',status_code=201)
def create_training_course(x:TrainingCourseIn,db:Session=Depends(session),u:User=Depends(permit('TRAINING_ADMIN'))):
 if db.scalar(select(TrainingCourse).where(TrainingCourse.external_course_id==x.external_course_id)): raise HTTPException(409,'课程关联已存在')
 rec=TrainingCourse(**x.model_dump());db.add(rec);db.flush();audit(db,u,'CREATE','training_course',rec.id,x.model_dump());db.commit();db.refresh(rec);return {'id':rec.id,'name':rec.name,'status':rec.status}
@app.get('/api/prices')
def prices(db:Session=Depends(session),u:User=Depends(permit('PRICE_VIEW'))):
 db.add(PriceAccessLog(user_id=u.id,action='VIEW',resource='price-list'));db.commit();cost='COST_VIEW' in permission_codes(u)
 return [{'product':p.product.name,'modelCode':p.product.model_code,'referencePrice':float(p.reference_price),'costPrice':float(p.cost_price) if cost else None,'currency':p.currency} for p in db.scalars(select(ProductPrice))]
@app.get('/api/prices/export')
def export_prices(db:Session=Depends(session),u:User=Depends(permit('PRICE_EXPORT'))):
 cost='COST_VIEW' in permission_codes(u);output=io.StringIO();writer=csv.writer(output);header=['产品','型号','参考报价','币种']+(['成本价'] if cost else []);writer.writerow(header)
 for p in db.scalars(select(ProductPrice).order_by(ProductPrice.id)):
  writer.writerow([p.product.name,p.product.model_code,float(p.reference_price),p.currency]+([float(p.cost_price)] if cost else []))
 db.add(PriceAccessLog(user_id=u.id,action='EXPORT',resource='price-list'));db.commit()
 return Response('\ufeff'+output.getvalue(),media_type='text/csv',headers={'Content-Disposition':'attachment; filename=haizhi-prices.csv','Cache-Control':'no-store'})
@app.get('/api/admin/price-access-logs')
def price_access_logs(limit:int=100,db:Session=Depends(session),u:User=Depends(permit('SYSTEM_MANAGE'))):
 rows=db.scalars(select(PriceAccessLog).order_by(PriceAccessLog.created_at.desc()).limit(min(max(limit,1),500)))
 return [{'id':x.id,'userId':x.user_id,'username':db.get(User,x.user_id).username,'action':x.action,'resource':x.resource,'createdAt':x.created_at.isoformat()} for x in rows]
@app.post('/api/ai/requirement-analysis')
async def ai(x:BomIn,u:User=Depends(user),db:Session=Depends(session)):
 rid=uuid.uuid4().hex;started=time.time()
 try:
  async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as c:r=await c.post(settings.ai_base_url.rstrip('/')+'/v1/chat/completions',json={'model':settings.ai_model,'messages':[{'role':'user','content':'将桥梁防撞需求整理为能力和约束：'+x.model_dump_json()}],'max_tokens':512});r.raise_for_status()
  message=r.json()['choices'][0]['message'];content=message.get('content') or message.get('reasoning') or message.get('reasoning_content') or '模型已响应，但未返回可展示文本';db.add(AiInteractionLog(request_id=rid,user_id=u.id,provider='local-llm',model_id=settings.ai_model,latency_ms=int((time.time()-started)*1000),success=True));db.commit();return {'requestId':rid,'mode':'llm','content':content}
 except Exception as e:
  db.add(AiInteractionLog(request_id=rid,user_id=u.id,provider='local-llm',model_id=settings.ai_model,latency_ms=int((time.time()-started)*1000),success=False,failure_reason=str(e)[:300]));db.commit();return {'requestId':rid,'mode':'rule-fallback','content':'AI服务暂不可用，已切换至规则式配单。'}

STATIC_ROOT=os.path.join(os.path.dirname(os.path.dirname(__file__)),'static')
@app.get('/{path:path}',include_in_schema=False)
def frontend(path:str):
 candidate=os.path.join(STATIC_ROOT,path)
 if path and os.path.isfile(candidate): return FileResponse(candidate)
 return FileResponse(os.path.join(STATIC_ROOT,'index.html'))
