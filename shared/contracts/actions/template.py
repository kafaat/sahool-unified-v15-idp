"""
SAHOOL Action Template
قالب الإجراء الموحد - Field-First

كل تحليل يُنتج قالب إجراء يحتوي على:
- ماذا (What): وصف الإجراء
- لماذا (Why): مصدر التحليل والثقة
- متى (When): الاستعجال والموعد
- كيف (How): الخطوات والموارد
- Fallback: تعليمات للعمل بدون اتصال
"""

import uuid
from datetime import date, datetime, time
from typing import Any

from pydantic import BaseModel, Field

from .types import ActionStatus, ActionType, ResourceType, UrgencyLevel


class TimeWindow(BaseModel):
    """نافذة الوقت المثالية للتنفيذ"""

    start_date: date
    end_date: date
    preferred_time_start: time | None = None
    preferred_time_end: time | None = None
    avoid_conditions: list[str] = Field(
        default_factory=list,
        description="ظروف يجب تجنبها مثل: rain, high_wind, extreme_heat",
    )


class Resource(BaseModel):
    """مورد مطلوب للإجراء"""

    resource_type: ResourceType
    name_ar: str
    name_en: str
    quantity: float
    unit: str
    unit_ar: str
    estimated_cost: float | None = None
    currency: str = "YER"
    notes: str | None = None


class ActionStep(BaseModel):
    """خطوة في الإجراء"""

    step_number: int
    title_ar: str
    title_en: str
    description_ar: str
    description_en: str
    duration_minutes: int | None = None
    requires_photo: bool = False
    requires_confirmation: bool = True
    safety_notes_ar: str | None = None
    safety_notes_en: str | None = None


class ActionTemplate(BaseModel):
    """
    قالب الإجراء الموحد

    هذا القالب هو العقد بين خدمات التحليل والميدان.
    كل توصية يجب أن تُترجم إلى هذا القالب.
    """

    # === Identity ===
    action_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="معرف فريد للإجراء"
    )
    action_type: ActionType = Field(..., description="نوع الإجراء")

    # === What (ماذا) ===
    title_ar: str = Field(..., min_length=3, max_length=200)
    title_en: str = Field(..., min_length=3, max_length=200)
    description_ar: str = Field(..., min_length=10)
    description_en: str = Field(..., min_length=10)
    summary_ar: str | None = Field(
        None, max_length=500, description="ملخص قصير للعرض في الإشعارات"
    )

    # === Why (لماذا) - Analysis Source ===
    source_service: str = Field(
        ..., description="اسم الخدمة المصدر مثل: satellite-service, crop-health-ai"
    )
    source_analysis_id: str | None = Field(None, description="معرف التحليل المصدر")
    source_analysis_type: str | None = Field(
        None, description="نوع التحليل مثل: ndvi_drop, disease_detected"
    )
    confidence: float = Field(
        ..., ge=0, le=1, description="مستوى الثقة في التوصية (0-1)"
    )
    reasoning_ar: str | None = Field(None, description="شرح سبب التوصية بالعربية")
    reasoning_en: str | None = Field(None, description="شرح سبب التوصية بالإنجليزية")

    # === When (متى) ===
    urgency: UrgencyLevel = Field(..., description="مستوى الاستعجال")
    deadline: datetime | None = Field(None, description="الموعد النهائي للتنفيذ")
    optimal_window: TimeWindow | None = Field(
        None, description="النافذة الزمنية المثالية"
    )

    # === Where (أين) ===
    field_id: str = Field(..., description="معرف الحقل")
    zone_ids: list[str] = Field(
        default_factory=list, description="معرفات المناطق المحددة داخل الحقل"
    )
    geometry: dict[str, Any] | None = Field(
        None, description="GeoJSON للمنطقة المستهدفة"
    )

    # === How (كيف) ===
    steps: list[ActionStep] = Field(default_factory=list, description="خطوات التنفيذ")
    resources_needed: list[Resource] = Field(
        default_factory=list, description="الموارد المطلوبة"
    )
    estimated_duration_minutes: int = Field(
        ..., gt=0, description="الوقت المتوقع للتنفيذ بالدقائق"
    )
    estimated_cost: float | None = Field(None, description="التكلفة التقديرية")
    cost_currency: str = "YER"

    # === Field-First: Offline Support ===
    offline_executable: bool = Field(
        default=True, description="هل يمكن تنفيذه بدون اتصال؟"
    )
    fallback_instructions_ar: str = Field(
        ..., description="تعليمات Fallback بالعربية في حال عدم الاتصال"
    )
    fallback_instructions_en: str = Field(
        ..., description="تعليمات Fallback بالإنجليزية"
    )
    requires_sync_before: bool = Field(
        default=False, description="هل يتطلب مزامنة قبل التنفيذ؟"
    )

    # === Metadata ===
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    status: ActionStatus = Field(default=ActionStatus.PENDING)
    priority_score: float = Field(
        default=0, ge=0, le=100, description="درجة الأولوية للترتيب (0-100)"
    )
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    # === Tracking ===
    tenant_id: str | None = None
    created_by_service: str | None = None
    version: str = "1.0"

    class Config:
        json_schema_extra = {
            "example": {
                "action_id": "act_123e4567-e89b-12d3-a456-426614174000",
                "action_type": "irrigation",
                "title_ar": "ري الحقل - انخفاض رطوبة التربة",
                "title_en": "Field Irrigation - Low Soil Moisture",
                "description_ar": "رطوبة التربة انخفضت إلى 25%، يُنصح بالري خلال 24 ساعة",
                "description_en": "Soil moisture dropped to 25%, irrigation recommended within 24 hours",
                "source_service": "irrigation-smart",
                "confidence": 0.92,
                "urgency": "high",
                "field_id": "field_abc123",
                "estimated_duration_minutes": 120,
                "offline_executable": True,
                "fallback_instructions_ar": "في حال عدم توفر البيانات، قم بري الحقل لمدة ساعتين في الصباح الباكر",
                "fallback_instructions_en": "If data unavailable, irrigate field for 2 hours in early morning",
            }
        }

    def calculate_priority_score(self) -> float:
        """حساب درجة الأولوية بناءً على الاستعجال والثقة"""
        urgency_weights = {
            UrgencyLevel.CRITICAL: 40,
            UrgencyLevel.HIGH: 30,
            UrgencyLevel.MEDIUM: 20,
            UrgencyLevel.LOW: 10,
        }
        base_score = urgency_weights.get(self.urgency, 10)
        confidence_bonus = self.confidence * 30

        # Deadline proximity bonus
        deadline_bonus = 0
        if self.deadline:
            hours_until = (self.deadline - datetime.utcnow()).total_seconds() / 3600
            if hours_until < 24:
                deadline_bonus = 30
            elif hours_until < 72:
                deadline_bonus = 20
            elif hours_until < 168:
                deadline_bonus = 10

        self.priority_score = min(100, base_score + confidence_bonus + deadline_bonus)
        return self.priority_score

    def to_notification_payload(self) -> dict[str, Any]:
        """تحويل إلى حمولة إشعار"""
        return {
            "action_id": self.action_id,
            "type": self.action_type.value,
            "title": self.title_ar,
            "summary": self.summary_ar or self.description_ar[:100],
            "urgency": self.urgency.value,
            "urgency_label": self.urgency.label_ar,
            "field_id": self.field_id,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "confidence": self.confidence,
            "offline_executable": self.offline_executable,
        }

    def to_task_card(self) -> dict[str, Any]:
        """تحويل إلى بطاقة مهمة للعرض"""
        return {
            "id": self.action_id,
            "type": self.action_type.value,
            "title_ar": self.title_ar,
            "title_en": self.title_en,
            "urgency": {
                "level": self.urgency.value,
                "label_ar": self.urgency.label_ar,
                "color": self._get_urgency_color(),
            },
            "field_id": self.field_id,
            "duration_minutes": self.estimated_duration_minutes,
            "steps_count": len(self.steps),
            "resources_count": len(self.resources_needed),
            "confidence_percent": int(self.confidence * 100),
            "status": self.status.value,
            "offline_ready": self.offline_executable,
            "created_at": self.created_at.isoformat(),
        }

    def _get_urgency_color(self) -> str:
        colors = {
            UrgencyLevel.LOW: "#22C55E",  # green
            UrgencyLevel.MEDIUM: "#EAB308",  # yellow
            UrgencyLevel.HIGH: "#F97316",  # orange
            UrgencyLevel.CRITICAL: "#EF4444",  # red
        }
        return colors.get(self.urgency, "#6B7280")
