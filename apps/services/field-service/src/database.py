"""
SAHOOL Field Service - Database Configuration
إعدادات قاعدة البيانات
"""

import os
from typing import Dict, Any

# Database connection URL
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgres://sahool:sahool@postgres:5432/sahool"
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
