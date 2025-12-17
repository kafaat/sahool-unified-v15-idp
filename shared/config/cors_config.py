"""
SAHOOL Platform - Centralized CORS Configuration
منصة سهول - تهيئة CORS المركزية

This module provides a centralized and secure CORS configuration
for all SAHOOL services to prevent security vulnerabilities.

Security: Never use wildcard (*) origins in production!
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class CORSSettings(BaseSettings):
    """
    Centralized CORS configuration for all services
    
    Environment Variables:
        ENVIRONMENT: Application environment (development/staging/production)
        ALLOWED_ORIGINS: Comma-separated list of allowed origins
    """
    
    # Production origins - explicitly defined
    allowed_origins: List[str] = [
        "https://admin.sahool.io",
        "https://app.sahool.io",
        "https://dashboard.sahool.io",
        "https://api.sahool.io",
    ]
    
    # Development origins - only enabled in development
    dev_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8080",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8080",
    ]
    
    @property
    def all_origins(self) -> List[str]:
        """
        Get all allowed origins based on environment
        
        Returns:
            List of allowed origins
        """
        environment = os.getenv("ENVIRONMENT", "development").lower()
        
        # In development, allow both production and dev origins
        if environment == "development":
            return self.allowed_origins + self.dev_origins
        
        # In production, only allow explicitly defined origins
        # Also check for custom ALLOWED_ORIGINS env var
        custom_origins = os.getenv("ALLOWED_ORIGINS", "")
        if custom_origins:
            custom_list = [origin.strip() for origin in custom_origins.split(",")]
            return self.allowed_origins + custom_list
        
        return self.allowed_origins
    
    @property
    def allow_credentials(self) -> bool:
        """Allow credentials (cookies, authorization headers)"""
        return True
    
    @property
    def allow_methods(self) -> List[str]:
        """Allowed HTTP methods"""
        return ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    
    @property
    def allow_headers(self) -> List[str]:
        """Allowed HTTP headers"""
        return [
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Tenant-Id",
            "Accept",
            "Origin",
        ]
    
    @property
    def expose_headers(self) -> List[str]:
        """Headers to expose to the browser"""
        return [
            "Content-Length",
            "Content-Range",
            "X-Total-Count",
        ]
    
    @property
    def max_age(self) -> int:
        """Maximum age for CORS preflight cache (seconds)"""
        return 600  # 10 minutes


# Global instance
cors_settings = CORSSettings()


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
        "allow_origins": cors_settings.all_origins,
        "allow_credentials": cors_settings.allow_credentials,
        "allow_methods": cors_settings.allow_methods,
        "allow_headers": cors_settings.allow_headers,
        "expose_headers": cors_settings.expose_headers,
        "max_age": cors_settings.max_age,
    }
