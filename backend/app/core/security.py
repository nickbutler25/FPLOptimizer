"""
Security Utilities and Configuration
Authentication, authorization, and security helpers
"""

import secrets
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.config import get_settings


def generate_secret_key(length: int = 32) -> str:
    """
    Generate a cryptographically secure secret key

    Args:
        length: Length of the secret key in bytes

    Returns:
        Base64 encoded secret key
    """
    return secrets.token_urlsafe(length)


def hash_string(value: str, salt: str = None) -> str:
    """
    Hash a string value with optional salt

    Args:
        value: String to hash
        salt: Optional salt value

    Returns:
        Hexadecimal hash string
    """
    if salt:
        value = f"{value}{salt}"

    return hashlib.sha256(value.encode()).hexdigest()


def generate_request_id() -> str:
    """
    Generate a unique request ID

    Returns:
        Unique request identifier
    """
    return secrets.token_hex(8)


def is_safe_url(url: str, allowed_hosts: list = None) -> bool:
    """
    Check if a URL is safe for redirects

    Args:
        url: URL to validate
        allowed_hosts: List of allowed hostnames

    Returns:
        True if URL is safe
    """
    if not url:
        return False

    # Add basic URL validation logic here
    # This is a simplified example
    return not url.startswith(('javascript:', 'data:', 'vbscript:'))


def get_cors_settings() -> Dict[str, Any]:
    """
    Get CORS settings from configuration

    Returns:
        CORS configuration dictionary
    """
    settings = get_settings()

    return {
        "allow_origins": settings.ALLOWED_ORIGINS,
        "allow_methods": settings.ALLOWED_METHODS,
        "allow_headers": ["*"],
        "allow_credentials": True,
        "expose_headers": ["X-Request-ID", "X-Process-Time", "X-API-Version"]
    }

