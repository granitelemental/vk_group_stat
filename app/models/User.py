from sqlalchemy import DateTime, Table, Column, Integer, String, MetaData, JSON, ARRAY, Boolean

from app.models.db import BaseModel, BaseMixin

class User(BaseModel, BaseMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    first_name = Column(String)
    last_name = Column(String)
    vk_id = Column(Integer, unique=True, nullable = False)
    sex = Column(Integer)
    bdate = Column(DateTime)
    city = Column(String)
    country = Column(String)
    home_town = Column(String)
    schools = Column(ARRAY(String))
    relation = Column(Integer)
    is_subscribed = Column(Boolean, nullable = False)

    vk_fields = ["first_name", "last_name","sex","bdate", "city","country","home_town","schools","relation"]