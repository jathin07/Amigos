import uuid
from flask import Blueprint, request
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity

from app.modules.auth.permissions import permission_required
from app.domain.exceptions import NotFoundException, ValidationException, BusinessException
from .schemas import (
    RecordCustomerPaymentRequestSchema,
    VerifyPaymentRequestSchema,
    UploadPaymentReceiptRequestSchema,
    RecordVendorPaymentRequestSchema,
    CreateExpenseRequestSchema,
    CreateRefundRequestSchema,
    CloseBookingFinanceRequestSchema,
    PaymentDetailResponseSchema,
    VendorPaymentDetailResponseSchema,
    ExpenseDetailResponseSchema,
    RefundDetailResponseSchema,
    BookingFinanceSummaryResponseSchema,
    InstallmentScheduleResponseSchema,
    OutstandingPaymentResponseSchema,
    UpcomingInstallmentResponseSchema,
    PendingVendorPaymentResponseSchema
)
from .service import FinanceService

finance_bp = Blueprint("finance", __name__)

def _flatten_errors(messages: dict) -> list[dict]:
    errors = []
    for field, msgs in messages.items():
        if isinstance(msgs, dict):
            for subfield, submsgs in msgs.items():
                for submsg in (submsgs if isinstance(submsgs, list) else [submsgs]):
                    errors.append({"code": "ERR_VALIDATION", "field": f"{field}.{subfield}", "message": str(submsg)})
        elif isinstance(msgs, list):
            for item in msgs:
                if isinstance(item, dict):
                    for subfield, submsgs in item.items():
                        for submsg in (submsgs if isinstance(submsgs, list) else [submsgs]):
                            errors.append({"code": "ERR_VALIDATION", "field": f"{field}.{subfield}", "message": str(submsg)})
                else:
                    errors.append({"code": "ERR_VALIDATION", "field": field, "message": str(item)})
        else:
            errors.append({"code": "ERR_VALIDATION", "field": field, "message": str(messages[field])})
    return errors

def _get_context_team_member_id() -> uuid.UUID | None:
    try:
        identity = get_jwt_identity()
    except RuntimeError:
        identity = None
    if not identity:
        return None
    try:
        from app.models import UserAccount
        from app.core.extensions import db
        user = db.session.get(UserAccount, uuid.UUID(str(identity)))
        return user.team_member_id if user else None
    except ValueError:
        return None

# --- Customer Payments ---

@finance_bp.route("/bookings/<uuid:id>/payments", methods=["GET"])
@permission_required("finance.payment.read")
def get_booking_payments(id):
    service = FinanceService()
    from .repository import PaymentRepository
    payments_list = PaymentRepository().get_by_booking_id(id)
    response_data = PaymentDetailResponseSchema(many=True).dump(payments_list)
    return service.success(data=response_data, message="Payments retrieved successfully.")

@finance_bp.route("/payments", methods=["POST"])
@permission_required("finance.payment.create")
def record_customer_payment():
    payload = request.get_json(silent=True) or {}
    try:
        data = RecordCustomerPaymentRequestSchema().load(payload)
    except ValidationError as err:
        errors = _flatten_errors(err.messages)
        service = FinanceService()
        return service.error(message="Request validation failed.", code="VALIDATION_ERROR", errors=errors, status_code=422)

    service = FinanceService()
    actor_id = _get_context_team_member_id()
    payment = service.record_customer_payment(data, actor_id)
    response_data = PaymentDetailResponseSchema().dump(payment)
    return service.success(data=response_data, message="Payment recorded successfully.", status_code=201)

@finance_bp.route("/payments/<uuid:payment_id>/verify", methods=["PATCH"])
@permission_required("finance.payment.verify")
def verify_payment(payment_id):
    payload = request.get_json(silent=True) or {}
    try:
        data = VerifyPaymentRequestSchema().load(payload)
    except ValidationError as err:
        errors = _flatten_errors(err.messages)
        service = FinanceService()
        return service.error(message="Request validation failed.", code="VALIDATION_ERROR", errors=errors, status_code=422)

    service = FinanceService()
    actor_id = _get_context_team_member_id()
    payment = service.verify_payment(payment_id, data, actor_id)
    response_data = PaymentDetailResponseSchema().dump(payment)
    return service.success(data=response_data, message="Payment verified successfully.")

@finance_bp.route("/payments/<uuid:payment_id>/attachments", methods=["POST"])
@permission_required("finance.payment.create")
def upload_payment_receipt(payment_id):
    payload = request.get_json(silent=True) or {}
    try:
        data = UploadPaymentReceiptRequestSchema().load(payload)
    except ValidationError as err:
        errors = _flatten_errors(err.messages)
        service = FinanceService()
        return service.error(message="Request validation failed.", code="VALIDATION_ERROR", errors=errors, status_code=422)

    service = FinanceService()
    actor_id = _get_context_team_member_id()
    payment = service.upload_receipt(payment_id, data, actor_id)
    response_data = PaymentDetailResponseSchema().dump(payment)
    return service.success(data=response_data, message="Payment receipt uploaded successfully.")

# --- Vendor Payments ---

@finance_bp.route("/bookings/<uuid:id>/vendor-payments", methods=["GET"])
@permission_required("finance.vendor_payment.read")
def get_booking_vendor_payments(id):
    service = FinanceService()
    from .repository import VendorPaymentRepository
    vps = VendorPaymentRepository().get_by_booking_id(id)
    response_data = VendorPaymentDetailResponseSchema(many=True).dump(vps)
    return service.success(data=response_data, message="Vendor payments retrieved successfully.")

@finance_bp.route("/vendor-payments", methods=["POST"])
@permission_required("finance.vendor_payment.create")
def record_vendor_payment():
    payload = request.get_json(silent=True) or {}
    try:
        data = RecordVendorPaymentRequestSchema().load(payload)
    except ValidationError as err:
        errors = _flatten_errors(err.messages)
        service = FinanceService()
        return service.error(message="Request validation failed.", code="VALIDATION_ERROR", errors=errors, status_code=422)

    service = FinanceService()
    actor_id = _get_context_team_member_id()
    vp = service.record_vendor_payment(data, actor_id)
    response_data = VendorPaymentDetailResponseSchema().dump(vp)
    return service.success(data=response_data, message="Vendor payment recorded successfully.", status_code=201)

# --- Expenses ---

@finance_bp.route("/bookings/<uuid:id>/expenses", methods=["GET"])
@permission_required("finance.expense.read")
def get_booking_expenses(id):
    service = FinanceService()
    from .repository import ExpenseRepository
    expenses = ExpenseRepository().get_by_booking_id(id)
    response_data = ExpenseDetailResponseSchema(many=True).dump(expenses)
    return service.success(data=response_data, message="Expenses retrieved successfully.")

@finance_bp.route("/expenses", methods=["POST"])
@permission_required("finance.expense.create")
def log_expense():
    payload = request.get_json(silent=True) or {}
    try:
        data = CreateExpenseRequestSchema().load(payload)
    except ValidationError as err:
        errors = _flatten_errors(err.messages)
        service = FinanceService()
        return service.error(message="Request validation failed.", code="VALIDATION_ERROR", errors=errors, status_code=422)

    service = FinanceService()
    actor_id = _get_context_team_member_id()
    expense = service.create_expense(data, actor_id)
    response_data = ExpenseDetailResponseSchema().dump(expense)
    return service.success(data=response_data, message="Expense logged successfully.", status_code=201)

@finance_bp.route("/expenses/<uuid:expense_id>", methods=["DELETE"])
@permission_required("finance.expense.delete")
def delete_expense(expense_id):
    service = FinanceService()
    actor_id = _get_context_team_member_id()
    service.delete_expense(expense_id, actor_id)
    return service.success(message="Expense deleted successfully.")

# --- Refunds ---

@finance_bp.route("/bookings/<uuid:id>/refunds", methods=["GET"])
@permission_required("finance.refund.read")
def get_booking_refunds(id):
    service = FinanceService()
    from .repository import RefundRepository
    refunds = RefundRepository().get_by_booking_id(id)
    response_data = RefundDetailResponseSchema(many=True).dump(refunds)
    return service.success(data=response_data, message="Refunds retrieved successfully.")

@finance_bp.route("/refunds", methods=["POST"])
@permission_required("finance.refund.create")
def create_refund():
    payload = request.get_json(silent=True) or {}
    try:
        data = CreateRefundRequestSchema().load(payload)
    except ValidationError as err:
        errors = _flatten_errors(err.messages)
        service = FinanceService()
        return service.error(message="Request validation failed.", code="VALIDATION_ERROR", errors=errors, status_code=422)

    service = FinanceService()
    actor_id = _get_context_team_member_id()
    refund = service.create_refund(data, actor_id)
    response_data = RefundDetailResponseSchema().dump(refund)
    return service.success(data=response_data, message="Refund request created successfully.", status_code=201)

@finance_bp.route("/refunds/<uuid:refund_id>/status", methods=["PATCH"])
@permission_required("finance.refund.create")
def transition_refund_status(refund_id):
    payload = request.get_json(silent=True) or {}
    target_status = payload.get("status")
    service = FinanceService()
    if not target_status:
        return service.error(message="status field is required.", code="VALIDATION_ERROR", status_code=422)
    actor_id = _get_context_team_member_id()
    refund = service.transition_refund_status(refund_id, target_status, actor_id)
    response_data = RefundDetailResponseSchema().dump(refund)
    return service.success(data=response_data, message=f"Refund transition to {target_status} successful.")

# --- Analytics and Schedules ---

@finance_bp.route("/bookings/<uuid:id>/profit-summary", methods=["GET"])
@permission_required("finance.profit_summary.read")
def get_booking_profit_summary(id):
    service = FinanceService()
    summary = service.get_profit_summary(id)
    response_data = BookingFinanceSummaryResponseSchema().dump(summary)
    return service.success(data=response_data, message="Profit summary retrieved successfully.")

@finance_bp.route("/bookings/<uuid:id>/installment-schedule", methods=["GET"])
@permission_required("finance.payment.read")
def get_booking_installment_schedule(id):
    service = FinanceService()
    sched = service.get_installment_schedule(id)
    response_data = InstallmentScheduleResponseSchema().dump(sched)
    return service.success(data=response_data, message="Installment schedule retrieved successfully.")

@finance_bp.route("/outstanding-payments", methods=["GET"])
@permission_required("finance.payment.read")
def get_outstanding_payments():
    service = FinanceService()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    outstanding, total = service.list_outstanding_payments(page, per_page)
    response_data = OutstandingPaymentResponseSchema(many=True).dump(outstanding)
    return service.success(data=response_data, meta={"total": total, "page": page, "per_page": per_page}, message="Outstanding payments retrieved successfully.")

@finance_bp.route("/upcoming-installments", methods=["GET"])
@permission_required("finance.payment.read")
def get_upcoming_installments():
    service = FinanceService()
    installments = service.list_upcoming_installments()
    response_data = UpcomingInstallmentResponseSchema(many=True).dump(installments)
    return service.success(data=response_data, message="Upcoming installments retrieved successfully.")

@finance_bp.route("/pending-vendor-payments", methods=["GET"])
@permission_required("finance.vendor_payment.read")
def get_pending_vendor_payments():
    service = FinanceService()
    pending = service.list_pending_vendor_payments()
    response_data = PendingVendorPaymentResponseSchema(many=True).dump(pending)
    return service.success(data=response_data, message="Pending vendor payments retrieved successfully.")

# --- Close Finance ---

@finance_bp.route("/bookings/<uuid:id>/close", methods=["POST"])
@permission_required("finance.close")
def close_finance(id):
    payload = request.get_json(silent=True) or {}
    try:
        data = CloseBookingFinanceRequestSchema().load(payload)
    except ValidationError as err:
        errors = _flatten_errors(err.messages)
        service = FinanceService()
        return service.error(message="Request validation failed.", code="VALIDATION_ERROR", errors=errors, status_code=422)

    service = FinanceService()
    actor_id = _get_context_team_member_id()
    booking = service.close_finance(id, data, actor_id)
    from app.models import BookingStatus
    status_name = booking.status.name if booking.status else "Closed"
    return service.success(data={"booking_id": str(booking.id), "status": status_name}, message="Booking finance ledger closed successfully.")
