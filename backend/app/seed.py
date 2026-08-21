import json, hashlib, hmac, os, base64
from sqlalchemy import select
from .models import Role,Permission,RolePermission,User,ProductCategory,Product,ProductCapability,Capability,Algorithm,Software,Scene,Solution,BomRule,ProductPrice
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
