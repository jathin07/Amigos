import uuid
from sqlalchemy import select, func, text
from sqlalchemy.orm import joinedload

from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from app.models import Proposal, ProposalDestination, ProposalStatus
from app.core.extensions import db
from app.common.pagination import PaginationResult


class ProposalRepository(SQLAlchemyBaseRepository[Proposal]):
    """
    Repository handling persistence for the Proposal aggregate root.

    Architectural rule: This repository is the only layer allowed to query the
    proposals table. Services consume this repository exclusively.
    """

    sortable_fields = [
        "created_at",
        "updated_at",
        "proposal_title",
        "total_amount",
        "valid_until",
        "version",
    ]

    default_sort = [
        ("created_at", "desc"),
    ]

    def __init__(self):
        super().__init__(Proposal)

    def get_with_destinations(self, proposal_id: uuid.UUID) -> Proposal | None:
        """
        Fetch a single proposal by PK with ProposalDestination eagerly loaded.
        Returns None if not found or soft-deleted.
        """
        stmt = (
            select(Proposal)
            .options(joinedload(Proposal.destinations))
            .where(
                Proposal.id == proposal_id,
                Proposal.is_deleted == False,
            )
        )
        return db.session.scalar(stmt)

    def find_by_lead(self, lead_id: uuid.UUID) -> list[Proposal]:
        """
        Return all proposals for a lead, ordered by version descending.
        Excludes soft-deleted proposals.
        """
        stmt = (
            select(Proposal)
            .where(
                Proposal.lead_id == lead_id,
                Proposal.is_deleted == False,
            )
            .order_by(Proposal.version.desc())
        )
        return list(db.session.scalars(stmt).all())

    def find_final_for_lead(self, lead_id: uuid.UUID) -> Proposal | None:
        """
        Return the is_final=True proposal for a lead, or None if none exists.
        Excludes soft-deleted proposals (consistent with partial unique index).
        """
        stmt = select(Proposal).where(
            Proposal.lead_id == lead_id,
            Proposal.is_final == True,
            Proposal.is_deleted == False,
        )
        return db.session.scalar(stmt)

    def calculate_next_version(self, lead_id: uuid.UUID) -> int:
        """
        Calculate MAX(version) + 1 for proposals belonging to this lead.
        Returns 1 if this is the first proposal for the lead.
        """
        stmt = select(
            func.coalesce(func.max(Proposal.version), 0) + 1
        ).where(Proposal.lead_id == lead_id)
        return db.session.scalar(stmt) or 1

    def list_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        lead_id: uuid.UUID | None = None,
        status_code: str | None = None,
        is_final: bool | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> PaginationResult:
        """
        Return a paginated list of proposals with optional filtering and sorting.
        """
        stmt = (
            select(Proposal)
            .options(joinedload(Proposal.status))
            .where(Proposal.is_deleted == False)
        )

        # Filters
        if lead_id:
            stmt = stmt.where(Proposal.lead_id == lead_id)
        if is_final is not None:
            stmt = stmt.where(Proposal.is_final == is_final)
        if search:
            stmt = stmt.where(Proposal.proposal_title.ilike(f"%{search}%"))
        if status_code:
            stmt = stmt.join(Proposal.status).where(
                ProposalStatus.code == status_code
            )

        # Sorting
        sort_col = getattr(Proposal, sort_by, None)
        if sort_col is not None:
            stmt = stmt.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())
        else:
            stmt = stmt.order_by(Proposal.created_at.desc())

        # Count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.session.scalar(count_stmt) or 0

        # Paginate
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)
        items = list(db.session.scalars(stmt).unique().all())

        return PaginationResult(
            items=items,
            page=page,
            page_size=page_size,
            total_records=total,
        )


class _ProposalDestinationRepository:
    """
    Internal repository for ProposalDestination child entities.

    ARCHITECTURAL RULE: This class must NEVER be imported or used outside
    app/modules/proposal/. It is an internal implementation detail of ProposalService.
    All ProposalDestination mutations must go through ProposalService.
    """

    def delete_by_proposal(self, proposal_id: uuid.UUID) -> None:
        """Delete all destinations belonging to a proposal."""
        stmt = select(ProposalDestination).where(
            ProposalDestination.proposal_id == proposal_id
        )
        destinations = db.session.scalars(stmt).all()
        for dest in destinations:
            db.session.delete(dest)

    def add(self, destination: ProposalDestination) -> None:
        """Persist a new ProposalDestination."""
        db.session.add(destination)


# Internal singleton — not exported from __init__.py
_proposal_destination_repository = _ProposalDestinationRepository()
