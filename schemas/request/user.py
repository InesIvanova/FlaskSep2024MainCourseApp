from marshmallow import Schema, fields, validates_schema, ValidationError
from marshmallow.validate import OneOf


class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    # TODO homework - add more validations for the password
    password = fields.String(required=True)


class UserRegisterSchema(UserLoginSchema):
    # TODO homework - add more validations for the first and last name
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    phone = fields.String()
    iban = fields.String(required=True)


class UserCreateRequestSchema(UserRegisterSchema):
    role = fields.String(required=True, validate=OneOf(["admin", "approver"]))
    certificate = fields.URL()

    @validates_schema
    def validate_cerfificate(self, data, **kwargs):
        if data["role"] == "approver" and "certificate" not in data:
            raise ValidationError(
                "You must append certificate for approver user",
                field_names=["certificate"],
            )
        if data["role"] == "admin":
            raise ValidationError(
                "Admins should not have certificate",
                field_names=["certificate"],
            )


class PasswordChangeSchema(Schema):
    old_password = fields.String(required=True)
    new_password = fields.String(required=True)

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        # Ensure that the old password is not the same as the new password
        if data["old_password"] == data["new_password"]:
            raise ValidationError(
                "New password cannot be the same as the old password.",
                field_names=["new_password"],
            )

