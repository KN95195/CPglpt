import csv,io,json,time,uuid,os,re,secrets,urllib.parse
from contextlib import asynccontextmanager
from datetime import datetime,timedelta,timezone
import jwt,httpx
from fastapi import FastAPI,Depends,HTTPException,status,UploadFile,File,Form,Request
from fastapi.responses import FileResponse,Response
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from pydantic import BaseModel,Field,ConfigDict,model_validator
from sqlalchemy import select,func,or_
from sqlalchemy.orm import Session
from .database import Base,engine,session
from .models import *
from .seed import bootstrap,ensure_v3_seed,pwd
from .config import settings
from .directory_crypto import decrypt_directory_password,encrypt_directory_password
from .document_preview import build_preview,preview_capable
from .storage import storage
from .knowledge import router as knowledge_router
security=HTTPBearer(auto_error=False)
@asynccontextmanager
async def lifespan(app):
 with next(session()) as db: bootstrap(db);ensure_v3_seed(db)
 yield
app=FastAPI(title='海智产品中心正式版',version='5.0.0',lifespan=lifespan)
app.include_router(knowledge_router)
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
class ProductParameterIn(BaseModel): id:int|None=None;name:str=Field(min_length=1,max_length=120);value:str='';unit:str='';group:str='基础参数';highlight:bool=False;order:int=Field(default=0,ge=0)
class ProductIn(BaseModel): name:str=Field(min_length=2);product_type:str='HARDWARE';model_code:str=Field(min_length=1,max_length=80);current_version:str='v1.0';category_id:int;summary:str='';status:str='ON_SALE';main_image:str=''
class ProductPatch(BaseModel): name:str|None=None;product_type:str|None=None;model_code:str|None=None;current_version:str|None=None;category_id:int|None=None;summary:str|None=None;status:str|None=None;main_image:str|None=None;dynamic_fields:dict[str,str]|None=None;parameters:list[ProductParameterIn]|None=None;data_status:str|None=None
_CATALOG_ALIASES={'coverImage':'cover_image','painPoints':'pain_points','businessProcess':'business_process','coreCapabilitySummary':'core_capability_summary','functionType':'function_type','inputSummary':'input_summary','outputSummary':'output_summary','inputRequirements':'input_requirements','deploymentRequirements':'deployment_requirements','softwareType':'software_type','deploymentMode':'deployment_mode','supportedOs':'supported_os','sceneId':'scene_id','targetDescription':'target_description','coverageScope':'coverage_scope','architectureSummary':'architecture_summary','implementationNotes':'implementation_notes','modelType':'model_type','taskType':'task_type','inputDefinitions':'input_definitions','outputDefinitions':'output_definitions','useConditions':'use_conditions','capabilityCoverage':'capability_coverage'}
class CatalogIn(BaseModel):
 model_config=ConfigDict(extra='allow')
 name:str=Field(min_length=2);summary:str='';code:str='';version:str='v1.0';category:str='通用';cover_image:str='';pain_points:str|list[dict]='';goals:list[str|dict]=[];business_process:list[str|dict]=[];core_capability_summary:str='';function_type:str='识别';input_summary:str='';output_summary:str='';metrics:dict|list[dict]={};input_requirements:dict|list[dict]={};deployment_requirements:dict[str,str]={};boundaries:list[str]=[];software_type:str='PLATFORM';vendor:str='海智科技';deployment_mode:str='PRIVATE';supported_os:list[str]=[];scene_id:int|None=None;tier:str='标准型';target_description:str='';coverage_scope:str='';architecture_summary:str='';implementation_notes:str='';status:str='SUPPORTED'
 @model_validator(mode='before')
 @classmethod
 def accept_camel_case(cls,value):
  if isinstance(value,dict): return {(_CATALOG_ALIASES.get(k,k)):v for k,v in value.items()}
  return value
class CatalogPatch(CatalogIn):
 name:str|None=None;summary:str|None=None;code:str|None=None;version:str|None=None;category:str|None=None;cover_image:str|None=None;pain_points:str|list[dict]|None=None;goals:list[str|dict]|None=None;business_process:list[str|dict]|None=None;core_capability_summary:str|None=None;function_type:str|None=None;input_summary:str|None=None;output_summary:str|None=None;metrics:dict|list[dict]|None=None;input_requirements:dict|list[dict]|None=None;deployment_requirements:dict[str,str]|None=None;boundaries:list[str]|None=None;software_type:str|None=None;vendor:str|None=None;deployment_mode:str|None=None;supported_os:list[str]|None=None;scene_id:int|None=None;tier:str|None=None;target_description:str|None=None;coverage_scope:str|None=None;architecture_summary:str|None=None;implementation_notes:str|None=None;status:str|None=None
class SolutionBomItemIn(BaseModel): product_id:int;quantity:int=Field(default=1,ge=1,le=10000);unit:str='台';purpose:str='';requirement_level:str='REQUIRED';recommendation_reason:str=''
class SolutionBomIn(BaseModel): items:list[SolutionBomItemIn]
class RelationIn(BaseModel): source_type:str;source_id:int;target_type:str;target_id:int;relation_type:str='RELATED';metadata:dict[str,str|int|bool]={}
class RelationPatch(BaseModel): relation_type:str|None=None; metadata:dict[str,str|int|bool]={}
class ProductPricePatch(BaseModel): reference_price:float=Field(ge=0);currency:str='CNY';tax_included:bool=True;tax_rate:float=Field(default=13,ge=0,le=100);valid_until:datetime|None=None;notes:str=''
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
class RolePermissionPatch(BaseModel): permissions:list[str]
class DirectoryApproval(BaseModel): candidate_id:int;role_code:str
class DirectoryConfirm(BaseModel): run_id:int;users:list[DirectoryApproval]
class DirectoryConfigInput(BaseModel):
 enabled:bool=False;server_type:str='MS_ACTIVE_DIRECTORY';protocol:str=Field(default='LDAP',pattern=r'^(LDAP|LDAPS)$');host:str='';port:int=Field(default=389,ge=1,le=65535);timeout_seconds:int=Field(default=30,ge=1,le=300);bind_dn:str='';bind_password:str='';base_dn:str='';login_domain:str='';user_filter:str='(&(objectClass=user)(sAMAccountName=*))';default_role:str='sales'
class UserCreate(BaseModel): username:str=Field(min_length=2,max_length=64);display_name:str=Field(min_length=1,max_length=80);password:str=Field(min_length=8,max_length=128);role_code:str;email:str='';department:str='';enabled:bool=True
class UserPatch(BaseModel): display_name:str|None=None;password:str|None=Field(default=None,min_length=8,max_length=128);role_code:str|None=None;email:str|None=None;department:str|None=None;enabled:bool|None=None
class RoleCreate(BaseModel): code:str=Field(pattern=r'^[a-z][a-z0-9_]{1,63}$');name:str=Field(min_length=2,max_length=80);permissions:list[str]=[]
class RolePatch(BaseModel): name:str|None=None;permissions:list[str]|None=None
def chinese_role_name(value):
 if not re.fullmatch(r'[\u4e00-\u9fff0-9（）()·\s-]{2,80}',value.strip()):raise HTTPException(422,'角色名称必须使用中文')
 return value.strip()
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
def get_directory_config(db):return db.get(DirectoryConfig,1)
def ad_ready(config):return bool(config and config.enabled and config.host and config.base_dn and config.bind_dn and config.bind_password_encrypted)
def directory_error_message(value,limit=1000):
 return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]','',str(value)).strip()[:limit]
def directory_connection(config,password=''):
 from ldap3 import ALL,Connection,Server
 secret=password or decrypt_directory_password(config.bind_password_encrypted)
 if not secret:raise RuntimeError('请填写管理密码')
 server=Server(config.host,port=config.port,use_ssl=config.protocol=='LDAPS',connect_timeout=config.timeout_seconds,get_info=ALL)
 return Connection(server,user=config.bind_dn,password=secret,auto_bind=True,receive_timeout=config.timeout_seconds,raise_exceptions=True)
def ad_authenticate(username,password,db):
 config=get_directory_config(db)
 if not ad_ready(config) or not password:return False
 try:
  from ldap3 import Connection,Server
  principal=f'{username}@{config.login_domain}' if config.login_domain and '@' not in username else username
  connection=Connection(Server(config.host,port=config.port,use_ssl=config.protocol=='LDAPS',connect_timeout=config.timeout_seconds),user=principal,password=password,auto_bind=True,receive_timeout=config.timeout_seconds,raise_exceptions=True);connection.unbind();return True
 except Exception:return False
def gateway_client(c:HTTPAuthorizationCredentials|None=Depends(security),db:Session=Depends(session)):
 if not c: raise HTTPException(401,'missing gateway credential')
 if settings.ai_gateway_api_key and secrets.compare_digest(c.credentials,settings.ai_gateway_api_key):
  service_user=db.scalar(select(User).join(Role).where(Role.code=='admin',User.enabled==True))
  if not service_user: raise HTTPException(503,'gateway service account unavailable')
  return service_user
 return user(c,db)
def parameter_dto(x):return {'id':x.id,'name':x.name,'value':x.value,'unit':x.unit,'group':x.group_name,'highlight':x.highlight,'order':x.sort_order}
def dto(p,db=None,u=None):
 result={'id':p.id,'name':p.name,'productCode':p.product_code,'productType':p.product_type,'modelCode':p.model_code,'currentVersion':p.current_version,'categoryId':p.category_id,'category':p.category.name,'summary':p.summary,'status':p.status,'mainImage':p.main_image,'dataStatus':p.data_status,'parameters':[parameter_dto(x) for x in p.parameters],'updatedAt':p.updated_at.isoformat()}
 if db and u and 'PRICE_VIEW' in permission_codes(u):
  price=db.scalar(select(ProductPrice).where(ProductPrice.product_id==p.id));result['price']={'referencePrice':float(price.reference_price),'currency':price.currency} if price else None
 return result
def product_detail_dto(p,db,u=None):
 caps=db.scalars(select(Capability).join(ProductCapability,Capability.id==ProductCapability.capability_id).where(ProductCapability.product_id==p.id)).all()
 return dto(p,db,u)|{'dynamicFields':{x.name:x.value for x in p.parameters} or json.loads(p.dynamic_fields_json or '{}'),'capabilities':[{'id':c.id,'type':'model-capabilities','name':c.name,'category':c.category,'meta':c.category,'summary':c.description} for c in caps]}
RELATION_MODELS={'products':Product,'software':Software,'algorithms':Algorithm,'model-capabilities':Capability,'scenes':Scene,'solutions':Solution}
def relation_payload(kind:str,rid:int,db:Session):
 rows=db.scalars(select(KnowledgeRelation).where(((KnowledgeRelation.source_type==kind)&(KnowledgeRelation.source_id==rid))|((KnowledgeRelation.target_type==kind)&(KnowledgeRelation.target_id==rid))).order_by(KnowledgeRelation.updated_at.desc())).all();result=[]
 for rel in rows:
  outgoing=rel.source_type==kind and rel.source_id==rid;other_type=rel.target_type if outgoing else rel.source_type;other_id=rel.target_id if outgoing else rel.source_id;other=db.get(RELATION_MODELS[other_type],other_id)
  if other:result.append({'relationId':rel.id,'relationType':rel.relation_type,'id':other_id,'type':other_type,'name':other.name,'meta':json.loads(rel.metadata_json or '{}'),'summary':getattr(other,'summary',getattr(other,'description',''))})
 return result
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
def documents(center_type:str|None=None,center_id:int|None=None,db:Session=Depends(session),u:User=Depends(permit('DOCUMENT_VIEW'))):
 query=select(DocumentAsset)
 if center_type is not None:query=query.where(DocumentAsset.center_type==center_type)
 if center_id is not None:query=query.where(DocumentAsset.center_id==center_id)
 if 'DOCUMENT_EDIT' not in permission_codes(u):query=query.where(DocumentAsset.status=='PUBLISHED',DocumentAsset.document_status!='OBSOLETE')
 can_download='DOCUMENT_DOWNLOAD' in permission_codes(u)
 return [{'id':x.id,'name':x.name,'originalFileName':x.original_file_name or x.name,'mimeType':x.mime_type,'fileSize':x.file_size,'category':x.category,'version':x.version,'description':x.description,'status':x.status,'documentStatus':x.document_status,'applicableModels':x.applicable_models,'applicableVersions':x.applicable_versions,'knowledgeEnabled':x.knowledge_enabled,'knowledgeStatus':x.knowledge_status,'knowledgeSyncError':x.knowledge_sync_error,'productId':x.product_id,'sceneId':x.scene_id,'tenderId':x.tender_id,'centerType':x.center_type,'centerId':x.center_id,'canPreview':preview_capable(x.original_file_name or x.name,x.mime_type),'canDownload':can_download,'updatedAt':x.updated_at.isoformat()} for x in db.scalars(query.order_by(DocumentAsset.updated_at.desc()))]
@app.post('/api/documents',status_code=201)
async def upload_document(file:UploadFile=File(...),product_id:int|None=Form(None),scene_id:int|None=Form(None),tender_id:int|None=Form(None),center_type:str|None=Form(None),center_id:int|None=Form(None),category:str=Form('产品资料'),version:str=Form('V1.0'),description:str=Form(''),applicable_models:str=Form(''),applicable_versions:str=Form(''),knowledge_enabled:bool=Form(False),db:Session=Depends(session),u:User=Depends(permit('DOCUMENT_EDIT'))):
 data=await file.read()
 if not data or len(data)>200*1024*1024: raise HTTPException(413,'文件为空或超过200MB')
 if product_id and not db.get(Product,product_id):raise HTTPException(422,'产品不存在')
 if scene_id and not db.get(Scene,scene_id):raise HTTPException(422,'场景不存在')
 if tender_id and not db.get(Tender,tender_id):raise HTTPException(422,'投标项目不存在')
 if (center_type is None)!=(center_id is None):raise HTTPException(422,'知识中心类型和记录ID必须同时提供')
 if center_type is not None:
  model=RELATION_MODELS.get(center_type)
  if not model:raise HTTPException(422,'知识中心类型无效')
  if not db.get(model,center_id):raise HTTPException(422,'知识中心记录不存在')
 object_name=f'{uuid.uuid4().hex}-{os.path.basename(file.filename or "document")}'
 try: path=storage.put(object_name,data,file.content_type or 'application/octet-stream')
 except Exception as e: raise HTTPException(503,'对象存储不可用') from e
 rec=DocumentAsset(name=file.filename or object_name,original_file_name=file.filename or object_name,path=path,mime_type=file.content_type or 'application/octet-stream',file_size=len(data),category=category,version=version,description=description,status='DRAFT',document_status='CURRENT',applicable_models=applicable_models,applicable_versions=applicable_versions,knowledge_enabled=knowledge_enabled,knowledge_status='NOT_SYNCED',uploaded_by=u.id,product_id=product_id,scene_id=scene_id,tender_id=tender_id,center_type=center_type,center_id=center_id);db.add(rec);db.flush()
 try:
  preview=build_preview(rec.original_file_name,rec.mime_type,data)
  if preview:
   preview_name=f'previews/{uuid.uuid4().hex}{preview.extension}';preview_path=storage.put(preview_name,preview.data,preview.mime_type);db.add(DocumentPreview(document_id=rec.id,preview_type=preview.preview_type,file_path=preview_path,mime_type=preview.mime_type,status='READY'))
 except Exception as exc:
  db.add(DocumentPreview(document_id=rec.id,preview_type='UNAVAILABLE',file_path='',mime_type='',status='FAILED',error_message=str(exc)[:500]))
 audit(db,u,'CREATE','document',rec.id,{'name':rec.name,'centerType':center_type,'centerId':center_id});db.commit();db.refresh(rec)
 preview_row=db.scalar(select(DocumentPreview).where(DocumentPreview.document_id==rec.id).order_by(DocumentPreview.id.desc()))
 return {'id':rec.id,'name':rec.name,'mimeType':rec.mime_type,'fileSize':rec.file_size,'status':rec.status,'documentStatus':rec.document_status,'knowledgeEnabled':rec.knowledge_enabled,'knowledgeStatus':rec.knowledge_status,'productId':rec.product_id,'sceneId':rec.scene_id,'tenderId':rec.tender_id,'centerType':rec.center_type,'centerId':rec.center_id,'canPreview':preview_row is None or preview_row.status=='READY','previewStatus':preview_row.status if preview_row else 'DIRECT','canDownload':'DOCUMENT_DOWNLOAD' in permission_codes(u)}
def object_response(rec,disposition):
 try:
  response=storage.get(rec.path.split('/',1)[1]);data=response.read();response.close();response.release_conn()
 except Exception as exc:raise HTTPException(503,'对象存储不可用') from exc
 return Response(data,media_type=rec.mime_type,headers={'Content-Disposition':f"{disposition}; filename*=UTF-8''{urllib.parse.quote(rec.name)}",'Cache-Control':'no-store'})
@app.get('/api/documents/{did}/preview')
def preview_document(did:int,db:Session=Depends(session),u:User=Depends(permit('DOCUMENT_VIEW'))):
 rec=db.get(DocumentAsset,did)
 if not rec:raise HTTPException(404,'文件不存在')
 preview=db.scalar(select(DocumentPreview).where(DocumentPreview.document_id==did).order_by(DocumentPreview.id.desc()))
 if preview and preview.status=='FAILED':raise HTTPException(422,preview.error_message or '预览生成失败')
 if preview and preview.status=='READY':
  try:
   response=storage.get(preview.file_path.split('/',1)[1]);data=response.read();response.close();response.release_conn()
  except Exception as exc:raise HTTPException(503,'预览文件不可用') from exc
  suffix='.pdf' if preview.mime_type=='application/pdf' else '.html';name=os.path.splitext(rec.name)[0]+suffix
  return Response(data,media_type=preview.mime_type,headers={'Content-Disposition':f"inline; filename*=UTF-8''{urllib.parse.quote(name)}",'Cache-Control':'no-store'})
 try:
  response=storage.get(rec.path.split('/',1)[1]);original=response.read();response.close();response.release_conn();derived=build_preview(rec.original_file_name or rec.name,rec.mime_type,original)
 except Exception as exc:raise HTTPException(422,str(exc)[:500] or '预览生成失败') from exc
 if not derived:return Response(original,media_type=rec.mime_type,headers={'Content-Disposition':f"inline; filename*=UTF-8''{urllib.parse.quote(rec.name)}",'Cache-Control':'no-store'})
 preview_path=storage.put(f'previews/{uuid.uuid4().hex}{derived.extension}',derived.data,derived.mime_type);db.add(DocumentPreview(document_id=rec.id,preview_type=derived.preview_type,file_path=preview_path,mime_type=derived.mime_type,status='READY'));db.commit();name=os.path.splitext(rec.name)[0]+derived.extension
 return Response(derived.data,media_type=derived.mime_type,headers={'Content-Disposition':f"inline; filename*=UTF-8''{urllib.parse.quote(name)}",'Cache-Control':'no-store'})
@app.get('/api/documents/{did}/download')
def download_document(did:int,db:Session=Depends(session),u:User=Depends(permit('DOCUMENT_DOWNLOAD'))):
 rec=db.get(DocumentAsset,did)
 if not rec:raise HTTPException(404,'文件不存在')
 return object_response(rec,'attachment')
@app.delete('/api/documents/{did}',status_code=204)
def delete_document(did:int,db:Session=Depends(session),u:User=Depends(permit('DOCUMENT_EDIT'))):
 rec=db.get(DocumentAsset,did)
 if not rec:raise HTTPException(404,'文件不存在')
 previews=list(db.scalars(select(DocumentPreview).where(DocumentPreview.document_id==did)))
 try:
  storage.delete(rec.path.split('/',1)[1])
  for preview in previews:
   if preview.file_path:storage.delete(preview.file_path.split('/',1)[1])
 except Exception as exc:raise HTTPException(503,'对象存储不可用') from exc
 db.query(DocumentChunk).filter(DocumentChunk.document_id==did).delete();audit(db,u,'DELETE','document',did,{'name':rec.name});db.delete(rec);db.commit()
@app.post('/api/media/images',status_code=201)
async def upload_knowledge_image(file:UploadFile=File(...),db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_MANAGE'))):
 data=await file.read();mime=(file.content_type or '').lower()
 if not mime.startswith('image/'):raise HTTPException(415,'仅支持图片文件')
 if not data or len(data)>10*1024*1024:raise HTTPException(413,'图片为空或超过10MB')
 public_id=uuid.uuid4().hex;object_name=f'knowledge-images/{public_id}-{os.path.basename(file.filename or "image")}'
 try:path=storage.put(object_name,data,mime)
 except Exception as exc:raise HTTPException(503,'对象存储不可用') from exc
 rec=KnowledgeImage(public_id=public_id,name=file.filename or object_name,path=path,mime_type=mime,uploaded_by=u.id);db.add(rec);db.flush();audit(db,u,'CREATE','knowledge_image',rec.id,{'name':rec.name});db.commit()
 return {'id':rec.id,'name':rec.name,'mimeType':rec.mime_type,'url':f'/api/media/images/{rec.public_id}'}
@app.get('/api/media/images/{public_id}')
def knowledge_image(public_id:str,db:Session=Depends(session)):
 rec=db.scalar(select(KnowledgeImage).where(KnowledgeImage.public_id==public_id))
 if not rec:raise HTTPException(404,'图片不存在')
 return object_response(rec,'inline')
@app.delete('/api/media/images/{public_id}',status_code=204)
def delete_knowledge_image(public_id:str,db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_MANAGE'))):
 rec=db.scalar(select(KnowledgeImage).where(KnowledgeImage.public_id==public_id))
 if not rec:raise HTTPException(404,'图片不存在')
 try:storage.delete(rec.path.split('/',1)[1])
 except Exception as exc:raise HTTPException(503,'对象存储不可用') from exc
 audit(db,u,'DELETE','knowledge_image',rec.id,{'name':rec.name});db.delete(rec);db.commit()
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
 key=request.client.host if request.client else 'unknown';now=time.monotonic()
 attempts=[stamp for stamp in login_failures.get(key,[]) if now-stamp<300]
 if len(attempts)>=5:raise HTTPException(429,'登录失败次数过多，请稍后重试')
 u=db.scalar(select(User).where(User.username==x.username))
 valid=bool(u and ((u.auth_source=='AD' and ad_authenticate(x.username,x.password,db)) or (u.auth_source!='AD' and pwd.verify(x.password,u.password_hash))))
 if not valid:
  login_failures[key]=attempts+[now];raise HTTPException(401,'账号或密码错误')
 login_failures.pop(key,None)
 token=jwt.encode({'uid':u.id,'exp':datetime.now(timezone.utc)+timedelta(hours=8)},settings.jwt_secret,algorithm='HS256')
 return {'access_token':token,'user':{'username':u.username,'displayName':u.display_name,'role':u.role.code,'permissions':sorted(permission_codes(u))}}
@app.get('/api/auth/me')
def me(u:User=Depends(user)):return {'username':u.username,'displayName':u.display_name,'role':u.role.code,'permissions':sorted(permission_codes(u))}
@app.get('/api/dashboard')
def dashboard(u:User=Depends(user),db:Session=Depends(session)):
 metrics={'products':db.scalar(select(func.count(Product.id)).where(Product.data_status!='ARCHIVED')),'software':db.scalar(select(func.count(Software.id)).where(Software.status.notin_(['ARCHIVED','DEPRECATED']))),'algorithms':db.scalar(select(func.count(Algorithm.id)).where(Algorithm.status.notin_(['ARCHIVED','DEPRECATED']))),'capabilities':db.scalar(select(func.count(Capability.id)).where(Capability.status.notin_(['ARCHIVED','DEPRECATED']))),'scenes':db.scalar(select(func.count(Scene.id)).where(Scene.status.notin_(['ARCHIVED','DEPRECATED']))),'solutions':db.scalar(select(func.count(Solution.id)).where(Solution.status.notin_(['ARCHIVED','DEPRECATED'])))}
 products=list(db.scalars(select(Product).where(Product.data_status!='ARCHIVED').order_by(Product.updated_at.desc()).limit(4)))
 scenes=list(db.scalars(select(Scene).where(Scene.status=='PUBLISHED').order_by(Scene.updated_at.desc()).limit(4)))
 capabilities=list(db.scalars(select(Capability).where(Capability.status=='SUPPORTED').order_by(Capability.updated_at.desc()).limit(6)))
 updates=[]
 for kind,label,model,path in [('products','产品',Product,'/products/'),('software','软件',Software,'/software/'),('algorithms','算法',Algorithm,'/algorithms/'),('model-capabilities','模型能力',Capability,'/model-capabilities/'),('scenes','场景',Scene,'/scenes/'),('solutions','方案',Solution,'/solutions/')]:
  statement=select(model)
  statement=statement.where(Product.data_status!='ARCHIVED') if kind=='products' else statement.where(model.status.notin_(['ARCHIVED','DEPRECATED']))
  for item in db.scalars(statement.order_by(model.updated_at.desc()).limit(2)):updates.append({'type':kind,'typeLabel':label,'id':item.id,'name':item.name,'url':path+str(item.id),'updatedAt':item.updated_at.isoformat()})
 projects=[]
 if 'BOM_VIEW' in permission_codes(u):
  query=select(Project).order_by(Project.updated_at.desc()).limit(5)
  if u.role.code=='sales':query=query.where(Project.sales_owner_id==u.id)
  projects=[{'id':item.id,'name':item.name,'customer':item.customer,'status':item.status,'scene':item.scene.name if item.scene else '','updatedAt':item.updated_at.isoformat()} for item in db.scalars(query)]
 return {'metrics':metrics,'coreProducts':[{'id':item.id,'name':item.name,'modelCode':item.model_code,'summary':item.summary,'image':item.main_image} for item in products],'commonScenes':[{'id':item.id,'name':item.name,'category':item.category,'summary':item.summary,'image':item.cover_image} for item in scenes],'recentProjects':projects,'recentUpdates':sorted(updates,key=lambda item:item['updatedAt'],reverse=True)[:6],'popularCapabilities':[{'id':item.id,'name':item.name,'category':item.category,'functionType':item.function_type,'version':item.version} for item in capabilities]}
@app.get('/api/products')
def products(q:str='',db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_VIEW'))):
 st=select(Product).where(Product.data_status!='ARCHIVED').order_by(Product.updated_at.desc())
 if q:st=st.where(Product.name.ilike('%'+q+'%')|Product.model_code.ilike('%'+q+'%'))
 return [dto(x,db,u) for x in db.scalars(st)]
@app.get('/api/product-categories')
def product_categories(db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_VIEW'))):
 return [{'id':x.id,'name':x.name} for x in db.scalars(select(ProductCategory).order_by(ProductCategory.name))]
@app.get('/api/products/{pid}')
def product(pid:int,db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_VIEW'))):
 p=db.get(Product,pid)
 if not p:raise HTTPException(404,'产品不存在')
 result=product_detail_dto(p,db,u)|{'source':p.source,'owner':p.owner,'lastVerifiedAt':p.last_verified_at.isoformat() if p.last_verified_at else None,'relations':relation_payload('products',pid,db),'documents':[{'id':x.id,'name':x.name,'mimeType':x.mime_type} for x in db.scalars(select(DocumentAsset).where(DocumentAsset.product_id==pid).order_by(DocumentAsset.updated_at.desc()))]}
 if 'PRICE_VIEW' in permission_codes(u):
  price=db.scalar(select(ProductPrice).where(ProductPrice.product_id==pid))
  result['price']={'referencePrice':float(price.reference_price),'currency':price.currency,'taxIncluded':price.tax_included,'taxRate':float(price.tax_rate),'validUntil':price.valid_until.isoformat() if price.valid_until else None,'notes':price.notes} if price else None
 return result
@app.get('/api/products/{pid}/prices')
def product_price(pid:int,db:Session=Depends(session),u:User=Depends(permit('PRICE_VIEW'))):
 if not db.get(Product,pid):raise HTTPException(404,'产品不存在')
 price=db.scalar(select(ProductPrice).where(ProductPrice.product_id==pid))
 if not price:return None
 return {'referencePrice':float(price.reference_price),'currency':price.currency,'taxIncluded':price.tax_included,'taxRate':float(price.tax_rate),'validUntil':price.valid_until.isoformat() if price.valid_until else None,'notes':price.notes}
@app.patch('/api/products/{pid}/prices')
def update_product_price(pid:int,x:ProductPricePatch,db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_MANAGE'))):
 if not db.get(Product,pid):raise HTTPException(404,'产品不存在')
 price=db.scalar(select(ProductPrice).where(ProductPrice.product_id==pid));values=x.model_dump()
 if price:
  for key,value in values.items():setattr(price,key,value)
 else:price=ProductPrice(product_id=pid,cost_price=0,**values);db.add(price)
 audit(db,u,'UPDATE','product_price',pid,x.model_dump(mode='json'));db.commit();db.refresh(price)
 return {'referencePrice':float(price.reference_price),'currency':price.currency,'taxIncluded':price.tax_included,'taxRate':float(price.tax_rate),'validUntil':price.valid_until.isoformat() if price.valid_until else None,'notes':price.notes}
@app.post('/api/products',status_code=201)
@app.post('/api/admin/products',status_code=201)
def create_product(x:ProductIn,db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_MANAGE'))):
 values=x.model_dump()
 model_code=values['model_code'].strip()
 if db.scalar(select(Product.id).where(Product.model_code==model_code)) is not None:raise HTTPException(409,'产品型号已存在')
 values['model_code']=model_code
 # The legacy admin alias still feeds the NOT NULL products.product_code column.
 # Keep it compatible with the canonical knowledge route by deriving a stable,
 # unique code from the submitted model code (and suffixing on collisions).
 base_code=model_code
 product_code=base_code
 suffix=1
 while db.scalar(select(Product.id).where(Product.product_code==product_code)) is not None:
  suffix+=1
  product_code=f'{base_code}-{suffix}'
 p=Product(**values,product_code=product_code,source='后台维护',owner=u.display_name);db.add(p);db.flush();audit(db,u,'CREATE','product',p.id,values|{'product_code':product_code});db.commit();db.refresh(p);return dto(p,db,u)
@app.patch('/api/products/{pid}')
@app.patch('/api/admin/products/{pid}')
def update_product(pid:int,x:ProductPatch,db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_MANAGE'))):
 p=db.get(Product,pid)
 if not p: raise HTTPException(404,'产品不存在')
 values=x.model_dump(exclude_none=True)
 parameters=values.pop('parameters',None)
 if 'dynamic_fields' in values:values['dynamic_fields_json']=json.dumps(values.pop('dynamic_fields'),ensure_ascii=False)
 for k,v in values.items(): setattr(p,k,v)
 if parameters is not None:
  db.query(ProductParameter).filter(ProductParameter.product_id==pid).delete()
  db.add_all([ProductParameter(product_id=pid,name=item['name'].strip(),value=item['value'],unit=item['unit'],group_name=item['group'].strip() or '基础参数',highlight=item['highlight'],sort_order=index) for index,item in enumerate(parameters)])
  p.dynamic_fields_json=json.dumps({item['name']:item['value'] for item in parameters},ensure_ascii=False)
 p.owner=u.display_name;audit(db,u,'UPDATE','product',p.id,values);db.commit();db.refresh(p);return product_detail_dto(p,db,u)
@app.delete('/api/products/{pid}',status_code=204)
@app.delete('/api/admin/products/{pid}',status_code=204)
def delete_product(pid:int,db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_MANAGE'))):
 p=db.get(Product,pid)
 if not p: raise HTTPException(404,'产品不存在')
 db.query(ProductCapability).filter(ProductCapability.product_id==pid).delete()
 db.query(ProductParameter).filter(ProductParameter.product_id==pid).delete()
 db.query(ProductPrice).filter(ProductPrice.product_id==pid).delete()
 db.query(SolutionBomItem).filter(SolutionBomItem.product_id==pid).delete()
 db.query(DocumentAsset).filter(DocumentAsset.product_id==pid).update({'product_id':None})
 db.query(KnowledgeRelation).filter(
  ((KnowledgeRelation.source_type=='products')&(KnowledgeRelation.source_id==pid))|
  ((KnowledgeRelation.target_type=='products')&(KnowledgeRelation.target_id==pid))
 ).delete(synchronize_session=False)
 audit(db,u,'DELETE','product',pid,{'name':p.name,'modelCode':p.model_code});db.delete(p);db.commit()
@app.get('/api/admin/audit-logs')
def audit_logs(limit:int=100,db:Session=Depends(session),u:User=Depends(permit('SYSTEM_MANAGE'))):
 rows=db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(min(max(limit,1),500)))
 return [{'id':x.id,'userId':x.user_id,'action':x.action,'resourceType':x.resource_type,'resourceId':x.resource_id,'detail':json.loads(x.detail_json),'createdAt':x.created_at.isoformat()} for x in rows]
@app.get('/api/products/{pid}/capabilities')
def product_capabilities(pid:int,db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_VIEW'))):
 if not db.get(Product,pid): raise HTTPException(404,'产品不存在')
 return product_detail_dto(db.get(Product,pid),db)['capabilities']
@app.get('/api/catalog/{kind}')
def catalog(kind:str,q:str='',db:Session=Depends(session),u:User=Depends(user)):
 meta={'model-capabilities':Capability,'capabilities':Capability,'algorithms':Algorithm,'software':Software,'scenes':Scene,'solutions':Solution}.get(kind)
 if not meta:raise HTTPException(404,'模块不存在')
 if 'KNOWLEDGE_VIEW' not in permission_codes(u):raise HTTPException(403,'缺少权限：KNOWLEDGE_VIEW')
 m=meta
 rows=[]
 statement=select(m).order_by(m.updated_at.desc())
 if q:
  search=f'%{q.strip()}%'
  fields=[m.name.ilike(search)]
  if hasattr(m,'code'): fields.append(m.code.ilike(search))
  if hasattr(m,'version'): fields.append(m.version.ilike(search))
  if hasattr(m,'summary'): fields.append(m.summary.ilike(search))
  if hasattr(m,'description'): fields.append(m.description.ilike(search))
  statement=statement.where(or_(*fields))
 for x in db.scalars(statement):
  row={'id':x.id,'name':x.name,'summary':getattr(x,'summary',getattr(x,'description','')),'status':getattr(x,'status','SUPPORTED'),'updatedAt':x.updated_at.isoformat()}
  for attr,key in [('code','code'),('version','version'),('category','category'),('software_type','softwareType'),('vendor','vendor'),('deployment_mode','deploymentMode'),('tier','tier'),('scene_id','sceneId')]:
   if hasattr(x,attr):row[key]=getattr(x,attr)
  if isinstance(x,Software):row['supportedOs']=json.loads(x.supported_os_json or '[]')
  if isinstance(x,Algorithm):row|={'inputSummary':x.input_summary,'outputSummary':x.output_summary,'metrics':json.loads(x.metrics_json or '{}'),'boundaries':json.loads(x.boundaries_json or '[]')}
  if isinstance(x,Capability):row|={'functionType':x.function_type,'metrics':json.loads(x.metrics_json or '{}'),'inputRequirements':json.loads(x.input_requirements_json or '{}'),'deploymentRequirements':json.loads(x.deployment_requirements_json or '{}'),'boundaries':json.loads(x.boundaries_json or '[]')}
  if isinstance(x,Scene):row|={'category':x.category,'coverImage':x.cover_image,'painPoints':x.pain_points,'goals':json.loads(x.goals_json or '[]'),'businessProcess':json.loads(x.process_json or '[]'),'coreCapabilitySummary':x.core_capability_summary}
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
 result={'id':rec.id,'name':rec.name,'summary':getattr(rec,'summary',getattr(rec,'description','')),'status':getattr(rec,'status','SUPPORTED'),'updatedAt':rec.updated_at.isoformat(),'relations':relation_payload(kind,rid,db)}
 for attr,key in [('code','code'),('version','version'),('category','category'),('software_type','softwareType'),('vendor','vendor'),('deployment_mode','deploymentMode'),('tier','tier'),('pain_points','painPoints')]:
  if hasattr(rec,attr):result[key]=getattr(rec,attr)
 if isinstance(rec,Software):result['supportedOs']=json.loads(rec.supported_os_json or '[]')
 if isinstance(rec,Algorithm):result|={'inputSummary':rec.input_summary,'outputSummary':rec.output_summary,'metrics':json.loads(rec.metrics_json or '{}'),'boundaries':json.loads(rec.boundaries_json or '[]')}
 if isinstance(rec,Capability):result|={'functionType':rec.function_type,'metrics':json.loads(rec.metrics_json or '{}'),'inputRequirements':json.loads(rec.input_requirements_json or '{}'),'deploymentRequirements':json.loads(rec.deployment_requirements_json or '{}'),'boundaries':json.loads(rec.boundaries_json or '[]')}
 if isinstance(rec,Scene):result|={'category':rec.category,'coverImage':rec.cover_image,'painPoints':rec.pain_points,'goals':json.loads(rec.goals_json or '[]'),'businessProcess':json.loads(rec.process_json or '[]'),'coreCapabilitySummary':rec.core_capability_summary}
 if isinstance(rec,Scene):
  solutions=db.scalars(select(Solution).where(Solution.scene_id==rid).order_by(Solution.tier,Solution.name)).all()
  known={(x['type'],x['id']) for x in result['relations']};result['relations'] += [{'id':x.id,'type':'solutions','name':x.name,'meta':{'relationLevel':x.tier},'summary':x.summary} for x in solutions if ('solutions',x.id) not in known]
 if isinstance(rec,Solution):
  result['sceneId']=rec.scene_id;result['scene']=rec.scene.name
  if not any(x['type']=='scenes' and x['id']==rec.scene.id for x in result['relations']):result['relations'].append({'id':rec.scene.id,'type':'scenes','name':rec.scene.name,'meta':{'purpose':'适用场景'},'summary':rec.scene.summary})
  result|={'code':rec.code,'category':rec.category,'targetDescription':rec.target_description,'coverageScope':rec.coverage_scope,'architectureSummary':rec.architecture_summary,'implementationNotes':rec.implementation_notes}
  result['bom']=solution_bom_payload(rec.id,db,u)
 return result

def solution_bom_payload(solution_id:int,db:Session,u:User):
 show_price='PRICE_VIEW' in permission_codes(u);rows=[];total=0.0
 for item in db.scalars(select(SolutionBomItem).where(SolutionBomItem.solution_id==solution_id).order_by(SolutionBomItem.id)):
  row={'id':item.id,'productId':item.product_id,'product':item.product.name,'modelCode':item.product.model_code,'quantity':item.quantity,'unit':item.unit,'purpose':item.purpose,'requirementLevel':item.requirement_level,'recommendationReason':item.recommendation_reason}
  if show_price:
   price=db.scalar(select(ProductPrice).where(ProductPrice.product_id==item.product_id));unit_price=float(price.reference_price) if price else None;subtotal=unit_price*item.quantity if unit_price is not None else None;row|={'unitPrice':unit_price,'subtotal':subtotal,'currency':price.currency if price else 'CNY'};total+=subtotal or 0
  rows.append(row)
 result={'items':rows}
 if show_price:result['total']=total;result['currency']='CNY'
 return result

@app.get('/api/solutions/{rid}/bom')
def solution_bom(rid:int,db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_VIEW'))):
 if not db.get(Solution,rid):raise HTTPException(404,'方案不存在')
 return solution_bom_payload(rid,db,u)

@app.patch('/api/solutions/{rid}/bom')
def update_solution_bom(rid:int,x:SolutionBomIn,db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_MANAGE'))):
 if not db.get(Solution,rid):raise HTTPException(404,'方案不存在')
 if any(not db.get(Product,item.product_id) for item in x.items):raise HTTPException(422,'BOM引用了不存在的产品')
 db.query(SolutionBomItem).filter(SolutionBomItem.solution_id==rid).delete()
 db.add_all([SolutionBomItem(solution_id=rid,**item.model_dump()) for item in x.items]);audit(db,u,'UPDATE','solution_bom',rid,{'count':len(x.items)});db.commit()
 return solution_bom_payload(rid,db,u)

@app.post('/api/relations',status_code=201)
def create_relation(x:RelationIn,db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_MANAGE'))):
 if x.source_type not in RELATION_MODELS or x.target_type not in RELATION_MODELS:raise HTTPException(422,'关系对象类型无效')
 if x.source_type==x.target_type and x.source_id==x.target_id:raise HTTPException(422,'不能关联对象自身')
 if not db.get(RELATION_MODELS[x.source_type],x.source_id) or not db.get(RELATION_MODELS[x.target_type],x.target_id):raise HTTPException(422,'关系对象不存在')
 existing=db.scalar(select(KnowledgeRelation).where(KnowledgeRelation.source_type==x.source_type,KnowledgeRelation.source_id==x.source_id,KnowledgeRelation.target_type==x.target_type,KnowledgeRelation.target_id==x.target_id,KnowledgeRelation.relation_type==x.relation_type))
 if existing:raise HTTPException(409,'关系已存在')
 rec=KnowledgeRelation(source_type=x.source_type,source_id=x.source_id,target_type=x.target_type,target_id=x.target_id,relation_type=x.relation_type,metadata_json=json.dumps(x.metadata,ensure_ascii=False));db.add(rec);db.flush();audit(db,u,'CREATE','knowledge_relation',rec.id,x.model_dump());db.commit();db.refresh(rec);return {'id':rec.id}

@app.patch('/api/relations/{rid}')
def update_relation(rid:int,x:RelationPatch,db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_MANAGE'))):
 rec=db.get(KnowledgeRelation,rid)
 if not rec:raise HTTPException(404,'关系不存在')
 if x.relation_type: rec.relation_type=x.relation_type
 allowed={'supportVersion','minimumVersion','recommendedConcurrency','maxConcurrency','supportStatus','purpose','relationLevel','requirementLevel','solutionLevel','recommended','condition','recommendationReason','notes'}
 unknown=set(x.metadata)-allowed
 if unknown:raise HTTPException(422,'不支持的关系属性：'+','.join(sorted(unknown)))
 rec.metadata_json=json.dumps(x.metadata,ensure_ascii=False);audit(db,u,'UPDATE','knowledge_relation',rid,x.metadata);db.commit();db.refresh(rec)
 return {'id':rec.id,'relationType':rec.relation_type,'metadata':json.loads(rec.metadata_json)}

@app.delete('/api/relations/{rid}',status_code=204)
def delete_relation(rid:int,db:Session=Depends(session),u:User=Depends(permit('KNOWLEDGE_MANAGE'))):
 rec=db.get(KnowledgeRelation,rid)
 if not rec:raise HTTPException(404,'关系不存在')
 audit(db,u,'DELETE','knowledge_relation',rid,{});db.delete(rec);db.commit()

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
 relations=relation_payload('scenes',sid,db);known={(x['type'],x['id']) for x in relations};relations += [{'id':x['id'],'type':'solutions','name':x['name'],'meta':{'relationLevel':x['tier']},'summary':x['summary']} for x in relation_rows if ('solutions',x['id']) not in known]
 return {'id':rec.id,'name':rec.name,'category':rec.category,'summary':rec.summary,'coverImage':rec.cover_image,'painPoints':rec.pain_points,'goals':json.loads(rec.goals_json or '[]'),'businessProcess':json.loads(rec.process_json or '[]'),'coreCapabilitySummary':rec.core_capability_summary,'status':rec.status,'updatedAt':rec.updated_at.isoformat(),'solutions':relation_rows,'relations':relations}
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
 if 'metrics' in d:d['metrics_json']=json.dumps(d.pop('metrics'),ensure_ascii=False)
 if 'input_requirements' in d:d['input_requirements_json']=json.dumps(d.pop('input_requirements'),ensure_ascii=False)
 if 'deployment_requirements' in d:d['deployment_requirements_json']=json.dumps(d.pop('deployment_requirements'),ensure_ascii=False)
 if 'boundaries' in d:d['boundaries_json']=json.dumps(d.pop('boundaries'),ensure_ascii=False)
 if 'goals' in d:d['goals_json']=json.dumps(d.pop('goals'),ensure_ascii=False)
 if 'business_process' in d:d['process_json']=json.dumps(d.pop('business_process'),ensure_ascii=False)
 allowed={'model-capabilities':{'name','description','code','version','category','function_type','metrics_json','input_requirements_json','deployment_requirements_json','boundaries_json','status'},'capabilities':{'name','description','code','version','category','function_type','metrics_json','input_requirements_json','deployment_requirements_json','boundaries_json','status'},'algorithms':{'name','description','code','version','category','input_summary','output_summary','metrics_json','boundaries_json','status'},'software':{'name','description','code','software_type','vendor','version','deployment_mode','supported_os_json','status'},'scenes':{'name','summary','category','cover_image','pain_points','goals_json','process_json','core_capability_summary','status'},'solutions':{'name','summary','code','category','scene_id','tier','status','target_description','coverage_scope','architecture_summary','implementation_notes'}}[kind]
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
 db.query(KnowledgeRelation).filter(
  ((KnowledgeRelation.source_type==kind)&(KnowledgeRelation.source_id==rid))|
  ((KnowledgeRelation.target_type==kind)&(KnowledgeRelation.target_id==rid))
 ).delete(synchronize_session=False)
 audit(db,u,'DELETE',kind,rid,{'name':rec.name});db.delete(rec)
 try:db.commit()
 except Exception as exc:db.rollback();raise HTTPException(409,'记录仍被业务数据引用') from exc
@app.post('/api/legacy/bom/recommend',include_in_schema=False)
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
@app.get('/api/legacy/projects',include_in_schema=False)
def projects(db:Session=Depends(session),u:User=Depends(permit('BOM_VIEW'))):
 return [{'id':x.id,'name':x.name,'customer':x.customer,'region':x.region,'scene':x.scene.name,'bomVersion':x.bom_version,'updatedAt':x.updated_at.isoformat()} for x in db.scalars(select(Project).order_by(Project.updated_at.desc()))]
@app.post('/api/legacy/projects',status_code=201,include_in_schema=False)
def create_project(x:ProjectIn,db:Session=Depends(session),u:User=Depends(permit('BOM_EDIT'))):
 if not db.get(Scene,x.scene_id):raise HTTPException(422,'场景不存在')
 if not x.bom_json:raise HTTPException(422,'BOM不能为空')
 rec=Project(name=x.name,customer=x.customer,region=x.region,scene_id=x.scene_id,requirements_json=json.dumps(x.requirements_json,ensure_ascii=False),bom_json=json.dumps(x.bom_json,ensure_ascii=False));db.add(rec);db.commit();db.refresh(rec);return {'id':rec.id,'name':rec.name,'bomVersion':rec.bom_version}
@app.get('/api/legacy/projects/{pid}',include_in_schema=False)
def project_detail(pid:int,db:Session=Depends(session),u:User=Depends(permit('BOM_VIEW'))):
 rec=db.get(Project,pid)
 if not rec:raise HTTPException(404,'项目不存在')
 return {'id':rec.id,'name':rec.name,'customer':rec.customer,'region':rec.region,'sceneId':rec.scene_id,'scene':rec.scene.name,'requirements':json.loads(rec.requirements_json),'bom':json.loads(rec.bom_json),'bomVersion':rec.bom_version,'updatedAt':rec.updated_at.isoformat()}
@app.patch('/api/legacy/projects/{pid}',include_in_schema=False)
def update_project(pid:int,x:ProjectPatch,db:Session=Depends(session),u:User=Depends(permit('BOM_EDIT'))):
 rec=db.get(Project,pid)
 if not rec:raise HTTPException(404,'项目不存在')
 values=x.model_dump(exclude_none=True)
 if values.get('scene_id') and not db.get(Scene,values['scene_id']):raise HTTPException(422,'场景不存在')
 for key,value in values.items():setattr(rec,key,json.dumps(value,ensure_ascii=False) if key in {'requirements_json','bom_json'} else value)
 rec.bom_version+=1;audit(db,u,'UPDATE','project',pid,{'bomVersion':rec.bom_version});db.commit();return {'id':rec.id,'name':rec.name,'bomVersion':rec.bom_version}
@app.delete('/api/legacy/projects/{pid}',status_code=204,include_in_schema=False)
def delete_project(pid:int,db:Session=Depends(session),u:User=Depends(permit('BOM_EDIT'))):
 rec=db.get(Project,pid)
 if not rec:raise HTTPException(404,'项目不存在')
 audit(db,u,'DELETE','project',pid,{'name':rec.name});db.delete(rec);db.commit()
def role_dto(x):return {'id':x.id,'code':x.code,'name':x.name,'permissions':sorted({p.permission.code for p in x.permission_links} or {p for p in x.permissions.split(',') if p}),'userCount':len(getattr(x,'users',[]) or [])}
def apply_role_permissions(db,role,requested):
 requested=set(requested);available={p.code:p for p in db.scalars(select(Permission).where(Permission.code.in_(requested)))} if requested else {};missing=requested-set(available)
 if missing:raise HTTPException(422,'权限不存在：'+','.join(sorted(missing)))
 role.permission_links.clear();db.flush()
 for code in sorted(requested):role.permission_links.append(RolePermission(permission=available[code]))
 role.permissions=','.join(sorted(requested))
@app.get('/api/admin/permissions')
def list_permissions(db:Session=Depends(session),u:User=Depends(permit('USER_MANAGE'))):
 return [{'id':x.id,'code':x.code,'name':x.name,'description':x.description} for x in db.scalars(select(Permission).order_by(Permission.code))]
@app.get('/api/admin/users')
def list_users(q:str='',source:str='',db:Session=Depends(session),u:User=Depends(permit('USER_MANAGE'))):
 st=select(User).order_by(User.username)
 if q:st=st.where(User.username.ilike('%'+q+'%')|User.display_name.ilike('%'+q+'%')|User.email.ilike('%'+q+'%'))
 if source:st=st.where(User.auth_source==source)
 return [{'id':x.id,'username':x.username,'displayName':x.display_name,'email':x.email,'department':x.department,'authSource':x.auth_source,'externalId':x.external_id,'enabled':x.enabled,'roleCode':x.role.code,'roleName':x.role.name,'lastDirectorySyncAt':x.last_directory_sync_at.isoformat() if x.last_directory_sync_at else None,'updatedAt':x.updated_at.isoformat()} for x in db.scalars(st)]
@app.post('/api/admin/users',status_code=201)
def create_user(x:UserCreate,db:Session=Depends(session),u:User=Depends(permit('USER_MANAGE'))):
 if db.scalar(select(User).where(User.username==x.username)):raise HTTPException(409,'用户名已存在')
 role=db.scalar(select(Role).where(Role.code==x.role_code))
 if not role:raise HTTPException(422,'角色不存在')
 rec=User(username=x.username,display_name=x.display_name,password_hash=pwd.hash(x.password),role_id=role.id,email=x.email,department=x.department,enabled=x.enabled,auth_source='LOCAL');db.add(rec);db.flush();audit(db,u,'CREATE','user',rec.id,{'username':rec.username,'role':role.code});db.commit();db.refresh(rec);return {'id':rec.id,'username':rec.username}
@app.patch('/api/admin/users/{user_id}')
def update_user_admin(user_id:int,x:UserPatch,db:Session=Depends(session),u:User=Depends(permit('USER_MANAGE'))):
 rec=db.get(User,user_id)
 if not rec:raise HTTPException(404,'用户不存在')
 values=x.model_dump(exclude_none=True)
 if 'role_code' in values:
  role=db.scalar(select(Role).where(Role.code==values.pop('role_code')))
  if not role:raise HTTPException(422,'角色不存在')
  rec.role_id=role.id
 if 'password' in values:
  if rec.auth_source=='AD':raise HTTPException(422,'AD用户密码由域控管理')
  rec.password_hash=pwd.hash(values.pop('password'))
 for key,value in values.items():setattr(rec,key,value)
 if rec.id==u.id and not rec.enabled:raise HTTPException(422,'不能禁用当前登录用户')
 audit(db,u,'UPDATE','user',rec.id,{'fields':sorted(x.model_dump(exclude_none=True))});db.commit();return {'id':rec.id,'username':rec.username,'enabled':rec.enabled}
@app.delete('/api/admin/users/{user_id}',status_code=204)
def delete_user_admin(user_id:int,db:Session=Depends(session),u:User=Depends(permit('USER_MANAGE'))):
 rec=db.get(User,user_id)
 if not rec:raise HTTPException(404,'用户不存在')
 if rec.id==u.id:raise HTTPException(422,'不能删除当前登录用户')
 audit(db,u,'DELETE','user',rec.id,{'username':rec.username});db.delete(rec);db.commit()
@app.get('/api/admin/roles')
def roles(db:Session=Depends(session),u:User=Depends(permit('USER_MANAGE'))):return [role_dto(x) for x in db.scalars(select(Role).order_by(Role.code))]
@app.post('/api/admin/roles',status_code=201)
def create_role(x:RoleCreate,db:Session=Depends(session),u:User=Depends(permit('USER_MANAGE'))):
 if db.scalar(select(Role).where(Role.code==x.code)):raise HTTPException(409,'角色编码已存在')
 role=Role(code=x.code,name=chinese_role_name(x.name),permissions='');db.add(role);db.flush();apply_role_permissions(db,role,x.permissions);audit(db,u,'CREATE','role',role.id,x.model_dump());db.commit();db.refresh(role);return role_dto(role)
@app.patch('/api/admin/roles/{role_code}')
def update_role(role_code:str,x:RolePatch,db:Session=Depends(session),u:User=Depends(permit('USER_MANAGE'))):
 role=db.scalar(select(Role).where(Role.code==role_code))
 if not role:raise HTTPException(404,'角色不存在')
 if x.name is not None:role.name=chinese_role_name(x.name)
 if x.permissions is not None:apply_role_permissions(db,role,x.permissions)
 audit(db,u,'UPDATE','role',role.id,x.model_dump(exclude_none=True));db.commit();return role_dto(role)
@app.delete('/api/admin/roles/{role_code}',status_code=204)
def delete_role(role_code:str,db:Session=Depends(session),u:User=Depends(permit('USER_MANAGE'))):
 role=db.scalar(select(Role).where(Role.code==role_code))
 if not role:raise HTTPException(404,'角色不存在')
 if role.code=='admin' or db.scalar(select(func.count(User.id)).where(User.role_id==role.id)):raise HTTPException(422,'系统角色或已分配用户的角色不能删除')
 audit(db,u,'DELETE','role',role.id,{'code':role.code});db.delete(role);db.commit()
@app.patch('/api/admin/roles/{role_code}/permissions')
def update_role_permissions(role_code:str,x:RolePermissionPatch,db:Session=Depends(session),u:User=Depends(permit('USER_MANAGE'))):
 role=db.scalar(select(Role).where(Role.code==role_code))
 if not role:raise HTTPException(404,'角色不存在')
 apply_role_permissions(db,role,x.permissions);audit(db,u,'UPDATE','role_permissions',role.id,{'permissions':sorted(x.permissions)});db.commit();return role_dto(role)
def directory_config_dto(config):
 return {'enabled':bool(config and config.enabled),'serverType':config.server_type if config else 'MS_ACTIVE_DIRECTORY','protocol':config.protocol if config else 'LDAP','host':config.host if config else '','port':config.port if config else 389,'timeoutSeconds':config.timeout_seconds if config else 30,'bindDn':config.bind_dn if config else '','passwordConfigured':bool(config and config.bind_password_encrypted),'baseDn':config.base_dn if config else '','loginDomain':config.login_domain if config else '','userFilter':config.user_filter if config else '(&(objectClass=user)(sAMAccountName=*))','defaultRole':config.default_role if config else 'sales','lastTestStatus':config.last_test_status if config else 'UNTESTED','lastTestMessage':config.last_test_message if config else '','lastTestAt':config.last_test_at.isoformat() if config and config.last_test_at else None}
def validate_directory_values(x,password_available=False):
 missing=[name for name,value in [('服务器地址',x.host.strip()),('管理员账号',x.bind_dn.strip()),('Base DN',x.base_dn.strip()),('管理密码',x.bind_password or password_available)] if not value]
 if missing:raise HTTPException(422,'请填写：'+'、'.join(missing))
 if x.login_domain and ('=' in x.login_domain or ',' in x.login_domain):raise HTTPException(422,'登录域请填写域名，例如 hilaicloud.com，不要填写 Base DN')
@app.get('/api/admin/directory/status')
def directory_status(db:Session=Depends(session),u:User=Depends(permit('USER_MANAGE'))):
 config=get_directory_config(db);last=db.scalar(select(DirectorySyncRun).order_by(DirectorySyncRun.created_at.desc()))
 pending=db.scalar(select(func.count(DirectorySyncCandidate.id)).where(DirectorySyncCandidate.run_id==last.id,DirectorySyncCandidate.approval_status=='PENDING')) if last else 0
 result=directory_config_dto(config);result['configured']=ad_ready(config);result['lastRun']=({'id':last.id,'status':last.status,'created':last.created_count,'updated':last.updated_count,'pending':pending,'error':last.error_message,'finishedAt':last.finished_at.isoformat() if last.finished_at else None} if last else None);return result
@app.put('/api/admin/directory/config')
def save_directory_config(x:DirectoryConfigInput,db:Session=Depends(session),u:User=Depends(permit('USER_MANAGE'))):
 config=get_directory_config(db);password_available=bool(config and config.bind_password_encrypted)
 if x.enabled:validate_directory_values(x,password_available)
 role=db.scalar(select(Role).where(Role.code==x.default_role))
 if not role:raise HTTPException(422,'默认角色不存在')
 if not config:config=DirectoryConfig(id=1);db.add(config)
 for field in ('enabled','server_type','protocol','host','port','timeout_seconds','bind_dn','base_dn','login_domain','user_filter','default_role'):setattr(config,field,getattr(x,field))
 if x.bind_password:config.bind_password_encrypted=encrypt_directory_password(x.bind_password)
 config.last_test_status='UNTESTED';config.last_test_message='配置已变更，请执行连通性测试';config.last_test_at=None
 audit(db,u,'UPDATE','directory_config',config.id,{'enabled':x.enabled,'serverType':x.server_type,'protocol':x.protocol,'host':x.host,'port':x.port,'timeoutSeconds':x.timeout_seconds,'bindDn':x.bind_dn,'baseDn':x.base_dn,'loginDomain':x.login_domain,'defaultRole':x.default_role,'passwordChanged':bool(x.bind_password)});db.commit();db.refresh(config);return directory_config_dto(config)
@app.post('/api/admin/directory/test')
def test_directory_config(x:DirectoryConfigInput,db:Session=Depends(session),u:User=Depends(permit('USER_MANAGE'))):
 saved=get_directory_config(db);validate_directory_values(x,bool(saved and saved.bind_password_encrypted))
 config=DirectoryConfig(server_type=x.server_type,protocol=x.protocol,host=x.host,port=x.port,timeout_seconds=x.timeout_seconds,bind_dn=x.bind_dn,base_dn=x.base_dn,login_domain=x.login_domain,user_filter=x.user_filter,default_role=x.default_role,bind_password_encrypted=saved.bind_password_encrypted if saved else '')
 try:
  connection=directory_connection(config,x.bind_password);connection.search(x.base_dn,'(objectClass=*)',attributes=[]);connection.unbind();message=f'{x.protocol} {x.host}:{x.port} 连接和目录认证成功'
  if saved:saved.last_test_status='SUCCESS';saved.last_test_message=message;saved.last_test_at=datetime.now(timezone.utc);db.commit()
  audit(db,u,'TEST','directory_config',saved.id if saved else 'unsaved',{'protocol':x.protocol,'host':x.host,'port':x.port,'success':True});db.commit();return {'success':True,'message':message}
 except Exception as exc:
  message='连接失败：'+directory_error_message(exc,300)
  if saved:saved.last_test_status='FAILED';saved.last_test_message=message;saved.last_test_at=datetime.now(timezone.utc);db.commit()
  raise HTTPException(502,message)
def directory_candidate_dto(row,db):
 existing=db.scalar(select(User).where((User.external_id==row.external_id)|(User.username==row.username)))
 return {'id':row.id,'runId':row.run_id,'username':row.username,'displayName':row.display_name,'email':row.email,'department':row.department,'distinguishedName':row.distinguished_name,'changeType':row.change_type,'approvalStatus':row.approval_status,'roleCode':existing.role.code if existing else row.role_code,'existingUser':bool(existing)}
@app.get('/api/admin/directory/candidates')
def directory_candidates(run_id:int|None=None,db:Session=Depends(session),u:User=Depends(permit('USER_MANAGE'))):
 if run_id is None:
  run=db.scalar(select(DirectorySyncRun).where(DirectorySyncRun.status=='PENDING_CONFIRMATION').order_by(DirectorySyncRun.created_at.desc()))
  if not run:return {'runId':None,'items':[]}
  run_id=run.id
 rows=db.scalars(select(DirectorySyncCandidate).where(DirectorySyncCandidate.run_id==run_id).order_by(DirectorySyncCandidate.department,DirectorySyncCandidate.display_name,DirectorySyncCandidate.username))
 return {'runId':run_id,'items':[directory_candidate_dto(row,db) for row in rows]}
@app.post('/api/admin/directory/sync')
def sync_directory(db:Session=Depends(session),u:User=Depends(permit('USER_MANAGE'))):
 run=DirectorySyncRun(status='RUNNING',initiated_by=u.id);db.add(run);db.commit();db.refresh(run)
 config=get_directory_config(db)
 if not ad_ready(config):run.status='FAILED';run.error_message='AD同步未启用或连接参数未配置完整';run.finished_at=datetime.now(timezone.utc);db.commit();raise HTTPException(503,'请先启用并保存完整的 AD 配置')
 try:
  from ldap3 import SUBTREE
  connection=directory_connection(config)
  username_attribute='sAMAccountName';display_name_attribute='displayName';email_attribute='mail';department_attribute='department';external_id_attribute='objectGUID'
  attributes=[username_attribute,display_name_attribute,email_attribute,department_attribute,external_id_attribute];connection.search(config.base_dn,config.user_filter,search_scope=SUBTREE,attributes=attributes)
  role=db.scalar(select(Role).where(Role.code==config.default_role)) or db.scalar(select(Role).where(Role.code=='sales'))
  if not role:raise RuntimeError('AD默认角色不存在')
  seen=set()
  for entry in connection.entries:
   def value(name):
    item=getattr(entry,name,None);raw=item.value if item is not None else '';return raw.hex() if isinstance(raw,bytes) else str(raw or '')
   username=value(username_attribute).strip()
   if not username:continue
   distinguished_name=str(entry.entry_dn);department=value(department_attribute) or next((part[3:] for part in distinguished_name.split(',') if part.upper().startswith('OU=') and part[3:]!='浙江海莱云智科技有限公司'),'')
   seen.add(username.lower());external=value(external_id_attribute) or distinguished_name;rec=db.scalar(select(User).where((User.external_id==external)|(User.username==username)))
   candidate=DirectorySyncCandidate(run_id=run.id,external_id=external,username=username,display_name=value(display_name_attribute) or username,email=value(email_attribute),department=department,distinguished_name=distinguished_name,change_type='UPDATE' if rec else 'CREATE',role_code=rec.role.code if rec else role.code);db.add(candidate)
  connection.unbind();run.status='PENDING_CONFIRMATION';audit(db,u,'PREVIEW','active_directory',run.id,{'candidates':len(seen)});db.commit();return directory_candidates(run.id,db,u)
 except Exception as exc:
  message=directory_error_message(exc)
  db.rollback();run=db.get(DirectorySyncRun,run.id);run.status='FAILED';run.error_message=message;run.finished_at=datetime.now(timezone.utc);db.commit();raise HTTPException(502,'AD同步失败：'+message[:200])
@app.post('/api/admin/directory/confirm')
def confirm_directory(x:DirectoryConfirm,db:Session=Depends(session),u:User=Depends(permit('USER_MANAGE'))):
 run=db.get(DirectorySyncRun,x.run_id)
 if not run or run.status!='PENDING_CONFIRMATION':raise HTTPException(409,'该同步批次不存在或已经处理')
 if not x.users:raise HTTPException(422,'请至少选择一个允许登录的域用户')
 selected={item.candidate_id:item.role_code for item in x.users};candidates=list(db.scalars(select(DirectorySyncCandidate).where(DirectorySyncCandidate.run_id==run.id)))
 if set(selected)-{item.id for item in candidates}:raise HTTPException(422,'包含不属于本批次的候选用户')
 roles={role.code:role for role in db.scalars(select(Role).where(Role.code.in_(set(selected.values()))))} if selected else {}
 if set(selected.values())-set(roles):raise HTTPException(422,'包含不存在的角色')
 now_value=datetime.now(timezone.utc)
 for item in candidates:
  if item.id not in selected:item.approval_status='SKIPPED';continue
  rec=db.scalar(select(User).where((User.external_id==item.external_id)|(User.username==item.username)))
  if not rec:rec=User(username=item.username,display_name=item.display_name,password_hash=pwd.hash(secrets.token_urlsafe(32)),role_id=roles[selected[item.id]].id,auth_source='AD',external_id=item.external_id);db.add(rec);run.created_count+=1
  else:run.updated_count+=1
  rec.display_name=item.display_name;rec.email=item.email;rec.department=item.department;rec.role_id=roles[selected[item.id]].id;rec.auth_source='AD';rec.external_id=item.external_id;rec.last_directory_sync_at=now_value;rec.enabled=True;item.approval_status='APPROVED';item.role_code=selected[item.id]
 run.status='SUCCESS';run.finished_at=now_value;audit(db,u,'CONFIRM','active_directory',run.id,{'selected':len(selected),'created':run.created_count,'updated':run.updated_count});db.commit();return {'status':'SUCCESS','created':run.created_count,'updated':run.updated_count,'selected':len(selected)}
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

from .phase2 import build_phase2_router
app.include_router(build_phase2_router(user,permit,permission_codes,audit))

# Frozen V3 aliases keep knowledge-center writes on the same canonical paths as reads.
# These routes are declared after specific APIs so existing business endpoints retain priority.
@app.post('/api/{kind}',status_code=201)
def create_center(kind:str,x:CatalogIn,db:Session=Depends(session),u:User=Depends(user)):
 return create_catalog(kind,x,db,u)

@app.patch('/api/{kind}/{rid}')
def update_center(kind:str,rid:int,x:CatalogPatch,db:Session=Depends(session),u:User=Depends(user)):
 return update_catalog(kind,rid,x,db,u)

@app.delete('/api/{kind}/{rid}',status_code=204)
def delete_center(kind:str,rid:int,db:Session=Depends(session),u:User=Depends(user)):
 return delete_catalog(kind,rid,db,u)

STATIC_ROOT=os.path.join(os.path.dirname(os.path.dirname(__file__)),'static')
@app.get('/{path:path}',include_in_schema=False)
def frontend(path:str):
 candidate=os.path.join(STATIC_ROOT,path)
 if path and os.path.isfile(candidate): return FileResponse(candidate)
 return FileResponse(os.path.join(STATIC_ROOT,'index.html'))
