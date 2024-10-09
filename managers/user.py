from werkzeug.exceptions import BadRequest
from werkzeug.security import generate_password_hash, check_password_hash

from db import db
from managers.auth import auth
from models import UserModel


class UserManager:
    @staticmethod
    def create_user(user_data):
        user_data['password'] = generate_password_hash(user_data['password'], method='pbkdf2:sha256')
        user = UserModel(**user_data)
        db.session.add(user)
        db.session.flush()

    @staticmethod
    def change_password(pass_data):
        user = auth.current_user()

        if not check_password_hash(user.password, pass_data["old_password"]):
            raise BadRequest("Invalid password")

        user.password = generate_password_hash(pass_data["new_password"], method='pbkdf2:sha256')
        db.session.add(user)
        db.session.flush()
