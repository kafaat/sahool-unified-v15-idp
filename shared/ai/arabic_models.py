"""
Arabic-Specialized Model Configurations
=========================================
إعدادات النماذج المتخصصة بالعربية

Registry of Arabic-specialized AI models for the SAHOOL platform,
covering embedding, classification, NER, sentiment analysis,
translation, and text generation tasks.

Addresses Gap G-02: Arabic-specialized model configurations
missing from the models registry.

Supported Models:
    - AraBERT v2 (NER, classification)
    - CAMeLBERT (NER, morphological analysis)
    - Multilingual MiniLM (embedding)
    - Helsinki OPUS MT (translation AR<->EN)
    - AraELECTRA (classification)
    - Multilingual E5 Large (embedding)

Author: SAHOOL Platform Team
Updated: March 2026
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Optional

logger = logging.getLogger(__name__)


class ArabicModelTask(StrEnum):
    """Supported Arabic model tasks | مهام النماذج العربية المدعومة"""

    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"
    NER = "ner"
    SENTIMENT = "sentiment"
    GENERATION = "generation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"


class ArabicModelProvider(StrEnum):
    """Model hosting providers | مزودي استضافة النماذج"""

    HUGGINGFACE = "huggingface"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    OLLAMA = "ollama"
    LOCAL = "local"


@dataclass
class ArabicModelConfig:
    """
    Configuration for an Arabic-specialized model.

    إعدادات نموذج متخصص بالعربية - يتضمن معلومات المزود والمهمة
    واللغات المدعومة ونافذة السياق وأبعاد التضمين.
    """

    model_id: str
    model_name: str
    model_name_ar: str
    provider: ArabicModelProvider
    task: ArabicModelTask
    language_support: list[str] = field(default_factory=lambda: ["ar", "en"])
    context_window: int = 512
    embedding_dim: int | None = None
    recommended_for: list[str] = field(default_factory=list)

    def supports_language(self, lang_code: str) -> bool:
        """Check if model supports a language | التحقق من دعم اللغة"""
        return lang_code.lower() in self.language_support

    def __repr__(self) -> str:
        return (
            f"ArabicModelConfig(id={self.model_id!r}, "
            f"task={self.task.value!r}, "
            f"name_ar={self.model_name_ar!r})"
        )


# ---------------------------------------------------------------------------
# Arabic Models Registry | سجل النماذج العربية
# ---------------------------------------------------------------------------

ARABIC_MODELS: dict[str, ArabicModelConfig] = {
    # AraBERT v2 - flagship Arabic BERT model
    "aubmindlab/bert-base-arabertv2": ArabicModelConfig(
        model_id="aubmindlab/bert-base-arabertv2",
        model_name="AraBERT v2 Base",
        model_name_ar="أرابيرت الإصدار الثاني",
        provider=ArabicModelProvider.HUGGINGFACE,
        task=ArabicModelTask.NER,
        language_support=["ar"],
        context_window=512,
        embedding_dim=768,
        recommended_for=[
            "crop_entity_extraction",
            "disease_name_recognition",
            "intent_classification",
            "agricultural_text_classification",
        ],
    ),
    # CAMeLBERT Mix - robust Arabic NER
    "CAMeL-Lab/bert-base-arabic-camelbert-mix": ArabicModelConfig(
        model_id="CAMeL-Lab/bert-base-arabic-camelbert-mix",
        model_name="CAMeLBERT Mix",
        model_name_ar="كاميلبيرت ميكس",
        provider=ArabicModelProvider.HUGGINGFACE,
        task=ArabicModelTask.NER,
        language_support=["ar"],
        context_window=512,
        embedding_dim=768,
        recommended_for=[
            "morphological_analysis",
            "pest_name_extraction",
            "location_recognition",
        ],
    ),
    # Multilingual MiniLM - lightweight multilingual embeddings
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": ArabicModelConfig(
        model_id="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_name="Multilingual MiniLM L12 v2",
        model_name_ar="ميني إل إم متعدد اللغات",
        provider=ArabicModelProvider.SENTENCE_TRANSFORMERS,
        task=ArabicModelTask.EMBEDDING,
        language_support=["ar", "en", "fr", "de", "es", "it", "pt", "zh", "ja", "ko"],
        context_window=512,
        embedding_dim=384,
        recommended_for=[
            "semantic_search",
            "advisory_retrieval",
            "knowledge_base_indexing",
            "farmer_query_matching",
        ],
    ),
    # OPUS MT Arabic -> English translation
    "Helsinki-NLP/opus-mt-ar-en": ArabicModelConfig(
        model_id="Helsinki-NLP/opus-mt-ar-en",
        model_name="OPUS MT Arabic to English",
        model_name_ar="أوبس للترجمة من العربية إلى الإنجليزية",
        provider=ArabicModelProvider.HUGGINGFACE,
        task=ArabicModelTask.TRANSLATION,
        language_support=["ar", "en"],
        context_window=512,
        recommended_for=[
            "farmer_query_translation",
            "advisory_localization",
            "report_translation",
        ],
    ),
    # OPUS MT English -> Arabic translation
    "Helsinki-NLP/opus-mt-en-ar": ArabicModelConfig(
        model_id="Helsinki-NLP/opus-mt-en-ar",
        model_name="OPUS MT English to Arabic",
        model_name_ar="أوبس للترجمة من الإنجليزية إلى العربية",
        provider=ArabicModelProvider.HUGGINGFACE,
        task=ArabicModelTask.TRANSLATION,
        language_support=["ar", "en"],
        context_window=512,
        recommended_for=[
            "advisory_arabic_generation",
            "alert_translation",
            "documentation_localization",
        ],
    ),
    # AraELECTRA - efficient Arabic text classification
    "aubmindlab/araelectra-base-discriminator": ArabicModelConfig(
        model_id="aubmindlab/araelectra-base-discriminator",
        model_name="AraELECTRA Base Discriminator",
        model_name_ar="أرا إلكترا للتصنيف",
        provider=ArabicModelProvider.HUGGINGFACE,
        task=ArabicModelTask.CLASSIFICATION,
        language_support=["ar"],
        context_window=512,
        embedding_dim=768,
        recommended_for=[
            "sentiment_analysis",
            "feedback_classification",
            "urgency_detection",
            "topic_classification",
        ],
    ),
    # Multilingual E5 Large - high-quality multilingual embeddings
    "Xenova/multilingual-e5-large": ArabicModelConfig(
        model_id="Xenova/multilingual-e5-large",
        model_name="Multilingual E5 Large",
        model_name_ar="إي فايف الكبير متعدد اللغات",
        provider=ArabicModelProvider.HUGGINGFACE,
        task=ArabicModelTask.EMBEDDING,
        language_support=["ar", "en", "fr", "de", "es", "zh", "ja", "ko", "ru"],
        context_window=512,
        embedding_dim=1024,
        recommended_for=[
            "high_accuracy_retrieval",
            "cross_lingual_search",
            "agricultural_document_search",
            "knowledge_graph_embedding",
        ],
    ),
}


# ---------------------------------------------------------------------------
# Task-to-model preference mapping (ordered by recommendation priority)
# ---------------------------------------------------------------------------

_TASK_PREFERENCE: dict[ArabicModelTask, list[str]] = {
    ArabicModelTask.EMBEDDING: [
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "Xenova/multilingual-e5-large",
    ],
    ArabicModelTask.NER: [
        "aubmindlab/bert-base-arabertv2",
        "CAMeL-Lab/bert-base-arabic-camelbert-mix",
    ],
    ArabicModelTask.CLASSIFICATION: [
        "aubmindlab/araelectra-base-discriminator",
        "aubmindlab/bert-base-arabertv2",
    ],
    ArabicModelTask.SENTIMENT: [
        "aubmindlab/araelectra-base-discriminator",
    ],
    ArabicModelTask.TRANSLATION: [
        "Helsinki-NLP/opus-mt-ar-en",
        "Helsinki-NLP/opus-mt-en-ar",
    ],
}

# Agriculture-relevant model IDs
_AGRICULTURE_MODELS: list[str] = [
    "aubmindlab/bert-base-arabertv2",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "aubmindlab/araelectra-base-discriminator",
    "Helsinki-NLP/opus-mt-ar-en",
    "Helsinki-NLP/opus-mt-en-ar",
]


# ---------------------------------------------------------------------------
# Helper functions | وظائف مساعدة
# ---------------------------------------------------------------------------


def get_arabic_model(task: ArabicModelTask) -> ArabicModelConfig:
    """
    Get the best Arabic model for a given task.

    الحصول على أفضل نموذج عربي لمهمة محددة.

    Args:
        task: The NLP task to find a model for.

    Returns:
        The top-ranked ArabicModelConfig for the task.

    Raises:
        ValueError: If no model is registered for the task.
    """
    preferred = _TASK_PREFERENCE.get(task)
    if preferred:
        model_id = preferred[0]
        if model_id in ARABIC_MODELS:
            return ARABIC_MODELS[model_id]

    # Fallback: search the full registry
    for config in ARABIC_MODELS.values():
        if config.task == task:
            return config

    raise ValueError(
        f"No Arabic model registered for task '{task.value}'. "
        f"Available tasks: {[t.value for t in ArabicModelTask]}"
    )


def get_arabic_embedding_model() -> ArabicModelConfig:
    """
    Convenience function to get the default Arabic embedding model.

    الحصول على نموذج التضمين العربي الافتراضي.

    Returns:
        ArabicModelConfig configured for embedding.
    """
    return get_arabic_model(ArabicModelTask.EMBEDDING)


def list_arabic_models(
    task: Optional[ArabicModelTask] = None,
) -> list[ArabicModelConfig]:
    """
    List all registered Arabic models, optionally filtered by task.

    عرض جميع النماذج العربية المسجلة، مع إمكانية التصفية حسب المهمة.

    Args:
        task: Optional task filter. If None, returns all models.

    Returns:
        List of matching ArabicModelConfig instances.
    """
    if task is None:
        return list(ARABIC_MODELS.values())

    return [cfg for cfg in ARABIC_MODELS.values() if cfg.task == task]


def get_recommended_models_for_agriculture() -> list[ArabicModelConfig]:
    """
    Get models recommended for SAHOOL agricultural use cases.

    الحصول على النماذج الموصى بها لحالات الاستخدام الزراعية في سهول.

    Returns:
        List of ArabicModelConfig instances suitable for agriculture.
    """
    models: list[ArabicModelConfig] = []
    for model_id in _AGRICULTURE_MODELS:
        cfg = ARABIC_MODELS.get(model_id)
        if cfg is not None:
            models.append(cfg)
        else:
            logger.warning("Agriculture model '%s' not found in registry", model_id)
    return models
