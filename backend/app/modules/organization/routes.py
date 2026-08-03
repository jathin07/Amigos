from flask import Blueprint, request
from marshmallow import ValidationError

from app.modules.auth.permissions import permission_required
from app.domain.exceptions import BusinessException, NotFoundException
from .schemas import (
    UpdateOrganizationRequestSchema,
    OrganizationDetailResponseSchema,
)
from .service import OrganizationService

organization_bp = Blueprint("organization", __name__)


def _flatten_errors(messages: dict) -> list[dict]:
    errors = []
    for field, msgs in messages.items():
        # Handle dict errors nested in lists/objects
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


@organization_bp.route("", methods=["GET"])
@permission_required("organization.read")
def get_organization():
    service = OrganizationService()
    try:
        org = service.get_active()
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data=OrganizationDetailResponseSchema().dump(org),
        message="Organization retrieved successfully.",
    )


@organization_bp.route("", methods=["PUT"])
@permission_required("organization.update")
def update_organization():
    service = OrganizationService()
    try:
        data = UpdateOrganizationRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error(
            "Validation failed.",
            code="ERR_VALIDATION",
            errors=_flatten_errors(err.messages),
            status_code=400,
        )

    try:
        org = service.update_active(data)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=400)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data=OrganizationDetailResponseSchema().dump(org),
        message="Organization updated successfully.",
    )
