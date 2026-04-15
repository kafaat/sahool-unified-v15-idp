from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ISSUER: str = "sahool-platform"
    JWT_AUDIENCE: str = "sahool-api"

    # Security
    BCRYPT_COST: int = 12
    CORS_ORIGINS: str = "http://localhost:3000"

    # Service
    AUTH_HOST: str = "0.0.0.0"
    AUTH_PORT: int = 8000

    # Default admin (seeded on first run)
    ADMIN_EMAIL: str = "admin@local.dev"
    ADMIN_PASSWORD: str = "Admin123!"
    ADMIN_NAME: str = "Admin"

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def secret_must_be_long_enough(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters")
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
