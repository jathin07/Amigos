import uuid
from flask import Blueprint, request
from marshmallow import ValidationError
from app.domain.exceptions import BusinessException, NotFoundException
from app.modules.auth.permissions import permission_required
from .service import OrganizationService

organization_bp = Blueprint("organization", __name__)
from .schemas import (
    UpdateOrganizationRequestSchema,
    OrganizationDetailResponseSchema,
)

def _flatten_errors(messages: dict) -> list[dict]:
    errors = []
    for field, msgs in messages.items():
        if isinstance(msgs, list):
            for item in msgs:
                errors.append({"code": "ERR_VALIDATION", "field": field, "message": str(item)})
        else:
            errors.append({"code": "ERR_VALIDATION", "field": field, "message": str(msgs)})
    return errors

@organization_bp.route("", methods=["GET"])
@permission_required("organization.read")
def list_organizations():
    service = OrganizationService()
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    search = request.args.get("search", None, type=str)
    is_active = request.args.get("is_active", None)
    if is_active is not None:
        is_active = is_active.lower() == "true"

    paginated = service.list_organizations(page=page, page_size=page_size, search=search, is_active=is_active)
    
    return service.success(
        data={
            "items": OrganizationDetailResponseSchema(many=True).dump(paginated.items),
            "pagination": {
                "page": paginated.page,
                "page_size": paginated.per_page,
                "total_records": paginated.total,
                "total_pages": paginated.pages
            }
        },
        message="Organizations retrieved successfully.",
    )

@organization_bp.route("/lookup", methods=["GET"])
@permission_required("organization.read")
def lookup_organizations():
    service = OrganizationService()
    orgs = service.lookup()
    # Simple ID and Name mapping
    items = [{"id": str(o.id), "name": o.organization_name} for o in orgs]
    return service.success(
        data={"items": items},
        message="Organization lookup retrieved successfully.",
    )

@organization_bp.route("", methods=["POST"])
@permission_required("organization.update") # Reuse update permission for management
def create_organization():
    service = OrganizationService()
    try:
        data = UpdateOrganizationRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)

    try:
        org = service.create(data)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=400)

    return service.success(
        data=OrganizationDetailResponseSchema().dump(org),
        message="Organization created successfully.",
        status_code=201
    )

@organization_bp.route("/<id>", methods=["GET"])
@permission_required("organization.read")
def get_organization(id):
    service = OrganizationService()
    try:
        org_uid = uuid.UUID(str(id))
        org = service.get_by_id(org_uid)
    except ValueError:
        return service.error("Invalid organization ID format.", code="ERR_VALIDATION", status_code=400)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data=OrganizationDetailResponseSchema().dump(org),
        message="Organization retrieved successfully.",
    )

@organization_bp.route("/<id>", methods=["PUT"])
@permission_required("organization.update")
def update_organization(id):
    service = OrganizationService()
    try:
        org_uid = uuid.UUID(str(id))
        data = UpdateOrganizationRequestSchema().load(request.get_json(silent=True) or {})
    except ValueError:
        return service.error("Invalid organization ID format.", code="ERR_VALIDATION", status_code=400)
    except ValidationError as err:
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)

    try:
        org = service.update(org_uid, data)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=400)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data=OrganizationDetailResponseSchema().dump(org),
        message="Organization updated successfully.",
    )

@organization_bp.route("/<id>", methods=["DELETE"])
@permission_required("organization.update")
def delete_organization(id):
    service = OrganizationService()
    try:
        org_uid = uuid.UUID(str(id))
        service.delete(org_uid)
    except ValueError:
        return service.error("Invalid organization ID format.", code="ERR_VALIDATION", status_code=400)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        message="Organization deleted successfully."
    )
