from flask import Blueprint, request
from marshmallow import ValidationError

from app.modules.auth.permissions import permission_required
from app.domain.exceptions import BusinessException, NotFoundException
from .schemas import (
    CreateTeamMemberRequestSchema,
    UpdateTeamMemberRequestSchema,
    TeamMemberSummaryResponseSchema,
    TeamMemberDetailResponseSchema,
)
from .service import TeamService

team_bp = Blueprint("team", __name__)


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


@team_bp.route("", methods=["GET"])
@permission_required("team.read")
def list_team_members():
    service = TeamService()
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    search = request.args.get("search", None)
    sort_by = request.args.get("sort_by", "created_at")
    sort_order = request.args.get("sort_order", "desc")

    is_active_raw = request.args.get("is_active")
    is_active = None
    if is_active_raw is not None:
        is_active = is_active_raw.lower() == "true"

    department_id = request.args.get("department_id", None)
    role_id = request.args.get("role_id", None)
    reporting_manager_id = request.args.get("reporting_manager_id", None)
    employment_status = request.args.get("employment_status", None)

    filters = {}
    if is_active is not None:
        filters["is_active"] = is_active
    if department_id:
        filters["department_id"] = department_id
    if role_id:
        filters["role_id"] = role_id
    if reporting_manager_id:
        filters["reporting_manager_id"] = reporting_manager_id
    if employment_status:
        filters["employment_status"] = employment_status

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
            "items": TeamMemberSummaryResponseSchema(many=True).dump(result.items),
            "pagination": {
                "page": result.page,
                "page_size": result.page_size,
                "total_records": result.total_records,
                "total_pages": result.total_pages,
            },
        },
        message="Team members retrieved successfully.",
    )


@team_bp.route("/<string:member_id>", methods=["GET"])
@permission_required("team.read")
def get_team_member(member_id):
    service = TeamService()
    try:
        member = service.get(member_id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data=TeamMemberDetailResponseSchema().dump(member),
        message="Team member retrieved successfully.",
    )


@team_bp.route("", methods=["POST"])
@permission_required("team.create")
def create_team_member():
    service = TeamService()
    try:
        data = CreateTeamMemberRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error(
            "Validation failed.",
            code="ERR_VALIDATION",
            errors=_flatten_errors(err.messages),
            status_code=400,
        )

    try:
        member = service.create(data)
    except BusinessException as err:
        status_code = 409 if err.code in ("ERR_DUPLICATE_EMPLOYEE_CODE", "ERR_DUPLICATE_EMAIL") else 400
        return service.error(err.message, code=err.code, status_code=status_code)

    return service.success(
        data=TeamMemberDetailResponseSchema().dump(member),
        message="Team member created successfully.",
        status_code=201,
    )


@team_bp.route("/<string:member_id>", methods=["PUT"])
@permission_required("team.update")
def update_team_member(member_id):
    service = TeamService()
    try:
        data = UpdateTeamMemberRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return service.error(
            "Validation failed.",
            code="ERR_VALIDATION",
            errors=_flatten_errors(err.messages),
            status_code=400,
        )

    try:
        member = service.update(member_id, data)
    except BusinessException as err:
        status_code = 409 if err.code in ("ERR_DUPLICATE_EMPLOYEE_CODE", "ERR_DUPLICATE_EMAIL") else 400
        return service.error(err.message, code=err.code, status_code=status_code)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)

    return service.success(
        data=TeamMemberDetailResponseSchema().dump(member),
        message="Team member updated successfully.",
    )


@team_bp.route("/<string:member_id>", methods=["DELETE"])
@permission_required("team.delete")
def delete_team_member(member_id):
    service = TeamService()
    try:
        service.delete(member_id)
    except NotFoundException as err:
        return service.error(err.message, code=err.code, status_code=404)
    except BusinessException as err:
        status_code = getattr(err, "status_code", 409)
        return service.error(err.message, code=err.code, status_code=status_code)

    return service.success(
        message="Team member deleted successfully.",
    )
