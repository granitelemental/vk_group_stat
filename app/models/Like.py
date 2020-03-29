from sqlalchemy import Column, Integer, ForeignKey

from app.models.db import BaseModel


class Like(BaseModel):
    __tablename__ = 'likes'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)

    post_id = Column(Integer, ForeignKey('posts.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    
