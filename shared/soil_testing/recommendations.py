"""
Soil Amendment Recommendations - توصيات تعديل التربة

Generates amendment recommendations based on soil test interpretations.
Includes fertilizers, lime, gypsum, organic amendments, and micronutrient products.

Supports:
- Crop-specific recommendations
- Cost-optimized product selection
- Split application scheduling
- Environmental considerations
- Local product availability (Middle East)

Author: SAHOOL Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from .interpreter import SoilTestInterpreter
from .models import (
    AmendmentPlan,
    AmendmentRecommendation,
    InterpretationReport,
    NutrientStatus,
    SoilProperties,
    SoilTestResult,
)

# Common fertilizer products available in Middle East
FERTILIZER_PRODUCTS: dict[str, dict] = {
    # Nitrogen fertilizers
    "urea": {
        "name": "Urea 46%",
        "name_ar": "يوريا 46%",
        "formula": "CO(NH2)2",
        "type": "nitrogen",
        "type_ar": "نيتروجيني",
        "nutrients": {"N": 46.0},
        "price_per_kg_sar": 2.50,
        "method": "broadcast or fertigation",
        "method_ar": "نثر أو تسميد بالري",
    },
    "ammonium_sulfate": {
        "name": "Ammonium Sulfate 21%",
        "name_ar": "سلفات الأمونيوم 21%",
        "formula": "(NH4)2SO4",
        "type": "nitrogen",
        "type_ar": "نيتروجيني",
        "nutrients": {"N": 21.0, "S": 24.0},
        "price_per_kg_sar": 1.80,
        "method": "broadcast or banding",
        "method_ar": "نثر أو شريطي",
        "notes": "Good for alkaline soils, provides sulfur",
        "notes_ar": "جيد للتربة القلوية، يوفر الكبريت",
    },
    "calcium_ammonium_nitrate": {
        "name": "CAN 26%",
        "name_ar": "نترات الأمونيوم الكالسية 26%",
        "formula": "CaCO3.NH4NO3",
        "type": "nitrogen",
        "type_ar": "نيتروجيني",
        "nutrients": {"N": 26.0, "Ca": 8.0},
        "price_per_kg_sar": 2.20,
        "method": "broadcast or topdress",
        "method_ar": "نثر أو تسميد سطحي",
    },
    # Phosphorus fertilizers
    "dap": {
        "name": "DAP 18-46-0",
        "name_ar": "داب 18-46-0",
        "formula": "(NH4)2HPO4",
        "type": "phosphorus",
        "type_ar": "فسفوري",
        "nutrients": {"N": 18.0, "P2O5": 46.0},
        "price_per_kg_sar": 3.20,
        "method": "band or incorporate",
        "method_ar": "شريطي أو خلط بالتربة",
    },
    "tsp": {
        "name": "TSP 0-46-0",
        "name_ar": "سوبر فوسفات ثلاثي 0-46-0",
        "formula": "Ca(H2PO4)2",
        "type": "phosphorus",
        "type_ar": "فسفوري",
        "nutrients": {"P2O5": 46.0, "Ca": 14.0},
        "price_per_kg_sar": 2.80,
        "method": "band or broadcast before planting",
        "method_ar": "شريطي أو نثر قبل الزراعة",
    },
    "map": {
        "name": "MAP 11-52-0",
        "name_ar": "ماب 11-52-0",
        "formula": "NH4H2PO4",
        "type": "phosphorus",
        "type_ar": "فسفوري",
        "nutrients": {"N": 11.0, "P2O5": 52.0},
        "price_per_kg_sar": 3.50,
        "method": "fertigation or band",
        "method_ar": "تسميد بالري أو شريطي",
    },
    # Potassium fertilizers
    "mop": {
        "name": "MOP 0-0-60",
        "name_ar": "كلوريد البوتاسيوم 0-0-60",
        "formula": "KCl",
        "type": "potassium",
        "type_ar": "بوتاسي",
        "nutrients": {"K2O": 60.0, "Cl": 47.0},
        "price_per_kg_sar": 2.80,
        "method": "broadcast or band",
        "method_ar": "نثر أو شريطي",
        "warnings": ["Avoid for Cl-sensitive crops"],
        "warnings_ar": ["تجنب للمحاصيل الحساسة للكلور"],
    },
    "sop": {
        "name": "SOP 0-0-50",
        "name_ar": "سلفات البوتاسيوم 0-0-50",
        "formula": "K2SO4",
        "type": "potassium",
        "type_ar": "بوتاسي",
        "nutrients": {"K2O": 50.0, "S": 18.0},
        "price_per_kg_sar": 4.50,
        "method": "broadcast or fertigation",
        "method_ar": "نثر أو تسميد بالري",
        "notes": "Preferred for Cl-sensitive crops",
        "notes_ar": "مفضل للمحاصيل الحساسة للكلور",
    },
    "potassium_nitrate": {
        "name": "Potassium Nitrate 13-0-46",
        "name_ar": "نترات البوتاسيوم 13-0-46",
        "formula": "KNO3",
        "type": "potassium",
        "type_ar": "بوتاسي",
        "nutrients": {"N": 13.0, "K2O": 46.0},
        "price_per_kg_sar": 5.50,
        "method": "fertigation or foliar",
        "method_ar": "تسميد بالري أو ورقي",
    },
    # NPK compounds
    "npk_15_15_15": {
        "name": "NPK 15-15-15",
        "name_ar": "مركب 15-15-15",
        "formula": "compound",
        "type": "compound",
        "type_ar": "مركب",
        "nutrients": {"N": 15.0, "P2O5": 15.0, "K2O": 15.0},
        "price_per_kg_sar": 3.00,
        "method": "broadcast or band",
        "method_ar": "نثر أو شريطي",
    },
    "npk_20_20_20": {
        "name": "NPK 20-20-20",
        "name_ar": "مركب 20-20-20 (مذاب)",
        "formula": "compound soluble",
        "type": "compound",
        "type_ar": "مركب",
        "nutrients": {"N": 20.0, "P2O5": 20.0, "K2O": 20.0},
        "price_per_kg_sar": 6.00,
        "method": "fertigation",
        "method_ar": "تسميد بالري",
    },
    # Calcium and Magnesium
    "calcium_nitrate": {
        "name": "Calcium Nitrate 15.5-0-0+19Ca",
        "name_ar": "نترات الكالسيوم",
        "formula": "Ca(NO3)2",
        "type": "calcium",
        "type_ar": "كالسيوم",
        "nutrients": {"N": 15.5, "Ca": 19.0},
        "price_per_kg_sar": 4.00,
        "method": "fertigation",
        "method_ar": "تسميد بالري",
    },
    "magnesium_sulfate": {
        "name": "Magnesium Sulfate (Epsom Salt)",
        "name_ar": "سلفات المغنيسيوم",
        "formula": "MgSO4.7H2O",
        "type": "magnesium",
        "type_ar": "مغنيسيوم",
        "nutrients": {"Mg": 10.0, "S": 13.0},
        "price_per_kg_sar": 3.50,
        "method": "fertigation or foliar",
        "method_ar": "تسميد بالري أو ورقي",
    },
    # Micronutrients
    "iron_sulfate": {
        "name": "Iron Sulfate (Ferrous)",
        "name_ar": "سلفات الحديد",
        "formula": "FeSO4.7H2O",
        "type": "micronutrient",
        "type_ar": "عنصر صغير",
        "nutrients": {"Fe": 20.0, "S": 12.0},
        "price_per_kg_sar": 8.00,
        "method": "soil or foliar",
        "method_ar": "أرضي أو ورقي",
    },
    "iron_chelate": {
        "name": "Iron EDDHA Chelate 6%",
        "name_ar": "حديد مخلبي EDDHA 6%",
        "formula": "Fe-EDDHA",
        "type": "micronutrient",
        "type_ar": "عنصر صغير",
        "nutrients": {"Fe": 6.0},
        "price_per_kg_sar": 85.00,
        "method": "soil application",
        "method_ar": "تطبيق أرضي",
        "notes": "Stable in alkaline soils",
        "notes_ar": "مستقر في التربة القلوية",
    },
    "zinc_sulfate": {
        "name": "Zinc Sulfate",
        "name_ar": "سلفات الزنك",
        "formula": "ZnSO4.7H2O",
        "type": "micronutrient",
        "type_ar": "عنصر صغير",
        "nutrients": {"Zn": 23.0, "S": 11.0},
        "price_per_kg_sar": 12.00,
        "method": "soil or foliar",
        "method_ar": "أرضي أو ورقي",
    },
    "manganese_sulfate": {
        "name": "Manganese Sulfate",
        "name_ar": "سلفات المنجنيز",
        "formula": "MnSO4.H2O",
        "type": "micronutrient",
        "type_ar": "عنصر صغير",
        "nutrients": {"Mn": 32.0, "S": 19.0},
        "price_per_kg_sar": 15.00,
        "method": "soil or foliar",
        "method_ar": "أرضي أو ورقي",
    },
    "copper_sulfate": {
        "name": "Copper Sulfate",
        "name_ar": "سلفات النحاس",
        "formula": "CuSO4.5H2O",
        "type": "micronutrient",
        "type_ar": "عنصر صغير",
        "nutrients": {"Cu": 25.0, "S": 13.0},
        "price_per_kg_sar": 18.00,
        "method": "soil or foliar",
        "method_ar": "أرضي أو ورقي",
    },
    "borax": {
        "name": "Borax",
        "name_ar": "بوراكس",
        "formula": "Na2B4O7.10H2O",
        "type": "micronutrient",
        "type_ar": "عنصر صغير",
        "nutrients": {"B": 11.0},
        "price_per_kg_sar": 25.00,
        "method": "soil broadcast",
        "method_ar": "نثر أرضي",
    },
    "boric_acid": {
        "name": "Boric Acid",
        "name_ar": "حمض البوريك",
        "formula": "H3BO3",
        "type": "micronutrient",
        "type_ar": "عنصر صغير",
        "nutrients": {"B": 17.5},
        "price_per_kg_sar": 30.00,
        "method": "foliar spray",
        "method_ar": "رش ورقي",
    },
    "sodium_molybdate": {
        "name": "Sodium Molybdate",
        "name_ar": "موليبدات الصوديوم",
        "formula": "Na2MoO4.2H2O",
        "type": "micronutrient",
        "type_ar": "عنصر صغير",
        "nutrients": {"Mo": 39.0},
        "price_per_kg_sar": 150.00,
        "method": "seed treatment or foliar",
        "method_ar": "معاملة بذور أو ورقي",
    },
    # Organic amendments
    "compost": {
        "name": "Composted Organic Matter",
        "name_ar": "سماد عضوي مخمر",
        "formula": "organic",
        "type": "organic",
        "type_ar": "عضوي",
        "nutrients": {"N": 1.5, "P2O5": 1.0, "K2O": 1.0, "OM": 40.0},
        "price_per_kg_sar": 0.30,
        "method": "broadcast and incorporate",
        "method_ar": "نثر وخلط بالتربة",
    },
    "cow_manure": {
        "name": "Composted Cow Manure",
        "name_ar": "سماد بقري مخمر",
        "formula": "organic",
        "type": "organic",
        "type_ar": "عضوي",
        "nutrients": {"N": 2.0, "P2O5": 1.5, "K2O": 2.0, "OM": 30.0},
        "price_per_kg_sar": 0.20,
        "method": "broadcast and incorporate",
        "method_ar": "نثر وخلط بالتربة",
    },
    "chicken_manure": {
        "name": "Composted Chicken Manure",
        "name_ar": "سماد دجاج مخمر",
        "formula": "organic",
        "type": "organic",
        "type_ar": "عضوي",
        "nutrients": {"N": 3.5, "P2O5": 3.0, "K2O": 2.5, "OM": 25.0},
        "price_per_kg_sar": 0.35,
        "method": "broadcast and incorporate",
        "method_ar": "نثر وخلط بالتربة",
    },
    "humic_acid": {
        "name": "Humic Acid",
        "name_ar": "حمض الهيوميك",
        "formula": "organic",
        "type": "organic",
        "type_ar": "عضوي",
        "nutrients": {"OM": 65.0, "humic": 12.0},
        "price_per_kg_sar": 15.00,
        "method": "soil drench or fertigation",
        "method_ar": "غمر أرضي أو تسميد بالري",
    },
    # Soil amendments
    "agricultural_lime": {
        "name": "Agricultural Lime (CaCO3)",
        "name_ar": "جير زراعي",
        "formula": "CaCO3",
        "type": "amendment",
        "type_ar": "معدل تربة",
        "nutrients": {"Ca": 40.0},
        "price_per_kg_sar": 0.50,
        "method": "broadcast and incorporate",
        "method_ar": "نثر وخلط بالتربة",
        "purpose": "Raise soil pH",
        "purpose_ar": "رفع درجة حموضة التربة",
    },
    "dolomitic_lime": {
        "name": "Dolomitic Lime",
        "name_ar": "جير دولوميتي",
        "formula": "CaMg(CO3)2",
        "type": "amendment",
        "type_ar": "معدل تربة",
        "nutrients": {"Ca": 22.0, "Mg": 12.0},
        "price_per_kg_sar": 0.60,
        "method": "broadcast and incorporate",
        "method_ar": "نثر وخلط بالتربة",
        "purpose": "Raise pH and supply Mg",
        "purpose_ar": "رفع الحموضة وتوفير المغنيسيوم",
    },
    "gypsum": {
        "name": "Agricultural Gypsum",
        "name_ar": "جبس زراعي",
        "formula": "CaSO4.2H2O",
        "type": "amendment",
        "type_ar": "معدل تربة",
        "nutrients": {"Ca": 23.0, "S": 19.0},
        "price_per_kg_sar": 0.40,
        "method": "broadcast and irrigate",
        "method_ar": "نثر وري",
        "purpose": "Reclaim sodic soils, improve structure",
        "purpose_ar": "استصلاح التربة الصودية، تحسين البنية",
    },
    "elemental_sulfur": {
        "name": "Elemental Sulfur",
        "name_ar": "كبريت عنصري",
        "formula": "S",
        "type": "amendment",
        "type_ar": "معدل تربة",
        "nutrients": {"S": 90.0},
        "price_per_kg_sar": 2.00,
        "method": "broadcast and incorporate",
        "method_ar": "نثر وخلط بالتربة",
        "purpose": "Lower soil pH",
        "purpose_ar": "خفض درجة حموضة التربة",
    },
}

# Crop nutrient requirements (kg/ha for target yield)
CROP_REQUIREMENTS: dict[str, dict] = {
    "wheat": {
        "name_ar": "قمح",
        "N": 120,
        "P2O5": 50,
        "K2O": 80,
        "target_yield": 5.0,
        "cl_sensitive": False,
        "growth_stages": ["seeding", "tillering", "stem_elongation", "heading"],
    },
    "barley": {
        "name_ar": "شعير",
        "N": 100,
        "P2O5": 45,
        "K2O": 70,
        "target_yield": 4.5,
        "cl_sensitive": False,
    },
    "tomato": {
        "name_ar": "طماطم",
        "N": 180,
        "P2O5": 60,
        "K2O": 270,
        "target_yield": 60.0,
        "cl_sensitive": True,
    },
    "cucumber": {
        "name_ar": "خيار",
        "N": 150,
        "P2O5": 50,
        "K2O": 200,
        "target_yield": 50.0,
        "cl_sensitive": True,
    },
    "date_palm": {
        "name_ar": "نخيل",
        "N": 1.5,
        "P2O5": 0.5,
        "K2O": 2.0,
        "per_tree": True,
        "target_yield": 100.0,
        "cl_sensitive": False,
    },
    "alfalfa": {
        "name_ar": "برسيم",
        "N": 0,
        "P2O5": 60,
        "K2O": 150,
        "target_yield": 15.0,
        "cl_sensitive": False,
    },
    "potato": {
        "name_ar": "بطاطس",
        "N": 175,
        "P2O5": 55,
        "K2O": 245,
        "target_yield": 35.0,
        "cl_sensitive": True,
    },
    "onion": {
        "name_ar": "بصل",
        "N": 120,
        "P2O5": 40,
        "K2O": 100,
        "target_yield": 40.0,
        "cl_sensitive": False,
    },
}


@dataclass
class RecommendationConfig:
    """Configuration for amendment recommendations - إعدادات توصيات التعديل"""

    # Economic factors
    max_budget_per_ha: Decimal | None = None
    currency: str = "SAR"

    # Environmental constraints
    water_body_nearby: bool = False
    buffer_zone_m: float = 0.0

    # Product preferences
    prefer_organic: bool = False
    available_products: list[str] | None = None

    # Application constraints
    has_fertigation: bool = True
    has_spreader: bool = True

    # Language
    language: str = "both"


class SoilAmendmentRecommender:
    """
    Generates soil amendment recommendations based on test results.
    مولد توصيات تعديل التربة بناءً على نتائج التحليل

    Usage:
        recommender = SoilAmendmentRecommender()
        plan = recommender.generate_plan(soil_test, "wheat")
        print(plan.summary_ar)
    """

    def __init__(
        self,
        config: RecommendationConfig | None = None,
        custom_products: dict | None = None,
    ):
        """
        Initialize the recommender.

        Args:
            config: Recommendation configuration
            custom_products: Custom product definitions to add/override
        """
        self.config = config or RecommendationConfig()
        self.products = {**FERTILIZER_PRODUCTS}
        if custom_products:
            self.products.update(custom_products)
        self.crop_requirements = CROP_REQUIREMENTS
        self.interpreter = SoilTestInterpreter()

    def generate_plan(
        self,
        soil_test: SoilTestResult,
        crop: str,
        target_yield: float | None = None,
        field_area_ha: float = 1.0,
    ) -> AmendmentPlan:
        """
        Generate a complete amendment plan for a field.

        Args:
            soil_test: The soil test results
            crop: Target crop
            target_yield: Target yield (uses default if not specified)
            field_area_ha: Field area in hectares

        Returns:
            AmendmentPlan with all recommendations
        """
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        crop_data = self.crop_requirements.get(crop.lower(), {})
        crop_ar = crop_data.get("name_ar", crop)

        # Get interpretation
        interpretation = self.interpreter.interpret(soil_test, crop)

        # Get target yield
        target_yield = target_yield or crop_data.get("target_yield", 5.0)

        # Generate recommendations
        recommendations: list[AmendmentRecommendation] = []

        # 1. Soil property amendments (pH, salinity, organic matter)
        if soil_test.soil_properties:
            recommendations.extend(self._recommend_soil_amendments(soil_test.soil_properties, crop_data))

        # 2. Macronutrient fertilizers
        recommendations.extend(self._recommend_macronutrients(interpretation, soil_test, crop_data, target_yield))

        # 3. Micronutrient amendments
        recommendations.extend(self._recommend_micronutrients(interpretation, soil_test, crop_data))

        # 4. Organic matter
        if soil_test.soil_properties and soil_test.soil_properties.organic_matter_percent < 2.0:
            recommendations.extend(self._recommend_organic_amendments(soil_test.soil_properties))

        # Sort by priority
        recommendations.sort(key=lambda x: x.priority)

        # Calculate totals
        total_cost = sum(r.estimated_cost_per_ha for r in recommendations)
        total_n = sum(r.nutrients_supplied.get("N", 0) * r.application_rate_kg_ha / 100 for r in recommendations)
        total_p = sum(r.nutrients_supplied.get("P2O5", 0) * r.application_rate_kg_ha / 100 for r in recommendations)
        total_k = sum(r.nutrients_supplied.get("K2O", 0) * r.application_rate_kg_ha / 100 for r in recommendations)

        # Generate phases/timeline
        phases = self._generate_application_phases(recommendations, crop)

        # Generate summary
        summary_en, summary_ar = self._generate_plan_summary(recommendations, crop, crop_ar, total_cost)

        # Estimate yield improvement
        yield_improvement = self._estimate_yield_improvement(interpretation, recommendations)

        # Calculate ROI
        expected_revenue_improvement = Decimal(str(yield_improvement * target_yield * 1500))  # Approximate
        roi = float(expected_revenue_improvement - total_cost) / float(total_cost) * 100 if total_cost > 0 else 0

        return AmendmentPlan(
            plan_id=plan_id,
            soil_test_id=soil_test.id,
            field_id=soil_test.field_id,
            tenant_id=soil_test.tenant_id,
            crop=crop,
            crop_ar=crop_ar,
            target_yield_tons_ha=target_yield,
            field_area_ha=field_area_ha,
            recommendations=recommendations,
            total_estimated_cost=total_cost,
            total_n_kg_ha=total_n,
            total_p_kg_ha=total_p,
            total_k_kg_ha=total_k,
            phases=phases,
            expected_yield_improvement_percent=yield_improvement,
            expected_roi=roi,
            summary_en=summary_en,
            summary_ar=summary_ar,
            valid_until=datetime.now(UTC) + timedelta(days=180),
        )

    def _recommend_soil_amendments(
        self,
        properties: SoilProperties,
        crop_data: dict,
    ) -> list[AmendmentRecommendation]:
        """Generate soil property amendment recommendations"""
        recommendations = []

        # pH adjustment
        if properties.ph < 5.5:
            # Need lime
            lime_rate = self._calculate_lime_requirement(properties)
            recommendations.append(
                self._create_recommendation(
                    "agricultural_lime" if lime_rate < 3000 else "dolomitic_lime",
                    lime_rate,
                    target="pH",
                    priority=1,
                    reason_en=f"Soil pH ({properties.ph}) is too low; lime needed to raise to optimal range",
                    reason_ar=f"درجة حموضة التربة ({properties.ph}) منخفضة جداً؛ يحتاج جير لرفعها للنطاق المثالي",
                )
            )
        elif properties.ph > 8.5:
            # Need sulfur
            sulfur_rate = self._calculate_sulfur_requirement(properties)
            recommendations.append(
                self._create_recommendation(
                    "elemental_sulfur",
                    sulfur_rate,
                    target="pH",
                    priority=2,
                    reason_en=f"Soil pH ({properties.ph}) is too high; sulfur needed to lower",
                    reason_ar=f"درجة حموضة التربة ({properties.ph}) مرتفعة جداً؛ يحتاج كبريت لخفضها",
                )
            )

        # Sodicity
        if properties.is_sodic or properties.esp > 15 or properties.sar > 13:
            gypsum_rate = self._calculate_gypsum_requirement(properties)
            recommendations.append(
                self._create_recommendation(
                    "gypsum",
                    gypsum_rate,
                    target="sodicity",
                    priority=1,
                    reason_en=f"Soil is sodic (ESP: {properties.esp}%, SAR: {properties.sar}); gypsum needed for reclamation",
                    reason_ar=f"التربة صودية (ESP: {properties.esp}%، SAR: {properties.sar})؛ يحتاج جبس للاستصلاح",
                )
            )

        return recommendations

    def _recommend_macronutrients(
        self,
        interpretation: InterpretationReport,
        soil_test: SoilTestResult,
        crop_data: dict,
        target_yield: float,
    ) -> list[AmendmentRecommendation]:
        """Generate macronutrient fertilizer recommendations"""
        recommendations = []

        # Calculate requirements
        n_required = crop_data.get("N", 100) * (target_yield / crop_data.get("target_yield", 5.0))
        p_required = crop_data.get("P2O5", 50) * (target_yield / crop_data.get("target_yield", 5.0))
        k_required = crop_data.get("K2O", 80) * (target_yield / crop_data.get("target_yield", 5.0))

        # Adjust based on soil test levels
        n_interp = next((i for i in interpretation.interpretations if i.nutrient_code == "N"), None)
        p_interp = next((i for i in interpretation.interpretations if i.nutrient_code == "P"), None)
        k_interp = next((i for i in interpretation.interpretations if i.nutrient_code == "K"), None)

        # Soil contribution estimates (simplified)
        n_soil = 0
        p_soil = 0
        k_soil = 0

        if soil_test.macronutrients:
            n_soil = soil_test.macronutrients.available_nitrogen_ppm * 2  # ppm to kg/ha estimate
            p_soil = soil_test.macronutrients.phosphorus_ppm * 2
            k_soil = soil_test.macronutrients.potassium_ppm * 1.2

        # Net requirements
        n_needed = max(0, n_required - n_soil)
        p_needed = max(0, p_required - p_soil)
        k_needed = max(0, k_required - k_soil)

        # Nitrogen
        if n_needed > 0:
            n_product = "urea"
            if soil_test.soil_properties and soil_test.soil_properties.ph > 7.5:
                # Prefer ammonium sulfate for alkaline soils
                n_product = "ammonium_sulfate"

            n_rate = n_needed / (self.products[n_product]["nutrients"]["N"] / 100)
            priority = (
                1 if n_interp and n_interp.status in [NutrientStatus.DEFICIENT, NutrientStatus.VERY_DEFICIENT] else 2
            )

            recommendations.append(
                self._create_recommendation(
                    n_product,
                    n_rate,
                    target="N",
                    priority=priority,
                    reason_en=f"Nitrogen required: {n_needed:.0f} kg/ha for target yield",
                    reason_ar=f"النيتروجين المطلوب: {n_needed:.0f} كجم/هـ للإنتاجية المستهدفة",
                )
            )

        # Phosphorus
        if p_needed > 0:
            p_product = "dap"
            if soil_test.soil_properties and soil_test.soil_properties.ec_ds_m > 4:
                # Use MAP or TSP to avoid adding more N in saline conditions
                p_product = "tsp"

            p_rate = p_needed / (self.products[p_product]["nutrients"]["P2O5"] / 100)
            priority = (
                1 if p_interp and p_interp.status in [NutrientStatus.DEFICIENT, NutrientStatus.VERY_DEFICIENT] else 2
            )

            recommendations.append(
                self._create_recommendation(
                    p_product,
                    p_rate,
                    target="P",
                    priority=priority,
                    reason_en=f"Phosphorus required: {p_needed:.0f} kg P2O5/ha",
                    reason_ar=f"الفسفور المطلوب: {p_needed:.0f} كجم P2O5/هـ",
                )
            )

        # Potassium
        if k_needed > 0:
            k_product = "mop"
            if crop_data.get("cl_sensitive", False):
                k_product = "sop"

            k_rate = k_needed / (self.products[k_product]["nutrients"]["K2O"] / 100)
            priority = (
                2 if k_interp and k_interp.status in [NutrientStatus.DEFICIENT, NutrientStatus.VERY_DEFICIENT] else 3
            )

            recommendations.append(
                self._create_recommendation(
                    k_product,
                    k_rate,
                    target="K",
                    priority=priority,
                    reason_en=f"Potassium required: {k_needed:.0f} kg K2O/ha",
                    reason_ar=f"البوتاسيوم المطلوب: {k_needed:.0f} كجم K2O/هـ",
                )
            )

        return recommendations

    def _recommend_micronutrients(
        self,
        interpretation: InterpretationReport,
        soil_test: SoilTestResult,
        crop_data: dict,
    ) -> list[AmendmentRecommendation]:
        """Generate micronutrient recommendations"""
        recommendations = []

        # Check each micronutrient
        micro_products = {
            "Fe": ("iron_chelate", "iron_sulfate"),
            "Zn": ("zinc_sulfate",),
            "Mn": ("manganese_sulfate",),
            "Cu": ("copper_sulfate",),
            "B": ("borax", "boric_acid"),
            "Mo": ("sodium_molybdate",),
        }

        micro_rates = {
            "Fe": 5.0,  # kg/ha for iron chelate
            "Zn": 10.0,
            "Mn": 10.0,
            "Cu": 5.0,
            "B": 2.0,
            "Mo": 0.2,
        }

        for interp in interpretation.interpretations:
            if interp.nutrient_code in micro_products:
                if interp.status in [
                    NutrientStatus.DEFICIENT,
                    NutrientStatus.VERY_DEFICIENT,
                    NutrientStatus.LOW,
                ]:
                    product_options = micro_products[interp.nutrient_code]

                    # Choose product based on soil pH
                    product = product_options[0]
                    if interp.nutrient_code == "Fe" and soil_test.soil_properties:
                        if soil_test.soil_properties.ph > 7.5:
                            product = "iron_chelate"  # More effective in alkaline soil
                        else:
                            product = "iron_sulfate"
                    elif interp.nutrient_code == "B":
                        if self.config.has_fertigation:
                            product = "boric_acid"
                        else:
                            product = "borax"

                    rate = micro_rates.get(interp.nutrient_code, 5.0)
                    if interp.status == NutrientStatus.VERY_DEFICIENT:
                        rate *= 1.5

                    recommendations.append(
                        self._create_recommendation(
                            product,
                            rate,
                            target=interp.nutrient_code,
                            priority=3 if interp.status == NutrientStatus.LOW else 2,
                            reason_en=f"{interp.nutrient_name} is {interp.status.value} ({interp.value:.2f} {interp.unit})",
                            reason_ar=f"{interp.nutrient_name_ar} {interp.status_description_ar} ({interp.value:.2f} {interp.unit})",
                        )
                    )

        return recommendations

    def _recommend_organic_amendments(
        self,
        properties: SoilProperties,
    ) -> list[AmendmentRecommendation]:
        """Generate organic matter recommendations"""
        recommendations = []

        om = properties.organic_matter_percent
        if om < 1.0:
            rate = 10000  # 10 tons/ha
            priority = 2
            message = "very low"
            message_ar = "منخفض جداً"
        elif om < 2.0:
            rate = 5000  # 5 tons/ha
            priority = 3
            message = "low"
            message_ar = "منخفض"
        else:
            return recommendations

        # Choose product
        product = "compost"
        if self.config.prefer_organic:
            product = "cow_manure"

        recommendations.append(
            self._create_recommendation(
                product,
                rate,
                target="OM",
                priority=priority,
                reason_en=f"Organic matter is {message} ({om:.1f}%); add organic amendments",
                reason_ar=f"المادة العضوية {message_ar} ({om:.1f}%)؛ أضف تعديلات عضوية",
            )
        )

        # Also recommend humic acid
        recommendations.append(
            self._create_recommendation(
                "humic_acid",
                20.0,  # 20 kg/ha
                target="OM",
                priority=priority + 1,
                reason_en="Humic acid to improve soil structure and nutrient availability",
                reason_ar="حمض الهيوميك لتحسين بنية التربة وتوفر العناصر الغذائية",
            )
        )

        return recommendations

    def _create_recommendation(
        self,
        product_id: str,
        rate_kg_ha: float,
        target: str,
        priority: int,
        reason_en: str,
        reason_ar: str,
    ) -> AmendmentRecommendation:
        """Create an amendment recommendation from product"""
        product = self.products.get(product_id, {})

        return AmendmentRecommendation(
            amendment_id=f"rec_{uuid.uuid4().hex[:8]}",
            amendment_type=product.get("type", "fertilizer"),
            amendment_type_ar=product.get("type_ar", "سماد"),
            product_name=product.get("name", product_id),
            product_name_ar=product.get("name_ar", product_id),
            product_formula=product.get("formula", ""),
            application_rate_kg_ha=round(rate_kg_ha, 1),
            application_method=product.get("method", "broadcast"),
            application_method_ar=product.get("method_ar", "نثر"),
            target_nutrient=target,
            nutrients_supplied=product.get("nutrients", {}),
            estimated_cost_per_ha=Decimal(str(rate_kg_ha * product.get("price_per_kg_sar", 0))),
            priority=priority,
            warnings=product.get("warnings", []),
            warnings_ar=product.get("warnings_ar", []),
            reason_en=reason_en,
            reason_ar=reason_ar,
        )

    def _calculate_lime_requirement(self, properties: SoilProperties) -> float:
        """Calculate lime requirement in kg/ha"""
        target_ph = 6.5
        current_ph = properties.ph

        if current_ph >= target_ph:
            return 0

        # Simplified calculation based on buffer pH or CEC
        if properties.ph_buffer:
            # More accurate with buffer pH
            lime_factor = 2000  # kg lime per unit pH change
        else:
            # Estimate from CEC
            cec = properties.cec_meq_100g or 15
            lime_factor = cec * 100  # kg lime per unit pH change

        lime_needed = (target_ph - current_ph) * lime_factor
        return min(max(500, lime_needed), 10000)  # Limit between 500-10000 kg/ha

    def _calculate_sulfur_requirement(self, properties: SoilProperties) -> float:
        """Calculate elemental sulfur requirement in kg/ha"""
        target_ph = 7.5
        current_ph = properties.ph

        if current_ph <= target_ph:
            return 0

        # Sulfur requirement depends on soil type and CaCO3 content
        base_rate = 200  # kg S per unit pH reduction in non-calcareous soil

        # Adjust for CaCO3 content
        if properties.caco3_percent > 5:
            # Calcareous soils need more sulfur
            base_rate *= 1 + properties.caco3_percent / 10

        sulfur_needed = (current_ph - target_ph) * base_rate
        return min(max(100, sulfur_needed), 2000)  # Limit between 100-2000 kg/ha

    def _calculate_gypsum_requirement(self, properties: SoilProperties) -> float:
        """Calculate gypsum requirement for sodic soil reclamation in kg/ha"""
        if properties.esp <= 15 and properties.sar <= 13:
            return 0

        # Gypsum requirement based on ESP reduction needed
        target_esp = 10
        esp_to_reduce = max(0, properties.esp - target_esp)

        # Simplified calculation (actual depends on CEC and soil depth)
        cec = properties.cec_meq_100g or 15
        gypsum_needed = esp_to_reduce * cec * 86.4  # 86.4 kg gypsum per meq Na to replace

        return min(max(1000, gypsum_needed), 30000)  # Limit between 1-30 tons/ha

    def _generate_application_phases(
        self,
        recommendations: list[AmendmentRecommendation],
        crop: str,
    ) -> list[dict]:
        """Generate application timeline/phases"""
        phases = []

        # Phase 1: Soil amendments (before planting)
        soil_amendments = [r for r in recommendations if r.amendment_type in ["amendment", "organic"]]
        if soil_amendments:
            phases.append(
                {
                    "phase": 1,
                    "name": "Soil Preparation",
                    "name_ar": "تحضير التربة",
                    "timing": "2-4 weeks before planting",
                    "timing_ar": "2-4 أسابيع قبل الزراعة",
                    "recommendations": [r.amendment_id for r in soil_amendments],
                }
            )

        # Phase 2: Basal fertilizer (at planting)
        basal = [
            r
            for r in recommendations
            if r.target_nutrient in ["P", "K"] and r.amendment_type in ["phosphorus", "potassium"]
        ]
        if basal:
            phases.append(
                {
                    "phase": 2,
                    "name": "Basal Application",
                    "name_ar": "التسميد الأساسي",
                    "timing": "At planting",
                    "timing_ar": "عند الزراعة",
                    "recommendations": [r.amendment_id for r in basal],
                }
            )

        # Phase 3: Top dressing (during growth)
        topdress = [
            r for r in recommendations if r.target_nutrient == "N" and r.amendment_type in ["nitrogen", "compound"]
        ]
        if topdress:
            phases.append(
                {
                    "phase": 3,
                    "name": "Top Dressing",
                    "name_ar": "التسميد السطحي",
                    "timing": "Split during active growth",
                    "timing_ar": "مقسم خلال النمو النشط",
                    "recommendations": [r.amendment_id for r in topdress],
                    "split": True,
                }
            )

        # Phase 4: Micronutrients
        micros = [r for r in recommendations if r.amendment_type == "micronutrient"]
        if micros:
            phases.append(
                {
                    "phase": 4,
                    "name": "Micronutrient Application",
                    "name_ar": "تطبيق العناصر الصغرى",
                    "timing": "Early to mid growth",
                    "timing_ar": "من بداية إلى منتصف النمو",
                    "recommendations": [r.amendment_id for r in micros],
                }
            )

        return phases

    def _generate_plan_summary(
        self,
        recommendations: list[AmendmentRecommendation],
        crop: str,
        crop_ar: str,
        total_cost: Decimal,
    ) -> tuple[str, str]:
        """Generate plan summary in both languages"""
        n_recs = len(recommendations)

        summary_en = f"Amendment plan for {crop} includes {n_recs} recommendation(s) "
        summary_en += f"with estimated total cost of {total_cost:.2f} SAR/ha. "

        urgent = [r for r in recommendations if r.priority <= 2]
        if urgent:
            summary_en += "Priority actions: "
            summary_en += ", ".join([r.product_name for r in urgent[:3]])
            summary_en += "."

        summary_ar = f"خطة التعديل لمحصول {crop_ar} تتضمن {n_recs} توصية "
        summary_ar += f"بتكلفة إجمالية تقديرية {total_cost:.2f} ريال/هـ. "

        if urgent:
            summary_ar += "الإجراءات ذات الأولوية: "
            summary_ar += "، ".join([r.product_name_ar for r in urgent[:3]])
            summary_ar += "."

        return summary_en, summary_ar

    def _estimate_yield_improvement(
        self,
        interpretation: InterpretationReport,
        recommendations: list[AmendmentRecommendation],
    ) -> float:
        """Estimate expected yield improvement percentage"""
        improvement = 0.0

        # Base improvement from addressing deficiencies
        for deficiency in interpretation.deficiencies:
            if deficiency in ["Nitrogen", "Phosphorus", "Potassium"]:
                improvement += 10.0  # Major nutrients
            else:
                improvement += 5.0  # Secondary/micro

        # Adjustment for soil property corrections
        soil_amendments = [r for r in recommendations if r.amendment_type == "amendment"]
        if soil_amendments:
            improvement += 5.0

        # Cap at reasonable maximum
        return min(improvement, 50.0)


# Convenience functions
def generate_amendment_plan(
    soil_test: SoilTestResult,
    crop: str,
    target_yield: float | None = None,
    field_area_ha: float = 1.0,
) -> AmendmentPlan:
    """
    Quick generation of amendment plan.

    Args:
        soil_test: Soil test results
        crop: Target crop
        target_yield: Target yield in tons/ha
        field_area_ha: Field area

    Returns:
        AmendmentPlan
    """
    recommender = SoilAmendmentRecommender()
    return recommender.generate_plan(soil_test, crop, target_yield, field_area_ha)


def get_available_products() -> list[dict]:
    """
    Get list of available fertilizer products.

    Returns:
        List of product dictionaries
    """
    return [
        {
            "id": pid,
            "name": p["name"],
            "name_ar": p["name_ar"],
            "type": p["type"],
            "nutrients": p["nutrients"],
            "price_per_kg": p["price_per_kg_sar"],
        }
        for pid, p in FERTILIZER_PRODUCTS.items()
    ]


def get_crop_requirements(crop: str) -> dict | None:
    """
    Get nutrient requirements for a crop.

    Args:
        crop: Crop name

    Returns:
        Requirements dictionary or None
    """
    return CROP_REQUIREMENTS.get(crop.lower())


def calculate_fertilizer_rate(
    nutrient_needed_kg_ha: float,
    fertilizer_nutrient_percent: float,
) -> float:
    """
    Calculate fertilizer application rate.

    Args:
        nutrient_needed_kg_ha: Amount of nutrient needed in kg/ha
        fertilizer_nutrient_percent: Nutrient content in fertilizer (%)

    Returns:
        Fertilizer rate in kg/ha
    """
    if fertilizer_nutrient_percent <= 0:
        return 0.0
    return nutrient_needed_kg_ha / (fertilizer_nutrient_percent / 100)
