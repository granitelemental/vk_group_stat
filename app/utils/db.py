from app.models.db import session

def upsert(model, clause, **kwargs):
    obj = session.query(model).filter(clause).one_or_none() # возвращает объект, если находит один айдишник в базе, 0 - если не находит ни одного
    if obj:
        session.query(model).filter(clause).update(kwargs)
    else:             
        session.add(model(**kwargs))
    session.commit()