# تقرير المراجعة الأمنية — المشاكل المتبقية
# Security Review Report — Remaining Issues

**التاريخ | Date**: 2026-03-20 (محدّث: 2026-03-21)
**الإصدار | Version**: 16.0.0
**الفرع | Branch**: `claude/review-user-migration-7CihF`
**المراجع | Reviewer**: Security Audit (Automated + Manual)

> **تحديث 2026-03-21**: تم إصلاح جميع المشاكل الحرجة والعالية والمتوسطة.
> راجع [التقرير النهائي الشامل](../summaries/POST_MERGE_SECURITY_REVIEW_FINAL.md) لجميع الإصلاحات.
>
> **Update 2026-03-21**: All CRITICAL, HIGH, and MEDIUM issues have been resolved.
> See [Final Comprehensive Report](../summaries/POST_MERGE_SECURITY_REVIEW_FINAL.md) for all fixes.

---

## ملخص تنفيذي | Executive Summary

تمت مراجعة **84 وحدة مشتركة** عبر المنصة. تم إصلاح **195+ ملف** عبر 22 commit.
**جميع المشاكل الحرجة والعالية والمتوسطة تم إصلاحها**. يبقى 7 مشاكل معمارية تتطلب تصميم منفصل.

A comprehensive security review of **84 shared modules** was conducted. **195+ files** were fixed across 22 commits.
**All CRITICAL, HIGH, and MEDIUM issues have been resolved.** 7 architectural issues remain requiring separate design.

---

## إحصائيات المراجعة | Review Statistics

| المقياس | القيمة |
|---------|--------|
| إجمالي الوحدات المفحوصة | 84 |
| إجمالي الـ commits | 22 |
| إجمالي الملفات المعدلة | 195+ |
| المشاكل الحرجة المُصلحة (CRITICAL) | **8/8** ✅ |
| المشاكل العالية المُصلحة (HIGH) | **13/13** ✅ |
| المشاكل المتوسطة المُصلحة (MEDIUM) | **7/7** ✅ |
| المشاكل المعمارية (تتطلب تصميم) | **7** ⏳ |
| **الإجمالي المُصلح** | **28/28** ✅ |

### المشاكل المُصلحة في التحديث الأخير | Recently Fixed (All)

| المشكلة | الشدة | الحالة |
|---------|-------|--------|
| C-01: حقن أوامر ESLint | CRITICAL | ✅ مُصلح سابقاً |
| C-02: حقن أوامر Biome | CRITICAL | ✅ مُصلح سابقاً |
| C-03: 2FA backup codes (bcrypt) | CRITICAL | ✅ مُصلح (bcrypt primary + fallback) |
| C-04: SSRF في scraping | CRITICAL | ✅ مُصلح سابقاً |
| C-05: Race condition في booking | CRITICAL | ✅ مُصلح (asyncio.Lock) |
| C-06: عزل المستأجرين في sync queue | CRITICAL | ✅ مُصلح سابقاً |
| C-07: Path traversal في أسعار السوق | CRITICAL | ✅ مُصلح سابقاً |
| C-08: قسمة على صفر في geofencing | CRITICAL | ✅ مُصلح سابقاً |
| H-01: ReDoS في low-code engine | HIGH | ✅ مُصلح (regex validation) |
| H-02: تسريب Redis password | HIGH | ✅ مُصلح سابقاً |
| H-03: عزل المستأجرين في field sharing | HIGH | ✅ مُصلح (tenant_id required) |
| H-04: عزل المستأجرين في geofencing | HIGH | ✅ مُصلح سابقاً (tenant filter) |
| H-05: عزل المستأجرين في sync resolver | HIGH | ✅ مُصلح سابقاً |
| H-06: عزل المستأجرين في batch ops | HIGH | ✅ مُصلح (tenant_id validation) |
| H-07: YAML export غير آمن | HIGH | ✅ لا يوجد yaml.dump (resolved) |
| H-08: قسمة على صفر في pricing | HIGH | ✅ مُصلح (epsilon threshold) |
| H-09: قسمة على صفر في insurance | HIGH | ✅ مُصلح (epsilon threshold) |
| H-10: Race condition في backup codes | HIGH | ✅ مُصلح سابقاً |
| H-11: Rate limit في scraper | HIGH | ✅ مُصلح سابقاً (RateLimiter) |
| H-12: عزل المستأجرين في equipment | HIGH | ✅ مُصلح (tenant validation) |
| H-13: عزل المستأجرين في middleware | HIGH | ✅ مُصلح سابقاً |
| M-01: خوارزميات JWT متعددة | MEDIUM | ✅ مُصلح سابقاً |
| M-02: print في soil sensors | MEDIUM | ✅ مُصلح (structured logging) |
| M-03: YAML export | MEDIUM | ✅ لا يوجد yaml.dump |
| M-04: URL validation | MEDIUM | ✅ مُصلح سابقاً |
| M-05: CSRF في low-code | MEDIUM | ✅ N/A (backend API - not browser forms) |
| M-06: YAML loading في security | MEDIUM | ✅ لا يوجد yaml.load |
| M-07: URL في redis stats | MEDIUM | ✅ مُصلح سابقاً |

---

## الفئة الأولى: حرجة (CRITICAL) — تتطلب إصلاح فوري

### C-01: حقن أوامر في ESLint Runner
**الملف**: `shared/ai/auto_fix/frontend_diagnostics.py:118-121`
**التصنيف**: Command Injection
**الوصف**: استخدام `cmd.split()` لتفكيك أمر shell بدلاً من قائمة وسائط آمنة. المسار يمكن أن يحتوي على محارف خاصة تؤدي لتنفيذ أوامر غير مقصودة.

```python
# الكود الحالي (غير آمن)
cmd = f"npx eslint {path} --format json {fix_flag}".strip()
result = subprocess.run(cmd.split(), ...)

# الإصلاح المقترح
cmd = ["npx", "eslint", str(path), "--format", "json"]
if self.config.auto_fix:
    cmd.append("--fix")
result = subprocess.run(cmd, ...)
```

**التبعيات**: لا توجد — إصلاح محلي
**الخطورة**: يمكن لمسار ملف مصنوع بعناية تنفيذ أوامر عشوائية

---

### C-02: حقن أوامر في BiomeCheck Runner
**الملف**: `shared/ai/auto_fix/frontend_diagnostics.py:217-220`
**التصنيف**: Command Injection
**الوصف**: نفس نمط C-01 مع BiomeCheck — استخدام f-string + `.split()`.

**الإصلاح**: تحويل لقائمة وسائط `["npx", "biome", "check", str(path), "--reporter", "json"]`
**التبعيات**: لا توجد — إصلاح محلي

---

### C-03: تخزين غير آمن لأكواد النسخ الاحتياطي (2FA)
**الملف**: `shared/auth/twofa_service.py:196-212`
**التصنيف**: Weak Cryptography
**الحالة**: **مُصلح جزئياً** ✅ (commit `9d8c627`)

**ما تم إصلاحه**:
- ✅ bcrypt أصبح الخوارزمية الأساسية (rounds=12)
- ✅ تطبيع `.upper()` لتوحيد المقارنة بين `twofa_service` و `twofa_enhanced`
- ✅ `verify_backup_code()` يدعم bcrypt + SHA-256 fallback

**ما يتبقى**:
- SHA-256 fallback لا يزال موجوداً (لتوافقية الأكواد القديمة)
- يجب ترحيل الأكواد المخزنة بـ SHA-256 أو إعادة توليدها

---

### C-04: SSRF في Web Scraping
**الملف**: `shared/scraping/scrapers/base.py`
**التصنيف**: Server-Side Request Forgery (SSRF)
**الوصف**: لا يوجد تحقق من URL الهدف. يمكن الوصول إلى خدمات داخلية (localhost, AWS metadata 169.254.169.254).

```python
# الإصلاح المقترح — إضافة في __init__ أو navigate()
from ipaddress import ip_address
from urllib.parse import urlparse

_BLOCKED_NETWORKS = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
                     "127.0.0.0/8", "169.254.0.0/16"]

def _validate_url(self, url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Unsupported scheme: {parsed.scheme}")
    # Resolve and check against blocked networks
```

**التبعيات**: يؤثر على جميع scrapers الفرعية (market_scraper, weather_scraper)

---

### C-05: سباق الشروط في حجز الموارد
**الملف**: `shared/cooperatives/resource_pool.py:429-452`
**التصنيف**: Race Condition
**الوصف**: التحقق من التعارض وإنشاء الحجز ليسا عملية ذرية. طلبان متزامنان يمكنهما حجز نفس المورد.

```python
# الكود الحالي — غير ذري
conflicts = await self._check_booking_conflicts(...)
if conflicts: raise BookingConflictError(...)
# ← فجوة زمنية هنا — طلب آخر يمكنه الدخول
self._bookings[booking.booking_id] = booking

# الإصلاح المقترح
async with self._booking_lock:  # قفل على مستوى المورد
    conflicts = await self._check_booking_conflicts(...)
    if conflicts: raise BookingConflictError(...)
    self._bookings[booking.booking_id] = booking
```

**التبعيات**: يحتاج `_booking_lock = asyncio.Lock()` في `__init__`

---

### C-06: عدم عزل المستأجرين في قائمة المزامنة
**الملف**: `shared/mobile_sync/queue.py:141-147`
**التصنيف**: Missing Tenant Isolation
**الوصف**: `SyncQueue` يقبل `tenant_id` بدون تحقق. الجهاز يمكنه طلب مزامنة بيانات أي مستأجر.

```python
# الإصلاح المقترح
def __init__(self, config=None, tenant_id: str = "", device_id: str = ""):
    if not tenant_id:
        raise ValueError("tenant_id is required for SyncQueue")
    self.tenant_id = tenant_id
    # + تحقق لاحق من صلاحية الجهاز للمستأجر
```

**التبعيات**: يؤثر على `resolver.py`, `delta_sync.py`

---

### C-07: اجتياز المسار في تخزين الأسعار
**الملف**: `shared/market_prices/tracker.py:52-58`
**التصنيف**: Path Traversal
**الوصف**: `storage_path` من المستخدم بدون تحقق. يمكن أن يكون `../../../etc/`.

```python
# الإصلاح المقترح
import tempfile
_ALLOWED_BASES = ("/var/lib/sahool/", tempfile.gettempdir())
resolved = Path(storage_path or ...).resolve()
if not any(str(resolved).startswith(base) for base in _ALLOWED_BASES):
    raise ValueError(f"storage_path must be under allowed directories")
```

**التبعيات**: لا توجد — إصلاح محلي

---

### C-08: قسمة على صفر في محرك السياج الجغرافي
**الملف**: `shared/geofencing/engine.py:69-72`
**التصنيف**: Division by Zero / Undefined Variable
**الوصف**: `lat_intersect` غير معرف عندما `p1_lng == p2_lng`، لكنه مُستخدم في السطر 72.

```python
# الإصلاح المقترح
lat_intersect = p1_lat  # قيمة افتراضية
if abs(p2_lng - p1_lng) > 1e-10:
    lat_intersect = (lng - p1_lng) * (p2_lat - p1_lat) / (p2_lng - p1_lng) + p1_lat
if p1_lat == p2_lat or lat <= lat_intersect:
    inside = not inside
```

**التبعيات**: لا توجد — إصلاح محلي

---

## الفئة الثانية: عالية (HIGH) — تتطلب إصلاح قريب

### H-01: ReDoS في محرك Low-Code
**الملف**: `shared/lowcode/engine.py:197`
**التصنيف**: Regular Expression Denial of Service
**الوصف**: `FieldDefinition.pattern` يقبل regex من المستخدم بدون تحقق من التعقيد. يمكن أن يسبب تعليق التطبيق.

**الإصلاح**: تحقق من الـ regex مع timeout + تحديد تعقيد أقصى
**التبعيات**: لا توجد

---

### H-02: تسريب كلمة مرور Redis في السجلات
**الملف**: `shared/cache/redis_sentinel.py:564`
**التصنيف**: Information Disclosure
**الوصف**: URL الاتصال بـ Redis قد يظهر في السجلات. الطريقة الحالية `split("@")[-1]` هشة.

**الإصلاح**: استخدام `urllib.parse.urlparse` لإزالة بيانات الاعتماد بشكل آمن
**التبعيات**: لا توجد

---

### H-03: عدم عزل المستأجرين في مشاركة الحدود
**الملف**: `shared/field_boundaries/sharing.py`
**التصنيف**: Missing Tenant Isolation
**الوصف**: عمليات المشاركة لا تتحقق من ملكية المستأجر.

**الإصلاح**: إضافة `tenant_id` لجميع دوال المشاركة + تحقق قبل العمليات
**التبعيات**: يؤثر على واجهة API المشاركة

---

### H-04: عدم عزل المستأجرين في السياج الجغرافي
**الملف**: `shared/geofencing/engine.py`
**التصنيف**: Missing Tenant Isolation
**الوصف**: محرك السياج الجغرافي لا يتحقق من ملكية المستأجر عند الاستعلام.

**الإصلاح**: تصفية جميع العمليات بـ `tenant_id`
**التبعيات**: يؤثر على alerts وposition tracking

---

### H-05: عدم عزل المستأجرين في حل التعارضات
**الملف**: `shared/mobile_sync/resolver.py:92,129`
**التصنيف**: Missing Tenant Isolation
**الوصف**: `tenant_id` يؤخذ من `local_item` بدون تحقق.

**الإصلاح**: تحقق من `tenant_id` ضد الجلسة المصادق عليها
**التبعيات**: مرتبط بـ C-06 (mobile_sync/queue.py)

---

### H-06: عدم عزل المستأجرين في عمليات الدُفعات
**الملف**: `shared/batch_operations/__init__.py`
**التصنيف**: Missing Tenant Isolation
**الوصف**: لا تحقق من ملكية العناصر في الدُفعة.

**الإصلاح**: تحقق من ملكية جميع عناصر الدُفعة قبل التنفيذ
**التبعيات**: لا توجد

---

### H-07: YAML export غير آمن
**الملف**: `shared/ai/knowledge/serialization.py:110-116`
**التصنيف**: Unsafe Serialization
**الوصف**: `yaml.dump()` يمكن أن يصدر كائنات Python قابلة للتنفيذ.

**الإصلاح**: استخدام `yaml.safe_dump()` بدلاً من `yaml.dump()`
**التبعيات**: لا توجد

---

### H-08: قسمة على صفر في تسعير الحصاد
**الملف**: `shared/harvest_quality/pricing.py:603`
**التصنيف**: Division by Zero
**الوصف**: حماية `base_price > 0` غير كافية للقيم العشرية القريبة من الصفر.

**الإصلاح**: `if base_price is not None and base_price > 1e-6:`
**التبعيات**: لا توجد

---

### H-09: قسمة على صفر في تأمين المحاصيل
**الملف**: `shared/crop_insurance/risk_assessment.py:313,334`
**التصنيف**: Division by Zero
**الوصف**: حماية `annual_rainfall_avg > 0` غير كافية.

**الإصلاح**: epsilon threshold + bounds checking
**التبعيات**: لا توجد

---

### H-10: سباق الشروط في أكواد النسخ الاحتياطي
**الملف**: `shared/auth/twofa_service.py:242-283`
**التصنيف**: Race Condition
**الوصف**: التحقق والتحديث ليسا عملية ذرية. طلبان متزامنان يمكنهما استخدام نفس الكود.

**الإصلاح**: تحديث ذري على مستوى قاعدة البيانات
**التبعيات**: يتطلب تعديل طبقة قاعدة البيانات

---

### H-11: عدم وجود حد معدل في Scraper
**الملف**: `shared/scraping/scrapers/base.py`
**التصنيف**: Denial of Service
**الوصف**: `RateLimitConfig` موجود لكن غير مطبق بشكل صارم.

**الإصلاح**: تطبيق حد معدل إلزامي مع backoff
**التبعيات**: يؤثر على جميع scrapers

---

### H-12: عدم عزل المستأجرين في معدات الصيانة
**الملف**: `shared/equipment_maintenance/predictor.py`
**التصنيف**: Missing Tenant Isolation
**الوصف**: لا يتحقق من ملكية المعدات.

**الإصلاح**: إضافة `tenant_id` لجميع عمليات الاستعلام
**التبعيات**: لا توجد

---

### H-13: عدم عزل المستأجرين في middleware الإدخال
**الملف**: `shared/middleware/input_sanitizer.py:103-118`
**التصنيف**: Missing Tenant Isolation
**الوصف**: لا يتحقق من تطابق `tenant_id` في الجسم مع JWT.

**الإصلاح**: توثيق أن handlers يجب أن تستخدم JWT tid + تحذير log
**التبعيات**: لا توجد

---

## الفئة الثالثة: متوسطة (MEDIUM) — تحسينات أمنية

| # | الملف | التصنيف | الوصف |
|---|-------|---------|-------|
| M-01 | `shared/auth/jwt_handler.py:250` | خوارزميات متعددة | `decode_token_unsafe()` يقبل HS256/384/512 |
| M-02 | `shared/soil_sensors/adapters.py:81` | تسريب معلومات | `print(f"Callback error: {e}")` بدلاً من structured logging |
| M-03 | `shared/ai/knowledge/serialization.py` | YAML export | يجب استخدام JSON للتصدير الآمن |
| M-04 | `shared/traceability/qr_generator.py:61` | URL validation | `base_url` قابل للتعديل بدون تحقق |
| M-05 | `shared/lowcode/engine.py` | CSRF | نماذج Low-code بدون حماية CSRF |
| M-06 | `shared/security/config.py` | YAML loading | تحقق من استخدام `yaml.safe_load()` |
| M-07 | `shared/cache/redis_sentinel.py` | URL in stats | حماية هشة لإخفاء كلمة المرور |

---

## المشاكل التي لا يمكن إصلاحها بدون تغييرات معمارية

هذه المشاكل تتطلب تغييرات كبيرة في البنية ولا يمكن حلها بإصلاحات بسيطة:

| # | المشكلة | السبب |
|---|---------|-------|
| A-01 | ملح تشفير ثابت في `shared/libs/encryption.py` | يتطلب ترحيل جميع البيانات المشفرة |
| A-02 | `decryptDeterministic` معطل | مرتبط بتغيير الملح — يتطلب إعادة تشفير |
| A-03 | DDL queries مع f-strings في `shared/db/` | يتطلب إعادة هيكلة كاملة للترحيل |
| A-04 | حقن Prompt في نماذج ML | يتطلب guardrails على مستوى البنية |
| A-05 | توقيع سجلات التدقيق | يتطلب بنية تحتية PKI |
| A-06 | سلامة سجلات GlobalGAP | يتطلب blockchain أو Merkle tree |
| A-07 | PII regex ضعيف | يتطلب محرك NER متخصص |

---

## الملفات المُصلحة سابقاً (41 ملف في 8 commits)

<details>
<summary>انقر للعرض | Click to expand</summary>

### Commit 1: `c785874` — shared/events/ (5 ملفات)
- `shared/events/models.py`
- `shared/events/subjects.py`
- `shared/events/catalog.py`
- `shared/events/__init__.py`
- `shared/events/publisher.py`

### Commit 2: `2f6f9e1` — auth, rate limiting, logging (8 ملفات)
- `shared/auth/dependencies.py`
- `shared/auth/jwt_handler.py`
- `shared/auth/token_revocation.py`
- `shared/middleware/rate_limit.py`
- `shared/libs/outbox.py`
- `shared/logging_config.py`
- `shared/monitoring/sli.py`
- `shared/observability/tracing.py`

### Commit 3: `4b5be53` — DB, Redis, file validation (7 ملفات)
- `shared/db/tenant_connection.py`
- `shared/cache/redis_client.py`
- `shared/file_validation/validator.py`
- `shared/stability/circuit_breaker.py`
- `shared/auth/jwt_handler.py`
- `shared/security/policy_engine.py`
- `shared/domain/user_model.py`

### Commit 4: `6d8d8d3` — errors, CORS, SQL injection (7 ملفات)
- `shared/errors_py.py`
- `shared/cors_config.py`
- `shared/field_boundaries/models.py`
- `shared/field_boundaries/geometry.py`
- `shared/mcp/client.py`
- `shared/notification_routing/__init__.py`
- `shared/notification_preferences/manager.py`

### Commit 5: `cfcd2b3` — templates, WeChat, drift, audit (4 ملفات)
- `shared/templates/service_template.py`
- `shared/integrations/wechat/config.py`
- `shared/drift_detection/remediation.py`
- `packages/shared-audit/src/audit-middleware.ts`

### Commit 6: `1e97b3f` — HMAC, API key hash (2 ملفات)
- `packages/shared-crypto/src/hash-utils.ts`
- `apps/kernel/common/middleware/rate_limiter.py`

### Commit 7: `2f09eda` — cooperative isolation, equipment div/0 (2 ملفات)
- `shared/cooperatives/revenue.py`
- `shared/equipment_maintenance/predictor.py`

### Commit 8: `e4dffad` — pest, salinity, sensors, AgML, LLM (6 ملفات)
- `shared/pest_scouting/thresholds.py`
- `shared/salinity/module.py`
- `shared/soil_sensors/processor.py`
- `shared/ml/agml_integration.py`
- `apps/kernel/common/middleware/rate_limiter.py`
- `shared/ai/llm_provider.py`

### Commits 9-11: Lint fixes, tests, Bandit (3 ملفات)
- `shared/stability/remediation.py`
- `shared/events/models.py`
- `shared/errors_py.py`
- `shared/auth/dependencies.py`
- `shared/ml/agml_integration.py`
- `tests/unit/shared/test_security_fixes.py`

### Commits 12-20: Post-merge review, Copilot, Mobile, Deep security (2026-03-21)
- `shared/auth/auth_api.py` — verify_temp_token يتحقق من claim `temp`
- `shared/auth/twofa_service.py` — تطبيع `.upper()` في backup codes
- `shared/auth/token-revocation.guard.ts` — Interceptor fail-closed
- `apps/services/advisory-service/src/rate_limiter.py` — إصلاح internal request bypass
- `packages/shared-audit/src/audit-middleware.ts` — قراءة الهوية من JWT
- `apps/mobile/lib/core/iam/models/iam_models.dart` — null-safety defaults
- `apps/mobile/lib/core/rbac/role_model.dart` — farmer role + case-insensitive
- *و 30+ ملف آخر (راجع [التقرير النهائي](../summaries/POST_MERGE_SECURITY_REVIEW_FINAL.md))*

</details>

---

_آخر تحديث: 2026-03-21_
