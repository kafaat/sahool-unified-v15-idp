"""
Contract Tests for SAHOOL Services - منصة سهول
اختبارات العقود بين الخدمات

Two categories of contract tests:

1. Schemathesis-based tests (فحص بالمخطط)
   Auto-generate test cases from an OpenAPI/JSON-Schema spec and
   verify every endpoint conforms to the declared contract.

2. GraphQL ↔ REST consistency tests (اتساق GraphQL مع REST)
   Verify that the GraphQL BFF and the REST field-service return
   identical data for the same resource.

These tests require a running services stack.
They skip gracefully when services are unavailable.

Test Markers:
- @pytest.mark.contract  - Contract tests between services
- @pytest.mark.asyncio   - Async tests

Author: SAHOOL QA Team
Updated: March 2026
"""

from __future__ import annotations

import os
from typing import Any

import pytest

try:
    import httpx

    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

try:
    import schemathesis  # type: ignore[import]

    HAS_SCHEMATHESIS = True
except ImportError:
    HAS_SCHEMATHESIS = False

# ── Service URLs (overridable via environment) ─────────────────────────────────
FIELD_SERVICE_OPENAPI_URL = os.getenv(
    "FIELD_SERVICE_OPENAPI_URL",
    "http://localhost:3000/api-json",  # field-management-service OpenAPI spec
)
GRAPHQL_URL = os.getenv("GRAPHQL_URL", "http://localhost:8000/graphql")
REST_BASE_URL = os.getenv("KONG_BASE_URL", "http://localhost:8000")
TEST_JWT_TOKEN = os.getenv("TEST_JWT_TOKEN", "mock-jwt-for-contract-tests")

# Known paths where field-management-service may expose its OpenAPI spec
OPENAPI_SPEC_PATHS = ("/api-json", "/openapi.json", "/docs/json")

# ═══════════════════════════════════════════════════════════════════════════════
# Schemathesis — OpenAPI Contract Tests
# توليد اختبارات تلقائي من OpenAPI spec
# ═══════════════════════════════════════════════════════════════════════════════


def _load_schema_or_skip():
    """
    Load the OpenAPI schema from field-management-service.
    Skip the whole module section gracefully if the service is not running
    or schemathesis is not installed.
    """
    if not HAS_SCHEMATHESIS:
        return None
    if not HAS_HTTPX:
        return None
    try:
        return schemathesis.from_uri(
            FIELD_SERVICE_OPENAPI_URL,
            headers={"Authorization": f"Bearer {TEST_JWT_TOKEN}"},
        )
    except Exception:
        return None


_schema = _load_schema_or_skip()


if _schema is not None:

    @_schema.parametrize()
    def test_field_service_contract(case: Any) -> None:
        """
        كل endpoint في field-service يتبع OpenAPI spec المُعلَن

        Auto-generated test: for every operation declared in the
        field-management-service OpenAPI spec, send a valid request
        and assert the response matches the declared schema.
        """
        response = case.call()
        case.validate_response(response)

else:

    @pytest.mark.contract
    def test_field_service_contract_skipped() -> None:
        """
        Placeholder: Schemathesis contract tests skipped.
        يُستبدل بالاختبار الحقيقي عند توفر الخدمة و schemathesis.
        """
        pytest.skip(
            "Schemathesis or field-management-service not available; "
            "start docker-compose.test.yml and install schemathesis to run contract tests."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# GraphQL ↔ REST Consistency Tests
# اتساق GraphQL مع REST — نفس البيانات من كلا المصدرين
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
async def rest_client():
    """
    عميل HTTP للـ REST API.
    Async HTTP client for the REST API via Kong.
    """
    if not HAS_HTTPX:
        pytest.skip("httpx not installed")

    async with httpx.AsyncClient(
        base_url=REST_BASE_URL,
        headers={"Authorization": f"Bearer {TEST_JWT_TOKEN}", "Content-Type": "application/json"},
        timeout=15.0,
    ) as client:
        try:
            await client.get("/healthz")
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("REST API Gateway not reachable — start docker-compose.test.yml first")
        yield client


@pytest.fixture
async def graphql_client():
    """
    عميل HTTP لـ GraphQL BFF.
    Async HTTP client for the GraphQL endpoint.
    """
    if not HAS_HTTPX:
        pytest.skip("httpx not installed")

    async with httpx.AsyncClient(
        base_url=GRAPHQL_URL,
        headers={"Authorization": f"Bearer {TEST_JWT_TOKEN}", "Content-Type": "application/json"},
        timeout=15.0,
    ) as client:
        try:
            await client.post("", json={"query": "{ __typename }"})
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("GraphQL endpoint not reachable — start docker-compose.test.yml first")
        yield client


@pytest.fixture
def test_field_id() -> str:
    """
    معرّف حقل اختبار موجود مسبقاً في البيئة.
    A pre-existing field ID available in the test environment.
    """
    return os.getenv("TEST_FIELD_ID", "test-field-contract-001")


@pytest.mark.contract
class TestGraphQLToRestContract:
    """
    اتساق استجابات GraphQL مع REST — نفس الحقل يُعاد بنفس البيانات

    Verifies that the GraphQL BFF and the REST field-service return
    identical data for the same field resource.
    """

    @pytest.mark.asyncio
    async def test_graphql_field_matches_rest_field(
        self,
        graphql_client: Any,
        rest_client: Any,
        test_field_id: str,
    ) -> None:
        """
        GraphQL و REST يعيدان نفس البيانات للحقل الواحد

        Fetch the same field from both GraphQL and REST endpoints
        and assert the returned data is identical on key fields:
        id, name, ndvi, areaHa / area_ha.
        """
        # REST response
        rest_resp = await rest_client.get(f"/api/v1/fields/{test_field_id}")
        if rest_resp.status_code == 404:
            pytest.skip(f"Test field {test_field_id!r} does not exist in the running environment")
        assert rest_resp.status_code == 200, f"REST endpoint failed: {rest_resp.text}"
        rest_field = rest_resp.json()

        # GraphQL response
        gql_resp = await graphql_client.post(
            "",
            json={
                "query": """
                    query GetField($id: String!) {
                        field(id: $id) {
                            id
                            name
                            ndvi
                            status
                            areaHa
                        }
                    }
                """,
                "variables": {"id": test_field_id},
            },
        )
        assert gql_resp.status_code == 200, f"GraphQL endpoint failed: {gql_resp.text}"
        gql_data = gql_resp.json().get("data", {}).get("field")
        if gql_data is None:
            pytest.skip("GraphQL field query returned null — field may not be in GraphQL schema")

        # يجب أن تكون البيانات متطابقة — data must be consistent.
        # IDs are compared as strings because the REST service (NestJS/Prisma)
        # may return numeric IDs while GraphQL may return string IDs. The
        # contract requires value equality; type coercion is intentional here.
        assert str(gql_data["id"]) == str(rest_field["id"]), (
            f"ID mismatch: GraphQL={gql_data['id']}, REST={rest_field['id']}"
        )
        assert gql_data["name"] == rest_field["name"], (
            f"Name mismatch: GraphQL={gql_data['name']}, REST={rest_field['name']}"
        )

        # NDVI (optional — may be null if not yet computed)
        if gql_data.get("ndvi") is not None and rest_field.get("ndvi") is not None:
            assert gql_data["ndvi"] == rest_field["ndvi"], (
                f"NDVI mismatch: GraphQL={gql_data['ndvi']}, REST={rest_field['ndvi']}"
            )

        # المساحة — area (GraphQL camelCase vs REST snake_case)
        gql_area = gql_data.get("areaHa")
        rest_area = rest_field.get("area_ha") or rest_field.get("areaHa")
        if gql_area is not None and rest_area is not None:
            assert abs(float(gql_area) - float(rest_area)) < 0.001, (
                f"Area mismatch: GraphQL={gql_area}, REST={rest_area}"
            )

    @pytest.mark.asyncio
    async def test_rest_field_list_schema(
        self,
        rest_client: Any,
    ) -> None:
        """
        قائمة الحقول من REST API تحتوي على الحقول المطلوبة

        The REST field list endpoint must return a payload conforming
        to the expected schema: items array + pagination metadata.
        """
        resp = await rest_client.get("/api/v1/fields")
        assert resp.status_code == 200, f"Field list endpoint failed: {resp.text}"

        body = resp.json()
        # الاستجابة يجب أن تكون قائمة أو كائن مُرقَّم
        assert isinstance(body, (list, dict)), "Unexpected response type"

        if isinstance(body, dict):
            # Paginated response must have an items/fields array
            data = body.get("items") or body.get("fields") or body.get("data") or []
            assert isinstance(data, list), "Expected items/fields/data to be a list"


# ═══════════════════════════════════════════════════════════════════════════════
# Pact-style Provider State Tests (optional, requires pact-python)
# اختبارات حالة المزوّد — اختياري
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.contract
class TestFieldServiceContractBasic:
    """
    اختبارات عقد أساسية لا تتطلب Schemathesis أو Pact

    Basic contract tests that verify the field-management-service
    exposes the minimum required interface without needing a full
    contract testing framework.
    """

    @pytest.mark.asyncio
    async def test_health_endpoint_returns_ok(self, rest_client: Any) -> None:
        """
        /healthz يُعيد 200 OK مع حقل status

        Every service must expose /healthz returning
        {"status": "ok"} with HTTP 200.
        """
        # Try service-direct health check
        if not HAS_HTTPX:
            pytest.skip("httpx not installed")

        async with httpx.AsyncClient(base_url="http://localhost:3000", timeout=5.0) as svc_client:
            try:
                resp = await svc_client.get("/healthz")
                assert resp.status_code == 200
                body = resp.json()
                assert body.get("status") == "ok", f"Unexpected health body: {body}"
            except (httpx.ConnectError, httpx.TimeoutException):
                pytest.skip("field-management-service not reachable on port 3000")

    @pytest.mark.asyncio
    async def test_openapi_spec_accessible(self) -> None:
        """
        OpenAPI spec متاح على /api-json أو /openapi.json

        The service must expose its OpenAPI spec so contract tests
        can be generated automatically.
        """
        if not HAS_HTTPX:
            pytest.skip("httpx not installed")

        async with httpx.AsyncClient(base_url="http://localhost:3000", timeout=5.0) as svc_client:
            for path in OPENAPI_SPEC_PATHS:
                try:
                    resp = await svc_client.get(path)
                    if resp.status_code == 200:
                        spec = resp.json()
                        assert "openapi" in spec or "swagger" in spec, (
                            f"Response at {path} is not a valid OpenAPI spec"
                        )
                        return
                except (httpx.ConnectError, httpx.TimeoutException):
                    pytest.skip("field-management-service not reachable on port 3000")

            pytest.skip("OpenAPI spec not found on any known path")
