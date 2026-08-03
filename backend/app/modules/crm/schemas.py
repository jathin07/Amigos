from marshmallow import Schema, fields, validate, post_dump, validates_schema, ValidationError


class ContactPersonRequestSchema(Schema):
    """
    Schema validating contact person creation or update requests.
    """
    name = fields.String(required=True, validate=validate.Length(min=1, max=150))
    phone = fields.String(required=True, validate=validate.Length(min=5, max=20))
    email = fields.Email(allow_none=True)
    designation = fields.String(allow_none=True, validate=validate.Length(max=100))
    alternate_phone = fields.String(allow_none=True, validate=validate.Length(max=20))
    preferred_contact_method = fields.String(allow_none=True, validate=validate.Length(max=30))
    notes = fields.String(allow_none=True)
    is_primary = fields.Boolean(allow_none=True, load_default=False)
    organization_id = fields.UUID(allow_none=True)


class ContactPersonResponseSchema(Schema):
    """
    Schema serializing full contact person details.
    """
    id = fields.UUID()
    organization_id = fields.UUID(allow_none=True)
    name = fields.String()
    designation = fields.String(allow_none=True)
    phone = fields.String()
    alternate_phone = fields.String(allow_none=True)
    email = fields.String(allow_none=True)
    is_primary = fields.Boolean()
    preferred_contact_method = fields.String(allow_none=True)
    notes = fields.String(allow_none=True)
    is_active = fields.Boolean()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class SimpleLookupResponseSchema(Schema):
    """
    Simplified code/name lookups for responses.
    """
    id = fields.UUID()
    code = fields.String()
    name = fields.String()


class SimplePackageResponseSchema(Schema):
    """
    Simplified package response details.
    """
    id = fields.UUID()
    title = fields.String()


class SimpleContactResponseSchema(Schema):
    """
    Simplified contact person details.
    """
    id = fields.UUID()
    name = fields.String()
    phone = fields.String()
    email = fields.String(allow_none=True)


class LeadDestinationRequestSchema(Schema):
    """
    Destination payload attached to Lead request.
    """
    destination_id = fields.UUID(required=True)
    priority = fields.String(allow_none=True, validate=validate.Length(max=50))
    day_preference = fields.String(allow_none=True, validate=validate.Length(max=50))


class LeadDestinationResponseSchema(Schema):
    """
    Destination response nested inside Lead details.
    """
    id = fields.UUID()
    destination_id = fields.UUID()
    name = fields.Method("get_destination_name")
    priority = fields.String()
    day_preference = fields.String()

    def get_destination_name(self, obj):
        # Access destination table via lazy loaded relation or manual query
        # Because we will populate the backref or destination lookup
        if hasattr(obj, "destination") and obj.destination:
            return obj.destination.name
        return None


class CreateLeadRequestSchema(Schema):
    """
    Validates payload for creating a new Lead.
    """
    contact_person_id = fields.UUID(allow_none=True)
    contact_person = fields.Nested(ContactPersonRequestSchema, allow_none=True)
    lead_source_id = fields.UUID(required=True)
    organization_division_id = fields.UUID(allow_none=True)
    package_id = fields.UUID(allow_none=True)
    trip_type_id = fields.UUID(allow_none=True)
    priority_id = fields.UUID(allow_none=True)
    travel_start_date = fields.Date(allow_none=True)
    travel_end_date = fields.Date(allow_none=True)
    estimated_trip_days = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    estimated_trip_nights = fields.Integer(allow_none=True, validate=validate.Range(min=0))
    traveler_count = fields.Integer(load_default=1, validate=validate.Range(min=1))
    male_count = fields.Integer(allow_none=True, validate=validate.Range(min=0))
    female_count = fields.Integer(allow_none=True, validate=validate.Range(min=0))
    faculty_count = fields.Integer(allow_none=True, validate=validate.Range(min=0))
    budget = fields.Decimal(allow_none=True, validate=validate.Range(min=0))
    notes = fields.String(allow_none=True, validate=validate.Length(max=2000))
    expected_travel_date = fields.Date(allow_none=True)
    current_status_id = fields.UUID(allow_none=True)
    owner_team_member_id = fields.UUID(allow_none=True)
    destinations = fields.List(fields.Nested(LeadDestinationRequestSchema), load_default=list)

    @validates_schema
    def validate_contact(self, data, **kwargs):
        if not data.get("contact_person_id") and not data.get("contact_person"):
            raise ValidationError("Either contact_person_id or contact_person must be provided.", "contact_person")
        if data.get("travel_start_date") and data.get("travel_end_date"):
            if data["travel_end_date"] < data["travel_start_date"]:
                raise ValidationError("travel_end_date cannot be before travel_start_date.", "travel_end_date")


class UpdateLeadRequestSchema(Schema):
    """
    Validates payload for updating a Lead. Enforces optimistic locking version.
    """
    version = fields.Integer(required=True)
    contact_person_id = fields.UUID(allow_none=True)
    lead_source_id = fields.UUID(allow_none=True)
    organization_division_id = fields.UUID(allow_none=True)
    package_id = fields.UUID(allow_none=True)
    trip_type_id = fields.UUID(allow_none=True)
    priority_id = fields.UUID(allow_none=True)
    travel_start_date = fields.Date(allow_none=True)
    travel_end_date = fields.Date(allow_none=True)
    estimated_trip_days = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    estimated_trip_nights = fields.Integer(allow_none=True, validate=validate.Range(min=0))
    traveler_count = fields.Integer(validate=validate.Range(min=1))
    male_count = fields.Integer(allow_none=True, validate=validate.Range(min=0))
    female_count = fields.Integer(allow_none=True, validate=validate.Range(min=0))
    faculty_count = fields.Integer(allow_none=True, validate=validate.Range(min=0))
    budget = fields.Decimal(allow_none=True, validate=validate.Range(min=0))
    notes = fields.String(allow_none=True, validate=validate.Length(max=2000))
    expected_travel_date = fields.Date(allow_none=True)
    current_status_id = fields.UUID(allow_none=True)
    owner_team_member_id = fields.UUID(allow_none=True)
    destinations = fields.List(fields.Nested(LeadDestinationRequestSchema))
    lost_reason_id = fields.UUID(allow_none=True)
    lost_date = fields.Date(allow_none=True)
    assignment_reason = fields.String(allow_none=True, validate=validate.Length(max=500))

    @validates_schema
    def validate_dates(self, data, **kwargs):
        if data.get("travel_start_date") and data.get("travel_end_date"):
            if data["travel_end_date"] < data["travel_start_date"]:
                raise ValidationError("travel_end_date cannot be before travel_start_date.", "travel_end_date")


class LeadSummaryResponseSchema(Schema):
    """
    Serialized summary representation of a Lead (used in list views).
    """
    id = fields.UUID()
    lead_number = fields.String()
    contact_person = fields.Nested(SimpleContactResponseSchema)
    lead_source = fields.Nested(SimpleLookupResponseSchema)
    current_status = fields.Nested(SimpleLookupResponseSchema)
    priority = fields.Nested(SimpleLookupResponseSchema)
    travel_start_date = fields.Date()
    travel_end_date = fields.Date()
    traveler_count = fields.Integer()
    budget = fields.Decimal(as_string=True)
    owner_team_member_id = fields.UUID(allow_none=True)
    created_at = fields.DateTime()
    version = fields.Integer()


class AuditInfoSchema(Schema):
    """
    Serialized audit information.
    """
    created_at = fields.DateTime()
    created_by_team_member_id = fields.UUID(allow_none=True)
    updated_at = fields.DateTime()
    updated_by_team_member_id = fields.UUID(allow_none=True)


class LeadDetailResponseSchema(Schema):
    """
    Serialized complete detail representation of a Lead.
    """
    id = fields.UUID()
    lead_number = fields.String()
    contact_person = fields.Nested(ContactPersonResponseSchema)
    lead_source = fields.Nested(SimpleLookupResponseSchema)
    organization_division_id = fields.UUID(allow_none=True)
    package = fields.Nested(SimplePackageResponseSchema, allow_none=True)
    trip_type = fields.Nested(SimpleLookupResponseSchema, allow_none=True)
    priority = fields.Nested(SimpleLookupResponseSchema, allow_none=True)
    travel_start_date = fields.Date(allow_none=True)
    travel_end_date = fields.Date(allow_none=True)
    estimated_trip_days = fields.Integer(allow_none=True)
    estimated_trip_nights = fields.Integer(allow_none=True)
    traveler_count = fields.Integer()
    male_count = fields.Integer(allow_none=True)
    female_count = fields.Integer(allow_none=True)
    faculty_count = fields.Integer(allow_none=True)
    budget = fields.Decimal(as_string=True, allow_none=True)
    notes = fields.String(allow_none=True)
    current_status = fields.Nested(SimpleLookupResponseSchema)
    expected_travel_date = fields.Date(allow_none=True)
    lost_reason = fields.Nested(SimpleLookupResponseSchema, allow_none=True)
    lost_date = fields.Date(allow_none=True)
    owner_team_member_id = fields.UUID(allow_none=True)
    destinations = fields.List(fields.Nested(LeadDestinationResponseSchema), attribute="lead_destinations")
    version = fields.Integer()
    audit_info = fields.Method("get_audit_info")

    def get_audit_info(self, obj):
        return {
            "created_at": obj.created_at,
            "created_by_team_member_id": obj.created_by_team_member_id,
            "updated_at": obj.updated_at,
            "updated_by_team_member_id": obj.updated_by_team_member_id
        }


class AssignmentHistoryResponseSchema(Schema):
    """
    Serialized representation of an AssignmentHistory record.
    """
    id = fields.UUID()
    entity_type = fields.String()
    entity_id = fields.UUID()
    assignment_type = fields.String()
    previous_team_member = fields.Method("get_prev_member")
    new_team_member = fields.Method("get_new_member")
    reason = fields.String()
    effective_from = fields.DateTime()
    effective_to = fields.DateTime(allow_none=True)
    entity_status = fields.String()

    def get_prev_member(self, obj):
        if obj.previous_team_member:
            return {"id": str(obj.previous_team_member.id), "display_name": obj.previous_team_member.display_name}
        return {"id": "00000000-0000-0000-0000-000000000000", "display_name": "Unassigned"}

    def get_new_member(self, obj):
        if obj.new_team_member:
            return {"id": str(obj.new_team_member.id), "display_name": obj.new_team_member.display_name}
        return {"id": "00000000-0000-0000-0000-000000000000", "display_name": "Unassigned"}


class CRMActivityResponseSchema(Schema):
    """
    Schema serializing logged CRM interaction activities.
    """
    id = fields.UUID()
    lead_id = fields.UUID()
    activity_type = fields.Nested(SimpleLookupResponseSchema)
    activity_date = fields.DateTime()
    discussion_summary = fields.String()
    outcome = fields.String(allow_none=True)
    next_action = fields.String(allow_none=True)
    next_followup_date = fields.Date(allow_none=True)
    audit_info = fields.Method("get_audit_info")

    def get_audit_info(self, obj):
        return {
            "created_at": obj.created_at,
            "created_by_team_member_id": obj.created_by_team_member_id
        }


class FollowUpResponseSchema(Schema):
    """
    Schema serializing scheduled FollowUp reminders.
    """
    id = fields.UUID()
    lead_id = fields.UUID()
    followup_type = fields.Nested(SimpleLookupResponseSchema)
    scheduled_date = fields.DateTime()
    notes = fields.String(allow_none=True)
    is_completed = fields.Boolean()
    completed_at = fields.DateTime(allow_none=True)
    owner_team_member_id = fields.UUID()
    status = fields.Method("get_status")
    completion_notes = fields.Method("get_completion_notes")
    audit_info = fields.Method("get_audit_info")

    def get_status(self, obj):
        if getattr(obj, "is_deleted", False):
            return "cancelled"
        if obj.is_completed:
            return "completed"
        return "pending"

    def get_completion_notes(self, obj):
        import re
        if not obj.notes:
            return None
        match = re.search(r"\[Completed Notes\]:\s*(.*)", obj.notes, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def get_audit_info(self, obj):
        return {
            "created_at": obj.created_at,
            "created_by_team_member_id": obj.created_by_team_member_id
        }
