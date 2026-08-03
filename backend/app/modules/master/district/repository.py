from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from .models import District
import uuid

class DistrictRepository(SQLAlchemyBaseRepository[District]):
    searchable_fields = ["name", "code"]
    filterable_fields = ["is_active", "state_id"]

    def __init__(self):
        super().__init__(District)

    def find_by_code(self, code: str, state_id: uuid.UUID) -> District | None:
        """Find a district by its code within a specific state."""
        return self.model_class.query.filter_by(code=code.upper(), state_id=state_id).first()

    def get(self, district_id: uuid.UUID) -> District | None:
        """Override to ensure UUID is passed."""
        return super().get(district_id)
