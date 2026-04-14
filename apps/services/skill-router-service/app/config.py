"""Configuration for skill-router-service. No secrets — all sourced from env."""

from __future__ import annotations

import os

from pydantic import BaseModel


class Settings(BaseModel):
    SKILLS_INDEX_PATH: str = os.getenv(
        "SKILLS_INDEX_PATH",
        "/app/.claude/skills/index.yaml",
    )
    SERVICE_NAME: str = "skill-router-service"
    SERVICE_VERSION: str = "16.0.0"
    PORT: int = int(os.getenv("PORT", "8205"))
    HOST: str = os.getenv("HOST", "0.0.0.0")


settings = Settings()
