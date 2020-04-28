from sqlalchemy import DateTime, Table, Column, Integer, String, MetaData, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.db import BaseModel, session
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

    __table_args__ = (UniqueConstraint('vk_id', 'group_id', name='postvk_group_uc'),
                     )
    
    # Relations
    likes = relationship('Like', backref='posts')

    # TODO вместо session.query и так далее
    @classmethod 
    def get_all(entities = None, filter = None):
        query = session.query(Post)
        if entities
            query = query.with_entities(*entities)
        
        if filter:
            query = query.filter(filter)
        
        return query.all()