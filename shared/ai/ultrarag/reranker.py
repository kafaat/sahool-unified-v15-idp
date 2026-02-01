# ═══════════════════════════════════════════════════════════════════════════════
# UltraRAG Reranker - Advanced Result Reranking
# إعادة ترتيب النتائج المتقدمة
# ═══════════════════════════════════════════════════════════════════════════════

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import structlog

from .models import (
    RetrievalResult,
    RerankResult,
    RerankingMethod,
)

logger = structlog.get_logger(__name__)


@dataclass
class RerankConfig:
    """Configuration for reranking | تكوين إعادة الترتيب"""
    method: RerankingMethod = RerankingMethod.CROSS_ENCODER
    top_k: int = 5
    model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    batch_size: int = 32
    min_score_threshold: float = 0.0


class Reranker(ABC):
    """Abstract base class for rerankers | فئة أساسية مجردة لإعادة الترتيب"""

    @abstractmethod
    async def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        config: RerankConfig,
    ) -> RerankResult:
        """Rerank retrieval results"""
        pass


class CrossEncoderReranker(Reranker):
    """Cross-encoder based reranker | إعادة ترتيب بناءً على Cross-encoder"""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self._model = None
        self._initialized = False

    async def _ensure_initialized(self):
        """Lazy initialization of the cross-encoder model"""
        if self._initialized:
            return

        try:
            # Try to import sentence-transformers
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self.model_name)
            self._initialized = True
            logger.info("cross_encoder_initialized", model=self.model_name)
        except ImportError:
            logger.warning(
                "cross_encoder_import_error",
                message="sentence-transformers not installed, falling back to score-based reranking"
            )
            self._model = None
            self._initialized = True
        except Exception as e:
            logger.error("cross_encoder_init_error", error=str(e))
            self._model = None
            self._initialized = True

    async def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        config: RerankConfig,
    ) -> RerankResult:
        """Rerank using cross-encoder"""
        start_time = time.time()

        if not results:
            return RerankResult(
                results=[],
                method=RerankingMethod.CROSS_ENCODER,
                processing_time_ms=0.0,
            )

        await self._ensure_initialized()

        try:
            if self._model is not None:
                # Create query-document pairs
                pairs = [(query, r.chunk.text) for r in results]

                # Score with cross-encoder
                scores = self._model.predict(pairs)

                # Update scores and sort
                scored_results = []
                for i, result in enumerate(results):
                    result.score = float(scores[i])
                    scored_results.append(result)

                # Sort by new scores
                scored_results.sort(key=lambda x: x.score, reverse=True)

                # Update ranks
                for i, result in enumerate(scored_results):
                    result.rank = i + 1

                # Apply threshold and top_k
                final_results = [
                    r for r in scored_results[:config.top_k]
                    if r.score >= config.min_score_threshold
                ]
            else:
                # Fallback: just use original scores and return top_k
                final_results = sorted(results, key=lambda x: x.score, reverse=True)
                for i, result in enumerate(final_results):
                    result.rank = i + 1
                final_results = final_results[:config.top_k]

            elapsed = (time.time() - start_time) * 1000

            logger.info(
                "cross_encoder_rerank_complete",
                input_count=len(results),
                output_count=len(final_results),
                elapsed_ms=elapsed,
            )

            return RerankResult(
                results=final_results,
                method=RerankingMethod.CROSS_ENCODER,
                processing_time_ms=elapsed,
            )

        except Exception as e:
            logger.error("cross_encoder_rerank_error", error=str(e))
            # Fallback to original results
            return RerankResult(
                results=results[:config.top_k],
                method=RerankingMethod.CROSS_ENCODER,
                processing_time_ms=(time.time() - start_time) * 1000,
            )


class LLMReranker(Reranker):
    """LLM-based reranker using local Ollama | إعادة ترتيب بناءً على LLM محلي"""

    def __init__(self, llm_client: Any = None, model: str = "codellama:7b"):
        self.llm_client = llm_client
        self.model = model

    async def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        config: RerankConfig,
    ) -> RerankResult:
        """Rerank using LLM scoring"""
        start_time = time.time()

        if not results:
            return RerankResult(
                results=[],
                method=RerankingMethod.LLM,
                processing_time_ms=0.0,
            )

        try:
            if self.llm_client is None:
                # Fallback to original ranking
                logger.warning("llm_reranker_no_client")
                return RerankResult(
                    results=results[:config.top_k],
                    method=RerankingMethod.LLM,
                    processing_time_ms=(time.time() - start_time) * 1000,
                )

            # Create prompt for LLM to score relevance
            scored_results = []

            for result in results[:min(len(results), 20)]:  # Limit to 20 for efficiency
                prompt = self._create_scoring_prompt(query, result.chunk.text)

                response = await self.llm_client.generate(
                    prompt=prompt,
                    model=self.model,
                    max_tokens=10,
                    temperature=0.0,
                )

                # Parse score from response
                score = self._parse_score(response)
                result.score = score
                scored_results.append(result)

            # Sort by new scores
            scored_results.sort(key=lambda x: x.score, reverse=True)

            # Update ranks
            for i, result in enumerate(scored_results):
                result.rank = i + 1

            final_results = scored_results[:config.top_k]
            elapsed = (time.time() - start_time) * 1000

            logger.info(
                "llm_rerank_complete",
                input_count=len(results),
                output_count=len(final_results),
                elapsed_ms=elapsed,
            )

            return RerankResult(
                results=final_results,
                method=RerankingMethod.LLM,
                processing_time_ms=elapsed,
            )

        except Exception as e:
            logger.error("llm_rerank_error", error=str(e))
            return RerankResult(
                results=results[:config.top_k],
                method=RerankingMethod.LLM,
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    def _create_scoring_prompt(self, query: str, document: str) -> str:
        """Create prompt for relevance scoring"""
        return f"""Rate the relevance of the following document to the query on a scale of 0-10.
Only respond with a single number.

Query: {query}

Document: {document[:500]}

Relevance score (0-10):"""

    def _parse_score(self, response: str) -> float:
        """Parse score from LLM response"""
        try:
            # Extract first number from response
            import re
            numbers = re.findall(r'\d+(?:\.\d+)?', response)
            if numbers:
                score = float(numbers[0])
                return min(max(score / 10.0, 0.0), 1.0)  # Normalize to 0-1
            return 0.5
        except Exception:
            return 0.5


class ReciprocalRankFusionReranker(Reranker):
    """Reciprocal Rank Fusion reranker for combining multiple result lists
    دمج قوائم نتائج متعددة باستخدام Reciprocal Rank Fusion"""

    def __init__(self, k: int = 60):
        self.k = k  # RRF constant

    async def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        config: RerankConfig,
    ) -> RerankResult:
        """Apply RRF scoring (useful when results come from multiple sources)"""
        start_time = time.time()

        if not results:
            return RerankResult(
                results=[],
                method=RerankingMethod.RECIPROCAL_RANK,
                processing_time_ms=0.0,
            )

        try:
            # Group results by retrieval method
            method_groups: dict[str, list[RetrievalResult]] = {}
            for result in results:
                method = result.retrieval_method
                if method not in method_groups:
                    method_groups[method] = []
                method_groups[method].append(result)

            # Calculate RRF scores
            rrf_scores: dict[str, float] = {}
            chunk_map: dict[str, RetrievalResult] = {}

            for method, method_results in method_groups.items():
                # Sort by original score within method
                method_results.sort(key=lambda x: x.score, reverse=True)

                for rank, result in enumerate(method_results, 1):
                    doc_id = result.chunk.id
                    rrf_score = 1.0 / (self.k + rank)

                    if doc_id not in rrf_scores:
                        rrf_scores[doc_id] = 0.0
                        chunk_map[doc_id] = result

                    rrf_scores[doc_id] += rrf_score

            # Sort by RRF score
            sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

            # Create final results
            final_results = []
            for i, (doc_id, score) in enumerate(sorted_docs[:config.top_k]):
                result = chunk_map[doc_id]
                result.score = score
                result.rank = i + 1
                final_results.append(result)

            elapsed = (time.time() - start_time) * 1000

            logger.info(
                "rrf_rerank_complete",
                input_count=len(results),
                num_methods=len(method_groups),
                output_count=len(final_results),
                elapsed_ms=elapsed,
            )

            return RerankResult(
                results=final_results,
                method=RerankingMethod.RECIPROCAL_RANK,
                processing_time_ms=elapsed,
            )

        except Exception as e:
            logger.error("rrf_rerank_error", error=str(e))
            return RerankResult(
                results=results[:config.top_k],
                method=RerankingMethod.RECIPROCAL_RANK,
                processing_time_ms=(time.time() - start_time) * 1000,
            )


class NoReranker(Reranker):
    """Pass-through reranker that doesn't modify results | إعادة ترتيب بدون تعديل"""

    async def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        config: RerankConfig,
    ) -> RerankResult:
        """Simply return top_k results without reranking"""
        start_time = time.time()

        # Sort by original score
        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)

        # Update ranks
        for i, result in enumerate(sorted_results):
            result.rank = i + 1

        final_results = sorted_results[:config.top_k]
        elapsed = (time.time() - start_time) * 1000

        return RerankResult(
            results=final_results,
            method=RerankingMethod.NONE,
            processing_time_ms=elapsed,
        )


def get_reranker(method: RerankingMethod, **kwargs) -> Reranker:
    """Factory function to get appropriate reranker"""
    if method == RerankingMethod.CROSS_ENCODER:
        model = kwargs.get("model", "cross-encoder/ms-marco-MiniLM-L-6-v2")
        return CrossEncoderReranker(model_name=model)
    elif method == RerankingMethod.LLM:
        llm_client = kwargs.get("llm_client")
        model = kwargs.get("model", "codellama:7b")
        return LLMReranker(llm_client=llm_client, model=model)
    elif method == RerankingMethod.RECIPROCAL_RANK:
        k = kwargs.get("k", 60)
        return ReciprocalRankFusionReranker(k=k)
    else:
        return NoReranker()


# Export classes
__all__ = [
    "Reranker",
    "CrossEncoderReranker",
    "LLMReranker",
    "ReciprocalRankFusionReranker",
    "NoReranker",
    "RerankConfig",
    "RerankResult",
    "get_reranker",
]
