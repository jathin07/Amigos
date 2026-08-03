from flask import Blueprint, request
from marshmallow import ValidationError

from app.modules.auth.permissions import permission_required
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from .schemas import (
    CreateDistrictRequestSchema,
    UpdateDistrictRequestSchema,
    DistrictSummaryResponseSchema,
    DistrictDetailResponseSchema,
    DistrictLookupResponseSchema,
)
from .service import DistrictService

district_bp = Blueprint("district", __name__, url_prefix="/api/v1/masters/districts")


def _flatten_errors(messages: dict) -> list[dict]:
    errors = []
    for field, msgs in messages.items():
        for msg in (msgs if isinstance(msgs, list) else [msgs]):
            errors.append({"code": "ERR_VALIDATION", "field": field, "message": msg})
    return errors


# ─────────────────────────────────────────────────────────────────
# POST /api/v1/masters/districts
# ─────────────────────────────────────────────────────────────────
@district_bp.route("", methods=["POST"])
@permission_required("master.district.create")
def create_district():
    service = DistrictService()
    try:
        data = CreateDistrictRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)

    try:
        district = service.create(data)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)

    resp, status = service.success(
        data=DistrictDetailResponseSchema().dump(district),
        message="District created successfully.",
        status_code=201,
    )
    resp.headers["Location"] = f"/api/v1/masters/districts/{district.id}"
    return resp, status


# ─────────────────────────────────────────────────────────────────
# GET /api/v1/masters/districts
# ─────────────────────────────────────────────────────────────────
@district_bp.route("", methods=["GET"])
@permission_required("master.district.read")
def list_districts():
    service = DistrictService()
    page       = request.args.get("page",       1,   type=int)
    page_size  = request.args.get("page_size",  20,  type=int)
    search     = request.args.get("search",     None)
    state_id   = request.args.get("state_id",   None)
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
            state_id=state_id,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data={
            "items": DistrictSummaryResponseSchema(many=True).dump(result.items),
            "pagination": {
                "page":          result.page,
                "page_size":     result.page_size,
                "total_records": result.total_records,
                "total_pages":   result.total_pages,
            },
        },
        message="Districts retrieved successfully.",
    )


# ─────────────────────────────────────────────────────────────────
# GET /api/v1/masters/districts/lookup  ← MUST be before /<id>
# ─────────────────────────────────────────────────────────────────
@district_bp.route("/lookup", methods=["GET"])
@permission_required("master.district.read")
def lookup_districts():
    service = DistrictService()
    state_id = request.args.get("state_id", None)
    search   = request.args.get("search",   None)

    try:
        result = service.list(
            page=1,
            page_size=200,
            search=search,
            is_active=True,
            state_id=state_id,
            sort_by="name",
            sort_order="asc",
        )
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data=DistrictLookupResponseSchema(many=True).dump(result.items),
        message="Districts lookup retrieved successfully.",
    )


# ─────────────────────────────────────────────────────────────────
# GET /api/v1/masters/districts/<id>
# ─────────────────────────────────────────────────────────────────
@district_bp.route("/<id>", methods=["GET"])
@permission_required("master.district.read")
def get_district(id):
    service = DistrictService()
    try:
        district = service.get(id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data=DistrictDetailResponseSchema().dump(district),
        message="District retrieved successfully.",
    )


# ─────────────────────────────────────────────────────────────────
# PUT /api/v1/masters/districts/<id>
# ─────────────────────────────────────────────────────────────────
@district_bp.route("/<id>", methods=["PUT"])
@permission_required("master.district.update")
def update_district(id):
    service = DistrictService()
    try:
        data = UpdateDistrictRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)

    try:
        district = service.update(id, data)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    except DomainException as err:
        return service.error(err.message, code=err.code, status_code=409)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)

    return service.success(
        data=DistrictDetailResponseSchema().dump(district),
        message="District updated successfully.",
    )


# ─────────────────────────────────────────────────────────────────
# DELETE /api/v1/masters/districts/<id>
# ─────────────────────────────────────────────────────────────────
@district_bp.route("/<id>", methods=["DELETE"])
@permission_required("master.district.delete")
def delete_district(id):
    service = DistrictService()
    try:
        service.delete(id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)

    return service.success(message="District deactivated successfully.")
