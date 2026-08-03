from flask import Blueprint, request
from marshmallow import ValidationError
from app.modules.auth.permissions import permission_required
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from .schemas import (CreatePackageCategoryRequestSchema, UpdatePackageCategoryRequestSchema,
    PackageCategorySummaryResponseSchema, PackageCategoryDetailResponseSchema, PackageCategoryLookupResponseSchema)
from .service import PackageCategoryService

package_category_bp = Blueprint("package_category", __name__, url_prefix="/api/v1/masters/package-categories")

def _flatten_errors(messages):
    return [{"code": "ERR_VALIDATION", "field": f, "message": m}
            for f, msgs in messages.items() for m in (msgs if isinstance(msgs, list) else [msgs])]

@package_category_bp.route("", methods=["POST"])
@permission_required("master.package_category.create")
def create_package_category():
    service = PackageCategoryService()
    try:
        data = CreatePackageCategoryRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)
    try:
        entity = service.create(data)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)
    resp, status = service.success(data=PackageCategoryDetailResponseSchema().dump(entity), message="Package category created.", status_code=201)
    resp.headers["Location"] = f"/api/v1/masters/package-categories/{entity.id}"
    return resp, status

@package_category_bp.route("", methods=["GET"])
@permission_required("master.package_category.read")
def list_package_categories():
    service = PackageCategoryService()
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    search = request.args.get("search", None)
    sort_by = request.args.get("sort_by", "display_order")
    sort_order = request.args.get("sort_order", "asc")
    is_active_raw = request.args.get("is_active")
    is_active = None if is_active_raw is None else is_active_raw.lower() == "true"
    result = service.list(page=page, page_size=page_size, search=search, is_active=is_active, sort_by=sort_by, sort_order=sort_order)
    return service.success(data={"items": PackageCategorySummaryResponseSchema(many=True).dump(result.items), "pagination": {"page": result.page, "page_size": result.page_size, "total_records": result.total_records, "total_pages": result.total_pages}}, message="Package categories retrieved.")

# LOOKUP MUST BE BEFORE /<id>
@package_category_bp.route("/lookup", methods=["GET"])
@permission_required("master.package_category.read")
def lookup_package_categories():
    service = PackageCategoryService()
    result = service.list(page=1, page_size=200, search=request.args.get("search"), is_active=True, sort_by="name", sort_order="asc")
    return service.success(data=PackageCategoryLookupResponseSchema(many=True).dump(result.items), message="Package categories lookup.")

@package_category_bp.route("/<id>", methods=["GET"])
@permission_required("master.package_category.read")
def get_package_category(id):
    service = PackageCategoryService()
    try:
        entity = service.get(id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    return service.success(data=PackageCategoryDetailResponseSchema().dump(entity), message="Package category retrieved.")

@package_category_bp.route("/<id>", methods=["PUT"])
@permission_required("master.package_category.update")
def update_package_category(id):
    service = PackageCategoryService()
    try:
        data = UpdatePackageCategoryRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)
    try:
        entity = service.update(id, data)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    except (DomainException, BusinessException) as err:
        return service.error(err.message, code=err.code, status_code=409)
    return service.success(data=PackageCategoryDetailResponseSchema().dump(entity), message="Package category updated.")

@package_category_bp.route("/<id>", methods=["DELETE"])
@permission_required("master.package_category.delete")
def delete_package_category(id):
    service = PackageCategoryService()
    try:
        service.delete(id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=409)
    return service.success(message="Package category deactivated.")
