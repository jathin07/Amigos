from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from .models import State
import uuid

class StateRepository(SQLAlchemyBaseRepository[State]):
    searchable_fields = ["name", "code"]
    filterable_fields = ["is_active", "country_id"]

    def __init__(self):
        super().__init__(State)

    def find_by_code(self, code: str, country_id: uuid.UUID) -> State | None:
        """Find a state by its code within a specific country."""
        return self.find_by_code_and_country(code, country_id)

    def find_by_code_and_country(self, code: str, country_id: uuid.UUID) -> State | None:
        """Find a state by its code within a specific country."""
        return self.model_class.query.filter_by(code=code.upper(), country_id=country_id).first()

    def list_by_country(self, country_id: uuid.UUID) -> list[State]:
        """Return active states for a country, sorted by display_order then name."""
        return self.list(country_id=country_id, is_active=True)

    def get_by_id(self, state_id: uuid.UUID) -> State | None:
        """Override to ensure UUID is passed."""
        return super().get(state_id)
