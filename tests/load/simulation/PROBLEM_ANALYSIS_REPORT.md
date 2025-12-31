# تقرير تحليل المشاكل - SAHOOL IDP Load Testing
# Problem Analysis Report - SAHOOL IDP Load Testing

## نظرة عامة | Overview

هذا التقرير يوثق المشاكل المتوقعة عند تشغيل بيئة المحاكاة الافتراضية مع 10 وكلاء (مستخدمين افتراضيين) و3 نسخ من التطبيق، مع الحلول الجذرية لكل مشكلة.

This report documents expected problems when running the virtual simulation environment with 10 agents (virtual users) and 3 application instances, along with root cause solutions for each problem.

---

## المشاكل المتوقعة والحلول | Expected Problems and Solutions

### المشكلة 1: استنفاد تجمع الاتصالات
### Problem 1: Connection Pool Exhaustion

#### الأعراض | Symptoms
```
HikariPool-1 - Connection is not available, request timed out after 30000ms
Pool exhausted: Unable to acquire connection from pool
```

#### السبب الجذري | Root Cause
عندما تعمل 3 نسخ من التطبيق مع 10 وكلاء متزامنين، يحاول كل وكيل حجز اتصال بقاعدة البيانات. إذا كان `maximum-pool-size` صغيراً جداً، ستنفد الاتصالات.

When 3 application instances run with 10 concurrent agents, each agent tries to acquire a database connection. If `maximum-pool-size` is too small, connections will be exhausted.

**الحساب | Calculation:**
```
Total Required Connections = Agents × Requests per Agent × Concurrent Factor
Pool Size per Instance = (PostgreSQL max_connections - Reserved) / Instance Count

مثال | Example:
- PostgreSQL max_connections = 200
- Reserved connections = 50 (for admin, monitoring, etc.)
- Number of instances = 3
- Pool Size per Instance = (200 - 50) / 3 = 50
```

#### الحل الجذري | Root Cause Solution

**1. تهيئة PostgreSQL:**
```sql
-- في postgresql.conf أو عبر docker-compose
max_connections = 200
shared_buffers = 256MB
```

**2. تهيئة HikariCP (application-ha.yml):**
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20        # لكل نسخة
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
      leak-detection-threshold: 60000
```

**3. استخدام PgBouncer:**
```yaml
# في docker-compose
sahool-pgbouncer:
  environment:
    POOL_MODE: transaction
    MAX_DB_CONNECTIONS: 150
    DEFAULT_POOL_SIZE: 30
```

#### مقاييس المراقبة | Monitoring Metrics
- `hikaricp_connections_active`
- `hikaricp_connections_pending`
- `connection_pool_errors` (custom k6 metric)

---

### المشكلة 2: فقدان الجلسات بين النسخ
### Problem 2: Session Loss Between Instances

#### الأعراض | Symptoms
```json
{
  "error": "unauthorized",
  "message": "Session not found or expired"
}
```
المستخدم يسجل دخوله بنجاح في النسخة A، لكن الطلب التالي يذهب للنسخة B ويطلب تسجيل دخول جديد.

User logs in successfully on instance A, but the next request goes to instance B and requires new login.

#### السبب الجذري | Root Cause
الجلسات مخزنة محلياً في ذاكرة كل نسخة بدلاً من تخزين موزع (Redis).

Sessions are stored locally in each instance's memory instead of distributed storage (Redis).

#### الحل الجذري | Root Cause Solution

**1. إضافة Spring Session Redis:**
```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.session</groupId>
    <artifactId>spring-session-data-redis</artifactId>
</dependency>
```

**2. تهيئة الجلسات الموزعة:**
```yaml
spring:
  session:
    store-type: redis
    timeout: 30m
    redis:
      flush-mode: on_save
      namespace: sahool:session
  redis:
    host: sahool-redis
    port: 6379
    password: ${REDIS_PASSWORD}
```

**3. بديل: IP Hash في Nginx (Sticky Sessions):**
```nginx
upstream sahool_backend {
    ip_hash;  # يضمن ذهاب المستخدم لنفس الخادم
    server sahool-app-1:8080;
    server sahool-app-2:8080;
    server sahool-app-3:8080;
}
```

#### مقاييس المراقبة | Monitoring Metrics
- `session_loss_errors` (custom k6 metric)
- `session_persistence_rate` (custom k6 metric)
- Redis: `connected_clients`, `used_memory`

---

### المشكلة 3: منافسة البيانات (Race Conditions)
### Problem 3: Data Race Conditions

#### الأعراض | Symptoms
```
DataIntegrityViolationException: Duplicate key value violates unique constraint
org.postgresql.util.PSQLException: ERROR: duplicate key value violates unique constraint
```

#### السبب الجذري | Root Cause
10 وكلاء يحاولون إنشاء سجلات في نفس الوقت، مما يسبب:
- تكرار البيانات
- انتهاك القيود الفريدة
- بيانات غير متسقة

10 agents trying to create records simultaneously, causing:
- Data duplication
- Unique constraint violations
- Inconsistent data

#### الحل الجذري | Root Cause Solution

**1. قيود فريدة في قاعدة البيانات:**
```sql
-- إنشاء فهارس فريدة
CREATE UNIQUE INDEX CONCURRENTLY idx_fields_tenant_name
ON fields (tenant_id, name);

CREATE UNIQUE INDEX CONCURRENTLY idx_users_email
ON users (LOWER(email));
```

**2. معاملات مع مستوى عزل مناسب:**
```java
@Transactional(isolation = Isolation.SERIALIZABLE)
public Field createField(FieldDTO dto) {
    // Check existence first
    if (fieldRepository.existsByTenantAndName(dto.getTenantId(), dto.getName())) {
        throw new DuplicateFieldException();
    }
    return fieldRepository.save(dto.toEntity());
}
```

**3. قفل متفائل (Optimistic Locking):**
```java
@Entity
public class Field {
    @Version
    private Long version;
    // ...
}
```

**4. التعامل مع أخطاء التكرار:**
```java
try {
    fieldRepository.save(field);
} catch (DataIntegrityViolationException e) {
    if (isDuplicateKeyException(e)) {
        return fieldRepository.findByTenantAndName(tenantId, name);
    }
    throw e;
}
```

#### مقاييس المراقبة | Monitoring Metrics
- `race_condition_errors` (custom k6 metric)
- PostgreSQL: `deadlocks`, `conflicts`

---

### المشكلة 4: بطء وقت الاستجابة
### Problem 4: High Latency / Slow Response Time

#### الأعراض | Symptoms
```
WARN: TTFB (Time To First Byte) exceeded threshold: 2500ms > 500ms
p95 response time: 1.5s (threshold: 500ms)
```

#### السبب الجذري | Root Cause
1. **N+1 Query Problem:** استعلامات متعددة لجلب البيانات المرتبطة
2. **عدم وجود تخزين مؤقت:** جلب نفس البيانات مراراً
3. **استعلامات غير محسنة:** عدم استخدام الفهارس

#### الحل الجذري | Root Cause Solution

**1. حل مشكلة N+1 Query:**
```java
// استخدام EntityGraph
@EntityGraph(attributePaths = {"operations", "weather"})
Optional<Field> findByIdWithOperations(UUID id);

// أو JOIN FETCH
@Query("SELECT f FROM Field f " +
       "LEFT JOIN FETCH f.operations " +
       "WHERE f.id = :id")
Optional<Field> findByIdWithData(@Param("id") UUID id);
```

**2. التخزين المؤقت باستخدام Redis:**
```java
@Cacheable(value = "fields", key = "#id")
public Field getField(UUID id) {
    return fieldRepository.findById(id).orElseThrow();
}

@CacheEvict(value = "fields", key = "#field.id")
public Field updateField(Field field) {
    return fieldRepository.save(field);
}
```

**3. تهيئة التخزين المؤقت:**
```yaml
spring:
  cache:
    type: redis
    redis:
      time-to-live: 3600000  # 1 hour
```

**4. تحسين الاستعلامات:**
```sql
-- إنشاء فهارس مناسبة
CREATE INDEX CONCURRENTLY idx_fields_tenant
ON fields (tenant_id);

CREATE INDEX CONCURRENTLY idx_operations_field_date
ON operations (field_id, scheduled_date DESC);

-- EXPLAIN ANALYZE للاستعلامات البطيئة
EXPLAIN ANALYZE SELECT * FROM fields WHERE tenant_id = $1;
```

#### مقاييس المراقبة | Monitoring Metrics
- `http_req_duration` (p95, p99)
- `profile_duration_ms` (custom k6 metric)
- `field_list_duration_ms` (custom k6 metric)

---

## ملخص التوصيات | Summary of Recommendations

### البنية التحتية | Infrastructure

| المكون | التوصية | القيمة |
|--------|---------|--------|
| PostgreSQL | max_connections | 200 |
| PgBouncer | pool_mode | transaction |
| PgBouncer | max_db_connections | 150 |
| Redis | maxmemory | 512mb |
| Nginx | worker_connections | 4096 |
| Nginx | upstream algorithm | least_conn |

### التطبيق | Application

| الإعداد | القيمة | الوصف |
|---------|--------|-------|
| hikari.maximum-pool-size | 20 | لكل نسخة |
| hikari.minimum-idle | 5 | الحد الأدنى للاتصالات |
| hikari.connection-timeout | 30s | مهلة الانتظار |
| server.tomcat.threads.max | 200 | خيوط المعالجة |
| session.store-type | redis | جلسات موزعة |

### الأداء | Performance Targets

| المقياس | الهدف | الحد الأقصى المقبول |
|---------|-------|-------------------|
| p95 Response Time | <500ms | <800ms |
| Error Rate | <1% | <5% |
| Session Persistence | >95% | >90% |
| Connection Pool Errors | 0 | <10 |

---

## أوامر المراقبة | Monitoring Commands

### فحص اتصالات PostgreSQL:
```bash
docker exec sahool_db_sim psql -U sahool_admin -d sahool_sim -c \
  "SELECT count(*) as active_connections FROM pg_stat_activity WHERE state = 'active';"
```

### فحص Redis:
```bash
docker exec sahool_redis_sim redis-cli -a sim_redis_pass_123 INFO clients
docker exec sahool_redis_sim redis-cli -a sim_redis_pass_123 KEYS "sahool:session:*"
```

### فحص Nginx:
```bash
docker exec sahool_nginx_sim nginx -t
docker logs sahool_nginx_sim --tail 100
```

### فحص k6 metrics:
```bash
# أثناء التشغيل
docker logs -f sahool_k6_sim

# بعد الانتهاء
cat tests/load/simulation/results/agent-simulation-summary.json | jq
```

---

## المراجع | References

1. [HikariCP Configuration](https://github.com/brettwooldridge/HikariCP#configuration-knobs-baby)
2. [Spring Session with Redis](https://docs.spring.io/spring-session/reference/guides/boot-redis.html)
3. [PostgreSQL Connection Pooling](https://www.postgresql.org/docs/current/runtime-config-connection.html)
4. [Nginx Load Balancing](https://nginx.org/en/docs/http/load_balancing.html)
5. [k6 Load Testing](https://k6.io/docs/)

---

*آخر تحديث | Last Updated: December 2025*
*الإصدار | Version: 1.0.0*
