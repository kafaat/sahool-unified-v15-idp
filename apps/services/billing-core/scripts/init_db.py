#!/usr/bin/env python3
"""
Database Initialization Script
سكريبت تهيئة قاعدة البيانات

This script initializes the billing-core database:
- Creates tables
- Sets up indexes
- Optionally seeds sample data

Usage:
    python scripts/init_db.py
    python scripts/init_db.py --seed
    python scripts/init_db.py --drop --seed
"""

import argparse
import asyncio
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import logging

from repository import BillingRepository

from database import check_db_connection, drop_db, get_db_context, init_db
from models import BillingCycle, Currency, SubscriptionStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_db")


async def seed_sample_data():
    """
    Seed the database with sample data for development/testing
    ملء قاعدة البيانات ببيانات نموذجية
    """
    logger.info("Seeding sample data...")

    async with get_db_context() as db:
        repo = BillingRepository(db)

        # Create sample subscriptions
        logger.info("Creating sample subscriptions...")

        # Active subscription
        subscription1 = await repo.subscriptions.create(
            tenant_id="tenant-001",
            plan_id="starter",
            billing_cycle=BillingCycle.MONTHLY,
            status=SubscriptionStatus.ACTIVE,
            start_date=date.today() - timedelta(days=15),
            end_date=date.today() + timedelta(days=15),
            currency=Currency.USD,
        )
        logger.info(f"Created subscription: {subscription1.id} (Active)")

        # Trial subscription
        subscription2 = await repo.subscriptions.create(
            tenant_id="tenant-002",
            plan_id="professional",
            billing_cycle=BillingCycle.MONTHLY,
            status=SubscriptionStatus.TRIAL,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            trial_end_date=date.today() + timedelta(days=14),
            currency=Currency.USD,
        )
        logger.info(f"Created subscription: {subscription2.id} (Trial)")

        # Create sample invoices
        logger.info("Creating sample invoices...")

        invoice1 = await repo.invoices.create(
            invoice_number="SAH-2025-0001",
            tenant_id="tenant-001",
            subscription_id=subscription1.id,
            currency=Currency.USD,
            issue_date=date.today() - timedelta(days=7),
            due_date=date.today(),
            subtotal=Decimal("29.00"),
            total=Decimal("29.00"),
            amount_due=Decimal("29.00"),
            line_items=[
                {
                    "description": "Starter Plan - Monthly",
                    "description_ar": "خطة المبتدئ - شهري",
                    "quantity": 1,
                    "unit_price": 29.00,
                    "amount": 29.00,
                }
            ],
        )
        logger.info(f"Created invoice: {invoice1.invoice_number}")

        # Create sample payment
        logger.info("Creating sample payment...")

        payment1 = await repo.payments.create(
            invoice_id=invoice1.id,
            tenant_id="tenant-001",
            amount=Decimal("29.00"),
            currency=Currency.USD,
            method="credit_card",
        )
        logger.info(f"Created payment: {payment1.id}")

        # Mark payment as succeeded
        await repo.payments.mark_succeeded(payment1.id)
        await repo.invoices.mark_paid(invoice1.id, Decimal("29.00"))

        logger.info("Sample payment marked as successful")

        # Create sample usage records
        logger.info("Creating sample usage records...")

        for i in range(5):
            await repo.usage_records.create(
                subscription_id=subscription1.id,
                tenant_id="tenant-001",
                metric_type="satellite_analyses_per_month",
                quantity=1,
            )

        logger.info("Created 5 usage records")

    logger.info("✓ Sample data seeded successfully!")


async def main():
    """Main initialization function"""
    parser = argparse.ArgumentParser(
        description="Initialize SAHOOL Billing Core database"
    )
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop all tables before creating (WARNING: deletes all data!)",
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed database with sample data after initialization",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check database connection without making changes",
    )

    args = parser.parse_args()

    # Check database connection
    logger.info("Checking database connection...")
    connected = await check_db_connection()

    if not connected:
        logger.error("❌ Database connection failed!")
        logger.error("Please check your DATABASE_URL environment variable")
        return 1

    logger.info("✓ Database connection successful")

    if args.check_only:
        logger.info("Check-only mode. Exiting.")
        return 0

    # Drop tables if requested
    if args.drop:
        logger.warning("⚠️  Dropping all tables...")
        confirm = input("Are you sure? This will delete all data! (yes/no): ")
        if confirm.lower() != "yes":
            logger.info("Aborted.")
            return 0

        await drop_db()
        logger.info("✓ All tables dropped")

    # Initialize database
    logger.info("Initializing database...")
    await init_db()
    logger.info("✓ Database initialized successfully")

    # Seed sample data if requested
    if args.seed:
        await seed_sample_data()

    logger.info("")
    logger.info("=" * 60)
    logger.info("Database initialization complete!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Start the service: python src/main.py")
    logger.info("2. Check health: curl http://localhost:8089/healthz")
    logger.info("3. View API docs: http://localhost:8089/docs")
    logger.info("")

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
