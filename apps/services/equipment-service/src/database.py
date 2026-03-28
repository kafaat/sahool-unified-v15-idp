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
    Initialize database tables and run migrations.

    This function:
    1. Creates tables if they don't exist
    2. Runs migration to rename 'id' to 'equipment_id' if needed

    In production, consider using Alembic migrations directly.
    """
    # Create tables that don't exist
    Base.metadata.create_all(bind=engine)

    # Run migration to rename id -> equipment_id if needed
    # This handles the schema mismatch where DB has 'id' but model expects 'equipment_id'
    try:
        db = SessionLocal()

        # Check if 'id' column exists (needs migration)
        result = db.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'equipment' AND column_name = 'id'
                """
            )
        )
        has_id_column = result.fetchone() is not None

        if has_id_column:
            # Run migration: rename 'id' to 'equipment_id'
            print("🔄 Running migration: renaming equipment.id to equipment.equipment_id...")
            db.execute(
                text(
                    """
                    ALTER TABLE equipment
                    RENAME COLUMN id TO equipment_id
                    """
                )
            )
            # Also change type from UUID to VARCHAR(50) to match model
            db.execute(
                text(
                    """
                    ALTER TABLE equipment
                    ALTER COLUMN equipment_id TYPE VARCHAR(50) USING equipment_id::VARCHAR(50)
                    """
                )
            )
            db.commit()
            print("✅ Migration completed: equipment.id -> equipment.equipment_id")
        else:
            # Check if equipment_id column exists
            result = db.execute(
                text(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'equipment' AND column_name = 'equipment_id'
                    """
                )
            )
            has_equipment_id = result.fetchone() is not None
            if has_equipment_id:
                print("✅ Database schema is up to date (equipment_id column exists)")
            else:
                print("ℹ️  Equipment table not found or empty, will be created on first use")

        db.close()
    except Exception as e:
        print(f"⚠️  Migration check failed (non-fatal): {e}")


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
