import json
from datetime import datetime, timedelta
from time import sleep

import vk
from sqlalchemy import and_, func, tuple_, cast, DATE
from sqlalchemy.ext.declarative import declarative_base

from app.models.db import session
from app.models.Comment import Comment
from app.models.Group import Group
from app.models.Like import Like
from app.models.Post import Post
from app.models.Repost import Repost
from app.models.Subscription import Subscription
from app.models.SubscriptionEvent import SubscriptionEvent
from app.models.User import User

from app.collector.functions import get_all, get_posts, get_comments, get_likes,\
     get_subscribers, get_users_by_ids, compute_user_ids, get_group_id_by_name
from app.utils.db import upsert, bulk_upsert_or_insert
from app.utils.log import init_logger
from app.utils.collections import get_diff_by
from app.config import comunity_token, screen_name, collector_period, init_posts_num, watch_posts_num

log = init_logger('collector', 'DEBUG')
  
def collect_vk_data(N_posts = 100, initial = True):
     if initial:
          log.info("INITIAL COLLECTING")
     else:
          log.info("WATCH COLLECTING")

     group_id = get_group_id_by_name(screen_name)

     log.debug("Updating groups")
     upsert({"vk_id": group_id}, Group, ["vk_id"])

     log.debug("Updating posts")
     posts = get_posts(group_id, count = N_posts)
     
     bulk_upsert_or_insert(posts, Post, ["vk_id", "group_id"], update=True)
     posts = Post.get_all(filter = and_(Post.vk_id.in_([p["vk_id"] for p in posts]), Post.group_id == group_id))

     log.debug("Getting likes, comments")
     all_likes = get_likes(group_id=group_id, posts=posts)

     all_comments = get_comments(group_id=group_id, posts=posts)
     commented_liked_user_ids = compute_user_ids(all_likes, all_comments)

     if initial == True:
          subscribers = get_subscribers(group_id, comunity_token) 
     else:
          subscribers = []

     log.debug("Updating users")     
     commented_liked_users = get_diff_by(items_are_in = get_users_by_ids(commented_liked_user_ids), 
                                        items_not_in = subscribers, 
                                        by = "vk_id")
     
     bulk_upsert_or_insert(commented_liked_users + subscribers, User, ["vk_id"])

     log.debug("Updating likes")
     bulk_upsert_or_insert(all_likes, Like, ["post_id", "user_id"])

     log.debug("Updating comments")
     bulk_upsert_or_insert(all_comments, Comment, ["group_id", "post_id", "user_id", "date"])

     if initial:
          log.debug("Updating subscribers")
          subscriptions_vk = [{"group_id": group_id, "user_id": item["vk_id"], "is_subscribed": True} for item in subscribers]
          bulk_upsert_or_insert(subscriptions_vk, Subscription, ["group_id", "user_id"])

     
def start_collector():
     collect_vk_data(N_posts = init_posts_num, initial = True)
     while True:
          collect_vk_data(N_posts = watch_posts_num, initial = False)
          sleep(collector_period)



   







