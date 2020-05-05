from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, Boolean
from app.models.db import BaseModel

from app.models.Group import Group
from app.models.User import User


class Subscription(BaseModel):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    group_id = Column(Integer, ForeignKey('groups.vk_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.vk_id'), nullable = False)
    is_subscribed = Column(Boolean, nullable = False)

    __table_args__ = (UniqueConstraint('group_id', 'user_id', name='_group_user_uc'),)


