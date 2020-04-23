from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, DateTime

from app.models.db import BaseModel

class Like(BaseModel):
    __tablename__ = 'likes'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    group_id = Column(Integer, ForeignKey('groups.vk_id'))
    post_id = Column(Integer, ForeignKey('posts.id'))
    user_id = Column(Integer, ForeignKey('users.vk_id'))
    date = Column(DateTime, nullable=False)

    __table_args__ = (UniqueConstraint('post_id', 'user_id', name='_post_user_uc'),
                     )
    
