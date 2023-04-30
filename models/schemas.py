""" Details Marshmallow data serialization schemas """
from marshmallow import fields, post_load, ValidationError, validates
from werkzeug.security import generate_password_hash

from extensions import ma
from models import Site, User, Channel, StatusOption, MeterConfig


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('password', )


class UserCreationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    privilege = fields.Str(required=True)

    @validates('username')
    def validate_username(self, username, **kwargs):
        # Check if the username is unique
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            raise ValidationError('Username already exists')

    # @validates('password')
    # def validate_password(self, password, **kwargs):
    #     # Check if password meets the criteria
    #     errors = []
    #     if len(password) < 8:
    #         errors.append('Password must be at least 8 characters long')
    #     if not any(char.isupper() for char in password):
    #         errors.append('Password must contain at least one uppercase letter')
    #     if not any(char.islower() for char in password):
    #         errors.append('Password must contain at least one lowercase letter')
    #     if not any(char.isdigit() for char in password):
    #         errors.append('Password must contain at least one number')
    #     if errors:
    #         raise ValidationError(errors)

    @post_load
    def load_user(self, data):
        user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            username=data["username"],
            password=generate_password_hash(data['password'], method='scrypt'),
            privilege='User'
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

