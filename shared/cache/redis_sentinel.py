"""
Redis Sentinel Client for High Availability
============================================
عميل Redis Sentinel للتوافر العالي

Provides Redis Sentinel connectivity with:
- Automatic failover handling (تجاوز الفشل التلقائي)
- Connection pooling (تجميع الاتصالات)
- Circuit breaker pattern (نمط قاطع الدائرة)
- Health monitoring (مراقبة الصحة)
- Retry logic with exponential backoff (إعادة المحاولة مع تراجع أسي)

Author: Sahool Platform Team
Updated: January 2026
License: MIT

Example:
    >>> client = RedisSentinelClient()
    >>> client.set('key', 'value', ex=60)
    >>> value = client.get('key')
    >>> print(value)
    'value'

    # Using context manager
    >>> with client.pipeline() as pipe:
    ...     pipe.set('key1', 'value1')
    ...     pipe.set('key2', 'value2')
    ...     pipe.execute()
"""

from __future__ import annotations

import logging
import os
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, TypeVar

from redis.exceptions import ConnectionError, RedisError, TimeoutError
from redis.sentinel import Sentinel

if TYPE_CHECKING:
    from collections.abc import Callable

# Type variable for generic operations
T = TypeVar("T")

# Configure structured logging
logger = logging.getLogger(__name__)


class CircuitBreakerState(str, Enum):
    """States for the circuit breaker pattern."""

    CLOSED = "CLOSED"  # Normal operation - requests pass through
    OPEN = "OPEN"  # Service down - requests fail fast
    HALF_OPEN = "HALF_OPEN"  # Testing recovery


@dataclass
class RedisSentinelConfig:
    """
    Redis Sentinel Configuration.
    تكوين Redis Sentinel

    Configuration for connecting to Redis via Sentinel for high availability.
    All settings can be overridden via environment variables.

    Environment Variables:
        REDIS_SENTINEL_HOSTS: Comma-separated list of Sentinel hosts (قائمة مضيفي Sentinel)
        REDIS_SENTINEL_PORT: Sentinel port (default: 26379) (منفذ Sentinel)
        REDIS_PASSWORD: Redis authentication password (كلمة مرور Redis)
        REDIS_MASTER_NAME: Master set name (default: sahool-master) (اسم المجموعة الرئيسية)
        REDIS_DB: Database number (default: 0) (رقم قاعدة البيانات)
        REDIS_SOCKET_TIMEOUT: Socket timeout in seconds (default: 5) (مهلة الاتصال)
        REDIS_SOCKET_CONNECT_TIMEOUT: Connection timeout (default: 5) (مهلة الاتصال الأولي)
        REDIS_MAX_CONNECTIONS: Max pool connections (default: 50) (الحد الأقصى للاتصالات)

    Example:
        >>> config = RedisSentinelConfig()
        >>> config = RedisSentinelConfig(master_name="custom-master", db=1)
    """

    # Sentinel hosts (loaded from env or default)
    sentinel_hosts: list[str] = field(
        default_factory=lambda: os.getenv(
            "REDIS_SENTINEL_HOSTS", "localhost,localhost,localhost"
        ).split(",")
    )
    sentinel_port: int = field(
        default_factory=lambda: int(os.getenv("REDIS_SENTINEL_PORT", "26379"))
    )
    sentinel_ports: list[int] = field(default_factory=lambda: [26379, 26380, 26381])

    # Redis configuration
    password: str = field(default_factory=lambda: os.getenv("REDIS_PASSWORD", "redis_password"))
    master_name: str = field(
        default_factory=lambda: os.getenv("REDIS_MASTER_NAME", "sahool-master")
    )
    db: int = field(default_factory=lambda: int(os.getenv("REDIS_DB", "0")))

    # Connection settings
    socket_timeout: int = field(default_factory=lambda: int(os.getenv("REDIS_SOCKET_TIMEOUT", "5")))
    socket_connect_timeout: int = field(
        default_factory=lambda: int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5"))
    )
    socket_keepalive: bool = True
    socket_keepalive_options: dict[int, int] = field(
        default_factory=lambda: {
            1: 1,  # TCP_KEEPIDLE
            2: 1,  # TCP_KEEPINTVL
            3: 3,  # TCP_KEEPCNT
        }
    )

    # Connection pool settings
    max_connections: int = field(
        default_factory=lambda: int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
    )
    retry_on_timeout: bool = True
    health_check_interval: int = 30

    @property
    def sentinel_kwargs(self) -> dict[str, Any]:
        """
        Get sentinel connection kwargs.

        Returns:
            Dictionary of sentinel connection parameters
        """
        return {
            "socket_timeout": self.socket_timeout,
            "socket_connect_timeout": self.socket_connect_timeout,
            "password": self.password,
        }

    def get_sentinels(self) -> list[tuple[str, int]]:
        """
        Get list of Sentinel nodes as (host, port) tuples.
        الحصول على قائمة عقد Sentinel

        Returns:
            List of (host, port) tuples for Sentinel nodes
        """
        sentinels: list[tuple[str, int]] = []
        for i, host in enumerate(self.sentinel_hosts):
            port = self.sentinel_ports[i] if i < len(self.sentinel_ports) else self.sentinel_port
            sentinels.append((host.strip(), port))
        return sentinels

    def to_dict(self) -> dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        return {
            "sentinel_hosts": self.sentinel_hosts,
            "sentinel_port": self.sentinel_port,
            "master_name": self.master_name,
            "db": self.db,
            "socket_timeout": self.socket_timeout,
            "max_connections": self.max_connections,
        }


class CircuitBreakerOpenError(Exception):
    """
    Exception raised when circuit breaker is open.
    استثناء يُطرح عندما يكون قاطع الدائرة مفتوحاً

    Attributes:
        retry_after: Seconds until circuit breaker may close
        message: Error description
    """

    def __init__(self, message: str = "Circuit breaker is OPEN", retry_after: float | None = None):
        self.retry_after = retry_after
        self.message = message
        super().__init__(message)


@dataclass
class CircuitBreakerStats:
    """
    Statistics for circuit breaker monitoring.
    إحصائيات مراقبة قاطع الدائرة
    """

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    state_changes: int = 0
    last_state_change: datetime | None = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_calls == 0:
            return 100.0
        return (self.successful_calls / self.total_calls) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "rejected_calls": self.rejected_calls,
            "state_changes": self.state_changes,
            "success_rate": round(self.success_rate, 2),
            "last_state_change": self.last_state_change.isoformat()
            if self.last_state_change
            else None,
        }


class CircuitBreaker:
    """
    Circuit Breaker Pattern for protecting against cascading failures.
    نمط قاطع الدائرة للحماية من الأخطاء المتتالية

    States:
        - CLOSED: Normal operation, requests pass through (عمل عادي)
        - OPEN: Service is down, requests fail immediately (الخدمة معطلة)
        - HALF_OPEN: Testing if service has recovered (اختبار استعادة الخدمة)

    Attributes:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Seconds to wait before testing recovery
        expected_exception: Exception type to catch

    Example:
        >>> breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)
        >>> result = breaker.call(some_function, arg1, arg2)
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type[Exception] = Exception,
        name: str = "default",
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.name = name

        self._failure_count: int = 0
        self._last_failure_time: float | None = None
        self._state: CircuitBreakerState = CircuitBreakerState.CLOSED
        self._stats = CircuitBreakerStats()

    @property
    def state(self) -> str:
        """Get current state as string."""
        return self._state.value

    @property
    def failure_count(self) -> int:
        """Get current failure count."""
        return self._failure_count

    @property
    def last_failure_time(self) -> float | None:
        """Get timestamp of last failure."""
        return self._last_failure_time

    @property
    def stats(self) -> CircuitBreakerStats:
        """Get circuit breaker statistics."""
        return self._stats

    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Execute function through circuit breaker protection.
        تنفيذ دالة مع حماية قاطع الدائرة

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Result of the function call

        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: If function raises an expected exception
        """
        self._stats.total_calls += 1

        # Check if we should transition from OPEN to HALF_OPEN
        if self._state == CircuitBreakerState.OPEN:
            if (
                self._last_failure_time
                and time.time() - self._last_failure_time > self.recovery_timeout
            ):
                self._transition_to(CircuitBreakerState.HALF_OPEN)
                logger.info(f"Circuit breaker '{self.name}' entering HALF_OPEN state")
            else:
                self._stats.rejected_calls += 1
                retry_after = None
                if self._last_failure_time:
                    retry_after = self.recovery_timeout - (time.time() - self._last_failure_time)
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.name}' is OPEN", retry_after=retry_after
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    def _transition_to(self, new_state: CircuitBreakerState) -> None:
        """Transition to a new state."""
        if self._state != new_state:
            old_state = self._state
            self._state = new_state
            self._stats.state_changes += 1
            self._stats.last_state_change = datetime.utcnow()
            logger.info(
                f"Circuit breaker '{self.name}' transitioned: {old_state.value} -> {new_state.value}"
            )

    def _on_success(self) -> None:
        """Handle successful operation."""
        self._failure_count = 0
        self._stats.successful_calls += 1
        if self._state == CircuitBreakerState.HALF_OPEN:
            self._transition_to(CircuitBreakerState.CLOSED)
            logger.info(f"Circuit breaker '{self.name}' closed after successful recovery")
        elif self._state != CircuitBreakerState.CLOSED:
            self._transition_to(CircuitBreakerState.CLOSED)

    def _on_failure(self) -> None:
        """Handle failed operation."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        self._stats.failed_calls += 1

        if self._state == CircuitBreakerState.HALF_OPEN:
            # Recovery failed, reopen circuit
            self._transition_to(CircuitBreakerState.OPEN)
            logger.warning(f"Circuit breaker '{self.name}' reopened after failed recovery")
        elif self._failure_count >= self.failure_threshold:
            self._transition_to(CircuitBreakerState.OPEN)
            logger.error(
                f"Circuit breaker '{self.name}' opened after {self._failure_count} failures"
            )

    def reset(self) -> None:
        """
        Manually reset the circuit breaker to CLOSED state.
        إعادة ضبط قاطع الدائرة يدوياً
        """
        self._failure_count = 0
        self._last_failure_time = None
        self._transition_to(CircuitBreakerState.CLOSED)
        logger.info(f"Circuit breaker '{self.name}' manually reset")

    def get_status(self) -> dict[str, Any]:
        """
        Get current status of the circuit breaker.
        الحصول على الحالة الحالية لقاطع الدائرة

        Returns:
            Dictionary with state, failure count, and statistics
        """
        return {
            "name": self.name,
            "state": self.state,
            "failure_count": self._failure_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
            "stats": self._stats.to_dict(),
        }


class RedisSentinelClient:
    """
    Redis Sentinel Client مع دعم التوافر العالي

    Features:
        - Automatic failover
        - Connection pooling
        - Circuit breaker
        - Retry logic
        - Health monitoring

    Example:
        >>> client = RedisSentinelClient()
        >>> client.set('key', 'value', ex=60)
        >>> value = client.get('key')
    """

    def __init__(self, config: RedisSentinelConfig | None = None):
        """
        تهيئة Redis Sentinel Client

        Args:
            config: تكوين Sentinel (اختياري)
        """
        self.config = config or RedisSentinelConfig()
        self._sentinel = None
        self._master = None
        self._slave = None
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=5, recovery_timeout=60, expected_exception=RedisError
        )
        self._initialize_sentinel()

    def _initialize_sentinel(self):
        """تهيئة اتصال Sentinel"""
        try:
            sentinels = self.config.get_sentinels()
            logger.info(f"Initializing Sentinel with nodes: {sentinels}")

            self._sentinel = Sentinel(
                sentinels,
                sentinel_kwargs=self.config.sentinel_kwargs,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                socket_keepalive=self.config.socket_keepalive,
                socket_keepalive_options=self.config.socket_keepalive_options,
                retry_on_timeout=self.config.retry_on_timeout,
                health_check_interval=self.config.health_check_interval,
            )

            # الحصول على اتصال Master
            self._master = self._sentinel.master_for(
                self.config.master_name,
                socket_timeout=self.config.socket_timeout,
                password=self.config.password,
                db=self.config.db,
                decode_responses=True,
                max_connections=self.config.max_connections,
            )

            # الحصول على اتصال Slave للقراءة
            self._slave = self._sentinel.slave_for(
                self.config.master_name,
                socket_timeout=self.config.socket_timeout,
                password=self.config.password,
                db=self.config.db,
                decode_responses=True,
                max_connections=self.config.max_connections,
            )

            logger.info(f"Successfully connected to Redis master: {self.config.master_name}")

        except Exception as e:
            logger.error(f"Failed to initialize Sentinel: {e}")
            raise

    def get_master_address(self) -> tuple | None:
        """
        الحصول على عنوان Master الحالي

        Returns:
            (host, port) أو None
        """
        try:
            return self._sentinel.discover_master(self.config.master_name)
        except Exception as e:
            logger.error(f"Failed to discover master: {e}")
            return None

    def get_slaves_addresses(self) -> list[tuple]:
        """
        الحصول على عناوين جميع Slaves

        Returns:
            قائمة من (host, port)
        """
        try:
            return self._sentinel.discover_slaves(self.config.master_name)
        except Exception as e:
            logger.error(f"Failed to discover slaves: {e}")
            return []

    @contextmanager
    def get_connection(self, read_only: bool = False):
        """
        Context manager للحصول على اتصال Redis

        Args:
            read_only: استخدام Slave للقراءة فقط

        Yields:
            Redis connection
        """
        conn = self._slave if read_only else self._master
        try:
            yield conn
        finally:
            pass  # Connection pooling handles cleanup

    def _execute_with_retry(
        self, func, *args, max_retries: int = 3, retry_delay: float = 0.5, **kwargs
    ) -> Any:
        """
        تنفيذ عملية مع إعادة المحاولة

        Args:
            func: الدالة المراد تنفيذها
            max_retries: عدد المحاولات
            retry_delay: التأخير بين المحاولات (ثواني)

        Returns:
            نتيجة الدالة
        """
        last_exception = None

        for attempt in range(max_retries):
            try:
                return self._circuit_breaker.call(func, *args, **kwargs)
            except (ConnectionError, TimeoutError) as e:
                last_exception = e
                if attempt < max_retries - 1:
                    delay = retry_delay * (2**attempt)  # Exponential backoff
                    logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s due to: {e}")
                    time.sleep(delay)
                else:
                    logger.error(f"All {max_retries} retries failed")

        raise last_exception

    # ─────────────────────────────────────────────────────────────────────────
    # Basic Operations
    # ─────────────────────────────────────────────────────────────────────────

    def set(
        self,
        key: str,
        value: Any,
        ex: int | None = None,
        px: int | None = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        """
        تعيين قيمة مفتاح

        Args:
            key: المفتاح
            value: القيمة
            ex: انتهاء الصلاحية بالثواني
            px: انتهاء الصلاحية بالميلي ثانية
            nx: تعيين فقط إذا لم يكن موجوداً
            xx: تعيين فقط إذا كان موجوداً

        Returns:
            True إذا نجحت العملية
        """
        return self._execute_with_retry(self._master.set, key, value, ex=ex, px=px, nx=nx, xx=xx)

    def get(self, key: str, use_slave: bool = True) -> str | None:
        """
        الحصول على قيمة مفتاح

        Args:
            key: المفتاح
            use_slave: استخدام Slave للقراءة

        Returns:
            القيمة أو None
        """
        conn = self._slave if use_slave else self._master
        return self._execute_with_retry(conn.get, key)

    def delete(self, *keys: str) -> int:
        """
        حذف مفاتيح

        Args:
            keys: المفاتيح المراد حذفها

        Returns:
            عدد المفاتيح المحذوفة
        """
        return self._execute_with_retry(self._master.delete, *keys)

    def exists(self, *keys: str) -> int:
        """
        التحقق من وجود مفاتيح

        Args:
            keys: المفاتيح

        Returns:
            عدد المفاتيح الموجودة
        """
        return self._execute_with_retry(self._slave.exists, *keys)

    def expire(self, key: str, seconds: int) -> bool:
        """
        تعيين وقت انتهاء صلاحية مفتاح

        Args:
            key: المفتاح
            seconds: الثواني

        Returns:
            True إذا نجحت العملية
        """
        return self._execute_with_retry(self._master.expire, key, seconds)

    def ttl(self, key: str) -> int:
        """
        الحصول على وقت انتهاء الصلاحية المتبقي

        Args:
            key: المفتاح

        Returns:
            الثواني المتبقية (-1 لا نهاية، -2 غير موجود)
        """
        return self._execute_with_retry(self._slave.ttl, key)

    # ─────────────────────────────────────────────────────────────────────────
    # Hash Operations
    # ─────────────────────────────────────────────────────────────────────────

    def hset(self, name: str, key: str, value: Any) -> int:
        """تعيين قيمة في Hash"""
        return self._execute_with_retry(self._master.hset, name, key, value)

    def hget(self, name: str, key: str, use_slave: bool = True) -> str | None:
        """الحصول على قيمة من Hash"""
        conn = self._slave if use_slave else self._master
        return self._execute_with_retry(conn.hget, name, key)

    def hgetall(self, name: str, use_slave: bool = True) -> dict:
        """الحصول على جميع قيم Hash"""
        conn = self._slave if use_slave else self._master
        return self._execute_with_retry(conn.hgetall, name)

    def hdel(self, name: str, *keys: str) -> int:
        """حذف مفاتيح من Hash"""
        return self._execute_with_retry(self._master.hdel, name, *keys)

    # ─────────────────────────────────────────────────────────────────────────
    # List Operations
    # ─────────────────────────────────────────────────────────────────────────

    def lpush(self, name: str, *values: Any) -> int:
        """إضافة عناصر في بداية القائمة"""
        return self._execute_with_retry(self._master.lpush, name, *values)

    def rpush(self, name: str, *values: Any) -> int:
        """إضافة عناصر في نهاية القائمة"""
        return self._execute_with_retry(self._master.rpush, name, *values)

    def lpop(self, name: str) -> str | None:
        """إزالة وإرجاع أول عنصر"""
        return self._execute_with_retry(self._master.lpop, name)

    def rpop(self, name: str) -> str | None:
        """إزالة وإرجاع آخر عنصر"""
        return self._execute_with_retry(self._master.rpop, name)

    def lrange(self, name: str, start: int, end: int, use_slave: bool = True) -> list:
        """الحصول على نطاق من القائمة"""
        conn = self._slave if use_slave else self._master
        return self._execute_with_retry(conn.lrange, name, start, end)

    # ─────────────────────────────────────────────────────────────────────────
    # Set Operations
    # ─────────────────────────────────────────────────────────────────────────

    def sadd(self, name: str, *values: Any) -> int:
        """إضافة عناصر إلى مجموعة"""
        return self._execute_with_retry(self._master.sadd, name, *values)

    def smembers(self, name: str, use_slave: bool = True) -> set:
        """الحصول على جميع عناصر المجموعة"""
        conn = self._slave if use_slave else self._master
        return self._execute_with_retry(conn.smembers, name)

    def srem(self, name: str, *values: Any) -> int:
        """إزالة عناصر من مجموعة"""
        return self._execute_with_retry(self._master.srem, name, *values)

    # ─────────────────────────────────────────────────────────────────────────
    # Sorted Set Operations
    # ─────────────────────────────────────────────────────────────────────────

    def zadd(self, name: str, mapping: dict[Any, float]) -> int:
        """إضافة عناصر إلى مجموعة مرتبة"""
        return self._execute_with_retry(self._master.zadd, name, mapping)

    def zrange(
        self,
        name: str,
        start: int,
        end: int,
        withscores: bool = False,
        use_slave: bool = True,
    ) -> list:
        """الحصول على نطاق من المجموعة المرتبة"""
        conn = self._slave if use_slave else self._master
        return self._execute_with_retry(conn.zrange, name, start, end, withscores=withscores)

    def zrem(self, name: str, *values: Any) -> int:
        """إزالة عناصر من مجموعة مرتبة"""
        return self._execute_with_retry(self._master.zrem, name, *values)

    # ─────────────────────────────────────────────────────────────────────────
    # Pipeline Operations
    # ─────────────────────────────────────────────────────────────────────────

    @contextmanager
    def pipeline(self, transaction: bool = True):
        """
        إنشاء Pipeline لتنفيذ عمليات متعددة

        Args:
            transaction: استخدام Transaction

        Example:
            >>> with client.pipeline() as pipe:
            ...     pipe.set('key1', 'value1')
            ...     pipe.set('key2', 'value2')
            ...     pipe.execute()
        """
        pipe = self._master.pipeline(transaction=transaction)
        try:
            yield pipe
        finally:
            pass

    # ─────────────────────────────────────────────────────────────────────────
    # Health & Monitoring
    # ─────────────────────────────────────────────────────────────────────────

    def ping(self) -> bool:
        """
        فحص الاتصال

        Returns:
            True إذا كان الاتصال نشطاً
        """
        try:
            return self._master.ping()
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return False

    def info(self, section: str | None = None) -> dict:
        """
        الحصول على معلومات Redis

        Args:
            section: القسم المطلوب (اختياري)

        Returns:
            معلومات الخادم
        """
        try:
            return self._master.info(section)
        except Exception as e:
            logger.error(f"Failed to get info: {e}")
            return {}

    def get_sentinel_info(self) -> dict:
        """
        الحصول على معلومات Sentinel

        Returns:
            معلومات حالة النظام
        """
        try:
            master_addr = self.get_master_address()
            slaves_addrs = self.get_slaves_addresses()

            return {
                "master": master_addr,
                "slaves": slaves_addrs,
                "master_name": self.config.master_name,
                "sentinel_count": len(self.config.get_sentinels()),
                "is_connected": self.ping(),
                "circuit_breaker_state": self._circuit_breaker.state,
            }
        except Exception as e:
            logger.error(f"Failed to get sentinel info: {e}")
            return {"error": str(e)}

    def health_check(self) -> dict[str, Any]:
        """
        فحص صحة شامل

        Returns:
            تقرير الصحة
        """
        health = {"status": "healthy", "timestamp": time.time(), "checks": {}}

        # Check master connection
        try:
            health["checks"]["master_ping"] = self.ping()
        except Exception as e:
            health["checks"]["master_ping"] = False
            health["status"] = "unhealthy"
            health["error"] = str(e)

        # Check sentinel
        try:
            sentinel_info = self.get_sentinel_info()
            health["checks"]["sentinel"] = sentinel_info
        except Exception as e:
            health["checks"]["sentinel"] = {"error": str(e)}
            health["status"] = "degraded"

        # Check circuit breaker
        health["checks"]["circuit_breaker"] = self._circuit_breaker.state
        if self._circuit_breaker.state == "OPEN":
            health["status"] = "degraded"

        return health

    def close(self):
        """إغلاق جميع الاتصالات"""
        try:
            if self._master:
                self._master.close()
            if self._slave:
                self._slave.close()
            logger.info("Redis connections closed")
        except Exception as e:
            logger.error(f"Error closing connections: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# Singleton Instance
# ═══════════════════════════════════════════════════════════════════════════════

_redis_client: RedisSentinelClient | None = None


def get_redis_client() -> RedisSentinelClient:
    """
    الحصول على Redis Client (Singleton)

    Returns:
        RedisSentinelClient instance
    """
    global _redis_client

    if _redis_client is None:
        _redis_client = RedisSentinelClient()

    return _redis_client


def close_redis_client():
    """إغلاق Redis Client"""
    global _redis_client

    if _redis_client is not None:
        _redis_client.close()
        _redis_client = None
