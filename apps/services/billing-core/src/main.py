"""
💰 SAHOOL Billing Core Service v15.6
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

import os
import uuid
import hmac
import hashlib
import logging
import asyncio
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum
from contextlib import asynccontextmanager

import httpx
import nats
from nats.js.api import StreamConfig, RetentionPolicy
from fastapi import FastAPI, HTTPException, Query, Header, Depends, BackgroundTasks, Request
from pydantic import BaseModel, Field, EmailStr

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sahool-billing")

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
                subjects=["sahool.billing.*", "sahool.payment.*", "sahool.subscription.*"],
                retention=RetentionPolicy.LIMITS,
                max_age=86400 * 30  # 30 days
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
        logger.info(f"Event (local): {subject} - {data}")

# =============================================================================
# App Configuration
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifespan events"""
    await init_nats()
    yield
    if nats_client:
        await nats_client.close()


app = FastAPI(
    title="SAHOOL Billing Core | خدمة الفوترة",
    version="15.6.0",
    description="Complete billing, subscription, and payment management for SAHOOL platform",
    lifespan=lifespan,
)

# Environment configuration
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "USD")
YER_EXCHANGE_RATE = float(os.getenv("YER_EXCHANGE_RATE", "250"))  # 1 USD = 250 YER

# Tharwatt Payment Gateway Configuration - بوابة ثروات
THARWATT_BASE_URL = os.getenv("THARWATT_BASE_URL", "https://developers-test.tharwatt.com:5253")
THARWATT_API_KEY = os.getenv("THARWATT_API_KEY", "")
THARWATT_MERCHANT_ID = os.getenv("THARWATT_MERCHANT_ID", "")
THARWATT_WEBHOOK_SECRET = os.getenv("THARWATT_WEBHOOK_SECRET", "")


# =============================================================================
# Enums
# =============================================================================


class PlanTier(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    MOBILE_MONEY = "mobile_money"
    CASH = "cash"
    THARWATT = "tharwatt"  # بوابة ثروات اليمنية


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


class Currency(str, Enum):
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
    limit: Optional[int] = None  # None = unlimited


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
    features: Dict[str, PlanFeature]
    limits: Dict[str, int]  # Feature limits
    is_active: bool = True
    trial_days: int = 14
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TenantContact(BaseModel):
    """معلومات الاتصال"""
    name: str
    name_ar: str
    email: EmailStr
    phone: str
    address: Optional[str] = None
    city: Optional[str] = None
    governorate: Optional[str] = None


class Tenant(BaseModel):
    """المستأجر/العميل"""
    tenant_id: str
    name: str
    name_ar: str
    contact: TenantContact
    tax_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    metadata: Dict[str, Any] = {}


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
    trial_end_date: Optional[date] = None
    canceled_at: Optional[datetime] = None

    # Billing
    next_billing_date: date
    last_billing_date: Optional[date] = None

    # Payment
    payment_method: Optional[PaymentMethod] = None
    stripe_subscription_id: Optional[str] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


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
    paid_date: Optional[date] = None

    # Amounts
    subtotal: Decimal
    tax_rate: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    total: Decimal
    amount_paid: Decimal = Decimal("0")
    amount_due: Decimal

    # Line items
    line_items: List[InvoiceLineItem]

    # Notes
    notes: Optional[str] = None
    notes_ar: Optional[str] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    stripe_invoice_id: Optional[str] = None


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
    processed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None

    # External references
    stripe_payment_id: Optional[str] = None
    receipt_url: Optional[str] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UsageRecord(BaseModel):
    """سجل الاستخدام"""
    record_id: str
    tenant_id: str
    metric: str
    quantity: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}


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
    features: Dict[str, bool]
    limits: Dict[str, int]
    trial_days: int = 14


class CreateTenantRequest(BaseModel):
    name: str
    name_ar: str
    email: EmailStr
    phone: str
    plan_id: str
    billing_cycle: BillingCycle = BillingCycle.MONTHLY


class UpdateSubscriptionRequest(BaseModel):
    plan_id: Optional[str] = None
    billing_cycle: Optional[BillingCycle] = None
    payment_method: Optional[PaymentMethod] = None


class RecordUsageRequest(BaseModel):
    metric: str
    quantity: int = 1
    metadata: Dict[str, Any] = {}


class CreatePaymentRequest(BaseModel):
    invoice_id: str
    amount: Decimal
    method: PaymentMethod
    stripe_token: Optional[str] = None


# =============================================================================
# In-Memory Storage (Replace with PostgreSQL in production)
# =============================================================================

PLANS: Dict[str, Plan] = {}
TENANTS: Dict[str, Tenant] = {}
SUBSCRIPTIONS: Dict[str, Subscription] = {}
INVOICES: Dict[str, Invoice] = {}
PAYMENTS: Dict[str, Payment] = {}
USAGE_RECORDS: List[UsageRecord] = []
INVOICE_COUNTER: int = 0


# =============================================================================
# Initialize Default Plans
# =============================================================================

def init_default_plans():
    """تهيئة الخطط الافتراضية"""
    global PLANS

    PLANS = {
        "free": Plan(
            plan_id="free",
            name="Free",
            name_ar="مجاني",
            description="Perfect for small farmers getting started",
            description_ar="مثالي للمزارعين الصغار للبدء",
            tier=PlanTier.FREE,
            pricing=PlanPricing(
                monthly_usd=Decimal("0"),
                quarterly_usd=Decimal("0"),
                yearly_usd=Decimal("0"),
            ),
            features={
                "fields": PlanFeature(name="Fields", name_ar="الحقول", included=True, limit=3),
                "satellite": PlanFeature(name="Satellite Analysis", name_ar="تحليل الأقمار", included=True, limit=10),
                "weather": PlanFeature(name="Weather Forecasts", name_ar="توقعات الطقس", included=True, limit=None),
                "irrigation": PlanFeature(name="Irrigation Planning", name_ar="تخطيط الري", included=False),
                "ai_diagnosis": PlanFeature(name="AI Crop Diagnosis", name_ar="تشخيص المحاصيل", included=False),
                "reports": PlanFeature(name="PDF Reports", name_ar="تقارير PDF", included=False),
                "support": PlanFeature(name="Email Support", name_ar="دعم البريد", included=True),
            },
            limits={
                "fields": 3,
                "satellite_analyses_per_month": 10,
                "storage_gb": 1,
                "api_calls_per_day": 100,
            },
            trial_days=0,
        ),
        "starter": Plan(
            plan_id="starter",
            name="Starter",
            name_ar="المبتدئ",
            description="For growing farms with moderate needs",
            description_ar="للمزارع المتنامية ذات الاحتياجات المتوسطة",
            tier=PlanTier.STARTER,
            pricing=PlanPricing(
                monthly_usd=Decimal("29"),
                quarterly_usd=Decimal("79"),
                yearly_usd=Decimal("290"),
            ),
            features={
                "fields": PlanFeature(name="Fields", name_ar="الحقول", included=True, limit=10),
                "satellite": PlanFeature(name="Satellite Analysis", name_ar="تحليل الأقمار", included=True, limit=50),
                "weather": PlanFeature(name="Weather Forecasts", name_ar="توقعات الطقس", included=True, limit=None),
                "irrigation": PlanFeature(name="Irrigation Planning", name_ar="تخطيط الري", included=True, limit=None),
                "ai_diagnosis": PlanFeature(name="AI Crop Diagnosis", name_ar="تشخيص المحاصيل", included=True, limit=20),
                "reports": PlanFeature(name="PDF Reports", name_ar="تقارير PDF", included=True, limit=10),
                "support": PlanFeature(name="Email Support", name_ar="دعم البريد", included=True),
            },
            limits={
                "fields": 10,
                "satellite_analyses_per_month": 50,
                "ai_diagnoses_per_month": 20,
                "pdf_reports_per_month": 10,
                "storage_gb": 5,
                "api_calls_per_day": 500,
            },
            trial_days=14,
        ),
        "professional": Plan(
            plan_id="professional",
            name="Professional",
            name_ar="الاحترافي",
            description="For professional farmers and agricultural businesses",
            description_ar="للمزارعين المحترفين والأعمال الزراعية",
            tier=PlanTier.PROFESSIONAL,
            pricing=PlanPricing(
                monthly_usd=Decimal("99"),
                quarterly_usd=Decimal("269"),
                yearly_usd=Decimal("990"),
            ),
            features={
                "fields": PlanFeature(name="Fields", name_ar="الحقول", included=True, limit=50),
                "satellite": PlanFeature(name="Satellite Analysis", name_ar="تحليل الأقمار", included=True, limit=200),
                "weather": PlanFeature(name="Weather Forecasts", name_ar="توقعات الطقس", included=True, limit=None),
                "irrigation": PlanFeature(name="Irrigation Planning", name_ar="تخطيط الري", included=True, limit=None),
                "ai_diagnosis": PlanFeature(name="AI Crop Diagnosis", name_ar="تشخيص المحاصيل", included=True, limit=100),
                "reports": PlanFeature(name="PDF Reports", name_ar="تقارير PDF", included=True, limit=None),
                "support": PlanFeature(name="Priority Support", name_ar="دعم أولوية", included=True),
                "api_access": PlanFeature(name="API Access", name_ar="الوصول للـAPI", included=True),
            },
            limits={
                "fields": 50,
                "satellite_analyses_per_month": 200,
                "ai_diagnoses_per_month": 100,
                "pdf_reports_per_month": -1,  # Unlimited
                "storage_gb": 25,
                "api_calls_per_day": 2000,
                "team_members": 5,
            },
            trial_days=14,
        ),
        "enterprise": Plan(
            plan_id="enterprise",
            name="Enterprise",
            name_ar="المؤسسات",
            description="Custom solutions for large agricultural operations",
            description_ar="حلول مخصصة للعمليات الزراعية الكبيرة",
            tier=PlanTier.ENTERPRISE,
            pricing=PlanPricing(
                monthly_usd=Decimal("499"),
                quarterly_usd=Decimal("1349"),
                yearly_usd=Decimal("4990"),
            ),
            features={
                "fields": PlanFeature(name="Fields", name_ar="الحقول", included=True, limit=None),
                "satellite": PlanFeature(name="Satellite Analysis", name_ar="تحليل الأقمار", included=True, limit=None),
                "weather": PlanFeature(name="Weather Forecasts", name_ar="توقعات الطقس", included=True, limit=None),
                "irrigation": PlanFeature(name="Irrigation Planning", name_ar="تخطيط الري", included=True, limit=None),
                "ai_diagnosis": PlanFeature(name="AI Crop Diagnosis", name_ar="تشخيص المحاصيل", included=True, limit=None),
                "reports": PlanFeature(name="PDF Reports", name_ar="تقارير PDF", included=True, limit=None),
                "support": PlanFeature(name="Dedicated Support", name_ar="دعم مخصص", included=True),
                "api_access": PlanFeature(name="API Access", name_ar="الوصول للـAPI", included=True),
                "sla": PlanFeature(name="SLA Guarantee", name_ar="ضمان SLA", included=True),
                "custom_integrations": PlanFeature(name="Custom Integrations", name_ar="تكاملات مخصصة", included=True),
            },
            limits={
                "fields": -1,  # Unlimited
                "satellite_analyses_per_month": -1,
                "ai_diagnoses_per_month": -1,
                "pdf_reports_per_month": -1,
                "storage_gb": 100,
                "api_calls_per_day": 10000,
                "team_members": -1,
            },
            trial_days=30,
        ),
    }


# Initialize on startup
init_default_plans()


# =============================================================================
# Helper Functions
# =============================================================================


def generate_invoice_number() -> str:
    """توليد رقم الفاتورة"""
    global INVOICE_COUNTER
    INVOICE_COUNTER += 1
    year = datetime.utcnow().year
    return f"SAH-{year}-{INVOICE_COUNTER:04d}"


def convert_to_yer(amount_usd: Decimal) -> Decimal:
    """تحويل المبلغ من الدولار للريال اليمني"""
    return amount_usd * Decimal(str(YER_EXCHANGE_RATE))


def get_plan_price(plan: Plan, cycle: BillingCycle) -> Decimal:
    """الحصول على سعر الخطة حسب دورة الفوترة"""
    if cycle == BillingCycle.MONTHLY:
        return plan.pricing.monthly_usd
    elif cycle == BillingCycle.QUARTERLY:
        return plan.pricing.quarterly_usd
    else:
        return plan.pricing.yearly_usd


def get_billing_period_end(start_date: date, cycle: BillingCycle) -> date:
    """حساب تاريخ انتهاء فترة الفوترة"""
    if cycle == BillingCycle.MONTHLY:
        return start_date + timedelta(days=30)
    elif cycle == BillingCycle.QUARTERLY:
        return start_date + timedelta(days=90)
    else:
        return start_date + timedelta(days=365)


def check_usage_limit(tenant_id: str, metric: str) -> Dict[str, Any]:
    """التحقق من حدود الاستخدام"""
    tenant = TENANTS.get(tenant_id)
    if not tenant:
        return {"allowed": False, "reason": "Tenant not found"}

    # Get active subscription
    subscription = None
    for sub in SUBSCRIPTIONS.values():
        if sub.tenant_id == tenant_id and sub.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]:
            subscription = sub
            break

    if not subscription:
        return {"allowed": False, "reason": "No active subscription"}

    plan = PLANS.get(subscription.plan_id)
    if not plan:
        return {"allowed": False, "reason": "Plan not found"}

    # Check limit
    limit = plan.limits.get(metric, 0)
    if limit == -1:  # Unlimited
        return {"allowed": True, "limit": None, "used": 0}

    # Calculate current usage
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    used = sum(
        r.quantity for r in USAGE_RECORDS
        if r.tenant_id == tenant_id and r.metric == metric and r.timestamp >= current_month_start
    )

    return {
        "allowed": used < limit,
        "limit": limit,
        "used": used,
        "remaining": max(0, limit - used),
    }


def generate_invoice(subscription: Subscription) -> Invoice:
    """توليد فاتورة للاشتراك"""
    plan = PLANS[subscription.plan_id]
    price = get_plan_price(plan, subscription.billing_cycle)

    line_items = [
        InvoiceLineItem(
            description=f"{plan.name} - {subscription.billing_cycle.value.title()}",
            description_ar=f"{plan.name_ar} - {'شهري' if subscription.billing_cycle == BillingCycle.MONTHLY else 'ربع سنوي' if subscription.billing_cycle == BillingCycle.QUARTERLY else 'سنوي'}",
            quantity=1,
            unit_price=price,
            amount=price,
        )
    ]

    # Add usage-based charges
    # TODO: Calculate overage charges

    subtotal = sum(item.amount for item in line_items)
    tax_amount = Decimal("0")  # Yemen generally has no VAT on agricultural services
    total = subtotal + tax_amount

    invoice = Invoice(
        invoice_id=str(uuid.uuid4()),
        invoice_number=generate_invoice_number(),
        tenant_id=subscription.tenant_id,
        subscription_id=subscription.subscription_id,
        status=InvoiceStatus.PENDING,
        currency=subscription.currency,
        issue_date=date.today(),
        due_date=date.today() + timedelta(days=7),
        subtotal=subtotal,
        tax_amount=tax_amount,
        total=total,
        amount_due=total,
        line_items=line_items,
        notes_ar="شكراً لاختياركم منصة سهول الزراعية",
    )

    return invoice


# =============================================================================
# API Endpoints - Plans
# =============================================================================


@app.get("/healthz")
def health_check():
    return {
        "status": "ok",
        "service": "billing-core",
        "version": "15.5.0",
        "plans_count": len(PLANS),
        "tenants_count": len(TENANTS),
        "active_subscriptions": sum(1 for s in SUBSCRIPTIONS.values() if s.status == SubscriptionStatus.ACTIVE),
    }


@app.get("/v1/plans")
def list_plans(active_only: bool = True):
    """قائمة الخطط المتاحة"""
    plans = list(PLANS.values())
    if active_only:
        plans = [p for p in plans if p.is_active]

    return {
        "plans": [
            {
                "plan_id": p.plan_id,
                "name": p.name,
                "name_ar": p.name_ar,
                "tier": p.tier.value,
                "pricing": {
                    "monthly_usd": float(p.pricing.monthly_usd),
                    "monthly_yer": float(convert_to_yer(p.pricing.monthly_usd)),
                    "yearly_usd": float(p.pricing.yearly_usd),
                    "yearly_yer": float(convert_to_yer(p.pricing.yearly_usd)),
                },
                "limits": p.limits,
                "trial_days": p.trial_days,
            }
            for p in plans
        ]
    }


@app.get("/v1/plans/{plan_id}")
def get_plan(plan_id: str):
    """تفاصيل خطة محددة"""
    plan = PLANS.get(plan_id)
    if not plan:
        raise HTTPException(404, "الخطة غير موجودة")

    return {
        "plan": plan.dict(),
        "pricing_yer": {
            "monthly": float(convert_to_yer(plan.pricing.monthly_usd)),
            "quarterly": float(convert_to_yer(plan.pricing.quarterly_usd)),
            "yearly": float(convert_to_yer(plan.pricing.yearly_usd)),
        }
    }


@app.post("/v1/plans")
def create_plan(request: CreatePlanRequest):
    """إنشاء خطة جديدة (للمسؤولين)"""
    plan_id = request.name.lower().replace(" ", "_")

    if plan_id in PLANS:
        raise HTTPException(400, "الخطة موجودة بالفعل")

    features = {}
    for feature_name, included in request.features.items():
        limit = request.limits.get(feature_name)
        features[feature_name] = PlanFeature(
            name=feature_name.replace("_", " ").title(),
            name_ar=feature_name,  # TODO: Add proper Arabic translations
            included=included,
            limit=limit,
        )

    plan = Plan(
        plan_id=plan_id,
        name=request.name,
        name_ar=request.name_ar,
        description=request.description,
        description_ar=request.description_ar,
        tier=request.tier,
        pricing=PlanPricing(
            monthly_usd=request.monthly_price_usd,
            quarterly_usd=request.monthly_price_usd * Decimal("2.7"),
            yearly_usd=request.monthly_price_usd * Decimal("10"),
        ),
        features=features,
        limits=request.limits,
        trial_days=request.trial_days,
    )

    PLANS[plan_id] = plan
    logger.info(f"Plan created: {plan_id}")

    return {"success": True, "plan": plan.dict()}


# =============================================================================
# API Endpoints - Tenants & Subscriptions
# =============================================================================


@app.post("/v1/tenants")
def create_tenant(request: CreateTenantRequest):
    """تسجيل مستأجر جديد مع اشتراك"""
    tenant_id = str(uuid.uuid4())

    # Validate plan
    plan = PLANS.get(request.plan_id)
    if not plan:
        raise HTTPException(400, "الخطة غير موجودة")

    # Create tenant
    tenant = Tenant(
        tenant_id=tenant_id,
        name=request.name,
        name_ar=request.name_ar,
        contact=TenantContact(
            name=request.name,
            name_ar=request.name_ar,
            email=request.email,
            phone=request.phone,
        ),
    )
    TENANTS[tenant_id] = tenant

    # Create subscription
    today = date.today()
    trial_end = today + timedelta(days=plan.trial_days) if plan.trial_days > 0 else None

    subscription = Subscription(
        subscription_id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        plan_id=request.plan_id,
        status=SubscriptionStatus.TRIAL if trial_end else SubscriptionStatus.ACTIVE,
        billing_cycle=request.billing_cycle,
        start_date=today,
        end_date=get_billing_period_end(today, request.billing_cycle),
        trial_end_date=trial_end,
        next_billing_date=trial_end or get_billing_period_end(today, request.billing_cycle),
    )
    SUBSCRIPTIONS[subscription.subscription_id] = subscription

    logger.info(f"Tenant created: {tenant_id} with subscription {subscription.subscription_id}")

    return {
        "success": True,
        "tenant_id": tenant_id,
        "subscription_id": subscription.subscription_id,
        "status": subscription.status.value,
        "trial_ends": trial_end.isoformat() if trial_end else None,
        "message_ar": f"مرحباً {request.name_ar}! تم إنشاء حسابك بنجاح.",
    }


@app.get("/v1/tenants/{tenant_id}")
def get_tenant(tenant_id: str):
    """معلومات المستأجر"""
    tenant = TENANTS.get(tenant_id)
    if not tenant:
        raise HTTPException(404, "المستأجر غير موجود")

    # Get subscription
    subscription = None
    for sub in SUBSCRIPTIONS.values():
        if sub.tenant_id == tenant_id:
            subscription = sub
            break

    # Get usage summary
    usage = {}
    if subscription:
        plan = PLANS.get(subscription.plan_id)
        if plan:
            for metric in plan.limits.keys():
                usage[metric] = check_usage_limit(tenant_id, metric)

    return {
        "tenant": tenant.dict(),
        "subscription": subscription.dict() if subscription else None,
        "usage": usage,
    }


@app.get("/v1/tenants/{tenant_id}/subscription")
def get_subscription(tenant_id: str):
    """تفاصيل الاشتراك"""
    subscription = None
    for sub in SUBSCRIPTIONS.values():
        if sub.tenant_id == tenant_id:
            subscription = sub
            break

    if not subscription:
        raise HTTPException(404, "لا يوجد اشتراك")

    plan = PLANS.get(subscription.plan_id)

    return {
        "subscription": subscription.dict(),
        "plan": plan.dict() if plan else None,
        "days_remaining": (subscription.end_date - date.today()).days,
        "is_trial": subscription.status == SubscriptionStatus.TRIAL,
    }


@app.patch("/v1/tenants/{tenant_id}/subscription")
def update_subscription(tenant_id: str, request: UpdateSubscriptionRequest):
    """تحديث الاشتراك (ترقية/تخفيض)"""
    subscription = None
    for sub in SUBSCRIPTIONS.values():
        if sub.tenant_id == tenant_id:
            subscription = sub
            break

    if not subscription:
        raise HTTPException(404, "لا يوجد اشتراك")

    changes = []

    if request.plan_id and request.plan_id != subscription.plan_id:
        new_plan = PLANS.get(request.plan_id)
        if not new_plan:
            raise HTTPException(400, "الخطة غير موجودة")
        subscription.plan_id = request.plan_id
        changes.append(f"Plan changed to {new_plan.name}")

    if request.billing_cycle and request.billing_cycle != subscription.billing_cycle:
        subscription.billing_cycle = request.billing_cycle
        subscription.end_date = get_billing_period_end(subscription.start_date, request.billing_cycle)
        changes.append(f"Billing cycle changed to {request.billing_cycle.value}")

    if request.payment_method:
        subscription.payment_method = request.payment_method
        changes.append(f"Payment method set to {request.payment_method.value}")

    subscription.updated_at = datetime.utcnow()

    return {
        "success": True,
        "subscription": subscription.dict(),
        "changes": changes,
    }


@app.post("/v1/tenants/{tenant_id}/cancel")
def cancel_subscription(tenant_id: str, immediate: bool = False):
    """إلغاء الاشتراك"""
    subscription = None
    for sub in SUBSCRIPTIONS.values():
        if sub.tenant_id == tenant_id:
            subscription = sub
            break

    if not subscription:
        raise HTTPException(404, "لا يوجد اشتراك")

    subscription.canceled_at = datetime.utcnow()

    if immediate:
        subscription.status = SubscriptionStatus.CANCELED
        subscription.end_date = date.today()
    else:
        # Will be canceled at end of billing period
        subscription.status = SubscriptionStatus.ACTIVE  # Keep active until end

    logger.info(f"Subscription canceled for tenant {tenant_id}, immediate={immediate}")

    return {
        "success": True,
        "status": subscription.status.value,
        "end_date": subscription.end_date.isoformat(),
        "message_ar": "تم إلغاء اشتراكك. سيظل حسابك نشطاً حتى نهاية الفترة المدفوعة." if not immediate else "تم إلغاء اشتراكك فوراً.",
    }


# =============================================================================
# API Endpoints - Usage & Quotas
# =============================================================================


@app.post("/v1/tenants/{tenant_id}/usage")
def record_usage(tenant_id: str, request: RecordUsageRequest):
    """تسجيل استخدام"""
    if tenant_id not in TENANTS:
        raise HTTPException(404, "المستأجر غير موجود")

    # Check limit before recording
    limit_check = check_usage_limit(tenant_id, request.metric)
    if not limit_check["allowed"]:
        raise HTTPException(
            429,
            f"تم تجاوز الحد الأقصى للاستخدام: {request.metric}. الحد: {limit_check.get('limit', 'N/A')}, المستخدم: {limit_check.get('used', 'N/A')}"
        )

    record = UsageRecord(
        record_id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        metric=request.metric,
        quantity=request.quantity,
        metadata=request.metadata,
    )
    USAGE_RECORDS.append(record)

    return {
        "success": True,
        "record_id": record.record_id,
        "remaining": limit_check.get("remaining", 0) - request.quantity,
    }


@app.get("/v1/tenants/{tenant_id}/quota")
def get_quota(tenant_id: str):
    """حالة الحصة والاستخدام"""
    tenant = TENANTS.get(tenant_id)
    if not tenant:
        raise HTTPException(404, "المستأجر غير موجود")

    # Get subscription and plan
    subscription = None
    for sub in SUBSCRIPTIONS.values():
        if sub.tenant_id == tenant_id:
            subscription = sub
            break

    if not subscription:
        return {"error": "لا يوجد اشتراك نشط"}

    plan = PLANS.get(subscription.plan_id)
    if not plan:
        return {"error": "الخطة غير موجودة"}

    # Calculate usage for each metric
    usage_summary = {}
    for metric, limit in plan.limits.items():
        check = check_usage_limit(tenant_id, metric)
        usage_summary[metric] = {
            "limit": limit if limit != -1 else "unlimited",
            "used": check.get("used", 0),
            "remaining": check.get("remaining", "unlimited" if limit == -1 else 0),
            "percentage": round((check.get("used", 0) / limit) * 100, 1) if limit > 0 else 0,
        }

    return {
        "tenant_id": tenant_id,
        "plan": plan.name,
        "plan_ar": plan.name_ar,
        "subscription_status": subscription.status.value,
        "usage": usage_summary,
        "billing_cycle_ends": subscription.end_date.isoformat(),
    }


@app.get("/v1/enforce")
def enforce_quota(
    x_tenant_id: Optional[str] = Header(default=None),
    metric: str = Query(...),
):
    """التحقق من الصلاحيات (للـ Gateway)"""
    if not x_tenant_id:
        raise HTTPException(400, "Missing x-tenant-id header")

    check = check_usage_limit(x_tenant_id, metric)

    if not check["allowed"]:
        raise HTTPException(
            429,
            detail={
                "error": "quota_exceeded",
                "metric": metric,
                "limit": check.get("limit"),
                "used": check.get("used"),
            }
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


@app.get("/v1/tenants/{tenant_id}/invoices")
def list_invoices(
    tenant_id: str,
    status: Optional[InvoiceStatus] = None,
    limit: int = Query(default=20, le=100),
):
    """قائمة الفواتير"""
    if tenant_id not in TENANTS:
        raise HTTPException(404, "المستأجر غير موجود")

    invoices = [inv for inv in INVOICES.values() if inv.tenant_id == tenant_id]

    if status:
        invoices = [inv for inv in invoices if inv.status == status]

    invoices.sort(key=lambda x: x.issue_date, reverse=True)

    return {
        "invoices": [inv.dict() for inv in invoices[:limit]],
        "total": len(invoices),
    }


@app.get("/v1/invoices/{invoice_id}")
def get_invoice(invoice_id: str):
    """تفاصيل فاتورة"""
    invoice = INVOICES.get(invoice_id)
    if not invoice:
        raise HTTPException(404, "الفاتورة غير موجودة")

    tenant = TENANTS.get(invoice.tenant_id)

    return {
        "invoice": invoice.dict(),
        "tenant": tenant.dict() if tenant else None,
        "amount_yer": float(convert_to_yer(invoice.total)) if invoice.currency == Currency.USD else float(invoice.total),
    }


@app.post("/v1/tenants/{tenant_id}/invoices/generate")
def generate_tenant_invoice(tenant_id: str, background_tasks: BackgroundTasks):
    """توليد فاتورة يدوياً"""
    subscription = None
    for sub in SUBSCRIPTIONS.values():
        if sub.tenant_id == tenant_id:
            subscription = sub
            break

    if not subscription:
        raise HTTPException(404, "لا يوجد اشتراك")

    invoice = generate_invoice(subscription)
    INVOICES[invoice.invoice_id] = invoice

    logger.info(f"Invoice generated: {invoice.invoice_number} for tenant {tenant_id}")

    return {
        "success": True,
        "invoice": invoice.dict(),
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
                    "callback_url": f"https://api.sahool.com/api/v1/webhooks/tharwatt",
                },
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Tharwatt API error: {e}")
            raise HTTPException(502, f"Tharwatt payment gateway error: {str(e)}")


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
        logger.error(f"Stripe API error: {e}")
        raise HTTPException(502, f"Stripe payment error: {str(e)}")


@app.post("/v1/payments")
async def create_payment(request: CreatePaymentRequest, background_tasks: BackgroundTasks):
    """تسجيل دفعة"""
    invoice = INVOICES.get(request.invoice_id)
    if not invoice:
        raise HTTPException(404, "الفاتورة غير موجودة")

    if invoice.status == InvoiceStatus.PAID:
        raise HTTPException(400, "الفاتورة مدفوعة بالفعل")

    payment = Payment(
        payment_id=str(uuid.uuid4()),
        invoice_id=request.invoice_id,
        tenant_id=invoice.tenant_id,
        amount=request.amount,
        currency=invoice.currency,
        status=PaymentStatus.PENDING,
        method=request.method,
    )

    tharwatt_response = None
    stripe_response = None

    # Process payment based on method
    if request.method == PaymentMethod.CREDIT_CARD and STRIPE_API_KEY:
        # Stripe Payment Processing
        token = getattr(request, 'stripe_token', None)
        if token:
            stripe_response = await call_stripe_api(payment, token)
            if stripe_response.get("status") == "succeeded":
                payment.status = PaymentStatus.SUCCEEDED
                payment.processed_at = datetime.utcnow()
                payment.stripe_payment_id = stripe_response.get("stripe_charge_id")
            else:
                payment.status = PaymentStatus.PROCESSING
        else:
            # Mark as pending for client-side Stripe checkout
            payment.status = PaymentStatus.PENDING

    elif request.method == PaymentMethod.THARWATT and THARWATT_API_KEY:
        # Tharwatt Payment Gateway - بوابة ثروات
        phone_number = getattr(request, 'phone_number', '')
        if phone_number:
            tharwatt_response = await call_tharwatt_api(payment, phone_number)
            payment.status = PaymentStatus.PROCESSING
            logger.info(f"Tharwatt payment initiated: {payment.payment_id} - Response: {tharwatt_response}")
        else:
            payment.status = PaymentStatus.PENDING
            logger.info(f"Tharwatt payment pending phone: {payment.payment_id}")

    elif request.method == PaymentMethod.MOBILE_MONEY:
        # Mobile Money (Yemen operators) - الدفع بالمحفظة
        payment.status = PaymentStatus.PENDING
    elif request.method == PaymentMethod.BANK_TRANSFER:
        payment.status = PaymentStatus.PENDING
    elif request.method == PaymentMethod.CASH:
        payment.status = PaymentStatus.SUCCEEDED
        payment.processed_at = datetime.utcnow()
    else:
        payment.status = PaymentStatus.SUCCEEDED
        payment.processed_at = datetime.utcnow()

    PAYMENTS[payment.payment_id] = payment

    # Update invoice if payment succeeded
    if payment.status == PaymentStatus.SUCCEEDED:
        invoice.amount_paid += request.amount
        invoice.amount_due = invoice.total - invoice.amount_paid

        if invoice.amount_due <= 0:
            invoice.status = InvoiceStatus.PAID
            invoice.paid_date = date.today()

    logger.info(f"Payment {payment.payment_id} created for invoice {request.invoice_id}")

    # Publish payment event
    background_tasks.add_task(
        publish_event,
        "sahool.payment.created",
        {
            "payment_id": payment.payment_id,
            "invoice_id": payment.invoice_id,
            "tenant_id": payment.tenant_id,
            "amount": float(payment.amount),
            "currency": payment.currency.value,
            "method": payment.method.value,
            "status": payment.status.value,
        }
    )

    return {
        "success": True,
        "payment": payment.dict(),
        "invoice_status": invoice.status.value,
        "tharwatt_response": tharwatt_response,
        "stripe_response": stripe_response,
    }


@app.get("/v1/tenants/{tenant_id}/payments")
def list_payments(tenant_id: str, limit: int = Query(default=20, le=100)):
    """قائمة المدفوعات"""
    payments = [p for p in PAYMENTS.values() if p.tenant_id == tenant_id]
    payments.sort(key=lambda x: x.created_at, reverse=True)

    return {
        "payments": [p.dict() for p in payments[:limit]],
        "total": len(payments),
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
    phone_number: Optional[str] = None
    reference: Optional[str] = None  # Our payment_id
    timestamp: Optional[str] = None
    error_message: Optional[str] = None


@app.post("/v1/webhooks/tharwatt")
async def tharwatt_webhook(payload: TharwattWebhookPayload, background_tasks: BackgroundTasks):
    """
    Tharwatt payment webhook callback
    ويب هوك لتأكيد المدفوعات من ثروات
    """
    # Find payment by reference
    payment = None
    for p in PAYMENTS.values():
        if p.payment_id == payload.reference:
            payment = p
            break

    if not payment:
        logger.warning(f"Tharwatt webhook: Payment not found for reference {payload.reference}")
        raise HTTPException(404, "Payment not found")

    # Update payment status
    if payload.status == "completed":
        payment.status = PaymentStatus.SUCCEEDED
        payment.processed_at = datetime.utcnow()

        # Update invoice
        invoice = INVOICES.get(payment.invoice_id)
        if invoice:
            invoice.amount_paid += payment.amount
            invoice.amount_due = invoice.total - invoice.amount_paid
            if invoice.amount_due <= 0:
                invoice.status = InvoiceStatus.PAID
                invoice.paid_date = date.today()

        logger.info(f"Tharwatt payment completed: {payment.payment_id}")

        # Publish payment success event
        background_tasks.add_task(
            publish_event,
            "sahool.payment.succeeded",
            {
                "payment_id": payment.payment_id,
                "invoice_id": payment.invoice_id,
                "tenant_id": payment.tenant_id,
                "amount": float(payment.amount),
                "method": "tharwatt",
                "transaction_id": payload.transaction_id,
            }
        )

    elif payload.status == "failed":
        payment.status = PaymentStatus.FAILED
        payment.failure_reason = payload.error_message or "Payment failed"
        logger.warning(f"Tharwatt payment failed: {payment.payment_id} - {payload.error_message}")

        # Publish payment failed event
        background_tasks.add_task(
            publish_event,
            "sahool.payment.failed",
            {
                "payment_id": payment.payment_id,
                "invoice_id": payment.invoice_id,
                "error": payload.error_message,
            }
        )

    elif payload.status == "cancelled":
        payment.status = PaymentStatus.FAILED
        payment.failure_reason = "Payment cancelled by user"
        logger.info(f"Tharwatt payment cancelled: {payment.payment_id}")

    return {
        "success": True,
        "payment_id": payment.payment_id,
        "status": payment.status.value,
    }


# =============================================================================
# Stripe Webhook - ويب هوك سترايب
# =============================================================================


class StripeWebhookPayload(BaseModel):
    """Stripe webhook event payload"""
    id: str
    type: str
    data: Dict[str, Any]


def verify_stripe_signature(payload: bytes, signature: str) -> bool:
    """Verify Stripe webhook signature"""
    if not STRIPE_WEBHOOK_SECRET:
        return True  # Skip verification in dev

    try:
        import stripe
        stripe.Webhook.construct_event(payload, signature, STRIPE_WEBHOOK_SECRET)
        return True
    except Exception as e:
        logger.warning(f"Stripe signature verification failed: {e}")
        return False


@app.post("/v1/webhooks/stripe")
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks):
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

    # Handle different event types
    if event_type == "charge.succeeded":
        payment_id = data.get("metadata", {}).get("payment_id")
        if payment_id:
            payment = PAYMENTS.get(payment_id)
            if payment:
                payment.status = PaymentStatus.SUCCEEDED
                payment.processed_at = datetime.utcnow()
                payment.stripe_payment_id = data.get("id")

                # Update invoice
                invoice = INVOICES.get(payment.invoice_id)
                if invoice:
                    invoice.amount_paid += payment.amount
                    invoice.amount_due = invoice.total - invoice.amount_paid
                    if invoice.amount_due <= 0:
                        invoice.status = InvoiceStatus.PAID
                        invoice.paid_date = date.today()

                logger.info(f"Stripe payment succeeded: {payment_id}")

                # Publish payment success event
                background_tasks.add_task(
                    publish_event,
                    "sahool.payment.succeeded",
                    {
                        "payment_id": payment_id,
                        "invoice_id": payment.invoice_id,
                        "tenant_id": payment.tenant_id,
                        "amount": float(payment.amount),
                        "method": "stripe",
                        "stripe_charge_id": data.get("id"),
                    }
                )

    elif event_type == "charge.failed":
        payment_id = data.get("metadata", {}).get("payment_id")
        if payment_id:
            payment = PAYMENTS.get(payment_id)
            if payment:
                payment.status = PaymentStatus.FAILED
                payment.failure_reason = data.get("failure_message", "Payment failed")
                logger.warning(f"Stripe payment failed: {payment_id}")

                # Publish payment failed event
                background_tasks.add_task(
                    publish_event,
                    "sahool.payment.failed",
                    {
                        "payment_id": payment_id,
                        "error": payment.failure_reason,
                    }
                )

    elif event_type == "customer.subscription.updated":
        # Handle subscription updates from Stripe
        subscription_id = data.get("metadata", {}).get("subscription_id")
        if subscription_id:
            subscription = SUBSCRIPTIONS.get(subscription_id)
            if subscription:
                stripe_status = data.get("status")
                if stripe_status == "active":
                    subscription.status = SubscriptionStatus.ACTIVE
                elif stripe_status == "past_due":
                    subscription.status = SubscriptionStatus.PAST_DUE
                elif stripe_status == "canceled":
                    subscription.status = SubscriptionStatus.CANCELED

                logger.info(f"Stripe subscription updated: {subscription_id} -> {stripe_status}")

                # Publish subscription event
                background_tasks.add_task(
                    publish_event,
                    "sahool.subscription.updated",
                    {
                        "subscription_id": subscription_id,
                        "tenant_id": subscription.tenant_id,
                        "status": subscription.status.value,
                    }
                )

    return {"received": True}


# =============================================================================
# API Endpoints - Reports & Analytics
# =============================================================================


@app.get("/v1/reports/revenue")
def get_revenue_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    """تقرير الإيرادات"""
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()

    # Calculate revenue from paid invoices
    paid_invoices = [
        inv for inv in INVOICES.values()
        if inv.status == InvoiceStatus.PAID
        and inv.paid_date
        and start_date <= inv.paid_date <= end_date
    ]

    total_usd = sum(inv.total for inv in paid_invoices if inv.currency == Currency.USD)
    total_yer = sum(inv.total for inv in paid_invoices if inv.currency == Currency.YER)

    # Revenue by plan
    by_plan = {}
    for inv in paid_invoices:
        sub = SUBSCRIPTIONS.get(inv.subscription_id)
        if sub:
            plan_id = sub.plan_id
            by_plan[plan_id] = by_plan.get(plan_id, Decimal("0")) + inv.total

    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        },
        "total_revenue": {
            "usd": float(total_usd),
            "yer": float(total_yer + convert_to_yer(total_usd)),
        },
        "invoices_count": len(paid_invoices),
        "by_plan": {k: float(v) for k, v in by_plan.items()},
    }


@app.get("/v1/reports/subscriptions")
def get_subscriptions_report():
    """تقرير الاشتراكات"""
    by_status = {}
    by_plan = {}

    for sub in SUBSCRIPTIONS.values():
        # By status
        status = sub.status.value
        by_status[status] = by_status.get(status, 0) + 1

        # By plan
        by_plan[sub.plan_id] = by_plan.get(sub.plan_id, 0) + 1

    # Calculate MRR (Monthly Recurring Revenue)
    mrr = Decimal("0")
    for sub in SUBSCRIPTIONS.values():
        if sub.status == SubscriptionStatus.ACTIVE:
            plan = PLANS.get(sub.plan_id)
            if plan:
                mrr += plan.pricing.monthly_usd

    return {
        "total_subscriptions": len(SUBSCRIPTIONS),
        "by_status": by_status,
        "by_plan": by_plan,
        "mrr_usd": float(mrr),
        "mrr_yer": float(convert_to_yer(mrr)),
        "total_tenants": len(TENANTS),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8089)
