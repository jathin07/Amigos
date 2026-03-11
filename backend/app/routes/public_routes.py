from flask import Blueprint, jsonify, request
from app.models import Destination, Package, Lead
from app import db

public_bp = Blueprint('public', __name__)


# -------------------------
# Health Check
# -------------------------
@public_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200


# -------------------------
# Get Destinations (Grouped by State)
# -------------------------
@public_bp.route('/destinations', methods=['GET'])
def get_destinations():

    destinations = Destination.query.order_by(Destination.state).all()

    grouped_data = {}

    for dest in destinations:

        if dest.state not in grouped_data:
            grouped_data[dest.state] = []

        grouped_data[dest.state].append({
            "name": dest.name,
            "image": f"/images/places/{dest.image_url}"
        })

    response = [
        {"state": state, "places": places}
        for state, places in grouped_data.items()
    ]

    return jsonify(response), 200


# -------------------------
# Get Packages
# -------------------------
@public_bp.route('/packages', methods=['GET'])
def get_packages():

    packages = Package.query.order_by(Package.id.desc()).all()

    result = []

    for pkg in packages:
        result.append({
            "id": pkg.id,
            "title": pkg.title,
            "description": pkg.description,
            "duration_days": pkg.duration_days,
            "duration_nights": pkg.duration_nights,
            "price_per_person": pkg.price_per_person,
            "thumbnail_url": pkg.thumbnail_url,
            "highlights": pkg.highlights
        })

    return jsonify(result), 200


# -------------------------
# Submit Lead (Plan My Trip / Package Booking)
# -------------------------
@public_bp.route('/lead', methods=['POST'])
def create_lead():

    data = request.get_json(silent=True) or {}

    name = (data.get('name') or '').strip()
    phone = (data.get('phone') or '').strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    if not phone:
        return jsonify({"error": "Phone number is required"}), 400

    new_lead = Lead(
        name=name,
        phone=phone,
        email=data.get("email"),
        lead_type=data.get("lead_type", "trip_request"),
        package_id=data.get("package_id"),
        travel_dates=data.get("travel_dates"),
        travelers=data.get("travelers"),
        budget=data.get("budget"),
        notes=data.get("notes"),
        status="pending"
    )

    try:
        db.session.add(new_lead)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Lead submitted successfully",
        "lead_id": new_lead.id
    }), 201