#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════════════
SAHOOL IDP - Cache Invalidation Manager
مدير إبطال ذاكرة التخزين المؤقت
═══════════════════════════════════════════════════════════════════════════════════════

Closes the "Database Sync Gap" by ensuring cache consistency after data changes.

Features:
- Invalidate cache after database migrations
- Pattern-based cache key deletion
- Cache-aside strategy implementation
- Event-driven invalidation via Redis pub/sub

Usage:
    # Invalidate all field-related cache after orphaned data cleanup
    python cache_invalidation_manager.py --pattern "field:*" --reason "orphaned_data_cleanup"

    # Full cache flush (use with caution)
    python cache_invalidation_manager.py --flush-all --confirm

    # Listen for database change events
    python cache_invalidation_manager.py --listen

═══════════════════════════════════════════════════════════════════════════════════════
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime

try:
    import redis.asyncio as aioredis
except ImportError:
    try:
        import aioredis
    except ImportError:
        print("Error: redis/aioredis is required. Install with: pip install redis")
        sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("cache-invalidation")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Cache key patterns used by SAHOOL services
CACHE_PATTERNS = {
    "fields": ["field:*", "fields:user:*", "field_list:*"],
    "users": ["user:*", "user_session:*", "auth:*"],
    "sensor_data": ["sensor:*", "sensor_readings:*", "iot:*"],
    "tasks": ["task:*", "tasks:field:*", "task_list:*"],
    "weather": ["weather:*", "forecast:*"],
    "sessions": ["session:*", "jwt:*", "refresh_token:*"],
}

# Pub/Sub channel for cache invalidation events
INVALIDATION_CHANNEL = "sahool:cache:invalidate"

# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class InvalidationEvent:
    timestamp: str
    pattern: str
    reason: str
    keys_affected: int
    initiated_by: str = "system"
    source_operation: str = "manual"

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


@dataclass
class InvalidationReport:
    timestamp: str
    total_keys_deleted: int
    patterns_processed: list[str]
    events: list[dict]
    duration_ms: float

    def print_summary(self):
        print("\n" + "=" * 70)
        print("  🗑️ CACHE INVALIDATION REPORT")
        print("  تقرير إبطال ذاكرة التخزين المؤقت")
        print("=" * 70)
        print(f"  Timestamp:    {self.timestamp}")
        print(f"  Duration:     {self.duration_ms:.2f}ms")
        print(f"  Keys Deleted: {self.total_keys_deleted}")
        print("")
        print("  Patterns Processed:")
        for pattern in self.patterns_processed:
            print(f"    • {pattern}")
        print("=" * 70 + "\n")


# ═══════════════════════════════════════════════════════════════════════════════
# CACHE INVALIDATION MANAGER
# ═══════════════════════════════════════════════════════════════════════════════


class CacheInvalidationManager:
    """Manages cache invalidation to maintain database-cache consistency."""

    def __init__(self, redis_url: str = REDIS_URL):
        self.redis_url = redis_url
        self.redis: aioredis.Redis | None = None
        self.events: list[InvalidationEvent] = []

    async def connect(self):
        """Establish Redis connection."""
        try:
            self.redis = await aioredis.from_url(
                self.redis_url,
                password=REDIS_PASSWORD,
                decode_responses=True,
            )
            await self.redis.ping()
            logger.info("✅ Connected to Redis")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise

    async def disconnect(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()

    async def invalidate_pattern(
        self,
        pattern: str,
        reason: str = "manual",
        batch_size: int = 100,
    ) -> int:
        """
        Invalidate all keys matching a pattern.
        Uses SCAN for memory-efficient iteration.
        """
        if not self.redis:
            await self.connect()

        total_deleted = 0
        cursor = 0
        keys_to_delete = []

        logger.info(f"🔍 Scanning for pattern: {pattern}")

        # Use SCAN to iterate without blocking
        while True:
            cursor, keys = await self.redis.scan(
                cursor=cursor,
                match=pattern,
                count=batch_size,
            )

            if keys:
                keys_to_delete.extend(keys)

            # Delete in batches to prevent memory issues
            if len(keys_to_delete) >= batch_size:
                deleted = await self.redis.delete(*keys_to_delete)
                total_deleted += deleted
                logger.info(f"  🗑️ Deleted {deleted} keys")
                keys_to_delete = []

            if cursor == 0:
                break

        # Delete remaining keys
        if keys_to_delete:
            deleted = await self.redis.delete(*keys_to_delete)
            total_deleted += deleted

        # Log event
        event = InvalidationEvent(
            timestamp=datetime.now(UTC).isoformat(),
            pattern=pattern,
            reason=reason,
            keys_affected=total_deleted,
            source_operation="pattern_invalidation",
        )
        self.events.append(event)

        # Publish invalidation event for distributed systems
        await self._publish_event(event)

        logger.info(f"✅ Invalidated {total_deleted} keys for pattern: {pattern}")
        return total_deleted

    async def invalidate_entity(
        self,
        entity_type: str,
        entity_ids: list[str],
        reason: str = "entity_update",
    ) -> int:
        """
        Invalidate cache for specific entities.
        Used after database updates/deletes.
        """
        if not self.redis:
            await self.connect()

        patterns = CACHE_PATTERNS.get(entity_type, [])
        total_deleted = 0

        for entity_id in entity_ids:
            for pattern_template in patterns:
                # Replace wildcard with specific ID
                if "*" in pattern_template:
                    specific_key = pattern_template.replace("*", entity_id)
                else:
                    specific_key = f"{pattern_template}:{entity_id}"

                # Try exact key first
                deleted = await self.redis.delete(specific_key)
                if deleted:
                    total_deleted += deleted
                else:
                    # Fall back to pattern scan
                    deleted = await self.invalidate_pattern(
                        f"*{entity_id}*",
                        reason=reason,
                    )
                    total_deleted += deleted

        return total_deleted

    async def invalidate_after_migration(
        self,
        migration_name: str,
        affected_tables: list[str],
    ) -> InvalidationReport:
        """
        Comprehensive cache invalidation after database migration.
        This is the key function to close the "Database Sync Gap".
        """
        start_time = datetime.now()
        total_deleted = 0
        patterns_processed = []

        logger.info("=" * 70)
        logger.info("  🔄 POST-MIGRATION CACHE INVALIDATION")
        logger.info(f"  Migration: {migration_name}")
        logger.info("=" * 70)

        for table in affected_tables:
            # Map table names to cache patterns
            patterns = CACHE_PATTERNS.get(table, [])

            if not patterns:
                # Generic pattern based on table name
                patterns = [f"{table}:*", f"{table}_*"]

            for pattern in patterns:
                deleted = await self.invalidate_pattern(
                    pattern,
                    reason=f"migration:{migration_name}",
                )
                total_deleted += deleted
                patterns_processed.append(pattern)

        # Also invalidate related caches that might reference deleted data
        if "fields" in affected_tables:
            # Sensor data might reference deleted fields
            await self.invalidate_pattern("sensor_readings:*", reason="cascade")
            patterns_processed.append("sensor_readings:*")

            # Tasks might reference deleted fields
            await self.invalidate_pattern("task:*", reason="cascade")
            patterns_processed.append("task:*")

        # Generate report
        duration = (datetime.now() - start_time).total_seconds() * 1000

        report = InvalidationReport(
            timestamp=datetime.now(UTC).isoformat(),
            total_keys_deleted=total_deleted,
            patterns_processed=patterns_processed,
            events=[asdict(e) for e in self.events],
            duration_ms=duration,
        )

        return report

    async def flush_all(self, confirm: bool = False) -> int:
        """
        Flush all cache keys. Use with extreme caution!
        """
        if not confirm:
            logger.warning("❌ flush_all requires --confirm flag")
            return 0

        if not self.redis:
            await self.connect()

        # Get count before flush
        info = await self.redis.info("keyspace")
        keys_before = 0
        for db_info in info.values():
            if isinstance(db_info, dict):
                keys_before += db_info.get("keys", 0)

        logger.warning("⚠️ FLUSHING ALL CACHE KEYS...")
        await self.redis.flushall()

        logger.info(f"✅ Flushed {keys_before} keys")
        return keys_before

    async def _publish_event(self, event: InvalidationEvent):
        """Publish invalidation event for distributed cache coordination."""
        try:
            await self.redis.publish(INVALIDATION_CHANNEL, event.to_json())
        except Exception as e:
            logger.warning(f"Could not publish event: {e}")

    async def listen_for_events(self):
        """
        Listen for cache invalidation events from other services.
        Used for distributed cache coordination.
        """
        if not self.redis:
            await self.connect()

        pubsub = self.redis.pubsub()
        await pubsub.subscribe(INVALIDATION_CHANNEL)

        logger.info(f"📡 Listening for cache invalidation events on: {INVALIDATION_CHANNEL}")

        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    event_data = json.loads(message["data"])
                    logger.info(f"📥 Received invalidation event: {event_data['pattern']}")

                    # Process the invalidation locally
                    await self.invalidate_pattern(
                        event_data["pattern"],
                        reason=f"distributed:{event_data.get('reason', 'unknown')}",
                    )
                except json.JSONDecodeError:
                    logger.warning(f"Invalid event data: {message['data']}")


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION WITH DATA INTEGRITY CHECKER
# ═══════════════════════════════════════════════════════════════════════════════


async def invalidate_after_orphaned_data_cleanup(
    deleted_field_ids: list[str],
    deleted_sensor_ids: list[str],
    deleted_task_ids: list[str],
) -> InvalidationReport:
    """
    Called after data_integrity_checker.py cleans orphaned records.
    Ensures cache doesn't serve stale/deleted data (Cache Poisoning prevention).
    """
    manager = CacheInvalidationManager()

    try:
        await manager.connect()

        logger.info("=" * 70)
        logger.info("  🔄 CACHE INVALIDATION AFTER ORPHANED DATA CLEANUP")
        logger.info(f"  Fields deleted: {len(deleted_field_ids)}")
        logger.info(f"  Sensors deleted: {len(deleted_sensor_ids)}")
        logger.info(f"  Tasks deleted: {len(deleted_task_ids)}")
        logger.info("=" * 70)

        total_deleted = 0

        # Invalidate field caches
        if deleted_field_ids:
            deleted = await manager.invalidate_entity(
                "fields",
                deleted_field_ids,
                reason="orphaned_data_cleanup",
            )
            total_deleted += deleted

        # Invalidate sensor caches
        if deleted_sensor_ids:
            deleted = await manager.invalidate_entity(
                "sensor_data",
                deleted_sensor_ids,
                reason="orphaned_data_cleanup",
            )
            total_deleted += deleted

        # Invalidate task caches
        if deleted_task_ids:
            deleted = await manager.invalidate_entity(
                "tasks",
                deleted_task_ids,
                reason="orphaned_data_cleanup",
            )
            total_deleted += deleted

        # Also invalidate list caches that might contain deleted IDs
        await manager.invalidate_pattern("field_list:*", reason="list_refresh")
        await manager.invalidate_pattern("task_list:*", reason="list_refresh")

        logger.info(f"✅ Total cache keys invalidated: {total_deleted}")

        return InvalidationReport(
            timestamp=datetime.now(UTC).isoformat(),
            total_keys_deleted=total_deleted,
            patterns_processed=["fields", "sensor_data", "tasks", "lists"],
            events=[asdict(e) for e in manager.events],
            duration_ms=0,
        )

    finally:
        await manager.disconnect()


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════


async def main():
    parser = argparse.ArgumentParser(
        description="SAHOOL Cache Invalidation Manager - مدير إبطال ذاكرة التخزين المؤقت"
    )

    parser.add_argument(
        "--pattern", "-p", type=str, help="Cache key pattern to invalidate (e.g., 'field:*')"
    )
    parser.add_argument(
        "--reason", "-r", type=str, default="manual", help="Reason for invalidation"
    )
    parser.add_argument(
        "--entity-type",
        "-e",
        type=str,
        choices=["fields", "users", "sensor_data", "tasks", "weather", "sessions"],
        help="Entity type to invalidate",
    )
    parser.add_argument("--entity-ids", type=str, help="Comma-separated entity IDs to invalidate")
    parser.add_argument(
        "--migration", "-m", type=str, help="Migration name for post-migration invalidation"
    )
    parser.add_argument(
        "--tables", "-t", type=str, help="Comma-separated table names affected by migration"
    )
    parser.add_argument("--flush-all", action="store_true", help="Flush all cache keys (DANGEROUS)")
    parser.add_argument("--confirm", action="store_true", help="Confirm dangerous operations")
    parser.add_argument("--listen", action="store_true", help="Listen for invalidation events")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    manager = CacheInvalidationManager()

    try:
        await manager.connect()

        if args.listen:
            await manager.listen_for_events()

        elif args.flush_all:
            deleted = await manager.flush_all(confirm=args.confirm)
            print(f"Flushed {deleted} keys")

        elif args.migration and args.tables:
            tables = [t.strip() for t in args.tables.split(",")]
            report = await manager.invalidate_after_migration(args.migration, tables)
            report.print_summary()

        elif args.entity_type and args.entity_ids:
            entity_ids = [e.strip() for e in args.entity_ids.split(",")]
            deleted = await manager.invalidate_entity(
                args.entity_type,
                entity_ids,
                reason=args.reason,
            )
            print(f"Invalidated {deleted} cache keys")

        elif args.pattern:
            deleted = await manager.invalidate_pattern(
                args.pattern,
                reason=args.reason,
            )
            print(f"Invalidated {deleted} keys matching pattern: {args.pattern}")

        else:
            parser.print_help()

    finally:
        await manager.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
