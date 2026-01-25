# Makefile Commands Reference | مرجع أوامر Makefile

> Complete reference for all SAHOOL Platform Makefile commands
> مرجع شامل لجميع أوامر Makefile في منصة سهول

**Version**: 2.0.0
**Last Updated**: January 2026

---

## Table of Contents | الفهرس

1. [Quick Reference](#quick-reference--مرجع-سريع)
2. [Development Commands](#development-commands--أوامر-التطوير)
3. [Docker Management](#docker-management--إدارة-docker)
4. [Database Commands](#database-commands--أوامر-قاعدة-البيانات)
5. [Testing Commands](#testing-commands--أوامر-الاختبارات)
6. [Mobile Development](#mobile-development--تطوير-الجوال)
7. [Infrastructure Commands](#infrastructure-commands--أوامر-البنية-التحتية)
8. [Monitoring Commands](#monitoring-commands--أوامر-المراقبة)
9. [Code Quality Commands](#code-quality-commands--أوامر-جودة-الكود)
10. [Development Tools](#development-tools--أدوات-التطوير)
11. [CI/CD Commands](#cicd-commands--أوامر-التكامل-المستمر)
12. [Utility Commands](#utility-commands--أوامر-مساعدة)
13. [Aliases & Quick Start](#aliases--quick-start--الاختصارات-والبدء-السريع)
14. [Environment Variables](#environment-variables--متغيرات-البيئة)

---

## Quick Reference | مرجع سريع

| Command | Description | الوصف |
|---------|-------------|-------|
| `make help` | Show all available commands | عرض جميع الأوامر المتاحة |
| `make dev` | Start full development environment | بدء بيئة التطوير الكاملة |
| `make quickstart` | Quick start for new developers | بدء سريع للمطورين الجدد |
| `make status` | Show service status and URLs | عرض حالة الخدمات والروابط |
| `make health` | Check health of all services | فحص صحة جميع الخدمات |

---

## Development Commands | أوامر التطوير

### `make dev`

**Description | الوصف**: Start full development environment with all services.
بدء بيئة التطوير الكاملة مع جميع الخدمات.

**Usage | الاستخدام**:
```bash
make dev
```

**What it does | ماذا يفعل**:
1. Starts all Docker containers from `docker-compose.yml`
2. Displays service status and URLs
3. Confirms environment is ready

**Output | المخرجات**:
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- NATS: `localhost:4222`
- Kong API Gateway: `http://localhost:8000`
- Web Application: `http://localhost:3000`

---

### `make dev-starter`

**Description | الوصف**: Start only starter package services (minimal setup).
بدء حزمة المبتدئين فقط (الإعداد الأساسي).

**Usage | الاستخدام**:
```bash
make dev-starter
```

**Services Included | الخدمات المتضمنة**:
- PostgreSQL, Redis, NATS
- Field Core, Weather Service, Advisory Service

**Best For | الأفضل لـ**:
- Local development with minimal resources
- Testing core functionality
- New developer onboarding

---

### `make dev-professional`

**Description | الوصف**: Start professional package with extended services.
بدء حزمة الاحترافية مع الخدمات الموسعة.

**Usage | الاستخدام**:
```bash
make dev-professional
```

**Services Included | الخدمات المتضمنة**:
- All starter services
- NDVI processing, Crop intelligence
- Irrigation smart, Yield prediction

---

### `make dev-enterprise`

**Description | الوصف**: Start all enterprise services for full platform testing.
بدء جميع الخدمات المتقدمة لاختبار المنصة الكاملة.

**Usage | الاستخدام**:
```bash
make dev-enterprise
```

**Services Included | الخدمات المتضمنة**:
- All professional services
- Marketplace, Community chat
- Advanced analytics, Multi-tenant support

---

## Docker Management | إدارة Docker

### `make build`

**Description | الوصف**: Build all Docker images in parallel for faster builds.
بناء جميع صور Docker بالتوازي لبناء أسرع.

**Usage | الاستخدام**:
```bash
make build
```

**Options | الخيارات**:
```bash
# Force rebuild without cache
docker compose build --no-cache

# Build specific service
docker compose build field_ops
```

---

### `make build-python`

**Description | الوصف**: Build only Python/FastAPI service images.
بناء صور خدمات Python/FastAPI فقط.

**Usage | الاستخدام**:
```bash
make build-python
```

**Services Built | الخدمات المبنية**:
- field_ops, weather_core, ndvi_engine
- crop_health_ai, virtual_sensors, yield_engine
- agro_advisor, alert_service, astronomical_calendar
- billing_core, fertilizer_advisor, crop_health
- ai_advisor, agro_rules

---

### `make build-node`

**Description | الوصف**: Build only Node.js/NestJS service images.
بناء صور خدمات Node.js/NestJS فقط.

**Usage | الاستخدام**:
```bash
make build-node
```

**Services Built | الخدمات المبنية**:
- crop_growth_model, disaster_assessment
- lai_estimation, yield_prediction
- marketplace_service, community_chat
- field_core, iot_service

---

### `make up`

**Description | الوصف**: Start all services defined in docker-compose.yml.
تشغيل جميع الخدمات المعرفة في docker-compose.yml.

**Usage | الاستخدام**:
```bash
make up
```

---

### `make down`

**Description | الوصف**: Stop all running services gracefully.
إيقاف جميع الخدمات قيد التشغيل بشكل آمن.

**Usage | الاستخدام**:
```bash
make down
```

---

### `make down-volumes`

**Description | الوصف**: Stop services and remove all volumes (deletes data).
إيقاف الخدمات وحذف جميع البيانات.

**Usage | الاستخدام**:
```bash
make down-volumes
```

**Warning | تحذير**: This command deletes all data including database contents!
هذا الأمر يحذف جميع البيانات بما في ذلك محتويات قاعدة البيانات!

---

### `make restart`

**Description | الوصف**: Restart all services (down + up).
إعادة تشغيل جميع الخدمات.

**Usage | الاستخدام**:
```bash
make restart
```

---

### `make logs`

**Description | الوصف**: View logs from all services in real-time.
عرض سجلات جميع الخدمات في الوقت الفعلي.

**Usage | الاستخدام**:
```bash
make logs
```

**Tips | نصائح**:
```bash
# Filter by service
docker compose logs -f field_ops

# Last 100 lines
docker compose logs --tail 100
```

---

### `make logs-service`

**Description | الوصف**: View logs for a specific service.
عرض سجلات خدمة محددة.

**Usage | الاستخدام**:
```bash
make logs-service SERVICE=field_ops
make logs-service SERVICE=postgres
make logs-service SERVICE=kong
```

**Required Parameters | المعاملات المطلوبة**:
- `SERVICE`: Name of the service to view logs for

---

## Database Commands | أوامر قاعدة البيانات

### `make db-migrate`

**Description | الوصف**: Run Prisma database migrations for all Node.js services.
تشغيل ترحيلات Prisma لجميع خدمات Node.js.

**Usage | الاستخدام**:
```bash
make db-migrate
```

**Services Migrated | الخدمات المرحلة**:
- field-core
- crop-growth-model
- disaster-assessment

---

### `make db-seed`

**Description | الوصف**: Seed database with sample/test data.
ملء قاعدة البيانات ببيانات تجريبية.

**Usage | الاستخدام**:
```bash
make db-seed
```

---

### `make db-reset`

**Description | الوصف**: Reset database completely (deletes all data and recreates).
إعادة تعيين قاعدة البيانات بالكامل.

**Usage | الاستخدام**:
```bash
make db-reset
```

**Warning | تحذير**: Interactive confirmation required. All data will be lost!
مطلوب تأكيد تفاعلي. سيتم فقدان جميع البيانات!

---

### `make db-shell`

**Description | الوصف**: Open PostgreSQL interactive shell.
فتح طرفية PostgreSQL التفاعلية.

**Usage | الاستخدام**:
```bash
make db-shell
```

**Example Queries | استعلامات مثال**:
```sql
-- List all tables
\dt

-- Describe a table
\d fields

-- Query data
SELECT * FROM fields LIMIT 10;

-- Exit
\q
```

---

### `make db-backup`

**Description | الوصف**: Create a timestamped database backup in `backups/` directory.
إنشاء نسخة احتياطية مؤرخة في مجلد `backups/`.

**Usage | الاستخدام**:
```bash
make db-backup
```

**Output | المخرجات**:
- Creates: `backups/backup_YYYYMMDD_HHMMSS.sql`

**Restore Example | مثال الاستعادة**:
```bash
cat backups/backup_20260120_143000.sql | docker exec -i sahool-postgres psql -U sahool -d sahool
```

---

## Testing Commands | أوامر الاختبارات

### `make test`

**Description | الوصف**: Run all tests (Python + Node.js).
تشغيل جميع الاختبارات.

**Usage | الاستخدام**:
```bash
make test
```

---

### `make test-python`

**Description | الوصف**: Run Python tests using pytest.
تشغيل اختبارات Python باستخدام pytest.

**Usage | الاستخدام**:
```bash
make test-python
```

**Output | المخرجات**:
- Test results with verbose output
- Short traceback on failures

---

### `make test-node`

**Description | الوصف**: Run Node.js tests for all services.
تشغيل اختبارات Node.js لجميع الخدمات.

**Usage | الاستخدام**:
```bash
make test-node
```

**Services Tested | الخدمات المختبرة**:
- field-core
- crop-growth-model
- web application

---

### `make test-integration`

**Description | الوصف**: Run integration tests that test API and database interactions.
تشغيل اختبارات التكامل.

**Usage | الاستخدام**:
```bash
make test-integration
```

---

### `make test-unit`

**Description | الوصف**: Run fast unit tests only.
تشغيل اختبارات الوحدة السريعة فقط.

**Usage | الاستخدام**:
```bash
make test-unit
```

---

### `make test-coverage`

**Description | الوصف**: Run tests with coverage report generation.
تشغيل الاختبارات مع توليد تقرير التغطية.

**Usage | الاستخدام**:
```bash
make test-coverage
```

**Output | المخرجات**:
- Terminal coverage summary
- HTML report: `coverage_html/index.html`

---

### `make test-docker`

**Description | الوصف**: Run tests inside Docker containers for isolated testing.
تشغيل الاختبارات داخل حاويات Docker.

**Usage | الاستخدام**:
```bash
make test-docker
```

---

## Mobile Development | تطوير الجوال

### `make mobile-test`

**Description | الوصف**: Run Flutter mobile app tests with coverage.
تشغيل اختبارات تطبيق Flutter مع التغطية.

**Usage | الاستخدام**:
```bash
make mobile-test
```

**Output | المخرجات**:
- Test results with expanded reporter
- Coverage percentage from `coverage/lcov.info`

**Example Output | مثال المخرجات**:
```
Running Flutter tests...
✓ All 150 tests passed
Coverage: 78.5% of lines
```

---

### `make mobile-build`

**Description | الوصف**: Build Flutter APK for debugging.
بناء APK للتطبيق للتصحيح.

**Usage | الاستخدام**:
```bash
make mobile-build
```

**What it does | ماذا يفعل**:
1. Runs `flutter pub get` to install dependencies
2. Runs `build_runner` for code generation (Drift, Freezed, Riverpod)
3. Builds debug APK
4. Displays APK path and size

**Output Location | موقع المخرجات**:
- `apps/mobile/build/app/outputs/flutter-apk/app-debug.apk`

---

### `make mobile-build-release`

**Description | الوصف**: Build optimized release APK for production testing.
بناء APK للإنتاج محسن.

**Usage | الاستخدام**:
```bash
make mobile-build-release
```

**What it does | ماذا يفعل**:
1. Installs dependencies
2. Generates code
3. Builds release APK with optimizations (minification, ProGuard)
4. Displays APK path and size

**Output Location | موقع المخرجات**:
- `apps/mobile/build/app/outputs/flutter-apk/app-release.apk`

---

### `make mobile-build-aab`

**Description | الوصف**: Build Android App Bundle (AAB) for Google Play Store submission.
بناء حزمة التطبيق للنشر في متجر Google Play.

**Usage | الاستخدام**:
```bash
make mobile-build-aab
```

**What it does | ماذا يفعل**:
1. Installs dependencies
2. Generates code
3. Builds release AAB for Play Store
4. Displays AAB path and size

**Output Location | موقع المخرجات**:
- `apps/mobile/build/app/outputs/bundle/release/app-release.aab`

**Note | ملاحظة**: AAB format is required for new apps on Google Play Store since August 2021.
صيغة AAB مطلوبة للتطبيقات الجديدة على متجر Google Play منذ أغسطس 2021.

---

### `make mobile-analyze`

**Description | الوصف**: Analyze Flutter/Dart code for issues and warnings.
تحليل كود Flutter/Dart للمشاكل والتحذيرات.

**Usage | الاستخدام**:
```bash
make mobile-analyze
```

**What it does | ماذا يفعل**:
1. Runs `flutter pub get`
2. Runs `flutter analyze` with `--no-fatal-infos` (warnings don't fail build)

**Example Output | مثال المخرجات**:
```
Analyzing apps/mobile...
   info - Unused import - lib/features/field/data.dart:5
   warning - Missing return type on function - lib/core/utils.dart:23
No issues found!
```

---

### `make mobile-format`

**Description | الوصف**: Format all Dart code in lib/ and test/ directories.
تنسيق جميع كود Dart في مجلدات lib/ و test/.

**Usage | الاستخدام**:
```bash
make mobile-format
```

**What it does | ماذا يفعل**:
- Runs `dart format lib/ test/`
- Applies consistent code style per Dart guidelines

---

### `make mobile-clean`

**Description | الوصف**: Clean Flutter build artifacts and caches.
تنظيف ملفات البناء والذاكرة المؤقتة.

**Usage | الاستخدام**:
```bash
make mobile-clean
```

**What it does | ماذا يفعل**:
1. Runs `flutter clean`
2. Removes `.dart_tool`, `build`, `coverage` directories

**When to use | متى تستخدم**:
- After changing dependencies
- When experiencing build issues
- Before creating release builds

---

### `make mobile-deps`

**Description | الوصف**: Install Flutter dependencies and run code generation.
تثبيت تبعيات Flutter وتشغيل توليد الكود.

**Usage | الاستخدام**:
```bash
make mobile-deps
```

**What it does | ماذا يفعل**:
1. Runs `flutter pub get`
2. Runs `build_runner build --delete-conflicting-outputs`

---

### `make mobile-codegen`

**Description | الوصف**: Generate code for Drift (SQLite), Freezed (immutable models), Riverpod.
توليد الكود لـ Drift و Freezed و Riverpod.

**Usage | الاستخدام**:
```bash
make mobile-codegen
```

**Generated Files | الملفات المولدة**:
- `*.g.dart` - Drift database tables
- `*.freezed.dart` - Freezed immutable models
- `*.gr.dart` - Riverpod providers

**When to run | متى تشغل**:
- After modifying `@freezed` classes
- After modifying Drift table definitions
- After modifying `@riverpod` providers

---

### `make mobile-doctor`

**Description | الوصف**: Check Flutter environment and dependencies status.
فحص بيئة Flutter وحالة التبعيات.

**Usage | الاستخدام**:
```bash
make mobile-doctor
```

**What it does | ماذا يفعل**:
- Runs `flutter doctor -v` for verbose output
- Checks Flutter SDK, Android SDK, Xcode, etc.

**Example Output | مثال المخرجات**:
```
[✓] Flutter (Channel stable, 3.27.x)
[✓] Android toolchain - develop for Android devices
[✓] Xcode - develop for iOS and macOS
[✓] Android Studio (version 2024.1)
[✓] Connected device (2 available)
```

---

### `make mobile-ci`

**Description | الوصف**: Run mobile CI checks (analyze + test).
تشغيل فحوصات CI للجوال.

**Usage | الاستخدام**:
```bash
make mobile-ci
```

**What it does | ماذا يفعل**:
1. Runs `mobile-analyze`
2. Runs `mobile-test`
3. Reports pass/fail status

**Use in CI/CD | الاستخدام في CI/CD**:
```yaml
# GitHub Actions example
- name: Mobile CI Checks
  run: make mobile-ci
```

---

## Infrastructure Commands | أوامر البنية التحتية

### `make infra-up`

**Description | الوصف**: Start infrastructure services only (no application services).
تشغيل خدمات البنية التحتية فقط.

**Usage | الاستخدام**:
```bash
make infra-up
```

**Services Started | الخدمات المبدوءة**:
| Service | Port | Purpose |
|---------|------|---------|
| PostgreSQL | 5432 | Primary database |
| Redis | 6379 | Caching & sessions |
| NATS | 4222 | Message queue |
| Kong | 8000 | API Gateway |

**When to use | متى تستخدم**:
- Running services locally without Docker
- Debugging specific services
- Minimal resource usage during development

---

### `make kong-reload`

**Description | الوصف**: Reload Kong API Gateway configuration without restart.
إعادة تحميل إعدادات Kong بدون إعادة تشغيل.

**Usage | الاستخدام**:
```bash
make kong-reload
```

**When to use | متى تستخدم**:
- After modifying Kong configuration
- Adding/removing routes
- Updating plugins

---

### `make vault-up`

**Description | الوصف**: Start HashiCorp Vault for secrets management.
تشغيل HashiCorp Vault لإدارة الأسرار.

**Usage | الاستخدام**:
```bash
make vault-up
```

**Access | الوصول**:
- URL: `http://localhost:8200`
- Dev Token: `dev-root-token`

**Warning | تحذير**: Dev mode Vault is not for production! Data is not persisted.
وضع التطوير ليس للإنتاج! البيانات لا تُحفظ.

---

### `make vault-down`

**Description | الوصف**: Stop HashiCorp Vault.
إيقاف HashiCorp Vault.

**Usage | الاستخدام**:
```bash
make vault-down
```

---

### `make network-create`

**Description | الوصف**: Create the SAHOOL Docker network for inter-container communication.
إنشاء شبكة Docker لـ SAHOOL للتواصل بين الحاويات.

**Usage | الاستخدام**:
```bash
make network-create
```

**What it does | ماذا يفعل**:
- Creates `sahool-network` Docker bridge network
- Idempotent - safe to run multiple times

---

### `make network-inspect`

**Description | الوصف**: Inspect SAHOOL Docker network configuration and connected containers.
فحص إعدادات شبكة Docker والحاويات المتصلة.

**Usage | الاستخدام**:
```bash
make network-inspect
```

**Output | المخرجات**:
- Network configuration (subnet, gateway)
- List of connected containers
- IP addresses of each container

---

## Monitoring Commands | أوامر المراقبة

### `make monitoring-up`

**Description | الوصف**: Start Prometheus, Grafana, and Alertmanager monitoring stack.
تشغيل Prometheus و Grafana و Alertmanager.

**Usage | الاستخدام**:
```bash
make monitoring-up
```

**Prerequisites | المتطلبات**:
- `.env` file with `GRAFANA_ADMIN_PASSWORD` set

**Access URLs | روابط الوصول**:
| Service | URL | Default Credentials |
|---------|-----|---------------------|
| Prometheus | http://localhost:9090 | None |
| Grafana | http://localhost:3002 | admin / (from .env) |
| Alertmanager | http://localhost:9093 | None |

---

### `make monitoring-down`

**Description | الوصف**: Stop all monitoring services.
إيقاف جميع خدمات المراقبة.

**Usage | الاستخدام**:
```bash
make monitoring-down
```

---

### `make monitoring-logs`

**Description | الوصف**: View monitoring stack logs in real-time.
عرض سجلات المراقبة في الوقت الفعلي.

**Usage | الاستخدام**:
```bash
make monitoring-logs
```

---

## Code Quality Commands | أوامر جودة الكود

### `make lint`

**Description | الوصف**: Run all linters (Python Ruff + TypeScript ESLint).
تشغيل جميع أدوات فحص الكود.

**Usage | الاستخدام**:
```bash
make lint
```

**What it checks | ما يفحصه**:
- Python: Ruff format check + linting rules
- TypeScript/JavaScript: ESLint rules

---

### `make fmt`

**Description | الوصف**: Auto-format all code (Python + TypeScript).
تنسيق جميع الكود تلقائياً.

**Usage | الاستخدام**:
```bash
make fmt
```

**What it does | ماذا يفعل**:
1. `ruff format .` - Format Python code
2. `ruff check . --fix` - Auto-fix Python linting issues
3. `npm run format` - Format TypeScript/JavaScript

---

## Development Tools | أدوات التطوير

### `make dev-install`

**Description | الوصف**: Install all development dependencies and pre-commit hooks.
تثبيت جميع تبعيات التطوير و pre-commit hooks.

**Usage | الاستخدام**:
```bash
make dev-install
```

**What it does | ماذا يفعل**:
1. Upgrades pip
2. Installs Python dev requirements from `requirements/dev.txt`
3. Installs pre-commit hooks
4. Installs npm dependencies for web and admin apps

---

### `make generate-tokens`

**Description | الوصف**: Generate design tokens from design system definitions.
توليد رموز التصميم من تعريفات نظام التصميم.

**Usage | الاستخدام**:
```bash
make generate-tokens
```

**What it does | ماذا يفعل**:
- Runs `scripts/generators/generate_design_tokens.py`
- Generates CSS variables, TypeScript types, and mobile theme files

---

### `make security-scan`

**Description | الوصف**: Run security scans using detect-secrets.
تشغيل فحوصات الأمان باستخدام detect-secrets.

**Usage | الاستخدام**:
```bash
make security-scan
```

**What it does | ماذا يفعل**:
- Scans codebase for potential secrets
- Compares against baseline in `.secrets.baseline`
- Reports any new potential secrets

---

### `make env-check`

**Description | الوصف**: Validate environment configuration and create .env if missing.
التحقق من إعدادات البيئة وإنشاء .env إذا لم يوجد.

**Usage | الاستخدام**:
```bash
make env-check
```

**What it does | ماذا يفعل**:
1. Checks if `.env` file exists
2. If missing, creates from `.env.example`
3. Reminds user to update values

---

### `make docs`

**Description | الوصف**: Display documentation overview and file locations.
عرض نظرة عامة على التوثيق ومواقع الملفات.

**Usage | الاستخدام**:
```bash
make docs
```

**Output | المخرجات**:
- List of main documentation files
- Package documentation locations
- Quick reference to key docs

---

### `make watch`

**Description | الوصف**: Continuously watch and display service status.
مراقبة مستمرة وعرض حالة الخدمات.

**Usage | الاستخدام**:
```bash
make watch
```

**What it does | ماذا يفعل**:
- Runs `docker compose ps` every 2 seconds
- Updates display in-place
- Press `Ctrl+C` to exit

---

## CI/CD Commands | أوامر التكامل المستمر

### `make ci`

**Description | الوصف**: Run standard CI checks (lint + test).
تشغيل فحوصات CI القياسية.

**Usage | الاستخدام**:
```bash
make ci
```

**What it does | ماذا يفعل**:
1. Runs `make lint`
2. Runs `make test`

**Use in CI/CD | الاستخدام في CI/CD**:
```yaml
# GitHub Actions
- name: CI Checks
  run: make ci
```

---

### `make ci-full`

**Description | الوصف**: Run full CI checks including coverage and security scan.
تشغيل فحوصات CI الكاملة بما في ذلك التغطية وفحص الأمان.

**Usage | الاستخدام**:
```bash
make ci-full
```

**What it does | ماذا يفعل**:
1. Runs `make lint`
2. Runs `make test-coverage`
3. Runs `make security-scan`

**When to use | متى تستخدم**:
- Before creating pull requests
- Nightly builds
- Release preparation

---

## Utility Commands | أوامر مساعدة

### `make clean`

**Description | الوصف**: Clean up containers, volumes, and build artifacts.
تنظيف الحاويات والبيانات وملفات البناء.

**Usage | الاستخدام**:
```bash
make clean
```

**What it does | ماذا يفعل**:
1. Stops and removes all containers
2. Removes volumes and orphaned containers
3. Prunes Docker system
4. Removes `coverage_html`, `__pycache__`, `node_modules/.cache`

---

### `make status`

**Description | الوصف**: Display detailed service status and access URLs.
عرض حالة الخدمات وروابط الوصول بالتفصيل.

**Usage | الاستخدام**:
```bash
make status
```

**Output | المخرجات**:
- Container status table (name, status, ports)
- Service URLs with ports

---

### `make health`

**Description | الوصف**: Check health of all critical services.
فحص صحة جميع الخدمات الحرجة.

**Usage | الاستخدام**:
```bash
make health
```

**What it checks | ما يفحصه**:
- Container status for: postgres, redis, nats, kong, field_ops, weather_core
- HTTP response codes for Kong Gateway and Field Ops API

---

### `make shell`

**Description | الوصف**: Open an interactive shell inside a container.
فتح طرفية تفاعلية داخل حاوية.

**Usage | الاستخدام**:
```bash
make shell SERVICE=postgres
make shell SERVICE=field_ops
make shell SERVICE=kong
```

**Required Parameters | المعاملات المطلوبة**:
- `SERVICE`: Container name to open shell in

---

### `make ps`

**Description | الوصف**: List all running containers with status.
قائمة جميع الحاويات قيد التشغيل مع الحالة.

**Usage | الاستخدام**:
```bash
make ps
```

---

### `make stats`

**Description | الوصف**: Display project statistics (services, containers, code files).
عرض إحصائيات المشروع.

**Usage | الاستخدام**:
```bash
make stats
```

**Output | المخرجات**:
- Number of Python services
- Number of Node.js services
- Running containers count
- Docker images count
- Python file count
- TypeScript file count

---

## Aliases & Quick Start | الاختصارات والبدء السريع

### `make start`

**Description | الوصف**: Alias for `make up`.
اختصار لـ `make up`.

**Usage | الاستخدام**:
```bash
make start
```

---

### `make stop`

**Description | الوصف**: Alias for `make down`.
اختصار لـ `make down`.

**Usage | الاستخدام**:
```bash
make stop
```

---

### `make rebuild`

**Description | الوصف**: Full rebuild - clean, build, and start.
إعادة بناء كاملة - تنظيف وبناء وتشغيل.

**Usage | الاستخدام**:
```bash
make rebuild
```

**What it does | ماذا يفعل**:
1. `make clean` - Remove all containers and artifacts
2. `make build` - Build all Docker images
3. `make up` - Start all services

---

### `make starter-up`

**Description | الوصف**: Alias for `make dev-starter`.
اختصار لـ `make dev-starter`.

**Usage | الاستخدام**:
```bash
make starter-up
```

---

### `make professional-up`

**Description | الوصف**: Alias for `make dev-professional`.
اختصار لـ `make dev-professional`.

**Usage | الاستخدام**:
```bash
make professional-up
```

---

### `make enterprise-up`

**Description | الوصف**: Alias for `make dev-enterprise`.
اختصار لـ `make dev-enterprise`.

**Usage | الاستخدام**:
```bash
make enterprise-up
```

---

### `make quickstart`

**Description | الوصف**: Complete quick start for new developers.
بدء سريع كامل للمطورين الجدد.

**Usage | الاستخدام**:
```bash
make quickstart
```

**What it does | ماذا يفعل**:
1. **Step 1**: Environment check - validates/creates `.env`
2. **Step 2**: Network creation - creates Docker network
3. **Step 3**: Infrastructure start - starts postgres, redis, nats, kong
4. **Step 4**: Migrations - runs database migrations
5. **Step 5**: Services start - starts all application services
6. **Final**: Displays status and URLs

**Recommended for | موصى به لـ**:
- New team members
- Fresh clones of the repository
- After system reset

---

## Environment Variables | متغيرات البيئة

The Makefile uses these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `ENV` | `development` | Environment mode |
| `COMPOSE_PROJECT_NAME` | `sahool` | Docker Compose project name |
| `SERVICE` | (none) | Service name for targeted commands |

**Docker Compose Files | ملفات Docker Compose**:

| Variable | Path |
|----------|------|
| `COMPOSE_BASE` | `docker-compose.yml` |
| `COMPOSE_STARTER` | `packages/starter/docker-compose.yml` |
| `COMPOSE_PROFESSIONAL` | `packages/professional/docker-compose.yml` |
| `COMPOSE_ENTERPRISE` | `packages/enterprise/docker-compose.yml` |
| `COMPOSE_MONITORING` | `infrastructure/monitoring/docker-compose.monitoring.yml` |
| `COMPOSE_TEST` | `docker-compose.test.yml` |

---

## Command Summary by Category | ملخص الأوامر حسب الفئة

### Development (4)
| Command | Purpose |
|---------|---------|
| `dev` | Full environment |
| `dev-starter` | Starter package |
| `dev-professional` | Professional package |
| `dev-enterprise` | Enterprise package |

### Docker (9)
| Command | Purpose |
|---------|---------|
| `build` | Build all images |
| `build-python` | Build Python services |
| `build-node` | Build Node.js services |
| `up` | Start services |
| `down` | Stop services |
| `down-volumes` | Stop + remove data |
| `restart` | Restart services |
| `logs` | View all logs |
| `logs-service` | View specific logs |

### Database (5)
| Command | Purpose |
|---------|---------|
| `db-migrate` | Run migrations |
| `db-seed` | Seed database |
| `db-reset` | Reset database |
| `db-shell` | Open psql |
| `db-backup` | Backup database |

### Testing (7)
| Command | Purpose |
|---------|---------|
| `test` | All tests |
| `test-python` | Python tests |
| `test-node` | Node.js tests |
| `test-integration` | Integration tests |
| `test-unit` | Unit tests |
| `test-coverage` | Tests + coverage |
| `test-docker` | Tests in Docker |

### Mobile (11)
| Command | Purpose |
|---------|---------|
| `mobile-test` | Flutter tests |
| `mobile-build` | Debug APK |
| `mobile-build-release` | Release APK |
| `mobile-build-aab` | Play Store AAB |
| `mobile-analyze` | Code analysis |
| `mobile-format` | Format Dart |
| `mobile-clean` | Clean builds |
| `mobile-deps` | Install deps |
| `mobile-codegen` | Generate code |
| `mobile-doctor` | Flutter doctor |
| `mobile-ci` | CI checks |

### Infrastructure (6)
| Command | Purpose |
|---------|---------|
| `infra-up` | Start infra only |
| `kong-reload` | Reload Kong |
| `vault-up` | Start Vault |
| `vault-down` | Stop Vault |
| `network-create` | Create network |
| `network-inspect` | Inspect network |

### Monitoring (3)
| Command | Purpose |
|---------|---------|
| `monitoring-up` | Start monitoring |
| `monitoring-down` | Stop monitoring |
| `monitoring-logs` | View logs |

### Code Quality (2)
| Command | Purpose |
|---------|---------|
| `lint` | Check code |
| `fmt` | Format code |

### Development Tools (6)
| Command | Purpose |
|---------|---------|
| `dev-install` | Install deps |
| `generate-tokens` | Design tokens |
| `security-scan` | Security scan |
| `env-check` | Validate env |
| `docs` | Show docs |
| `watch` | Watch status |

### CI/CD (2)
| Command | Purpose |
|---------|---------|
| `ci` | Standard CI |
| `ci-full` | Full CI |

### Utilities (5)
| Command | Purpose |
|---------|---------|
| `clean` | Cleanup |
| `status` | Show status |
| `health` | Health check |
| `shell` | Open shell |
| `ps` | List containers |
| `stats` | Project stats |

### Aliases (7)
| Command | Purpose |
|---------|---------|
| `start` | Alias: up |
| `stop` | Alias: down |
| `rebuild` | Full rebuild |
| `starter-up` | Alias: dev-starter |
| `professional-up` | Alias: dev-professional |
| `enterprise-up` | Alias: dev-enterprise |
| `quickstart` | New dev setup |

---

**Total Commands: 68**

---

_Last Updated: January 2026_
