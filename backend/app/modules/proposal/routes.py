import uuid
from flask import Blueprint, request
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity

from app.modules.auth.permissions import permission_required
from app.domain.exceptions import NotFoundException, ValidationException, BusinessException
from .schemas import (
    CreateProposalRequestSchema,
    UpdateProposalRequestSchema,
    FinalizeProposalRequestSchema,
    ProposalDetailResponseSchema,
    ProposalSummaryResponseSchema,
    ProposalVersionSummaryResponseSchema,
    SimpleLookupResponseSchema,
)
from .service import ProposalService, ProposalLookupService

proposal_bp = Blueprint("proposal", __name__)


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


def _get_context_team_member_id() -> uuid.UUID | None:
    """Helper to safely retrieve the team member ID of the authenticated user account context."""
    identity = get_jwt_identity()
    if not identity:
        return None
    try:
        from app.models import UserAccount
        from app.core.extensions import db
        user = db.session.get(UserAccount, uuid.UUID(str(identity)))
        return user.team_member_id if user else None
    except ValueError:
        return None


# ─────────────────────────────────────────────────────────────────
# Proposal CRUD Controllers
# ─────────────────────────────────────────────────────────────────

@proposal_bp.route("/proposals", methods=["POST"])
@permission_required("proposal.create")
def create_proposal():
    payload = request.get_json(silent=True) or {}
    raw_keys = set(payload.keys())
    try:
        data = CreateProposalRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = ProposalService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=422)

    context_id = _get_context_team_member_id()
    service = ProposalService()
    proposal = service.create_proposal(data, raw_keys, context_id)
    response_data = ProposalDetailResponseSchema().dump(proposal)
    return service.success(data=response_data, message="Proposal created successfully.", status_code=201)


@proposal_bp.route("/proposals/<uuid:id>", methods=["PUT"])
@permission_required("proposal.update")
def update_proposal(id):
    payload = request.get_json(silent=True) or {}
    raw_keys = set(payload.keys())
    try:
        data = UpdateProposalRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = ProposalService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=422)

    context_id = _get_context_team_member_id()
    service = ProposalService()
    proposal = service.update_proposal(id, data, raw_keys, context_id)
    response_data = ProposalDetailResponseSchema().dump(proposal)
    return service.success(data=response_data, message="Proposal updated successfully.", status_code=200)


@proposal_bp.route("/proposals/<uuid:id>/finalize", methods=["POST"])
@permission_required("proposal.finalize")
def finalize_proposal(id):
    payload = request.get_json(silent=True) or {}
    try:
        data = FinalizeProposalRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = ProposalService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=422)

    context_id = _get_context_team_member_id()
    service = ProposalService()
    proposal = service.finalize_proposal(id, data, context_id)
    response_data = ProposalDetailResponseSchema().dump(proposal)
    return service.success(data=response_data, message="Proposal finalized successfully.", status_code=200)


@proposal_bp.route("/proposals/<uuid:id>", methods=["DELETE"])
@permission_required("proposal.delete")
def delete_proposal(id):
    context_id = _get_context_team_member_id()
    service = ProposalService()
    service.soft_delete_proposal(id, context_id)
    return service.success(message="Proposal deleted successfully.", status_code=200)


@proposal_bp.route("/proposals/<uuid:id>", methods=["GET"])
@permission_required("proposal.read")
def get_proposal(id):
    service = ProposalService()
    proposal = service.get_proposal(id)
    response_data = ProposalDetailResponseSchema().dump(proposal)
    return service.success(data=response_data, message="Proposal retrieved successfully.", status_code=200)


@proposal_bp.route("/proposals", methods=["GET"])
@permission_required("proposal.read")
def list_proposals():
    # Parse pagination parameters
    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))
    except ValueError:
        page = 1
        page_size = 20

    lead_id_str = request.args.get("lead_id")
    lead_id = None
    if lead_id_str:
        try:
            lead_id = uuid.UUID(lead_id_str)
        except ValueError:
            service = ProposalService()
            return service.error("Invalid lead_id UUID format.", code="ERR_VALIDATION", status_code=422)

    status_code = request.args.get("status")
    is_final_str = request.args.get("is_final")
    is_final = None
    if is_final_str:
        is_final = is_final_str.lower() in ("true", "1")

    search = request.args.get("search")
    sort_by = request.args.get("sort_by", "created_at")
    sort_order = request.args.get("sort_order", "desc")

    service = ProposalService()
    paginated_result = service.list_proposals(
        page=page,
        page_size=page_size,
        lead_id=lead_id,
        status_code=status_code,
        is_final=is_final,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response_data = ProposalSummaryResponseSchema(many=True).dump(paginated_result.items)
    return service.success(
        data=response_data,
        meta={
            "page": paginated_result.page,
            "page_size": paginated_result.page_size,
            "total_records": paginated_result.total_records,
            "total_pages": paginated_result.total_pages,
        },
        message="Proposals retrieved successfully.",
        status_code=200,
    )


@proposal_bp.route("/leads/<uuid:lead_id>/proposals", methods=["GET"])
@permission_required("proposal.read")
def list_by_lead(lead_id):
    service = ProposalService()
    # Check if lead exists, to raise 404 appropriately
    service._validate_lead_eligibility(lead_id)
    proposals = service.list_by_lead(lead_id)
    response_data = ProposalVersionSummaryResponseSchema(many=True).dump(proposals)
    return service.success(data=response_data, message="Lead version history retrieved successfully.", status_code=200)


@proposal_bp.route("/crm/lookups/proposal_statuses", methods=["GET"])
@permission_required("proposal.read")
def list_proposal_statuses():
    service = ProposalLookupService()
    statuses = service.list_proposal_statuses()
    response_data = SimpleLookupResponseSchema(many=True).dump(statuses)
    return service.success(data=response_data, message="Proposal statuses retrieved successfully.", status_code=200)
