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
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise OSError("DATABASE_URL environment variable is required. See .env.example for format")

# Tortoise ORM requires 'postgres://' scheme, not 'postgresql://'
# Normalize the URL scheme for Tortoise ORM compatibility
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgres://", 1)
    logger.info("Normalized DATABASE_URL scheme from 'postgresql://' to 'postgres://' for Tortoise ORM")

# Tortoise ORM configuration
TORTOISE_ORM = {
    "connections": {
        "default": DATABASE_URL,
    },
    "apps": {
        "models": {
            "models": [
                "apps.services.notification-service.src.models",
                "aerich.models",
            ],
            "default_connection": "default",
        },
    },
    "use_tz": True,
    "timezone": "UTC",
}

# Alternative config for when running directly
TORTOISE_ORM_LOCAL = {
    "connections": {
        "default": DATABASE_URL,
    },
    "apps": {
        "models": {
            "models": ["src.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": True,
    "timezone": "UTC",
}


async def init_db(create_db: bool = False) -> None:
    """
    تهيئة اتصال قاعدة البيانات
    Initialize database connection and create tables

    Args:
        create_db: If True, creates tables (use only in development)
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
        logger.info(
            f"📊 Database URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'configured'}"
        )

        # Generate schemas (only in development!)
        if create_db:
            logger.warning(
                "⚠️  Creating database schemas - this should only be done in development!"
            )
            await Tortoise.generate_schemas()
            logger.info("✅ Database schemas created")
        else:
            logger.info("ℹ️  Skipping schema generation (use Aerich migrations in production)")

    except DBConnectionError as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        logger.error("Make sure PostgreSQL is running and DATABASE_URL is correct")
        raise
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def close_db() -> None:
    """
    إغلاق اتصال قاعدة البيانات
    Close database connections
    """
    try:
        await connections.close_all()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error closing database connections: {e}")


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
        logger.error(f"Database health check failed: {e}")
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
        logger.error(f"Failed to get database stats: {e}")
        return {"error": str(e)}


# Migration helpers (for Aerich)
def get_aerich_config() -> dict:
    """
    الحصول على إعدادات Aerich للترحيلات
    Get Aerich configuration for migrations
    """
    return TORTOISE_ORM


async def run_migrations() -> None:
    """
    تشغيل ترحيلات قاعدة البيانات
    Run database migrations using Aerich

    Note: This should be called from a migration script, not in production code
    """
    logger.info("Running database migrations...")

    try:
        from aerich import Command

        command = Command(
            tortoise_config=TORTOISE_ORM,
            app="models",
            location="./migrations",
        )

        await command.init()
        await command.migrate()
        await command.upgrade()

        logger.info("✅ Migrations completed successfully")
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


# Initialization flags
_db_initialized = False


async def ensure_db_initialized(create_db: bool = False) -> None:
    """
    التأكد من تهيئة قاعدة البيانات
    Ensure database is initialized (idempotent)
    """
    global _db_initialized

    if not _db_initialized:
        await init_db(create_db=create_db)
        _db_initialized = True
    else:
        logger.debug("Database already initialized")


# Context manager for database session
class DatabaseSession:
    """
    مدير سياق لجلسة قاعدة البيانات
    Context manager for database session
    """

    def __init__(self, create_db: bool = False):
        self.create_db = create_db

    async def __aenter__(self):
        await ensure_db_initialized(create_db=self.create_db)
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
            logger.info(f"Database connection attempt {attempt}/{max_retries}...")

            await Tortoise.init(config=TORTOISE_ORM_LOCAL)
            conn = connections.get("default")
            await conn.execute_query("SELECT 1")
            await connections.close_all()

            logger.info("✅ Database is ready!")
            return True

        except Exception as e:
            logger.warning(f"Database not ready (attempt {attempt}/{max_retries}): {e}")

            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
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
            await init_db(create_db=False)

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
