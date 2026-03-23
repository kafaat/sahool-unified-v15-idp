"""
Tests for SAHOOL Unified Request Context
==========================================
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from shared.stability.context import (
    RequestContext,
    UnifiedContextMiddleware,
    _request_context,
    clear_context,
    get_optional_context,
    get_request_context,
    set_context_for_worker,
)


class TestRequestContext:
    """Tests for the RequestContext dataclass."""

    def test_create_basic_context(self):
        ctx = RequestContext(
            correlation_id="corr-123",
            request_id="req-456",
            tenant_id="tenant-789",
            user_id="user-001",
            service_name="test-service",
        )
        assert ctx.correlation_id == "corr-123"
        assert ctx.request_id == "req-456"
        assert ctx.tenant_id == "tenant-789"
        assert ctx.user_id == "user-001"
        assert ctx.service_name == "test-service"

    def test_to_propagation_headers(self):
        ctx = RequestContext(
            correlation_id="corr-123",
            request_id="req-456",
            tenant_id="tenant-789",
            user_id="user-001",
            trace_id="abc123",
            span_id="def456",
        )
        headers = ctx.to_propagation_headers()

        assert headers["X-Correlation-ID"] == "corr-123"
        assert headers["X-Request-ID"] == "req-456"
        assert headers["X-Tenant-ID"] == "tenant-789"
        assert headers["X-User-ID"] == "user-001"
        assert headers["traceparent"] == "00-abc123-def456-01"

    def test_to_propagation_headers_minimal(self):
        ctx = RequestContext(
            correlation_id="corr-123",
            request_id="req-456",
        )
        headers = ctx.to_propagation_headers()

        assert headers["X-Correlation-ID"] == "corr-123"
        assert "X-Tenant-ID" not in headers
        assert "X-User-ID" not in headers
        assert "traceparent" not in headers

    def test_to_nats_headers(self):
        ctx = RequestContext(
            correlation_id="corr-123",
            tenant_id="tenant-789",
            trace_id="abc123",
            span_id="def456",
        )
        headers = ctx.to_nats_headers()

        assert headers["X-Correlation-ID"] == "corr-123"
        assert headers["X-Tenant-ID"] == "tenant-789"
        assert headers["traceparent"] == "00-abc123-def456-01"

    def test_enrich_event(self):
        ctx = RequestContext(
            correlation_id="corr-123",
            tenant_id="tenant-789",
            trace_id="trace-abc",
        )

        # Mock event with attributes
        event = MagicMock()
        event.correlation_id = None
        event.tenant_id_header = None
        event.trace_id = None
        event.span_id = None

        ctx.enrich_event(event)

        assert event.correlation_id == "corr-123"
        assert event.tenant_id_header == "tenant-789"
        assert event.trace_id == "trace-abc"

    def test_enrich_event_does_not_overwrite(self):
        ctx = RequestContext(
            correlation_id="corr-123",
            tenant_id="tenant-789",
        )

        event = MagicMock()
        event.correlation_id = "existing-corr"
        event.tenant_id_header = "existing-tenant"

        ctx.enrich_event(event)

        # Should not overwrite existing values
        assert event.correlation_id == "existing-corr"
        assert event.tenant_id_header == "existing-tenant"

    def test_to_log_context(self):
        ctx = RequestContext(
            correlation_id="corr-123",
            request_id="req-456",
            tenant_id="tenant-789",
            user_id="user-001",
            trace_id="trace-abc",
            service_name="test-service",
        )
        log_ctx = ctx.to_log_context()

        assert log_ctx["correlationId"] == "corr-123"
        assert log_ctx["tenantId"] == "tenant-789"
        assert log_ctx["userId"] == "user-001"
        assert log_ctx["traceId"] == "trace-abc"
        assert log_ctx["service"] == "test-service"

    def test_has_role(self):
        ctx = RequestContext(roles=["admin", "farmer"])
        assert ctx.has_role("admin") is True
        assert ctx.has_role("farmer") is True
        assert ctx.has_role("superadmin") is False

    def test_has_role_empty(self):
        ctx = RequestContext()
        assert ctx.has_role("admin") is False

    def test_traceparent_in_headers_when_set(self):
        ctx = RequestContext(
            correlation_id="corr-123",
            request_id="req-456",
            traceparent="00-abc-def-01",
        )
        headers = ctx.to_propagation_headers()
        assert headers["traceparent"] == "00-abc-def-01"


class TestContextFunctions:
    """Tests for context getter/setter functions."""

    def setup_method(self):
        """Clear context before each test."""
        _request_context.set(None)

    def test_get_request_context_raises_when_not_set(self):
        with pytest.raises(RuntimeError, match="Request context not available"):
            get_request_context()

    def test_get_optional_context_returns_none(self):
        assert get_optional_context() is None

    def test_set_context_for_worker(self):
        ctx = set_context_for_worker(
            correlation_id="worker-corr",
            tenant_id="tenant-1",
            service_name="worker-service",
        )
        assert ctx.correlation_id == "worker-corr"
        assert ctx.tenant_id == "tenant-1"

        # Should be accessible via get_request_context
        retrieved = get_request_context()
        assert retrieved.correlation_id == "worker-corr"

    def test_clear_context(self):
        set_context_for_worker(correlation_id="corr-123")
        assert get_optional_context() is not None

        clear_context()
        assert get_optional_context() is None

    def teardown_method(self):
        _request_context.set(None)
