# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Smoke + decision-flow tests for prescription-safety-gateway (ADR-013)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture()
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


def _payload(**overrides: object) -> dict:
    base: dict = {
        "tenant_id": "farm-01",
        "prescription_id": "rx-001",
        "prescription_type": "fertilizer",
        "field_id": "FIELD-003",
        "crop": "wheat",
        "product": "Urea 46%",
        "rate": 50.0,
        "rate_unit": "kg/ha",
    }
    base.update(overrides)
    return base


@pytest.mark.smoke
def test_healthz(client: TestClient) -> None:
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["service"] == "prescription-safety-gateway"


@pytest.mark.smoke
def test_readyz(client: TestClient) -> None:
    resp = client.get("/readyz")
    assert resp.status_code == 200
    assert resp.json()["checks"]["gateway_configured"] is True


@pytest.mark.smoke
def test_root_advertises_adr(client: TestClient) -> None:
    body = client.get("/").json()
    assert body["adr"] == "ADR-013"
    assert body["layer"] == "decision"


@pytest.mark.smoke
def test_metrics(client: TestClient) -> None:
    assert client.get("/metrics").status_code == 200


@pytest.mark.smoke
def test_list_checkers_returns_pipeline(client: TestClient) -> None:
    body = client.get("/api/v1/prescription/checkers").json()
    assert body["checkers"] == [
        "forbidden_substance",
        "dosage_tolerance",
        "pesticide_compliance",
    ]


@pytest.mark.smoke
def test_check_approved_for_in_window_dose(client: TestClient) -> None:
    resp = client.post("/api/v1/prescription/check", json=_payload(rate=50.0))
    assert resp.status_code == 200
    body = resp.json()
    assert body["decision"] == "APPROVED"
    assert body["reasons"] == []
    assert {e["checker"] for e in body["evidence"]} >= {
        "forbidden_substance",
        "dosage_tolerance",
    }


@pytest.mark.smoke
def test_check_review_for_unknown_crop_product(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/prescription/check",
        json=_payload(crop="quinoa", product="MysteryMix"),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["decision"] == "REVIEW"
    assert any(r["code"] == "UNCHECKED_DOSAGE_NO_REFERENCE" for r in body["reasons"])


@pytest.mark.smoke
def test_check_rejected_for_extreme_dose(client: TestClient) -> None:
    resp = client.post("/api/v1/prescription/check", json=_payload(rate=500.0))
    assert resp.status_code == 200
    body = resp.json()
    assert body["decision"] == "REJECTED"
    assert any(r["code"] == "DOSAGE_HARD_LIMIT_EXCEEDED" for r in body["reasons"])


@pytest.mark.smoke
def test_check_rejects_invalid_prescription_type(client: TestClient) -> None:
    resp = client.post("/api/v1/prescription/check", json=_payload(prescription_type="cosmic"))
    assert resp.status_code == 422


@pytest.mark.smoke
def test_correlation_id_passthrough(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/prescription/check",
        json=_payload(),
        headers={"X-Correlation-Id": "trace-abc"},
    )
    assert resp.json()["correlation_id"] == "trace-abc"
