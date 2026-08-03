import re
import uuid
from sqlalchemy import select, func, or_, extract
from sqlalchemy.orm import joinedload

from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from app.models import ContactPerson, Lead, CRMActivity, FollowUp, AssignmentHistory, TeamMember, Package
from app.core.extensions import db
from app.common.pagination import PaginationResult


class ContactPersonRepository(SQLAlchemyBaseRepository[ContactPerson]):
    """
    Repository handling persistence logic for ContactPerson.
    """
    def __init__(self):
        super().__init__(ContactPerson)

    def find_by_phone(self, phone: str) -> ContactPerson | None:
        """
        Find an active contact person by normalized phone number.
        Normalizes both input and stored numbers to only digits,
        and matches the last 10 digits to handle country codes safely.
        """
        if not phone:
            return None
        normalized_input = re.sub(r"\D", "", phone)[-10:]
        if not normalized_input:
            return None
        
        stmt = select(ContactPerson).where(
            ContactPerson.is_active == True,
            ContactPerson.is_deleted == False
        )
        contacts = db.session.scalars(stmt).all()
        for contact in contacts:
            if contact.phone:
                normalized_stored = re.sub(r"\D", "", contact.phone)[-10:]
                if normalized_stored == normalized_input:
                    return contact
        return None

    def find_by_email(self, email: str) -> ContactPerson | None:
        """
        Find an active contact person by email.
        """
        if not email:
            return None
        stmt = select(ContactPerson).where(
            ContactPerson.email == email.strip(),
            ContactPerson.is_active == True,
            ContactPerson.is_deleted == False
        )
        return db.session.scalar(stmt)


class LeadRepository(SQLAlchemyBaseRepository[Lead]):
    """
    Repository handling persistence logic for Lead, implementing custom search, filtering, and eager loading.
    """
    sortable_fields = [
        "created_at",
        "updated_at",
        "lead_number",
        "expected_travel_date",
        "priority_id",
        "current_status_id",
    ]
    
    default_sort = [
        ("created_at", "desc"),
    ]

    def __init__(self):
        super().__init__(Lead)

    def count_leads_by_year(self, year: int) -> int:
        """
        Count the number of active leads created in a given calendar year.
        Uses SQLAlchemy extract to remain dialect-agnostic (works on both SQLite and PostgreSQL).
        """
        stmt = select(func.count(Lead.id)).where(
            extract("year", Lead.created_at) == year,
            Lead.is_deleted == False
        )
        return db.session.scalar(stmt) or 0

    def paginate(
        self,
        page: int,
        page_size: int,
        search_query: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
        **filters,
    ) -> PaginationResult[Lead]:
        # Start statement with joins to prevent N+1 queries and support joined searching
        stmt = select(Lead).outerjoin(Lead.contact_person).outerjoin(Lead.package)
        
        # Eager load related lookup relations
        stmt = stmt.options(
            joinedload(Lead.contact_person),
            joinedload(Lead.current_status),
            joinedload(Lead.lead_source),
            joinedload(Lead.priority),
            joinedload(Lead.trip_type),
            joinedload(Lead.lost_reason),
            joinedload(Lead.package)
        )
        
        # Filter active only
        stmt = stmt.where(Lead.is_deleted == False)

        # Apply specific filters
        if "current_status_id" in filters and filters["current_status_id"]:
            stmt = stmt.where(Lead.current_status_id == filters["current_status_id"])
        if "priority_id" in filters and filters["priority_id"]:
            stmt = stmt.where(Lead.priority_id == filters["priority_id"])
        if "lead_source_id" in filters and filters["lead_source_id"]:
            stmt = stmt.where(Lead.lead_source_id == filters["lead_source_id"])
        if "owner_team_member_id" in filters and filters["owner_team_member_id"]:
            stmt = stmt.where(Lead.owner_team_member_id == filters["owner_team_member_id"])
        
        # Date range filters
        if "travel_start_date_gte" in filters and filters["travel_start_date_gte"]:
            stmt = stmt.where(Lead.travel_start_date >= filters["travel_start_date_gte"])
        if "travel_start_date_lte" in filters and filters["travel_start_date_lte"]:
            stmt = stmt.where(Lead.travel_start_date <= filters["travel_start_date_lte"])

        # Apply text search across joined tables and lead_number
        if search_query:
            stmt = stmt.outerjoin(TeamMember, Lead.owner_team_member_id == TeamMember.id)
            q = f"%{search_query.strip()}%"
            stmt = stmt.where(
                or_(
                    Lead.lead_number.ilike(q),
                    ContactPerson.name.ilike(q),
                    ContactPerson.phone.ilike(q),
                    ContactPerson.email.ilike(q),
                    Package.title.ilike(q),
                    TeamMember.display_name.ilike(q)
                )
            )

        # Count total records matching filters and search
        total_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.session.scalar(total_stmt) or 0

        # Apply sorting
        if sort_by in self.sortable_fields:
            col = getattr(Lead, sort_by)
            stmt = stmt.order_by(col.desc() if sort_order == "desc" else col.asc())
        else:
            stmt = stmt.order_by(Lead.created_at.desc())

        # Apply offset and limit pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        items = list(db.session.scalars(stmt).unique().all())

        return PaginationResult(
            items=items,
            page=page,
            page_size=page_size,
            total_records=total,
        )


class CRMActivityRepository(SQLAlchemyBaseRepository[CRMActivity]):
    """
    Repository handling persistence logic for CRMActivity.
    """
    def __init__(self):
        super().__init__(CRMActivity)


class FollowUpRepository(SQLAlchemyBaseRepository[FollowUp]):
    """
    Repository handling persistence logic for FollowUp.
    """
    def __init__(self):
        super().__init__(FollowUp)


class AssignmentHistoryRepository(SQLAlchemyBaseRepository[AssignmentHistory]):
    """
    Repository handling persistence logic for AssignmentHistory.
    """
    def __init__(self):
        super().__init__(AssignmentHistory)

    def get_active_assignment(self, lead_id: str | uuid.UUID) -> AssignmentHistory | None:
        """Get the current active assignment log for a lead."""
        stmt = select(AssignmentHistory).where(
            AssignmentHistory.entity_id == lead_id,
            AssignmentHistory.entity_type == "Lead",
            AssignmentHistory.effective_to == None
        )
        return db.session.scalar(stmt)

    def get_assignment_history(self, lead_id: str | uuid.UUID) -> list[AssignmentHistory]:
        """Get all assignment history logs for a lead, sorted by date desc."""
        stmt = select(AssignmentHistory).where(
            AssignmentHistory.entity_id == lead_id,
            AssignmentHistory.entity_type == "Lead"
        ).order_by(AssignmentHistory.effective_from.desc())
        return list(db.session.scalars(stmt).all())
