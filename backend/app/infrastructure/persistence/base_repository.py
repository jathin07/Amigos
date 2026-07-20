from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import select, func

from app.core.extensions import db
from app.domain.interfaces import IRepository

T = TypeVar("T")


class SQLAlchemyBaseRepository(IRepository[T], Generic[T]):
    """
    Generic SQLAlchemy repository.

    Concrete repositories should inherit from this class.

    Example:
        class LeadRepository(SQLAlchemyBaseRepository[Lead]):
            def __init__(self):
                super().__init__(Lead)
    """

    def __init__(self, model_class: type[T]):
        self.model_class = model_class

    def add(self, entity: T) -> T:
        db.session.add(entity)
        return entity

    def get(self, entity_id: Any) -> T | None:
        return db.session.get(self.model_class, entity_id)

    def list(self, **filters: Any) -> list[T]:
        stmt = select(self.model_class)

        for field, value in filters.items():
            if hasattr(self.model_class, field):
                stmt = stmt.where(getattr(self.model_class, field) == value)

        return list(db.session.scalars(stmt))

    def update(self, entity: T) -> T:
        """
        SQLAlchemy automatically tracks attached entities.
        """
        db.session.add(entity)
        return entity

    def delete(self, entity: T) -> None:
        db.session.delete(entity)

    def exists(self, entity_id: Any) -> bool:
        stmt = (
            select(func.count())
            .select_from(self.model_class)
            .where(self.model_class.id == entity_id)
        )
        return db.session.scalar(stmt) > 0

    def count(self, **filters: Any) -> int:
        stmt = select(func.count()).select_from(self.model_class)

        for field, value in filters.items():
            if hasattr(self.model_class, field):
                stmt = stmt.where(getattr(self.model_class, field) == value)

        return db.session.scalar(stmt)

    def paginate(
        self,
        page: int,
        limit: int,
        **filters: Any,
    ) -> tuple[list[T], int]:

        stmt = select(self.model_class)

        for field, value in filters.items():
            if hasattr(self.model_class, field):
                stmt = stmt.where(getattr(self.model_class, field) == value)

        total_stmt = (
            select(func.count())
            .select_from(stmt.subquery())
        )

        total = db.session.scalar(total_stmt)

        stmt = stmt.offset((page - 1) * limit).limit(limit)

        items = list(db.session.scalars(stmt))

        return items, total
    
    def _apply_filters(self, stmt, filters):
        for field, value in filters.items():
            if hasattr(self.model_class, field):
                stmt = stmt.where(getattr(self.model_class, field) == value)
        return stmt