import vk
from datetime import datetime, timedelta

from sqlalchemy.ext.declarative import declarative_base

from app.models.db import session, engine
from app.models.User import User
from app.models.Post import Post
from app.models.Like import Like

from app.models.db import BaseModel  # BaseModel запоминает, что от нее наследовалось в User, Post и Like, при create_all создает все эти таблицы

vk_session = vk.Session(access_token="4c6d8d6e4c6d8d6e4c6d8d6e054c02301244c6d4c6d8d6e1224aadc8ad37bd1098d8a3f")
vk_api = vk.API(vk_session, v = 5.8)

BaseModel.metadata.create_all(engine)

def upsert(model, clause, **kwargs):
    obj = session.query(model).filter(clause).one_or_none() # возвращает объект, если находит один айдишник в базе, 0 - если не находит ни одного

    if obj:
        session.query(model).filter(clause).update(kwargs)
    else:
        session.add(model(**kwargs))
    session.commit()

def start_collector():
    group_id = vk_api.utils.resolveScreenName(screen_name="ewe.nemnogo").get('object_id')

    posts = vk_api.wall.get(owner_id=-group_id, offset=0, count=1)


    # p_count = posts['count']
    p_items = posts['items']

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
            likes = likes = vk_api.likes.getList(type = "post", 
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
            likes_count = post['likes']['count'],
            likes = {"user_ids": like_list}
            )
            
        for user_id in like_list:

            upsert(User, (User.id == user_id), 
            id = user_id,
            )

            upsert(Like, (Like.user_id == user_id) and (Like.post_id == post['id']), 
            user_id = user_id,
            post_id = post['id'],)





        