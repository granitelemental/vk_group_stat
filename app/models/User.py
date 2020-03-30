from sqlalchemy import DateTime, Table, Column, Integer, String, MetaData, JSON, ARRAY
from app.models.db import BaseModel



class User(BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    vk_id = Column(Integer, unique=True, nullable = False)
    sex = Column(Integer)
    bdate = Column(DateTime)
    city = Column(String)
    country = Column(String)
    home_town = Column(String)
    schools = Column(ARRAY(String))
    relation = Column(Integer)

    vk_fields = ["sex","bdate", "city","country","home_town","schools","relation"]