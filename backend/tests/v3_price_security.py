from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Role,Permission,RolePermission,User,ProductCategory,Product,ProductPrice,Scene,Solution,SolutionBomItem
from app.main import product,solution_bom_payload

engine=create_engine('sqlite+pysqlite:///:memory:')
Base.metadata.create_all(engine)
Session=sessionmaker(bind=engine,expire_on_commit=False)
with Session() as db:
    view=Permission(code='KNOWLEDGE_VIEW',name='知识查看');price_view=Permission(code='PRICE_VIEW',name='价格查看')
    reader_role=Role(code='reader',name='普通用户',permissions='KNOWLEDGE_VIEW');price_role=Role(code='price_reader',name='价格用户',permissions='KNOWLEDGE_VIEW,PRICE_VIEW')
    db.add_all([view,price_view,reader_role,price_role]);db.flush();db.add_all([RolePermission(role_id=reader_role.id,permission_id=view.id),RolePermission(role_id=price_role.id,permission_id=view.id),RolePermission(role_id=price_role.id,permission_id=price_view.id)])
    reader=User(username='reader',display_name='普通用户',password_hash='-',role_id=reader_role.id);price_user=User(username='price',display_name='价格用户',password_hash='-',role_id=price_role.id)
    category=ProductCategory(name='智能终端');db.add_all([reader,price_user,category]);db.flush();item=Product(name='海智感知终端',model_code='HZ-SEC-01',category_id=category.id,summary='安全测试产品');scene=Scene(name='安全测试场景',summary='验证价格权限');db.add_all([item,scene]);db.flush();solution=Solution(name='安全测试方案',scene_id=scene.id,tier='标准型',summary='验证BOM价格权限');db.add(solution);db.flush();db.add_all([ProductPrice(product_id=item.id,reference_price=120000,cost_price=80000),SolutionBomItem(solution_id=solution.id,product_id=item.id,quantity=2)]);db.commit()
    reader=db.get(User,reader.id);price_user=db.get(User,price_user.id)
    reader_product=product(item.id,db,reader);priced_product=product(item.id,db,price_user)
    reader_bom=solution_bom_payload(solution.id,db,reader);priced_bom=solution_bom_payload(solution.id,db,price_user)
    assert 'price' not in reader_product
    assert priced_product['price']['referencePrice']==120000
    assert 'total' not in reader_bom and all('unitPrice' not in row and 'subtotal' not in row for row in reader_bom['items'])
    assert priced_bom['total']==240000 and priced_bom['items'][0]['subtotal']==240000
    print({'readerProductPriceOmitted':True,'readerBomPriceKeysOmitted':True,'priceReaderTotal':priced_bom['total']})
