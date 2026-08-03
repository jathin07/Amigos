import re
from marshmallow import Schema, fields, validate, validates, ValidationError

class CreateCurrencyRequestSchema(Schema):
    name          = fields.String(required=True, validate=validate.Length(min=1, max=100))
    code          = fields.String(required=True, validate=validate.Length(min=1, max=20))
    description   = fields.String(load_default=None, validate=validate.Length(max=2000))
    display_order = fields.Integer(load_default=0, validate=validate.Range(min=0))
    is_active     = fields.Boolean(load_default=True)
    symbol        = fields.String(required=True, validate=validate.Length(min=1, max=5))
    is_default    = fields.Boolean(load_default=False)

    @validates("code")
    def validate_code(self, value, **kwargs):
        if not re.match(r"^[A-Z0-9_\-]+$", value.strip().upper()):
            raise ValidationError("Code must be uppercase letters, digits, underscores or hyphens.")
        return value.strip().upper()

class UpdateCurrencyRequestSchema(Schema):
    name          = fields.String(validate=validate.Length(min=1, max=100))
    code          = fields.String(validate=validate.Length(min=1, max=20))
    description   = fields.String(allow_none=True, validate=validate.Length(max=2000))
    display_order = fields.Integer(validate=validate.Range(min=0))
    is_active     = fields.Boolean()
    symbol        = fields.String(validate=validate.Length(min=1, max=5))
    is_default    = fields.Boolean()
    version       = fields.Integer(required=True)

    @validates("code")
    def validate_code(self, value, **kwargs):
        if not re.match(r"^[A-Z0-9_\-]+$", value.strip().upper()):
            raise ValidationError("Code must be uppercase letters, digits, underscores or hyphens.")
        return value.strip().upper()

class CurrencyLookupResponseSchema(Schema):
    id   = fields.UUID()
    name = fields.String()
    code = fields.String()

class CurrencySummaryResponseSchema(Schema):
    id            = fields.UUID()
    name          = fields.String()
    code          = fields.String()
    is_active     = fields.Boolean()
    display_order = fields.Integer()
    symbol        = fields.String()
    is_default    = fields.Boolean()

class CurrencyDetailResponseSchema(CurrencySummaryResponseSchema):
    description = fields.String()
    version     = fields.Integer()
    audit_info  = fields.Method("get_audit_info")
    def get_audit_info(self, obj):
        return {
            "created_by": str(obj.created_by) if obj.created_by else None,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_by": str(obj.updated_by) if obj.updated_by else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        }
