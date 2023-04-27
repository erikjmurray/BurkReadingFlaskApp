"""
Web app to digitally sign and save Burk readings to database
"""
# ----- IMPORTS -----
import os
from dotenv import load_dotenv, set_key
from flask import Flask, redirect, render_template

from extensions import db, login_manager, ma
from models import *

env_file_path = os.path.join(os.getcwd(), 'instance\\.env')


def create_app(app_name) -> Flask:
    """ Creates Flask app with settings """
    app = Flask(app_name)

    # Setup files
    # setup_loggers(app)
    load_settings(app)
    register_blueprints(app)
    initialize_addons(app)

    # Creates SQL tables in db for any imported models
    with app.app_context():
        db.create_all()

    return app


def setup_loggers(app):
    """ Sets up logging """
    import logging
    from logging.handlers import RotatingFileHandler

    # Remove default handler
    from flask.logging import default_handler
    app.logger.removeHandler(default_handler)

    # Create a logger that only writes custom logs
    app_logger = logging.getLogger(__name__)
    file_handler = RotatingFileHandler(os.path.join('logs', 'app.log'), maxBytes=100000, backupCount=10)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    app_logger.addHandler(file_handler)

    # Create a log for Werkzeug data
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_handler = RotatingFileHandler(os.path.join('logs', 'werkzeug.log'), maxBytes=10000, backupCount=10)
    werkzeug_handler.setLevel(logging.DEBUG)
    werkzeug_logger.addHandler(werkzeug_handler)

    # Set the log level for Flask's app.logger and disable propagation to the root logger
    app.logger.setLevel(logging.DEBUG)
    app.logger.propagate = False

    # Add the app logger to the Flask app
    app.logger.addHandler(app_logger)
    return


def load_settings(app) -> None:
    """ Load app settings to app """
    # Load environment setup values
    load_dotenv(env_file_path)
    app.config.from_prefixed_env()

    if not app.config.get('SECRET_KEY'):
        add_secret_key(app)

    if not app.config.get('ENCRYPTION_KEY'):
        add_encryption_key(app)

    return


def add_secret_key(app) -> None:
    """ Adds secret key to .env if no value is present """
    import secrets
    # Generate a new random hex value for FLASK_SECRET_KEY
    app.config['SECRET_KEY'] = secrets.token_hex(16)
    update_env_file('FLASK_SECRET_KEY', app.config['SECRET_KEY'])
    return


def add_encryption_key(app) -> None:
    """
    Adds an encryption key to .env if no value is present.
    Uses Fernet cryptography to generate a new key.
    """
    from cryptography.fernet import Fernet
    # Generate a new encryption key using Fernet cryptography
    key = Fernet.generate_key()
    app.config['ENCRYPTION_KEY'] = key.decode()
    update_env_file('FLASK_ENCRYPTION_KEY', app.config['ENCRYPTION_KEY'])
    return


def update_env_file(key_name, value) -> None:
    """ Set key to value in .env """
    set_key(env_file_path, key_name, value)
    return


def register_blueprints(app) -> None:
    """ Loads blueprints to app, details what happens when visiting routes """
    from routes import views, admin, api, auth, eas, errors, tasks, validate
    app.register_blueprint(views, url_prefix='/')           # register routes laid out in routes.views
    app.register_blueprint(admin, url_prefix='/admin')      # register routes laid out in routes.admin with /admin
    app.register_blueprint(api, url_prefix='/api')          # register routes laid out in routes.api with /api
    app.register_blueprint(auth, url_prefix='/')            # register routes laid out in routes.auth
    app.register_blueprint(eas, url_prefix='/')            # register routes laid out in routes.auth
    app.register_blueprint(tasks, url_prefix='/tasks')      # register routes laid out in routes.tasks with /tasks
    app.register_blueprint(validate, url_prefix='/validate')#
    app.register_blueprint(errors, url_prefix='/')          # details error handling
    return


def initialize_addons(app) -> None:
    """ Register Flask add-ons with the app """
    db.init_app(app)
    login_manager.init_app(app)
    ma.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # In this example, the user ID is the user's email address
        user = User.query.get(user_id)
        return user

    return


if __name__ == "__main__":
    app = create_app('BurkFlaskApp')
    app.run()