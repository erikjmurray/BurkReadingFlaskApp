""" Details routes for error messaging """
# ----- 3RD PARTY IMPORTS -----
from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user


# Initialize Blueprint
errors = Blueprint('errors', __name__)


# Handles unauthorized error
@errors.app_errorhandler(401)
def unauthorized_error(e):
    """ Redirect on 401 Error """
    # current_app.logger.warning(e)
    flash('You must be logged in to view this page')
    return redirect(url_for('auth.login'))


# Handles permissions error
@errors.app_errorhandler(403)
def forbidden_error(e):
    """ Redirect on 403 Error """
    current_app.logger.warning(f"{current_user.name} attempted to access Admin page")
    return redirect(url_for('errors.forbidden'))


@errors.route('/forbidden')
def forbidden():
    """ Custom 403 page """
    return render_template('errors/forbidden.html')


# Handles page not found errors
@errors.app_errorhandler(404)
def page_not_found(e):
    """ On 404 not found error, route to custom 404 page """
    current_app.logger.warning(e)
    return redirect(url_for('errors.not_found'))


@errors.route('/not_found')
def not_found():
    """ Return an internal page for 404 """
    return render_template('/errors/not_found.html')
