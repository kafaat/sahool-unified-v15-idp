"""Tests for shared.libs.simulated_data helper."""

from __future__ import annotations

import pytest
from fastapi import HTTPException, Response

from shared.libs.simulated_data import guard_simulated_response, mark_simulated


def test_guard_passthrough_in_development(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.delenv("ALLOW_SIMULATED_DATA", raising=False)
    # Should not raise in dev
    guard_simulated_response("test-service", "endpoint")


def test_guard_passthrough_in_test_env(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.delenv("ALLOW_SIMULATED_DATA", raising=False)
    guard_simulated_response("test-service", "endpoint")


def test_guard_blocks_in_production(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("ALLOW_SIMULATED_DATA", raising=False)
    with pytest.raises(HTTPException) as exc:
        guard_simulated_response("test-service", "endpoint")
    assert exc.value.status_code == 503
    assert exc.value.detail["service"] == "test-service"
    assert exc.value.detail["endpoint"] == "endpoint"


def test_guard_blocks_in_staging(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.delenv("ALLOW_SIMULATED_DATA", raising=False)
    with pytest.raises(HTTPException) as exc:
        guard_simulated_response("test-service", "endpoint")
    assert exc.value.status_code == 503


def test_guard_allows_opt_in_production(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("ALLOW_SIMULATED_DATA", "true")
    # No raise expected
    guard_simulated_response("test-service", "endpoint")


@pytest.mark.parametrize("flag_value", ["1", "true", "TRUE", "yes", "on"])
def test_guard_accepts_truthy_flag_variants(monkeypatch, flag_value):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("ALLOW_SIMULATED_DATA", flag_value)
    guard_simulated_response("test-service", "endpoint")


def test_guard_rejects_falsy_flag(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("ALLOW_SIMULATED_DATA", "false")
    with pytest.raises(HTTPException):
        guard_simulated_response("test-service", "endpoint")


def test_mark_sets_headers():
    response = Response()
    mark_simulated(response, source="random_sampling")
    assert response.headers["X-Data-Source"] == "simulated"
    assert response.headers["X-Data-Source-Detail"] == "random_sampling"
    assert "199 sahool" in response.headers["Warning"]


def test_mark_preserves_existing_warning():
    response = Response()
    response.headers["Warning"] = '299 - "existing"'
    mark_simulated(response, source="mock_list", message="custom warn")
    warning = response.headers["Warning"]
    assert "existing" in warning
    assert "custom warn" in warning


def test_mark_custom_message():
    response = Response()
    mark_simulated(response, source="external_mock", message="fixture data")
    assert response.headers["X-Data-Source-Detail"] == "external_mock"
    assert "fixture data" in response.headers["Warning"]
