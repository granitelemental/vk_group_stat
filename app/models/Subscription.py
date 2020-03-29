from sqlalchemy import Column, Integer, ForeignKey
from app.models.db import BaseModel

class Subscription(BaseModel):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable = False)


