from __future__ import annotations

import logging
from typing import Any

from app.core.extensions import db
from app.domain.exceptions import (
    DomainException,
    InfrastructureException,
)
from app.infrastructure.responses.api_response import (
    error_response,
    success_response,
)

logger = logging.getLogger(__name__)


class BaseService:
    """
    Base service.

    Contains only infrastructure helpers.

    Business validation belongs
    inside concrete services.
    """

    def commit(self) -> None:
        try:
            db.session.commit()

        except Exception as ex:

            db.session.rollback()

            logger.exception("Database transaction failed")

            raise InfrastructureException(
                "Database transaction failed"
            ) from ex

    def rollback(self) -> None:
        db.session.rollback()

    def success(
        self,
        data: Any = None,
        message: str = "Success",
        status_code: int = 200,
        meta: dict | None = None,
    ):
        return success_response(
            data=data,
            message=message,
            meta=meta,
            status_code=status_code,
        )

    def error(
        self,
        message: str,
        code: str = "ERR_BAD_REQUEST",
        errors: list | None = None,
        status_code: int = 400,
    ):
        return error_response(
            message=message,
            code=code,
            errors=errors,
            status_code=status_code,
        )

    @staticmethod
    def check_optimistic_lock(
        current_version: int,
        expected_version: int | None,
    ) -> None:

        if expected_version is None:
            return

        if current_version != expected_version:

            raise DomainException(
                "Record has been modified by another user.",
                code="ERR_CONCURRENT_MODIFICATION",
            )