from .base import BaseDomainException

class AuthorizationException(BaseDomainException):
    def __init__(self, message="Not authorized", code="AUTH_FORBIDDEN", details=None):
        super().__init__(message, code, details)

class AuthenticationException(BaseDomainException):
    def __init__(self, message="Authentication failed", code="ERR_UNAUTHORIZED", details=None):
        super().__init__(message, code, details)
