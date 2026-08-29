import logging

from app.workflow.engine import event_bus
from app.domain.events import DomainEvent
from .service import DashboardQueryService

logger = logging.getLogger("app.dashboard.events")

@event_bus.subscribe(DomainEvent.LEAD_CREATED)
def handle_lead_created(payload: dict):
    logger.info("Handling LEAD_CREATED event. Invalidating CRM widget cache.")
    service = DashboardQueryService()
    service.invalidate_widget("summary_cards")
    service.invalidate_widget("lead_pipeline")

@event_bus.subscribe(DomainEvent.LEAD_STATUS_CHANGED)
def handle_lead_status_changed(payload: dict):
    logger.info("Handling LEAD_STATUS_CHANGED event. Invalidating CRM widget cache.")
    service = DashboardQueryService()
    service.invalidate_widget("summary_cards")
    service.invalidate_widget("lead_pipeline")

@event_bus.subscribe(DomainEvent.BOOKING_CONFIRMED)
def handle_booking_confirmed(payload: dict):
    logger.info("Handling BOOKING_CONFIRMED event. Invalidating booking widget caches.")
    service = DashboardQueryService()
    service.invalidate_widget("summary_cards")
    service.invalidate_widget("booking_pipeline")
    service.invalidate_upcoming_trips()

@event_bus.subscribe(DomainEvent.BOOKING_CANCELLED)
def handle_booking_cancelled(payload: dict):
    logger.info("Handling BOOKING_CANCELLED event. Invalidating booking widget caches.")
    service = DashboardQueryService()
    service.invalidate_widget("summary_cards")
    service.invalidate_widget("booking_pipeline")
    service.invalidate_upcoming_trips()

@event_bus.subscribe(DomainEvent.PAYMENT_VERIFIED)
def handle_payment_verified(payload: dict):
    logger.info("Handling PAYMENT_VERIFIED event. Invalidating finance widget caches.")
    service = DashboardQueryService()
    service.invalidate_widget("summary_cards")
    service.invalidate_widget("finance_summary")
    service.invalidate_widget("revenue_trend")

@event_bus.subscribe(DomainEvent.REFUND_COMPLETED)
def handle_refund_completed(payload: dict):
    logger.info("Handling REFUND_COMPLETED event. Invalidating finance widget caches.")
    service = DashboardQueryService()
    service.invalidate_widget("summary_cards")
    service.invalidate_widget("finance_summary")
    service.invalidate_widget("revenue_trend")

@event_bus.subscribe(DomainEvent.FINANCE_CLOSED)
def handle_finance_closed(payload: dict):
    logger.info("Handling FINANCE_CLOSED event. Invalidating finance widget caches.")
    service = DashboardQueryService()
    service.invalidate_widget("summary_cards")
    service.invalidate_widget("finance_summary")
    service.invalidate_widget("revenue_trend")

@event_bus.subscribe(DomainEvent.TRIP_COMPLETED)
def handle_trip_completed(payload: dict):
    logger.info("Handling TRIP_COMPLETED event. Invalidating ops and booking widget caches.")
    service = DashboardQueryService()
    service.invalidate_widget("summary_cards")
    service.invalidate_widget("operations_overview")
    service.invalidate_widget("booking_pipeline")
    service.invalidate_upcoming_trips()

@event_bus.subscribe(DomainEvent.CHECKLIST_COMPLETED)
def handle_checklist_completed(payload: dict):
    logger.info("Handling CHECKLIST_COMPLETED event. Invalidating ops widget caches.")
    service = DashboardQueryService()
    service.invalidate_widget("operations_overview")

@event_bus.subscribe(DomainEvent.TASK_ASSIGNED)
def handle_task_assigned(payload: dict):
    logger.info("Handling TASK_ASSIGNED event. Invalidating ops widget caches.")
    service = DashboardQueryService()
    service.invalidate_widget("operations_overview")

@event_bus.subscribe(DomainEvent.TASK_COMPLETED)
def handle_task_completed(payload: dict):
    logger.info("Handling TASK_COMPLETED event. Invalidating ops widget caches.")
    service = DashboardQueryService()
    service.invalidate_widget("operations_overview")

@event_bus.subscribe(DomainEvent.VENDOR_ALLOCATION_CONFIRMED)
def handle_vendor_allocation_confirmed(payload: dict):
    logger.info("Handling VENDOR_ALLOCATION_CONFIRMED event. Invalidating ops widget caches.")
    service = DashboardQueryService()
    service.invalidate_widget("summary_cards")
    service.invalidate_widget("operations_overview")
