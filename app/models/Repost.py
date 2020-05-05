from sqlalchemy import DateTime, Table, Column, Integer, String, MetaData, ForeignKey, JSON, UniqueConstraint

from app.models.Group import Group
from app.models.User import User
from app.models.Post import Post

from app.models.db import BaseModel

class Repost(BaseModel):
    __tablename__ = 'reposts'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    group_id = Column(Integer, ForeignKey("groups.vk_id"), nullable = False) 
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False) 
    user_id = Column(Integer, ForeignKey("users.vk_id"), nullable=False)   
    date = Column(DateTime, nullable = False)
    event_vk_id = Column(String, nullable = False)

    __table_args__ = (UniqueConstraint("event_vk_id", name='rep_event_vk_id_uc'),
                )
    

