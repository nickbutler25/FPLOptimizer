"""
API-specific exceptions and error handling
"""

from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status


class APIException(HTTPException):
    """Base API exception with enhanced error information"""

    def __init__(
            self,
            status_code: int,
            message: str,
            details: Optional[str] = None,
            error_code: Optional[str] = None,
            headers: Optional[Dict[str, str]] = None
    ):
        self.message = message
        self.details = details
        self.error_code = error_code

        super().__init__(
            status_code=status_code,
            detail=self._format_error(),
            headers=headers
        )

    def _format_error(self) -> Dict[str, Any]:
        """Format error for API response"""
        error_response = {
            "message": self.message,
            "error_code": self.error_code or "API_ERROR"
        }

        if self.details:
            error_response["details"] = self.details

        return error_response


class ValidationException(APIException):
    """Exception for validation errors"""

    def __init__(
            self,
            message: str = "Validation failed",
            field_errors: Optional[List[Dict[str, Any]]] = None,
            details: Optional[str] = None
    ):
        self.field_errors = field_errors or []

        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            details=details,
            error_code="VALIDATION_ERROR"
        )

    def _format_error(self) -> Dict[str, Any]:
        error_response = super()._format_error()
        if self.field_errors:
            error_response["field_errors"] = self.field_errors
        return error_response


class ServiceUnavailableException(APIException):
    """Exception for when external services are unavailable"""

    def __init__(
            self,
            service_name: str,
            message: Optional[str] = None,
            details: Optional[str] = None
    ):
        default_message = f"{service_name} is currently unavailable"

        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message=message or default_message,
            details=details,
            error_code="SERVICE_UNAVAILABLE"
        )
