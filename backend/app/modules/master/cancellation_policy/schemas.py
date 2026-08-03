import re
from marshmallow import Schema, fields, validate, validates, ValidationError

class CreateCancellationPolicyRequestSchema(Schema):
    name               = fields.String(required=True, validate=validate.Length(min=1, max=100))
    code               = fields.String(required=True, validate=validate.Length(min=1, max=20))
    description        = fields.String(load_default=None, validate=validate.Length(max=2000))
    display_order      = fields.Integer(load_default=0, validate=validate.Range(min=0))
    is_active          = fields.Boolean(load_default=True)
    refund_percentage  = fields.Decimal(required=True, as_string=False, validate=validate.Range(min=0, max=100))
    days_before_travel = fields.Integer(required=True, validate=validate.Range(min=0))
    policy_type        = fields.String(load_default="PERCENTAGE", validate=validate.OneOf(["PERCENTAGE", "FLAT"]))

    @validates("code")
    def validate_code(self, value, **kwargs):
        if not re.match(r"^[A-Z0-9_\-]+$", value.strip().upper()):
            raise ValidationError("Code must be uppercase letters, digits, underscores or hyphens.")
        return value.strip().upper()

class UpdateCancellationPolicyRequestSchema(Schema):
    name               = fields.String(validate=validate.Length(min=1, max=100))
    code               = fields.String(validate=validate.Length(min=1, max=20))
    description        = fields.String(allow_none=True, validate=validate.Length(max=2000))
    display_order      = fields.Integer(validate=validate.Range(min=0))
    is_active          = fields.Boolean()
    refund_percentage  = fields.Decimal(as_string=False, validate=validate.Range(min=0, max=100))
    days_before_travel = fields.Integer(validate=validate.Range(min=0))
    policy_type        = fields.String(validate=validate.OneOf(["PERCENTAGE", "FLAT"]))
    version            = fields.Integer(required=True)

    @validates("code")
    def validate_code(self, value, **kwargs):
        if not re.match(r"^[A-Z0-9_\-]+$", value.strip().upper()):
            raise ValidationError("Code must be uppercase letters, digits, underscores or hyphens.")
        return value.strip().upper()

class CancellationPolicyLookupResponseSchema(Schema):
    id   = fields.UUID()
    name = fields.String()
    code = fields.String()

class CancellationPolicySummaryResponseSchema(Schema):
    id                 = fields.UUID()
    name               = fields.String()
    code               = fields.String()
    is_active          = fields.Boolean()
    display_order      = fields.Integer()

class CancellationPolicyDetailResponseSchema(CancellationPolicySummaryResponseSchema):
    description        = fields.String()
    refund_percentage  = fields.Decimal(as_string=True)
    days_before_travel = fields.Integer()
    policy_type        = fields.String()
    version            = fields.Integer()
    audit_info         = fields.Method("get_audit_info")
    def get_audit_info(self, obj):
        return {
            "created_by": str(obj.created_by) if obj.created_by else None,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_by": str(obj.updated_by) if obj.updated_by else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        }
