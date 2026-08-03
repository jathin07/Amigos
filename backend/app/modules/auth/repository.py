from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select

from app.core.extensions import db
from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from app.models import RefreshToken, TeamMember, UserAccount


class AuthRepository(SQLAlchemyBaseRepository[UserAccount]):
    """
    Repository responsible for authentication persistence operations.
    """

    def __init__(self) -> None:
        super().__init__(UserAccount)

    def find_by_email(self, email: str) -> Optional[UserAccount]:
        """
        Find a user by official email address.
        Email comparison is case-insensitive.
        """

        statement = (
            select(UserAccount)
            .join(TeamMember)
            .where(
                func.lower(TeamMember.official_email)
                == email.strip().lower()
            )
        )

        return db.session.execute(statement).scalar_one_or_none()

    def find_active_user(self, user_id: str) -> Optional[UserAccount]:
        """
        Returns an active user whose linked TeamMember is also active.
        """

        statement = (
            select(UserAccount)
            .join(TeamMember)
            .where(
                UserAccount.id == (uuid.UUID(user_id) if isinstance(user_id, str) else user_id),
                UserAccount.is_active.is_(True),
                TeamMember.is_active.is_(True),
            )
        )

        return db.session.execute(statement).scalar_one_or_none()

    def save_refresh_token(
        self,
        token_hash: str,
        user_id: str,
        expires_at: datetime,
    ) -> RefreshToken:
        """
        Persist a new refresh token.
        """

        token = RefreshToken(
            user_account_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_revoked=False,
        )

        db.session.add(token)

        return token

    def find_refresh_token(
        self,
        token_hash: str,
    ) -> Optional[RefreshToken]:
        """
        Find an active refresh token.
        """

        statement = (
            select(RefreshToken)
            .where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.is_revoked.is_(False),
            )
        )

        return db.session.execute(statement).scalar_one_or_none()

    def revoke_refresh_token(
        self,
        token_hash: str,
    ) -> bool:
        """
        Revoke a refresh token.

        Returns:
            True if revoked.
            False if token was not found.
        """

        token = self.find_refresh_token(token_hash)

        if token is None:
            return False

        token.is_revoked = True

        db.session.add(token)

        return True

    def find_by_reset_token(self, token_hash: str) -> Optional[UserAccount]:
        """
        Finds a user by their reset token hash.
        """
        statement = (
            select(UserAccount)
            .where(UserAccount.reset_token_hash == token_hash)
        )
        return db.session.execute(statement).scalar_one_or_none()