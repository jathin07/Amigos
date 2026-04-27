class APIException(Exception):
    """Base class for API exceptions."""
    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        return rv


class ResourceNotFound(APIException):
    """Raised when a requested resource is not found."""
    def __init__(self, message="Resource not found"):
        super().__init__(message, status_code=404)


class ValidationException(APIException):
    """Raised when validation fails (e.g., from Marshmallow)."""
    def __init__(self, message="Validation error", payload=None):
        super().__init__(message, status_code=400, payload=payload)


class DatabaseException(APIException):
    """Raised when a database error occurs."""
    def __init__(self, message="A database error occurred"):
        super().__init__(message, status_code=500)


class Unauthorized(APIException):
    """Raised when a user is not authorized."""
    def __init__(self, message="Unauthorized"):
        super().__init__(message, status_code=401)


class Forbidden(APIException):
    """Raised when access is forbidden."""
    def __init__(self, message="Forbidden"):
        super().__init__(message, status_code=403)
