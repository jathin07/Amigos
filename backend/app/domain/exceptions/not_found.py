from .base import BaseDomainException

class NotFoundException(BaseDomainException):
    def __init__(self, message="Resource not found", code="ERR_NOT_FOUND", details=None):
        super().__init__(message, code, details)
