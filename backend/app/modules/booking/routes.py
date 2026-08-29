import uuid
from flask import Blueprint, request
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity

from app.modules.auth.permissions import permission_required
from app.domain.exceptions import NotFoundException, ValidationException, BusinessException
from .schemas import (
    CreateBookingRequestSchema,
    UpdateBookingRequestSchema,
    ConfirmBookingRequestSchema,
    CancelBookingRequestSchema,
    TravelerRequestSchema,
    TravelerResponseSchema,
    DocumentResponseSchema,
    BookingSummaryResponseSchema,
    BookingDetailResponseSchema,
    BookingTimelineResponseSchema,
    SimpleLookupResponseSchema,
)
from .service import BookingService, BookingLookupService

booking_bp = Blueprint("booking", __name__)


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
    """Safely retrieves current user team_member_id context."""
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
# Booking CRUD Routes
# ─────────────────────────────────────────────────────────────────

@booking_bp.route("/bookings", methods=["POST"])
@permission_required("booking.create")
def create_booking():
    payload = request.get_json(silent=True) or {}
    try:
        data = CreateBookingRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = BookingService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=422)

    context_id = _get_context_team_member_id()
    service = BookingService()
    booking = service.create_booking(data, context_id)
    response_data = BookingDetailResponseSchema().dump(booking)
    return service.success(data=response_data, message="Booking draft created successfully.", status_code=201)


@booking_bp.route("/bookings", methods=["GET"])
@permission_required("booking.read")
def list_bookings():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    search = request.args.get("q")
    sort_by = request.args.get("sort")
    sort_order = "asc"
    
    if sort_by and sort_by.startswith("-"):
        sort_order = "desc"
        sort_by = sort_by[1:]

    filters = {}
    for param in ["booking_status_id", "booking_type_id", "booking_source_id", "customer_id", "trip_coordinator_team_member_id"]:
        val = request.args.get(param)
        if val:
            filters[param] = val

    service = BookingService()
    paginated_res = service.repository.paginate(
        page=page,
        page_size=limit,
        search_query=search,
        sort_by=sort_by,
        sort_order=sort_order,
        **filters
    )
    
    items_data = BookingSummaryResponseSchema(many=True).dump(paginated_res.items)
    
    meta = {
        "page": paginated_res.page,
        "limit": paginated_res.page_size,
        "total": paginated_res.total_records,
        "pages": paginated_res.total_pages
    }
    
    return service.success(data=items_data, meta=meta, message="Bookings list retrieved.")


@booking_bp.route("/bookings/<uuid:id>", methods=["GET"])
@permission_required("booking.read")
def get_booking(id):
    service = BookingService()
    booking = service.repository.get_details(id)
    if not booking:
        raise NotFoundException("Booking not found.")
    
    response_data = BookingDetailResponseSchema().dump(booking)
    return service.success(data=response_data, message="Booking details retrieved.")


@booking_bp.route("/bookings/<uuid:id>", methods=["PUT"])
@permission_required("booking.update")
def update_booking(id):
    payload = request.get_json(silent=True) or {}
    try:
        data = UpdateBookingRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = BookingService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=422)

    context_id = _get_context_team_member_id()
    service = BookingService()
    booking = service.update_booking(id, data, context_id)
    response_data = BookingDetailResponseSchema().dump(booking)
    return service.success(data=response_data, message="Booking updated successfully.")


# ─────────────────────────────────────────────────────────────────
# Workflow Transition Commands
# ─────────────────────────────────────────────────────────────────

@booking_bp.route("/bookings/<uuid:id>/confirm", methods=["POST"])
@permission_required("booking.confirm")
def confirm_booking(id):
    payload = request.get_json(silent=True) or {}
    try:
        data = ConfirmBookingRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = BookingService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=422)

    context_id = _get_context_team_member_id()
    service = BookingService()
    booking = service.confirm_booking(id, data, context_id)
    response_data = BookingDetailResponseSchema().dump(booking)
    return service.success(data=response_data, message="Booking confirmed successfully.")


@booking_bp.route("/bookings/<uuid:id>/cancel", methods=["POST"])
@permission_required("booking.cancel")
def cancel_booking(id):
    payload = request.get_json(silent=True) or {}
    try:
        data = CancelBookingRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = BookingService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=422)

    context_id = _get_context_team_member_id()
    service = BookingService()
    booking = service.cancel_booking(id, data, context_id)
    response_data = BookingDetailResponseSchema().dump(booking)
    return service.success(data=response_data, message="Booking cancelled successfully.")


@booking_bp.route("/bookings/<uuid:id>/status", methods=["POST"])
@permission_required("booking.update")
def update_booking_status(id):
    payload = request.get_json(silent=True) or {}
    target_status = payload.get("status_code")
    if not target_status:
        service = BookingService()
        return service.error("status_code is required.", code="ERR_VALIDATION", status_code=422)

    notes = payload.get("notes")
    context_id = _get_context_team_member_id()
    service = BookingService()
    booking = service.update_booking_status(id, target_status, notes=notes, context_team_member_id=context_id)
    response_data = BookingDetailResponseSchema().dump(booking)
    return service.success(data=response_data, message=f"Booking status updated to {target_status}.")


# ─────────────────────────────────────────────────────────────────
# Nested Traveler Manifest Endpoints
# ─────────────────────────────────────────────────────────────────

@booking_bp.route("/bookings/<uuid:id>/travelers", methods=["GET"])
@permission_required("booking.read")
def list_travelers(id):
    service = BookingService()
    booking = service.repository.get_details(id)
    if not booking:
        raise NotFoundException("Booking not found.")
    
    response_data = TravelerResponseSchema(many=True).dump(booking.travelers)
    return service.success(data=response_data, message="Traveler list retrieved.")


@booking_bp.route("/bookings/<uuid:id>/travelers", methods=["POST"])
@permission_required("booking.update")
def add_traveler(id):
    payload = request.get_json(silent=True) or {}
    try:
        data = TravelerRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = BookingService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=422)

    context_id = _get_context_team_member_id()
    service = BookingService()
    traveler = service.add_traveler(id, data, context_id)
    response_data = TravelerResponseSchema().dump(traveler)
    return service.success(data=response_data, message="Traveler added successfully.", status_code=201)


@booking_bp.route("/bookings/<uuid:id>/travelers/<uuid:traveler_id>", methods=["PUT"])
@permission_required("booking.update")
def update_traveler(id, traveler_id):
    payload = request.get_json(silent=True) or {}
    try:
        data = TravelerRequestSchema().load(payload)
    except ValidationError as err:
        flat = _flatten_errors(err.messages)
        service = BookingService()
        return service.error("Validation failed.", code="ERR_VALIDATION", errors=flat, status_code=422)

    context_id = _get_context_team_member_id()
    service = BookingService()
    traveler = service.update_traveler(id, traveler_id, data, context_id)
    response_data = TravelerResponseSchema().dump(traveler)
    return service.success(data=response_data, message="Traveler updated successfully.")


@booking_bp.route("/bookings/<uuid:id>/travelers/<uuid:traveler_id>", methods=["DELETE"])
@permission_required("booking.update")
def delete_traveler(id, traveler_id):
    context_id = _get_context_team_member_id()
    service = BookingService()
    service.delete_traveler(id, traveler_id, context_id)
    return "", 204


# ─────────────────────────────────────────────────────────────────
# Nested Document Attachment Endpoints
# ─────────────────────────────────────────────────────────────────

@booking_bp.route("/bookings/<uuid:id>/documents", methods=["GET"])
@permission_required("booking.read")
def list_documents(id):
    service = BookingService()
    booking = service.repository.get_details(id)
    if not booking:
        raise NotFoundException("Booking not found.")
    
    response_data = DocumentResponseSchema(many=True).dump(booking.documents)
    return service.success(data=response_data, message="Documents list retrieved.")


@booking_bp.route("/bookings/<uuid:id>/documents", methods=["POST"])
@permission_required("booking.update")
def add_document(id):
    payload = request.get_json(silent=True) or {}
    # Basic structural check
    if "file_name" not in payload or "file_url" not in payload:
        service = BookingService()
        return service.error("file_name and file_url are required.", code="ERR_VALIDATION", status_code=422)

    context_id = _get_context_team_member_id()
    service = BookingService()
    doc = service.add_document(id, payload, context_id)
    response_data = DocumentResponseSchema().dump(doc)
    return service.success(data=response_data, message="Document registered successfully.", status_code=201)


@booking_bp.route("/bookings/<uuid:id>/documents/<uuid:document_id>", methods=["DELETE"])
@permission_required("booking.update")
def delete_document(id, document_id):
    context_id = _get_context_team_member_id()
    service = BookingService()
    service.delete_document(id, document_id, context_id)
    return "", 204


# ─────────────────────────────────────────────────────────────────
# Booking Timeline Audit History
# ─────────────────────────────────────────────────────────────────

@booking_bp.route("/bookings/<uuid:id>/timeline", methods=["GET"])
@permission_required("booking.read")
def get_timeline(id):
    service = BookingService()
    booking = service.repository.get_details(id)
    if not booking:
        raise NotFoundException("Booking not found.")
    
    response_data = BookingTimelineResponseSchema().dump(booking)
    return service.success(data=response_data, message="Booking timeline retrieved.")


# ─────────────────────────────────────────────────────────────────
# Lookup Dropdowns
# ─────────────────────────────────────────────────────────────────

@booking_bp.route("/lookups/booking-statuses", methods=["GET"])
def lookup_booking_statuses():
    service = BookingLookupService()
    items = service.get_booking_statuses()
    response_data = SimpleLookupResponseSchema(many=True).dump(items)
    return service.success(data=response_data)


@booking_bp.route("/lookups/booking-sources", methods=["GET"])
def lookup_booking_sources():
    service = BookingLookupService()
    items = service.get_booking_sources()
    response_data = SimpleLookupResponseSchema(many=True).dump(items)
    return service.success(data=response_data)


@booking_bp.route("/lookups/booking-types", methods=["GET"])
def lookup_booking_types():
    service = BookingLookupService()
    items = service.get_booking_types()
    response_data = SimpleLookupResponseSchema(many=True).dump(items)
    return service.success(data=response_data)
