from sqlalchemy import DateTime, Table, Column, Integer, String, MetaData, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app.models.db import BaseModel

class Post(BaseModel):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    vk_id = Column(Integer, nullable = False)
    group_id = Column(Integer, nullable = False)
    date = Column(DateTime)
    data = Column(JSON)
    
    # Relations
    likes = relationship('Like', backref='posts')
