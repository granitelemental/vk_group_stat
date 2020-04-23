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

def update_likes(likes):
   pass

def update_comments(comments):
   pass

def update_users(users):
   pass