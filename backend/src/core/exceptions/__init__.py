class AppException(Exception):
    """Base exception for the application"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DatabaseError(AppException):
    """Database related errors"""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=500)


class NotFoundError(AppException):
    """Resource not found errors"""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(AppException):
    """Data validation errors"""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=400)
