from __future__ import annotations

from functools import wraps
from typing import Callable

from flask_jwt_extended import get_jwt, verify_jwt_in_request

from app.domain.exceptions import AuthorizationException


def login_required() -> Callable:
    """
    Ensure the request contains a valid JWT.
    """

    def wrapper(fn: Callable) -> Callable:
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            return fn(*args, **kwargs)

        return decorator

    return wrapper


def role_required(*allowed_roles: str) -> Callable:
    """
    Allow access only if the user's role matches one of the allowed roles.

    Example:
        @role_required("Admin", "Manager")
    """

    def wrapper(fn: Callable) -> Callable:
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()

            claims = get_jwt()
            user_role = claims.get("role")

            if not user_role:
                raise AuthorizationException(
                    "Role information missing from token."
                )

            if user_role not in allowed_roles:
                raise AuthorizationException(
                    f"Access denied. Required role: {', '.join(allowed_roles)}."
                )

            return fn(*args, **kwargs)

        return decorator

    return wrapper


def permission_required(*required_permissions: str) -> Callable:
    """
    Allow access only if the user possesses all required permissions.

    'admin.full' bypasses all permission checks.
    """

    def wrapper(fn: Callable) -> Callable:
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()

            claims = get_jwt()

            user_permissions = set(
                claims.get("permissions", [])
            )

            # Super Admin shortcut
            if "admin.full" in user_permissions:
                return fn(*args, **kwargs)

            missing_permissions = [
                permission
                for permission in required_permissions
                if permission not in user_permissions
            ]

            if missing_permissions:
                raise AuthorizationException(
                    "Missing required permission(s): "
                    + ", ".join(missing_permissions)
                )

            return fn(*args, **kwargs)

        return decorator

    return wrapper