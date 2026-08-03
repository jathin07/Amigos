from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from .models import City
import uuid

class CityRepository(SQLAlchemyBaseRepository[City]):
    searchable_fields = ["name", "code"]
    filterable_fields = ["is_active", "state_id"]

    def __init__(self):
        super().__init__(City)

    def find_by_code(self, code: str, state_id: uuid.UUID) -> City | None:
        """Find a city by its code within a specific state."""
        return self.model_class.query.filter_by(code=code.upper(), state_id=state_id).first()

    def get(self, city_id: uuid.UUID) -> City | None:
        """Override to ensure UUID is passed."""
        return super().get(city_id)
