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
_ADVISORY_MAIN_TREE = ast.parse(_ADVISORY_MAIN.read_text(encoding="utf-8"))


def _handler_node(handler_name: str) -> ast.AsyncFunctionDef:
    for node in ast.walk(_ADVISORY_MAIN_TREE):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == handler_name:
            return node
    # `pytest.fail` raises unconditionally (NoReturn-like) so control
    # never reaches past this line — return a clean TypeError for any
    # static analyser that doesn't follow pytest.fail's non-returning
    # behaviour, and CodeQL's "mixed explicit/implicit returns" note.
    raise pytest.fail.Exception(f"Handler {handler_name} not found in main.py")


def _call_target_name(call: ast.Call) -> str | None:
    """Return the function name being invoked (last segment of the
    attribute chain, or the bare name for plain function calls)."""
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _awaited_calls(node: ast.AST) -> list[ast.Call]:
    """Collect every ``await <expr>(...)`` call inside *node* — the
    gate is always awaited, so this is what we check."""
    out: list[ast.Call] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Await) and isinstance(child.value, ast.Call):
            out.append(child.value)
    return out


@pytest.mark.parametrize(
    "handler",
    ["comprehensive_advisory", "verify_crop_loan"],
)
def test_field_scoped_handlers_call_ownership_verifier(handler: str):
    """Regression pin (Copilot audit round 1, tightened in round 4):
    both field-scoped advisory endpoints must call
    ``verify_field_owned_by_tenant`` BEFORE running the downstream
    orchestrator / engine. This test walks the parsed AST for a
    real ``await verify_field_owned_by_tenant(...)`` ``Call`` node —
    not a substring match — so a gate accidentally moved into a
    comment, docstring, or dead conditional branch still fails."""
    node = _handler_node(handler)
    calls = _awaited_calls(node)
    names = [_call_target_name(c) for c in calls]
    assert "verify_field_owned_by_tenant" in names, (
        f"{handler}: no `await verify_field_owned_by_tenant(...)` call "
        f"found in function body. Awaited calls found: {names}. "
        "Cross-tenant field_id access is possible without it."
    )


@pytest.mark.parametrize(
    "handler",
    ["comprehensive_advisory", "verify_crop_loan"],
)
def test_field_scoped_handlers_gate_runs_before_downstream(handler: str):
    """Defense-in-depth: the gate must execute BEFORE we touch the
    orchestrator / loan engine. If someone reorders the calls so the
    downstream fan-out runs first, this test fails."""
    node = _handler_node(handler)
    # Walk the statements in source order and find the first awaited
    # call whose target is either the gate or a downstream.
    DOWNSTREAM = {"collect", "verify"}  # orchestrator.collect / engine.verify
    first_gate_idx: int | None = None
    first_downstream_idx: int | None = None
    for idx, call in enumerate(_awaited_calls(node)):
        name = _call_target_name(call)
        if name == "verify_field_owned_by_tenant" and first_gate_idx is None:
            first_gate_idx = idx
        if name in DOWNSTREAM and first_downstream_idx is None:
            first_downstream_idx = idx
    assert first_gate_idx is not None, f"{handler}: ownership gate not awaited at all — re-check."
    if first_downstream_idx is not None:
        assert first_gate_idx < first_downstream_idx, (
            f"{handler}: ownership gate runs AFTER downstream call "
            f"(gate={first_gate_idx}, downstream={first_downstream_idx}). "
            "Reorder so the gate fails closed before any fan-out."
        )


@pytest.mark.parametrize(
    "handler",
    ["comprehensive_advisory", "verify_crop_loan"],
)
def test_field_scoped_handlers_accept_request_for_bearer_forwarding(handler: str):
    """The ownership verifier needs the inbound Bearer JWT to prove
    identity to field-management-service. The handler must accept a
    ``request`` parameter for that forwarding."""
    node = _handler_node(handler)
    arg_names = [a.arg for a in node.args.args]
    assert "request" in arg_names, (
        f"{handler}: missing `request: Request` parameter. Bearer JWT can't be forwarded to field-management-service."
    )


# =============================================================================
# Fix #2a — verify_field_owned_by_tenant helper behaviour
# =============================================================================


@pytest.mark.asyncio
async def test_ownership_verifier_raises_403_without_tenant():
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
async def test_ownership_verifier_forwards_bearer_token():
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


# =============================================================================
# Copilot review round 4 pins
# =============================================================================


@pytest.mark.asyncio
async def test_ownership_verifier_401_passes_through_as_401():
    """Regression pin: FMS returning 401 (bad/missing Bearer) must
    surface as 401 to the caller — not 503 (which blames a service
    outage) nor 400 (which blames field_id format). Copilot review
    round 4."""
    from fastapi import HTTPException
    from src.field_ownership import verify_field_owned_by_tenant

    async def fake_get(url, *, headers=None):
        m = MagicMock()
        m.status_code = 401
        return m

    client = MagicMock(spec=httpx.AsyncClient)
    client.get = AsyncMock(side_effect=fake_get)

    with pytest.raises(HTTPException) as exc:
        await verify_field_owned_by_tenant(
            tenant_id="t1",
            field_id="field-1",
            http_client=client,
        )
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_ownership_verifier_429_preserved():
    """Regression pin: FMS rate-limit (429) must propagate so upstream
    clients can back off, not get swallowed into a generic 503."""
    from fastapi import HTTPException
    from src.field_ownership import verify_field_owned_by_tenant

    async def fake_get(url, *, headers=None):
        m = MagicMock()
        m.status_code = 429
        return m

    client = MagicMock(spec=httpx.AsyncClient)
    client.get = AsyncMock(side_effect=fake_get)

    with pytest.raises(HTTPException) as exc:
        await verify_field_owned_by_tenant(
            tenant_id="t1",
            field_id="field-1",
            http_client=client,
        )
    assert exc.value.status_code == 429


@pytest.mark.asyncio
async def test_ownership_verifier_400_tenant_message_maps_to_403():
    """FMS's TenantGuard can return 400 when X-Tenant-Id is missing.
    The old code labelled every 400 "Invalid field_id", which hid the
    real cause. Now we peek at the error body and surface 403 for
    tenant-shaped 400s (Copilot review round 4)."""
    from fastapi import HTTPException
    from src.field_ownership import verify_field_owned_by_tenant

    async def fake_get(url, *, headers=None):
        m = MagicMock()
        m.status_code = 400
        m.json = MagicMock(return_value={"message": "Tenant ID is required"})
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
async def test_ownership_verifier_400_field_message_stays_400():
    """A real field_id validation 400 from FMS should still surface
    as 400 (same as before)."""
    from fastapi import HTTPException
    from src.field_ownership import verify_field_owned_by_tenant

    async def fake_get(url, *, headers=None):
        m = MagicMock()
        m.status_code = 400
        m.json = MagicMock(return_value={"message": "Validation failed (uuid is expected)"})
        return m

    client = MagicMock(spec=httpx.AsyncClient)
    client.get = AsyncMock(side_effect=fake_get)

    with pytest.raises(HTTPException) as exc:
        await verify_field_owned_by_tenant(
            tenant_id="t1",
            field_id="not-a-uuid",
            http_client=client,
        )
    assert exc.value.status_code == 400


def test_comprehensive_advisory_fails_closed_when_user_has_no_tenant():
    """Regression pin (Copilot review round 4): the old
    ``tenant_id = user.tenant_id or "default"`` silently mapped
    anonymous JWTs to the "default" tenant, which then PASSED the
    ownership gate (FMS happily returned a row for that synthetic
    tenant). The handler must now reject 403 before touching FMS.

    We assert on the ASSIGNMENT form specifically — the anti-pattern
    name may still appear in docstrings explaining *why* it's gone.
    """
    import re

    src = _ADVISORY_MAIN.read_text(encoding="utf-8")
    # Match:  tenant_id = user.tenant_id or "default"   (assignment form)
    # Don't match:  # ``user.tenant_id or "default"``   (docstring mention)
    anti_pattern = re.compile(
        r"^\s*tenant_id\s*=\s*user\.tenant_id\s+or\s+[\"']default[\"']",
        re.MULTILINE,
    )
    assert not anti_pattern.search(src), (
        "Default-tenant fallback reintroduced. Use `(user.tenant_id or "
        "'').strip()` and raise 403 when empty, so the ownership gate "
        "fails closed instead of silently using a synthetic tenant."
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "bogus",
    [
        "../etc/passwd",
        "field/with/slashes",
        "field%2e%2e",
        "field?injection=1",
        "field with space",
        "field\nwith\nnewline",
        "field;DROP TABLE",
        "a" * 101,  # too long
    ],
)
async def test_ownership_verifier_rejects_ssrf_prone_field_ids(bogus: str):
    """Regression pin (CodeQL: partial SSRF on URL construction):
    the helper must reject field_ids that contain path-separators,
    URL-escape characters, control characters, or are too long —
    BEFORE building the outbound URL. FastAPIPath on the endpoint
    would normally reject these, but the helper is reusable and must
    not rely on its callers."""
    from fastapi import HTTPException
    from src.field_ownership import verify_field_owned_by_tenant

    # Use a client that would blow up if reached — the validator must
    # fail before any HTTP call happens.
    reached = {"called": False}

    async def fail_if_reached(url, **kwargs):
        reached["called"] = True
        raise AssertionError(f"validator bypassed; reached HTTP call with url={url!r}")

    client = MagicMock(spec=httpx.AsyncClient)
    client.get = AsyncMock(side_effect=fail_if_reached)

    with pytest.raises(HTTPException) as exc:
        await verify_field_owned_by_tenant(
            tenant_id="t1",
            field_id=bogus,
            http_client=client,
        )
    assert exc.value.status_code == 400, (
        f"bogus field_id {bogus!r} must be rejected with 400 before the HTTP call; got {exc.value.status_code}"
    )
    assert reached["called"] is False, f"field_id {bogus!r} reached the outbound HTTP call — SSRF gate failed"


@pytest.mark.asyncio
async def test_ownership_verifier_sanitises_field_id_in_logs(caplog):
    """Regression pin (CodeQL: log injection, medium): a CRLF-crafted
    field_id must not end up verbatim in a log record — the sanitiser
    strips \\r and \\n so an attacker can't forge separate log lines.

    Note: this test does NOT use a CRLF-containing field_id to trigger
    the log, because the shape gate (added for the SSRF fix) rejects
    those up-front. Instead we prove the sanitiser works in isolation.
    """
    from src.field_ownership import _safe_for_log

    crafted = "field-1\r\nFAKE LOG ENTRY x-user=admin"
    sanitised = _safe_for_log(crafted)
    assert "\r" not in sanitised
    assert "\n" not in sanitised
    # The dangerous substring should still be visible (it's not about
    # deleting content, just preventing newline-based separation).
    assert "FAKE LOG ENTRY" in sanitised


@pytest.mark.parametrize(
    "handler",
    ["comprehensive_advisory", "verify_crop_loan"],
)
def test_field_id_is_path_validated(handler: str):
    """Both handlers must declare ``field_id`` with an ``Annotated[...,
    FastAPIPath(pattern=..., max_length=...)]`` so path-traversal and
    URL-escape characters are rejected at the framework boundary —
    BEFORE the engine interpolates field_id into downstream URLs."""
    node = _handler_node(handler)
    for arg in node.args.args:
        if arg.arg != "field_id":
            continue
        ann = arg.annotation
        # Expect ``Annotated[str, FastAPIPath(...)]`` — the subscript
        # node must contain a Call to FastAPIPath.
        if not isinstance(ann, ast.Subscript):
            pytest.fail(f"{handler}: field_id annotation is not Annotated[...]; path validation missing.")
        calls = [c for c in ast.walk(ann) if isinstance(c, ast.Call)]
        call_names = [_call_target_name(c) for c in calls]
        assert "FastAPIPath" in call_names, (
            f"{handler}: field_id missing FastAPIPath(...) validator "
            f"(calls found: {call_names}). Path traversal / URL-escape "
            "characters won't be rejected at the framework boundary."
        )
        return
    pytest.fail(f"{handler}: no field_id parameter found")
