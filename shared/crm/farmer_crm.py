"""
SAHOOL Farmer CRM Module
========================
وحدة إدارة علاقات المزارعين

Inspired by CordysCRM's AI-powered CRM architecture:
- MCP Server for custom agents
- MaxKB for intelligent assistants
- SQLBot for natural language queries
- DataEase for BI dashboards

This module adapts CRM concepts for agricultural context.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class FarmerStatus(StrEnum):
    """Farmer engagement status."""

    LEAD = "lead"  # مهتم - Initial contact
    REGISTERED = "registered"  # مسجل - Completed registration
    ACTIVE = "active"  # نشط - Using platform
    PREMIUM = "premium"  # مميز - Premium subscriber
    CHURNED = "churned"  # متوقف - Stopped using


class DealStage(StrEnum):
    """Agricultural deal stages (harvest/supply)."""

    PROSPECTING = "prospecting"  # استكشاف - Identifying opportunity
    QUALIFICATION = "qualification"  # تأهيل - Assessing viability
    NEGOTIATION = "negotiation"  # تفاوض - Price/terms discussion
    CONTRACTED = "contracted"  # متعاقد - Agreement signed
    DELIVERED = "delivered"  # مسلم - Crop delivered
    PAID = "paid"  # مدفوع - Payment received
    CLOSED_LOST = "closed_lost"  # خسارة - Deal fell through


class InteractionType(StrEnum):
    """Types of farmer interactions."""

    ADVISORY = "advisory"  # استشارة
    SUPPORT = "support"  # دعم فني
    SALES = "sales"  # مبيعات
    TRAINING = "training"  # تدريب
    INSPECTION = "inspection"  # فحص ميداني


@dataclass
class Farmer:
    """
    Farmer entity (equivalent to Customer in CRM).
    كيان المزارع (مكافئ للعميل في CRM)
    """

    farmer_id: str
    name: str
    name_ar: str
    phone: str
    email: str | None = None

    # Location
    governorate: str | None = None
    district: str | None = None
    village: str | None = None
    coordinates: tuple[float, float] | None = None

    # Farm details
    total_area_ha: float = 0.0
    primary_crops: list[str] = field(default_factory=list)
    water_source: str | None = None
    irrigation_type: str | None = None

    # CRM fields
    status: FarmerStatus = FarmerStatus.LEAD
    source: str | None = None  # How they found us
    assigned_advisor: str | None = None

    # Engagement metrics
    last_interaction: datetime | None = None
    total_interactions: int = 0
    satisfaction_score: float | None = None

    # Financial
    lifetime_value: float = 0.0
    outstanding_balance: float = 0.0

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    tags: list[str] = field(default_factory=list)
    custom_fields: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "farmer_id": self.farmer_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "phone": self.phone,
            "status": self.status.value,
            "total_area_ha": self.total_area_ha,
            "primary_crops": self.primary_crops,
            "lifetime_value": self.lifetime_value,
        }


@dataclass
class HarvestDeal:
    """
    Harvest/Supply deal (equivalent to Opportunity in CRM).
    صفقة الحصاد/التوريد (مكافئ للفرصة في CRM)
    """

    deal_id: str
    farmer_id: str

    # Deal details
    title: str
    title_ar: str
    crop_type: str
    expected_quantity_tons: float
    expected_price_per_ton: float

    # Timing
    expected_harvest_date: datetime | None = None
    delivery_deadline: datetime | None = None

    # Stage tracking (CRM pipeline)
    stage: DealStage = DealStage.PROSPECTING
    probability: float = 0.1  # Win probability

    # Buyer info
    buyer_id: str | None = None
    buyer_name: str | None = None

    # Financials
    deal_value: float = 0.0
    actual_quantity: float | None = None
    actual_price: float | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    closed_at: datetime | None = None
    notes: str | None = None

    @property
    def expected_value(self) -> float:
        return self.expected_quantity_tons * self.expected_price_per_ton

    def to_dict(self) -> dict[str, Any]:
        return {
            "deal_id": self.deal_id,
            "farmer_id": self.farmer_id,
            "title": self.title,
            "crop_type": self.crop_type,
            "stage": self.stage.value,
            "expected_value": self.expected_value,
            "probability": self.probability,
        }


@dataclass
class Interaction:
    """
    Farmer interaction record (equivalent to Activity in CRM).
    سجل تفاعل المزارع (مكافئ للنشاط في CRM)
    """

    interaction_id: str
    farmer_id: str

    # Interaction details
    type: InteractionType
    subject: str
    subject_ar: str
    description: str | None = None

    # Participants
    advisor_id: str | None = None
    advisor_name: str | None = None

    # Timing
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    duration_minutes: int | None = None

    # Outcome
    outcome: str | None = None
    follow_up_required: bool = False
    follow_up_date: datetime | None = None

    # Related entities
    deal_id: str | None = None
    field_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "interaction_id": self.interaction_id,
            "farmer_id": self.farmer_id,
            "type": self.type.value,
            "subject": self.subject,
            "occurred_at": self.occurred_at.isoformat(),
        }


@dataclass
class SupplyContract:
    """
    Supply contract (equivalent to Contract in CRM).
    عقد التوريد (مكافئ للعقد في CRM)
    """

    contract_id: str
    deal_id: str
    farmer_id: str
    buyer_id: str

    # Contract terms
    title: str
    crop_type: str
    quantity_tons: float
    price_per_ton: float
    total_value: float

    # Dates
    start_date: datetime
    end_date: datetime
    delivery_dates: list[datetime] = field(default_factory=list)

    # Status
    status: str = "draft"  # draft, active, completed, cancelled
    signed_by_farmer: bool = False
    signed_by_buyer: bool = False

    # Quality requirements
    quality_grade: str | None = None
    moisture_max: float | None = None
    impurity_max: float | None = None

    # Payment terms
    payment_terms: str | None = None  # e.g., "50% advance, 50% on delivery"
    advance_payment: float = 0.0

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class Payment:
    """
    Payment record (equivalent to Payment in CRM).
    سجل الدفع (مكافئ للدفع في CRM)
    """

    payment_id: str
    contract_id: str
    farmer_id: str

    amount: float
    currency: str = "SAR"

    payment_type: str = "bank_transfer"  # bank_transfer, cash, mobile_wallet
    payment_date: datetime = field(default_factory=lambda: datetime.now(UTC))

    status: str = "pending"  # pending, completed, failed, refunded
    reference: str | None = None

    # For partial deliveries
    delivery_id: str | None = None
    quantity_paid_for: float | None = None


class FarmerCRMService:
    """
    Farmer CRM Service - Main service for farmer relationship management.
    خدمة إدارة علاقات المزارعين

    Inspired by CordysCRM, adapted for agricultural context.

    Features:
    - Farmer lifecycle management
    - Deal pipeline tracking
    - Interaction logging
    - Analytics and reporting

    Example:
        crm = FarmerCRMService(tenant_id="sahool")

        # Register new farmer
        farmer = await crm.create_farmer(
            name="أحمد محمد",
            phone="+966501234567",
            governorate="الرياض",
        )

        # Create harvest deal
        deal = await crm.create_deal(
            farmer_id=farmer.farmer_id,
            crop_type="wheat",
            expected_quantity=50,  # tons
            expected_price=1850,   # SAR/ton
        )

        # Log interaction
        await crm.log_interaction(
            farmer_id=farmer.farmer_id,
            type=InteractionType.ADVISORY,
            subject="Irrigation advice provided",
        )
    """

    def __init__(self, tenant_id: str = "sahool"):
        self.tenant_id = tenant_id
        # In production, these would be database-backed
        self._farmers: dict[str, Farmer] = {}
        self._deals: dict[str, HarvestDeal] = {}
        self._interactions: dict[str, Interaction] = {}
        self._contracts: dict[str, SupplyContract] = {}
        self._payments: dict[str, Payment] = {}

    async def create_farmer(
        self,
        name: str,
        phone: str,
        name_ar: str | None = None,
        **kwargs,
    ) -> Farmer:
        """Create a new farmer record."""
        farmer = Farmer(
            farmer_id=f"FRM-{uuid.uuid4().hex[:8].upper()}",
            name=name,
            name_ar=name_ar or name,
            phone=phone,
            **kwargs,
        )
        self._farmers[farmer.farmer_id] = farmer
        return farmer

    async def get_farmer(self, farmer_id: str) -> Farmer | None:
        """Get farmer by ID."""
        return self._farmers.get(farmer_id)

    async def update_farmer_status(
        self,
        farmer_id: str,
        status: FarmerStatus,
    ) -> Farmer | None:
        """Update farmer engagement status."""
        farmer = self._farmers.get(farmer_id)
        if farmer:
            farmer.status = status
            farmer.updated_at = datetime.now(UTC)
        return farmer

    async def create_deal(
        self,
        farmer_id: str,
        crop_type: str,
        expected_quantity: float,
        expected_price: float,
        title: str | None = None,
        **kwargs,
    ) -> HarvestDeal:
        """Create a new harvest deal."""
        deal = HarvestDeal(
            deal_id=f"DEAL-{uuid.uuid4().hex[:8].upper()}",
            farmer_id=farmer_id,
            title=title or f"{crop_type} Harvest Deal",
            title_ar=kwargs.pop("title_ar", f"صفقة حصاد {crop_type}"),
            crop_type=crop_type,
            expected_quantity_tons=expected_quantity,
            expected_price_per_ton=expected_price,
            deal_value=expected_quantity * expected_price,
            **kwargs,
        )
        self._deals[deal.deal_id] = deal
        return deal

    async def advance_deal_stage(
        self,
        deal_id: str,
        new_stage: DealStage,
    ) -> HarvestDeal | None:
        """Move deal to next stage in pipeline."""
        deal = self._deals.get(deal_id)
        if deal:
            deal.stage = new_stage
            # Update probability based on stage
            stage_probabilities = {
                DealStage.PROSPECTING: 0.1,
                DealStage.QUALIFICATION: 0.25,
                DealStage.NEGOTIATION: 0.5,
                DealStage.CONTRACTED: 0.75,
                DealStage.DELIVERED: 0.9,
                DealStage.PAID: 1.0,
                DealStage.CLOSED_LOST: 0.0,
            }
            deal.probability = stage_probabilities.get(new_stage, 0.5)

            if new_stage in (DealStage.PAID, DealStage.CLOSED_LOST):
                deal.closed_at = datetime.now(UTC)

        return deal

    async def log_interaction(
        self,
        farmer_id: str,
        type: InteractionType,
        subject: str,
        subject_ar: str | None = None,
        **kwargs,
    ) -> Interaction:
        """Log a farmer interaction."""
        interaction = Interaction(
            interaction_id=f"INT-{uuid.uuid4().hex[:8].upper()}",
            farmer_id=farmer_id,
            type=type,
            subject=subject,
            subject_ar=subject_ar or subject,
            **kwargs,
        )
        self._interactions[interaction.interaction_id] = interaction

        # Update farmer's last interaction
        farmer = self._farmers.get(farmer_id)
        if farmer:
            farmer.last_interaction = interaction.occurred_at
            farmer.total_interactions += 1

        return interaction

    async def get_pipeline_summary(self) -> dict[str, Any]:
        """Get deal pipeline summary for dashboard."""
        pipeline = {stage.value: {"count": 0, "value": 0.0} for stage in DealStage}

        for deal in self._deals.values():
            pipeline[deal.stage.value]["count"] += 1
            pipeline[deal.stage.value]["value"] += deal.expected_value

        return {
            "pipeline": pipeline,
            "total_deals": len(self._deals),
            "total_value": sum(d.expected_value for d in self._deals.values()),
            "weighted_value": sum(d.expected_value * d.probability for d in self._deals.values()),
        }

    async def get_farmer_analytics(self, farmer_id: str) -> dict[str, Any]:
        """Get analytics for a specific farmer."""
        farmer = self._farmers.get(farmer_id)
        if not farmer:
            return {}

        farmer_deals = [d for d in self._deals.values() if d.farmer_id == farmer_id]
        farmer_interactions = [i for i in self._interactions.values() if i.farmer_id == farmer_id]

        return {
            "farmer": farmer.to_dict(),
            "deals": {
                "total": len(farmer_deals),
                "active": len([d for d in farmer_deals if d.stage not in (DealStage.PAID, DealStage.CLOSED_LOST)]),
                "won": len([d for d in farmer_deals if d.stage == DealStage.PAID]),
                "total_value": sum(d.expected_value for d in farmer_deals),
            },
            "interactions": {
                "total": len(farmer_interactions),
                "by_type": {t.value: len([i for i in farmer_interactions if i.type == t]) for t in InteractionType},
            },
            "engagement_score": self._calculate_engagement_score(farmer, farmer_deals, farmer_interactions),
        }

    def _calculate_engagement_score(
        self,
        farmer: Farmer,
        deals: list[HarvestDeal],
        interactions: list[Interaction],
    ) -> float:
        """Calculate farmer engagement score (0-100)."""
        score = 0.0

        # Recency of last interaction (max 30 points)
        if farmer.last_interaction:
            days_since = (datetime.now(UTC) - farmer.last_interaction).days
            if days_since <= 7:
                score += 30
            elif days_since <= 30:
                score += 20
            elif days_since <= 90:
                score += 10

        # Number of interactions (max 25 points)
        score += min(25, len(interactions) * 5)

        # Active deals (max 25 points)
        active_deals = [d for d in deals if d.stage not in (DealStage.PAID, DealStage.CLOSED_LOST)]
        score += min(25, len(active_deals) * 10)

        # Profile completeness (max 20 points)
        if farmer.email:
            score += 5
        if farmer.coordinates:
            score += 5
        if farmer.primary_crops:
            score += 5
        if farmer.total_area_ha > 0:
            score += 5

        return min(100, score)


# Natural Language Query Interface (inspired by SQLBot)
class FarmerQueryBot:
    """
    Natural language query interface for farmer data.
    واجهة استعلام باللغة الطبيعية لبيانات المزارعين

    Inspired by CordysCRM's SQLBot feature.

    Example:
        bot = FarmerQueryBot(crm_service)

        result = await bot.query("كم عدد المزارعين النشطين؟")
        result = await bot.query("Show me wheat deals this month")
        result = await bot.query("Who are the top 5 farmers by value?")
    """

    # Query patterns (simplified - would use LLM in production)
    QUERY_PATTERNS = {
        "farmer_count": ["كم عدد", "how many farmers", "عدد المزارعين"],
        "active_farmers": ["نشط", "active", "المزارعين النشطين"],
        "deals_by_crop": ["صفقات", "deals", "محصول"],
        "top_farmers": ["أعلى", "top", "الأفضل"],
        "pipeline": ["خط الأنابيب", "pipeline", "مراحل"],
    }

    def __init__(self, crm_service: FarmerCRMService):
        self.crm = crm_service

    async def query(self, natural_query: str) -> dict[str, Any]:
        """Process natural language query."""
        query_lower = natural_query.lower()

        # Detect query type
        if any(p in query_lower for p in self.QUERY_PATTERNS["farmer_count"]):
            return await self._count_farmers(query_lower)

        elif any(p in query_lower for p in self.QUERY_PATTERNS["pipeline"]):
            return await self.crm.get_pipeline_summary()

        elif any(p in query_lower for p in self.QUERY_PATTERNS["top_farmers"]):
            return await self._top_farmers()

        else:
            return {
                "error": "Query not understood",
                "error_ar": "لم يتم فهم الاستعلام",
                "suggestion": "Try: 'How many active farmers?' or 'Show pipeline'",
            }

    async def _count_farmers(self, query: str) -> dict[str, Any]:
        """Count farmers with optional status filter."""
        farmers = list(self.crm._farmers.values())

        if "نشط" in query or "active" in query:
            farmers = [f for f in farmers if f.status == FarmerStatus.ACTIVE]
            status = "active"
        elif "premium" in query or "مميز" in query:
            farmers = [f for f in farmers if f.status == FarmerStatus.PREMIUM]
            status = "premium"
        else:
            status = "all"

        return {
            "query_type": "farmer_count",
            "status_filter": status,
            "count": len(farmers),
            "answer": f"عدد المزارعين ({status}): {len(farmers)}",
            "answer_en": f"Number of farmers ({status}): {len(farmers)}",
        }

    async def _top_farmers(self, limit: int = 5) -> dict[str, Any]:
        """Get top farmers by lifetime value."""
        farmers = sorted(
            self.crm._farmers.values(),
            key=lambda f: f.lifetime_value,
            reverse=True,
        )[:limit]

        return {
            "query_type": "top_farmers",
            "limit": limit,
            "farmers": [f.to_dict() for f in farmers],
            "answer_ar": f"أعلى {limit} مزارعين من حيث القيمة",
        }
