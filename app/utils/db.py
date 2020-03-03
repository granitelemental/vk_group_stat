from app.models.db import session

def upsert(instance, clause, **kwargs):
    entry = session.query(instance).filter(clause).one_or_none()

    if entry:
        session.query(instance).filter(clause).update(kwargs)
    else:
        session.add(instance(**kwargs))

    session.commit()
