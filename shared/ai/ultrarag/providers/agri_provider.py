# ═══════════════════════════════════════════════════════════════════════════════
# AgriRAGProvider - Agricultural Agents Integration
# مزود RAG الزراعي - تكامل الوكلاء الزراعيين
#
# Integrates UltraRAG with Tri-RAG for agricultural advisory agents:
# - disease-expert-agent: Crop disease diagnosis
# - irrigation-advisor-agent: Smart irrigation recommendations
# - fertilizer-advisor-agent: Fertilizer recommendations
# - yield-predictor-agent: Yield prediction
# ═══════════════════════════════════════════════════════════════════════════════

from dataclasses import dataclass, field
from typing import Any

import structlog

from ..mcp_tools import RAGMCPTools
from ..models import (
    EntityType,
    RelationType,
    RetrievalStrategy,
    TriRAGConfig,
)
from ..retriever import (
    DenseRetriever,
    KnowledgeGraphRetriever,
    RetrievalConfig,
    SparseRetriever,
    TriRAGRetriever,
)

# Knowledge base integration
from ...knowledge.collections import (
    DIGITAL_TWIN_KNOWLEDGE,
    FERTILIZER_KNOWLEDGE,
    GENERAL_AGRICULTURE,
    PRECISION_FARMING_KNOWLEDGE,
    REMOTE_SENSING_KNOWLEDGE,
    SOIL_KNOWLEDGE,
    WEATHER_KNOWLEDGE,
)
from ...knowledge.corrective_retrieval import CorrectiveRetrievalEngine
from ...knowledge.graph_builder import build_agricultural_knowledge_graph
from ...knowledge.verification.region_filter import CLIMATE_ZONES

logger = structlog.get_logger(__name__)


@dataclass
class AgriQueryContext:
    """Agricultural query context | سياق الاستعلام الزراعي"""

    crop_type: str | None = None
    growth_stage: str | None = None
    region: str | None = None
    climate_zone: str | None = None
    soil_type: str | None = None
    weather: dict[str, Any] | None = None
    field_id: str | None = None
    tenant_id: str | None = None
    language: str = "both"  # en, ar, both


@dataclass
class AgriAdvisoryResult:
    """Agricultural advisory result | نتيجة الاستشارة الزراعية"""

    query: str
    advisory: str
    advisory_ar: str | None = None
    confidence: float = 0.0
    sources: list[dict[str, Any]] = field(default_factory=list)
    related_entities: list[dict[str, Any]] = field(default_factory=list)
    treatment_options: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class AgriRAGProvider:
    """
    Agricultural RAG Provider for SAHOOL AI Agents
    مزود RAG الزراعي لوكلاء سهول الذكية

    Provides Tri-RAG capabilities to agricultural advisory agents
    using Knowledge Graph for crop-disease-treatment relationships.
    """

    def __init__(
        self,
        config: TriRAGConfig | None = None,
        embedding_service: Any | None = None,
        vector_store: Any | None = None,
    ):
        self.config = config or TriRAGConfig()
        self.embedding_service = embedding_service
        self.vector_store = vector_store

        # Initialize retrievers
        self._kg_retriever = KnowledgeGraphRetriever(embedding_service)
        self._dense_retriever: DenseRetriever | None = None
        self._sparse_retriever: SparseRetriever | None = None
        self._tri_rag: TriRAGRetriever | None = None

        # CRAG engine for corrective retrieval
        self._crag_engine = CorrectiveRetrievalEngine(
            correct_threshold=0.7,
            ambiguous_threshold=0.4,
            max_refined_chunks=10,
        )

        # Initialize knowledge graph with agricultural entities
        self._initialized = False

    async def initialize(self):
        """Initialize the provider with agricultural knowledge"""
        if self._initialized:
            return

        # Initialize dense/sparse retrievers if services available
        if self.vector_store and self.embedding_service:
            self._dense_retriever = DenseRetriever(self.vector_store, self.embedding_service)
            self._sparse_retriever = SparseRetriever(self.vector_store)
        else:
            # Use mock for testing
            self._dense_retriever = _MockRetriever()
            self._sparse_retriever = _MockRetriever()

        # Create Tri-RAG retriever
        self._tri_rag = TriRAGRetriever(
            dense_retriever=self._dense_retriever,
            sparse_retriever=self._sparse_retriever,
            kg_retriever=self._kg_retriever,
            config=self.config,
        )

        # Load agricultural knowledge graph
        await self._load_agricultural_knowledge()

        self._initialized = True
        logger.info("agri_rag_provider_initialized")

    async def _load_agricultural_knowledge(self):
        """Load agricultural knowledge from the shared graph builder.
        تحميل المعرفة الزراعية من منشئ الرسم البياني المشترك

        Uses shared/ai/knowledge/graph_builder.py as single source of truth,
        eliminating duplication across services.
        """
        kg = build_agricultural_knowledge_graph()

        # Map entity types to UltraRAG EntityType enum
        _type_map = {
            "crop": EntityType.CROP.value,
            "disease": EntityType.DISEASE.value,
            "pest": EntityType.PEST.value,
            "treatment": EntityType.PESTICIDE.value,
            "fertilizer": EntityType.FERTILIZER.value,
            "irrigation": EntityType.IRRIGATION.value,
        }

        # Add all entities
        for entity in kg.entities:
            await self._kg_retriever.add_entity(
                {
                    "id": entity.id,
                    "name": entity.name,
                    "name_ar": entity.name_ar,
                    "entity_type": _type_map.get(entity.entity_type, entity.entity_type),
                    "properties": entity.properties,
                }
            )

        # Map relation types
        _rel_map = {
            "affects": RelationType.AFFECTS.value,
            "treats": RelationType.TREATS.value,
            "compatible_with": RelationType.COMPATIBLE_WITH.value,
        }

        # Add all relations
        for relation in kg.relations:
            await self._kg_retriever.add_relation(
                {
                    "source_id": relation.source_id,
                    "target_id": relation.target_id,
                    "relation_type": _rel_map.get(relation.relation_type, relation.relation_type),
                }
            )

        logger.info(
            "agricultural_knowledge_loaded",
            entities=len(kg.entities),
            relations=len(kg.relations),
            source="shared_graph_builder",
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # Agent Integration Methods
    # ═══════════════════════════════════════════════════════════════════════════

    async def diagnose_disease(
        self,
        symptoms: str,
        crop_type: str | None = None,
        context: AgriQueryContext | None = None,
    ) -> AgriAdvisoryResult:
        """
        Diagnose crop disease using Tri-RAG
        تشخيص أمراض المحاصيل باستخدام Tri-RAG

        For: disease-expert-agent
        """
        await self.initialize()

        # Build query
        query = f"Diagnose disease: {symptoms}"
        if crop_type:
            query += f" in {crop_type}"

        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=10,
            filters={"kg_max_hops": 2},
        )

        results = await self._tri_rag.retrieve(query, config)

        # Extract disease entities from results
        diseases = []
        treatments = []
        for r in results:
            if r.chunk.metadata.get("entity_type") == EntityType.DISEASE.value:
                diseases.append(
                    {
                        "name": r.chunk.text,
                        "name_ar": r.chunk.text_ar,
                        "confidence": r.score,
                    }
                )
            elif r.chunk.metadata.get("entity_type") == EntityType.PESTICIDE.value:
                treatments.append(
                    {
                        "name": r.chunk.text,
                        "name_ar": r.chunk.text_ar,
                    }
                )

        return AgriAdvisoryResult(
            query=query,
            advisory=f"Based on symptoms '{symptoms}', possible diseases identified.",
            advisory_ar=f"بناءً على الأعراض '{symptoms}'، تم تحديد الأمراض المحتملة.",
            confidence=results[0].score if results else 0.0,
            sources=[r.to_dict() for r in results[:5]],
            related_entities=diseases,
            treatment_options=treatments,
            metadata={"crop_type": crop_type, "symptoms": symptoms},
        )

    async def recommend_irrigation(
        self,
        crop_type: str,
        growth_stage: str,
        soil_moisture: float | None = None,
        weather_forecast: dict[str, Any] | None = None,
        context: AgriQueryContext | None = None,
    ) -> AgriAdvisoryResult:
        """
        Recommend irrigation schedule using Tri-RAG
        توصية جدول الري باستخدام Tri-RAG

        For: irrigation-advisor-agent
        """
        await self.initialize()

        query = f"Irrigation recommendation for {crop_type} at {growth_stage} stage"
        if soil_moisture is not None:
            query += f", soil moisture {soil_moisture}%"

        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=10,
            filters={"kg_max_hops": 2},
        )

        results = await self._tri_rag.retrieve(query, config)

        # Extract irrigation methods
        irrigation_methods = []
        for r in results:
            if r.chunk.metadata.get("entity_type") == EntityType.IRRIGATION.value:
                irrigation_methods.append(
                    {
                        "name": r.chunk.text,
                        "name_ar": r.chunk.text_ar,
                        "score": r.score,
                    }
                )

        return AgriAdvisoryResult(
            query=query,
            advisory=f"Irrigation recommendation for {crop_type} at {growth_stage}.",
            advisory_ar=f"توصية الري لـ {crop_type} في مرحلة {growth_stage}.",
            confidence=results[0].score if results else 0.0,
            sources=[r.to_dict() for r in results[:5]],
            related_entities=irrigation_methods,
            metadata={
                "crop_type": crop_type,
                "growth_stage": growth_stage,
                "soil_moisture": soil_moisture,
            },
        )

    async def recommend_fertilizer(
        self,
        crop_type: str,
        growth_stage: str,
        soil_analysis: dict[str, Any] | None = None,
        target_yield: float | None = None,
        context: AgriQueryContext | None = None,
    ) -> AgriAdvisoryResult:
        """
        Recommend fertilizer application using Tri-RAG
        توصية تطبيق الأسمدة باستخدام Tri-RAG

        For: fertilizer-advisor-agent
        """
        await self.initialize()

        query = f"Fertilizer recommendation for {crop_type} at {growth_stage}"
        if soil_analysis:
            query += f", soil N={soil_analysis.get('nitrogen', 'unknown')} ppm"

        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=10,
            filters={"kg_max_hops": 2},
        )

        results = await self._tri_rag.retrieve(query, config)

        # Extract fertilizer options
        fertilizers = []
        for r in results:
            if r.chunk.metadata.get("entity_type") == EntityType.FERTILIZER.value:
                fertilizers.append(
                    {
                        "name": r.chunk.text,
                        "name_ar": r.chunk.text_ar,
                        "score": r.score,
                    }
                )

        return AgriAdvisoryResult(
            query=query,
            advisory=f"Fertilizer recommendation for {crop_type}.",
            advisory_ar=f"توصية السماد لـ {crop_type}.",
            confidence=results[0].score if results else 0.0,
            sources=[r.to_dict() for r in results[:5]],
            treatment_options=fertilizers,
            metadata={
                "crop_type": crop_type,
                "growth_stage": growth_stage,
                "soil_analysis": soil_analysis,
                "target_yield": target_yield,
            },
        )

    async def predict_yield(
        self,
        crop_type: str,
        area_hectares: float,
        growth_stage: str | None = None,
        field_data: dict[str, Any] | None = None,
        context: AgriQueryContext | None = None,
    ) -> AgriAdvisoryResult:
        """
        Predict yield using Tri-RAG knowledge
        توقع الإنتاج باستخدام معرفة Tri-RAG

        For: yield-predictor-agent
        """
        await self.initialize()

        query = f"Yield prediction for {crop_type} on {area_hectares} hectares"
        if growth_stage:
            query += f" at {growth_stage} stage"

        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=10,
            filters={"kg_max_hops": 2},
        )

        results = await self._tri_rag.retrieve(query, config)

        return AgriAdvisoryResult(
            query=query,
            advisory=f"Yield prediction analysis for {crop_type}.",
            advisory_ar=f"تحليل توقع الإنتاج لـ {crop_type}.",
            confidence=results[0].score if results else 0.0,
            sources=[r.to_dict() for r in results[:5]],
            metadata={
                "crop_type": crop_type,
                "area_hectares": area_hectares,
                "growth_stage": growth_stage,
            },
        )

    async def general_query(
        self,
        query: str,
        context: AgriQueryContext | None = None,
    ) -> AgriAdvisoryResult:
        """
        General agricultural query using Tri-RAG
        استعلام زراعي عام باستخدام Tri-RAG
        """
        await self.initialize()

        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=10,
            filters={"kg_max_hops": 2},
        )

        results = await self._tri_rag.retrieve(query, config)

        return AgriAdvisoryResult(
            query=query,
            advisory=f"Results for query: {query}",
            advisory_ar=f"نتائج الاستعلام: {query}",
            confidence=results[0].score if results else 0.0,
            sources=[r.to_dict() for r in results[:5]],
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # Extended Domain Queries (New Collections)
    # استعلامات المجالات الموسعة (مجموعات جديدة)
    # ═══════════════════════════════════════════════════════════════════════════

    async def query_soil_knowledge(
        self,
        query: str,
        context: AgriQueryContext | None = None,
    ) -> AgriAdvisoryResult:
        """Query soil knowledge collection | استعلام قاعدة معرفة التربة"""
        await self.initialize()
        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=8,
            collection=SOIL_KNOWLEDGE,
            filters={"kg_max_hops": 2},
        )
        results = await self._tri_rag.retrieve(query, config)
        results = self._apply_region_filter(results, context)
        results = self._apply_crag(results, query, GENERAL_AGRICULTURE)
        return self._build_result(query, results, "soil")

    async def query_fertilizer_knowledge(
        self,
        query: str,
        context: AgriQueryContext | None = None,
    ) -> AgriAdvisoryResult:
        """Query fertilizer knowledge collection | استعلام قاعدة معرفة التسميد"""
        await self.initialize()
        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=8,
            collection=FERTILIZER_KNOWLEDGE,
            filters={"kg_max_hops": 2},
        )
        results = await self._tri_rag.retrieve(query, config)
        results = self._apply_region_filter(results, context)
        results = self._apply_crag(results, query, GENERAL_AGRICULTURE)
        return self._build_result(query, results, "fertilizer")

    async def query_weather_knowledge(
        self,
        query: str,
        context: AgriQueryContext | None = None,
    ) -> AgriAdvisoryResult:
        """Query weather knowledge collection | استعلام قاعدة معرفة الطقس"""
        await self.initialize()
        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=8,
            collection=WEATHER_KNOWLEDGE,
            filters={"kg_max_hops": 2},
        )
        results = await self._tri_rag.retrieve(query, config)
        results = self._apply_region_filter(results, context)
        results = self._apply_crag(results, query, GENERAL_AGRICULTURE)
        return self._build_result(query, results, "weather")

    async def query_remote_sensing(
        self,
        query: str,
        context: AgriQueryContext | None = None,
    ) -> AgriAdvisoryResult:
        """Query remote sensing knowledge | استعلام قاعدة معرفة الاستشعار عن بعد"""
        await self.initialize()
        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=8,
            collection=REMOTE_SENSING_KNOWLEDGE,
            filters={"kg_max_hops": 1},
        )
        results = await self._tri_rag.retrieve(query, config)
        results = self._apply_crag(results, query, GENERAL_AGRICULTURE)
        return self._build_result(query, results, "remote_sensing")

    async def query_precision_farming_knowledge(
        self,
        query: str,
        context: AgriQueryContext | None = None,
    ) -> AgriAdvisoryResult:
        """Query precision farming knowledge | استعلام قاعدة معرفة الزراعة الدقيقة

        Covers VRA, GPS/GNSS guidance, yield mapping, site-specific management.
        يغطي: معدل متغير، توجيه GPS، خرائط إنتاجية، إدارة موقعية.
        """
        await self.initialize()
        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=8,
            collection=PRECISION_FARMING_KNOWLEDGE,
            filters={"kg_max_hops": 2},
        )
        results = await self._tri_rag.retrieve(query, config)
        results = self._apply_region_filter(results, context)
        results = self._apply_crag(results, query, GENERAL_AGRICULTURE)
        return self._build_result(query, results, "precision_farming")

    async def query_digital_twin_knowledge(
        self,
        query: str,
        context: AgriQueryContext | None = None,
    ) -> AgriAdvisoryResult:
        """Query digital twin knowledge | استعلام قاعدة معرفة التوأم الرقمي

        Covers farm simulation, crop models, irrigation optimization, cyber-physical systems.
        يغطي: محاكاة المزرعة، نماذج المحاصيل، تحسين الري، أنظمة سيبرانية-مادية.
        """
        await self.initialize()
        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=8,
            collection=DIGITAL_TWIN_KNOWLEDGE,
            filters={"kg_max_hops": 2},
        )
        results = await self._tri_rag.retrieve(query, config)
        results = self._apply_region_filter(results, context)
        results = self._apply_crag(results, query, GENERAL_AGRICULTURE)
        return self._build_result(query, results, "digital_twin")

    # ═══════════════════════════════════════════════════════════════════════════
    # Region Filter & CRAG (Corrective RAG)
    # فلتر إقليمي و RAG تصحيحي
    # ═══════════════════════════════════════════════════════════════════════════

    # Quality threshold for CRAG - below this triggers broadened search
    CRAG_QUALITY_THRESHOLD = 0.4

    def _apply_region_filter(self, results: list, context: AgriQueryContext | None) -> list:
        """Apply AgriRegion-style spatial-semantic scoring.
        تطبيق تسجيل مكاني-دلالي على نمط AgriRegion

        - Local knowledge = highest score (1.0x)
        - Similar ecoregions = reduced (0.7x)
        - Dissimilar regions = heavily reduced (0.3x)
        """
        if not context or not context.climate_zone:
            return results

        target_zone = context.climate_zone
        zone_info = CLIMATE_ZONES.get(target_zone)
        if not zone_info:
            return results

        similar_zones = set(zone_info.get("similar_zones", []))
        similar_zones.add(target_zone)

        scored_results = []
        for r in results:
            region_meta = r.chunk.metadata.get("region_relevance", {})
            doc_regions = region_meta.get("applicable_regions", [])

            if not doc_regions:
                # No region info → general content, keep at moderate score
                scored_results.append(r)
            elif target_zone in doc_regions:
                # Direct match → boost
                r.score = min(r.score * 1.2, 1.0)
                scored_results.append(r)
            elif any(z in similar_zones for z in doc_regions):
                # Similar ecoregion → keep but reduce
                r.score *= 0.7
                scored_results.append(r)
            else:
                # Dissimilar region → heavily reduce but don't remove
                r.score *= 0.3
                scored_results.append(r)

        # Re-sort by score
        scored_results.sort(key=lambda x: x.score, reverse=True)
        return scored_results

    def _apply_crag(self, results: list, query: str, fallback_collection: str) -> list:
        """Apply Corrective RAG (CRAG) pattern using CorrectiveRetrievalEngine.
        تطبيق نمط RAG التصحيحي باستخدام محرك الاسترجاع التصحيحي

        Evaluates retrieval quality and refines chunks:
        - CORRECT (>=0.7): Light refinement, keep most content
        - AMBIGUOUS (0.4-0.7): Deep sentence-level refinement
        - INCORRECT (<0.4): Salvage usable content, suggest fallback
        """
        if not results:
            return results

        # Convert retrieval results to chunk dicts for CRAG engine
        chunks = []
        for r in results:
            chunk_dict = {
                "content": r.chunk.text if hasattr(r, "chunk") else "",
                "content_ar": r.chunk.text_ar if hasattr(r, "chunk") and hasattr(r.chunk, "text_ar") else "",
                "metadata": r.chunk.metadata if hasattr(r, "chunk") else {},
            }
            if hasattr(r, "score"):
                chunk_dict["metadata"]["retrieval_score"] = r.score
            chunks.append(chunk_dict)

        # Detect query domain from fallback collection name
        domain_map = {
            SOIL_KNOWLEDGE: "soil",
            FERTILIZER_KNOWLEDGE: "fertilizer",
            WEATHER_KNOWLEDGE: "weather",
            REMOTE_SENSING_KNOWLEDGE: "remote_sensing",
            PRECISION_FARMING_KNOWLEDGE: "precision_farming",
            DIGITAL_TWIN_KNOWLEDGE: "digital_twin",
            GENERAL_AGRICULTURE: "general",
        }
        query_domain = domain_map.get(fallback_collection, "")

        # Run CRAG evaluation and refinement
        crag_result = self._crag_engine.evaluate_and_refine(
            query=query,
            retrieved_chunks=chunks,
            query_domain=query_domain,
        )

        logger.info(
            "crag_applied",
            action=crag_result.action_taken.value,
            confidence=crag_result.evaluation.confidence.value,
            score=round(crag_result.evaluation.overall_score, 3),
            chunks_in=crag_result.total_chunks_input,
            chunks_out=crag_result.total_chunks_output,
            fallback_needed=crag_result.fallback_used,
            fallback_collection=fallback_collection if crag_result.fallback_used else None,
            query=query[:100],
        )

        # If CRAG refined the chunks, update scores on the original results
        if crag_result.refined_chunks:
            # Build a content-to-score map from refined chunks
            refined_scores = {}
            for rc in crag_result.refined_chunks:
                refined_scores[rc.content[:100]] = rc.relevance_score

            # Re-score original results based on CRAG refinement
            for r in results:
                content_key = (r.chunk.text if hasattr(r, "chunk") else "")[:100]
                if content_key in refined_scores:
                    # Blend original score with CRAG relevance
                    r.score = 0.6 * r.score + 0.4 * refined_scores[content_key]

            # Re-sort by blended score
            results.sort(key=lambda x: x.score, reverse=True)

        return results

    def _build_result(self, query: str, results: list, domain: str) -> AgriAdvisoryResult:
        """Build a standard advisory result from retrieval results."""
        return AgriAdvisoryResult(
            query=query,
            advisory=f"Results for {domain} query: {query}",
            advisory_ar=f"نتائج استعلام {domain}: {query}",
            confidence=results[0].score if results else 0.0,
            sources=[r.to_dict() for r in results[:5]],
            metadata={"domain": domain},
        )

    def get_mcp_tools(self) -> RAGMCPTools:
        """Get MCP tools for this provider"""
        return RAGMCPTools(
            rag_pipeline=None,  # Will use direct methods
            knowledge_base=None,
        )

    @property
    def knowledge_graph(self) -> KnowledgeGraphRetriever:
        """Access the knowledge graph retriever"""
        return self._kg_retriever


class _MockRetriever:
    """Mock retriever for testing without vector store"""

    async def retrieve(self, query: str, config: RetrievalConfig) -> list:
        return []

    async def add_documents(self, chunks: list, collection: str = "default") -> bool:
        return True


# Export
__all__ = [
    "AgriRAGProvider",
    "AgriQueryContext",
    "AgriAdvisoryResult",
]
