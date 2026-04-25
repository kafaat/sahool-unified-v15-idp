# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""``POST /api/v1/prescription/check`` route (ADR-013)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from shared.prescription_safety import PrescriptionGateway, PrescriptionRequest

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic schemas (wire format)
# ---------------------------------------------------------------------------


class PrescriptionRequestIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: str = Field(..., min_length=1)
    prescription_id: str = Field(..., min_length=1)
    prescription_type: str = Field(..., pattern="^(pesticide|fertilizer|irrigation)$")
    field_id: str = Field(..., min_length=1)
    crop: str = Field(..., min_length=1)
    product: str = Field(..., min_length=1)
    rate: float = Field(..., ge=0.0)
    rate_unit: str = Field(..., min_length=1)
    target: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReasonOut(BaseModel):
    code: str
    message_en: str
    message_ar: str
    severity: str
    source_checker: str


class EvidenceOut(BaseModel):
    checker: str
    payload: dict[str, Any]
    checked_at: str


class DecisionOut(BaseModel):
    decision: str
    reasons: list[ReasonOut]
    evidence: list[EvidenceOut]
    decided_at: str
    correlation_id: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post("/check", response_model=DecisionOut)
async def check_prescription(
    body: PrescriptionRequestIn,
    request: Request,
    x_correlation_id: str | None = Header(default=None, alias="X-Correlation-Id"),
) -> DecisionOut:
    gateway: PrescriptionGateway | None = getattr(request.app.state, "gateway", None)
    if gateway is None:
        raise HTTPException(status_code=503, detail="Gateway not initialised")

    decision = await gateway.check(
        PrescriptionRequest(
            tenant_id=body.tenant_id,
            prescription_id=body.prescription_id,
            prescription_type=body.prescription_type,
            field_id=body.field_id,
            crop=body.crop,
            product=body.product,
            rate=body.rate,
            rate_unit=body.rate_unit,
            target=body.target,
            metadata=body.metadata,
        ),
        correlation_id=x_correlation_id,
    )

    return DecisionOut(
        decision=decision.decision.value,
        reasons=[
            ReasonOut(
                code=r.code,
                message_en=r.message_en,
                message_ar=r.message_ar,
                severity=r.severity,
                source_checker=r.source_checker,
            )
            for r in decision.reasons
        ],
        evidence=[
            EvidenceOut(
                checker=e.checker,
                payload=e.payload,
                checked_at=e.checked_at.isoformat(),
            )
            for e in decision.evidence
        ],
        decided_at=decision.decided_at.isoformat(),
        correlation_id=decision.correlation_id,
    )


@router.get("/checkers")
async def list_checkers(request: Request) -> dict[str, list[str]]:
    """Introspect the configured checker pipeline."""

    gateway: PrescriptionGateway | None = getattr(request.app.state, "gateway", None)
    if gateway is None:
        raise HTTPException(status_code=503, detail="Gateway not initialised")
    return {"checkers": [getattr(c, "name", c.__class__.__name__) for c in gateway.checkers]}
