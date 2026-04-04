# خطة التوصيات والتحسينات المستقبلية
# SAHOOL Platform — Post-Session Technical TODO
> **تاريخ الجلسة**: 2026-04-04
> **PRs ذات الصلة**: #1463 (مدمج), #1464, #1465
> **الأولوية**: مرتبة من الأعلى للأدنى

---

## المرحلة 1: اختبارات (أسبوع 1) — أولوية حرجة 🔴

### 1.1 اختبارات API Proxy Routes الجديدة (Web)

> **السبب**: 10 مسارات proxy جديدة بدون اختبارات — Copilot نبّه على ذلك
> **المرجع**: تعليقات Copilot على PR #1463 (satellite-route.test.ts, weather-route.test.ts)

- [ ] `apps/web/src/app/api/satellite/__tests__/route.test.ts` — 8 actions + fieldId validation + error cases (~15 اختبار)
- [ ] `apps/web/src/app/api/weather/__tests__/route.test.ts` — GET+POST + auth + locationId validation (~12 اختبار)
- [ ] `apps/web/src/app/api/alerts/__tests__/route.test.ts` — CRUD + acknowledge/resolve/dismiss (~10 اختبارات)
- [ ] `apps/web/src/app/api/irrigation/__tests__/route.test.ts` — calculate + methods (~8 اختبارات)
- [ ] `apps/web/src/app/api/advisory/__tests__/route.test.ts` — disease-assess + fertilizer-plan (~8 اختبارات)
- [ ] `apps/web/src/app/api/tasks/__tests__/route.test.ts` — CRUD + assign/complete (~10 اختبارات)
- [ ] `apps/web/src/app/api/equipment/__tests__/route.test.ts` — tracking + maintenance (~8 اختبارات)
- [ ] `apps/web/src/app/api/soil-analysis/__tests__/route.test.ts` — interpret + amendment (~8 اختبارات)
- [ ] `apps/web/src/app/api/pest-detection/__tests__/route.test.ts` — identify + treatment (~8 اختبارات)
- [ ] `apps/web/src/app/api/terrain/__tests__/route.test.ts` — DEM + slope + aspect (~8 اختبارات)

**الإجمالي المتوقع: ~95 اختبار**

### 1.2 اختبارات Admin المفقودة (من تعليقات Copilot)

- [ ] `apps/admin/src/app/api/__tests__/satellite-route.test.ts` — إضافة اختبارات sar-timeseries, cloud-cover, clear-observations
- [ ] `apps/admin/src/app/api/__tests__/weather-route.test.ts` — إضافة اختبارات GET handler (providers, locations, current, forecast)
- [ ] `apps/admin/src/app/farms/__tests__/field-detail.test.tsx` — اختبار boundary parsing مع GeoJSON
- [ ] `apps/admin/src/hooks/api/__tests__/use-alerts.test.ts` — اختبار acknowledge عبر alertService

### 1.3 اختبارات المكونات الجديدة (Web)

- [ ] `CommandPalette.test.tsx` — Ctrl+K, search, navigation, Arabic/English
- [ ] `DrawableMap.test.tsx` — polygon drawing, undo, GeoJSON export
- [ ] `MapLayersPanel.test.tsx` — toggle layers, opacity
- [ ] `SplitScreenNDVI.test.tsx` — date selection, comparison
- [ ] `NDVIWeatherChart.test.tsx` — dual axis render
- [ ] `CrossFarmDashboard.test.tsx` — sort, search, data display
- [ ] `RealTimeActivityFeed.test.tsx` — event display, auto-scroll
- [ ] `ExpertView.test.tsx` — field status rendering
- [ ] `CropCatalog.test.tsx` — 12 crops, search filter
- [ ] `ScoutingNotes.test.tsx` — GPS display, category filter
- [ ] `FieldCreateDialog.test.tsx` — form validation, boundary submission

**الإجمالي المتوقع: ~44 اختبار**

### 1.4 اختبارات E2E (Playwright)

- [ ] سيناريو: إنشاء حقل → رسم حدود → عرض NDVI
- [ ] سيناريو: تسجيل دخول → لوحة تحكم → Ctrl+K بحث → تنقل
- [ ] سيناريو: كشف ميداني → إضافة ملاحظة → تقرير
- [ ] سيناريو: تخطيط موسم → 7 خطوات → توصيات AI
- [ ] سيناريو: مقارنة حقلين → NDVI + طقس + إنتاجية

---

## المرحلة 2: TypeScript وجودة الكود (أسبوع 1-2) — أولوية عالية 🟠

### 2.1 إزالة @ts-nocheck

> **السبب**: يخفي أخطاء حقيقية — Copilot نبّه على ذلك مرتين

- [ ] `apps/web/src/...` — 3 ملفات (تحديد الملفات وإصلاح أخطاء TS الفعلية)
- [ ] `apps/admin/src/app/crop-planning/page.tsx` — إصلاح TS errors
- [ ] `apps/admin/src/app/field-prep/page.tsx` — إصلاح TS errors
- [ ] `apps/admin/src/app/field-zones/page.tsx` — إصلاح TS errors
- [ ] `apps/admin/src/app/reports/page.tsx` — إصلاح TS errors

### 2.2 إزالة console.log/console.error من production code

- [ ] مسح شامل واستبدال بـ `logger.error()` أو `logger.warn()`
- [ ] التأكد من أن `next.config.js` يزيل console.log في production

### 2.3 تحسين أنواع TypeScript

- [ ] استخدام `@sahool/shared-types/contracts` بشكل أوسع في Web
- [ ] إضافة أنواع للمكونات الجديدة (Props interfaces)
- [ ] تفعيل `noUncheckedIndexedAccess` إذا لم يكن مفعّلاً

---

## المرحلة 3: أمان وبنية تحتية (أسبوع 2) — أولوية عالية 🟠

### 3.1 Sentinel Hub كتبعية اختيارية

> **السبب**: Copilot نبّه أن sentinelhub في requirements.txt يجعلها إلزامية
> **المرجع**: تعليق Copilot على PR #1463

- [ ] نقل `sentinelhub` من `requirements.txt` إلى `requirements-eo.txt`
- [ ] إضافة `EO_MODE` build arg في Dockerfile
- [ ] تحديث `pip install` في Dockerfile ليكون مشروطاً
- [ ] تحديث التعليق في requirements.txt

### 3.2 تحسين E2E Mock Servers

> **السبب**: تعليقات Copilot حول fixed ports وglobal state

- [ ] تحويل mock servers لاستخدام dynamic port allocation (port 0)
- [ ] إضافة `conftest.py` بدلاً من `sys.path` manipulation
- [ ] إضافة fixture لتنظيف global in-memory stores بين الاختبارات
- [ ] استبدال relative imports بـ absolute imports

### 3.3 Docker و CI

- [ ] إصلاح Docker BuildX cache (Azure blob 404) — retry strategy
- [ ] إضافة `VEGETATION_SERVICE_URL` و `WEATHER_SERVICE_URL` لـ Web Dockerfile
- [ ] التحقق من أن Web healthcheck يعمل مع الخدمات الجديدة

---

## المرحلة 4: تحسين الواجهات الحالية (أسبوع 2-3) — أولوية متوسطة 🟡

### 4.1 Dashboard تحسينات

- [ ] ربط `RealTimeActivityFeed` بـ WebSocket الحقيقي (بدلاً من mock timer)
- [ ] إضافة `ExpertView` للحقل المحدد في Dashboard
- [ ] إضافة Quick Actions: إنشاء حقل، كشف ميداني، تقرير جديد
- [ ] تحسين MapView بطبقات NDVI + weather overlay

### 4.2 Weather تحسينات

- [ ] توقعات 14 يوم بدلاً من 7
- [ ] تقرير زراعي: ET0, GDD, نافذة الرش
- [ ] مقارنة مزودين: OpenWeather vs Open-Meteo
- [ ] تنبيهات طقس مع ربط alert-service

### 4.3 Irrigation تحسينات

- [ ] حاسبة ري ذكية: كمية + توقيت + طريقة
- [ ] جدول ري أسبوعي (تقويم مرئي)
- [ ] إحصائيات توفير المياه
- [ ] تنبيهات ري عبر WebSocket

### 4.4 Alerts تحسينات

- [ ] ربط WebSocket لتحديث فوري
- [ ] صوت تنبيه للتنبيهات الحرجة
- [ ] تجميع التنبيهات حسب الحقل/النوع
- [ ] تصدير تقرير التنبيهات (PDF/CSV)

---

## المرحلة 5: WebSocket Events الجديدة (أسبوع 3) — أولوية متوسطة 🟡

> **السبب**: المكونات الجديدة تحتاج أحداث WebSocket للتحديث المباشر

- [ ] إضافة `sahool.vision.pest_detected` → تنبيه فوري في Vision page
- [ ] إضافة `sahool.vision.disease_detected` → تنبيه فوري + صورة
- [ ] إضافة `sahool.terrain.analysis_completed` → تحديث Terrain page
- [ ] إضافة `sahool.hydrology.flow_calculated` → تحديث خريطة المياه
- [ ] إضافة `sahool.edge.device_online` → تحديث Edge Devices
- [ ] إضافة `sahool.drone.mission_completed` → تحديث Drone page
- [ ] إضافة `sahool.market.price_updated` → تحديث Market Prices
- [ ] إضافة `sahool.irrigation.schedule_updated` → تحديث Irrigation
- [ ] تحديث `useWebSocketQueryInvalidation` بالأحداث الجديدة

---

## المرحلة 6: أداء (أسبوع 3-4) — أولوية متوسطة 🟡

### 6.1 Bundle Optimization

- [ ] تشغيل `ANALYZE=true next build` وتحليل الحزمة
- [ ] التأكد من تحميل ديناميكي للخرائط والرسوم البيانية
- [ ] Code splitting للمكونات الثقيلة (DrawableMap, CropCatalog)
- [ ] Prefetching للصفحات المتوقعة (sidebar hover)

### 6.2 React Query Optimization

- [ ] ضبط `staleTime` لكل نوع بيانات:
  - Weather: 5 دقائق
  - NDVI: 30 دقيقة
  - Fields: 10 دقائق
  - Alerts: 1 دقيقة (مع WebSocket invalidation)
- [ ] تفعيل `placeholderData` للانتقال السلس بين الصفحات

### 6.3 Image Optimization

- [ ] استخدام `next/image` لجميع الصور
- [ ] Lazy loading لصور الأقمار الصناعية
- [ ] WebP/AVIF format لصور المحاصيل

---

## المرحلة 7: إمكانية الوصول والتصميم (مستمر) — أولوية منخفضة 🟢

### 7.1 Accessibility (WCAG AA)

- [ ] إضافة `aria-label` لجميع الأزرار بدون نص
- [ ] إضافة `alt` لجميع الصور
- [ ] تحسين تباين الألوان (خاصة severity badges)
- [ ] دعم التنقل بلوحة المفاتيح في جميع الجداول
- [ ] اختبار مع screen reader
- [ ] إضافة pa11y للفحص التلقائي

### 7.2 Dark Mode

- [ ] اختبار Dark Mode لجميع المكونات الجديدة
- [ ] التأكد من قابلية القراءة في الوضع المظلم
- [ ] خرائط: إضافة dark tile layer

### 7.3 Responsive Design

- [ ] اختبار جميع الصفحات على الهاتف (< 640px)
- [ ] اختبار على الأجهزة اللوحية (768px-1024px)
- [ ] التأكد من أن CommandPalette يعمل على الهاتف
- [ ] تحسين DrawableMap للشاشات الصغيرة

### 7.4 Storybook

- [ ] إعداد Storybook لمكونات `components/` المشتركة
- [ ] إضافة stories لكل مكون جديد
- [ ] التكامل مع CI لبناء Storybook تلقائياً

---

## المرحلة 8: توثيق (مستمر) — أولوية منخفضة 🟢

- [ ] تحديث `apps/services-docs/README.md` بالمسارات الجديدة
- [ ] إضافة JSDoc لجميع API proxy routes
- [ ] تحديث `docs/SERVICES_MAP.md` بالخدمات المتصلة حديثاً
- [ ] إنشاء دليل المكونات (Component Guide) للمطورين الجدد
- [ ] تحديث PR description لـ #1463 ليعكس النطاق الكامل

---

## ملخص الأرقام

| المرحلة | المهام | الأولوية | المدة المتوقعة |
|---------|--------|---------|---------------|
| 1. الاختبارات | ~227 اختبار | 🔴 حرج | أسبوع 1 |
| 2. TypeScript | ~10 ملفات | 🟠 عالي | أسبوع 1-2 |
| 3. أمان وبنية | ~8 مهام | 🟠 عالي | أسبوع 2 |
| 4. تحسين الواجهات | ~16 مهمة | 🟡 متوسط | أسبوع 2-3 |
| 5. WebSocket Events | ~9 أحداث | 🟡 متوسط | أسبوع 3 |
| 6. أداء | ~10 مهام | 🟡 متوسط | أسبوع 3-4 |
| 7. إمكانية الوصول | ~15 مهمة | 🟢 منخفض | مستمر |
| 8. توثيق | ~5 مهام | 🟢 منخفض | مستمر |
| **الإجمالي** | **~300 مهمة** | | **4-6 أسابيع** |

---

_تم إنشاؤه تلقائياً من جلسة Claude Code بتاريخ 2026-04-04_
_PRs: #1463, #1464, #1465_
