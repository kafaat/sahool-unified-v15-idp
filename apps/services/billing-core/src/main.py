"""
💰 SAHOOL Billing Core Service v16.0
خدمة الفوترة الأساسية - إدارة الاشتراكات والمدفوعات

Features:
- Plan management with tiered pricing
- Tenant/subscription lifecycle
- Usage-based billing
- Invoice generation
- Payment processing (Stripe + Tharwatt integration)
- Multi-currency support (USD, YER)
- NATS event publishing for billing events
"""

import hashlib
import hmac
import logging
import os
import structlog

# Authentication imports
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime, timedelta, timezone
from decimal import Decimal
from enum import Enum, StrEnum
from pathlib import Path
from typing import Any

import httpx
import nats
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Query,
    Request,
)

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
try:
    from shared.middleware import (
        RequestLoggingMiddleware,
        TenantContextMiddleware,
        setup_cors,
    )
    from shared.observability.middleware import ObservabilityMiddleware
except ImportError:
    RequestLoggingMiddleware = None
    TenantContextMiddleware = None
    setup_cors = None
    ObservabilityMiddleware = None
from nats.js.api import RetentionPolicy
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from . import models as db_models

# Database imports
from .database import check_db_connection, close_db, db_health_check, get_db, init_db
from .repository import BillingRepository

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

# Configure logging early so it can be used in imports
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger("sahool-billing")


def _sanitize_log(value: Any) -> str:
    """Sanitize user-provided values before logging to prevent log injection."""
    return str(value).replace("\r\n", " ").replace("\n", " ").replace("\r", " ")


try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers
except ImportError:
    setup_exception_handlers = None
    add_request_id_middleware = None

# Security headers middleware
try:
    from shared.middleware.security_headers import setup_security_headers

    SECURITY_HEADERS_AVAILABLE = True
except ImportError:
    SECURITY_HEADERS_AVAILABLE = False

    def setup_security_headers(app):
        pass


try:
    from shared.auth.dependencies import (
        get_current_active_user,
        require_roles,
    )

    AUTH_AVAILABLE = True

    async def api_key_auth():
        """Service-to-service API key auth (placeholder when shared auth is available)"""
        return None

except ImportError:
    # SECURITY: Auth module not available - restrict access in production
    AUTH_AVAILABLE = False
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production").lower()

    if ENVIRONMENT not in ("development", "dev", "test", "testing"):
        logger.critical("AUTH MODULE NOT AVAILABLE IN PRODUCTION - SECURITY RISK!")

    async def get_current_active_user():
        """Fallback - blocks access in production, allows in dev only"""
        if ENVIRONMENT not in ("development", "dev", "test", "testing"):
            raise HTTPException(
                status_code=503, detail="Authentication service unavailable"
            )
        logger.warning("Auth bypass active - DEVELOPMENT MODE ONLY")
        return None

    def require_roles(roles):
        """Fallback - blocks access in production, allows in dev only"""

        async def check_roles():
            if ENVIRONMENT not in ("development", "dev", "test", "testing"):
                raise HTTPException(
                    status_code=503, detail="Authorization service unavailable"
                )
            logger.warning(f"Role check bypassed for {roles} - DEVELOPMENT MODE ONLY")
            return None

        return check_roles

    async def api_key_auth():
        """Fallback - blocks access in production, allows in dev only"""
        if ENVIRONMENT not in ("development", "dev", "test", "testing"):
            raise HTTPException(
                status_code=503, detail="API key auth service unavailable"
            )
        return None


# Note: logging already configured above

# =============================================================================
# NATS Configuration - تكوين الرسائل
# =============================================================================

NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")
nats_client = None
js = None  # JetStream context


async def init_nats():
    """Initialize NATS connection and JetStream"""
    global nats_client, js
    try:
        nats_client = await nats.connect(NATS_URL)
        js = nats_client.jetstream()

        # Create billing stream if not exists
        try:
            await js.add_stream(
                name="BILLING",
                subjects=[
                    "sahool.billing.*",
                    "sahool.billing.payment.*",
                    "sahool.billing.subscription.*",
                ],
                retention=RetentionPolicy.LIMITS,
                max_age=86400 * 30,  # 30 days
            )
        except Exception:
            pass  # Stream already exists

        logger.info("NATS connected and JetStream initialized")
    except Exception as e:
        logger.warning(f"NATS connection failed: {e}. Events will be logged only.")


async def publish_event(subject: str, data: dict):
    """Publish event to NATS JetStream"""
    if js:
        try:
            import json

            payload = json.dumps(data, default=str).encode()
            await js.publish(subject, payload)
            logger.info(f"Event published: {subject}")
        except Exception as e:
            logger.warning(f"Failed to publish event {subject}: {e}")
    else:
        safe_data = (
            {k: str(v).replace("\n", " ").replace("\r", " ") for k, v in data.items()}
            if isinstance(data, dict)
            else str(data).replace("\n", " ").replace("\r", " ")
        )
        logger.info(f"Event (local): {subject} - {safe_data}")


# =============================================================================
# App Configuration
# =============================================================================


# =============================================================================
# Scheduled Billing Jobs - الوظائف المجدولة للفوترة
# =============================================================================

scheduler = None


async def job_generate_invoices():
    """
    Generate invoices for subscriptions due for billing
    توليد فواتير للاشتراكات المستحقة للفوترة
    Runs daily at 02:00 UTC
    """
    from .database import get_db_context

    logger.info("Starting scheduled invoice generation...")
    generated = 0
    errors = 0

    try:
        async with get_db_context() as db:
            repo = BillingRepository(db)
            due_subs = await repo.subscriptions.get_due_for_billing()

            for sub in due_subs:
                try:
                    invoice = await generate_invoice_for_subscription(db, sub)
                    if invoice:
                        # Advance next_billing_date
                        next_date = get_billing_period_end(
                            sub.next_billing_date, sub.billing_cycle
                        )
                        await repo.subscriptions.update(
                            sub.id,
                            next_billing_date=next_date,
                            last_billing_date=date.today(),
                        )
                        generated += 1

                        # Publish event
                        await publish_event(
                            "sahool.billing.invoice_generated",
                            {
                                "invoice_id": str(invoice.id),
                                "invoice_number": invoice.invoice_number,
                                "tenant_id": sub.tenant_id,
                                "amount": float(invoice.total),
                            },
                        )
                except Exception as e:
                    errors += 1
                    logger.error(
                        f"Failed to generate invoice for subscription {sub.id}: {e}",
                        exc_info=True,
                    )

    except Exception as e:
        logger.error(f"Invoice generation job failed: {e}", exc_info=True)

    logger.info(f"Invoice generation complete: {generated} generated, {errors} errors")


async def job_mark_overdue_invoices():
    """
    Mark overdue invoices as OVERDUE
    تحديث الفواتير المتأخرة
    Runs daily at 03:00 UTC
    """
    from .database import get_db_context

    logger.info("Starting overdue invoice check...")
    marked = 0

    try:
        async with get_db_context() as db:
            repo = BillingRepository(db)
            overdue_invoices = await repo.invoices.get_overdue()

            for invoice in overdue_invoices:
                if invoice.status != db_models.InvoiceStatus.OVERDUE:
                    await repo.invoices.update(
                        invoice.id, status=db_models.InvoiceStatus.OVERDUE
                    )
                    marked += 1

                    await publish_event(
                        "sahool.billing.invoice_overdue",
                        {
                            "invoice_id": str(invoice.id),
                            "invoice_number": invoice.invoice_number,
                            "tenant_id": invoice.tenant_id,
                            "amount_due": float(invoice.amount_due),
                            "due_date": invoice.due_date.isoformat(),
                        },
                    )

    except Exception as e:
        logger.error(f"Overdue invoice check failed: {e}", exc_info=True)

    logger.info(f"Overdue check complete: {marked} invoices marked overdue")


async def job_handle_trial_expiry():
    """
    Handle trial subscription expiry - convert to active or suspend
    معالجة انتهاء الاشتراكات التجريبية
    Runs daily at 04:00 UTC
    """
    from .database import get_db_context

    logger.info("Starting trial expiry check...")
    expired = 0

    try:
        async with get_db_context() as db:
            repo = BillingRepository(db)
            # Get all trial subscriptions
            by_status = await repo.subscriptions.count_by_status()
            if not by_status.get("trial", 0):
                return

            # Find trials that have expired
            from sqlalchemy import select as sa_select, and_

            result = await db.execute(
                sa_select(db_models.Subscription).where(
                    and_(
                        db_models.Subscription.status
                        == db_models.SubscriptionStatus.TRIAL,
                        db_models.Subscription.trial_end_date <= date.today(),
                    )
                )
            )
            expired_trials = list(result.scalars().all())

            for sub in expired_trials:
                # Check if plan is free - auto-activate. Otherwise suspend.
                plan = await repo.plans.get_by_plan_id(sub.plan_id)
                if plan and plan.tier == db_models.PlanTier.FREE:
                    await repo.subscriptions.update(
                        sub.id, status=db_models.SubscriptionStatus.ACTIVE
                    )
                else:
                    await repo.subscriptions.update(
                        sub.id, status=db_models.SubscriptionStatus.SUSPENDED
                    )

                expired += 1

                await publish_event(
                    "sahool.billing.subscription.trial_expired",
                    {
                        "subscription_id": str(sub.id),
                        "tenant_id": sub.tenant_id,
                        "plan_id": sub.plan_id,
                    },
                )

    except Exception as e:
        logger.error(f"Trial expiry check failed: {e}", exc_info=True)

    logger.info(f"Trial expiry check complete: {expired} trials expired")


async def job_suspend_past_due():
    """
    Suspend subscriptions with invoices overdue > 14 days
    تعليق الاشتراكات ذات الفواتير المتأخرة أكثر من 14 يوم
    Runs daily at 05:00 UTC
    """
    from .database import get_db_context

    logger.info("Starting past-due suspension check...")
    suspended = 0

    try:
        async with get_db_context() as db:
            repo = BillingRepository(db)
            cutoff_date = date.today() - timedelta(days=14)
            overdue_invoices = await repo.invoices.get_overdue(as_of_date=cutoff_date)

            # Group by tenant
            tenants_to_suspend: set[str] = set()
            for inv in overdue_invoices:
                tenants_to_suspend.add(inv.tenant_id)

            for tenant_id in tenants_to_suspend:
                sub = await repo.subscriptions.get_by_tenant(tenant_id)
                if sub and sub.status == db_models.SubscriptionStatus.ACTIVE:
                    await repo.subscriptions.update(
                        sub.id, status=db_models.SubscriptionStatus.PAST_DUE
                    )
                    suspended += 1

                    await publish_event(
                        "sahool.billing.subscription.past_due",
                        {
                            "subscription_id": str(sub.id),
                            "tenant_id": tenant_id,
                        },
                    )

    except Exception as e:
        logger.error(f"Past-due suspension check failed: {e}", exc_info=True)

    logger.info(f"Past-due check complete: {suspended} subscriptions marked past_due")


def start_scheduler():
    """Initialize and start the APScheduler background jobs"""
    global scheduler

    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger

        scheduler = AsyncIOScheduler()

        # Generate invoices daily at 02:00 UTC
        scheduler.add_job(
            job_generate_invoices,
            CronTrigger(hour=2, minute=0),
            id="generate_invoices",
            name="Generate billing invoices",
            replace_existing=True,
        )

        # Mark overdue invoices daily at 03:00 UTC
        scheduler.add_job(
            job_mark_overdue_invoices,
            CronTrigger(hour=3, minute=0),
            id="mark_overdue",
            name="Mark overdue invoices",
            replace_existing=True,
        )

        # Handle trial expiry daily at 04:00 UTC
        scheduler.add_job(
            job_handle_trial_expiry,
            CronTrigger(hour=4, minute=0),
            id="trial_expiry",
            name="Handle trial expiry",
            replace_existing=True,
        )

        # Suspend past-due subscriptions daily at 05:00 UTC
        scheduler.add_job(
            job_suspend_past_due,
            CronTrigger(hour=5, minute=0),
            id="suspend_past_due",
            name="Suspend past-due subscriptions",
            replace_existing=True,
        )

        scheduler.start()
        logger.info("Billing scheduler started with 4 scheduled jobs")

    except ImportError:
        logger.warning("APScheduler not available - scheduled billing jobs disabled")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifespan events"""
    # Initialize NATS
    await init_nats()

    # Initialize Database
    try:
        await init_db()
        db_connected = await check_db_connection()
        if db_connected:
            logger.info("Database initialized and connected successfully")
            # Initialize invoice number sequence
            await init_invoice_sequence()
            # Initialize default plans in database
            await init_default_plans_in_db()
            # Start scheduled billing jobs
            start_scheduler()
        else:
            logger.warning(
                "Database connection check failed - some features may not work"
            )
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.warning("Service will start but database features will be unavailable")

    yield

    # Cleanup
    if scheduler:
        scheduler.shutdown(wait=False)

    if nats_client:
        await nats_client.close()

    await close_db()


app = FastAPI(
    title="SAHOOL Billing Core | خدمة الفوترة",
    version="16.0.0",
    description="Complete billing, subscription, and payment management for SAHOOL platform",
    lifespan=lifespan,
)

# Setup unified error handling
if setup_exception_handlers:
    setup_exception_handlers(app)
if add_request_id_middleware:
    add_request_id_middleware(app)

# Rate Limiting - Security measure for payment endpoints
try:
    from middleware.rate_limiter import setup_rate_limiting

    rate_limiter = setup_rate_limiting(
        app,
        use_redis=os.getenv("REDIS_URL") is not None,
        exclude_paths=[
            "/healthz",
            "/api/v1/webhooks/stripe",
            "/api/v1/webhooks/tharwatt",
        ],
    )
    logger.info("Rate limiting enabled for billing-core")
except ImportError:
    logger.warning("Rate limiter not available - proceeding without rate limiting")

# Security headers - رؤوس الأمان
if SECURITY_HEADERS_AVAILABLE:
    setup_security_headers(app)

# Tenant context middleware - عزل المستأجرين
if TenantContextMiddleware:
    app.add_middleware(TenantContextMiddleware)

# Environment configuration
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "USD")
YER_EXCHANGE_RATE = float(os.getenv("YER_EXCHANGE_RATE", "250"))  # 1 USD = 250 YER

# Tharwatt Payment Gateway Configuration - بوابة ثروات
THARWATT_BASE_URL = os.getenv(
    "THARWATT_BASE_URL", "https://developers-test.tharwatt.com:5253"
)
THARWATT_API_KEY = os.getenv("THARWATT_API_KEY", "")
THARWATT_MERCHANT_ID = os.getenv("THARWATT_MERCHANT_ID", "")
THARWATT_WEBHOOK_SECRET = os.getenv("THARWATT_WEBHOOK_SECRET", "")


# =============================================================================
# Authentication Helpers - مساعدات المصادقة
# =============================================================================


def verify_tenant_access(current_user, tenant_id: str) -> bool:
    """
    Verify user can access the specified tenant
    التحقق من أن المستخدم يمكنه الوصول إلى المستأجر المحدد
    """
    if not AUTH_AVAILABLE or current_user is None:
        # Only bypass in dev/test — production rejects unauthenticated access
        env = os.getenv("ENVIRONMENT", "production").lower()
        return env in ("development", "dev", "test", "testing")

    # Super admins can access any tenant
    if hasattr(current_user, "has_any_role") and current_user.has_any_role(
        ["super_admin"]
    ):
        return True

    # Users can only access their own tenant
    user_tenant = getattr(current_user, "tenant_id", None)
    return user_tenant == tenant_id


def require_tenant_or_admin(current_user, tenant_id: str):
    """
    Require user to be tenant owner or admin, raise 403 if not
    يتطلب أن يكون المستخدم مالك المستأجر أو مسؤول، ورفع 403 إذا لم يكن كذلك
    """
    if not verify_tenant_access(current_user, tenant_id):
        raise HTTPException(
            status_code=403, detail="Access denied - cannot access this tenant's data"
        )


# =============================================================================
# Enums
# =============================================================================


class PlanTier(StrEnum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class BillingCycle(StrEnum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class SubscriptionStatus(StrEnum):
    ACTIVE = "active"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


class InvoiceStatus(StrEnum):
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class PaymentMethod(StrEnum):
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    MOBILE_MONEY = "mobile_money"
    CASH = "cash"
    THARWATT = "tharwatt"  # بوابة ثروات اليمنية


class PaymentStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


class Currency(StrEnum):
    USD = "USD"
    YER = "YER"


# =============================================================================
# Pydantic Models
# =============================================================================


class PlanFeature(BaseModel):
    """ميزة الخطة"""

    name: str
    name_ar: str
    included: bool
    limit: int | None = None  # None = unlimited


class PlanPricing(BaseModel):
    """تسعير الخطة"""

    monthly_usd: Decimal
    quarterly_usd: Decimal
    yearly_usd: Decimal
    setup_fee_usd: Decimal = Decimal("0")


class Plan(BaseModel):
    """خطة الاشتراك"""

    plan_id: str
    name: str
    name_ar: str
    description: str
    description_ar: str
    tier: PlanTier
    pricing: PlanPricing
    features: dict[str, PlanFeature]
    limits: dict[str, int]  # Feature limits
    is_active: bool = True
    trial_days: int = 14
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TenantContact(BaseModel):
    """معلومات الاتصال"""

    name: str
    name_ar: str
    email: EmailStr
    phone: str
    address: str | None = None
    city: str | None = None
    governorate: str | None = None


class Tenant(BaseModel):
    """المستأجر/العميل"""

    tenant_id: str
    name: str
    name_ar: str
    contact: TenantContact
    tax_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
    metadata: dict[str, Any] = {}


class Subscription(BaseModel):
    """الاشتراك"""

    subscription_id: str
    tenant_id: str
    plan_id: str
    status: SubscriptionStatus
    billing_cycle: BillingCycle
    currency: Currency = Currency.USD

    # Dates
    start_date: date
    end_date: date
    trial_end_date: date | None = None
    canceled_at: datetime | None = None

    # Billing
    next_billing_date: date
    last_billing_date: date | None = None

    # Payment
    payment_method: PaymentMethod | None = None
    stripe_subscription_id: str | None = None

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class InvoiceLineItem(BaseModel):
    """بند الفاتورة"""

    description: str
    description_ar: str
    quantity: int = 1
    unit_price: Decimal
    amount: Decimal
    is_usage_based: bool = False


class Invoice(BaseModel):
    """الفاتورة"""

    invoice_id: str
    invoice_number: str  # e.g., SAH-2025-0001
    tenant_id: str
    subscription_id: str

    status: InvoiceStatus
    currency: Currency

    # Dates
    issue_date: date
    due_date: date
    paid_date: date | None = None

    # Amounts
    subtotal: Decimal
    tax_rate: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    total: Decimal
    amount_paid: Decimal = Decimal("0")
    amount_due: Decimal

    # Line items
    line_items: list[InvoiceLineItem]

    # Notes
    notes: str | None = None
    notes_ar: str | None = None

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    stripe_invoice_id: str | None = None


class Payment(BaseModel):
    """الدفعة"""

    payment_id: str
    invoice_id: str
    tenant_id: str

    amount: Decimal
    currency: Currency
    status: PaymentStatus
    method: PaymentMethod

    # Processing
    processed_at: datetime | None = None
    failure_reason: str | None = None

    # External references
    stripe_payment_id: str | None = None
    receipt_url: str | None = None

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UsageRecord(BaseModel):
    """سجل الاستخدام"""

    record_id: str
    tenant_id: str
    metric: str
    quantity: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = {}


# =============================================================================
# Request/Response Models
# =============================================================================


class CreatePlanRequest(BaseModel):
    name: str
    name_ar: str
    description: str
    description_ar: str
    tier: PlanTier
    monthly_price_usd: Decimal
    features: dict[str, bool]
    limits: dict[str, int]
    trial_days: int = 14


class CreateTenantRequest(BaseModel):
    name: str
    name_ar: str
    email: EmailStr
    phone: str
    plan_id: str
    billing_cycle: BillingCycle = BillingCycle.MONTHLY


class UpdateSubscriptionRequest(BaseModel):
    plan_id: str | None = None
    billing_cycle: BillingCycle | None = None
    payment_method: PaymentMethod | None = None


class RecordUsageRequest(BaseModel):
    metric: str
    quantity: int = 1
    metadata: dict[str, Any] = {}


class CreatePaymentRequest(BaseModel):
    invoice_id: str
    amount: Decimal
    method: PaymentMethod
    stripe_token: str | None = None
    phone_number: str | None = (
        None  # Required for Tharwatt payments - مطلوب لمدفوعات ثروات
    )


# =============================================================================
# Database Initialization - Default Plans
# =============================================================================

# Invoice Number Sequence - تسلسل رقم الفاتورة
# Uses PostgreSQL sequence for generating unique invoice numbers
# across multiple instances and service restarts.
INVOICE_SEQUENCE_NAME = "invoice_number_seq"
_invoice_sequence_initialized = False


async def init_invoice_sequence() -> None:
    """
    Initialize the PostgreSQL sequence for invoice numbers.
    تهيئة تسلسل PostgreSQL لأرقام الفواتير

    This creates a sequence if it doesn't exist and sets the starting value
    based on the current year. The sequence is designed to be unique across
    all service instances and persists across restarts.
    """
    global _invoice_sequence_initialized

    if _invoice_sequence_initialized:
        return

    from .database import get_db_context

    try:
        async with get_db_context() as db:
            # Create sequence if it doesn't exist
            # Start from 1 and increment by 1
            # Note: Using literal string to avoid SQL injection warnings
            # INVOICE_SEQUENCE_NAME is a constant defined at module level
            await db.execute(text("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM pg_sequences WHERE schemaname = 'public' AND sequencename = 'invoice_number_seq'
                        ) THEN
                            CREATE SEQUENCE invoice_number_seq
                                START WITH 1
                                INCREMENT BY 1
                                NO MAXVALUE
                                CACHE 10;
                        END IF;
                    END $$;
                """))
            await db.commit()
            _invoice_sequence_initialized = True
            logger.info(
                "Invoice sequence 'invoice_number_seq' initialized successfully"
            )
    except Exception:
        logger.error("Failed to initialize invoice sequence", exc_info=True)
        # Don't raise - allow service to start with fallback


async def get_next_invoice_number() -> str:
    """
    Get the next invoice number from the database sequence.
    الحصول على رقم الفاتورة التالي من تسلسل قاعدة البيانات

    Returns:
        str: Invoice number in format SAH-YYYY-NNNN (e.g., SAH-2025-0001)

    Uses PostgreSQL sequence for atomicity and uniqueness across
    multiple service instances. Falls back to UUID-based number
    if sequence is unavailable.
    """
    from .database import get_db_context

    year = datetime.now(UTC).year

    try:
        async with get_db_context() as db:
            # Get next value from sequence (atomic operation)
            # Note: Using literal string to avoid SQL injection warnings
            result = await db.execute(text("SELECT nextval('invoice_number_seq')"))
            sequence_value = result.scalar()
            await db.commit()

            return f"SAH-{year}-{sequence_value:04d}"
    except Exception:
        # Fallback: Generate unique number using UUID suffix
        # This ensures uniqueness even if sequence fails
        logger.warning("Invoice sequence failed, using fallback", exc_info=True)
        import hashlib

        unique_suffix = (
            hashlib.sha256(f"{datetime.now(UTC).isoformat()}-{uuid.uuid4()}".encode())
            .hexdigest()[:8]
            .upper()
        )
        return f"SAH-{year}-{unique_suffix}"


# NOTE: Legacy INVOICE_COUNTER has been removed for security reasons.
# Use get_next_invoice_number() for production (uses PostgreSQL sequence).
# For tests, generate_invoice_number() now uses UUID-based suffixes.

# =============================================================================
# Arabic Translations - الترجمات العربية
# =============================================================================

# Feature name translations (English -> Arabic)
# ترجمة أسماء الميزات (الإنجليزية -> العربية)
FEATURE_TRANSLATIONS_AR: dict[str, str] = {
    # Core Features - الميزات الأساسية
    "fields": "الحقول",
    "satellite": "تحليل الأقمار الصناعية",
    "satellite_analysis": "تحليل الأقمار الصناعية",
    "satellite_analyses": "تحليلات الأقمار الصناعية",
    "satellite_analyses_per_month": "تحليلات الأقمار الصناعية شهرياً",
    "weather": "توقعات الطقس",
    "weather_forecasts": "توقعات الطقس",
    "irrigation": "تخطيط الري",
    "irrigation_planning": "تخطيط الري",
    "irrigation_smart": "الري الذكي",
    # AI Features - ميزات الذكاء الاصطناعي
    "ai_diagnosis": "تشخيص المحاصيل بالذكاء الاصطناعي",
    "ai_diagnoses": "تشخيصات الذكاء الاصطناعي",
    "ai_diagnoses_per_month": "تشخيصات الذكاء الاصطناعي شهرياً",
    "crop_health": "صحة المحاصيل",
    "crop_health_ai": "صحة المحاصيل بالذكاء الاصطناعي",
    "pest_detection": "اكتشاف الآفات",
    "disease_detection": "اكتشاف الأمراض",
    # Reports & Documents - التقارير والوثائق
    "reports": "تقارير PDF",
    "pdf_reports": "تقارير PDF",
    "pdf_reports_per_month": "تقارير PDF شهرياً",
    "analytics": "التحليلات",
    "advanced_analytics": "التحليلات المتقدمة",
    "export": "تصدير البيانات",
    "data_export": "تصدير البيانات",
    # Support - الدعم
    "support": "الدعم الفني",
    "email_support": "دعم البريد الإلكتروني",
    "priority_support": "دعم أولوية",
    "dedicated_support": "دعم مخصص",
    "phone_support": "دعم هاتفي",
    "24_7_support": "دعم على مدار الساعة",
    # API & Integration - واجهة برمجة التطبيقات والتكامل
    "api_access": "الوصول لواجهة برمجة التطبيقات",
    "api_calls": "استدعاءات API",
    "api_calls_per_day": "استدعاءات API يومياً",
    "custom_integrations": "تكاملات مخصصة",
    "webhook_access": "الوصول للويب هوك",
    "third_party_integrations": "تكاملات الطرف الثالث",
    # Team & Collaboration - الفريق والتعاون
    "team_members": "أعضاء الفريق",
    "multi_user": "متعدد المستخدمين",
    "collaboration": "التعاون",
    "user_management": "إدارة المستخدمين",
    "role_management": "إدارة الأدوار",
    # Storage & Resources - التخزين والموارد
    "storage": "التخزين",
    "storage_gb": "التخزين (جيجابايت)",
    "cloud_storage": "التخزين السحابي",
    "data_retention": "الاحتفاظ بالبيانات",
    "backup": "النسخ الاحتياطي",
    # Enterprise Features - ميزات المؤسسات
    "sla": "ضمان مستوى الخدمة",
    "sla_guarantee": "ضمان SLA",
    "white_label": "العلامة البيضاء",
    "custom_branding": "العلامة التجارية المخصصة",
    "audit_logs": "سجلات التدقيق",
    "compliance": "الامتثال",
    "sso": "تسجيل الدخول الموحد",
    "single_sign_on": "تسجيل الدخول الموحد",
    # Notifications - الإشعارات
    "notifications": "الإشعارات",
    "sms_alerts": "تنبيهات الرسائل النصية",
    "push_notifications": "الإشعارات الفورية",
    "email_alerts": "تنبيهات البريد الإلكتروني",
    # Mapping & GIS - الخرائط ونظم المعلومات الجغرافية
    "mapping": "رسم الخرائط",
    "gis": "نظم المعلومات الجغرافية",
    "field_mapping": "رسم خرائط الحقول",
    "boundary_detection": "اكتشاف الحدود",
    "ndvi": "مؤشر الغطاء النباتي",
    "ndvi_analysis": "تحليل مؤشر الغطاء النباتي",
    # Crop & Farm Management - إدارة المحاصيل والمزرعة
    "crop_planning": "تخطيط المحاصيل",
    "crop_rotation": "تناوب المحاصيل",
    "farm_management": "إدارة المزرعة",
    "inventory": "المخزون",
    "equipment_tracking": "تتبع المعدات",
    # Financial - المالية
    "billing": "الفوترة",
    "invoicing": "إصدار الفواتير",
    "expense_tracking": "تتبع النفقات",
    "cost_analysis": "تحليل التكاليف",
    # Generic / Fallback
    "unlimited": "غير محدود",
    "limited": "محدود",
    "included": "مشمول",
    "not_included": "غير مشمول",
}


def translate_feature_name(feature_name: str) -> str:
    """
    Translate a feature name from English to Arabic.
    ترجمة اسم الميزة من الإنجليزية إلى العربية

    Args:
        feature_name: English feature name (snake_case or regular)

    Returns:
        Arabic translation if found, otherwise returns a formatted version
        of the English name with Arabic note.
    """
    # Normalize the feature name (lowercase, replace spaces with underscores)
    normalized = feature_name.lower().replace(" ", "_").replace("-", "_")

    # Check if we have a direct translation
    if normalized in FEATURE_TRANSLATIONS_AR:
        return FEATURE_TRANSLATIONS_AR[normalized]

    # Check for partial matches (e.g., "fields_limit" -> "الحقول")
    for key, value in FEATURE_TRANSLATIONS_AR.items():
        if normalized.startswith(key) or normalized.endswith(key):
            return value

    # Fallback: Return a formatted version with indication it needs translation
    # Format the English name nicely
    formatted_name = feature_name.replace("_", " ").replace("-", " ").title()
    safe_feature_name = str(feature_name).replace("\n", "").replace("\r", "")[:100]
    logger.warning("Missing Arabic translation for feature: %s", safe_feature_name)
    return f"{formatted_name}"


# Overage rates per metric (USD per unit over limit)
# رسوم تجاوز الاستخدام لكل مقياس (بالدولار لكل وحدة إضافية)
OVERAGE_RATES: dict[str, Decimal] = {
    "fields": Decimal("5.00"),  # $5 per additional field
    "satellite_analyses_per_month": Decimal("0.50"),  # $0.50 per additional analysis
    "ai_diagnoses_per_month": Decimal("0.25"),  # $0.25 per additional diagnosis
    "pdf_reports_per_month": Decimal("0.10"),  # $0.10 per additional report
    "storage_gb": Decimal("2.00"),  # $2 per additional GB
    "api_calls_per_day": Decimal("0.001"),  # $0.001 per additional API call
    "team_members": Decimal("10.00"),  # $10 per additional team member
}

# Plan limits for legacy in-memory invoice generation
# NOTE: This mirrors the limits in init_default_plans_in_db for backward compatibility
PLAN_LIMITS: dict[str, dict[str, int]] = {
    "free": {
        "fields": 3,
        "satellite_analyses_per_month": 10,
        "storage_gb": 1,
        "api_calls_per_day": 100,
    },
    "starter": {
        "fields": 10,
        "satellite_analyses_per_month": 50,
        "ai_diagnoses_per_month": 20,
        "pdf_reports_per_month": 10,
        "storage_gb": 5,
        "api_calls_per_day": 500,
    },
    "professional": {
        "fields": 50,
        "satellite_analyses_per_month": 200,
        "ai_diagnoses_per_month": 100,
        "pdf_reports_per_month": -1,  # Unlimited
        "storage_gb": 25,
        "api_calls_per_day": 2000,
        "team_members": 5,
    },
    "enterprise": {
        "fields": -1,  # Unlimited
        "satellite_analyses_per_month": -1,
        "ai_diagnoses_per_month": -1,
        "pdf_reports_per_month": -1,
        "storage_gb": 100,
        "api_calls_per_day": 10000,
        "team_members": -1,
    },
}


# NOTE: Legacy in-memory USAGE_RECORDS and PLANS dicts have been removed.
# All billing data is now served from the database via BillingRepository.
# See: calculate_overage_charges_db(), generate_invoice_for_subscription()


async def init_default_plans_in_db():
    """
    Initialize default plans in database
    تهيئة الخطط الافتراضية في قاعدة البيانات

    This function is called on startup to ensure default plans exist in the database.
    It uses upsert logic to avoid duplicates.
    """
    from .database import get_db_context

    # Define default plans as dictionaries that can be inserted into the database
    default_plans_data = [
        {
            "plan_id": "free",
            "name": "Free",
            "name_ar": "مجاني",
            "description": "Perfect for small farmers getting started",
            "description_ar": "مثالي للمزارعين الصغار للبدء",
            "tier": db_models.PlanTier.FREE,
            "pricing": {
                "monthly_usd": "0",
                "quarterly_usd": "0",
                "yearly_usd": "0",
                "setup_fee_usd": "0",
            },
            "features": {
                "fields": {
                    "name": "Fields",
                    "name_ar": "الحقول",
                    "included": True,
                    "limit": 3,
                },
                "satellite": {
                    "name": "Satellite Analysis",
                    "name_ar": "تحليل الأقمار",
                    "included": True,
                    "limit": 10,
                },
                "weather": {
                    "name": "Weather Forecasts",
                    "name_ar": "توقعات الطقس",
                    "included": True,
                    "limit": None,
                },
                "irrigation": {
                    "name": "Irrigation Planning",
                    "name_ar": "تخطيط الري",
                    "included": False,
                },
                "ai_diagnosis": {
                    "name": "AI Crop Diagnosis",
                    "name_ar": "تشخيص المحاصيل",
                    "included": False,
                },
                "reports": {
                    "name": "PDF Reports",
                    "name_ar": "تقارير PDF",
                    "included": False,
                },
                "support": {
                    "name": "Email Support",
                    "name_ar": "دعم البريد",
                    "included": True,
                },
            },
            "limits": {
                "fields": 3,
                "satellite_analyses_per_month": 10,
                "storage_gb": 1,
                "api_calls_per_day": 100,
            },
            "trial_days": 0,
        },
        {
            "plan_id": "starter",
            "name": "Starter",
            "name_ar": "المبتدئ",
            "description": "For growing farms with moderate needs",
            "description_ar": "للمزارع المتنامية ذات الاحتياجات المتوسطة",
            "tier": db_models.PlanTier.STARTER,
            "pricing": {
                "monthly_usd": "29",
                "quarterly_usd": "79",
                "yearly_usd": "290",
                "setup_fee_usd": "0",
            },
            "features": {
                "fields": {
                    "name": "Fields",
                    "name_ar": "الحقول",
                    "included": True,
                    "limit": 10,
                },
                "satellite": {
                    "name": "Satellite Analysis",
                    "name_ar": "تحليل الأقمار",
                    "included": True,
                    "limit": 50,
                },
                "weather": {
                    "name": "Weather Forecasts",
                    "name_ar": "توقعات الطقس",
                    "included": True,
                    "limit": None,
                },
                "irrigation": {
                    "name": "Irrigation Planning",
                    "name_ar": "تخطيط الري",
                    "included": True,
                    "limit": None,
                },
                "ai_diagnosis": {
                    "name": "AI Crop Diagnosis",
                    "name_ar": "تشخيص المحاصيل",
                    "included": True,
                    "limit": 20,
                },
                "reports": {
                    "name": "PDF Reports",
                    "name_ar": "تقارير PDF",
                    "included": True,
                    "limit": 10,
                },
                "support": {
                    "name": "Email Support",
                    "name_ar": "دعم البريد",
                    "included": True,
                },
            },
            "limits": {
                "fields": 10,
                "satellite_analyses_per_month": 50,
                "ai_diagnoses_per_month": 20,
                "pdf_reports_per_month": 10,
                "storage_gb": 5,
                "api_calls_per_day": 500,
            },
            "trial_days": 14,
        },
        {
            "plan_id": "professional",
            "name": "Professional",
            "name_ar": "الاحترافي",
            "description": "For professional farmers and agricultural businesses",
            "description_ar": "للمزارعين المحترفين والأعمال الزراعية",
            "tier": db_models.PlanTier.PROFESSIONAL,
            "pricing": {
                "monthly_usd": "99",
                "quarterly_usd": "269",
                "yearly_usd": "990",
                "setup_fee_usd": "0",
            },
            "features": {
                "fields": {
                    "name": "Fields",
                    "name_ar": "الحقول",
                    "included": True,
                    "limit": 50,
                },
                "satellite": {
                    "name": "Satellite Analysis",
                    "name_ar": "تحليل الأقمار",
                    "included": True,
                    "limit": 200,
                },
                "weather": {
                    "name": "Weather Forecasts",
                    "name_ar": "توقعات الطقس",
                    "included": True,
                    "limit": None,
                },
                "irrigation": {
                    "name": "Irrigation Planning",
                    "name_ar": "تخطيط الري",
                    "included": True,
                    "limit": None,
                },
                "ai_diagnosis": {
                    "name": "AI Crop Diagnosis",
                    "name_ar": "تشخيص المحاصيل",
                    "included": True,
                    "limit": 100,
                },
                "reports": {
                    "name": "PDF Reports",
                    "name_ar": "تقارير PDF",
                    "included": True,
                    "limit": None,
                },
                "support": {
                    "name": "Priority Support",
                    "name_ar": "دعم أولوية",
                    "included": True,
                },
                "api_access": {
                    "name": "API Access",
                    "name_ar": "الوصول للـAPI",
                    "included": True,
                },
            },
            "limits": {
                "fields": 50,
                "satellite_analyses_per_month": 200,
                "ai_diagnoses_per_month": 100,
                "pdf_reports_per_month": -1,
                "storage_gb": 25,
                "api_calls_per_day": 2000,
                "team_members": 5,
            },
            "trial_days": 14,
        },
        {
            "plan_id": "enterprise",
            "name": "Enterprise",
            "name_ar": "المؤسسات",
            "description": "Custom solutions for large agricultural operations",
            "description_ar": "حلول مخصصة للعمليات الزراعية الكبيرة",
            "tier": db_models.PlanTier.ENTERPRISE,
            "pricing": {
                "monthly_usd": "499",
                "quarterly_usd": "1349",
                "yearly_usd": "4990",
                "setup_fee_usd": "0",
            },
            "features": {
                "fields": {
                    "name": "Fields",
                    "name_ar": "الحقول",
                    "included": True,
                    "limit": None,
                },
                "satellite": {
                    "name": "Satellite Analysis",
                    "name_ar": "تحليل الأقمار",
                    "included": True,
                    "limit": None,
                },
                "weather": {
                    "name": "Weather Forecasts",
                    "name_ar": "توقعات الطقس",
                    "included": True,
                    "limit": None,
                },
                "irrigation": {
                    "name": "Irrigation Planning",
                    "name_ar": "تخطيط الري",
                    "included": True,
                    "limit": None,
                },
                "ai_diagnosis": {
                    "name": "AI Crop Diagnosis",
                    "name_ar": "تشخيص المحاصيل",
                    "included": True,
                    "limit": None,
                },
                "reports": {
                    "name": "PDF Reports",
                    "name_ar": "تقارير PDF",
                    "included": True,
                    "limit": None,
                },
                "support": {
                    "name": "Dedicated Support",
                    "name_ar": "دعم مخصص",
                    "included": True,
                },
                "api_access": {
                    "name": "API Access",
                    "name_ar": "الوصول للـAPI",
                    "included": True,
                },
                "sla": {
                    "name": "SLA Guarantee",
                    "name_ar": "ضمان SLA",
                    "included": True,
                },
                "custom_integrations": {
                    "name": "Custom Integrations",
                    "name_ar": "تكاملات مخصصة",
                    "included": True,
                },
            },
            "limits": {
                "fields": -1,
                "satellite_analyses_per_month": -1,
                "ai_diagnoses_per_month": -1,
                "pdf_reports_per_month": -1,
                "storage_gb": 100,
                "api_calls_per_day": 10000,
                "team_members": -1,
            },
            "trial_days": 30,
        },
    ]

    try:
        async with get_db_context() as db:
            repo = BillingRepository(db)

            for plan_data in default_plans_data:
                try:
                    await repo.plans.upsert(**plan_data)
                    logger.info(f"Initialized plan: {plan_data['plan_id']}")
                except Exception as e:
                    logger.error(
                        f"Failed to initialize plan {plan_data['plan_id']}: {e}"
                    )

            logger.info("Default plans initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize default plans: {e}")
        # Don't raise - allow service to start even if plan initialization fails


# =============================================================================
# Helper Functions
# =============================================================================


def generate_invoice_number() -> str:
    """
    Generate invoice number (legacy synchronous version).
    توليد رقم الفاتورة (النسخة المتزامنة القديمة)

    NOTE: This is a legacy function kept for backward compatibility with tests.
    For production use, prefer `get_next_invoice_number()` which uses
    a PostgreSQL sequence for proper uniqueness across instances.

    SECURITY: Uses UUID-based suffix to prevent information disclosure
    about invoice volume.
    """
    import warnings

    warnings.warn(
        "generate_invoice_number() is deprecated. Use get_next_invoice_number() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    year = datetime.now(UTC).year
    # Use UUID-based suffix to prevent sequential number exposure
    unique_suffix = uuid.uuid4().hex[:8].upper()
    return f"SAH-{year}-{unique_suffix}"


def convert_to_yer(amount_usd: Decimal) -> Decimal:
    """تحويل المبلغ من الدولار للريال اليمني"""
    return amount_usd * Decimal(str(YER_EXCHANGE_RATE))


def get_plan_price(plan_pricing: dict, cycle: BillingCycle) -> Decimal:
    """
    Get plan price based on billing cycle
    الحصول على سعر الخطة حسب دورة الفوترة

    Args:
        plan_pricing: Plan pricing dict from database (contains monthly_usd, quarterly_usd, yearly_usd)
        cycle: Billing cycle enum

    Returns:
        Decimal: Price for the billing cycle
    """
    if cycle == BillingCycle.MONTHLY:
        return Decimal(str(plan_pricing.get("monthly_usd", "0")))
    elif cycle == BillingCycle.QUARTERLY:
        return Decimal(str(plan_pricing.get("quarterly_usd", "0")))
    else:
        return Decimal(str(plan_pricing.get("yearly_usd", "0")))


def get_billing_period_end(start_date: date, cycle: BillingCycle) -> date:
    """حساب تاريخ انتهاء فترة الفوترة"""
    if cycle == BillingCycle.MONTHLY:
        return start_date + timedelta(days=30)
    elif cycle == BillingCycle.QUARTERLY:
        return start_date + timedelta(days=90)
    else:
        return start_date + timedelta(days=365)


async def check_usage_limit_db(
    db: AsyncSession, tenant_id: str, metric: str
) -> dict[str, Any]:
    """
    Check usage limits for a tenant (database version)
    التحقق من حدود الاستخدام للمستأجر (نسخة قاعدة البيانات)

    Args:
        db: Database session
        tenant_id: Tenant ID
        metric: Metric name (e.g., "satellite_analyses_per_month")

    Returns:
        Dict with allowed, limit, used, remaining
    """
    repo = BillingRepository(db)

    # Check if tenant exists
    tenant = await repo.tenants.get_by_tenant_id(tenant_id)
    if not tenant:
        return {"allowed": False, "reason": "Tenant not found"}

    # Get active subscription
    subscription = await repo.subscriptions.get_by_tenant(tenant_id)
    if not subscription:
        return {"allowed": False, "reason": "No active subscription"}

    # Get plan
    plan = await repo.plans.get_by_plan_id(subscription.plan_id)
    if not plan:
        return {"allowed": False, "reason": "Plan not found"}

    # Check limit
    limit = plan.limits.get(metric, 0)
    if limit == -1:  # Unlimited
        return {"allowed": True, "limit": None, "used": 0, "remaining": "unlimited"}

    # Calculate current usage for the current month
    current_month_start = datetime.now(UTC).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    used = await repo.usage_records.get_metric_count(
        tenant_id=tenant_id,
        metric_type=metric,
        start_date=current_month_start,
    )

    return {
        "allowed": used < limit,
        "limit": limit,
        "used": used,
        "remaining": max(0, limit - used),
    }


async def calculate_overage_charges_db(
    db: AsyncSession,
    tenant_id: str,
    plan_limits: dict[str, int],
) -> list[InvoiceLineItem]:
    """
    Calculate overage charges based on usage exceeding plan limits (database version)
    حساب رسوم تجاوز الاستخدام بناءً على تجاوز حدود الخطة (نسخة قاعدة البيانات)

    Args:
        db: Database session
        tenant_id: Tenant ID for usage lookup
        plan_limits: Plan limits dict from the database plan

    Returns:
        List of InvoiceLineItem for overage charges
    """
    overage_items: list[InvoiceLineItem] = []
    repo = BillingRepository(db)

    if not plan_limits:
        return overage_items

    # Get current month usage from database
    current_month_start = datetime.now(UTC).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    # Calculate overages for each metered feature
    for metric, limit in plan_limits.items():
        # Skip unlimited features (-1) or metrics without overage rates
        if limit == -1 or metric not in OVERAGE_RATES:
            continue

        used = await repo.usage_records.get_metric_count(
            tenant_id=tenant_id,
            metric_type=metric,
            start_date=current_month_start,
        )

        if used > limit:
            excess = used - limit
            rate = OVERAGE_RATES[metric]
            overage_amount = rate * Decimal(str(excess))

            # Create human-readable metric name with Arabic translation
            metric_name = (
                metric.replace("_", " ")
                .replace(" per month", "")
                .replace(" per day", "")
                .title()
            )
            metric_name_ar = translate_feature_name(metric)

            overage_items.append(
                InvoiceLineItem(
                    description=f"Overage: {metric_name} ({excess} units over {limit} limit @ ${rate}/unit)",
                    description_ar=f"تجاوز: {metric_name_ar} ({excess} وحدة إضافية فوق الحد {limit} @ {rate}$/وحدة)",
                    quantity=excess,
                    unit_price=rate,
                    amount=overage_amount,
                    is_usage_based=True,
                )
            )

            logger.info(
                f"Overage charge calculated for tenant {tenant_id}: "
                f"{metric} - {excess} units over limit, amount: ${overage_amount}"
            )

    return overage_items


async def generate_invoice_for_subscription(
    db: AsyncSession,
    subscription: db_models.Subscription,
) -> db_models.Invoice | None:
    """
    Generate an invoice for a subscription (database-driven)
    توليد فاتورة للاشتراك (نسخة قاعدة البيانات)

    Args:
        db: Database session
        subscription: Database subscription model

    Returns:
        Created Invoice or None on failure
    """
    repo = BillingRepository(db)

    # Get plan from database
    plan = await repo.plans.get_by_plan_id(subscription.plan_id)
    if not plan:
        logger.error(
            f"Plan {subscription.plan_id} not found for subscription {subscription.id}"
        )
        return None

    price = get_plan_price(plan.pricing, subscription.billing_cycle)
    cycle_label_ar = (
        "شهري"
        if subscription.billing_cycle == db_models.BillingCycle.MONTHLY
        else (
            "ربع سنوي"
            if subscription.billing_cycle == db_models.BillingCycle.QUARTERLY
            else "سنوي"
        )
    )

    line_items = [
        {
            "description": f"{plan.name} - {subscription.billing_cycle.value.title()}",
            "description_ar": f"{plan.name_ar} - {cycle_label_ar}",
            "quantity": 1,
            "unit_price": float(price),
            "amount": float(price),
            "is_usage_based": False,
        }
    ]

    # Add usage-based overage charges
    overage_items = await calculate_overage_charges_db(
        db=db,
        tenant_id=subscription.tenant_id,
        plan_limits=plan.limits or {},
    )
    for item in overage_items:
        line_items.append(
            {
                "description": item.description,
                "description_ar": item.description_ar,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "amount": float(item.amount),
                "is_usage_based": True,
            }
        )

    subtotal = price + sum(item.amount for item in overage_items)
    tax_amount = Decimal("0")  # Yemen generally has no VAT on agricultural services
    total = subtotal + tax_amount

    # Get next invoice number from database sequence
    invoice_number = await get_next_invoice_number()

    invoice = await repo.invoices.create(
        invoice_number=invoice_number,
        tenant_id=subscription.tenant_id,
        subscription_id=subscription.id,
        currency=db_models.Currency(subscription.currency.value),
        issue_date=date.today(),
        due_date=date.today() + timedelta(days=7),
        subtotal=subtotal,
        tax_amount=tax_amount,
        total=total,
        amount_due=total,
        line_items=line_items,
        status=db_models.InvoiceStatus.PENDING,
        notes_ar="شكراً لاختياركم منصة سهول الزراعية",
    )

    logger.info(
        f"Invoice {invoice.invoice_number} generated for tenant {subscription.tenant_id}, total: ${total}"
    )

    return invoice


# =============================================================================
# API Endpoints - Plans
# =============================================================================


@app.get("/healthz")
async def health_check():
    """Health check endpoint (liveness probe)"""
    return {
        "status": "ok",
        "service": "billing-core",
        "version": "16.0.0",
    }


@app.get("/readyz")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Kubernetes readiness probe - is the service ready to accept traffic?"""
    db_status = await db_health_check()

    # Get plans count from database
    plans_count = 0
    try:
        repo = BillingRepository(db)
        plans = await repo.plans.list_all(active_only=False, limit=1000)
        plans_count = len(plans)
    except Exception:
        pass

    db_ok = db_status.get("status") == "healthy"
    nats_ok = nats_client is not None

    return {
        "status": "ready" if db_ok else "not_ready",
        "service": "billing-core",
        "version": "16.0.0",
        "checks": {
            "database": "connected" if db_ok else "disconnected",
            "nats": "connected" if nats_ok else "disconnected",
        },
        "plans_count": plans_count,
    }


@app.get("/api/v1/plans")
async def list_plans(active_only: bool = True, db: AsyncSession = Depends(get_db)):
    """قائمة الخطط المتاحة"""
    repo = BillingRepository(db)
    plans = await repo.plans.list_all(active_only=active_only, limit=1000)

    return {
        "plans": [
            {
                "plan_id": p.plan_id,
                "name": p.name,
                "name_ar": p.name_ar,
                "tier": p.tier.value,
                "pricing": {
                    "monthly_usd": float(
                        Decimal(str(p.pricing.get("monthly_usd", "0")))
                    ),
                    "monthly_yer": float(
                        convert_to_yer(Decimal(str(p.pricing.get("monthly_usd", "0"))))
                    ),
                    "yearly_usd": float(Decimal(str(p.pricing.get("yearly_usd", "0")))),
                    "yearly_yer": float(
                        convert_to_yer(Decimal(str(p.pricing.get("yearly_usd", "0"))))
                    ),
                },
                "limits": p.limits,
                "trial_days": p.trial_days,
            }
            for p in plans
        ]
    }


@app.get("/api/v1/plans/{plan_id}")
async def get_plan(plan_id: str, db: AsyncSession = Depends(get_db)):
    """تفاصيل خطة محددة"""
    repo = BillingRepository(db)
    plan = await repo.plans.get_by_plan_id(plan_id)

    if not plan:
        raise HTTPException(404, "الخطة غير موجودة")

    return {
        "plan": {
            "plan_id": plan.plan_id,
            "name": plan.name,
            "name_ar": plan.name_ar,
            "description": plan.description,
            "description_ar": plan.description_ar,
            "tier": plan.tier.value,
            "pricing": plan.pricing,
            "features": plan.features,
            "limits": plan.limits,
            "is_active": plan.is_active,
            "trial_days": plan.trial_days,
            "created_at": plan.created_at.isoformat(),
        },
        "pricing_yer": {
            "monthly": float(
                convert_to_yer(Decimal(str(plan.pricing.get("monthly_usd", "0"))))
            ),
            "quarterly": float(
                convert_to_yer(Decimal(str(plan.pricing.get("quarterly_usd", "0"))))
            ),
            "yearly": float(
                convert_to_yer(Decimal(str(plan.pricing.get("yearly_usd", "0"))))
            ),
        },
    }


@app.post("/api/v1/plans")
async def create_plan(
    request: CreatePlanRequest,
    current_user=Depends(require_roles(["super_admin", "tenant_admin"])),
    db: AsyncSession = Depends(get_db),
):
    """إنشاء خطة جديدة (للمسؤولين)"""
    plan_id = request.name.lower().replace(" ", "_")

    repo = BillingRepository(db)

    # Check if plan already exists
    existing_plan = await repo.plans.get_by_plan_id(plan_id)
    if existing_plan:
        raise HTTPException(400, "الخطة موجودة بالفعل")

    # Build features dict with proper Arabic translations
    features = {}
    for feature_name, included in request.features.items():
        limit = request.limits.get(feature_name)
        features[feature_name] = {
            "name": feature_name.replace("_", " ").title(),
            "name_ar": translate_feature_name(feature_name),
            "included": included,
            "limit": limit,
        }

    # Build pricing dict
    pricing = {
        "monthly_usd": str(request.monthly_price_usd),
        "quarterly_usd": str(request.monthly_price_usd * Decimal("2.7")),
        "yearly_usd": str(request.monthly_price_usd * Decimal("10")),
        "setup_fee_usd": "0",
    }

    # Create plan in database
    plan = await repo.plans.create(
        plan_id=plan_id,
        name=request.name,
        name_ar=request.name_ar,
        description=request.description,
        description_ar=request.description_ar,
        tier=request.tier,
        pricing=pricing,
        features=features,
        limits=request.limits,
        trial_days=request.trial_days,
    )

    logger.info(f"Plan created: {plan_id}")

    return {
        "success": True,
        "plan": {
            "plan_id": plan.plan_id,
            "name": plan.name,
            "name_ar": plan.name_ar,
            "tier": plan.tier.value,
            "pricing": plan.pricing,
            "limits": plan.limits,
            "trial_days": plan.trial_days,
        },
    }


# =============================================================================
# API Endpoints - Tenants & Subscriptions
# =============================================================================


@app.post("/api/v1/tenants")
async def create_tenant(
    request: CreateTenantRequest,
    db: AsyncSession = Depends(get_db),
):
    """تسجيل مستأجر جديد مع اشتراك"""
    tenant_id = str(uuid.uuid4())
    repo = BillingRepository(db)

    # Validate plan exists in database
    plan = await repo.plans.get_by_plan_id(request.plan_id)
    if not plan:
        raise HTTPException(400, "الخطة غير موجودة")

    # Create tenant in database
    await repo.tenants.create(
        tenant_id=tenant_id,
        name=request.name,
        name_ar=request.name_ar,
        contact={
            "name": request.name,
            "name_ar": request.name_ar,
            "email": request.email,
            "phone": request.phone,
        },
    )

    # Create subscription in database
    today = date.today()
    trial_end = today + timedelta(days=plan.trial_days) if plan.trial_days > 0 else None

    subscription = await repo.subscriptions.create(
        tenant_id=tenant_id,
        plan_id=request.plan_id,
        billing_cycle=request.billing_cycle,
        start_date=today,
        end_date=get_billing_period_end(today, request.billing_cycle),
        status=(
            db_models.SubscriptionStatus.TRIAL
            if trial_end
            else db_models.SubscriptionStatus.ACTIVE
        ),
        trial_end_date=trial_end,
    )

    logger.info(f"Tenant created: {tenant_id} with subscription {subscription.id}")

    return {
        "success": True,
        "tenant_id": tenant_id,
        "subscription_id": str(subscription.id),
        "status": subscription.status.value,
        "trial_ends": trial_end.isoformat() if trial_end else None,
        "message_ar": f"مرحباً {request.name_ar}! تم إنشاء حسابك بنجاح.",
    }


@app.get("/api/v1/tenants/{tenant_id}")
async def get_tenant(
    tenant_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """معلومات المستأجر"""
    # Verify tenant access
    require_tenant_or_admin(current_user, tenant_id)

    repo = BillingRepository(db)

    # Get tenant from database
    tenant = await repo.tenants.get_by_tenant_id(tenant_id)
    if not tenant:
        raise HTTPException(404, "المستأجر غير موجود")

    # Get subscription
    subscription = await repo.subscriptions.get_by_tenant(tenant_id)

    # Get usage summary
    usage = {}
    if subscription:
        plan = await repo.plans.get_by_plan_id(subscription.plan_id)
        if plan:
            for metric in plan.limits:
                usage[metric] = await check_usage_limit_db(db, tenant_id, metric)

    return {
        "tenant": {
            "tenant_id": tenant.tenant_id,
            "name": tenant.name,
            "name_ar": tenant.name_ar,
            "contact": tenant.contact,
            "tax_id": tenant.tax_id,
            "is_active": tenant.is_active,
            "created_at": tenant.created_at.isoformat(),
        },
        "subscription": (
            {
                "subscription_id": str(subscription.id),
                "plan_id": subscription.plan_id,
                "status": subscription.status.value,
                "billing_cycle": subscription.billing_cycle.value,
                "start_date": subscription.start_date.isoformat(),
                "end_date": subscription.end_date.isoformat(),
            }
            if subscription
            else None
        ),
        "usage": usage,
    }


@app.get("/api/v1/tenants/{tenant_id}/subscription")
async def get_subscription(
    tenant_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """تفاصيل الاشتراك"""
    require_tenant_or_admin(current_user, tenant_id)

    # Get subscription from database
    repo = BillingRepository(db)
    subscription = await repo.subscriptions.get_by_tenant(tenant_id)

    if not subscription:
        raise HTTPException(404, "لا يوجد اشتراك")

    plan = await repo.plans.get_by_plan_id(subscription.plan_id)

    return {
        "subscription": {
            "subscription_id": str(subscription.id),
            "tenant_id": subscription.tenant_id,
            "plan_id": subscription.plan_id,
            "status": subscription.status.value,
            "billing_cycle": subscription.billing_cycle.value,
            "currency": subscription.currency.value,
            "start_date": subscription.start_date.isoformat(),
            "end_date": subscription.end_date.isoformat(),
            "next_billing_date": subscription.next_billing_date.isoformat(),
            "trial_end_date": (
                subscription.trial_end_date.isoformat()
                if subscription.trial_end_date
                else None
            ),
        },
        "plan": (
            {
                "plan_id": plan.plan_id,
                "name": plan.name,
                "name_ar": plan.name_ar,
                "tier": plan.tier.value,
                "pricing": plan.pricing,
                "limits": plan.limits,
            }
            if plan
            else None
        ),
        "days_remaining": (subscription.end_date - date.today()).days,
        "is_trial": subscription.status == db_models.SubscriptionStatus.TRIAL,
    }


@app.patch("/api/v1/tenants/{tenant_id}/subscription")
async def update_subscription(
    tenant_id: str,
    request: UpdateSubscriptionRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """تحديث الاشتراك (ترقية/تخفيض) مع حساب التناسب"""
    require_tenant_or_admin(current_user, tenant_id)

    repo = BillingRepository(db)
    subscription = await repo.subscriptions.get_by_tenant(tenant_id)

    if not subscription:
        raise HTTPException(404, "لا يوجد اشتراك")

    changes = []
    update_data = {}
    proration_credit = Decimal("0")
    proration_charge = Decimal("0")
    old_plan = None
    new_plan = None

    if request.plan_id and request.plan_id != subscription.plan_id:
        new_plan = await repo.plans.get_by_plan_id(request.plan_id)
        if not new_plan:
            raise HTTPException(400, "الخطة غير موجودة")

        old_plan = await repo.plans.get_by_plan_id(subscription.plan_id)

        # Calculate proration
        if old_plan and subscription.status in (
            db_models.SubscriptionStatus.ACTIVE,
            db_models.SubscriptionStatus.TRIAL,
        ):
            old_price = get_plan_price(old_plan.pricing, subscription.billing_cycle)
            new_price = get_plan_price(new_plan.pricing, subscription.billing_cycle)

            # Calculate remaining days in current period
            today = date.today()
            total_days = (subscription.end_date - subscription.start_date).days or 1
            remaining_days = max(0, (subscription.end_date - today).days)

            if remaining_days > 0 and total_days > 0:
                daily_old = old_price / Decimal(str(total_days))
                daily_new = new_price / Decimal(str(total_days))

                # Credit for unused days on old plan
                proration_credit = (daily_old * Decimal(str(remaining_days))).quantize(
                    Decimal("0.01")
                )
                # Charge for remaining days on new plan
                proration_charge = (daily_new * Decimal(str(remaining_days))).quantize(
                    Decimal("0.01")
                )

        update_data["plan_id"] = request.plan_id
        changes.append(f"Plan changed to {new_plan.name}")

    if request.billing_cycle and request.billing_cycle != subscription.billing_cycle:
        update_data["billing_cycle"] = request.billing_cycle
        update_data["end_date"] = get_billing_period_end(
            subscription.start_date, request.billing_cycle
        )
        changes.append(f"Billing cycle changed to {request.billing_cycle.value}")

    if request.payment_method:
        update_data["payment_method"] = request.payment_method
        changes.append(f"Payment method set to {request.payment_method.value}")

    # Update subscription in database
    if update_data:
        subscription = await repo.subscriptions.update(subscription.id, **update_data)

    # Generate proration invoice if there's a difference
    proration_invoice = None
    net_proration = proration_charge - proration_credit
    if net_proration != Decimal("0") and request.plan_id:
        line_items = []
        if proration_credit > 0:
            line_items.append(
                {
                    "description": f"Credit for unused days on {old_plan.name if old_plan else subscription.plan_id}",
                    "description_ar": f"رصيد الأيام المتبقية من {old_plan.name_ar if old_plan else subscription.plan_id}",
                    "quantity": 1,
                    "unit_price": float(-proration_credit),
                    "amount": float(-proration_credit),
                    "is_usage_based": False,
                }
            )
        if proration_charge > 0:
            line_items.append(
                {
                    "description": f"Charge for remaining days on {new_plan.name if new_plan else request.plan_id}",
                    "description_ar": f"رسوم الأيام المتبقية على {new_plan.name_ar if new_plan else request.plan_id}",
                    "quantity": 1,
                    "unit_price": float(proration_charge),
                    "amount": float(proration_charge),
                    "is_usage_based": False,
                }
            )

        if net_proration > 0:
            invoice_number = await get_next_invoice_number()
            proration_invoice = await repo.invoices.create(
                invoice_number=invoice_number,
                tenant_id=tenant_id,
                subscription_id=subscription.id,
                currency=db_models.Currency(subscription.currency.value),
                issue_date=date.today(),
                due_date=date.today() + timedelta(days=7),
                subtotal=net_proration,
                total=net_proration,
                amount_due=net_proration,
                line_items=line_items,
                status=db_models.InvoiceStatus.PENDING,
                notes="Proration invoice for plan change",
                notes_ar="فاتورة تناسبية لتغيير الخطة",
            )
            changes.append(f"Proration invoice generated: {invoice_number}")

        # Publish plan change event
        background_tasks.add_task(
            publish_event,
            "sahool.billing.subscription.plan_changed",
            {
                "subscription_id": str(subscription.id),
                "tenant_id": tenant_id,
                "old_plan": old_plan.plan_id if old_plan else None,
                "new_plan": request.plan_id,
                "proration_credit": float(proration_credit),
                "proration_charge": float(proration_charge),
                "net_proration": float(net_proration),
            },
        )

    return {
        "success": True,
        "subscription": {
            "subscription_id": str(subscription.id),
            "tenant_id": subscription.tenant_id,
            "plan_id": subscription.plan_id,
            "status": subscription.status.value,
            "billing_cycle": subscription.billing_cycle.value,
            "end_date": subscription.end_date.isoformat(),
        },
        "proration": (
            {
                "credit": float(proration_credit),
                "charge": float(proration_charge),
                "net": float(net_proration),
                "invoice_id": str(proration_invoice.id) if proration_invoice else None,
            }
            if proration_credit or proration_charge
            else None
        ),
        "changes": changes,
    }


@app.post("/api/v1/tenants/{tenant_id}/cancel")
async def cancel_subscription(
    tenant_id: str,
    immediate: bool = False,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """إلغاء الاشتراك"""
    require_tenant_or_admin(current_user, tenant_id)

    repo = BillingRepository(db)

    # Get subscription first
    subscription = await repo.subscriptions.get_by_tenant(tenant_id)
    if not subscription:
        raise HTTPException(404, "لا يوجد اشتراك")

    # Cancel it
    subscription = await repo.subscriptions.cancel(
        subscription_id=subscription.id,
        immediate=immediate,
    )

    logger.info(f"Subscription canceled for tenant {tenant_id}, immediate={immediate}")

    return {
        "success": True,
        "status": subscription.status.value,
        "end_date": subscription.end_date.isoformat(),
        "message_ar": (
            "تم إلغاء اشتراكك. سيظل حسابك نشطاً حتى نهاية الفترة المدفوعة."
            if not immediate
            else "تم إلغاء اشتراكك فوراً."
        ),
    }


# =============================================================================
# API Endpoints - Usage & Quotas
# =============================================================================


@app.post("/api/v1/tenants/{tenant_id}/usage")
async def record_usage(
    tenant_id: str,
    request: RecordUsageRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """تسجيل استخدام"""
    require_tenant_or_admin(current_user, tenant_id)

    repo = BillingRepository(db)

    # Check tenant exists in database
    tenant = await repo.tenants.get_by_tenant_id(tenant_id)
    if not tenant:
        raise HTTPException(404, "المستأجر غير موجود")

    # Get subscription
    subscription = await repo.subscriptions.get_by_tenant(tenant_id)
    if not subscription:
        raise HTTPException(404, "لا يوجد اشتراك نشط")

    # Check limit before recording
    limit_check = await check_usage_limit_db(db, tenant_id, request.metric)
    if not limit_check["allowed"]:
        raise HTTPException(
            429,
            f"تم تجاوز الحد الأقصى للاستخدام: {request.metric}. الحد: {limit_check.get('limit', 'N/A')}, المستخدم: {limit_check.get('used', 'N/A')}",
        )

    # Create usage record in database
    record = await repo.usage_records.create(
        subscription_id=subscription.id,
        tenant_id=tenant_id,
        metric_type=request.metric,
        quantity=request.quantity,
        metadata=request.metadata,
    )

    return {
        "success": True,
        "record_id": str(record.id),
        "remaining": limit_check.get("remaining", 0) - request.quantity,
    }


@app.get("/api/v1/tenants/{tenant_id}/quota")
async def get_quota(
    tenant_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """حالة الحصة والاستخدام"""
    require_tenant_or_admin(current_user, tenant_id)

    repo = BillingRepository(db)

    # Get tenant from database
    tenant = await repo.tenants.get_by_tenant_id(tenant_id)
    if not tenant:
        raise HTTPException(404, "المستأجر غير موجود")

    # Get subscription and plan
    subscription = await repo.subscriptions.get_by_tenant(tenant_id)
    if not subscription:
        return {"error": "لا يوجد اشتراك نشط"}

    plan = await repo.plans.get_by_plan_id(subscription.plan_id)
    if not plan:
        return {"error": "الخطة غير موجودة"}

    # Calculate usage for each metric
    usage_summary = {}
    for metric, limit in plan.limits.items():
        check = await check_usage_limit_db(db, tenant_id, metric)
        usage_summary[metric] = {
            "limit": limit if limit != -1 else "unlimited",
            "used": check.get("used", 0),
            "remaining": check.get("remaining", "unlimited" if limit == -1 else 0),
            "percentage": (
                round((check.get("used", 0) / limit) * 100, 1) if limit > 0 else 0
            ),
        }

    return {
        "tenant_id": tenant_id,
        "plan": plan.name,
        "plan_ar": plan.name_ar,
        "subscription_status": subscription.status.value,
        "usage": usage_summary,
        "billing_cycle_ends": subscription.end_date.isoformat(),
    }


@app.get("/api/v1/enforce")
async def enforce_quota(
    x_tenant_id: str | None = Header(default=None),
    metric: str = Query(...),
    api_key: str = Depends(api_key_auth),  # Service-to-service auth
    db: AsyncSession = Depends(get_db),
):
    """التحقق من الصلاحيات (للـ Gateway)"""
    if not x_tenant_id:
        raise HTTPException(400, "Missing x-tenant-id header")

    check = await check_usage_limit_db(db, x_tenant_id, metric)

    if not check["allowed"]:
        raise HTTPException(
            429,
            detail={
                "error": "quota_exceeded",
                "metric": metric,
                "limit": check.get("limit"),
                "used": check.get("used"),
            },
        )

    return {
        "allowed": True,
        "tenant_id": x_tenant_id,
        "metric": metric,
        "remaining": check.get("remaining"),
    }


# =============================================================================
# API Endpoints - Invoices
# =============================================================================


@app.get("/api/v1/tenants/{tenant_id}/invoices")
async def list_invoices(
    tenant_id: str,
    status: InvoiceStatus | None = None,
    limit: int = Query(default=20, le=100),
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """قائمة الفواتير"""
    require_tenant_or_admin(current_user, tenant_id)

    repo = BillingRepository(db)

    # Check tenant exists
    tenant = await repo.tenants.get_by_tenant_id(tenant_id)
    if not tenant:
        raise HTTPException(404, "المستأجر غير موجود")

    # Get invoices from database
    db_status = db_models.InvoiceStatus(status.value) if status else None
    invoices = await repo.invoices.list_by_tenant(
        tenant_id=tenant_id,
        status=db_status,
        limit=limit,
    )

    return {
        "invoices": [
            {
                "invoice_id": str(inv.id),
                "invoice_number": inv.invoice_number,
                "tenant_id": inv.tenant_id,
                "status": inv.status.value,
                "currency": inv.currency.value,
                "total": float(inv.total),
                "amount_due": float(inv.amount_due),
                "issue_date": inv.issue_date.isoformat(),
                "due_date": inv.due_date.isoformat(),
                "paid_date": inv.paid_date.isoformat() if inv.paid_date else None,
            }
            for inv in invoices
        ],
        "total": len(invoices),
    }


@app.get("/api/v1/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """تفاصيل فاتورة"""
    try:
        invoice_uuid = uuid.UUID(invoice_id)
    except (ValueError, AttributeError):
        raise HTTPException(400, "معرف فاتورة غير صالح")

    repo = BillingRepository(db)
    invoice = await repo.invoices.get_by_id(invoice_uuid)

    if not invoice:
        raise HTTPException(404, "الفاتورة غير موجودة")

    # Verify tenant access for this invoice
    require_tenant_or_admin(current_user, invoice.tenant_id)

    # Get tenant
    tenant = await repo.tenants.get_by_tenant_id(invoice.tenant_id)

    return {
        "invoice": {
            "invoice_id": str(invoice.id),
            "invoice_number": invoice.invoice_number,
            "tenant_id": invoice.tenant_id,
            "subscription_id": str(invoice.subscription_id),
            "status": invoice.status.value,
            "currency": invoice.currency.value,
            "issue_date": invoice.issue_date.isoformat(),
            "due_date": invoice.due_date.isoformat(),
            "paid_date": invoice.paid_date.isoformat() if invoice.paid_date else None,
            "subtotal": float(invoice.subtotal),
            "tax_amount": float(invoice.tax_amount),
            "discount_amount": float(invoice.discount_amount),
            "total": float(invoice.total),
            "amount_paid": float(invoice.amount_paid),
            "amount_due": float(invoice.amount_due),
            "line_items": invoice.line_items,
            "notes": invoice.notes,
            "notes_ar": invoice.notes_ar,
        },
        "tenant": (
            {
                "tenant_id": tenant.tenant_id,
                "name": tenant.name,
                "name_ar": tenant.name_ar,
                "contact": tenant.contact,
            }
            if tenant
            else None
        ),
        "amount_yer": (
            float(convert_to_yer(invoice.total))
            if invoice.currency == db_models.Currency.USD
            else float(invoice.total)
        ),
    }


@app.post("/api/v1/tenants/{tenant_id}/invoices/generate")
async def generate_tenant_invoice(
    tenant_id: str,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """توليد فاتورة يدوياً"""
    require_tenant_or_admin(current_user, tenant_id)

    # Get subscription from database
    repo = BillingRepository(db)
    subscription = await repo.subscriptions.get_by_tenant(tenant_id)

    if not subscription:
        raise HTTPException(404, "لا يوجد اشتراك")

    # Generate invoice data - get plan from database
    plan = await repo.plans.get_by_plan_id(subscription.plan_id)
    if not plan:
        raise HTTPException(404, "الخطة غير موجودة")

    price = get_plan_price(plan.pricing, subscription.billing_cycle)

    line_items = [
        {
            "description": f"{plan.name} - {subscription.billing_cycle.value.title()}",
            "description_ar": f"{plan.name_ar} - {'شهري' if subscription.billing_cycle == BillingCycle.MONTHLY else 'ربع سنوي' if subscription.billing_cycle == BillingCycle.QUARTERLY else 'سنوي'}",
            "quantity": 1,
            "unit_price": float(price),
            "amount": float(price),
            "is_usage_based": False,
        }
    ]

    subtotal = price
    tax_amount = Decimal("0")
    total = subtotal + tax_amount

    # Create invoice in database using database sequence for invoice number
    invoice_number = await get_next_invoice_number()
    invoice = await repo.invoices.create(
        invoice_number=invoice_number,
        tenant_id=tenant_id,
        subscription_id=subscription.id,
        currency=db_models.Currency(subscription.currency.value),
        issue_date=date.today(),
        due_date=date.today() + timedelta(days=7),
        subtotal=subtotal,
        total=total,
        amount_due=total,
        line_items=line_items,
        status=db_models.InvoiceStatus.PENDING,
        notes_ar="شكراً لاختياركم منصة سهول الزراعية",
    )

    logger.info(f"Invoice generated: {invoice.invoice_number} for tenant {tenant_id}")

    return {
        "success": True,
        "invoice": {
            "invoice_id": str(invoice.id),
            "invoice_number": invoice.invoice_number,
            "tenant_id": invoice.tenant_id,
            "subscription_id": str(invoice.subscription_id),
            "status": invoice.status.value,
            "currency": invoice.currency.value,
            "total": float(invoice.total),
            "amount_due": float(invoice.amount_due),
            "issue_date": invoice.issue_date.isoformat(),
            "due_date": invoice.due_date.isoformat(),
        },
    }


# =============================================================================
# API Endpoints - Payments
# =============================================================================


async def call_tharwatt_api(payment: Any, phone_number: str) -> dict:
    """Call Tharwatt payment gateway API"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{THARWATT_BASE_URL}/api/v1/payment/deposit",
                headers={
                    "Authorization": f"Bearer {THARWATT_API_KEY}",
                    "X-Merchant-Id": THARWATT_MERCHANT_ID,
                    "Content-Type": "application/json",
                },
                json={
                    "reference": payment.payment_id,
                    "amount": float(payment.amount),
                    "currency": "YER",
                    "phone_number": phone_number,
                    "description": f"SAHOOL Invoice Payment - {payment.invoice_id}",
                    "callback_url": "https://api.sahool.com/api/v1/webhooks/tharwatt",
                },
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(
                "Tharwatt API error: %s", str(e).replace("\n", " ").replace("\r", " ")
            )
            # Security: Don't expose internal error details to client
            raise HTTPException(
                502, "Payment gateway temporarily unavailable. Please try again."
            )


async def call_stripe_api(payment: Any, token: str) -> dict:
    """Call Stripe payment API"""
    try:
        import stripe

        stripe.api_key = STRIPE_API_KEY

        charge = stripe.Charge.create(
            amount=int(payment.amount * 100),  # Stripe uses cents
            currency=payment.currency.value.lower(),
            source=token,
            description=f"SAHOOL Invoice Payment - {payment.invoice_id}",
            metadata={
                "payment_id": payment.payment_id,
                "invoice_id": payment.invoice_id,
                "tenant_id": payment.tenant_id,
            },
        )
        return {"stripe_charge_id": charge.id, "status": charge.status}
    except Exception as e:
        logger.error(
            "Stripe API error: %s", str(e).replace("\n", " ").replace("\r", " ")
        )
        # Security: Don't expose internal error details to client
        raise HTTPException(
            502, "Payment processing failed. Please try again or contact support."
        )


@app.post("/api/v1/payments")
async def create_payment(
    request: CreatePaymentRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """تسجيل دفعة"""
    # Parse invoice_id (could be UUID string)
    try:
        invoice_uuid = uuid.UUID(request.invoice_id)
    except (ValueError, AttributeError):
        raise HTTPException(400, "معرف فاتورة غير صالح")

    # Get invoice from database
    repo = BillingRepository(db)
    invoice = await repo.invoices.get_by_id(invoice_uuid)

    if not invoice:
        raise HTTPException(404, "الفاتورة غير موجودة")

    # Verify user can make payment for this tenant's invoice
    require_tenant_or_admin(current_user, invoice.tenant_id)

    if invoice.status == db_models.InvoiceStatus.PAID:
        raise HTTPException(400, "الفاتورة مدفوعة بالفعل")

    # Create payment in database
    payment = await repo.payments.create(
        invoice_id=invoice.id,
        tenant_id=invoice.tenant_id,
        amount=request.amount,
        currency=db_models.Currency(invoice.currency.value),
        method=db_models.PaymentMethod(request.method.value),
        status=db_models.PaymentStatus.PENDING,
    )

    tharwatt_response = None
    stripe_response = None

    # Process payment based on method
    if request.method == PaymentMethod.CREDIT_CARD and STRIPE_API_KEY:
        # Stripe Payment Processing
        token = getattr(request, "stripe_token", None)
        if token:
            # Create temporary payment object for API call
            temp_payment = type(
                "obj",
                (object,),
                {
                    "payment_id": str(payment.id),
                    "invoice_id": str(payment.invoice_id),
                    "tenant_id": payment.tenant_id,
                    "amount": payment.amount,
                    "currency": payment.currency,
                },
            )()
            stripe_response = await call_stripe_api(temp_payment, token)
            if stripe_response.get("status") == "succeeded":
                await repo.payments.mark_succeeded(
                    payment.id, external_id=stripe_response.get("stripe_charge_id")
                )
            else:
                await repo.payments.update(
                    payment.id, status=db_models.PaymentStatus.PROCESSING
                )

    elif request.method == PaymentMethod.THARWATT and THARWATT_API_KEY:
        # Tharwatt Payment Gateway - بوابة ثروات
        phone_number = getattr(request, "phone_number", "")
        if phone_number:
            temp_payment = type(
                "obj",
                (object,),
                {
                    "payment_id": str(payment.id),
                    "invoice_id": str(payment.invoice_id),
                    "amount": payment.amount,
                },
            )()
            tharwatt_response = await call_tharwatt_api(temp_payment, phone_number)
            await repo.payments.update(
                payment.id, status=db_models.PaymentStatus.PROCESSING
            )
            safe_resp = str(tharwatt_response).replace("\n", " ").replace("\r", " ")
            logger.info(
                f"Tharwatt payment initiated: {payment.id} - Response: {safe_resp}"
            )

    elif request.method == PaymentMethod.CASH:
        await repo.payments.mark_succeeded(payment.id)

    # Refresh payment to get updated status
    payment = await repo.payments.get_by_id(payment.id)

    # Update invoice if payment succeeded
    if payment.status == db_models.PaymentStatus.SUCCEEDED:
        await repo.invoices.mark_paid(invoice.id, request.amount)

    safe_inv_id = str(request.invoice_id).replace("\n", " ").replace("\r", " ")
    logger.info(f"Payment {payment.id} created for invoice {safe_inv_id}")

    # Publish payment event
    background_tasks.add_task(
        publish_event,
        "sahool.billing.payment.created",
        {
            "payment_id": str(payment.id),
            "invoice_id": str(payment.invoice_id),
            "tenant_id": payment.tenant_id,
            "amount": float(payment.amount),
            "currency": payment.currency.value,
            "method": payment.method.value,
            "status": payment.status.value,
        },
    )

    # Refresh invoice to get updated status
    invoice = await repo.invoices.get_by_id(invoice.id)

    return {
        "success": True,
        "payment": {
            "payment_id": str(payment.id),
            "invoice_id": str(payment.invoice_id),
            "tenant_id": payment.tenant_id,
            "amount": float(payment.amount),
            "currency": payment.currency.value,
            "method": payment.method.value,
            "status": payment.status.value,
            "created_at": payment.created_at.isoformat(),
        },
        "invoice_status": invoice.status.value,
        "tharwatt_response": tharwatt_response,
        "stripe_response": stripe_response,
    }


@app.get("/api/v1/tenants/{tenant_id}/payments")
async def list_payments(
    tenant_id: str,
    limit: int = Query(default=20, le=100),
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """قائمة المدفوعات"""
    require_tenant_or_admin(current_user, tenant_id)

    repo = BillingRepository(db)
    payments = await repo.payments.list_by_tenant(tenant_id=tenant_id, limit=limit)

    return {
        "payments": [
            {
                "payment_id": str(p.id),
                "invoice_id": str(p.invoice_id),
                "tenant_id": p.tenant_id,
                "amount": float(p.amount),
                "currency": p.currency.value,
                "status": p.status.value,
                "method": p.method.value,
                "created_at": p.created_at.isoformat(),
                "paid_at": p.paid_at.isoformat() if p.paid_at else None,
            }
            for p in payments
        ],
        "total": len(payments),
    }


# =============================================================================
# API Endpoints - Refunds
# =============================================================================


class RefundRequest(BaseModel):
    """طلب استرداد"""

    payment_id: str
    amount: Decimal | None = None  # None = full refund
    reason: str
    reason_ar: str | None = None


@app.post("/api/v1/refunds")
async def create_refund(
    request: RefundRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(require_roles(["super_admin", "tenant_admin"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Process a refund for a payment (admin only)
    معالجة استرداد لدفعة (للمسؤولين فقط)
    """
    try:
        payment_uuid = uuid.UUID(request.payment_id)
    except (ValueError, AttributeError):
        raise HTTPException(400, "معرف الدفعة غير صالح")

    repo = BillingRepository(db)
    payment = await repo.payments.get_by_id(payment_uuid)

    if not payment:
        raise HTTPException(404, "الدفعة غير موجودة")

    if payment.status != db_models.PaymentStatus.SUCCEEDED:
        raise HTTPException(400, "لا يمكن استرداد دفعة غير ناجحة")

    refund_amount = request.amount or payment.amount

    if refund_amount > payment.amount:
        raise HTTPException(400, "مبلغ الاسترداد أكبر من مبلغ الدفعة الأصلية")

    # Process refund via payment gateway
    refund_external_id = None

    if (
        payment.method == db_models.PaymentMethod.CREDIT_CARD
        and STRIPE_API_KEY
        and payment.stripe_payment_id
    ):
        # Stripe refund
        try:
            import stripe

            stripe.api_key = STRIPE_API_KEY
            refund = stripe.Refund.create(
                charge=payment.stripe_payment_id,
                amount=int(refund_amount * 100),  # cents
                reason="requested_by_customer",
                metadata={
                    "payment_id": str(payment.id),
                    "tenant_id": payment.tenant_id,
                    "reason": request.reason,
                },
            )
            refund_external_id = refund.id
        except Exception as e:
            logger.error(f"Stripe refund failed: {e}")
            raise HTTPException(502, "فشل في معالجة الاسترداد عبر بوابة الدفع")

    elif payment.method == db_models.PaymentMethod.THARWATT and THARWATT_API_KEY:
        # Tharwatt refund
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{THARWATT_BASE_URL}/api/v1/payment/refund",
                    headers={
                        "Authorization": f"Bearer {THARWATT_API_KEY}",
                        "X-Merchant-Id": THARWATT_MERCHANT_ID,
                        "Content-Type": "application/json",
                    },
                    json={
                        "reference": str(payment.id),
                        "amount": float(refund_amount),
                        "currency": "YER",
                        "reason": request.reason,
                    },
                )
                response.raise_for_status()
                refund_data = response.json()
                refund_external_id = refund_data.get("transaction_id")
        except httpx.HTTPError as e:
            logger.error(f"Tharwatt refund failed: {e}")
            raise HTTPException(502, "فشل في معالجة الاسترداد عبر بوابة ثروات")

    # Update payment status
    safe_reason = str(request.reason).replace("\n", " ").replace("\r", " ")
    is_full_refund = refund_amount >= payment.amount
    if is_full_refund:
        await repo.payments.update(
            payment.id,
            status=db_models.PaymentStatus.REFUNDED,
            failure_reason=f"Refunded: {safe_reason}",
        )
    else:
        # Partial refund - record in metadata
        await repo.payments.update(
            payment.id,
            failure_reason=f"Partial refund ({refund_amount}): {safe_reason}",
        )

    # Update invoice - reverse the payment
    invoice = await repo.invoices.get_by_id(payment.invoice_id)
    if invoice:
        new_amount_paid = max(Decimal("0"), invoice.amount_paid - refund_amount)
        new_amount_due = invoice.total - new_amount_paid
        update_kwargs = {
            "amount_paid": new_amount_paid,
            "amount_due": new_amount_due,
        }
        if is_full_refund:
            update_kwargs["status"] = db_models.InvoiceStatus.REFUNDED
        elif new_amount_due > 0:
            update_kwargs["status"] = db_models.InvoiceStatus.PENDING

        await repo.invoices.update(invoice.id, **update_kwargs)

    safe_refund_amount = str(refund_amount).replace("\n", " ").replace("\r", " ")
    logger.info(
        f"Refund processed: payment={payment.id}, amount={safe_refund_amount}, full={is_full_refund}, reason={safe_reason}"
    )

    # Publish refund event
    background_tasks.add_task(
        publish_event,
        "sahool.billing.payment.refunded",
        {
            "payment_id": str(payment.id),
            "invoice_id": str(payment.invoice_id),
            "tenant_id": payment.tenant_id,
            "refund_amount": float(refund_amount),
            "is_full_refund": is_full_refund,
            "reason": request.reason,
            "external_refund_id": refund_external_id,
        },
    )

    return {
        "success": True,
        "refund": {
            "payment_id": str(payment.id),
            "tenant_id": payment.tenant_id,
            "original_amount": float(payment.amount),
            "refund_amount": float(refund_amount),
            "is_full_refund": is_full_refund,
            "reason": request.reason,
            "reason_ar": request.reason_ar or request.reason,
            "external_refund_id": refund_external_id,
        },
        "message_ar": (
            "تم استرداد المبلغ بالكامل بنجاح"
            if is_full_refund
            else f"تم استرداد مبلغ {refund_amount} بنجاح"
        ),
    }


# =============================================================================
# Tharwatt Webhook - ويب هوك ثروات
# =============================================================================


class TharwattWebhookPayload(BaseModel):
    """Tharwatt webhook payload"""

    transaction_id: str
    status: str  # 'completed', 'failed', 'cancelled'
    amount: Decimal
    currency: str = "YER"
    phone_number: str | None = None
    reference: str | None = None  # Our payment_id
    timestamp: str | None = None
    error_message: str | None = None


def verify_tharwatt_signature(payload: bytes, signature: str) -> bool:
    """
    Verify Tharwatt webhook signature using HMAC-SHA256
    التحقق من توقيع ويب هوك ثروات
    """
    # SECURITY: Webhook secret is mandatory - reject if not configured
    if not THARWATT_WEBHOOK_SECRET:
        logger.error(
            "THARWATT_WEBHOOK_SECRET not configured - webhook signature verification failed. "
            "Set THARWATT_WEBHOOK_SECRET environment variable to enable webhook processing."
        )
        return False

    # Validate signature is present
    if not signature:
        logger.error(
            "Tharwatt webhook signature missing in X-Tharwatt-Signature header"
        )
        return False

    try:
        expected_signature = hmac.new(
            THARWATT_WEBHOOK_SECRET.encode("utf-8"), payload, hashlib.sha256
        ).hexdigest()

        # Use constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(signature.lower(), expected_signature.lower())

        if not is_valid:
            logger.error(
                f"Tharwatt webhook signature verification failed. "
                f"Received signature: {signature[:16]}... (truncated), "
                f"Expected signature: {expected_signature[:16]}... (truncated)"
            )

        return is_valid
    except Exception as e:
        logger.error(f"Tharwatt signature verification error: {e}", exc_info=True)
        return False


@app.post("/api/v1/webhooks/tharwatt")
async def tharwatt_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Tharwatt payment webhook callback
    ويب هوك لتأكيد المدفوعات من ثروات
    """
    # Security: Verify webhook signature
    raw_body = await request.body()
    signature = request.headers.get("X-Tharwatt-Signature", "")

    if not verify_tharwatt_signature(raw_body, signature):
        logger.warning("Tharwatt webhook: Invalid signature")
        raise HTTPException(401, "Invalid webhook signature")

    # Parse payload after verification
    try:
        import json

        payload_dict = json.loads(raw_body)
        payload = TharwattWebhookPayload(**payload_dict)
    except Exception as e:
        logger.error(f"Tharwatt webhook: Invalid payload: {e}")
        raise HTTPException(400, "Invalid payload format")

    # Find payment by reference (payment_id) in database
    repo = BillingRepository(db)
    payment = None
    if payload.reference:
        try:
            payment = await repo.payments.get_by_id(uuid.UUID(payload.reference))
        except (ValueError, AttributeError) as e:
            safe_ref = str(payload.reference).replace("\n", " ").replace("\r", " ")
            logger.warning(f"Failed to resolve payment reference {safe_ref}: {e}")

    if not payment:
        safe_ref = str(payload.reference).replace("\n", " ").replace("\r", " ")
        logger.warning(f"Tharwatt webhook: Payment not found for reference {safe_ref}")
        raise HTTPException(404, "Payment not found")

    # Update payment status in database
    if payload.status == "completed":
        await repo.payments.mark_succeeded(
            payment.id,
            external_id=payload.transaction_id,
        )

        # Update invoice
        await repo.invoices.mark_paid(payment.invoice_id, payment.amount)

        logger.info(f"Tharwatt payment completed: {payment.id}")

        # Publish payment success event
        background_tasks.add_task(
            publish_event,
            "sahool.billing.payment.succeeded",
            {
                "payment_id": str(payment.id),
                "invoice_id": str(payment.invoice_id),
                "tenant_id": payment.tenant_id,
                "amount": float(payment.amount),
                "method": "tharwatt",
                "transaction_id": payload.transaction_id,
            },
        )

    elif payload.status == "failed":
        await repo.payments.mark_failed(
            payment.id,
            failure_reason=payload.error_message or "Payment failed",
        )
        safe_err = str(payload.error_message).replace("\n", " ").replace("\r", " ")
        logger.warning(f"Tharwatt payment failed: {payment.id} - {safe_err}")

        # Publish payment failed event
        background_tasks.add_task(
            publish_event,
            "sahool.billing.payment.failed",
            {
                "payment_id": str(payment.id),
                "invoice_id": str(payment.invoice_id),
                "error": payload.error_message,
            },
        )

    elif payload.status == "cancelled":
        await repo.payments.mark_failed(
            payment.id,
            failure_reason="Payment cancelled by user",
        )
        logger.info(f"Tharwatt payment cancelled: {payment.id}")

    # Refresh payment to get updated status
    payment = await repo.payments.get_by_id(payment.id)

    return {
        "success": True,
        "payment_id": str(payment.id),
        "status": payment.status.value,
    }


# =============================================================================
# Stripe Webhook - ويب هوك سترايب
# =============================================================================


class StripeWebhookPayload(BaseModel):
    """Stripe webhook event payload"""

    id: str
    type: str
    data: dict[str, Any]


def verify_stripe_signature(payload: bytes, signature: str) -> bool:
    """Verify Stripe webhook signature"""
    # SECURITY: Webhook secret is mandatory - reject if not configured
    if not STRIPE_WEBHOOK_SECRET:
        logger.error(
            "STRIPE_WEBHOOK_SECRET not configured - webhook signature verification failed. "
            "Set STRIPE_WEBHOOK_SECRET environment variable to enable webhook processing."
        )
        return False

    # Validate signature is present
    if not signature:
        logger.error("Stripe webhook signature missing in stripe-signature header")
        return False

    try:
        import stripe

        stripe.Webhook.construct_event(payload, signature, STRIPE_WEBHOOK_SECRET)
        return True
    except stripe.error.SignatureVerificationError as e:
        logger.error(
            f"Stripe webhook signature verification failed: {e}. "
            f"This may indicate an invalid webhook secret or a spoofed request."
        )
        return False
    except Exception as e:
        logger.error(f"Stripe signature verification error: {e}", exc_info=True)
        return False


@app.post("/api/v1/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Stripe payment webhook callback
    ويب هوك لتأكيد المدفوعات من سترايب
    """
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")

    if not verify_stripe_signature(payload, signature):
        raise HTTPException(400, "Invalid signature")

    try:
        import json

        event = json.loads(payload)
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid payload")

    event_type = event.get("type", "")
    data = event.get("data", {}).get("object", {})
    repo = BillingRepository(db)

    # Handle different event types
    if event_type == "charge.succeeded":
        payment_id = data.get("metadata", {}).get("payment_id")
        if payment_id:
            try:
                payment = await repo.payments.get_by_id(uuid.UUID(payment_id))
            except (ValueError, AttributeError):
                payment = None

            if payment:
                await repo.payments.mark_succeeded(
                    payment.id,
                    external_id=data.get("id"),
                )

                # Update invoice
                await repo.invoices.mark_paid(payment.invoice_id, payment.amount)

                logger.info(f"Stripe payment succeeded: {payment_id}")

                # Publish payment success event
                background_tasks.add_task(
                    publish_event,
                    "sahool.billing.payment.succeeded",
                    {
                        "payment_id": payment_id,
                        "invoice_id": str(payment.invoice_id),
                        "tenant_id": payment.tenant_id,
                        "amount": float(payment.amount),
                        "method": "stripe",
                        "stripe_charge_id": data.get("id"),
                    },
                )

    elif event_type == "charge.failed":
        payment_id = data.get("metadata", {}).get("payment_id")
        if payment_id:
            try:
                payment = await repo.payments.get_by_id(uuid.UUID(payment_id))
            except (ValueError, AttributeError):
                payment = None

            if payment:
                failure_reason = data.get("failure_message", "Payment failed")
                await repo.payments.mark_failed(
                    payment.id, failure_reason=failure_reason
                )
                logger.warning(f"Stripe payment failed: {payment_id}")

                # Publish payment failed event
                background_tasks.add_task(
                    publish_event,
                    "sahool.billing.payment.failed",
                    {
                        "payment_id": payment_id,
                        "error": failure_reason,
                    },
                )

    elif event_type == "customer.subscription.updated":
        # Handle subscription updates from Stripe
        subscription_id = data.get("metadata", {}).get("subscription_id")
        if subscription_id:
            try:
                subscription = await repo.subscriptions.get_by_id(
                    uuid.UUID(subscription_id)
                )
            except (ValueError, AttributeError):
                subscription = None

            if subscription:
                stripe_status = data.get("status")
                status_map = {
                    "active": db_models.SubscriptionStatus.ACTIVE,
                    "past_due": db_models.SubscriptionStatus.PAST_DUE,
                    "canceled": db_models.SubscriptionStatus.CANCELED,
                }
                new_status = status_map.get(stripe_status)
                if new_status:
                    await repo.subscriptions.update(subscription.id, status=new_status)

                logger.info(
                    f"Stripe subscription updated: {subscription_id} -> {stripe_status}"
                )

                # Publish subscription event
                background_tasks.add_task(
                    publish_event,
                    "sahool.billing.subscription.updated",
                    {
                        "subscription_id": subscription_id,
                        "tenant_id": subscription.tenant_id,
                        "status": new_status.value if new_status else stripe_status,
                    },
                )

    return {"received": True}


# =============================================================================
# API Endpoints - Reports & Analytics
# =============================================================================


@app.get("/api/v1/reports/revenue")
async def get_revenue_report(
    start_date: date | None = None,
    end_date: date | None = None,
    current_user=Depends(require_roles(["super_admin", "tenant_admin"])),
    db: AsyncSession = Depends(get_db),
):
    """تقرير الإيرادات (للمسؤولين)"""
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()

    repo = BillingRepository(db)

    # Calculate revenue from database
    total_usd = await repo.invoices.get_total_revenue(
        start_date=start_date, end_date=end_date, currency=db_models.Currency.USD
    )
    total_yer = await repo.invoices.get_total_revenue(
        start_date=start_date, end_date=end_date, currency=db_models.Currency.YER
    )

    # Revenue by payment method
    by_method = await repo.payments.get_total_by_method(
        start_date=datetime.combine(start_date, datetime.min.time()).replace(
            tzinfo=UTC
        ),
        end_date=datetime.combine(end_date, datetime.max.time()).replace(tzinfo=UTC),
    )

    # Count paid invoices in period
    paid_invoices = await repo.invoices.list_by_tenant(
        tenant_id=None, status=db_models.InvoiceStatus.PAID, limit=10000
    )
    invoices_in_period = [
        inv
        for inv in paid_invoices
        if inv.paid_date and start_date <= inv.paid_date <= end_date
    ]

    # Revenue by plan
    by_plan: dict[str, Decimal] = {}
    for inv in invoices_in_period:
        sub = await repo.subscriptions.get_by_id(inv.subscription_id)
        if sub:
            by_plan[sub.plan_id] = by_plan.get(sub.plan_id, Decimal("0")) + inv.total

    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        },
        "total_revenue": {
            "usd": float(total_usd),
            "yer": float(total_yer + convert_to_yer(total_usd)),
        },
        "invoices_count": len(invoices_in_period),
        "by_plan": {k: float(v) for k, v in by_plan.items()},
        "by_payment_method": {k: float(v) for k, v in by_method.items()},
    }


@app.get("/api/v1/reports/subscriptions")
async def get_subscriptions_report(
    current_user=Depends(require_roles(["super_admin", "tenant_admin"])),
    db: AsyncSession = Depends(get_db),
):
    """تقرير الاشتراكات (للمسؤولين)"""
    repo = BillingRepository(db)

    # Get counts from database
    by_status = await repo.subscriptions.count_by_status()
    by_plan = await repo.subscriptions.count_by_plan()
    total_tenants = await repo.tenants.count_total(active_only=False)

    total_subscriptions = sum(by_status.values())

    # Calculate MRR (Monthly Recurring Revenue) from database
    mrr = Decimal("0")
    active_subs = await repo.subscriptions.get_due_for_billing(
        billing_date=date.today() + timedelta(days=365),  # Get all active
    )
    for sub in active_subs:
        if sub.status == db_models.SubscriptionStatus.ACTIVE:
            plan = await repo.plans.get_by_plan_id(sub.plan_id)
            if plan:
                monthly_price = Decimal(str(plan.pricing.get("monthly_usd", "0")))
                mrr += monthly_price

    return {
        "total_subscriptions": total_subscriptions,
        "by_status": by_status,
        "by_plan": by_plan,
        "mrr_usd": float(mrr),
        "mrr_yer": float(convert_to_yer(mrr)),
        "total_tenants": total_tenants,
    }


# ---------------------------------------------------------------------------
# Backward-compatible route aliases (deprecated, remove in v17.0.0)
# Clients/tests using the old /v1/... paths will continue to work.
# New integrations should use /api/v1/... paths.
# ---------------------------------------------------------------------------
_v1_prefix = "/api/v1"
for _route in list(app.routes):
    _path = getattr(_route, "path", "")
    if _path.startswith(_v1_prefix):
        _old_path = "/v1" + _path[len(_v1_prefix) :]
        app.router.add_api_route(
            _old_path,
            _route.endpoint,
            methods=list(_route.methods) if _route.methods else ["GET"],
            tags=["deprecated"],
            include_in_schema=False,
            deprecated=True,
        )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8089))
    uvicorn.run(app, host="0.0.0.0", port=port)
