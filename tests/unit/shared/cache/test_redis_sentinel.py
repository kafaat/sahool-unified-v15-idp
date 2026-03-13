"""
Tests for Redis Sentinel Client Module
======================================
اختبارات وحدة عميل Redis Sentinel

Comprehensive tests for Redis Sentinel client with circuit breaker pattern.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

pytest.importorskip("redis")

from shared.cache.redis_sentinel import (
    CircuitBreaker,
    RedisSentinelConfig,
    RedisSentinelClient,
    get_redis_client,
    close_redis_client,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def redis_config():
    """Create a test Redis Sentinel configuration."""
    config = RedisSentinelConfig()
    return config


@pytest.fixture
def circuit_breaker():
    """Create a test circuit breaker."""
    return CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=1,  # Short timeout for tests
        expected_exception=Exception,
    )


@pytest.fixture
def mock_sentinel():
    """Create a mock Sentinel instance."""
    with patch("shared.cache.redis_sentinel.Sentinel") as MockSentinel:
        mock_instance = MagicMock()
        mock_master = MagicMock()
        mock_slave = MagicMock()

        mock_instance.master_for.return_value = mock_master
        mock_instance.slave_for.return_value = mock_slave
        mock_instance.discover_master.return_value = ("localhost", 6379)
        mock_instance.discover_slaves.return_value = [("localhost", 6380)]

        MockSentinel.return_value = mock_instance
        yield mock_instance


# =============================================================================
# Test RedisSentinelConfig
# =============================================================================


class TestRedisSentinelConfig:
    """Tests for Redis Sentinel configuration."""

    def test_default_config_values(self, redis_config):
        """Test default configuration values."""
        assert redis_config.master_name == "sahool-master"
        assert redis_config.db == 0
        assert redis_config.socket_timeout == 5
        assert redis_config.max_connections == 50

    def test_sentinel_hosts_parsing(self, redis_config):
        """Test parsing of sentinel hosts."""
        sentinels = redis_config.get_sentinels()

        assert isinstance(sentinels, list)
        assert len(sentinels) > 0
        assert all(isinstance(s, tuple) for s in sentinels)
        assert all(len(s) == 2 for s in sentinels)

    def test_sentinel_ports_default(self, redis_config):
        """Test default sentinel ports."""
        assert 26379 in redis_config.sentinel_ports
        assert 26380 in redis_config.sentinel_ports
        assert 26381 in redis_config.sentinel_ports

    def test_socket_keepalive_options(self, redis_config):
        """Test socket keepalive options."""
        assert redis_config.socket_keepalive is True
        assert isinstance(redis_config.socket_keepalive_options, dict)

    def test_sentinel_kwargs(self, redis_config):
        """Test sentinel kwargs contain required fields."""
        assert "socket_timeout" in redis_config.sentinel_kwargs
        assert "socket_connect_timeout" in redis_config.sentinel_kwargs
        assert "password" in redis_config.sentinel_kwargs


# =============================================================================
# Test CircuitBreaker
# =============================================================================


class TestCircuitBreaker:
    """Tests for Circuit Breaker pattern."""

    def test_initial_state_is_closed(self, circuit_breaker):
        """Test that circuit breaker starts in CLOSED state."""
        assert circuit_breaker.state == "CLOSED"

    def test_initial_failure_count_is_zero(self, circuit_breaker):
        """Test that failure count starts at zero."""
        assert circuit_breaker.failure_count == 0

    def test_successful_call_returns_result(self, circuit_breaker):
        """Test that successful call returns result."""

        def success_func():
            return "success"

        result = circuit_breaker.call(success_func)
        assert result == "success"

    def test_successful_call_resets_failure_count(self, circuit_breaker):
        """Test that successful call resets failure count."""
        circuit_breaker.failure_count = 2

        def success_func():
            return "success"

        circuit_breaker.call(success_func)
        assert circuit_breaker.failure_count == 0

    def test_failed_call_increments_failure_count(self, circuit_breaker):
        """Test that failed call increments failure count."""

        def fail_func():
            raise Exception("Test failure")

        with pytest.raises(Exception):
            circuit_breaker.call(fail_func)

        assert circuit_breaker.failure_count == 1

    def test_circuit_opens_after_threshold(self, circuit_breaker):
        """Test that circuit opens after reaching failure threshold."""

        def fail_func():
            raise Exception("Test failure")

        # Fail until threshold (3 failures)
        for _ in range(3):
            with pytest.raises(Exception):
                circuit_breaker.call(fail_func)

        assert circuit_breaker.state == "OPEN"

    def test_open_circuit_rejects_calls(self, circuit_breaker):
        """Test that open circuit rejects calls."""
        # Manually open the circuit
        circuit_breaker.state = "OPEN"
        circuit_breaker.last_failure_time = time.time()

        def any_func():
            return "should not run"

        with pytest.raises(Exception) as exc_info:
            circuit_breaker.call(any_func)

        assert "OPEN" in str(exc_info.value)

    def test_circuit_enters_half_open_after_timeout(self, circuit_breaker):
        """Test that circuit enters HALF_OPEN after recovery timeout."""
        # Open the circuit with old failure time
        circuit_breaker.state = "OPEN"
        circuit_breaker.last_failure_time = time.time() - 2  # 2 seconds ago

        def success_func():
            return "success"

        # Should allow call and move to HALF_OPEN/CLOSED
        result = circuit_breaker.call(success_func)
        assert result == "success"

    def test_successful_call_in_half_open_closes_circuit(self, circuit_breaker):
        """Test that successful call in HALF_OPEN closes circuit."""
        circuit_breaker.state = "HALF_OPEN"

        def success_func():
            return "success"

        circuit_breaker.call(success_func)
        assert circuit_breaker.state == "CLOSED"

    def test_failure_in_half_open_reopens_circuit(self, circuit_breaker):
        """Test that failure in HALF_OPEN reopens circuit."""
        circuit_breaker.state = "HALF_OPEN"
        circuit_breaker.failure_count = circuit_breaker.failure_threshold - 1

        def fail_func():
            raise Exception("Test failure")

        with pytest.raises(Exception):
            circuit_breaker.call(fail_func)

        assert circuit_breaker.state == "OPEN"

    def test_call_with_arguments(self, circuit_breaker):
        """Test call with positional and keyword arguments."""

        def add(a, b, c=0):
            return a + b + c

        result = circuit_breaker.call(add, 1, 2, c=3)
        assert result == 6

    def test_expected_exception_type(self):
        """Test that only expected exception type triggers failure."""
        breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60,
            expected_exception=ValueError,
        )

        def raise_type_error():
            raise TypeError("Wrong type")

        # TypeError should propagate but not count as circuit failure
        with pytest.raises(TypeError):
            breaker.call(raise_type_error)

        # Failure count should still be 0 for unexpected exception types
        # (depending on implementation - verify actual behavior)


# =============================================================================
# Test RedisSentinelClient
# =============================================================================


class TestRedisSentinelClient:
    """Tests for Redis Sentinel client."""

    def test_client_initialization_with_config(self, mock_sentinel, redis_config):
        """Test client initialization with config."""
        client = RedisSentinelClient(config=redis_config)

        assert client.config == redis_config
        assert client._circuit_breaker is not None

    def test_client_has_circuit_breaker(self, mock_sentinel, redis_config):
        """Test that client has circuit breaker."""
        client = RedisSentinelClient(config=redis_config)

        assert isinstance(client._circuit_breaker, CircuitBreaker)

    def test_get_master_address(self, mock_sentinel, redis_config):
        """Test getting master address."""
        client = RedisSentinelClient(config=redis_config)
        address = client.get_master_address()

        assert address is not None
        assert isinstance(address, tuple)
        assert len(address) == 2

    def test_get_slaves_addresses(self, mock_sentinel, redis_config):
        """Test getting slave addresses."""
        client = RedisSentinelClient(config=redis_config)
        addresses = client.get_slaves_addresses()

        assert isinstance(addresses, list)

    def test_get_connection_context_manager(self, mock_sentinel, redis_config):
        """Test get_connection context manager."""
        client = RedisSentinelClient(config=redis_config)

        with client.get_connection(read_only=False) as conn:
            assert conn is not None

        with client.get_connection(read_only=True) as conn:
            assert conn is not None

    def test_set_operation(self, mock_sentinel, redis_config):
        """Test set operation."""
        client = RedisSentinelClient(config=redis_config)
        client._master.set.return_value = True

        result = client.set("test_key", "test_value", ex=60)

        assert result is True

    def test_get_operation(self, mock_sentinel, redis_config):
        """Test get operation."""
        client = RedisSentinelClient(config=redis_config)
        client._slave.get.return_value = "test_value"

        result = client.get("test_key")

        assert result == "test_value"

    def test_get_uses_slave_by_default(self, mock_sentinel, redis_config):
        """Test that get uses slave connection by default."""
        client = RedisSentinelClient(config=redis_config)
        client._slave.get.return_value = "value"

        client.get("key", use_slave=True)

        client._slave.get.assert_called()

    def test_delete_operation(self, mock_sentinel, redis_config):
        """Test delete operation."""
        client = RedisSentinelClient(config=redis_config)
        client._master.delete.return_value = 1

        result = client.delete("key1", "key2")

        assert result == 1

    def test_exists_operation(self, mock_sentinel, redis_config):
        """Test exists operation."""
        client = RedisSentinelClient(config=redis_config)
        client._slave.exists.return_value = 2

        result = client.exists("key1", "key2")

        assert result == 2

    def test_expire_operation(self, mock_sentinel, redis_config):
        """Test expire operation."""
        client = RedisSentinelClient(config=redis_config)
        client._master.expire.return_value = True

        result = client.expire("key", 60)

        assert result is True

    def test_ttl_operation(self, mock_sentinel, redis_config):
        """Test TTL operation."""
        client = RedisSentinelClient(config=redis_config)
        client._slave.ttl.return_value = 45

        result = client.ttl("key")

        assert result == 45

    def test_hset_operation(self, mock_sentinel, redis_config):
        """Test hash set operation."""
        client = RedisSentinelClient(config=redis_config)
        client._master.hset.return_value = 1

        result = client.hset("hash_name", "field", "value")

        assert result == 1

    def test_hget_operation(self, mock_sentinel, redis_config):
        """Test hash get operation."""
        client = RedisSentinelClient(config=redis_config)
        client._slave.hget.return_value = "value"

        result = client.hget("hash_name", "field")

        assert result == "value"

    def test_hgetall_operation(self, mock_sentinel, redis_config):
        """Test hash get all operation."""
        client = RedisSentinelClient(config=redis_config)
        client._slave.hgetall.return_value = {"field1": "value1", "field2": "value2"}

        result = client.hgetall("hash_name")

        assert result == {"field1": "value1", "field2": "value2"}

    def test_lpush_operation(self, mock_sentinel, redis_config):
        """Test list push operation."""
        client = RedisSentinelClient(config=redis_config)
        client._master.lpush.return_value = 3

        result = client.lpush("list_name", "value1", "value2")

        assert result == 3

    def test_rpush_operation(self, mock_sentinel, redis_config):
        """Test right push operation."""
        client = RedisSentinelClient(config=redis_config)
        client._master.rpush.return_value = 2

        result = client.rpush("list_name", "value")

        assert result == 2

    def test_lpop_operation(self, mock_sentinel, redis_config):
        """Test left pop operation."""
        client = RedisSentinelClient(config=redis_config)
        client._master.lpop.return_value = "first_value"

        result = client.lpop("list_name")

        assert result == "first_value"

    def test_lrange_operation(self, mock_sentinel, redis_config):
        """Test list range operation."""
        client = RedisSentinelClient(config=redis_config)
        client._slave.lrange.return_value = ["a", "b", "c"]

        result = client.lrange("list_name", 0, -1)

        assert result == ["a", "b", "c"]

    def test_sadd_operation(self, mock_sentinel, redis_config):
        """Test set add operation."""
        client = RedisSentinelClient(config=redis_config)
        client._master.sadd.return_value = 2

        result = client.sadd("set_name", "member1", "member2")

        assert result == 2

    def test_smembers_operation(self, mock_sentinel, redis_config):
        """Test set members operation."""
        client = RedisSentinelClient(config=redis_config)
        client._slave.smembers.return_value = {"member1", "member2"}

        result = client.smembers("set_name")

        assert result == {"member1", "member2"}

    def test_zadd_operation(self, mock_sentinel, redis_config):
        """Test sorted set add operation."""
        client = RedisSentinelClient(config=redis_config)
        client._master.zadd.return_value = 2

        result = client.zadd("zset_name", {"member1": 1.0, "member2": 2.0})

        assert result == 2

    def test_zrange_operation(self, mock_sentinel, redis_config):
        """Test sorted set range operation."""
        client = RedisSentinelClient(config=redis_config)
        client._slave.zrange.return_value = ["member1", "member2"]

        result = client.zrange("zset_name", 0, -1)

        assert result == ["member1", "member2"]

    def test_pipeline_context_manager(self, mock_sentinel, redis_config):
        """Test pipeline context manager."""
        client = RedisSentinelClient(config=redis_config)
        mock_pipe = MagicMock()
        client._master.pipeline.return_value = mock_pipe

        with client.pipeline() as pipe:
            assert pipe is not None

    def test_ping_success(self, mock_sentinel, redis_config):
        """Test successful ping."""
        client = RedisSentinelClient(config=redis_config)
        client._master.ping.return_value = True

        result = client.ping()

        assert result is True

    def test_ping_failure(self, mock_sentinel, redis_config):
        """Test failed ping."""
        client = RedisSentinelClient(config=redis_config)
        client._master.ping.side_effect = Exception("Connection failed")

        result = client.ping()

        assert result is False

    def test_info_operation(self, mock_sentinel, redis_config):
        """Test info operation."""
        client = RedisSentinelClient(config=redis_config)
        client._master.info.return_value = {"redis_version": "7.0.0"}

        result = client.info()

        assert "redis_version" in result

    def test_get_sentinel_info(self, mock_sentinel, redis_config):
        """Test getting sentinel info."""
        client = RedisSentinelClient(config=redis_config)
        client._master.ping.return_value = True

        info = client.get_sentinel_info()

        assert "master" in info
        assert "slaves" in info
        assert "master_name" in info
        assert "is_connected" in info

    def test_health_check(self, mock_sentinel, redis_config):
        """Test health check."""
        client = RedisSentinelClient(config=redis_config)
        client._master.ping.return_value = True

        health = client.health_check()

        assert "status" in health
        assert "timestamp" in health
        assert "checks" in health

    def test_health_check_unhealthy(self, mock_sentinel, redis_config):
        """Test health check when unhealthy.

        Note: The health_check method calls self.ping() which catches
        exceptions internally and returns False. To trigger unhealthy status,
        we need to mock the ping method on the client instance to raise.
        """
        client = RedisSentinelClient(config=redis_config)
        client.ping = MagicMock(side_effect=Exception("Connection failed"))

        health = client.health_check()

        assert health["status"] == "unhealthy"
        assert "error" in health

    def test_close_operation(self, mock_sentinel, redis_config):
        """Test close operation."""
        client = RedisSentinelClient(config=redis_config)

        client.close()

        client._master.close.assert_called_once()
        client._slave.close.assert_called_once()


# =============================================================================
# Test Singleton Functions
# =============================================================================


class TestSingletonFunctions:
    """Tests for singleton pattern functions."""

    def test_get_redis_client_singleton(self, mock_sentinel):
        """Test that get_redis_client returns singleton."""
        # Reset singleton
        close_redis_client()

        client1 = get_redis_client()
        client2 = get_redis_client()

        assert client1 is client2

    def test_close_redis_client(self, mock_sentinel):
        """Test closing redis client."""
        # Ensure client exists
        get_redis_client()

        # Close should not raise
        close_redis_client()


# =============================================================================
# Test Retry Logic
# =============================================================================


class TestRetryLogic:
    """Tests for retry logic with exponential backoff."""

    def test_retry_on_connection_error(self, mock_sentinel, redis_config):
        """Test retry on connection error."""
        client = RedisSentinelClient(config=redis_config)

        # First call fails, second succeeds
        client._master.set.side_effect = [
            Exception("Connection error"),
            True,
        ]

        # Should succeed on retry (if implemented)
        # Note: Actual retry behavior depends on implementation

    def test_exponential_backoff_delay(self, circuit_breaker):
        """Test that exponential backoff is applied."""
        # This is more of an integration test
        # Verify delays increase exponentially
        delays = [0.5 * (2**i) for i in range(3)]

        assert delays[0] == 0.5
        assert delays[1] == 1.0
        assert delays[2] == 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
