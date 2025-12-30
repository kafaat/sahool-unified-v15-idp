"""
SAHOOL Field Service - Database Configuration
إعدادات قاعدة البيانات
"""

import os
from typing import Dict, Any

# Database connection URL - MUST be set via environment variable in production
# Format: postgres://user:password@host:port/database
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise EnvironmentError(
        "DATABASE_URL environment variable is required. "
        "Format: postgres://user:password@host:port/database"
    )

# Tortoise ORM Configuration
TORTOISE_ORM: Dict[str, Any] = {
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
