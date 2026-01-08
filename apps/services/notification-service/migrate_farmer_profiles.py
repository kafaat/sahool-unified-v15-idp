#!/usr/bin/env python3
"""
SAHOOL Notification Service - Farmer Profile Migration Script
نص ترحيل ملفات المزارعين - Migration to PostgreSQL

This script creates the necessary database tables for farmer profiles:
- farmer_profiles: Main farmer information
- farmer_crops: Junction table for farmer's crops
- farmer_fields: Junction table for farmer's fields

Usage:
    python migrate_farmer_profiles.py

Requirements:
    - DATABASE_URL environment variable must be set
    - PostgreSQL database must be running and accessible
"""

import asyncio
import logging
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from database import init_db, close_db, check_db_health
from models import FarmerProfile, FarmerCrop, FarmerField
from repository import FarmerProfileRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migration")


async def migrate():
    """Run the migration"""
    logger.info("=" * 80)
    logger.info("SAHOOL Notification Service - Farmer Profile Migration")
    logger.info("=" * 80)

    # Check database URL
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("❌ DATABASE_URL environment variable not set!")
        logger.error("   Set it in .env file or export it:")
        logger.error("   export DATABASE_URL='postgresql://user:password@localhost:5432/sahool_notifications'")
        return False

    logger.info(f"Database URL: {db_url.split('@')[1] if '@' in db_url else 'configured'}")

    try:
        # Initialize database connection
        logger.info("\n📊 Initializing database connection...")
        await init_db(create_db=True)  # create_db=True will generate schemas
        logger.info("✅ Database initialized")

        # Check health
        logger.info("\n🏥 Checking database health...")
        health = await check_db_health()
        if not health.get("connected"):
            logger.error(f"❌ Database not healthy: {health}")
            return False
        logger.info("✅ Database is healthy")

        # Verify tables were created
        logger.info("\n🔍 Verifying tables...")
        try:
            # Try to query each table
            await FarmerProfile.all().count()
            logger.info("✅ farmer_profiles table exists")

            await FarmerCrop.all().count()
            logger.info("✅ farmer_crops table exists")

            await FarmerField.all().count()
            logger.info("✅ farmer_fields table exists")

        except Exception as e:
            logger.error(f"❌ Error verifying tables: {e}")
            return False

        # Insert test data (optional)
        logger.info("\n📝 Creating sample farmer profiles for testing...")
        try:
            # Sample farmer 1
            farmer1 = await FarmerProfileRepository.create(
                farmer_id="test-farmer-1",
                name="Ahmed Ali",
                name_ar="أحمد علي",
                governorate="sanaa",
                district="Bani Harith",
                crops=["tomato", "coffee"],
                field_ids=["field-001", "field-002"],
                phone="+967771234567",
                email="ahmed.ali@example.com",
                language="ar",
            )
            logger.info(f"✅ Created test farmer: {farmer1.farmer_id}")

            # Sample farmer 2
            farmer2 = await FarmerProfileRepository.create(
                farmer_id="test-farmer-2",
                name="Mohammed Hassan",
                name_ar="محمد حسن",
                governorate="ibb",
                district="Ibb City",
                crops=["banana", "mango"],
                field_ids=["field-003"],
                phone="+967772345678",
                email="mohammed.hassan@example.com",
                language="ar",
            )
            logger.info(f"✅ Created test farmer: {farmer2.farmer_id}")

            # Verify count
            count = await FarmerProfileRepository.get_count()
            logger.info(f"✅ Total farmers in database: {count}")

        except Exception as e:
            logger.warning(f"⚠️  Could not create test data (might already exist): {e}")

        logger.info("\n" + "=" * 80)
        logger.info("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        logger.info("\nNext steps:")
        logger.info("1. Verify the tables in your PostgreSQL database:")
        logger.info("   psql -d sahool_notifications -c '\\dt'")
        logger.info("2. Check the farmer_profiles table:")
        logger.info("   psql -d sahool_notifications -c 'SELECT * FROM farmer_profiles;'")
        logger.info("3. Start the notification service:")
        logger.info("   uvicorn src.main:app --reload")
        logger.info("")

        return True

    except Exception as e:
        logger.error(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Close database connection
        logger.info("\n🔌 Closing database connection...")
        await close_db()
        logger.info("✅ Database connection closed")


async def rollback():
    """Rollback the migration (drop tables)"""
    logger.warning("=" * 80)
    logger.warning("ROLLBACK - This will DROP all farmer profile tables!")
    logger.warning("=" * 80)

    response = input("Are you sure you want to drop all farmer tables? (type 'yes' to confirm): ")
    if response.lower() != "yes":
        logger.info("Rollback cancelled")
        return

    try:
        await init_db(create_db=False)

        from tortoise import Tortoise

        # Drop tables in reverse order (to handle foreign keys)
        logger.info("Dropping farmer_fields table...")
        await Tortoise.get_connection("default").execute_query("DROP TABLE IF EXISTS farmer_fields CASCADE")

        logger.info("Dropping farmer_crops table...")
        await Tortoise.get_connection("default").execute_query("DROP TABLE IF EXISTS farmer_crops CASCADE")

        logger.info("Dropping farmer_profiles table...")
        await Tortoise.get_connection("default").execute_query("DROP TABLE IF EXISTS farmer_profiles CASCADE")

        logger.info("✅ Rollback completed - all farmer tables dropped")

    except Exception as e:
        logger.error(f"❌ Rollback failed: {e}")
    finally:
        await close_db()


if __name__ == "__main__":
    import sys

    # Check for rollback flag
    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        asyncio.run(rollback())
    else:
        success = asyncio.run(migrate())
        sys.exit(0 if success else 1)
