# توثيق هيكل مستودع SAHOOL

## نظرة عامة

**SAHOOL** - منصة زراعية ذكية لليمن والشرق الأوسط
**الإصدار:** 16.0.0
**نوع المشروع:** Monorepo (NPM Workspaces + Python Services)

---

## الهيكل الرئيسي

```
sahool-unified-v15-idp/
├── apps/                    # التطبيقات الرئيسية
├── packages/                # الحزم المشتركة (NPM)
├── shared/                  # الكود المشترك (Python)
├── infra/                   # إعدادات البنية التحتية
├── gitops/                  # GitOps و ArgoCD
├── governance/              # الحوكمة والسياسات
├── observability/           # المراقبة والتنبيهات
├── helm/                    # Helm Charts
├── idp/                     # Internal Developer Platform
├── tools/                   # أدوات التطوير
├── tests/                   # الاختبارات العامة
├── docs/                    # التوثيق
├── legacy/                  # الكود القديم
└── .github/workflows/       # GitHub Actions
```

---

## 1. مجلد `apps/` - التطبيقات

### 1.1 `apps/web/` - تطبيق الويب الرئيسي

**التقنية:** Next.js 15.5.9 + React 19 + TypeScript
**الغرض:** واجهة المستخدم الرئيسية للمزارعين

```
apps/web/
├── src/
│   ├── app/                 # Next.js App Router
│   │   ├── api/             # API Routes
│   │   └── log-error/       # تسجيل الأخطاء
│   ├── components/          # المكونات
│   │   ├── common/          # مكونات عامة
│   │   └── dashboard/       # مكونات لوحة القيادة
│   ├── features/            # الميزات
│   │   ├── advisor/         # المستشار الزراعي
│   │   ├── alerts/          # التنبيهات
│   │   ├── field-map/       # خريطة الحقول
│   │   ├── ndvi/            # مؤشر NDVI
│   │   └── reports/         # التقارير
│   ├── hooks/               # React Hooks المشتركة
│   ├── lib/                 # المكتبات
│   │   ├── auth/            # المصادقة
│   │   ├── monitoring/      # المراقبة
│   │   ├── performance/     # تحسين الأداء
│   │   └── security/        # الأمان
│   └── types/               # TypeScript Types
├── package.json
├── next.config.ts
├── eslint.config.mjs
└── vitest.config.ts
```

### 1.2 `apps/admin/` - لوحة الإدارة

**التقنية:** Next.js 15.5.9 + React 19 + TypeScript
**الغرض:** لوحة تحكم المشرفين والإداريين

```
apps/admin/
├── src/
│   ├── app/                 # صفحات التطبيق
│   │   ├── alerts/          # إدارة التنبيهات
│   │   ├── dashboard/       # لوحة القيادة
│   │   ├── diseases/        # إدارة الأمراض
│   │   ├── epidemic/        # إدارة الأوبئة
│   │   ├── farms/           # إدارة المزارع
│   │   ├── irrigation/      # إدارة الري
│   │   ├── lab/             # المختبر
│   │   ├── login/           # تسجيل الدخول
│   │   ├── sensors/         # إدارة المستشعرات
│   │   ├── support/         # الدعم الفني
│   │   └── yield/           # إدارة المحصول
│   ├── components/
│   │   ├── common/          # مكونات عامة
│   │   ├── layout/          # تخطيط الصفحة
│   │   ├── maps/            # مكونات الخرائط
│   │   └── ui/              # مكونات UI
│   ├── lib/
│   │   ├── api-gateway/     # بوابة API
│   │   └── i18n/            # الترجمة
│   └── types/
├── package.json
└── next.config.ts
```

### 1.3 `apps/mobile/` - تطبيق الموبايل

**التقنية:** Flutter (Dart)
**الغرض:** تطبيق ميداني للمزارعين

```
apps/mobile/
├── sahool_field_app/
│   ├── lib/
│   │   └── features/
│   │       └── gamification/     # نظام التلعيب
│   ├── test/
│   │   ├── integration/          # اختبارات التكامل
│   │   ├── unit/                 # اختبارات الوحدة
│   │   └── widget/               # اختبارات الواجهة
│   └── pubspec.yaml
├── android/                      # إعدادات Android
├── scripts/                      # سكربتات البناء
└── pubspec.yaml
```

### 1.4 `apps/services/` - الخدمات المصغرة (Microservices)

**التقنية:** Python + FastAPI
**الغرض:** خدمات API الخلفية

| الخدمة                 | المنفذ | الوظيفة                                          |
| ---------------------- | ------ | ------------------------------------------------ |
| `satellite-service`    | 8090   | تحليل صور الأقمار الصناعية (Sentinel-2, Landsat) |
| `indicators-service`   | 8091   | المؤشرات الزراعية (20+ مؤشر)                     |
| `weather-advanced`     | 8092   | التنبؤات الجوية والتقويم الزراعي                 |
| `fertilizer-advisor`   | 8093   | توصيات التسميد (12+ محصول)                       |
| `irrigation-smart`     | 8094   | الري الذكي وإدارة المياه                         |
| `crop-health-ai`       | -      | تحليل صحة المحاصيل بالذكاء الاصطناعي             |
| `yield-engine`         | -      | التنبؤ بالمحصول                                  |
| `yield-prediction`     | -      | نماذج التنبؤ                                     |
| `notification-service` | -      | خدمة الإشعارات                                   |
| `billing-core`         | -      | نظام الفوترة                                     |
| `virtual-sensors`      | -      | المستشعرات الافتراضية                            |
| `alert-service`        | -      | خدمة التنبيهات                                   |
| `field-service`        | -      | إدارة الحقول                                     |
| `iot-service`          | -      | خدمة IoT                                         |
| `ndvi-processor`       | -      | معالجة NDVI                                      |
| `lai-estimation`       | -      | تقدير مساحة الأوراق                              |
| `disaster-assessment`  | -      | تقييم الكوارث                                    |
| `crop-growth-model`    | -      | نموذج نمو المحاصيل                               |
| `community-chat`       | -      | دردشة المجتمع                                    |
| `marketplace-service`  | -      | السوق الإلكتروني                                 |
| `research-core`        | -      | البحث العلمي                                     |

---

## 2. مجلد `packages/` - الحزم المشتركة (NPM)

| الحزمة              | الوظيفة                 |
| ------------------- | ----------------------- |
| `shared-utils`      | دوال مساعدة مشتركة      |
| `shared-ui`         | مكونات UI مشتركة        |
| `shared-hooks`      | React Hooks مشتركة      |
| `api-client`        | عميل API موحد           |
| `design-system`     | نظام التصميم            |
| `tailwind-config`   | إعدادات Tailwind CSS    |
| `typescript-config` | إعدادات TypeScript      |
| `i18n`              | الترجمة والتعريب        |
| `mock-data`         | بيانات وهمية للاختبار   |
| `advisor`           | منطق المستشار الزراعي   |
| `field_suite`       | أدوات إدارة الحقول      |
| `kernel_domain`     | نماذج المجال الأساسية   |
| `sahool-eo`         | Earth Observation tools |
| `shared`            | كود مشترك عام           |

---

## 3. مجلد `shared/` - الكود المشترك (Python)

```
shared/
├── __init__.py
├── contracts/           # عقود الخدمات والواجهات
├── domain/              # نماذج المجال
├── events/              # أحداث النظام
├── libs/                # مكتبات مشتركة
├── middleware/          # Middleware
├── monitoring/          # أدوات المراقبة
├── observability/       # OpenTelemetry integration
├── security/            # أدوات الأمان
└── templates/           # قوالب
```

---

## 4. مجلد `infra/` - البنية التحتية

```
infra/
├── kong/                # Kong API Gateway configs
├── mqtt/                # MQTT Broker (Mosquitto)
├── postgres/            # PostgreSQL configs
├── qdrant/              # Qdrant Vector DB
└── vault/               # HashiCorp Vault
```

---

## 5. مجلد `gitops/` - GitOps

```
gitops/
├── argocd/              # ArgoCD Applications
│   ├── applications/    # تعريفات التطبيقات
│   └── projects/        # مشاريع ArgoCD
├── environments/        # إعدادات البيئات
├── feature-flags/       # أعلام الميزات
├── idp/                 # IDP configs
├── ingress/             # Ingress rules
├── sahool/              # Sahool-specific configs
├── scripts/             # سكربتات النشر
└── secrets/             # إدارة الأسرار
```

---

## 6. مجلد `governance/` - الحوكمة

```
governance/
├── decisions/           # سجل القرارات (ADR)
├── design/              # وثائق التصميم
├── events/              # كتالوج الأحداث
├── policies/            # سياسات Kyverno
├── reliability/         # SLO/SLI definitions
├── schemas/             # JSON Schemas
├── templates/           # Backstage Templates
├── services.yaml        # سجل الخدمات
├── credentials.template.yaml
└── DEDUP_MATRIX.md      # مصفوفة إزالة التكرار
```

**السياسات المفروضة:**

- `restrict-latest-tag`: منع استخدام `image:latest`
- `require-resource-limits`: فرض تحديد CPU/Memory
- `require-governance-labels`: فرض labels الحوكمة
- `baseline-security`: منع privileged containers

---

## 7. مجلد `observability/` - المراقبة

```
observability/
├── alerts/              # قواعد التنبيهات
├── dashboards/          # Grafana Dashboards
├── grafana/             # إعدادات Grafana
├── metrics/             # تعريفات المقاييس
├── prometheus/          # Prometheus configs
└── slo/                 # SLO definitions
```

---

## 8. مجلد `helm/` - Helm Charts

```
helm/
└── sahool/              # Helm Chart الرئيسي
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
```

---

## 9. مجلد `idp/` - Internal Developer Platform

```
idp/
├── backstage/           # Backstage configurations
│   ├── catalog-info.yaml
│   └── app-config.yaml
├── sahoolctl/           # CLI tool
│   └── sahoolctl.py
└── templates/           # Service templates
    └── python-fastapi/
```

---

## 10. مجلد `tools/` - أدوات التطوير

```
tools/
├── arch/                # أدوات التحقق من البنية
├── compliance/          # أدوات الامتثال
├── env/                 # إدارة البيئات
├── events/              # أدوات الأحداث
├── release/             # أدوات الإصدار
├── security/            # أدوات الأمان
└── sensor-simulator/    # محاكي المستشعرات
```

---

## 11. مجلد `tests/` - الاختبارات

```
tests/
├── conftest.py          # إعدادات pytest
├── factories/           # Factory patterns
├── integration/         # اختبارات التكامل
├── smoke/               # اختبارات Smoke
└── unit/                # اختبارات الوحدة
```

---

## 12. مجلد `.github/workflows/` - GitHub Actions

| Workflow                    | الوظيفة                                |
| --------------------------- | -------------------------------------- |
| `ci.yml`                    | CI الرئيسي                             |
| `frontend-ci.yml`           | CI للواجهات الأمامية                   |
| `test.yml`                  | تشغيل الاختبارات                       |
| `security-checks.yml`       | فحوصات الأمان (Trivy, Bandit, Semgrep) |
| `quality-gates.yml`         | بوابات الجودة                          |
| `governance-ci.yml`         | فحوصات الحوكمة                         |
| `governance-structure.yml`  | التحقق من الهيكل                       |
| `event-contracts-guard.yml` | حماية عقود الأحداث                     |
| `generator-guard.yml`       | حماية المولدات                         |
| `flutter-apk.yml`           | بناء تطبيق Android                     |
| `docker-image.yml`          | بناء Docker images                     |
| `release.yml`               | الإصدار                                |
| `release-candidate.yml`     | مرشح الإصدار                           |
| `infra-sync.yml`            | مزامنة البنية التحتية                  |

---

## 13. الملفات الجذرية

| الملف                     | الوظيفة                     |
| ------------------------- | --------------------------- |
| `package.json`            | إعدادات NPM Monorepo        |
| `package-lock.json`       | قفل التبعيات                |
| `pyproject.toml`          | إعدادات Python              |
| `pytest.ini`              | إعدادات pytest              |
| `conftest.py`             | إعدادات الاختبار            |
| `vitest.config.ts`        | إعدادات Vitest              |
| `tsconfig.base.json`      | إعدادات TypeScript الأساسية |
| `.eslintrc.base.json`     | إعدادات ESLint الأساسية     |
| `.pre-commit-config.yaml` | إعدادات pre-commit hooks    |
| `.secrets.baseline`       | خط أساس detect-secrets      |
| `docker-compose.yml`      | تشغيل الخدمات محلياً        |
| `Makefile`                | أوامر make                  |
| `.env.example`            | مثال متغيرات البيئة         |
| `.gitignore`              | الملفات المتجاهلة           |

---

## 14. التبعيات الرئيسية

### Frontend (Node.js)

- **Runtime:** Node.js >= 20.0.0
- **Package Manager:** NPM 10.9.0
- **Framework:** Next.js 15.5.9
- **UI Library:** React 19.0.0
- **Language:** TypeScript 5.9.3
- **Styling:** Tailwind CSS
- **Testing:** Vitest 3.1.3

### Backend (Python)

- **Runtime:** Python 3.11
- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Database:** PostgreSQL 15
- **Messaging:** NATS JetStream
- **Caching:** Redis 7

### Mobile (Flutter)

- **SDK:** Flutter Stable
- **Language:** Dart 3.6.0

### Infrastructure

- **Container Runtime:** Docker
- **Orchestration:** Kubernetes
- **GitOps:** ArgoCD
- **API Gateway:** Kong
- **Secrets:** HashiCorp Vault
- **Monitoring:** Prometheus + Grafana
- **Tracing:** OpenTelemetry

---

## 15. أوامر التطوير

```bash
# تشغيل تطبيق الويب
npm run dev:web

# تشغيل لوحة الإدارة
npm run dev:admin

# بناء جميع الحزم
npm run build:packages

# بناء جميع التطبيقات
npm run build:all

# فحص الكود
npm run lint:all

# فحص الأنواع
npm run type-check

# تنظيف node_modules
npm run clean

# تشغيل الخدمات الخلفية
docker compose up -d
```

---

## التاريخ

- **تاريخ الإنشاء:** 2025-12-20
- **آخر تحديث:** 2025-12-20
- **الإصدار:** 16.0.0
