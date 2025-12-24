from flask import Blueprint, request, jsonify
from flask import current_app

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    # Fetch admin creds from config
    admin_email = current_app.config.get("ADMIN_EMAIL")
    admin_password = current_app.config.get("ADMIN_PASSWORD")

    if email == admin_email and password == admin_password:
        return jsonify({
            "message": "Admin login successful"
        }), 200

    return jsonify({
        "message": "Invalid admin credentials"
    }), 401
