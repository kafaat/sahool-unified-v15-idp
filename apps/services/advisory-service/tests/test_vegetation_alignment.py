"""Regression tests for advisory-service's alignment with
vegetation-analysis-service after PR #1704 shipped.

Pins four things:

  1. ``CropLoanVerificationEngine._fetch_ndvi_series`` calls the
     canonical vegetation endpoint (``/v1/timeseries/{field_id}``),
     not the legacy non-existent path that always returned 404.
  2. The NDVI response from vegetation is mapped into the shape
     ``_summarise_ndvi`` expects (``series`` key, not ``timeseries``).
  3. Both field-scoped advisory endpoints (``/advisory/comprehensive/
     {field_id}`` + ``/loans/crop-loan-verification/{field_id}``)
     invoke ``verify_field_owned_by_tenant`` — an AST pin so the gate
     can't silently be removed.
  4. The NDVI threshold constants in ``kb.nutrients`` match
     ``vegetation-analysis-service/src/multi_date.py::status_for_ndvi``
     — advisory's nutrient diagnosis and vegetation's health status
     must agree on "moderate" vs "good" for the same field.

Downstream-error tests (403/404/503 from vegetation) live alongside
the verification flow tests so the loan engine's graceful-degradation
contract stays honest.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

# =============================================================================
# Fix #1 — _fetch_ndvi_series endpoint path + response shape
# =============================================================================


@pytest.mark.asyncio
async def test_fetch_ndvi_series_hits_canonical_vegetation_endpoint():
    """Regression pin: the loan engine must call
    ``/v1/timeseries/{field_id}``, not the legacy
    ``/api/v1/vegetation/fields/{field_id}/ndvi/history`` which
    doesn't exist in vegetation-analysis-service and always 404s."""
    from src.loans.verification import CropLoanVerificationEngine

    engine = CropLoanVerificationEngine(
        field_management_url="http://fms:3000",
        vegetation_analysis_url="http://veg:8090",
        crop_intelligence_url="http://ci:8095",
    )

    captured: dict = {}

    async def fake_get(url, *, headers=None, params=None):
        captured["url"] = url
        captured["params"] = params
        m = MagicMock()
        m.status_code = 200
        m.json = MagicMock(
            return_value={
                "field_id": "f-1",
                "timeseries": [
                    {"date": "2026-01-01", "ndvi": 0.6, "ndwi": 0.2, "evi": 0.55, "cloud_cover": 5.0},
                    {"date": "2026-02-01", "ndvi": 0.62, "ndwi": 0.22, "evi": 0.58, "cloud_cover": 3.0},
                ],
                "data_source": "simulated",
                "period_days": 365,
            }
        )
        return m

    client = MagicMock(spec=httpx.AsyncClient)
    client.get = AsyncMock(side_effect=fake_get)

    result = await engine._fetch_ndvi_series(client, {"X-Tenant-Id": "t1"}, "f-1")

    assert captured["url"] == "http://veg:8090/v1/timeseries/f-1"
    assert captured["params"] == {"days": 365}
    # Response must be mapped from `timeseries` → `series` so the
    # existing `_summarise_ndvi` keeps working.
    assert result["_degraded"] is False
    assert "series" in result
    assert len(result["series"]) == 2
    assert result["series"][0]["ndvi"] == 0.6


@pytest.mark.asyncio
async def test_fetch_ndvi_series_marks_404_as_non_degraded_empty():
    """Vegetation's 404 for an unknown field should yield an empty
    result without degrading — the loan engine's own verdict logic
    downgrades when there's no NDVI evidence."""
    from src.loans.verification import CropLoanVerificationEngine

    engine = CropLoanVerificationEngine(
        field_management_url="http://fms",
        vegetation_analysis_url="http://veg",
        crop_intelligence_url="http://ci",
    )

    async def fake_get(url, *, headers=None, params=None):
        m = MagicMock()
        m.status_code = 404
        return m

    client = MagicMock(spec=httpx.AsyncClient)
    client.get = AsyncMock(side_effect=fake_get)

    result = await engine._fetch_ndvi_series(client, {}, "unknown-field")
    # `_safe_get` treats 404 as degraded=False, empty payload.
    assert result.get("_degraded") is False
    # No `series` key because there was no payload to map.
    assert "series" not in result


@pytest.mark.asyncio
async def test_fetch_ndvi_series_degrades_on_503():
    """A vegetation 503 (service unavailable) must NOT raise — it
    degrades the loan engine so the verdict falls back gracefully."""
    from src.loans.verification import CropLoanVerificationEngine

    engine = CropLoanVerificationEngine(
        field_management_url="http://fms",
        vegetation_analysis_url="http://veg",
        crop_intelligence_url="http://ci",
    )

    async def fake_get(url, *, headers=None, params=None):
        m = MagicMock()
        m.status_code = 503
        return m

    client = MagicMock(spec=httpx.AsyncClient)
    client.get = AsyncMock(side_effect=fake_get)

    result = await engine._fetch_ndvi_series(client, {}, "f-1")
    assert result.get("_degraded") is True
    assert result.get("_error") == "HTTP 503"


@pytest.mark.asyncio
async def test_fetch_ndvi_series_degrades_on_network_timeout():
    """httpx TimeoutException must degrade, not crash."""
    from src.loans.verification import CropLoanVerificationEngine

    engine = CropLoanVerificationEngine(
        field_management_url="http://fms",
        vegetation_analysis_url="http://veg",
        crop_intelligence_url="http://ci",
    )

    async def fake_get(url, *, headers=None, params=None):
        raise httpx.TimeoutException("timed out")

    client = MagicMock(spec=httpx.AsyncClient)
    client.get = AsyncMock(side_effect=fake_get)

    result = await engine._fetch_ndvi_series(client, {}, "f-1")
    assert result.get("_degraded") is True
    assert result.get("_error") == "timeout"


# =============================================================================
# Fix #2 — ownership gate on field-scoped advisory endpoints
# =============================================================================

_ADVISORY_MAIN = Path(__file__).parent.parent / "src" / "main.py"


def _handler_body(handler_name: str) -> str:
    src = _ADVISORY_MAIN.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == handler_name:
            return ast.get_source_segment(src, node) or ""
    pytest.fail(f"Handler {handler_name} not found in main.py")


@pytest.mark.parametrize(
    "handler",
    ["comprehensive_advisory", "verify_crop_loan"],
)
def test_field_scoped_handlers_call_ownership_verifier(handler: str):
    """Regression pin (Copilot audit round 1): both field-scoped
    advisory endpoints must call ``verify_field_owned_by_tenant``
    BEFORE running the downstream orchestrator / engine. Otherwise
    a valid JWT for tenant A can harvest data for tenant B's fields
    via advisory — downstream services enforce their own gates, but
    advisory has to refuse early as defense-in-depth."""
    body = _handler_body(handler)
    assert "verify_field_owned_by_tenant" in body, (
        f"{handler}: missing verify_field_owned_by_tenant call. Cross-tenant field_id access is possible without it."
    )


@pytest.mark.parametrize(
    "handler",
    ["comprehensive_advisory", "verify_crop_loan"],
)
def test_field_scoped_handlers_accept_request_for_bearer_forwarding(handler: str):
    """The ownership verifier needs the inbound Bearer JWT to prove
    identity to field-management-service. The handler must accept a
    ``request`` parameter for that forwarding."""
    src = _ADVISORY_MAIN.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == handler:
            arg_names = [a.arg for a in node.args.args]
            assert "request" in arg_names, (
                f"{handler}: missing `request: Request` parameter. "
                "Bearer JWT can't be forwarded to field-management-service."
            )
            return
    pytest.fail(f"Handler {handler} not found")


# =============================================================================
# Fix #2a — verify_field_owned_by_tenant helper behaviour
# =============================================================================


@pytest.mark.asyncio
async def test_ownership_verifier_raises_403_without_tenant(monkeypatch):
    from fastapi import HTTPException
    from src.field_ownership import verify_field_owned_by_tenant

    with pytest.raises(HTTPException) as exc:
        await verify_field_owned_by_tenant(tenant_id="", field_id="f-1")
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_ownership_verifier_raises_400_on_bogus_field_id():
    from fastapi import HTTPException
    from src.field_ownership import verify_field_owned_by_tenant

    with pytest.raises(HTTPException) as exc:
        await verify_field_owned_by_tenant(tenant_id="t1", field_id="")
    assert exc.value.status_code == 400

    with pytest.raises(HTTPException) as exc:
        await verify_field_owned_by_tenant(tenant_id="t1", field_id="a" * 200)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_ownership_verifier_raises_403_when_fms_says_403():
    from fastapi import HTTPException
    from src.field_ownership import verify_field_owned_by_tenant

    async def fake_get(url, *, headers=None):
        m = MagicMock()
        m.status_code = 403
        return m

    client = MagicMock(spec=httpx.AsyncClient)
    client.get = AsyncMock(side_effect=fake_get)

    with pytest.raises(HTTPException) as exc:
        await verify_field_owned_by_tenant(
            tenant_id="t1",
            field_id="field-1",
            http_client=client,
        )
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_ownership_verifier_raises_404_when_fms_says_404():
    from fastapi import HTTPException
    from src.field_ownership import verify_field_owned_by_tenant

    async def fake_get(url, *, headers=None):
        m = MagicMock()
        m.status_code = 404
        return m

    client = MagicMock(spec=httpx.AsyncClient)
    client.get = AsyncMock(side_effect=fake_get)

    with pytest.raises(HTTPException) as exc:
        await verify_field_owned_by_tenant(
            tenant_id="t1",
            field_id="field-1",
            http_client=client,
        )
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_ownership_verifier_forwards_bearer_token(monkeypatch):
    """The Bearer JWT from the inbound request must reach field-
    management-service so FMS's own tenant guard has what it needs."""
    from src.field_ownership import verify_field_owned_by_tenant

    captured: dict = {}

    async def fake_get(url, *, headers=None):
        captured["headers"] = dict(headers or {})
        m = MagicMock()
        m.status_code = 200
        m.json = MagicMock(return_value={"data": {"tenantId": "t1"}})
        return m

    client = MagicMock(spec=httpx.AsyncClient)
    client.get = AsyncMock(side_effect=fake_get)

    mock_req = MagicMock()
    mock_req.headers = {"Authorization": "Bearer jwt-abc"}

    await verify_field_owned_by_tenant(
        tenant_id="t1",
        field_id="field-1",
        http_request=mock_req,
        http_client=client,
    )
    assert captured["headers"].get("Authorization") == "Bearer jwt-abc"
    assert captured["headers"].get("X-Tenant-Id") == "t1"


@pytest.mark.asyncio
async def test_ownership_verifier_raises_403_on_tenant_mismatch():
    """Defense-in-depth: even if FMS returns 200 with a different
    tenant in the body (impossible if FMS is healthy, but we don't
    want to rely on that), the helper rejects."""
    from fastapi import HTTPException
    from src.field_ownership import verify_field_owned_by_tenant

    async def fake_get(url, *, headers=None):
        m = MagicMock()
        m.status_code = 200
        m.json = MagicMock(return_value={"data": {"tenantId": "other-tenant"}})
        return m

    client = MagicMock(spec=httpx.AsyncClient)
    client.get = AsyncMock(side_effect=fake_get)

    with pytest.raises(HTTPException) as exc:
        await verify_field_owned_by_tenant(
            tenant_id="t1",
            field_id="field-1",
            http_client=client,
        )
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_ownership_verifier_503_strict_mode(monkeypatch):
    """With ADVISORY_STRICT_OWNERSHIP=true, an FMS outage must surface
    as 503 — don't silently allow the caller through."""
    monkeypatch.setenv("ADVISORY_STRICT_OWNERSHIP", "true")
    from fastapi import HTTPException
    from src.field_ownership import verify_field_owned_by_tenant

    async def fake_get(url, *, headers=None):
        raise httpx.ConnectError("connection refused")

    client = MagicMock(spec=httpx.AsyncClient)
    client.get = AsyncMock(side_effect=fake_get)

    with pytest.raises(HTTPException) as exc:
        await verify_field_owned_by_tenant(
            tenant_id="t1",
            field_id="field-1",
            http_client=client,
        )
    assert exc.value.status_code == 503


@pytest.mark.asyncio
async def test_ownership_verifier_503_lenient_mode(monkeypatch):
    """With strict mode off (default), an FMS outage logs + returns
    without raising, so a transient blip doesn't break advisory."""
    monkeypatch.delenv("ADVISORY_STRICT_OWNERSHIP", raising=False)
    from src.field_ownership import verify_field_owned_by_tenant

    async def fake_get(url, *, headers=None):
        raise httpx.ConnectError("connection refused")

    client = MagicMock(spec=httpx.AsyncClient)
    client.get = AsyncMock(side_effect=fake_get)

    # Must not raise.
    result = await verify_field_owned_by_tenant(
        tenant_id="t1",
        field_id="field-1",
        http_client=client,
    )
    assert result is None


# =============================================================================
# Fix #3 — NDVI threshold alignment with vegetation-analysis-service
# =============================================================================


def test_nutrient_thresholds_match_vegetation_status_for_ndvi():
    """Regression pin: advisory's ``diagnose_from_ndvi`` thresholds
    (poor vs moderate vs good) must agree with vegetation's
    ``status_for_ndvi`` so a farmer doesn't see a "good" health badge
    next to a "nitrogen deficiency" advisory on the same field."""
    from src.kb.nutrients import _NDVI_MODERATE_CUTOFF, _NDVI_POOR_CUTOFF

    # These values are chosen to match vegetation-analysis-service's
    # boundaries:
    #   NDVI < 0.2  → vegetation "poor"
    #   NDVI < 0.4  → vegetation "moderate"
    #   NDVI >= 0.4 → vegetation "good" or "excellent"
    assert _NDVI_POOR_CUTOFF == 0.2, (
        "Advisory 'poor' cutoff drifted from vegetation's status_for_ndvi "
        "boundary (0.2). Update multi_date.py in lockstep or accept UX drift."
    )
    assert _NDVI_MODERATE_CUTOFF == 0.4, (
        "Advisory 'moderate' cutoff drifted from vegetation's status_for_ndvi "
        "boundary (0.4). Update multi_date.py in lockstep or accept UX drift."
    )


def test_diagnose_from_ndvi_below_poor_cutoff_flags_severe_nitrogen():
    from src.kb.nutrients import diagnose_from_ndvi

    diagnoses = diagnose_from_ndvi(0.15)  # below 0.2 → severe
    assert len(diagnoses) >= 1
    assert diagnoses[0]["id"] == "nitrogen_deficiency"
    assert diagnoses[0]["reason"] == "severe_ndvi_drop"


def test_diagnose_from_ndvi_between_cutoffs_flags_moderate_NK():
    from src.kb.nutrients import diagnose_from_ndvi

    diagnoses = diagnose_from_ndvi(0.3)  # between 0.2 and 0.4
    ids = {d["id"] for d in diagnoses}
    assert "nitrogen_deficiency" in ids
    assert "potassium_deficiency" in ids


def test_diagnose_from_ndvi_above_moderate_cutoff_no_nutrient_hypothesis():
    from src.kb.nutrients import diagnose_from_ndvi

    # NDVI 0.5 is "good" per vegetation — advisory should not hypothesise
    # a deficiency on the same field.
    assert diagnose_from_ndvi(0.5) == []
    assert diagnose_from_ndvi(0.8) == []
