"""
SAHOOL Tenant Service - Multi-tenancy Management
=================================================
Layer: Platform Core (Layer 1)
Purpose: Tenant management, subscription, billing, and multi-tenant isolation
"""

import os
import asyncio
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import uuid
import secrets

from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, validator
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Integer,
    Float,
    Date,
    select,
    update,
    func,
)
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import structlog
import enum

# Shared imports
import sys

sys.path.insert(0, "/app/shared")
from database import Database, BaseModel as DBBaseModel
from events.base_event import BaseEvent, EventBus
from utils.logging import setup_logging
from metrics import MetricsManager

# ============================================================================
# Configuration
# ============================================================================


class Settings:
    """Tenant service configuration"""

    SERVICE_NAME = "tenant-service"
    SERVICE_PORT = int(os.getenv("TENANT_SERVICE_PORT", "8084"))

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://sahool:sahool@postgres:5432/sahool_tenants",
    )
    NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")

    # Trial Settings
    TRIAL_DAYS = int(os.getenv("TRIAL_DAYS", "14"))

    # Limits by plan
    PLAN_LIMITS = {
        "free": {
            "max_users": 3,
            "max_fields": 5,
            "max_area_hectares": 50,
            "features": ["basic_weather", "basic_tasks", "basic_alerts"],
        },
        "starter": {
            "max_users": 10,
            "max_fields": 20,
            "max_area_hectares": 500,
            "features": ["weather", "tasks", "alerts", "ndvi_basic", "reports_basic"],
        },
        "professional": {
            "max_users": 50,
            "max_fields": 100,
            "max_area_hectares": 5000,
            "features": [
                "weather",
                "tasks",
                "alerts",
                "ndvi",
                "reports",
                "ai_advisor",
                "irrigation",
            ],
        },
        "enterprise": {
            "max_users": -1,  # Unlimited
            "max_fields": -1,
            "max_area_hectares": -1,
            "features": ["all"],
        },
    }


settings = Settings()

# ============================================================================
# Logging & Metrics
# ============================================================================

setup_logging(settings.SERVICE_NAME)
logger = structlog.get_logger()

tenant_operations = Counter(
    "tenant_operations_total", "Tenant operations", ["operation", "status"]
)

# ============================================================================
# Database Models
# ============================================================================


class TenantStatus(str, enum.Enum):
    ACTIVE = "active"
    TRIAL = "trial"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    PENDING = "pending"


class SubscriptionPlan(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class BillingCycle(str, enum.Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Tenant(DBBaseModel):
    """Tenant model - represents a farm/organization"""

    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic Info
    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)

    # Contact Info
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)

    # Organization Details
    organization_type = Column(
        String(50), default="farm"
    )  # farm, cooperative, company, research
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)

    # Location
    country = Column(String(100), default="Yemen")
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)

    # Subscription & Billing
    plan = Column(String(20), default=SubscriptionPlan.FREE.value)
    billing_cycle = Column(String(20), default=BillingCycle.MONTHLY.value)
    subscription_start = Column(Date, nullable=True)
    subscription_end = Column(Date, nullable=True)
    trial_end = Column(Date, nullable=True)

    # Status
    status = Column(String(20), default=TenantStatus.PENDING.value)

    # Limits Override (for custom plans)
    max_users_override = Column(Integer, nullable=True)
    max_fields_override = Column(Integer, nullable=True)
    max_area_override = Column(Float, nullable=True)
    custom_features = Column(ARRAY(String), nullable=True)

    # Settings
    settings = Column(JSON, default={})
    default_language = Column(String(10), default="ar")
    default_timezone = Column(String(50), default="Asia/Aden")
    default_currency = Column(String(10), default="YER")  # Yemeni Rial

    # API Access
    api_enabled = Column(Boolean, default=False)
    api_key_prefix = Column(String(10), nullable=True)

    # Metadata
    owner_user_id = Column(UUID(as_uuid=True), nullable=True)  # Main admin
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    usage_records = relationship(
        "TenantUsage", back_populates="tenant", cascade="all, delete-orphan"
    )
    invoices = relationship(
        "Invoice", back_populates="tenant", cascade="all, delete-orphan"
    )
    features = relationship(
        "TenantFeature", back_populates="tenant", cascade="all, delete-orphan"
    )


class TenantUsage(DBBaseModel):
    """Track tenant resource usage"""

    __tablename__ = "tenant_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )

    # Usage Period
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    # Resource Usage
    user_count = Column(Integer, default=0)
    field_count = Column(Integer, default=0)
    total_area_hectares = Column(Float, default=0.0)
    task_count = Column(Integer, default=0)
    alert_count = Column(Integer, default=0)
    ndvi_requests = Column(Integer, default=0)
    ai_queries = Column(Integer, default=0)
    storage_mb = Column(Float, default=0.0)
    api_calls = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="usage_records")


class TenantFeature(DBBaseModel):
    """Feature flags for tenant"""

    __tablename__ = "tenant_features"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )

    feature_code = Column(String(100), nullable=False)
    is_enabled = Column(Boolean, default=True)

    # Optional limits for feature
    limit_value = Column(Integer, nullable=True)
    config = Column(JSON, nullable=True)

    # Validity
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="features")


class Invoice(DBBaseModel):
    """Billing invoices"""

    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )

    invoice_number = Column(String(50), unique=True, nullable=False)

    # Billing Period
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    # Amounts
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(10), default="YER")

    # Status
    status = Column(String(20), default="pending")  # pending, paid, overdue, cancelled
    due_date = Column(Date, nullable=False)
    paid_date = Column(Date, nullable=True)

    # Payment Details
    payment_method = Column(String(50), nullable=True)
    payment_reference = Column(String(255), nullable=True)

    # Line Items
    line_items = Column(JSON, default=[])

    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="invoices")


class PricingPlan(DBBaseModel):
    """Pricing plans configuration"""

    __tablename__ = "pricing_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    name_ar = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)

    # Pricing
    monthly_price = Column(Float, nullable=False)
    yearly_price = Column(Float, nullable=False)
    currency = Column(String(10), default="YER")

    # Limits
    max_users = Column(Integer, default=-1)
    max_fields = Column(Integer, default=-1)
    max_area_hectares = Column(Float, default=-1)

    # Features
    features = Column(ARRAY(String), default=[])

    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)

    # Metadata
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# Pydantic Schemas
# ============================================================================


class TenantCreate(BaseModel):
    """Create tenant request"""

    name: str = Field(..., min_length=2, max_length=255)
    name_ar: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    organization_type: str = "farm"
    country: str = "Yemen"
    region: Optional[str] = None
    city: Optional[str] = None
    owner_user_id: Optional[uuid.UUID] = None

    @validator("organization_type")
    def validate_org_type(cls, v):
        allowed = ["farm", "cooperative", "company", "research", "government"]
        if v not in allowed:
            raise ValueError(f"organization_type must be one of {allowed}")
        return v


class TenantUpdate(BaseModel):
    """Update tenant request"""

    name: Optional[str] = None
    name_ar: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    logo_url: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    default_language: Optional[str] = None
    default_timezone: Optional[str] = None
    default_currency: Optional[str] = None


class TenantResponse(BaseModel):
    """Tenant response"""

    id: uuid.UUID
    name: str
    name_ar: Optional[str]
    slug: str
    email: str
    phone: Optional[str]
    website: Optional[str]
    organization_type: str
    description: Optional[str]
    description_ar: Optional[str]
    logo_url: Optional[str]
    country: str
    region: Optional[str]
    city: Optional[str]
    address: Optional[str]
    plan: str
    billing_cycle: str
    subscription_start: Optional[date]
    subscription_end: Optional[date]
    trial_end: Optional[date]
    status: str
    settings: Dict[str, Any]
    default_language: str
    default_timezone: str
    default_currency: str
    api_enabled: bool
    owner_user_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TenantLimitsResponse(BaseModel):
    """Tenant limits response"""

    max_users: int
    current_users: int
    max_fields: int
    current_fields: int
    max_area_hectares: float
    current_area_hectares: float
    features: List[str]


class UsageResponse(BaseModel):
    """Usage record response"""

    period_start: date
    period_end: date
    user_count: int
    field_count: int
    total_area_hectares: float
    task_count: int
    alert_count: int
    ndvi_requests: int
    ai_queries: int
    storage_mb: float
    api_calls: int

    class Config:
        from_attributes = True


class SubscriptionUpdate(BaseModel):
    """Update subscription request"""

    plan: str
    billing_cycle: str = "monthly"


class InvoiceResponse(BaseModel):
    """Invoice response"""

    id: uuid.UUID
    invoice_number: str
    period_start: date
    period_end: date
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    currency: str
    status: str
    due_date: date
    paid_date: Optional[date]
    line_items: List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class PricingPlanResponse(BaseModel):
    """Pricing plan response"""

    code: str
    name: str
    name_ar: Optional[str]
    description: Optional[str]
    description_ar: Optional[str]
    monthly_price: float
    yearly_price: float
    currency: str
    max_users: int
    max_fields: int
    max_area_hectares: float
    features: List[str]

    class Config:
        from_attributes = True


# ============================================================================
# Tenant Service
# ============================================================================


class TenantService:
    """Core tenant management service"""

    def __init__(self, db: Database, event_bus: EventBus):
        self.db = db
        self.event_bus = event_bus

    def _generate_slug(self, name: str) -> str:
        """Generate URL-friendly slug from name"""
        import re

        slug = name.lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s_-]+", "-", slug)
        slug = slug.strip("-")
        return f"{slug}-{secrets.token_hex(4)}"

    async def create_tenant(self, data: TenantCreate) -> Tenant:
        """Create new tenant"""
        async with self.db.session() as session:
            # Generate unique slug
            slug = self._generate_slug(data.name)

            # Check if email exists
            existing = await session.execute(
                select(Tenant).where(Tenant.email == data.email)
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

            tenant = Tenant(
                name=data.name,
                name_ar=data.name_ar,
                slug=slug,
                email=data.email,
                phone=data.phone,
                organization_type=data.organization_type,
                country=data.country,
                region=data.region,
                city=data.city,
                owner_user_id=data.owner_user_id,
                plan=SubscriptionPlan.FREE.value,
                status=TenantStatus.TRIAL.value,
                trial_end=date.today() + timedelta(days=settings.TRIAL_DAYS),
            )

            session.add(tenant)
            await session.commit()
            await session.refresh(tenant)

            # Create default features based on plan
            await self._create_default_features(session, tenant)

            # Emit event
            await self.event_bus.publish(
                "tenant.created",
                {
                    "tenant_id": str(tenant.id),
                    "name": tenant.name,
                    "plan": tenant.plan,
                    "trial_end": (
                        tenant.trial_end.isoformat() if tenant.trial_end else None
                    ),
                },
            )

            logger.info("Tenant created", tenant_id=str(tenant.id), name=tenant.name)
            return tenant

    async def _create_default_features(self, session, tenant: Tenant):
        """Create default features for tenant based on plan"""
        plan_config = settings.PLAN_LIMITS.get(
            tenant.plan, settings.PLAN_LIMITS["free"]
        )

        for feature_code in plan_config["features"]:
            feature = TenantFeature(
                tenant_id=tenant.id, feature_code=feature_code, is_enabled=True
            )
            session.add(feature)

        await session.commit()

    async def get_tenant(self, tenant_id: uuid.UUID) -> Optional[Tenant]:
        """Get tenant by ID"""
        async with self.db.session() as session:
            result = await session.execute(
                select(Tenant)
                .options(selectinload(Tenant.features))
                .where(Tenant.id == tenant_id)
            )
            return result.scalar_one_or_none()

    async def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug"""
        async with self.db.session() as session:
            result = await session.execute(
                select(Tenant)
                .options(selectinload(Tenant.features))
                .where(Tenant.slug == slug)
            )
            return result.scalar_one_or_none()

    async def update_tenant(self, tenant_id: uuid.UUID, data: TenantUpdate) -> Tenant:
        """Update tenant"""
        async with self.db.session() as session:
            result = await session.execute(select(Tenant).where(Tenant.id == tenant_id))
            tenant = result.scalar_one_or_none()

            if not tenant:
                raise HTTPException(status_code=404, detail="Tenant not found")

            update_data = data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(tenant, key, value)

            tenant.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(tenant)

            # Emit event
            await self.event_bus.publish(
                "tenant.updated",
                {
                    "tenant_id": str(tenant.id),
                    "updated_fields": list(update_data.keys()),
                },
            )

            return tenant

    async def get_limits(self, tenant_id: uuid.UUID) -> TenantLimitsResponse:
        """Get tenant limits and current usage"""
        async with self.db.session() as session:
            result = await session.execute(
                select(Tenant)
                .options(selectinload(Tenant.features))
                .where(Tenant.id == tenant_id)
            )
            tenant = result.scalar_one_or_none()

            if not tenant:
                raise HTTPException(status_code=404, detail="Tenant not found")

            # Get plan config
            plan_config = settings.PLAN_LIMITS.get(
                tenant.plan, settings.PLAN_LIMITS["free"]
            )

            # Use overrides if set
            max_users = tenant.max_users_override or plan_config["max_users"]
            max_fields = tenant.max_fields_override or plan_config["max_fields"]
            max_area = tenant.max_area_override or plan_config["max_area_hectares"]

            # Get current usage (would typically come from other services)
            # For now, get from latest usage record
            usage_result = await session.execute(
                select(TenantUsage)
                .where(TenantUsage.tenant_id == tenant_id)
                .order_by(TenantUsage.period_end.desc())
                .limit(1)
            )
            latest_usage = usage_result.scalar_one_or_none()

            current_users = latest_usage.user_count if latest_usage else 0
            current_fields = latest_usage.field_count if latest_usage else 0
            current_area = latest_usage.total_area_hectares if latest_usage else 0.0

            # Get features
            features = tenant.custom_features or plan_config["features"]

            return TenantLimitsResponse(
                max_users=max_users,
                current_users=current_users,
                max_fields=max_fields,
                current_fields=current_fields,
                max_area_hectares=max_area,
                current_area_hectares=current_area,
                features=features,
            )

    async def check_limit(
        self, tenant_id: uuid.UUID, resource: str, requested: int = 1
    ) -> bool:
        """Check if tenant can use more of a resource"""
        limits = await self.get_limits(tenant_id)

        if resource == "users":
            if limits.max_users == -1:  # Unlimited
                return True
            return limits.current_users + requested <= limits.max_users
        elif resource == "fields":
            if limits.max_fields == -1:
                return True
            return limits.current_fields + requested <= limits.max_fields
        elif resource == "area":
            if limits.max_area_hectares == -1:
                return True
            return limits.current_area_hectares + requested <= limits.max_area_hectares

        return True

    async def has_feature(self, tenant_id: uuid.UUID, feature_code: str) -> bool:
        """Check if tenant has access to a feature"""
        async with self.db.session() as session:
            result = await session.execute(
                select(Tenant)
                .options(selectinload(Tenant.features))
                .where(Tenant.id == tenant_id)
            )
            tenant = result.scalar_one_or_none()

            if not tenant:
                return False

            # Check custom features first
            if tenant.custom_features:
                if (
                    "all" in tenant.custom_features
                    or feature_code in tenant.custom_features
                ):
                    return True

            # Check plan features
            plan_config = settings.PLAN_LIMITS.get(
                tenant.plan, settings.PLAN_LIMITS["free"]
            )
            if (
                "all" in plan_config["features"]
                or feature_code in plan_config["features"]
            ):
                return True

            # Check tenant-specific features
            for feature in tenant.features:
                if feature.feature_code == feature_code and feature.is_enabled:
                    if feature.valid_until and feature.valid_until < datetime.utcnow():
                        continue
                    return True

            return False

    async def update_subscription(
        self, tenant_id: uuid.UUID, data: SubscriptionUpdate
    ) -> Tenant:
        """Update tenant subscription"""
        async with self.db.session() as session:
            result = await session.execute(select(Tenant).where(Tenant.id == tenant_id))
            tenant = result.scalar_one_or_none()

            if not tenant:
                raise HTTPException(status_code=404, detail="Tenant not found")

            old_plan = tenant.plan
            tenant.plan = data.plan
            tenant.billing_cycle = data.billing_cycle
            tenant.subscription_start = date.today()

            # Calculate subscription end based on billing cycle
            if data.billing_cycle == BillingCycle.MONTHLY.value:
                tenant.subscription_end = date.today() + timedelta(days=30)
            else:
                tenant.subscription_end = date.today() + timedelta(days=365)

            # Update status
            if tenant.status == TenantStatus.TRIAL.value:
                tenant.status = TenantStatus.ACTIVE.value

            await session.commit()
            await session.refresh(tenant)

            # Update features
            # Delete old features
            await session.execute(
                delete(TenantFeature).where(TenantFeature.tenant_id == tenant_id)
            )
            await self._create_default_features(session, tenant)

            # Emit event
            await self.event_bus.publish(
                "tenant.subscription.changed",
                {
                    "tenant_id": str(tenant.id),
                    "old_plan": old_plan,
                    "new_plan": tenant.plan,
                    "billing_cycle": tenant.billing_cycle,
                },
            )

            return tenant

    async def record_usage(
        self,
        tenant_id: uuid.UUID,
        user_count: int = 0,
        field_count: int = 0,
        area_hectares: float = 0.0,
        task_count: int = 0,
        alert_count: int = 0,
        ndvi_requests: int = 0,
        ai_queries: int = 0,
        storage_mb: float = 0.0,
        api_calls: int = 0,
    ):
        """Record tenant resource usage"""
        async with self.db.session() as session:
            today = date.today()
            period_start = today.replace(day=1)
            next_month = period_start.replace(month=period_start.month % 12 + 1)
            period_end = next_month - timedelta(days=1)

            # Get or create usage record for this period
            result = await session.execute(
                select(TenantUsage).where(
                    TenantUsage.tenant_id == tenant_id,
                    TenantUsage.period_start == period_start,
                )
            )
            usage = result.scalar_one_or_none()

            if not usage:
                usage = TenantUsage(
                    tenant_id=tenant_id,
                    period_start=period_start,
                    period_end=period_end,
                )
                session.add(usage)

            # Update counts
            usage.user_count = user_count
            usage.field_count = field_count
            usage.total_area_hectares = area_hectares
            usage.task_count += task_count
            usage.alert_count += alert_count
            usage.ndvi_requests += ndvi_requests
            usage.ai_queries += ai_queries
            usage.storage_mb = storage_mb
            usage.api_calls += api_calls

            await session.commit()

    async def get_usage_history(
        self, tenant_id: uuid.UUID, months: int = 12
    ) -> List[TenantUsage]:
        """Get tenant usage history"""
        async with self.db.session() as session:
            cutoff = date.today() - timedelta(days=months * 30)

            result = await session.execute(
                select(TenantUsage)
                .where(
                    TenantUsage.tenant_id == tenant_id,
                    TenantUsage.period_start >= cutoff,
                )
                .order_by(TenantUsage.period_start.desc())
            )
            return result.scalars().all()

    async def get_invoices(self, tenant_id: uuid.UUID) -> List[Invoice]:
        """Get tenant invoices"""
        async with self.db.session() as session:
            result = await session.execute(
                select(Invoice)
                .where(Invoice.tenant_id == tenant_id)
                .order_by(Invoice.created_at.desc())
            )
            return result.scalars().all()

    async def suspend_tenant(self, tenant_id: uuid.UUID, reason: str):
        """Suspend tenant"""
        async with self.db.session() as session:
            result = await session.execute(select(Tenant).where(Tenant.id == tenant_id))
            tenant = result.scalar_one_or_none()

            if not tenant:
                raise HTTPException(status_code=404, detail="Tenant not found")

            tenant.status = TenantStatus.SUSPENDED.value
            await session.commit()

            # Emit event
            await self.event_bus.publish(
                "tenant.suspended", {"tenant_id": str(tenant.id), "reason": reason}
            )

    async def activate_tenant(self, tenant_id: uuid.UUID):
        """Activate suspended tenant"""
        async with self.db.session() as session:
            result = await session.execute(select(Tenant).where(Tenant.id == tenant_id))
            tenant = result.scalar_one_or_none()

            if not tenant:
                raise HTTPException(status_code=404, detail="Tenant not found")

            tenant.status = TenantStatus.ACTIVE.value
            await session.commit()

            # Emit event
            await self.event_bus.publish(
                "tenant.activated", {"tenant_id": str(tenant.id)}
            )

    async def list_tenants(
        self,
        page: int = 1,
        page_size: int = 20,
        status_filter: Optional[str] = None,
        plan_filter: Optional[str] = None,
        search: Optional[str] = None,
    ) -> tuple[List[Tenant], int]:
        """List tenants with pagination and filters"""
        async with self.db.session() as session:
            query = select(Tenant)
            count_query = select(func.count(Tenant.id))

            if status_filter:
                query = query.where(Tenant.status == status_filter)
                count_query = count_query.where(Tenant.status == status_filter)

            if plan_filter:
                query = query.where(Tenant.plan == plan_filter)
                count_query = count_query.where(Tenant.plan == plan_filter)

            if search:
                search_filter = f"%{search}%"
                query = query.where(
                    (Tenant.name.ilike(search_filter))
                    | (Tenant.name_ar.ilike(search_filter))
                    | (Tenant.email.ilike(search_filter))
                )
                count_query = count_query.where(
                    (Tenant.name.ilike(search_filter))
                    | (Tenant.name_ar.ilike(search_filter))
                    | (Tenant.email.ilike(search_filter))
                )

            # Get total count
            total_result = await session.execute(count_query)
            total = total_result.scalar()

            # Apply pagination
            offset = (page - 1) * page_size
            query = (
                query.offset(offset).limit(page_size).order_by(Tenant.created_at.desc())
            )

            result = await session.execute(query)
            tenants = result.scalars().all()

            return tenants, total

    async def get_pricing_plans(self) -> List[PricingPlan]:
        """Get all active pricing plans"""
        async with self.db.session() as session:
            result = await session.execute(
                select(PricingPlan)
                .where(PricingPlan.is_active == True, PricingPlan.is_public == True)
                .order_by(PricingPlan.sort_order)
            )
            return result.scalars().all()


# ============================================================================
# Dependencies
# ============================================================================

db: Database = None
event_bus: EventBus = None
tenant_service: TenantService = None

# ============================================================================
# FastAPI Application
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global db, event_bus, tenant_service

    logger.info("Starting Tenant Service...")

    db = Database(settings.DATABASE_URL)
    await db.connect()

    event_bus = EventBus(settings.NATS_URL)
    await event_bus.connect()

    tenant_service = TenantService(db, event_bus)

    logger.info("Tenant Service started successfully")

    yield

    logger.info("Shutting down Tenant Service...")
    await event_bus.close()
    await db.disconnect()


app = FastAPI(
    title="SAHOOL Tenant Service",
    description="Multi-tenancy Management Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# API Endpoints
# ============================================================================


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME}


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Tenant CRUD
@app.post(
    "/api/v1/tenants",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tenant(data: TenantCreate):
    """Create new tenant"""
    tenant = await tenant_service.create_tenant(data)
    tenant_operations.labels(operation="create", status="success").inc()
    return tenant


@app.get("/api/v1/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: uuid.UUID):
    """Get tenant by ID"""
    tenant = await tenant_service.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@app.get("/api/v1/tenants/by-slug/{slug}", response_model=TenantResponse)
async def get_tenant_by_slug(slug: str):
    """Get tenant by slug"""
    tenant = await tenant_service.get_tenant_by_slug(slug)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@app.patch("/api/v1/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(tenant_id: uuid.UUID, data: TenantUpdate):
    """Update tenant"""
    tenant = await tenant_service.update_tenant(tenant_id, data)
    tenant_operations.labels(operation="update", status="success").inc()
    return tenant


@app.get("/api/v1/tenants")
async def list_tenants(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = None,
    plan_filter: Optional[str] = None,
    search: Optional[str] = None,
):
    """List all tenants with pagination"""
    tenants, total = await tenant_service.list_tenants(
        page=page,
        page_size=page_size,
        status_filter=status_filter,
        plan_filter=plan_filter,
        search=search,
    )

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": tenants,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# Limits & Features
@app.get("/api/v1/tenants/{tenant_id}/limits", response_model=TenantLimitsResponse)
async def get_tenant_limits(tenant_id: uuid.UUID):
    """Get tenant limits and current usage"""
    return await tenant_service.get_limits(tenant_id)


@app.get("/api/v1/tenants/{tenant_id}/check-limit")
async def check_tenant_limit(tenant_id: uuid.UUID, resource: str, requested: int = 1):
    """Check if tenant can use more of a resource"""
    can_use = await tenant_service.check_limit(tenant_id, resource, requested)
    return {"can_use": can_use, "resource": resource, "requested": requested}


@app.get("/api/v1/tenants/{tenant_id}/features/{feature_code}")
async def check_tenant_feature(tenant_id: uuid.UUID, feature_code: str):
    """Check if tenant has access to a feature"""
    has_feature = await tenant_service.has_feature(tenant_id, feature_code)
    return {"has_feature": has_feature, "feature_code": feature_code}


# Subscription
@app.put("/api/v1/tenants/{tenant_id}/subscription", response_model=TenantResponse)
async def update_subscription(tenant_id: uuid.UUID, data: SubscriptionUpdate):
    """Update tenant subscription"""
    tenant = await tenant_service.update_subscription(tenant_id, data)
    return tenant


# Usage
@app.post("/api/v1/tenants/{tenant_id}/usage")
async def record_usage(
    tenant_id: uuid.UUID,
    user_count: int = 0,
    field_count: int = 0,
    area_hectares: float = 0.0,
    task_count: int = 0,
    alert_count: int = 0,
    ndvi_requests: int = 0,
    ai_queries: int = 0,
    storage_mb: float = 0.0,
    api_calls: int = 0,
):
    """Record tenant usage"""
    await tenant_service.record_usage(
        tenant_id=tenant_id,
        user_count=user_count,
        field_count=field_count,
        area_hectares=area_hectares,
        task_count=task_count,
        alert_count=alert_count,
        ndvi_requests=ndvi_requests,
        ai_queries=ai_queries,
        storage_mb=storage_mb,
        api_calls=api_calls,
    )
    return {"status": "recorded"}


@app.get("/api/v1/tenants/{tenant_id}/usage", response_model=List[UsageResponse])
async def get_usage_history(tenant_id: uuid.UUID, months: int = Query(12, ge=1, le=24)):
    """Get tenant usage history"""
    usage = await tenant_service.get_usage_history(tenant_id, months)
    return usage


# Invoices
@app.get("/api/v1/tenants/{tenant_id}/invoices", response_model=List[InvoiceResponse])
async def get_invoices(tenant_id: uuid.UUID):
    """Get tenant invoices"""
    invoices = await tenant_service.get_invoices(tenant_id)
    return invoices


# Status Management
@app.post("/api/v1/tenants/{tenant_id}/suspend", status_code=status.HTTP_204_NO_CONTENT)
async def suspend_tenant(tenant_id: uuid.UUID, reason: str = ""):
    """Suspend tenant"""
    await tenant_service.suspend_tenant(tenant_id, reason)


@app.post(
    "/api/v1/tenants/{tenant_id}/activate", status_code=status.HTTP_204_NO_CONTENT
)
async def activate_tenant(tenant_id: uuid.UUID):
    """Activate suspended tenant"""
    await tenant_service.activate_tenant(tenant_id)


# Pricing Plans
@app.get("/api/v1/pricing-plans", response_model=List[PricingPlanResponse])
async def get_pricing_plans():
    """Get all available pricing plans"""
    plans = await tenant_service.get_pricing_plans()
    return plans


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
