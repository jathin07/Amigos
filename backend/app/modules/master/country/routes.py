from flask import Blueprint, request
from marshmallow import ValidationError

from app.modules.auth.permissions import permission_required
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from .schemas import (
    CreateCountryRequestSchema,
    UpdateCountryRequestSchema,
    CountrySummaryResponseSchema,
    CountryDetailResponseSchema,
    CountryLookupResponseSchema,
)
from .service import CountryService

country_bp = Blueprint("country", __name__, url_prefix="/api/v1/masters/countries")

# ─────────────────────────────────────────────────────────────────
# POST /api/v1/masters/countries
# ─────────────────────────────────────────────────────────────────
@country_bp.route("", methods=["POST"])
@permission_required("master.country.create")
def create_country():
    service = CountryService()
    try:
        data = CreateCountryRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)

    try:
        country = service.create(data)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)

    resp, status = service.success(
        data=CountryDetailResponseSchema().dump(country),
        message="Country created successfully.",
        status_code=201,
    )
    resp.headers["Location"] = f"/api/v1/masters/countries/{country.id}"
    return resp, status


# ─────────────────────────────────────────────────────────────────
# GET /api/v1/masters/countries
# ─────────────────────────────────────────────────────────────────
@country_bp.route("", methods=["GET"])
@permission_required("master.country.read")
def list_countries():
    service = CountryService()
    page       = request.args.get("page",       1,            type=int)
    page_size  = request.args.get("page_size",  20,           type=int)
    search     = request.args.get("search",     None)
    sort_by    = request.args.get("sort_by",    "display_order")
    sort_order = request.args.get("sort_order", "asc")

    is_active_raw = request.args.get("is_active")
    is_active = None
    if is_active_raw is not None:
        is_active = is_active_raw.lower() == "true"

    result = service.list(
        page=page,
        page_size=page_size,
        search=search,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return service.success(
        data={
            "items": CountrySummaryResponseSchema(many=True).dump(result.items),
            "pagination": {
                "page":          result.page,
                "page_size":     result.page_size,
                "total_records": result.total_records,
                "total_pages":   result.total_pages,
            },
        },
        message="Countries retrieved successfully.",
    )


# ─────────────────────────────────────────────────────────────────
# GET /api/v1/masters/countries/lookup
# ─────────────────────────────────────────────────────────────────
@country_bp.route("/lookup", methods=["GET"])
@permission_required("master.country.read")
def lookup_countries():
    service = CountryService()
    countries = service.lookup()
    return service.success(
        data={"items": CountryLookupResponseSchema(many=True).dump(countries)},
        message="Country lookup retrieved successfully.",
    )


# ─────────────────────────────────────────────────────────────────
# GET /api/v1/masters/countries/<id>
# ─────────────────────────────────────────────────────────────────
@country_bp.route("/<id>", methods=["GET"])
@permission_required("master.country.read")
def get_country(id):
    service = CountryService()
    try:
        country = service.get(id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data=CountryDetailResponseSchema().dump(country),
        message="Country retrieved successfully.",
    )


# ─────────────────────────────────────────────────────────────────
# PUT /api/v1/masters/countries/<id>
# ─────────────────────────────────────────────────────────────────
@country_bp.route("/<id>", methods=["PUT"])
@permission_required("master.country.update")
def update_country(id):
    service = CountryService()
    try:
        data = UpdateCountryRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)

    try:
        country = service.update(id, data)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    except DomainException as err:
        return service.error(err.message, code=err.code, status_code=409)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)

    return service.success(
        data=CountryDetailResponseSchema().dump(country),
        message="Country updated successfully.",
    )


# ─────────────────────────────────────────────────────────────────
# DELETE /api/v1/masters/countries/<id>
# ─────────────────────────────────────────────────────────────────
@country_bp.route("/<id>", methods=["DELETE"])
@permission_required("master.country.delete")
def delete_country(id):
    service = CountryService()
    try:
        service.delete(id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)

    return service.success(message="Country deactivated successfully.")


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
