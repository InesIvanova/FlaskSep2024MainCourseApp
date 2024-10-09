from flask import request
from flask_restful import Resource

from managers.auth import auth
from managers.complainer import ComplainerManager
from models.enums import RoleType
from schemas.request.complaint import ComplaintRequestSchema
from schemas.response.complaint import ComplaintResponseSchema
from util.decorators import permission_required, validate_schema


class ComplaintListCreate(Resource):
    @auth.login_required
    def get(self):
        user = auth.current_user()
        complaints = ComplainerManager.get_claims(user)
        return {"complaints": ComplaintResponseSchema().dump(complaints, many=True)}

    @auth.login_required
    @permission_required(RoleType.complainer)
    @validate_schema(ComplaintRequestSchema)
    def post(self):
        data = request.get_json()
        user = auth.current_user()
        ComplainerManager.create(user, data)
        return 201


class ComplaintApprove(Resource):
    @auth.login_required
    @permission_required(RoleType.approver)
    def put(self, complaint_id):
        ComplainerManager.approve(complaint_id)
        return 204


class ComplaintReject(Resource):
    @auth.login_required
    @permission_required(RoleType.approver)
    def put(self, complaint_id):
        ComplainerManager.reject(complaint_id)
        return 204


# class ComplaintDetail(Resource):
#     @auth.login_required
#     @permission_required(RoleType.admin)
#     def delete(self, complaint_id):


