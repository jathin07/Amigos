import uuid
from typing import List
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload

from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from app.models import Payment, VendorPayment, Expense, Refund, VendorAllocation, TripDay, TripPlan
from app.core.extensions import db

class PaymentRepository(SQLAlchemyBaseRepository[Payment]):
    """Repository for customer Payment aggregate."""
    
    searchable_fields = ["transaction_reference", "remarks"]
    sortable_fields = ["payment_date", "amount", "created_at"]
    filterable_fields = ["booking_id", "payment_status_id", "payment_method_id"]
    default_sort = [("created_at", "desc")]

    def __init__(self):
        super().__init__(Payment)

    def get_by_booking_id(self, booking_id: uuid.UUID | str) -> List[Payment]:
        stmt = select(Payment).options(
            joinedload(Payment.status),
            joinedload(Payment.payment_method),
            joinedload(Payment.payment_type),
            joinedload(Payment.verified_by)
        ).where(Payment.booking_id == booking_id)
        return list(db.session.scalars(stmt).all())

    def check_duplicate_reference(self, booking_id: uuid.UUID | str, amount: float, reference: str) -> bool:
        if not reference:
            return False
        stmt = select(func.count(Payment.id)).where(
            Payment.booking_id == booking_id,
            Payment.amount == amount,
            Payment.transaction_reference == reference
        )
        return db.session.scalar(stmt) > 0


class VendorPaymentRepository(SQLAlchemyBaseRepository[VendorPayment]):
    """Repository for VendorPayment aggregate."""

    searchable_fields = ["transaction_reference", "internal_notes"]
    sortable_fields = ["payment_date", "amount", "created_at"]
    filterable_fields = ["vendor_allocation_id", "payment_status_id"]
    default_sort = [("created_at", "desc")]

    def __init__(self):
        super().__init__(VendorPayment)

    def get_by_booking_id(self, booking_id: uuid.UUID | str) -> List[VendorPayment]:
        stmt = select(VendorPayment).options(
            joinedload(VendorPayment.payment_status),
            joinedload(VendorPayment.payment_method),
            joinedload(VendorPayment.vendor_allocation)
        ).join(
            VendorAllocation, VendorPayment.vendor_allocation_id == VendorAllocation.id
        ).join(
            TripDay, VendorAllocation.trip_day_id == TripDay.id
        ).join(
            TripPlan, TripDay.trip_plan_id == TripPlan.id
        ).where(
            TripPlan.booking_id == booking_id
        )
        return list(db.session.scalars(stmt).all())

    def check_duplicate_reference(self, vendor_allocation_id: uuid.UUID | str, amount: float, reference: str) -> bool:
        if not reference:
            return False
        stmt = select(func.count(VendorPayment.id)).where(
            VendorPayment.vendor_allocation_id == vendor_allocation_id,
            VendorPayment.amount == amount,
            VendorPayment.transaction_reference == reference
        )
        return db.session.scalar(stmt) > 0


class ExpenseRepository(SQLAlchemyBaseRepository[Expense]):
    """Repository for Expense aggregate."""

    searchable_fields = ["expense_description", "remarks"]
    sortable_fields = ["expense_date", "amount", "created_at"]
    filterable_fields = ["booking_id", "expense_category_id", "expense_type_id", "vendor_allocation_id"]
    default_sort = [("created_at", "desc")]

    def __init__(self):
        super().__init__(Expense)

    def get_by_booking_id(self, booking_id: uuid.UUID | str) -> List[Expense]:
        stmt = select(Expense).options(
            joinedload(Expense.expense_type),
            joinedload(Expense.expense_category),
            joinedload(Expense.vendor_allocation)
        ).where(Expense.booking_id == booking_id)
        return list(db.session.scalars(stmt).all())


class RefundRepository(SQLAlchemyBaseRepository[Refund]):
    """Repository for Refund aggregate."""

    searchable_fields = ["transaction_reference", "remarks"]
    sortable_fields = ["refund_date", "amount", "created_at"]
    filterable_fields = ["booking_id", "refund_status_id", "payment_method_id"]
    default_sort = [("created_at", "desc")]

    def __init__(self):
        super().__init__(Refund)

    def get_by_booking_id(self, booking_id: uuid.UUID | str) -> List[Refund]:
        stmt = select(Refund).options(
            joinedload(Refund.refund_status),
            joinedload(Refund.payment_method)
        ).where(Refund.booking_id == booking_id)
        return list(db.session.scalars(stmt).all())
