from flask import Blueprint, request
from marshmallow import ValidationError

from app.modules.auth.permissions import permission_required
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from .schemas import (
    CreateCityRequestSchema,
    UpdateCityRequestSchema,
    CitySummaryResponseSchema,
    CityDetailResponseSchema,
)
from .service import CityService

city_bp = Blueprint("city", __name__, url_prefix="/api/v1/masters/cities")

def _flatten_errors(messages: dict) -> list[dict]:
    errors = []
    for field, msgs in messages.items():
        for msg in (msgs if isinstance(msgs, list) else [msgs]):
            errors.append({"code": "ERR_VALIDATION", "field": field, "message": msg})
    return errors

@city_bp.route("", methods=["POST"])
@permission_required("master.city.create")
def create_city():
    service = CityService()
    try:
        data = CreateCityRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)

    try:
        city = service.create(data)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)

    resp, status = service.success(
        data=CityDetailResponseSchema().dump(city),
        message="City created successfully.",
        status_code=201,
    )
    resp.headers["Location"] = f"/api/v1/masters/cities/{city.id}"
    return resp, status

@city_bp.route("", methods=["GET"])
@permission_required("master.city.read")
def list_cities():
    service = CityService()
    page       = request.args.get("page",       1,            type=int)
    page_size  = request.args.get("page_size",  20,           type=int)
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
            "items": CitySummaryResponseSchema(many=True).dump(result.items),
            "pagination": {
                "page":          result.page,
                "page_size":     result.page_size,
                "total_records": result.total_records,
                "total_pages":   result.total_pages,
            },
        },
        message="Cities retrieved successfully.",
    )

@city_bp.route("/<id>", methods=["GET"])
@permission_required("master.city.read")
def get_city(id):
    service = CityService()
    try:
        city = service.get(id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data=CityDetailResponseSchema().dump(city),
        message="City retrieved successfully.",
    )

@city_bp.route("/<id>", methods=["PUT"])
@permission_required("master.city.update")
def update_city(id):
    service = CityService()
    try:
        data = UpdateCityRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)

    try:
        city = service.update(id, data)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    except DomainException as err:
        return service.error(err.message, code=err.code, status_code=409)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)

    return service.success(
        data=CityDetailResponseSchema().dump(city),
        message="City updated successfully.",
    )

@city_bp.route("/<id>", methods=["DELETE"])
@permission_required("master.city.delete")
def delete_city(id):
    service = CityService()
    try:
        service.delete(id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)

    return service.success(message="City deactivated successfully.")
