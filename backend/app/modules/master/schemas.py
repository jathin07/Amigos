import re
from marshmallow import Schema, fields, validate, validates, ValidationError


class BaseMasterRequestSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    code = fields.String(required=True, validate=validate.Length(min=1, max=20))
    description = fields.String(load_default=None, validate=validate.Length(max=255))
    display_order = fields.Integer(load_default=0, validate=validate.Range(min=0))
    is_active = fields.Boolean(load_default=True)

    @validates("code")
    def validate_code(self, value, **kwargs):
        if not re.match(r"^[A-Z0-9_\-]+$", value.strip().upper()):
            raise ValidationError("Code must be uppercase letters, digits, underscores, or hyphens only.")
        return value.strip().upper()


class BaseMasterUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(min=1, max=100))
    code = fields.String(validate=validate.Length(min=1, max=20))
    description = fields.String(allow_none=True, validate=validate.Length(max=255))
    display_order = fields.Integer(validate=validate.Range(min=0))
    is_active = fields.Boolean()
    version = fields.Integer(required=True)

    @validates("code")
    def validate_code(self, value, **kwargs):
        if not re.match(r"^[A-Z0-9_\-]+$", value.strip().upper()):
            raise ValidationError("Code must be uppercase letters, digits, underscores, or hyphens only.")
        return value.strip().upper()


class BaseMasterSummaryResponseSchema(Schema):
    id = fields.UUID()
    name = fields.String()
    code = fields.String()
    is_active = fields.Boolean()
    display_order = fields.Integer()


class BaseMasterDetailResponseSchema(BaseMasterSummaryResponseSchema):
    description = fields.String()
    version = fields.Integer()
    audit_info = fields.Method("get_audit_info")

    def get_audit_info(self, obj):
        return {
            "created_by": str(obj.created_by) if obj.created_by else None,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_by": str(obj.updated_by) if obj.updated_by else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        }


class BaseMasterLookupResponseSchema(Schema):
    id = fields.UUID()
    name = fields.String()
    code = fields.String()


# ─────────────────────────────────────────────────────────────────
# Currency Schemas
# ─────────────────────────────────────────────────────────────────

class CreateCurrencyRequestSchema(BaseMasterRequestSchema):
    symbol = fields.String(required=True, validate=validate.Length(min=1, max=10))
    is_default = fields.Boolean(load_default=False)


class UpdateCurrencyRequestSchema(BaseMasterUpdateSchema):
    symbol = fields.String(validate=validate.Length(min=1, max=10))
    is_default = fields.Boolean()


class CurrencySummaryResponseSchema(BaseMasterSummaryResponseSchema):
    symbol = fields.String()
    is_default = fields.Boolean()


class CurrencyDetailResponseSchema(BaseMasterDetailResponseSchema):
    symbol = fields.String()
    is_default = fields.Boolean()


class CurrencyLookupResponseSchema(BaseMasterLookupResponseSchema):
    symbol = fields.String()
    is_default = fields.Boolean()


# ─────────────────────────────────────────────────────────────────
# Cancellation Policy Schemas
# ─────────────────────────────────────────────────────────────────

class CreateCancellationPolicyRequestSchema(BaseMasterRequestSchema):
    refund_percentage = fields.Decimal(required=True, validate=validate.Range(min=0, max=100), places=2, as_string=False)
    days_before_travel = fields.Integer(required=True, validate=validate.Range(min=0))


class UpdateCancellationPolicyRequestSchema(BaseMasterUpdateSchema):
    refund_percentage = fields.Decimal(validate=validate.Range(min=0, max=100), places=2, as_string=False)
    days_before_travel = fields.Integer(validate=validate.Range(min=0))


class CancellationPolicySummaryResponseSchema(BaseMasterSummaryResponseSchema):
    refund_percentage = fields.Decimal(places=2, as_string=True)
    days_before_travel = fields.Integer()


class CancellationPolicyDetailResponseSchema(BaseMasterDetailResponseSchema):
    refund_percentage = fields.Decimal(places=2, as_string=True)
    days_before_travel = fields.Integer()


class CancellationPolicyLookupResponseSchema(BaseMasterLookupResponseSchema):
    refund_percentage = fields.Decimal(places=2, as_string=True)
    days_before_travel = fields.Integer()


# ─────────────────────────────────────────────────────────────────
# Tax Configuration Schemas
# ─────────────────────────────────────────────────────────────────

class CreateTaxConfigurationRequestSchema(BaseMasterRequestSchema):
    tax_rate = fields.Decimal(required=True, validate=validate.Range(min=0, max=100), places=2, as_string=False)
    tax_type = fields.String(required=True, validate=validate.Length(min=1, max=20))


class UpdateTaxConfigurationRequestSchema(BaseMasterUpdateSchema):
    tax_rate = fields.Decimal(validate=validate.Range(min=0, max=100), places=2, as_string=False)
    tax_type = fields.String(validate=validate.Length(min=1, max=20))


class TaxConfigurationSummaryResponseSchema(BaseMasterSummaryResponseSchema):
    tax_rate = fields.Decimal(places=2, as_string=True)
    tax_type = fields.String()


class TaxConfigurationDetailResponseSchema(BaseMasterDetailResponseSchema):
    tax_rate = fields.Decimal(places=2, as_string=True)
    tax_type = fields.String()


class TaxConfigurationLookupResponseSchema(BaseMasterLookupResponseSchema):
    tax_rate = fields.Decimal(places=2, as_string=True)
    tax_type = fields.String()
