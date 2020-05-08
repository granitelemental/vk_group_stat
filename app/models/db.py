import os

from sqlalchemy import create_engine, DateTime, Table, Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

BaseModel = declarative_base()

POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'test')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'test')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'test')

engine = create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}", echo = False)

Session = sessionmaker(bind=engine)
session = Session()

engine.connect()

from app.models import *

BaseModel.metadata.create_all(engine)