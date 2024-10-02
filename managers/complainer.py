from werkzeug.exceptions import Unauthorized
from werkzeug.security import generate_password_hash, check_password_hash

from db import db
from managers.auth import AuthManager
from models import RoleType, UserModel


class ComplainerManager:
    @staticmethod
    def login(data):
        user = db.session.execute(db.select(UserModel).filter_by(email=data["email"])).scalar()
        if user and check_password_hash(user.password, data["password"]):
            return AuthManager.encode_token(user)
        raise Unauthorized()

    @staticmethod
    def register(complainer_data):
        complainer_data["password"] = generate_password_hash(
            complainer_data["password"], method="pbkdf2:sha256"
        )
        complainer_data["role"] = RoleType.complainer.name
        user = UserModel(**complainer_data)
        db.session.add(user)
        db.session.flush()
        return AuthManager.encode_token(user)
