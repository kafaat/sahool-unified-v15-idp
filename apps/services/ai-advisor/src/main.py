"""
AI Advisor Service - Main Application
خدمة المستشار الذكي - التطبيق الرئيسي

Multi-agent AI system for agricultural advisory.
نظام ذكاء اصطناعي متعدد الوكلاء للاستشارات الزراعية.
"""

# Import shared CORS configuration | استيراد تكوين CORS المشترك
import os
import sys
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from .agents import (
    DiseaseExpertAgent,
    FieldAnalystAgent,
    IrrigationAdvisorAgent,
    YieldPredictorAgent,
)
from .config import settings
from .middleware import (
    InputValidationMiddleware,
    RateLimitMiddleware,
    rate_limiter,
)
from .monitoring import cost_tracker
from .orchestration import Supervisor
from .rag import EmbeddingsManager, KnowledgeRetriever
from .security import PromptGuard
from .tools import AgroTool, CropHealthTool, SatelliteTool, WeatherTool
from .utils import pii_masking_processor

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "shared"))
try:
    from config.cors_config import setup_cors_middleware
except ImportError:
    # Fallback: define secure origins locally if shared module not available
    setup_cors_middleware = None

# Configure structured logging with PII masking | تكوين السجلات المنظمة مع إخفاء المعلومات الشخصية
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        pii_masking_processor,  # Mask PII before rendering
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()

# Import A2A Protocol Support | استيراد دعم بروتوكول A2A
try:
    from a2a.server import create_a2a_router

    from .a2a_adapter import create_ai_advisor_a2a_agent

    A2A_AVAILABLE = True
except ImportError:
    A2A_AVAILABLE = False
    logger.warning("A2A protocol support not available")


# Pydantic models for requests/responses
# نماذج Pydantic للطلبات/الاستجابات


class QuestionRequest(BaseModel):
    """General question request | طلب سؤال عام"""

    question: str = Field(..., description="User question")
    language: str = Field(default="en", description="Response language (en/ar)")
    context: dict[str, Any] | None = Field(
        default=None, description="Additional context"
    )


class DiagnoseRequest(BaseModel):
    """Disease diagnosis request | طلب تشخيص مرض"""

    crop_type: str = Field(..., description="Type of crop")
    symptoms: dict[str, Any] = Field(..., description="Disease symptoms")
    image_path: str | None = Field(default=None, description="Path to crop image")
    location: str | None = Field(default=None, description="Field location")


class RecommendationRequest(BaseModel):
    """Recommendation request | طلب توصيات"""

    crop_type: str = Field(..., description="Type of crop")
    growth_stage: str = Field(..., description="Current growth stage")
    recommendation_type: str = Field(
        ..., description="Type (irrigation/fertilizer/pest)"
    )
    field_data: dict[str, Any] | None = Field(default=None, description="Field data")


class FieldAnalysisRequest(BaseModel):
    """Field analysis request | طلب تحليل حقل"""

    field_id: str = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Type of crop")
    include_disease_check: bool = Field(
        default=True, description="Include disease analysis"
    )
    include_irrigation: bool = Field(
        default=True, description="Include irrigation advice"
    )
    include_yield_prediction: bool = Field(
        default=True, description="Include yield prediction"
    )


class AgentResponse(BaseModel):
    """Agent response model | نموذج استجابة الوكيل"""

    status: str
    data: dict[str, Any] | None = None
    error: str | None = None


# Global instances | المثيلات العامة
app_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    مدير دورة حياة التطبيق
    """
    # Startup | بدء التشغيل
    logger.info("ai_advisor_service_starting", version="1.0.0")

    try:
        # Initialize embeddings and retriever | تهيئة التضمينات والمسترجع
        embeddings_manager = EmbeddingsManager()
        knowledge_retriever = KnowledgeRetriever(embeddings_manager=embeddings_manager)

        # Initialize tools | تهيئة الأدوات
        crop_health_tool = CropHealthTool()
        weather_tool = WeatherTool()
        satellite_tool = SatelliteTool()
        agro_tool = AgroTool()

        # Initialize agents | تهيئة الوكلاء
        field_analyst = FieldAnalystAgent(tools=[], retriever=knowledge_retriever)

        disease_expert = DiseaseExpertAgent(tools=[], retriever=knowledge_retriever)

        irrigation_advisor = IrrigationAdvisorAgent(
            tools=[], retriever=knowledge_retriever
        )

        yield_predictor = YieldPredictorAgent(tools=[], retriever=knowledge_retriever)

        # Initialize supervisor | تهيئة المشرف
        agents = {
            "field_analyst": field_analyst,
            "disease_expert": disease_expert,
            "irrigation_advisor": irrigation_advisor,
            "yield_predictor": yield_predictor,
        }

        supervisor = Supervisor(agents=agents)

        # Store in app state | التخزين في حالة التطبيق
        app_state["embeddings"] = embeddings_manager
        app_state["retriever"] = knowledge_retriever
        app_state["tools"] = {
            "crop_health": crop_health_tool,
            "weather": weather_tool,
            "satellite": satellite_tool,
            "agro": agro_tool,
        }
        app_state["agents"] = agents
        app_state["supervisor"] = supervisor

        # Initialize A2A agent if available | تهيئة وكيل A2A إذا كان متاحاً
        if A2A_AVAILABLE:
            try:
                base_url = os.getenv(
                    "SERVICE_BASE_URL", f"http://localhost:{settings.service_port}"
                )
                a2a_agent = create_ai_advisor_a2a_agent(
                    base_url=base_url, agents=agents, supervisor=supervisor
                )
                app_state["a2a_agent"] = a2a_agent
                logger.info("a2a_agent_initialized", agent_id=a2a_agent.agent_id)
            except Exception as e:
                logger.error("a2a_agent_initialization_failed", error=str(e))

        logger.info("ai_advisor_service_started_successfully")

    except Exception as e:
        logger.error("ai_advisor_service_startup_failed", error=str(e))
        raise

    yield

    # Shutdown | الإغلاق
    logger.info("ai_advisor_service_shutting_down")
    app_state.clear()


# Create FastAPI app | إنشاء تطبيق FastAPI
app = FastAPI(
    title="AI Advisor Service",
    description="Multi-agent AI system for agricultural advisory",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware with secure configuration | إضافة middleware CORS بتكوين آمن
# Security: No wildcard origins - uses environment-based whitelist
if setup_cors_middleware:
    setup_cors_middleware(app)
else:
    # Fallback: Secure origins list when shared module unavailable
    from fastapi.middleware.cors import CORSMiddleware

    SECURE_ORIGINS = [
        "https://sahool.app",
        "https://admin.sahool.app",
        "https://api.sahool.app",
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=SECURE_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Accept",
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "X-Tenant-ID",
        ],
    )

# Add input validation middleware | إضافة middleware التحقق من المدخلات
# Security: Validate and sanitize all incoming requests
app.add_middleware(InputValidationMiddleware)

# Add rate limiting middleware | إضافة middleware تحديد المعدل
# Security: Rate limiting to prevent abuse of AI endpoints
app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter)

# Add A2A router if available | إضافة موجه A2A إذا كان متاحاً
if A2A_AVAILABLE:

    @app.on_event("startup")
    async def setup_a2a_routes():
        """Setup A2A protocol routes after startup"""
        a2a_agent = app_state.get("a2a_agent")
        if a2a_agent:
            a2a_router = create_a2a_router(a2a_agent, prefix="/a2a")
            app.include_router(a2a_router)
            logger.info("a2a_routes_registered")


# Endpoints | نقاط النهاية


@app.get("/healthz", tags=["Health"])
async def health_check():
    """
    Health check endpoint with dependency validation
    نقطة فحص الصحة مع التحقق من التبعيات
    """
    embeddings_ok = embeddings_manager is not None
    retriever_ok = knowledge_retriever is not None
    agents_count = len([a for a in [field_analyst, disease_expert, irrigation_advisor, yield_predictor] if a])

    is_healthy = embeddings_ok or retriever_ok or agents_count > 0

    return {
        "status": "healthy" if is_healthy else "degraded",
        "service": settings.service_name,
        "version": "1.0.0",
        "embeddings_ready": embeddings_ok,
        "retriever_ready": retriever_ok,
        "agents_available": agents_count,
    }


@app.post("/v1/advisor/ask", response_model=AgentResponse, tags=["Advisor"])
async def ask_question(request: QuestionRequest):
    """
    Ask a general question to the AI advisor
    طرح سؤال عام على المستشار الذكي

    The supervisor will route the question to appropriate agents.
    سيوجه المشرف السؤال إلى الوكلاء المناسبين.
    """
    try:
        supervisor = app_state.get("supervisor")
        if not supervisor:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not initialized",
            )

        # Guard against prompt injection at API level (defense in depth)
        # الحماية من حقن الأوامر على مستوى API (دفاع متعدد الطبقات)
        sanitized_question, is_safe, warnings = PromptGuard.validate_and_sanitize(
            request.question, strict=False
        )

        if not is_safe:
            logger.warning(
                "potential_injection_at_api",
                endpoint="ask",
                warnings=warnings,
            )

        # Coordinate agents to answer
        # تنسيق الوكلاء للإجابة
        result = await supervisor.coordinate(
            query=sanitized_question,
            context=request.context,
        )

        return AgentResponse(status="success", data=result)

    except Exception as e:
        logger.error("ask_question_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/v1/advisor/diagnose", response_model=AgentResponse, tags=["Advisor"])
async def diagnose_disease(request: DiagnoseRequest):
    """
    Diagnose crop disease
    تشخيص مرض المحصول

    Uses disease expert agent for diagnosis.
    يستخدم وكيل خبير الأمراض للتشخيص.
    """
    try:
        agents = app_state.get("agents")
        tools = app_state.get("tools")

        if not agents:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not initialized",
            )

        disease_expert = agents["disease_expert"]

        # Get image analysis if image provided
        # الحصول على تحليل الصورة إذا تم توفير صورة
        image_analysis = None
        if request.image_path:
            crop_health_tool = tools["crop_health"]
            image_analysis = await crop_health_tool.analyze_image(
                image_path=request.image_path, crop_type=request.crop_type
            )

        # Diagnose disease
        # تشخيص المرض
        result = await disease_expert.diagnose(
            symptoms=request.symptoms,
            crop_type=request.crop_type,
            image_analysis=image_analysis,
        )

        return AgentResponse(status="success", data=result)

    except Exception as e:
        logger.error("diagnose_disease_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/v1/advisor/recommend", response_model=AgentResponse, tags=["Advisor"])
async def get_recommendations(request: RecommendationRequest):
    """
    Get agricultural recommendations
    الحصول على توصيات زراعية

    Routes to appropriate agent based on recommendation type.
    يوجه إلى الوكيل المناسب بناءً على نوع التوصية.
    """
    try:
        agents = app_state.get("agents")
        if not agents:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not initialized",
            )

        # Route to appropriate agent
        # التوجيه إلى الوكيل المناسب
        if request.recommendation_type == "irrigation":
            agent = agents["irrigation_advisor"]
            result = await agent.recommend_irrigation(
                crop_type=request.crop_type,
                growth_stage=request.growth_stage,
                soil_data=(
                    request.field_data.get("soil", {}) if request.field_data else {}
                ),
                weather_data=(
                    request.field_data.get("weather", {}) if request.field_data else {}
                ),
            )
        elif request.recommendation_type in ["fertilizer", "pest"]:
            supervisor = app_state.get("supervisor")
            result = await supervisor.coordinate(
                query=f"Provide {request.recommendation_type} recommendations for {request.crop_type} at {request.growth_stage}",
                context={"field_data": request.field_data},
                specific_agents=["disease_expert"],
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown recommendation type: {request.recommendation_type}",
            )

        return AgentResponse(status="success", data=result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_recommendations_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/v1/advisor/analyze-field", response_model=AgentResponse, tags=["Advisor"])
async def analyze_field(request: FieldAnalysisRequest):
    """
    Comprehensive field analysis
    تحليل شامل للحقل

    Coordinates multiple agents for complete field assessment.
    ينسق وكلاء متعددين لتقييم شامل للحقل.
    """
    try:
        agents = app_state.get("agents")
        tools = app_state.get("tools")

        if not agents or not tools:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not initialized",
            )

        results = {}

        # Get satellite data
        # الحصول على بيانات الأقمار الصناعية
        satellite_tool = tools["satellite"]
        satellite_data = await satellite_tool.get_ndvi(field_id=request.field_id)
        results["satellite_data"] = satellite_data

        # Field analysis
        # تحليل الحقل
        field_analyst = agents["field_analyst"]
        field_analysis = await field_analyst.analyze_field(
            field_id=request.field_id,
            satellite_data=satellite_data,
        )
        results["field_analysis"] = field_analysis

        # Disease check
        # فحص الأمراض
        if request.include_disease_check:
            disease_expert = agents["disease_expert"]
            disease_risk = await disease_expert.assess_risk(
                crop_type=request.crop_type,
                location=request.field_id,
                season="current",
                environmental_conditions=satellite_data,
            )
            results["disease_risk"] = disease_risk

        # Irrigation advice
        # نصائح الري
        if request.include_irrigation:
            irrigation_advisor = agents["irrigation_advisor"]
            irrigation_advice = await irrigation_advisor.recommend_irrigation(
                crop_type=request.crop_type,
                growth_stage="vegetative",  # Could be passed in request
                soil_data={},
                weather_data={},
            )
            results["irrigation_advice"] = irrigation_advice

        # Yield prediction
        # التنبؤ بالمحصول
        if request.include_yield_prediction:
            yield_predictor = agents["yield_predictor"]
            yield_prediction = await yield_predictor.predict_yield(
                crop_type=request.crop_type,
                area=1.0,  # Could be passed in request
                growth_stage="vegetative",
                field_data=field_analysis,
                weather_data={},
            )
            results["yield_prediction"] = yield_prediction

        return AgentResponse(
            status="success",
            data={
                "field_id": request.field_id,
                "crop_type": request.crop_type,
                "analysis": results,
            },
        )

    except Exception as e:
        logger.error("analyze_field_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/v1/advisor/agents", tags=["Advisor"])
async def list_agents():
    """
    List available agents
    قائمة الوكلاء المتاحين

    Returns information about all available AI agents.
    يعيد معلومات حول جميع وكلاء الذكاء الاصطناعي المتاحين.
    """
    try:
        supervisor = app_state.get("supervisor")
        if not supervisor:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not initialized",
            )

        agents_info = supervisor.get_available_agents()

        return {
            "status": "success",
            "agents": agents_info,
            "total": len(agents_info),
        }

    except Exception as e:
        logger.error("list_agents_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/v1/advisor/tools", tags=["Advisor"])
async def list_tools():
    """
    List available external tools
    قائمة الأدوات الخارجية المتاحة
    """
    tools = app_state.get("tools", {})

    return {
        "status": "success",
        "tools": list(tools.keys()),
        "total": len(tools),
    }


@app.get("/v1/advisor/rag/info", tags=["RAG"])
async def get_rag_info():
    """
    Get RAG system information
    الحصول على معلومات نظام RAG
    """
    try:
        retriever = app_state.get("retriever")
        embeddings = app_state.get("embeddings")

        if not retriever or not embeddings:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG system not initialized",
            )

        collection_info = retriever.get_collection_info()
        model_info = embeddings.get_model_info()

        return {
            "status": "success",
            "collection": collection_info,
            "embeddings_model": model_info,
        }

    except Exception as e:
        logger.error("get_rag_info_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/v1/advisor/cost/usage", tags=["Monitoring"])
async def get_cost_usage(user_id: str | None = None):
    """
    Get LLM cost usage statistics
    الحصول على إحصائيات تكلفة استخدام نماذج اللغة

    Args:
        user_id: Optional user ID to filter statistics
    """
    try:
        stats = cost_tracker.get_usage_stats(user_id=user_id)

        return {
            "status": "success",
            "data": {
                "daily_cost_usd": round(stats["daily_cost"], 4),
                "monthly_cost_usd": round(stats["monthly_cost"], 4),
                "daily_limit_usd": stats["daily_limit"],
                "monthly_limit_usd": stats["monthly_limit"],
                "total_requests": stats["total_requests"],
                "daily_remaining_usd": round(stats["daily_limit"] - stats["daily_cost"], 4),
                "monthly_remaining_usd": round(stats["monthly_limit"] - stats["monthly_cost"], 4),
                "daily_usage_percent": round((stats["daily_cost"] / stats["daily_limit"]) * 100, 2) if stats["daily_limit"] > 0 else 0,
                "monthly_usage_percent": round((stats["monthly_cost"] / stats["monthly_limit"]) * 100, 2) if stats["monthly_limit"] > 0 else 0,
            },
            "user_id": user_id or "anonymous",
        }
    except Exception as e:
        logger.error("get_cost_usage_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.service_port,
        log_level=settings.log_level.lower(),
        reload=False,
    )
