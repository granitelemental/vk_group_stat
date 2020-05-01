from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, Boolean, DateTime
from app.models.db import BaseModel, BaseMixin
from sqlalchemy.orm import relationship, backref

class SubscriptionEvent(BaseModel, BaseMixin):
    __tablename__ = 'subscription_events'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    group_id = Column(Integer, ForeignKey('groups.vk_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.vk_id'), nullable = False)
    date = Column(DateTime, nullable=False)
    is_subscribed = Column(Boolean, nullable = False)

    # Relations
    user = relationship('User', backref=backref('subscription_events', uselist=False))


