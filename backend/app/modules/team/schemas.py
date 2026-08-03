from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
import datetime


# ─────────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────────

class CreateTeamMemberRequestSchema(Schema):
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=100))
    display_name = fields.String(required=True, validate=validate.Length(min=1, max=150))
    avatar_url = fields.String(load_default=None, allow_none=True)
    dob = fields.Date(format="%Y-%m-%d", load_default=None, allow_none=True)
    gender = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=20))
    employee_code = fields.String(required=True, validate=validate.Length(min=1, max=50))
    official_email = fields.String(required=True, validate=[validate.Email(), validate.Length(max=150)])
    personal_email = fields.String(load_default=None, allow_none=True, validate=[validate.Email(), validate.Length(max=150)])
    phone = fields.String(required=True, validate=validate.Length(min=1, max=20))
    designation = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=100))
    department_id = fields.UUID(load_default=None, allow_none=True)
    role_id = fields.UUID(load_default=None, allow_none=True)
    reporting_manager_id = fields.UUID(load_default=None, allow_none=True)
    employment_status = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=50))
    joined_date = fields.Date(format="%Y-%m-%d", load_default=None, allow_none=True)
    left_date = fields.Date(format="%Y-%m-%d", load_default=None, allow_none=True)
    is_active = fields.Boolean(load_default=True)
    emergency_contact_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=150))
    emergency_contact_phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=20))

class UpdateTeamMemberRequestSchema(Schema):
    first_name = fields.String(validate=validate.Length(min=1, max=100))
    last_name = fields.String(allow_none=True, validate=validate.Length(max=100))
    display_name = fields.String(validate=validate.Length(min=1, max=150))
    avatar_url = fields.String(allow_none=True)
    dob = fields.Date(format="%Y-%m-%d", allow_none=True)
    gender = fields.String(allow_none=True, validate=validate.Length(max=20))
    employee_code = fields.String(validate=validate.Length(min=1, max=50))
    official_email = fields.String(validate=[validate.Email(), validate.Length(max=150)])
    personal_email = fields.String(allow_none=True, validate=[validate.Email(), validate.Length(max=150)])
    phone = fields.String(validate=validate.Length(min=1, max=20))
    designation = fields.String(allow_none=True, validate=validate.Length(max=100))
    department_id = fields.UUID(allow_none=True)
    role_id = fields.UUID(allow_none=True)
    reporting_manager_id = fields.UUID(allow_none=True)
    employment_status = fields.String(allow_none=True, validate=validate.Length(max=50))
    joined_date = fields.Date(format="%Y-%m-%d", allow_none=True)
    left_date = fields.Date(format="%Y-%m-%d", allow_none=True)
    is_active = fields.Boolean()
    emergency_contact_name = fields.String(allow_none=True, validate=validate.Length(max=150))
    emergency_contact_phone = fields.String(allow_none=True, validate=validate.Length(max=20))
    version = fields.Integer(required=True)


# ─────────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────────

class TeamMemberSummaryResponseSchema(Schema):
    id = fields.UUID()
    employee_code = fields.String()
    display_name = fields.String()
    official_email = fields.String()
    phone = fields.String()
    designation = fields.String()
    employment_status = fields.String()
    is_active = fields.Boolean()


class TeamMemberDetailResponseSchema(Schema):
    id = fields.UUID()
    first_name = fields.String()
    last_name = fields.String()
    display_name = fields.String()
    avatar_url = fields.String()
    dob = fields.Date(format="%Y-%m-%d")
    gender = fields.String()
    employee_code = fields.String()
    official_email = fields.String()
    personal_email = fields.String()
    phone = fields.String()
    designation = fields.String()
    department_id = fields.UUID()
    role_id = fields.UUID()
    reporting_manager_id = fields.UUID()
    employment_status = fields.String()
    availability_status = fields.String()
    joined_date = fields.Date(format="%Y-%m-%d")
    left_date = fields.Date(format="%Y-%m-%d")
    emergency_contact_name = fields.String()
    emergency_contact_phone = fields.String()
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
