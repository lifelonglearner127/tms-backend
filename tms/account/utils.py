import jwt
from datetime import datetime, timedelta
from django.conf import settings


def jwt_payload_handler(user):
    payload = {
        'username': user.username,
        'user_type': user.user_type,
        'exp': datetime.utcnow() + timedelta(days=7)
    }

    return payload


def jwt_encode_handler(payload):
    key = settings.SECRET_KEY
    return jwt.encode(
        payload,
        key,
        algorithm='HS256'
    ).decode('utf-8')
