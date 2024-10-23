from marshmallow import fields
from marshmallow_enum import EnumField

from models import State
from schemas.base import BaseComplaint


class ComplaintResponseSchema(BaseComplaint):
    id = fields.Integer(required=True)
    status = EnumField(State, by_value=True)
    complainer_id = fields.Integer(required=True)
    create_on = fields.DateTime(required=True)
    photo_url = fields.URL(required=True)
