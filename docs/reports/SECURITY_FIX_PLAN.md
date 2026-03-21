# خطة الإصلاح الأمني التفصيلية — المراحل والتبعيات
# Security Fix Execution Plan — Phases, Dependencies & Best Approaches

**التاريخ | Date**: 2026-03-20
**الإصدار | Version**: 16.0.0
**المرجع | Reference**: [SECURITY_REVIEW_REMAINING_ISSUES.md](./SECURITY_REVIEW_REMAINING_ISSUES.md)

---

## نظرة عامة | Overview

هذه الخطة تغطي إصلاح **28 مشكلة أمنية متبقية** (8 حرجة + 13 عالية + 7 متوسطة) مقسمة إلى **5 مراحل** مرتبة حسب الأولوية والتبعيات. كل مرحلة مستقلة عن التالية ويمكن اختبارها بشكل منفصل.

This plan covers fixing **28 remaining security issues** (8 CRITICAL + 13 HIGH + 7 MEDIUM) organized into **5 phases** ordered by priority and dependencies. Each phase is independently testable.

---

## مخطط التبعيات | Dependency Graph

```
المرحلة 1: حقن الأوامر + اجتياز المسار (مستقلة — لا تبعيات)
Phase 1: Command Injection + Path Traversal (Independent — no deps)
├── C-01: frontend_diagnostics.py (ESLint runner)
├── C-02: frontend_diagnostics.py (Biome runner)
├── C-07: market_prices/tracker.py (path traversal)
└── C-08: geofencing/engine.py (division by zero)

المرحلة 2: التشفير والمصادقة (تبعيات داخلية بين الملفات)
Phase 2: Crypto & Auth (internal file deps)
├── C-03: auth/twofa_service.py ← يتطلب تحديث verify_backup_code()
│   └── H-10: auth/twofa_service.py (race condition — same file)
└── H-07: ai/knowledge/serialization.py (yaml.safe_dump)
    └── M-03: (same file — JSON export fallback)

المرحلة 3: SSRF + حماية الشبكة (تبعيات مع scrapers فرعية)
Phase 3: SSRF + Network Protection (deps with child scrapers)
├── C-04: scraping/scrapers/base.py ← الفئة الأساسية
│   └── H-11: (same file — rate limiting)
└── H-02: cache/redis_sentinel.py (password leak)
    └── M-07: (same file — URL in stats)

المرحلة 4: عزل المستأجرين (أكبر مرحلة — 9 ملفات مترابطة)
Phase 4: Tenant Isolation (largest phase — 9 interrelated files)
├── مجموعة المزامنة | Sync Group:
│   ├── C-06: mobile_sync/queue.py
│   └── H-05: mobile_sync/resolver.py (depends on C-06)
├── مجموعة الجغرافيا | Geo Group:
│   ├── H-03: field_boundaries/sharing.py
│   └── H-04: geofencing/engine.py
├── مجموعة الأعمال | Business Group:
│   ├── C-05: cooperatives/resource_pool.py (race + tenant)
│   ├── H-06: batch_operations/executor.py
│   ├── H-12: equipment_maintenance/predictor.py
│   └── H-13: middleware/input_sanitizer.py
└── مجموعة التعلم | Learning Group:
    └── learning_marketplace/education_platform.py

المرحلة 5: تحسينات متنوعة (مستقلة)
Phase 5: Misc Improvements (independent)
├── H-01: lowcode/engine.py (ReDoS)
├── H-08: harvest_quality/pricing.py (div/0)
├── H-09: crop_insurance/risk_assessment.py (div/0)
├── M-01: auth/jwt_handler.py (multi-algorithm)
├── M-02: soil_sensors/adapters.py (info leak)
├── M-04: traceability/qr_generator.py (URL validation)
├── M-05: lowcode/engine.py (CSRF)
└── M-06: security/config.py (YAML loading)
```

---

## المرحلة 1: حقن الأوامر واجتياز المسار
## Phase 1: Command Injection & Path Traversal

**الأولوية**: حرجة — خطر تنفيذ أوامر عشوائية
**المدة المتوقعة**: ملف واحد + 2 ملفات مستقلة
**عدد الملفات**: 3
**التبعيات الخارجية**: لا توجد

### 1.1 — C-01 + C-02: حقن أوامر في frontend_diagnostics.py

**الملف**: `shared/ai/auto_fix/frontend_diagnostics.py`
**الأسطر المتأثرة**: 118-121 (ESLint), 215-220 (Biome)
**الملفات المستوردة منه**:
- `shared/ai/auto_fix/__init__.py`
- `apps/services/code-fix-agent/src/agent/code_fix_agent.py`
- `tests/unit/ai/test_auto_fix.py`
- `tests/smoke/test_fixops_smoke.py`

**أفضل طريقة للإصلاح**:
```python
# بدلاً من:
cmd = f"npx eslint {path} --format json {fix_flag}".strip()
result = subprocess.run(cmd.split(), ...)

# استخدم قائمة وسائط مباشرة:
cmd = ["npx", "eslint", str(path), "--format", "json"]
if self.config.auto_fix:
    cmd.append("--fix")
result = subprocess.run(cmd, ...)

# نفس النمط لـ Biome:
cmd = ["npx", "@biomejs/biome", "check", str(path), "--reporter", "json"]
if self.config.auto_fix:
    cmd.append("--write")
result = subprocess.run(cmd, ...)
```

**اختبار التحقق**: تمرير مسار يحتوي على `; rm -rf /` والتأكد من فشله بأمان.

### 1.2 — C-07: اجتياز المسار في tracker.py

**الملف**: `shared/market_prices/tracker.py`
**الأسطر المتأثرة**: 52-58 (PriceStorage.__init__), 65 (save_price)
**الملفات المستوردة منه**: لا يوجد استيراد مباشر خارج الوحدة

**أفضل طريقة للإصلاح**:
```python
import tempfile

class PriceStorage:
    def __init__(self, storage_path: str | None = None):
        _default = os.path.join(tempfile.gettempdir(), "sahool_market_prices")
        resolved = Path(storage_path or os.getenv("MARKET_PRICES_STORAGE_PATH", _default)).resolve()
        _allowed = (tempfile.gettempdir(), "/var/lib/sahool")
        if not any(str(resolved).startswith(p) for p in _allowed):
            raise ValueError(f"storage_path must be under {_allowed}")
        self.storage_path = resolved

    async def save_price(self, price: CropPrice) -> None:
        # تعقيم market_id لمنع اجتياز المسار
        safe_id = re.sub(r"[^a-zA-Z0-9_-]", "", price.market_id)
        file_path = self.storage_path / f"prices_{safe_id}.jsonl"
```

### 1.3 — C-08: قسمة على صفر في engine.py

**الملف**: `shared/geofencing/engine.py`
**الأسطر المتأثرة**: 69-72 (point_in_polygon)

**أفضل طريقة للإصلاح**:
```python
lat_intersect = p1_lat  # قيمة افتراضية عندما يكون الخط عمودي
if abs(p2_lng - p1_lng) > 1e-10:
    lat_intersect = (lng - p1_lng) * (p2_lat - p1_lat) / (p2_lng - p1_lng) + p1_lat
```

---

## المرحلة 2: التشفير والمصادقة
## Phase 2: Cryptography & Authentication

**الأولوية**: حرجة — ضعف في تخزين بيانات المصادقة
**عدد الملفات**: 2
**التبعيات**: C-03 ← H-10 (نفس الملف), H-07 ← M-03 (نفس الملف)

### 2.1 — C-03 + H-10: تشفير أكواد النسخ الاحتياطي

**الملف**: `shared/auth/twofa_service.py`
**الأسطر المتأثرة**: 196-212 (hash_backup_code), 242-283 (verify + race)
**الملفات المتأثرة**:
- `shared/auth/twofa_api.py` — يستدعي `hash_backup_code()` و `verify_backup_code()`
- `shared/auth/auth_api.py` — يستورد خدمة 2FA
- `tests/unit/shared/test_twofa_service.py`

**أفضل طريقة للإصلاح**:

```python
import bcrypt

def hash_backup_code(self, code: str) -> str:
    """Hash a backup code with bcrypt for secure storage."""
    clean_code = code.replace("-", "").strip()
    return bcrypt.hashpw(clean_code.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_backup_code(self, code: str, stored_hash: str) -> bool:
    """Verify a backup code against its bcrypt hash."""
    clean_code = code.replace("-", "").strip()
    # دعم الترحيل: تحقق من النوع القديم (sha256 hex = 64 chars) والجديد (bcrypt)
    if len(stored_hash) == 64:
        import hashlib
        return hashlib.sha256(clean_code.encode()).hexdigest() == stored_hash
    return bcrypt.checkpw(clean_code.encode(), stored_hash.encode())
```

**إصلاح سباق الشروط (H-10)**:
```python
async def verify_backup_code_with_remaining(
    self, code: str, hashed_codes: list[str]
) -> tuple[bool, list[str]]:
    # استخدام قفل asyncio لمنع الاستخدام المتزامن
    async with self._backup_code_lock:
        clean_code = code.replace("-", "").strip()
        for i, stored_hash in enumerate(hashed_codes):
            if self.verify_backup_code(clean_code, stored_hash):
                remaining = hashed_codes[:i] + hashed_codes[i + 1:]
                return True, remaining
        return False, hashed_codes
```

**تبعية**: إضافة `bcrypt` إلى `requirements/auth.txt` إن لم يكن موجوداً.
**ترحيل**: الأكواد القديمة (SHA256) ستُقبل مؤقتاً عبر فحص الطول (64 chars = SHA256 hex).

### 2.2 — H-07 + M-03: YAML serialization

**الملف**: `shared/ai/knowledge/serialization.py`
**الأسطر**: 110-116

**أفضل طريقة للإصلاح**:
```python
# بدلاً من yaml.dump()
yaml.safe_dump(data, stream, default_flow_style=False, allow_unicode=True)
```

---

## المرحلة 3: SSRF وحماية الشبكة
## Phase 3: SSRF & Network Protection

**الأولوية**: حرجة/عالية — إمكانية الوصول لخدمات داخلية
**عدد الملفات**: 2
**التبعيات**: C-04 ← H-11 (نفس الملف), H-02 ← M-07 (نفس الملف)

### 3.1 — C-04 + H-11: SSRF في base scraper

**الملف**: `shared/scraping/scrapers/base.py`
**الأسطر**: 276-317 (navigate), RateLimiter class
**المتأثرون**: جميع scrapers الفرعية (market, weather, etc.)

**أفضل طريقة للإصلاح**:
```python
import ipaddress
import socket
from urllib.parse import urlparse

_BLOCKED_CIDRS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]

def _validate_url(self, url: str) -> None:
    """Validate URL to prevent SSRF attacks."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Unsupported URL scheme: {parsed.scheme}")
    if not parsed.hostname:
        raise ValueError("URL must have a hostname")

    # Resolve hostname and check against blocked networks
    try:
        for info in socket.getaddrinfo(parsed.hostname, None):
            addr = ipaddress.ip_address(info[4][0])
            for cidr in _BLOCKED_CIDRS:
                if addr in cidr:
                    raise ValueError(
                        f"URL resolves to blocked network: {cidr}"
                    )
    except socket.gaierror:
        raise ValueError(f"Cannot resolve hostname: {parsed.hostname}")

async def navigate(self, url: str, **kwargs) -> None:
    self._validate_url(url)  # ← إضافة هذا السطر
    # ... بقية الكود الحالي
```

### 3.2 — H-02 + M-07: تسريب كلمة مرور Redis

**الملف**: `shared/cache/redis_sentinel.py`
**السطر**: 564

**أفضل طريقة للإصلاح**:
```python
from urllib.parse import urlparse, urlunparse

def _safe_url(url: str) -> str:
    """Remove credentials from Redis URL for logging."""
    parsed = urlparse(url)
    if parsed.password:
        safe = parsed._replace(
            netloc=f"***:***@{parsed.hostname}:{parsed.port or 6379}"
        )
        return urlunparse(safe)
    return url
```

---

## المرحلة 4: عزل المستأجرين
## Phase 4: Tenant Isolation

**الأولوية**: حرجة/عالية — خطر تسرب بيانات بين المستأجرين
**عدد الملفات**: 9
**التبعيات**: مجموعات مترابطة (انظر المخطط أعلاه)

### النمط المشترك للإصلاح | Common Fix Pattern

جميع ملفات عزل المستأجرين تتبع نفس النمط:

```python
# 1. التحقق من وجود tenant_id
if not tenant_id:
    raise ValueError("tenant_id is required")

# 2. تصفية جميع الاستعلامات بـ tenant_id
items = [i for i in self._items.values() if i.tenant_id == self.tenant_id]

# 3. التحقق من الملكية قبل التعديل
if item.tenant_id != self.tenant_id:
    raise ForbiddenException("Cannot access resource from another tenant")
```

### 4.1 — مجموعة المزامنة (C-06 + H-05)

**الملفات**:
- `shared/mobile_sync/queue.py` — إضافة تحقق إلزامي من tenant_id
- `shared/mobile_sync/resolver.py` — تحقق من تطابق tenant_id مع الجلسة

**ترتيب الإصلاح**: queue.py أولاً (C-06) ثم resolver.py (H-05)

### 4.2 — مجموعة الجغرافيا (H-03 + H-04)

**الملفات**:
- `shared/field_boundaries/sharing.py` — إضافة tenant_id لجميع دوال المشاركة
- `shared/geofencing/engine.py` — تصفية المناطق بـ tenant_id

### 4.3 — مجموعة الأعمال (C-05 + H-06 + H-12 + H-13)

**الملفات**:
- `shared/cooperatives/resource_pool.py` — قفل ذري + tenant check
- `shared/batch_operations/executor.py` — tenant validation في execute()
- `shared/equipment_maintenance/predictor.py` — tenant filtering
- `shared/middleware/input_sanitizer.py` — تحذير log عند عدم تطابق tenant_id

### 4.4 — مجموعة التعلم

**الملف**: `shared/learning_marketplace/education_platform.py`
- إضافة `tenant_id` إلى `DigitalCertificate`, `LearningModule`, `LearningPath`

---

## المرحلة 5: تحسينات متنوعة
## Phase 5: Miscellaneous Improvements

**الأولوية**: عالية/متوسطة
**عدد الملفات**: 8
**التبعيات**: كل إصلاح مستقل

| # | الملف | الإصلاح | النهج |
|---|-------|---------|-------|
| H-01 | `shared/lowcode/engine.py:197` | ReDoS | `re.compile(pattern)` داخل `try/except` مع timeout + حد أقصى لطول النمط (256 char) |
| H-08 | `shared/harvest_quality/pricing.py:603` | div/0 | `if base_price > 1e-6:` بدلاً من `> 0` |
| H-09 | `shared/crop_insurance/risk_assessment.py:313,334` | div/0 | epsilon threshold `> 1e-6` |
| M-01 | `shared/auth/jwt_handler.py:250` | multi-algo | تقييد `algorithms=["HS256"]` فقط في decode_token_unsafe |
| M-02 | `shared/soil_sensors/adapters.py:81` | info leak | `logger.warning("Callback error", exc_info=True)` بدلاً من `print()` |
| M-04 | `shared/traceability/qr_generator.py:61` | URL valid | `urlparse(base_url).scheme in ("http", "https")` |
| M-05 | `shared/lowcode/engine.py` | CSRF | إضافة CSRF token validation في form handlers |
| M-06 | `shared/security/config.py` | YAML | التأكد من `yaml.safe_load()` في كل مكان |

---

## ملخص المراحل | Phase Summary

| المرحلة | الملفات | الحرجة | العالية | المتوسطة | التبعيات |
|---------|---------|--------|---------|----------|----------|
| 1: حقن الأوامر | 3 | 4 (C-01,02,07,08) | 0 | 0 | لا توجد |
| 2: التشفير | 2 | 1 (C-03) | 2 (H-07,H-10) | 1 (M-03) | داخل الملف |
| 3: SSRF | 2 | 1 (C-04) | 2 (H-02,H-11) | 1 (M-07) | داخل الملف |
| 4: المستأجرين | 9 | 2 (C-05,C-06) | 5 (H-03,04,05,06,12,13) | 0 | مجموعات |
| 5: متنوعة | 8 | 0 | 3 (H-01,08,09) | 5 | لا توجد |
| **الإجمالي** | **~20 ملف** | **8** | **13** | **7** | — |

---

## المشاكل المعمارية المستبعدة | Excluded Architectural Issues

هذه المشاكل **خارج نطاق** هذه الخطة لأنها تتطلب تغييرات معمارية كبيرة:

| # | المشكلة | السبب | التوصية |
|---|---------|-------|---------|
| A-01 | ملح تشفير ثابت | يتطلب ترحيل بيانات | ADR + migration plan |
| A-02 | decryptDeterministic | مرتبط بـ A-01 | نفس الخطة |
| A-03 | DDL f-strings | يتطلب إعادة هيكلة DB | Sprint مخصص |
| A-04 | Prompt injection | يتطلب guardrails معمارية | مشروع منفصل |
| A-05 | توقيع التدقيق | يتطلب PKI | بنية تحتية |
| A-06 | سلامة GlobalGAP | blockchain/Merkle | بحث + POC |
| A-07 | PII regex | يتطلب NER | تكامل NLP |

---

## المرحلة 6: إصلاحات AI/ML
## Phase 6: AI/ML-Specific Fixes (NEW — from AI/ML audit)

**الأولوية**: عالية — ثغرات SSRF وحقن في وحدات الذكاء الاصطناعي
**عدد الملفات**: 3
**التبعيات**: لا توجد — كل إصلاح مستقل

| # | الملف | الإصلاح | النهج |
|---|-------|---------|-------|
| AI-01 | `shared/ai/llm_provider.py:60-71` | SSRF — عدم فحص IPs الداخلية | إضافة فحص `ipaddress` للشبكات المحجوبة (RFC 1918, link-local, loopback) |
| AI-02 | `shared/mcp/server.py:244-252` | حقن اسم الأداة بدون تحقق | تحقق من `tool_name` ضد قائمة الأدوات المسجلة + تعقيم `arguments` |
| AI-03 | `shared/ai/auto_fix/diagnostics.py:185-191` | MD5 ضعيف للتخزين المؤقت | استبدال `hashlib.md5` بـ `hashlib.sha256` |

### 6.1 — AI-01: SSRF في LLM Provider

**الملف**: `shared/ai/llm_provider.py`
**الأسطر**: 60-71

**أفضل طريقة للإصلاح**:
```python
import ipaddress
import socket
from urllib.parse import urlparse

_BLOCKED_CIDRS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]

def _validate_base_url(url: str | None) -> str | None:
    if url is None:
        return None
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(...)
    if not parsed.hostname:
        raise ValueError(...)
    # Block private/internal IPs
    try:
        for info in socket.getaddrinfo(parsed.hostname, None):
            addr = ipaddress.ip_address(info[4][0])
            for cidr in _BLOCKED_CIDRS:
                if addr in cidr:
                    raise ValueError(f"LLM base_url resolves to blocked network: {cidr}")
    except socket.gaierror:
        pass  # Allow unresolvable hostnames (may resolve at runtime)
    return url
```

### 6.2 — AI-02: MCP Tool Injection

**الملف**: `shared/mcp/server.py`
**الأسطر**: 244-252

**أفضل طريقة للإصلاح**:
```python
async def handle_tools_call(self, params: dict[str, Any]) -> dict[str, Any]:
    tool_name = params.get("name", "").strip()
    arguments = params.get("arguments", {})
    if not tool_name:
        raise ValueError("Tool name is required")
    # Validate against registered tools
    registered = {t["name"] for t in self.tools.get_tool_definitions()}
    if tool_name not in registered:
        raise ValueError(f"Unknown tool: {tool_name}")
    result = await self.tools.invoke_tool(tool_name, arguments)
```

### 6.3 — AI-03: MD5 → SHA-256

**الملف**: `shared/ai/auto_fix/diagnostics.py`
**السطر**: 189

```python
return hashlib.sha256(f.read()).hexdigest()
```

---

## ملخص المراحل المحدّث | Updated Phase Summary

| المرحلة | الملفات | الحرجة | العالية | المتوسطة | التبعيات |
|---------|---------|--------|---------|----------|----------|
| 1: حقن الأوامر | 3 | 4 (C-01,02,07,08) | 0 | 0 | لا توجد |
| 2: التشفير | 2 | 1 (C-03) | 2 (H-07,H-10) | 1 (M-03) | داخل الملف |
| 3: SSRF | 2 | 1 (C-04) | 2 (H-02,H-11) | 1 (M-07) | داخل الملف |
| 4: المستأجرين | 9 | 2 (C-05,C-06) | 5 (H-03..13) | 0 | مجموعات |
| 5: متنوعة | 8 | 0 | 3 (H-01,08,09) | 5 | لا توجد |
| 6: AI/ML | 3 | 0 | 3 (AI-01..03) | 0 | لا توجد |
| **الإجمالي** | **~27 ملف** | **8** | **15** | **7** | — |

---

## اختبارات التحقق | Verification Tests

لكل مرحلة، يجب إضافة اختبارات في `tests/unit/shared/test_security_fixes.py`:

```python
# المرحلة 1
def test_eslint_runner_rejects_path_injection(): ...
def test_biome_runner_rejects_path_injection(): ...
def test_price_storage_rejects_path_traversal(): ...
def test_point_in_polygon_handles_vertical_line(): ...

# المرحلة 2
def test_backup_code_uses_bcrypt(): ...
def test_backup_code_legacy_sha256_migration(): ...
def test_yaml_export_uses_safe_dump(): ...

# المرحلة 3
def test_scraper_blocks_internal_urls(): ...
def test_scraper_blocks_metadata_endpoint(): ...
def test_redis_url_hides_password(): ...

# المرحلة 4
def test_sync_queue_requires_tenant_id(): ...
def test_resource_booking_validates_tenant(): ...
def test_batch_operation_filters_by_tenant(): ...

# المرحلة 5
def test_regex_pattern_rejects_redos(): ...
def test_harvest_pricing_handles_near_zero(): ...

# المرحلة 6
def test_llm_provider_blocks_internal_urls(): ...
def test_mcp_rejects_unknown_tool(): ...
def test_diagnostics_uses_sha256(): ...
```

---

_آخر تحديث: 2026-03-21_
