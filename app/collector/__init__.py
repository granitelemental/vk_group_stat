from datetime import datetime, timedelta

import vk
import json
import tqdm
import requests
import numpy as np

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import and_, tuple_, func
from sqlalchemy.dialects import postgresql

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
from app.utils.collector import get_all


app_token = "4c6d8d6e4c6d8d6e4c6d8d6e054c02301244c6d4c6d8d6e1224aadc8ad37bd1098d8a3f" # TODO в конфиг
comunity_token = "1d05d5656b70b874e93a44b5821a378e12c48f7f249d5cdf10f81e0ca970394f144209f39480ccb02cc09" # TODO в кофиг

vk_session = vk.Session(access_token=app_token)
vk_api = vk.API(vk_session, v = 5.8)

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
    return obj

def bulk_upsert(items, model, index_elements):
    keys = items[0].keys()
    insert_stmt = postgresql.insert(model.__table__).values(items)
    update_stmt = insert_stmt.on_conflict_do_update(
    index_elements=index_elements,
    set_={key: getattr(insert_stmt.excluded, key) for key in keys}
    )
    engine.execute(update_stmt)
    return None


def get_subcribers(group_id, comunity_token):
    vk_session = vk.Session(access_token=comunity_token)
    vk_api = vk.API(vk_session, v = 5.8)
    def get_members(offset, count):
        res = vk_api.groups.getMembers(
            offset=offset,
            max_count=count,
            group_id=group_id,
            fields=User.vk_fields
        )
        return res["users"], res["count"]
    subscribers = get_all(get_members, 200)
    subscribers = [create_user_object(sub) for sub in subscribers]
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
    posts = vk_api.wall.get(owner_id=-group_id, offset=0, count=count)
    posts = [{
            "group_id": group_id, 
            "data": post, 
            "vk_id": post["id"], 
            "date": local_date_from_timestamp(post['date']),
            "comments_count": post["comments"]["count"],
            "reposts_count": post["reposts"]["count"]
             } for post in posts["items"]]
    return posts


def get_likes(posts, group_id):
    all_post_likes = []
    for post_vk_id in posts.keys():
        def get_post_likes(offset, count): # posts.keys() - vk_ids, posts.values() - ids in db
            res = vk_api.likes.getList(
                offset=offset,
                max_count=count,
                type="post", 
                item_id=post_vk_id, 
                owner_id=-group_id,
            )
            return res["items"], res["count"]
        post_db_id = posts[post_vk_id]
        post_likes = [{"group_id": group_id,
                        "post_id": post_db_id, 
                        "user_id": user_id, 
                        "date": datetime.now()} for user_id in get_all(get_post_likes, 200)]
        all_post_likes.extend(post_likes)
    return all_post_likes


def get_comments(posts, group_id):
    all_post_comments = []
    for post_vk_id in posts.keys():
        def get_post_comments(offset, count):
            res = vk_api.wall.getComments(
                offset=offset,
                max_count=count,
                owner_id=-group_id, 
                post_id=post_vk_id
            )
            return res["items"], res["count"]
        post_comments = get_all(get_post_comments, 200)
        post_db_id = posts[post_vk_id]
        post_comments = [{"group_id": group_id, 
                        "post_id": post_db_id,  
                        "user_id": comment["from_id"],
                        "data": comment["text"], 
                        "date": local_date_from_timestamp(comment['date'])} for comment in post_comments]
        all_post_comments.extend(post_comments)
    return all_post_comments


def compute_user_ids(likes, comments):
    user_ids = [like["user_id"] for like in likes] + [comment["user_id"] for comment in comments]
    user_ids = list(set((user_ids)))
    return user_ids
    

def start_collector():
    group_id = vk_api.utils.resolveScreenName(screen_name="public193519310").get('object_id')
    
    log.debug("Updating groups")
    upsert(Group, Group.vk_id==group_id, vk_id=group_id)

    log.debug("Getting posts info and upserting posts:")
    
    posts = get_posts(group_id, count=100)
    bulk_upsert(posts, Post, ["vk_id", "group_id"])

    posts = session.query(Post).with_entities(Post.vk_id, Post.id).filter(
        Post.vk_id.in_([p["vk_id"] for p in posts]),
        Post.group_id == group_id
    ).all()
    posts = dict(posts)

    all_likes = get_likes(group_id=group_id, posts=posts)
    all_comments = get_comments(group_id=group_id, posts=posts)
    all_users_ids = compute_user_ids(all_likes, all_comments)
    
    current_subcribers = get_subcribers(group_id, comunity_token)  # потом разобраться c субскрибшенами
    users = get_users_by_ids(all_users_ids)
    users = users + [sub for sub in current_subcribers if sub not in users]


    bulk_upsert(users, User, ["vk_id"])
    bulk_upsert(all_likes, Like, ["post_id", "user_id"])
    bulk_upsert(all_comments, Comment, ["group_id", "post_id", "user_id", "date"])

    









    




    

    print("Collecting subscriptions")
    subscribers = collect_subcriptions(group_id, comunity_token)

    print("Adding users with subscribers")
    query = session.query(User)
    existing_user_ids = [item.vk_id for item in query.filter(User.vk_id.in_([sub["id"] for sub in subscribers])).all()]

    user_objects = create_user_objects([sub for sub in subscribers if sub["id"] not in existing_user_ids])
    session.bulk_save_objects(user_objects)
    session.commit()

    print("Adding subscriptions")
    current_subscriptions_vk = [(sub["id"], group_id) for sub in subscribers]
    existing_subscriptions_db = session.query() \
        .with_entities(Subscription.user_id, Subscription.group_id) \
        .filter(tuple_(Subscription.user_id, Subscription.group_id) \
        .in_(current_subscriptions_vk)).all()
    
    resubscribed_users_db = session.query() \
        .with_entities(Subscription.id, Subscription.user_id, Subscription.group_id) \
        .filter(and_(tuple_(Subscription.user_id, Subscription.group_id) \
        .in_(current_subscriptions_vk),
        (Subscription.is_subscribed==False))).all()

    deleted_subscriptions_db = session.query() \
        .with_entities(Subscription.id, Subscription.user_id, Subscription.group_id) \
        .filter(tuple_(Subscription.user_id, Subscription.group_id) \
        .notin_(current_subscriptions_vk)).all()
    

    subscription_event_mappings = [{
        "user_id": sub[1], 
        "group_id": sub[2],
        "date": datetime.now(), 
        "is_subscribed": True}
        for sub in resubscribed_users_db] + \
            [{
        "user_id": sub[0], 
        "group_id": sub[1], 
        "date": datetime.now(),
        "is_subscribed": True} 
        for sub in current_subscriptions_vk
        if sub not in existing_subscriptions_db] + \
            [{
        "user_id": sub[1], 
        "group_id": sub[2], 
        "date": datetime.now(),
        "is_subscribed": False}
        for sub in deleted_subscriptions_db]

    session.bulk_insert_mappings(SubscriptionEvent, subscription_event_mappings)
    session.commit()

    new_subscription_mappings = [{
        "user_id": sub[0], 
        "group_id": sub[1], 
        "is_subscribed": True} 
        for sub in current_subscriptions_vk
        if sub not in existing_subscriptions_db]
    session.bulk_insert_mappings(Subscription, new_subscription_mappings)
    session.commit()

    resubscribed_user_mappings = [{
        "id": sub[0],
        "user_id": sub[1], 
        "group_id": sub[2], 
        "is_subscribed": True}
        for sub in resubscribed_users_db]
    session.bulk_update_mappings(Subscription, resubscribed_user_mappings)
    session.commit()

    deleted_subscriber_mappings = [{
        "id": sub[0],
        "user_id": sub[1], 
        "group_id": sub[2], 
        "is_subscribed": False}
        for sub in deleted_subscriptions_db]
    session.bulk_update_mappings(Subscription, deleted_subscriber_mappings)
    session.commit()

    
    print("Collecting likes:")
    likes = []
    for post in tqdm.tqdm(post_items):
        post_id = session.query(Post).filter(Post.vk_id==post["id"]).one_or_none().id
        for user_vk_id in post_like_usr_ids[post["id"]]:
            # user_id = session.query(User).filter(User.vk_id==user_vk_id).one_or_none().id
            if not session.query(Like).filter(Like.user_id==user_vk_id, Like.post_id==post_id).one_or_none():
                likes.append(Like(group_id=group_id, post_id=post_id, user_id=user_vk_id, date=datetime.now()))

    print("Inserting likes:")
    session.bulk_save_objects(likes)
    session.commit()


    




