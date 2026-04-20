"""
SAHOOL Equipment Service - Database Configuration
إعدادات قاعدة البيانات لخدمة إدارة المعدات
"""

import os
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from .db_models import Base

# ═══════════════════════════════════════════════════════════════════════════════
# Database Configuration
# ═══════════════════════════════════════════════════════════════════════════════

# Get database URL from environment
# Security: No fallback credentials - require DATABASE_URL to be set
#
# TLS/SSL Security:
# - SSL is configured via DATABASE_URL connection string parameter
# - For production: DATABASE_URL MUST include sslmode=require
# - Example: postgresql://user:pass@host:port/db?sslmode=require
# - Development: sslmode=disable is acceptable for Docker internal network
# - Production: sslmode=require is MANDATORY for external connections
DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql://localhost:5432/sahool"

# Determine SSL mode based on environment
_environment = os.getenv("ENVIRONMENT", "development")
_connect_args = {}
if _environment in ("production", "staging"):
    _connect_args["sslmode"] = "require"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,  # Maximum number of connections in the pool
    max_overflow=20,  # Maximum overflow connections
    echo=False,  # Set to True for SQL query logging (debug only)
    connect_args=_connect_args,
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

    Creates tables that don't exist yet. The Equipment model maps the Python
    attribute 'equipment_id' to the DB column 'id' (via mapped_column("id", ...)),
    so no rename migration is required or safe to run — the FK constraint on
    equipment_maintenance blocks any attempt to rename or retype that column.
    """
    # Create tables that don't exist
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
        return True
    except Exception:
        return False
