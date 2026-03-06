"""
Agricultural AI Models Registry
================================
سجل نماذج الذكاء الاصطناعي الزراعي
农业AI模型注册表

Comprehensive registry of 50+ agricultural AI models from academic institutions,
research laboratories, and commercial organizations worldwide.

Based on the survey article covering major agricultural AI innovations.

Categories:
1. General Agriculture Decision (通用农业决策) - 20+ models
2. Breeding & Bioscience (育种与生物科学) - 10+ models
3. Livestock & Veterinary (畜牧兽医) - 10+ models
4. Remote Sensing & Geo (遥感地理) - 10+ models
5. Specialty (专业垂直) - 10+ models

Philosophy:
- "让知识流动" (Let Knowledge Flow) - LLM consultants democratize agricultural expertise
  Enabling farmers and agronomists to access expert-level knowledge through natural
  language interaction, breaking down knowledge barriers.

- "让计算创造" (Let Computation Create) - Bio/remote sensing models enable precision
  Leveraging computational power for genomics, satellite imagery analysis, and
  biological sequence design to create new agricultural possibilities.

- Future: From "advice" to "Agent execution"
  Moving beyond advisory systems toward autonomous agents that can plan, execute,
  and optimize agricultural operations end-to-end.

Key Models Included:
- ShengNong 3.0 (神农) - China Agricultural University flagship multimodal model
- CropWizard - NCSA/UIUC expert agricultural system
- PlantGPT - Plant genomics and breeding assistant
- AgroGPT - Arabic-supporting agricultural VLM from MBZUAI
- Prithvi - NASA/IBM geospatial foundation model
- AgroNT - Agro Nucleotide Transformer for genomics
- And 45+ more specialized agricultural AI models

Usage:
    from shared.ai.models_registry import (
        # Registry
        AgriculturalAIRegistry,
        get_registry,

        # Models
        AIModelInfo,
        AIModelCategory,
        ModelCapability,

        # Integration
        ModelIntegrator,
        get_integrator,
        discover_models,
        get_best_model,

        # Connectors
        ShengNongConnector,
        CropWizardConnector,
        PlantGPTConnector,
    )

    # Get all available models
    registry = get_registry()
    print(f"Total models: {registry.count()}")

    # Discover models for a specific task
    from shared.ai.models_registry import TaskType
    selection = get_best_model(TaskType.CROP_ADVISORY, language="ar")
    print(f"Recommended: {selection.recommended_model.name}")

    # Call a model
    integrator = get_integrator()
    result = await integrator.call_model("shengnong", "How to treat wheat rust?")
    print(result.response)

Author: SAHOOL Platform Team
Updated: January 2026
"""

# Models and Enums
# Connectors
# Arabic Models
from .arabic_models import (
    ARABIC_MODEL_IDS,
    ARABIC_MODELS_BY_COUNTRY,
    ARABIC_MODELS_FOR_AGRICULTURE,
    get_arabic_models,
    register_arabic_models,
)
from .connector import (
    AgroGPTConnector,
    # Base
    BaseConnector,
    ConnectorResponse,
    CropWizardConnector,
    GenericRESTConnector,
    PlantGPTConnector,
    # Model-Specific Connectors
    ShengNongConnector,
    # Factory
    create_connector,
    get_available_connectors,
)

# Integrator
from .integrator import (
    # Constants
    TASK_CAPABILITY_MAP,
    ModelCallResult,
    # Classes
    ModelIntegrator,
    ModelSelection,
    # Enums
    TaskType,
    call_model,
    compare_models,
    # Convenience Functions
    discover_models,
    get_best_model,
    # Factory Functions
    get_integrator,
    reset_integrator,
)
from .models import (
    # Enums
    AIModelCategory,
    AIModelInfo,
    DeveloperInfo,
    # Data Classes
    LanguageSupport,
    ModelArchitecture,
    ModelCapability,
    ModelComparison,
    ModelDiscoveryResult,
    ModelEndpoint,
    ModelLicense,
    ModelPerformance,
    ModelStatus,
)

# Registry
from .registry import (
    AgriculturalAIRegistry,
    get_registry,
    reset_registry,
)

__version__ = "1.0.0"

__all__ = [
    # === Models & Enums ===
    # Category Enum
    "AIModelCategory",
    # Capability Enum
    "ModelCapability",
    # License Enum
    "ModelLicense",
    # Status Enum
    "ModelStatus",
    # Architecture Enum
    "ModelArchitecture",
    # Data Classes
    "LanguageSupport",
    "ModelEndpoint",
    "DeveloperInfo",
    "ModelPerformance",
    "AIModelInfo",
    "ModelComparison",
    "ModelDiscoveryResult",
    # === Registry ===
    "AgriculturalAIRegistry",
    "get_registry",
    "reset_registry",
    # === Integrator ===
    # Task Type Enum
    "TaskType",
    # Classes
    "ModelIntegrator",
    "ModelCallResult",
    "ModelSelection",
    # Factory Functions
    "get_integrator",
    "reset_integrator",
    # Convenience Functions
    "discover_models",
    "get_best_model",
    "call_model",
    "compare_models",
    # Constants
    "TASK_CAPABILITY_MAP",
    # === Connectors ===
    # Base
    "BaseConnector",
    "ConnectorResponse",
    # Model-Specific Connectors
    "ShengNongConnector",
    "CropWizardConnector",
    "PlantGPTConnector",
    "AgroGPTConnector",
    "GenericRESTConnector",
    # Factory
    "create_connector",
    "get_available_connectors",
    # === Arabic Models (G-02) ===
    "get_arabic_models",
    "register_arabic_models",
    "ARABIC_MODEL_IDS",
    "ARABIC_MODELS_BY_COUNTRY",
    "ARABIC_MODELS_FOR_AGRICULTURE",
]


# ========================================================================
# Quick Reference: Model Categories
# ========================================================================

CATEGORY_DESCRIPTIONS = {
    AIModelCategory.GENERAL_AGRICULTURE: {
        "en": "General Agricultural Decision Support",
        "ar": "دعم القرار الزراعي العام",
        "cn": "通用农业决策支持",
        "models": ["shengnong", "cropwizard", "agrigpt", "agrogpt", "farmvibes_ai"],
    },
    AIModelCategory.BREEDING_BIOSCIENCE: {
        "en": "Breeding & Bioscience",
        "ar": "التربية والعلوم الحيوية",
        "cn": "育种与生物科学",
        "models": ["plantgpt", "seedllm", "breedinggpt", "agront", "evo2", "pllama"],
    },
    AIModelCategory.LIVESTOCK_VETERINARY: {
        "en": "Livestock & Veterinary",
        "ar": "الثروة الحيوانية والبيطرية",
        "cn": "畜牧兽医",
        "models": ["ai4dllm", "vetcloud", "piggpt", "vetgpt", "poultryai"],
    },
    AIModelCategory.REMOTE_SENSING_GEO: {
        "en": "Remote Sensing & Geospatial",
        "ar": "الاستشعار عن بعد والجغرافيا المكانية",
        "cn": "遥感地理",
        "models": ["earthgpt", "geogpt", "skysense", "geochat", "agromind", "prithvi"],
    },
    AIModelCategory.SPECIALTY: {
        "en": "Specialty/Vertical Agriculture",
        "ar": "الزراعة المتخصصة/العمودية",
        "cn": "专业垂直农业",
        "models": ["linlong", "luyu", "cottonai", "riceai", "datepalmAI", "oliveai"],
    },
}


# ========================================================================
# Philosophy & Future Vision
# ========================================================================

PHILOSOPHY = {
    "knowledge_flow": {
        "chinese": "让知识流动",
        "english": "Let Knowledge Flow",
        "arabic": "دع المعرفة تتدفق",
        "description": (
            "LLM consultants democratize agricultural expertise, enabling "
            "smallholder farmers to access expert-level knowledge through "
            "natural language interaction."
        ),
    },
    "computation_creates": {
        "chinese": "让计算创造",
        "english": "Let Computation Create",
        "arabic": "دع الحوسبة تبدع",
        "description": (
            "Bio-informatics and remote sensing models leverage computational "
            "power for genomics, satellite imagery analysis, and biological "
            "sequence design to create new agricultural possibilities."
        ),
    },
    "agent_execution": {
        "chinese": "从建议到执行",
        "english": "From Advice to Agent Execution",
        "arabic": "من النصيحة إلى تنفيذ الوكيل",
        "description": (
            "The future direction: moving beyond advisory systems toward "
            "autonomous agents that can plan, execute, and optimize "
            "agricultural operations end-to-end."
        ),
    },
}


def get_philosophy() -> dict:
    """Get the philosophy behind agricultural AI models.

    الحصول على فلسفة نماذج الذكاء الاصطناعي الزراعي
    获取农业AI模型的理念
    """
    return PHILOSOPHY


def get_category_info(category: AIModelCategory) -> dict:
    """Get information about a category.

    الحصول على معلومات عن فئة
    获取类别信息
    """
    return CATEGORY_DESCRIPTIONS.get(category, {})


def list_featured_models() -> list[str]:
    """Get list of featured/flagship models.

    الحصول على قائمة النماذج المميزة/الرائدة
    获取特色/旗舰模型列表
    """
    return [
        "shengnong",  # ShengNong 3.0 - China Agricultural University flagship
        "cropwizard",  # CropWizard - NCSA expert system
        "plantgpt",  # PlantGPT - Plant genomics leader
        "agrogpt",  # AgroGPT - Arabic-supporting VLM
        "prithvi",  # Prithvi - NASA/IBM geospatial foundation
        "agront",  # AgroNT - Nucleotide transformer
        "farmvibes_ai",  # FarmVibes.AI - Microsoft precision farming
    ]


def list_arabic_supported_models() -> list[str]:
    """Get list of models with Arabic language support.

    الحصول على قائمة النماذج التي تدعم اللغة العربية
    获取支持阿拉伯语的模型列表
    """
    registry = get_registry()
    result = registry.discover_by_language("ar")
    return [m.model_id for m in result.models]


def list_open_source_models() -> list[str]:
    """Get list of open source models.

    الحصول على قائمة النماذج مفتوحة المصدر
    获取开源模型列表
    """
    registry = get_registry()
    result = registry.discover_open_source()
    return [m.model_id for m in result.models]
