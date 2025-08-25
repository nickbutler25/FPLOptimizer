"""
Core Middleware Components
Request processing, logging, and cross-cutting concerns
"""

import time
import uuid
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging

from app.core.config import get_settings


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add request context and tracking
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Add to request state
        request.state.request_id = request_id
        request.state.start_time = time.time()

        # Process request
        response = await call_next(request)

        # Add response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{time.time() - request.state.start_time:.4f}"

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for structured request/response logging
    """

    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("api.requests")
        self.settings = get_settings()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Log request
        if self.settings.ENABLE_ACCESS_LOGS:
            self.logger.info(
                "Request started",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "user_agent": request.headers.get("user-agent"),
                    "request_id": getattr(request.state, "request_id", "unknown")
                }
            )

        # Process request
        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        if self.settings.ENABLE_ACCESS_LOGS:
            self.logger.info(
                "Request completed",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "process_time": f"{process_time:.4f}s",
                    "request_id": getattr(request.state, "request_id", "unknown")
                }
            )

        return response