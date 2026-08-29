from marshmallow import Schema, fields, validate

class LeadSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    phone = fields.String(required=True, validate=validate.Length(min=5, max=20))
    email = fields.Email(allow_none=True)
    lead_type = fields.String(validate=validate.OneOf(["trip_request", "quick_callback", "package_booking"]), allow_none=True, load_default="trip_request")
    package_id = fields.String(allow_none=True)
    preferred_destination = fields.String(allow_none=True, validate=validate.Length(max=255))
    travel_dates = fields.String(allow_none=True, validate=validate.Length(max=50))
    travelers = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    budget = fields.String(allow_none=True, validate=validate.Length(max=50))
    notes = fields.String(allow_none=True)
    status = fields.String(validate=validate.OneOf(["pending", "contacted", "confirmed", "completed"]), allow_none=True)
    trip_type = fields.String(allow_none=True)
    estimated_trip_days = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    male_count = fields.Integer(allow_none=True, validate=validate.Range(min=0))
    female_count = fields.Integer(allow_none=True, validate=validate.Range(min=0))
    faculty_count = fields.Integer(allow_none=True, validate=validate.Range(min=0))

class PackageSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=150))
    description = fields.String(allow_none=True)
    duration_days = fields.Integer(allow_none=True, validate=validate.Range(min=0))
    duration_nights = fields.Integer(allow_none=True, validate=validate.Range(min=0))
    price_per_person = fields.Float(allow_none=True, validate=validate.Range(min=0))
    thumbnail_url = fields.String(allow_none=True, validate=validate.Length(max=255))
    highlights = fields.String(allow_none=True)
    destination_ids = fields.List(fields.Integer(), allow_none=True)

class TaskSchema(Schema):
    assigned_to_id = fields.Integer(allow_none=True)
    linked_lead_id = fields.Integer(allow_none=True)
    description = fields.String(required=True)
    due_date = fields.String(allow_none=True)
    status = fields.String(validate=validate.OneOf(["pending", "in_progress", "completed"]), load_default="pending")

class CustomerSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(allow_none=True)
    phone = fields.String(required=True, validate=validate.Length(min=5, max=20))
    secondary_contact = fields.String(allow_none=True, validate=validate.Length(max=20))
    address = fields.String(allow_none=True)
    preferences = fields.String(allow_none=True)

class BookingSchema(Schema):
    lead_id = fields.Integer(allow_none=True)
    customer_id = fields.Integer(required=True)
    package_id = fields.Integer(allow_none=True)
    start_date = fields.String(allow_none=True)
    end_date = fields.String(allow_none=True)
    total_price = fields.Float(allow_none=True, validate=validate.Range(min=0))
    status = fields.String(validate=validate.OneOf(["pending", "confirmed", "completed", "cancelled"]), load_default="pending")

class DummyModelSchema:
    def load(self, *args, **kwargs):
        pass
    def dump(self, *args, **kwargs):
        pass
