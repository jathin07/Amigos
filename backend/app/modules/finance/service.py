import uuid
import logging
from datetime import datetime, timezone, date
from decimal import Decimal
from typing import List, Tuple
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload

from app.core.base_service import BaseService
from app.domain.exceptions import NotFoundException, ValidationException, BusinessException
from app.domain.events import DomainEvent
from app.workflow.engine import event_bus
from app.core.extensions import db
from app.models import (
    Booking,
    BookingStatus,
    Payment,
    PaymentStatus,
    PaymentMethod,
    PaymentType,
    PaymentSchedule,
    VendorPayment,
    VendorAllocation,
    TripPlan,
    TripDay,
    Expense,
    ExpenseCategory,
    ExpenseType,
    Refund,
    RefundStatus,
    TeamMember
)

logger = logging.getLogger(__name__)

class FinanceService(BaseService):
    """
    Service handling all financial logic: customer payments, vendor disbursements,
    operational expenses, refunds, and derived P&L reporting.
    """

    # --- Lookups Resolvers ---
    def _resolve_payment_status(self, code: str) -> PaymentStatus:
        stmt = select(PaymentStatus).where(PaymentStatus.code == code)
        status = db.session.scalar(stmt)
        if not status:
            status = PaymentStatus(code=code, name=code.replace("_", " ").title(), is_active=True)
            db.session.add(status)
            db.session.flush()
        return status

    def _resolve_refund_status(self, code: str) -> RefundStatus:
        stmt = select(RefundStatus).where(RefundStatus.code == code)
        status = db.session.scalar(stmt)
        if not status:
            status = RefundStatus(code=code, name=code.replace("_", " ").title(), is_active=True)
            db.session.add(status)
            db.session.flush()
        return status

    # --- Customer Payments ---
    def record_customer_payment(self, data: dict, actor_id: uuid.UUID | str) -> Payment:
        """Command: Record customer payment transaction."""
        booking_id = data["booking_id"]
        booking = db.session.get(Booking, booking_id)
        if not booking or booking.is_deleted:
            raise NotFoundException("Booking not found.")

        # Payment date guard
        payment_date = data["payment_date"]
        if isinstance(payment_date, str):
            payment_date = datetime.strptime(payment_date, "%Y-%m-%d").date()
        if payment_date > date.today():
            raise ValidationException("Payment date cannot be in the future.", code="INVALID_DATE")

        amount = Decimal(str(data["amount"]))
        ref = data.get("transaction_reference")

        # Duplicate payment check
        if ref:
            stmt_dup = select(func.count(Payment.id)).where(
                Payment.booking_id == booking_id,
                Payment.amount == amount,
                Payment.transaction_reference == ref
            )
            if db.session.scalar(stmt_dup) > 0:
                raise BusinessException("Duplicate payment reference number.", code="DUPLICATE_PAYMENT_REFERENCE")

        # Outstanding balance guard
        stmt_paid = select(func.sum(Payment.amount)).where(
            Payment.booking_id == booking_id,
            Payment.payment_status_id.in_([
                self._resolve_payment_status("RECEIVED").id,
                self._resolve_payment_status("VERIFIED").id
            ])
        )
        total_paid = db.session.scalar(stmt_paid) or Decimal("0.00")
        outstanding = booking.total_amount - total_paid
        if amount > outstanding:
            raise ValidationException("Payment amount exceeds outstanding balance.", code="PAYMENT_EXCEEDS_OUTSTANDING")

        # If payment schedule is provided
        schedule_id = data.get("payment_schedule_id")
        if schedule_id:
            sched = db.session.get(PaymentSchedule, schedule_id)
            if not sched or sched.booking_id != booking_id:
                raise ValidationException("Invalid payment schedule ID.", code="INVALID_SCHEDULE")

        status_received = self._resolve_payment_status("RECEIVED")

        payment = Payment(
            booking_id=booking_id,
            payment_schedule_id=schedule_id,
            payment_date=payment_date,
            amount=amount,
            payment_method_id=data["payment_method_id"],
            payment_type_id=data["payment_type_id"],
            payment_status_id=status_received.id, # Manual payment entry defaults to RECEIVED
            installment_no=data.get("installment_no"),
            transaction_reference=ref,
            remarks=data.get("remarks"),
            created_by_team_member_id=actor_id,
            updated_by_team_member_id=actor_id
        )

        db.session.add(payment)
        db.session.flush()

        # Update linked schedule
        if schedule_id:
            sched = db.session.get(PaymentSchedule, schedule_id)
            sched.payment_status_id = status_received.id
            db.session.add(sched)

        # Check for first payment (AdvanceReceived)
        if total_paid == 0:
            event_bus.publish(DomainEvent.ADVANCE_RECEIVED, {
                "booking_id": str(booking_id),
                "payment_id": str(payment.id),
                "amount": str(amount),
                "occurred_at": datetime.now(timezone.utc).isoformat()
            })

        event_bus.publish(DomainEvent.PAYMENT_RECEIVED, {
            "booking_id": str(booking_id),
            "payment_id": str(payment.id),
            "amount": str(amount),
            "occurred_at": datetime.now(timezone.utc).isoformat()
        })

        self.commit()
        return payment

    def verify_payment(self, payment_id: uuid.UUID | str, data: dict, actor_id: uuid.UUID | str) -> Payment:
        """Command: Verify customer payment transaction."""
        payment = db.session.get(Payment, payment_id)
        if not payment:
            raise NotFoundException("Payment not found.")

        # Idempotency check
        status_verified = self._resolve_payment_status("VERIFIED")
        if payment.payment_status_id == status_verified.id:
            return payment

        payment.payment_status_id = status_verified.id
        payment.verified_by_team_member_id = actor_id
        payment.remarks = (payment.remarks or "") + f" | Verified: {data.get('verification_notes', '')}"
        payment.updated_by_team_member_id = actor_id

        db.session.add(payment)
        db.session.flush()

        event_bus.publish(DomainEvent.PAYMENT_VERIFIED, {
            "booking_id": str(payment.booking_id),
            "payment_id": str(payment.id),
            "verified_by": str(actor_id),
            "occurred_at": datetime.now(timezone.utc).isoformat()
        })

        self.commit()
        return payment

    def upload_receipt(self, payment_id: uuid.UUID | str, data: dict, actor_id: uuid.UUID | str) -> Payment:
        """Command: Upload receipt URL for payment."""
        payment = db.session.get(Payment, payment_id)
        if not payment:
            raise NotFoundException("Payment not found.")

        payment.receipt_url = data["receipt_url"]
        payment.updated_by_team_member_id = actor_id

        db.session.add(payment)
        self.commit()
        return payment

    # --- Vendor Payments ---
    def record_vendor_payment(self, data: dict, actor_id: uuid.UUID | str) -> VendorPayment:
        """Command: Record vendor payment disbursement."""
        alloc_id = data["vendor_allocation_id"]
        alloc = db.session.get(VendorAllocation, alloc_id)
        if not alloc:
            raise NotFoundException("Vendor allocation not found.")

        # Finance Lock Check
        booking = db.session.get(Booking, alloc.trip_day.trip_plan.booking_id)
        if booking.status.code in ["COMPLETED", "CLOSED"]:
            raise BusinessException("Finance is locked. Operational costs cannot be modified.", code="FINANCE_LOCKED")

        # Payment date guard
        payment_date = data["payment_date"]
        if isinstance(payment_date, str):
            payment_date = datetime.strptime(payment_date, "%Y-%m-%d").date()
        if payment_date > date.today():
            raise ValidationException("Payment date cannot be in the future.", code="INVALID_DATE")

        amount = Decimal(str(data["amount"]))
        ref = data.get("transaction_reference")

        # Duplicate check
        if ref:
            stmt_dup = select(func.count(VendorPayment.id)).where(
                VendorPayment.vendor_allocation_id == alloc_id,
                VendorPayment.amount == amount,
                VendorPayment.transaction_reference == ref
            )
            if db.session.scalar(stmt_dup) > 0:
                raise BusinessException("Duplicate vendor payment reference.", code="DUPLICATE_VENDOR_PAYMENT")

        # Vendor balance check
        confirmed_cost = alloc.confirmed_price if alloc.confirmed_price is not None else alloc.quoted_amount
        stmt_paid = select(func.sum(VendorPayment.amount)).where(
            VendorPayment.vendor_allocation_id == alloc_id,
            VendorPayment.payment_status_id == self._resolve_payment_status("RECEIVED").id
        )
        total_paid = db.session.scalar(stmt_paid) or Decimal("0.00")
        vendor_balance = confirmed_cost - total_paid
        if amount > vendor_balance:
            raise ValidationException("Vendor payment amount exceeds remaining balance due.", code="VENDOR_PAYMENT_EXCEEDS_BALANCE")

        status_received = self._resolve_payment_status("RECEIVED")

        vp = VendorPayment(
            vendor_allocation_id=alloc_id,
            payment_date=payment_date,
            amount=amount,
            payment_method_id=data["payment_method_id"],
            payment_status_id=status_received.id,
            transaction_reference=ref,
            receipt_url=data.get("receipt_url"),
            internal_notes=data.get("internal_notes"),
            created_by_team_member_id=actor_id,
            updated_by_team_member_id=actor_id
        )

        db.session.add(vp)
        db.session.flush()

        # Re-fetch/re-calculate allocation settlement status
        # If fully paid, transition allocation status (handled in Operations or updated dynamically)
        
        event_bus.publish(DomainEvent.VENDOR_PAYMENT_RECORDED, {
            "vendor_allocation_id": str(alloc_id),
            "vendor_payment_id": str(vp.id),
            "amount": str(amount),
            "occurred_at": datetime.now(timezone.utc).isoformat()
        })

        self.commit()
        return vp

    # --- Expenses ---
    def create_expense(self, data: dict, actor_id: uuid.UUID | str) -> Expense:
        """Command: Log operational expense."""
        booking_id = data["booking_id"]
        booking = db.session.get(Booking, booking_id)
        if not booking or booking.is_deleted:
            raise NotFoundException("Booking not found.")

        # Finance Lock Check
        if booking.status.code in ["COMPLETED", "CLOSED"]:
            raise BusinessException("Finance is locked. Operational costs cannot be modified.", code="EXPENSE_LOCKED")

        # Date validation
        expense_date = data["expense_date"]
        if isinstance(expense_date, str):
            expense_date = datetime.strptime(expense_date, "%Y-%m-%d").date()
        if expense_date > date.today():
            raise ValidationException("Expense date cannot be in the future.", code="INVALID_EXPENSE_DATE")
        if expense_date < booking.trip_start_date:
            raise ValidationException("Expense date cannot be before trip start date.", code="EXPENSE_DATE_OUT_OF_RANGE")

        amount = Decimal(str(data["amount"]))

        expense = Expense(
            booking_id=booking_id,
            vendor_allocation_id=data.get("vendor_allocation_id"),
            expense_category_id=data["expense_category_id"],
            expense_type_id=data["expense_type_id"],
            amount=amount,
            expense_date=expense_date,
            expense_description=data.get("expense_description"),
            remarks=data.get("remarks"),
            created_by_team_member_id=actor_id,
            updated_by_team_member_id=actor_id
        )

        db.session.add(expense)
        db.session.flush()

        event_bus.publish(DomainEvent.EXPENSE_RECORDED, {
            "booking_id": str(booking_id),
            "expense_id": str(expense.id),
            "amount": str(amount),
            "occurred_at": datetime.now(timezone.utc).isoformat()
        })

        self.commit()
        return expense

    def delete_expense(self, expense_id: uuid.UUID | str, actor_id: uuid.UUID | str) -> None:
        """Command: Delete expense."""
        expense = db.session.get(Expense, expense_id)
        if not expense:
            raise NotFoundException("Expense not found.")

        # Finance Lock Check
        booking = db.session.get(Booking, expense.booking_id)
        if booking.status.code in ["COMPLETED", "CLOSED"]:
            raise BusinessException("Finance is locked. Operational costs cannot be modified.", code="EXPENSE_LOCKED")

        db.session.delete(expense)
        self.commit()

    # --- Refunds ---
    def create_refund(self, data: dict, actor_id: uuid.UUID | str) -> Refund:
        """Command: Create refund request."""
        booking_id = data["booking_id"]
        booking = db.session.get(Booking, booking_id)
        if not booking or booking.is_deleted:
            raise NotFoundException("Booking not found.")

        amount = Decimal(str(data["amount"]))

        # Refund limit guard
        # Total Collected
        stmt_paid = select(func.sum(Payment.amount)).where(
            Payment.booking_id == booking_id,
            Payment.payment_status_id.in_([
                self._resolve_payment_status("RECEIVED").id,
                self._resolve_payment_status("VERIFIED").id
            ])
        )
        total_paid = db.session.scalar(stmt_paid) or Decimal("0.00")

        # Cumulative refunds (REQUESTED, APPROVED, PROCESSED, COMPLETED)
        stmt_ref = select(func.sum(Refund.amount)).where(
            Refund.booking_id == booking_id,
            Refund.refund_status_id.in_([
                self._resolve_refund_status("REQUESTED").id,
                self._resolve_refund_status("APPROVED").id,
                self._resolve_refund_status("PROCESSED").id,
                self._resolve_refund_status("COMPLETED").id
            ])
        )
        total_refunded = db.session.scalar(stmt_ref) or Decimal("0.00")

        if amount + total_refunded > total_paid:
            raise ValidationException("Cumulative refunds exceed total collected amount.", code="REFUND_EXCEEDS_PAID")

        status_requested = self._resolve_refund_status("REQUESTED")
        refund_date = data.get("refund_date") or date.today()
        if isinstance(refund_date, str):
            refund_date = datetime.strptime(refund_date, "%Y-%m-%d").date()

        refund = Refund(
            booking_id=booking_id,
            refund_status_id=status_requested.id,
            amount=amount,
            refund_date=refund_date,
            payment_method_id=data["payment_method_id"],
            transaction_reference=data.get("transaction_reference"),
            remarks=data.get("remarks"),
            created_by_team_member_id=actor_id,
            updated_by_team_member_id=actor_id
        )

        db.session.add(refund)
        self.commit()
        return refund

    def transition_refund_status(self, refund_id: uuid.UUID | str, target_status: str, actor_id: uuid.UUID | str) -> Refund:
        """Command: Transition refund status."""
        refund = db.session.get(Refund, refund_id)
        if not refund:
            raise NotFoundException("Refund not found.")

        # Idempotency check
        status_target = self._resolve_refund_status(target_status)
        if refund.refund_status_id == status_target.id:
            return refund

        # Update
        refund.refund_status_id = status_target.id
        refund.updated_by_team_member_id = actor_id

        db.session.add(refund)
        db.session.flush()

        if target_status == "COMPLETED":
            event_bus.publish(DomainEvent.REFUND_COMPLETED, {
                "booking_id": str(refund.booking_id),
                "refund_id": str(refund.id),
                "amount": str(refund.amount),
                "occurred_at": datetime.now(timezone.utc).isoformat()
            })

        self.commit()
        return refund

    # --- P&L and Reporting Queries ---
    def get_profit_summary(self, booking_id: uuid.UUID | str) -> dict:
        """Query: Get derived P&L summary dynamically."""
        booking = db.session.get(Booking, booking_id)
        if not booking or booking.is_deleted:
            raise NotFoundException("Booking not found.")

        # 1. Total Paid
        stmt_paid = select(func.sum(Payment.amount)).where(
            Payment.booking_id == booking_id,
            Payment.payment_status_id.in_([
                self._resolve_payment_status("RECEIVED").id,
                self._resolve_payment_status("VERIFIED").id
            ])
        )
        total_paid = db.session.scalar(stmt_paid) or Decimal("0.00")

        # 2. Refunds Issued
        stmt_ref = select(func.sum(Refund.amount)).where(
            Refund.booking_id == booking_id,
            Refund.refund_status_id == self._resolve_refund_status("COMPLETED").id
        )
        refunds_issued = db.session.scalar(stmt_ref) or Decimal("0.00")

        # 3. Net Revenue
        net_revenue = total_paid - refunds_issued

        # 4. Vendor cost (Confirmed vendor allocations)
        # Query vendor allocations linked to booking
        stmt_alloc = select(VendorAllocation).join(
            TripDay, VendorAllocation.trip_day_id == TripDay.id
        ).join(
            TripPlan, TripDay.trip_plan_id == TripPlan.id
        ).where(
            TripPlan.booking_id == booking_id
        )
        allocations = db.session.scalars(stmt_alloc).all()
        vendor_cost = sum((a.confirmed_price if a.confirmed_price is not None else a.quoted_amount) for a in allocations)
        vendor_cost = Decimal(str(vendor_cost))

        # 5. Vendor amount paid
        stmt_vp = select(func.sum(VendorPayment.amount)).join(
            VendorAllocation, VendorPayment.vendor_allocation_id == VendorAllocation.id
        ).join(
            TripDay, VendorAllocation.trip_day_id == TripDay.id
        ).join(
            TripPlan, TripDay.trip_plan_id == TripPlan.id
        ).where(
            TripPlan.booking_id == booking_id,
            VendorPayment.payment_status_id == self._resolve_payment_status("RECEIVED").id
        )
        vendor_amount_paid = db.session.scalar(stmt_vp) or Decimal("0.00")

        # 6. Operational expenses
        stmt_exp = select(func.sum(Expense.amount)).where(
            Expense.booking_id == booking_id
        )
        operational_expenses = db.session.scalar(stmt_exp) or Decimal("0.00")

        # Derived profit fields
        outstanding_balance = booking.total_amount - total_paid
        vendor_balance_due = vendor_cost - vendor_amount_paid
        total_cost = vendor_cost + operational_expenses
        gross_profit = net_revenue - total_cost

        if net_revenue > 0:
            profit_margin = (gross_profit / net_revenue) * 100
        else:
            profit_margin = Decimal("0.00")

        return {
            "booking_id": booking.id,
            "booking_number": booking.booking_number,
            "total_amount": booking.total_amount,
            "total_paid": total_paid,
            "outstanding_balance": outstanding_balance,
            "vendor_cost": vendor_cost,
            "vendor_amount_paid": vendor_amount_paid,
            "vendor_balance_due": vendor_balance_due,
            "operational_expenses": operational_expenses,
            "refunds_issued": refunds_issued,
            "net_revenue": net_revenue,
            "total_cost": total_cost,
            "gross_profit": gross_profit,
            "profit_margin_percentage": round(profit_margin, 2),
            "finance_status": booking.status.code
        }

    def get_installment_schedule(self, booking_id: uuid.UUID | str) -> dict:
        """Query: Get installment schedule for a booking."""
        booking = db.session.get(Booking, booking_id)
        if not booking or booking.is_deleted:
            raise NotFoundException("Booking not found.")

        # Schedules
        stmt_sched = select(PaymentSchedule).options(
            joinedload(PaymentSchedule.payment_status)
        ).where(
            PaymentSchedule.booking_id == booking_id
        ).order_by(PaymentSchedule.installment_no)
        schedules = db.session.scalars(stmt_sched).all()

        # Sum total paid
        stmt_paid = select(func.sum(Payment.amount)).where(
            Payment.booking_id == booking_id,
            Payment.payment_status_id.in_([
                self._resolve_payment_status("RECEIVED").id,
                self._resolve_payment_status("VERIFIED").id
            ])
        )
        total_paid = db.session.scalar(stmt_paid) or Decimal("0.00")
        outstanding = booking.total_amount - total_paid

        return {
            "booking_id": booking.id,
            "booking_number": booking.booking_number,
            "total_amount": booking.total_amount,
            "total_paid": total_paid,
            "outstanding_balance": outstanding,
            "schedules": [
                {
                    "id": s.id,
                    "installment_no": s.installment_no,
                    "due_date": s.due_date,
                    "amount": s.amount,
                    "percentage": s.percentage,
                    "payment_status": {
                        "id": s.payment_status.id if s.payment_status else None,
                        "code": s.payment_status.code if s.payment_status else "PENDING",
                        "name": s.payment_status.name if s.payment_status else "Pending"
                    },
                    "remarks": s.remarks
                } for s in schedules
            ]
        }

    def list_outstanding_payments(self, page: int = 1, per_page: int = 20) -> Tuple[List[dict], int]:
        """Query: List bookings with outstanding customer balances."""
        # Find bookings where total paid (RECEIVED/VERIFIED payments) < total_amount
        stmt_bookings = select(Booking).where(Booking.is_deleted == False)
        bookings = db.session.scalars(stmt_bookings).all()

        outstanding_list = []
        for b in bookings:
            stmt_paid = select(func.sum(Payment.amount)).where(
                Payment.booking_id == b.id,
                Payment.payment_status_id.in_([
                    self._resolve_payment_status("RECEIVED").id,
                    self._resolve_payment_status("VERIFIED").id
                ])
            )
            paid = db.session.scalar(stmt_paid) or Decimal("0.00")
            bal = b.total_amount - paid
            if bal > 0:
                # Find next due date from pending schedules
                stmt_next_sched = select(PaymentSchedule.due_date).where(
                    PaymentSchedule.booking_id == b.id,
                    PaymentSchedule.payment_status.has(PaymentStatus.code == "PENDING")
                ).order_by(PaymentSchedule.due_date).limit(1)
                next_due = db.session.scalar(stmt_next_sched)

                outstanding_list.append({
                    "booking_id": b.id,
                    "booking_number": b.booking_number,
                    "customer_name": b.customer.customer_name if b.customer else "Unknown",
                    "total_amount": b.total_amount,
                    "total_paid": paid,
                    "outstanding_balance": bal,
                    "next_due_date": next_due,
                    "booking_status": b.status.code if b.status else "Unknown"
                })

        # Apply simple manual pagination
        total = len(outstanding_list)
        start = (page - 1) * per_page
        end = start + per_page
        return outstanding_list[start:end], total

    def list_upcoming_installments(self) -> List[dict]:
        """Query: List upcoming payment due dates."""
        stmt = select(PaymentSchedule).join(
            Booking, PaymentSchedule.booking_id == Booking.id
        ).where(
            PaymentSchedule.due_date >= date.today(),
            PaymentSchedule.payment_status.has(PaymentStatus.code == "PENDING")
        ).order_by(PaymentSchedule.due_date)
        schedules = db.session.scalars(stmt).all()

        return [
            {
                "schedule_id": s.id,
                "booking_id": s.booking_id,
                "booking_number": s.booking.booking_number,
                "customer_name": s.booking.customer.customer_name if s.booking.customer else "Unknown",
                "installment_no": s.installment_no,
                "due_date": s.due_date,
                "amount": s.amount,
                "payment_status": "PENDING"
            } for s in schedules
        ]

    def list_pending_vendor_payments(self) -> List[dict]:
        """Query: List pending vendor disbursements."""
        stmt = select(VendorAllocation).join(
            TripDay, VendorAllocation.trip_day_id == TripDay.id
        ).join(
            TripPlan, TripDay.trip_plan_id == TripPlan.id
        ).where(
            TripPlan.booking.has(Booking.is_deleted == False)
        )
        allocations = db.session.scalars(stmt).all()

        pending = []
        for a in allocations:
            if a.settlement_status != "SETTLED":
                confirmed_cost = a.confirmed_price if a.confirmed_price is not None else a.quoted_amount
                pending.append({
                    "vendor_allocation_id": a.id,
                    "booking_id": a.trip_day.trip_plan.booking_id,
                    "booking_number": a.trip_day.trip_plan.booking.booking_number,
                    "vendor_name": a.vendor.vendor_name if a.vendor else "Unknown",
                    "service_name": a.service_name,
                    "service_date": a.service_date,
                    "quoted_amount": a.quoted_amount,
                    "confirmed_price": confirmed_cost,
                    "amount_paid": a.total_paid,
                    "balance_due": confirmed_cost - a.total_paid,
                    "allocation_status": a.allocation_status.code if a.allocation_status else "PENDING"
                })
        return pending

    # --- Close Finance ---
    def close_finance(self, booking_id: uuid.UUID | str, data: dict, actor_id: uuid.UUID | str) -> Booking:
        """Command: Close booking finance ledger (admin only)."""
        booking = db.session.get(Booking, booking_id)
        if not booking or booking.is_deleted:
            raise NotFoundException("Booking not found.")

        # Idempotency check
        if booking.status.code == "CLOSED":
            return booking

        # Outstanding check
        stmt_paid = select(func.sum(Payment.amount)).where(
            Payment.booking_id == booking_id,
            Payment.payment_status_id.in_([
                self._resolve_payment_status("RECEIVED").id,
                self._resolve_payment_status("VERIFIED").id
            ])
        )
        total_paid = db.session.scalar(stmt_paid) or Decimal("0.00")
        outstanding = booking.total_amount - total_paid
        if outstanding > 0:
            raise BusinessException("Cannot close finance: outstanding balance exists.", code="PENDING_INSTALLMENTS_EXIST")

        # Unsettled vendor allocations check
        trip_plan = db.session.scalar(select(TripPlan).where(TripPlan.booking_id == booking_id, TripPlan.is_final == True))
        if trip_plan:
            for day in trip_plan.trip_days:
                for alloc in day.vendor_allocations:
                    if alloc.settlement_status != "SETTLED":
                        raise BusinessException(
                            f"Cannot close finance: Vendor allocation {alloc.id} is not settled.",
                            code="VENDOR_PENDING_SETTLEMENTS"
                        )

        # Transition status
        stmt_closed = select(BookingStatus).where(BookingStatus.code == "CLOSED")
        closed_status = db.session.scalar(stmt_closed) or BookingStatus(code="CLOSED", name="Closed", is_active=True)
        db.session.add(closed_status)
        db.session.flush()

        booking.booking_status_id = closed_status.id
        booking.row_version += 1

        db.session.add(booking)
        db.session.flush()

        event_bus.publish(DomainEvent.FINANCE_CLOSED, {
            "booking_id": str(booking_id),
            "closed_by": str(actor_id),
            "occurred_at": datetime.now(timezone.utc).isoformat()
        })

        self.commit()
        return booking
