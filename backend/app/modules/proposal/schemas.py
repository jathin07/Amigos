from marshmallow import Schema, fields, validate, validates_schema, ValidationError, post_dump


# ---------------------------------------------------------------------------
# Shared / Reusable
# ---------------------------------------------------------------------------

class SimpleLookupResponseSchema(Schema):
    """Standard code/name lookup embedded in responses."""
    id = fields.UUID()
    code = fields.String()
    name = fields.String()


class AuditInfoSchema(Schema):
    """Standard audit fields embedded in all response DTOs."""
    created_at = fields.DateTime(allow_none=True)
    created_by_team_member_id = fields.UUID(allow_none=True)
    updated_at = fields.DateTime(allow_none=True)
    updated_by_team_member_id = fields.UUID(allow_none=True)


# ---------------------------------------------------------------------------
# Destination nested schemas
# ---------------------------------------------------------------------------

class ProposalDestinationRequestSchema(Schema):
    """
    Validates a single destination entry on create or update.
    Used inside CreateProposalRequestSchema and UpdateProposalRequestSchema.
    """
    destination_id = fields.UUID(required=True)
    day_order      = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    sequence_no    = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    overnight_stay = fields.Boolean(load_default=False)
    day_title      = fields.String(allow_none=True, validate=validate.Length(max=150))
    travel_time    = fields.String(allow_none=True, validate=validate.Length(max=100))
    travel_mode    = fields.String(allow_none=True, validate=validate.Length(max=100))
    distance       = fields.Decimal(allow_none=True, places=2)
    notes          = fields.String(allow_none=True)


class ProposalDestinationResponseSchema(Schema):
    """
    Serializes a ProposalDestination child entity.
    Resolves destination_name from the relationship.
    """
    id               = fields.UUID()
    destination_id   = fields.UUID()
    destination_name = fields.Method("get_destination_name")
    day_order        = fields.Integer(allow_none=True)
    sequence_no      = fields.Integer(allow_none=True)
    overnight_stay   = fields.Boolean()
    day_title        = fields.String(allow_none=True)
    travel_time      = fields.String(allow_none=True)
    travel_mode      = fields.String(allow_none=True)
    distance         = fields.Decimal(allow_none=True, places=2, as_string=True)
    notes            = fields.String(allow_none=True)

    def get_destination_name(self, obj) -> str | None:
        if obj.destination:
            return obj.destination.name
        return None


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class CreateProposalRequestSchema(Schema):
    """
    Validates the create-proposal request body.
    All financial fields use Decimal for precision.
    """
    lead_id              = fields.UUID(required=True)
    proposal_title       = fields.String(required=True, validate=validate.Length(min=1, max=200))
    price_per_person     = fields.Decimal(allow_none=True, places=2)
    total_amount         = fields.Decimal(allow_none=True, places=2)
    status_id            = fields.UUID(allow_none=True)
    valid_until          = fields.Date(allow_none=True)
    revision_reason      = fields.String(allow_none=True, validate=validate.Length(max=1000))
    internal_notes       = fields.String(allow_none=True, validate=validate.Length(max=2000))
    structured_itinerary = fields.Dict(allow_none=True)
    destinations         = fields.List(
        fields.Nested(ProposalDestinationRequestSchema),
        allow_none=True,
        load_default=None,
    )


class UpdateProposalRequestSchema(Schema):
    """
    Validates the update-proposal request body.
    row_version is required for optimistic locking.
    All other fields are optional.
    """
    row_version          = fields.Integer(required=True)
    proposal_title       = fields.String(allow_none=True, validate=validate.Length(min=1, max=200))
    price_per_person     = fields.Decimal(allow_none=True, places=2)
    total_amount         = fields.Decimal(allow_none=True, places=2)
    status_id            = fields.UUID(allow_none=True)
    valid_until          = fields.Date(allow_none=True)
    revision_reason      = fields.String(allow_none=True, validate=validate.Length(max=1000))
    internal_notes       = fields.String(allow_none=True, validate=validate.Length(max=2000))
    structured_itinerary = fields.Dict(allow_none=True)
    destinations         = fields.List(
        fields.Nested(ProposalDestinationRequestSchema),
        allow_none=True,
        load_default=None,
    )


class FinalizeProposalRequestSchema(Schema):
    """
    Validates the finalize-proposal request body.
    row_version is required for optimistic locking.
    """
    row_version                 = fields.Integer(required=True)
    approved_by_team_member_id  = fields.UUID(allow_none=True)
    approved_date               = fields.Date(allow_none=True)


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class ProposalSummaryResponseSchema(Schema):
    """
    Compact proposal record for paginated list responses.
    """
    id             = fields.UUID()
    lead_id        = fields.UUID()
    version        = fields.Integer()
    proposal_title = fields.String()
    price_per_person = fields.Decimal(allow_none=True, places=2, as_string=True)
    total_amount   = fields.Decimal(allow_none=True, places=2, as_string=True)
    is_final       = fields.Boolean()
    status         = fields.Method("get_status")
    valid_until    = fields.Date(allow_none=True)
    sent_date      = fields.Date(allow_none=True)
    approved_date  = fields.Date(allow_none=True)
    row_version    = fields.Integer()
    audit_info     = fields.Method("get_audit_info")

    def get_status(self, obj):
        if obj.status:
            return {"id": str(obj.status.id), "code": obj.status.code, "name": obj.status.name}
        return None

    def get_audit_info(self, obj):
        return {
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "created_by_team_member_id": str(obj.created_by_team_member_id) if obj.created_by_team_member_id else None,
        }


class ProposalDetailResponseSchema(Schema):
    """
    Full proposal record including destinations, itinerary, and all metadata.
    Returned on create, update, finalize, and single-GET requests.
    """
    id                          = fields.UUID()
    lead_id                     = fields.UUID()
    version                     = fields.Integer()
    proposal_title              = fields.String()
    price_per_person            = fields.Decimal(allow_none=True, places=2, as_string=True)
    total_amount                = fields.Decimal(allow_none=True, places=2, as_string=True)
    is_final                    = fields.Boolean()
    status                      = fields.Method("get_status")
    valid_until                 = fields.Date(allow_none=True)
    sent_date                   = fields.Date(allow_none=True)
    approved_date               = fields.Date(allow_none=True)
    approved_by_team_member_id  = fields.UUID(allow_none=True)
    revision_reason             = fields.String(allow_none=True)
    internal_notes              = fields.String(allow_none=True)
    pdf_url                     = fields.String(allow_none=True)
    structured_itinerary        = fields.Dict(allow_none=True)
    destinations                = fields.Method("get_destinations")
    row_version                 = fields.Integer()
    audit_info                  = fields.Method("get_audit_info")

    def get_status(self, obj):
        if obj.status:
            return {"id": str(obj.status.id), "code": obj.status.code, "name": obj.status.name}
        return None

    def get_destinations(self, obj):
        if not obj.destinations:
            return []
        return ProposalDestinationResponseSchema(many=True).dump(obj.destinations)

    def get_audit_info(self, obj):
        return {
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "created_by_team_member_id": str(obj.created_by_team_member_id) if obj.created_by_team_member_id else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
            "updated_by_team_member_id": str(obj.updated_by_team_member_id) if obj.updated_by_team_member_id else None,
        }


class ProposalVersionSummaryResponseSchema(Schema):
    """
    Compact version-history item returned in list-by-lead responses.
    """
    id             = fields.UUID()
    version        = fields.Integer()
    proposal_title = fields.String()
    total_amount   = fields.Decimal(allow_none=True, places=2, as_string=True)
    status         = fields.Method("get_status")
    is_final       = fields.Boolean()
    created_at     = fields.DateTime(allow_none=True)

    def get_status(self, obj):
        if obj.status:
            return {"code": obj.status.code, "name": obj.status.name}
        return None
