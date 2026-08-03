from flask import Blueprint, request
from marshmallow import ValidationError

from app.modules.auth.permissions import permission_required
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from .schemas import (
    CreateDestinationRequestSchema,
    UpdateDestinationRequestSchema,
    DestinationSummaryResponseSchema,
    DestinationDetailResponseSchema,
    DestinationLookupResponseSchema,
)
from .service import DestinationService

destination_bp = Blueprint("destination", __name__, url_prefix="/api/v1/masters/destinations")


def _flatten_errors(messages: dict) -> list[dict]:
    errors = []
    for field, msgs in messages.items():
        for msg in (msgs if isinstance(msgs, list) else [msgs]):
            errors.append({"code": "ERR_VALIDATION", "field": field, "message": msg})
    return errors


# ─────────────────────────────────────────────────────────────────
# POST /api/v1/masters/destinations
# ─────────────────────────────────────────────────────────────────
@destination_bp.route("", methods=["POST"])
@permission_required("master.destination.create")
def create_destination():
    service = DestinationService()
    try:
        data = CreateDestinationRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)

    try:
        destination = service.create(data)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)

    resp, status = service.success(
        data=DestinationDetailResponseSchema().dump(destination),
        message="Destination created successfully.",
        status_code=201,
    )
    resp.headers["Location"] = f"/api/v1/masters/destinations/{destination.id}"
    return resp, status


# ─────────────────────────────────────────────────────────────────
# GET /api/v1/masters/destinations
# ─────────────────────────────────────────────────────────────────
@destination_bp.route("", methods=["GET"])
@permission_required("master.destination.read")
def list_destinations():
    service = DestinationService()
    page        = request.args.get("page",        1,   type=int)
    page_size   = request.args.get("page_size",   20,  type=int)
    search      = request.args.get("search",      None)
    country_id  = request.args.get("country_id",  None)
    state_id    = request.args.get("state_id",    None)
    district_id = request.args.get("district_id", None)
    sort_by     = request.args.get("sort_by",     "display_order")
    sort_order  = request.args.get("sort_order",  "asc")

    is_active_raw = request.args.get("is_active")
    is_active = None
    if is_active_raw is not None:
        is_active = is_active_raw.lower() == "true"

    result = service.list(
        page=page,
        page_size=page_size,
        search=search,
        is_active=is_active,
        country_id=country_id,
        state_id=state_id,
        district_id=district_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return service.success(
        data={
            "items": DestinationSummaryResponseSchema(many=True).dump(result.items),
            "pagination": {
                "page":          result.page,
                "page_size":     result.page_size,
                "total_records": result.total_records,
                "total_pages":   result.total_pages,
            },
        },
        message="Destinations retrieved successfully.",
    )


# ─────────────────────────────────────────────────────────────────
# GET /api/v1/masters/destinations/lookup  ← MUST be before /<id>
# ─────────────────────────────────────────────────────────────────
@destination_bp.route("/lookup", methods=["GET"])
@permission_required("master.destination.read")
def lookup_destinations():
    service     = DestinationService()
    district_id = request.args.get("district_id", None)
    state_id    = request.args.get("state_id",    None)
    country_id  = request.args.get("country_id",  None)
    search      = request.args.get("search",      None)

    result = service.list(
        page=1,
        page_size=500,
        search=search,
        is_active=True,
        country_id=country_id,
        state_id=state_id,
        district_id=district_id,
        sort_by="name",
        sort_order="asc",
    )

    return service.success(
        data=DestinationLookupResponseSchema(many=True).dump(result.items),
        message="Destinations lookup retrieved successfully.",
    )


# ─────────────────────────────────────────────────────────────────
# GET /api/v1/masters/destinations/<id>
# ─────────────────────────────────────────────────────────────────
@destination_bp.route("/<id>", methods=["GET"])
@permission_required("master.destination.read")
def get_destination(id):
    service = DestinationService()
    try:
        destination = service.get(id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data=DestinationDetailResponseSchema().dump(destination),
        message="Destination retrieved successfully.",
    )


# ─────────────────────────────────────────────────────────────────
# PUT /api/v1/masters/destinations/<id>
# ─────────────────────────────────────────────────────────────────
@destination_bp.route("/<id>", methods=["PUT"])
@permission_required("master.destination.update")
def update_destination(id):
    service = DestinationService()
    try:
        data = UpdateDestinationRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)

    try:
        destination = service.update(id, data)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    except DomainException as err:
        return service.error(err.message, code=err.code, status_code=409)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)

    return service.success(
        data=DestinationDetailResponseSchema().dump(destination),
        message="Destination updated successfully.",
    )


# ─────────────────────────────────────────────────────────────────
# DELETE /api/v1/masters/destinations/<id>
# ─────────────────────────────────────────────────────────────────
@destination_bp.route("/<id>", methods=["DELETE"])
@permission_required("master.destination.delete")
def delete_destination(id):
    service = DestinationService()
    try:
        service.delete(id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)

    return service.success(message="Destination deactivated successfully.")
