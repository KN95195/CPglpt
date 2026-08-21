from sqlalchemy import select,func
from app.database import SessionLocal
from app.models import Product,Software,Algorithm,Capability,Scene,Solution,SolutionBomItem,KnowledgeRelation

minimums={Product:15,Software:3,Algorithm:10,Capability:15,Scene:5,Solution:6}
dirty=['测试','嗯嗯嗯','product a','demo']
with SessionLocal() as db:
    counts={model.__tablename__:db.scalar(select(func.count(model.id))) for model in minimums}
    for model,minimum in minimums.items():
        assert counts[model.__tablename__]>=minimum,(model.__tablename__,counts[model.__tablename__],minimum)
        names=[name for name in db.scalars(select(model.name))]
        assert not any(token in name.lower() for token in dirty for name in names),(model.__tablename__,names)
    solution_ids=list(db.scalars(select(Solution.id)))
    missing=[sid for sid in solution_ids if not db.scalar(select(SolutionBomItem.id).where(SolutionBomItem.solution_id==sid).limit(1))]
    assert not missing,missing
    relation_count=db.scalar(select(func.count(KnowledgeRelation.id)))
    assert relation_count>=60,relation_count
    print({'counts':counts,'solutionsWithBom':len(solution_ids),'relations':relation_count,'dirtyRecords':0})
