# الحاويات والبنية التحتية (Containers & Infrastructure)

يوثّق هذا القسم جميع حاويات Docker المستخدَمة في منصة SAHOOL، بما في ذلك ملفات `docker-compose`، وصور Docker الأساسية، وخدمات البنية التحتية المشتركة.

---

## 1. ملفات Docker Compose

تحتوي المنصة على **15 ملف `docker-compose`** موزّعة بين جذر المشروع ومجلد `docker/`. كل ملف يخدم غرضاً محدداً (تطوير، إنتاج، HA، اختبارات، إلخ).

### 1.1 الملفات في جذر المشروع

#### `docker-compose.yml` — الملف الرئيسي (197 KB)

- **الغرض**: التنسيق الأساسي لكامل المنصة (تطوير وإنتاج). يحتوي على جميع الخدمات المصغرة والبنية التحتية المتكاملة.
- **عدد الخدمات**: أكثر من **85 حاوية** (72 خدمة مصغرة + 13 خدمة بنية تحتية).
- **الخدمات الرئيسية** (مختارة):
  - **البنية التحتية**: `postgres` (PostGIS 16)، `pgbouncer`، `redis`، `vault`، `nats`، `nats-prometheus-exporter`، `mlflow`، `mqtt`، `qdrant`، `mongo`، `rocketchat`، `ollama`، `vllm-deepseek`، `etcd`، `minio`، `milvus`، `kong`
  - **خدمات الأعمال** (Node.js): `field-management-service`، `marketplace-service`، `research-core`، `disaster-assessment`، `yield-prediction`، `lai-estimation`، `crop-growth-model`، `chat-service`، `iot-service`، `user-service`، `yield-prediction-service`، `code-review-agent`
  - **خدمات Python FastAPI**: `ws-gateway`، `billing-core`، `vegetation-analysis-service`، `indicators-service`، `weather-service`، `advisory-service`، `irrigation-smart`، `crop-intelligence-service`، `virtual-sensors`، `equipment-service`، `task-service`، `notification-service`، وغيرها كثير
- **الشبكات**: `sahool-network` (bridge)
- **التخزين (Volumes)**: `postgres_data`، `nats_data`، `vault_data`، `mlflow_artifacts`، `redis_data`، `qdrant_data`، `mqtt_data`، `mqtt_logs`، `kong_logs`، `ollama_data`، `vllm_models`، `vllm_hf_cache`، `etcd_data`، `minio_data`، `milvus_data`، `mongo_data`، `rocketchat_uploads`، `terrain-dem-data`
- **Profiles**:
  - `deprecated`: تفعيل الخدمات المُلغاة (rocketchat، wechat-service)
  - `gpu`: تفعيل خدمات GPU (vllm-deepseek)
  - `etcd-auth`: تفعيل مصادقة etcd
- **التسجيل**: محرك `json-file` بحجم أقصى 50MB وتدوير 3 ملفات

#### `docker-compose-core.yml` (125 KB)

- **الغرض**: بنية تحتية أساسية مخففة للتطوير السريع، بدون خدمات مصغرة غير ضرورية.
- **الخدمات الرئيسية**: PostgreSQL، PgBouncer، Redis، NATS، Kong فقط
- **التحسينات**: PgBouncer بوضع `transaction mode` مع 250 اتصالاً كحد أقصى وحجم pool = 30

#### `docker-compose.prod.yml`

- **الغرض**: تجاوزات (overrides) خاصة بالإنتاج لتطبيق حدود الموارد وتحسينات الأداء.
- **التطبيقات**:
  - PostgreSQL: حد أقصى 2 CPU / 2 GB RAM
  - Kong: حد أقصى 1 CPU / 512 MB مع 4 عمليات عاملة و8192 اتصالاً
  - NATS: فرض TLS باستخدام `nats-secure.conf`
- **التسجيل**: 100 MB بحجم أقصى وتدوير 5 ملفات (أكثر حزماً من التطوير)
- **الأمان**: يتطلب أسرار KONG_JWT لواجهات Web/Mobile/Internal

#### `docker-compose.ha.yml` (High Availability)

- **الغرض**: النسخ المتماثل (replication) لـ PostgreSQL مع دعم الفشل التلقائي.
- **الخدمات**: `postgres` (أساسي) + `postgres-replica` مع أرشفة WAL
- **النسخ المتماثل**: مستخدم مخصص `postgres_replication_user`، ودعم الاسترداد لنقطة زمنية (PITR)
- **التخزين**: `postgres_wal_archive` لتخزين WAL و`postgres_logs` للسجلات
- **TLS**: يدعم شهادات العميل والـ CA للاتصالات الآمنة

#### `docker-compose.redis-ha.yml`

- **الغرض**: Redis عالي التوفر مع Sentinel.
- **البنية**: 1 Redis master + 2 replicas + 3 Sentinels (quorum = 2)
- **المزايا**: فشل تلقائي، دعم ACL (app/admin/kong/readonly)
- **الصورة**: `redis:7.4-alpine`

#### `docker-compose.telemetry.yml` (مجموعة OpenTelemetry)

- **الغرض**: التتبع الموزع والمراقبة لأكثر من 44 خدمة.
- **الخدمات**: Jaeger (all-in-one)، OpenTelemetry Collector، Prometheus، Grafana
- **التخزين**: Jaeger يستخدم Badger لتخزين مؤقت، و Prometheus كخلفية للمقاييس
- **الشبكات**: `sahool-network` + `telemetry-network` (شبكة معزولة)
- **حدود الموارد**: Jaeger = 2 CPU / 2 GB

#### `docker-compose.test.yml`

- **الغرض**: بيئة اختبار معزولة مع بيانات اعتماد افتراضية.
- **الخدمات**:
  - `postgres_test` (port 5433)
  - `redis_test` (port 6380)
  - `nats_test` (port 4223)
  - `qdrant_test` (port 6335)
- **الشبكة**: `sahool-test-network` (منفصلة)
- **الأمان**: بيانات اعتماد اختبار فقط (ليست للإنتاج)

#### `docker-compose.tls.yml`

- **الغرض**: طبقة تغطية (overlay) لفرض TLS على اتصالات الخدمات الداخلية.
- **تجاوزات**:
  - PostgreSQL: وضع TLS
  - PgBouncer: فرض TLS باستخدام `pgbouncer-tls.ini`
  - etcd: شهادات يدوية
- **الشهادات**: يتوقع وجودها في `./config/certs/postgres`، `./config/certs/pgbouncer`، `./config/certs/etcd`

#### `docker-compose.walg.yml` (النسخ الاحتياطي)

- **الغرض**: أرشفة WAL إلى S3/MinIO للاسترداد لنقطة زمنية.
- **الصورة المخصصة**: `sahool/postgres-walg:16-3.4`
- **الإعدادات**:
  - ضغط Brotli
  - 6 خطوات delta كحد أقصى
  - 4 عمليات رفع/تنزيل متزامنة
  - احتفاظ لمدة 7 أيام
- **الأرشفة**: بادئة S3 مع بيانات اعتماد AWS

#### `docker-compose.wsl2.yml`

- **الغرض**: إصلاحات خاصة بـ Windows Subsystem for Linux 2 (حل مشكلة انحراف الساعة).
- **الخدمات المتأثرة**: `etcd`، `milvus` (مع قدرة `SYS_TIME`)
- **تحذير**: للتطوير فقط، ليس للإنتاج

### 1.2 الملفات في مجلد `docker/`

#### `docker/docker-compose.infra.yml`

- **الغرض**: نشر مستقل لخدمات البنية التحتية (قابل للتشغيل بشكل مستقل).
- **الخدمات**: PostgreSQL، `db-migrator` (تشغيل تلقائي للهجرات)، Redis، NATS، Kong، Vault
- **الاستخدام**: يمكن استخدامه كملف رئيسي للنشر الأدنى

#### `docker/docker-compose.dlq.yml`

- **الغرض**: إدارة ومراقبة رسائل قائمة الانتظار الميتة (Dead Letter Queue).
- **الخدمة**: `dlq-service` (FastAPI على المنفذ 8190)
- **الإعدادات**: 3 محاولات إعادة كحد أقصى، حد تنبيه 100 رسالة، احتفاظ 30 يوماً

#### `docker/docker-compose.iot.yml` (ملغى)

- **الغرض**: اختبار IoT مستقل (مُلغى — الوظائف مُدمجة في الملف الرئيسي).
- **الخدمات**:
  - `mqtt-broker-test` (eclipse-mosquitto على 11883)
  - `iot-gateway-test`
- **ملاحظة**: استخدم الملف الرئيسي في الإنتاج

#### `docker/docker-compose.logging.yml`

- **الغرض**: تجميع السجلات باستخدام Loki + Promtail.
- **الخدمات**:
  - `loki` (port 3100)
  - `promtail` (شاحن السجلات)
- **نقاط التركيب**: `/var/log` و socket لـ Docker daemon لسجلات الحاويات
- **حدود الموارد**: Loki = 1 CPU / 1 GB، Promtail = 0.5 CPU / 512 MB

#### `docker/docker-compose.secrets.yml`

- **الغرض**: قالب لإدارة الأسرار (Docker Swarm/Compose Secrets).
- **الأسرار المعرفة**:
  - قاعدة البيانات (`postgres`, `replication`)
  - Redis
  - NATS
  - JWT (secret / private / public)
  - مفاتيح التشفير
  - MinIO
  - شهادات TLS
- **مواقع الملفات**: `./secrets/` و `./certs/`

---

## 2. صور Docker الأساسية (Base Images)

تقع الملفات الأساسية في `docker/`:

| الملف | الصورة الأساسية | الغرض |
|-------|----------------|--------|
| `Dockerfile.python.base` | `python:3.11-slim-bookworm` | الصورة الأساسية لكل خدمات Python FastAPI |
| `Dockerfile.node.base` | `node:20-slim` | الصورة الأساسية لكل خدمات Node.js / NestJS |
| `Dockerfile.ai-base` | Python 3.11 مع تبعيات ML | للخدمات المتعلقة بالذكاء الاصطناعي مع مرايا Aliyun + Tsinghua |
| `Dockerfile.etcd-init` | مُهيِّئ مخصص | تهيئة كتلة etcd |

### خصائص مشتركة لجميع الصور الأساسية:

- **مستخدم غير root**: `sahool` (UID 1000, GID 1000)
- **دعم إشارات النظام**: يستخدم `tini` (Node.js) لمعالجة SIGTERM
- **متغيرات Python**: `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`
- **متغيرات pip**: `PIP_NO_CACHE_DIR=1`, `PIP_DEFAULT_TIMEOUT=300`, `PIP_RETRIES=10`
- **مرايا pip** (متعددة المستويات): PyPI الرسمي → Aliyun → Tsinghua → Tencent
- **تقوية أمنية**: إزالة صلاحيات setuid، نظام ملفات للقراءة فقط حيث أمكن

### استثناء: `yolo26-vision-service`

يستخدم صورة مختلفة: `nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04` لدعم GPU وتسريع الاستدلال بـ TensorRT.

---

## 3. خدمات البنية التحتية المشتركة

توفّر هذه الخدمات الأساس التشغيلي لكامل المنصة:

### 3.1 قواعد البيانات والتخزين

| الخدمة | الصورة | المنفذ | الغرض |
|--------|---------|--------|--------|
| **postgres** | `postgis/postgis:16-3.4` | 5432 | قاعدة البيانات الرئيسية مع PostGIS للعمليات الجغرافية |
| **pgbouncer** | `edoburu/pgbouncer` | 6432 | تجميع الاتصالات (transaction mode، 250 اتصال كحد أقصى) |
| **redis** | `redis:7.4-alpine` | 6379 | التخزين المؤقت، إدارة الجلسات، rate limiting |
| **mongo** | `mongo:7` | 27017 | قاعدة بيانات NoSQL (لـ RocketChat وبعض الخدمات) |
| **minio** | `minio/minio` | 9000/9001 | تخزين كائنات متوافق مع S3 |
| **milvus** | `milvusdb/milvus` | 19530 | قاعدة بيانات متجهات للبحث الدلالي |
| **qdrant** | `qdrant/qdrant` | 6333 | قاعدة بيانات متجهات بديلة للـ RAG |

### 3.2 المراسلة والأحداث

| الخدمة | الصورة | المنفذ | الغرض |
|--------|---------|--------|--------|
| **nats** | `nats:2.10-alpine` | 4222 | ناقل الأحداث مع JetStream للاستمرارية |
| **nats-prometheus-exporter** | `natsio/prometheus-nats-exporter` | 7777 | تصدير مقاييس NATS إلى Prometheus |
| **nats-stream-init** | مخصص | - | تهيئة تدفقات JetStream عند الإقلاع |
| **mqtt** | `eclipse-mosquitto:2.0` | 1883/9001 | وسيط MQTT لأجهزة IoT |

### 3.3 بوابة API والأمان

| الخدمة | الصورة | المنفذ | الغرض |
|--------|---------|--------|--------|
| **kong** | `kong:3.x-alpine` | 8000/8001 | بوابة API مع 105 مسارات، مصادقة، rate limiting |
| **vault** | `hashicorp/vault` | 8200 | إدارة الأسرار والتشفير |
| **etcd** | `bitnami/etcd` | 2379/2380 | مخزن key-value موزع (لـ Milvus) |

### 3.4 الذكاء الاصطناعي والـ ML

| الخدمة | الصورة | المنفذ | الغرض |
|--------|---------|--------|--------|
| **ollama** | `ollama/ollama` | 11434 | استضافة LLMs محلياً (CodeLlama, Mistral, DeepSeek) |
| **ollama-model-loader** | مخصص | - | تحميل النماذج المطلوبة عند الإقلاع |
| **vllm-deepseek** | `vllm/vllm-openai` | 8270 | خادم استدلال GPU لـ DeepSeek Coder (profile: gpu) |
| **mlflow** | `ghcr.io/mlflow/mlflow` | 5000 | تتبع تجارب ML وتسجيل النماذج |

### 3.5 المراقبة والسجلات (من ملفات overlay)

| الخدمة | الصورة | المنفذ | الغرض |
|--------|---------|--------|--------|
| **prometheus** | `prom/prometheus` | 9090 | جمع المقاييس |
| **grafana** | `grafana/grafana` | 3000 | لوحات تحكم المراقبة (4 لوحات) |
| **jaeger** | `jaegertracing/all-in-one` | 16686 | التتبع الموزع (OpenTelemetry) |
| **otel-collector** | `otel/opentelemetry-collector-contrib` | 4317/4318 | جمع ونقل بيانات التتبع |
| **loki** | `grafana/loki` | 3100 | تجميع السجلات |
| **promtail** | `grafana/promtail` | - | شحن سجلات الحاويات إلى Loki |

### 3.6 التواصل والدردشة

| الخدمة | الصورة | المنفذ | الغرض |
|--------|---------|--------|--------|
| **rocketchat** | `rocket.chat` | 3000 | منصة دردشة لمجتمعات المزارعين (profile: deprecated) |

---

## 4. الشبكات والتخزين

### الشبكات المعرفة

| الشبكة | النوع | الاستخدام |
|--------|-------|------------|
| `sahool-network` | bridge | الشبكة الرئيسية لجميع الخدمات |
| `telemetry-network` | bridge | شبكة معزولة لمكونات المراقبة |
| `sahool-test-network` | bridge | بيئة الاختبار (منفصلة تماماً) |

### الأحجام المُسماة (Named Volumes)

الأحجام الرئيسية من `docker-compose.yml`:

| الحجم | المحتوى |
|-------|---------|
| `postgres_data` | بيانات PostgreSQL |
| `redis_data` | بيانات Redis |
| `nats_data` | تخزين JetStream |
| `vault_data` | أسرار Vault |
| `mlflow_artifacts` | قطع نماذج MLflow |
| `qdrant_data` | مؤشرات Qdrant |
| `milvus_data` | مؤشرات Milvus |
| `minio_data` | كائنات MinIO (S3) |
| `etcd_data` | حالة etcd |
| `mongo_data`, `mongo_configdb` | بيانات MongoDB |
| `mqtt_data`, `mqtt_logs`, `mqtt_passwd` | بيانات Mosquitto |
| `kong_logs` | سجلات Kong |
| `ollama_data` | نماذج Ollama |
| `vllm_models`, `vllm_hf_cache` | نماذج vLLM و HuggingFace cache |
| `rocketchat_uploads` | مرفقات RocketChat |
| `terrain-dem-data` | بيانات DEM للتضاريس |
| `code_review_logs` | سجلات خدمة مراجعة الكود |

---

## 5. الأوامر الشائعة (Makefile)

فيما يلي الأوامر الأكثر استخداماً لإدارة الحاويات:

### تشغيل البيئات

```bash
make dev                    # بدء البيئة الكاملة
make dev-starter            # حزمة البداية فقط
make dev-professional       # حزمة المحترفين
make dev-enterprise         # جميع خدمات المؤسسات
make infra-up               # البنية التحتية فقط (postgres، redis، nats، kong)
make dev-vision             # تشغيل خدمات الرؤية (yolo26-vision-service)
make dev-terrain            # تشغيل خدمات التضاريس
make dev-edge               # تشغيل edge-orchestrator
make dev-ai                 # تشغيل خدمات الذكاء الاصطناعي
make dev-agents             # تشغيل خدمات الوكلاء
make dev-mcp                # تشغيل خادم MCP
```

### البناء والإدارة

```bash
make build                  # بناء كل صور Docker (بالتوازي)
make build-python           # خدمات Python فقط
make build-node             # خدمات Node.js فقط
make build-ai               # صور خدمات الذكاء الاصطناعي
make up                     # بدء كل الخدمات
make down                   # إيقاف كل الخدمات
make down-volumes           # إيقاف وحذف الأحجام
make restart                # إعادة التشغيل
```

### السجلات والحالة

```bash
make logs                   # سجلات كل الخدمات
make logs-service SERVICE=field_ops   # سجلات خدمة محددة
make ps                     # قائمة الحاويات قيد التشغيل
make stats                  # إحصائيات المشروع
make status                 # حالة الخدمات وعناوينها
make health                 # فحص صحة جميع الخدمات
make shell SERVICE=name     # فتح shell داخل حاوية
```

### قاعدة البيانات

```bash
make db-migrate             # تشغيل الهجرات (Prisma)
make db-seed                # بيانات تجريبية
make db-reset               # إعادة تعيين (تحذير: يحذف البيانات)
make db-shell               # اتصال PostgreSQL
make db-backup              # نسخة احتياطية
```

### المراقبة والتنظيف

```bash
make monitoring-up          # تشغيل مجموعة Prometheus/Grafana
make monitoring-down        # إيقاف المراقبة
make monitoring-logs        # سجلات المراقبة
make clean                  # تنظيف الحاويات والأحجام
```

### تشغيل الخدمات المُلغاة (للاختبار فقط)

```bash
docker compose --profile deprecated up
docker compose --profile legacy up
```

---

## 6. أنماط الأمان والصحة

### فحوصات الصحة (Health Checks)

كل حاوية تعرّف `HEALTHCHECK` مع:
- `interval: 30s`
- `timeout: 10s`
- `retries: 3`
- `start_period: 10s-60s` (حسب الخدمة)

### نقاط النهاية القياسية للصحة

```
GET /healthz    # liveness probe
GET /readyz     # readiness probe  
GET /health     # حالة مجمّعة
GET /metrics    # مقاييس Prometheus
```

### ممارسات الأمان

- **مستخدم غير root**: جميع الحاويات تعمل باسم `sahool` (UID 1000)
- **نظام ملفات للقراءة فقط**: حيث أمكن
- **بناء متعدد المراحل**: 35+ خدمة تستخدم multi-stage builds
- **حدود الموارد**: CPU/RAM محددة في الإنتاج
- **شبكة معزولة**: الخدمات تتحدث فقط عبر `sahool-network`
- **TLS اختياري**: عبر `docker-compose.tls.yml`
- **إدارة الأسرار**: عبر Vault + Docker secrets
