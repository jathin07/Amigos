from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class SimpleLookupResponseSchema(Schema):
    id = fields.UUID()
    code = fields.String()
    name = fields.String()


class AuditRefSchema(Schema):
    id = fields.UUID()
    display_name = fields.String()


class AuditInfoSchema(Schema):
    created_at = fields.DateTime(allow_none=True)
    created_by = fields.Nested(AuditRefSchema, allow_none=True)
    updated_at = fields.DateTime(allow_none=True)
    updated_by = fields.Nested(AuditRefSchema, allow_none=True)


# Request Schemas

class CreateTripPlanRequestSchema(Schema):
    booking_id = fields.UUID(required=True)
    prepared_date = fields.Date(required=True)
    notes = fields.String(allow_none=True)


class UpdateTripPlanStatusRequestSchema(Schema):
    target_status = fields.String(required=True)


class CompleteTripRequestSchema(Schema):
    notes = fields.String(allow_none=True)


class UpdateTripDayRequestSchema(Schema):
    start_location = fields.String(allow_none=True, validate=validate.Length(max=100))
    end_location = fields.String(allow_none=True, validate=validate.Length(max=100))
    overnight_destination_id = fields.UUID(allow_none=True)
    start_time = fields.String(allow_none=True, validate=validate.Length(max=50))
    end_time = fields.String(allow_none=True, validate=validate.Length(max=50))
    morning_plan = fields.String(allow_none=True)
    afternoon_plan = fields.String(allow_none=True)
    evening_plan = fields.String(allow_none=True)
    night_stay = fields.String(allow_none=True, validate=validate.Length(max=150))
    notes = fields.String(allow_none=True)


class CreateVendorAllocationRequestSchema(Schema):
    vendor_id = fields.UUID(required=True)
    service_name = fields.String(required=True, validate=validate.Length(max=150))
    service_type_id = fields.UUID(required=True)
    service_date = fields.Date(required=True)
    quantity = fields.Integer(load_default=1, validate=validate.Range(min=1))
    unit_price = fields.Decimal(required=True, validate=validate.Range(min=0.01))
    notes = fields.String(allow_none=True)


class ConfirmVendorAllocationRequestSchema(Schema):
    confirmed_price = fields.Decimal(required=True, validate=validate.Range(min=0.01))


class CreateTaskRequestSchema(Schema):
    booking_id = fields.UUID(allow_none=True)
    lead_id = fields.UUID(allow_none=True)
    assigned_to_team_member_id = fields.UUID(required=True)
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(allow_none=True)
    due_date = fields.Date(allow_none=True)
    priority_id = fields.UUID(required=True)
    task_status_id = fields.UUID(required=True)
    parent_task_id = fields.UUID(allow_none=True)
    estimated_hours = fields.Decimal(allow_none=True, validate=validate.Range(min=0.0))

    @validates_schema
    def validate_parent(self, data, **kwargs):
        if not data.get("booking_id") and not data.get("lead_id"):
            raise ValidationError("Either booking_id or lead_id must be provided.", "booking_id")
        if data.get("booking_id") and data.get("lead_id"):
            raise ValidationError("Only one of booking_id or lead_id should be provided.", "booking_id")


class UpdateTaskStatusRequestSchema(Schema):
    task_status_id = fields.UUID(required=True)
    actual_hours = fields.Decimal(allow_none=True, validate=validate.Range(min=0.0))
    notes = fields.String(allow_none=True)


class BulkAssignTasksRequestSchema(Schema):
    task_ids = fields.List(fields.UUID(), required=True, validate=validate.Length(min=1, max=50))
    team_member_id = fields.UUID(required=True)


class BulkUpdateTaskStatusRequestSchema(Schema):
    task_ids = fields.List(fields.UUID(), required=True, validate=validate.Length(min=1, max=50))
    task_status_id = fields.UUID(required=True)


# Response Schemas

class VendorAllocationSummaryResponseSchema(Schema):
    id = fields.UUID()
    trip_day_id = fields.UUID()
    vendor_id = fields.UUID()
    vendor_name = fields.Method("get_vendor_name")
    service_name = fields.String()
    service_date = fields.Date()
    quantity = fields.Integer()
    unit_price = fields.Decimal(places=2, as_string=True)
    quoted_amount = fields.Decimal(places=2, as_string=True)
    confirmed_price = fields.Decimal(places=2, as_string=True, allow_none=True)
    allocation_status = fields.Method("get_status_code")
    is_locked = fields.Boolean()

    def get_vendor_name(self, obj) -> str:
        if obj.vendor_name_snapshot:
            return obj.vendor_name_snapshot
        if hasattr(obj, 'vendor') and obj.vendor:
            return obj.vendor.vendor_name
        return "Unknown Vendor"

    def get_status_code(self, obj) -> str:
        if hasattr(obj, 'allocation_status') and obj.allocation_status:
            return obj.allocation_status.code
        return "PENDING"


class VendorAllocationDetailResponseSchema(VendorAllocationSummaryResponseSchema):
    settlement_status = fields.String()
    total_paid = fields.Decimal(places=2, as_string=True)
    balance_due = fields.Decimal(places=2, as_string=True)
    confirmed_by = fields.Method("get_confirmed_by")
    confirmed_at = fields.DateTime(allow_none=True)
    audit = fields.Nested(AuditInfoSchema, attribute="self")

    def get_confirmed_by(self, obj) -> dict | None:
        if hasattr(obj, 'confirmed_by') and obj.confirmed_by:
            return {
                "id": str(obj.confirmed_by.id),
                "display_name": obj.confirmed_by.display_name or obj.confirmed_by.name
            }
        return None


class TripDayDetailResponseSchema(Schema):
    id = fields.UUID()
    day_number = fields.Integer()
    start_location = fields.String(allow_none=True)
    end_location = fields.String(allow_none=True)
    overnight_destination_id = fields.UUID(allow_none=True)
    start_time = fields.String(allow_none=True)
    end_time = fields.String(allow_none=True)
    morning_plan = fields.String(allow_none=True)
    afternoon_plan = fields.String(allow_none=True)
    evening_plan = fields.String(allow_none=True)
    night_stay = fields.String(allow_none=True)
    notes = fields.String(allow_none=True)
    vendor_allocations = fields.List(fields.Nested(VendorAllocationSummaryResponseSchema))


class ChecklistItemResponseSchema(Schema):
    id = fields.UUID()
    item_name = fields.String()
    is_completed = fields.Boolean()
    completed_at = fields.DateTime(allow_none=True)


class ChecklistSummaryResponseSchema(Schema):
    total_items = fields.Integer()
    completed_items = fields.Integer()
    completion_rate = fields.Decimal(places=2, as_string=True)
    items = fields.List(fields.Nested(ChecklistItemResponseSchema))


class TripPlanSummaryResponseSchema(Schema):
    id = fields.UUID()
    booking_id = fields.UUID()
    booking_number = fields.Method("get_booking_number")
    version = fields.Integer()
    is_final = fields.Boolean()
    status = fields.Method("get_status_code")
    prepared_date = fields.Date()
    trip_days_count = fields.Method("get_days_count")
    vendor_allocations_count = fields.Method("get_allocations_count")
    checklist_completion_rate = fields.Method("get_checklist_completion_rate")
    prepared_by = fields.Method("get_prepared_by")
    approved_by = fields.Method("get_approved_by")
    approved_at = fields.DateTime(allow_none=True)

    def get_booking_number(self, obj) -> str:
        if hasattr(obj, 'booking') and obj.booking:
            return obj.booking.booking_number
        return "Unknown"

    def get_status_code(self, obj) -> str:
        if hasattr(obj, 'status') and obj.status:
            return obj.status.code
        return "PLANNING"

    def get_days_count(self, obj) -> int:
        return len(obj.trip_days) if hasattr(obj, 'trip_days') else 0

    def get_allocations_count(self, obj) -> int:
        if not hasattr(obj, 'trip_days'):
            return 0
        return sum(len(day.vendor_allocations) for day in obj.trip_days)

    def get_checklist_completion_rate(self, obj) -> str:
        from .repository import ChecklistRepository
        repo = ChecklistRepository()
        return f"{repo.completion_rate(obj.booking_id):.2f}"

    def get_prepared_by(self, obj) -> dict | None:
        if hasattr(obj, 'prepared_by') and obj.prepared_by:
            return {
                "id": str(obj.prepared_by.id),
                "display_name": obj.prepared_by.display_name or obj.prepared_by.name
            }
        return None

    def get_approved_by(self, obj) -> dict | None:
        if hasattr(obj, 'approved_by') and obj.approved_by:
            return {
                "id": str(obj.approved_by.id),
                "display_name": obj.approved_by.display_name or obj.approved_by.name
            }
        return None


class TripPlanDetailResponseSchema(TripPlanSummaryResponseSchema):
    row_version = fields.Integer()
    trip_days = fields.List(fields.Nested(TripDayDetailResponseSchema))
    checklist = fields.Method("get_checklist_summary")
    audit = fields.Nested(AuditInfoSchema, attribute="self")

    def get_checklist_summary(self, obj) -> dict:
        from .repository import ChecklistRepository
        repo = ChecklistRepository()
        items = repo.list_by_booking(obj.booking_id)
        total = len(items)
        done = sum(1 for i in items if i.is_completed)
        rate = f"{(done / total * 100.0) if total > 0 else 100.0:.2f}"
        return {
            "total_items": total,
            "completed_items": done,
            "completion_rate": rate,
            "items": ChecklistItemResponseSchema(many=True).dump(items)
        }


class TaskSummaryResponseSchema(Schema):
    id = fields.UUID()
    title = fields.String()
    due_date = fields.Date()
    priority = fields.Method("get_priority")
    status = fields.Method("get_status")
    assigned_to = fields.Method("get_assigned_to")

    def get_priority(self, obj) -> str:
        if hasattr(obj, 'priority') and obj.priority:
            return obj.priority.code
        return "MEDIUM"

    def get_status(self, obj) -> str:
        if hasattr(obj, 'status') and obj.status:
            return obj.status.code
        return "PENDING"

    def get_assigned_to(self, obj) -> dict | None:
        if hasattr(obj, 'assigned_to') and obj.assigned_to:
            return {
                "id": str(obj.assigned_to.id),
                "display_name": obj.assigned_to.display_name or obj.assigned_to.name
            }
        return None


class TaskDetailResponseSchema(TaskSummaryResponseSchema):
    booking_id = fields.UUID(allow_none=True)
    lead_id = fields.UUID(allow_none=True)
    description = fields.String()
    completed_date = fields.Date(allow_none=True)
    estimated_hours = fields.Decimal(places=2, as_string=True, allow_none=True)
    actual_hours = fields.Decimal(places=2, as_string=True, allow_none=True)
    assigned_by = fields.Method("get_assigned_by")
    parent_task_id = fields.UUID(allow_none=True)
    subtasks = fields.List(fields.Nested(TaskSummaryResponseSchema))
    audit = fields.Nested(AuditInfoSchema, attribute="self")

    def get_assigned_by(self, obj) -> dict | None:
        if hasattr(obj, 'assigned_by') and obj.assigned_by:
            return {
                "id": str(obj.assigned_by.id),
                "display_name": obj.assigned_by.display_name or obj.assigned_by.name
            }
        return None


class TripCompletionValidationResponseSchema(Schema):
    can_complete = fields.Boolean()
    blocking_reasons = fields.List(fields.String())
    checklist_completion_rate = fields.Decimal(places=2, as_string=True)
    unconfirmed_allocations = fields.Integer()
    open_high_priority_tasks = fields.Integer()
