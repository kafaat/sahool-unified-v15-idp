"""
Harvest Quality Pricing Module
==============================
وحدة تسعير جودة المحصول

Grade-based pricing calculations for agricultural produce.
Supports price adjustments based on quality parameters and market conditions.

حسابات التسعير المبنية على الدرجة للمنتجات الزراعية.
يدعم تعديلات الأسعار بناءً على معايير الجودة وظروف السوق.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from .models import (
    CropCategory,
    Currency,
    GradePriceMatrix,
    PriceCalculation,
    PriceUnit,
    QualityGrade,
    QualityTestRecord,
)

# ─────────────────────────────────────────────────────────────────────────────
# Predefined Price Matrices - مصفوفات الأسعار المحددة مسبقاً
# ─────────────────────────────────────────────────────────────────────────────


def get_wheat_price_matrix(
    base_price: Decimal = Decimal("2.00"),
    currency: Currency = Currency.SAR,
) -> GradePriceMatrix:
    """
    Get wheat price matrix
    الحصول على مصفوفة أسعار القمح
    """
    return GradePriceMatrix(
        id="wheat_price_matrix_default",
        crop_category=CropCategory.GRAIN,
        crop_type="wheat",
        crop_type_ar="قمح",
        currency=currency,
        price_unit=PriceUnit.KG,
        base_price=base_price,
        premium_multiplier=1.35,  # 35% premium
        grade_a_multiplier=1.15,  # 15% premium
        grade_b_multiplier=1.00,  # Base price
        grade_c_multiplier=0.85,  # 15% discount
        industrial_multiplier=0.60,  # 40% discount
        moisture_adjustment_per_percent=Decimal("0.05"),  # 0.05 SAR deduction per % above 13%
        protein_bonus_per_percent=Decimal("0.10"),  # 0.10 SAR bonus per % above 12%
        foreign_matter_deduction_per_percent=Decimal("0.08"),  # 0.08 SAR deduction per %
        is_active=True,
        source="market",
    )


def get_barley_price_matrix(
    base_price: Decimal = Decimal("1.50"),
    currency: Currency = Currency.SAR,
) -> GradePriceMatrix:
    """
    Get barley price matrix
    الحصول على مصفوفة أسعار الشعير
    """
    return GradePriceMatrix(
        id="barley_price_matrix_default",
        crop_category=CropCategory.GRAIN,
        crop_type="barley",
        crop_type_ar="شعير",
        currency=currency,
        price_unit=PriceUnit.KG,
        base_price=base_price,
        premium_multiplier=1.30,
        grade_a_multiplier=1.12,
        grade_b_multiplier=1.00,
        grade_c_multiplier=0.88,
        industrial_multiplier=0.65,
        moisture_adjustment_per_percent=Decimal("0.04"),
        protein_bonus_per_percent=Decimal("0.08"),
        foreign_matter_deduction_per_percent=Decimal("0.06"),
        is_active=True,
        source="market",
    )


def get_date_price_matrix(
    variety: str = "sukkari",
    base_price: Decimal = Decimal("25.00"),
    currency: Currency = Currency.SAR,
) -> GradePriceMatrix:
    """
    Get date price matrix by variety
    الحصول على مصفوفة أسعار التمور حسب الصنف
    """
    # Price varies significantly by variety
    variety_multipliers = {
        "sukkari": Decimal("1.0"),
        "ajwa": Decimal("2.5"),  # Premium variety
        "khalas": Decimal("1.2"),
        "medjool": Decimal("1.8"),
        "barhi": Decimal("0.9"),
        "safawi": Decimal("1.1"),
        "segai": Decimal("0.85"),
        "khudri": Decimal("0.7"),
        "mabroom": Decimal("1.3"),
    }

    variety_ar = {
        "sukkari": "سكري",
        "ajwa": "عجوة",
        "khalas": "خلاص",
        "medjool": "مجهول",
        "barhi": "برحي",
        "safawi": "صفاوي",
        "segai": "صقعي",
        "khudri": "خضري",
        "mabroom": "مبروم",
    }

    multiplier = variety_multipliers.get(variety.lower(), Decimal("1.0"))
    adjusted_base = base_price * multiplier

    return GradePriceMatrix(
        id=f"date_price_matrix_{variety.lower()}",
        crop_category=CropCategory.DATE,
        crop_type="date",
        crop_type_ar="تمر",
        variety=variety.lower(),
        variety_ar=variety_ar.get(variety.lower(), variety),
        currency=currency,
        price_unit=PriceUnit.KG,
        base_price=adjusted_base,
        premium_multiplier=1.50,  # Dates have high premium for top quality
        grade_a_multiplier=1.20,
        grade_b_multiplier=1.00,
        grade_c_multiplier=0.75,
        industrial_multiplier=0.45,  # Processing dates significantly cheaper
        is_active=True,
        source="market",
    )


def get_vegetable_price_matrix(
    vegetable_type: str = "tomato",
    base_price: Decimal = Decimal("3.50"),
    currency: Currency = Currency.SAR,
) -> GradePriceMatrix:
    """
    Get vegetable price matrix
    الحصول على مصفوفة أسعار الخضروات
    """
    vegetable_names_ar = {
        "tomato": "طماطم",
        "cucumber": "خيار",
        "onion": "بصل",
        "potato": "بطاطس",
        "carrot": "جزر",
        "eggplant": "باذنجان",
        "pepper": "فلفل",
        "lettuce": "خس",
        "zucchini": "كوسة",
        "cabbage": "ملفوف",
    }

    return GradePriceMatrix(
        id=f"vegetable_price_matrix_{vegetable_type.lower()}",
        crop_category=CropCategory.VEGETABLE,
        crop_type=vegetable_type.lower(),
        crop_type_ar=vegetable_names_ar.get(vegetable_type.lower(), vegetable_type),
        currency=currency,
        price_unit=PriceUnit.KG,
        base_price=base_price,
        premium_multiplier=1.40,  # Fresh produce commands premium
        grade_a_multiplier=1.15,
        grade_b_multiplier=1.00,
        grade_c_multiplier=0.70,  # Lower grades heavily discounted
        industrial_multiplier=0.40,  # Processing grade very cheap
        is_active=True,
        source="market",
    )


# Price matrix registry
PRICE_MATRICES: dict[str, GradePriceMatrix] = {
    "wheat": get_wheat_price_matrix(),
    "barley": get_barley_price_matrix(),
    "date_sukkari": get_date_price_matrix("sukkari"),
    "date_ajwa": get_date_price_matrix("ajwa"),
    "date_khalas": get_date_price_matrix("khalas"),
    "date_medjool": get_date_price_matrix("medjool"),
    "tomato": get_vegetable_price_matrix("tomato"),
    "cucumber": get_vegetable_price_matrix("cucumber", Decimal("2.80")),
    "onion": get_vegetable_price_matrix("onion", Decimal("2.00")),
    "potato": get_vegetable_price_matrix("potato", Decimal("2.50")),
}


# ─────────────────────────────────────────────────────────────────────────────
# Price Adjustment Rules - قواعد تعديل الأسعار
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class PriceAdjustmentRule:
    """
    Rule for adjusting price based on a parameter
    قاعدة لتعديل السعر بناءً على معيار
    """

    parameter_name: str
    parameter_name_ar: str
    adjustment_type: str  # "per_unit", "percentage", "fixed"

    # Threshold-based adjustment
    threshold_value: float  # Value above/below which adjustment applies
    threshold_direction: str  # "above" or "below"

    # Adjustment amount
    adjustment_amount: Decimal  # Amount per unit or percentage
    adjustment_unit: str  # "%", "SAR/unit", etc.

    # Limits
    max_adjustment: Decimal | None = None  # Maximum total adjustment
    min_adjustment: Decimal | None = None  # Minimum total adjustment

    # Description
    description: str = ""
    description_ar: str = ""

    def calculate_adjustment(
        self,
        actual_value: float,
        base_price: Decimal,
        quantity: float,
    ) -> tuple[Decimal, str, str]:
        """
        Calculate adjustment amount

        Returns:
            Tuple of (adjustment_amount, reason_en, reason_ar)
        """
        # Check if threshold is met
        if self.threshold_direction == "above":
            if actual_value <= self.threshold_value:
                return Decimal("0"), "", ""
            deviation = actual_value - self.threshold_value
        else:
            if actual_value >= self.threshold_value:
                return Decimal("0"), "", ""
            deviation = self.threshold_value - actual_value

        # Calculate adjustment
        if self.adjustment_type == "per_unit":
            # Adjustment per unit of deviation
            adjustment = self.adjustment_amount * Decimal(str(deviation))
            if self.threshold_direction == "above":
                adjustment = -adjustment  # Deduction for exceeding threshold
            # else: adjustment stays positive as a bonus for exceeding minimum

            # Apply to total quantity
            total_adjustment = adjustment * Decimal(str(quantity))

        elif self.adjustment_type == "percentage":
            # Percentage adjustment on base price
            pct_adjustment = self.adjustment_amount * Decimal(str(deviation))
            adjustment = base_price * pct_adjustment / Decimal("100")
            total_adjustment = adjustment * Decimal(str(quantity))

        else:  # fixed
            total_adjustment = self.adjustment_amount

        # Apply limits
        if self.max_adjustment is not None:
            total_adjustment = min(total_adjustment, self.max_adjustment)
        if self.min_adjustment is not None:
            total_adjustment = max(total_adjustment, self.min_adjustment)

        # Generate reason
        direction_word = "above" if self.threshold_direction == "above" else "below"
        direction_word_ar = "فوق" if self.threshold_direction == "above" else "تحت"

        reason_en = (
            f"{self.parameter_name}: {actual_value:.1f} ({direction_word} {self.threshold_value}), "
            f"adjustment: {total_adjustment:.2f} {self.adjustment_unit}"
        )
        reason_ar = (
            f"{self.parameter_name_ar}: {actual_value:.1f} ({direction_word_ar} {self.threshold_value})، "
            f"التعديل: {total_adjustment:.2f} {self.adjustment_unit}"
        )

        return total_adjustment, reason_en, reason_ar


# Standard adjustment rules
GRAIN_ADJUSTMENT_RULES: list[PriceAdjustmentRule] = [
    PriceAdjustmentRule(
        parameter_name="moisture",
        parameter_name_ar="الرطوبة",
        adjustment_type="per_unit",
        threshold_value=13.0,
        threshold_direction="above",
        adjustment_amount=Decimal("0.05"),
        adjustment_unit="SAR/kg/%",
        max_adjustment=Decimal("-0.50"),  # Max 0.50 SAR/kg deduction
        description="Deduction for excess moisture",
        description_ar="خصم للرطوبة الزائدة",
    ),
    PriceAdjustmentRule(
        parameter_name="protein",
        parameter_name_ar="البروتين",
        adjustment_type="per_unit",
        threshold_value=12.0,
        threshold_direction="below",
        adjustment_amount=Decimal("0.10"),
        adjustment_unit="SAR/kg/%",
        max_adjustment=Decimal("0.50"),  # Max 0.50 SAR/kg bonus
        description="Bonus for high protein content",
        description_ar="مكافأة لمحتوى بروتين مرتفع",
    ),
    PriceAdjustmentRule(
        parameter_name="foreign_matter",
        parameter_name_ar="الشوائب",
        adjustment_type="per_unit",
        threshold_value=1.0,
        threshold_direction="above",
        adjustment_amount=Decimal("0.08"),
        adjustment_unit="SAR/kg/%",
        max_adjustment=Decimal("-0.40"),
        description="Deduction for foreign matter",
        description_ar="خصم للشوائب",
    ),
]

DATE_ADJUSTMENT_RULES: list[PriceAdjustmentRule] = [
    PriceAdjustmentRule(
        parameter_name="sugar_content",
        parameter_name_ar="نسبة السكر",
        adjustment_type="per_unit",
        threshold_value=65.0,
        threshold_direction="below",
        adjustment_amount=Decimal("0.30"),
        adjustment_unit="SAR/kg/brix",
        max_adjustment=Decimal("3.00"),
        description="Bonus for high sugar content",
        description_ar="مكافأة لمحتوى سكر مرتفع",
    ),
    PriceAdjustmentRule(
        parameter_name="defects",
        parameter_name_ar="العيوب",
        adjustment_type="per_unit",
        threshold_value=5.0,
        threshold_direction="above",
        adjustment_amount=Decimal("0.50"),
        adjustment_unit="SAR/kg/%",
        max_adjustment=Decimal("-5.00"),
        description="Deduction for visual defects",
        description_ar="خصم للعيوب المرئية",
    ),
    PriceAdjustmentRule(
        parameter_name="size",
        parameter_name_ar="الحجم",
        adjustment_type="per_unit",
        threshold_value=12.0,
        threshold_direction="below",
        adjustment_amount=Decimal("0.25"),
        adjustment_unit="SAR/kg/g",
        max_adjustment=Decimal("2.00"),
        description="Bonus for large fruit size",
        description_ar="مكافأة للحجم الكبير",
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# Pricing Engine - محرك التسعير
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class PricingConfig:
    """Configuration for pricing engine | إعدادات محرك التسعير"""

    apply_parameter_adjustments: bool = True
    round_to_decimal_places: int = 2
    currency: Currency = Currency.SAR
    price_unit: PriceUnit = PriceUnit.KG

    # Market adjustments
    market_adjustment_percent: float = 0.0  # Market-wide adjustment
    seasonal_adjustment_percent: float = 0.0  # Seasonal adjustment

    # Minimum price floor
    minimum_price_per_unit: Decimal | None = None


class QualityPricingEngine:
    """
    Engine for calculating prices based on quality grades
    محرك لحساب الأسعار بناءً على درجات الجودة
    """

    def __init__(
        self,
        price_matrix: GradePriceMatrix | None = None,
        config: PricingConfig | None = None,
    ):
        """Initialize pricing engine"""
        self.price_matrix = price_matrix
        self.config = config or PricingConfig()
        self.adjustment_rules: list[PriceAdjustmentRule] = []

    def set_price_matrix(self, matrix: GradePriceMatrix) -> None:
        """Set price matrix to use"""
        self.price_matrix = matrix

    def set_adjustment_rules(self, rules: list[PriceAdjustmentRule]) -> None:
        """Set adjustment rules"""
        self.adjustment_rules = rules

    def get_price_matrix_for_crop(self, crop_type: str, variety: str | None = None) -> GradePriceMatrix | None:
        """Get price matrix for a crop type"""
        # Try with variety first
        if variety:
            key = f"{crop_type.lower()}_{variety.lower()}"
            matrix = PRICE_MATRICES.get(key)
            if matrix:
                return matrix

        # Fall back to crop type only
        return PRICE_MATRICES.get(crop_type.lower())

    def calculate_price(
        self,
        grade: QualityGrade,
        quantity: float,
        test_values: dict[str, float] | None = None,
        price_matrix: GradePriceMatrix | None = None,
    ) -> PriceCalculation:
        """
        Calculate price for a given grade and quantity

        Args:
            grade: Quality grade
            quantity: Quantity in price unit (kg, ton, etc.)
            test_values: Optional dict of parameter values for adjustments
            price_matrix: Optional price matrix override

        Returns:
            PriceCalculation with detailed breakdown
        """
        matrix = price_matrix or self.price_matrix
        if not matrix:
            raise ValueError("No price matrix provided")

        # Get base and grade-adjusted prices
        base_price = matrix.base_price
        grade_price = matrix.get_price_for_grade(grade)

        # Start calculation
        calc = PriceCalculation(
            id=str(uuid.uuid4()),
            overall_grade=grade,
            price_matrix_id=matrix.id,
            base_price_per_unit=base_price,
            grade_price_per_unit=grade_price,
            currency=matrix.currency,
            price_unit=matrix.price_unit,
            quantity=quantity,
            quantity_unit=matrix.price_unit.value,
        )

        # Calculate subtotal
        calc.subtotal = grade_price * Decimal(str(quantity))

        # Apply parameter adjustments if enabled
        adjustments: list[dict[str, Any]] = []

        if self.config.apply_parameter_adjustments and test_values:
            # Apply standard adjustments from price matrix
            if test_values.get("moisture") is not None:
                moisture_threshold = 13.0  # Standard threshold
                if test_values["moisture"] > moisture_threshold:
                    excess = test_values["moisture"] - moisture_threshold
                    adjustment = -matrix.moisture_adjustment_per_percent * Decimal(str(excess)) * Decimal(str(quantity))
                    adjustments.append(
                        {
                            "reason": f"Moisture above {moisture_threshold}%: {test_values['moisture']:.1f}%",
                            "reason_ar": f"الرطوبة فوق {moisture_threshold}%: {test_values['moisture']:.1f}%",
                            "amount": float(adjustment),
                        }
                    )

            if test_values.get("protein") is not None:
                protein_threshold = 12.0  # Standard threshold
                if test_values["protein"] > protein_threshold:
                    excess = test_values["protein"] - protein_threshold
                    adjustment = matrix.protein_bonus_per_percent * Decimal(str(excess)) * Decimal(str(quantity))
                    adjustments.append(
                        {
                            "reason": f"Protein above {protein_threshold}%: {test_values['protein']:.1f}%",
                            "reason_ar": f"البروتين فوق {protein_threshold}%: {test_values['protein']:.1f}%",
                            "amount": float(adjustment),
                        }
                    )

            if test_values.get("foreign_matter") is not None:
                fm_threshold = 1.0  # Standard threshold
                if test_values["foreign_matter"] > fm_threshold:
                    excess = test_values["foreign_matter"] - fm_threshold
                    adjustment = (
                        -matrix.foreign_matter_deduction_per_percent * Decimal(str(excess)) * Decimal(str(quantity))
                    )
                    adjustments.append(
                        {
                            "reason": f"Foreign matter above {fm_threshold}%: {test_values['foreign_matter']:.1f}%",
                            "reason_ar": f"الشوائب فوق {fm_threshold}%: {test_values['foreign_matter']:.1f}%",
                            "amount": float(adjustment),
                        }
                    )

            # Apply custom adjustment rules
            for rule in self.adjustment_rules:
                if rule.parameter_name in test_values:
                    adj_amount, reason_en, reason_ar = rule.calculate_adjustment(
                        test_values[rule.parameter_name], grade_price, quantity
                    )
                    if adj_amount != 0:
                        adjustments.append(
                            {
                                "reason": reason_en,
                                "reason_ar": reason_ar,
                                "amount": float(adj_amount),
                            }
                        )

        # Apply market and seasonal adjustments
        if self.config.market_adjustment_percent != 0:
            market_adj = calc.subtotal * Decimal(str(self.config.market_adjustment_percent / 100))
            adjustments.append(
                {
                    "reason": f"Market adjustment: {self.config.market_adjustment_percent:+.1f}%",
                    "reason_ar": f"تعديل السوق: {self.config.market_adjustment_percent:+.1f}%",
                    "amount": float(market_adj),
                }
            )

        if self.config.seasonal_adjustment_percent != 0:
            seasonal_adj = calc.subtotal * Decimal(str(self.config.seasonal_adjustment_percent / 100))
            adjustments.append(
                {
                    "reason": f"Seasonal adjustment: {self.config.seasonal_adjustment_percent:+.1f}%",
                    "reason_ar": f"تعديل موسمي: {self.config.seasonal_adjustment_percent:+.1f}%",
                    "amount": float(seasonal_adj),
                }
            )

        # Store adjustments and calculate totals
        calc.adjustments = adjustments
        calc.total_adjustments = sum(Decimal(str(adj["amount"])) for adj in adjustments)

        # Calculate final price
        calc.final_price = calc.subtotal + calc.total_adjustments

        # Apply minimum price floor if configured
        if self.config.minimum_price_per_unit is not None:
            min_total = self.config.minimum_price_per_unit * Decimal(str(quantity))
            if calc.final_price < min_total:
                calc.final_price = min_total
                calc.adjustments.append(
                    {
                        "reason": "Minimum price floor applied",
                        "reason_ar": "تم تطبيق الحد الأدنى للسعر",
                        "amount": float(min_total - calc.subtotal - calc.total_adjustments),
                    }
                )

        # Round to configured decimal places
        calc.final_price = calc.final_price.quantize(
            Decimal(f"0.{'0' * self.config.round_to_decimal_places}"),
            rounding=ROUND_HALF_UP,
        )

        # Calculate per-unit final price
        if quantity > 0:
            calc.final_price_per_unit = (calc.final_price / Decimal(str(quantity))).quantize(
                Decimal(f"0.{'0' * self.config.round_to_decimal_places}"),
                rounding=ROUND_HALF_UP,
            )

        # Calculate comparison percentages
        if base_price > 0:
            calc.vs_base_price_percent = float((calc.final_price_per_unit - base_price) / base_price * 100)

        calc.calculated_at = datetime.now(UTC)

        return calc

    def calculate_price_for_test_record(
        self,
        test_record: QualityTestRecord,
        quantity: float,
        price_matrix: GradePriceMatrix | None = None,
    ) -> PriceCalculation:
        """
        Calculate price from a quality test record

        Args:
            test_record: Quality test record with grade and test values
            quantity: Quantity to price
            price_matrix: Optional price matrix override

        Returns:
            PriceCalculation with detailed breakdown
        """
        # Get appropriate price matrix
        matrix = price_matrix or self.get_price_matrix_for_crop(test_record.crop_type, test_record.variety)
        if not matrix:
            matrix = self.price_matrix

        if not matrix:
            raise ValueError(f"No price matrix found for crop: {test_record.crop_type}")

        # Extract test values
        test_values: dict[str, float] = {}
        if test_record.moisture_percent is not None:
            test_values["moisture"] = test_record.moisture_percent
        if test_record.protein_percent is not None:
            test_values["protein"] = test_record.protein_percent
        if test_record.sugar_brix is not None:
            test_values["sugar_content"] = test_record.sugar_brix
        if test_record.foreign_matter_percent is not None:
            test_values["foreign_matter"] = test_record.foreign_matter_percent
        if test_record.defect_percent is not None:
            test_values["defects"] = test_record.defect_percent

        # Calculate price
        calc = self.calculate_price(
            grade=test_record.overall_grade,
            quantity=quantity,
            test_values=test_values,
            price_matrix=matrix,
        )

        # Link to test record
        calc.batch_id = test_record.batch_id
        calc.test_record_id = test_record.id
        calc.grade_score = test_record.grade_score

        return calc

    def compare_prices_by_grade(
        self,
        quantity: float,
        price_matrix: GradePriceMatrix | None = None,
    ) -> dict[str, dict[str, Any]]:
        """
        Generate price comparison across all grades

        Args:
            quantity: Quantity to price
            price_matrix: Price matrix to use

        Returns:
            Dictionary of grade -> price information
        """
        matrix = price_matrix or self.price_matrix
        if not matrix:
            raise ValueError("No price matrix provided")

        comparison: dict[str, dict[str, Any]] = {}

        for grade in [
            QualityGrade.PREMIUM,
            QualityGrade.GRADE_A,
            QualityGrade.GRADE_B,
            QualityGrade.GRADE_C,
            QualityGrade.INDUSTRIAL,
        ]:
            grade_price = matrix.get_price_for_grade(grade)
            total = grade_price * Decimal(str(quantity))

            # Calculate difference from Grade B (standard)
            base_total = matrix.base_price * Decimal(str(quantity))
            difference = total - base_total
            difference_percent = float((total - base_total) / base_total * 100) if base_total > 0 else 0

            comparison[grade.value] = {
                "grade": grade.value,
                "grade_ar": {
                    "premium": "ممتاز",
                    "grade_a": "درجة أولى",
                    "grade_b": "درجة ثانية",
                    "grade_c": "درجة ثالثة",
                    "industrial": "صناعي",
                }.get(grade.value, grade.value),
                "price_per_unit": str(grade_price),
                "total_price": str(total),
                "currency": matrix.currency.value,
                "difference_from_base": str(difference),
                "difference_percent": difference_percent,
            }

        return comparison


# ─────────────────────────────────────────────────────────────────────────────
# Price Calculator Utilities - أدوات حساب السعر
# ─────────────────────────────────────────────────────────────────────────────


def calculate_quick_price(
    crop_type: str,
    grade: QualityGrade,
    quantity_kg: float,
    variety: str | None = None,
) -> tuple[Decimal, Currency]:
    """
    Quick price calculation utility

    Args:
        crop_type: Type of crop (wheat, barley, date, tomato, etc.)
        grade: Quality grade
        quantity_kg: Quantity in kilograms
        variety: Optional variety for dates

    Returns:
        Tuple of (total_price, currency)
    """
    engine = QualityPricingEngine()
    matrix = engine.get_price_matrix_for_crop(crop_type, variety)

    if not matrix:
        raise ValueError(f"No price matrix found for crop: {crop_type}")

    calc = engine.calculate_price(grade, quantity_kg, price_matrix=matrix)
    return calc.final_price, calc.currency


def get_grade_price_breakdown(
    crop_type: str,
    quantity_kg: float,
    variety: str | None = None,
) -> list[dict[str, Any]]:
    """
    Get price breakdown for all grades

    Args:
        crop_type: Type of crop
        quantity_kg: Quantity in kilograms
        variety: Optional variety

    Returns:
        List of price information for each grade
    """
    engine = QualityPricingEngine()
    matrix = engine.get_price_matrix_for_crop(crop_type, variety)

    if not matrix:
        raise ValueError(f"No price matrix found for crop: {crop_type}")

    comparison = engine.compare_prices_by_grade(quantity_kg, matrix)
    return list(comparison.values())


def estimate_value_improvement(
    current_grade: QualityGrade,
    target_grade: QualityGrade,
    crop_type: str,
    quantity_kg: float,
    variety: str | None = None,
) -> dict[str, Any]:
    """
    Estimate potential value improvement from grade upgrade

    Args:
        current_grade: Current quality grade
        target_grade: Target quality grade
        crop_type: Type of crop
        quantity_kg: Quantity in kilograms
        variety: Optional variety

    Returns:
        Dictionary with improvement analysis
    """
    engine = QualityPricingEngine()
    matrix = engine.get_price_matrix_for_crop(crop_type, variety)

    if not matrix:
        raise ValueError(f"No price matrix found for crop: {crop_type}")

    current_price = matrix.get_price_for_grade(current_grade)
    target_price = matrix.get_price_for_grade(target_grade)

    current_total = current_price * Decimal(str(quantity_kg))
    target_total = target_price * Decimal(str(quantity_kg))

    improvement = target_total - current_total
    improvement_percent = float(improvement / current_total * 100) if current_total > 0 else 0

    return {
        "current_grade": current_grade.value,
        "current_grade_ar": {
            "premium": "ممتاز",
            "grade_a": "درجة أولى",
            "grade_b": "درجة ثانية",
            "grade_c": "درجة ثالثة",
            "industrial": "صناعي",
        }.get(current_grade.value, current_grade.value),
        "target_grade": target_grade.value,
        "target_grade_ar": {
            "premium": "ممتاز",
            "grade_a": "درجة أولى",
            "grade_b": "درجة ثانية",
            "grade_c": "درجة ثالثة",
            "industrial": "صناعي",
        }.get(target_grade.value, target_grade.value),
        "current_price_per_kg": str(current_price),
        "target_price_per_kg": str(target_price),
        "current_total": str(current_total),
        "target_total": str(target_total),
        "potential_improvement": str(improvement),
        "improvement_percent": improvement_percent,
        "currency": matrix.currency.value,
        "recommendation": (
            f"Improving from {current_grade.value} to {target_grade.value} could increase value by "
            f"{improvement:.2f} {matrix.currency.value} ({improvement_percent:.1f}%)"
        ),
        "recommendation_ar": (
            f"تحسين الدرجة من {current_grade.value} إلى {target_grade.value} قد يزيد القيمة بمقدار "
            f"{improvement:.2f} {matrix.currency.value} ({improvement_percent:.1f}%)"
        ),
    }
