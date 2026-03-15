# SAHOOL Platform - Versions & Dependencies | الإصدارات والاعتماديات

> Comprehensive documentation of all platform versions, libraries, and dependencies

**Platform Version**: 16.0.0
**Last Updated**: March 2026

---

## Table of Contents | جدول المحتويات

1. [Platform Overview](#platform-overview)
2. [Infrastructure Versions](#infrastructure-versions)
3. [Python Dependencies](#python-dependencies)
4. [Node.js Dependencies](#nodejs-dependencies)
5. [Flutter/Dart Dependencies](#flutterdart-dependencies)
6. [Development Tools](#development-tools)
7. [Critical Constraints](#critical-constraints)
8. [Version Matrix](#version-matrix)

---

## Platform Overview | نظرة عامة على المنصة

### Runtime Requirements | متطلبات التشغيل

| Component | Version | Notes |
|-----------|---------|-------|
| **Python** | 3.11+ | Required for all backend services |
| **Node.js** | 20.0.0+ | LTS version required |
| **Flutter** | 3.27.x | With Dart SDK >=3.2.0 |
| **npm** | 10.9.0 | Package manager |
| **Docker** | v2+ | Container runtime |

### Platform Statistics | إحصائيات المنصة

| Metric | Count |
|--------|-------|
| Python Services | 50+ |
| Node.js Services | 11 |
| Flutter Apps | 3 |
| Shared Packages | 15+ |
| Total Dependencies | 250+ |

---

## Infrastructure Versions | إصدارات البنية التحتية

### Database & Storage | قواعد البيانات والتخزين

| Service | Version | Image | Purpose |
|---------|---------|-------|---------|
| **PostgreSQL** | 16 | `postgis/postgis:16-3.4` | Primary database with PostGIS |
| **PostGIS** | 3.4 | (included) | Geospatial extension |
| **PgBouncer** | latest | `edoburu/pgbouncer` | Connection pooling |
| **Redis** | 7.4 | `redis:7.4-alpine` | Caching & sessions |
| **MinIO** | 2024-05-28 | `minio/minio:RELEASE.2024-05-28T17-19-04Z` | Object storage |
| **Milvus** | 2.5.27 | `milvusdb/milvus:v2.5.27` | Vector database |
| **etcd** | 3.5.18 | `quay.io/coreos/etcd:v3.5.18` | Milvus metadata storage |

### Messaging & Events | الرسائل والأحداث

| Service | Version | Image | Purpose |
|---------|---------|-------|---------|
| **NATS** | 2.10.24 | `nats:2.10.24-alpine` | Event streaming |
| **NATS Exporter** | 0.15.0 | `natsio/prometheus-nats-exporter:0.15.0` | Metrics export |

### API Gateway | بوابة API

| Service | Version | Image | Purpose |
|---------|---------|-------|---------|
| **Kong** | 3.5 | `kong:3.5-alpine` | API Gateway |
| **Konga** | 0.14.9 | `pantsel/konga:0.14.9` | Kong Admin UI |

### Monitoring | المراقبة

| Service | Version | Image | Purpose |
|---------|---------|-------|---------|
| **PostgreSQL Exporter** | 0.15.0 | `prometheuscommunity/postgres-exporter:v0.15.0` | DB metrics |
| **Redis Exporter** | 1.55.0 | `oliver006/redis_exporter:v1.55.0` | Redis metrics |

### Kubernetes & Orchestration | Kubernetes والتنسيق

| Component | Version | Notes |
|-----------|---------|-------|
| **Kubernetes (EKS)** | 1.28 | AWS managed |
| **Helm** | 3.x | Chart deployment |
| **Terraform** | >= 1.5.0 | Infrastructure as Code |
| **AWS Provider** | ~> 5.0 | Terraform provider |

---

## Python Dependencies | اعتماديات Python

### Core Framework | الإطار الأساسي

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `fastapi` | 0.126.0 | Web framework | إطار الويب |
| `starlette` | >=0.49.1 | ASGI toolkit | أدوات ASGI |
| `uvicorn[standard]` | >=0.27.0,<1.0.0 | ASGI server | خادم ASGI |
| `pydantic` | 2.9.2 | Data validation | التحقق من البيانات |
| `pydantic-settings` | 2.7.1 | Settings management | إدارة الإعدادات |

### Database & ORM | قاعدة البيانات و ORM

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `asyncpg` | 0.30.0 | Async PostgreSQL driver | تشغيل PostgreSQL غير متزامن |
| `tortoise-orm` | 0.21.7 | Async ORM | ORM غير متزامن |
| `sqlalchemy` | >=2.0.0 | SQL toolkit | أدوات SQL |
| `psycopg2-binary` | 2.9.10 | PostgreSQL adapter | محول PostgreSQL |
| `alembic` | 1.14.0 | Database migrations | ترحيل قواعد البيانات |
| `aerich` | 0.7.2 | Tortoise migrations | ترحيل Tortoise |

### Messaging & Caching | الرسائل والتخزين المؤقت

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `nats-py` | 2.9.0 | NATS client | عميل NATS |
| `redis[hiredis]` | 5.2.1 | Redis client | عميل Redis |
| `celery` | 5.4.0 | Task queue | قائمة المهام |
| `kombu` | 5.4.2 | Messaging library | مكتبة الرسائل |
| `aiomqtt` | 2.3.0 | MQTT client (IoT) | عميل MQTT |

### HTTP & Networking | HTTP والشبكات

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `httpx` | 0.28.1 | Async HTTP client | عميل HTTP غير متزامن |
| `aiohttp` | >=3.11.12 | Async HTTP | HTTP غير متزامن |
| `python-multipart` | 0.0.18 | File uploads | رفع الملفات |
| `aiofiles` | >=24.1.0 | Async file I/O | ملفات غير متزامنة |

### Authentication & Security | المصادقة والأمان

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `python-jose[cryptography]` | 3.4.0 | JWT handling | معالجة JWT |
| `passlib[bcrypt]` | 1.7.4 | Password hashing | تشفير كلمات المرور |
| `PyJWT` | 2.10.1 | JWT tokens | رموز JWT |
| `bcrypt` | 4.2.1 | Password encryption | تشفير كلمات المرور |
| `cryptography` | >=41.0.0 | Cryptographic primitives | التشفير الأساسي |

### Observability | المراقبة

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `prometheus-client` | 0.21.1 | Metrics export | تصدير المقاييس |
| `structlog` | 24.4.0 | Structured logging | التسجيل المنظم |
| `opentelemetry-api` | 1.29.0 | Tracing API | API التتبع |
| `opentelemetry-sdk` | 1.29.0 | Tracing SDK | SDK التتبع |
| `opentelemetry-instrumentation-fastapi` | 0.50b0 | FastAPI tracing | تتبع FastAPI |
| `python-json-logger` | >=2.0.7 | JSON logging | تسجيل JSON |

### AI/ML Stack | مكدس الذكاء الاصطناعي

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `tensorflow-cpu` | 2.18.0 | Machine learning | التعلم الآلي |
| `numpy` | >=1.26.0,<2.0.0 | Numerical computing | الحوسبة العددية |
| `Pillow` | 11.0.0 | Image processing | معالجة الصور |
| `scikit-learn` | >=1.0.0 | ML algorithms | خوارزميات التعلم |
| `pandas` | >=2.0.0 | Data analysis | تحليل البيانات |

### Geospatial | الجغرافيا المكانية

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `shapely` | 2.0.6 | Geometric objects | الكائنات الهندسية |
| `rasterio` | 1.4.3 | Raster data | بيانات النقطية |
| `pyproj` | 3.7.0 | Coordinate transformation | تحويل الإحداثيات |

### Notifications | الإشعارات

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `firebase-admin` | 6.6.0 | Firebase integration | تكامل Firebase |
| `twilio` | 9.3.7 | SMS gateway | بوابة SMS |
| `sendgrid` | 6.11.0 | Email service | خدمة البريد |

### Testing | الاختبارات

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `pytest` | 8.3.4 | Test framework | إطار الاختبار |
| `pytest-asyncio` | 0.24.0 | Async testing | اختبار غير متزامن |
| `pytest-cov` | 4.1.0 | Code coverage | تغطية الكود |
| `pytest-mock` | 3.12.0 | Mocking | المحاكاة |
| `pytest-xdist` | 3.5.0 | Parallel testing | اختبار متوازي |

### Development Tools | أدوات التطوير

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `ruff` | 0.8.4 | Linting & formatting | التنسيق والفحص |
| `black` | 24.10.0 | Code formatting | تنسيق الكود |
| `isort` | 5.13.2 | Import sorting | ترتيب الاستيرادات |
| `mypy` | >=1.14.0 | Type checking | فحص الأنواع |
| `pre-commit` | 4.0.1 | Git hooks | خطافات Git |

---

## Node.js Dependencies | اعتماديات Node.js

### Core Frameworks | الأطر الأساسية

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `next` | ^15.5.9 / ^16.1.4 | React framework | إطار React |
| `react` | ^19.0.0 | UI library | مكتبة واجهة المستخدم |
| `react-dom` | ^19.0.0 | React renderer | عارض React |
| `@nestjs/core` | ^10.4.15 | NestJS framework | إطار NestJS |
| `@nestjs/common` | ^10.4.15 | NestJS common | NestJS المشترك |
| `@nestjs/platform-express` | ^10.4.15 | Express adapter | محول Express |
| `express` | ^4.21.2 | Web server | خادم الويب |
| `typescript` | 5.7.2 | TypeScript language | لغة TypeScript |

### Database & ORM | قاعدة البيانات و ORM

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `@prisma/client` | ^5.22.0 | Prisma ORM client | عميل Prisma ORM |
| `prisma` | ^5.22.0 | Prisma CLI | أداة Prisma |
| `typeorm` | ^0.3.20 | TypeORM | TypeORM |
| `pg` | ^8.13.1 | PostgreSQL driver | تشغيل PostgreSQL |

### HTTP & API | HTTP و API

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `axios` | ^1.7.9 | HTTP client | عميل HTTP |
| `@nestjs/swagger` | ^8.1.0 | API documentation | توثيق API |
| `nats` | ^2.28.2 | NATS client | عميل NATS |
| `socket.io` | ^4.8.1 | WebSocket server | خادم WebSocket |

### Authentication | المصادقة

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `jsonwebtoken` | ^9.0.2 | JWT tokens | رموز JWT |
| `passport` | ^0.7.0 | Auth middleware | وسيط المصادقة |
| `passport-jwt` | ^4.0.1 | JWT strategy | استراتيجية JWT |
| `@nestjs/jwt` | ^10.2.0 | NestJS JWT | NestJS JWT |
| `bcryptjs` | ^2.4.3 | Password hashing | تشفير كلمات المرور |
| `jose` | ^5.9.6 | JWT utilities | أدوات JWT |

### Validation | التحقق

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `class-validator` | ^0.14.1 | Validation decorators | مصممات التحقق |
| `class-transformer` | ^0.5.1 | Object transformation | تحويل الكائنات |
| `zod` | ^3.23.8 | Schema validation | التحقق من المخطط |

### State & Data Fetching | الحالة وجلب البيانات

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `@tanstack/react-query` | ^5.90.14 | Data fetching | جلب البيانات |
| `rxjs` | ^7.8.1 | Reactive programming | البرمجة التفاعلية |

### Caching | التخزين المؤقت

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `ioredis` | ^5.4.2 | Redis client | عميل Redis |
| `redis` | ^4.7.0 | Redis client | عميل Redis |

### UI Components | مكونات واجهة المستخدم

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `tailwindcss` | ^3.4.17 | Utility CSS | CSS الأدوات |
| `tailwind-merge` | ^2.6.0 | CSS utilities | أدوات CSS |
| `lucide-react` | ^0.468.0 | Icons | الأيقونات |
| `recharts` | ^2.14.1 | Charts | الرسوم البيانية |
| `leaflet` | ^1.9.4 | Maps | الخرائط |
| `react-leaflet` | ^4.2.1 | React maps | خرائط React |
| `maplibre-gl` | ^4.7.1 | Vector maps | خرائط متجهة |

### Testing | الاختبارات

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `vitest` | ^3.2.4 | Test runner | منفذ الاختبارات |
| `jest` | ^29.7.0 | Test framework | إطار الاختبار |
| `@testing-library/react` | ^16.3.0 | Component testing | اختبار المكونات |
| `@playwright/test` | ^1.57.0 | E2E testing | اختبار E2E |
| `supertest` | ^7.1.4 | HTTP testing | اختبار HTTP |

### Build Tools | أدوات البناء

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `vite` | ^6.4.1 | Build tool | أداة البناء |
| `@vitejs/plugin-react` | ^4.5.2 | Vite React plugin | إضافة Vite React |
| `tsup` | ^8.0.1 | TypeScript bundler | حزم TypeScript |
| `tsx` | ^4.19.0 | TS executor | منفذ TypeScript |

### Code Quality | جودة الكود

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `@biomejs/biome` | ^1.9.4 | Linter/Formatter | المنسق والفاحص |
| `eslint` | ^9.39.2 | Linting | الفحص |
| `oxlint` | ^0.12.0 | Fast linting | فحص سريع |
| `knip` | ^5.40.0 | Dead code finder | كشف الكود الميت |
| `madge` | ^8.0.0 | Circular deps | التبعيات الدائرية |
| `typedoc` | ^0.27.6 | Documentation | التوثيق |

### Utilities | الأدوات المساعدة

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `uuid` | ^11.0.3 | UUID generation | توليد UUID |
| `date-fns` | ^4.1.0 | Date utilities | أدوات التاريخ |
| `js-cookie` | ^3.0.5 | Cookie management | إدارة الكوكيز |
| `next-intl` | ^3.26.3 | Internationalization | التدويل |
| `clsx` | ^2.1.1 | Class composition | تركيب الفئات |

### Monitoring | المراقبة

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `@sentry/nextjs` | ^8.0.0 | Error tracking | تتبع الأخطاء |
| `nestjs-pino` | ^4.1.0 | Logging | التسجيل |
| `pino-http` | ^10.3.0 | HTTP logging | تسجيل HTTP |

---

## Flutter/Dart Dependencies | اعتماديات Flutter/Dart

### SDK Requirements | متطلبات SDK

| Component | Version | الوصف |
|-----------|---------|-------|
| **Flutter SDK** | 3.27.x | إطار Flutter |
| **Dart SDK** | >=3.2.0 <4.0.0 | لغة Dart |

### State Management | إدارة الحالة

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `flutter_riverpod` | ^2.6.1 | State management | إدارة الحالة |
| `riverpod_annotation` | ^2.6.1 | Riverpod codegen | توليد كود Riverpod |
| `riverpod_generator` | ^2.6.1 | Generator | المولد |

### Local Database | قاعدة البيانات المحلية

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `drift` | ^2.24.0 | SQL database | قاعدة بيانات SQL |
| `drift_dev` | ^2.24.0 | Drift generator | مولد Drift |
| `sqlcipher_flutter_libs` | ^0.6.1 | Encrypted SQLite | SQLite مشفر |
| `sqlite3` | ^2.4.6 | SQLite bindings | ربط SQLite |

### Networking | الشبكات

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `dio` | ^5.7.0 | HTTP client | عميل HTTP |
| `http` | ^1.2.2 | HTTP client | عميل HTTP |
| `connectivity_plus` | ^6.1.1 | Network detection | كشف الشبكة |
| `socket_io_client` | ^2.0.3+1 | WebSocket | WebSocket |

### Security | الأمان

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `flutter_secure_storage` | ^9.2.2 | Secure storage | تخزين آمن |
| `local_auth` | ^2.3.0 | Biometric auth | المصادقة البيومترية |
| `crypto` | ^3.0.6 | Encryption | التشفير |
| `safe_device` | ^1.1.7 | Root detection | كشف الروت |
| `secure_application` | ^4.1.0 | Screenshot prevention | منع لقطات الشاشة |

### Maps & Location | الخرائط والموقع

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `flutter_map` | ^8.1.1 | Map rendering | عرض الخرائط |
| `flutter_map_cache` | ^2.0.0 | Offline maps | خرائط أوفلاين |
| `geolocator` | ^13.0.2 | GPS location | موقع GPS |
| `latlong2` | ^0.9.1 | Coordinates | الإحداثيات |

### UI Components | مكونات واجهة المستخدم

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `flutter_svg` | ^2.0.16 | SVG rendering | عرض SVG |
| `cached_network_image` | ^3.4.1 | Image caching | تخزين الصور |
| `fl_chart` | ^0.69.2 | Charts | الرسوم البيانية |
| `table_calendar` | ^3.0.9 | Calendar widget | أداة التقويم |
| `cupertino_icons` | ^1.0.8 | iOS icons | أيقونات iOS |

### Camera & Media | الكاميرا والوسائط

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `image_picker` | ^1.1.2 | Image selection | اختيار الصور |
| `camera` | ^0.11.0+2 | Camera capture | التقاط الكاميرا |
| `mobile_scanner` | ^6.0.2 | QR/Barcode scanner | ماسح QR |
| `image` | ^4.3.0 | Image processing | معالجة الصور |
| `record` | 5.0.5 | Audio recording | تسجيل الصوت |

### Audio & Speech | الصوت والكلام

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `speech_to_text` | ^7.0.0 | Voice recognition | التعرف على الصوت |
| `flutter_tts` | ^4.2.0 | Text-to-speech | النص إلى كلام |

### Firebase | Firebase

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `firebase_core` | ^3.8.1 | Firebase core | نواة Firebase |
| `firebase_messaging` | ^15.1.6 | Cloud messaging | الرسائل السحابية |

### Navigation | التنقل

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `go_router` | ^14.6.2 | Routing | التوجيه |
| `app_links` | ^3.5.1 | Deep linking | الروابط العميقة |

### Utilities | الأدوات المساعدة

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `uuid` | ^4.5.1 | UUID generation | توليد UUID |
| `intl` | ^0.19.0 | Internationalization | التدويل |
| `equatable` | ^2.0.7 | Value equality | المساواة بالقيمة |
| `jiffy` | ^6.3.1 | Date/time | التاريخ والوقت |
| `flutter_dotenv` | ^5.2.1 | Environment vars | متغيرات البيئة |
| `shared_preferences` | ^2.3.3 | Key-value storage | تخزين مفتاح-قيمة |

### Background & Notifications | الخلفية والإشعارات

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `workmanager` | ^0.6.0 | Background tasks | مهام الخلفية |
| `flutter_local_notifications` | ^18.0.1 | Local notifications | الإشعارات المحلية |

### Monitoring | المراقبة

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `sentry_flutter` | ^8.11.0 | Crash reporting | تقارير الأعطال |

### Code Generation | توليد الكود

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `build_runner` | ^2.4.13 | Code generator | مولد الكود |
| `freezed` | 2.5.8 | Immutable classes | فئات غير قابلة للتغيير |
| `freezed_annotation` | ^2.4.4 | Freezed annotations | تعليقات Freezed |
| `json_serializable` | ^6.9.0 | JSON serialization | تسلسل JSON |
| `json_annotation` | ^4.9.0 | JSON annotations | تعليقات JSON |

### Testing | الاختبارات

| Package | Version | Purpose | الوصف |
|---------|---------|---------|-------|
| `flutter_test` | SDK | Testing framework | إطار الاختبار |
| `integration_test` | SDK | Integration tests | اختبارات التكامل |
| `mocktail` | ^1.0.4 | Mocking | المحاكاة |
| `fake_async` | ^1.3.1 | Async testing | اختبار غير متزامن |
| `flutter_lints` | ^5.0.0 | Linting rules | قواعد الفحص |

---

## Development Tools | أدوات التطوير

### CI/CD Pipeline | خط أنابيب CI/CD

| Tool | Version | Purpose |
|------|---------|---------|
| **GitHub Actions** | v4 | CI/CD automation |
| **Docker Buildx** | v3 | Multi-platform builds |
| **BuildKit** | 0.12.5 | Docker build |
| **Trivy** | 0.28.0 | Security scanning |
| **CodeQL** | v3 | Code analysis |

### Linting & Formatting | الفحص والتنسيق

| Tool | Language | Version |
|------|----------|---------|
| **Ruff** | Python | 0.8.4 |
| **Black** | Python | 24.10.0 |
| **isort** | Python | 5.13.2 |
| **Biome** | JS/TS | 1.9.4 |
| **ESLint** | JS/TS | 9.39.2 |
| **Oxlint** | JS/TS | 0.12.0 |

### Documentation | التوثيق

| Tool | Language | Version |
|------|----------|---------|
| **TypeDoc** | TypeScript | 0.27.6 |
| **MkDocs** | Python | - |

---

## Critical Constraints | القيود الحرجة

### ⚠️ Version Pinning | تثبيت الإصدارات

| Package | Constraint | Reason |
|---------|------------|--------|
| **NumPy** | <2.0.0 | TensorFlow 2.18 compatibility |
| **Freezed** | 2.5.8 | Dart 3.6.0 compatibility |
| **Record** | 5.0.5 | record_linux compatibility |
| **build_runner** | 2.4.13 | Dart 3.6.0 compatibility |

### 🔒 Security Updates | تحديثات الأمان

| CVE | Package | Fixed Version |
|-----|---------|---------------|
| CVE-2026-26190 | Milvus | 2.5.27 |
| CVE-2025-53643 | aiohttp | >=3.11.12 |
| CVE-2024-33663 | python-jose | 3.4.0 |
| CVE-2024-33664 | python-jose | 3.4.0 |

### ❌ Incompatible Packages | الحزم غير المتوافقة

| Package | Issue | Alternative |
|---------|-------|-------------|
| MapLibre GL (Flutter) | Requires Java 21, NDK 28 | flutter_map |
| Mockito (Dart) | Requires Dart 3.7.0+ | mocktail |
| Google Fonts (Flutter) | Large APK, slow startup | Local fonts |

---

## Version Matrix | مصفوفة الإصدارات

### Complete Stack | المكدس الكامل

| Layer | Technology | Version |
|-------|------------|---------|
| **Platform** | SAHOOL | 16.0.0 |
| **Database** | PostgreSQL + PostGIS | 16 + 3.4 |
| **Cache** | Redis | 7.4 |
| **Events** | NATS | 2.10.24 |
| **Gateway** | Kong | 3.5 |
| **Backend (Python)** | FastAPI | 0.126.0 |
| **Backend (Node.js)** | NestJS | 10.4.15 |
| **Frontend** | Next.js + React | 15.5.9 + 19.0.0 |
| **Mobile** | Flutter | 3.27.x |
| **ORM (Python)** | Tortoise/SQLAlchemy | 0.21.7/2.0+ |
| **ORM (Node.js)** | Prisma | 5.22.0 |
| **ORM (Flutter)** | Drift + SQLCipher | 2.24.0 + 0.6.1 |
| **Vector DB** | Milvus | 2.5.27 |
| **Metadata Store** | etcd | 3.5.18 |
| **ML** | TensorFlow | 2.18.0 |
| **Kubernetes** | EKS | 1.28 |
| **IaC** | Terraform | >=1.5.0 |

---

## Upgrade Guidelines | إرشادات الترقية

### Before Upgrading | قبل الترقية

1. **Check compatibility matrix** - تحقق من مصفوفة التوافق
2. **Review breaking changes** - راجع التغييرات الجذرية
3. **Test in staging first** - اختبر في البيئة التجريبية أولاً
4. **Backup database** - انسخ قاعدة البيانات احتياطياً

### Critical Dependencies | الاعتماديات الحرجة

```bash
# Python - Do NOT upgrade NumPy to 2.x
pip install "numpy>=1.26.0,<2.0.0"

# Flutter - Pin freezed version
flutter pub add freezed:2.5.8 --dev

# Node.js - Use exact TypeScript version
npm install typescript@5.7.2 --save-exact
```

---

**Document Version**: 1.0
**Last Updated**: March 2026
**Maintained By**: SAHOOL Platform Team
