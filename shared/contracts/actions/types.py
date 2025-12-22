"""
SAHOOL Action Types
أنواع الإجراءات والحالات
"""

from enum import Enum


class ActionType(str, Enum):
    """أنواع الإجراءات الميدانية"""

    # Irrigation - الري
    IRRIGATION = "irrigation"
    IRRIGATION_EMERGENCY = "irrigation_emergency"
    IRRIGATION_SCHEDULE = "irrigation_schedule"

    # Fertilization - التسميد
    FERTILIZATION = "fertilization"
    FERTILIZATION_NPK = "fertilization_npk"
    FERTILIZATION_ORGANIC = "fertilization_organic"
    FERTILIZATION_FOLIAR = "fertilization_foliar"

    # Plant Protection - الوقاية
    SPRAY = "spray"
    SPRAY_FUNGICIDE = "spray_fungicide"
    SPRAY_INSECTICIDE = "spray_insecticide"
    SPRAY_HERBICIDE = "spray_herbicide"

    # Inspection - الفحص
    INSPECTION = "inspection"
    INSPECTION_DISEASE = "inspection_disease"
    INSPECTION_PEST = "inspection_pest"
    INSPECTION_SOIL = "inspection_soil"

    # Harvest - الحصاد
    HARVEST = "harvest"
    HARVEST_PARTIAL = "harvest_partial"
    HARVEST_FULL = "harvest_full"

    # Maintenance - الصيانة
    MAINTENANCE = "maintenance"
    PRUNING = "pruning"
    WEEDING = "weeding"

    # Monitoring - المراقبة
    MONITORING = "monitoring"
    SENSOR_CHECK = "sensor_check"
    PHOTO_CAPTURE = "photo_capture"


class ActionStatus(str, Enum):
    """حالات الإجراء"""

    PENDING = "pending"           # في الانتظار
    SCHEDULED = "scheduled"       # مجدول
    IN_PROGRESS = "in_progress"   # قيد التنفيذ
    COMPLETED = "completed"       # مكتمل
    SKIPPED = "skipped"           # تم تخطيه
    FAILED = "failed"             # فشل
    EXPIRED = "expired"           # انتهت صلاحيته


class UrgencyLevel(str, Enum):
    """مستويات الاستعجال"""

    LOW = "low"           # منخفض - يمكن الانتظار
    MEDIUM = "medium"     # متوسط - خلال أيام
    HIGH = "high"         # عالي - خلال 24 ساعة
    CRITICAL = "critical" # حرج - فوري

    @property
    def label_ar(self) -> str:
        labels = {
            "low": "منخفض",
            "medium": "متوسط",
            "high": "عالي",
            "critical": "حرج"
        }
        return labels[self.value]

    @property
    def max_delay_hours(self) -> int:
        delays = {
            "low": 168,      # أسبوع
            "medium": 72,    # 3 أيام
            "high": 24,      # يوم
            "critical": 4    # 4 ساعات
        }
        return delays[self.value]


class ResourceType(str, Enum):
    """أنواع الموارد المطلوبة"""

    # Water - المياه
    WATER = "water"

    # Fertilizers - الأسمدة
    FERTILIZER_UREA = "fertilizer_urea"
    FERTILIZER_DAP = "fertilizer_dap"
    FERTILIZER_NPK = "fertilizer_npk"
    FERTILIZER_POTASSIUM = "fertilizer_potassium"
    FERTILIZER_ORGANIC = "fertilizer_organic"

    # Pesticides - المبيدات
    PESTICIDE_FUNGICIDE = "pesticide_fungicide"
    PESTICIDE_INSECTICIDE = "pesticide_insecticide"
    PESTICIDE_HERBICIDE = "pesticide_herbicide"

    # Equipment - المعدات
    EQUIPMENT_SPRAYER = "equipment_sprayer"
    EQUIPMENT_TRACTOR = "equipment_tractor"
    EQUIPMENT_HARVESTER = "equipment_harvester"

    # Labor - العمالة
    LABOR_SKILLED = "labor_skilled"
    LABOR_UNSKILLED = "labor_unskilled"

    # Other
    OTHER = "other"
