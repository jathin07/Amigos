from flask import Flask

from app.api.v1.health import health_bp
from app.core.config import config_by_name
from app.core.error_handlers import register_error_handlers
from app.core.extensions import bcrypt, db, jwt, migrate, cache
from app.core.logging import setup_logging
from app.modules.auth.routes import auth_bp
from app.workflow.engine import event_bus


def create_app(config_name: str = "development") -> Flask:
    """
    Flask Application Factory.
    """

    app = Flask(__name__)

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------
    app.config.from_object(config_by_name[config_name])

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    setup_logging(app)

    # ------------------------------------------------------------------
    # Extensions
    # ------------------------------------------------------------------
    register_extensions(app)

    # ------------------------------------------------------------------
    # Error Handlers
    # ------------------------------------------------------------------
    register_error_handlers(app)

    # ------------------------------------------------------------------
    # Blueprints
    # ------------------------------------------------------------------
    register_blueprints(app)

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------
    event_bus.initialize(app)

    app.logger.info("Application initialized successfully.")

    return app


def register_extensions(app: Flask) -> None:
    """Initialize Flask extensions."""

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cache.init_app(app)

    # Initialize CORS for api endpoints
    from flask_cors import CORS
    frontend_origin = app.config.get("FRONTEND_ORIGIN", "*")
    CORS(app, resources={r"/*": {"origins": frontend_origin}})


def register_blueprints(app: Flask) -> None:
    """Register API blueprints."""

    app.register_blueprint(
        health_bp,
        url_prefix="/api/v1/health",
    )

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/v1/auth",
    )

    from app.modules.master.country import country_bp
    app.register_blueprint(country_bp)

    from app.modules.master.state import state_bp
    app.register_blueprint(state_bp)

    from app.modules.master.district import district_bp
    app.register_blueprint(district_bp)

    from app.modules.master.destination import destination_bp
    app.register_blueprint(destination_bp)

    from app.modules.master.city import city_bp
    app.register_blueprint(city_bp)

    from app.modules.master import catalog_bp
    app.register_blueprint(catalog_bp)

    from app.modules.organization import organization_bp
    app.register_blueprint(
        organization_bp,
        url_prefix="/api/v1/organization",
    )

    from app.modules.team import team_bp
    app.register_blueprint(
        team_bp,
        url_prefix="/api/v1/team-members",
    )

    from app.modules.vendor import vendor_bp
    app.register_blueprint(
        vendor_bp,
        url_prefix="/api/v1/vendors",
    )

    from app.modules.package import package_bp
    app.register_blueprint(
        package_bp,
        url_prefix="/api/v1/packages",
    )

    from app.modules.crm import crm_bp
    app.register_blueprint(
        crm_bp,
        url_prefix="/api/v1",
    )

    from app.modules.proposal import proposal_bp
    app.register_blueprint(
        proposal_bp,
        url_prefix="/api/v1",
    )

    from app.modules.booking import booking_bp
    app.register_blueprint(
        booking_bp,
        url_prefix="/api/v1",
    )

    from app.modules.operations import operations_bp
    app.register_blueprint(
        operations_bp,
        url_prefix="/api/v1/operations",
    )

    from app.modules.finance import finance_bp
    app.register_blueprint(
        finance_bp,
        url_prefix="/api/v1/finance",
    )

    from app.modules.storage import storage_bp
    app.register_blueprint(
        storage_bp,
        url_prefix="/api/v1/storage",
    )

    from app.modules.dashboard import dashboard_bp
    app.register_blueprint(
        dashboard_bp,
        url_prefix="/api/v1/dashboard",
    )

    from app.modules.reports import reports_bp
    app.register_blueprint(
        reports_bp,
        url_prefix="/api/v1/reports",
    )

    from app.routes.public_routes import public_bp
    app.register_blueprint(public_bp)