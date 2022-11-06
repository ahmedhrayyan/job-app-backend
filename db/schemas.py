import bleach
from marshmallow import Schema, fields, post_load, EXCLUDE, validate, ValidationError
from flask_jwt_extended import current_user
from .models import Admin, Job
from pyuploadcare import exceptions
from utils.uploadcare import uploadcare


class Image(fields.Str):
    """ Custom logic for handling image paths """

    def _serialize(self, value, attr, obj, **kwargs):
        return uploadcare.file(value).cdn_url

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            uploadcare.file(value)
            return value
        except exceptions.InvalidParamError:
            raise ValidationError("Do not exist.")


class BaseSchema(Schema):
    id = fields.Int(dump_only=True)
    created_at = fields.AwareDateTime(dump_only=True)

    class Meta:
        # Exclude unknown fields in the deserialized output
        unknown = EXCLUDE


class AdminSchema(BaseSchema):
    email = fields.Email(required=True, validate=validate.Length(max=64))
    name = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8))

    @post_load
    def create_admin(self, data, **kwargs):
        # strip & lowercase the email field
        if 'email' in data:
            data['email'] = data['email'].strip().lower()

        # if partial option was passed, return the dictionary of fields not an object (useful for updating)
        if kwargs.get("partial"):
            return data

        return Admin(**data)


admin_schema = AdminSchema()


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


login_schema = LoginSchema()


class JobSchema(BaseSchema):
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    vacancy = fields.Int(required=True)
    salary = fields.Str(required=True)
    location = fields.Str(required=True)
    type = fields.Int(required=True, validate=validate.OneOf([1, 2]))
    company_name = fields.Str(required=True)
    company_logo = Image(required=True)
    company_email = fields.Str(required=True)

    @post_load
    def create_job(self, data, **kwargs):
        # strip & lowercase the email field
        if 'description' in data:
            data['description'] = bleach.clean(data['description'], tags=['p', 'h1', 'h2', 'h3', 'ul', 'li', 'li'])

        # if partial option was passed, return the dictionary of fields not an object (useful for updating)
        if kwargs.get("partial"):
            return data

        return Job(admin_id=current_user.id if current_user else Admin.query.first().id, **data)


job_schema = JobSchema()
