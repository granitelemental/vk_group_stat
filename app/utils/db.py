from app.models.db import session
from sqlalchemy import cast, DATE
from datetime import datetime, timedelta

def upsert(model, clause, **kwargs):
    obj = session.query(model).filter(clause).one_or_none() # возвращает объект, если находит один айдишник в базе, 0 - если не находит ни одного
    if obj:
        session.query(model).filter(clause).update(kwargs)
    else:             
        session.add(model(**kwargs))
    session.commit()

def filter_period(model, period):
    periods = {"1d": 1,
               "1w": 7,
               "1M": 30,
               "1y": 365}
    time_pass = datetime.now() - timedelta(days=int(periods[period]))     # TODO перевести все время вообще в UTC
    filter = cast(model.date, DATE) >= time_pass
    return filter


