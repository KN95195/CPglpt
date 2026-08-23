import json, hashlib, hmac, os, base64
from sqlalchemy import select
from .models import (
 Role,Permission,RolePermission,User,ProductCategory,Product,ProductParameter,
 ProductFeature,ProductCapability,Capability,ModelMetric,ModelInputDefinition,
 ModelOutputDefinition,Algorithm,AlgorithmParameter,AlgorithmMetric,Software,
 SoftwareModule,SoftwareFeature,SoftwareVersion,Scene,ScenePain,SceneGoal,
 SceneProcessStep,Solution,SolutionArchitectureNode,SolutionCapabilityCoverage,
 BomRule,ProductPrice,SolutionBomItem,KnowledgeRelation,
)
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
'admin':'KNOWLEDGE_VIEW,KNOWLEDGE_MANAGE,PRICE_VIEW,USER_MANAGE'}
def bootstrap(db):
 if db.scalar(select(Role.id).limit(1)): return
 bootstrap_passwords=json.loads(os.environ.get('BOOTSTRAP_PASSWORDS_JSON','{}'))
 missing=sorted(set(PERMS)-set(bootstrap_passwords))
 if missing: raise RuntimeError('BOOTSTRAP_PASSWORDS_JSON must define every initial role')
 roles={k:Role(code=k,name=k.replace('_',' ').title(),permissions=v) for k,v in PERMS.items()};db.add_all(roles.values());db.flush()
 permission_codes=sorted({code for values in PERMS.values() for code in values.split(',') if code})
 permissions={item.code:item for item in db.scalars(select(Permission).where(Permission.code.in_(permission_codes)))}
 missing_permissions=[Permission(code=code,name=code.replace('_',' ').title()) for code in permission_codes if code not in permissions]
 db.add_all(missing_permissions);db.flush();permissions.update({item.code:item for item in missing_permissions})
 db.add_all([RolePermission(role_id=role.id,permission_id=permissions[code].id) for key,role in roles.items() for code in PERMS[key].split(',') if code])
 for k in roles: db.add(User(username=k,display_name={'admin':'系统管理员','sales':'销售专员','sales_support':'销售支持'}.get(k,k),password_hash=pwd.hash(bootstrap_passwords[k]),role_id=roles[k].id))
 cats=[ProductCategory(name=x,description=x+'产品分类') for x in ['监测终端','智能分析','综合平台','桥梁防撞','雷达感知','通信与控制']];db.add_all(cats);db.flush()
 names=[('岸海船舶监测终端','HZ-MT-100'),('海智AI分析终端','HZ-AI-200'),('智慧海洋综合管控平台','HZ-OC-300'),('桥梁防撞综合系统','HZ-BC-400'),('雷达融合感知终端','HZ-RF-500'),('船舶智能识别终端','HZ-VI-600'),('航道视频联动终端','HZ-VC-700'),('水域安全边缘网关','HZ-EG-800'),('AIS融合服务器','HZ-AS-900'),('船名OCR识别服务','HZ-OCR-1000'),('偏航预警分析服务','HZ-YW-1100'),('超高预警分析服务','HZ-OH-1200'),('港口监管一体机','HZ-PM-1300'),('浮标监测接入终端','HZ-BU-1400'),('应急指挥协同平台','HZ-EC-1500')]
 products=[]
 for i,(n,m) in enumerate(names): products.append(Product(name=n,product_code=m,model_code=m,category_id=cats[i%len(cats)].id,summary='面向水域安全与智能监管的正式演示产品。',source='产品中心正式演示数据',owner='产品管理部'))
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

 product_types=['HARDWARE','HARDWARE','SOFTWARE_PRODUCT','SYSTEM_PRODUCT','HARDWARE','HARDWARE','HARDWARE','HARDWARE','SOFTWARE_PRODUCT','SOFTWARE_PRODUCT','SOFTWARE_PRODUCT','SOFTWARE_PRODUCT','HARDWARE','ACCESSORY','SOFTWARE_PRODUCT']
 for index,product in enumerate(products):
  product.product_type=product_types[index%len(product_types)];product.product_code=product.product_code or product.model_code;product.product_series=product.product_series or '海智水域智能';product.current_version=product.current_version or 'V1.0';product.description=product.description or product.summary;product.main_image=product.main_image or ('/assets/product-radar.png' if index%2==0 else '/assets/product-terminal.png');product.tags_json=json.dumps(['水域安全','智能监管'],ensure_ascii=False);product.boundaries_json=json.dumps(['具体现场适配范围以项目勘察结果为准'],ensure_ascii=False)
  if not product.parameters:
   defaults=[('产品型号',product.model_code,'','基础信息',True),('当前版本',product.current_version,'','基础信息',False),('关键性能参数','待产品资料确认','','技术参数',True)]
   product.parameters=[ProductParameter(name=n,value=v,unit=u,group_name=g,highlight=h,data_type='TEXT',sort_order=i) for i,(n,v,u,g,h) in enumerate(defaults)]
  if not product.features:
   product.features=[ProductFeature(title='多源数据接入',description='面向水域业务的标准化数据接入与处理能力',sort_order=0),ProductFeature(title='私有化部署',description='支持按项目环境进行本地部署与集成',sort_order=1)]
  product.dynamic_fields_json=json.dumps({x.name:x.value for x in product.parameters},ensure_ascii=False)

 software_profiles=[('HZ-SW-OC','PLATFORM','PRIVATE',['Linux','国产操作系统']),('HZ-SW-AI','PLATFORM','HYBRID',['Linux']),('HZ-SW-FUSION','SERVICE','PRIVATE',['Linux','Windows'])]
 for item,profile in zip(software,software_profiles):
  item.code,item.software_type,item.deployment_mode,systems=profile;item.vendor='海智科技';item.supported_os_json=json.dumps(systems,ensure_ascii=False);item.database_json=json.dumps(['PostgreSQL'],ensure_ascii=False);item.protocols_json=json.dumps(['HTTPS','REST API'],ensure_ascii=False);item.detail_description=item.detail_description or item.description;item.boundaries_json=json.dumps(['具体接口与部署规格以项目技术协议为准'],ensure_ascii=False)
  if not item.modules:
   item.modules=[SoftwareModule(name='综合态势',description='汇聚多源感知数据并形成统一态势',sort_order=0,features=[SoftwareFeature(name='态势展示',description='统一展示目标、设备和事件',sort_order=0)]),SoftwareModule(name='告警处置',description='承载告警确认、分派与闭环',sort_order=1,features=[SoftwareFeature(name='事件闭环',description='记录告警处理全过程',sort_order=0)])]
  if not item.versions:item.versions=[SoftwareVersion(version=item.version,summary='当前正式版本')]

 for index,item in enumerate(algorithms):
  item.code=f'HZ-ALG-{index+1:03d}';item.principle=item.principle or '对输入目标数据进行特征提取、规则分析与结果输出。';item.input_summary='AIS、雷达、视频或结构化目标数据';item.output_summary='风险事件、目标属性与置信度结果';item.metrics_json=json.dumps({'准确率':'待测试报告确认','处理性能':'待测试报告确认'},ensure_ascii=False);item.boundaries_json=json.dumps(['需满足输入数据质量要求','极端天气下需人工复核'],ensure_ascii=False)
  if not item.parameters:item.parameters=[AlgorithmParameter(name='时间窗口',value='按场景配置',group_name='运行参数',sort_order=0),AlgorithmParameter(name='告警阈值',value='按项目规则配置',group_name='规则参数',sort_order=1)]
  if not item.metrics:item.metrics=[AlgorithmMetric(name='准确率',value='待测试报告确认',group_name='性能指标',condition='待确认',source='待产品测试报告确认',highlight=True,sort_order=0)]

 function_types=['融合','检测','预警','识别','预警','联动','检测','跟踪','预测','分析','识别','联动','分析','通信','融合']
 for index,item in enumerate(capabilities):
  item.code=f'HZ-MC-{index+1:03d}';item.version='V2.'+str(index%4+1);item.function_type=function_types[index%len(function_types)];item.model_type=['FUSION','DETECTION','TIME_SERIES','OCR','DETECTION'][index%5];item.task_type=item.function_type;item.metrics_json=json.dumps({'准确率':'待测试报告确认','响应延迟':'待测试报告确认'},ensure_ascii=False);item.input_requirements_json=json.dumps({'输入类型':'视频或结构化数据','数据质量':'满足项目接入规范'},ensure_ascii=False);item.deployment_requirements_json=json.dumps({'运行环境':'Linux','推荐硬件':'待项目并发量评估后确认'},ensure_ascii=False);item.use_conditions_json=json.dumps(['需完成现场数据标定与接入验证'],ensure_ascii=False);item.boundaries_json=json.dumps(['遮挡严重或输入质量不足时需人工复核'],ensure_ascii=False)
  if not item.metrics:item.metrics=[ModelMetric(name='准确率',value='待测试报告确认',group_name='性能指标',condition='待确认',source='待产品测试报告确认',dataset='待确认',highlight=True,sort_order=0)]
  if not item.inputs:item.inputs=[ModelInputDefinition(name='业务数据',data_type='JSON/Stream',required=True,description='符合项目接入规范的视频或结构化数据',sort_order=0)]
  if not item.outputs:item.outputs=[ModelOutputDefinition(name='分析结果',data_type='JSON',description='目标属性、事件类型与置信信息',sort_order=0)]

 for index,item in enumerate(scenes):
  item.category=['水域安全','航道监管','港口监管','综合监管','海上设施'][index%5];item.tags_json=json.dumps([item.category,'多源感知'],ensure_ascii=False);item.conditions_json=json.dumps(['现场具备基础感知与网络条件','完成业务规则确认'],ensure_ascii=False);item.goals_json=json.dumps(['提升多源感知覆盖','缩短风险事件响应时间'],ensure_ascii=False);item.process_json=json.dumps(['采集多源数据','模型分析研判','联动告警处置','形成事件闭环'],ensure_ascii=False);item.core_capability_summary='融合感知、目标识别、风险预警与联动处置';item.cover_image=item.cover_image or ('/assets/bridge-ship-waterway.jpg' if index==0 else '/assets/scene-waterway.png')
  if not item.pains:item.pains=[ScenePain(title='感知数据分散',description='多类设备数据缺少统一汇聚与研判',sort_order=0),ScenePain(title='事件响应链路长',description='告警发现、确认和处置之间缺少闭环',sort_order=1)]
  if not item.goals:item.goals=[SceneGoal(title='形成统一态势',description='建立多源数据一体化展示与研判能力',sort_order=0),SceneGoal(title='建立处置闭环',description='贯通告警、分派、处置和复盘流程',sort_order=1)]
  if not item.process_steps:item.process_steps=[SceneProcessStep(node_title=title,node_description=desc,sort_order=i) for i,(title,desc) in enumerate([('数据采集','汇聚雷达、AIS、视频等数据'),('智能研判','算法与模型识别目标和风险'),('联动处置','生成告警并驱动业务处置'),('事件复盘','留存过程与结果形成闭环')])]

 for index,item in enumerate(solutions):
  item.code=f'HZ-SOL-{index+1:03d}';item.category=scenes[index%len(scenes)].category;item.status='ACTIVE';item.target_description='面向'+item.scene.name+'的标准化建设与交付';item.coverage_scope='覆盖感知、分析、告警、处置和复盘全流程';item.architecture_summary='前端感知层、边缘智能层、平台服务层和业务应用层';item.implementation_notes='按现场勘察、方案确认、部署联调和验收交付四阶段实施'
  if not item.architecture:item.architecture=[SolutionArchitectureNode(layer='感知层',name='多源感知设备',description='雷达、AIS和视频等现场感知设备',sort_order=0),SolutionArchitectureNode(layer='边缘智能层',name='智能分析终端',description='承载算法和模型能力',sort_order=1),SolutionArchitectureNode(layer='平台服务层',name='海智综合管控平台',description='提供态势、告警和处置闭环',sort_order=2)]
  if not item.capability_coverage:item.capability_coverage=[SolutionCapabilityCoverage(capability_name='多源态势融合',status='COVERED',implementation='由感知设备、边缘智能和平台协同实现',sort_order=0),SolutionCapabilityCoverage(capability_name='风险事件闭环',status='COVERED',implementation='由平台告警与处置流程实现',sort_order=1)]

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
 for product,software_item in zip([x for x in products if x.product_type=='SOFTWARE_PRODUCT'],software):
  relation_specs.append(('products',product.id,'software',software_item.id,'COMMERCIALIZATION',{'primary':True,'notes':'商业产品与软件技术实体的主映射'}))
 normalized=[(*spec[:4],'SUPPORT' if spec[2] in {'software','algorithms','model-capabilities'} else 'RECOMMENDATION',spec[4]) if len(spec)==5 else spec for spec in relation_specs]
 for source_type,source_id,target_type,target_id,relation_type,metadata in normalized:
  exists=db.scalar(select(KnowledgeRelation.id).where(KnowledgeRelation.source_type==source_type,KnowledgeRelation.source_id==source_id,KnowledgeRelation.target_type==target_type,KnowledgeRelation.target_id==target_id,KnowledgeRelation.relation_type==relation_type).limit(1))
  if not exists:db.add(KnowledgeRelation(source_type=source_type,source_id=source_id,target_type=target_type,target_id=target_id,relation_type=relation_type,metadata_json=json.dumps(metadata,ensure_ascii=False)))
 db.commit()
