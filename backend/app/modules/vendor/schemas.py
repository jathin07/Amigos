from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load


class CreateVendorRequestSchema(Schema):
    vendor_name = fields.String(required=True, validate=validate.Length(min=1, max=200))
    vendor_type_id = fields.UUID(required=True)
    contact_person = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=150))
    phone = fields.String(required=True, validate=validate.Length(min=1, max=20))
    email = fields.String(load_default=None, allow_none=True, validate=[validate.Email(), validate.Length(max=150)])
    address = fields.String(load_default=None, allow_none=True)
    city = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=100))
    state = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=100))
    service_area = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=255))
    internal_rating = fields.Integer(load_default=None, allow_none=True, validate=validate.Range(min=1, max=5))
    bank_account_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=150))
    bank_account_number = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=50))
    ifsc = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=20))
    gst_number = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=20))
    notes = fields.String(load_default=None, allow_none=True)
    is_active = fields.Boolean(load_default=True)

    @pre_load
    def process_fields(self, data, **kwargs):
        if not data:
            return data
        # Trim names and string fields
        for field in ("vendor_name", "phone", "email", "gst_number"):
            if field in data and isinstance(data[field], str):
                data[field] = data[field].strip()
        if "email" in data and isinstance(data["email"], str):
            data["email"] = data["email"].lower()
        if "gst_number" in data and isinstance(data["gst_number"], str):
            data["gst_number"] = data["gst_number"].upper()
        return data

    @validates("vendor_name")
    def validate_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Vendor name cannot be blank.")


class UpdateVendorRequestSchema(Schema):
    vendor_name = fields.String(validate=validate.Length(min=1, max=200))
    vendor_type_id = fields.UUID()
    contact_person = fields.String(allow_none=True, validate=validate.Length(max=150))
    phone = fields.String(validate=validate.Length(min=1, max=20))
    email = fields.String(allow_none=True, validate=[validate.Email(), validate.Length(max=150)])
    address = fields.String(allow_none=True)
    city = fields.String(allow_none=True, validate=validate.Length(max=100))
    state = fields.String(allow_none=True, validate=validate.Length(max=100))
    service_area = fields.String(allow_none=True, validate=validate.Length(max=255))
    internal_rating = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=5))
    bank_account_name = fields.String(allow_none=True, validate=validate.Length(max=150))
    bank_account_number = fields.String(allow_none=True, validate=validate.Length(max=50))
    ifsc = fields.String(allow_none=True, validate=validate.Length(max=20))
    gst_number = fields.String(allow_none=True, validate=validate.Length(max=20))
    notes = fields.String(allow_none=True)
    is_active = fields.Boolean()
    version = fields.Integer(required=True)

    @pre_load
    def process_fields(self, data, **kwargs):
        if not data:
            return data
        for field in ("vendor_name", "phone", "email", "gst_number"):
            if field in data and isinstance(data[field], str):
                data[field] = data[field].strip()
        if "email" in data and isinstance(data["email"], str):
            data["email"] = data["email"].lower()
        if "gst_number" in data and isinstance(data["gst_number"], str):
            data["gst_number"] = data["gst_number"].upper()
        return data

    @validates("vendor_name")
    def validate_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Vendor name cannot be blank.")


class VendorSummaryResponseSchema(Schema):
    id = fields.UUID()
    vendor_name = fields.String()
    vendor_type_id = fields.UUID()
    phone = fields.String()
    email = fields.String()
    is_verified = fields.Boolean()
    is_active = fields.Boolean()


class VendorDetailResponseSchema(Schema):
    id = fields.UUID()
    vendor_name = fields.String()
    vendor_type_id = fields.UUID()
    contact_person = fields.String()
    phone = fields.String()
    email = fields.String()
    address = fields.String()
    city = fields.String()
    state = fields.String()
    service_area = fields.String()
    internal_rating = fields.Integer()
    bank_account_name = fields.String()
    bank_account_number = fields.String()
    ifsc = fields.String()
    gst_number = fields.String()
    is_verified = fields.Boolean()
    verified_at = fields.DateTime(format="%Y-%m-%dT%H:%M:%SZ")
    notes = fields.String()
    is_active = fields.Boolean()
    version = fields.Integer()
    audit_info = fields.Method("get_audit_info")

    def get_audit_info(self, obj):
        return {
            "created_by": str(obj.created_by_team_member_id) if obj.created_by_team_member_id else None,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_by": str(obj.updated_by_team_member_id) if obj.updated_by_team_member_id else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        }
