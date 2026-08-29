from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from decimal import Decimal

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

class RecordCustomerPaymentRequestSchema(Schema):
    booking_id = fields.UUID(required=True)
    payment_schedule_id = fields.UUID(allow_none=True)
    payment_date = fields.Date(required=True)
    amount = fields.Decimal(required=True, validate=validate.Range(min=0.01))
    payment_method_id = fields.UUID(required=True)
    payment_type_id = fields.UUID(required=True)
    installment_no = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    transaction_reference = fields.String(allow_none=True, validate=validate.Length(max=100))
    remarks = fields.String(allow_none=True, validate=validate.Length(max=500))

class VerifyPaymentRequestSchema(Schema):
    verification_notes = fields.String(allow_none=True, validate=validate.Length(max=500))

class UploadPaymentReceiptRequestSchema(Schema):
    receipt_url = fields.String(required=True, validate=validate.Length(max=2000))
    storage_provider = fields.String(allow_none=True, validate=validate.OneOf(["S3", "LOCAL"]))

class RecordVendorPaymentRequestSchema(Schema):
    vendor_allocation_id = fields.UUID(required=True)
    payment_date = fields.Date(required=True)
    amount = fields.Decimal(required=True, validate=validate.Range(min=0.01))
    payment_method_id = fields.UUID(required=True)
    transaction_reference = fields.String(allow_none=True, validate=validate.Length(max=100))
    internal_notes = fields.String(allow_none=True, validate=validate.Length(max=500))

class CreateExpenseRequestSchema(Schema):
    booking_id = fields.UUID(required=True)
    vendor_allocation_id = fields.UUID(allow_none=True)
    expense_category_id = fields.UUID(required=True)
    expense_type_id = fields.UUID(required=True)
    amount = fields.Decimal(required=True, validate=validate.Range(min=0.01))
    expense_date = fields.Date(required=True)
    expense_description = fields.String(allow_none=True, validate=validate.Length(max=255))
    remarks = fields.String(allow_none=True, validate=validate.Length(max=500))

class CreateRefundRequestSchema(Schema):
    booking_id = fields.UUID(required=True)
    amount = fields.Decimal(required=True, validate=validate.Range(min=0.01))
    refund_date = fields.Date(allow_none=True)
    payment_method_id = fields.UUID(required=True)
    transaction_reference = fields.String(allow_none=True, validate=validate.Length(max=100))
    remarks = fields.String(allow_none=True, validate=validate.Length(max=500))

class CloseBookingFinanceRequestSchema(Schema):
    closing_notes = fields.String(allow_none=True, validate=validate.Length(max=1000))

# Response Schemas

class PaymentDetailResponseSchema(Schema):
    id = fields.UUID()
    booking_id = fields.UUID()
    booking_number = fields.Method("get_booking_number")
    payment_schedule_id = fields.UUID(allow_none=True)
    payment_date = fields.Date()
    amount = fields.Decimal(as_string=True)
    payment_method = fields.Nested(SimpleLookupResponseSchema)
    payment_type = fields.Nested(SimpleLookupResponseSchema)
    payment_status = fields.Nested(SimpleLookupResponseSchema, attribute="status")
    installment_no = fields.Integer(allow_none=True)
    transaction_reference = fields.String(allow_none=True)
    receipt_url = fields.String(allow_none=True)
    received_by = fields.Nested(AuditRefSchema, attribute="creator")
    verified_by = fields.Nested(AuditRefSchema, allow_none=True)
    remarks = fields.String(allow_none=True)
    created_at = fields.DateTime()

    def get_booking_number(self, obj) -> str:
        from app.core.extensions import db
        from app.models import Booking
        booking = db.session.get(Booking, obj.booking_id)
        return booking.booking_number if booking else "Unknown"

class VendorPaymentDetailResponseSchema(Schema):
    id = fields.UUID()
    vendor_allocation_id = fields.UUID()
    vendor_name = fields.Method("get_vendor_name")
    service_name = fields.Method("get_service_name")
    payment_date = fields.Date()
    amount = fields.Decimal(as_string=True)
    payment_method = fields.Nested(SimpleLookupResponseSchema)
    payment_status = fields.Nested(SimpleLookupResponseSchema)
    transaction_reference = fields.String(allow_none=True)
    receipt_url = fields.String(allow_none=True)
    internal_notes = fields.String(allow_none=True)
    created_at = fields.DateTime()

    def get_vendor_name(self, obj) -> str:
        alloc = obj.vendor_allocation
        if alloc:
            if alloc.vendor_name_snapshot:
                return alloc.vendor_name_snapshot
            if alloc.vendor:
                return alloc.vendor.vendor_name
        return "Unknown Vendor"

    def get_service_name(self, obj) -> str:
        alloc = obj.vendor_allocation
        return alloc.service_name if alloc else "Unknown Service"

class ExpenseDetailResponseSchema(Schema):
    id = fields.UUID()
    booking_id = fields.UUID()
    booking_number = fields.Method("get_booking_number")
    vendor_allocation_id = fields.UUID(allow_none=True)
    expense_category = fields.Nested(SimpleLookupResponseSchema)
    expense_type = fields.Nested(SimpleLookupResponseSchema)
    amount = fields.Decimal(as_string=True)
    expense_date = fields.Date()
    expense_description = fields.String(allow_none=True)
    remarks = fields.String(allow_none=True)
    approved_by = fields.Nested(AuditRefSchema, allow_none=True)
    created_at = fields.DateTime()

    def get_booking_number(self, obj) -> str:
        from app.core.extensions import db
        from app.models import Booking
        booking = db.session.get(Booking, obj.booking_id)
        return booking.booking_number if booking else "Unknown"

class RefundDetailResponseSchema(Schema):
    id = fields.UUID()
    booking_id = fields.UUID()
    booking_number = fields.Method("get_booking_number")
    refund_status = fields.Nested(SimpleLookupResponseSchema)
    amount = fields.Decimal(as_string=True)
    refund_date = fields.Date()
    payment_method = fields.Nested(SimpleLookupResponseSchema)
    transaction_reference = fields.String(allow_none=True)
    remarks = fields.String(allow_none=True)
    created_at = fields.DateTime()

    def get_booking_number(self, obj) -> str:
        from app.core.extensions import db
        from app.models import Booking
        booking = db.session.get(Booking, obj.booking_id)
        return booking.booking_number if booking else "Unknown"

class BookingFinanceSummaryResponseSchema(Schema):
    booking_id = fields.UUID()
    booking_number = fields.String()
    total_amount = fields.Decimal(as_string=True)
    total_paid = fields.Decimal(as_string=True)
    outstanding_balance = fields.Decimal(as_string=True)
    vendor_cost = fields.Decimal(as_string=True)
    vendor_amount_paid = fields.Decimal(as_string=True)
    vendor_balance_due = fields.Decimal(as_string=True)
    operational_expenses = fields.Decimal(as_string=True)
    refunds_issued = fields.Decimal(as_string=True)
    net_revenue = fields.Decimal(as_string=True)
    total_cost = fields.Decimal(as_string=True)
    gross_profit = fields.Decimal(as_string=True)
    profit_margin_percentage = fields.Decimal(as_string=True)
    finance_status = fields.String()

class InstallmentScheduleItemSchema(Schema):
    id = fields.UUID()
    installment_no = fields.Integer()
    due_date = fields.Date()
    amount = fields.Decimal(as_string=True)
    percentage = fields.Decimal(as_string=True)
    payment_status = fields.Nested(SimpleLookupResponseSchema)
    remarks = fields.String(allow_none=True)

class InstallmentScheduleResponseSchema(Schema):
    booking_id = fields.UUID()
    booking_number = fields.String()
    total_amount = fields.Decimal(as_string=True)
    total_paid = fields.Decimal(as_string=True)
    outstanding_balance = fields.Decimal(as_string=True)
    schedules = fields.List(fields.Nested(InstallmentScheduleItemSchema))

class OutstandingPaymentResponseSchema(Schema):
    booking_id = fields.UUID()
    booking_number = fields.String()
    customer_name = fields.String()
    total_amount = fields.Decimal(as_string=True)
    total_paid = fields.Decimal(as_string=True)
    outstanding_balance = fields.Decimal(as_string=True)
    next_due_date = fields.Date(allow_none=True)
    booking_status = fields.String()

class UpcomingInstallmentResponseSchema(Schema):
    schedule_id = fields.UUID()
    booking_id = fields.UUID()
    booking_number = fields.String()
    customer_name = fields.String()
    installment_no = fields.Integer()
    due_date = fields.Date()
    amount = fields.Decimal(as_string=True)
    payment_status = fields.String()

class PendingVendorPaymentResponseSchema(Schema):
    vendor_allocation_id = fields.UUID()
    booking_id = fields.UUID()
    booking_number = fields.String()
    vendor_name = fields.String()
    service_name = fields.String()
    service_date = fields.Date()
    quoted_amount = fields.Decimal(as_string=True)
    confirmed_price = fields.Decimal(as_string=True)
    amount_paid = fields.Decimal(as_string=True)
    balance_due = fields.Decimal(as_string=True)
    allocation_status = fields.String()
