
from flask import Blueprint, redirect, render_template, url_for


errors = Blueprint('errors', __name__)


@errors.app_errorhandler(401)
def unauthorized_error(e):
    """ Redirect on 401 Error """
    return redirect(url_for('errors.unauthorized'))


@errors.route('/unauthorized')
def unauthorized():
    """ Custom 401 page """
    return render_template('errors/unauthorized.html')


@errors.app_errorhandler(403)
def forbidden_error(e):
    """ Redirect on 403 Error """
    return redirect(url_for('errors.forbidden'))


@errors.route('/forbidden')
def forbidden():
    """ Custom 403 page """
    return render_template('errors/forbidden.html')


# Handle 404 errors
@errors.app_errorhandler(404)
def page_not_found(e):
    """ On 404 not found error, route to custom 404 page """
    # current_app.logger.warning(e)
    return redirect(url_for('errors.not_found'))


@errors.route('/not_found')
def not_found():
    """ Return an internal page for 404 """
    return render_template('/errors/not_found.html')

