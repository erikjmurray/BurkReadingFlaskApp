""" Blueprint for Flask routes regarding login and authorization """

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from models import User

# create Flask blueprint
auth = Blueprint('auth', __name__)


# ----- LOGIN VERIFICATION -----
# TODO: Create admin login for config pages
@auth.route('/login')
def login():
    return render_template('admin/login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    """ Attempt to log in """
    def validate_username_pass(results) -> bool:
        return True
    # Gather form input
    results = request.form
    # TODO: Validate the user input before submission to config
    # validate_results(results)

    login_verification = validate_username_pass(results)

    if login_verification:
        return redirect(url_for('admin.home'))
    else:
        flash('Incorrect username or password')
        return redirect(url_for('auth.login'))


@auth.route('/logout')
def logout(user):
    session.pop(user)
    return 'You have been logged out'
