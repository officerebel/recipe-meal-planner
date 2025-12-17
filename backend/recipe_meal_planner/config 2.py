"""
Configuration helpers for 12-Factor App compliance

This module provides utilities for loading configuration from environment variables
with proper type conversion and validation.
"""

import os
from typing import Any, List, Optional


def get_env_bool(key: str, default: bool = False) -> bool:
    """
    Get boolean value from environment variable.
    
    Accepts: true, 1, yes (case-insensitive) as True
    Everything else is False
    """
    value = os.environ.get(key, str(default))
    return value.lower() in ('true', '1', 'yes')


def get_env_list(key: str, default: str = '', separator: str = ',') -> List[str]:
    """
    Get list value from environment variable.
    
    Splits by separator and strips whitespace from each item.
    """
    value = os.environ.get(key, default)
    if not value:
        return []
    return [item.strip() for item in value.split(separator) if item.strip()]


def get_env_int(key: str, default: int = 0) -> int:
    """
    Get integer value from environment variable.
    
    Returns default if value cannot be converted to int.
    """
    value = os.environ.get(key, str(default))
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def get_env_str(key: str, default: str = '') -> str:
    """
    Get string value from environment variable.
    
    Simple wrapper for consistency.
    """
    return os.environ.get(key, default)


def require_env(key: str) -> str:
    """
    Get required environment variable.
    
    Raises ValueError if not set.
    """
    value = os.environ.get(key)
    if value is None:
        raise ValueError(f"Required environment variable '{key}' is not set")
    return value


def is_production() -> bool:
    """Check if running in production environment."""
    return 'RAILWAY_ENVIRONMENT' in os.environ or get_env_bool('PRODUCTION', False)


def is_development() -> bool:
    """Check if running in development environment."""
    return not is_production()


# Configuration validation
def validate_config():
    """
    Validate required configuration is present.
    
    Call this at startup to fail fast if config is missing.
    """
    errors = []
    
    # Check required settings in production
    if is_production():
        required_vars = ['SECRET_KEY', 'DATABASE_URL']
        for var in required_vars:
            if not os.environ.get(var):
                errors.append(f"Missing required environment variable: {var}")
    
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(errors))


# Example usage in settings.py:
# from recipe_meal_planner.config import get_env_bool, get_env_list, get_env_str
# 
# DEBUG = get_env_bool('DEBUG', default=True)
# ALLOWED_HOSTS = get_env_list('ALLOWED_HOSTS', default='localhost,127.0.0.1')
# SECRET_KEY = get_env_str('SECRET_KEY', default='dev-key-change-in-production')
