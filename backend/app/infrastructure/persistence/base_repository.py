from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import func, select

from app.common.filters import apply_filters
from app.common.pagination import PaginationResult, apply_pagination
from app.common.search import apply_search
from app.common.sorting import apply_sort
from app.core.extensions import db
from app.domain.interfaces import IRepository

T = TypeVar("T")


class SQLAlchemyBaseRepository(
    IRepository[T],
    Generic[T],
):
    """
    Generic SQLAlchemy repository.
    """

    searchable_fields: list[str] = []

    sortable_fields = [
        "name",
        "code",
        "display_order",
        "created_at",
        "updated_at",
    ]

    filterable_fields = [
        "is_active",
    ]

    default_sort = [
        ("display_order", "asc"),
        ("name", "asc"),
    ]

    def __init__(self, model_class: type[T]):
        self.model_class = model_class

    def add(self, entity: T) -> T:
        db.session.add(entity)
        return entity

    def get(self, entity_id: Any) -> T | None:
        return db.session.get(
            self.model_class,
            entity_id,
        )

    def update(self, entity: T) -> T:
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

    def count(
        self,
        **filters,
    ) -> int:

        stmt = select(func.count()).select_from(self.model_class)

        stmt = apply_filters(
            stmt,
            self.model_class,
            filters,
            self.filterable_fields,
        )

        return db.session.scalar(stmt)


    def list(
        self,
        **filters,
    ) -> list[T]:

        stmt = select(self.model_class)

        stmt = apply_filters(
            stmt,
            self.model_class,
            filters,
            self.filterable_fields,
        )

        stmt = apply_sort(
            stmt,
            self.model_class,
            None,
            sortable_fields=self.sortable_fields,
            default_sort=self.default_sort,
        )

        return list(
            db.session.scalars(stmt)
        )

    def paginate(
        self,
        page: int,
        page_size: int,
        search_query: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
        **filters,
    ) -> PaginationResult[T]:

        stmt = select(self.model_class)

        stmt = apply_filters(
            stmt,
            self.model_class,
            filters,
            self.filterable_fields,
        )

        stmt = apply_search(
            stmt,
            self.model_class,
            search_query,
            self.searchable_fields,
        )

        total_stmt = (
            select(func.count())
            .select_from(stmt.subquery())
        )

        total = db.session.scalar(total_stmt)

        stmt = apply_sort(
            stmt,
            self.model_class,
            sort_by,
            sort_order,
            sortable_fields=self.sortable_fields,
            default_sort=self.default_sort,
        )

        stmt = apply_pagination(
            stmt,
            page,
            page_size,
        )

        items = list(
            db.session.scalars(stmt)
        )

        return PaginationResult(
            items=items,
            page=page,
            page_size=page_size,
            total_records=total,
        )