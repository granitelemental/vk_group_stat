import json
from datetime import datetime, timedelta

import numpy as np
import requests
import tqdm
import vk
from sqlalchemy import and_, func, tuple_, cast, DATE
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base

from app.models.Comment import Comment
from app.models.db import \
    BaseModel  # BaseModel запоминает, что от нее наследовалось в User, Post и Like, при create_all создает все эти таблицы
from app.models.db import engine, session
from app.models.Group import Group
from app.models.Like import Like
from app.models.Post import Post
from app.models.Subscription import Subscription
from app.models.SubscriptionEvent import SubscriptionEvent
from app.models.User import User
from app.utils.collector import get_all
from app.utils.db import upsert
from app.utils.log import init_logger

app_token = "4c6d8d6e4c6d8d6e4c6d8d6e054c02301244c6d4c6d8d6e1224aadc8ad37bd1098d8a3f" # TODO в конфиг
comunity_token = "1d05d5656b70b874e93a44b5821a378e12c48f7f249d5cdf10f81e0ca970394f144209f39480ccb02cc09" # TODO в кофиг

vk_session = vk.Session(access_token=app_token)
vk_api = vk.API(vk_session, v = 5.103)

BaseModel.metadata.create_all(engine)

def local_date_from_timestamp(ts):
    return datetime.utcfromtimestamp(ts) + timedelta(hours=3)

log = init_logger('collector', 'DEBUG')


def create_user_object(user):
    """user - user item obtained from vk_api; 
    obj - object of class User"""
    obj = {key: user[key] if key in user.keys() else None for key in User.vk_fields}
    obj["vk_id"] = user["id"]
    try:
        obj["bdate"] = datetime.strptime(obj["bdate"], "%d.%m.%Y") if (len(obj["bdate"].split(".")) == 3) else None
    except:
        obj["bdate"] = None
    obj["city"] = [obj["city"]["title"] if obj["city"] else None][0]
    obj["country"] = [obj["country"]["title"] if obj["country"] else None][0]
    obj["schools"] = [school["name"] for school in obj["schools"]] if obj["schools"] else None
    obj["is_subscribed"] = False
    return obj

def bulk_upsert_or_insert(items, model, index_elements, update=False):
    keys = items[0].keys()
    insert_stmt = postgresql.insert(model.__table__).values(items)
    update_stmt = insert_stmt.on_conflict_do_update(
    index_elements = index_elements,
    set_={key: getattr(insert_stmt.excluded, key) for key in keys}
    )
    do_nothing_stmt = insert_stmt.on_conflict_do_nothing(
    index_elements = index_elements
    )
    stmt = update_stmt if update else do_nothing_stmt
    engine.execute(stmt)
    return None


def get_subscribers(group_id, comunity_token):
    def get_members(offset, count):
        res = vk_api.groups.getMembers(
            offset=offset,
            max_count=count,
            group_id=group_id,
            fields=User.vk_fields
        )
        print("---->",res)
        return res["items"], res["count"]
    subscribers = get_all(get_members, 200)
    subscribers = [create_user_object(sub) for sub in subscribers]
    subscribers = list(map(lambda x: {**x, "is_subscribed": True}, subscribers))
    return subscribers

def get_users_by_ids(user_ids):
    users = []
    open_users = vk_api.users.get(user_ids = user_ids, fields = User.vk_fields)
    open_user_ids = [user["id"] for user in open_users]
    closed_user_ids = [user_id for user_id in user_ids if user_id not in open_user_ids]
    closed_users = [{"id": user_id} for user_id in closed_user_ids]
    users.extend(open_users + closed_users)
    users = [create_user_object(user) for user in users]
    return users


def get_posts(group_id, count):
    posts = vk_api.wall.get(owner_id=-group_id, offset=0, count=count, fields=["views"])
    posts = [{
            "group_id": group_id, 
            "data": post, 
            "vk_id": post["id"], 
            "date": local_date_from_timestamp(post['date']),
            "comments_count": post["comments"]["count"],
            "reposts_count": post["reposts"]["count"],
            "likes_count": post["likes"]["count"],
            "views_count": post["views"]["count"]
             } for post in posts["items"]]
    return posts


def get_likes(posts, group_id):
    all_post_likes = []
    for post in posts:
        def get_post_likes(offset, count): # posts.keys() - vk_ids, posts.values() - ids in db
            res = vk_api.likes.getList(
                offset=offset,
                max_count=count,
                type="post", 
                item_id=post["vk_id"], 
                owner_id=-group_id,
            )
            return res["items"], res["count"]
        post_likes = [{"group_id": group_id,
                        "post_id": post["id"], 
                        "user_id": user_id, 
                        "date": datetime.now()} 
                        for user_id in get_all(get_post_likes, 200)]
        all_post_likes.extend(post_likes)
    return all_post_likes


def get_comments(posts, group_id):
    all_post_comments = []
    for post in posts:
        def get_post_comments(offset, count):
            res = vk_api.wall.getComments(
                offset=offset,
                max_count=count,
                owner_id=-group_id, 
                post_id=post["vk_id"]
            )
            return res["items"], res["count"]
        post_comments = get_all(get_post_comments, 200)
        post_comments = [{"group_id": group_id, 
                        "post_id": post["id"],  
                        "user_id": comment["from_id"],
                        "data": comment["text"], 
                        "date": local_date_from_timestamp(comment['date'])} for comment in post_comments]
        all_post_comments.extend(post_comments)
    return all_post_comments


def compute_user_ids(likes, comments):
    user_ids = [like["user_id"] for like in likes] + [comment["user_id"] for comment in comments]
    user_ids = list(set((user_ids)))
    return user_ids

def get_subscription_events(users, group_id):
    events = []
    for user in users:
        events.append({
            "group_id": group_id,
            "user_id": user["vk_id"],
            "date": datetime.now(),
            "is_subscribed": user["is_subscribed"]
        })
    return events

def get_diff_by(items_are_in, items_not_in, by = None):
    """by - str; items_are_in and items_not_in - lists of dicts. diff - list of dicts"""
    if by == None:
        diff = [item for item in items_are_in if item not in items_not_in]
    else:
        by_not_in = [item[by] for item in items_not_in]
        diff = [item for item in items_are_in if item[by] not in by_not_in]
    return diff
    

def start_collector():
    group_id = vk_api.utils.resolveScreenName(screen_name="public193519310").get('object_id')
    
    log.debug("Updating groups")
    upsert(Group, Group.vk_id==group_id, vk_id=group_id)

    log.debug("Updating posts")
    
    posts = get_posts(group_id, count=100)
    bulk_upsert_or_insert(posts, Post, ["vk_id", "group_id"], update=True)
    posts = Post.get_all(filter = and_( Post.vk_id.in_([p["vk_id"] for p in posts]), 
                                        Post.group_id == group_id))
    
    log.debug("Getting likes, comments, users")
    all_likes = get_likes(group_id=group_id, posts=posts)

    all_comments = get_comments(group_id=group_id, posts=posts)

    commented_liked_user_ids = compute_user_ids(all_likes, all_comments)

    subscribers_vk = get_subscribers(group_id, comunity_token) 

    commented_liked_users = get_diff_by(items_are_in = get_users_by_ids(commented_liked_user_ids), 
                                        items_not_in = subscribers_vk, 
                                        by = "vk_id")
    log.debug("Updating users")
    bulk_upsert_or_insert(commented_liked_users + subscribers_vk, User, ["vk_id"])
    log.debug("Updating likes")
    bulk_upsert_or_insert(all_likes, Like, ["post_id", "user_id"])
    log.debug("Updating comments")
    bulk_upsert_or_insert(all_comments, Comment, ["group_id", "post_id", "user_id", "date"])
    


   







