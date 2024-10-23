from marshmallow import fields

from schemas.base import BaseComplaint


class ComplaintRequestSchema(BaseComplaint):
    photo = fields.String(required=True)
    photo_extension = fields.String(required=True)
