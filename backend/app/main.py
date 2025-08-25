"""
FPL Players Service - Main Application Entry Point
Professional REST API with Clean Architecture and Repository Pattern
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.exceptions import FPLAPIException, PlayerNotFoundException
from app.api.v1.router import api_router


# ===== APPLICATION LIFECYCLE MANAGEMENT =====

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events
    """
    # Startup
    logger = logging.getLogger(__name__)
    logger.info("🚀 FPL Players Service starting up...")

    # Initialize any startup tasks here
    try:
        # You could add cache warming, health checks, etc.
        logger.info("✅ Application startup completed successfully")
        yield

    except Exception as e:
        logger.error(f"❌ Application startup failed: {str(e)}")
        raise

    finally:
        # Shutdown
        logger.info("🛑 FPL Players Service shutting down...")
        # Cleanup resources here (close HTTP sessions, database connections, etc.)
        logger.info("✅ Application shutdown completed")


# ===== APPLICATION SETUP =====

# Get application settings
settings = get_settings()

# Setup logging
setup_logging(settings.LOG_LEVEL)

# Create FastAPI application
app = FastAPI(
    title="FPL Players Service",
    description="""
    Professional REST API for Fantasy Premier League player data.

    ## Features
    - 🔥 **Live FPL Data**: Real-time data from official FPL API
    - ⚡ **Smart Caching**: Optimized performance with intelligent caching
    - 🎯 **Advanced Filtering**: Comprehensive player filtering and search
    - 🏗️ **Clean Architecture**: Repository pattern with SOLID principles
    - 🧪 **Fully Tested**: Comprehensive test coverage
    - 🐳 **Docker Ready**: Containerized for easy deployment

    ## Data Sources
    All player data is sourced from the official Fantasy Premier League API at
    fantasy.premierleague.com, ensuring accuracy and real-time updates.
    """,
    version=settings.API_VERSION,
    contact={
        "name": "FPL Players API",
        "url": "https://github.com/your-repo/fpl-players-service",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    # Custom OpenAPI configuration
    openapi_tags=[
        {
            "name": "players",
            "description": "Player data operations with live FPL integration",
        },
        {
            "name": "health",
            "description": "Health checks and system status",
        },
    ]
)

# ===== MIDDLEWARE CONFIGURATION =====

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Cache-Status"],
)


# ===== GLOBAL EXCEPTION HANDLERS =====

@app.exception_handler(FPLAPIException)
async def fpl_api_exception_handler(request, exc: FPLAPIException):
    """Handle FPL API specific exceptions"""
    logger = logging.getLogger(__name__)
    logger.error(f"FPL API Error: {exc.message} - {exc.details}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.message,
            "details": exc.details,
            "error_type": "FPL_API_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(PlayerNotFoundException)
async def player_not_found_exception_handler(request, exc: PlayerNotFoundException):
    """Handle player not found exceptions"""
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": f"Player with ID {exc.player_id} not found",
            "error_type": "PLAYER_NOT_FOUND",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle general HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "error_type": "HTTP_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions"""
    logger = logging.getLogger(__name__)
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)

    # Don't expose internal errors in production
    if settings.DEBUG:
        error_detail = str(exc)
    else:
        error_detail = "An internal server error occurred"

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": error_detail,
            "error_type": "INTERNAL_SERVER_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ===== API ROUTER INCLUSION =====

# Include API v1 router
app.include_router(
    api_router,
    prefix="/api/v1",
    tags=["v1"]
)


# ===== ROOT ENDPOINTS =====

@app.get("/", tags=["root"])
async def root() -> Dict[str, Any]:
    """
    Root endpoint with API information
    """
    return {
        "message": "FPL Players Service API",
        "version": settings.API_VERSION,
        "description": "Professional REST API for Fantasy Premier League player data",
        "documentation": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "api_v1": "/api/v1",
        "features": [
            "Live FPL data integration",
            "Smart caching for performance",
            "Advanced filtering and search",
            "Clean architecture with repository pattern",
            "Comprehensive error handling",
            "Full OpenAPI documentation"
        ],
        "endpoints": {
            "players": "/api/v1/players",
            "player_by_id": "/api/v1/players/{id}",
            "refresh_data": "/api/v1/players/refresh",
            "health": "/health"
        }
    }


@app.get("/health", tags=["health"])
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint

    This is a simple health check that doesn't test external dependencies.
    For more comprehensive health checks including FPL API connectivity,
    use /api/v1/health endpoint.
    """
    return {
        "status": "healthy",
        "service": "FPL Players Service",
        "version": settings.API_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "debug_mode": settings.DEBUG
    }


# ===== MIDDLEWARE FOR REQUEST/RESPONSE LOGGING =====

@app.middleware("http")
async def log_requests(request, call_next):
    """
    Middleware to log requests and responses
    """
    logger = logging.getLogger("api.requests")

    # Log request
    start_time = datetime.utcnow()
    logger.info(f"Request: {request.method} {request.url}")

    # Process request
    response = await call_next(request)

    # Log response
    process_time = (datetime.utcnow() - start_time).total_seconds()
    logger.info(
        f"Response: {response.status_code} - {process_time:.3f}s - {request.method} {request.url}"
    )

    # Add custom headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-API-Version"] = settings.API_VERSION

    return response


# ===== APPLICATION METADATA =====

def get_application_info() -> Dict[str, Any]:
    """Get comprehensive application information"""
    return {
        "name": "FPL Players Service",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "architecture": {
            "pattern": "Clean Architecture with Repository Pattern",
            "layers": [
                "API Layer (FastAPI controllers)",
                "Business Logic Layer (Services)",
                "Repository Layer (Data access)",
                "Domain Layer (Entities and interfaces)"
            ],
            "data_source": "Official FPL API (fantasy.premierleague.com)",
            "caching": "In-memory with configurable TTL",
            "error_handling": "Comprehensive with custom exceptions"
        },
        "features": {
            "live_data": "Real-time FPL player data",
            "filtering": "Advanced player filtering and search",
            "caching": "Smart caching for optimal performance",
            "testing": "Comprehensive test suite with mocks",
            "documentation": "Full OpenAPI/Swagger documentation",
            "docker": "Container ready with docker-compose",
            "monitoring": "Health checks and request logging"
        }
    }


# ===== DEVELOPMENT HELPERS =====

if settings.DEBUG:
    @app.get("/debug/info", tags=["debug"], include_in_schema=False)
    async def debug_info():
        """Debug endpoint - only available in development"""
        return get_application_info()


    @app.get("/debug/settings", tags=["debug"], include_in_schema=False)
    async def debug_settings():
        """Debug endpoint to view current settings"""
        return {
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "log_level": settings.LOG_LEVEL,
            "api_version": settings.API_VERSION,
            "repository_type": getattr(settings, 'PLAYER_REPOSITORY_TYPE', 'fpl'),
            "fpl_api_url": getattr(settings, 'FPL_API_URL', 'default'),
            "cache_ttl": getattr(settings, 'FPL_CACHE_TTL', 3600),
        }

# ===== APPLICATION ENTRY POINT =====

if __name__ == "__main__":
    import uvicorn

    # Setup logging for direct execution
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Starting FPL Players Service in {settings.ENVIRONMENT} mode")

    # Run the application
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        reload_dirs=["app"] if settings.DEBUG else None,
    )