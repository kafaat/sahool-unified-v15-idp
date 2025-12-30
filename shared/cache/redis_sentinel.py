"""
Redis Sentinel Client for High Availability
===========================================

يوفر هذا الملف اتصالاً بـ Redis Sentinel مع:
- Automatic failover handling
- Connection pooling
- Circuit breaker pattern
- Health monitoring
- Retry logic with exponential backoff

Author: Sahool Platform Team
License: MIT
"""

import logging
import os
import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Union

import redis
from redis.sentinel import Sentinel
from redis.exceptions import (
    ConnectionError,
    RedisError,
    TimeoutError,
    ResponseError
)

logger = logging.getLogger(__name__)


class RedisSentinelConfig:
    """
    تكوين Redis Sentinel

    Environment Variables:
        REDIS_SENTINEL_HOSTS: قائمة بعناوين Sentinel (مفصولة بفاصلة)
        REDIS_SENTINEL_PORT: منفذ Sentinel (افتراضي: 26379)
        REDIS_PASSWORD: كلمة مرور Redis
        REDIS_MASTER_NAME: اسم المجموعة الرئيسية (افتراضي: sahool-master)
        REDIS_DB: رقم قاعدة البيانات (افتراضي: 0)
        REDIS_SOCKET_TIMEOUT: مهلة الاتصال بالثواني (افتراضي: 5)
        REDIS_SOCKET_CONNECT_TIMEOUT: مهلة الاتصال الأولي (افتراضي: 5)
        REDIS_MAX_CONNECTIONS: الحد الأقصى للاتصالات (افتراضي: 50)
    """

    def __init__(self):
        # Sentinel configuration
        self.sentinel_hosts = os.getenv(
            'REDIS_SENTINEL_HOSTS',
            'localhost,localhost,localhost'
        ).split(',')
        self.sentinel_port = int(os.getenv('REDIS_SENTINEL_PORT', '26379'))
        self.sentinel_ports = [26379, 26380, 26381]  # Multiple sentinel ports

        # Redis configuration
        self.password = os.getenv('REDIS_PASSWORD', 'redis_password')
        self.master_name = os.getenv('REDIS_MASTER_NAME', 'sahool-master')
        self.db = int(os.getenv('REDIS_DB', '0'))

        # Connection settings
        self.socket_timeout = int(os.getenv('REDIS_SOCKET_TIMEOUT', '5'))
        self.socket_connect_timeout = int(os.getenv('REDIS_SOCKET_CONNECT_TIMEOUT', '5'))
        self.socket_keepalive = True
        self.socket_keepalive_options = {
            1: 1,  # TCP_KEEPIDLE
            2: 1,  # TCP_KEEPINTVL
            3: 3   # TCP_KEEPCNT
        }

        # Connection pool settings
        self.max_connections = int(os.getenv('REDIS_MAX_CONNECTIONS', '50'))
        self.retry_on_timeout = True
        self.health_check_interval = 30

        # Failover settings
        self.sentinel_kwargs = {
            'socket_timeout': self.socket_timeout,
            'socket_connect_timeout': self.socket_connect_timeout,
            'password': self.password,
        }

    def get_sentinels(self) -> List[tuple]:
        """
        الحصول على قائمة Sentinels

        Returns:
            قائمة من tuples (host, port)
        """
        sentinels = []
        for i, host in enumerate(self.sentinel_hosts):
            port = self.sentinel_ports[i] if i < len(self.sentinel_ports) else self.sentinel_port
            sentinels.append((host.strip(), port))
        return sentinels


class CircuitBreaker:
    """
    Circuit Breaker Pattern لحماية من الأخطاء المتكررة

    States:
        - CLOSED: عمل عادي
        - OPEN: الخدمة معطلة، رفض الطلبات
        - HALF_OPEN: اختبار استعادة الخدمة
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'

    def call(self, func, *args, **kwargs):
        """
        استدعاء دالة مع حماية Circuit Breaker
        """
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'HALF_OPEN'
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """نجاح العملية"""
        self.failure_count = 0
        self.state = 'CLOSED'

    def _on_failure(self):
        """فشل العملية"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.error(f"Circuit breaker opened after {self.failure_count} failures")


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

    def __init__(self, config: Optional[RedisSentinelConfig] = None):
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
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=RedisError
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

    def get_master_address(self) -> Optional[tuple]:
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

    def get_slaves_addresses(self) -> List[tuple]:
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
        self,
        func,
        *args,
        max_retries: int = 3,
        retry_delay: float = 0.5,
        **kwargs
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
                    delay = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(
                        f"Retry {attempt + 1}/{max_retries} after {delay}s due to: {e}"
                    )
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
        ex: Optional[int] = None,
        px: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
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
        return self._execute_with_retry(
            self._master.set,
            key,
            value,
            ex=ex,
            px=px,
            nx=nx,
            xx=xx
        )

    def get(self, key: str, use_slave: bool = True) -> Optional[str]:
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

    def hget(self, name: str, key: str, use_slave: bool = True) -> Optional[str]:
        """الحصول على قيمة من Hash"""
        conn = self._slave if use_slave else self._master
        return self._execute_with_retry(conn.hget, name, key)

    def hgetall(self, name: str, use_slave: bool = True) -> Dict:
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

    def lpop(self, name: str) -> Optional[str]:
        """إزالة وإرجاع أول عنصر"""
        return self._execute_with_retry(self._master.lpop, name)

    def rpop(self, name: str) -> Optional[str]:
        """إزالة وإرجاع آخر عنصر"""
        return self._execute_with_retry(self._master.rpop, name)

    def lrange(self, name: str, start: int, end: int, use_slave: bool = True) -> List:
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

    def zadd(self, name: str, mapping: Dict[Any, float]) -> int:
        """إضافة عناصر إلى مجموعة مرتبة"""
        return self._execute_with_retry(self._master.zadd, name, mapping)

    def zrange(
        self,
        name: str,
        start: int,
        end: int,
        withscores: bool = False,
        use_slave: bool = True
    ) -> List:
        """الحصول على نطاق من المجموعة المرتبة"""
        conn = self._slave if use_slave else self._master
        return self._execute_with_retry(
            conn.zrange,
            name,
            start,
            end,
            withscores=withscores
        )

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

    def info(self, section: Optional[str] = None) -> Dict:
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

    def get_sentinel_info(self) -> Dict:
        """
        الحصول على معلومات Sentinel

        Returns:
            معلومات حالة النظام
        """
        try:
            master_addr = self.get_master_address()
            slaves_addrs = self.get_slaves_addresses()

            return {
                'master': master_addr,
                'slaves': slaves_addrs,
                'master_name': self.config.master_name,
                'sentinel_count': len(self.config.get_sentinels()),
                'is_connected': self.ping(),
                'circuit_breaker_state': self._circuit_breaker.state,
            }
        except Exception as e:
            logger.error(f"Failed to get sentinel info: {e}")
            return {'error': str(e)}

    def health_check(self) -> Dict[str, Any]:
        """
        فحص صحة شامل

        Returns:
            تقرير الصحة
        """
        health = {
            'status': 'healthy',
            'timestamp': time.time(),
            'checks': {}
        }

        # Check master connection
        try:
            health['checks']['master_ping'] = self.ping()
        except Exception as e:
            health['checks']['master_ping'] = False
            health['status'] = 'unhealthy'
            health['error'] = str(e)

        # Check sentinel
        try:
            sentinel_info = self.get_sentinel_info()
            health['checks']['sentinel'] = sentinel_info
        except Exception as e:
            health['checks']['sentinel'] = {'error': str(e)}
            health['status'] = 'degraded'

        # Check circuit breaker
        health['checks']['circuit_breaker'] = self._circuit_breaker.state
        if self._circuit_breaker.state == 'OPEN':
            health['status'] = 'degraded'

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

_redis_client: Optional[RedisSentinelClient] = None


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
