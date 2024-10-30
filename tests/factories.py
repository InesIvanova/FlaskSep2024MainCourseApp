from random import randint

import factory

from db import db
from models import UserModel, RoleType
from werkzeug.security import generate_password_hash, check_password_hash


class BaseFactory(factory.Factory):
    @classmethod
    def create(cls, **kwargs):
        object = super().create(**kwargs)
        if hasattr(object, "password:"):
            plain_pass = object.password
            object.password = generate_password_hash(plain_pass, method="pbkdf2:sha256")
        db.session.add(object)
        db.session.flush()
        return object


class UserFactory(BaseFactory):
    class Meta:
        model = UserModel

    id = factory.Sequence(lambda n: n)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    phone = str(randint(100000, 200000))
    password = factory.Faker("password")
    role = RoleType.complainer
    iban = factory.Faker("iban")
