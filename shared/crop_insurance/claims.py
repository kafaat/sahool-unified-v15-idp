"""
Claims Processing Module for Crop Insurance
============================================
وحدة معالجة المطالبات للتأمين الزراعي

Provides comprehensive claims management functionality:
- Claim submission and validation
- Claim processing workflow
- Payout calculation for traditional and parametric claims
- Automatic parametric trigger processing
- Claims storage and tracking

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from shared.crop_insurance.models import (
    ClaimEvidence,
    ClaimPayout,
    ClaimStatus,
    ClaimType,
    InsuranceClaim,
    InsuranceErrors,
    InsuranceException,
    InsurancePolicy,
    InsuranceType,
    ParametricTrigger,
    PolicyStatus,
    WeatherIndex,
)


@dataclass
class ValidationResult:
    """Result of claim validation | نتيجة التحقق من المطالبة"""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    errors_ar: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    warnings_ar: list[str] = field(default_factory=list)

    def add_error(self, en: str, ar: str) -> None:
        """Add an error message"""
        self.is_valid = False
        self.errors.append(en)
        self.errors_ar.append(ar)

    def add_warning(self, en: str, ar: str) -> None:
        """Add a warning message"""
        self.warnings.append(en)
        self.warnings_ar.append(ar)

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "errors_ar": self.errors_ar,
            "warnings": self.warnings,
            "warnings_ar": self.warnings_ar,
        }


@dataclass
class PayoutCalculation:
    """Detailed payout calculation | حساب الدفع المفصل"""

    claim_id: str

    # Amounts
    gross_loss: Decimal = Decimal("0")
    covered_loss: Decimal = Decimal("0")
    deductible: Decimal = Decimal("0")
    net_payout: Decimal = Decimal("0")
    currency: str = "SAR"

    # Calculation factors
    loss_percentage: float = 0.0
    coverage_percentage: float = 0.0
    loss_ratio: float = 0.0

    # For parametric claims
    trigger_value: float | None = None
    threshold_value: float | None = None
    payout_units: float | None = None
    unit_payout_rate: Decimal | None = None

    # Breakdown
    calculation_steps: list[dict[str, Any]] = field(default_factory=list)

    # Status
    is_approved: bool = False
    rejection_reason: str = ""
    rejection_reason_ar: str = ""

    calculated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    calculated_by: str = "system"

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "gross_loss": str(self.gross_loss),
            "covered_loss": str(self.covered_loss),
            "deductible": str(self.deductible),
            "net_payout": str(self.net_payout),
            "currency": self.currency,
            "loss_percentage": self.loss_percentage,
            "coverage_percentage": self.coverage_percentage,
            "loss_ratio": self.loss_ratio,
            "trigger_value": self.trigger_value,
            "threshold_value": self.threshold_value,
            "payout_units": self.payout_units,
            "unit_payout_rate": str(self.unit_payout_rate) if self.unit_payout_rate else None,
            "calculation_steps": self.calculation_steps,
            "is_approved": self.is_approved,
            "rejection_reason": self.rejection_reason,
            "rejection_reason_ar": self.rejection_reason_ar,
            "calculated_at": self.calculated_at.isoformat(),
            "calculated_by": self.calculated_by,
        }


class ClaimValidator:
    """
    Validates insurance claims before processing
    يتحقق من مطالبات التأمين قبل المعالجة
    """

    # Maximum days allowed between incident and reporting
    MAX_REPORTING_DELAY_DAYS = 30

    # Minimum evidence requirements by claim type
    MIN_EVIDENCE_REQUIREMENTS = {
        ClaimType.CROP_LOSS: 2,
        ClaimType.YIELD_SHORTFALL: 1,
        ClaimType.WEATHER_EVENT: 1,
        ClaimType.PEST_DAMAGE: 2,
        ClaimType.DISEASE_DAMAGE: 2,
        ClaimType.HAIL_DAMAGE: 3,
        ClaimType.FLOOD_DAMAGE: 2,
        ClaimType.DROUGHT_DAMAGE: 1,
        ClaimType.FROST_DAMAGE: 2,
        ClaimType.FIRE_DAMAGE: 3,
        ClaimType.EQUIPMENT_FAILURE: 2,
        ClaimType.PARAMETRIC_TRIGGER: 0,  # Auto-triggered
    }

    def validate(
        self,
        claim: InsuranceClaim,
        policy: InsurancePolicy,
    ) -> ValidationResult:
        """
        Validate a claim against its policy
        التحقق من المطالبة مقابل بوليصتها

        Args:
            claim: The insurance claim to validate
            policy: The associated insurance policy

        Returns:
            ValidationResult with any errors or warnings
        """
        result = ValidationResult(is_valid=True)

        # Check policy status
        if policy.status != PolicyStatus.ACTIVE:
            result.add_error(
                f"Policy is not active (status: {policy.status.value})",
                f"البوليصة غير نشطة (الحالة: {policy.status.value})",
            )

        # Check policy expiry
        if policy.expiry_date and claim.incident_date:
            if claim.incident_date > policy.expiry_date:
                result.add_error(
                    "Incident date is after policy expiry date",
                    "تاريخ الحادثة بعد تاريخ انتهاء البوليصة",
                )

            if claim.incident_date < (policy.effective_date or date.min):
                result.add_error(
                    "Incident date is before policy effective date",
                    "تاريخ الحادثة قبل تاريخ سريان البوليصة",
                )

        # Check reporting delay
        if claim.incident_date and claim.reported_date:
            delay = (claim.reported_date - claim.incident_date).days
            if delay > self.MAX_REPORTING_DELAY_DAYS:
                result.add_warning(
                    f"Claim reported {delay} days after incident (max: {self.MAX_REPORTING_DELAY_DAYS})",
                    f"تم الإبلاغ عن المطالبة بعد {delay} يوماً من الحادثة (الحد الأقصى: {self.MAX_REPORTING_DELAY_DAYS})",
                )

        # Check premium payment
        if policy.premium and not policy.premium.paid:
            result.add_error("Premium payment is required before claiming", "يجب دفع القسط قبل تقديم المطالبة")

        # Check evidence requirements
        min_evidence = self.MIN_EVIDENCE_REQUIREMENTS.get(claim.claim_type, 1)
        if len(claim.evidence) < min_evidence:
            result.add_error(
                f"Insufficient evidence: {len(claim.evidence)} provided, {min_evidence} required",
                f"دليل غير كافٍ: تم تقديم {len(claim.evidence)}، مطلوب {min_evidence}",
            )

        # Check field match
        if claim.field_id != policy.field_id:
            result.add_error("Claim field does not match policy field", "حقل المطالبة لا يتطابق مع حقل البوليصة")

        # Check loss percentage
        if claim.estimated_loss_percentage <= 0:
            result.add_error("Loss percentage must be greater than 0", "يجب أن تكون نسبة الخسارة أكبر من 0")
        elif claim.estimated_loss_percentage > 100:
            result.add_error("Loss percentage cannot exceed 100%", "لا يمكن أن تتجاوز نسبة الخسارة 100%")

        # Check affected area
        if claim.affected_area_hectares > claim.total_field_area_hectares:
            result.add_error(
                "Affected area cannot exceed total field area",
                "لا يمكن أن تتجاوز المساحة المتضررة مساحة الحقل الإجمالية",
            )

        # Validate claim description
        if not claim.description and not claim.description_ar:
            result.add_error("Claim description is required", "وصف المطالبة مطلوب")

        # Validate incident date
        if not claim.incident_date:
            result.add_error("Incident date is required", "تاريخ الحادثة مطلوب")

        # Check for parametric claims
        if claim.is_parametric_claim and policy.insurance_type not in [
            InsuranceType.PARAMETRIC,
            InsuranceType.HYBRID,
            InsuranceType.WEATHER_INDEX,
        ]:
            result.add_error(
                "Parametric claims require a parametric or hybrid policy",
                "المطالبات المعيارية تتطلب بوليصة معيارية أو مختلطة",
            )

        return result

    def validate_parametric_trigger(
        self,
        trigger: ParametricTrigger,
        measured_value: float,
    ) -> ValidationResult:
        """
        Validate a parametric trigger condition
        التحقق من شرط المحفز المعياري
        """
        result = ValidationResult(is_valid=True)

        is_triggered, payout_pct = trigger.evaluate_trigger(measured_value)

        if not is_triggered:
            result.add_error(
                f"Trigger condition not met: {measured_value} {trigger.threshold_operator} {trigger.threshold_value}",
                f"شرط المحفز غير مستوفى: {measured_value} {trigger.threshold_operator} {trigger.threshold_value}",
            )

        if is_triggered and trigger.requires_verification:
            result.add_warning(
                "This trigger requires manual verification before payout",
                "هذا المحفز يتطلب التحقق اليدوي قبل الدفع",
            )

        return result


class PayoutCalculator:
    """
    Calculates payouts for insurance claims
    يحسب المدفوعات لمطالبات التأمين
    """

    def calculate_traditional_payout(
        self,
        claim: InsuranceClaim,
        policy: InsurancePolicy,
        verified_loss_percentage: float | None = None,
    ) -> PayoutCalculation:
        """
        Calculate payout for traditional indemnity-based claim
        حساب الدفع للمطالبة التقليدية القائمة على التعويض

        Args:
            claim: The insurance claim
            policy: The associated policy
            verified_loss_percentage: Verified loss % (if different from estimated)

        Returns:
            PayoutCalculation with detailed breakdown
        """
        calculation = PayoutCalculation(claim_id=claim.id)
        calculation.calculation_steps = []

        # Use verified loss if available, otherwise estimated
        loss_pct = verified_loss_percentage or claim.verified_loss_percentage or claim.estimated_loss_percentage
        calculation.loss_percentage = loss_pct

        # Step 1: Calculate gross loss
        if policy.coverage:
            sum_insured = policy.coverage.sum_insured
            calculation.currency = policy.coverage.currency
        else:
            calculation.is_approved = False
            calculation.rejection_reason = "Policy has no coverage details"
            calculation.rejection_reason_ar = "البوليصة لا تحتوي على تفاصيل التغطية"
            return calculation

        # Calculate area ratio
        area_ratio = claim.affected_area_hectares / max(claim.total_field_area_hectares, 0.01)

        # Gross loss = Sum insured * Area ratio * Loss percentage
        gross_loss = sum_insured * Decimal(str(area_ratio)) * Decimal(str(loss_pct / 100))
        calculation.gross_loss = gross_loss
        calculation.calculation_steps.append(
            {
                "step": 1,
                "description": "Calculate gross loss",
                "description_ar": "حساب الخسارة الإجمالية",
                "formula": f"{sum_insured} × {area_ratio:.2f} × {loss_pct / 100:.2f}",
                "result": str(gross_loss),
            }
        )

        # Step 2: Apply coverage limits based on claim type
        coverage_multiplier = self._get_coverage_multiplier(claim.claim_type, policy.coverage)
        calculation.coverage_percentage = coverage_multiplier * 100

        covered_loss = gross_loss * Decimal(str(coverage_multiplier))
        calculation.covered_loss = covered_loss
        calculation.calculation_steps.append(
            {
                "step": 2,
                "description": f"Apply coverage limit ({coverage_multiplier:.0%})",
                "description_ar": f"تطبيق حد التغطية ({coverage_multiplier:.0%})",
                "formula": f"{gross_loss} × {coverage_multiplier}",
                "result": str(covered_loss),
            }
        )

        # Step 3: Apply deductible
        deductible_pct = policy.coverage.deductible_percentage / 100
        if policy.coverage.deductible_amount:
            deductible = min(policy.coverage.deductible_amount, covered_loss * Decimal(str(deductible_pct)))
        else:
            deductible = covered_loss * Decimal(str(deductible_pct))

        calculation.deductible = deductible
        calculation.calculation_steps.append(
            {
                "step": 3,
                "description": f"Apply deductible ({policy.coverage.deductible_percentage}%)",
                "description_ar": f"تطبيق التحمل ({policy.coverage.deductible_percentage}%)",
                "formula": f"min({covered_loss} × {deductible_pct}, fixed amount)",
                "result": str(deductible),
            }
        )

        # Step 4: Calculate net payout
        net_payout = max(covered_loss - deductible, Decimal("0"))

        # Apply maximum payout limit if set
        if policy.coverage.max_payout and net_payout > policy.coverage.max_payout:
            net_payout = policy.coverage.max_payout
            calculation.calculation_steps.append(
                {
                    "step": 4,
                    "description": "Apply maximum payout limit",
                    "description_ar": "تطبيق الحد الأقصى للدفع",
                    "result": str(net_payout),
                }
            )

        calculation.net_payout = net_payout
        calculation.calculation_steps.append(
            {
                "step": 5 if len(calculation.calculation_steps) > 3 else 4,
                "description": "Final net payout",
                "description_ar": "صافي الدفع النهائي",
                "formula": f"{covered_loss} - {deductible}",
                "result": str(net_payout),
            }
        )

        # Calculate loss ratio
        if policy.premium and policy.premium.total_premium > 0:
            calculation.loss_ratio = float(net_payout / policy.premium.total_premium)

        # Determine approval
        if net_payout > 0:
            calculation.is_approved = True
        else:
            calculation.is_approved = False
            calculation.rejection_reason = "Calculated payout is zero or negative"
            calculation.rejection_reason_ar = "الدفع المحسوب صفر أو سالب"

        return calculation

    def calculate_parametric_payout(
        self,
        claim: InsuranceClaim,
        policy: InsurancePolicy,
        trigger: ParametricTrigger,
        measured_value: float,
    ) -> PayoutCalculation:
        """
        Calculate payout for parametric/index-based claim
        حساب الدفع للمطالبة المعيارية/القائمة على المؤشر

        Args:
            claim: The insurance claim
            policy: The associated policy
            trigger: The parametric trigger that was activated
            measured_value: The measured value that triggered the claim

        Returns:
            PayoutCalculation with detailed breakdown
        """
        calculation = PayoutCalculation(claim_id=claim.id)
        calculation.calculation_steps = []
        calculation.trigger_value = measured_value
        calculation.threshold_value = trigger.threshold_value

        if not policy.coverage:
            calculation.is_approved = False
            calculation.rejection_reason = "Policy has no coverage details"
            calculation.rejection_reason_ar = "البوليصة لا تحتوي على تفاصيل التغطية"
            return calculation

        sum_insured = policy.coverage.sum_insured
        calculation.currency = policy.coverage.currency

        # Step 1: Evaluate trigger
        is_triggered, payout_percentage = trigger.evaluate_trigger(measured_value)

        if not is_triggered:
            calculation.is_approved = False
            calculation.rejection_reason = (
                f"Trigger condition not met: {measured_value} {trigger.threshold_operator} {trigger.threshold_value}"
            )
            calculation.rejection_reason_ar = (
                f"شرط المحفز غير مستوفى: {measured_value} {trigger.threshold_operator} {trigger.threshold_value}"
            )
            return calculation

        calculation.calculation_steps.append(
            {
                "step": 1,
                "description": "Evaluate trigger condition",
                "description_ar": "تقييم شرط المحفز",
                "formula": f"{measured_value} {trigger.threshold_operator} {trigger.threshold_value}",
                "result": "Triggered" if is_triggered else "Not triggered",
            }
        )

        # Step 2: Calculate payout amount
        if trigger.payout_amount:
            # Fixed payout amount
            gross_payout = trigger.payout_amount * Decimal(str(payout_percentage / 100))
            calculation.calculation_steps.append(
                {
                    "step": 2,
                    "description": f"Apply fixed payout ({payout_percentage}%)",
                    "description_ar": f"تطبيق الدفع الثابت ({payout_percentage}%)",
                    "formula": f"{trigger.payout_amount} × {payout_percentage / 100}",
                    "result": str(gross_payout),
                }
            )
        else:
            # Percentage of sum insured
            gross_payout = sum_insured * Decimal(str(payout_percentage / 100))
            calculation.calculation_steps.append(
                {
                    "step": 2,
                    "description": f"Calculate payout ({payout_percentage}% of sum insured)",
                    "description_ar": f"حساب الدفع ({payout_percentage}% من المبلغ المؤمن عليه)",
                    "formula": f"{sum_insured} × {payout_percentage / 100}",
                    "result": str(gross_payout),
                }
            )

        calculation.gross_loss = gross_payout
        calculation.loss_percentage = payout_percentage

        # Step 3: Apply deductible (usually lower or zero for parametric)
        deductible_pct = policy.coverage.deductible_percentage / 100
        deductible = gross_payout * Decimal(str(deductible_pct))
        calculation.deductible = deductible
        calculation.calculation_steps.append(
            {
                "step": 3,
                "description": f"Apply deductible ({policy.coverage.deductible_percentage}%)",
                "description_ar": f"تطبيق التحمل ({policy.coverage.deductible_percentage}%)",
                "result": str(deductible),
            }
        )

        # Step 4: Net payout
        net_payout = max(gross_payout - deductible, Decimal("0"))

        # Apply maximum payout limit
        if policy.coverage.max_payout and net_payout > policy.coverage.max_payout:
            net_payout = policy.coverage.max_payout

        calculation.net_payout = net_payout
        calculation.covered_loss = net_payout + deductible
        calculation.coverage_percentage = 100.0  # Full coverage for parametric

        calculation.calculation_steps.append(
            {
                "step": 4,
                "description": "Final net payout",
                "description_ar": "صافي الدفع النهائي",
                "formula": f"{gross_payout} - {deductible}",
                "result": str(net_payout),
            }
        )

        calculation.is_approved = net_payout > 0

        return calculation

    def calculate_weather_index_payout(
        self,
        claim: InsuranceClaim,
        policy: InsurancePolicy,
        index: WeatherIndex,
    ) -> PayoutCalculation:
        """
        Calculate payout for weather index insurance
        حساب الدفع للتأمين القائم على مؤشر الطقس

        Args:
            claim: The insurance claim
            policy: The associated policy
            index: The weather index that was triggered

        Returns:
            PayoutCalculation with detailed breakdown
        """
        calculation = PayoutCalculation(claim_id=claim.id)
        calculation.calculation_steps = []

        if not policy.coverage:
            calculation.is_approved = False
            calculation.rejection_reason = "Policy has no coverage details"
            calculation.rejection_reason_ar = "البوليصة لا تحتوي على تفاصيل التغطية"
            return calculation

        # Check if index is triggered
        if not index.is_triggered():
            calculation.is_approved = False
            calculation.rejection_reason = (
                f"Weather index not triggered: {index.current_value} vs threshold {index.trigger_threshold}"
            )
            calculation.rejection_reason_ar = (
                f"مؤشر الطقس غير محفز: {index.current_value} مقابل العتبة {index.trigger_threshold}"
            )
            return calculation

        calculation.trigger_value = index.current_value
        calculation.threshold_value = index.trigger_threshold
        calculation.currency = policy.coverage.currency

        # Calculate payout units
        payout_units = index.calculate_payout_units()
        calculation.payout_units = payout_units
        calculation.unit_payout_rate = index.payout_rate_per_unit

        calculation.calculation_steps.append(
            {
                "step": 1,
                "description": "Calculate payout units",
                "description_ar": "حساب وحدات الدفع",
                "formula": f"Based on deviation from threshold: {payout_units:.2f} {index.unit_name}",
                "result": str(payout_units),
            }
        )

        # Calculate gross payout
        gross_payout = index.payout_rate_per_unit * Decimal(str(payout_units))
        calculation.gross_loss = gross_payout
        calculation.calculation_steps.append(
            {
                "step": 2,
                "description": "Calculate gross payout",
                "description_ar": "حساب الدفع الإجمالي",
                "formula": f"{index.payout_rate_per_unit} × {payout_units}",
                "result": str(gross_payout),
            }
        )

        # Apply deductible
        deductible_pct = policy.coverage.deductible_percentage / 100
        deductible = gross_payout * Decimal(str(deductible_pct))
        calculation.deductible = deductible

        # Net payout
        net_payout = max(gross_payout - deductible, Decimal("0"))

        # Apply max payout limit
        if policy.coverage.max_payout and net_payout > policy.coverage.max_payout:
            net_payout = policy.coverage.max_payout

        calculation.net_payout = net_payout
        calculation.covered_loss = net_payout + deductible
        calculation.coverage_percentage = 100.0
        calculation.loss_percentage = (
            (float(gross_payout / policy.coverage.sum_insured) * 100) if policy.coverage.sum_insured else 0
        )

        calculation.calculation_steps.append(
            {
                "step": 3,
                "description": "Final net payout",
                "description_ar": "صافي الدفع النهائي",
                "formula": f"{gross_payout} - {deductible}",
                "result": str(net_payout),
            }
        )

        calculation.is_approved = net_payout > 0

        return calculation

    def _get_coverage_multiplier(self, claim_type: ClaimType, coverage: Any) -> float:
        """Get coverage multiplier based on claim type and coverage details"""
        coverage_map = {
            ClaimType.DROUGHT_DAMAGE: coverage.drought_coverage if coverage else 1.0,
            ClaimType.FLOOD_DAMAGE: coverage.flood_coverage if coverage else 1.0,
            ClaimType.HAIL_DAMAGE: coverage.hail_coverage if coverage else 1.0,
            ClaimType.FROST_DAMAGE: coverage.frost_coverage if coverage else 1.0,
            ClaimType.PEST_DAMAGE: coverage.pest_coverage if coverage else 0.8,
            ClaimType.DISEASE_DAMAGE: coverage.disease_coverage if coverage else 0.8,
        }
        return coverage_map.get(claim_type, 1.0)


class ClaimStorage:
    """
    Storage backend for insurance claims
    التخزين الخلفي لمطالبات التأمين
    """

    def __init__(self, storage_path: str | None = None):
        """Initialize storage"""
        # Default to /var/lib/sahool in production, /tmp for development only
        default_path = (
            "/var/lib/sahool/insurance_claims"
            if os.getenv("ENVIRONMENT") == "production"
            else "/tmp/sahool_insurance_claims"
        )  # nosec B108
        self.storage_path = Path(storage_path or os.getenv("INSURANCE_CLAIMS_STORAGE_PATH", default_path))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()

    async def save_claim(self, claim: InsuranceClaim) -> None:
        """Save a claim to storage"""
        async with self._lock:
            file_path = self.storage_path / f"{claim.tenant_id}_claims.jsonl"
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(claim.to_dict(), ensure_ascii=False) + "\n")

    async def get_claim(self, claim_id: str, tenant_id: str) -> InsuranceClaim | None:
        """Get a claim by ID"""
        claims = await self.load_all_claims(tenant_id)
        for claim in claims:
            if claim.id == claim_id:
                return claim
        return None

    async def update_claim(self, claim: InsuranceClaim) -> None:
        """Update an existing claim"""
        claims = await self.load_all_claims(claim.tenant_id)
        updated_claims = [c if c.id != claim.id else claim for c in claims]

        # Rewrite file
        async with self._lock:
            file_path = self.storage_path / f"{claim.tenant_id}_claims.jsonl"
            with open(file_path, "w", encoding="utf-8") as f:
                for c in updated_claims:
                    f.write(json.dumps(c.to_dict(), ensure_ascii=False) + "\n")

    async def load_all_claims(self, tenant_id: str) -> list[InsuranceClaim]:
        """Load all claims for a tenant"""
        file_path = self.storage_path / f"{tenant_id}_claims.jsonl"
        if not file_path.exists():
            return []

        claims = []
        async with self._lock:
            with open(file_path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        claims.append(self._dict_to_claim(data))
        return claims

    async def load_claims_by_policy(
        self,
        tenant_id: str,
        policy_id: str,
    ) -> list[InsuranceClaim]:
        """Load claims for a specific policy"""
        all_claims = await self.load_all_claims(tenant_id)
        return [c for c in all_claims if c.policy_id == policy_id]

    async def load_claims_by_status(
        self,
        tenant_id: str,
        status: ClaimStatus,
    ) -> list[InsuranceClaim]:
        """Load claims by status"""
        all_claims = await self.load_all_claims(tenant_id)
        return [c for c in all_claims if c.status == status]

    def _dict_to_claim(self, data: dict[str, Any]) -> InsuranceClaim:
        """Convert dictionary to InsuranceClaim"""
        # Parse evidence
        evidence = []
        for e_data in data.get("evidence", []):
            evidence.append(
                ClaimEvidence(
                    id=e_data.get("id", str(uuid.uuid4())),
                    evidence_type=e_data.get("evidence_type", ""),
                    title=e_data.get("title", ""),
                    title_ar=e_data.get("title_ar", ""),
                    description=e_data.get("description", ""),
                    description_ar=e_data.get("description_ar", ""),
                    file_url=e_data.get("file_url"),
                    file_type=e_data.get("file_type"),
                    file_size_bytes=e_data.get("file_size_bytes"),
                    data_source=e_data.get("data_source", ""),
                    data_value=e_data.get("data_value"),
                    verified=e_data.get("verified", False),
                )
            )

        # Parse payout
        payout = None
        if data.get("payout"):
            p_data = data["payout"]
            payout = ClaimPayout(
                id=p_data.get("id", str(uuid.uuid4())),
                claim_id=p_data.get("claim_id", ""),
                approved_amount=Decimal(p_data.get("approved_amount", "0")),
                deductible_amount=Decimal(p_data.get("deductible_amount", "0")),
                net_payout=Decimal(p_data.get("net_payout", "0")),
                currency=p_data.get("currency", "SAR"),
                loss_percentage=p_data.get("loss_percentage", 0.0),
                coverage_percentage=p_data.get("coverage_percentage", 0.0),
                payment_status=p_data.get("payment_status", "pending"),
            )

        return InsuranceClaim(
            id=data.get("id", str(uuid.uuid4())),
            claim_number=data.get("claim_number", ""),
            policy_id=data.get("policy_id", ""),
            policy_number=data.get("policy_number", ""),
            tenant_id=data.get("tenant_id", ""),
            farmer_id=data.get("farmer_id", ""),
            claim_type=ClaimType(data.get("claim_type", "crop_loss")),
            status=ClaimStatus(data.get("status", "draft")),
            title=data.get("title", ""),
            title_ar=data.get("title_ar", ""),
            description=data.get("description", ""),
            description_ar=data.get("description_ar", ""),
            incident_date=date.fromisoformat(data["incident_date"]) if data.get("incident_date") else None,
            discovery_date=date.fromisoformat(data["discovery_date"]) if data.get("discovery_date") else None,
            reported_date=date.fromisoformat(data["reported_date"]) if data.get("reported_date") else date.today(),
            field_id=data.get("field_id", ""),
            field_name=data.get("field_name", ""),
            affected_area_hectares=data.get("affected_area_hectares", 0.0),
            total_field_area_hectares=data.get("total_field_area_hectares", 0.0),
            crop_type=data.get("crop_type", ""),
            crop_stage=data.get("crop_stage", ""),
            estimated_loss_percentage=data.get("estimated_loss_percentage", 0.0),
            estimated_loss_amount=Decimal(data.get("estimated_loss_amount", "0")),
            actual_yield=data.get("actual_yield"),
            expected_yield=data.get("expected_yield"),
            cause_of_loss=data.get("cause_of_loss", ""),
            cause_of_loss_ar=data.get("cause_of_loss_ar", ""),
            is_parametric_claim=data.get("is_parametric_claim", False),
            trigger_id=data.get("trigger_id"),
            index_value=data.get("index_value"),
            threshold_value=data.get("threshold_value"),
            evidence=evidence,
            verified_loss_percentage=data.get("verified_loss_percentage"),
            payout=payout,
            status_history=data.get("status_history", []),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(UTC),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(UTC),
            contact_phone=data.get("contact_phone", ""),
            contact_email=data.get("contact_email", ""),
            preferred_language=data.get("preferred_language", "ar"),
        )


class ClaimProcessor:
    """
    Main processor for insurance claims
    المعالج الرئيسي لمطالبات التأمين

    Handles the complete claim lifecycle:
    - Claim creation and submission
    - Validation and verification
    - Payout calculation
    - Status management
    - Automatic parametric trigger processing

    Usage:
        processor = ClaimProcessor(tenant_id="farm_001")

        # Submit a traditional claim
        claim = await processor.submit_claim(
            policy=policy,
            claim_type=ClaimType.DROUGHT_DAMAGE,
            incident_date=date(2026, 1, 10),
            description="Severe drought caused 30% crop loss",
            estimated_loss_percentage=30.0,
            affected_area_hectares=5.0,
            evidence=[evidence1, evidence2],
        )

        # Process parametric trigger
        claim = await processor.process_parametric_trigger(
            policy=policy,
            trigger=trigger,
            measured_value=45.0,
        )
    """

    def __init__(
        self,
        tenant_id: str,
        storage: ClaimStorage | None = None,
        on_claim_submitted: Callable[[InsuranceClaim], None] | None = None,
        on_claim_approved: Callable[[InsuranceClaim, PayoutCalculation], None] | None = None,
    ):
        """
        Initialize the claim processor

        Args:
            tenant_id: Tenant identifier
            storage: Storage backend (default: file-based)
            on_claim_submitted: Callback when claim is submitted
            on_claim_approved: Callback when claim is approved
        """
        self.tenant_id = tenant_id
        self.storage = storage or ClaimStorage()
        self.validator = ClaimValidator()
        self.calculator = PayoutCalculator()
        self.on_claim_submitted = on_claim_submitted
        self.on_claim_approved = on_claim_approved

        # Claim number counter (in production, use database sequence)
        self._claim_counter = 1000

    def _generate_claim_number(self) -> str:
        """Generate unique claim number"""
        self._claim_counter += 1
        timestamp = datetime.now().strftime("%Y%m")
        return f"CLM-{timestamp}-{self._claim_counter:05d}"

    async def create_draft_claim(
        self,
        policy: InsurancePolicy,
        claim_type: ClaimType,
        incident_date: date,
        description: str = "",
        description_ar: str = "",
        estimated_loss_percentage: float = 0.0,
        affected_area_hectares: float | None = None,
    ) -> InsuranceClaim:
        """
        Create a draft claim (not yet submitted)
        إنشاء مسودة مطالبة (لم يتم تقديمها بعد)
        """
        claim = InsuranceClaim(
            claim_number=self._generate_claim_number(),
            policy_id=policy.id,
            policy_number=policy.policy_number,
            tenant_id=self.tenant_id,
            farmer_id=policy.farmer_id,
            claim_type=claim_type,
            status=ClaimStatus.DRAFT,
            incident_date=incident_date,
            description=description,
            description_ar=description_ar,
            field_id=policy.field_id,
            field_name=policy.field_name,
            affected_area_hectares=affected_area_hectares or policy.field_area_hectares,
            total_field_area_hectares=policy.field_area_hectares,
            crop_type=policy.crop_type,
            estimated_loss_percentage=estimated_loss_percentage,
        )

        await self.storage.save_claim(claim)
        return claim

    async def add_evidence(
        self,
        claim_id: str,
        evidence: ClaimEvidence,
    ) -> InsuranceClaim:
        """Add evidence to a claim"""
        claim = await self.storage.get_claim(claim_id, self.tenant_id)
        if not claim:
            raise InsuranceException(InsuranceErrors.CLAIM_NOT_FOUND, status_code=404)

        if claim.status != ClaimStatus.DRAFT:
            raise InsuranceException(
                InsuranceErrors.CLAIM_INVALID_STATUS,
                details="Can only add evidence to draft claims",
            )

        claim.evidence.append(evidence)
        claim.updated_at = datetime.now(UTC)
        await self.storage.update_claim(claim)
        return claim

    async def submit_claim(
        self,
        policy: InsurancePolicy,
        claim_type: ClaimType,
        incident_date: date,
        description: str = "",
        description_ar: str = "",
        estimated_loss_percentage: float = 0.0,
        affected_area_hectares: float | None = None,
        evidence: list[ClaimEvidence] | None = None,
        cause_of_loss: str = "",
        cause_of_loss_ar: str = "",
        contact_phone: str = "",
        contact_email: str = "",
    ) -> tuple[InsuranceClaim, ValidationResult]:
        """
        Submit a new insurance claim
        تقديم مطالبة تأمين جديدة

        Args:
            policy: The insurance policy
            claim_type: Type of claim
            incident_date: Date of the incident
            description: Description of the loss (English)
            description_ar: Description of the loss (Arabic)
            estimated_loss_percentage: Estimated loss percentage
            affected_area_hectares: Affected area (defaults to full field)
            evidence: List of evidence items
            cause_of_loss: Cause of loss (English)
            cause_of_loss_ar: Cause of loss (Arabic)
            contact_phone: Contact phone number
            contact_email: Contact email

        Returns:
            Tuple of (claim, validation_result)
        """
        # Create the claim
        claim = InsuranceClaim(
            claim_number=self._generate_claim_number(),
            policy_id=policy.id,
            policy_number=policy.policy_number,
            tenant_id=self.tenant_id,
            farmer_id=policy.farmer_id,
            claim_type=claim_type,
            status=ClaimStatus.DRAFT,
            incident_date=incident_date,
            discovery_date=date.today(),
            reported_date=date.today(),
            description=description,
            description_ar=description_ar,
            field_id=policy.field_id,
            field_name=policy.field_name,
            affected_area_hectares=affected_area_hectares or policy.field_area_hectares,
            total_field_area_hectares=policy.field_area_hectares,
            crop_type=policy.crop_type,
            estimated_loss_percentage=estimated_loss_percentage,
            evidence=evidence or [],
            cause_of_loss=cause_of_loss,
            cause_of_loss_ar=cause_of_loss_ar,
            contact_phone=contact_phone,
            contact_email=contact_email,
        )

        # Validate
        validation_result = self.validator.validate(claim, policy)

        if validation_result.is_valid:
            # Submit the claim
            claim.add_status_change(ClaimStatus.SUBMITTED, "farmer", "Claim submitted")
            claim.submitted_at = datetime.now(UTC)

            # Save
            await self.storage.save_claim(claim)

            # Trigger callback
            if self.on_claim_submitted:
                self.on_claim_submitted(claim)
        else:
            # Save as draft with errors
            await self.storage.save_claim(claim)

        return claim, validation_result

    async def submit_existing_claim(
        self,
        claim_id: str,
        policy: InsurancePolicy,
    ) -> tuple[InsuranceClaim, ValidationResult]:
        """Submit an existing draft claim"""
        claim = await self.storage.get_claim(claim_id, self.tenant_id)
        if not claim:
            raise InsuranceException(InsuranceErrors.CLAIM_NOT_FOUND, status_code=404)

        if claim.status != ClaimStatus.DRAFT:
            raise InsuranceException(
                InsuranceErrors.CLAIM_ALREADY_SUBMITTED,
                details=f"Claim status: {claim.status.value}",
            )

        # Validate
        validation_result = self.validator.validate(claim, policy)

        if validation_result.is_valid:
            claim.add_status_change(ClaimStatus.SUBMITTED, "farmer", "Claim submitted")
            claim.submitted_at = datetime.now(UTC)
            await self.storage.update_claim(claim)

            if self.on_claim_submitted:
                self.on_claim_submitted(claim)

        return claim, validation_result

    async def process_parametric_trigger(
        self,
        policy: InsurancePolicy,
        trigger: ParametricTrigger,
        measured_value: float,
        data_source: str = "weather_service",
        auto_approve: bool = True,
    ) -> tuple[InsuranceClaim | None, PayoutCalculation | None]:
        """
        Process an automatic parametric trigger
        معالجة محفز معياري تلقائي

        Args:
            policy: The insurance policy
            trigger: The parametric trigger configuration
            measured_value: The measured value that triggered the claim
            data_source: Source of the measurement data
            auto_approve: Whether to auto-approve if trigger is valid

        Returns:
            Tuple of (claim, payout_calculation) or (None, None) if not triggered
        """
        # Validate trigger
        validation = self.validator.validate_parametric_trigger(trigger, measured_value)

        if not validation.is_valid:
            return None, None

        # Create parametric claim
        claim = InsuranceClaim(
            claim_number=self._generate_claim_number(),
            policy_id=policy.id,
            policy_number=policy.policy_number,
            tenant_id=self.tenant_id,
            farmer_id=policy.farmer_id,
            claim_type=ClaimType.PARAMETRIC_TRIGGER,
            status=ClaimStatus.SUBMITTED,
            title=f"Parametric Trigger: {trigger.name}",
            title_ar=f"محفز معياري: {trigger.name_ar}",
            description=f"Automatic claim triggered by {trigger.trigger_type.value}: {measured_value} {trigger.measurement_unit}",
            description_ar=f"مطالبة تلقائية محفزة بواسطة {trigger.trigger_type.value}: {measured_value} {trigger.measurement_unit_ar}",
            incident_date=date.today(),
            reported_date=date.today(),
            field_id=policy.field_id,
            field_name=policy.field_name,
            affected_area_hectares=policy.field_area_hectares,
            total_field_area_hectares=policy.field_area_hectares,
            crop_type=policy.crop_type,
            is_parametric_claim=True,
            trigger_id=trigger.id,
            index_value=measured_value,
            threshold_value=trigger.threshold_value,
            submitted_at=datetime.now(UTC),
        )

        # Add evidence from data source
        claim.evidence.append(
            ClaimEvidence(
                evidence_type="sensor_data",
                title="Parametric Trigger Data",
                title_ar="بيانات المحفز المعياري",
                description=f"Measured value: {measured_value} {trigger.measurement_unit}",
                description_ar=f"القيمة المقاسة: {measured_value} {trigger.measurement_unit_ar}",
                data_source=data_source,
                data_value=measured_value,
                data_timestamp=datetime.now(UTC),
                verified=True,
                verified_by="system",
                verified_at=datetime.now(UTC),
            )
        )

        # Calculate payout
        payout_calc = self.calculator.calculate_parametric_payout(claim, policy, trigger, measured_value)

        if auto_approve and payout_calc.is_approved and not trigger.requires_verification:
            # Auto-approve the claim
            claim.add_status_change(ClaimStatus.APPROVED, "system", "Auto-approved parametric claim")
            claim.verified_loss_percentage = payout_calc.loss_percentage

            # Create payout record
            payout = ClaimPayout(
                claim_id=claim.id,
                approved_amount=payout_calc.covered_loss,
                deductible_amount=payout_calc.deductible,
                net_payout=payout_calc.net_payout,
                currency=payout_calc.currency,
                loss_percentage=payout_calc.loss_percentage,
                coverage_percentage=payout_calc.coverage_percentage,
                calculation_details={"steps": payout_calc.calculation_steps},
                approved_by="system",
                approved_at=datetime.now(UTC),
                approval_notes="Automatically approved parametric claim",
                approval_notes_ar="مطالبة معيارية موافق عليها تلقائياً",
            )
            payout.calculate_net_payout()
            claim.payout = payout

            # Trigger callback
            if self.on_claim_approved:
                self.on_claim_approved(claim, payout_calc)
        else:
            # Requires manual review
            claim.add_status_change(ClaimStatus.UNDER_REVIEW, "system", "Parametric claim requires verification")

        await self.storage.save_claim(claim)
        return claim, payout_calc

    async def process_weather_index_trigger(
        self,
        policy: InsurancePolicy,
        index: WeatherIndex,
        auto_approve: bool = True,
    ) -> tuple[InsuranceClaim | None, PayoutCalculation | None]:
        """
        Process a weather index trigger
        معالجة محفز مؤشر الطقس
        """
        if not index.is_triggered():
            return None, None

        # Create claim from weather index
        claim = InsuranceClaim(
            claim_number=self._generate_claim_number(),
            policy_id=policy.id,
            policy_number=policy.policy_number,
            tenant_id=self.tenant_id,
            farmer_id=policy.farmer_id,
            claim_type=ClaimType.WEATHER_EVENT,
            status=ClaimStatus.SUBMITTED,
            title=f"Weather Index Trigger: {index.index_type.value}",
            title_ar=f"محفز مؤشر الطقس: {index.index_type.value}",
            description=f"Index value {index.current_value} crossed threshold {index.trigger_threshold}",
            description_ar=f"قيمة المؤشر {index.current_value} تجاوزت العتبة {index.trigger_threshold}",
            incident_date=date.today(),
            reported_date=date.today(),
            field_id=policy.field_id,
            field_name=policy.field_name,
            affected_area_hectares=policy.field_area_hectares,
            total_field_area_hectares=policy.field_area_hectares,
            crop_type=policy.crop_type,
            is_parametric_claim=True,
            index_value=index.current_value,
            threshold_value=index.trigger_threshold,
            submitted_at=datetime.now(UTC),
        )

        # Add weather data evidence
        claim.evidence.append(
            ClaimEvidence(
                evidence_type="weather_data",
                title="Weather Index Data",
                title_ar="بيانات مؤشر الطقس",
                description=f"Index: {index.index_type.value}, Value: {index.current_value} {index.unit_name}",
                description_ar=f"المؤشر: {index.index_type.value}، القيمة: {index.current_value} {index.unit_name_ar}",
                data_source=f"station_{index.measurement_station_id}",
                data_value=index.current_value,
                data_timestamp=index.last_updated,
                verified=True,
                verified_by="system",
                verified_at=datetime.now(UTC),
            )
        )

        # Calculate payout
        payout_calc = self.calculator.calculate_weather_index_payout(claim, policy, index)

        if auto_approve and payout_calc.is_approved:
            claim.add_status_change(ClaimStatus.APPROVED, "system", "Auto-approved weather index claim")
            claim.verified_loss_percentage = payout_calc.loss_percentage

            payout = ClaimPayout(
                claim_id=claim.id,
                approved_amount=payout_calc.covered_loss,
                deductible_amount=payout_calc.deductible,
                net_payout=payout_calc.net_payout,
                currency=payout_calc.currency,
                loss_percentage=payout_calc.loss_percentage,
                coverage_percentage=payout_calc.coverage_percentage,
                calculation_details={"steps": payout_calc.calculation_steps},
                approved_by="system",
                approved_at=datetime.now(UTC),
            )
            payout.calculate_net_payout()
            claim.payout = payout

            if self.on_claim_approved:
                self.on_claim_approved(claim, payout_calc)

        await self.storage.save_claim(claim)
        return claim, payout_calc

    async def review_claim(
        self,
        claim_id: str,
        reviewer_id: str,
        decision: str,  # "approve", "reject", "request_inspection"
        verified_loss_percentage: float | None = None,
        notes: str = "",
        notes_ar: str = "",
    ) -> InsuranceClaim:
        """
        Review and process a submitted claim
        مراجعة ومعالجة مطالبة مقدمة
        """
        claim = await self.storage.get_claim(claim_id, self.tenant_id)
        if not claim:
            raise InsuranceException(InsuranceErrors.CLAIM_NOT_FOUND, status_code=404)

        if claim.status not in [ClaimStatus.SUBMITTED, ClaimStatus.UNDER_REVIEW]:
            raise InsuranceException(
                InsuranceErrors.CLAIM_INVALID_STATUS,
                details=f"Cannot review claim with status: {claim.status.value}",
            )

        if decision == "approve":
            claim.add_status_change(ClaimStatus.APPROVED, reviewer_id, notes)
            claim.verified_loss_percentage = verified_loss_percentage
            claim.resolved_at = datetime.now(UTC)

        elif decision == "reject":
            claim.add_status_change(ClaimStatus.REJECTED, reviewer_id, notes)
            claim.resolved_at = datetime.now(UTC)

        elif decision == "request_inspection":
            claim.add_status_change(ClaimStatus.FIELD_INSPECTION, reviewer_id, notes)

        else:
            raise ValueError(f"Invalid decision: {decision}")

        claim.assessment_notes = notes
        claim.assessment_notes_ar = notes_ar
        claim.assessor_id = reviewer_id
        claim.assessment_date = date.today()

        await self.storage.update_claim(claim)
        return claim

    async def calculate_payout(
        self,
        claim_id: str,
        policy: InsurancePolicy,
    ) -> PayoutCalculation:
        """Calculate payout for an approved claim"""
        claim = await self.storage.get_claim(claim_id, self.tenant_id)
        if not claim:
            raise InsuranceException(InsuranceErrors.CLAIM_NOT_FOUND, status_code=404)

        if claim.is_parametric_claim and claim.trigger_id:
            # Find trigger
            trigger = next((t for t in policy.parametric_triggers if t.id == claim.trigger_id), None)
            if trigger and claim.index_value is not None:
                return self.calculator.calculate_parametric_payout(claim, policy, trigger, claim.index_value)

        # Traditional claim
        return self.calculator.calculate_traditional_payout(claim, policy)

    async def finalize_payout(
        self,
        claim_id: str,
        policy: InsurancePolicy,
        approved_by: str,
        payment_method: str = "bank_transfer",
        bank_name: str = "",
        account_number: str = "",
        iban: str = "",
    ) -> InsuranceClaim:
        """Finalize and record payout for approved claim"""
        claim = await self.storage.get_claim(claim_id, self.tenant_id)
        if not claim:
            raise InsuranceException(InsuranceErrors.CLAIM_NOT_FOUND, status_code=404)

        if claim.status != ClaimStatus.APPROVED:
            raise InsuranceException(
                InsuranceErrors.CLAIM_INVALID_STATUS, details="Claim must be approved before payout"
            )

        # Calculate payout
        payout_calc = await self.calculate_payout(claim_id, policy)

        if not payout_calc.is_approved:
            raise InsuranceException(InsuranceErrors.CLAIM_INVALID_STATUS, details=payout_calc.rejection_reason)

        # Create payout record
        payout = ClaimPayout(
            claim_id=claim.id,
            approved_amount=payout_calc.covered_loss,
            deductible_amount=payout_calc.deductible,
            net_payout=payout_calc.net_payout,
            currency=payout_calc.currency,
            loss_percentage=payout_calc.loss_percentage,
            coverage_percentage=payout_calc.coverage_percentage,
            calculation_details={"steps": payout_calc.calculation_steps},
            payment_method=payment_method,
            bank_name=bank_name,
            account_number=account_number,
            iban=iban,
            approved_by=approved_by,
            approved_at=datetime.now(UTC),
        )
        payout.calculate_net_payout()

        claim.payout = payout
        claim.add_status_change(ClaimStatus.PAID, approved_by, "Payout finalized")
        claim.resolved_at = datetime.now(UTC)

        await self.storage.update_claim(claim)

        if self.on_claim_approved:
            self.on_claim_approved(claim, payout_calc)

        return claim

    async def get_claim(self, claim_id: str) -> InsuranceClaim | None:
        """Get a claim by ID"""
        return await self.storage.get_claim(claim_id, self.tenant_id)

    async def get_claims_by_policy(self, policy_id: str) -> list[InsuranceClaim]:
        """Get all claims for a policy"""
        return await self.storage.load_claims_by_policy(self.tenant_id, policy_id)

    async def get_claims_by_status(self, status: ClaimStatus) -> list[InsuranceClaim]:
        """Get claims by status"""
        return await self.storage.load_claims_by_status(self.tenant_id, status)

    async def get_all_claims(self) -> list[InsuranceClaim]:
        """Get all claims for the tenant"""
        return await self.storage.load_all_claims(self.tenant_id)


# Singleton instances
_claim_processors: dict[str, ClaimProcessor] = {}


def get_claim_processor(tenant_id: str) -> ClaimProcessor:
    """Get or create a claim processor for a tenant"""
    if tenant_id not in _claim_processors:
        _claim_processors[tenant_id] = ClaimProcessor(tenant_id)
    return _claim_processors[tenant_id]


async def submit_claim(
    tenant_id: str,
    policy: InsurancePolicy,
    claim_type: ClaimType,
    incident_date: date,
    description: str = "",
    estimated_loss_percentage: float = 0.0,
    evidence: list[ClaimEvidence] | None = None,
    **kwargs,
) -> tuple[InsuranceClaim, ValidationResult]:
    """Submit a claim using the default processor"""
    processor = get_claim_processor(tenant_id)
    return await processor.submit_claim(
        policy=policy,
        claim_type=claim_type,
        incident_date=incident_date,
        description=description,
        estimated_loss_percentage=estimated_loss_percentage,
        evidence=evidence,
        **kwargs,
    )


async def get_claim_status(
    tenant_id: str,
    claim_id: str,
) -> dict[str, Any]:
    """Get claim status"""
    processor = get_claim_processor(tenant_id)
    claim = await processor.get_claim(claim_id)
    if not claim:
        raise InsuranceException(InsuranceErrors.CLAIM_NOT_FOUND, status_code=404)

    return {
        "claim_id": claim.id,
        "claim_number": claim.claim_number,
        "status": claim.status.value,
        "status_history": claim.status_history,
        "submitted_at": claim.submitted_at.isoformat() if claim.submitted_at else None,
        "payout": claim.payout.to_dict() if claim.payout else None,
    }


async def process_parametric_trigger(
    tenant_id: str,
    policy: InsurancePolicy,
    trigger: ParametricTrigger,
    measured_value: float,
) -> tuple[InsuranceClaim | None, PayoutCalculation | None]:
    """Process a parametric trigger using the default processor"""
    processor = get_claim_processor(tenant_id)
    return await processor.process_parametric_trigger(
        policy=policy,
        trigger=trigger,
        measured_value=measured_value,
    )
