
from flask import current_app, Blueprint, redirect, render_template


errors = Blueprint('errors', __name__)


# Handle 404 errors
@errors.app_errorhandler(404)
def page_not_found(e):
    """ On 404 not found error, route to custom 404 page """
    # current_app.logger.warning(e)
    return redirect('/not_found')


@errors.route('/not_found')
def not_found():
    """ Return an internal page for 404 """
    return render_template('not_found.html')

