"""
WeChat Service API Endpoint Tests
=================================
Comprehensive tests for all WeChat service API endpoints.

Tests cover:
- Health endpoints (/healthz, /readyz, /health)
- Message endpoints (/api/v1/messages/fetch, /api/v1/messages/send)
- Contact endpoints (/api/v1/contacts/add)
- Moment endpoints (/api/v1/moments/publish)
- Chat analysis endpoints (/api/v1/chat/summarize, /api/v1/chat/insights)
- Metrics endpoint (/metrics)
- Error handling
- Input validation
- Tenant access control

Author: SAHOOL Platform Team
"""

import os
import sys
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

# Ensure test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["DATABASE_URL"] = ""
os.environ["NATS_URL"] = ""
os.environ["REDIS_URL"] = ""


# ===============================================================================
# Mock Classes
# ===============================================================================


class MockUser:
    """Mock User model for authentication."""

    def __init__(self, tenant_id: str = "test-tenant"):
        self.id = "test-user-id"
        self.email = "test@example.com"
        self.tenant_id = tenant_id
        self.roles = ["user"]
        self.permissions = []
        self.is_active = True
        self.is_verified = True
        self.farm_ids = []

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def has_any_role(self, *roles: str) -> bool:
        return any(role in self.roles for role in roles)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def has_farm_access(self, farm_id: str) -> bool:
        return farm_id in self.farm_ids


# Mock auth dependencies
def mock_get_current_user():
    return MockUser(tenant_id="test-tenant")


mock_auth_deps = MagicMock()
mock_auth_deps.get_current_user = mock_get_current_user
mock_auth_models = MagicMock()
mock_auth_models.User = MockUser

# Patch before importing main
sys.modules["shared.auth.dependencies"] = mock_auth_deps
sys.modules["shared.auth.models"] = mock_auth_models


# ===============================================================================
# Import App After Patching
# ===============================================================================

import importlib.util

# Get the path to main.py
tests_dir = os.path.dirname(os.path.abspath(__file__))
service_dir = os.path.dirname(tests_dir)
main_path = os.path.join(service_dir, "src", "main.py")

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(service_dir)))
sys.path.insert(0, project_root)

# Import main module
spec = importlib.util.spec_from_file_location("main", main_path)
main_module = importlib.util.module_from_spec(spec)
sys.modules["main"] = main_module
spec.loader.exec_module(main_module)

# Get objects from the module
app = main_module.app
messages = main_module.messages
contacts = main_module.contacts
moments = main_module.moments
get_current_user_dep = main_module.get_current_user


# ===============================================================================
# Test Imports
# ===============================================================================

from httpx import ASGITransport, AsyncClient

# ===============================================================================
# Test Fixtures
# ===============================================================================


@pytest.fixture(autouse=True)
def clear_storage():
    """Clear in-memory storage before each test."""
    messages.clear()
    contacts.clear()
    moments.clear()
    yield
    messages.clear()
    contacts.clear()
    moments.clear()


@pytest.fixture
def setup_app_state():
    """Setup app state for testing."""
    app.state.publisher = None
    app.state.nats_connected = False
    app.state.db_pool = None
    app.state.db_connected = False
    app.state.redis = None
    app.state.redis_connected = False
    app.state.wechat_configured = False

    if hasattr(app.state, "limiter"):
        original_enabled = app.state.limiter.enabled
        app.state.limiter.enabled = False
    else:
        original_enabled = None

    yield

    if original_enabled is not None:
        app.state.limiter.enabled = original_enabled


@pytest.fixture
async def client(setup_app_state):
    """Create async test client with dependency overrides."""
    app.dependency_overrides[get_current_user_dep] = lambda: MockUser(tenant_id="test-tenant")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_fetch_request():
    return {
        "chat_id": "chat_001",
        "tenant_id": "test-tenant",
        "limit": 50,
    }


@pytest.fixture
def sample_send_request():
    return {
        "chat_id": "chat_001",
        "tenant_id": "test-tenant",
        "message_type": "text",
        "content": "Hello, how is the crop?",
    }


@pytest.fixture
def sample_contact_request():
    return {
        "wechat_id": "farmer_001",
        "tenant_id": "test-tenant",
        "contact_type": "friend",
        "greeting_message": "Hello!",
    }


@pytest.fixture
def sample_moment_request():
    return {
        "tenant_id": "test-tenant",
        "content": "Great harvest!",
        "visibility": "friends",
    }


@pytest.fixture
def sample_summarize_request():
    return {
        "chat_id": "chat_001",
        "tenant_id": "test-tenant",
        "time_range_hours": 24,
    }


@pytest.fixture
def sample_insights_request():
    return {
        "chat_id": "chat_001",
        "tenant_id": "test-tenant",
        "insight_types": ["sentiment", "topic"],
    }


# ===============================================================================
# Health Endpoint Tests
# ===============================================================================


class TestHealthEndpoints:
    """Test health check endpoints."""

    @pytest.mark.asyncio
    async def test_healthz_endpoint(self, client):
        """Test /healthz liveness probe."""
        response = await client.get("/healthz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "wechat-service"
        assert data["service_ar"] == "خدمة تكامل ويتشات"
        assert data["version"] == "16.0.0"

    @pytest.mark.asyncio
    async def test_readyz_endpoint(self, client):
        """Test /readyz readiness probe."""
        response = await client.get("/readyz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "database" in data
        assert "redis" in data
        assert "nats" in data
        assert "wechat_configured" in data

    @pytest.mark.asyncio
    async def test_health_detailed_endpoint(self, client):
        """Test /health detailed status."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "wechat-service"
        assert "messages_count" in data
        assert "contacts_count" in data
        assert "moments_count" in data

    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, client):
        """Test /metrics Prometheus endpoint."""
        response = await client.get("/metrics")

        assert response.status_code == 200
        content = response.text
        assert "wechat_messages_total" in content
        assert "wechat_contacts_total" in content
        assert "wechat_moments_total" in content
        assert "wechat_chats_total" in content


# ===============================================================================
# Message Endpoint Tests
# ===============================================================================


class TestMessageEndpoints:
    """Test message fetch and send endpoints."""

    @pytest.mark.asyncio
    async def test_fetch_messages_success(self, client, sample_fetch_request):
        """Test POST /api/v1/messages/fetch."""
        response = await client.post("/api/v1/messages/fetch", json=sample_fetch_request)

        assert response.status_code == 200
        data = response.json()
        assert data["chat_id"] == sample_fetch_request["chat_id"]
        assert "messages" in data
        assert "total_count" in data
        assert "has_more" in data

    @pytest.mark.asyncio
    async def test_fetch_messages_with_limit(self, client):
        """Test fetching messages with custom limit."""
        request = {
            "chat_id": "chat_001",
            "tenant_id": "test-tenant",
            "limit": 10,
        }
        response = await client.post("/api/v1/messages/fetch", json=request)

        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) <= 10

    @pytest.mark.asyncio
    async def test_fetch_messages_with_time_filter(self, client):
        """Test fetching messages with time filter."""
        request = {
            "chat_id": "chat_001",
            "tenant_id": "test-tenant",
            "after_timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
        }
        response = await client.post("/api/v1/messages/fetch", json=request)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_fetch_messages_with_type_filter(self, client):
        """Test fetching messages with message type filter."""
        request = {
            "chat_id": "chat_001",
            "tenant_id": "test-tenant",
            "message_types": ["text"],
        }
        response = await client.post("/api/v1/messages/fetch", json=request)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_fetch_messages_wrong_tenant(self, client, sample_fetch_request):
        """Test tenant access denied on fetch."""
        sample_fetch_request["tenant_id"] = "wrong-tenant"
        response = await client.post("/api/v1/messages/fetch", json=sample_fetch_request)

        assert response.status_code == 403
        data = response.json()
        assert data["error_code"] == "FORBIDDEN"

    @pytest.mark.asyncio
    async def test_send_message_success(self, client, sample_send_request):
        """Test POST /api/v1/messages/send."""
        response = await client.post("/api/v1/messages/send", json=sample_send_request)

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["chat_id"] == sample_send_request["chat_id"]
        assert data["content"] == sample_send_request["content"]
        assert data["status"] == "sent"
        assert data["status_ar"] == "تم الإرسال"

    @pytest.mark.asyncio
    async def test_send_message_with_reply(self, client, sample_send_request):
        """Test sending message as reply."""
        sample_send_request["reply_to_id"] = "msg_original_001"
        response = await client.post("/api/v1/messages/send", json=sample_send_request)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_send_message_with_metadata(self, client, sample_send_request):
        """Test sending message with metadata."""
        sample_send_request["metadata"] = {"priority": "high", "topic": "irrigation"}
        response = await client.post("/api/v1/messages/send", json=sample_send_request)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_send_image_message_without_url(self, client):
        """Test validation error for image message without media_url."""
        request = {
            "chat_id": "chat_001",
            "tenant_id": "test-tenant",
            "message_type": "image",
            "content": "Check this image",
        }
        response = await client.post("/api/v1/messages/send", json=request)

        assert response.status_code == 400
        data = response.json()
        assert "media_url" in data["detail"].lower() or "media" in data["error"].lower()

    @pytest.mark.asyncio
    async def test_send_message_wrong_tenant(self, client, sample_send_request):
        """Test tenant access denied on send."""
        sample_send_request["tenant_id"] = "wrong-tenant"
        response = await client.post("/api/v1/messages/send", json=sample_send_request)

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_send_message_empty_content(self, client):
        """Test validation error for empty content."""
        request = {
            "chat_id": "chat_001",
            "tenant_id": "test-tenant",
            "message_type": "text",
            "content": "",
        }
        response = await client.post("/api/v1/messages/send", json=request)

        assert response.status_code == 422  # Pydantic validation error


# ===============================================================================
# Contact Endpoint Tests
# ===============================================================================


class TestContactEndpoints:
    """Test contact management endpoints."""

    @pytest.mark.asyncio
    async def test_add_contact_success(self, client, sample_contact_request):
        """Test POST /api/v1/contacts/add."""
        response = await client.post("/api/v1/contacts/add", json=sample_contact_request)

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["wechat_id"] == sample_contact_request["wechat_id"]
        assert data["status"] == "pending"
        assert data["status_ar"] == "قيد الانتظار"

    @pytest.mark.asyncio
    async def test_add_contact_with_tags(self, client, sample_contact_request):
        """Test adding contact with tags."""
        sample_contact_request["tags"] = ["farmer", "wheat", "vip"]
        response = await client.post("/api/v1/contacts/add", json=sample_contact_request)

        assert response.status_code == 200
        data = response.json()
        assert data["tags"] == ["farmer", "wheat", "vip"]

    @pytest.mark.asyncio
    async def test_add_contact_with_notes(self, client, sample_contact_request):
        """Test adding contact with notes."""
        sample_contact_request["notes"] = "Wheat farmer from Riyadh region"
        response = await client.post("/api/v1/contacts/add", json=sample_contact_request)

        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "Wheat farmer from Riyadh region"

    @pytest.mark.asyncio
    async def test_add_contact_duplicate(self, client, sample_contact_request):
        """Test adding duplicate contact returns 409."""
        # Add first contact
        await client.post("/api/v1/contacts/add", json=sample_contact_request)

        # Try to add duplicate
        response = await client.post("/api/v1/contacts/add", json=sample_contact_request)

        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_add_contact_wrong_tenant(self, client, sample_contact_request):
        """Test tenant access denied on add contact."""
        sample_contact_request["tenant_id"] = "wrong-tenant"
        response = await client.post("/api/v1/contacts/add", json=sample_contact_request)

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_add_group_contact(self, client, sample_contact_request):
        """Test adding group type contact."""
        sample_contact_request["contact_type"] = "group"
        response = await client.post("/api/v1/contacts/add", json=sample_contact_request)

        assert response.status_code == 200
        data = response.json()
        assert data["contact_type"] == "group"

    @pytest.mark.asyncio
    async def test_add_official_account(self, client, sample_contact_request):
        """Test adding official account contact."""
        sample_contact_request["contact_type"] = "official_account"
        response = await client.post("/api/v1/contacts/add", json=sample_contact_request)

        assert response.status_code == 200
        data = response.json()
        assert data["contact_type"] == "official_account"


# ===============================================================================
# Moment Endpoint Tests
# ===============================================================================


class TestMomentEndpoints:
    """Test moments publishing endpoints."""

    @pytest.mark.asyncio
    async def test_publish_moment_success(self, client, sample_moment_request):
        """Test POST /api/v1/moments/publish."""
        response = await client.post("/api/v1/moments/publish", json=sample_moment_request)

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["content"] == sample_moment_request["content"]
        assert data["status"] == "published"
        assert data["status_ar"] == "تم النشر"

    @pytest.mark.asyncio
    async def test_publish_moment_with_media(self, client, sample_moment_request):
        """Test publishing moment with media."""
        sample_moment_request["media_urls"] = [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg",
        ]
        response = await client.post("/api/v1/moments/publish", json=sample_moment_request)

        assert response.status_code == 200
        data = response.json()
        assert len(data["media_urls"]) == 2

    @pytest.mark.asyncio
    async def test_publish_moment_with_location(self, client, sample_moment_request):
        """Test publishing moment with location."""
        sample_moment_request["location"] = "Riyadh Farm"
        sample_moment_request["location_ar"] = "مزرعة الرياض"
        response = await client.post("/api/v1/moments/publish", json=sample_moment_request)

        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "Riyadh Farm"
        assert data["location_ar"] == "مزرعة الرياض"

    @pytest.mark.asyncio
    async def test_publish_moment_with_link(self, client, sample_moment_request):
        """Test publishing moment with link."""
        sample_moment_request["link_url"] = "https://sahool.com/advisory"
        sample_moment_request["link_title"] = "Irrigation Advisory"
        response = await client.post("/api/v1/moments/publish", json=sample_moment_request)

        assert response.status_code == 200
        data = response.json()
        assert data["link_url"] == "https://sahool.com/advisory"

    @pytest.mark.asyncio
    async def test_publish_moment_selected_visibility_no_users(self, client, sample_moment_request):
        """Test validation error for selected visibility without users."""
        sample_moment_request["visibility"] = "selected"
        sample_moment_request["visible_to"] = None
        response = await client.post("/api/v1/moments/publish", json=sample_moment_request)

        assert response.status_code == 400
        data = response.json()
        assert "visible_to" in data["detail"].lower() or "visible" in data["error"].lower()

    @pytest.mark.asyncio
    async def test_publish_moment_selected_visibility_with_users(self, client, sample_moment_request):
        """Test publishing with selected visibility and user list."""
        sample_moment_request["visibility"] = "selected"
        sample_moment_request["visible_to"] = ["user_001", "user_002"]
        response = await client.post("/api/v1/moments/publish", json=sample_moment_request)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_publish_moment_wrong_tenant(self, client, sample_moment_request):
        """Test tenant access denied on publish."""
        sample_moment_request["tenant_id"] = "wrong-tenant"
        response = await client.post("/api/v1/moments/publish", json=sample_moment_request)

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_publish_moment_bilingual(self, client, sample_moment_request):
        """Test publishing bilingual moment."""
        sample_moment_request["content_ar"] = "حصاد رائع!"
        response = await client.post("/api/v1/moments/publish", json=sample_moment_request)

        assert response.status_code == 200
        data = response.json()
        assert data["content_ar"] == "حصاد رائع!"


# ===============================================================================
# Chat Analysis Endpoint Tests
# ===============================================================================


class TestChatAnalysisEndpoints:
    """Test chat summarization and insights endpoints."""

    @pytest.mark.asyncio
    async def test_summarize_chat_success(self, client, sample_summarize_request):
        """Test POST /api/v1/chat/summarize."""
        response = await client.post("/api/v1/chat/summarize", json=sample_summarize_request)

        assert response.status_code == 200
        data = response.json()
        assert data["chat_id"] == sample_summarize_request["chat_id"]
        assert "summary" in data
        assert "key_topics" in data
        assert "action_items" in data
        assert "generated_at" in data

    @pytest.mark.asyncio
    async def test_summarize_chat_with_participants(self, client, sample_summarize_request):
        """Test chat summary with participant info."""
        sample_summarize_request["include_participants"] = True
        response = await client.post("/api/v1/chat/summarize", json=sample_summarize_request)

        assert response.status_code == 200
        data = response.json()
        assert "participants" in data

    @pytest.mark.asyncio
    async def test_summarize_chat_bilingual(self, client, sample_summarize_request):
        """Test bilingual chat summary."""
        sample_summarize_request["language"] = "both"
        response = await client.post("/api/v1/chat/summarize", json=sample_summarize_request)

        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "summary_ar" in data
        assert "key_topics_ar" in data

    @pytest.mark.asyncio
    async def test_summarize_chat_arabic_only(self, client, sample_summarize_request):
        """Test Arabic-only chat summary."""
        sample_summarize_request["language"] = "ar"
        response = await client.post("/api/v1/chat/summarize", json=sample_summarize_request)

        assert response.status_code == 200
        data = response.json()
        assert "summary_ar" in data

    @pytest.mark.asyncio
    async def test_summarize_chat_wrong_tenant(self, client, sample_summarize_request):
        """Test tenant access denied on summarize."""
        sample_summarize_request["tenant_id"] = "wrong-tenant"
        response = await client.post("/api/v1/chat/summarize", json=sample_summarize_request)

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_insights_success(self, client, sample_insights_request):
        """Test POST /api/v1/chat/insights."""
        response = await client.post("/api/v1/chat/insights", json=sample_insights_request)

        assert response.status_code == 200
        data = response.json()
        assert data["chat_id"] == sample_insights_request["chat_id"]
        assert "insights" in data
        assert "overall_sentiment" in data
        assert "generated_at" in data

    @pytest.mark.asyncio
    async def test_get_insights_all_types(self, client, sample_insights_request):
        """Test insights with all insight types."""
        sample_insights_request["insight_types"] = [
            "sentiment",
            "topic",
            "action_items",
            "questions",
            "key_decisions",
        ]
        response = await client.post("/api/v1/chat/insights", json=sample_insights_request)

        assert response.status_code == 200
        data = response.json()
        assert len(data["insights"]) == 5

    @pytest.mark.asyncio
    async def test_get_insights_bilingual(self, client, sample_insights_request):
        """Test bilingual insights."""
        sample_insights_request["language"] = "both"
        response = await client.post("/api/v1/chat/insights", json=sample_insights_request)

        assert response.status_code == 200
        data = response.json()
        assert "sentiment_label_ar" in data

    @pytest.mark.asyncio
    async def test_get_insights_wrong_tenant(self, client, sample_insights_request):
        """Test tenant access denied on insights."""
        sample_insights_request["tenant_id"] = "wrong-tenant"
        response = await client.post("/api/v1/chat/insights", json=sample_insights_request)

        assert response.status_code == 403


# ===============================================================================
# Error Handling Tests
# ===============================================================================


class TestErrorHandling:
    """Test error response format and handling."""

    @pytest.mark.asyncio
    async def test_error_response_has_bilingual_messages(self, client):
        """Test error responses include Arabic messages."""
        request = {"tenant_id": "wrong-tenant", "chat_id": "chat_001"}
        response = await client.post("/api/v1/messages/fetch", json=request)

        assert response.status_code == 403
        data = response.json()
        assert "error" in data
        assert "error_ar" in data
        assert "error_code" in data

    @pytest.mark.asyncio
    async def test_request_id_in_response(self, client):
        """Test X-Request-ID is present in response headers."""
        response = await client.get("/healthz")

        assert response.status_code == 200
        assert "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_custom_request_id_preserved(self, client):
        """Test custom X-Request-ID is preserved."""
        custom_id = "custom-request-id-12345"
        response = await client.get("/healthz", headers={"X-Request-ID": custom_id})

        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id

    @pytest.mark.asyncio
    async def test_validation_error_format(self, client):
        """Test validation error response format."""
        # Missing required field
        response = await client.post("/api/v1/messages/fetch", json={})

        assert response.status_code == 422


# ===============================================================================
# Response Format Tests
# ===============================================================================


class TestResponseFormats:
    """Test API response formats."""

    @pytest.mark.asyncio
    async def test_message_response_has_all_fields(self, client, sample_send_request):
        """Test message response includes all expected fields."""
        response = await client.post("/api/v1/messages/send", json=sample_send_request)

        assert response.status_code == 200
        data = response.json()
        expected_fields = [
            "id",
            "chat_id",
            "message_type",
            "content",
            "timestamp",
            "status",
            "status_ar",
        ]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"

    @pytest.mark.asyncio
    async def test_contact_response_has_all_fields(self, client, sample_contact_request):
        """Test contact response includes all expected fields."""
        response = await client.post("/api/v1/contacts/add", json=sample_contact_request)

        assert response.status_code == 200
        data = response.json()
        expected_fields = [
            "id",
            "wechat_id",
            "contact_type",
            "status",
            "status_ar",
            "tags",
            "added_at",
        ]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"

    @pytest.mark.asyncio
    async def test_moment_response_has_all_fields(self, client, sample_moment_request):
        """Test moment response includes all expected fields."""
        response = await client.post("/api/v1/moments/publish", json=sample_moment_request)

        assert response.status_code == 200
        data = response.json()
        expected_fields = [
            "id",
            "content",
            "media_urls",
            "visibility",
            "published_at",
            "status",
            "status_ar",
        ]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"

    @pytest.mark.asyncio
    async def test_summary_response_has_all_fields(self, client, sample_summarize_request):
        """Test summary response includes all expected fields."""
        response = await client.post("/api/v1/chat/summarize", json=sample_summarize_request)

        assert response.status_code == 200
        data = response.json()
        expected_fields = [
            "chat_id",
            "time_range_start",
            "time_range_end",
            "total_messages",
            "summary",
            "key_topics",
            "action_items",
            "generated_at",
        ]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"

    @pytest.mark.asyncio
    async def test_insights_response_has_all_fields(self, client, sample_insights_request):
        """Test insights response includes all expected fields."""
        response = await client.post("/api/v1/chat/insights", json=sample_insights_request)

        assert response.status_code == 200
        data = response.json()
        expected_fields = [
            "chat_id",
            "time_range_start",
            "time_range_end",
            "total_messages_analyzed",
            "insights",
            "overall_sentiment",
            "generated_at",
        ]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"


# ===============================================================================
# Message Type Tests
# ===============================================================================


class TestMessageTypes:
    """Test different message types."""

    @pytest.mark.asyncio
    async def test_send_text_message(self, client):
        """Test sending text message."""
        request = {
            "chat_id": "chat_001",
            "tenant_id": "test-tenant",
            "message_type": "text",
            "content": "Hello world!",
        }
        response = await client.post("/api/v1/messages/send", json=request)

        assert response.status_code == 200
        assert response.json()["message_type"] == "text"

    @pytest.mark.asyncio
    async def test_send_image_message(self, client):
        """Test sending image message."""
        request = {
            "chat_id": "chat_001",
            "tenant_id": "test-tenant",
            "message_type": "image",
            "content": "Check this field photo",
            "media_url": "https://example.com/field.jpg",
        }
        response = await client.post("/api/v1/messages/send", json=request)

        assert response.status_code == 200
        assert response.json()["message_type"] == "image"

    @pytest.mark.asyncio
    async def test_send_location_message(self, client):
        """Test sending location message."""
        request = {
            "chat_id": "chat_001",
            "tenant_id": "test-tenant",
            "message_type": "location",
            "content": "Farm location",
            "media_url": "geo:24.7136,46.6753",
        }
        response = await client.post("/api/v1/messages/send", json=request)

        assert response.status_code == 200
        assert response.json()["message_type"] == "location"

    @pytest.mark.asyncio
    async def test_send_link_message(self, client):
        """Test sending link message."""
        request = {
            "chat_id": "chat_001",
            "tenant_id": "test-tenant",
            "message_type": "link",
            "content": "Check this advisory",
            "media_url": "https://sahool.com/advisory/123",
        }
        response = await client.post("/api/v1/messages/send", json=request)

        assert response.status_code == 200
        assert response.json()["message_type"] == "link"


# ===============================================================================
# Insight Type Tests
# ===============================================================================


class TestInsightTypes:
    """Test different insight types."""

    @pytest.mark.asyncio
    async def test_sentiment_insight(self, client):
        """Test sentiment insight extraction."""
        request = {
            "chat_id": "chat_001",
            "tenant_id": "test-tenant",
            "insight_types": ["sentiment"],
        }
        response = await client.post("/api/v1/chat/insights", json=request)

        assert response.status_code == 200
        data = response.json()
        assert any(i["insight_type"] == "sentiment" for i in data["insights"])

    @pytest.mark.asyncio
    async def test_topic_insight(self, client):
        """Test topic insight extraction."""
        request = {
            "chat_id": "chat_001",
            "tenant_id": "test-tenant",
            "insight_types": ["topic"],
        }
        response = await client.post("/api/v1/chat/insights", json=request)

        assert response.status_code == 200
        data = response.json()
        assert any(i["insight_type"] == "topic" for i in data["insights"])

    @pytest.mark.asyncio
    async def test_action_items_insight(self, client):
        """Test action items insight extraction."""
        request = {
            "chat_id": "chat_001",
            "tenant_id": "test-tenant",
            "insight_types": ["action_items"],
        }
        response = await client.post("/api/v1/chat/insights", json=request)

        assert response.status_code == 200
        data = response.json()
        assert any(i["insight_type"] == "action_items" for i in data["insights"])

    @pytest.mark.asyncio
    async def test_questions_insight(self, client):
        """Test questions insight extraction."""
        request = {
            "chat_id": "chat_001",
            "tenant_id": "test-tenant",
            "insight_types": ["questions"],
        }
        response = await client.post("/api/v1/chat/insights", json=request)

        assert response.status_code == 200
        data = response.json()
        assert any(i["insight_type"] == "questions" for i in data["insights"])

    @pytest.mark.asyncio
    async def test_key_decisions_insight(self, client):
        """Test key decisions insight extraction."""
        request = {
            "chat_id": "chat_001",
            "tenant_id": "test-tenant",
            "insight_types": ["key_decisions"],
        }
        response = await client.post("/api/v1/chat/insights", json=request)

        assert response.status_code == 200
        data = response.json()
        assert any(i["insight_type"] == "key_decisions" for i in data["insights"])
