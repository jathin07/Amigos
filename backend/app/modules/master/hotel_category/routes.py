from flask import Blueprint, request
from marshmallow import ValidationError
from app.modules.auth.permissions import permission_required
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from .schemas import (CreateHotelCategoryRequestSchema, UpdateHotelCategoryRequestSchema,
    HotelCategorySummaryResponseSchema, HotelCategoryDetailResponseSchema, HotelCategoryLookupResponseSchema)
from .service import HotelCategoryService

hotel_category_bp = Blueprint("hotel_category", __name__, url_prefix="/api/v1/masters/hotel-categories")

def _flatten_errors(messages):
    return [{"code": "ERR_VALIDATION", "field": f, "message": m}
            for f, msgs in messages.items() for m in (msgs if isinstance(msgs, list) else [msgs])]

@hotel_category_bp.route("", methods=["POST"])
@permission_required("master.hotel_category.create")
def create_hotel_category():
    service = HotelCategoryService()
    try:
        data = CreateHotelCategoryRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)
    try:
        entity = service.create(data)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)
    resp, status = service.success(data=HotelCategoryDetailResponseSchema().dump(entity), message="Hotel category created.", status_code=201)
    resp.headers["Location"] = f"/api/v1/masters/hotel-categories/{entity.id}"
    return resp, status

@hotel_category_bp.route("", methods=["GET"])
@permission_required("master.hotel_category.read")
def list_hotel_categories():
    service = HotelCategoryService()
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    search = request.args.get("search", None)
    sort_by = request.args.get("sort_by", "display_order")
    sort_order = request.args.get("sort_order", "asc")
    is_active_raw = request.args.get("is_active")
    is_active = None if is_active_raw is None else is_active_raw.lower() == "true"
    result = service.list(page=page, page_size=page_size, search=search, is_active=is_active, sort_by=sort_by, sort_order=sort_order)
    return service.success(data={"items": HotelCategorySummaryResponseSchema(many=True).dump(result.items), "pagination": {"page": result.page, "page_size": result.page_size, "total_records": result.total_records, "total_pages": result.total_pages}}, message="Hotel categories retrieved.")

# LOOKUP MUST BE BEFORE /<id>
@hotel_category_bp.route("/lookup", methods=["GET"])
@permission_required("master.hotel_category.read")
def lookup_hotel_categories():
    service = HotelCategoryService()
    result = service.list(page=1, page_size=200, search=request.args.get("search"), is_active=True, sort_by="name", sort_order="asc")
    return service.success(data=HotelCategoryLookupResponseSchema(many=True).dump(result.items), message="Hotel categories lookup.")

@hotel_category_bp.route("/<id>", methods=["GET"])
@permission_required("master.hotel_category.read")
def get_hotel_category(id):
    service = HotelCategoryService()
    try:
        entity = service.get(id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    return service.success(data=HotelCategoryDetailResponseSchema().dump(entity), message="Hotel category retrieved.")

@hotel_category_bp.route("/<id>", methods=["PUT"])
@permission_required("master.hotel_category.update")
def update_hotel_category(id):
    service = HotelCategoryService()
    try:
        data = UpdateHotelCategoryRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)
    try:
        entity = service.update(id, data)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    except (DomainException, BusinessException) as err:
        return service.error(err.message, code=err.code, status_code=409)
    return service.success(data=HotelCategoryDetailResponseSchema().dump(entity), message="Hotel category updated.")

@hotel_category_bp.route("/<id>", methods=["DELETE"])
@permission_required("master.hotel_category.delete")
def delete_hotel_category(id):
    service = HotelCategoryService()
    try:
        service.delete(id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)
    return service.success(message="Hotel category deactivated.")
