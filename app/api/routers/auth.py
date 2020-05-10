import urllib 
import requests 
import vk
import jwt

from flask import Flask, redirect, jsonify, request

from app.models.db import session
from app.models.Account import Account
from app.models.User import User

from app.collector.functions import create_user_object

from app.api.utils import response
from app.config import app_token, vk_api_version
from app.api.errors import NotFoundError

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

@response
def auth_vk():
    json = request.get_json()
    code = json['code']
    redirect_uri = json['redirect_uri']
    data = get_access_token(redirect_uri, code)

    vk_user_id = data['user_id']

    acc = Account.get_by(Account.vk_id == vk_user_id, except_fields=[Account.password_hash])
    
    if not acc:
        raise NotFoundError('Пользователь не найден')

    token = jwt.encode({
        'id': acc['id'],
        'vk_id': vk_user_id,
    }, 'secret', algorithm='HS256').decode('utf-8')

    return {**acc, 'token': token}

@response
def sign_up_vk_check():
    json = request.get_json()
    code = json['code']

    redirect_uri =  json['redirect_uri']
    data = get_access_token(redirect_uri, code)
    
    if data.get('error'):
        raise Exception(data['error_description'])

    vk_user_id = data['user_id']

    acc = Account.get_by(Account.vk_id == vk_user_id)

    if acc:
        raise Exception('Пользователь уже зарегистрирован')

    return {
        'vk_id': vk_user_id,
        'email': data['email'],
        'access_token': data['access_token'],
    }

@response
def sign_up_vk():
    json = request.get_json()

    access_token = json['access_token']
    vk_user_id = json['vk_id']
    email = json['email']
    password = json['password']

    acc = Account.get_by(Account.vk_id == vk_user_id)

    if acc:
        raise Exception('Пользователь уже зарегистрирован')

    vk_session = vk.Session(access_token=access_token)
    vk_api = vk.API(vk_session, v=vk_api_version)

    user = vk_api.users.get(user_ids=[vk_user_id], fields=User.vk_fields)

    if (user[0]):
        u = create_user_object(user[0])
        User.save(u, ['vk_id'])

    Account.save({
        'vk_id': vk_user_id,
        'email': email,
    }, ['id'])

    acc = Account.get(Account.vk_id == vk_user_id)

    token = jwt.encode({
        'id': acc.id,
        'vk_id': vk_user_id,
    }, 'secret', algorithm='HS256').decode('utf-8')

    acc.set_password(password)
    session.commit()

    updated_acc = Account.get_by(Account.id == acc.id, except_fields=[Account.password_hash])    
    return {**updated_acc, 'token': token}

@response
def auth():
    token = request.headers.get('Authorization')

    if token:
        jwt_data = jwt.decode(token, 'secret', algorithms=['HS256'])

        account = Account.get_by(Account.id == jwt_data['id'], except_fields=[Account.password_hash])

        if not account:
            raise NotFoundError('User not found')

        return {**account, 'token': token}
    else:
        json = request.get_json()
        
        email = json['email']
        password = json['password']

        account = Account.get(Account.email == email)
        account.check_password(password)

        account = Account.get_by(Account.email == email, except_fields=[Account.password_hash])

        token = jwt.encode({
            'id': account['id'],
            'vk_id': account['vk_id'],
        }, 'secret', algorithm='HS256').decode('utf-8')
        return {**account, 'token': token}


def Router(app):
    app.route('/api/v1.0/auth', methods=['POST'])(auth)
    app.route('/api/v1.0/auth/vk', methods=['POST'])(auth_vk)
    
    app.route('/api/v1.0/signup/vk/check', methods=['POST'])(sign_up_vk_check)
    app.route('/api/v1.0/signup/vk', methods=['POST'])(sign_up_vk)
