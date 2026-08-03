from flask import jsonify
import logging
from app.domain.exceptions import ValidationException, DomainException, AuthorizationException, InfrastructureException, AuthenticationException, NotFoundException, BusinessException

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(BusinessException)
    def handle_business_error(e):
        return jsonify({
            "success": False,
            "data": None,
            "code": e.code,
            "error": {
                "code": e.code,
                "message": e.message,
                "details": e.details
            },
            "validation_errors": []
        }), 409
    @app.errorhandler(NotFoundException)
    def handle_not_found_error(e):
        return jsonify({
            "success": False,
            "data": None,
            "code": e.code,
            "error": {
                "code": e.code,
                "message": e.message,
                "details": e.details
            },
            "validation_errors": []
        }), 404

    @app.errorhandler(ValidationException)
    def handle_validation_error(e):
        return jsonify({
            "success": False,
            "data": None,
            "code": e.code,
            "error": {
                "code": e.code,
                "message": e.message,
                "details": e.details
            },
            "validation_errors": e.validation_errors
        }), 400

    @app.errorhandler(DomainException)
    def handle_domain_error(e):
        code = "ERR_OPTIMISTIC_LOCK" if e.code == "ERR_CONCURRENT_MODIFICATION" else e.code
        return jsonify({
            "success": False,
            "data": None,
            "code": code,
            "error": {
                "code": code,
                "message": e.message,
                "details": e.details
            },
            "validation_errors": []
        }), 409

    @app.errorhandler(AuthenticationException)
    def handle_authentication_error(e):
        logger.warning("Authentication failed: %s", e.message)
        return jsonify({
            "success": False,
            "data": None,
            "error": {
                "code": e.code,
                "message": e.message,
                "details": e.details
            },
            "validation_errors": []
        }), 401

    @app.errorhandler(AuthorizationException)
    def handle_authorization_error(e):
        logger.warning("Unauthorized access attempt: %s", e.message)
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
        logger.error("Infrastructure Exception: %s", e.message, exc_info=True)
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
        logger.error("Unexpected error: %s", str(e), exc_info=True)
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
