from flask import request
from flask_restful import Resource

from managers.auth import auth
from managers.user import UserManager
from models import RoleType
from schemas.request.user import UserCreateRequestSchema
from util.decorators import permission_required, validate_schema


class User(Resource):
    @auth.login_required
    @permission_required(RoleType.admin)
    @validate_schema(UserCreateRequestSchema)
    def post(self):
        data = request.get_json()
        UserManager.create_user(data)
        return 201