import os

from sqlalchemy import create_engine, DateTime, Table, Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

BaseModel = declarative_base()

class BaseMixin:
    @classmethod 
    def get_all(cls, filter=None):
        query = session.query(cls)
        if filter is not None:
            query = query.filter(filter)
        items = list(map(lambda x: getattr(x, "__dict__"), query.all()))
        items = [{key: item[key] for key in item.keys() if key!="_sa_instance_state"}
                for item in items]
        return items

POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'test')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'test')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'test')

engine = create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}", echo = False)

Session = sessionmaker(bind=engine)
session = Session()

engine.connect()