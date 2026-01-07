"""
Redis Sentinel Usage Examples
==============================

أمثلة على استخدام Redis Sentinel في تطبيقات مختلفة

Author: Sahool Platform Team
"""

import contextlib
import json
import time
import uuid
from collections.abc import Callable
from functools import wraps
from typing import Any

from redis_sentinel import get_redis_client

# ═══════════════════════════════════════════════════════════════════════════
# Example 1: Basic Cache Decorator
# ═══════════════════════════════════════════════════════════════════════════


def cache_result(key_prefix: str, ttl: int = 3600):
    """
    Cache function results in Redis

    Args:
        key_prefix: بادئة المفتاح
        ttl: وقت انتهاء الصلاحية بالثواني

    Example:
        @cache_result('user:profile', ttl=3600)
        def get_user_profile(user_id: int):
            return db.query(f"SELECT * FROM users WHERE id = {user_id}")
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            redis = get_redis_client()

            # إنشاء مفتاح فريد
            cache_key = f"{key_prefix}:{args}:{kwargs}"

            # محاولة القراءة من Cache
            cached = redis.get(cache_key, use_slave=True)
            if cached:
                print(f"✓ Cache hit: {cache_key}")
                return json.loads(cached)

            print(f"✗ Cache miss: {cache_key}")

            # تنفيذ الدالة
            result = func(*args, **kwargs)

            # حفظ في Cache
            redis.set(cache_key, json.dumps(result), ex=ttl)

            return result

        return wrapper

    return decorator


# ═══════════════════════════════════════════════════════════════════════════
# Example 2: Rate Limiter
# ═══════════════════════════════════════════════════════════════════════════


class RateLimiter:
    """
    معدل تحديد الطلبات باستخدام Redis

    Example:
        limiter = RateLimiter(max_requests=100, window=60)
        if limiter.is_allowed('user:1000'):
            process_request()
        else:
            return "Rate limit exceeded", 429
    """

    def __init__(self, max_requests: int = 100, window: int = 60):
        """
        Args:
            max_requests: الحد الأقصى للطلبات
            window: نافذة الوقت بالثواني
        """
        self.redis = get_redis_client()
        self.max_requests = max_requests
        self.window = window

    def is_allowed(self, identifier: str) -> bool:
        """
        التحقق من السماح بالطلب

        Args:
            identifier: معرف المستخدم أو IP

        Returns:
            True إذا كان مسموحاً
        """
        key = f"rate_limit:{identifier}"
        current = int(time.time())

        # استخدام Sorted Set لتتبع الطلبات
        with self.redis.pipeline() as pipe:
            # حذف الطلبات القديمة
            pipe.zremrangebyscore(key, 0, current - self.window)
            # إضافة الطلب الحالي
            pipe.zadd(key, {str(current): current})
            # عد الطلبات
            pipe.zcard(key)
            # تعيين TTL
            pipe.expire(key, self.window)
            results = pipe.execute()

        request_count = results[2]
        return request_count <= self.max_requests

    def get_remaining(self, identifier: str) -> int:
        """
        الحصول على عدد الطلبات المتبقية

        Args:
            identifier: معرف المستخدم

        Returns:
            عدد الطلبات المتبقية
        """
        key = f"rate_limit:{identifier}"
        current = int(time.time())

        # حذف الطلبات القديمة وعد الحالية
        with self.redis.pipeline() as pipe:
            pipe.zremrangebyscore(key, 0, current - self.window)
            pipe.zcard(key)
            results = pipe.execute()

        current_count = results[1]
        return max(0, self.max_requests - current_count)


# ═══════════════════════════════════════════════════════════════════════════
# Example 3: Distributed Lock
# ═══════════════════════════════════════════════════════════════════════════


class DistributedLock:
    """
    قفل موزع باستخدام Redis

    Example:
        lock = DistributedLock('process:export', timeout=30)
        if lock.acquire():
            try:
                process_export()
            finally:
                lock.release()
    """

    def __init__(self, lock_name: str, timeout: int = 10):
        """
        Args:
            lock_name: اسم القفل
            timeout: مهلة القفل بالثواني
        """
        self.redis = get_redis_client()
        self.lock_name = f"lock:{lock_name}"
        self.timeout = timeout
        self.identifier = str(uuid.uuid4())

    def acquire(self, blocking: bool = True, acquire_timeout: int | None = None) -> bool:
        """
        الحصول على القفل

        Args:
            blocking: انتظار حتى يصبح القفل متاحاً
            acquire_timeout: مهلة الانتظار

        Returns:
            True إذا تم الحصول على القفل
        """
        end_time = time.time() + (acquire_timeout or self.timeout)

        while True:
            # محاولة الحصول على القفل
            if self.redis.set(self.lock_name, self.identifier, nx=True, ex=self.timeout):
                return True

            if not blocking:
                return False

            if time.time() >= end_time:
                return False

            # انتظار قصير قبل المحاولة مرة أخرى
            time.sleep(0.001)

    def release(self) -> bool:
        """
        تحرير القفل

        Returns:
            True إذا تم التحرير بنجاح
        """
        # التحقق من الملكية قبل الحذف
        value = self.redis.get(self.lock_name, use_slave=False)
        if value == self.identifier:
            self.redis.delete(self.lock_name)
            return True
        return False

    def __enter__(self):
        """Context manager support"""
        if not self.acquire():
            raise Exception(f"Could not acquire lock: {self.lock_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support"""
        self.release()


# ═══════════════════════════════════════════════════════════════════════════
# Example 4: Session Manager
# ═══════════════════════════════════════════════════════════════════════════


class SessionManager:
    """
    إدارة جلسات المستخدم باستخدام Redis

    Example:
        session = SessionManager()
        session.create('user:1000', {'name': 'Ahmed'}, ttl=3600)
        data = session.get('user:1000')
    """

    def __init__(self, prefix: str = "session"):
        """
        Args:
            prefix: بادئة مفاتيح الجلسات
        """
        self.redis = get_redis_client()
        self.prefix = prefix

    def create(self, session_id: str, data: dict, ttl: int = 3600) -> bool:
        """
        إنشاء جلسة جديدة

        Args:
            session_id: معرف الجلسة
            data: بيانات الجلسة
            ttl: مدة الجلسة بالثواني

        Returns:
            True إذا نجحت العملية
        """
        key = f"{self.prefix}:{session_id}"
        return self.redis.set(key, json.dumps(data), ex=ttl)

    def get(self, session_id: str) -> dict | None:
        """
        الحصول على بيانات الجلسة

        Args:
            session_id: معرف الجلسة

        Returns:
            بيانات الجلسة أو None
        """
        key = f"{self.prefix}:{session_id}"
        data = self.redis.get(key, use_slave=True)
        return json.loads(data) if data else None

    def update(self, session_id: str, data: dict, ttl: int | None = None) -> bool:
        """
        تحديث بيانات الجلسة

        Args:
            session_id: معرف الجلسة
            data: البيانات الجديدة
            ttl: مدة الجلسة (اختياري)

        Returns:
            True إذا نجحت العملية
        """
        key = f"{self.prefix}:{session_id}"

        if ttl:
            return self.redis.set(key, json.dumps(data), ex=ttl)
        else:
            # الحفاظ على TTL الحالي
            current_ttl = self.redis.ttl(key)
            if current_ttl > 0:
                return self.redis.set(key, json.dumps(data), ex=current_ttl)
            return self.redis.set(key, json.dumps(data))

    def delete(self, session_id: str) -> bool:
        """
        حذف جلسة

        Args:
            session_id: معرف الجلسة

        Returns:
            True إذا تم الحذف
        """
        key = f"{self.prefix}:{session_id}"
        return self.redis.delete(key) > 0

    def refresh(self, session_id: str, ttl: int = 3600) -> bool:
        """
        تجديد مدة الجلسة

        Args:
            session_id: معرف الجلسة
            ttl: المدة الجديدة

        Returns:
            True إذا نجحت العملية
        """
        key = f"{self.prefix}:{session_id}"
        return self.redis.expire(key, ttl)


# ═══════════════════════════════════════════════════════════════════════════
# Example 5: Pub/Sub Event System
# ═══════════════════════════════════════════════════════════════════════════


class EventPublisher:
    """
    نشر الأحداث باستخدام Redis Pub/Sub

    Example:
        publisher = EventPublisher()
        publisher.publish('notifications', {'user': 1000, 'message': 'Hello'})
    """

    def __init__(self):
        self.redis = get_redis_client()

    def publish(self, channel: str, message: Any) -> int:
        """
        نشر حدث

        Args:
            channel: قناة النشر
            message: الرسالة

        Returns:
            عدد المشتركين الذين استلموا الرسالة
        """
        # التحويل إلى JSON إذا لم يكن نص
        if not isinstance(message, str):
            message = json.dumps(message)

        with self.redis.get_connection() as conn:
            return conn.publish(channel, message)


class EventSubscriber:
    """
    الاشتراك في الأحداث باستخدام Redis Pub/Sub

    Example:
        subscriber = EventSubscriber()
        subscriber.subscribe('notifications', on_notification)
        subscriber.listen()
    """

    def __init__(self):
        self.redis = get_redis_client()
        self.pubsub = None
        self.handlers = {}

    def subscribe(self, channel: str, handler: Callable):
        """
        الاشتراك في قناة

        Args:
            channel: اسم القناة
            handler: دالة معالجة الرسائل
        """
        if self.pubsub is None:
            with self.redis.get_connection() as conn:
                self.pubsub = conn.pubsub()

        self.handlers[channel] = handler
        self.pubsub.subscribe(channel)

    def listen(self):
        """
        الاستماع للرسائل
        """
        if self.pubsub is None:
            raise Exception("No channels subscribed")

        print("Listening for events...")
        for message in self.pubsub.listen():
            if message["type"] == "message":
                channel = message["channel"]
                data = message["data"]

                # محاولة تحويل من JSON
                with contextlib.suppress(Exception):
                    data = json.loads(data)

                # استدعاء المعالج
                if channel in self.handlers:
                    self.handlers[channel](data)


# ═══════════════════════════════════════════════════════════════════════════
# Example Usage
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Example 1: Cache
    @cache_result("user:profile", ttl=60)
    def get_user(user_id: int):
        print(f"Fetching user {user_id} from database...")
        return {"id": user_id, "name": f"User {user_id}"}

    print("Example 1: Cache Decorator")
    print(get_user(1000))  # Cache miss
    print(get_user(1000))  # Cache hit
    print()

    # Example 2: Rate Limiter
    print("Example 2: Rate Limiter")
    limiter = RateLimiter(max_requests=5, window=10)
    for i in range(7):
        if limiter.is_allowed("user:1000"):
            print(f"  Request {i + 1}: Allowed (Remaining: {limiter.get_remaining('user:1000')})")
        else:
            print(f"  Request {i + 1}: Denied (Rate limit exceeded)")
    print()

    # Example 3: Distributed Lock
    print("Example 3: Distributed Lock")
    with DistributedLock("export:process", timeout=5) as lock:
        print("  Lock acquired, processing...")
        time.sleep(1)
        print("  Processing completed")
    print("  Lock released")
    print()

    # Example 4: Session Manager
    print("Example 4: Session Manager")
    session = SessionManager()
    session.create("user:1000", {"username": "ahmed", "role": "admin"}, ttl=300)
    data = session.get("user:1000")
    print(f"  Session data: {data}")
    session.delete("user:1000")
    print()

    # Example 5: Events
    print("Example 5: Pub/Sub Events")
    publisher = EventPublisher()
    count = publisher.publish("test", {"message": "Hello World"})
    print(f"  Published to {count} subscribers")
