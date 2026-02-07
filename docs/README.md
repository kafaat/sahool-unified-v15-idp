# SAHOOL Documentation Index

# فهرس وثائق سهول

**SAHOOL** - National Agricultural Intelligence Platform | منصة الذكاء الزراعي الوطنية

**Version | الإصدار**: 16.0.0

---

## Quick Navigation | التنقل السريع

| Category | الفئة | Count |
|----------|-------|-------|
| [Getting Started](#getting-started--البدء) | البدء | 8 |
| [Architecture](#architecture--الهندسة-المعمارية) | الهندسة المعمارية | 18 |
| [API Reference](#api-reference--مرجع-واجهة-برمجة-التطبيقات) | مرجع API | 14 |
| [Services Documentation](#services-documentation--وثائق-الخدمات) | وثائق الخدمات | 16 |
| [Development Guides](#development-guides--أدلة-التطوير) | أدلة التطوير | 22 |
| [Security & Compliance](#security--compliance--الأمان-والامتثال) | الأمان والامتثال | 12 |
| [Operations & Monitoring](#operations--monitoring--العمليات-والمراقبة) | العمليات والمراقبة | 20 |
| [Agricultural Libraries](#agricultural-libraries--المكتبات-الزراعية) | المكتبات الزراعية | 16 |
| [AI/ML Documentation](#aiml-documentation--وثائق-الذكاء-الاصطناعي) | وثائق الذكاء الاصطناعي | 8 |
| [Reports & Audits](#reports--audits--التقارير-والمراجعات) | التقارير والمراجعات | 32 |

---

## Getting Started | البدء

Essential documents for new developers and deployment.

الوثائق الأساسية للمطورين الجدد والنشر.

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [DEPLOYMENT.md](./DEPLOYMENT.md) | دليل النشر | Complete deployment guide for Docker and Kubernetes | دليل النشر الكامل لـ Docker و Kubernetes |
| [DOCKER.md](./DOCKER.md) | دليل Docker | Docker configuration and container management | تكوين Docker وإدارة الحاويات |
| [ENVIRONMENT.md](./ENVIRONMENT.md) | متغيرات البيئة | Environment variables and configuration | متغيرات البيئة والتكوين |
| [REPOSITORY_STRUCTURE.md](./REPOSITORY_STRUCTURE.md) | هيكل المستودع | Complete repository structure overview | نظرة عامة على هيكل المستودع |
| [OPERATIONAL_SETUP.md](./OPERATIONAL_SETUP.md) | الإعداد التشغيلي | Initial operational setup guide | دليل الإعداد التشغيلي الأولي |
| [DEVELOPMENT_STATUS.md](./DEVELOPMENT_STATUS.md) | حالة التطوير | Current development status and progress | حالة التطوير الحالية والتقدم |
| [WINDOWS_COMMANDS.md](./WINDOWS_COMMANDS.md) | أوامر Windows | Windows-specific development commands | أوامر التطوير الخاصة بـ Windows |
| [MAKEFILE_COMMANDS_REFERENCE.md](./MAKEFILE_COMMANDS_REFERENCE.md) | مرجع أوامر Makefile | Complete Makefile commands reference | مرجع أوامر Makefile الكامل |
| [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) | استكشاف الأخطاء | Comprehensive troubleshooting guide | دليل استكشاف الأخطاء الشامل |

---

## Architecture | الهندسة المعمارية

System architecture, design decisions, and patterns.

هندسة النظام والقرارات التصميمية والأنماط.

### Core Architecture | الهندسة الأساسية

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [ARCHITECTURE_DIAGRAMS.md](./ARCHITECTURE_DIAGRAMS.md) | مخططات الهندسة | System architecture diagrams | مخططات هندسة النظام |
| [ARCH_RULES.md](./ARCH_RULES.md) | قواعد الهندسة | Architectural rules and constraints | القواعد والقيود المعمارية |
| [DATA_FLOW.md](./DATA_FLOW.md) | تدفق البيانات | Data flow patterns across services | أنماط تدفق البيانات عبر الخدمات |
| [EVENT_CATALOG.md](./EVENT_CATALOG.md) | كتالوج الأحداث | NATS event catalog and message schemas | كتالوج أحداث NATS ومخططات الرسائل |
| [GIS_ARCHITECTURE.md](./GIS_ARCHITECTURE.md) | هندسة GIS | PostGIS and geospatial architecture | هندسة PostGIS والنظم الجغرافية |
| [IDP_ARCHITECTURE.md](./IDP_ARCHITECTURE.md) | هندسة IDP | Internal Developer Platform architecture | هندسة منصة المطورين الداخلية |
| [INFRASTRUCTURE.md](./INFRASTRUCTURE.md) | البنية التحتية | Infrastructure overview and components | نظرة عامة على البنية التحتية |
| [PLATFORM_STRATEGY.md](./PLATFORM_STRATEGY.md) | استراتيجية المنصة | Platform strategy and vision | استراتيجية المنصة والرؤية |

### Architecture Decision Records (ADR) | سجلات القرارات المعمارية

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [adr/README.md](./adr/README.md) | فهرس ADR | ADR index and overview | فهرس ونظرة عامة على ADR |
| [adr/ADR-000-template.md](./adr/ADR-000-template.md) | قالب ADR | ADR template for new decisions | قالب ADR للقرارات الجديدة |
| [adr/ADR-001-offline-first-architecture.md](./adr/ADR-001-offline-first-architecture.md) | الهندسة دون اتصال | Offline-first mobile architecture decision | قرار هندسة التطبيق دون اتصال |
| [adr/ADR-002-riverpod-state-management.md](./adr/ADR-002-riverpod-state-management.md) | إدارة الحالة | Riverpod state management decision | قرار إدارة الحالة باستخدام Riverpod |
| [adr/ADR-003-drift-local-database.md](./adr/ADR-003-drift-local-database.md) | قاعدة البيانات المحلية | Drift local database decision | قرار قاعدة البيانات المحلية Drift |
| [adr/ADR-004-kong-api-gateway.md](./adr/ADR-004-kong-api-gateway.md) | بوابة Kong | Kong API Gateway decision | قرار بوابة Kong |
| [adr/ADR-005-nats-event-bus.md](./adr/ADR-005-nats-event-bus.md) | ناقل أحداث NATS | NATS event bus decision | قرار ناقل أحداث NATS |
| [adr/ADR-006-circuit-breaker.md](./adr/ADR-006-circuit-breaker.md) | قاطع الدائرة | Circuit breaker pattern decision | قرار نمط قاطع الدائرة |
| [adr/ADR-007-redis-caching.md](./adr/ADR-007-redis-caching.md) | تخزين Redis | Redis caching decision | قرار التخزين المؤقت باستخدام Redis |

### Architecture Subdirectory | دليل الهندسة الفرعي

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [architecture/PRINCIPLES.md](./architecture/PRINCIPLES.md) | المبادئ | Core architectural principles | المبادئ المعمارية الأساسية |
| [architecture/EVENT_SEQUENCES.md](./architecture/EVENT_SEQUENCES.md) | تسلسل الأحداث | Event sequence diagrams | مخططات تسلسل الأحداث |
| [architecture/FIELD_FIRST_ARCHITECTURE.md](./architecture/FIELD_FIRST_ARCHITECTURE.md) | هندسة الحقل أولاً | Field-first architecture design | تصميم هندسة الحقل أولاً |
| [architecture/FIELD_FIRST_ASSESSMENT.md](./architecture/FIELD_FIRST_ASSESSMENT.md) | تقييم الحقل أولاً | Field-first implementation assessment | تقييم تنفيذ الحقل أولاً |
| [architecture/FIELD_FIRST_IMPLEMENTATION_PLAN.md](./architecture/FIELD_FIRST_IMPLEMENTATION_PLAN.md) | خطة التنفيذ | Field-first implementation plan | خطة تنفيذ الحقل أولاً |
| [architecture/SERVICE_ACTIVATION_MAP.md](./architecture/SERVICE_ACTIVATION_MAP.md) | خريطة تنشيط الخدمات | Service activation and dependencies | تنشيط الخدمات والتبعيات |
| [architecture/ASSET_INVESTMENT_PLAN.md](./architecture/ASSET_INVESTMENT_PLAN.md) | خطة الاستثمار | Asset investment and prioritization | خطة الاستثمار في الأصول |
| [architecture/frontend-governance.md](./architecture/frontend-governance.md) | حوكمة الواجهة | Frontend governance standards | معايير حوكمة الواجهة الأمامية |

---

## API Reference | مرجع واجهة برمجة التطبيقات

API documentation, versioning, and integration guides.

وثائق واجهة برمجة التطبيقات والإصدارات وأدلة التكامل.

### API Gateway | بوابة API

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [API_GATEWAY.md](./API_GATEWAY.md) | بوابة API | Kong API Gateway documentation | وثائق بوابة Kong |
| [KONG_CONFIGURATION_GUIDE.md](./KONG_CONFIGURATION_GUIDE.md) | تكوين Kong | Kong configuration reference | مرجع تكوين Kong |
| [RATE_LIMITING.md](./RATE_LIMITING.md) | تحديد المعدل | Rate limiting policies and tiers | سياسات ومستويات تحديد المعدل |
| [rate-limiting-configuration.md](./rate-limiting-configuration.md) | تكوين تحديد المعدل | Detailed rate limiting configuration | تكوين تفصيلي لتحديد المعدل |
| [rate-limiting-implementation-summary.md](./rate-limiting-implementation-summary.md) | ملخص التنفيذ | Rate limiting implementation summary | ملخص تنفيذ تحديد المعدل |

### API Versioning | إصدارات API

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [API_VERSIONING_STRATEGY.md](./API_VERSIONING_STRATEGY.md) | استراتيجية الإصدارات | API versioning strategy | استراتيجية إصدارات API |
| [API_VERSIONING_QUICK_REFERENCE.md](./API_VERSIONING_QUICK_REFERENCE.md) | مرجع سريع | Quick reference for API versioning | مرجع سريع لإصدارات API |
| [API_V2_MIGRATION_GUIDE.md](./API_V2_MIGRATION_GUIDE.md) | دليل الترحيل | V1 to V2 API migration guide | دليل ترحيل API من V1 إلى V2 |

### API Documentation | وثائق API

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [API_COMPREHENSIVE.md](./API_COMPREHENSIVE.md) | دليل API الشامل | Comprehensive API developer guide | دليل المطور الشامل لـ API |
| [api/README.md](./api/README.md) | فهرس API | API documentation index | فهرس وثائق API |
| [api/authentication.md](./api/authentication.md) | المصادقة | Authentication API reference | مرجع API المصادقة |
| [api/fields.md](./api/fields.md) | الحقول | Fields API reference | مرجع API الحقول |
| [api/sensors.md](./api/sensors.md) | المستشعرات | Sensors API reference | مرجع API المستشعرات |
| [api/weather.md](./api/weather.md) | الطقس | Weather API reference | مرجع API الطقس |
| [api/ai.md](./api/ai.md) | الذكاء الاصطناعي | AI API reference | مرجع API الذكاء الاصطناعي |
| [api/IMPLEMENTATION_SUMMARY.md](./api/IMPLEMENTATION_SUMMARY.md) | ملخص التنفيذ | API implementation summary | ملخص تنفيذ API |
| [api/openapi/README.md](./api/openapi/README.md) | OpenAPI | OpenAPI specifications | مواصفات OpenAPI |

---

## Services Documentation | وثائق الخدمات

Microservices documentation and service maps.

وثائق الخدمات المصغرة وخرائط الخدمات.

### Service Overview | نظرة عامة على الخدمات

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [BACKEND_SERVICES_DOCUMENTATION.md](./BACKEND_SERVICES_DOCUMENTATION.md) | وثائق الخدمات الخلفية | Complete backend services documentation | وثائق كاملة للخدمات الخلفية |
| [SERVICES_MAP.md](./SERVICES_MAP.md) | خريطة الخدمات | Service map and relationships | خريطة الخدمات والعلاقات |
| [SERVICE_CONSOLIDATION_MAP.md](./SERVICE_CONSOLIDATION_MAP.md) | خريطة الدمج | Service consolidation mapping | خريطة دمج الخدمات |
| [SERVICE_PORTFOLIO_REVIEW.md](./SERVICE_PORTFOLIO_REVIEW.md) | مراجعة المحفظة | Service portfolio review | مراجعة محفظة الخدمات |
| [DEPRECATED_SERVICES.md](./DEPRECATED_SERVICES.md) | الخدمات المهملة | Deprecated services reference | مرجع الخدمات المهملة |
| [LEGACY_SERVICES.md](./LEGACY_SERVICES.md) | الخدمات القديمة | Legacy services documentation | وثائق الخدمات القديمة |
| [KERNEL_SERVICES_MERGE_PLAN.md](./KERNEL_SERVICES_MERGE_PLAN.md) | خطة دمج النواة | Kernel services merge plan | خطة دمج خدمات النواة |

### Service-Kong Mappings | تعيينات الخدمات وKong

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [kong-backend-services-api-mapping.md](./kong-backend-services-api-mapping.md) | تعيين Kong-Backend | Kong to backend services API mapping | تعيين Kong إلى API الخدمات الخلفية |
| [database-schema-mapping.md](./database-schema-mapping.md) | تعيين مخطط قاعدة البيانات | Database schema to service mapping | تعيين مخطط قاعدة البيانات إلى الخدمات |
| [web-kong-services-mapping.md](./web-kong-services-mapping.md) | تعيين الويب-Kong | Web app to Kong services mapping | تعيين تطبيق الويب إلى خدمات Kong |
| [mobile-kong-services-mapping.md](./mobile-kong-services-mapping.md) | تعيين الجوال-Kong | Mobile app to Kong services mapping | تعيين تطبيق الجوال إلى خدمات Kong |
| [admin-kong-services-mapping.md](./admin-kong-services-mapping.md) | تعيين الإدارة-Kong | Admin portal to Kong services mapping | تعيين بوابة الإدارة إلى خدمات Kong |

### Specific Services | خدمات محددة

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [ASTRONOMICAL_CALENDAR_SERVICE.md](./ASTRONOMICAL_CALENDAR_SERVICE.md) | خدمة التقويم الفلكي | Islamic calendar and astronomical timings | التقويم الإسلامي والتوقيتات الفلكية |
| [BILLING_QUOTAS.md](./BILLING_QUOTAS.md) | حصص الفواتير | Billing quotas and limits | حصص وحدود الفواتير |
| [FEATURE_FLAGS.md](./FEATURE_FLAGS.md) | علامات الميزات | Feature flags configuration | تكوين علامات الميزات |

---

## Development Guides | أدلة التطوير

Guides for developers working on SAHOOL.

أدلة للمطورين العاملين على سهول.

### Database | قاعدة البيانات

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [DATABASE_CONFIGURATION_GUIDE.md](./DATABASE_CONFIGURATION_GUIDE.md) | دليل تكوين قاعدة البيانات | Database configuration guide | دليل تكوين قاعدة البيانات |
| [DATABASE_CONNECTION_POOLING.md](./DATABASE_CONNECTION_POOLING.md) | تجميع الاتصالات | PgBouncer connection pooling | تجميع الاتصالات باستخدام PgBouncer |
| [DATABASE_QUERY_OPTIMIZATIONS.md](./DATABASE_QUERY_OPTIMIZATIONS.md) | تحسين الاستعلامات | Database query optimization guide | دليل تحسين استعلامات قاعدة البيانات |
| [DATABASE_TLS_CONFIGURATION.md](./DATABASE_TLS_CONFIGURATION.md) | تكوين TLS | Database TLS configuration | تكوين TLS لقاعدة البيانات |
| [MIGRATIONS.md](./MIGRATIONS.md) | الترحيل | Database migrations guide | دليل ترحيل قاعدة البيانات |

### ORM & Data Access | ORM والوصول للبيانات

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [ORM_STANDARDIZATION.md](./ORM_STANDARDIZATION.md) | توحيد ORM | ORM standardization guide | دليل توحيد ORM |
| [ORM_DOCUMENTATION_INDEX.md](./ORM_DOCUMENTATION_INDEX.md) | فهرس وثائق ORM | ORM documentation index | فهرس وثائق ORM |
| [ORM_MIGRATION_QUICK_REFERENCE.md](./ORM_MIGRATION_QUICK_REFERENCE.md) | مرجع ترحيل ORM | ORM migration quick reference | مرجع سريع لترحيل ORM |
| [ORM_AUDIT_SUMMARY.md](./ORM_AUDIT_SUMMARY.md) | ملخص تدقيق ORM | ORM audit summary | ملخص تدقيق ORM |
| [PRISMA_SERVICE_TEMPLATE.md](./PRISMA_SERVICE_TEMPLATE.md) | قالب خدمة Prisma | Prisma service template | قالب خدمة Prisma |

### Testing | الاختبار

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [TESTING.md](./TESTING.md) | دليل الاختبار | Testing guide and best practices | دليل الاختبار وأفضل الممارسات |
| [TEST_COVERAGE_ANALYSIS.md](./TEST_COVERAGE_ANALYSIS.md) | تحليل التغطية | Test coverage analysis | تحليل تغطية الاختبار |

### Middleware & Shared Code | البرمجيات الوسيطة والكود المشترك

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [SHARED_MIDDLEWARE_GUIDE.md](./SHARED_MIDDLEWARE_GUIDE.md) | دليل البرمجيات الوسيطة | Shared middleware guide | دليل البرمجيات الوسيطة المشتركة |
| [MIDDLEWARE_ADOPTION_REPORT.md](./MIDDLEWARE_ADOPTION_REPORT.md) | تقرير تبني البرمجيات الوسيطة | Middleware adoption report | تقرير تبني البرمجيات الوسيطة |
| [UNIFIED_PACKAGES_GUIDE.md](./UNIFIED_PACKAGES_GUIDE.md) | دليل الحزم الموحدة | Unified packages guide | دليل الحزم الموحدة |

### Mobile Development | تطوير الجوال

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [MOBILE_API_INTEGRATION_GUIDE.md](./MOBILE_API_INTEGRATION_GUIDE.md) | دليل تكامل API للجوال | Mobile API integration guide | دليل تكامل API للجوال |
| [MOBILE_ARCHITECTURE_ANALYSIS.md](./MOBILE_ARCHITECTURE_ANALYSIS.md) | تحليل هندسة الجوال | Mobile architecture analysis | تحليل هندسة الجوال |
| [MOBILE_VOICE_COMMANDS.md](./MOBILE_VOICE_COMMANDS.md) | الأوامر الصوتية | Voice commands implementation | تنفيذ الأوامر الصوتية |

### Web Development | تطوير الويب

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [WEB_APP_DEVELOPMENT_PLAN.md](./WEB_APP_DEVELOPMENT_PLAN.md) | خطة تطوير الويب | Web app development plan | خطة تطوير تطبيق الويب |
| [WEB_DASHBOARD_API_INTEGRATION_GUIDE.md](./WEB_DASHBOARD_API_INTEGRATION_GUIDE.md) | دليل تكامل لوحة المعلومات | Dashboard API integration guide | دليل تكامل API لوحة المعلومات |

### Integration Guides | أدلة التكامل

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [guides/FIELD_FIRST_INTEGRATION_GUIDE.md](./guides/FIELD_FIRST_INTEGRATION_GUIDE.md) | دليل تكامل الحقل أولاً | Field-first integration guide | دليل تكامل الحقل أولاً |
| [OPEN_SOURCE_INTEGRATION.md](./OPEN_SOURCE_INTEGRATION.md) | تكامل المصادر المفتوحة | Open source integration guide | دليل تكامل المصادر المفتوحة |
| [VERSIONS_AND_DEPENDENCIES.md](./VERSIONS_AND_DEPENDENCIES.md) | الإصدارات والتبعيات | Versions and dependencies reference | مرجع الإصدارات والتبعيات |

---

## Security & Compliance | الأمان والامتثال

Security documentation and compliance guides.

وثائق الأمان وأدلة الامتثال.

### Security Guides | أدلة الأمان

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [SECURITY.md](./SECURITY.md) | دليل الأمان | Security overview and best practices | نظرة عامة على الأمان وأفضل الممارسات |
| [SECURITY_HARDENING.md](./SECURITY_HARDENING.md) | تعزيز الأمان | Security hardening guide | دليل تعزيز الأمان |
| [TLS_CONFIGURATION.md](./TLS_CONFIGURATION.md) | تكوين TLS | TLS/SSL configuration | تكوين TLS/SSL |
| [CERTIFICATE_ROTATION.md](./CERTIFICATE_ROTATION.md) | تدوير الشهادات | Certificate rotation procedures | إجراءات تدوير الشهادات |
| [CERTIFICATE_ROTATION_QUICKSTART.md](./CERTIFICATE_ROTATION_QUICKSTART.md) | بدء سريع للتدوير | Quick start for certificate rotation | بدء سريع لتدوير الشهادات |
| [REFRESH_TOKEN_ROTATION.md](./REFRESH_TOKEN_ROTATION.md) | تدوير رموز التحديث | Refresh token rotation | تدوير رموز التحديث |
| [file-upload-validation-summary.md](./file-upload-validation-summary.md) | التحقق من رفع الملفات | File upload validation summary | ملخص التحقق من رفع الملفات |

### Secrets Management | إدارة الأسرار

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [SECRETS_MANAGEMENT.md](./SECRETS_MANAGEMENT.md) | إدارة الأسرار | Secrets management with Vault | إدارة الأسرار باستخدام Vault |
| [SECRETS_SETUP.md](./SECRETS_SETUP.md) | إعداد الأسرار | Secrets setup guide | دليل إعداد الأسرار |
| [SECRETS_ROTATION_POLICY.md](./SECRETS_ROTATION_POLICY.md) | سياسة تدوير الأسرار | Secrets rotation policy | سياسة تدوير الأسرار |
| [SECRETS_GITOPS.md](./SECRETS_GITOPS.md) | GitOps للأسرار | GitOps secrets management | إدارة الأسرار باستخدام GitOps |

### Security Subdirectory | دليل الأمان الفرعي

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [security/DATA_CLASSIFICATION.md](./security/DATA_CLASSIFICATION.md) | تصنيف البيانات | Data classification policy | سياسة تصنيف البيانات |
| [security/THREAT_MODEL_STRIDE.md](./security/THREAT_MODEL_STRIDE.md) | نموذج التهديد STRIDE | STRIDE threat model | نموذج التهديد STRIDE |

### Compliance | الامتثال

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [compliance/COMPLIANCE_CHECKLIST.md](./compliance/COMPLIANCE_CHECKLIST.md) | قائمة التحقق من الامتثال | Compliance checklist | قائمة التحقق من الامتثال |
| [governance/DEPENDENCY_MANAGEMENT.md](./governance/DEPENDENCY_MANAGEMENT.md) | إدارة التبعيات | Dependency management policy | سياسة إدارة التبعيات |

---

## Operations & Monitoring | العمليات والمراقبة

Operations, monitoring, and incident management.

العمليات والمراقبة وإدارة الحوادث.

### Observability | الملاحظة

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [OBSERVABILITY.md](./OBSERVABILITY.md) | دليل الملاحظة | Observability guide (metrics, logs, traces) | دليل الملاحظة (المقاييس، السجلات، التتبع) |
| [SLO_SLI_GUIDE.md](./SLO_SLI_GUIDE.md) | دليل SLO/SLI | SLO/SLI definitions and targets | تعريفات وأهداف SLO/SLI |
| [HEALTH_ENDPOINTS_IMPLEMENTATION_GUIDE.md](./HEALTH_ENDPOINTS_IMPLEMENTATION_GUIDE.md) | دليل نقاط الصحة | Health endpoints implementation guide | دليل تنفيذ نقاط فحص الصحة |

### Operations | العمليات

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [OPERATIONS.md](./OPERATIONS.md) | دليل العمليات | Operations guide | دليل العمليات |
| [RUNBOOKS.md](./RUNBOOKS.md) | دفاتر التشغيل | Incident runbooks | دفاتر تشغيل الحوادث |
| [backup-strategy.md](./backup-strategy.md) | استراتيجية النسخ الاحتياطي | Backup strategy and procedures | استراتيجية وإجراءات النسخ الاحتياطي |

### Deployment | النشر

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [DEPLOYMENT_STRATEGIES.md](./DEPLOYMENT_STRATEGIES.md) | استراتيجيات النشر | Deployment strategies (blue-green, canary) | استراتيجيات النشر (blue-green، canary) |
| [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md) | نشر الإنتاج | Production deployment guide | دليل نشر الإنتاج |
| [PREVIEW_DEPLOYMENT.md](./PREVIEW_DEPLOYMENT.md) | نشر المعاينة | Preview environment deployment | نشر بيئة المعاينة |
| [PR_PREVIEW_ENVIRONMENTS.md](./PR_PREVIEW_ENVIRONMENTS.md) | بيئات معاينة PR | PR preview environments | بيئات معاينة طلبات السحب |
| [PR_PREVIEW_URLS.md](./PR_PREVIEW_URLS.md) | عناوين URL للمعاينة | PR preview URLs | عناوين URL لمعاينة طلبات السحب |
| [MULTI_REGION.md](./MULTI_REGION.md) | المناطق المتعددة | Multi-region deployment | النشر متعدد المناطق |

### NATS Messaging | رسائل NATS

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [NATS_CLUSTER_SETUP.md](./NATS_CLUSTER_SETUP.md) | إعداد عنقود NATS | NATS cluster setup | إعداد عنقود NATS |
| [NATS_MONITORING.md](./NATS_MONITORING.md) | مراقبة NATS | NATS monitoring guide | دليل مراقبة NATS |
| [NATS_NKEY_SETUP.md](./NATS_NKEY_SETUP.md) | إعداد NKey | NATS NKey authentication setup | إعداد مصادقة NKey لـ NATS |

### Disaster Recovery | التعافي من الكوارث

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [disaster-recovery/README.md](./disaster-recovery/README.md) | فهرس التعافي من الكوارث | Disaster recovery index | فهرس التعافي من الكوارث |
| [disaster-recovery/DR_RUNBOOK.md](./disaster-recovery/DR_RUNBOOK.md) | دفتر تشغيل التعافي | Disaster recovery runbook | دفتر تشغيل التعافي من الكوارث |
| [disaster-recovery/IMPLEMENTATION_GUIDE.md](./disaster-recovery/IMPLEMENTATION_GUIDE.md) | دليل التنفيذ | DR implementation guide | دليل تنفيذ التعافي من الكوارث |

### CI/CD | التكامل والتسليم المستمر

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [GITHUB_WORKFLOWS_REFERENCE.md](./GITHUB_WORKFLOWS_REFERENCE.md) | مرجع GitHub Workflows | GitHub Actions workflows reference | مرجع سير عمل GitHub Actions |
| [CI_TROUBLESHOOTING.md](./CI_TROUBLESHOOTING.md) | استكشاف أخطاء CI | CI troubleshooting guide | دليل استكشاف أخطاء CI |
| [CI_ISSUES_RESOLVED.md](./CI_ISSUES_RESOLVED.md) | مشاكل CI المحلولة | Resolved CI issues | مشاكل CI المحلولة |

### Infrastructure | البنية التحتية

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [infrastructure/CIRCUIT_BREAKER.md](./infrastructure/CIRCUIT_BREAKER.md) | قاطع الدائرة | Circuit breaker implementation | تنفيذ قاطع الدائرة |
| [infrastructure/KONG_HA_SETUP.md](./infrastructure/KONG_HA_SETUP.md) | إعداد Kong HA | Kong high availability setup | إعداد Kong عالي التوفر |
| [infrastructure/POSTGIS_OPTIMIZATION.md](./infrastructure/POSTGIS_OPTIMIZATION.md) | تحسين PostGIS | PostGIS optimization guide | دليل تحسين PostGIS |

---

## Agricultural Libraries | المكتبات الزراعية

Agricultural domain modules and knowledge base.

وحدات المجال الزراعي وقاعدة المعرفة.

### Core Agricultural Documentation | وثائق الزراعة الأساسية

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [AGRICULTURAL_LIBRARIES.md](./AGRICULTURAL_LIBRARIES.md) | المكتبات الزراعية | Complete agricultural libraries documentation | وثائق كاملة للمكتبات الزراعية |
| [FIRMWARE_AND_IOT_DEVICES.md](./FIRMWARE_AND_IOT_DEVICES.md) | البرامج الثابتة وأجهزة IoT | IoT devices and firmware documentation | وثائق أجهزة IoT والبرامج الثابتة |

### Knowledge Base | قاعدة المعرفة

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [knowledge-base/README.md](./knowledge-base/README.md) | فهرس قاعدة المعرفة | Agricultural knowledge base index | فهرس قاعدة المعرفة الزراعية |

#### Crops | المحاصيل

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [knowledge-base/crops/README.md](./knowledge-base/crops/README.md) | فهرس المحاصيل | Crops documentation index | فهرس وثائق المحاصيل |
| [knowledge-base/crops/wheat.md](./knowledge-base/crops/wheat.md) | القمح | Wheat cultivation guide | دليل زراعة القمح |
| [knowledge-base/crops/barley.md](./knowledge-base/crops/barley.md) | الشعير | Barley cultivation guide | دليل زراعة الشعير |
| [knowledge-base/crops/dates.md](./knowledge-base/crops/dates.md) | التمور | Date palm cultivation guide | دليل زراعة النخيل |

#### Diseases & Pests | الأمراض والآفات

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [knowledge-base/diseases/README.md](./knowledge-base/diseases/README.md) | فهرس الأمراض | Diseases documentation index | فهرس وثائق الأمراض |
| [knowledge-base/diseases/fungal.md](./knowledge-base/diseases/fungal.md) | الأمراض الفطرية | Fungal diseases guide | دليل الأمراض الفطرية |
| [knowledge-base/diseases/pests.md](./knowledge-base/diseases/pests.md) | الآفات | Pests identification and control | تحديد الآفات ومكافحتها |

#### Irrigation | الري

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [knowledge-base/irrigation/README.md](./knowledge-base/irrigation/README.md) | فهرس الري | Irrigation documentation index | فهرس وثائق الري |
| [knowledge-base/irrigation/drip.md](./knowledge-base/irrigation/drip.md) | الري بالتنقيط | Drip irrigation guide | دليل الري بالتنقيط |
| [knowledge-base/irrigation/scheduling.md](./knowledge-base/irrigation/scheduling.md) | جدولة الري | Irrigation scheduling guide | دليل جدولة الري |

#### Best Practices | أفضل الممارسات

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [knowledge-base/best-practices/README.md](./knowledge-base/best-practices/README.md) | فهرس أفضل الممارسات | Best practices index | فهرس أفضل الممارسات |
| [knowledge-base/best-practices/sustainable-farming.md](./knowledge-base/best-practices/sustainable-farming.md) | الزراعة المستدامة | Sustainable farming practices | ممارسات الزراعة المستدامة |

#### Monitoring | المراقبة

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [knowledge-base/monitoring/remote-sensing-ai.md](./knowledge-base/monitoring/remote-sensing-ai.md) | الاستشعار عن بعد والذكاء الاصطناعي | Remote sensing and AI monitoring | مراقبة الاستشعار عن بعد والذكاء الاصطناعي |

---

## AI/ML Documentation | وثائق الذكاء الاصطناعي

AI and machine learning documentation.

وثائق الذكاء الاصطناعي والتعلم الآلي.

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [AI_ARCHITECTURE.md](./AI_ARCHITECTURE.md) | هندسة الذكاء الاصطناعي | AI/ML architecture (RAG pipeline, LLM) | هندسة الذكاء الاصطناعي (RAG، LLM) |
| [OLLAMA_INTEGRATION.md](./OLLAMA_INTEGRATION.md) | تكامل Ollama | Local LLM integration with Ollama | تكامل LLM المحلي مع Ollama |
| [MCP_INTEGRATION.md](./MCP_INTEGRATION.md) | تكامل MCP | Model Context Protocol integration | تكامل بروتوكول سياق النموذج |
| [A2A_IMPLEMENTATION_SUMMARY.md](./A2A_IMPLEMENTATION_SUMMARY.md) | ملخص A2A | Agent-to-Agent implementation summary | ملخص تنفيذ Agent-to-Agent |
| [proposals/AI_CODE_AGENT_PROPOSAL.md](./proposals/AI_CODE_AGENT_PROPOSAL.md) | اقتراح وكيل الكود | AI code agent proposal | اقتراح وكيل الكود بالذكاء الاصطناعي |

---

## Reports & Audits | التقارير والمراجعات

Audit reports, reviews, and analysis documents.

تقارير المراجعة والتحليل.

### Documentation Reports | تقارير التوثيق

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [DOCUMENTATION_AUDIT_REPORT.md](./DOCUMENTATION_AUDIT_REPORT.md) | تقرير تدقيق التوثيق | Documentation audit report | تقرير تدقيق التوثيق |
| [DOCUMENTATION_GAPS_REPORT.md](./DOCUMENTATION_GAPS_REPORT.md) | تقرير الفجوات | Documentation gaps report | تقرير فجوات التوثيق |
| [COMPREHENSIVE_AUDIT_REPORT.md](./COMPREHENSIVE_AUDIT_REPORT.md) | تقرير التدقيق الشامل | Comprehensive audit report | تقرير التدقيق الشامل |

### Platform Reports | تقارير المنصة

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [FUTURE_ROADMAP.md](./FUTURE_ROADMAP.md) | خريطة الطريق المستقبلية | Future roadmap and plans | خريطة الطريق والخطط المستقبلية |
| [PLATFORM_ROADMAP_NEXT.md](./PLATFORM_ROADMAP_NEXT.md) | الخطوات التالية | Next platform roadmap steps | الخطوات التالية في خريطة طريق المنصة |
| [PHASE1_DEPENDENCY_ANALYSIS.md](./PHASE1_DEPENDENCY_ANALYSIS.md) | تحليل التبعيات | Phase 1 dependency analysis | تحليل تبعيات المرحلة الأولى |
| [PHASE_D_MAJOR_UPGRADES_PLAN.md](./PHASE_D_MAJOR_UPGRADES_PLAN.md) | خطة الترقيات الرئيسية | Major upgrades plan | خطة الترقيات الرئيسية |
| [CHANGELOG_ARCHITECTURE.md](./CHANGELOG_ARCHITECTURE.md) | سجل تغييرات الهندسة | Architecture changelog | سجل تغييرات الهندسة |
| [CHANGELOG_FIX_GITHUB_ACTIONS.md](./CHANGELOG_FIX_GITHUB_ACTIONS.md) | إصلاحات GitHub Actions | GitHub Actions fixes changelog | سجل إصلاحات GitHub Actions |

### Application Reports | تقارير التطبيقات

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [MOBILE_APP_AUDIT_REPORT.md](./MOBILE_APP_AUDIT_REPORT.md) | تقرير تدقيق الجوال | Mobile app audit report | تقرير تدقيق تطبيق الجوال |
| [MOBILE_APP_REVIEW_REPORT.md](./MOBILE_APP_REVIEW_REPORT.md) | تقرير مراجعة الجوال | Mobile app review report | تقرير مراجعة تطبيق الجوال |
| [ADMIN_WEB_AUDIT_REPORT.md](./ADMIN_WEB_AUDIT_REPORT.md) | تقرير تدقيق الإدارة | Admin portal audit report | تقرير تدقيق بوابة الإدارة |
| [AUTH_UX_AUDIT_REPORT.md](./AUTH_UX_AUDIT_REPORT.md) | تقرير تجربة المصادقة | Authentication UX audit | تقرير تدقيق تجربة المصادقة |
| [FRONTEND_REVIEW_SUMMARY.md](./FRONTEND_REVIEW_SUMMARY.md) | ملخص مراجعة الواجهة | Frontend review summary | ملخص مراجعة الواجهة الأمامية |

### Reports Subdirectory | دليل التقارير الفرعي

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [reports/REPO_MAP.md](./reports/REPO_MAP.md) | خريطة المستودع | Repository map | خريطة المستودع |
| [reports/BACKEND_AUDIT_REPORT_v16.3.md](./reports/BACKEND_AUDIT_REPORT_v16.3.md) | تقرير تدقيق الخلفية | Backend audit report v16.3 | تقرير تدقيق الخلفية v16.3 |
| [reports/FINAL_REVIEW_REPORT.md](./reports/FINAL_REVIEW_REPORT.md) | التقرير النهائي | Final review report | التقرير النهائي للمراجعة |
| [reports/COMPREHENSIVE_REVIEW_REPORT_AR.md](./reports/COMPREHENSIVE_REVIEW_REPORT_AR.md) | تقرير المراجعة الشامل | Comprehensive review (Arabic) | تقرير المراجعة الشامل بالعربية |
| [reports/DATABASE_SCHEMA_ANALYSIS_AR.md](./reports/DATABASE_SCHEMA_ANALYSIS_AR.md) | تحليل مخطط قاعدة البيانات | Database schema analysis (Arabic) | تحليل مخطط قاعدة البيانات بالعربية |
| [reports/PROJECT_GAPS_AND_SOLUTIONS.md](./reports/PROJECT_GAPS_AND_SOLUTIONS.md) | الفجوات والحلول | Project gaps and solutions | فجوات المشروع والحلول |
| [reports/PROJECT_GAPS_SUMMARY_AR.md](./reports/PROJECT_GAPS_SUMMARY_AR.md) | ملخص الفجوات | Project gaps summary (Arabic) | ملخص فجوات المشروع بالعربية |
| [reports/DEVELOPMENT_PLAN.md](./reports/DEVELOPMENT_PLAN.md) | خطة التطوير | Development plan | خطة التطوير |
| [reports/ACTION_PLAN_IMPROVEMENTS.md](./reports/ACTION_PLAN_IMPROVEMENTS.md) | خطة التحسينات | Action plan improvements | خطة التحسينات |
| [reports/SERVICES_DOCUMENTATION.md](./reports/SERVICES_DOCUMENTATION.md) | وثائق الخدمات | Services documentation | وثائق الخدمات |
| [reports/SAHOOL_SERVICES_API_DOCUMENTATION.md](./reports/SAHOOL_SERVICES_API_DOCUMENTATION.md) | وثائق API للخدمات | SAHOOL services API documentation | وثائق API لخدمات سهول |
| [reports/DASHBOARD_REVIEW_REPORT.md](./reports/DASHBOARD_REVIEW_REPORT.md) | تقرير مراجعة لوحة المعلومات | Dashboard review report | تقرير مراجعة لوحة المعلومات |
| [reports/FRONTEND_OPTIMIZATION_REPORT.md](./reports/FRONTEND_OPTIMIZATION_REPORT.md) | تقرير تحسين الواجهة | Frontend optimization report | تقرير تحسين الواجهة الأمامية |
| [reports/IMPLEMENTATION_SUMMARY.md](./reports/IMPLEMENTATION_SUMMARY.md) | ملخص التنفيذ | Implementation summary | ملخص التنفيذ |
| [reports/IMPLEMENTATION_SUMMARY_COMPREHENSIVE.md](./reports/IMPLEMENTATION_SUMMARY_COMPREHENSIVE.md) | ملخص التنفيذ الشامل | Comprehensive implementation summary | ملخص التنفيذ الشامل |
| [reports/INFRASTRUCTURE_VERIFICATION_REPORT.md](./reports/INFRASTRUCTURE_VERIFICATION_REPORT.md) | تقرير التحقق من البنية | Infrastructure verification report | تقرير التحقق من البنية التحتية |
| [reports/COMPETITIVE_GAP_ANALYSIS_FIELD_VIEW.md](./reports/COMPETITIVE_GAP_ANALYSIS_FIELD_VIEW.md) | تحليل الفجوة التنافسية | Competitive gap analysis | تحليل الفجوة التنافسية |
| [reports/COMPETITIVE_GAP_REVIEW.md](./reports/COMPETITIVE_GAP_REVIEW.md) | مراجعة الفجوة التنافسية | Competitive gap review | مراجعة الفجوة التنافسية |
| [reports/JWT_GUARDS_IMPLEMENTATION_REPORT.md](./reports/JWT_GUARDS_IMPLEMENTATION_REPORT.md) | تقرير حراس JWT | JWT guards implementation report | تقرير تنفيذ حراس JWT |
| [reports/TOKEN_REVOCATION_COMPLETE_REPORT.md](./reports/TOKEN_REVOCATION_COMPLETE_REPORT.md) | تقرير إلغاء الرموز | Token revocation complete report | تقرير إلغاء الرموز الكامل |
| [reports/PASSWORD_MIGRATION_SUMMARY.md](./reports/PASSWORD_MIGRATION_SUMMARY.md) | ملخص ترحيل كلمات المرور | Password migration summary | ملخص ترحيل كلمات المرور |
| [reports/CORS_SECURITY_FIX_SUMMARY.md](./reports/CORS_SECURITY_FIX_SUMMARY.md) | ملخص إصلاح CORS | CORS security fix summary | ملخص إصلاح أمان CORS |
| [reports/RATE_LIMITING_FIX_SUMMARY.md](./reports/RATE_LIMITING_FIX_SUMMARY.md) | ملخص إصلاح تحديد المعدل | Rate limiting fix summary | ملخص إصلاح تحديد المعدل |
| [reports/REDIS_SENTINEL_IMPLEMENTATION.md](./reports/REDIS_SENTINEL_IMPLEMENTATION.md) | تنفيذ Redis Sentinel | Redis Sentinel implementation | تنفيذ Redis Sentinel |
| [reports/DOCKER_DEPLOYMENT.md](./reports/DOCKER_DEPLOYMENT.md) | نشر Docker | Docker deployment report | تقرير نشر Docker |
| [reports/TESTS_SUMMARY.md](./reports/TESTS_SUMMARY.md) | ملخص الاختبارات | Tests summary | ملخص الاختبارات |
| [reports/TEST_FIXES_SUMMARY.md](./reports/TEST_FIXES_SUMMARY.md) | ملخص إصلاحات الاختبارات | Test fixes summary | ملخص إصلاحات الاختبارات |
| [reports/WEATHER_FEATURE_UPDATE_SUMMARY.md](./reports/WEATHER_FEATURE_UPDATE_SUMMARY.md) | ملخص تحديث الطقس | Weather feature update summary | ملخص تحديث ميزة الطقس |
| [reports/TASK_ASTRONOMICAL_INTEGRATION_RECOMMENDATIONS.md](./reports/TASK_ASTRONOMICAL_INTEGRATION_RECOMMENDATIONS.md) | توصيات التكامل الفلكي | Astronomical integration recommendations | توصيات تكامل التقويم الفلكي |
| [reports/SAHOOL_MOBILE_APP_DEVELOPMENT_PROMPT.md](./reports/SAHOOL_MOBILE_APP_DEVELOPMENT_PROMPT.md) | تطوير تطبيق الجوال | Mobile app development prompt | موجه تطوير تطبيق الجوال |
| [reports/AUTO_AUDIT_TOOLS_BENEFITS_REPORT.md](./reports/AUTO_AUDIT_TOOLS_BENEFITS_REPORT.md) | فوائد أدوات التدقيق | Auto audit tools benefits | فوائد أدوات التدقيق الآلي |

### Tools | الأدوات

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [tools/PLATFORM_TOOLS.md](./tools/PLATFORM_TOOLS.md) | أدوات المنصة | Platform development tools | أدوات تطوير المنصة |

### Engineering | الهندسة

| Document | الوثيقة | Description | الوصف |
|----------|---------|-------------|-------|
| [engineering/ENGINEERING_RECOVERY_PLAN.md](./engineering/ENGINEERING_RECOVERY_PLAN.md) | خطة الاسترداد الهندسي | Engineering recovery plan | خطة الاسترداد الهندسي |
| [engineering/RECOVERY_SPRINT_TRACKER.md](./engineering/RECOVERY_SPRINT_TRACKER.md) | متتبع سبرنت الاسترداد | Recovery sprint tracker | متتبع سبرنت الاسترداد |

---

## Document Statistics | إحصائيات الوثائق

- **Total Documents**: 145+
- **Categories**: 10
- **Languages**: Arabic & English (Bilingual)
- **Last Updated**: February 2026

---

## Contributing | المساهمة

For contribution guidelines, see the main [CONTRIBUTING.md](../CONTRIBUTING.md) file.

للاطلاع على إرشادات المساهمة، راجع ملف [CONTRIBUTING.md](../CONTRIBUTING.md) الرئيسي.

### Documentation Guidelines | إرشادات التوثيق

When adding new documentation:

1. Place the document in the appropriate category directory
2. Update this index with the new document
3. Include both English and Arabic descriptions
4. Follow the naming convention: `UPPERCASE_WITH_UNDERSCORES.md` for root docs, `lowercase-with-hyphens.md` for subdirectories

عند إضافة وثائق جديدة:

1. ضع الوثيقة في دليل الفئة المناسبة
2. قم بتحديث هذا الفهرس بالوثيقة الجديدة
3. قم بتضمين الأوصاف بالإنجليزية والعربية
4. اتبع اتفاقية التسمية: `UPPERCASE_WITH_UNDERSCORES.md` للوثائق الجذرية، `lowercase-with-hyphens.md` للأدلة الفرعية

---

_Last Updated | آخر تحديث: February 2026_
