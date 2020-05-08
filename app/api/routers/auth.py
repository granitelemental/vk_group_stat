import urllib 
import requests 
import vk
import jwt

from flask import Flask, redirect, jsonify, request

from app.models.Account import Account
from app.models.User import User

from app.collector.functions import create_user_object

from app.config import app_token, vk_api_version


def get_access_token(redirect, code):
    if not code:
        raise Exception('Not authorised')

    r = requests.get('https://oauth.vk.com/access_token', params={
        'client_id': 7455040,
        'client_secret': 'PdU6rNCBPjWBiRAilPfM',
        'redirect_uri': redirect,
        'code': code
    })

    return r.json()

def auth_vk_callback():
    code = request.args['code']
    data = get_access_token('http://localhost:8080/api/v1.0/auth/vk/callback', code)

    vk_user_id = data['user_id']
    access_token = data['access_token']

    user = User.get_by(User.vk_id == vk_user_id)

    if not user:
        # Сохранить пользователя из vk
        pass

    acc = Account.get_by(Account.vk_id == vk_user_id)

    return jsonify({
        'ok': True,
        'data': {
        }
    })


def sign_up_vk_callback():
    code =  request.args['code']
    data = get_access_token('http://localhost:8080/api/v1.0/signup/vk/callback', code)

    print(data)
    vk_user_id = data['user_id']
    access_token = data['access_token']
    email = data.get('email') # TODO What if no email

    vk_session = vk.Session(access_token=access_token)
    vk_api = vk.API(vk_session, v=vk_api_version)

    user = vk_api.users.get(user_ids=[vk_user_id], fields=User.vk_fields)

    print(user)

    if (user[0]):
        u = create_user_object(user[0])
        User.save(u, ['vk_id'])

    acc = Account.get_by(Account.vk_id == vk_user_id)

    if acc:
        return jsonify({
            'ok': False,
            'error': {
                'message': 'Пользователь уже зарегистрирован'
            }
        })

    Account.save({
        'vk_id': vk_user_id,
        'email': email,
    }, ['id'])

    acc = Account.get_by(Account.vk_id == vk_user_id)

    token = jwt.encode({
        'id': acc['id']
    }, 'secret', algorithm='HS256').decode('utf-8')

    print({**acc, 'token': token})

    Account.save({**acc, 'token': token}, ['id'])

    return redirect(f'http://localhost:3000/signup/?token={token}&email={email}')

# Завершение регистрации
def sign_up_complete():
    pass


def Router(app):
    app.route('/api/v1.0/auth/vk/callback', methods=['GET'])(auth_vk_callback)
    app.route('/api/v1.0/signup/vk/callback', methods=['GET'])(sign_up_vk_callback)
    app.route('/api/v1.0/signup/complete', methods=['GET'])(sign_up_complete)