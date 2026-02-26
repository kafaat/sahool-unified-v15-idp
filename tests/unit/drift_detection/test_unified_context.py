"""Tests for unified request context middleware."""

from __future__ import annotations

import pytest

from shared.middleware.unified_request_context import (
    RequestContext,
    get_optional_request_context,
)


class TestRequestContext:
    """Tests for RequestContext dataclass."""

    def test_create_minimal(self):
        ctx = RequestContext(
            request_id="req-123",
            correlation_id="corr-456",
        )
        assert ctx.request_id == "req-123"
        assert ctx.correlation_id == "corr-456"
        assert ctx.tenant_id is None

    def test_create_full(self):
        ctx = RequestContext(
            request_id="req-123",
            correlation_id="corr-456",
            tenant_id="tenant-001",
            user_id="user-789",
            roles=["admin", "farmer"],
            trace_id="abc123def456",
            span_id="1234567890abcdef",
            environment="production",
        )
        assert ctx.tenant_id == "tenant-001"
        assert ctx.user_id == "user-789"
        assert "admin" in ctx.roles

    def test_immutable(self):
        ctx = RequestContext(
            request_id="req-123",
            correlation_id="corr-456",
        )
        with pytest.raises(AttributeError):
            ctx.request_id = "new-id"

    def test_to_headers(self):
        ctx = RequestContext(
            request_id="req-123",
            correlation_id="corr-456",
            tenant_id="tenant-001",
        )
        headers = ctx.to_headers()
        assert headers["X-Request-ID"] == "req-123"
        assert headers["X-Correlation-ID"] == "corr-456"
        assert headers["X-Tenant-ID"] == "tenant-001"

    def test_to_headers_without_tenant(self):
        ctx = RequestContext(
            request_id="req-123",
            correlation_id="corr-456",
        )
        headers = ctx.to_headers()
        assert "X-Tenant-ID" not in headers

    def test_to_headers_with_trace(self):
        ctx = RequestContext(
            request_id="req-123",
            correlation_id="corr-456",
            trace_id="abcd1234efgh5678",
            span_id="1234567890abcdef",
        )
        headers = ctx.to_headers()
        assert "traceparent" in headers
        assert "abcd1234efgh5678" in headers["traceparent"]

    def test_to_log_context(self):
        ctx = RequestContext(
            request_id="req-123",
            correlation_id="corr-456",
            tenant_id="tenant-001",
            user_id="user-789",
            trace_id="trace-abc",
        )
        log_ctx = ctx.to_log_context()
        assert log_ctx["request_id"] == "req-123"
        assert log_ctx["correlation_id"] == "corr-456"
        assert log_ctx["tenant_id"] == "tenant-001"
        assert log_ctx["user_id"] == "user-789"
        assert log_ctx["trace_id"] == "trace-abc"

    def test_to_log_context_minimal(self):
        ctx = RequestContext(
            request_id="req-123",
            correlation_id="corr-456",
        )
        log_ctx = ctx.to_log_context()
        assert "tenant_id" not in log_ctx
        assert "user_id" not in log_ctx


class TestContextVar:
    """Tests for context variable management."""

    def test_no_context_returns_none(self):
        ctx = get_optional_request_context()
        assert ctx is None
