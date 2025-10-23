"""
Application Configuration Management
Environment-based settings with validation and type safety - Pydantic v2 Compatible
"""

import os
from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings with environment variable support and validation
    """

    # ===== APPLICATION METADATA =====
    APP_NAME: str = "FPL Optimizer Api"
    API_VERSION: str = "1.0.0"
    DESCRIPTION: str = "REST API for Fantasy Premier League team optimization"

    # ===== ENVIRONMENT CONFIGURATION =====
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=False, description="Enable debug mode")

    # ===== SERVER CONFIGURATION =====
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, ge=1000, le=65535, description="Server port")
    WORKERS: int = Field(default=1, ge=1, le=10, description="Number of worker processes")

    # ===== LOGGING CONFIGURATION =====
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="structured", description="Log format: simple, structured, json")
    ENABLE_ACCESS_LOGS: bool = Field(default=True, description="Enable HTTP access logs")

    # ===== CORS CONFIGURATION =====
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:4200"],
        description="CORS allowed origins"
    )
    ALLOWED_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="CORS allowed methods"
    )

    # ===== REPOSITORY CONFIGURATION =====
    PLAYER_REPOSITORY_TYPE: str = Field(
        default="fpl",
        description="Repository type: fpl, mock, database, cached"
    )

    # ===== FPL API CONFIGURATION =====
    FPL_API_URL: str = Field(
        default="https://fantasy.premierleague.com/api",
        description="FPL API base URL"
    )
    FPL_TIMEOUT: int = Field(default=30, ge=5, le=120, description="FPL API timeout in seconds")
    FPL_RETRY_ATTEMPTS: int = Field(default=3, ge=1, le=5, description="FPL API retry attempts")
    FPL_BACKOFF_FACTOR: float = Field(default=1.0, ge=0.1, le=5.0, description="Retry backoff factor")

    # ===== CACHING CONFIGURATION =====
    CACHE_ENABLED: bool = Field(default=True, description="Enable caching")
    CACHE_TYPE: str = Field(default="memory", description="Cache type: memory, redis")
    FPL_CACHE_TTL: int = Field(default=3600, ge=60, le=86400, description="FPL cache TTL in seconds")
    REDIS_URL: Optional[str] = Field(default=None, description="Redis connection URL")

    # ===== DATABASE CONFIGURATION (Optional) =====
    DATABASE_URL: Optional[str] = Field(default=None, description="Database connection URL")
    DATABASE_POOL_SIZE: int = Field(default=5, ge=1, le=20, description="Database connection pool size")

    # ===== SECURITY CONFIGURATION =====
    SECRET_KEY: Optional[str] = Field(default=None, description="Application secret key")
    API_KEY_HEADER: str = Field(default="X-API-Key", description="API key header name")

    # ===== HEALTH CHECK CONFIGURATION =====
    HEALTH_CHECK_ENABLED: bool = Field(default=True, description="Enable health checks")
    HEALTH_RESPONSE_TIME_THRESHOLD: int = Field(
        default=5000,
        ge=100,
        le=30000,
        description="Health check response time threshold in ms"
    )
    HEALTH_CACHE_STALENESS_THRESHOLD: int = Field(
        default=2,
        ge=1,
        description="Cache staleness threshold in hours"
    )

    # ===== RATE LIMITING CONFIGURATION =====
    RATE_LIMIT_ENABLED: bool = Field(default=False, description="Enable rate limiting")
    RATE_LIMIT_REQUESTS: int = Field(default=100, ge=10, description="Requests per minute")
    RATE_LIMIT_WINDOW: int = Field(default=60, ge=10, description="Rate limit window in seconds")

    # ===== DEVELOPMENT CONFIGURATION =====
    RELOAD: bool = Field(default=False, description="Enable auto-reload (development only)")
    RELOAD_DIRS: List[str] = Field(default=["app"], description="Directories to watch for reload")

    # ===== PYDANTIC V2 CONFIGURATION =====
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # ===== VALIDATORS =====

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v):
        valid_environments = ["development", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    @field_validator("PLAYER_REPOSITORY_TYPE")
    @classmethod
    def validate_repository_type(cls, v):
        valid_types = ["fpl", "mock", "database", "cached"]
        if v not in valid_types:
            raise ValueError(f"Repository type must be one of: {valid_types}")
        return v

    @field_validator("CACHE_TYPE")
    @classmethod
    def validate_cache_type(cls, v):
        valid_types = ["memory", "redis"]
        if v not in valid_types:
            raise ValueError(f"Cache type must be one of: {valid_types}")
        return v

    @field_validator("FPL_API_URL")
    @classmethod
    def validate_fpl_api_url(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("FPL API URL must start with http:// or https://")
        return v.rstrip("/")  # Remove trailing slash

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v, info):
        # In Pydantic v2, use info.data instead of values
        if info.data.get("ENVIRONMENT") == "production" and not v:
            raise ValueError("SECRET_KEY is required in production environment")
        return v

    # ===== COMPUTED PROPERTIES =====

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT == "development"

    @property
    def should_use_mock_data(self) -> bool:
        """Determine if mock data should be used"""
        return self.PLAYER_REPOSITORY_TYPE == "mock" or (
                self.is_development and not self.FPL_API_URL.startswith("https://fantasy.premierleague.com")
        )

    @property
    def cache_enabled_with_redis(self) -> bool:
        """Check if caching is enabled with Redis"""
        return self.CACHE_ENABLED and self.CACHE_TYPE == "redis"

    @property
    def fpl_api_timeout_ms(self) -> int:
        """Get FPL API timeout in milliseconds"""
        return self.FPL_TIMEOUT * 1000


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings instance
    Uses LRU cache to avoid re-parsing environment variables
    """
    return Settings()