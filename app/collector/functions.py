from datetime import datetime, timedelta

import vk

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import and_, tuple_, func

from app.models.db import session, engine
from app.models.User import User
from app.models.Post import Post
from app.models.Like import Like
from app.models.Group import Group
from app.models.Comment import Comment
from app.models.Subscription import Subscription
from app.models.SubscriptionEvent import SubscriptionEvent

from app.models.db import BaseModel  # BaseModel запоминает, что от нее наследовалось в User, Post и Like, при create_all создает все эти таблицы

from app.utils.log import init_logger
from app.utils.db import upsert
from app.utils.time import date_from_timestamp

from app.config import app_token, vk_api_version

vk_session = vk.Session(access_token = app_token)
vk_api = vk.API(vk_session, v = vk_api_version)


def get_all(get_function, max_count):
    """get_function - function which collects data from api;
    max_count - max count of items per one attempt;
    """
    offset = 0
    all_items = []
    result, total_count = get_function(offset, max_count)

    while offset < total_count:
        result, _ = get_function(offset, max_count)
        all_items.extend(result)
        offset += max_count
    return all_items

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

def compute_user_ids(likes, comments):
    user_ids = [like["user_id"] for like in likes] + [comment["user_id"] for comment in comments]
    user_ids = list(set((user_ids)))
    return user_ids

def get_group_id_by_name(screen_name):
    group_id = vk_api.utils.resolveScreenName(screen_name = screen_name).get('object_id')
    return group_id

def get_posts(group_id, count):
    posts = vk_api.wall.get(owner_id=-group_id, offset=0, count=count, fields=["views"])
    posts = [{
            "group_id": group_id, 
            "data": post, 
            "vk_id": post["id"], 
            "date": date_from_timestamp(post['date']),
            "comments_count": post.get("comments", {}).get("count", 0),
            "reposts_count": post.get("reposts", {}).get("count", 0),
            "likes_count": post.get("likes", {}).get("count", 0),
            "views_count": post.get("views", {}).get('count', 0)
             } for post in posts.get("items", [])]
    return posts


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
                        "date": date_from_timestamp(comment['date'])} for comment in post_comments]
        all_post_comments.extend(post_comments)
    return all_post_comments

def get_likes(posts, group_id):
    all_post_likes = []
    for post in posts:
        def get_post_likes(offset, count): 
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

def get_subscribers(group_id, comunity_token):
    def get_members(offset, count):
        res = vk_api.groups.getMembers(
            offset=offset,
            max_count=count,
            group_id=group_id,
            fields=User.vk_fields
        )
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


