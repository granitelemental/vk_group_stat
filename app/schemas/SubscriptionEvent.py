from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field, fields

from app.models.SubscriptionEvent import SubscriptionEvent
from app.schemas.User import UserSchema

class SubscriptionEventSchema(SQLAlchemySchema):
    
    class Meta:
        model = SubscriptionEvent
        load_instance = True  # Optional: deserialize to model instances

    id = auto_field()
    user_id = auto_field()
    group_id = auto_field() 
    date = auto_field() 
    is_subscribed = auto_field()
    user = fields.Nested(UserSchema)