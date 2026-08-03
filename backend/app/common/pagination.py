from __future__ import annotations

import math
from typing import Any, Generic, TypeVar

T = TypeVar("T")

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


class PaginationResult(Generic[T]):
    def __init__(
        self,
        items: list[T],
        page: int,
        page_size: int,
        total_records: int,
    ):
        self.items = items
        self.page = page
        self.page_size = page_size
        self.total_records = total_records
        self.total_pages = (
            math.ceil(total_records / page_size)
            if page_size > 0
            else 0
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "items": self.items,
            "pagination": {
                "page": self.page,
                "page_size": self.page_size,
                "total_records": self.total_records,
                "total_pages": self.total_pages,
            },
        }


def normalize_pagination(
    page: int | None,
    page_size: int | None,
) -> tuple[int, int]:
    page = page or DEFAULT_PAGE
    page_size = page_size or DEFAULT_PAGE_SIZE

    page = max(page, 1)
    page_size = min(max(page_size, 1), MAX_PAGE_SIZE)

    return page, page_size


def apply_pagination(stmt, page: int, page_size: int):
    page, page_size = normalize_pagination(page, page_size)

    offset = (page - 1) * page_size

    return stmt.offset(offset).limit(page_size)