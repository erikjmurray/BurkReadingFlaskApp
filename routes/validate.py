""" Routes called by Javascript to validate whether the data already exists in the database or not """

from flask import Blueprint, jsonify
from models import Site, User


validate = Blueprint('validation', __name__)


@validate.route('site/<site_name>')
def validate_site_name(site_name):
    """ Given a site in the database return associated channels """
    site = Site.query.filter_by(site_name=site_name).first()
    if site:
        return jsonify({'exists': True, 'message': f'Site {site_name} already exists in database'}), 400
    else:
        return jsonify({'exists': False})


@validate.route('user/username/<username>')
def validate_username(username):
    """ Given a site in the database return associated channels """
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'exists': True, 'message': f'User {username} already exists in database'}), 400
    else:
        return jsonify({'exists': False})


@validate.route('user/name/<name>')
def validate_name(name):
    """ Given a site in the database return associated channels """
    user = User.query.filter_by(name=name).first()
    if user:
        return jsonify({'exists': True, 'message': f'User {name.replace("*", " ")} already exists in database'}), 400
    else:
        return jsonify({'exists': False})
