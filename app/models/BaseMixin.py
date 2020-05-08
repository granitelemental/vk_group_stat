from app.utils.db import upsert
from app.models.db import session

def map_instance_to_dict(i):
    d = getattr(i, "__dict__")
    del d['_sa_instance_state']
    return d

class BaseMixin:
    @classmethod 
    def get_all(cls, filter=None):
        query = session.query(cls)
        if filter is not None:
            query = query.filter(filter)
        items = list(map(map_instance_to_dict, query.all()))
        return items

    @classmethod
    def get_by(cls, clause):
        instance = session.query(cls).filter(clause).one_or_none()
        return instance and map_instance_to_dict(instance)

    @classmethod
    def save(cls, data, keys):
        return upsert(data, cls, keys)
