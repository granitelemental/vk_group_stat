from datetime import date, datetime, timedelta
import io

from sqlalchemy.orm import joinedload
from sqlalchemy import tuple_, func, cast, DATE
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import pandas as pd
import seaborn as sns

from app.models.db import session
from app.models.User import User
from app.models.Post import Post
from app.models.SubscriptionEvent import SubscriptionEvent

from app.schemas.User import UserSchema
from app.schemas.Post import PostSchema
from app.schemas.SubscriptionEvent import SubscriptionEventSchema


# sns.set()

def calculate_age(bdate):
    if bdate:
        bdate = pd.to_datetime(bdate)
        today = date.today()
        return today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))

def fig_to_response(fig):
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

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

@app.route('/v1.0/posts')
def v1_posts():
    posts = session.query(Post).options(
        joinedload(Post.likes)
    ).limit(10)
    schema = PostSchema()
    posts = schema.dump(posts, many=True)
    return jsonify(posts)


@app.route("/api/v1.0/stats/posts/top")
def get_top_posts(): 
    fields = ("id", "vk_id", "likes_count", "comments_count", "reposts_count", "date")
    weight_like, weight_comment, weight_repost = 0.2, 0.3, 0.5 
    periods = {"1d": 1,
               "1w": 7,
               "1M": 30,
               "1y": 365}
    order_by = {"default": (weight_like * Post.likes_count + 
                            weight_comment * Post.comments_count + 
                            weight_repost * Post.reposts_count).desc(),
                "likes": Post.likes_count.desc(),
                "comments": Post.comments_count.desc(),
                "reposts": Post.reposts_count.desc()}
    
    N = request.args.get('count', 10)
    period = periods[request.args.get('period', "1w")]
    by = request.args.get('by', "default")

    if period == None:
        posts = session.query(Post).order_by(order_by[by])
    else:
        time_pass = datetime.now() - timedelta(days=int(period)) # TODO перевести все время вообще в UTC
        print(time_pass)
        filter = cast(Post.date, DATE) >= time_pass
        posts = session.query(Post).filter(filter).order_by(order_by[by])

    posts = posts.limit(N)  
    schema = PostSchema(only = fields)
    posts = schema.dump(posts, many = True)
    return jsonify({'data': posts, 'ok': True})


@app.route('/v1.0/users/distr')
def v1_users():
    users = session.query(User).all()
    schema = UserSchema()
    users = schema.dump(users, many=True)
    users = pd.DataFrame(users)
    users["age"] = users["bdate"].apply(calculate_age)

    fig = plt.figure(figsize=(7,5))
    pol = { 1: "female", 
            2: "male"}
    for p in pol:
        users[users["sex"]==p][users["age"]<60]["age"].hist(bins=60, alpha=0.5,  
                                                            label=pol[p], log=False) 
    plt.legend()
    plt.title("Age-gender distribution")
    plt.xlabel("age (years)")
    plt.ylabel("Total number of users")
    response = fig_to_response(fig)
    return response

@app.route('/v1.0/subscriptions_dynamc/distr')
def v1_subscriptions_dynamc():
    sns.set()
    min_date = datetime.now()-timedelta(days=100)

    subscription_events = session.query(SubscriptionEvent).\
        filter(SubscriptionEvent.date >= min_date).\
            options(joinedload(SubscriptionEvent.user)).all()

    schema = SubscriptionEventSchema()
    subscription_events = schema.dump(subscription_events, many=True)
    subscription_events = pd.DataFrame(subscription_events)
    subscription_events.index  = pd.to_datetime(subscription_events["date"])
    subscription_events["age"] = subscription_events["user"].apply(lambda x: calculate_age(x["bdate"]))
    subscription_events["sex"] = subscription_events["user"].apply(lambda x: "female" if x["sex"]==1 else "male")
    subscription_events["is_subscribed"] = subscription_events["is_subscribed"].apply(lambda x: "subscribed" if x else "unsubscribed")
    subscription_events["is_subscribed"] = subscription_events["is_subscribed"].sort_index()

    subscription_events["cumcount"] = subscription_events.groupby(["sex", "is_subscribed"]).cumcount() + 1

    fig, ax = plt.subplots(figsize=(10,5))
    for label, df in subscription_events.groupby(["sex", "is_subscribed"]):    
        df["cumcount"].plot(ax=ax, label=f"{label}", style="-.o", alpha=0.7)
    plt.legend()
    plt.ylabel("cumulative count")
    plt.title("Subscribtions and unsubscribtions")

    response = fig_to_response(fig)
    return response


def start_app():
    app.run(port=8080, debug=True)