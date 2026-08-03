from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class SimpleLookupResponseSchema(Schema):
    """Standard code/name lookup embedded in responses."""
    id = fields.UUID()
    code = fields.String()
    name = fields.String()


class AuditInfoSchema(Schema):
    """Standard audit fields embedded in response DTOs."""
    created_at = fields.DateTime(attribute="created_at", allow_none=True)
    created_by = fields.UUID(attribute="created_by_team_member_id", allow_none=True)
    updated_at = fields.DateTime(attribute="updated_at", allow_none=True)
    updated_by = fields.UUID(attribute="updated_by_team_member_id", allow_none=True)


class TravelerRequestSchema(Schema):
    """Validates traveler manifest data during request processing."""
    name = fields.String(required=True, validate=validate.Length(min=1, max=150))
    age = fields.Integer(allow_none=True, validate=validate.Range(min=0, max=120))
    gender = fields.String(allow_none=True, validate=validate.Length(max=20))
    id_proof_type = fields.String(allow_none=True, validate=validate.Length(max=50))
    id_proof_number = fields.String(allow_none=True, validate=validate.Length(max=100))
    emergency_contact = fields.String(allow_none=True, validate=validate.Length(max=20))
    special_requirements = fields.String(allow_none=True, validate=validate.Length(max=1000))
    is_group_leader = fields.Boolean(load_default=False)

    @validates_schema
    def validate_id_proof(self, data, **kwargs):
        id_type = data.get("id_proof_type")
        id_num = data.get("id_proof_number")
        if id_type and not id_num:
            raise ValidationError("ID proof number is required when ID proof type is provided.", "id_proof_number")
        if id_num and not id_type:
            raise ValidationError("ID proof type is required when ID proof number is provided.", "id_proof_type")


class InstallmentRequestSchema(Schema):
    """Validates a single payment schedule installment request."""
    installment_no = fields.Integer(required=True, validate=validate.Range(min=1))
    percentage = fields.Decimal(required=True, validate=validate.Range(min=0.01, max=100.00), places=2)
    due_date = fields.Date(required=True)
    remarks = fields.String(allow_none=True, validate=validate.Length(max=500))


class CreateBookingRequestSchema(Schema):
    """Validates booking creation payload."""
    proposal_id = fields.UUID(required=True)
    entry_mode = fields.String(load_default="NORMAL", validate=validate.OneOf(["NORMAL", "HISTORICAL"]))
    group_name = fields.String(allow_none=True, validate=validate.Length(max=200))
    travelers = fields.List(fields.Nested(TravelerRequestSchema), required=True, validate=validate.Length(min=1))
    installments = fields.List(fields.Nested(InstallmentRequestSchema), required=True, validate=validate.Length(min=1))


class UpdateBookingRequestSchema(Schema):
    """Validates booking update payload."""
    row_version = fields.Integer(required=True)
    group_name = fields.String(allow_none=True, validate=validate.Length(max=200))
    internal_notes = fields.String(allow_none=True, validate=validate.Length(max=1000))


class ConfirmBookingRequestSchema(Schema):
    """Validates booking confirmation payload."""
    row_version = fields.Integer(required=True)
    trip_coordinator_team_member_id = fields.UUID(required=True)
    notes = fields.String(allow_none=True, validate=validate.Length(max=500))


class CancelBookingRequestSchema(Schema):
    """Validates booking cancellation request payload."""
    row_version = fields.Integer(required=True)
    cancellation_reason = fields.String(required=True, validate=validate.Length(min=5, max=1000))


class TravelerResponseSchema(Schema):
    """Serializes a Traveler child entity."""
    id = fields.UUID()
    name = fields.String()
    age = fields.Integer()
    gender = fields.String()
    id_proof_type = fields.String()
    id_proof_number = fields.String()
    emergency_contact = fields.String()
    special_requirements = fields.String()
    is_group_leader = fields.Boolean()


class PaymentScheduleResponseSchema(Schema):
    """Serializes a PaymentSchedule child entity."""
    id = fields.UUID()
    installment_no = fields.Integer()
    due_date = fields.Date()
    percentage = fields.Decimal(places=2, as_string=True)
    amount = fields.Decimal(places=2, as_string=True)
    status = fields.Method("get_payment_status")
    remarks = fields.String()

    def get_payment_status(self, obj) -> str:
        if obj.payment_status:
            return obj.payment_status.code
        return "UNPAID"


class DocumentResponseSchema(Schema):
    """Serializes a Document attachment child entity."""
    id = fields.UUID()
    document_type = fields.Nested(SimpleLookupResponseSchema)
    file_name = fields.String()
    file_url = fields.String()
    uploaded_at = fields.DateTime()


class BookingSummaryResponseSchema(Schema):
    """Serializes lightweight booking summary record."""
    id = fields.UUID()
    booking_number = fields.String()
    group_name = fields.String()
    booking_date = fields.Date()
    trip_start_date = fields.Date()
    trip_end_date = fields.Date()
    total_travelers = fields.Integer()
    total_amount = fields.Decimal(places=2, as_string=True)
    status = fields.Nested(SimpleLookupResponseSchema)
    created_at = fields.DateTime(attribute="booking_created_at")


class BookingDetailResponseSchema(Schema):
    """Serializes comprehensive detailed booking record."""
    id = fields.UUID()
    booking_number = fields.String()
    row_version = fields.Integer()
    entry_mode = fields.String()
    group_name = fields.String()
    booking_date = fields.Date()
    trip_start_date = fields.Date()
    trip_end_date = fields.Date()
    total_travelers = fields.Integer()
    total_amount = fields.Decimal(places=2, as_string=True)
    proposal_version_id = fields.UUID()
    lead_id = fields.UUID()
    customer_id = fields.UUID()
    contact_person_id = fields.UUID()
    status = fields.Nested(SimpleLookupResponseSchema)
    trip_coordinator = fields.Method("get_trip_coordinator")
    snapshots = fields.Method("get_snapshots")
    travelers = fields.List(fields.Nested(TravelerResponseSchema))
    payment_schedule = fields.Nested(PaymentScheduleResponseSchema, attribute="payment_schedules", many=True)
    audit = fields.Nested(AuditInfoSchema, attribute="self")

    def get_trip_coordinator(self, obj) -> dict | None:
        if obj.trip_coordinator:
            return {
                "id": str(obj.trip_coordinator.id),
                "display_name": obj.trip_coordinator.display_name or obj.trip_coordinator.name
            }
        return None

    def get_snapshots(self, obj) -> dict:
        return {
            "package_name": obj.package_name_snapshot,
            "organization_name": obj.organization_name_snapshot,
            "contact_person_name": obj.contact_person_snapshot,
            "trip_name": obj.trip_name_snapshot
        }


class BookingTimelineEventResponseSchema(Schema):
    """Serializes a single event on the Booking status history timeline."""
    id = fields.UUID()
    from_status = fields.Nested(SimpleLookupResponseSchema)
    to_status = fields.Nested(SimpleLookupResponseSchema)
    changed_by = fields.Method("get_changed_by")
    changed_at = fields.DateTime(attribute="created_at")
    notes = fields.String()

    def get_changed_by(self, obj) -> dict | None:
        if obj.changed_by:
            return {
                "id": str(obj.changed_by.id),
                "display_name": obj.changed_by.display_name or obj.changed_by.name
            }
        return None


class BookingTimelineResponseSchema(Schema):
    """Serializes unified timeline events array."""
    booking_id = fields.UUID()
    timeline_events = fields.List(fields.Nested(BookingTimelineEventResponseSchema), attribute="status_history")
