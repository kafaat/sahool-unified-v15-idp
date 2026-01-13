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
)
from .monitoring import cost_tracker
from .orchestration import Supervisor
from .rag import EmbeddingsManager, KnowledgeRetriever
from .security import PromptGuard
from .tools import AgroTool, CropHealthTool, SatelliteTool, WeatherTool
from .utils import pii_masking_processor

# Import context engineering modules | استيراد وحدات هندسة السياق
try:
    from shared.ai.context_engineering.compression import (
        CompressionStrategy,
        ContextCompressor,
    )
    from shared.ai.context_engineering.evaluation import (
        EvaluationCriteria,
        RecommendationType,
        RecommendationEvaluator,
    )
    from shared.ai.context_engineering.memory import (
        FarmMemory,
        MemoryConfig,
        MemoryType,
        RelevanceScore,
    )

    CONTEXT_ENGINEERING_AVAILABLE = True
except ImportError:
    CONTEXT_ENGINEERING_AVAILABLE = False
    logger = structlog.get_logger()
    logger.warning("Context engineering modules not available")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.errors_py import setup_exception_handlers

from shared.middleware import (
    RequestLoggingMiddleware,
    TenantContextMiddleware,
    setup_cors,
)
from shared.observability.middleware import ObservabilityMiddleware

from .middleware import RateLimitMiddleware, rate_limiter

# Configure structured logging with PII masking | تكوين السجلات المنظمة مع إخفاء المعلومات الشخصية
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        pii_masking_processor,  # Mask PII before rendering
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
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

# Import Token Revocation Support | استيراد دعم إلغاء الرموز
try:
    from auth.revocation_middleware import TokenRevocationMiddleware
    from auth.token_revocation import get_revocation_store

    REVOCATION_AVAILABLE = True
except ImportError:
    REVOCATION_AVAILABLE = False
    logger.warning("Token revocation support not available")


# Pydantic models for requests/responses
# نماذج Pydantic للطلبات/الاستجابات


class QuestionRequest(BaseModel):
    """General question request | طلب سؤال عام"""

    question: str = Field(..., description="User question")
    language: str = Field(default="en", description="Response language (en/ar)")
    context: dict[str, Any] | None = Field(default=None, description="Additional context")


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
    recommendation_type: str = Field(..., description="Type (irrigation/fertilizer/pest)")
    field_data: dict[str, Any] | None = Field(default=None, description="Field data")


class FieldAnalysisRequest(BaseModel):
    """Field analysis request | طلب تحليل حقل"""

    field_id: str = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Type of crop")
    include_disease_check: bool = Field(default=True, description="Include disease analysis")
    include_irrigation: bool = Field(default=True, description="Include irrigation advice")
    include_yield_prediction: bool = Field(default=True, description="Include yield prediction")


class AgentResponse(BaseModel):
    """Agent response model | نموذج استجابة الوكيل"""

    status: str
    data: dict[str, Any] | None = None
    error: str | None = None


class CompressionInfo(BaseModel):
    """Context compression information | معلومات ضغط السياق"""

    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    savings_percentage: float
    strategy: str | None = None


class EvaluationInfo(BaseModel):
    """Recommendation evaluation information | معلومات تقييم التوصيات"""

    overall_score: float
    grade: str
    is_approved: bool
    feedback: str
    improvements: list[str]
    criteria_scores: dict[str, float] | None = None


class EnhancedAgentResponse(AgentResponse):
    """Enhanced agent response with compression and evaluation | استجابة وكيل محسنة"""

    compression: CompressionInfo | None = None
    evaluation: EvaluationInfo | None = None
    memory_stored: bool = False
    context_tokens_used: int | None = None


# Global instances | المثيلات العامة
app_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    مدير دورة حياة التطبيق
    """
    global CONTEXT_ENGINEERING_AVAILABLE

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

        irrigation_advisor = IrrigationAdvisorAgent(tools=[], retriever=knowledge_retriever)

        yield_predictor = YieldPredictorAgent(tools=[], retriever=knowledge_retriever)

        # Initialize supervisor | تهيئة المشرف
        agents = {
            "field_analyst": field_analyst,
            "disease_expert": disease_expert,
            "irrigation_advisor": irrigation_advisor,
            "yield_predictor": yield_predictor,
        }

        supervisor = Supervisor(agents=agents)

        # Initialize context engineering modules | تهيئة وحدات هندسة السياق
        context_compressor = None
        farm_memory = None
        recommendation_evaluator = None

        if CONTEXT_ENGINEERING_AVAILABLE:
            try:
                # Initialize compression | تهيئة الضغط
                context_compressor = ContextCompressor(
                    default_strategy=CompressionStrategy.HYBRID, max_tokens=4000
                )
                logger.info("context_compressor_initialized")

                # Initialize memory with tenant isolation | تهيئة الذاكرة مع عزل المستأجرين
                memory_config = MemoryConfig(
                    window_size=20,
                    max_entries=1000,
                    ttl_hours=24,
                    enable_compression=True,
                    persist_to_storage=False,
                )
                farm_memory = FarmMemory(config=memory_config)
                logger.info("farm_memory_initialized")

                # Initialize evaluator with heuristics fallback | تهيئة المُقيّم مع القواعس الاحتياطية
                recommendation_evaluator = RecommendationEvaluator(
                    llm_client=None,  # Will use heuristics fallback
                    passing_threshold=0.7,
                    use_heuristics_fallback=True,
                )
                logger.info("recommendation_evaluator_initialized")

            except Exception as e:
                logger.error("context_engineering_initialization_failed", error=str(e))
                # Continue without context engineering modules if initialization fails
                CONTEXT_ENGINEERING_AVAILABLE = False

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
        app_state["context_compressor"] = context_compressor
        app_state["farm_memory"] = farm_memory
        app_state["recommendation_evaluator"] = recommendation_evaluator

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

        # Initialize token revocation store | تهيئة مخزن إلغاء الرموز
        if REVOCATION_AVAILABLE:
            try:
                revocation_store = get_revocation_store()
                await revocation_store.initialize()
                app_state["revocation_store"] = revocation_store
                logger.info("token_revocation_store_initialized")
            except Exception as e:
                logger.error("token_revocation_initialization_failed", error=str(e))

        logger.info("ai_advisor_service_started_successfully")

    except Exception as e:
        logger.error("ai_advisor_service_startup_failed", error=str(e))
        raise

    yield

    # Shutdown | الإغلاق
    logger.info("ai_advisor_service_shutting_down")
    # Close revocation store
    if revocation_store := app_state.get("revocation_store"):
        await revocation_store.close()

    # Log memory and evaluation statistics | تسجيل إحصائيات الذاكرة والتقييم
    if farm_memory := app_state.get("farm_memory"):
        stats = farm_memory.get_stats()
        logger.info("farm_memory_stats", **stats)

    if evaluator := app_state.get("recommendation_evaluator"):
        stats = evaluator.get_stats()
        logger.info("evaluation_stats", **stats)

    app_state.clear()


# Create FastAPI app | إنشاء تطبيق FastAPI
app = FastAPI(
    title="AI Advisor Service",
    description="Multi-agent AI system for agricultural advisory",
    version="1.0.0",
    lifespan=lifespan,
)

# Setup unified error handling
setup_exception_handlers(app)

# ============== Middleware Setup ==============
# Middleware order: Last added = First executed

# 1. CORS - Secure cross-origin configuration
setup_cors(app)

# 2. Observability - Tracing, metrics, and monitoring (with cost tracking)
app.add_middleware(
    ObservabilityMiddleware,
    service_name="ai-advisor",
    metrics_collector=cost_tracker,  # Use cost tracker for metrics
)

# 3. Request Logging - Correlation IDs and structured logging
app.add_middleware(
    RequestLoggingMiddleware,
    service_name="ai-advisor",
    log_request_body=os.getenv("LOG_REQUEST_BODY", "false").lower() == "true",
    log_response_body=False,
)

# 4. Tenant Context - Multi-tenancy isolation
app.add_middleware(
    TenantContextMiddleware,
    require_tenant=False,  # Some endpoints don't require tenant
    exempt_paths=["/healthz", "/docs", "/redoc", "/openapi.json"],
)

# 5. Input validation middleware - Security validation
app.add_middleware(InputValidationMiddleware)

# 6. Rate limiting middleware - Prevent abuse of AI endpoints
app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter)

# 7. Token revocation middleware - Check if tokens are revoked
if REVOCATION_AVAILABLE:
    app.add_middleware(
        TokenRevocationMiddleware,
        exempt_paths=["/healthz", "/health", "/docs", "/redoc", "/openapi.json", "/a2a"],
    )

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
    embeddings_ok = app_state.get("embeddings") is not None
    retriever_ok = app_state.get("retriever") is not None
    agents = app_state.get("agents", {})
    agents_count = len([a for a in agents.values() if a])

    is_healthy = embeddings_ok or retriever_ok or agents_count > 0

    return {
        "status": "healthy" if is_healthy else "degraded",
        "service": settings.service_name,
        "version": "1.0.0",
        "embeddings_ready": embeddings_ok,
        "retriever_ready": retriever_ok,
        "agents_available": agents_count,
    }


@app.post("/v1/advisor/ask", response_model=EnhancedAgentResponse, tags=["Advisor"])
async def ask_question(request: QuestionRequest):
    """
    Ask a general question to the AI advisor
    طرح سؤال عام على المستشار الذكي

    The supervisor will route the question to appropriate agents.
    Responses are compressed to optimize context window usage.
    سيوجه المشرف السؤال إلى الوكلاء المناسبين.
    يتم ضغط الاستجابات لتحسين استخدام نافذة السياق.
    """
    try:
        supervisor = app_state.get("supervisor")
        context_compressor = app_state.get("context_compressor")
        farm_memory = app_state.get("farm_memory")

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

        # Compress context if available | ضغط السياق إذا كان متاحاً
        compression_info = None
        compressed_context = request.context

        if CONTEXT_ENGINEERING_AVAILABLE and context_compressor and request.context:
            try:
                compression_result = context_compressor.compress_field_data(
                    request.context, strategy=CompressionStrategy.HYBRID
                )
                compression_info = CompressionInfo(
                    original_tokens=compression_result.original_tokens,
                    compressed_tokens=compression_result.compressed_tokens,
                    compression_ratio=compression_result.compression_ratio,
                    savings_percentage=compression_result.savings_percentage,
                    strategy=compression_result.strategy.value,
                )
                compressed_context = {
                    "original": request.context,
                    "compressed": compression_result.compressed_text,
                }
                logger.info(
                    "context_compressed",
                    original_tokens=compression_result.original_tokens,
                    compressed_tokens=compression_result.compressed_tokens,
                    savings_pct=compression_result.savings_percentage,
                )
            except Exception as e:
                logger.warning("context_compression_failed", error=str(e))
                # Continue with original context if compression fails

        # Coordinate agents to answer
        # تنسيق الوكلاء للإجابة
        result = await supervisor.coordinate(
            query=sanitized_question,
            context=compressed_context or request.context,
        )

        # Store interaction in memory if available | تخزين التفاعل في الذاكرة إذا كان متاحاً
        memory_stored = False
        if CONTEXT_ENGINEERING_AVAILABLE and farm_memory and request.context:
            try:
                tenant_id = request.context.get(
                    "tenant_id", request.context.get("field_id", "default")
                )
                field_id = request.context.get("field_id")

                farm_memory.store(
                    tenant_id=tenant_id,
                    content={
                        "question": sanitized_question,
                        "response_summary": str(result).split("\n")[0][:200],
                    },
                    memory_type=MemoryType.CONVERSATION,
                    field_id=field_id,
                    relevance=RelevanceScore.HIGH,
                )
                memory_stored = True
                logger.info("conversation_stored_in_memory", tenant_id=tenant_id)
            except Exception as e:
                logger.warning("memory_storage_failed", error=str(e))
                # Continue even if memory storage fails

        return EnhancedAgentResponse(
            status="success",
            data=result,
            compression=compression_info,
            memory_stored=memory_stored,
        )

    except Exception as e:
        logger.error("ask_question_failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/v1/advisor/recommend", response_model=EnhancedAgentResponse, tags=["Advisor"])
async def get_recommendations(request: RecommendationRequest):
    """
    Get agricultural recommendations
    الحصول على توصيات زراعية

    Routes to appropriate agent based on recommendation type.
    Evaluates recommendations for quality and stores in memory.
    يوجه إلى الوكيل المناسب بناءً على نوع التوصية.
    يقيم التوصيات من حيث الجودة ويخزنها في الذاكرة.
    """
    try:
        agents = app_state.get("agents")
        farm_memory = app_state.get("farm_memory")
        recommendation_evaluator = app_state.get("recommendation_evaluator")

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
                soil_data=(request.field_data.get("soil", {}) if request.field_data else {}),
                weather_data=(request.field_data.get("weather", {}) if request.field_data else {}),
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

        # Evaluate recommendation if evaluator is available | تقييم التوصية إذا كان المقيم متاحاً
        evaluation_info = None
        if CONTEXT_ENGINEERING_AVAILABLE and recommendation_evaluator and result:
            try:
                recommendation_text = str(result).split("\n")[0] if isinstance(result, dict) else str(result)

                # Map recommendation type to evaluation type | تعيين نوع التوصية إلى نوع التقييم
                type_mapping = {
                    "irrigation": RecommendationType.IRRIGATION,
                    "fertilizer": RecommendationType.FERTILIZATION,
                    "pest": RecommendationType.PEST_CONTROL,
                }
                eval_type = type_mapping.get(request.recommendation_type, RecommendationType.GENERAL)

                eval_result = recommendation_evaluator.evaluate(
                    recommendation=recommendation_text,
                    context=request.field_data,
                    query=f"Provide {request.recommendation_type} for {request.crop_type}",
                    recommendation_type=eval_type,
                )

                evaluation_info = EvaluationInfo(
                    overall_score=eval_result.overall_score,
                    grade=eval_result.grade.value,
                    is_approved=eval_result.is_approved,
                    feedback=eval_result.feedback,
                    improvements=eval_result.improvements,
                    criteria_scores={
                        k.value: v.score for k, v in eval_result.scores.items()
                    },
                )

                logger.info(
                    "recommendation_evaluated",
                    type=request.recommendation_type,
                    score=eval_result.overall_score,
                    approved=eval_result.is_approved,
                )
            except Exception as e:
                logger.warning("recommendation_evaluation_failed", error=str(e))
                # Continue even if evaluation fails

        # Store recommendation in memory if available | تخزين التوصية في الذاكرة إذا كان متاحاً
        memory_stored = False
        if CONTEXT_ENGINEERING_AVAILABLE and farm_memory:
            try:
                tenant_id = request.field_data.get("tenant_id", "default") if request.field_data else "default"
                field_id = request.field_data.get("field_id") if request.field_data else None

                # Determine relevance based on evaluation
                relevance = RelevanceScore.HIGH
                if evaluation_info and not evaluation_info.is_approved:
                    relevance = RelevanceScore.MEDIUM

                farm_memory.store(
                    tenant_id=tenant_id,
                    content={
                        "type": request.recommendation_type,
                        "crop_type": request.crop_type,
                        "growth_stage": request.growth_stage,
                        "recommendation": str(result).split("\n")[0][:300],
                        "approved": evaluation_info.is_approved if evaluation_info else None,
                    },
                    memory_type=MemoryType.RECOMMENDATION,
                    field_id=field_id,
                    relevance=relevance,
                )
                memory_stored = True
                logger.info("recommendation_stored_in_memory", tenant_id=tenant_id)
            except Exception as e:
                logger.warning("memory_storage_failed", error=str(e))
                # Continue even if memory storage fails

        return EnhancedAgentResponse(
            status="success",
            data=result,
            evaluation=evaluation_info,
            memory_stored=memory_stored,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_recommendations_failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/v1/advisor/analyze-field", response_model=EnhancedAgentResponse, tags=["Advisor"])
async def analyze_field(request: FieldAnalysisRequest):
    """
    Comprehensive field analysis
    تحليل شامل للحقل

    Coordinates multiple agents for complete field assessment.
    Results are compressed and stored in memory for future reference.
    ينسق وكلاء متعددين لتقييم شامل للحقل.
    يتم ضغط النتائج وتخزينها في الذاكرة للرجوع إليها لاحقاً.
    """
    try:
        agents = app_state.get("agents")
        tools = app_state.get("tools")
        context_compressor = app_state.get("context_compressor")
        farm_memory = app_state.get("farm_memory")

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

        # Compress field analysis results | ضغط نتائج تحليل الحقل
        compression_info = None
        if CONTEXT_ENGINEERING_AVAILABLE and context_compressor:
            try:
                compression_result = context_compressor.compress_field_data(
                    {"field_id": request.field_id, "crop_type": request.crop_type, **results},
                    strategy=CompressionStrategy.HYBRID,
                )
                compression_info = CompressionInfo(
                    original_tokens=compression_result.original_tokens,
                    compressed_tokens=compression_result.compressed_tokens,
                    compression_ratio=compression_result.compression_ratio,
                    savings_percentage=compression_result.savings_percentage,
                    strategy=compression_result.strategy.value,
                )
                logger.info(
                    "field_analysis_compressed",
                    field_id=request.field_id,
                    original_tokens=compression_result.original_tokens,
                    compressed_tokens=compression_result.compressed_tokens,
                )
            except Exception as e:
                logger.warning("field_analysis_compression_failed", error=str(e))
                # Continue even if compression fails

        # Store field state in memory | تخزين حالة الحقل في الذاكرة
        memory_stored = False
        if CONTEXT_ENGINEERING_AVAILABLE and farm_memory:
            try:
                farm_memory.store(
                    tenant_id="default",
                    content={
                        "crop_type": request.crop_type,
                        "ndvi": satellite_data.get("ndvi") if isinstance(satellite_data, dict) else None,
                        "analysis_summary": str(field_analysis).split("\n")[0][:200] if field_analysis else "",
                        "disease_risk_present": "disease_risk" in results,
                    },
                    memory_type=MemoryType.FIELD_STATE,
                    field_id=request.field_id,
                    relevance=RelevanceScore.CRITICAL,
                )
                memory_stored = True
                logger.info("field_state_stored_in_memory", field_id=request.field_id)
            except Exception as e:
                logger.warning("memory_storage_failed", error=str(e))
                # Continue even if memory storage fails

        response_data = {
            "field_id": request.field_id,
            "crop_type": request.crop_type,
            "analysis": results,
        }

        return EnhancedAgentResponse(
            status="success",
            data=response_data,
            compression=compression_info,
            memory_stored=memory_stored,
        )

    except Exception as e:
        logger.error("analyze_field_failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/v1/advisor/memory/context", tags=["Memory"])
async def get_memory_context(
    tenant_id: str | None = None,
    field_id: str | None = None,
    query: str | None = None,
    max_tokens: int = 2000,
):
    """
    Retrieve relevant context from memory
    استرجاع السياق ذي الصلة من الذاكرة

    Returns relevant memory entries for a given query.
    يعيد إدخالات الذاكرة ذات الصلة للاستعلام المعطى.
    """
    try:
        farm_memory = app_state.get("farm_memory")

        if not CONTEXT_ENGINEERING_AVAILABLE or not farm_memory:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Memory system not available",
            )

        if not tenant_id:
            tenant_id = "default"

        if not query:
            query = "all"

        context = farm_memory.get_relevant_context(
            tenant_id=tenant_id,
            query=query,
            field_id=field_id,
            max_tokens=max_tokens,
        )

        # Also get sliding window for recent entries
        window_entries = farm_memory.get_sliding_window(
            tenant_id=tenant_id,
            field_id=field_id,
        )

        return {
            "status": "success",
            "tenant_id": tenant_id,
            "field_id": field_id,
            "context": context,
            "recent_entries_count": len(window_entries),
            "memory_stats": farm_memory.get_stats(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_memory_context_failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/v1/advisor/evaluation/stats", tags=["Evaluation"])
async def get_evaluation_stats():
    """
    Get recommendation evaluation statistics
    الحصول على إحصائيات تقييم التوصيات

    Returns statistics about evaluated recommendations.
    يعيد إحصائيات التوصيات المقيمة.
    """
    try:
        evaluator = app_state.get("recommendation_evaluator")

        if not CONTEXT_ENGINEERING_AVAILABLE or not evaluator:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Evaluation system not available",
            )

        stats = evaluator.get_stats()

        return {
            "status": "success",
            "evaluation_stats": stats,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_evaluation_stats_failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/v1/advisor/context-engineering/status", tags=["System"])
async def get_context_engineering_status():
    """
    Get context engineering modules status
    الحصول على حالة وحدات هندسة السياق
    """
    compressor = app_state.get("context_compressor")
    memory = app_state.get("farm_memory")
    evaluator = app_state.get("recommendation_evaluator")

    memory_stats = memory.get_stats() if memory else None
    eval_stats = evaluator.get_stats() if evaluator else None

    return {
        "status": "success",
        "context_engineering_available": CONTEXT_ENGINEERING_AVAILABLE,
        "modules": {
            "compression": {
                "available": compressor is not None,
                "type": "ContextCompressor",
            },
            "memory": {
                "available": memory is not None,
                "type": "FarmMemory",
                "stats": memory_stats,
            },
            "evaluation": {
                "available": evaluator is not None,
                "type": "RecommendationEvaluator",
                "stats": eval_stats,
            },
        },
    }


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
                "daily_usage_percent": round((stats["daily_cost"] / stats["daily_limit"]) * 100, 2)
                if stats["daily_limit"] > 0
                else 0,
                "monthly_usage_percent": round(
                    (stats["monthly_cost"] / stats["monthly_limit"]) * 100, 2
                )
                if stats["monthly_limit"] > 0
                else 0,
            },
            "user_id": user_id or "anonymous",
        }
    except Exception as e:
        logger.error("get_cost_usage_failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.service_port,
        log_level=settings.log_level.lower(),
        reload=False,
    )
