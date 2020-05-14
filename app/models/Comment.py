from sqlalchemy import DateTime, Table, Column, Integer, String, MetaData, ForeignKey, JSON, UniqueConstraint

from app.models.db import BaseModel
from app.models.BaseMixin import BaseMixin

class Comment(BaseModel, BaseMixin):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    group_id = Column(Integer, ForeignKey("groups.vk_id"), nullable = False) 
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False) 
    user_id = Column(Integer, ForeignKey("users.vk_id"), nullable=False)   
    data = Column(JSON, nullable=False)
    date = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint('group_id', "post_id", 'user_id', "date", name='_post_user_group_date_uc'),
                    )

