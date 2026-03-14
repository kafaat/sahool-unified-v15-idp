"""
Fertilizer Recommendations - توصيات التسميد

Nutrient recommendations based on soil tests, crop requirements, and growth stage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal

from .models import (
    ApplicationMethod,
    Fertilizer,
    FertilizerType,
    NutrientStatus,
    SoilTest,
)

# Crop nutrient requirements (kg/ha for target yield)
# Format: {crop: {nutrient: (requirement_per_ton_yield, typical_yield_tons_ha)}}
CROP_NUTRIENT_REQUIREMENTS: dict[str, dict] = {
    "wheat": {
        "name_ar": "قمح",
        "N": 25,  # kg N per ton grain
        "P2O5": 10,
        "K2O": 20,
        "typical_yield": 5.0,  # tons/ha
        "growth_stages": {
            "seeding": {"N": 0.20, "P2O5": 0.60, "K2O": 0.30},
            "tillering": {"N": 0.40, "P2O5": 0.20, "K2O": 0.30},
            "stem_elongation": {"N": 0.25, "P2O5": 0.10, "K2O": 0.20},
            "heading": {"N": 0.15, "P2O5": 0.10, "K2O": 0.20},
        },
    },
    "barley": {
        "name_ar": "شعير",
        "N": 22,
        "P2O5": 9,
        "K2O": 18,
        "typical_yield": 4.5,
        "growth_stages": {
            "seeding": {"N": 0.20, "P2O5": 0.60, "K2O": 0.30},
            "tillering": {"N": 0.40, "P2O5": 0.20, "K2O": 0.30},
            "stem_elongation": {"N": 0.25, "P2O5": 0.10, "K2O": 0.20},
            "heading": {"N": 0.15, "P2O5": 0.10, "K2O": 0.20},
        },
    },
    "tomato": {
        "name_ar": "طماطم",
        "N": 3.0,  # kg per ton fruit
        "P2O5": 1.0,
        "K2O": 4.5,
        "typical_yield": 60.0,
        "growth_stages": {
            "transplanting": {"N": 0.10, "P2O5": 0.40, "K2O": 0.10},
            "vegetative": {"N": 0.30, "P2O5": 0.30, "K2O": 0.20},
            "flowering": {"N": 0.30, "P2O5": 0.20, "K2O": 0.30},
            "fruiting": {"N": 0.30, "P2O5": 0.10, "K2O": 0.40},
        },
    },
    "cucumber": {
        "name_ar": "خيار",
        "N": 2.5,
        "P2O5": 0.8,
        "K2O": 3.5,
        "typical_yield": 50.0,
        "growth_stages": {
            "transplanting": {"N": 0.10, "P2O5": 0.40, "K2O": 0.10},
            "vegetative": {"N": 0.30, "P2O5": 0.30, "K2O": 0.20},
            "flowering": {"N": 0.30, "P2O5": 0.20, "K2O": 0.30},
            "fruiting": {"N": 0.30, "P2O5": 0.10, "K2O": 0.40},
        },
    },
    "date_palm": {
        "name_ar": "نخيل",
        "N": 1.5,  # kg per tree per year
        "P2O5": 0.5,
        "K2O": 2.0,
        "typical_yield": 100.0,  # kg per tree
        "growth_stages": {
            "dormant": {"N": 0.10, "P2O5": 0.20, "K2O": 0.10},
            "flowering": {"N": 0.30, "P2O5": 0.30, "K2O": 0.20},
            "fruit_set": {"N": 0.30, "P2O5": 0.30, "K2O": 0.30},
            "ripening": {"N": 0.30, "P2O5": 0.20, "K2O": 0.40},
        },
    },
    "alfalfa": {
        "name_ar": "برسيم",
        "N": 0,  # N-fixing
        "P2O5": 15,
        "K2O": 25,
        "typical_yield": 15.0,
        "growth_stages": {
            "establishment": {"N": 0.0, "P2O5": 0.50, "K2O": 0.30},
            "cutting_1": {"N": 0.0, "P2O5": 0.25, "K2O": 0.35},
            "cutting_2": {"N": 0.0, "P2O5": 0.25, "K2O": 0.35},
        },
    },
    "potato": {
        "name_ar": "بطاطس",
        "N": 5.0,
        "P2O5": 1.5,
        "K2O": 7.0,
        "typical_yield": 35.0,
        "growth_stages": {
            "planting": {"N": 0.20, "P2O5": 0.50, "K2O": 0.20},
            "vegetative": {"N": 0.40, "P2O5": 0.30, "K2O": 0.30},
            "tuber_initiation": {"N": 0.25, "P2O5": 0.15, "K2O": 0.30},
            "tuber_bulking": {"N": 0.15, "P2O5": 0.05, "K2O": 0.20},
        },
    },
    "onion": {
        "name_ar": "بصل",
        "N": 3.0,
        "P2O5": 1.0,
        "K2O": 2.5,
        "typical_yield": 40.0,
        "growth_stages": {
            "transplanting": {"N": 0.15, "P2O5": 0.50, "K2O": 0.20},
            "vegetative": {"N": 0.35, "P2O5": 0.30, "K2O": 0.30},
            "bulb_initiation": {"N": 0.30, "P2O5": 0.15, "K2O": 0.30},
            "bulb_development": {"N": 0.20, "P2O5": 0.05, "K2O": 0.20},
        },
    },
}

# Soil nutrient thresholds (ppm)
SOIL_NUTRIENT_THRESHOLDS: dict[str, dict] = {
    "N": {
        "very_low": 10,
        "low": 20,
        "medium": 40,
        "high": 60,
        "very_high": 100,
    },
    "P": {
        "very_low": 5,
        "low": 10,
        "medium": 20,
        "high": 40,
        "very_high": 80,
    },
    "K": {
        "very_low": 50,
        "low": 100,
        "medium": 150,
        "high": 250,
        "very_high": 400,
    },
    "S": {
        "very_low": 5,
        "low": 10,
        "medium": 20,
        "high": 40,
    },
    "Zn": {
        "very_low": 0.5,
        "low": 1.0,
        "medium": 2.0,
        "high": 4.0,
    },
    "Fe": {
        "very_low": 2.0,
        "low": 4.0,
        "medium": 10.0,
        "high": 20.0,
    },
    "Mn": {
        "very_low": 1.0,
        "low": 2.0,
        "medium": 5.0,
        "high": 10.0,
    },
    "Cu": {
        "very_low": 0.2,
        "low": 0.5,
        "medium": 1.0,
        "high": 2.0,
    },
    "B": {
        "very_low": 0.3,
        "low": 0.5,
        "medium": 1.0,
        "high": 2.0,
    },
}


@dataclass
class NutrientRecommendation:
    """
    Single nutrient recommendation - توصية لعنصر غذائي واحد
    """

    nutrient: str
    nutrient_ar: str
    current_level_ppm: float
    status: NutrientStatus
    status_ar: str

    # Recommendation
    required_kg_ha: float
    reason_en: str
    reason_ar: str

    # Urgency
    priority: int = 1  # 1=highest, 5=lowest
    timing_en: str = ""
    timing_ar: str = ""


@dataclass
class FertilizerRecommendation:
    """
    Complete fertilizer recommendation - توصية تسميد كاملة
    """

    id: str
    tenant_id: str
    field_id: str
    recommendation_date: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Crop info
    crop: str = ""
    crop_ar: str = ""
    growth_stage: str = ""
    growth_stage_ar: str = ""
    target_yield_tons_ha: float = 0.0

    # Soil test reference
    soil_test_id: str | None = None
    soil_test_date: datetime | None = None

    # Nutrient requirements
    total_n_required_kg_ha: float = 0.0
    total_p_required_kg_ha: float = 0.0
    total_k_required_kg_ha: float = 0.0

    # Already applied
    n_applied_kg_ha: float = 0.0
    p_applied_kg_ha: float = 0.0
    k_applied_kg_ha: float = 0.0

    # Remaining needs
    n_remaining_kg_ha: float = 0.0
    p_remaining_kg_ha: float = 0.0
    k_remaining_kg_ha: float = 0.0

    # Individual nutrient recommendations
    nutrient_recommendations: list[NutrientRecommendation] = field(default_factory=list)

    # Fertilizer products recommended
    recommended_products: list[dict] = field(default_factory=list)

    # Application guidance
    application_method: ApplicationMethod = ApplicationMethod.BROADCAST
    application_timing_en: str = ""
    application_timing_ar: str = ""
    split_applications: list[dict] = field(default_factory=list)

    # Environmental considerations
    environmental_notes_en: list[str] = field(default_factory=list)
    environmental_notes_ar: list[str] = field(default_factory=list)

    # Cost estimate
    estimated_cost: Decimal = Decimal("0.00")
    currency: str = "SAR"

    # Confidence
    confidence_score: float = 0.8  # 0-1

    # Summary
    summary_en: str = ""
    summary_ar: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "field_id": self.field_id,
            "crop": self.crop,
            "growth_stage": self.growth_stage,
            "target_yield": self.target_yield_tons_ha,
            "nutrients_required": {
                "N": self.total_n_required_kg_ha,
                "P2O5": self.total_p_required_kg_ha,
                "K2O": self.total_k_required_kg_ha,
            },
            "nutrients_remaining": {
                "N": self.n_remaining_kg_ha,
                "P2O5": self.p_remaining_kg_ha,
                "K2O": self.k_remaining_kg_ha,
            },
            "recommended_products": self.recommended_products,
            "application_method": self.application_method.value,
            "estimated_cost": float(self.estimated_cost),
            "summary_en": self.summary_en,
            "summary_ar": self.summary_ar,
        }


class FertilizerRecommendationEngine:
    """
    Engine for generating fertilizer recommendations
    محرك توليد توصيات التسميد
    """

    def __init__(
        self,
        available_fertilizers: list[Fertilizer] | None = None,
    ):
        """
        Initialize recommendation engine.

        Args:
            available_fertilizers: List of available fertilizer products
        """
        self.available_fertilizers = available_fertilizers or []
        self.crop_requirements = CROP_NUTRIENT_REQUIREMENTS
        self.nutrient_thresholds = SOIL_NUTRIENT_THRESHOLDS

    def get_nutrient_status(
        self,
        nutrient: str,
        value_ppm: float,
    ) -> tuple[NutrientStatus, str, str]:
        """
        Determine nutrient status from soil test value.

        Args:
            nutrient: Nutrient code (N, P, K, etc.)
            value_ppm: Soil test value in ppm

        Returns:
            Tuple of (status, description_en, description_ar)
        """
        thresholds = self.nutrient_thresholds.get(nutrient, {})

        if value_ppm <= thresholds.get("very_low", 0):
            return NutrientStatus.DEFICIENT, "Severely deficient", "نقص شديد"
        elif value_ppm <= thresholds.get("low", 0):
            return NutrientStatus.LOW, "Low", "منخفض"
        elif value_ppm <= thresholds.get("medium", 0):
            return NutrientStatus.OPTIMAL, "Optimal", "مثالي"
        elif value_ppm <= thresholds.get("high", 0):
            return NutrientStatus.HIGH, "High", "مرتفع"
        else:
            return NutrientStatus.EXCESSIVE, "Excessive", "زائد"

    def calculate_crop_requirements(
        self,
        crop: str,
        target_yield_tons_ha: float | None = None,
        growth_stage: str | None = None,
    ) -> dict[str, float]:
        """
        Calculate total nutrient requirements for a crop.

        Args:
            crop: Crop name
            target_yield_tons_ha: Target yield (optional, uses typical if not provided)
            growth_stage: Current growth stage for split application

        Returns:
            Dictionary of nutrient requirements in kg/ha
        """
        crop_data = self.crop_requirements.get(crop.lower(), {})
        if not crop_data:
            # Return default values for unknown crops
            return {
                "N": 100.0,
                "P2O5": 50.0,
                "K2O": 80.0,
            }

        yield_target = target_yield_tons_ha or crop_data.get("typical_yield", 5.0)

        # Calculate total requirements
        n_total = crop_data.get("N", 20) * yield_target
        p_total = crop_data.get("P2O5", 10) * yield_target
        k_total = crop_data.get("K2O", 15) * yield_target

        # If growth stage specified, calculate portion for this stage
        if growth_stage and "growth_stages" in crop_data:
            stages = crop_data["growth_stages"]
            if growth_stage in stages:
                stage_factors = stages[growth_stage]
                return {
                    "N": n_total * stage_factors.get("N", 0.25),
                    "P2O5": p_total * stage_factors.get("P2O5", 0.25),
                    "K2O": k_total * stage_factors.get("K2O", 0.25),
                }

        return {
            "N": n_total,
            "P2O5": p_total,
            "K2O": k_total,
        }

    def soil_contribution(
        self,
        soil_test: SoilTest,
        crop: str,
    ) -> dict[str, float]:
        """
        Estimate soil nutrient contribution based on soil test.

        Args:
            soil_test: Soil test results
            crop: Crop type

        Returns:
            Dictionary of estimated soil contribution in kg/ha
        """
        # Conversion factors (ppm to kg/ha available, varies by extraction method)
        # These are approximate and should be calibrated for local conditions
        n_factor = 2.0  # Assumes 2 kg/ha available per ppm
        p_factor = 2.5  # Mehlich-3 extraction
        k_factor = 1.2

        # Availability factors based on soil pH
        ph = soil_test.ph
        p_ph_factor = 1.0
        if ph < 6.0:
            p_ph_factor = 0.7  # P less available in acidic soil
        elif ph > 7.5:
            p_ph_factor = 0.6  # P less available in alkaline soil

        return {
            "N": soil_test.nitrogen_ppm * n_factor,
            "P2O5": soil_test.phosphorus_ppm * p_factor * p_ph_factor,
            "K2O": soil_test.potassium_ppm * k_factor,
        }

    def generate_recommendation(
        self,
        recommendation_id: str,
        tenant_id: str,
        field_id: str,
        soil_test: SoilTest,
        crop: str,
        target_yield_tons_ha: float | None = None,
        growth_stage: str | None = None,
        already_applied_n: float = 0.0,
        already_applied_p: float = 0.0,
        already_applied_k: float = 0.0,
    ) -> FertilizerRecommendation:
        """
        Generate a complete fertilizer recommendation.

        Args:
            recommendation_id: Unique ID for this recommendation
            tenant_id: Tenant ID
            field_id: Field ID
            soil_test: Soil test results
            crop: Crop name
            target_yield_tons_ha: Target yield
            growth_stage: Current growth stage
            already_applied_*: Nutrients already applied this season

        Returns:
            FertilizerRecommendation object
        """
        crop_data = self.crop_requirements.get(crop.lower(), {})
        crop_ar = crop_data.get("name_ar", crop)

        # Growth stage Arabic translation
        growth_stage_translations = {
            "seeding": "البذر",
            "tillering": "التفريع",
            "stem_elongation": "استطالة الساق",
            "heading": "الإسبال",
            "transplanting": "الشتل",
            "vegetative": "النمو الخضري",
            "flowering": "الإزهار",
            "fruiting": "الإثمار",
            "planting": "الزراعة",
            "tuber_initiation": "بدء تكوين الدرنات",
            "tuber_bulking": "تضخم الدرنات",
            "dormant": "السكون",
            "fruit_set": "عقد الثمار",
            "ripening": "النضج",
        }
        growth_stage_ar = growth_stage_translations.get(growth_stage or "", "")

        # Calculate requirements
        total_requirements = self.calculate_crop_requirements(crop, target_yield_tons_ha)
        soil_contribution = self.soil_contribution(soil_test, crop)

        # Net requirements
        n_required = max(0, total_requirements["N"] - soil_contribution["N"] - already_applied_n)
        p_required = max(
            0,
            total_requirements["P2O5"] - soil_contribution["P2O5"] - already_applied_p,
        )
        k_required = max(0, total_requirements["K2O"] - soil_contribution["K2O"] - already_applied_k)

        # Build nutrient recommendations
        nutrient_recs = []

        # Nitrogen
        n_status, n_desc_en, n_desc_ar = self.get_nutrient_status("N", soil_test.nitrogen_ppm)
        if n_required > 0:
            nutrient_recs.append(
                NutrientRecommendation(
                    nutrient="N",
                    nutrient_ar="نيتروجين",
                    current_level_ppm=soil_test.nitrogen_ppm,
                    status=n_status,
                    status_ar=n_desc_ar,
                    required_kg_ha=n_required,
                    reason_en=f"Soil nitrogen is {n_desc_en.lower()} ({soil_test.nitrogen_ppm:.1f} ppm)",
                    reason_ar=f"نيتروجين التربة {n_desc_ar} ({soil_test.nitrogen_ppm:.1f} جزء بالمليون)",
                    priority=1 if n_status == NutrientStatus.DEFICIENT else 2,
                    timing_en="Apply in split doses during active growth",
                    timing_ar="يطبق على جرعات مقسمة خلال النمو النشط",
                )
            )

        # Phosphorus
        p_status, p_desc_en, p_desc_ar = self.get_nutrient_status("P", soil_test.phosphorus_ppm)
        if p_required > 0:
            nutrient_recs.append(
                NutrientRecommendation(
                    nutrient="P2O5",
                    nutrient_ar="فسفور",
                    current_level_ppm=soil_test.phosphorus_ppm,
                    status=p_status,
                    status_ar=p_desc_ar,
                    required_kg_ha=p_required,
                    reason_en=f"Soil phosphorus is {p_desc_en.lower()} ({soil_test.phosphorus_ppm:.1f} ppm)",
                    reason_ar=f"فسفور التربة {p_desc_ar} ({soil_test.phosphorus_ppm:.1f} جزء بالمليون)",
                    priority=2 if p_status == NutrientStatus.DEFICIENT else 3,
                    timing_en="Apply at planting or early growth",
                    timing_ar="يطبق عند الزراعة أو النمو المبكر",
                )
            )

        # Potassium
        k_status, k_desc_en, k_desc_ar = self.get_nutrient_status("K", soil_test.potassium_ppm)
        if k_required > 0:
            nutrient_recs.append(
                NutrientRecommendation(
                    nutrient="K2O",
                    nutrient_ar="بوتاسيوم",
                    current_level_ppm=soil_test.potassium_ppm,
                    status=k_status,
                    status_ar=k_desc_ar,
                    required_kg_ha=k_required,
                    reason_en=f"Soil potassium is {k_desc_en.lower()} ({soil_test.potassium_ppm:.1f} ppm)",
                    reason_ar=f"بوتاسيوم التربة {k_desc_ar} ({soil_test.potassium_ppm:.1f} جزء بالمليون)",
                    priority=2 if k_status == NutrientStatus.DEFICIENT else 3,
                    timing_en="Apply in split doses",
                    timing_ar="يطبق على جرعات مقسمة",
                )
            )

        # Check micronutrients
        for nutrient, field_name, nutrient_ar in [
            ("Zn", "zinc_ppm", "زنك"),
            ("Fe", "iron_ppm", "حديد"),
            ("Mn", "manganese_ppm", "منجنيز"),
            ("Cu", "copper_ppm", "نحاس"),
            ("B", "boron_ppm", "بورون"),
        ]:
            value = getattr(soil_test, field_name, 0.0)
            status, desc_en, desc_ar = self.get_nutrient_status(nutrient, value)
            if status in [NutrientStatus.DEFICIENT, NutrientStatus.LOW]:
                nutrient_recs.append(
                    NutrientRecommendation(
                        nutrient=nutrient,
                        nutrient_ar=nutrient_ar,
                        current_level_ppm=value,
                        status=status,
                        status_ar=desc_ar,
                        required_kg_ha=2.0,  # Standard micronutrient rate
                        reason_en=f"{nutrient} is {desc_en.lower()} ({value:.2f} ppm)",
                        reason_ar=f"{nutrient_ar} {desc_ar} ({value:.2f} جزء بالمليون)",
                        priority=4,
                        timing_en="Apply as foliar spray or soil application",
                        timing_ar="يطبق رشاً ورقياً أو تسميداً أرضياً",
                    )
                )

        # Generate product recommendations
        recommended_products = self._select_fertilizer_products(n_required, p_required, k_required)

        # Calculate estimated cost
        estimated_cost = Decimal("0.00")
        for product in recommended_products:
            estimated_cost += Decimal(str(product.get("total_cost", 0)))

        # Generate summary
        summary_en = self._generate_summary_en(crop, n_required, p_required, k_required, nutrient_recs)
        summary_ar = self._generate_summary_ar(crop_ar, n_required, p_required, k_required, nutrient_recs)

        # Environmental notes
        env_notes_en = []
        env_notes_ar = []
        if n_required > 150:
            env_notes_en.append("High nitrogen rate - consider split applications to reduce leaching")
            env_notes_ar.append("معدل نيتروجين مرتفع - يُنصح بتقسيم الجرعات لتقليل الغسيل")
        if soil_test.ec_ds_m > 4.0:
            env_notes_en.append("High soil salinity - avoid chloride-containing fertilizers")
            env_notes_ar.append("ملوحة تربة مرتفعة - تجنب الأسمدة المحتوية على الكلوريد")

        return FertilizerRecommendation(
            id=recommendation_id,
            tenant_id=tenant_id,
            field_id=field_id,
            crop=crop,
            crop_ar=crop_ar,
            growth_stage=growth_stage or "",
            growth_stage_ar=growth_stage_ar,
            target_yield_tons_ha=target_yield_tons_ha or crop_data.get("typical_yield", 5.0),
            soil_test_id=soil_test.id,
            soil_test_date=soil_test.sample_date,
            total_n_required_kg_ha=total_requirements["N"],
            total_p_required_kg_ha=total_requirements["P2O5"],
            total_k_required_kg_ha=total_requirements["K2O"],
            n_applied_kg_ha=already_applied_n,
            p_applied_kg_ha=already_applied_p,
            k_applied_kg_ha=already_applied_k,
            n_remaining_kg_ha=n_required,
            p_remaining_kg_ha=p_required,
            k_remaining_kg_ha=k_required,
            nutrient_recommendations=nutrient_recs,
            recommended_products=recommended_products,
            application_method=ApplicationMethod.BROADCAST,
            environmental_notes_en=env_notes_en,
            environmental_notes_ar=env_notes_ar,
            estimated_cost=estimated_cost,
            summary_en=summary_en,
            summary_ar=summary_ar,
        )

    def _select_fertilizer_products(
        self,
        n_required: float,
        p_required: float,
        k_required: float,
    ) -> list[dict]:
        """
        Select optimal fertilizer products to meet nutrient requirements.

        Returns list of recommended products with application rates.
        """
        products = []

        # If we have available fertilizers, use optimization algorithm
        if self.available_fertilizers:
            optimized = self._optimize_fertilizer_selection(n_required, p_required, k_required)
            if optimized:
                # Verify that the optimized selection meets nutrient needs
                # within an acceptable tolerance (5 kg/ha) before returning.
                # If requirements are not met, fall through to standard recs.
                tolerance = 5.0  # kg/ha
                total_n = sum(p.get("nutrients_supplied", {}).get("N", 0) for p in optimized)
                total_p = sum(p.get("nutrients_supplied", {}).get("P2O5", 0) for p in optimized)
                total_k = sum(p.get("nutrients_supplied", {}).get("K2O", 0) for p in optimized)
                n_met = n_required <= tolerance or total_n >= n_required - tolerance
                p_met = p_required <= tolerance or total_p >= p_required - tolerance
                k_met = k_required <= tolerance or total_k >= k_required - tolerance
                if n_met and p_met and k_met:
                    return optimized

        # Otherwise, use standard recommendations
        if n_required > 0:
            # Recommend Urea for nitrogen
            urea_rate = n_required / 0.46  # Urea is 46% N
            products.append(
                {
                    "fertilizer_name": "Urea 46%",
                    "fertilizer_name_ar": "يوريا 46%",
                    "fertilizer_type": FertilizerType.NITROGEN.value,
                    "npk_ratio": "46-0-0",
                    "application_rate_kg_ha": round(urea_rate, 1),
                    "nutrients_supplied": {
                        "N": round(n_required, 1),
                        "P2O5": 0,
                        "K2O": 0,
                    },
                    "unit_price_sar": 2.5,
                    "total_cost": round(urea_rate * 2.5, 2),
                    "application_notes_en": "Apply in 2-3 split doses during active growth",
                    "application_notes_ar": "يطبق على 2-3 جرعات مقسمة خلال النمو النشط",
                }
            )

        if p_required > 0:
            # Recommend DAP for phosphorus (also provides some N)
            dap_rate = p_required / 0.46  # DAP is 46% P2O5
            n_from_dap = dap_rate * 0.18  # DAP is 18% N
            products.append(
                {
                    "fertilizer_name": "DAP (18-46-0)",
                    "fertilizer_name_ar": "داب (18-46-0)",
                    "fertilizer_type": FertilizerType.PHOSPHORUS.value,
                    "npk_ratio": "18-46-0",
                    "application_rate_kg_ha": round(dap_rate, 1),
                    "nutrients_supplied": {
                        "N": round(n_from_dap, 1),
                        "P2O5": round(p_required, 1),
                        "K2O": 0,
                    },
                    "unit_price_sar": 3.2,
                    "total_cost": round(dap_rate * 3.2, 2),
                    "application_notes_en": "Apply at planting or early growth stage",
                    "application_notes_ar": "يطبق عند الزراعة أو في مرحلة النمو المبكر",
                }
            )

        if k_required > 0:
            # Recommend MOP or SOP based on chloride sensitivity
            mop_rate = k_required / 0.60  # MOP is 60% K2O
            products.append(
                {
                    "fertilizer_name": "MOP (0-0-60)",
                    "fertilizer_name_ar": "بوتاسيوم كلوريد (0-0-60)",
                    "fertilizer_type": FertilizerType.POTASSIUM.value,
                    "npk_ratio": "0-0-60",
                    "application_rate_kg_ha": round(mop_rate, 1),
                    "nutrients_supplied": {
                        "N": 0,
                        "P2O5": 0,
                        "K2O": round(k_required, 1),
                    },
                    "unit_price_sar": 2.8,
                    "total_cost": round(mop_rate * 2.8, 2),
                    "application_notes_en": "Apply in split doses, avoid for chloride-sensitive crops",
                    "application_notes_ar": "يطبق على جرعات مقسمة، يُتجنب للمحاصيل الحساسة للكلوريد",
                }
            )

        return products

    def _optimize_fertilizer_selection(
        self,
        n_required: float,
        p_required: float,
        k_required: float,
    ) -> list[dict]:
        """
        Greedy cost-minimization algorithm for selecting fertilizer products.

        For each remaining nutrient need (N, P, K), picks the cheapest
        available fertilizer per kg of that nutrient, calculates the
        application rate, clamps to min/max bounds, and tracks nutrients
        already supplied by compound fertilizers to avoid double-supplying.

        Returns:
            List of product dicts if optimization succeeds, empty list otherwise.
        """
        # Track remaining nutrient needs (can decrease as compound fertilizers supply multiple)
        remaining = {"N": n_required, "P2O5": p_required, "K2O": k_required}
        products: list[dict] = []
        used_fertilizer_ids: set[str] = set()

        # Process nutrients in priority order: N first (usually largest), then P, then K
        nutrient_keys = [
            ("N", "nitrogen_n"),
            ("P2O5", "phosphorus_p2o5"),
            ("K2O", "potassium_k2o"),
        ]

        for nutrient_key, composition_attr in nutrient_keys:
            if remaining[nutrient_key] <= 0.5:
                # Negligible need, skip
                continue

            # Find the cheapest fertilizer that supplies this nutrient
            # Cost metric: price per kg of the target nutrient delivered
            best_fertilizer: Fertilizer | None = None
            best_cost_per_kg_nutrient = float("inf")

            for fert in self.available_fertilizers:
                if not fert.is_active:
                    continue
                if fert.id in used_fertilizer_ids:
                    continue

                nutrient_percent = getattr(fert.composition, composition_attr, 0.0)
                if nutrient_percent <= 0:
                    continue

                # Cost per kg of this nutrient = (unit_price / unit_size_kg) / (percent / 100)
                price_per_kg_product = (
                    float(fert.unit_price) / fert.unit_size_kg if fert.unit_size_kg > 0 else float("inf")
                )
                cost_per_kg_nutrient = price_per_kg_product / (nutrient_percent / 100.0)

                if cost_per_kg_nutrient < best_cost_per_kg_nutrient:
                    best_cost_per_kg_nutrient = cost_per_kg_nutrient
                    best_fertilizer = fert

            if best_fertilizer is None:
                continue

            used_fertilizer_ids.add(best_fertilizer.id)

            # Calculate application rate to meet the remaining need for this nutrient
            nutrient_percent = getattr(best_fertilizer.composition, composition_attr, 0.0)
            application_rate = remaining[nutrient_key] / (nutrient_percent / 100.0)

            # Clamp to min/max application rates
            if best_fertilizer.min_application_rate_kg_ha is not None:
                application_rate = max(application_rate, best_fertilizer.min_application_rate_kg_ha)
            if best_fertilizer.max_application_rate_kg_ha is not None:
                application_rate = min(application_rate, best_fertilizer.max_application_rate_kg_ha)

            # Calculate all nutrients supplied at this application rate
            n_supplied = round(application_rate * best_fertilizer.composition.nitrogen_n / 100.0, 1)
            p_supplied = round(application_rate * best_fertilizer.composition.phosphorus_p2o5 / 100.0, 1)
            k_supplied = round(application_rate * best_fertilizer.composition.potassium_k2o / 100.0, 1)

            # Subtract supplied nutrients from remaining needs
            remaining["N"] = max(0, remaining["N"] - n_supplied)
            remaining["P2O5"] = max(0, remaining["P2O5"] - p_supplied)
            remaining["K2O"] = max(0, remaining["K2O"] - k_supplied)

            # Calculate cost
            price_per_kg = (
                float(best_fertilizer.unit_price) / best_fertilizer.unit_size_kg
                if best_fertilizer.unit_size_kg > 0
                else 0.0
            )
            total_cost = round(application_rate * price_per_kg, 2)

            # Build application notes based on fertilizer type
            notes_en = "Apply as recommended for the crop growth stage"
            notes_ar = "يطبق حسب التوصية لمرحلة نمو المحصول"
            if best_fertilizer.composition.nitrogen_n > 30:
                notes_en = "Apply in 2-3 split doses during active growth"
                notes_ar = "يطبق على 2-3 جرعات مقسمة خلال النمو النشط"
            elif best_fertilizer.composition.phosphorus_p2o5 > 30:
                notes_en = "Apply at planting or early growth stage"
                notes_ar = "يطبق عند الزراعة أو في مرحلة النمو المبكر"
            elif best_fertilizer.composition.potassium_k2o > 30:
                notes_en = "Apply in split doses, avoid for chloride-sensitive crops"
                notes_ar = "يطبق على جرعات مقسمة، يُتجنب للمحاصيل الحساسة للكلوريد"

            products.append(
                {
                    "fertilizer_name": best_fertilizer.name,
                    "fertilizer_name_ar": best_fertilizer.name_ar,
                    "fertilizer_type": best_fertilizer.fertilizer_type.value,
                    "npk_ratio": best_fertilizer.composition.npk_ratio,
                    "application_rate_kg_ha": round(application_rate, 1),
                    "nutrients_supplied": {
                        "N": n_supplied,
                        "P2O5": p_supplied,
                        "K2O": k_supplied,
                    },
                    "unit_price_sar": float(best_fertilizer.unit_price) / best_fertilizer.unit_size_kg
                    if best_fertilizer.unit_size_kg > 0
                    else 0.0,
                    "total_cost": total_cost,
                    "application_notes_en": notes_en,
                    "application_notes_ar": notes_ar,
                }
            )

        return products

    def _generate_summary_en(
        self,
        crop: str,
        n_required: float,
        p_required: float,
        k_required: float,
        nutrient_recs: list[NutrientRecommendation],
    ) -> str:
        """Generate English summary of recommendations."""
        if not any([n_required, p_required, k_required]):
            return f"Soil nutrient levels are adequate for {crop}. No fertilizer application recommended at this time."

        deficiencies = [rec for rec in nutrient_recs if rec.status == NutrientStatus.DEFICIENT]
        if deficiencies:
            nutrients = ", ".join([rec.nutrient for rec in deficiencies])
            return f"Critical deficiencies detected: {nutrients}. Immediate fertilizer application recommended for {crop} with {n_required:.0f} kg N, {p_required:.0f} kg P2O5, {k_required:.0f} kg K2O per hectare."

        return f"Fertilizer recommendation for {crop}: Apply {n_required:.0f} kg N, {p_required:.0f} kg P2O5, {k_required:.0f} kg K2O per hectare to achieve target yield."

    def _generate_summary_ar(
        self,
        crop_ar: str,
        n_required: float,
        p_required: float,
        k_required: float,
        nutrient_recs: list[NutrientRecommendation],
    ) -> str:
        """Generate Arabic summary of recommendations."""
        if not any([n_required, p_required, k_required]):
            return f"مستويات العناصر الغذائية في التربة كافية لمحصول {crop_ar}. لا يُنصح بتطبيق الأسمدة في هذا الوقت."

        deficiencies = [rec for rec in nutrient_recs if rec.status == NutrientStatus.DEFICIENT]
        if deficiencies:
            nutrients = "، ".join([rec.nutrient_ar for rec in deficiencies])
            return f"تم اكتشاف نقص حرج: {nutrients}. يُنصح بتطبيق الأسمدة فوراً لمحصول {crop_ar} بمعدل {n_required:.0f} كجم نيتروجين، {p_required:.0f} كجم فسفور، {k_required:.0f} كجم بوتاسيوم للهكتار."

        return f"توصية التسميد لمحصول {crop_ar}: يُطبق {n_required:.0f} كجم نيتروجين، {p_required:.0f} كجم فسفور، {k_required:.0f} كجم بوتاسيوم للهكتار لتحقيق الإنتاجية المستهدفة."


def get_crop_requirements(crop: str) -> dict | None:
    """
    Get nutrient requirements for a specific crop.

    Args:
        crop: Crop name

    Returns:
        Dictionary of crop requirements or None if not found
    """
    return CROP_NUTRIENT_REQUIREMENTS.get(crop.lower())


def get_supported_crops() -> list[dict]:
    """
    Get list of supported crops with Arabic names.

    Returns:
        List of crop dictionaries
    """
    return [{"name": crop, "name_ar": data.get("name_ar", crop)} for crop, data in CROP_NUTRIENT_REQUIREMENTS.items()]


def calculate_quick_recommendation(
    crop: str,
    soil_n_ppm: float,
    soil_p_ppm: float,
    soil_k_ppm: float,
    target_yield: float | None = None,
) -> dict:
    """
    Quick calculation of fertilizer recommendation.

    Args:
        crop: Crop name
        soil_n_ppm: Soil nitrogen in ppm
        soil_p_ppm: Soil phosphorus in ppm
        soil_k_ppm: Soil potassium in ppm
        target_yield: Target yield in tons/ha

    Returns:
        Dictionary with recommended rates
    """
    engine = FertilizerRecommendationEngine()
    crop_data = engine.crop_requirements.get(crop.lower(), {})

    if not crop_data:
        return {
            "error": f"Crop '{crop}' not found in database",
            "error_ar": f"المحصول '{crop}' غير موجود في قاعدة البيانات",
        }

    yield_target = target_yield or crop_data.get("typical_yield", 5.0)

    # Calculate total requirements
    n_total = crop_data.get("N", 20) * yield_target
    p_total = crop_data.get("P2O5", 10) * yield_target
    k_total = crop_data.get("K2O", 15) * yield_target

    # Estimate soil contribution
    n_soil = soil_n_ppm * 2.0
    p_soil = soil_p_ppm * 2.5
    k_soil = soil_k_ppm * 1.2

    # Net requirements
    n_required = max(0, n_total - n_soil)
    p_required = max(0, p_total - p_soil)
    k_required = max(0, k_total - k_soil)

    return {
        "crop": crop,
        "crop_ar": crop_data.get("name_ar", crop),
        "target_yield_tons_ha": yield_target,
        "recommendations": {
            "N_kg_ha": round(n_required, 1),
            "P2O5_kg_ha": round(p_required, 1),
            "K2O_kg_ha": round(k_required, 1),
        },
        "suggested_fertilizers": {
            "urea_46_kg_ha": round(n_required / 0.46, 1) if n_required > 0 else 0,
            "dap_18_46_0_kg_ha": round(p_required / 0.46, 1) if p_required > 0 else 0,
            "mop_0_0_60_kg_ha": round(k_required / 0.60, 1) if k_required > 0 else 0,
        },
    }
