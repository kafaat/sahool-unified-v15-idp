"""
Sahool Vision - Diagnosis Data Models
نماذج بيانات التشخيص
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from .disease import DiseaseSeverity, CropType, Treatment


class DiagnosisRequest(BaseModel):
    """طلب تشخيص"""
    field_id: Optional[str] = None
    crop_type: Optional[CropType] = None
    symptoms_description: Optional[str] = None
    location_governorate: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    farmer_id: Optional[str] = None


class DiagnosisResult(BaseModel):
    """نتيجة التشخيص"""
    diagnosis_id: str = Field(description="معرف التشخيص الفريد")
    timestamp: datetime = Field(description="وقت التشخيص")

    # Disease information
    disease_name: str = Field(description="اسم المرض بالإنجليزية")
    disease_name_ar: str = Field(description="اسم المرض بالعربية")
    disease_description: str = Field(description="وصف المرض")
    disease_description_ar: str = Field(description="وصف المرض بالعربية")

    # Confidence and severity
    confidence: float = Field(ge=0, le=1, description="نسبة الثقة في التشخيص")
    severity: DiseaseSeverity = Field(description="مستوى خطورة الإصابة")
    affected_area_percent: float = Field(ge=0, le=100, description="نسبة المنطقة المصابة")

    # Crop information
    detected_crop: CropType = Field(description="نوع المحصول المكتشف")
    growth_stage: Optional[str] = Field(None, description="مرحلة النمو")

    # Treatment recommendations
    treatments: List[Treatment] = Field(description="العلاجات المقترحة")
    urgent_action_required: bool = Field(description="هل يتطلب تدخل عاجل")

    # Expert review
    needs_expert_review: bool = Field(description="يحتاج مراجعة خبير")
    expert_review_reason: Optional[str] = Field(None, description="سبب طلب مراجعة الخبير")

    # Additional metadata
    weather_consideration: Optional[str] = Field(None, description="اعتبارات الطقس")
    prevention_tips: List[str] = Field(default_factory=list, description="نصائح الوقاية")
    prevention_tips_ar: List[str] = Field(default_factory=list, description="نصائح الوقاية بالعربية")

    # Image URL (for Admin Dashboard)
    image_url: Optional[str] = Field(None, description="رابط الصورة المحفوظة")


class DiagnosisHistoryRecord(BaseModel):
    """سجل تشخيص محفوظ للوحة التحكم"""
    id: str
    image_url: str
    thumbnail_url: Optional[str] = None
    disease_id: str
    disease_name: str
    disease_name_ar: str
    confidence: float
    severity: str
    crop_type: str
    field_id: Optional[str] = None
    governorate: Optional[str] = None
    location: Optional[dict] = None  # {lat, lng}
    status: str = "pending"  # pending, confirmed, rejected, treated
    expert_notes: Optional[str] = None
    timestamp: datetime
    farmer_id: Optional[str] = None
    updated_at: Optional[datetime] = None


class BatchDiagnosisResult(BaseModel):
    """نتيجة تشخيص دفعة من الصور"""
    batch_id: str
    field_id: Optional[str] = None
    total_images: int
    processed: int
    results: List[dict]
    summary: dict
