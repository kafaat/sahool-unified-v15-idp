"""
Multi-Agent System API Module
وحدة واجهة برمجة التطبيقات لنظام الوكلاء المتعددين

FastAPI routes and models for the SAHOOL multi-agent agricultural advisory system.
مسارات ونماذج FastAPI لنظام SAHOOL الاستشاري الزراعي متعدد الوكلاء.
"""

from .routes import (
    router,
    initialize_multi_agent_api,
    # Request Models | نماذج الطلبات
    FarmerQueryRequest,
    ConsultRequest,
    CouncilRequest,
    MonitoringConfig,
    FeedbackRequest,
    # Response Models | نماذج الاستجابات
    AgentInfo,
    AgentResponse,
    AdvisoryResponse,
    CouncilDecision,
    CouncilStatus,
    MonitoringStatus,
    MetricsResponse,
    FeedbackResponse,
    # Enums | التعدادات
    QueryTypeEnum,
    ExecutionModeEnum,
    PriorityEnum,
    CouncilTypeEnum,
    MonitoringIntervalEnum,
)

__all__ = [
    # Router
    "router",
    "initialize_multi_agent_api",
    # Request Models
    "FarmerQueryRequest",
    "ConsultRequest",
    "CouncilRequest",
    "MonitoringConfig",
    "FeedbackRequest",
    # Response Models
    "AgentInfo",
    "AgentResponse",
    "AdvisoryResponse",
    "CouncilDecision",
    "CouncilStatus",
    "MonitoringStatus",
    "MetricsResponse",
    "FeedbackResponse",
    # Enums
    "QueryTypeEnum",
    "ExecutionModeEnum",
    "PriorityEnum",
    "CouncilTypeEnum",
    "MonitoringIntervalEnum",
]
