"""
SAHOOL Pest Risk Assessment Module
وحدة تقييم مخاطر الآفات

Pest risk assessment based on environmental conditions and vegetation indices.
Based on agricultural research for Yemen crops.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class PestType(str, Enum):
    """
    أنواع الآفات الشائعة - Extended pest types database
    Based on Agricultural Sensing Technology Article (50+ types)
    مرجع: مقالة تكنولوجيا الاستشعار الزراعي (2025)
    """

    # =========================================================================
    # Sucking Insects - الحشرات الماصة
    # =========================================================================
    APHIDS = "aphids"  # من
    WHITEFLY = "whitefly"  # ذبابة بيضاء
    THRIPS = "thrips"  # تربس
    MEALYBUG = "mealybug"  # البق الدقيقي
    SCALE_INSECTS = "scale_insects"  # الحشرات القشرية
    PSYLLIDS = "psyllids"  # سيليد
    LEAFHOPPERS = "leafhoppers"  # نطاطات الأوراق
    PLANT_BUGS = "plant_bugs"  # بق النبات

    # =========================================================================
    # Mites & Acarids - الأكاروسات والعناكب
    # =========================================================================
    MITES = "mites"  # أكاروس
    SPIDER_MITES = "spider_mites"  # العنكبوت الأحمر
    RUST_MITES = "rust_mites"  # أكاروس الصدأ
    BROAD_MITES = "broad_mites"  # الأكاروس العريض

    # =========================================================================
    # Chewing Insects - الحشرات القارضة
    # =========================================================================
    LOCUST = "locust"  # جراد
    ARMYWORM = "armyworm"  # دودة الجيش
    BOLLWORM = "bollworm"  # دودة اللوز
    CUTWORM = "cutworm"  # الدودة القارضة
    CORN_BORER = "corn_borer"  # حفار الذرة
    SUGARCANE_BORER = "sugarcane_borer"  # حفار قصب السكر
    PINK_BOLLWORM = "pink_bollworm"  # دودة اللوز القرنفلية
    TOMATO_LEAFMINER = "tomato_leafminer"  # توتا أبسلوتا
    CABBAGE_LOOPER = "cabbage_looper"  # دودة ورق الملفوف
    DIAMONDBACK_MOTH = "diamondback_moth"  # فراشة الظهر الماسي
    GRASSHOPPERS = "grasshoppers"  # الجنادب
    BEETLES = "beetles"  # الخنافس

    # =========================================================================
    # Borers - الحفارات
    # =========================================================================
    STEM_BORER = "stem_borer"  # حفار الساق
    FRUIT_BORER = "fruit_borer"  # حفار الثمار
    SHOOT_BORER = "shoot_borer"  # حفار البراعم
    ROOT_BORER = "root_borer"  # حفار الجذور

    # =========================================================================
    # Leaf Miners - صانعات الأنفاق
    # =========================================================================
    LEAF_MINER = "leaf_miner"  # صانعة الأنفاق
    CITRUS_LEAFMINER = "citrus_leafminer"  # صانعة أنفاق الحمضيات
    VEGETABLE_LEAFMINER = "vegetable_leafminer"  # صانعة أنفاق الخضر

    # =========================================================================
    # Flies - الذباب
    # =========================================================================
    FRUIT_FLY = "fruit_fly"  # ذبابة الفاكهة
    MEDITERRANEAN_FRUIT_FLY = "mediterranean_fruit_fly"  # ذبابة فاكهة البحر المتوسط
    OLIVE_FRUIT_FLY = "olive_fruit_fly"  # ذبابة ثمار الزيتون
    ONION_FLY = "onion_fly"  # ذبابة البصل
    CARROT_FLY = "carrot_fly"  # ذبابة الجزر
    BEAN_FLY = "bean_fly"  # ذبابة الفاصوليا

    # =========================================================================
    # Date Palm Pests - آفات النخيل
    # =========================================================================
    RED_PALM_WEEVIL = "red_palm_weevil"  # سوسة النخيل الحمراء
    DATE_MOTH = "date_moth"  # فراشة التمر
    DUBAS_BUG = "dubas_bug"  # دوباس النخيل
    LESSER_DATE_MOTH = "lesser_date_moth"  # فراشة التمر الصغرى
    PARLATORIA_SCALE = "parlatoria_scale"  # بارلاتوريا النخيل

    # =========================================================================
    # Coffee & Qat Pests - آفات البن والقات
    # =========================================================================
    COFFEE_BERRY_BORER = "coffee_berry_borer"  # حفار ثمار البن
    COFFEE_LEAF_RUST = "coffee_leaf_rust"  # صدأ أوراق البن
    COFFEE_MEALYBUG = "coffee_mealybug"  # البق الدقيقي للبن

    # =========================================================================
    # Nematodes - النيماتودا
    # =========================================================================
    ROOT_KNOT_NEMATODE = "root_knot_nematode"  # نيماتودا تعقد الجذور
    CYST_NEMATODE = "cyst_nematode"  # نيماتودا الأكياس
    ROOT_LESION_NEMATODE = "root_lesion_nematode"  # نيماتودا تقرح الجذور
    BURROWING_NEMATODE = "burrowing_nematode"  # نيماتودا الجذور الحفارة

    # =========================================================================
    # Soil Pests - آفات التربة
    # =========================================================================
    WIREWORMS = "wireworms"  # الديدان السلكية
    WHITE_GRUBS = "white_grubs"  # اليرقات البيضاء
    TERMITES = "termites"  # النمل الأبيض
    ANTS = "ants"  # النمل
    MOLE_CRICKETS = "mole_crickets"  # الحفارات

    # =========================================================================
    # Storage Pests - آفات المخازن
    # =========================================================================
    GRAIN_WEEVIL = "grain_weevil"  # سوسة الحبوب
    FLOUR_BEETLE = "flour_beetle"  # خنفساء الدقيق
    RICE_WEEVIL = "rice_weevil"  # سوسة الأرز
    KHAPRA_BEETLE = "khapra_beetle"  # خنفساء الخابرا

    # =========================================================================
    # Vertebrate Pests - الآفات الفقارية
    # =========================================================================
    RATS = "rats"  # فئران
    MICE = "mice"  # فأر
    BIRDS = "birds"  # طيور
    QUELEA_BIRDS = "quelea_birds"  # طيور الكيليا
    WILD_BOAR = "wild_boar"  # الخنزير البري

    # =========================================================================
    # Mollusks - الرخويات
    # =========================================================================
    SNAILS = "snails"  # القواقع
    SLUGS = "slugs"  # البزاقات


class RiskLevel(str, Enum):
    """مستوى المخاطر"""

    VERY_LOW = "very_low"  # منخفض جداً
    LOW = "low"  # منخفض
    MODERATE = "moderate"  # متوسط
    HIGH = "high"  # مرتفع
    CRITICAL = "critical"  # حرج


class ControlMethod(str, Enum):
    """طريقة المكافحة"""

    BIOLOGICAL = "biological"  # حيوية
    CHEMICAL = "chemical"  # كيميائية
    CULTURAL = "cultural"  # زراعية
    MECHANICAL = "mechanical"  # ميكانيكية
    INTEGRATED = "integrated"  # متكاملة


@dataclass
class PestControl:
    """طريقة مكافحة الآفة"""

    method: ControlMethod
    product_name: str
    product_name_ar: str
    dosage: str
    dosage_ar: str
    timing: str
    timing_ar: str
    effectiveness: str  # high, medium, low
    safety_interval_days: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method.value,
            "product_name": self.product_name,
            "product_name_ar": self.product_name_ar,
            "dosage": self.dosage,
            "dosage_ar": self.dosage_ar,
            "timing": self.timing,
            "timing_ar": self.timing_ar,
            "effectiveness": self.effectiveness,
            "safety_interval_days": self.safety_interval_days,
        }


@dataclass
class PestRisk:
    """تقييم مخاطر الآفة"""

    pest_type: PestType
    risk_level: RiskLevel
    risk_score: float  # 0-100
    name_en: str
    name_ar: str
    description_en: str
    description_ar: str
    favorable_conditions: list[str]
    favorable_conditions_ar: list[str]
    damage_symptoms_en: list[str]
    damage_symptoms_ar: list[str]
    controls: list[PestControl]
    monitoring_advice_en: str
    monitoring_advice_ar: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "pest_type": self.pest_type.value,
            "risk_level": self.risk_level.value,
            "risk_score": round(self.risk_score, 1),
            "name_en": self.name_en,
            "name_ar": self.name_ar,
            "description_en": self.description_en,
            "description_ar": self.description_ar,
            "favorable_conditions": self.favorable_conditions,
            "favorable_conditions_ar": self.favorable_conditions_ar,
            "damage_symptoms_en": self.damage_symptoms_en,
            "damage_symptoms_ar": self.damage_symptoms_ar,
            "controls": [c.to_dict() for c in self.controls],
            "monitoring_advice_en": self.monitoring_advice_en,
            "monitoring_advice_ar": self.monitoring_advice_ar,
        }


# Pest database with conditions and controls
PEST_DATABASE = {
    PestType.APHIDS: {
        "name_en": "Aphids",
        "name_ar": "المن",
        "description_en": "Small sap-sucking insects that cause leaf curling and transmit viruses",
        "description_ar": "حشرات صغيرة ماصة للعصارة تسبب تجعد الأوراق ونقل الفيروسات",
        "favorable_temp_range": (15, 28),
        "favorable_humidity_min": 50,
        "favorable_humidity_max": 80,
        "ndvi_vulnerability_max": 0.65,  # Dense canopy favors aphids
        "damage_symptoms_en": [
            "Leaf curling",
            "Honeydew on leaves",
            "Stunted growth",
            "Sooty mold",
        ],
        "damage_symptoms_ar": ["تجعد الأوراق", "ندوة عسلية على الأوراق", "تقزم النمو", "عفن أسود"],
        "controls": [
            PestControl(
                method=ControlMethod.BIOLOGICAL,
                product_name="Ladybugs/Lacewings release",
                product_name_ar="إطلاق أبو العيد/أسد المن",
                dosage="5000-10000 per hectare",
                dosage_ar="5000-10000 لكل هكتار",
                timing="At first detection",
                timing_ar="عند أول اكتشاف",
                effectiveness="medium",
                safety_interval_days=0,
            ),
            PestControl(
                method=ControlMethod.CHEMICAL,
                product_name="Imidacloprid (Confidor)",
                product_name_ar="إيميداكلوبريد (كونفيدور)",
                dosage="0.3-0.5 L/ha",
                dosage_ar="0.3-0.5 لتر/هكتار",
                timing="When population exceeds threshold",
                timing_ar="عند تجاوز الكثافة للعتبة الاقتصادية",
                effectiveness="high",
                safety_interval_days=21,
            ),
        ],
        "monitoring_advice_en": "Check undersides of leaves weekly, especially young shoots",
        "monitoring_advice_ar": "افحص أسفل الأوراق أسبوعياً، خاصة النموات الحديثة",
    },
    PestType.WHITEFLY: {
        "name_en": "Whitefly",
        "name_ar": "الذبابة البيضاء",
        "description_en": "Small white flying insects that suck plant sap and transmit viruses",
        "description_ar": "حشرات بيضاء صغيرة طائرة تمتص عصارة النبات وتنقل الفيروسات",
        "favorable_temp_range": (25, 35),
        "favorable_humidity_min": 40,
        "favorable_humidity_max": 70,
        "ndvi_vulnerability_max": 0.70,
        "damage_symptoms_en": ["Yellowing leaves", "Honeydew", "Virus symptoms", "Leaf drop"],
        "damage_symptoms_ar": ["اصفرار الأوراق", "ندوة عسلية", "أعراض فيروسية", "سقوط أوراق"],
        "controls": [
            PestControl(
                method=ControlMethod.MECHANICAL,
                product_name="Yellow sticky traps",
                product_name_ar="مصائد لاصقة صفراء",
                dosage="20-40 traps/ha",
                dosage_ar="20-40 مصيدة/هكتار",
                timing="Preventive",
                timing_ar="وقائياً",
                effectiveness="medium",
                safety_interval_days=0,
            ),
            PestControl(
                method=ControlMethod.CHEMICAL,
                product_name="Pyriproxyfen (Admiral)",
                product_name_ar="بيريبروكسيفين (أدميرال)",
                dosage="0.5-0.75 L/ha",
                dosage_ar="0.5-0.75 لتر/هكتار",
                timing="At egg stage",
                timing_ar="في مرحلة البيض",
                effectiveness="high",
                safety_interval_days=14,
            ),
        ],
        "monitoring_advice_en": "Shake plants over white paper to detect adults",
        "monitoring_advice_ar": "هز النباتات فوق ورقة بيضاء لاكتشاف الحشرات البالغة",
    },
    PestType.LOCUST: {
        "name_en": "Desert Locust",
        "name_ar": "الجراد الصحراوي",
        "description_en": "Migratory pest that can devastate crops in swarms",
        "description_ar": "آفة مهاجرة يمكن أن تدمر المحاصيل في أسراب",
        "favorable_temp_range": (25, 40),
        "favorable_humidity_min": 30,
        "favorable_humidity_max": 60,
        "seasonal_peak": ["spring", "summer"],
        "damage_symptoms_en": ["Complete defoliation", "Stripped stems", "Destroyed crops"],
        "damage_symptoms_ar": ["إزالة كاملة للأوراق", "سيقان عارية", "محاصيل مدمرة"],
        "controls": [
            PestControl(
                method=ControlMethod.CHEMICAL,
                product_name="Malathion ULV",
                product_name_ar="مالاثيون ULV",
                dosage="1-1.5 L/ha aerial",
                dosage_ar="1-1.5 لتر/هكتار جوي",
                timing="At swarm detection",
                timing_ar="عند اكتشاف السرب",
                effectiveness="high",
                safety_interval_days=7,
            ),
            PestControl(
                method=ControlMethod.BIOLOGICAL,
                product_name="Metarhizium acridum",
                product_name_ar="ميتاريزيوم أكريدوم",
                dosage="50g/ha",
                dosage_ar="50 جم/هكتار",
                timing="Preventive in breeding areas",
                timing_ar="وقائياً في مناطق التكاثر",
                effectiveness="medium",
                safety_interval_days=0,
            ),
        ],
        "monitoring_advice_en": "Monitor FAO Desert Locust bulletins and local reports",
        "monitoring_advice_ar": "راقب نشرات الفاو للجراد الصحراوي والتقارير المحلية",
    },
    PestType.THRIPS: {
        "name_en": "Thrips",
        "name_ar": "التربس",
        "description_en": "Tiny insects that rasp and suck plant tissue, causing silvering",
        "description_ar": "حشرات دقيقة تكشط وتمتص أنسجة النبات مسببة فضية الأوراق",
        "favorable_temp_range": (20, 30),
        "favorable_humidity_min": 30,
        "favorable_humidity_max": 60,
        "damage_symptoms_en": ["Silvery streaks", "Distorted growth", "Flower damage"],
        "damage_symptoms_ar": ["خطوط فضية", "نمو مشوه", "تلف الأزهار"],
        "controls": [
            PestControl(
                method=ControlMethod.CHEMICAL,
                product_name="Spinosad (Success)",
                product_name_ar="سبينوساد (ساكسس)",
                dosage="200-400 ml/ha",
                dosage_ar="200-400 مل/هكتار",
                timing="At flower stage",
                timing_ar="في مرحلة الإزهار",
                effectiveness="high",
                safety_interval_days=3,
            ),
        ],
        "monitoring_advice_en": "Use blue sticky traps for monitoring",
        "monitoring_advice_ar": "استخدم مصائد لاصقة زرقاء للمراقبة",
    },
    PestType.FRUIT_FLY: {
        "name_en": "Fruit Fly",
        "name_ar": "ذبابة الفاكهة",
        "description_en": "Lays eggs in fruit causing maggot infestation",
        "description_ar": "تضع بيضها في الثمار مسببة إصابة باليرقات",
        "favorable_temp_range": (25, 35),
        "favorable_humidity_min": 60,
        "favorable_humidity_max": 90,
        "damage_symptoms_en": ["Fruit punctures", "Maggots in fruit", "Premature fruit drop"],
        "damage_symptoms_ar": ["ثقوب في الثمار", "يرقات في الثمار", "سقوط مبكر للثمار"],
        "controls": [
            PestControl(
                method=ControlMethod.MECHANICAL,
                product_name="Protein bait traps",
                product_name_ar="مصائد طعوم بروتينية",
                dosage="10-15 traps/ha",
                dosage_ar="10-15 مصيدة/هكتار",
                timing="Before fruit ripening",
                timing_ar="قبل نضج الثمار",
                effectiveness="medium",
                safety_interval_days=0,
            ),
            PestControl(
                method=ControlMethod.CHEMICAL,
                product_name="Bait spray (protein + insecticide)",
                product_name_ar="رش طعوم (بروتين + مبيد)",
                dosage="Spot application",
                dosage_ar="رش موضعي",
                timing="Weekly during fruiting",
                timing_ar="أسبوعياً خلال الإثمار",
                effectiveness="high",
                safety_interval_days=7,
            ),
        ],
        "monitoring_advice_en": "Install McPhail traps 6 weeks before harvest",
        "monitoring_advice_ar": "ركب مصائد ماكفيل قبل 6 أسابيع من الحصاد",
    },
    # ==========================================================================
    # آفات إضافية من مقالة الاستشعار الزراعي
    # Additional pests from Agricultural Sensing Article
    # ==========================================================================
    PestType.RED_PALM_WEEVIL: {
        "name_en": "Red Palm Weevil",
        "name_ar": "سوسة النخيل الحمراء",
        "description_en": "Lethal pest of date palms, requires 24-48h response",
        "description_ar": "آفة قاتلة للنخيل، تتطلب استجابة خلال 24-48 ساعة",
        "favorable_temp_range": (25, 38),
        "favorable_humidity_min": 50,
        "favorable_humidity_max": 90,
        "seasonal_peak": ["spring", "summer", "fall"],
        "damage_symptoms_en": [
            "Wilting of crown leaves",
            "Brown frass at trunk base",
            "Fermented odor",
            "Trunk collapse",
        ],
        "damage_symptoms_ar": [
            "ذبول أوراق التاج",
            "نشارة بنية عند قاعدة الجذع",
            "رائحة تخمر",
            "انهيار الجذع",
        ],
        "controls": [
            PestControl(
                method=ControlMethod.CHEMICAL,
                product_name="Emamectin benzoate 5% injection",
                product_name_ar="حقن إيمامكتين بنزوات 5%",
                dosage="50-100ml per injection point (4-6 points/tree)",
                dosage_ar="50-100 مل لكل نقطة حقن (4-6 نقاط/شجرة)",
                timing="At detection, within 24-48 hours",
                timing_ar="عند الاكتشاف، خلال 24-48 ساعة",
                effectiveness="high",
                safety_interval_days=30,
            ),
            PestControl(
                method=ControlMethod.MECHANICAL,
                product_name="Pheromone traps (aggregation pheromone)",
                product_name_ar="مصائد الفرمونات (فرمون التجميع)",
                dosage="5 traps per hectare",
                dosage_ar="5 مصائد لكل هكتار",
                timing="Preventive year-round",
                timing_ar="وقائي طوال العام",
                effectiveness="medium",
                safety_interval_days=0,
            ),
        ],
        "monitoring_advice_en": "Weekly visual inspection, check for frass and wilting. Report to Ministry immediately.",
        "monitoring_advice_ar": "فحص بصري أسبوعي، ابحث عن النشارة والذبول. أبلغ الوزارة فوراً.",
    },
    PestType.SPIDER_MITES: {
        "name_en": "Spider Mites (Two-spotted)",
        "name_ar": "العنكبوت الأحمر ذو البقعتين",
        "description_en": "Tiny mites that cause stippling and webbing on leaves",
        "description_ar": "أكاروسات دقيقة تسبب تنقيط الأوراق وظهور خيوط عنكبوتية",
        "favorable_temp_range": (25, 35),
        "favorable_humidity_min": 20,
        "favorable_humidity_max": 50,
        "damage_symptoms_en": ["Stippling on leaves", "Webbing", "Bronzing", "Leaf drop"],
        "damage_symptoms_ar": ["تنقيط الأوراق", "خيوط عنكبوتية", "تبرنز", "سقوط أوراق"],
        "controls": [
            PestControl(
                method=ControlMethod.BIOLOGICAL,
                product_name="Phytoseiulus persimilis",
                product_name_ar="فيتوسيولوس بيرسيميلس",
                dosage="2-5 per plant",
                dosage_ar="2-5 لكل نبات",
                timing="At first detection",
                timing_ar="عند أول اكتشاف",
                effectiveness="high",
                safety_interval_days=0,
            ),
            PestControl(
                method=ControlMethod.CHEMICAL,
                product_name="Abamectin (Vertimec)",
                product_name_ar="أبامكتين (فيرتيمك)",
                dosage="0.5-1 L/ha",
                dosage_ar="0.5-1 لتر/هكتار",
                timing="When population builds",
                timing_ar="عند ازدياد الأعداد",
                effectiveness="high",
                safety_interval_days=7,
            ),
        ],
        "monitoring_advice_en": "Check underside of leaves with hand lens, especially in hot dry periods",
        "monitoring_advice_ar": "افحص أسفل الأوراق بعدسة مكبرة، خاصة في الفترات الحارة الجافة",
    },
    PestType.TOMATO_LEAFMINER: {
        "name_en": "Tomato Leafminer (Tuta absoluta)",
        "name_ar": "توتا أبسلوتا (حافرة أوراق الطماطم)",
        "description_en": "Devastating pest of tomatoes, causes extensive leaf and fruit damage",
        "description_ar": "آفة مدمرة للطماطم، تسبب أضراراً كبيرة للأوراق والثمار",
        "favorable_temp_range": (20, 30),
        "favorable_humidity_min": 60,
        "favorable_humidity_max": 90,
        "seasonal_peak": ["spring", "summer"],
        "damage_symptoms_en": [
            "Blotch mines in leaves",
            "Holes in fruits",
            "Galleries in stems",
            "Frass in mines",
        ],
        "damage_symptoms_ar": [
            "أنفاق بقعية في الأوراق",
            "ثقوب في الثمار",
            "أنفاق في السيقان",
            "براز في الأنفاق",
        ],
        "controls": [
            PestControl(
                method=ControlMethod.MECHANICAL,
                product_name="Delta traps with pheromone",
                product_name_ar="مصائد دلتا مع فرمون",
                dosage="20-40 traps/ha",
                dosage_ar="20-40 مصيدة/هكتار",
                timing="From transplanting",
                timing_ar="من الشتل",
                effectiveness="medium",
                safety_interval_days=0,
            ),
            PestControl(
                method=ControlMethod.BIOLOGICAL,
                product_name="Bacillus thuringiensis (Bt)",
                product_name_ar="باسيلوس ثورينجينسيس",
                dosage="1-2 kg/ha",
                dosage_ar="1-2 كجم/هكتار",
                timing="At first detection",
                timing_ar="عند أول اكتشاف",
                effectiveness="medium",
                safety_interval_days=0,
            ),
        ],
        "monitoring_advice_en": "Check traps twice weekly, inspect leaves for mines",
        "monitoring_advice_ar": "افحص المصائد مرتين أسبوعياً، فتش الأوراق عن الأنفاق",
    },
    PestType.MEALYBUG: {
        "name_en": "Mealybug",
        "name_ar": "البق الدقيقي",
        "description_en": "Soft-bodied insects covered in white waxy coating",
        "description_ar": "حشرات رخوة مغطاة بطبقة شمعية بيضاء",
        "favorable_temp_range": (22, 32),
        "favorable_humidity_min": 50,
        "favorable_humidity_max": 80,
        "damage_symptoms_en": ["White cottony masses", "Honeydew", "Sooty mold", "Distorted growth"],
        "damage_symptoms_ar": ["كتل قطنية بيضاء", "ندوة عسلية", "عفن أسود", "نمو مشوه"],
        "controls": [
            PestControl(
                method=ControlMethod.BIOLOGICAL,
                product_name="Cryptolaemus montrouzieri",
                product_name_ar="كريبتوليموس مونتروزييري",
                dosage="5-10 per plant",
                dosage_ar="5-10 لكل نبات",
                timing="Early season",
                timing_ar="بداية الموسم",
                effectiveness="high",
                safety_interval_days=0,
            ),
        ],
        "monitoring_advice_en": "Check leaf axils and stem joints for cottony masses",
        "monitoring_advice_ar": "افحص آباط الأوراق ومفاصل السيقان للكتل القطنية",
    },
    PestType.DUBAS_BUG: {
        "name_en": "Dubas Bug (Date Palm Hopper)",
        "name_ar": "دوباس النخيل",
        "description_en": "Major pest of date palms in Middle East, causes honeydew and sooty mold",
        "description_ar": "آفة رئيسية للنخيل في الشرق الأوسط، تسبب الندوة العسلية والعفن الأسود",
        "favorable_temp_range": (25, 40),
        "favorable_humidity_min": 30,
        "favorable_humidity_max": 70,
        "seasonal_peak": ["spring", "fall"],
        "damage_symptoms_en": [
            "Honeydew on fronds",
            "Sooty mold",
            "Reduced photosynthesis",
            "Fruit quality decline",
        ],
        "damage_symptoms_ar": [
            "ندوة عسلية على السعف",
            "عفن أسود",
            "انخفاض التمثيل الضوئي",
            "تدهور جودة الثمار",
        ],
        "controls": [
            PestControl(
                method=ControlMethod.CHEMICAL,
                product_name="Diflubenzuron (Dimilin)",
                product_name_ar="ديفلوبنزورون (ديميلين)",
                dosage="0.5-1 L/ha",
                dosage_ar="0.5-1 لتر/هكتار",
                timing="At nymph emergence (spring/fall)",
                timing_ar="عند ظهور الحوريات (ربيع/خريف)",
                effectiveness="high",
                safety_interval_days=14,
            ),
        ],
        "monitoring_advice_en": "Monitor nymph populations on lower fronds in spring and fall",
        "monitoring_advice_ar": "راقب الحوريات على السعف السفلي في الربيع والخريف",
    },
}


def assess_pest_risks(
    temp_c: float,
    humidity_pct: float,
    ndvi: float,
    crop_type: str = "general",
    season: str = "summer",
    region: str = "yemen",
) -> list[PestRisk]:
    """
    تقييم مخاطر الآفات بناءً على الظروف البيئية
    Assess pest risks based on environmental conditions

    Args:
        temp_c: Current temperature (°C)
        humidity_pct: Relative humidity (%)
        ndvi: NDVI value for canopy assessment
        crop_type: Type of crop
        season: Current season (spring, summer, fall, winter)
        region: Geographic region

    Returns:
        List of pest risks sorted by risk level
    """
    risks = []

    for pest_type, pest_data in PEST_DATABASE.items():
        # Calculate base risk score
        risk_score = 0.0
        favorable_conditions = []
        favorable_conditions_ar = []

        # Temperature factor
        temp_range = pest_data.get("favorable_temp_range", (15, 35))
        if temp_range[0] <= temp_c <= temp_range[1]:
            temp_factor = 1.0 - abs(temp_c - (temp_range[0] + temp_range[1]) / 2) / (
                temp_range[1] - temp_range[0]
            )
            risk_score += 35 * temp_factor
            favorable_conditions.append(
                f"Temperature in favorable range ({temp_range[0]}-{temp_range[1]}°C)"
            )
            favorable_conditions_ar.append(
                f"الحرارة في النطاق الملائم ({temp_range[0]}-{temp_range[1]} °م)"
            )

        # Humidity factor
        humidity_min = pest_data.get("favorable_humidity_min", 40)
        humidity_max = pest_data.get("favorable_humidity_max", 80)
        if humidity_min <= humidity_pct <= humidity_max:
            humidity_factor = 1.0 - abs(humidity_pct - (humidity_min + humidity_max) / 2) / (
                humidity_max - humidity_min
            )
            risk_score += 25 * humidity_factor
            favorable_conditions.append(
                f"Humidity in favorable range ({humidity_min}-{humidity_max}%)"
            )
            favorable_conditions_ar.append(
                f"الرطوبة في النطاق الملائم ({humidity_min}-{humidity_max}%)"
            )

        # NDVI/canopy factor
        ndvi_max = pest_data.get("ndvi_vulnerability_max", 0.75)
        if ndvi >= ndvi_max - 0.15:
            ndvi_factor = min(1.0, (ndvi - (ndvi_max - 0.15)) / 0.15)
            risk_score += 20 * ndvi_factor
            favorable_conditions.append("Dense canopy providing favorable habitat")
            favorable_conditions_ar.append("مظلة كثيفة توفر بيئة ملائمة")

        # Seasonal factor
        seasonal_peak = pest_data.get("seasonal_peak", [])
        if season.lower() in seasonal_peak:
            risk_score += 20
            favorable_conditions.append(f"Peak season for this pest ({season})")
            favorable_conditions_ar.append(f"موسم الذروة لهذه الآفة ({season})")

        # Only include if risk score is meaningful
        if risk_score < 15:
            continue

        # Determine risk level
        if risk_score >= 75:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 55:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 35:
            risk_level = RiskLevel.MODERATE
        elif risk_score >= 20:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.VERY_LOW

        risks.append(
            PestRisk(
                pest_type=pest_type,
                risk_level=risk_level,
                risk_score=risk_score,
                name_en=pest_data["name_en"],
                name_ar=pest_data["name_ar"],
                description_en=pest_data["description_en"],
                description_ar=pest_data["description_ar"],
                favorable_conditions=favorable_conditions,
                favorable_conditions_ar=favorable_conditions_ar,
                damage_symptoms_en=pest_data["damage_symptoms_en"],
                damage_symptoms_ar=pest_data["damage_symptoms_ar"],
                controls=pest_data["controls"],
                monitoring_advice_en=pest_data["monitoring_advice_en"],
                monitoring_advice_ar=pest_data["monitoring_advice_ar"],
            )
        )

    # Sort by risk score (highest first)
    risks.sort(key=lambda r: r.risk_score, reverse=True)

    return risks


def get_pest_summary(risks: list[PestRisk]) -> dict[str, Any]:
    """
    ملخص تقييم مخاطر الآفات
    Get pest risk assessment summary

    Returns:
        Summary dictionary
    """
    if not risks:
        return {
            "overall_status_en": "Low Risk",
            "overall_status_ar": "مخاطر منخفضة",
            "total_pests_assessed": 0,
            "critical_risks": 0,
            "high_risks": 0,
            "action_required": False,
        }

    critical = sum(1 for r in risks if r.risk_level == RiskLevel.CRITICAL)
    high = sum(1 for r in risks if r.risk_level == RiskLevel.HIGH)
    moderate = sum(1 for r in risks if r.risk_level == RiskLevel.MODERATE)

    if critical > 0:
        status_en, status_ar = "Critical - Immediate Action Required", "حرج - إجراء فوري مطلوب"
    elif high > 0:
        status_en, status_ar = "High Risk - Monitor Closely", "مخاطر عالية - راقب عن كثب"
    elif moderate > 0:
        status_en, status_ar = "Moderate Risk - Regular Monitoring", "مخاطر متوسطة - مراقبة منتظمة"
    else:
        status_en, status_ar = "Low Risk - Routine Checks", "مخاطر منخفضة - فحوصات روتينية"

    return {
        "overall_status_en": status_en,
        "overall_status_ar": status_ar,
        "total_pests_assessed": len(risks),
        "critical_risks": critical,
        "high_risks": high,
        "moderate_risks": moderate,
        "action_required": critical > 0 or high > 0,
    }


def get_pest_types() -> list[dict[str, str]]:
    """Get list of all pest types"""
    return [
        {
            "value": pt.value,
            "name_en": PEST_DATABASE.get(pt, {}).get("name_en", pt.value),
            "name_ar": PEST_DATABASE.get(pt, {}).get("name_ar", pt.value),
        }
        for pt in PestType
        if pt in PEST_DATABASE
    ]
