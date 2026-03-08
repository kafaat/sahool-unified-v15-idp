"""
🗄️ SAHOOL Billing Core - Database Configuration
إعداد قاعدة البيانات - PostgreSQL مع Async SQLAlchemy

This module provides:
- Database engine configuration
- Session management
- Connection pooling
- Database initialization
"""

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool

logger = logging.getLogger("sahool-billing")

# =============================================================================
# Database Configuration
# =============================================================================

# Database URL from environment
# TLS/SSL: DATABASE_URL must include sslmode=require for production
# Example: postgresql+asyncpg://user:pass@host:5432/db?sslmode=require
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Build from individual environment variables for flexibility
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db_name = os.getenv("POSTGRES_DB", "sahool_billing")
    DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Ensure async driver
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql+psycopg2://"):
    # Convert sync driver to async
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)

# Environment settings
ENVIRONMENT = os.getenv("ENVIRONMENT", "production").lower()
IS_DEV = ENVIRONMENT in ("development", "dev", "test", "testing")

# Pool settings
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5" if IS_DEV else "20"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10" if IS_DEV else "40"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # 1 hour

# =============================================================================
# SQLAlchemy Base
# =============================================================================

Base = declarative_base()

# =============================================================================
# Engine & Session
# =============================================================================

# Global engine instance
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """
    Get or create the database engine
    الحصول على محرك قاعدة البيانات أو إنشاءه
    """
    global _engine

    if _engine is None:
        # Determine pool class based on environment
        # For async engines, SQLAlchemy 2.0+ automatically adapts sync pools
        if IS_DEV:
            # Development: Use NullPool (no pooling) for simplicity
            logger.info("Using NullPool for development environment")
        else:
            # Production: Use QueuePool for connection pooling
            # SQLAlchemy 2.0+ async engines automatically wrap sync pools
            logger.info("Using QueuePool for production environment")

        # Create engine with connection pooling
        # For async engines, SQLAlchemy automatically uses async pool classes
        engine_kwargs = {
            "echo": IS_DEV,  # Log SQL queries in dev mode
            "pool_pre_ping": True,  # Verify connections before using
            "pool_recycle": POOL_RECYCLE,
            "connect_args": {
                "server_settings": {
                    "application_name": "sahool-billing-core",
                    "jit": "off",  # Disable JIT for better compatibility
                },
                "command_timeout": 60,  # Query timeout in seconds
                "timeout": 10,  # Connection timeout in seconds
            },
        }

        if IS_DEV:
            # Development: Use NullPool (no pooling) for simplicity
            engine_kwargs["poolclass"] = NullPool
            logger.info("Using NullPool for development environment")
        else:
            # Production: Use default async pool with size limits
            # create_async_engine uses QueuePool by default for async drivers
            engine_kwargs["poolclass"] = QueuePool
            engine_kwargs["pool_size"] = POOL_SIZE
            engine_kwargs["max_overflow"] = MAX_OVERFLOW
            engine_kwargs["pool_timeout"] = POOL_TIMEOUT
            logger.info(f"Using async QueuePool for production: pool_size={POOL_SIZE}, max_overflow={MAX_OVERFLOW}")

        _engine = create_async_engine(DATABASE_URL, **engine_kwargs)

        logger.info(f"Database engine created: pool_size={POOL_SIZE}, max_overflow={MAX_OVERFLOW}")

    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Get or create the session factory
    الحصول على مصنع الجلسات أو إنشاءه
    """
    global _session_factory

    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Don't expire objects after commit
            autocommit=False,
            autoflush=False,
        )
        logger.info("Session factory created")

    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database sessions
    FastAPI dependency للحصول على جلسات قاعدة البيانات

    Usage:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions
    مدير السياق للحصول على جلسات قاعدة البيانات

    Usage:
        async with get_db_context() as db:
            result = await db.execute(...)
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database transaction error: {e}")
            raise
        finally:
            await session.close()


# =============================================================================
# Database Initialization
# =============================================================================


async def init_db() -> None:
    """
    Initialize database - create all tables
    تهيئة قاعدة البيانات - إنشاء جميع الجداول

    Note: In production, use Alembic migrations instead
    ملاحظة: في الإنتاج، استخدم Alembic migrations بدلاً من ذلك
    """
    engine = get_engine()

    try:
        # Import models to register them with Base
        from . import models  # noqa: F401

        # Create all tables
        async with engine.begin() as conn:
            logger.info("Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def drop_db() -> None:
    """
    Drop all database tables
    حذف جميع جداول قاعدة البيانات

    WARNING: This will delete all data!
    تحذير: سيؤدي هذا إلى حذف جميع البيانات!
    """
    engine = get_engine()

    try:
        from . import models  # noqa: F401

        async with engine.begin() as conn:
            logger.warning("Dropping all database tables...")
            await conn.run_sync(Base.metadata.drop_all)
            logger.warning("Database tables dropped")

    except Exception as e:
        logger.error(f"Failed to drop database: {e}")
        raise


async def check_db_connection() -> bool:
    """
    Check if database connection is working
    التحقق من عمل الاتصال بقاعدة البيانات

    Returns:
        bool: True if connection is successful
    """
    try:
        async with get_db_context() as db:
            result = await db.execute(text("SELECT 1"))
            result.scalar()
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


async def close_db() -> None:
    """
    Close database connections and dispose engine
    إغلاق اتصالات قاعدة البيانات
    """
    global _engine, _session_factory

    if _engine is not None:
        await _engine.dispose()
        logger.info("Database engine disposed")
        _engine = None
        _session_factory = None


# =============================================================================
# Health Check
# =============================================================================


async def db_health_check() -> dict:
    """
    Database health check for monitoring
    فحص صحة قاعدة البيانات للمراقبة

    Returns:
        dict: Health status information
    """
    try:
        is_connected = await check_db_connection()

        if is_connected:
            return {
                "status": "healthy",
                "database": "postgresql",
                "pool_size": POOL_SIZE,
                "max_overflow": MAX_OVERFLOW,
            }
        else:
            return {
                "status": "unhealthy",
                "database": "postgresql",
                "error": "Connection failed",
            }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "postgresql",
            "error": str(e),
        }
