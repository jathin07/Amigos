import uuid
from datetime import date, datetime, timedelta
from sqlalchemy import select, func, and_, or_

from app.core.extensions import db
from app.models import (
    Lead, LeadStatus, Proposal, ProposalStatus, Booking, BookingStatus,
    PaymentSchedule, PaymentStatus, VendorAllocation, VendorAllocationStatus,
    Payment, Expense, Refund, RefundStatus, TeamMember, Task, TaskStatus,
    Destination, TripPlan, TripPlanStatus, ContactPerson, ProposalDestination,
    Checklist, TripDay
)

class SummaryQueryRepository:
    def get_active_leads_count(self) -> int:
        stmt = (
            select(func.count(Lead.id))
            .join(LeadStatus, Lead.current_status_id == LeadStatus.id)
            .where(and_(LeadStatus.code.notin_(["WON", "LOST"]), Lead.is_deleted == False))
        )
        return db.session.scalar(stmt) or 0

    def get_open_proposals_count(self) -> int:
        stmt = (
            select(func.count(Proposal.id))
            .join(ProposalStatus, Proposal.status_id == ProposalStatus.id)
            .where(and_(ProposalStatus.code.in_(["DRAFT", "UNDER_DISCUSSION"]), Proposal.is_deleted == False))
        )
        return db.session.scalar(stmt) or 0

    def get_confirmed_bookings_count(self) -> int:
        stmt = (
            select(func.count(Booking.id))
            .join(BookingStatus, Booking.booking_status_id == BookingStatus.id)
            .where(and_(BookingStatus.code.in_(["CONFIRMED", "PLANNING", "READY", "ONGOING"]), Booking.is_deleted == False))
        )
        return db.session.scalar(stmt) or 0

    def get_trips_today_count(self, today: date) -> int:
        stmt = (
            select(func.count(Booking.id))
            .join(BookingStatus, Booking.booking_status_id == BookingStatus.id)
            .where(and_(
                Booking.trip_start_date <= today,
                Booking.trip_end_date >= today,
                BookingStatus.code.notin_(["CANCELLED", "CLOSED"]),
                Booking.is_deleted == False
            ))
        )
        return db.session.scalar(stmt) or 0

    def get_outstanding_payments_count(self, today: date) -> int:
        stmt = (
            select(func.count(PaymentSchedule.id))
            .join(PaymentStatus, PaymentSchedule.payment_status_id == PaymentStatus.id)
            .where(and_(
                PaymentSchedule.due_date < today,
                PaymentStatus.code == "PENDING"
            ))
        )
        return db.session.scalar(stmt) or 0

    def get_pending_vendor_payments_count(self) -> int:
        stmt = (
            select(func.count(VendorAllocation.id))
            .join(VendorAllocationStatus, VendorAllocation.allocation_status_id == VendorAllocationStatus.id)
            .where(VendorAllocationStatus.code.in_(["CONFIRMED", "LOCKED"]))
        )
        return db.session.scalar(stmt) or 0

    def get_revenue_this_month(self, start_date: date, end_date: date) -> float:
        stmt = (
            select(func.coalesce(func.sum(Payment.amount), 0))
            .join(PaymentStatus, Payment.payment_status_id == PaymentStatus.id)
            .where(and_(
                PaymentStatus.code == "VERIFIED",
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date
            ))
        )
        return float(db.session.scalar(stmt) or 0.0)

    def get_expenses_this_month(self, start_date: date, end_date: date) -> float:
        stmt = (
            select(func.coalesce(func.sum(Expense.amount), 0))
            .where(and_(
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date
            ))
        )
        return float(db.session.scalar(stmt) or 0.0)


class CRMQueryRepository:
    def get_lead_funnel(self) -> list[dict]:
        # Query total active leads count for percentage
        total_stmt = select(func.count(Lead.id)).where(Lead.is_deleted == False)
        total_count = db.session.scalar(total_stmt) or 0

        # Query counts grouped by status code
        stmt = (
            select(LeadStatus.code, func.count(Lead.id))
            .join(LeadStatus, Lead.current_status_id == LeadStatus.id)
            .where(Lead.is_deleted == False)
            .group_by(LeadStatus.code)
        )
        raw_results = db.session.execute(stmt).all()
        counts_dict = {row[0]: row[1] for row in raw_results}

        stages = [
            {"status": "NEW", "color": "#2196F3"},
            {"status": "ASSIGNED", "color": "#00BCD4"},
            {"status": "CONTACTED", "color": "#9C27B0"},
            {"status": "PROPOSAL", "color": "#FF9800"},
            {"status": "NEGOTIATION", "color": "#FFC107"},
            {"status": "WON", "color": "#4CAF50"},
            {"status": "LOST", "color": "#F44336"}
        ]

        funnel = []
        for stage in stages:
            code = stage["status"]
            count = counts_dict.get(code, 0)
            percentage = round((count / total_count * 100), 2) if total_count > 0 else 0.0
            funnel.append({
                "status": code,
                "count": count,
                "percentage": percentage,
                "color": stage["color"]
            })
        return funnel


class BookingQueryRepository:
    def get_booking_funnel(self) -> list[dict]:
        total_stmt = select(func.count(Booking.id)).where(Booking.is_deleted == False)
        total_count = db.session.scalar(total_stmt) or 0

        stmt = (
            select(BookingStatus.code, func.count(Booking.id))
            .join(BookingStatus, Booking.booking_status_id == BookingStatus.id)
            .where(Booking.is_deleted == False)
            .group_by(BookingStatus.code)
        )
        raw_results = db.session.execute(stmt).all()
        counts_dict = {row[0]: row[1] for row in raw_results}

        stages = [
            {"status": "WAITING_FOR_ADVANCE"},
            {"status": "CONFIRMED"},
            {"status": "PLANNING"},
            {"status": "READY"},
            {"status": "ONGOING"},
            {"status": "COMPLETED"},
            {"status": "CLOSED"},
            {"status": "CANCELLED"}
        ]

        funnel = []
        for stage in stages:
            code = stage["status"]
            count = counts_dict.get(code, 0)
            percentage = round((count / total_count * 100), 2) if total_count > 0 else 0.0
            # Wait, WAITING_ADVANCE vs WAITING_FOR_ADVANCE: Standardize mapping to WAITING_ADVANCE in DTO
            dto_status = "WAITING_ADVANCE" if code == "WAITING_FOR_ADVANCE" else code
            funnel.append({
                "status": dto_status,
                "count": count,
                "percentage": percentage
            })
        return funnel

    def get_upcoming_trips(self, today: date, limit_date: date, page: int = 1, page_size: int = 10) -> dict:
        # We join Booking -> Customer -> ContactPerson, Proposal -> ProposalDestination -> Destination
        # Using outer joins to avoid exclusion if fields are missing
        stmt_count = (
            select(func.count(Booking.id))
            .where(and_(
                Booking.trip_start_date >= today,
                Booking.trip_start_date <= limit_date,
                Booking.is_deleted == False
            ))
        )
        total_items = db.session.scalar(stmt_count) or 0

        # Build paginated query
        offset = (page - 1) * page_size
        stmt_data = (
            select(
                Booking.booking_number,
                func.coalesce(Booking.contact_person_snapshot, ContactPerson.name).label("customer"),
                func.coalesce(Destination.name, Booking.package_name_snapshot).label("destination"),
                func.coalesce(TeamMember.display_name, "Unassigned").label("coordinator"),
                Booking.trip_start_date
            )
            .select_from(Booking)
            .join(BookingStatus, Booking.booking_status_id == BookingStatus.id)
            .outerjoin(ContactPerson, Booking.contact_person_id == ContactPerson.id)
            .outerjoin(TeamMember, Booking.trip_coordinator_team_member_id == TeamMember.id)
            .outerjoin(ProposalDestination, Booking.proposal_version_id == ProposalDestination.proposal_id)
            .outerjoin(Destination, ProposalDestination.destination_id == Destination.id)
            .where(and_(
                Booking.trip_start_date >= today,
                Booking.trip_start_date <= limit_date,
                BookingStatus.code.notin_(["CANCELLED", "CLOSED"]),
                Booking.is_deleted == False
            ))
            .order_by(Booking.trip_start_date.asc())
            .offset(offset)
            .limit(page_size)
        )

        raw_rows = db.session.execute(stmt_data).all()
        trips = []
        for row in raw_rows:
            remaining = (row[4] - today).days
            trips.append({
                "booking_number": row[0],
                "customer": row[1] or "Customer",
                "destination": row[2] or "N/A",
                "coordinator": row[3],
                "departure": row[4].isoformat(),
                "remaining_days": remaining if remaining >= 0 else 0
            })

        total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1
        return {
            "upcoming_trips": trips,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": total_pages
            }
        }


class FinanceQueryRepository:
    def get_finance_summary(self, today: date, start_date: date, end_date: date) -> dict:
        # 1. Collected Revenue this month
        revenue_stmt = (
            select(func.coalesce(func.sum(Payment.amount), 0))
            .join(PaymentStatus, Payment.payment_status_id == PaymentStatus.id)
            .where(and_(
                PaymentStatus.code == "VERIFIED",
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date
            ))
        )
        collected = db.session.scalar(revenue_stmt) or 0.0

        # 2. Outstanding Balance
        balance_stmt = (
            select(func.coalesce(func.sum(PaymentSchedule.amount), 0))
            .join(PaymentStatus, PaymentSchedule.payment_status_id == PaymentStatus.id)
            .where(PaymentStatus.code == "PENDING")
        )
        outstanding = db.session.scalar(balance_stmt) or 0.0

        # 3. Vendor due
        vendor_stmt = (
            select(func.coalesce(func.sum(VendorAllocation.confirmed_price), 0))
            .join(VendorAllocationStatus, VendorAllocation.allocation_status_id == VendorAllocationStatus.id)
            .where(VendorAllocationStatus.code.in_(["CONFIRMED", "LOCKED"]))
        )
        vendor_due = db.session.scalar(vendor_stmt) or 0.0

        # 4. Expenses this month
        expense_stmt = (
            select(func.coalesce(func.sum(Expense.amount), 0))
            .where(and_(
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date
            ))
        )
        expenses = db.session.scalar(expense_stmt) or 0.0

        # 5. Refunds completed this month
        refund_stmt = (
            select(func.coalesce(func.sum(Refund.amount), 0))
            .join(RefundStatus, Refund.refund_status_id == RefundStatus.id)
            .where(and_(
                RefundStatus.code == "COMPLETED",
                Refund.refund_date >= start_date,
                Refund.refund_date <= end_date
            ))
        )
        refunds = db.session.scalar(refund_stmt) or 0.0

        net_profit = collected - expenses - refunds
        margin = round((net_profit / collected * 100), 2) if collected > 0 else 0.0

        return {
            "collected": float(collected),
            "outstanding": float(outstanding),
            "vendor_due": float(vendor_due),
            "expenses": float(expenses),
            "refunds": float(refunds),
            "net_profit": float(net_profit),
            "gross_margin_percentage": float(margin)
        }

    def get_monthly_metrics(self, year: int, month: int) -> dict:
        """Helper to get verified revenue, completed refunds, and logged expenses for a specific calendar month."""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        rev_stmt = (
            select(func.coalesce(func.sum(Payment.amount), 0))
            .join(PaymentStatus, Payment.payment_status_id == PaymentStatus.id)
            .where(and_(
                PaymentStatus.code == "VERIFIED",
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date
            ))
        )
        collected = db.session.scalar(rev_stmt) or 0.0

        exp_stmt = (
            select(func.coalesce(func.sum(Expense.amount), 0))
            .where(and_(
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date
            ))
        )
        expenses = db.session.scalar(exp_stmt) or 0.0

        ref_stmt = (
            select(func.coalesce(func.sum(Refund.amount), 0))
            .join(RefundStatus, Refund.refund_status_id == RefundStatus.id)
            .where(and_(
                RefundStatus.code == "COMPLETED",
                Refund.refund_date >= start_date,
                Refund.refund_date <= end_date
            ))
        )
        refunds = db.session.scalar(ref_stmt) or 0.0

        # Booking Count
        booking_stmt = (
            select(func.count(Booking.id))
            .where(and_(
                Booking.booking_date >= start_date,
                Booking.booking_date <= end_date,
                Booking.is_deleted == False
            ))
        )
        bookings_count = db.session.scalar(booking_stmt) or 0

        profit = collected - expenses - refunds

        return {
            "month": f"{year}-{month:02d}",
            "collected": float(collected),
            "refund": float(refunds),
            "expenses": float(expenses),
            "profit": float(profit),
            "bookings_count": bookings_count
        }


class OperationsQueryRepository:
    def get_operations_overview(self) -> list[dict]:
        # Coordinator workload query: trips assigned, open tasks, uncompleted checklist items, pending vendor allocations
        # Query active TripPlans
        stmt_trips = (
            select(Booking.trip_coordinator_team_member_id, func.count(TripPlan.id))
            .select_from(TripPlan)
            .join(Booking, TripPlan.booking_id == Booking.id)
            .join(TripPlanStatus, TripPlan.status_id == TripPlanStatus.id)
            .where(TripPlanStatus.code.in_(["PLANNING", "READY", "ONGOING"]))
            .group_by(Booking.trip_coordinator_team_member_id)
        )
        raw_trips = db.session.execute(stmt_trips).all()
        trips_map = {row[0]: row[1] for row in raw_trips if row[0]}

        # Query open Tasks
        stmt_tasks = (
            select(Task.assigned_to_team_member_id, func.count(Task.id))
            .join(TaskStatus, Task.task_status_id == TaskStatus.id)
            .where(and_(TaskStatus.code.notin_(["COMPLETED", "CANCELLED"]), Task.is_deleted == False))
            .group_by(Task.assigned_to_team_member_id)
        )
        raw_tasks = db.session.execute(stmt_tasks).all()
        tasks_map = {row[0]: row[1] for row in raw_tasks if row[0]}

        # Query pending Checklists (Checklist items that are uncompleted)
        stmt_checklist = (
            select(Booking.trip_coordinator_team_member_id, func.count(Checklist.id))
            .select_from(Checklist)
            .join(Booking, Checklist.booking_id == Booking.id)
            .where(Checklist.is_completed == False)
            .group_by(Booking.trip_coordinator_team_member_id)
        )
        raw_checklist = db.session.execute(stmt_checklist).all()
        checklist_map = {row[0]: row[1] for row in raw_checklist if row[0]}

        # Query pending vendor allocations (allocations in waiting/pending/negotiating/confirmed/locked, not settled/failed)
        stmt_vendors = (
            select(Booking.trip_coordinator_team_member_id, func.count(VendorAllocation.id))
            .select_from(VendorAllocation)
            .join(TripDay, VendorAllocation.trip_day_id == TripDay.id)
            .join(TripPlan, TripDay.trip_plan_id == TripPlan.id)
            .join(Booking, TripPlan.booking_id == Booking.id)
            .join(VendorAllocationStatus, VendorAllocation.allocation_status_id == VendorAllocationStatus.id)
            .where(VendorAllocationStatus.code.in_(["PENDING", "NEGOTIATING", "CONFIRMED", "LOCKED"]))
            .group_by(Booking.trip_coordinator_team_member_id)
        )
        raw_vendors = db.session.execute(stmt_vendors).all()
        vendors_map = {row[0]: row[1] for row in raw_vendors if row[0]}

        # Query all coordinators
        coordinators = db.session.scalars(select(TeamMember).where(TeamMember.is_active == True)).all()
        
        results = []
        for tm in coordinators:
            # We only show coordinators who have active assignments to keep UI clean,
            # or show all active team members if they have coordinator designating properties.
            # To be safe, we list any coordinator with at least one metric > 0
            trips_count = trips_map.get(tm.id, 0)
            tasks_count = tasks_map.get(tm.id, 0)
            checklist_count = checklist_map.get(tm.id, 0)
            vendors_count = vendors_map.get(tm.id, 0)

            if trips_count > 0 or tasks_count > 0 or checklist_count > 0 or vendors_count > 0:
                results.append({
                    "coordinator_id": str(tm.id),
                    "coordinator": tm.display_name,
                    "trips_assigned": trips_count,
                    "open_tasks": tasks_count,
                    "pending_checklist": checklist_count,
                    "pending_vendors": vendors_count
                })
        return results
