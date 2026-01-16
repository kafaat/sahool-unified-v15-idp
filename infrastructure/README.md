# Sahool Infrastructure

# بنية سهول التحتية

هذا الدليل يحتوي على جميع مكونات البنية التحتية الموحدة لمنصة سهول.

## Directory Structure / هيكل الدليل

```
infrastructure/
├── core/                    # المكونات الأساسية
│   ├── postgres/           # قاعدة البيانات PostgreSQL
│   │   ├── init/          # سكربتات التهيئة
│   │   └── migrations/    # ملفات الترحيل
│   ├── redis-ha/          # Redis مع High Availability
│   ├── mqtt/              # MQTT Broker (Mosquitto)
│   ├── pgbouncer/         # PostgreSQL connection pooling
│   ├── qdrant/            # Vector database للبحث الدلالي
│   └── vault/             # HashiCorp Vault لإدارة الأسرار
│
├── gateway/                # بوابة API
│   ├── kong/              # Kong Gateway الرئيسي
│   ├── kong-ha/           # إعداد Kong للتوافر العالي
│   └── kong-legacy/       # الإعدادات القديمة (للمرجعية)
│
└── monitoring/            # المراقبة والتنبيهات
    ├── prometheus/        # جمع المقاييس
    ├── alertmanager/      # إدارة التنبيهات
    └── grafana/           # لوحات المراقبة
```

## Quick Start / البدء السريع

### تشغيل البنية التحتية الكاملة

```bash
cd docker
docker-compose -f docker-compose.infra.yml up -d
```

### تشغيل المراقبة

```bash
cd infrastructure/monitoring
./start-monitoring.sh
```

### تشغيل Kong Gateway

```bash
cd infrastructure/gateway/kong
make start
```

## Components / المكونات

### Core Components / المكونات الأساسية

| Component      | Port  | Description              |
| -------------- | ----- | ------------------------ |
| PostgreSQL     | 5432  | قاعدة البيانات الرئيسية  |
| Redis Sentinel | 26379 | التخزين المؤقت والجلسات  |
| MQTT           | 1883  | بروتوكول IoT             |
| PgBouncer      | 6432  | تجميع اتصالات PostgreSQL |
| Qdrant         | 6333  | قاعدة البيانات المتجهية  |
| Vault          | 8200  | إدارة الأسرار            |

### Gateway / البوابة

| Component  | Port | Description      |
| ---------- | ---- | ---------------- |
| Kong Admin | 8001 | واجهة إدارة Kong |
| Kong Proxy | 8000 | بروكسي API       |
| Kong HTTPS | 8443 | بروكسي API آمن   |

### Monitoring / المراقبة

| Component    | Port | Description     |
| ------------ | ---- | --------------- |
| Prometheus   | 9090 | جمع المقاييس    |
| Alertmanager | 9093 | إدارة التنبيهات |
| Grafana      | 3001 | لوحات المراقبة  |

## Migration from infra/ / الترحيل من infra/

تم نقل جميع المكونات من `/infra` إلى هذا الدليل:

- `infra/postgres` → `infrastructure/core/postgres`
- `infra/redis-ha` → `infrastructure/core/redis-ha`
- `infra/mqtt` → `infrastructure/core/mqtt`
- `infra/kong` → `infrastructure/gateway/kong-legacy`
- `infra/kong-ha` → `infrastructure/gateway/kong-ha`

## Documentation / التوثيق

- [Kong Setup Guide](gateway/kong/README.md)
- [Redis HA Guide](core/redis-ha/README.md)
- [Monitoring Guide](monitoring/README.md)
