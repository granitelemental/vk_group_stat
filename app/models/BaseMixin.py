from app.utils.db import upsert
from app.models.db import session

def map_instance_to_dict(row):
    return row._asdict()
    # d = getattr(i, "__dict__")
    # del d['_sa_instance_state']
    # return d

class BaseMixin:
    @classmethod 
    def get_all(cls, filter=None):
        query = session.query(cls)
        if filter is not None:
            query = query.filter(filter)
        items = list(map(map_instance_to_dict, query.all()))
        return items

    @classmethod
    def get(cls, clause):
        return session.query(cls).filter(clause).one_or_none()

    @classmethod
    def get_instance(cls, clause, except_fields=[], only_fields=None):
        columns = [c for c in cls.__table__.c if c not in except_fields and (True if only_fields is None else c in only_fields)]
        return session.query(*columns).filter(clause).one_or_none()

    @classmethod
    def get_by(cls, *args, **kwargs):
        instance = cls.get_instance(*args, **kwargs)
        if instance:
            r = map_instance_to_dict(instance)
            print('----', r)
            print(type(r))
            return r

    @classmethod
    def save(cls, data, keys):
        return upsert(data, cls, keys)
