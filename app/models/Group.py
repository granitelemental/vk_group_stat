from sqlalchemy import Column, Integer
from app.models.db import BaseModel

class Group(BaseModel):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    vk_id = Column(Integer, nullable=False)
    


