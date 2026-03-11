from functools import wraps
from flask import Blueprint, current_app, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app import db
from app.models import Package, Lead, TeamMember, TripFinance

admin_bp = Blueprint("admin", __name__)

TOKEN_MAX_AGE_SECONDS = 60 * 60 * 8  # 8 hours


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def _make_token(admin_email: str):
    return _serializer().dumps({"email": admin_email}, salt="admin-auth")


def _verify_token(token: str):
    return _serializer().loads(
        token,
        salt="admin-auth",
        max_age=TOKEN_MAX_AGE_SECONDS,
    )


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split(" ", 1)
        token = parts[1].strip() if len(parts) == 2 else ""

        if not token:
            return jsonify({"error": "Missing admin token"}), 401

        try:
            _verify_token(token)
        except SignatureExpired:
            return jsonify({"error": "Token expired"}), 401
        except BadSignature:
            return jsonify({"error": "Invalid token"}), 401

        return view_func(*args, **kwargs)

    return wrapper


# -------------------------
# Admin Login
# -------------------------
@admin_bp.route("/login", methods=["POST"])
def admin_login():

    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    admin_email = current_app.config.get("ADMIN_EMAIL")
    admin_password = current_app.config.get("ADMIN_PASSWORD")

    if email == admin_email and password == admin_password:

        token = _make_token(email)

        return jsonify({
            "message": "Login successful",
            "token": token
        })

    return jsonify({"error": "Invalid credentials"}), 401


# -------------------------
# Get Leads
# -------------------------
@admin_bp.route("/leads", methods=["GET"])
@admin_required
def get_leads():

    leads = Lead.query.order_by(Lead.id.desc()).all()

    result = []

    for lead in leads:
        result.append({
            "id": lead.id,
            "name": lead.name,
            "phone": lead.phone,
            "email": lead.email,
            "lead_type": lead.lead_type,
            "package_id": lead.package_id,
            "travel_dates": lead.travel_dates,
            "travelers": lead.travelers,
            "budget": lead.budget,
            "status": lead.status
        })

    return jsonify(result)


# -------------------------
# Update Lead Status
# -------------------------
@admin_bp.route("/lead/<int:lead_id>", methods=["PATCH"])
@admin_required
def update_lead_status(lead_id):

    lead = Lead.query.get_or_404(lead_id)

    data = request.get_json()

    lead.status = data.get("status", lead.status)

    db.session.commit()

    return jsonify({"message": "Lead updated"})


# -------------------------
# Create Package
# -------------------------
@admin_bp.route("/packages", methods=["POST"])
@admin_required
def create_package():

    data = request.get_json()

    pkg = Package(
        title=data.get("title"),
        description=data.get("description"),
        duration_days=data.get("duration_days"),
        duration_nights=data.get("duration_nights"),
        price_per_person=data.get("price_per_person"),
        thumbnail_url=data.get("thumbnail_url"),
        highlights=data.get("highlights")
    )

    db.session.add(pkg)
    db.session.commit()

    return jsonify({"message": "Package created"}), 201


# -------------------------
# Finance Entry
# -------------------------
@admin_bp.route("/finance", methods=["POST"])
@admin_required
def add_finance():

    data = request.get_json()

    revenue = float(data.get("revenue", 0))
    transport = float(data.get("transport_cost", 0))
    hotel = float(data.get("hotel_cost", 0))
    food = float(data.get("food_cost", 0))
    activity = float(data.get("activity_cost", 0))
    other = float(data.get("other_cost", 0))

    total_cost = transport + hotel + food + activity + other
    profit = revenue - total_cost

    finance = TripFinance(
        lead_id=data.get("lead_id"),
        revenue=revenue,
        transport_cost=transport,
        hotel_cost=hotel,
        food_cost=food,
        activity_cost=activity,
        other_cost=other,
        total_cost=total_cost,
        profit=profit
    )

    db.session.add(finance)
    db.session.commit()

    return jsonify({"message": "Finance record added"})