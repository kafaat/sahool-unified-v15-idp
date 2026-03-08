"""
Treatment Recommendations - توصيات العلاج
==========================================

Treatment recommendations engine for pest management in Middle East agriculture.
Provides chemical, biological, and cultural control options with bilingual support.

Integrates with:
- Pest identification database
- Economic threshold system
- Pesticide compliance module

Author: SAHOOL Platform Team
Version: 1.0.0
Updated: January 2026
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from .models import (
    AlertPriority,
    CropType,
    InfestationLevel,
    PestAlert,
    PestLifeStage,
    ScoutReport,
    TreatmentRecommendation,
    TreatmentType,
    TreatmentUrgency,
)
from .thresholds import ThresholdAssessment

# =============================================================================
# TREATMENT OPTIONS DATABASE - قاعدة بيانات خيارات العلاج
# =============================================================================


@dataclass
class ChemicalOption:
    """Chemical treatment option."""

    product_name: str
    product_name_ar: str
    active_ingredient: str
    active_ingredient_ar: str
    formulation: str  # EC, WP, SC, etc.
    rate_per_ha: str
    rate_unit: str
    phi_days: int  # Pre-harvest interval
    rei_hours: int  # Re-entry interval
    target_stages: list[PestLifeStage]
    mode_of_action: str
    mode_of_action_ar: str
    efficacy: str  # excellent, good, moderate, variable
    resistance_risk: str  # high, moderate, low
    notes: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "product_name": self.product_name,
            "product_name_ar": self.product_name_ar,
            "active_ingredient": self.active_ingredient,
            "active_ingredient_ar": self.active_ingredient_ar,
            "formulation": self.formulation,
            "rate_per_ha": self.rate_per_ha,
            "rate_unit": self.rate_unit,
            "phi_days": self.phi_days,
            "rei_hours": self.rei_hours,
            "target_stages": [s.value for s in self.target_stages],
            "mode_of_action": self.mode_of_action,
            "mode_of_action_ar": self.mode_of_action_ar,
            "efficacy": self.efficacy,
            "resistance_risk": self.resistance_risk,
            "notes": self.notes,
            "notes_ar": self.notes_ar,
        }


@dataclass
class BiologicalOption:
    """Biological control option."""

    agent_name: str
    agent_name_ar: str
    agent_type: str  # predator, parasitoid, pathogen, biopesticide
    target_pest_stages: list[PestLifeStage]
    application_rate: str
    application_method: str
    application_method_ar: str
    optimal_conditions: str
    optimal_conditions_ar: str
    efficacy: str
    notes: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "agent_name_ar": self.agent_name_ar,
            "agent_type": self.agent_type,
            "target_pest_stages": [s.value for s in self.target_pest_stages],
            "application_rate": self.application_rate,
            "application_method": self.application_method,
            "application_method_ar": self.application_method_ar,
            "optimal_conditions": self.optimal_conditions,
            "optimal_conditions_ar": self.optimal_conditions_ar,
            "efficacy": self.efficacy,
            "notes": self.notes,
            "notes_ar": self.notes_ar,
        }


@dataclass
class CulturalPractice:
    """Cultural control practice."""

    practice: str
    practice_ar: str
    timing: str
    timing_ar: str
    effectiveness: str  # high, moderate, supplementary
    cost: str  # low, moderate, high
    notes: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "practice": self.practice,
            "practice_ar": self.practice_ar,
            "timing": self.timing,
            "timing_ar": self.timing_ar,
            "effectiveness": self.effectiveness,
            "cost": self.cost,
            "notes": self.notes,
            "notes_ar": self.notes_ar,
        }


# =============================================================================
# TREATMENT PROTOCOLS - بروتوكولات العلاج
# =============================================================================

TREATMENT_PROTOCOLS: dict[str, dict[str, Any]] = {
    # -------------------------------------------------------------------------
    # RED PALM WEEVIL - سوسة النخيل الحمراء
    # -------------------------------------------------------------------------
    "RPW001": {
        "pest_name": "Red Palm Weevil",
        "pest_name_ar": "سوسة النخيل الحمراء",
        "urgency": TreatmentUrgency.IMMEDIATE,
        "primary_strategy": "Integrated management combining chemical injection, trapping, and sanitation",
        "primary_strategy_ar": "إدارة متكاملة تجمع بين الحقن الكيميائي والمصائد والصرف الصحي",
        "chemical_options": [
            ChemicalOption(
                product_name="Emamectin benzoate 5% SG",
                product_name_ar="إمامكتين بنزوات 5% محبب قابل للذوبان",
                active_ingredient="Emamectin benzoate",
                active_ingredient_ar="إمامكتين بنزوات",
                formulation="SG",
                rate_per_ha="50-100 ml per injection point, 4-6 points per tree",
                rate_unit="ml/point",
                phi_days=14,
                rei_hours=24,
                target_stages=[PestLifeStage.LARVA, PestLifeStage.ADULT],
                mode_of_action="Chloride channel activator",
                mode_of_action_ar="منشط قناة الكلوريد",
                efficacy="excellent",
                resistance_risk="low",
                notes="Inject into trunk at 45 degree angle, 15-20cm depth",
                notes_ar="حقن في الجذع بزاوية 45 درجة، عمق 15-20 سم",
            ),
            ChemicalOption(
                product_name="Imidacloprid 35% SC",
                product_name_ar="إميداكلوبريد 35% معلق مركز",
                active_ingredient="Imidacloprid",
                active_ingredient_ar="إميداكلوبريد",
                formulation="SC",
                rate_per_ha="2-4 ml per liter, soil drench",
                rate_unit="ml/L",
                phi_days=21,
                rei_hours=48,
                target_stages=[PestLifeStage.LARVA, PestLifeStage.ADULT],
                mode_of_action="Neonicotinoid - nicotinic acetylcholine receptor agonist",
                mode_of_action_ar="نيونيكوتينويد - محفز مستقبل أسيتيل كولين النيكوتيني",
                efficacy="good",
                resistance_risk="moderate",
                notes="Apply as soil drench for preventive treatment, 20-40 L per tree",
                notes_ar="يُطبق كغمر تربة للعلاج الوقائي، 20-40 لتر لكل شجرة",
            ),
        ],
        "biological_options": [
            BiologicalOption(
                agent_name="Metarhizium anisopliae",
                agent_name_ar="فطر الميتاريزيوم",
                agent_type="entomopathogenic_fungus",
                target_pest_stages=[PestLifeStage.LARVA, PestLifeStage.ADULT],
                application_rate="10^8 spores/ml, 500ml per tree",
                application_method="Injection or spray into wounds",
                application_method_ar="حقن أو رش في الجروح",
                optimal_conditions="High humidity >60%, temperature 25-30C",
                optimal_conditions_ar="رطوبة عالية >60%، درجة حرارة 25-30 مئوية",
                efficacy="moderate",
                notes="Best used in combination with chemical treatment",
                notes_ar="أفضل استخدام بالتزامن مع العلاج الكيميائي",
            ),
            BiologicalOption(
                agent_name="Beauveria bassiana",
                agent_name_ar="فطر البوفيريا",
                agent_type="entomopathogenic_fungus",
                target_pest_stages=[PestLifeStage.LARVA, PestLifeStage.ADULT],
                application_rate="10^9 spores/ml",
                application_method="Spray on trunk and offshoots",
                application_method_ar="رش على الجذع والفسائل",
                optimal_conditions="High humidity, moderate temperature",
                optimal_conditions_ar="رطوبة عالية، درجة حرارة معتدلة",
                efficacy="moderate",
                notes="Preventive application during high-risk periods",
                notes_ar="تطبيق وقائي خلال فترات الخطر العالي",
            ),
        ],
        "cultural_practices": [
            CulturalPractice(
                practice="Pheromone trap deployment",
                practice_ar="نشر المصائد الفرمونية",
                timing="Year-round, 5-10 traps per hectare",
                timing_ar="على مدار السنة، 5-10 مصائد لكل هكتار",
                effectiveness="high",
                cost="moderate",
                notes="Essential for early detection. Replace lures every 3 months.",
                notes_ar="ضروري للكشف المبكر. استبدل الطعم كل 3 أشهر.",
            ),
            CulturalPractice(
                practice="Removal and destruction of infested palms",
                practice_ar="إزالة وتدمير النخيل المصاب",
                timing="Immediately upon confirmed infestation with >30% damage",
                timing_ar="فوراً عند تأكيد الإصابة بضرر >30%",
                effectiveness="high",
                cost="high",
                notes="Burn or chip infested material. Do not transport infested palms.",
                notes_ar="حرق أو تفتيت المواد المصابة. لا تنقل النخيل المصاب.",
            ),
            CulturalPractice(
                practice="Wound treatment and sealing",
                practice_ar="معالجة الجروح وإغلاقها",
                timing="After pruning or any mechanical damage",
                timing_ar="بعد التقليم أو أي ضرر ميكانيكي",
                effectiveness="high",
                cost="low",
                notes="Apply insecticide + fungicide paste to all wounds",
                notes_ar="ضع معجون مبيد حشري + فطري على جميع الجروح",
            ),
            CulturalPractice(
                practice="Avoid pruning during peak adult activity",
                practice_ar="تجنب التقليم خلال ذروة نشاط الحشرات الكاملة",
                timing="Avoid March-May and September-November",
                timing_ar="تجنب مارس-مايو وسبتمبر-نوفمبر",
                effectiveness="moderate",
                cost="low",
            ),
        ],
        "precautions": [
            "Quarantine pest - report detections to agricultural authorities",
            "Wear full PPE during trunk injection",
            "Do not transport infested plant material",
            "Treat all palms within 500m radius of detection",
        ],
        "precautions_ar": [
            "آفة حجر زراعي - أبلغ عن الاكتشافات للسلطات الزراعية",
            "ارتدِ معدات الحماية الكاملة أثناء حقن الجذع",
            "لا تنقل المواد النباتية المصابة",
            "عالج جميع النخيل ضمن دائرة 500 متر من الاكتشاف",
        ],
    },
    # -------------------------------------------------------------------------
    # DUBAS BUG - دوباس النخيل
    # -------------------------------------------------------------------------
    "DUBAS001": {
        "pest_name": "Dubas Bug",
        "pest_name_ar": "دوباس النخيل",
        "urgency": TreatmentUrgency.SOON,
        "primary_strategy": "Timed sprays targeting nymphal stages in spring and fall",
        "primary_strategy_ar": "رشات موقوتة تستهدف مراحل الحوريات في الربيع والخريف",
        "chemical_options": [
            ChemicalOption(
                product_name="Dimethoate 40% EC",
                product_name_ar="دايميثويت 40% مركز قابل للاستحلاب",
                active_ingredient="Dimethoate",
                active_ingredient_ar="دايميثويت",
                formulation="EC",
                rate_per_ha="1.5-2 L/ha",
                rate_unit="L/ha",
                phi_days=28,
                rei_hours=48,
                target_stages=[PestLifeStage.NYMPH, PestLifeStage.ADULT],
                mode_of_action="Organophosphate - acetylcholinesterase inhibitor",
                mode_of_action_ar="فوسفات عضوي - مثبط أسيتيل كولين استراز",
                efficacy="good",
                resistance_risk="moderate",
                notes="Apply when majority of population is in nymphal stage",
                notes_ar="طبق عندما تكون غالبية الأعداد في مرحلة الحورية",
            ),
            ChemicalOption(
                product_name="Spirotetramat 15% OD",
                product_name_ar="سبيروتيتامات 15% معلق زيتي",
                active_ingredient="Spirotetramat",
                active_ingredient_ar="سبيروتيتامات",
                formulation="OD",
                rate_per_ha="0.8-1 L/ha",
                rate_unit="L/ha",
                phi_days=14,
                rei_hours=24,
                target_stages=[PestLifeStage.NYMPH],
                mode_of_action="Lipid synthesis inhibitor - systemic",
                mode_of_action_ar="مثبط تصنيع الدهون - جهازي",
                efficacy="excellent",
                resistance_risk="low",
                notes="Two-way systemic - good for hidden stages",
                notes_ar="جهازي ثنائي الاتجاه - جيد للمراحل المختفية",
            ),
        ],
        "biological_options": [
            BiologicalOption(
                agent_name="Azadirachtin (Neem)",
                agent_name_ar="أزاديراكتين (النيم)",
                agent_type="botanical_insecticide",
                target_pest_stages=[PestLifeStage.NYMPH],
                application_rate="3-5 ml/L water",
                application_method="Foliar spray",
                application_method_ar="رش ورقي",
                optimal_conditions="Early morning or late afternoon",
                optimal_conditions_ar="الصباح الباكر أو بعد العصر",
                efficacy="moderate",
                notes="IGR effect - disrupts molting. Requires repeat applications.",
                notes_ar="تأثير منظم نمو - يعيق الانسلاخ. يتطلب تطبيقات متكررة.",
            ),
        ],
        "cultural_practices": [
            CulturalPractice(
                practice="High-pressure water spray",
                practice_ar="رش الماء عالي الضغط",
                timing="Before chemical spray to remove honeydew and sooty mold",
                timing_ar="قبل الرش الكيميائي لإزالة الندوة العسلية والعفن الهبابي",
                effectiveness="supplementary",
                cost="low",
            ),
            CulturalPractice(
                practice="Pruning and removal of heavily infested fronds",
                practice_ar="تقليم وإزالة السعف المصاب بشدة",
                timing="Before population buildup",
                timing_ar="قبل تراكم الأعداد",
                effectiveness="moderate",
                cost="moderate",
            ),
        ],
        "precautions": [
            "Time applications based on pest phenology - target early nymphs",
            "Use high water volume for good coverage (1000+ L/ha)",
            "Monitor for natural enemies before spraying",
        ],
        "precautions_ar": [
            "وقت التطبيقات بناءً على فينولوجيا الآفة - استهدف الحوريات المبكرة",
            "استخدم حجم ماء عالي للتغطية الجيدة (1000+ لتر/هكتار)",
            "راقب الأعداء الطبيعيين قبل الرش",
        ],
    },
    # -------------------------------------------------------------------------
    # APHIDS - المن
    # -------------------------------------------------------------------------
    "APHID001": {
        "pest_name": "Cotton/Melon Aphid",
        "pest_name_ar": "من القطن/الخضروات",
        "urgency": TreatmentUrgency.SOON,
        "primary_strategy": "IPM approach: conserve natural enemies, use selective insecticides when needed",
        "primary_strategy_ar": "نهج المكافحة المتكاملة: حافظ على الأعداء الطبيعيين، استخدم مبيدات انتقائية عند الحاجة",
        "chemical_options": [
            ChemicalOption(
                product_name="Flonicamid 50% WG",
                product_name_ar="فلونيكاميد 50% محبب قابل للبلل",
                active_ingredient="Flonicamid",
                active_ingredient_ar="فلونيكاميد",
                formulation="WG",
                rate_per_ha="140-200 g/ha",
                rate_unit="g/ha",
                phi_days=3,
                rei_hours=12,
                target_stages=[PestLifeStage.NYMPH, PestLifeStage.ADULT],
                mode_of_action="Selective feeding blocker",
                mode_of_action_ar="مانع تغذية انتقائي",
                efficacy="excellent",
                resistance_risk="low",
                notes="Soft on beneficials, excellent aphid control",
                notes_ar="لطيف على المفترسات النافعة، مكافحة ممتازة للمن",
            ),
            ChemicalOption(
                product_name="Spirotetramat 15% OD",
                product_name_ar="سبيروتيتامات 15% معلق زيتي",
                active_ingredient="Spirotetramat",
                active_ingredient_ar="سبيروتيتامات",
                formulation="OD",
                rate_per_ha="0.5-0.75 L/ha",
                rate_unit="L/ha",
                phi_days=7,
                rei_hours=24,
                target_stages=[PestLifeStage.NYMPH, PestLifeStage.ADULT],
                mode_of_action="Lipid synthesis inhibitor",
                mode_of_action_ar="مثبط تصنيع الدهون",
                efficacy="excellent",
                resistance_risk="low",
                notes="Systemic, reduces reproduction",
                notes_ar="جهازي، يقلل التكاثر",
            ),
            ChemicalOption(
                product_name="Pymetrozine 50% WG",
                product_name_ar="بيميتروزين 50% محبب قابل للبلل",
                active_ingredient="Pymetrozine",
                active_ingredient_ar="بيميتروزين",
                formulation="WG",
                rate_per_ha="250-300 g/ha",
                rate_unit="g/ha",
                phi_days=3,
                rei_hours=12,
                target_stages=[PestLifeStage.NYMPH, PestLifeStage.ADULT],
                mode_of_action="Feeding inhibitor",
                mode_of_action_ar="مثبط التغذية",
                efficacy="good",
                resistance_risk="moderate",
                notes="Stops feeding rapidly, aphids die within days",
                notes_ar="يوقف التغذية بسرعة، المن يموت خلال أيام",
            ),
        ],
        "biological_options": [
            BiologicalOption(
                agent_name="Aphidius colemani",
                agent_name_ar="أفيديوس كوليماني (طفيل المن)",
                agent_type="parasitoid",
                target_pest_stages=[PestLifeStage.NYMPH, PestLifeStage.ADULT],
                application_rate="1-5 per m2, weekly releases",
                application_method="Release in infested areas",
                application_method_ar="إطلاق في المناطق المصابة",
                optimal_conditions="18-28C, avoid during spray residues",
                optimal_conditions_ar="18-28 مئوية، تجنب خلال بقايا الرش",
                efficacy="excellent",
                notes="Preventive releases before aphid buildup most effective",
                notes_ar="الإطلاقات الوقائية قبل تراكم المن أكثر فعالية",
            ),
            BiologicalOption(
                agent_name="Chrysoperla carnea (Green Lacewing)",
                agent_name_ar="أسد المن (الكريسوبيرلا)",
                agent_type="predator",
                target_pest_stages=[PestLifeStage.NYMPH, PestLifeStage.ADULT],
                application_rate="5-10 larvae per m2",
                application_method="Distribute larvae on infested plants",
                application_method_ar="توزيع اليرقات على النباتات المصابة",
                optimal_conditions="Humidity >50%",
                optimal_conditions_ar="رطوبة >50%",
                efficacy="good",
                notes="Voracious predator, also feeds on other pests",
                notes_ar="مفترس شره، يتغذى أيضاً على آفات أخرى",
            ),
            BiologicalOption(
                agent_name="Insecticidal soap",
                agent_name_ar="صابون مبيد للحشرات",
                agent_type="biopesticide",
                target_pest_stages=[PestLifeStage.NYMPH, PestLifeStage.ADULT],
                application_rate="10-20 ml/L water",
                application_method="Thorough coverage spray",
                application_method_ar="رش بتغطية شاملة",
                optimal_conditions="Avoid during hot midday",
                optimal_conditions_ar="تجنب خلال منتصف النهار الحار",
                efficacy="moderate",
                notes="Contact action only, repeat every 5-7 days",
                notes_ar="فعل تلامسي فقط، كرر كل 5-7 أيام",
            ),
        ],
        "cultural_practices": [
            CulturalPractice(
                practice="Reflective mulches",
                practice_ar="أغطية عاكسة",
                timing="At planting, especially for virus-prone crops",
                timing_ar="عند الزراعة، خاصة للمحاصيل المعرضة للفيروسات",
                effectiveness="moderate",
                cost="moderate",
                notes="Disorients flying aphids",
                notes_ar="تربك المن الطائر",
            ),
            CulturalPractice(
                practice="Remove infested plant parts",
                practice_ar="إزالة أجزاء النبات المصابة",
                timing="At first detection of colonies",
                timing_ar="عند أول اكتشاف للمستعمرات",
                effectiveness="moderate",
                cost="low",
            ),
            CulturalPractice(
                practice="Avoid excessive nitrogen fertilization",
                practice_ar="تجنب الإفراط في التسميد النيتروجيني",
                timing="Throughout growing season",
                timing_ar="طوال موسم النمو",
                effectiveness="moderate",
                cost="low",
                notes="Excess N promotes succulent growth attractive to aphids",
                notes_ar="النيتروجين الزائد يعزز النمو الغض الجاذب للمن",
            ),
        ],
        "precautions": [
            "Rotate insecticide modes of action to prevent resistance",
            "Preserve natural enemies - avoid broad-spectrum insecticides",
            "Consider virus transmission risk when setting thresholds",
        ],
        "precautions_ar": [
            "بدل آليات عمل المبيدات لمنع المقاومة",
            "حافظ على الأعداء الطبيعيين - تجنب المبيدات واسعة الطيف",
            "راعِ خطر نقل الفيروسات عند تحديد العتبات",
        ],
    },
    # -------------------------------------------------------------------------
    # WHITEFLIES - الذبابة البيضاء
    # -------------------------------------------------------------------------
    "WHITEFLY001": {
        "pest_name": "Silverleaf Whitefly",
        "pest_name_ar": "الذبابة البيضاء",
        "urgency": TreatmentUrgency.URGENT,
        "primary_strategy": "Prevention and early intervention critical. IPM with emphasis on resistance management.",
        "primary_strategy_ar": "الوقاية والتدخل المبكر ضروريان. مكافحة متكاملة مع التركيز على إدارة المقاومة.",
        "chemical_options": [
            ChemicalOption(
                product_name="Cyantraniliprole 10% OD",
                product_name_ar="سيانترانيليبرول 10% معلق زيتي",
                active_ingredient="Cyantraniliprole",
                active_ingredient_ar="سيانترانيليبرول",
                formulation="OD",
                rate_per_ha="0.75-1 L/ha",
                rate_unit="L/ha",
                phi_days=3,
                rei_hours=12,
                target_stages=[PestLifeStage.NYMPH, PestLifeStage.ADULT],
                mode_of_action="Ryanodine receptor modulator",
                mode_of_action_ar="معدل مستقبل الريانودين",
                efficacy="excellent",
                resistance_risk="low",
                notes="Excellent translaminar activity, good for nymphs on leaf undersides",
                notes_ar="نشاط عبر الورقة ممتاز، جيد للحوريات على السطح السفلي",
            ),
            ChemicalOption(
                product_name="Spiromesifen 24% SC",
                product_name_ar="سبيروميسيفين 24% معلق مركز",
                active_ingredient="Spiromesifen",
                active_ingredient_ar="سبيروميسيفين",
                formulation="SC",
                rate_per_ha="0.4-0.5 L/ha",
                rate_unit="L/ha",
                phi_days=3,
                rei_hours=24,
                target_stages=[PestLifeStage.EGG, PestLifeStage.NYMPH],
                mode_of_action="Lipid synthesis inhibitor",
                mode_of_action_ar="مثبط تصنيع الدهون",
                efficacy="excellent",
                resistance_risk="low",
                notes="Ovicidal and larvicidal, affects immature stages",
                notes_ar="قاتل للبيض واليرقات، يؤثر على المراحل غير الناضجة",
            ),
            ChemicalOption(
                product_name="Pyriproxyfen 10% EC",
                product_name_ar="بيريبروكسيفين 10% مركز قابل للاستحلاب",
                active_ingredient="Pyriproxyfen",
                active_ingredient_ar="بيريبروكسيفين",
                formulation="EC",
                rate_per_ha="0.5-0.75 L/ha",
                rate_unit="L/ha",
                phi_days=7,
                rei_hours=24,
                target_stages=[PestLifeStage.EGG, PestLifeStage.NYMPH],
                mode_of_action="Juvenile hormone mimic",
                mode_of_action_ar="مقلد هرمون الأحداث",
                efficacy="good",
                resistance_risk="moderate",
                notes="IGR - prevents metamorphosis, sterilizes adults",
                notes_ar="منظم نمو - يمنع التحول، يعقم الحشرات الكاملة",
            ),
        ],
        "biological_options": [
            BiologicalOption(
                agent_name="Encarsia formosa",
                agent_name_ar="إنكارسيا فورموسا (طفيل الذبابة البيضاء)",
                agent_type="parasitoid",
                target_pest_stages=[PestLifeStage.NYMPH],
                application_rate="3-10 per m2, weekly",
                application_method="Release cards or loose parasitoids",
                application_method_ar="إطلاق بطاقات أو طفيليات سائبة",
                optimal_conditions="20-27C, avoid during spray residues",
                optimal_conditions_ar="20-27 مئوية، تجنب خلال بقايا الرش",
                efficacy="excellent",
                notes="Most effective when introduced early at low whitefly densities",
                notes_ar="أكثر فعالية عند التقديم المبكر بكثافات منخفضة للذبابة البيضاء",
            ),
            BiologicalOption(
                agent_name="Beauveria bassiana",
                agent_name_ar="فطر البوفيريا",
                agent_type="entomopathogenic_fungus",
                target_pest_stages=[PestLifeStage.NYMPH, PestLifeStage.ADULT],
                application_rate="As per product label",
                application_method="Foliar spray, thorough coverage",
                application_method_ar="رش ورقي، تغطية شاملة",
                optimal_conditions="High humidity >70%",
                optimal_conditions_ar="رطوبة عالية >70%",
                efficacy="moderate",
                notes="Best combined with other tactics",
                notes_ar="أفضل بالتزامن مع تكتيكات أخرى",
            ),
        ],
        "cultural_practices": [
            CulturalPractice(
                practice="Yellow sticky traps for monitoring and mass trapping",
                practice_ar="مصائد لاصقة صفراء للمراقبة والصيد الجماعي",
                timing="Throughout growing season, 1 per 100m2",
                timing_ar="طوال موسم النمو، 1 لكل 100م2",
                effectiveness="moderate",
                cost="low",
            ),
            CulturalPractice(
                practice="Use virus-resistant varieties",
                practice_ar="استخدم أصناف مقاومة للفيروسات",
                timing="At planting",
                timing_ar="عند الزراعة",
                effectiveness="high",
                cost="low",
                notes="TYLCV-resistant tomato varieties essential in endemic areas",
                notes_ar="أصناف الطماطم المقاومة لـ TYLCV ضرورية في المناطق المتوطنة",
            ),
            CulturalPractice(
                practice="Crop-free period",
                practice_ar="فترة خالية من المحصول",
                timing="2-4 weeks between crops",
                timing_ar="2-4 أسابيع بين المحاصيل",
                effectiveness="high",
                cost="moderate",
                notes="Breaks pest cycle, reduces initial infestation",
                notes_ar="يقطع دورة الآفة، يقلل الإصابة الأولية",
            ),
            CulturalPractice(
                practice="Insect-proof netting on greenhouse vents",
                practice_ar="شبكات مقاومة للحشرات على فتحات البيوت المحمية",
                timing="Permanent installation",
                timing_ar="تركيب دائم",
                effectiveness="high",
                cost="high",
                notes="50 mesh or finer",
                notes_ar="50 ثقب في البوصة أو أدق",
            ),
        ],
        "precautions": [
            "Strict resistance management - rotate modes of action",
            "TYLCV vector - consider virus transmission in management",
            "Avoid pyrethroid sprays - promote resistance",
            "Scout frequently, treat at low densities",
        ],
        "precautions_ar": [
            "إدارة مقاومة صارمة - بدل آليات العمل",
            "ناقل TYLCV - راعِ نقل الفيروسات في الإدارة",
            "تجنب رشات البيرثرويد - تعزز المقاومة",
            "امسح بشكل متكرر، عالج عند الكثافات المنخفضة",
        ],
    },
    # -------------------------------------------------------------------------
    # SPIDER MITES - العنكبوت الأحمر
    # -------------------------------------------------------------------------
    "MITE001": {
        "pest_name": "Two-spotted Spider Mite",
        "pest_name_ar": "العنكبوت الأحمر ذو البقعتين",
        "urgency": TreatmentUrgency.URGENT,
        "primary_strategy": "Rapid intervention needed. Acaricide rotation essential due to high resistance risk.",
        "primary_strategy_ar": "تدخل سريع ضروري. تبديل المبيدات الأكاروسية ضروري بسبب خطر المقاومة العالي.",
        "chemical_options": [
            ChemicalOption(
                product_name="Abamectin 1.8% EC",
                product_name_ar="أبامكتين 1.8% مركز قابل للاستحلاب",
                active_ingredient="Abamectin",
                active_ingredient_ar="أبامكتين",
                formulation="EC",
                rate_per_ha="0.5-0.75 L/ha",
                rate_unit="L/ha",
                phi_days=7,
                rei_hours=24,
                target_stages=[PestLifeStage.NYMPH, PestLifeStage.ADULT],
                mode_of_action="Chloride channel activator",
                mode_of_action_ar="منشط قناة الكلوريد",
                efficacy="good",
                resistance_risk="high",
                notes="Translaminar activity, avoid overuse",
                notes_ar="نشاط عبر الورقة، تجنب الإفراط في الاستخدام",
            ),
            ChemicalOption(
                product_name="Bifenazate 24% SC",
                product_name_ar="بيفينازات 24% معلق مركز",
                active_ingredient="Bifenazate",
                active_ingredient_ar="بيفينازات",
                formulation="SC",
                rate_per_ha="0.5-0.6 L/ha",
                rate_unit="L/ha",
                phi_days=3,
                rei_hours=12,
                target_stages=[PestLifeStage.NYMPH, PestLifeStage.ADULT],
                mode_of_action="METI acaricide",
                mode_of_action_ar="مبيد أكاروسي METI",
                efficacy="excellent",
                resistance_risk="moderate",
                notes="Specific to mites, safe on beneficials",
                notes_ar="خاص بالعناكب، آمن على المفترسات النافعة",
            ),
            ChemicalOption(
                product_name="Etoxazole 11% SC",
                product_name_ar="إيتوكسازول 11% معلق مركز",
                active_ingredient="Etoxazole",
                active_ingredient_ar="إيتوكسازول",
                formulation="SC",
                rate_per_ha="0.5-0.6 L/ha",
                rate_unit="L/ha",
                phi_days=7,
                rei_hours=24,
                target_stages=[PestLifeStage.EGG, PestLifeStage.NYMPH],
                mode_of_action="Mite growth inhibitor",
                mode_of_action_ar="مثبط نمو العناكب",
                efficacy="excellent",
                resistance_risk="low",
                notes="Ovicide/larvicide, no adult activity",
                notes_ar="قاتل للبيض واليرقات، لا نشاط على الحشرات الكاملة",
            ),
        ],
        "biological_options": [
            BiologicalOption(
                agent_name="Phytoseiulus persimilis",
                agent_name_ar="فيتوسيلس بيرسيميليس (مفترس العنكبوت)",
                agent_type="predatory_mite",
                target_pest_stages=[PestLifeStage.EGG, PestLifeStage.NYMPH, PestLifeStage.ADULT],
                application_rate="5-20 per m2 depending on infestation",
                application_method="Distribute on infested leaves",
                application_method_ar="توزيع على الأوراق المصابة",
                optimal_conditions="20-27C, humidity >60%",
                optimal_conditions_ar="20-27 مئوية، رطوبة >60%",
                efficacy="excellent",
                notes="Specialist predator, very effective in humid conditions",
                notes_ar="مفترس متخصص، فعال جداً في الظروف الرطبة",
            ),
            BiologicalOption(
                agent_name="Amblyseius californicus",
                agent_name_ar="أمبليسيوس كاليفورنيكس",
                agent_type="predatory_mite",
                target_pest_stages=[PestLifeStage.EGG, PestLifeStage.NYMPH, PestLifeStage.ADULT],
                application_rate="5-10 per m2",
                application_method="Preventive release on crop",
                application_method_ar="إطلاق وقائي على المحصول",
                optimal_conditions="Tolerates lower humidity than P. persimilis",
                optimal_conditions_ar="يتحمل رطوبة أقل من P. persimilis",
                efficacy="good",
                notes="Generalist, survives on pollen, better in dry conditions",
                notes_ar="عام التغذية، يعيش على حبوب اللقاح، أفضل في الظروف الجافة",
            ),
        ],
        "cultural_practices": [
            CulturalPractice(
                practice="Overhead irrigation / water spraying",
                practice_ar="الري العلوي / رش الماء",
                timing="During hot, dry periods",
                timing_ar="خلال الفترات الحارة والجافة",
                effectiveness="moderate",
                cost="low",
                notes="Increases humidity, dislodges mites",
                notes_ar="يزيد الرطوبة، يزيح العناكب",
            ),
            CulturalPractice(
                practice="Remove and destroy heavily infested leaves",
                practice_ar="إزالة وتدمير الأوراق المصابة بشدة",
                timing="At first detection of hot spots",
                timing_ar="عند أول اكتشاف للبؤر الساخنة",
                effectiveness="moderate",
                cost="low",
            ),
            CulturalPractice(
                practice="Control dust on foliage",
                practice_ar="مكافحة الغبار على الأوراق",
                timing="Throughout season",
                timing_ar="طوال الموسم",
                effectiveness="moderate",
                cost="low",
                notes="Dust favors mites, inhibits predators",
                notes_ar="الغبار يفضل العناكب، يثبط المفترسات",
            ),
        ],
        "precautions": [
            "Rotate acaricide modes of action - max 2 applications per mode/season",
            "Avoid broad-spectrum insecticides that kill predatory mites",
            "Treat hot spots immediately - populations explode in hot weather",
            "Thorough coverage essential - especially leaf undersides",
        ],
        "precautions_ar": [
            "بدل آليات عمل المبيدات الأكاروسية - أقصى تطبيقين لكل آلية/موسم",
            "تجنب المبيدات واسعة الطيف التي تقتل العناكب المفترسة",
            "عالج البؤر الساخنة فوراً - الأعداد تنفجر في الطقس الحار",
            "التغطية الشاملة ضرورية - خاصة السطح السفلي للأوراق",
        ],
    },
    # -------------------------------------------------------------------------
    # TUTA ABSOLUTA - حافرة أنفاق الطماطم
    # -------------------------------------------------------------------------
    "TUTA001": {
        "pest_name": "Tomato Leafminer",
        "pest_name_ar": "حافرة أنفاق الطماطم",
        "urgency": TreatmentUrgency.IMMEDIATE,
        "primary_strategy": "Intensive IPM program combining multiple tactics. Early detection critical.",
        "primary_strategy_ar": "برنامج مكافحة متكاملة مكثف يجمع تكتيكات متعددة. الكشف المبكر ضروري.",
        "chemical_options": [
            ChemicalOption(
                product_name="Chlorantraniliprole 20% SC",
                product_name_ar="كلورانترانيليبرول 20% معلق مركز",
                active_ingredient="Chlorantraniliprole",
                active_ingredient_ar="كلورانترانيليبرول",
                formulation="SC",
                rate_per_ha="150-200 ml/ha",
                rate_unit="ml/ha",
                phi_days=1,
                rei_hours=12,
                target_stages=[PestLifeStage.EGG, PestLifeStage.LARVA],
                mode_of_action="Ryanodine receptor modulator (diamide)",
                mode_of_action_ar="معدل مستقبل الريانودين (دياميد)",
                efficacy="excellent",
                resistance_risk="moderate",
                notes="Ovicidal and larvicidal, excellent control",
                notes_ar="قاتل للبيض واليرقات، مكافحة ممتازة",
            ),
            ChemicalOption(
                product_name="Spinosad 48% SC",
                product_name_ar="سبينوساد 48% معلق مركز",
                active_ingredient="Spinosad",
                active_ingredient_ar="سبينوساد",
                formulation="SC",
                rate_per_ha="200-300 ml/ha",
                rate_unit="ml/ha",
                phi_days=3,
                rei_hours=12,
                target_stages=[PestLifeStage.LARVA],
                mode_of_action="Nicotinic receptor allosteric activator",
                mode_of_action_ar="منشط ألوستيري لمستقبل النيكوتين",
                efficacy="excellent",
                resistance_risk="moderate",
                notes="Organic-approved option",
                notes_ar="خيار معتمد للزراعة العضوية",
            ),
            ChemicalOption(
                product_name="Indoxacarb 15% SC",
                product_name_ar="إندوكساكارب 15% معلق مركز",
                active_ingredient="Indoxacarb",
                active_ingredient_ar="إندوكساكارب",
                formulation="SC",
                rate_per_ha="300-400 ml/ha",
                rate_unit="ml/ha",
                phi_days=7,
                rei_hours=24,
                target_stages=[PestLifeStage.LARVA],
                mode_of_action="Sodium channel blocker (oxadiazine)",
                mode_of_action_ar="مانع قناة الصوديوم (أوكساديازين)",
                efficacy="good",
                resistance_risk="moderate",
                notes="Different mode of action for rotation",
                notes_ar="آلية عمل مختلفة للتبديل",
            ),
        ],
        "biological_options": [
            BiologicalOption(
                agent_name="Trichogramma spp.",
                agent_name_ar="تريكوجراما (طفيل البيض)",
                agent_type="egg_parasitoid",
                target_pest_stages=[PestLifeStage.EGG],
                application_rate="100,000-200,000 per ha, 2-3 releases/week",
                application_method="Cards or capsules distributed in crop",
                application_method_ar="بطاقات أو كبسولات موزعة في المحصول",
                optimal_conditions="Start releases at transplanting or first moth catch",
                optimal_conditions_ar="ابدأ الإطلاقات عند الشتل أو أول صيد للعثة",
                efficacy="good",
                notes="Preventive, must be started early",
                notes_ar="وقائي، يجب البدء مبكراً",
            ),
            BiologicalOption(
                agent_name="Nesidiocoris tenuis",
                agent_name_ar="نيسيديوكوريس (البق المفترس)",
                agent_type="predator",
                target_pest_stages=[PestLifeStage.EGG, PestLifeStage.LARVA],
                application_rate="0.5-1 per m2",
                application_method="Release in greenhouse",
                application_method_ar="إطلاق في البيت المحمي",
                optimal_conditions="Establish before Tuta arrives",
                optimal_conditions_ar="ثبت قبل وصول توتا",
                efficacy="good",
                notes="Also feeds on whitefly and spider mites",
                notes_ar="يتغذى أيضاً على الذبابة البيضاء والعنكبوت الأحمر",
            ),
            BiologicalOption(
                agent_name="Bacillus thuringiensis kurstaki",
                agent_name_ar="باسيلس ثورنجينسيس (بي تي)",
                agent_type="microbial_insecticide",
                target_pest_stages=[PestLifeStage.LARVA],
                application_rate="1-2 kg/ha",
                application_method="Foliar spray, repeat every 5-7 days",
                application_method_ar="رش ورقي، كرر كل 5-7 أيام",
                optimal_conditions="Spray late afternoon, larvae actively feeding",
                optimal_conditions_ar="رش بعد العصر، اليرقات تتغذى بنشاط",
                efficacy="moderate",
                notes="Must be ingested, works slowly",
                notes_ar="يجب أن يُبتلع، يعمل ببطء",
            ),
        ],
        "cultural_practices": [
            CulturalPractice(
                practice="Pheromone mass trapping",
                practice_ar="الصيد الجماعي بالفرمونات",
                timing="20-40 traps/ha, started 2 weeks before transplanting",
                timing_ar="20-40 مصيدة/هكتار، تبدأ قبل أسبوعين من الشتل",
                effectiveness="moderate",
                cost="moderate",
                notes="Reduces male population, use with water traps",
                notes_ar="يقلل أعداد الذكور، استخدم مع مصائد مائية",
            ),
            CulturalPractice(
                practice="Remove and destroy infested plant material",
                practice_ar="إزالة وتدمير المواد النباتية المصابة",
                timing="Throughout season",
                timing_ar="طوال الموسم",
                effectiveness="moderate",
                cost="moderate",
                notes="Seal in bags before removal from greenhouse",
                notes_ar="أغلق في أكياس قبل الإزالة من البيت المحمي",
            ),
            CulturalPractice(
                practice="Insect-proof netting",
                practice_ar="شبكات مقاومة للحشرات",
                timing="Permanent on greenhouse vents and doors",
                timing_ar="دائمة على فتحات وأبواب البيت المحمي",
                effectiveness="high",
                cost="high",
                notes="9x6 threads/cm minimum",
                notes_ar="9×6 خيوط/سم كحد أدنى",
            ),
            CulturalPractice(
                practice="Crop-free period",
                practice_ar="فترة خالية من المحصول",
                timing="Minimum 6 weeks between tomato crops",
                timing_ar="6 أسابيع كحد أدنى بين محاصيل الطماطم",
                effectiveness="high",
                cost="moderate",
            ),
        ],
        "precautions": [
            "Quarantine pest in some regions - check regulations",
            "Intensive monitoring essential - check traps 2-3 times/week",
            "Never rely on single control method",
            "Rotate chemical classes strictly",
            "Zero tolerance for fruit damage in markets",
        ],
        "precautions_ar": [
            "آفة حجر زراعي في بعض المناطق - تحقق من اللوائح",
            "المراقبة المكثفة ضرورية - افحص المصائد 2-3 مرات/أسبوع",
            "لا تعتمد أبداً على طريقة مكافحة واحدة",
            "بدل الفئات الكيميائية بصرامة",
            "لا تحمل لأي ضرر للثمار في الأسواق",
        ],
    },
}


# =============================================================================
# RECOMMENDATION GENERATOR - مولد التوصيات
# =============================================================================


def get_treatment_protocol(pest_id: str) -> dict[str, Any] | None:
    """
    Get treatment protocol for a pest.
    الحصول على بروتوكول العلاج لآفة.
    """
    return TREATMENT_PROTOCOLS.get(pest_id)


def generate_treatment_recommendation(
    pest_id: str,
    crop_type: CropType,
    growth_stage: str,
    infestation_level: InfestationLevel,
    area_ha: float = 1.0,
    assessment: ThresholdAssessment | None = None,
    prefer_biological: bool = False,
    organic_only: bool = False,
    field_id: str = "",
) -> TreatmentRecommendation | None:
    """
    Generate comprehensive treatment recommendation.

    إنشاء توصية علاج شاملة.

    Args:
        pest_id: Pest identifier
        crop_type: Target crop
        growth_stage: Current crop growth stage
        infestation_level: Assessed infestation level
        area_ha: Field area in hectares
        assessment: Optional threshold assessment
        prefer_biological: Prioritize biological options
        organic_only: Only include organic-compatible options
        field_id: Field identifier

    Returns:
        TreatmentRecommendation object
    """
    protocol = get_treatment_protocol(pest_id)
    if not protocol:
        return None

    # Determine treatment type and urgency
    if organic_only:
        treatment_type = TreatmentType.BIOLOGICAL
    elif prefer_biological and protocol.get("biological_options"):
        treatment_type = TreatmentType.INTEGRATED
    else:
        treatment_type = TreatmentType.INTEGRATED

    # Determine urgency based on infestation level
    if infestation_level in (InfestationLevel.CRITICAL, InfestationLevel.SEVERE):
        urgency = TreatmentUrgency.IMMEDIATE
    elif infestation_level == InfestationLevel.HIGH:
        urgency = TreatmentUrgency.URGENT
    elif infestation_level == InfestationLevel.MODERATE or assessment and assessment.exceeds_action_threshold:
        urgency = TreatmentUrgency.SOON
    else:
        urgency = TreatmentUrgency.MONITOR

    # Build recommendation
    rec = TreatmentRecommendation(
        pest_id=pest_id,
        pest_name=protocol["pest_name"],
        pest_name_ar=protocol["pest_name_ar"],
        field_id=field_id,
        crop_type=crop_type,
        growth_stage=growth_stage,
        area_to_treat_ha=area_ha,
        treatment_type=treatment_type,
        urgency=urgency,
        recommendation_title=f"Treatment for {protocol['pest_name']}",
        recommendation_title_ar=f"علاج {protocol['pest_name_ar']}",
        recommendation_details=protocol.get("primary_strategy", ""),
        recommendation_details_ar=protocol.get("primary_strategy_ar", ""),
        precautions=protocol.get("precautions", []),
        precautions_ar=protocol.get("precautions_ar", []),
    )

    # Add chemical options (if not organic only)
    if not organic_only:
        chemical_opts = protocol.get("chemical_options", [])
        rec.chemical_options = [opt.to_dict() for opt in chemical_opts[:3]]

    # Add biological options
    bio_opts = protocol.get("biological_options", [])
    rec.biological_options = [opt.to_dict() for opt in bio_opts[:3]]

    # Add cultural practices
    cultural = protocol.get("cultural_practices", [])
    rec.cultural_practices = [p.practice for p in cultural]
    rec.cultural_practices_ar = [p.practice_ar for p in cultural]

    # Application timing
    rec.application_timing = _get_application_timing(urgency)
    rec.application_timing_ar = _get_application_timing_ar(urgency)

    # Application method
    if rec.chemical_options:
        rec.application_method = "Foliar spray with thorough coverage"
        rec.application_method_ar = "رش ورقي بتغطية شاملة"
    elif rec.biological_options:
        rec.application_method = "Biological agent release per protocol"
        rec.application_method_ar = "إطلاق العامل الحيوي حسب البروتوكول"

    # Economic analysis
    if assessment:
        rec.estimated_cost_per_ha = assessment.treatment_cost / max(area_ha, 1)
        rec.estimated_total_cost = assessment.treatment_cost
        rec.expected_yield_saved_pct = min(80.0, assessment.percentage_of_economic_threshold)
        rec.roi_estimate = assessment.benefit_cost_ratio

    # Follow-up
    rec.follow_up_scouting_days = 7
    rec.retreatment_interval_days = _get_retreatment_interval(pest_id)
    rec.max_applications = 3

    # Weather requirements
    rec.weather_requirements = "Temperature 15-30C, wind <15 km/h, no rain expected for 4+ hours"
    rec.weather_requirements_ar = "درجة حرارة 15-30 مئوية، رياح <15 كم/ساعة، لا أمطار متوقعة لـ 4+ ساعات"

    # Set optimal window
    now = datetime.now(UTC)
    if urgency == TreatmentUrgency.IMMEDIATE:
        rec.optimal_window_start = now
        rec.optimal_window_end = now + timedelta(hours=48)
    elif urgency == TreatmentUrgency.URGENT:
        rec.optimal_window_start = now
        rec.optimal_window_end = now + timedelta(days=3)
    elif urgency == TreatmentUrgency.SOON:
        rec.optimal_window_start = now
        rec.optimal_window_end = now + timedelta(days=7)

    return rec


def _get_application_timing(urgency: TreatmentUrgency) -> str:
    """Get application timing based on urgency."""
    timings = {
        TreatmentUrgency.IMMEDIATE: "Apply within 24-48 hours. Early morning (6-9 AM) or late afternoon (4-6 PM).",
        TreatmentUrgency.URGENT: "Apply within 2-3 days. Early morning preferred.",
        TreatmentUrgency.SOON: "Apply within 1 week at next suitable spray window.",
        TreatmentUrgency.SCHEDULED: "Apply according to normal schedule.",
        TreatmentUrgency.PREVENTIVE: "Apply before pest arrives or population builds.",
        TreatmentUrgency.MONITOR: "Continue monitoring. No treatment needed at this time.",
    }
    return timings.get(urgency, "Follow IPM guidelines")


def _get_application_timing_ar(urgency: TreatmentUrgency) -> str:
    """Get application timing in Arabic based on urgency."""
    timings = {
        TreatmentUrgency.IMMEDIATE: "طبق خلال 24-48 ساعة. الصباح الباكر (6-9 صباحاً) أو بعد العصر (4-6 مساءً).",
        TreatmentUrgency.URGENT: "طبق خلال 2-3 أيام. الصباح الباكر مفضل.",
        TreatmentUrgency.SOON: "طبق خلال أسبوع في نافذة الرش المناسبة التالية.",
        TreatmentUrgency.SCHEDULED: "طبق وفقاً للجدول العادي.",
        TreatmentUrgency.PREVENTIVE: "طبق قبل وصول الآفة أو تراكم الأعداد.",
        TreatmentUrgency.MONITOR: "استمر في المراقبة. لا علاج مطلوب حالياً.",
    }
    return timings.get(urgency, "اتبع إرشادات المكافحة المتكاملة")


def _get_retreatment_interval(pest_id: str) -> int:
    """Get retreatment interval days for a pest."""
    intervals = {
        "RPW001": 30,  # Monthly for RPW
        "DUBAS001": 14,  # Bi-weekly during active generation
        "APHID001": 7,
        "APHID002": 7,
        "WHITEFLY001": 7,
        "MITE001": 5,  # Short due to rapid reproduction
        "TUTA001": 7,
        "DMOTH001": 10,
        "LOCUST001": 7,
        "THRIPS001": 7,
        "FRUITFLY001": 7,
    }
    return intervals.get(pest_id, 10)


def generate_recommendation_from_alert(
    alert: PestAlert,
    prefer_biological: bool = False,
    organic_only: bool = False,
) -> TreatmentRecommendation | None:
    """
    Generate treatment recommendation from a pest alert.

    إنشاء توصية علاج من تنبيه آفة.
    """
    # Map alert priority to infestation level
    priority_to_level = {
        AlertPriority.CRITICAL: InfestationLevel.CRITICAL,
        AlertPriority.HIGH: InfestationLevel.SEVERE,
        AlertPriority.MEDIUM: InfestationLevel.HIGH,
        AlertPriority.LOW: InfestationLevel.MODERATE,
        AlertPriority.INFORMATIONAL: InfestationLevel.LOW,
    }

    level = priority_to_level.get(alert.priority, InfestationLevel.MODERATE)

    rec = generate_treatment_recommendation(
        pest_id=alert.pest_id,
        crop_type=alert.crop_type,
        growth_stage=alert.growth_stage,
        infestation_level=level,
        area_ha=alert.area_affected_ha or 1.0,
        prefer_biological=prefer_biological,
        organic_only=organic_only,
        field_id=alert.field_id,
    )

    if rec:
        rec.alert_id = alert.id

    return rec


def generate_recommendations_from_report(
    report: ScoutReport,
    assessments: list[ThresholdAssessment],
    prefer_biological: bool = False,
    organic_only: bool = False,
) -> list[TreatmentRecommendation]:
    """
    Generate treatment recommendations from a scout report and its assessments.

    إنشاء توصيات علاج من تقرير مسح وتقييماته.
    """
    recommendations: list[TreatmentRecommendation] = []

    for assessment in assessments:
        if assessment.action_required:
            rec = generate_treatment_recommendation(
                pest_id=assessment.pest_id,
                crop_type=report.crop_type,
                growth_stage=report.growth_stage,
                infestation_level=assessment.infestation_level,
                area_ha=report.field_area_ha or 1.0,
                assessment=assessment,
                prefer_biological=prefer_biological,
                organic_only=organic_only,
                field_id=report.field_id,
            )
            if rec:
                rec.scout_report_id = report.id
                recommendations.append(rec)

    return recommendations


# =============================================================================
# ROTATION RECOMMENDATIONS - توصيات التبديل
# =============================================================================


def get_rotation_recommendation(
    pest_id: str,
    recent_treatments: list[str],  # List of recently used active ingredients
) -> dict[str, Any]:
    """
    Get insecticide rotation recommendation to manage resistance.

    الحصول على توصية تبديل المبيدات لإدارة المقاومة.

    Args:
        pest_id: Pest identifier
        recent_treatments: List of active ingredients used in recent treatments

    Returns:
        Dict with recommended next treatment and rotation advice
    """
    protocol = get_treatment_protocol(pest_id)
    if not protocol:
        return {"error": f"No protocol found for pest {pest_id}"}

    chemical_options = protocol.get("chemical_options", [])
    if not chemical_options:
        return {"recommendation": "Use biological control options only"}

    # Group by mode of action
    mode_groups: dict[str, list[ChemicalOption]] = {}
    for opt in chemical_options:
        mode = opt.mode_of_action
        if mode not in mode_groups:
            mode_groups[mode] = []
        mode_groups[mode].append(opt)

    # Find modes of action not recently used
    recent_lower = [ai.lower() for ai in recent_treatments]
    unused_modes: list[str] = []
    for mode, options in mode_groups.items():
        mode_used = any(opt.active_ingredient.lower() in recent_lower for opt in options)
        if not mode_used:
            unused_modes.append(mode)

    # Generate recommendation
    if unused_modes:
        recommended_mode = unused_modes[0]
        recommended_options = mode_groups[recommended_mode]
        return {
            "recommended_mode_of_action": recommended_mode,
            "recommended_products": [
                {
                    "product": opt.product_name,
                    "product_ar": opt.product_name_ar,
                    "active_ingredient": opt.active_ingredient,
                }
                for opt in recommended_options
            ],
            "advice": f"Rotate to {recommended_mode} to reduce resistance risk",
            "advice_ar": f"بدل إلى {recommended_mode} لتقليل خطر المقاومة",
            "recently_used": recent_treatments,
        }
    else:
        return {
            "warning": "All modes of action have been recently used",
            "warning_ar": "جميع آليات العمل استُخدمت مؤخراً",
            "advice": "Consider biological control or wait before next chemical application",
            "advice_ar": "فكر في المكافحة الحيوية أو انتظر قبل التطبيق الكيميائي التالي",
            "recently_used": recent_treatments,
        }


def get_ipm_calendar(
    pest_id: str,
    crop_type: CropType,
) -> list[dict[str, Any]]:
    """
    Get IPM activity calendar for a pest-crop combination.

    الحصول على تقويم أنشطة المكافحة المتكاملة لمجموعة آفة-محصول.
    """
    protocol = get_treatment_protocol(pest_id)
    if not protocol:
        return []

    # Generic IPM calendar activities
    activities = [
        {
            "activity": "Deploy monitoring traps",
            "activity_ar": "نشر مصائد المراقبة",
            "timing": "Before planting / early season",
            "timing_ar": "قبل الزراعة / أول الموسم",
            "frequency": "Continuous",
            "frequency_ar": "مستمر",
        },
        {
            "activity": "Begin scouting",
            "activity_ar": "بدء المسح",
            "timing": "At crop emergence / transplanting",
            "timing_ar": "عند إنبات المحصول / الشتل",
            "frequency": "Weekly to twice weekly",
            "frequency_ar": "أسبوعياً إلى مرتين أسبوعياً",
        },
        {
            "activity": "Release biological control agents",
            "activity_ar": "إطلاق عوامل المكافحة الحيوية",
            "timing": "Before pest pressure builds",
            "timing_ar": "قبل تراكم ضغط الآفة",
            "frequency": "Weekly during risk period",
            "frequency_ar": "أسبوعياً خلال فترة الخطر",
        },
        {
            "activity": "Threshold-based treatments",
            "activity_ar": "علاجات مبنية على العتبة",
            "timing": "When action threshold exceeded",
            "timing_ar": "عند تجاوز عتبة التدخل",
            "frequency": "As needed",
            "frequency_ar": "حسب الحاجة",
        },
        {
            "activity": "Post-harvest sanitation",
            "activity_ar": "الصرف الصحي بعد الحصاد",
            "timing": "Immediately after harvest",
            "timing_ar": "فوراً بعد الحصاد",
            "frequency": "Once per crop cycle",
            "frequency_ar": "مرة لكل دورة محصول",
        },
    ]

    return activities
