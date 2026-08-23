import json
from pathlib import Path
from sqlalchemy import select
from .database import SessionLocal
from .models import Algorithm,Capability,KnowledgeCommercialProfile,ModelMetric,Product,ProductCategory,ProductVariant,Scene,Software

SOURCE_PATH=Path(__file__).with_name('data')/'official_material_2026.json'

def load_source():return json.loads(SOURCE_PATH.read_text(encoding='utf-8'))
def profile(db,kind,record_id,data):
    item=db.scalar(select(KnowledgeCommercialProfile).where(KnowledgeCommercialProfile.center_type==kind,KnowledgeCommercialProfile.center_id==record_id))
    if not item:item=KnowledgeCommercialProfile(center_type=kind,center_id=record_id);db.add(item)
    item.material_code=data.get('code','');item.unit=data.get('unit','套');item.is_agent_product=True;item.agent_price=data.get('agent');item.sale_price=data.get('sale');item.warranty_months=12;item.extended_warranty_rule='延保价格及年限按项目商务政策执行';item.applicable_scenes_json=json.dumps(data.get('scenes',[]),ensure_ascii=False);item.sales_notes=data.get('delivery','以正式报价单和合同为准');item.commercial_status='FEATURED';item.license_unit=data.get('unit','');item.included_quantity=data.get('included');item.overage_unit_price=data.get('overage');item.delivery_method=data.get('delivery','软件授权许可')
def run():
    source=load_source();counts={'products':0,'variants':0,'software':0,'algorithms':0,'scenes':0,'capabilities':0}
    with SessionLocal() as db:
        for data in source['scenes']:
            item=db.scalar(select(Scene).where(Scene.name==data['name']))
            if not item:item=Scene(name=data['name'],category='水域安全',summary=data['summary'],status='PUBLISHED');db.add(item)
            item.summary=data['summary'];counts['scenes']+=1
        db.flush()
        for data in source['products']:
            category=db.scalar(select(ProductCategory).where(ProductCategory.name==data['category']))
            if not category:category=ProductCategory(name=data['category'],description='正式配单材料分类');db.add(category);db.flush()
            item=db.scalar(select(Product).where(Product.name==data['name']))
            primary=data['variants'][0]['model']
            if not item:item=Product(name=data['name'],product_code=primary,product_series=data['series'],model_code=primary,current_version='2026',product_type='HARDWARE',category_id=category.id,summary=data['summary'],description=data['summary'],status='ON_SALE',source=source['source'],owner='产品中心');db.add(item);db.flush()
            item.product_series=data['series'];item.summary=data['summary'];item.description=data['summary'];item.source=source['source']
            variants={variant.model_code:variant for variant in item.variants}
            for index,row in enumerate(data['variants']):
                variant=variants.get(row['model'])
                if not variant:
                    variant=ProductVariant(product_id=item.id,model_code=row['model'])
                    db.add(variant)
                variant.material_code=row['material'];variant.unit=row['unit'];variant.is_primary=index==0;variant.is_agent_product=True;variant.agent_price=row['agent'];variant.sale_price=row['sale'];variant.warranty_months=12;variant.extended_warranty_rule='默认质保12个月，延保按项目商务政策执行';variant.applicable_scenes_json=json.dumps(data['scenes'],ensure_ascii=False);variant.sales_notes='价格以正式报价单为准';variant.commercial_status=row['status'];variant.specifications_json=json.dumps(row['spec'],ensure_ascii=False);variant.sort_order=index
                counts['variants']+=1
            counts['products']+=1
        for data in source['software']:
            item=db.scalar(select(Software).where(Software.name==data['name']))
            if not item:item=Software(name=data['name'],code=data['code'],version='2026',description=data['summary'],detail_description=data['summary'],status='SUPPORTED');db.add(item);db.flush()
            item.code=data['code'] or item.code;item.description=data['summary'];item.detail_description=data['summary'];profile(db,'software',item.id,data);counts['software']+=1
        for data in source['algorithms']:
            item=db.scalar(select(Algorithm).where((Algorithm.code==data['code'])|(Algorithm.name==data['name'])))
            if not item:item=Algorithm(name=data['name'],code=data['code'],version='V2',category='视觉智能',description=data['name'],status='SUPPORTED');db.add(item);db.flush()
            item.name=data['name'];item.code=data['code'];profile(db,'algorithms',item.id,data);counts['algorithms']+=1
        for data in source['capability_metrics']:
            item=db.scalar(select(Capability).where(Capability.name==data['name']))
            if not item:item=Capability(name=data['name'],code='',version='2026',category='海洋智能',description=data['name'],status='SUPPORTED');db.add(item);db.flush()
            known={metric.name:metric for metric in item.metrics}
            for index,(name,(value,unit)) in enumerate(data['metrics'].items()):
                metric=known.get(name)
                if not metric:item.metrics.append(ModelMetric(name=name,value=value,unit=unit,group_name='正式材料指标',condition='以正式材料口径为准',source='海莱云智2026产品介绍（对外）',highlight=index<4,sort_order=index))
                else:metric.value=value;metric.unit=unit;metric.source='海莱云智2026产品介绍（对外）'
            counts['capabilities']+=1
        db.commit()
    return counts

if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False))
