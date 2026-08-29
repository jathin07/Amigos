import uuid
from sqlalchemy import select
from app.core.extensions import db
from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from app.models import TeamMember


class TeamRepository(SQLAlchemyBaseRepository[TeamMember]):
    searchable_fields = [
        "first_name",
        "last_name",
        "display_name",
        "employee_code",
        "official_email",
    ]

    sortable_fields = [
        "employee_code",
        "first_name",
        "last_name",
        "display_name",
        "designation",
        "joined_date",
        "created_at",
        "updated_at",
    ]

    filterable_fields = [
        "is_active",
        "department_id",
        "role_id",
        "reporting_manager_id",
        "employment_status",
        "is_deleted",
    ]

    default_sort = [
        ("created_at", "desc"),
    ]

    def __init__(self):
        super().__init__(TeamMember)

    def find_by_employee_code(self, code: str) -> TeamMember | None:
        """Find active team member by employee code (case-insensitive check is clean)."""
        stmt = select(self.model_class).where(
            self.model_class.employee_code.ilike(code.strip()),
            self.model_class.is_deleted == False
        )
        return db.session.scalars(stmt).first()

    def find_by_employee_code_excluding(self, code: str, exclude_id: uuid.UUID) -> TeamMember | None:
        """Find active team member by employee code excluding a specific ID."""
        stmt = (
            select(self.model_class)
            .where(
                self.model_class.employee_code.ilike(code.strip()),
                self.model_class.id != exclude_id,
                self.model_class.is_deleted == False
            )
        )
        return db.session.scalars(stmt).first()

    def find_by_official_email(self, email: str) -> TeamMember | None:
        """Find active team member by official email (case-insensitive)."""
        stmt = select(self.model_class).where(
            self.model_class.official_email.ilike(email.strip()),
            self.model_class.is_deleted == False
        )
        return db.session.scalars(stmt).first()

    def find_by_official_email_excluding(self, email: str, exclude_id: uuid.UUID) -> TeamMember | None:
        """Find active team member by official email excluding a specific ID."""
        stmt = (
            select(self.model_class)
            .where(
                self.model_class.official_email.ilike(email.strip()),
                self.model_class.id != exclude_id,
                self.model_class.is_deleted == False
            )
        )
        return db.session.scalars(stmt).first()
