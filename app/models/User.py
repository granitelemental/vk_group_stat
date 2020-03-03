from sqlalchemy import DateTime, Table, Column, Integer, String, MetaData, JSON
from app.models.db import BaseModel

class User(BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    first_name = Column(String)
    last_name = Column(String)
    bdate = Column(DateTime)
    sex = Column(String)
    city = Column(String)
    Country = Column(String)
    home_town = Column(String)
    schools = Column(JSON)
    followers_count = Column(Integer, active_history = True)
    last_seen = Column(DateTime)
    education = Column(String)

    @classmethod
    def get_vk_fields(cls):
        return [
            'id',
            'sex',
            'bdate',
            'city',
            'country',
            'home_town',
            'first_name',
            'last_name',
            'education',
            'universities',
            'schools',
            'status',
            'last_seen',
            'followers_count'
        ]