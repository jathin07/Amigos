import uuid
import logging
from datetime import datetime, timezone

from app.workflow.engine import event_bus
from app.domain.events import DomainEvent
from app.core.extensions import db
from app.models import Booking, TripPlan, Checklist
from .service import OperationsService

logger = logging.getLogger("app.operations.events")


@event_bus.subscribe(DomainEvent.BOOKING_CONFIRMED)
def handle_booking_confirmed(payload: dict):
    """
    Subscribed to DomainEvent.BOOKING_CONFIRMED.
    Idempotently creates a TripPlan stub, scaffolds days and seeds default checklists.
    """
    booking_id_str = payload.get("booking_id")
    if not booking_id_str:
        logger.warning("BOOKING_CONFIRMED payload missing booking_id")
        return

    booking_id = uuid.UUID(booking_id_str)
    booking = db.session.get(Booking, booking_id)
    if not booking or booking.is_deleted:
        logger.warning(f"Booking {booking_id} not found or deleted")
        return

    # Idempotency check: check if TripPlan already exists
    stmt = select(TripPlan).where(TripPlan.booking_id == booking_id, TripPlan.is_final == True)
    existing_plan = db.session.scalar(stmt)
    if existing_plan:
        logger.info(f"TripPlan already exists for Booking {booking_id}. Skipping creation.")
        return

    # Create the TripPlan
    service = OperationsService()
    try:
        # Create TripPlan stub (which also scaffolds TripDays)
        plan = service.create_trip_plan(
            {"booking_id": str(booking_id), "prepared_date": datetime.now(timezone.utc).date().isoformat()},
            actor_id=booking.trip_coordinator_team_member_id
        )

        # Seed default checklists
        default_items = [
            "Verify traveler ID proofs",
            "Confirm transport vendor allocation",
            "Confirm accommodation vendor allocation"
        ]
        for item_name in default_items:
            checklist_item = Checklist(
                booking_id=booking_id,
                item_name=item_name,
                is_completed=False
            )
            db.session.add(checklist_item)

        db.session.commit()
        logger.info(f"Successfully created TripPlan stub and default checklists for Booking {booking_id}")
    except Exception as ex:
        db.session.rollback()
        logger.exception(f"Failed to auto-create TripPlan for confirmed booking {booking_id}")


@event_bus.subscribe(DomainEvent.FINANCE_CLOSED)
def handle_finance_closed(payload: dict):
    """
    Subscribed to DomainEvent.FINANCE_CLOSED.
    Transitions TripPlan status to CLOSED.
    """
    booking_id_str = payload.get("booking_id")
    if not booking_id_str:
        logger.warning("FINANCE_CLOSED payload missing booking_id")
        return

    booking_id = uuid.UUID(booking_id_str)
    stmt = select(TripPlan).where(TripPlan.booking_id == booking_id, TripPlan.is_final == True)
    trip_plan = db.session.scalar(stmt)
    if not trip_plan:
        logger.warning(f"TripPlan not found for Booking {booking_id}")
        return

    service = OperationsService()
    try:
        service.transition_status(trip_plan.id, "CLOSED")
        logger.info(f"Successfully closed TripPlan {trip_plan.id} after finance closure")
    except Exception:
        logger.exception(f"Failed to transition TripPlan {trip_plan.id} to CLOSED status")


from sqlalchemy import select  # local helper import for select in event handlers
