"""Tests for the AI advisor v2 pure-Python modules.

These tests intentionally avoid network / qdrant / nats so they can run in
the standard CI test environment without extra services.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure the service package is importable as ``src.*``.
_SVC_ROOT = Path(__file__).resolve().parents[1]
if str(_SVC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SVC_ROOT))

from src.governance import (  # noqa: E402
    DecisionStatus,
    GovernanceEngine,
    RiskLevel,
)
from src.learning import (  # noqa: E402
    DEFAULT_NEUTRAL_RATE,
    LearningEngine,
)
from src.signal_derivation import (  # noqa: E402
    FieldContext,
    compute_risk_score,
    derive_signals,
)


# ---------- signal_derivation ---------------------------------------------


def _healthy_field(**overrides) -> FieldContext:
    base = {
        "ndvi": 0.7,
        "ndwi": 0.5,
        "soil_moisture": 0.5,
        "temperature": 25.0,
        "crop_type": "wheat",
        "growth_stage": "vegetative",
        "region": "saudi",
    }
    base.update(overrides)
    return FieldContext(**base)


def test_derive_signals_healthy_field() -> None:
    signals = derive_signals(_healthy_field())
    assert not signals.water_stress
    assert not signals.heat_stress
    assert not signals.nitrogen_deficiency
    assert signals.pest_risk == "low"
    assert signals.growth_stage_appropriate
    assert not signals.critical_ndvi


def test_derive_signals_water_stress_via_low_ndwi() -> None:
    signals = derive_signals(_healthy_field(ndwi=0.1))
    assert signals.water_stress


def test_derive_signals_water_stress_via_low_soil_moisture() -> None:
    signals = derive_signals(_healthy_field(soil_moisture=0.2))
    assert signals.water_stress


def test_derive_signals_heat_stress() -> None:
    signals = derive_signals(_healthy_field(temperature=40.0))
    assert signals.heat_stress


def test_derive_signals_nitrogen_deficiency() -> None:
    signals = derive_signals(_healthy_field(nitrogen_level=0.2))
    assert signals.nitrogen_deficiency


def test_derive_signals_critical_ndvi() -> None:
    signals = derive_signals(_healthy_field(ndvi=0.1))
    assert signals.critical_ndvi


def test_compute_risk_score_zero_for_healthy() -> None:
    field = _healthy_field()
    score = compute_risk_score(derive_signals(field), field)
    assert score == 0.0


def test_compute_risk_score_clamped_to_one() -> None:
    field = _healthy_field(
        ndvi=0.05,
        ndwi=0.05,
        soil_moisture=0.05,
        temperature=45.0,
        nitrogen_level=0.1,
        soil_texture="sandy",
    )
    score = compute_risk_score(derive_signals(field), field)
    assert 0.0 <= score <= 1.0
    assert score == pytest.approx(1.0)


def test_sandy_soil_amplifies_risk() -> None:
    sandy = _healthy_field(ndwi=0.1, soil_texture="sandy")
    loamy = _healthy_field(ndwi=0.1, soil_texture="loam")
    sandy_score = compute_risk_score(derive_signals(sandy), sandy)
    loamy_score = compute_risk_score(derive_signals(loamy), loamy)
    assert sandy_score > loamy_score


# ---------- governance -----------------------------------------------------


def test_governance_auto_approves_low_risk() -> None:
    engine = GovernanceEngine()
    out = engine.evaluate({"action": "increase_irrigation", "risk_score": 0.2})
    assert out["status"] == DecisionStatus.APPROVED.value
    assert out["risk_level"] == RiskLevel.LOW.value
    assert out["requires_approval"] is False


def test_governance_review_required_action() -> None:
    engine = GovernanceEngine()
    out = engine.evaluate({"action": "add_nitrogen", "risk_score": 0.4})
    assert out["status"] == DecisionStatus.PENDING.value
    assert out["requires_approval"] is True


def test_governance_review_required_via_high_score() -> None:
    engine = GovernanceEngine()
    out = engine.evaluate({"action": "increase_irrigation", "risk_score": 0.7})
    assert out["status"] == DecisionStatus.PENDING.value


def test_governance_rejects_high_risk_action() -> None:
    engine = GovernanceEngine()
    out = engine.evaluate({"action": "apply_banned_pesticide", "risk_score": 0.5})
    assert out["status"] == DecisionStatus.REJECTED.value
    assert out["risk_level"] == RiskLevel.HIGH.value
    assert out["requires_approval"] is False


def test_governance_rejects_when_score_extreme() -> None:
    engine = GovernanceEngine()
    out = engine.evaluate({"action": "no_action", "risk_score": 0.95})
    assert out["status"] == DecisionStatus.REJECTED.value


def test_governance_approve_modifies_action() -> None:
    engine = GovernanceEngine()
    pending = engine.evaluate({"action": "add_nitrogen", "risk_score": 0.4})
    approved = engine.approve(pending, approved_by="agronomist", modified_action="add_phosphorus")
    assert approved["status"] == DecisionStatus.APPROVED.value
    assert approved["action"] == "add_phosphorus"
    assert approved["approved_by"] == "agronomist"


def test_governance_reject_records_reason() -> None:
    engine = GovernanceEngine()
    pending = engine.evaluate({"action": "add_nitrogen", "risk_score": 0.4})
    rejected = engine.reject(pending, rejected_by="agronomist", reason="too late in season")
    assert rejected["status"] == DecisionStatus.REJECTED.value
    assert "too late in season" in rejected["governance_reason"]


def test_governance_evaluate_does_not_mutate_input() -> None:
    engine = GovernanceEngine()
    original = {"action": "increase_irrigation", "risk_score": 0.2}
    snapshot = dict(original)
    engine.evaluate(original)
    assert original == snapshot


def test_governance_approve_does_not_mutate_input() -> None:
    engine = GovernanceEngine()
    pending = engine.evaluate({"action": "add_nitrogen", "risk_score": 0.4})
    snapshot = dict(pending)
    approved = engine.approve(pending, approved_by="x", modified_action="add_potassium")
    assert pending == snapshot  # original untouched
    assert approved is not pending
    assert approved["action"] == "add_potassium"


def test_governance_reject_does_not_mutate_input() -> None:
    engine = GovernanceEngine()
    pending = engine.evaluate({"action": "add_nitrogen", "risk_score": 0.4})
    snapshot = dict(pending)
    rejected = engine.reject(pending, rejected_by="x", reason="test")
    assert pending == snapshot
    assert rejected is not pending
    assert rejected["status"] == DecisionStatus.REJECTED.value


# ---------- learning -------------------------------------------------------


def test_learning_default_rate_when_no_data() -> None:
    engine = LearningEngine()
    assert engine.get_success_rate("wheat", "saudi", "increase_irrigation") == DEFAULT_NEUTRAL_RATE


def test_learning_records_and_computes_rate() -> None:
    engine = LearningEngine()
    for result in ["improved", "improved", "no_change", "worsened"]:
        engine.record_outcome({
            "crop": "wheat",
            "region": "saudi",
            "action": "increase_irrigation",
            "result": result,
        })
    assert engine.get_success_rate("wheat", "saudi", "increase_irrigation") == pytest.approx(0.5)


def test_learning_invalid_result_treated_as_no_change() -> None:
    engine = LearningEngine()
    engine.record_outcome({
        "crop": "wheat",
        "region": "saudi",
        "action": "no_action",
        "result": "garbage",
    })
    assert engine.get_success_rate("wheat", "saudi", "no_action") == 0.0


def test_learning_bounded_memory() -> None:
    engine = LearningEngine(memory_size=3)
    for _ in range(10):
        engine.record_outcome({
            "crop": "wheat",
            "region": "saudi",
            "action": "no_action",
            "result": "improved",
        })
    assert len(engine.outcomes[("wheat", "saudi", "no_action")]) == 3


def test_learning_statistics() -> None:
    engine = LearningEngine()
    engine.record_outcome({"crop": "w", "region": "r", "action": "a", "result": "improved"})
    stats = engine.get_statistics()
    assert stats["unique_keys"] == 1
    assert stats["total_recorded_outcomes"] == 1


# ---------- PR-C: resilience wiring ---------------------------------------
#
# These tests exercise the consumption of the canonical resilience primitives
# from the advisor router:
#   * shared.ai.circuit_breaker.CircuitBreaker (PR-A)
#   * shared.stability.retry_classifier.build_retry / classify (PR-B)
# They intentionally do NOT spin up Redis or NATS — they patch the helpers in
# place and assert the contract.


@pytest.mark.asyncio
async def test_redis_breaker_open_falls_back_to_memory(monkeypatch) -> None:
    """When the Redis circuit is OPEN, _save/_load fall through to in-memory.

    The breaker must NOT surface the component name to callers — endpoints
    keep working transparently.
    """
    from src import advisor_router  # noqa: PLC0415

    # Force a real breaker (in case shared/ wasn't importable for some reason).
    if not advisor_router._RESILIENCE_AVAILABLE:
        pytest.skip("shared resilience primitives not available")

    # Trip the breaker manually.
    advisor_router._redis_breaker.trip()
    assert advisor_router._redis_breaker.is_open

    # Pretend Redis is "available" but every call would go through the breaker.
    class _SpyClient:
        calls = 0

        async def set(self, *_a, **_kw):  # pragma: no cover - must not be called
            _SpyClient.calls += 1
            return True

        async def get(self, *_a, **_kw):  # pragma: no cover - must not be called
            _SpyClient.calls += 1
            return None

        async def delete(self, *_a, **_kw):  # pragma: no cover - must not be called
            _SpyClient.calls += 1
            return 1

    async def _fake_client():
        return _SpyClient()

    monkeypatch.setattr(advisor_router, "_redis_client", _fake_client)
    advisor_router._pending_memory.clear()
    try:
        await advisor_router._save_pending("d1", {"k": "v"})
        loaded = await advisor_router._load_pending("d1")
        assert loaded == {"k": "v"}, "should round-trip via in-memory fallback"
        # No real Redis ops should have run while the breaker was OPEN.
        assert _SpyClient.calls == 0
    finally:
        advisor_router._redis_breaker.reset()
        advisor_router._pending_memory.clear()


@pytest.mark.asyncio
async def test_redis_breaker_error_not_leaked_to_response() -> None:
    """The CircuitBreakerError type is never used as an HTTP response detail.

    We assert this structurally: the helper that wraps Redis ops returns
    ``None`` on CircuitBreakerError, never re-raising. Endpoints therefore
    cannot accidentally surface 'advisor.redis' to the client.
    """
    from src import advisor_router  # noqa: PLC0415

    if not advisor_router._RESILIENCE_AVAILABLE:
        pytest.skip("shared resilience primitives not available")

    advisor_router._redis_breaker.trip()
    try:
        async def _never_called():  # pragma: no cover - must not run
            raise AssertionError("should not be invoked when CB is OPEN")

        result = await advisor_router._through_redis_breaker("set", _never_called)
        # Critical: returns None, does NOT raise CircuitBreakerError.
        assert result is None
    finally:
        advisor_router._redis_breaker.reset()


def test_build_retry_auth_uses_single_attempt() -> None:
    """AUTH-only retry policy collapses to stop_after_attempt(1) (PR-B contract)."""
    from shared.stability.retry_classifier import (  # noqa: PLC0415
        FailureClass,
        build_retry,
    )

    retrier = build_retry(failure_classes={FailureClass.AUTH}, max_attempts=5)
    # AUTH is silently dropped → effective attempts = 1.
    assert retrier.stop.max_attempt_number == 1


@pytest.mark.asyncio
async def test_build_retry_does_not_retry_auth_even_when_requested() -> None:
    """Defense in depth: a 401/403 must never trigger a retry, regardless of
    whether the caller listed AUTH in failure_classes.
    """
    import httpx  # noqa: PLC0415

    from shared.stability.retry_classifier import (  # noqa: PLC0415
        FailureClass,
        build_retry,
    )

    calls = {"n": 0}

    async def _raises_401():
        calls["n"] += 1
        request = httpx.Request("GET", "http://example.test/")
        response = httpx.Response(401, request=request)
        raise httpx.HTTPStatusError("unauthorized", request=request, response=response)

    retrier = build_retry(
        failure_classes={
            FailureClass.AUTH,
            FailureClass.NETWORK,
            FailureClass.TIMEOUT,
        },
        max_attempts=5,
        asynchronous=True,
    )

    with pytest.raises(httpx.HTTPStatusError):
        await retrier(_raises_401)
    assert calls["n"] == 1, "AUTH must never be retried"


@pytest.mark.asyncio
async def test_build_retry_exhausts_on_persistent_network_failure() -> None:
    """Retries up to max_attempts on a retryable failure class, then re-raises."""
    import httpx  # noqa: PLC0415

    from shared.stability.retry_classifier import build_retry  # noqa: PLC0415

    calls = {"n": 0}

    async def _always_fails():
        calls["n"] += 1
        raise httpx.ConnectError("boom")

    retrier = build_retry(max_attempts=3, multiplier=0.001, max_wait=0.01, asynchronous=True)
    with pytest.raises(httpx.ConnectError):
        await retrier(_always_fails)
    assert calls["n"] == 3
