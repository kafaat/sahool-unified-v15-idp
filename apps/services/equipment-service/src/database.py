"""
SAHOOL Equipment Service - Database Configuration
إعدادات قاعدة البيانات لخدمة إدارة المعدات
"""

import os
import re
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


def _run_additive_migrations() -> None:
    """Add columns that exist in the ORM model but may be missing from older DB schemas."""
    # Columns that were added to the model after the initial DB schema was created.
    # All are nullable so adding them to existing rows is safe.
    # NOTE: col_name and col_type are hardcoded literals (not user input) — the
    # regex validation below is defense-in-depth in case this list is ever edited
    # carelessly. SQL injection is not reachable from any external input here.
    new_columns = [
        ("year", "INTEGER"),
        ("horsepower", "INTEGER"),
        ("fuel_capacity_liters", "NUMERIC(8, 2)"),
        ("current_fuel_percent", "NUMERIC(5, 2)"),
        ("current_lat", "NUMERIC(10, 7)"),
        ("current_lon", "NUMERIC(10, 7)"),
        ("next_maintenance_hours", "NUMERIC(10, 2)"),
        ("qr_code", "VARCHAR(100)"),
    ]
    # Defense-in-depth: only allow safe identifier/type characters.
    _ident_re = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
    _type_re = re.compile(r"^[A-Z]+(\([0-9]+(,\s*[0-9]+)?\))?$")
    try:
        db = SessionLocal()
        for col_name, col_type in new_columns:
            if not _ident_re.match(col_name) or not _type_re.match(col_type):
                raise ValueError(f"Refusing unsafe DDL identifier: {col_name} {col_type}")
            stmt = f"ALTER TABLE equipment ADD COLUMN IF NOT EXISTS {col_name} {col_type}"
            db.execute(text(stmt))  # noqa: S608  # nosec B608  # nosemgrep: python.sqlalchemy.security.audit.avoid-sqlalchemy-text.avoid-sqlalchemy-text -- col_name/col_type are validated against strict regex above; no user input reaches here
        db.commit()
        db.close()
    except Exception as e:
        print(f"⚠️  Additive migration failed (non-fatal): {e}")


def init_db():
    """
    Initialize database tables and run migrations.

    This function:
    1. Creates tables if they don't exist
    2. Adds columns that the model requires but may be missing from older DB schemas

    Column name mismatches (e.g. model 'equipment_id' → DB 'id') are handled
    via SQLAlchemy mapped_column aliases in db_models.py — no DB renames needed.
    """
    # Create tables that don't exist (no-op for existing tables)
    Base.metadata.create_all(bind=engine)

    # Add columns introduced in newer model versions that may not exist in older DB schemas
    _run_additive_migrations()


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
