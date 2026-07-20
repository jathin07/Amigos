from flask import Blueprint, jsonify, current_app
from app.core.extensions import db
from sqlalchemy import text

health_bp = Blueprint('health', __name__)

@health_bp.route('', methods=['GET'])
def health_check():
    db_status = "connected"
    try:
        db.session.execute(text('SELECT 1'))
    except Exception as e:
        db_status = f"error: {str(e)}"

    env = "development"
    if current_app.config.get("TESTING"):
        env = "testing"
    elif not current_app.config.get("DEBUG"):
        env = "production"

    return jsonify({
        "success": True,
        "data": {
            "status": "healthy",
            "version": "v1",
            "environment": env,
            "database": db_status
        },
        "error": None,
        "validation_errors": []
    }), 200
