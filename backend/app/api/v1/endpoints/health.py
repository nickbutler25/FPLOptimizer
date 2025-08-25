"""
Health Check API Endpoints - Refactored with Clean Architecture
Minimal HTTP concerns, delegates health checking to business service
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import logging

from app.api.dependencies import HealthServiceDep
from app.schemas.responses.health import HealthResponseDTO, StatusResponseDTO
from app.core.exceptions import FPLAPIException, HealthCheckException

# Create router
router = APIRouter()

# Setup logging
logger = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=HealthResponseDTO,
    summary="Comprehensive health check",
    description="""
    **Comprehensive health check** including external dependencies.

    **Checks performed:**
    - Application status and configuration
    - FPL API connectivity and response time
    - Cache status and data freshness
    - Repository health and data availability
    - System resource information

    **Use cases:**
    - Load balancer health checks
    - Monitoring and alerting systems
    - DevOps health verification
    - Debugging connectivity issues

    **Response codes:**
    - `200`: All systems healthy
    - `503`: System degraded (some components unhealthy)
    - `500`: Critical system failure
    """,
    responses={
        200: {
            "description": "All systems healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "service": "FPL Players Service",
                        "version": "1.0.0",
                        "fpl_api_status": "connected",
                        "cache_status": "valid",
                        "data_freshness": "fresh",
                        "response_time_ms": 250
                    }
                }
            }
        },
        503: {
            "description": "System degraded or unhealthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "degraded",
                        "fpl_api_status": "disconnected",
                        "error": "FPL API timeout",
                        "cache_status": "stale"
                    }
                }
            }
        }
    },
    tags=["health"]
)
async def comprehensive_health_check(service: HealthServiceDep) -> HealthResponseDTO:
    """
    **API Layer**: Minimal HTTP handling, delegates to health service for all business logic
    """
    try:
        logger.debug("API: Performing comprehensive health check")

        # Delegate ALL health checking logic to business service
        health_info = await service.get_comprehensive_health()

        # Business service determines overall health status
        overall_status = health_info.get("status", "unknown")

        if overall_status == "healthy":
            logger.info("API: Health check passed - all systems operational")
            return health_info

        elif overall_status == "degraded":
            logger.warning("API: Health check degraded - some systems unavailable")
            # Return 503 for degraded state but include details
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=health_info
            )

        else:
            # Unknown or unhealthy status
            logger.error(f"API: Health check failed with status: {overall_status}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=health_info
            )

    except HealthCheckException as e:
        # Business layer health check exceptions
        logger.error(f"API: Health check business error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "error_type": "HEALTH_CHECK_ERROR",
                "message": str(e),
                "timestamp": e.timestamp if hasattr(e, 'timestamp') else None
            }
        )

    except FPLAPIException as e:
        # FPL API specific errors
        logger.error(f"API: Health check FPL API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "error_type": "FPL_API_ERROR",
                "message": "FPL API connectivity check failed",
                "details": str(e)
            }
        )

    except Exception as e:
        # Unexpected errors
        logger.error(f"API: Unexpected health check error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "error_type": "INTERNAL_ERROR",
                "message": "Health check system failure"
            }
        )


@router.get(
    "/simple",
    summary="Simple health check",
    description="""
    **Simple health check** that only verifies the application is running.

    **Features:**
    - No external dependency testing
    - Fast response time (< 10ms typical)
    - Container-friendly for Docker health checks
    - Basic service information

    **Use cases:**
    - Container orchestrator health checks (Docker, Kubernetes)
    - Quick uptime monitoring
    - Load balancer basic checks
    - CI/CD pipeline verification

    **Always returns 200** unless the application is completely down.
    """,
    responses={
        200: {
            "description": "Application is running",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "service": "FPL Players Service",
                        "version": "1.0.0",
                        "environment": "production",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                }
            }
        }
    },
    tags=["health"]
)
async def simple_health_check() -> Dict[str, Any]:
    """
    **API Layer**: Simple health check with no external dependencies

    This endpoint doesn't call the business service since it's just
    returning static application information.
    """
    try:
        logger.debug("API: Performing simple health check")

        # Get basic application info from service
        # Note: We could inject HealthService here too, but for a truly
        # simple check, we can return static info to avoid any dependencies
        from app.core.config import get_settings
        from datetime import datetime

        settings = get_settings()

        response = {
            "status": "healthy",
            "service": "FPL Players Service",
            "version": settings.API_VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": datetime.utcnow().isoformat(),
            "check_type": "simple"
        }

        logger.debug("API: Simple health check completed successfully")
        return response

    except Exception as e:
        # Even simple health check can fail
        logger.error(f"API: Simple health check failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Simple health check failed",
                "error": str(e)
            }
        )


@router.get(
    "/status",
    response_model=StatusResponseDTO,
    summary="Detailed status information",
    description="""
    **Detailed status and configuration information** about the service.

    **Information provided:**
    - Application metadata and version
    - Environment and configuration details
    - Architecture and component information
    - Runtime statistics and metrics
    - Repository configuration
    - Cache configuration and status

    **Use cases:**
    - DevOps debugging and troubleshooting
    - Configuration verification
    - Architecture documentation
    - Performance monitoring setup
    - Integration testing verification

    **Note:** May include sensitive configuration in development mode.
    """,
    responses={
        200: {
            "description": "Status information returned",
            "content": {
                "application/json": {
                    "example": {
                        "service": "FPL Players Service",
                        "version": "1.0.0",
                        "environment": "production",
                        "architecture": {
                            "pattern": "Clean Architecture",
                            "layers": ["API", "Business", "Repository", "Domain"]
                        },
                        "configuration": {
                            "repository_type": "fpl",
                            "cache_ttl": 3600,
                            "fpl_api_url": "https://fantasy.premierleague.com/api/"
                        }
                    }
                }
            }
        }
    },
    tags=["health"]
)
async def get_detailed_status(service: HealthServiceDep) -> StatusResponseDTO:
    """
    **API Layer**: Get detailed status, delegates to business service
    """
    try:
        logger.debug("API: Getting detailed status information")

        # Delegate to business service for all status logic
        status_info = await service.get_detailed_status()

        logger.debug("API: Successfully retrieved detailed status")
        return status_info

    except Exception as e:
        logger.error(f"API: Error getting detailed status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_type": "STATUS_ERROR",
                "message": "Failed to retrieve status information",
                "details": str(e)
            }
        )


@router.get(
    "/ready",
    summary="Readiness probe",
    description="""
    **Kubernetes-style readiness probe** for container orchestration.

    **Checks:**
    - Application startup completed
    - External dependencies available (FPL API)
    - Service ready to accept traffic

    **Kubernetes integration:**
    ```yaml
    readinessProbe:
      httpGet:
        path: /api/v1/health/ready
        port: 8000
      initialDelaySeconds: 30
      periodSeconds: 10
    ```

    **Use cases:**
    - Kubernetes readiness probes
    - Load balancer traffic routing decisions
    - Blue/green deployment verification
    - Service mesh health checks
    """,
    responses={
        200: {"description": "Service ready to accept traffic"},
        503: {"description": "Service not ready"}
    },
    tags=["health"]
)
async def readiness_probe(service: HealthServiceDep) -> Dict[str, Any]:
    """
    **API Layer**: Readiness probe for orchestration systems
    """
    try:
        logger.debug("API: Performing readiness probe")

        # Delegate readiness logic to business service
        readiness_info = await service.check_readiness()

        is_ready = readiness_info.get("ready", False)

        if is_ready:
            logger.debug("API: Readiness probe passed")
            return readiness_info
        else:
            logger.warning("API: Readiness probe failed")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=readiness_info
            )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error(f"API: Readiness probe error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "ready": False,
                "error": "Readiness probe failed",
                "details": str(e)
            }
        )


@router.get(
    "/live",
    summary="Liveness probe",
    description="""
    **Kubernetes-style liveness probe** for container health.

    **Purpose:**
    - Verify application is alive and not deadlocked
    - Trigger container restart if unhealthy
    - Minimal overhead check

    **Kubernetes integration:**
    ```yaml
    livenessProbe:
      httpGet:
        path: /api/v1/health/live
        port: 8000
      initialDelaySeconds: 60
      periodSeconds: 30
      failureThreshold: 3
    ```

    **Note:** This should NOT check external dependencies.
    Only internal application health.
    """,
    responses={
        200: {"description": "Application is alive"},
        500: {"description": "Application is deadlocked or crashed"}
    },
    tags=["health"]
)
async def liveness_probe() -> Dict[str, Any]:
    """
    **API Layer**: Liveness probe - minimal dependency check
    """
    try:
        logger.debug("API: Performing liveness probe")

        # Minimal check - just verify application is responsive
        # No external dependencies or business service calls
        from datetime import datetime

        response = {
            "alive": True,
            "service": "FPL Players Service",
            "timestamp": datetime.utcnow().isoformat()
        }

        logger.debug("API: Liveness probe passed")
        return response

    except Exception as e:
        logger.error(f"API: Liveness probe failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "alive": False,
                "error": "Application liveness check failed"
            }
        )


# ===== OPTIONAL: Metrics endpoint for monitoring =====

@router.get(
    "/metrics",
    summary="Application metrics",
    description="""
    **Prometheus-compatible metrics** for monitoring and observability.

    **Metrics included:**
    - Request counts and response times
    - FPL API call statistics
    - Cache hit/miss ratios
    - Error rates and types
    - Business metrics (active players, etc.)

    **Integration:**
    ```yaml
    # prometheus.yml
    scrape_configs:
      - job_name: 'fpl-players-api'
        static_configs:
          - targets: ['fpl-api:8000']
        metrics_path: '/api/v1/health/metrics'
    ```
    """,
    responses={
        200: {"description": "Metrics in Prometheus format"}
    },
    tags=["health", "monitoring"]
)
async def get_metrics(service: HealthServiceDep) -> Dict[str, Any]:
    """
    **API Layer**: Get application metrics, delegates to service
    """
    try:
        logger.debug("API: Getting application metrics")

        # Delegate metrics collection to business service
        metrics = await service.get_metrics()

        return metrics

    except Exception as e:
        logger.error(f"API: Error getting metrics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to retrieve metrics",
                "details": str(e)
            }
        )