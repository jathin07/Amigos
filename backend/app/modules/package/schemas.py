from decimal import Decimal
from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load


# ---------------------------------------------------------------------------
# Nested request schemas
# ---------------------------------------------------------------------------

class PackageHighlightRequestSchema(Schema):
    highlight_text = fields.String(required=True, validate=validate.Length(min=1))
    display_order = fields.Integer(load_default=None, allow_none=True, validate=validate.Range(min=1))

    @pre_load
    def strip_text(self, data, **kwargs):
        if "highlight_text" in data and isinstance(data["highlight_text"], str):
            data["highlight_text"] = data["highlight_text"].strip()
        return data

    @validates("highlight_text")
    def validate_highlight_text(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Highlight text cannot be blank.")


class PackageInclusionRequestSchema(Schema):
    """
    display_order accepted for forward-compatibility but NOT persisted:
    package_inclusions table does not have this column yet.
    """
    inclusion_text = fields.String(required=True, validate=validate.Length(min=1))
    display_order = fields.Integer(load_default=None, allow_none=True, validate=validate.Range(min=1))

    @pre_load
    def strip_text(self, data, **kwargs):
        if "inclusion_text" in data and isinstance(data["inclusion_text"], str):
            data["inclusion_text"] = data["inclusion_text"].strip()
        return data

    @validates("inclusion_text")
    def validate_inclusion_text(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Inclusion text cannot be blank.")


class PackageExclusionRequestSchema(Schema):
    """
    display_order accepted for forward-compatibility but NOT persisted:
    package_exclusions table does not have this column yet.
    """
    exclusion_text = fields.String(required=True, validate=validate.Length(min=1))
    display_order = fields.Integer(load_default=None, allow_none=True, validate=validate.Range(min=1))

    @pre_load
    def strip_text(self, data, **kwargs):
        if "exclusion_text" in data and isinstance(data["exclusion_text"], str):
            data["exclusion_text"] = data["exclusion_text"].strip()
        return data

    @validates("exclusion_text")
    def validate_exclusion_text(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Exclusion text cannot be blank.")


class PackageDestinationRequestSchema(Schema):
    destination_id = fields.UUID(required=True)
    day_order = fields.Integer(required=True, validate=validate.Range(min=1))
    sequence = fields.Integer(required=True, validate=validate.Range(min=1))
    overnight_stay = fields.Boolean(load_default=False)
    default_duration = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=50))


# ---------------------------------------------------------------------------
# Top-level request schemas
# ---------------------------------------------------------------------------

class CreatePackageRequestSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(load_default=None, allow_none=True)
    duration_days = fields.Integer(required=True, validate=validate.Range(min=1))
    duration_nights = fields.Integer(required=True, validate=validate.Range(min=0))
    starting_price = fields.Decimal(
        load_default=None, allow_none=True, places=2, as_string=False
    )
    starting_city = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=100))
    thumbnail_url = fields.String(load_default=None, allow_none=True)
    terms = fields.String(load_default=None, allow_none=True)
    is_featured = fields.Boolean(load_default=False)
    is_active = fields.Boolean(load_default=True)
    highlights = fields.List(fields.Nested(PackageHighlightRequestSchema), load_default=[])
    inclusions = fields.List(fields.Nested(PackageInclusionRequestSchema), load_default=[])
    exclusions = fields.List(fields.Nested(PackageExclusionRequestSchema), load_default=[])
    destinations = fields.List(fields.Nested(PackageDestinationRequestSchema), load_default=[])

    @pre_load
    def strip_title(self, data, **kwargs):
        if "title" in data and isinstance(data["title"], str):
            data["title"] = data["title"].strip()
        return data

    @validates("title")
    def validate_title(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Package title cannot be blank.")


class UpdatePackageRequestSchema(Schema):
    """
    All scalar fields optional. `version` is REQUIRED.
    Nested collection fields follow the three-state rule handled in the service:
      - key absent   → collection unchanged
      - key = []     → collection cleared
      - key = [...]  → collection replaced
    """
    title = fields.String(validate=validate.Length(min=1, max=200))
    description = fields.String(allow_none=True)
    duration_days = fields.Integer(validate=validate.Range(min=1))
    duration_nights = fields.Integer(validate=validate.Range(min=0))
    starting_price = fields.Decimal(allow_none=True, places=2, as_string=False)
    starting_city = fields.String(allow_none=True, validate=validate.Length(max=100))
    thumbnail_url = fields.String(allow_none=True)
    terms = fields.String(allow_none=True)
    is_featured = fields.Boolean()
    is_active = fields.Boolean()
    highlights = fields.List(fields.Nested(PackageHighlightRequestSchema))
    inclusions = fields.List(fields.Nested(PackageInclusionRequestSchema))
    exclusions = fields.List(fields.Nested(PackageExclusionRequestSchema))
    destinations = fields.List(fields.Nested(PackageDestinationRequestSchema))
    version = fields.Integer(required=True)

    @pre_load
    def strip_title(self, data, **kwargs):
        if "title" in data and isinstance(data["title"], str):
            data["title"] = data["title"].strip()
        return data

    @validates("title")
    def validate_title(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Package title cannot be blank.")


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class PackageHighlightResponseSchema(Schema):
    id = fields.UUID()
    highlight_text = fields.String()
    display_order = fields.Integer(allow_none=True)


class PackageInclusionResponseSchema(Schema):
    id = fields.UUID()
    inclusion_text = fields.String()
    # display_order not in DB — always null
    display_order = fields.Method("get_display_order")

    def get_display_order(self, obj):
        return None


class PackageExclusionResponseSchema(Schema):
    id = fields.UUID()
    exclusion_text = fields.String()
    # display_order not in DB — always null
    display_order = fields.Method("get_display_order")

    def get_display_order(self, obj):
        return None


class PackageDestinationResponseSchema(Schema):
    id = fields.UUID()
    destination_id = fields.UUID()
    day_order = fields.Integer()
    sequence = fields.Integer()
    overnight_stay = fields.Boolean()
    default_duration = fields.String(allow_none=True)


class PackageSummaryResponseSchema(Schema):
    id = fields.UUID()
    title = fields.String()
    duration_days = fields.Integer()
    duration_nights = fields.Integer()
    starting_price = fields.Decimal(allow_none=True, places=2, as_string=False)
    is_featured = fields.Boolean()
    is_active = fields.Boolean()


class PackageDetailResponseSchema(Schema):
    id = fields.UUID()
    title = fields.String()
    description = fields.String(allow_none=True)
    duration_days = fields.Integer()
    duration_nights = fields.Integer()
    starting_price = fields.Decimal(allow_none=True, places=2, as_string=False)
    starting_city = fields.String(allow_none=True)
    thumbnail_url = fields.String(allow_none=True)
    terms = fields.String(allow_none=True)
    is_featured = fields.Boolean()
    is_active = fields.Boolean()
    highlights = fields.List(fields.Nested(PackageHighlightResponseSchema))
    inclusions = fields.List(fields.Nested(PackageInclusionResponseSchema))
    exclusions = fields.List(fields.Nested(PackageExclusionResponseSchema))
    destinations = fields.List(fields.Nested(PackageDestinationResponseSchema))
    version = fields.Integer()
    audit_info = fields.Method("get_audit_info")

    def get_audit_info(self, obj):
        return {
            "created_by": str(obj.created_by_team_member_id) if obj.created_by_team_member_id else None,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_by": str(obj.updated_by_team_member_id) if obj.updated_by_team_member_id else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        }
