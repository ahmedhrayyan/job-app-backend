import bleach
from marshmallow import Schema, fields, post_load, EXCLUDE, validate
from enum import Enum, unique
from .models import Admin, Job


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


class JobSchema(BaseSchema):
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    vacancy = fields.Int(required=True)
    salary = fields.Str(required=True)
    location = fields.Str(required=True)
    type = fields.Int(required=True, validate=validate.OneOf([1, 2]))
    company_name = fields.Str(required=True)
    company_logo = fields.Str(required=True)
    company_email = fields.Str(required=True)

    @post_load
    def create_job(self, data, **kwargs):
        # strip & lowercase the email field
        if 'description' in data:
            data['description'] = bleach.clean(data['description'], tags=['p', 'h1', 'h2', 'h3', 'ul', 'li', 'li'])

        # if partial option was passed, return the dictionary of fields not an object (useful for updating)
        if kwargs.get("partial"):
            return data

        return Job(**data)


job_schema = JobSchema()
