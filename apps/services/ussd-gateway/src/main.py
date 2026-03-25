"""
USSD Gateway Service - بوابة USSD
SMS and USSD support for basic phones

Features:
- USSD menu navigation for farmers without smartphones
- SMS alerts and notifications
- Weather and advisory via SMS
- WhatsApp Business API integration
"""

import json
import os
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timezone

import asyncpg
import nats
from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from shared.auth.dependencies import get_current_user
from shared.auth.models import User
from shared.errors_py import add_request_id_middleware, setup_exception_handlers
from shared.middleware.tenant_context import TenantContextMiddleware
from shared.observability.logging import get_logger

logger = get_logger(__name__)

# Service info
SERVICE_NAME = "ussd-gateway"
SERVICE_VERSION = "16.0.0"


# ============================================================
# Rate Limiting - تحديد معدل الطلبات
# ============================================================

try:
    from shared.auth.rate_limiting import RateLimiter

    rate_limiter = RateLimiter()  # noqa: F841 — used by middleware
    RATE_LIMITER_AVAILABLE = True
except ImportError:
    rate_limiter = None  # noqa: F841
    RATE_LIMITER_AVAILABLE = False
    logger.warning("Rate limiter not available, endpoints are unprotected")


# ============================================================
# Request Models - نماذج الطلبات (Pydantic)
# ============================================================


class USSDCallbackRequest(BaseModel):
    """USSD callback from telecom provider"""

    sessionId: str = Field(default="", alias="session_id", max_length=256)
    phoneNumber: str = Field(default="", alias="msisdn", max_length=20)
    text: str = Field(default="", max_length=500)

    model_config = {"populate_by_name": True}


class USSDSimulateRequest(BaseModel):
    """USSD simulation request"""

    phone_number: str = Field(default="+966500000000", max_length=20)
    text: str = Field(default="", max_length=500)
    language: str = Field(default="ar", pattern=r"^(ar|en)$")


class SendSMSRequest(BaseModel):
    """Send SMS request"""

    phone_number: str = Field(max_length=20)
    message: str | None = Field(default=None, max_length=1600)
    message_ar: str | None = Field(default=None, max_length=1600)
    tenant_id: str | None = Field(default=None, max_length=128)

    @field_validator("phone_number")
    @classmethod
    def phone_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("phone_number is required")
        return v.strip()


class BulkSMSRequest(BaseModel):
    """Bulk SMS request"""

    phone_numbers: list[str] = Field(min_length=1, max_length=5000)
    message: str | None = Field(default=None, max_length=1600)
    message_ar: str | None = Field(default=None, max_length=1600)
    tenant_id: str | None = Field(default=None, max_length=128)


class WhatsAppSendRequest(BaseModel):
    """WhatsApp send request"""

    phone_number: str = Field(max_length=20)
    message: str | None = Field(default=None, max_length=4096)
    message_ar: str | None = Field(default=None, max_length=4096)
    template: str | None = Field(default=None, max_length=256)
    buttons: list[dict] = Field(default_factory=list, max_length=10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage service lifecycle"""
    logger.info(f"Starting {SERVICE_NAME} v{SERVICE_VERSION}")

    # Database connection
    db_url = os.getenv("DATABASE_URL")
    # Enforce sslmode for non-development database connections
    if db_url and os.getenv("ENVIRONMENT", "development") != "development":
        if "sslmode" not in db_url:
            # Use sslmode=disable for PgBouncer (port 6432) which does not support SSL
            ssl_mode = "disable" if ":6432" in db_url else "require"
            db_url += f"?sslmode={ssl_mode}" if "?" not in db_url else f"&sslmode={ssl_mode}"
    if db_url:
        try:
            app.state.db_pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10)
            app.state.db_connected = True
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            app.state.db_connected = False
    else:
        app.state.db_connected = False

    # NATS connection
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            app.state.nc = await nats.connect(nats_url)
            app.state.nats_connected = True
            logger.info("NATS connection established")

            # Subscribe to alert events for SMS forwarding
            await app.state.nc.subscribe("sahool.*.alert.*", cb=lambda msg: handle_alert_for_sms(app, msg))
        except Exception as e:
            logger.error(f"NATS connection failed: {e}")
            app.state.nats_connected = False
    else:
        app.state.nats_connected = False

    yield

    # Cleanup
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()

    logger.info(f"{SERVICE_NAME} shutdown complete")


app = FastAPI(
    title="USSD Gateway - بوابة USSD",
    description="SMS and USSD support for basic phones - دعم الهواتف البسيطة",
    version=SERVICE_VERSION,
    lifespan=lifespan,
)

# Setup error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# CORS - Configure via environment variable for security
# In production, set CORS_ORIGINS to comma-separated list of allowed origins
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS or ["https://sahool.kafaat.io", "https://admin.sahool.kafaat.io"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

# Tenant context middleware
app.add_middleware(TenantContextMiddleware)


# ============================================================
# USSD Menu Definitions - قوائم USSD
# ============================================================

USSD_MENUS = {
    "main": {
        "title_en": "SAHOOL Services",
        "title_ar": "خدمات سهول",
        "options": [
            {"key": "1", "label_en": "Weather", "label_ar": "الطقس", "next": "weather"},
            {"key": "2", "label_en": "My Fields", "label_ar": "حقولي", "next": "fields"},
            {"key": "3", "label_en": "Irrigation", "label_ar": "الري", "next": "irrigation"},
            {"key": "4", "label_en": "Alerts", "label_ar": "التنبيهات", "next": "alerts"},
            {"key": "5", "label_en": "Market Prices", "label_ar": "أسعار السوق", "next": "prices"},
            {"key": "6", "label_en": "Help", "label_ar": "مساعدة", "next": "help"},
        ],
    },
    "weather": {
        "title_en": "Weather Information",
        "title_ar": "معلومات الطقس",
        "options": [
            {"key": "1", "label_en": "Today", "label_ar": "اليوم", "action": "weather_today"},
            {
                "key": "2",
                "label_en": "3-Day Forecast",
                "label_ar": "توقعات 3 أيام",
                "action": "weather_3day",
            },
            {
                "key": "3",
                "label_en": "Rain Alert",
                "label_ar": "تنبيه مطر",
                "action": "weather_rain",
            },
            {"key": "0", "label_en": "Back", "label_ar": "رجوع", "next": "main"},
        ],
    },
    "fields": {
        "title_en": "My Fields",
        "title_ar": "حقولي",
        "options": [
            {
                "key": "1",
                "label_en": "Field Status",
                "label_ar": "حالة الحقل",
                "action": "field_status",
            },
            {
                "key": "2",
                "label_en": "NDVI Health",
                "label_ar": "صحة المحصول",
                "action": "field_ndvi",
            },
            {
                "key": "3",
                "label_en": "Recent Alerts",
                "label_ar": "التنبيهات الأخيرة",
                "action": "field_alerts",
            },
            {"key": "0", "label_en": "Back", "label_ar": "رجوع", "next": "main"},
        ],
    },
    "irrigation": {
        "title_en": "Irrigation",
        "title_ar": "الري",
        "options": [
            {
                "key": "1",
                "label_en": "Today's Schedule",
                "label_ar": "جدول اليوم",
                "action": "irr_today",
            },
            {
                "key": "2",
                "label_en": "Soil Moisture",
                "label_ar": "رطوبة التربة",
                "action": "irr_moisture",
            },
            {
                "key": "3",
                "label_en": "Start Irrigation",
                "label_ar": "بدء الري",
                "action": "irr_start",
            },
            {
                "key": "4",
                "label_en": "Stop Irrigation",
                "label_ar": "إيقاف الري",
                "action": "irr_stop",
            },
            {"key": "0", "label_en": "Back", "label_ar": "رجوع", "next": "main"},
        ],
    },
    "alerts": {
        "title_en": "My Alerts",
        "title_ar": "تنبيهاتي",
        "options": [
            {
                "key": "1",
                "label_en": "Unread Alerts",
                "label_ar": "تنبيهات غير مقروءة",
                "action": "alerts_unread",
            },
            {
                "key": "2",
                "label_en": "Critical Alerts",
                "label_ar": "تنبيهات حرجة",
                "action": "alerts_critical",
            },
            {
                "key": "3",
                "label_en": "Alert Settings",
                "label_ar": "إعدادات التنبيهات",
                "next": "alert_settings",
            },
            {"key": "0", "label_en": "Back", "label_ar": "رجوع", "next": "main"},
        ],
    },
    "prices": {
        "title_en": "Market Prices",
        "title_ar": "أسعار السوق",
        "options": [
            {"key": "1", "label_en": "Wheat", "label_ar": "القمح", "action": "price_wheat"},
            {"key": "2", "label_en": "Barley", "label_ar": "الشعير", "action": "price_barley"},
            {"key": "3", "label_en": "Dates", "label_ar": "التمور", "action": "price_dates"},
            {
                "key": "4",
                "label_en": "Vegetables",
                "label_ar": "الخضروات",
                "action": "price_vegetables",
            },
            {"key": "0", "label_en": "Back", "label_ar": "رجوع", "next": "main"},
        ],
    },
    "help": {
        "title_en": "Help",
        "title_ar": "مساعدة",
        "options": [
            {
                "key": "1",
                "label_en": "How to use",
                "label_ar": "كيفية الاستخدام",
                "action": "help_usage",
            },
            {
                "key": "2",
                "label_en": "Contact Support",
                "label_ar": "تواصل مع الدعم",
                "action": "help_contact",
            },
            {
                "key": "3",
                "label_en": "Register Farm",
                "label_ar": "تسجيل مزرعة",
                "action": "help_register",
            },
            {"key": "0", "label_en": "Back", "label_ar": "رجوع", "next": "main"},
        ],
    },
}


# ============================================================
# Health Endpoints
# ============================================================


@app.get("/healthz")
@app.get("/health/live")
async def health():
    """Liveness probe"""
    return {"status": "ok", "service": SERVICE_NAME, "version": SERVICE_VERSION}


@app.get("/readyz")
@app.get("/health/ready")
async def readiness():
    """Readiness probe"""
    return {
        "status": "ok",
        "database": getattr(app.state, "db_connected", False),
        "nats": getattr(app.state, "nats_connected", False),
    }


# ============================================================
# USSD Endpoints - نقاط USSD
# ============================================================


@app.post("/ussd/callback")
async def ussd_callback(request: Request):
    """
    Handle USSD callback from telecom provider
    معالجة استدعاء USSD من مزود الاتصالات

    Supports Africa's Talking, Infobip, and local telcos
    """
    # Parse request based on provider format
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        data = await request.json()
    else:
        # Form data (Africa's Talking format)
        form = await request.form()
        data = dict(form)

    # Validate input via Pydantic
    validated = USSDCallbackRequest(
        sessionId=data.get("sessionId", data.get("session_id", "")),
        phoneNumber=data.get("phoneNumber", data.get("msisdn", "")),
        text=data.get("text", ""),
    )

    session_id = validated.sessionId
    phone_number = validated.phoneNumber
    text = validated.text

    logger.info("USSD request: phone=%s, text_len=%d", phone_number[-4:] if phone_number else "?", len(text))

    # Determine user language preference
    language = await get_user_language(app, phone_number)

    # Process USSD input and generate response
    response_text, end_session = await process_ussd_input(app, session_id, phone_number, text, language)

    # Format response for telecom provider
    if end_session:
        return Response(content=f"END {response_text}", media_type="text/plain")
    else:
        return Response(content=f"CON {response_text}", media_type="text/plain")


@app.post("/ussd/simulate")
async def ussd_simulate(body: USSDSimulateRequest):
    """
    Simulate USSD session for testing
    محاكاة جلسة USSD للاختبار
    """
    response_text, end_session = await process_ussd_input(
        app,
        "test-session",
        body.phone_number,
        body.text,
        body.language,
    )

    return {
        "response": response_text,
        "end_session": end_session,
        "language": body.language,
    }


# ============================================================
# SMS Endpoints - نقاط SMS
# ============================================================


@app.post("/sms/send")
async def send_sms(body: SendSMSRequest, current_user: User = Depends(get_current_user)):
    """
    Send SMS to farmer
    إرسال رسالة نصية للمزارع
    """
    phone_number = body.phone_number
    message = body.message
    message_ar = body.message_ar
    tenant_id = body.tenant_id

    if not (message or message_ar):
        return {"success": False, "error": "Missing message or message_ar"}

    # Get user language preference
    language = await get_user_language(app, phone_number)
    final_message = message_ar if language == "ar" else message

    # Send via SMS provider
    result = await send_sms_via_provider(phone_number, final_message)

    # Log event
    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.publish(
            f"sahool.{tenant_id or 'system'}.sms.sent",
            json.dumps(
                {
                    "phone_number": phone_number[-4:],  # Last 4 digits only for privacy
                    "message_length": len(final_message),
                    "language": language,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            ).encode(),
        )

    return {
        "success": result.get("success", False),
        "message_id": result.get("message_id"),
        "language": language,
    }


@app.post("/sms/receive")
async def receive_sms(request: Request):
    """
    Handle incoming SMS from farmer
    معالجة الرسائل الواردة من المزارع

    Supports keyword-based responses
    """
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        data = await request.json()
    else:
        form = await request.form()
        data = dict(form)

    from_number = str(data.get("from", data.get("msisdn", "")))[:20]
    message = str(data.get("text", data.get("message", "")))[:500].strip().upper()

    logger.info("SMS received: from=%s, message_len=%d", from_number[-4:] if from_number else "?", len(message))

    # Process SMS keywords
    response = await process_sms_keyword(app, from_number, message)

    if response:
        await send_sms_via_provider(from_number, response)

    return {"status": "received", "response_sent": bool(response)}


@app.post("/sms/bulk")
async def send_bulk_sms(body: BulkSMSRequest, current_user: User = Depends(get_current_user)):
    """
    Send bulk SMS to multiple farmers
    إرسال رسائل جماعية للمزارعين
    """
    phone_numbers = body.phone_numbers
    message = body.message
    message_ar = body.message_ar

    if not (message or message_ar):
        return {"success": False, "error": "Missing message or message_ar"}

    results = []
    for phone in phone_numbers:
        language = await get_user_language(app, phone)
        final_message = message_ar if language == "ar" else message
        result = await send_sms_via_provider(phone, final_message)
        results.append(
            {
                "phone": phone[-4:],
                "success": result.get("success", False),
            }
        )

    success_count = sum(1 for r in results if r["success"])

    return {
        "total": len(phone_numbers),
        "success": success_count,
        "failed": len(phone_numbers) - success_count,
    }


# ============================================================
# WhatsApp Endpoints - نقاط واتساب
# ============================================================


@app.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """
    Handle WhatsApp Business API webhook
    معالجة webhook واتساب للأعمال
    """
    body = await request.body()
    if len(body) > 1_048_576:  # 1 MB limit
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=413,
            content={"status": "error", "message": "Payload too large"},
        )
    try:
        data = json.loads(body)
    except (json.JSONDecodeError, ValueError):
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid JSON payload"},
        )

    # Handle different webhook types
    if "messages" in data:
        for msg in data["messages"]:
            from_number = msg.get("from", "")
            message_type = msg.get("type", "text")

            if message_type == "text":
                text = msg.get("text", {}).get("body", "")
                await process_whatsapp_message(app, from_number, text)
            elif message_type == "interactive":
                # Handle button clicks
                interactive = msg.get("interactive", {})
                button_id = interactive.get("button_reply", {}).get("id", "")
                await process_whatsapp_button(app, from_number, button_id)

    return {"status": "ok"}


@app.post("/whatsapp/send")
async def send_whatsapp(body: WhatsAppSendRequest, current_user: User = Depends(get_current_user)):
    """
    Send WhatsApp message to farmer
    إرسال رسالة واتساب للمزارع
    """
    phone_number = body.phone_number
    message = body.message
    message_ar = body.message_ar
    template = body.template
    buttons = body.buttons

    language = await get_user_language(app, phone_number)
    final_message = message_ar if language == "ar" else message

    result = await send_whatsapp_via_provider(phone_number, final_message, template, buttons, language)

    return {
        "success": result.get("success", False),
        "message_id": result.get("message_id"),
    }


# ============================================================
# Helper Functions
# ============================================================


async def get_user_language(app: FastAPI, phone_number: str) -> str:
    """Get user's preferred language"""
    if not hasattr(app.state, "db_pool") or not app.state.db_pool:
        return "ar"  # Default to Arabic

    try:
        async with app.state.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT preferred_language
                FROM users
                WHERE phone_number = $1
                """,
                phone_number,
            )
            if row:
                return row["preferred_language"] or "ar"
    except Exception as e:
        logger.warning(f"Error getting user language: {e}")

    return "ar"


async def process_ussd_input(
    app: FastAPI, session_id: str, phone_number: str, text: str, language: str
) -> tuple[str, bool]:
    """
    Process USSD input and return response
    معالجة إدخال USSD وإرجاع الاستجابة
    """
    # Parse navigation path
    inputs = text.split("*") if text else []

    # Determine current menu
    current_menu = "main"
    for inp in inputs:
        menu = USSD_MENUS.get(current_menu)
        if not menu:
            break

        for option in menu.get("options", []):
            if option["key"] == inp:
                if "next" in option:
                    current_menu = option["next"]
                elif "action" in option:
                    # Execute action and return result
                    result = await execute_ussd_action(app, option["action"], phone_number, language)
                    return result, True
                break

    # Build menu response
    menu = USSD_MENUS.get(current_menu, USSD_MENUS["main"])
    title = menu.get(f"title_{language}", menu.get("title_ar"))

    lines = [title, ""]
    for option in menu.get("options", []):
        label = option.get(f"label_{language}", option.get("label_ar"))
        lines.append(f"{option['key']}. {label}")

    return "\n".join(lines), False


async def execute_ussd_action(app: FastAPI, action: str, phone_number: str, language: str) -> str:
    """Execute USSD action and return response"""
    from .handlers.ussd_actions import USSD_ACTIONS

    handler = USSD_ACTIONS.get(action)
    if handler:
        return await handler(app, phone_number, language)

    # Default response
    if language == "ar":
        return "عذراً، هذه الخدمة غير متوفرة حالياً"
    return "Sorry, this service is not available"


async def process_sms_keyword(app: FastAPI, phone_number: str, message: str) -> str | None:
    """
    Process SMS keyword and return response
    معالجة كلمة مفتاحية SMS وإرجاع الاستجابة
    """
    language = await get_user_language(app, phone_number)

    # Keyword mappings (Arabic and English)
    keywords = {
        # Weather
        "WEATHER": ("weather_today", "ar" if language == "ar" else "en"),
        "طقس": ("weather_today", "ar"),
        "RAIN": ("weather_rain", "en"),
        "مطر": ("weather_rain", "ar"),
        # Field status
        "FIELD": ("field_status", "en"),
        "حقل": ("field_status", "ar"),
        "NDVI": ("field_ndvi", language),
        # Irrigation
        "WATER": ("irr_moisture", "en"),
        "ماء": ("irr_moisture", "ar"),
        "ري": ("irr_today", "ar"),
        # Prices
        "PRICE": ("price_wheat", "en"),
        "سعر": ("price_wheat", "ar"),
        # Help
        "HELP": ("help_usage", "en"),
        "مساعدة": ("help_usage", "ar"),
        # Registration
        "REGISTER": ("help_register", "en"),
        "تسجيل": ("help_register", "ar"),
    }

    # Check for keyword
    for keyword, (action, resp_lang) in keywords.items():
        if message.startswith(keyword):
            from .handlers.ussd_actions import USSD_ACTIONS

            handler = USSD_ACTIONS.get(action)
            if handler:
                return await handler(app, phone_number, resp_lang)

    return None


async def process_whatsapp_message(app: FastAPI, phone_number: str, text: str):
    """Process incoming WhatsApp message"""
    # Similar to SMS processing but with rich responses
    response = await process_sms_keyword(app, phone_number, text.upper())
    if response:
        await send_whatsapp_via_provider(phone_number, response)


async def process_whatsapp_button(app: FastAPI, phone_number: str, button_id: str):
    """Process WhatsApp button click"""
    language = await get_user_language(app, phone_number)
    from .handlers.ussd_actions import USSD_ACTIONS

    handler = USSD_ACTIONS.get(button_id)
    if handler:
        response = await handler(app, phone_number, language)
        await send_whatsapp_via_provider(phone_number, response)


async def send_sms_via_provider(phone_number: str, message: str) -> dict:
    """
    Send SMS via configured provider
    إرسال SMS عبر المزود المكوّن

    Supports: Africa's Talking, Twilio, Unifonic (Saudi)
    """
    provider = os.getenv("SMS_PROVIDER", "unifonic")

    logger.info(f"Sending SMS via {provider} to {phone_number[-4:]}")

    # In production, integrate with actual provider
    # For now, log and return success
    return {
        "success": True,
        "message_id": f"sms_{datetime.now(UTC).timestamp()}",
        "provider": provider,
    }


async def send_whatsapp_via_provider(
    phone_number: str,
    message: str,
    template: str | None = None,
    buttons: list | None = None,
    language: str = "ar",
) -> dict:
    """
    Send WhatsApp message via Business API
    إرسال رسالة واتساب عبر API للأعمال
    """
    logger.info(f"Sending WhatsApp to {phone_number[-4:]}")

    # In production, integrate with Meta WhatsApp Business API
    return {
        "success": True,
        "message_id": f"wa_{datetime.now(UTC).timestamp()}",
    }


async def handle_alert_for_sms(app: FastAPI, msg):
    """
    Handle NATS alert event and forward to SMS if needed
    معالجة تنبيه NATS وإعادة توجيهه إلى SMS
    """
    try:
        data = json.loads(msg.data.decode())
        channels = data.get("channels", [])

        if "sms" not in channels:
            return

        # Get phone number from tenant/user
        tenant_id = data.get("tenant_id")
        data.get("equipment_id")

        # Build SMS message
        title_ar = data.get("title_ar", "تنبيه من سهول")
        message_ar = data.get("message_ar", "")

        sms_text = f"{title_ar}\n{message_ar[:140]}"  # Limit to SMS length

        # Get phone numbers for notification (batched to prevent memory exhaustion)
        if hasattr(app.state, "db_pool") and app.state.db_pool:
            async with app.state.db_pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT phone_number
                    FROM user_notification_settings
                    WHERE tenant_id = $1
                    AND sms_enabled = true
                    AND alert_types @> $2
                    LIMIT 5000
                    """,
                    tenant_id,
                    [data.get("alert_type", "general")],
                )

                for row in rows:
                    await send_sms_via_provider(row["phone_number"], sms_text)

    except Exception as e:
        logger.error(f"Error handling alert for SMS: {e}")


# Include API routes
from .api.v1 import router as api_router

app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8183))
    uvicorn.run(app, host="0.0.0.0", port=port)
