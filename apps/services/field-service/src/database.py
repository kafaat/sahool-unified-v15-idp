"""
SAHOOL Field Service - Database Configuration
إعدادات قاعدة البيانات
"""

import os
from typing import Dict, Any

# Database connection URL - MUST be set via environment variable in production
# Example: DATABASE_URL=postgres://$USER:$PASSWORD@$HOST:$PORT/$DB
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise EnvironmentError(
        "DATABASE_URL environment variable is required. "
        "See .env.example for format"
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
