import re
from marshmallow import Schema, fields, validate, validates, ValidationError

class CreateTaxConfigurationRequestSchema(Schema):
    name          = fields.String(required=True, validate=validate.Length(min=1, max=100))
    code          = fields.String(required=True, validate=validate.Length(min=1, max=20))
    description   = fields.String(load_default=None, validate=validate.Length(max=2000))
    display_order = fields.Integer(load_default=0, validate=validate.Range(min=0))
    is_active     = fields.Boolean(load_default=True)
    tax_rate      = fields.Decimal(required=True, as_string=False, validate=validate.Range(min=0, max=100))
    tax_type      = fields.String(required=True, validate=validate.OneOf(["GST", "VAT", "SERVICE_TAX", "CESS"]))
    is_inclusive  = fields.Boolean(load_default=False)
    is_default    = fields.Boolean(load_default=False)

    @validates("code")
    def validate_code(self, value, **kwargs):
        if not re.match(r"^[A-Z0-9_\-]+$", value.strip().upper()):
            raise ValidationError("Code must be uppercase letters, digits, underscores or hyphens.")
        return value.strip().upper()

class UpdateTaxConfigurationRequestSchema(Schema):
    name          = fields.String(validate=validate.Length(min=1, max=100))
    code          = fields.String(validate=validate.Length(min=1, max=20))
    description   = fields.String(allow_none=True, validate=validate.Length(max=2000))
    display_order = fields.Integer(validate=validate.Range(min=0))
    is_active     = fields.Boolean()
    tax_rate      = fields.Decimal(as_string=False, validate=validate.Range(min=0, max=100))
    tax_type      = fields.String(validate=validate.OneOf(["GST", "VAT", "SERVICE_TAX", "CESS"]))
    is_inclusive  = fields.Boolean()
    is_default    = fields.Boolean()
    version       = fields.Integer(required=True)

    @validates("code")
    def validate_code(self, value, **kwargs):
        if not re.match(r"^[A-Z0-9_\-]+$", value.strip().upper()):
            raise ValidationError("Code must be uppercase letters, digits, underscores or hyphens.")
        return value.strip().upper()

class TaxConfigurationLookupResponseSchema(Schema):
    id   = fields.UUID()
    name = fields.String()
    code = fields.String()

class TaxConfigurationSummaryResponseSchema(Schema):
    id            = fields.UUID()
    name          = fields.String()
    code          = fields.String()
    is_active     = fields.Boolean()
    display_order = fields.Integer()
    tax_rate      = fields.Decimal(as_string=True)
    tax_type      = fields.String()

class TaxConfigurationDetailResponseSchema(TaxConfigurationSummaryResponseSchema):
    description   = fields.String()
    is_inclusive  = fields.Boolean()
    is_default    = fields.Boolean()
    version       = fields.Integer()
    audit_info    = fields.Method("get_audit_info")
    def get_audit_info(self, obj):
        return {
            "created_by": str(obj.created_by) if obj.created_by else None,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_by": str(obj.updated_by) if obj.updated_by else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        }
