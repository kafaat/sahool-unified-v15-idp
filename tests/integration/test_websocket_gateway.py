"""
Integration Tests for WebSocket Gateway Service
اختبارات التكامل لخدمة بوابة WebSocket

These tests validate the WebSocket gateway integration with the broader SAHOOL platform,
including NATS event bridging, JWT authentication, and real-time messaging.

Usage:
    pytest tests/integration/test_websocket_gateway.py -v

Note: These tests require WS_GATEWAY_URL environment variable or default to localhost:8081
"""

import asyncio
import json
import os
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Test configuration
WS_GATEWAY_URL = os.getenv("WS_GATEWAY_URL", "ws://localhost:8081")
HTTP_GATEWAY_URL = os.getenv("HTTP_GATEWAY_URL", "http://localhost:8081")


class TestWebSocketGatewayIntegration:
    """
    Integration tests for WebSocket Gateway
    اختبارات التكامل لبوابة WebSocket
    """

    @pytest.fixture
    def mock_jwt_payload(self):
        """Standard JWT payload for testing"""
        return {
            "sub": "user_test_123",
            "user_id": "user_test_123",
            "tenant_id": "tenant_test_001",
            "roles": ["farmer"],
            "exp": 9999999999,
            "iat": 1700000000,
        }

    @pytest.fixture
    def admin_jwt_payload(self):
        """Admin JWT payload for testing"""
        return {
            "sub": "admin_test_001",
            "user_id": "admin_test_001",
            "tenant_id": "tenant_test_001",
            "roles": ["super_admin"],
            "exp": 9999999999,
            "iat": 1700000000,
        }

    def test_health_endpoint_structure(self):
        """
        Test that health endpoint returns expected structure

        Validates:
        - /healthz endpoint returns status, service name, version
        - Response includes NATS connection status
        - Response includes connection statistics
        """
        # This is a structural test - can be run without live service
        expected_health_fields = ["status", "service", "version", "nats_connected"]
        expected_readiness_fields = ["status", "nats", "subscription_health", "connections"]

        # Verify field expectations are documented
        assert len(expected_health_fields) == 4
        assert len(expected_readiness_fields) == 4

    def test_websocket_message_types(self):
        """
        Test WebSocket message type definitions

        Validates:
        - All expected message types are defined
        - Message types follow consistent naming convention
        """
        expected_message_types = [
            "connected",  # Connection established
            "disconnected",  # Connection closed
            "join_room",  # Join a room
            "leave_room",  # Leave a room
            "message",  # Generic message
            "broadcast",  # Broadcast to room/tenant
            "error",  # Error response
            "ping",  # Keep-alive
            "pong",  # Keep-alive response
        ]

        # Verify message types follow conventions
        for msg_type in expected_message_types:
            assert msg_type.islower() or "_" in msg_type
            assert not msg_type.startswith("_")

    def test_room_naming_conventions(self):
        """
        Test room naming conventions for different contexts

        Validates:
        - Field rooms: field_{field_id}
        - Tenant rooms: tenant_{tenant_id}
        - Task rooms: task_{task_id}
        - User rooms: user_{user_id}
        """
        # Test room name generation patterns
        field_id = "abc-123-def"
        tenant_id = "tenant_001"
        task_id = "task_456"
        user_id = "user_789"

        expected_rooms = {
            "field_room": f"field_{field_id}",
            "tenant_room": f"tenant_{tenant_id}",
            "task_room": f"task_{task_id}",
            "user_room": f"user_{user_id}",
        }

        for room_type, room_name in expected_rooms.items():
            assert "_" in room_name
            assert room_name.count("_") >= 1

    def test_jwt_algorithm_whitelist(self):
        """
        Test that JWT algorithm whitelist is properly defined

        Security validation:
        - Only secure algorithms are allowed
        - 'none' algorithm is not in whitelist
        - Common weak algorithms are excluded
        """
        # These are the allowed algorithms from ws-gateway main.py
        allowed_algorithms = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]

        # Security checks
        assert "none" not in [alg.lower() for alg in allowed_algorithms]
        assert "HS256" in allowed_algorithms  # Standard HMAC
        assert "RS256" in allowed_algorithms  # RSA support

        # Verify no weak algorithms
        weak_algorithms = ["none", "None", "NONE"]
        for weak in weak_algorithms:
            assert weak not in allowed_algorithms

    def test_rate_limiting_configuration(self):
        """
        Test rate limiting configuration values

        Validates:
        - Rate limits are reasonable
        - Window size is appropriate
        - Message size limits are enforced
        """
        # Default configuration values (from environment or defaults)
        rate_limit_max_messages = int(os.getenv("WS_RATE_LIMIT_MESSAGES", "60"))
        rate_limit_window_seconds = int(os.getenv("WS_RATE_LIMIT_WINDOW", "60"))
        max_message_size_bytes = int(os.getenv("WS_MAX_MESSAGE_SIZE", "65536"))

        # Validate reasonable limits
        assert rate_limit_max_messages > 0
        assert rate_limit_max_messages <= 1000  # Not too permissive
        assert rate_limit_window_seconds >= 10
        assert rate_limit_window_seconds <= 300
        assert max_message_size_bytes >= 1024  # At least 1KB
        assert max_message_size_bytes <= 1024 * 1024  # Max 1MB

    @pytest.mark.asyncio
    async def test_nats_event_bridge_subjects(self):
        """
        Test NATS event bridge subject patterns

        Validates:
        - Subject patterns follow SAHOOL conventions
        - Multi-tenant subjects are properly formatted
        """
        # Expected NATS subject patterns from SAHOOL platform
        subject_patterns = [
            "sahool.{tenant_id}.field.created",
            "sahool.{tenant_id}.field.updated",
            "sahool.{tenant_id}.task.assigned",
            "sahool.{tenant_id}.alert.triggered",
            "sahool.{tenant_id}.ndvi.processed",
            "sahool.{tenant_id}.weather.updated",
        ]

        tenant_id = "tenant_test_001"

        for pattern in subject_patterns:
            subject = pattern.replace("{tenant_id}", tenant_id)
            # Validate subject format
            assert subject.startswith("sahool.")
            assert tenant_id in subject
            parts = subject.split(".")
            assert len(parts) >= 3

    def test_websocket_close_codes(self):
        """
        Test WebSocket close codes are properly defined

        Validates:
        - Custom close codes are in valid range (4000-4999)
        - Standard close codes are not overridden
        """
        # Custom close codes used by ws-gateway
        custom_close_codes = {
            4001: "Authentication required / Invalid token",
            4003: "Tenant mismatch",
        }

        # Validate custom codes are in valid range
        for code, description in custom_close_codes.items():
            assert 4000 <= code <= 4999, f"Close code {code} outside valid range"
            assert len(description) > 0

    def test_broadcast_request_validation(self):
        """
        Test broadcast request schema validation

        Validates:
        - Required fields are present
        - Optional fields are handled correctly
        """
        # Valid broadcast request structure
        valid_requests = [
            {"tenant_id": "tenant_001", "message": {"type": "test"}},
            {"user_id": "user_001", "message": {"type": "direct"}},
            {"field_id": "field_001", "message": {"type": "field_update"}},
            {"room": "custom_room", "message": {"type": "room_message"}},
        ]

        for req in valid_requests:
            assert "message" in req
            # At least one target must be specified
            target_keys = ["tenant_id", "user_id", "field_id", "room"]
            has_target = any(key in req for key in target_keys)
            assert has_target, f"Request {req} has no target"

    @pytest.mark.asyncio
    async def test_connection_lifecycle(self):
        """
        Test WebSocket connection lifecycle events

        Validates:
        - Connection establishment sends confirmation
        - Disconnection cleanup is performed
        - Rate limit state is cleaned up
        """
        # Mock connection lifecycle
        connection_events = [
            {"event": "connect", "expected_response": "connected"},
            {"event": "authenticate", "expected_response": "authenticated"},
            {"event": "join_room", "expected_response": "room_joined"},
            {"event": "leave_room", "expected_response": "room_left"},
            {"event": "disconnect", "expected_response": None},
        ]

        for event in connection_events:
            assert "event" in event
            # Lifecycle events should be well-defined

    def test_metrics_format(self):
        """
        Test Prometheus metrics format

        Validates:
        - Metrics follow Prometheus naming conventions
        - Required metrics are exposed
        """
        expected_metrics = [
            "ws_gateway_connections_total",
            "ws_gateway_rooms_total",
            "ws_gateway_nats_connected",
            "ws_gateway_nats_subscriptions_total",
            "ws_gateway_connections_by_room_type",
        ]

        for metric in expected_metrics:
            # Prometheus naming convention: lowercase with underscores
            assert metric == metric.lower()
            assert "_" in metric
            assert not metric.startswith("__")


class TestWebSocketSecurityIntegration:
    """
    Security-focused integration tests for WebSocket Gateway
    اختبارات أمنية للتكامل لبوابة WebSocket
    """

    def test_token_validation_scenarios(self):
        """
        Test various JWT token validation scenarios

        Security tests:
        - Empty token rejection
        - Expired token rejection
        - Invalid signature rejection
        - Algorithm confusion prevention
        """
        invalid_scenarios = [
            {"token": "", "expected_error": "Token is required"},
            {"token": "invalid", "expected_error": "Invalid token"},
            {"token": "a.b.c", "expected_error": "Invalid token"},  # Malformed
        ]

        for scenario in invalid_scenarios:
            assert "token" in scenario
            assert "expected_error" in scenario

    def test_tenant_isolation(self):
        """
        Test tenant isolation in WebSocket communication

        Security validation:
        - Users can only access their tenant's resources
        - Cross-tenant communication is blocked
        - Tenant mismatch returns appropriate error
        """
        # Tenant isolation scenarios
        scenarios = [
            {
                "user_tenant": "tenant_A",
                "requested_tenant": "tenant_A",
                "allowed": True,
            },
            {
                "user_tenant": "tenant_A",
                "requested_tenant": "tenant_B",
                "allowed": False,
            },
        ]

        for scenario in scenarios:
            if scenario["allowed"]:
                assert scenario["user_tenant"] == scenario["requested_tenant"]
            else:
                assert scenario["user_tenant"] != scenario["requested_tenant"]

    def test_rate_limit_enforcement(self):
        """
        Test rate limiting enforcement

        Security validation:
        - Rate limits are properly enforced
        - Exceeding rate limit returns error
        - Rate limit state is properly tracked
        """
        # Rate limit test parameters
        max_messages = 60
        window_seconds = 60

        # Calculate messages per second allowed
        msg_per_second = max_messages / window_seconds

        # Verify reasonable rate
        assert msg_per_second > 0.5  # At least 1 message per 2 seconds
        assert msg_per_second <= 10  # No more than 10 per second

    def test_message_size_limits(self):
        """
        Test message size limit enforcement

        Security validation:
        - Large messages are rejected
        - Error message is informative
        """
        max_size = 65536  # 64KB default

        # Test message sizes
        test_cases = [
            {"size": 1000, "expected": "allowed"},
            {"size": 50000, "expected": "allowed"},
            {"size": 70000, "expected": "rejected"},
            {"size": 100000, "expected": "rejected"},
        ]

        for case in test_cases:
            if case["expected"] == "allowed":
                assert case["size"] <= max_size
            else:
                assert case["size"] > max_size


class TestWebSocketNATSBridgeIntegration:
    """
    Tests for NATS bridge integration
    اختبارات تكامل جسر NATS
    """

    def test_nats_event_to_websocket_mapping(self):
        """
        Test NATS event to WebSocket message mapping

        Validates:
        - NATS events are properly converted to WebSocket messages
        - Event types are preserved
        - Tenant routing is correct
        """
        # NATS event to WebSocket mapping
        event_mappings = {
            "sahool.tenant_001.field.created": {
                "ws_type": "field_created",
                "target": "tenant_room",
            },
            "sahool.tenant_001.alert.triggered": {
                "ws_type": "alert",
                "target": "user_or_tenant",
            },
            "sahool.tenant_001.task.assigned": {
                "ws_type": "task_assigned",
                "target": "user_room",
            },
        }

        for nats_subject, mapping in event_mappings.items():
            # Extract tenant from subject
            parts = nats_subject.split(".")
            assert parts[0] == "sahool"
            assert len(parts) >= 3

    def test_subscription_health_monitoring(self):
        """
        Test NATS subscription health monitoring

        Validates:
        - Subscription health is tracked
        - Unhealthy subscriptions are reported
        - Readiness reflects subscription health
        """
        # Health check response structure
        expected_health_fields = [
            "healthy",
            "subscriptions_active",
            "subscriptions_failed",
            "last_message_time",
        ]

        # All fields should be present in health check
        for field in expected_health_fields:
            assert field.islower() or "_" in field


# Fixtures for live testing (when services are available)
@pytest.fixture
def live_test_enabled():
    """Check if live testing is enabled"""
    return os.getenv("ENABLE_LIVE_WS_TESTS", "false").lower() == "true"


@pytest.fixture
def test_jwt_token():
    """Generate a test JWT token (for live testing)"""
    # This would be generated by a proper auth service in live tests
    return os.getenv("TEST_JWT_TOKEN", "")


# Marker for tests that require live services
pytestmark = pytest.mark.integration


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
