""" Details Marshmallow data serialization schemas """

from extensions import ma
from models import Site, User, Channel, StatusOption, MeterConfig


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('password', )


class SiteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Site
        exclude = ('api_key', )


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

