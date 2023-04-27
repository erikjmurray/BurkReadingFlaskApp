"""
Creates necessary Flask instances as variable.
Easily referenced in other files without creating circular import
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_marshmallow import Marshmallow

# instantiation of SQLAlchemy ORM object
db = SQLAlchemy()

# instantiation of Marshmallow object
ma = Marshmallow()

# instantiation of LoginManager object
login_manager = LoginManager()

