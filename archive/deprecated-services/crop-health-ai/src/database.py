"""
Database Configuration for Crop Health AI Service
تكوين قاعدة البيانات لخدمة صحة المحاصيل

This module provides database connection and initialization for the
Crop Health AI service using asyncpg with PostgreSQL.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sahool:sahool@localhost:5432/sahool")

# Connection pool
_pool = None


async def init_db():
    """
    Initialize database connection pool
    تهيئة مجموعة اتصالات قاعدة البيانات
    """
    global _pool

    if _pool is not None:
        return

    try:
        import asyncpg

        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=2,
            max_size=10,
            command_timeout=60,
        )
        logger.info("✅ Database connection pool initialized")

        # Create tables if they don't exist
        await _create_tables()

    except ImportError:
        logger.warning("asyncpg not available, database features disabled")
    except Exception as e:
        logger.error("Failed to initialize database: %s", str(e))
        raise


async def _create_tables():
    """
    Create database tables if they don't exist
    إنشاء جداول قاعدة البيانات إذا لم تكن موجودة
    """
    if _pool is None:
        return

    async with _pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS crop_diagnoses (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                image_url TEXT,
                thumbnail_url TEXT,
                disease_id VARCHAR(100),
                disease_name VARCHAR(255),
                disease_name_ar VARCHAR(255),
                confidence DECIMAL(5, 4),
                severity VARCHAR(50),
                crop_type VARCHAR(100),
                field_id VARCHAR(100),
                governorate VARCHAR(100),
                latitude DECIMAL(10, 8),
                longitude DECIMAL(11, 8),
                status VARCHAR(50) DEFAULT 'pending',
                farmer_id VARCHAR(100),
                expert_notes TEXT,
                recommendations JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );

            -- Create indexes for common queries
            CREATE INDEX IF NOT EXISTS idx_crop_diagnoses_field_id
                ON crop_diagnoses(field_id);
            CREATE INDEX IF NOT EXISTS idx_crop_diagnoses_governorate
                ON crop_diagnoses(governorate);
            CREATE INDEX IF NOT EXISTS idx_crop_diagnoses_farmer_id
                ON crop_diagnoses(farmer_id);
            CREATE INDEX IF NOT EXISTS idx_crop_diagnoses_created_at
                ON crop_diagnoses(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_crop_diagnoses_disease_id
                ON crop_diagnoses(disease_id);
            CREATE INDEX IF NOT EXISTS idx_crop_diagnoses_status
                ON crop_diagnoses(status);
        """)
        logger.info("✅ Database tables and indexes created")


async def close_db():
    """
    Close database connection pool
    إغلاق مجموعة اتصالات قاعدة البيانات
    """
    global _pool

    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("✅ Database connection pool closed")


@asynccontextmanager
async def get_connection() -> AsyncGenerator:
    """
    Get database connection from pool
    الحصول على اتصال من المجموعة
    """
    if _pool is None:
        raise RuntimeError("Database pool not initialized")

    async with _pool.acquire() as conn:
        yield conn


def is_db_available() -> bool:
    """Check if database is available"""
    return _pool is not None
