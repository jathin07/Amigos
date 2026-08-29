import logging
from datetime import datetime, timezone
from sqlalchemy import select

from app.core.extensions import db
from app.domain.events import DomainEvent
from app.workflow.engine import event_bus
from app.models import Booking, BookingStatus, BookingStatusHistory

logger = logging.getLogger(__name__)

@event_bus.subscribe(DomainEvent.ADVANCE_RECEIVED)
def handle_advance_received(payload: dict):
    """
    Subscribes to ADVANCE_RECEIVED. Auto-confirms Booking status if it is WAITING_FOR_ADVANCE,
    which in turn publishes BOOKING_CONFIRMED (auto-scaffolding operations trip plans).
    """
    booking_id = payload["booking_id"]
    logger.info(f"Received ADVANCE_RECEIVED event for booking {booking_id}")
    
    import uuid
    booking = db.session.get(Booking, uuid.UUID(str(booking_id)))
    if not booking or booking.is_deleted:
        logger.warning(f"Booking {booking_id} not found or deleted. Skipping confirmation.")
        return

    current_status = booking.status.code if booking.status else "WAITING_FOR_ADVANCE"
    if current_status == "WAITING_FOR_ADVANCE":
        stmt_confirm = select(BookingStatus).where(BookingStatus.code == "CONFIRMED")
        confirm_status = db.session.scalar(stmt_confirm) or BookingStatus(code="CONFIRMED", name="Confirmed", is_active=True)
        db.session.add(confirm_status)
        db.session.flush()

        old_status_id = booking.booking_status_id
        booking.booking_status_id = confirm_status.id
        booking.confirmed_at = datetime.now(timezone.utc)
        booking.row_version += 1
        db.session.add(booking)

        # Status history log
        hist = BookingStatusHistory(
            booking_id=booking.id,
            from_status_id=old_status_id,
            to_status_id=confirm_status.id,
            notes="Booking auto-confirmed upon receipt of advance payment."
        )
        db.session.add(hist)
        db.session.flush()

        logger.info(f"Auto-confirming booking {booking.id} upon advance received.")
        
        # Fire BookingConfirmed
        event_bus.publish(DomainEvent.BOOKING_CONFIRMED, {
            "booking_id": str(booking.id),
            "confirmed_by": "SYSTEM",
            "occurred_at": datetime.now(timezone.utc).isoformat()
        })
        db.session.commit()
