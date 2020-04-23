from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field, fields

from app.models.Post import Post

from app.schemas.Like import LikeSchema

class PostSchema(SQLAlchemySchema):
    class Meta:
        model = Post
        load_instance = True  # Optional: deserialize to model instances
        include_relationships = True

    id = auto_field()
    vk_id = auto_field()
    likes = fields.Nested(LikeSchema, many=True)