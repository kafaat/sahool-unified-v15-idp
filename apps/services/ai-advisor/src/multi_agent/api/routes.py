"""
Multi-Agent System API Routes
مسارات واجهة برمجة التطبيقات لنظام الوكلاء المتعددين

FastAPI routes for the SAHOOL multi-agent agricultural advisory system.
مسارات FastAPI لنظام SAHOOL الاستشاري الزراعي متعدد الوكلاء.
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional, AsyncIterator
from datetime import datetime
from enum import Enum
import structlog
import json
import asyncio

from ..orchestration.master_advisor import (
    MasterAdvisor,
    FarmerQuery,
    QueryType,
    ExecutionMode,
    AgentRegistry,
    ContextStore,
)
from ..orchestration.council_manager import (
    CouncilManager,
    CouncilType,
    CouncilDecision as CouncilDecisionModel,
)

logger = structlog.get_logger()

# Create router | إنشاء الموجه
router = APIRouter(
    prefix="/v1/advisor",
    tags=["Multi-Agent Advisor"],
)

# ═══════════════════════════════════════════════════════════════════════════════
# Enums for API Models
# التعدادات لنماذج واجهة برمجة التطبيقات
# ═══════════════════════════════════════════════════════════════════════════════


class QueryTypeEnum(str, Enum):
    """
    Types of queries | أنواع الاستفسارات
    """
    diagnosis = "diagnosis"
    treatment = "treatment"
    irrigation = "irrigation"
    fertilization = "fertilization"
    pest_management = "pest_management"
    harvest_planning = "harvest_planning"
    emergency = "emergency"
    ecological_transition = "ecological_transition"
    market_analysis = "market_analysis"
    field_analysis = "field_analysis"
    yield_prediction = "yield_prediction"
    general_advisory = "general_advisory"


class ExecutionModeEnum(str, Enum):
    """
    Execution modes | أوضاع التنفيذ
    """
    parallel = "parallel"
    sequential = "sequential"
    council = "council"
    single_agent = "single_agent"


class PriorityEnum(str, Enum):
    """
    Query priority levels | مستويات أولوية الاستفسار
    """
    normal = "normal"
    high = "high"
    emergency = "emergency"


class CouncilTypeEnum(str, Enum):
    """
    Council types | أنواع المجالس
    """
    diagnosis_council = "diagnosis_council"
    treatment_council = "treatment_council"
    resource_council = "resource_council"
    emergency_council = "emergency_council"
    sustainability_council = "sustainability_council"
    harvest_council = "harvest_council"
    planning_council = "planning_council"


class MonitoringIntervalEnum(str, Enum):
    """
    Monitoring intervals | فترات المراقبة
    """
    hourly = "hourly"
    daily = "daily"
    weekly = "weekly"
    custom = "custom"


# ═══════════════════════════════════════════════════════════════════════════════
# Request Models
# نماذج الطلبات
# ═══════════════════════════════════════════════════════════════════════════════


class FarmerQueryRequest(BaseModel):
    """
    Farmer query request | طلب استفسار المزارع

    Used for processing farmer questions through the multi-agent system.
    يُستخدم لمعالجة أسئلة المزارعين عبر نظام الوكلاء المتعددين.
    """
    query: str = Field(
        ...,
        description="Farmer's question or request | سؤال أو طلب المزارع",
        min_length=1,
        max_length=2000,
        example="ما هي أفضل طريقة لري محصول الطماطم في هذا الوقت من السنة؟"
    )
    farmer_id: Optional[str] = Field(
        None,
        description="Farmer identifier | معرف المزارع",
        example="farmer_12345"
    )
    field_id: Optional[str] = Field(
        None,
        description="Field identifier | معرف الحقل",
        example="field_67890"
    )
    crop_type: Optional[str] = Field(
        None,
        description="Type of crop | نوع المحصول",
        example="tomato"
    )
    language: str = Field(
        default="ar",
        description="Response language (ar/en) | لغة الاستجابة",
        example="ar"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context | سياق إضافي",
        example={"soil_type": "clay", "weather": "sunny"}
    )
    images: Optional[List[str]] = Field(
        default=None,
        description="Image URLs or paths | روابط أو مسارات الصور",
        example=["https://example.com/crop_image.jpg"]
    )
    location: Optional[Dict[str, float]] = Field(
        default=None,
        description="Geographic location | الموقع الجغرافي",
        example={"lat": 31.9454, "lon": 35.9284}
    )
    priority: PriorityEnum = Field(
        default=PriorityEnum.normal,
        description="Query priority | أولوية الاستفسار"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session identifier for context | معرف الجلسة للسياق",
        example="session_abc123"
    )

    @validator('query')
    def validate_query(cls, v):
        """Validate query is not empty | التحقق من أن الاستفسار ليس فارغاً"""
        if not v or not v.strip():
            raise ValueError("Query cannot be empty | لا يمكن أن يكون الاستفسار فارغاً")
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "query": "نباتات الطماطم لديها بقع صفراء على الأوراق، ما السبب؟",
                "farmer_id": "farmer_001",
                "field_id": "field_123",
                "crop_type": "tomato",
                "language": "ar",
                "priority": "high",
                "location": {"lat": 31.9454, "lon": 35.9284}
            }
        }


class ConsultRequest(BaseModel):
    """
    Direct agent consultation request | طلب استشارة مباشر للوكيل

    For querying a specific agent directly.
    للاستعلام من وكيل محدد مباشرة.
    """
    query: str = Field(
        ...,
        description="Question for the agent | سؤال للوكيل",
        min_length=1,
        example="ما هو أفضل وقت لحصاد الطماطم؟"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Query context | سياق الاستفسار"
    )
    use_rag: bool = Field(
        default=True,
        description="Use RAG for knowledge retrieval | استخدام RAG لاسترجاع المعرفة"
    )

    class Config:
        schema_extra = {
            "example": {
                "query": "كيف يمكنني تحسين إنتاجية الطماطم؟",
                "context": {"crop_type": "tomato", "growth_stage": "flowering"},
                "use_rag": True
            }
        }


class CouncilRequest(BaseModel):
    """
    Council convening request | طلب عقد مجلس

    Request to convene a council of agents for critical decisions.
    طلب عقد مجلس من الوكلاء للقرارات الحرجة.
    """
    council_type: CouncilTypeEnum = Field(
        ...,
        description="Type of council to convene | نوع المجلس المراد عقده"
    )
    query: str = Field(
        ...,
        description="Issue or question to address | المسألة أو السؤال المراد معالجته",
        min_length=1,
        example="هل يجب رش المبيدات الآن أم الانتظار؟"
    )
    agent_ids: List[str] = Field(
        ...,
        description="List of agent IDs to participate | قائمة معرفات الوكلاء للمشاركة",
        min_items=2,
        example=["disease_expert", "ecological_expert", "field_analyst"]
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context | سياق إضافي"
    )
    min_confidence: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold | الحد الأدنى لعتبة الثقة"
    )

    class Config:
        schema_extra = {
            "example": {
                "council_type": "treatment_council",
                "query": "المحصول مصاب بمرض فطري، ما هو أفضل علاج إيكولوجي؟",
                "agent_ids": ["disease_expert", "ecological_expert"],
                "min_confidence": 0.7
            }
        }


class MonitoringConfig(BaseModel):
    """
    Field monitoring configuration | تكوين مراقبة الحقل

    Configuration for continuous field monitoring.
    تكوين المراقبة المستمرة للحقل.
    """
    crop_type: str = Field(
        ...,
        description="Type of crop | نوع المحصول",
        example="wheat"
    )
    monitoring_interval: MonitoringIntervalEnum = Field(
        default=MonitoringIntervalEnum.daily,
        description="Monitoring frequency | تواتر المراقبة"
    )
    custom_interval_hours: Optional[int] = Field(
        None,
        ge=1,
        le=168,
        description="Custom interval in hours (for custom mode) | فترة مخصصة بالساعات"
    )
    alerts_enabled: bool = Field(
        default=True,
        description="Enable alerts for issues | تمكين التنبيهات للمشاكل"
    )
    alert_thresholds: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Alert threshold configuration | تكوين عتبة التنبيه",
        example={"ndvi_drop": 0.1, "disease_risk": 0.7}
    )
    agents_to_consult: Optional[List[str]] = Field(
        default=None,
        description="Specific agents for monitoring | وكلاء محددون للمراقبة",
        example=["field_analyst", "disease_expert"]
    )

    @validator('custom_interval_hours')
    def validate_custom_interval(cls, v, values):
        """Validate custom interval when custom mode selected"""
        if values.get('monitoring_interval') == MonitoringIntervalEnum.custom and v is None:
            raise ValueError("custom_interval_hours required for custom monitoring")
        return v

    class Config:
        schema_extra = {
            "example": {
                "crop_type": "wheat",
                "monitoring_interval": "daily",
                "alerts_enabled": True,
                "alert_thresholds": {
                    "ndvi_drop": 0.15,
                    "disease_risk": 0.6
                },
                "agents_to_consult": ["field_analyst", "disease_expert"]
            }
        }


class FeedbackRequest(BaseModel):
    """
    User feedback request | طلب ملاحظات المستخدم

    Feedback on advisory responses for continuous improvement.
    ملاحظات على الاستجابات الاستشارية للتحسين المستمر.
    """
    query_id: Optional[str] = Field(
        None,
        description="ID of the original query | معرف الاستفسار الأصلي"
    )
    rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="Rating from 1-5 | التقييم من 1-5",
        example=4
    )
    helpful: bool = Field(
        ...,
        description="Was the response helpful? | هل كانت الاستجابة مفيدة؟"
    )
    comment: Optional[str] = Field(
        None,
        max_length=1000,
        description="Additional feedback | ملاحظات إضافية",
        example="الإجابة كانت مفصلة ومفيدة جداً"
    )
    issues: Optional[List[str]] = Field(
        default=None,
        description="Reported issues | المشاكل المبلغ عنها",
        example=["too_technical", "unclear_language"]
    )
    farmer_id: Optional[str] = Field(
        None,
        description="Farmer identifier | معرف المزارع"
    )

    class Config:
        schema_extra = {
            "example": {
                "query_id": "query_xyz789",
                "rating": 5,
                "helpful": True,
                "comment": "شكراً، المعلومات كانت دقيقة وواضحة",
                "farmer_id": "farmer_001"
            }
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Response Models
# نماذج الاستجابات
# ═══════════════════════════════════════════════════════════════════════════════


class AgentInfo(BaseModel):
    """
    Agent information | معلومات الوكيل
    """
    agent_id: str = Field(..., description="Agent identifier | معرف الوكيل")
    name: str = Field(..., description="Agent name | اسم الوكيل")
    role: str = Field(..., description="Agent role | دور الوكيل")
    description: str = Field(..., description="Agent description | وصف الوكيل")
    capabilities: List[str] = Field(..., description="Agent capabilities | قدرات الوكيل")
    status: str = Field(default="active", description="Agent status | حالة الوكيل")

    class Config:
        schema_extra = {
            "example": {
                "agent_id": "disease_expert",
                "name": "Disease Expert",
                "role": "Disease Diagnosis & Treatment",
                "description": "Expert in diagnosing plant diseases and recommending treatments",
                "capabilities": ["diagnosis", "treatment", "pest_management"],
                "status": "active"
            }
        }


class AgentResponse(BaseModel):
    """
    Individual agent response | استجابة وكيل فردي
    """
    agent_name: str = Field(..., description="Agent name | اسم الوكيل")
    agent_role: str = Field(..., description="Agent role | دور الوكيل")
    response: str = Field(..., description="Agent's response | استجابة الوكيل")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level | مستوى الثقة")
    execution_time: float = Field(..., description="Execution time in seconds | وقت التنفيذ بالثواني")
    sources: Optional[List[str]] = Field(default=None, description="Knowledge sources | مصادر المعرفة")

    class Config:
        schema_extra = {
            "example": {
                "agent_name": "disease_expert",
                "agent_role": "Disease Diagnosis",
                "response": "البقع الصفراء قد تكون بسبب نقص النيتروجين أو الإصابة بمرض فطري...",
                "confidence": 0.85,
                "execution_time": 2.3,
                "sources": ["plant_pathology_db", "crop_disease_manual"]
            }
        }


class AdvisoryResponse(BaseModel):
    """
    Complete advisory response | الاستجابة الاستشارية الكاملة
    """
    query: str = Field(..., description="Original query | الاستفسار الأصلي")
    answer: str = Field(..., description="Advisory answer | الإجابة الاستشارية")
    query_type: QueryTypeEnum = Field(..., description="Query type | نوع الاستفسار")
    agents_consulted: List[str] = Field(..., description="Agents consulted | الوكلاء المستشارون")
    execution_mode: ExecutionModeEnum = Field(..., description="Execution mode | وضع التنفيذ")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence | الثقة الإجمالية")
    recommendations: Optional[List[str]] = Field(default=None, description="Action recommendations | توصيات العمل")
    warnings: Optional[List[str]] = Field(default=None, description="Warnings | التحذيرات")
    next_steps: Optional[List[str]] = Field(default=None, description="Next steps | الخطوات التالية")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata | بيانات وصفية إضافية")
    language: str = Field(default="ar", description="Response language | لغة الاستجابة")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp | طابع زمني للاستجابة")

    class Config:
        schema_extra = {
            "example": {
                "query": "نباتات الطماطم لديها بقع صفراء",
                "answer": "البقع الصفراء على أوراق الطماطم يمكن أن تشير إلى نقص النيتروجين...",
                "query_type": "diagnosis",
                "agents_consulted": ["disease_expert", "field_analyst"],
                "execution_mode": "parallel",
                "confidence": 0.82,
                "recommendations": [
                    "إجراء اختبار للتربة",
                    "تطبيق سماد عضوي غني بالنيتروجين"
                ],
                "warnings": ["تجنب الإفراط في التسميد"],
                "next_steps": ["مراقبة النباتات لمدة أسبوع"],
                "language": "ar",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class CouncilDecision(BaseModel):
    """
    Council decision response | استجابة قرار المجلس
    """
    decision: str = Field(..., description="Final decision | القرار النهائي")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Decision confidence | ثقة القرار")
    consensus_level: float = Field(..., ge=0.0, le=1.0, description="Consensus level | مستوى الإجماع")
    participating_agents: List[str] = Field(..., description="Participating agents | الوكلاء المشاركون")
    supporting_count: int = Field(..., description="Supporting agents count | عدد الوكلاء المؤيدين")
    dissenting_count: int = Field(..., description="Dissenting agents count | عدد الوكلاء المعارضين")
    conflicts_count: int = Field(..., description="Number of conflicts | عدد التعارضات")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes | ملاحظات الحل")
    council_type: CouncilTypeEnum = Field(..., description="Council type | نوع المجلس")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Decision timestamp | طابع زمني للقرار")

    class Config:
        schema_extra = {
            "example": {
                "decision": "يُنصح باستخدام العلاج البيولوجي بدلاً من المبيدات الكيميائية",
                "confidence": 0.88,
                "consensus_level": 0.92,
                "participating_agents": ["disease_expert", "ecological_expert", "field_analyst"],
                "supporting_count": 3,
                "dissenting_count": 0,
                "conflicts_count": 0,
                "council_type": "treatment_council",
                "timestamp": "2024-01-15T11:00:00Z"
            }
        }


class CouncilStatus(BaseModel):
    """
    Council status information | معلومات حالة المجلس
    """
    council_id: str = Field(..., description="Council identifier | معرف المجلس")
    status: str = Field(..., description="Council status | حالة المجلس")
    progress: float = Field(..., ge=0.0, le=1.0, description="Progress percentage | نسبة التقدم")
    current_phase: str = Field(..., description="Current phase | المرحلة الحالية")
    started_at: datetime = Field(..., description="Start time | وقت البدء")
    estimated_completion: Optional[datetime] = Field(None, description="Est. completion | التقدير المتوقع للإكمال")

    class Config:
        schema_extra = {
            "example": {
                "council_id": "council_abc123",
                "status": "in_progress",
                "progress": 0.65,
                "current_phase": "deliberation",
                "started_at": "2024-01-15T10:00:00Z",
                "estimated_completion": "2024-01-15T10:15:00Z"
            }
        }


class MonitoringStatus(BaseModel):
    """
    Field monitoring status | حالة مراقبة الحقل
    """
    field_id: str = Field(..., description="Field identifier | معرف الحقل")
    is_active: bool = Field(..., description="Monitoring active | المراقبة نشطة")
    crop_type: str = Field(..., description="Crop type | نوع المحصول")
    interval: str = Field(..., description="Monitoring interval | فترة المراقبة")
    last_check: Optional[datetime] = Field(None, description="Last check time | وقت آخر فحص")
    next_check: Optional[datetime] = Field(None, description="Next check time | وقت الفحص التالي")
    alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Active alerts | التنبيهات النشطة")
    health_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Field health score | درجة صحة الحقل")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional data | بيانات إضافية")

    class Config:
        schema_extra = {
            "example": {
                "field_id": "field_123",
                "is_active": True,
                "crop_type": "wheat",
                "interval": "daily",
                "last_check": "2024-01-15T08:00:00Z",
                "next_check": "2024-01-16T08:00:00Z",
                "alerts": [
                    {
                        "type": "disease_risk",
                        "severity": "medium",
                        "message": "خطر متوسط للإصابة بالصدأ"
                    }
                ],
                "health_score": 0.78
            }
        }


class MetricsResponse(BaseModel):
    """
    System metrics response | استجابة مقاييس النظام
    """
    total_queries: int = Field(..., description="Total queries processed | إجمالي الاستفسارات المعالجة")
    avg_response_time: float = Field(..., description="Avg response time (seconds) | متوسط وقت الاستجابة")
    avg_confidence: float = Field(..., ge=0.0, le=1.0, description="Avg confidence score | متوسط درجة الثقة")
    agent_usage: Dict[str, int] = Field(..., description="Agent usage statistics | إحصائيات استخدام الوكلاء")
    query_types: Dict[str, int] = Field(..., description="Query type distribution | توزيع أنواع الاستفسارات")
    execution_modes: Dict[str, int] = Field(..., description="Execution mode distribution | توزيع أوضاع التنفيذ")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Success rate | معدل النجاح")
    avg_rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Average user rating | متوسط تقييم المستخدم")
    period: str = Field(..., description="Metrics period | فترة المقاييس")

    class Config:
        schema_extra = {
            "example": {
                "total_queries": 1523,
                "avg_response_time": 3.2,
                "avg_confidence": 0.83,
                "agent_usage": {
                    "disease_expert": 456,
                    "field_analyst": 389,
                    "irrigation_advisor": 312
                },
                "query_types": {
                    "diagnosis": 456,
                    "irrigation": 312,
                    "general_advisory": 755
                },
                "execution_modes": {
                    "parallel": 823,
                    "single_agent": 512,
                    "council": 188
                },
                "success_rate": 0.94,
                "avg_rating": 4.3,
                "period": "last_30_days"
            }
        }


class FeedbackResponse(BaseModel):
    """
    Feedback submission response | استجابة إرسال الملاحظات
    """
    feedback_id: str = Field(..., description="Feedback identifier | معرف الملاحظات")
    status: str = Field(..., description="Submission status | حالة الإرسال")
    message: str = Field(..., description="Response message | رسالة الاستجابة")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Submission time | وقت الإرسال")

    class Config:
        schema_extra = {
            "example": {
                "feedback_id": "feedback_xyz456",
                "status": "success",
                "message": "شكراً لملاحظاتك، سنعمل على تحسين الخدمة",
                "timestamp": "2024-01-15T12:00:00Z"
            }
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Global State (will be initialized by the application)
# الحالة العامة (سيتم تهيئتها بواسطة التطبيق)
# ═══════════════════════════════════════════════════════════════════════════════

# These will be injected by the main application
# سيتم حقن هذه من قبل التطبيق الرئيسي
_master_advisor: Optional[MasterAdvisor] = None
_agent_registry: Optional[AgentRegistry] = None
_council_manager: Optional[CouncilManager] = None
_context_store: Optional[ContextStore] = None

# In-memory storage for monitoring (in production, use Redis/database)
# تخزين في الذاكرة للمراقبة (في الإنتاج، استخدم Redis/قاعدة بيانات)
_active_monitoring: Dict[str, Dict[str, Any]] = {}
_feedback_store: List[Dict[str, Any]] = []
_metrics_store: Dict[str, Any] = {
    "total_queries": 0,
    "total_response_time": 0.0,
    "total_confidence": 0.0,
    "agent_usage": {},
    "query_types": {},
    "execution_modes": {},
    "successful_queries": 0,
    "ratings": [],
}


def initialize_multi_agent_api(
    master_advisor: MasterAdvisor,
    agent_registry: AgentRegistry,
    council_manager: CouncilManager,
    context_store: Optional[ContextStore] = None,
):
    """
    Initialize the multi-agent API with required components
    تهيئة واجهة برمجة التطبيقات متعددة الوكلاء بالمكونات المطلوبة

    This should be called during application startup.
    يجب استدعاء هذا أثناء بدء تشغيل التطبيق.
    """
    global _master_advisor, _agent_registry, _council_manager, _context_store

    _master_advisor = master_advisor
    _agent_registry = agent_registry
    _council_manager = council_manager
    _context_store = context_store or ContextStore()

    logger.info("multi_agent_api_initialized")


# ═══════════════════════════════════════════════════════════════════════════════
# Query Processing Endpoints
# نقاط نهاية معالجة الاستفسارات
# ═══════════════════════════════════════════════════════════════════════════════


@router.post(
    "/query",
    response_model=AdvisoryResponse,
    summary="Process farmer query | معالجة استفسار المزارع",
    description="""
    Process a farmer query through the multi-agent system.
    معالجة استفسار المزارع عبر نظام الوكلاء المتعددين.

    The system will:
    - Analyze the query to determine type and requirements
    - Route to appropriate specialized agents
    - Execute agents in optimal mode (parallel/sequential/council)
    - Aggregate and synthesize responses
    - Return comprehensive advisory

    سيقوم النظام بـ:
    - تحليل الاستفسار لتحديد النوع والمتطلبات
    - التوجيه للوكلاء المتخصصين المناسبين
    - تنفيذ الوكلاء في الوضع الأمثل (متوازي/متتابع/مجلس)
    - تجميع ودمج الاستجابات
    - إرجاع استشارة شاملة
    """,
    tags=["Query Processing"],
)
async def process_query(request: FarmerQueryRequest) -> AdvisoryResponse:
    """
    Process farmer query | معالجة استفسار المزارع
    """
    if not _master_advisor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Multi-agent system not initialized | نظام الوكلاء المتعددين غير مهيأ"
        )

    try:
        start_time = datetime.utcnow()

        # Create FarmerQuery object
        # إنشاء كائن استفسار المزارع
        farmer_query = FarmerQuery(
            query=request.query,
            farmer_id=request.farmer_id,
            field_id=request.field_id,
            crop_type=request.crop_type,
            language=request.language,
            context=request.context or {},
            images=request.images or [],
            location=request.location,
            priority=request.priority.value,
        )

        # Process query through master advisor
        # معالجة الاستفسار عبر المستشار الرئيسي
        result = await _master_advisor.process_query(
            query=farmer_query,
            session_id=request.session_id
        )

        # Update metrics
        # تحديث المقاييس
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        _update_metrics(result, execution_time)

        logger.info(
            "query_processed",
            query_type=result.query_type.value,
            execution_time=execution_time,
            confidence=result.confidence
        )

        # Convert to API response model
        # التحويل إلى نموذج استجابة واجهة برمجة التطبيقات
        return AdvisoryResponse(
            query=result.query,
            answer=result.answer,
            query_type=QueryTypeEnum(result.query_type.value),
            agents_consulted=result.agents_consulted,
            execution_mode=ExecutionModeEnum(result.execution_mode.value),
            confidence=result.confidence,
            recommendations=result.recommendations,
            warnings=result.warnings,
            next_steps=result.next_steps,
            metadata=result.metadata,
            language=result.language,
            timestamp=result.timestamp,
        )

    except Exception as e:
        logger.error("query_processing_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed | فشلت معالجة الاستفسار: {str(e)}"
        )


@router.post(
    "/query/stream",
    summary="Process query with streaming | معالجة الاستفسار مع البث",
    description="""
    Process farmer query with streaming response.
    معالجة استفسار المزارع مع استجابة البث.

    Returns a streaming response for real-time updates.
    يعيد استجابة بث للتحديثات في الوقت الفعلي.
    """,
    tags=["Query Processing"],
)
async def process_query_stream(request: FarmerQueryRequest) -> StreamingResponse:
    """
    Process query with streaming response | معالجة الاستفسار مع استجابة البث
    """
    if not _master_advisor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Multi-agent system not initialized"
        )

    async def generate_stream() -> AsyncIterator[str]:
        """Generate streaming response | إنشاء استجابة البث"""
        try:
            # Send initial status
            # إرسال الحالة الأولية
            yield f"data: {json.dumps({'status': 'analyzing', 'message': 'Analyzing query...', 'message_ar': 'تحليل الاستفسار...'})}\n\n"

            # Create farmer query
            # إنشاء استفسار المزارع
            farmer_query = FarmerQuery(
                query=request.query,
                farmer_id=request.farmer_id,
                field_id=request.field_id,
                crop_type=request.crop_type,
                language=request.language,
                context=request.context or {},
                images=request.images or [],
                location=request.location,
                priority=request.priority.value,
            )

            # Analyze query
            # تحليل الاستفسار
            analysis = await _master_advisor.analyze_query(farmer_query)

            yield f"data: {json.dumps({'status': 'routing', 'query_type': analysis.query_type.value, 'agents': analysis.required_agents, 'message_ar': 'توجيه للوكلاء...'})}\n\n"

            # Process query
            # معالجة الاستفسار
            result = await _master_advisor.process_query(
                query=farmer_query,
                session_id=request.session_id
            )

            # Send final result
            # إرسال النتيجة النهائية
            final_data = {
                'status': 'complete',
                'query': result.query,
                'answer': result.answer,
                'confidence': result.confidence,
                'agents_consulted': result.agents_consulted,
                'recommendations': result.recommendations,
                'warnings': result.warnings,
                'next_steps': result.next_steps,
            }

            yield f"data: {json.dumps(final_data)}\n\n"

        except Exception as e:
            logger.error("streaming_query_failed", error=str(e))
            error_data = {
                'status': 'error',
                'error': str(e),
                'message_ar': f'حدث خطأ: {str(e)}'
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Agent Discovery Endpoints
# نقاط نهاية اكتشاف الوكلاء
# ═══════════════════════════════════════════════════════════════════════════════


@router.get(
    "/agents",
    response_model=List[AgentInfo],
    summary="List all available agents | قائمة جميع الوكلاء المتاحين",
    description="""
    Get information about all available AI agents.
    الحصول على معلومات حول جميع وكلاء الذكاء الاصطناعي المتاحين.
    """,
    tags=["Agent Discovery"],
)
async def list_agents() -> List[AgentInfo]:
    """
    List all available agents | قائمة جميع الوكلاء المتاحين
    """
    if not _agent_registry:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent registry not initialized"
        )

    try:
        agents_data = _agent_registry.list_agents()

        agent_info_list = []
        for agent_data in agents_data:
            agent_info = AgentInfo(
                agent_id=agent_data["name"],
                name=agent_data["name"].replace("_", " ").title(),
                role=agent_data["role"],
                description=f"Specialized agent for {agent_data['role']}",
                capabilities=agent_data["capabilities"],
                status="active"
            )
            agent_info_list.append(agent_info)

        logger.info("agents_listed", count=len(agent_info_list))
        return agent_info_list

    except Exception as e:
        logger.error("list_agents_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}"
        )


@router.get(
    "/agents/{agent_id}",
    response_model=AgentInfo,
    summary="Get agent information | الحصول على معلومات الوكيل",
    description="""
    Get detailed information about a specific agent.
    الحصول على معلومات مفصلة حول وكيل محدد.
    """,
    tags=["Agent Discovery"],
)
async def get_agent(agent_id: str) -> AgentInfo:
    """
    Get specific agent information | الحصول على معلومات وكيل محدد
    """
    if not _agent_registry:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent registry not initialized"
        )

    try:
        agent = _agent_registry.get_agent(agent_id)

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent not found: {agent_id}"
            )

        # Get agent capabilities from registry
        # الحصول على قدرات الوكيل من السجل
        agents_list = _agent_registry.list_agents()
        agent_data = next((a for a in agents_list if a["name"] == agent_id), None)

        if not agent_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent not found in registry: {agent_id}"
            )

        return AgentInfo(
            agent_id=agent_id,
            name=agent_id.replace("_", " ").title(),
            role=agent_data["role"],
            description=f"Specialized agent for {agent_data['role']}",
            capabilities=agent_data["capabilities"],
            status="active"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_agent_failed", agent_id=agent_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent information: {str(e)}"
        )


@router.post(
    "/agents/{agent_id}/consult",
    response_model=AgentResponse,
    summary="Consult specific agent | استشارة وكيل محدد",
    description="""
    Directly consult a specific agent.
    استشارة وكيل محدد مباشرة.

    Bypasses the master advisor and queries the agent directly.
    يتجاوز المستشار الرئيسي ويستعلم من الوكيل مباشرة.
    """,
    tags=["Agent Discovery"],
)
async def consult_agent(agent_id: str, request: ConsultRequest) -> AgentResponse:
    """
    Consult a specific agent directly | استشارة وكيل محدد مباشرة
    """
    if not _agent_registry:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent registry not initialized"
        )

    try:
        agent = _agent_registry.get_agent(agent_id)

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent not found: {agent_id}"
            )

        start_time = datetime.utcnow()

        # Call agent's think method
        # استدعاء طريقة التفكير للوكيل
        result = await agent.think(
            query=request.query,
            context=request.context or {},
            use_rag=request.use_rag
        )

        execution_time = (datetime.utcnow() - start_time).total_seconds()

        logger.info(
            "agent_consulted",
            agent_id=agent_id,
            execution_time=execution_time
        )

        return AgentResponse(
            agent_name=agent_id,
            agent_role=getattr(agent, "role", "Unknown"),
            response=result.get("response", ""),
            confidence=result.get("confidence", 0.7),
            execution_time=execution_time,
            sources=result.get("sources", [])
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("consult_agent_failed", agent_id=agent_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent consultation failed: {str(e)}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Council Operations Endpoints
# نقاط نهاية عمليات المجلس
# ═══════════════════════════════════════════════════════════════════════════════


@router.post(
    "/council/convene",
    response_model=CouncilDecision,
    summary="Convene agent council | عقد مجلس الوكلاء",
    description="""
    Convene a council of agents for critical decision-making.
    عقد مجلس من الوكلاء لاتخاذ قرارات حرجة.

    Council mode enables:
    - Collaborative decision-making
    - Consensus building
    - Conflict resolution
    - High-confidence recommendations

    يتيح وضع المجلس:
    - اتخاذ قرارات تعاونية
    - بناء الإجماع
    - حل التعارضات
    - توصيات عالية الثقة
    """,
    tags=["Council Operations"],
)
async def convene_council(request: CouncilRequest) -> CouncilDecision:
    """
    Convene a council of agents | عقد مجلس من الوكلاء
    """
    if not _council_manager or not _agent_registry:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Council manager not initialized"
        )

    try:
        # Get agents from registry
        # الحصول على الوكلاء من السجل
        agents = []
        for agent_id in request.agent_ids:
            agent = _agent_registry.get_agent(agent_id)
            if not agent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Agent not found: {agent_id}"
                )
            agents.append(agent)

        # Convert council type
        # تحويل نوع المجلس
        council_type = CouncilType(request.council_type.value)

        # Convene council
        # عقد المجلس
        decision = await _council_manager.convene_council(
            council_type=council_type,
            query=request.query,
            agents=agents,
            context=request.context,
            min_confidence=request.min_confidence,
        )

        logger.info(
            "council_convened",
            council_type=council_type.value,
            consensus_level=decision.consensus_level,
            confidence=decision.confidence
        )

        # Convert to API response
        # التحويل إلى استجابة واجهة برمجة التطبيقات
        return CouncilDecision(
            decision=decision.decision,
            confidence=decision.confidence,
            consensus_level=decision.consensus_level,
            participating_agents=decision.participating_agents,
            supporting_count=len(decision.supporting_opinions),
            dissenting_count=len(decision.dissenting_opinions),
            conflicts_count=len(decision.conflicts),
            resolution_notes=decision.resolution_notes,
            council_type=CouncilTypeEnum(decision.council_type.value),
            timestamp=decision.timestamp,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("convene_council_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Council convening failed: {str(e)}"
        )


@router.get(
    "/council/{council_id}/status",
    response_model=CouncilStatus,
    summary="Get council status | الحصول على حالة المجلس",
    description="""
    Get the current status of a council session.
    الحصول على الحالة الحالية لجلسة المجلس.
    """,
    tags=["Council Operations"],
)
async def get_council_status(council_id: str) -> CouncilStatus:
    """
    Get council status | الحصول على حالة المجلس

    Note: This is a placeholder. In a production system, council sessions
    would be tracked with unique IDs and stored in a database.
    ملاحظة: هذا نائب. في نظام الإنتاج، سيتم تتبع جلسات المجلس
    بمعرفات فريدة وتخزينها في قاعدة بيانات.
    """
    # This is a mock implementation
    # هذا تنفيذ وهمي
    # In production, retrieve from database/cache
    # في الإنتاج، الاسترجاع من قاعدة البيانات/الذاكرة المؤقتة

    return CouncilStatus(
        council_id=council_id,
        status="completed",
        progress=1.0,
        current_phase="decision_reached",
        started_at=datetime.utcnow(),
        estimated_completion=datetime.utcnow(),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Monitoring Endpoints
# نقاط نهاية المراقبة
# ═══════════════════════════════════════════════════════════════════════════════


@router.get(
    "/monitoring/{field_id}",
    response_model=MonitoringStatus,
    summary="Get field monitoring status | الحصول على حالة مراقبة الحقل",
    description="""
    Get current monitoring status for a field.
    الحصول على حالة المراقبة الحالية للحقل.
    """,
    tags=["Monitoring"],
)
async def get_monitoring_status(field_id: str) -> MonitoringStatus:
    """
    Get field monitoring status | الحصول على حالة مراقبة الحقل
    """
    monitoring_data = _active_monitoring.get(field_id)

    if not monitoring_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No monitoring active for field: {field_id}"
        )

    return MonitoringStatus(**monitoring_data)


@router.post(
    "/monitoring/{field_id}/start",
    summary="Start field monitoring | بدء مراقبة الحقل",
    description="""
    Start continuous monitoring for a field.
    بدء المراقبة المستمرة للحقل.

    Monitoring includes:
    - Regular field health checks
    - Disease risk assessment
    - Irrigation needs
    - Automated alerts

    تشمل المراقبة:
    - فحوصات صحة الحقل المنتظمة
    - تقييم مخاطر الأمراض
    - احتياجات الري
    - تنبيهات تلقائية
    """,
    tags=["Monitoring"],
)
async def start_monitoring(
    field_id: str,
    config: MonitoringConfig,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Start field monitoring | بدء مراقبة الحقل
    """
    if field_id in _active_monitoring:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Monitoring already active for field: {field_id}"
        )

    try:
        # Calculate next check time
        # حساب وقت الفحص التالي
        next_check = _calculate_next_check(config.monitoring_interval, config.custom_interval_hours)

        # Initialize monitoring
        # تهيئة المراقبة
        monitoring_data = {
            "field_id": field_id,
            "is_active": True,
            "crop_type": config.crop_type,
            "interval": config.monitoring_interval.value,
            "last_check": None,
            "next_check": next_check,
            "alerts": [],
            "health_score": None,
            "metadata": {
                "config": config.dict(),
                "started_at": datetime.utcnow().isoformat()
            }
        }

        _active_monitoring[field_id] = monitoring_data

        # Schedule background monitoring task
        # جدولة مهمة المراقبة في الخلفية
        # Note: In production, use Celery or similar for proper task scheduling
        # ملاحظة: في الإنتاج، استخدم Celery أو ما شابه للجدولة المناسبة للمهام

        logger.info(
            "monitoring_started",
            field_id=field_id,
            crop_type=config.crop_type,
            interval=config.monitoring_interval.value
        )

        return {
            "status": "success",
            "message": f"Monitoring started for field {field_id}",
            "message_ar": f"تم بدء المراقبة للحقل {field_id}",
            "next_check": next_check.isoformat(),
        }

    except Exception as e:
        logger.error("start_monitoring_failed", field_id=field_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start monitoring: {str(e)}"
        )


@router.post(
    "/monitoring/{field_id}/stop",
    summary="Stop field monitoring | إيقاف مراقبة الحقل",
    description="""
    Stop continuous monitoring for a field.
    إيقاف المراقبة المستمرة للحقل.
    """,
    tags=["Monitoring"],
)
async def stop_monitoring(field_id: str) -> Dict[str, Any]:
    """
    Stop field monitoring | إيقاف مراقبة الحقل
    """
    if field_id not in _active_monitoring:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No monitoring active for field: {field_id}"
        )

    try:
        del _active_monitoring[field_id]

        logger.info("monitoring_stopped", field_id=field_id)

        return {
            "status": "success",
            "message": f"Monitoring stopped for field {field_id}",
            "message_ar": f"تم إيقاف المراقبة للحقل {field_id}",
        }

    except Exception as e:
        logger.error("stop_monitoring_failed", field_id=field_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop monitoring: {str(e)}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Feedback & Metrics Endpoints
# نقاط نهاية الملاحظات والمقاييس
# ═══════════════════════════════════════════════════════════════════════════════


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    summary="Submit feedback | إرسال ملاحظات",
    description="""
    Submit feedback on advisory responses.
    إرسال ملاحظات على الاستجابات الاستشارية.

    Your feedback helps improve the system.
    ملاحظاتك تساعد في تحسين النظام.
    """,
    tags=["Feedback"],
)
async def submit_feedback(feedback: FeedbackRequest) -> FeedbackResponse:
    """
    Submit user feedback | إرسال ملاحظات المستخدم
    """
    try:
        # Generate feedback ID
        # إنشاء معرف الملاحظات
        feedback_id = f"feedback_{datetime.utcnow().timestamp()}"

        # Store feedback
        # تخزين الملاحظات
        feedback_data = feedback.dict()
        feedback_data["feedback_id"] = feedback_id
        feedback_data["timestamp"] = datetime.utcnow().isoformat()

        _feedback_store.append(feedback_data)

        # Update metrics with rating
        # تحديث المقاييس بالتقييم
        _metrics_store["ratings"].append(feedback.rating)

        logger.info(
            "feedback_received",
            feedback_id=feedback_id,
            rating=feedback.rating,
            helpful=feedback.helpful
        )

        message = (
            "شكراً لملاحظاتك القيمة! سنستخدمها لتحسين خدماتنا."
            if feedback.rating >= 4
            else "شكراً لملاحظاتك. نعمل باستمرار على تحسين جودة الخدمة."
        )

        return FeedbackResponse(
            feedback_id=feedback_id,
            status="success",
            message=message,
            timestamp=datetime.utcnow(),
        )

    except Exception as e:
        logger.error("submit_feedback_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Get system metrics | الحصول على مقاييس النظام",
    description="""
    Get performance and usage metrics for the multi-agent system.
    الحصول على مقاييس الأداء والاستخدام لنظام الوكلاء المتعددين.
    """,
    tags=["Feedback"],
)
async def get_metrics() -> MetricsResponse:
    """
    Get system metrics | الحصول على مقاييس النظام
    """
    try:
        total_queries = _metrics_store["total_queries"]

        # Calculate averages
        # حساب المتوسطات
        avg_response_time = (
            _metrics_store["total_response_time"] / total_queries
            if total_queries > 0 else 0.0
        )

        avg_confidence = (
            _metrics_store["total_confidence"] / total_queries
            if total_queries > 0 else 0.0
        )

        success_rate = (
            _metrics_store["successful_queries"] / total_queries
            if total_queries > 0 else 0.0
        )

        avg_rating = (
            sum(_metrics_store["ratings"]) / len(_metrics_store["ratings"])
            if _metrics_store["ratings"] else None
        )

        logger.info("metrics_retrieved", total_queries=total_queries)

        return MetricsResponse(
            total_queries=total_queries,
            avg_response_time=round(avg_response_time, 2),
            avg_confidence=round(avg_confidence, 2),
            agent_usage=_metrics_store["agent_usage"],
            query_types=_metrics_store["query_types"],
            execution_modes=_metrics_store["execution_modes"],
            success_rate=round(success_rate, 2),
            avg_rating=round(avg_rating, 1) if avg_rating else None,
            period="all_time"
        )

    except Exception as e:
        logger.error("get_metrics_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# الوظائف المساعدة
# ═══════════════════════════════════════════════════════════════════════════════


def _update_metrics(result, execution_time: float):
    """
    Update system metrics | تحديث مقاييس النظام
    """
    _metrics_store["total_queries"] += 1
    _metrics_store["total_response_time"] += execution_time
    _metrics_store["total_confidence"] += result.confidence
    _metrics_store["successful_queries"] += 1

    # Update agent usage
    # تحديث استخدام الوكلاء
    for agent in result.agents_consulted:
        _metrics_store["agent_usage"][agent] = _metrics_store["agent_usage"].get(agent, 0) + 1

    # Update query types
    # تحديث أنواع الاستفسارات
    query_type = result.query_type.value
    _metrics_store["query_types"][query_type] = _metrics_store["query_types"].get(query_type, 0) + 1

    # Update execution modes
    # تحديث أوضاع التنفيذ
    exec_mode = result.execution_mode.value
    _metrics_store["execution_modes"][exec_mode] = _metrics_store["execution_modes"].get(exec_mode, 0) + 1


def _calculate_next_check(interval: MonitoringIntervalEnum, custom_hours: Optional[int]) -> datetime:
    """
    Calculate next check time | حساب وقت الفحص التالي
    """
    from datetime import timedelta

    now = datetime.utcnow()

    if interval == MonitoringIntervalEnum.hourly:
        return now + timedelta(hours=1)
    elif interval == MonitoringIntervalEnum.daily:
        return now + timedelta(days=1)
    elif interval == MonitoringIntervalEnum.weekly:
        return now + timedelta(weeks=1)
    elif interval == MonitoringIntervalEnum.custom and custom_hours:
        return now + timedelta(hours=custom_hours)
    else:
        return now + timedelta(days=1)  # Default to daily
