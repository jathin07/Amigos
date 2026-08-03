from .base import BaseDomainException

class ValidationException(BaseDomainException):
    def __init__(self, message="Validation failed", code="ERR_VALIDATION", details=None, validation_errors=None):
        super().__init__(message, code, details)
        self.validation_errors = validation_errors or []
