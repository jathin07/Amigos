import uuid
from sqlalchemy import select
from app.core.extensions import db
from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from .models import Destination


class DestinationRepository(SQLAlchemyBaseRepository[Destination]):
    searchable_fields  = ["name", "code", "slug"]
    filterable_fields  = ["is_active", "country_id", "state_id", "district_id"]

    def __init__(self):
        super().__init__(Destination)

    # ── Unique lookups ────────────────────────────────────────────

    def find_by_code(self, code: str) -> Destination | None:
        """Global unique code lookup."""
        return self.model_class.query.filter_by(code=code.strip().upper()).first()

    def find_by_slug(self, slug: str) -> Destination | None:
        """Global unique slug lookup."""
        return self.model_class.query.filter_by(slug=slug.strip().lower()).first()

    def find_by_code_excluding(self, code: str, exclude_id: uuid.UUID) -> Destination | None:
        """Duplicate code check that excludes self during update."""
        stmt = (
            select(self.model_class)
            .where(
                self.model_class.code == code.strip().upper(),
                self.model_class.id   != exclude_id,
            )
        )
        return db.session.scalars(stmt).first()

    def find_by_slug_excluding(self, slug: str, exclude_id: uuid.UUID) -> Destination | None:
        """Duplicate slug check that excludes self during update."""
        stmt = (
            select(self.model_class)
            .where(
                self.model_class.slug == slug.strip().lower(),
                self.model_class.id   != exclude_id,
            )
        )
        return db.session.scalars(stmt).first()

    def get(self, destination_id: uuid.UUID) -> Destination | None:
        return super().get(destination_id)
