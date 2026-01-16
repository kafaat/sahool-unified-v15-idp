"""
JWT Authentication Configuration for SAHOOL Platform
Centralized configuration for JWT token handling

Note: This configuration only supports HS256 algorithm.
RS256 with RSA keys has been deprecated.
"""

import os

# JWT Secret Key - Required, must be at least 32 characters
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is required")
if len(JWT_SECRET_KEY) < 32:
    raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")

# JWT Algorithm - HS256 only (RS256 deprecated)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Token expiration times
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# JWT Issuer and Audience
JWT_ISSUER = os.getenv("JWT_ISSUER", "sahool-platform")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "sahool-api")

# Token header configuration
TOKEN_HEADER = "Authorization"
TOKEN_PREFIX = "Bearer"

# Rate limiting
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

# Token revocation
TOKEN_REVOCATION_ENABLED = os.getenv("TOKEN_REVOCATION_ENABLED", "true").lower() == "true"

# Redis configuration for token revocation
REDIS_URL = os.getenv("REDIS_URL")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")


# Backward compatibility aliases
class JWTConfig:
    """JWT Configuration Settings - HS256 Only (backward compatibility wrapper)"""

    JWT_SECRET = JWT_SECRET_KEY
    JWT_ALGORITHM = JWT_ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_DAYS = JWT_REFRESH_TOKEN_EXPIRE_DAYS
    JWT_ISSUER = JWT_ISSUER
    JWT_AUDIENCE = JWT_AUDIENCE
    TOKEN_HEADER = TOKEN_HEADER
    TOKEN_PREFIX = TOKEN_PREFIX
    RATE_LIMIT_ENABLED = RATE_LIMIT_ENABLED
    RATE_LIMIT_REQUESTS = RATE_LIMIT_REQUESTS
    RATE_LIMIT_WINDOW_SECONDS = RATE_LIMIT_WINDOW_SECONDS
    TOKEN_REVOCATION_ENABLED = TOKEN_REVOCATION_ENABLED
    REDIS_URL = REDIS_URL
    REDIS_HOST = REDIS_HOST
    REDIS_PORT = REDIS_PORT
    REDIS_DB = REDIS_DB
    REDIS_PASSWORD = REDIS_PASSWORD

    @classmethod
    def validate(cls) -> None:
        """Validation is performed at module load time."""
        pass

    @classmethod
    def get_signing_key(cls) -> str:
        """Get the key for signing tokens (HS256 only)"""
        return JWT_SECRET_KEY

    @classmethod
    def get_verification_key(cls) -> str:
        """Get the key for verifying tokens (HS256 only)"""
        return JWT_SECRET_KEY


# Singleton instance for backward compatibility
config = JWTConfig()
