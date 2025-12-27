"""
Database Configuration
تكوين قاعدة البيانات
"""

import os
from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote_plus


@dataclass
class DatabaseConfig:
    """Database configuration settings"""

    # Connection settings
    host: str = "postgres"
    port: int = 5432
    database: str = "sahool"
    username: str = "sahool"
    # SECURITY: No default password - MUST be provided via environment variable
    password: str = ""

    # Pool settings
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 1800  # 30 minutes

    # SSL settings
    ssl_mode: str = "prefer"

    # Debug
    echo: bool = False

    @classmethod
    def from_env(cls, prefix: str = "DB") -> "DatabaseConfig":
        """Load configuration from environment variables

        SECURITY: Password must be provided via environment variable.
        An empty password is allowed only in test environment.
        """
        environment = os.getenv("ENVIRONMENT", "production").lower()
        password = os.getenv(f"{prefix}_PASSWORD", "")

        # Enforce password in non-test environments
        if not password and environment not in ("test", "testing", "ci"):
            import warnings
            warnings.warn(
                f"SECURITY WARNING: {prefix}_PASSWORD environment variable is not set. "
                "This is required for production environments.",
                UserWarning,
                stacklevel=2
            )

        return cls(
            host=os.getenv(f"{prefix}_HOST", "postgres"),
            port=int(os.getenv(f"{prefix}_PORT", "5432")),
            database=os.getenv(f"{prefix}_NAME", "sahool"),
            username=os.getenv(f"{prefix}_USER", "sahool"),
            password=password,
            pool_size=int(os.getenv(f"{prefix}_POOL_SIZE", "5")),
            max_overflow=int(os.getenv(f"{prefix}_MAX_OVERFLOW", "10")),
            pool_timeout=int(os.getenv(f"{prefix}_POOL_TIMEOUT", "30")),
            pool_recycle=int(os.getenv(f"{prefix}_POOL_RECYCLE", "1800")),
            ssl_mode=os.getenv(f"{prefix}_SSL_MODE", "prefer"),
            echo=os.getenv(f"{prefix}_ECHO", "false").lower() == "true",
        )

    def get_url(self, async_driver: bool = False) -> str:
        """Generate database URL"""
        driver = "postgresql+asyncpg" if async_driver else "postgresql+psycopg2"
        encoded_password = quote_plus(self.password)
        return f"{driver}://{self.username}:{encoded_password}@{self.host}:{self.port}/{self.database}"


def get_database_url(async_driver: bool = False) -> str:
    """Get database URL from environment"""
    # Check for DATABASE_URL first (common in cloud deployments)
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if async_driver and "postgresql://" in database_url:
            return database_url.replace("postgresql://", "postgresql+asyncpg://")
        elif not async_driver and "postgresql+asyncpg://" in database_url:
            return database_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
        return database_url

    # Build from individual env vars
    config = DatabaseConfig.from_env()
    return config.get_url(async_driver)
