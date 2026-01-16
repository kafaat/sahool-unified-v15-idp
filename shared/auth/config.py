"""
JWT Authentication Configuration for SAHOOL Platform
Centralized configuration for JWT token handling

Note: This configuration only supports HS256 algorithm.
RS256 with RSA keys has been deprecated.
"""

import os


class JWTConfig:
    """JWT Configuration Settings - HS256 Only"""

    # JWT Secret Key (required)
    JWT_SECRET: str = os.getenv("JWT_SECRET_KEY", os.getenv("JWT_SECRET", ""))

    # JWT Algorithm - HS256 only (RS256 deprecated)
    JWT_ALGORITHM: str = "HS256"

    # Token expiration times
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # JWT Issuer and Audience
    JWT_ISSUER: str = os.getenv("JWT_ISSUER", "sahool-platform")
    JWT_AUDIENCE: str = os.getenv("JWT_AUDIENCE", "sahool-api")

    # Token header name
    TOKEN_HEADER: str = "Authorization"
    TOKEN_PREFIX: str = "Bearer"

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

    # Token revocation
    TOKEN_REVOCATION_ENABLED: bool = os.getenv("TOKEN_REVOCATION_ENABLED", "true").lower() == "true"

    # Redis configuration for token revocation
    REDIS_URL: str | None = os.getenv("REDIS_URL")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str | None = os.getenv("REDIS_PASSWORD")

    @classmethod
    def validate(cls) -> None:
        """Validate JWT configuration"""
        env = os.getenv("ENVIRONMENT", "development")

        if env in ("production", "staging"):
            if not cls.JWT_SECRET or len(cls.JWT_SECRET) < 32:
                raise ValueError("JWT_SECRET must be at least 32 characters in production")

    @classmethod
    def get_signing_key(cls) -> str:
        """Get the key for signing tokens"""
        return cls.JWT_SECRET

    @classmethod
    def get_verification_key(cls) -> str:
        """Get the key for verifying tokens"""
        return cls.JWT_SECRET


# Singleton instance
config = JWTConfig()
