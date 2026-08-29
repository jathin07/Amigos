import uuid
from flask import Blueprint, request
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity

from app.modules.auth.permissions import permission_required
from app.domain.exceptions import NotFoundException, ValidationException, BusinessException
from .schemas import (
    CreateTripPlanRequestSchema,
    UpdateTripPlanStatusRequestSchema,
    CompleteTripRequestSchema,
    UpdateTripDayRequestSchema,
    CreateVendorAllocationRequestSchema,
    ConfirmVendorAllocationRequestSchema,
    CreateTaskRequestSchema,
    UpdateTaskStatusRequestSchema,
    BulkAssignTasksRequestSchema,
    BulkUpdateTaskStatusRequestSchema,
    TripPlanSummaryResponseSchema,
    TripPlanDetailResponseSchema,
    TripDayDetailResponseSchema,
    VendorAllocationSummaryResponseSchema,
    VendorAllocationDetailResponseSchema,
    ChecklistSummaryResponseSchema,
    ChecklistItemResponseSchema,
    TaskSummaryResponseSchema,
    TaskDetailResponseSchema,
    TripCompletionValidationResponseSchema,
)
from .service import OperationsService

operations_bp = Blueprint("operations", __name__)


def _flatten_errors(messages: dict) -> list[dict]:
    errors = []
    for field, msgs in messages.items():
        if isinstance(msgs, dict):
            for subfield, submsgs in msgs.items():
                for submsg in (submsgs if isinstance(submsgs, list) else [submsgs]):
                    errors.append({"code": "ERR_VALIDATION", "field": f"{field}.{subfield}", "message": str(submsg)})
        elif isinstance(msgs, list):
            for item in msgs:
                if isinstance(item, dict):
                    for subfield, submsgs in item.items():
                        for submsg in (submsgs if isinstance(submsgs, list) else [submsgs]):
                            errors.append({"code": "ERR_VALIDATION", "field": f"{field}.{subfield}", "message": str(submsg)})
                else:
                    errors.append({"code": "ERR_VALIDATION", "field": field, "message": str(item)})
        else:
            errors.append({"code": "ERR_VALIDATION", "field": field, "message": str(msgs)})
    return errors


def _get_context_team_member_id() -> uuid.UUID | None:
    """Safely retrieves current user team_member_id context."""
    try:
        identity = get_jwt_identity()
    except RuntimeError:
        identity = None
    if not identity:
        return None
    try:
        from app.models import UserAccount
        from app.core.extensions import db
        user = db.session.get(UserAccount, uuid.UUID(str(identity)))
        return user.team_member_id if user else None
    except ValueError:
        return None


# ─────────────────────────────────────────────────────────────────
# TripPlan CRUD Routes
# ─────────────────────────────────────────────────────────────────

@operations_bp.route("/trip-plans", methods=["POST"])
@permission_required("operations.create")
def create_trip_plan():
    payload = request.get_json(silent=True) or {}
    try:
        data = CreateTripPlanRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = OperationsService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=422)

    context_id = _get_context_team_member_id()
    service = OperationsService()
    trip_plan = service.create_trip_plan(data, context_id)
    response_data = TripPlanDetailResponseSchema().dump(trip_plan)
    return service.success(data=response_data, message="Trip plan draft created successfully.", status_code=201)


@operations_bp.route("/trip-plans", methods=["GET"])
@permission_required("operations.read")
def list_trip_plans():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    search = request.args.get("q")
    sort_by = request.args.get("sort")
    sort_order = "asc"

    if sort_by and sort_by.startswith("-"):
        sort_order = "desc"
        sort_by = sort_by[1:]

    filters = {}
    for param in ["status_id", "prepared_by_team_member_id", "booking_id", "is_final"]:
        val = request.args.get(param)
        if val:
            if param == "is_final":
                filters[param] = val.lower() == "true"
            else:
                filters[param] = val

    service = OperationsService()
    paginated_res = service.plan_repo.paginate(
        page=page,
        page_size=limit,
        search_query=search,
        sort_by=sort_by,
        sort_order=sort_order,
        **filters
    )

    items_data = TripPlanSummaryResponseSchema(many=True).dump(paginated_res.items)

    meta = {
        "page": paginated_res.page,
        "limit": paginated_res.page_size,
        "total": paginated_res.total_records,
        "pages": paginated_res.total_pages
    }

    return service.success(data=items_data, meta=meta, message="Trip plans list retrieved.")


@operations_bp.route("/trip-plans/<uuid:id>", methods=["GET"])
@permission_required("operations.read")
def get_trip_plan(id):
    service = OperationsService()
    trip_plan = service.plan_repo.get_by_id(id)
    if not trip_plan:
        raise NotFoundException("Trip plan not found.")

    response_data = TripPlanDetailResponseSchema().dump(trip_plan)
    return service.success(data=response_data, message="Trip plan details retrieved.")


@operations_bp.route("/trip-plans/<uuid:id>/completion-check", methods=["GET"])
@permission_required("operations.read")
def check_trip_completion(id):
    service = OperationsService()
    validation_res = service.validate_completion(id)
    response_data = TripCompletionValidationResponseSchema().dump(validation_res)
    return service.success(data=response_data, message="Trip plan completion check complete.")


@operations_bp.route("/trip-plans/<uuid:id>/status", methods=["POST"])
@permission_required("operations.update")
def transition_trip_plan_status(id):
    payload = request.get_json(silent=True) or {}
    try:
        data = UpdateTripPlanStatusRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = OperationsService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=422)

    context_id = _get_context_team_member_id()
    service = OperationsService()
    trip_plan = service.transition_status(id, data["target_status"], context_id)
    response_data = TripPlanDetailResponseSchema().dump(trip_plan)
    return service.success(data=response_data, message="Trip plan status updated successfully.")


@operations_bp.route("/trip-plans/<uuid:id>/complete", methods=["POST"])
@permission_required("operations.update")
def complete_trip(id):
    payload = request.get_json(silent=True) or {}
    try:
        data = CompleteTripRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = OperationsService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=422)

    context_id = _get_context_team_member_id()
    service = OperationsService()
    trip_plan = service.complete_trip(id, data.get("notes"), context_id)
    response_data = TripPlanDetailResponseSchema().dump(trip_plan)
    return service.success(data=response_data, message="Trip plan completed successfully.")


# ─────────────────────────────────────────────────────────────────
# TripDay Routes
# ─────────────────────────────────────────────────────────────────

@operations_bp.route("/trip-plans/<uuid:id>/days", methods=["GET"])
@permission_required("operations.read")
def list_trip_days(id):
    service = OperationsService()
    trip_plan = service.plan_repo.get_by_id(id)
    if not trip_plan:
        raise NotFoundException("Trip plan not found.")

    response_data = TripDayDetailResponseSchema(many=True).dump(trip_plan.trip_days)
    return service.success(data=response_data, message="Trip days list retrieved.")


@operations_bp.route("/trip-plans/<uuid:id>/days/<uuid:day_id>", methods=["PATCH"])
@permission_required("operations.update")
def update_trip_day(id, day_id):
    payload = request.get_json(silent=True) or {}
    try:
        data = UpdateTripDayRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = OperationsService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=422)

    context_id = _get_context_team_member_id()
    service = OperationsService()
    trip_day = service.update_trip_day(id, day_id, data, context_id)
    response_data = TripDayDetailResponseSchema().dump(trip_day)
    return service.success(data=response_data, message="Trip day updated successfully.")


# ─────────────────────────────────────────────────────────────────
# VendorAllocation Routes
# ─────────────────────────────────────────────────────────────────

@operations_bp.route("/trip-plans/<uuid:id>/allocations", methods=["GET"])
@permission_required("operations.read")
def list_allocations(id):
    service = OperationsService()
    trip_plan = service.plan_repo.get_by_id(id)
    if not trip_plan:
        raise NotFoundException("Trip plan not found.")

    allocs = []
    for day in trip_plan.trip_days:
        allocs.extend(day.vendor_allocations)

    response_data = VendorAllocationSummaryResponseSchema(many=True).dump(allocs)
    return service.success(data=response_data, message="Vendor allocations list retrieved.")


@operations_bp.route("/trip-plans/<uuid:id>/days/<uuid:day_id>/allocations", methods=["POST"])
@permission_required("operations.update")
def create_vendor_allocation(id, day_id):
    payload = request.get_json(silent=True) or {}
    try:
        data = CreateVendorAllocationRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = OperationsService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=422)

    context_id = _get_context_team_member_id()
    service = OperationsService()
    alloc = service.create_vendor_allocation(id, day_id, data, context_id)
    response_data = VendorAllocationSummaryResponseSchema().dump(alloc)
    return service.success(data=response_data, message="Vendor allocation created successfully.", status_code=201)


@operations_bp.route("/allocations/<uuid:alloc_id>", methods=["GET"])
@permission_required("operations.read")
def get_vendor_allocation(alloc_id):
    service = OperationsService()
    alloc = service.alloc_repo.get(alloc_id)
    if not alloc:
        raise NotFoundException("Vendor allocation not found.")

    response_data = VendorAllocationDetailResponseSchema().dump(alloc)
    return service.success(data=response_data, message="Vendor allocation details retrieved.")


@operations_bp.route("/allocations/<uuid:alloc_id>", methods=["PATCH"])
@permission_required("operations.update")
def update_vendor_allocation(alloc_id):
    payload = request.get_json(silent=True) or {}
    service = OperationsService()
    alloc = service.alloc_repo.get(alloc_id)
    if not alloc:
        raise NotFoundException("Vendor allocation not found.")

    if alloc.is_locked:
        raise BusinessException("Cannot update a locked vendor allocation.", code="VENDOR_ALLOCATION_LOCKED")

    # Simple field updates
    if "notes" in payload:
        alloc.notes = payload["notes"]
    if "quantity" in payload:
        alloc.quantity = int(payload["quantity"])
        alloc.quoted_amount = alloc.quantity * alloc.unit_price
    if "unit_price" in payload:
        alloc.unit_price = payload["unit_price"]
        alloc.quoted_amount = alloc.quantity * alloc.unit_price

    context_id = _get_context_team_member_id()
    if context_id:
        alloc.updated_by_team_member_id = context_id

    service.alloc_repo.update(alloc)
    service.commit()

    response_data = VendorAllocationDetailResponseSchema().dump(alloc)
    return service.success(data=response_data, message="Vendor allocation updated successfully.")


@operations_bp.route("/allocations/<uuid:alloc_id>", methods=["DELETE"])
@permission_required("operations.update")
def delete_vendor_allocation(alloc_id):
    service = OperationsService()
    alloc = service.alloc_repo.get(alloc_id)
    if not alloc:
        raise NotFoundException("Vendor allocation not found.")

    if alloc.is_locked:
        raise BusinessException("Cannot delete a locked vendor allocation.", code="VENDOR_ALLOCATION_LOCKED")

    service.alloc_repo.delete(alloc)
    service.commit()
    return "", 204


@operations_bp.route("/allocations/<uuid:alloc_id>/confirm", methods=["POST"])
@permission_required("operations.update")
def confirm_vendor_allocation(alloc_id):
    payload = request.get_json(silent=True) or {}
    try:
        data = ConfirmVendorAllocationRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = OperationsService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=422)

    context_id = _get_context_team_member_id()
    service = OperationsService()
    alloc = service.confirm_vendor_allocation(alloc_id, data, context_id)
    response_data = VendorAllocationDetailResponseSchema().dump(alloc)
    return service.success(data=response_data, message="Vendor allocation confirmed successfully.")


@operations_bp.route("/allocations/<uuid:alloc_id>/lock", methods=["POST"])
@permission_required("operations.lock")
def lock_vendor_allocation(alloc_id):
    context_id = _get_context_team_member_id()
    service = OperationsService()
    alloc = service.lock_vendor_allocation(alloc_id, context_id)
    response_data = VendorAllocationDetailResponseSchema().dump(alloc)
    return service.success(data=response_data, message="Vendor allocation locked successfully.")


@operations_bp.route("/allocations/bulk-confirm", methods=["POST"])
@permission_required("operations.update")
def bulk_confirm_allocations():
    payload = request.get_json(silent=True) or {}
    alloc_ids = payload.get("allocation_ids", [])
    confirmed_price = payload.get("confirmed_price", 0)

    context_id = _get_context_team_member_id()
    service = OperationsService()
    confirmed_count = 0
    for a_id in alloc_ids:
        try:
            service.confirm_vendor_allocation(a_id, {"confirmed_price": confirmed_price}, context_id)
            confirmed_count += 1
        except Exception:
            continue
    return service.success(data={"confirmed_count": confirmed_count}, message="Bulk confirmations completed.")


# ─────────────────────────────────────────────────────────────────
# Checklist Routes
# ─────────────────────────────────────────────────────────────────

@operations_bp.route("/trip-plans/<uuid:id>/checklist", methods=["GET"])
@permission_required("operations.read")
def get_trip_checklist(id):
    service = OperationsService()
    trip_plan = service.plan_repo.get_by_id(id)
    if not trip_plan:
        raise NotFoundException("Trip plan not found.")

    items = service.checklist_repo.list_by_booking(trip_plan.booking_id)
    rate = service.checklist_repo.completion_rate(trip_plan.booking_id)

    response_data = {
        "total_items": len(items),
        "completed_items": sum(1 for i in items if i.is_completed),
        "completion_rate": str(rate),
        "items": items
    }
    dumped = ChecklistSummaryResponseSchema().dump(response_data)
    return service.success(data=dumped, message="Checklist retrieved.")


@operations_bp.route("/trip-plans/<uuid:id>/checklist/<uuid:item_id>", methods=["PATCH"])
@permission_required("operations.update_checklist")
def update_checklist_item(id, item_id):
    payload = request.get_json(silent=True) or {}
    is_completed = payload.get("is_completed", False)

    context_id = _get_context_team_member_id()
    service = OperationsService()
    item = service.update_checklist_item(item_id, is_completed, context_id)
    response_data = ChecklistItemResponseSchema().dump(item)
    return service.success(data=response_data, message="Checklist item updated successfully.")


@operations_bp.route("/trip-plans/<uuid:id>/checklist/bulk-complete", methods=["POST"])
@permission_required("operations.update_checklist")
def bulk_complete_checklist(id, item_id):
    payload = request.get_json(silent=True) or {}
    item_ids = payload.get("item_ids", [])

    context_id = _get_context_team_member_id()
    service = OperationsService()
    trip_plan = service.plan_repo.get_by_id(id)
    if not trip_plan:
        raise NotFoundException("Trip plan not found.")

    res = service.bulk_complete_checklist(trip_plan.booking_id, item_ids, context_id)
    return service.success(data=res, message="Bulk complete checklist items complete.")


# ─────────────────────────────────────────────────────────────────
# Task Routes
# ─────────────────────────────────────────────────────────────────

@operations_bp.route("/tasks", methods=["GET"])
@permission_required("operations.read")
def list_tasks():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    search = request.args.get("q")
    sort_by = request.args.get("sort")
    sort_order = "asc"

    if sort_by and sort_by.startswith("-"):
        sort_order = "desc"
        sort_by = sort_by[1:]

    filters = {}
    for param in ["booking_id", "lead_id", "assigned_to_team_member_id", "task_status_id", "priority_id"]:
        val = request.args.get(param)
        if val:
            filters[param] = val

    service = OperationsService()
    paginated_res = service.task_repo.paginate(
        page=page,
        page_size=limit,
        search_query=search,
        sort_by=sort_by,
        sort_order=sort_order,
        **filters
    )

    items_data = TaskSummaryResponseSchema(many=True).dump(paginated_res.items)

    meta = {
        "page": paginated_res.page,
        "limit": paginated_res.page_size,
        "total": paginated_res.total_records,
        "pages": paginated_res.total_pages
    }

    return service.success(data=items_data, meta=meta, message="Tasks list retrieved.")


@operations_bp.route("/tasks", methods=["POST"])
@permission_required("operations.update")
def create_task():
    payload = request.get_json(silent=True) or {}
    try:
        data = CreateTaskRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = OperationsService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=422)

    context_id = _get_context_team_member_id()
    service = OperationsService()
    task = service.create_task(data, context_id)
    response_data = TaskDetailResponseSchema().dump(task)
    return service.success(data=response_data, message="Task created successfully.", status_code=201)


@operations_bp.route("/tasks/<uuid:task_id>", methods=["GET"])
@permission_required("operations.read")
def get_task(task_id):
    service = OperationsService()
    task = service.task_repo.get(task_id)
    if not task or task.is_deleted:
        raise NotFoundException("Task not found.")

    response_data = TaskDetailResponseSchema().dump(task)
    return service.success(data=response_data, message="Task details retrieved.")


@operations_bp.route("/tasks/<uuid:task_id>/status", methods=["PATCH"])
@permission_required("operations.update")
def update_task_status(task_id):
    payload = request.get_json(silent=True) or {}
    try:
        data = UpdateTaskStatusRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = OperationsService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=422)

    context_id = _get_context_team_member_id()
    service = OperationsService()
    task = service.update_task_status(task_id, data, context_id)
    response_data = TaskDetailResponseSchema().dump(task)
    return service.success(data=response_data, message="Task status updated successfully.")


@operations_bp.route("/tasks/<uuid:task_id>", methods=["DELETE"])
@permission_required("operations.update")
def delete_task(task_id):
    context_id = _get_context_team_member_id()
    service = OperationsService()
    service.soft_delete_task(task_id, context_id)
    return "", 204


@operations_bp.route("/tasks/bulk-assign", methods=["POST"])
@permission_required("operations.update")
def bulk_assign_tasks():
    payload = request.get_json(silent=True) or {}
    try:
        data = BulkAssignTasksRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = OperationsService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=422)

    context_id = _get_context_team_member_id()
    service = OperationsService()
    res = service.bulk_assign_tasks(data["task_ids"], data["team_member_id"], context_id)
    return service.success(data=res, message="Bulk assignment completed.")


@operations_bp.route("/tasks/bulk-status", methods=["PATCH"])
@permission_required("operations.update")
def bulk_update_tasks_status():
    payload = request.get_json(silent=True) or {}
    try:
        data = BulkUpdateTaskStatusRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = OperationsService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=422)

    context_id = _get_context_team_member_id()
    service = OperationsService()
    res = service.bulk_update_task_status(data["task_ids"], data["task_status_id"], context_id)
    return service.success(data=res, message="Bulk status update completed.")
