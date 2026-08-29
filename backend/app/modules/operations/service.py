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
    TripPlan,
    TripPlanStatus,
    TripDay,
    VendorAllocation,
    VendorAllocationStatus,
    Task,
    TaskStatus,
    TaskPriority,
    Checklist,
    Booking,
    BookingStatus,
    Vendor,
    VendorType,
    TeamMember,
    Destination,
)
from .repository import (
    TripPlanRepository,
    TripDayRepository,
    VendorAllocationRepository,
    TaskRepository,
    ChecklistRepository,
)

logger = logging.getLogger("app.operations")


TRIP_PLAN_TRANSITIONS = {
    "PLANNING": ["READY"],
    "READY": ["PLANNING", "STARTED"],
    "STARTED": ["ONGOING"],
    "ONGOING": ["COMPLETED"],
    "COMPLETED": ["CLOSED"],
    "CLOSED": []
}

VENDOR_ALLOCATION_TRANSITIONS = {
    "PENDING": ["NEGOTIATING", "FAILED"],
    "NEGOTIATING": ["PENDING", "CONFIRMED", "FAILED"],
    "CONFIRMED": ["NEGOTIATING", "LOCKED", "FAILED"],
    "LOCKED": ["SETTLED"],
    "SETTLED": [],
    "FAILED": []
}


class OperationsService(BaseService):
    """
    Service layer orchestrator for Operations (TripPlans, Days, Allocations, Tasks, Checklists).
    """

    def __init__(self):
        self.plan_repo = TripPlanRepository()
        self.day_repo = TripDayRepository()
        self.alloc_repo = VendorAllocationRepository()
        self.task_repo = TaskRepository()
        self.checklist_repo = ChecklistRepository()

    # -----------------------------------------------------------------------
    # Helper Status Resolvers
    # -----------------------------------------------------------------------

    def _resolve_trip_plan_status(self, code: str) -> TripPlanStatus:
        stmt = select(TripPlanStatus).where(TripPlanStatus.code == code)
        status = db.session.scalar(stmt)
        if not status:
            status = TripPlanStatus(code=code, name=code.title().replace("_", " "), is_active=True)
            db.session.add(status)
            db.session.flush()
        return status

    def _resolve_vendor_allocation_status(self, code: str) -> VendorAllocationStatus:
        stmt = select(VendorAllocationStatus).where(VendorAllocationStatus.code == code)
        status = db.session.scalar(stmt)
        if not status:
            status = VendorAllocationStatus(code=code, name=code.title().replace("_", " "), is_active=True)
            db.session.add(status)
            db.session.flush()
        return status

    def _resolve_task_status(self, code: str) -> TaskStatus:
        stmt = select(TaskStatus).where(TaskStatus.code == code)
        status = db.session.scalar(stmt)
        if not status:
            status = TaskStatus(code=code, name=code.title().replace("_", " "), is_active=True)
            db.session.add(status)
            db.session.flush()
        return status

    def _resolve_task_priority(self, code: str) -> TaskPriority:
        stmt = select(TaskPriority).where(TaskPriority.code == code)
        priority = db.session.scalar(stmt)
        if not priority:
            priority = TaskPriority(code=code, name=code.title().replace("_", " "), is_active=True)
            db.session.add(priority)
            db.session.flush()
        return priority

    # -----------------------------------------------------------------------
    # TripPlan Operations
    # -----------------------------------------------------------------------

    def create_trip_plan(self, data: dict, actor_id: str | uuid.UUID | None = None) -> TripPlan:
        booking_id = data.get("booking_id")
        booking = db.session.get(Booking, uuid.UUID(str(booking_id)))
        if not booking or booking.is_deleted:
            raise NotFoundException("Booking not found.")

        # Invariant: Booking status must be CONFIRMED or PLANNING or READY
        if booking.status and booking.status.code not in ["CONFIRMED", "PLANNING", "READY"]:
            raise BusinessException(
                "Cannot create a trip plan for a booking that is not confirmed.",
                code="BOOKING_NOT_CONFIRMED"
            )

        # Invariant: Only one active trip plan (is_final = True) per Booking
        existing_plan = self.plan_repo.get_by_booking_id(booking.id)
        if existing_plan:
            raise BusinessException(
                "An active trip plan already exists for this booking.",
                code="TRIP_PLAN_ALREADY_EXISTS"
            )

        # Check if booking is cancelled
        if booking.status and booking.status.code == "CANCELLED":
            raise BusinessException("Cannot create trip plan for a cancelled booking.", code="BOOKING_CANCELLED")

        # Resolve lookups
        status_planning = self._resolve_trip_plan_status("PLANNING")

        prepared_date_val = data.get("prepared_date")
        if isinstance(prepared_date_val, str):
            prepared_date_val = datetime.strptime(prepared_date_val, "%Y-%m-%d").date()

        trip_plan = TripPlan(
            booking_id=booking.id,
            version=1,
            row_version=1,
            is_final=True,
            prepared_by_team_member_id=actor_id or booking.trip_coordinator_team_member_id,
            prepared_date=prepared_date_val or datetime.now(timezone.utc).date(),
            notes=data.get("notes"),
            status_id=status_planning.id,
            trip_plan_type="MANUAL"
        )
        if actor_id:
            trip_plan.created_by_team_member_id = actor_id
            trip_plan.updated_by_team_member_id = actor_id

        db.session.add(trip_plan)
        db.session.flush()

        # Scaffold TripDays based on booking duration
        start_date = booking.trip_start_date
        end_date = booking.trip_end_date
        total_days = (end_date - start_date).days + 1 if start_date and end_date else 1
        for i in range(1, total_days + 1):
            day = TripDay(
                trip_plan_id=trip_plan.id,
                day_number=i,
                notes=f"Day {i} plan"
            )
            db.session.add(day)

        self.commit()

        # Publish Event
        event_bus.publish(
            DomainEvent.TRIP_PLAN_CREATED,
            {
                "trip_plan_id": str(trip_plan.id),
                "booking_id": str(booking.id),
                "created_by": str(actor_id) if actor_id else None,
                "occurred_at": datetime.now(timezone.utc).isoformat()
            }
        )

        return trip_plan

    def transition_status(self, trip_plan_id: str | uuid.UUID, target_status_code: str, actor_id: str | uuid.UUID | None = None) -> TripPlan:
        trip_plan = self.plan_repo.get_by_id(trip_plan_id)
        if not trip_plan:
            raise NotFoundException("Trip plan not found.")

        current_status = trip_plan.status.code if trip_plan.status else "PLANNING"
        
        # Idempotency Check
        if current_status == target_status_code:
            return trip_plan

        allowed = TRIP_PLAN_TRANSITIONS.get(current_status, [])
        if target_status_code not in allowed:
            raise BusinessException(
                f"Invalid status transition from {current_status} to {target_status_code}.",
                code="INVALID_STATE_TRANSITION"
            )

        booking = trip_plan.booking
        if booking and booking.status and booking.status.code == "CANCELLED":
            raise BusinessException("Cannot update trip plan status of a cancelled booking.", code="BOOKING_CANCELLED")

        # Guard Conditions
        if target_status_code == "READY":
            # Guard: All checklist items must be complete
            if not self.checklist_repo.all_complete(booking.id):
                raise BusinessException(
                    "Cannot set trip plan to READY. Checklist has incomplete items.",
                    code="CHECKLIST_INCOMPLETE"
                )
            # Guard: All vendor allocations must be LOCKED
            for day in trip_plan.trip_days:
                for alloc in day.vendor_allocations:
                    if not alloc.is_locked:
                        raise BusinessException(
                            "Cannot set trip plan to READY. All vendor allocations must be confirmed and locked.",
                            code="UNCONFIRMED_ALLOCATIONS"
                        )

        if target_status_code == "STARTED":
            if booking.status and booking.status.code != "CONFIRMED" and booking.status.code != "PLANNING" and booking.status.code != "READY":
                raise BusinessException(
                    "Cannot start a trip plan unless the parent booking is confirmed.",
                    code="BOOKING_NOT_CONFIRMED"
                )

        # Apply transition
        status_obj = self._resolve_trip_plan_status(target_status_code)
        trip_plan.status_id = status_obj.id
        trip_plan.row_version += 1
        if actor_id:
            trip_plan.updated_by_team_member_id = actor_id

        # Update Booking Status in tandem
        if target_status_code in ["READY", "STARTED", "ONGOING"]:
            stmt = select(BookingStatus).where(BookingStatus.code == target_status_code)
            booking_status = db.session.scalar(stmt)
            if booking_status:
                booking.booking_status_id = booking_status.id
                booking.row_version += 1

        self.commit()

        # Publish appropriate domain event
        if target_status_code == "READY":
            event_bus.publish(DomainEvent.TRIP_READY, {"trip_plan_id": str(trip_plan.id), "booking_id": str(booking.id), "occurred_at": datetime.now(timezone.utc).isoformat()})
        elif target_status_code == "STARTED":
            event_bus.publish(DomainEvent.TRIP_STARTED, {"trip_plan_id": str(trip_plan.id), "booking_id": str(booking.id), "started_at": datetime.now(timezone.utc).isoformat()})
        elif target_status_code == "CLOSED":
            event_bus.publish(DomainEvent.TRIP_CLOSED, {"trip_plan_id": str(trip_plan.id), "booking_id": str(booking.id), "occurred_at": datetime.now(timezone.utc).isoformat()})

        return trip_plan

    def validate_completion(self, trip_plan_id: str | uuid.UUID) -> dict:
        trip_plan = self.plan_repo.get_by_id(trip_plan_id)
        if not trip_plan:
            raise NotFoundException("Trip plan not found.")

        booking = trip_plan.booking
        checklist_rate = self.checklist_repo.completion_rate(booking.id)
        
        high_priority = self._resolve_task_priority("HIGH")
        done_status = self._resolve_task_status("DONE")
        open_high_tasks = self.task_repo.count_open_high_priority(booking.id, high_priority.id, done_status.id)

        unconfirmed_allocs = 0
        for day in trip_plan.trip_days:
            for alloc in day.vendor_allocations:
                if not alloc.is_locked:
                    unconfirmed_allocs += 1

        blocking_reasons = []
        if checklist_rate < 100.0:
            blocking_reasons.append("Checklist contains incomplete items.")
        if unconfirmed_allocs > 0:
            blocking_reasons.append("Trip contains unconfirmed/unlocked vendor allocations.")
        if open_high_tasks > 0:
            blocking_reasons.append("There are open high-priority tasks associated with this trip.")

        return {
            "can_complete": len(blocking_reasons) == 0,
            "blocking_reasons": blocking_reasons,
            "checklist_completion_rate": checklist_rate,
            "unconfirmed_allocations": unconfirmed_allocs,
            "open_high_priority_tasks": open_high_tasks
        }

    def complete_trip(self, trip_plan_id: str | uuid.UUID, notes: str | None = None, actor_id: str | uuid.UUID | None = None) -> TripPlan:
        trip_plan = self.plan_repo.get_by_id(trip_plan_id)
        if not trip_plan:
            raise NotFoundException("Trip plan not found.")

        # Idempotency check
        if trip_plan.status.code == "COMPLETED":
            return trip_plan

        # Invariant validations
        val_result = self.validate_completion(trip_plan_id)
        if not val_result["can_complete"]:
            code = "CHECKLIST_INCOMPLETE" if val_result["checklist_completion_rate"] < 100.0 else (
                "UNCONFIRMED_ALLOCATIONS" if val_result["unconfirmed_allocations"] > 0 else "OPEN_HIGH_PRIORITY_TASKS"
            )
            raise BusinessException(
                f"Cannot complete trip. Reasons: {', '.join(val_result['blocking_reasons'])}",
                code=code
            )

        booking = trip_plan.booking
        if booking and booking.status and booking.status.code == "CANCELLED":
            raise BusinessException("Cannot complete a trip plan for a cancelled booking.", code="BOOKING_CANCELLED")

        # Apply state changes
        status_completed = self._resolve_trip_plan_status("COMPLETED")
        trip_plan.status_id = status_completed.id
        trip_plan.notes = notes or trip_plan.notes
        trip_plan.approved_by_team_member_id = actor_id
        trip_plan.approved_at = datetime.now(timezone.utc)
        trip_plan.row_version += 1

        # Also update Booking status to COMPLETED in the same transaction
        stmt = select(BookingStatus).where(BookingStatus.code == "COMPLETED")
        booking_status = db.session.scalar(stmt)
        if booking_status:
            booking.booking_status_id = booking_status.id
            booking.row_version += 1
            if actor_id:
                booking.updated_by_team_member_id = actor_id

        self.commit()

        # Publish Event
        event_bus.publish(
            DomainEvent.TRIP_COMPLETED,
            {
                "trip_plan_id": str(trip_plan.id),
                "booking_id": str(booking.id),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "coordinator_id": str(booking.trip_coordinator_team_member_id) if booking else None
            }
        )

        return trip_plan

    # -----------------------------------------------------------------------
    # TripDay Operations
    # -----------------------------------------------------------------------

    def update_trip_day(self, trip_plan_id: str | uuid.UUID, day_id: str | uuid.UUID, data: dict, actor_id: str | uuid.UUID | None = None) -> TripDay:
        trip_plan = self.plan_repo.get_by_id(trip_plan_id)
        if not trip_plan:
            raise NotFoundException("Trip plan not found.")

        # Completed trip guard
        if trip_plan.status.code in ["COMPLETED", "CLOSED"]:
            raise BusinessException("Cannot update trip day of a completed or closed trip plan.", code="TRIP_ALREADY_COMPLETED")

        booking = trip_plan.booking
        if booking and booking.status and booking.status.code == "CANCELLED":
            raise BusinessException("Cannot update trip day of a cancelled booking.", code="BOOKING_CANCELLED")

        day = self.day_repo.get_day(trip_plan.id, day_id)
        if not day:
            raise NotFoundException("Trip day not found.")

        # Update fields
        if "start_location" in data:
            day.start_location = data["start_location"]
        if "end_location" in data:
            day.end_location = data["end_location"]
        if "overnight_destination_id" in data:
            dest_id = data["overnight_destination_id"]
            if dest_id:
                dest = db.session.get(Destination, uuid.UUID(str(dest_id)))
                if not dest:
                    raise NotFoundException("Destination not found.")
                day.overnight_destination_id = dest.id
            else:
                day.overnight_destination_id = None
        if "start_time" in data:
            day.start_time = data["start_time"]
        if "end_time" in data:
            day.end_time = data["end_time"]
        if "morning_plan" in data:
            day.morning_plan = data["morning_plan"]
        if "afternoon_plan" in data:
            day.afternoon_plan = data["afternoon_plan"]
        if "evening_plan" in data:
            day.evening_plan = data["evening_plan"]
        if "night_stay" in data:
            day.night_stay = data["night_stay"]
        if "notes" in data:
            day.notes = data["notes"]

        trip_plan.row_version += 1
        if actor_id:
            trip_plan.updated_by_team_member_id = actor_id

        self.commit()
        return day

    # -----------------------------------------------------------------------
    # VendorAllocation Operations
    # -----------------------------------------------------------------------

    def create_vendor_allocation(self, trip_plan_id: str | uuid.UUID, day_id: str | uuid.UUID, data: dict, actor_id: str | uuid.UUID | None = None) -> VendorAllocation:
        trip_plan = self.plan_repo.get_by_id(trip_plan_id)
        if not trip_plan:
            raise NotFoundException("Trip plan not found.")

        # Completed trip guard
        if trip_plan.status.code in ["COMPLETED", "CLOSED"]:
            raise BusinessException("Cannot add allocation to a completed or closed trip plan.", code="TRIP_ALREADY_COMPLETED")

        booking = trip_plan.booking
        if booking and booking.status and booking.status.code == "CANCELLED":
            raise BusinessException("Cannot add allocation to a cancelled booking.", code="BOOKING_CANCELLED")

        day = self.day_repo.get_day(trip_plan.id, day_id)
        if not day:
            raise NotFoundException("Trip day not found.")

        vendor_id = uuid.UUID(str(data.get("vendor_id")))
        vendor = db.session.get(Vendor, vendor_id)
        if not vendor or vendor.is_deleted:
            raise NotFoundException("Vendor not found.")

        service_type_id = uuid.UUID(str(data.get("service_type_id")))
        v_type = db.session.get(VendorType, service_type_id)
        if not v_type:
            raise NotFoundException("Vendor type not found.")

        service_date_val = data.get("service_date")
        if isinstance(service_date_val, str):
            service_date_val = datetime.strptime(service_date_val, "%Y-%m-%d").date()

        # Invariant: Service date within booking dates
        if booking.trip_start_date and booking.trip_end_date:
            if service_date_val < booking.trip_start_date or service_date_val > booking.trip_end_date:
                raise BusinessException(
                    "Service date must fall within the booking trip start and end dates.",
                    code="SERVICE_DATE_OUT_OF_RANGE"
                )

        service_name = data.get("service_name")
        # Duplicate detection check
        if self.alloc_repo.check_duplicate(day.id, vendor.id, service_date_val, service_name):
            raise BusinessException(
                "A duplicate vendor allocation exists for the same vendor, date, and service.",
                code="DUPLICATE_VENDOR_ALLOCATION"
            )

        quantity = int(data.get("quantity", 1))
        unit_price = Decimal(str(data.get("unit_price", 0)))
        quoted_amount = quantity * unit_price

        status_pending = self._resolve_vendor_allocation_status("PENDING")

        allocation = VendorAllocation(
            trip_day_id=day.id,
            vendor_id=vendor.id,
            service_name=service_name,
            service_type_id=v_type.id,
            service_date=service_date_val,
            quantity=quantity,
            unit_price=unit_price,
            quoted_amount=quoted_amount,
            allocation_status_id=status_pending.id,
            is_locked=False,
            notes=data.get("notes")
        )
        if actor_id:
            allocation.created_by_team_member_id = actor_id
            allocation.updated_by_team_member_id = actor_id

        db.session.add(allocation)
        trip_plan.row_version += 1
        self.commit()

        return allocation

    def confirm_vendor_allocation(self, allocation_id: str | uuid.UUID, data: dict, actor_id: str | uuid.UUID | None = None) -> VendorAllocation:
        # SELECT FOR UPDATE lock safety
        allocation = self.alloc_repo.get_with_lock(allocation_id)
        if not allocation:
            raise NotFoundException("Vendor allocation not found.")

        # Lock check
        if allocation.is_locked:
            raise BusinessException("Cannot confirm a locked vendor allocation.", code="VENDOR_ALLOCATION_LOCKED")

        trip_day = allocation.trip_day
        trip_plan = trip_day.trip_plan
        if trip_plan.status.code in ["COMPLETED", "CLOSED"]:
            raise BusinessException("Cannot confirm allocation for a completed or closed trip plan.", code="TRIP_ALREADY_COMPLETED")

        booking = trip_plan.booking
        if booking and booking.status and booking.status.code == "CANCELLED":
            raise BusinessException("Cannot confirm allocation for a cancelled booking.", code="BOOKING_CANCELLED")

        confirmed_price = Decimal(str(data.get("confirmed_price", 0)))

        # Invariant: confirmed price <= quoted amount * 1.10
        max_allowed = allocation.quoted_amount * Decimal("1.10")
        if confirmed_price > max_allowed:
            raise BusinessException(
                "Confirmed price exceeds the quoted amount by more than 10%.",
                code="ALLOCATION_PRICE_OVERRUN"
            )

        vendor = allocation.vendor
        if not vendor:
            raise NotFoundException("Vendor not found.")

        # Capture Snapshot
        allocation.vendor_name_snapshot = vendor.vendor_name
        allocation.vendor_phone_snapshot = vendor.phone
        allocation.vendor_address_snapshot = vendor.address
        allocation.confirmed_price = confirmed_price
        allocation.confirmed_by_team_member_id = actor_id
        allocation.confirmed_at = datetime.now(timezone.utc)

        # Enforce transition confirmed -> auto locks
        status_confirmed = self._resolve_vendor_allocation_status("CONFIRMED")
        allocation.allocation_status_id = status_confirmed.id

        self.commit()

        # Publish Event
        event_bus.publish(
            DomainEvent.VENDOR_ALLOCATION_CONFIRMED,
            {
                "allocation_id": str(allocation.id),
                "vendor_id": str(allocation.vendor_id),
                "trip_day_id": str(allocation.trip_day_id),
                "confirmed_price": str(confirmed_price),
                "booking_id": str(booking.id) if booking else None,
                "occurred_at": datetime.now(timezone.utc).isoformat()
            }
        )

        return allocation

    def lock_vendor_allocation(self, allocation_id: str | uuid.UUID, actor_id: str | uuid.UUID | None = None) -> VendorAllocation:
        allocation = self.alloc_repo.get_with_lock(allocation_id)
        if not allocation:
            raise NotFoundException("Vendor allocation not found.")

        # Idempotency Check
        if allocation.is_locked:
            return allocation

        if allocation.allocation_status.code != "CONFIRMED":
            raise BusinessException("Only confirmed allocations can be locked.", code="INVALID_STATE_TRANSITION")

        status_locked = self._resolve_vendor_allocation_status("LOCKED")
        allocation.allocation_status_id = status_locked.id
        allocation.is_locked = True
        if actor_id:
            allocation.updated_by_team_member_id = actor_id

        self.commit()

        event_bus.publish(
            DomainEvent.VENDOR_ALLOCATION_LOCKED,
            {
                "allocation_id": str(allocation.id),
                "locked_by": str(actor_id) if actor_id else None,
                "locked_at": datetime.now(timezone.utc).isoformat()
            }
        )

        return allocation

    # -----------------------------------------------------------------------
    # Checklist Operations
    # -----------------------------------------------------------------------

    def update_checklist_item(self, item_id: str | uuid.UUID, is_completed: bool, actor_id: str | uuid.UUID | None = None) -> Checklist:
        item = self.checklist_repo.get(item_id)
        if not item:
            raise NotFoundException("Checklist item not found.")

        # Trip completed guard
        stmt = select(TripPlan).where(TripPlan.booking_id == item.booking_id, TripPlan.is_final == True)
        trip_plan = db.session.scalar(stmt)
        if trip_plan and trip_plan.status.code in ["COMPLETED", "CLOSED"]:
            raise BusinessException("Cannot update checklist of a completed or closed trip.", code="TRIP_ALREADY_COMPLETED")

        # Booking cancellation guard
        booking = db.session.get(Booking, item.booking_id)
        if booking and booking.status and booking.status.code == "CANCELLED":
            raise BusinessException("Cannot update checklist of a cancelled booking.", code="BOOKING_CANCELLED")

        # Apply changes
        item.is_completed = is_completed
        item.completed_at = datetime.now(timezone.utc) if is_completed else None
        if actor_id:
            item.updated_by_team_member_id = actor_id

        self.commit()

        # Check if all completed
        if is_completed:
            event_bus.publish(DomainEvent.CHECKLIST_ITEM_COMPLETED, {"item_id": str(item.id), "booking_id": str(item.booking_id), "occurred_at": datetime.now(timezone.utc).isoformat()})
            if self.checklist_repo.all_complete(item.booking_id):
                event_bus.publish(DomainEvent.CHECKLIST_COMPLETED, {"booking_id": str(item.booking_id), "completed_at": datetime.now(timezone.utc).isoformat()})
        else:
            event_bus.publish(DomainEvent.CHECKLIST_REOPENED, {"item_id": str(item.id), "booking_id": str(item.booking_id), "occurred_at": datetime.now(timezone.utc).isoformat()})

        return item

    def bulk_complete_checklist(self, booking_id: str | uuid.UUID, item_ids: List[str | uuid.UUID], actor_id: str | uuid.UUID | None = None) -> dict:
        completed_count = 0
        for i_id in item_ids:
            try:
                self.update_checklist_item(i_id, True, actor_id)
                completed_count += 1
            except (NotFoundException, BusinessException):
                continue
        return {"completed_count": completed_count}

    # -----------------------------------------------------------------------
    # Task Operations
    # -----------------------------------------------------------------------

    def create_task(self, data: dict, actor_id: str | uuid.UUID | None = None) -> Task:
        assignee_id = uuid.UUID(str(data.get("assigned_to_team_member_id")))
        assignee = db.session.get(TeamMember, assignee_id)
        if not assignee or assignee.is_deleted or not assignee.is_active:
            raise ValidationException("Assigned team member is invalid or inactive.", code="TEAM_MEMBER_NOT_FOUND")

        booking_id = data.get("booking_id")
        lead_id = data.get("lead_id")

        booking = None
        if booking_id:
            booking = db.session.get(Booking, uuid.UUID(str(booking_id)))
            if not booking or booking.is_deleted:
                raise NotFoundException("Booking not found.")

        lead = None
        if lead_id:
            lead = db.session.get(Lead, uuid.UUID(str(lead_id)))
            if not lead or lead.is_deleted:
                raise NotFoundException("Lead not found.")

        parent_task_id = data.get("parent_task_id")
        if parent_task_id:
            parent = self.task_repo.get(uuid.UUID(str(parent_task_id)))
            if not parent:
                raise NotFoundException("Parent task not found.")

        priority_id = uuid.UUID(str(data.get("priority_id")))
        priority = db.session.get(TaskPriority, priority_id)
        if not priority:
            priority = self._resolve_task_priority("MEDIUM")

        status_id = uuid.UUID(str(data.get("task_status_id")))
        status = db.session.get(TaskStatus, status_id)
        if not status:
            status = self._resolve_task_status("PENDING")

        due_date_val = data.get("due_date")
        if isinstance(due_date_val, str):
            due_date_val = datetime.strptime(due_date_val, "%Y-%m-%d").date()

        task = Task(
            booking_id=booking.id if booking else None,
            lead_id=lead.id if lead else None,
            assigned_to_team_member_id=assignee.id,
            assigned_by_team_member_id=actor_id,
            parent_task_id=parent_task_id,
            title=data.get("title"),
            description=data.get("description"),
            due_date=due_date_val,
            task_status_id=status.id,
            priority_id=priority.id,
            estimated_hours=data.get("estimated_hours")
        )
        if actor_id:
            task.created_by_team_member_id = actor_id
            task.updated_by_team_member_id = actor_id

        db.session.add(task)
        self.commit()

        # Publish Event
        event_bus.publish(
            DomainEvent.TASK_ASSIGNED,
            {
                "task_id": str(task.id),
                "title": task.title,
                "assigned_to_id": str(task.assigned_to_team_member_id),
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "booking_id": str(task.booking_id) if task.booking_id else None
            }
        )

        return task

    def update_task_status(self, task_id: str | uuid.UUID, data: dict, actor_id: str | uuid.UUID | None = None) -> Task:
        task = self.task_repo.get(task_id)
        if not task or task.is_deleted:
            raise NotFoundException("Task not found.")

        status_id = uuid.UUID(str(data.get("task_status_id")))
        status = db.session.get(TaskStatus, status_id)
        if not status:
            raise NotFoundException("Task status not found.")

        # Idempotency Check
        if task.task_status_id == status.id:
            return task

        task.task_status_id = status.id
        if status.code == "DONE":
            task.completed_date = datetime.now(timezone.utc).date()
        else:
            task.completed_date = None

        if "actual_hours" in data:
            task.actual_hours = data["actual_hours"]
        if actor_id:
            task.updated_by_team_member_id = actor_id

        self.commit()

        if status.code == "DONE":
            event_bus.publish(
                DomainEvent.TASK_COMPLETED,
                {
                    "task_id": str(task.id),
                    "title": task.title,
                    "completed_by": str(actor_id) if actor_id else None,
                    "completed_date": task.completed_date.isoformat() if task.completed_date else None
                }
            )

        return task

    def bulk_assign_tasks(self, task_ids: List[str | uuid.UUID], team_member_id: str | uuid.UUID, actor_id: str | uuid.UUID | None = None) -> dict:
        assignee = db.session.get(TeamMember, uuid.UUID(str(team_member_id)))
        if not assignee or assignee.is_deleted or not assignee.is_active:
            raise ValidationException("Assigned team member is invalid or inactive.", code="TEAM_MEMBER_NOT_FOUND")

        assigned_count = 0
        for t_id in task_ids:
            task = self.task_repo.get(t_id)
            if task and not task.is_deleted:
                # Idempotency check
                if task.assigned_to_team_member_id == assignee.id:
                    continue
                task.assigned_to_team_member_id = assignee.id
                task.assigned_by_team_member_id = actor_id
                if actor_id:
                    task.updated_by_team_member_id = actor_id
                db.session.add(task)
                assigned_count += 1
                
                # Publish Event per assignment
                event_bus.publish(
                    DomainEvent.TASK_ASSIGNED,
                    {
                        "task_id": str(task.id),
                        "title": task.title,
                        "assigned_to_id": str(task.assigned_to_team_member_id),
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "booking_id": str(task.booking_id) if task.booking_id else None
                    }
                )

        self.commit()
        return {"assigned_count": assigned_count}

    def bulk_update_task_status(self, task_ids: List[str | uuid.UUID], task_status_id: str | uuid.UUID, actor_id: str | uuid.UUID | None = None) -> dict:
        status = db.session.get(TaskStatus, uuid.UUID(str(task_status_id)))
        if not status:
            raise NotFoundException("Task status not found.")

        updated_count = 0
        for t_id in task_ids:
            task = self.task_repo.get(t_id)
            if task and not task.is_deleted:
                # Idempotency check
                if task.task_status_id == status.id:
                    continue
                task.task_status_id = status.id
                if status.code == "DONE":
                    task.completed_date = datetime.now(timezone.utc).date()
                else:
                    task.completed_date = None
                if actor_id:
                    task.updated_by_team_member_id = actor_id
                db.session.add(task)
                updated_count += 1

                if status.code == "DONE":
                    event_bus.publish(
                        DomainEvent.TASK_COMPLETED,
                        {
                            "task_id": str(task.id),
                            "title": task.title,
                            "completed_by": str(actor_id) if actor_id else None,
                            "completed_date": task.completed_date.isoformat() if task.completed_date else None
                        }
                    )

        self.commit()
        return {"updated_count": updated_count}

    def soft_delete_task(self, task_id: str | uuid.UUID, actor_id: str | uuid.UUID | None = None) -> None:
        task = self.task_repo.get(task_id)
        if not task or task.is_deleted:
            raise NotFoundException("Task not found.")

        task.is_deleted = True
        if actor_id:
            task.updated_by_team_member_id = actor_id
        self.commit()
