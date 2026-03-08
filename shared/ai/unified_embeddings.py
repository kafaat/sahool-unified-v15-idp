"""
Unified Embeddings Manager
==========================
مدير التضمينات الموحد - ضمان اتساق التضمينات عبر جميع الخدمات

Ensures embedding consistency across all AI layers (Gap G-05):
- Same model/dimension enforced across services
- Automatic fallback chain: SentenceTransformers -> Ollama -> OpenAI
- Caching with configurable TTL
- Dimension validation for all produced vectors
- Arabic text pre-processing before embedding
- GraphMemory -> EmbeddingsAdapter bridge (UnifiedEmbedder)

Author: SAHOOL Platform Team
Updated: March 2026
"""

from __future__ import annotations

import logging
import math
import re
import time
import unicodedata
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

try:
    from .embeddings import (
        EmbeddingConfig,
        EmbeddingProvider,
        EmbeddingProviderError,
        EmbeddingResult,
        EmbeddingsAdapter,
    )
except ImportError:
    EmbeddingsAdapter = None  # type: ignore[assignment,misc]
    EmbeddingConfig = None  # type: ignore[assignment,misc]
    EmbeddingProvider = None  # type: ignore[assignment,misc]
    EmbeddingProviderError = Exception  # type: ignore[assignment,misc]
    EmbeddingResult = None  # type: ignore[assignment,misc]

try:
    from .arabic_models import get_arabic_embedding_model
except ImportError:
    get_arabic_embedding_model = None  # type: ignore[assignment]

try:
    from .graph_memory import SimpleEmbedder

    _SIMPLE_EMBEDDER_AVAILABLE = True
except ImportError:
    _SIMPLE_EMBEDDER_AVAILABLE = False
    SimpleEmbedder = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_ARABIC_PATTERN = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+")
_DIACRITICS_PATTERN = re.compile(r"[\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]")

# Tatweel (kashida) character used for stretching Arabic text
_TATWEEL = "\u0640"


class FallbackStatus(StrEnum):
    """Provider fallback status | حالة الانتقال بين المزودين"""

    PRIMARY = "primary"
    FALLBACK_1 = "fallback_1"
    FALLBACK_2 = "fallback_2"
    EXHAUSTED = "exhausted"


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class EmbeddingConsistencyConfig:
    """
    Configuration for unified embedding consistency.
    إعدادات اتساق التضمينات الموحدة

    Attributes:
        default_model: Primary embedding model name | اسم نموذج التضمين الأساسي
        default_dimension: Expected vector dimension | البعد المتوقع للمتجه
        fallback_models: Ordered list of fallback models | قائمة النماذج البديلة
        cache_ttl_seconds: Cache time-to-live in seconds | مدة صلاحية الذاكرة المؤقتة
        normalize: Whether to L2-normalize vectors | تطبيع المتجهات
        arabic_preprocessing: Enable Arabic text cleanup | تفعيل معالجة النص العربي
    """

    default_model: str = "all-MiniLM-L6-v2"
    default_dimension: int = 384
    fallback_models: list[str] = field(
        default_factory=lambda: [
            "nomic-embed-text",  # Ollama fallback
            "text-embedding-3-small",  # OpenAI fallback
        ]
    )
    cache_ttl_seconds: int = 3600
    normalize: bool = True
    arabic_preprocessing: bool = True


# ---------------------------------------------------------------------------
# Arabic pre-processing helpers
# ---------------------------------------------------------------------------


def preprocess_arabic(text: str) -> str:
    """
    Normalise Arabic text before embedding.
    تطبيع النص العربي قبل التضمين

    Steps:
      1. Unicode NFC normalisation
      2. Remove diacritics (tashkeel)
      3. Remove tatweel (kashida)
      4. Normalise alef variants -> ا
      5. Normalise taa marbuta -> ه
      6. Collapse whitespace
    """
    text = unicodedata.normalize("NFC", text)
    text = _DIACRITICS_PATTERN.sub("", text)
    text = text.replace(_TATWEEL, "")
    # Alef variants -> plain alef
    text = text.replace("\u0622", "\u0627")  # Alef with madda
    text = text.replace("\u0623", "\u0627")  # Alef with hamza above
    text = text.replace("\u0625", "\u0627")  # Alef with hamza below
    # Taa marbuta -> haa
    text = text.replace("\u0629", "\u0647")
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _contains_arabic(text: str) -> bool:
    """Check if text contains Arabic characters | التحقق من وجود أحرف عربية"""
    return bool(_ARABIC_PATTERN.search(text))


def _l2_normalize(vector: list[float]) -> list[float]:
    """L2-normalise a vector | تطبيع المتجه"""
    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0.0:
        return vector
    return [v / norm for v in vector]


# ---------------------------------------------------------------------------
# Provider → model mapping for fallback chain
# ---------------------------------------------------------------------------

_PROVIDER_FOR_MODEL: dict[str, str] = {
    # SentenceTransformers models
    "all-MiniLM-L6-v2": "sentence_transformers",
    "all-mpnet-base-v2": "sentence_transformers",
    "paraphrase-multilingual-MiniLM-L12-v2": "sentence_transformers",
    # Ollama models
    "nomic-embed-text": "ollama",
    "mxbai-embed-large": "ollama",
    # OpenAI models
    "text-embedding-3-small": "openai",
    "text-embedding-3-large": "openai",
    "text-embedding-ada-002": "openai",
}


# ---------------------------------------------------------------------------
# Unified Embeddings Manager
# ---------------------------------------------------------------------------


class UnifiedEmbeddingsManager:
    """
    Unified embeddings manager ensuring consistency across all AI layers.
    مدير التضمينات الموحد لضمان الاتساق عبر جميع طبقات الذكاء الاصطناعي

    Features | الميزات:
        - Single model/dimension enforced across services
        - Automatic fallback: SentenceTransformers -> Ollama -> OpenAI
        - Embedding cache with TTL
        - Dimension validation on every vector
        - Arabic text pre-processing
    """

    def __init__(self, config: EmbeddingConsistencyConfig | None = None) -> None:
        self._config = config or EmbeddingConsistencyConfig()
        self._adapters: dict[str, EmbeddingsAdapter] = {}
        self._active_provider: FallbackStatus = FallbackStatus.PRIMARY
        logger.info(
            "UnifiedEmbeddingsManager initialised | تهيئة مدير التضمينات الموحد",
            extra={
                "model": self._config.default_model,
                "dimension": self._config.default_dimension,
            },
        )

    # -- public properties ---------------------------------------------------

    @property
    def config(self) -> EmbeddingConsistencyConfig:
        """Current configuration | الإعدادات الحالية"""
        return self._config

    @property
    def dimension(self) -> int:
        """Configured embedding dimension | بُعد التضمين المعتمد"""
        return self._config.default_dimension

    @property
    def active_provider(self) -> FallbackStatus:
        """Current fallback status | حالة المزود الحالي"""
        return self._active_provider

    # -- adapter helpers -----------------------------------------------------

    def _get_adapter(self, model: str) -> EmbeddingsAdapter:
        """Get or create an EmbeddingsAdapter for a specific model."""
        if EmbeddingsAdapter is None:
            raise RuntimeError("EmbeddingsAdapter is not available; install shared.ai.embeddings")

        if model not in self._adapters:
            provider_str = _PROVIDER_FOR_MODEL.get(model, "sentence_transformers")
            provider = EmbeddingProvider(provider_str)
            cfg = EmbeddingConfig(
                provider=provider,
                model=model,
                cache_enabled=True,
                cache_ttl_seconds=self._config.cache_ttl_seconds,
                embedding_dimension=self._config.default_dimension,
            )
            self._adapters[model] = EmbeddingsAdapter(cfg)
        return self._adapters[model]

    def _ordered_models(self) -> list[str]:
        """Return models in fallback order | ترتيب النماذج حسب الأولوية"""
        return [self._config.default_model, *self._config.fallback_models]

    # -- core embedding ------------------------------------------------------

    async def embed(self, text: str) -> EmbeddingResult:
        """
        Generate an embedding with consistency guarantees.
        توليد تضمين مع ضمان الاتساق

        Applies Arabic pre-processing, tries each provider in the fallback
        chain, validates dimension, and optionally L2-normalises.
        """
        processed = self._preprocess(text)

        models = self._ordered_models()
        last_error: Exception | None = None

        for idx, model in enumerate(models):
            try:
                adapter = self._get_adapter(model)
                result = await adapter.embed(processed)

                # Validate dimension
                if len(result.embedding) != self._config.default_dimension:
                    raise ValueError(
                        f"Dimension mismatch: got {len(result.embedding)}, expected {self._config.default_dimension}"
                    )

                # Optional normalisation
                if self._config.normalize:
                    result.embedding[:] = _l2_normalize(result.embedding)

                # Track which provider answered
                if idx == 0:
                    self._active_provider = FallbackStatus.PRIMARY
                elif idx == 1:
                    self._active_provider = FallbackStatus.FALLBACK_1
                else:
                    self._active_provider = FallbackStatus.FALLBACK_2

                return result

            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Embedding provider failed, trying next | فشل المزود، جاري المحاولة التالية",
                    extra={"model": model, "error": str(exc)},
                )

        self._active_provider = FallbackStatus.EXHAUSTED
        raise EmbeddingProviderError(
            f"All embedding providers exhausted | استنفاد جميع مزودي التضمينات: {last_error}",
            provider=EmbeddingProvider.SENTENCE_TRANSFORMERS if EmbeddingProvider else "unknown",
            recoverable=False,
            original_error=last_error,
        )

    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Embed multiple texts with consistency guarantees.
        تضمين نصوص متعددة مع ضمان الاتساق
        """
        results: list[EmbeddingResult] = []
        for text in texts:
            result = await self.embed(text)
            results.append(result)
        return results

    # -- bilingual embedding -------------------------------------------------

    async def embed_bilingual(self, text_en: str, text_ar: str) -> dict[str, Any]:
        """
        Embed bilingual content and return combined representation.
        تضمين محتوى ثنائي اللغة وإرجاع تمثيل مدمج

        Returns a dict with keys:
            embedding_en, embedding_ar, embedding_combined,
            similarity, dimension
        """
        result_en = await self.embed(text_en)
        result_ar = await self.embed(text_ar)

        # Combined = element-wise average of the two vectors
        combined = [(a + b) / 2.0 for a, b in zip(result_en.embedding, result_ar.embedding)]
        if self._config.normalize:
            combined = _l2_normalize(combined)

        # Cosine similarity between the two language vectors
        similarity = self._cosine(result_en.embedding, result_ar.embedding)

        return {
            "embedding_en": result_en.embedding,
            "embedding_ar": result_ar.embedding,
            "embedding_combined": combined,
            "similarity": similarity,
            "dimension": self._config.default_dimension,
        }

    # -- consistency validation ----------------------------------------------

    def ensure_consistency(self, vectors: list[list[float]]) -> bool:
        """
        Validate that all vectors match the configured dimension.
        التحقق من أن جميع المتجهات تطابق البعد المحدد

        Returns True when every vector has the expected dimension.
        """
        expected = self._config.default_dimension
        for i, vec in enumerate(vectors):
            if len(vec) != expected:
                logger.error(
                    "Dimension mismatch | عدم تطابق البعد",
                    extra={"index": i, "got": len(vec), "expected": expected},
                )
                return False
        return True

    # -- cleanup -------------------------------------------------------------

    async def close(self) -> None:
        """Close all underlying adapters | إغلاق جميع المحولات"""
        for adapter in self._adapters.values():
            await adapter.close()
        self._adapters.clear()

    def clear_cache(self) -> None:
        """Clear caches on all adapters | مسح الذاكرة المؤقتة"""
        for adapter in self._adapters.values():
            adapter.clear_cache()

    # -- internal helpers ----------------------------------------------------

    def _preprocess(self, text: str) -> str:
        """Apply Arabic preprocessing if enabled and text contains Arabic."""
        if self._config.arabic_preprocessing and _contains_arabic(text):
            return preprocess_arabic(text)
        return text

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        """Cosine similarity between two vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na == 0.0 or nb == 0.0:
            return 0.0
        return dot / (na * nb)


# ---------------------------------------------------------------------------
# Singleton factory
# ---------------------------------------------------------------------------

_instance: UnifiedEmbeddingsManager | None = None


def get_unified_embeddings(
    config: EmbeddingConsistencyConfig | None = None,
) -> UnifiedEmbeddingsManager:
    """
    Get or create the singleton UnifiedEmbeddingsManager.
    الحصول على أو إنشاء مدير التضمينات الموحد (نسخة وحيدة)

    Pass a config to replace the existing instance; otherwise the
    previously created instance is returned.
    """
    global _instance
    if _instance is None or config is not None:
        _instance = UnifiedEmbeddingsManager(config)
    return _instance


# ═══════════════════════════════════════════════════════════════════════════════
# UnifiedEmbedder - GraphMemory <-> EmbeddingsAdapter Bridge (G-05)
# المضمّن الموحد - جسر بين ذاكرة الرسم البياني ومحول التضمينات
# ═══════════════════════════════════════════════════════════════════════════════


def _project_embedding(
    embedding: list[float],
    source_dim: int,
    target_dim: int,
) -> list[float]:
    """
    Project an embedding from one dimension to another.
    إسقاط تضمين من بعد إلى آخر.

    If target_dim > source_dim: pad with zeros and re-normalize.
    If target_dim < source_dim: truncate and re-normalize.
    """
    if source_dim == target_dim:
        return embedding

    if target_dim > source_dim:
        projected = embedding + [0.0] * (target_dim - source_dim)
    else:
        projected = embedding[:target_dim]

    norm = math.sqrt(sum(x * x for x in projected))
    if norm > 0:
        projected = [x / norm for x in projected]

    return projected


_unified_embedder_instance: UnifiedEmbedder | None = None


class UnifiedEmbedder:
    """
    Bridge that wraps both SimpleEmbedder and EmbeddingsAdapter.
    جسر يغلف كلاً من المضمّن البسيط ومحول التضمينات.

    Uses EmbeddingsAdapter when available for higher quality embeddings,
    and falls back to SimpleEmbedder (TF-IDF hashing) for offline/minimal
    environments. Ensures consistent embedding dimensions across the system
    and provides a migration path for GraphMemory to use production embeddings.

    Usage:
        embedder = get_unified_embedder()

        # Drop-in replacement for SimpleEmbedder.embed()
        vector = await embedder.embed_raw("farm entity description")

        # Rich result with metadata
        result = await embedder.embed("Wheat irrigation schedule")
        print(result.embedding, result.dimension)

        # Similarity (works across Arabic/English)
        score = await embedder.similarity("wheat disease", "مرض القمح")
    """

    DEFAULT_DIMENSION: int = 384

    def __init__(
        self,
        target_dimension: int | None = None,
        adapter_config: Any = None,
        prefer_adapter: bool = True,
    ):
        """
        Initialize the UnifiedEmbedder.

        Args:
            target_dimension: Force all embeddings to this dimension.
                            If None, uses the active provider's native dimension.
            adapter_config: Optional EmbeddingConfig for EmbeddingsAdapter.
            prefer_adapter: If True, prefer EmbeddingsAdapter over SimpleEmbedder.
        """
        self._target_dimension = target_dimension
        self._prefer_adapter = prefer_adapter
        self._adapter: EmbeddingsAdapter | None = None
        self._simple: SimpleEmbedder | None = None  # type: ignore[assignment]
        self._active_provider_name: str = "none"
        self._native_dimension: int = target_dimension or self.DEFAULT_DIMENSION

        self._initialize_providers(adapter_config)

    def _initialize_providers(self, adapter_config: Any = None) -> None:
        """Initialize embedding providers based on availability."""
        adapter_ok = False

        if self._prefer_adapter and EmbeddingsAdapter is not None:
            try:
                cfg = adapter_config
                if cfg is None:
                    cfg = EmbeddingConfig(
                        provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
                        model="all-MiniLM-L6-v2",
                        cache_enabled=True,
                    )
                self._adapter = EmbeddingsAdapter(cfg)
                self._native_dimension = self._adapter.get_dimension()
                self._active_provider_name = "embeddings_adapter"
                adapter_ok = True
                logger.info(
                    "unified_embedder_using_adapter",
                    extra={
                        "provider": cfg.provider.value,
                        "model": cfg.model,
                        "dimension": self._native_dimension,
                    },
                )
            except Exception as e:
                logger.warning(
                    "unified_embedder_adapter_init_failed",
                    extra={"error": str(e)},
                )

        if _SIMPLE_EMBEDDER_AVAILABLE and SimpleEmbedder is not None:
            dim = self._target_dimension or self.DEFAULT_DIMENSION
            self._simple = SimpleEmbedder(dimension=dim)
            if not adapter_ok:
                self._active_provider_name = "simple_embedder"
                self._native_dimension = dim
                logger.info(
                    "unified_embedder_using_simple",
                    extra={"dimension": dim},
                )

        if self._adapter is None and self._simple is None:
            raise RuntimeError(
                "No embedding provider available. Install sentence-transformers "
                "or ensure shared.ai.graph_memory is importable."
            )

    # -- properties ----------------------------------------------------------

    @property
    def active_provider(self) -> str:
        """Name of the active embedding provider | اسم مزود التضمين النشط"""
        return self._active_provider_name

    @property
    def dimension(self) -> int:
        """Output embedding dimension | بُعد التضمين الناتج"""
        return self._target_dimension if self._target_dimension else self._native_dimension

    # -- core methods --------------------------------------------------------

    async def embed(self, text: str) -> EmbeddingResult:
        """
        Generate embedding with full metadata.
        توليد تضمين مع بيانات وصفية كاملة.

        Tries EmbeddingsAdapter first, falls back to SimpleEmbedder.
        Returns an EmbeddingResult (from shared.ai.embeddings) when the
        adapter is active, or a compatible object when using SimpleEmbedder.
        """
        start_time = time.time()

        # Try adapter
        if self._adapter is not None and self._active_provider_name == "embeddings_adapter":
            try:
                result = await self._adapter.embed(text)
                # Project if needed
                if self._target_dimension and len(result.embedding) != self._target_dimension:
                    result.embedding[:] = _project_embedding(
                        result.embedding,
                        len(result.embedding),
                        self._target_dimension,
                    )
                return result
            except Exception as exc:
                logger.warning(
                    "unified_embedder_adapter_failed",
                    extra={"error": str(exc)},
                )
                if self._simple is None:
                    raise

        # SimpleEmbedder fallback
        if self._simple is not None:
            vector = await self._simple.embed(text)
            if self._target_dimension and len(vector) != self._target_dimension:
                vector = _project_embedding(vector, len(vector), self._target_dimension)

            latency = (time.time() - start_time) * 1000

            if EmbeddingResult is not None:
                return EmbeddingResult(
                    embedding=vector,
                    text=text,
                    provider=EmbeddingProvider.SENTENCE_TRANSFORMERS if EmbeddingProvider else "simple",
                    model="tfidf_hash",
                    dimension=len(vector),
                    latency_ms=latency,
                    cached=False,
                )
            # Minimal fallback when EmbeddingResult class is unavailable
            from dataclasses import dataclass as _dc

            @_dc
            class _MinimalResult:
                embedding: list[float]
                text: str
                provider: str = "simple"
                model: str = "tfidf_hash"
                dimension: int = 0
                latency_ms: float = 0.0
                cached: bool = False

            return _MinimalResult(  # type: ignore[return-value]
                embedding=vector,
                text=text,
                dimension=len(vector),
                latency_ms=latency,
            )

        raise RuntimeError("No embedding provider available")

    async def embed_raw(self, text: str) -> list[float]:
        """
        Generate a raw embedding vector (GraphMemory compatible).
        توليد متجه تضمين خام (متوافق مع ذاكرة الرسم البياني).

        Drop-in replacement for ``SimpleEmbedder.embed()``.
        """
        result = await self.embed(text)
        return result.embedding

    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Embed multiple texts.
        تضمين نصوص متعددة.
        """
        return [await self.embed(t) for t in texts]

    async def embed_batch_raw(self, texts: list[str]) -> list[list[float]]:
        """
        Generate raw vectors for a batch (GraphMemory compatible).
        توليد متجهات خام لدفعة (متوافق مع ذاكرة الرسم البياني).
        """
        return [await self.embed_raw(t) for t in texts]

    async def similarity(self, text1: str, text2: str) -> float:
        """
        Cosine similarity between two texts.
        التشابه بين نصين.
        """
        if self._adapter is not None and self._active_provider_name == "embeddings_adapter":
            try:
                return await self._adapter.similarity(text1, text2)
            except Exception:
                pass

        v1 = await self.embed_raw(text1)
        v2 = await self.embed_raw(text2)
        return self._cosine(v1, v2)

    async def find_most_similar(
        self,
        query: str,
        candidates: list[str],
        top_k: int = 5,
    ) -> list[tuple[str, float]]:
        """
        Find most similar texts to a query.
        إيجاد النصوص الأكثر تشابهاً مع استعلام.
        """
        if self._adapter is not None and self._active_provider_name == "embeddings_adapter":
            try:
                return await self._adapter.find_most_similar(query, candidates, top_k)
            except Exception:
                pass

        query_vec = await self.embed_raw(query)
        scored: list[tuple[str, float]] = []
        for c in candidates:
            c_vec = await self.embed_raw(c)
            scored.append((c, self._cosine(query_vec, c_vec)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    async def is_available(self) -> bool:
        """Check if the embedder is functional | التحقق من عمل المضمّن"""
        try:
            await self.embed_raw("test")
            return True
        except Exception:
            return False

    def get_provider_info(self) -> dict[str, Any]:
        """Diagnostic info about the active provider | معلومات تشخيصية"""
        info: dict[str, Any] = {
            "active_provider": self._active_provider_name,
            "dimension": self.dimension,
            "target_dimension": self._target_dimension,
            "native_dimension": self._native_dimension,
            "adapter_available": self._adapter is not None,
            "simple_available": self._simple is not None,
        }
        if self._adapter is not None:
            info["adapter_provider"] = self._adapter.config.provider.value
            info["adapter_model"] = self._adapter.config.model
        return info

    def update_idf(self, documents: list[str]) -> None:
        """
        Update IDF values for SimpleEmbedder (improves quality when active).
        تحديث قيم IDF للمضمّن البسيط.
        """
        if self._simple is not None:
            self._simple.update_idf(documents)

    def clear_cache(self) -> None:
        """Clear embedding caches | مسح الذاكرة المؤقتة"""
        if self._adapter is not None:
            self._adapter.clear_cache()

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        if len(a) != len(b):
            target = max(len(a), len(b))
            a = _project_embedding(a, len(a), target)
            b = _project_embedding(b, len(b), target)
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        return dot / (na * nb) if na and nb else 0.0


# ---------------------------------------------------------------------------
# Singleton access for UnifiedEmbedder
# ---------------------------------------------------------------------------


def get_unified_embedder(
    target_dimension: int | None = None,
    adapter_config: Any = None,
    prefer_adapter: bool = True,
) -> UnifiedEmbedder:
    """
    Get or create the singleton UnifiedEmbedder instance.
    الحصول على أو إنشاء مثيل المضمّن الموحد الوحيد.

    Usage:
        embedder = get_unified_embedder()
        vector = await embedder.embed_raw("wheat irrigation schedule")
    """
    global _unified_embedder_instance
    if _unified_embedder_instance is None:
        _unified_embedder_instance = UnifiedEmbedder(
            target_dimension=target_dimension,
            adapter_config=adapter_config,
            prefer_adapter=prefer_adapter,
        )
    return _unified_embedder_instance


def reset_unified_embedder() -> None:
    """Reset the singleton (useful for testing) | إعادة تعيين المثيل الوحيد"""
    global _unified_embedder_instance
    _unified_embedder_instance = None


def create_graph_memory_embedder(
    target_dimension: int = 128,
    prefer_adapter: bool = True,
) -> UnifiedEmbedder:
    """
    Create an embedder configured for GraphMemory use.
    إنشاء مضمّن مهيأ لاستخدام ذاكرة الرسم البياني.

    GraphMemory's SimpleEmbedder defaults to 128 dimensions.
    This factory creates a UnifiedEmbedder that projects to 128 dims
    for backward compatibility, while using better embeddings internally
    when EmbeddingsAdapter is available.

    Usage:
        from shared.ai.unified_embeddings import create_graph_memory_embedder

        embedder = create_graph_memory_embedder()
        # Drop-in replacement for SimpleEmbedder.embed()
        vector = await embedder.embed_raw("farm entity description")
        assert len(vector) == 128
    """
    return UnifiedEmbedder(
        target_dimension=target_dimension,
        prefer_adapter=prefer_adapter,
    )
