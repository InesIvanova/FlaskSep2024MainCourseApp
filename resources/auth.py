from flask import request
from flask_restful import Resource

from managers.auth import auth
from managers.complainer import ComplainerManager
from managers.user import UserManager
from schemas.request.user import UserLoginSchema, UserRegisterSchema, PasswordChangeSchema
from util.decorators import validate_schema


class RegisterComplainer(Resource):
    @validate_schema(UserRegisterSchema)
    def post(self):
        data = request.get_json()
        token = ComplainerManager.register(data)
        return {"token": token}, 201


class Login(Resource):
    @validate_schema(UserLoginSchema)
    def post(self):
        data = request.get_json()
        token = ComplainerManager.login(data)
        return {"token": token}


class Password(Resource):
    @auth.login_required
    @validate_schema(PasswordChangeSchema)
    def post(self):
        data = request.get_json()
        UserManager.change_password(data)
        return 204
