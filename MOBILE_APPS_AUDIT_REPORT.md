# تقرير تدقيق تطبيقات الموبايل - تحديث خط الأساس
# Mobile Apps Audit Report - Baseline Refresh

**تاريخ التحديث | Refresh Date:** 2026-04-04  
**الإصدار | Version:** 16.0.0  
**المشروع | Project:** SAHOOL Platform  
**نوع الوثيقة | Document Type:** تحديث تنفيذي مباشر يحل محل اللقطات الأقدم عند التعارض | Direct executive refresh that supersedes older snapshots when conflicts exist

---

## 1. الملخص التنفيذي | Executive Summary

هذا التحديث يعيد ضبط خط الأساس لتطبيقات الموبايل قبل تنفيذ أي تحسينات واسعة. المراجعة السابقة لم تعد كافية كمصدر وحيد لأن الشجرة الحالية تحتوي على أربعة مسارات تطبيقات فعلية يجب التفريق بينها بوضوح:

1. `sahool_field_app`
2. `sahol_atmosphere`
3. `sahool_app`
4. `sahool-mobile`

### القرار التنفيذي الحالي | Current Executive Decision
- **التطبيق المرجعي للموبايل حالياً هو `sahool_field_app`.**
- `sahol_atmosphere` يحتاج قرار استمرار/إعادة تعريف.
- `sahool_app` يحتاج حسم دوره المعماري.
- `sahool-mobile` يحتاج قراراً رسمياً: استمرار أو دمج أو تجميد أو أرشفة.

---

## 2. خط الأساس المثبت بالأدلة | Evidence-Based Baseline

### 2.1 هيكل التطبيقات | Application Structure

| App | Stack | Files Snapshot | Platforms in Path | Lockfile | Quick Read |
|---|---|---:|---|---|---|
| `sahool_field_app` | Flutter | 675 Dart files, 165 test files, 6 integration tests | android/ios/web/linux/macos/windows | ✅ | التطبيق الأكثر نضجاً واتساعاً |
| `sahol_atmosphere` | Flutter | 18 Dart files, 4 tests, 3 screen classes | android/ios/web/linux/macos/windows | ✅ | concept app محدود التنفيذ |
| `sahool_app` | Flutter wrapper | 7 Dart files, 1 test, 2 integration tests | لا توجد منصات تشغيل داخل مساره | ❌ | wrapper فوق `sahool_mobile_core` |
| `sahool-mobile` | React Native | 4 TS/TSX files تقريباً + sync tests | لا توجد منصات تشغيل داخل المسار | ❌ | shell تقني يركز على sync manager |

### 2.2 التحقق التشغيلي الحالي | Current Validation Baseline

| Command | Result | Interpretation |
|---|---|---|
| `make mobile-analyze` | ❌ failed | `flutter` غير متوفر في بيئة الـ sandbox الحالية |
| `make mobile-test` | ⚠️ كان success مضللاً | target كان يخفي فشل flutter، وتم تصحيح ذلك في هذا التحديث |
| `npm test -- --runInBand` داخل `apps/mobile/sahool-mobile` | ❌ failed | `jest` غير متاح لعدم وجود تثبيت dependencies/lockfile جاهز |

### 2.3 ملاحظات مهمة | Important Notes
- وجود `pubspec.lock` في `sahool_field_app` و `sahol_atmosphere` يعني أن ادعاء “lockfile مفقود” لم يعد صحيحاً لهذين التطبيقين.
- `sahool_app` لا يبدو تطبيقاً مستقلاً كاملاً داخل مساره؛ هو bootstrap/wrapper يعتمد على package خارجي.
- `sahool-mobile` ليس shell إنتاجياً كاملاً حالياً رغم وجود service logic واختبارات sync.

---

## 3. مصفوفة مراجعة على نمط الأدمن | Admin-Style Review Matrix

| App | Config & Env | Routes & Screens | APIs & Contracts | Security | Storage / Offline | Tests & CI | Primary Gaps |
|---|---|---|---|---|---|---|---|
| `sahool_field_app` | جيد | قوي لكن متشعب | مدمج مع gateway-style endpoints | جيد مع فجوة pins الحقيقية | قوي | جيد نسبياً | route sprawl, duplicate/legacy features, production pin completion |
| `sahol_atmosphere` | محدود | MaterialApp + 3 شاشات فقط | health checks مباشرة وبعض env use | أولي فقط | لا توجد بنية offline مكافئة | محدود | ينقصه app shell + auth + db + domain flows |
| `sahool_app` | env files موجودة | يعتمد على router من core package | يعتمد على `sahool_mobile_core` | فيه crash/security bootstrap | غير واضح محلياً | محدود | role ambiguity and overlap with field app |
| `sahool-mobile` | package.json فقط تقريباً | لا يوجد app shell مكتمل | يركز على sync manager | غير مكتمل كتطبيق | sync-oriented only | tests موجودة لكن baseline غير جاهز | strategic decision required |

---

## 4. التقييم التفصيلي لكل تطبيق | Per-App Assessment

### 4.1 `sahool_field_app`

#### الوضع الحالي | Current State
- يستخدم `GoRouter` مع guard للمصادقة.
- يضم router كبيراً (~61 `GoRoute` + `ShellRoute` واحد) ما يشير إلى غنى وظيفي لكن أيضاً إلى خطر التشتت.
- هو التطبيق الوحيد الذي يملك حالياً مزيجاً واضحاً من: auth, security, offline database, sync, notifications, deep links, localization, وواجهات متعددة.

#### ما تم التحقق منه فعلياً | Verified Now
- `ApiClient` يدمج `CertificatePinningService` فعلياً.
- `android/app/proguard-rules.pro` يحتوي بالفعل قواعد لـ Drift و SQLCipher و Notifications و Mobile Scanner و Riverpod.
- `ios/Runner/Info.plist` يحتوي permissions أساسية للكاميرا والموقع والصور والـ Face ID.

#### الفجوات الحالية | Current Gaps
1. **Production certificate pins ما تزال placeholder**
   - المنظومة موجودة، لكن القيم النهائية للشهادات لم تُثبت بعد.
2. **iOS native pinned domains ما تزال معلّقة بتعليقات**
   - الحماية على مستوى Dart موجودة، لكن native ATS pinning غير مفعّل بعد.
3. **اتساع معماري كبير في المسارات والميزات**
   - هناك حاجة لحصر الشاشات المتداخلة والميزات القديمة/المكررة.
4. ~~**التقرير القديم أصبح فيه drift عن الواقع**~~ ✅ تم تحديث التقارير المرجعية.
5. ~~**جاهزية CI للموبايل تحتاج tightening**~~ ✅ تم إصلاح:
   - `Makefile MOBILE_DIR` يشير الآن إلى `sahool_field_app` مباشرة
   - `mobile-release.yml` و `flutter-apk.yml` working-directory paths مصلحة
   - cache key paths تشير إلى `sahool_field_app/pubspec.lock`
6. ~~**hardcoded demo tenant ID**~~ ✅ تم حذف القيمة `sahool-demo` من `env_config.dart`
7. ~~**missing .env.production**~~ ✅ تم إنشاء `.env.production.template` كقالب آمن؛ يتم إنشاء `.env.production` محلياً/تشغيلياً منه عند الحاجة

#### الحكم التنفيذي | Executive Verdict
`/home/runner/work/sahool-unified-v15-idp/sahool-unified-v15-idp/apps/mobile/sahool_field_app` هو **التطبيق المرجعي المعتمد للتطوير والتحسين**.

---

### 4.2 `sahol_atmosphere`

#### الوضع الحالي | Current State
- تطبيق Flutter تجريبي/تصوري بواجهة بصرية خاصة.
- `main.dart` يستخدم `MaterialApp` مباشر مع `DashboardScreen` كـ home.
- لا يوجد router تطبيقي فعلي أو flows تشغيلية مكافئة للتطبيق المرجعي.

#### ما تم التحقق منه فعلياً | Verified Now
- توجد فقط ثلاث شاشات أساسية ظاهرة من `lib/screens`.
- يوجد `ServiceHealthWidget` يجري health checks مباشرة على `/api/v1/.../healthz` باستخدام `API_URL` compile-time env.
- يوجد device security check أولي في `main.dart`.

#### الفجوات الحالية | Current Gaps
1. لا يوجد auth flow واضح.
2. لا توجد طبقة بيانات / قاعدة محلية / sync architecture بمستوى production.
3. لا يوجد app shell أو route map حقيقي.
4. coverage الوظيفي للشاشات منخفض جداً بالنسبة لنطاق المنتج المتوقع.

#### الإصلاحات المنفذة | Fixes Applied
- ✅ أُضيفت صلاحيات Android المفقودة (INTERNET, LOCATION) وإعدادات الأمان (`allowBackup=false`, `usesCleartextTraffic=false`)
- ✅ تحسين معالجة أمان الجهاز في `main.dart` مع تسجيل حالة emulator
- ✅ تحسين `device_security.dart`: حالات فشل root/jailbreak detection تُسجل كتهديد محتمل في الإنتاج
- ✅ استبدال الأزرار الفارغة في dashboard و fields list و field map و field card بتعليقات TODO ورسائل مستخدم
- ✅ توثيق `voice_control_button.dart` مع خطوات تكامل speech_to_text الفعلية

#### الحكم التنفيذي | Executive Verdict
هذا المسار يحتاج قراراً سريعاً: **إما تحويله إلى تطبيق مستقل فعلياً أو تثبيته كـ concept/secondary experience** وربطه بخارطة طريق واقعية.

---

### 4.3 `sahool_app`

#### الوضع الحالي | Current State
- Entry point خفيف يعتمد على `sahool_mobile_core`.
- `main.dart` و `app.dart` يهيئان crash reporting و error reporting و security و router من package خارجي.
- توجد ملفات بيئة متعددة داخل المسار (`.env.development`, `.env.staging`, `.env.production`).

#### الفجوات الحالية | Current Gaps
1. لا توجد منصات تشغيل مستقلة داخل المسار نفسه.
2. لا توجد هوية واضحة هل هو المنتج المستقبلي الموحد أم wrapper مرحلي.
3. يوجد احتمال تداخل مسؤوليات مع `sahool_field_app`.

#### الحكم التنفيذي | Executive Verdict
يجب توثيق قرار معماري صريح: **هل `sahool_app` هو successor موحد، أم مجرد bootstrap layer فوق core package؟** بدون هذا القرار ستستمر الازدواجية.

#### الإصلاحات المنفذة | Fixes Applied
- ✅ تم إنشاء `ARCHITECTURE_DECISION.md` يوثق القرار المطلوب ويحدد ثلاثة خيارات
- ✅ تم توثيق علاقته مع `sahool_field_app` ومتطلبات الحسم المعماري

---

### 4.4 `sahool-mobile`

#### الوضع الحالي | Current State
- React Native path يحتوي package.json ومنطق sync manager واختبارات له.
- لا توجد مؤشرات على app shell إنتاجي متكامل داخل المسار الحالي.
- لا يوجد lockfile مثبت في المسار.

#### ما تم التحقق منه فعلياً | Verified Now
- يوجد `src/services/syncManager.ts` واختبارات Jest مرتبطة به.
- `npm test` لا يعمل مباشرة في الـ sandbox لغياب `jest` الناتج عن عدم تثبيت dependencies.

#### الفجوات الحالية | Current Gaps
1. لا يوجد قرار استراتيجي واضح لسبب بقاء هذا المسار منفصلاً.
2. لا يوجد baseline تشغيل متكامل أو منصات واضحة داخل المسار الحالي.
3. المخاطر عالية إذا استمر كمسار غامض بالتوازي مع Flutter apps.

#### الحكم التنفيذي | Executive Verdict

#### الإصلاحات المنفذة | Fixes Applied
- ✅ تم إنشاء `.env.example` لضبط بيئة التطوير
- ✅ تم إنشاء `ARCHITECTURE_DECISION.md` يوثق القرار المطلوب ويحدد أربعة خيارات مع توصية
`/home/runner/work/sahool-unified-v15-idp/sahool-unified-v15-idp/apps/mobile/sahool-mobile` يحتاج **قراراً إدارياً وتقنياً مباشراً** قبل أي استثمار إضافي.

---

## 5. القرارات المطلوبة الآن | Decisions Required Now

### قرار 1: تثبيت التطبيق المرجعي
اعتماد `sahool_field_app` كتطبيق baseline للموبايل إلى أن يُحسم مستقبل `sahool_app` رسمياً.

### قرار 2: `sahool_app`
اختيار واحد فقط:
- successor موحّد
- wrapper مرحلي
- أو مسار تجريبي داخلي

### قرار 3: `sahool-mobile`
اختيار واحد فقط:
- الاستمرار مع roadmap واضحة
- الدمج
- التجميد
- الأرشفة

### قرار 4: `sahol_atmosphere`
اختيار واحد فقط:
- product track مستقل
- concept app
- secondary module experience

---

## 6. backlog الأولويّات | Prioritized Backlog

### P0 — Immediate
1. تحديث الوثائق المرجعية للموبايل وفق البنية الحالية.
2. اعتبار `sahool_field_app` baseline product app.
3. استبدال certificate pins الوهمية بالقيم الحقيقية.
4. تثبيت readiness signals بحيث تفشل أوامر CI عند فشل الأدوات فعلياً.

### P1 — High
1. حصر route/screen duplication داخل `sahool_field_app`.
2. ربط features بالمسارات والعقود المشتركة بشكل أوضح.
3. تقييم شاشات/وحدات `sahol_atmosphere` مقابل scope المطلوب.
4. إصدار قرار معماري مكتوب لـ `sahool_app` و `sahool-mobile`.

### P2 — Medium
1. توحيد loading / empty / error states مع مستوى الجودة الموجود في admin.
2. تقوية a11y و RTL consistency.
3. توحيد telemetry/monitoring expectations across active mobile paths.

---

## 7. الخلاصة | Conclusion

التحسين المطلوب الآن ليس “إضافة ميزات عشوائية”، بل **تنظيف المشهد المعماري للموبايل وتثبيت baseline موثوق**. هذا التحديث يضع الوضع الحالي بوضوح:
- `sahool_field_app` = المرجع العملي الحالي
- `sahol_atmosphere` = ناقص وظيفياً ويحتاج قراراً
- `sahool_app` = wrapper/مسار موحد غير محسوم
- `sahool-mobile` = مسار React Native يحتاج قراراً استراتيجياً

أي تنفيذ لاحق يجب أن ينطلق من هذه الحقيقة أولاً.
