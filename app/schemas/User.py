from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from app.models.User import User

class UserSchema(SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True  # Optional: deserialize to model instances

    id = auto_field()