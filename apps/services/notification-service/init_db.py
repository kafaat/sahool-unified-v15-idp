#!/usr/bin/env python3
"""
SAHOOL Notification Service - Database Initialization Script
سكريبت تهيئة قاعدة البيانات

Usage:
    python init_db.py                    # Initialize with migrations
    python init_db.py --create-schema    # Create schema directly (dev only!)
    python init_db.py --check           # Check database health
"""

import argparse
import asyncio
import logging
import os
import sys

# Add notification-service root to path so 'from src.X import' works
sys.path.insert(0, os.path.dirname(__file__))

from src.database import (
    check_db_health,
    close_db,
    get_db_stats,
    init_notification_db,
    wait_for_db,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("init_db")


async def main():
    """Main initialization function"""
    parser = argparse.ArgumentParser(description="SAHOOL Notification Service Database Initialization")
    parser.add_argument(
        "--create-schema",
        action="store_true",
        help="Create database schema directly (development only!)",
    )
    parser.add_argument("--check", action="store_true", help="Check database health and exit")
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for database to be available (useful for Docker)",
    )

    args = parser.parse_args()

    try:
        # Wait for database if requested
        if args.wait:
            logger.info("Waiting for database to be available...")
            if not await wait_for_db(max_retries=10, retry_delay=3):
                logger.error("Database is not available after waiting")
                sys.exit(1)

        # Health check only
        if args.check:
            logger.info("Checking database health...")
            await init_notification_db(create_schema=False)

            health = await check_db_health()
            stats = await get_db_stats()

            logger.info("Database health: %s", health)
            logger.info("Database stats: %s", stats)

            await close_db()

            if health.get("status") == "healthy":
                logger.info("✅ Database is healthy!")
                sys.exit(0)
            else:
                logger.error("❌ Database is unhealthy!")
                sys.exit(1)

        # Initialize database
        logger.info("Initializing database...")

        if args.create_schema:
            logger.warning("⚠️  Creating schema directly - THIS SHOULD ONLY BE USED IN DEVELOPMENT!")
            logger.warning("⚠️  In production, use Aerich migrations instead!")

            await init_notification_db(create_schema=True)
            logger.info("✅ Database schema created successfully!")

        else:
            logger.info("Initializing database connection...")
            logger.info("To create schema, use: aerich init-db")
            logger.info("Or for development only: python init_db.py --create-schema")

            await init_notification_db(create_schema=False)

        # Get stats
        health = await check_db_health()
        stats = await get_db_stats()

        logger.info("Database health: %s", health)
        logger.info("Database stats: %s", stats)

        # Close connection
        await close_db()

        logger.info("✅ Database initialization completed!")
        sys.exit(0)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(130)

    except Exception as e:
        logger.error("❌ Database initialization failed: %s", e)
        logger.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
