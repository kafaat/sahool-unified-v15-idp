# فهرس تدقيق تطبيقات الموبايل
# Mobile Apps Audit Index

**تاريخ التحديث | Refresh Date:** 2026-04-04  
**المشروع | Project:** SAHOOL Platform v16.0.0  
**نطاق العمل | Scope:** تحديث خط الأساس ومراجعة تنفيذية لأربع تطبيقات موبايل فعلية + مسار الجاهزية والاختبارات

---

## 📋 الوثائق المتوفرة | Available Documents

### 1️⃣ التقرير التنفيذي المحدّث | Refreshed Executive Audit
**الملف | File:** `MOBILE_APPS_AUDIT_REPORT.md`

يغطي الوضع الحالي لكل من:
- `sahool_field_app`
- `sahol_atmosphere`
- `sahool_app`
- `sahool-mobile`

ويشمل:
- مصفوفة فجوات على نمط الأدمن
- خط الأساس الحالي للبنية والتكوين والاختبارات
- قرار التطبيق المرجعي للموبايل
- backlog أولويّات مباشرة

### 2️⃣ خطة الإصلاح المحدّثة | Refreshed Repair Plan
**الملف | File:** `MOBILE_APPS_REPAIR_PLAN.md`

تشمل:
- مرحلة تحديث التدقيق قبل التعديلات الواسعة
- ترتيب الأولويات لكل تطبيق
- خطوات توحيد التجربة والمكونات
- قرارات الحسم لـ `sahool_app` و `sahool-mobile`

### 3️⃣ الملخص المرئي | Visual Summary
**الملف | File:** `MOBILE_APPS_VISUAL_SUMMARY.md`

> ملاحظة: هذا الملف ما يزال مرجعاً تاريخياً بصرياً، لكن المرجع التنفيذي الحالي هو التقرير المحدّث وخطة الإصلاح المحدّثة.

---

## 📊 النتائج الرئيسية | Key Findings

### التطبيقات ضمن التدقيق الحالي | Apps in Current Scope

| التطبيق | النوع | الحالة الحالية | ملاحظات سريعة |
|---|---|---|---|
| `sahool_field_app` | Flutter app | **التطبيق المرجعي الحالي** | ناضج نسبياً، لكن فيه تشتت مسارات ووحدات وبعض فجوات جاهزية الإنتاج |
| `sahol_atmosphere` | Flutter app | **تجريبي / ناقص** | ثلاث شاشات أساسية فقط، بدون بنية تطبيق تشغيلية كاملة |
| `sahool_app` | Flutter wrapper | **طبقة wrapper غير محسومة** | يعتمد على `sahool_mobile_core` ولا يملك منصات تشغيل محلية داخل مساره |
| `sahool-mobile` | React Native shell | **مسار منفصل بحاجة قرار** | يركز على sync manager فقط تقريباً، وليس تطبيقاً كاملاً جاهزاً |

### إحصائيات الخط الأساسي | Baseline Snapshot

```text
📱 التطبيقات المدققة | Apps Audited: 4
🧭 التطبيق المرجعي المعتمد | Reference App: sahool_field_app ✅
🧪 Makefile: MOBILE_DIR => apps/mobile/sahool_field_app ✅ (fixed)
🧪 CI: mobile-release.yml & flutter-apk.yml => apps/mobile/sahool_field_app ✅ (fixed)
🧪 Flutter validation: make mobile-test => يفشل عند غياب flutter ✅
🧪 React Native: sahool-mobile => بحاجة قرار معماري (ARCHITECTURE_DECISION.md)
📦 lockfiles:
   - sahool_field_app: present ✅
   - sahol_atmosphere: present ✅
   - sahool_app: missing
   - sahool-mobile: missing (+ .env.example added ✅)
🔧 إصلاحات منفذة في هذا التحديث:
   - Makefile, CI workflows, AndroidManifest, security handling
   - Empty handlers, env config, .env.production, architecture decisions
```

---

## 🧩 مصفوفة الفجوات | Gap Matrix

| App | Config | Routes / Screens | APIs / Contracts | Security | Tests / CI | Main Gap |
|---|---|---|---|---|---|---|
| `sahool_field_app` | جيد | قوي لكن متشعب (GoRouter كبير) | مدمج مع gateway-style endpoints | جيد مع فجوات pins الفعلية | جيد نسبياً | تنظيف معماري وتوحيد الواجهات والمسارات |
| `sahol_atmosphere` | محدود | 3 شاشات فقط وبدون router فعلي | فحوصات health مباشرة فقط | فحص جهاز غير كافٍ | محدود | ينقصه auth/db/navigation/app shell |
| `sahool_app` | موجود بيئياً | يعتمد على core router | يعتمد على package core | فيه مسار أمان وcrash init | محدود | حسم دوره: منتج نهائي أم wrapper فقط |
| `sahool-mobile` | محدود | لا يوجد app shell كامل | يركز على sync manager | غير مكتمل | tests موجودة لكن غير قابلة للتشغيل بدون setup | قرار استمرار/دمج/تجميد |

---

## 🎯 الأولويات الحالية | Current Priorities

### الأولوية 1 — تحديث خط الأساس التنفيذي
- اعتماد `MOBILE_APPS_AUDIT_REPORT.md` و `MOBILE_APPS_REPAIR_PLAN.md` كمصدرين أساسيين
- عدم الاعتماد على الاستنتاجات القديمة غير المتوافقة مع البنية الحالية
- اعتبار `sahool_field_app` هو baseline المرجعي للموبايل حالياً

### الأولوية 2 — `sahool_field_app`
- تقليص التشتت المعماري في routes/features
- حصر الشاشات المكررة أو المسارات اليتيمة
- استبدال certificate pins الوهمية بالقيم الفعلية
- توحيد readiness checks ورفع جودة CI

### الأولوية 3 — `sahol_atmosphere`
- تحديد إن كان منتجاً مستقلاً أو concept app
- إن تقرر الاستمرار: إضافة auth/navigation/data layer/app shell
- إن لم يتقرر: تجميد التطوير وربطه بخارطة طريق واضحة

### الأولوية 4 — `sahool_app`
- تثبيت مسؤوليته المعمارية
- منع التداخل مع `sahool_field_app`
- توثيق هل هو مستقبل التطبيق الموحد أم مجرد wrapper فوق `sahool_mobile_core`

### الأولوية 5 — `sahool-mobile`
- اتخاذ قرار رسمي: استمرار / دمج / تجميد / أرشفة
- لا ينبغي التعامل معه كتطبيق إنتاجي كامل بصيغته الحالية

---

## 🔒 التقييم الأمني الحالي | Current Security View

### `sahool_field_app`
- ✅ API client يفعّل certificate pinning logic
- ✅ ProGuard rules تشمل Drift و SQLCipher و Notifications و Scanner و Riverpod
- ⚠️ ما تزال هناك placeholder certificate fingerprints يجب استبدالها قبل الإنتاج
- ⚠️ iOS `NSPinnedDomains` ما يزال معطلاً بتعليقات لحين توفير SPKI hashes الفعلية

### `sahol_atmosphere`
- ⚠️ يوجد device security check أولي
- ❌ لا توجد طبقة auth أو secure offline architecture مكافئة للتطبيق المرجعي
- ❌ لا توجد بنية production security متكاملة

### `sahool_app`
- ✅ يهيّئ crash/error/security flow عبر `sahool_mobile_core`
- ⚠️ يحتاج قراراً معماريّاً قبل تقييم أمني نهائي مستقل

### `sahool-mobile`
- ⚠️ يحتوي منطق sync واختبارات له
- ❌ لا يرقى حالياً إلى تقييم أمني لتطبيق كامل بسبب غياب shell والمنصات والـ setup الكامل

---

## 📚 كيفية استخدام هذا التدقيق | How to Use This Audit

### للإدارة والمنتج
- اعتبر `sahool_field_app` التطبيق المرجعي الحالي
- اطلب قراراً رسمياً حول `sahool_app` و `sahool-mobile`
- لا تبدأ feature expansion قبل غلق فجوات baseline الحالية

### للفريق التقني
- استخدم التقرير التنفيذي المحدّث لتحديد الفجوات الحقيقية الحالية
- استخدم خطة الإصلاح لتقسيم التنفيذ على مراحل صغيرة
- اعتبر أي نتائج قديمة تخالف هذا التحديث نتائج تاريخية فقط

### لفريق الجودة و CI
- راجع readiness commands أولاً
- تأكد من أن أوامر الموبايل تفشل عند فشل الأدوات بدلاً من النجاح المضلل
- ميّز بين فشل البيئة وفشل التطبيق نفسه

---

## 🎯 الخلاصة | Conclusion

التدقيق الحالي لم يعد يدعم فرضية “3 تطبيقات فقط”. الوضع الفعلي اليوم هو **أربع مسارات تطبيقات موبايل** متفاوتة النضج، مع ضرورة اعتماد `sahool_field_app` كتطبيق مرجعي، وتحديث القرار المعماري بشأن `sahool_app` و `sahool-mobile` قبل أي توسع كبير في التطوير.
