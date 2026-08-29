from marshmallow import Schema, fields, validates_schema, ValidationError
from datetime import date, timedelta
import uuid

class ReportFilterSchema(Schema):
    date_from = fields.Date(required=True, error_messages={"required": "date_from is required."})
    date_to = fields.Date(required=True, error_messages={"required": "date_to is required."})
    team_member_id = fields.UUID(allow_none=True)
    booking_status = fields.String(allow_none=True)
    format = fields.String(load_default="json")
    page = fields.Integer(load_default=1)
    per_page = fields.Integer(load_default=50)
    sort_by = fields.String(allow_none=True)
    sort_order = fields.String(load_default="desc")

    @validates_schema
    def validate_filters(self, data, **kwargs):
        date_from = data.get("date_from")
        date_to = data.get("date_to")

        if date_from and date_to:
            if date_from > date_to:
                raise ValidationError(
                    {"date_to": "Date range is invalid. End date must be after start date."},
                    "INVALID_DATE_RANGE"
                )
            if (date_to - date_from) > timedelta(days=730):
                raise ValidationError(
                    {"date_to": "Date range must not exceed 2 years."},
                    "REPORT_DATE_RANGE_TOO_WIDE"
                )

        page = data.get("page")
        if page is not None and page <= 0:
            raise ValidationError({"page": "Page must be a positive integer."}, "VALIDATION_ERROR")

        per_page = data.get("per_page")
        if per_page is not None and (per_page <= 0 or per_page > 200):
            raise ValidationError({"per_page": "per_page must be between 1 and 200."}, "VALIDATION_ERROR")

        sort_order = data.get("sort_order")
        if sort_order and sort_order.lower() not in ["asc", "desc"]:
            raise ValidationError({"sort_order": "sort_order must be 'asc' or 'desc'."}, "VALIDATION_ERROR")

        fmt = data.get("format")
        if fmt and fmt.lower() not in ["json", "csv", "xlsx", "pdf"]:
            raise ValidationError({"format": "Requested export format is not supported."}, "UNSUPPORTED_FORMAT")


class ReportJobDataSchema(Schema):
    job_id = fields.UUID(attribute="id")
    report_type = fields.String()
    status = fields.String()
    progress_percentage = fields.Float()
    file_url = fields.String(allow_none=True)
    expires_at = fields.DateTime(allow_none=True)
    created_at = fields.DateTime()
    row_count = fields.Integer(allow_none=True)
    file_size_bytes = fields.Integer(allow_none=True)
    error_details = fields.String(allow_none=True)
    started_at = fields.DateTime(allow_none=True)
    completed_at = fields.DateTime(allow_none=True)
    execution_time_ms = fields.Integer(allow_none=True)
    download_count = fields.Integer()
    last_downloaded_at = fields.DateTime(allow_none=True)

class ReportJobResponseSchema(Schema):
    status = fields.String(dump_default="success")
    data = fields.Nested(ReportJobDataSchema)

class AsyncJobInitiatedSchema(Schema):
    status = fields.String(dump_default="accepted")
    message = fields.String(dump_default="Report dataset exceeds synchronous execution limit. Export job queued.")
    data = fields.Nested(ReportJobDataSchema)


# --- Synchronous Data Schemas ---

class BookingBreakdownSchema(Schema):
    booking_id = fields.String()
    booking_number = fields.String()
    group_name = fields.String()
    trip_start_date = fields.String()
    total_amount = fields.Float()
    revenue_collected = fields.Float()
    vendor_cost = fields.Float()
    operational_expense = fields.Float()
    refund_amount = fields.Float()
    gross_profit = fields.Float()
    profit_margin_percentage = fields.Float()
    outstanding_balance = fields.Float()
    status = fields.String()

class FinanceProfitLossReportDataSchema(Schema):
    report_period_from = fields.String()
    report_period_to = fields.String()
    total_bookings_analyzed = fields.Integer()
    total_revenue = fields.Float()
    total_refunds = fields.Float()
    net_revenue = fields.Float()
    total_vendor_costs = fields.Float()
    total_operational_expenses = fields.Float()
    total_costs = fields.Float()
    gross_profit = fields.Float()
    profit_margin_percentage = fields.Float()
    outstanding_customer_balance = fields.Float()
    pending_vendor_disbursements = fields.Float()
    booking_breakdown = fields.List(fields.Nested(BookingBreakdownSchema))
    generated_at = fields.String()

class FinanceProfitLossReportResponseSchema(Schema):
    status = fields.String(dump_default="success")
    data = fields.Nested(FinanceProfitLossReportDataSchema)


# --- CRM Conversion Report ---

class LeadSourceBreakdownSchema(Schema):
    source = fields.String()
    leads = fields.Integer()
    won = fields.Integer()
    conversion_rate = fields.Float()

class TeamMemberBreakdownSchema(Schema):
    team_member_id = fields.String()
    name = fields.String()
    leads_assigned = fields.Integer()
    won = fields.Integer()
    conversion_rate = fields.Float()

class CRMConversionReportDataSchema(Schema):
    report_period_from = fields.String()
    report_period_to = fields.String()
    total_leads_created = fields.Integer()
    total_leads_won = fields.Integer()
    total_leads_lost = fields.Integer()
    total_leads_active = fields.Integer()
    conversion_rate_percentage = fields.Float()
    average_lead_age_days = fields.Float()
    average_deal_size = fields.Float()
    lead_source_breakdown = fields.List(fields.Nested(LeadSourceBreakdownSchema))
    team_member_breakdown = fields.List(fields.Nested(TeamMemberBreakdownSchema))
    generated_at = fields.String()

class CRMConversionReportResponseSchema(Schema):
    status = fields.String(dump_default="success")
    data = fields.Nested(CRMConversionReportDataSchema)


# --- Booking Trends Report ---

class MonthlyTrendItemSchema(Schema):
    month = fields.String()
    bookings_created = fields.Integer()
    bookings_completed = fields.Integer()
    total_revenue = fields.Float()

class TripTypeBreakdownItemSchema(Schema):
    trip_type = fields.String()
    count = fields.Integer()
    percentage = fields.Float()

class TopDestinationItemSchema(Schema):
    destination = fields.String()
    booking_count = fields.Integer()
    percentage = fields.Float()

class BookingTrendsReportDataSchema(Schema):
    report_period_from = fields.String()
    report_period_to = fields.String()
    total_bookings = fields.Integer()
    total_travelers_served = fields.Integer()
    average_group_size = fields.Float()
    average_booking_value = fields.Float()
    monthly_trends = fields.List(fields.Nested(MonthlyTrendItemSchema))
    trip_type_breakdown = fields.List(fields.Nested(TripTypeBreakdownItemSchema))
    top_destinations = fields.List(fields.Nested(TopDestinationItemSchema))
    generated_at = fields.String()

class BookingTrendsReportResponseSchema(Schema):
    status = fields.String(dump_default="success")
    data = fields.Nested(BookingTrendsReportDataSchema)


# --- Customer History Report ---

class TopCustomerItemSchema(Schema):
    customer_id = fields.String()
    customer_name = fields.String()
    total_bookings = fields.Integer()
    total_revenue = fields.Float()
    last_trip_date = fields.String()
    preferred_destinations = fields.List(fields.String())

class CustomerHistoryReportDataSchema(Schema):
    report_period_from = fields.String()
    report_period_to = fields.String()
    total_unique_customers = fields.Integer()
    repeat_customers = fields.Integer()
    repeat_customer_rate_percentage = fields.Float()
    top_customers = fields.List(fields.Nested(TopCustomerItemSchema))
    generated_at = fields.String()

class CustomerHistoryReportResponseSchema(Schema):
    status = fields.String(dump_default="success")
    data = fields.Nested(CustomerHistoryReportDataSchema)


# --- Operations Efficiency Report ---

class CoordinatorPerformanceItemSchema(Schema):
    coordinator_id = fields.String()
    coordinator_name = fields.String()
    trips_managed = fields.Integer()
    average_checklist_completion = fields.Float()
    on_time_trips = fields.Integer()
    delayed_trips = fields.Integer()

class OperationsEfficiencyReportDataSchema(Schema):
    report_period_from = fields.String()
    report_period_to = fields.String()
    total_trip_plans_analyzed = fields.Integer()
    average_checklist_completion_rate = fields.Float()
    trips_delayed_by_checklist = fields.Integer()
    average_vendor_allocations_per_trip = fields.Float()
    vendor_settlement_rate_percentage = fields.Float()
    coordinator_performance = fields.List(fields.Nested(CoordinatorPerformanceItemSchema))
    generated_at = fields.String()

class OperationsEfficiencyReportResponseSchema(Schema):
    status = fields.String(dump_default="success")
    data = fields.Nested(OperationsEfficiencyReportDataSchema)


# --- Vendor Payment Report ---

class VendorBreakdownItemSchema(Schema):
    vendor_id = fields.String()
    vendor_name = fields.String()
    total_allocations = fields.Integer()
    total_confirmed_value = fields.Float()
    total_paid = fields.Float()
    balance_due = fields.Float()
    settlement_rate = fields.Float()

class VendorPaymentReportDataSchema(Schema):
    report_period_from = fields.String()
    report_period_to = fields.String()
    total_vendor_allocations = fields.Integer()
    total_quoted_value = fields.Float()
    total_confirmed_value = fields.Float()
    total_disbursed = fields.Float()
    total_pending = fields.Float()
    settlement_rate_percentage = fields.Float()
    vendor_breakdown = fields.List(fields.Nested(VendorBreakdownItemSchema))
    generated_at = fields.String()

class VendorPaymentReportResponseSchema(Schema):
    status = fields.String(dump_default="success")
    data = fields.Nested(VendorPaymentReportDataSchema)
