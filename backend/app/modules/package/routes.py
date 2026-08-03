from flask import Blueprint, request
from marshmallow import ValidationError

from app.modules.auth.permissions import permission_required
from app.domain.exceptions import BusinessException, NotFoundException
from .schemas import (
    CreatePackageRequestSchema,
    UpdatePackageRequestSchema,
    PackageSummaryResponseSchema,
    PackageDetailResponseSchema,
)
from .service import PackageService

package_bp = Blueprint("package", __name__)


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


@package_bp.route("", methods=["GET"])
@permission_required("package.read")
def list_packages():
    service = PackageService()
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    search = request.args.get("search", None)
    sort_by = request.args.get("sort_by", "title")
    sort_order = request.args.get("sort_order", "asc")

    filters = {}
    is_active_raw = request.args.get("is_active")
    if is_active_raw is not None:
        filters["is_active"] = is_active_raw.lower() == "true"

    is_featured_raw = request.args.get("is_featured")
    if is_featured_raw is not None:
        filters["is_featured"] = is_featured_raw.lower() == "true"

    duration_days_raw = request.args.get("duration_days")
    if duration_days_raw is not None:
        try:
            filters["duration_days"] = int(duration_days_raw)
        except ValueError:
            pass

    result = service.list(
        page=page,
        page_size=page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        **filters,
    )

    return service.success(
        data={
            "items": PackageSummaryResponseSchema(many=True).dump(result.items),
            "pagination": {
                "page": result.page,
                "page_size": result.page_size,
                "total_records": result.total_records,
                "total_pages": result.total_pages,
            },
        },
        message="Packages retrieved successfully.",
    )


@package_bp.route("/<string:package_id>", methods=["GET"])
@permission_required("package.read")
def get_package(package_id):
    service = PackageService()
    try:
        pkg = service.get(package_id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data=PackageDetailResponseSchema().dump(pkg),
        message="Package retrieved successfully.",
    )


@package_bp.route("", methods=["POST"])
@permission_required("package.create")
def create_package():
    service = PackageService()
    try:
        data = CreatePackageRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error(
            "Validation failed.",
            code="ERR_VALIDATION",
            errors=_flatten_errors(err.messages),
            status_code=400,
        )

    try:
        pkg = service.create(data)
    except BusinessException as err:
        status_code = 409 if err.code == "ERR_PACKAGE_DUPLICATE_TITLE" else 400
        return service.error(err.message, code=err.code, status_code=status_code)

    return service.success(
        data=PackageDetailResponseSchema().dump(pkg),
        message="Package created successfully.",
        status_code=201,
    )


@package_bp.route("/<string:package_id>", methods=["PUT"])
@permission_required("package.update")
def update_package(package_id):
    service = PackageService()
    body = request.get_json(silent=True) or {}
    # Capture raw keys BEFORE schema deserialization so we can implement
    # the three-state collection rule (absent / [] / [...]) in the service.
    raw_keys = set(body.keys())

    try:
        data = UpdatePackageRequestSchema().load(body)
    except ValidationError as err:
        return service.error(
            "Validation failed.",
            code="ERR_VALIDATION",
            errors=_flatten_errors(err.messages),
            status_code=400,
        )

    try:
        pkg = service.update(package_id, data, raw_keys=raw_keys)
    except BusinessException as err:
        status_code = 409 if err.code in (
            "ERR_PACKAGE_DUPLICATE_TITLE",
            "ERR_CONCURRENT_MODIFICATION",
        ) else 400
        return service.error(err.message, code=err.code, status_code=status_code)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data=PackageDetailResponseSchema().dump(pkg),
        message="Package updated successfully.",
    )


@package_bp.route("/<string:package_id>", methods=["DELETE"])
@permission_required("package.delete")
def delete_package(package_id):
    service = PackageService()
    try:
        service.delete(package_id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(message="Package deleted successfully.")
