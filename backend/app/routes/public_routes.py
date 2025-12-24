from flask import Blueprint, jsonify, request
from app.models import TripRequest, Destination, QuickBooking
from app import db

public_bp = Blueprint('public', __name__)

@public_bp.route('/destinations', methods=['GET'])
def get_destinations():
    destinations = Destination.query.all()
    result = []
    for dest in destinations:
        result.append({
            'id': dest.id,
            'name': dest.name,
            'description': dest.description,
            'image_url': dest.image_url,
            'tags': dest.tags
        })
    return jsonify(result)

@public_bp.route('/plan-trip', methods=['POST'])
def plan_trip():
    data = request.get_json()

    new_request = TripRequest(
        user_name=data.get('name'),
        contact_number=data.get('phone'),
        email=data.get('email'),
        selected_destinations=data.get('destination'),
        travel_dates=data.get('travelDate'),
        num_travelers=data.get('travelers'),
        budget_range=data.get('budget'),
        notes=data.get('notes'),
    )

    db.session.add(new_request)
    db.session.commit()

    return jsonify({
        "message": "Trip request submitted successfully!",
        "request_id": new_request.id
    }), 201


# Quick Booking - Create
@public_bp.route("/quick-booking", methods=["POST"])
def create_quick_booking():
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get("user_name") or not data.get("contact_number"):
            return jsonify({"error": "Name and contact number are required"}), 400

        new_booking = QuickBooking(
            user_name=data.get("user_name"),
            contact_number=data.get("contact_number"),
            email=data.get("email"),
            preferred_destinations=data.get("preferred_destinations"),
            notes=data.get("notes"),
            status="pending"
        )

        db.session.add(new_booking)
        db.session.commit()

        return jsonify({
            "message": "Quick booking request submitted successfully",
            "booking_id": new_booking.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500