"""
Fertilizer Application Rate Calculator - حاسبة معدلات التسميد

Calculate application rates, costs, and environmental compliance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from .models import (
    ApplicationMethod,
    ComplianceLevel,
    CostAnalysis,
    EnvironmentalCompliance,
    Fertilizer,
    FertilizerApplication,
    NutrientBalance,
    NutrientStatus,
    SoilTest,
)


@dataclass
class ApplicationRateResult:
    """
    Result of application rate calculation - نتيجة حساب معدل التطبيق
    """

    fertilizer_name: str
    fertilizer_name_ar: str
    npk_ratio: str

    # Calculated rates
    rate_kg_per_ha: float
    rate_kg_per_dunum: float  # 1 dunum = 0.1 hectare (common in Middle East)
    rate_kg_total: float
    area_ha: float

    # Nutrients provided
    n_kg_per_ha: float
    p2o5_kg_per_ha: float
    k2o_kg_per_ha: float

    # Cost
    cost_per_ha: Decimal = Decimal("0.00")
    cost_total: Decimal = Decimal("0.00")
    currency: str = "SAR"

    # Application guidance
    method: ApplicationMethod = ApplicationMethod.BROADCAST
    timing_en: str = ""
    timing_ar: str = ""
    notes_en: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "fertilizer_name": self.fertilizer_name,
            "fertilizer_name_ar": self.fertilizer_name_ar,
            "npk_ratio": self.npk_ratio,
            "rate_kg_per_ha": self.rate_kg_per_ha,
            "rate_kg_per_dunum": self.rate_kg_per_dunum,
            "rate_kg_total": self.rate_kg_total,
            "area_ha": self.area_ha,
            "nutrients_per_ha": {
                "N": self.n_kg_per_ha,
                "P2O5": self.p2o5_kg_per_ha,
                "K2O": self.k2o_kg_per_ha,
            },
            "cost_per_ha": float(self.cost_per_ha),
            "cost_total": float(self.cost_total),
            "method": self.method.value,
        }


@dataclass
class BlendCalculation:
    """
    Custom fertilizer blend calculation - حساب خلطة سماد مخصصة
    """

    target_n_kg_ha: float
    target_p_kg_ha: float
    target_k_kg_ha: float

    # Components
    components: list[dict] = field(default_factory=list)

    # Totals
    total_n_kg_ha: float = 0.0
    total_p_kg_ha: float = 0.0
    total_k_kg_ha: float = 0.0

    # Variance from target
    n_variance_percent: float = 0.0
    p_variance_percent: float = 0.0
    k_variance_percent: float = 0.0

    # Cost
    total_cost_per_ha: Decimal = Decimal("0.00")
    currency: str = "SAR"

    # Warnings
    warnings_en: list[str] = field(default_factory=list)
    warnings_ar: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "target": {
                "N": self.target_n_kg_ha,
                "P2O5": self.target_p_kg_ha,
                "K2O": self.target_k_kg_ha,
            },
            "actual": {
                "N": self.total_n_kg_ha,
                "P2O5": self.total_p_kg_ha,
                "K2O": self.total_k_kg_ha,
            },
            "variance_percent": {
                "N": self.n_variance_percent,
                "P2O5": self.p_variance_percent,
                "K2O": self.k_variance_percent,
            },
            "components": self.components,
            "total_cost_per_ha": float(self.total_cost_per_ha),
            "warnings": self.warnings_en,
        }


class FertilizerCalculator:
    """
    Calculator for fertilizer application rates and costs
    حاسبة معدلات وتكاليف التسميد
    """

    # Common fertilizer compositions
    STANDARD_FERTILIZERS: dict[str, dict] = {
        "urea": {
            "name": "Urea 46%",
            "name_ar": "يوريا 46%",
            "N": 46.0,
            "P2O5": 0.0,
            "K2O": 0.0,
            "price_per_kg": Decimal("2.50"),
        },
        "dap": {
            "name": "DAP (18-46-0)",
            "name_ar": "داب (18-46-0)",
            "N": 18.0,
            "P2O5": 46.0,
            "K2O": 0.0,
            "price_per_kg": Decimal("3.20"),
        },
        "map": {
            "name": "MAP (11-52-0)",
            "name_ar": "ماب (11-52-0)",
            "N": 11.0,
            "P2O5": 52.0,
            "K2O": 0.0,
            "price_per_kg": Decimal("3.50"),
        },
        "mop": {
            "name": "MOP (0-0-60)",
            "name_ar": "بوتاسيوم كلوريد (0-0-60)",
            "N": 0.0,
            "P2O5": 0.0,
            "K2O": 60.0,
            "price_per_kg": Decimal("2.80"),
        },
        "sop": {
            "name": "SOP (0-0-50)",
            "name_ar": "بوتاسيوم سلفات (0-0-50)",
            "N": 0.0,
            "P2O5": 0.0,
            "K2O": 50.0,
            "price_per_kg": Decimal("4.00"),
        },
        "npk_20_20_20": {
            "name": "NPK 20-20-20",
            "name_ar": "مركب 20-20-20",
            "N": 20.0,
            "P2O5": 20.0,
            "K2O": 20.0,
            "price_per_kg": Decimal("3.80"),
        },
        "npk_15_15_15": {
            "name": "NPK 15-15-15",
            "name_ar": "مركب 15-15-15",
            "N": 15.0,
            "P2O5": 15.0,
            "K2O": 15.0,
            "price_per_kg": Decimal("3.50"),
        },
        "ammonium_sulfate": {
            "name": "Ammonium Sulfate (21-0-0-24S)",
            "name_ar": "سلفات أمونيوم (21-0-0-24S)",
            "N": 21.0,
            "P2O5": 0.0,
            "K2O": 0.0,
            "S": 24.0,
            "price_per_kg": Decimal("2.00"),
        },
        "calcium_nitrate": {
            "name": "Calcium Nitrate (15.5-0-0-19Ca)",
            "name_ar": "نترات كالسيوم (15.5-0-0-19Ca)",
            "N": 15.5,
            "P2O5": 0.0,
            "K2O": 0.0,
            "Ca": 19.0,
            "price_per_kg": Decimal("3.00"),
        },
        "compost": {
            "name": "Organic Compost",
            "name_ar": "سماد عضوي (كمبوست)",
            "N": 1.5,
            "P2O5": 1.0,
            "K2O": 1.0,
            "price_per_kg": Decimal("0.50"),
        },
        "chicken_manure": {
            "name": "Chicken Manure (Dried)",
            "name_ar": "سماد دجاج (مجفف)",
            "N": 3.0,
            "P2O5": 2.5,
            "K2O": 2.0,
            "price_per_kg": Decimal("0.80"),
        },
    }

    # Environmental limits (kg/ha/year)
    ENVIRONMENTAL_LIMITS: dict[str, float] = {
        "N_max_annual": 200.0,  # Maximum nitrogen per year
        "P_max_annual": 50.0,  # Maximum phosphorus per year
        "buffer_zone_m": 10.0,  # Minimum distance from water bodies
    }

    def __init__(self):
        """Initialize calculator."""
        self.fertilizers = self.STANDARD_FERTILIZERS.copy()

    def calculate_rate_for_nutrient(
        self,
        fertilizer_code: str,
        target_nutrient: str,
        target_kg_per_ha: float,
        area_ha: float,
    ) -> ApplicationRateResult:
        """
        Calculate fertilizer rate to supply a target nutrient amount.

        Args:
            fertilizer_code: Code of fertilizer (e.g., 'urea', 'dap')
            target_nutrient: Target nutrient ('N', 'P2O5', 'K2O')
            target_kg_per_ha: Target kg of nutrient per hectare
            area_ha: Field area in hectares

        Returns:
            ApplicationRateResult with calculated rates
        """
        fert = self.fertilizers.get(fertilizer_code)
        if not fert:
            raise ValueError(f"Unknown fertilizer: {fertilizer_code}")

        nutrient_content = fert.get(target_nutrient, 0)
        if nutrient_content <= 0:
            raise ValueError(f"Fertilizer {fertilizer_code} does not contain {target_nutrient}")

        # Calculate rate
        rate_kg_ha = (target_kg_per_ha / nutrient_content) * 100
        rate_kg_total = rate_kg_ha * area_ha

        # Calculate all nutrients provided
        n_kg_ha = rate_kg_ha * fert.get("N", 0) / 100
        p_kg_ha = rate_kg_ha * fert.get("P2O5", 0) / 100
        k_kg_ha = rate_kg_ha * fert.get("K2O", 0) / 100

        # Calculate cost
        price_per_kg = fert.get("price_per_kg", Decimal("0.00"))
        cost_per_ha = price_per_kg * Decimal(str(rate_kg_ha))
        cost_total = price_per_kg * Decimal(str(rate_kg_total))

        npk_ratio = f"{int(fert.get('N', 0))}-{int(fert.get('P2O5', 0))}-{int(fert.get('K2O', 0))}"

        return ApplicationRateResult(
            fertilizer_name=fert["name"],
            fertilizer_name_ar=fert["name_ar"],
            npk_ratio=npk_ratio,
            rate_kg_per_ha=round(rate_kg_ha, 1),
            rate_kg_per_dunum=round(rate_kg_ha / 10, 2),  # 1 dunum = 0.1 ha
            rate_kg_total=round(rate_kg_total, 1),
            area_ha=area_ha,
            n_kg_per_ha=round(n_kg_ha, 1),
            p2o5_kg_per_ha=round(p_kg_ha, 1),
            k2o_kg_per_ha=round(k_kg_ha, 1),
            cost_per_ha=cost_per_ha,
            cost_total=cost_total,
        )

    def calculate_rate_from_fertilizer(
        self,
        fertilizer: Fertilizer,
        target_nutrient: str,
        target_kg_per_ha: float,
        area_ha: float,
    ) -> ApplicationRateResult:
        """
        Calculate rate using a Fertilizer object.

        Args:
            fertilizer: Fertilizer product
            target_nutrient: Target nutrient ('N', 'P2O5', 'K2O')
            target_kg_per_ha: Target kg of nutrient per hectare
            area_ha: Field area in hectares

        Returns:
            ApplicationRateResult with calculated rates
        """
        composition = fertilizer.composition

        # Get nutrient content
        nutrient_map = {
            "N": composition.nitrogen_n,
            "P2O5": composition.phosphorus_p2o5,
            "K2O": composition.potassium_k2o,
        }
        nutrient_content = nutrient_map.get(target_nutrient, 0)

        if nutrient_content <= 0:
            raise ValueError(f"Fertilizer {fertilizer.name} does not contain {target_nutrient}")

        # Calculate rate
        rate_kg_ha = (target_kg_per_ha / nutrient_content) * 100
        rate_kg_total = rate_kg_ha * area_ha

        # Calculate all nutrients provided
        n_kg_ha = rate_kg_ha * composition.nitrogen_n / 100
        p_kg_ha = rate_kg_ha * composition.phosphorus_p2o5 / 100
        k_kg_ha = rate_kg_ha * composition.potassium_k2o / 100

        # Calculate cost
        cost_per_ha = fertilizer.unit_price * Decimal(str(rate_kg_ha / fertilizer.unit_size_kg))
        cost_total = cost_per_ha * Decimal(str(area_ha))

        return ApplicationRateResult(
            fertilizer_name=fertilizer.name,
            fertilizer_name_ar=fertilizer.name_ar,
            npk_ratio=composition.npk_ratio,
            rate_kg_per_ha=round(rate_kg_ha, 1),
            rate_kg_per_dunum=round(rate_kg_ha / 10, 2),
            rate_kg_total=round(rate_kg_total, 1),
            area_ha=area_ha,
            n_kg_per_ha=round(n_kg_ha, 1),
            p2o5_kg_per_ha=round(p_kg_ha, 1),
            k2o_kg_per_ha=round(k_kg_ha, 1),
            cost_per_ha=cost_per_ha,
            cost_total=cost_total,
        )

    def calculate_blend(
        self,
        target_n_kg_ha: float,
        target_p_kg_ha: float,
        target_k_kg_ha: float,
        available_fertilizers: list[str] | None = None,
    ) -> BlendCalculation:
        """
        Calculate optimal fertilizer blend to meet nutrient targets.

        Uses simple prioritization: P first (DAP), then K (MOP), then N (Urea).

        Args:
            target_n_kg_ha: Target nitrogen kg/ha
            target_p_kg_ha: Target P2O5 kg/ha
            target_k_kg_ha: Target K2O kg/ha
            available_fertilizers: List of available fertilizer codes

        Returns:
            BlendCalculation with component rates
        """
        if available_fertilizers is None:
            available_fertilizers = ["dap", "mop", "urea"]

        blend = BlendCalculation(
            target_n_kg_ha=target_n_kg_ha,
            target_p_kg_ha=target_p_kg_ha,
            target_k_kg_ha=target_k_kg_ha,
        )

        remaining_n = target_n_kg_ha
        remaining_p = target_p_kg_ha
        remaining_k = target_k_kg_ha

        # Step 1: Apply P source (DAP or MAP)
        if remaining_p > 0 and ("dap" in available_fertilizers or "map" in available_fertilizers):
            p_source = "dap" if "dap" in available_fertilizers else "map"
            fert = self.fertilizers[p_source]
            rate = (remaining_p / fert["P2O5"]) * 100

            n_from_p_source = rate * fert["N"] / 100

            blend.components.append(
                {
                    "fertilizer": fert["name"],
                    "fertilizer_ar": fert["name_ar"],
                    "rate_kg_ha": round(rate, 1),
                    "N_kg_ha": round(n_from_p_source, 1),
                    "P2O5_kg_ha": round(remaining_p, 1),
                    "K2O_kg_ha": 0,
                    "cost_per_ha": float(fert["price_per_kg"] * Decimal(str(rate))),
                }
            )

            blend.total_p_kg_ha += remaining_p
            blend.total_n_kg_ha += n_from_p_source
            remaining_n -= n_from_p_source
            remaining_p = 0
            blend.total_cost_per_ha += fert["price_per_kg"] * Decimal(str(rate))

        # Step 2: Apply K source (MOP or SOP)
        if remaining_k > 0 and ("mop" in available_fertilizers or "sop" in available_fertilizers):
            k_source = "mop" if "mop" in available_fertilizers else "sop"
            fert = self.fertilizers[k_source]
            rate = (remaining_k / fert["K2O"]) * 100

            blend.components.append(
                {
                    "fertilizer": fert["name"],
                    "fertilizer_ar": fert["name_ar"],
                    "rate_kg_ha": round(rate, 1),
                    "N_kg_ha": 0,
                    "P2O5_kg_ha": 0,
                    "K2O_kg_ha": round(remaining_k, 1),
                    "cost_per_ha": float(fert["price_per_kg"] * Decimal(str(rate))),
                }
            )

            blend.total_k_kg_ha += remaining_k
            remaining_k = 0
            blend.total_cost_per_ha += fert["price_per_kg"] * Decimal(str(rate))

        # Step 3: Apply N source (Urea)
        if remaining_n > 0 and "urea" in available_fertilizers:
            fert = self.fertilizers["urea"]
            rate = (remaining_n / fert["N"]) * 100

            blend.components.append(
                {
                    "fertilizer": fert["name"],
                    "fertilizer_ar": fert["name_ar"],
                    "rate_kg_ha": round(rate, 1),
                    "N_kg_ha": round(remaining_n, 1),
                    "P2O5_kg_ha": 0,
                    "K2O_kg_ha": 0,
                    "cost_per_ha": float(fert["price_per_kg"] * Decimal(str(rate))),
                }
            )

            blend.total_n_kg_ha += remaining_n
            remaining_n = 0
            blend.total_cost_per_ha += fert["price_per_kg"] * Decimal(str(rate))

        # Calculate variance
        if target_n_kg_ha > 0:
            blend.n_variance_percent = ((blend.total_n_kg_ha - target_n_kg_ha) / target_n_kg_ha) * 100
        if target_p_kg_ha > 0:
            blend.p_variance_percent = ((blend.total_p_kg_ha - target_p_kg_ha) / target_p_kg_ha) * 100
        if target_k_kg_ha > 0:
            blend.k_variance_percent = ((blend.total_k_kg_ha - target_k_kg_ha) / target_k_kg_ha) * 100

        # Add warnings if there are remaining unfulfilled needs
        if remaining_n > 5:
            blend.warnings_en.append(f"Unable to fully meet N requirement. {remaining_n:.1f} kg/ha short.")
            blend.warnings_ar.append(f"لم يتم تلبية احتياج النيتروجين بالكامل. نقص {remaining_n:.1f} كجم/هكتار.")
        if remaining_p > 5:
            blend.warnings_en.append(f"Unable to fully meet P2O5 requirement. {remaining_p:.1f} kg/ha short.")
            blend.warnings_ar.append(f"لم يتم تلبية احتياج الفسفور بالكامل. نقص {remaining_p:.1f} كجم/هكتار.")
        if remaining_k > 5:
            blend.warnings_en.append(f"Unable to fully meet K2O requirement. {remaining_k:.1f} kg/ha short.")
            blend.warnings_ar.append(f"لم يتم تلبية احتياج البوتاسيوم بالكامل. نقص {remaining_k:.1f} كجم/هكتار.")

        return blend

    def check_environmental_compliance(
        self,
        field_id: str,
        applications: list[FertilizerApplication],
        water_body_distance_m: float | None = None,
    ) -> EnvironmentalCompliance:
        """
        Check environmental compliance for fertilizer applications.

        Args:
            field_id: Field ID
            applications: List of fertilizer applications this season
            water_body_distance_m: Distance to nearest water body

        Returns:
            EnvironmentalCompliance assessment
        """
        compliance = EnvironmentalCompliance(field_id=field_id)

        # Sum up total applications
        for app in applications:
            compliance.total_n_applied_kg_ha += app.nitrogen_applied_kg_ha
            compliance.total_p_applied_kg_ha += app.phosphorus_applied_kg_ha

        # Check N compliance
        if compliance.total_n_applied_kg_ha > self.ENVIRONMENTAL_LIMITS["N_max_annual"]:
            compliance.n_compliance = ComplianceLevel.VIOLATION
            compliance.violations_en.append(
                f"Total nitrogen applied ({compliance.total_n_applied_kg_ha:.1f} kg/ha) "
                f"exceeds annual limit ({self.ENVIRONMENTAL_LIMITS['N_max_annual']:.0f} kg/ha)"
            )
            compliance.violations_ar.append(
                f"إجمالي النيتروجين المطبق ({compliance.total_n_applied_kg_ha:.1f} كجم/هكتار) "
                f"يتجاوز الحد السنوي ({self.ENVIRONMENTAL_LIMITS['N_max_annual']:.0f} كجم/هكتار)"
            )
        elif compliance.total_n_applied_kg_ha > self.ENVIRONMENTAL_LIMITS["N_max_annual"] * 0.8:
            compliance.n_compliance = ComplianceLevel.WARNING
            compliance.recommendations_en.append(
                "Approaching nitrogen application limit. Consider reducing future applications."
            )
            compliance.recommendations_ar.append("اقتراب من حد تطبيق النيتروجين. ينصح بتقليل التطبيقات المستقبلية.")

        # Check P compliance
        if compliance.total_p_applied_kg_ha > self.ENVIRONMENTAL_LIMITS["P_max_annual"]:
            compliance.p_compliance = ComplianceLevel.VIOLATION
            compliance.violations_en.append(
                f"Total phosphorus applied ({compliance.total_p_applied_kg_ha:.1f} kg/ha) "
                f"exceeds annual limit ({self.ENVIRONMENTAL_LIMITS['P_max_annual']:.0f} kg/ha)"
            )
            compliance.violations_ar.append(
                f"إجمالي الفسفور المطبق ({compliance.total_p_applied_kg_ha:.1f} كجم/هكتار) "
                f"يتجاوز الحد السنوي ({self.ENVIRONMENTAL_LIMITS['P_max_annual']:.0f} كجم/هكتار)"
            )
        elif compliance.total_p_applied_kg_ha > self.ENVIRONMENTAL_LIMITS["P_max_annual"] * 0.8:
            compliance.p_compliance = ComplianceLevel.WARNING

        # Check buffer zone compliance
        if water_body_distance_m is not None:
            compliance.water_body_distance_m = water_body_distance_m
            compliance.required_buffer_m = self.ENVIRONMENTAL_LIMITS["buffer_zone_m"]

            if water_body_distance_m < compliance.required_buffer_m:
                compliance.buffer_compliance = ComplianceLevel.VIOLATION
                compliance.violations_en.append(
                    f"Field is within {water_body_distance_m:.1f}m of water body. "
                    f"Minimum buffer zone is {compliance.required_buffer_m:.0f}m."
                )
                compliance.violations_ar.append(
                    f"الحقل على بعد {water_body_distance_m:.1f}م من مصدر المياه. "
                    f"المنطقة العازلة الأدنى هي {compliance.required_buffer_m:.0f}م."
                )
                compliance.recommendations_en.append(
                    "Apply fertilizer only outside buffer zone or use precision application."
                )
                compliance.recommendations_ar.append("طبق السماد فقط خارج المنطقة العازلة أو استخدم التطبيق الدقيق.")

        # Determine overall status
        if (
            compliance.n_compliance == ComplianceLevel.VIOLATION
            or compliance.p_compliance == ComplianceLevel.VIOLATION
            or compliance.buffer_compliance == ComplianceLevel.VIOLATION
        ):
            compliance.overall_status = ComplianceLevel.VIOLATION
        elif compliance.n_compliance == ComplianceLevel.WARNING or compliance.p_compliance == ComplianceLevel.WARNING:
            compliance.overall_status = ComplianceLevel.WARNING

        return compliance

    def calculate_cost_analysis(
        self,
        field_id: str,
        season: str,
        area_ha: float,
        applications: list[FertilizerApplication],
        previous_season_cost: Decimal | None = None,
    ) -> CostAnalysis:
        """
        Calculate cost analysis for fertilizer applications.

        Args:
            field_id: Field ID
            season: Season identifier
            area_ha: Field area in hectares
            applications: List of fertilizer applications
            previous_season_cost: Previous season total cost for comparison

        Returns:
            CostAnalysis with detailed breakdown
        """
        analysis = CostAnalysis(
            field_id=field_id,
            season=season,
            area_ha=area_ha,
        )

        total_n = 0.0
        total_p = 0.0
        total_k = 0.0
        costs_by_fertilizer: dict[str, dict] = {}

        for app in applications:
            analysis.total_fertilizer_cost += app.total_cost
            total_n += app.nitrogen_applied_kg_ha * app.area_treated_ha
            total_p += app.phosphorus_applied_kg_ha * app.area_treated_ha
            total_k += app.potassium_applied_kg_ha * app.area_treated_ha

            # Track by fertilizer
            fert_id = app.fertilizer_id
            if fert_id not in costs_by_fertilizer:
                costs_by_fertilizer[fert_id] = {
                    "quantity_kg": 0,
                    "cost": Decimal("0.00"),
                }
            costs_by_fertilizer[fert_id]["quantity_kg"] += app.total_quantity_kg
            costs_by_fertilizer[fert_id]["cost"] += app.total_cost

        analysis.total_cost = analysis.total_fertilizer_cost + analysis.total_application_cost
        analysis.cost_per_ha = analysis.total_cost / Decimal(str(area_ha)) if area_ha > 0 else Decimal("0.00")

        # Cost per kg nutrient
        if total_n > 0:
            analysis.cost_per_kg_n = analysis.total_fertilizer_cost / Decimal(str(total_n))
        if total_p > 0:
            analysis.cost_per_kg_p = analysis.total_fertilizer_cost / Decimal(str(total_p))
        if total_k > 0:
            analysis.cost_per_kg_k = analysis.total_fertilizer_cost / Decimal(str(total_k))

        analysis.costs_by_fertilizer = costs_by_fertilizer

        # Compare with previous season
        if previous_season_cost and previous_season_cost > 0:
            analysis.previous_season_cost = previous_season_cost
            change = ((analysis.total_cost - previous_season_cost) / previous_season_cost) * 100
            analysis.cost_change_percent = float(change)

            if change > 10:
                analysis.savings_opportunities_en.append(
                    f"Costs increased {change:.1f}% from previous season. "
                    "Consider soil testing to optimize application rates."
                )
                analysis.savings_opportunities_ar.append(
                    f"ارتفعت التكاليف {change:.1f}% عن الموسم السابق. ينصح بإجراء تحليل تربة لتحسين معدلات التطبيق."
                )

        # Identify savings opportunities
        if analysis.cost_per_kg_n > Decimal("6.00"):
            analysis.savings_opportunities_en.append("Consider using more cost-effective nitrogen sources like Urea.")
            analysis.savings_opportunities_ar.append(
                "ينصح باستخدام مصادر نيتروجين أكثر فعالية من حيث التكلفة مثل اليوريا."
            )
            analysis.potential_savings = (analysis.cost_per_kg_n - Decimal("5.50")) * Decimal(str(total_n))

        return analysis

    def calculate_nutrient_balance(
        self,
        field_id: str,
        season: str,
        crop: str,
        crop_ar: str,
        soil_test: SoilTest,
        target_yield_tons_ha: float,
        applications: list[FertilizerApplication],
    ) -> NutrientBalance:
        """
        Calculate nutrient balance for a field.

        Args:
            field_id: Field ID
            season: Season identifier
            crop: Crop name
            crop_ar: Crop name in Arabic
            soil_test: Soil test results
            target_yield_tons_ha: Target yield
            applications: List of fertilizer applications

        Returns:
            NutrientBalance showing surplus/deficit
        """
        balance = NutrientBalance(
            field_id=field_id,
            season=season,
            crop=crop,
            crop_ar=crop_ar,
        )

        # Estimate soil available nutrients (simplified)
        balance.soil_n_kg_ha = soil_test.nitrogen_ppm * 2.0
        balance.soil_p_kg_ha = soil_test.phosphorus_ppm * 2.5
        balance.soil_k_kg_ha = soil_test.potassium_ppm * 1.2

        # Sum applied nutrients
        for app in applications:
            balance.applied_n_kg_ha += app.nitrogen_applied_kg_ha
            balance.applied_p_kg_ha += app.phosphorus_applied_kg_ha
            balance.applied_k_kg_ha += app.potassium_applied_kg_ha

        # Estimate crop requirements (simplified factors)
        crop_factors = {
            "wheat": {"N": 25, "P": 10, "K": 20},
            "barley": {"N": 22, "P": 9, "K": 18},
            "tomato": {"N": 3, "P": 1, "K": 4.5},
            "date_palm": {"N": 1.5, "P": 0.5, "K": 2},
        }
        factors = crop_factors.get(crop.lower(), {"N": 20, "P": 10, "K": 15})

        balance.crop_n_requirement_kg_ha = factors["N"] * target_yield_tons_ha
        balance.crop_p_requirement_kg_ha = factors["P"] * target_yield_tons_ha
        balance.crop_k_requirement_kg_ha = factors["K"] * target_yield_tons_ha

        # Calculate balance
        total_n_available = balance.soil_n_kg_ha + balance.applied_n_kg_ha
        total_p_available = balance.soil_p_kg_ha + balance.applied_p_kg_ha
        total_k_available = balance.soil_k_kg_ha + balance.applied_k_kg_ha

        balance.n_balance_kg_ha = total_n_available - balance.crop_n_requirement_kg_ha
        balance.p_balance_kg_ha = total_p_available - balance.crop_p_requirement_kg_ha
        balance.k_balance_kg_ha = total_k_available - balance.crop_k_requirement_kg_ha

        # Determine status
        def get_status(balance_value: float, requirement: float) -> NutrientStatus:
            ratio = balance_value / requirement if requirement > 0 else 0
            if ratio < -0.3:
                return NutrientStatus.DEFICIENT
            elif ratio < -0.1:
                return NutrientStatus.LOW
            elif ratio < 0.2:
                return NutrientStatus.OPTIMAL
            elif ratio < 0.5:
                return NutrientStatus.HIGH
            else:
                return NutrientStatus.EXCESSIVE

        balance.n_status = get_status(balance.n_balance_kg_ha, balance.crop_n_requirement_kg_ha)
        balance.p_status = get_status(balance.p_balance_kg_ha, balance.crop_p_requirement_kg_ha)
        balance.k_status = get_status(balance.k_balance_kg_ha, balance.crop_k_requirement_kg_ha)

        # Check micronutrients
        micronutrient_thresholds = {
            ("zinc_ppm", 1.0, "Zinc", "زنك"),
            ("iron_ppm", 4.0, "Iron", "حديد"),
            ("manganese_ppm", 2.0, "Manganese", "منجنيز"),
            ("copper_ppm", 0.5, "Copper", "نحاس"),
            ("boron_ppm", 0.5, "Boron", "بورون"),
        }

        for attr, threshold, name_en, name_ar in micronutrient_thresholds:
            value = getattr(soil_test, attr, 0.0)
            if value < threshold:
                balance.micronutrient_deficiencies.append(name_en)
                balance.micronutrient_deficiencies_ar.append(name_ar)

        return balance


def quick_rate_calculation(
    fertilizer_code: str,
    target_nutrient: str,
    target_kg_per_ha: float,
    area_ha: float = 1.0,
) -> dict:
    """
    Quick calculation of fertilizer application rate.

    Args:
        fertilizer_code: Fertilizer code (e.g., 'urea', 'dap', 'npk_20_20_20')
        target_nutrient: Target nutrient ('N', 'P2O5', 'K2O')
        target_kg_per_ha: Target nutrient amount in kg/ha
        area_ha: Field area in hectares

    Returns:
        Dictionary with calculated rate and cost
    """
    calculator = FertilizerCalculator()
    try:
        result = calculator.calculate_rate_for_nutrient(fertilizer_code, target_nutrient, target_kg_per_ha, area_ha)
        return result.to_dict()
    except ValueError as e:
        return {"error": str(e)}


def calculate_blend_for_targets(
    n_kg_ha: float,
    p_kg_ha: float,
    k_kg_ha: float,
) -> dict:
    """
    Calculate fertilizer blend to meet nutrient targets.

    Args:
        n_kg_ha: Target nitrogen in kg/ha
        p_kg_ha: Target P2O5 in kg/ha
        k_kg_ha: Target K2O in kg/ha

    Returns:
        Dictionary with blend components and costs
    """
    calculator = FertilizerCalculator()
    result = calculator.calculate_blend(n_kg_ha, p_kg_ha, k_kg_ha)
    return result.to_dict()
