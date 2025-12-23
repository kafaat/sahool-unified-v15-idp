# SAHOOL Mobile App Documentation
# توثيق تطبيق سهول المحمول

> **الإصدار:** v16.1 | **المنصة:** Flutter | **الحالة:** Production

---

## نظرة عامة | Overview

تطبيق SAHOOL المحمول مصمم بمنهجية **Offline-First** لضمان عمل المزارعين في المناطق الريفية بدون اتصال إنترنت مستمر.

### المبادئ الأساسية | Core Principles

```
┌─────────────────────────────────────────────────────────────────┐
│                    OFFLINE-FIRST MOBILE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1️⃣ Local-First    → البيانات محلية أولاً                       │
│  2️⃣ Sync-Later     → المزامنة عند توفر الاتصال                  │
│  3️⃣ Conflict-Safe  → حل التعارضات تلقائياً                      │
│  4️⃣ Field-Ready    → جاهز للميدان دائماً                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## فهرس التوثيق | Documentation Index

| الملف | الوصف | الأهمية |
|-------|-------|---------|
| [OFFLINE_FIRST.md](./OFFLINE_FIRST.md) | استراتيجية Offline-First الكاملة | 🔴 حرج |
| [SYNC_ENGINE.md](./SYNC_ENGINE.md) | محرك المزامنة وآلية العمل | 🔴 حرج |
| [CONFLICT_RESOLUTION.md](./CONFLICT_RESOLUTION.md) | حل التعارضات بين الأجهزة | 🟡 مهم |
| [CACHING_STRATEGY.md](./CACHING_STRATEGY.md) | استراتيجية التخزين المؤقت | 🟡 مهم |

---

## الهيكل التقني | Technical Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      MOBILE APP LAYERS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    UI Layer (Flutter)                        ││
│  │  • Riverpod State Management                                ││
│  │  • Responsive Widgets                                        ││
│  │  • Offline-aware Components                                  ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                  Domain Layer (Use Cases)                    ││
│  │  • Business Logic                                            ││
│  │  • Validation Rules                                          ││
│  │  • Field Operations                                          ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                  Data Layer (Repositories)                   ││
│  │  • Local Database (Drift/SQLite)                            ││
│  │  • Remote API (Dio + Retrofit)                              ││
│  │  • Sync Queue                                                ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                  Infrastructure Layer                        ││
│  │  • Connectivity Monitor                                      ││
│  │  • Background Sync Worker                                    ││
│  │  • Push Notifications (Firebase)                            ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## التقنيات المستخدمة | Technology Stack

| المكون | التقنية | الإصدار | الغرض |
|--------|---------|---------|-------|
| Framework | Flutter | 3.24+ | واجهة المستخدم |
| State Management | Riverpod | 2.5+ | إدارة الحالة |
| Local Database | Drift | 2.20+ | قاعدة بيانات محلية |
| HTTP Client | Dio | 5.7+ | طلبات API |
| Code Generation | Freezed | 2.5+ | Data Classes |
| Push Notifications | Firebase | Latest | الإشعارات |
| Background Work | Workmanager | 0.5+ | المزامنة الخلفية |

---

## تدفق البيانات | Data Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                       DATA FLOW DIAGRAM                           │
└──────────────────────────────────────────────────────────────────┘

    ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
    │   User      │         │   Local     │         │   Remote    │
    │   Action    │────────▶│   Database  │────────▶│   Server    │
    └─────────────┘         └─────────────┘         └─────────────┘
          │                       │                       │
          │   1. Save locally     │   3. Sync when online │
          │                       │                       │
          ▼                       ▼                       ▼
    ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
    │   Instant   │         │   Queued    │         │   Confirmed │
    │   Response  │         │   Changes   │         │   & Merged  │
    └─────────────┘         └─────────────┘         └─────────────┘

    Timeline:
    ═════════════════════════════════════════════════════════════
    │ Offline ──────────────────────│ Online ───────────────────│
    │ (Works normally)              │ (Auto-sync happens)       │
    ═════════════════════════════════════════════════════════════
```

---

## السيناريوهات الرئيسية | Key Scenarios

### 1. إنشاء مهمة ميدانية (Offline)

```
المزارع                    التطبيق                    الخادم
   │                          │                          │
   │──"أضف مهمة ري"──────────▶│                          │
   │                          │                          │
   │                          │──حفظ محلي + Queue──────▶ │
   │                          │                          │
   │◀──"تم الحفظ ✓"───────────│                          │
   │                          │                          │
   │        [لاحقاً - عند توفر الإنترنت]                  │
   │                          │                          │
   │                          │──مزامنة تلقائية─────────▶│
   │                          │                          │
   │                          │◀─────"تم التأكيد"────────│
   │                          │                          │
```

### 2. تلقي تنبيه (Online → Offline)

```
الخادم                     التطبيق                    المزارع
   │                          │                          │
   │──Push: "تنبيه ري"───────▶│                          │
   │                          │                          │
   │                          │──حفظ محلي──────────────▶ │
   │                          │                          │
   │                          │──عرض الإشعار───────────▶ │
   │                          │                          │
   │        [لاحقاً - بدون إنترنت]                        │
   │                          │                          │
   │          ✗               │◀──"عرض التنبيه"──────────│
   │                          │                          │
   │                          │──قراءة من Cache─────────▶│
   │                          │                          │
```

---

## حدود التخزين | Storage Limits

| نوع البيانات | الحد الأقصى | مدة الاحتفاظ | الأولوية |
|-------------|-------------|--------------|----------|
| المهام | 1000 مهمة | 90 يوم | 🔴 عالية |
| التنبيهات | 500 تنبيه | 30 يوم | 🟡 متوسطة |
| الصور المؤقتة | 100 صورة | 7 أيام | 🟢 منخفضة |
| بيانات الطقس | 7 أيام | 24 ساعة | 🟡 متوسطة |
| بيانات الحقول | غير محدود | دائم | 🔴 عالية |

---

## مؤشرات الأداء | Performance Metrics

### أهداف SLO

| المقياس | الهدف | الحالة |
|---------|-------|--------|
| Cold Start | < 3 ثواني | ✅ |
| Hot Start | < 1 ثانية | ✅ |
| Sync Latency | < 5 ثواني | ✅ |
| Offline Read | < 100ms | ✅ |
| Battery Impact | < 5%/ساعة | ✅ |

---

## الأمان | Security

- **تشفير البيانات:** AES-256 للبيانات المحلية
- **المصادقة:** JWT مع Refresh Token
- **Biometric:** دعم Face ID / Fingerprint
- **Certificate Pinning:** للاتصالات الحساسة

---

## الموارد ذات الصلة | Related Resources

- [ADR-001: Offline-First Architecture](../adr/ADR-001-offline-first-architecture.md)
- [ADR-002: Riverpod State Management](../adr/ADR-002-riverpod-state-management.md)
- [ADR-003: Drift Local Database](../adr/ADR-003-drift-local-database.md)
- [FIELD_FIRST_ARCHITECTURE](../architecture/FIELD_FIRST_ARCHITECTURE.md)
- [MOBILE_APP_REVIEW_REPORT](../MOBILE_APP_REVIEW_REPORT.md)

---

<p align="center">
  <strong>SAHOOL Mobile v16.1</strong><br>
  <sub>Offline-First Field Application</sub><br>
  <sub>December 2025</sub>
</p>
