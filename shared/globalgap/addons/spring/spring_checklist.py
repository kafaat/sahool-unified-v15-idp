"""
SPRING Assessment Checklist
قائمة تحقق تقييم SPRING

Comprehensive checklist for SPRING (Sustainable Program for Irrigation and Groundwater)
compliance assessment.

قائمة تحقق شاملة لتقييم امتثال SPRING (البرنامج المستدام للري والمياه الجوفية).
"""

from typing import Dict, List, Optional
from enum import Enum


# ==================== Categories ====================


class SpringCategory(str, Enum):
    """SPRING checklist categories / فئات قائمة تحقق SPRING"""

    WATER_SOURCES = "WATER_SOURCES"
    WATER_EFFICIENCY = "WATER_EFFICIENCY"
    IRRIGATION_SYSTEMS = "IRRIGATION_SYSTEMS"
    WATER_QUALITY = "WATER_QUALITY"
    LEGAL_COMPLIANCE = "LEGAL_COMPLIANCE"
    MONITORING_RECORDS = "MONITORING_RECORDS"


SPRING_CATEGORIES = {
    "WATER_SOURCES": {
        "code": "WS",
        "name_en": "Water Sources Assessment",
        "name_ar": "تقييم مصادر المياه",
        "description_en": "Assessment of water sources, sustainability, and resource management",
        "description_ar": "تقييم مصادر المياه والاستدامة وإدارة الموارد",
        "order": 1,
    },
    "WATER_EFFICIENCY": {
        "code": "WE",
        "name_en": "Water Use Efficiency",
        "name_ar": "كفاءة استخدام المياه",
        "description_en": "Metrics and practices for efficient water use",
        "description_ar": "المقاييس والممارسات لاستخدام المياه بكفاءة",
        "order": 2,
    },
    "IRRIGATION_SYSTEMS": {
        "code": "IS",
        "name_en": "Irrigation System Requirements",
        "name_ar": "متطلبات نظام الري",
        "description_en": "Irrigation infrastructure and technology requirements",
        "description_ar": "متطلبات البنية التحتية والتقنية للري",
        "order": 3,
    },
    "WATER_QUALITY": {
        "code": "WQ",
        "name_en": "Water Quality Monitoring",
        "name_ar": "مراقبة جودة المياه",
        "description_en": "Water quality testing and monitoring requirements",
        "description_ar": "متطلبات اختبار ومراقبة جودة المياه",
        "order": 4,
    },
    "LEGAL_COMPLIANCE": {
        "code": "LC",
        "name_en": "Legal Compliance for Water Rights",
        "name_ar": "الامتثال القانوني لحقوق المياه",
        "description_en": "Legal permits and water rights compliance",
        "description_ar": "الامتثال للتصاريح القانونية وحقوق المياه",
        "order": 5,
    },
    "MONITORING_RECORDS": {
        "code": "MR",
        "name_en": "Monitoring and Record Keeping",
        "name_ar": "المراقبة وحفظ السجلات",
        "description_en": "Water use monitoring and documentation requirements",
        "description_ar": "متطلبات مراقبة استخدام المياه والتوثيق",
        "order": 6,
    },
}


# ==================== Compliance Levels ====================


class SpringComplianceLevel(str, Enum):
    """SPRING compliance level / مستوى امتثال SPRING"""

    MANDATORY = "MANDATORY"  # إلزامي
    RECOMMENDED = "RECOMMENDED"  # موصى به


# ==================== SPRING Checklist Items ====================

SPRING_CHECKLIST: List[Dict] = [
    # ==================== WATER SOURCES ====================
    {
        "item_id": "WS.01",
        "category": "WATER_SOURCES",
        "compliance_level": "MANDATORY",
        "title_en": "Water Source Identification",
        "title_ar": "تحديد مصدر المياه",
        "requirement_en": "All water sources used for irrigation must be identified and documented, including type, location, and capacity.",
        "requirement_ar": "يجب تحديد وتوثيق جميع مصادر المياه المستخدمة للري، بما في ذلك النوع والموقع والسعة.",
        "guidance_en": "Maintain a register of all water sources (wells, boreholes, rivers, canals, etc.) with GPS coordinates and technical specifications.",
        "guidance_ar": "الاحتفاظ بسجل لجميع مصادر المياه (الآبار، الحفر، الأنهار، القنوات، إلخ) مع الإحداثيات الجغرافية والمواصفات الفنية.",
        "verification_en": "Water source register, maps, technical specifications",
        "verification_ar": "سجل مصادر المياه، الخرائط، المواصفات الفنية",
    },
    {
        "item_id": "WS.02",
        "category": "WATER_SOURCES",
        "compliance_level": "MANDATORY",
        "title_en": "Groundwater Sustainability Assessment",
        "title_ar": "تقييم استدامة المياه الجوفية",
        "requirement_en": "For groundwater sources, evidence of sustainable extraction must be demonstrated (water level monitoring, aquifer recharge assessment).",
        "requirement_ar": "بالنسبة لمصادر المياه الجوفية، يجب إثبات الاستخراج المستدام (مراقبة مستوى المياه، تقييم إعادة شحن طبقة المياه الجوفية).",
        "guidance_en": "Monitor water levels quarterly. If declining >1m/year, implement water conservation measures and/or seek alternative sources.",
        "guidance_ar": "مراقبة مستويات المياه فصلياً. إذا انخفضت >1 متر/سنة، تنفيذ تدابير الحفاظ على المياه و/أو البحث عن مصادر بديلة.",
        "verification_en": "Water level monitoring records, hydrogeological reports",
        "verification_ar": "سجلات مراقبة مستوى المياه، تقارير هيدروجيولوجية",
        "yemen_context": "Critical in Yemen due to severe groundwater depletion. Water tables declining 6-7m/year in Sana'a basin.",
    },
    {
        "item_id": "WS.03",
        "category": "WATER_SOURCES",
        "compliance_level": "RECOMMENDED",
        "title_en": "Rainwater Harvesting",
        "title_ar": "حصاد مياه الأمطار",
        "requirement_en": "Implement rainwater harvesting systems where feasible to supplement irrigation water.",
        "requirement_ar": "تنفيذ أنظمة حصاد مياه الأمطار حيثما أمكن ذلك لتكملة مياه الري.",
        "guidance_en": "Install rainwater collection systems (roof catchment, surface runoff collection). Minimum 100m³ storage capacity recommended.",
        "guidance_ar": "تركيب أنظمة تجميع مياه الأمطار (تجميع من الأسطح، تجميع الجريان السطحي). يوصى بسعة تخزين لا تقل عن 100 متر مكعب.",
        "verification_en": "Rainwater harvesting infrastructure, collection records",
        "verification_ar": "البنية التحتية لحصاد مياه الأمطار، سجلات التجميع",
    },
    {
        "item_id": "WS.04",
        "category": "WATER_SOURCES",
        "compliance_level": "RECOMMENDED",
        "title_en": "Alternative Water Sources",
        "title_ar": "مصادر مياه بديلة",
        "requirement_en": "Explore and implement use of alternative water sources (treated wastewater, brackish water with desalination).",
        "requirement_ar": "استكشاف وتنفيذ استخدام مصادر المياه البديلة (مياه الصرف المعالجة، المياه قليلة الملوحة مع التحلية).",
        "guidance_en": "Assess feasibility of recycled water use. Ensure proper treatment and quality testing for food safety.",
        "guidance_ar": "تقييم جدوى استخدام المياه المعاد تدويرها. ضمان المعالجة المناسبة واختبار الجودة لسلامة الغذاء.",
        "verification_en": "Feasibility studies, treatment systems, quality test results",
        "verification_ar": "دراسات الجدوى، أنظمة المعالجة، نتائج اختبار الجودة",
    },
    # ==================== WATER EFFICIENCY ====================
    {
        "item_id": "WE.01",
        "category": "WATER_EFFICIENCY",
        "compliance_level": "MANDATORY",
        "title_en": "Water Use Measurement",
        "title_ar": "قياس استخدام المياه",
        "requirement_en": "All water used for irrigation must be measured using flow meters or other reliable measurement devices.",
        "requirement_ar": "يجب قياس جميع المياه المستخدمة للري باستخدام عدادات التدفق أو أجهزة قياس موثوقة أخرى.",
        "guidance_en": "Install water meters on all water sources. Record daily/weekly usage. Calibrate meters annually.",
        "guidance_ar": "تركيب عدادات المياه على جميع مصادر المياه. تسجيل الاستخدام اليومي/الأسبوعي. معايرة العدادات سنوياً.",
        "verification_en": "Water meters, usage records, calibration certificates",
        "verification_ar": "عدادات المياه، سجلات الاستخدام، شهادات المعايرة",
    },
    {
        "item_id": "WE.02",
        "category": "WATER_EFFICIENCY",
        "compliance_level": "MANDATORY",
        "title_en": "Irrigation Efficiency Target",
        "title_ar": "هدف كفاءة الري",
        "requirement_en": "Achieve minimum irrigation application efficiency of 70% (recommended 85% for drip systems).",
        "requirement_ar": "تحقيق كفاءة تطبيق الري بحد أدنى 70% (يوصى بـ 85% لأنظمة التنقيط).",
        "guidance_en": "Calculate efficiency: (Water stored in root zone / Total water applied) × 100. Conduct field evaluations quarterly.",
        "guidance_ar": "حساب الكفاءة: (المياه المخزنة في منطقة الجذور / إجمالي المياه المطبقة) × 100. إجراء تقييمات ميدانية فصلياً.",
        "verification_en": "Efficiency calculations, field evaluation reports",
        "verification_ar": "حسابات الكفاءة، تقارير التقييم الميداني",
    },
    {
        "item_id": "WE.03",
        "category": "WATER_EFFICIENCY",
        "compliance_level": "MANDATORY",
        "title_en": "Water Use Per Hectare Benchmark",
        "title_ar": "معيار استخدام المياه لكل هكتار",
        "requirement_en": "Water use must not exceed crop-specific benchmarks by more than 20% without documented justification.",
        "requirement_ar": "يجب ألا يتجاوز استخدام المياه معايير المحصول المحددة بأكثر من 20% دون تبرير موثق.",
        "guidance_en": "Compare actual water use against regional crop water requirements (ETc). Document reasons for exceedance (soil type, climate anomalies, etc.).",
        "guidance_ar": "مقارنة الاستخدام الفعلي للمياه مع متطلبات المياه الإقليمية للمحاصيل (ETc). توثيق أسباب التجاوز (نوع التربة، الحالات المناخية الشاذة، إلخ).",
        "verification_en": "Water use records, crop water requirement calculations, variance justifications",
        "verification_ar": "سجلات استخدام المياه، حسابات متطلبات مياه المحاصيل، تبريرات التباين",
    },
    {
        "item_id": "WE.04",
        "category": "WATER_EFFICIENCY",
        "compliance_level": "RECOMMENDED",
        "title_en": "Soil Moisture Monitoring",
        "title_ar": "مراقبة رطوبة التربة",
        "requirement_en": "Use soil moisture sensors or other monitoring tools to guide irrigation scheduling.",
        "requirement_ar": "استخدام أجهزة استشعار رطوبة التربة أو أدوات المراقبة الأخرى لتوجيه جدولة الري.",
        "guidance_en": "Install sensors at representative locations. Irrigate when soil moisture drops to 70-80% of field capacity.",
        "guidance_ar": "تركيب أجهزة الاستشعار في مواقع تمثيلية. الري عندما تنخفض رطوبة التربة إلى 70-80% من السعة الحقلية.",
        "verification_en": "Soil moisture sensors, irrigation scheduling records",
        "verification_ar": "أجهزة استشعار رطوبة التربة، سجلات جدولة الري",
    },
    {
        "item_id": "WE.05",
        "category": "WATER_EFFICIENCY",
        "compliance_level": "RECOMMENDED",
        "title_en": "Weather-Based Irrigation Scheduling",
        "title_ar": "جدولة الري بناءً على الطقس",
        "requirement_en": "Utilize weather data and crop evapotranspiration (ETc) calculations for irrigation scheduling.",
        "requirement_ar": "استخدام بيانات الطقس وحسابات التبخر النتح للمحاصيل (ETc) لجدولة الري.",
        "guidance_en": "Access local weather data (temperature, humidity, wind, solar radiation). Calculate crop water requirements using FAO Penman-Monteith or similar method.",
        "guidance_ar": "الوصول إلى بيانات الطقس المحلية (درجة الحرارة، الرطوبة، الرياح، الإشعاع الشمسي). حساب متطلبات مياه المحاصيل باستخدام طريقة FAO Penman-Monteith أو طريقة مماثلة.",
        "verification_en": "Weather data access, ETc calculations, irrigation schedules",
        "verification_ar": "الوصول إلى بيانات الطقس، حسابات ETc، جداول الري",
    },
    {
        "item_id": "WE.06",
        "category": "WATER_EFFICIENCY",
        "compliance_level": "RECOMMENDED",
        "title_en": "Mulching and Water Conservation Practices",
        "title_ar": "التغطية وممارسات الحفاظ على المياه",
        "requirement_en": "Implement mulching, cover crops, or other practices to reduce evaporation and conserve soil moisture.",
        "requirement_ar": "تنفيذ التغطية أو المحاصيل الغطائية أو ممارسات أخرى لتقليل التبخر والحفاظ على رطوبة التربة.",
        "guidance_en": "Use organic mulch (straw, compost), plastic mulch, or cover crops. Target 30-50% reduction in evaporative losses.",
        "guidance_ar": "استخدام الغطاء العضوي (القش، السماد)، الغطاء البلاستيكي، أو المحاصيل الغطائية. استهداف تقليل 30-50% في خسائر التبخر.",
        "verification_en": "Field observations, practice documentation, water savings estimates",
        "verification_ar": "الملاحظات الميدانية، توثيق الممارسات، تقديرات توفير المياه",
    },
    # ==================== IRRIGATION SYSTEMS ====================
    {
        "item_id": "IS.01",
        "category": "IRRIGATION_SYSTEMS",
        "compliance_level": "MANDATORY",
        "title_en": "Irrigation System Suitability",
        "title_ar": "ملاءمة نظام الري",
        "requirement_en": "Irrigation system must be appropriate for crop type, soil conditions, and topography.",
        "requirement_ar": "يجب أن يكون نظام الري مناسباً لنوع المحصول وظروف التربة والتضاريس.",
        "guidance_en": "Drip irrigation recommended for vegetables, fruits. Sprinkler for field crops. Avoid flood irrigation on sloped land.",
        "guidance_ar": "يوصى بالري بالتنقيط للخضروات والفواكه. الرش للمحاصيل الحقلية. تجنب الري بالغمر على الأراضي المنحدرة.",
        "verification_en": "System design documents, field assessment",
        "verification_ar": "وثائق تصميم النظام، التقييم الميداني",
    },
    {
        "item_id": "IS.02",
        "category": "IRRIGATION_SYSTEMS",
        "compliance_level": "MANDATORY",
        "title_en": "Irrigation System Maintenance",
        "title_ar": "صيانة نظام الري",
        "requirement_en": "Regular maintenance and inspection of irrigation equipment to ensure optimal performance and prevent leaks.",
        "requirement_ar": "الصيانة والفحص المنتظم لمعدات الري لضمان الأداء الأمثل ومنع التسربات.",
        "guidance_en": "Inspect system monthly. Clean filters, check emitters/nozzles, repair leaks immediately. Conduct pressure tests quarterly.",
        "guidance_ar": "فحص النظام شهرياً. تنظيف الفلاتر، فحص الموزعات/الفوهات، إصلاح التسربات فوراً. إجراء اختبارات الضغط فصلياً.",
        "verification_en": "Maintenance logs, inspection records, repair invoices",
        "verification_ar": "سجلات الصيانة، سجلات الفحص، فواتير الإصلاح",
    },
    {
        "item_id": "IS.03",
        "category": "IRRIGATION_SYSTEMS",
        "compliance_level": "MANDATORY",
        "title_en": "Distribution Uniformity",
        "title_ar": "توحيد التوزيع",
        "requirement_en": "Irrigation system must achieve minimum distribution uniformity of 85%.",
        "requirement_ar": "يجب أن يحقق نظام الري الحد الأدنى من توحيد التوزيع بنسبة 85%.",
        "guidance_en": "Conduct uniformity tests annually. For drip: measure emitter flow rates. For sprinkler: catch can tests.",
        "guidance_ar": "إجراء اختبارات التوحيد سنوياً. للتنقيط: قياس معدلات تدفق الموزعات. للرش: اختبارات جمع العينات.",
        "verification_en": "Uniformity test results, corrective actions for non-compliance",
        "verification_ar": "نتائج اختبار التوحيد، الإجراءات التصحيحية لعدم الامتثال",
    },
    {
        "item_id": "IS.04",
        "category": "IRRIGATION_SYSTEMS",
        "compliance_level": "RECOMMENDED",
        "title_en": "Drip Irrigation Adoption",
        "title_ar": "اعتماد الري بالتنقيط",
        "requirement_en": "Prioritize drip irrigation for high-value crops (vegetables, fruits, orchards).",
        "requirement_ar": "إعطاء الأولوية للري بالتنقيط للمحاصيل ذات القيمة العالية (الخضروات، الفواكه، البساتين).",
        "guidance_en": "Target >70% of high-value crop area under drip irrigation. Provides water savings of 30-60% vs. surface irrigation.",
        "guidance_ar": "استهداف >70% من مساحة المحاصيل ذات القيمة العالية تحت الري بالتنقيط. يوفر توفيراً في المياه بنسبة 30-60% مقارنة بالري السطحي.",
        "verification_en": "Field maps showing irrigation methods by area",
        "verification_ar": "خرائط الحقول تظهر طرق الري حسب المنطقة",
    },
    {
        "item_id": "IS.05",
        "category": "IRRIGATION_SYSTEMS",
        "compliance_level": "RECOMMENDED",
        "title_en": "Automation and Smart Irrigation",
        "title_ar": "الأتمتة والري الذكي",
        "requirement_en": "Implement automated irrigation controls (timers, sensors, smart controllers) where economically feasible.",
        "requirement_ar": "تنفيذ ضوابط الري الآلية (الموقتات، أجهزة الاستشعار، وحدات التحكم الذكية) حيثما كان ذلك مجدياً اقتصادياً.",
        "guidance_en": "Use soil moisture sensors, weather-based controllers, or mobile app-based systems for precision irrigation.",
        "guidance_ar": "استخدام أجهزة استشعار رطوبة التربة، وحدات التحكم القائمة على الطقس، أو الأنظمة القائمة على تطبيقات الهاتف المحمول للري الدقيق.",
        "verification_en": "Automation equipment, system operation records",
        "verification_ar": "معدات الأتمتة، سجلات تشغيل النظام",
    },
    # ==================== WATER QUALITY ====================
    {
        "item_id": "WQ.01",
        "category": "WATER_QUALITY",
        "compliance_level": "MANDATORY",
        "title_en": "Water Quality Testing - Frequency",
        "title_ar": "اختبار جودة المياه - التكرار",
        "requirement_en": "Conduct water quality testing at least annually for all irrigation water sources. More frequent testing (quarterly) for groundwater and recycled water.",
        "requirement_ar": "إجراء اختبار جودة المياه سنوياً على الأقل لجميع مصادر مياه الري. اختبار أكثر تكراراً (فصلياً) للمياه الجوفية والمياه المعاد تدويرها.",
        "guidance_en": "Test parameters: pH, EC, TDS, salinity, nitrates, phosphates, bacterial count. Use accredited laboratories.",
        "guidance_ar": "معايير الاختبار: الحموضة، التوصيل الكهربائي، المواد الصلبة الذائبة، الملوحة، النترات، الفوسفات، عدد البكتيريا. استخدام مختبرات معتمدة.",
        "verification_en": "Laboratory test reports, testing schedule",
        "verification_ar": "تقارير اختبار المختبر، جدول الاختبار",
    },
    {
        "item_id": "WQ.02",
        "category": "WATER_QUALITY",
        "compliance_level": "MANDATORY",
        "title_en": "Water Quality Standards Compliance",
        "title_ar": "الامتثال لمعايير جودة المياه",
        "requirement_en": "Irrigation water must meet food safety and crop health standards (WHO/FAO guidelines for agricultural water).",
        "requirement_ar": "يجب أن تلبي مياه الري معايير سلامة الغذاء وصحة المحاصيل (إرشادات منظمة الصحة العالمية/الفاو للمياه الزراعية).",
        "guidance_en": "E.coli: <1000 CFU/100ml for crops eaten raw. Salinity: <2 dS/m for sensitive crops, <4 dS/m for moderately tolerant crops.",
        "guidance_ar": "الإشريكية القولونية: <1000 وحدة تشكيل مستعمرة/100 مل للمحاصيل المأكولة نيئة. الملوحة: <2 ديسي سيمنز/م للمحاصيل الحساسة، <4 للمحاصيل المتحملة معتدلاً.",
        "verification_en": "Test results showing compliance, corrective actions for non-compliance",
        "verification_ar": "نتائج الاختبار تظهر الامتثال، الإجراءات التصحيحية لعدم الامتثال",
    },
    {
        "item_id": "WQ.03",
        "category": "WATER_QUALITY",
        "compliance_level": "MANDATORY",
        "title_en": "Contamination Prevention",
        "title_ar": "منع التلوث",
        "requirement_en": "Implement measures to prevent contamination of irrigation water (proper storage, protection from animal access, chemical isolation).",
        "requirement_ar": "تنفيذ تدابير لمنع تلوث مياه الري (التخزين الصحيح، الحماية من وصول الحيوانات، عزل المواد الكيميائية).",
        "guidance_en": "Cover water storage tanks, fence water sources, maintain buffer zones around wells (minimum 50m from contamination sources).",
        "guidance_ar": "تغطية خزانات تخزين المياه، سياج مصادر المياه، الحفاظ على مناطق عازلة حول الآبار (50 متراً على الأقل من مصادر التلوث).",
        "verification_en": "Field inspection, protection infrastructure",
        "verification_ar": "الفحص الميداني، البنية التحتية للحماية",
    },
    {
        "item_id": "WQ.04",
        "category": "WATER_QUALITY",
        "compliance_level": "RECOMMENDED",
        "title_en": "Water Treatment Systems",
        "title_ar": "أنظمة معالجة المياه",
        "requirement_en": "Install water treatment systems (filtration, UV, chlorination) where water quality does not meet standards.",
        "requirement_ar": "تركيب أنظمة معالجة المياه (الترشيح، الأشعة فوق البنفسجية، الكلورة) حيث لا تلبي جودة المياه المعايير.",
        "guidance_en": "For recycled water: multi-stage filtration + UV treatment. For high salinity: consider desalination or blending with fresher sources.",
        "guidance_ar": "للمياه المعاد تدويرها: ترشيح متعدد المراحل + معالجة بالأشعة فوق البنفسجية. للملوحة العالية: النظر في التحلية أو الخلط مع مصادر أنقى.",
        "verification_en": "Treatment system documentation, operational records",
        "verification_ar": "وثائق نظام المعالجة، سجلات التشغيل",
    },
    # ==================== LEGAL COMPLIANCE ====================
    {
        "item_id": "LC.01",
        "category": "LEGAL_COMPLIANCE",
        "compliance_level": "MANDATORY",
        "title_en": "Water Extraction Permits",
        "title_ar": "تصاريح استخراج المياه",
        "requirement_en": "Valid permits/licenses must be held for all water extraction (wells, boreholes, surface water abstraction).",
        "requirement_ar": "يجب حيازة تصاريح/تراخيص صالحة لجميع عمليات استخراج المياه (الآبار، الحفر، استخلاص المياه السطحية).",
        "guidance_en": "Obtain permits from relevant water authority. Ensure permits are current and cover actual extraction volumes.",
        "guidance_ar": "الحصول على التصاريح من السلطة المائية ذات الصلة. التأكد من أن التصاريح حالية وتغطي أحجام الاستخراج الفعلية.",
        "verification_en": "Permit documents, renewal dates, compliance with permit conditions",
        "verification_ar": "وثائق التصريح، تواريخ التجديد، الامتثال لشروط التصريح",
        "yemen_context": "In Yemen, permits from National Water Resources Authority (NWRA) or local water authorities.",
    },
    {
        "item_id": "LC.02",
        "category": "LEGAL_COMPLIANCE",
        "compliance_level": "MANDATORY",
        "title_en": "Extraction Limits Compliance",
        "title_ar": "الامتثال لحدود الاستخراج",
        "requirement_en": "Water extraction must not exceed permitted limits. Records must demonstrate compliance.",
        "requirement_ar": "يجب ألا يتجاوز استخراج المياه الحدود المسموح بها. يجب أن توضح السجلات الامتثال.",
        "guidance_en": "Compare monthly extraction volumes against permit limits. Alert system if approaching 90% of limit.",
        "guidance_ar": "مقارنة أحجام الاستخراج الشهرية بحدود التصريح. نظام تنبيه عند الاقتراب من 90% من الحد.",
        "verification_en": "Extraction records, permit documents, alert logs",
        "verification_ar": "سجلات الاستخراج، وثائق التصريح، سجلات التنبيه",
    },
    {
        "item_id": "LC.03",
        "category": "LEGAL_COMPLIANCE",
        "compliance_level": "MANDATORY",
        "title_en": "Environmental Flow Requirements",
        "title_ar": "متطلبات التدفق البيئي",
        "requirement_en": "For surface water sources, maintain minimum environmental flows as required by regulations.",
        "requirement_ar": "بالنسبة لمصادر المياه السطحية، الحفاظ على الحد الأدنى من التدفقات البيئية كما هو مطلوب بموجب اللوائح.",
        "guidance_en": "Do not extract water when river flow is below environmental minimum. Typically 10-30% of average annual flow.",
        "guidance_ar": "عدم استخراج المياه عندما يكون تدفق النهر أقل من الحد الأدنى البيئي. عادة 10-30% من متوسط التدفق السنوي.",
        "verification_en": "Flow monitoring data, extraction schedules",
        "verification_ar": "بيانات مراقبة التدفق، جداول الاستخراج",
    },
    {
        "item_id": "LC.04",
        "category": "LEGAL_COMPLIANCE",
        "compliance_level": "RECOMMENDED",
        "title_en": "Water Rights Documentation",
        "title_ar": "توثيق حقوق المياه",
        "requirement_en": "Maintain comprehensive documentation of water rights, including historical use, agreements with neighbors, and dispute resolution.",
        "requirement_ar": "الحفاظ على توثيق شامل لحقوق المياه، بما في ذلك الاستخدام التاريخي، والاتفاقيات مع الجيران، وحل النزاعات.",
        "guidance_en": "Keep records of traditional water rights (especially in Yemen where customary law applies), community agreements, and formal permits.",
        "guidance_ar": "الاحتفاظ بسجلات حقوق المياه التقليدية (خاصة في اليمن حيث ينطبق القانون العرفي)، والاتفاقات المجتمعية، والتصاريح الرسمية.",
        "verification_en": "Legal documents, community agreements, historical records",
        "verification_ar": "الوثائق القانونية، الاتفاقيات المجتمعية، السجلات التاريخية",
    },
    # ==================== MONITORING & RECORDS ====================
    {
        "item_id": "MR.01",
        "category": "MONITORING_RECORDS",
        "compliance_level": "MANDATORY",
        "title_en": "Water Use Records",
        "title_ar": "سجلات استخدام المياه",
        "requirement_en": "Maintain detailed records of all water use: date, source, volume, crop/field, irrigation method.",
        "requirement_ar": "الاحتفاظ بسجلات مفصلة لجميع استخدامات المياه: التاريخ، المصدر، الحجم، المحصول/الحقل، طريقة الري.",
        "guidance_en": "Record water use at least weekly. Use logbooks or digital systems. Retain records for minimum 3 years.",
        "guidance_ar": "تسجيل استخدام المياه أسبوعياً على الأقل. استخدام دفاتر السجلات أو الأنظمة الرقمية. الاحتفاظ بالسجلات لمدة 3 سنوات على الأقل.",
        "verification_en": "Water use logbooks, digital records, reports",
        "verification_ar": "دفاتر سجلات استخدام المياه، السجلات الرقمية، التقارير",
    },
    {
        "item_id": "MR.02",
        "category": "MONITORING_RECORDS",
        "compliance_level": "MANDATORY",
        "title_en": "Irrigation System Maintenance Records",
        "title_ar": "سجلات صيانة نظام الري",
        "requirement_en": "Keep records of all maintenance activities, repairs, and system performance evaluations.",
        "requirement_ar": "الاحتفاظ بسجلات جميع أنشطة الصيانة والإصلاحات وتقييمات أداء النظام.",
        "guidance_en": "Document inspections, filter cleaning, leak repairs, pump servicing, uniformity tests, efficiency evaluations.",
        "guidance_ar": "توثيق الفحوصات، تنظيف الفلاتر، إصلاحات التسرب، صيانة المضخات، اختبارات التوحيد، تقييمات الكفاءة.",
        "verification_en": "Maintenance logs, service invoices, test reports",
        "verification_ar": "سجلات الصيانة، فواتير الخدمة، تقارير الاختبار",
    },
    {
        "item_id": "MR.03",
        "category": "MONITORING_RECORDS",
        "compliance_level": "MANDATORY",
        "title_en": "Water Quality Test Records",
        "title_ar": "سجلات اختبار جودة المياه",
        "requirement_en": "Maintain all water quality test results with dates, parameters tested, and follow-up actions.",
        "requirement_ar": "الاحتفاظ بجميع نتائج اختبارات جودة المياه مع التواريخ والمعايير المختبرة والإجراءات المتابعة.",
        "guidance_en": "File laboratory reports systematically. Track trends over time. Document corrective actions for non-compliance.",
        "guidance_ar": "تقديم تقارير المختبر بشكل منهجي. تتبع الاتجاهات بمرور الوقت. توثيق الإجراءات التصحيحية لعدم الامتثال.",
        "verification_en": "Laboratory reports, trend analysis, corrective action logs",
        "verification_ar": "تقارير المختبر، تحليل الاتجاهات، سجلات الإجراءات التصحيحية",
    },
    {
        "item_id": "MR.04",
        "category": "MONITORING_RECORDS",
        "compliance_level": "RECOMMENDED",
        "title_en": "Digital Water Management System",
        "title_ar": "نظام إدارة المياه الرقمي",
        "requirement_en": "Implement digital system for water management (mobile app, cloud platform, SCADA integration).",
        "requirement_ar": "تنفيذ نظام رقمي لإدارة المياه (تطبيق الهاتف المحمول، منصة سحابية، تكامل SCADA).",
        "guidance_en": "Use SAHOOL irrigation-smart service or similar platform for real-time monitoring, alerts, and reporting.",
        "guidance_ar": "استخدام خدمة SAHOOL للري الذكي أو منصة مماثلة للمراقبة في الوقت الفعلي والتنبيهات وإعداد التقارير.",
        "verification_en": "System access, usage logs, automated reports",
        "verification_ar": "الوصول إلى النظام، سجلات الاستخدام، التقارير الآلية",
    },
    {
        "item_id": "MR.05",
        "category": "MONITORING_RECORDS",
        "compliance_level": "RECOMMENDED",
        "title_en": "Annual Water Audit",
        "title_ar": "تدقيق المياه السنوي",
        "requirement_en": "Conduct comprehensive annual water audit covering all aspects of water use, efficiency, and compliance.",
        "requirement_ar": "إجراء تدقيق شامل سنوي للمياه يغطي جميع جوانب استخدام المياه والكفاءة والامتثال.",
        "guidance_en": "Calculate water balance, benchmark against standards, identify improvement opportunities, set targets for next year.",
        "guidance_ar": "حساب توازن المياه، المقارنة بالمعايير، تحديد فرص التحسين، تحديد الأهداف للعام القادم.",
        "verification_en": "Annual audit report, improvement plan",
        "verification_ar": "تقرير التدقيق السنوي، خطة التحسين",
    },
]


# ==================== Helper Functions ====================


def get_spring_category(category_code: str) -> Optional[Dict]:
    """
    Get SPRING category details
    الحصول على تفاصيل فئة SPRING

    Args:
        category_code: Category code (e.g., "WATER_SOURCES")

    Returns:
        Category details or None if not found
    """
    return SPRING_CATEGORIES.get(category_code)


def get_spring_item(item_id: str) -> Optional[Dict]:
    """
    Get specific checklist item by ID
    الحصول على عنصر قائمة تحقق محدد بواسطة المعرف

    Args:
        item_id: Item ID (e.g., "WS.01")

    Returns:
        Checklist item or None if not found
    """
    for item in SPRING_CHECKLIST:
        if item["item_id"] == item_id:
            return item
    return None


def get_items_by_category(category: str) -> List[Dict]:
    """
    Get all checklist items for a specific category
    الحصول على جميع عناصر قائمة التحقق لفئة محددة

    Args:
        category: Category code

    Returns:
        List of checklist items
    """
    return [item for item in SPRING_CHECKLIST if item["category"] == category]


def get_mandatory_items() -> List[Dict]:
    """
    Get all mandatory checklist items
    الحصول على جميع عناصر قائمة التحقق الإلزامية

    Returns:
        List of mandatory items
    """
    return [
        item for item in SPRING_CHECKLIST if item["compliance_level"] == "MANDATORY"
    ]


def calculate_spring_compliance(
    compliant_items: List[str], all_items: Optional[List[str]] = None
) -> Dict[str, float]:
    """
    Calculate SPRING compliance score
    حساب درجة امتثال SPRING

    Args:
        compliant_items: List of compliant item IDs
        all_items: List of all assessed item IDs (defaults to all mandatory items)

    Returns:
        Compliance metrics
    """
    if all_items is None:
        all_items = [item["item_id"] for item in get_mandatory_items()]

    total_items = len(all_items)
    compliant_count = len([item for item in compliant_items if item in all_items])

    compliance_percentage = (
        (compliant_count / total_items * 100) if total_items > 0 else 0
    )

    # Calculate by category
    category_compliance = {}
    for category_code in SPRING_CATEGORIES.keys():
        category_items = [
            item["item_id"]
            for item in get_items_by_category(category_code)
            if item["item_id"] in all_items
        ]
        category_compliant = [
            item for item in compliant_items if item in category_items
        ]
        category_total = len(category_items)
        category_percentage = (
            (len(category_compliant) / category_total * 100)
            if category_total > 0
            else 0
        )
        category_compliance[category_code] = category_percentage

    return {
        "overall_compliance_percentage": round(compliance_percentage, 2),
        "compliant_items": compliant_count,
        "total_items": total_items,
        "non_compliant_items": total_items - compliant_count,
        "category_compliance": category_compliance,
    }


def get_yemen_specific_items() -> List[Dict]:
    """
    Get checklist items with Yemen-specific context
    الحصول على عناصر قائمة التحقق ذات السياق الخاص باليمن

    Returns:
        List of items with yemen_context field
    """
    return [item for item in SPRING_CHECKLIST if "yemen_context" in item]
