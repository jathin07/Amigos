from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

import os

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Explicit path to instance/config.py
    app.config.from_pyfile(os.path.join(app.instance_path, 'config.py'))
    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)  # ✅ proper place
    CORS(app)

    # Register Blueprints
    from .routes.public_routes import public_bp
    from .routes.admin_routes import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app
