import json, hashlib, hmac, os, base64
from sqlalchemy import select
from .models import Role,Permission,RolePermission,User,ProductCategory,Product,ProductCapability,Capability,Algorithm,Software,Scene,Solution,BomRule,ProductPrice,SolutionBomItem,KnowledgeRelation
class Passwords:
 def hash(self,value):
  salt=os.urandom(16); digest=hashlib.pbkdf2_hmac('sha256',value.encode(),salt,210000)
  return 'pbkdf2_sha256$210000$%s$%s'%(base64.b64encode(salt).decode(),base64.b64encode(digest).decode())
 def verify(self,value,stored):
  _,rounds,salt,digest=stored.split('$'); candidate=hashlib.pbkdf2_hmac('sha256',value.encode(),base64.b64decode(salt),int(rounds))
  return hmac.compare_digest(candidate,base64.b64decode(digest))
pwd=Passwords()
PERMS={
'sales':'KNOWLEDGE_VIEW',
'presales':'KNOWLEDGE_VIEW',
'sales_support':'KNOWLEDGE_VIEW,PRICE_VIEW',
'product_admin':'KNOWLEDGE_VIEW,KNOWLEDGE_MANAGE,PRICE_VIEW',
'algorithm_admin':'KNOWLEDGE_VIEW,KNOWLEDGE_MANAGE,PRICE_VIEW',
'price_admin':'KNOWLEDGE_VIEW,PRICE_VIEW',
'admin':'KNOWLEDGE_VIEW,KNOWLEDGE_MANAGE,PRICE_VIEW'}
def bootstrap(db):
 if db.scalar(select(Role.id).limit(1)): return
 bootstrap_passwords=json.loads(os.environ.get('BOOTSTRAP_PASSWORDS_JSON','{}'))
 missing=sorted(set(PERMS)-set(bootstrap_passwords))
 if missing: raise RuntimeError('BOOTSTRAP_PASSWORDS_JSON must define every initial role')
 roles={k:Role(code=k,name=k.replace('_',' ').title(),permissions=v) for k,v in PERMS.items()};db.add_all(roles.values());db.flush()
 permission_codes=sorted({code for values in PERMS.values() for code in values.split(',') if code})
 permissions={code:Permission(code=code,name=code.replace('_',' ').title()) for code in permission_codes};db.add_all(permissions.values());db.flush()
 db.add_all([RolePermission(role_id=role.id,permission_id=permissions[code].id) for key,role in roles.items() for code in PERMS[key].split(',') if code])
 for k in roles: db.add(User(username=k,display_name={'admin':'系统管理员','sales':'销售专员','sales_support':'销售支持'}.get(k,k),password_hash=pwd.hash(bootstrap_passwords[k]),role_id=roles[k].id))
 cats=[ProductCategory(name=x,description=x+'产品分类') for x in ['监测终端','智能分析','综合平台','桥梁防撞','雷达感知','通信与控制']];db.add_all(cats);db.flush()
 names=[('岸海船舶监测终端','HZ-MT-100'),('海智AI分析终端','HZ-AI-200'),('智慧海洋综合管控平台','HZ-OC-300'),('桥梁防撞综合系统','HZ-BC-400'),('雷达融合感知终端','HZ-RF-500'),('船舶智能识别终端','HZ-VI-600'),('航道视频联动终端','HZ-VC-700'),('水域安全边缘网关','HZ-EG-800'),('AIS融合服务器','HZ-AS-900'),('船名OCR识别服务','HZ-OCR-1000'),('偏航预警分析服务','HZ-YW-1100'),('超高预警分析服务','HZ-OH-1200'),('港口监管一体机','HZ-PM-1300'),('浮标监测接入终端','HZ-BU-1400'),('应急指挥协同平台','HZ-EC-1500')]
 products=[]
 for i,(n,m) in enumerate(names): products.append(Product(name=n,model_code=m,category_id=cats[i%len(cats)].id,summary='面向水域安全与智能监管的正式演示产品。',source='产品中心正式演示数据',owner='产品管理部'))
 db.add_all(products)
 caps=[Capability(name=x,category='感知与分析',description=x+'能力，覆盖水域监管业务场景。') for x in ['AIS融合','雷视融合','偏航预警','船名OCR','超高预警','球机联动','船舶检测','目标跟踪','航迹预测','入侵检测','视频结构化','告警联动','电子围栏','VHF通信','多源态势融合']];db.add_all(caps)
 db.flush();db.add_all([ProductCapability(product_id=products[i%len(products)].id,capability_id=caps[i].id) for i in range(len(caps))])
 db.add_all([Algorithm(name=x,version='v1.0',category='视觉智能',description=x+'算法，支持正式演示环境。') for x in ['船名OCR','船舶检测','偏航识别','超高识别','目标跟踪','航迹预测','雷视融合','AIS融合','入侵检测','视频结构化']])
 db.add_all([Software(name=x,version=v,description=x+'软件模块。') for x,v in [('海智综合管控平台','3.2.0'),('智能视频分析平台','2.8.1'),('多源态势融合平台','1.9.0')]])
 scenes=[Scene(name=x,summary=x+'场景，通过产品、能力和方案建立配置关系。',pain_points='现场感知不足、信息孤岛、告警联动效率低。') for x in ['桥梁防撞','智慧航道','港口监管','水域监管','近海风场']];db.add_all(scenes);db.flush()
 db.add_all([Solution(name=s.name+'标准方案',scene_id=s.id,tier='标准型',summary='覆盖核心能力与标准设备的可落地方案。') for s in scenes]+[Solution(name='桥梁防撞增强方案',scene_id=scenes[0].id,tier='增强型',summary='增加雷视融合与冗余链路。')])
 db.add_all([BomRule(code='BRIDGE_AIS',name='桥梁防撞AIS融合规则',condition_json='{"scene":"桥梁防撞","ais":true}',recommendation_json='{"model":"HZ-AS-900","quantity":1,"reason":"提供AIS融合"}'),BomRule(code='BRIDGE_CAMERA',name='桥梁防撞球机规则',condition_json='{"scene":"桥梁防撞"}',recommendation_json='{"model":"HZ-VC-700","quantity_from":"ptz_count","reason":"提供球机联动"}')])
 db.flush();db.add_all([ProductPrice(product_id=p.id,reference_price=100000+i*12500,cost_price=65000+i*8000) for i,p in enumerate(products[:10])]);db.commit()

def ensure_v3_seed(db):
 products=list(db.scalars(select(Product).order_by(Product.id)))
 software=list(db.scalars(select(Software).order_by(Software.id)))
 algorithms=list(db.scalars(select(Algorithm).order_by(Algorithm.id)))
 capabilities=list(db.scalars(select(Capability).order_by(Capability.id)))
 scenes=list(db.scalars(select(Scene).order_by(Scene.id)))
 solutions=list(db.scalars(select(Solution).order_by(Solution.id)))
 if not all([products,software,algorithms,capabilities,scenes,solutions]):return

 product_types=['HARDWARE','HARDWARE','SOFTWARE_PRODUCT','SYSTEM_SOLUTION','HARDWARE','AI_PRODUCT','HARDWARE','HARDWARE','SOFTWARE_PRODUCT','AI_PRODUCT','AI_PRODUCT','AI_PRODUCT','HARDWARE','ACCESSORY','SOFTWARE_PRODUCT']
 for index,product in enumerate(products):
  product.product_type=product_types[index%len(product_types)];product.main_image='';product.dynamic_fields_json=json.dumps({'工作温度':'-20℃至60℃','防护等级':'IP66'} if product.product_type=='HARDWARE' else {'部署方式':'私有化部署','支持架构':'x86/ARM'})

 software_profiles=[('HZ-SW-OC','PLATFORM','PRIVATE',['Linux','国产操作系统']),('HZ-SW-AI','PLATFORM','HYBRID',['Linux']),('HZ-SW-FUSION','SERVICE','PRIVATE',['Linux','Windows'])]
 for item,profile in zip(software,software_profiles):item.code,item.software_type,item.deployment_mode,systems=profile;item.vendor='海智科技';item.supported_os_json=json.dumps(systems,ensure_ascii=False)

 for index,item in enumerate(algorithms):
  item.code=f'HZ-ALG-{index+1:03d}';item.input_summary='AIS、雷达、视频或结构化目标数据';item.output_summary='风险事件、目标属性与置信度结果';item.metrics_json=json.dumps({'准确率':f'{92+index%6}%','处理帧率':f'{20+index%10} FPS'},ensure_ascii=False);item.boundaries_json=json.dumps(['需满足输入数据质量要求','极端天气下性能可能下降'],ensure_ascii=False)

 function_types=['融合','检测','预警','识别','预警','联动','检测','跟踪','预测','分析','识别','联动','分析','通信','融合']
 for index,item in enumerate(capabilities):
  item.code=f'HZ-MC-{index+1:03d}';item.version='V2.'+str(index%4+1);item.function_type=function_types[index%len(function_types)];item.metrics_json=json.dumps({'准确率':f'{93+index%5}%','响应延迟':f'{80+index*3} ms'},ensure_ascii=False);item.input_requirements_json=json.dumps({'输入类型':'视频/结构化数据','推荐分辨率':'1080P'},ensure_ascii=False);item.deployment_requirements_json=json.dumps({'运行环境':'Linux','推荐算力':'16 TOPS'},ensure_ascii=False);item.boundaries_json=json.dumps(['需完成现场标定','遮挡严重时需人工复核'],ensure_ascii=False)

 for index,item in enumerate(scenes):
  item.category=['水域安全','航道监管','港口监管','综合监管','海上设施'][index%5];item.goals_json=json.dumps(['提升多源感知覆盖率','缩短风险事件响应时间'],ensure_ascii=False);item.process_json=json.dumps(['采集多源数据','模型分析研判','联动告警处置','形成事件闭环'],ensure_ascii=False);item.core_capability_summary='融合感知、目标识别、风险预警与联动处置';item.cover_image=''

 for index,item in enumerate(solutions):
  item.code=f'HZ-SOL-{index+1:03d}';item.category=scenes[index%len(scenes)].category;item.status='ACTIVE';item.target_description='面向'+item.scene.name+'的标准化建设与交付';item.coverage_scope='覆盖感知、分析、告警、处置和复盘全流程';item.architecture_summary='前端感知层、边缘智能层、平台服务层和业务应用层';item.implementation_notes='按现场勘察、方案确认、部署联调和验收交付四阶段实施'

 dirty_tokens=['测试','嗯嗯嗯','Product A','Demo']
 for model in [Product,Software,Algorithm,Capability,Scene,Solution]:
  for item in db.scalars(select(model)):
   if any(token.lower() in item.name.lower() for token in dirty_tokens):item.name=f'海智正式知识条目-{model.__tablename__}-{item.id}'

 for solution in solutions:
  if not db.scalar(select(SolutionBomItem.id).where(SolutionBomItem.solution_id==solution.id).limit(1)):
   for offset,product in enumerate(products[:3]):db.add(SolutionBomItem(solution_id=solution.id,product_id=product.id,quantity=1 if offset<2 else 2,unit='套' if offset<2 else '台',purpose=['核心平台','智能分析','现场感知'][offset],requirement_level=['REQUIRED','RECOMMENDED','OPTIONAL'][offset],recommendation_reason='满足方案标准能力覆盖'))

 relation_specs=[]
 for index,product in enumerate(products):
  relation_specs += [('products',product.id,'model-capabilities',capabilities[index%len(capabilities)].id,{'supportVersion':'V2.x','recommendedConcurrency':4,'maxConcurrency':8,'supportStatus':'SUPPORTED'}),('products',product.id,'software',software[index%len(software)].id,{'minimumVersion':'V1.0','supportStatus':'SUPPORTED','purpose':'业务平台接入'}),('products',product.id,'algorithms',algorithms[index%len(algorithms)].id,{'supportVersion':'V1.x','purpose':'智能分析','supportStatus':'SUPPORTED'}),('products',product.id,'scenes',scenes[index%len(scenes)].id,{'relationLevel':'RECOMMENDED','recommendationReason':'匹配核心业务需求'})]
 for index,solution in enumerate(solutions):relation_specs.append(('solutions',solution.id,'scenes',solution.scene_id,{'relationLevel':'CORE','purpose':'标准适用场景'}))
 for source_type,source_id,target_type,target_id,metadata in relation_specs:
  exists=db.scalar(select(KnowledgeRelation.id).where(KnowledgeRelation.source_type==source_type,KnowledgeRelation.source_id==source_id,KnowledgeRelation.target_type==target_type,KnowledgeRelation.target_id==target_id).limit(1))
  if not exists:db.add(KnowledgeRelation(source_type=source_type,source_id=source_id,target_type=target_type,target_id=target_id,metadata_json=json.dumps(metadata,ensure_ascii=False)))
 db.commit()
