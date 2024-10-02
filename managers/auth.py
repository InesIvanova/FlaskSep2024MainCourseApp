from datetime import datetime, timedelta

import jwt

from decouple import config
from flask_httpauth import HTTPTokenAuth
from werkzeug.exceptions import Unauthorized

from db import db
from models.user import UserModel


class AuthManager:
    @staticmethod
    def encode_token(user):
        payload = {
            "sub": user.id,
            "exp": datetime.utcnow() + timedelta(days=2),
            "role": user.role if isinstance(user.role, str) else user.role.name,
        }
        return jwt.encode(payload, key=config("SECRET_KEY"), algorithm="HS256")

    @staticmethod
    def decode_token(token):
        try:
            info = jwt.decode(jwt=token, key=config("SECRET_KEY"), algorithms=["HS256"])
            return info["sub"], info["role"]
        except Exception as ex:
            raise ex


auth = HTTPTokenAuth(scheme="Bearer")


@auth.verify_token
def verify_token(token):
    try:
        user_id, type_user = AuthManager.decode_token(token)
        return db.session.execute(db.select(UserModel).filter_by(id=user_id)).scalar()
    except Exception:
        raise Unauthorized("Invalid or missing token")
