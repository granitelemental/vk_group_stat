from datetime import date
import io

from sqlalchemy.orm import joinedload
from flask import Flask, jsonify, request, Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from app.models.db import session
from app.models.User import User 
from app.schemas.User import UserSchema

from app.models.Post import Post 
from app.schemas.Post import PostSchema

# sns.set()

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def fig_to_response(fig):
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

app = Flask('API')

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

@app.route('/v1.0/users/distr')
def v1_users():
    users = session.query(User).all()
    schema = UserSchema()
    users = schema.dump(users, many=True)
    result = pd.DataFrame(users)
    result["bdate"] = pd.to_datetime(result["bdate"])
    result["age"] = result["bdate"].apply(calculate_age)

    fig = plt.figure(figsize=(7,5))
    pol = { 1: "female", 
            2: "male"}
    for p in pol:
        result[result["sex"]==p][result["age"]<60]["age"].hist(bins=60, alpha=0.5,  
                                                            label=pol[p], log=False) 
    plt.legend()
    plt.title("Age-gender distribution")
    plt.xlabel("age (years)")
    plt.ylabel("Total number of users")
    response = fig_to_response(fig)

    return response

def start_app():
    app.run(port=8080, debug=True)