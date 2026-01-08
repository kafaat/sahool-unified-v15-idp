"""
Database Initialization and Configuration
تهيئة وإعداد قاعدة البيانات
"""

import logging
import os
import sys
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

# Import shared database components
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
from database.base import Base

# Import models to ensure they're registered with Base
from .models import Task

logger = logging.getLogger(__name__)

# Global engine and session factory
_engine = None
_SessionLocal = None


def get_database_url() -> str:
    """
    Get database URL from environment
    الحصول على رابط قاعدة البيانات من البيئة
    """
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        # Fallback to individual components
        user = os.getenv("POSTGRES_USER", "sahool")
        password = os.getenv("POSTGRES_PASSWORD", "")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        database = os.getenv("POSTGRES_DB", "sahool")

        database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"

    # Handle pgbouncer URLs that might have different schemes
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    return database_url


def init_database(create_tables: bool = True) -> None:
    """
    Initialize database connection and create tables
    تهيئة اتصال قاعدة البيانات وإنشاء الجداول

    Args:
        create_tables: Whether to create tables if they don't exist
    """
    global _engine, _SessionLocal

    if _engine is not None:
        logger.info("Database already initialized")
        return

    try:
        database_url = get_database_url()

        logger.info("Initializing database connection...")

        # Create engine with connection pooling
        _engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
            echo=os.getenv("SQL_ECHO", "false").lower() == "true",
        )

        # Create session factory
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=_engine,
        )

        # Add connection event listeners
        @event.listens_for(_engine, "connect")
        def on_connect(dbapi_connection, connection_record):
            logger.debug("Database connection established")

        # Test connection
        with _engine.connect() as conn:
            logger.info("Database connection test successful")

        # Create tables if requested
        if create_tables:
            logger.info("Creating database tables...")
            Base.metadata.create_all(bind=_engine)
            logger.info("Database tables created successfully")

        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise


def close_database() -> None:
    """
    Close database connections
    إغلاق اتصالات قاعدة البيانات
    """
    global _engine

    if _engine:
        _engine.dispose()
        logger.info("Database connections closed")


def get_db() -> Session:
    """
    Get a database session (for FastAPI Depends)
    الحصول على جلسة قاعدة بيانات (لـ FastAPI Depends)

    Usage in FastAPI:
        from fastapi import Depends

        @app.get("/tasks")
        def get_tasks(db: Session = Depends(get_db)):
            repo = TaskRepository(db)
            return repo.list_tasks(...)
    """
    if _SessionLocal is None:
        init_database()

    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """
    Context manager for database session
    مدير سياق لجلسة قاعدة البيانات

    Usage:
        with get_db_session() as db:
            repo = TaskRepository(db)
            task = repo.get_task_by_id(...)
    """
    if _SessionLocal is None:
        init_database()

    db = _SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def seed_demo_data(db: Session) -> None:
    """
    Seed demo tasks for testing
    إضافة مهام تجريبية للاختبار
    """
    from datetime import datetime, timedelta

    logger.info("Checking if demo data exists...")

    # Check if we already have tasks
    existing_tasks = db.query(Task).count()
    if existing_tasks > 0:
        logger.info(f"Demo data already exists ({existing_tasks} tasks)")
        return

    logger.info("Seeding demo data...")
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    demo_tasks = [
        Task(
            task_id="task_001",
            tenant_id="tenant_demo",
            title="Irrigate North Field",
            title_ar="ري الحقل الشمالي",
            description="Sector C needs irrigation using pump #2",
            description_ar="القطاع C يحتاج ري باستخدام مضخة رقم 2",
            task_type="irrigation",
            priority="high",
            status="pending",
            field_id="field_north",
            assigned_to="user_ahmed",
            created_by="user_admin",
            due_date=today + timedelta(hours=10),
            scheduled_time="08:00",
            estimated_duration_minutes=120,
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(days=1),
            metadata={"pump_id": "pump_2", "water_volume_m3": 500},
        ),
        Task(
            task_id="task_002",
            tenant_id="tenant_demo",
            title="Pest Inspection",
            title_ar="فحص الحشرات",
            description="Weekly pest inspection for tomato greenhouse",
            description_ar="فحص أسبوعي للحشرات في بيت الطماطم المحمي",
            task_type="scouting",
            priority="medium",
            status="completed",
            field_id="field_greenhouse",
            assigned_to="user_ahmed",
            created_by="user_admin",
            due_date=today + timedelta(hours=12),
            scheduled_time="10:30",
            estimated_duration_minutes=60,
            actual_duration_minutes=45,
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(hours=2),
            completed_at=now - timedelta(hours=2),
            completion_notes="No pests found. Healthy plants.",
        ),
        Task(
            task_id="task_003",
            tenant_id="tenant_demo",
            title="Collect Soil Samples",
            title_ar="جمع عينات التربة",
            description="Collect samples for nutrient analysis",
            description_ar="جمع عينات لتحليل المغذيات",
            task_type="sampling",
            priority="medium",
            status="pending",
            field_id="field_south",
            assigned_to="user_ahmed",
            created_by="user_admin",
            due_date=today + timedelta(hours=16),
            scheduled_time="14:00",
            estimated_duration_minutes=90,
            created_at=now - timedelta(hours=12),
            updated_at=now - timedelta(hours=12),
        ),
        Task(
            task_id="task_004",
            tenant_id="tenant_demo",
            title="Apply NPK Fertilizer",
            title_ar="تسميد التربة (NPK)",
            description="Apply 50kg/ha NPK to south field",
            description_ar="تطبيق 50 كجم/هكتار NPK للحقل الجنوبي",
            task_type="fertilization",
            priority="low",
            status="pending",
            field_id="field_south",
            assigned_to="user_mohammed",
            created_by="user_admin",
            due_date=today + timedelta(days=1),
            scheduled_time="07:00",
            estimated_duration_minutes=180,
            created_at=now - timedelta(hours=6),
            updated_at=now - timedelta(hours=6),
            metadata={"fertilizer_type": "NPK 20-20-20", "rate_kg_ha": 50},
        ),
        Task(
            task_id="task_005",
            tenant_id="tenant_demo",
            title="Irrigation System Maintenance",
            title_ar="صيانة نظام الري",
            description="Check filters and valves",
            description_ar="فحص الفلاتر والصمامات",
            task_type="maintenance",
            priority="medium",
            status="pending",
            field_id="field_north",
            assigned_to="user_tech",
            created_by="user_admin",
            due_date=today + timedelta(days=2),
            created_at=now - timedelta(hours=3),
            updated_at=now - timedelta(hours=3),
        ),
        Task(
            task_id="task_006",
            tenant_id="tenant_demo",
            title="Fungicide Spray",
            title_ar="رش مبيد فطري",
            description="Preventive spray for east field",
            description_ar="رش وقائي للحقل الشرقي",
            task_type="spraying",
            priority="high",
            status="pending",
            field_id="field_east",
            assigned_to="user_ahmed",
            created_by="user_admin",
            due_date=today + timedelta(days=3),
            scheduled_time="06:00",
            estimated_duration_minutes=150,
            created_at=now - timedelta(hours=1),
            updated_at=now - timedelta(hours=1),
            metadata={"chemical": "Mancozeb", "rate_ml_ha": 2500},
        ),
    ]

    try:
        for task in demo_tasks:
            db.add(task)

        db.commit()
        logger.info(f"Seeded {len(demo_tasks)} demo tasks")

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding demo data: {e}", exc_info=True)
        raise


def init_demo_data_if_needed() -> None:
    """
    Initialize demo data if the database is empty
    تهيئة البيانات التجريبية إذا كانت قاعدة البيانات فارغة
    """
    # Only seed if SEED_DEMO_DATA is set to true
    if os.getenv("SEED_DEMO_DATA", "true").lower() == "true":
        with get_db_session() as db:
            seed_demo_data(db)
