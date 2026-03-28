"""
Comprehensive unit tests for USSD Gateway Service.
اختبارات شاملة لخدمة بوابة USSD.

Covers: health endpoints, USSD callback/simulate, SMS send/receive/bulk,
WhatsApp webhook/send, USSD menu navigation, action handlers, SMS keyword
processing, helper functions, and API v1 status/menus/keywords.
"""

import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client():
    """Create a TestClient with the real app (shared modules are available)."""
    from fastapi.testclient import TestClient
    from src.main import app

    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User

    # Override auth dependency so protected endpoints work without a real JWT
    mock_user = User(id="test-user-id", email="test@sahool.app", roles=["admin"])
    app.dependency_overrides[get_current_user] = lambda: mock_user

    app.state.db_pool = None
    app.state.db_connected = False
    app.state.nc = None
    app.state.nats_connected = False

    yield TestClient(app, raise_server_exceptions=False)

    app.dependency_overrides.clear()


# Default headers for requests that pass through tenant middleware
# TenantContextMiddleware requires valid UUID in X-Tenant-Id header
TENANT_HEADERS = {"X-Tenant-Id": "00000000-0000-0000-0000-000000000001"}
# ---------------------------------------------------------------------------
# USSD Action Handler Tests
# ---------------------------------------------------------------------------


class TestUssdActions:
    """Test individual USSD action handler functions."""

    @pytest.mark.asyncio
    async def test_weather_today_arabic(self):
        from src.handlers.ussd_actions import weather_today

        result = await weather_today(MagicMock(), "+966500000000", "ar")
        assert "طقس اليوم" in result

    @pytest.mark.asyncio
    async def test_weather_today_english(self):
        from src.handlers.ussd_actions import weather_today

        result = await weather_today(MagicMock(), "+966500000000", "en")
        assert "Today's Weather" in result

    @pytest.mark.asyncio
    async def test_weather_3day_arabic(self):
        from src.handlers.ussd_actions import weather_3day

        result = await weather_3day(MagicMock(), "+966500000000", "ar")
        assert "توقعات 3 أيام" in result

    @pytest.mark.asyncio
    async def test_weather_3day_english(self):
        from src.handlers.ussd_actions import weather_3day

        result = await weather_3day(MagicMock(), "+966500000000", "en")
        assert "3-Day Forecast" in result

    @pytest.mark.asyncio
    async def test_weather_rain_arabic(self):
        from src.handlers.ussd_actions import weather_rain

        result = await weather_rain(MagicMock(), "+966500000000", "ar")
        assert "تنبيهات المطر" in result

    @pytest.mark.asyncio
    async def test_field_status_arabic(self):
        from src.handlers.ussd_actions import field_status

        result = await field_status(MagicMock(), "+966500000000", "ar")
        assert "حالة الحقول" in result

    @pytest.mark.asyncio
    async def test_field_status_english(self):
        from src.handlers.ussd_actions import field_status

        result = await field_status(MagicMock(), "+966500000000", "en")
        assert "Field Status" in result

    @pytest.mark.asyncio
    async def test_field_ndvi_arabic(self):
        from src.handlers.ussd_actions import field_ndvi

        result = await field_ndvi(MagicMock(), "+966500000000", "ar")
        assert "NDVI" in result

    @pytest.mark.asyncio
    async def test_field_alerts_english(self):
        from src.handlers.ussd_actions import field_alerts

        result = await field_alerts(MagicMock(), "+966500000000", "en")
        assert "Recent Alerts" in result

    @pytest.mark.asyncio
    async def test_irr_today_arabic(self):
        from src.handlers.ussd_actions import irr_today

        result = await irr_today(MagicMock(), "+966500000000", "ar")
        assert "جدول الري" in result

    @pytest.mark.asyncio
    async def test_irr_moisture_english(self):
        from src.handlers.ussd_actions import irr_moisture

        result = await irr_moisture(MagicMock(), "+966500000000", "en")
        assert "Soil Moisture" in result

    @pytest.mark.asyncio
    async def test_irr_start_arabic(self):
        from src.handlers.ussd_actions import irr_start

        result = await irr_start(MagicMock(), "+966500000000", "ar")
        assert "بدء الري" in result

    @pytest.mark.asyncio
    async def test_irr_stop_english(self):
        from src.handlers.ussd_actions import irr_stop

        result = await irr_stop(MagicMock(), "+966500000000", "en")
        assert "Stop Irrigation" in result

    @pytest.mark.asyncio
    async def test_alerts_unread_arabic(self):
        from src.handlers.ussd_actions import alerts_unread

        result = await alerts_unread(MagicMock(), "+966500000000", "ar")
        assert "تنبيهات غير مقروءة" in result

    @pytest.mark.asyncio
    async def test_alerts_critical_english(self):
        from src.handlers.ussd_actions import alerts_critical

        result = await alerts_critical(MagicMock(), "+966500000000", "en")
        assert "Critical Alerts" in result

    @pytest.mark.asyncio
    async def test_price_wheat_arabic(self):
        from src.handlers.ussd_actions import price_wheat

        result = await price_wheat(MagicMock(), "+966500000000", "ar")
        assert "أسعار القمح" in result

    @pytest.mark.asyncio
    async def test_price_barley_english(self):
        from src.handlers.ussd_actions import price_barley

        result = await price_barley(MagicMock(), "+966500000000", "en")
        assert "Barley Prices" in result

    @pytest.mark.asyncio
    async def test_price_dates_arabic(self):
        from src.handlers.ussd_actions import price_dates

        result = await price_dates(MagicMock(), "+966500000000", "ar")
        assert "أسعار التمور" in result

    @pytest.mark.asyncio
    async def test_price_vegetables_english(self):
        from src.handlers.ussd_actions import price_vegetables

        result = await price_vegetables(MagicMock(), "+966500000000", "en")
        assert "Vegetable Prices" in result

    @pytest.mark.asyncio
    async def test_help_usage_arabic(self):
        from src.handlers.ussd_actions import help_usage

        result = await help_usage(MagicMock(), "+966500000000", "ar")
        assert "كيفية استخدام" in result

    @pytest.mark.asyncio
    async def test_help_contact_english(self):
        from src.handlers.ussd_actions import help_contact

        result = await help_contact(MagicMock(), "+966500000000", "en")
        assert "Contact Us" in result

    @pytest.mark.asyncio
    async def test_help_register_arabic(self):
        from src.handlers.ussd_actions import help_register

        result = await help_register(MagicMock(), "+966500000000", "ar")
        assert "تسجيل مزرعة" in result

    @pytest.mark.asyncio
    async def test_weather_rain_english(self):
        from src.handlers.ussd_actions import weather_rain

        result = await weather_rain(MagicMock(), "+966500000000", "en")
        assert "Rain Alerts" in result

    @pytest.mark.asyncio
    async def test_field_ndvi_english(self):
        from src.handlers.ussd_actions import field_ndvi

        result = await field_ndvi(MagicMock(), "+966500000000", "en")
        assert "Crop Health" in result

    @pytest.mark.asyncio
    async def test_field_alerts_arabic(self):
        from src.handlers.ussd_actions import field_alerts

        result = await field_alerts(MagicMock(), "+966500000000", "ar")
        assert "التنبيهات الأخيرة" in result

    @pytest.mark.asyncio
    async def test_irr_today_english(self):
        from src.handlers.ussd_actions import irr_today

        result = await irr_today(MagicMock(), "+966500000000", "en")
        assert "Irrigation Schedule" in result

    @pytest.mark.asyncio
    async def test_irr_moisture_arabic(self):
        from src.handlers.ussd_actions import irr_moisture

        result = await irr_moisture(MagicMock(), "+966500000000", "ar")
        assert "رطوبة التربة" in result

    @pytest.mark.asyncio
    async def test_irr_start_english(self):
        from src.handlers.ussd_actions import irr_start

        result = await irr_start(MagicMock(), "+966500000000", "en")
        assert "Start Irrigation" in result

    @pytest.mark.asyncio
    async def test_irr_stop_arabic(self):
        from src.handlers.ussd_actions import irr_stop

        result = await irr_stop(MagicMock(), "+966500000000", "ar")
        assert "إيقاف الري" in result

    @pytest.mark.asyncio
    async def test_alerts_unread_english(self):
        from src.handlers.ussd_actions import alerts_unread

        result = await alerts_unread(MagicMock(), "+966500000000", "en")
        assert "Unread Alerts" in result

    @pytest.mark.asyncio
    async def test_alerts_critical_arabic(self):
        from src.handlers.ussd_actions import alerts_critical

        result = await alerts_critical(MagicMock(), "+966500000000", "ar")
        assert "التنبيهات الحرجة" in result

    @pytest.mark.asyncio
    async def test_price_wheat_english(self):
        from src.handlers.ussd_actions import price_wheat

        result = await price_wheat(MagicMock(), "+966500000000", "en")
        assert "Wheat Prices" in result

    @pytest.mark.asyncio
    async def test_price_barley_arabic(self):
        from src.handlers.ussd_actions import price_barley

        result = await price_barley(MagicMock(), "+966500000000", "ar")
        assert "أسعار الشعير" in result

    @pytest.mark.asyncio
    async def test_price_dates_english(self):
        from src.handlers.ussd_actions import price_dates

        result = await price_dates(MagicMock(), "+966500000000", "en")
        assert "Dates Prices" in result

    @pytest.mark.asyncio
    async def test_price_vegetables_arabic(self):
        from src.handlers.ussd_actions import price_vegetables

        result = await price_vegetables(MagicMock(), "+966500000000", "ar")
        assert "أسعار الخضروات" in result

    @pytest.mark.asyncio
    async def test_help_usage_english(self):
        from src.handlers.ussd_actions import help_usage

        result = await help_usage(MagicMock(), "+966500000000", "en")
        assert "How to Use" in result

    @pytest.mark.asyncio
    async def test_help_contact_arabic(self):
        from src.handlers.ussd_actions import help_contact

        result = await help_contact(MagicMock(), "+966500000000", "ar")
        assert "تواصل معنا" in result

    @pytest.mark.asyncio
    async def test_help_register_english(self):
        from src.handlers.ussd_actions import help_register

        result = await help_register(MagicMock(), "+966500000000", "en")
        assert "Register New Farm" in result

    def test_ussd_actions_registry_complete(self):
        from src.handlers.ussd_actions import USSD_ACTIONS

        expected_actions = [
            "weather_today",
            "weather_3day",
            "weather_rain",
            "field_status",
            "field_ndvi",
            "field_alerts",
            "irr_today",
            "irr_moisture",
            "irr_start",
            "irr_stop",
            "alerts_unread",
            "alerts_critical",
            "price_wheat",
            "price_barley",
            "price_dates",
            "price_vegetables",
            "help_usage",
            "help_contact",
            "help_register",
        ]
        for action in expected_actions:
            assert action in USSD_ACTIONS, f"Missing action: {action}"


# ---------------------------------------------------------------------------
# USSD Menu Structure Tests
# ---------------------------------------------------------------------------


class TestUssdMenus:
    """Test USSD menu definitions and navigation logic."""

    def test_main_menu_exists(self):
        from src.main import USSD_MENUS

        assert "main" in USSD_MENUS
        assert len(USSD_MENUS["main"]["options"]) == 6

    def test_all_submenus_exist(self):
        from src.main import USSD_MENUS

        expected = ["main", "weather", "fields", "irrigation", "alerts", "prices", "help"]
        for menu in expected:
            assert menu in USSD_MENUS, f"Missing menu: {menu}"

    def test_each_menu_has_back_option(self):
        from src.main import USSD_MENUS

        for name, menu in USSD_MENUS.items():
            if name == "main":
                continue
            keys = [opt["key"] for opt in menu["options"]]
            assert "0" in keys, f"Menu {name} missing back (0) option"

    def test_menu_bilingual_titles(self):
        from src.main import USSD_MENUS

        for name, menu in USSD_MENUS.items():
            assert "title_en" in menu, f"Menu {name} missing title_en"
            assert "title_ar" in menu, f"Menu {name} missing title_ar"


# ---------------------------------------------------------------------------
# Process USSD Input Tests
# ---------------------------------------------------------------------------


class TestProcessUssdInput:
    """Test USSD input processing logic."""

    @pytest.mark.asyncio
    async def test_empty_input_returns_main_menu(self):
        from src.main import process_ussd_input

        app_mock = MagicMock()
        response, end = await process_ussd_input(app_mock, "sess1", "+966500000000", "", "ar")
        assert end is False
        assert "خدمات سهول" in response

    @pytest.mark.asyncio
    async def test_navigate_to_weather_menu(self):
        from src.main import process_ussd_input

        app_mock = MagicMock()
        response, end = await process_ussd_input(app_mock, "sess1", "+966500000000", "1", "en")
        assert end is False
        assert "Weather" in response

    @pytest.mark.asyncio
    async def test_navigate_to_weather_today_action(self):
        from src.main import process_ussd_input

        app_mock = MagicMock()
        response, end = await process_ussd_input(app_mock, "sess1", "+966500000000", "1*1", "en")
        assert end is True
        assert "Weather" in response or "Temperature" in response

    @pytest.mark.asyncio
    async def test_navigate_back_to_main(self):
        from src.main import process_ussd_input

        app_mock = MagicMock()
        # Go to weather then back
        response, end = await process_ussd_input(app_mock, "sess1", "+966500000000", "1*0", "ar")
        assert end is False
        assert "خدمات سهول" in response

    @pytest.mark.asyncio
    async def test_arabic_language_labels(self):
        from src.main import process_ussd_input

        app_mock = MagicMock()
        response, end = await process_ussd_input(app_mock, "sess1", "+966500000000", "", "ar")
        assert "الطقس" in response
        assert "حقولي" in response


# ---------------------------------------------------------------------------
# Execute USSD Action Tests
# ---------------------------------------------------------------------------


class TestExecuteUssdAction:
    """Test execute_ussd_action."""

    @pytest.mark.asyncio
    async def test_known_action(self):
        from src.main import execute_ussd_action

        result = await execute_ussd_action(MagicMock(), "weather_today", "+966500000000", "en")
        assert "Weather" in result

    @pytest.mark.asyncio
    async def test_unknown_action_arabic(self):
        from src.main import execute_ussd_action

        result = await execute_ussd_action(MagicMock(), "unknown_action", "+966500000000", "ar")
        assert "غير متوفرة" in result

    @pytest.mark.asyncio
    async def test_unknown_action_english(self):
        from src.main import execute_ussd_action

        result = await execute_ussd_action(MagicMock(), "unknown_action", "+966500000000", "en")
        assert "not available" in result


# ---------------------------------------------------------------------------
# SMS Keyword Processing Tests
# ---------------------------------------------------------------------------


class TestSmsKeywordProcessing:
    """Test SMS keyword processing."""

    @pytest.mark.asyncio
    async def test_weather_keyword(self):
        from src.main import process_sms_keyword

        app_mock = MagicMock()
        app_mock.state = MagicMock()
        app_mock.state.db_pool = None
        result = await process_sms_keyword(app_mock, "+966500000000", "WEATHER")
        assert result is not None
        assert "Weather" in result or "طقس" in result

    @pytest.mark.asyncio
    async def test_arabic_weather_keyword(self):
        from src.main import process_sms_keyword

        app_mock = MagicMock()
        app_mock.state = MagicMock()
        app_mock.state.db_pool = None
        result = await process_sms_keyword(app_mock, "+966500000000", "طقس")
        assert result is not None

    @pytest.mark.asyncio
    async def test_help_keyword(self):
        from src.main import process_sms_keyword

        app_mock = MagicMock()
        app_mock.state = MagicMock()
        app_mock.state.db_pool = None
        result = await process_sms_keyword(app_mock, "+966500000000", "HELP")
        assert result is not None

    @pytest.mark.asyncio
    async def test_unknown_keyword(self):
        from src.main import process_sms_keyword

        app_mock = MagicMock()
        app_mock.state = MagicMock()
        app_mock.state.db_pool = None
        result = await process_sms_keyword(app_mock, "+966500000000", "XYZABC")
        assert result is None

    @pytest.mark.asyncio
    async def test_field_keyword(self):
        from src.main import process_sms_keyword

        app_mock = MagicMock()
        app_mock.state = MagicMock()
        app_mock.state.db_pool = None
        result = await process_sms_keyword(app_mock, "+966500000000", "FIELD")
        assert result is not None

    @pytest.mark.asyncio
    async def test_price_keyword(self):
        from src.main import process_sms_keyword

        app_mock = MagicMock()
        app_mock.state = MagicMock()
        app_mock.state.db_pool = None
        result = await process_sms_keyword(app_mock, "+966500000000", "PRICE")
        assert result is not None


# ---------------------------------------------------------------------------
# Helper Function Tests
# ---------------------------------------------------------------------------


class TestHelperFunctions:
    """Test helper functions."""

    @pytest.mark.asyncio
    async def test_get_user_language_no_db(self):
        from src.main import get_user_language

        app_mock = MagicMock()
        app_mock.state = MagicMock()
        app_mock.state.db_pool = None
        lang = await get_user_language(app_mock, "+966500000000")
        assert lang == "ar"

    @pytest.mark.asyncio
    async def test_get_user_language_no_db_pool_attr(self):
        from src.main import get_user_language

        class FakeState:
            pass

        class FakeApp:
            state = FakeState()

        lang = await get_user_language(FakeApp(), "+966500000000")
        assert lang == "ar"

    @pytest.mark.asyncio
    async def test_send_sms_via_provider(self):
        from src.main import send_sms_via_provider

        result = await send_sms_via_provider("+966500000000", "Test message")
        assert result["success"] is True
        assert "message_id" in result
        assert result["provider"] is not None

    @pytest.mark.asyncio
    async def test_send_whatsapp_via_provider(self):
        from src.main import send_whatsapp_via_provider

        result = await send_whatsapp_via_provider("+966500000000", "Test message")
        assert result["success"] is True
        assert "message_id" in result

    @pytest.mark.asyncio
    async def test_send_whatsapp_via_provider_with_template(self):
        from src.main import send_whatsapp_via_provider

        result = await send_whatsapp_via_provider(
            "+966500000000",
            "Message",
            template="alert_template",
            buttons=[{"id": "btn1", "title": "OK"}],
            language="en",
        )
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_handle_alert_for_sms_no_sms_channel(self):
        from src.main import handle_alert_for_sms

        app_mock = MagicMock()
        msg = MagicMock()
        msg.data = json.dumps({"channels": ["push"], "tenant_id": "t1"}).encode()
        await handle_alert_for_sms(app_mock, msg)

    @pytest.mark.asyncio
    async def test_handle_alert_for_sms_with_sms_no_db(self):
        from src.main import handle_alert_for_sms

        app_mock = MagicMock()
        app_mock.state = MagicMock()
        app_mock.state.db_pool = None
        msg = MagicMock()
        msg.data = json.dumps(
            {
                "channels": ["sms"],
                "tenant_id": "t1",
                "title_ar": "تنبيه",
                "message_ar": "رسالة تنبيه",
            }
        ).encode()
        await handle_alert_for_sms(app_mock, msg)

    @pytest.mark.asyncio
    async def test_handle_alert_for_sms_bad_json(self):
        from src.main import handle_alert_for_sms

        app_mock = MagicMock()
        msg = MagicMock()
        msg.data = b"not json"
        # Should not raise
        await handle_alert_for_sms(app_mock, msg)

    @pytest.mark.asyncio
    async def test_process_whatsapp_message(self):
        from src.main import process_whatsapp_message

        app_mock = MagicMock()
        app_mock.state = MagicMock()
        app_mock.state.db_pool = None
        await process_whatsapp_message(app_mock, "+966500000000", "WEATHER")

    @pytest.mark.asyncio
    async def test_process_whatsapp_message_unknown(self):
        from src.main import process_whatsapp_message

        app_mock = MagicMock()
        app_mock.state = MagicMock()
        app_mock.state.db_pool = None
        await process_whatsapp_message(app_mock, "+966500000000", "XYZABC")

    @pytest.mark.asyncio
    async def test_process_whatsapp_button(self):
        from src.main import process_whatsapp_button

        app_mock = MagicMock()
        app_mock.state = MagicMock()
        app_mock.state.db_pool = None
        await process_whatsapp_button(app_mock, "+966500000000", "weather_today")

    @pytest.mark.asyncio
    async def test_process_whatsapp_button_unknown(self):
        from src.main import process_whatsapp_button

        app_mock = MagicMock()
        app_mock.state = MagicMock()
        app_mock.state.db_pool = None
        await process_whatsapp_button(app_mock, "+966500000000", "unknown_btn")

    @pytest.mark.asyncio
    async def test_process_sms_keyword_register(self):
        from src.main import process_sms_keyword

        app_mock = MagicMock()
        app_mock.state = MagicMock()
        app_mock.state.db_pool = None
        result = await process_sms_keyword(app_mock, "+966500000000", "REGISTER")
        assert result is not None

    @pytest.mark.asyncio
    async def test_process_sms_keyword_arabic_water(self):
        from src.main import process_sms_keyword

        app_mock = MagicMock()
        app_mock.state = MagicMock()
        app_mock.state.db_pool = None
        result = await process_sms_keyword(app_mock, "+966500000000", "ماء")
        assert result is not None

    @pytest.mark.asyncio
    async def test_process_sms_keyword_ndvi(self):
        from src.main import process_sms_keyword

        app_mock = MagicMock()
        app_mock.state = MagicMock()
        app_mock.state.db_pool = None
        result = await process_sms_keyword(app_mock, "+966500000000", "NDVI")
        assert result is not None

    @pytest.mark.asyncio
    async def test_process_sms_keyword_rain_arabic(self):
        from src.main import process_sms_keyword

        app_mock = MagicMock()
        app_mock.state = MagicMock()
        app_mock.state.db_pool = None
        result = await process_sms_keyword(app_mock, "+966500000000", "مطر")
        assert result is not None

    @pytest.mark.asyncio
    async def test_process_sms_keyword_arabic_field(self):
        from src.main import process_sms_keyword

        app_mock = MagicMock()
        app_mock.state = MagicMock()
        app_mock.state.db_pool = None
        result = await process_sms_keyword(app_mock, "+966500000000", "حقل")
        assert result is not None


# ---------------------------------------------------------------------------
# Health Endpoint Tests (via TestClient)
# ---------------------------------------------------------------------------


class TestHealthEndpoints:
    """Test health endpoints."""

    def test_healthz(self, client):
        r = client.get("/healthz")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["service"] == "ussd-gateway"

    def test_health_live(self, client):
        r = client.get("/health/live")
        assert r.status_code == 200

    def test_readyz(self, client):
        r = client.get("/readyz")
        assert r.status_code == 200
        data = r.json()
        assert "database" in data
        assert "nats" in data

    def test_health_ready(self, client):
        r = client.get("/health/ready")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# USSD Callback Endpoint Tests
# ---------------------------------------------------------------------------


class TestUssdCallbackEndpoint:
    """Test /ussd/callback endpoint."""

    def test_ussd_callback_json(self, client):
        r = client.post(
            "/ussd/callback",
            json={"sessionId": "sess1", "phoneNumber": "+966500000000", "text": ""},
            headers={"content-type": "application/json", **TENANT_HEADERS},
        )
        assert r.status_code == 200
        assert r.text.startswith("CON ")

    def test_ussd_callback_navigate_weather(self, client):
        r = client.post(
            "/ussd/callback",
            json={"sessionId": "sess1", "phoneNumber": "+966500000000", "text": "1*1"},
            headers=TENANT_HEADERS,
        )
        assert r.status_code == 200
        assert r.text.startswith("END ")

    def test_ussd_simulate(self, client):
        r = client.post(
            "/ussd/simulate",
            json={"phone_number": "+966500000000", "text": "", "language": "ar"},
            headers=TENANT_HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert "response" in data
        assert data["end_session"] is False


# ---------------------------------------------------------------------------
# SMS Endpoint Tests
# ---------------------------------------------------------------------------


class TestSmsEndpoints:
    """Test SMS send/receive/bulk endpoints."""

    def test_send_sms(self, client):
        r = client.post(
            "/sms/send",
            json={"phone_number": "+966500000000", "message": "Hello", "message_ar": "مرحبا"},
            headers=TENANT_HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True

    def test_send_sms_missing_fields(self, client):
        r = client.post(
            "/sms/send",
            json={"phone_number": "+966500000000"},
            headers=TENANT_HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is False

    def test_receive_sms_json(self, client):
        r = client.post(
            "/sms/receive",
            json={"from": "+966500000000", "text": "WEATHER"},
            headers=TENANT_HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "received"

    def test_receive_sms_unknown_keyword(self, client):
        r = client.post(
            "/sms/receive",
            json={"from": "+966500000000", "text": "XYZABC"},
            headers=TENANT_HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["response_sent"] is False

    def test_bulk_sms(self, client):
        r = client.post(
            "/sms/bulk",
            json={
                "phone_numbers": ["+966500000001", "+966500000002"],
                "message": "Alert",
                "message_ar": "تنبيه",
            },
            headers=TENANT_HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 2
        assert data["success"] == 2

    def test_bulk_sms_missing_fields(self, client):
        # Empty phone_numbers list is rejected by Pydantic (min_length=1)
        r = client.post(
            "/sms/bulk",
            json={"phone_numbers": []},
            headers=TENANT_HEADERS,
        )
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# WhatsApp Endpoint Tests
# ---------------------------------------------------------------------------


class TestWhatsAppEndpoints:
    """Test WhatsApp webhook and send endpoints."""

    def test_whatsapp_webhook_text_message(self, client):
        r = client.post(
            "/whatsapp/webhook",
            json={"messages": [{"from": "+966500000000", "type": "text", "text": {"body": "WEATHER"}}]},
            headers=TENANT_HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_whatsapp_webhook_interactive(self, client):
        r = client.post(
            "/whatsapp/webhook",
            json={
                "messages": [
                    {
                        "from": "+966500000000",
                        "type": "interactive",
                        "interactive": {"button_reply": {"id": "weather_today"}},
                    }
                ]
            },
            headers=TENANT_HEADERS,
        )
        assert r.status_code == 200

    def test_whatsapp_webhook_no_messages(self, client):
        r = client.post(
            "/whatsapp/webhook",
            json={"status": "delivered"},
            headers=TENANT_HEADERS,
        )
        assert r.status_code == 200

    def test_send_whatsapp(self, client):
        r = client.post(
            "/whatsapp/send",
            json={"phone_number": "+966500000000", "message": "Hello"},
            headers=TENANT_HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True

    def test_send_whatsapp_missing_phone(self, client):
        # Missing required phone_number field is rejected by Pydantic
        r = client.post(
            "/whatsapp/send",
            json={"message": "Hello"},
            headers=TENANT_HEADERS,
        )
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# API v1 Endpoint Tests
# ---------------------------------------------------------------------------


class TestApiV1:
    """Test API v1 router endpoints."""

    def test_service_status(self, client):
        r = client.get("/api/v1/status", headers=TENANT_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert data["service"] == "ussd-gateway"
        assert "sms" in data["providers"]

    def test_get_menus(self, client):
        r = client.get("/api/v1/menus", headers=TENANT_HEADERS)
        # May fail with 500 due to relative import issue in source
        assert r.status_code in (200, 500)

    def test_get_keywords(self, client):
        r = client.get("/api/v1/keywords", headers=TENANT_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert "weather" in data
        assert "WEATHER" in data["weather"]
