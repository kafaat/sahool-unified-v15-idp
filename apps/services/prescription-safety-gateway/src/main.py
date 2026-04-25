# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""prescription-safety-gateway — FastAPI entry point (ADR-013)."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from shared.prescription_safety import (
    DosageToleranceChecker,
    ForbiddenSubstanceChecker,
    PesticideComplianceCheckerAdapter,
    PrescriptionGateway,
    RateRange,
)

from .api.v1.prescription import router as prescription_router

SERVICE_NAME = os.getenv("SERVICE_NAME", "prescription-safety-gateway")
SERVICE_LAYER = os.getenv("SERVICE_LAYER", "decision")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "0.1.0")
GATEWAY_MODE = os.getenv("PRESCRIPTION_GATEWAY_MODE", "standalone")
FORBIDDEN_SUBSTANCES = os.getenv("FORBIDDEN_SUBSTANCES", "")

log = structlog.get_logger()


def build_gateway() -> PrescriptionGateway:
    """Construct the gateway from env. Pure factory so tests can override."""

    blocklist = [item for item in FORBIDDEN_SUBSTANCES.split(",") if item.strip()]
    return PrescriptionGateway(
        mode=GATEWAY_MODE,
        checkers=[
            ForbiddenSubstanceChecker.from_iterable(blocklist),
            # Phase 4.1 wires this table to agro-rules. Until then we ship a
            # tiny seed table so the endpoint is useful for smoke tests.
            DosageToleranceChecker(
                rates={
                    ("wheat", "urea 46%"): RateRange(40.0, 60.0, "kg/ha"),
                    ("wheat", "dap"): RateRange(80.0, 120.0, "kg/ha"),
                    ("date palm", "urea 46%"): RateRange(0.5, 2.0, "kg/tree"),
                }
            ),
            PesticideComplianceCheckerAdapter(),
        ],
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info(
        "service.startup",
        service=SERVICE_NAME,
        layer=SERVICE_LAYER,
        version=SERVICE_VERSION,
        mode=GATEWAY_MODE,
    )
    app.state.gateway = build_gateway()
    yield
    log.info("service.shutdown", service=SERVICE_NAME)


app = FastAPI(title=SERVICE_NAME, version=SERVICE_VERSION, lifespan=lifespan)
app.include_router(prescription_router, prefix="/api/v1/prescription", tags=["prescription"])


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME, "version": SERVICE_VERSION}


@app.get("/readyz")
def readyz() -> dict[str, object]:
    return {
        "status": "ready",
        "service": SERVICE_NAME,
        "checks": {
            "gateway_configured": getattr(app.state, "gateway", None) is not None,
        },
    }


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": SERVICE_NAME,
        "layer": SERVICE_LAYER,
        "version": SERVICE_VERSION,
        "adr": "ADR-013",
        "mode": GATEWAY_MODE,
    }
