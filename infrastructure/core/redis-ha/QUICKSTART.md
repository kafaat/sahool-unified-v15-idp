# Redis Sentinel - Quick Start Guide
# دليل البدء السريع

## التثبيت السريع | Quick Installation

### 1. إعداد البيئة | Setup Environment

```bash
# الانتقال إلى مجلد redis-ha
cd infra/redis-ha

# إنشاء ملف .env
make setup

# تحديث كلمة المرور في .env
# افتح الملف وغيّر REDIS_PASSWORD
nano .env
```

### 2. تشغيل النظام | Start System

```bash
# بدء جميع الخدمات
make start

# الانتظار حتى تصبح الخدمات جاهزة (حوالي 10 ثواني)
# أو استخدام الأمر التالي للمراقبة:
make logs
```

### 3. التحقق من التشغيل | Verify Installation

```bash
# فحص الصحة الشامل
make health

# عرض حالة الخدمات
make status

# عرض معلومات النظام
make info
```

---

## الاستخدام السريع | Quick Usage

### Python

```python
from shared.cache import get_redis_client

# الحصول على Redis Client
redis = get_redis_client()

# الكتابة
redis.set('my_key', 'my_value', ex=60)

# القراءة
value = redis.get('my_key')
print(value)  # my_value

# الحذف
redis.delete('my_key')
```

### TypeScript

```typescript
import { getRedisSentinelClient } from '@sahool/cache/redis-sentinel';

// الحصول على Redis Client
const redis = getRedisSentinelClient();

// الكتابة
await redis.set('my_key', 'my_value', { ex: 60 });

// القراءة
const value = await redis.get('my_key');
console.log(value); // my_value

// الحذف
await redis.delete('my_key');
```

---

## الأوامر المفيدة | Useful Commands

```bash
# عرض السجلات
make logs

# فحص الصحة
make health

# اختبار Failover
make test-failover

# النسخ الاحتياطي
make backup

# إعادة التشغيل
make restart

# الإيقاف
make stop

# الدخول إلى Master
make shell-master

# عرض الإحصائيات
make stats
```

---

## اختبار سريع | Quick Test

```bash
# اختبار الكتابة
docker-compose -f ../../docker-compose.redis-ha.yml exec \
  redis-master redis-cli -a $REDIS_PASSWORD SET test "Hello Sentinel"

# اختبار القراءة
docker-compose -f ../../docker-compose.redis-ha.yml exec \
  redis-master redis-cli -a $REDIS_PASSWORD GET test
```

---

## استكشاف الأخطاء السريع | Quick Troubleshooting

### المشكلة: لا يمكن الاتصال

```bash
# التحقق من حالة Containers
make status

# التحقق من السجلات
make logs

# إعادة التشغيل
make restart
```

### المشكلة: كلمة المرور خاطئة

```bash
# تحديث .env
nano .env

# إعادة التشغيل
make restart
```

---

## الأوامر المتقدمة | Advanced Commands

```bash
# عرض معلومات Master
redis-cli -p 26379 SENTINEL master sahool-master

# قائمة Replicas
redis-cli -p 26379 SENTINEL slaves sahool-master

# فرض Failover
redis-cli -p 26379 SENTINEL failover sahool-master

# مراقبة الأوامر في الوقت الفعلي
make monitor
```

---

## المزيد من المعلومات | More Information

للحصول على دليل شامل، راجع:
- [README.md](../../shared/cache/README.md) - التوثيق الكامل
- [examples.py](../../shared/cache/examples.py) - أمثلة Python
- [examples.ts](../../shared/cache/examples.ts) - أمثلة TypeScript

---

## الدعم | Support

للمساعدة:
- 📧 Email: support@sahool.platform
- 📝 GitHub Issues
- 📖 Documentation: docs.sahool.platform
