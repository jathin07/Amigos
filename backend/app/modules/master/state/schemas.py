import re
from marshmallow import Schema, fields, validate, validates, ValidationError

# ─────────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────────

class CreateStateRequestSchema(Schema):
    name          = fields.String(required=True,  validate=validate.Length(min=1, max=100))
    code          = fields.String(required=True,  validate=validate.Length(min=1, max=10))
    country_id    = fields.UUID(required=True)
    description   = fields.String(load_default=None, validate=validate.Length(max=255))
    display_order = fields.Integer(load_default=0, validate=validate.Range(min=0))
    is_active     = fields.Boolean(load_default=True)

    @validates("code")
    def validate_code(self, value, **kwargs):
        if not re.match(r"^[A-Z0-9_]+$", value.strip().upper()):
            raise ValidationError("Code must be uppercase letters, digits, or underscores only.")
        return value.strip().upper()


class UpdateStateRequestSchema(Schema):
    name          = fields.String(validate=validate.Length(min=1, max=100))
    code          = fields.String(validate=validate.Length(min=1, max=10))
    country_id    = fields.UUID()
    description   = fields.String(allow_none=True, validate=validate.Length(max=255))
    display_order = fields.Integer(validate=validate.Range(min=0))
    is_active     = fields.Boolean()
    version       = fields.Integer(required=True)

    @validates("code")
    def validate_code(self, value, **kwargs):
        if not re.match(r"^[A-Z0-9_]+$", value.strip().upper()):
            raise ValidationError("Code must be uppercase letters, digits, or underscores only.")
        return value.strip().upper()


# ─────────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────────

class StateSummaryResponseSchema(Schema):
    id        = fields.UUID()
    name      = fields.String()
    code      = fields.String()
    is_active = fields.Boolean()


class StateDetailResponseSchema(StateSummaryResponseSchema):
    country_id    = fields.UUID()
    description   = fields.String()
    display_order = fields.Integer()
    version       = fields.Integer()
    audit_info    = fields.Method("get_audit_info")

    def get_audit_info(self, obj):
        return {
            "created_by": str(obj.created_by) if obj.created_by else None,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_by": str(obj.updated_by) if obj.updated_by else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        }


class StateLookupResponseSchema(Schema):
    id   = fields.UUID()
    name = fields.String()
    code = fields.String()
