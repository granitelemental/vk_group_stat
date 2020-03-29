from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from app.models.User import User

class UserSchema(SQLAlchemySchema):
    
    class Meta:
        model = User
        load_instance = True  # Optional: deserialize to model instances

    id = auto_field()
    vk_id = auto_field()
    sex = auto_field() 
    bdate = auto_field() 
    city = auto_field()
    country = auto_field() 
    home_town = auto_field() 
    schools = auto_field()
    relation = auto_field()