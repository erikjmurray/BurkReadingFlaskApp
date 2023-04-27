""" Details Marshmallow data serialization schemas """

from extensions import ma
from models import Site, User


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('password', )


class SiteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Site
        exclude = ('api_key', )
