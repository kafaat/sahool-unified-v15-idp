"""
Economic Threshold Calculations - حسابات العتبة الاقتصادية
===========================================================

Economic and action threshold calculations for pest management decisions.
Includes threshold database for Middle East agricultural pests and
functions for threshold-based alert generation.

Implements Integrated Pest Management (IPM) decision support:
- Economic Injury Level (EIL) - مستوى الضرر الاقتصادي
- Economic Threshold (ET) - العتبة الاقتصادية
- Action Threshold (AT) - عتبة التدخل

Author: SAHOOL Platform Team
Version: 1.0.0
Updated: January 2026
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import (
    AlertPriority,
    CropType,
    EconomicThreshold,
    InfestationLevel,
    PestAlert,
    ScoutObservation,
    ScoutReport,
)

# =============================================================================
# THRESHOLD DATABASE - قاعدة بيانات العتبات
# =============================================================================

THRESHOLD_DATABASE: dict[str, EconomicThreshold] = {
    # -------------------------------------------------------------------------
    # RED PALM WEEVIL - سوسة النخيل الحمراء
    # -------------------------------------------------------------------------
    "THR_RPW001_PALM": EconomicThreshold(
        id="THR_RPW001_PALM",
        pest_id="RPW001",
        pest_name="Red Palm Weevil",
        pest_name_ar="سوسة النخيل الحمراء",
        crop_type=CropType.DATE_PALM,
        growth_stages=["all"],
        action_threshold=0.0,  # Zero tolerance - any detection requires action
        economic_threshold=0.0,
        threshold_unit="detection",
        threshold_description="Zero tolerance pest. Any detection (trap catch, acoustic detection, "
        "or visual symptoms) requires immediate action.",
        threshold_description_ar="آفة لا تحمل أي حد. أي اكتشاف (مصيدة، كشف صوتي، أو أعراض بصرية) يتطلب تدخلاً فورياً.",
        sampling_method="Pheromone traps (5-10/ha), acoustic detection devices, visual inspection",
        sampling_method_ar="مصائد فرمونية (5-10/هكتار)، أجهزة كشف صوتي، فحص بصري",
        sampling_frequency="Weekly trap checks, monthly acoustic surveys",
        sampling_frequency_ar="فحص المصائد أسبوعياً، مسح صوتي شهرياً",
        treatment_cost_per_ha=5000.0,  # SAR - includes injection + preventive treatments
        crop_value_per_ha=50000.0,  # SAR - mature palm grove
        expected_loss_per_pest_unit=15000.0,  # SAR per infested tree
        source="MEWA (Ministry of Environment, Water and Agriculture, Saudi Arabia)",
        source_ar="وزارة البيئة والمياه والزراعة، المملكة العربية السعودية",
        reference_year=2024,
        notes="Critical quarantine pest. Death of infested palm is almost certain without treatment.",
        notes_ar="آفة حجر زراعي حرجة. موت النخلة المصابة شبه مؤكد بدون علاج.",
    ),
    # -------------------------------------------------------------------------
    # DUBAS BUG - دوباس النخيل
    # -------------------------------------------------------------------------
    "THR_DUBAS001_PALM": EconomicThreshold(
        id="THR_DUBAS001_PALM",
        pest_id="DUBAS001",
        pest_name="Dubas Bug",
        pest_name_ar="دوباس النخيل",
        crop_type=CropType.DATE_PALM,
        growth_stages=["all"],
        action_threshold=5.0,  # 5 nymphs/adults per frond
        economic_threshold=10.0,
        threshold_unit="per_frond",
        threshold_description="Count nymphs and adults on 10 fronds per palm, 5-10 palms per block. "
        "Action at 5 per frond average, economic damage at 10+.",
        threshold_description_ar="عد الحوريات والحشرات الكاملة على 10 سعفات لكل نخلة، 5-10 نخلات لكل قطعة. "
        "التدخل عند متوسط 5 لكل سعفة، الضرر الاقتصادي عند 10+.",
        sampling_method="Visual count on randomly selected fronds",
        sampling_method_ar="عد بصري على سعفات مختارة عشوائياً",
        sampling_frequency="Twice per season (spring generation: March-April, fall: September-October)",
        sampling_frequency_ar="مرتين في الموسم (جيل الربيع: مارس-أبريل، الخريف: سبتمبر-أكتوبر)",
        temperature_modifier={"hot": 0.8, "optimal": 1.0, "cool": 1.2},
        treatment_cost_per_ha=800.0,
        crop_value_per_ha=45000.0,
        expected_loss_per_pest_unit=100.0,  # Per frond affected
        source="Date Palm Research Center, UAE",
        source_ar="مركز أبحاث النخيل، الإمارات",
        reference_year=2023,
        notes="Two generations per year. Spring generation often more damaging.",
        notes_ar="جيلان في السنة. جيل الربيع غالباً أكثر ضرراً.",
    ),
    # -------------------------------------------------------------------------
    # APHIDS ON VEGETABLES - المن على الخضروات
    # -------------------------------------------------------------------------
    "THR_APHID001_TOMATO": EconomicThreshold(
        id="THR_APHID001_TOMATO",
        pest_id="APHID001",
        pest_name="Cotton/Melon Aphid",
        pest_name_ar="من القطن/الخضروات",
        crop_type=CropType.TOMATO,
        growth_stages=["seedling", "vegetative", "flowering", "fruiting"],
        action_threshold=10.0,  # 10% plants infested
        economic_threshold=20.0,
        threshold_unit="percentage_plants",
        threshold_description="Sample 20-50 plants per plot. Action threshold at 10% plants with colonies. "
        "Consider virus transmission risk - lower threshold if virus present in area.",
        threshold_description_ar="عينة 20-50 نبات لكل قطعة. عتبة التدخل عند 10% نباتات بمستعمرات. "
        "راعِ خطر نقل الفيروسات - عتبة أقل إذا كان الفيروس موجوداً في المنطقة.",
        sampling_method="Visual inspection of growing tips and leaf undersides",
        sampling_method_ar="فحص بصري للقمم النامية والسطح السفلي للأوراق",
        sampling_frequency="Twice weekly during vegetative growth, weekly during fruiting",
        sampling_frequency_ar="مرتين أسبوعياً خلال النمو الخضري، أسبوعياً خلال الإثمار",
        growth_stage_modifier={
            "seedling": 0.5,
            "vegetative": 0.7,
            "flowering": 0.8,
            "fruiting": 1.0,
        },
        treatment_cost_per_ha=400.0,
        crop_value_per_ha=80000.0,
        expected_loss_per_pest_unit=400.0,  # Per 1% infestation
        source="Agricultural Extension, Saudi Arabia",
        source_ar="الإرشاد الزراعي، المملكة العربية السعودية",
        reference_year=2024,
        notes="Virus vector - reduce threshold by 50% if TYLCV or other viruses present.",
        notes_ar="ناقل فيروسات - خفض العتبة 50% إذا كان TYLCV أو فيروسات أخرى موجودة.",
    ),
    "THR_APHID001_CUCUMBER": EconomicThreshold(
        id="THR_APHID001_CUCUMBER",
        pest_id="APHID001",
        pest_name="Cotton/Melon Aphid",
        pest_name_ar="من القطن/الخضروات",
        crop_type=CropType.CUCUMBER,
        growth_stages=["seedling", "vegetative", "flowering", "fruiting"],
        action_threshold=5.0,  # 5% plants infested
        economic_threshold=15.0,
        threshold_unit="percentage_plants",
        threshold_description="Lower threshold than tomato due to high virus susceptibility. "
        "Sample 20 plants per greenhouse or 50 per open field plot.",
        threshold_description_ar="عتبة أقل من الطماطم بسبب قابلية عالية للفيروسات. "
        "عينة 20 نبات لكل بيت محمي أو 50 للحقل المكشوف.",
        sampling_method="Visual inspection focusing on young leaves",
        sampling_method_ar="فحص بصري مع التركيز على الأوراق الحديثة",
        sampling_frequency="Twice weekly, especially during vegetative growth",
        sampling_frequency_ar="مرتين أسبوعياً، خاصة خلال النمو الخضري",
        treatment_cost_per_ha=400.0,
        crop_value_per_ha=120000.0,
        expected_loss_per_pest_unit=600.0,
        source="Protected Agriculture Research Center",
        source_ar="مركز أبحاث الزراعة المحمية",
        reference_year=2024,
        notes="CMV transmission can cause severe losses in cucumber.",
        notes_ar="نقل فيروس CMV يمكن أن يسبب خسائر شديدة في الخيار.",
    ),
    # -------------------------------------------------------------------------
    # WHITEFLIES - الذبابة البيضاء
    # -------------------------------------------------------------------------
    "THR_WHITEFLY001_TOMATO": EconomicThreshold(
        id="THR_WHITEFLY001_TOMATO",
        pest_id="WHITEFLY001",
        pest_name="Silverleaf Whitefly",
        pest_name_ar="الذبابة البيضاء",
        crop_type=CropType.TOMATO,
        growth_stages=["seedling", "vegetative", "flowering", "fruiting"],
        action_threshold=3.0,  # 3 adults per leaf or 5 nymphs per leaf
        economic_threshold=10.0,
        threshold_unit="per_leaf",
        threshold_description="Count adults on upper surface and nymphs on lower surface of middle leaves. "
        "CRITICAL: If TYLCV present, threshold is 0.5 per leaf (vector control).",
        threshold_description_ar="عد الحشرات الكاملة على السطح العلوي والحوريات على السطح السفلي للأوراق الوسطى. "
        "حرج: إذا كان TYLCV موجوداً، العتبة 0.5 لكل ورقة (مكافحة الناقل).",
        sampling_method="Yellow sticky traps (1/100m2) + leaf samples (10 leaves per 10 plants)",
        sampling_method_ar="مصائد لاصقة صفراء (1/100م2) + عينات أوراق (10 أوراق من 10 نباتات)",
        sampling_frequency="Twice weekly, daily during high pressure periods",
        sampling_frequency_ar="مرتين أسبوعياً، يومياً خلال فترات الضغط العالي",
        temperature_modifier={"hot": 0.7, "optimal": 1.0, "cool": 1.5},
        growth_stage_modifier={
            "seedling": 0.3,
            "vegetative": 0.5,
            "flowering": 0.8,
            "fruiting": 1.0,
        },
        treatment_cost_per_ha=600.0,
        crop_value_per_ha=80000.0,
        expected_loss_per_pest_unit=800.0,
        source="ICARDA / National Research Centers",
        source_ar="إيكاردا / مراكز البحوث الوطنية",
        reference_year=2024,
        notes="TYLCV vector - extremely important in tomato. Use resistant varieties where possible.",
        notes_ar="ناقل TYLCV - مهم للغاية في الطماطم. استخدم أصناف مقاومة حيثما أمكن.",
    ),
    # -------------------------------------------------------------------------
    # SPIDER MITES - العنكبوت الأحمر
    # -------------------------------------------------------------------------
    "THR_MITE001_CUCUMBER": EconomicThreshold(
        id="THR_MITE001_CUCUMBER",
        pest_id="MITE001",
        pest_name="Two-spotted Spider Mite",
        pest_name_ar="العنكبوت الأحمر ذو البقعتين",
        crop_type=CropType.CUCUMBER,
        growth_stages=["vegetative", "flowering", "fruiting"],
        action_threshold=2.0,  # 2 mites per leaf
        economic_threshold=5.0,
        threshold_unit="per_leaf",
        threshold_description="Count motile stages on undersides of leaves using hand lens (10x). "
        "Sample lower, middle, and upper leaves. Hot spots often start at field edges.",
        threshold_description_ar="عد المراحل المتحركة على السطح السفلي للأوراق باستخدام عدسة يدوية (10×). "
        "عينات من الأوراق السفلى والوسطى والعليا. البؤر الساخنة غالباً تبدأ من حواف الحقل.",
        sampling_method="10x hand lens, 5 leaves per 10 plants, focus on leaf undersides",
        sampling_method_ar="عدسة يدوية 10×، 5 أوراق من 10 نباتات، ركز على السطح السفلي",
        sampling_frequency="Twice weekly in hot weather, weekly otherwise",
        sampling_frequency_ar="مرتين أسبوعياً في الطقس الحار، أسبوعياً خلاف ذلك",
        temperature_modifier={"hot": 0.5, "optimal": 0.8, "cool": 1.2},  # Lower in hot weather
        treatment_cost_per_ha=500.0,
        crop_value_per_ha=120000.0,
        expected_loss_per_pest_unit=2400.0,
        source="IPM Guidelines for Protected Vegetables",
        source_ar="إرشادات المكافحة المتكاملة للخضروات المحمية",
        reference_year=2024,
        notes="Populations explode in hot, dry conditions. Overhead irrigation can suppress.",
        notes_ar="الأعداد تنفجر في الظروف الحارة والجافة. الري العلوي يمكن أن يثبط.",
    ),
    # -------------------------------------------------------------------------
    # TUTA ABSOLUTA - حافرة أنفاق الطماطم
    # -------------------------------------------------------------------------
    "THR_TUTA001_TOMATO": EconomicThreshold(
        id="THR_TUTA001_TOMATO",
        pest_id="TUTA001",
        pest_name="Tomato Leafminer",
        pest_name_ar="حافرة أنفاق الطماطم",
        crop_type=CropType.TOMATO,
        growth_stages=["seedling", "vegetative", "flowering", "fruiting"],
        action_threshold=1.0,  # 1 moth per trap per week or 1% leaves mined
        economic_threshold=5.0,
        threshold_unit="per_trap_week",
        threshold_description="Pheromone traps: action at 1 moth/trap/week. Leaf mines: action at 1% leaves mined. "
        "Zero tolerance for fruit damage. Very destructive - act early.",
        threshold_description_ar="مصائد فرمونية: تدخل عند 1 عثة/مصيدة/أسبوع. أنفاق الأوراق: تدخل عند 1% أوراق منقبة. "
        "لا تحمل أي ضرر للثمار. مدمرة جداً - تصرف مبكراً.",
        sampling_method="Pheromone traps (2-4/ha) + visual inspection for leaf mines and fruit damage",
        sampling_method_ar="مصائد فرمونية (2-4/هكتار) + فحص بصري لأنفاق الأوراق وضرر الثمار",
        sampling_frequency="Traps checked twice weekly, visual inspection weekly",
        sampling_frequency_ar="فحص المصائد مرتين أسبوعياً، الفحص البصري أسبوعياً",
        growth_stage_modifier={
            "seedling": 0.5,
            "vegetative": 0.7,
            "flowering": 0.8,
            "fruiting": 0.5,
        },
        treatment_cost_per_ha=800.0,
        crop_value_per_ha=80000.0,
        expected_loss_per_pest_unit=1600.0,
        source="FAO Tuta absoluta Management Guidelines",
        source_ar="إرشادات الفاو لإدارة توتا أبسولوتا",
        reference_year=2024,
        notes="Quarantine pest in some regions. Can cause 100% loss if uncontrolled. IPM essential.",
        notes_ar="آفة حجر زراعي في بعض المناطق. يمكن أن تسبب خسارة 100% بدون مكافحة. المكافحة المتكاملة ضرورية.",
    ),
    # -------------------------------------------------------------------------
    # DATE MOTH - فراشة التمر
    # -------------------------------------------------------------------------
    "THR_DMOTH001_PALM": EconomicThreshold(
        id="THR_DMOTH001_PALM",
        pest_id="DMOTH001",
        pest_name="Date Moth",
        pest_name_ar="فراشة التمر",
        crop_type=CropType.DATE_PALM,
        growth_stages=["kimri", "khalal", "rutab", "tamr"],
        action_threshold=2.0,  # 2% fruit infestation
        economic_threshold=5.0,
        threshold_unit="percentage_fruit",
        threshold_description="Sample 100 fruits from 10 bunches per palm, 5 palms per block. "
        "Action at 2% infestation. Higher threshold acceptable for processing dates.",
        threshold_description_ar="عينة 100 ثمرة من 10 عذوق لكل نخلة، 5 نخلات لكل قطعة. "
        "التدخل عند 2% إصابة. عتبة أعلى مقبولة لتمور التصنيع.",
        sampling_method="Visual inspection of fruit, pheromone traps (3-5/ha)",
        sampling_method_ar="فحص بصري للثمار، مصائد فرمونية (3-5/هكتار)",
        sampling_frequency="Weekly during fruit development (June-October)",
        sampling_frequency_ar="أسبوعياً خلال تطور الثمار (يونيو-أكتوبر)",
        growth_stage_modifier={"kimri": 0.5, "khalal": 0.8, "rutab": 1.0, "tamr": 1.2},
        treatment_cost_per_ha=600.0,
        crop_value_per_ha=60000.0,
        expected_loss_per_pest_unit=600.0,
        source="Date Palm Research Institute",
        source_ar="معهد أبحاث النخيل",
        reference_year=2023,
        notes="Sanitation crucial - remove fallen and infested fruits.",
        notes_ar="الصرف الصحي ضروري - أزل الثمار الساقطة والمصابة.",
    ),
    # -------------------------------------------------------------------------
    # THRIPS - التربس
    # -------------------------------------------------------------------------
    "THR_THRIPS001_PEPPER": EconomicThreshold(
        id="THR_THRIPS001_PEPPER",
        pest_id="THRIPS001",
        pest_name="Western Flower Thrips",
        pest_name_ar="تربس الأزهار الغربي",
        crop_type=CropType.PEPPER,
        growth_stages=["vegetative", "flowering", "fruiting"],
        action_threshold=5.0,  # 5 thrips per flower
        economic_threshold=10.0,
        threshold_unit="per_flower",
        threshold_description="Tap flowers over white paper and count. Sample 10 flowers per 10 plants. "
        "CRITICAL: If TSWV present in area, threshold is 1 per flower.",
        threshold_description_ar="اضرب الأزهار فوق ورق أبيض وعد. عينة 10 أزهار من 10 نباتات. "
        "حرج: إذا كان TSWV موجوداً في المنطقة، العتبة 1 لكل زهرة.",
        sampling_method="Flower tapping onto white paper, blue sticky traps (1/100m2)",
        sampling_method_ar="ضرب الأزهار على ورق أبيض، مصائد لاصقة زرقاء (1/100م2)",
        sampling_frequency="Twice weekly during flowering",
        sampling_frequency_ar="مرتين أسبوعياً خلال الإزهار",
        treatment_cost_per_ha=500.0,
        crop_value_per_ha=100000.0,
        expected_loss_per_pest_unit=500.0,
        source="Vegetable IPM Guidelines",
        source_ar="إرشادات المكافحة المتكاملة للخضروات",
        reference_year=2024,
        notes="TSWV vector. Cryptic behavior makes control difficult. Multiple tactics needed.",
        notes_ar="ناقل TSWV. السلوك الخفي يجعل المكافحة صعبة. تكتيكات متعددة ضرورية.",
    ),
    # -------------------------------------------------------------------------
    # FRUIT FLY - ذباب الفاكهة
    # -------------------------------------------------------------------------
    "THR_FRUITFLY001_CITRUS": EconomicThreshold(
        id="THR_FRUITFLY001_CITRUS",
        pest_id="FRUITFLY001",
        pest_name="Mediterranean Fruit Fly",
        pest_name_ar="ذبابة فاكهة البحر المتوسط",
        crop_type=CropType.CITRUS,
        growth_stages=["fruit_development", "ripening"],
        action_threshold=0.5,  # 0.5 flies per trap per day (FTD)
        economic_threshold=1.0,
        threshold_unit="FTD",  # Flies per Trap per Day
        threshold_description="McPhail traps with protein bait at 1-2 traps/ha. FTD = total flies / (traps x days). "
        "Export orchards may require 0 FTD tolerance.",
        threshold_description_ar="مصائد ماكفيل بطعم بروتيني بمعدل 1-2 مصيدة/هكتار. FTD = إجمالي الذباب / (المصائد × الأيام). "
        "بساتين التصدير قد تتطلب تحمل صفر.",
        sampling_method="McPhail traps with protein bait, inspected twice weekly",
        sampling_method_ar="مصائد ماكفيل بطعم بروتيني، تُفحص مرتين أسبوعياً",
        sampling_frequency="Twice weekly during fruiting season",
        sampling_frequency_ar="مرتين أسبوعياً خلال موسم الإثمار",
        treatment_cost_per_ha=700.0,
        crop_value_per_ha=50000.0,
        expected_loss_per_pest_unit=5000.0,
        source="Quarantine and Plant Protection Guidelines",
        source_ar="إرشادات الحجر الزراعي وحماية النبات",
        reference_year=2024,
        notes="Quarantine pest. Essential for export markets. Area-wide management recommended.",
        notes_ar="آفة حجر زراعي. ضرورية لأسواق التصدير. الإدارة على مستوى المنطقة موصى بها.",
    ),
}


# =============================================================================
# THRESHOLD LOOKUP FUNCTIONS - دوال البحث عن العتبات
# =============================================================================


def get_threshold(pest_id: str, crop_type: CropType) -> EconomicThreshold | None:
    """
    Get threshold for a specific pest-crop combination.
    الحصول على عتبة لمجموعة آفة-محصول محددة.
    """
    key = f"THR_{pest_id}_{crop_type.value.upper()}"
    if key in THRESHOLD_DATABASE:
        return THRESHOLD_DATABASE[key]

    # Try alternative keys (PALM vs DATE_PALM, etc.)
    for threshold in THRESHOLD_DATABASE.values():
        if threshold.pest_id == pest_id and threshold.crop_type == crop_type:
            return threshold

    return None


def get_thresholds_for_crop(crop_type: CropType) -> list[EconomicThreshold]:
    """
    Get all thresholds applicable to a crop.
    الحصول على جميع العتبات المطبقة على محصول.
    """
    return [t for t in THRESHOLD_DATABASE.values() if t.crop_type == crop_type]


def get_thresholds_for_pest(pest_id: str) -> list[EconomicThreshold]:
    """
    Get all thresholds for a pest across crops.
    الحصول على جميع العتبات لآفة عبر المحاصيل.
    """
    return [t for t in THRESHOLD_DATABASE.values() if t.pest_id == pest_id]


# =============================================================================
# THRESHOLD CALCULATION FUNCTIONS - دوال حساب العتبات
# =============================================================================


@dataclass
class ThresholdAssessment:
    """
    Result of threshold assessment.
    نتيجة تقييم العتبة.
    """

    pest_id: str
    pest_name: str
    pest_name_ar: str
    crop_type: CropType

    # Current observation
    observed_value: float
    unit: str

    # Thresholds
    action_threshold: float
    economic_threshold: float
    adjusted_action_threshold: float  # After modifiers
    adjusted_economic_threshold: float

    # Assessment
    exceeds_action_threshold: bool
    exceeds_economic_threshold: bool
    percentage_of_action_threshold: float
    percentage_of_economic_threshold: float

    # Risk level
    infestation_level: InfestationLevel
    alert_priority: AlertPriority

    # Economic analysis
    estimated_loss_if_no_action: float
    treatment_cost: float
    benefit_cost_ratio: float

    # Modifiers applied
    modifiers_applied: dict[str, float] = field(default_factory=dict)

    # Recommendations
    action_required: bool = False
    recommendation: str = ""
    recommendation_ar: str = ""
    urgency: str = ""
    urgency_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "pest_id": self.pest_id,
            "pest_name": self.pest_name,
            "pest_name_ar": self.pest_name_ar,
            "crop_type": self.crop_type.value,
            "observed_value": self.observed_value,
            "unit": self.unit,
            "action_threshold": self.action_threshold,
            "economic_threshold": self.economic_threshold,
            "adjusted_action_threshold": self.adjusted_action_threshold,
            "adjusted_economic_threshold": self.adjusted_economic_threshold,
            "exceeds_action_threshold": self.exceeds_action_threshold,
            "exceeds_economic_threshold": self.exceeds_economic_threshold,
            "percentage_of_action_threshold": self.percentage_of_action_threshold,
            "percentage_of_economic_threshold": self.percentage_of_economic_threshold,
            "infestation_level": self.infestation_level.value,
            "alert_priority": self.alert_priority.value,
            "estimated_loss_if_no_action": self.estimated_loss_if_no_action,
            "treatment_cost": self.treatment_cost,
            "benefit_cost_ratio": self.benefit_cost_ratio,
            "modifiers_applied": self.modifiers_applied,
            "action_required": self.action_required,
            "recommendation": self.recommendation,
            "recommendation_ar": self.recommendation_ar,
            "urgency": self.urgency,
            "urgency_ar": self.urgency_ar,
        }


def assess_threshold(
    pest_id: str,
    crop_type: CropType,
    observed_value: float,
    growth_stage: str | None = None,
    temperature_c: float | None = None,
    virus_present: bool = False,
    area_ha: float = 1.0,
) -> ThresholdAssessment | None:
    """
    Assess observed pest levels against economic thresholds.

    تقييم مستويات الآفة الملاحظة مقابل العتبات الاقتصادية.

    Args:
        pest_id: Pest identifier
        crop_type: Crop type
        observed_value: Observed count/percentage
        growth_stage: Current crop growth stage
        temperature_c: Current temperature for modifiers
        virus_present: Whether vectored viruses are present in area
        area_ha: Field area in hectares

    Returns:
        ThresholdAssessment with analysis and recommendations
    """
    threshold = get_threshold(pest_id, crop_type)
    if not threshold:
        return None

    # Start with base thresholds
    adj_action = threshold.action_threshold
    adj_economic = threshold.economic_threshold
    modifiers_applied: dict[str, float] = {}

    # Apply growth stage modifier
    if growth_stage and threshold.growth_stage_modifier:
        if growth_stage.lower() in threshold.growth_stage_modifier:
            modifier = threshold.growth_stage_modifier[growth_stage.lower()]
            adj_action *= modifier
            adj_economic *= modifier
            modifiers_applied["growth_stage"] = modifier

    # Apply temperature modifier
    if temperature_c is not None and threshold.temperature_modifier:
        if temperature_c > 35:
            temp_key = "hot"
        elif temperature_c < 20:
            temp_key = "cool"
        else:
            temp_key = "optimal"
        if temp_key in threshold.temperature_modifier:
            modifier = threshold.temperature_modifier[temp_key]
            adj_action *= modifier
            adj_economic *= modifier
            modifiers_applied["temperature"] = modifier

    # Reduce threshold if virus present (for vector pests)
    if virus_present:
        adj_action *= 0.5
        adj_economic *= 0.5
        modifiers_applied["virus_present"] = 0.5

    # Calculate percentages
    pct_action = (observed_value / adj_action * 100) if adj_action > 0 else float("inf")
    pct_economic = (observed_value / adj_economic * 100) if adj_economic > 0 else float("inf")

    # Determine if thresholds exceeded
    exceeds_action = observed_value >= adj_action
    exceeds_economic = observed_value >= adj_economic

    # Determine infestation level
    if observed_value == 0:
        level = InfestationLevel.NONE
    elif pct_action < 25:
        level = InfestationLevel.TRACE
    elif pct_action < 50:
        level = InfestationLevel.LOW
    elif pct_action < 100:
        level = InfestationLevel.MODERATE
    elif pct_economic < 100:
        level = InfestationLevel.HIGH
    elif pct_economic < 200:
        level = InfestationLevel.SEVERE
    else:
        level = InfestationLevel.CRITICAL

    # Determine alert priority
    if level == InfestationLevel.CRITICAL:
        priority = AlertPriority.CRITICAL
    elif level == InfestationLevel.SEVERE:
        priority = AlertPriority.HIGH
    elif exceeds_action:
        priority = AlertPriority.MEDIUM
    elif pct_action >= 50:
        priority = AlertPriority.LOW
    else:
        priority = AlertPriority.INFORMATIONAL

    # Economic analysis
    loss_per_unit = threshold.expected_loss_per_pest_unit
    estimated_loss = observed_value * loss_per_unit * area_ha
    treatment_cost = threshold.treatment_cost_per_ha * area_ha
    bcr = estimated_loss / treatment_cost if treatment_cost > 0 else 0

    # Determine action and urgency
    action_required = exceeds_action
    if exceeds_economic:
        recommendation = "Immediate treatment required. Economic damage threshold exceeded."
        recommendation_ar = "مطلوب علاج فوري. تم تجاوز عتبة الضرر الاقتصادي."
        urgency = "Immediate (24-48 hours)"
        urgency_ar = "فوري (24-48 ساعة)"
    elif exceeds_action:
        recommendation = "Treatment recommended. Action threshold exceeded."
        recommendation_ar = "يُوصى بالعلاج. تم تجاوز عتبة التدخل."
        urgency = "Soon (within 1 week)"
        urgency_ar = "قريباً (خلال أسبوع)"
    elif pct_action >= 75:
        recommendation = "Monitor closely. Approaching action threshold."
        recommendation_ar = "راقب عن كثب. يقترب من عتبة التدخل."
        urgency = "Scheduled monitoring"
        urgency_ar = "مراقبة مجدولة"
    elif pct_action >= 50:
        recommendation = "Continue monitoring. Pest pressure building."
        recommendation_ar = "استمر في المراقبة. ضغط الآفة يتزايد."
        urgency = "Routine monitoring"
        urgency_ar = "مراقبة روتينية"
    else:
        recommendation = "No action needed. Below threshold."
        recommendation_ar = "لا إجراء مطلوب. تحت العتبة."
        urgency = "None"
        urgency_ar = "لا يوجد"

    return ThresholdAssessment(
        pest_id=pest_id,
        pest_name=threshold.pest_name,
        pest_name_ar=threshold.pest_name_ar,
        crop_type=crop_type,
        observed_value=observed_value,
        unit=threshold.threshold_unit,
        action_threshold=threshold.action_threshold,
        economic_threshold=threshold.economic_threshold,
        adjusted_action_threshold=adj_action,
        adjusted_economic_threshold=adj_economic,
        exceeds_action_threshold=exceeds_action,
        exceeds_economic_threshold=exceeds_economic,
        percentage_of_action_threshold=min(pct_action, 999.9),
        percentage_of_economic_threshold=min(pct_economic, 999.9),
        infestation_level=level,
        alert_priority=priority,
        estimated_loss_if_no_action=estimated_loss,
        treatment_cost=treatment_cost,
        benefit_cost_ratio=bcr,
        modifiers_applied=modifiers_applied,
        action_required=action_required,
        recommendation=recommendation,
        recommendation_ar=recommendation_ar,
        urgency=urgency,
        urgency_ar=urgency_ar,
    )


def assess_scout_report(
    report: ScoutReport,
    virus_present: bool = False,
) -> list[ThresholdAssessment]:
    """
    Assess all observations in a scout report against thresholds.

    تقييم جميع الملاحظات في تقرير المسح مقابل العتبات.
    """
    assessments: list[ThresholdAssessment] = []

    # Group observations by pest
    pest_observations: dict[str, list[ScoutObservation]] = {}
    for obs in report.observations:
        pest_key = obs.pest_id or obs.pest_name
        if pest_key not in pest_observations:
            pest_observations[pest_key] = []
        pest_observations[pest_key].append(obs)

    # Assess each pest
    for pest_key, observations in pest_observations.items():
        # Calculate average count per unit
        counts = [obs.count_per_unit for obs in observations if obs.count_per_unit is not None]
        if not counts:
            counts = [float(obs.count or 0) for obs in observations]

        if counts:
            avg_count = sum(counts) / len(counts)

            assessment = assess_threshold(
                pest_id=pest_key,
                crop_type=report.crop_type,
                observed_value=avg_count,
                growth_stage=report.growth_stage,
                temperature_c=report.temperature_c,
                virus_present=virus_present,
                area_ha=report.field_area_ha or 1.0,
            )

            if assessment:
                assessments.append(assessment)

    return assessments


def generate_threshold_alert(
    assessment: ThresholdAssessment,
    field_id: str,
    farm_id: str = "",
    tenant_id: str = "",
    field_name: str = "",
    field_name_ar: str = "",
) -> PestAlert:
    """
    Generate a pest alert from a threshold assessment.

    إنشاء تنبيه آفة من تقييم العتبة.
    """
    # Determine alert type
    if assessment.exceeds_economic_threshold:
        alert_type = "economic_threshold_exceeded"
    elif assessment.exceeds_action_threshold:
        alert_type = "action_threshold_exceeded"
    else:
        alert_type = "threshold_approaching"

    # Build description
    desc_en = (
        f"Observed: {assessment.observed_value:.1f} {assessment.unit}. "
        f"Action threshold: {assessment.adjusted_action_threshold:.1f}, "
        f"Economic threshold: {assessment.adjusted_economic_threshold:.1f}. "
        f"{assessment.recommendation}"
    )

    desc_ar = (
        f"الملاحظ: {assessment.observed_value:.1f} {assessment.unit}. "
        f"عتبة التدخل: {assessment.adjusted_action_threshold:.1f}، "
        f"العتبة الاقتصادية: {assessment.adjusted_economic_threshold:.1f}. "
        f"{assessment.recommendation_ar}"
    )

    # Build impact statement
    impact_en = (
        f"Estimated loss without action: {assessment.estimated_loss_if_no_action:.0f} SAR. "
        f"Treatment cost: {assessment.treatment_cost:.0f} SAR. "
        f"Benefit-cost ratio: {assessment.benefit_cost_ratio:.1f}:1"
    )

    impact_ar = (
        f"الخسارة المقدرة بدون إجراء: {assessment.estimated_loss_if_no_action:.0f} ريال. "
        f"تكلفة العلاج: {assessment.treatment_cost:.0f} ريال. "
        f"نسبة الفائدة للتكلفة: {assessment.benefit_cost_ratio:.1f}:1"
    )

    # Recommended actions
    actions_en: list[str] = []
    actions_ar: list[str] = []

    if assessment.exceeds_action_threshold:
        actions_en.append("Initiate treatment according to IPM guidelines")
        actions_ar.append("ابدأ العلاج وفقاً لإرشادات المكافحة المتكاملة")
        actions_en.append("Consider environmental conditions for spray timing")
        actions_ar.append("راعِ الظروف البيئية لتوقيت الرش")

    actions_en.append("Schedule follow-up scouting in 5-7 days")
    actions_ar.append("جدول مسحاً للمتابعة خلال 5-7 أيام")

    if assessment.benefit_cost_ratio < 1.5:
        actions_en.append("Consider non-chemical control options due to marginal economics")
        actions_ar.append("فكر في خيارات مكافحة غير كيميائية بسبب الجدوى الاقتصادية الهامشية")

    return PestAlert(
        alert_type=alert_type,
        priority=assessment.alert_priority,
        tenant_id=tenant_id,
        farm_id=farm_id,
        field_id=field_id,
        field_name=field_name,
        field_name_ar=field_name_ar,
        pest_id=assessment.pest_id,
        pest_name=assessment.pest_name,
        pest_name_ar=assessment.pest_name_ar,
        title=f"{assessment.pest_name} - {alert_type.replace('_', ' ').title()}",
        title_ar=f"{assessment.pest_name_ar} - {'تجاوز العتبة' if assessment.exceeds_action_threshold else 'اقتراب من العتبة'}",
        description=desc_en,
        description_ar=desc_ar,
        impact=impact_en,
        impact_ar=impact_ar,
        recommended_actions=actions_en,
        recommended_actions_ar=actions_ar,
        current_value=assessment.observed_value,
        threshold_value=assessment.adjusted_action_threshold,
        threshold_unit=assessment.unit,
        potential_loss_min=assessment.estimated_loss_if_no_action * 0.5,
        potential_loss_max=assessment.estimated_loss_if_no_action * 1.5,
        crop_type=assessment.crop_type,
        is_active=assessment.action_required,
    )


# =============================================================================
# ECONOMIC CALCULATIONS - الحسابات الاقتصادية
# =============================================================================


def calculate_economic_injury_level(
    control_cost_per_ha: float,
    crop_value_per_ha: float,
    damage_per_pest_unit: float,
    control_efficacy: float = 0.85,
) -> float:
    """
    Calculate the Economic Injury Level (EIL).

    حساب مستوى الضرر الاقتصادي (EIL).

    EIL = C / (V * D * K)

    Where:
        C = Control cost per hectare
        V = Market value of crop per unit
        D = Damage per pest unit
        K = Control efficacy (0-1)

    Returns:
        EIL in pest units per ha
    """
    if crop_value_per_ha <= 0 or damage_per_pest_unit <= 0 or control_efficacy <= 0:
        return 0.0

    eil = control_cost_per_ha / (crop_value_per_ha * damage_per_pest_unit * control_efficacy)
    return eil


def calculate_gain_threshold(
    eil: float,
    pest_growth_rate: float = 1.5,
    days_to_treatment: int = 3,
) -> float:
    """
    Calculate the action threshold (gain threshold) based on EIL.

    حساب عتبة التدخل (عتبة الربح) بناءً على EIL.

    Accounts for pest population growth between detection and treatment.

    Args:
        eil: Economic Injury Level
        pest_growth_rate: Population growth multiplier per day
        days_to_treatment: Expected days from detection to treatment

    Returns:
        Action threshold (lower than EIL to account for growth)
    """
    if days_to_treatment <= 0:
        return eil

    # Work backwards from EIL
    growth_factor = pest_growth_rate**days_to_treatment
    action_threshold = eil / growth_factor
    return action_threshold


def estimate_yield_loss(
    infestation_level: float,
    threshold: EconomicThreshold,
    area_ha: float,
) -> dict[str, float]:
    """
    Estimate potential yield loss based on infestation level.

    تقدير خسارة الغلة المحتملة بناءً على مستوى الإصابة.

    Returns dict with low, expected, and high estimates.
    """
    if infestation_level <= 0:
        return {"low": 0.0, "expected": 0.0, "high": 0.0, "currency": threshold.currency}

    base_loss = infestation_level * threshold.expected_loss_per_pest_unit * area_ha

    return {
        "low": base_loss * 0.6,
        "expected": base_loss,
        "high": base_loss * 1.5,
        "currency": threshold.currency,
    }


def calculate_treatment_roi(
    assessment: ThresholdAssessment,
) -> dict[str, Any]:
    """
    Calculate ROI for treatment based on threshold assessment.

    حساب العائد على الاستثمار للعلاج بناءً على تقييم العتبة.
    """
    if assessment.treatment_cost <= 0:
        return {"roi": 0.0, "recommendation": "No treatment cost data available"}

    net_benefit = assessment.estimated_loss_if_no_action - assessment.treatment_cost
    roi = (net_benefit / assessment.treatment_cost) * 100

    if roi > 200:
        rec = "Highly recommended - strong economic justification"
        rec_ar = "موصى به بشدة - تبرير اقتصادي قوي"
    elif roi > 100:
        rec = "Recommended - good return on investment"
        rec_ar = "موصى به - عائد جيد على الاستثمار"
    elif roi > 50:
        rec = "Consider treatment - moderate return"
        rec_ar = "فكر في العلاج - عائد متوسط"
    elif roi > 0:
        rec = "Marginal benefit - consider non-chemical options"
        rec_ar = "فائدة هامشية - فكر في خيارات غير كيميائية"
    else:
        rec = "Not economically justified - monitor only"
        rec_ar = "غير مبرر اقتصادياً - مراقبة فقط"

    return {
        "gross_benefit": assessment.estimated_loss_if_no_action,
        "treatment_cost": assessment.treatment_cost,
        "net_benefit": net_benefit,
        "roi_percentage": roi,
        "benefit_cost_ratio": assessment.benefit_cost_ratio,
        "recommendation": rec,
        "recommendation_ar": rec_ar,
        "currency": "SAR",
    }
