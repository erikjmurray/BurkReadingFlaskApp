
# ----- IMPORTS -----
from extensions import db
from flask_login import UserMixin


# ----- MODELS -----
class User(UserMixin, db.Model):
    """
    Users of the web app
    Includes all MCEODs
    Define Admin privileges here
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)

    @property
    def name(self):
        return self.fullname()

    def fullname(self):
        return f"{self.first_name} {self.last_name}"
