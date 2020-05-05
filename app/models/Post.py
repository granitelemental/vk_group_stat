from sqlalchemy import DateTime, Table, Column, Integer, String, MetaData, ForeignKey, JSON, UniqueConstraint, and_
from sqlalchemy.orm import relationship

from app.models.db import BaseModel, session, BaseMixin
from app.models.Like import Like

class Post(BaseModel, BaseMixin):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    vk_id = Column(Integer, nullable = False)
    group_id = Column(Integer, nullable = False) # TODO Add relation
    date = Column(DateTime)
    data = Column(JSON)
    comments_count = Column(Integer, nullable=False)
    reposts_count = Column(Integer, nullable=False)
    likes_count = Column(Integer, nullable=False)
    views_count = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint('vk_id', 'group_id', name='postvk_group_uc'),
                     )

    @classmethod
    def post_vk_to_db_id(cls, vk_id, group_id):
        res = session.query(cls.id).filter(and_(cls.vk_id==vk_id, cls.group_id==group_id)).scalar()
        print("--->",res,"vk_id:", vk_id, "group_id:", group_id)
        return res
    
    # Relations
    likes = relationship('Like', backref='posts')

    