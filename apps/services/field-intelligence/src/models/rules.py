"""
نماذج قواعد الأتمتة - Automation Rules Models
Field automation and event-triggered rules
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RuleStatus(str, Enum):
    """حالات القاعدة - Rule Status"""

    ACTIVE = "active"  # نشطة
    INACTIVE = "inactive"  # غير نشطة
    PAUSED = "paused"  # متوقفة مؤقتاً


class ConditionOperator(str, Enum):
    """معاملات الشرط - Condition Operators"""

    EQUALS = "equals"  # يساوي
    NOT_EQUALS = "not_equals"  # لا يساوي
    GREATER_THAN = "greater_than"  # أكبر من
    LESS_THAN = "less_than"  # أقل من
    GREATER_EQUAL = "greater_equal"  # أكبر من أو يساوي
    LESS_EQUAL = "less_equal"  # أقل من أو يساوي
    CONTAINS = "contains"  # يحتوي
    IN = "in"  # ضمن
    BETWEEN = "between"  # بين


class ActionType(str, Enum):
    """أنواع الإجراءات - Action Types"""

    CREATE_TASK = "create_task"  # إنشاء مهمة
    SEND_NOTIFICATION = "send_notification"  # إرسال إشعار
    CREATE_ALERT = "create_alert"  # إنشاء تنبيه
    UPDATE_FIELD = "update_field"  # تحديث حقل
    TRIGGER_IRRIGATION = "trigger_irrigation"  # تفعيل الري
    WEBHOOK = "webhook"  # نداء ويب هوك
    LOG_EVENT = "log_event"  # تسجيل الحدث


# ═══════════════════════════════════════════════════════════════════════════════
# Rule Condition Models
# ═══════════════════════════════════════════════════════════════════════════════


class RuleCondition(BaseModel):
    """
    شرط القاعدة
    Rule Condition
    """

    field: str = Field(..., description="الحقل للفحص (e.g., 'event_type', 'severity')")
    operator: ConditionOperator
    value: Any = Field(..., description="القيمة للمقارنة")
    value_type: str = Field(
        default="string", description="نوع البيانات: string, number, boolean, list"
    )


class RuleConditionGroup(BaseModel):
    """
    مجموعة شروط (AND/OR)
    Condition Group with logical operators
    """

    logic: str = Field(default="AND", description="المعامل المنطقي: AND أو OR")
    conditions: list[RuleCondition] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# Action Configuration Models
# ═══════════════════════════════════════════════════════════════════════════════


class TaskConfig(BaseModel):
    """
    إعداد المهمة التلقائية
    Auto-Task Configuration
    """

    title: str
    title_ar: str | None = None
    description: str
    description_ar: str | None = None
    task_type: str  # من TaskType في task-service
    priority: str = "medium"
    assign_to: str | None = None  # user_id أو "field_owner"
    due_hours: int = Field(default=24, description="المهمة مستحقة بعد كم ساعة من الحدث")
    metadata: dict[str, Any] = Field(default_factory=dict)


class NotificationConfig(BaseModel):
    """
    إعداد الإشعار
    Notification Configuration
    """

    channels: list[str] = Field(
        default_factory=lambda: ["push"],
        description="قنوات الإشعار: push, sms, email, whatsapp",
    )
    recipients: list[str] = Field(
        default_factory=list, description="معرفات المستلمين أو 'field_owner'"
    )
    title: str
    title_ar: str | None = None
    message: str
    message_ar: str | None = None
    priority: str = "normal"  # low, normal, high, urgent
    template_id: str | None = None


class AlertConfig(BaseModel):
    """
    إعداد التنبيه
    Alert Configuration
    """

    alert_type: str
    severity: str  # low, medium, high, critical
    title: str
    title_ar: str | None = None
    message: str
    message_ar: str | None = None
    recommendations: list[str] = Field(default_factory=list)
    recommendations_ar: list[str] = Field(default_factory=list)
    expire_hours: int | None = None


class WebhookConfig(BaseModel):
    """
    إعداد Webhook
    Webhook Configuration
    """

    url: str
    method: str = "POST"
    headers: dict[str, str] = Field(default_factory=dict)
    body_template: dict[str, Any] | None = None
    timeout_seconds: int = 10
    retry_count: int = 3


class ActionConfig(BaseModel):
    """
    إعداد الإجراء
    Action Configuration
    """

    action_type: ActionType
    enabled: bool = True
    task_config: TaskConfig | None = None
    notification_config: NotificationConfig | None = None
    alert_config: AlertConfig | None = None
    webhook_config: WebhookConfig | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════════
# Rule Models
# ═══════════════════════════════════════════════════════════════════════════════


class Rule(BaseModel):
    """
    قاعدة الأتمتة
    Automation Rule
    """

    rule_id: str
    tenant_id: str
    name: str
    name_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    status: RuleStatus = RuleStatus.ACTIVE
    field_ids: list[str] = Field(
        default_factory=list, description="الحقول المطبقة عليها القاعدة (فارغ = كل الحقول)"
    )
    event_types: list[str] = Field(
        default_factory=list, description="أنواع الأحداث التي تفعل القاعدة"
    )
    conditions: RuleConditionGroup
    actions: list[ActionConfig] = Field(default_factory=list)
    cooldown_minutes: int = Field(
        default=60,
        description="المدة الدنيا بين التفعيلات بالدقائق (لتجنب التكرار الزائد)",
    )
    priority: int = Field(default=100, description="أولوية تنفيذ القاعدة (أقل = أعلى)")
    created_at: datetime
    updated_at: datetime
    last_triggered_at: datetime | None = None
    trigger_count: int = Field(default=0, description="عدد مرات التفعيل")
    metadata: dict[str, Any] = Field(default_factory=dict)


class RuleCreate(BaseModel):
    """
    إنشاء قاعدة جديدة
    Create New Rule
    """

    tenant_id: str
    name: str
    name_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    status: RuleStatus = RuleStatus.ACTIVE
    field_ids: list[str] = Field(default_factory=list)
    event_types: list[str] = Field(default_factory=list)
    conditions: RuleConditionGroup
    actions: list[ActionConfig]
    cooldown_minutes: int = 60
    priority: int = 100
    metadata: dict[str, Any] = Field(default_factory=dict)


class RuleUpdate(BaseModel):
    """
    تحديث القاعدة
    Update Rule
    """

    name: str | None = None
    name_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    status: RuleStatus | None = None
    field_ids: list[str] | None = None
    event_types: list[str] | None = None
    conditions: RuleConditionGroup | None = None
    actions: list[ActionConfig] | None = None
    cooldown_minutes: int | None = None
    priority: int | None = None
    metadata: dict[str, Any] | None = None


class RuleResponse(BaseModel):
    """
    استجابة القاعدة
    Rule Response
    """

    rule_id: str
    tenant_id: str
    name: str
    name_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    status: RuleStatus
    field_ids: list[str]
    event_types: list[str]
    conditions: RuleConditionGroup
    actions: list[ActionConfig]
    cooldown_minutes: int
    priority: int
    created_at: datetime
    updated_at: datetime
    last_triggered_at: datetime | None = None
    trigger_count: int
    metadata: dict[str, Any]


class RuleExecutionResult(BaseModel):
    """
    نتيجة تنفيذ القاعدة
    Rule Execution Result
    """

    rule_id: str
    event_id: str
    success: bool
    executed_at: datetime
    actions_executed: int
    actions_failed: int
    execution_details: list[dict[str, Any]] = Field(default_factory=list)
    error_message: str | None = None
