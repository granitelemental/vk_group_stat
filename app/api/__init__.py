from sqlalchemy.sql.expression import between
from sqlalchemy import tuple_, func, cast, DATE, String, extract, case, and_, text, INTEGER
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from datetime import datetime, timedelta, timezone

from app.models.db import session, engine
from app.models.User import User
from app.models.Post import Post
from app.models.Like import Like
from app.models.Comment import Comment
from app.models.SubscriptionEvent import SubscriptionEvent
from app.models.Subscription import Subscription
from app.models.Repost import Repost

from app.schemas.User import UserSchema
from app.schemas.Post import PostSchema
from app.schemas.SubscriptionEvent import SubscriptionEventSchema

from app.collector.functions import get_users_by_ids
from app.utils.db import filter_period, upsert
from app.utils.time import date_from_timestamp
from app.api.utils import response


import app.config as config

from app.api.routers.auth import Router as AuthRouter


def edit_group_join(json, is_subscribed):
    item = {"user_id": json["object"]["user_id"], 
            "group_id": json["group_id"],
            "is_subscribed":  is_subscribed, 
            "event_vk_id": json["event_id"]}
    upsert(item, SubscriptionEvent, ["event_vk_id"])

    item = {"user_id": item["user_id"],
            "group_id": item["group_id"],
            "is_subscribed": item["is_subscribed"]}
    upsert(item, Subscription, ["user_id", "group_id"])
    print("---->")

    item = get_users_by_ids([item["user_id"]])[0]
    item["is_subscribed"] = is_subscribed
    upsert(item, User, ["vk_id"])


def add_repost(json):
    item = {"user_id": json["object"]["from_id"],
            "post_id": Post.post_vk_to_db_id(json["object"]["copy_history"][0]["id"], json["group_id"]),
            "group_id": json["group_id"],
            "date": date_from_timestamp(json["object"]["date"]),
            "event_vk_id": json["event_id"]}
    upsert(item, Repost, ["event_vk_id"])


app = Flask('API')
CORS(app)

AuthRouter(app)


@app.route("/")
def ping():
    return jsonify({'ok': True})

@response
@app.route("/api/v1.0/events/timeline")
def get_timeline():
    """time_window: d | M | h | w | m , entities: 'posts,likes,comments,reposts' (string), start and end - string  %Y-%m-%d %H:%M:%S """
    format = '%Y-%m-%d %H:%M:%S'
    default_start = (datetime.now(tz=datetime.utc) - timedelta(hours=1000)).strftime(format)
    default_end = datetime.now(tz=datetime.utc).strftime(format)

    start = request.args.get('from', default_start) # 
    end = request.args.get('to', default_end) # 

    start = datetime.strptime(start, format).timestamp()
    end = datetime.strptime(end, format).timestamp()

    windows = {'y': 12*30*7*24*3600, 'M': 30*7*24*3600, 'w': 7*24*3600, 'd': 24*3600, 'h': 3600, 'm': 60}
    window = windows[request.args.get('time_window', 'm')]
    
    entities = {'likes': Like, 'posts': Post, 'comments': Comment, 'reposts': Repost}
    entity = entities[request.args.get('entities', 'likes')]

    
    grouper_by = cast(
        (extract('epoch', entity.date) - start) / window, 
        INTEGER
        ) 
    filter_by = and_(
        extract('epoch', entity.date) <= end, 
        extract('epoch', entity.date) > start
        )

    result = session.query(
        grouper_by * window + start, 
        func.count(entity.id) 
        ).filter(filter_by).group_by(grouper_by).all()

    return {"ok": True, "data": result, "start": str(start), "end": str(end), "time_window": window}


@app.route("/api/v1.0/stats/users/distribution")
def get_distribution():
    age_expr = case(
            [
                (between(extract("year", func.age(User.bdate)), ((i // 5) * 5) , ((i // 5 + 1) * 5 - 1)) ,
                 f"{(i // 5) * 5}-{(i // 5 + 1) * 5 - 1}") # TODO check how between works (does it include borders)
                for i in range(0,90)
            ]
        )
    gender_expr = case(
            [
                (User.sex == '1' , "female"),
                (User.sex == '2' , "male")  
            ]
        )
    by = request.args.get("property", "gender")
    groupers = {"gender": gender_expr,
                "country": User.country,
                "age": age_expr}
    result = session.query(groupers[by], func.count(User.id)).group_by(groupers[by]).all()
    result = dict(map(lambda x: x if x[0]!=None else ["not specified", x[1]], result))
    total_count = {"total": session.query(func.count(User.id)).scalar()}
    result.update(total_count)
    return jsonify({"data": result, "ok": True})


@app.route('/vk', methods=["POST"])
def add_vk_event():
    json = request.get_json()

    if json['type'] == 'group_join':
        edit_group_join(json, is_subscribed = True)

    if json['type'] == 'group_leave':
        edit_group_join(json, is_subscribed = False)    

    if json['type'] == 'wall_repost':
        add_repost(json)

    return "1"


@app.route("/api/v1.0/stats/events/activity")
def get_activity():
    period = request.args.get("period", "1w")

    posts_count = session.query(func.count(Post.id)).filter(filter_period(Post, period)).scalar()
    likes_count = session.query(func.count(Like.id)).filter(filter_period(Like, period)).scalar()
    comments_count = session.query(func.count(Comment.id)).filter(filter_period(Comment, period)).scalar()
    reposts_count = session.query(func.sum(Post.reposts_count)).filter(filter_period(Post, period)).scalar()
    views_count = session.query(func.sum(Post.views_count)).filter(filter_period(Post, period)).scalar()
    subscriptions_count = session.query(func.count(SubscriptionEvent.id)).filter(and_(filter_period(SubscriptionEvent, period),
                                                                                        SubscriptionEvent.is_subscribed == True)).scalar()
    result = {
            'ok': True,
            'data': {
                'posts': posts_count,
                'likes': likes_count,
                'comments': comments_count,
                'reposts': reposts_count,
                'subscriptions': subscriptions_count,
                'views': views_count,
            }
        }
    return jsonify(result)  

@app.route("/api/v1.0/stats/posts/top")
def get_top_posts(): 
    fields = ("id", "vk_id", "likes_count", "comments_count", "reposts_count", "views_count", "date")
    weight_like, weight_comment, weight_repost, weight_views = 0.2, 0.2, 0.5, 0.1

    order_by = {"default": (weight_like * Post.likes_count + 
                            weight_comment * Post.comments_count + 
                            weight_repost * Post.reposts_count + 
                            weight_views * Post.views_count).desc(),
                "likes": Post.likes_count.desc(),
                "comments": Post.comments_count.desc(),
                "reposts": Post.reposts_count.desc(),
                "views": Post.views_count.desc()}
    N = request.args.get('count', 10)
    period = request.args.get('period', "1w")
    by = request.args.get('by', "default")
    if period == None:
        posts = session.query(Post).order_by(order_by[by]).limit(N)
    else:
        posts = session.query(Post).filter(filter_period(Post, period)).order_by(order_by[by]).limit(N)
    schema = PostSchema(only = fields)
    posts = schema.dump(posts, many = True)
    return jsonify({'data': posts, 'ok': True})


def start_app():
    app.run(host=config.host, port=config.port , debug=True)



