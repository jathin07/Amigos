from datetime import datetime
from functools import wraps
from flask import Blueprint, current_app, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from marshmallow import ValidationError
from app.exceptions import ValidationException, Unauthorized

from app import db
from app.models import Package, Lead, TeamMember, TripFinance, PackageDestination, Destination, Task, Customer
from app.schemas import PackageSchema, TripFinanceSchema, TaskSchema, CustomerSchema

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
            raise Unauthorized("Missing admin token")

        try:
            _verify_token(token)
        except SignatureExpired:
            raise Unauthorized("Token expired")
        except BadSignature:
            raise Unauthorized("Invalid token")

        return view_func(*args, **kwargs)

    return wrapper


# -------------------------
# Admin Login
# -------------------------
@admin_bp.route("/login", methods=["POST"])
def admin_login():
    from app.models import Admin

    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    admin = Admin.query.filter_by(email=email).first()

    if admin and admin.check_password(password):

        token = _make_token(email)

        return jsonify({
            "message": "Login successful",
            "token": token
        })

    raise Unauthorized("Invalid credentials")


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
            "status": lead.status,
            "contact_person_id": lead.contact_person_id
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
    if "contact_person_id" in data:
        lead.contact_person_id = data.get("contact_person_id")

    db.session.commit()

    return jsonify({"message": "Lead updated"})


# -------------------------
# Convert Lead to Booking
# -------------------------
@admin_bp.route("/lead/<int:lead_id>/convert", methods=["POST"])
@admin_required
def convert_lead_to_booking(lead_id):
    from app.models import Customer, Booking, Task
    from datetime import datetime

    lead = Lead.query.get_or_404(lead_id)

    if lead.status == "confirmed":
        raise ValidationException("Lead is already confirmed")

    data = request.get_json() or {}

    # Check for existing Customer
    customer = None
    if lead.email or lead.phone:
        query = Customer.query
        if lead.email and lead.phone:
            customer = query.filter(db.or_(Customer.email == lead.email, Customer.phone == lead.phone)).first()
        elif lead.email:
            customer = query.filter_by(email=lead.email).first()
        else:
            customer = query.filter_by(phone=lead.phone).first()

    if not customer:
        customer = Customer(
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            address=data.get("address", ""),
            preferences=lead.notes
        )
        db.session.add(customer)
        db.session.flush() # To get customer.id

    # Parse Dates
    start_date_str = data.get("start_date")
    end_date_str = data.get("end_date")
    start_date = None
    end_date = None
    
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        except ValueError:
            pass
            
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            pass

    # Create Booking
    booking = Booking(
        lead_id=lead.id,
        customer_id=customer.id,
        package_id=lead.package_id,
        total_price=data.get("total_price", 0),
        start_date=start_date,
        end_date=end_date,
        status="confirmed"
    )
    db.session.add(booking)

    # Auto-generate a "Review Itinerary" task
    task = Task(
        linked_lead_id=lead.id,
        description="Review Itinerary for newly confirmed booking",
        status="pending"
    )
    db.session.add(task)

    # Update Lead Status
    lead.status = "confirmed"

    db.session.commit()

    return jsonify({
        "message": "Lead converted to booking successfully",
        "customer_id": customer.id,
        "booking_id": booking.id
    })


# -------------------------
# Get Packages
# -------------------------
@admin_bp.route("/packages", methods=["GET"])
@admin_required
def get_packages():
    packages = Package.query.order_by(Package.id.desc()).all()
    result = []
    for pkg in packages:
        destinations = [pd.destination_id for pd in pkg.destinations]
        result.append({
            "id": pkg.id,
            "title": pkg.title,
            "description": pkg.description,
            "duration_days": pkg.duration_days,
            "duration_nights": pkg.duration_nights,
            "price_per_person": pkg.price_per_person,
            "thumbnail_url": pkg.thumbnail_url,
            "highlights": pkg.highlights,
            "destination_ids": destinations
        })
    return jsonify(result)


# -------------------------
# Create Package
# -------------------------
@admin_bp.route("/packages", methods=["POST"])
@admin_required
def create_package():

    data = request.get_json()

    try:
        validated_data = PackageSchema().load(data)
    except ValidationError as err:
        raise ValidationException("Validation failed", payload=err.messages)

    pkg = Package(
        title=validated_data.get("title"),
        description=validated_data.get("description"),
        duration_days=validated_data.get("duration_days"),
        duration_nights=validated_data.get("duration_nights"),
        price_per_person=validated_data.get("price_per_person"),
        thumbnail_url=validated_data.get("thumbnail_url"),
        highlights=validated_data.get("highlights")
    )

    db.session.add(pkg)
    db.session.flush()

    destination_ids = validated_data.get("destination_ids", [])
    for dest_id in destination_ids:
        pkg_dest = PackageDestination(package_id=pkg.id, destination_id=dest_id)
        db.session.add(pkg_dest)

    db.session.commit()

    return jsonify({"message": "Package created", "id": pkg.id}), 201


# -------------------------
# Update Package
# -------------------------
@admin_bp.route("/packages/<int:package_id>", methods=["PUT"])
@admin_required
def update_package(package_id):
    pkg = Package.query.get_or_404(package_id)
    data = request.get_json()

    try:
        validated_data = PackageSchema().load(data)
    except ValidationError as err:
        raise ValidationException("Validation failed", payload=err.messages)

    pkg.title = validated_data.get("title", pkg.title)
    pkg.description = validated_data.get("description", pkg.description)
    pkg.duration_days = validated_data.get("duration_days", pkg.duration_days)
    pkg.duration_nights = validated_data.get("duration_nights", pkg.duration_nights)
    pkg.price_per_person = validated_data.get("price_per_person", pkg.price_per_person)
    pkg.thumbnail_url = validated_data.get("thumbnail_url", pkg.thumbnail_url)
    pkg.highlights = validated_data.get("highlights", pkg.highlights)

    if validated_data.get("destination_ids") is not None:
        PackageDestination.query.filter_by(package_id=pkg.id).delete()
        for dest_id in validated_data["destination_ids"]:
            pkg_dest = PackageDestination(package_id=pkg.id, destination_id=dest_id)
            db.session.add(pkg_dest)

    db.session.commit()
    return jsonify({"message": "Package updated"})


# -------------------------
# Delete Package
# -------------------------
@admin_bp.route("/packages/<int:package_id>", methods=["DELETE"])
@admin_required
def delete_package(package_id):
    pkg = Package.query.get_or_404(package_id)
    PackageDestination.query.filter_by(package_id=pkg.id).delete()
    db.session.delete(pkg)
    db.session.commit()
    return jsonify({"message": "Package deleted"})


# -------------------------
# Get Destinations
# -------------------------
@admin_bp.route("/destinations", methods=["GET"])
@admin_required
def get_destinations():
    destinations = Destination.query.order_by(Destination.id.desc()).all()
    result = []
    for d in destinations:
        result.append({
            "id": d.id,
            "name": d.name,
            "state": d.state,
            "description": d.description,
            "image_url": d.image_url,
            "tags": d.tags
        })
    return jsonify(result)


# -------------------------
# Create Destination
# -------------------------
@admin_bp.route("/destinations", methods=["POST"])
@admin_required
def create_destination():
    data = request.get_json()
    dest = Destination(
        name=data.get("name"),
        state=data.get("state"),
        description=data.get("description"),
        image_url=data.get("image_url"),
        tags=data.get("tags")
    )
    db.session.add(dest)
    db.session.commit()
    return jsonify({"message": "Destination created", "id": dest.id}), 201


# -------------------------
# Update Destination
# -------------------------
@admin_bp.route("/destinations/<int:dest_id>", methods=["PUT"])
@admin_required
def update_destination(dest_id):
    dest = Destination.query.get_or_404(dest_id)
    data = request.get_json()
    dest.name = data.get("name", dest.name)
    dest.state = data.get("state", dest.state)
    dest.description = data.get("description", dest.description)
    dest.image_url = data.get("image_url", dest.image_url)
    dest.tags = data.get("tags", dest.tags)
    db.session.commit()
    return jsonify({"message": "Destination updated"})


# -------------------------
# Delete Destination
# -------------------------
@admin_bp.route("/destinations/<int:dest_id>", methods=["DELETE"])
@admin_required
def delete_destination(dest_id):
    dest = Destination.query.get_or_404(dest_id)
    db.session.delete(dest)
    db.session.commit()
    return jsonify({"message": "Destination deleted"})


# -------------------------
# Get Team Members
# -------------------------
@admin_bp.route("/team-members", methods=["GET"])
@admin_required
def get_team_members():
    members = TeamMember.query.order_by(TeamMember.id.desc()).all()
    result = []
    for m in members:
        result.append({
            "id": m.id,
            "name": m.name,
            "role": m.role,
            "phone": m.phone,
            "active": m.active
        })
    return jsonify(result)


# -------------------------
# Create Team Member
# -------------------------
@admin_bp.route("/team-members", methods=["POST"])
@admin_required
def create_team_member():
    data = request.get_json()
    member = TeamMember(
        name=data.get("name"),
        role=data.get("role"),
        phone=data.get("phone"),
        active=data.get("active", True)
    )
    db.session.add(member)
    db.session.commit()
    return jsonify({"message": "Team member created", "id": member.id}), 201


# -------------------------
# Update Team Member
# -------------------------
@admin_bp.route("/team-members/<int:member_id>", methods=["PUT"])
@admin_required
def update_team_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    data = request.get_json()
    member.name = data.get("name", member.name)
    member.role = data.get("role", member.role)
    member.phone = data.get("phone", member.phone)
    if "active" in data:
        member.active = data.get("active")
    db.session.commit()
    return jsonify({"message": "Team member updated"})


# -------------------------
# Delete Team Member
# -------------------------
@admin_bp.route("/team-members/<int:member_id>", methods=["DELETE"])
@admin_required
def delete_team_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Team member deleted"})



# -------------------------
# Finance Entry
# -------------------------
@admin_bp.route("/finance", methods=["GET"])
@admin_required
def get_finances():
    finances = TripFinance.query.order_by(TripFinance.id.desc()).all()
    result = []
    for f in finances:
        lead = Lead.query.get(f.lead_id)
        result.append({
            "id": f.id,
            "lead_id": f.lead_id,
            "lead_name": lead.name if lead else "Unknown",
            "revenue": f.revenue,
            "transport_cost": f.transport_cost,
            "hotel_cost": f.hotel_cost,
            "food_cost": f.food_cost,
            "activity_cost": f.activity_cost,
            "other_cost": f.other_cost,
            "total_cost": f.total_cost,
            "profit": f.profit,
            "created_at": f.created_at.isoformat() if f.created_at else None
        })
    return jsonify(result)

@admin_bp.route("/finance", methods=["POST"])
@admin_required
def add_finance():
    data = request.get_json()

    try:
        validated_data = TripFinanceSchema().load(data)
    except ValidationError as err:
        raise ValidationException("Validation failed", payload=err.messages)

    revenue = float(validated_data.get("revenue", 0))
    transport = float(validated_data.get("transport_cost", 0))
    hotel = float(validated_data.get("hotel_cost", 0))
    food = float(validated_data.get("food_cost", 0))
    activity = float(validated_data.get("activity_cost", 0))
    other = float(validated_data.get("other_cost", 0))

    total_cost = transport + hotel + food + activity + other
    profit = revenue - total_cost

    finance = TripFinance(
        lead_id=validated_data.get("lead_id"),
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

    return jsonify({"message": "Finance record added", "id": finance.id})

@admin_bp.route("/finance/<int:id>", methods=["PUT"])
@admin_required
def update_finance(id):
    finance = TripFinance.query.get_or_404(id)
    data = request.get_json()

    try:
        validated_data = TripFinanceSchema().load(data, partial=True)
    except ValidationError as err:
        raise ValidationException("Validation failed", payload=err.messages)

    finance.revenue = float(validated_data.get("revenue", finance.revenue))
    finance.transport_cost = float(validated_data.get("transport_cost", finance.transport_cost))
    finance.hotel_cost = float(validated_data.get("hotel_cost", finance.hotel_cost))
    finance.food_cost = float(validated_data.get("food_cost", finance.food_cost))
    finance.activity_cost = float(validated_data.get("activity_cost", finance.activity_cost))
    finance.other_cost = float(validated_data.get("other_cost", finance.other_cost))

    finance.total_cost = (finance.transport_cost + finance.hotel_cost + 
                          finance.food_cost + finance.activity_cost + finance.other_cost)
    finance.profit = finance.revenue - finance.total_cost
    
    if "lead_id" in validated_data:
        finance.lead_id = validated_data.get("lead_id")

    db.session.commit()

    return jsonify({"message": "Finance record updated"})

@admin_bp.route("/finance/<int:id>", methods=["DELETE"])
@admin_required
def delete_finance(id):
    finance = TripFinance.query.get_or_404(id)
    db.session.delete(finance)
    db.session.commit()
    return jsonify({"message": "Finance record deleted"})


# -------------------------
# Task Management Engine
# -------------------------
@admin_bp.route("/tasks", methods=["GET"])
@admin_required
def get_tasks():
    tasks = Task.query.order_by(Task.id.desc()).all()
    result = []
    for task in tasks:
        result.append({
            "id": task.id,
            "assigned_to_id": task.assigned_to_id,
            "linked_lead_id": task.linked_lead_id,
            "description": task.description,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "status": task.status,
            "created_at": task.created_at.isoformat() if task.created_at else None
        })
    return jsonify(result)


@admin_bp.route("/tasks", methods=["POST"])
@admin_required
def create_task():
    from datetime import datetime
    data = request.get_json()

    try:
        validated_data = TaskSchema().load(data)
    except ValidationError as err:
        raise ValidationException("Validation failed", payload=err.messages)

    # Parse due_date string to datetime
    due_date = None
    due_date_str = validated_data.get("due_date")
    if due_date_str:
        for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                due_date = datetime.strptime(due_date_str, fmt)
                break
            except ValueError:
                continue

    task = Task(
        assigned_to_id=validated_data.get("assigned_to_id"),
        linked_lead_id=validated_data.get("linked_lead_id"),
        description=validated_data.get("description"),
        due_date=due_date,
        status=validated_data.get("status", "pending")
    )
    db.session.add(task)
    db.session.commit()

    return jsonify({"message": "Task created", "id": task.id}), 201


@admin_bp.route("/tasks/<int:id>", methods=["PUT", "PATCH"])
@admin_required
def update_task(id):
    from datetime import datetime
    task = Task.query.get_or_404(id)
    data = request.get_json()

    try:
        validated_data = TaskSchema().load(data, partial=True)
    except ValidationError as err:
        raise ValidationException("Validation failed", payload=err.messages)

    task.assigned_to_id = validated_data.get("assigned_to_id", task.assigned_to_id)
    task.linked_lead_id = validated_data.get("linked_lead_id", task.linked_lead_id)
    task.description = validated_data.get("description", task.description)
    task.status = validated_data.get("status", task.status)

    # Parse due_date string to datetime if provided
    if "due_date" in validated_data:
        due_date_str = validated_data["due_date"]
        if due_date_str:
            for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                try:
                    task.due_date = datetime.strptime(due_date_str, fmt)
                    break
                except ValueError:
                    continue
        else:
            task.due_date = None

    db.session.commit()
    return jsonify({"message": "Task updated"})


@admin_bp.route("/tasks/<int:id>", methods=["DELETE"])
@admin_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"})