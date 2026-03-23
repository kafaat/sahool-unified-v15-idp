"""
Mock Classes for Testing
=========================
فئات وهمية للاختبار

Mock implementations of common services for testing.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4


class MockDatabase:
    """
    Mock database for testing.
    قاعدة بيانات وهمية للاختبار

    Provides an in-memory store for testing database operations.
    """

    def __init__(self):
        self._store: dict[str, dict[str, Any]] = {}
        self._connected = False

    async def connect(self) -> bool:
        """Connect to mock database."""
        self._connected = True
        return True

    async def disconnect(self) -> None:
        """Disconnect from mock database."""
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected

    async def insert(self, table: str, data: dict) -> str:
        """Insert a record."""
        if table not in self._store:
            self._store[table] = {}

        record_id = data.get("id") or str(uuid4())
        data["id"] = record_id
        data["created_at"] = datetime.now(UTC).isoformat()
        data["updated_at"] = datetime.now(UTC).isoformat()

        self._store[table][record_id] = data
        return record_id

    async def get(self, table: str, record_id: str) -> dict | None:
        """Get a record by ID."""
        return self._store.get(table, {}).get(record_id)

    async def update(self, table: str, record_id: str, data: dict) -> bool:
        """Update a record."""
        if table not in self._store or record_id not in self._store[table]:
            return False

        self._store[table][record_id].update(data)
        self._store[table][record_id]["updated_at"] = datetime.now(UTC).isoformat()
        return True

    async def delete(self, table: str, record_id: str) -> bool:
        """Delete a record."""
        if table not in self._store or record_id not in self._store[table]:
            return False

        del self._store[table][record_id]
        return True

    async def query(self, table: str, filters: dict | None = None, limit: int = 100) -> list[dict]:
        """Query records with optional filters."""
        if table not in self._store:
            return []

        records = list(self._store[table].values())

        if filters:
            for key, value in filters.items():
                records = [r for r in records if r.get(key) == value]

        return records[:limit]

    async def count(self, table: str, filters: dict | None = None) -> int:
        """Count records."""
        records = await self.query(table, filters)
        return len(records)

    def clear(self) -> None:
        """Clear all data."""
        self._store.clear()

    def clear_table(self, table: str) -> None:
        """Clear a specific table."""
        if table in self._store:
            self._store[table].clear()


class MockEventPublisher:
    """
    Mock event publisher for testing.
    ناشر أحداث وهمي للاختبار
    """

    def __init__(self):
        self._connected = False
        self._published_events: list[tuple[str, Any]] = []
        self.publish_event = AsyncMock(side_effect=self._mock_publish)
        self.publish_events = AsyncMock(side_effect=self._mock_publish_batch)
        self.publish_json = AsyncMock(side_effect=self._mock_publish_json)

    async def connect(self) -> bool:
        """Connect to mock publisher."""
        self._connected = True
        return True

    async def close(self) -> None:
        """Close mock publisher."""
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected

    async def _mock_publish(self, subject: str, event: Any, **kwargs) -> bool:
        """Mock publish event."""
        self._published_events.append((subject, event))
        return True

    async def _mock_publish_batch(self, events: list[tuple[str, Any]], **kwargs) -> int:
        """Mock batch publish."""
        for subject, event in events:
            self._published_events.append((subject, event))
        return len(events)

    async def _mock_publish_json(self, subject: str, data: dict, **kwargs) -> bool:
        """Mock publish JSON."""
        self._published_events.append((subject, data))
        return True

    def get_published_events(self, subject: str | None = None) -> list:
        """Get published events, optionally filtered by subject."""
        if subject is None:
            return self._published_events.copy()
        return [(s, e) for s, e in self._published_events if s == subject]

    def clear(self) -> None:
        """Clear published events."""
        self._published_events.clear()
        self.publish_event.reset_mock()
        self.publish_events.reset_mock()
        self.publish_json.reset_mock()


class MockRedisClient:
    """
    Mock Redis client for testing.
    عميل Redis وهمي للاختبار
    """

    def __init__(self):
        self._store: dict[str, Any] = {}
        self._expiry: dict[str, float] = {}
        self._connected = False

    def connect(self) -> bool:
        """Connect to mock Redis."""
        self._connected = True
        return True

    def close(self) -> None:
        """Close mock Redis."""
        self._connected = False

    def ping(self) -> bool:
        """Ping mock Redis."""
        return self._connected

    def get(self, key: str) -> str | None:
        """Get a value."""
        self._check_expiry(key)
        return self._store.get(key)

    def set(
        self,
        key: str,
        value: Any,
        ex: int | None = None,
        px: int | None = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        """Set a value."""
        if nx and key in self._store:
            return False
        if xx and key not in self._store:
            return False

        self._store[key] = value

        if ex:
            import time

            self._expiry[key] = time.time() + ex
        elif px:
            import time

            self._expiry[key] = time.time() + (px / 1000)

        return True

    def delete(self, *keys: str) -> int:
        """Delete keys."""
        count = 0
        for key in keys:
            if key in self._store:
                del self._store[key]
                self._expiry.pop(key, None)
                count += 1
        return count

    def exists(self, *keys: str) -> int:
        """Check if keys exist."""
        count = 0
        for key in keys:
            self._check_expiry(key)
            if key in self._store:
                count += 1
        return count

    def expire(self, key: str, seconds: int) -> bool:
        """Set expiry on a key."""
        if key not in self._store:
            return False
        import time

        self._expiry[key] = time.time() + seconds
        return True

    def ttl(self, key: str) -> int:
        """Get TTL of a key."""
        if key not in self._store:
            return -2
        if key not in self._expiry:
            return -1
        import time

        remaining = int(self._expiry[key] - time.time())
        return max(0, remaining)

    def hset(self, name: str, key: str, value: Any) -> int:
        """Set hash field."""
        if name not in self._store:
            self._store[name] = {}
        is_new = key not in self._store[name]
        self._store[name][key] = value
        return 1 if is_new else 0

    def hget(self, name: str, key: str) -> Any:
        """Get hash field."""
        return self._store.get(name, {}).get(key)

    def hgetall(self, name: str) -> dict:
        """Get all hash fields."""
        return self._store.get(name, {}).copy()

    def hdel(self, name: str, *keys: str) -> int:
        """Delete hash fields."""
        if name not in self._store:
            return 0
        count = 0
        for key in keys:
            if key in self._store[name]:
                del self._store[name][key]
                count += 1
        return count

    def lpush(self, name: str, *values: Any) -> int:
        """Push to list head."""
        if name not in self._store:
            self._store[name] = []
        for value in reversed(values):
            self._store[name].insert(0, value)
        return len(self._store[name])

    def rpush(self, name: str, *values: Any) -> int:
        """Push to list tail."""
        if name not in self._store:
            self._store[name] = []
        self._store[name].extend(values)
        return len(self._store[name])

    def lpop(self, name: str) -> Any:
        """Pop from list head."""
        if name not in self._store or not self._store[name]:
            return None
        return self._store[name].pop(0)

    def rpop(self, name: str) -> Any:
        """Pop from list tail."""
        if name not in self._store or not self._store[name]:
            return None
        return self._store[name].pop()

    def lrange(self, name: str, start: int, end: int) -> list:
        """Get list range."""
        if name not in self._store:
            return []
        if end == -1:
            return self._store[name][start:]
        return self._store[name][start : end + 1]

    def sadd(self, name: str, *values: Any) -> int:
        """Add to set."""
        if name not in self._store:
            self._store[name] = set()
        before = len(self._store[name])
        self._store[name].update(values)
        return len(self._store[name]) - before

    def smembers(self, name: str) -> set:
        """Get set members."""
        return self._store.get(name, set()).copy()

    def srem(self, name: str, *values: Any) -> int:
        """Remove from set."""
        if name not in self._store:
            return 0
        count = 0
        for value in values:
            if value in self._store[name]:
                self._store[name].discard(value)
                count += 1
        return count

    def _check_expiry(self, key: str) -> None:
        """Check and remove expired keys."""
        if key in self._expiry:
            import time

            if time.time() > self._expiry[key]:
                del self._store[key]
                del self._expiry[key]

    def clear(self) -> None:
        """Clear all data."""
        self._store.clear()
        self._expiry.clear()


class MockNATSClient:
    """
    Mock NATS client for testing.
    عميل NATS وهمي للاختبار
    """

    def __init__(self):
        self._connected = False
        self._subscriptions: dict[str, list] = {}
        self._published: list[tuple[str, bytes]] = []
        self._jetstream = MockJetStream()

    async def connect(self, **kwargs) -> None:
        """Connect to mock NATS."""
        self._connected = True

    async def close(self) -> None:
        """Close mock NATS."""
        self._connected = False

    async def drain(self) -> None:
        """Drain mock NATS."""
        pass

    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected

    async def publish(self, subject: str, data: bytes, **kwargs) -> None:
        """Publish message."""
        self._published.append((subject, data))

        # Deliver to subscribers
        for pattern, callbacks in self._subscriptions.items():
            if self._matches_subject(subject, pattern):
                for callback in callbacks:
                    msg = MagicMock()
                    msg.subject = subject
                    msg.data = data
                    await callback(msg)

    async def subscribe(self, subject: str, cb=None, **kwargs):
        """Subscribe to subject."""
        if subject not in self._subscriptions:
            self._subscriptions[subject] = []
        if cb:
            self._subscriptions[subject].append(cb)

        sub = MagicMock()
        sub.unsubscribe = AsyncMock()
        return sub

    def jetstream(self, **kwargs):
        """Get JetStream context."""
        return self._jetstream

    def _matches_subject(self, subject: str, pattern: str) -> bool:
        """Check if subject matches pattern (simplified)."""
        if pattern.endswith(">"):
            return subject.startswith(pattern[:-1])
        if pattern.endswith("*"):
            parts = subject.split(".")
            pattern_parts = pattern[:-1].split(".")
            return parts[:-1] == pattern_parts[:-1]
        return subject == pattern

    def get_published(self, subject: str | None = None) -> list:
        """Get published messages."""
        if subject is None:
            return self._published.copy()
        return [(s, d) for s, d in self._published if s == subject]

    def clear(self) -> None:
        """Clear published messages."""
        self._published.clear()


class MockJetStream:
    """
    Mock JetStream context.
    سياق JetStream وهمي
    """

    def __init__(self):
        self._published: list[tuple[str, bytes]] = []

    async def publish(self, subject: str, data: bytes, **kwargs):
        """Publish to JetStream."""
        self._published.append((subject, data))

        ack = MagicMock()
        ack.stream = "test-stream"
        ack.seq = len(self._published)
        return ack

    async def subscribe(self, subject: str, **kwargs):
        """Subscribe to JetStream."""
        sub = MagicMock()
        sub.unsubscribe = AsyncMock()
        return sub

    def get_published(self) -> list:
        """Get published messages."""
        return self._published.copy()

    def clear(self) -> None:
        """Clear published messages."""
        self._published.clear()
