import uuid
import re
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import select, func, extract
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.core.base_service import BaseService
from app.domain.exceptions import NotFoundException, ValidationException, BusinessException
from app.domain.events import DomainEvent
from app.workflow.engine import event_bus
from app.core.extensions import db
from app.models import (
    Lead,
    LeadDestination,
    CRMActivity,
    FollowUp,
    AssignmentHistory,
    ContactPerson,
    Customer,
    Booking,
    Task,
    LeadStatus,
    LeadSource,
    LeadPriority,
    TripType,
    LeadLostReason,
    BookingType,
    BookingSource,
    BookingStatus,
    TaskStatus,
    TaskPriority,
    Destination,
    TeamMember,
    Role,
    Package,
    CRMActivityType,
    FollowUpType
)
from .repository import (
    ContactPersonRepository,
    LeadRepository,
    CRMActivityRepository,
    FollowUpRepository,
    AssignmentHistoryRepository,
)


class ContactService(BaseService):
    """
    Service handling business logic for ContactPerson aggregate.
    """
    def __init__(self):
        self.repository = ContactPersonRepository()

    def list_contacts(self, page=1, page_size=20, search_query=None):
        return self.repository.paginate_contacts(page=page, page_size=page_size, search_query=search_query)

    def get_contact_by_id(self, contact_id: str | uuid.UUID) -> ContactPerson:
        """
        Retrieve an active contact person by ID, or raise NotFoundException.
        """
        try:
            uid = uuid.UUID(str(contact_id)) if isinstance(contact_id, str) else contact_id
        except ValueError:
            raise ValidationException("Invalid UUID format for contact_id.")
        
        contact = self.repository.get(uid)
        if not contact or contact.is_deleted or not contact.is_active:
            raise NotFoundException("Contact person not found.")
        return contact

    def create_or_get_contact(self, data: dict) -> ContactPerson:
        """
        Links to an existing contact by phone (if found) or creates a new ContactPerson.
        Only fills in missing profile values (does NOT overwrite existing ones).
        """
        phone = data.get("phone")
        if not phone:
            raise ValidationException("Phone number is required to create or resolve a contact.")
            
        existing = self.repository.find_by_phone(phone)
        if existing:
            # Fill missing profile values only
            updated = False
            for field in ["email", "designation", "alternate_phone", "preferred_contact_method", "notes"]:
                val = data.get(field)
                if val and not getattr(existing, field):
                    setattr(existing, field, val)
                    updated = True
            if updated:
                self.repository.update(existing)
                self.commit()
            return existing

        # Create new ContactPerson
        contact = ContactPerson(
            name=data["name"],
            phone=phone,
            email=data.get("email"),
            designation=data.get("designation"),
            alternate_phone=data.get("alternate_phone"),
            preferred_contact_method=data.get("preferred_contact_method"),
            notes=data.get("notes"),
            is_primary=data.get("is_primary", False),
            organization_id=data.get("organization_id"),
            is_active=True
        )
        self.repository.add(contact)
        self.commit()
        return contact

    def update_contact(self, contact_id: str | uuid.UUID, data: dict) -> ContactPerson:
        """
        Directly updates contact person details.
        """
        contact = self.get_contact_by_id(contact_id)
        
        for field in ["name", "phone", "email", "designation", "alternate_phone", "preferred_contact_method", "notes", "is_primary", "organization_id"]:
            if field in data:
                setattr(contact, field, data[field])
        
        self.repository.update(contact)
        self.commit()
        return contact


class CRMService(BaseService):
    """
    Service handling business logic and lifecycle for Lead aggregate.
    """
    STATUS_TRANSITION_MATRIX = {
        "NEW": ["ASSIGNED", "CONTACTED", "LOST"],
        "ASSIGNED": ["CONTACTED", "LOST"],
        "CONTACTED": ["REQUIREMENT_GATHERING", "LOST"],
        "REQUIREMENT_GATHERING": ["PROPOSAL_SENT", "LOST"],
        "PROPOSAL_SENT": ["NEGOTIATION", "WON", "LOST"],
        "NEGOTIATION": ["WON", "LOST"],
        "WON": [],
        "LOST": []
    }

    def __init__(self):
        self.repository = LeadRepository()
        self.contact_repo = ContactPersonRepository()
        self.assign_repo = AssignmentHistoryRepository()
        self.contact_service = ContactService()

    def get_lead_by_id(self, lead_id: str | uuid.UUID) -> Lead:
        """
        Get a specific active lead by ID, or raise NotFoundException.
        """
        try:
            uid = uuid.UUID(str(lead_id)) if isinstance(lead_id, str) else lead_id
        except ValueError:
            raise ValidationException("Invalid UUID format for lead_id.")
        
        # Load lead with joined loads to prevent N+1 query issues
        stmt = select(Lead).where(
            Lead.id == uid,
            Lead.is_deleted == False
        ).options(
            joinedload(Lead.contact_person),
            joinedload(Lead.current_status),
            joinedload(Lead.lead_source),
            joinedload(Lead.priority),
            joinedload(Lead.trip_type),
            joinedload(Lead.lost_reason),
            joinedload(Lead.package),
            joinedload(Lead.lead_destinations).joinedload(LeadDestination.destination)
        )
        lead = db.session.scalar(stmt)
        if not lead:
            raise NotFoundException("Lead not found.")
        return lead

    def _resolve_status(self, code: str) -> LeadStatus:
        """Helper to find or create a status lookup by code."""
        status = db.session.execute(select(LeadStatus).where(func.upper(LeadStatus.code) == code.upper())).scalars().first()
        if not status:
            status = LeadStatus(code=code.upper(), name=code.capitalize(), is_active=True)
            db.session.add(status)
            db.session.flush()
        return status

    def _resolve_auto_operations_owner(self) -> uuid.UUID | None:
        """
        Least-loaded Round-Robin Auto-Assignment Strategy:
        Finds active and available TeamMembers holding the OPERATIONS role,
        counts their current active leads, and selects the member with the lowest workload.
        """
        stmt_ops = (
            select(TeamMember)
            .join(Role, TeamMember.role_id == Role.id)
            .where(
                TeamMember.is_active == True,
                TeamMember.is_deleted == False,
                (func.upper(Role.code).like("%OPERATIONS%") | func.upper(Role.code).like("%OP%"))
            )
        )
        ops_members = list(db.session.scalars(stmt_ops).all())
        if not ops_members:
            return None

        closed_status_stmt = select(LeadStatus.id).where(
            func.upper(LeadStatus.code).in_(["WON", "LOST"])
        )
        closed_status_ids = set(db.session.scalars(closed_status_stmt).all())

        member_workload = []
        for member in ops_members:
            lead_count_stmt = select(func.count(Lead.id)).where(
                Lead.owner_team_member_id == member.id,
                Lead.is_deleted == False,
                ~Lead.current_status_id.in_(closed_status_ids) if closed_status_ids else True
            )
            count = db.session.scalar(lead_count_stmt) or 0
            member_workload.append((count, member.id))

        member_workload.sort(key=lambda x: x[0])
        return member_workload[0][1]

    def create_lead(self, data: dict, context_team_member_id: str | uuid.UUID | None = None) -> Lead:
        """
        Create a new Lead within a single database transaction boundary.
        Implements concurrency retries for generating lead numbers.
        """
        # Resolve Contact Person (creates new if not found, reuses existing if matched)
        if data.get("contact_person_id"):
            contact = self.contact_service.get_contact_by_id(data["contact_person_id"])
        else:
            contact = self.contact_service.create_or_get_contact(data["contact_person"])

        # Determine owner and status (auto-assign unassigned leads to Operations role)
        owner_id = data.get("owner_team_member_id")
        is_auto_assigned = False
        if not owner_id:
            owner_id = self._resolve_auto_operations_owner()
            if owner_id:
                is_auto_assigned = True

        if data.get("current_status_id"):
            status_id = data["current_status_id"]
        else:
            # Default status code: ASSIGNED if owner is passed, else NEW
            status_code = "ASSIGNED" if owner_id else "NEW"
            status_obj = self._resolve_status(status_code)
            status_id = status_obj.id

        # Safely parse UUID strings into uuid.UUID objects
        def _to_uuid(val):
            if not val:
                return None
            return uuid.UUID(str(val)) if isinstance(val, str) else val

        lead_source_id = _to_uuid(data.get("lead_source_id"))
        trip_type_id = _to_uuid(data.get("trip_type_id"))
        priority_id = _to_uuid(data.get("priority_id"))
        package_id = _to_uuid(data.get("package_id"))
        org_division_id = _to_uuid(data.get("organization_division_id"))
        owner_id = _to_uuid(owner_id)

        # Validate lookups exist
        if lead_source_id and not db.session.get(LeadSource, lead_source_id):
            raise ValidationException("Invalid lead_source_id.")
        if trip_type_id and not db.session.get(TripType, trip_type_id):
            raise ValidationException("Invalid trip_type_id.")
        if priority_id and not db.session.get(LeadPriority, priority_id):
            raise ValidationException("Invalid priority_id.")
        if package_id and not db.session.get(Package, package_id):
            raise ValidationException("Invalid package_id.")

        # Create Lead Instance
        lead = Lead(
            contact_person_id=contact.id,
            lead_source_id=lead_source_id,
            organization_division_id=org_division_id,
            package_id=package_id,
            trip_type_id=trip_type_id,
            priority_id=priority_id,
            travel_start_date=data.get("travel_start_date"),
            travel_end_date=data.get("travel_end_date"),
            estimated_trip_days=data.get("estimated_trip_days"),
            estimated_trip_nights=data.get("estimated_trip_nights"),
            traveler_count=data.get("traveler_count", 1),
            male_count=data.get("male_count"),
            female_count=data.get("female_count"),
            faculty_count=data.get("faculty_count"),
            budget=data.get("budget"),
            notes=data.get("notes"),
            current_status_id=status_id,
            expected_travel_date=data.get("expected_travel_date"),
            owner_team_member_id=owner_id,
            version=1,
            is_deleted=False
        )

        if context_team_member_id:
            lead.created_by_team_member_id = context_team_member_id
            lead.updated_by_team_member_id = context_team_member_id

        # Sync destinations
        if "destinations" in data:
            self._sync_lead_destinations(lead, data["destinations"])

        # Generate next guaranteed unique lead number
        year = datetime.now(timezone.utc).year
        lead.lead_number = self.repository.generate_next_lead_number(year)

        db.session.add(lead)
        db.session.flush()

        # Log initial assignment history if owner was assigned
        if owner_id:
            initial_status_obj = db.session.get(LeadStatus, status_id)
            status_name = initial_status_obj.name if initial_status_obj else "Assigned"
            hist_reason = (
                "Automated Round-Robin Allocation to Operations Team"
                if is_auto_assigned
                else "Initial manual allocation upon intake"
            )
            hist = AssignmentHistory(
                entity_type="Lead",
                entity_id=lead.id,
                assignment_type="Lead Owner",
                new_team_member_id=owner_id,
                effective_from=datetime.now(timezone.utc),
                entity_status=status_name,
                reason=hist_reason
            )
            db.session.add(hist)

        self.commit()

        # Publish Events Post-Commit
        event_bus.publish(
            DomainEvent.LEAD_CREATED,
            {
                "lead_id": str(lead.id),
                "lead_number": lead.lead_number,
                "contact_person_id": str(contact.id),
                "status": "NEW" if not owner_id else "ASSIGNED",
                "occurred_at": datetime.now(timezone.utc).isoformat()
            }
        )
        if owner_id:
            event_bus.publish(
                DomainEvent.LEAD_ASSIGNED,
                {
                    "lead_id": str(lead.id),
                    "previous_team_member_id": "00000000-0000-0000-0000-000000000000",
                    "new_team_member_id": str(owner_id),
                    "reason": "Initial manual allocation upon intake",
                    "occurred_at": datetime.now(timezone.utc).isoformat()
                }
            )

        return lead

    def update_lead(
        self,
        lead_id: str | uuid.UUID,
        data: dict,
        expected_version: int,
        context_team_member_id: str | uuid.UUID | None = None
    ) -> Lead:
        """
        Update Lead details, validating optimistic lock version and status transition logic.
        Executes within a single transaction boundary.
        """
        lead = self.get_lead_by_id(lead_id)

        # Optimistic Locking Check
        if lead.version != expected_version:
            raise BusinessException(
                "Record has been modified by another user.",
                code="ERR_OPTIMISTIC_LOCK"
            )

        # Status transition matrix verification
        status_changed = False
        old_status_code = None
        new_status_code = None
        if "current_status_id" in data and data["current_status_id"]:
            new_status_id = data["current_status_id"]
            if new_status_id != lead.current_status_id:
                old_status = db.session.get(LeadStatus, lead.current_status_id)
                new_status = db.session.get(LeadStatus, new_status_id)
                if not new_status:
                    raise ValidationException("Invalid current_status_id lookup.")
                
                old_status_code = old_status.code if old_status else "NEW"
                new_status_code = new_status.code
                
                # Check status transition validity
                allowed = self.STATUS_TRANSITION_MATRIX.get(old_status_code, [])
                if new_status_code not in allowed:
                    raise BusinessException(
                        f"Status transition from {old_status_code} to {new_status_code} is not allowed.",
                        code="ERR_INVALID_STATUS_TRANSITION"
                    )

                # Validate Lost Reasons if transitioning to LOST
                if new_status_code == "LOST":
                    if not data.get("lost_reason_id") or not data.get("lost_date"):
                        raise ValidationException("lost_reason_id and lost_date are required when status is LOST.")
                    if not db.session.get(LeadLostReason, data["lost_reason_id"]):
                        raise ValidationException("Invalid lost_reason_id.")
                    lead.lost_reason_id = data["lost_reason_id"]
                    lead.lost_date = data["lost_date"]

                lead.current_status_id = new_status_id
                status_changed = True

        # Ownership assignment history change logging
        owner_changed = False
        prev_owner_id = None
        new_owner_id = None
        if "owner_team_member_id" in data:
            new_owner_id = data["owner_team_member_id"]
            if new_owner_id != lead.owner_team_member_id:
                prev_owner_id = lead.owner_team_member_id
                
                # Verify new owner exists if not None
                if new_owner_id and not db.session.get(TeamMember, new_owner_id):
                    raise ValidationException("Invalid owner_team_member_id.")
                
                # Close previous active assignment row
                active_assign = self.assign_repo.get_active_assignment(lead.id)
                now = datetime.now(timezone.utc)
                if active_assign:
                    active_assign.effective_to = now
                    self.assign_repo.update(active_assign)

                # Insert new assignment row
                status_obj = db.session.get(LeadStatus, lead.current_status_id)
                status_name = status_obj.name if status_obj else "Assigned"
                hist = AssignmentHistory(
                    entity_type="Lead",
                    entity_id=lead.id,
                    assignment_type="Lead Owner",
                    previous_team_member_id=prev_owner_id,
                    new_team_member_id=new_owner_id,
                    effective_from=now,
                    entity_status=status_name,
                    reason=data.get("assignment_reason", "Re-assigned by administrator")
                )
                db.session.add(hist)
                
                lead.owner_team_member_id = new_owner_id
                owner_changed = True

        # Sync destinations (full replacement)
        if "destinations" in data:
            self._sync_lead_destinations(lead, data["destinations"])

        # Update remaining details
        for field in [
            "contact_person_id", "lead_source_id", "organization_division_id",
            "package_id", "trip_type_id", "priority_id", "travel_start_date",
            "travel_end_date", "estimated_trip_days", "estimated_trip_nights",
            "traveler_count", "male_count", "female_count", "faculty_count",
            "budget", "notes", "expected_travel_date"
        ]:
            if field in data:
                setattr(lead, field, data[field])

        # Increment Version
        lead.version += 1
        if context_team_member_id:
            lead.updated_by_team_member_id = context_team_member_id

        self.repository.update(lead)
        self.commit()

        # Publish Events Post-Commit
        event_bus.publish(
            DomainEvent.LEAD_UPDATED,
            {
                "lead_id": str(lead.id),
                "version": lead.version,
                "occurred_at": datetime.now(timezone.utc).isoformat()
            }
        )
        if status_changed:
            event_bus.publish(
                DomainEvent.LEAD_STATUS_CHANGED,
                {
                    "lead_id": str(lead.id),
                    "previous_status": old_status_code,
                    "new_status": new_status_code,
                    "occurred_at": datetime.now(timezone.utc).isoformat()
                }
            )
        if owner_changed:
            event_bus.publish(
                DomainEvent.LEAD_ASSIGNED,
                {
                    "lead_id": str(lead.id),
                    "previous_team_member_id": str(prev_owner_id) if prev_owner_id else "00000000-0000-0000-0000-000000000000",
                    "new_team_member_id": str(new_owner_id) if new_owner_id else "00000000-0000-0000-0000-000000000000",
                    "reason": data.get("assignment_reason", "Re-assigned by administrator"),
                    "occurred_at": datetime.now(timezone.utc).isoformat()
                }
            )

        return lead

    def soft_delete_lead(self, lead_id: str | uuid.UUID, context_team_member_id: str | uuid.UUID | None = None) -> bool:
        """
        Logical soft delete. Cancels all pending followups and closes owner assignment.
        """
        lead = self.get_lead_by_id(lead_id)
        
        now = datetime.now(timezone.utc)
        lead.is_deleted = True
        if context_team_member_id:
            lead.updated_by_team_member_id = context_team_member_id
        
        # Close owner assignment log
        active_assign = self.assign_repo.get_active_assignment(lead.id)
        if active_assign:
            active_assign.effective_to = now
            self.assign_repo.update(active_assign)

        # Cancel all pending followups
        stmt = select(FollowUp).where(
            FollowUp.lead_id == lead.id,
            FollowUp.is_completed == False,
            FollowUp.is_deleted == False
        )
        followups = db.session.scalars(stmt).all()
        for f in followups:
            f.is_deleted = True
            if context_team_member_id:
                f.updated_by_team_member_id = context_team_member_id
            db.session.add(f)

        self.repository.update(lead)
        self.commit()
        return True

    def _sync_lead_destinations(self, lead: Lead, destinations_data: list[dict]):
        """Helper to replace destinations in aggregate transaction."""
        # Validate destinations first
        input_ids = []
        for item in destinations_data:
            dest_id = item["destination_id"]
            if not db.session.get(Destination, dest_id):
                raise ValidationException(f"Destination with ID {dest_id} does not exist.")
            if dest_id in input_ids:
                raise ValidationException("Duplicate destinations not allowed in lead payload.")
            input_ids.append(dest_id)

        # SQLite/Postgres full replacement
        lead.lead_destinations.clear()
        for item in destinations_data:
            ld = LeadDestination(
                destination_id=item["destination_id"],
                priority=item.get("priority"),
                day_preference=item.get("day_preference")
            )
            lead.lead_destinations.append(ld)

    def convert_lead_to_booking(
        self,
        lead_id: str | uuid.UUID,
        data: dict,
        context_team_member_id: str | uuid.UUID | None = None
    ) -> Booking:
        """
        Convert Lead to Booking by delegating to BookingService.
        """
        lead = self.get_lead_by_id(lead_id)

        # Check status transition to WON
        won_status = self._resolve_status("WON")
        if lead.current_status_id != won_status.id:
            # We enforce transition to WON
            self.update_lead(
                lead.id,
                {"current_status_id": won_status.id, "version": lead.version},
                expected_version=lead.version,
                context_team_member_id=context_team_member_id
            )

        # Retrieve or auto-create finalized Proposal for this lead (for backward/test compatibility)
        from app.models import Proposal, ProposalStatus
        stmt_prop = select(Proposal).where(Proposal.lead_id == lead.id, Proposal.is_final == True)
        proposal = db.session.scalar(stmt_prop)

        if not proposal:
            stmt_pstatus = select(ProposalStatus).where(ProposalStatus.code == "WAITING_FOR_ADVANCE")
            p_status = db.session.scalar(stmt_pstatus) or ProposalStatus(code="WAITING_FOR_ADVANCE", name="Waiting for Advance", is_active=True)
            db.session.add(p_status)
            db.session.flush()

            proposal = Proposal(
                lead_id=lead.id,
                version=1,
                proposal_title="Auto-generated Proposal for Conversion",
                price_per_person=lead.budget or Decimal("10000.00"),
                total_amount=lead.budget or Decimal("10000.00"),
                is_final=True,
                status_id=p_status.id
            )
            db.session.add(proposal)
            db.session.flush()

        # Determine booking source based on lead origin
        lead_source_code = lead.lead_source.code if lead.lead_source else None
        is_public_form = (
            lead_source_code in ["TRIP_REQUEST", "WEBSITE"] or 
            not lead.created_by_team_member_id
        )
        booking_source_code = "WEBSITE" if is_public_form else "ADMIN"

        # Build travelers and installments data if not provided in payload
        booking_data = {
            "proposal_id": str(proposal.id),
            "group_name": data.get("group_name") or f"BK-{lead.lead_number}",
            "trip_start_date": data.get("trip_start_date"),
            "trip_end_date": data.get("trip_end_date"),
            "total_amount": data.get("total_amount"),
            "booking_source_code": booking_source_code,
            "booking_type_id": data.get("booking_type_id"),
            "travelers": data.get("travelers") or [
                {
                    "name": lead.contact_person.name if lead.contact_person else "Guest Traveler",
                    "age": 30,
                    "gender": "Male",
                    "is_group_leader": True
                }
            ],
            "installments": data.get("installments") or [
                {
                    "installment_no": 1,
                    "percentage": 100.00,
                    "due_date": datetime.now(timezone.utc).date().isoformat(),
                    "remarks": "Single payment"
                }
            ]
        }

        # Delegate to BookingService
        from app.modules.booking.service import BookingService
        booking_service = BookingService()
        booking = booking_service.create_booking(booking_data, context_team_member_id)

        # Create Task Record for Booking
        from app.models import TaskStatus, TaskPriority, Task
        t_status = db.session.execute(select(TaskStatus)).scalars().first()
        if not t_status:
            t_status = TaskStatus(code="PENDING", name="Pending", is_active=True)
            db.session.add(t_status)
            db.session.flush()

        t_priority = db.session.execute(select(TaskPriority)).scalars().first()
        if not t_priority:
            t_priority = TaskPriority(code="MEDIUM", name="Medium", is_active=True)
            db.session.add(t_priority)
            db.session.flush()

        task = Task(
            booking_id=booking.id,
            lead_id=lead.id,
            title=f"Review Booking BK-{lead.lead_number}",
            description="CRM conversion automated review check.",
            task_status_id=t_status.id,
            priority_id=t_priority.id,
            assigned_to_team_member_id=lead.owner_team_member_id or context_team_member_id or uuid.uuid4()
        )
        db.session.add(task)
        db.session.flush()

        # Publish Event
        event_bus.publish(
            DomainEvent.LEAD_CONVERTED,
            {
                "lead_id": str(lead.id),
                "booking_id": str(booking.id),
                "customer_id": str(booking.customer_id),
                "occurred_at": datetime.now(timezone.utc).isoformat()
            }
        )

        return booking


class CRMActivityService(BaseService):
    """
    Service handling business logic for CRMActivity.
    """
    def __init__(self):
        self.repository = CRMActivityRepository()

    def get_activities_by_lead(self, lead_id: str | uuid.UUID) -> list[CRMActivity]:
        """Fetch all activities logged for a lead, sorted by date descending."""
        try:
            uid = uuid.UUID(str(lead_id)) if isinstance(lead_id, str) else lead_id
        except ValueError:
            raise ValidationException("Invalid UUID format.")
            
        stmt = select(CRMActivity).where(
            CRMActivity.lead_id == uid
        ).options(
            joinedload(CRMActivity.lead)
        ).order_by(CRMActivity.activity_date.desc())
        return list(db.session.scalars(stmt).all())

    def _resolve_activity_type(self, type_id_or_code: str) -> CRMActivityType:
        from app.models import CRMActivityType
        try:
            val = uuid.UUID(type_id_or_code)
            type_obj = db.session.get(CRMActivityType, val)
            if not type_obj:
                raise NotFoundException("Activity type not found.")
            return type_obj
        except ValueError:
            code = type_id_or_code.upper()
            type_obj = db.session.execute(select(CRMActivityType).where(func.upper(CRMActivityType.code) == code)).scalars().first()
            if not type_obj:
                type_obj = CRMActivityType(code=code, name=code.replace("_", " ").title(), is_active=True)
                db.session.add(type_obj)
                db.session.commit()
            return type_obj

    def log_activity(self, lead_id: str | uuid.UUID, data: dict, context_team_member_id: str | uuid.UUID | None = None) -> CRMActivity:
        """Log a new activity discussion on a lead in a single transaction."""
        from app.models import CRMActivity
        try:
            uid = uuid.UUID(str(lead_id)) if isinstance(lead_id, str) else lead_id
        except ValueError:
            raise ValidationException("Invalid UUID format.")

        lead = db.session.get(Lead, uid)
        if not lead or lead.is_deleted:
            raise NotFoundException("Lead not found.")

        # Auto-advance lead status to CONTACTED if it is currently NEW or ASSIGNED
        if lead.current_status_id:
            current_status = db.session.get(LeadStatus, lead.current_status_id)
            if current_status and current_status.code in ("NEW", "ASSIGNED"):
                contacted_status = db.session.execute(
                    select(LeadStatus).where(func.upper(LeadStatus.code) == "CONTACTED")
                ).scalars().first()
                if contacted_status:
                    lead.current_status_id = contacted_status.id
                    lead.version += 1

        type_obj = self._resolve_activity_type(data["activity_type_id"])

        activity = CRMActivity(
            lead_id=uid,
            activity_type_id=type_obj.id,
            activity_date=data.get("activity_date", datetime.now(timezone.utc)),
            discussion_summary=data["discussion_summary"],
            outcome=data.get("outcome"),
            next_action=data.get("next_action"),
            next_followup_date=data.get("next_followup_date")
        )
        if context_team_member_id:
            activity.created_by_team_member_id = context_team_member_id

        self.repository.add(activity)
        self.commit()

        # Publish post-commit
        event_bus.publish(
            DomainEvent.ACTIVITY_CREATED,
            {
                "lead_id": str(uid),
                "activity_id": str(activity.id),
                "occurred_at": datetime.now(timezone.utc).isoformat()
            }
        )

        return activity


class FollowUpService(BaseService):
    """
    Service handling business logic for FollowUp scheduling and lifecycles.
    """
    def __init__(self):
        self.repository = FollowUpRepository()

    def get_followups_by_lead(self, lead_id: str | uuid.UUID) -> list[FollowUp]:
        """Fetch all follow-ups scheduled for a lead."""
        try:
            uid = uuid.UUID(str(lead_id)) if isinstance(lead_id, str) else lead_id
        except ValueError:
            raise ValidationException("Invalid UUID format.")
            
        stmt = select(FollowUp).where(
            FollowUp.lead_id == uid,
            FollowUp.is_deleted == False
        ).order_by(FollowUp.scheduled_date.asc())
        return list(db.session.scalars(stmt).all())

    def _resolve_followup_type(self, type_id_or_code: str) -> FollowUpType:
        from app.models import FollowUpType
        try:
            val = uuid.UUID(type_id_or_code)
            type_obj = db.session.get(FollowUpType, val)
            if not type_obj:
                raise NotFoundException("Follow up type not found.")
            return type_obj
        except ValueError:
            code = type_id_or_code.upper()
            type_obj = db.session.execute(select(FollowUpType).where(func.upper(FollowUpType.code) == code)).scalars().first()
            if not type_obj:
                type_obj = FollowUpType(code=code, name=code.replace("_", " ").title(), is_active=True)
                db.session.add(type_obj)
                db.session.commit()
            return type_obj

    def schedule_followup(self, lead_id: str | uuid.UUID, data: dict, context_team_member_id: str | uuid.UUID | None = None) -> FollowUp:
        """Schedule a new followup reminder task."""
        from app.models import FollowUp
        try:
            uid = uuid.UUID(str(lead_id)) if isinstance(lead_id, str) else lead_id
        except ValueError:
            raise ValidationException("Invalid UUID format.")

        lead = db.session.get(Lead, uid)
        if not lead or lead.is_deleted:
            raise NotFoundException("Lead not found.")

        # Ensure scheduled date is in the future
        sched = data["scheduled_date"]
        # Convert to offset-aware if naive, using timezone.utc
        if sched.tzinfo is None:
            sched = sched.replace(tzinfo=timezone.utc)
        if sched < datetime.now(timezone.utc):
            raise ValidationException("Followup scheduled date must be in the future.")

        owner_id = data.get("owner_team_member_id") or context_team_member_id or lead.owner_team_member_id
        if not owner_id:
            raise ValidationException("Followup must have an assigned owner.")

        type_obj = self._resolve_followup_type(data["followup_type_id"])

        followup = FollowUp(
            lead_id=uid,
            followup_type_id=type_obj.id,
            scheduled_date=sched,
            notes=data.get("notes"),
            is_completed=False,
            owner_team_member_id=owner_id,
            is_deleted=False
        )
        if context_team_member_id:
            followup.created_by_team_member_id = context_team_member_id

        self.repository.add(followup)
        self.commit()

        # Publish post-commit
        event_bus.publish(
            DomainEvent.FOLLOWUP_CREATED,
            {
                "lead_id": str(uid),
                "followup_id": str(followup.id),
                "occurred_at": datetime.now(timezone.utc).isoformat()
            }
        )

        return followup

    def complete_followup(self, lead_id: str | uuid.UUID, followup_id: str | uuid.UUID, data: dict, context_team_member_id: str | uuid.UUID | None = None) -> FollowUp:
        """Mark a followup reminder task as completed."""
        try:
            f_uid = uuid.UUID(str(followup_id)) if isinstance(followup_id, str) else followup_id
        except ValueError:
            raise ValidationException("Invalid UUID format.")

        followup = self.repository.get(f_uid)
        if not followup or followup.is_deleted or str(followup.lead_id) != str(lead_id):
            raise NotFoundException("Follow-up not found for this lead.")

        if followup.is_completed:
            raise BusinessException("Followup is already completed.", code="ERR_BAD_REQUEST")

        followup.is_completed = True
        followup.completed_at = datetime.now(timezone.utc)
        comp_notes = data.get("completion_notes") or data.get("notes")
        if comp_notes:
            # Append completion notes
            followup.notes = f"{followup.notes or ''}\n[Completed Notes]: {comp_notes}".strip()

        if context_team_member_id:
            followup.updated_by_team_member_id = context_team_member_id

        # Auto-advance lead status to CONTACTED if it is currently NEW or ASSIGNED
        lead = db.session.get(Lead, followup.lead_id)
        if lead and lead.current_status_id:
            current_status = db.session.get(LeadStatus, lead.current_status_id)
            if current_status and current_status.code in ("NEW", "ASSIGNED"):
                contacted_status = db.session.execute(
                    select(LeadStatus).where(func.upper(LeadStatus.code) == "CONTACTED")
                ).scalars().first()
                if contacted_status:
                    lead.current_status_id = contacted_status.id
                    lead.version += 1

        self.repository.update(followup)
        self.commit()

        # Publish post-commit
        event_bus.publish(
            DomainEvent.FOLLOWUP_COMPLETED,
            {
                "lead_id": str(lead_id),
                "followup_id": str(followup.id),
                "occurred_at": datetime.now(timezone.utc).isoformat()
            }
        )

        return followup


class CRMLookupService(BaseService):
    """
    Consolidated query service for all CRM lookup models.
    """
    def list_lookups(self, lookup_type: str) -> list:
        """Fetch all lookup selection options for dropdowns, auto-seeding defaults if missing."""
        mapping = {
            "statuses": (LeadStatus, [
                ("NEW", "New"),
                ("ASSIGNED", "Assigned"),
                ("CONTACTED", "Contacted"),
                ("REQUIREMENT_GATHERING", "Intake"),
                ("PROPOSAL_SENT", "Proposal"),
                ("NEGOTIATION", "Negotiation"),
                ("WON", "Won"),
                ("LOST", "Lost")
            ]),
            "sources": (LeadSource, [
                ("TRIP_REQUEST", "Trip Request"),
                ("WEBSITE", "Website Intake"),
                ("INSTAGRAM", "Instagram Direct"),
                ("FACEBOOK", "Facebook Ad"),
                ("REFERRAL", "Customer Referral"),
                ("WALK_IN", "Walk-in Desk")
            ]),
            "priorities": (LeadPriority, [
                ("LOW", "Low"),
                ("MEDIUM", "Medium"),
                ("HIGH", "High"),
                ("URGENT", "Urgent")
            ]),
            "lost_reasons": (LeadLostReason, [
                ("PRICE_HIGH", "Price too high"),
                ("COMPETITOR", "Chosen competitor"),
                ("CANCELLED", "Trip cancelled by client"),
                ("NO_RESPONSE", "Client unreachable / unresponsive")
            ]),
            "activity_types": (CRMActivityType, [
                ("CALL", "Phone Call"),
                ("EMAIL", "Email Exchange"),
                ("MEETING", "In-person Meeting"),
                ("WHATSAPP", "WhatsApp Chat"),
                ("SITE_VISIT", "Site Visit"),
                ("NOTE", "Internal Note")
            ]),
            "followup_types": (FollowUpType, [
                ("CALL", "Phone Call"),
                ("EMAIL", "Email"),
                ("MEETING", "Meeting"),
                ("WHATSAPP", "WhatsApp")
            ]),
            "trip_types": (TripType, [
                ("COUPLE", "Couple / Honeymoon"),
                ("FAMILY", "Family"),
                ("FRIENDS", "Friends Group"),
                ("COLLEGE_IV", "College Industrial Visit (IV)"),
                ("SCHOOL_TOUR", "School Tour"),
                ("CORPORATE", "Corporate Tour"),
                ("CLUB_TOUR", "Association / Club Tour"),
                ("CUSTOM_GROUP", "Custom Group Tour"),
                ("INDIVIDUAL", "Individual Traveler")
            ]),
        }

        entry = mapping.get(lookup_type.lower())
        if not entry:
            raise NotFoundException(f"Lookup type '{lookup_type}' is not supported.")

        model, defaults = entry
        stmt = select(model).where(model.is_active == True)
        records = list(db.session.scalars(stmt).all())

        # Auto-seed defaults if missing
        existing_codes = {r.code.upper() for r in records if hasattr(r, "code") and r.code}
        needed = [d for d in defaults if d[0] not in existing_codes]
        if needed:
            for idx, (code, name) in enumerate(needed):
                item = model(code=code, name=name, is_active=True)
                if hasattr(item, "display_order"):
                    item.display_order = idx + 1
                db.session.add(item)
            db.session.commit()
            records = list(db.session.scalars(stmt).all())

        return records
