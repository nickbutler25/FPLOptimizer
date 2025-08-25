"""
Centralized Logging Configuration
Structured logging with environment-based configuration
"""

import logging
import logging.config
import sys
from typing import Dict, Any
from pythonjsonlogger import jsonlogger

from app.core.config import get_settings


def setup_logging(log_level: str = None) -> None:
    """
    Setup application logging with structured format

    Args:
        log_level: Override log level from settings
    """
    settings = get_settings()
    level = log_level or settings.LOG_LEVEL

    # Create logging configuration
    if settings.LOG_FORMAT == "json":
        logging_config = _get_json_logging_config(level)
    elif settings.LOG_FORMAT == "structured":
        logging_config = _get_structured_logging_config(level)
    else:
        logging_config = _get_simple_logging_config(level)

    # Apply logging configuration
    logging.config.dictConfig(logging_config)

    # Set specific logger levels
    _configure_third_party_loggers()

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured",
        extra={
            "log_level": level,
            "log_format": settings.LOG_FORMAT,
            "environment": settings.ENVIRONMENT
        }
    )


def _get_json_logging_config(level: str) -> Dict[str, Any]:
    """Get JSON structured logging configuration"""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": jsonlogger.JsonFormatter,
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": sys.stdout
            }
        },
        "root": {
            "level": level,
            "handlers": ["console"]
        }
    }


def _get_structured_logging_config(level: str) -> Dict[str, Any]:
    """Get structured logging configuration"""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structured": {
                "format": "%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "structured",
                "stream": sys.stdout
            }
        },
        "root": {
            "level": level,
            "handlers": ["console"]
        }
    }


def _get_simple_logging_config(level: str) -> Dict[str, Any]:
    """Get simple logging configuration"""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(levelname)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "stream": sys.stdout
            }
        },
        "root": {
            "level": level,
            "handlers": ["console"]
        }
    }


def _configure_third_party_loggers() -> None:
    """Configure third-party library loggers"""
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

    # Set specific loggers based on environment
    settings = get_settings()
    if settings.is_production:
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
    else:
        logging.getLogger("uvicorn").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get logger with consistent configuration

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)