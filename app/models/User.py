from sqlalchemy import DateTime, Table, Column, Integer, String, MetaData, JSON
from app.models.db import BaseModel

class User(BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    sex = Column(Integer)
    bdate = Column(String)
    city = Column(JSON)
    country = Column(JSON)
    home_town = Column(String)
    schools = Column(JSON)
    relation = Column(Integer)