# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Smoke tests for agri-taxonomy-service scaffold (ADR-012)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.mark.smoke
def test_healthz_returns_ok(client: TestClient) -> None:
    resp = client.get("/healthz")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "agri-taxonomy-service"


@pytest.mark.smoke
def test_readyz_reports_checks(client: TestClient) -> None:
    resp = client.get("/readyz")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ready"
    assert "knowledge_graph" in body["checks"]
    assert "nats" in body["checks"]


@pytest.mark.smoke
def test_root_advertises_adr(client: TestClient) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["adr"] == "ADR-012"
    assert body["layer"] == "intelligence"


@pytest.mark.smoke
def test_metrics_endpoint_serves_prometheus(client: TestClient) -> None:
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "text/plain" in resp.headers["content-type"]


@pytest.mark.smoke
@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/taxonomy/version",
        "/api/v1/taxonomy/nodes/00000000-0000-4000-8000-000000000000",
        "/api/v1/taxonomy/nodes",
        "/api/v1/taxonomy/search?q=wheat",
        "/api/v1/taxonomy/fertilizers/00000000-0000-4000-8000-000000000000/forbidden",
    ],
)
def test_phase4_routes_return_501(client: TestClient, path: str) -> None:
    """All domain routes are scaffolded but not implemented yet."""

    resp = client.get(path)
    assert resp.status_code == 501
    assert "ADR-012" in resp.json()["detail"]


@pytest.mark.smoke
def test_publish_release_returns_501(client: TestClient) -> None:
    resp = client.post("/api/v1/taxonomy/releases")
    assert resp.status_code == 501
