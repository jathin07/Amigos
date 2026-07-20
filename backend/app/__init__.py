import os
import logging

from flask import Flask, request
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

db = SQLAlchemy()
migrate = Migrate()
cache = Cache()


def create_app():
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    app = Flask(__name__, instance_relative_config=True)

    # Instance config is expected for local development.
    app.config.from_pyfile('config.py', silent=True)

    app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///amigos.db')
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    # Enable SQL query logging
    app.config.setdefault('SQLALCHEMY_ECHO', True)
    
    app.config.setdefault('SECRET_KEY', os.environ.get('SECRET_KEY', 'dev-secret-key'))
    app.config.setdefault('CACHE_TYPE', 'SimpleCache')
    app.config.setdefault('CACHE_DEFAULT_TIMEOUT', 1800)

    frontend_origin = app.config.get('FRONTEND_ORIGIN', '*')

    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    CORS(app, resources={r'/*': {'origins': frontend_origin}})

    from .routes.public_routes import public_bp
    from .routes.admin_routes import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from .exceptions import APIException
    from flask import jsonify
    from werkzeug.exceptions import HTTPException

    @app.before_request
    def log_request_info():
        app.logger.info('Headers: %s', request.headers)
        app.logger.info('Body: %s', request.get_data())

    @app.errorhandler(APIException)
    def handle_api_exception(error):
        app.logger.error(f'APIException: {error.to_dict()}')
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        app.logger.error(f'HTTPException: {error.description}')
        return jsonify({"error": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        app.logger.exception('An unexpected error occurred:')
        return jsonify({"error": "An unexpected error occurred."}), 500

    return app

