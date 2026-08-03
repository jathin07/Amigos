import uuid
from sqlalchemy import select
from app.core.extensions import db
from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from .models import Season

class SeasonRepository(SQLAlchemyBaseRepository[Season]):
    searchable_fields = ["name", "code"]
    filterable_fields = ["is_active"]

    def __init__(self):
        super().__init__(Season)

    def find_by_code(self, code: str) -> Season | None:
        return self.model_class.query.filter_by(code=code.strip().upper()).first()

    def find_by_code_excluding(self, code: str, exclude_id: uuid.UUID) -> Season | None:
        stmt = select(self.model_class).where(
            self.model_class.code == code.strip().upper(),
            self.model_class.id != exclude_id,
        )
        return db.session.scalars(stmt).first()

    def get(self, entity_id: uuid.UUID):
        return super().get(entity_id)
