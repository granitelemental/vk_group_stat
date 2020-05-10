import traceback
from functools import wraps

from flask import jsonify, request
import jwt

from app.api.errors import *

def response(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        try:
            return jsonify({
                'ok': True,
                'data': fn(),
            })
        except Exception as error:
            print(error)
            traceback.print_exc()
            try:
                code = error.code
            except: 
                code = 500

            return jsonify({
                'ok': False,
                'error': {
                    'message': str(error)
                }
            }), code
    return wrapped

def with_authorization(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            raise NotAuthorizedError('Not authorised')

            jwt_data = jwt.decode(token, 'secret', algorithms=['HS256'])