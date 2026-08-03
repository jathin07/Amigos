from sqlalchemy import or_
from sqlalchemy.sql import Select


def apply_search(
    stmt: Select,
    model_class,
    search_query: str | None,
    searchable_fields: list[str],
) -> Select:
    """
    Performs case-insensitive LIKE search across
    configured searchable fields.
    """

    if not search_query:
        return stmt

    search_query = search_query.strip()

    if not search_query:
        return stmt

    conditions = []

    for field in searchable_fields:
        if hasattr(model_class, field):
            column = getattr(model_class, field)
            conditions.append(column.ilike(f"%{search_query}%"))

    if conditions:
        stmt = stmt.where(or_(*conditions))

    return stmt