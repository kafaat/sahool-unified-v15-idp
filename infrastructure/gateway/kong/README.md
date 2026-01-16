# Kong API Gateway Configuration for SAHOOL Platform

# تكوين بوابة Kong API لمنصة سهول الزراعية

## Overview | نظرة عامة

This directory contains the complete Kong API Gateway configuration for the SAHOOL agricultural platform, managing all 39 microservices with package-based access control and rate limiting.

يحتوي هذا الدليل على تكوين بوابة Kong API الكامل لمنصة سهول الزراعية، لإدارة جميع الخدمات المصغرة الـ 39 مع التحكم في الوصول حسب الباقات وتحديد المعدل.

## Configuration Files | ملفات التكوين

### 1. kong.yml

Main declarative Kong configuration containing:

- All 39 microservices definitions
- Routes with proper path prefixes
- JWT authentication plugin
- ACL plugin for package-based access control
- Rate limiting per package tier
- Health check endpoints
- Global plugins (CORS, logging, Prometheus)

التكوين الأساسي التصريحي لـ Kong ويحتوي على:

- تعريفات جميع الخدمات المصغرة الـ 39
- المسارات مع البادئات المناسبة
- إضافة مصادقة JWT
- إضافة ACL للتحكم في الوصول حسب الباقات
- تحديد المعدل لكل مستوى باقة
- نقاط فحص الصحة
- الإضافات العامة (CORS، التسجيل، Prometheus)

### 2. kong-packages.yml

Package-specific routes configuration:

- `/api/v1/starter/*` → Starter package services (100 req/min)
- `/api/v1/professional/*` → Professional package services (1000 req/min)
- `/api/v1/enterprise/*` → Enterprise package services (10000 req/min)
- `/api/v1/research/*` → Research package services (10000 req/min)
- `/api/v1/shared/*` → Shared services for all packages

تكوين المسارات الخاصة بالباقات:

- `/api/v1/starter/*` → خدمات الباقة الأساسية (100 طلب/دقيقة)
- `/api/v1/professional/*` → خدمات الباقة المتوسطة (1000 طلب/دقيقة)
- `/api/v1/enterprise/*` → خدمات الباقة المتقدمة (10000 طلب/دقيقة)
- `/api/v1/research/*` → خدمات البحث العلمي (10000 طلب/دقيقة)
- `/api/v1/shared/*` → الخدمات المشتركة لجميع الباقات

### 3. consumers.yml

Consumer groups and ACL configuration:

- Starter users (starter-users group)
- Professional users (professional-users group)
- Enterprise users (enterprise-users group)
- Research users (research-users group)
- Admin users (admin-users group)
- Service accounts (service-accounts group)
- Trial users (trial-users group)

تكوين مجموعات المستهلكين وACL:

- المستخدمون الأساسيون (مجموعة starter-users)
- المستخدمون المحترفون (مجموعة professional-users)
- المستخدمون المؤسسيون (مجموعة enterprise-users)
- المستخدمون البحثيون (مجموعة research-users)
- المستخدمون المسؤولون (مجموعة admin-users)
- حسابات الخدمة (مجموعة service-accounts)
- المستخدمون التجريبيون (مجموعة trial-users)

## Service Port Registry | سجل منافذ الخدمات

### Infrastructure Services | الخدمات الأساسية

```yaml
postgres: 5432
redis: 6379
nats: 4222
kong: 8000 (proxy), 8001 (admin)
```

### Starter Package Services | خدمات الباقة الأساسية

```yaml
field_core: 3000 # إدارة الحقول
weather_core: 8108 # الطقس
astronomical_calendar: 8111 # التقويم الفلكي
agro_advisor: 8105 # المستشار الزراعي
notification_service: 8110 # الإشعارات
```

### Professional Package Services | خدمات الباقة المتوسطة

```yaml
satellite_service: 8090 # الأقمار الصناعية
ndvi_engine: 8107 # محرك NDVI
crop_health_ai: 8095 # صحة المحاصيل AI
irrigation_smart: 8094 # الري الذكي
virtual_sensors: 8096 # المستشعرات الافتراضية
yield_engine: 8098 # توقع الإنتاجية
fertilizer_advisor: 8093 # مستشار التسميد
inventory_service: 8116 # إدارة المخزون
equipment_service: 8101 # خدمة المعدات
weather_advanced: 8092 # الطقس المتقدم
ndvi_processor: 8118 # معالج NDVI
```

### Enterprise Package Services | خدمات الباقة المتقدمة

```yaml
ai_advisor: 8112 # المستشار الذكي
iot_gateway: 8106 # بوابة IoT
research_core: 3015 # الأبحاث
marketplace_service: 3010 # السوق
billing_core: 8089 # الفوترة
disaster_assessment: 3020 # تقييم الكوارث
crop_growth_model: 3023 # نماذج نمو المحاصيل
lai_estimation: 3022 # تقدير LAI
yield_prediction: 3021 # توقع الإنتاجية
iot_service: 8117 # خدمة IoT
```

### Shared Services | الخدمات المشتركة

```yaml
field_ops: 8080 # عمليات الحقول
ws_gateway: 8081 # بوابة WebSocket
indicators_service: 8091 # المؤشرات
community_chat: 8097 # محادثة المجتمع
field_chat: 8099 # محادثة الحقل
task_service: 8103 # المهام
provider_config: 8104 # تكوين المزودين
admin_dashboard: 3001 # لوحة التحكم
alert_service: 8113 # التنبيهات
chat_service: 8114 # المحادثة
field_service: 8115 # خدمة الحقول
```

## Rate Limiting Tiers | مستويات تحديد المعدل

| Package      | Requests/Min | Requests/Hour | Requests/Day |
| ------------ | ------------ | ------------- | ------------ |
| Trial        | 50           | 2,000         | 30,000       |
| Starter      | 100          | 5,000         | 100,000      |
| Professional | 1,000        | 50,000        | 1,000,000    |
| Enterprise   | 10,000       | 500,000       | 10,000,000   |
| Research     | 10,000       | 500,000       | 10,000,000   |
| Admin        | 50,000       | 2,000,000     | Unlimited    |

## Setup Instructions | تعليمات الإعداد

### 1. Environment Variables | المتغيرات البيئية

Create a `.env` file with the following variables:

```bash
# JWT Secrets
STARTER_JWT_SECRET=your-starter-jwt-secret-here
PROFESSIONAL_JWT_SECRET=your-professional-jwt-secret-here
ENTERPRISE_JWT_SECRET=your-enterprise-jwt-secret-here
RESEARCH_JWT_SECRET=your-research-jwt-secret-here
ADMIN_JWT_SECRET=your-admin-jwt-secret-here
SERVICE_JWT_SECRET=your-service-jwt-secret-here
TRIAL_JWT_SECRET=your-trial-jwt-secret-here

# Kong Database
KONG_PG_HOST=postgres
KONG_PG_PORT=5432
KONG_PG_DATABASE=kong
KONG_PG_USER=kong
KONG_PG_PASSWORD=your-postgres-password

# Kong Configuration
KONG_PROXY_ACCESS_LOG=/dev/stdout
KONG_ADMIN_ACCESS_LOG=/dev/stdout
KONG_PROXY_ERROR_LOG=/dev/stderr
KONG_ADMIN_ERROR_LOG=/dev/stderr
```

### 2. Deploy Kong with Docker Compose | نشر Kong باستخدام Docker Compose

```bash
# Start Kong and PostgreSQL
docker-compose up -d

# Wait for PostgreSQL to be ready
sleep 10

# Run Kong migrations
docker-compose exec kong kong migrations bootstrap

# Apply declarative configuration
docker-compose exec kong kong config db_import /etc/kong/kong.yml

# Verify Kong is running
curl http://localhost:8000/health
```

### 3. Apply Configurations | تطبيق التكوينات

Using Kong's declarative configuration:

```bash
# Apply main configuration
curl -i -X POST http://localhost:8001/config \
  --data config=@kong.yml

# Apply package-based routes
curl -i -X POST http://localhost:8001/config \
  --data config=@kong-packages.yml

# Apply consumers
curl -i -X POST http://localhost:8001/config \
  --data config=@consumers.yml
```

Using deck (recommended):

```bash
# Install deck
brew tap kong/deck
brew install deck

# Sync configuration
deck sync -s kong.yml
deck sync -s kong-packages.yml
deck sync -s consumers.yml

# Validate configuration
deck validate -s kong.yml
```

## Testing | الاختبار

### 1. Health Check | فحص الصحة

```bash
curl http://localhost:8000/health
# Expected: {"message": "SAHOOL Platform is healthy"}
```

### 2. Test Starter Package Route | اختبار مسار الباقة الأساسية

```bash
# Generate JWT token for starter user
TOKEN=$(jwt encode --secret "$STARTER_JWT_SECRET" --alg HS256 '{"iss":"starter-jwt-key","exp":'$(date -d '+1 hour' +%s)'}')

# Test field core service
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/starter/fields

# Test weather service
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/starter/weather
```

### 3. Test Professional Package Route | اختبار مسار الباقة المتوسطة

```bash
# Generate JWT token for professional user
TOKEN=$(jwt encode --secret "$PROFESSIONAL_JWT_SECRET" --alg HS256 '{"iss":"professional-jwt-key","exp":'$(date -d '+1 hour' +%s)'}')

# Test satellite service
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/professional/satellite

# Test NDVI service
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/professional/ndvi
```

### 4. Test Enterprise Package Route | اختبار مسار الباقة المتقدمة

```bash
# Generate JWT token for enterprise user
TOKEN=$(jwt encode --secret "$ENTERPRISE_JWT_SECRET" --alg HS256 '{"iss":"enterprise-jwt-key","exp":'$(date -d '+1 hour' +%s)'}')

# Test AI advisor
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/enterprise/ai-advisor

# Test IoT gateway
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/enterprise/iot
```

### 5. Test Rate Limiting | اختبار تحديد المعدل

```bash
# Test starter rate limit (100 req/min)
for i in {1..150}; do
  curl -H "Authorization: Bearer $STARTER_TOKEN" \
    http://localhost:8000/api/v1/starter/fields
done
# Expected: 429 Too Many Requests after 100 requests
```

## Monitoring | المراقبة

### Prometheus Metrics

Kong exposes Prometheus metrics on port 8001:

```bash
curl http://localhost:8001/metrics
```

### Key Metrics to Monitor | المقاييس الرئيسية للمراقبة

- `kong_http_status` - HTTP status codes distribution
- `kong_latency` - Request latency
- `kong_bandwidth` - Bandwidth usage
- `kong_nginx_http_current_connections` - Active connections
- `kong_memory_lua_shared_dict_bytes` - Memory usage

### Grafana Dashboard

Import the Kong dashboard into Grafana:

1. Go to Grafana → Dashboards → Import
2. Use dashboard ID: 7424 (Official Kong Dashboard)
3. Configure Prometheus data source

## Security Best Practices | أفضل ممارسات الأمان

### 1. JWT Secret Management | إدارة أسرار JWT

- Use strong, unique secrets for each package tier
- Rotate JWT secrets regularly (every 90 days)
- Store secrets in secure vault (e.g., HashiCorp Vault, AWS Secrets Manager)
- Never commit secrets to version control

استخدم أسرار قوية وفريدة لكل مستوى باقة
قم بتدوير أسرار JWT بانتظام (كل 90 يوم)
احفظ الأسرار في خزنة آمنة
لا تقم أبداً بإيداع الأسرار في نظام التحكم بالإصدارات

### 2. IP Whitelisting for Admin | القائمة البيضاء لـ IP للمسؤولين

Restrict admin access to specific IP ranges:

```yaml
plugins:
  - name: ip-restriction
    config:
      allow:
        - 10.0.0.0/8
        - 172.16.0.0/12
        - 192.168.0.0/16
```

### 3. HTTPS Only in Production | HTTPS فقط في الإنتاج

Force HTTPS for all routes in production:

```yaml
routes:
  - protocols:
      - https
```

### 4. Request Size Limiting | تحديد حجم الطلب

Protect against large payloads:

```yaml
plugins:
  - name: request-size-limiting
    config:
      allowed_payload_size: 10 # MB
```

## Troubleshooting | استكشاف الأخطاء

### Kong not starting | Kong لا يعمل

```bash
# Check logs
docker-compose logs kong

# Verify database connection
docker-compose exec kong kong health

# Check configuration syntax
deck validate -s kong.yml
```

### 401 Unauthorized | 401 غير مصرح

```bash
# Verify JWT token is valid
echo $TOKEN | jwt decode -

# Check consumer exists
curl http://localhost:8001/consumers/starter-user-demo

# Verify ACL group membership
curl http://localhost:8001/consumers/starter-user-demo/acls
```

### 429 Rate Limit Exceeded | 429 تجاوز حد المعدل

```bash
# Check current rate limit
curl -I http://localhost:8000/api/v1/starter/fields
# Look for X-RateLimit-Remaining header

# Wait for rate limit to reset
# Or upgrade to higher package tier
```

### 502 Bad Gateway | 502 بوابة سيئة

```bash
# Check if service is running
docker-compose ps

# Verify service connectivity
docker-compose exec kong curl http://field-core:3000/health

# Check Kong upstream status
curl http://localhost:8001/upstreams
```

## Advanced Configuration | التكوين المتقدم

### Custom Plugins | الإضافات المخصصة

Add custom Kong plugins for SAHOOL-specific needs:

```lua
-- plugins/sahool-auth/handler.lua
local SahoolAuthHandler = {
  PRIORITY = 1000,
  VERSION = "1.0.0",
}

function SahoolAuthHandler:access(conf)
  -- Custom authentication logic
  -- Verify SAHOOL-specific claims
  -- Check subscription status
end

return SahoolAuthHandler
```

### Circuit Breaker | قاطع الدائرة

Protect services from cascading failures:

```yaml
plugins:
  - name: circuit-breaker
    config:
      threshold: 10 # Number of failures before opening circuit
      window_size: 60 # Time window in seconds
      failure_rate: 0.5 # Failure rate to trigger circuit breaker
```

### Caching | التخزين المؤقت

Cache responses to reduce backend load:

```yaml
plugins:
  - name: proxy-cache
    config:
      strategy: memory
      content_type:
        - application/json
      cache_ttl: 300 # 5 minutes
      cache_control: true
```

## References | المراجع

- [Kong Documentation](https://docs.konghq.com/)
- [Kong Declarative Configuration](https://docs.konghq.com/gateway/latest/production/deployment-topologies/db-less-and-declarative-config/)
- [Kong Rate Limiting Plugin](https://docs.konghq.com/hub/kong-inc/rate-limiting/)
- [Kong JWT Plugin](https://docs.konghq.com/hub/kong-inc/jwt/)
- [Kong ACL Plugin](https://docs.konghq.com/hub/kong-inc/acl/)
- [deck Documentation](https://docs.konghq.com/deck/latest/)

## Support | الدعم

For SAHOOL platform-specific questions:

- Email: support@sahool.platform
- Documentation: https://docs.sahool.platform
- GitHub: https://github.com/sahool-platform

---

**Version:** 1.0.0
**Last Updated:** 2025-12-25
**Maintained by:** SAHOOL Platform Team
