import vk
import json
from datetime import datetime, timedelta
import time

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import and_

from app.models.db import session, engine
from app.models.User import User
from app.models.Post import Post
from app.models.Like import Like
import numpy as np

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

    start_time = time.time()
    print("1-------------->")
    #print(start_time)

    group_id = vk_api.utils.resolveScreenName(screen_name="ewe.nemnogo").get('object_id')
    posts = vk_api.wall.get(owner_id=-group_id, offset=0, count=3)
    p_items = posts['items']

    post_like_usr_ids = {post["id"]: [] for post in p_items}
    post_like_usr_ids["all_usr_ids"] = []

    for post in p_items:
        max_count = 1000
        offset = 0
        likes = vk_api.likes.getList(type="post", item_id=post["id"], owner_id=post["owner_id"], offset=offset, count=max_count)
        while offset < likes["count"]:
            likes = vk_api.likes.getList(type = "post", item_id = post["id"], owner_id = post["owner_id"], offset = offset, count = max_count)

            post_like_usr_ids[post["id"]].extend(likes["items"])
            post_like_usr_ids["all_usr_ids"] = list(set(likes["items"] + post_like_usr_ids["all_usr_ids"]))
            offset += max_count
        
        localdate = datetime.utcfromtimestamp(post['date']) + timedelta(hours=3)
        upsert(Post, Post.id == post['id'], data = post, id = post["id"], date = localdate)

    elapsed_time = time.time() - start_time
    print("1 elapsed-------------->")
    print(elapsed_time)
    print("\n")

    user_fields = ["sex","bdate", "city","country","home_town","schools","relation"]
    
    print("2 start-------------->")
    start_time = time.time()
    #print(start_time)

    print(len(post_like_usr_ids["all_usr_ids"]))

    for i, user_id in enumerate(post_like_usr_ids["all_usr_ids"]):
        if session.query(User).filter(User.id == user_id).one_or_none():
            post_like_usr_ids["all_usr_ids"].pop(i)

    print(len(post_like_usr_ids["all_usr_ids"]))
           
    users = vk_api.users.get(user_ids=post_like_usr_ids["all_usr_ids"], fields=user_fields)

    for user in users:
        print(user)
        kwargs = {key: user[key] if key in user.keys() else None for key in user_fields}
        kwargs["id"] = user_id

        if kwargs["bdate"] != None:
            if len(kwargs["bdate"].split(".")) == 3:
                kwargs["bdate"] = datetime.strptime(kwargs["bdate"], "%d.%m.%Y")
            else:
                kwargs["bdate"] = None
        else:
            kwargs["bdate"] = None

        kwargs["city"] = [kwargs["city"]["title"] if kwargs["city"] else None][0]
        kwargs["country"] = [kwargs["country"]["title"] if kwargs["country"] else None][0]
        if kwargs["schools"]:
            kwargs["schools"] = [school["name"] for school in kwargs["schools"]]

        session.add(User(**kwargs))
        session.commit()


    elapsed_time = time.time() - start_time
    print("2 elapsed-------------->")
    print(elapsed_time)
    print("\n")


    print("3 start-------------->")
    start_time = time.time()
    #print(start_time)

    for post in p_items:
        for user_id in post_like_usr_ids[post["id"]]:
            upsert(Like, and_(Like.user_id == user_id, Like.post_id == post['id']), user_id = user_id, post_id = post['id'])

    elapsed_time = time.time() - start_time
    print("3 elapsed-------------->")
    print(elapsed_time)



