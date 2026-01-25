"""
SAHOOL Field Service - Database Configuration
إعدادات قاعدة البيانات
"""

import os
from typing import Any

# Database connection URL - MUST be set via environment variable in production
# Set DATABASE_URL in .env file (see .env.example for format)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise OSError("DATABASE_URL environment variable is required. See .env.example for format")

# Tortoise ORM Configuration
TORTOISE_ORM: dict[str, Any] = {
    "connections": {
        "default": DATABASE_URL,
    },
    "apps": {
        "models": {
            "models": ["src.db_models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": True,
    "timezone": "UTC",
}
