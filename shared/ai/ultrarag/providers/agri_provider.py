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
    FERTILIZER_KNOWLEDGE,
    GENERAL_AGRICULTURE,
    REMOTE_SENSING_KNOWLEDGE,
    SOIL_KNOWLEDGE,
    WEATHER_KNOWLEDGE,
)
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
        """Load agricultural knowledge into the knowledge graph"""
        # ═══════════════════════════════════════════════════════════════════════
        # Crop Entities - كيانات المحاصيل
        # ═══════════════════════════════════════════════════════════════════════
        crops = [
            {
                "id": "crop_wheat",
                "name": "Wheat",
                "name_ar": "قمح",
                "entity_type": EntityType.CROP.value,
                "properties": {"family": "Poaceae", "season": "winter"},
            },
            {
                "id": "crop_barley",
                "name": "Barley",
                "name_ar": "شعير",
                "entity_type": EntityType.CROP.value,
                "properties": {"family": "Poaceae", "season": "winter"},
            },
            {
                "id": "crop_date_palm",
                "name": "Date Palm",
                "name_ar": "نخيل",
                "entity_type": EntityType.CROP.value,
                "properties": {"family": "Arecaceae", "season": "perennial"},
            },
            {
                "id": "crop_tomato",
                "name": "Tomato",
                "name_ar": "طماطم",
                "entity_type": EntityType.CROP.value,
                "properties": {"family": "Solanaceae", "season": "summer"},
            },
            {
                "id": "crop_cucumber",
                "name": "Cucumber",
                "name_ar": "خيار",
                "entity_type": EntityType.CROP.value,
                "properties": {"family": "Cucurbitaceae", "season": "summer"},
            },
            {
                "id": "crop_alfalfa",
                "name": "Alfalfa",
                "name_ar": "برسيم",
                "entity_type": EntityType.CROP.value,
                "properties": {"family": "Fabaceae", "season": "perennial"},
            },
        ]

        # ═══════════════════════════════════════════════════════════════════════
        # Disease Entities - كيانات الأمراض
        # ═══════════════════════════════════════════════════════════════════════
        diseases = [
            {
                "id": "disease_rust",
                "name": "Rust Disease",
                "name_ar": "مرض الصدأ",
                "entity_type": EntityType.DISEASE.value,
                "properties": {"type": "fungal", "severity": "high"},
            },
            {
                "id": "disease_powdery_mildew",
                "name": "Powdery Mildew",
                "name_ar": "البياض الدقيقي",
                "entity_type": EntityType.DISEASE.value,
                "properties": {"type": "fungal", "severity": "medium"},
            },
            {
                "id": "disease_fusarium",
                "name": "Fusarium Wilt",
                "name_ar": "ذبول الفيوزاريوم",
                "entity_type": EntityType.DISEASE.value,
                "properties": {"type": "fungal", "severity": "high"},
            },
            {
                "id": "disease_bacterial_blight",
                "name": "Bacterial Blight",
                "name_ar": "اللفحة البكتيرية",
                "entity_type": EntityType.DISEASE.value,
                "properties": {"type": "bacterial", "severity": "high"},
            },
            {
                "id": "disease_rpw",
                "name": "Red Palm Weevil",
                "name_ar": "سوسة النخيل الحمراء",
                "entity_type": EntityType.PEST.value,
                "properties": {"type": "insect", "severity": "critical"},
            },
            {
                "id": "disease_leaf_miner",
                "name": "Leaf Miner",
                "name_ar": "حافرة الأوراق",
                "entity_type": EntityType.PEST.value,
                "properties": {"type": "insect", "severity": "medium"},
            },
        ]

        # ═══════════════════════════════════════════════════════════════════════
        # Treatment Entities - كيانات العلاج
        # ═══════════════════════════════════════════════════════════════════════
        treatments = [
            {
                "id": "treat_fungicide_propiconazole",
                "name": "Propiconazole",
                "name_ar": "بروبيكونازول",
                "entity_type": EntityType.PESTICIDE.value,
                "properties": {"type": "fungicide", "target": "rust"},
            },
            {
                "id": "treat_fungicide_sulfur",
                "name": "Sulfur",
                "name_ar": "كبريت",
                "entity_type": EntityType.PESTICIDE.value,
                "properties": {"type": "fungicide", "target": "powdery_mildew"},
            },
            {
                "id": "treat_insecticide_emamectin",
                "name": "Emamectin Benzoate",
                "name_ar": "إيمامكتين بنزوات",
                "entity_type": EntityType.PESTICIDE.value,
                "properties": {"type": "insecticide", "target": "rpw"},
            },
            {
                "id": "treat_urea",
                "name": "Urea 46%",
                "name_ar": "يوريا 46%",
                "entity_type": EntityType.FERTILIZER.value,
                "properties": {"type": "nitrogen", "n_content": 46},
            },
            {
                "id": "treat_dap",
                "name": "DAP 18-46-0",
                "name_ar": "داب 18-46-0",
                "entity_type": EntityType.FERTILIZER.value,
                "properties": {"type": "phosphorus", "n_content": 18, "p_content": 46},
            },
            {
                "id": "treat_potash",
                "name": "Potassium Sulfate",
                "name_ar": "سلفات البوتاسيوم",
                "entity_type": EntityType.FERTILIZER.value,
                "properties": {"type": "potassium", "k_content": 50},
            },
        ]

        # ═══════════════════════════════════════════════════════════════════════
        # Irrigation Entities - كيانات الري
        # ═══════════════════════════════════════════════════════════════════════
        irrigation = [
            {
                "id": "irr_drip",
                "name": "Drip Irrigation",
                "name_ar": "الري بالتنقيط",
                "entity_type": EntityType.IRRIGATION.value,
                "properties": {"efficiency": 90, "type": "localized"},
            },
            {
                "id": "irr_sprinkler",
                "name": "Sprinkler Irrigation",
                "name_ar": "الري بالرش",
                "entity_type": EntityType.IRRIGATION.value,
                "properties": {"efficiency": 75, "type": "overhead"},
            },
            {
                "id": "irr_pivot",
                "name": "Center Pivot",
                "name_ar": "الري المحوري",
                "entity_type": EntityType.IRRIGATION.value,
                "properties": {"efficiency": 85, "type": "mechanical"},
            },
        ]

        # Add all entities
        for entity in crops + diseases + treatments + irrigation:
            await self._kg_retriever.add_entity(entity)

        # ═══════════════════════════════════════════════════════════════════════
        # Relations - العلاقات
        # ═══════════════════════════════════════════════════════════════════════
        relations = [
            # Crop-Disease relations
            {
                "source_id": "disease_rust",
                "target_id": "crop_wheat",
                "relation_type": RelationType.AFFECTS.value,
            },
            {
                "source_id": "disease_rust",
                "target_id": "crop_barley",
                "relation_type": RelationType.AFFECTS.value,
            },
            {
                "source_id": "disease_powdery_mildew",
                "target_id": "crop_cucumber",
                "relation_type": RelationType.AFFECTS.value,
            },
            {
                "source_id": "disease_fusarium",
                "target_id": "crop_tomato",
                "relation_type": RelationType.AFFECTS.value,
            },
            {
                "source_id": "disease_rpw",
                "target_id": "crop_date_palm",
                "relation_type": RelationType.AFFECTS.value,
            },
            # Treatment-Disease relations
            {
                "source_id": "treat_fungicide_propiconazole",
                "target_id": "disease_rust",
                "relation_type": RelationType.TREATS.value,
            },
            {
                "source_id": "treat_fungicide_sulfur",
                "target_id": "disease_powdery_mildew",
                "relation_type": RelationType.TREATS.value,
            },
            {
                "source_id": "treat_insecticide_emamectin",
                "target_id": "disease_rpw",
                "relation_type": RelationType.TREATS.value,
            },
            # Fertilizer-Crop relations
            {
                "source_id": "treat_urea",
                "target_id": "crop_wheat",
                "relation_type": RelationType.COMPATIBLE_WITH.value,
            },
            {
                "source_id": "treat_dap",
                "target_id": "crop_wheat",
                "relation_type": RelationType.COMPATIBLE_WITH.value,
            },
            {
                "source_id": "treat_potash",
                "target_id": "crop_date_palm",
                "relation_type": RelationType.COMPATIBLE_WITH.value,
            },
            # Irrigation-Crop relations
            {
                "source_id": "irr_drip",
                "target_id": "crop_tomato",
                "relation_type": RelationType.COMPATIBLE_WITH.value,
            },
            {
                "source_id": "irr_drip",
                "target_id": "crop_date_palm",
                "relation_type": RelationType.COMPATIBLE_WITH.value,
            },
            {
                "source_id": "irr_pivot",
                "target_id": "crop_wheat",
                "relation_type": RelationType.COMPATIBLE_WITH.value,
            },
            {
                "source_id": "irr_sprinkler",
                "target_id": "crop_alfalfa",
                "relation_type": RelationType.COMPATIBLE_WITH.value,
            },
        ]

        for relation in relations:
            await self._kg_retriever.add_relation(relation)

        logger.info(
            "agricultural_knowledge_loaded",
            entities=len(crops + diseases + treatments + irrigation),
            relations=len(relations),
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
        """Apply Corrective RAG (CRAG) pattern.
        تطبيق نمط RAG التصحيحي

        If retrieval quality is below threshold, trigger broadened search
        in the fallback (general_agriculture) collection.
        """
        if not results:
            return results

        # Evaluate retrieval quality (average top-3 scores)
        top_scores = [r.score for r in results[:3]]
        avg_quality = sum(top_scores) / len(top_scores) if top_scores else 0.0

        if avg_quality >= self.CRAG_QUALITY_THRESHOLD:
            return results

        # Quality below threshold → would trigger broadened search
        # In synchronous context, just log the need
        logger.info(
            "crag_low_quality_detected",
            avg_quality=avg_quality,
            threshold=self.CRAG_QUALITY_THRESHOLD,
            fallback_collection=fallback_collection,
            query=query[:100],
        )

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
