from marshmallow import Schema, fields, validate

class LeadSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    phone = fields.String(required=True, validate=validate.Length(min=5, max=20))
    email = fields.Email(allow_none=True)
    lead_type = fields.String(validate=validate.OneOf(["trip_request", "quick_callback", "package_booking"]), allow_none=True, load_default="trip_request")
    package_id = fields.Integer(allow_none=True)
    preferred_destination = fields.String(allow_none=True, validate=validate.Length(max=255))
    travel_dates = fields.String(allow_none=True, validate=validate.Length(max=50))
    travelers = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    budget = fields.String(allow_none=True, validate=validate.Length(max=50))
    notes = fields.String(allow_none=True)
    status = fields.String(validate=validate.OneOf(["pending", "contacted", "confirmed", "completed"]), allow_none=True)

class PackageSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=150))
    description = fields.String(allow_none=True)
    duration_days = fields.Integer(allow_none=True, validate=validate.Range(min=0))
    duration_nights = fields.Integer(allow_none=True, validate=validate.Range(min=0))
    price_per_person = fields.Float(allow_none=True, validate=validate.Range(min=0))
    thumbnail_url = fields.String(allow_none=True, validate=validate.Length(max=255))
    highlights = fields.String(allow_none=True)
    destination_ids = fields.List(fields.Integer(), allow_none=True)

class TripFinanceSchema(Schema):
    lead_id = fields.Integer(required=True)
    revenue = fields.Float(allow_none=True, load_default=0.0)
    transport_cost = fields.Float(allow_none=True, load_default=0.0)
    hotel_cost = fields.Float(allow_none=True, load_default=0.0)
    food_cost = fields.Float(allow_none=True, load_default=0.0)
    activity_cost = fields.Float(allow_none=True, load_default=0.0)
    other_cost = fields.Float(allow_none=True, load_default=0.0)

class TaskSchema(Schema):
    assigned_to_id = fields.Integer(allow_none=True)
    linked_lead_id = fields.Integer(allow_none=True)
    description = fields.String(required=True)
    due_date = fields.String(allow_none=True)
    status = fields.String(validate=validate.OneOf(["pending", "in_progress", "completed"]), load_default="pending")
