# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Pydantic schemas for LLM Orchestrator Service.
مخططات Pydantic لخدمة تنسيق نماذج اللغة الكبيرة.

These schemas define the request/response models for orchestrating
AI agents across the SAHOOL platform.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class IntentType(str, Enum):
    """
    Types of user intents that can be classified.
    أنواع نوايا المستخدم التي يمكن تصنيفها.
    """

    CROP_DISEASE = "crop_disease"
    IRRIGATION_QUERY = "irrigation_query"
    FERTILIZER_ADVICE = "fertilizer_advice"
    PEST_DETECTION = "pest_detection"
    WEATHER_QUERY = "weather_query"
    YIELD_PREDICTION = "yield_prediction"
    FIELD_ANALYSIS = "field_analysis"
    GENERAL_ADVISORY = "general_advisory"
    TERRAIN_ANALYSIS = "terrain_analysis"
    HYDROLOGY_QUERY = "hydrology_query"
    LEVELING_QUERY = "leveling_query"
    IMAGE_ANALYSIS = "image_analysis"
    MULTI_INTENT = "multi_intent"
    UNKNOWN = "unknown"


class ActionType(str, Enum):
    """
    Types of automated actions that can be triggered.
    أنواع الإجراءات التلقائية التي يمكن تنفيذها.
    """

    SCHEDULE_IRRIGATION = "schedule_irrigation"
    APPLY_FERTILIZER = "apply_fertilizer"
    TRIGGER_PEST_SCAN = "trigger_pest_scan"
    GENERATE_REPORT = "generate_report"
    SEND_ALERT = "send_alert"
    UPDATE_FIELD_STATUS = "update_field_status"
    SCHEDULE_SCOUTING = "schedule_scouting"
    CREATE_TASK = "create_task"


class ExecutionMode(str, Enum):
    """
    Execution modes for agent calls.
    أوضاع تنفيذ استدعاءات الوكلاء.
    """

    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    CONDITIONAL = "conditional"


class UserIntent(BaseModel):
    """
    User intent input for orchestration.
    مدخلات نية المستخدم للتنسيق.
    """

    text: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User's input text | نص إدخال المستخدم",
    )
    image_base64: str | None = Field(
        default=None,
        description="Optional base64-encoded image for vision analysis | صورة مشفرة بـ base64 اختيارية",
    )
    image_url: str | None = Field(
        default=None,
        description="Optional image URL for vision analysis | رابط صورة اختياري",
    )
    language: Literal["ar", "en", "auto"] = Field(
        default="auto",
        description="Preferred language for response | اللغة المفضلة للاستجابة",
    )
    field_id: str | None = Field(
        default=None,
        description="Field ID for context | معرف الحقل للسياق",
    )
    tenant_id: str | None = Field(
        default=None,
        description="Tenant ID for multi-tenancy | معرف المستأجر",
    )
    context: dict[str, Any] | None = Field(
        default=None,
        description="Additional context data | بيانات سياق إضافية",
    )
    correlation_id: str | None = Field(
        default=None,
        description="Correlation ID for tracing | معرف الارتباط للتتبع",
    )


class IntentClassification(BaseModel):
    """
    Result of intent classification.
    نتيجة تصنيف النية.
    """

    intent_type: IntentType = Field(
        ...,
        description="Classified intent type | نوع النية المصنفة",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0-1) | درجة الثقة",
    )
    entities: dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted entities | الكيانات المستخرجة",
    )
    secondary_intents: list[IntentType] = Field(
        default_factory=list,
        description="Secondary detected intents | النوايا الثانوية المكتشفة",
    )
    language_detected: str = Field(
        default="ar",
        description="Detected language | اللغة المكتشفة",
    )
    reasoning: str | None = Field(
        default=None,
        description="Reasoning for classification | سبب التصنيف",
    )


class AgentCall(BaseModel):
    """
    Definition of an agent call to be made.
    تعريف استدعاء الوكيل المراد تنفيذه.
    """

    agent_name: str = Field(
        ...,
        description="Name of the agent to call | اسم الوكيل المراد استدعاؤه",
    )
    endpoint: str = Field(
        ...,
        description="API endpoint to call | نقطة النهاية API المراد استدعاؤها",
    )
    method: Literal["GET", "POST", "PUT", "DELETE"] = Field(
        default="POST",
        description="HTTP method | طريقة HTTP",
    )
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters for the call | معاملات الاستدعاء",
    )
    headers: dict[str, str] = Field(
        default_factory=dict,
        description="Additional headers | رؤوس إضافية",
    )
    priority: int = Field(
        default=0,
        ge=0,
        le=10,
        description="Priority (0=highest) | الأولوية (0=الأعلى)",
    )
    required: bool = Field(
        default=True,
        description="Whether this call is required | هل هذا الاستدعاء مطلوب",
    )
    timeout: int = Field(
        default=30,
        description="Timeout in seconds | المهلة بالثواني",
    )


class ExecutionPlan(BaseModel):
    """
    Execution plan for orchestrating multiple agents.
    خطة التنفيذ لتنسيق عدة وكلاء.
    """

    plan_id: str = Field(
        ...,
        description="Unique plan identifier | معرف الخطة الفريد",
    )
    agents: list[AgentCall] = Field(
        ...,
        description="List of agents to call | قائمة الوكلاء المراد استدعاؤهم",
    )
    execution_mode: ExecutionMode = Field(
        default=ExecutionMode.PARALLEL,
        description="How to execute agent calls | كيفية تنفيذ استدعاءات الوكلاء",
    )
    intent: IntentClassification = Field(
        ...,
        description="Classified intent | النية المصنفة",
    )
    estimated_duration_ms: int = Field(
        default=5000,
        description="Estimated execution duration | مدة التنفيذ المقدرة",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Plan creation timestamp | وقت إنشاء الخطة",
    )


class AgentResult(BaseModel):
    """
    Result from an individual agent call.
    نتيجة من استدعاء وكيل فردي.
    """

    agent_name: str = Field(
        ...,
        description="Name of the agent | اسم الوكيل",
    )
    success: bool = Field(
        ...,
        description="Whether the call succeeded | هل نجح الاستدعاء",
    )
    result: dict[str, Any] | None = Field(
        default=None,
        description="Agent response data | بيانات استجابة الوكيل",
    )
    error: str | None = Field(
        default=None,
        description="Error message if failed | رسالة الخطأ إذا فشل",
    )
    latency_ms: int = Field(
        default=0,
        description="Latency in milliseconds | زمن الاستجابة بالميلي ثانية",
    )
    cached: bool = Field(
        default=False,
        description="Whether result was from cache | هل النتيجة من التخزين المؤقت",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata | بيانات وصفية إضافية",
    )


class AutoAction(BaseModel):
    """
    Automated action recommendation.
    توصية بإجراء تلقائي.
    """

    action_type: ActionType = Field(
        ...,
        description="Type of action | نوع الإجراء",
    )
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="Action parameters | معاملات الإجراء",
    )
    requires_confirmation: bool = Field(
        default=True,
        description="Requires user confirmation | يتطلب تأكيد المستخدم",
    )
    priority: Literal["low", "medium", "high", "critical"] = Field(
        default="medium",
        description="Action priority | أولوية الإجراء",
    )
    reason_en: str = Field(
        ...,
        description="Reason for action (English) | سبب الإجراء (إنجليزي)",
    )
    reason_ar: str = Field(
        ...,
        description="Reason for action (Arabic) | سبب الإجراء (عربي)",
    )
    expires_at: datetime | None = Field(
        default=None,
        description="When the action expires | متى ينتهي صلاحية الإجراء",
    )


class OrchestratorResponse(BaseModel):
    """
    Complete orchestrator response with all results.
    استجابة التنسيق الكاملة مع جميع النتائج.
    """

    request_id: str = Field(
        ...,
        description="Unique request identifier | معرف الطلب الفريد",
    )
    success: bool = Field(
        ...,
        description="Overall success status | حالة النجاح الإجمالية",
    )
    summary_en: str = Field(
        ...,
        description="Human-readable summary (English) | ملخص مفهوم (إنجليزي)",
    )
    summary_ar: str = Field(
        ...,
        description="Human-readable summary (Arabic) | ملخص مفهوم (عربي)",
    )
    detailed_results: list[AgentResult] = Field(
        default_factory=list,
        description="Results from all agents | نتائج جميع الوكلاء",
    )
    actions: list[AutoAction] = Field(
        default_factory=list,
        description="Recommended actions | الإجراءات الموصى بها",
    )
    recommendations_en: list[str] = Field(
        default_factory=list,
        description="Recommendations in English | التوصيات بالإنجليزية",
    )
    recommendations_ar: list[str] = Field(
        default_factory=list,
        description="Recommendations in Arabic | التوصيات بالعربية",
    )
    intent: IntentClassification | None = Field(
        default=None,
        description="Classified intent | النية المصنفة",
    )
    total_latency_ms: int = Field(
        default=0,
        description="Total latency | إجمالي زمن الاستجابة",
    )
    agents_called: int = Field(
        default=0,
        description="Number of agents called | عدد الوكلاء المستدعين",
    )
    cached_responses: int = Field(
        default=0,
        description="Number of cached responses | عدد الاستجابات المخزنة مؤقتا",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata | بيانات وصفية إضافية",
    )


class ExecutionPlanResponse(BaseModel):
    """
    Response for available execution plans.
    استجابة لخطط التنفيذ المتاحة.
    """

    plans: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Available execution plans | خطط التنفيذ المتاحة",
    )
    total: int = Field(
        default=0,
        description="Total number of plans | إجمالي عدد الخطط",
    )


class ExecuteActionRequest(BaseModel):
    """
    Request to execute a recommended action.
    طلب تنفيذ إجراء موصى به.
    """

    action: AutoAction = Field(
        ...,
        description="Action to execute | الإجراء المراد تنفيذه",
    )
    confirmed: bool = Field(
        default=False,
        description="User confirmed the action | أكد المستخدم الإجراء",
    )
    field_id: str | None = Field(
        default=None,
        description="Target field ID | معرف الحقل المستهدف",
    )
    tenant_id: str | None = Field(
        default=None,
        description="Tenant ID | معرف المستأجر",
    )


class ExecuteActionResponse(BaseModel):
    """
    Response from action execution.
    استجابة من تنفيذ الإجراء.
    """

    success: bool = Field(
        ...,
        description="Whether action was executed | هل تم تنفيذ الإجراء",
    )
    action_id: str | None = Field(
        default=None,
        description="Executed action ID | معرف الإجراء المنفذ",
    )
    message_en: str = Field(
        ...,
        description="Result message (English) | رسالة النتيجة (إنجليزي)",
    )
    message_ar: str = Field(
        ...,
        description="Result message (Arabic) | رسالة النتيجة (عربي)",
    )
    result: dict[str, Any] | None = Field(
        default=None,
        description="Action result data | بيانات نتيجة الإجراء",
    )
