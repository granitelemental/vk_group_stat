from datetime import datetime, timedelta

import vk
import json
import tqdm
import requests
import numpy as np

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
from app.utils.collector import get_all

from app.collector.functions import collect_post_entities

app_token = "4c6d8d6e4c6d8d6e4c6d8d6e054c02301244c6d4c6d8d6e1224aadc8ad37bd1098d8a3f" # TODO в конфиг
comunity_token = "1d05d5656b70b874e93a44b5821a378e12c48f7f249d5cdf10f81e0ca970394f144209f39480ccb02cc09" # TODO в кофиг

vk_session = vk.Session(access_token=app_token)
vk_api = vk.API(vk_session, v = 5.8)

BaseModel.metadata.create_all(engine)

def local_date_from_timestamp(ts):
    return datetime.utcfromtimestamp(ts) + timedelta(hours=3)

log = init_logger('collector', 'debug')

log.error('dsds')

def collect_subcriptions(group_id, comunity_token):
    vk_session = vk.Session(access_token=comunity_token)
    vk_api = vk.API(vk_session, v = 5.8)

    def get_members(offset, count):
        res = vk_api.groups.getMembers(
            offset=offset,
            max_count=count,
            group_id=group_id,
            fields=User.vk_fields
        )
        return res["users"]

    subscribers = get_all(get_members, 200)
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

def pick_keys(d, *keys):
    try:
        return tuple([d[key] for key in keys])
    except:
        print(f"Invalid keys {keys} for dict {d}")

def start_collector():
    group_id = vk_api.utils.resolveScreenName(screen_name="public193519310").get('object_id')
    
    log.debug("Updating groups")
    upsert(Group, Group.vk_id==group_id, vk_id=group_id)

    log.debug("Getting posts info and upserting posts:")
    posts = vk_api.wall.get(owner_id=-group_id, offset=0, count=100)

    post_items = posts['items']
    post_like_usr_ids = {post["id"]: [] for post in post_items}
    post_comments = []
    post_like_usr_ids["all_usr_ids"] = []

    # {
    #     '12312': []
    #     'all_usr_ids': []
    # }    
   
    for post in tqdm.tqdm(post_items):
        def get_likes(offset, count):
            res = vk_api.likes.getList(
                max_count=count,
                type="post", 
                item_id=post["id"], 
                owner_id=post["owner_id"]
            )
            return res["items"]

        def get_comments(offset, count):
            res = vk_api.wall.getComments(
                max_count=count,
                owner_id=-group_id, 
                post_id=post["id"]
            )

            return res["items"]

        post_likes = get_all(get_likes, 200)
        post_comments = get_all(get_comments, 200)

        localdate = local_date_from_timestamp(post['date'])

        upsert(Post, Post.vk_id == post['id'],
            group_id = group_id, 
            data = post, 
            vk_id = post["id"], 
            date = localdate,
            comments_count = post["comments"]["count"],
            reposts_count = post["reposts"]["count"])

        collect_post_entities(post, post_likes, post_comments)

   
    query = session.query(Comment)

    keys = "group_id", "post_id", "user_id", "date"#, "data"

    current_post_comments = [pick_keys(comment, *keys) for comment in post_comments]
    print("----->")
    # print(current_post_comments)
    existing_post_comments = session.query() \
        .with_entities(Comment.group_id, Comment.post_id, Comment.user_id, Comment.date) \
        .filter(tuple_(Comment.group_id, Comment.post_id, Comment.user_id, Comment.date) \
        .in_([pick_keys(comment, *keys) for comment in post_comments])).all()

    print(existing_post_comments)
    print(len(existing_post_comments))

    current_post_comments = [comment for comment in post_comments \
        if pick_keys(comment, *keys) not in existing_post_comments]
    # print("----->")
    # print(current_post_comments[0].values())
    keys = "group_id", "post_id", "user_id", "date", "data"
    current_post_comment_mappings = [dict(zip(keys, comment.values())) for comment in current_post_comments]
    # print("-------mappings")
    # print(current_post_comment_mappings)
    session.bulk_insert_mappings(Comment, current_post_comment_mappings)
    session.commit()




    print("Updating comments")
    
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


    


   


