"""
Agricultural AI Model Integrator
=================================
مُدمج نماذج الذكاء الاصطناعي الزراعي

Integrator for discovering, selecting, and calling agricultural AI models.
Provides intelligent model selection based on task requirements and
supports model comparison for optimal results.

Philosophy:
- "让知识流动" (Let Knowledge Flow) - LLM consultants democratize agricultural expertise
- "让计算创造" (Let Computation Create) - Bio/remote sensing models enable precision agriculture
- Future: From "advice" to "Agent execution" - autonomous farm operations

Author: SAHOOL Platform Team
Updated: January 2026
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from .models import (
    AIModelCategory,
    AIModelInfo,
    ModelCapability,
    ModelComparison,
    ModelDiscoveryResult,
    ModelStatus,
)
from .registry import AgriculturalAIRegistry, get_registry

logger = logging.getLogger(__name__)


class TaskType(str, Enum):
    """Types of agricultural tasks.

    أنواع المهام الزراعية
    农业任务类型
    """

    # Advisory Tasks | المهام الاستشارية | 咨询任务
    CROP_ADVISORY = "crop_advisory"                 # Crop management advice
    PEST_IDENTIFICATION = "pest_identification"     # Pest identification
    DISEASE_DIAGNOSIS = "disease_diagnosis"         # Disease diagnosis
    FERTILIZER_RECOMMENDATION = "fertilizer_recommendation"  # Fertilizer advice
    IRRIGATION_SCHEDULING = "irrigation_scheduling" # Irrigation planning

    # Analysis Tasks | مهام التحليل | 分析任务
    YIELD_PREDICTION = "yield_prediction"           # Yield prediction
    SATELLITE_ANALYSIS = "satellite_analysis"       # Satellite image analysis
    SOIL_ANALYSIS = "soil_analysis"                 # Soil analysis
    WEATHER_IMPACT = "weather_impact"               # Weather impact assessment

    # Breeding Tasks | مهام التربية | 育种任务
    BREEDING_RECOMMENDATION = "breeding_recommendation"  # Breeding advice
    GENOMICS_ANALYSIS = "genomics_analysis"         # Genomics analysis
    PHENOTYPE_PREDICTION = "phenotype_prediction"   # Phenotype prediction

    # Livestock Tasks | مهام الثروة الحيوانية | 畜牧任务
    ANIMAL_HEALTH = "animal_health"                 # Animal health
    VETERINARY_QA = "veterinary_qa"                 # Veterinary Q&A
    FEED_OPTIMIZATION = "feed_optimization"         # Feed optimization

    # Specialty Tasks | المهام المتخصصة | 专业任务
    FORESTRY_MANAGEMENT = "forestry_management"     # Forestry
    TEA_CULTIVATION = "tea_cultivation"             # Tea cultivation
    LEGAL_QA = "legal_qa"                           # Agricultural law


# Task to capability mapping
TASK_CAPABILITY_MAP: dict[TaskType, list[ModelCapability]] = {
    TaskType.CROP_ADVISORY: [ModelCapability.QA, ModelCapability.DECISION_SUPPORT],
    TaskType.PEST_IDENTIFICATION: [ModelCapability.PEST_DETECTION],
    TaskType.DISEASE_DIAGNOSIS: [ModelCapability.DISEASE_DETECTION],
    TaskType.FERTILIZER_RECOMMENDATION: [ModelCapability.DECISION_SUPPORT],
    TaskType.IRRIGATION_SCHEDULING: [ModelCapability.DECISION_SUPPORT],
    TaskType.YIELD_PREDICTION: [ModelCapability.YIELD_PREDICTION],
    TaskType.SATELLITE_ANALYSIS: [ModelCapability.SATELLITE_ANALYSIS, ModelCapability.NDVI_ANALYSIS],
    TaskType.SOIL_ANALYSIS: [ModelCapability.SOIL_ANALYSIS],
    TaskType.WEATHER_IMPACT: [ModelCapability.WEATHER_FORECAST, ModelCapability.CLIMATE_MODELING],
    TaskType.BREEDING_RECOMMENDATION: [ModelCapability.BREEDING],
    TaskType.GENOMICS_ANALYSIS: [ModelCapability.GENOMICS],
    TaskType.PHENOTYPE_PREDICTION: [ModelCapability.PHENOTYPE_PREDICTION],
    TaskType.ANIMAL_HEALTH: [ModelCapability.ANIMAL_HEALTH],
    TaskType.VETERINARY_QA: [ModelCapability.VETERINARY_QA],
    TaskType.FEED_OPTIMIZATION: [ModelCapability.FEED_OPTIMIZATION],
    TaskType.FORESTRY_MANAGEMENT: [ModelCapability.FORESTRY],
    TaskType.TEA_CULTIVATION: [ModelCapability.TEA_CULTIVATION],
    TaskType.LEGAL_QA: [ModelCapability.LEGAL_QA],
}


@dataclass
class ModelCallResult:
    """Result of calling a model.

    نتيجة استدعاء النموذج
    模型调用结果
    """

    model_id: str
    model_name: str
    success: bool
    response: str | None = None
    error: str | None = None
    latency_ms: float = 0.0
    tokens_used: int | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "success": self.success,
            "response": self.response,
            "error": self.error,
            "latency_ms": self.latency_ms,
            "tokens_used": self.tokens_used,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ModelSelection:
    """Result of model selection for a task.

    نتيجة اختيار النموذج للمهمة
    任务模型选择结果
    """

    recommended_model: AIModelInfo
    alternatives: list[AIModelInfo] = field(default_factory=list)
    selection_criteria: dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    explanation: str = ""
    explanation_ar: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "recommended_model": self.recommended_model.model_id,
            "alternatives": [m.model_id for m in self.alternatives],
            "selection_criteria": self.selection_criteria,
            "confidence_score": self.confidence_score,
            "explanation": self.explanation,
            "explanation_ar": self.explanation_ar,
            "timestamp": self.timestamp.isoformat(),
        }


class ModelIntegrator:
    """Integrator for agricultural AI models.

    مُدمج نماذج الذكاء الاصطناعي الزراعي
    农业AI模型集成器

    Provides model discovery, selection, and orchestration capabilities
    for the SAHOOL agricultural platform.

    Key Features:
    - Model discovery by category, capability, and language
    - Intelligent model selection based on task requirements
    - Model availability checking
    - Model comparison for quality assessment
    - Multi-model orchestration

    Philosophy (from the article):
    - "让知识流动" (Let Knowledge Flow): LLM consultants democratize expertise
    - "让计算创造" (Let Computation Create): Bio/RS models enable precision
    - Future direction: From "advice" to "Agent execution"
    """

    def __init__(
        self,
        registry: AgriculturalAIRegistry | None = None,
        default_language: str = "en",
    ):
        """Initialize the integrator.

        Args:
            registry: Model registry to use (uses singleton if not provided)
            default_language: Default language for model selection
        """
        self._registry = registry or get_registry()
        self._default_language = default_language
        self._connectors: dict[str, Any] = {}  # model_id -> connector
        self._availability_cache: dict[str, tuple[bool, float]] = {}  # model_id -> (available, timestamp)
        self._cache_ttl = 300  # 5 minutes

    # ========================================================================
    # Model Discovery
    # ========================================================================

    def discover_models(
        self,
        category: AIModelCategory | None = None,
        capability: ModelCapability | None = None,
        language: str | None = None,
    ) -> ModelDiscoveryResult:
        """Discover models matching criteria.

        اكتشاف النماذج المطابقة للمعايير
        发现匹配条件的模型

        Args:
            category: Filter by category
            capability: Filter by capability
            language: Filter by language support

        Returns:
            ModelDiscoveryResult with matching models
        """
        if category and not capability and not language:
            return self._registry.discover_by_category(category)

        if capability and not category and not language:
            return self._registry.discover_by_capability(capability)

        if language and not category and not capability:
            return self._registry.discover_by_language(language)

        # Multi-criteria search
        capabilities = [capability] if capability else None
        return self._registry.search(
            category=category,
            capabilities=capabilities,
            language=language,
        )

    def discover_for_task(
        self,
        task_type: TaskType,
        language: str | None = None,
    ) -> ModelDiscoveryResult:
        """Discover models suitable for a specific task type.

        اكتشاف النماذج المناسبة لنوع مهمة معين
        发现适合特定任务类型的模型

        Args:
            task_type: Type of agricultural task
            language: Preferred language

        Returns:
            ModelDiscoveryResult with suitable models
        """
        capabilities = TASK_CAPABILITY_MAP.get(task_type, [])

        return self._registry.search(
            capabilities=capabilities if capabilities else None,
            language=language or self._default_language,
            status=ModelStatus.ACTIVE,
        )

    def get_available_models(self) -> ModelDiscoveryResult:
        """Get all currently available models.

        الحصول على جميع النماذج المتاحة حاليا
        获取所有当前可用的模型
        """
        return self._registry.discover_available()

    def get_open_source_models(self) -> ModelDiscoveryResult:
        """Get all open source models.

        الحصول على جميع النماذج مفتوحة المصدر
        获取所有开源模型
        """
        return self._registry.discover_open_source()

    # ========================================================================
    # Model Selection
    # ========================================================================

    def get_best_model_for_task(
        self,
        task_type: TaskType,
        language: str | None = None,
        prefer_open_source: bool = False,
        prefer_local: bool = False,
    ) -> ModelSelection:
        """Select the best model for a given task.

        اختيار أفضل نموذج لمهمة معينة
        为给定任务选择最佳模型

        Args:
            task_type: Type of agricultural task
            language: Preferred language
            prefer_open_source: Prefer open source models
            prefer_local: Prefer locally deployable models

        Returns:
            ModelSelection with recommended model and alternatives
        """
        language = language or self._default_language
        discovery = self.discover_for_task(task_type, language)

        if not discovery.models:
            # Fallback to any available model with QA capability
            discovery = self._registry.search(
                capabilities=[ModelCapability.QA],
                status=ModelStatus.ACTIVE,
            )

        if not discovery.models:
            raise ValueError(f"No models found for task: {task_type.value}")

        # Score and rank models
        scored_models: list[tuple[float, AIModelInfo]] = []
        for model in discovery.models:
            score = self._calculate_model_score(
                model,
                task_type,
                language,
                prefer_open_source,
                prefer_local,
            )
            scored_models.append((score, model))

        # Sort by score descending
        scored_models.sort(key=lambda x: x[0], reverse=True)

        best_score, best_model = scored_models[0]
        alternatives = [m for _, m in scored_models[1:5]]  # Top 4 alternatives

        explanation = self._generate_selection_explanation(
            best_model, task_type, language
        )

        return ModelSelection(
            recommended_model=best_model,
            alternatives=alternatives,
            selection_criteria={
                "task_type": task_type.value,
                "language": language,
                "prefer_open_source": prefer_open_source,
                "prefer_local": prefer_local,
            },
            confidence_score=best_score,
            explanation=explanation["en"],
            explanation_ar=explanation["ar"],
        )

    def _calculate_model_score(
        self,
        model: AIModelInfo,
        task_type: TaskType,
        language: str,
        prefer_open_source: bool,
        prefer_local: bool,
    ) -> float:
        """Calculate a score for model selection."""
        score = 0.0

        # Capability match (40%)
        required_caps = TASK_CAPABILITY_MAP.get(task_type, [])
        if required_caps:
            matching_caps = sum(1 for cap in required_caps if cap in model.capabilities)
            score += (matching_caps / len(required_caps)) * 40

        # Language support (20%)
        if model.supports_language(language):
            score += 20

        # Status (15%)
        if model.status == ModelStatus.ACTIVE:
            score += 15
        elif model.status == ModelStatus.BETA:
            score += 10

        # Open source preference (10%)
        from .models import ModelLicense
        if prefer_open_source and model.license == ModelLicense.OPEN_SOURCE:
            score += 10

        # Local deployability preference (10%)
        if prefer_local:
            if model.github_url or model.huggingface_url:
                score += 10

        # Has endpoint (5%)
        if model.endpoint:
            score += 5

        return score

    def _generate_selection_explanation(
        self,
        model: AIModelInfo,
        task_type: TaskType,
        language: str,
    ) -> dict[str, str]:
        """Generate explanation for model selection."""
        # English explanation
        en_parts = [f"Selected {model.name} for {task_type.value.replace('_', ' ')}."]

        if model.supports_language(language):
            en_parts.append(f"Model supports {language}.")

        if model.developer:
            en_parts.append(f"Developed by {model.developer.name}.")

        if model.description:
            en_parts.append(model.description[:100] + "...")

        # Arabic explanation
        ar_parts = [f"تم اختيار {model.name_ar or model.name} للمهمة."]

        if model.supports_language("ar"):
            ar_parts.append("النموذج يدعم اللغة العربية.")

        if model.developer and model.developer.name_ar:
            ar_parts.append(f"تم تطويره بواسطة {model.developer.name_ar}.")

        return {
            "en": " ".join(en_parts),
            "ar": " ".join(ar_parts),
        }

    # ========================================================================
    # Model Availability
    # ========================================================================

    async def check_availability(self, model_id: str) -> bool:
        """Check if a model is currently available.

        التحقق مما إذا كان النموذج متاحا حاليا
        检查模型当前是否可用

        Args:
            model_id: ID of the model to check

        Returns:
            True if model is available
        """
        # Check cache
        if model_id in self._availability_cache:
            available, timestamp = self._availability_cache[model_id]
            if time.time() - timestamp < self._cache_ttl:
                return available

        # Check model exists
        model = self._registry.get(model_id)
        if not model:
            return False

        # Check status
        if not model.is_available():
            self._availability_cache[model_id] = (False, time.time())
            return False

        # Try to get connector and check
        try:
            connector = self._get_or_create_connector(model)
            if connector and hasattr(connector, "is_available"):
                available = await connector.is_available()
                self._availability_cache[model_id] = (available, time.time())
                return available
        except Exception as e:
            logger.warning(f"Error checking availability for {model_id}: {e}")

        # Default to status-based availability
        available = model.is_available()
        self._availability_cache[model_id] = (available, time.time())
        return available

    def get_model_endpoint(self, model_id: str) -> str | None:
        """Get the API endpoint for a model.

        الحصول على نقطة نهاية API للنموذج
        获取模型的API端点

        Args:
            model_id: ID of the model

        Returns:
            Endpoint URL or None
        """
        model = self._registry.get(model_id)
        if model and model.endpoint:
            return model.endpoint.url
        if model and model.url:
            return model.url
        return None

    # ========================================================================
    # Model Calling
    # ========================================================================

    async def call_model(
        self,
        model_id: str,
        query: str,
        context: dict[str, Any] | None = None,
        timeout: float = 60.0,
    ) -> ModelCallResult:
        """Call a model with a query.

        استدعاء نموذج مع استعلام
        使用查询调用模型

        Args:
            model_id: ID of the model to call
            query: Query/prompt to send
            context: Additional context
            timeout: Request timeout in seconds

        Returns:
            ModelCallResult with response or error
        """
        start_time = time.time()

        model = self._registry.get(model_id)
        if not model:
            return ModelCallResult(
                model_id=model_id,
                model_name="Unknown",
                success=False,
                error=f"Model not found: {model_id}",
                latency_ms=(time.time() - start_time) * 1000,
            )

        try:
            connector = self._get_or_create_connector(model)
            if not connector:
                return ModelCallResult(
                    model_id=model_id,
                    model_name=model.name,
                    success=False,
                    error="No connector available for this model",
                    latency_ms=(time.time() - start_time) * 1000,
                )

            # Call the model
            response = await asyncio.wait_for(
                connector.call(query, context),
                timeout=timeout,
            )

            latency_ms = (time.time() - start_time) * 1000

            return ModelCallResult(
                model_id=model_id,
                model_name=model.name,
                success=True,
                response=response.get("text", str(response)),
                latency_ms=latency_ms,
                tokens_used=response.get("tokens_used"),
            )

        except asyncio.TimeoutError:
            return ModelCallResult(
                model_id=model_id,
                model_name=model.name,
                success=False,
                error=f"Request timed out after {timeout}s",
                latency_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            logger.error(f"Error calling model {model_id}: {e}")
            return ModelCallResult(
                model_id=model_id,
                model_name=model.name,
                success=False,
                error=str(e),
                latency_ms=(time.time() - start_time) * 1000,
            )

    # ========================================================================
    # Model Comparison
    # ========================================================================

    async def compare_models(
        self,
        query: str,
        model_ids: list[str],
        context: dict[str, Any] | None = None,
        timeout: float = 60.0,
    ) -> ModelComparison:
        """Compare responses from multiple models.

        مقارنة الردود من نماذج متعددة
        比较多个模型的响应

        Args:
            query: Query to send to all models
            model_ids: List of model IDs to compare
            context: Additional context
            timeout: Request timeout per model

        Returns:
            ModelComparison with all responses and scores
        """
        models = []
        for model_id in model_ids:
            model = self._registry.get(model_id)
            if model:
                models.append(model)

        if not models:
            raise ValueError("No valid models found for comparison")

        # Call all models concurrently
        tasks = [
            self.call_model(model.model_id, query, context, timeout)
            for model in models
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        responses: dict[str, str] = {}
        latencies: dict[str, float] = {}
        scores: dict[str, float] = {}

        for model, result in zip(models, results):
            if isinstance(result, Exception):
                responses[model.model_id] = f"Error: {result}"
                latencies[model.model_id] = 0.0
                scores[model.model_id] = 0.0
            elif isinstance(result, ModelCallResult):
                if result.success:
                    responses[model.model_id] = result.response or ""
                    latencies[model.model_id] = result.latency_ms
                    # Simple score based on response length and latency
                    scores[model.model_id] = self._calculate_response_score(result)
                else:
                    responses[model.model_id] = f"Error: {result.error}"
                    latencies[model.model_id] = result.latency_ms
                    scores[model.model_id] = 0.0

        # Determine winner
        winner = max(scores.items(), key=lambda x: x[1])[0] if scores else None

        return ModelComparison(
            query=query,
            models=models,
            responses=responses,
            latencies=latencies,
            scores=scores,
            winner=winner,
            comparison_criteria=["response_quality", "latency", "completeness"],
        )

    def _calculate_response_score(self, result: ModelCallResult) -> float:
        """Calculate a quality score for a model response."""
        if not result.success or not result.response:
            return 0.0

        score = 50.0  # Base score for success

        # Response length (up to 30 points)
        response_len = len(result.response)
        if response_len > 100:
            score += min(30, response_len / 50)

        # Latency bonus (up to 20 points for fast responses)
        if result.latency_ms < 1000:
            score += 20
        elif result.latency_ms < 3000:
            score += 10
        elif result.latency_ms < 5000:
            score += 5

        return min(100, score)

    # ========================================================================
    # Connector Management
    # ========================================================================

    def _get_or_create_connector(self, model: AIModelInfo) -> Any:
        """Get or create a connector for a model."""
        if model.model_id in self._connectors:
            return self._connectors[model.model_id]

        # Try to create an appropriate connector
        connector = self._create_connector(model)
        if connector:
            self._connectors[model.model_id] = connector

        return connector

    def _create_connector(self, model: AIModelInfo) -> Any:
        """Create a connector based on model type."""
        from .connector import (
            GenericRESTConnector,
            ShengNongConnector,
            CropWizardConnector,
            PlantGPTConnector,
        )

        # Model-specific connectors
        if model.model_id == "shengnong":
            return ShengNongConnector(model)
        elif model.model_id == "cropwizard":
            return CropWizardConnector(model)
        elif model.model_id == "plantgpt":
            return PlantGPTConnector(model)

        # Generic REST connector for models with endpoints
        if model.endpoint:
            return GenericRESTConnector(model)

        return None

    def register_connector(self, model_id: str, connector: Any) -> None:
        """Register a custom connector for a model.

        تسجيل موصل مخصص لنموذج
        为模型注册自定义连接器

        Args:
            model_id: ID of the model
            connector: Connector instance
        """
        self._connectors[model_id] = connector

    # ========================================================================
    # Statistics & Info
    # ========================================================================

    def get_registry_stats(self) -> dict[str, Any]:
        """Get statistics about the model registry.

        الحصول على إحصائيات عن سجل النماذج
        获取模型注册表的统计信息
        """
        return self._registry.get_statistics()

    def get_model_info(self, model_id: str) -> AIModelInfo | None:
        """Get detailed information about a model.

        الحصول على معلومات تفصيلية عن نموذج
        获取模型的详细信息

        Args:
            model_id: ID of the model

        Returns:
            AIModelInfo or None if not found
        """
        return self._registry.get(model_id)

    def list_all_models(self) -> list[AIModelInfo]:
        """List all registered models.

        عرض جميع النماذج المسجلة
        列出所有已注册的模型
        """
        return self._registry.get_all()


# ========================================================================
# Singleton & Factory Functions
# ========================================================================

_integrator: ModelIntegrator | None = None


def get_integrator(
    default_language: str = "en",
) -> ModelIntegrator:
    """Get the singleton integrator instance.

    الحصول على مثيل المُدمج الوحيد
    获取单例集成器实例
    """
    global _integrator
    if _integrator is None:
        _integrator = ModelIntegrator(default_language=default_language)
    return _integrator


def reset_integrator() -> None:
    """Reset the singleton integrator (mainly for testing)."""
    global _integrator
    _integrator = None


# ========================================================================
# Convenience Functions
# ========================================================================

def discover_models(
    category: AIModelCategory | None = None,
    capability: ModelCapability | None = None,
    language: str | None = None,
) -> ModelDiscoveryResult:
    """Discover models matching criteria."""
    return get_integrator().discover_models(category, capability, language)


def get_best_model(
    task_type: TaskType,
    language: str = "en",
    prefer_open_source: bool = False,
) -> ModelSelection:
    """Get the best model for a task type."""
    return get_integrator().get_best_model_for_task(
        task_type, language, prefer_open_source
    )


async def call_model(
    model_id: str,
    query: str,
    context: dict[str, Any] | None = None,
) -> ModelCallResult:
    """Call a model with a query."""
    return await get_integrator().call_model(model_id, query, context)


async def compare_models(
    query: str,
    model_ids: list[str],
    context: dict[str, Any] | None = None,
) -> ModelComparison:
    """Compare responses from multiple models."""
    return await get_integrator().compare_models(query, model_ids, context)
