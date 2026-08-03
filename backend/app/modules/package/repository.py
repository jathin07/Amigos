import uuid
from sqlalchemy import select, func, text
from app.core.extensions import db
from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from app.models import Package


class PackageRepository(SQLAlchemyBaseRepository[Package]):
    searchable_fields = ["title"]

    sortable_fields = [
        "title",
        "duration_days",
        "starting_price",
        "created_at",
        "updated_at",
    ]

    filterable_fields = [
        "is_active",
        "is_featured",
        "duration_days",
        "is_deleted",
    ]

    default_sort = [("title", "asc")]

    def __init__(self):
        super().__init__(Package)

    def find_by_title_active(self, title: str, exclude_id: uuid.UUID | None = None) -> Package | None:
        """
        Find an active, non-deleted package whose normalized title matches.
        Optionally exclude a specific package ID (for update duplicate checks).
        """
        stmt = select(self.model_class).where(
            func.lower(func.trim(self.model_class.title)) == title.strip().lower(),
            self.model_class.is_deleted == False,  # noqa: E712
        )
        if exclude_id is not None:
            stmt = stmt.where(self.model_class.id != exclude_id)
        return db.session.scalars(stmt).first()

    def find_active_destination(self, destination_id: uuid.UUID) -> bool:
        """
        Return True if a Destination row exists in the 'destinations' table
        with the given id and is_active=True.

        Uses raw SQL because app/models.py re-imports the master module's
        Destination class (which maps to 'destinations_master', not 'destinations').
        PackageDestination.destination_id FK references 'destinations.id'.
        """
        result = db.session.execute(
            text(
                "SELECT id FROM destinations "
                "WHERE id = :dest_id AND is_active = 1 AND is_deleted = 0 "
                "LIMIT 1"
            ),
            {"dest_id": str(destination_id)},
        ).fetchone()
        return result is not None
