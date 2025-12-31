# SAHOOL IDP - Virtual Simulation Environment
# بيئة المحاكاة الافتراضية لمنصة سهول

## نظرة عامة | Overview

بيئة محاكاة افتراضية كاملة لاختبار الحمل على نظام SAHOOL IDP باستخدام:
- **10 وكلاء افتراضيين** (Virtual Agents) يضربون النظام بالطلبات المتزامنة
- **3 نسخ من التطبيق** (Application Instances) لاختبار توزيع الحمل
- **Nginx Load Balancer** لتوزيع الطلبات
- **Redis** للجلسات الموزعة
- **PostgreSQL + PgBouncer** لتجميع اتصالات قاعدة البيانات
- **K6** لاختبار الحمل مع **InfluxDB + Grafana** للمراقبة

A complete virtual simulation environment for load testing the SAHOOL IDP system.

---

## البنية المعمارية | Architecture

```
                                    ┌─────────────────┐
                                    │   K6 Agents     │
                                    │  (10 Virtual    │
                                    │   Users)        │
                                    └────────┬────────┘
                                             │
                                             ▼
                              ┌──────────────────────────┐
                              │   Nginx Load Balancer    │
                              │   (least_conn)           │
                              │   Port: 8080             │
                              └──────────┬───────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
           ┌───────────────┐    ┌───────────────┐    ┌───────────────┐
           │  App Instance │    │  App Instance │    │  App Instance │
           │      #1       │    │      #2       │    │      #3       │
           │  172.30.0.100 │    │  172.30.0.101 │    │  172.30.0.102 │
           └───────┬───────┘    └───────┬───────┘    └───────┬───────┘
                   │                    │                    │
                   └────────────────────┼────────────────────┘
                                        │
                   ┌────────────────────┴────────────────────┐
                   │                                         │
                   ▼                                         ▼
          ┌───────────────┐                         ┌───────────────┐
          │   PgBouncer   │                         │    Redis      │
          │  Connection   │                         │   Sessions    │
          │    Pooler     │                         │   & Cache     │
          └───────┬───────┘                         └───────────────┘
                  │
                  ▼
          ┌───────────────┐
          │  PostgreSQL   │
          │  (PostGIS)    │
          │ max_conn=200  │
          └───────────────┘
```

---

## البدء السريع | Quick Start

### المتطلبات | Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM available
- 10GB+ disk space

### خطوات التشغيل | Steps

```bash
# 1. انتقل إلى مجلد المحاكاة
cd tests/load/simulation

# 2. شغّل البنية التحتية
./run-simulation.sh start

# 3. شغّل اختبار الحمل مع 10 وكلاء
./run-simulation.sh test 10

# 4. شاهد النتائج في Grafana
open http://localhost:3031

# 5. أوقف كل شيء
./run-simulation.sh stop
```

---

## الأوامر المتاحة | Available Commands

| الأمر | الوصف |
|-------|-------|
| `./run-simulation.sh start` | تشغيل البنية التحتية |
| `./run-simulation.sh start-apps` | تشغيل نسخ التطبيق |
| `./run-simulation.sh test [N]` | تشغيل المحاكاة مع N وكيل |
| `./run-simulation.sh quick [URL]` | اختبار سريع بدون بنية تحتية |
| `./run-simulation.sh status` | حالة الخدمات |
| `./run-simulation.sh logs [service]` | عرض السجلات |
| `./run-simulation.sh stop` | إيقاف الخدمات |
| `./run-simulation.sh clean` | تنظيف كامل |

---

## هيكل المجلدات | Directory Structure

```
simulation/
├── docker-compose-sim.yml     # Docker Compose configuration
├── run-simulation.sh          # Execution script
├── README.md                  # This file
├── PROBLEM_ANALYSIS_REPORT.md # Expected problems & solutions
├── config/
│   ├── nginx.conf             # Nginx load balancer config
│   ├── proxy-params.conf      # Nginx proxy parameters
│   ├── nginx-upstream.conf    # Nginx upstream config
│   └── application-ha.yml     # High availability app config
├── scripts/
│   └── agent-simulation.js    # K6 agent simulation script
├── grafana/
│   ├── dashboards/
│   │   ├── dashboards.yml     # Dashboard provisioning
│   │   └── k6-dashboard.json  # K6 metrics dashboard
│   └── datasources/
│       └── influxdb.yml       # InfluxDB datasource
├── init-scripts/              # Database init scripts
└── results/                   # Test results output
```

---

## سيناريو المحاكاة | Simulation Scenario

### مراحل الوكيل | Agent Phases

كل وكيل (Virtual User) يمر بالمراحل التالية:

1. **Phase 1: Authentication** - تسجيل الدخول
   - POST `/api/auth/login`
   - Measure: `login_duration_ms`

2. **Phase 2: Profile** - جلب الملف الشخصي
   - GET `/api/profile`
   - Measure: `profile_duration_ms`

3. **Phase 3: Session Persistence** - اختبار استمرارية الجلسة
   - 3 طلبات متتالية للتحقق من عدم فقدان الجلسة
   - Measure: `session_persistence_rate`

4. **Phase 4: Field Operations** - عمليات الحقول
   - GET `/api/fields` - قائمة الحقول
   - POST `/api/fields` - إنشاء حقل
   - Measure: `field_list_duration_ms`, `field_create_duration_ms`

5. **Phase 5: Cleanup** - التنظيف
   - DELETE `/api/fields/{id}`

### ملف التحميل | Load Profile

```
VUs (Virtual Users)
    │
 20 ├─────────────────────┐
    │                     │
 10 ├──────┐              ├──────┐
    │      │              │      │
  0 └──────┴──────────────┴──────┴────▶ Time
    0     30s    1m      1m30s   2m  2m30s

    Ramp up → Hold → Stress → Hold → Ramp down
```

---

## المقاييس المخصصة | Custom Metrics

### معدلات النجاح | Success Rates
- `login_success_rate` - معدل نجاح تسجيل الدخول
- `profile_success_rate` - معدل نجاح جلب الملف الشخصي
- `session_persistence_rate` - معدل استمرارية الجلسة
- `field_operations_success_rate` - معدل نجاح عمليات الحقول

### أوقات الاستجابة | Response Times
- `login_duration_ms` - وقت تسجيل الدخول
- `profile_duration_ms` - وقت جلب الملف الشخصي
- `field_list_duration_ms` - وقت قائمة الحقول
- `field_create_duration_ms` - وقت إنشاء حقل

### عدادات الأخطاء | Error Counters
- `connection_pool_errors` - أخطاء تجمع الاتصالات
- `session_loss_errors` - أخطاء فقدان الجلسة
- `race_condition_errors` - أخطاء التنافس
- `timeout_errors` - أخطاء المهلة

---

## معايير النجاح | Success Thresholds

| المقياس | الهدف | الحد المقبول |
|---------|-------|-------------|
| p95 Response Time | <500ms | <800ms |
| Error Rate | <1% | <5% |
| Login Success | >99% | >95% |
| Session Persistence | >95% | >90% |
| Connection Pool Errors | 0 | <10 |
| Session Loss Errors | 0 | <5 |
| Race Condition Errors | 0 | <5 |

---

## المشاكل المتوقعة | Expected Problems

راجع [PROBLEM_ANALYSIS_REPORT.md](./PROBLEM_ANALYSIS_REPORT.md) للتفاصيل الكاملة:

1. **استنفاد تجمع الاتصالات** (Connection Pool Exhaustion)
2. **فقدان الجلسات** (Session Loss)
3. **منافسة البيانات** (Race Conditions)
4. **بطء الاستجابة** (High Latency)

---

## الوصول للخدمات | Service Access

| الخدمة | العنوان | البيانات الافتراضية |
|--------|---------|-------------------|
| Nginx (Load Balancer) | http://localhost:8080 | - |
| Grafana | http://localhost:3031 | admin / admin |
| InfluxDB | http://localhost:8087 | admin / adminpassword123 |
| PostgreSQL | localhost:5433 | sahool_admin / simulation_password_123 |
| Redis | localhost:6380 | sim_redis_pass_123 |

---

## استكشاف الأخطاء | Troubleshooting

### الخدمات لا تبدأ
```bash
# تحقق من السجلات
./run-simulation.sh logs

# تحقق من حالة Docker
docker-compose -f docker-compose-sim.yml ps
```

### أخطاء الاتصال بقاعدة البيانات
```bash
# تحقق من PostgreSQL
docker exec sahool_db_sim pg_isready -U sahool_admin

# تحقق من اتصالات PgBouncer
docker exec sahool_pgbouncer_sim psql -h localhost -p 6432 -U sahool_admin -c "SHOW POOLS"
```

### أخطاء Redis
```bash
# تحقق من Redis
docker exec sahool_redis_sim redis-cli -a sim_redis_pass_123 ping

# عرض الجلسات المخزنة
docker exec sahool_redis_sim redis-cli -a sim_redis_pass_123 KEYS "sahool:session:*"
```

---

## المساهمة | Contributing

للمساهمة في تحسين هذه البيئة:

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

---

## الترخيص | License

هذا المشروع جزء من منصة SAHOOL.

---

*آخر تحديث | Last Updated: December 2025*
