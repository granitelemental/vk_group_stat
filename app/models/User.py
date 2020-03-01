from sqlalchemy import DateTime, Table, Column, Integer, String, MetaData
from app.models.db import BaseModel

class User(BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    # ["sex","bdate", "city","country","home_town","schools","relation"]