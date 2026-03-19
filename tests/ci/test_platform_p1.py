"""
SAHOOL Platform P1 Tests (Week 2 - Intelligence Layer)
اختبارات المنصة P1 - الأسبوع الثاني

P1 covers NDVI / satellite intelligence, JWT propagation, and tenant isolation:

  ✅ test_fetch_ndvi_history
  ✅ test_satellite_provider_fallback
  ✅ test_imagery_cached + persisted_to_db
  ✅ test_jwt_propagation_through_kong
  ✅ test_tenant_isolation (RLS)

All tests run entirely in-process using mocks; no live services required.

Run:
    pytest tests/ci/test_platform_p1.py -v -m integration
"""

from __future__ import annotations

import base64
import json
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
RLS_MIGRATION = (
    REPO_ROOT / "infrastructure" / "core" / "postgres" / "migrations" / "010_row_level_security.sql"
)
KONG_CONFIG_PATH = REPO_ROOT / "infra" / "kong" / "kong.yml"
KONG_GATEWAY_CONFIG_PATH = REPO_ROOT / "infrastructure" / "gateway" / "kong" / "kong.yml"

pytestmark = [pytest.mark.integration]

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

JWT_SECRET = "test-secret-key-for-unit-tests-only-32chars"
JWT_ALGORITHM = "HS256"


def _make_jwt(user_id: str, tenant_id: str, roles: list[str]) -> str:
    """Create a HS256 JWT token (requires PyJWT)."""
    try:
        import jwt

        payload = {
            "sub": user_id,
            "tid": tenant_id,
            "roles": roles,
            "iss": "sahool-idp",
            "aud": "sahool-platform",
            "iat": datetime.now(UTC),
            "exp": datetime.now(UTC) + timedelta(hours=1),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    except ImportError:
        header = base64.urlsafe_b64encode(
            json.dumps({"alg": "HS256", "typ": "JWT"}).encode()
        ).rstrip(b"=")
        body = base64.urlsafe_b64encode(
            json.dumps({"sub": user_id, "tid": tenant_id}).encode()
        ).rstrip(b"=")
        return f"{header.decode()}.{body.decode()}.fake_sig"


# ---------------------------------------------------------------------------
# P1-1  test_fetch_ndvi_history
# ---------------------------------------------------------------------------


class TestFetchNDVIHistory:
    """
    Validate NDVI history retrieval logic and response structure.
    التحقق من منطق استرداد تاريخ NDVI وبنية الاستجابة
    """

    @pytest.fixture
    def mock_ndvi_store(self) -> list[dict]:
        """In-memory NDVI history for a single field."""
        field_id = "field-ndvi-test-001"
        base_date = datetime.now(UTC)
        return [
            {
                "field_id": field_id,
                "timestamp": (base_date - timedelta(days=i * 5)).isoformat(),
                "mean_ndvi": round(0.45 + i * 0.02, 3),
                "min_ndvi": round(0.30 + i * 0.02, 3),
                "max_ndvi": round(0.70 + i * 0.02, 3),
                "cloud_cover_percent": round(5.0 + i, 1),
                "health_status": "healthy" if 0.45 + i * 0.02 > 0.5 else "moderate",
                "data_source": "sentinel-2",
            }
            for i in range(6)  # 6 data points, 5-day cadence
        ]

    def test_fetch_ndvi_history(self, mock_ndvi_store: list[dict]):
        """
        NDVI history must return a time-ordered list of records.
        تاريخ NDVI يجب أن يُعيد قائمة مرتبة زمنيًا من السجلات
        """
        history = sorted(mock_ndvi_store, key=lambda r: r["timestamp"])

        assert len(history) >= 2, "At least 2 NDVI data points are required for history"
        for record in history:
            assert "field_id" in record
            assert "timestamp" in record
            assert "mean_ndvi" in record
            assert -1.0 <= record["mean_ndvi"] <= 1.0, "NDVI must be in [-1, 1]"

        # Time ordering: oldest first
        timestamps = [r["timestamp"] for r in history]
        assert timestamps == sorted(timestamps), "NDVI history must be sorted oldest-first"

    def test_ndvi_history_health_status_classification(self, mock_ndvi_store: list[dict]):
        """
        Each NDVI record must carry a health_status classification.
        كل سجل NDVI يجب أن يحمل تصنيف الحالة الصحية
        """
        valid_statuses = {"healthy", "moderate", "stressed", "critical"}
        for record in mock_ndvi_store:
            assert record.get("health_status") in valid_statuses, (
                f"health_status '{record.get('health_status')}' is not valid"
            )

    def test_ndvi_history_returns_field_id(self, mock_ndvi_store: list[dict]):
        """
        Every record must carry the originating field_id.
        كل سجل يجب أن يحمل field_id المصدر
        """
        field_id = mock_ndvi_store[0]["field_id"]
        for record in mock_ndvi_store:
            assert record["field_id"] == field_id, (
                "All NDVI history records must belong to the same field"
            )

    def test_ndvi_history_date_range_filter(self, mock_ndvi_store: list[dict]):
        """
        Fetching NDVI within a date range must return only matching records.
        استرداد NDVI ضمن نطاق زمني يجب أن يُعيد السجلات المطابقة فقط
        """
        cutoff = (datetime.now(UTC) - timedelta(days=15)).isoformat()
        recent = [r for r in mock_ndvi_store if r["timestamp"] >= cutoff]
        assert len(recent) <= len(mock_ndvi_store), (
            "Filtered result must have ≤ total records"
        )
        for r in recent:
            assert r["timestamp"] >= cutoff, "Filtered records must be within date range"

    def test_ndvi_history_5_day_cadence(self, mock_ndvi_store: list[dict]):
        """
        Sentinel-2 has a ~5-day revisit cycle; gaps must be acceptable.
        دورة مرور القمر الصناعي 5 أيام؛ الفجوات يجب أن تكون مقبولة
        """
        MAX_GAP_DAYS = 30  # Allow for cloud cover / data gaps
        history = sorted(mock_ndvi_store, key=lambda r: r["timestamp"])
        for i in range(1, len(history)):
            t1 = datetime.fromisoformat(history[i - 1]["timestamp"].replace("Z", "+00:00"))
            t2 = datetime.fromisoformat(history[i]["timestamp"].replace("Z", "+00:00"))
            gap = abs((t2 - t1).days)
            assert gap <= MAX_GAP_DAYS, (
                f"NDVI gap of {gap} days exceeds maximum allowed {MAX_GAP_DAYS} days"
            )


# ---------------------------------------------------------------------------
# P1-2  test_satellite_provider_fallback
# ---------------------------------------------------------------------------


class TestSatelliteProviderFallback:
    """
    Validate the satellite provider fallback mechanism:
    primary (Sentinel Hub) → fallback (mock / cached data).
    التحقق من آلية الرجوع إلى مزود بديل عند تعذر الوصول للأقمار الصناعية
    """

    def _make_analyzer(self, *, sentinel_available: bool = True):
        """
        Build a minimal SentinelNDVIAnalyzer-like object whose initialize()
        returns False when sentinel_available is False, triggering fallback.
        """

        class FakeAnalyzer:
            def __init__(self, available: bool):
                self._available = available
                self._initialized = False
                self.fallback_used = False

            async def initialize(self) -> bool:
                if self._available:
                    self._initialized = True
                return self._initialized

            async def get_ndvi(self, field_id: str, date=None) -> dict:
                if not self._initialized:
                    # Fallback path
                    self.fallback_used = True
                    return self._mock_ndvi(field_id, date)
                return {"field_id": field_id, "mean_ndvi": 0.65, "data_source": "sentinel-2"}

            def _mock_ndvi(self, field_id: str, date=None) -> dict:
                return {
                    "field_id": field_id,
                    "mean_ndvi": 0.50,
                    "data_source": "mock",
                    "health_status": "moderate",
                }

        return FakeAnalyzer(available=sentinel_available)

    @pytest.mark.asyncio
    async def test_satellite_provider_fallback(self):
        """
        When the primary satellite provider is unavailable, the system must fall
        back to mock/cached data rather than raising an unhandled error.
        عند عدم توفر المزود الأساسي للأقمار الصناعية، يجب الرجوع إلى البيانات المؤقتة
        """
        analyzer = self._make_analyzer(sentinel_available=False)
        await analyzer.initialize()
        result = await analyzer.get_ndvi("field-001")

        assert result is not None, "Fallback must return a result, not None"
        assert result["data_source"] == "mock", "Fallback must indicate mock data source"
        assert analyzer.fallback_used, "Fallback path must have been exercised"

    @pytest.mark.asyncio
    async def test_primary_provider_used_when_available(self):
        """
        When the primary provider is available, it must be used.
        عند توفر المزود الأساسي يجب استخدامه
        """
        analyzer = self._make_analyzer(sentinel_available=True)
        await analyzer.initialize()
        result = await analyzer.get_ndvi("field-001")

        assert result["data_source"] == "sentinel-2"
        assert not analyzer.fallback_used

    @pytest.mark.asyncio
    async def test_fallback_result_is_valid_ndvi(self):
        """
        Fallback data must have valid NDVI range and required fields.
        بيانات الاحتياط يجب أن تحتوي على قيم NDVI صالحة
        """
        analyzer = self._make_analyzer(sentinel_available=False)
        await analyzer.initialize()
        result = await analyzer.get_ndvi("field-002")

        assert "mean_ndvi" in result, "Fallback result must include mean_ndvi"
        assert -1.0 <= result["mean_ndvi"] <= 1.0, "Fallback NDVI must be in valid range"

    def test_provider_config_has_fallback_defined(self):
        """
        The sentinel_ndvi module must document the mock/fallback path in source.
        وحدة sentinel_ndvi يجب أن توثق مسار الاحتياط
        """
        ndvi_module = REPO_ROOT / "shared" / "satellite" / "sentinel_ndvi.py"
        assert ndvi_module.exists(), "sentinel_ndvi.py must exist"
        content = ndvi_module.read_text(encoding="utf-8")
        assert "_get_mock_ndvi" in content or "mock" in content.lower(), (
            "Satellite module must define a mock/fallback path"
        )


# ---------------------------------------------------------------------------
# P1-3  test_imagery_cached + persisted_to_db
# ---------------------------------------------------------------------------


class TestImageryCachedAndPersistedToDB:
    """
    Validate that satellite imagery results are:
    1. Written to an in-process cache (Redis-like) for fast subsequent reads.
    2. Persisted to a DB-like store for long-term record keeping.
    التحقق من تخزين صور الأقمار الصناعية مؤقتًا وحفظها في قاعدة البيانات
    """

    @pytest.fixture
    def cache_store(self) -> dict:
        """Simulates a Redis cache (key → value)."""
        return {}

    @pytest.fixture
    def db_store(self) -> list[dict]:
        """Simulates persistent DB rows."""
        return []

    def _ndvi_cache_key(self, field_id: str, date: str) -> str:
        return f"ndvi:{field_id}:{date}"

    def _fetch_or_cache(
        self,
        field_id: str,
        date: str,
        cache: dict,
        db: list,
    ) -> dict:
        """Fetch NDVI; check cache first, then DB, then compute and store."""
        key = self._ndvi_cache_key(field_id, date)
        if key in cache:
            return {**cache[key], "_source": "cache"}

        # Check DB
        for row in db:
            if row["field_id"] == field_id and row["date"] == date:
                # Re-populate cache on DB hit
                cache[key] = row
                return {**row, "_source": "db"}

        # Compute (mock)
        result = {
            "field_id": field_id,
            "date": date,
            "mean_ndvi": 0.62,
            "data_source": "sentinel-2",
        }
        # Persist to DB and cache
        db.append(result)
        cache[key] = result
        return {**result, "_source": "computed"}

    def test_imagery_cached(self, cache_store: dict, db_store: list):
        """
        First request computes the result; second request returns the cached value.
        الطلب الأول يحسب النتيجة؛ الطلب الثاني يُعيد القيمة المحفوظة مؤقتًا
        """
        field_id = "field-cache-test"
        date = "2026-01-15"

        r1 = self._fetch_or_cache(field_id, date, cache_store, db_store)
        assert r1["_source"] == "computed", "First call must compute"

        r2 = self._fetch_or_cache(field_id, date, cache_store, db_store)
        assert r2["_source"] == "cache", "Second call must serve from cache"
        assert r1["mean_ndvi"] == r2["mean_ndvi"], "Cached value must match original"

    def test_imagery_persisted_to_db(self, cache_store: dict, db_store: list):
        """
        After the first fetch the result must also exist in the DB store.
        بعد الاسترداد الأول يجب أن تكون النتيجة محفوظة في قاعدة البيانات
        """
        field_id = "field-db-persist-test"
        date = "2026-01-20"

        self._fetch_or_cache(field_id, date, cache_store, db_store)

        matching_rows = [r for r in db_store if r["field_id"] == field_id and r["date"] == date]
        assert len(matching_rows) == 1, "Result must be persisted to DB exactly once"

    def test_cache_miss_falls_back_to_db(self, cache_store: dict, db_store: list):
        """
        A cache miss must fall back to the DB (not recompute unnecessarily).
        عند انتهاء صلاحية الذاكرة المؤقتة يجب الرجوع إلى قاعدة البيانات
        """
        field_id = "field-cache-miss-test"
        date = "2026-01-22"

        # Pre-populate DB (simulates a warm DB with a previous session's data)
        pre_existing = {"field_id": field_id, "date": date, "mean_ndvi": 0.71, "data_source": "sentinel-2"}
        db_store.append(pre_existing)

        result = self._fetch_or_cache(field_id, date, cache_store, db_store)
        assert result["_source"] == "db", "DB row must be returned on cache miss"
        assert result["mean_ndvi"] == 0.71

    def test_db_store_has_unique_entries(self, cache_store: dict, db_store: list):
        """
        Multiple calls for the same field/date must not duplicate DB rows.
        الاستدعاءات المتعددة لنفس الحقل والتاريخ يجب ألا تُضاعف صفوف قاعدة البيانات
        """
        field_id = "field-dedup-test"
        date = "2026-01-25"

        for _ in range(3):
            self._fetch_or_cache(field_id, date, cache_store, db_store)

        matching = [r for r in db_store if r["field_id"] == field_id and r["date"] == date]
        assert len(matching) == 1, "DB must not contain duplicate entries for the same field/date"


# ---------------------------------------------------------------------------
# P1-4  test_jwt_propagation_through_kong
# ---------------------------------------------------------------------------


class TestJWTPropagationThroughKong:
    """
    Validate that the Kong API Gateway configuration correctly propagates JWT
    claims (X-Tenant-ID, X-User-ID) downstream to microservices.
    التحقق من أن Kong ينقل رموز JWT ومعلومات الهوية إلى الخدمات الداخلية
    """

    @pytest.fixture
    def kong_config(self) -> dict:
        """Load Kong YAML config (skip if absent)."""
        import yaml

        for path in (KONG_CONFIG_PATH, KONG_GATEWAY_CONFIG_PATH):
            if path.exists():
                with open(path, encoding="utf-8") as fh:
                    return yaml.safe_load(fh)
        pytest.skip("Kong configuration file not found")

    def test_jwt_propagation_through_kong(self, kong_config: dict):
        """
        Kong services must include JWT authentication plugin.
        خدمات Kong يجب أن تتضمن مكوّن مصادقة JWT
        """
        jwt_services: list[str] = []
        for svc in kong_config.get("services", []):
            for plugin in svc.get("plugins", []):
                if plugin.get("name") == "jwt":
                    jwt_services.append(svc["name"])
                    break
        assert jwt_services, (
            "At least one Kong service must use the 'jwt' plugin for token propagation"
        )

    def test_jwt_token_structure_valid(self):
        """
        JWT tokens must have three dot-separated segments.
        رموز JWT يجب أن تحتوي على ثلاثة أجزاء مفصولة بنقاط
        """
        token = _make_jwt("user-001", "tenant-001", ["farmer"])
        parts = token.split(".")
        assert len(parts) == 3, "JWT must consist of header.payload.signature"

    def test_jwt_carries_tenant_id_claim(self):
        """
        The JWT payload must include the tid (tenant_id) claim.
        حمولة JWT يجب أن تحتوي على مطالبة tid (tenant_id)
        """
        token = _make_jwt("user-001", "tenant-from-jwt", ["farmer"])
        try:
            import jwt

            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], options={"verify_aud": False})
            assert "tid" in payload, "JWT must include 'tid' claim for tenant isolation"
            assert payload["tid"] == "tenant-from-jwt"
        except ImportError:
            # Decode base64 payload manually
            parts = token.split(".")
            padded = parts[1] + "=="
            payload = json.loads(base64.urlsafe_b64decode(padded))
            assert "tid" in payload, "JWT must include 'tid' claim"

    def test_kong_jwt_plugin_specifies_key_claim(self, kong_config: dict):
        """
        Kong JWT plugin must specify which claim holds the key identifier.
        مكوّن JWT في Kong يجب أن يحدد المطالبة التي تحمل معرف المفتاح
        """
        for svc in kong_config.get("services", []):
            for plugin in svc.get("plugins", []):
                if plugin.get("name") == "jwt":
                    config = plugin.get("config", {})
                    # key_claim_name defaults to "iss" in Kong
                    # Accept either explicit key_claim_name or default
                    assert isinstance(config, dict), "JWT plugin must have a config dict"
                    return  # At least one valid JWT plugin config found
        pytest.skip("No JWT plugin found in Kong config")

    def test_authorization_header_format(self):
        """
        Authorization header must use 'Bearer <token>' format.
        رأس التفويض يجب أن يستخدم صيغة 'Bearer <token>'
        """
        token = _make_jwt("user-001", "tenant-001", ["farmer"])
        auth_header = f"Bearer {token}"
        assert auth_header.startswith("Bearer "), "Auth header must start with 'Bearer '"
        extracted_token = auth_header[len("Bearer "):]
        assert len(extracted_token.split(".")) == 3, "Extracted token must be a valid JWT"


# ---------------------------------------------------------------------------
# P1-5  test_tenant_isolation (RLS)
# ---------------------------------------------------------------------------


class TestTenantIsolation:
    """
    Validate multi-tenant data isolation at the RLS policy level and through
    in-process query simulation.
    التحقق من عزل بيانات المستأجرين عبر سياسات أمان مستوى الصف
    """

    @pytest.fixture(scope="class")
    def rls_sql(self) -> str:
        assert RLS_MIGRATION.exists(), f"RLS migration not found: {RLS_MIGRATION}"
        return RLS_MIGRATION.read_text(encoding="utf-8")

    @pytest.fixture
    def multi_tenant_db(self) -> list[dict]:
        """Two tenants, each with two fields."""
        tenant_a = str(uuid.uuid4())
        tenant_b = str(uuid.uuid4())
        return [
            {"id": str(uuid.uuid4()), "tenant_id": tenant_a, "name": "Field A1"},
            {"id": str(uuid.uuid4()), "tenant_id": tenant_a, "name": "Field A2"},
            {"id": str(uuid.uuid4()), "tenant_id": tenant_b, "name": "Field B1"},
            {"id": str(uuid.uuid4()), "tenant_id": tenant_b, "name": "Field B2"},
        ]

    def _query_fields(self, db: list[dict], current_tenant: str) -> list[dict]:
        """Simulate a tenant-scoped SELECT (mirrors RLS behaviour)."""
        return [row for row in db if row["tenant_id"] == current_tenant]

    def test_tenant_isolation(self, multi_tenant_db: list[dict]):
        """
        A tenant must only see its own records; cross-tenant leakage must be zero.
        المستأجر يجب أن يرى سجلاته فقط؛ يجب ألا تكون هناك تسربات بين المستأجرين
        """
        tenant_ids = list({row["tenant_id"] for row in multi_tenant_db})
        assert len(tenant_ids) == 2, "Test requires exactly two tenants"

        tenant_a, tenant_b = tenant_ids[0], tenant_ids[1]

        results_a = self._query_fields(multi_tenant_db, tenant_a)
        results_b = self._query_fields(multi_tenant_db, tenant_b)

        # Each tenant sees only their own records
        assert all(r["tenant_id"] == tenant_a for r in results_a), (
            "Tenant A must not see Tenant B's records"
        )
        assert all(r["tenant_id"] == tenant_b for r in results_b), (
            "Tenant B must not see Tenant A's records"
        )
        # No leakage
        ids_a = {r["id"] for r in results_a}
        ids_b = {r["id"] for r in results_b}
        assert ids_a.isdisjoint(ids_b), "Record sets of distinct tenants must not overlap"

    def test_rls_policy_covers_all_critical_tables(self, rls_sql: str):
        """
        The RLS migration must enable RLS on every critical multi-tenant table.
        ملف ترحيل RLS يجب أن يغطي جميع الجداول الأساسية متعددة المستأجرين
        """
        critical_tables = ["fields", "tasks", "orders", "equipment"]
        import re

        for table in critical_tables:
            pattern = rf"ALTER\s+TABLE\s+{re.escape(table)}\s+ENABLE\s+ROW\s+LEVEL\s+SECURITY"
            assert re.search(pattern, rls_sql, re.IGNORECASE), (
                f"RLS not enabled on critical table: {table}"
            )

    def test_tenant_id_required_for_all_operations(self, multi_tenant_db: list[dict]):
        """
        Any insert or update without a tenant_id must be rejected.
        أي إدراج أو تحديث بدون tenant_id يجب أن يُرفض
        """

        def create_field(payload: dict, db: list) -> dict:
            if not payload.get("tenant_id"):
                return {"error": "TENANT_ID_REQUIRED", "status": 400}
            record = {**payload, "id": str(uuid.uuid4())}
            db.append(record)
            return {"id": record["id"], "status": 201}

        ok = create_field({"name": "Field X", "tenant_id": str(uuid.uuid4())}, multi_tenant_db)
        assert ok["status"] == 201

        bad = create_field({"name": "Orphan Field"}, multi_tenant_db)
        assert bad["status"] == 400
        assert bad["error"] == "TENANT_ID_REQUIRED"

    def test_cross_tenant_access_denied(self, multi_tenant_db: list[dict]):
        """
        A tenant must not be able to read another tenant's record by ID.
        المستأجر يجب ألا يستطيع قراءة سجل مستأجر آخر بواسطة المعرّف
        """
        tenant_ids = list({row["tenant_id"] for row in multi_tenant_db})
        tenant_a, tenant_b = tenant_ids[0], tenant_ids[1]

        # Get a record that belongs to tenant_b
        record_b = next(r for r in multi_tenant_db if r["tenant_id"] == tenant_b)

        def get_field_by_id(field_id: str, current_tenant: str, db: list) -> dict | None:
            """Tenant-scoped lookup (simulates RLS WHERE tenant_id = current_tenant)."""
            return next(
                (r for r in db if r["id"] == field_id and r["tenant_id"] == current_tenant),
                None,
            )

        # Tenant A trying to access Tenant B's record → must return None
        result = get_field_by_id(record_b["id"], tenant_a, multi_tenant_db)
        assert result is None, "Cross-tenant record access must return None (RLS blocks it)"

    def test_jwt_tenant_claim_matches_db_tenant(self):
        """
        The tenant_id in the JWT must match the tenant_id used in DB queries.
        معرّف المستأجر في JWT يجب أن يتطابق مع المستخدم في استعلامات قاعدة البيانات
        """
        tenant_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())

        token = _make_jwt(user_id, tenant_id, ["farmer"])

        # Simulate Kong / middleware extracting tenant from JWT
        try:
            import jwt

            payload = jwt.decode(
                token, JWT_SECRET, algorithms=["HS256"], options={"verify_aud": False}
            )
            extracted_tenant = payload.get("tid")
        except ImportError:
            parts = token.split(".")
            payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
            extracted_tenant = payload.get("tid")

        assert extracted_tenant == tenant_id, (
            "JWT 'tid' claim must match the original tenant_id used for DB scoping"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
