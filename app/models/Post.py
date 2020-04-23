from sqlalchemy import DateTime, Table, Column, Integer, String, MetaData, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.models.db import BaseModel
from app.models.Like import Like

class Post(BaseModel):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    vk_id = Column(Integer, nullable = False)
    group_id = Column(Integer, nullable = False)
    date = Column(DateTime)
    data = Column(JSON)
    comments_count = Column(Integer, nullable=False)
    reposts_count = Column(Integer, nullable=False)
    
    # Relations
    likes = relationship('Like', backref='posts')
