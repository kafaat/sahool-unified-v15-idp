"""
Knowledge Service Bridge - Connecting Knowledge Base and UltraRAG to Production Services
جسر خدمة المعرفة - ربط قاعدة المعرفة ونظام UltraRAG بالخدمات الإنتاجية

Provides a unified interface for microservices to query the agricultural
knowledge base using UltraRAG workflows. Supports offline-first architecture
by falling back to local knowledge collections when vector DB is unavailable.

يوفر واجهة موحدة للخدمات المصغرة للاستعلام من قاعدة المعرفة الزراعية
باستخدام سير عمل UltraRAG. يدعم بنية الأوفلاين أولاً من خلال الرجوع
إلى مجموعات المعرفة المحلية عندما تكون قاعدة البيانات المتجهية غير متاحة.

Gap Coverage:
- G-04: Knowledge Base → Production services bridge
- G-09: UltraRAG → Production services integration

Author: SAHOOL Platform Team
Updated: March 2026
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

# ── Knowledge Base imports (local, always available) ─────────────────────────
from .knowledge.collections import (
    CROP_KNOWLEDGE,
    CROP_WATER_REQUIREMENTS,
    FERTILIZER_KNOWLEDGE,
    GENERAL_AGRICULTURE,
    IRRIGATION_PRACTICES,
    PEST_KNOWLEDGE,
    SOIL_KNOWLEDGE,
    WEATHER_KNOWLEDGE,
)

logger = logging.getLogger(__name__)

# Try structured logging first
try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    pass

# ── Optional imports for full-featured mode ──────────────────────────────────
_KNOWLEDGE_MODELS_AVAILABLE = False

try:
    from .ultrarag import (
        RAGRequest,
        WorkflowEngine,
        load_workflow_from_yaml,
        load_workflows_from_directory,
    )

    _ULTRARAG_AVAILABLE = True
except ImportError:
    _ULTRARAG_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════════
# Data Models
# ═══════════════════════════════════════════════════════════════════════════════


class QueryDomain(StrEnum):
    """Agricultural knowledge domains for queries | مجالات المعرفة الزراعية للاستعلامات"""

    CROP = "crop"  # محاصيل
    IRRIGATION = "irrigation"  # ري
    PEST = "pest"  # آفات
    FERTILIZER = "fertilizer"  # أسمدة
    WEATHER = "weather"  # طقس
    SOIL = "soil"  # تربة
    GENERAL = "general"  # عام


# Mapping from domain to knowledge collection names
DOMAIN_COLLECTION_MAP: dict[QueryDomain, list[str]] = {
    QueryDomain.CROP: [CROP_KNOWLEDGE, GENERAL_AGRICULTURE],
    QueryDomain.IRRIGATION: [CROP_WATER_REQUIREMENTS, IRRIGATION_PRACTICES],
    QueryDomain.PEST: [PEST_KNOWLEDGE, CROP_KNOWLEDGE],
    QueryDomain.FERTILIZER: [FERTILIZER_KNOWLEDGE, SOIL_KNOWLEDGE],
    QueryDomain.WEATHER: [WEATHER_KNOWLEDGE, GENERAL_AGRICULTURE],
    QueryDomain.SOIL: [SOIL_KNOWLEDGE, FERTILIZER_KNOWLEDGE],
    QueryDomain.GENERAL: [GENERAL_AGRICULTURE, CROP_KNOWLEDGE],
}

# Mapping from domain to UltraRAG workflow YAML files
DOMAIN_WORKFLOW_MAP: dict[QueryDomain, str] = {
    QueryDomain.CROP: "crop_advisory.yaml",
    QueryDomain.IRRIGATION: "irrigation_advisory.yaml",
    QueryDomain.PEST: "pest_diagnosis.yaml",
    QueryDomain.FERTILIZER: "fertilizer_advisory.yaml",
    QueryDomain.WEATHER: "weather_advisory.yaml",
    QueryDomain.SOIL: "soil_analysis_advisory.yaml",
    QueryDomain.GENERAL: "knowledge_search.yaml",
}


@dataclass
class KnowledgeQueryResult:
    """Result from a knowledge query | نتيجة استعلام المعرفة"""

    query: str
    domain: QueryDomain
    answer: str = ""
    answer_ar: str = ""
    sources: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    used_rag: bool = False
    used_local_fallback: bool = False
    latency_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary | تحويل إلى قاموس"""
        return {
            "query": self.query,
            "domain": self.domain.value,
            "answer": self.answer,
            "answer_ar": self.answer_ar,
            "sources": self.sources,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "used_rag": self.used_rag,
            "used_local_fallback": self.used_local_fallback,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp.isoformat(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Local Knowledge Index (offline fallback)
# ═══════════════════════════════════════════════════════════════════════════════


class LocalKnowledgeIndex:
    """
    Simple keyword-based knowledge index for offline/fallback scenarios.
    فهرس معرفة محلي بسيط قائم على الكلمات المفتاحية لسيناريوهات عدم الاتصال.

    When UltraRAG or vector DB is unavailable, this provides basic
    keyword matching against the knowledge collection documents.
    """

    def __init__(self):
        self._documents: dict[str, list[dict[str, Any]]] = {}
        self._loaded = False

    def _load_default_knowledge(self) -> None:
        """Load built-in knowledge entries for offline use."""
        if self._loaded:
            return

        # Crop knowledge entries
        self._documents[CROP_KNOWLEDGE] = [
            {
                "title": "Wheat Cultivation Guide",
                "title_ar": "دليل زراعة القمح",
                "content": (
                    "Wheat requires well-drained loamy soil with pH 6.0-7.5. "
                    "Optimal planting temperature is 10-25°C. Growth stages include "
                    "germination, tillering, stem elongation, heading, flowering, and grain filling. "
                    "Water requirement is 400-650mm per season. Apply nitrogen at tillering "
                    "and stem elongation stages."
                ),
                "content_ar": (
                    "يتطلب القمح تربة طينية جيدة الصرف بدرجة حموضة 6.0-7.5. "
                    "درجة حرارة الزراعة المثلى 10-25 درجة مئوية. "
                    "الاحتياج المائي 400-650 ملم في الموسم."
                ),
                "tags": ["wheat", "قمح", "cultivation", "زراعة", "cereal"],
            },
            {
                "title": "Date Palm Management",
                "title_ar": "إدارة نخيل التمر",
                "content": (
                    "Date palms thrive in arid climates with temperatures 20-40°C. "
                    "Pollination occurs February-April. Key pests include Red Palm Weevil. "
                    "Irrigation requirement is 150-200 liters per tree per day in summer. "
                    "Stages: Hababouk, Kimri, Khalal, Rutab, Tamar."
                ),
                "content_ar": (
                    "تزدهر أشجار النخيل في المناخات الجافة بدرجات حرارة 20-40 مئوية. "
                    "يحدث التلقيح من فبراير إلى أبريل. "
                    "مراحل التمر: الحبابوك، الكمري، الخلال، الرطب، التمر."
                ),
                "tags": ["date_palm", "نخيل", "تمر", "palm", "arid"],
            },
            {
                "title": "Barley Cultivation",
                "title_ar": "زراعة الشعير",
                "content": (
                    "Barley is drought-tolerant and grows in pH 6.0-8.5 soils. "
                    "Requires 350-500mm water per season. Harvest at 12-14% grain moisture. "
                    "Tolerates salinity better than wheat."
                ),
                "content_ar": (
                    "الشعير محصول يتحمل الجفاف وينمو في تربة بدرجة حموضة 6.0-8.5. "
                    "يتحمل الملوحة أفضل من القمح."
                ),
                "tags": ["barley", "شعير", "drought", "cereal"],
            },
        ]

        # Irrigation knowledge
        self._documents[IRRIGATION_PRACTICES] = [
            {
                "title": "Drip Irrigation Best Practices",
                "title_ar": "أفضل ممارسات الري بالتنقيط",
                "content": (
                    "Drip irrigation achieves 90-95% water use efficiency. "
                    "Emitter spacing depends on soil type: 20-30cm for sandy, 40-60cm for clay. "
                    "Operating pressure 0.5-1.5 bar. Filter regularly to prevent clogging. "
                    "Fertigation can be integrated for precise nutrient delivery."
                ),
                "content_ar": (
                    "يحقق الري بالتنقيط كفاءة استخدام مياه 90-95%. "
                    "المسافة بين النقاطات تعتمد على نوع التربة."
                ),
                "tags": ["drip", "irrigation", "ري", "تنقيط", "efficiency"],
            },
            {
                "title": "Deficit Irrigation Strategies",
                "title_ar": "استراتيجيات الري الناقص",
                "content": (
                    "Regulated deficit irrigation (RDI) applies water below ETc during "
                    "non-critical growth stages. Can save 20-40% water with minimal yield loss. "
                    "Critical stages (flowering, grain filling) must receive full irrigation."
                ),
                "content_ar": (
                    "الري الناقص المنظم يطبق المياه أقل من ETc خلال مراحل النمو غير الحرجة. "
                    "يمكن توفير 20-40% من المياه مع فقدان محصول ضئيل."
                ),
                "tags": ["deficit", "irrigation", "ري", "water_saving"],
            },
        ]

        self._documents[CROP_WATER_REQUIREMENTS] = [
            {
                "title": "Crop Water Requirements (ETc)",
                "title_ar": "الاحتياجات المائية للمحاصيل",
                "content": (
                    "Crop water use = ET0 × Kc. Wheat Kc: initial 0.4, mid 1.15, end 0.25. "
                    "Tomato Kc: initial 0.6, mid 1.15, end 0.80. "
                    "Date palm Kc: 0.90-1.0 year-round. "
                    "Barley Kc: initial 0.3, mid 1.15, end 0.25."
                ),
                "content_ar": (
                    "استخدام المياه للمحصول = ET0 × Kc. "
                    "معامل القمح: أولي 0.4، منتصف 1.15، نهاية 0.25."
                ),
                "tags": ["water", "ETc", "Kc", "requirement", "احتياج_مائي"],
            },
        ]

        # Pest knowledge
        self._documents[PEST_KNOWLEDGE] = [
            {
                "title": "Red Palm Weevil (RPW) Management",
                "title_ar": "إدارة سوسة النخيل الحمراء",
                "content": (
                    "Red Palm Weevil (Rhynchophorus ferrugineus) is the most destructive "
                    "palm pest. Detection by pheromone traps (5/ha). Treatment: inject "
                    "Emamectin benzoate 5% at 4-6 points per tree. Response window: 24-48h. "
                    "Preventive spraying every 45 days."
                ),
                "content_ar": (
                    "سوسة النخيل الحمراء هي أخطر آفة تصيب النخيل. "
                    "الكشف بمصائد الفيرومونات. العلاج: حقن إيمامكتين بنزوات 5%."
                ),
                "tags": ["rpw", "palm_weevil", "سوسة", "نخيل", "pest", "critical"],
            },
            {
                "title": "Wheat Aphid Control",
                "title_ar": "مكافحة المن في القمح",
                "content": (
                    "Wheat aphids (Russian wheat aphid, greenbug) cause yield loss up to 70%. "
                    "Economic threshold: 10-15 aphids per tiller. Natural enemies: ladybugs, "
                    "lacewings. Chemical control: Imidacloprid, Thiamethoxam. "
                    "Scout weekly during tillering to heading."
                ),
                "content_ar": (
                    "حشرات المن تسبب خسائر في المحصول تصل إلى 70%. "
                    "العتبة الاقتصادية: 10-15 حشرة لكل شطء."
                ),
                "tags": ["aphid", "من", "wheat", "قمح", "pest", "ipm"],
            },
        ]

        # Fertilizer knowledge
        self._documents[FERTILIZER_KNOWLEDGE] = [
            {
                "title": "Nitrogen Fertilizer Application Guide",
                "title_ar": "دليل تطبيق الأسمدة النيتروجينية",
                "content": (
                    "Nitrogen is critical for vegetative growth. Wheat needs 120-150 kg N/ha: "
                    "split 1/3 at planting, 1/3 at tillering, 1/3 at stem elongation. "
                    "Urea (46% N), Ammonium Sulfate (21% N + 24% S). "
                    "Apply early morning with dew for better absorption. "
                    "Soil test threshold: 25 ppm N minimum."
                ),
                "content_ar": (
                    "النيتروجين ضروري للنمو الخضري. القمح يحتاج 120-150 كجم/هكتار. "
                    "يقسم: ثلث عند الزراعة، ثلث عند التفريع، ثلث عند استطالة الساق."
                ),
                "tags": ["nitrogen", "نيتروجين", "fertilizer", "سماد", "urea"],
            },
            {
                "title": "Phosphorus and Potassium Guide",
                "title_ar": "دليل الفسفور والبوتاسيوم",
                "content": (
                    "Phosphorus (P) promotes root growth and flowering. Apply DAP (18-46-0) "
                    "at planting: 60-80 kg P2O5/ha for wheat. "
                    "Potassium (K) improves drought tolerance and grain quality. "
                    "MOP (0-0-60): 40-60 kg K2O/ha. Soil test: P > 15 ppm, K > 120 ppm."
                ),
                "content_ar": (
                    "الفسفور يعزز نمو الجذور والإزهار. البوتاسيوم يحسن تحمل الجفاف."
                ),
                "tags": ["phosphorus", "potassium", "فسفور", "بوتاسيوم", "fertilizer"],
            },
        ]

        # Weather knowledge
        self._documents[WEATHER_KNOWLEDGE] = [
            {
                "title": "Heat Stress Management",
                "title_ar": "إدارة الإجهاد الحراري",
                "content": (
                    "Heat stress occurs above 35°C for most crops. Wheat is sensitive "
                    "during flowering (>30°C causes sterility). Mitigation: irrigate before "
                    "heat wave, apply potassium, use reflective mulch. "
                    "Date palms tolerate up to 50°C but fruit quality declines above 45°C."
                ),
                "content_ar": (
                    "يحدث الإجهاد الحراري فوق 35 درجة مئوية لمعظم المحاصيل. "
                    "القمح حساس أثناء الإزهار."
                ),
                "tags": ["heat", "stress", "حرارة", "إجهاد", "temperature"],
            },
            {
                "title": "Frost Protection Strategies",
                "title_ar": "استراتيجيات الحماية من الصقيع",
                "content": (
                    "Frost damage occurs below 0°C. Protect by: overhead sprinklers "
                    "(latent heat release), wind machines, smudge pots, row covers. "
                    "Critical temperatures: wheat -5°C (vegetative), citrus -2°C, "
                    "tomato 0°C. Monitor weather alerts 48h ahead."
                ),
                "content_ar": (
                    "يحدث ضرر الصقيع تحت 0 درجة مئوية. "
                    "الحماية: رشاشات علوية، مراوح هوائية، أغطية."
                ),
                "tags": ["frost", "صقيع", "protection", "cold", "برد"],
            },
        ]

        # Soil knowledge
        self._documents[SOIL_KNOWLEDGE] = [
            {
                "title": "Soil pH Management",
                "title_ar": "إدارة حموضة التربة",
                "content": (
                    "Optimal pH for most crops: 6.0-7.5. Acidic soils (<6): apply lime "
                    "(CaCO3) at 2-4 t/ha. Alkaline soils (>8): apply gypsum (CaSO4) or "
                    "elemental sulfur. pH affects nutrient availability: P locked at pH<5.5 "
                    "and pH>7.5. Test soil every 2-3 years."
                ),
                "content_ar": (
                    "درجة الحموضة المثلى لمعظم المحاصيل: 6.0-7.5. "
                    "التربة الحمضية: إضافة الجير. التربة القلوية: إضافة الجبس."
                ),
                "tags": ["pH", "soil", "تربة", "حموضة", "lime", "gypsum"],
            },
            {
                "title": "Salinity Management in Arid Soils",
                "title_ar": "إدارة الملوحة في التربة الجافة",
                "content": (
                    "Soil salinity is a major challenge in arid regions. EC > 4 dS/m is saline. "
                    "Leaching requirement: LR = ECw / (5×ECt - ECw). Salt-tolerant crops: "
                    "barley (8 dS/m), date palm (4 dS/m), wheat (6 dS/m). "
                    "Use drip irrigation to manage salt accumulation at root zone edges."
                ),
                "content_ar": (
                    "ملوحة التربة تحدٍ كبير في المناطق الجافة. "
                    "محاصيل متحملة للملوحة: الشعير، النخيل، القمح."
                ),
                "tags": ["salinity", "ملوحة", "arid", "جاف", "soil", "leaching"],
            },
        ]

        self._documents[GENERAL_AGRICULTURE] = [
            {
                "title": "Integrated Farming Systems",
                "title_ar": "أنظمة الزراعة المتكاملة",
                "content": (
                    "Integrated farming combines crop production, livestock, and aquaculture "
                    "for resource efficiency. Crop rotation improves soil health. "
                    "Cover crops prevent erosion. Composting recycles nutrients."
                ),
                "content_ar": "الزراعة المتكاملة تجمع بين إنتاج المحاصيل والثروة الحيوانية.",
                "tags": ["integrated", "farming", "زراعة", "متكاملة"],
            },
        ]

        self._loaded = True

    def search(
        self,
        query: str,
        collections: list[str],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Search local knowledge by keyword matching.
        البحث في المعرفة المحلية عن طريق مطابقة الكلمات المفتاحية.
        """
        self._load_default_knowledge()

        query_lower = query.lower()
        query_tokens = set(query_lower.split())

        scored_results: list[tuple[float, dict[str, Any]]] = []

        for collection in collections:
            docs = self._documents.get(collection, [])
            for doc in docs:
                score = self._score_document(query_tokens, query_lower, doc)
                if score > 0:
                    result = {
                        **doc,
                        "collection": collection,
                        "score": score,
                    }
                    scored_results.append((score, result))

        # Sort by score descending and return top_k
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in scored_results[:top_k]]

    @staticmethod
    def _score_document(
        query_tokens: set[str],
        query_lower: str,
        doc: dict[str, Any],
    ) -> float:
        """Score a document against query tokens."""
        score = 0.0

        # Check tags (highest weight)
        doc_tags = {t.lower() for t in doc.get("tags", [])}
        tag_matches = query_tokens & doc_tags
        score += len(tag_matches) * 3.0

        # Check title
        title_lower = doc.get("title", "").lower()
        title_ar = doc.get("title_ar", "").lower()
        for token in query_tokens:
            if token in title_lower or token in title_ar:
                score += 2.0

        # Check content (lower weight)
        content_lower = doc.get("content", "").lower()
        content_ar = doc.get("content_ar", "").lower()
        for token in query_tokens:
            if len(token) > 2 and (token in content_lower or token in content_ar):
                score += 1.0

        return score


# ═══════════════════════════════════════════════════════════════════════════════
# Knowledge Service Bridge (Singleton)
# ═══════════════════════════════════════════════════════════════════════════════


_bridge_instance: KnowledgeServiceBridge | None = None


class KnowledgeServiceBridge:
    """
    Unified interface for services to access the agricultural knowledge base.
    واجهة موحدة للخدمات للوصول إلى قاعدة المعرفة الزراعية.

    Integrates Knowledge Base collections with UltraRAG workflows.
    Provides domain-specific query methods with offline-first fallback.

    Usage:
        bridge = get_knowledge_bridge()

        # Query crop knowledge
        result = await bridge.query_crop_knowledge(
            query="When to irrigate wheat during tillering?",
            crop_type="wheat",
            region="middle_east"
        )
        print(result.answer)

        # Query pest treatment
        result = await bridge.query_pest_treatment(
            pest_type="red_palm_weevil",
            crop_type="date_palm"
        )
    """

    def __init__(
        self,
        workflow_dir: str | Path | None = None,
        rag_pipeline: Any = None,
        knowledge_base: Any = None,
        vector_store: Any = None,
    ):
        """
        Initialize the Knowledge Service Bridge.

        Args:
            workflow_dir: Path to UltraRAG workflow YAML files.
                         Defaults to shared/ai/ultrarag/workflows/
            rag_pipeline: Optional pre-configured RAGPipeline instance
            knowledge_base: Optional pre-configured KnowledgeBase instance
            vector_store: Optional vector store for semantic search
        """
        # Determine workflow directory
        if workflow_dir is None:
            workflow_dir = Path(__file__).parent / "ultrarag" / "workflows"
        self._workflow_dir = Path(workflow_dir)

        # External dependencies (lazy initialized)
        self._rag_pipeline = rag_pipeline
        self._knowledge_base = knowledge_base
        self._vector_store = vector_store

        # Internal state
        self._workflow_engine: WorkflowEngine | None = None
        self._local_index = LocalKnowledgeIndex()
        self._initialized = False

    async def _ensure_initialized(self) -> None:
        """Lazy initialization of UltraRAG components."""
        if self._initialized:
            return

        if _ULTRARAG_AVAILABLE and self._workflow_dir.exists():
            try:
                # Initialize workflow engine
                self._workflow_engine = WorkflowEngine(
                    rag_pipeline=self._rag_pipeline
                )

                # Load all workflow configurations
                workflows = load_workflows_from_directory(str(self._workflow_dir))
                for wf_config in workflows:
                    self._workflow_engine._workflows[wf_config.workflow_id] = wf_config

                logger.info(
                    "knowledge_bridge_initialized",
                    workflow_count=len(workflows),
                    ultrarag_available=True,
                )
            except Exception as e:
                logger.warning(
                    "knowledge_bridge_ultrarag_init_failed",
                    error=str(e),
                    fallback="local_index",
                )
                self._workflow_engine = None
        else:
            logger.info(
                "knowledge_bridge_offline_mode",
                ultrarag_available=_ULTRARAG_AVAILABLE,
                workflow_dir_exists=self._workflow_dir.exists(),
            )

        self._initialized = True

    # ── Domain-Specific Query Methods ────────────────────────────────────────

    async def query_crop_knowledge(
        self,
        query: str,
        crop_type: str | None = None,
        region: str | None = None,
        growth_stage: str | None = None,
        top_k: int = 5,
    ) -> KnowledgeQueryResult:
        """
        Query crop-specific knowledge.
        استعلام معرفة خاصة بالمحاصيل.

        Args:
            query: The natural language query (Arabic or English)
            crop_type: e.g. "wheat", "date_palm", "barley", "tomato"
            region: e.g. "middle_east", "gulf", "yemen", "north_africa"
            growth_stage: e.g. "tillering", "flowering", "grain_filling"
            top_k: Number of results to return

        Returns:
            KnowledgeQueryResult with answer and sources
        """
        enriched_query = query
        if crop_type:
            enriched_query = f"{crop_type} {enriched_query}"
        if growth_stage:
            enriched_query = f"{enriched_query} {growth_stage}"

        metadata = {
            "crop_type": crop_type,
            "region": region,
            "growth_stage": growth_stage,
        }

        return await self._execute_query(
            query=enriched_query,
            domain=QueryDomain.CROP,
            workflow_name=DOMAIN_WORKFLOW_MAP[QueryDomain.CROP],
            metadata=metadata,
            top_k=top_k,
        )

    async def query_irrigation_advice(
        self,
        query: str,
        crop_type: str | None = None,
        soil_type: str | None = None,
        irrigation_method: str | None = None,
        top_k: int = 5,
    ) -> KnowledgeQueryResult:
        """
        Query irrigation-specific knowledge.
        استعلام معرفة خاصة بالري.

        Args:
            query: The natural language query
            crop_type: e.g. "wheat", "date_palm"
            soil_type: e.g. "sandy", "clay", "loam"
            irrigation_method: e.g. "drip", "sprinkler", "flood"
            top_k: Number of results to return
        """
        enriched_query = query
        if crop_type:
            enriched_query = f"{crop_type} {enriched_query}"
        if soil_type:
            enriched_query = f"{enriched_query} {soil_type} soil"

        metadata = {
            "crop_type": crop_type,
            "soil_type": soil_type,
            "irrigation_method": irrigation_method,
        }

        return await self._execute_query(
            query=enriched_query,
            domain=QueryDomain.IRRIGATION,
            workflow_name=DOMAIN_WORKFLOW_MAP[QueryDomain.IRRIGATION],
            metadata=metadata,
            top_k=top_k,
        )

    async def query_pest_treatment(
        self,
        pest_type: str,
        crop_type: str | None = None,
        severity: str | None = None,
        top_k: int = 5,
    ) -> KnowledgeQueryResult:
        """
        Query pest treatment knowledge.
        استعلام معرفة معالجة الآفات.

        Args:
            pest_type: e.g. "red_palm_weevil", "aphid", "whitefly", "locust"
            crop_type: e.g. "date_palm", "wheat", "tomato"
            severity: e.g. "low", "moderate", "high", "critical"
            top_k: Number of results to return
        """
        query = f"{pest_type} treatment control"
        if crop_type:
            query = f"{crop_type} {query}"
        if severity:
            query = f"{query} {severity} severity"

        metadata = {
            "pest_type": pest_type,
            "crop_type": crop_type,
            "severity": severity,
        }

        return await self._execute_query(
            query=query,
            domain=QueryDomain.PEST,
            workflow_name=DOMAIN_WORKFLOW_MAP[QueryDomain.PEST],
            metadata=metadata,
            top_k=top_k,
        )

    async def query_fertilizer_recommendation(
        self,
        soil_test: dict[str, float] | None = None,
        crop_type: str | None = None,
        growth_stage: str | None = None,
        top_k: int = 5,
    ) -> KnowledgeQueryResult:
        """
        Query fertilizer recommendation knowledge.
        استعلام معرفة توصيات الأسمدة.

        Args:
            soil_test: Dict with nutrient levels, e.g. {"nitrogen": 18, "phosphorus": 25, "potassium": 150}
            crop_type: e.g. "wheat", "tomato"
            growth_stage: e.g. "tillering", "flowering"
            top_k: Number of results to return
        """
        query_parts = ["fertilizer recommendation"]
        if crop_type:
            query_parts.insert(0, crop_type)
        if growth_stage:
            query_parts.append(f"at {growth_stage} stage")
        if soil_test:
            deficiencies = []
            thresholds = {"nitrogen": 25, "phosphorus": 15, "potassium": 120}
            for nutrient, level in soil_test.items():
                threshold = thresholds.get(nutrient.lower())
                if threshold and level < threshold:
                    deficiencies.append(f"low {nutrient}")
            if deficiencies:
                query_parts.append(", ".join(deficiencies))

        query = " ".join(query_parts)

        metadata = {
            "soil_test": soil_test,
            "crop_type": crop_type,
            "growth_stage": growth_stage,
        }

        return await self._execute_query(
            query=query,
            domain=QueryDomain.FERTILIZER,
            workflow_name=DOMAIN_WORKFLOW_MAP[QueryDomain.FERTILIZER],
            metadata=metadata,
            top_k=top_k,
        )

    async def query_weather_advisory(
        self,
        region: str,
        season: str | None = None,
        concern: str | None = None,
        top_k: int = 5,
    ) -> KnowledgeQueryResult:
        """
        Query weather and climate advisory knowledge.
        استعلام معرفة الطقس والمناخ.

        Args:
            region: e.g. "middle_east", "gulf", "yemen", "saudi_arabia"
            season: e.g. "summer", "winter", "spring"
            concern: e.g. "heat_stress", "frost", "drought", "flood"
            top_k: Number of results to return
        """
        query_parts = [region, "weather advisory"]
        if season:
            query_parts.insert(1, season)
        if concern:
            query_parts.append(concern)

        query = " ".join(query_parts)

        metadata = {
            "region": region,
            "season": season,
            "concern": concern,
        }

        return await self._execute_query(
            query=query,
            domain=QueryDomain.WEATHER,
            workflow_name=DOMAIN_WORKFLOW_MAP[QueryDomain.WEATHER],
            metadata=metadata,
            top_k=top_k,
        )

    async def general_query(
        self,
        query: str,
        domain: str | QueryDomain | None = None,
        top_k: int = 5,
    ) -> KnowledgeQueryResult:
        """
        General-purpose knowledge query with optional domain hint.
        استعلام معرفة عام مع تلميح اختياري بالمجال.

        Args:
            query: The natural language query (Arabic or English)
            domain: Optional domain hint for better results
            top_k: Number of results to return
        """
        if domain is not None:
            if isinstance(domain, str):
                try:
                    resolved_domain = QueryDomain(domain)
                except ValueError:
                    resolved_domain = QueryDomain.GENERAL
            else:
                resolved_domain = domain
        else:
            resolved_domain = self._detect_domain(query)

        workflow_name = DOMAIN_WORKFLOW_MAP.get(
            resolved_domain,
            DOMAIN_WORKFLOW_MAP[QueryDomain.GENERAL],
        )

        return await self._execute_query(
            query=query,
            domain=resolved_domain,
            workflow_name=workflow_name,
            metadata={"auto_detected_domain": resolved_domain.value},
            top_k=top_k,
        )

    # ── Internal Methods ─────────────────────────────────────────────────────

    async def _execute_query(
        self,
        query: str,
        domain: QueryDomain,
        workflow_name: str,
        metadata: dict[str, Any],
        top_k: int = 5,
    ) -> KnowledgeQueryResult:
        """
        Execute a knowledge query, attempting UltraRAG first, then local fallback.
        تنفيذ استعلام معرفي، محاولة UltraRAG أولاً ثم الرجوع للمحلي.
        """
        await self._ensure_initialized()
        start_time = time.time()

        # Attempt UltraRAG workflow execution
        if self._workflow_engine and _ULTRARAG_AVAILABLE:
            try:
                result = await self._execute_rag_query(
                    query=query,
                    domain=domain,
                    workflow_name=workflow_name,
                    metadata=metadata,
                    top_k=top_k,
                )
                if result is not None:
                    result.latency_ms = (time.time() - start_time) * 1000
                    return result
            except Exception as e:
                logger.warning(
                    "rag_query_failed_falling_back",
                    domain=domain.value,
                    error=str(e),
                )

        # Fallback to local keyword-based search
        result = self._execute_local_query(
            query=query,
            domain=domain,
            metadata=metadata,
            top_k=top_k,
        )
        result.latency_ms = (time.time() - start_time) * 1000
        return result

    async def _execute_rag_query(
        self,
        query: str,
        domain: QueryDomain,
        workflow_name: str,
        metadata: dict[str, Any],
        top_k: int = 5,
    ) -> KnowledgeQueryResult | None:
        """Execute query using UltraRAG workflow engine."""
        if not self._workflow_engine:
            return None

        # Determine which workflow to use
        workflow_id = workflow_name.replace(".yaml", "")

        # Check if workflow is loaded
        if workflow_id not in self._workflow_engine._workflows:
            # Try loading the specific workflow file
            workflow_path = self._workflow_dir / workflow_name
            if workflow_path.exists():
                wf_config = load_workflow_from_yaml(str(workflow_path))
                self._workflow_engine._workflows[wf_config.workflow_id] = wf_config
            else:
                return None

        # Build RAG request
        rag_request = RAGRequest(
            query=query,
            collection=DOMAIN_COLLECTION_MAP.get(domain, [GENERAL_AGRICULTURE])[0],
            top_k=top_k,
            metadata=metadata,
        )

        # Execute workflow
        from .ultrarag.workflow import WorkflowExecutionContext

        context = WorkflowExecutionContext(
            workflow_id=workflow_id,
            variables={
                "query": query,
                "domain": domain.value,
                "top_k": top_k,
                **metadata,
            },
        )

        # Execute workflow steps
        await self._workflow_engine.execute(workflow_id, context)

        # Extract results from context
        answer = context.variables.get("final_answer", "")
        answer_ar = context.variables.get("final_answer_ar", "")
        sources_raw = context.variables.get("sources", [])
        confidence = context.variables.get("confidence", 0.5)

        sources = []
        if isinstance(sources_raw, list):
            for src in sources_raw:
                if isinstance(src, dict):
                    sources.append(src)
                elif isinstance(src, str):
                    sources.append({"content": src})

        if not answer and not sources:
            return None

        return KnowledgeQueryResult(
            query=query,
            domain=domain,
            answer=answer,
            answer_ar=answer_ar,
            sources=sources,
            confidence=confidence,
            metadata=metadata,
            used_rag=True,
            used_local_fallback=False,
        )

    def _execute_local_query(
        self,
        query: str,
        domain: QueryDomain,
        metadata: dict[str, Any],
        top_k: int = 5,
    ) -> KnowledgeQueryResult:
        """Execute query using local keyword-based knowledge index."""
        collections = DOMAIN_COLLECTION_MAP.get(
            domain, DOMAIN_COLLECTION_MAP[QueryDomain.GENERAL]
        )

        results = self._local_index.search(
            query=query,
            collections=collections,
            top_k=top_k,
        )

        # Build answer from top results
        answer_parts: list[str] = []
        answer_ar_parts: list[str] = []
        sources: list[dict[str, Any]] = []

        for doc in results:
            answer_parts.append(doc.get("content", ""))
            if doc.get("content_ar"):
                answer_ar_parts.append(doc["content_ar"])
            sources.append({
                "title": doc.get("title", ""),
                "title_ar": doc.get("title_ar", ""),
                "collection": doc.get("collection", ""),
                "score": doc.get("score", 0),
            })

        answer = "\n\n".join(answer_parts) if answer_parts else ""
        answer_ar = "\n\n".join(answer_ar_parts) if answer_ar_parts else ""
        confidence = min(results[0]["score"] / 10.0, 1.0) if results else 0.0

        return KnowledgeQueryResult(
            query=query,
            domain=domain,
            answer=answer,
            answer_ar=answer_ar,
            sources=sources,
            confidence=confidence,
            metadata=metadata,
            used_rag=False,
            used_local_fallback=True,
        )

    def _detect_domain(self, query: str) -> QueryDomain:
        """
        Auto-detect query domain from keywords.
        الكشف التلقائي عن مجال الاستعلام من الكلمات المفتاحية.
        """
        query_lower = query.lower()

        domain_keywords: dict[QueryDomain, list[str]] = {
            QueryDomain.IRRIGATION: [
                "irrigat", "water", "ري", "مياه", "drip", "sprinkler", "تنقيط",
                "moisture", "رطوبة", "ETc", "ET0",
            ],
            QueryDomain.PEST: [
                "pest", "insect", "آفة", "حشرة", "weevil", "سوسة", "aphid", "من",
                "worm", "locust", "جراد", "whitefly", "ذبابة",
            ],
            QueryDomain.FERTILIZER: [
                "fertiliz", "nutrient", "سماد", "nitrogen", "نيتروجين", "phosphor",
                "فسفور", "potassium", "بوتاسيوم", "urea", "يوريا", "NPK", "deficien",
            ],
            QueryDomain.WEATHER: [
                "weather", "طقس", "temperature", "حرارة", "rain", "مطر", "frost",
                "صقيع", "heat", "drought", "جفاف", "wind", "رياح", "climate", "مناخ",
            ],
            QueryDomain.SOIL: [
                "soil", "تربة", "pH", "salinity", "ملوحة", "clay", "sand", "رمل",
                "organic matter", "EC", "drainage", "صرف",
            ],
            QueryDomain.CROP: [
                "crop", "محصول", "wheat", "قمح", "barley", "شعير", "date", "نخيل",
                "tomato", "طماطم", "growth", "نمو", "yield", "إنتاج", "planting", "زراعة",
                "harvest", "حصاد", "variety", "صنف",
            ],
        }

        best_domain = QueryDomain.GENERAL
        best_score = 0

        for domain, keywords in domain_keywords.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > best_score:
                best_score = score
                best_domain = domain

        return best_domain


# ═══════════════════════════════════════════════════════════════════════════════
# Singleton Access
# ═══════════════════════════════════════════════════════════════════════════════


def get_knowledge_bridge(
    workflow_dir: str | Path | None = None,
    rag_pipeline: Any = None,
    knowledge_base: Any = None,
    vector_store: Any = None,
) -> KnowledgeServiceBridge:
    """
    Get or create the singleton KnowledgeServiceBridge instance.
    الحصول على أو إنشاء مثيل جسر خدمة المعرفة الوحيد.

    Usage:
        bridge = get_knowledge_bridge()
        result = await bridge.query_crop_knowledge("When to plant wheat?")
    """
    global _bridge_instance

    if _bridge_instance is None:
        _bridge_instance = KnowledgeServiceBridge(
            workflow_dir=workflow_dir,
            rag_pipeline=rag_pipeline,
            knowledge_base=knowledge_base,
            vector_store=vector_store,
        )

    return _bridge_instance


def reset_knowledge_bridge() -> None:
    """
    Reset the singleton instance (useful for testing).
    إعادة تعيين المثيل الوحيد (مفيد للاختبار).
    """
    global _bridge_instance
    _bridge_instance = None
