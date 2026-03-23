"""
SAHOOL Cooperatives Module - Revenue Sharing & Accounting
==========================================================
توزيع الايرادات والمحاسبة

Revenue sharing and financial management for cooperatives including:
- Revenue distribution calculations
- Multiple sharing methods (equal, contribution-based, production-based)
- Financial period management
- Member payment tracking
- Reserve fund management
- Audit trail and reporting

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum
from typing import Any

from .models import (
    CooperativeMember,
    MemberStatus,
    RevenueShareMethod,
)


class TransactionType(StrEnum):
    """Types of financial transactions | انواع المعاملات المالية"""

    REVENUE = "revenue"  # ايراد - Income received
    EXPENSE = "expense"  # مصروف - Cost paid
    DISTRIBUTION = "distribution"  # توزيع - Member payout
    MEMBERSHIP_FEE = "membership_fee"  # رسوم عضوية
    ANNUAL_DUES = "annual_dues"  # اشتراك سنوي
    RESOURCE_FEE = "resource_fee"  # رسوم استخدام موارد
    RESERVE_TRANSFER = "reserve_transfer"  # تحويل للاحتياطي
    LOAN = "loan"  # قرض
    LOAN_REPAYMENT = "loan_repayment"  # سداد قرض
    ADJUSTMENT = "adjustment"  # تعديل


class PeriodStatus(StrEnum):
    """Financial period status | حالة الفترة المالية"""

    OPEN = "open"  # مفتوحة - Accepting transactions
    CALCULATING = "calculating"  # قيد الحساب - Distribution in progress
    DISTRIBUTED = "distributed"  # تم التوزيع
    CLOSED = "closed"  # مغلقة - Finalized


class PaymentStatus(StrEnum):
    """Payment status | حالة الدفع"""

    PENDING = "pending"  # معلق
    APPROVED = "approved"  # معتمد
    PAID = "paid"  # مدفوع
    FAILED = "failed"  # فشل
    CANCELLED = "cancelled"  # ملغي


@dataclass
class FinancialPeriod:
    """
    Financial accounting period for a cooperative.
    الفترة المحاسبية المالية للتعاونية
    """

    # Identification
    period_id: str
    cooperative_id: str

    # Period details
    name: str
    name_ar: str
    start_date: datetime
    end_date: datetime

    # Status
    status: PeriodStatus = PeriodStatus.OPEN

    # Totals (calculated)
    total_revenue: Decimal = Decimal("0")
    total_expenses: Decimal = Decimal("0")
    net_income: Decimal = Decimal("0")

    # Distribution amounts
    management_fee: Decimal = Decimal("0")
    reserve_fund_amount: Decimal = Decimal("0")
    distributable_amount: Decimal = Decimal("0")
    total_distributed: Decimal = Decimal("0")

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    closed_at: datetime | None = None
    notes: str | None = None

    @classmethod
    def create(
        cls,
        cooperative_id: str,
        name: str,
        name_ar: str,
        start_date: datetime,
        end_date: datetime,
        **kwargs,
    ) -> FinancialPeriod:
        """Factory method to create a new financial period"""
        return cls(
            period_id=f"FP-{uuid.uuid4().hex[:8].upper()}",
            cooperative_id=cooperative_id,
            name=name,
            name_ar=name_ar,
            start_date=start_date,
            end_date=end_date,
            **kwargs,
        )

    def calculate_net_income(self) -> Decimal:
        """Calculate net income for the period"""
        self.net_income = self.total_revenue - self.total_expenses
        return self.net_income

    def to_dict(self) -> dict[str, Any]:
        return {
            "period_id": self.period_id,
            "cooperative_id": self.cooperative_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "status": self.status.value,
            "total_revenue": str(self.total_revenue),
            "total_expenses": str(self.total_expenses),
            "net_income": str(self.net_income),
            "management_fee": str(self.management_fee),
            "reserve_fund_amount": str(self.reserve_fund_amount),
            "distributable_amount": str(self.distributable_amount),
            "total_distributed": str(self.total_distributed),
            "created_at": self.created_at.isoformat(),
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
        }


@dataclass
class Transaction:
    """
    Financial transaction record.
    سجل المعاملة المالية
    """

    # Identification
    transaction_id: str
    cooperative_id: str

    # Transaction details (required fields)
    type: TransactionType
    description: str
    description_ar: str

    # Optional fields
    period_id: str | None = None
    amount: Decimal = Decimal("0")
    currency: str = "SAR"

    # Related entities
    member_id: str | None = None  # If member-related
    category: str | None = None  # Revenue/expense category
    reference: str | None = None  # External reference

    # Source of funds
    source: str | None = None  # crop_sales, services, grants, etc.
    source_ar: str | None = None

    # Timing
    transaction_date: datetime = field(default_factory=lambda: datetime.now(UTC))
    effective_date: datetime | None = None

    # Status
    status: str = "completed"  # pending, completed, reversed

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str | None = None
    notes: str | None = None
    attachments: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        cooperative_id: str,
        type: TransactionType,
        description: str,
        description_ar: str,
        amount: Decimal,
        **kwargs,
    ) -> Transaction:
        """Factory method to create a transaction"""
        return cls(
            transaction_id=f"TXN-{uuid.uuid4().hex[:8].upper()}",
            cooperative_id=cooperative_id,
            type=type,
            description=description,
            description_ar=description_ar,
            amount=amount,
            **kwargs,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "cooperative_id": self.cooperative_id,
            "period_id": self.period_id,
            "type": self.type.value,
            "description": self.description,
            "description_ar": self.description_ar,
            "amount": str(self.amount),
            "currency": self.currency,
            "member_id": self.member_id,
            "category": self.category,
            "source": self.source,
            "source_ar": self.source_ar,
            "transaction_date": self.transaction_date.isoformat(),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class MemberShare:
    """
    Calculated share for a member in a distribution.
    الحصة المحسوبة للعضو في التوزيع
    """

    member_id: str
    member_name: str
    member_name_ar: str

    # Contribution metrics
    share_count: int = 0
    land_area_ha: float = 0.0
    production_volume: float = 0.0
    contribution_percent: Decimal = Decimal("0")

    # Calculated amounts
    base_share: Decimal = Decimal("0")
    bonus_share: Decimal = Decimal("0")
    deductions: Decimal = Decimal("0")
    net_share: Decimal = Decimal("0")

    # Breakdown
    share_breakdown: dict[str, Decimal] = field(default_factory=dict)
    deduction_breakdown: dict[str, Decimal] = field(default_factory=dict)

    def calculate_net(self) -> Decimal:
        """Calculate net share after deductions"""
        self.net_share = self.base_share + self.bonus_share - self.deductions
        return self.net_share

    def to_dict(self) -> dict[str, Any]:
        return {
            "member_id": self.member_id,
            "member_name": self.member_name,
            "member_name_ar": self.member_name_ar,
            "share_count": self.share_count,
            "land_area_ha": self.land_area_ha,
            "production_volume": self.production_volume,
            "contribution_percent": str(self.contribution_percent),
            "base_share": str(self.base_share),
            "bonus_share": str(self.bonus_share),
            "deductions": str(self.deductions),
            "net_share": str(self.net_share),
            "share_breakdown": {k: str(v) for k, v in self.share_breakdown.items()},
            "deduction_breakdown": {k: str(v) for k, v in self.deduction_breakdown.items()},
        }


@dataclass
class DistributionPlan:
    """
    Plan for distributing revenue to members.
    خطة توزيع الايرادات على الاعضاء
    """

    # Identification
    plan_id: str
    cooperative_id: str
    period_id: str

    # Distribution configuration
    method: RevenueShareMethod
    total_amount: Decimal = Decimal("0")
    currency: str = "SAR"

    # Deductions
    management_fee_percent: Decimal = Decimal("5.0")
    management_fee_amount: Decimal = Decimal("0")
    reserve_fund_percent: Decimal = Decimal("10.0")
    reserve_fund_amount: Decimal = Decimal("0")
    other_deductions: Decimal = Decimal("0")
    distributable_amount: Decimal = Decimal("0")

    # Member shares
    member_shares: list[MemberShare] = field(default_factory=list)
    total_shares_count: int = 0
    total_land_area: float = 0.0
    total_production: float = 0.0

    # Status
    status: str = "draft"  # draft, approved, executing, completed
    approved_by: str | None = None
    approved_at: datetime | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    notes: str | None = None
    notes_ar: str | None = None

    @classmethod
    def create(
        cls,
        cooperative_id: str,
        period_id: str,
        method: RevenueShareMethod,
        total_amount: Decimal,
        **kwargs,
    ) -> DistributionPlan:
        """Factory method to create a distribution plan"""
        return cls(
            plan_id=f"DIST-{uuid.uuid4().hex[:8].upper()}",
            cooperative_id=cooperative_id,
            period_id=period_id,
            method=method,
            total_amount=total_amount,
            **kwargs,
        )

    def calculate_distributable(self) -> Decimal:
        """Calculate amount available for distribution after deductions"""
        self.management_fee_amount = (self.total_amount * self.management_fee_percent / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        self.reserve_fund_amount = (self.total_amount * self.reserve_fund_percent / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        self.distributable_amount = (
            self.total_amount - self.management_fee_amount - self.reserve_fund_amount - self.other_deductions
        )

        return self.distributable_amount

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "cooperative_id": self.cooperative_id,
            "period_id": self.period_id,
            "method": self.method.value,
            "total_amount": str(self.total_amount),
            "currency": self.currency,
            "management_fee_percent": str(self.management_fee_percent),
            "management_fee_amount": str(self.management_fee_amount),
            "reserve_fund_percent": str(self.reserve_fund_percent),
            "reserve_fund_amount": str(self.reserve_fund_amount),
            "other_deductions": str(self.other_deductions),
            "distributable_amount": str(self.distributable_amount),
            "member_count": len(self.member_shares),
            "total_shares_count": self.total_shares_count,
            "total_land_area": self.total_land_area,
            "total_production": self.total_production,
            "status": self.status,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "created_at": self.created_at.isoformat(),
            "member_shares": [s.to_dict() for s in self.member_shares],
        }

    def to_summary(self) -> dict[str, Any]:
        """Compact summary for display"""
        return {
            "plan_id": self.plan_id,
            "method": self.method.value,
            "total_amount": str(self.total_amount),
            "distributable_amount": str(self.distributable_amount),
            "member_count": len(self.member_shares),
            "status": self.status,
        }


@dataclass
class MemberPayment:
    """
    Payment record for a member distribution.
    سجل دفع توزيع العضو
    """

    # Identification
    payment_id: str
    plan_id: str
    member_id: str
    cooperative_id: str

    # Amount
    amount: Decimal = Decimal("0")
    currency: str = "SAR"

    # Payment details
    payment_method: str = "bank_transfer"  # bank_transfer, cash, mobile_wallet
    payment_date: datetime | None = None
    reference: str | None = None

    # Bank details (if bank transfer)
    bank_name: str | None = None
    account_number: str | None = None
    iban: str | None = None

    # Status
    status: PaymentStatus = PaymentStatus.PENDING

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    processed_by: str | None = None
    notes: str | None = None

    @classmethod
    def create(
        cls,
        plan_id: str,
        member_id: str,
        cooperative_id: str,
        amount: Decimal,
        **kwargs,
    ) -> MemberPayment:
        """Factory method to create a payment record"""
        return cls(
            payment_id=f"PAY-{uuid.uuid4().hex[:8].upper()}",
            plan_id=plan_id,
            member_id=member_id,
            cooperative_id=cooperative_id,
            amount=amount,
            **kwargs,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "payment_id": self.payment_id,
            "plan_id": self.plan_id,
            "member_id": self.member_id,
            "cooperative_id": self.cooperative_id,
            "amount": str(self.amount),
            "currency": self.currency,
            "payment_method": self.payment_method,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "reference": self.reference,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
        }


class RevenueShareCalculator:
    """
    Calculator for different revenue sharing methods.
    حاسب لطرق توزيع الايرادات المختلفة

    Supports multiple distribution methods:
    - EQUAL: Equal distribution among all members
    - CONTRIBUTION: Based on financial contribution (share value)
    - PRODUCTION: Based on production volume
    - LAND_AREA: Based on contributed land area
    - WEIGHTED: Custom weights per member
    - HYBRID: Combination of methods

    Example:
        calculator = RevenueShareCalculator()

        # Calculate by contribution
        shares = calculator.calculate_by_contribution(
            total_amount=Decimal("100000"),
            members=members,
        )

        # Calculate hybrid (50% equal, 50% production)
        shares = calculator.calculate_hybrid(
            total_amount=Decimal("100000"),
            members=members,
            weights={"equal": 0.5, "production": 0.5},
        )
    """

    def calculate(
        self,
        method: RevenueShareMethod,
        total_amount: Decimal,
        members: list[CooperativeMember],
        production_data: dict[str, float] | None = None,
        custom_weights: dict[str, Decimal] | None = None,
        hybrid_weights: dict[str, float] | None = None,
    ) -> list[MemberShare]:
        """
        Calculate member shares based on the specified method.
        حساب حصص الاعضاء بناء على الطريقة المحددة

        Args:
            method: Distribution method to use
            total_amount: Total amount to distribute
            members: List of cooperative members
            production_data: Dict of member_id -> production volume (for PRODUCTION method)
            custom_weights: Dict of member_id -> weight (for WEIGHTED method)
            hybrid_weights: Dict of method -> weight (for HYBRID method)

        Returns:
            List of MemberShare objects
        """
        # Filter active members
        active_members = [m for m in members if m.status == MemberStatus.ACTIVE]

        if not active_members:
            return []

        if method == RevenueShareMethod.EQUAL:
            return self.calculate_equal(total_amount, active_members)
        elif method == RevenueShareMethod.CONTRIBUTION:
            return self.calculate_by_contribution(total_amount, active_members)
        elif method == RevenueShareMethod.PRODUCTION:
            return self.calculate_by_production(total_amount, active_members, production_data or {})
        elif method == RevenueShareMethod.LAND_AREA:
            return self.calculate_by_land_area(total_amount, active_members)
        elif method == RevenueShareMethod.WEIGHTED:
            return self.calculate_weighted(total_amount, active_members, custom_weights or {})
        elif method == RevenueShareMethod.HYBRID:
            return self.calculate_hybrid(total_amount, active_members, hybrid_weights or {}, production_data or {})
        else:
            raise ValueError(f"Unknown distribution method: {method}")

    def calculate_equal(
        self,
        total_amount: Decimal,
        members: list[CooperativeMember],
    ) -> list[MemberShare]:
        """
        Calculate equal shares for all members.
        حساب حصص متساوية لجميع الاعضاء
        """
        if not members:
            return []

        share_amount = (total_amount / len(members)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        shares = []
        for member in members:
            share = MemberShare(
                member_id=member.member_id,
                member_name=member.name,
                member_name_ar=member.name_ar,
                share_count=member.share_count,
                land_area_ha=member.land_area_ha,
                contribution_percent=Decimal("100") / len(members),
                base_share=share_amount,
                net_share=share_amount,
                share_breakdown={"equal_share": share_amount},
            )
            shares.append(share)

        # Handle rounding remainder
        distributed = sum(s.net_share for s in shares)
        remainder = total_amount - distributed
        if remainder != Decimal("0") and shares:
            shares[0].net_share += remainder
            shares[0].base_share += remainder

        return shares

    def calculate_by_contribution(
        self,
        total_amount: Decimal,
        members: list[CooperativeMember],
    ) -> list[MemberShare]:
        """
        Calculate shares based on financial contribution (share value).
        حساب الحصص بناء على المساهمة المالية (قيمة الاسهم)
        """
        if not members:
            return []

        total_contribution = sum(m.share_value for m in members)

        if total_contribution == Decimal("0"):
            # Fall back to equal distribution
            return self.calculate_equal(total_amount, members)

        shares = []
        for member in members:
            contribution_percent = (member.share_value / total_contribution * Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            share_amount = (total_amount * member.share_value / total_contribution).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            share = MemberShare(
                member_id=member.member_id,
                member_name=member.name,
                member_name_ar=member.name_ar,
                share_count=member.share_count,
                land_area_ha=member.land_area_ha,
                contribution_percent=contribution_percent,
                base_share=share_amount,
                net_share=share_amount,
                share_breakdown={
                    "contribution_share": share_amount,
                    "share_value": member.share_value,
                },
            )
            shares.append(share)

        # Handle rounding remainder
        self._adjust_for_remainder(shares, total_amount)

        return shares

    def calculate_by_production(
        self,
        total_amount: Decimal,
        members: list[CooperativeMember],
        production_data: dict[str, float],
    ) -> list[MemberShare]:
        """
        Calculate shares based on production volume.
        حساب الحصص بناء على حجم الانتاج
        """
        if not members:
            return []

        # Get production for each member
        member_production = {m.member_id: production_data.get(m.member_id, 0.0) for m in members}
        total_production = sum(member_production.values())

        if total_production == 0:
            # Fall back to equal distribution
            return self.calculate_equal(total_amount, members)

        shares = []
        for member in members:
            production = member_production.get(member.member_id, 0.0)
            contribution_percent = Decimal(str(production / total_production * 100)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            share_amount = (total_amount * Decimal(str(production / total_production))).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            share = MemberShare(
                member_id=member.member_id,
                member_name=member.name,
                member_name_ar=member.name_ar,
                share_count=member.share_count,
                land_area_ha=member.land_area_ha,
                production_volume=production,
                contribution_percent=contribution_percent,
                base_share=share_amount,
                net_share=share_amount,
                share_breakdown={
                    "production_share": share_amount,
                    "production_volume": Decimal(str(production)),
                },
            )
            shares.append(share)

        self._adjust_for_remainder(shares, total_amount)

        return shares

    def calculate_by_land_area(
        self,
        total_amount: Decimal,
        members: list[CooperativeMember],
    ) -> list[MemberShare]:
        """
        Calculate shares based on contributed land area.
        حساب الحصص بناء على مساحة الارض المساهمة
        """
        if not members:
            return []

        total_area = sum(m.land_area_ha for m in members)

        if total_area == 0:
            # Fall back to equal distribution
            return self.calculate_equal(total_amount, members)

        shares = []
        for member in members:
            contribution_percent = Decimal(str(member.land_area_ha / total_area * 100)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            share_amount = (total_amount * Decimal(str(member.land_area_ha / total_area))).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            share = MemberShare(
                member_id=member.member_id,
                member_name=member.name,
                member_name_ar=member.name_ar,
                share_count=member.share_count,
                land_area_ha=member.land_area_ha,
                contribution_percent=contribution_percent,
                base_share=share_amount,
                net_share=share_amount,
                share_breakdown={
                    "land_area_share": share_amount,
                    "land_area_ha": Decimal(str(member.land_area_ha)),
                },
            )
            shares.append(share)

        self._adjust_for_remainder(shares, total_amount)

        return shares

    def calculate_weighted(
        self,
        total_amount: Decimal,
        members: list[CooperativeMember],
        custom_weights: dict[str, Decimal],
    ) -> list[MemberShare]:
        """
        Calculate shares based on custom weights.
        حساب الحصص بناء على اوزان مخصصة
        """
        if not members:
            return []

        # Get weights, defaulting to equal weight for unspecified members
        member_weights = {}
        for member in members:
            weight = custom_weights.get(member.member_id, Decimal("1"))
            member_weights[member.member_id] = weight

        total_weight = sum(member_weights.values())

        if total_weight == Decimal("0"):
            return self.calculate_equal(total_amount, members)

        shares = []
        for member in members:
            weight = member_weights[member.member_id]
            contribution_percent = (weight / total_weight * Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            share_amount = (total_amount * weight / total_weight).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            share = MemberShare(
                member_id=member.member_id,
                member_name=member.name,
                member_name_ar=member.name_ar,
                share_count=member.share_count,
                land_area_ha=member.land_area_ha,
                contribution_percent=contribution_percent,
                base_share=share_amount,
                net_share=share_amount,
                share_breakdown={
                    "weighted_share": share_amount,
                    "weight": weight,
                },
            )
            shares.append(share)

        self._adjust_for_remainder(shares, total_amount)

        return shares

    def calculate_hybrid(
        self,
        total_amount: Decimal,
        members: list[CooperativeMember],
        method_weights: dict[str, float],
        production_data: dict[str, float],
    ) -> list[MemberShare]:
        """
        Calculate shares using multiple methods combined.
        حساب الحصص باستخدام طرق متعددة مجتمعة

        Args:
            total_amount: Total to distribute
            members: List of members
            method_weights: Dict of method -> weight (e.g., {"equal": 0.3, "production": 0.7})
            production_data: Production data for PRODUCTION method

        Example:
            shares = calculator.calculate_hybrid(
                total_amount=Decimal("100000"),
                members=members,
                method_weights={"equal": 0.3, "contribution": 0.3, "production": 0.4},
                production_data=production_data,
            )
        """
        if not members:
            return []

        # Normalize weights
        total_weight = sum(method_weights.values())
        if total_weight == 0:
            return self.calculate_equal(total_amount, members)

        normalized_weights = {k: v / total_weight for k, v in method_weights.items()}

        # Calculate shares for each method
        method_shares: dict[str, list[MemberShare]] = {}

        if "equal" in normalized_weights and normalized_weights["equal"] > 0:
            portion = total_amount * Decimal(str(normalized_weights["equal"]))
            method_shares["equal"] = self.calculate_equal(portion, members)

        if "contribution" in normalized_weights and normalized_weights["contribution"] > 0:
            portion = total_amount * Decimal(str(normalized_weights["contribution"]))
            method_shares["contribution"] = self.calculate_by_contribution(portion, members)

        if "production" in normalized_weights and normalized_weights["production"] > 0:
            portion = total_amount * Decimal(str(normalized_weights["production"]))
            method_shares["production"] = self.calculate_by_production(portion, members, production_data)

        if "land_area" in normalized_weights and normalized_weights["land_area"] > 0:
            portion = total_amount * Decimal(str(normalized_weights["land_area"]))
            method_shares["land_area"] = self.calculate_by_land_area(portion, members)

        # Combine shares for each member
        combined_shares = []
        for member in members:
            breakdown = {}
            total_share = Decimal("0")

            for method_name, shares in method_shares.items():
                member_share = next((s for s in shares if s.member_id == member.member_id), None)
                if member_share:
                    breakdown[f"{method_name}_share"] = member_share.net_share
                    total_share += member_share.net_share

            share = MemberShare(
                member_id=member.member_id,
                member_name=member.name,
                member_name_ar=member.name_ar,
                share_count=member.share_count,
                land_area_ha=member.land_area_ha,
                base_share=total_share,
                net_share=total_share,
                share_breakdown=breakdown,
            )
            combined_shares.append(share)

        self._adjust_for_remainder(combined_shares, total_amount)

        return combined_shares

    def _adjust_for_remainder(
        self,
        shares: list[MemberShare],
        total_amount: Decimal,
    ) -> None:
        """Adjust for rounding remainder"""
        distributed = sum(s.net_share for s in shares)
        remainder = total_amount - distributed

        if remainder != Decimal("0") and shares:
            # Add remainder to the member with highest contribution
            largest = max(shares, key=lambda s: s.net_share)
            largest.net_share += remainder
            largest.base_share += remainder


class RevenueService:
    """
    Service for managing cooperative revenue and distributions.
    خدمة ادارة ايرادات وتوزيعات التعاونية

    Features:
    - Financial period management
    - Transaction recording
    - Distribution planning and execution
    - Member payment processing
    - Financial reporting

    Example:
        service = RevenueService(cooperative_id="COOP-001")

        # Create financial period
        period = await service.create_period(
            name="Winter Season 2025-26",
            name_ar="موسم الشتاء 2025-26",
            start_date=datetime(2025, 10, 1),
            end_date=datetime(2026, 3, 31),
        )

        # Record revenue
        await service.record_revenue(
            period_id=period.period_id,
            amount=Decimal("500000"),
            description="Wheat sales",
            description_ar="مبيعات القمح",
            source="crop_sales",
        )

        # Create distribution plan
        plan = await service.create_distribution_plan(
            period_id=period.period_id,
            method=RevenueShareMethod.PRODUCTION,
            members=members,
            production_data=production_data,
        )

        # Execute distribution
        await service.execute_distribution(plan.plan_id)
    """

    def __init__(self, cooperative_id: str):
        self.cooperative_id = cooperative_id
        self.calculator = RevenueShareCalculator()

        # In-memory storage (production would use database)
        self._periods: dict[str, FinancialPeriod] = {}
        self._transactions: dict[str, Transaction] = {}
        self._plans: dict[str, DistributionPlan] = {}
        self._payments: dict[str, MemberPayment] = {}

        # Configuration
        self._default_management_fee = Decimal("5.0")
        self._default_reserve_fund = Decimal("10.0")

    # ===== Period Management =====

    async def create_period(
        self,
        name: str,
        name_ar: str,
        start_date: datetime,
        end_date: datetime,
        **kwargs,
    ) -> FinancialPeriod:
        """
        Create a new financial period.
        انشاء فترة مالية جديدة
        """
        period = FinancialPeriod.create(
            cooperative_id=self.cooperative_id,
            name=name,
            name_ar=name_ar,
            start_date=start_date,
            end_date=end_date,
            **kwargs,
        )
        self._periods[period.period_id] = period
        return period

    async def get_period(self, period_id: str) -> FinancialPeriod | None:
        """Get period by ID"""
        return self._periods.get(period_id)

    async def get_current_period(self) -> FinancialPeriod | None:
        """Get the current open period"""
        now = datetime.now(UTC)
        for period in self._periods.values():
            if period.status == PeriodStatus.OPEN and period.start_date <= now <= period.end_date:
                return period
        return None

    async def close_period(self, period_id: str) -> FinancialPeriod | None:
        """Close a financial period"""
        period = self._periods.get(period_id)
        if not period:
            return None

        period.status = PeriodStatus.CLOSED
        period.closed_at = datetime.now(UTC)
        return period

    # ===== Transactions =====

    async def record_revenue(
        self,
        period_id: str,
        amount: Decimal,
        description: str,
        description_ar: str,
        source: str | None = None,
        source_ar: str | None = None,
        **kwargs,
    ) -> Transaction:
        """
        Record revenue transaction.
        تسجيل معاملة ايراد
        """
        period = self._periods.get(period_id)
        if period and period.status != PeriodStatus.OPEN:
            raise ValueError(f"Period {period_id} is not open for transactions")

        txn = Transaction.create(
            cooperative_id=self.cooperative_id,
            type=TransactionType.REVENUE,
            description=description,
            description_ar=description_ar,
            amount=amount,
            period_id=period_id,
            source=source,
            source_ar=source_ar,
            **kwargs,
        )
        self._transactions[txn.transaction_id] = txn

        # Update period totals
        if period:
            period.total_revenue += amount
            period.calculate_net_income()

        return txn

    async def record_expense(
        self,
        period_id: str,
        amount: Decimal,
        description: str,
        description_ar: str,
        category: str | None = None,
        **kwargs,
    ) -> Transaction:
        """
        Record expense transaction.
        تسجيل معاملة مصروف
        """
        period = self._periods.get(period_id)
        if period and period.status != PeriodStatus.OPEN:
            raise ValueError(f"Period {period_id} is not open for transactions")

        txn = Transaction.create(
            cooperative_id=self.cooperative_id,
            type=TransactionType.EXPENSE,
            description=description,
            description_ar=description_ar,
            amount=amount,
            period_id=period_id,
            category=category,
            **kwargs,
        )
        self._transactions[txn.transaction_id] = txn

        # Update period totals
        if period:
            period.total_expenses += amount
            period.calculate_net_income()

        return txn

    async def list_transactions(
        self,
        period_id: str | None = None,
        type: TransactionType | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[Transaction]:
        """List transactions with filters"""
        transactions = list(self._transactions.values())

        if period_id:
            transactions = [t for t in transactions if t.period_id == period_id]

        if type:
            transactions = [t for t in transactions if t.type == type]

        if from_date:
            transactions = [t for t in transactions if t.transaction_date >= from_date]

        if to_date:
            transactions = [t for t in transactions if t.transaction_date <= to_date]

        return sorted(transactions, key=lambda t: t.transaction_date, reverse=True)

    # ===== Distribution =====

    async def create_distribution_plan(
        self,
        period_id: str,
        method: RevenueShareMethod,
        members: list[CooperativeMember],
        production_data: dict[str, float] | None = None,
        custom_weights: dict[str, Decimal] | None = None,
        hybrid_weights: dict[str, float] | None = None,
        management_fee_percent: Decimal | None = None,
        reserve_fund_percent: Decimal | None = None,
    ) -> DistributionPlan:
        """
        Create a distribution plan for a period.
        انشاء خطة توزيع لفترة مالية

        Args:
            period_id: Financial period ID
            method: Distribution method
            members: List of cooperative members
            production_data: Production data for PRODUCTION method
            custom_weights: Custom weights for WEIGHTED method
            hybrid_weights: Method weights for HYBRID method
            management_fee_percent: Override default management fee
            reserve_fund_percent: Override default reserve fund percent

        Returns:
            DistributionPlan with calculated member shares
        """
        period = self._periods.get(period_id)
        if not period:
            raise ValueError(f"Period {period_id} not found")

        # Create plan
        plan = DistributionPlan.create(
            cooperative_id=self.cooperative_id,
            period_id=period_id,
            method=method,
            total_amount=period.net_income,
            management_fee_percent=management_fee_percent or self._default_management_fee,
            reserve_fund_percent=reserve_fund_percent or self._default_reserve_fund,
        )

        # Calculate distributable amount
        plan.calculate_distributable()

        # Calculate member shares
        plan.member_shares = self.calculator.calculate(
            method=method,
            total_amount=plan.distributable_amount,
            members=members,
            production_data=production_data,
            custom_weights=custom_weights,
            hybrid_weights=hybrid_weights,
        )

        # Update plan totals
        plan.total_shares_count = sum(m.share_count for m in members)
        plan.total_land_area = sum(m.land_area_ha for m in members)
        plan.total_production = sum(production_data.values()) if production_data else 0.0

        self._plans[plan.plan_id] = plan

        return plan

    async def get_distribution_plan(self, plan_id: str) -> DistributionPlan | None:
        """Get distribution plan by ID"""
        return self._plans.get(plan_id)

    async def approve_distribution(
        self,
        plan_id: str,
        approved_by: str,
    ) -> DistributionPlan | None:
        """Approve a distribution plan"""
        plan = self._plans.get(plan_id)
        if not plan:
            return None

        plan.status = "approved"
        plan.approved_by = approved_by
        plan.approved_at = datetime.now(UTC)

        return plan

    async def execute_distribution(
        self,
        plan_id: str,
    ) -> list[MemberPayment]:
        """
        Execute distribution - create payment records for all members.
        تنفيذ التوزيع - انشاء سجلات دفع لجميع الاعضاء
        """
        plan = self._plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        if plan.status != "approved":
            raise ValueError(f"Plan must be approved before execution. Current status: {plan.status}")

        plan.status = "executing"

        payments = []
        for member_share in plan.member_shares:
            payment = MemberPayment.create(
                plan_id=plan_id,
                member_id=member_share.member_id,
                cooperative_id=self.cooperative_id,
                amount=member_share.net_share,
            )
            self._payments[payment.payment_id] = payment
            payments.append(payment)

        plan.status = "completed"

        # Update period
        period = self._periods.get(plan.period_id)
        if period:
            period.management_fee = plan.management_fee_amount
            period.reserve_fund_amount = plan.reserve_fund_amount
            period.distributable_amount = plan.distributable_amount
            period.total_distributed = sum(p.amount for p in payments)
            period.status = PeriodStatus.DISTRIBUTED

        return payments

    async def process_payment(
        self,
        payment_id: str,
        payment_method: str,
        reference: str | None = None,
        processed_by: str | None = None,
    ) -> MemberPayment | None:
        """
        Process a member payment.
        معالجة دفع عضو
        """
        payment = self._payments.get(payment_id)
        if not payment:
            return None

        payment.status = PaymentStatus.PAID
        payment.payment_method = payment_method
        payment.payment_date = datetime.now(UTC)
        payment.reference = reference
        payment.processed_by = processed_by
        payment.updated_at = datetime.now(UTC)

        # Record transaction
        await self._record_distribution_transaction(payment)

        return payment

    async def _record_distribution_transaction(
        self,
        payment: MemberPayment,
    ) -> Transaction:
        """Record transaction for a distribution payment"""
        plan = self._plans.get(payment.plan_id)
        period_id = plan.period_id if plan else None

        txn = Transaction.create(
            cooperative_id=self.cooperative_id,
            type=TransactionType.DISTRIBUTION,
            description=f"Distribution to member {payment.member_id}",
            description_ar=f"توزيع للعضو {payment.member_id}",
            amount=payment.amount,
            period_id=period_id,
            member_id=payment.member_id,
            reference=payment.payment_id,
        )
        self._transactions[txn.transaction_id] = txn
        return txn

    async def list_payments(
        self,
        plan_id: str | None = None,
        member_id: str | None = None,
        status: PaymentStatus | None = None,
    ) -> list[MemberPayment]:
        """List payments with filters"""
        payments = list(self._payments.values())

        if plan_id:
            payments = [p for p in payments if p.plan_id == plan_id]

        if member_id:
            payments = [p for p in payments if p.member_id == member_id]

        if status:
            payments = [p for p in payments if p.status == status]

        return payments

    # ===== Reporting =====

    async def get_period_summary(self, period_id: str) -> dict[str, Any]:
        """
        Get summary report for a financial period.
        الحصول على تقرير ملخص للفترة المالية
        """
        period = self._periods.get(period_id)
        if not period:
            raise ValueError(f"Period {period_id} not found")

        transactions = await self.list_transactions(period_id=period_id)

        # Group revenue by source
        revenue_by_source = {}
        for txn in transactions:
            if txn.type == TransactionType.REVENUE:
                source = txn.source or "other"
                revenue_by_source[source] = revenue_by_source.get(source, Decimal("0")) + txn.amount

        # Group expenses by category
        expenses_by_category = {}
        for txn in transactions:
            if txn.type == TransactionType.EXPENSE:
                category = txn.category or "other"
                expenses_by_category[category] = expenses_by_category.get(category, Decimal("0")) + txn.amount

        # Get distribution plan if exists
        plans = [p for p in self._plans.values() if p.period_id == period_id]

        return {
            "period": period.to_dict(),
            "summary": {
                "total_revenue": str(period.total_revenue),
                "total_expenses": str(period.total_expenses),
                "net_income": str(period.net_income),
                "management_fee": str(period.management_fee),
                "reserve_fund": str(period.reserve_fund_amount),
                "distributed": str(period.total_distributed),
            },
            "revenue_breakdown": {k: str(v) for k, v in revenue_by_source.items()},
            "expense_breakdown": {k: str(v) for k, v in expenses_by_category.items()},
            "distribution_plans": [p.to_summary() for p in plans],
            "transaction_count": len(transactions),
        }

    async def get_member_statement(
        self,
        member_id: str,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        requesting_cooperative_id: str = "",
    ) -> dict[str, Any]:
        """
        Get financial statement for a member.
        الحصول على كشف حساب مالي للعضو

        SECURITY: requesting_cooperative_id is required and must match service
        cooperative_id to prevent cross-cooperative financial data access.
        """
        # SECURITY: Verify caller belongs to this cooperative
        if requesting_cooperative_id != self.cooperative_id:
            raise PermissionError("Cannot access member statements from a different cooperative")

        payments = await self.list_payments(member_id=member_id)

        if from_date:
            payments = [p for p in payments if p.created_at >= from_date]
        if to_date:
            payments = [p for p in payments if p.created_at <= to_date]

        total_received = sum(p.amount for p in payments if p.status == PaymentStatus.PAID)
        total_pending = sum(p.amount for p in payments if p.status == PaymentStatus.PENDING)

        return {
            "member_id": member_id,
            "period": {
                "from": from_date.isoformat() if from_date else None,
                "to": to_date.isoformat() if to_date else None,
            },
            "summary": {
                "total_received": str(total_received),
                "total_pending": str(total_pending),
                "payment_count": len([p for p in payments if p.status == PaymentStatus.PAID]),
            },
            "payments": [p.to_dict() for p in sorted(payments, key=lambda p: p.created_at, reverse=True)],
        }


# Convenience functions
async def create_revenue_service(cooperative_id: str) -> RevenueService:
    """Create a new revenue service"""
    return RevenueService(cooperative_id=cooperative_id)
