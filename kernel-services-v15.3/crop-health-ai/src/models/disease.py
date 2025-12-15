"""
Sahool Vision - Disease Data Models
نماذج بيانات الأمراض
"""

from enum import Enum
from typing import List
from pydantic import BaseModel


class DiseaseSeverity(str, Enum):
    """مستوى خطورة المرض"""
    HEALTHY = "healthy"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CropType(str, Enum):
    """أنواع المحاصيل المدعومة"""
    WHEAT = "wheat"          # قمح
    TOMATO = "tomato"        # طماطم
    POTATO = "potato"        # بطاطس
    CORN = "corn"            # ذرة
    GRAPE = "grape"          # عنب
    APPLE = "apple"          # تفاح
    COFFEE = "coffee"        # قهوة (بن)
    DATE_PALM = "date_palm"  # نخيل
    MANGO = "mango"          # مانجو
    CITRUS = "citrus"        # حمضيات
    COTTON = "cotton"        # قطن
    SORGHUM = "sorghum"      # ذرة رفيعة
    UNKNOWN = "unknown"


class TreatmentType(str, Enum):
    """نوع العلاج"""
    FUNGICIDE = "fungicide"        # مبيد فطري
    INSECTICIDE = "insecticide"    # مبيد حشري
    HERBICIDE = "herbicide"        # مبيد أعشاب
    FERTILIZER = "fertilizer"      # سماد
    IRRIGATION = "irrigation"      # ري
    PRUNING = "pruning"            # تقليم
    NONE = "none"                  # لا يحتاج علاج


class Treatment(BaseModel):
    """معلومات العلاج المقترح"""
    treatment_type: TreatmentType
    product_name: str
    product_name_ar: str
    dosage: str
    dosage_ar: str
    application_method: str
    application_method_ar: str
    frequency: str
    frequency_ar: str
    precautions: List[str] = []
    precautions_ar: List[str] = []


class DiseaseInfo(BaseModel):
    """معلومات المرض"""
    disease_id: str
    name: str
    name_ar: str
    description: str
    description_ar: str
    crop: CropType
    severity_default: DiseaseSeverity
    treatments: List[Treatment] = []
    prevention: List[str] = []
    prevention_ar: List[str] = []
