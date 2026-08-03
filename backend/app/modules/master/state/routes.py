from flask import Blueprint, request
from marshmallow import ValidationError

from app.modules.auth.permissions import permission_required
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from .schemas import (
    CreateStateRequestSchema,
    UpdateStateRequestSchema,
    StateSummaryResponseSchema,
    StateDetailResponseSchema,
    StateLookupResponseSchema,
)
from .service import StateService

state_bp = Blueprint("state", __name__, url_prefix="/api/v1/masters/states")

# ─────────────────────────────────────────────────────────────────
# POST /api/v1/masters/states
# ─────────────────────────────────────────────────────────────────
@state_bp.route("", methods=["POST"])
@permission_required("master.state.create")
def create_state():
    service = StateService()
    try:
        data = CreateStateRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)

    try:
        state = service.create(data)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)

    resp, status = service.success(
        data=StateDetailResponseSchema().dump(state),
        message="State created successfully.",
        status_code=201,
    )
    resp.headers["Location"] = f"/api/v1/masters/states/{state.id}"
    return resp, status


# ─────────────────────────────────────────────────────────────────
# GET /api/v1/masters/states
# ─────────────────────────────────────────────────────────────────
@state_bp.route("", methods=["GET"])
@permission_required("master.state.read")
def list_states():
    service = StateService()
    page       = request.args.get("page",       1,            type=int)
    page_size  = request.args.get("page_size",  20,           type=int)
    search     = request.args.get("search",     None)
    country_id = request.args.get("country_id", None)
    sort_by    = request.args.get("sort_by",    "display_order")
    sort_order = request.args.get("sort_order", "asc")

    is_active_raw = request.args.get("is_active")
    is_active = None
    if is_active_raw is not None:
        is_active = is_active_raw.lower() == "true"

    try:
        result = service.list(
            page=page,
            page_size=page_size,
            search=search,
            is_active=is_active,
            country_id=country_id,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data={
            "items": StateSummaryResponseSchema(many=True).dump(result.items),
            "pagination": {
                "page":          result.page,
                "page_size":     result.page_size,
                "total_records": result.total_records,
                "total_pages":   result.total_pages,
            },
        },
        message="States retrieved successfully.",
    )


# ─────────────────────────────────────────────────────────────────
# GET /api/v1/masters/states/lookup
# ─────────────────────────────────────────────────────────────────
@state_bp.route("/lookup", methods=["GET"])
@permission_required("master.state.read")
def lookup_states():
    service = StateService()
    country_id = request.args.get("country_id", None)
    try:
        states = service.lookup(country_id=country_id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data={"items": StateLookupResponseSchema(many=True).dump(states)},
        message="State lookup retrieved successfully.",
    )


# ─────────────────────────────────────────────────────────────────
# GET /api/v1/masters/states/<id>
# ─────────────────────────────────────────────────────────────────
@state_bp.route("/<id>", methods=["GET"])
@permission_required("master.state.read")
def get_state(id):
    service = StateService()
    try:
        state = service.get(id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data=StateDetailResponseSchema().dump(state),
        message="State retrieved successfully.",
    )


# ─────────────────────────────────────────────────────────────────
# PUT /api/v1/masters/states/<id>
# ─────────────────────────────────────────────────────────────────
@state_bp.route("/<id>", methods=["PUT"])
@permission_required("master.state.update")
def update_state(id):
    service = StateService()
    try:
        data = UpdateStateRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)

    try:
        state = service.update(id, data)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    except DomainException as err:
        return service.error(err.message, code=err.code, status_code=409)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)

    return service.success(
        data=StateDetailResponseSchema().dump(state),
        message="State updated successfully.",
    )


# ─────────────────────────────────────────────────────────────────
# DELETE /api/v1/masters/states/<id>
# ─────────────────────────────────────────────────────────────────
@state_bp.route("/<id>", methods=["DELETE"])
@permission_required("master.state.delete")
def delete_state(id):
    service = StateService()
    try:
        service.delete(id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)

    return service.success(message="State deactivated successfully.")


# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────
def _flatten_errors(messages: dict) -> list[dict]:
    """Convert Marshmallow validation messages into error list format."""
    errors = []
    for field, msgs in messages.items():
        for msg in (msgs if isinstance(msgs, list) else [msgs]):
            errors.append({"code": "ERR_VALIDATION", "field": field, "message": msg})
    return errors
