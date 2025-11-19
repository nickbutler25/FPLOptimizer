"""Main FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.container import container
from app.api.v1.router import api_router
from app.api.middleware import (
    LoggingMiddleware,
    ErrorHandlingMiddleware,
    CORSSecurityMiddleware,
)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events.

    Args:
        app: FastAPI application instance

    Yields:
        None
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")

    # Initialize Redis cache
    try:
        redis_cache = container.redis_cache()
        await redis_cache.connect()
        logger.info("Redis cache initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize Redis cache: {e}. Continuing without cache.")

    yield

    # Shutdown
    logger.info("Shutting down application")

    # Close Redis connection
    try:
        redis_cache = container.redis_cache()
        await redis_cache.disconnect()
        logger.info("Redis cache disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting Redis: {e}")

    # Close HTTP client
    try:
        http_client = container.http_client()
        await http_client.aclose()
        logger.info("HTTP client closed")
    except Exception as e:
        logger.error(f"Error closing HTTP client: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Professional FastAPI REST API for Fantasy Premier League data optimization",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(CORSSecurityMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)

# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint redirecting to docs."""
    return JSONResponse(
        content={
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "docs": "/docs",
            "health": f"{settings.api_v1_prefix}/health",
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
