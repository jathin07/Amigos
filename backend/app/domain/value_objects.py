from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class Money:
    """
    Represents a monetary value.
    """

    amount: Decimal
    currency: str = "INR"

    def __post_init__(self) -> None:
        if self.amount < Decimal("0"):
            raise ValueError("Amount cannot be negative.")

        if len(self.currency) != 3:
            raise ValueError("Currency must be a valid ISO 4217 code.")

    def __add__(self, other: "Money") -> "Money":
        self._validate_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._validate_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def _validate_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError("Currency mismatch.")

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"


@dataclass(frozen=True)
class Address:
    """
    Represents a postal address.
    """

    line1: str
    city: str
    state: str
    country: str
    postal_code: str
    line2: str | None = None

    def __post_init__(self) -> None:
        if not self.line1.strip():
            raise ValueError("Address line1 cannot be empty.")

        if not self.city.strip():
            raise ValueError("City cannot be empty.")

        if not self.country.strip():
            raise ValueError("Country cannot be empty.")

        if not self.postal_code.strip():
            raise ValueError("Postal code cannot be empty.")

    @property
    def full_address(self) -> str:
        parts = [
            self.line1,
            self.line2,
            self.city,
            self.state,
            self.country,
            self.postal_code,
        ]
        return ", ".join(part for part in parts if part)


@dataclass(frozen=True)
class UUIDReference:
    """
    Strongly typed UUID wrapper.
    """

    id: UUID

    def __str__(self) -> str:
        return str(self.id)