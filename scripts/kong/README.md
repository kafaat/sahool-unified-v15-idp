# Kong Service Health Verification System

# نظام التحقق من صحة خدمات Kong

## Overview | نظرة عامة

This directory contains comprehensive tools for verifying, testing, and monitoring Kong API Gateway services in the SAHOOL platform.

يحتوي هذا الدليل على أدوات شاملة للتحقق والاختبار والمراقبة لخدمات بوابة Kong API في منصة سهول.

---

## Files | الملفات

| File | Description | الوصف |
|------|-------------|-------|
| `verify-services.sh` | Bash script for health checks | سكريبت Bash للتحقق من الصحة |
| `service-connectivity-test.py` | Python connectivity tester | مختبر الاتصال بـ Python |
| `monitor-kong.py` | Continuous monitoring daemon | برنامج المراقبة المستمرة |
| `kong-services.json` | Service registry (77+ services) | سجل الخدمات (أكثر من 77 خدمة) |

---

## Quick Start | البداية السريعة

```bash
# Navigate to scripts directory
cd scripts/kong

# 1. Basic health check | فحص الصحة الأساسي
./verify-services.sh

# 2. Critical services only | الخدمات الحرجة فقط
./verify-services.sh --critical

# 3. Connectivity test | اختبار الاتصال
python service-connectivity-test.py

# 4. Start continuous monitoring | بدء المراقبة المستمرة
python monitor-kong.py
```

---

## 1. verify-services.sh

### Description | الوصف

Bash script that reads the service registry and checks health endpoints for all Kong-registered services.

سكريبت Bash يقرأ سجل الخدمات ويفحص نقاط فحص الصحة لجميع الخدمات المسجلة في Kong.

### Usage | الاستخدام

```bash
./verify-services.sh [options]
```

### Options | الخيارات

| Option | Description | الوصف |
|--------|-------------|-------|
| `-h, --help` | Show help message | عرض رسالة المساعدة |
| `-v, --verbose` | Enable verbose output | تفعيل الإخراج المفصل |
| `-c, --critical` | Check only critical services | فحص الخدمات الحرجة فقط |
| `-j, --json` | Output as JSON | الإخراج بتنسيق JSON |
| `-o, --output FILE` | Write report to file | كتابة التقرير إلى ملف |
| `--category CAT` | Filter by category | تصفية حسب الفئة |
| `--timeout SECONDS` | Request timeout | مهلة الطلب |

### Examples | أمثلة

```bash
# Check all services
./verify-services.sh

# Check AI services only
./verify-services.sh --category ai

# JSON output to file
./verify-services.sh --json --output health-report.json

# Verbose mode with critical services
./verify-services.sh --verbose --critical
```

### Output | الإخراج

```
==============================================================================
SAHOOL Kong Service Health Report | تقرير صحة خدمات Kong
==============================================================================

Timestamp: 2026-02-07T10:30:00Z
Platform Version: 16.0.0

------------------------------------------------------------------------------
Summary | ملخص
------------------------------------------------------------------------------

  Total Services Checked:   77
  Healthy:                  72 OK
  Unhealthy:                3 FAIL
  Unreachable:              2 WARN
  Skipped:                  0

  Health Percentage:        93%

==============================================================================
```

---

## 2. service-connectivity-test.py

### Description | الوصف

Python script that performs comprehensive connectivity tests including:
- Route accessibility testing
- Rate limiting verification
- CORS configuration validation
- JWT authentication flow testing

سكريبت Python يقوم بإجراء اختبارات اتصال شاملة تشمل:
- اختبار إمكانية الوصول للمسارات
- التحقق من الحد من المعدل
- التحقق من تكوين CORS
- اختبار تدفق مصادقة JWT

### Requirements | المتطلبات

```bash
pip install aiohttp  # Optional: for async mode
# أو
pip install requests  # Fallback: sync mode
```

### Usage | الاستخدام

```bash
python service-connectivity-test.py [options]
```

### Options | الخيارات

| Option | Description | الوصف |
|--------|-------------|-------|
| `--kong-url URL` | Kong gateway URL | عنوان بوابة Kong |
| `--admin-url URL` | Kong admin URL | عنوان إدارة Kong |
| `-v, --verbose` | Verbose output | الإخراج المفصل |
| `-j, --json` | JSON output | إخراج JSON |
| `-o, --output FILE` | Output file | ملف الإخراج |
| `--test TYPE` | Specific test type | نوع الاختبار المحدد |
| `--skip-deprecated` | Skip deprecated services | تخطي الخدمات القديمة |

### Test Types | أنواع الاختبارات

- `routes` - Route accessibility | إمكانية الوصول للمسارات
- `rate-limit` - Rate limiting | الحد من المعدل
- `cors` - CORS configuration | تكوين CORS
- `jwt` - JWT authentication | مصادقة JWT
- `all` - All tests (default) | جميع الاختبارات (افتراضي)

### Examples | أمثلة

```bash
# Full connectivity test
python service-connectivity-test.py

# Test only routes
python service-connectivity-test.py --test routes

# JSON output, skip deprecated
python service-connectivity-test.py --json --skip-deprecated --output connectivity-report.json

# Test against specific Kong URL
python service-connectivity-test.py --kong-url http://kong:8000
```

---

## 3. monitor-kong.py

### Description | الوصف

Continuous monitoring daemon that:
- Polls all services at configurable intervals
- Logs results to file with timestamps
- Sends alerts for failures (webhook, Slack)
- Exports Prometheus-compatible metrics

برنامج مراقبة مستمر يقوم بـ:
- استقصاء جميع الخدمات على فترات قابلة للتكوين
- تسجيل النتائج في ملف مع الطوابع الزمنية
- إرسال تنبيهات عند الفشل (webhook، Slack)
- تصدير مقاييس متوافقة مع Prometheus

### Requirements | المتطلبات

```bash
pip install aiohttp  # Optional: for async mode
```

### Usage | الاستخدام

```bash
python monitor-kong.py [options]
```

### Options | الخيارات

| Option | Description | Default | الوصف |
|--------|-------------|---------|-------|
| `--interval` | Polling interval (seconds) | 30 | فترة الاستقصاء (بالثواني) |
| `--log-file` | Log file path | kong-monitor.log | مسار ملف السجل |
| `--metrics-port` | Prometheus metrics port | 9101 | منفذ مقاييس Prometheus |
| `--kong-url` | Kong gateway URL | localhost:8000 | عنوان بوابة Kong |
| `--alert-webhook` | Alert webhook URL | - | عنوان webhook للتنبيهات |
| `--slack-webhook` | Slack webhook URL | - | عنوان Slack webhook |
| `--failure-threshold` | Failures before alert | 3 | عدد الفشل قبل التنبيه |
| `--critical-only` | Monitor critical only | false | مراقبة الحرجة فقط |

### Prometheus Metrics | مقاييس Prometheus

The monitor exposes the following metrics at `http://localhost:9101/metrics`:

يعرض المراقب المقاييس التالية على `http://localhost:9101/metrics`:

| Metric | Type | Description | الوصف |
|--------|------|-------------|-------|
| `sahool_kong_service_up` | gauge | Service health (1=up, 0=down) | صحة الخدمة |
| `sahool_kong_service_response_time_ms` | gauge | Response time in ms | وقت الاستجابة بالملي ثانية |
| `sahool_kong_service_uptime_percent` | gauge | Uptime percentage | نسبة وقت التشغيل |
| `sahool_kong_service_consecutive_failures` | gauge | Failure count | عدد حالات الفشل |
| `sahool_kong_total_services` | gauge | Total monitored services | إجمالي الخدمات المراقبة |
| `sahool_kong_healthy_services` | gauge | Healthy service count | عدد الخدمات الصحية |

### Examples | أمثلة

```bash
# Basic monitoring (30s interval)
python monitor-kong.py

# Custom interval with Slack alerts
python monitor-kong.py --interval 60 --slack-webhook https://hooks.slack.com/services/XXX

# Monitor critical services only
python monitor-kong.py --critical-only --metrics-port 9102

# Production setup
python monitor-kong.py \
  --interval 30 \
  --log-file /var/log/sahool/kong-monitor.log \
  --alert-webhook https://alerts.example.com/webhook \
  --slack-webhook https://hooks.slack.com/services/XXX
```

### Running as a Service | التشغيل كخدمة

Create a systemd service file `/etc/systemd/system/kong-monitor.service`:

```ini
[Unit]
Description=SAHOOL Kong Monitor
After=network.target

[Service]
Type=simple
User=sahool
WorkingDirectory=/opt/sahool/scripts/kong
ExecStart=/usr/bin/python3 monitor-kong.py --interval 30 --log-file /var/log/sahool/kong-monitor.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start the service
sudo systemctl enable kong-monitor
sudo systemctl start kong-monitor
```

---

## 4. kong-services.json

### Description | الوصف

JSON registry containing all 77+ Kong-registered services with:
- Service name and Arabic name
- Host, port, and health endpoint
- Expected response codes
- Service category
- Timeout configuration
- Critical flag
- Deprecation status

سجل JSON يحتوي على جميع الخدمات المسجلة في Kong (أكثر من 77 خدمة) مع:
- اسم الخدمة والاسم بالعربية
- المضيف والمنفذ ونقطة فحص الصحة
- رموز الاستجابة المتوقعة
- فئة الخدمة
- تكوين المهلة
- علامة الحرجة
- حالة الإيقاف

### Categories | الفئات

| Category | Description | الوصف |
|----------|-------------|-------|
| `core` | Essential platform services | الخدمات الأساسية للمنصة |
| `ai` | AI and ML services | خدمات الذكاء الاصطناعي |
| `analysis` | Data analysis services | خدمات تحليل البيانات |
| `bridge` | Transform analysis to actions | تحويل التحليل إلى إجراءات |
| `terrain` | Terrain analysis services | خدمات تحليل التضاريس |
| `edge` | Edge computing services | خدمات الحوسبة الطرفية |
| `iot` | IoT integration | تكامل إنترنت الأشياء |
| `communication` | Real-time communication | الاتصال في الوقت الفعلي |
| `marketplace` | Marketplace services | خدمات السوق |
| `compliance` | Regulatory compliance | الامتثال التنظيمي |

### Service Entry Format | تنسيق إدخال الخدمة

```json
{
  "name": "field-management-service",
  "name_ar": "خدمة إدارة الحقول",
  "host": "field-management-service",
  "port": 3000,
  "health_endpoint": "/healthz",
  "expected_status": 200,
  "category": "core",
  "category_ar": "الخدمات الأساسية",
  "framework": "nestjs",
  "routes": ["/api/v1/fields", "/api/v1/field", "/field"],
  "critical": true,
  "timeout_ms": 5000,
  "deprecated": false
}
```

---

## Environment Variables | متغيرات البيئة

| Variable | Description | Default | الوصف |
|----------|-------------|---------|-------|
| `KONG_GATEWAY_URL` | Kong gateway URL | http://localhost:8000 | عنوان بوابة Kong |
| `KONG_ADMIN_URL` | Kong admin URL | http://localhost:8001 | عنوان إدارة Kong |
| `ALERT_WEBHOOK_URL` | Alert webhook URL | - | عنوان webhook للتنبيهات |
| `SLACK_WEBHOOK_URL` | Slack webhook URL | - | عنوان Slack webhook |

---

## Integration with CI/CD | التكامل مع CI/CD

### GitHub Actions Example | مثال GitHub Actions

```yaml
name: Kong Health Check

on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
  workflow_dispatch:

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Kong Health Verification
        run: |
          cd scripts/kong
          ./verify-services.sh --json --output report.json

      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: kong-health-report
          path: scripts/kong/report.json
```

---

## Troubleshooting | استكشاف الأخطاء

### Common Issues | المشاكل الشائعة

1. **Services unreachable | الخدمات غير قابلة للوصول**
   - Check if Docker containers are running | تحقق من تشغيل حاويات Docker
   - Verify network connectivity | تحقق من الاتصال بالشبكة
   - Check firewall rules | تحقق من قواعد جدار الحماية

2. **Rate limit headers missing | رؤوس الحد من المعدل مفقودة**
   - Rate limiting may be disabled for health endpoints | قد يكون الحد من المعدل معطلاً لنقاط فحص الصحة
   - Check Kong plugin configuration | تحقق من تكوين إضافات Kong

3. **JWT test failures | فشل اختبار JWT**
   - JWT plugin may not be enabled on all routes | قد لا تكون إضافة JWT مفعلة على جميع المسارات
   - This is expected for public endpoints | هذا متوقع للنقاط النهائية العامة

---

## Support | الدعم

For issues and questions, please contact the SAHOOL Platform Team.

للمشاكل والأسئلة، يرجى التواصل مع فريق منصة سهول.

---

## Version History | تاريخ الإصدارات

| Version | Date | Changes | التغييرات |
|---------|------|---------|-----------|
| 16.0.0 | 2026-02-07 | Initial release | الإصدار الأول |

---

_Last Updated: 2026-02-07_
_آخر تحديث: 2026-02-07_
