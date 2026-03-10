# SAHOOL Platform Environment Variables Reference

# دليل متغيرات البيئة لمنصة سهول

**Version**: 16.0.0
**Last Updated**: January 2026

This document provides a comprehensive reference for all environment variables used across the SAHOOL Agricultural Intelligence Platform.

يقدم هذا المستند مرجعاً شاملاً لجميع متغيرات البيئة المستخدمة في منصة سهول للذكاء الزراعي.

---

## Table of Contents | جدول المحتويات

1. [Core Application Settings](#1-core-application-settings)
2. [Database Configuration](#2-database-configuration)
3. [PgBouncer Connection Pooling](#3-pgbouncer-connection-pooling)
4. [Redis Configuration](#4-redis-configuration)
5. [NATS Message Queue](#5-nats-message-queue)
6. [Authentication & JWT](#6-authentication--jwt)
7. [Kong API Gateway](#7-kong-api-gateway)
8. [AI/ML Services](#8-aiml-services)
9. [Ollama Local LLM](#9-ollama-local-llm)
10. [Monitoring & Observability](#10-monitoring--observability)
11. [External APIs](#11-external-apis)
12. [Notification Services](#12-notification-services)
13. [File Storage & CDN](#13-file-storage--cdn)
14. [Security & Secrets](#14-security--secrets)
15. [Mobile Application](#15-mobile-application)
16. [Frontend Applications](#16-frontend-applications)
17. [Service URLs](#17-service-urls)
18. [Backup & Disaster Recovery](#18-backup--disaster-recovery)
19. [Development & Debug](#19-development--debug)

---

## 1. Core Application Settings

### متغيرات التطبيق الأساسية

| Variable | Description | الوصف | Required | Default | Example | Services |
|----------|-------------|-------|----------|---------|---------|----------|
| `ENVIRONMENT` | Deployment environment | بيئة النشر | Yes | `development` | `development`, `staging`, `production` | All |
| `LOG_LEVEL` | Application log level | مستوى السجلات | No | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | All |
| `NODE_ENV` | Node.js environment | بيئة Node.js | No | `production` | `development`, `production` | Node.js services |
| `TZ` | Timezone setting | إعداد المنطقة الزمنية | No | `UTC` | `Asia/Aden`, `Asia/Riyadh` | All |
| `PORT` | Service port | منفذ الخدمة | Yes | Varies | `8080`, `3000` | All |
| `SERVICE_NAME` | Service identifier | معرف الخدمة | No | `sahool-platform` | `field-management-service` | All |

---

## 2. Database Configuration

### تكوين قاعدة البيانات

PostgreSQL 16+ with PostGIS 3.4 for geospatial data storage.

| Variable | Description | الوصف | Required | Default | Example | Services |
|----------|-------------|-------|----------|---------|---------|----------|
| `POSTGRES_USER` | PostgreSQL username | اسم مستخدم PostgreSQL | **Yes** | `sahool` | `sahool` | All |
| `POSTGRES_PASSWORD` | PostgreSQL password | كلمة مرور PostgreSQL | **Yes** | - | `secure_password_here` | All |
| `POSTGRES_DB` | Database name | اسم قاعدة البيانات | Yes | `sahool` | `sahool` | All |
| `POSTGRES_HOST` | Database host | مضيف قاعدة البيانات | No | `postgres` | `postgres`, `localhost` | All |
| `POSTGRES_PORT` | Database port | منفذ قاعدة البيانات | No | `5432` | `5432` | All |
| `POSTGRES_SSL_MODE` | SSL connection mode | وضع اتصال SSL | Yes | `require` | `require`, `verify-full` | All |
| `POSTGRES_SSL_CERT` | Client certificate path | مسار شهادة العميل | No | `/certs/client.crt` | `/certs/client.crt` | All |
| `POSTGRES_SSL_KEY` | Client key path | مسار مفتاح العميل | No | `/certs/client.key` | `/certs/client.key` | All |
| `POSTGRES_SSL_ROOT_CERT` | CA certificate path | مسار شهادة CA | No | `/certs/ca.crt` | `/certs/ca.crt` | All |
| `POSTGRES_CONTAINER` | Container name for backups | اسم الحاوية للنسخ الاحتياطي | No | `sahool-postgres` | `sahool-postgres` | Backup |

### Connection URLs | روابط الاتصال

| Variable | Description | الوصف | Required | Default | Example |
|----------|-------------|-------|----------|---------|---------|
| `DATABASE_URL` | Primary connection URL (via PgBouncer) | رابط الاتصال الرئيسي | **Yes** | - | `postgresql://sahool:pass@pgbouncer:6432/sahool?sslmode=require` |
| `DATABASE_URL_DIRECT` | Direct PostgreSQL connection (for migrations) | اتصال مباشر (للترحيل) | No | - | `postgresql://sahool:pass@postgres:5432/sahool?sslmode=require` |
| `DATABASE_URL_POOLED` | Pooled connection URL | رابط الاتصال المجمّع | No | - | Same as `DATABASE_URL` |
| `DATABASE_URL_HIGH_TRAFFIC` | High traffic services (10 connections) | خدمات الحركة العالية | No | - | Connection with `connection_limit=10` |
| `DATABASE_URL_MEDIUM_TRAFFIC` | Medium traffic services (8 connections) | خدمات الحركة المتوسطة | No | - | Connection with `connection_limit=8` |
| `DATABASE_URL_LOW_TRAFFIC` | Low traffic services (6 connections) | خدمات الحركة المنخفضة | No | - | Connection with `connection_limit=6` |
| `SQLALCHEMY_DATABASE_URL` | SQLAlchemy async connection | اتصال SQLAlchemy غير متزامن | No | - | `postgresql+asyncpg://...` |
| `PRISMA_DATABASE_URL` | Prisma ORM connection | اتصال Prisma ORM | No | - | Same as `DATABASE_URL` |

### Connection Pool Settings | إعدادات تجمع الاتصالات

| Variable | Description | الوصف | Required | Default | Example |
|----------|-------------|-------|----------|---------|---------|
| `DB_POOL_SIZE` | SQLAlchemy pool size | حجم تجمع SQLAlchemy | No | `20` | `20` |
| `DB_MAX_OVERFLOW` | Max overflow connections | الفائض الأقصى للاتصالات | No | `10` | `10` |
| `DB_POOL_TIMEOUT` | Pool timeout (seconds) | مهلة التجمع (ثانية) | No | `30` | `30` |
| `DB_POOL_RECYCLE` | Connection recycle time (seconds) | وقت إعادة تدوير الاتصال | No | `3600` | `3600` |
| `DB_POOL_PRE_PING` | Enable pre-ping | تمكين الفحص المسبق | No | `true` | `true` |

### Prisma Settings | إعدادات Prisma

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `PRISMA_POOL_TIMEOUT` | Pool timeout (seconds) | مهلة التجمع | No | `20` |
| `PRISMA_CONNECT_TIMEOUT` | Connection timeout (seconds) | مهلة الاتصال | No | `10` |
| `PRISMA_QUERY_TIMEOUT` | Query timeout (ms) | مهلة الاستعلام | No | `30000` |
| `PRISMA_STATEMENT_TIMEOUT` | Statement timeout (ms) | مهلة البيان | No | `30000` |
| `PRISMA_IDLE_TIMEOUT` | Idle timeout (seconds) | مهلة الخمول | No | `600` |
| `PRISMA_CONNECTION_LIFETIME` | Max connection lifetime (seconds) | عمر الاتصال الأقصى | No | `3600` |

---

## 3. PgBouncer Connection Pooling

### تجمع اتصالات PgBouncer

PgBouncer optimized for 39+ services with transaction pooling mode.

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `PGBOUNCER_POOL_MODE` | Pool mode | وضع التجمع | No | `transaction` |
| `PGBOUNCER_MAX_DB_CONNECTIONS` | Max PostgreSQL connections | أقصى اتصالات PostgreSQL | No | `250` |
| `PGBOUNCER_DEFAULT_POOL_SIZE` | Default pool size per user/db | حجم التجمع الافتراضي | No | `30` |
| `PGBOUNCER_MIN_POOL_SIZE` | Minimum pool size | الحد الأدنى لحجم التجمع | No | `10` |
| `PGBOUNCER_RESERVE_POOL_SIZE` | Reserve pool for maintenance | تجمع احتياطي للصيانة | No | `10` |
| `PGBOUNCER_MAX_CLIENT_CONN` | Max client connections | أقصى اتصالات العميل | No | `800` |
| `PGBOUNCER_CLIENT_IDLE_TIMEOUT` | Client idle timeout (seconds) | مهلة خمول العميل | No | `900` |
| `PGBOUNCER_SERVER_IDLE_TIMEOUT` | Server idle timeout (seconds) | مهلة خمول الخادم | No | `600` |
| `PGBOUNCER_QUERY_TIMEOUT` | Query timeout (seconds) | مهلة الاستعلام | No | `120` |
| `PGBOUNCER_QUERY_WAIT_TIMEOUT` | Query wait timeout (seconds) | مهلة انتظار الاستعلام | No | `30` |

---

## 4. Redis Configuration

### تكوين Redis

Redis 7.x for caching, sessions, and rate limiting.

| Variable | Description | الوصف | Required | Default | Example |
|----------|-------------|-------|----------|---------|---------|
| `REDIS_PASSWORD` | Redis authentication password | كلمة مرور Redis | **Yes** | - | `secure_redis_password` |
| `REDIS_HOST` | Redis server host | مضيف خادم Redis | No | `redis` | `redis`, `localhost` |
| `REDIS_PORT` | Redis server port | منفذ خادم Redis | No | `6379` | `6379` |
| `REDIS_DB` | Redis database number | رقم قاعدة بيانات Redis | No | `0` | `0`, `1` |
| `REDIS_MAXMEMORY` | Max memory limit | حد الذاكرة الأقصى | No | `512mb` | `512mb`, `1gb` |
| `REDIS_URL` | Full Redis connection URL | رابط اتصال Redis الكامل | No | - | `redis://:password@redis:6379/0` |
| `REDIS_CONTAINER` | Container name for backups | اسم الحاوية للنسخ الاحتياطي | No | `sahool-redis` | `sahool-redis` |

### Redis TLS Configuration | تكوين TLS لـ Redis

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `REDIS_SSL_ENABLED` | Enable SSL/TLS | تمكين SSL/TLS | No | `true` |
| `REDIS_TLS_PORT` | TLS port | منفذ TLS | No | `6380` |
| `REDIS_SSL_CERT` | Client certificate | شهادة العميل | No | `/certs/redis-client.crt` |
| `REDIS_SSL_KEY` | Client key | مفتاح العميل | No | `/certs/redis-client.key` |
| `REDIS_SSL_CA` | CA certificate | شهادة CA | No | `/certs/ca.crt` |

### Redis ACL Users (Enhanced Security) | مستخدمو ACL لـ Redis

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `REDIS_APP_PASSWORD` | Application user password | كلمة مرور مستخدم التطبيق | No | `${REDIS_PASSWORD}` |
| `REDIS_ADMIN_PASSWORD` | Admin user password | كلمة مرور المسؤول | No | `${REDIS_PASSWORD}` |
| `REDIS_KONG_PASSWORD` | Kong user password | كلمة مرور Kong | No | `${REDIS_PASSWORD}` |
| `REDIS_READONLY_PASSWORD` | Read-only user password | كلمة مرور القراءة فقط | No | `${REDIS_PASSWORD}` |

---

## 5. NATS Message Queue

### طابور رسائل NATS

NATS 2.x with JetStream for event-driven architecture.

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `NATS_USER` | NATS application username | اسم مستخدم تطبيق NATS | **Yes** | `sahool_app` |
| `NATS_PASSWORD` | NATS application password | كلمة مرور تطبيق NATS | **Yes** | - |
| `NATS_ADMIN_USER` | NATS admin username | اسم مستخدم مسؤول NATS | **Yes** | `nats_admin` |
| `NATS_ADMIN_PASSWORD` | NATS admin password | كلمة مرور مسؤول NATS | **Yes** | - |
| `NATS_MONITOR_USER` | NATS monitor username | اسم مستخدم مراقب NATS | **Yes** | `nats_monitor` |
| `NATS_MONITOR_PASSWORD` | NATS monitor password | كلمة مرور مراقب NATS | **Yes** | - |
| `NATS_CLUSTER_USER` | NATS cluster username | اسم مستخدم مجموعة NATS | Yes | `nats_cluster` |
| `NATS_CLUSTER_PASSWORD` | NATS cluster password | كلمة مرور مجموعة NATS | Yes | - |
| `NATS_SYSTEM_USER` | NATS system username | اسم مستخدم نظام NATS | No | `nats_system` |
| `NATS_SYSTEM_PASSWORD` | NATS system password | كلمة مرور نظام NATS | No | - |
| `NATS_JETSTREAM_KEY` | JetStream encryption key (AES-256) | مفتاح تشفير JetStream | No | - |
| `NATS_URL` | Full NATS connection URL | رابط اتصال NATS الكامل | Yes | - |
| `NATS_SUBJECT` | Default subscription pattern | نمط الاشتراك الافتراضي | No | `sahool.notifications.*` |

### NATS TLS Configuration | تكوين TLS لـ NATS

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `NATS_TLS_ENABLED` | Enable TLS | تمكين TLS | No | `true` |
| `NATS_TLS_PORT` | TLS port | منفذ TLS | No | `4223` |
| `NATS_TLS_CERT` | Client certificate | شهادة العميل | No | `/certs/nats-client.crt` |
| `NATS_TLS_KEY` | Client key | مفتاح العميل | No | `/certs/nats-client.key` |
| `NATS_TLS_CA` | CA certificate | شهادة CA | No | `/certs/ca.crt` |

### NATS Prometheus Exporter | مُصدِّر Prometheus لـ NATS

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `NATS_EXPORTER_LISTEN_ADDRESS` | Exporter listen address | عنوان الاستماع | No | `0.0.0.0:7777` |
| `NATS_EXPORTER_LISTEN_PATH` | Metrics path | مسار المقاييس | No | `/metrics` |

---

## 6. Authentication & JWT

### المصادقة و JWT

| Variable | Description | الوصف | Required | Default | Example |
|----------|-------------|-------|----------|---------|---------|
| `JWT_SECRET_KEY` | JWT signing secret (min 32 chars) | مفتاح توقيع JWT | **Yes** | - | `your-secure-secret-key-min-32-chars` |
| `JWT_SECRET` | Alias for JWT_SECRET_KEY | اسم بديل | No | `${JWT_SECRET_KEY}` | - |
| `JWT_ALGORITHM` | JWT signing algorithm | خوارزمية التوقيع | No | `HS256` | `HS256`, `RS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry (minutes) | انتهاء رمز الوصول | No | `60` | `60`, `30` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry (days) | انتهاء رمز التحديث | No | `7` | `7`, `14` |
| `JWT_AUDIENCE` | JWT audience claim | مطالبة الجمهور | No | `sahool-api` | `sahool-api` |
| `JWT_ISSUER` | JWT issuer claim | مطالبة المُصدر | No | `sahool-platform` | `sahool-platform` |
| `JWT_EXPIRES_IN` | Token expiry (alternative format) | انتهاء الرمز | No | `7d` | `7d`, `24h` |
| `TOKEN_REVOCATION_ENABLED` | Enable token revocation | تمكين إلغاء الرمز | No | `true` | `true` |

### Kong JWT Secrets | أسرار JWT لـ Kong

| Variable | Description | الوصف | Required |
|----------|-------------|-------|----------|
| `STARTER_JWT_SECRET` | Starter package JWT secret | سر JWT للباقة المبدئية | Yes |
| `PROFESSIONAL_JWT_SECRET` | Professional package JWT secret | سر JWT للباقة المهنية | Yes |
| `ENTERPRISE_JWT_SECRET` | Enterprise package JWT secret | سر JWT للباقة المؤسسية | Yes |
| `RESEARCH_JWT_SECRET` | Research JWT secret | سر JWT للبحث | Yes |
| `ADMIN_JWT_SECRET` | Admin JWT secret | سر JWT للمسؤول | Yes |
| `SERVICE_JWT_SECRET` | Service-to-service JWT secret | سر JWT بين الخدمات | Yes |
| `TRIAL_JWT_SECRET` | Trial JWT secret | سر JWT للتجربة | Yes |

### MFA Configuration | تكوين المصادقة متعددة العوامل

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `MFA_ENABLED` | Enable MFA | تمكين MFA | No | `true` |
| `MFA_ENFORCEMENT_LEVEL` | MFA enforcement level | مستوى فرض MFA | No | `required_for_admin` |
| `TOTP_ISSUER` | TOTP issuer name | اسم مُصدر TOTP | No | `SAHOOL` |
| `MAX_LOGIN_ATTEMPTS` | Max failed login attempts | أقصى محاولات تسجيل دخول فاشلة | No | `5` |
| `LOCKOUT_DURATION_MINUTES` | Account lockout duration | مدة قفل الحساب | No | `30` |

---

## 7. Kong API Gateway

### بوابة Kong API

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `KONG_DATABASE` | Kong database type | نوع قاعدة بيانات Kong | No | `off` (declarative) |
| `KONG_PG_HOST` | Kong PostgreSQL host | مضيف PostgreSQL لـ Kong | No | `kong-database` |
| `KONG_PG_USER` | Kong PostgreSQL user | مستخدم PostgreSQL لـ Kong | No | `kong` |
| `KONG_PG_PASSWORD` | Kong PostgreSQL password | كلمة مرور PostgreSQL لـ Kong | No | - |
| `KONG_PG_DATABASE` | Kong database name | اسم قاعدة بيانات Kong | No | `kong` |
| `KONG_DECLARATIVE_CONFIG` | Declarative config path | مسار التكوين التصريحي | No | `/kong/declarative/kong.yml` |
| `KONG_ADMIN_LISTEN` | Admin API listen address | عنوان استماع Admin API | No | `127.0.0.1:8001` |
| `KONG_PROXY_LISTEN` | Proxy listen address | عنوان استماع البروكسي | No | `0.0.0.0:8000` |
| `KONG_PLUGINS` | Enabled plugins | الإضافات المُمكّنة | No | `bundled,cors,rate-limiting,jwt,acl,prometheus` |
| `KONG_LOG_LEVEL` | Kong log level | مستوى سجل Kong | No | `notice` |

### Kong Performance | أداء Kong

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `KONG_NGINX_WORKER_PROCESSES` | Nginx worker processes | عمليات عامل Nginx | `auto` |
| `KONG_NGINX_WORKER_CONNECTIONS` | Worker connections | اتصالات العامل | `4096` |
| `KONG_NGINX_KEEPALIVE_TIMEOUT` | Keepalive timeout | مهلة الحفاظ على الاتصال | `60s` |
| `KONG_UPSTREAM_KEEPALIVE_POOL_SIZE` | Upstream keepalive pool | تجمع الحفاظ على الاتصال | `60` |
| `KONG_MEM_CACHE_SIZE` | Memory cache size | حجم ذاكرة التخزين المؤقت | `128m` |

### Kong DNS Configuration | تكوين DNS لـ Kong

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `KONG_DNS_RESOLVER` | DNS resolver address | عنوان محلل DNS | `127.0.0.11:53` |
| `KONG_DNS_ORDER` | DNS resolution order | ترتيب حل DNS | `LAST,A,CNAME` |
| `KONG_DNS_CACHE_TTL` | DNS cache TTL (seconds) | TTL ذاكرة DNS | `300` |
| `KONG_DNS_STALE_TTL` | Stale DNS TTL | TTL DNS القديم | `30` |
| `KONG_DNS_ERROR_TTL` | DNS error TTL | TTL خطأ DNS | `30` |

### Kong CORS Configuration | تكوين CORS لـ Kong

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `KONG_CORS_ORIGINS` | Comma-separated list of allowed CORS origins. Use specific domains in production instead of wildcard '*'. | قائمة أصول CORS المسموح بها مفصولة بفواصل. استخدم نطاقات محددة في الإنتاج بدلاً من '*'. | `*` |

### Kong Rate Limiting (Redis-based distributed) | تحديد المعدل الموزع لـ Kong (عبر Redis)

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `KONG_RATE_LIMIT_REDIS_HOST` | Redis host for Redis-based distributed rate limiting | مضيف Redis لتحديد المعدل الموزع | `redis` |
| `KONG_RATE_LIMIT_REDIS_PORT` | Redis port for distributed rate limiting | منفذ Redis لتحديد المعدل الموزع | `6379` |
| `KONG_RATE_LIMIT_REDIS_DB` | Redis database number for rate limiting | رقم قاعدة بيانات Redis لتحديد المعدل | `1` |

---

## 8. AI/ML Services

### خدمات الذكاء الاصطناعي والتعلم الآلي

### Multi-Provider LLM Configuration | تكوين متعدد المزودين

| Variable | Description | الوصف | Required | Default | Services |
|----------|-------------|-------|----------|---------|----------|
| `PRIMARY_LLM_PROVIDER` | Primary LLM provider | المزود الرئيسي | No | `anthropic` | ai-advisor |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | مفتاح API لـ Claude | No | - | ai-advisor |
| `CLAUDE_MODEL` | Claude model ID | معرف نموذج Claude | No | `claude-sonnet-4-6` | ai-advisor |
| `OPENAI_API_KEY` | OpenAI API key | مفتاح API لـ OpenAI | No | - | ai-advisor |
| `OPENAI_MODEL` | OpenAI model ID | معرف نموذج OpenAI | No | `gpt-4o` | ai-advisor |
| `GOOGLE_API_KEY` | Google AI API key | مفتاح API لـ Google AI | No | - | ai-advisor |
| `GEMINI_MODEL` | Gemini model ID | معرف نموذج Gemini | No | `gemini-1.5-pro` | ai-advisor |

### Qdrant Vector Database | قاعدة بيانات Qdrant الشعاعية

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `QDRANT_HOST` | Qdrant server host | مضيف خادم Qdrant | No | `qdrant` |
| `QDRANT_PORT` | Qdrant HTTP port | منفذ HTTP لـ Qdrant | No | `6333` |
| `QDRANT_GRPC_PORT` | Qdrant gRPC port | منفذ gRPC لـ Qdrant | No | `6334` |
| `QDRANT_API_KEY` | Qdrant API key (production) | مفتاح API لـ Qdrant | No | - |
| `QDRANT__LOG_LEVEL` | Qdrant log level | مستوى سجل Qdrant | No | `INFO` |
| `EMBEDDING_MODEL` | Embedding model name | اسم نموذج التضمين | No | `paraphrase-multilingual-MiniLM-L12-v2` |

### AI Model Configuration | تكوين نموذج الذكاء الاصطناعي

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `AI_MODEL_ENDPOINT` | AI model prediction endpoint | نقطة نهاية التنبؤ | No | `http://localhost:8080/predict` |
| `MODEL_PATH` | Path to ML models | مسار نماذج ML | No | `/models` |
| `USE_LOCAL_MODEL` | Use local model | استخدام نموذج محلي | No | `false` |
| `CONFIDENCE_THRESHOLD` | Prediction confidence threshold | عتبة ثقة التنبؤ | No | `0.8` |
| `EXPERT_REVIEW_THRESHOLD` | Expert review threshold | عتبة مراجعة الخبير | No | `0.6` |
| `SIGNIFICANT_CHANGE_PERCENT` | Significant change threshold | عتبة التغيير المهم | No | `10` |

---

## 9. Ollama Local LLM

### Ollama للنماذج اللغوية المحلية

Local LLM hosting for offline-first code analysis and agricultural advisory.

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `OLLAMA_HOST` | Ollama server host | مضيف خادم Ollama | No | `0.0.0.0` |
| `OLLAMA_URL` | Ollama server URL | رابط خادم Ollama | No | `http://ollama:11434` |
| `OLLAMA_MODEL` | Default model to use | النموذج الافتراضي | No | `llama3.2` |
| `OLLAMA_ORIGINS` | Allowed CORS origins | أصول CORS المسموحة | No | `*` |
| `OLLAMA_KEEP_ALIVE` | Model keep-alive duration | مدة إبقاء النموذج | No | `24h` |
| `OLLAMA_NUM_PARALLEL` | Max parallel requests | أقصى طلبات متوازية | No | `24` |
| `OLLAMA_MAX_LOADED_MODELS` | Max loaded models | أقصى نماذج محملة | No | `2` |

### Ollama GPU Configuration | تكوين GPU لـ Ollama

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `OLLAMA_NUM_GPU` | Number of GPUs to use | عدد وحدات GPU | No | `1` |
| `CUDA_VISIBLE_DEVICES` | CUDA device IDs | معرفات أجهزة CUDA | No | `0` |
| `OLLAMA_GPU_LAYERS` | GPU layers (999=all) | طبقات GPU | No | `999` |

---

## 10. Monitoring & Observability

### المراقبة والرؤية

### Grafana | جرافانا

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `GRAFANA_ADMIN_USER` | Grafana admin username | اسم مستخدم مسؤول Grafana | No | `admin` |
| `GRAFANA_ADMIN_PASSWORD` | Grafana admin password | كلمة مرور مسؤول Grafana | **Yes** | - |
| `GRAFANA_ROOT_URL` | Grafana root URL | رابط جذر Grafana | No | `http://localhost:3002` |
| `GRAFANA_DOMAIN` | Grafana domain | نطاق Grafana | No | `localhost` |
| `GF_LOG_LEVEL` | Grafana log level | مستوى سجل Grafana | No | `info` |
| `GF_INSTALL_PLUGINS` | Plugins to install | الإضافات للتثبيت | No | `grafana-clock-panel,...` |

### Prometheus | بروميثيوس

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `PROMETHEUS_METRICS_ENABLED` | Enable Prometheus metrics | تمكين مقاييس Prometheus | No | `true` |
| `PROMETHEUS_MULTIPROC_DIR` | Multiprocess metrics directory | دليل المقاييس متعددة العمليات | No | `/tmp/prometheus_multiproc` |

### OpenTelemetry | OpenTelemetry

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP exporter endpoint | نقطة نهاية مُصدر OTLP | No | - |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | OTLP protocol | بروتوكول OTLP | No | `grpc` |
| `OTEL_SERVICE_NAME` | Service name for tracing | اسم الخدمة للتتبع | No | - |
| `OTEL_TRACES_SAMPLER` | Trace sampler | عينة التتبع | No | `parentbased_traceidratio` |
| `OTEL_TRACES_SAMPLER_ARG` | Sampler argument | معامل العينة | No | `0.1` |

### Jaeger | Jaeger

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `JAEGER_ENDPOINT` | Jaeger collector endpoint | نقطة نهاية جامع Jaeger | No | `jaeger:14250` |
| `JAEGER_LOG_LEVEL` | Jaeger log level | مستوى سجل Jaeger | No | `info` |

### Health Checks | فحوصات الصحة

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `HEALTH_CHECK_INTERVAL_SECONDS` | Health check interval | فترة فحص الصحة | No | `30` |
| `HEALTH_CHECK_TIMEOUT_SECONDS` | Health check timeout | مهلة فحص الصحة | No | `5` |

---

## 11. External APIs

### واجهات برمجة التطبيقات الخارجية

### Weather APIs | واجهات الطقس

| Variable | Description | الوصف | Required | Default | Services |
|----------|-------------|-------|----------|---------|----------|
| `USE_MULTI_PROVIDER` | Enable multi-provider weather | تمكين متعدد المزودين | No | `true` | weather-service |
| `USE_MOCK_WEATHER` | Use mock weather data | استخدام بيانات وهمية | No | `false` | weather-service |
| `OPENWEATHERMAP_API_KEY` | OpenWeatherMap API key | مفتاح OpenWeatherMap | No | - | weather-service |
| `OPENWEATHER_API_KEY` | Alias for OpenWeatherMap | اسم بديل | No | - | weather-service |
| `WEATHERAPI_KEY` | WeatherAPI.com API key | مفتاح WeatherAPI | No | - | weather-service |
| `YEMEN_MET_ENABLED` | Enable Yemen Met Service | تمكين خدمة الأرصاد اليمنية | No | `false` | weather-service |
| `YEMEN_MET_API_KEY` | Yemen Met API key | مفتاح Yemen Met | No | - | weather-service |

### Weather Cache Configuration | تكوين ذاكرة التخزين المؤقت للطقس

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `WEATHER_CACHE_ENABLED` | Enable weather caching | تمكين التخزين المؤقت | `true` |
| `WEATHER_CACHE_TTL_MINUTES` | Cache TTL (minutes) | TTL التخزين المؤقت | `30` |
| `WEATHER_CACHE_CURRENT_TTL` | Current weather cache TTL | TTL الطقس الحالي | `1800` |
| `WEATHER_CACHE_FORECAST_TTL` | Forecast cache TTL | TTL التوقعات | `3600` |
| `WEATHER_ALERTS_ENABLED` | Enable weather alerts | تمكين تنبيهات الطقس | `true` |
| `WEATHER_AG_INDICES_ENABLED` | Enable agricultural indices | تمكين المؤشرات الزراعية | `true` |

### Agricultural Weather Thresholds | عتبات الطقس الزراعية

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `GDD_BASE_TEMP` | Growing Degree Days base temp | درجة حرارة أساس GDD | `10` |
| `CHILL_HOURS_THRESHOLD` | Chill hours threshold | عتبة ساعات البرودة | `7.2` |
| `FROST_CRITICAL_TEMP` | Critical frost temperature | درجة حرارة الصقيع الحرجة | `0` |
| `HEAT_WAVE_CRITICAL_TEMP` | Critical heat wave temperature | درجة حرارة موجة الحر | `35` |
| `HEAVY_RAIN_CRITICAL_MM` | Critical rainfall (mm) | هطول الأمطار الحرج | `50` |

### Satellite Imagery APIs | واجهات صور الأقمار الصناعية

| Variable | Description | الوصف | Required | Services |
|----------|-------------|-------|----------|----------|
| `SENTINEL_HUB_CLIENT_ID` | Sentinel Hub client ID | معرف عميل Sentinel Hub | No | vegetation-analysis-service |
| `SENTINEL_HUB_CLIENT_SECRET` | Sentinel Hub client secret | سر عميل Sentinel Hub | No | vegetation-analysis-service |
| `NASA_EARTHDATA_USERNAME` | NASA Earthdata username | اسم مستخدم NASA Earthdata | No | vegetation-analysis-service |
| `NASA_EARTHDATA_PASSWORD` | NASA Earthdata password | كلمة مرور NASA Earthdata | No | vegetation-analysis-service |
| `PLANET_API_KEY` | Planet Labs API key | مفتاح Planet Labs | No | vegetation-analysis-service |
| `PLANET_CLIENT_ID` | Planet Labs client ID | معرف عميل Planet Labs | No | vegetation-analysis-service |

### Payment Gateways | بوابات الدفع

| Variable | Description | الوصف | Required | Services |
|----------|-------------|-------|----------|----------|
| `STRIPE_API_KEY` | Stripe API key | مفتاح Stripe API | No | billing-core |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | سر webhook لـ Stripe | No | billing-core |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | مفتاح Stripe العام | No | web, mobile |
| `THARWATT_BASE_URL` | Tharwatt API base URL | رابط قاعدة Tharwatt API | No | billing-core |
| `THARWATT_API_KEY` | Tharwatt API key | مفتاح Tharwatt API | No | billing-core |
| `THARWATT_MERCHANT_ID` | Tharwatt merchant ID | معرف تاجر Tharwatt | No | billing-core |
| `THARWATT_WEBHOOK_SECRET` | Tharwatt webhook secret | سر webhook لـ Tharwatt | No | billing-core |
| `DEFAULT_CURRENCY` | Default currency | العملة الافتراضية | No | billing-core |
| `YER_EXCHANGE_RATE` | YER exchange rate | سعر صرف الريال اليمني | No | billing-core |

### Maps APIs | واجهات الخرائط

| Variable | Description | الوصف | Required | Services |
|----------|-------------|-------|----------|----------|
| `GOOGLE_MAPS_API_KEY` | Google Maps API key | مفتاح Google Maps API | No | mobile, web |
| `MAPBOX_ACCESS_TOKEN` | Mapbox access token | رمز وصول Mapbox | No | mobile |
| `MAPBOX_STYLE_URL` | Mapbox style URL | رابط نمط Mapbox | No | mobile |
| `MAP_TILE_URL` | Custom map tile URL | رابط بلاطات الخريطة | No | mobile |

---

## 12. Notification Services

### خدمات الإشعارات

### SMTP Email Configuration | تكوين بريد SMTP

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `SMTP_HOST` | SMTP server host | مضيف خادم SMTP | No | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | منفذ خادم SMTP | No | `587` |
| `SMTP_USER` | SMTP username | اسم مستخدم SMTP | No | - |
| `SMTP_PASSWORD` | SMTP password | كلمة مرور SMTP | No | - |
| `SMTP_FROM_EMAIL` | From email address | عنوان البريد المرسل | No | `noreply@sahool.com` |
| `SMTP_FROM_NAME` | From name | اسم المرسل | No | `SAHOOL Platform` |

### SendGrid Configuration | تكوين SendGrid

| Variable | Description | الوصف | Required |
|----------|-------------|-------|----------|
| `SENDGRID_API_KEY` | SendGrid API key | مفتاح SendGrid API | No |
| `SENDGRID_FROM_EMAIL` | SendGrid from email | بريد SendGrid المرسل | No |
| `SENDGRID_FROM_NAME` | SendGrid from name | اسم SendGrid المرسل | No |

### Firebase Push Notifications | إشعارات Firebase

| Variable | Description | الوصف | Required |
|----------|-------------|-------|----------|
| `FIREBASE_PROJECT_ID` | Firebase project ID | معرف مشروع Firebase | No |
| `FIREBASE_CREDENTIALS` | Firebase credentials JSON | اعتمادات Firebase | No |
| `FIREBASE_CREDENTIALS_PATH` | Path to credentials file | مسار ملف الاعتمادات | No |
| `FIREBASE_CREDENTIALS_JSON` | Credentials as JSON string | الاعتمادات كنص JSON | No |
| `FCM_SERVER_KEY` | FCM server key | مفتاح خادم FCM | No |

### SMS Configuration | تكوين الرسائل القصيرة

| Variable | Description | الوصف | Required |
|----------|-------------|-------|----------|
| `SMS_PROVIDER` | SMS provider name | اسم مزود SMS | No |
| `SMS_API_KEY` | SMS API key | مفتاح SMS API | No |
| `SMS_API_SECRET` | SMS API secret | سر SMS API | No |
| `SMS_FROM_NUMBER` | SMS sender number | رقم المرسل | No |
| `TWILIO_ACCOUNT_SID` | Twilio account SID | معرف حساب Twilio | No |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | رمز مصادقة Twilio | No |
| `TWILIO_PHONE_NUMBER` | Twilio phone number | رقم هاتف Twilio | No |

---

## 13. File Storage & CDN

### تخزين الملفات و CDN

### MinIO Object Storage | تخزين كائنات MinIO

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `MINIO_ROOT_USER` | MinIO root username (min 16 chars) | اسم مستخدم جذر MinIO | **Yes** | - |
| `MINIO_ROOT_PASSWORD` | MinIO root password (min 16 chars) | كلمة مرور جذر MinIO | **Yes** | - |
| `MINIO_ACCESS_KEY` | Alias for MINIO_ROOT_USER | اسم بديل | No | `${MINIO_ROOT_USER}` |
| `MINIO_SECRET_KEY` | Alias for MINIO_ROOT_PASSWORD | اسم بديل | No | `${MINIO_ROOT_PASSWORD}` |
| `MINIO_ENDPOINT` | MinIO server endpoint | نقطة نهاية خادم MinIO | No | `https://minio:9000` |
| `MINIO_BROWSER` | Enable MinIO console | تمكين وحدة تحكم MinIO | No | `off` |
| `MINIO_PROMETHEUS_AUTH_TYPE` | Prometheus auth type | نوع مصادقة Prometheus | No | `jwt` |
| `MINIO_DOMAIN` | MinIO domain for virtual-host | نطاق MinIO للمضيف الافتراضي | No | `minio.sahool.local` |
| `MINIO_REGION` | MinIO region | منطقة MinIO | No | `us-east-1` |
| `MINIO_BUCKETS` | Default buckets to create | الدلاء الافتراضية | No | `uploads,documents,images,backups` |

### MinIO Encryption | تشفير MinIO

| Variable | Description | الوصف | Required |
|----------|-------------|-------|----------|
| `MINIO_ENCRYPTION_MASTER_KEY` | SSE master key | مفتاح تشفير رئيسي | No |
| `MINIO_KMS_SECRET_KEY` | KMS secret key | مفتاح KMS السري | No |

### General File Storage | تخزين الملفات العام

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `UPLOAD_DIR` | Upload directory | دليل التحميل | No | `/uploads` |
| `AVATAR_UPLOAD_PATH` | Avatar upload path | مسار تحميل الصور الشخصية | No | `/uploads/avatars` |
| `CDN_BASE_URL` | CDN base URL | رابط قاعدة CDN | No | `https://cdn.sahool.com` |
| `CDN_URL` | CDN URL | رابط CDN | No | `https://cdn.sahool.com` |
| `MAX_FILE_SIZE` | Max file size (bytes) | أقصى حجم ملف | No | `10485760` |

---

## 14. Security & Secrets

### الأمان والأسرار

### General Security | الأمان العام

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `APP_SECRET_KEY` | Application secret key | مفتاح التطبيق السري | **Yes** | - |
| `SIGNATURE_SECRET_KEY` | Signature secret key | مفتاح التوقيع السري | No | - |
| `SAHOOL_AUTH_ENABLED` | Enable SAHOOL authentication | تمكين مصادقة سهول | No | `true` |
| `WS_REQUIRE_AUTH` | Require WebSocket auth | طلب مصادقة WebSocket | No | `true` |

### Secrets Backend Configuration | تكوين خلفية الأسرار

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `SECRET_BACKEND` | Secrets backend type | نوع خلفية الأسرار | No | `environment` |

Options: `environment`, `vault`, `aws_secrets_manager`, `azure_key_vault`

### HashiCorp Vault | HashiCorp Vault

| Variable | Description | الوصف | Required |
|----------|-------------|-------|----------|
| `VAULT_ADDR` | Vault server address | عنوان خادم Vault | No |
| `VAULT_TOKEN` | Vault authentication token | رمز مصادقة Vault | No |
| `VAULT_ROLE_ID` | Vault AppRole role ID | معرف دور AppRole | No |
| `VAULT_SECRET_ID` | Vault AppRole secret ID | معرف سر AppRole | No |
| `VAULT_NAMESPACE` | Vault namespace (Enterprise) | مساحة اسم Vault | No |
| `VAULT_MOUNT_POINT` | KV secrets mount point | نقطة تثبيت أسرار KV | No |
| `VAULT_PATH_PREFIX` | Secrets path prefix | بادئة مسار الأسرار | No |

### AWS Secrets Manager | AWS Secrets Manager

| Variable | Description | الوصف | Required |
|----------|-------------|-------|----------|
| `AWS_REGION` | AWS region | منطقة AWS | No |
| `AWS_ACCESS_KEY_ID` | AWS access key ID | معرف مفتاح وصول AWS | No |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key | مفتاح وصول AWS السري | No |
| `AWS_SECRETS_PREFIX` | Secrets prefix | بادئة الأسرار | No |

### Azure Key Vault | Azure Key Vault

| Variable | Description | الوصف | Required |
|----------|-------------|-------|----------|
| `AZURE_KEY_VAULT_URL` | Key Vault URL | رابط Key Vault | No |
| `AZURE_TENANT_ID` | Azure tenant ID | معرف مستأجر Azure | No |
| `AZURE_CLIENT_ID` | Azure client ID | معرف عميل Azure | No |
| `AZURE_CLIENT_SECRET` | Azure client secret | سر عميل Azure | No |

### Local Encryption | التشفير المحلي

| Variable | Description | الوصف | Required |
|----------|-------------|-------|----------|
| `ENCRYPTION_KEY` | Local encryption key | مفتاح التشفير المحلي | No |
| `ENCRYPTION_KEY_FILE` | Encryption key file path | مسار ملف مفتاح التشفير | No |
| `ENCRYPTED_SECRETS_FILE` | Encrypted secrets file path | مسار ملف الأسرار المشفرة | No |

### etcd Configuration | تكوين etcd

| Variable | Description | الوصف | Required |
|----------|-------------|-------|----------|
| `ETCD_ROOT_USERNAME` | etcd root username | اسم مستخدم جذر etcd | **Yes** |
| `ETCD_ROOT_PASSWORD` | etcd root password | كلمة مرور جذر etcd | **Yes** |
| `ETCDCTL_API` | etcdctl API version | إصدار API لـ etcdctl | No |
| `ETCDCTL_ENDPOINTS` | etcd endpoints | نقاط نهاية etcd | No |

### MQTT IoT Security | أمان MQTT IoT

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `MQTT_BROKER` | MQTT broker host | مضيف وسيط MQTT | No | `mqtt` |
| `MQTT_PORT` | MQTT broker port | منفذ وسيط MQTT | No | `1883` |
| `MQTT_USER` | MQTT username | اسم مستخدم MQTT | No | `sahool_iot` |
| `MQTT_PASSWORD` | MQTT password | كلمة مرور MQTT | **Yes** | - |
| `MQTT_TOPIC` | Default MQTT topic pattern | نمط موضوع MQTT | No | `sahool/sensors/#` |

---

## 15. Mobile Application

### تطبيق الجوال

### API Configuration | تكوين API

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `ENV` | Environment name | اسم البيئة | No | `development` |
| `API_BASE_URL` | API base URL | رابط قاعدة API | **Yes** | `http://10.0.2.2:8000/api/v1` |
| `API_VERSION` | API version | إصدار API | No | `v1` |
| `DEV_HOST` | Development host | مضيف التطوير | No | `10.0.2.2` |
| `PROD_HOST` | Production host | مضيف الإنتاج | No | `api.sahool.app` |
| `STAGING_HOST` | Staging host | مضيف التجهيز | No | `api-staging.sahool.app` |
| `WS_GATEWAY_URL` | WebSocket gateway URL | رابط بوابة WebSocket | No | `ws://10.0.2.2:8081` |

### Feature Flags | أعلام الميزات

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `ENABLE_OFFLINE_MODE` | Enable offline-first mode | تمكين وضع عدم الاتصال | `true` |
| `ENABLE_BACKGROUND_SYNC` | Enable background sync | تمكين المزامنة الخلفية | `true` |
| `ENABLE_CAMERA` | Enable camera features | تمكين ميزات الكاميرا | `true` |
| `ENABLE_PUSH_NOTIFICATIONS` | Enable push notifications | تمكين الإشعارات | `false` |
| `ENABLE_EDGE_AI` | Enable on-device AI | تمكين الذكاء الاصطناعي على الجهاز | `false` |
| `ENABLE_VOICE` | Enable voice commands | تمكين الأوامر الصوتية | `false` |
| `ENABLE_AR` | Enable AR features | تمكين ميزات الواقع المعزز | `false` |
| `ENABLE_ANALYTICS` | Enable analytics | تمكين التحليلات | `false` |
| `ENABLE_CRASH_REPORTING` | Enable crash reporting | تمكين تقارير الأعطال | `false` |

### Security Settings | إعدادات الأمان

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `ENABLE_BIOMETRIC_AUTH` | Enable biometric auth | تمكين المصادقة البيومترية | `true` |
| `ENABLE_CERTIFICATE_PINNING` | Enable cert pinning | تمكين تثبيت الشهادة | `false` |
| `ENABLE_DEVICE_INTEGRITY` | Enable integrity checks | تمكين فحوصات السلامة | `false` |
| `ENABLE_DATABASE_ENCRYPTION` | Enable DB encryption | تمكين تشفير قاعدة البيانات | `false` |
| `SKIP_DEVICE_CHECKS` | Skip device security checks | تخطي فحوصات الأمان | `true` |

### Sync Configuration | تكوين المزامنة

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `SYNC_INTERVAL_SECONDS` | Foreground sync interval | فترة المزامنة الأمامية | `30` |
| `BG_SYNC_INTERVAL_MINUTES` | Background sync interval | فترة المزامنة الخلفية | `15` |
| `MAX_RETRY_COUNT` | Max retry attempts | أقصى محاولات إعادة | `5` |
| `OUTBOX_BATCH_SIZE` | Outbox batch size | حجم دفعة الصندوق الصادر | `50` |

### Monitoring | المراقبة

| Variable | Description | الوصف | Required |
|----------|-------------|-------|----------|
| `SENTRY_DSN` | Sentry DSN for crash reporting | DSN Sentry لتقارير الأعطال | No |
| `SENTRY_ENVIRONMENT` | Sentry environment | بيئة Sentry | No |

---

## 16. Frontend Applications

### تطبيقات الواجهة الأمامية

### Web Dashboard & Admin Portal | لوحة تحكم الويب وبوابة الإدارة

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `NEXT_PUBLIC_API_URL` | API gateway URL | رابط بوابة API | **Yes** | `http://localhost:8000` |
| `NEXT_PUBLIC_WS_URL` | WebSocket gateway URL | رابط بوابة WebSocket | No | `ws://localhost:8081` |
| `NEXT_PUBLIC_API_BASE` | API base URL | رابط قاعدة API | No | `http://localhost` |
| `NEXT_PUBLIC_AUTH_URL` | Auth service URL | رابط خدمة المصادقة | No | `http://localhost:8001` |
| `NEXT_PUBLIC_APP_NAME` | Application name | اسم التطبيق | No | `SAHOOL` |
| `NEXT_PUBLIC_APP_VERSION` | Application version | إصدار التطبيق | No | `16.0.0` |

### Feature Flags | أعلام الميزات

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `NEXT_PUBLIC_FEATURE_OFFLINE` | Enable offline feature | تمكين ميزة عدم الاتصال | `true` |
| `NEXT_PUBLIC_FEATURE_NDVI` | Enable NDVI feature | تمكين ميزة NDVI | `true` |
| `NEXT_PUBLIC_FEATURE_ADVISOR` | Enable advisor feature | تمكين ميزة المستشار | `true` |
| `NEXT_PUBLIC_FEATURE_MAPS` | Enable maps feature | تمكين ميزة الخرائط | `true` |
| `NEXT_PUBLIC_FEATURE_CHARTS` | Enable charts feature | تمكين ميزة الرسوم البيانية | `true` |

### Monitoring | المراقبة

| Variable | Description | الوصف | Required |
|----------|-------------|-------|----------|
| `NEXT_PUBLIC_SENTRY_DSN` | Sentry DSN (client-side) | DSN Sentry (جانب العميل) | No |
| `SENTRY_DSN` | Sentry DSN (server-side) | DSN Sentry (جانب الخادم) | No |

---

## 17. Service URLs

### روابط الخدمات

### Primary Service URLs (Current) | روابط الخدمات الرئيسية

| Variable | Service | Port | Description |
|----------|---------|------|-------------|
| `FIELD_MANAGEMENT_URL` | field-management-service | 3000 | Unified field operations |
| `USER_SERVICE_URL` | user-service | 3025 | Authentication & user management |
| `MARKETPLACE_SERVICE_URL` | marketplace-service | 3010 | Agricultural marketplace |
| `WEATHER_SERVICE_URL` | weather-service | 8092 | Weather data |
| `VEGETATION_ANALYSIS_URL` | vegetation-analysis-service | 8090 | Satellite & NDVI analysis |
| `ADVISORY_SERVICE_URL` | advisory-service | 8093 | Agricultural advisory |
| `CROP_INTELLIGENCE_URL` | crop-intelligence-service | 8095 | Crop health AI |
| `YIELD_PREDICTION_URL` | yield-prediction-service | 8098 | Yield estimation |
| `NOTIFICATION_SERVICE_URL` | notification-service | 8110 | Push notifications |
| `IOT_GATEWAY_URL` | iot-gateway | 8106 | IoT protocol gateway |
| `TASK_SERVICE_URL` | task-service | 8103 | Task management |
| `ASTRONOMICAL_SERVICE_URL` | astronomical-calendar | 8111 | Islamic calendar |
| `ALERT_SERVICE_URL` | alert-service | 8113 | Alert management |
| `FIELD_INTELLIGENCE_URL` | field-intelligence | 8120 | Field analytics |
| `CHAT_SERVICE_URL` | chat-service | 8114 | Chat & messaging |
| `KONG_URL` | kong | 8000 | API Gateway |
| `SAHOOL_API_URL` | kong | 8000 | Main API URL |

### Legacy URLs (Deprecated) | روابط قديمة (مهملة)

These URLs are maintained for backward compatibility and will be removed in v17.0.0:

| Variable | Replacement | Description |
|----------|-------------|-------------|
| `FIELDOPS_URL` | `FIELD_MANAGEMENT_URL` | Legacy field-ops |
| `WEATHER_URL` | `WEATHER_SERVICE_URL` | Legacy weather |
| `SATELLITE_URL` | `VEGETATION_ANALYSIS_URL` | Legacy satellite |
| `SATELLITE_SERVICE_URL` | `VEGETATION_ANALYSIS_URL` | Legacy satellite |
| `FERTILIZER_URL` | `ADVISORY_SERVICE_URL` | Legacy fertilizer |
| `IRRIGATION_URL` | `irrigation-smart:8094` | Legacy irrigation |
| `INDICATORS_URL` | `indicators-service:8091` | Indicators service |
| `CROP_HEALTH_URL` | `CROP_INTELLIGENCE_URL` | Legacy crop health |
| `AGRO_ADVISOR_URL` | `ADVISORY_SERVICE_URL` | Legacy agro advisor |
| `NDVI_URL` | `VEGETATION_ANALYSIS_URL` | Legacy NDVI |
| `NDVI_SERVICE_URL` | `VEGETATION_ANALYSIS_URL` | Legacy NDVI |

---

## 18. Backup & Disaster Recovery

### النسخ الاحتياطي والتعافي من الكوارث

### General Backup | النسخ الاحتياطي العام

| Variable | Description | الوصف | Required | Default |
|----------|-------------|-------|----------|---------|
| `BACKUP_DIR` | Base backup directory | دليل النسخ الاحتياطي الأساسي | No | `/backups` |
| `BACKUP_COMPRESSION` | Compression method | طريقة الضغط | No | `gzip` |
| `BACKUP_ENCRYPTION_ENABLED` | Enable encryption | تمكين التشفير | No | `true` |
| `BACKUP_ENCRYPTION_KEY` | Encryption key | مفتاح التشفير | **Yes*** | - |
| `BACKUP_ENCRYPTION_ALGORITHM` | Encryption algorithm | خوارزمية التشفير | No | `aes-256-cbc` |

*Required when BACKUP_ENCRYPTION_ENABLED=true

### WAL Archiving (PITR) | أرشفة WAL

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `WAL_ARCHIVE_ENABLED` | Enable WAL archiving | تمكين أرشفة WAL | `true` |
| `WAL_ARCHIVE_MODE` | Archive mode | وضع الأرشفة | `always` |
| `WAL_LEVEL` | WAL level | مستوى WAL | `replica` |
| `MAX_WAL_SENDERS` | Max WAL senders | أقصى مرسلي WAL | `3` |
| `WAL_RETENTION_DAYS` | WAL retention period | فترة الاحتفاظ بـ WAL | `7` |
| `BASE_BACKUP_RETENTION_DAYS` | Base backup retention | الاحتفاظ بالنسخة الأساسية | `30` |

### Retention Policies | سياسات الاحتفاظ

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `RETENTION_DAILY` | Daily backup retention (days) | الاحتفاظ بالنسخ اليومية | `7` |
| `RETENTION_WEEKLY` | Weekly backup retention (days) | الاحتفاظ بالنسخ الأسبوعية | `28` |
| `RETENTION_MONTHLY` | Monthly backup retention (days) | الاحتفاظ بالنسخ الشهرية | `365` |
| `RETENTION_MANUAL` | Manual backup retention (days) | الاحتفاظ بالنسخ اليدوية | `90` |

### S3/MinIO Backup Storage | تخزين النسخ الاحتياطية في S3/MinIO

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `S3_BACKUP_ENABLED` | Enable S3 backup | تمكين نسخ S3 | `true` |
| `S3_ENDPOINT` | S3/MinIO endpoint | نقطة نهاية S3/MinIO | `http://minio:9000` |
| `S3_BUCKET` | S3 backup bucket | دلو النسخ الاحتياطي | `sahool-backups` |
| `S3_ACCESS_KEY` | S3 access key | مفتاح وصول S3 | `${MINIO_ROOT_USER}` |
| `S3_SECRET_KEY` | S3 secret key | مفتاح S3 السري | `${MINIO_ROOT_PASSWORD}` |

### AWS S3 Off-Site Backup | نسخ AWS S3 خارج الموقع

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `AWS_S3_BACKUP_ENABLED` | Enable AWS S3 backup | تمكين نسخ AWS S3 | `false` |
| `AWS_S3_BACKUP_BUCKET` | AWS S3 bucket | دلو AWS S3 | `sahool-backups-offsite` |
| `AWS_S3_REGION` | AWS S3 region | منطقة AWS S3 | `eu-central-1` |
| `AWS_S3_STORAGE_CLASS` | S3 storage class | فئة تخزين S3 | `STANDARD_IA` |

### Disaster Recovery | التعافي من الكوارث

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `RTO_TARGET_HOURS` | Recovery Time Objective | هدف وقت الاستعادة | `6` |
| `RPO_TARGET_HOURS` | Recovery Point Objective | هدف نقطة الاستعادة | `24` |
| `DR_DRILL_SCHEDULE` | DR drill schedule (cron) | جدول تدريب DR | `0 0 1 */3 *` |
| `DR_CONTACT_EMAIL` | DR contact email | بريد اتصال DR | `dr-team@sahool.com` |

### Notification Settings | إعدادات الإشعارات

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `SLACK_NOTIFICATIONS_ENABLED` | Enable Slack notifications | تمكين إشعارات Slack | `false` |
| `SLACK_WEBHOOK_URL` | Slack webhook URL | رابط webhook لـ Slack | - |
| `EMAIL_NOTIFICATIONS_ENABLED` | Enable email notifications | تمكين إشعارات البريد | `false` |
| `BACKUP_EMAIL_TO` | Backup notification email | بريد إشعارات النسخ الاحتياطي | `admin@sahool.com` |

---

## 19. Development & Debug

### التطوير والتصحيح

**WARNING**: Set these to `false` in production environments!

| Variable | Description | الوصف | Default | Production |
|----------|-------------|-------|---------|------------|
| `DEBUG` | Enable debug mode | تمكين وضع التصحيح | `false` | `false` |
| `RELOAD` | Enable hot reload | تمكين إعادة التحميل الساخن | `false` | `false` |
| `SQL_ECHO` | Echo SQL queries | عرض استعلامات SQL | `false` | `false` |
| `DB_ECHO` | Echo database operations | عرض عمليات قاعدة البيانات | `false` | `false` |
| `ALLOW_DEV_DEFAULTS` | Allow development defaults | السماح بالقيم الافتراضية للتطوير | `false` | `false` |
| `SEED_DEMO_DATA` | Seed demo data on startup | زرع بيانات تجريبية | `false` | `false` |
| `CREATE_DB_SCHEMA` | Create database schema | إنشاء مخطط قاعدة البيانات | `false` | `false` |
| `INCLUDE_STACK_TRACE` | Include stack traces in errors | تضمين تتبع المكدس | `false` | `false` |
| `LOG_REQUEST_BODY` | Log request bodies | تسجيل نصوص الطلبات | `false` | `false` |

### Demo Mode | وضع العرض التوضيحي

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `DEMO_MODE` | Demo mode type | نوع وضع العرض | `continuous` |
| `DEMO_INTERVAL_SECONDS` | Demo data interval | فترة بيانات العرض | `30` |
| `DEMO_TENANT_ID` | Demo tenant ID | معرف مستأجر العرض | `a0000000-0000-0000-0000-000000000001` |
| `DEMO_USER_ID` | Demo user ID | معرف مستخدم العرض | `b0000000-0000-0000-0000-000000000001` |
| `DEMO_BATCH_COUNT` | Demo batch count | عدد دفعات العرض | `100` |

### MCP Server Configuration | تكوين خادم MCP

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `MCP_SERVER_HOST` | MCP server host | مضيف خادم MCP | `0.0.0.0` |
| `MCP_SERVER_PORT` | MCP server port | منفذ خادم MCP | `8200` |

---

## Rate Limiting Configuration

### تكوين تحديد المعدل

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `RATE_LIMIT_ENABLED` | Enable rate limiting | تمكين تحديد المعدل | `true` |
| `RATE_LIMIT_REQUESTS` | General rate limit | حد المعدل العام | `100` |
| `RATE_LIMIT_WINDOW_SECONDS` | Rate limit window | نافذة تحديد المعدل | `60` |

### Tier-Based Rate Limits | حدود المعدل حسب المستوى

| Tier | RPM | RPH | Burst |
|------|-----|-----|-------|
| Free | `RATE_LIMIT_FREE_RPM=30` | `RATE_LIMIT_FREE_RPH=500` | `RATE_LIMIT_FREE_BURST=5` |
| Standard | `RATE_LIMIT_STANDARD_RPM=60` | `RATE_LIMIT_STANDARD_RPH=2000` | `RATE_LIMIT_STANDARD_BURST=10` |
| Premium | `RATE_LIMIT_PREMIUM_RPM=120` | `RATE_LIMIT_PREMIUM_RPH=5000` | `RATE_LIMIT_PREMIUM_BURST=20` |
| Internal | `RATE_LIMIT_INTERNAL_RPM=1000` | `RATE_LIMIT_INTERNAL_RPH=50000` | `RATE_LIMIT_INTERNAL_BURST=100` |

---

## Cache Configuration

### تكوين التخزين المؤقت

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `CACHE_ENABLED` | Enable caching | تمكين التخزين المؤقت | `true` |
| `CACHE_TTL_SECONDS` | Default cache TTL | TTL التخزين المؤقت الافتراضي | `300` |
| `CACHE_MAX_SIZE` | Max cache entries | أقصى إدخالات التخزين المؤقت | `10000` |
| `CACHE_TTL_USER_DATA` | User data cache TTL | TTL بيانات المستخدم | `600` |
| `CACHE_TTL_FIELD_DATA` | Field data cache TTL | TTL بيانات الحقل | `300` |
| `CACHE_TTL_WEATHER_DATA` | Weather data cache TTL | TTL بيانات الطقس | `1800` |
| `CACHE_TTL_SATELLITE_DATA` | Satellite data cache TTL | TTL بيانات الأقمار الصناعية | `3600` |

---

## API Configuration

### تكوين API

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `DEFAULT_PAGE_SIZE` | Default pagination size | حجم الترقيم الافتراضي | `50` |
| `MAX_PAGE_SIZE` | Maximum page size | أقصى حجم صفحة | `1000` |
| `ENABLE_STREAMING_RESPONSES` | Enable streaming | تمكين البث | `true` |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins | أصول CORS المسموحة | `http://localhost:3000,...` |

---

## Application Limits

### حدود التطبيق

| Variable | Description | الوصف | Default |
|----------|-------------|-------|---------|
| `MAX_NOTIFICATIONS_PER_HOUR` | Max notifications per hour | أقصى إشعارات في الساعة | `100` |
| `MAX_RETRIES` | Max retry attempts | أقصى محاولات إعادة | `3` |
| `RETRY_DELAY_SECONDS` | Retry delay | تأخير إعادة المحاولة | `5` |
| `MAINTENANCE_CHECK_INTERVAL` | Maintenance check interval | فترة فحص الصيانة | `3600` |
| `PLAN_LIMITS` | Plan limits JSON | حدود الخطة (JSON) | `{"free":{"fields":10},...}` |
| `TRIAL_DAYS` | Trial period days | أيام الفترة التجريبية | `14` |

---

## Quick Reference - Environment Files

### مرجع سريع - ملفات البيئة

| File | Purpose | الغرض |
|------|---------|-------|
| `.env.example` | Main environment template | قالب البيئة الرئيسي |
| `.env.development.template` | Development environment (no TLS) | بيئة التطوير (بدون TLS) |
| `apps/admin/.env.example` | Admin portal configuration | تكوين بوابة الإدارة |
| `apps/web/.env.example` | Web dashboard configuration | تكوين لوحة تحكم الويب |
| `apps/mobile/.env.example` | Mobile app configuration | تكوين تطبيق الجوال |
| `apps/mobile/sahool_field_app/.env.example` | Field app configuration | تكوين تطبيق الحقل |
| `apps/mobile/sahol_atmosphere/.env.example` | Atmosphere app configuration | تكوين تطبيق الأجواء |

---

## Security Best Practices

### أفضل ممارسات الأمان

1. **Never commit secrets** - استخدم ملفات `.env` المحلية فقط
2. **Use strong passwords** - استخدم كلمات مرور قوية (32+ حرفاً)
3. **Rotate credentials regularly** - قم بتدوير الاعتمادات بانتظام
4. **Enable TLS in production** - مكّن TLS في الإنتاج
5. **Use Vault for production** - استخدم Vault للإنتاج
6. **Set DEBUG=false in production** - اضبط DEBUG على false في الإنتاج

### Generating Secure Values | توليد قيم آمنة

```bash
# Generate secure password (32 characters)
openssl rand -base64 32

# Generate encryption key
python -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"

# Generate JWT secret
openssl rand -hex 32
```

---

_Last Updated: January 2026_
_Version: 16.0.0_
