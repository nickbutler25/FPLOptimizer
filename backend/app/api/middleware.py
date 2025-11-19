"""API middleware for request/response processing."""

import time
import logging
from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import FPLOptimizerException
from app.schemas.responses import ErrorResponse, ErrorDetail

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details.

        Args:
            request: Incoming request
            call_next: Next middleware/endpoint

        Returns:
            Response from endpoint
        """
        # Start timer
        start_time = time.time()

        # Get request details
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"

        # Log request
        logger.info(f"Request: {method} {path} from {client_ip}")

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"Response: {method} {path} - Status: {response.status_code} - "
            f"Duration: {duration:.3f}s"
        )

        # Add custom headers
        response.headers["X-Process-Time"] = str(duration)

        # Disable caching for API responses
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling exceptions globally."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle exceptions and format error responses.

        Args:
            request: Incoming request
            call_next: Next middleware/endpoint

        Returns:
            Response or error response
        """
        try:
            return await call_next(request)
        except FPLOptimizerException as e:
            # Handle custom application exceptions
            logger.error(f"Application error: {e.message}", exc_info=True)
            return JSONResponse(
                status_code=e.status_code,
                content=ErrorResponse(
                    success=False,
                    message=e.message,
                    errors=[ErrorDetail(message=e.message, type=type(e).__name__)],
                ).model_dump(),
            )
        except Exception as e:
            # Handle unexpected exceptions
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    success=False,
                    message="An unexpected error occurred",
                    errors=[ErrorDetail(message=str(e), type="InternalServerError")],
                ).model_dump(),
            )


class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response.

        Args:
            request: Incoming request
            call_next: Next middleware/endpoint

        Returns:
            Response with security headers
        """
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
