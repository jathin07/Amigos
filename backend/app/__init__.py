import os

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Instance config is expected for local development.
    app.config.from_pyfile('config.py', silent=True)

    app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///amigos.db')
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    app.config.setdefault('SECRET_KEY', os.environ.get('SECRET_KEY', 'dev-secret-key'))

    frontend_origin = app.config.get('FRONTEND_ORIGIN', '*')

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r'/*': {'origins': frontend_origin}})

    from .routes.public_routes import public_bp
    from .routes.admin_routes import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
