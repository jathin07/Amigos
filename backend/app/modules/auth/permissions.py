from __future__ import annotations

from functools import wraps
from typing import Callable
from flask import current_app
from flask_jwt_extended import get_jwt, verify_jwt_in_request

from app.domain.exceptions import AuthorizationException


def _is_dev_mode() -> bool:
    """Check if app is running in development / debug mode."""
    try:
        return current_app.config.get("ENV") == "development" or current_app.config.get("DEBUG") or current_app.debug
    except Exception:
        return True


def login_required() -> Callable:
    """Ensure request contains valid JWT, or pass-through in dev mode if unauthenticated."""
    def wrapper(fn: Callable) -> Callable:
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request(optional=True)
            except Exception:
                pass
            if _is_dev_mode():
                return fn(*args, **kwargs)
            verify_jwt_in_request()
            return fn(*args, **kwargs)

        return decorator

    return wrapper


def role_required(*allowed_roles: str) -> Callable:
    """Allow access if user's role matches allowed roles or in dev mode."""
    def wrapper(fn: Callable) -> Callable:
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request(optional=True)
                claims = get_jwt() or {}
            except Exception:
                claims = {}

            if _is_dev_mode() and not claims:
                return fn(*args, **kwargs)

            user_role = claims.get("role")
            if not user_role and not _is_dev_mode():
                raise AuthorizationException("Role information missing from token.")

            if user_role and user_role not in allowed_roles and not _is_dev_mode():
                raise AuthorizationException(f"Access denied. Required role: {', '.join(allowed_roles)}.")

            return fn(*args, **kwargs)

        return decorator

    return wrapper


def permission_required(*required_permissions: str) -> Callable:
    """Allow access if user possesses required permissions or in dev mode."""
    def wrapper(fn: Callable) -> Callable:
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request(optional=True)
                claims = get_jwt() or {}
            except Exception:
                claims = {}

            # In development mode or unauthenticated dev testing, allow request
            if _is_dev_mode() and not claims:
                return fn(*args, **kwargs)

            user_permissions = set(claims.get("permissions", []))
            if "admin.full" in user_permissions:
                return fn(*args, **kwargs)

            missing_permissions = [
                permission for permission in required_permissions if permission not in user_permissions
            ]

            if missing_permissions:
                if claims or not _is_dev_mode():
                    raise AuthorizationException(
                        "Missing required permission(s): " + ", ".join(missing_permissions)
                    )

            return fn(*args, **kwargs)

        return decorator

    return wrapper