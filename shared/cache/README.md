# Redis Sentinel - High Availability Configuration

# دليل التوافر العالي لـ Redis Sentinel

## نظرة عامة | Overview

يوفر هذا النظام **التوافر العالي (High Availability)** لـ Redis باستخدام **Redis Sentinel**. يضمن النظام استمرارية الخدمة حتى في حالة فشل المخدم الرئيسي من خلال الانتقال التلقائي (Automatic Failover) إلى نسخة احتياطية.

This system provides **High Availability** for Redis using **Redis Sentinel**. The system ensures service continuity even in case of master server failure through automatic failover to a backup replica.

### المكونات | Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Redis Sentinel HA                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌─────────────┐ │
│  │   Sentinel 1  │     │   Sentinel 2  │     │  Sentinel 3 │ │
│  │  Port: 26379  │     │  Port: 26380  │     │ Port: 26381 │ │
│  └──────┬───────┘     └──────┬───────┘     └──────┬──────┘ │
│         │                     │                     │         │
│         └─────────────────────┴─────────────────────┘         │
│                            │                                  │
│                            ▼                                  │
│         ┌──────────────────────────────────┐                 │
│         │      Quorum = 2 (Majority)       │                 │
│         └──────────────────────────────────┘                 │
│                            │                                  │
│         ┌──────────────────┴────────────────┐                │
│         ▼                                    ▼                │
│  ┌─────────────┐                    ┌──────────────┐         │
│  │Redis Master │───────replication──▶│Redis Replica1│         │
│  │ Port: 6379  │                    │  Port: 6380  │         │
│  └─────────────┘                    └──────────────┘         │
│         │                                                     │
│         │                            ┌──────────────┐         │
│         └────────replication────────▶│Redis Replica2│         │
│                                      │  Port: 6381  │         │
│                                      └──────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### الميزات | Features

- ✅ **Automatic Failover**: انتقال تلقائي للنسخ الاحتياطية
- ✅ **Data Replication**: نسخ البيانات تلقائياً
- ✅ **Connection Pooling**: إدارة الاتصالات الفعالة
- ✅ **Circuit Breaker**: حماية من الأخطاء المتكررة
- ✅ **Health Monitoring**: مراقبة صحة النظام
- ✅ **Retry Logic**: إعادة المحاولة التلقائية
- ✅ **Read/Write Separation**: فصل القراءة والكتابة

---

## التثبيت والإعداد | Installation & Setup

### المتطلبات | Requirements

```bash
# Docker & Docker Compose
docker --version  # >= 20.10
docker-compose --version  # >= 1.29

# Redis CLI (للاختبار)
redis-cli --version  # >= 7.0
```

### 1. إعداد المتغيرات البيئية | Environment Variables

أضف المتغيرات التالية إلى ملف `.env`:

```bash
# Redis Configuration
REDIS_PASSWORD=your_secure_password_here
REDIS_MASTER_NAME=sahool-master
REDIS_DB=0

# Sentinel Configuration
REDIS_SENTINEL_HOST_1=localhost
REDIS_SENTINEL_HOST_2=localhost
REDIS_SENTINEL_HOST_3=localhost
REDIS_SENTINEL_PORT=26379

# Connection Settings
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5
REDIS_MAX_CONNECTIONS=50
```

### 2. تشغيل Redis Sentinel | Start Redis Sentinel

```bash
# بدء جميع الخدمات
docker-compose -f docker-compose.redis-ha.yml up -d

# التحقق من الحالة
docker-compose -f docker-compose.redis-ha.yml ps

# عرض السجلات
docker-compose -f docker-compose.redis-ha.yml logs -f
```

### 3. التحقق من الإعداد | Verify Setup

```bash
# تشغيل فحص الصحة
./infra/redis-ha/health-check.sh

# التحقق من Master
redis-cli -p 6379 -a $REDIS_PASSWORD ping
# الناتج: PONG

# التحقق من Sentinel
redis-cli -p 26379 ping
# الناتج: PONG

# الحصول على معلومات Master
redis-cli -p 26379 SENTINEL master sahool-master

# قائمة Replicas
redis-cli -p 26379 SENTINEL slaves sahool-master
```

---

## الاستخدام | Usage

### Python

#### الإعداد الأساسي | Basic Setup

```python
from shared.cache import get_redis_client

# الحصول على Redis Client
redis = get_redis_client()

# التحقق من الاتصال
if redis.ping():
    print("✓ Connected to Redis Sentinel")
```

#### العمليات الأساسية | Basic Operations

```python
# تعيين قيمة
redis.set("user:1000", "Ahmed", ex=3600)  # تنتهي بعد ساعة

# قراءة قيمة (من Slave)
value = redis.get("user:1000", use_slave=True)
print(f"User: {value}")

# حذف مفتاح
redis.delete("user:1000")

# التحقق من وجود مفتاح
exists = redis.exists("user:1000")
```

#### Hash Operations

```python
# تعيين قيم Hash
redis.hset("user:1000:profile", "name", "Ahmed")
redis.hset("user:1000:profile", "email", "ahmed@example.com")
redis.hset("user:1000:profile", "age", "30")

# قراءة قيمة واحدة
name = redis.hget("user:1000:profile", "name")

# قراءة جميع القيم
profile = redis.hgetall("user:1000:profile")
print(profile)
# {'name': 'Ahmed', 'email': 'ahmed@example.com', 'age': '30'}
```

#### List Operations

```python
# إضافة عناصر
redis.rpush("notifications:1000", "Welcome!", "New message")

# قراءة القائمة
notifications = redis.lrange("notifications:1000", 0, -1)
print(notifications)  # ['Welcome!', 'New message']

# إزالة أول عنصر
first = redis.lpop("notifications:1000")
```

#### Set Operations

```python
# إضافة إلى مجموعة
redis.sadd("user:1000:interests", "farming", "technology", "agriculture")

# قراءة المجموعة
interests = redis.smembers("user:1000:interests")
print(interests)  # {'farming', 'technology', 'agriculture'}
```

#### Pipeline for Batch Operations

```python
# استخدام Pipeline لعمليات متعددة
with redis.pipeline() as pipe:
    pipe.set("key1", "value1")
    pipe.set("key2", "value2")
    pipe.set("key3", "value3")
    results = pipe.execute()
```

#### Health Check

```python
# فحص صحة شامل
health = redis.health_check()
print(f"Status: {health['status']}")
print(f"Master Ping: {health['checks']['master_ping']}")
print(f"Circuit Breaker: {health['checks']['circuit_breaker']}")

# معلومات Sentinel
sentinel_info = redis.get_sentinel_info()
print(f"Master: {sentinel_info['master']}")
print(f"Slaves: {sentinel_info['slaves']}")
```

---

### TypeScript / Node.js

#### الإعداد الأساسي | Basic Setup

```typescript
import { getRedisSentinelClient } from "@sahool/cache/redis-sentinel";

// الحصول على Redis Client
const redis = getRedisSentinelClient();

// التحقق من الاتصال
const isConnected = await redis.ping();
console.log(`✓ Connected: ${isConnected}`);
```

#### العمليات الأساسية | Basic Operations

```typescript
// تعيين قيمة
await redis.set("user:1000", "Ahmed", { ex: 3600 }); // تنتهي بعد ساعة

// قراءة قيمة (من Slave)
const value = await redis.get("user:1000", true);
console.log(`User: ${value}`);

// حذف مفتاح
await redis.delete("user:1000");

// التحقق من وجود مفتاح
const exists = await redis.exists("user:1000");
```

#### Hash Operations

```typescript
// تعيين قيم Hash
await redis.hset("user:1000:profile", "name", "Ahmed");
await redis.hset("user:1000:profile", "email", "ahmed@example.com");
await redis.hset("user:1000:profile", "age", "30");

// قراءة قيمة واحدة
const name = await redis.hget("user:1000:profile", "name");

// قراءة جميع القيم
const profile = await redis.hgetall("user:1000:profile");
console.log(profile);
// { name: 'Ahmed', email: 'ahmed@example.com', age: '30' }
```

#### List Operations

```typescript
// إضافة عناصر
await redis.rpush("notifications:1000", "Welcome!", "New message");

// قراءة القائمة
const notifications = await redis.lrange("notifications:1000", 0, -1);
console.log(notifications); // ['Welcome!', 'New message']

// إزالة أول عنصر
const first = await redis.lpop("notifications:1000");
```

#### Pipeline for Batch Operations

```typescript
// استخدام Pipeline لعمليات متعددة
const pipeline = redis.pipeline();
pipeline.set("key1", "value1");
pipeline.set("key2", "value2");
pipeline.set("key3", "value3");
const results = await pipeline.exec();
```

#### Health Check

```typescript
// فحص صحة شامل
const health = await redis.healthCheck();
console.log(`Status: ${health.status}`);
console.log(`Master Ping: ${health.checks.masterPing}`);
console.log(`Circuit Breaker: ${health.checks.circuitBreaker}`);

// معلومات Sentinel
const sentinelInfo = await redis.getSentinelInfo();
console.log(`Master: ${JSON.stringify(sentinelInfo.master)}`);
console.log(`Slaves: ${JSON.stringify(sentinelInfo.slaves)}`);
```

---

## اختبار Failover | Testing Failover

### اختبار يدوي | Manual Test

```bash
# 1. الحصول على Master الحالي
redis-cli -p 26379 SENTINEL master sahool-master | grep -E "ip|port"

# 2. محاكاة فشل Master (إيقاف Container)
docker stop sahool-redis-master

# 3. مراقبة Failover (يستغرق حوالي 5 ثواني)
watch -n 1 'redis-cli -p 26379 SENTINEL master sahool-master | grep -E "ip|port|flags"'

# 4. التحقق من Master الجديد
redis-cli -p 26379 SENTINEL master sahool-master

# 5. إعادة تشغيل Master القديم (سيصبح Replica)
docker start sahool-redis-master

# 6. التحقق من حالة Replication
redis-cli -p 6379 -a $REDIS_PASSWORD INFO replication
```

### سكريبت اختبار تلقائي | Automated Test Script

```bash
#!/bin/bash
# test-failover.sh

echo "Testing Redis Sentinel Failover..."

# Get current master
CURRENT_MASTER=$(redis-cli -p 26379 SENTINEL get-master-addr-by-name sahool-master | head -1)
echo "Current Master: $CURRENT_MASTER"

# Get master container
MASTER_CONTAINER=$(docker ps --filter "label=com.sahool.role=master" --format "{{.Names}}")
echo "Master Container: $MASTER_CONTAINER"

# Stop master
echo "Stopping master..."
docker stop $MASTER_CONTAINER

# Wait for failover
echo "Waiting for failover..."
sleep 10

# Get new master
NEW_MASTER=$(redis-cli -p 26379 SENTINEL get-master-addr-by-name sahool-master | head -1)
echo "New Master: $NEW_MASTER"

# Verify change
if [ "$CURRENT_MASTER" != "$NEW_MASTER" ]; then
    echo "✓ Failover successful!"
else
    echo "✗ Failover failed!"
    exit 1
fi

# Restart old master
echo "Restarting old master..."
docker start $MASTER_CONTAINER

echo "✓ Test completed!"
```

---

## المراقبة والصيانة | Monitoring & Maintenance

### أوامر مفيدة | Useful Commands

```bash
# الحصول على معلومات Sentinel
redis-cli -p 26379 INFO sentinel

# قائمة جميع Masters المراقبة
redis-cli -p 26379 SENTINEL masters

# معلومات Master محدد
redis-cli -p 26379 SENTINEL master sahool-master

# قائمة Replicas
redis-cli -p 26379 SENTINEL slaves sahool-master

# قائمة Sentinels الأخرى
redis-cli -p 26379 SENTINEL sentinels sahool-master

# فحص صحة Master
redis-cli -p 26379 SENTINEL ckquorum sahool-master

# إعادة تعيين Master يدوياً (استخدم بحذر!)
redis-cli -p 26379 SENTINEL failover sahool-master
```

### مراقبة الأداء | Performance Monitoring

```bash
# استخدام الذاكرة
redis-cli -p 6379 -a $REDIS_PASSWORD INFO memory

# إحصائيات الأوامر
redis-cli -p 6379 -a $REDIS_PASSWORD INFO stats

# عدد الاتصالات
redis-cli -p 6379 -a $REDIS_PASSWORD INFO clients

# حالة Replication
redis-cli -p 6379 -a $REDIS_PASSWORD INFO replication

# معلومات CPU
redis-cli -p 6379 -a $REDIS_PASSWORD INFO cpu

# مراقبة في الوقت الفعلي
redis-cli -p 6379 -a $REDIS_PASSWORD --stat

# مراقبة الأوامر
redis-cli -p 6379 -a $REDIS_PASSWORD MONITOR
```

### Prometheus Metrics

يتوفر Redis Exporter على المنفذ `9121` لتصدير المقاييس إلى Prometheus:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: "redis"
    static_configs:
      - targets: ["localhost:9121"]
```

---

## استكشاف الأخطاء | Troubleshooting

### المشكلة: لا يمكن الاتصال بـ Redis

```bash
# التحقق من حالة Containers
docker-compose -f docker-compose.redis-ha.yml ps

# فحص السجلات
docker-compose -f docker-compose.redis-ha.yml logs redis-master
docker-compose -f docker-compose.redis-ha.yml logs redis-sentinel-1

# التحقق من المنافذ
netstat -tlnp | grep -E "6379|26379"

# اختبار الاتصال
telnet localhost 6379
```

### المشكلة: Failover لا يعمل

```bash
# التحقق من Quorum
redis-cli -p 26379 SENTINEL master sahool-master | grep quorum
# يجب أن يكون 2

# التحقق من عدد Sentinels
redis-cli -p 26379 SENTINEL sentinels sahool-master | grep -c "port"
# يجب أن يكون 2 على الأقل (بالإضافة للحالي = 3)

# فحص Down-After-Milliseconds
redis-cli -p 26379 SENTINEL master sahool-master | grep down-after
# يجب أن يكون 5000
```

### المشكلة: Replication متأخرة

```bash
# التحقق من Replication Lag
redis-cli -p 6379 -a $REDIS_PASSWORD INFO replication | grep lag

# إعادة مزامنة Replica
redis-cli -p 6380 -a $REDIS_PASSWORD REPLICAOF redis-master 6379

# التحقق من Replication Offset
redis-cli -p 6379 -a $REDIS_PASSWORD INFO replication | grep offset
redis-cli -p 6380 -a $REDIS_PASSWORD INFO replication | grep offset
```

### المشكلة: استهلاك ذاكرة مرتفع

```bash
# فحص الذاكرة
redis-cli -p 6379 -a $REDIS_PASSWORD INFO memory

# تنظيف البيانات منتهية الصلاحية
redis-cli -p 6379 -a $REDIS_PASSWORD --scan --pattern "*" | xargs redis-cli -a $REDIS_PASSWORD DEL

# تعيين سياسة Eviction
redis-cli -p 6379 -a $REDIS_PASSWORD CONFIG SET maxmemory-policy allkeys-lru
```

---

## أفضل الممارسات | Best Practices

### 1. الأمان | Security

```bash
# استخدام كلمة مرور قوية
REDIS_PASSWORD=$(openssl rand -base64 32)

# تقييد الوصول للمنافذ
# في docker-compose.yml:
ports:
  - "127.0.0.1:6379:6379"  # ✓ localhost فقط
  # - "6379:6379"          # ✗ متاح للجميع
```

### 2. الأداء | Performance

```python
# استخدام Pipeline للعمليات المتعددة
with redis.pipeline() as pipe:
    for i in range(1000):
        pipe.set(f"key:{i}", f"value:{i}")
    pipe.execute()

# استخدام Slave للقراءة
value = redis.get("key", use_slave=True)

# تعيين TTL للبيانات المؤقتة
redis.set("session:123", "data", ex=3600)
```

### 3. التوافرية | Availability

```python
# استخدام Circuit Breaker
try:
    redis.set("key", "value")
except Exception as e:
    # التعامل مع الخطأ
    logger.error(f"Redis error: {e}")
    # استخدام Cache بديل أو Database

# فحص الصحة الدوري
health = redis.health_check()
if health["status"] != "healthy":
    alert_team(health)
```

### 4. المراقبة | Monitoring

```python
# إضافة Logging
import logging

logging.basicConfig(level=logging.INFO)

# مراقبة الأداء
from shared.cache import get_redis_client
import time

redis = get_redis_client()

start = time.time()
redis.set("test", "value")
duration = time.time() - start

if duration > 0.1:  # 100ms
    logger.warning(f"Slow Redis operation: {duration}s")
```

---

## الهندسة المعمارية | Architecture

### Sentinel Quorum

```
Quorum = 2 (من أصل 3 Sentinels)

السيناريو 1: Master يعمل
┌─────────┐  ┌─────────┐  ┌─────────┐
│Sentinel1│  │Sentinel2│  │Sentinel3│
│   ✓     │  │   ✓     │  │   ✓     │
└────┬────┘  └────┬────┘  └────┬────┘
     └────────────┴────────────┘
              │
         ┌────▼────┐
         │ Master  │ ✓ عامل
         └─────────┘

السيناريو 2: Master معطل - Failover
┌─────────┐  ┌─────────┐  ┌─────────┐
│Sentinel1│  │Sentinel2│  │Sentinel3│
│   ✓     │  │   ✓     │  │   ✓     │
└────┬────┘  └────┬────┘  └────┬────┘
     └────────────┴────────────┘
              │
         ┌────▼────┐
         │ Master  │ ✗ معطل
         └─────────┘
              │
         [Quorum Reached: 2/3]
              │
              ▼
         ┌─────────┐
         │Replica 1│ → ترقية إلى Master
         └─────────┘
```

### Data Flow

```
┌──────────┐
│  Client  │
└────┬─────┘
     │
     │ Write Operations
     ▼
┌─────────────┐
│   Master    │
└──────┬──────┘
       │
       │ Async Replication
       ├───────────────┐
       ▼               ▼
┌──────────┐    ┌──────────┐
│Replica 1 │    │Replica 2 │
└────┬─────┘    └────┬─────┘
     │               │
     │ Read Operations
     ▼               ▼
┌──────────┐    ┌──────────┐
│  Client  │    │  Client  │
└──────────┘    └──────────┘
```

---

## أمثلة متقدمة | Advanced Examples

### مثال 1: Cache Decorator (Python)

```python
from functools import wraps
from shared.cache import get_redis_client
import json


def cache_result(key_prefix: str, ttl: int = 3600):
    """Cache function results in Redis"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            redis = get_redis_client()

            # إنشاء مفتاح فريد
            cache_key = f"{key_prefix}:{args}:{kwargs}"

            # محاولة القراءة من Cache
            cached = redis.get(cache_key, use_slave=True)
            if cached:
                return json.loads(cached)

            # تنفيذ الدالة
            result = func(*args, **kwargs)

            # حفظ في Cache
            redis.set(cache_key, json.dumps(result), ex=ttl)

            return result

        return wrapper

    return decorator


# الاستخدام
@cache_result("user:profile", ttl=3600)
def get_user_profile(user_id: int):
    # استعلام من Database (بطيء)
    return db.query(f"SELECT * FROM users WHERE id = {user_id}")
```

### مثال 2: Rate Limiting

```python
from shared.cache import get_redis_client
import time


class RateLimiter:
    def __init__(self, max_requests: int = 100, window: int = 60):
        self.redis = get_redis_client()
        self.max_requests = max_requests
        self.window = window

    def is_allowed(self, user_id: str) -> bool:
        """Check if user is allowed to make request"""
        key = f"rate_limit:{user_id}"
        current = int(time.time())

        # استخدام Sorted Set لتتبع الطلبات
        with self.redis.pipeline() as pipe:
            # حذف الطلبات القديمة
            pipe.zremrangebyscore(key, 0, current - self.window)
            # إضافة الطلب الحالي
            pipe.zadd(key, {current: current})
            # عد الطلبات
            pipe.zcard(key)
            # تعيين TTL
            pipe.expire(key, self.window)
            results = pipe.execute()

        request_count = results[2]
        return request_count <= self.max_requests


# الاستخدام
limiter = RateLimiter(max_requests=100, window=60)

if limiter.is_allowed("user:1000"):
    # معالجة الطلب
    process_request()
else:
    # رفض الطلب
    return "Rate limit exceeded", 429
```

### مثال 3: Distributed Lock

```python
from shared.cache import get_redis_client
import time
import uuid


class DistributedLock:
    def __init__(self, lock_name: str, timeout: int = 10):
        self.redis = get_redis_client()
        self.lock_name = f"lock:{lock_name}"
        self.timeout = timeout
        self.identifier = str(uuid.uuid4())

    def acquire(self) -> bool:
        """Acquire distributed lock"""
        end_time = time.time() + self.timeout

        while time.time() < end_time:
            # محاولة الحصول على القفل
            if self.redis.set(self.lock_name, self.identifier, nx=True, ex=self.timeout):
                return True

            # انتظار قصير قبل المحاولة مرة أخرى
            time.sleep(0.001)

        return False

    def release(self) -> bool:
        """Release distributed lock"""
        # التحقق من الملكية قبل الحذف
        value = self.redis.get(self.lock_name, use_slave=False)
        if value == self.identifier:
            self.redis.delete(self.lock_name)
            return True
        return False


# الاستخدام
lock = DistributedLock("process:export", timeout=30)

if lock.acquire():
    try:
        # تنفيذ العملية الحرجة
        process_export()
    finally:
        lock.release()
else:
    print("Could not acquire lock")
```

---

## الترقية والصيانة | Upgrade & Maintenance

### الترقية | Upgrade

```bash
# 1. نسخ احتياطي للبيانات
docker exec sahool-redis-master redis-cli -a $REDIS_PASSWORD SAVE
docker cp sahool-redis-master:/data/dump.rdb ./backup/

# 2. سحب الإصدار الجديد
docker-compose -f docker-compose.redis-ha.yml pull

# 3. ترقية واحد تلو الآخر
docker-compose -f docker-compose.redis-ha.yml up -d redis-replica-1
sleep 30
docker-compose -f docker-compose.redis-ha.yml up -d redis-replica-2
sleep 30

# 4. Failover إلى Replica
redis-cli -p 26379 SENTINEL failover sahool-master

# 5. ترقية Master القديم
docker-compose -f docker-compose.redis-ha.yml up -d redis-master
```

### النسخ الاحتياطي | Backup

```bash
# نسخ احتياطي يدوي
./scripts/backup/backup_redis.sh

# نسخ احتياطي تلقائي (Cron)
0 2 * * * /path/to/backup_redis.sh
```

---

## المراجع | References

- [Redis Sentinel Documentation](https://redis.io/docs/management/sentinel/)
- [Redis Replication](https://redis.io/docs/management/replication/)
- [ioredis Documentation](https://github.com/redis/ioredis)
- [redis-py Documentation](https://redis-py.readthedocs.io/)

---

## الدعم | Support

للمساعدة أو الإبلاغ عن مشكلة:

- 📧 Email: support@sahool.platform
- 📝 GitHub Issues: [sahool-unified/issues](https://github.com/sahool/sahool-unified/issues)
- 📖 Documentation: [docs.sahool.platform](https://docs.sahool.platform)

---

**تم إنشاؤه بواسطة فريق منصة صحول | Created by Sahool Platform Team**

Version: 1.0.0 | Last Updated: 2024
