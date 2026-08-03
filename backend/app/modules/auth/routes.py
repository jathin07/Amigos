from __future__ import annotations

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from app.infrastructure.responses.responses import success_response
from app.modules.auth.permissions import login_required
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas.request import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
)
from app.modules.auth.service import AuthService
from app.modules.auth.validators import validate_request

auth_bp = Blueprint("auth", __name__)

repository = AuthRepository()
auth_service = AuthService(repository)


@auth_bp.post("/login")
def login():
    """Authenticate user."""

    request_dto = validate_request(
        LoginRequest,
        request.get_json(silent=True) or {},
    )

    response_dto = auth_service.login(request_dto)

    return success_response(data=response_dto.model_dump())


@auth_bp.post("/logout")
@login_required()
def logout():
    """Logout current user."""

    request_dto = validate_request(
        LogoutRequest,
        request.get_json(silent=True) or {},
    )

    auth_service.logout(
        get_jwt_identity(),
        request_dto,
    )

    return success_response(
        data={
            "message": "Logged out successfully."
        }
    )


@auth_bp.post("/refresh")
def refresh():
    """Refresh JWT."""

    request_dto = validate_request(
        RefreshTokenRequest,
        request.get_json(silent=True) or {},
    )

    response_dto = auth_service.refresh_token(
        request_dto
    )

    return success_response(
        data=response_dto.model_dump()
    )


@auth_bp.post("/forgot-password")
def forgot_password():
    """Request password reset."""

    request_dto = validate_request(
        ForgotPasswordRequest,
        request.get_json(silent=True) or {},
    )

    auth_service.forgot_password(request_dto)

    return success_response(
        data={
            "message":
            "Password reset link has been sent if the account exists."
        }
    )


@auth_bp.post("/reset-password")
def reset_password():
    """Reset password."""

    request_dto = validate_request(
        ResetPasswordRequest,
        request.get_json(silent=True) or {},
    )

    auth_service.reset_password(request_dto)

    return success_response(
        data={
            "message": "Password reset successfully."
        }
    )


@auth_bp.post("/change-password")
@login_required()
def change_password():
    """Change current user's password."""

    request_dto = validate_request(
        ChangePasswordRequest,
        request.get_json(silent=True) or {},
    )

    auth_service.change_password(
        get_jwt_identity(),
        request_dto,
    )

    return success_response(
        data={
            "message": "Password updated successfully."
        }
    )


@auth_bp.get("/me")
@login_required()
def me():
    """Return authenticated user."""

    response_dto = auth_service.get_current_user(
        get_jwt_identity()
    )

    return success_response(
        data=response_dto.model_dump()
    )


@auth_bp.get("/verify")
@login_required()
def verify():
    """
    Verify access token.
    """

    response_dto = auth_service.verify_token(
        get_jwt_identity()
    )

    return success_response(
        data=response_dto.model_dump()
    )