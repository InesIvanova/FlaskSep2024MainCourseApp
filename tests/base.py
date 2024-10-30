from config import create_app
from db import db
from managers.auth import AuthManager
from flask_testing import TestCase

from models import UserModel


def generate_token(user):
    return AuthManager.encode_token(user)


class APIBaseTestCase(TestCase):
    def create_app(self):
        return create_app("config.TestingConfig")

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def register_user(self) -> tuple[str, str]:
        data = {
            "email": "a@a.com",
            "password": "asd",
            "first_name": "Test",
            "last_name": "testov",
            "phone": "08888888",
            "iban": "BG1234",
        }

        users = UserModel.query.all()
        self.assertEqual(len(users), 0)

        resp = self.client.post("/register", json=data)
        self.assertEqual(resp.status_code, 201)
        token = resp.json["token"]
        self.assertIsNotNone(data)
        return (data["email"], data["password"])
