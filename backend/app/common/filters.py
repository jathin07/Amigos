from typing import Any
from sqlalchemy.sql import Select


def apply_filters(
    stmt: Select,
    model_class,
    filters: dict[str, Any],
    filterable_fields: list[str],
) -> Select:
    """
    Apply equality filters safely.

    Only fields declared in filterable_fields are allowed.
    """

    if not filters:
        return stmt

    allowed_fields = set(filterable_fields)

    for field, value in filters.items():
        if field not in allowed_fields:
            continue

        if not hasattr(model_class, field):
            continue

        if value is None:
            continue

        if isinstance(value, str):
            value = value.strip()
            if value == "":
                continue

        stmt = stmt.where(getattr(model_class, field) == value)

    return stmt