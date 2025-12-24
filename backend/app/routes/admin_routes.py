from flask import Blueprint, jsonify
from app.models import db, TripRequest

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/trip-requests', methods=['GET'])
def get_trip_requests():
    requests = TripRequest.query.all()
    return jsonify([
        {
            "id": r.id,
            "user_name": r.user_name,
            "contact_number": r.contact_number,
            "selected_destinations": r.selected_destinations,
            "travel_dates": r.travel_dates,
            "num_travelers": r.num_travelers,
            "budget_range": r.budget_range,
            "notes": r.notes,
            "status": r.status,
            "pdf_itinerary_url": r.pdf_itinerary_url
        }
        for r in requests
    ])
