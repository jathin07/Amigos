from flask import Blueprint, request
from marshmallow import ValidationError

from app.modules.auth.permissions import permission_required
from app.domain.exceptions import BusinessException, NotFoundException
from .schemas import (
    CreateVendorRequestSchema,
    UpdateVendorRequestSchema,
    VendorSummaryResponseSchema,
    VendorDetailResponseSchema,
)
from .service import VendorService

vendor_bp = Blueprint("vendor", __name__)


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


@vendor_bp.route("", methods=["GET"])
@permission_required("vendor.read")
def list_vendors():
    service = VendorService()
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    search = request.args.get("search", None)
    sort_by = request.args.get("sort_by", "vendor_name")
    sort_order = request.args.get("sort_order", "asc")

    is_active_raw = request.args.get("is_active")
    is_active = None
    if is_active_raw is not None:
        is_active = is_active_raw.lower() == "true"

    is_verified_raw = request.args.get("is_verified")
    is_verified = None
    if is_verified_raw is not None:
        is_verified = is_verified_raw.lower() == "true"

    vendor_type_id = request.args.get("vendor_type_id", None)

    filters = {}
    if is_active is not None:
        filters["is_active"] = is_active
    if is_verified is not None:
        filters["is_verified"] = is_verified
    if vendor_type_id:
        filters["vendor_type_id"] = vendor_type_id

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
            "items": VendorSummaryResponseSchema(many=True).dump(result.items),
            "pagination": {
                "page": result.page,
                "page_size": result.page_size,
                "total_records": result.total_records,
                "total_pages": result.total_pages,
            },
        },
        message="Vendors retrieved successfully.",
    )


@vendor_bp.route("/<string:vendor_id>", methods=["GET"])
@permission_required("vendor.read")
def get_vendor(vendor_id):
    service = VendorService()
    try:
        vendor = service.get(vendor_id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data=VendorDetailResponseSchema().dump(vendor),
        message="Vendor retrieved successfully.",
    )


@vendor_bp.route("", methods=["POST"])
@permission_required("vendor.create")
def create_vendor():
    service = VendorService()
    try:
        data = CreateVendorRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error(
            "Validation failed.",
            code="ERR_VALIDATION",
            errors=_flatten_errors(err.messages),
            status_code=400,
        )

    try:
        vendor = service.create(data)
    except BusinessException as err:
        status_code = 409 if err.code == "ERR_VENDOR_DUPLICATE_GST" else 400
        return service.error(err.message, code=err.code, status_code=status_code)

    return service.success(
        data=VendorDetailResponseSchema().dump(vendor),
        message="Vendor created successfully.",
        status_code=201,
    )


@vendor_bp.route("/<string:vendor_id>", methods=["PUT"])
@permission_required("vendor.update")
def update_vendor(vendor_id):
    service = VendorService()
    try:
        data = UpdateVendorRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error(
            "Validation failed.",
            code="ERR_VALIDATION",
            errors=_flatten_errors(err.messages),
            status_code=400,
        )

    try:
        vendor = service.update(vendor_id, data)
    except BusinessException as err:
        status_code = 409 if err.code in ("ERR_VENDOR_DUPLICATE_GST", "ERR_CONCURRENT_MODIFICATION") else 400
        return service.error(err.message, code=err.code, status_code=status_code)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data=VendorDetailResponseSchema().dump(vendor),
        message="Vendor updated successfully.",
    )


@vendor_bp.route("/<string:vendor_id>", methods=["DELETE"])
@permission_required("vendor.delete")
def delete_vendor(vendor_id):
    service = VendorService()
    try:
        service.delete(vendor_id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        message="Vendor deleted successfully.",
    )


@vendor_bp.route("/<string:vendor_id>/verify", methods=["POST"])
@permission_required("vendor.update")
def verify_vendor(vendor_id):
    service = VendorService()
    try:
        vendor = service.verify(vendor_id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data=VendorDetailResponseSchema().dump(vendor),
        message="Vendor verified successfully.",
    )


@vendor_bp.route("/<string:vendor_id>/unverify", methods=["POST"])
@permission_required("vendor.update")
def unverify_vendor(vendor_id):
    service = VendorService()
    try:
        vendor = service.unverify(vendor_id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data=VendorDetailResponseSchema().dump(vendor),
        message="Vendor unverified successfully.",
    )
