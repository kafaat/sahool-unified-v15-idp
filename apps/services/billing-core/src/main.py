"""
💰 SAHOOL Billing Core Service v15.5
خدمة الفوترة الأساسية - إدارة الاشتراكات والمدفوعات

Features:
- Plan management with tiered pricing
- Tenant/subscription lifecycle
- Usage-based billing
- Invoice generation
- Payment processing (Stripe integration)
- Multi-currency support (USD, YER)
"""

import os
import uuid
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum

from fastapi import FastAPI, HTTPException, Query, Header, Depends, BackgroundTasks
from pydantic import BaseModel, Field, EmailStr

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sahool-billing")

# =============================================================================
# App Configuration
# =============================================================================

app = FastAPI(
    title="SAHOOL Billing Core | خدمة الفوترة",
    version="15.5.0",
    description="Complete billing, subscription, and payment management for SAHOOL platform",
)

# Environment configuration
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "USD")
YER_EXCHANGE_RATE = float(os.getenv("YER_EXCHANGE_RATE", "250"))  # 1 USD = 250 YER


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


@app.post("/v1/payments")
def create_payment(request: CreatePaymentRequest):
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

    # Process payment based on method
    if request.method == PaymentMethod.CREDIT_CARD and STRIPE_API_KEY:
        # TODO: Integrate with Stripe
        # stripe.Charge.create(...)
        payment.status = PaymentStatus.SUCCEEDED
        payment.processed_at = datetime.utcnow()
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

    return {
        "success": True,
        "payment": payment.dict(),
        "invoice_status": invoice.status.value,
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
