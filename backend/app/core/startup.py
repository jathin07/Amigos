from flask import Flask
from app.core.config import config_by_name
from app.core.extensions import db, migrate, jwt, bcrypt
from app.core.logging import setup_logging
from app.core.error_handlers import register_error_handlers
from app.api.v1.health import health_bp
from app.workflow.engine import event_bus

def create_app(config_name="development"):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_by_name[config_name])
    
    # Initialize Logging
    setup_logging(app)
    
    # Register Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    
    # Register Error Handlers
    register_error_handlers(app)
    
    # Register Blueprints
    app.register_blueprint(health_bp, url_prefix="/api/v1/health")
    
    # Initialize Workflow Event Bus
    event_bus.initialize(app)
    
    return app
