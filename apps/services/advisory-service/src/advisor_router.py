"""
Advisor v2 router — exposes the AI advisor (CRAG + KG + governance + learning)
as a small set of endpoints alongside the existing advisory endpoints.

Mounted under ``/v2/...`` and reachable through Kong as
``/api/v1/advisory/v2/...`` (Kong route ``advisory-service-route`` strips
``/api/v1/advisory``).

Pending decisions that require human approval are persisted in Redis with a
TTL when available; otherwise an in-memory map is used (single-instance only).
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from .advisor_engine import AdvisorEngine
from .feedback import FeedbackPublisher
from .governance import GovernanceEngine
from .kb.crag_knowledge_base import CragKnowledgeBase
from .kb.knowledge_graph_client import KnowledgeGraphClient
from .learning import LearningEngine
from .signal_derivation import FieldContext

# Canonical resilience primitives (PR-A: adaptive circuit breaker, PR-B: retry).
# These are imported eagerly because they are pure-Python and have no heavy
# dependencies beyond ``tenacity`` (declared in pyproject base extras).
try:  # pragma: no cover - import-time defensive
    from shared.ai.circuit_breaker import (
        CircuitBreaker,
        CircuitBreakerConfig,
        CircuitBreakerError,
    )
    from shared.stability.retry_classifier import FailureClass, build_retry

    _RESILIENCE_AVAILABLE = True
except Exception:  # noqa: BLE001 — degrade gracefully if shared/ is missing
    CircuitBreaker = None  # type: ignore[assignment]
    CircuitBreakerConfig = None  # type: ignore[assignment]
    CircuitBreakerError = Exception  # type: ignore[assignment,misc]
    FailureClass = None  # type: ignore[assignment]
    build_retry = None  # type: ignore[assignment]
    _RESILIENCE_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v2", tags=["advisor-v2"])

# Pending-decision Redis key prefix and TTL (24h).
_PENDING_KEY_PREFIX = "advisor:pending"
_PENDING_TTL_SECONDS = 24 * 3600
# Bound the in-memory fallback so a long Redis outage can't exhaust memory.
_PENDING_MEMORY_MAX = 1024
# Dimensionality of the deterministic fallback embedding. Matches what the
# AdvisorEngine / CRAG vector store expect when vLLM is unreachable.
_FALLBACK_EMBEDDING_DIM = 384

# In-memory fallback for pending decisions (insertion-ordered → drop oldest).
_pending_memory: dict[str, dict[str, Any]] = {}

# Lazily-initialised module-level singletons. Initialised inside the request
# handler the first time it runs, so we don't have to touch the existing
# ``main.py`` lifespan.
_advisor: AdvisorEngine | None = None
_feedback: FeedbackPublisher | None = None
_kg_client: KnowledgeGraphClient | None = None


# ---------- Request models -------------------------------------------------


class FieldDataRequest(BaseModel):
    ndvi: float = Field(..., ge=0.0, le=1.0, description="NDVI 0-1")
    ndwi: float = Field(..., ge=0.0, le=1.0, description="NDWI 0-1")
    soil_moisture: float = Field(..., ge=0.0, le=1.0, description="Soil moisture 0-1")
    temperature: float = Field(..., ge=-60.0, le=70.0, description="°C")
    crop_type: str = Field(..., min_length=1, max_length=64)
    growth_stage: str = Field(..., min_length=1, max_length=32)
    region: str = Field(..., min_length=1, max_length=32)
    soil_texture: str | None = Field(default=None, max_length=16)
    nitrogen_level: float | None = Field(default=None, ge=0.0, le=1.0)


class ApproveRequest(BaseModel):
    decision_id: str = Field(..., min_length=1, max_length=128)
    modified_action: str | None = Field(default=None, max_length=64)


class RejectRequest(BaseModel):
    decision_id: str = Field(..., min_length=1, max_length=128)
    reason: str = Field(default="", max_length=500)


class FeedbackRequest(BaseModel):
    decision_id: str = Field(..., min_length=1, max_length=128)
    result: str = Field(..., pattern="^(improved|no_change|worsened)$")


# ---------- Pending decision storage --------------------------------------


# Cached Redis client (created on first use, reused thereafter).
_redis_singleton: Any = None
_redis_unavailable: bool = False

# Canonical circuit breaker around Redis. When Redis flaps, the breaker trips
# OPEN and subsequent calls fail fast (no 5s socket-timeout per request) until
# the adaptive recovery window elapses. We never surface ``CircuitBreakerError``
# to the caller — it always falls through to the in-memory fallback so endpoint
# behavior is identical to the pre-PR state. The component name is *not*
# returned in any HTTP response, only logged at debug level — preventing
# information leakage about backend topology.
def _build_redis_breaker() -> Any:
    """Construct the Redis circuit breaker, or ``None`` when shared/ is absent."""
    if not _RESILIENCE_AVAILABLE or CircuitBreaker is None:
        return None
    return CircuitBreaker(
        name="advisor.redis",
        config=CircuitBreakerConfig(
            failure_threshold=5,
            success_threshold=2,
            timeout_seconds=15.0,
            adaptive_recovery=True,
            min_recovery_seconds=5.0,
            max_recovery_seconds=120.0,
        ),
    )


_redis_breaker: Any = _build_redis_breaker()


async def _through_redis_breaker(op_name: str, coro_factory: Any) -> Any:
    """Run a Redis operation through the circuit breaker.

    ``coro_factory`` must be a zero-arg async callable producing the awaitable.
    On ``CircuitBreakerError`` returns ``None`` — callers fall through to the
    in-memory fallback. We deliberately don't include the component name in
    any error returned to the client.
    """
    if _redis_breaker is None:
        return await coro_factory()
    try:
        return await _redis_breaker.call(coro_factory)
    except CircuitBreakerError:
        # Circuit is OPEN — fail fast, fall through to in-memory.
        logger.debug("advisor.redis_breaker_open", extra={"op": op_name})
        return None
    except Exception as exc:  # noqa: BLE001 — caller logs context
        logger.warning(
            "advisor.redis_op_failed",
            extra={"op": op_name, "error": str(exc)},
        )
        return None


async def _redis_client() -> Any:
    """Return a connected ``redis.asyncio.Redis`` client, or ``None``.

    Typed ``Any`` to avoid importing ``redis`` at module load (it's an optional
    dependency). The connection is created once and reused — opening a new
    TCP/auth connection on every approve/reject/feedback call would be
    wasteful and add unnecessary latency under load.
    """
    global _redis_singleton, _redis_unavailable
    if _redis_singleton is not None:
        return _redis_singleton
    if _redis_unavailable:
        return None

    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        _redis_unavailable = True
        return None
    try:
        import redis.asyncio as aioredis  # noqa: PLC0415
    except ImportError:
        _redis_unavailable = True
        return None
    try:
        client = aioredis.from_url(redis_url, decode_responses=True, socket_timeout=5)
        # Run the ping through the breaker so a hung redis trips it instead of
        # blocking every caller for 5s on the socket timeout.
        ping_result = await _through_redis_breaker("ping", client.ping)
        if ping_result is None:
            # Either CB OPEN, or the ping raised — close the half-built client.
            try:
                await client.aclose()
            except Exception:  # noqa: BLE001
                pass
            return None
        _redis_singleton = client
        return client
    except Exception as exc:  # noqa: BLE001
        logger.warning("advisor.redis_unavailable", extra={"error": str(exc)})
        # Don't permanently disable — Redis may come back; just don't return a
        # broken client right now. Next call will retry.
        return None


async def _save_pending(decision_id: str, decision: dict[str, Any]) -> None:
    client = await _redis_client()
    if client is not None:
        result = await _through_redis_breaker(
            "set",
            lambda: client.set(
                f"{_PENDING_KEY_PREFIX}:{decision_id}",
                json.dumps(decision),
                ex=_PENDING_TTL_SECONDS,
            ),
        )
        if result is not None:
            return
    # Bounded LRU-ish fallback: drop the oldest entry when over capacity.
    if len(_pending_memory) >= _PENDING_MEMORY_MAX:
        try:
            oldest = next(iter(_pending_memory))
            _pending_memory.pop(oldest, None)
        except StopIteration:
            pass
    _pending_memory[decision_id] = decision


async def _load_pending(decision_id: str) -> dict[str, Any] | None:
    client = await _redis_client()
    if client is not None:
        raw = await _through_redis_breaker(
            "get",
            lambda: client.get(f"{_PENDING_KEY_PREFIX}:{decision_id}"),
        )
        if raw:
            try:
                return json.loads(raw)
            except (TypeError, ValueError) as exc:
                logger.warning("advisor.pending_decode_failed", extra={"error": str(exc)})
    return _pending_memory.get(decision_id)


async def _delete_pending(decision_id: str) -> None:
    client = await _redis_client()
    if client is not None:
        await _through_redis_breaker(
            "delete",
            lambda: client.delete(f"{_PENDING_KEY_PREFIX}:{decision_id}"),
        )
    _pending_memory.pop(decision_id, None)


# ---------- Embedding function (vLLM with deterministic fallback) ---------


async def _vllm_embedding(text: str) -> list[float]:
    """Embed ``text`` via vLLM. On failure return a deterministic fallback.

    The fallback uses SHA-256 to derive a stable 384-dim float vector — this
    keeps the system testable end-to-end without an embedding service.

    Transient HTTP errors (connect/read timeout, 429, 5xx) are retried via the
    canonical ``shared.stability.retry_classifier.build_retry`` helper. AUTH
    (401/403) is never retried — defense in depth at the helper level.
    """
    import httpx  # noqa: PLC0415

    vllm_url = os.getenv("VLLM_BASE_URL", "http://vllm-deepseek:8270/v1")
    vllm_model = os.getenv("VLLM_EMBEDDING_MODEL", "meta-llama/Llama-3-8b-Instruct")

    async def _do_post() -> list[float] | None:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{vllm_url}/embeddings",
                json={"model": vllm_model, "input": text},
            )
            # Trigger retry for 429/5xx; classify(HTTPStatusError) handles it.
            resp.raise_for_status()
            data = resp.json()
            return data["data"][0]["embedding"]

    try:
        if _RESILIENCE_AVAILABLE and build_retry is not None:
            retrier = build_retry(
                failure_classes={
                    FailureClass.NETWORK,
                    FailureClass.TIMEOUT,
                    FailureClass.RATE_LIMITED,
                    FailureClass.SERVER_ERROR,
                    FailureClass.SERVICE_UNAVAILABLE,
                },
                max_attempts=3,
                multiplier=0.5,
                max_wait=5.0,
                asynchronous=True,
            )
            embedding = await retrier(_do_post)
        else:
            embedding = await _do_post()
        if embedding is not None:
            return embedding
    except Exception as exc:  # noqa: BLE001 — fall through to deterministic fallback
        logger.warning("advisor.vllm_embedding_failed", extra={"error": str(exc)})

    # Deterministic fallback — SHA-256 expanded to ``_FALLBACK_EMBEDDING_DIM``
    # floats in [-1, 1).
    import hashlib  # noqa: PLC0415

    digest = hashlib.sha256(text.encode("utf-8")).digest()
    expanded = (digest * ((_FALLBACK_EMBEDDING_DIM // len(digest)) + 1))[:_FALLBACK_EMBEDDING_DIM]
    return [(b - 128) / 128.0 for b in expanded]


# ---------- Engine bootstrap (lazy) ---------------------------------------


async def _get_advisor() -> AdvisorEngine:
    """Lazily construct the singleton :class:`AdvisorEngine`."""
    global _advisor, _feedback, _kg_client
    if _advisor is not None:
        return _advisor

    kg_url = os.getenv("KNOWLEDGE_GRAPH_URL", "http://knowledge-graph:8140/api/v1")
    qdrant_host = os.getenv("QDRANT_HOST", "qdrant")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    nats_url = os.getenv("NATS_URL", "nats://nats:4222")

    _kg_client = KnowledgeGraphClient(base_url=kg_url)

    crag_kb: CragKnowledgeBase | None = None
    try:
        crag_kb = CragKnowledgeBase(qdrant_host=qdrant_host, qdrant_port=qdrant_port)
    except Exception as exc:  # noqa: BLE001 — degrade gracefully without Qdrant
        logger.warning("advisor.crag_unavailable", extra={"error": str(exc)})

    _feedback = FeedbackPublisher(nats_url=nats_url)
    await _feedback.connect()

    _advisor = AdvisorEngine(
        kg_client=_kg_client,
        crag_kb=crag_kb,
        governance=GovernanceEngine(),
        learning=LearningEngine(),
        feedback=_feedback,
        embedding_func=_vllm_embedding,
    )
    return _advisor


# ---------- Auth dependency -----------------------------------------------


async def _resolve_current_user() -> Any:
    """Resolve the current user via shared auth, or return an anonymous stub.

    Implemented as a *real* async dependency function (not a closure built at
    module-load time) so tests can override it with
    ``app.dependency_overrides[_resolve_current_user] = ...``.
    """
    try:
        from shared.auth.dependencies import get_current_user  # noqa: PLC0415
    except Exception:  # noqa: BLE001 — shared auth not available in this env
        return {"id": "anonymous", "tenant_id": "default"}

    # ``get_current_user`` is itself a FastAPI dependency that expects to be
    # resolved by the framework (it inspects the ``Authorization`` header via
    # ``Depends(security)``). Calling it directly here would bypass that
    # plumbing, so instead we raise to let the user wire it as ``Depends``.
    # In practice tests should override ``_resolve_current_user`` directly.
    raise RuntimeError(
        "_resolve_current_user must be overridden when shared.auth is present"
    )


def _current_user_dep() -> Any:
    """Build a FastAPI ``Depends(...)`` that resolves the current user.

    Prefers ``shared.auth.dependencies.get_current_user`` when importable
    (so JWT auth is enforced in production); falls back to
    ``_resolve_current_user`` (which is monkeypatchable in tests).
    """
    try:
        from shared.auth.dependencies import get_current_user  # noqa: PLC0415

        return Depends(get_current_user)
    except Exception:  # noqa: BLE001
        return Depends(_resolve_current_user)


# ---------- Endpoints ------------------------------------------------------


@router.post("/recommend")
async def recommend(
    request: Request,  # noqa: ARG001 — kept for parity with shared deps
    body: FieldDataRequest,
    user: Any = _current_user_dep(),  # noqa: B008 — FastAPI Depends
) -> dict[str, Any]:
    """Generate a governed recommendation for the given field telemetry."""
    advisor = await _get_advisor()
    field = FieldContext(**body.model_dump())
    recommendation = await advisor.generate_recommendation(field)
    recommendation["generated_at"] = datetime.now(UTC).isoformat()

    if recommendation.get("requires_approval"):
        decision_id = str(uuid.uuid4())
        recommendation["decision_id"] = decision_id
        # Tenant-scope the stored decision so approve/reject can verify.
        recommendation["tenant_id"] = getattr(user, "tenant_id", None) or (
            user.get("tenant_id") if isinstance(user, dict) else None
        )
        await _save_pending(decision_id, recommendation)

    return recommendation


def _check_tenant_match(decision: dict[str, Any], user: Any) -> None:
    expected = decision.get("tenant_id")
    actual = getattr(user, "tenant_id", None) or (
        user.get("tenant_id") if isinstance(user, dict) else None
    )
    if expected and actual and expected != actual:
        raise HTTPException(status_code=403, detail="tenant mismatch")


@router.post("/approve")
async def approve_decision(
    body: ApproveRequest,
    user: Any = _current_user_dep(),  # noqa: B008
) -> dict[str, Any]:
    """Approve a pending decision; optionally override the action."""
    decision = await _load_pending(body.decision_id)
    if decision is None:
        raise HTTPException(status_code=404, detail="decision not found or expired")
    _check_tenant_match(decision, user)

    advisor = await _get_advisor()
    approver = getattr(user, "id", None) or (
        user.get("id") if isinstance(user, dict) else "human"
    )
    approved = advisor.governance.approve(
        decision, approved_by=str(approver), modified_action=body.modified_action
    )
    await _delete_pending(body.decision_id)
    return {"status": "approved", "decision": approved}


@router.post("/reject")
async def reject_decision(
    body: RejectRequest,
    user: Any = _current_user_dep(),  # noqa: B008
) -> dict[str, Any]:
    """Reject a pending decision."""
    decision = await _load_pending(body.decision_id)
    if decision is None:
        raise HTTPException(status_code=404, detail="decision not found or expired")
    _check_tenant_match(decision, user)

    advisor = await _get_advisor()
    rejecter = getattr(user, "id", None) or (
        user.get("id") if isinstance(user, dict) else "human"
    )
    rejected = advisor.governance.reject(
        decision, rejected_by=str(rejecter), reason=body.reason
    )
    await _delete_pending(body.decision_id)
    return {"status": "rejected", "decision": rejected}


@router.post("/feedback")
async def submit_feedback(
    body: FeedbackRequest,
    user: Any = _current_user_dep(),  # noqa: B008, ARG001 — kept for auth & future tenant scoping
) -> dict[str, Any]:
    """Record outcome of a previously-issued decision.

    The crop / region / action are looked up from the stored pending decision
    when available; otherwise we fall back to ``"unknown"`` so the call still
    publishes an event that downstream services can correlate by decision_id.
    """
    advisor = await _get_advisor()
    decision = await _load_pending(body.decision_id) or {}
    field_ctx = decision.get("field_context", {}) if isinstance(decision, dict) else {}
    await advisor.record_feedback(
        decision_id=body.decision_id,
        result=body.result,
        crop=field_ctx.get("crop", "unknown"),
        region=field_ctx.get("region", "unknown"),
        action=decision.get("action", "unknown") if isinstance(decision, dict) else "unknown",
    )
    return {"status": "feedback_recorded"}


# ---------- Shutdown hook -------------------------------------------------


async def shutdown_advisor() -> None:
    """Best-effort teardown — invoked by main.py at shutdown."""
    global _advisor, _feedback, _kg_client, _redis_singleton, _redis_unavailable
    if _kg_client is not None:
        try:
            await _kg_client.close()
        except Exception:  # noqa: BLE001
            pass
    if _feedback is not None:
        try:
            await _feedback.close()
        except Exception:  # noqa: BLE001
            pass
    if _redis_singleton is not None:
        try:
            await _redis_singleton.aclose()
        except Exception:  # noqa: BLE001
            pass
    _advisor = None
    _feedback = None
    _kg_client = None
    _redis_singleton = None
    _redis_unavailable = False
