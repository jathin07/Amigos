from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class IRepository(Generic[T], ABC):
    """Base repository contract."""

    @abstractmethod
    def add(self, entity: T) -> T:
        ...

    @abstractmethod
    def get(self, entity_id: Any) -> T | None:
        ...

    @abstractmethod
    def list(self, **filters: Any) -> list[T]:
        ...

    @abstractmethod
    def update(self, entity: T) -> T:
        ...

    @abstractmethod
    def delete(self, entity: T) -> None:
        ...

    @abstractmethod
    def exists(self, entity_id: Any) -> bool:
        ...

    @abstractmethod
    def count(self, **filters: Any) -> int:
        ...

    @abstractmethod
    def paginate(
        self,
        page: int,
        limit: int,
        **filters: Any,
    ) -> tuple[list[T], int]:
        """
        Returns:
            (items, total_count)
        """
        ...


class IUnitOfWork(ABC):
    """Transaction boundary."""

    @abstractmethod
    def __enter__(self) -> "IUnitOfWork":
        ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        ...

    @abstractmethod
    def commit(self) -> None:
        ...

    @abstractmethod
    def rollback(self) -> None:
        ...

    @abstractmethod
    def flush(self) -> None:
        """
        Flush pending SQL without committing.
        """
        ...


class IService(ABC):
    """
    Marker interface for all Application Services.
    """
    pass