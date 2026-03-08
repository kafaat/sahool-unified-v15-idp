"""
Soil Test Result Interpreter - مفسر نتائج تحليل التربة

Interprets soil test results to determine nutrient status levels
(deficient, adequate, optimal, excessive) based on established thresholds.

Supports:
- Regional calibration for Middle East soils
- Crop-specific interpretation
- pH and EC impact on nutrient availability
- Bilingual explanations (Arabic/English)

Author: SAHOOL Platform Team
Version: 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import (
    ExtractionMethod,
    InterpretationReport,
    MacronutrientResults,
    MicronutrientResults,
    NutrientInterpretation,
    NutrientStatus,
    SoilProperties,
    SoilTestResult,
    SoilType,
)

# Nutrient thresholds for interpretation (ppm unless noted)
# Calibrated for Middle East alkaline calcareous soils
NUTRIENT_THRESHOLDS: dict[str, dict] = {
    # Nitrogen (available N: NO3 + NH4)
    "N": {
        "very_deficient": 5,
        "deficient": 10,
        "low": 20,
        "adequate": 40,
        "high": 60,
        "excessive": 100,
        "unit": "ppm",
        "unit_ar": "جزء بالمليون",
        "name": "Nitrogen",
        "name_ar": "نيتروجين",
    },
    # Phosphorus - Olsen extraction (for alkaline soils)
    "P_olsen": {
        "very_deficient": 3,
        "deficient": 5,
        "low": 10,
        "adequate": 20,
        "high": 40,
        "excessive": 80,
        "unit": "ppm",
        "unit_ar": "جزء بالمليون",
        "name": "Phosphorus (Olsen)",
        "name_ar": "فسفور (أولسن)",
    },
    # Phosphorus - Mehlich-3 extraction
    "P_mehlich": {
        "very_deficient": 10,
        "deficient": 15,
        "low": 25,
        "adequate": 40,
        "high": 80,
        "excessive": 150,
        "unit": "ppm",
        "unit_ar": "جزء بالمليون",
        "name": "Phosphorus (Mehlich-3)",
        "name_ar": "فسفور (ميليك-3)",
    },
    # Potassium
    "K": {
        "very_deficient": 50,
        "deficient": 80,
        "low": 120,
        "adequate": 180,
        "high": 280,
        "excessive": 500,
        "unit": "ppm",
        "unit_ar": "جزء بالمليون",
        "name": "Potassium",
        "name_ar": "بوتاسيوم",
    },
    # Calcium
    "Ca": {
        "very_deficient": 200,
        "deficient": 400,
        "low": 800,
        "adequate": 1500,
        "high": 3000,
        "excessive": 6000,
        "unit": "ppm",
        "unit_ar": "جزء بالمليون",
        "name": "Calcium",
        "name_ar": "كالسيوم",
    },
    # Magnesium
    "Mg": {
        "very_deficient": 25,
        "deficient": 50,
        "low": 100,
        "adequate": 200,
        "high": 400,
        "excessive": 800,
        "unit": "ppm",
        "unit_ar": "جزء بالمليون",
        "name": "Magnesium",
        "name_ar": "مغنيسيوم",
    },
    # Sulfur
    "S": {
        "very_deficient": 3,
        "deficient": 6,
        "low": 10,
        "adequate": 20,
        "high": 40,
        "excessive": 100,
        "unit": "ppm",
        "unit_ar": "جزء بالمليون",
        "name": "Sulfur",
        "name_ar": "كبريت",
    },
    # Iron - DTPA extraction
    "Fe": {
        "very_deficient": 2.0,
        "deficient": 4.0,
        "low": 6.0,
        "adequate": 10.0,
        "high": 25.0,
        "excessive": 100.0,
        "unit": "ppm",
        "unit_ar": "جزء بالمليون",
        "name": "Iron",
        "name_ar": "حديد",
    },
    # Zinc - DTPA extraction
    "Zn": {
        "very_deficient": 0.3,
        "deficient": 0.5,
        "low": 1.0,
        "adequate": 2.0,
        "high": 5.0,
        "excessive": 20.0,
        "unit": "ppm",
        "unit_ar": "جزء بالمليون",
        "name": "Zinc",
        "name_ar": "زنك",
    },
    # Manganese - DTPA extraction
    "Mn": {
        "very_deficient": 1.0,
        "deficient": 2.0,
        "low": 4.0,
        "adequate": 8.0,
        "high": 20.0,
        "excessive": 100.0,
        "unit": "ppm",
        "unit_ar": "جزء بالمليون",
        "name": "Manganese",
        "name_ar": "منجنيز",
    },
    # Copper - DTPA extraction
    "Cu": {
        "very_deficient": 0.1,
        "deficient": 0.2,
        "low": 0.5,
        "adequate": 1.0,
        "high": 3.0,
        "excessive": 20.0,
        "unit": "ppm",
        "unit_ar": "جزء بالمليون",
        "name": "Copper",
        "name_ar": "نحاس",
    },
    # Boron - Hot water extraction
    "B": {
        "very_deficient": 0.2,
        "deficient": 0.3,
        "low": 0.5,
        "adequate": 1.0,
        "high": 2.0,
        "excessive": 5.0,
        "toxic": 10.0,
        "unit": "ppm",
        "unit_ar": "جزء بالمليون",
        "name": "Boron",
        "name_ar": "بورون",
    },
    # Molybdenum
    "Mo": {
        "very_deficient": 0.01,
        "deficient": 0.05,
        "low": 0.1,
        "adequate": 0.2,
        "high": 0.5,
        "excessive": 2.0,
        "unit": "ppm",
        "unit_ar": "جزء بالمليون",
        "name": "Molybdenum",
        "name_ar": "موليبدنوم",
    },
}

# Soil property thresholds
SOIL_PROPERTY_THRESHOLDS: dict[str, dict] = {
    "pH": {
        "very_acidic": 5.0,
        "acidic": 5.5,
        "slightly_acidic": 6.0,
        "neutral_low": 6.5,
        "neutral_high": 7.5,
        "slightly_alkaline": 8.0,
        "alkaline": 8.5,
        "very_alkaline": 9.0,
        "optimal_low": 6.0,
        "optimal_high": 7.5,
    },
    "EC": {  # dS/m
        "non_saline": 2.0,
        "slightly_saline": 4.0,
        "moderately_saline": 8.0,
        "strongly_saline": 16.0,
        "very_strongly_saline": 32.0,
    },
    "OM": {  # Organic matter %
        "very_low": 0.5,
        "low": 1.0,
        "moderate": 2.0,
        "adequate": 3.0,
        "high": 5.0,
        "very_high": 10.0,
    },
    "CEC": {  # meq/100g
        "very_low": 5,
        "low": 10,
        "moderate": 20,
        "high": 30,
        "very_high": 50,
    },
    "CaCO3": {  # %
        "non_calcareous": 1,
        "slightly_calcareous": 5,
        "moderately_calcareous": 15,
        "strongly_calcareous": 25,
        "very_calcareous": 40,
    },
}

# Status translations
STATUS_TRANSLATIONS: dict[NutrientStatus, dict] = {
    NutrientStatus.VERY_DEFICIENT: {
        "en": "Very Deficient",
        "ar": "نقص شديد جداً",
        "description_en": "Severely low level requiring immediate correction",
        "description_ar": "مستوى منخفض جداً يتطلب تصحيح فوري",
    },
    NutrientStatus.DEFICIENT: {
        "en": "Deficient",
        "ar": "نقص",
        "description_en": "Below adequate level, supplementation recommended",
        "description_ar": "أقل من المستوى الكافي، يُنصح بالتسميد",
    },
    NutrientStatus.LOW: {
        "en": "Low",
        "ar": "منخفض",
        "description_en": "On the low side, may need supplementation",
        "description_ar": "في الحد الأدنى، قد يحتاج تسميد",
    },
    NutrientStatus.ADEQUATE: {
        "en": "Adequate",
        "ar": "كافي",
        "description_en": "Sufficient for crop needs",
        "description_ar": "كافٍ لاحتياجات المحصول",
    },
    NutrientStatus.OPTIMAL: {
        "en": "Optimal",
        "ar": "مثالي",
        "description_en": "Ideal level for crop production",
        "description_ar": "مستوى مثالي لإنتاج المحصول",
    },
    NutrientStatus.HIGH: {
        "en": "High",
        "ar": "مرتفع",
        "description_en": "Above optimal, reduce or skip application",
        "description_ar": "أعلى من المثالي، قلل أو توقف عن التسميد",
    },
    NutrientStatus.EXCESSIVE: {
        "en": "Excessive",
        "ar": "زائد",
        "description_en": "Too high, may cause toxicity or imbalance",
        "description_ar": "مرتفع جداً، قد يسبب سمية أو خلل في التوازن",
    },
    NutrientStatus.TOXIC: {
        "en": "Toxic",
        "ar": "سام",
        "description_en": "At levels that may harm crops",
        "description_ar": "في مستويات قد تضر المحصول",
    },
}

# Crop-specific sensitivity adjustments
# Multipliers for threshold adjustments by crop
CROP_SENSITIVITY: dict[str, dict[str, float]] = {
    "wheat": {
        "N": 1.0,
        "P": 1.0,
        "K": 1.0,
        "Fe": 0.8,
        "Zn": 1.2,
        "B": 0.9,
    },
    "barley": {
        "N": 0.9,
        "P": 1.0,
        "K": 1.0,
        "Fe": 0.8,
        "Zn": 1.0,
        "B": 0.8,
    },
    "tomato": {
        "N": 1.2,
        "P": 1.1,
        "K": 1.3,
        "Ca": 1.5,
        "Mg": 1.2,
        "B": 1.3,
    },
    "cucumber": {
        "N": 1.1,
        "P": 1.0,
        "K": 1.2,
        "Ca": 1.2,
        "Mg": 1.1,
        "B": 1.2,
    },
    "date_palm": {
        "N": 0.8,
        "P": 0.9,
        "K": 1.3,
        "Fe": 1.5,
        "Mn": 1.3,
        "Zn": 1.4,
    },
    "alfalfa": {
        "N": 0.3,
        "P": 1.2,
        "K": 1.4,
        "B": 1.5,
        "Mo": 1.5,
    },
    "potato": {
        "N": 1.1,
        "P": 1.2,
        "K": 1.4,
        "Ca": 1.0,
        "Mg": 1.1,
        "B": 1.0,
    },
    "onion": {
        "N": 1.0,
        "P": 1.0,
        "K": 1.1,
        "S": 1.5,
        "Cu": 1.2,
        "Zn": 1.1,
    },
}


@dataclass
class InterpretationConfig:
    """Configuration for soil test interpretation - إعدادات تفسير تحليل التربة"""

    # Regional adjustments
    region: str = "middle_east"
    soil_type: SoilType | None = None

    # Crop-specific
    crop: str | None = None

    # Extraction methods used
    p_extraction: ExtractionMethod = ExtractionMethod.OLSEN

    # pH adjustment factors
    apply_ph_corrections: bool = True

    # Language preference
    language: str = "both"  # "en", "ar", or "both"


class SoilTestInterpreter:
    """
    Interpreter for soil test results
    مفسر نتائج تحليل التربة

    Provides nutrient status interpretation based on soil test values,
    considering regional calibrations, crop requirements, and soil conditions.

    Usage:
        interpreter = SoilTestInterpreter()
        report = interpreter.interpret(soil_test_result)
        print(report.summary_ar)  # Arabic summary
    """

    def __init__(
        self,
        config: InterpretationConfig | None = None,
        custom_thresholds: dict | None = None,
    ):
        """
        Initialize the interpreter.

        Args:
            config: Interpretation configuration
            custom_thresholds: Custom threshold overrides
        """
        self.config = config or InterpretationConfig()
        self.thresholds = {**NUTRIENT_THRESHOLDS}
        if custom_thresholds:
            self.thresholds.update(custom_thresholds)
        self.property_thresholds = SOIL_PROPERTY_THRESHOLDS
        self.status_translations = STATUS_TRANSLATIONS
        self.crop_sensitivity = CROP_SENSITIVITY

    def interpret(
        self,
        soil_test: SoilTestResult,
        crop: str | None = None,
    ) -> InterpretationReport:
        """
        Generate complete interpretation report for a soil test.

        Args:
            soil_test: The soil test result to interpret
            crop: Optional crop for crop-specific interpretation

        Returns:
            InterpretationReport with all nutrient interpretations
        """
        crop = crop or self.config.crop
        interpretations: list[NutrientInterpretation] = []

        # Get pH for availability corrections
        ph = 7.0
        if soil_test.soil_properties:
            ph = soil_test.soil_properties.ph

        # Interpret macronutrients
        if soil_test.macronutrients:
            interpretations.extend(self._interpret_macronutrients(soil_test.macronutrients, ph, crop))

        # Interpret micronutrients
        if soil_test.micronutrients:
            interpretations.extend(self._interpret_micronutrients(soil_test.micronutrients, ph, crop))

        # Calculate overall scores and identify issues
        deficiencies = []
        deficiencies_ar = []
        excesses = []
        excesses_ar = []
        fertility_score = 100.0

        for interp in interpretations:
            if interp.status in [NutrientStatus.VERY_DEFICIENT, NutrientStatus.DEFICIENT]:
                deficiencies.append(interp.nutrient_name)
                deficiencies_ar.append(interp.nutrient_name_ar)
                fertility_score -= 10 if interp.status == NutrientStatus.DEFICIENT else 15
            elif interp.status == NutrientStatus.LOW:
                fertility_score -= 5
            elif interp.status in [NutrientStatus.EXCESSIVE, NutrientStatus.TOXIC]:
                excesses.append(interp.nutrient_name)
                excesses_ar.append(interp.nutrient_name_ar)
                fertility_score -= 8

        # Interpret soil properties
        ph_status, ph_status_ar = self._interpret_ph(ph)
        ec_status, ec_status_ar = "", ""
        om_status, om_status_ar = "", ""
        salinity_status, salinity_status_ar = "", ""

        if soil_test.soil_properties:
            ec_status, ec_status_ar = self._interpret_ec(soil_test.soil_properties.ec_ds_m)
            salinity_status = ec_status
            salinity_status_ar = ec_status_ar
            om_status, om_status_ar = self._interpret_om(soil_test.soil_properties.organic_matter_percent)

            # Adjust fertility score based on properties
            if soil_test.soil_properties.is_saline:
                fertility_score -= 10
            if soil_test.soil_properties.organic_matter_percent < 1.0:
                fertility_score -= 5

        # Clamp fertility score
        fertility_score = max(0, min(100, fertility_score))

        # Determine grade
        grade, grade_ar = self._score_to_grade(fertility_score)

        # Generate summary
        summary_en, summary_ar = self._generate_summary(
            deficiencies, excesses, ph_status, ec_status, om_status, fertility_score, crop
        )

        # Generate immediate actions
        immediate_actions, immediate_actions_ar = self._generate_immediate_actions(
            interpretations, soil_test.soil_properties
        )

        return InterpretationReport(
            soil_test_id=soil_test.id,
            field_id=soil_test.field_id,
            interpretations=interpretations,
            overall_fertility_score=fertility_score,
            overall_fertility_grade=grade,
            overall_fertility_grade_ar=grade_ar,
            deficiencies=deficiencies,
            deficiencies_ar=deficiencies_ar,
            excesses=excesses,
            excesses_ar=excesses_ar,
            ph_status=ph_status,
            ph_status_ar=ph_status_ar,
            salinity_status=salinity_status,
            salinity_status_ar=salinity_status_ar,
            organic_matter_status=om_status,
            organic_matter_status_ar=om_status_ar,
            summary_en=summary_en,
            summary_ar=summary_ar,
            immediate_actions=immediate_actions,
            immediate_actions_ar=immediate_actions_ar,
        )

    def interpret_single_nutrient(
        self,
        nutrient_code: str,
        value: float,
        ph: float = 7.0,
        crop: str | None = None,
    ) -> NutrientInterpretation:
        """
        Interpret a single nutrient value.

        Args:
            nutrient_code: Nutrient code (N, P, K, Fe, etc.)
            value: Nutrient value in ppm
            ph: Soil pH for availability corrections
            crop: Optional crop for sensitivity adjustment

        Returns:
            NutrientInterpretation object
        """
        # Get appropriate thresholds
        threshold_key = nutrient_code
        if nutrient_code == "P":
            if self.config.p_extraction == ExtractionMethod.OLSEN:
                threshold_key = "P_olsen"
            else:
                threshold_key = "P_mehlich"

        thresholds = self.thresholds.get(threshold_key, self.thresholds.get("N"))

        # Apply crop sensitivity adjustment
        adjusted_value = value
        if crop and crop.lower() in self.crop_sensitivity:
            sensitivity = self.crop_sensitivity[crop.lower()].get(nutrient_code, 1.0)
            # Higher sensitivity means crops need more, so we effectively lower the value
            adjusted_value = value / sensitivity

        # Apply pH corrections for availability
        if self.config.apply_ph_corrections:
            adjusted_value = self._apply_ph_correction(nutrient_code, adjusted_value, ph)

        # Determine status
        status = self._value_to_status(adjusted_value, thresholds)

        # Get translations
        trans = self.status_translations.get(status, {})

        # Determine if action is needed
        action_needed = status in [
            NutrientStatus.VERY_DEFICIENT,
            NutrientStatus.DEFICIENT,
            NutrientStatus.LOW,
            NutrientStatus.EXCESSIVE,
            NutrientStatus.TOXIC,
        ]

        # Determine priority
        priority = 5
        if status == NutrientStatus.VERY_DEFICIENT:
            priority = 1
        elif status == NutrientStatus.DEFICIENT:
            priority = 2
        elif status == NutrientStatus.TOXIC:
            priority = 1
        elif status == NutrientStatus.EXCESSIVE or status == NutrientStatus.LOW:
            priority = 3

        # Generate action description
        action_en, action_ar = self._generate_action_description(nutrient_code, status, value, thresholds)

        # Generate crop impact
        crop_impact, crop_impact_ar = self._generate_crop_impact(nutrient_code, status, crop)

        return NutrientInterpretation(
            nutrient_code=nutrient_code,
            nutrient_name=thresholds.get("name", nutrient_code),
            nutrient_name_ar=thresholds.get("name_ar", nutrient_code),
            value=value,
            unit=thresholds.get("unit", "ppm"),
            unit_ar=thresholds.get("unit_ar", "جزء بالمليون"),
            status=status,
            status_description=trans.get("description_en", ""),
            status_description_ar=trans.get("description_ar", ""),
            deficient_threshold=thresholds.get("deficient", 0),
            low_threshold=thresholds.get("low", 0),
            adequate_threshold=thresholds.get("adequate", 0),
            high_threshold=thresholds.get("high", 0),
            excessive_threshold=thresholds.get("excessive", 0),
            action_needed=action_needed,
            action_priority=priority,
            action_description=action_en,
            action_description_ar=action_ar,
            crop_impact=crop_impact,
            crop_impact_ar=crop_impact_ar,
        )

    def _interpret_macronutrients(
        self,
        macros: MacronutrientResults,
        ph: float,
        crop: str | None,
    ) -> list[NutrientInterpretation]:
        """Interpret all macronutrients"""
        interpretations = []

        # Nitrogen
        n_value = macros.available_nitrogen_ppm
        if n_value == 0:
            n_value = macros.nitrogen_total_percent * 10000 * 0.02  # Rough estimate
        interpretations.append(self.interpret_single_nutrient("N", n_value, ph, crop))

        # Phosphorus
        interpretations.append(self.interpret_single_nutrient("P", macros.phosphorus_ppm, ph, crop))

        # Potassium
        interpretations.append(self.interpret_single_nutrient("K", macros.potassium_ppm, ph, crop))

        # Calcium
        if macros.calcium_ppm > 0:
            interpretations.append(self.interpret_single_nutrient("Ca", macros.calcium_ppm, ph, crop))

        # Magnesium
        if macros.magnesium_ppm > 0:
            interpretations.append(self.interpret_single_nutrient("Mg", macros.magnesium_ppm, ph, crop))

        # Sulfur
        if macros.sulfur_ppm > 0:
            interpretations.append(self.interpret_single_nutrient("S", macros.sulfur_ppm, ph, crop))

        return interpretations

    def _interpret_micronutrients(
        self,
        micros: MicronutrientResults,
        ph: float,
        crop: str | None,
    ) -> list[NutrientInterpretation]:
        """Interpret all micronutrients"""
        interpretations = []

        # Iron
        if micros.iron_ppm > 0:
            interpretations.append(self.interpret_single_nutrient("Fe", micros.iron_ppm, ph, crop))

        # Zinc
        if micros.zinc_ppm > 0:
            interpretations.append(self.interpret_single_nutrient("Zn", micros.zinc_ppm, ph, crop))

        # Manganese
        if micros.manganese_ppm > 0:
            interpretations.append(self.interpret_single_nutrient("Mn", micros.manganese_ppm, ph, crop))

        # Copper
        if micros.copper_ppm > 0:
            interpretations.append(self.interpret_single_nutrient("Cu", micros.copper_ppm, ph, crop))

        # Boron
        if micros.boron_ppm > 0:
            interpretations.append(self.interpret_single_nutrient("B", micros.boron_ppm, ph, crop))

        # Molybdenum
        if micros.molybdenum_ppm > 0:
            interpretations.append(self.interpret_single_nutrient("Mo", micros.molybdenum_ppm, ph, crop))

        return interpretations

    def _value_to_status(
        self,
        value: float,
        thresholds: dict,
    ) -> NutrientStatus:
        """Convert a value to a status based on thresholds"""
        if value <= thresholds.get("very_deficient", 0):
            return NutrientStatus.VERY_DEFICIENT
        elif value <= thresholds.get("deficient", 0):
            return NutrientStatus.DEFICIENT
        elif value <= thresholds.get("low", 0):
            return NutrientStatus.LOW
        elif value <= thresholds.get("adequate", 0):
            return NutrientStatus.ADEQUATE
        elif value <= thresholds.get("high", 0):
            return NutrientStatus.OPTIMAL
        elif value <= thresholds.get("excessive", float("inf")):
            return NutrientStatus.HIGH
        elif "toxic" in thresholds and value > thresholds["toxic"]:
            return NutrientStatus.TOXIC
        else:
            return NutrientStatus.EXCESSIVE

    def _apply_ph_correction(
        self,
        nutrient: str,
        value: float,
        ph: float,
    ) -> float:
        """
        Apply pH correction to nutrient availability.

        In alkaline soils (pH > 7.5), micronutrients like Fe, Zn, Mn, Cu
        become less available. In acidic soils (pH < 6), Mo becomes less available.
        """
        correction_factor = 1.0

        if nutrient in ["Fe", "Zn", "Mn", "Cu"]:
            if ph > 7.5:
                # Decrease availability by ~10% per 0.5 pH unit above 7.5
                correction_factor = max(0.5, 1 - (ph - 7.5) * 0.2)
            elif ph < 6.0:
                # Increase availability in acidic soil
                correction_factor = min(1.5, 1 + (6.0 - ph) * 0.1)

        elif nutrient == "P":
            # P availability drops in very acidic or alkaline soils
            if ph < 6.0:
                correction_factor = max(0.6, 1 - (6.0 - ph) * 0.15)
            elif ph > 7.5:
                correction_factor = max(0.7, 1 - (ph - 7.5) * 0.1)

        elif nutrient == "Mo":
            # Mo availability increases with pH
            if ph < 6.0:
                correction_factor = max(0.5, 1 - (6.0 - ph) * 0.2)
            elif ph > 7.0:
                correction_factor = min(1.3, 1 + (ph - 7.0) * 0.1)

        elif nutrient == "B":
            # B availability decreases in alkaline soils
            if ph > 7.5:
                correction_factor = max(0.7, 1 - (ph - 7.5) * 0.15)

        return value * correction_factor

    def _interpret_ph(self, ph: float) -> tuple[str, str]:
        """Interpret soil pH"""
        thresholds = self.property_thresholds["pH"]

        if ph < thresholds["very_acidic"]:
            return "Very acidic - lime required", "حمضية جداً - يحتاج جير"
        elif ph < thresholds["acidic"]:
            return "Acidic - consider liming", "حمضية - يُنصح بالتجيير"
        elif ph < thresholds["slightly_acidic"]:
            return "Slightly acidic", "حمضية قليلاً"
        elif ph < thresholds["neutral_low"]:
            return "Optimal range", "في النطاق المثالي"
        elif ph <= thresholds["neutral_high"]:
            return "Optimal - neutral", "مثالي - متعادل"
        elif ph <= thresholds["slightly_alkaline"]:
            return "Slightly alkaline", "قلوية قليلاً"
        elif ph <= thresholds["alkaline"]:
            return "Alkaline - monitor micronutrients", "قلوية - راقب العناصر الصغرى"
        else:
            return (
                "Very alkaline - may need sulfur or acidifiers",
                "قلوية جداً - قد يحتاج كبريت أو محمضات",
            )

    def _interpret_ec(self, ec: float) -> tuple[str, str]:
        """Interpret electrical conductivity (salinity)"""
        thresholds = self.property_thresholds["EC"]

        if ec < thresholds["non_saline"]:
            return "Non-saline", "غير ملحي"
        elif ec < thresholds["slightly_saline"]:
            return "Slightly saline", "ملحي قليلاً"
        elif ec < thresholds["moderately_saline"]:
            return (
                "Moderately saline - sensitive crops affected",
                "ملحي بشكل معتدل - يؤثر على المحاصيل الحساسة",
            )
        elif ec < thresholds["strongly_saline"]:
            return "Strongly saline - most crops affected", "ملحي بشدة - يؤثر على معظم المحاصيل"
        else:
            return "Very strongly saline - few crops tolerate", "ملحي جداً - قليل من المحاصيل تتحمل"

    def _interpret_om(self, om: float) -> tuple[str, str]:
        """Interpret organic matter content"""
        thresholds = self.property_thresholds["OM"]

        if om < thresholds["very_low"]:
            return (
                "Very low - add organic matter urgently",
                "منخفض جداً - أضف المادة العضوية بشكل عاجل",
            )
        elif om < thresholds["low"]:
            return "Low - increase organic inputs", "منخفض - زد من المدخلات العضوية"
        elif om < thresholds["moderate"]:
            return "Moderate", "متوسط"
        elif om < thresholds["adequate"]:
            return "Adequate", "كافٍ"
        elif om < thresholds["high"]:
            return "High - excellent", "مرتفع - ممتاز"
        else:
            return "Very high", "مرتفع جداً"

    def _score_to_grade(self, score: float) -> tuple[str, str]:
        """Convert fertility score to letter grade"""
        if score >= 90:
            return "A", "ممتاز"
        elif score >= 80:
            return "B", "جيد جداً"
        elif score >= 70:
            return "C", "جيد"
        elif score >= 60:
            return "D", "مقبول"
        else:
            return "F", "ضعيف"

    def _generate_summary(
        self,
        deficiencies: list[str],
        excesses: list[str],
        ph_status: str,
        ec_status: str,
        om_status: str,
        fertility_score: float,
        crop: str | None,
    ) -> tuple[str, str]:
        """Generate summary text in both languages"""
        # English summary
        summary_en_parts = []

        if fertility_score >= 80:
            summary_en_parts.append(f"Overall soil fertility is good (score: {fertility_score:.0f}/100).")
        elif fertility_score >= 60:
            summary_en_parts.append(f"Soil fertility is moderate (score: {fertility_score:.0f}/100).")
        else:
            summary_en_parts.append(f"Soil fertility needs improvement (score: {fertility_score:.0f}/100).")

        if deficiencies:
            summary_en_parts.append(f"Deficient nutrients: {', '.join(deficiencies)}.")

        if excesses:
            summary_en_parts.append(f"Excess nutrients: {', '.join(excesses)}.")

        if "saline" in ec_status.lower():
            summary_en_parts.append(f"Salinity concern: {ec_status}.")

        if "acidic" in ph_status.lower() or "alkaline" in ph_status.lower():
            if "optimal" not in ph_status.lower():
                summary_en_parts.append(f"pH status: {ph_status}.")

        summary_en = " ".join(summary_en_parts)

        # Arabic summary
        summary_ar_parts = []

        if fertility_score >= 80:
            summary_ar_parts.append(f"خصوبة التربة العامة جيدة (الدرجة: {fertility_score:.0f}/100).")
        elif fertility_score >= 60:
            summary_ar_parts.append(f"خصوبة التربة متوسطة (الدرجة: {fertility_score:.0f}/100).")
        else:
            summary_ar_parts.append(f"خصوبة التربة تحتاج تحسين (الدرجة: {fertility_score:.0f}/100).")

        if deficiencies:
            deficiencies_ar_text = self._translate_nutrient_list(deficiencies)
            summary_ar_parts.append(f"عناصر ناقصة: {deficiencies_ar_text}.")

        if excesses:
            excesses_ar_text = self._translate_nutrient_list(excesses)
            summary_ar_parts.append(f"عناصر زائدة: {excesses_ar_text}.")

        summary_ar = " ".join(summary_ar_parts)

        return summary_en, summary_ar

    def _generate_immediate_actions(
        self,
        interpretations: list[NutrientInterpretation],
        properties: SoilProperties | None,
    ) -> tuple[list[str], list[str]]:
        """Generate list of immediate actions needed"""
        actions_en = []
        actions_ar = []

        # Sort by priority
        urgent = [i for i in interpretations if i.action_priority <= 2]
        for interp in sorted(urgent, key=lambda x: x.action_priority):
            if interp.action_description:
                actions_en.append(interp.action_description)
                actions_ar.append(interp.action_description_ar)

        # Add property-based actions
        if properties:
            if properties.is_saline:
                actions_en.append("Implement salinity management practices")
                actions_ar.append("تطبيق ممارسات إدارة الملوحة")
            if properties.organic_matter_percent < 1.0:
                actions_en.append("Add organic matter (compost, manure)")
                actions_ar.append("إضافة المادة العضوية (سماد عضوي، روث)")
            if properties.ph < 5.5:
                actions_en.append("Apply agricultural lime to raise pH")
                actions_ar.append("تطبيق الجير الزراعي لرفع درجة الحموضة")
            elif properties.ph > 8.5:
                actions_en.append("Consider sulfur application to lower pH")
                actions_ar.append("النظر في تطبيق الكبريت لخفض درجة الحموضة")

        return actions_en, actions_ar

    def _generate_action_description(
        self,
        nutrient: str,
        status: NutrientStatus,
        value: float,
        thresholds: dict,
    ) -> tuple[str, str]:
        """Generate action description for a nutrient"""
        nutrient_name = thresholds.get("name", nutrient)
        nutrient_name_ar = thresholds.get("name_ar", nutrient)

        if status == NutrientStatus.VERY_DEFICIENT:
            return (
                f"Apply {nutrient_name} fertilizer immediately at high rate",
                f"تطبيق سماد {nutrient_name_ar} فوراً بمعدل مرتفع",
            )
        elif status == NutrientStatus.DEFICIENT:
            return (
                f"Apply {nutrient_name} fertilizer as soon as possible",
                f"تطبيق سماد {nutrient_name_ar} في أقرب وقت ممكن",
            )
        elif status == NutrientStatus.LOW:
            return (
                f"Consider {nutrient_name} supplementation",
                f"النظر في إضافة {nutrient_name_ar}",
            )
        elif status in [NutrientStatus.ADEQUATE, NutrientStatus.OPTIMAL]:
            return (
                f"Maintain current {nutrient_name} management",
                f"الحفاظ على الإدارة الحالية لـ{nutrient_name_ar}",
            )
        elif status == NutrientStatus.HIGH:
            return (
                f"Reduce or skip {nutrient_name} application",
                f"تقليل أو تخطي تطبيق {nutrient_name_ar}",
            )
        elif status == NutrientStatus.EXCESSIVE:
            return (
                f"Do not apply {nutrient_name}; monitor for toxicity",
                f"لا تطبق {nutrient_name_ar}؛ راقب علامات السمية",
            )
        elif status == NutrientStatus.TOXIC:
            return (
                f"Warning: {nutrient_name} at toxic levels; remediation needed",
                f"تحذير: {nutrient_name_ar} في مستويات سامة؛ يحتاج معالجة",
            )
        return "", ""

    def _generate_crop_impact(
        self,
        nutrient: str,
        status: NutrientStatus,
        crop: str | None,
    ) -> tuple[str, str]:
        """Generate crop-specific impact description"""
        impacts = {
            "N": {
                "deficient": (
                    "Yellowing leaves, stunted growth, reduced yield",
                    "اصفرار الأوراق، تقزم النمو، انخفاض الإنتاجية",
                ),
                "excessive": (
                    "Excessive vegetative growth, delayed maturity, disease susceptibility",
                    "نمو خضري مفرط، تأخر النضج، قابلية للأمراض",
                ),
            },
            "P": {
                "deficient": (
                    "Purple discoloration, poor root development, delayed maturity",
                    "تلون أرجواني، ضعف نمو الجذور، تأخر النضج",
                ),
                "excessive": (
                    "May induce micronutrient deficiencies (Zn, Fe)",
                    "قد يسبب نقص العناصر الصغرى (زنك، حديد)",
                ),
            },
            "K": {
                "deficient": (
                    "Leaf edge scorch, weak stems, poor fruit quality",
                    "احتراق حواف الأوراق، سيقان ضعيفة، جودة ثمار منخفضة",
                ),
                "excessive": (
                    "May inhibit Ca and Mg uptake",
                    "قد يثبط امتصاص الكالسيوم والمغنيسيوم",
                ),
            },
            "Fe": {
                "deficient": (
                    "Interveinal chlorosis on young leaves",
                    "اصفرار بين العروق في الأوراق الحديثة",
                ),
                "excessive": ("Rare in field conditions", "نادر في ظروف الحقل"),
            },
            "Zn": {
                "deficient": (
                    "Small leaves, shortened internodes, mottled appearance",
                    "أوراق صغيرة، سلاميات قصيرة، مظهر مرقط",
                ),
                "excessive": (
                    "Stunted growth, Fe deficiency symptoms",
                    "تقزم النمو، أعراض نقص الحديد",
                ),
            },
            "B": {
                "deficient": (
                    "Hollow stems, cracked fruits, poor pollination",
                    "سيقان جوفاء، ثمار متشققة، تلقيح ضعيف",
                ),
                "excessive": ("Leaf tip and edge burn", "احتراق أطراف وحواف الأوراق"),
            },
        }

        status_key = (
            "deficient"
            if status
            in [
                NutrientStatus.VERY_DEFICIENT,
                NutrientStatus.DEFICIENT,
                NutrientStatus.LOW,
            ]
            else "excessive"
        )

        if nutrient in impacts and status_key in impacts[nutrient]:
            return impacts[nutrient][status_key]
        return "", ""

    def _translate_nutrient_list(self, nutrients: list[str]) -> str:
        """Translate a list of nutrient names to Arabic"""
        translations = {
            "Nitrogen": "نيتروجين",
            "Phosphorus": "فسفور",
            "Potassium": "بوتاسيوم",
            "Calcium": "كالسيوم",
            "Magnesium": "مغنيسيوم",
            "Sulfur": "كبريت",
            "Iron": "حديد",
            "Zinc": "زنك",
            "Manganese": "منجنيز",
            "Copper": "نحاس",
            "Boron": "بورون",
            "Molybdenum": "موليبدنوم",
        }
        return "، ".join([translations.get(n, n) for n in nutrients])


# Convenience functions
def interpret_soil_test(
    soil_test: SoilTestResult,
    crop: str | None = None,
) -> InterpretationReport:
    """
    Quick interpretation of a soil test result.

    Args:
        soil_test: The soil test to interpret
        crop: Optional crop for crop-specific interpretation

    Returns:
        InterpretationReport
    """
    interpreter = SoilTestInterpreter()
    return interpreter.interpret(soil_test, crop)


def get_nutrient_status(
    nutrient: str,
    value: float,
    extraction_method: ExtractionMethod = ExtractionMethod.OLSEN,
) -> tuple[NutrientStatus, str, str]:
    """
    Quick check of a single nutrient status.

    Args:
        nutrient: Nutrient code (N, P, K, etc.)
        value: Value in ppm
        extraction_method: Extraction method for P

    Returns:
        Tuple of (status, description_en, description_ar)
    """
    config = InterpretationConfig(p_extraction=extraction_method)
    interpreter = SoilTestInterpreter(config)
    result = interpreter.interpret_single_nutrient(nutrient, value)
    return result.status, result.status_description, result.status_description_ar


def get_ph_status(ph: float) -> tuple[str, str]:
    """
    Quick pH status check.

    Args:
        ph: Soil pH value

    Returns:
        Tuple of (status_en, status_ar)
    """
    interpreter = SoilTestInterpreter()
    return interpreter._interpret_ph(ph)


def get_ec_status(ec: float) -> tuple[str, str]:
    """
    Quick EC/salinity status check.

    Args:
        ec: Electrical conductivity in dS/m

    Returns:
        Tuple of (status_en, status_ar)
    """
    interpreter = SoilTestInterpreter()
    return interpreter._interpret_ec(ec)
