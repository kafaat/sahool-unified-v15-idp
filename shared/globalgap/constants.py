"""
GlobalGAP IFA v6 Constants
ثوابت GlobalGAP IFA v6

Constants and configuration values for IFA v6 compliance.
الثوابت وقيم التكوين للامتثال لـ IFA v6.
"""

from enum import Enum

# IFA Version
# إصدار IFA
IFA_VERSION = "6.0"
IFA_VERSION_FULL = "6.0-1_March2024"

# Certificate Validity
# صلاحية الشهادة
CERTIFICATE_VALIDITY_DAYS = 365
CERTIFICATE_RENEWAL_WARNING_DAYS = 90  # 3 months before expiry

# GGN (Global GAP Number) Format
# تنسيق رقم GlobalGAP
GGN_FORMAT_PATTERN = r"^40\d{11}$"  # 4000000000000 to 4099999999999
GGN_LENGTH = 13
GGN_PREFIX = "40"


# Compliance Levels
# مستويات الامتثال
class ComplianceLevel(str, Enum):
    """Compliance level enumeration / تعداد مستويات الامتثال"""

    MAJOR_MUST = "MAJOR_MUST"
    MINOR_MUST = "MINOR_MUST"
    RECOMMENDATION = "RECOMMENDATION"


COMPLIANCE_LEVELS = {
    "MAJOR_MUST": {
        "name_en": "Major Must",
        "name_ar": "إلزامي رئيسي",
        "description_en": "100% compliance required",
        "description_ar": "يجب الامتثال بنسبة 100%",
        "threshold": 100.0,
        "allows_non_conformance": False,
    },
    "MINOR_MUST": {
        "name_en": "Minor Must",
        "name_ar": "إلزامي ثانوي",
        "description_en": "95% compliance required",
        "description_ar": "يجب الامتثال بنسبة 95%",
        "threshold": 95.0,
        "allows_non_conformance": True,
    },
    "RECOMMENDATION": {
        "name_en": "Recommendation",
        "name_ar": "توصية",
        "description_en": "Recommended best practice",
        "description_ar": "ممارسة موصى بها",
        "threshold": 0.0,
        "allows_non_conformance": True,
    },
}

# Compliance Thresholds
# عتبات الامتثال
COMPLIANCE_THRESHOLDS = {
    "major_must": 100.0,  # Must be 100% compliant
    "minor_must": 95.0,  # Must be at least 95% compliant
    "overall": 95.0,  # Overall compliance threshold
}

# Minimum Requirements for Certification
# الحد الأدنى من المتطلبات للحصول على الشهادة
CERTIFICATION_MINIMUM_REQUIREMENTS = {
    "major_must_compliance": 100.0,
    "minor_must_compliance": 95.0,
    "max_non_conformances": {
        "critical": 0,
        "major": 0,
        "minor": 5,
    },
}


# Audit Types
# أنواع التدقيق
class AuditType(str, Enum):
    """Audit type enumeration / تعداد أنواع التدقيق"""

    INITIAL = "INITIAL"
    RENEWAL = "RENEWAL"
    SURVEILLANCE = "SURVEILLANCE"
    ANNOUNCED = "ANNOUNCED"
    UNANNOUNCED = "UNANNOUNCED"
    WITNESSED = "WITNESSED"


AUDIT_TYPES = {
    "INITIAL": {
        "name_en": "Initial Certification Audit",
        "name_ar": "تدقيق الشهادة الأولية",
        "description_en": "First-time certification audit",
        "description_ar": "تدقيق الشهادة للمرة الأولى",
    },
    "RENEWAL": {
        "name_en": "Renewal Audit",
        "name_ar": "تدقيق التجديد",
        "description_en": "Certificate renewal audit",
        "description_ar": "تدقيق تجديد الشهادة",
    },
    "SURVEILLANCE": {
        "name_en": "Surveillance Audit",
        "name_ar": "تدقيق المراقبة",
        "description_en": "Interim monitoring audit",
        "description_ar": "تدقيق مراقبة مؤقت",
    },
    "ANNOUNCED": {
        "name_en": "Announced Audit",
        "name_ar": "تدقيق معلن",
        "description_en": "Pre-scheduled audit",
        "description_ar": "تدقيق مجدول مسبقاً",
    },
    "UNANNOUNCED": {
        "name_en": "Unannounced Audit",
        "name_ar": "تدقيق غير معلن",
        "description_en": "Surprise audit",
        "description_ar": "تدقيق مفاجئ",
    },
}

# Certification Scopes
# نطاقات الشهادة
CERTIFICATION_SCOPES = {
    "FV": {
        "code": "FV",
        "name_en": "Fruit and Vegetables",
        "name_ar": "الفواكه والخضروات",
        "description_en": "Fresh fruit and vegetables production",
        "description_ar": "إنتاج الفواكه والخضروات الطازجة",
    },
    "CROPS_BASE": {
        "code": "CROPS_BASE",
        "name_en": "Crops Base",
        "name_ar": "المحاصيل الأساسية",
        "description_en": "General crops module",
        "description_ar": "وحدة المحاصيل العامة",
    },
}

# Checklist Categories
# فئات قائمة التحقق
CHECKLIST_CATEGORIES = {
    "FOOD_SAFETY": {
        "code": "FS",
        "name_en": "Food Safety and Quality",
        "name_ar": "سلامة الغذاء والجودة",
        "description_en": "Food safety management and quality assurance",
        "description_ar": "إدارة سلامة الغذاء وضمان الجودة",
        "order": 1,
    },
    "ENVIRONMENT": {
        "code": "ENV",
        "name_en": "Environmental Management",
        "name_ar": "الإدارة البيئية",
        "description_en": "Environmental protection and sustainability",
        "description_ar": "حماية البيئة والاستدامة",
        "order": 2,
    },
    "WORKERS_HEALTH_SAFETY": {
        "code": "WHS",
        "name_en": "Workers Health, Safety and Welfare",
        "name_ar": "صحة وسلامة ورفاهية العمال",
        "description_en": "Occupational health and safety management",
        "description_ar": "إدارة الصحة والسلامة المهنية",
        "order": 3,
    },
    "TRACEABILITY": {
        "code": "TRACE",
        "name_en": "Traceability and Segregation",
        "name_ar": "التتبع والفصل",
        "description_en": "Product traceability and segregation systems",
        "description_ar": "أنظمة تتبع وفصل المنتجات",
        "order": 4,
    },
    "FARM_MANAGEMENT": {
        "code": "FM",
        "name_en": "Farm Management",
        "name_ar": "إدارة المزرعة",
        "description_en": "General farm management and record keeping",
        "description_ar": "إدارة المزرعة العامة وحفظ السجلات",
        "order": 5,
    },
    "SITE_MANAGEMENT": {
        "code": "SM",
        "name_en": "Site Management",
        "name_ar": "إدارة الموقع",
        "description_en": "Site history and farm management",
        "description_ar": "تاريخ الموقع وإدارة المزرعة",
        "order": 6,
    },
    "SOIL_MANAGEMENT": {
        "code": "SOIL",
        "name_en": "Soil Management",
        "name_ar": "إدارة التربة",
        "description_en": "Soil conservation and fertility management",
        "description_ar": "حفظ التربة وإدارة الخصوبة",
        "order": 7,
    },
    "WATER_MANAGEMENT": {
        "code": "WATER",
        "name_en": "Water Management",
        "name_ar": "إدارة المياه",
        "description_en": "Water use and quality management",
        "description_ar": "إدارة استخدام وجودة المياه",
        "order": 8,
    },
    "CROP_PROTECTION": {
        "code": "CP",
        "name_en": "Crop Protection",
        "name_ar": "حماية المحاصيل",
        "description_en": "Integrated pest management and pesticide use",
        "description_ar": "الإدارة المتكاملة للآفات واستخدام المبيدات",
        "order": 9,
    },
    "HARVEST_HANDLING": {
        "code": "HH",
        "name_en": "Harvesting and Handling",
        "name_ar": "الحصاد والمناولة",
        "description_en": "Harvest and post-harvest handling",
        "description_ar": "معالجة الحصاد وما بعد الحصاد",
        "order": 10,
    },
}

# Non-Conformance Severity Levels
# مستويات خطورة عدم المطابقة
NON_CONFORMANCE_LEVELS = {
    "CRITICAL": {
        "name_en": "Critical",
        "name_ar": "حرج",
        "description_en": "Immediate risk to food safety or worker safety",
        "description_ar": "خطر فوري على سلامة الغذاء أو سلامة العمال",
        "action_required": "IMMEDIATE",
        "affects_certification": True,
    },
    "MAJOR": {
        "name_en": "Major",
        "name_ar": "رئيسي",
        "description_en": "Significant deviation from requirements",
        "description_ar": "انحراف كبير عن المتطلبات",
        "action_required": "WITHIN_30_DAYS",
        "affects_certification": True,
    },
    "MINOR": {
        "name_en": "Minor",
        "name_ar": "ثانوي",
        "description_en": "Minor deviation from best practices",
        "description_ar": "انحراف بسيط عن أفضل الممارسات",
        "action_required": "WITHIN_90_DAYS",
        "affects_certification": False,
    },
}

# Evidence Types
# أنواع الأدلة
EVIDENCE_TYPES = {
    "DOCUMENT": {
        "name_en": "Document",
        "name_ar": "مستند",
        "examples_en": ["Procedures, records, certificates"],
        "examples_ar": ["إجراءات، سجلات، شهادات"],
    },
    "OBSERVATION": {
        "name_en": "Physical Observation",
        "name_ar": "ملاحظة مادية",
        "examples_en": ["Site inspection, equipment check"],
        "examples_ar": ["فحص الموقع، فحص المعدات"],
    },
    "INTERVIEW": {
        "name_en": "Interview",
        "name_ar": "مقابلة",
        "examples_en": ["Staff interviews, management review"],
        "examples_ar": ["مقابلات الموظفين، مراجعة الإدارة"],
    },
    "TEST_RESULT": {
        "name_en": "Test Result",
        "name_ar": "نتيجة الاختبار",
        "examples_en": ["Lab analysis, water quality test"],
        "examples_ar": ["تحليل المختبر، اختبار جودة المياه"],
    },
    "PHOTO": {
        "name_en": "Photographic Evidence",
        "name_ar": "دليل فوتوغرافي",
        "examples_en": ["Site photos, equipment photos"],
        "examples_ar": ["صور الموقع، صور المعدات"],
    },
}

# Corrective Action Status
# حالة الإجراء التصحيحي
CORRECTIVE_ACTION_STATUS = {
    "PLANNED": {
        "name_en": "Planned",
        "name_ar": "مخطط",
        "description_en": "Action identified and planned",
        "description_ar": "تم تحديد الإجراء والتخطيط له",
    },
    "IN_PROGRESS": {
        "name_en": "In Progress",
        "name_ar": "قيد التنفيذ",
        "description_en": "Action being implemented",
        "description_ar": "جاري تنفيذ الإجراء",
    },
    "COMPLETED": {
        "name_en": "Completed",
        "name_ar": "مكتمل",
        "description_en": "Action completed, awaiting verification",
        "description_ar": "تم إكمال الإجراء، في انتظار التحقق",
    },
    "VERIFIED": {
        "name_en": "Verified",
        "name_ar": "تم التحقق منه",
        "description_en": "Action verified as effective",
        "description_ar": "تم التحقق من فعالية الإجراء",
    },
    "REJECTED": {
        "name_en": "Rejected",
        "name_ar": "مرفوض",
        "description_en": "Action not effective, needs revision",
        "description_ar": "الإجراء غير فعال، يحتاج للمراجعة",
    },
}

# Product Handling Types
# أنواع معالجة المنتجات
PRODUCT_HANDLING_TYPES = {
    "FRESH_PRODUCE": {
        "name_en": "Fresh Produce",
        "name_ar": "منتجات طازجة",
        "description_en": "Fresh fruits and vegetables",
        "description_ar": "فواكه وخضروات طازجة",
    },
    "PACKAGED": {
        "name_en": "Pre-packaged",
        "name_ar": "معبأة مسبقاً",
        "description_en": "Pre-packaged products",
        "description_ar": "منتجات معبأة مسبقاً",
    },
}

# Countries (for farm location)
# البلدان (لموقع المزرعة)
COUNTRIES = {
    "SA": {
        "code": "SA",
        "name_en": "Saudi Arabia",
        "name_ar": "المملكة العربية السعودية",
        "region": "Middle East",
    },
    "AE": {
        "code": "AE",
        "name_en": "United Arab Emirates",
        "name_ar": "الإمارات العربية المتحدة",
        "region": "Middle East",
    },
    "EG": {
        "code": "EG",
        "name_en": "Egypt",
        "name_ar": "مصر",
        "region": "Middle East",
    },
    "JO": {
        "code": "JO",
        "name_en": "Jordan",
        "name_ar": "الأردن",
        "region": "Middle East",
    },
}

# Time Periods
# الفترات الزمنية
TIME_PERIODS = {
    "IMMEDIATE": {
        "name_en": "Immediate",
        "name_ar": "فوري",
        "days": 0,
    },
    "WITHIN_7_DAYS": {
        "name_en": "Within 7 Days",
        "name_ar": "خلال 7 أيام",
        "days": 7,
    },
    "WITHIN_30_DAYS": {
        "name_en": "Within 30 Days",
        "name_ar": "خلال 30 يوماً",
        "days": 30,
    },
    "WITHIN_90_DAYS": {
        "name_en": "Within 90 Days",
        "name_ar": "خلال 90 يوماً",
        "days": 90,
    },
    "ANNUAL": {
        "name_en": "Annual",
        "name_ar": "سنوي",
        "days": 365,
    },
}
