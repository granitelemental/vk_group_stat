import vk
from datetime import datetime, timedelta

from sqlalchemy.ext.declarative import declarative_base

from app.models.db import session, engine
from app.models.User import User
from app.models.Post import Post
from app.models.Like import Like
import numpy as np

from app.models.db import BaseModel  # BaseModel запоминает, что от нее наследовалось в User, Post и Like, при create_all создает все эти таблицы

vk_session = vk.Session(access_token="4c6d8d6e4c6d8d6e4c6d8d6e054c02301244c6d4c6d8d6e1224aadc8ad37bd1098d8a3f")
vk_api = vk.API(vk_session, v = 5.8)

BaseModel.metadata.create_all(engine)

def upsert(model, clause, pass_if_exists=False, **kwargs):
    obj = session.query(model).filter(clause).one_or_none() # возвращает объект, если находит один айдишник в базе, 0 - если не находит ни одного
    
    if obj:
        if pass_if_exists:
            return
        session.query(model).filter(clause).update(kwargs)
    else:             
        session.add(model(**kwargs))
    session.commit()


def start_collector():
    group_id = vk_api.utils.resolveScreenName(screen_name="ewe.nemnogo").get('object_id')

    posts = vk_api.wall.get(owner_id=-group_id, offset=1, count=100)

    p_items = posts['items']

    user_fields = ["sex","bdate", "city","country","home_town","schools","relation"]

    for post in p_items:
        localdate = datetime.utcfromtimestamp(post['date']) + timedelta(hours=3)
        
        like_list = []
        max_count = 1000
        offset = 0
        likes = vk_api.likes.getList(type="post", 
                                    item_id=post["id"], 
                                    owner_id=post["owner_id"], 
                                    offset=offset, 
                                    count=max_count)
                                    
        while offset < likes["count"]:
            likes = vk_api.likes.getList(type = "post", 
                                        item_id = post["id"], 
                                        owner_id = post["owner_id"], 
                                        offset = offset, 
                                        count = max_count)
            like_list.extend(likes["items"])
            offset += max_count


        upsert(Post, Post.id == post['id'], 
            data = post, 
            id = post["id"],
            date = localdate,
            )
            
        for user_id in like_list:

            user = vk_api.users.get(user_ids=user_id, fields=user_fields)[0]

            kwargs = {key: user[key] if key in user.keys() else None for key in user_fields}
            print("---------->")
            print(kwargs)

            upsert(User, (User.id == user_id), pass_if_exists=True,
                                            id = user_id,
                                            **kwargs)

            upsert(Like, (Like.user_id == user_id) and (Like.post_id == post['id']), pass_if_exists=True,
                                                                                user_id = user_id,
                                                                                post_id = post['id'],)





        