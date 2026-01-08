"""
SAHOOL Notification Service - Push Notification Tests
Comprehensive tests for Firebase Cloud Messaging integration
Coverage: Push notification sending, topics, multicast, error handling
"""

import json
from unittest.mock import MagicMock, call, patch

import pytest


@pytest.fixture
def mock_firebase_credentials():
    """Mock Firebase credentials"""
    return {
        "type": "service_account",
        "project_id": "test-project",
        "private_key_id": "test-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----",
        "client_email": "test@test-project.iam.gserviceaccount.com",
        "client_id": "123456789",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }


@pytest.fixture
def firebase_client():
    """Create FirebaseClient instance"""
    from src.firebase_client import FirebaseClient

    return FirebaseClient()


class TestFirebaseClientInitialization:
    """Test Firebase client initialization"""

    def test_initialize_with_credentials_path(
        self, firebase_client, mock_firebase_credentials, tmp_path
    ):
        """Test initialization with credentials file path"""
        # Create temporary credentials file
        creds_file = tmp_path / "firebase-creds.json"
        creds_file.write_text(json.dumps(mock_firebase_credentials))

        with patch("firebase_admin.initialize_app") as mock_init:
            result = firebase_client.initialize(credentials_path=str(creds_file))

            assert result is True
            assert firebase_client._initialized is True
            mock_init.assert_called_once()

    def test_initialize_with_credentials_dict(self, firebase_client, mock_firebase_credentials):
        """Test initialization with credentials dictionary"""
        with patch("firebase_admin.initialize_app") as mock_init:
            result = firebase_client.initialize(credentials_dict=mock_firebase_credentials)

            assert result is True
            assert firebase_client._initialized is True

    def test_initialize_from_environment(self, firebase_client, mock_firebase_credentials):
        """Test initialization from environment variables"""
        with patch.dict(
            "os.environ", {"FIREBASE_CREDENTIALS_JSON": json.dumps(mock_firebase_credentials)}
        ), patch("firebase_admin.initialize_app") as mock_init:
            result = firebase_client.initialize()

            assert result is True

    def test_initialize_without_credentials(self, firebase_client):
        """Test initialization without credentials fails gracefully"""
        with patch.dict("os.environ", {}, clear=True):
            result = firebase_client.initialize()

            assert result is False
            assert firebase_client._initialized is False

    def test_initialize_already_initialized(self, firebase_client):
        """Test initialization when already initialized"""
        firebase_client._initialized = True

        result = firebase_client.initialize()

        assert result is True

    def test_initialize_with_error(self, firebase_client, mock_firebase_credentials):
        """Test initialization handles errors"""
        with patch("firebase_admin.initialize_app", side_effect=Exception("Init error")):
            result = firebase_client.initialize(credentials_dict=mock_firebase_credentials)

            assert result is False
            assert firebase_client._initialized is False


class TestSingleNotificationSending:
    """Test sending notifications to single device"""

    def test_send_notification_success(self, firebase_client):
        """Test successful notification sending"""
        firebase_client._initialized = True

        mock_response = "projects/test-project/messages/msg-123"

        with patch("firebase_admin.messaging.send", return_value=mock_response) as mock_send:
            result = firebase_client.send_notification(
                token="device-token-123",
                title="Test Notification",
                body="Test body",
                title_ar="إشعار تجريبي",
                body_ar="نص تجريبي",
            )

            assert result == mock_response
            mock_send.assert_called_once()

            # Verify message structure
            call_args = mock_send.call_args[0][0]
            assert call_args.token == "device-token-123"
            assert call_args.notification is not None

    def test_send_notification_with_data(self, firebase_client):
        """Test sending notification with custom data"""
        firebase_client._initialized = True

        with patch("firebase_admin.messaging.send", return_value="msg-123") as mock_send:
            result = firebase_client.send_notification(
                token="device-token-123",
                title="Alert",
                body="Important alert",
                data={"type": "weather_alert", "severity": "high", "action_url": "/weather/123"},
            )

            assert result == "msg-123"

            # Verify data payload
            call_args = mock_send.call_args[0][0]
            assert call_args.data is not None
            assert call_args.data["type"] == "weather_alert"

    def test_send_notification_high_priority(self, firebase_client):
        """Test sending high priority notification"""
        from src.firebase_client import NotificationPriority

        firebase_client._initialized = True

        with patch("firebase_admin.messaging.send", return_value="msg-123") as mock_send:
            result = firebase_client.send_notification(
                token="device-token-123",
                title="Critical Alert",
                body="Immediate action required",
                priority=NotificationPriority.CRITICAL,
            )

            assert result == "msg-123"

            # Verify Android config has high priority
            call_args = mock_send.call_args[0][0]
            assert call_args.android is not None
            assert call_args.android.priority == "high"

    def test_send_notification_with_image(self, firebase_client):
        """Test sending notification with image"""
        firebase_client._initialized = True

        with patch("firebase_admin.messaging.send", return_value="msg-123") as mock_send:
            result = firebase_client.send_notification(
                token="device-token-123",
                title="Alert",
                body="Check this out",
                image_url="https://example.com/image.jpg",
            )

            assert result == "msg-123"

            # Verify notification has image
            call_args = mock_send.call_args[0][0]
            assert call_args.notification.image == "https://example.com/image.jpg"

    def test_send_notification_not_initialized(self, firebase_client):
        """Test sending notification when client not initialized"""
        firebase_client._initialized = False

        result = firebase_client.send_notification(
            token="device-token-123", title="Test", body="Test"
        )

        assert result is None

    def test_send_notification_with_error(self, firebase_client):
        """Test notification sending handles errors"""
        firebase_client._initialized = True

        with patch("firebase_admin.messaging.send", side_effect=Exception("Send failed")):
            result = firebase_client.send_notification(
                token="device-token-123", title="Test", body="Test"
            )

            assert result is None


class TestTopicNotifications:
    """Test sending notifications to topics"""

    def test_send_to_topic_success(self, firebase_client):
        """Test successful topic notification"""
        firebase_client._initialized = True

        with patch("firebase_admin.messaging.send", return_value="msg-topic-123") as mock_send:
            result = firebase_client.send_to_topic(
                topic="weather_alerts",
                title="Weather Alert",
                body="Storm approaching",
                title_ar="تنبيه طقس",
                body_ar="عاصفة قادمة",
            )

            assert result == "msg-topic-123"

            # Verify topic was set
            call_args = mock_send.call_args[0][0]
            assert call_args.topic == "weather_alerts"

    def test_send_to_topic_with_data(self, firebase_client):
        """Test topic notification with custom data"""
        firebase_client._initialized = True

        with patch("firebase_admin.messaging.send", return_value="msg-123") as mock_send:
            result = firebase_client.send_to_topic(
                topic="pest_alerts_sanaa",
                title="Pest Alert",
                body="Aphids detected",
                data={"crop": "tomato", "severity": "medium"},
            )

            assert result == "msg-123"

    def test_send_to_topic_not_initialized(self, firebase_client):
        """Test topic notification when not initialized"""
        firebase_client._initialized = False

        result = firebase_client.send_to_topic(topic="test_topic", title="Test", body="Test")

        assert result is None


class TestMulticastNotifications:
    """Test sending notifications to multiple devices"""

    def test_send_multicast_success(self, firebase_client):
        """Test successful multicast notification"""
        firebase_client._initialized = True

        # Mock successful response for all tokens
        mock_response = MagicMock()
        mock_response.success_count = 3
        mock_response.failure_count = 0
        mock_response.responses = [
            MagicMock(success=True, message_id="msg-1", exception=None),
            MagicMock(success=True, message_id="msg-2", exception=None),
            MagicMock(success=True, message_id="msg-3", exception=None),
        ]

        tokens = ["token-1", "token-2", "token-3"]

        with patch("firebase_admin.messaging.send_multicast", return_value=mock_response):
            result = firebase_client.send_multicast(
                tokens=tokens,
                title="Broadcast Alert",
                body="Important message",
                title_ar="إشعار جماعي",
                body_ar="رسالة مهمة",
            )

            assert result["success_count"] == 3
            assert result["failure_count"] == 0
            assert len(result["responses"]) == 3

    def test_send_multicast_partial_failure(self, firebase_client):
        """Test multicast with some failures"""
        firebase_client._initialized = True

        mock_response = MagicMock()
        mock_response.success_count = 2
        mock_response.failure_count = 1
        mock_response.responses = [
            MagicMock(success=True, message_id="msg-1", exception=None),
            MagicMock(success=False, message_id=None, exception=Exception("Invalid token")),
            MagicMock(success=True, message_id="msg-3", exception=None),
        ]

        tokens = ["token-1", "invalid-token", "token-3"]

        with patch("firebase_admin.messaging.send_multicast", return_value=mock_response):
            result = firebase_client.send_multicast(tokens=tokens, title="Test", body="Test")

            assert result["success_count"] == 2
            assert result["failure_count"] == 1

    def test_send_multicast_empty_tokens(self, firebase_client):
        """Test multicast with empty token list"""
        firebase_client._initialized = True

        result = firebase_client.send_multicast(tokens=[], title="Test", body="Test")

        assert result["success_count"] == 0
        assert result["failure_count"] == 0

    def test_send_multicast_not_initialized(self, firebase_client):
        """Test multicast when not initialized"""
        firebase_client._initialized = False

        result = firebase_client.send_multicast(
            tokens=["token-1", "token-2"], title="Test", body="Test"
        )

        assert result["success_count"] == 0
        assert result["failure_count"] == 2


class TestTopicSubscription:
    """Test topic subscription management"""

    def test_subscribe_to_topic_single_token(self, firebase_client):
        """Test subscribing single token to topic"""
        firebase_client._initialized = True

        mock_response = MagicMock()
        mock_response.success_count = 1
        mock_response.failure_count = 0

        with patch("firebase_admin.messaging.subscribe_to_topic", return_value=mock_response):
            result = firebase_client.subscribe_to_topic(tokens="token-123", topic="weather_alerts")

            assert result["success_count"] == 1
            assert result["failure_count"] == 0

    def test_subscribe_to_topic_multiple_tokens(self, firebase_client):
        """Test subscribing multiple tokens to topic"""
        firebase_client._initialized = True

        mock_response = MagicMock()
        mock_response.success_count = 3
        mock_response.failure_count = 0

        with patch("firebase_admin.messaging.subscribe_to_topic", return_value=mock_response):
            result = firebase_client.subscribe_to_topic(
                tokens=["token-1", "token-2", "token-3"], topic="pest_alerts"
            )

            assert result["success_count"] == 3

    def test_subscribe_to_topic_with_failures(self, firebase_client):
        """Test topic subscription with some failures"""
        firebase_client._initialized = True

        mock_response = MagicMock()
        mock_response.success_count = 2
        mock_response.failure_count = 1

        with patch("firebase_admin.messaging.subscribe_to_topic", return_value=mock_response):
            result = firebase_client.subscribe_to_topic(
                tokens=["token-1", "invalid-token", "token-3"], topic="alerts"
            )

            assert result["success_count"] == 2
            assert result["failure_count"] == 1

    def test_unsubscribe_from_topic(self, firebase_client):
        """Test unsubscribing from topic"""
        firebase_client._initialized = True

        mock_response = MagicMock()
        mock_response.success_count = 2
        mock_response.failure_count = 0

        with patch("firebase_admin.messaging.unsubscribe_from_topic", return_value=mock_response):
            result = firebase_client.unsubscribe_from_topic(
                tokens=["token-1", "token-2"], topic="weather_alerts"
            )

            assert result["success_count"] == 2
            assert result["failure_count"] == 0


class TestRetryLogic:
    """Test notification retry logic"""

    def test_send_with_retry_success_first_attempt(self, firebase_client):
        """Test retry succeeds on first attempt"""
        firebase_client._initialized = True

        with patch("firebase_admin.messaging.send", return_value="msg-123"):
            result = firebase_client.send_with_retry(
                token="token-123", title="Test", body="Test", max_retries=3
            )

            assert result == "msg-123"

    def test_send_with_retry_success_after_failures(self, firebase_client):
        """Test retry succeeds after initial failures"""
        firebase_client._initialized = True

        # Fail twice, then succeed
        mock_send = MagicMock(side_effect=[None, None, "msg-123"])

        with patch.object(firebase_client, "send_notification", mock_send):
            result = firebase_client.send_with_retry(
                token="token-123", title="Test", body="Test", max_retries=3
            )

            assert result == "msg-123"
            assert mock_send.call_count == 3

    def test_send_with_retry_all_failures(self, firebase_client):
        """Test retry exhausts all attempts"""
        firebase_client._initialized = True

        with patch.object(firebase_client, "send_notification", return_value=None):
            result = firebase_client.send_with_retry(
                token="token-123", title="Test", body="Test", max_retries=3
            )

            assert result is None


class TestGlobalClientInstance:
    """Test global Firebase client instance"""

    def test_get_firebase_client_creates_instance(self):
        """Test getting global client instance"""
        from src.firebase_client import get_firebase_client

        with patch("src.firebase_client._firebase_client", None):
            client = get_firebase_client()

            assert client is not None
            assert isinstance(client, type(client))

    def test_get_firebase_client_auto_initializes(self):
        """Test client auto-initializes with environment credentials"""
        # Reset global client
        import src.firebase_client
        from src.firebase_client import _firebase_client, get_firebase_client

        src.firebase_client._firebase_client = None

        with patch.dict("os.environ", {"FIREBASE_CREDENTIALS_PATH": "/path/to/creds.json"}):
            with patch(
                "src.firebase_client.FirebaseClient.initialize", return_value=True
            ) as mock_init:
                client = get_firebase_client()

                assert client is not None
                mock_init.assert_called_once()


class TestBilingualSupport:
    """Test bilingual (Arabic/English) notification support"""

    def test_notification_with_arabic(self, firebase_client):
        """Test notification with Arabic content"""
        firebase_client._initialized = True

        with patch("firebase_admin.messaging.send", return_value="msg-123") as mock_send:
            result = firebase_client.send_notification(
                token="token-123",
                title="Weather Alert",
                body="Frost expected",
                title_ar="تنبيه طقس",
                body_ar="صقيع متوقع",
            )

            # Verify Arabic content is used in notification
            call_args = mock_send.call_args[0][0]
            assert call_args.notification.title == "تنبيه طقس"
            assert call_args.notification.body == "صقيع متوقع"

            # Verify English is in data payload
            assert "title_en" in call_args.data
            assert call_args.data["title_en"] == "Weather Alert"

    def test_notification_without_arabic(self, firebase_client):
        """Test notification without Arabic content"""
        firebase_client._initialized = True

        with patch("firebase_admin.messaging.send", return_value="msg-123") as mock_send:
            result = firebase_client.send_notification(
                token="token-123", title="Test", body="Test body"
            )

            # Should use English when no Arabic provided
            call_args = mock_send.call_args[0][0]
            assert call_args.notification.title == "Test"
            assert call_args.notification.body == "Test body"


class TestPriorityHandling:
    """Test notification priority levels"""

    def test_critical_priority_android(self, firebase_client):
        """Test critical priority for Android"""
        from src.firebase_client import NotificationPriority

        firebase_client._initialized = True

        with patch("firebase_admin.messaging.send", return_value="msg-123") as mock_send:
            firebase_client.send_notification(
                token="token-123",
                title="Critical",
                body="Critical alert",
                priority=NotificationPriority.CRITICAL,
            )

            call_args = mock_send.call_args[0][0]
            assert call_args.android.priority == "high"
            assert call_args.android.notification.channel_id == "sahool_alerts"

    def test_low_priority_android(self, firebase_client):
        """Test low priority for Android"""
        from src.firebase_client import NotificationPriority

        firebase_client._initialized = True

        with patch("firebase_admin.messaging.send", return_value="msg-123") as mock_send:
            firebase_client.send_notification(
                token="token-123",
                title="Info",
                body="Informational message",
                priority=NotificationPriority.LOW,
            )

            call_args = mock_send.call_args[0][0]
            assert call_args.android.priority == "normal"

    def test_critical_priority_ios(self, firebase_client):
        """Test critical priority for iOS"""
        from src.firebase_client import NotificationPriority

        firebase_client._initialized = True

        with patch("firebase_admin.messaging.send", return_value="msg-123") as mock_send:
            firebase_client.send_notification(
                token="token-123",
                title="Critical",
                body="Critical alert",
                priority=NotificationPriority.CRITICAL,
            )

            call_args = mock_send.call_args[0][0]
            assert call_args.apns.headers["apns-priority"] == "10"
