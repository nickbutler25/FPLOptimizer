"""
Core Application Exceptions
Centralized exception hierarchy with structured error handling
"""

from typing import Dict, Any, Optional, List
from datetime import datetime


class BaseApplicationException(Exception):
    """
    Base exception for all application-specific exceptions
    """

    def __init__(
        self,
        message: str,
        error_code: str = None,
        details: str = None,
        context: Dict[str, Any] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details
        self.context = context or {}
        self.timestamp = datetime.utcnow().isoformat()

        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        result = {
            "error_type": self.error_code,
            "message": self.message,
            "timestamp": self.timestamp
        }

        if self.details:
            result["details"] = self.details

        if self.context:
            result["context"] = self.context

        return result


class ValidationError(BaseApplicationException):
    """
    Business validation error with field-level details
    """

    def __init__(
        self,
        message: str,
        field: str = None,
        details: str = None,
        field_errors: List[Dict[str, Any]] = None
    ):
        self.field = field
        self.field_errors = field_errors or []

        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details
        )

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()

        if self.field:
            result["field"] = self.field

        if self.field_errors:
            result["field_errors"] = self.field_errors

        return result


class FPLAPIException(BaseApplicationException):
    """
    Exception for FPL API related errors
    """

    def __init__(
        self,
        message: str,
        status_code: int = None,
        response_data: Dict[str, Any] = None,
        details: str = None
    ):
        self.status_code = status_code
        self.response_data = response_data

        super().__init__(
            message=message,
            error_code="FPL_API_ERROR",
            details=details,
            context={
                "status_code": status_code,
                "response_data": response_data
            }
        )


class PlayerNotFoundException(BaseApplicationException):
    """
    Exception for when a player is not found
    """

    def __init__(self, player_id: int):
        self.player_id = player_id

        super().__init__(
            message=f"Player with ID {player_id} not found",
            error_code="PLAYER_NOT_FOUND",
            context={"player_id": player_id}
        )


class RepositoryException(BaseApplicationException):
    """
    Exception for repository layer errors
    """

    def __init__(self, message: str, repository_type: str = None, operation: str = None):
        self.repository_type = repository_type
        self.operation = operation

        super().__init__(
            message=message,
            error_code="REPOSITORY_ERROR",
            context={
                "repository_type": repository_type,
                "operation": operation
            }
        )


class HealthCheckException(BaseApplicationException):
    """
    Exception for health check system failures
    """

    def __init__(self, message: str, component: str = None, check_type: str = None):
        self.component = component
        self.check_type = check_type

        super().__init__(
            message=message,
            error_code="HEALTH_CHECK_ERROR",
            context={
                "component": component,
                "check_type": check_type
            }
        )


class CacheException(BaseApplicationException):
    """
    Exception for caching system errors
    """

    def __init__(self, message: str, cache_type: str = None, operation: str = None):
        self.cache_type = cache_type
        self.operation = operation

        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            context={
                "cache_type": cache_type,
                "operation": operation
            }
        )


class ConfigurationException(BaseApplicationException):
    """
    Exception for configuration errors
    """

    def __init__(self, message: str, setting_name: str = None, setting_value: Any = None):
        self.setting_name = setting_name
        self.setting_value = setting_value

        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            context={
                "setting_name": setting_name,
                "setting_value": str(setting_value) if setting_value is not None else None
            }
        )