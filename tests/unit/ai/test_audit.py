"""
Tests for AI Audit Module
==========================
اختبارات وحدة تدقيق الذكاء الاصطناعي

Comprehensive tests for audit logging, cost calculation, and event tracking.

Author: SAHOOL Platform Team
Updated: January 2026
"""

import uuid
from datetime import datetime

import pytest

from shared.ai.audit import (
    LLM_COSTS,
    AIAuditLogger,
    AuditEvent,
    AuditEventType,
    SafetyLevel,
    calculate_cost,
    get_audit_logger,
)

# ═══════════════════════════════════════════════════════════════════════════
# Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def audit_logger() -> AIAuditLogger:
    """Create a fresh audit logger for testing."""
    return AIAuditLogger(tenant_id="test-tenant")


@pytest.fixture
def sample_event() -> AuditEvent:
    """Create a sample audit event."""
    return AuditEvent(
        id=str(uuid.uuid4()),
        event_type=AuditEventType.AGENT_INVOCATION,
        timestamp=datetime.utcnow(),
        tenant_id="test-tenant",
        agent_id="test-agent",
        user_id="user-123",
        correlation_id=str(uuid.uuid4()),
        input_data={"prompt": "Test prompt"},
        output_data=None,
        latency_ms=None,
        token_count_input=100,
        token_count_output=None,
        model_name="claude-3-haiku",
        llm_provider="anthropic",
        cost_usd=None,
        safety_level=SafetyLevel.SAFE,
        metadata={"test": True},
    )


# ═══════════════════════════════════════════════════════════════════════════
# Test AuditEventType Enum
# ═══════════════════════════════════════════════════════════════════════════


class TestAuditEventType:
    """Tests for AuditEventType enum."""

    def test_event_types_exist(self):
        """Test that all expected event types exist."""
        assert AuditEventType.AGENT_INVOCATION
        assert AuditEventType.AGENT_RESPONSE
        assert AuditEventType.SAFETY_VIOLATION
        assert AuditEventType.AGENT_ERROR

    def test_event_type_values(self):
        """Test event type string values."""
        assert AuditEventType.AGENT_INVOCATION.value == "agent_invocation"
        assert AuditEventType.AGENT_RESPONSE.value == "agent_response"
        assert AuditEventType.SAFETY_VIOLATION.value == "safety_violation"


# ═══════════════════════════════════════════════════════════════════════════
# Test SafetyLevel Enum
# ═══════════════════════════════════════════════════════════════════════════


class TestSafetyLevel:
    """Tests for SafetyLevel enum."""

    def test_safety_levels_exist(self):
        """Test that all expected safety levels exist."""
        assert SafetyLevel.SAFE
        assert SafetyLevel.LOW_RISK
        assert SafetyLevel.MEDIUM_RISK
        assert SafetyLevel.HIGH_RISK
        assert SafetyLevel.BLOCKED

    def test_safety_level_values(self):
        """Test safety level string values."""
        assert SafetyLevel.SAFE.value == "safe"
        assert SafetyLevel.BLOCKED.value == "blocked"


# ═══════════════════════════════════════════════════════════════════════════
# Test AuditEvent Model
# ═══════════════════════════════════════════════════════════════════════════


class TestAuditEvent:
    """Tests for AuditEvent data model."""

    def test_audit_event_creation(self, sample_event: AuditEvent):
        """Test creating an audit event."""
        assert sample_event.event_type == AuditEventType.AGENT_INVOCATION
        assert sample_event.tenant_id == "test-tenant"
        assert sample_event.agent_id == "test-agent"
        assert sample_event.token_count_input == 100

    def test_audit_event_to_dict(self, sample_event: AuditEvent):
        """Test converting audit event to dictionary."""
        data = sample_event.to_dict()

        assert data["event_type"] == "agent_invocation"
        assert data["tenant_id"] == "test-tenant"
        assert data["agent_id"] == "test-agent"
        assert data["safety_level"] == "safe"
        assert "timestamp" in data

    def test_audit_event_minimal(self):
        """Test creating a minimal audit event."""
        event = AuditEvent(
            id=str(uuid.uuid4()),
            event_type=AuditEventType.AGENT_ERROR,
            timestamp=datetime.utcnow(),
            tenant_id="minimal-tenant",
        )

        assert event.agent_id is None
        assert event.user_id is None
        assert event.cost_usd is None


# ═══════════════════════════════════════════════════════════════════════════
# Test Cost Calculation
# ═══════════════════════════════════════════════════════════════════════════


class TestCostCalculation:
    """Tests for LLM cost calculation."""

    def test_calculate_cost_anthropic_haiku(self):
        """Test cost calculation for Anthropic Haiku."""
        cost = calculate_cost(
            provider="anthropic",
            model="claude-3-haiku",
            input_tokens=1000,
            output_tokens=500,
        )

        # Haiku: $0.00025/1K input, $0.00125/1K output
        expected = (1000 / 1000) * 0.00025 + (500 / 1000) * 0.00125
        assert abs(cost - expected) < 0.0001

    def test_calculate_cost_anthropic_opus(self):
        """Test cost calculation for Anthropic Opus."""
        cost = calculate_cost(
            provider="anthropic",
            model="claude-3-opus",
            input_tokens=1000,
            output_tokens=1000,
        )

        # Opus: $0.015/1K input, $0.075/1K output
        expected = (1000 / 1000) * 0.015 + (1000 / 1000) * 0.075
        assert abs(cost - expected) < 0.0001

    def test_calculate_cost_ollama_free(self):
        """Test cost calculation for Ollama (local, free)."""
        cost = calculate_cost(
            provider="ollama",
            model="codellama:7b",
            input_tokens=10000,
            output_tokens=5000,
        )

        assert cost == 0.0

    def test_calculate_cost_unknown_provider(self):
        """Test cost calculation for unknown provider."""
        cost = calculate_cost(
            provider="unknown-provider",
            model="unknown-model",
            input_tokens=1000,
            output_tokens=500,
        )

        # Should return 0 for unknown providers
        assert cost == 0.0

    def test_calculate_cost_unknown_model(self):
        """Test cost calculation for unknown model."""
        cost = calculate_cost(
            provider="anthropic",
            model="unknown-model",
            input_tokens=1000,
            output_tokens=500,
        )

        # Should return 0 for unknown models
        assert cost == 0.0

    def test_llm_costs_structure(self):
        """Test LLM_COSTS dictionary structure."""
        assert "anthropic" in LLM_COSTS
        assert "openai" in LLM_COSTS
        assert "ollama" in LLM_COSTS

        # Check Anthropic models
        assert "claude-3-opus" in LLM_COSTS["anthropic"]
        assert "claude-3-haiku" in LLM_COSTS["anthropic"]

        # Check cost keys
        assert "input" in LLM_COSTS["anthropic"]["claude-3-opus"]
        assert "output" in LLM_COSTS["anthropic"]["claude-3-opus"]


# ═══════════════════════════════════════════════════════════════════════════
# Test AIAuditLogger
# ═══════════════════════════════════════════════════════════════════════════


class TestAIAuditLogger:
    """Tests for AIAuditLogger class."""

    def test_logger_initialization(self, audit_logger: AIAuditLogger):
        """Test audit logger initialization."""
        assert audit_logger.tenant_id == "test-tenant"

    def test_log_agent_invocation(self, audit_logger: AIAuditLogger):
        """Test logging an agent invocation."""
        event = audit_logger.log_agent_invocation(
            agent_id="test-agent",
            input_data={"prompt": "Hello"},
            user_id="user-1",
        )

        assert event is not None
        assert event.event_type == AuditEventType.AGENT_INVOCATION
        assert event.agent_id == "test-agent"
        assert event.correlation_id is not None

    def test_log_agent_response(self, audit_logger: AIAuditLogger):
        """Test logging an agent response."""
        # First, log invocation
        invocation = audit_logger.log_agent_invocation(
            agent_id="test-agent",
            input_data={"prompt": "Hello"},
        )

        # Then, log response
        response = audit_logger.log_agent_response(
            correlation_id=invocation.correlation_id,
            output_data={"response": "Hi there"},
            latency_ms=150.5,
            token_count_input=10,
            token_count_output=15,
            model_name="claude-3-haiku",
            llm_provider="anthropic",
        )

        assert response is not None
        assert response.event_type == AuditEventType.AGENT_RESPONSE
        assert response.latency_ms == 150.5
        assert response.cost_usd is not None  # Cost should be calculated

    def test_log_safety_violation(self, audit_logger: AIAuditLogger):
        """Test logging a safety violation."""
        correlation_id = str(uuid.uuid4())

        event = audit_logger.log_safety_violation(
            correlation_id=correlation_id,
            violation_type="prompt_injection",
            severity=SafetyLevel.HIGH_RISK,
            details={"pattern": "ignore previous instructions"},
            agent_id="test-agent",
        )

        assert event is not None
        assert event.event_type == AuditEventType.SAFETY_VIOLATION
        assert event.safety_level == SafetyLevel.HIGH_RISK

    def test_get_summary(self, audit_logger: AIAuditLogger):
        """Test getting audit summary."""
        # Log some events
        audit_logger.log_agent_invocation(
            agent_id="test-agent",
            input_data={},
        )

        summary = audit_logger.get_summary()

        assert "total_events" in summary
        assert "total_cost_usd" in summary


# ═══════════════════════════════════════════════════════════════════════════
# Test Module Functions
# ═══════════════════════════════════════════════════════════════════════════


class TestModuleFunctions:
    """Tests for module-level functions."""

    def test_get_audit_logger_returns_logger(self):
        """Test that get_audit_logger returns a logger."""
        logger = get_audit_logger(tenant_id="test")

        assert logger is not None
        assert isinstance(logger, AIAuditLogger)


# ═══════════════════════════════════════════════════════════════════════════
# Test Edge Cases
# ═══════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_zero_tokens(self):
        """Test cost calculation with zero tokens."""
        cost = calculate_cost(
            provider="anthropic",
            model="claude-3-haiku",
            input_tokens=0,
            output_tokens=0,
        )
        assert cost == 0.0

    def test_large_token_count(self):
        """Test cost calculation with large token counts."""
        cost = calculate_cost(
            provider="anthropic",
            model="claude-3-opus",
            input_tokens=1_000_000,
            output_tokens=500_000,
        )

        # Should calculate correctly without overflow
        assert cost > 0
        assert cost < 100_000  # Sanity check

    def test_logger_with_callback(self):
        """Test logger with event callback."""
        events_received = []

        def callback(event: AuditEvent):
            events_received.append(event)

        logger = AIAuditLogger(
            tenant_id="callback-test",
            on_event_callback=callback,
        )

        logger.log_agent_invocation(
            agent_id="test",
            input_data={},
        )

        assert len(events_received) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
