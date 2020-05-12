from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, Boolean, DateTime, String
from datetime import datetime, timezone

from app.models.db import BaseModel
from app.models.BaseMixin import BaseMixin
from sqlalchemy.orm import relationship, backref

from app.models.Group import Group
from app.models.User import User


class SubscriptionEvent(BaseModel, BaseMixin):
    __tablename__ = 'subscription_events'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    group_id = Column(Integer, ForeignKey('groups.vk_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.vk_id'), nullable = False)
    date = Column(DateTime, default = datetime.now(tz=timezone.utc))
    is_subscribed = Column(Boolean, nullable = False)
    event_vk_id = Column(String, nullable = False)

    __table_args__ = (UniqueConstraint('event_vk_id', name='sub_event_vk_id_uc'),
                    )

    # Relations
    user = relationship('User', backref=backref('subscription_events', uselist=False))


