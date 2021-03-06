from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint

from app.models.db import BaseModel
from app.models.BaseMixin import BaseMixin

class Like(BaseModel, BaseMixin):
    __tablename__ = 'likes'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    group_id = Column(Integer, ForeignKey('groups.vk_id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.vk_id'), nullable=False)
    date = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint('post_id', 'user_id', name='_post_user_uc'),
                     )

   




    
