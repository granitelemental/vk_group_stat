from datetime import datetime, timedelta

import vk
import json
import tqdm
import requests
import numpy as np

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import and_

from app.models.db import session, engine
from app.models.User import User
from app.models.Post import Post
from app.models.Like import Like
from app.models.Group import Group
from app.models.Subscription import Subscription


from app.models.db import BaseModel  # BaseModel запоминает, что от нее наследовалось в User, Post и Like, при create_all создает все эти таблицы

app_token = "4c6d8d6e4c6d8d6e4c6d8d6e054c02301244c6d4c6d8d6e1224aadc8ad37bd1098d8a3f"
comunity_token = "1d05d5656b70b874e93a44b5821a378e12c48f7f249d5cdf10f81e0ca970394f144209f39480ccb02cc09"

vk_session = vk.Session(access_token=app_token)
vk_api = vk.API(vk_session, v = 5.8)

BaseModel.metadata.create_all(engine)

def upsert(model, clause, **kwargs):
    obj = session.query(model).filter(clause).one_or_none() # возвращает объект, если находит один айдишник в базе, 0 - если не находит ни одного
    if obj:
        session.query(model).filter(clause).update(kwargs)
    else:             
        session.add(model(**kwargs))
    session.commit()


def get_all(get_function, max_count, items_to_get, **qwargs):
    """get_function - something like vk_api.groups.getMembers;
    max_count - max count of items;
    items_to_get - 'users' or something else;
    **qwargs - e.g. user fields"""
    max_count = max_count
    offset = 0
    all_items = []
    result = get_function(**qwargs, offset=offset, count=max_count)

    while offset < result["count"]:
        result = get_function(**qwargs, offset=offset, count=max_count)
        all_items.extend(result[items_to_get])
        offset += max_count
    return all_items

def collect_subcriptions(group_id, comunity_token):
    vk_session = vk.Session(access_token=comunity_token)
    vk_api = vk.API(vk_session, v = 5.8)
    subscribers = get_all(get_function=vk_api.groups.getMembers,
                        max_count=200,
                        items_to_get = "users",
                        group_id=group_id,
                        fields=User.vk_fields)
    return subscribers

def create_user_objects(users):
    """users - user items obtained from vk_api; 
    user_objects - objects of class User"""
    user_objects = []
    for user in tqdm.tqdm(users):
        kwargs = {key: user[key] if key in user.keys() else None for key in User.vk_fields}
        kwargs["vk_id"] = user["id"]
        if (kwargs["bdate"] != None) and (len(kwargs["bdate"].split(".")) == 3):
            kwargs["bdate"] = datetime.strptime(kwargs["bdate"], "%d.%m.%Y")
        else:
            kwargs["bdate"] = None
        kwargs["city"] = [kwargs["city"]["title"] if kwargs["city"] else None][0]
        kwargs["country"] = [kwargs["country"]["title"] if kwargs["country"] else None][0]
        if kwargs["schools"]:
            kwargs["schools"] = [school["name"] for school in kwargs["schools"]]
        user_objects.append(User(**kwargs))
    return user_objects

def start_collector():

    group_id = vk_api.utils.resolveScreenName(screen_name="public193519310").get('object_id')
    print("Updating groups")
    upsert(Group, Group.vk_id==group_id, vk_id=group_id)

    print("Getting posts info and upserting posts:")
    posts = vk_api.wall.get(owner_id=-group_id, offset=0, count=100)
    post_items = posts['items']
    post_like_usr_ids = {post["id"]: [] for post in post_items}
    post_like_usr_ids["all_usr_ids"] = []

    for post in tqdm.tqdm(post_items):
        post_like_usr_ids[post["id"]] = get_all(get_function=vk_api.likes.getList,
                                                max_count=200,
                                                type="post", 
                                                items_to_get = "items",
                                                item_id=post["id"], 
                                                owner_id=post["owner_id"])

        post_like_usr_ids["all_usr_ids"] = list(set(post_like_usr_ids[post["id"]] + post_like_usr_ids["all_usr_ids"]))
        localdate = datetime.utcfromtimestamp(post['date']) + timedelta(hours=3)
        upsert(Post, Post.vk_id == post['id'], group_id = group_id, data = post, vk_id = post["id"], date = localdate)

    query = session.query(User)
    existing_user_ids = query.filter(User.vk_id.in_(post_like_usr_ids["all_usr_ids"])).all()
    existing_user_ids = [user.vk_id for user in existing_user_ids]
    post_like_usr_ids["all_usr_ids"] = [id for id in  post_like_usr_ids["all_usr_ids"] if id not in existing_user_ids ]

    print("Getting users info:")
    users = []
    for start in tqdm.tqdm(range(0,len(post_like_usr_ids["all_usr_ids"]),1000)):
        user_ids = post_like_usr_ids["all_usr_ids"][start:start+1000]
        open_users = vk_api.users.get(user_ids = user_ids, fields = User.vk_fields)
        open_user_ids = [user["id"] for user in open_users]
        closed_user_ids = [user_id for user_id in user_ids if user_id not in open_user_ids]
        closed_users = [{"id": user_id} for user_id in closed_user_ids]
        users.extend(open_users + closed_users)

    print("Adding users:") 
    user_objects = create_user_objects(users)
    session.bulk_save_objects(user_objects)
    session.commit()

    print("Collecting subscriptions")
    subscribers = collect_subcriptions(group_id, comunity_token)

    print("Adding users with subscribers")
    query = session.query(User)
    existing_user_ids = [item.vk_id for item in query.filter(User.vk_id.in_([sub["id"] for sub in subscribers])).all()]
    user_objects = create_user_objects([sub for sub in subscribers if sub["id"] not in existing_user_ids])
    session.bulk_save_objects(user_objects)
    session.commit()


    print("Adding subscriptions")
    subscriber_objects = []

    existing_subscriptions = [(sub["user_id"], sub["group_id"]) for sub in subscribers]

    existing_subscriptions = session.query(Subscription).filter((Subscription.user_id, Subscription.group_id).in_(existing_subscriptions))
    print(existing_subscriptions)
    # for sub in subscribers:
    #     if not session.query(Subscription).filter(Subscription.user_id==sub["id"], Subscription.group_id==group_id).one_or_none():
    #         subscriber_objects.append(Subscription(user_id=sub["id"], group_id=group_id)) 
    # session.bulk_save_objects(subscriber_objects)
    # session.commit()

    print("Collecting likes:")
    likes = []
    for post in tqdm.tqdm(post_items):
        post_id = session.query(Post).filter(Post.vk_id==post["id"]).one_or_none().id
        for user_vk_id in post_like_usr_ids[post["id"]]:
            user_id = session.query(User).filter(User.vk_id==user_vk_id).one_or_none().id
            if not session.query(Like).filter(Like.user_id==user_id, Like.post_id==post_id).one_or_none():
                likes.append(Like(post_id=post_id, user_id=user_id))

    print("Inserting likes:")
    session.bulk_save_objects(likes)
    session.commit()





