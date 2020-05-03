from datetime import date, datetime, timedelta
import io

from sqlalchemy.orm import joinedload
from sqlalchemy import tuple_, func, cast, DATE
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import pandas as pd

from app.models.db import session
from app.models.User import User
from app.models.Post import Post
from app.models.Like import Like
from app.models.Comment import Comment
from app.models.SubscriptionEvent import SubscriptionEvent

from app.schemas.User import UserSchema
from app.schemas.Post import PostSchema
from app.schemas.SubscriptionEvent import SubscriptionEventSchema

from app.utils.db import filter_period



def calculate_age(bdate):
    if bdate:
        bdate = pd.to_datetime(bdate)
        today = date.today()
        return today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))

def get_current_subscribers(Subscription):
    subquery = session.\
        query(Subscription.user_id, func.max(Subscription.date)).\
            group_by(Subscription.user_id).all()
    query = session.\
        query(Subscription.id, Subscription.user_id, Subscription.user_id, Subscription.date).\
            filter(tuple_(Subscription.user_id, Subscription.date).in_(list(subquery)), Subscription.is_subscribed==True)
    return query.all()

app = Flask('API')
CORS(app)

@app.route("/")
def ping():
    return jsonify({'ok': True})

@app.route("/api/v1.0/stats/users/distribution")
def get_distribution():
    age_bins = {f"{i}-{i+4}": lambda x: x>=i and x<i+4 for i in range(0,90, 5)}
    by = request.args.get("property", "gender")
    groupers = {"gender": User.sex,
                "country": User.country
                }
    result = session.query(groupers[by], func.count(User.id)).group_by(groupers[by]).all()
    result = dict(map(lambda x: x if x[0]!=None else ["not specified", x[1]],result))
    return jsonify({"data": result, "ok": True})



@app.route("/api/v1.0/stats/events/activity")
def get_activity():
    period = request.args.get("period", "1w")

    posts_count = session.query(func.count(Post.id)).filter(filter_period(Post, period)).scalar()
    likes_count = session.query(func.count(Like.id)).filter(filter_period(Like, period)).scalar()
    comments_count = session.query(func.count(Comment.id)).filter(filter_period(Comment, period)).scalar()
    reposts_count = session.query(func.sum(Post.reposts_count)).filter(filter_period(Post, period)).scalar() # TODO проверить, можно ли доставать не из евентов
    views_count = session.query(func.sum(Post.views_count)).filter(filter_period(Post, period)).scalar() # TODO проверить, можно ли доставать не из евентов
    # subscriptions_count # TODO проверить, можно ли доставать не из евентов
    result = {
            'ok': True,
            'data': {
                'posts': posts_count,
                'likes': likes_count,
                'comments': comments_count,
                'reposts': reposts_count,
                # 'subscriptions': number,
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
    app.run(port=8080, debug=True)