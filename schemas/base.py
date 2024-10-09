from marshmallow import Schema, fields


class BaseComplaint(Schema):
    title = fields.String(required=True)
    description = fields.String(required=True)
    photo_url = fields.URL(required=True)
    amount = fields.Float(required=True)