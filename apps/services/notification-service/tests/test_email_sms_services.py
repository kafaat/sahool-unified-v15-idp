"""
SAHOOL Notification Service - Email and SMS Services Tests
Comprehensive tests for email (SendGrid) and SMS (Twilio) integrations
Coverage: Email sending, SMS sending, bulk operations, error handling, bilingual support
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestSMSClient:
    """Test SMS client (Twilio) functionality"""

    def test_sms_client_initialization(self):
        """Test SMS client initializes correctly"""
        from src.sms_client import SMSClient

        client = SMSClient()

        assert client._initialized is False
        assert client._client is None

    def test_sms_client_initialize_with_credentials(self):
        """Test SMS client initialization with credentials"""
        from src.sms_client import SMSClient

        with patch("src.sms_client.TwilioClient") as mock_twilio:
            client = SMSClient()
            result = client.initialize(
                account_sid="test_sid", auth_token="test_token", from_number="+1234567890"
            )

            assert result is True
            assert client._initialized is True
            mock_twilio.assert_called_once_with("test_sid", "test_token")

    def test_sms_client_initialize_from_environment(self):
        """Test SMS client initialization from environment variables"""
        from src.sms_client import SMSClient

        with (
            patch.dict(
                "os.environ",
                {
                    "TWILIO_ACCOUNT_SID": "env_sid",
                    "TWILIO_AUTH_TOKEN": "env_token",
                    "TWILIO_FROM_NUMBER": "+1234567890",
                },
            ),
            patch("src.sms_client.TwilioClient"),
        ):
            client = SMSClient()
            result = client.initialize()

            assert result is True

    def test_sms_client_initialize_without_credentials(self):
        """Test SMS client initialization fails without credentials"""
        from src.sms_client import SMSClient

        with patch.dict("os.environ", {}, clear=True):
            client = SMSClient()
            result = client.initialize()

            assert result is False
            assert client._initialized is False

    @pytest.mark.asyncio
    async def test_send_sms_success(self):
        """Test successful SMS sending"""
        from src.sms_client import SMSClient

        client = SMSClient()
        client._initialized = True
        client._from_number = "+1234567890"

        mock_message = MagicMock()
        mock_message.sid = "SM123456"

        mock_twilio_client = MagicMock()
        mock_twilio_client.messages.create = MagicMock(return_value=mock_message)
        client._client = mock_twilio_client

        result = await client.send_sms(
            to="+967771234567", body="Test message", body_ar="رسالة تجريبية"
        )

        assert result == "SM123456"

    @pytest.mark.asyncio
    async def test_send_sms_arabic_content(self):
        """Test SMS sending with Arabic content"""
        from src.sms_client import SMSClient

        client = SMSClient()
        client._initialized = True
        client._from_number = "+1234567890"

        mock_message = MagicMock()
        mock_message.sid = "SM123456"

        mock_twilio_client = MagicMock()
        mock_twilio_client.messages.create = MagicMock(return_value=mock_message)
        client._client = mock_twilio_client

        await client.send_sms(
            to="+967771234567", body="Weather alert", body_ar="تنبيه طقس", language="ar"
        )

        # Verify Arabic content was sent
        call_args = mock_twilio_client.messages.create.call_args
        assert "تنبيه طقس" in str(call_args)

    @pytest.mark.asyncio
    async def test_send_sms_phone_number_formatting(self):
        """Test SMS sending handles phone number formatting"""
        from src.sms_client import SMSClient

        client = SMSClient()
        client._initialized = True
        client._from_number = "+1234567890"

        mock_message = MagicMock()
        mock_message.sid = "SM123456"

        mock_twilio_client = MagicMock()
        mock_twilio_client.messages.create = MagicMock(return_value=mock_message)
        client._client = mock_twilio_client

        # Send without + prefix
        result = await client.send_sms(
            to="967771234567",  # No + prefix
            body="Test",
        )

        # Should add + prefix
        assert result == "SM123456"

    @pytest.mark.asyncio
    async def test_send_sms_truncates_long_messages(self):
        """Test SMS sending truncates messages exceeding max length"""
        from src.sms_client import SMSClient

        client = SMSClient()
        client._initialized = True
        client._from_number = "+1234567890"

        mock_message = MagicMock()
        mock_message.sid = "SM123456"

        mock_twilio_client = MagicMock()
        mock_twilio_client.messages.create = MagicMock(return_value=mock_message)
        client._client = mock_twilio_client

        long_message = "A" * 2000  # Exceeds default max_length

        result = await client.send_sms(to="+967771234567", body=long_message, max_length=1600)

        # Should still send (truncated)
        assert result == "SM123456"

    @pytest.mark.asyncio
    async def test_send_sms_not_initialized(self):
        """Test SMS sending when client not initialized"""
        from src.sms_client import SMSClient

        client = SMSClient()
        client._initialized = False

        result = await client.send_sms(to="+967771234567", body="Test")

        assert result is None

    @pytest.mark.asyncio
    async def test_send_sms_with_error(self):
        """Test SMS sending handles errors"""
        from src.sms_client import SMSClient
        from twilio.base.exceptions import TwilioRestException

        client = SMSClient()
        client._initialized = True
        client._from_number = "+1234567890"

        mock_twilio_client = MagicMock()
        mock_twilio_client.messages.create = MagicMock(
            side_effect=TwilioRestException(400, "http://test", msg="Invalid phone number")
        )
        client._client = mock_twilio_client

        result = await client.send_sms(to="+invalid", body="Test")

        assert result is None

    @pytest.mark.asyncio
    async def test_send_bulk_sms(self):
        """Test sending bulk SMS"""
        from src.sms_client import SMSClient

        client = SMSClient()
        client._initialized = True

        # Mock send_sms to return success for all
        client.send_sms = AsyncMock(side_effect=["SM1", "SM2", "SM3"])

        result = await client.send_bulk_sms(
            recipients=["+9671", "+9672", "+9673"], body="Bulk message", body_ar="رسالة جماعية"
        )

        assert result["success_count"] == 3
        assert result["failure_count"] == 0

    @pytest.mark.asyncio
    async def test_send_sms_with_retry_success(self):
        """Test SMS sending with retry succeeds"""
        from src.sms_client import SMSClient

        client = SMSClient()
        client._initialized = True

        # Fail first, succeed second
        client.send_sms = AsyncMock(side_effect=[None, "SM123456"])

        result = await client.send_sms_with_retry(
            to="+967771234567",
            body="Test",
            max_retries=3,
            retry_delay=0,  # No delay for testing
        )

        assert result == "SM123456"
        assert client.send_sms.call_count == 2

    def test_validate_phone_number_valid(self):
        """Test phone number validation with valid E.164 format"""
        from src.sms_client import SMSClient

        client = SMSClient()

        assert client.validate_phone_number("+967771234567") is True
        assert client.validate_phone_number("+1234567890") is True

    def test_validate_phone_number_invalid(self):
        """Test phone number validation with invalid formats"""
        from src.sms_client import SMSClient

        client = SMSClient()

        assert client.validate_phone_number("967771234567") is False  # No +
        assert client.validate_phone_number("+123") is False  # Too short
        assert client.validate_phone_number("+12345678901234567890") is False  # Too long
        assert client.validate_phone_number("+967abc") is False  # Contains letters


class TestEmailClient:
    """Test Email client (SendGrid) functionality"""

    def test_email_client_initialization(self):
        """Test Email client initializes correctly"""
        from src.email_client import EmailClient

        client = EmailClient()

        assert client._initialized is False
        assert client._client is None

    def test_email_client_initialize_with_credentials(self):
        """Test Email client initialization with credentials"""
        from src.email_client import EmailClient

        with patch("src.email_client.SendGridAPIClient") as mock_sendgrid:
            client = EmailClient()
            result = client.initialize(
                api_key="test_api_key", from_email="noreply@sahool.com", from_name="SAHOOL Platform"
            )

            assert result is True
            assert client._initialized is True
            mock_sendgrid.assert_called_once_with("test_api_key")

    def test_email_client_initialize_from_environment(self):
        """Test Email client initialization from environment"""
        from src.email_client import EmailClient

        with (
            patch.dict(
                "os.environ",
                {
                    "SENDGRID_API_KEY": "env_api_key",
                    "SENDGRID_FROM_EMAIL": "noreply@sahool.com",
                    "SENDGRID_FROM_NAME": "SAHOOL",
                },
            ),
            patch("src.email_client.SendGridAPIClient"),
        ):
            client = EmailClient()
            result = client.initialize()

            assert result is True

    def test_email_client_initialize_without_credentials(self):
        """Test Email client initialization fails without credentials"""
        from src.email_client import EmailClient

        with patch.dict("os.environ", {}, clear=True):
            client = EmailClient()
            result = client.initialize()

            assert result is False

    @pytest.mark.asyncio
    async def test_send_email_success(self):
        """Test successful email sending"""
        from src.email_client import EmailClient

        client = EmailClient()
        client._initialized = True
        client._from_email = "noreply@sahool.com"
        client._from_name = "SAHOOL"

        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"X-Message-Id": "msg-123456"}

        mock_sendgrid_client = MagicMock()
        mock_sendgrid_client.send = MagicMock(return_value=mock_response)
        client._client = mock_sendgrid_client

        result = await client.send_email(
            to="farmer@example.com",
            subject="Weather Alert",
            body="Frost expected tonight",
            subject_ar="تنبيه طقس",
            body_ar="صقيع متوقع الليلة",
        )

        assert result == "msg-123456"

    @pytest.mark.asyncio
    async def test_send_email_html_content(self):
        """Test sending HTML email"""
        from src.email_client import EmailClient

        client = EmailClient()
        client._initialized = True
        client._from_email = "noreply@sahool.com"
        client._from_name = "SAHOOL"

        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"X-Message-Id": "msg-123456"}

        mock_sendgrid_client = MagicMock()
        mock_sendgrid_client.send = MagicMock(return_value=mock_response)
        client._client = mock_sendgrid_client

        html_body = "<h1>Alert</h1><p>Important message</p>"

        result = await client.send_email(
            to="farmer@example.com", subject="Alert", body=html_body, is_html=True
        )

        assert result == "msg-123456"

    @pytest.mark.asyncio
    async def test_send_email_arabic_content(self):
        """Test email sending with Arabic content"""
        from src.email_client import EmailClient

        client = EmailClient()
        client._initialized = True
        client._from_email = "noreply@sahool.com"
        client._from_name = "SAHOOL"

        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"X-Message-Id": "msg-123456"}

        mock_sendgrid_client = MagicMock()
        mock_sendgrid_client.send = MagicMock(return_value=mock_response)
        client._client = mock_sendgrid_client

        result = await client.send_email(
            to="farmer@example.com",
            subject="Weather Alert",
            body="Frost expected",
            subject_ar="تنبيه طقس",
            body_ar="صقيع متوقع",
            language="ar",
        )

        assert result == "msg-123456"

    @pytest.mark.asyncio
    async def test_send_email_with_cc_bcc(self):
        """Test email sending with CC and BCC"""
        from src.email_client import EmailClient

        client = EmailClient()
        client._initialized = True
        client._from_email = "noreply@sahool.com"
        client._from_name = "SAHOOL"

        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"X-Message-Id": "msg-123456"}

        mock_sendgrid_client = MagicMock()
        mock_sendgrid_client.send = MagicMock(return_value=mock_response)
        client._client = mock_sendgrid_client

        result = await client.send_email(
            to="farmer@example.com",
            subject="Test",
            body="Test body",
            cc=["cc1@example.com", "cc2@example.com"],
            bcc=["bcc@example.com"],
        )

        assert result == "msg-123456"

    @pytest.mark.asyncio
    async def test_send_email_invalid_email(self):
        """Test email validation"""
        from src.email_client import EmailClient

        client = EmailClient()
        client._initialized = True

        result = await client.send_email(
            to="invalid-email",  # No @ sign
            subject="Test",
            body="Test",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_send_email_not_initialized(self):
        """Test email sending when not initialized"""
        from src.email_client import EmailClient

        client = EmailClient()
        client._initialized = False

        result = await client.send_email(to="test@example.com", subject="Test", body="Test")

        assert result is None

    @pytest.mark.asyncio
    async def test_send_email_with_error(self):
        """Test email sending handles errors"""
        from python_http_client.exceptions import HTTPError
        from src.email_client import EmailClient

        client = EmailClient()
        client._initialized = True
        client._from_email = "noreply@sahool.com"
        client._from_name = "SAHOOL"

        mock_sendgrid_client = MagicMock()
        mock_error = HTTPError(None, None, None)
        mock_error.to_dict = {"errors": [{"message": "Invalid API key"}]}
        mock_sendgrid_client.send = MagicMock(side_effect=mock_error)
        client._client = mock_sendgrid_client

        result = await client.send_email(to="test@example.com", subject="Test", body="Test")

        assert result is None

    @pytest.mark.asyncio
    async def test_send_bulk_email(self):
        """Test sending bulk emails"""
        from src.email_client import EmailClient

        client = EmailClient()
        client._initialized = True

        # Mock send_email to return success
        client.send_email = AsyncMock(side_effect=["msg-1", "msg-2", "msg-3"])

        result = await client.send_bulk_email(
            recipients=["user1@example.com", "user2@example.com", "user3@example.com"],
            subject="Broadcast",
            body="Important message",
        )

        assert result["success_count"] == 3
        assert result["failure_count"] == 0

    @pytest.mark.asyncio
    async def test_send_email_with_retry(self):
        """Test email sending with retry logic"""
        from src.email_client import EmailClient

        client = EmailClient()
        client._initialized = True

        # Fail first, succeed second
        client.send_email = AsyncMock(side_effect=[None, "msg-123456"])

        result = await client.send_email_with_retry(
            to="test@example.com", subject="Test", body="Test", max_retries=3, retry_delay=0
        )

        assert result == "msg-123456"
        assert client.send_email.call_count == 2

    @pytest.mark.asyncio
    async def test_send_template_email(self):
        """Test sending email with SendGrid template"""
        from src.email_client import EmailClient

        client = EmailClient()
        client._initialized = True
        client._from_email = "noreply@sahool.com"
        client._from_name = "SAHOOL"

        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"X-Message-Id": "msg-template-123"}

        mock_sendgrid_client = MagicMock()
        mock_sendgrid_client.send = MagicMock(return_value=mock_response)
        client._client = mock_sendgrid_client

        result = await client.send_template_email(
            to="farmer@example.com",
            template_id="d-1234567890",
            template_data={"farmer_name": "Ahmed", "alert_type": "frost", "temperature": -2},
            language="ar",
        )

        assert result == "msg-template-123"

    def test_validate_email_valid(self):
        """Test email validation with valid emails"""
        from src.email_client import EmailClient

        client = EmailClient()

        assert client._validate_email("user@example.com") is True
        assert client._validate_email("test.user+tag@domain.co.uk") is True

    def test_validate_email_invalid(self):
        """Test email validation with invalid emails"""
        from src.email_client import EmailClient

        client = EmailClient()

        assert client._validate_email("invalid") is False
        assert client._validate_email("@example.com") is False
        assert client._validate_email("user@") is False
        assert client._validate_email("user@domain") is True  # Missing TLD is allowed


class TestGlobalClientInstances:
    """Test global client instances and auto-initialization"""

    def test_get_sms_client(self):
        """Test getting global SMS client instance"""
        from src.sms_client import get_sms_client

        client1 = get_sms_client()
        client2 = get_sms_client()

        # Should return same instance
        assert client1 is client2

    def test_get_email_client(self):
        """Test getting global Email client instance"""
        from src.email_client import get_email_client

        client1 = get_email_client()
        client2 = get_email_client()

        # Should return same instance
        assert client1 is client2

    def test_sms_client_auto_initialize(self):
        """Test SMS client auto-initializes with environment variables"""
        import src.sms_client

        # Reset global client
        src.sms_client._sms_client = None

        with (
            patch.dict(
                "os.environ",
                {
                    "TWILIO_ACCOUNT_SID": "test_sid",
                    "TWILIO_AUTH_TOKEN": "test_token",
                    "TWILIO_FROM_NUMBER": "+1234567890",
                },
            ),
            patch("src.sms_client.SMSClient.initialize", return_value=True) as mock_init,
        ):
            from src.sms_client import get_sms_client

            client = get_sms_client()

            assert client is not None
            mock_init.assert_called_once()

    def test_email_client_auto_initialize(self):
        """Test Email client auto-initializes with environment variables"""
        import src.email_client

        # Reset global client
        src.email_client._email_client = None

        with (
            patch.dict(
                "os.environ",
                {"SENDGRID_API_KEY": "test_key", "SENDGRID_FROM_EMAIL": "noreply@sahool.com"},
            ),
            patch("src.email_client.EmailClient.initialize", return_value=True) as mock_init,
        ):
            from src.email_client import get_email_client

            client = get_email_client()

            assert client is not None
            mock_init.assert_called_once()


class TestBilingualSupport:
    """Test bilingual (Arabic/English) support across channels"""

    @pytest.mark.asyncio
    async def test_sms_arabic_english_selection(self):
        """Test SMS selects correct language content"""
        from src.sms_client import SMSClient

        client = SMSClient()
        client._initialized = True
        client._from_number = "+1234567890"

        mock_message = MagicMock()
        mock_message.sid = "SM123"

        mock_twilio_client = MagicMock()
        mock_twilio_client.messages.create = MagicMock(return_value=mock_message)
        client._client = mock_twilio_client

        # Test Arabic
        await client.send_sms(
            to="+967771234567", body="English version", body_ar="النسخة العربية", language="ar"
        )

        # Verify Arabic was used
        call_args = mock_twilio_client.messages.create.call_args
        assert "النسخة العربية" in str(call_args)

    @pytest.mark.asyncio
    async def test_email_arabic_english_selection(self):
        """Test Email selects correct language content"""
        from src.email_client import EmailClient

        client = EmailClient()
        client._initialized = True
        client._from_email = "noreply@sahool.com"
        client._from_name = "SAHOOL"

        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"X-Message-Id": "msg-123"}

        mock_sendgrid_client = MagicMock()
        mock_sendgrid_client.send = MagicMock(return_value=mock_response)
        client._client = mock_sendgrid_client

        # Test Arabic
        result = await client.send_email(
            to="test@example.com",
            subject="English Subject",
            body="English body",
            subject_ar="العنوان العربي",
            body_ar="النص العربي",
            language="ar",
        )

        assert result == "msg-123"
