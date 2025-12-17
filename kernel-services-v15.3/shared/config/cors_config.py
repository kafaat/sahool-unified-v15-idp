"""
SAHOOL Platform - Centralized CORS Configuration
منصة سهول - تهيئة CORS المركزية

This module provides a centralized and secure CORS configuration
for all SAHOOL services to prevent security vulnerabilities.

Security: Never use wildcard (*) origins in production!
"""

import os
from typing import List


class CORSSettings:
    """
    Centralized CORS configuration for all services
    
    Environment Variables:
        ENVIRONMENT: Application environment (development/staging/production)
        ALLOWED_ORIGINS: Comma-separated list of allowed origins
    """
    
    # Production origins - explicitly defined
    ALLOWED_ORIGINS = [
        "https://admin.sahool.io",
        "https://app.sahool.io",
        "https://dashboard.sahool.io",
        "https://api.sahool.io",
    ]
    
    # Development origins - only enabled in development
    DEV_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8080",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8080",
    ]
    
    @staticmethod
    def get_allowed_origins() -> List[str]:
        """
        Get all allowed origins based on environment
        
        Returns:
            List of allowed origins
        """
        environment = os.getenv("ENVIRONMENT", "development").lower()
        
        # In development, allow both production and dev origins
        if environment == "development":
            return CORSSettings.ALLOWED_ORIGINS + CORSSettings.DEV_ORIGINS
        
        # In production, only allow explicitly defined origins
        # Also check for custom ALLOWED_ORIGINS env var
        custom_origins = os.getenv("ALLOWED_ORIGINS", "")
        if custom_origins:
            custom_list = [origin.strip() for origin in custom_origins.split(",")]
            return CORSSettings.ALLOWED_ORIGINS + custom_list
        
        return CORSSettings.ALLOWED_ORIGINS


def get_cors_config() -> dict:
    """
    Get CORS middleware configuration dictionary
    
    Usage in FastAPI:
        from shared.config.cors_config import get_cors_config
        
        app.add_middleware(
            CORSMiddleware,
            **get_cors_config()
        )
    
    Returns:
        Dictionary with CORS configuration
    """
    return {
        "allow_origins": CORSSettings.get_allowed_origins(),
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Tenant-Id",
            "Accept",
            "Origin",
        ],
        "expose_headers": [
            "Content-Length",
            "Content-Range",
            "X-Total-Count",
        ],
        "max_age": 600,  # 10 minutes
    }
