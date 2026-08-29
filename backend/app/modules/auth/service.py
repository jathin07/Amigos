from __future__ import annotations

import hashlib
import logging
import secrets
from datetime import timedelta, timezone, datetime

from flask import current_app
from werkzeug.security import check_password_hash as werkzeug_check_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
)

from app.common.utils import current_utc_time
from app.core.extensions import bcrypt
from app.domain.exceptions import (
    AuthenticationException,
    AuthorizationException,
    ValidationException,
)
from app.infrastructure.persistence.uow import UnitOfWork
from app.modules.auth.mapper import AuthMapper
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas.request import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
)
from app.modules.auth.schemas.response import (
    CurrentUserResponse,
    LoginResponse,
    SessionDTO,
    VerifyTokenResponse,
)

logger = logging.getLogger(__name__)


class AuthService:

    def __init__(self, repository: AuthRepository):
        self.repository = repository
        self.mapper = AuthMapper()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def _build_claims(self, user):
        permissions = [
            permission.code
            for permission in self.mapper.to_permissions(
                user.team_member
            )
        ]

        role = (
            user.team_member.role.name
            if user.team_member.role
            else "Team Member"
        )

        return {
            "role": role,
            "permissions": permissions,
        }

    def _create_session(self, user):
        claims = self._build_claims(user)

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims=claims,
        )

        refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims=claims,
        )

        expires_days = current_app.config.get(
            "JWT_REFRESH_TOKEN_EXPIRES_DAYS",
            30,
        )

        self.repository.save_refresh_token(
            token_hash=self._hash_token(refresh_token),
            user_id=str(user.id),
            expires_at=current_utc_time()
            + timedelta(days=expires_days),
        )

        return SessionDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=current_app.config.get(
                "JWT_ACCESS_TOKEN_EXPIRES_SECONDS",
                3600,
            ),
        )

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    def login(
        self,
        request: LoginRequest,
    ) -> LoginResponse:

        with UnitOfWork() as uow:

            user = self.repository.find_by_email(
                request.email
            )

            if (
                user is None
                or not user.is_active
                or not user.team_member.is_active
            ):
                logger.warning(
                    "Invalid login for %s",
                    request.email,
                )
                raise AuthenticationException()

            locked_until_utc = user.locked_until
            if locked_until_utc and locked_until_utc.tzinfo is None:
                locked_until_utc = locked_until_utc.replace(tzinfo=timezone.utc)

            if (
                locked_until_utc
                and locked_until_utc > current_utc_time()
            ):
                raise AuthenticationException(
                    "Account locked.",
                    code="ERR_ACCOUNT_LOCKED",
                )

            # Verify password against bcrypt or werkzeug hashes
            is_valid_password = False
            if user.password_hash:
                if user.password_hash.startswith("scrypt:") or user.password_hash.startswith("pbkdf2:"):
                    is_valid_password = werkzeug_check_password_hash(user.password_hash, request.password)
                    if is_valid_password:
                        # Auto-upgrade hash to bcrypt format
                        user.password_hash = bcrypt.generate_password_hash(request.password).decode("utf-8")
                else:
                    try:
                        is_valid_password = bcrypt.check_password_hash(user.password_hash, request.password)
                    except Exception:
                        is_valid_password = werkzeug_check_password_hash(user.password_hash, request.password)

            if not is_valid_password:
                user.failed_login_attempts += 1
                max_attempts = current_app.config.get("MAX_LOGIN_ATTEMPTS", 5)

                if user.failed_login_attempts >= max_attempts:
                    lock_duration = current_app.config.get(
                        "ACCOUNT_LOCK_DURATION", timedelta(minutes=30)
                    )
                    user.locked_until = current_utc_time() + lock_duration

                uow.commit()

                raise AuthenticationException()

            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login_at = current_utc_time()

            session = self._create_session(user)

            uow.commit()

            logger.info(
                "User %s logged in successfully.",
                request.email,
            )

            return LoginResponse(
                session=session,
                user=self.mapper.to_user_summary(
                    user,
                    user.team_member,
                ),
            )

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------

    def logout(
        self,
        user_id: str,
        request: LogoutRequest,
    ):

        if not request.refresh_token:
            return

        with UnitOfWork() as uow:

            revoked = self.repository.revoke_refresh_token(
                self._hash_token(
                    request.refresh_token
                )
            )

            uow.commit()

            logger.info(
                "User %s logged out.",
                user_id,
            )

            return revoked

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    def refresh_token(
        self,
        request: RefreshTokenRequest,
    ) -> SessionDTO:

        try:
            decoded = decode_token(
                request.refresh_token
            )

        except Exception:
            raise AuthenticationException(
                "Invalid refresh token.",
                code="ERR_INVALID_TOKEN",
            )

        token_hash = self._hash_token(
            request.refresh_token
        )

        with UnitOfWork() as uow:

            db_token = self.repository.find_refresh_token(
                token_hash
            )

            if db_token is None:
                raise AuthenticationException(
                    "Refresh token expired.",
                    code="ERR_REFRESH_TOKEN_EXPIRED",
                )

            user = self.repository.find_active_user(
                decoded["sub"]
            )

            if user is None:
                raise AuthenticationException(
                    "Account disabled.",
                    code="ERR_ACCOUNT_DISABLED",
                )

            self.repository.revoke_refresh_token(
                token_hash
            )

            session = self._create_session(user)

            uow.commit()

            logger.info(
                "Refresh token rotated for %s",
                user.id,
            )

            return session

    # ------------------------------------------------------------------
    # Change Password
    # ------------------------------------------------------------------

    def change_password(
        self,
        user_id: str,
        request: ChangePasswordRequest,
    ):

        with UnitOfWork() as uow:

            user = self.repository.find_active_user(
                user_id
            )

            if user is None:
                raise AuthorizationException(
                    "User not found."
                )

            if not bcrypt.check_password_hash(
                user.password_hash,
                request.current_password,
            ):
                raise ValidationException(
                    "Incorrect current password.",
                    code="ERR_PASSWORD_MISMATCH",
                )

            user.password_hash = bcrypt.generate_password_hash(
                request.new_password
            ).decode()

            user.last_password_change = (
                current_utc_time()
            )

            uow.commit()

            logger.info(
                "Password changed for %s",
                user.id,
            )

    # ------------------------------------------------------------------
    # Forgot Password
    # ------------------------------------------------------------------

    def forgot_password(
        self,
        request: ForgotPasswordRequest,
    ):
        with UnitOfWork() as uow:
            user = self.repository.find_by_email(request.email)
            if not user or not user.is_active:
                logger.info("Password reset requested for inactive or non-existent email: %s", request.email)
                return  # Return silently to prevent email enumeration

            reset_token = secrets.token_urlsafe(32)
            user.reset_token_hash = self._hash_token(reset_token)
            
            expiry_hours = current_app.config.get("PASSWORD_RESET_EXPIRY_HOURS", 24)
            user.reset_token_expires_at = current_utc_time() + timedelta(hours=expiry_hours)
            
            uow.commit()
            
            # Note: In a real app, send an email here with `reset_token`.
            logger.info("Generated password reset token for %s", request.email)

    # ------------------------------------------------------------------
    # Reset Password
    # ------------------------------------------------------------------

    def reset_password(
        self,
        request: ResetPasswordRequest,
    ):
        with UnitOfWork() as uow:
            token_hash = self._hash_token(request.token)
            
            # Needs a repository method to find user by reset token hash, or we just do it via repo
            user = self.repository.find_by_reset_token(token_hash)
            
            if not user or not user.is_active:
                raise ValidationException("Invalid or expired reset token.", code="ERR_INVALID_TOKEN")
                
            if user.reset_token_expires_at and user.reset_token_expires_at < current_utc_time():
                raise ValidationException("Reset token expired.", code="ERR_TOKEN_EXPIRED")
                
            user.password_hash = bcrypt.generate_password_hash(request.new_password).decode()
            user.last_password_change = current_utc_time()
            user.reset_token_hash = None
            user.reset_token_expires_at = None
            
            uow.commit()

        logger.info("Password reset completed for user %s", user.id)

    # ------------------------------------------------------------------
    # Current User
    # ------------------------------------------------------------------

    def get_current_user(
        self,
        user_id: str,
    ) -> CurrentUserResponse:

        user = self.repository.find_active_user(
            user_id
        )

        if user is None:
            raise AuthorizationException(
                "User not found."
            )

        return CurrentUserResponse(
            user=self.mapper.to_user_summary(
                user,
                user.team_member,
            ),
            permissions=self.mapper.to_permissions(
                user.team_member
            ),
        )

    # ------------------------------------------------------------------
    # Verify Token
    # ------------------------------------------------------------------

    def verify_token(
        self,
        user_id: str,
    ) -> VerifyTokenResponse:

        user = self.repository.find_active_user(
            user_id
        )

        if user is None:
            raise AuthenticationException(
                "Invalid token.",
                code="ERR_INVALID_TOKEN",
            )

        return VerifyTokenResponse(
            valid=True,
            expires_at=(current_utc_time() + timedelta(hours=1)).isoformat(),
            user_id=str(user.id),
            role=(
                user.team_member.role.name
                if user.team_member.role
                else "Team Member"
            ),
        )