from marshmallow import Schema, fields, validate, validates, ValidationError
import re


# ─────────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────────

class OrganizationDivisionRequestSchema(Schema):
    id = fields.UUID(load_default=None)
    department = fields.String(load_default=None, validate=validate.Length(max=150))
    course = fields.String(load_default=None, validate=validate.Length(max=150))
    section = fields.String(load_default=None, validate=validate.Length(max=50))
    year = fields.String(load_default=None, validate=validate.Length(max=50))
    semester = fields.String(load_default=None, validate=validate.Length(max=50))
    batch = fields.String(load_default=None, validate=validate.Length(max=50))


class ContactPersonRequestSchema(Schema):
    id = fields.UUID(load_default=None)
    name = fields.String(required=True, validate=validate.Length(min=1, max=150))
    designation = fields.String(load_default=None, validate=validate.Length(max=100))
    phone = fields.String(required=True, validate=validate.Length(min=1, max=20))
    alternate_phone = fields.String(load_default=None, validate=validate.Length(max=20))
    email = fields.String(load_default=None, validate=validate.Length(max=150))
    is_primary = fields.Boolean(load_default=False)
    preferred_contact_method = fields.String(load_default=None, validate=validate.Length(max=30))
    notes = fields.String(load_default=None)
    is_active = fields.Boolean(load_default=True)


class UpdateOrganizationRequestSchema(Schema):
    organization_name = fields.String(validate=validate.Length(min=1, max=200))
    organization_type_id = fields.UUID()
    address = fields.String(allow_none=True)
    city = fields.String(allow_none=True, validate=validate.Length(max=100))
    state = fields.String(allow_none=True, validate=validate.Length(max=100))
    phone = fields.String(allow_none=True, validate=validate.Length(max=20))
    email = fields.String(allow_none=True, validate=validate.Length(max=150))
    website = fields.String(allow_none=True, validate=validate.Length(max=200))
    notes = fields.String(allow_none=True)
    is_active = fields.Boolean()
    divisions = fields.List(fields.Nested(OrganizationDivisionRequestSchema), load_default=None)
    contact_persons = fields.List(fields.Nested(ContactPersonRequestSchema), load_default=None)


# ─────────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────────

class OrganizationDivisionResponseSchema(Schema):
    id = fields.UUID()
    department = fields.String()
    course = fields.String()
    section = fields.String()
    year = fields.String()
    semester = fields.String()
    batch = fields.String()


class ContactPersonResponseSchema(Schema):
    id = fields.UUID()
    name = fields.String()
    designation = fields.String()
    phone = fields.String()
    alternate_phone = fields.String()
    email = fields.String()
    is_primary = fields.Boolean()
    preferred_contact_method = fields.String()
    notes = fields.String()
    is_active = fields.Boolean()


class OrganizationDetailResponseSchema(Schema):
    id = fields.UUID()
    organization_name = fields.String()
    organization_type_id = fields.UUID()
    address = fields.String()
    city = fields.String()
    state = fields.String()
    phone = fields.String()
    email = fields.String()
    website = fields.String()
    notes = fields.String()
    is_active = fields.Boolean()
    divisions = fields.List(fields.Nested(OrganizationDivisionResponseSchema))
    contact_persons = fields.Method("get_active_contact_persons")
    version = fields.Method("get_dummy_version")
    audit_info = fields.Method("get_audit_info")

    def get_active_contact_persons(self, obj):
        active_contacts = [c for c in obj.contact_persons if not c.is_deleted]
        return ContactPersonResponseSchema(many=True).dump(active_contacts)

    def get_dummy_version(self, obj):
        return 1

    def get_audit_info(self, obj):
        return {
            "created_by": str(obj.created_by_team_member_id) if obj.created_by_team_member_id else None,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_by": str(obj.updated_by_team_member_id) if obj.updated_by_team_member_id else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        }
