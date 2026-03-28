"""
Weather Alert Generation Module
===============================
وحدة توليد تنبيهات الطقس

Generates weather alerts for agricultural operations based on forecast data.
Includes frost, heat, wind, hail, and other severe weather warnings with
bilingual Arabic/English support.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .models import (
    CROP_FROST_THRESHOLDS,
    CROP_HEAT_THRESHOLDS,
    AlertSeverity,
    AlertThresholds,
    AlertType,
    CropType,
    HarvestCondition,
    HarvestWindow,
    IrrigationRecommendation,
    IrrigationSchedule,
    WeatherAlert,
    WeatherForecast,
)

# Bilingual alert templates
ALERT_TEMPLATES: dict[AlertType, dict[str, dict[str, str]]] = {
    AlertType.FROST: {
        "critical": {
            "title": "CRITICAL: Severe Frost Warning",
            "title_ar": "حرج: تحذير صقيع شديد",
            "description": "Temperatures expected to drop to {temp}C. Severe frost damage likely.",
            "description_ar": "من المتوقع أن تنخفض درجات الحرارة إلى {temp} درجة مئوية. أضرار صقيع شديدة متوقعة.",
            "impact": "Crop tissue damage, potential total crop loss for sensitive crops",
            "impact_ar": "تلف أنسجة المحصول، احتمال فقدان كامل للمحاصيل الحساسة",
        },
        "warning": {
            "title": "WARNING: Frost Expected",
            "title_ar": "تحذير: صقيع متوقع",
            "description": "Temperatures expected to drop to {temp}C. Frost damage possible.",
            "description_ar": "من المتوقع أن تنخفض درجات الحرارة إلى {temp} درجة مئوية. أضرار الصقيع محتملة.",
            "impact": "Leaf damage, reduced growth, potential yield loss",
            "impact_ar": "تلف الأوراق، انخفاض النمو، فقدان محتمل في الإنتاجية",
        },
        "advisory": {
            "title": "ADVISORY: Near-Frost Conditions",
            "title_ar": "استشارة: ظروف قريبة من الصقيع",
            "description": "Temperatures may drop to {temp}C. Monitor sensitive crops.",
            "description_ar": "قد تنخفض درجات الحرارة إلى {temp} درجة مئوية. راقب المحاصيل الحساسة.",
            "impact": "Possible stress to sensitive crops, slow growth",
            "impact_ar": "إجهاد محتمل للمحاصيل الحساسة، بطء في النمو",
        },
    },
    AlertType.HEAT: {
        "critical": {
            "title": "CRITICAL: Extreme Heat Warning",
            "title_ar": "حرج: تحذير حرارة شديدة",
            "description": "Temperatures expected to reach {temp}C. Extreme heat stress likely.",
            "description_ar": "من المتوقع أن تصل درجات الحرارة إلى {temp} درجة مئوية. إجهاد حراري شديد متوقع.",
            "impact": "Severe heat stress, pollination failure, crop damage",
            "impact_ar": "إجهاد حراري شديد، فشل التلقيح، تلف المحصول",
        },
        "warning": {
            "title": "WARNING: High Heat Expected",
            "title_ar": "تحذير: حرارة مرتفعة متوقعة",
            "description": "Temperatures expected to reach {temp}C. Heat stress possible.",
            "description_ar": "من المتوقع أن تصل درجات الحرارة إلى {temp} درجة مئوية. إجهاد حراري محتمل.",
            "impact": "Increased water demand, possible heat stress",
            "impact_ar": "زيادة الطلب على المياه، إجهاد حراري محتمل",
        },
        "advisory": {
            "title": "ADVISORY: Elevated Heat",
            "title_ar": "استشارة: حرارة مرتفعة",
            "description": "Temperatures may reach {temp}C. Consider additional irrigation.",
            "description_ar": "قد تصل درجات الحرارة إلى {temp} درجة مئوية. فكر في ري إضافي.",
            "impact": "Moderate heat stress, increased evapotranspiration",
            "impact_ar": "إجهاد حراري معتدل، زيادة التبخر والنتح",
        },
    },
    AlertType.WIND: {
        "critical": {
            "title": "CRITICAL: Damaging Wind Warning",
            "title_ar": "حرج: تحذير رياح مدمرة",
            "description": "Wind speeds expected to reach {speed} km/h. Structural damage possible.",
            "description_ar": "من المتوقع أن تصل سرعة الرياح إلى {speed} كم/ساعة. أضرار هيكلية محتملة.",
            "impact": "Crop lodging, greenhouse damage, irrigation system damage",
            "impact_ar": "رقاد المحاصيل، أضرار بالبيوت المحمية، تلف أنظمة الري",
        },
        "warning": {
            "title": "WARNING: Strong Wind Expected",
            "title_ar": "تحذير: رياح قوية متوقعة",
            "description": "Wind speeds expected to reach {speed} km/h. Spray operations suspended.",
            "description_ar": "من المتوقع أن تصل سرعة الرياح إلى {speed} كم/ساعة. تعليق عمليات الرش.",
            "impact": "Spray drift risk, mechanical damage to tall crops",
            "impact_ar": "خطر انجراف الرش، أضرار ميكانيكية للمحاصيل الطويلة",
        },
        "advisory": {
            "title": "ADVISORY: Moderate Wind",
            "title_ar": "استشارة: رياح معتدلة",
            "description": "Wind speeds may reach {speed} km/h. Adjust spray operations.",
            "description_ar": "قد تصل سرعة الرياح إلى {speed} كم/ساعة. اضبط عمليات الرش.",
            "impact": "Possible spray drift, plan operations carefully",
            "impact_ar": "انجراف رش محتمل، خطط للعمليات بعناية",
        },
    },
    AlertType.HAIL: {
        "critical": {
            "title": "CRITICAL: Large Hail Warning",
            "title_ar": "حرج: تحذير برد كبير",
            "description": "Large hail (>2cm) expected. Severe crop damage likely.",
            "description_ar": "برد كبير (أكبر من 2 سم) متوقع. أضرار شديدة للمحاصيل متوقعة.",
            "impact": "Severe physical damage, total fruit/vegetable loss possible",
            "impact_ar": "أضرار جسدية شديدة، فقدان كامل محتمل للفواكه/الخضروات",
        },
        "warning": {
            "title": "WARNING: Hail Expected",
            "title_ar": "تحذير: برد متوقع",
            "description": "Hail expected in the area. Protect sensitive crops.",
            "description_ar": "برد متوقع في المنطقة. احمِ المحاصيل الحساسة.",
            "impact": "Physical damage to leaves and fruit, reduced quality",
            "impact_ar": "أضرار جسدية للأوراق والثمار، انخفاض الجودة",
        },
    },
    AlertType.RAIN: {
        "critical": {
            "title": "CRITICAL: Heavy Rain Warning",
            "title_ar": "حرج: تحذير أمطار غزيرة",
            "description": "Heavy rainfall ({amount} mm) expected. Flash flooding possible.",
            "description_ar": "أمطار غزيرة ({amount} مم) متوقعة. فيضانات مفاجئة محتملة.",
            "impact": "Waterlogging, root damage, disease outbreak risk",
            "impact_ar": "تشبع التربة بالماء، تلف الجذور، خطر تفشي الأمراض",
        },
        "warning": {
            "title": "WARNING: Significant Rain Expected",
            "title_ar": "تحذير: أمطار كبيرة متوقعة",
            "description": "Significant rainfall ({amount} mm) expected. Adjust irrigation.",
            "description_ar": "أمطار كبيرة ({amount} مم) متوقعة. اضبط الري.",
            "impact": "Skip irrigation, disease risk increases",
            "impact_ar": "تخطي الري، زيادة خطر الأمراض",
        },
    },
    AlertType.SANDSTORM: {
        "critical": {
            "title": "CRITICAL: Severe Sandstorm Warning",
            "title_ar": "حرج: تحذير عاصفة رملية شديدة",
            "description": "Severe sandstorm expected. Visibility will be severely reduced.",
            "description_ar": "عاصفة رملية شديدة متوقعة. ستنخفض الرؤية بشكل كبير.",
            "impact": "Leaf damage from abrasion, blocked stomata, equipment damage",
            "impact_ar": "تلف الأوراق من الاحتكاك، انسداد الثغور، تلف المعدات",
        },
        "warning": {
            "title": "WARNING: Sandstorm Expected",
            "title_ar": "تحذير: عاصفة رملية متوقعة",
            "description": "Sandstorm conditions expected. Protect equipment and crops.",
            "description_ar": "ظروف عاصفة رملية متوقعة. احمِ المعدات والمحاصيل.",
            "impact": "Reduced photosynthesis, mechanical leaf damage",
            "impact_ar": "انخفاض التمثيل الضوئي، أضرار ميكانيكية للأوراق",
        },
    },
    AlertType.HUMIDITY: {
        "warning": {
            "title": "WARNING: High Humidity Alert",
            "title_ar": "تحذير: تنبيه رطوبة عالية",
            "description": "Humidity expected to reach {humidity}%. Disease risk elevated.",
            "description_ar": "من المتوقع أن تصل الرطوبة إلى {humidity}%. خطر الأمراض مرتفع.",
            "impact": "Fungal disease risk, poor spray drying, quality issues",
            "impact_ar": "خطر الأمراض الفطرية، جفاف الرش ضعيف، مشاكل جودة",
        },
        "advisory": {
            "title": "ADVISORY: Low Humidity",
            "title_ar": "استشارة: رطوبة منخفضة",
            "description": "Humidity may drop to {humidity}%. Plant stress possible.",
            "description_ar": "قد تنخفض الرطوبة إلى {humidity}%. إجهاد النبات محتمل.",
            "impact": "Increased water demand, spray evaporation risk",
            "impact_ar": "زيادة الطلب على المياه، خطر تبخر الرش",
        },
    },
    AlertType.INVERSION: {
        "warning": {
            "title": "WARNING: Temperature Inversion Alert",
            "title_ar": "تحذير: تنبيه انقلاب حراري",
            "description": "Temperature inversion expected from {start}:00 to {end}:00. Spray drift risk high.",
            "description_ar": "انقلاب حراري متوقع من الساعة {start}:00 إلى {end}:00. خطر انجراف الرش مرتفع.",
            "impact": "Spray particles remain suspended, off-target drift likely",
            "impact_ar": "جزيئات الرش تبقى معلقة، انجراف خارج الهدف محتمل",
        },
    },
    AlertType.UV: {
        "warning": {
            "title": "WARNING: Extreme UV Alert",
            "title_ar": "تحذير: تنبيه أشعة فوق بنفسجية شديدة",
            "description": "UV index expected to reach {uv}. Worker protection required.",
            "description_ar": "من المتوقع أن يصل مؤشر الأشعة فوق البنفسجية إلى {uv}. حماية العمال مطلوبة.",
            "impact": "Sunburn risk to workers, accelerated crop stress",
            "impact_ar": "خطر حروق الشمس للعمال، تسارع إجهاد المحصول",
        },
    },
    AlertType.DROUGHT: {
        "critical": {
            "title": "Severe Drought Conditions",
            "title_ar": "ظروف جفاف شديدة",
            "description": "Prolonged dry period with no rainfall expected. Soil moisture critically low.",
            "description_ar": "فترة جفاف مطولة بدون أمطار متوقعة. رطوبة التربة منخفضة بشكل حرج.",
            "impact": "Severe crop water stress, potential crop failure",
            "impact_ar": "إجهاد مائي شديد للمحاصيل، احتمال فشل المحصول",
        },
        "warning": {
            "title": "Drought Warning",
            "title_ar": "تحذير جفاف",
            "description": "Extended dry conditions detected. Monitor soil moisture and increase irrigation.",
            "description_ar": "ظروف جفاف ممتدة. راقب رطوبة التربة وزد الري.",
            "impact": "Increased water demand, crop stress likely",
            "impact_ar": "زيادة الطلب على المياه، إجهاد المحاصيل محتمل",
        },
    },
}

# Recommended actions by alert type
ALERT_ACTIONS: dict[AlertType, dict[str, tuple[list[str], list[str]]]] = {
    AlertType.FROST: {
        "critical": (
            [
                "Activate frost protection systems immediately",
                "Apply overhead irrigation if available (ice protection)",
                "Cover sensitive crops with frost cloth",
                "Harvest mature crops if possible",
                "Delay planting of new crops",
            ],
            [
                "شغّل أنظمة الحماية من الصقيع فوراً",
                "طبق الري العلوي إذا كان متاحاً (حماية بالجليد)",
                "غطِّ المحاصيل الحساسة بقماش الصقيع",
                "احصد المحاصيل الناضجة إن أمكن",
                "أجّل زراعة المحاصيل الجديدة",
            ],
        ),
        "warning": (
            [
                "Prepare frost protection measures",
                "Monitor temperatures closely overnight",
                "Delay irrigation to allow soil warming",
                "Inspect crops at first light for damage",
            ],
            [
                "جهّز تدابير الحماية من الصقيع",
                "راقب درجات الحرارة عن كثب ليلاً",
                "أجّل الري للسماح بتدفئة التربة",
                "افحص المحاصيل عند أول ضوء للتحقق من الأضرار",
            ],
        ),
        "advisory": (
            [
                "Monitor weather updates closely",
                "Have frost protection materials ready",
                "Check cold-sensitive crops",
            ],
            [
                "راقب تحديثات الطقس عن كثب",
                "جهّز مواد الحماية من الصقيع",
                "افحص المحاصيل الحساسة للبرد",
            ],
        ),
    },
    AlertType.HEAT: {
        "critical": (
            [
                "Increase irrigation frequency immediately",
                "Apply light irrigation during hottest hours if possible",
                "Provide shade for sensitive crops",
                "Avoid any field work during peak heat (11am-4pm)",
                "Ensure worker hydration and rest breaks",
            ],
            [
                "زِد تكرار الري فوراً",
                "طبق رياً خفيفاً خلال ساعات الذروة إن أمكن",
                "وفر الظل للمحاصيل الحساسة",
                "تجنب أي عمل ميداني خلال ذروة الحرارة (11ص-4م)",
                "تأكد من ترطيب العمال وفترات الراحة",
            ],
        ),
        "warning": (
            [
                "Adjust irrigation schedule - increase amounts",
                "Monitor soil moisture more frequently",
                "Apply mulch to conserve moisture",
                "Schedule field work for early morning or evening",
            ],
            [
                "اضبط جدول الري - زد الكميات",
                "راقب رطوبة التربة بشكل أكثر تكراراً",
                "طبق التغطية للحفاظ على الرطوبة",
                "جدول العمل الميداني للصباح الباكر أو المساء",
            ],
        ),
        "advisory": (
            [
                "Check irrigation system efficiency",
                "Monitor crops for heat stress symptoms",
                "Plan irrigation adjustments if heat continues",
            ],
            [
                "تحقق من كفاءة نظام الري",
                "راقب المحاصيل لأعراض الإجهاد الحراري",
                "خطط لتعديلات الري إذا استمرت الحرارة",
            ],
        ),
    },
    AlertType.WIND: {
        "critical": (
            [
                "Suspend all spray operations",
                "Secure all equipment and structures",
                "Protect greenhouses - close vents",
                "Stay indoors during peak wind",
                "Inspect for damage after wind subsides",
            ],
            [
                "أوقف جميع عمليات الرش",
                "ثبّت جميع المعدات والهياكل",
                "احمِ البيوت المحمية - أغلق الفتحات",
                "ابقَ في الداخل أثناء ذروة الرياح",
                "افحص الأضرار بعد هدوء الرياح",
            ],
        ),
        "warning": (
            [
                "Stop spray operations immediately",
                "Check and secure loose items",
                "Support tall/weak plants if possible",
                "Delay harvest if wind-sensitive crop",
            ],
            [
                "أوقف عمليات الرش فوراً",
                "تحقق من وثبّت العناصر غير المثبتة",
                "ادعم النباتات الطويلة/الضعيفة إن أمكن",
                "أجّل الحصاد إذا كان المحصول حساساً للرياح",
            ],
        ),
        "advisory": (
            [
                "Adjust spray nozzle pressure (lower)",
                "Use drift-reducing nozzles",
                "Spray early morning when wind is calmer",
                "Monitor wind speed before operations",
            ],
            [
                "اضبط ضغط فوهة الرش (أخفض)",
                "استخدم فوهات تقليل الانجراف",
                "رش في الصباح الباكر عندما تكون الرياح أهدأ",
                "راقب سرعة الرياح قبل العمليات",
            ],
        ),
    },
    AlertType.HAIL: {
        "critical": (
            [
                "Deploy hail nets if available",
                "Move portable equipment under cover",
                "Harvest any mature crops immediately",
                "Document damage for insurance claims",
                "Plan recovery treatment (fungicide for wounds)",
            ],
            [
                "انشر شبكات البرد إذا كانت متاحة",
                "انقل المعدات المحمولة تحت غطاء",
                "احصد أي محاصيل ناضجة فوراً",
                "وثّق الأضرار لمطالبات التأمين",
                "خطط لعلاج التعافي (مبيد فطري للجروح)",
            ],
        ),
        "warning": (
            [
                "Prepare hail protection if available",
                "Consider emergency harvest",
                "Have fungicide ready for post-hail treatment",
                "Document crop condition before hail",
            ],
            [
                "جهّز حماية البرد إذا كانت متاحة",
                "فكر في الحصاد الطارئ",
                "جهّز مبيد فطري لعلاج ما بعد البرد",
                "وثّق حالة المحصول قبل البرد",
            ],
        ),
    },
    AlertType.RAIN: {
        "critical": (
            [
                "Ensure drainage systems are clear",
                "Protect harvested crops from moisture",
                "Suspend all field operations",
                "Plan fungicide application after rain",
                "Check for waterlogging after storm",
            ],
            [
                "تأكد من خلو أنظمة الصرف",
                "احمِ المحاصيل المحصودة من الرطوبة",
                "أوقف جميع العمليات الميدانية",
                "خطط لتطبيق مبيد فطري بعد المطر",
                "تحقق من التشبع بالماء بعد العاصفة",
            ],
        ),
        "warning": (
            [
                "Skip scheduled irrigation",
                "Delay any spray applications",
                "Ensure field drainage is working",
                "Adjust irrigation plan for coming days",
            ],
            [
                "تخطَّ الري المجدول",
                "أجّل أي تطبيقات رش",
                "تأكد من عمل صرف الحقل",
                "اضبط خطة الري للأيام القادمة",
            ],
        ),
    },
    AlertType.SANDSTORM: {
        "critical": (
            [
                "Secure all equipment and covers",
                "Close greenhouse vents and doors",
                "Suspend all outdoor operations",
                "Protect irrigation emitters from clogging",
                "Plan leaf washing after storm clears",
            ],
            [
                "ثبّت جميع المعدات والأغطية",
                "أغلق فتحات وأبواب البيوت المحمية",
                "أوقف جميع العمليات الخارجية",
                "احمِ منقطات الري من الانسداد",
                "خطط لغسل الأوراق بعد انقشاع العاصفة",
            ],
        ),
        "warning": (
            [
                "Protect sensitive equipment",
                "Have irrigation filters ready for cleaning",
                "Plan post-storm cleanup",
                "Check air filters on machinery",
            ],
            [
                "احمِ المعدات الحساسة",
                "جهّز مرشحات الري للتنظيف",
                "خطط للتنظيف بعد العاصفة",
                "تحقق من مرشحات الهواء في الآلات",
            ],
        ),
    },
    AlertType.HUMIDITY: {
        "warning": (
            [
                "Scout for fungal disease symptoms",
                "Increase plant spacing if possible",
                "Improve air circulation in greenhouses",
                "Delay spray applications (slow drying)",
                "Plan preventive fungicide application",
            ],
            [
                "ابحث عن أعراض الأمراض الفطرية",
                "زِد المسافة بين النباتات إن أمكن",
                "حسّن دورة الهواء في البيوت المحمية",
                "أجّل تطبيقات الرش (جفاف بطيء)",
                "خطط لتطبيق مبيد فطري وقائي",
            ],
        ),
        "advisory": (
            [
                "Increase irrigation to compensate for evaporation",
                "Monitor crops for stress symptoms",
                "Use adjuvants to reduce spray evaporation",
            ],
            [
                "زِد الري للتعويض عن التبخر",
                "راقب المحاصيل لأعراض الإجهاد",
                "استخدم المواد المساعدة لتقليل تبخر الرش",
            ],
        ),
    },
    AlertType.INVERSION: {
        "warning": (
            [
                "DO NOT spray during inversion period",
                "Wait for air mixing (wind >5 km/h)",
                "Monitor for smoke/dust hanging in air",
                "Resume spraying after inversion breaks",
            ],
            [
                "لا ترش أثناء فترة الانقلاب الحراري",
                "انتظر اختلاط الهواء (رياح أكثر من 5 كم/ساعة)",
                "راقب الدخان/الغبار المعلق في الهواء",
                "استأنف الرش بعد انتهاء الانقلاب",
            ],
        ),
    },
    AlertType.UV: {
        "warning": (
            [
                "Schedule outdoor work before 10am or after 4pm",
                "Ensure workers wear protective clothing and sunscreen",
                "Provide adequate shade and water for workers",
                "Limit continuous outdoor exposure",
            ],
            [
                "جدول العمل الخارجي قبل 10ص أو بعد 4م",
                "تأكد من ارتداء العمال ملابس واقية وكريم الشمس",
                "وفر الظل الكافي والماء للعمال",
                "حدّ من التعرض الخارجي المستمر",
            ],
        ),
    },
    AlertType.DROUGHT: {
        "critical": (
            [
                "Switch to deficit irrigation strategy immediately",
                "Apply mulch to conserve soil moisture",
                "Prioritize water for high-value crops",
                "Consider emergency water sourcing",
            ],
            [
                "انتقل لاستراتيجية الري العجزي فوراً",
                "ضع تغطية عضوية للحفاظ على رطوبة التربة",
                "أعطِ أولوية المياه للمحاصيل عالية القيمة",
                "فكّر في مصادر مياه طوارئ",
            ],
        ),
        "warning": (
            [
                "Increase irrigation frequency",
                "Monitor soil moisture sensors closely",
                "Apply organic mulch around crop bases",
            ],
            [
                "زد تكرار الري",
                "راقب مستشعرات رطوبة التربة عن كثب",
                "ضع تغطية عضوية حول قواعد المحاصيل",
            ],
        ),
    },
}


@dataclass
class AlertGeneratorConfig:
    """Configuration for alert generator"""

    thresholds: AlertThresholds = None
    default_crop: CropType = CropType.GENERAL
    timezone_offset_hours: int = 3  # Default to AST (Arabia Standard Time)
    enable_crop_specific_thresholds: bool = True
    enable_inversion_detection: bool = True

    def __post_init__(self):
        if self.thresholds is None:
            self.thresholds = AlertThresholds()


class WeatherAlertGenerator:
    """
    Weather Alert Generator
    مولد تنبيهات الطقس

    Generates weather alerts from forecast data with support for:
    - Multiple alert types (frost, heat, wind, hail, etc.)
    - Crop-specific thresholds
    - Temperature inversion detection
    - Bilingual alerts (Arabic/English)

    Usage:
        generator = WeatherAlertGenerator()

        # From forecast
        alerts = generator.generate_alerts(
            forecasts=[forecast1, forecast2],
            crop_type=CropType.WHEAT,
            field_id="FIELD-001"
        )

        for alert in alerts:
            print(f"{alert.get_priority_icon()} {alert.title}")
            print(f"   {alert.title_ar}")
    """

    def __init__(self, config: AlertGeneratorConfig | None = None):
        """Initialize the alert generator"""
        self.config = config or AlertGeneratorConfig()
        self.thresholds = self.config.thresholds

    def generate_alerts(
        self,
        forecasts: list[WeatherForecast],
        crop_type: CropType | None = None,
        field_id: str | None = None,
        farm_id: str | None = None,
        location_name: str = "",
        location_name_ar: str = "",
    ) -> list[WeatherAlert]:
        """
        Generate all relevant alerts from forecast data

        Args:
            forecasts: List of weather forecasts
            crop_type: Crop type for crop-specific thresholds
            field_id: Field identifier
            farm_id: Farm identifier
            location_name: Location name (English)
            location_name_ar: Location name (Arabic)

        Returns:
            List of generated alerts sorted by severity
        """
        crop_type = crop_type or self.config.default_crop
        alerts: list[WeatherAlert] = []

        for i, forecast in enumerate(forecasts):
            # Frost alerts
            frost_alert = self._check_frost(forecast, crop_type)
            if frost_alert:
                frost_alert.field_id = field_id
                frost_alert.farm_id = farm_id
                frost_alert.location_name = location_name
                frost_alert.location_name_ar = location_name_ar
                alerts.append(frost_alert)

            # Heat alerts
            heat_alert = self._check_heat(forecast, crop_type)
            if heat_alert:
                heat_alert.field_id = field_id
                heat_alert.farm_id = farm_id
                heat_alert.location_name = location_name
                heat_alert.location_name_ar = location_name_ar
                alerts.append(heat_alert)

            # Wind alerts
            wind_alert = self._check_wind(forecast)
            if wind_alert:
                wind_alert.field_id = field_id
                wind_alert.farm_id = farm_id
                wind_alert.location_name = location_name
                wind_alert.location_name_ar = location_name_ar
                alerts.append(wind_alert)

            # Rain alerts
            rain_alert = self._check_rain(forecast)
            if rain_alert:
                rain_alert.field_id = field_id
                rain_alert.farm_id = farm_id
                rain_alert.location_name = location_name
                rain_alert.location_name_ar = location_name_ar
                alerts.append(rain_alert)

            # Humidity alerts
            humidity_alert = self._check_humidity(forecast)
            if humidity_alert:
                humidity_alert.field_id = field_id
                humidity_alert.farm_id = farm_id
                humidity_alert.location_name = location_name
                humidity_alert.location_name_ar = location_name_ar
                alerts.append(humidity_alert)

            # Temperature inversion alerts
            if self.config.enable_inversion_detection:
                inversion_alert = self._check_inversion(forecast)
                if inversion_alert:
                    inversion_alert.field_id = field_id
                    inversion_alert.farm_id = farm_id
                    inversion_alert.location_name = location_name
                    inversion_alert.location_name_ar = location_name_ar
                    alerts.append(inversion_alert)

            # UV alerts
            uv_alert = self._check_uv(forecast)
            if uv_alert:
                uv_alert.field_id = field_id
                uv_alert.farm_id = farm_id
                uv_alert.location_name = location_name
                uv_alert.location_name_ar = location_name_ar
                alerts.append(uv_alert)

            # Sandstorm alerts
            sandstorm_alert = self._check_sandstorm(forecast)
            if sandstorm_alert:
                sandstorm_alert.field_id = field_id
                sandstorm_alert.farm_id = farm_id
                sandstorm_alert.location_name = location_name
                sandstorm_alert.location_name_ar = location_name_ar
                alerts.append(sandstorm_alert)

            # Hail alerts
            hail_alert = self._check_hail(forecast)
            if hail_alert:
                hail_alert.field_id = field_id
                hail_alert.farm_id = farm_id
                hail_alert.location_name = location_name
                hail_alert.location_name_ar = location_name_ar
                alerts.append(hail_alert)

            # Drought alerts (multi-day analysis)
            drought_alert = self._check_drought(forecasts, i)
            # Only emit drought alert once (at the first day of the dry window)
            if drought_alert and not any(a.alert_type == AlertType.DROUGHT for a in alerts):
                drought_alert.field_id = field_id
                drought_alert.farm_id = farm_id
                drought_alert.location_name = location_name
                drought_alert.location_name_ar = location_name_ar
                alerts.append(drought_alert)

        # Sort by severity (critical first)
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.WARNING: 1,
            AlertSeverity.ADVISORY: 2,
            AlertSeverity.WATCH: 3,
            AlertSeverity.INFORMATION: 4,
        }
        alerts.sort(key=lambda a: severity_order.get(a.severity, 5))

        return alerts

    def _check_frost(
        self,
        forecast: WeatherForecast,
        crop_type: CropType,
    ) -> WeatherAlert | None:
        """Check for frost conditions"""
        temp = forecast.temperature_min

        # Get crop-specific thresholds
        if self.config.enable_crop_specific_thresholds:
            thresholds = CROP_FROST_THRESHOLDS.get(crop_type, CROP_FROST_THRESHOLDS[CropType.GENERAL])
        else:
            thresholds = {
                "critical": self.thresholds.frost_critical,
                "warning": self.thresholds.frost_warning,
                "advisory": self.thresholds.frost_advisory,
            }

        # Determine severity
        if temp <= thresholds["critical"]:
            severity = AlertSeverity.CRITICAL
            level = "critical"
        elif temp <= thresholds["warning"]:
            severity = AlertSeverity.WARNING
            level = "warning"
        elif temp <= thresholds["advisory"]:
            severity = AlertSeverity.ADVISORY
            level = "advisory"
        else:
            return None

        template = ALERT_TEMPLATES[AlertType.FROST].get(level)
        if not template:
            return None

        actions_en, actions_ar = ALERT_ACTIONS[AlertType.FROST].get(level, ([], []))

        return WeatherAlert(
            alert_type=AlertType.FROST,
            severity=severity,
            valid_from=datetime.combine(forecast.forecast_date, datetime.min.time()),
            valid_until=datetime.combine(forecast.forecast_date, datetime.min.time()) + timedelta(hours=24),
            title=template["title"],
            description=template["description"].format(temp=temp),
            impact=template["impact"],
            recommended_actions=list(actions_en),
            title_ar=template["title_ar"],
            description_ar=template["description_ar"].format(temp=temp),
            impact_ar=template["impact_ar"],
            recommended_actions_ar=list(actions_ar),
            trigger_value=temp,
            threshold_value=thresholds[level],
            trigger_unit="C",
            affected_crops=[crop_type.value],
            crop_damage_risk="severe" if severity == AlertSeverity.CRITICAL else "high",
            crop_damage_risk_ar="شديد" if severity == AlertSeverity.CRITICAL else "مرتفع",
            confidence=forecast.confidence,
        )

    def _check_heat(
        self,
        forecast: WeatherForecast,
        crop_type: CropType,
    ) -> WeatherAlert | None:
        """Check for heat conditions"""
        temp = forecast.temperature_max

        # Get crop-specific thresholds
        if self.config.enable_crop_specific_thresholds:
            thresholds = CROP_HEAT_THRESHOLDS.get(crop_type, CROP_HEAT_THRESHOLDS[CropType.GENERAL])
        else:
            thresholds = {
                "critical": self.thresholds.heat_critical,
                "warning": self.thresholds.heat_warning,
                "advisory": self.thresholds.heat_advisory,
            }

        # Determine severity
        if temp >= thresholds["critical"]:
            severity = AlertSeverity.CRITICAL
            level = "critical"
        elif temp >= thresholds["warning"]:
            severity = AlertSeverity.WARNING
            level = "warning"
        elif temp >= thresholds["advisory"]:
            severity = AlertSeverity.ADVISORY
            level = "advisory"
        else:
            return None

        template = ALERT_TEMPLATES[AlertType.HEAT].get(level)
        if not template:
            return None

        actions_en, actions_ar = ALERT_ACTIONS[AlertType.HEAT].get(level, ([], []))

        return WeatherAlert(
            alert_type=AlertType.HEAT,
            severity=severity,
            valid_from=datetime.combine(forecast.forecast_date, datetime.min.time()),
            valid_until=datetime.combine(forecast.forecast_date, datetime.min.time()) + timedelta(hours=24),
            title=template["title"],
            description=template["description"].format(temp=temp),
            impact=template["impact"],
            recommended_actions=list(actions_en),
            title_ar=template["title_ar"],
            description_ar=template["description_ar"].format(temp=temp),
            impact_ar=template["impact_ar"],
            recommended_actions_ar=list(actions_ar),
            trigger_value=temp,
            threshold_value=thresholds[level],
            trigger_unit="C",
            affected_crops=[crop_type.value],
            crop_damage_risk="severe" if severity == AlertSeverity.CRITICAL else "high",
            crop_damage_risk_ar="شديد" if severity == AlertSeverity.CRITICAL else "مرتفع",
            confidence=forecast.confidence,
        )

    def _check_wind(self, forecast: WeatherForecast) -> WeatherAlert | None:
        """Check for wind conditions"""
        wind = forecast.wind_gust or forecast.wind_speed

        if wind >= self.thresholds.wind_critical:
            severity = AlertSeverity.CRITICAL
            level = "critical"
        elif wind >= self.thresholds.wind_warning:
            severity = AlertSeverity.WARNING
            level = "warning"
        elif wind >= self.thresholds.wind_advisory:
            severity = AlertSeverity.ADVISORY
            level = "advisory"
        else:
            return None

        template = ALERT_TEMPLATES[AlertType.WIND].get(level)
        if not template:
            return None

        actions_en, actions_ar = ALERT_ACTIONS[AlertType.WIND].get(level, ([], []))

        return WeatherAlert(
            alert_type=AlertType.WIND,
            severity=severity,
            valid_from=datetime.combine(forecast.forecast_date, datetime.min.time()),
            valid_until=datetime.combine(forecast.forecast_date, datetime.min.time()) + timedelta(hours=24),
            title=template["title"],
            description=template["description"].format(speed=wind),
            impact=template["impact"],
            recommended_actions=list(actions_en),
            title_ar=template["title_ar"],
            description_ar=template["description_ar"].format(speed=wind),
            impact_ar=template["impact_ar"],
            recommended_actions_ar=list(actions_ar),
            trigger_value=wind,
            threshold_value=getattr(self.thresholds, f"wind_{level}"),
            trigger_unit="km/h",
            confidence=forecast.confidence,
        )

    def _check_rain(self, forecast: WeatherForecast) -> WeatherAlert | None:
        """Check for rain conditions"""
        rain = forecast.precipitation_amount

        if rain >= self.thresholds.rain_critical:
            severity = AlertSeverity.CRITICAL
            level = "critical"
        elif rain >= self.thresholds.rain_warning:
            severity = AlertSeverity.WARNING
            level = "warning"
        else:
            return None

        template = ALERT_TEMPLATES[AlertType.RAIN].get(level)
        if not template:
            return None

        actions_en, actions_ar = ALERT_ACTIONS[AlertType.RAIN].get(level, ([], []))

        return WeatherAlert(
            alert_type=AlertType.RAIN,
            severity=severity,
            valid_from=datetime.combine(forecast.forecast_date, datetime.min.time()),
            valid_until=datetime.combine(forecast.forecast_date, datetime.min.time()) + timedelta(hours=24),
            title=template["title"],
            description=template["description"].format(amount=rain),
            impact=template["impact"],
            recommended_actions=list(actions_en),
            title_ar=template["title_ar"],
            description_ar=template["description_ar"].format(amount=rain),
            impact_ar=template["impact_ar"],
            recommended_actions_ar=list(actions_ar),
            trigger_value=rain,
            threshold_value=getattr(self.thresholds, f"rain_{level}"),
            trigger_unit="mm",
            confidence=forecast.confidence,
        )

    def _check_humidity(self, forecast: WeatherForecast) -> WeatherAlert | None:
        """Check for humidity conditions"""
        humidity = forecast.humidity

        if humidity >= self.thresholds.humidity_high_warning:
            severity = AlertSeverity.WARNING
            template = ALERT_TEMPLATES[AlertType.HUMIDITY].get("warning")
            level = "warning"
        elif humidity <= self.thresholds.humidity_low_warning:
            severity = AlertSeverity.ADVISORY
            template = ALERT_TEMPLATES[AlertType.HUMIDITY].get("advisory")
            level = "advisory"
        else:
            return None

        if not template:
            return None

        actions_en, actions_ar = ALERT_ACTIONS[AlertType.HUMIDITY].get(level, ([], []))

        return WeatherAlert(
            alert_type=AlertType.HUMIDITY,
            severity=severity,
            valid_from=datetime.combine(forecast.forecast_date, datetime.min.time()),
            valid_until=datetime.combine(forecast.forecast_date, datetime.min.time()) + timedelta(hours=24),
            title=template["title"],
            description=template["description"].format(humidity=humidity),
            impact=template["impact"],
            recommended_actions=list(actions_en),
            title_ar=template["title_ar"],
            description_ar=template["description_ar"].format(humidity=humidity),
            impact_ar=template["impact_ar"],
            recommended_actions_ar=list(actions_ar),
            trigger_value=humidity,
            threshold_value=self.thresholds.humidity_high_warning
            if humidity >= self.thresholds.humidity_high_warning
            else self.thresholds.humidity_low_warning,
            trigger_unit="%",
            confidence=forecast.confidence,
        )

    def _check_inversion(self, forecast: WeatherForecast) -> WeatherAlert | None:
        """Check for temperature inversion conditions"""
        if not forecast.is_inversion_likely:
            return None

        template = ALERT_TEMPLATES[AlertType.INVERSION].get("warning")
        if not template:
            return None

        actions_en, actions_ar = ALERT_ACTIONS[AlertType.INVERSION].get("warning", ([], []))

        start_hour = forecast.inversion_start_hour or 18
        end_hour = forecast.inversion_end_hour or 8

        return WeatherAlert(
            alert_type=AlertType.INVERSION,
            severity=AlertSeverity.WARNING,
            valid_from=datetime.combine(forecast.forecast_date, datetime.min.time()),
            valid_until=datetime.combine(forecast.forecast_date, datetime.min.time()) + timedelta(hours=24),
            title=template["title"],
            description=template["description"].format(start=start_hour, end=end_hour),
            impact=template["impact"],
            recommended_actions=list(actions_en),
            title_ar=template["title_ar"],
            description_ar=template["description_ar"].format(start=start_hour, end=end_hour),
            impact_ar=template["impact_ar"],
            recommended_actions_ar=list(actions_ar),
            confidence=forecast.confidence,
            tags=["inversion", "spray-window"],
        )

    def _check_uv(self, forecast: WeatherForecast) -> WeatherAlert | None:
        """Check for UV conditions"""
        if forecast.uv_index is None:
            return None

        uv = forecast.uv_index

        if uv >= self.thresholds.uv_extreme:
            severity = AlertSeverity.WARNING
        elif uv >= self.thresholds.uv_very_high:
            severity = AlertSeverity.ADVISORY
        else:
            return None

        template = ALERT_TEMPLATES[AlertType.UV].get("warning")
        if not template:
            return None

        actions_en, actions_ar = ALERT_ACTIONS[AlertType.UV].get("warning", ([], []))

        return WeatherAlert(
            alert_type=AlertType.UV,
            severity=severity,
            valid_from=datetime.combine(forecast.forecast_date, datetime.min.time()),
            valid_until=datetime.combine(forecast.forecast_date, datetime.min.time()) + timedelta(hours=24),
            title=template["title"],
            description=template["description"].format(uv=uv),
            impact=template["impact"],
            recommended_actions=list(actions_en),
            title_ar=template["title_ar"],
            description_ar=template["description_ar"].format(uv=uv),
            impact_ar=template["impact_ar"],
            recommended_actions_ar=list(actions_ar),
            trigger_value=float(uv),
            threshold_value=float(self.thresholds.uv_extreme),
            trigger_unit="UV Index",
            confidence=forecast.confidence,
        )

    def _check_sandstorm(self, forecast: WeatherForecast) -> WeatherAlert | None:
        """Check for sandstorm conditions — فحص ظروف العاصفة الرملية"""
        wind = forecast.wind_gust or forecast.wind_speed
        humidity = forecast.humidity

        # Sandstorm conditions: high wind + low humidity in arid regions
        if wind >= 60 and humidity < 20:
            severity = AlertSeverity.CRITICAL
            level = "critical"
        elif wind >= 45 and humidity < 25:
            severity = AlertSeverity.WARNING
            level = "warning"
        elif wind >= 35 and humidity < 30:
            severity = AlertSeverity.ADVISORY
            level = "warning"  # Use warning template (closest available)
        else:
            return None

        template = ALERT_TEMPLATES.get(AlertType.SANDSTORM, {}).get(level)
        actions = ALERT_ACTIONS.get(AlertType.SANDSTORM, {}).get(level, ([], []))

        if not template:
            return None

        actions_en, actions_ar = actions if isinstance(actions, tuple) else (actions, [])

        return WeatherAlert(
            alert_type=AlertType.SANDSTORM,
            severity=severity,
            valid_from=datetime.combine(forecast.forecast_date, datetime.min.time()),
            valid_until=datetime.combine(forecast.forecast_date, datetime.min.time()) + timedelta(hours=6),
            title=template.get("title", "Sandstorm Warning"),
            title_ar=template.get("title_ar", "تحذير عاصفة رملية"),
            description=template.get("description", ""),
            description_ar=template.get("description_ar", ""),
            impact=template.get("impact", ""),
            impact_ar=template.get("impact_ar", ""),
            recommended_actions=list(actions_en),
            recommended_actions_ar=list(actions_ar),
            trigger_value=wind,
            threshold_value=60.0 if severity == AlertSeverity.CRITICAL else (45.0 if severity == AlertSeverity.WARNING else 35.0),
            trigger_unit="km/h",
            confidence=forecast.confidence,
        )

    def _check_hail(self, forecast: WeatherForecast) -> WeatherAlert | None:
        """Check for hail conditions — فحص ظروف البرد"""
        # Only trigger if precipitation type indicates hail
        if forecast.precipitation_type != "hail":
            return None

        # Determine severity based on precipitation amount as proxy for hail size
        rain = forecast.precipitation_amount
        if rain >= 20:
            severity = AlertSeverity.CRITICAL
            level = "critical"
        else:
            severity = AlertSeverity.WARNING
            level = "warning"

        template = ALERT_TEMPLATES.get(AlertType.HAIL, {}).get(level)
        if not template:
            return None

        actions = ALERT_ACTIONS.get(AlertType.HAIL, {}).get(level, ([], []))
        actions_en, actions_ar = actions if isinstance(actions, tuple) else (actions, [])

        return WeatherAlert(
            alert_type=AlertType.HAIL,
            severity=severity,
            valid_from=datetime.combine(forecast.forecast_date, datetime.min.time()),
            valid_until=datetime.combine(forecast.forecast_date, datetime.min.time()) + timedelta(hours=24),
            title=template["title"],
            description=template["description"],
            impact=template["impact"],
            recommended_actions=list(actions_en),
            title_ar=template["title_ar"],
            description_ar=template["description_ar"],
            impact_ar=template["impact_ar"],
            recommended_actions_ar=list(actions_ar),
            trigger_value=rain,
            trigger_unit="mm",
            confidence=forecast.confidence,
        )

    def _check_drought(self, forecasts: list, current_index: int) -> WeatherAlert | None:
        """Check for drought conditions over multi-day forecast — فحص ظروف الجفاف"""
        if current_index + 5 > len(forecasts):
            return None

        # Check 5 consecutive days with no significant precipitation
        upcoming = forecasts[current_index : current_index + 5]
        total_precip = sum(getattr(f, "precipitation_amount", 0) or 0 for f in upcoming)
        avg_humidity = sum(f.humidity for f in upcoming) / len(upcoming)
        avg_temp = sum(f.temperature for f in upcoming) / len(upcoming)

        if total_precip < 1.0 and avg_humidity < 25 and avg_temp > 35:
            severity = AlertSeverity.CRITICAL
            level = "critical"
        elif total_precip < 2.0 and avg_humidity < 30 and avg_temp > 30:
            severity = AlertSeverity.WARNING
            level = "warning"
        else:
            return None

        template = ALERT_TEMPLATES.get(AlertType.DROUGHT, {}).get(level)
        actions = ALERT_ACTIONS.get(AlertType.DROUGHT, {}).get(level, ([], []))

        if not template:
            return None

        actions_en, actions_ar = actions if isinstance(actions, tuple) else (actions, [])

        first_forecast = upcoming[0]
        return WeatherAlert(
            alert_type=AlertType.DROUGHT,
            severity=severity,
            valid_from=datetime.combine(first_forecast.forecast_date, datetime.min.time()),
            valid_until=datetime.combine(first_forecast.forecast_date, datetime.min.time()) + timedelta(hours=120),
            title=template.get("title", "Drought Warning"),
            title_ar=template.get("title_ar", "تحذير جفاف"),
            description=template.get("description", ""),
            description_ar=template.get("description_ar", ""),
            impact=template.get("impact", ""),
            impact_ar=template.get("impact_ar", ""),
            recommended_actions=list(actions_en),
            recommended_actions_ar=list(actions_ar),
            trigger_value=total_precip,
            trigger_unit="mm (5-day total)",
            confidence=first_forecast.confidence,
            tags=["drought", "multi-day"],
        )

    def generate_irrigation_schedule(
        self,
        forecasts: list[WeatherForecast],
        field_id: str,
        crop_type: CropType,
        soil_moisture_current: float | None = None,
        planned_irrigation_mm: float = 0.0,
        field_area_ha: float = 1.0,
    ) -> IrrigationSchedule:
        """
        Generate irrigation scheduling recommendation based on forecast

        Args:
            forecasts: Weather forecasts for coming days
            field_id: Field identifier
            crop_type: Crop type
            soil_moisture_current: Current soil moisture (%)
            planned_irrigation_mm: Originally planned irrigation amount
            field_area_ha: Field area in hectares

        Returns:
            IrrigationSchedule with recommendation
        """
        # Calculate expected rain and ET
        expected_rain_mm = sum(f.precipitation_amount for f in forecasts[:3])
        expected_rain_prob = max((f.precipitation_probability for f in forecasts[:3]), default=0)

        # Simple ET calculation (more sophisticated in real implementation)
        avg_temp = sum(f.temperature for f in forecasts[:3]) / max(len(forecasts[:3]), 1)
        avg_humidity = sum(f.humidity for f in forecasts[:3]) / max(len(forecasts[:3]), 1)
        avg_wind = sum(f.wind_speed for f in forecasts[:3]) / max(len(forecasts[:3]), 1)

        # Simplified Hargreaves ET (reference ET)
        expected_et_mm = max(0.0023 * (avg_temp + 17.8) * 7, 0) * 3  # 3 days

        # Determine recommendation
        factors: list[str] = []
        factors_ar: list[str] = []
        warnings: list[str] = []
        warnings_ar: list[str] = []

        if expected_rain_mm >= 10 or expected_rain_prob >= 60:
            recommendation = IrrigationRecommendation.SKIP_IRRIGATION
            reason = f"Significant rain expected ({expected_rain_mm:.1f}mm with {expected_rain_prob:.0f}% probability)"
            reason_ar = f"أمطار كبيرة متوقعة ({expected_rain_mm:.1f}مم باحتمال {expected_rain_prob:.0f}%)"
            adjustment_factor = 0.0
            factors.append(f"Expected rainfall: {expected_rain_mm:.1f}mm")
            factors_ar.append(f"الأمطار المتوقعة: {expected_rain_mm:.1f}مم")
        elif expected_rain_mm >= 5:
            recommendation = IrrigationRecommendation.REDUCE_AMOUNT
            reduction = min(expected_rain_mm / planned_irrigation_mm, 0.5) if planned_irrigation_mm > 0 else 0.3
            adjustment_factor = 1.0 - reduction
            reason = f"Light rain expected, reduce irrigation by {reduction * 100:.0f}%"
            reason_ar = f"أمطار خفيفة متوقعة، قلل الري بنسبة {reduction * 100:.0f}%"
            factors.append(f"Expected rainfall: {expected_rain_mm:.1f}mm")
            factors_ar.append(f"الأمطار المتوقعة: {expected_rain_mm:.1f}مم")
        elif avg_temp > 38:
            recommendation = IrrigationRecommendation.INCREASE_AMOUNT
            adjustment_factor = 1.2  # Increase by 20%
            reason = f"High temperatures expected ({avg_temp:.1f}C), increase irrigation"
            reason_ar = f"درجات حرارة مرتفعة متوقعة ({avg_temp:.1f}م)، زد الري"
            factors.append(f"High temperature: {avg_temp:.1f}C")
            factors_ar.append(f"حرارة مرتفعة: {avg_temp:.1f}م")
            warnings.append("Irrigate early morning to reduce evaporation")
            warnings_ar.append("الري في الصباح الباكر لتقليل التبخر")
        elif soil_moisture_current is not None and soil_moisture_current > 60:
            recommendation = IrrigationRecommendation.DELAY_IRRIGATION
            adjustment_factor = 1.0
            reason = f"Soil moisture adequate ({soil_moisture_current:.0f}%), delay irrigation"
            reason_ar = f"رطوبة التربة كافية ({soil_moisture_current:.0f}%)، أجّل الري"
            factors.append(f"Current soil moisture: {soil_moisture_current:.0f}%")
            factors_ar.append(f"رطوبة التربة الحالية: {soil_moisture_current:.0f}%")
        elif soil_moisture_current is not None and soil_moisture_current < 30:
            recommendation = IrrigationRecommendation.IRRIGATE_NOW
            adjustment_factor = 1.1  # Slight increase
            reason = f"Low soil moisture ({soil_moisture_current:.0f}%), irrigate immediately"
            reason_ar = f"رطوبة التربة منخفضة ({soil_moisture_current:.0f}%)، ري فوري"
            factors.append(f"Low soil moisture: {soil_moisture_current:.0f}%")
            factors_ar.append(f"رطوبة تربة منخفضة: {soil_moisture_current:.0f}%")
        else:
            recommendation = IrrigationRecommendation.IRRIGATE_SOON
            adjustment_factor = 1.0
            reason = "Normal conditions, proceed with planned irrigation"
            reason_ar = "ظروف طبيعية، استمر بالري المخطط"
            factors.append("Weather conditions normal")
            factors_ar.append("ظروف الطقس طبيعية")

        # Calculate water saved
        recommended_amount = planned_irrigation_mm * adjustment_factor
        water_saved_liters = None
        cost_saved = None

        if adjustment_factor < 1.0 and planned_irrigation_mm > 0:
            water_saved_mm = planned_irrigation_mm - recommended_amount
            water_saved_liters = water_saved_mm * field_area_ha * 10000  # Convert to liters
            water_cost_per_liter = getattr(self.config, "water_cost_per_liter", 0.003)
            cost_saved = water_saved_liters * water_cost_per_liter

        return IrrigationSchedule(
            field_id=field_id,
            crop_type=crop_type,
            recommendation=recommendation,
            recommended_date=forecasts[0].forecast_date if forecasts else None,
            recommended_amount_mm=recommended_amount,
            original_amount_mm=planned_irrigation_mm,
            adjustment_factor=adjustment_factor,
            expected_rain_mm=expected_rain_mm,
            expected_et_mm=expected_et_mm,
            soil_moisture_current=soil_moisture_current,
            reason=reason,
            factors=factors,
            warnings=warnings,
            reason_ar=reason_ar,
            factors_ar=factors_ar,
            warnings_ar=warnings_ar,
            water_saved_liters=water_saved_liters,
            cost_saved=cost_saved,
            confidence=0.8 if soil_moisture_current else 0.6,
            forecast_days_used=min(len(forecasts), 3),
        )

    def generate_harvest_window(
        self,
        forecasts: list[WeatherForecast],
        field_id: str,
        crop_type: CropType,
        target_moisture_content: float | None = None,
    ) -> HarvestWindow:
        """
        Generate harvest timing recommendation

        Args:
            forecasts: Weather forecasts for coming days
            field_id: Field identifier
            crop_type: Crop type
            target_moisture_content: Target grain moisture (%)

        Returns:
            HarvestWindow with recommendation
        """
        if not forecasts:
            return HarvestWindow(
                field_id=field_id,
                crop_type=crop_type,
                overall_condition=HarvestCondition.UNSUITABLE,
                recommendation="Insufficient forecast data",
                recommendation_ar="بيانات التوقعات غير كافية",
            )

        # Score each day
        best_day = None
        best_score = 0.0
        considerations: list[str] = []
        considerations_ar: list[str] = []

        for forecast in forecasts[:7]:  # Look at next 7 days
            score = 100.0

            # Rain penalty
            if forecast.precipitation_probability > 50:
                score -= 50
            elif forecast.precipitation_probability > 30:
                score -= 25
            elif forecast.precipitation_probability > 10:
                score -= 10

            # Humidity penalty for grain crops
            if crop_type in [CropType.WHEAT, CropType.BARLEY]:
                if forecast.humidity > 70:
                    score -= 30
                elif forecast.humidity > 60:
                    score -= 15

            # Wind bonus (helps drying) but too much is bad
            if 5 < forecast.wind_speed < 20:
                score += 10
            elif forecast.wind_speed > 40:
                score -= 20

            # Temperature (moderate is best)
            if 20 < forecast.temperature < 35:
                score += 10
            elif forecast.temperature > 40:
                score -= 15

            if score > best_score:
                best_score = score
                best_day = forecast

        # Determine condition
        if best_score >= 80:
            condition = HarvestCondition.OPTIMAL
        elif best_score >= 60:
            condition = HarvestCondition.GOOD
        elif best_score >= 40:
            condition = HarvestCondition.ACCEPTABLE
        elif best_score >= 20:
            condition = HarvestCondition.RISKY
        else:
            condition = HarvestCondition.UNSUITABLE

        # Generate recommendations
        if condition == HarvestCondition.OPTIMAL:
            recommendation = f"Optimal harvest window on {best_day.forecast_date if best_day else 'N/A'}"
            recommendation_ar = f"نافذة حصاد مثالية في {best_day.forecast_date if best_day else 'غير متاح'}"
        elif condition == HarvestCondition.GOOD:
            recommendation = "Good harvest conditions expected. Proceed with harvest plans."
            recommendation_ar = "ظروف حصاد جيدة متوقعة. استمر في خطط الحصاد."
        elif condition == HarvestCondition.ACCEPTABLE:
            recommendation = "Acceptable conditions, but monitor weather closely."
            recommendation_ar = "ظروف مقبولة، لكن راقب الطقس عن كثب."
            considerations.append("Have drying facilities ready")
            considerations_ar.append("جهّز مرافق التجفيف")
        elif condition == HarvestCondition.RISKY:
            recommendation = "Risky conditions. Consider delaying harvest if possible."
            recommendation_ar = "ظروف محفوفة بالمخاطر. فكر في تأجيل الحصاد إن أمكن."
            considerations.append("Monitor hourly forecasts")
            considerations_ar.append("راقب التوقعات كل ساعة")
        else:
            recommendation = "Unsuitable conditions for harvest. Wait for better weather."
            recommendation_ar = "ظروف غير مناسبة للحصاد. انتظر طقساً أفضل."

        # Calculate dry hours
        dry_hours = sum(24.0 if f.precipitation_probability < 20 else 0.0 for f in forecasts[:3])

        return HarvestWindow(
            field_id=field_id,
            crop_type=crop_type,
            window_start=datetime.combine(forecasts[0].forecast_date, datetime.min.time()) if forecasts else None,
            window_end=datetime.combine(forecasts[-1].forecast_date, datetime.max.time()) if forecasts else None,
            optimal_date=best_day.forecast_date if best_day else None,
            overall_condition=condition,
            score=best_score,
            expected_rain_probability=max((f.precipitation_probability for f in forecasts[:3]), default=0),
            expected_humidity_avg=sum(f.humidity for f in forecasts[:3]) / max(len(forecasts[:3]), 1),
            expected_temperature_avg=sum(f.temperature for f in forecasts[:3]) / max(len(forecasts[:3]), 1),
            dry_hours_available=dry_hours,
            rain_risk="high" if max((f.precipitation_probability for f in forecasts[:3]), default=0) > 50 else "low",
            rain_risk_ar="مرتفع"
            if max((f.precipitation_probability for f in forecasts[:3]), default=0) > 50
            else "منخفض",
            recommendation=recommendation,
            considerations=considerations,
            recommendation_ar=recommendation_ar,
            considerations_ar=considerations_ar,
            target_moisture_content=target_moisture_content,
        )


# Convenience function
def generate_weather_alerts(
    forecasts: list[WeatherForecast],
    crop_type: CropType = CropType.GENERAL,
    field_id: str | None = None,
) -> list[WeatherAlert]:
    """
    Generate weather alerts from forecast data

    Args:
        forecasts: List of weather forecasts
        crop_type: Crop type for crop-specific thresholds
        field_id: Optional field identifier

    Returns:
        List of weather alerts
    """
    generator = WeatherAlertGenerator()
    return generator.generate_alerts(
        forecasts=forecasts,
        crop_type=crop_type,
        field_id=field_id,
    )
