import uuid
from flask import Blueprint, request
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity

from app.modules.auth.permissions import permission_required
from app.domain.exceptions import NotFoundException, ValidationException, BusinessException
from .schemas import (
    ContactPersonRequestSchema,
    ContactPersonResponseSchema,
    CreateLeadRequestSchema,
    UpdateLeadRequestSchema,
    LeadSummaryResponseSchema,
    LeadDetailResponseSchema,
    SimpleLookupResponseSchema,
    AssignmentHistoryResponseSchema,
)
from .service import ContactService, CRMService, CRMActivityService, FollowUpService, CRMLookupService

crm_bp = Blueprint("crm", __name__)


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
    try:
        identity = get_jwt_identity()
    except RuntimeError:
        identity = None
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
# Contact Person Controllers
# ─────────────────────────────────────────────────────────────────

@crm_bp.route("/crm/contacts", methods=["POST"])
@permission_required("crm.create")
def create_contact():
    payload = request.get_json(silent=True) or {}
    try:
        data = ContactPersonRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = ContactService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=400)

    service = ContactService()
    contact = service.create_or_get_contact(data)
    response_data = ContactPersonResponseSchema().dump(contact)
    return service.success(data=response_data, message="Contact person processed successfully.", status_code=201)


@crm_bp.route("/crm/contacts", methods=["GET"])
@permission_required("crm.read")
def list_contacts():
    service = ContactService()
    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))
    except ValueError:
        return service.error("Page and page_size must be integers.", code="ERR_VALIDATION", status_code=400)

    search = request.args.get("search", "")

    result = service.list_contacts(page=page, page_size=page_size, search_query=search)
    meta = {
        "page": result.page,
        "page_size": result.page_size,
        "total_records": result.total_records,
        "total_pages": result.total_pages
    }
    return service.success(data=result.items, meta=meta, message="Contacts directory retrieved successfully.")


@crm_bp.route("/crm/contacts/<uuid:id>", methods=["GET"])
@permission_required("crm.read")
def get_contact(id):
    service = ContactService()
    contact = service.get_contact_by_id(id)
    response_data = ContactPersonResponseSchema().dump(contact)
    return service.success(data=response_data, message="Contact person details retrieved.")


@crm_bp.route("/crm/contacts/<uuid:id>", methods=["PUT"])
@permission_required("crm.update")
def update_contact(id):
    payload = request.get_json(silent=True) or {}
    try:
        data = ContactPersonRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = ContactService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=400)

    service = ContactService()
    contact = service.update_contact(id, data)
    response_data = ContactPersonResponseSchema().dump(contact)
    return service.success(data=response_data, message="Contact person updated successfully.")


# ─────────────────────────────────────────────────────────────────
# Lead Controllers
# ─────────────────────────────────────────────────────────────────

@crm_bp.route("/leads", methods=["GET"])
@permission_required("crm.read")
def list_leads():
    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))
    except ValueError:
        service = CRMService()
        return service.error("Page and page_size must be integers.", code="ERR_VALIDATION", status_code=400)

    search_query = request.args.get("q")
    sort_by = request.args.get("sort_by")
    sort_order = request.args.get("sort_order", "asc")

    filters = {}
    for key in ["current_status_id", "priority_id", "lead_source_id", "owner_team_member_id"]:
        val = request.args.get(key)
        if val:
            filters[key] = val

    filters["travel_start_date_gte"] = request.args.get("travel_start_date[gte]")
    filters["travel_start_date_lte"] = request.args.get("travel_start_date[lte]")

    service = CRMService()
    result = service.repository.paginate(
        page=page,
        page_size=page_size,
        search_query=search_query,
        sort_by=sort_by,
        sort_order=sort_order,
        **filters
    )

    response_data = LeadSummaryResponseSchema(many=True).dump(result.items)
    meta = {
        "page": result.page,
        "page_size": result.page_size,
        "total_records": result.total_records,
        "total_pages": result.total_pages
    }
    return service.success(data=response_data, meta=meta, message="Leads retrieved successfully.")


@crm_bp.route("/leads", methods=["POST"])
@permission_required("crm.create")
def create_lead():
    payload = request.get_json(silent=True) or {}
    try:
        data = CreateLeadRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = CRMService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=400)

    user_id = _get_context_team_member_id()

    service = CRMService()
    lead = service.create_lead(data, context_team_member_id=user_id)
    response_data = LeadDetailResponseSchema().dump(lead)
    return service.success(data=response_data, message="Lead created successfully.", status_code=201)


@crm_bp.route("/leads/<uuid:id>", methods=["GET"])
@permission_required("crm.read")
def get_lead(id):
    service = CRMService()
    lead = service.get_lead_by_id(id)
    response_data = LeadDetailResponseSchema().dump(lead)
    return service.success(data=response_data, message="Lead details retrieved.")


@crm_bp.route("/leads/<uuid:id>", methods=["PUT"])
@permission_required("crm.update")
def update_lead(id):
    payload = request.get_json(silent=True) or {}
    try:
        data = UpdateLeadRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = CRMService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=400)

    expected_version = data.get("version")
    user_id = _get_context_team_member_id()

    service = CRMService()
    try:
        lead = service.update_lead(id, data, expected_version=expected_version, context_team_member_id=user_id)
    except BusinessException as err:
        status_code = 409 if err.code == "ERR_OPTIMISTIC_LOCK" else 400
        return service.error(err.message, code=err.code, status_code=status_code)

    response_data = LeadDetailResponseSchema().dump(lead)
    return service.success(data=response_data, message="Lead updated successfully.")


@crm_bp.route("/leads/<uuid:id>", methods=["DELETE"])
@permission_required("crm.delete")
def delete_lead(id):
    user_id = _get_context_team_member_id()

    service = CRMService()
    service.soft_delete_lead(id, context_team_member_id=user_id)
    return service.success(message="Lead deleted successfully.")


@crm_bp.route("/leads/<uuid:id>/convert", methods=["POST"])
@permission_required("crm.convert")
def convert_lead(id):
    payload = request.get_json(silent=True) or {}
    user_id = _get_context_team_member_id()

    service = CRMService()
    booking = service.convert_lead_to_booking(id, payload, context_team_member_id=user_id)
    return service.success(data={"booking_id": str(booking.id), "booking_number": booking.booking_number}, message="Lead successfully converted to confirmed Booking.", status_code=201)


# ─────────────────────────────────────────────────────────────────
# CRM Activity Controllers
# ─────────────────────────────────────────────────────────────────

@crm_bp.route("/leads/<uuid:id>/activities", methods=["GET"])
@permission_required("crm.read")
def list_activities(id):
    service = CRMActivityService()
    activities = service.get_activities_by_lead(id)
    from .schemas import CRMActivityResponseSchema
    response_data = CRMActivityResponseSchema(many=True).dump(activities)
    return service.success(data=response_data, message="Activities retrieved successfully.")


@crm_bp.route("/leads/<uuid:id>/activities", methods=["POST"])
@permission_required("crm.create")
def log_activity(id):
    payload = request.get_json(silent=True) or {}
    
    if not payload.get("activity_type_id") or not payload.get("discussion_summary"):
        service = CRMActivityService()
        return service.error("activity_type_id and discussion_summary are required.", code="ERR_VALIDATION", status_code=400)

    user_id = _get_context_team_member_id()

    service = CRMActivityService()
    activity = service.log_activity(id, payload, context_team_member_id=user_id)
    from .schemas import CRMActivityResponseSchema
    response_data = CRMActivityResponseSchema().dump(activity)
    return service.success(data=response_data, message="Activity logged successfully.", status_code=201)


# ─────────────────────────────────────────────────────────────────
# Follow Up Controllers
# ─────────────────────────────────────────────────────────────────

@crm_bp.route("/leads/<uuid:id>/followups", methods=["GET"])
@permission_required("crm.read")
def list_followups(id):
    service = FollowUpService()
    followups = service.get_followups_by_lead(id)
    from .schemas import FollowUpResponseSchema
    response_data = FollowUpResponseSchema(many=True).dump(followups)
    return service.success(data=response_data, message="Follow-ups retrieved successfully.")


@crm_bp.route("/leads/<uuid:id>/followups", methods=["POST"])
@permission_required("crm.create")
def schedule_followup(id):
    payload = request.get_json(silent=True) or {}
    
    if not payload.get("followup_type_id") or not payload.get("scheduled_date"):
        service = FollowUpService()
        return service.error("followup_type_id and scheduled_date are required.", code="ERR_VALIDATION", status_code=400)

    try:
        from marshmallow import fields
        payload["scheduled_date"] = fields.DateTime().deserialize(payload["scheduled_date"])
    except Exception:
        service = FollowUpService()
        return service.error("Invalid scheduled_date ISO datetime format.", code="ERR_VALIDATION", status_code=400)

    user_id = _get_context_team_member_id()

    service = FollowUpService()
    followup = service.schedule_followup(id, payload, context_team_member_id=user_id)
    from .schemas import FollowUpResponseSchema
    response_data = FollowUpResponseSchema().dump(followup)
    return service.success(data=response_data, message="Follow-up scheduled successfully.", status_code=201)


@crm_bp.route("/leads/<uuid:id>/followups/<uuid:f_id>/complete", methods=["PUT"])
@permission_required("crm.update")
def complete_followup(id, f_id):
    payload = request.get_json(silent=True) or {}
    user_id = _get_context_team_member_id()

    service = FollowUpService()
    try:
        followup = service.complete_followup(id, f_id, payload, context_team_member_id=user_id)
    except BusinessException as err:
        return service.error(err.message, code=err.code, status_code=400)

    from .schemas import FollowUpResponseSchema
    response_data = FollowUpResponseSchema().dump(followup)
    return service.success(data=response_data, message="Follow-up marked completed.")


# ─────────────────────────────────────────────────────────────────
# Assignment History Controllers
# ─────────────────────────────────────────────────────────────────

@crm_bp.route("/leads/<uuid:id>/assignments", methods=["GET"])
@permission_required("crm.read")
def list_assignments(id):
    service = CRMService()
    histories = service.assign_repo.get_assignment_history(id)
    response_data = AssignmentHistoryResponseSchema(many=True).dump(histories)
    return service.success(data=response_data, message="Assignment histories retrieved successfully.")


# ─────────────────────────────────────────────────────────────────
# Unified Lookups Controllers
# ─────────────────────────────────────────────────────────────────

@crm_bp.route("/crm/lookups/<string:lookup_type>", methods=["GET"])
@permission_required("crm.read")
def list_lookups(lookup_type):
    service = CRMLookupService()
    try:
        items = service.list_lookups(lookup_type)
    except NotFoundException as err:
        return service.error(err.message, code="ERR_NOT_FOUND", status_code=404)
        
    response_data = SimpleLookupResponseSchema(many=True).dump(items)
    return service.success(data=response_data, message=f"Lookups for '{lookup_type}' retrieved successfully.")
