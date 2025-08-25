# ===== app/services/common/health_service.py =====

"""
Health Service Business Layer
Centralized health checking logic with comprehensive system validation
"""

import asyncio
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

from app.domain.interfaces.repositories import PlayerRepositoryInterface
from app.core.config import get_settings
from app.core.exceptions import HealthCheckException, FPLAPIException
from app.schemas.responses.health import (
    HealthResponseDTO,
    StatusResponseDTO,
    ReadinessResponseDTO,
    MetricsResponseDTO
)


class HealthService:
    """
    Business layer service for health checking and system status

    Responsibilities:
    - Validate system health and external dependencies
    - Monitor application performance and resource usage
    - Provide detailed status and configuration information
    - Generate metrics for monitoring systems
    - Determine service readiness and liveness
    """

    def __init__(self, repository: PlayerRepositoryInterface):
        self.repository = repository
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)

        # Health check thresholds (configurable)
        self.response_time_threshold_ms = getattr(self.settings, 'HEALTH_RESPONSE_TIME_THRESHOLD', 5000)
        self.cache_staleness_threshold_hours = getattr(self.settings, 'HEALTH_CACHE_STALENESS_THRESHOLD', 2)

        # Internal metrics tracking
        self._health_check_count = 0
        self._last_successful_fpl_check = None
        self._last_health_check_duration = None

    async def get_comprehensive_health(self) -> HealthResponseDTO:
        """
        **Business Logic**: Perform comprehensive health check including external dependencies

        Checks performed:
        1. Application basic health
        2. FPL API connectivity and response time
        3. Repository health and data availability
        4. Cache status and data freshness
        5. System resource utilization
        """
        start_time = time.time()

        try:
            self.logger.info("Business: Starting comprehensive health check")
            self._health_check_count += 1

            # Collect all health information
            health_data = {}

            # 1. Basic application health
            app_health = await self._check_application_health()
            health_data.update(app_health)

            # 2. FPL API connectivity (critical external dependency)
            fpl_health = await self._check_fpl_api_health()
            health_data.update(fpl_health)

            # 3. Repository health and data availability
            repository_health = await self._check_repository_health()
            health_data.update(repository_health)

            # 4. Cache status and data freshness
            cache_health = await self._check_cache_health()
            health_data.update(cache_health)

            # 5. System resources (optional, for monitoring)
            if getattr(self.settings, 'INCLUDE_SYSTEM_METRICS', True):
                system_health = self._check_system_health()
                health_data.update(system_health)

            # Calculate overall health status
            overall_status = self._determine_overall_health_status(health_data)
            health_data["status"] = overall_status

            # Record metrics
            duration_ms = (time.time() - start_time) * 1000
            self._last_health_check_duration = duration_ms
            health_data["health_check_duration_ms"] = round(duration_ms, 2)

            if overall_status == "healthy":
                self._last_successful_fpl_check = datetime.utcnow()
                self.logger.info(f"Business: Comprehensive health check passed in {duration_ms:.1f}ms")
            else:
                self.logger.warning(f"Business: Health check status: {overall_status}")

            return HealthResponseDTO(**health_data)

        except Exception as e:
            self.logger.error(f"Business: Health check failed: {str(e)}", exc_info=True)

            # Return degraded status with error information
            duration_ms = (time.time() - start_time) * 1000

            return HealthResponseDTO(
                status="unhealthy",
                service="FPL Players Service",
                version=self.settings.API_VERSION,
                timestamp=datetime.utcnow().isoformat(),
                error="Health check system failure",
                error_details=str(e),
                health_check_duration_ms=round(duration_ms, 2)
            )

    async def get_detailed_status(self) -> StatusResponseDTO:
        """
        **Business Logic**: Get comprehensive status and configuration information
        """
        try:
            self.logger.debug("Business: Gathering detailed status information")

            status_data = {
                # Application metadata
                "service": "FPL Players Service",
                "version": self.settings.API_VERSION,
                "environment": self.settings.ENVIRONMENT,
                "debug_mode": self.settings.DEBUG,
                "timestamp": datetime.utcnow().isoformat(),

                # Architecture information
                "architecture": {
                    "pattern": "Clean Architecture with Repository Pattern",
                    "layers": [
                        "API Layer (FastAPI controllers)",
                        "Business Logic Layer (Services)",
                        "Repository Layer (Data access)",
                        "Domain Layer (Entities and interfaces)"
                    ],
                    "design_principles": [
                        "SOLID Principles",
                        "Dependency Inversion",
                        "Separation of Concerns",
                        "Repository Pattern"
                    ]
                },

                # Configuration details
                "configuration": await self._get_configuration_info(),

                # Runtime information
                "runtime": await self._get_runtime_info(),

                # Health metrics
                "health_metrics": await self._get_health_metrics()
            }

            return StatusResponseDTO(**status_data)

        except Exception as e:
            self.logger.error(f"Business: Error getting detailed status: {str(e)}", exc_info=True)
            raise HealthCheckException(f"Failed to retrieve system status: {str(e)}")

    async def check_readiness(self) -> ReadinessResponseDTO:
        """
        **Business Logic**: Determine if service is ready to accept traffic

        Readiness criteria:
        1. Application startup completed
        2. External dependencies available (FPL API)
        3. Repository functional with data
        4. No critical errors in recent history
        """
        try:
            self.logger.debug("Business: Checking service readiness")

            readiness_checks = {}
            is_ready = True

            # 1. Check FPL API availability (critical for readiness)
            try:
                fpl_health = await self._check_fpl_api_health()
                fpl_connected = fpl_health.get("fpl_api_status") == "connected"
                readiness_checks["fpl_api_ready"] = fpl_connected

                if not fpl_connected:
                    is_ready = False

            except Exception as e:
                readiness_checks["fpl_api_ready"] = False
                readiness_checks["fpl_api_error"] = str(e)
                is_ready = False

            # 2. Check repository functionality
            try:
                repo_health = await self._check_repository_health()
                repo_functional = repo_health.get("repository_status") == "functional"
                readiness_checks["repository_ready"] = repo_functional

                if not repo_functional:
                    is_ready = False

            except Exception as e:
                readiness_checks["repository_ready"] = False
                readiness_checks["repository_error"] = str(e)
                is_ready = False

            # 3. Check data availability
            try:
                data_available = await self._check_data_availability()
                readiness_checks["data_available"] = data_available

                if not data_available:
                    is_ready = False

            except Exception as e:
                readiness_checks["data_available"] = False
                readiness_checks["data_error"] = str(e)
                is_ready = False

            # Compile readiness response
            readiness_data = {
                "ready": is_ready,
                "timestamp": datetime.utcnow().isoformat(),
                "checks": readiness_checks
            }

            if is_ready:
                self.logger.debug("Business: Service is ready to accept traffic")
            else:
                self.logger.warning(f"Business: Service not ready. Failed checks: {readiness_checks}")

            return ReadinessResponseDTO(**readiness_data)

        except Exception as e:
            self.logger.error(f"Business: Readiness check failed: {str(e)}", exc_info=True)
            return ReadinessResponseDTO(
                ready=False,
                timestamp=datetime.utcnow().isoformat(),
                error="Readiness check system failure",
                checks={"readiness_system": False}
            )

    async def get_metrics(self) -> MetricsResponseDTO:
        """
        **Business Logic**: Generate application metrics for monitoring systems
        """
        try:
            self.logger.debug("Business: Collecting application metrics")

            metrics = {
                "timestamp": datetime.utcnow().isoformat(),

                # Health check metrics
                "health": {
                    "total_checks": self._health_check_count,
                    "last_check_duration_ms": self._last_health_check_duration,
                    "last_successful_fpl_check": self._last_successful_fpl_check.isoformat()
                    if self._last_successful_fpl_check else None
                },

                # Repository metrics
                "repository": await self._get_repository_metrics(),

                # System metrics
                "system": self._get_system_metrics(),

                # Application metrics
                "application": {
                    "version": self.settings.API_VERSION,
                    "environment": self.settings.ENVIRONMENT,
                    "uptime_seconds": self._get_uptime_seconds()
                }
            }

            return MetricsResponseDTO(**metrics)

        except Exception as e:
            self.logger.error(f"Business: Error collecting metrics: {str(e)}", exc_info=True)
            raise HealthCheckException(f"Failed to collect metrics: {str(e)}")

    # ===== PRIVATE HELPER METHODS =====

    async def _check_application_health(self) -> Dict[str, Any]:
        """Check basic application health and metadata"""
        return {
            "service": "FPL Players Service",
            "version": self.settings.API_VERSION,
            "environment": self.settings.ENVIRONMENT,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _check_fpl_api_health(self) -> Dict[str, Any]:
        """Check FPL API connectivity and response time"""
        start_time = time.time()

        try:
            self.logger.debug("Business: Testing FPL API connectivity")

            # Use repository to test FPL API (repository encapsulates FPL API calls)
            health_info = await self.repository.health_check()

            response_time_ms = (time.time() - start_time) * 1000

            # Determine status based on repository health check
            if health_info.get("status") == "healthy":
                fpl_status = "connected"
            elif health_info.get("fpl_api") == "connected":
                fpl_status = "connected"
            else:
                fpl_status = "disconnected"

            return {
                "fpl_api_status": fpl_status,
                "fpl_response_time_ms": round(response_time_ms, 2),
                "fpl_api_healthy": fpl_status == "connected"
            }

        except FPLAPIException as e:
            response_time_ms = (time.time() - start_time) * 1000
            self.logger.warning(f"Business: FPL API health check failed: {e}")

            return {
                "fpl_api_status": "disconnected",
                "fpl_response_time_ms": round(response_time_ms, 2),
                "fpl_api_healthy": False,
                "fpl_api_error": str(e)
            }

        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            self.logger.error(f"Business: FPL API health check error: {e}")

            return {
                "fpl_api_status": "error",
                "fpl_response_time_ms": round(response_time_ms, 2),
                "fpl_api_healthy": False,
                "fpl_api_error": str(e)
            }

    async def _check_repository_health(self) -> Dict[str, Any]:
        """Check repository functionality and data access"""
        try:
            self.logger.debug("Business: Checking repository health")

            # Test repository functionality
            health_info = await self.repository.health_check()

            return {
                "repository_status": "functional" if health_info.get("status") == "healthy" else "degraded",
                "repository_type": self._get_repository_type(),
                "cached_players": health_info.get("cached_players", 0),
                "cache_status": health_info.get("cache_status", "unknown"),
                "last_refresh": health_info.get("last_refresh")
            }

        except Exception as e:
            self.logger.error(f"Business: Repository health check failed: {e}")
            return {
                "repository_status": "error",
                "repository_error": str(e)
            }

    async def _check_cache_health(self) -> Dict[str, Any]:
        """Check cache status and data freshness"""
        try:
            self.logger.debug("Business: Checking cache health")

            # Get cache information from repository
            health_info = await self.repository.health_check()

            cache_status = health_info.get("cache_status", "unknown")
            last_refresh = health_info.get("last_refresh")

            # Determine data freshness
            data_freshness = "unknown"
            if last_refresh:
                try:
                    last_refresh_dt = datetime.fromisoformat(last_refresh.replace('Z', '+00:00'))
                    age_hours = (datetime.utcnow() - last_refresh_dt.replace(tzinfo=None)).total_seconds() / 3600

                    if age_hours < 1:
                        data_freshness = "fresh"
                    elif age_hours < self.cache_staleness_threshold_hours:
                        data_freshness = "acceptable"
                    else:
                        data_freshness = "stale"

                except Exception:
                    data_freshness = "unknown"

            return {
                "cache_status": cache_status,
                "data_freshness": data_freshness,
                "last_cache_refresh": last_refresh
            }

        except Exception as e:
            self.logger.error(f"Business: Cache health check failed: {e}")
            return {
                "cache_status": "error",
                "cache_error": str(e)
            }

    def _check_system_health(self) -> Dict[str, Any]:
        """Check system resource utilization"""
        try:
            # Get system metrics using psutil
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                "system_cpu_percent": round(cpu_percent, 1),
                "system_memory_percent": round(memory.percent, 1),
                "system_disk_percent": round(disk.percent, 1),
                "system_healthy": (
                        cpu_percent < 90 and
                        memory.percent < 90 and
                        disk.percent < 90
                )
            }

        except Exception as e:
            self.logger.warning(f"Business: System health check failed: {e}")
            return {
                "system_healthy": False,
                "system_error": str(e)
            }

    def _determine_overall_health_status(self, health_data: Dict[str, Any]) -> str:
        """
        **Business Logic**: Determine overall health status based on component health
        """
        # Critical checks that determine overall health
        fpl_healthy = health_data.get("fpl_api_healthy", False)
        repository_functional = health_data.get("repository_status") == "functional"
        data_fresh = health_data.get("data_freshness") in ["fresh", "acceptable"]

        # Response time check
        response_time_ok = True
        if "fpl_response_time_ms" in health_data:
            response_time_ok = health_data["fpl_response_time_ms"] < self.response_time_threshold_ms

        # Determine status
        if fpl_healthy and repository_functional and data_fresh and response_time_ok:
            return "healthy"
        elif fpl_healthy and repository_functional:
            return "degraded"  # Some non-critical issues
        else:
            return "unhealthy"  # Critical issues

    async def _check_data_availability(self) -> bool:
        """Check if we have player data available"""
        try:
            count = await self.repository.count()
            return count > 0
        except Exception:
            return False

    async def _get_configuration_info(self) -> Dict[str, Any]:
        """Get sanitized configuration information"""
        config = {
            "repository_type": self._get_repository_type(),
            "cache_ttl_seconds": getattr(self.settings, 'FPL_CACHE_TTL', 3600),
            "api_timeout_seconds": getattr(self.settings, 'FPL_TIMEOUT', 30),
            "log_level": self.settings.LOG_LEVEL,
            "include_system_metrics": getattr(self.settings, 'INCLUDE_SYSTEM_METRICS', True)
        }

        # Add FPL API URL in development only
        if self.settings.DEBUG:
            config["fpl_api_url"] = getattr(self.settings, 'FPL_API_URL', 'default')

        return config

    async def _get_runtime_info(self) -> Dict[str, Any]:
        """Get runtime information"""
        return {
            "python_version": f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}.{psutil.sys.version_info.micro}",
            "process_id": psutil.os.getpid(),
            "uptime_seconds": self._get_uptime_seconds(),
            "memory_usage_mb": round(psutil.Process().memory_info().rss / 1024 / 1024, 1)
        }

    async def _get_health_metrics(self) -> Dict[str, Any]:
        """Get health-related metrics"""
        return {
            "total_health_checks": self._health_check_count,
            "last_check_duration_ms": self._last_health_check_duration,
            "last_successful_fpl_check": self._last_successful_fpl_check.isoformat()
            if self._last_successful_fpl_check else None
        }

    async def _get_repository_metrics(self) -> Dict[str, Any]:
        """Get repository-specific metrics"""
        try:
            health_info = await self.repository.health_check()
            return {
                "type": self._get_repository_type(),
                "cached_players": health_info.get("cached_players", 0),
                "cache_status": health_info.get("cache_status", "unknown")
            }
        except Exception:
            return {
                "type": self._get_repository_type(),
                "error": "Failed to get repository metrics"
            }

    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            return {
                "cpu_percent": round(psutil.cpu_percent(), 1),
                "memory_percent": round(psutil.virtual_memory().percent, 1),
                "disk_percent": round(psutil.disk_usage('/').percent, 1)
            }
        except Exception:
            return {"error": "Failed to get system metrics"}

    def _get_repository_type(self) -> str:
        """Get the type of repository being used"""
        return getattr(self.settings, 'PLAYER_REPOSITORY_TYPE', 'fpl')

    def _get_uptime_seconds(self) -> int:
        """Get application uptime in seconds"""
        try:
            return int(time.time() - psutil.Process().create_time())
        except Exception:
            return 0


# ===== HEALTH CHECK EXCEPTION =====

class HealthCheckException(Exception):
    """Exception for health check system failures"""

    def __init__(self, message: str, component: str = None):
        self.message = message
        self.component = component
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(message)