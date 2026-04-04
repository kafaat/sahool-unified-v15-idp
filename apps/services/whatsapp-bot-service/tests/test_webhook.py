# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Tests for WhatsApp webhook endpoints.
اختبارات نقاط نهاية webhook لواتساب.
"""

import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)

# Set test environment before imports
os.environ.setdefault("ENVIRONMENT", "test")
os.environ["WHATSAPP_TOKEN"] = "test_token"
os.environ["WHATSAPP_PHONE_ID"] = "123456789012345"
os.environ["WHATSAPP_VERIFY_TOKEN"] = "test_verify_token"
os.environ["LLM_ORCHESTRATOR_URL"] = "http://localhost:8220"
os.environ.setdefault("REDIS_URL", "")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


class TestWebhookVerification:
    """Tests for webhook verification endpoint."""

    def setup_method(self):
        """Set up test client."""
        # Import app after environment is set
        from src.main import app

        self.client = TestClient(app)

    def test_webhook_verification_success(self):
        """Test successful webhook verification."""
        response = self.client.get(
            "/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "test_verify_token",
                "hub.challenge": "challenge_123",
            },
        )
        assert response.status_code == 200
        assert response.text == "challenge_123"

    def test_webhook_verification_wrong_token(self):
        """Test webhook verification with wrong token."""
        response = self.client.get(
            "/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "wrong_token",
                "hub.challenge": "challenge_123",
            },
        )
        assert response.status_code == 403

    def test_webhook_verification_wrong_mode(self):
        """Test webhook verification with wrong mode."""
        response = self.client.get(
            "/webhook",
            params={
                "hub.mode": "unsubscribe",
                "hub.verify_token": "test_verify_token",
                "hub.challenge": "challenge_123",
            },
        )
        assert response.status_code == 403

    def test_webhook_verification_missing_params(self):
        """Test webhook verification with missing parameters."""
        response = self.client.get("/webhook")
        assert response.status_code == 403


class TestWebhookMessageReceive:
    """Tests for webhook message receive endpoint."""

    def setup_method(self):
        """Set up test client.

        WHATSAPP_HMAC_REQUIRED=false bypasses HMAC verification for tests that
        do not exercise signature checking (e.g. payload parsing, message types).
        Tests that DO exercise HMAC explicitly set the app secret instead.
        """
        import os

        os.environ.setdefault("WHATSAPP_HMAC_REQUIRED", "false")
        from src.main import app

        self.client = TestClient(app)
        self.app = app

    def teardown_method(self):
        import os

        os.environ.pop("WHATSAPP_HMAC_REQUIRED", None)

    def _make_signature(self, secret: str, body: bytes) -> str:
        """Compute X-Hub-Signature-256 for a payload."""
        import hashlib
        import hmac as _hmac

        digest = _hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        return f"sha256={digest}"

    def test_receive_text_message(self, sample_text_message, mock_message_handler):
        """Test receiving a text message (no app secret configured → passes)."""
        # WHATSAPP_APP_SECRET not set → HMAC check skipped (dev mode)
        self.app.state.message_handler = mock_message_handler

        response = self.client.post("/webhook", json=sample_text_message)
        assert response.status_code == 200
        assert response.json()["status"] == "received"

    def test_receive_text_message_valid_signature(self, sample_text_message, mock_message_handler):
        """Test receiving a text message with correct HMAC signature."""
        import json as _json
        import os

        secret = "test-app-secret-12345"
        from src.api.endpoints import webhook as _wh

        original_secret = _wh.settings.whatsapp_app_secret
        # Re-enable HMAC for this specific test
        os.environ.pop("WHATSAPP_HMAC_REQUIRED", None)

        try:
            _wh.settings.whatsapp_app_secret = secret
            self.app.state.message_handler = mock_message_handler
            body = _json.dumps(sample_text_message).encode()
            sig = self._make_signature(secret, body)

            response = self.client.post(
                "/webhook",
                content=body,
                headers={"Content-Type": "application/json", "X-Hub-Signature-256": sig},
            )
            assert response.status_code == 200
            assert response.json()["status"] == "received"
        finally:
            _wh.settings.whatsapp_app_secret = original_secret
            os.environ["WHATSAPP_HMAC_REQUIRED"] = "false"

    def test_receive_message_invalid_signature_rejected(self, sample_text_message, mock_message_handler):
        """Test that a wrong HMAC signature is rejected with 401."""
        import os

        from src.api.endpoints import webhook as _wh

        original_secret = _wh.settings.whatsapp_app_secret
        os.environ.pop("WHATSAPP_HMAC_REQUIRED", None)

        try:
            _wh.settings.whatsapp_app_secret = "test-app-secret-12345"
            self.app.state.message_handler = mock_message_handler
            response = self.client.post(
                "/webhook",
                json=sample_text_message,
                headers={"X-Hub-Signature-256": "sha256=badhash"},
            )
            assert response.status_code == 401
        finally:
            _wh.settings.whatsapp_app_secret = original_secret
            os.environ["WHATSAPP_HMAC_REQUIRED"] = "false"

    def test_receive_message_missing_signature_rejected(self, sample_text_message, mock_message_handler):
        """Test that a missing signature is rejected when app secret is configured."""
        import os

        from src.api.endpoints import webhook as _wh

        original_secret = _wh.settings.whatsapp_app_secret
        os.environ.pop("WHATSAPP_HMAC_REQUIRED", None)

        try:
            _wh.settings.whatsapp_app_secret = "test-app-secret-12345"
            self.app.state.message_handler = mock_message_handler
            # No X-Hub-Signature-256 header
            response = self.client.post("/webhook", json=sample_text_message)
            assert response.status_code == 401
        finally:
            _wh.settings.whatsapp_app_secret = original_secret
            os.environ["WHATSAPP_HMAC_REQUIRED"] = "false"

    def test_receive_image_message(self, sample_image_message, mock_message_handler):
        """Test receiving an image message."""
        self.app.state.message_handler = mock_message_handler

        response = self.client.post("/webhook", json=sample_image_message)
        assert response.status_code == 200
        assert response.json()["status"] == "received"

    def test_receive_location_message(self, sample_location_message, mock_message_handler):
        """Test receiving a location message."""
        self.app.state.message_handler = mock_message_handler

        response = self.client.post("/webhook", json=sample_location_message)
        assert response.status_code == 200
        assert response.json()["status"] == "received"

    def test_receive_button_response(self, sample_button_response, mock_message_handler):
        """Test receiving a button response."""
        self.app.state.message_handler = mock_message_handler

        response = self.client.post("/webhook", json=sample_button_response)
        assert response.status_code == 200
        assert response.json()["status"] == "received"

    def test_receive_status_update(self, sample_status_update, mock_message_handler):
        """Test receiving a status update."""
        self.app.state.message_handler = mock_message_handler

        response = self.client.post("/webhook", json=sample_status_update)
        assert response.status_code == 200
        assert response.json()["status"] == "received"

    def test_receive_invalid_payload(self, mock_message_handler):
        """Test receiving an invalid payload."""
        self.app.state.message_handler = mock_message_handler

        response = self.client.post("/webhook", json={"invalid": "payload"})
        # Should still return 200 to prevent WhatsApp from retrying
        assert response.status_code == 200


class TestSendMessageAPI:
    """Tests for send message API endpoint."""

    _TENANT_HEADER = {"X-Tenant-ID": "00000000-0000-0000-0000-000000000001"}

    def setup_method(self):
        """Set up test client with auth bypassed for unit testing."""
        from src.main import app

        # Override auth dependency so send endpoints are testable without JWT
        from src.api.endpoints.webhook import get_current_user

        app.dependency_overrides[get_current_user] = lambda: {"id": "test-user", "tid": "test-tenant"}
        self.client = TestClient(app)
        self.app = app

    def teardown_method(self):
        self.app.dependency_overrides.clear()

    def test_send_text_message(self, mock_whatsapp_client):
        """Test sending a text message."""
        self.app.state.whatsapp_client = mock_whatsapp_client

        response = self.client.post(
            "/api/v1/send",
            json={
                "to": "967123456789",
                "type": "text",
                "text": {"body": "مرحبا!"},
            },
            headers=self._TENANT_HEADER,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message_id"] == "msg_123"

    def test_send_text_message_not_configured(self):
        """Test sending a text message when WhatsApp is not configured."""
        # Create a mock client that is not configured
        mock_client = MagicMock()
        mock_client.is_configured = False
        self.app.state.whatsapp_client = mock_client

        response = self.client.post(
            "/api/v1/send",
            json={
                "to": "967123456789",
                "type": "text",
                "text": {"body": "مرحبا!"},
            },
            headers=self._TENANT_HEADER,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "not configured" in data["error"]


class TestSendTemplateAPI:
    """Tests for send template message API endpoint."""

    _TENANT_HEADER = {"X-Tenant-ID": "00000000-0000-0000-0000-000000000001"}

    def setup_method(self):
        """Set up test client with auth bypassed for unit testing."""
        from src.main import app

        from src.api.endpoints.webhook import get_current_user

        app.dependency_overrides[get_current_user] = lambda: {"id": "test-user", "tid": "test-tenant"}
        self.client = TestClient(app)
        self.app = app

    def teardown_method(self):
        self.app.dependency_overrides.clear()

    def test_send_template_message(self, mock_whatsapp_client):
        """Test sending a template message."""
        self.app.state.whatsapp_client = mock_whatsapp_client

        response = self.client.post(
            "/api/v1/send-template",
            json={
                "to": "967123456789",
                "template_name": "hello_world",
                "language_code": "ar",
            },
            headers=self._TENANT_HEADER,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message_id"] == "msg_128"


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def setup_method(self):
        """Set up test client."""
        from src.main import app

        self.client = TestClient(app)

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "whatsapp-bot-service"
        assert "version" in data

    def test_readiness_endpoint(self):
        """Test readiness check endpoint."""
        response = self.client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "SAHOOL WhatsApp Bot"
        assert "endpoints" in data


class TestSchemas:
    """Tests for Pydantic schemas."""

    def test_whatsapp_message_parsing(self):
        """Test WhatsApp message schema parsing."""
        from src.api.schemas import MessageType, WhatsAppMessage

        message_data = {
            "from": "967123456789",
            "id": "wamid.test123",
            "timestamp": "1704067200",
            "type": "text",
            "text": {"body": "Hello"},
        }
        message = WhatsAppMessage(**message_data)
        assert message.from_ == "967123456789"
        assert message.type == MessageType.TEXT
        assert message.text.body == "Hello"

    def test_webhook_payload_parsing(self):
        """Test webhook payload schema parsing."""
        from src.api.schemas import WhatsAppWebhookPayload

        payload_data = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "123456789",
                    "changes": [
                        {
                            "field": "messages",
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "967123456789",
                                    "phone_number_id": "123456789",
                                },
                            },
                        }
                    ],
                }
            ],
        }
        payload = WhatsAppWebhookPayload(**payload_data)
        assert payload.object == "whatsapp_business_account"
        assert len(payload.entry) == 1

    def test_conversation_state(self):
        """Test conversation state schema."""
        from src.api.schemas import (
            ConversationIntent,
            ConversationState,
            FarmerProfile,
            Language,
            MessageType,
        )

        profile = FarmerProfile(
            phone_number="967123456789",
            name="Test Farmer",
            language=Language.ARABIC,
        )

        state = ConversationState(
            phone_number="967123456789",
            session_id="test-123",
            profile=profile,
            language=Language.ARABIC,
            current_intent=ConversationIntent.IRRIGATION,
        )

        # Test adding messages
        state.add_message(
            message_id="msg1",
            role="user",
            content="كيف أسقي القمح؟",
            content_type=MessageType.TEXT,
        )
        state.add_message(
            message_id="msg2",
            role="assistant",
            content="يُنصح بالري كل 10-14 يوم",
        )

        assert len(state.messages) == 2
        assert state.get_recent_messages(1)[0].content == "يُنصح بالري كل 10-14 يوم"

        context = state.get_context_for_llm()
        assert len(context) == 2
        assert context[0]["role"] == "user"
        assert context[1]["role"] == "assistant"


class TestResponseBuilder:
    """Tests for response builder."""

    def test_greeting_arabic(self):
        """Test Arabic greeting."""
        from src.api.schemas import Language
        from src.handlers.response_builder import ResponseBuilder

        builder = ResponseBuilder()
        greeting = builder.build_greeting(Language.ARABIC, name="أحمد")
        assert "أحمد" in greeting
        assert "مرحباً" in greeting

    def test_greeting_english(self):
        """Test English greeting."""
        from src.api.schemas import Language
        from src.handlers.response_builder import ResponseBuilder

        builder = ResponseBuilder()
        greeting = builder.build_greeting(Language.ENGLISH, name="Ahmed")
        assert "Ahmed" in greeting
        assert "Hello" in greeting

    def test_help_message_arabic(self):
        """Test Arabic help message."""
        from src.api.schemas import Language
        from src.handlers.response_builder import ResponseBuilder

        builder = ResponseBuilder()
        help_text = builder.build_help_message(Language.ARABIC)
        assert "دليل الاستخدام" in help_text

    def test_menu_buttons_arabic(self):
        """Test Arabic menu buttons."""
        from src.api.schemas import Language
        from src.handlers.response_builder import ResponseBuilder

        builder = ResponseBuilder()
        buttons = builder.get_main_menu_buttons(Language.ARABIC)
        assert len(buttons) == 3
        assert any("أمراض" in btn["title"] for btn in buttons)

    def test_vision_response_with_detections(self):
        """Test vision response with detections."""
        from src.api.schemas import Language
        from src.handlers.response_builder import ResponseBuilder

        builder = ResponseBuilder()
        vision_result = {
            "detections": [
                {"label": "Rust", "label_ar": "صدأ", "confidence": 0.85, "category": "disease"},
                {"label": "Aphid", "label_ar": "من", "confidence": 0.72, "category": "pest"},
            ],
            "recommendations_ar": ["رش مبيد فطري", "استخدام مكافحة حيوية"],
            "recommendations": ["Apply fungicide", "Use biological control"],
            "severity": "medium",
        }

        # Test Arabic response
        response_ar = builder.build_vision_response(vision_result, Language.ARABIC)
        assert "صدأ" in response_ar
        assert "من" in response_ar
        assert "التوصيات" in response_ar
        assert "متوسطة" in response_ar

        # Test English response
        response_en = builder.build_vision_response(vision_result, Language.ENGLISH)
        assert "Rust" in response_en
        assert "Aphid" in response_en
        assert "Recommendations" in response_en
        assert "Medium" in response_en

    def test_vision_response_no_detections(self):
        """Test vision response with no detections."""
        from src.api.schemas import Language
        from src.handlers.response_builder import ResponseBuilder

        builder = ResponseBuilder()
        vision_result = {"detections": []}

        response = builder.build_vision_response(vision_result, Language.ARABIC)
        assert "لم أتمكن" in response


class TestSessionManager:
    """Tests for session manager."""

    @pytest.mark.asyncio
    async def test_create_session(self):
        """Test session creation."""
        from src.api.schemas import Language
        from src.utils.session_manager import SessionManager

        manager = SessionManager(redis_client=None, session_ttl=3600)

        session = await manager.create_session(
            phone_number="967123456789",
            sender_name="Test Farmer",
            language=Language.ARABIC,
        )

        assert session.phone_number == "967123456789"
        assert session.profile.name == "Test Farmer"
        assert session.language == Language.ARABIC

    @pytest.mark.asyncio
    async def test_get_session(self):
        """Test session retrieval."""
        from src.api.schemas import Language
        from src.utils.session_manager import SessionManager

        manager = SessionManager(redis_client=None, session_ttl=3600)

        # Create and retrieve session
        created = await manager.create_session(
            phone_number="967123456789",
            sender_name="Test",
            language=Language.ARABIC,
        )

        retrieved = await manager.get_session("967123456789")
        assert retrieved is not None
        assert retrieved.session_id == created.session_id

    @pytest.mark.asyncio
    async def test_delete_session(self):
        """Test session deletion."""
        from src.api.schemas import Language
        from src.utils.session_manager import SessionManager

        manager = SessionManager(redis_client=None, session_ttl=3600)

        # Create and delete session
        await manager.create_session(
            phone_number="967123456789",
            sender_name="Test",
            language=Language.ARABIC,
        )

        result = await manager.delete_session("967123456789")
        assert result is True

        # Verify session is deleted
        session = await manager.get_session("967123456789")
        assert session is None

    @pytest.mark.asyncio
    async def test_set_language(self):
        """Test setting language preference."""
        from src.api.schemas import Language
        from src.utils.session_manager import SessionManager

        manager = SessionManager(redis_client=None, session_ttl=3600)

        await manager.create_session(
            phone_number="967123456789",
            sender_name="Test",
            language=Language.ARABIC,
        )

        result = await manager.set_language("967123456789", Language.ENGLISH)
        assert result is True

        session = await manager.get_session("967123456789")
        assert session.language == Language.ENGLISH

    @pytest.mark.asyncio
    async def test_set_location(self):
        """Test setting location."""
        from src.api.schemas import Language
        from src.utils.session_manager import SessionManager

        manager = SessionManager(redis_client=None, session_ttl=3600)

        await manager.create_session(
            phone_number="967123456789",
            sender_name="Test",
            language=Language.ARABIC,
        )

        result = await manager.set_location("967123456789", 15.3694, 44.1910)
        assert result is True

        session = await manager.get_session("967123456789")
        assert session.profile.location["lat"] == 15.3694
        assert session.profile.location["lng"] == 44.1910
