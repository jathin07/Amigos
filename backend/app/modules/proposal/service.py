import uuid
import logging
from datetime import datetime, timezone
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
    Proposal,
    ProposalDestination,
    ProposalStatus,
    Lead,
    TeamMember,
)
from .repository import ProposalRepository, _proposal_destination_repository

logger = logging.getLogger("app.proposal")


# ---------------------------------------------------------------------------
# Status transition matrix
# ---------------------------------------------------------------------------

PROPOSAL_TRANSITIONS: dict[str, list[str]] = {
    "DRAFT":               ["UNDER_DISCUSSION", "ARCHIVED"],
    "UNDER_DISCUSSION":    ["REVISED", "APPROVED", "ARCHIVED"],
    "REVISED":             ["UNDER_DISCUSSION", "ARCHIVED"],
    "APPROVED":            ["UNDER_DISCUSSION", "WAITING_FOR_ADVANCE"],
    "WAITING_FOR_ADVANCE": ["CONVERTED"],
    "CONVERTED":           [],
    "ARCHIVED":            [],
}

# Lead statuses that block proposal creation
_INELIGIBLE_LEAD_STATUSES = {"LOST", "WON"}


class ProposalService(BaseService):
    """
    Business service for the Proposal aggregate.

    Owns: create, update, finalize, soft-delete, and read operations.
    All ProposalDestination mutations are internal to this service.
    Events are published strictly after database commit.
    """

    def __init__(self):
        self.repository = ProposalRepository()

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------

    def _resolve_status_id(self, status_code: str) -> uuid.UUID:
        """Return the UUID of a ProposalStatus by code."""
        status = db.session.scalar(
            select(ProposalStatus).where(ProposalStatus.code == status_code)
        )
        if not status:
            raise BusinessException(
                f"ProposalStatus '{status_code}' not found.",
                code="ERR_NOT_FOUND",
            )
        return status.id

    def _get_status_code(self, status_id: uuid.UUID) -> str:
        """Return the code of a ProposalStatus by ID."""
        status = db.session.get(ProposalStatus, status_id)
        return status.code if status else ""

    def _validate_lead_eligibility(self, lead_id: uuid.UUID) -> Lead:
        """
        Verify that the lead exists and is eligible for proposal creation.
        Raises ERR_NOT_FOUND if lead does not exist.
        Raises ERR_LEAD_INELIGIBLE if lead is LOST or WON.
        """
        lead = db.session.scalar(
            select(Lead).where(Lead.id == lead_id, Lead.is_deleted == False)
        )
        if not lead:
            raise NotFoundException("Lead not found.", code="ERR_NOT_FOUND")

        # Resolve lead status code
        if lead.current_status_id:
            from app.models import LeadStatus
            status = db.session.get(LeadStatus, lead.current_status_id)
            if status and status.code in _INELIGIBLE_LEAD_STATUSES:
                raise BusinessException(
                    f"Cannot create a proposal for a lead in '{status.code}' status.",
                    code="ERR_LEAD_INELIGIBLE",
                )
        return lead

    def _validate_status_transition(self, from_status_id: uuid.UUID, to_status_id: uuid.UUID) -> None:
        """Validate that a status transition is allowed by the transition matrix."""
        from_code = self._get_status_code(from_status_id)
        to_code = self._get_status_code(to_status_id)
        allowed = PROPOSAL_TRANSITIONS.get(from_code, [])
        if to_code not in allowed:
            raise BusinessException(
                f"Invalid status transition from '{from_code}' to '{to_code}'.",
                code="ERR_INVALID_STATUS_TRANSITION",
            )

    def _validate_destinations(self, destinations: list[dict]) -> None:
        """
        Validate that all destination_id values reference active records in the
        destinations table. Uses SQLAlchemy Core on the metadata table object
        to bypass class-name registry collision and compile dialect-agnostically.
        """
        if not destinations:
            return
        dest_ids = [uuid.UUID(str(d["destination_id"])) for d in destinations]
        dest_table = db.metadata.tables["destinations"]
        stmt = select(func.count()).select_from(dest_table).where(
            dest_table.c.id.in_(dest_ids),
            dest_table.c.is_deleted == False
        )
        result = db.session.scalar(stmt) or 0
        if result != len(dest_ids):
            raise ValidationException(
                "One or more destination_id values are invalid or inactive.",
                code="ERR_VALIDATION",
            )

    def _sync_destinations(self, proposal: Proposal, destinations: list[dict], context_id: uuid.UUID | None) -> None:
        """Replace all destinations for a proposal with the provided list."""
        _proposal_destination_repository.delete_by_proposal(proposal.id)
        for dest_data in destinations:
            dest = ProposalDestination(
                proposal_id=proposal.id,
                destination_id=dest_data["destination_id"],
                day_order=dest_data.get("day_order"),
                sequence_no=dest_data.get("sequence_no"),
                overnight_stay=dest_data.get("overnight_stay", False),
                day_title=dest_data.get("day_title"),
                travel_time=dest_data.get("travel_time"),
                travel_mode=dest_data.get("travel_mode"),
                distance=dest_data.get("distance"),
                notes=dest_data.get("notes"),
            )
            _proposal_destination_repository.add(dest)

    def _generate_next_version(self, lead_id: uuid.UUID) -> int:
        """
        Generate the next proposal version for a lead using MAX(version)+1.
        Returns the calculated version; collision is handled by the caller retry loop.
        """
        return self.repository.calculate_next_version(lead_id)

    # -----------------------------------------------------------------------
    # Public service methods
    # -----------------------------------------------------------------------

    def create_proposal(self, data: dict, raw_keys: set, context_id: uuid.UUID | None) -> Proposal:
        """
        Create a new proposal version for a lead.

        Transaction Boundary:
          BEGIN
            1. Validate lead eligibility
            2. Resolve default status (DRAFT) if not provided
            3. Validate destination_ids
            4. Calculate next version (with retry on collision)
            5. INSERT Proposal
            6. INSERT ProposalDestination records
          COMMIT
          Publish PROPOSAL_CREATED
        """
        lead_id = data["lead_id"]
        self._validate_lead_eligibility(lead_id)

        # Resolve status_id — default to DRAFT
        status_id = data.get("status_id")
        if not status_id:
            status_id = self._resolve_status_id("DRAFT")

        destinations = data.get("destinations") or []
        if destinations:
            self._validate_destinations(destinations)

        max_retries = current_app.config.get("PROPOSAL_VERSION_MAX_RETRIES", 3)

        for attempt in range(max_retries):
            try:
                next_version = self._generate_next_version(lead_id)

                proposal = Proposal(
                    lead_id=lead_id,
                    version=next_version,
                    row_version=1,
                    proposal_title=data["proposal_title"],
                    price_per_person=data.get("price_per_person"),
                    total_amount=data.get("total_amount"),
                    status_id=status_id,
                    valid_until=data.get("valid_until"),
                    revision_reason=data.get("revision_reason"),
                    internal_notes=data.get("internal_notes"),
                    structured_itinerary=data.get("structured_itinerary"),
                    is_final=False,
                )
                if context_id:
                    proposal.created_by_team_member_id = context_id
                    proposal.updated_by_team_member_id = context_id

                db.session.add(proposal)
                db.session.flush()  # detect version collision early

                if destinations:
                    self._sync_destinations(proposal, destinations, context_id)

                db.session.commit()
                break

            except IntegrityError:
                db.session.rollback()
                logger.warning("Proposal version collision for lead %s (attempt %d)", lead_id, attempt + 1)
                if attempt == max_retries - 1:
                    raise BusinessException(
                        "Could not generate a unique proposal version after multiple retries.",
                        code="ERR_PROPOSAL_VERSION_GENERATION",
                    )
                continue
            except Exception:
                db.session.rollback()
                raise

        # Reload with eager-loaded relationships
        proposal = self.repository.get_with_destinations(proposal.id)

        # Publish event after commit
        try:
            event_bus.publish(DomainEvent.PROPOSAL_CREATED, {
                "proposal_id": str(proposal.id),
                "lead_id": str(proposal.lead_id),
                "version": proposal.version,
                "created_by": str(context_id) if context_id else None,
                "occurred_at": datetime.now(timezone.utc).isoformat(),
            })
        except Exception:
            logger.exception("Failed to publish PROPOSAL_CREATED event for proposal %s", proposal.id)

        logger.info(
            "Proposal created: proposal_id=%s lead_id=%s version=%s",
            proposal.id, proposal.lead_id, proposal.version,
        )
        return proposal

    def update_proposal(self, proposal_id: uuid.UUID, data: dict, raw_keys: set, context_id: uuid.UUID | None) -> Proposal:
        """
        Update a non-finalized proposal.

        Transaction Boundary:
          BEGIN
            1. Fetch proposal → ERR_NOT_FOUND
            2. Guard is_final → ERR_PROPOSAL_IMMUTABLE
            3. Guard row_version mismatch → ERR_CONCURRENT_MODIFICATION
            4. Validate status transition (if status_id changes)
            5. Apply field updates
            6. Apply three-state destination update
            7. Increment row_version
          COMMIT
        """
        proposal = self.repository.get_with_destinations(proposal_id)
        if not proposal:
            raise NotFoundException("Proposal not found.", code="ERR_NOT_FOUND")

        # Guard: immutability — must be first check
        if proposal.is_final:
            raise BusinessException(
                "This proposal has been finalized and cannot be modified.",
                code="ERR_PROPOSAL_IMMUTABLE",
            )

        # Guard: optimistic lock
        if data["row_version"] != proposal.row_version:
            raise BusinessException(
                "Proposal was modified by another user. Please reload and try again.",
                code="ERR_CONCURRENT_MODIFICATION",
            )

        # Status transition validation
        new_status_id = data.get("status_id")
        if new_status_id and new_status_id != proposal.status_id:
            self._validate_status_transition(proposal.status_id, new_status_id)
            proposal.status_id = new_status_id

        try:
            # Apply field updates
            if "proposal_title" in data and data["proposal_title"] is not None:
                proposal.proposal_title = data["proposal_title"]
            if "price_per_person" in data:
                proposal.price_per_person = data.get("price_per_person")
            if "total_amount" in data:
                proposal.total_amount = data.get("total_amount")
            if "valid_until" in data:
                proposal.valid_until = data.get("valid_until")
            if "revision_reason" in data:
                proposal.revision_reason = data.get("revision_reason")
            if "internal_notes" in data:
                proposal.internal_notes = data.get("internal_notes")
            if "structured_itinerary" in data:
                proposal.structured_itinerary = data.get("structured_itinerary")

            # Three-state destination update
            if "destinations" in raw_keys:
                destinations = data.get("destinations")
                if destinations is None:
                    # Key present but null — treat as absent (do not modify)
                    pass
                elif destinations == []:
                    # Explicit empty list — clear all destinations
                    _proposal_destination_repository.delete_by_proposal(proposal.id)
                else:
                    # Non-empty list — validate and replace
                    self._validate_destinations(destinations)
                    self._sync_destinations(proposal, destinations, context_id)

            proposal.row_version += 1
            if context_id:
                proposal.updated_by_team_member_id = context_id

            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        proposal = self.repository.get_with_destinations(proposal_id)
        logger.info(
            "Proposal updated: proposal_id=%s row_version=%s",
            proposal.id, proposal.row_version,
        )
        return proposal

    def finalize_proposal(self, proposal_id: uuid.UUID, data: dict, context_id: uuid.UUID | None) -> Proposal:
        """
        Finalize a proposal (mark as final, transition to WAITING_FOR_ADVANCE).

        Transaction Boundary:
          BEGIN
            1. Fetch proposal → ERR_NOT_FOUND
            2. Guard is_final already → ERR_PROPOSAL_IMMUTABLE
            3. Guard row_version → ERR_CONCURRENT_MODIFICATION
            4. Guard status != APPROVED → ERR_INVALID_STATUS_TRANSITION
            5. Guard another is_final exists for lead → ERR_FINALIZATION_CONFLICT
            6. Set is_final=True, status=WAITING_FOR_ADVANCE
            7. Increment row_version
          COMMIT
          Publish PROPOSAL_FINALIZED
        """
        proposal = self.repository.get_with_destinations(proposal_id)
        if not proposal:
            raise NotFoundException("Proposal not found.", code="ERR_NOT_FOUND")

        # Guard: immutability — must be first check
        if proposal.is_final:
            raise BusinessException(
                "This proposal has already been finalized.",
                code="ERR_PROPOSAL_IMMUTABLE",
            )

        # Guard: optimistic lock
        if data["row_version"] != proposal.row_version:
            raise BusinessException(
                "Proposal was modified by another user. Please reload and try again.",
                code="ERR_CONCURRENT_MODIFICATION",
            )

        # Guard: status must be APPROVED
        current_code = self._get_status_code(proposal.status_id)
        if current_code != "APPROVED":
            raise BusinessException(
                f"Only proposals in 'APPROVED' status can be finalized. Current status: '{current_code}'.",
                code="ERR_INVALID_STATUS_TRANSITION",
            )

        # Guard: no other final proposal for this lead
        existing_final = self.repository.find_final_for_lead(proposal.lead_id)
        if existing_final and existing_final.id != proposal.id:
            raise BusinessException(
                "A finalized proposal already exists for this lead.",
                code="ERR_FINALIZATION_CONFLICT",
            )

        # Resolve WAITING_FOR_ADVANCE status ID
        waiting_status_id = self._resolve_status_id("WAITING_FOR_ADVANCE")

        try:
            proposal.is_final = True
            proposal.status_id = waiting_status_id
            proposal.row_version += 1

            if data.get("approved_by_team_member_id"):
                proposal.approved_by_team_member_id = data["approved_by_team_member_id"]
            if data.get("approved_date"):
                proposal.approved_date = data["approved_date"]
            if context_id:
                proposal.updated_by_team_member_id = context_id

            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        # Publish event after commit — critical event
        try:
            event_bus.publish(DomainEvent.PROPOSAL_FINALIZED, {
                "proposal_id": str(proposal.id),
                "lead_id": str(proposal.lead_id),
                "version": proposal.version,
                "approved_by": str(proposal.approved_by_team_member_id) if proposal.approved_by_team_member_id else None,
                "approved_date": proposal.approved_date.isoformat() if proposal.approved_date else None,
                "total_amount": str(proposal.total_amount) if proposal.total_amount else None,
                "occurred_at": datetime.now(timezone.utc).isoformat(),
            })
        except Exception:
            logger.exception("Failed to publish PROPOSAL_FINALIZED event for proposal %s", proposal.id)

        logger.info(
            "Proposal finalized: proposal_id=%s lead_id=%s version=%s total_amount=%s",
            proposal.id, proposal.lead_id, proposal.version, proposal.total_amount,
        )

        proposal = self.repository.get_with_destinations(proposal_id)
        return proposal

    def soft_delete_proposal(self, proposal_id: uuid.UUID, context_id: uuid.UUID | None) -> None:
        """
        Soft-delete a proposal by setting is_deleted=True.
        Blocked if the proposal is finalized or converted.

        Transaction Boundary:
          BEGIN
            1. Fetch → ERR_NOT_FOUND
            2. Guard is_final → ERR_PROPOSAL_IMMUTABLE
            3. Guard status=CONVERTED → ERR_PROPOSAL_IMMUTABLE
            4. Set is_deleted=True
          COMMIT
        """
        proposal = self.repository.get_with_destinations(proposal_id)
        if not proposal:
            raise NotFoundException("Proposal not found.", code="ERR_NOT_FOUND")

        # Guard: immutability — must be first check
        if proposal.is_final:
            raise BusinessException(
                "A finalized proposal cannot be deleted.",
                code="ERR_PROPOSAL_IMMUTABLE",
            )

        current_code = self._get_status_code(proposal.status_id)
        if current_code == "CONVERTED":
            raise BusinessException(
                "A converted proposal cannot be deleted.",
                code="ERR_PROPOSAL_IMMUTABLE",
            )

        try:
            proposal.is_deleted = True
            if context_id:
                proposal.updated_by_team_member_id = context_id

            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        logger.info("Proposal soft-deleted: proposal_id=%s", proposal_id)

    def get_proposal(self, proposal_id: uuid.UUID) -> Proposal:
        """Fetch a proposal by ID with all relationships loaded."""
        proposal = self.repository.get_with_destinations(proposal_id)
        if not proposal:
            raise NotFoundException("Proposal not found.", code="ERR_NOT_FOUND")
        return proposal

    def list_proposals(
        self,
        page: int = 1,
        page_size: int = 20,
        lead_id: uuid.UUID | None = None,
        status_code: str | None = None,
        is_final: bool | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        """Return a paginated list of proposals with optional filters."""
        max_page_size = current_app.config.get("PROPOSAL_MAX_PAGE_SIZE", 100)
        page_size = min(page_size, max_page_size)
        return self.repository.list_paginated(
            page=page,
            page_size=page_size,
            lead_id=lead_id,
            status_code=status_code,
            is_final=is_final,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def list_by_lead(self, lead_id: uuid.UUID) -> list[Proposal]:
        """Return all proposal versions for a lead, ordered by version descending."""
        return self.repository.find_by_lead(lead_id)


class ProposalLookupService(BaseService):
    """
    Service providing lookup data for Proposal-related dropdowns.
    """

    def list_proposal_statuses(self) -> list[ProposalStatus]:
        """Return all active ProposalStatus records ordered by name."""
        return list(db.session.scalars(
            select(ProposalStatus).order_by(ProposalStatus.name)
        ).all())
