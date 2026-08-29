from marshmallow import Schema, fields

class SummaryCardsDataSchema(Schema):
    active_leads = fields.Integer()
    open_proposals = fields.Integer()
    confirmed_bookings = fields.Integer()
    trips_today = fields.Integer()
    outstanding_payments = fields.Integer()
    pending_vendor_payments = fields.Integer()
    revenue_this_month = fields.Float()
    profit_this_month = fields.Float()

class SummaryCardsResponseSchema(Schema):
    status = fields.String(dump_default="success")
    message = fields.String(dump_default="Summary cards retrieved successfully.")
    data = fields.Nested(SummaryCardsDataSchema)
    generated_at = fields.String()
    as_of = fields.String()
    cache_ttl = fields.Integer()
    cache_status = fields.String()

class LeadFunnelItemSchema(Schema):
    status = fields.String()
    count = fields.Integer()
    percentage = fields.Float()
    color = fields.String()

class LeadPipelineResponseSchema(Schema):
    status = fields.String(dump_default="success")
    message = fields.String(dump_default="Lead pipeline retrieved successfully.")
    data = fields.List(fields.Nested(LeadFunnelItemSchema))
    generated_at = fields.String()
    as_of = fields.String()
    cache_ttl = fields.Integer()
    cache_status = fields.String()

class BookingFunnelItemSchema(Schema):
    status = fields.String()
    count = fields.Integer()
    percentage = fields.Float()

class BookingPipelineResponseSchema(Schema):
    status = fields.String(dump_default="success")
    message = fields.String(dump_default="Booking pipeline retrieved successfully.")
    data = fields.List(fields.Nested(BookingFunnelItemSchema))
    generated_at = fields.String()
    as_of = fields.String()
    cache_ttl = fields.Integer()
    cache_status = fields.String()

class FinanceSummaryDataSchema(Schema):
    collected = fields.Float()
    outstanding = fields.Float()
    vendor_due = fields.Float()
    expenses = fields.Float()
    refunds = fields.Float()
    net_profit = fields.Float()
    gross_margin_percentage = fields.Float()

class FinanceSummaryResponseSchema(Schema):
    status = fields.String(dump_default="success")
    message = fields.String(dump_default="Finance summary retrieved successfully.")
    data = fields.Nested(FinanceSummaryDataSchema)
    generated_at = fields.String()
    as_of = fields.String()
    cache_ttl = fields.Integer()
    cache_status = fields.String()

class UpcomingTripItemSchema(Schema):
    booking_number = fields.String()
    customer = fields.String()
    destination = fields.String()
    coordinator = fields.String()
    departure = fields.String()
    remaining_days = fields.Integer()

class PaginationSchema(Schema):
    page = fields.Integer()
    page_size = fields.Integer()
    total_items = fields.Integer()
    total_pages = fields.Integer()

class UpcomingTripsDataSchema(Schema):
    upcoming_trips = fields.List(fields.Nested(UpcomingTripItemSchema))
    pagination = fields.Nested(PaginationSchema)

class UpcomingTripsResponseSchema(Schema):
    status = fields.String(dump_default="success")
    message = fields.String(dump_default="Upcoming trips retrieved successfully.")
    data = fields.Nested(UpcomingTripsDataSchema)
    generated_at = fields.String()
    as_of = fields.String()
    cache_ttl = fields.Integer()
    cache_status = fields.String()

class OperationsOverviewItemSchema(Schema):
    coordinator_id = fields.String()
    coordinator = fields.String()
    trips_assigned = fields.Integer()
    open_tasks = fields.Integer()
    pending_checklist = fields.Integer()
    pending_vendors = fields.Integer()

class OperationsOverviewResponseSchema(Schema):
    status = fields.String(dump_default="success")
    message = fields.String(dump_default="Operations overview retrieved successfully.")
    data = fields.List(fields.Nested(OperationsOverviewItemSchema))
    generated_at = fields.String()
    as_of = fields.String()
    cache_ttl = fields.Integer()
    cache_status = fields.String()

class MonthlyRevenueTrendItemSchema(Schema):
    month = fields.String()
    collected = fields.Float()
    refund = fields.Float()
    expenses = fields.Float()
    profit = fields.Float()
    bookings_count = fields.Integer()

class MonthlyRevenueTrendDataSchema(Schema):
    trend_months = fields.List(fields.Nested(MonthlyRevenueTrendItemSchema))
    period = fields.String(dump_default="6M")

class MonthlyRevenueTrendResponseSchema(Schema):
    status = fields.String(dump_default="success")
    message = fields.String(dump_default="Revenue trend retrieved successfully.")
    data = fields.Nested(MonthlyRevenueTrendDataSchema)
    generated_at = fields.String()
    as_of = fields.String()
    cache_ttl = fields.Integer()
    cache_status = fields.String()
