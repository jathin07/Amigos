from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from .models import Country


class CountryRepository(SQLAlchemyBaseRepository[Country]):

    searchable_fields = ["name", "code"]
    filterable_fields = ["is_active"]

    def __init__(self):
        super().__init__(Country)

    def get_by_id(self, country_id) -> Country | None:
        return self.get(country_id)

    def find_by_code(self, code: str) -> Country | None:
        """Return country by exact code match (case-insensitive)."""
        return self.model_class.query.filter_by(code=code.strip().upper()).first()

    def find_by_code_excluding(self, code: str, exclude_id) -> Country | None:
        """Duplicate check that excludes self during update."""
        from sqlalchemy import select
        from app.core.extensions import db
        stmt = (
            select(Country)
            .where(Country.code == code.strip().upper())
            .where(Country.id != exclude_id)
        )
        return db.session.scalars(stmt).first()

    def list_active(self):
        return self.list(is_active=True)
