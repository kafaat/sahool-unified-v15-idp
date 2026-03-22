"""
Test Utilities Module
=====================
وحدة أدوات الاختبار

Common utilities, helpers, and fixtures for testing.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from .assertions import (
    assert_api_response,
    assert_event_published,
    assert_field_valid,
    assert_json_schema,
    assert_response_error,
    assert_response_ok,
)
from .helpers import (
    async_test,
    create_test_token,
    mock_nats_client,
    mock_redis_client,
    wait_for_condition,
    with_timeout,
)
from .mocks import (
    MockDatabase,
    MockEventPublisher,
    MockNATSClient,
    MockRedisClient,
)

__all__ = [
    # Assertions
    "assert_api_response",
    "assert_event_published",
    "assert_field_valid",
    "assert_json_schema",
    "assert_response_ok",
    "assert_response_error",
    # Helpers
    "async_test",
    "create_test_token",
    "mock_nats_client",
    "mock_redis_client",
    "wait_for_condition",
    "with_timeout",
    # Mocks
    "MockDatabase",
    "MockEventPublisher",
    "MockRedisClient",
    "MockNATSClient",
]
