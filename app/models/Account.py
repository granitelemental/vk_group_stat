from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import DateTime, Table, Column, Integer, String, MetaData, ForeignKey, JSON, UniqueConstraint
from app.models.db import BaseModel
from app.models.BaseMixin import BaseMixin
from app.models.User import User

class Account(BaseModel, BaseMixin):
    __tablename__ = 'accounts'

    # Self main keys
    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    phone = Column(String(32), index=True)
    password_hash = Column(String(128))
    email = Column(String(256))

    # Social Ids
    vk_id = Column(Integer, ForeignKey("users.vk_id"), nullable = False)
    vk_access_token = Column(String(256))
    # twitter_id
    # facebook_id
    # google_id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    __table_args__ = (UniqueConstraint("vk_id", name='_account_user_id_uc'),
                    )

