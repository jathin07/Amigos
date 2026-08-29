import re
from marshmallow import Schema, fields, validate, validates, ValidationError


# ─────────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────────

class CreateDestinationRequestSchema(Schema):
    name          = fields.String(required=True, validate=validate.Length(min=1, max=150))
    code          = fields.String(load_default=None, allow_none=True)
    slug          = fields.String(load_default=None, allow_none=True)
    country_id    = fields.UUID(load_default=None, allow_none=True)
    state_id      = fields.UUID(load_default=None, allow_none=True)
    district_id   = fields.UUID(load_default=None, allow_none=True)
    description   = fields.String(load_default=None, validate=validate.Length(max=2000))
    cover_image   = fields.String(load_default=None, validate=validate.Length(max=500))
    latitude      = fields.Decimal(load_default=None, places=7, as_string=False)
    longitude     = fields.Decimal(load_default=None, places=7, as_string=False)
    display_order = fields.Integer(load_default=0, validate=validate.Range(min=0))
    is_active     = fields.Boolean(load_default=True)

    @validates("code")
    def validate_code(self, value, **kwargs):
        if value:
            if not re.match(r"^[A-Z0-9_\-]+$", value.strip().upper()):
                raise ValidationError("Code must be uppercase letters, digits, underscores, or hyphens only.")
            return value.strip().upper()
        return value

    @validates("slug")
    def validate_slug(self, value, **kwargs):
        if value:
            if not re.match(r"^[a-z0-9\-]+$", value.strip().lower()):
                raise ValidationError("Slug must be lowercase letters, digits, or hyphens only.")
            return value.strip().lower()
        return value


class UpdateDestinationRequestSchema(Schema):
    name          = fields.String(validate=validate.Length(min=1, max=150))
    code          = fields.String(validate=validate.Length(min=1, max=20))
    slug          = fields.String(validate=validate.Length(min=1, max=100))
    country_id    = fields.UUID()
    state_id      = fields.UUID()
    district_id   = fields.UUID()
    description   = fields.String(allow_none=True, validate=validate.Length(max=2000))
    cover_image   = fields.String(allow_none=True, validate=validate.Length(max=500))
    latitude      = fields.Decimal(allow_none=True, places=7, as_string=False)
    longitude     = fields.Decimal(allow_none=True, places=7, as_string=False)
    display_order = fields.Integer(validate=validate.Range(min=0))
    is_active     = fields.Boolean()
    version       = fields.Integer(required=True)

    @validates("code")
    def validate_code(self, value, **kwargs):
        if not re.match(r"^[A-Z0-9_\-]+$", value.strip().upper()):
            raise ValidationError("Code must be uppercase letters, digits, underscores, or hyphens only.")
        return value.strip().upper()

    @validates("slug")
    def validate_slug(self, value, **kwargs):
        if not re.match(r"^[a-z0-9\-]+$", value.strip().lower()):
            raise ValidationError("Slug must be lowercase letters, digits, or hyphens only.")
        return value.strip().lower()


# ─────────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────────

class DestinationLookupResponseSchema(Schema):
    id   = fields.UUID()
    name = fields.String()
    code = fields.String()
    slug = fields.String()


class DestinationSummaryResponseSchema(Schema):
    id            = fields.UUID()
    name          = fields.String()
    code          = fields.String()
    slug          = fields.String()
    is_active     = fields.Boolean()
    display_order = fields.Integer()


class DestinationDetailResponseSchema(DestinationSummaryResponseSchema):
    description = fields.String()
    country_id  = fields.UUID()
    state_id    = fields.UUID()
    district_id = fields.UUID()
    cover_image = fields.String()
    latitude    = fields.Decimal(places=7, as_string=True)
    longitude   = fields.Decimal(places=7, as_string=True)
    version     = fields.Integer()
    audit_info  = fields.Method("get_audit_info")

    def get_audit_info(self, obj):
        return {
            "created_by": str(obj.created_by) if obj.created_by else None,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_by": str(obj.updated_by) if obj.updated_by else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        }
