from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field, fields

from app.models.Like import Like

class LikeSchema(SQLAlchemySchema):
    class Meta:
        model = Like
        load_instance = True  # Optional: deserialize to model instances

    id = auto_field() 
    post_id = auto_field()
    user_id = auto_field()

