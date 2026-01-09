"""
اختبارات عميل Redis Sentinel
Redis Sentinel Client Tests

Tests for the SAHOOL platform Redis Sentinel client with high availability.
"""

import time
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

# Import the modules under test
from shared.cache.redis_sentinel import (
    RedisSentinelConfig,
    CircuitBreaker,
    RedisSentinelClient,
    get_redis_client,
    close_redis_client,
)


# ─────────────────────────────────────────────────────────────────────────────
# RedisSentinelConfig Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestRedisSentinelConfig:
    """Tests for RedisSentinelConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = RedisSentinelConfig()

        assert config.sentinel_port == 26379
        assert config.master_name == "sahool-master"
        assert config.db == 0
        assert config.socket_timeout == 5
        assert config.socket_connect_timeout == 5
        assert config.socket_keepalive is True
        assert config.max_connections == 50
        assert config.retry_on_timeout is True
        assert config.health_check_interval == 30

    def test_config_from_env(self, monkeypatch):
        """Test configuration from environment variables."""
        monkeypatch.setenv("REDIS_SENTINEL_HOSTS", "host1,host2,host3")
        monkeypatch.setenv("REDIS_SENTINEL_PORT", "26380")
        monkeypatch.setenv("REDIS_PASSWORD", "secret123")
        monkeypatch.setenv("REDIS_MASTER_NAME", "my-master")
        monkeypatch.setenv("REDIS_DB", "2")
        monkeypatch.setenv("REDIS_SOCKET_TIMEOUT", "10")
        monkeypatch.setenv("REDIS_MAX_CONNECTIONS", "100")

        config = RedisSentinelConfig()

        assert config.sentinel_hosts == ["host1", "host2", "host3"]
        assert config.sentinel_port == 26380
        assert config.password == "secret123"
        assert config.master_name == "my-master"
        assert config.db == 2
        assert config.socket_timeout == 10
        assert config.max_connections == 100

    def test_get_sentinels(self):
        """Test sentinel address list generation."""
        config = RedisSentinelConfig()
        config.sentinel_hosts = ["host1", "host2", "host3"]
        config.sentinel_ports = [26379, 26380, 26381]

        sentinels = config.get_sentinels()

        assert len(sentinels) == 3
        assert sentinels[0] == ("host1", 26379)
        assert sentinels[1] == ("host2", 26380)
        assert sentinels[2] == ("host3", 26381)

    def test_get_sentinels_strips_whitespace(self):
        """Test that sentinel hosts are stripped of whitespace."""
        config = RedisSentinelConfig()
        config.sentinel_hosts = ["  host1 ", " host2", "host3  "]

        sentinels = config.get_sentinels()

        assert sentinels[0][0] == "host1"
        assert sentinels[1][0] == "host2"
        assert sentinels[2][0] == "host3"


# ─────────────────────────────────────────────────────────────────────────────
# CircuitBreaker Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCircuitBreaker:
    """Tests for CircuitBreaker pattern implementation."""

    def test_initial_state_closed(self):
        """Test that circuit breaker starts in CLOSED state."""
        cb = CircuitBreaker()
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0

    def test_success_resets_failures(self):
        """Test that success resets failure count."""
        cb = CircuitBreaker(failure_threshold=3)

        # Simulate some failures
        cb.failure_count = 2

        # Success should reset
        def success_func():
            return "success"

        result = cb.call(success_func)
        assert result == "success"
        assert cb.failure_count == 0
        assert cb.state == "CLOSED"

    def test_failure_increments_count(self):
        """Test that failures increment the count."""
        cb = CircuitBreaker(failure_threshold=3, expected_exception=ValueError)

        def failing_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            cb.call(failing_func)

        assert cb.failure_count == 1
        assert cb.state == "CLOSED"

    def test_circuit_opens_after_threshold(self):
        """Test that circuit opens after failure threshold."""
        cb = CircuitBreaker(failure_threshold=3, expected_exception=ValueError)

        def failing_func():
            raise ValueError("Test error")

        # Fail 3 times
        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(failing_func)

        assert cb.state == "OPEN"
        assert cb.failure_count == 3

    def test_open_circuit_rejects_calls(self):
        """Test that open circuit rejects new calls."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60)
        cb.state = "OPEN"
        cb.last_failure_time = time.time()

        def test_func():
            return "success"

        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            cb.call(test_func)

    def test_half_open_after_recovery_timeout(self):
        """Test transition to HALF_OPEN after recovery timeout."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1)
        cb.state = "OPEN"
        cb.last_failure_time = time.time() - 2  # 2 seconds ago

        def test_func():
            return "success"

        result = cb.call(test_func)

        assert result == "success"
        assert cb.state == "CLOSED"  # Success in HALF_OPEN returns to CLOSED

    def test_half_open_failure_reopens(self):
        """Test that failure in HALF_OPEN reopens circuit."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1, expected_exception=ValueError)
        cb.state = "OPEN"
        cb.last_failure_time = time.time() - 2

        def failing_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            cb.call(failing_func)

        assert cb.state == "OPEN"


# ─────────────────────────────────────────────────────────────────────────────
# RedisSentinelClient Tests (Mocked)
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestRedisSentinelClient:
    """Tests for RedisSentinelClient with mocked Redis."""

    @pytest.fixture
    def mock_sentinel(self):
        """Create mock Sentinel."""
        with patch("shared.cache.redis_sentinel.Sentinel") as mock:
            mock_master = MagicMock()
            mock_slave = MagicMock()

            mock_instance = MagicMock()
            mock_instance.master_for.return_value = mock_master
            mock_instance.slave_for.return_value = mock_slave
            mock_instance.discover_master.return_value = ("master-host", 6379)
            mock_instance.discover_slaves.return_value = [
                ("slave1-host", 6379),
                ("slave2-host", 6379),
            ]

            mock.return_value = mock_instance

            yield {
                "sentinel_class": mock,
                "sentinel": mock_instance,
                "master": mock_master,
                "slave": mock_slave,
            }

    def test_client_initialization(self, mock_sentinel):
        """Test client initialization."""
        client = RedisSentinelClient()

        assert client._sentinel is not None
        assert client._master is not None
        assert client._slave is not None
        mock_sentinel["sentinel_class"].assert_called_once()

    def test_get_master_address(self, mock_sentinel):
        """Test getting master address."""
        client = RedisSentinelClient()

        address = client.get_master_address()

        assert address == ("master-host", 6379)
        mock_sentinel["sentinel"].discover_master.assert_called_once()

    def test_get_slaves_addresses(self, mock_sentinel):
        """Test getting slave addresses."""
        client = RedisSentinelClient()

        addresses = client.get_slaves_addresses()

        assert len(addresses) == 2
        assert ("slave1-host", 6379) in addresses
        mock_sentinel["sentinel"].discover_slaves.assert_called_once()

    def test_set_operation(self, mock_sentinel):
        """Test SET operation."""
        mock_sentinel["master"].set.return_value = True
        client = RedisSentinelClient()

        result = client.set("test_key", "test_value", ex=60)

        assert result is True
        mock_sentinel["master"].set.assert_called_once_with(
            "test_key", "test_value", ex=60, px=None, nx=False, xx=False
        )

    def test_get_operation_uses_slave(self, mock_sentinel):
        """Test GET operation uses slave by default."""
        mock_sentinel["slave"].get.return_value = "test_value"
        client = RedisSentinelClient()

        result = client.get("test_key")

        assert result == "test_value"
        mock_sentinel["slave"].get.assert_called_once_with("test_key")

    def test_get_operation_uses_master(self, mock_sentinel):
        """Test GET operation can use master."""
        mock_sentinel["master"].get.return_value = "test_value"
        client = RedisSentinelClient()

        result = client.get("test_key", use_slave=False)

        assert result == "test_value"
        mock_sentinel["master"].get.assert_called_once_with("test_key")

    def test_delete_operation(self, mock_sentinel):
        """Test DELETE operation."""
        mock_sentinel["master"].delete.return_value = 2
        client = RedisSentinelClient()

        result = client.delete("key1", "key2")

        assert result == 2
        mock_sentinel["master"].delete.assert_called_once_with("key1", "key2")

    def test_exists_operation(self, mock_sentinel):
        """Test EXISTS operation."""
        mock_sentinel["slave"].exists.return_value = 1
        client = RedisSentinelClient()

        result = client.exists("key1")

        assert result == 1

    def test_expire_operation(self, mock_sentinel):
        """Test EXPIRE operation."""
        mock_sentinel["master"].expire.return_value = True
        client = RedisSentinelClient()

        result = client.expire("key1", 300)

        assert result is True

    def test_ttl_operation(self, mock_sentinel):
        """Test TTL operation."""
        mock_sentinel["slave"].ttl.return_value = 100
        client = RedisSentinelClient()

        result = client.ttl("key1")

        assert result == 100

    def test_hash_operations(self, mock_sentinel):
        """Test hash operations."""
        mock_sentinel["master"].hset.return_value = 1
        mock_sentinel["slave"].hget.return_value = "value"
        mock_sentinel["slave"].hgetall.return_value = {"field": "value"}
        mock_sentinel["master"].hdel.return_value = 1

        client = RedisSentinelClient()

        assert client.hset("hash", "field", "value") == 1
        assert client.hget("hash", "field") == "value"
        assert client.hgetall("hash") == {"field": "value"}
        assert client.hdel("hash", "field") == 1

    def test_list_operations(self, mock_sentinel):
        """Test list operations."""
        mock_sentinel["master"].lpush.return_value = 1
        mock_sentinel["master"].rpush.return_value = 2
        mock_sentinel["master"].lpop.return_value = "item1"
        mock_sentinel["master"].rpop.return_value = "item2"
        mock_sentinel["slave"].lrange.return_value = ["item1", "item2"]

        client = RedisSentinelClient()

        assert client.lpush("list", "item1") == 1
        assert client.rpush("list", "item2") == 2
        assert client.lpop("list") == "item1"
        assert client.rpop("list") == "item2"
        assert client.lrange("list", 0, -1) == ["item1", "item2"]

    def test_set_operations(self, mock_sentinel):
        """Test set operations."""
        mock_sentinel["master"].sadd.return_value = 2
        mock_sentinel["slave"].smembers.return_value = {"member1", "member2"}
        mock_sentinel["master"].srem.return_value = 1

        client = RedisSentinelClient()

        assert client.sadd("set", "member1", "member2") == 2
        assert client.smembers("set") == {"member1", "member2"}
        assert client.srem("set", "member1") == 1

    def test_sorted_set_operations(self, mock_sentinel):
        """Test sorted set operations."""
        mock_sentinel["master"].zadd.return_value = 2
        mock_sentinel["slave"].zrange.return_value = ["member1", "member2"]
        mock_sentinel["master"].zrem.return_value = 1

        client = RedisSentinelClient()

        assert client.zadd("zset", {"member1": 1.0, "member2": 2.0}) == 2
        assert client.zrange("zset", 0, -1) == ["member1", "member2"]
        assert client.zrem("zset", "member1") == 1

    def test_ping_success(self, mock_sentinel):
        """Test successful ping."""
        mock_sentinel["master"].ping.return_value = True
        client = RedisSentinelClient()

        assert client.ping() is True

    def test_ping_failure(self, mock_sentinel):
        """Test failed ping."""
        mock_sentinel["master"].ping.side_effect = Exception("Connection failed")
        client = RedisSentinelClient()

        assert client.ping() is False

    def test_info(self, mock_sentinel):
        """Test INFO command."""
        mock_sentinel["master"].info.return_value = {"redis_version": "7.0.0"}
        client = RedisSentinelClient()

        info = client.info()

        assert info["redis_version"] == "7.0.0"

    def test_get_sentinel_info(self, mock_sentinel):
        """Test getting sentinel info."""
        mock_sentinel["master"].ping.return_value = True
        client = RedisSentinelClient()

        info = client.get_sentinel_info()

        assert info["master"] == ("master-host", 6379)
        assert len(info["slaves"]) == 2
        assert info["is_connected"] is True

    def test_health_check(self, mock_sentinel):
        """Test health check."""
        mock_sentinel["master"].ping.return_value = True
        client = RedisSentinelClient()

        health = client.health_check()

        assert health["status"] == "healthy"
        assert health["checks"]["master_ping"] is True
        assert "timestamp" in health

    def test_health_check_unhealthy(self, mock_sentinel):
        """Test health check when unhealthy."""
        mock_sentinel["master"].ping.side_effect = Exception("Connection failed")
        client = RedisSentinelClient()

        health = client.health_check()

        assert health["status"] == "unhealthy"
        assert health["checks"]["master_ping"] is False

    def test_close(self, mock_sentinel):
        """Test closing connections."""
        client = RedisSentinelClient()

        client.close()

        mock_sentinel["master"].close.assert_called_once()
        mock_sentinel["slave"].close.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
# Retry Logic Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestRetryLogic:
    """Tests for retry logic with exponential backoff."""

    @pytest.fixture
    def mock_sentinel(self):
        """Create mock Sentinel."""
        with patch("shared.cache.redis_sentinel.Sentinel") as mock:
            mock_master = MagicMock()
            mock_slave = MagicMock()

            mock_instance = MagicMock()
            mock_instance.master_for.return_value = mock_master
            mock_instance.slave_for.return_value = mock_slave

            mock.return_value = mock_instance

            yield {"master": mock_master, "slave": mock_slave}

    def test_retry_on_connection_error(self, mock_sentinel):
        """Test retry on ConnectionError."""
        from redis.exceptions import ConnectionError

        # First call fails, second succeeds
        mock_sentinel["master"].set.side_effect = [
            ConnectionError("Connection lost"),
            True,
        ]

        client = RedisSentinelClient()

        with patch.object(client, "_circuit_breaker") as mock_cb:
            # Mock circuit breaker to pass through
            mock_cb.call.side_effect = lambda f, *args, **kwargs: f(*args, **kwargs)

            result = client.set("key", "value")

        # Should succeed after retry
        assert result is True
        assert mock_sentinel["master"].set.call_count >= 2

    def test_retry_on_timeout(self, mock_sentinel):
        """Test retry on TimeoutError."""
        from redis.exceptions import TimeoutError

        mock_sentinel["slave"].get.side_effect = [TimeoutError("Timeout"), "value"]

        client = RedisSentinelClient()

        with patch.object(client, "_circuit_breaker") as mock_cb:
            mock_cb.call.side_effect = lambda f, *args, **kwargs: f(*args, **kwargs)

            result = client.get("key")

        assert result == "value"


# ─────────────────────────────────────────────────────────────────────────────
# Singleton Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSingleton:
    """Tests for singleton pattern."""

    def test_get_redis_client_singleton(self):
        """Test that get_redis_client returns singleton."""
        with patch("shared.cache.redis_sentinel.RedisSentinelClient") as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            # Reset singleton
            with patch("shared.cache.redis_sentinel._redis_client", None):
                client1 = get_redis_client()

                # Should create new instance
                mock_class.assert_called_once()

    def test_close_redis_client(self):
        """Test closing the singleton client."""
        mock_client = MagicMock()

        with patch("shared.cache.redis_sentinel._redis_client", mock_client):
            close_redis_client()

            mock_client.close.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
# Context Manager Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestContextManager:
    """Tests for context manager usage."""

    @pytest.fixture
    def mock_sentinel(self):
        """Create mock Sentinel."""
        with patch("shared.cache.redis_sentinel.Sentinel") as mock:
            mock_master = MagicMock()
            mock_slave = MagicMock()

            mock_instance = MagicMock()
            mock_instance.master_for.return_value = mock_master
            mock_instance.slave_for.return_value = mock_slave

            mock.return_value = mock_instance

            yield {"master": mock_master, "slave": mock_slave}

    def test_get_connection_master(self, mock_sentinel):
        """Test getting master connection via context manager."""
        client = RedisSentinelClient()

        with client.get_connection(read_only=False) as conn:
            assert conn == mock_sentinel["master"]

    def test_get_connection_slave(self, mock_sentinel):
        """Test getting slave connection via context manager."""
        client = RedisSentinelClient()

        with client.get_connection(read_only=True) as conn:
            assert conn == mock_sentinel["slave"]

    def test_pipeline_context_manager(self, mock_sentinel):
        """Test pipeline context manager."""
        mock_pipe = MagicMock()
        mock_sentinel["master"].pipeline.return_value = mock_pipe

        client = RedisSentinelClient()

        with client.pipeline() as pipe:
            assert pipe == mock_pipe

        mock_sentinel["master"].pipeline.assert_called_once_with(transaction=True)
