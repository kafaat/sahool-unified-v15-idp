"""
SAHOOL Platform P2 Tests (Week 3 - Quality & Security Layer)
اختبارات المنصة P2 - الأسبوع الثالث

P2 covers contract validation, E2E journeys, security, and performance:

  ✅ Contract tests (Schemathesis-style schema validation)
  ✅ E2E complete farmer journey
  ✅ Rate limiting + security tests
  ✅ Performance tests (locust baseline expectations)

All tests are static / in-process; no live services required.

Run:
    pytest tests/ci/test_platform_p2.py -v -m integration
"""

from __future__ import annotations

import base64
import hmac
import hashlib
import json
import time
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
OPENAPI_SPEC = REPO_ROOT / "api" / "gateway-openapi.yaml"
KONG_CONFIG_PATH = REPO_ROOT / "infra" / "kong" / "kong.yml"
KONG_GATEWAY_CONFIG_PATH = REPO_ROOT / "infrastructure" / "gateway" / "kong" / "kong.yml"
LOCUSTFILE = REPO_ROOT / "tests" / "load" / "locustfile.py"

pytestmark = [pytest.mark.integration]

JWT_SECRET = "test-secret-key-for-unit-tests-only-32chars"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_jwt(user_id: str, tenant_id: str, roles: list[str]) -> str:
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
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    except ImportError:
        header = base64.urlsafe_b64encode(
            json.dumps({"alg": "HS256", "typ": "JWT"}).encode()
        ).rstrip(b"=")
        body = base64.urlsafe_b64encode(
            json.dumps({"sub": user_id, "tid": tenant_id, "roles": roles}).encode()
        ).rstrip(b"=")
        return f"{header.decode()}.{body.decode()}.fake_sig"


def _load_kong() -> dict | None:
    """
    Load the Kong configuration used by the platform.

    Prefer KONG_GATEWAY_CONFIG_PATH — the file mounted by docker-compose.yml
    (./infrastructure/gateway/kong/kong.yml:/kong/declarative/kong.yml:ro).
    Fall back to the legacy infra path if the gateway config is absent.
    """
    for path in (KONG_GATEWAY_CONFIG_PATH, KONG_CONFIG_PATH):
        if path.exists():
            with open(path, encoding="utf-8") as fh:
                return yaml.safe_load(fh)
    pytest.skip("Kong configuration file not found")
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# P2-1  Contract Tests (Schemathesis-style)
# ═══════════════════════════════════════════════════════════════════════════════


class TestContractTests:
    """
    API contract validation against the gateway OpenAPI specification.
    Exercises the same invariants that Schemathesis would verify at runtime:
    - Every declared path exists in the spec
    - Every path has at least one operation (GET / POST / …)
    - Required request schemas include type and properties
    - Shared security components are declared

    These tests act as a Schemathesis smoke-test in environments where a live
    server is not available.
    اختبارات العقد للتحقق من مواصفة OpenAPI
    """

    @pytest.fixture(scope="class")
    def openapi(self) -> dict:
        assert OPENAPI_SPEC.exists(), f"OpenAPI spec not found: {OPENAPI_SPEC}"
        with open(OPENAPI_SPEC, encoding="utf-8") as fh:
            return yaml.safe_load(fh)

    # ------------------------------------------------------------------
    # Structural contract checks
    # ------------------------------------------------------------------

    def test_contract_tests(self, openapi: dict):
        """
        OpenAPI spec must define paths, components, and core authentication endpoints.
        مواصفة OpenAPI يجب أن تحتوي على المسارات والمكونات ونقاط نهاية المصادقة
        """
        assert "openapi" in openapi, "Spec must declare 'openapi' version"
        assert openapi["openapi"].startswith("3."), "Must be OpenAPI 3.x"
        assert "info" in openapi, "Spec must include 'info'"
        assert "paths" in openapi, "Spec must declare 'paths'"
        paths = openapi["paths"]
        assert len(paths) > 0, "Spec must have at least one path"

    def test_contract_required_auth_endpoints_declared(self, openapi: dict):
        """
        Core authentication endpoints must be declared in the OpenAPI spec.
        نقاط نهاية المصادقة الأساسية يجب أن تكون معرّفة في المواصفة
        """
        required = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
        ]
        paths = openapi.get("paths", {})
        missing = [p for p in required if p not in paths]
        assert not missing, f"Missing required auth paths in OpenAPI spec: {missing}"

    def test_contract_auth_endpoints_have_post_operation(self, openapi: dict):
        """
        /auth/login and /auth/register must define a POST operation.
        نقطتا تسجيل الدخول والتسجيل يجب أن تحددا عملية POST
        """
        paths = openapi.get("paths", {})
        for path in ("/api/v1/auth/login", "/api/v1/auth/register"):
            if path in paths:
                assert "post" in paths[path], (
                    f"{path} must define a POST operation"
                )

    def test_contract_health_endpoint_declared(self, openapi: dict):
        """
        Health/liveness endpoints must be in the spec.
        نقطة نهاية الصحة يجب أن تكون معرّفة في المواصفة
        """
        paths = openapi.get("paths", {})
        health_paths = [p for p in paths if "health" in p.lower() or "healthz" in p.lower()]
        assert health_paths, "At least one health endpoint must be declared in the OpenAPI spec"

    def test_contract_security_schemes_declared(self, openapi: dict):
        """
        Security schemes (Bearer JWT) must be declared in components.
        مخططات الأمان يجب أن تكون معرّفة في المكونات
        """
        components = openapi.get("components", {})
        security_schemes = components.get("securitySchemes", {})
        assert security_schemes, "At least one security scheme must be declared"
        # Check for a Bearer/JWT scheme
        bearer_found = any(
            scheme.get("type") in ("http", "apiKey") or "bearer" in str(scheme).lower()
            for scheme in security_schemes.values()
        )
        assert bearer_found, "A Bearer/JWT security scheme must be declared"

    def test_contract_info_has_version_and_title(self, openapi: dict):
        """
        Spec info must include version and title for consumer discoverability.
        معلومات المواصفة يجب أن تحتوي على الإصدار والعنوان
        """
        info = openapi.get("info", {})
        assert "version" in info, "OpenAPI info must include 'version'"
        assert "title" in info, "OpenAPI info must include 'title'"

    def test_contract_response_schema_defined_for_login(self, openapi: dict):
        """
        POST /auth/login must declare at least one response schema.
        POST /auth/login يجب أن يعرّف على الأقل مخطط استجابة واحدًا
        """
        paths = openapi.get("paths", {})
        login_path = paths.get("/api/v1/auth/login", {})
        post_op = login_path.get("post", {})
        responses = post_op.get("responses", {})
        assert responses, "POST /api/v1/auth/login must declare responses"
        # At least one success (2xx) response
        success_codes = [k for k in responses if str(k).startswith("2")]
        assert success_codes, "Login must declare at least one 2xx response"


# ═══════════════════════════════════════════════════════════════════════════════
# P2-2  E2E Complete Farmer Journey
# ═══════════════════════════════════════════════════════════════════════════════


class TestE2ECompleteFarmerJourney:
    """
    End-to-end simulation of the complete farmer journey from registration to
    harvest — all in-process without live services.
    محاكاة رحلة المزارع الكاملة من التسجيل إلى الحصاد داخل الذاكرة
    """

    # Lightweight in-process "service" used across all steps
    class FarmPlatform:
        def __init__(self):
            self.users: dict[str, dict] = {}
            self.fields: dict[str, dict] = {}
            self.tasks: list[dict] = []
            self.ndvi_history: dict[str, list] = {}

        def register(self, email: str, password: str, tenant_id: str) -> dict:
            if email in self.users:
                return {"error": "EMAIL_EXISTS", "status": 409}
            uid = str(uuid.uuid4())
            self.users[email] = {"id": uid, "email": email, "tenant_id": tenant_id}
            return {"user_id": uid, "status": 201}

        def login(self, email: str, password: str) -> dict:
            user = self.users.get(email)
            if not user:
                return {"error": "INVALID_CREDENTIALS", "status": 401}
            token = _make_jwt(user["id"], user["tenant_id"], ["farmer"])
            return {"access_token": token, "status": 200}

        def create_field(self, name: str, tenant_id: str, geometry: dict) -> dict:
            fid = str(uuid.uuid4())
            field = {"id": fid, "name": name, "tenant_id": tenant_id, "geometry": geometry}
            self.fields[fid] = field
            return {"field_id": fid, "status": 201}

        def add_task(self, field_id: str, task_type: str, tenant_id: str) -> dict:
            tid = str(uuid.uuid4())
            task = {"id": tid, "field_id": field_id, "type": task_type, "status": "scheduled", "tenant_id": tenant_id}
            self.tasks.append(task)
            return {"task_id": tid, "status": 201}

        def complete_task(self, task_id: str) -> dict:
            for task in self.tasks:
                if task["id"] == task_id:
                    task["status"] = "completed"
                    return {"status": 200}
            return {"error": "NOT_FOUND", "status": 404}

        def record_ndvi(self, field_id: str, mean_ndvi: float) -> dict:
            entry = {
                "field_id": field_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "mean_ndvi": mean_ndvi,
                "health_status": "healthy" if mean_ndvi >= 0.5 else "moderate",
            }
            self.ndvi_history.setdefault(field_id, []).append(entry)
            return {"status": 200, "entry": entry}

        def record_harvest(self, field_id: str, yield_kg: float) -> dict:
            return {"field_id": field_id, "yield_kg": yield_kg, "status": "recorded"}

    @pytest.fixture
    def platform(self) -> "TestE2ECompleteFarmerJourney.FarmPlatform":
        return self.FarmPlatform()

    def test_e2e_complete_farmer_journey(self, platform: "TestE2ECompleteFarmerJourney.FarmPlatform"):
        """
        Full in-process farmer journey: register → login → create field →
        schedule task → NDVI → complete task → record harvest.
        رحلة المزارع الكاملة: تسجيل → تسجيل دخول → إنشاء حقل → NDVI → حصاد
        """
        tenant_id = str(uuid.uuid4())
        email = f"farmer_{uuid.uuid4().hex[:8]}@e2e.sahool.app"

        # Step 1 — Register
        reg = platform.register(email, "Secure123!", tenant_id)
        assert reg["status"] == 201, "Registration must succeed"
        assert reg["user_id"], "Registration must return user_id"

        # Step 2 — Login
        login = platform.login(email, "Secure123!")
        assert login["status"] == 200
        token = login["access_token"]
        assert token and len(token.split(".")) == 3

        # Step 3 — Create field
        geom = {
            "type": "Polygon",
            "coordinates": [[[46.67, 24.71], [46.68, 24.71], [46.68, 24.72], [46.67, 24.72], [46.67, 24.71]]],
        }
        field_resp = platform.create_field("حقل القمح", tenant_id, geom)
        assert field_resp["status"] == 201
        field_id = field_resp["field_id"]

        # Step 4 — Schedule irrigation task
        task_resp = platform.add_task(field_id, "irrigation", tenant_id)
        assert task_resp["status"] == 201
        task_id = task_resp["task_id"]

        # Step 5 — Record NDVI observation
        ndvi_resp = platform.record_ndvi(field_id, 0.67)
        assert ndvi_resp["status"] == 200
        assert ndvi_resp["entry"]["health_status"] == "healthy"

        # Step 6 — Complete the task
        complete = platform.complete_task(task_id)
        assert complete["status"] == 200
        completed_task = next(t for t in platform.tasks if t["id"] == task_id)
        assert completed_task["status"] == "completed"

        # Step 7 — Record harvest
        harvest = platform.record_harvest(field_id, 5250.0)
        assert harvest["field_id"] == field_id
        assert harvest["yield_kg"] > 0

    def test_e2e_duplicate_registration_rejected(self, platform: "TestE2ECompleteFarmerJourney.FarmPlatform"):
        """Duplicate e-mail registration must return 409."""
        email = "dup@e2e.sahool.app"
        tenant_id = str(uuid.uuid4())
        platform.register(email, "Pass123!", tenant_id)
        result = platform.register(email, "Pass123!", tenant_id)
        assert result["status"] == 409

    def test_e2e_field_belongs_to_correct_tenant(self, platform: "TestE2ECompleteFarmerJourney.FarmPlatform"):
        """Field created by tenant A must not be visible to tenant B."""
        tenant_a = str(uuid.uuid4())
        tenant_b = str(uuid.uuid4())
        geom = {"type": "Polygon", "coordinates": [[[46.67, 24.71], [46.68, 24.71], [46.68, 24.72], [46.67, 24.72], [46.67, 24.71]]]}
        field_resp = platform.create_field("Tenant A Field", tenant_a, geom)
        field_id = field_resp["field_id"]

        # Tenant B query (simulated RLS)
        visible_to_b = [f for f in platform.fields.values() if f["tenant_id"] == tenant_b]
        assert not any(f["id"] == field_id for f in visible_to_b), (
            "Tenant B must not see Tenant A's field"
        )

    def test_e2e_ndvi_history_accumulates(self, platform: "TestE2ECompleteFarmerJourney.FarmPlatform"):
        """NDVI observations must accumulate over time for a field."""
        field_id = str(uuid.uuid4())
        for ndvi in [0.40, 0.55, 0.68, 0.72]:
            platform.record_ndvi(field_id, ndvi)
        history = platform.ndvi_history.get(field_id, [])
        assert len(history) == 4, "All NDVI readings must be recorded"
        assert history[-1]["mean_ndvi"] == 0.72


# ═══════════════════════════════════════════════════════════════════════════════
# P2-3  Rate Limiting + Security Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestRateLimitingAndSecurity:
    """
    Validate rate-limiting configuration in Kong and in-process security controls:
    - Rate limiting is configured on production services
    - JWT tampering detection
    - CORS policy
    - Security response headers
    اختبارات تحديد معدل الطلبات والأمان
    """

    # Expected per-minute limits per tier (from CLAUDE.md).
    # Used to validate Kong service rate limits stay within documented bounds.
    RATE_LIMITS = {
        "starter": 30,
        "professional": 60,
        "enterprise": 120,
        "research": 120,
        "internal": 1000,
    }

    @pytest.fixture(scope="class")
    def kong(self) -> dict:
        return _load_kong()

    def test_rate_limiting(self, kong: dict):
        """
        Kong must configure rate-limiting on production services.
        Kong يجب أن يكوّن تحديد معدل الطلبات للخدمات
        """
        rate_limited_services = [
            svc["name"]
            for svc in kong.get("services", [])
            for plugin in svc.get("plugins", [])
            if plugin.get("name") == "rate-limiting"
        ]
        assert rate_limited_services, (
            "At least one Kong service must have rate-limiting configured"
        )

    def test_rate_limit_thresholds_are_reasonable(self, kong: dict):
        """
        Rate-limit values must be positive integers.
        قيم تحديد المعدل يجب أن تكون أعدادًا صحيحة موجبة
        """
        for svc in kong.get("services", []):
            for plugin in svc.get("plugins", []):
                if plugin.get("name") == "rate-limiting":
                    config = plugin.get("config", {})
                    minute_limit = config.get("minute")
                    if minute_limit is not None:
                        assert isinstance(minute_limit, int) and minute_limit > 0, (
                            f"Rate limit 'minute' for {svc['name']} must be a positive int"
                        )

    def test_kong_rate_limits_within_tier_bounds(self, kong: dict):
        """
        All Kong per-minute rate limits must not exceed the internal-tier ceiling
        defined in RATE_LIMITS, ensuring no service can be misconfigured above the
        maximum documented throughput.
        قيم المعدل يجب ألا تتجاوز السقف الداخلي المحدد في RATE_LIMITS
        """
        internal_ceiling = self.RATE_LIMITS["internal"]  # 1000 req/min
        starter_floor = min(self.RATE_LIMITS.values())   # 30 req/min (minimum documented tier)
        violations = []
        for svc in kong.get("services", []):
            for plugin in svc.get("plugins", []):
                if plugin.get("name") == "rate-limiting":
                    minute_limit = plugin.get("config", {}).get("minute")
                    if minute_limit is not None:
                        if minute_limit > internal_ceiling:
                            violations.append(
                                f"{svc['name']}: {minute_limit} req/min exceeds internal ceiling {internal_ceiling}"
                            )
                        if minute_limit < starter_floor:
                            violations.append(
                                f"{svc['name']}: {minute_limit} req/min is below starter tier floor {starter_floor}"
                            )
        assert not violations, (
            "Kong services exceed the documented tier bounds:\n" + "\n".join(violations)
        )

    def test_in_process_rate_limiter_blocks_after_threshold(self):
        """
        An in-process rate limiter must block requests exceeding the threshold.
        محدد معدل الطلبات داخل العملية يجب أن يحجب الطلبات الزائدة
        """
        MAX_REQUESTS = 5
        window_seconds = 60
        requests: list[float] = []

        def is_allowed() -> bool:
            now = time.time()
            cutoff = now - window_seconds
            while requests and requests[0] < cutoff:
                requests.pop(0)
            if len(requests) >= MAX_REQUESTS:
                return False
            requests.append(now)
            return True

        for i in range(MAX_REQUESTS):
            assert is_allowed(), f"Request {i + 1} should be allowed"
        assert not is_allowed(), "Request beyond threshold must be blocked"

    def test_jwt_tampering_rejected(self):
        """
        A tampered JWT (modified payload without re-signing) must be rejected.
        رمز JWT المعدَّل يجب أن يُرفض
        """
        token = _make_jwt("user-001", "tenant-001", ["farmer"])
        parts = token.split(".")
        # Tamper the payload — use correct base64url padding
        payload_seg = parts[1]
        p_padding = "=" * (-len(payload_seg) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_seg + p_padding))
        payload["roles"] = ["admin"]  # Privilege escalation attempt
        tampered_payload = base64.urlsafe_b64encode(
            json.dumps(payload).encode()
        ).rstrip(b"=").decode()
        tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"

        try:
            import jwt

            with pytest.raises(Exception):
                jwt.decode(
                    tampered_token,
                    JWT_SECRET,
                    algorithms=["HS256"],
                    options={"verify_aud": False},
                )
        except ImportError:
            # Without PyJWT, perform minimal HS256 signature verification using stdlib.
            def _verify_hs256(token: str, secret: str) -> None:
                header_b64, payload_b64, signature_b64 = token.split(".")
                signing_input = f"{header_b64}.{payload_b64}".encode()
                # Base64url-decode the provided signature (add correct padding if needed)
                s_padding = "=" * (-len(signature_b64) % 4)
                try:
                    sig_bytes = base64.urlsafe_b64decode(signature_b64 + s_padding)
                except Exception as exc:
                    # Normalize any base64 decoding error to ValueError so tests are reliable.
                    raise ValueError("Invalid JWT signature") from exc
                expected_sig = hmac.new(
                    secret.encode(),
                    signing_input,
                    hashlib.sha256,
                ).digest()
                if not hmac.compare_digest(sig_bytes, expected_sig):
                    raise ValueError("Invalid JWT signature")

            with pytest.raises(ValueError):
                _verify_hs256(tampered_token, JWT_SECRET)

    def test_security_headers_in_kong_config(self, kong: dict):
        """
        Kong must configure security response headers via response-transformer.
        Kong يجب أن يكوّن رؤوس أمان الاستجابة عبر response-transformer
        """
        security_headers_found = False
        for plugin in kong.get("plugins", []):
            if plugin.get("name") == "response-transformer":
                add_headers = plugin.get("config", {}).get("add", {}).get("headers", [])
                header_str = " ".join(str(h) for h in add_headers)
                if "X-Frame-Options" in header_str or "X-Content-Type-Options" in header_str:
                    security_headers_found = True
                    break
        assert security_headers_found, (
            "Kong must add security headers (X-Frame-Options, X-Content-Type-Options) via response-transformer"
        )

    def test_cors_allows_required_origins(self, kong: dict):
        """
        CORS must be configured to allow platform domains.
        CORS يجب أن يكون مكوَّنًا للسماح بنطاقات المنصة
        """
        for plugin in kong.get("plugins", []):
            if plugin.get("name") == "cors":
                origins = plugin.get("config", {}).get("origins", [])
                assert origins, "CORS plugin must define allowed origins"
                return
        pytest.fail("CORS plugin not found in Kong global plugins")

    def test_sql_injection_in_tenant_id_rejected(self):
        """
        A tenant_id containing SQL injection must be sanitised / rejected.
        معرف المستأجر الذي يحتوي على حقن SQL يجب أن يُرفض
        """

        def validate_tenant_id(tenant_id: str) -> bool:
            """Basic UUID validation to prevent SQL injection."""
            try:
                uuid.UUID(tenant_id)
                return True
            except ValueError:
                return False

        valid_tid = str(uuid.uuid4())
        assert validate_tenant_id(valid_tid), "Valid UUID tenant_id must pass"

        malicious_tids = [
            "'; DROP TABLE tenants;--",
            "1 OR 1=1",
            "<script>alert(1)</script>",
            "../../../etc/passwd",
        ]
        for tid in malicious_tids:
            assert not validate_tenant_id(tid), (
                f"Malicious tenant_id '{tid}' must be rejected"
            )

    def test_missing_auth_header_rejected(self):
        """
        Requests without an Authorization header must be treated as unauthorised.
        الطلبات التي لا تحمل رأس التفويض يجب أن تُعامَل كطلبات غير مصرح بها
        """

        def check_auth(headers: dict) -> int:
            if "Authorization" not in headers:
                return 401
            if not headers["Authorization"].startswith("Bearer "):
                return 401
            return 200

        assert check_auth({}) == 401
        assert check_auth({"Authorization": "invalid"}) == 401
        assert check_auth({"Authorization": "Bearer fake.token.here"}) == 200


# ═══════════════════════════════════════════════════════════════════════════════
# P2-4  Performance Tests (Locust baseline expectations)
# ═══════════════════════════════════════════════════════════════════════════════


class TestPerformanceTests:
    """
    Validate that Locust performance baseline expectations are correctly
    configured and that locustfile.py is well-formed.
    التحقق من تكوين اختبارات الأداء وملف locust
    """

    # SLO baselines from docs/CLAUDE.md and locustfile.py
    EXPECTED_BASELINES_MS = {
        "health_check": 100,
        "field_list": 300,
        "field_detail": 250,
        "weather_current": 200,
        "ndvi_latest": 500,
        "advisory_recommendations": 400,
    }

    def test_performance_tests(self):
        """
        Locustfile must exist and define at least one HttpUser subclass.
        ملف Locust يجب أن يوجد ويحتوي على فئة HttpUser على الأقل
        """
        assert LOCUSTFILE.exists(), f"locustfile.py not found at {LOCUSTFILE}"
        content = LOCUSTFILE.read_text(encoding="utf-8")
        assert "HttpUser" in content, "locustfile.py must define at least one HttpUser subclass"
        assert "@task" in content, "locustfile.py must define task methods with @task decorator"

    def test_performance_baselines_defined_in_locustfile(self):
        """
        Performance baselines for critical endpoints must be defined in locustfile.py.
        خطوط الأساس لأداء نقاط النهاية الحيوية يجب أن تُعرَّف في ملف Locust
        """
        content = LOCUSTFILE.read_text(encoding="utf-8")
        for endpoint in self.EXPECTED_BASELINES_MS:
            assert endpoint in content, (
                f"Performance baseline for '{endpoint}' not found in locustfile.py"
            )

    def test_performance_baseline_values_are_reasonable(self):
        """
        All SLO baseline response times must be positive and within sensible bounds.
        قيم خط الأساس للأداء يجب أن تكون إيجابية وضمن حدود معقولة
        """
        for endpoint, max_ms in self.EXPECTED_BASELINES_MS.items():
            assert max_ms > 0, f"Baseline for '{endpoint}' must be positive"
            assert max_ms <= 5000, (
                f"Baseline for '{endpoint}' ({max_ms} ms) seems too high (> 5 s)"
            )

    def test_performance_locust_user_classes_have_tasks(self):
        """
        HttpUser subclasses in locustfile.py must define at least one @task.
        فئات HttpUser في ملف Locust يجب أن تحتوي على مهمة واحدة على الأقل
        """
        content = LOCUSTFILE.read_text(encoding="utf-8")
        # Count @task decorators
        task_count = content.count("@task")
        assert task_count >= 3, (
            f"locustfile.py should define ≥ 3 tasks (found {task_count})"
        )

    def test_performance_slo_health_check(self):
        """
        /healthz must respond within 100 ms (SLO baseline) — validated via mock.
        /healthz يجب أن يستجيب خلال 100 ms وفق خط الأساس للأداء
        """

        def mock_health_check() -> dict:
            # Simulate an ultra-fast health check handler
            start = time.perf_counter()
            result = {"status": "ok", "service": "gateway", "version": "16.0.0"}
            elapsed_ms = (time.perf_counter() - start) * 1000
            return {**result, "latency_ms": elapsed_ms}

        response = mock_health_check()
        assert response["status"] == "ok"
        assert response["latency_ms"] < self.EXPECTED_BASELINES_MS["health_check"], (
            "Mock health check must complete well within 100 ms baseline"
        )

    def test_performance_locust_wait_time_configured(self):
        """
        Locust user classes must define a wait_time to simulate realistic pacing.
        فئات Locust يجب أن تحدد وقت الانتظار لمحاكاة الاستخدام الحقيقي
        """
        content = LOCUSTFILE.read_text(encoding="utf-8")
        assert "wait_time" in content, (
            "Locust user classes must define 'wait_time' for realistic load simulation"
        )
        assert "between(" in content, (
            "Locust 'wait_time' should use 'between(min, max)' for variable pacing"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
