""" Details Marshmallow data serialization schemas """
# ----- 3RD PARTY IMPORTS -----
from marshmallow import fields, post_dump, post_load, ValidationError
from werkzeug.security import generate_password_hash
# ----- PROJECT IMPORTS -----
from extensions import ma
from models import Site, User, Channel, StatusOption, MeterConfig, Reading


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('password',)

    @post_dump
    def add_name(self, data, **kwargs):
        data['name'] = f"{data['first_name']} {data['last_name']}"
        return data


class UserCreationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

    first_name = fields.Str(required=True)
    last_name = fields.Str(required=False)
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    is_admin = fields.Boolean(required=True)
    is_operator = fields.Boolean(required=True)

    def validate_username(self, username, **kwargs):
        """ Raises error if user already exists """
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            raise ValidationError('Username already exists')

    @post_load
    def load_user(self, data) -> User:
        self.validate_username(data.get('username'))
        user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            username=data["username"],
            password=generate_password_hash(data['password'], method='scrypt'),
            is_admin=False,
            is_operator=True
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

    @post_dump(pass_many=False)
    def add_site_name(self, data, **kwargs):
        site_id = data.get('site_id')
        if site_id:
            site = Site.query.get(site_id)
            if site:
                data['site_name'] = site.display_name
        return data


class SiteSchema(ma.SQLAlchemyAutoSchema):
    channels = ma.Nested(ChannelSchema, many=True)

    class Meta:
        model = Site
        exclude = ('api_key',)

    @post_dump
    def add_display_name(self, data, **kwargs):
        data['display_name'] = data['site_name'].replace('_', ' ')
        return data


class ReadingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Reading
