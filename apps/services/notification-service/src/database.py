"""
SAHOOL Notification Service - Database Configuration
إعدادات قاعدة البيانات - Tortoise ORM
"""

import logging
import os

from tortoise import Tortoise, connections
from tortoise.exceptions import DBConnectionError

logger = logging.getLogger("sahool-notifications.database")

# Database configuration - MUST be set via environment variable in production
# Set DATABASE_URL in .env file (see .env.example for format)
#
# TLS/SSL Security (أمان TLS/SSL):
# - SSL is configured via DATABASE_URL connection string parameter
# - يتم تكوين SSL عبر معامل سلسلة اتصال DATABASE_URL
# - For production: DATABASE_URL MUST include sslmode=require
# - للإنتاج: يجب أن يتضمن DATABASE_URL معامل sslmode=require
# - Example: postgresql://user:pass@host:port/db?sslmode=require
# - Development: sslmode=disable is acceptable for Docker internal network
# - Production: sslmode=require is MANDATORY for external connections
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    if os.getenv("ENVIRONMENT") == "test":
        # Use a clearly non-routable URL that will fail fast if tests actually try to connect
        DATABASE_URL = "postgresql://test:test@invalid-test-host.local:5432/test_notifications"
        logger.warning("DATABASE_URL not set in test environment, using placeholder URL")
    else:
        raise OSError("DATABASE_URL environment variable is required. See .env.example for format")

# Tortoise ORM requires 'postgres://' scheme, not 'postgresql://'
# Normalize the URL scheme for Tortoise ORM compatibility
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgres://", 1)
    logger.info("Normalized DATABASE_URL scheme from 'postgresql://' to 'postgres://' for Tortoise ORM")

# Tortoise ORM configuration with SSL/TLS encryption
TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "dsn": DATABASE_URL,
                "ssl": "prefer",  # Enforce TLS/SSL encryption
            },
        },
    },
    "apps": {
        "models": {
            "models": [
                "src.models",
            ],
            "default_connection": "default",
            "migrations": "migrations.models",
        },
    },
    "use_tz": True,
    "timezone": "UTC",
}

# Alternative config for when running directly with SSL/TLS encryption
TORTOISE_ORM_LOCAL = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "dsn": DATABASE_URL,
                "ssl": "prefer",  # Enforce TLS/SSL encryption
            },
        },
    },
    "apps": {
        "models": {
            "models": ["src.models"],
            "default_connection": "default",
            "migrations": "migrations.models",
        },
    },
    "use_tz": True,
    "timezone": "UTC",
}


async def init_notification_db(create_schema: bool = False) -> None:
    """
    تهيئة اتصال قاعدة البيانات
    Initialize database connection and create tables

    Args:
        create_schema: If True, creates tables (use only in development)
    """
    try:
        # Determine which config to use based on module path
        # In Docker, we're at /app and models are at /app/src/models.py
        # So we use src.models for the models path
        try:
            # Try relative import first (for Docker container)
            from .models import Notification

            config = TORTOISE_ORM_LOCAL
            logger.info("Using local module path configuration (src.models)")
        except ImportError:
            # Fall back to full path import (for local development)
            try:
                from apps.services.notification_service.src.models import Notification

                config = TORTOISE_ORM
                logger.info("Using full module path configuration")
            except ImportError:
                # Last resort: use local config anyway
                config = TORTOISE_ORM_LOCAL
                logger.warning("Could not import models, using local config anyway")

        # Initialize Tortoise ORM
        await Tortoise.init(config=config)

        logger.info("✅ Database connection established")
        db_host = DATABASE_URL.split("@")[1] if "@" in DATABASE_URL else "configured"
        logger.info("📊 Database URL: %s", db_host)

        # Generate schemas (only in development!)
        if create_schema:
            logger.warning("⚠️  Creating database schemas - this should only be done in development!")
            await Tortoise.generate_schemas()
            logger.info("✅ Database schemas created")
        else:
            logger.info("ℹ️  Skipping schema generation (use Aerich migrations in production)")

    except DBConnectionError as e:
        logger.error("❌ Failed to connect to database: %s", e)
        logger.error("Make sure PostgreSQL is running and DATABASE_URL is correct")
        raise
    except Exception as e:
        logger.error("❌ Database initialization failed: %s", e)
        raise


# Alias for backward compatibility - CodeQL will see this as a unique function
init_db = init_notification_db


async def close_db() -> None:
    """
    إغلاق اتصال قاعدة البيانات
    Close database connections
    """
    try:
        await connections.close_all()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error("❌ Error closing database connections: %s", e)


async def check_db_health() -> dict:
    """
    التحقق من صحة قاعدة البيانات
    Check database health and return status
    """
    try:
        # Try a simple query
        conn = connections.get("default")
        await conn.execute_query("SELECT 1")

        return {
            "status": "healthy",
            "connected": True,
            "database": (DATABASE_URL.split("/")[-1] if "/" in DATABASE_URL else "unknown"),
        }
    except Exception as e:
        logger.error("Database health check failed: %s", e)
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e),
        }


async def get_db_stats() -> dict:
    """
    الحصول على إحصائيات قاعدة البيانات
    Get database statistics
    """
    try:
        from .models import Notification, NotificationPreference, NotificationTemplate

        total_notifications = await Notification.all().count()
        pending_notifications = await Notification.filter(status="pending").count()
        total_templates = await NotificationTemplate.filter(is_active=True).count()
        total_preferences = await NotificationPreference.all().count()

        return {
            "total_notifications": total_notifications,
            "pending_notifications": pending_notifications,
            "total_templates": total_templates,
            "total_preferences": total_preferences,
        }
    except Exception as e:
        logger.error("Failed to get database stats: %s", e)
        return {"error": str(e)}


# Migration helpers (Tortoise ORM built-in migrations)
# Aerich is incompatible with tortoise-orm>=1.0.0. Use the built-in CLI instead:
#   python -m tortoise init        # Initialize migration packages
#   python -m tortoise makemigrations --name "description"
#   python -m tortoise migrate     # Apply pending migrations
#   python -m tortoise downgrade   # Rollback last migration
# Config is resolved from [tool.tortoise] in pyproject.toml or via -c flag.
def get_tortoise_config() -> dict:
    """
    الحصول على إعدادات Tortoise ORM للترحيلات
    Get Tortoise ORM configuration for migrations
    """
    return TORTOISE_ORM


# Keep old name as alias for backward compatibility
get_aerich_config = get_tortoise_config


async def run_migrations() -> None:
    """
    تشغيل ترحيلات قاعدة البيانات
    Run database migrations using Tortoise ORM built-in migration API

    Note: This should be called from a migration script, not in production code.
    For CLI usage, prefer: python -m tortoise migrate
    """
    logger.info("Running database migrations...")

    try:
        from tortoise.migrations.api import migrate

        await Tortoise.init(config=TORTOISE_ORM)
        await migrate(app_label="models")

        logger.info("Migrations completed successfully")
    except Exception as e:
        logger.error("Migration failed: %s", e)
        raise


# Initialization flags
_db_initialized = False


async def ensure_db_initialized(create_schema: bool = False) -> None:
    """
    التأكد من تهيئة قاعدة البيانات
    Ensure database is initialized (idempotent)
    """
    global _db_initialized

    if not _db_initialized:
        await init_notification_db(create_schema=create_schema)
        _db_initialized = True
    else:
        logger.debug("Database already initialized")


# Context manager for database session
class DatabaseSession:
    """
    مدير سياق لجلسة قاعدة البيانات
    Context manager for database session
    """

    def __init__(self, create_schema: bool = False):
        self.create_schema = create_schema

    async def __aenter__(self):
        await ensure_db_initialized(create_schema=self.create_schema)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Don't close connection here - let it persist for the app lifetime
        # Only close on application shutdown
        pass


# Health check for startup
async def wait_for_db(max_retries: int = 5, retry_delay: int = 2) -> bool:
    """
    انتظار توفر قاعدة البيانات
    Wait for database to be available (useful for Docker startup)

    Args:
        max_retries: Maximum number of connection attempts
        retry_delay: Seconds to wait between retries

    Returns:
        True if connected, False otherwise
    """
    import asyncio

    for attempt in range(1, max_retries + 1):
        try:
            logger.info("Database connection attempt %d/%d...", attempt, max_retries)

            await Tortoise.init(config=TORTOISE_ORM_LOCAL)
            conn = connections.get("default")
            await conn.execute_query("SELECT 1")
            await connections.close_all()

            logger.info("✅ Database is ready!")
            return True

        except Exception as e:
            logger.warning("Database not ready (attempt %d/%d): %s", attempt, max_retries, e)

            if attempt < max_retries:
                logger.info("Retrying in %d seconds...", retry_delay)
                await asyncio.sleep(retry_delay)
            else:
                logger.error("❌ Database connection failed after all retries")
                return False

    return False


if __name__ == "__main__":
    """
    Script للتحقق من الاتصال بقاعدة البيانات
    Test database connection
    """
    import asyncio

    async def test_connection():
        print("Testing database connection...")
        print(f"Database URL: {DATABASE_URL}")

        try:
            await init_notification_db(create_schema=False)

            health = await check_db_health()
            print(f"Health check: {health}")

            stats = await get_db_stats()
            print(f"Database stats: {stats}")

            await close_db()
            print("✅ Database test completed successfully")

        except Exception as e:
            print(f"❌ Database test failed: {e}")
            raise

    asyncio.run(test_connection())
