
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
    name = db.Column(db.String(1000), nullable=False)       # firstname*lastname
    username = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(100), nullable=False)    # hash comparator
    privilege = db.Column(db.String(15), nullable=False)
