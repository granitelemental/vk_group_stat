from flask import Flask, jsonify

from app.models.User import User 
from app.models.db import session

from app.schemas.User import UserSchema

app = Flask('API')

@app.route("/")
def ping():
    return jsonify({'ok': True})

@app.route('/v1.0/users')
def v1_users():
    users = session.query(User).all()
    schema = UserSchema()

    return jsonify(schema.dump(users, many=True))

def start_app():
    app.run(port=8080, debug=True)