""" Details Marshmallow data serialization schemas """
from marshmallow import fields, post_dump, post_load, ValidationError, validates
from werkzeug.security import generate_password_hash

from extensions import ma
from models import Site, User, Channel, StatusOption, MeterConfig


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('password', )

    @post_dump
    def add_name(self, data, **kwargs):
        data['name'] = f"{data['first_name']} {data['last_name']}"
        return data


class UserCreationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    is_admin = fields.Boolean(required=True)

    def validate_username(self, username, **kwargs):
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            raise ValidationError('Username already exists')

    @post_load
    def load_user(self, data):
        self.validate_username(data.get('username'))
        user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            username=data["username"],
            password=generate_password_hash(data['password'], method='scrypt'),
            is_admin=False
        )
        return user


class MeterConfigSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MeterConfig
        include_fk = True
        load_instance = True


class StatusOptionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = StatusOption
        include_fk = True
        load_instance = True


class ChannelSchema(ma.SQLAlchemyAutoSchema):
    meter_config = ma.Nested(MeterConfigSchema, many=True)
    status_options = ma.Nested(StatusOptionSchema, many=True)

    class Meta:
        model = Channel
        include_fk = True
        load_instance = True


class SiteSchema(ma.SQLAlchemyAutoSchema):
    channels = ma.Nested(ChannelSchema, many=True)

    class Meta:
        model = Site
        exclude = ('api_key',)

