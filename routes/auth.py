""" Blueprint for Flask routes regarding login and authorization """
# ----- 3RD PARTY IMPORTS -----
from flask import Blueprint, flash, jsonify, redirect, render_template, request, Response, url_for
from flask_login import current_user, login_user, logout_user, login_required
from marshmallow import ValidationError
from werkzeug.security import check_password_hash
# ----- PROJECT IMPORTS -----
from extensions import db
from models import Site, User
from models.schemas import UserCreationSchema

# create Flask blueprint
auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    if current_user.is_authenticated:
        flash('Log out before trying to log in')
        return redirect(url_for('views.index'))
    return render_template('auth/login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    form_data = request.form
    error_message = 'Sorry, we were unable to log you in. The username and password \
        you provided did not match our records. Please check your login details and try again.\
         If you continue to experience issues, please contact our support team for assistance.'
    username = form_data.get('username')
    user = User.query.filter_by(username=username).first()

    if not user:
        flash(error_message)
        return redirect(url_for('auth.login'))

    if check_password_hash(user.password, form_data.get('password')):
        login_user(user)
        return redirect(url_for('views.index'))
    else:
        flash(error_message)
        return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out!')
    return redirect(url_for('auth.login'))


@auth.route('/signup')
def signup():
    return render_template('auth/signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    form_data = request.form

    try:
        add_user_schema = UserCreationSchema()              # password hashed in creation
        new_user = add_user_schema.load_user(form_data)

        db.session.add(new_user)
        db.session.commit()
    except ValidationError as err:
        error_messages = err.messages
        db.session.rollback()
        flash('Something went wrong trying to post new user')
        return render_template('auth/signup.html', error_messages=error_messages)
    flash('User added!')
    return redirect(url_for('auth.login'))


@auth.route("/check_username")
def check_username() -> Response:
    username = request.args.get("username")
    current_username = request.args.get('current_username')

    # if updating, don't raise error on existing username
    if username == current_username:
        return jsonify({'exists': False})

    # check if username exists, raise error
    user = User.query.filter_by(username=username).first()
    if user:
        jsonify({'exists': True, 'message': f'Username {username} already exists in database'}), 400
    else:
        return jsonify({"exists": False})


@auth.route('/check_site_name')
def check_site_name() -> Response:
    """ Given a site in the database return associated channels """
    site_name = request.args.get('site_name').replace(' ', '_')
    current_site_name = request.args.get('current_site_name').replace(' ', '_')

    # if updating, don't raise error on existing site_name
    if site_name == current_site_name:
        return jsonify({'exists': False})

    # if site name exists, raise error
    site = Site.query.filter_by(site_name=site_name).first()
    if site:
        return jsonify({'exists': True, 'message': f'Site {site_name} already exists in database'}), 400
    else:
        return jsonify({'exists': False})

