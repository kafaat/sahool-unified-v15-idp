# SAHOOL Unified Platform Documentation
# توثيق منصة سهول الموحدة

> **الإصدار:** v15.5 | **آخر تحديث:** December 2025

---

## فهرس المحتويات | Table of Contents

### 1. المعمارية | Architecture

| الملف | الوصف | الحالة |
|-------|-------|--------|
| [FIELD_FIRST_ARCHITECTURE.md](./architecture/FIELD_FIRST_ARCHITECTURE.md) | البنية الميدانية أولاً - المبدأ الأساسي | ✅ |
| [PRINCIPLES.md](./architecture/PRINCIPLES.md) | المبادئ المعمارية | ✅ |
| [SERVICE_ACTIVATION_MAP.md](./architecture/SERVICE_ACTIVATION_MAP.md) | خريطة تفعيل الخدمات | ✅ |
| [frontend-governance.md](./architecture/frontend-governance.md) | حوكمة الواجهة الأمامية | ✅ |
| [EVENT_SEQUENCES.md](./architecture/EVENT_SEQUENCES.md) | تسلسلات الأحداث | ✅ |
| [FIELD_FIRST_IMPLEMENTATION_PLAN.md](./architecture/FIELD_FIRST_IMPLEMENTATION_PLAN.md) | خطة تنفيذ Field-First | ✅ |
| [FIELD_FIRST_ASSESSMENT.md](./architecture/FIELD_FIRST_ASSESSMENT.md) | تقييم Field-First | ✅ |
| [ASSET_INVESTMENT_PLAN.md](./architecture/ASSET_INVESTMENT_PLAN.md) | خطة الاستثمار في الأصول | ✅ |

---

### 2. الخدمات | Services

| الملف | الوصف | الحالة |
|-------|-------|--------|
| [SERVICES_MAP.md](./SERVICES_MAP.md) | خريطة جميع الخدمات والمنافذ | ✅ |
| [BACKEND_SERVICES_DOCUMENTATION.md](./BACKEND_SERVICES_DOCUMENTATION.md) | توثيق خدمات الخلفية | ✅ |
| [ASTRONOMICAL_CALENDAR_SERVICE.md](./ASTRONOMICAL_CALENDAR_SERVICE.md) | خدمة التقويم الفلكي | ✅ |
| [LEGACY_SERVICES.md](./LEGACY_SERVICES.md) | الخدمات القديمة والترحيل | ✅ |
| [SERVICE_PORTFOLIO_REVIEW.md](./SERVICE_PORTFOLIO_REVIEW.md) | مراجعة محفظة الخدمات | ✅ |
| [KERNEL_SERVICES_MERGE_PLAN.md](./KERNEL_SERVICES_MERGE_PLAN.md) | خطة دمج خدمات Kernel | ✅ |

---

### 3. سجلات القرارات المعمارية | ADRs (Architecture Decision Records)

| الملف | القرار | الحالة |
|-------|--------|--------|
| [ADR-000-template.md](./adr/ADR-000-template.md) | قالب ADR | Template |
| [ADR-001-offline-first-architecture.md](./adr/ADR-001-offline-first-architecture.md) | Offline-First Mobile | ✅ Accepted |
| [ADR-002-riverpod-state-management.md](./adr/ADR-002-riverpod-state-management.md) | Riverpod State Management | ✅ Accepted |
| [ADR-003-drift-local-database.md](./adr/ADR-003-drift-local-database.md) | Drift Local Database | ✅ Accepted |
| [ADR-004-kong-api-gateway.md](./adr/ADR-004-kong-api-gateway.md) | Kong API Gateway | ✅ Accepted |
| [ADR-005-nats-event-bus.md](./adr/ADR-005-nats-event-bus.md) | NATS Event Bus | ✅ Accepted |
| [ADR-006-circuit-breaker.md](./adr/ADR-006-circuit-breaker.md) | Circuit Breaker Pattern | ✅ Accepted |
| [ADR-007-redis-caching.md](./adr/ADR-007-redis-caching.md) | Redis Caching | ✅ Accepted |

---

### 4. الأمان | Security

| الملف | الوصف | الحالة |
|-------|-------|--------|
| [SECURITY.md](./SECURITY.md) | نظرة عامة على الأمان | ✅ |
| [security/THREAT_MODEL_STRIDE.md](./security/THREAT_MODEL_STRIDE.md) | نموذج التهديدات STRIDE | ✅ |
| [security/DATA_CLASSIFICATION.md](./security/DATA_CLASSIFICATION.md) | تصنيف البيانات | ✅ |
| [SECRETS_GITOPS.md](./SECRETS_GITOPS.md) | إدارة الأسرار GitOps | ✅ |

---

### 5. البنية التحتية | Infrastructure

| الملف | الوصف | الحالة |
|-------|-------|--------|
| [infrastructure/KONG_HA_SETUP.md](./infrastructure/KONG_HA_SETUP.md) | إعداد Kong HA | ✅ |
| [infrastructure/POSTGIS_OPTIMIZATION.md](./infrastructure/POSTGIS_OPTIMIZATION.md) | تحسين PostGIS | ✅ |
| [infrastructure/CIRCUIT_BREAKER.md](./infrastructure/CIRCUIT_BREAKER.md) | نمط Circuit Breaker | ✅ |
| [DOCKER.md](./DOCKER.md) | توثيق Docker | ✅ |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | دليل النشر | ✅ |
| [MULTI_REGION.md](./MULTI_REGION.md) | النشر متعدد المناطق | ✅ |
| [ENVIRONMENT.md](./ENVIRONMENT.md) | متغيرات البيئة | ✅ |

---

### 6. التطبيق المحمول | Mobile App

| الملف | الوصف | الحالة |
|-------|-------|--------|
| [mobile/README.md](./mobile/README.md) | نظرة عامة على Mobile | ✅ |
| [mobile/OFFLINE_FIRST.md](./mobile/OFFLINE_FIRST.md) | استراتيجية Offline-First | ✅ |
| [mobile/SYNC_ENGINE.md](./mobile/SYNC_ENGINE.md) | محرك المزامنة | ✅ |
| [mobile/CONFLICT_RESOLUTION.md](./mobile/CONFLICT_RESOLUTION.md) | حل التعارضات | ✅ |
| [mobile/CACHING_STRATEGY.md](./mobile/CACHING_STRATEGY.md) | استراتيجية التخزين المؤقت | ✅ |
| [MOBILE_APP_REVIEW_REPORT.md](./MOBILE_APP_REVIEW_REPORT.md) | تقرير مراجعة التطبيق | ✅ |
| [MOBILE_ARCHITECTURE_ANALYSIS.md](./MOBILE_ARCHITECTURE_ANALYSIS.md) | تحليل معمارية Mobile | ✅ |

---

### 7. الواجهة الأمامية | Frontend

| الملف | الوصف | الحالة |
|-------|-------|--------|
| [architecture/frontend-governance.md](./architecture/frontend-governance.md) | حوكمة الواجهة | ✅ |
| [WEB_APP_DEVELOPMENT_PLAN.md](./WEB_APP_DEVELOPMENT_PLAN.md) | خطة تطوير Web | ✅ |
| [FEATURE_FLAGS.md](./FEATURE_FLAGS.md) | Feature Flags | ✅ |
| [PR_PREVIEW_ENVIRONMENTS.md](./PR_PREVIEW_ENVIRONMENTS.md) | بيئات معاينة PR | ✅ |
| [PR_PREVIEW_URLS.md](./PR_PREVIEW_URLS.md) | روابط معاينة PR | ✅ |

---

### 8. الأحداث والتكامل | Events & Integration

| الملف | الوصف | الحالة |
|-------|-------|--------|
| [EVENT_CATALOG.md](./EVENT_CATALOG.md) | كتالوج الأحداث | ✅ |
| [architecture/EVENT_SEQUENCES.md](./architecture/EVENT_SEQUENCES.md) | تسلسلات الأحداث | ✅ |
| [GIS_ARCHITECTURE.md](./GIS_ARCHITECTURE.md) | معمارية GIS | ✅ |
| [AI_ARCHITECTURE.md](./AI_ARCHITECTURE.md) | معمارية الذكاء الاصطناعي | ✅ |
| [IDP_ARCHITECTURE.md](./IDP_ARCHITECTURE.md) | معمارية IDP | ✅ |

---

### 9. التشغيل والمراقبة | Operations & Observability

| الملف | الوصف | الحالة |
|-------|-------|--------|
| [OPERATIONS.md](./OPERATIONS.md) | دليل التشغيل | ✅ |
| [OPERATIONAL_SETUP.md](./OPERATIONAL_SETUP.md) | إعداد التشغيل | ✅ |
| [OBSERVABILITY.md](./OBSERVABILITY.md) | المراقبة والرصد | ✅ |
| [SLO_SLI_GUIDE.md](./SLO_SLI_GUIDE.md) | دليل SLO/SLI | ✅ |
| [RUNBOOKS.md](./RUNBOOKS.md) | كتيبات التشغيل | ✅ |
| [BILLING_QUOTAS.md](./BILLING_QUOTAS.md) | الفوترة والحصص | ✅ |

---

### 10. الاختبار والجودة | Testing & Quality

| الملف | الوصف | الحالة |
|-------|-------|--------|
| [TESTING.md](./TESTING.md) | استراتيجية الاختبار | ✅ |
| [ARCH_RULES.md](./ARCH_RULES.md) | قواعد المعمارية | ✅ |

---

### 11. الامتثال والحوكمة | Compliance & Governance

| الملف | الوصف | الحالة |
|-------|-------|--------|
| [compliance/COMPLIANCE_CHECKLIST.md](./compliance/COMPLIANCE_CHECKLIST.md) | قائمة الامتثال | ✅ |
| [governance/DEPENDENCY_MANAGEMENT.md](./governance/DEPENDENCY_MANAGEMENT.md) | إدارة التبعيات | ✅ |

---

### 12. الأدلة والمراجع | Guides & References

| الملف | الوصف | الحالة |
|-------|-------|--------|
| [guides/FIELD_FIRST_INTEGRATION_GUIDE.md](./guides/FIELD_FIRST_INTEGRATION_GUIDE.md) | دليل تكامل Field-First | ✅ |
| [UNIFIED_PACKAGES_GUIDE.md](./UNIFIED_PACKAGES_GUIDE.md) | دليل الحزم الموحدة | ✅ |
| [tools/PLATFORM_TOOLS.md](./tools/PLATFORM_TOOLS.md) | أدوات المنصة | ✅ |
| [REPOSITORY_STRUCTURE.md](./REPOSITORY_STRUCTURE.md) | هيكل المستودع | ✅ |
| [MIGRATIONS.md](./MIGRATIONS.md) | الترحيلات | ✅ |

---

### 13. الهندسة والتخطيط | Engineering & Planning

| الملف | الوصف | الحالة |
|-------|-------|--------|
| [engineering/ENGINEERING_RECOVERY_PLAN.md](./engineering/ENGINEERING_RECOVERY_PLAN.md) | خطة استعادة الهندسة | ✅ |
| [engineering/RECOVERY_SPRINT_TRACKER.md](./engineering/RECOVERY_SPRINT_TRACKER.md) | متتبع Sprint الاستعادة | ✅ |
| [PLATFORM_ROADMAP_NEXT.md](./PLATFORM_ROADMAP_NEXT.md) | خارطة طريق المنصة | ✅ |
| [PHASE1_DEPENDENCY_ANALYSIS.md](./PHASE1_DEPENDENCY_ANALYSIS.md) | تحليل تبعيات المرحلة 1 | ✅ |
| [PHASE_D_MAJOR_UPGRADES_PLAN.md](./PHASE_D_MAJOR_UPGRADES_PLAN.md) | خطة الترقيات الكبرى | ✅ |
| [CHANGELOG_ARCHITECTURE.md](./CHANGELOG_ARCHITECTURE.md) | سجل تغييرات المعمارية | ✅ |

---

## خريطة البنية السريعة | Quick Architecture Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SAHOOL Platform v15.5                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │  Mobile    │  │    Web     │  │   Admin    │  │  External  │    │
│  │  Flutter   │  │  Dashboard │  │  Dashboard │  │   APIs     │    │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘    │
│        └───────────────┴───────────────┴───────────────┘            │
│                              │                                       │
│                    ┌─────────▼─────────┐                            │
│                    │   Kong Gateway    │                            │
│                    │  (Auth & Rate)    │                            │
│                    └─────────┬─────────┘                            │
│                              │                                       │
│  ┌───────────────────────────┴───────────────────────────────────┐  │
│  │                    Core Services Layer                         │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │  │
│  │  │billing  │ │satellite│ │weather  │ │irrigat° │ │crop_ai  │ │  │
│  │  │ :8089   │ │ :8090   │ │ :8092   │ │ :8094   │ │ :8095   │ │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│  ┌───────────────────────────┴───────────────────────────────────┐  │
│  │                   Infrastructure Layer                         │  │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐              │  │
│  │  │PostGIS │  │ Redis  │  │  NATS  │  │  MQTT  │              │  │
│  │  │ :5432  │  │ :6379  │  │ :4222  │  │ :1883  │              │  │
│  │  └────────┘  └────────┘  └────────┘  └────────┘              │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## البدء السريع | Quick Start

### للمطورين الجدد | For New Developers

1. ابدأ بـ [REPOSITORY_STRUCTURE.md](./REPOSITORY_STRUCTURE.md) لفهم هيكل المشروع
2. اقرأ [FIELD_FIRST_ARCHITECTURE.md](./architecture/FIELD_FIRST_ARCHITECTURE.md) للمبادئ الأساسية
3. راجع [SERVICES_MAP.md](./SERVICES_MAP.md) لمعرفة الخدمات

### للمساهمة | For Contributors

1. راجع [ADRs](./adr/) قبل اتخاذ قرارات معمارية
2. اتبع [ARCH_RULES.md](./ARCH_RULES.md) للقواعد
3. حدّث التوثيق مع كل PR يغير السلوك

### للتشغيل | For Operations

1. [DEPLOYMENT.md](./DEPLOYMENT.md) للنشر
2. [RUNBOOKS.md](./RUNBOOKS.md) للحالات الطارئة
3. [OBSERVABILITY.md](./OBSERVABILITY.md) للمراقبة

---

## إحصائيات التوثيق | Documentation Stats

| المجلد | عدد الملفات | الحالة |
|--------|-------------|--------|
| architecture/ | 8 | ✅ Complete |
| adr/ | 8 | ✅ Complete |
| security/ | 2 | ✅ Complete |
| infrastructure/ | 3 | ✅ Complete |
| mobile/ | 5 | ✅ Complete |
| guides/ | 1 | 🔄 Growing |
| engineering/ | 2 | ✅ Complete |
| governance/ | 1 | ✅ Complete |
| compliance/ | 1 | ✅ Complete |
| tools/ | 1 | ✅ Complete |
| **الإجمالي** | **60+** | **✅ 8.2/10** |

---

## قواعد التوثيق | Documentation Rules

1. **كل PR يغير السلوك = تحديث docs**
2. **ADR لكل قرار معماري مهم**
3. **التوثيق بالعربية والإنجليزية**
4. **أمثلة عملية في كل ملف**
5. **تحديث README.md عند إضافة ملفات**

---

<p align="center">
  <strong>SAHOOL Unified Platform v15.5</strong><br>
  <sub>Documentation Hub - December 2025</sub><br>
  <sub>KAFAAT Engineering Team</sub>
</p>
