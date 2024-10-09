from flask import request
from marshmallow import Schema
from werkzeug.exceptions import Forbidden, BadRequest

from managers.auth import auth


def permission_required(required_role):
    def decorator(func):
        def wrapper(*args, **kwargs):
            current_user = auth.current_user()

            if current_user.role != required_role:
                raise Forbidden("You do not have permissions to access this resource")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_schema(schema_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            schema: Schema = schema_name()
            data = request.get_json()
            errors = schema.validate(data)
            if errors:
                raise BadRequest(f"Invalid payload {errors}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

