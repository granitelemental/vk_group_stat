from sqlalchemy import cast, DATE
from sqlalchemy.dialects import postgresql
from datetime import datetime, timedelta, timezone

from app.models.db import session, engine


def bulk_upsert_or_insert(items, model, index_elements, update=False):
    if len(items) == 0:
        return None
    """items = list of dicts, model - db model, index_elements - list of fields to identify unique items in db, update - whether update is needed in case of item existance """
    keys = items[0].keys()
    insert_stmt = postgresql.insert(model.__table__).values(items)
    update_stmt = insert_stmt.on_conflict_do_update(
    index_elements = index_elements,
    set_={key: getattr(insert_stmt.excluded, key) for key in keys}
    )
    do_nothing_stmt = insert_stmt.on_conflict_do_nothing(
    index_elements = index_elements
    )
    stmt = update_stmt if update else do_nothing_stmt
    engine.execute(stmt)
    return None

def upsert(item, model, index_elements):
    bulk_upsert_or_insert(items = [item], model=model, index_elements=index_elements, update=True)


def filter_period(model, period):
    periods = {"1d": 1,
               "1w": 7,
               "1M": 30,
               "1y": 365}

    time_pass = datetime.now(tz=timezone.utc) - timedelta(days=int(periods[period]))     
    filter = cast(model.date, DATE) >= time_pass
    return filter


