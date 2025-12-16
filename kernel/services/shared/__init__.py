"""
SAHOOL Shared Service Utilities
أدوات مشتركة للخدمات
"""

from .cors_config import CORS_SETTINGS, get_allowed_origins, get_cors_middleware_config

__all__ = ["CORS_SETTINGS", "get_allowed_origins", "get_cors_middleware_config"]
