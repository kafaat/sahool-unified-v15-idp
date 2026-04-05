# خطة إصلاح تطبيقات الموبايل - التحديث التنفيذي
# Mobile Apps Repair Plan - Executive Refresh

**تاريخ التحديث | Refresh Date:** 2026-04-04  
**مستوى الأولوية | Priority Level:** Critical Baseline Alignment  
**الهدف | Goal:** تحديث التدقيق أولاً، ثم تنفيذ تحسينات صغيرة مرتّبة بدل تعديلات واسعة غير منظمة

---

## المرحلة 0: تثبيت خط الأساس | Phase 0: Baseline Lock

### الهدف | Goal
منع أي تنفيذ واسع قبل توحيد الصورة الفعلية لتطبيقات الموبايل.

### المهام | Tasks
- [x] اعتماد `sahool_field_app` كتطبيق baseline رسمي للموبايل
- [x] اعتماد `MOBILE_APPS_AUDIT_REPORT.md` و `MOBILE_APPS_REPAIR_PLAN.md` كمصدرين تنفيذيين محدثين
- [x] توثيق أن `sahool_app` و `sahool-mobile` يحتاجان قراراً معمارياً منفصلاً — تم إنشاء `ARCHITECTURE_DECISION.md` لكل منهما
- [x] عدم استخدام الاستنتاجات التاريخية القديمة إذا خالفت هذا التحديث

### المخرجات | Deliverables
- baseline واضح
- أولويات واضحة
- تقليل الالتباس بين التطبيقات الأربعة

---

## المرحلة 1: إصلاحات الجاهزية الفورية | Phase 1: Immediate Readiness Fixes

### 1.1 `sahool_field_app` كمرجع إنتاجي
- [ ] استبدال placeholder certificate fingerprints بالقيم الفعلية
- [ ] تفعيل / توثيق iOS native pinning بعد توفير SPKI hashes الحقيقية
- [ ] حصر الـ routes والشاشات وربطها بالميزات المستخدمة فعلياً
- [ ] تحديد الشاشات المكررة أو المسارات اليتيمة أو legacy flows
- [ ] مراجعة استهلاك الـ API endpoints وربطه بالعقود المشتركة الحالية

### 1.2 CI / Validation
- [x] جعل `make mobile-test` يفشل عند فشل أو غياب Flutter بدل النجاح المضلل ✅
- [x] مراجعة بقية أوامر الموبايل — تم إصلاح `MOBILE_DIR` ليشير إلى `sahool_field_app` مباشرة
- [ ] توثيق الفرق بين فشل البيئة وفشل التطبيق
- [x] تثبيت baseline: تم إصلاح `mobile-release.yml` و `flutter-apk.yml` working-directory paths

---

## المرحلة 2: تنظيف `sahool_field_app` | Phase 2: Field App Consolidation

### الهدف | Goal
تنظيف التطبيق المرجعي قبل أي توسع وظيفي جديد.

### المسارات الرئيسية | Main Tracks

#### A. التنقل والشاشات
- [ ] بناء inventory واضح: route → screen → feature owner
- [ ] إزالة أو دمج المسارات المتداخلة
- [ ] توحيد entry points للشاشات الرئيسية
- [ ] توحيد app shell patterns مع ما هو قائم في admin

#### B. الوحدات والمكونات
- [ ] تصنيف features إلى: active / duplicate / legacy / demo
- [ ] تقليل التداخل بين `features/*` القديمة والجديدة
- [ ] توحيد naming و folder conventions

#### C. الجودة والاتساق
- [ ] توحيد loading/error/empty states
- [ ] رفع consistency في RTL والعربية
- [ ] مراجعة accessibility الأساسية للشاشات المحورية

---

## المرحلة 3: قرار `sahol_atmosphere` | Phase 3: Atmosphere Decision Track

### سؤال القرار | Decision Question
هل `sahol_atmosphere` تطبيق منتج مستقل أم concept app؟

### إذا كان Product Track
- [ ] إضافة router فعلي
- [ ] إضافة auth flow
- [ ] إضافة data layer / repository layer
- [ ] إضافة local persistence أو تبرير غيابها
- [ ] بناء roadmap واضحة للشاشات المطلوبة

### إذا كان Concept / Experimental Track
- [ ] تقليل التوقعات التشغيلية في الوثائق
- [ ] وسمه كمسار تجريبي
- [ ] منع التداخل مع baseline product commitments

---

## المرحلة 4: قرار `sahool_app` | Phase 4: Unified Wrapper Decision

### سؤال القرار | Decision Question
هل `sahool_app` هو التطبيق الموحد المستقبلي أم مجرد wrapper مرحلي فوق `sahool_mobile_core`؟

### المطلوب | Required Work
- [ ] توثيق علاقة `sahool_app` مع `sahool_field_app`
- [ ] توثيق حدود المسؤولية مع `sahool_mobile_core`
- [ ] تحديد هل سيتم نقل baseline إليه لاحقاً أم لا
- [ ] منع ازدواجية التطوير بين المسارين

---

## المرحلة 5: قرار `sahool-mobile` | Phase 5: React Native Track Decision

### سؤال القرار | Decision Question
هل يبقى `sahool-mobile` مساراً معتمداً؟

### الخيارات | Options
- [ ] الاستمرار كمنتج منفصل مع setup كامل وخارطة طريق
- [ ] الدمج مع Flutter strategy
- [ ] التجميد
- [ ] الأرشفة

### ملاحظات تنفيذية | Execution Notes
- وجود `syncManager` واختباراته لا يكفي لتصنيفه كتطبيق إنتاجي كامل
- غياب lockfile ومنصات المسار الحالية يرفع تكلفة استمراره بصيغته الحالية

---

## المرحلة 6: مصفوفة التنفيذ | Execution Matrix

| الأولوية | المسار | النتيجة المطلوبة |
|---|---|---|
| P0 | audit baseline | توحيد الرؤية قبل التوسع |
| P0 | field app security/readiness | جاهزية إنتاجية حقيقية بدون placeholders |
| P1 | field app consolidation | تقليل التشتت المعماري |
| P1 | atmosphere decision | إما roadmap حقيقية أو تثبيت كمسار تجريبي |
| P1 | sahool_app decision | وضوح المعمارية ومنع التداخل |
| P1 | sahool-mobile decision | حسم الاستثمار أو الإيقاف |

---

## معايير النجاح | Success Criteria

- [ ] أصبح لدى الفريق تطبيق baseline واحد واضح للموبايل
- [ ] لم تعد الوثائق تشير إلى افتراض “3 تطبيقات فقط”
- [ ] لم تعد أوامر الجاهزية تعطي نجاحاً مضللاً
- [ ] تم توثيق الدور الحقيقي لـ `sahool_app`
- [ ] تم اتخاذ قرار رسمي حول `sahool-mobile`
- [ ] أصبحت فجوات `sahol_atmosphere` موثقة كقرار منتج/تقني لا كغموض

---

## الخلاصة | Conclusion

الأولوية الآن ليست “التطوير أكثر”، بل **تثبيت الواقع المعماري وتخفيض الالتباس**. بعد ذلك فقط تصبح الإصلاحات الكودية اللاحقة ذات أثر حقيقي ومستدام.
