from sqlalchemy import DateTime, Table, Column, Integer, String, MetaData, ForeignKey, JSON



from app.models.db import BaseModel

class Repost(BaseModel):
    __tablename__ = 'reposts'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    group_id = Column(Integer, ForeignKey("groups.vk_id"), nullable = False) 
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False) 
    user_id = Column(Integer, ForeignKey("users.vk_id"), nullable=False)   
    

