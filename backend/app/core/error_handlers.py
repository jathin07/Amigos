from flask import jsonify
import logging
from app.domain.exceptions import ValidationException, DomainException, AuthorizationException, InfrastructureException

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(ValidationException)
    def handle_validation_error(e):
        return jsonify({
            "success": False,
            "data": None,
            "error": {
                "code": e.code,
                "message": e.message,
                "details": e.details
            },
            "validation_errors": e.validation_errors
        }), 400

    @app.errorhandler(DomainException)
    def handle_domain_error(e):
        return jsonify({
            "success": False,
            "data": None,
            "error": {
                "code": e.code,
                "message": e.message,
                "details": e.details
            },
            "validation_errors": []
        }), 409

    @app.errorhandler(AuthorizationException)
    def handle_authorization_error(e):
        logger.warning(f"Unauthorized access attempt: {e.message}")
        return jsonify({
            "success": False,
            "data": None,
            "error": {
                "code": e.code,
                "message": e.message,
                "details": e.details
            },
            "validation_errors": []
        }), 403

    @app.errorhandler(InfrastructureException)
    def handle_infrastructure_error(e):
        logger.error(f"Infrastructure Exception: {e.message}", exc_info=True)
        return jsonify({
            "success": False,
            "data": None,
            "error": {
                "code": e.code,
                "message": "An internal infrastructure error occurred.",
                "details": e.details
            },
            "validation_errors": []
        }), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "data": None,
            "error": {
                "code": "ERR_INTERNAL_SERVER",
                "message": "An unexpected error occurred.",
                "details": {}
            },
            "validation_errors": []
        }), 500
