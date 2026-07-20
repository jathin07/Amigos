class BaseDomainException(Exception):
    def __init__(self, message, code="ERR_UNKNOWN", details=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

class ValidationException(BaseDomainException):
    def __init__(self, message="Validation failed", code="ERR_VALIDATION", details=None, validation_errors=None):
        super().__init__(message, code, details)
        self.validation_errors = validation_errors or []

class DomainException(BaseDomainException):
    def __init__(self, message, code="ERR_DOMAIN", details=None):
        super().__init__(message, code, details)

class AuthorizationException(BaseDomainException):
    def __init__(self, message="Not authorized", code="AUTH_FORBIDDEN", details=None):
        super().__init__(message, code, details)

class InfrastructureException(BaseDomainException):
    def __init__(self, message="Infrastructure error", code="ERR_INFRASTRUCTURE", details=None):
        super().__init__(message, code, details)
