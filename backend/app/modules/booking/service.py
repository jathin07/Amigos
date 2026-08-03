import uuid
import logging
from datetime import datetime, timezone, date
from decimal import Decimal

from sqlalchemy import select, func, text
from sqlalchemy.exc import IntegrityError
from flask import current_app

from app.core.base_service import BaseService
from app.domain.exceptions import NotFoundException, ValidationException, BusinessException
from app.domain.events import DomainEvent
from app.workflow.engine import event_bus
from app.core.extensions import db
from app.models import (
    Booking,
    BookingStatus,
    BookingSource,
    BookingType,
    Traveler,
    Document,
    PaymentSchedule,
    BookingStatusHistory,
    Proposal,
    ProposalStatus,
    Lead,
    Customer,
    TeamMember,
    PaymentStatus,
    DocumentType,
)
from .repository import (
    BookingRepository,
    _TravelerRepository,
    _DocumentRepository,
    _PaymentScheduleRepository,
    _BookingStatusHistoryRepository,
)

logger = logging.getLogger("app.booking")

# ---------------------------------------------------------------------------
# Status transition rules
# ---------------------------------------------------------------------------
BOOKING_TRANSITIONS = {
    "WAITING_FOR_ADVANCE": ["CONFIRMED", "CANCELLED"],
    "CONFIRMED": ["PLANNING", "CANCELLED"],
    "PLANNING": ["READY", "CANCELLED"],
    "READY": ["ONGOING", "CANCELLED"],
    "ONGOING": ["COMPLETED"],
    "COMPLETED": ["CLOSED"],
    "CLOSED": [],
    "CANCELLED": []
}


class BookingService(BaseService):
    """
    Service layer orchestrator for the Booking aggregate.
    """

    def __init__(self):
        self.repository = BookingRepository()
        self.traveler_repo = _TravelerRepository()
        self.document_repo = _DocumentRepository()
        self.payment_schedule_repo = _PaymentScheduleRepository()
        self.history_repo = _BookingStatusHistoryRepository()

    # -----------------------------------------------------------------------
    # Helper Invariant Validations
    # -----------------------------------------------------------------------

    def _validate_installments(self, installments_data: list[dict], total_amount: Decimal, booking_date_val: date):
        """
        Validates payment schedule invariants:
        - Sum of percentages is exactly 100.00%
        - Every percentage > 0.00% and <= 100.00%
        - Due dates are strictly ascending and >= booking_date
        - Installment numbers start at 1 and increment sequentially
        """
        if not installments_data:
            raise ValidationException("At least one installment is required.", code="ERR_PAYMENT_PERCENT_INVALID")

        installments_sorted = sorted(installments_data, key=lambda x: x["installment_no"])
        
        # Check sequence
        expected_no = 1
        total_percentage = Decimal("0.00")
        prev_due_date = None

        for inst in installments_sorted:
            inst_no = inst["installment_no"]
            pct = Decimal(str(inst["percentage"]))
            due_date = inst["due_date"]
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, "%Y-%m-%d").date()

            if inst_no != expected_no:
                raise ValidationException(
                    f"Installment numbers must be sequential starting at 1. Expected {expected_no}, got {inst_no}.",
                    code="ERR_PAYMENT_PERCENT_INVALID"
                )
            
            if pct <= Decimal("0.00") or pct > Decimal("100.00"):
                raise ValidationException(
                    f"Percentage for installment {inst_no} must be between 0.01 and 100.00.",
                    code="ERR_PAYMENT_PERCENT_INVALID"
                )

            if due_date < booking_date_val:
                raise ValidationException(
                    f"Installment {inst_no} due date cannot precede the booking date.",
                    code="ERR_PAYMENT_PERCENT_INVALID"
                )

            if prev_due_date and due_date <= prev_due_date:
                raise ValidationException(
                    f"Installment due dates must be strictly increasing. Installment {inst_no} is out of order.",
                    code="ERR_PAYMENT_PERCENT_INVALID"
                )

            total_percentage += pct
            prev_due_date = due_date
            expected_no += 1

        if total_percentage != Decimal("100.00"):
            raise ValidationException(
                f"Installment percentages must sum to exactly 100.00%. Current sum: {total_percentage}%.",
                code="ERR_PAYMENT_PERCENT_INVALID"
            )

    def _validate_travelers(self, travelers_data: list[dict]):
        """
        Validates traveler manifest invariants:
        - Manifest is not empty
        - Manifest has exactly one lead traveler (is_group_leader = True)
        - Age bounds between 0 and 120
        """
        if not travelers_data:
            raise ValidationException("At least one traveler is required.", code="ERR_LEAD_TRAVELER_REQUIRED")

        lead_count = sum(1 for t in travelers_data if t.get("is_group_leader") is True)
        if lead_count != 1:
            raise ValidationException(
                f"Traveler manifest must contain exactly one Lead Traveler. Found {lead_count}.",
                code="ERR_LEAD_TRAVELER_REQUIRED"
            )

        for traveler in travelers_data:
            age = traveler.get("age")
            if age is not None and (age < 0 or age > 120):
                raise ValidationException("Traveler age must be between 0 and 120.", code="ERR_VALIDATION")

    def _generate_booking_number(self, year: int) -> str:
        """
        Generates formatting-controlled AMT-YYYY-XXXXX sequence.
        Uses a retry loop to mitigate concurrent indexing collisions.
        """
        # Lock lookup query or perform sequence increment
        count = self.repository.count_bookings_by_year(year)
        next_seq = count + 1
        return f"AMT-{year}-{next_seq:05d}"

    # -----------------------------------------------------------------------
    # Core Write Actions
    # -----------------------------------------------------------------------

    def create_booking(
        self,
        data: dict,
        context_team_member_id: str | uuid.UUID | None = None
    ) -> Booking:
        """
        Generates a booking draft from a finalized proposal version.
        Wraps creation in an atomic transaction with rollback scopes.
        """
        proposal_id = data.get("proposal_id")
        if not proposal_id:
            raise ValidationException("proposal_id is required.", code="ERR_VALIDATION")

        if isinstance(proposal_id, str):
            try:
                proposal_id = uuid.UUID(proposal_id)
            except ValueError:
                raise ValidationException("Invalid UUID format for proposal_id.", code="ERR_VALIDATION")

        proposal = db.session.get(Proposal, proposal_id)
        if not proposal:
            raise NotFoundException(f"Proposal with ID {proposal_id} not found.")

        # Invariant 1: Proposal must be finalized
        if not proposal.is_final:
            raise BusinessException(
                "Cannot create a booking from a draft proposal. Finalization is required.",
                code="ERR_PROPOSAL_NOT_FINALIZED"
            )

        # check duplicate bookings
        stmt_dup = select(Booking).where(Booking.proposal_version_id == proposal.id, Booking.is_deleted == False)
        if db.session.scalar(stmt_dup):
            raise BusinessException(
                "A booking has already been created for this proposal version.",
                code="ERR_BOOKING_ALREADY_EXISTS"
            )

        lead = proposal.lead
        if not lead:
            raise NotFoundException("Lead associated with the proposal not found.")

        # Invariant 2: Booking must belong to customer (Find/Create via delegate)
        stmt_cust = select(Customer).where(Customer.primary_contact_person_id == lead.contact_person_id)
        customer = db.session.scalar(stmt_cust)
        if not customer:
            customer = Customer(
                primary_contact_person_id=lead.contact_person_id,
                customer_type="B2C",
                customer_since=datetime.now(timezone.utc).date()
            )
            db.session.add(customer)
            db.session.flush()

        booking_date_val = datetime.now(timezone.utc).date()
        total_amount_val = Decimal(str(proposal.total_amount or "0.00"))

        # Validations
        self._validate_travelers(data.get("travelers", []))
        self._validate_installments(data.get("installments", []), total_amount_val, booking_date_val)

        # Resolve lookup metadata owned by Master module
        stmt_type = select(BookingType).where(BookingType.code == "INDIVIDUAL")
        b_type = db.session.scalar(stmt_type) or BookingType(code="INDIVIDUAL", name="Individual", is_active=True)
        
        stmt_src = select(BookingSource).where(BookingSource.code == "CRM_CONVERSION")
        b_source = db.session.scalar(stmt_src) or BookingSource(code="CRM_CONVERSION", name="CRM Conversion", is_active=True)

        stmt_status = select(BookingStatus).where(BookingStatus.code == "WAITING_FOR_ADVANCE")
        b_status = db.session.scalar(stmt_status) or BookingStatus(code="WAITING_FOR_ADVANCE", name="Waiting for Advance", is_active=True)

        db.session.add(b_type)
        db.session.add(b_source)
        db.session.add(b_status)
        db.session.flush()

        # Eager load relationship names to snapshot
        package_name = lead.package.title if lead.package else "Custom Trip"
        
        org_name = "Individual"
        if lead.organization_division_id:
            from app.models import OrganizationDivision, Organization
            div = db.session.get(OrganizationDivision, lead.organization_division_id)
            if div:
                org = db.session.get(Organization, div.organization_id)
                org_name = f"{org.name} - {div.name}" if org else div.name

        contact_name = lead.contact_person.name if lead.contact_person else "Unknown"
        trip_name = proposal.proposal_title

        # Sequence counter block retry loops
        year = datetime.now(timezone.utc).year
        booking_number = None
        booking = None

        try:
            for attempt in range(3):
                try:
                    booking_number = self._generate_booking_number(year)
                    booking = Booking(
                        booking_number=booking_number,
                        booking_type_id=b_type.id,
                        booking_source_id=b_source.id,
                        booking_status_id=b_status.id,
                        customer_id=customer.id,
                        lead_id=lead.id,
                        proposal_version_id=proposal.id,
                        contact_person_id=lead.contact_person_id,
                        booking_date=booking_date_val,
                        trip_start_date=lead.travel_start_date or booking_date_val,
                        trip_end_date=lead.travel_end_date or booking_date_val,
                        total_travelers=len(data["travelers"]),
                        total_amount=total_amount_val,
                        package_name_snapshot=package_name,
                        organization_name_snapshot=org_name,
                        contact_person_snapshot=contact_name,
                        trip_name_snapshot=trip_name,
                        group_name=data.get("group_name"),
                        booking_created_at=datetime.now(timezone.utc)
                    )
                    if context_team_member_id:
                        booking.created_by_team_member_id = context_team_member_id
                        booking.owner_team_member_id = context_team_member_id

                    db.session.add(booking)
                    db.session.flush()
                    break
                except IntegrityError as ie:
                    db.session.rollback()
                    if attempt == 2:
                        raise ie
            
            if not booking:
                raise BusinessException("Unable to allocate unique booking sequence code.", code="ERR_OPTIMISTIC_LOCK")

            # Create travelers manifest
            for t_data in data["travelers"]:
                t = Traveler(
                    booking_id=booking.id,
                    name=t_data["name"],
                    age=t_data.get("age"),
                    gender=t_data.get("gender"),
                    id_proof_type=t_data.get("id_proof_type"),
                    id_proof_number=t_data.get("id_proof_number"),
                    emergency_contact=t_data.get("emergency_contact"),
                    special_requirements=t_data.get("special_requirements"),
                    is_group_leader=t_data.get("is_group_leader", False)
                )
                db.session.add(t)

            # Create payment schedules
            stmt_unpaid = select(PaymentStatus).where(PaymentStatus.code == "UNPAID")
            pay_status = db.session.scalar(stmt_unpaid) or PaymentStatus(code="UNPAID", name="Unpaid", is_active=True)
            db.session.add(pay_status)
            db.session.flush()

            for inst_data in data["installments"]:
                pct = Decimal(str(inst_data["percentage"]))
                amount = (pct / Decimal("100.00")) * total_amount_val
                
                due_date_val = inst_data["due_date"]
                if isinstance(due_date_val, str):
                    due_date_val = datetime.strptime(due_date_val, "%Y-%m-%d").date()

                schedule = PaymentSchedule(
                    booking_id=booking.id,
                    installment_no=inst_data["installment_no"],
                    due_date=due_date_val,
                    percentage=pct,
                    amount=amount,
                    payment_status_id=pay_status.id,
                    remarks=inst_data.get("remarks")
                )
                db.session.add(schedule)

            # Log history status timeline
            hist = BookingStatusHistory(
                booking_id=booking.id,
                from_status_id=None,
                to_status_id=b_status.id,
                changed_by_team_member_id=context_team_member_id,
                notes="Booking created from finalized proposal."
            )
            db.session.add(hist)

            # Proposal lock transitions
            # (Lock is final proposal)
            proposal.status_id = db.session.scalar(
                select(ProposalStatus.id).where(ProposalStatus.code == "CONVERTED")
            ) or proposal.status_id
            db.session.add(proposal)

            self.commit()

        except Exception as e:
            db.session.rollback()
            raise e

        # Publish domain events strictly AFTER successful commit
        event_bus.publish(
            DomainEvent.BOOKING_CREATED,
            {
                "booking_id": str(booking.id),
                "booking_number": booking.booking_number,
                "proposal_id": str(proposal.id),
                "occurred_at": datetime.now(timezone.utc).isoformat()
            }
        )

        return booking

    def update_booking(
        self,
        booking_id: str | uuid.UUID,
        data: dict,
        context_team_member_id: str | uuid.UUID | None = None
    ) -> Booking:
        """
        Performs partial updates on top-level details.
        """
        booking = self.repository.get(booking_id)
        if not booking or booking.is_deleted:
            raise NotFoundException("Booking not found.")

        # Invariant 6: Closed/completed bookings are immutable
        if booking.status and booking.status.code in ["COMPLETED", "CLOSED"]:
            raise BusinessException("Completed or closed bookings cannot be modified.", code="ERR_BOOKING_IMMUTABLE")

        # Concurrency check
        expected_version = data.get("row_version")
        if expected_version is None or booking.row_version != expected_version:
            raise BusinessException(
                "Concurrent modification detected. Please refresh and try again.",
                code="ERR_OPTIMISTIC_LOCK"
            )

        if "group_name" in data:
            booking.group_name = data["group_name"]
        if "internal_notes" in data:
            booking.internal_notes = data["internal_notes"]

        booking.row_version += 1
        if context_team_member_id:
            booking.updated_by_team_member_id = context_team_member_id

        self.repository.update(booking)
        self.commit()

        return booking

    def confirm_booking(
        self,
        booking_id: str | uuid.UUID,
        data: dict,
        context_team_member_id: str | uuid.UUID | None = None
    ) -> Booking:
        """
        Confirmed booking operations. Assigns operational trip coordinator
        and triggers checklist events.
        """
        booking = self.repository.get(booking_id)
        if not booking or booking.is_deleted:
            raise NotFoundException("Booking not found.")

        # Concurrency check
        expected_version = data.get("row_version")
        if expected_version is None or booking.row_version != expected_version:
            raise BusinessException(
                "Concurrent modification detected. Please refresh and try again.",
                code="ERR_OPTIMISTIC_LOCK"
            )

        # Transition validation
        current_status_code = booking.status.code if booking.status else "WAITING_FOR_ADVANCE"
        allowed = BOOKING_TRANSITIONS.get(current_status_code, [])
        if "CONFIRMED" not in allowed:
            raise BusinessException(
                f"Invalid status transition from {current_status_code} to CONFIRMED.",
                code="ERR_INVALID_STATUS_TRANSITION"
            )

        # Coordinator validation
        coordinator_id = data.get("trip_coordinator_team_member_id")
        if not coordinator_id:
            raise ValidationException("trip_coordinator_team_member_id is required.", code="ERR_VALIDATION")

        coordinator = db.session.get(TeamMember, coordinator_id)
        if not coordinator or coordinator.is_deleted or not coordinator.is_active:
            raise ValidationException("Assigned trip coordinator is inactive or invalid.", code="ERR_VALIDATION")

        stmt_confirm = select(BookingStatus).where(BookingStatus.code == "CONFIRMED")
        confirm_status = db.session.scalar(stmt_confirm) or BookingStatus(code="CONFIRMED", name="Confirmed", is_active=True)
        db.session.add(confirm_status)
        db.session.flush()

        booking.booking_status_id = confirm_status.id
        booking.trip_coordinator_team_member_id = coordinator.id
        booking.confirmed_by_team_member_id = context_team_member_id or coordinator.id
        booking.confirmed_at = datetime.now(timezone.utc)
        booking.row_version += 1

        # Timeline status logging
        hist = BookingStatusHistory(
            booking_id=booking.id,
            from_status_id=booking.status.id if booking.status else None,
            to_status_id=confirm_status.id,
            changed_by_team_member_id=context_team_member_id,
            notes=data.get("notes", "Booking confirmed.")
        )
        db.session.add(hist)

        self.repository.update(booking)
        self.commit()

        # Publish Event AFTER commit
        event_bus.publish(
            DomainEvent.BOOKING_CONFIRMED,
            {
                "booking_id": str(booking.id),
                "booking_number": booking.booking_number,
                "confirmed_by": str(booking.confirmed_by_team_member_id),
                "occurred_at": datetime.now(timezone.utc).isoformat()
            }
        )

        return booking

    def cancel_booking(
        self,
        booking_id: str | uuid.UUID,
        data: dict,
        context_team_member_id: str | uuid.UUID | None = None
    ) -> Booking:
        """
        Cancels a booking and releases allocations.
        """
        booking = self.repository.get(booking_id)
        if not booking or booking.is_deleted:
            raise NotFoundException("Booking not found.")

        # Concurrency check
        expected_version = data.get("row_version")
        if expected_version is None or booking.row_version != expected_version:
            raise BusinessException(
                "Concurrent modification detected. Please refresh and try again.",
                code="ERR_OPTIMISTIC_LOCK"
            )

        current_status_code = booking.status.code if booking.status else "WAITING_FOR_ADVANCE"
        allowed = BOOKING_TRANSITIONS.get(current_status_code, [])
        if "CANCELLED" not in allowed:
            raise BusinessException(
                f"Cannot cancel a booking in {current_status_code} status.",
                code="ERR_INVALID_STATUS_TRANSITION"
            )

        reason = data.get("cancellation_reason")
        if not reason:
            raise ValidationException("Cancellation reason is required.", code="ERR_VALIDATION")

        stmt_cancel = select(BookingStatus).where(BookingStatus.code == "CANCELLED")
        cancel_status = db.session.scalar(stmt_cancel) or BookingStatus(code="CANCELLED", name="Cancelled", is_active=True)
        db.session.add(cancel_status)
        db.session.flush()

        booking.booking_status_id = cancel_status.id
        booking.cancelled_by_team_member_id = context_team_member_id
        booking.cancelled_at = datetime.now(timezone.utc)
        booking.cancellation_reason = reason
        booking.row_version += 1

        # Timeline status logging
        hist = BookingStatusHistory(
            booking_id=booking.id,
            from_status_id=booking.status.id if booking.status else None,
            to_status_id=cancel_status.id,
            changed_by_team_member_id=context_team_member_id,
            notes=f"Booking cancelled: {reason}"
        )
        db.session.add(hist)

        self.repository.update(booking)
        self.commit()

        # Publish Event AFTER commit
        event_bus.publish(
            DomainEvent.BOOKING_CANCELLED,
            {
                "booking_id": str(booking.id),
                "booking_number": booking.booking_number,
                "occurred_at": datetime.now(timezone.utc).isoformat()
            }
        )

        return booking

    # -----------------------------------------------------------------------
    # Nested Travelers Manifest Writing
    # -----------------------------------------------------------------------

    def add_traveler(
        self,
        booking_id: str | uuid.UUID,
        traveler_data: dict,
        context_team_member_id: str | uuid.UUID | None = None
    ) -> Traveler:
        """
        Appends traveler to booking manifest. Enforces lead traveler constraints.
        """
        booking = self.repository.get_details(booking_id)
        if not booking:
            raise NotFoundException("Booking not found.")

        if booking.status and booking.status.code in ["COMPLETED", "CLOSED"]:
            raise BusinessException("Booking is closed or completed.", code="ERR_BOOKING_IMMUTABLE")

        # Validate manifest invariants
        all_travelers = [{"is_group_leader": t.is_group_leader, "age": t.age} for t in booking.travelers]
        all_travelers.append({
            "is_group_leader": traveler_data.get("is_group_leader", False),
            "age": traveler_data.get("age")
        })
        self._validate_travelers(all_travelers)

        # ID proof Aadhaar format check
        id_type = traveler_data.get("id_proof_type")
        id_num = traveler_data.get("id_proof_number")
        if id_type == "Aadhaar" and id_num:
            import re
            if not re.match(r"^[0-9]{4}-[0-9]{4}-[0-9]{4}$", id_num):
                raise ValidationException("Aadhaar format is invalid. Expected XXXX-XXXX-XXXX.", code="ERR_VALIDATION")

        traveler = Traveler(
            booking_id=booking.id,
            name=traveler_data["name"],
            age=traveler_data.get("age"),
            gender=traveler_data.get("gender"),
            id_proof_type=id_type,
            id_proof_number=id_num,
            emergency_contact=traveler_data.get("emergency_contact"),
            special_requirements=traveler_data.get("special_requirements"),
            is_group_leader=traveler_data.get("is_group_leader", False)
        )
        
        booking.total_travelers += 1
        db.session.add(traveler)
        db.session.add(booking)
        self.commit()

        return traveler

    def update_traveler(
        self,
        booking_id: str | uuid.UUID,
        traveler_id: str | uuid.UUID,
        traveler_data: dict,
        context_team_member_id: str | uuid.UUID | None = None
    ) -> Traveler:
        """
        Modifies a traveler payload. Enforces manifest leadership.
        """
        booking = self.repository.get_details(booking_id)
        if not booking:
            raise NotFoundException("Booking not found.")

        if booking.status and booking.status.code in ["COMPLETED", "CLOSED"]:
            raise BusinessException("Booking is closed or completed.", code="ERR_BOOKING_IMMUTABLE")

        traveler = None
        for t in booking.travelers:
            if str(t.id) == str(traveler_id):
                traveler = t
                break

        if not traveler or traveler.is_deleted:
            raise NotFoundException("Traveler not found.")

        # Build list to validate lead traveler invariant
        all_travelers = []
        for t in booking.travelers:
            if str(t.id) == str(traveler_id):
                all_travelers.append({
                    "is_group_leader": traveler_data.get("is_group_leader", t.is_group_leader),
                    "age": traveler_data.get("age", t.age)
                })
            else:
                all_travelers.append({
                    "is_group_leader": t.is_group_leader,
                    "age": t.age
                })
        self._validate_travelers(all_travelers)

        # Update traveler values
        if "name" in traveler_data:
            traveler.name = traveler_data["name"]
        if "age" in traveler_data:
            traveler.age = traveler_data["age"]
        if "gender" in traveler_data:
            traveler.gender = traveler_data["gender"]
        if "id_proof_type" in traveler_data:
            traveler.id_proof_type = traveler_data["id_proof_type"]
        if "id_proof_number" in traveler_data:
            traveler.id_proof_number = traveler_data["id_proof_number"]
        if "emergency_contact" in traveler_data:
            traveler.emergency_contact = traveler_data["emergency_contact"]
        if "special_requirements" in traveler_data:
            traveler.special_requirements = traveler_data["special_requirements"]
        if "is_group_leader" in traveler_data:
            traveler.is_group_leader = traveler_data["is_group_leader"]

        db.session.add(traveler)
        self.commit()

        return traveler

    def delete_traveler(
        self,
        booking_id: str | uuid.UUID,
        traveler_id: str | uuid.UUID,
        context_team_member_id: str | uuid.UUID | None = None
    ) -> bool:
        """
        Logical delete of traveler. Guard: blocks lead traveler deletion.
        """
        booking = self.repository.get_details(booking_id)
        if not booking:
            raise NotFoundException("Booking not found.")

        if booking.status and booking.status.code in ["COMPLETED", "CLOSED"]:
            raise BusinessException("Booking is closed or completed.", code="ERR_BOOKING_IMMUTABLE")

        traveler = None
        for t in booking.travelers:
            if str(t.id) == str(traveler_id):
                traveler = t
                break

        if not traveler or traveler.is_deleted:
            raise NotFoundException("Traveler not found.")

        # Guard lead traveler reassignment requirement
        if traveler.is_group_leader:
            raise BusinessException(
                "Cannot delete the Lead Traveler. Leadership role must be reassigned first.",
                code="ERR_LEAD_TRAVELER_REQUIRED"
            )

        # Soft delete traveler
        traveler.is_deleted = True
        booking.total_travelers -= 1
        db.session.add(traveler)
        db.session.add(booking)
        self.commit()

        return True

    # -----------------------------------------------------------------------
    # Nested Document Attachments Writing
    # -----------------------------------------------------------------------

    def add_document(
        self,
        booking_id: str | uuid.UUID,
        document_data: dict,
        context_team_member_id: str | uuid.UUID | None = None
    ) -> Document:
        """
        Registers a document upload under a booking.
        """
        booking = self.repository.get(booking_id)
        if not booking or booking.is_deleted:
            raise NotFoundException("Booking not found.")

        if booking.status and booking.status.code in ["COMPLETED", "CLOSED"]:
            raise BusinessException("Booking is closed or completed.", code="ERR_BOOKING_IMMUTABLE")

        doc_type_code = document_data.get("document_type", "PASSPORT")
        stmt_dtype = select(DocumentType).where(DocumentType.code == doc_type_code)
        doc_type = db.session.scalar(stmt_dtype) or DocumentType(code=doc_type_code, name=doc_type_code.capitalize(), is_active=True)
        db.session.add(doc_type)
        db.session.flush()

        doc = Document(
            booking_id=booking.id,
            document_type_id=doc_type.id,
            file_name=document_data["file_name"],
            file_url=document_data["file_url"],
            storage_provider=document_data.get("storage_provider", "LOCAL"),
            storage_key=document_data.get("storage_key", "doc_storage_key")
        )
        db.session.add(doc)
        self.commit()

        return doc

    def delete_document(
        self,
        booking_id: str | uuid.UUID,
        document_id: str | uuid.UUID,
        context_team_member_id: str | uuid.UUID | None = None
    ) -> bool:
        """
        Deletes a document attachment resource.
        """
        booking = self.repository.get(booking_id)
        if not booking or booking.is_deleted:
            raise NotFoundException("Booking not found.")

        if booking.status and booking.status.code in ["COMPLETED", "CLOSED"]:
            raise BusinessException("Booking is closed or completed.", code="ERR_BOOKING_IMMUTABLE")

        doc = db.session.get(Document, document_id)
        if not doc or str(doc.booking_id) != str(booking.id):
            raise NotFoundException("Document not found.")

        db.session.delete(doc)
        self.commit()
        return True


class BookingLookupService(BaseService):
    """
    Exposes lookup data collections owned by Master Module.
    """

    def get_booking_statuses(self) -> list[BookingStatus]:
        return list(db.session.scalars(select(BookingStatus).where(BookingStatus.is_active == True)).all())

    def get_booking_sources(self) -> list[BookingSource]:
        return list(db.session.scalars(select(BookingSource).where(BookingSource.is_active == True)).all())

    def get_booking_types(self) -> list[BookingType]:
        return list(db.session.scalars(select(BookingType).where(BookingType.is_active == True)).all())
