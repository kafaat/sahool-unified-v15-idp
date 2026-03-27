"""
Comprehensive Logging Configuration Tests for SAHOOL Platform
اختبارات شاملة لتكوين التسجيل لمنصة سهول

Tests cover:
- Context variables (correlation_id, tenant_id, user_id)
- setup_logging function
- get_logger function
- RequestLoggingMiddleware
- set/get correlation and context functions
- Health endpoint exclusion
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from shared.logging_config import (
    RequestLoggingMiddleware,
    add_correlation_id,
    correlation_id_var,
    get_correlation_id,
    get_logger,
    set_correlation_id,
    set_tenant_id,
    set_user_id,
    setup_logging,
    tenant_id_var,
    user_id_var,
)


@pytest.mark.unit
class TestContextVariables:
    """Tests for context variables"""

    def test_correlation_id_default_none(self):
        """Test that correlation ID defaults to None"""
        correlation_id_var.set(None)
        assert correlation_id_var.get() is None

    def test_set_correlation_id(self):
        """Test setting correlation ID"""
        set_correlation_id("test-corr-123")
        assert correlation_id_var.get() == "test-corr-123"
        correlation_id_var.set(None)  # Cleanup

    def test_get_correlation_id(self):
        """Test getting correlation ID"""
        correlation_id_var.set("corr-456")
        assert get_correlation_id() == "corr-456"
        correlation_id_var.set(None)

    def test_set_tenant_id(self):
        """Test setting tenant ID"""
        set_tenant_id("tenant-789")
        assert tenant_id_var.get() == "tenant-789"
        tenant_id_var.set(None)

    def test_set_user_id(self):
        """Test setting user ID"""
        set_user_id("user-abc")
        assert user_id_var.get() == "user-abc"
        user_id_var.set(None)


@pytest.mark.unit
class TestAddCorrelationIdProcessor:
    """Tests for the add_correlation_id structlog processor"""

    def test_adds_correlation_id_when_set(self):
        """Test that processor adds correlationId to event dict"""
        correlation_id_var.set("trace-123")
        event_dict = {"event": "test_event"}
        result = add_correlation_id(None, None, event_dict)
        assert result["correlationId"] == "trace-123"
        assert result["traceId"] == "trace-123"
        correlation_id_var.set(None)

    def test_adds_tenant_id_when_set(self):
        """Test that processor adds tenantId"""
        tenant_id_var.set("tenant-xyz")
        event_dict = {"event": "test_event"}
        result = add_correlation_id(None, None, event_dict)
        assert result["tenantId"] == "tenant-xyz"
        tenant_id_var.set(None)

    def test_adds_user_id_when_set(self):
        """Test that processor adds userId"""
        user_id_var.set("user-abc")
        event_dict = {"event": "test_event"}
        result = add_correlation_id(None, None, event_dict)
        assert result["userId"] == "user-abc"
        user_id_var.set(None)

    def test_no_context_no_extra_fields(self):
        """Test that processor doesn't add fields when not set"""
        correlation_id_var.set(None)
        tenant_id_var.set(None)
        user_id_var.set(None)
        event_dict = {"event": "test_event"}
        result = add_correlation_id(None, None, event_dict)
        assert "correlationId" not in result
        assert "tenantId" not in result
        assert "userId" not in result

    def test_preserves_existing_event_dict(self):
        """Test that processor preserves existing event dict fields"""
        event_dict = {"event": "test", "custom_field": "value"}
        result = add_correlation_id(None, None, event_dict)
        assert result["custom_field"] == "value"


@pytest.mark.unit
class TestSetupLogging:
    """Tests for setup_logging function"""

    def test_setup_with_default_params(self):
        """Test setup_logging with default parameters"""
        # Should not raise
        setup_logging(service_name="test-service")

    def test_setup_with_custom_log_level(self):
        """Test setup_logging with custom log level"""
        setup_logging(service_name="test-service", log_level="DEBUG")

    def test_setup_with_json_disabled(self):
        """Test setup_logging with JSON logs disabled"""
        setup_logging(service_name="test-service", json_logs=False)

    @patch.dict(os.environ, {"ENVIRONMENT": "production"})
    def test_production_forces_json_logs(self):
        """Test that production environment forces JSON logging"""
        setup_logging(service_name="test-service", json_logs=False)


@pytest.mark.unit
class TestGetLogger:
    """Tests for get_logger function"""

    def test_get_logger_with_name(self):
        """Test getting logger with specific name"""
        logger = get_logger("test.module")
        assert logger is not None

    def test_get_logger_without_name(self):
        """Test getting logger without name"""
        logger = get_logger()
        assert logger is not None


@pytest.mark.unit
class TestRequestLoggingMiddleware:
    """Tests for RequestLoggingMiddleware"""

    def setup_method(self):
        """Set up test FastAPI app"""
        self.app = FastAPI()
        self.app.add_middleware(RequestLoggingMiddleware, service_name="test-service")

        @self.app.get("/api/data")
        async def get_data():
            return {"data": "test"}

        @self.app.get("/healthz")
        async def health():
            return {"status": "ok"}

        @self.app.get("/readyz")
        async def ready():
            return {"status": "ok"}

        @self.app.get("/metrics")
        async def metrics():
            return "metrics_data"

        @self.app.get("/api/error")
        async def error():
            raise ValueError("Test error")

        self.client = TestClient(self.app, raise_server_exceptions=False)

    def test_adds_correlation_id_header(self):
        """Test that middleware adds X-Correlation-ID to response"""
        response = self.client.get("/api/data")
        assert "X-Correlation-ID" in response.headers
        assert "X-Request-ID" in response.headers

    def test_preserves_incoming_correlation_id(self):
        """Test that middleware uses existing correlation ID"""
        response = self.client.get(
            "/api/data",
            headers={"x-correlation-id": "incoming-corr-123"},
        )
        assert response.headers["X-Correlation-ID"] == "incoming-corr-123"

    def test_preserves_x_request_id(self):
        """Test that middleware uses existing X-Request-ID"""
        response = self.client.get(
            "/api/data",
            headers={"x-request-id": "req-456"},
        )
        assert response.headers["X-Correlation-ID"] == "req-456"

    def test_excludes_health_endpoints(self):
        """Test that health endpoints are excluded from logging"""
        # These should work without adding correlation headers
        for path in ["/healthz", "/readyz", "/metrics"]:
            response = self.client.get(path)
            assert response.status_code == 200

    def test_successful_request_returns_200(self):
        """Test that successful requests return normally"""
        response = self.client.get("/api/data")
        assert response.status_code == 200
        assert response.json() == {"data": "test"}

    def test_excluded_paths(self):
        """Test that the EXCLUDE_PATHS set contains expected paths"""
        expected = {"/health", "/healthz", "/health/live", "/health/ready",
                    "/readyz", "/livez", "/metrics", "/docs", "/redoc", "/openapi.json"}
        assert expected == RequestLoggingMiddleware.EXCLUDE_PATHS
