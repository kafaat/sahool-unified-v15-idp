# تقرير المراجعة المعمّقة الشاملة والموحّدة — بوابة الإدارة (Admin) و لوحة المعلومات (Web)

# Unified Comprehensive Deep Review — Admin Portal & Web Dashboard

> **تاريخ التوحيد:** 2026-04-07 · **الإصدار:** 16.0.0  
> **المصادر:** AUDIT_REPORT.md (Admin)، ADMIN_PORTAL_REVIEW.md، WEB_APP_DETAILED_REVIEW.md، SECURITY_AUDIT_REPORT.md (Web)، SECURITY_ENHANCEMENTS.md، SECURITY_FIXES_APPLIED.md، CSRF_IMPLEMENTATION_SUMMARY.md، CSRF_PROTECTION.md، CSP_IMPLEMENTATION_SUMMARY.md  
> **الحالة:** تقرير موحّد نهائي — لا تكرار

---

## الفهرس | Table of Contents

1. [ملخص تنفيذي](#1-ملخص-تنفيذي--executive-summary)
2. [البنية والتكوين](#2-البنية-والتكوين--architecture--configuration)
3. [التبعيات](#3-التبعيات--dependencies)
4. [الأمان الشامل](#4-الأمان-الشامل--comprehensive-security)
5. [تصنيف الصفحات](#5-تصنيف-الصفحات--page-classification)
6. [مكونات الواجهة](#6-مكونات-الواجهة--ui-components)
7. [تكامل API](#7-تكامل-api--api-integration)
8. [الأداء](#8-الأداء--performance)
9. [الاختبارات](#9-الاختبارات--testing)
10. [التعريب والوصول](#10-التعريب-والوصول--i18n--accessibility)
11. [الوضع الداكن](#11-الوضع-الداكن--dark-mode)
12. [جدول المشاكل الموحّد](#12-جدول-المشاكل-الموحّد--unified-issues-table)
13. [أفضل الأنماط المتبعة والمعمارية المرجعية](#13-أفضل-الأنماط-المتبعة-والمعمارية-المرجعية--best-practices--reference-patterns)
14. [حالة الأيقونات ونظام التصميم](#14-حالة-الأيقونات-ونظام-التصميم--icon-system--design-status)
15. [الهياكل والأكواد الناقصة مع أمثلة](#15-الهياكل-والأكواد-الناقصة-مع-أمثلة--missing-structures--code-examples)
16. [الاختبارات المطلوبة تفصيلياً](#16-الاختبارات-المطلوبة-تفصيلياً--required-tests-detailed)
17. [مقترحات التحسين المفصلة](#17-مقترحات-التحسين-المفصلة--detailed-improvement-proposals)
18. [خطة العمل](#18-خطة-العمل--action-plan)
19. [نتائج التحقق العميق](#19-نتائج-التحقق-العميق--deep-verification-results)
20. [النقاط الإيجابية](#20-النقاط-الإيجابية--positive-highlights)

---

## 1. ملخص تنفيذي | Executive Summary

### التقييم العام | Overall Scores

| المقياس | Admin Portal | Web Dashboard |
|---------|:------------:|:-------------:|
| **التقييم الكلي** | **B+ (85/100)** | **7.75/10** |
| **الأمان** | 8.5/10 🔒 | 9/10 🔒 |
| **جودة الكود** | 8/10 📝 | 8/10 📝 |
| **Type Safety** | 9/10 ⚡ | 8/10 ⚡ |
| **المعمارية** | 8/10 🏗️ | 8/10 🏗️ |
| **الأداء** | 8/10 ⚡ | 8/10 ⚡ |
| **الاختبارات** | 7/10 🧪 | 5/10 🧪 |
| **إمكانية الوصول** | 7/10 ♿ | 8/10 ♿ |
| **مكونات الواجهة** | 7/10 🎨 | 6/10 🎨 |
| **جاهزية الإنتاج** | 85% 🎯 | 78% 🎯 |

### أهم النتائج | Key Findings

**Admin Portal:**
- ✅ 0 أخطاء TypeScript — الوضع الصارم مفعّل
- ✅ لا توجد ثغرات أمنية حرجة
- ⚠️ ~116 تحذير ESLint (متغيرات/استيرادات غير مستخدمة)
- ⚠️ 4 ثغرات npm متوسطة (تبعيات عابرة)
- ⚠️ 8 صفحات هيكلية (Stub) و 20 صفحة بيانات وهمية فقط
- ⚠️ `edgeLogger` يُسكت جميع السجلات في الإنتاج

**Web Dashboard:**
- ✅ 3 مشاكل أمنية حرجة تم إصلاحها سابقاً
- ✅ أمان على مستوى الإنتاج (CSP, CSRF, JWT, HSTS)
- ✅ تقسيم الكود ممتاز (12 dynamic wrapper، ~600KB+ توفير)
- ⚠️ لا يوجد شريط جانبي متجاوب للهواتف
- ⚠️ `edgeLogger` يُسكت أخطاء الأمان في الإنتاج
- ⚠️ 12 مكون UI فقط — يحتاج توسيع

---

## 2. البنية والتكوين | Architecture & Configuration

### 2.1 الإطار التقني | Tech Stack (مشترك)

| التقنية | Admin | Web |
|---------|-------|-----|
| Next.js | 15.5.12 | 15.5.12 |
| React | 19.2.4 | 19.2.4 |
| TypeScript | 5.9.3 (strict) | 5.9.3 (strict) |
| Tailwind CSS | 3.4.17 | 3.4.x (shared config) |
| Testing | Vitest 3.2.4 | Vitest + Playwright |
| JWT | jose 5.9.6+ | jose (Edge-compatible) |
| Sanitization | xss 1.0.15 | safe-sanitizer.ts |

### 2.2 هيكل المسارات | Route Structure

**Admin Portal — 60 صفحة:**
```
(auth)/         → صفحات المصادقة العامة (login, register, OTP, forgot/reset password)
/               → إعادة توجيه إلى /dashboard
dashboard/      → لوحة التحكم الرئيسية
analytics/      → field-compare, profitability, satellite, soil, yield, gap-analysis, yield-forecasting
precision-agriculture/ → fertilizer, gdd, spray, vra, pivot
reports/        → seasonal
settings/       → إعدادات عامة + security + sessions
+ 40 صفحة أخرى (diseases, users, farms, sensors, copilot, tasks, alerts, etc.)
```

**Web Dashboard — 94+ مسار:**
```
(auth)/         → صفحات المصادقة العامة (login, register, OTP)
(dashboard)/    → 37+ مسار محمي (fields, weather, tasks, analytics, etc.)
api/            → 20 مسار API جانب الخادم (auth, CSRF, health, etc.)
```

### 2.3 تسلسل المزودين | Provider Hierarchy

**Admin:** `ThemeProvider` → `AuthProvider` → Pages  
**Web:** `ThemeProvider` → `AuthProvider` → `ToastProvider` → Dashboard: `QueryClientProvider`  
> ✅ Web يفصل QueryClientProvider في لوحة التحكم فقط — صفحات المصادقة لا تحمّل React Query (ممتاز)

### 2.4 حدود الأخطاء | Error Boundaries

| الميزة | Admin | Web |
|--------|-------|-----|
| Error Boundary Component | ✅ | ✅ |
| Development Stack Traces | ✅ | ✅ |
| Server-side Logging | ✅ via Sentry (lazy) | ✅ via `/api/log-error` |
| Error ID References | ✅ | ✅ |
| Retry Mechanism | ✅ | ✅ |
| Bilingual Messages | ✅ | ✅ |
| Granular Isolation | — | ✅ Sidebar + Header + Content each separate |

---

## 3. التبعيات | Dependencies

### 3.1 Admin Portal — التبعيات الرئيسية (17 إنتاج + 1 اختياري)

| الحزمة | الإصدار | الغرض | الحالة |
|---------|---------|-------|--------|
| react / react-dom | ^19.2.4 | إطار الواجهة | ✅ حديث |
| next | 15.5.12 | الإطار | ✅ حديث |
| axios | 1.13.6 | عميل HTTP | ✅ حديث |
| jose | 5.9.6 | JWT (متوافق مع Edge) | ✅ حديث |
| xss | ^1.0.15 | تطهير XSS | ✅ حديث |
| leaflet / react-leaflet | 1.9.4 / 4.2.1 | خرائط | ✅ حديث |
| recharts | 2.15.4 | رسوم بيانية | ✅ حديث |
| lucide-react | 0.575.0 | أيقونات | ✅ حديث |
| @sahool/api-client | ^16.0.0 | عميل API مشترك | ✅ داخلي |
| @sahool/shared-types | ^16.0.0 | أنواع مشتركة | ✅ داخلي |
| @opentelemetry/api | ^1.9.0 | تتبع | ✅ حديث |
| clsx / tailwind-merge | 2.1.1 / 2.6.0 | أدوات CSS | ✅ حديث |
| date-fns | 4.1.0 | تواريخ | ✅ حديث |
| js-cookie | 3.0.5 | إدارة الكوكيز | ✅ حديث |
| @sentry/nextjs | ^9.5.0 | تتبع الأخطاء (اختياري) | ✅ حديث |

**⚠️ ثغرات معروفة (4 متوسطة — تبعيات عابرة):**
- lodash (عبر @nestjs/config, @nestjs/swagger) — Prototype Pollution
- next — Unbounded Memory Consumption عبر PPR Resume Endpoint

### 3.2 Web Dashboard — تبعيات إضافية

| الحزمة | الغرض |
|---------|-------|
| next-intl | التعريب والتدويل |
| @tanstack/react-query | إدارة حالة الخادم |
| react-focus-lock | قفل التركيز في Modals |
| maplibre-gl | خرائط Vector |

---

## 4. الأمان الشامل | Comprehensive Security

### 4.1 المصادقة والتفويض | Authentication & Authorization

| الميزة | Admin | Web | الملف |
|--------|:-----:|:---:|-------|
| JWT بتحقق التوقيع (jose) | ✅ | ✅ | `middleware.ts` |
| httpOnly Cookies | ✅ | ✅ | `unified-client.ts` |
| RBAC (admin/supervisor/viewer) | ✅ | ✅ | `middleware.ts` |
| Idle Timeout (30 دقيقة) | ✅ | ✅ | `middleware.ts` |
| 2FA / OTP | ✅ | ✅ | صفحات auth |
| BroadcastChannel (sync logout) | — | ✅ | `auth.store.tsx` |
| UUID validation لـ tenant_id | — | ✅ | `auth.store.tsx` |
| E2E test mode gated | — | ✅ | `NODE_ENV=development` فقط |
| Rate Limiting (5 محاولات/15 دقيقة) | ✅ | — | `middleware.ts` |
| Backup Codes | ✅ | — | `settings/security` |

### 4.2 CSRF Protection (تم تطبيقه 2026-01-06)

| الميزة | التفاصيل |
|--------|----------|
| **الاستراتيجية** | طبقة مزدوجة: SameSite Cookies + CSRF Tokens |
| **الطبقة الأولى** | SameSite=Strict cookies (حماية أساسية) |
| **الطبقة الثانية** | CSRF tokens — 32 بايت عشوائي تشفيري |
| **المقارنة** | Timing-safe comparison (مقاومة لهجمات التوقيت) |
| **الاستثناءات** | `/api/auth/login`, `/api/auth/register`, `/api/webhooks` |
| **الأساليب المحمية** | POST, PUT, DELETE, PATCH |
| **الكوكيز** | `csrf_token` (httpOnly) + `_csrf` (قابل للقراءة من العميل) |
| **التغطية الاختبارية** | 100% — 35/35 اختبار (79 إجمالي) |
| **التوافق** | 99.8% من المتصفحات (Chrome 51+, Firefox 60+, Safari 12+, Edge 16+) |
| **الملفات** | `middleware.ts`, `csrf-server.ts`, `/api/csrf-token/route.ts` |

**⚠️ مشكلة (Web فقط):** لا يتم تدوير CSRF token عند الإجراءات الحساسة (تغيير كلمة المرور/تسجيل الدخول). الخطورة منخفضة بسبب SameSite=Strict.

### 4.3 Content Security Policy — CSP (تم تطبيقه 2025-12-30)

| الميزة | التفاصيل |
|--------|----------|
| **النوع** | Nonce-based (يزيل الحاجة لـ unsafe-inline) |
| **الإنتاج** | يزيل unsafe-eval |
| **التوجيهات** | 12 توجيه صارم |
| **الإبلاغ** | `/api/csp-report` مع rate limiting (100 تقرير/دقيقة/IP) |
| **البيئة** | سياسات مختلفة لـ dev و prod |

**التوجيهات الرئيسية:**
```
default-src: 'self'
script-src: 'self' 'nonce-{random}'
style-src: 'self' 'nonce-{random}' fonts.googleapis.com
img-src: 'self' data: https: blob:
frame-ancestors: 'none'
object-src: 'none'
upgrade-insecure-requests (production)
```

**الملفات المُنشأة (8 ملفات):**
- `csp-config.ts` (311 سطر) — التكوين الأساسي
- `nonce.ts` (129 سطر) — أدوات Nonce
- `/api/csp-report/route.ts` (146 سطر) — استقبال الإبلاغات
- `csp-example.tsx` (365 سطر) — أمثلة الاستخدام
- `csp-config.test.ts` (333 سطر) — الاختبارات
- `CSP_README.md`, `CSP_MIGRATION.md`, `CSP_QUICK_REFERENCE.md`

### 4.4 رؤوس الأمان | Security Headers

| الرأس | Admin | Web | القيمة |
|-------|:-----:|:---:|--------|
| HSTS | ✅ | ✅ | `max-age=31536000; includeSubDomains; preload` (2 سنة) |
| X-Frame-Options | ✅ | ✅ | `DENY` |
| X-Content-Type-Options | ✅ | ✅ | `nosniff` |
| Referrer-Policy | ✅ | ✅ | `strict-origin-when-cross-origin` |
| X-XSS-Protection | ✅ | ✅ | `1; mode=block` |
| Permissions-Policy | ✅ | ✅ | camera=(), microphone=(), geolocation=(self) |
| Content-Security-Policy | ✅ (nonce) | ✅ (nonce) | انظر القسم 4.3 |

### 4.5 حماية XSS | XSS Prevention

| الميزة | Admin | Web |
|--------|-------|-----|
| مكتبة تطهير | `xss` library | `safe-sanitizer.ts` (282 سطر) |
| لا `dangerouslySetInnerHTML` | ✅ لا يوجد | ✅ أمثلة تعليمية فقط |
| CSP nonce-based | ✅ | ✅ |
| Input validation | `lib/validation.ts` | `lib/validation.ts` (375 سطر) |
| URL validation | http/https فقط | http/https فقط |
| File Upload validation | 50MB, JPEG/PNG/WebP/TIFF | موجود (يحتاج مراجعة) |

### 4.6 التحقق من المدخلات | Input Validation

**المدققات المشتركة:**
- ✅ البريد الإلكتروني (RFC 5322, حد 254 حرف)
- ✅ الهاتف (تنسيق يمني +967 + دولي)
- ✅ كلمة المرور (8+ حرف, uppercase, lowercase, رقم, خاص)
- ✅ رمز 2FA (6 أرقام بالضبط)
- ✅ URL (http/https فقط)
- ✅ Safe Text (كشف HTML, protocols, event handlers, encoding bypasses)
- ✅ رفع الملفات (MIME whitelist, حد الحجم)

**خاص بـ Admin:**
- ✅ Weather Route: UUID field_id, lat/lon range, days 1-30 clamp

### 4.7 إدارة الأسرار | Secrets Management

- ✅ لا أسرار مشفرة في الكود (تم التحقق بـ grep)
- ✅ لا `Math.random()` في كود الإنتاج (Admin محقق — في ملفي اختبار فقط)
- ✅ `JWT_SECRET` جانب الخادم فقط (لا `NEXT_PUBLIC_`)
- ✅ `API_GATEWAY_URL` runtime فقط (Kong: `http://kong-gateway:8000`)
- ✅ `NEXT_PUBLIC_API_URL` آمن (fallback فقط، بدون أسرار)
- ✅ `console.*` في 3 ملفات إنتاج فقط (Admin: logger.ts, middleware.ts, api-middleware.ts)

### 4.8 التحسينات الأمنية المُطبقة (ديسمبر 2025 — يناير 2026)

| # | المشكلة الأصلية | الإصلاح | التأثير |
|---|----------------|---------|---------|
| 1 | كوكيز غير آمنة | أضيف `secure: true`, `sameSite: "strict"` | ✅ حماية من CSRF + اعتراض الشبكة |
| 2 | عدم وجود CSP | تطبيق CSP شامل مع nonce | ✅ حماية من XSS |
| 3 | تحليل كوكيز غير آمن | استبدال بمكتبة `js-cookie` | ✅ تحليل موثوق |
| 4 | JWT بدون تحقق توقيع | إضافة تحقق التوقيع بـ jose | ✅ حماية من التزوير |
| 5 | عدم وجود CSRF tokens | تطبيق طبقة مزدوجة | ✅ حماية شاملة |
| 6 | رؤوس أمان ضعيفة | HSTS + Permissions-Policy | ✅ defense-in-depth |
| 7 | Open redirect | `sanitizeReturnUrl()` | ✅ منع التحويلات المفتوحة |

**تحسين الدرجة الأمنية:** 6/10 → **9/10** (+50% تحسين)

---

## 5. تصنيف الصفحات | Page Classification

### 5.1 Admin Portal — 60 صفحة

| التصنيف | العدد | الوصف |
|---------|:-----:|-------|
| **FULL** (API حقيقي) | 16 | تكامل كامل مع الخدمات الخلفية |
| **MEDIUM** (API + fallback) | 16 | تحاول API أولاً، تراجع وهمي عند الفشل |
| **MOCK** (بيانات وهمية فقط) | 20 | واجهة واقعية بدون تكامل خلفي |
| **STUB** (هيكلية) | 8 | 78 سطر لكل صفحة، أرقام مشفرة |

<details>
<summary><strong>قائمة الصفحات FULL (16 صفحة) — API حقيقي</strong></summary>

| الصفحة | الأسطر | مصدر API | الميزات |
|--------|--------|---------|---------|
| `/dashboard` | 560 | `fetchDashboardStats`, `fetchFarms` | إحصائيات، قائمة مزارع، طقس |
| `/diseases` | 553 | `fetchDiagnoses`, `updateDiagnosisStatus` | شبكة بطاقات، modal، تأكيد/رفض/علاج |
| `/users` | 662 | `fetchUsers`, `updateUser`, `deleteUser` | CRUD، إدارة أدوار |
| `/farms` | 405 | `fetchFarms` | قائمة مزارع، satellite modal |
| `/sensors` | 745 | `iotService` (CRUD) | CRUD كامل، قراءات |
| `/epidemic` | 477 | `fetchDiagnoses`, `fetchDiagnosisStats` | خريطة حرارية، أمراض |
| `/copilot` | 1,074 | `axios` → copilot endpoints | RAG، سجلات الحراسة، 4 تبويبات |
| `/tasks` | 862 | `fetchTasks`, `createTask`, `updateTask` | إدارة مهام كاملة |
| `/alerts` | 782 | `fetchAlerts`, `updateAlertStatus` | إدارة تنبيهات |
| `/settings` | 1,310 | `fetchSettings`, `updateSettings` | إعدادات النظام |
| `/(auth)/login` | 355 | Zustand auth store | 2FA, backup codes |
| `/(auth)/register` | 287 | `/api/auth/register` | نموذج تسجيل |
| `/(auth)/forgot-password` | 280 | `/api/auth/forgot-password` | OTP متعدد القنوات |
| `/(auth)/reset-password` | 303 | `/api/auth/reset-password` | إعادة تعيين بالرمز |
| `/(auth)/verify-otp` | 541 | `/api/auth/verify-otp` | 6 أرقام، 5 دقائق انتهاء |
| `/settings/security` | 528 | `/admin/2fa` endpoints | إعداد/تحقق/تعطيل 2FA |

</details>

<details>
<summary><strong>قائمة الصفحات MEDIUM (16 صفحة) — API مع تراجع وهمي</strong></summary>

| الصفحة | الأسطر | النمط |
|--------|--------|-------|
| `/weather` | 633 | Proxy عبر `/api/weather` |
| `/yield` | 404 | `apiClient.post` → mock on catch |
| `/traceability` | 371 | `Promise.allSettled` → MOCK |
| `/support` | 537 | `apiClient.get` → mock on catch |
| `/equipment` | 1,061 | `apiClient.get` → mock on catch |
| `/analytics/field-compare` | 683 | `field.list` → mock fallback |
| `/analytics/profitability` | 310 | `fetchProfitabilityData` → fallback |
| `/analytics/satellite` | 513 | `fetchSatelliteData` → fallback |
| `/analytics/soil` | 385 | `/api/soil-analysis` → fallback |
| `/analytics/yield` | 449 | `Promise.allSettled` → fallback |
| `/precision-agriculture/fertilizer` | 752 | `/api/advisory/fertilizer` → fallback |
| `/precision-agriculture/gdd` | 276 | `fetchGDDData` → fallback |
| `/precision-agriculture/spray` | 402 | `Promise.all` → fallback |
| `/precision-agriculture/vra` | 311 | `fetchVRAPrescriptions` → fallback |
| `/reports/seasonal` | 566 | `/api/v1/reports/seasonal` → fallback |
| `/settings/sessions` | 270 | `/api/admin/sessions` |

</details>

<details>
<summary><strong>قائمة الصفحات MOCK (20 صفحة) — بيانات وهمية</strong></summary>

crop-health, compliance, disasters, logistics, research, community, marketplace, insurance, market-prices, irrigation, inventory, seeds, seasons, cooperatives, soil-map, lab, analytics/gap-analysis, analytics/yield-forecasting, precision-agriculture/pivot, equipment/fleet-tracking

</details>

<details>
<summary><strong>قائمة الصفحات STUB (8 صفحات) — هيكلية فقط</strong></summary>

`/` (15 سطر — redirect), `/vision`, `/terrain`, `/edge-devices`, `/audit`, `/scouting`, `/drone`, `/virtual-sensors`  
— جميعها 78 سطر، 4 بطاقات إحصاء بأرقام مشفرة + "سيتم عرض ... هنا"

</details>

### 5.2 Web Dashboard — هيكل المسارات

| المنطقة | المسارات | الحالة |
|---------|:--------:|--------|
| (auth) | 5+ | ✅ تكامل كامل |
| (dashboard) | 37+ | ✅ معظمها بتكامل API |
| api | 20 | ✅ مسارات جانب الخادم |

---

## 6. مكونات الواجهة | UI Components

### 6.1 مكونات Web المُراجعة

| المكون | التقييم | الميزات |
|--------|:-------:|---------|
| **Button** | 9/10 | 5 أنماط، 3 أحجام، loading، RTL-aware (`ms-`/`me-`)، `aria-busy/disabled` |
| **Modal** | 9/10 | Focus lock، Escape، focus restore، 5 أحجام، `aria-modal/labelledby/describedby` |
| **Toast** | 8/10 | Lazy icons (~5KB)، auto-dismiss، `aria-live="polite"` |
| **ErrorBoundary** | 9/10 | Server logging، retry، HOC wrapper، bilingual |

### 6.2 المكونات المفقودة (Web)

| المكون | الأولوية | السبب |
|--------|:--------:|-------|
| **Table/DataGrid** | عالية | مطلوب لقوائم الحقول والمهام |
| **Select/Dropdown** | عالية | لا يوجد مكون select مخصص |
| **Tabs** | عالية | مطلوب لصفحات التفاصيل |
| **Date Picker** | عالية | مطلوب لميزات المواسم/التقويم |
| **Map Component** | عالية | wrapper قابل لإعادة الاستخدام |
| **Breadcrumb** | متوسطة | سياق التنقل |
| **Avatar** | متوسطة | عرض ملف المستخدم |
| **Pagination** | متوسطة | تصفح القوائم |
| **Skeleton** | متوسطة | placeholders (موجود في dashboard فقط) |
| **Alert/Banner** | متوسطة | إشعارات inline |
| **Progress** | منخفضة | تقدم الرفع/المزامنة |
| **Tooltip** | منخفضة | تلميحات |

### 6.3 مكونات Admin

- ✅ استخدام `React.memo` لبعض المكونات
- ✅ Dynamic imports للخرائط والرسوم البيانية
- ⚠️ أزرار التصدير معطلة ("قريبًا") في ~10 صفحات
- ⚠️ أزرار العرض/التفاصيل معطلة في صفحات stub

---

## 7. تكامل API | API Integration

### 7.1 سلسلة API (مشتركة)

```
@sahool/api-client (حزمة مشتركة)
  → unified-client.ts (CSRF interceptor, httpOnly cookies, retry)
    → api.ts / client.ts (دوال API المركزية)
      → hooks (React Query integration — Web فقط)
        → مكونات الصفحات
```

### 7.2 نقاط القوة

| الميزة | Admin | Web |
|--------|:-----:|:---:|
| CSRF Header Injection | ✅ | ✅ |
| httpOnly Cookies | ✅ | ✅ |
| Token Refresh | ✅ (queuing) | ✅ (proxy `/api/auth/refresh`) |
| Retry + Exponential Backoff | ✅ | ✅ (3 محاولات, 1s-30s) |
| HTTPS Enforcement | ✅ (prod) | ✅ (prod) |
| Server-side Proxying | ✅ via next.config.js | ✅ via next.config.js |
| React Query | — | ✅ centralized hooks |
| Type-safe Methods | ✅ 40+ functions | ✅ 965-line client |

### 7.3 مشاكل API

| # | المشكلة | التطبيق | الخطورة |
|---|---------|---------|---------|
| API-1 | لا يوجد mutation hooks مركزية | Web | متوسطة |
| API-2 | WebSocket بدون connection pooling | Web | منخفضة |
| API-3 | API URL fallback إلى سلسلة فارغة | Web | منخفضة |
| API-4 | CORS مفتوح في `/api/csp-report` (`*`) | Admin | عالية |

---

## 8. الأداء | Performance

### 8.1 التحسينات المُطبقة

| التحسين | Admin | Web |
|---------|:-----:|:---:|
| Dynamic Imports (SSR: false) | ✅ خرائط + رسوم | ✅ **12 wrapper** (~600KB+) |
| Chunk Splitting | ✅ charts, maps, framework | ✅ charts, maps, framework |
| Package Import Optimization | ✅ | ✅ (14 حزمة) |
| Lazy Icons | — | ✅ Toast (~5KB) |
| Async CSS | — | ✅ Leaflet CSS |
| Self-hosted Fonts | — | ✅ Tajawal WOFF2 + CDN fallback |
| Query Scoping | — | ✅ Dashboard layout فقط |
| Standalone Output (Docker) | ✅ | ✅ |
| Console Stripping (prod) | ✅ | ✅ |
| Source Maps Disabled (prod) | ✅ | ✅ |

### 8.2 تقسيم الكود (Web — محقق بالتعمق)

| ملف Dynamic Wrapper | المكون | التوفير |
|---------------------|--------|---------|
| `LazyRecharts.dynamic.tsx` | 15 مكون Recharts | ~120KB |
| `MapView.dynamic.tsx` | MapLibre GL JS | ~200KB |
| `FieldMap.dynamic.tsx` | خريطة الحقل | ~50KB |
| `InteractiveFieldMap.dynamic.tsx` | خريطة تفاعلية | ~50KB |
| `ComparisonChart.dynamic.tsx` | رسوم المقارنة | ~30KB |
| `CostAnalysis.dynamic.tsx` | تحليل التكاليف | ~30KB |
| `YieldAnalysis.dynamic.tsx` | تحليل الإنتاجية | ~30KB |
| `YieldChart.dynamic.tsx` | رسم الإنتاجية | ~30KB |
| `SensorChart.dynamic.tsx` | رسوم IoT | ~30KB |
| `SensorReadings.dynamic.tsx` | بيانات الحساسات | ~20KB |
| `ObservationMarker.dynamic.tsx` | علامات الخريطة | ~15KB |
| `ScoutingMode.dynamic.tsx` | واجهة الاستكشاف | ~20KB |
| **المجموع** | | **~625KB+** |

### 8.3 مشاكل الأداء

| # | المشكلة | التطبيق | الخطورة |
|---|---------|---------|---------|
| PERF-1 | لا يوجد `next/image` wrapper | Web | متوسطة |
| PERF-2 | Route prefetching لـ 15 رابط (~750KB) | Web | متوسطة |
| PERF-3 | Edge middleware optimization | ✅ كلاهما | محلول |

---

## 9. الاختبارات | Testing

### 9.1 إحصائيات المقارنة

| المقياس | Admin | Web |
|---------|:-----:|:---:|
| **ملفات الاختبار** | 52 | 74 (47 unit + 27 E2E) |
| **حالات الاختبار** | 1,044 | — |
| **اختبارات وهمية** (expect(true)) | **0** ✅ | — |
| **اختبارات متخطاة** (skip) | **0** ✅ | — |
| **إطار Unit** | Vitest | Vitest |
| **إطار E2E** | Playwright (مستوى المشروع) | Playwright (27 ملف) |

### 9.2 المناطق المُختبرة جيداً

**Admin:**
- ✅ API route handlers (weather, auth, middleware)
- ✅ CSRF interceptor behavior
- ✅ Component rendering
- ✅ Utility functions
- ✅ Mock data factories
- ✅ Security middleware

**Web:**
- ✅ Security: CSP, CSRF, JWT, nonce validation (6 ملفات)
- ✅ Auth store: state, security, contracts (4 ملفات)
- ✅ API client: routes, auth (3 ملفات)
- ✅ UI components: Button, Modal, Toast (2 ملفات)
- ✅ E2E: Auth flows, navigation, forms, responsive, accessibility (27 spec)

### 9.3 فجوات الاختبار

| الفجوة | Admin | Web | الأولوية |
|--------|:-----:|:---:|:--------:|
| اختبارات مستوى الميزات | — | ⚠️ 37 ميزة بدون اختبار | عالية |
| اختبارات Hooks | — | ⚠️ `useFormValidation` فقط | عالية |
| اختبارات التكامل (API → UI) | — | ⚠️ | متوسطة |
| Snapshot tests | — | ⚠️ | منخفضة |
| Performance tests (Web Vitals) | — | ⚠️ | منخفضة |

### 9.4 جودة E2E (Web)

- ✅ Multi-browser (Chromium, Firefox, WebKit)
- ✅ Mobile viewport (Pixel 5, iPhone 12)
- ✅ CI adaptations (2 workers, 1 retry)
- ✅ Screenshots/video on failure
- ⚠️ `responsive.spec.ts` يشير إلى selectors غير موجودة (`mobile-menu`, `mobile-drawer`)

---

## 10. التعريب والوصول | i18n & Accessibility

### 10.1 التعريب

| الميزة | Admin | Web |
|--------|:-----:|:---:|
| نظام الترجمة | `lib/i18n` (مخصص) | `next-intl` (مكتبة كاملة) |
| اللغات | AR + EN | AR (افتراضي) + EN |
| RTL Support | ✅ | ✅ (`start`/`end`, `ms-`/`me-`) |
| Locale Detection | ✅ | ✅ Edge-optimized |
| Cookie Persistence | — | ✅ (سنة) |
| مفتاح تبديل اللغة | — | ⚠️ موجود لكن غير مستخدم في التنقل الرئيسي |
| نصوص مشفرة | ⚠️ بعض | ⚠️ Login + ErrorBoundary |

### 10.2 إمكانية الوصول

| الميزة | Admin | Web |
|--------|:-----:|:---:|
| ARIA attributes | ✅ | ✅ (299 حالة) |
| Skip-to-content | — | ✅ ثنائي اللغة |
| Focus lock (Modals) | — | ✅ react-focus-lock |
| Screen reader announcements | — | ✅ Modals + Toasts |
| `aria-current="page"` | — | ✅ |
| alt text coverage | ⚠️ يحتاج تحقق | ⚠️ حالة واحدة |

---

## 11. الوضع الداكن | Dark Mode

| الميزة | Admin | Web |
|--------|:-----:|:---:|
| التطبيق | Class-based (`dark:` Tailwind) | Class-based via ThemeProvider |
| System Preference Detection | ✅ | ✅ |
| localStorage Persistence | ✅ | ✅ |
| ThemeToggle Component | ✅ | ✅ |
| **Modal dark mode** | — | ⚠️ `bg-white` بدون `dark:` variant |
| **Toast dark mode** | — | ⚠️ light backgrounds فقط |

---

## 12. جدول المشاكل الموحّد | Unified Issues Table

### 🔴 حرج (P0) — يجب الإصلاح فوراً

| # | المشكلة | التطبيقات | الملفات | الحالة |
|---|---------|-----------|---------|--------|
| **C-1** | `edgeLogger` يُسكت أخطاء الأمان في الإنتاج (JWT brute-force, CSRF failures غير مرئية) | **Admin + Web** | `middleware.ts:43-48` (Web), `middleware.ts:56-59` (Admin) | **مؤكد** |
| **C-2** | لا يوجد شريط جانبي متجاوب للهواتف (sidebar w-64 ثابت، لا hamburger، لا drawer) | **Web** | `sidebar.tsx`, `header.tsx`, `layout.tsx` | **مؤكد** |
| **C-3** | E2E responsive tests تشير إلى selectors غير موجودة | **Web** | `e2e/responsive.spec.ts` | **مؤكد** |

### 🟠 عالي (P1) — إصلاح خلال أسبوع

| # | المشكلة | التطبيقات | الملفات |
|---|---------|-----------|---------|
| **H-1** | تحديث التبعيات (4 ثغرات متوسطة) | Admin | `package.json` |
| **H-2** | إضافة rate limiting لنقاط المصادقة | Admin | `api/auth/login/route.ts`, `refresh/route.ts` |
| **H-3** | إصلاح CORS في `/api/csp-report` (`*` → أصول محددة) | Admin | `api/csp-report/route.ts` |
| **H-4** | إصلاح ابتلاع الأخطاء الصامت (12 catch فارغ) | Admin | `lib/api.ts` + `irrigation/page.tsx` |
| **H-5** | إضافة `loading.tsx` لمسارات Dashboard | Web | مسارات (dashboard)/ |

### 🟡 متوسط (P2) — إصلاح خلال شهر

| # | المشكلة | التطبيقات | الملفات |
|---|---------|-----------|---------|
| **M-1** | استبدال `as any` (7 حالات) | Admin | `FarmsMap.tsx` |
| **M-2** | إضافة loading states/skeletons | Admin | `users/page.tsx`, `diseases/page.tsx` |
| **M-3** | تفعيل قاعدة `exhaustive-deps` ESLint | Admin | `eslint.config.mjs` |
| **M-4** | إضافة Zod schema validation لمسارات API | Admin | `api/log-error/route.ts` |
| **M-5** | تحسين UX الأخطاء (toast notifications) | Admin | صفحات متعددة |
| **M-6** | توسيع مكتبة UI (Table, Select, Tabs, DatePicker) | Web | — |
| **M-7** | إصلاح dark mode لـ Modal و Toast | Web | `modal.tsx`, `toast.tsx` |
| **M-8** | Mutation hooks مركزية | Web | `hooks.ts` |
| **M-9** | Route prefetching wastes bandwidth | Web | `sidebar.tsx` |
| **M-10** | نصوص مشفرة بدل i18n | كلاهما | Login, ErrorBoundary |
| **M-11** | مفتاح تبديل اللغة غير موجود في التنقل | Web | `sidebar.tsx` |
| **M-12** | CSRF token rotation عند الإجراءات الحساسة | Web | `middleware.ts` |
| **M-13** | Cookie cleanup هش عند logout | Web | `auth.store.tsx` |
| **M-14** | زيادة تغطية الاختبارات (target 70%+) | Admin | متعدد |
| **M-15** | إضافة اختبارات مستوى الميزات + hooks | Web | 37 ميزة |

### 🟢 منخفض (P3) — عند توفر الوقت

| # | المشكلة | التطبيقات | الملفات |
|---|---------|-----------|---------|
| **L-1** | إصلاح ~116 تحذير ESLint (متغيرات غير مستخدمة) | Admin | متعدد |
| **L-2** | استبدال `console.error` بـ `logger.error` | Admin | 4 ملفات |
| **L-3** | Root page renders Cockpit بدون auth check | Web | `HomeClient.tsx` |
| **L-4** | WebSocket بدون connection pooling | Web | `ws/index.ts` |
| **L-5** | API URL fallback إلى سلسلة فارغة | Web | `unified-client.ts` |
| **L-6** | لا يوجد `next/image` wrapper | Web | — |
| **L-7** | Toast بدون حد أقصى (يمكن التراكم لا نهائياً) | Web | `toast.tsx` |
| **L-8** | صفحات Stub بأرقام مشفرة (8 صفحات) | Admin | vision, terrain, etc. |
| **L-9** | أزرار التصدير معطلة في ~10 صفحات | Admin | متعدد |

---

## 13. أفضل الأنماط المتبعة والمعمارية المرجعية | Best Practices & Reference Patterns

### 13.1 أنماط معمارية ممتازة يجب الحفاظ عليها | Excellent Patterns to Preserve

#### أ) نمط Provider Hierarchy (Web)

```tsx
// ✅ نمط ممتاز: QueryClientProvider في dashboard فقط — يوفر ~50KB لصفحات المصادقة
// apps/web/src/app/layout.tsx
<ThemeProvider>
  <AuthProvider>
    <ToastProvider>
      {children}
    </ToastProvider>
  </AuthProvider>
</ThemeProvider>

// apps/web/src/app/(dashboard)/layout.tsx
<QueryClientProvider client={queryClient}>
  <Sidebar />
  <main>{children}</main>
</QueryClientProvider>
```

#### ب) نمط Edge Middleware Optimization (مشترك)

```typescript
// ✅ نمط ممتاز: استخدام jose بدلاً من jsonwebtoken لتوافق Edge Runtime
// يوفر ~500KB+ من حجم middleware bundle
import { jwtVerify } from 'jose';  // ~5KB — Edge-compatible
// ❌ import jwt from 'jsonwebtoken';  // ~200KB — لا يعمل في Edge
```

#### ج) نمط Code Splitting (Web)

```tsx
// ✅ نمط ممتاز: 12 ملف .dynamic.tsx مع SSR: false + loading fallback
// apps/web/src/components/charts/LazyRecharts.dynamic.tsx
import dynamic from 'next/dynamic';
export const LazyLineChart = dynamic(
  () => import('recharts').then(mod => mod.LineChart),
  { ssr: false, loading: () => <ChartSkeleton /> }
);
```

#### د) نمط CSRF Double-Submit (مشترك)

```typescript
// ✅ نمط أمني متقدم: كوكي httpOnly + كوكي قابل للقراءة + timing-safe comparison
// middleware.ts
const csrfCookie = cookies.get('csrf_token');  // httpOnly — لا يمكن قراءته من JS
const csrfHeader = request.headers.get('x-csrf-token');  // من العميل
// مقارنة آمنة ضد التوقيت (timing-safe)
if (!timingSafeEqual(csrfCookie, csrfHeader)) { return 403; }
```

#### هـ) نمط Error Boundary المتدرج (Web)

```tsx
// ✅ نمط ممتاز: كل منطقة لها ErrorBoundary مستقل
<ErrorBoundary fallback={<SidebarFallback />}>
  <Sidebar />
</ErrorBoundary>
<ErrorBoundary fallback={<HeaderFallback />}>
  <Header />
</ErrorBoundary>
<ErrorBoundary fallback={<ContentFallback />}>
  <main>{children}</main>
</ErrorBoundary>
```

#### و) نمط Toast Lazy Icons (Web)

```tsx
// ✅ إبداعي: تحميل أيقونات Toast بـ React.lazy() — يوفر ~5KB من البداية
const SuccessIcon = React.lazy(() => import('lucide-react').then(m => ({ default: m.CheckCircle })));
const ErrorIcon = React.lazy(() => import('lucide-react').then(m => ({ default: m.XCircle })));
```

#### ز) نمط API Chain مع Token Refresh Queue (Admin)

```typescript
// ✅ نمط متقدم: طابور Token Refresh لمنع طلبات متعددة متزامنة
let isRefreshing = false;
let failedQueue: Array<{ resolve: Function; reject: Function }> = [];

apiClient.interceptors.response.use(null, async (error) => {
  if (error.response?.status === 401 && !originalRequest._retry) {
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      });
    }
    isRefreshing = true;
    // ... refresh token, then process queue
  }
});
```

### 13.2 أنماط مضادة يجب تجنبها | Anti-Patterns to Avoid

| النمط المضاد | أين وُجد | النمط الصحيح |
|-------------|----------|-------------|
| `catch (error) { /* silent */ }` | Admin: 12 حالة في `lib/api.ts` | `catch (error) { logger.error('context', error); throw; }` |
| `as any` | Admin: 7 حالات في `FarmsMap.tsx` | استخدام types محددة أو `unknown` مع type guards |
| `edgeLogger` مشروط بـ dev فقط | مشترك: `middleware.ts` | `console.error` بدون شرط أو POST لـ endpoint |
| نصوص مشفرة بدل i18n | مشترك: Login, ErrorBoundary | استخدام `t('key')` من نظام الترجمة |
| `bg-white` بدون `dark:` variant | Web: `modal.tsx`, `toast.tsx` | `bg-white dark:bg-gray-800` دائماً |
| `<Link>` بدون `prefetch={false}` | Web: sidebar (15 رابط) | `<Link prefetch={false}>` لتوفير ~750KB |

---

## 14. حالة الأيقونات ونظام التصميم | Icon System & Design Status

### 14.1 نظام الأيقونات الحالي

| الجانب | Admin | Web |
|--------|-------|-----|
| **المكتبة** | `lucide-react` v0.575.0 | `lucide-react` (مشترك) |
| **عدد الأيقونات المستخدمة** | ~50 أيقونة | ~60 أيقونة |
| **التحميل الكسول** | ❌ استيراد مباشر | ✅ Toast icons فقط |
| **RTL Support** | ✅ (lucide مدعوم) | ✅ `ms-`/`me-` margins |

### 14.2 أيقونات مفقودة أو غير متسقة

| السياق | الحالة | التأثير |
|--------|--------|---------|
| **Sidebar mobile hamburger** | ❌ **مفقود** — لا يوجد `<Menu />` icon في header | لا يوجد زر hamburger menu للهواتف (Web) |
| **Notification badges** | ❌ **مفقود** — لا badge icons في sidebar | لا تنبيهات مرئية للمستخدم (Web) |
| **Export buttons** | ⚠️ موجودة لكن **معطلة** في ~10 صفحات | `<Download />` icon موجود لكن الزر disabled (Admin) |
| **Empty states** | ⚠️ **لا أيقونات حالة فارغة** | لا توجد رسومات/أيقونات عند عدم وجود بيانات |
| **Loading indicators** | ⚠️ **غير موحدة** | spinner مختلف بين الصفحات |
| **Status indicators** | ✅ متسقة | `CheckCircle`, `AlertTriangle`, `XCircle` |
| **Navigation icons** | ✅ 15 أيقونة في sidebar | كل عنصر له أيقونة مناسبة |

### 14.3 توصيات نظام الأيقونات

1. **إنشاء `IconProvider`** — wrapper موحد يدعم RTL/LTR تلقائياً وأحجام متناسقة
2. **تحميل كسول شامل** — استخدام `React.lazy` لجميع أيقونات lucide (مثل نمط Toast)
3. **أيقونات حالة فارغة** — إنشاء 4 رسومات SVG مخصصة: no-data, no-results, error, offline
4. **Spinner موحد** — مكون `<Spinner size="sm|md|lg" />` مع `aria-busy`

### 14.4 مكونات نظام التصميم المفقودة

| المكون | الأولوية | مثال الاستخدام | الحالة |
|--------|:--------:|---------------|--------|
| **`<Icon>`** wrapper | عالية | `<Icon name="home" size={20} />` | ❌ مفقود |
| **`<EmptyState>`** | عالية | حقول فارغة، نتائج بحث صفرية | ❌ مفقود |
| **`<StatusBadge>`** | متوسطة | Active/Inactive/Pending | ❌ مفقود |
| **`<LoadingOverlay>`** | متوسطة | تحميل الصفحة الكاملة | ❌ مفقود |
| **`<ConfirmDialog>`** | عالية | تأكيد الحذف/الإجراءات | ❌ مفقود |
| **`<FormField>`** | عالية | label + input + error + help text | ❌ مفقود |
| **`<Card>`** | عالية | بطاقات المعلومات | ⚠️ inline في كل صفحة |
| **`<Badge>`** | متوسطة | عدد التنبيهات، الحالة | ❌ مفقود |

---

## 15. الهياكل والأكواد الناقصة مع أمثلة | Missing Structures & Code Examples

### 15.1 ملفات ناقصة حرجة | Critical Missing Files

#### أ) `loading.tsx` لمسارات Dashboard (Web)

**الملفات المطلوبة:** `loading.tsx` في كل مسار dashboard (37 مسار)

```tsx
// apps/web/src/app/(dashboard)/analytics/loading.tsx
// apps/web/src/app/(dashboard)/weather/loading.tsx
// apps/web/src/app/(dashboard)/tasks/loading.tsx
// ... (حالياً فقط fields/ يملك loading.tsx)

export default function Loading() {
  return (
    <div className="animate-pulse space-y-4 p-6">
      <div className="h-8 w-48 bg-gray-200 dark:bg-gray-700 rounded" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-32 bg-gray-200 dark:bg-gray-700 rounded-lg" />
        ))}
      </div>
      <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded-lg" />
    </div>
  );
}
```

#### ب) Responsive Sidebar + Mobile Drawer (Web)

**الملفات المتأثرة:**
- `src/components/layouts/sidebar.tsx` — يحتاج responsive classes
- `src/components/layouts/header.tsx` — يحتاج hamburger button
- `src/app/(dashboard)/layout.tsx` — يحتاج state management

```tsx
// src/components/layouts/sidebar.tsx — التعديل المطلوب
interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}
      <aside
        className={cn(
          "fixed inset-y-0 start-0 z-50 w-64 bg-white dark:bg-gray-900 border-e",
          "transform transition-transform duration-300 ease-in-out",
          "md:relative md:translate-x-0",  // ✅ مرئي دائماً على Desktop
          isOpen ? "translate-x-0" : "-translate-x-full"  // ✅ drawer على Mobile
        )}
        data-testid="sidebar"
      >
        {/* ... navigation items ... */}
      </aside>
    </>
  );
}

// src/components/layouts/header.tsx — إضافة hamburger
import { Menu } from 'lucide-react';

export function Header({ onMenuToggle }: { onMenuToggle: () => void }) {
  return (
    <header className="...">
      <button
        className="md:hidden p-2"
        onClick={onMenuToggle}
        aria-label="Toggle menu"
        data-testid="mobile-menu"
      >
        <Menu className="h-6 w-6" />
      </button>
      {/* ... rest of header ... */}
    </header>
  );
}
```

#### ج) Edge-compatible Production Logger (مشترك)

```typescript
// src/lib/edge-logger.ts — ملف جديد مطلوب
const isProduction = process.env.NODE_ENV === 'production';

export const edgeLogger = {
  error: (...args: unknown[]) => {
    // ✅ دائماً يسجّل — لا يُسكت في الإنتاج!
    console.error('[SAHOOL]', ...args);
  },
  warn: (...args: unknown[]) => {
    console.warn('[SAHOOL]', ...args);
  },
  info: (...args: unknown[]) => {
    if (!isProduction) {
      console.info('[SAHOOL]', ...args);
    }
  },
  security: (event: string, details: Record<string, unknown>) => {
    // ✅ أحداث الأمان تُسجّل دائماً
    console.error('[SAHOOL:SECURITY]', event, JSON.stringify(details));
    // اختياري: POST إلى /api/security-log للتسجيل المركزي
  },
};
```

#### د) مكونات UI مفقودة حرجة

```tsx
// src/components/ui/table.tsx — مكون DataTable قابل لإعادة الاستخدام
interface Column<T> {
  key: keyof T;
  header: string;
  headerAr?: string;
  render?: (value: T[keyof T], row: T) => React.ReactNode;
  sortable?: boolean;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  emptyMessage?: string;
  emptyMessageAr?: string;
  onRowClick?: (row: T) => void;
  pagination?: { page: number; pageSize: number; total: number };
  onPageChange?: (page: number) => void;
}

export function DataTable<T>({ columns, data, loading, ... }: DataTableProps<T>) {
  // ... implementation with dark mode, RTL, a11y
}
```

```tsx
// src/components/ui/empty-state.tsx — حالة فارغة موحدة
interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  titleAr?: string;
  description?: string;
  descriptionAr?: string;
  action?: { label: string; labelAr?: string; onClick: () => void };
}

export function EmptyState({ icon, title, titleAr, description, ... }: EmptyStateProps) {
  const { locale } = useLocale();
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center" role="status">
      {icon && <div className="mb-4 text-gray-400">{icon}</div>}
      <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
        {locale === 'ar' ? (titleAr || title) : title}
      </h3>
      {/* ... */}
    </div>
  );
}
```

### 15.2 هياكل Stub تحتاج تحويل لتكامل حقيقي | Stub Pages Needing Real Integration

| الصفحة Stub | الخدمة الخلفية | المنفذ | API المطلوب |
|-------------|---------------|--------|------------|
| `/vision` | `yolo26-vision-service` | 8150 | `POST /api/v1/detect/pest`, `POST /api/v1/detect/disease` |
| `/terrain` | `terrain-core-service` | 8185 | `GET /api/v1/terrain/dem`, `GET /api/v1/terrain/slope` |
| `/edge-devices` | `edge-orchestrator-service` | 8180 | `GET /api/v1/edge/devices`, `POST /api/v1/edge/deploy` |
| `/audit` | `audit-service` | 8114 | `GET /api/v1/audit/logs`, `GET /api/v1/audit/stats` |
| `/scouting` | — | — | يحتاج endpoint جديد |
| `/drone` | `drone-service` | 8126 | `GET /api/v1/drones`, `POST /api/v1/flight-plan` |
| `/virtual-sensors` | `virtual-sensors` | 8119 | `GET /api/v1/sensors/virtual` |

### 15.3 ملفات i18n ناقصة | Missing i18n Entries

```json
// نصوص مشفرة يجب نقلها إلى ملفات الترجمة:

// apps/web — Login page
"تسجيل الدخول إلى سهول"  →  t('auth.login.title')

// apps/web — ErrorBoundary
"حدث خطأ غير متوقع"  →  t('errors.unexpected')

// apps/admin — Stub pages (8 صفحات)
"سيتم عرض ... هنا"  →  t('common.comingSoon', { feature: t('features.vision') })

// apps/admin — Export buttons (~10 صفحات)
"قريبًا"  →  t('common.comingSoonShort')
```

---

## 16. الاختبارات المطلوبة تفصيلياً | Required Tests — Detailed

### 16.1 اختبارات حرجة مفقودة (P0) | Critical Missing Tests

#### أ) اختبارات الأمان — Edge Logger (Admin + Web)

```typescript
// __tests__/middleware-security-logging.test.ts
describe('Security Event Logging', () => {
  it('logs CSRF failures in production', async () => {
    process.env.NODE_ENV = 'production';
    const consoleSpy = vi.spyOn(console, 'error');
    await middleware(requestWithInvalidCSRF);
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('CSRF'),
      expect.any(Object)
    );
  });

  it('logs JWT brute-force attempts in production', async () => {
    process.env.NODE_ENV = 'production';
    const consoleSpy = vi.spyOn(console, 'error');
    await middleware(requestWithInvalidJWT);
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('JWT'),
      expect.any(Object)
    );
  });

  it('logs rate limiting events in production', async () => {
    // 6th attempt should be logged
  });
});
```

#### ب) اختبارات Responsive Sidebar (Web)

```typescript
// e2e/responsive-sidebar.spec.ts — يجب أن يحل محل responsive.spec.ts المعطل
import { test, expect } from '@playwright/test';

test.describe('Mobile Sidebar', () => {
  test.use({ viewport: { width: 375, height: 667 } }); // iPhone SE

  test('sidebar is hidden by default on mobile', async ({ page }) => {
    await page.goto('/dashboard');
    const sidebar = page.getByTestId('sidebar');
    await expect(sidebar).not.toBeVisible();
  });

  test('hamburger menu opens sidebar drawer', async ({ page }) => {
    await page.goto('/dashboard');
    await page.getByTestId('mobile-menu').click();
    const sidebar = page.getByTestId('sidebar');
    await expect(sidebar).toBeVisible();
  });

  test('clicking overlay closes sidebar', async ({ page }) => {
    await page.goto('/dashboard');
    await page.getByTestId('mobile-menu').click();
    await page.getByTestId('sidebar-overlay').click();
    await expect(page.getByTestId('sidebar')).not.toBeVisible();
  });

  test('sidebar is always visible on desktop', async ({ page }) => {
    test.use({ viewport: { width: 1280, height: 720 } });
    await page.goto('/dashboard');
    await expect(page.getByTestId('sidebar')).toBeVisible();
  });
});
```

### 16.2 اختبارات عالية الأولوية (P1) | High Priority Tests

#### أ) اختبارات Hooks (Web — 37 ميزة بدون اختبار)

```typescript
// src/features/fields/__tests__/useCreateField.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { useCreateField } from '../hooks/useCreateField';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

describe('useCreateField', () => {
  it('creates field and invalidates cache', async () => {
    const { result } = renderHook(() => useCreateField(), { wrapper });
    result.current.mutate({ name: 'Field 1', area: 5.0, coordinates: [...] });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    // verify cache invalidation
  });

  it('handles validation errors', async () => {
    const { result } = renderHook(() => useCreateField(), { wrapper });
    result.current.mutate({ name: '', area: -1 });
    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error).toContain('validation');
  });
});
```

#### ب) اختبارات Dark Mode (Web)

```typescript
// src/components/ui/__tests__/modal-dark-mode.test.tsx
describe('Modal Dark Mode', () => {
  it('applies dark background when dark mode is active', () => {
    document.documentElement.classList.add('dark');
    render(<Modal open onClose={() => {}}><p>Content</p></Modal>);
    const overlay = screen.getByRole('dialog');
    expect(overlay).toHaveClass('dark:bg-gray-800');
  });

  it('applies dark border when dark mode is active', () => {
    document.documentElement.classList.add('dark');
    render(<Modal open onClose={() => {}}><p>Content</p></Modal>);
    expect(screen.getByRole('dialog')).toHaveClass('dark:border-gray-700');
  });
});
```

#### ج) اختبارات CSRF Token Rotation (Web)

```typescript
// __tests__/csrf-rotation.test.ts
describe('CSRF Token Rotation', () => {
  it('rotates CSRF token after login', async () => {
    const tokenBefore = getCookie('csrf_token');
    await login(validCredentials);
    const tokenAfter = getCookie('csrf_token');
    expect(tokenAfter).not.toBe(tokenBefore);
  });

  it('rotates CSRF token after password change', async () => {
    // ...
  });
});
```

### 16.3 اختبارات متوسطة الأولوية (P2) | Medium Priority Tests

| الفئة | عدد الاختبارات | الملفات المستهدفة |
|-------|:--------------:|-----------------|
| **Feature unit tests** | ~37 ملف | `src/features/*/` — كل ميزة تحتاج اختبار واحد على الأقل |
| **React Query hooks** | ~10 ملفات | `useFields`, `useWeather`, `useTasks`, `useAlerts`, etc. |
| **API integration** | ~5 ملفات | اختبار تدفق API → Cache → UI |
| **Dark mode** | ~4 ملفات | Modal, Toast, Sidebar, Dashboard cards |
| **i18n** | ~3 ملفات | تبديل اللغة، RTL rendering، placeholder text |

### 16.4 هدف التغطية | Coverage Targets

| المقياس | الحالي (Admin) | الحالي (Web) | الهدف |
|---------|:-------------:|:------------:|:-----:|
| **ملفات الاختبار** | 52 | 74 | 150+ |
| **Lines** | ~40% (تقديري) | ~30% (تقديري) | 70% |
| **Branches** | — | — | 60% |
| **Functions** | — | — | 75% |
| **Security paths** | ✅ جيد | ✅ جيد | 90%+ |

---

## 17. مقترحات التحسين المفصلة | Detailed Improvement Proposals

### 17.1 🔒 تحسينات أمنية | Security Improvements

| # | المقترح | التأثير | الجهد | التفاصيل |
|---|---------|---------|-------|----------|
| **SEC-1** | تمكين تسجيل الأمان في الإنتاج | حرج | 2 ساعة | استبدال `edgeLogger` بـ `console.error` بدون شرط + POST اختياري لـ `/api/security-log` |
| **SEC-2** | Rate limiting بـ Redis | عالي | 4 ساعات | استبدال `Map()` بـ `@upstash/ratelimit` أو Redis Sentinel الموجود |
| **SEC-3** | CSRF token rotation | متوسط | 3 ساعات | تدوير عند login/password-change/role-change |
| **SEC-4** | تقييد CORS لنقطة CSP | عالي | 30 دقيقة | `'*'` → `process.env.ALLOWED_ORIGINS` |
| **SEC-5** | WebAuthn/FIDO2 | منخفض | 20 ساعة | مصادقة بيومترية كبديل لـ 2FA |
| **SEC-6** | Subresource Integrity (SRI) | منخفض | 2 ساعة | إضافة `integrity` hashes لـ CDN scripts |

### 17.2 🏗️ تحسينات معمارية | Architecture Improvements

| # | المقترح | التأثير | الجهد | التفاصيل |
|---|---------|---------|-------|----------|
| **ARCH-1** | Responsive sidebar (drawer) | حرج | 8 ساعات | إعادة هيكلة sidebar/header/layout مع state management |
| **ARCH-2** | Mutation hooks مركزية | عالي | 6 ساعات | إنشاء `useMutation` hooks في `lib/api/hooks.ts` لكل عملية كتابة |
| **ARCH-3** | WebSocket connection pooling | متوسط | 8 ساعات | singleton connection مع multiplexing بدل connection-per-subscription |
| **ARCH-4** | Design System مشترك | عالي | 40 ساعة | توحيد مكونات UI بين Admin و Web عبر `@sahool/design-system` |
| **ARCH-5** | Monorepo build caching | متوسط | 4 ساعات | إضافة Turborepo caching للبناء المشترك |

### 17.3 🎨 تحسينات واجهة المستخدم | UI Improvements

| # | المقترح | التأثير | الجهد | التفاصيل |
|---|---------|---------|-------|----------|
| **UI-1** | مكتبة UI موسعة (12 مكون) | عالي | 30 ساعة | Table, Select, Tabs, DatePicker, Breadcrumb, Avatar, Pagination, Skeleton, Alert, Progress, Tooltip, EmptyState |
| **UI-2** | Dark mode شامل | متوسط | 4 ساعات | إصلاح Modal + Toast + أي مكون بـ `bg-white` بدون `dark:` |
| **UI-3** | أيقونات حالة فارغة | متوسط | 6 ساعات | 4 رسومات SVG: no-data, no-results, error, offline |
| **UI-4** | Spinner موحد | منخفض | 1 ساعة | مكون `<Spinner />` واحد بأحجام ثابتة |
| **UI-5** | `loading.tsx` لجميع المسارات | عالي | 4 ساعات | 36 ملف skeleton loader |
| **UI-6** | `next/image` wrapper | متوسط | 2 ساعة | wrapper موحد لصور المزرعة مع WebP/AVIF + blur placeholder |

### 17.4 📊 تحسينات الأداء | Performance Improvements

| # | المقترح | التأثير | الجهد | التفاصيل |
|---|---------|---------|-------|----------|
| **PERF-1** | `prefetch={false}` لروابط sidebar | متوسط | 30 دقيقة | توفير ~750KB bandwidth |
| **PERF-2** | Lazy loading لجميع أيقونات lucide | منخفض | 2 ساعة | `React.lazy` بدل static import |
| **PERF-3** | Bundle analyzer تقرير شهري | منخفض | 1 ساعة | `@next/bundle-analyzer` في CI |
| **PERF-4** | Web Vitals monitoring | متوسط | 3 ساعات | `next/web-vitals` + Grafana dashboard |

### 17.5 📝 تحسينات جودة الكود | Code Quality Improvements

| # | المقترح | التأثير | الجهد | التفاصيل |
|---|---------|---------|-------|----------|
| **CQ-1** | إصلاح 116 تحذير ESLint | متوسط | 3 ساعات | `pnpm lint --fix` + مراجعة يدوية |
| **CQ-2** | إزالة `as any` (7 حالات) | منخفض | 1 ساعة | استبدال بـ proper types |
| **CQ-3** | `exhaustive-deps` ESLint rule | متوسط | 2 ساعة | تفعيل وإصلاح warnings |
| **CQ-4** | Zod validation لمسارات API | عالي | 4 ساعات | schema validation لكل route handler |
| **CQ-5** | Error boundaries لجميع الصفحات | متوسط | 3 ساعات | wrap كل صفحة dashboard بـ ErrorBoundary |

### 17.6 🌐 تحسينات التعريب | i18n Improvements

| # | المقترح | التأثير | الجهد | التفاصيل |
|---|---------|---------|-------|----------|
| **I18N-1** | نقل النصوص المشفرة | متوسط | 3 ساعات | Login, ErrorBoundary, Stub pages (~30 نص) |
| **I18N-2** | مفتاح تبديل اللغة في sidebar | عالي | 1 ساعة | `<LocaleSwitcher />` موجود لكن غير مُدرج |
| **I18N-3** | i18n extraction CI check | منخفض | 2 ساعة | فحص CI يكشف نصوص مشفرة جديدة |
| **I18N-4** | RTL E2E tests | منخفض | 2 ساعة | اختبارات Playwright بـ `dir="rtl"` |

### 17.7 🔄 تحويل الصفحات MOCK/STUB | Page Conversion Roadmap

#### أولوية التحويل (حسب القيمة التجارية):

| الأولوية | الصفحة | الأسطر | الخدمة الخلفية | الجهد المقدّر |
|:--------:|--------|:------:|---------------|:------------:|
| 1 | `/insurance` | 1,053 | `crop-insurance` module | 12 ساعة |
| 2 | `/market-prices` | 821 | `market-prices` module | 8 ساعات |
| 3 | `/irrigation` | 816 | `irrigation-smart:8094` | 8 ساعات |
| 4 | `/seeds` | 1,066 | يحتاج endpoint جديد | 10 ساعات |
| 5 | `/seasons` | 1,125 | `agri-calendar` module | 10 ساعات |
| 6 | `/inventory` | 661 | `inventory-service:8116` | 6 ساعات |
| 7 | `/crop-health` | 339 | `crop-intelligence-service:8095` | 4 ساعات |
| 8 | `/vision` (stub) | 78 | `yolo26-vision-service:8150` | 16 ساعة |
| 9 | `/terrain` (stub) | 78 | `terrain-core-service:8185` | 12 ساعة |
| 10 | `/edge-devices` (stub) | 78 | `edge-orchestrator-service:8180` | 12 ساعة |

**المجموع التقديري:** ~98 ساعة لتحويل أعلى 10 صفحات

### 17.8 📊 مقاييس النجاح | Success Metrics

| المقياس | الحالي | الهدف (3 أشهر) | الهدف (6 أشهر) |
|---------|:------:|:-------------:|:-------------:|
| صفحات FULL API | 16 (27%) | 26 (43%) | 40 (67%) |
| مكونات UI مشتركة | 12 | 24 | 30 |
| تغطية الاختبارات | ~35% | 50% | 70% |
| ملفات الاختبار | 126 | 180 | 250 |
| تحذيرات ESLint | 116 | 30 | 0 |
| ثغرات npm | 4 moderate | 0 moderate | 0 |
| صفحات Stub | 8 | 4 | 0 |
| Dark mode coverage | ~70% | 90% | 100% |
| Lighthouse Performance | — | >80 | >90 |
| Lighthouse Accessibility | — | >85 | >95 |

---

## 18. خطة العمل | Action Plan

### المرحلة 1: فوري (أسبوع واحد) — الأمان والحرج (انظر SEC-1..6, ARCH-1, UI-5)

1. **إصلاح C-1:** تمكين `edgeLogger` في الإنتاج — استخدام `console.error` بدون شرط أو POST إلى `/api/security-log`
2. **إصلاح C-2:** إضافة sidebar متجاوب مع drawer pattern (hidden on mobile, visible on md+)
3. **إصلاح C-3:** تحديث E2E responsive tests لمطابقة selectors الفعلية
4. **إصلاح H-1:** تحديث التبعيات (lodash, next)
5. **إصلاح H-2:** إضافة rate limiting (Redis-backed للإنتاج)
6. **إصلاح H-3:** تقييد CORS على أصول محددة
7. **إصلاح H-4:** إضافة error logging لـ 12 catch فارغ
8. **إصلاح H-5:** إضافة `loading.tsx` لجميع مسارات dashboard

**الجهد المقدّر:** ~20 ساعة

### المرحلة 2: قصير المدى (شهر واحد) — الجودة والميزات (انظر UI-1..6, CQ-1..5, I18N-1..2)

9. توسيع مكتبة UI (Table, Select, Tabs, DatePicker, Pagination)
10. إصلاح dark mode لـ Modal و Toast
11. Mutation hooks مركزية
12. زيادة تغطية الاختبارات (target 150+ ملف)
13. إضافة `prefetch={false}` لروابط sidebar
14. نقل النصوص المشفرة إلى نظام الترجمة
15. إضافة مفتاح تبديل اللغة في sidebar

**الجهد المقدّر:** ~40 ساعة

### المرحلة 3: طويل المدى — التحسين المستمر (انظر القسم 17.7 — تحويل الصفحات)

16. إضافة WebAuthn/FIDO2 للمصادقة البيومترية
17. إنشاء design system مشترك بين web و mobile
18. تحويل صفحات MOCK إلى تكامل API حقيقي
19. تحويل صفحات STUB إلى واجهات كاملة
20. إضافة performance benchmarks (Web Vitals)

---

## 19. نتائج التحقق العميق | Deep Verification Results

تم التحقق العميق من 3 مشاكل حرجة مع فحص الملفات المتأثرة:

### ✅ مؤكد: Sidebar غير متجاوب (Web)

| الملف | النتيجة |
|-------|---------|
| `sidebar.tsx` | `w-64` ثابت، لا responsive breakpoints |
| `header.tsx` | لا hamburger menu |
| `layout.tsx` | `<Sidebar />` يظهر دائماً في flex |
| `responsive.spec.ts` | `[data-testid="mobile-menu"]` و `[data-testid="mobile-drawer"]` **غير موجودين** |

### ✅ مؤكد: edgeLogger يُسكت الأخطاء (Admin + Web)

| الملف | النتيجة |
|-------|---------|
| `middleware.ts` | `edgeLogger.error()` مغلف بـ `NODE_ENV === "development"` |
| الأسطر المتأثرة | CSRF failure (193), JWT exception (230), JWT validation failure (239) |
| `lib/logger.ts` | `logger.error/warn/info` جميعها dev-only. `logger.critical` يستخدم Sentry (~300KB — ثقيل جداً لـ Edge) |
| **التأثير** | هجمات JWT و فشل CSRF **غير مرئية تماماً** في الإنتاج |

### ❌ مدحوض: عدم وجود Dynamic Imports (Web)

- **النتيجة:** 12 ملف `.dynamic.tsx` مكتشف — تقسيم الكود **ممتاز**
- تم تصحيح تقييم الأداء من 7/10 إلى **8/10**

---

## 20. النقاط الإيجابية | Positive Highlights

### مشترك بين التطبيقين

1. ✅ **أمان على مستوى الإنتاج** — CSP, CSRF, JWT, HSTS, nonce
2. ✅ **TypeScript strict mode** بدون أخطاء
3. ✅ **Error Boundaries شاملة** — logging, retry, bilingual
4. ✅ **Edge middleware optimization** — تجنب imports ثقيلة (~500KB+)
5. ✅ **Standalone Docker output** — images محسّنة
6. ✅ **Tailwind shared config** عبر `@sahool/tailwind-config`
7. ✅ **Input validation شاملة** — email, phone, password, URL, safe text

### خاص بـ Admin

8. ✅ **1,044 حالة اختبار** بدون اختبارات وهمية أو متخطاة
9. ✅ **Rate limiting مُطبق** (5 محاولات/15 دقيقة)
10. ✅ **2FA مع backup codes** و QR code
11. ✅ **Multi-channel OTP** (email, SMS, WhatsApp, Telegram)
12. ✅ **Google Maps links** مع `encodeURIComponent` والتحقق من الإحداثيات

### خاص بـ Web

13. ✅ **تقسيم الكود ممتاز** — 12 dynamic wrapper (~625KB+ توفير)
14. ✅ **Auth store متقدم** — cross-tab logout, session expiry, UUID validation
15. ✅ **Button component مثالي** — variants, sizes, loading, icons, RTL, ARIA
16. ✅ **Modal accessibility ممتازة** — focus lock, restore, screen reader
17. ✅ **Toast lazy-loading** — إبداعي وفعال
18. ✅ **QueryClient scoping** — في dashboard فقط (توفير bundle لصفحات auth)
19. ✅ **Progressive dashboard loading** — Suspense + custom skeletons
20. ✅ **E2E شامل** — multi-browser, mobile viewport, CI-adapted

---

## ملحق: مصفوفة الجاهزية للإنتاج | Production Readiness Matrix

| البند | Admin | Web |
|-------|:-----:|:---:|
| HTTPS enforcement (CSP upgrade-insecure-requests) | ✅ | ✅ |
| HSTS headers (31536000s) | ✅ | ✅ |
| X-Frame-Options: DENY | ✅ | ✅ |
| Content Security Policy (nonce-based) | ✅ | ✅ |
| Environment variables template | ✅ | ✅ |
| Error logging (Sentry) | ✅ | ✅ |
| Session management (30min + refresh) | ✅ | ✅ |
| Input validation & sanitization | ✅ | ✅ |
| Secrets management | ✅ | ✅ |
| CORS restriction | ⚠️ CSP endpoint permissive | ✅ |
| Rate limiting on auth | ⚠️ in-memory only | ⚠️ needs verification |
| Dependency vulnerabilities | ⚠️ 4 moderate | ✅ |
| Mobile responsive | ✅ | ⚠️ **Sidebar مفقود** |
| Production error logging | ⚠️ **edgeLogger silent** | ⚠️ **edgeLogger silent** |
| E2E tests passing | ✅ (CI fixed) | ⚠️ responsive tests broken |

---

> **المراجعة القادمة:** بعد تطبيق إصلاحات المرحلة 1  
> **آخر تحديث:** 2026-04-07 · الإصدار 16.0.0
