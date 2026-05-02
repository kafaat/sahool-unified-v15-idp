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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v2", tags=["advisor-v2"])

# Pending-decision Redis key prefix and TTL (24h).
_PENDING_KEY_PREFIX = "advisor:pending"
_PENDING_TTL_SECONDS = 24 * 3600

# In-memory fallback for pending decisions.
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


async def _redis_client():  # type: ignore[no-untyped-def]
    """Return a connected redis.asyncio client, or ``None`` if unavailable."""
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        return None
    try:
        import redis.asyncio as aioredis  # noqa: PLC0415
    except ImportError:
        return None
    try:
        client = aioredis.from_url(redis_url, decode_responses=True, socket_timeout=5)
        await client.ping()
        return client
    except Exception as exc:  # noqa: BLE001
        logger.warning("advisor.redis_unavailable", extra={"error": str(exc)})
        return None


async def _save_pending(decision_id: str, decision: dict[str, Any]) -> None:
    client = await _redis_client()
    if client is not None:
        try:
            await client.set(
                f"{_PENDING_KEY_PREFIX}:{decision_id}",
                json.dumps(decision),
                ex=_PENDING_TTL_SECONDS,
            )
            return
        except Exception as exc:  # noqa: BLE001
            logger.warning("advisor.pending_save_failed", extra={"error": str(exc)})
    _pending_memory[decision_id] = decision


async def _load_pending(decision_id: str) -> dict[str, Any] | None:
    client = await _redis_client()
    if client is not None:
        try:
            raw = await client.get(f"{_PENDING_KEY_PREFIX}:{decision_id}")
            if raw:
                return json.loads(raw)
        except Exception as exc:  # noqa: BLE001
            logger.warning("advisor.pending_load_failed", extra={"error": str(exc)})
    return _pending_memory.get(decision_id)


async def _delete_pending(decision_id: str) -> None:
    client = await _redis_client()
    if client is not None:
        try:
            await client.delete(f"{_PENDING_KEY_PREFIX}:{decision_id}")
        except Exception as exc:  # noqa: BLE001
            logger.warning("advisor.pending_delete_failed", extra={"error": str(exc)})
    _pending_memory.pop(decision_id, None)


# ---------- Embedding function (vLLM with deterministic fallback) ---------


async def _vllm_embedding(text: str) -> list[float]:
    """Embed ``text`` via vLLM. On failure return a deterministic fallback.

    The fallback uses SHA-256 to derive a stable 384-dim float vector — this
    keeps the system testable end-to-end without an embedding service.
    """
    import httpx  # noqa: PLC0415

    vllm_url = os.getenv("VLLM_BASE_URL", "http://vllm-deepseek:8270/v1")
    vllm_model = os.getenv("VLLM_EMBEDDING_MODEL", "meta-llama/Llama-3-8b-Instruct")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{vllm_url}/embeddings",
                json={"model": vllm_model, "input": text},
            )
            if resp.status_code == 200:
                data = resp.json()
                return data["data"][0]["embedding"]
    except Exception as exc:  # noqa: BLE001
        logger.warning("advisor.vllm_embedding_failed", extra={"error": str(exc)})

    # Deterministic fallback — SHA-256 expanded to 384 floats in [-1, 1).
    import hashlib  # noqa: PLC0415

    digest = hashlib.sha256(text.encode("utf-8")).digest()
    expanded = (digest * ((384 // len(digest)) + 1))[:384]
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


def _current_user_dep() -> Any:
    """Resolve the shared ``get_current_user`` dependency lazily.

    Importing it at module load time would couple this router to the
    shared auth machinery in test environments where it isn't installed.
    """
    try:
        from shared.auth.dependencies import get_current_user  # noqa: PLC0415

        return Depends(get_current_user)
    except Exception:  # noqa: BLE001
        async def _no_auth() -> dict[str, Any]:
            return {"id": "anonymous", "tenant_id": "default"}

        return Depends(_no_auth)


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
    global _advisor, _feedback, _kg_client
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
    _advisor = None
    _feedback = None
    _kg_client = None
