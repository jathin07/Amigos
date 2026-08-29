import uuid
from typing import List, Tuple
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload, selectinload

from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from app.models import TripPlan, TripDay, VendorAllocation, Task, Checklist
from app.core.extensions import db
from app.common.pagination import PaginationResult
from app.common.filters import apply_filters
from app.common.search import apply_search
from app.common.sorting import apply_sort
from app.common.pagination import apply_pagination


class TripPlanRepository(SQLAlchemyBaseRepository[TripPlan]):
    """
    Repository for TripPlan command and query operations.
    """
    sortable_fields = [
        "prepared_date",
        "approved_at",
        "created_at",
        "updated_at"
    ]

    filterable_fields = [
        "booking_id",
        "status_id",
        "prepared_by_team_member_id",
        "approved_by_team_member_id",
        "is_final"
    ]

    default_sort = [
        ("created_at", "desc")
    ]

    def __init__(self):
        super().__init__(TripPlan)

    def get_by_booking_id(self, booking_id: uuid.UUID | str) -> TripPlan | None:
        """Query: Get active final trip plan for a booking with eager loading."""
        stmt = select(TripPlan).options(
            joinedload(TripPlan.trip_days).selectinload(TripDay.vendor_allocations),
            joinedload(TripPlan.prepared_by)
        ).where(
            TripPlan.booking_id == booking_id,
            TripPlan.is_final == True
        )
        return db.session.scalar(stmt)

    def get_with_lock(self, trip_plan_id: uuid.UUID | str, expected_version: int) -> TripPlan:
        """Query + Lock check: SELECT FOR UPDATE lock retrieval."""
        stmt = select(TripPlan).where(TripPlan.id == trip_plan_id).with_for_update()
        trip_plan = db.session.scalar(stmt)
        if not trip_plan:
            from app.domain.exceptions import NotFoundException
            raise NotFoundException("Trip plan not found.")
        
        if expected_version is not None and trip_plan.row_version != expected_version:
            from app.domain.exceptions import BusinessException
            raise BusinessException(
                "Concurrent modification detected. Please refresh and try again.",
                code="ERR_CONCURRENT_MODIFICATION"
            )
        return trip_plan

    def get_by_id(self, trip_plan_id: uuid.UUID | str) -> TripPlan | None:
        """Query: Get trip plan by ID with eager loading."""
        stmt = select(TripPlan).options(
            selectinload(TripPlan.trip_days).selectinload(TripDay.vendor_allocations)
        ).where(TripPlan.id == trip_plan_id)
        return db.session.scalar(stmt)


class TripDayRepository(SQLAlchemyBaseRepository[TripDay]):
    """
    Repository for TripDay entities.
    """
    def __init__(self):
        super().__init__(TripDay)

    def get_day(self, trip_plan_id: uuid.UUID | str, day_id: uuid.UUID | str) -> TripDay | None:
        stmt = select(TripDay).where(
            TripDay.trip_plan_id == trip_plan_id,
            TripDay.id == day_id
        )
        return db.session.scalar(stmt)

    def get_days_for_plan(self, trip_plan_id: uuid.UUID | str) -> List[TripDay]:
        stmt = select(TripDay).where(TripDay.trip_plan_id == trip_plan_id).order_by(TripDay.day_number.asc())
        return list(db.session.scalars(stmt))


class VendorAllocationRepository(SQLAlchemyBaseRepository[VendorAllocation]):
    """
    Repository for VendorAllocation operations.
    """
    def __init__(self):
        super().__init__(VendorAllocation)

    def get_with_lock(self, allocation_id: uuid.UUID | str) -> VendorAllocation | None:
        stmt = select(VendorAllocation).where(VendorAllocation.id == allocation_id).with_for_update()
        return db.session.scalar(stmt)

    def check_duplicate(self, trip_day_id: uuid.UUID | str, vendor_id: uuid.UUID | str, service_date: str, service_name: str) -> bool:
        stmt = select(func.count(VendorAllocation.id)).where(
            VendorAllocation.trip_day_id == trip_day_id,
            VendorAllocation.vendor_id == vendor_id,
            VendorAllocation.service_date == service_date,
            VendorAllocation.service_name == service_name
        )
        return (db.session.scalar(stmt) or 0) > 0

    def list_pending_settlements(self, booking_id: uuid.UUID | str) -> List[VendorAllocation]:
        stmt = select(VendorAllocation).join(TripDay).join(TripPlan).where(
            TripPlan.booking_id == booking_id,
            VendorAllocation.is_locked == True
        )
        return list(db.session.scalars(stmt))


class TaskRepository(SQLAlchemyBaseRepository[Task]):
    """
    Repository for Task operations.
    """
    sortable_fields = ["due_date", "priority_id", "task_status_id", "created_at"]
    filterable_fields = ["booking_id", "lead_id", "assigned_to_team_member_id", "task_status_id", "priority_id", "is_deleted"]
    searchable_fields = ["title", "description"]
    default_sort = [("due_date", "asc")]

    def __init__(self):
        super().__init__(Task)

    def count_open_high_priority(self, booking_id: uuid.UUID | str, high_priority_id: uuid.UUID | str, done_status_id: uuid.UUID | str) -> int:
        stmt = select(func.count(Task.id)).where(
            Task.booking_id == booking_id,
            Task.priority_id == high_priority_id,
            Task.task_status_id != done_status_id,
            Task.is_deleted == False
        )
        return db.session.scalar(stmt) or 0


class ChecklistRepository(SQLAlchemyBaseRepository[Checklist]):
    """
    Repository for Checklist child operations.
    """
    def __init__(self):
        super().__init__(Checklist)

    def list_by_booking(self, booking_id: uuid.UUID | str) -> List[Checklist]:
        stmt = select(Checklist).where(Checklist.booking_id == booking_id).order_by(Checklist.item_name.asc())
        return list(db.session.scalars(stmt))

    def completion_rate(self, booking_id: uuid.UUID | str) -> float:
        stmt_total = select(func.count(Checklist.id)).where(Checklist.booking_id == booking_id)
        total = db.session.scalar(stmt_total) or 0
        if total == 0:
            return 100.0
        stmt_done = select(func.count(Checklist.id)).where(Checklist.booking_id == booking_id, Checklist.is_completed == True)
        done = db.session.scalar(stmt_done) or 0
        return round((done / total) * 100.0, 2)

    def all_complete(self, booking_id: uuid.UUID | str) -> bool:
        stmt = select(func.count(Checklist.id)).where(
            Checklist.booking_id == booking_id,
            Checklist.is_completed == False
        )
        return (db.session.scalar(stmt) or 0) == 0
