# SAHOOL IDP - Load Testing Simulation Environment
# بيئة محاكاة اختبار الحمل لمنصة سهول

[![Load Test Validation](https://github.com/kafaat/sahool-unified-v15-idp/actions/workflows/load-test-validation.yml/badge.svg)](https://github.com/kafaat/sahool-unified-v15-idp/actions/workflows/load-test-validation.yml)

## نظرة عامة | Overview

بيئة محاكاة افتراضية كاملة لاختبار الحمل على نظام SAHOOL IDP مع دعم:

### الإصدار الأساسي (Standard)
- **10-20 وكيل افتراضي** (Virtual Agents)
- **3 نسخ من التطبيق** (Application Instances)
- **Nginx Load Balancer** لتوزيع الطلبات
- **Redis** للجلسات الموزعة
- **PostgreSQL + PgBouncer** لتجميع اتصالات قاعدة البيانات
- **K6** لاختبار الحمل مع **InfluxDB + Grafana** للمراقبة

### الإصدار المتقدم (Advanced) 🆕
- **15-100+ وكيل افتراضي**
- **5 نسخ من التطبيق** (High Availability)
- **Prometheus + Alertmanager** للتنبيهات
- **25+ قاعدة تنبيه** مخصصة
- **اختبار هندسة الفوضى** (Chaos Engineering)
- **4 أنواع اختبارات**: Standard, Stress, Spike, Chaos

---

## البنية المعمارية | Architecture

```
                                    ┌─────────────────────┐
                                    │    K6 Load Tester   │
                                    │  (15-100+ Agents)   │
                                    └──────────┬──────────┘
                                               │
                                               ▼
                                ┌────────────────────────────┐
                                │   Nginx Load Balancer      │
                                │   (least_conn algorithm)   │
                                └────────────┬───────────────┘
                                             │
           ┌──────────┬──────────┬──────────┼──────────┬──────────┐
           │          │          │          │          │          │
           ▼          ▼          ▼          ▼          ▼          ▼
      ┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐
      │ App #1  ││ App #2  ││ App #3  ││ App #4  ││ App #5  │
      └────┬────┘└────┬────┘└────┬────┘└────┬────┘└────┬────┘
           │          │          │          │          │
           └──────────┴──────────┼──────────┴──────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
       ┌───────────┐      ┌───────────┐      ┌───────────┐
       │ PgBouncer │      │   Redis   │      │Prometheus │
       │  (Pool)   │      │  (Cache)  │      │ (Metrics) │
       └─────┬─────┘      └───────────┘      └─────┬─────┘
             │                                     │
             ▼                                     ▼
       ┌───────────┐                        ┌───────────┐
       │PostgreSQL │                        │Alertmgr   │
       └───────────┘                        └───────────┘
```

---

## البدء السريع | Quick Start

### المتطلبات | Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ RAM (للإصدار المتقدم)
- 15GB+ disk space

### Linux / Mac

```bash
# 1. انتقل إلى مجلد المحاكاة
cd tests/load/simulation

# 2. تحقق من جاهزية البيئة
./verify-simulation.sh

# === الإصدار الأساسي (3 نسخ، 10-20 وكيل) ===
./run-simulation.sh start
./run-simulation.sh test 10

# === الإصدار المتقدم (5 نسخ، 15-100+ وكيل) ===
./run-advanced.sh start
./run-advanced.sh stress 50    # اختبار ضغط
./run-advanced.sh chaos high   # اختبار فوضى

# 3. شاهد النتائج
open http://localhost:3031     # Grafana (Basic)
open http://localhost:3032     # Grafana (Advanced)
open http://localhost:9091     # Prometheus
open http://localhost:9094     # Alertmanager

# 4. إيقاف
./run-simulation.sh stop
./run-advanced.sh stop
```

### Windows (PowerShell)

```powershell
# 1. انتقل إلى مجلد المحاكاة
cd tests\load\simulation

# 2. تحقق من جاهزية البيئة
.\verify-simulation.ps1

# === الإصدار الأساسي ===
.\run-simulation.ps1 -Command Start
.\run-simulation.ps1 -Command Test -AgentCount 10

# === الإصدار المتقدم ===
.\run-advanced.ps1 -Command start
.\run-advanced.ps1 -Command stress -AgentCount 50
.\run-advanced.ps1 -Command chaos -ChaosLevel high

# 3. إيقاف
.\run-simulation.ps1 -Command Stop
.\run-advanced.ps1 -Command stop
```

---

## أنواع الاختبارات | Test Types

| النوع | الوكلاء | الوصف | الأمر |
|-------|--------|-------|-------|
| **Standard** | 20 | اختبار أساسي متوازن | `./run-advanced.sh standard` |
| **Stress** | 20→100 | زيادة تدريجية للضغط | `./run-advanced.sh stress 50` |
| **Spike** | 20→200 | ارتفاع مفاجئ في الحمل | `./run-advanced.sh spike` |
| **Chaos** | 30+ | حقن أخطاء عشوائية | `./run-advanced.sh chaos high` |

### مستويات Chaos Testing

| المستوى | نسبة الفشل | الوصف |
|---------|-----------|-------|
| `low` | 5% | اختبار خفيف |
| `medium` | 15% | اختبار متوسط |
| `high` | 30% | اختبار شديد |
| `extreme` | 50% | اختبار قاسي |

---

## الأوامر المتاحة | Available Commands

### الإصدار الأساسي (run-simulation)

| الأمر | الوصف |
|-------|-------|
| `start` | تشغيل البنية التحتية (3 نسخ) |
| `test [N]` | تشغيل المحاكاة مع N وكيل |
| `quick [URL]` | اختبار سريع بدون بنية تحتية |
| `status` | حالة الخدمات |
| `logs [service]` | عرض السجلات |
| `stop` | إيقاف الخدمات |
| `clean` | تنظيف كامل |

### الإصدار المتقدم (run-advanced)

| الأمر | الوصف |
|-------|-------|
| `start` | تشغيل البنية التحتية (5 نسخ + مراقبة) |
| `standard` | اختبار قياسي (20 وكيل) |
| `stress [N]` | اختبار ضغط (N وكيل أساسي) |
| `spike` | اختبار ارتفاع مفاجئ |
| `chaos [level]` | اختبار فوضى |
| `all` | تشغيل جميع الاختبارات |
| `status` | حالة الخدمات |
| `stop` | إيقاف الخدمات |
| `clean` | تنظيف كامل |

---

## هيكل المجلدات | Directory Structure

```
simulation/
├── docker-compose-sim.yml        # Basic: 3 instances
├── docker-compose-advanced.yml   # Advanced: 5 instances + monitoring
├── run-simulation.sh             # Basic runner (Linux)
├── run-simulation.ps1            # Basic runner (Windows)
├── run-advanced.sh               # Advanced runner (Linux)
├── run-advanced.ps1              # Advanced runner (Windows)
├── verify-simulation.sh          # Verification (Linux)
├── verify-simulation.ps1         # Verification (Windows)
├── quick-test.sh                 # Quick validation (CI/CD)
├── config/
│   ├── nginx.conf                # Basic LB config
│   ├── nginx-advanced.conf       # Advanced LB config (5 instances)
│   └── proxy-params.conf         # Proxy parameters
├── scripts/
│   ├── agent-simulation.js       # Basic K6 script
│   ├── advanced-scenarios.js     # Advanced multi-scenario K6
│   └── chaos-testing.js          # Chaos engineering K6
├── monitoring/
│   ├── prometheus.yml            # Prometheus config
│   ├── alertmanager.yml          # Alert routing
│   └── alert-rules.yml           # 25+ alert rules
├── grafana/
│   ├── dashboards/
│   │   ├── k6-dashboard.json     # Basic dashboard
│   │   └── advanced-dashboard.json # Advanced dashboard
│   └── datasources/
│       └── influxdb.yml          # InfluxDB datasource
├── init-scripts/                 # Database init scripts
└── results/                      # Test results output
```

---

## سيناريوهات الاختبار | Test Scenarios

### السيناريو الأساسي (Basic)

```
Agent Flow:
  1. Login → 2. Profile → 3. Session Check → 4. Field Ops → 5. Cleanup
```

### السيناريوهات المتقدمة (Advanced)

| السيناريو | النسبة | العمليات |
|-----------|--------|----------|
| **Auth Flow** | 20% | Login, Session persistence |
| **Field Operations** | 40% | List, Create, Update, Delete |
| **Weather Queries** | 25% | Current weather, Forecasts |
| **IoT Data** | 15% | Sensor readings, History |

---

## نظام التنبيهات | Alerting System

### فئات التنبيهات

| الفئة | عدد القواعد | أمثلة |
|-------|------------|-------|
| Application | 4 | HighErrorRate, ServiceDown |
| Database | 3 | HighConnections, PoolExhaustion |
| Cache | 3 | RedisDown, HighMemory |
| Load Balancer | 2 | AllBackendsDown |
| Load Test | 3 | SessionLoss, RaceConditions |
| System | 3 | HighCPU, LowDisk |

### تكوين التنبيهات

```yaml
# monitoring/alertmanager.yml
route:
  receiver: 'default-receiver'
  routes:
    - match:
        severity: critical
      receiver: 'critical-receiver'
```

---

## المقاييس | Metrics

### معدلات النجاح
- `auth_success_rate` - نجاح المصادقة
- `field_ops_success_rate` - نجاح عمليات الحقول
- `weather_success_rate` - نجاح استعلامات الطقس
- `session_persistence_rate` - استمرارية الجلسة

### عدادات الأخطاء
- `connection_pool_errors` - استنفاد الاتصالات
- `session_loss_errors` - فقدان الجلسات
- `race_condition_errors` - تعارض البيانات
- `timeout_errors` - انتهاء المهلة
- `server_errors_5xx` - أخطاء الخادم
- `client_errors_4xx` - أخطاء العميل

### Chaos Metrics
- `recovery_rate` - معدل التعافي
- `failover_success_rate` - نجاح التجاوز
- `graceful_degradation_rate` - التدهور المتحكم
- `circuit_breaker_trips` - تفعيل قاطع الدائرة

---

## معايير النجاح | Success Thresholds

| المقياس | الهدف | الحد المقبول |
|---------|-------|-------------|
| p95 Response Time | <500ms | <1000ms |
| Error Rate | <1% | <5% |
| Login Success | >99% | >95% |
| Session Persistence | >95% | >90% |
| Connection Pool Errors | 0 | <50 |
| Recovery Rate (Chaos) | >90% | >80% |

---

## الوصول للخدمات | Service Access

### الإصدار الأساسي

| الخدمة | العنوان | البيانات |
|--------|---------|----------|
| App (LB) | http://localhost:8080 | - |
| Grafana | http://localhost:3031 | admin/admin |
| InfluxDB | http://localhost:8087 | See .env.influxdb.secret |
| PostgreSQL | localhost:5433 | See .env |
| Redis | localhost:6380 | See .env |

### الإصدار المتقدم

| الخدمة | العنوان | البيانات |
|--------|---------|----------|
| App (LB) | http://localhost:8081 | - |
| Grafana | http://localhost:3032 | admin/admin |
| Prometheus | http://localhost:9091 | - |
| Alertmanager | http://localhost:9094 | - |
| InfluxDB | http://localhost:8088 | admin/advancedpassword123 |

---

## CI/CD Integration

### GitHub Actions

يتم تشغيل workflow تلقائياً عند تعديل ملفات المحاكاة:

```yaml
# .github/workflows/load-test-validation.yml
on:
  push:
    paths:
      - 'tests/load/simulation/**'
```

### الاختبارات المحلية

```bash
# اختبار سريع بدون Docker
./quick-test.sh

# التحقق الكامل
./verify-simulation.sh
```

---

## استكشاف الأخطاء | Troubleshooting

### الخدمات لا تبدأ

```bash
# تحقق من السجلات
./run-advanced.sh logs

# تحقق من الموارد
docker stats
```

### أخطاء الاتصال

```bash
# PostgreSQL
docker exec sahool_db_advanced pg_isready -U sahool_admin

# Redis
docker exec sahool_redis_advanced redis-cli ping

# Nginx
curl http://localhost:8081/nginx-health
```

### مشاكل الذاكرة

```bash
# زيادة موارد Docker
# Docker Desktop → Settings → Resources → Memory: 8GB+
```

---

## المساهمة | Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Run tests: `./quick-test.sh`
4. Commit changes
5. Submit pull request

---

## الترخيص | License

جزء من منصة SAHOOL IDP

---

*آخر تحديث | Last Updated: December 2025*
