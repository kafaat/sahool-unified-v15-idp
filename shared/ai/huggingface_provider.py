"""
Huggingface Provider Module for SAHOOL AI
==========================================
مزود Huggingface للذكاء الاصطناعي في منصة سهول

Provides integration with Huggingface models for:
- Text embeddings (Arabic & English)
- Agricultural domain models
- Multilingual support
- Local model caching for offline-first architecture

Inspired by GenAI Learning Roadmap - Embedding Models component.

Author: SAHOOL Platform Team
Created: January 2026
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import time
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class HuggingfaceModelType(StrEnum):
    """Types of Huggingface models supported"""

    # Embedding models
    EMBEDDING = "embedding"

    # Text generation models
    TEXT_GENERATION = "text_generation"

    # Image models
    IMAGE_CLASSIFICATION = "image_classification"
    IMAGE_SEGMENTATION = "image_segmentation"

    # Multimodal
    VISION_LANGUAGE = "vision_language"


class EmbeddingModelFamily(StrEnum):
    """Embedding model families optimized for different use cases"""

    # Multilingual models (Arabic support)
    MULTILINGUAL_E5 = "multilingual-e5"
    MULTILINGUAL_MPNET = "multilingual-mpnet"
    PARAPHRASE_MULTILINGUAL = "paraphrase-multilingual"

    # Arabic-specific models
    ARABIC_BERT = "arabic-bert"
    ARABERT = "arabert"
    MARBERT = "marbert"

    # General English models
    ALL_MINILM = "all-minilm"
    ALL_MPNET = "all-mpnet"
    BGE = "bge"

    # Agricultural domain (custom fine-tuned)
    AGRI_ARABIC = "agri-arabic"


@dataclass
class HuggingfaceConfig:
    """Configuration for Huggingface provider

    إعدادات مزود Huggingface
    """

    # API settings
    api_token: str | None = None
    api_url: str = "https://api-inference.huggingface.co"

    # Model settings
    default_embedding_model: str = "intfloat/multilingual-e5-large"
    default_text_model: str = "aubmindlab/bert-base-arabertv02"

    # Cache settings
    cache_dir: str | None = None
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600 * 24  # 24 hours

    # Local model settings
    use_local_models: bool = True
    local_model_dir: str | None = None
    download_if_missing: bool = True

    # Performance settings
    batch_size: int = 32
    max_length: int = 512
    normalize_embeddings: bool = True

    # Timeout settings
    timeout_seconds: float = 30.0
    retry_count: int = 3
    retry_delay_seconds: float = 1.0

    # Device settings
    device: str = "auto"  # auto, cpu, cuda, mps

    def __post_init__(self):
        """Initialize defaults from environment"""
        if self.api_token is None:
            self.api_token = os.getenv("HUGGINGFACE_API_TOKEN")

        if self.cache_dir is None:
            self.cache_dir = os.getenv("HUGGINGFACE_CACHE_DIR", str(Path.home() / ".cache" / "huggingface" / "sahool"))

        if self.local_model_dir is None:
            self.local_model_dir = os.getenv(
                "HUGGINGFACE_MODEL_DIR", str(Path.home() / ".cache" / "huggingface" / "models")
            )


@dataclass
class EmbeddingResult:
    """Result of an embedding operation

    نتيجة عملية التضمين
    """

    embedding: list[float]
    model: str
    dimension: int
    latency_ms: float
    from_cache: bool = False
    token_count: int = 0

    # Metadata
    text_hash: str = ""
    normalized: bool = True


@dataclass
class BatchEmbeddingResult:
    """Result of batch embedding operation

    نتيجة عملية التضمين بالدفعات
    """

    embeddings: list[list[float]]
    model: str
    dimension: int
    total_latency_ms: float
    avg_latency_ms: float
    cache_hits: int = 0
    cache_misses: int = 0
    total_tokens: int = 0

    def __len__(self) -> int:
        return len(self.embeddings)


@dataclass
class ModelInfo:
    """Information about a Huggingface model

    معلومات نموذج Huggingface
    """

    model_id: str
    model_type: HuggingfaceModelType
    family: EmbeddingModelFamily | None = None

    # Model characteristics
    dimension: int = 0
    max_sequence_length: int = 512
    languages: list[str] = field(default_factory=lambda: ["en"])

    # Availability
    is_local: bool = False
    is_cached: bool = False
    download_size_mb: float = 0.0

    # Performance
    avg_latency_ms: float = 0.0

    # Arabic support
    supports_arabic: bool = False
    arabic_quality: str = "unknown"  # excellent, good, fair, poor


# Pre-defined model configurations
EMBEDDING_MODELS: dict[str, ModelInfo] = {
    # Multilingual models with Arabic support
    "intfloat/multilingual-e5-large": ModelInfo(
        model_id="intfloat/multilingual-e5-large",
        model_type=HuggingfaceModelType.EMBEDDING,
        family=EmbeddingModelFamily.MULTILINGUAL_E5,
        dimension=1024,
        max_sequence_length=512,
        languages=["ar", "en", "fr", "de", "es", "zh", "ja", "ko", "ru"],
        supports_arabic=True,
        arabic_quality="excellent",
        download_size_mb=2200,
    ),
    "intfloat/multilingual-e5-base": ModelInfo(
        model_id="intfloat/multilingual-e5-base",
        model_type=HuggingfaceModelType.EMBEDDING,
        family=EmbeddingModelFamily.MULTILINGUAL_E5,
        dimension=768,
        max_sequence_length=512,
        languages=["ar", "en", "fr", "de", "es", "zh", "ja", "ko", "ru"],
        supports_arabic=True,
        arabic_quality="excellent",
        download_size_mb=1100,
    ),
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2": ModelInfo(
        model_id="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        model_type=HuggingfaceModelType.EMBEDDING,
        family=EmbeddingModelFamily.MULTILINGUAL_MPNET,
        dimension=768,
        max_sequence_length=128,
        languages=["ar", "en", "de", "es", "fr", "it", "nl", "pl", "pt", "ru", "zh"],
        supports_arabic=True,
        arabic_quality="good",
        download_size_mb=970,
    ),
    # Arabic-specific models
    "aubmindlab/bert-base-arabertv02": ModelInfo(
        model_id="aubmindlab/bert-base-arabertv02",
        model_type=HuggingfaceModelType.EMBEDDING,
        family=EmbeddingModelFamily.ARABERT,
        dimension=768,
        max_sequence_length=512,
        languages=["ar"],
        supports_arabic=True,
        arabic_quality="excellent",
        download_size_mb=680,
    ),
    "UBC-NLP/MARBERT": ModelInfo(
        model_id="UBC-NLP/MARBERT",
        model_type=HuggingfaceModelType.EMBEDDING,
        family=EmbeddingModelFamily.MARBERT,
        dimension=768,
        max_sequence_length=512,
        languages=["ar"],
        supports_arabic=True,
        arabic_quality="excellent",
        download_size_mb=680,
    ),
    # English models (faster, smaller)
    "sentence-transformers/all-MiniLM-L6-v2": ModelInfo(
        model_id="sentence-transformers/all-MiniLM-L6-v2",
        model_type=HuggingfaceModelType.EMBEDDING,
        family=EmbeddingModelFamily.ALL_MINILM,
        dimension=384,
        max_sequence_length=256,
        languages=["en"],
        supports_arabic=False,
        arabic_quality="poor",
        download_size_mb=90,
    ),
    "sentence-transformers/all-mpnet-base-v2": ModelInfo(
        model_id="sentence-transformers/all-mpnet-base-v2",
        model_type=HuggingfaceModelType.EMBEDDING,
        family=EmbeddingModelFamily.ALL_MPNET,
        dimension=768,
        max_sequence_length=384,
        languages=["en"],
        supports_arabic=False,
        arabic_quality="poor",
        download_size_mb=420,
    ),
    "BAAI/bge-large-en-v1.5": ModelInfo(
        model_id="BAAI/bge-large-en-v1.5",
        model_type=HuggingfaceModelType.EMBEDDING,
        family=EmbeddingModelFamily.BGE,
        dimension=1024,
        max_sequence_length=512,
        languages=["en"],
        supports_arabic=False,
        arabic_quality="poor",
        download_size_mb=1340,
    ),
}

# Agricultural domain model recommendations
AGRICULTURAL_MODELS: dict[str, str] = {
    # Best for Arabic agricultural texts
    "arabic_agriculture": "intfloat/multilingual-e5-large",
    # Best for English agricultural texts
    "english_agriculture": "BAAI/bge-large-en-v1.5",
    # Best for mixed Arabic/English
    "bilingual_agriculture": "intfloat/multilingual-e5-base",
    # Best for fast inference
    "fast_agriculture": "sentence-transformers/all-MiniLM-L6-v2",
}


class EmbeddingCache:
    """In-memory cache for embeddings with persistence support

    ذاكرة تخزين مؤقت للتضمينات
    """

    def __init__(
        self,
        cache_dir: str | None = None,
        ttl_seconds: int = 3600 * 24,
        max_size: int = 10000,
    ):
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size

        self._cache: dict[str, tuple[list[float], float]] = {}
        self._access_order: list[str] = []

        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _hash_key(self, text: str, model: str) -> str:
        """Generate cache key from text and model"""
        content = f"{model}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    def get(self, text: str, model: str) -> list[float] | None:
        """Get embedding from cache"""
        key = self._hash_key(text, model)

        if key in self._cache:
            embedding, timestamp = self._cache[key]
            if time.time() - timestamp < self.ttl_seconds:
                # Update access order
                if key in self._access_order:
                    self._access_order.remove(key)
                self._access_order.append(key)
                return embedding
            else:
                # Expired
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)

        return None

    def set(self, text: str, model: str, embedding: list[float]) -> None:
        """Store embedding in cache"""
        key = self._hash_key(text, model)

        # Evict if at capacity
        while len(self._cache) >= self.max_size and self._access_order:
            oldest_key = self._access_order.pop(0)
            if oldest_key in self._cache:
                del self._cache[oldest_key]

        self._cache[key] = (embedding, time.time())
        self._access_order.append(key)

    def clear(self) -> None:
        """Clear all cached embeddings"""
        self._cache.clear()
        self._access_order.clear()

    @property
    def size(self) -> int:
        """Number of cached embeddings"""
        return len(self._cache)

    @property
    def stats(self) -> dict[str, Any]:
        """Cache statistics"""
        return {
            "size": self.size,
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
        }


class HuggingfaceProvider:
    """Huggingface model provider for SAHOOL AI

    مزود نماذج Huggingface للذكاء الاصطناعي في سهول

    Provides:
    - Text embeddings with multilingual support
    - Local model caching for offline use
    - Batch processing for efficiency
    - Arabic language optimization

    Example:
        provider = HuggingfaceProvider()

        # Single embedding
        result = await provider.embed("توصية زراعية للقمح")

        # Batch embedding
        results = await provider.embed_batch([
            "Agricultural advice for wheat",
            "نصائح زراعية للقمح",
        ])
    """

    def __init__(self, config: HuggingfaceConfig | None = None):
        self.config = config or HuggingfaceConfig()

        # Cache
        self._cache = (
            EmbeddingCache(
                cache_dir=self.config.cache_dir,
                ttl_seconds=self.config.cache_ttl_seconds,
            )
            if self.config.cache_enabled
            else None
        )

        # Model instances (lazy loaded)
        self._models: dict[str, Any] = {}
        self._tokenizers: dict[str, Any] = {}

        # HTTP client for API calls
        self._http_client: Any | None = None

        # Statistics
        self._stats = {
            "total_embeddings": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "api_calls": 0,
            "local_calls": 0,
            "total_tokens": 0,
            "total_latency_ms": 0.0,
        }

    async def _get_http_client(self) -> Any:
        """Get or create HTTP client"""
        if self._http_client is None:
            try:
                import httpx

                self._http_client = httpx.AsyncClient(
                    timeout=self.config.timeout_seconds,
                    headers={"Authorization": f"Bearer {self.config.api_token}"} if self.config.api_token else {},
                )
            except ImportError:
                logger.warning("httpx not available, API calls will fail")
                return None
        return self._http_client

    def _get_device(self) -> str:
        """Determine the best device to use"""
        if self.config.device != "auto":
            return self.config.device

        try:
            import torch

            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass

        return "cpu"

    async def _load_local_model(self, model_id: str) -> tuple[Any, Any]:
        """Load model locally using transformers"""
        if model_id in self._models:
            return self._models[model_id], self._tokenizers[model_id]

        try:
            import torch as _torch  # noqa: F401 - Required for model operations
            from transformers import AutoModel, AutoTokenizer

            device = self._get_device()
            cache_dir = self.config.local_model_dir

            logger.info(f"Loading model {model_id} on {device}")

            revision = os.getenv("HUGGINGFACE_MODEL_REVISION", "main")

            tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                cache_dir=cache_dir,
                revision=revision,
            )

            model = AutoModel.from_pretrained(
                model_id,
                cache_dir=cache_dir,
                revision=revision,
            )

            if device != "cpu":
                model = model.to(device)

            model.eval()

            self._models[model_id] = model
            self._tokenizers[model_id] = tokenizer

            return model, tokenizer

        except ImportError as e:
            logger.error(f"transformers/torch not available: {e}")
            raise RuntimeError(
                "Local models require transformers and torch. Install with: pip install transformers torch"
            ) from e
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            raise

    async def _embed_local(
        self,
        texts: list[str],
        model_id: str,
    ) -> list[list[float]]:
        """Generate embeddings using local model"""
        model, tokenizer = await self._load_local_model(model_id)

        try:
            import torch

            device = self._get_device()

            # Tokenize
            encoded = tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=self.config.max_length,
                return_tensors="pt",
            )

            if device != "cpu":
                encoded = {k: v.to(device) for k, v in encoded.items()}

            # Generate embeddings
            with torch.no_grad():
                outputs = model(**encoded)

                # Mean pooling
                attention_mask = encoded["attention_mask"]
                token_embeddings = outputs.last_hidden_state

                input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()

                embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
                    input_mask_expanded.sum(1), min=1e-9
                )

                # Normalize if configured
                if self.config.normalize_embeddings:
                    embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

                # Convert to list
                return embeddings.cpu().tolist()

        except Exception as e:
            logger.error(f"Local embedding failed: {e}")
            raise

    async def _embed_api(
        self,
        texts: list[str],
        model_id: str,
    ) -> list[list[float]]:
        """Generate embeddings using Huggingface API"""
        client = await self._get_http_client()
        if client is None:
            raise RuntimeError("HTTP client not available")

        api_url = f"{self.config.api_url}/pipeline/feature-extraction/{model_id}"

        for attempt in range(self.config.retry_count):
            try:
                response = await client.post(
                    api_url,
                    json={"inputs": texts, "options": {"wait_for_model": True}},
                )

                if response.status_code == 200:
                    embeddings = response.json()

                    # Handle nested response format
                    if embeddings and isinstance(embeddings[0][0], list):
                        # Mean pooling for token-level embeddings
                        result = []
                        for emb in embeddings:
                            mean_emb = [sum(token[i] for token in emb) / len(emb) for i in range(len(emb[0]))]
                            result.append(mean_emb)
                        return result

                    return embeddings

                elif response.status_code == 503:
                    # Model loading
                    logger.info(f"Model {model_id} loading, waiting...")
                    await asyncio.sleep(self.config.retry_delay_seconds * (attempt + 1))
                    continue

                else:
                    logger.error(f"API error: {response.status_code} - {response.text}")
                    raise RuntimeError(f"API error: {response.status_code}")

            except Exception:
                if attempt < self.config.retry_count - 1:
                    await asyncio.sleep(self.config.retry_delay_seconds * (attempt + 1))
                else:
                    raise

        raise RuntimeError(f"Failed after {self.config.retry_count} attempts")

    async def embed(
        self,
        text: str,
        model_id: str | None = None,
    ) -> EmbeddingResult:
        """Generate embedding for a single text

        إنشاء تضمين لنص واحد

        Args:
            text: Text to embed
            model_id: Model to use (default: config default)

        Returns:
            EmbeddingResult with embedding vector
        """
        model_id = model_id or self.config.default_embedding_model
        start_time = time.time()

        # Check cache
        from_cache = False
        if self._cache:
            cached = self._cache.get(text, model_id)
            if cached:
                from_cache = True
                self._stats["cache_hits"] += 1
                embedding = cached
            else:
                self._stats["cache_misses"] += 1

        if not from_cache:
            # Generate embedding
            if self.config.use_local_models:
                embeddings = await self._embed_local([text], model_id)
                self._stats["local_calls"] += 1
            else:
                embeddings = await self._embed_api([text], model_id)
                self._stats["api_calls"] += 1

            embedding = embeddings[0]

            # Cache result
            if self._cache:
                self._cache.set(text, model_id, embedding)

        latency_ms = (time.time() - start_time) * 1000
        self._stats["total_embeddings"] += 1
        self._stats["total_latency_ms"] += latency_ms

        # Get model info
        model_info = EMBEDDING_MODELS.get(model_id)
        dimension = model_info.dimension if model_info else len(embedding)

        return EmbeddingResult(
            embedding=embedding,
            model=model_id,
            dimension=dimension,
            latency_ms=latency_ms,
            from_cache=from_cache,
            text_hash=hashlib.sha256(text.encode()).hexdigest()[:16],
            normalized=self.config.normalize_embeddings,
        )

    async def embed_batch(
        self,
        texts: list[str],
        model_id: str | None = None,
        show_progress: bool = False,
    ) -> BatchEmbeddingResult:
        """Generate embeddings for multiple texts

        إنشاء تضمينات لنصوص متعددة

        Args:
            texts: List of texts to embed
            model_id: Model to use
            show_progress: Show progress indicator

        Returns:
            BatchEmbeddingResult with all embeddings
        """
        model_id = model_id or self.config.default_embedding_model
        start_time = time.time()

        embeddings: list[list[float]] = []
        cache_hits = 0
        cache_misses = 0
        texts_to_embed: list[tuple[int, str]] = []

        # Check cache for each text
        for i, text in enumerate(texts):
            if self._cache:
                cached = self._cache.get(text, model_id)
                if cached:
                    embeddings.append(cached)
                    cache_hits += 1
                    continue

            texts_to_embed.append((i, text))
            embeddings.append([])  # Placeholder
            cache_misses += 1

        # Embed uncached texts in batches
        if texts_to_embed:
            uncached_texts = [t for _, t in texts_to_embed]

            # Process in batches
            all_new_embeddings: list[list[float]] = []
            for i in range(0, len(uncached_texts), self.config.batch_size):
                batch = uncached_texts[i : i + self.config.batch_size]

                if self.config.use_local_models:
                    batch_embeddings = await self._embed_local(batch, model_id)
                    self._stats["local_calls"] += 1
                else:
                    batch_embeddings = await self._embed_api(batch, model_id)
                    self._stats["api_calls"] += 1

                all_new_embeddings.extend(batch_embeddings)

            # Place embeddings in correct positions and cache
            for (idx, text), embedding in zip(texts_to_embed, all_new_embeddings):
                embeddings[idx] = embedding
                if self._cache:
                    self._cache.set(text, model_id, embedding)

        total_latency = (time.time() - start_time) * 1000

        # Update stats
        self._stats["total_embeddings"] += len(texts)
        self._stats["cache_hits"] += cache_hits
        self._stats["cache_misses"] += cache_misses
        self._stats["total_latency_ms"] += total_latency

        # Get model info
        model_info = EMBEDDING_MODELS.get(model_id)
        dimension = model_info.dimension if model_info else len(embeddings[0]) if embeddings else 0

        return BatchEmbeddingResult(
            embeddings=embeddings,
            model=model_id,
            dimension=dimension,
            total_latency_ms=total_latency,
            avg_latency_ms=total_latency / len(texts) if texts else 0,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
        )

    async def similarity(
        self,
        text1: str,
        text2: str,
        model_id: str | None = None,
    ) -> float:
        """Calculate semantic similarity between two texts

        حساب التشابه الدلالي بين نصين

        Args:
            text1: First text
            text2: Second text
            model_id: Model to use

        Returns:
            Similarity score (0.0 to 1.0)
        """
        result = await self.embed_batch([text1, text2], model_id)

        # Cosine similarity
        emb1 = result.embeddings[0]
        emb2 = result.embeddings[1]

        dot_product = sum(a * b for a, b in zip(emb1, emb2))
        norm1 = sum(a * a for a in emb1) ** 0.5
        norm2 = sum(b * b for b in emb2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    async def find_most_similar(
        self,
        query: str,
        candidates: list[str],
        top_k: int = 5,
        model_id: str | None = None,
    ) -> list[tuple[str, float, int]]:
        """Find most similar texts from candidates

        إيجاد النصوص الأكثر تشابهاً

        Args:
            query: Query text
            candidates: List of candidate texts
            top_k: Number of results to return
            model_id: Model to use

        Returns:
            List of (text, similarity, index) tuples
        """
        # Embed query and candidates
        all_texts = [query] + candidates
        result = await self.embed_batch(all_texts, model_id)

        query_emb = result.embeddings[0]
        candidate_embs = result.embeddings[1:]

        # Calculate similarities
        similarities = []
        for i, (text, emb) in enumerate(zip(candidates, candidate_embs)):
            dot_product = sum(a * b for a, b in zip(query_emb, emb))
            norm1 = sum(a * a for a in query_emb) ** 0.5
            norm2 = sum(b * b for b in emb) ** 0.5

            sim = dot_product / (norm1 * norm2) if norm1 and norm2 else 0.0
            similarities.append((text, sim, i))

        # Sort and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def get_model_info(self, model_id: str) -> ModelInfo | None:
        """Get information about a model

        الحصول على معلومات النموذج
        """
        return EMBEDDING_MODELS.get(model_id)

    def list_models(
        self,
        arabic_only: bool = False,
        family: EmbeddingModelFamily | None = None,
    ) -> list[ModelInfo]:
        """List available models

        قائمة النماذج المتاحة
        """
        models = list(EMBEDDING_MODELS.values())

        if arabic_only:
            models = [m for m in models if m.supports_arabic]

        if family:
            models = [m for m in models if m.family == family]

        return models

    def get_recommended_model(
        self,
        use_case: str = "bilingual_agriculture",
    ) -> str:
        """Get recommended model for use case

        الحصول على النموذج الموصى به

        Args:
            use_case: One of:
                - arabic_agriculture
                - english_agriculture
                - bilingual_agriculture
                - fast_agriculture
        """
        return AGRICULTURAL_MODELS.get(use_case, self.config.default_embedding_model)

    @property
    def stats(self) -> dict[str, Any]:
        """Provider statistics"""
        return {
            **self._stats,
            "cache_stats": self._cache.stats if self._cache else None,
            "loaded_models": list(self._models.keys()),
        }

    def clear_cache(self) -> None:
        """Clear embedding cache"""
        if self._cache:
            self._cache.clear()

    async def close(self) -> None:
        """Close provider and release resources"""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

        self._models.clear()
        self._tokenizers.clear()


# ============================================================================
# Singleton Instance and Convenience Functions
# ============================================================================

_provider_instance: HuggingfaceProvider | None = None


def get_huggingface_provider(
    config: HuggingfaceConfig | None = None,
) -> HuggingfaceProvider:
    """Get or create Huggingface provider singleton

    الحصول على مزود Huggingface
    """
    global _provider_instance

    if _provider_instance is None or config is not None:
        _provider_instance = HuggingfaceProvider(config)

    return _provider_instance


async def embed_text(
    text: str,
    model_id: str | None = None,
) -> EmbeddingResult:
    """Convenience function to embed single text

    دالة مساعدة لتضمين نص واحد
    """
    provider = get_huggingface_provider()
    return await provider.embed(text, model_id)


async def embed_texts(
    texts: list[str],
    model_id: str | None = None,
) -> BatchEmbeddingResult:
    """Convenience function to embed multiple texts

    دالة مساعدة لتضمين نصوص متعددة
    """
    provider = get_huggingface_provider()
    return await provider.embed_batch(texts, model_id)


async def text_similarity(
    text1: str,
    text2: str,
    model_id: str | None = None,
) -> float:
    """Convenience function to calculate similarity

    دالة مساعدة لحساب التشابه
    """
    provider = get_huggingface_provider()
    return await provider.similarity(text1, text2, model_id)


def list_arabic_models() -> list[ModelInfo]:
    """List all models with Arabic support

    قائمة النماذج التي تدعم العربية
    """
    return [m for m in EMBEDDING_MODELS.values() if m.supports_arabic]


def get_best_arabic_model() -> str:
    """Get best model for Arabic text

    الحصول على أفضل نموذج للنص العربي
    """
    return AGRICULTURAL_MODELS["arabic_agriculture"]


# Export all public symbols
__all__ = [
    # Config
    "HuggingfaceConfig",
    # Enums
    "HuggingfaceModelType",
    "EmbeddingModelFamily",
    # Results
    "EmbeddingResult",
    "BatchEmbeddingResult",
    "ModelInfo",
    # Cache
    "EmbeddingCache",
    # Provider
    "HuggingfaceProvider",
    # Constants
    "EMBEDDING_MODELS",
    "AGRICULTURAL_MODELS",
    # Convenience functions
    "get_huggingface_provider",
    "embed_text",
    "embed_texts",
    "text_similarity",
    "list_arabic_models",
    "get_best_arabic_model",
]
