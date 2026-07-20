from __future__ import annotations

import logging
from typing import Optional, Type

from app.core.extensions import db
from app.domain.interfaces import IUnitOfWork

logger = logging.getLogger("app.repository")


class UnitOfWork(IUnitOfWork):
    """
    Owns the transaction boundary for an application service.
    """

    def __enter__(self) -> "UnitOfWork":
        logger.debug("UnitOfWork started.")
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb,
    ) -> None:
        if exc_type is not None:
            self.rollback()
            logger.debug("UnitOfWork exited with rollback.")
        else:
            self.commit()
            logger.debug("UnitOfWork exited with commit.")

    def commit(self) -> None:
        try:
            db.session.commit()
            logger.debug("Transaction committed.")
        except Exception:
            logger.exception("Failed to commit transaction.")
            db.session.rollback()
            raise

    def rollback(self) -> None:
        try:
            db.session.rollback()
            logger.debug("Transaction rolled back.")
        except Exception:
            logger.exception("Rollback failed.")
            raise

    def flush(self) -> None:
        try:
            db.session.flush()
            logger.debug("Session flushed.")
        except Exception:
            logger.exception("Flush failed.")
            raise