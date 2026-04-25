# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Smoke tests for agri-taxonomy-service Phase-4 wiring (ADR-012)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture()
def client() -> TestClient:
    # ``TestClient`` as a context manager runs the lifespan, which
    # seeds the in-memory store and cuts the initial release.
    with TestClient(app) as c:
        yield c


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
    assert body["checks"]["taxonomy_store"] is True
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
def test_version_returns_seeded_release(client: TestClient) -> None:
    resp = client.get("/api/v1/taxonomy/version")
    assert resp.status_code == 200
    body = resp.json()
    # The seed bump in lifespan is "minor" from 0.0.0 → 0.1.0.
    assert body["semver"] == "0.1.0"
    assert len(body["checksum_sha256"]) == 64


@pytest.mark.smoke
def test_list_nodes_returns_seeded_data(client: TestClient) -> None:
    resp = client.get("/api/v1/taxonomy/nodes?kind=crop")
    assert resp.status_code == 200
    body = resp.json()
    assert any(any(s["label"].lower() == "wheat" for s in node["synonyms"]) for node in body)


@pytest.mark.smoke
def test_get_node_404_for_unknown_uuid(client: TestClient) -> None:
    resp = client.get("/api/v1/taxonomy/nodes/00000000-0000-4000-8000-000000000000")
    assert resp.status_code == 404


@pytest.mark.smoke
def test_search_finds_arabic_label(client: TestClient) -> None:
    resp = client.get("/api/v1/taxonomy/search", params={"q": "قمح"})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) >= 1
    assert any(any(s["language"] == "ar" and "قمح" in s["label"] for s in node["synonyms"]) for node in body)


@pytest.mark.smoke
def test_forbidden_endpoint_flags_paraquat(client: TestClient) -> None:
    resp = client.get("/api/v1/taxonomy/fertilizers/44444444-4444-4444-8444-444444444444/forbidden")
    assert resp.status_code == 200
    body = resp.json()
    assert body["forbidden"] is True
    assert body["reason_en"]
    assert body["reason_ar"]


@pytest.mark.smoke
def test_forbidden_endpoint_does_not_flag_urea(client: TestClient) -> None:
    resp = client.get("/api/v1/taxonomy/fertilizers/55555555-5555-4555-8555-555555555555/forbidden")
    assert resp.status_code == 200
    assert resp.json()["forbidden"] is False


@pytest.mark.smoke
def test_publish_release_rejects_when_no_pending(client: TestClient) -> None:
    """Lifespan already drained the seeded staging area, so a second
    release with nothing pending must be rejected with 409.
    """

    resp = client.post("/api/v1/taxonomy/releases", json={"bump": "patch"})
    assert resp.status_code == 409
    assert "no staged" in resp.json()["detail"].lower()
