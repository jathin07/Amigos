import uuid
from sqlalchemy import select
from app.core.extensions import db
from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from .models import TaxConfiguration

class TaxConfigurationRepository(SQLAlchemyBaseRepository[TaxConfiguration]):
    searchable_fields = ["name", "code"]
    filterable_fields = ["is_active"]

    def __init__(self):
        super().__init__(TaxConfiguration)

    def find_by_code(self, code: str) -> TaxConfiguration | None:
        return self.model_class.query.filter_by(code=code.strip().upper()).first()

    def find_by_code_excluding(self, code: str, exclude_id: uuid.UUID) -> TaxConfiguration | None:
        stmt = select(self.model_class).where(
            self.model_class.code == code.strip().upper(),
            self.model_class.id != exclude_id,
        )
        return db.session.scalars(stmt).first()

    def get(self, entity_id: uuid.UUID):
        return super().get(entity_id)
        
    def get_defaults_by_type(self, tax_type: str):
        return self.model_class.query.filter_by(tax_type=tax_type, is_default=True).all()
