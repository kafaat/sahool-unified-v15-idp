#!/usr/bin/env python3
"""
SAHOOL Database Seed Runner
Runs all SQL seed files in order

Usage:
    python seed_runner.py --db-url postgresql://user:pass@localhost/sahool
    python seed_runner.py --env production
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("Error: psycopg2 not installed. Install with: pip install psycopg2-binary")
    sys.exit(1)


SEED_FILES = [
    "01_users.sql",
    "02_farms.sql",
    "03_fields.sql",
    "04_crops.sql",
    "05_weather_history.sql",
    "06_inventory.sql",
    "07_satellite_data.sql",
    "08_financial.sql",
]


class SeedRunner:
    """Database seed runner"""

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to database"""
        print(f"Connecting to database...")
        try:
            self.conn = psycopg2.connect(self.db_url)
            self.cursor = self.conn.cursor()
            print("✓ Connected successfully")
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            sys.exit(1)

    def disconnect(self):
        """Disconnect from database"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Disconnected from database")

    def run_seed_file(self, filepath: Path) -> bool:
        """Execute a single SQL seed file"""
        print(f"\nRunning {filepath.name}...")

        if not filepath.exists():
            print(f"✗ File not found: {filepath}")
            return False

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                sql_content = f.read()

            # Execute the SQL
            self.cursor.execute(sql_content)
            self.conn.commit()

            print(f"✓ {filepath.name} completed successfully")
            return True

        except Exception as e:
            print(f"✗ Error running {filepath.name}: {e}")
            self.conn.rollback()
            return False

    def run_all_seeds(self, seeds_dir: Path, continue_on_error: bool = False) -> bool:
        """Run all seed files in order"""
        print("=" * 60)
        print("SAHOOL Database Seeding")
        print("=" * 60)

        success_count = 0
        fail_count = 0

        for seed_file in SEED_FILES:
            filepath = seeds_dir / seed_file

            if self.run_seed_file(filepath):
                success_count += 1
            else:
                fail_count += 1
                if not continue_on_error:
                    print("\n✗ Seeding stopped due to error")
                    return False

        print("\n" + "=" * 60)
        print(f"Seeding completed: {success_count} succeeded, {fail_count} failed")
        print("=" * 60)

        return fail_count == 0

    def verify_database(self):
        """Verify database connection and show stats"""
        print("\nVerifying database...")

        queries = [
            ("Users", "SELECT COUNT(*) FROM users"),
            ("Farms", "SELECT COUNT(*) FROM farms"),
            ("Fields", "SELECT COUNT(*) FROM fields"),
            ("Crops", "SELECT COUNT(*) FROM crops"),
            ("Inventory Items", "SELECT COUNT(*) FROM inventory_items"),
            ("NDVI Observations", "SELECT COUNT(*) FROM ndvi_observations"),
        ]

        for name, query in queries:
            try:
                self.cursor.execute(query)
                count = self.cursor.fetchone()[0]
                print(f"  {name}: {count} records")
            except Exception as e:
                print(f"  {name}: Error - {e}")


def get_db_url_from_env(env: str) -> str:
    """Get database URL from environment variables"""
    env_map = {
        'development': 'DATABASE_URL_DEV',
        'staging': 'DATABASE_URL_STAGING',
        'production': 'DATABASE_URL_PROD',
    }

    env_var = env_map.get(env.lower(), 'DATABASE_URL')
    db_url = os.getenv(env_var)

    if not db_url:
        print(f"Error: Environment variable {env_var} not set")
        sys.exit(1)

    return db_url


def main():
    parser = argparse.ArgumentParser(description='SAHOOL Database Seed Runner')
    parser.add_argument(
        '--db-url',
        help='Database URL (postgresql://user:pass@host:port/dbname)'
    )
    parser.add_argument(
        '--env',
        choices=['development', 'staging', 'production'],
        help='Environment (uses DATABASE_URL_* env var)'
    )
    parser.add_argument(
        '--continue-on-error',
        action='store_true',
        help='Continue running seeds even if one fails'
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify database, do not run seeds'
    )

    args = parser.parse_args()

    # Get database URL
    if args.db_url:
        db_url = args.db_url
    elif args.env:
        db_url = get_db_url_from_env(args.env)
    else:
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("Error: Must provide --db-url or --env or set DATABASE_URL")
            parser.print_help()
            sys.exit(1)

    # Get seeds directory
    seeds_dir = Path(__file__).parent

    # Run seeding
    runner = SeedRunner(db_url)

    try:
        runner.connect()

        if args.verify_only:
            runner.verify_database()
        else:
            success = runner.run_all_seeds(seeds_dir, args.continue_on_error)
            runner.verify_database()

            if not success:
                sys.exit(1)

    finally:
        runner.disconnect()

    print("\n✓ All done!")


if __name__ == '__main__':
    main()
