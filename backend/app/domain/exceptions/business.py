from .base import BaseDomainException

class DomainException(BaseDomainException):
    def __init__(self, message, code="ERR_DOMAIN", details=None):
        super().__init__(message, code, details)

class BusinessException(BaseDomainException):
    def __init__(self, message, code="ERR_BUSINESS", details=None):
        super().__init__(message, code, details)
