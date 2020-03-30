from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.models.db import BaseModel

class Subscription(BaseModel):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)

    group_id = Column(Integer, ForeignKey('groups.vk_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.vk_id'), nullable = False)

    __table_args__ = (UniqueConstraint('group_id', 'user_id', name='_group_user_uc'),
                     )


