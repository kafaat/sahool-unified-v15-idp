"""
Migration Script: Migrate Password Hashes to Argon2id
سكريبت الترحيل: نقل تشفير كلمات المرور إلى Argon2id

This script migrates existing password hashes from bcrypt/PBKDF2 to Argon2id.
It can be run safely multiple times (idempotent).

Usage:
    python 011_migrate_passwords_to_argon2.py [--dry-run] [--batch-size=1000]

Options:
    --dry-run       Show what would be done without making changes
    --batch-size    Number of records to process per batch (default: 1000)
    --force         Force rehashing even for Argon2id hashes (parameter updates)
"""

import sys
from pathlib import Path
import argparse
import logging
from typing import List, Tuple
from datetime import datetime

# Add project root directory to path to import shared modules dynamically
BASE_DIR = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, BASE_DIR)

try:
    from shared.auth.password_hasher import (
        get_password_hasher,
        HashAlgorithm,
        PasswordHasher,
    )
except ImportError:
    print(
        "ERROR: Could not import password_hasher. Make sure argon2-cffi is installed."
    )
    print("Run: pip install argon2-cffi")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PasswordMigrator:
    """
    Migrates password hashes to Argon2id

    Note: This migrator does NOT have access to plaintext passwords.
    It can only flag passwords that need migration during next login.
    """

    def __init__(self, db_connection, dry_run: bool = False, force: bool = False):
        """
        Initialize migrator

        Args:
            db_connection: Database connection object
            dry_run: If True, don't make actual changes
            force: If True, rehash even Argon2id hashes
        """
        self.conn = db_connection
        self.dry_run = dry_run
        self.force = force
        self.hasher = get_password_hasher()
        self.stats = {
            "total": 0,
            "argon2id": 0,
            "bcrypt": 0,
            "pbkdf2": 0,
            "unknown": 0,
            "flagged_for_migration": 0,
            "errors": 0,
        }

    def analyze_hash(self, password_hash: str) -> HashAlgorithm:
        """
        Analyze a password hash to determine its algorithm

        Args:
            password_hash: The hashed password

        Returns:
            HashAlgorithm enum value
        """
        if password_hash.startswith("$argon2"):
            return HashAlgorithm.ARGON2ID
        elif (
            password_hash.startswith("$2a$")
            or password_hash.startswith("$2b$")
            or password_hash.startswith("$2y$")
        ):
            return HashAlgorithm.BCRYPT
        elif "$" in password_hash and len(password_hash.split("$")) >= 2:
            return HashAlgorithm.PBKDF2_SHA256
        else:
            return HashAlgorithm.UNKNOWN

    def get_users_to_migrate(
        self, batch_size: int = 1000, offset: int = 0
    ) -> List[Tuple]:
        """
        Get batch of users with passwords to potentially migrate

        Args:
            batch_size: Number of records to fetch
            offset: Offset for pagination

        Returns:
            List of (user_id, password_hash) tuples
        """
        cursor = self.conn.cursor()

        # Get users with password hashes
        query = """
            SELECT id, password_hash
            FROM users
            WHERE password_hash IS NOT NULL
            AND password_hash != ''
            ORDER BY id
            LIMIT %s OFFSET %s
        """

        cursor.execute(query, (batch_size, offset))
        results = cursor.fetchall()
        cursor.close()

        return results

    def flag_for_migration(self, user_id: str) -> bool:
        """
        Flag a user's password for migration on next login

        Args:
            user_id: User ID

        Returns:
            True if successful
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would flag user {user_id} for password migration")
            return True

        try:
            cursor = self.conn.cursor()

            # Add a column to track migration if it doesn't exist
            cursor.execute(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'users' AND column_name = 'password_needs_migration'
                    ) THEN
                        ALTER TABLE users ADD COLUMN password_needs_migration BOOLEAN DEFAULT FALSE;
                    END IF;
                END $$;
            """
            )

            # Flag the user for migration
            cursor.execute(
                """
                UPDATE users
                SET password_needs_migration = TRUE,
                    updated_at = NOW()
                WHERE id = %s
            """,
                (user_id,),
            )

            self.conn.commit()
            cursor.close()
            return True

        except Exception as e:
            logger.error(f"Error flagging user {user_id}: {e}")
            self.conn.rollback()
            return False

    def migrate_batch(self, batch_size: int = 1000, offset: int = 0) -> int:
        """
        Migrate a batch of password hashes

        Args:
            batch_size: Number of records to process
            offset: Offset for pagination

        Returns:
            Number of records processed
        """
        users = self.get_users_to_migrate(batch_size, offset)

        if not users:
            return 0

        for user_id, password_hash in users:
            self.stats["total"] += 1

            try:
                algorithm = self.analyze_hash(password_hash)

                # Count by algorithm
                if algorithm == HashAlgorithm.ARGON2ID:
                    self.stats["argon2id"] += 1
                    # Check if it needs rehashing due to parameter changes
                    if self.force and self.hasher.needs_rehash(password_hash):
                        self.flag_for_migration(user_id)
                        self.stats["flagged_for_migration"] += 1
                        logger.info(
                            f"User {user_id}: Argon2id hash needs parameter update"
                        )
                elif algorithm == HashAlgorithm.BCRYPT:
                    self.stats["bcrypt"] += 1
                    self.flag_for_migration(user_id)
                    self.stats["flagged_for_migration"] += 1
                    logger.info(f"User {user_id}: bcrypt hash flagged for migration")
                elif algorithm == HashAlgorithm.PBKDF2_SHA256:
                    self.stats["pbkdf2"] += 1
                    self.flag_for_migration(user_id)
                    self.stats["flagged_for_migration"] += 1
                    logger.info(f"User {user_id}: PBKDF2 hash flagged for migration")
                else:
                    self.stats["unknown"] += 1
                    logger.warning(f"User {user_id}: Unknown hash format")

            except Exception as e:
                self.stats["errors"] += 1
                logger.error(f"Error processing user {user_id}: {e}")

        return len(users)

    def migrate_all(self, batch_size: int = 1000):
        """
        Migrate all password hashes in batches

        Args:
            batch_size: Number of records per batch
        """
        logger.info("=" * 80)
        logger.info("Password Hash Migration to Argon2id")
        logger.info("=" * 80)

        if self.dry_run:
            logger.info("DRY RUN MODE - No changes will be made")

        offset = 0
        total_processed = 0

        while True:
            logger.info(f"\nProcessing batch at offset {offset}...")
            processed = self.migrate_batch(batch_size, offset)

            if processed == 0:
                break

            total_processed += processed
            offset += batch_size

            logger.info(f"Batch complete. Total processed: {total_processed}")

        self.print_summary()

    def print_summary(self):
        """Print migration summary"""
        logger.info("\n" + "=" * 80)
        logger.info("Migration Summary")
        logger.info("=" * 80)
        logger.info(f"Total users processed:       {self.stats['total']}")
        logger.info(
            f"  - Argon2id (up to date):   {self.stats['argon2id'] - self.stats.get('argon2id_updated', 0)}"
        )
        logger.info(f"  - bcrypt (legacy):         {self.stats['bcrypt']}")
        logger.info(f"  - PBKDF2 (legacy):         {self.stats['pbkdf2']}")
        logger.info(f"  - Unknown format:          {self.stats['unknown']}")
        logger.info(
            f"\nFlagged for migration:       {self.stats['flagged_for_migration']}"
        )
        logger.info(f"Errors:                      {self.stats['errors']}")
        logger.info("=" * 80)

        if self.stats["flagged_for_migration"] > 0:
            logger.info(
                "\nNOTE: Flagged users will have their passwords migrated to Argon2id"
            )
            logger.info("      automatically on their next successful login.")


def get_database_connection():
    """
    Get database connection

    Returns:
        Database connection object
    """
    try:
        import psycopg2
        import os

        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            # Try to construct from individual variables
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("DB_NAME", "sahool")
            db_user = os.getenv("DB_USER", "postgres")
            db_password = os.getenv("DB_PASSWORD", "")

            database_url = (
                f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            )

        conn = psycopg2.connect(database_url)
        return conn

    except ImportError:
        logger.error("psycopg2 not installed. Run: pip install psycopg2-binary")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Migrate password hashes to Argon2id")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Number of records to process per batch (default: 1000)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force rehashing even for Argon2id hashes (parameter updates)",
    )

    args = parser.parse_args()

    # Get database connection
    conn = get_database_connection()

    try:
        # Run migration
        migrator = PasswordMigrator(conn, dry_run=args.dry_run, force=args.force)
        migrator.migrate_all(batch_size=args.batch_size)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
