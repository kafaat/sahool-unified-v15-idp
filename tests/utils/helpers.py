"""
Test Helper Functions
=====================
دوال مساعدة للاختبار

Common helper functions for testing.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import functools
import os
from datetime import UTC, datetime, timedelta
from typing import Any, Awaitable, Callable
from unittest.mock import AsyncMock, MagicMock


def async_test(func: Callable[..., Awaitable]) -> Callable:
    """
    Decorator for running async test functions.
    مزخرف لتشغيل دوال الاختبار غير المتزامنة

    Usage:
        @async_test
        async def test_something():
            await some_async_function()

    Note: Prefer using pytest.mark.asyncio when available.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


def create_test_token(
    user_id: str = "test-user-123",
    roles: list[str] | None = None,
    permissions: list[str] | None = None,
    tenant_id: str = "test-tenant-456",
    expires_in_hours: int = 1,
) -> str:
    """
    Create a JWT token for testing.
    إنشاء رمز JWT للاختبار

    Args:
        user_id: User ID
        roles: User roles
        permissions: User permissions
        tenant_id: Tenant ID
        expires_in_hours: Token expiration in hours

    Returns:
        JWT token string
    """
    try:
        import jwt

        secret_key = os.environ.get("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
        algorithm = os.environ.get("JWT_ALGORITHM", "HS256")

        payload = {
            "sub": user_id,
            "tid": tenant_id,
            "roles": roles or ["farmer"],
            "permissions": permissions or [],
            "iss": os.environ.get("JWT_ISSUER", "sahool-idp"),
            "aud": os.environ.get("JWT_AUDIENCE", "sahool-platform"),
            "exp": datetime.now(UTC) + timedelta(hours=expires_in_hours),
            "iat": datetime.now(UTC),
            "type": "access",
        }

        return jwt.encode(payload, secret_key, algorithm=algorithm)
    except ImportError:
        return "test-token-placeholder"


def mock_nats_client() -> tuple[AsyncMock, AsyncMock]:
    """
    Create a mock NATS client.
    إنشاء عميل NATS وهمي

    Returns:
        Tuple of (nats_client, jetstream_context)
    """
    mock_nc = AsyncMock()
    mock_nc.publish = AsyncMock()
    mock_nc.subscribe = AsyncMock()
    mock_nc.drain = AsyncMock()
    mock_nc.close = AsyncMock()
    mock_nc.is_connected = True

    mock_js = AsyncMock()
    mock_ack = MagicMock()
    mock_ack.stream = "test-stream"
    mock_ack.seq = 1
    mock_js.publish = AsyncMock(return_value=mock_ack)
    mock_js.subscribe = AsyncMock()

    mock_nc.jetstream.return_value = mock_js

    return mock_nc, mock_js


def mock_redis_client() -> MagicMock:
    """
    Create a mock Redis client.
    إنشاء عميل Redis وهمي

    Returns:
        Mock Redis client
    """
    mock = MagicMock()

    # String operations
    mock.get = MagicMock(return_value=None)
    mock.set = MagicMock(return_value=True)
    mock.delete = MagicMock(return_value=1)
    mock.exists = MagicMock(return_value=1)
    mock.expire = MagicMock(return_value=True)
    mock.ttl = MagicMock(return_value=3600)

    # Hash operations
    mock.hget = MagicMock(return_value=None)
    mock.hset = MagicMock(return_value=1)
    mock.hgetall = MagicMock(return_value={})
    mock.hdel = MagicMock(return_value=1)

    # List operations
    mock.lpush = MagicMock(return_value=1)
    mock.rpush = MagicMock(return_value=1)
    mock.lpop = MagicMock(return_value=None)
    mock.rpop = MagicMock(return_value=None)
    mock.lrange = MagicMock(return_value=[])

    # Set operations
    mock.sadd = MagicMock(return_value=1)
    mock.smembers = MagicMock(return_value=set())
    mock.srem = MagicMock(return_value=1)

    # Connection
    mock.ping = MagicMock(return_value=True)
    mock.close = MagicMock()

    return mock


async def wait_for_condition(
    condition: Callable[[], bool] | Callable[[], Awaitable[bool]],
    timeout: float = 5.0,
    interval: float = 0.1,
    message: str = "Condition not met within timeout",
) -> bool:
    """
    Wait for a condition to become true.
    انتظار حتى يصبح الشرط صحيحًا

    Args:
        condition: Function that returns True when condition is met
        timeout: Maximum time to wait in seconds
        interval: Time between checks in seconds
        message: Error message if timeout

    Returns:
        True if condition was met

    Raises:
        TimeoutError: If condition not met within timeout
    """
    start_time = asyncio.get_event_loop().time()

    while True:
        result = condition()
        if asyncio.iscoroutine(result):
            result = await result

        if result:
            return True

        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed >= timeout:
            raise TimeoutError(f"{message} (waited {elapsed:.2f}s)")

        await asyncio.sleep(interval)


def with_timeout(timeout: float = 5.0):
    """
    Decorator to add timeout to async test.
    مزخرف لإضافة مهلة للاختبار غير المتزامن

    Args:
        timeout: Timeout in seconds

    Usage:
        @with_timeout(10.0)
        async def test_slow_operation():
            await slow_function()
    """

    def decorator(func: Callable[..., Awaitable]) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)

        return wrapper

    return decorator


def freeze_time(dt: datetime):
    """
    Context manager to freeze time for testing.
    مدير سياق لتجميد الوقت للاختبار

    Args:
        dt: Datetime to freeze to

    Note: This is a simplified version. For production, use freezegun library.
    """
    from unittest.mock import patch

    class FrozenDatetime:
        """Frozen datetime class."""

        @classmethod
        def now(cls, tz=None):
            return dt.replace(tzinfo=tz) if tz else dt

        @classmethod
        def utcnow(cls):
            return dt

    return patch("datetime.datetime", FrozenDatetime)


def generate_test_data(
    schema: dict,
    count: int = 1,
) -> list[dict]:
    """
    Generate test data based on schema.
    توليد بيانات اختبار بناءً على المخطط

    Args:
        schema: Schema definition with types
        count: Number of records to generate

    Returns:
        List of generated data dictionaries

    Example:
        schema = {
            "name": str,
            "age": int,
            "active": bool,
            "score": float,
        }
        data = generate_test_data(schema, count=5)
    """
    import random
    import string
    from uuid import uuid4

    def generate_value(value_type):
        if value_type == str:
            return "".join(random.choices(string.ascii_letters, k=10))
        elif value_type == int:
            return random.randint(1, 1000)
        elif value_type == float:
            return round(random.uniform(0, 100), 2)
        elif value_type == bool:
            return random.choice([True, False])
        elif value_type == "uuid":
            return str(uuid4())
        elif value_type == "email":
            name = "".join(random.choices(string.ascii_lowercase, k=8))
            return f"{name}@test.com"
        elif value_type == "date":
            return datetime.now(UTC).date().isoformat()
        elif value_type == "datetime":
            return datetime.now(UTC).isoformat()
        else:
            return None

    results = []
    for _ in range(count):
        record = {}
        for key, value_type in schema.items():
            record[key] = generate_value(value_type)
        results.append(record)

    return results


def assert_logs_contain(
    caplog,
    level: str,
    message_substring: str,
) -> None:
    """
    Assert that logs contain expected message.
    التحقق من أن السجلات تحتوي على الرسالة المتوقعة

    Args:
        caplog: pytest caplog fixture
        level: Expected log level (DEBUG, INFO, WARNING, ERROR)
        message_substring: Substring that should appear in log message
    """
    matching_logs = [
        record for record in caplog.records if record.levelname == level and message_substring in record.message
    ]

    assert len(matching_logs) > 0, (
        f"No {level} log containing '{message_substring}' found. Logs: {[r.message for r in caplog.records]}"
    )


def create_api_headers(
    token: str | None = None,
    tenant_id: str = "test-tenant",
    user_id: str = "test-user",
    content_type: str = "application/json",
) -> dict:
    """
    Create API request headers.
    إنشاء ترويسات طلب API

    Args:
        token: JWT token (creates one if not provided)
        tenant_id: Tenant ID
        user_id: User ID
        content_type: Content-Type header

    Returns:
        Headers dictionary
    """
    if token is None:
        token = create_test_token(user_id=user_id, tenant_id=tenant_id)

    return {
        "Content-Type": content_type,
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": tenant_id,
        "X-Request-ID": f"test-{datetime.now(UTC).timestamp()}",
    }


def compare_dicts(
    expected: dict,
    actual: dict,
    ignore_keys: list[str] | None = None,
) -> list[str]:
    """
    Compare two dictionaries and return differences.
    مقارنة قاموسين وإرجاع الفروقات

    Args:
        expected: Expected dictionary
        actual: Actual dictionary
        ignore_keys: Keys to ignore in comparison

    Returns:
        List of difference descriptions
    """
    ignore_keys = ignore_keys or []
    differences = []

    all_keys = set(expected.keys()) | set(actual.keys())

    for key in all_keys:
        if key in ignore_keys:
            continue

        if key not in expected:
            differences.append(f"Unexpected key: {key}")
        elif key not in actual:
            differences.append(f"Missing key: {key}")
        elif expected[key] != actual[key]:
            differences.append(f"Value mismatch for '{key}': expected {expected[key]!r}, got {actual[key]!r}")

    return differences
