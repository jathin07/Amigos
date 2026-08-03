class BaseDomainException(Exception):
    def __init__(self, message, code="ERR_UNKNOWN", details=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

class InfrastructureException(BaseDomainException):
    def __init__(self, message="Infrastructure error", code="ERR_INFRASTRUCTURE", details=None):
        super().__init__(message, code, details)
