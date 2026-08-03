from datetime import datetime
from functools import wraps
from flask import Blueprint, current_app, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from marshmallow import ValidationError
from app.exceptions import ValidationException, Unauthorized

from app import db
from app.models import Lead, TeamMember, Destination, Task, Customer
from app.schemas import DummyModelSchema, TaskSchema, CustomerSchema

admin_bp = Blueprint("admin", __name__)

from app.modules.auth.permissions import role_required


# -------------------------
# CRM CRUD routes migrated to app/modules/crm/
# -------------------------


# Package CRUD routes migrated to app/modules/package/ (registered at /api/v1/packages)


# -------------------------
# Get Destinations
# -------------------------
@admin_bp.route("/destinations", methods=["GET"])
@role_required("Admin")
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
@role_required("Admin")
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
@role_required("Admin")
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
@role_required("Admin")
def delete_destination(dest_id):
    dest = Destination.query.get_or_404(dest_id)
    db.session.delete(dest)
    db.session.commit()
    return jsonify({"message": "Destination deleted"})






# -------------------------
# Finance Entry
# -------------------------
@admin_bp.route("/finance", methods=["GET"])
@role_required("Admin")
def get_finances():
    finances = DummyModel.query.order_by(DummyModel.id.desc()).all()
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
@role_required("Admin")
def add_finance():
    data = request.get_json()

    try:
        validated_data = DummyModelSchema().load(data)
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

    finance = DummyModel(
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
@role_required("Admin")
def update_finance(id):
    finance = DummyModel.query.get_or_404(id)
    data = request.get_json()

    try:
        validated_data = DummyModelSchema().load(data, partial=True)
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
@role_required("Admin")
def delete_finance(id):
    finance = DummyModel.query.get_or_404(id)
    db.session.delete(finance)
    db.session.commit()
    return jsonify({"message": "Finance record deleted"})


# -------------------------
# Task Management Engine
# -------------------------
@admin_bp.route("/tasks", methods=["GET"])
@role_required("Admin")
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
@role_required("Admin")
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
@role_required("Admin")
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
@role_required("Admin")
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"})