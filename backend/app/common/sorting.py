from sqlalchemy.sql import Select


DEFAULT_SORT_ORDER = "asc"


def apply_sort(
    stmt: Select,
    model_class,
    sort_by: str | None,
    sort_order: str = DEFAULT_SORT_ORDER,
    sortable_fields: list[str] | None = None,
    default_sort: list[tuple[str, str]] | None = None,
) -> Select:
    """
    Applies safe sorting.

    Example:

    default_sort=[
        ("display_order", "asc"),
        ("name", "asc")
    ]
    """

    if sortable_fields is None:
        sortable_fields = []

    allowed_fields = set(sortable_fields)

    if sort_by:
        sort_by = sort_by.strip()

    if (
        sort_by
        and sort_by in allowed_fields
        and hasattr(model_class, sort_by)
    ):
        column = getattr(model_class, sort_by)

        if sort_order.lower() == "desc":
            return stmt.order_by(column.desc())

        return stmt.order_by(column.asc())

    if default_sort:
        order_columns = []

        for field, direction in default_sort:
            if hasattr(model_class, field):
                column = getattr(model_class, field)

                if direction.lower() == "desc":
                    order_columns.append(column.desc())
                else:
                    order_columns.append(column.asc())

        if order_columns:
            stmt = stmt.order_by(*order_columns)

    return stmt