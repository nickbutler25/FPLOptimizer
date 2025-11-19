"""Custom application exceptions."""


class FPLOptimizerException(Exception):
    """Base exception for FPL Optimizer API."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(FPLOptimizerException):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationException(FPLOptimizerException):
    """Exception raised when validation fails."""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=422)


class ExternalAPIException(FPLOptimizerException):
    """Exception raised when external API call fails."""

    def __init__(self, message: str = "External API error"):
        super().__init__(message, status_code=502)


class CacheException(FPLOptimizerException):
    """Exception raised when cache operation fails."""

    def __init__(self, message: str = "Cache error"):
        super().__init__(message, status_code=500)


class AuthenticationException(FPLOptimizerException):
    """Exception raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationException(FPLOptimizerException):
    """Exception raised when authorization fails."""

    def __init__(self, message: str = "Authorization failed"):
        super().__init__(message, status_code=403)
