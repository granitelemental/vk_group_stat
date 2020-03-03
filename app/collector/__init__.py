import vk
from datetime import datetime, timedelta

from sqlalchemy.ext.declarative import declarative_base

from app.models.db import session, engine
from app.models.User import User
from app.models.Post import Post
from app.models.Like import Like

from app.models.db import BaseModel

from app.utils import chunks
from app.utils.db import upsert

vk_session = vk.Session(access_token="4c6d8d6e4c6d8d6e4c6d8d6e054c02301244c6d4c6d8d6e1224aadc8ad37bd1098d8a3f")
vk_api = vk.API(vk_session, v = 5.8)

BaseModel.metadata.create_all(engine)


def collect_likes(post, step=200):
    offset = 0
    likes = vk_api.likes.getList(
        type="post",
        item_id=post["id"],
        owner_id=post["owner_id"],
        offset=offset,
        count=1
    )

    total = likes['count']
    users_list = []

    while offset < total:
        likes = vk_api.likes.getList(
            type="post",
            item_id=post["id"],
            owner_id=post["owner_id"],
            offset=offset,
            count=step
        )
        like_chunks = chunks(100, likes['items'])

        for chunk in like_chunks:
            users_list += vk_api.users.get(user_ids=chunk, fields=User.get_vk_fields())
        offset += len(likes['items'])

def start_collector():
    group_id = -1 * vk_api.utils.resolveScreenName(screen_name="ideal_gf").get('object_id')

    posts = vk_api.wall.get(owner_id=group_id, offset=1, count=1)

    p_count = posts['count']
    p_items = posts['items']

    for post in p_items:
        localdate = datetime.utcfromtimestamp(post['date']) + timedelta(hours=3)

        # Репосты можно получить только с сервисным ключем доступа группы
        # reposts = vk_api.wall.getReposts(owner_id=post['owner_id'], post_id = post['id'])

        upsert(Post,
            Post.id == post['id'],
            data=post,
            id=post['id'],
            date=localdate,
            likes_count=post['likes']['count'],
            comments_count=post['comments']['count'],
            reposts_count=post['reposts']['count'],
        )

        collect_likes(post)
