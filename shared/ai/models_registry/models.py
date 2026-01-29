"""
Agricultural AI Models - Data Models
=====================================
نماذج بيانات سجل نماذج الذكاء الاصطناعي الزراعي

Data models for the Agricultural AI Models Registry including
model categories, capabilities, and metadata.

Based on the comprehensive survey of 50+ agricultural AI models from
academic institutions, research labs, and commercial organizations.

Philosophy:
- "让知识流动" (Let Knowledge Flow) - LLM consultants democratize agricultural expertise
- "让计算创造" (Let Computation Create) - Bio/remote sensing models enable precision agriculture
- Future: From "advice" to "Agent execution" - autonomous farm operations

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class AIModelCategory(str, Enum):
    """Categories of Agricultural AI Models.

    فئات نماذج الذكاء الاصطناعي الزراعي
    农业AI模型类别
    """

    GENERAL_AGRICULTURE = "general_agriculture"      # 通用农业决策 | استشارات زراعية عامة
    BREEDING_BIOSCIENCE = "breeding_bioscience"      # 育种与生物科学 | التربية والعلوم الحيوية
    LIVESTOCK_VETERINARY = "livestock_veterinary"   # 畜牧兽医 | الثروة الحيوانية والبيطرية
    REMOTE_SENSING_GEO = "remote_sensing_geo"       # 遥感地理 | الاستشعار عن بعد والجغرافيا
    SPECIALTY = "specialty"                          # 专业垂直 | تخصصات عمودية
    FOOD_SAFETY = "food_safety"                     # 食品安全 | سلامة الغذاء
    AGRICULTURAL_LAW = "agricultural_law"           # 农业法律 | القانون الزراعي
    CLIMATE_WEATHER = "climate_weather"             # 气候天气 | المناخ والطقس


class ModelCapability(str, Enum):
    """Capabilities that agricultural AI models can provide.

    قدرات نماذج الذكاء الاصطناعي الزراعي
    农业AI模型能力
    """

    # Knowledge & Advisory | المعرفة والاستشارات | 知识咨询
    QA = "qa"                                        # Question Answering | الأسئلة والأجوبة
    DECISION_SUPPORT = "decision_support"           # Decision Support | دعم القرار
    EXPERT_CONSULTATION = "expert_consultation"     # Expert Consultation | استشارة الخبراء
    KNOWLEDGE_GRAPH = "knowledge_graph"             # Knowledge Graph | الرسم البياني المعرفي

    # Crop Intelligence | ذكاء المحاصيل | 作物智能
    PEST_DETECTION = "pest_detection"               # Pest Detection | كشف الآفات
    DISEASE_DETECTION = "disease_detection"         # Disease Detection | كشف الأمراض
    YIELD_PREDICTION = "yield_prediction"           # Yield Prediction | التنبؤ بالإنتاج
    GROWTH_STAGE = "growth_stage"                   # Growth Stage Analysis | تحليل مراحل النمو
    CROP_MONITORING = "crop_monitoring"             # Crop Monitoring | مراقبة المحاصيل

    # Breeding & Genomics | التربية والجينوم | 育种基因组
    BREEDING = "breeding"                           # Breeding Recommendations | توصيات التربية
    GENOMICS = "genomics"                           # Genomics Analysis | تحليل الجينوم
    GENE_EDITING = "gene_editing"                   # Gene Editing | التعديل الجيني
    PHENOTYPE_PREDICTION = "phenotype_prediction"   # Phenotype Prediction | التنبؤ بالنمط الظاهري
    MOLECULAR_DESIGN = "molecular_design"           # Molecular Design | التصميم الجزيئي

    # Remote Sensing | الاستشعار عن بعد | 遥感
    SATELLITE_ANALYSIS = "satellite_analysis"       # Satellite Image Analysis | تحليل صور الأقمار
    NDVI_ANALYSIS = "ndvi_analysis"                 # NDVI Analysis | تحليل NDVI
    LAND_USE = "land_use"                           # Land Use Classification | تصنيف استخدام الأراضي
    CHANGE_DETECTION = "change_detection"           # Change Detection | كشف التغيير
    SOIL_ANALYSIS = "soil_analysis"                 # Soil Analysis | تحليل التربة

    # Livestock & Veterinary | الثروة الحيوانية | 畜牧
    ANIMAL_HEALTH = "animal_health"                 # Animal Health | صحة الحيوان
    VETERINARY_QA = "veterinary_qa"                 # Veterinary Q&A | أسئلة بيطرية
    FEED_OPTIMIZATION = "feed_optimization"         # Feed Optimization | تحسين الأعلاف
    BREEDING_MANAGEMENT = "breeding_management"     # Breeding Management | إدارة التربية
    MILK_PRODUCTION = "milk_production"             # Milk Production | إنتاج الحليب

    # Weather & Climate | الطقس والمناخ | 气象
    WEATHER_FORECAST = "weather_forecast"           # Weather Forecasting | التنبؤ بالطقس
    CLIMATE_MODELING = "climate_modeling"           # Climate Modeling | نمذجة المناخ
    DISASTER_WARNING = "disaster_warning"           # Disaster Warning | الإنذار بالكوارث

    # Specialty | التخصصات | 专业
    FORESTRY = "forestry"                           # Forestry Management | إدارة الغابات
    TEA_CULTIVATION = "tea_cultivation"             # Tea Cultivation | زراعة الشاي
    AQUACULTURE = "aquaculture"                     # Aquaculture | الاستزراع المائي
    LEGAL_QA = "legal_qa"                           # Agricultural Law Q&A | أسئلة قانونية

    # Agent Capabilities | قدرات الوكيل | Agent能力
    AUTONOMOUS_OPERATION = "autonomous_operation"   # Autonomous Operation | التشغيل الذاتي
    MULTI_AGENT = "multi_agent"                     # Multi-Agent Collaboration | تعاون متعدد الوكلاء
    TOOL_USE = "tool_use"                           # Tool Use | استخدام الأدوات
    PLANNING = "planning"                           # Task Planning | تخطيط المهام


class ModelLicense(str, Enum):
    """License types for AI models.

    أنواع تراخيص نماذج الذكاء الاصطناعي
    AI模型许可类型
    """

    OPEN_SOURCE = "open_source"                     # Open Source | مفتوح المصدر
    ACADEMIC = "academic"                           # Academic Use Only | للاستخدام الأكاديمي فقط
    COMMERCIAL = "commercial"                       # Commercial | تجاري
    PROPRIETARY = "proprietary"                     # Proprietary | ملكية خاصة
    GOVERNMENT = "government"                       # Government | حكومي
    FREEMIUM = "freemium"                           # Freemium | مجاني مع خيارات مدفوعة
    UNKNOWN = "unknown"                             # Unknown | غير معروف


class ModelStatus(str, Enum):
    """Operational status of AI models.

    حالة تشغيل نماذج الذكاء الاصطناعي
    AI模型运行状态
    """

    ACTIVE = "active"                               # Active & Available | نشط ومتاح
    BETA = "beta"                                   # Beta Testing | اختبار تجريبي
    DEPRECATED = "deprecated"                       # Deprecated | مهمل
    RESEARCH = "research"                           # Research Only | للبحث فقط
    COMING_SOON = "coming_soon"                     # Coming Soon | قريبا
    OFFLINE = "offline"                             # Currently Offline | غير متصل حاليا


class ModelArchitecture(str, Enum):
    """Underlying architecture of AI models.

    البنية الأساسية لنماذج الذكاء الاصطناعي
    AI模型底层架构
    """

    LLM = "llm"                                     # Large Language Model | نموذج لغوي كبير
    VLM = "vlm"                                     # Vision-Language Model | نموذج رؤية-لغة
    CNN = "cnn"                                     # Convolutional Neural Network | شبكة عصبية تلافيفية
    TRANSFORMER = "transformer"                     # Transformer | محول
    FOUNDATION = "foundation"                       # Foundation Model | نموذج أساسي
    ENSEMBLE = "ensemble"                           # Ensemble Model | نموذج مجمع
    AGENT = "agent"                                 # AI Agent | وكيل ذكاء اصطناعي
    HYBRID = "hybrid"                               # Hybrid Architecture | بنية هجينة


@dataclass
class LanguageSupport:
    """Language support information for a model.

    معلومات دعم اللغة للنموذج
    模型语言支持信息
    """

    english: bool = True
    arabic: bool = False
    chinese: bool = False
    spanish: bool = False
    french: bool = False
    hindi: bool = False
    other_languages: list[str] = field(default_factory=list)

    def supports(self, language: str) -> bool:
        """Check if a language is supported."""
        lang_map = {
            "en": self.english,
            "ar": self.arabic,
            "zh": self.chinese,
            "es": self.spanish,
            "fr": self.french,
            "hi": self.hindi,
        }
        if language.lower() in lang_map:
            return lang_map[language.lower()]
        return language.lower() in [l.lower() for l in self.other_languages]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "english": self.english,
            "arabic": self.arabic,
            "chinese": self.chinese,
            "spanish": self.spanish,
            "french": self.french,
            "hindi": self.hindi,
            "other_languages": self.other_languages,
        }


@dataclass
class ModelEndpoint:
    """API endpoint information for a model.

    معلومات نقطة نهاية API للنموذج
    模型API端点信息
    """

    url: str
    method: str = "POST"
    auth_required: bool = True
    auth_type: str = "api_key"                      # api_key, oauth, basic, none
    rate_limit: int | None = None                   # Requests per minute
    timeout_seconds: int = 60
    is_streaming: bool = False
    documentation_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "method": self.method,
            "auth_required": self.auth_required,
            "auth_type": self.auth_type,
            "rate_limit": self.rate_limit,
            "timeout_seconds": self.timeout_seconds,
            "is_streaming": self.is_streaming,
            "documentation_url": self.documentation_url,
        }


@dataclass
class DeveloperInfo:
    """Information about the model developer/organization.

    معلومات عن مطور/منظمة النموذج
    模型开发者/机构信息
    """

    name: str
    name_ar: str = ""
    name_cn: str = ""
    organization_type: str = "academic"             # academic, commercial, government, research
    country: str = "Unknown"
    website: str | None = None
    contact_email: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "name_ar": self.name_ar,
            "name_cn": self.name_cn,
            "organization_type": self.organization_type,
            "country": self.country,
            "website": self.website,
            "contact_email": self.contact_email,
        }


@dataclass
class ModelPerformance:
    """Performance metrics for the model.

    مقاييس أداء النموذج
    模型性能指标
    """

    accuracy: float | None = None
    f1_score: float | None = None
    latency_ms: float | None = None
    throughput: float | None = None                 # Requests per second
    benchmark_dataset: str | None = None
    benchmark_date: str | None = None
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "accuracy": self.accuracy,
            "f1_score": self.f1_score,
            "latency_ms": self.latency_ms,
            "throughput": self.throughput,
            "benchmark_dataset": self.benchmark_dataset,
            "benchmark_date": self.benchmark_date,
            "notes": self.notes,
        }


@dataclass
class AIModelInfo:
    """Complete information about an Agricultural AI Model.

    معلومات كاملة عن نموذج ذكاء اصطناعي زراعي
    农业AI模型完整信息
    """

    # Identity | الهوية | 身份
    model_id: str
    name: str
    name_ar: str = ""
    name_cn: str = ""

    # Classification | التصنيف | 分类
    category: AIModelCategory = AIModelCategory.GENERAL_AGRICULTURE
    capabilities: list[ModelCapability] = field(default_factory=list)
    architecture: ModelArchitecture = ModelArchitecture.LLM

    # Developer | المطور | 开发者
    developer: DeveloperInfo | None = None

    # Access | الوصول | 访问
    url: str | None = None
    github_url: str | None = None
    huggingface_url: str | None = None
    paper_url: str | None = None

    # Status | الحالة | 状态
    status: ModelStatus = ModelStatus.ACTIVE
    license: ModelLicense = ModelLicense.UNKNOWN
    version: str | None = None
    release_date: str | None = None

    # Languages | اللغات | 语言
    language_support: LanguageSupport = field(default_factory=LanguageSupport)

    # Technical | التقنية | 技术
    endpoint: ModelEndpoint | None = None
    performance: ModelPerformance | None = None
    base_model: str | None = None                   # e.g., "Qwen2", "LLaMA", "GPT-4"
    parameter_count: str | None = None              # e.g., "7B", "13B", "70B"
    context_length: int | None = None

    # Description | الوصف | 描述
    description: str = ""
    description_ar: str = ""
    description_cn: str = ""

    # Use Cases | حالات الاستخدام | 使用场景
    use_cases: list[str] = field(default_factory=list)
    use_cases_ar: list[str] = field(default_factory=list)

    # Tags | العلامات | 标签
    tags: list[str] = field(default_factory=list)

    # Metadata | البيانات الوصفية | 元数据
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def has_capability(self, capability: ModelCapability) -> bool:
        """Check if model has a specific capability."""
        return capability in self.capabilities

    def supports_language(self, language: str) -> bool:
        """Check if model supports a specific language."""
        return self.language_support.supports(language)

    def is_available(self) -> bool:
        """Check if model is available for use."""
        return self.status in [ModelStatus.ACTIVE, ModelStatus.BETA]

    def get_display_name(self, language: str = "en") -> str:
        """Get display name in specified language."""
        if language == "ar" and self.name_ar:
            return self.name_ar
        elif language == "zh" and self.name_cn:
            return self.name_cn
        return self.name

    def get_description(self, language: str = "en") -> str:
        """Get description in specified language."""
        if language == "ar" and self.description_ar:
            return self.description_ar
        elif language == "zh" and self.description_cn:
            return self.description_cn
        return self.description

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_id": self.model_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "name_cn": self.name_cn,
            "category": self.category.value,
            "capabilities": [c.value for c in self.capabilities],
            "architecture": self.architecture.value,
            "developer": self.developer.to_dict() if self.developer else None,
            "url": self.url,
            "github_url": self.github_url,
            "huggingface_url": self.huggingface_url,
            "paper_url": self.paper_url,
            "status": self.status.value,
            "license": self.license.value,
            "version": self.version,
            "release_date": self.release_date,
            "language_support": self.language_support.to_dict(),
            "endpoint": self.endpoint.to_dict() if self.endpoint else None,
            "performance": self.performance.to_dict() if self.performance else None,
            "base_model": self.base_model,
            "parameter_count": self.parameter_count,
            "context_length": self.context_length,
            "description": self.description,
            "description_ar": self.description_ar,
            "description_cn": self.description_cn,
            "use_cases": self.use_cases,
            "use_cases_ar": self.use_cases_ar,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AIModelInfo":
        """Create from dictionary."""
        # Parse nested objects
        developer = None
        if data.get("developer"):
            developer = DeveloperInfo(**data["developer"])

        language_support = LanguageSupport()
        if data.get("language_support"):
            language_support = LanguageSupport(**data["language_support"])

        endpoint = None
        if data.get("endpoint"):
            endpoint = ModelEndpoint(**data["endpoint"])

        performance = None
        if data.get("performance"):
            performance = ModelPerformance(**data["performance"])

        return cls(
            model_id=data["model_id"],
            name=data["name"],
            name_ar=data.get("name_ar", ""),
            name_cn=data.get("name_cn", ""),
            category=AIModelCategory(data.get("category", "general_agriculture")),
            capabilities=[ModelCapability(c) for c in data.get("capabilities", [])],
            architecture=ModelArchitecture(data.get("architecture", "llm")),
            developer=developer,
            url=data.get("url"),
            github_url=data.get("github_url"),
            huggingface_url=data.get("huggingface_url"),
            paper_url=data.get("paper_url"),
            status=ModelStatus(data.get("status", "active")),
            license=ModelLicense(data.get("license", "unknown")),
            version=data.get("version"),
            release_date=data.get("release_date"),
            language_support=language_support,
            endpoint=endpoint,
            performance=performance,
            base_model=data.get("base_model"),
            parameter_count=data.get("parameter_count"),
            context_length=data.get("context_length"),
            description=data.get("description", ""),
            description_ar=data.get("description_ar", ""),
            description_cn=data.get("description_cn", ""),
            use_cases=data.get("use_cases", []),
            use_cases_ar=data.get("use_cases_ar", []),
            tags=data.get("tags", []),
        )


@dataclass
class ModelComparison:
    """Comparison result between multiple models.

    نتيجة المقارنة بين نماذج متعددة
    多模型比较结果
    """

    query: str
    models: list[AIModelInfo]
    responses: dict[str, str] = field(default_factory=dict)     # model_id -> response
    latencies: dict[str, float] = field(default_factory=dict)   # model_id -> latency_ms
    scores: dict[str, float] = field(default_factory=dict)      # model_id -> score
    winner: str | None = None
    comparison_criteria: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "models": [m.model_id for m in self.models],
            "responses": self.responses,
            "latencies": self.latencies,
            "scores": self.scores,
            "winner": self.winner,
            "comparison_criteria": self.comparison_criteria,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ModelDiscoveryResult:
    """Result of model discovery operation.

    نتيجة عملية اكتشاف النماذج
    模型发现操作结果
    """

    models: list[AIModelInfo]
    total_count: int
    filter_criteria: dict[str, Any] = field(default_factory=dict)
    search_duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "models": [m.to_dict() for m in self.models],
            "total_count": self.total_count,
            "filter_criteria": self.filter_criteria,
            "search_duration_ms": self.search_duration_ms,
            "timestamp": self.timestamp.isoformat(),
        }
