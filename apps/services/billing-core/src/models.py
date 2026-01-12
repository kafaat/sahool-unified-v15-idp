"""
📊 SAHOOL Billing Core - Database Models
نماذج قاعدة البيانات - SQLAlchemy ORM Models

This module defines the database schema for:
- Subscriptions (الاشتراكات)
- Invoices (الفواتير)
- Payments (المدفوعات)
- Usage Records (سجلات الاستخدام)
"""

# Import enums from main (we'll reference the existing ones)
# These will be defined in main.py
import enum
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

# =============================================================================
# Enums - نسخة من الـEnums الموجودة في main.py
# =============================================================================


class SubscriptionStatus(str, enum.Enum):
    """حالة الاشتراك"""

    ACTIVE = "active"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


class InvoiceStatus(str, enum.Enum):
    """حالة الفاتورة"""

    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    """طريقة الدفع"""

    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    MOBILE_MONEY = "mobile_money"
    CASH = "cash"
    THARWATT = "tharwatt"


class PaymentStatus(str, enum.Enum):
    """حالة الدفعة"""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


class Currency(str, enum.Enum):
    """العملة"""

    USD = "USD"
    YER = "YER"


class BillingCycle(str, enum.Enum):
    """دورة الفوترة"""

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class PlanTier(str, enum.Enum):
    """مستوى الخطة"""

    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


# =============================================================================
# Database Models
# =============================================================================


class Plan(Base):
    """
    Plan Model - نموذج الخطة

    Represents a subscription plan with pricing and features
    يمثل خطة اشتراك مع التسعير والميزات
    """

    __tablename__ = "plans"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    # Plan Identifier (e.g., "free", "starter", "professional")
    plan_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="معرف الخطة الفريد",
    )

    # Names
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="اسم الخطة (EN)")

    name_ar: Mapped[str] = mapped_column(String(255), nullable=False, comment="اسم الخطة (AR)")

    # Descriptions
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="وصف الخطة (EN)")

    description_ar: Mapped[str] = mapped_column(Text, nullable=False, comment="وصف الخطة (AR)")

    # Tier
    tier: Mapped[PlanTier] = mapped_column(
        SQLEnum(PlanTier, name="plan_tier_enum"),
        nullable=False,
        index=True,
        comment="مستوى الخطة",
    )

    # Pricing (stored as JSONB for flexibility)
    pricing: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="تسعير الخطة (monthly_usd, quarterly_usd, yearly_usd, setup_fee_usd)",
    )

    # Features (stored as JSONB)
    features: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default={}, server_default="{}", comment="ميزات الخطة"
    )

    # Limits (stored as JSONB)
    limits: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default={}, server_default="{}", comment="حدود الخطة"
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
        comment="نشطة؟",
    )

    # Trial
    trial_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=14,
        server_default="14",
        comment="أيام الفترة التجريبية",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="تاريخ الإنشاء",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="تاريخ آخر تحديث",
    )

    # Indexes
    __table_args__ = (Index("idx_plan_tier_active", "tier", "is_active"),)

    def __repr__(self) -> str:
        return f"<Plan(id={self.id}, plan_id={self.plan_id}, name={self.name}, tier={self.tier})>"


class Tenant(Base):
    """
    Tenant Model - نموذج المستأجر

    Represents a customer/tenant in the system
    يمثل عميل/مستأجر في النظام
    """

    __tablename__ = "tenants"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    # Tenant ID (for external references)
    tenant_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="معرف المستأجر الفريد",
    )

    # Names
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="اسم المستأجر (EN)")

    name_ar: Mapped[str] = mapped_column(String(255), nullable=False, comment="اسم المستأجر (AR)")

    # Contact Info (stored as JSONB)
    contact: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="معلومات الاتصال (name, email, phone, address, etc.)",
    )

    # Tax ID
    tax_id: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="الرقم الضريبي")

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
        comment="نشط؟",
    )

    # Metadata (renamed to avoid SQLAlchemy reserved name conflict)
    extra_metadata: Mapped[dict | None] = mapped_column(
        "metadata",  # Database column name stays as 'metadata'
        JSONB,
        nullable=True,
        default={},
        server_default="{}",
        comment="بيانات إضافية",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="تاريخ الإنشاء",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="تاريخ آخر تحديث",
    )

    # Indexes
    __table_args__ = (Index("idx_tenant_active", "is_active"),)

    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, tenant_id={self.tenant_id}, name={self.name})>"


class Subscription(Base):
    """
    Subscription Model - نموذج الاشتراك

    Represents a tenant's subscription to a plan
    يمثل اشتراك المستأجر في خطة
    """

    __tablename__ = "subscriptions"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    # Foreign Keys
    tenant_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="المستأجر/العميل"
    )

    plan_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="معرف الخطة"
    )

    # Status
    status: Mapped[SubscriptionStatus] = mapped_column(
        SQLEnum(SubscriptionStatus, name="subscription_status_enum"),
        nullable=False,
        default=SubscriptionStatus.ACTIVE,
        index=True,
        comment="حالة الاشتراك",
    )

    billing_cycle: Mapped[BillingCycle] = mapped_column(
        SQLEnum(BillingCycle, name="billing_cycle_enum"),
        nullable=False,
        default=BillingCycle.MONTHLY,
        comment="دورة الفوترة",
    )

    currency: Mapped[Currency] = mapped_column(
        SQLEnum(Currency, name="currency_enum"),
        nullable=False,
        default=Currency.USD,
        comment="العملة",
    )

    # Dates
    start_date: Mapped[date] = mapped_column(Date, nullable=False, comment="تاريخ البدء")

    end_date: Mapped[date] = mapped_column(Date, nullable=False, comment="تاريخ الانتهاء")

    trial_end_date: Mapped[date | None] = mapped_column(
        Date, nullable=True, comment="تاريخ انتهاء الفترة التجريبية"
    )

    canceled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="تاريخ الإلغاء"
    )

    # Billing Dates
    next_billing_date: Mapped[date] = mapped_column(
        Date, nullable=False, index=True, comment="تاريخ الفوترة التالي"
    )

    last_billing_date: Mapped[date | None] = mapped_column(
        Date, nullable=True, comment="تاريخ آخر فوترة"
    )

    # Payment Method
    payment_method: Mapped[PaymentMethod | None] = mapped_column(
        SQLEnum(PaymentMethod, name="payment_method_enum"),
        nullable=True,
        comment="طريقة الدفع",
    )

    # External IDs
    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True, comment="معرف الاشتراك في Stripe"
    )

    # Metadata (renamed to avoid SQLAlchemy reserved name conflict)
    extra_metadata: Mapped[dict | None] = mapped_column(
        "metadata",  # Database column name stays as 'metadata'
        JSONB,
        nullable=True,
        default={},
        server_default="{}",
        comment="بيانات إضافية",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="تاريخ الإنشاء",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="تاريخ آخر تحديث",
    )

    # Relationships
    invoices: Mapped[list["Invoice"]] = relationship(
        "Invoice",
        back_populates="subscription",
        cascade="all, delete-orphan",
    )

    usage_records: Mapped[list["UsageRecord"]] = relationship(
        "UsageRecord",
        back_populates="subscription",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("idx_subscription_tenant_status", "tenant_id", "status"),
        Index("idx_subscription_next_billing", "next_billing_date", "status"),
    )

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, tenant={self.tenant_id}, plan={self.plan_id}, status={self.status})>"


class Invoice(Base):
    """
    Invoice Model - نموذج الفاتورة

    Represents a billing invoice for a subscription
    يمثل فاتورة للاشتراك
    """

    __tablename__ = "invoices"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    # Invoice Number (human-readable)
    invoice_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="رقم الفاتورة (SAH-2025-0001)",
    )

    # Foreign Keys
    tenant_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="المستأجر/العميل"
    )

    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="معرف الاشتراك",
    )

    # Status
    status: Mapped[InvoiceStatus] = mapped_column(
        SQLEnum(InvoiceStatus, name="invoice_status_enum"),
        nullable=False,
        default=InvoiceStatus.DRAFT,
        index=True,
        comment="حالة الفاتورة",
    )

    currency: Mapped[Currency] = mapped_column(
        SQLEnum(Currency, name="currency_enum"),
        nullable=False,
        default=Currency.USD,
        comment="العملة",
    )

    # Dates
    issue_date: Mapped[date] = mapped_column(
        Date, nullable=False, index=True, comment="تاريخ الإصدار"
    )

    due_date: Mapped[date] = mapped_column(
        Date, nullable=False, index=True, comment="تاريخ الاستحقاق"
    )

    paid_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="تاريخ الدفع")

    # Amounts (stored as Numeric for precision)
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, comment="المجموع الفرعي"
    )

    tax_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0"),
        server_default="0",
        comment="معدل الضريبة",
    )

    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0"),
        server_default="0",
        comment="مبلغ الضريبة",
    )

    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0"),
        server_default="0",
        comment="مبلغ الخصم",
    )

    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, comment="المجموع الكلي")

    amount_paid: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0"),
        server_default="0",
        comment="المبلغ المدفوع",
    )

    amount_due: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, comment="المبلغ المستحق"
    )

    # Line Items (stored as JSONB for flexibility)
    line_items: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=[], server_default="[]", comment="بنود الفاتورة"
    )

    # Notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="ملاحظات (EN)")

    notes_ar: Mapped[str | None] = mapped_column(Text, nullable=True, comment="ملاحظات (AR)")

    # External IDs
    stripe_invoice_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True, comment="معرف الفاتورة في Stripe"
    )

    # Metadata (renamed to avoid SQLAlchemy reserved name conflict)
    extra_metadata: Mapped[dict | None] = mapped_column(
        "metadata",  # Database column name stays as 'metadata'
        JSONB,
        nullable=True,
        default={},
        server_default="{}",
        comment="بيانات إضافية",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="تاريخ الإنشاء",
    )

    # Relationships
    subscription: Mapped["Subscription"] = relationship(
        "Subscription",
        back_populates="invoices",
    )

    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="invoice",
        cascade="all, delete-orphan",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="check_subtotal_positive"),
        CheckConstraint("total >= 0", name="check_total_positive"),
        CheckConstraint("amount_paid >= 0", name="check_amount_paid_positive"),
        CheckConstraint("amount_due >= 0", name="check_amount_due_positive"),
        Index("idx_invoice_tenant_status", "tenant_id", "status"),
        Index("idx_invoice_due_date_status", "due_date", "status"),
    )

    def __repr__(self) -> str:
        return f"<Invoice(id={self.id}, number={self.invoice_number}, total={self.total}, status={self.status})>"


class Payment(Base):
    """
    Payment Model - نموذج الدفعة

    Represents a payment made towards an invoice
    يمثل دفعة تم إجراؤها للفاتورة
    """

    __tablename__ = "payments"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    # Foreign Keys
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="معرف الفاتورة",
    )

    tenant_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="المستأجر/العميل"
    )

    # Amount
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, comment="المبلغ")

    currency: Mapped[Currency] = mapped_column(
        SQLEnum(Currency, name="currency_enum"),
        nullable=False,
        default=Currency.USD,
        comment="العملة",
    )

    # Status & Method
    status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus, name="payment_status_enum"),
        nullable=False,
        default=PaymentStatus.PENDING,
        index=True,
        comment="حالة الدفعة",
    )

    method: Mapped[PaymentMethod] = mapped_column(
        SQLEnum(PaymentMethod, name="payment_method_enum"),
        nullable=False,
        comment="طريقة الدفع",
    )

    # Processing Details
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="تاريخ الدفع الفعلي"
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="تاريخ المعالجة"
    )

    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="سبب الفشل")

    # External References
    stripe_payment_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True, comment="معرف الدفعة في Stripe"
    )

    tharwatt_transaction_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True, comment="معرف المعاملة في ثروات"
    )

    receipt_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="رابط الإيصال"
    )

    # Metadata (renamed to avoid SQLAlchemy reserved name conflict)
    extra_metadata: Mapped[dict | None] = mapped_column(
        "metadata",  # Database column name stays as 'metadata'
        JSONB,
        nullable=True,
        default={},
        server_default="{}",
        comment="بيانات إضافية",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="تاريخ الإنشاء",
    )

    # Relationships
    invoice: Mapped["Invoice"] = relationship(
        "Invoice",
        back_populates="payments",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("amount > 0", name="check_payment_amount_positive"),
        Index("idx_payment_tenant_status", "tenant_id", "status"),
        Index("idx_payment_created", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, amount={self.amount}, method={self.method}, status={self.status})>"


class UsageRecord(Base):
    """
    Usage Record Model - نموذج سجل الاستخدام

    Tracks usage metrics for usage-based billing
    يتتبع مقاييس الاستخدام للفوترة المستندة إلى الاستخدام
    """

    __tablename__ = "usage_records"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    # Foreign Keys
    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="معرف الاشتراك",
    )

    tenant_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="المستأجر/العميل"
    )

    # Metric Details
    metric_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="نوع المقياس (e.g., satellite_analyses, api_calls)",
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1, comment="الكمية")

    # Timestamps
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
        index=True,
        comment="تاريخ التسجيل",
    )

    # Metadata (renamed to avoid SQLAlchemy reserved name conflict)
    extra_metadata: Mapped[dict | None] = mapped_column(
        "metadata",  # Database column name stays as 'metadata'
        JSONB,
        nullable=True,
        default={},
        server_default="{}",
        comment="بيانات إضافية (e.g., resource_id, user_id)",
    )

    # Relationships
    subscription: Mapped["Subscription"] = relationship(
        "Subscription",
        back_populates="usage_records",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_quantity_positive"),
        Index("idx_usage_subscription_metric", "subscription_id", "metric_type"),
        Index("idx_usage_tenant_metric_date", "tenant_id", "metric_type", "recorded_at"),
        Index("idx_usage_recorded_at", "recorded_at"),
    )

    def __repr__(self) -> str:
        return f"<UsageRecord(id={self.id}, metric={self.metric_type}, quantity={self.quantity}, recorded_at={self.recorded_at})>"
