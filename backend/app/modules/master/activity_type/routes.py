from flask import Blueprint, request
from marshmallow import ValidationError
from app.modules.auth.permissions import permission_required
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from .schemas import (CreateActivityTypeRequestSchema, UpdateActivityTypeRequestSchema,
    ActivityTypeSummaryResponseSchema, ActivityTypeDetailResponseSchema, ActivityTypeLookupResponseSchema)
from .service import ActivityTypeService

activity_type_bp = Blueprint("activity_type", __name__, url_prefix="/api/v1/masters/activity-types")

def _flatten_errors(messages):
    return [{"code": "ERR_VALIDATION", "field": f, "message": m}
            for f, msgs in messages.items() for m in (msgs if isinstance(msgs, list) else [msgs])]

@activity_type_bp.route("", methods=["POST"])
@permission_required("master.activity_type.create")
def create_activity_type():
    service = ActivityTypeService()
    try:
        data = CreateActivityTypeRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)
    try:
        entity = service.create(data)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)
    resp, status = service.success(data=ActivityTypeDetailResponseSchema().dump(entity), message="Activity type created.", status_code=201)
    resp.headers["Location"] = f"/api/v1/masters/activity-types/{entity.id}"
    return resp, status

@activity_type_bp.route("", methods=["GET"])
@permission_required("master.activity_type.read")
def list_activity_types():
    service = ActivityTypeService()
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    search = request.args.get("search", None)
    sort_by = request.args.get("sort_by", "display_order")
    sort_order = request.args.get("sort_order", "asc")
    is_active_raw = request.args.get("is_active")
    is_active = None if is_active_raw is None else is_active_raw.lower() == "true"
    result = service.list(page=page, page_size=page_size, search=search, is_active=is_active, sort_by=sort_by, sort_order=sort_order)
    return service.success(data={"items": ActivityTypeSummaryResponseSchema(many=True).dump(result.items), "pagination": {"page": result.page, "page_size": result.page_size, "total_records": result.total_records, "total_pages": result.total_pages}}, message="Activity types retrieved.")

# LOOKUP MUST BE BEFORE /<id>
@activity_type_bp.route("/lookup", methods=["GET"])
@permission_required("master.activity_type.read")
def lookup_activity_types():
    service = ActivityTypeService()
    result = service.list(page=1, page_size=200, search=request.args.get("search"), is_active=True, sort_by="name", sort_order="asc")
    return service.success(data=ActivityTypeLookupResponseSchema(many=True).dump(result.items), message="Activity types lookup.")

@activity_type_bp.route("/<id>", methods=["GET"])
@permission_required("master.activity_type.read")
def get_activity_type(id):
    service = ActivityTypeService()
    try:
        entity = service.get(id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    return service.success(data=ActivityTypeDetailResponseSchema().dump(entity), message="Activity type retrieved.")

@activity_type_bp.route("/<id>", methods=["PUT"])
@permission_required("master.activity_type.update")
def update_activity_type(id):
    service = ActivityTypeService()
    try:
        data = UpdateActivityTypeRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)
    try:
        entity = service.update(id, data)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    except (DomainException, BusinessException) as err:
        return service.error(err.message, code=err.code, status_code=409)
    return service.success(data=ActivityTypeDetailResponseSchema().dump(entity), message="Activity type updated.")

@activity_type_bp.route("/<id>", methods=["DELETE"])
@permission_required("master.activity_type.delete")
def delete_activity_type(id):
    service = ActivityTypeService()
    try:
        service.delete(id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)
    return service.success(message="Activity type deactivated.")
