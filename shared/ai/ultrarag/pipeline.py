# ═══════════════════════════════════════════════════════════════════════════════
# UltraRAG Pipeline - Main RAG Orchestration Engine
# محرك خط أنابيب RAG الرئيسي
# ═══════════════════════════════════════════════════════════════════════════════

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import structlog

from .models import (
    GenerationMode,
    GenerationResult,
    RAGPipelineConfig,
    RAGRequest,
    RAGResult,
    RerankingMethod,
    RerankResult,
    RetrievalResult,
    RetrievalStrategy,
)
from .reranker import (
    RerankConfig,
    Reranker,
    get_reranker,
)
from .retriever import (
    AdaptiveRetriever,
    DenseRetriever,
    HybridRetriever,
    KnowledgeGraphRetriever,
    RetrievalConfig,
    Retriever,
    SparseRetriever,
    TriRAGRetriever,
)

logger = structlog.get_logger(__name__)


class RAGStage(Enum):
    """RAG pipeline stages | مراحل خط أنابيب RAG"""

    QUERY_PROCESSING = "query_processing"
    RETRIEVAL = "retrieval"
    RERANKING = "reranking"
    CONTEXT_BUILDING = "context_building"
    GENERATION = "generation"
    POST_PROCESSING = "post_processing"


@dataclass
class StageResult:
    """Result from a pipeline stage | نتيجة مرحلة في خط الأنابيب"""

    stage: RAGStage
    success: bool
    data: Any = None
    error: str | None = None
    processing_time_ms: float = 0.0


@dataclass
class PipelineContext:
    """Context passed through pipeline stages | السياق الممرر عبر المراحل"""

    request: RAGRequest
    query: str
    expanded_queries: list[str] = field(default_factory=list)
    retrieval_results: list[RetrievalResult] = field(default_factory=list)
    rerank_result: RerankResult | None = None
    context_text: str = ""
    generation_result: GenerationResult | None = None
    stage_results: dict[RAGStage, StageResult] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class RAGPipeline:
    """
    Main RAG Pipeline - Orchestrates retrieval, reranking, and generation
    خط أنابيب RAG الرئيسي - ينسق الاسترجاع وإعادة الترتيب والتوليد
    """

    def __init__(
        self,
        config: RAGPipelineConfig,
        retriever: Retriever | None = None,
        reranker: Reranker | None = None,
        generator: Any = None,  # Generator from generator.py
        vector_store: Any = None,
        embedding_service: Any = None,
        llm_client: Any = None,
    ):
        self.config = config
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.llm_client = llm_client

        # Initialize components lazily
        self._retriever = retriever
        self._reranker = reranker
        self._generator = generator

        # Stage hooks for extensibility
        self._pre_hooks: dict[RAGStage, list[Callable]] = {stage: [] for stage in RAGStage}
        self._post_hooks: dict[RAGStage, list[Callable]] = {stage: [] for stage in RAGStage}

        # Metrics
        self._query_count = 0
        self._total_latency_ms = 0.0

        logger.info(
            "rag_pipeline_initialized",
            pipeline_name=config.name,
            strategy=config.retrieval_strategy.value,
            reranking=config.reranking_method.value,
        )

    @property
    def retriever(self) -> Retriever:
        """Get or initialize retriever"""
        if self._retriever is None:
            self._retriever = self._create_retriever()
        return self._retriever

    @property
    def reranker(self) -> Reranker:
        """Get or initialize reranker"""
        if self._reranker is None:
            self._reranker = get_reranker(
                self.config.reranking_method,
                model=self.config.rerank_model,
                llm_client=self.llm_client,
            )
        return self._reranker

    def _create_retriever(self) -> Retriever:
        """Create retriever based on config"""
        if self.vector_store is None or self.embedding_service is None:
            raise ValueError("vector_store and embedding_service required for retriever")

        dense = DenseRetriever(self.vector_store, self.embedding_service)
        sparse = SparseRetriever(self.vector_store)

        if self.config.retrieval_strategy == RetrievalStrategy.DENSE:
            return dense
        elif self.config.retrieval_strategy == RetrievalStrategy.SPARSE:
            return sparse
        elif self.config.retrieval_strategy == RetrievalStrategy.HYBRID:
            return HybridRetriever(dense, sparse)
        elif self.config.retrieval_strategy == RetrievalStrategy.TRI_RAG:
            # AgriGPT-style Tri-RAG with Knowledge Graph
            kg = KnowledgeGraphRetriever(self.embedding_service)
            return TriRAGRetriever(dense, sparse, kg)
        else:  # ADAPTIVE
            hybrid = HybridRetriever(dense, sparse)
            return AdaptiveRetriever(dense, sparse, hybrid)

    async def run(self, request: RAGRequest) -> RAGResult:
        """
        Run the full RAG pipeline
        تشغيل خط أنابيب RAG الكامل
        """
        start_time = time.time()
        self._query_count += 1

        # Initialize context
        ctx = PipelineContext(
            request=request,
            query=request.query,
        )

        try:
            # Stage 1: Query Processing
            ctx = await self._run_stage(RAGStage.QUERY_PROCESSING, ctx, self._process_query)

            # Stage 2: Retrieval
            ctx = await self._run_stage(RAGStage.RETRIEVAL, ctx, self._retrieve)

            # Stage 3: Reranking
            if self.config.reranking_method != RerankingMethod.NONE:
                ctx = await self._run_stage(RAGStage.RERANKING, ctx, self._rerank)

            # Stage 4: Context Building
            ctx = await self._run_stage(RAGStage.CONTEXT_BUILDING, ctx, self._build_context)

            # Stage 5: Generation
            if self._generator is not None:
                ctx = await self._run_stage(RAGStage.GENERATION, ctx, self._generate)

            # Stage 6: Post Processing
            ctx = await self._run_stage(RAGStage.POST_PROCESSING, ctx, self._post_process)

            total_time = (time.time() - start_time) * 1000
            self._total_latency_ms += total_time

            # Build final result
            result = RAGResult(
                request=request,
                retrieval_results=ctx.retrieval_results,
                rerank_result=ctx.rerank_result,
                generation_result=ctx.generation_result,
                total_time_ms=total_time,
                success=True,
            )

            logger.info(
                "rag_pipeline_complete",
                query_preview=request.query[:50],
                results_count=len(ctx.retrieval_results),
                total_time_ms=total_time,
            )

            return result

        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            logger.error("rag_pipeline_error", error=str(e))

            return RAGResult(
                request=request,
                retrieval_results=ctx.retrieval_results,
                rerank_result=ctx.rerank_result,
                generation_result=ctx.generation_result,
                total_time_ms=total_time,
                success=False,
                error=str(e),
            )

    async def _run_stage(
        self,
        stage: RAGStage,
        ctx: PipelineContext,
        handler: Callable,
    ) -> PipelineContext:
        """Run a single pipeline stage with hooks"""
        start_time = time.time()

        try:
            # Run pre-hooks
            for hook in self._pre_hooks[stage]:
                ctx = await hook(ctx)

            # Run main handler
            ctx = await handler(ctx)

            # Run post-hooks
            for hook in self._post_hooks[stage]:
                ctx = await hook(ctx)

            elapsed = (time.time() - start_time) * 1000
            ctx.stage_results[stage] = StageResult(
                stage=stage,
                success=True,
                processing_time_ms=elapsed,
            )

            logger.debug(
                "rag_stage_complete",
                stage=stage.value,
                elapsed_ms=elapsed,
            )

        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            ctx.stage_results[stage] = StageResult(
                stage=stage,
                success=False,
                error=str(e),
                processing_time_ms=elapsed,
            )
            logger.error("rag_stage_error", stage=stage.value, error=str(e))
            raise

        return ctx

    async def _process_query(self, ctx: PipelineContext) -> PipelineContext:
        """Process and optionally expand query | معالجة وتوسيع الاستعلام"""
        query = ctx.request.query

        # Basic query cleaning
        query = query.strip()

        # Query expansion (if enabled)
        if self.config.retrieval_strategy == RetrievalStrategy.ADAPTIVE:
            ctx.expanded_queries = await self._expand_query(query)
        else:
            ctx.expanded_queries = [query]

        ctx.query = query
        return ctx

    async def _expand_query(self, query: str) -> list[str]:
        """Expand query using LLM or rules | توسيع الاستعلام"""
        expansions = [query]

        # If LLM available, generate variations
        if self.llm_client is not None:
            try:
                prompt = f"""Generate 2 alternative phrasings for this query.
Return only the queries, one per line.

Original query: {query}

Alternative queries:"""

                response = await self.llm_client.generate(
                    prompt=prompt,
                    max_tokens=100,
                    temperature=0.3,
                )

                # Parse response
                lines = response.strip().split("\n")
                for line in lines[:2]:
                    line = line.strip()
                    if line and line not in expansions:
                        expansions.append(line)

            except Exception as e:
                logger.warning("query_expansion_error", error=str(e))

        return expansions

    async def _retrieve(self, ctx: PipelineContext) -> PipelineContext:
        """Retrieve relevant documents | استرجاع المستندات ذات الصلة"""
        retrieval_config = RetrievalConfig(
            strategy=self.config.retrieval_strategy,
            top_k=self.config.top_k,
            dense_weight=self.config.dense_weight,
            sparse_weight=self.config.sparse_weight,
            collection=ctx.request.collection,
            filters=ctx.request.filters,
        )

        # Retrieve for main query
        results = await self.retriever.retrieve(ctx.query, retrieval_config)

        # If we have expanded queries, merge results
        if len(ctx.expanded_queries) > 1:
            all_results = list(results)
            seen_ids = {r.chunk.id for r in results}

            for expanded in ctx.expanded_queries[1:]:
                extra_results = await self.retriever.retrieve(expanded, retrieval_config)
                for r in extra_results:
                    if r.chunk.id not in seen_ids:
                        all_results.append(r)
                        seen_ids.add(r.chunk.id)

            # Re-sort by score and limit
            all_results.sort(key=lambda x: x.score, reverse=True)
            results = all_results[: self.config.top_k * 2]  # Get more for reranking

        ctx.retrieval_results = results
        return ctx

    async def _rerank(self, ctx: PipelineContext) -> PipelineContext:
        """Rerank retrieval results | إعادة ترتيب النتائج"""
        rerank_config = RerankConfig(
            method=self.config.reranking_method,
            top_k=self.config.rerank_top_k,
            model=self.config.rerank_model,
        )

        rerank_result = await self.reranker.rerank(
            ctx.query,
            ctx.retrieval_results,
            rerank_config,
        )

        ctx.rerank_result = rerank_result
        ctx.retrieval_results = rerank_result.results
        return ctx

    async def _build_context(self, ctx: PipelineContext) -> PipelineContext:
        """Build context from retrieval results | بناء السياق من النتائج"""
        context_parts = []

        for i, result in enumerate(ctx.retrieval_results[: self.config.rerank_top_k]):
            # Build context entry
            entry = f"[Source {i + 1}] (Score: {result.score:.3f})\n{result.chunk.text}"

            # Add Arabic text if available
            if result.chunk.text_ar:
                entry += f"\n[العربية]: {result.chunk.text_ar}"

            context_parts.append(entry)

        ctx.context_text = "\n\n---\n\n".join(context_parts)
        return ctx

    async def _generate(self, ctx: PipelineContext) -> PipelineContext:
        """Generate response using LLM | توليد الاستجابة باستخدام LLM"""
        if self._generator is None:
            return ctx

        try:
            generation_result = await self._generator.generate(
                query=ctx.query,
                context=ctx.context_text,
                mode=ctx.request.generation_mode,
                language=ctx.request.language,
                max_tokens=ctx.request.max_tokens,
            )

            ctx.generation_result = generation_result

        except Exception as e:
            logger.error("generation_error", error=str(e))
            ctx.generation_result = GenerationResult(
                answer=f"Error generating response: {str(e)}",
                confidence=0.0,
            )

        return ctx

    async def _post_process(self, ctx: PipelineContext) -> PipelineContext:
        """Post-process results | معالجة النتائج النهائية"""
        # Add source metadata to generation result
        if ctx.generation_result:
            ctx.generation_result.sources = ctx.retrieval_results[: self.config.rerank_top_k]

        return ctx

    def add_pre_hook(self, stage: RAGStage, hook: Callable):
        """Add a pre-processing hook to a stage"""
        self._pre_hooks[stage].append(hook)

    def add_post_hook(self, stage: RAGStage, hook: Callable):
        """Add a post-processing hook to a stage"""
        self._post_hooks[stage].append(hook)

    def get_metrics(self) -> dict[str, Any]:
        """Get pipeline metrics | الحصول على مقاييس خط الأنابيب"""
        avg_latency = self._total_latency_ms / self._query_count if self._query_count > 0 else 0.0
        return {
            "query_count": self._query_count,
            "total_latency_ms": self._total_latency_ms,
            "average_latency_ms": avg_latency,
            "config": self.config.to_dict(),
        }


class RAGPipelineBuilder:
    """Builder for RAG pipeline configuration | منشئ تكوين خط الأنابيب"""

    def __init__(self, name: str = "default"):
        self._config = RAGPipelineConfig(name=name)
        self._vector_store = None
        self._embedding_service = None
        self._llm_client = None
        self._generator = None

    def with_retrieval_strategy(self, strategy: RetrievalStrategy) -> "RAGPipelineBuilder":
        self._config.retrieval_strategy = strategy
        return self

    def with_reranking(self, method: RerankingMethod, model: str = None) -> "RAGPipelineBuilder":
        self._config.reranking_method = method
        if model:
            self._config.rerank_model = model
        return self

    def with_generation_mode(self, mode: GenerationMode) -> "RAGPipelineBuilder":
        self._config.generation_mode = mode
        return self

    def with_top_k(self, retrieval_k: int, rerank_k: int = None) -> "RAGPipelineBuilder":
        self._config.top_k = retrieval_k
        if rerank_k:
            self._config.rerank_top_k = rerank_k
        return self

    def with_chunking(self, size: int, overlap: int) -> "RAGPipelineBuilder":
        self._config.chunk_size = size
        self._config.chunk_overlap = overlap
        return self

    def with_llm(self, model: str, provider: str = "ollama") -> "RAGPipelineBuilder":
        self._config.llm_model = model
        self._config.llm_provider = provider
        return self

    def with_embedding(self, model: str, provider: str = "sentence_transformers") -> "RAGPipelineBuilder":
        self._config.embedding_model = model
        self._config.embedding_provider = provider
        return self

    def with_arabic_support(self, enabled: bool = True, model: str = None) -> "RAGPipelineBuilder":
        self._config.arabic_enabled = enabled
        if model:
            self._config.arabic_embedding_model = model
        return self

    def with_vector_store(self, vector_store: Any) -> "RAGPipelineBuilder":
        self._vector_store = vector_store
        return self

    def with_embedding_service(self, embedding_service: Any) -> "RAGPipelineBuilder":
        self._embedding_service = embedding_service
        return self

    def with_llm_client(self, llm_client: Any) -> "RAGPipelineBuilder":
        self._llm_client = llm_client
        return self

    def with_generator(self, generator: Any) -> "RAGPipelineBuilder":
        self._generator = generator
        return self

    def build(self) -> RAGPipeline:
        """Build the RAG pipeline"""
        return RAGPipeline(
            config=self._config,
            vector_store=self._vector_store,
            embedding_service=self._embedding_service,
            llm_client=self._llm_client,
            generator=self._generator,
        )


# Export classes
__all__ = [
    "RAGPipeline",
    "RAGPipelineBuilder",
    "RAGStage",
    "StageResult",
    "PipelineContext",
]
