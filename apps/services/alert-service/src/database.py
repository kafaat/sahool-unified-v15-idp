"""
SAHOOL Alert Service - Database Configuration
إعدادات قاعدة البيانات لخدمة التنبيهات
"""

import logging
import os
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from .db_models import Base

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# Database Configuration
# ═══════════════════════════════════════════════════════════════════════════════

# Get database URL from environment
# Security: No fallback credentials - require DATABASE_URL to be set
# TLS/SSL: DATABASE_URL must include sslmode=require for production
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/sahool_alerts")

# Create SQLAlchemy engine with connection pooling and TLS support
# SSL/TLS is enforced via DATABASE_URL parameter: ?sslmode=require
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,  # Maximum number of connections in the pool
    max_overflow=20,  # Maximum overflow connections
    pool_timeout=30,  # Connection timeout (seconds)
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False,  # Set to True for SQL query logging (debug only)
    connect_args={
        "connect_timeout": 10,  # Connection timeout in seconds
        "options": "-c statement_timeout=30000",  # 30s query timeout
    },
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Database Dependency
# ═══════════════════════════════════════════════════════════════════════════════


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI.

    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db here
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════════
# Database Initialization
# ═══════════════════════════════════════════════════════════════════════════════


def init_db():
    """
    Initialize database tables.

    WARNING: This creates all tables defined in Base.
    In production, use Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    """
    Drop all database tables.

    WARNING: This will delete all data!
    Only use in development/testing.
    """
    Base.metadata.drop_all(bind=engine)


# ═══════════════════════════════════════════════════════════════════════════════
# Health Check
# ═══════════════════════════════════════════════════════════════════════════════


def check_db_connection() -> bool:
    """
    Check if database connection is working.

    Returns:
        True if connection is successful, False otherwise
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection check successful")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}", exc_info=True)
        return False
