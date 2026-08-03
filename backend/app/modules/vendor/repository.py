import uuid
from sqlalchemy import select
from app.core.extensions import db
from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from app.models import Vendor


class VendorRepository(SQLAlchemyBaseRepository[Vendor]):
    searchable_fields = [
        "vendor_name",
        "contact_person",
        "phone",
        "email",
        "gst_number",
    ]

    sortable_fields = [
        "vendor_name",
        "internal_rating",
        "created_at",
        "updated_at",
    ]

    filterable_fields = [
        "is_active",
        "vendor_type_id",
        "is_verified",
        "is_deleted",
    ]

    default_sort = [
        ("vendor_name", "asc"),
    ]

    def __init__(self):
        super().__init__(Vendor)

    def find_by_gst_number(self, gst_number: str) -> Vendor | None:
        """Find an active vendor with the given normalized GST number."""
        return self.model_class.query.filter(
            self.model_class.gst_number.ilike(gst_number.strip()),
            self.model_class.is_deleted == False
        ).first()

    def find_by_gst_number_excluding(self, gst_number: str, exclude_id: uuid.UUID) -> Vendor | None:
        """Find an active vendor with the given normalized GST number, excluding a specific ID."""
        stmt = (
            select(self.model_class)
            .where(
                self.model_class.gst_number.ilike(gst_number.strip()),
                self.model_class.id != exclude_id,
                self.model_class.is_deleted == False
            )
        )
        return db.session.scalars(stmt).first()
