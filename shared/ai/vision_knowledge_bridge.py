# ═══════════════════════════════════════════════════════════════════════════════
# Vision-Knowledge Bridge
# جسر الرؤية والمعرفة
# ═══════════════════════════════════════════════════════════════════════════════
#
# Connects CropVision detection results with the agricultural knowledge base
# to provide evidence-based recommendations with knowledge citations.
#
# Pipeline:
#   1. Takes CropVision detection results (disease/pest detections)
#   2. Queries PEST_KNOWLEDGE and CROP_KNOWLEDGE collections
#   3. Applies CRAG (Corrective Retrieval) for validation
#   4. Returns enriched recommendations with knowledge citations
#
# يربط نتائج كشف رؤية المحاصيل مع قاعدة المعرفة الزراعية
# لتقديم توصيات مبنية على الأدلة مع اقتباسات المعرفة
#
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog

from .crop_vision import (
    CropType,
    DiseaseDetection,
    DiseaseType,
    PestDetection,
    PestType,
    Severity,
    VisionAnalysisResult,
)
from .knowledge.collections import (
    CROP_KNOWLEDGE,
    GENERAL_AGRICULTURE,
    PEST_KNOWLEDGE,
)
from .knowledge.corrective_retrieval import (
    CorrectiveRetrievalEngine,
    CRAGResult,
    RetrievalAction,
)
from .knowledge.vector_store_integration import (
    KnowledgeVectorStore,
    VectorSearchResult,
)

logger = structlog.get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class KnowledgeCitation:
    """A citation from the knowledge base supporting a recommendation.
    اقتباس من قاعدة المعرفة يدعم توصية"""

    source: str
    content: str
    content_ar: str = ""
    relevance_score: float = 0.0
    collection: str = ""
    document_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "content": self.content,
            "content_ar": self.content_ar,
            "relevance_score": round(self.relevance_score, 3),
            "collection": self.collection,
            "document_id": self.document_id,
        }


@dataclass
class EnrichedRecommendation:
    """A recommendation enriched with knowledge base evidence.
    توصية معززة بأدلة من قاعدة المعرفة"""

    recommendation: str
    recommendation_ar: str = ""
    severity: str = ""
    confidence: float = 0.0
    knowledge_validated: bool = False
    validation_action: str = ""
    citations: list[KnowledgeCitation] = field(default_factory=list)
    treatment_options: list[dict[str, str]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "recommendation": self.recommendation,
            "recommendation_ar": self.recommendation_ar,
            "severity": self.severity,
            "confidence": self.confidence,
            "knowledge_validated": self.knowledge_validated,
            "validation_action": self.validation_action,
            "citations": [c.to_dict() for c in self.citations],
            "treatment_options": self.treatment_options,
            "metadata": self.metadata,
        }


@dataclass
class VisionKnowledgeResult:
    """Complete result from the Vision-Knowledge bridge.
    نتيجة كاملة من جسر الرؤية والمعرفة"""

    vision_result_id: str
    crop_type: str
    disease_recommendations: list[EnrichedRecommendation] = field(default_factory=list)
    pest_recommendations: list[EnrichedRecommendation] = field(default_factory=list)
    general_advisory: str = ""
    general_advisory_ar: str = ""
    total_citations: int = 0
    knowledge_confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "vision_result_id": self.vision_result_id,
            "crop_type": self.crop_type,
            "disease_recommendations": [r.to_dict() for r in self.disease_recommendations],
            "pest_recommendations": [r.to_dict() for r in self.pest_recommendations],
            "general_advisory": self.general_advisory,
            "general_advisory_ar": self.general_advisory_ar,
            "total_citations": self.total_citations,
            "knowledge_confidence": round(self.knowledge_confidence, 3),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Disease/Pest to Query Mapping
# ─────────────────────────────────────────────────────────────────────────────

# Maps disease types to bilingual search queries for knowledge retrieval
_DISEASE_QUERY_MAP: dict[DiseaseType, dict[str, str]] = {
    DiseaseType.WHEAT_RUST: {
        "en": "wheat rust disease treatment fungicide application",
        "ar": "علاج صدأ القمح مبيد فطري",
    },
    DiseaseType.WHEAT_POWDERY_MILDEW: {
        "en": "wheat powdery mildew treatment prevention",
        "ar": "علاج البياض الدقيقي للقمح الوقاية",
    },
    DiseaseType.WHEAT_SEPTORIA: {
        "en": "wheat septoria leaf blotch treatment",
        "ar": "علاج تبقع أوراق القمح سبتوريا",
    },
    DiseaseType.BARLEY_NET_BLOTCH: {
        "en": "barley net blotch disease management",
        "ar": "إدارة مرض التبقع الشبكي للشعير",
    },
    DiseaseType.BARLEY_SCALD: {
        "en": "barley scald disease treatment",
        "ar": "علاج مرض تلفح الشعير",
    },
    DiseaseType.DATE_PALM_BAYOUD: {
        "en": "date palm bayoud disease fusarium wilt",
        "ar": "مرض البيوض النخيل ذبول الفيوزاريوم",
    },
    DiseaseType.DATE_PALM_BLACK_SCORCH: {
        "en": "date palm black scorch disease treatment",
        "ar": "علاج مرض الحرق الأسود للنخيل",
    },
    DiseaseType.TOMATO_LATE_BLIGHT: {
        "en": "tomato late blight phytophthora treatment",
        "ar": "علاج اللفحة المتأخرة للطماطم فيتوفثورا",
    },
    DiseaseType.TOMATO_EARLY_BLIGHT: {
        "en": "tomato early blight alternaria treatment",
        "ar": "علاج اللفحة المبكرة للطماطم ألترناريا",
    },
    DiseaseType.TOMATO_LEAF_MOLD: {
        "en": "tomato leaf mold fulvia treatment",
        "ar": "علاج عفن أوراق الطماطم",
    },
    DiseaseType.NUTRIENT_DEFICIENCY: {
        "en": "crop nutrient deficiency diagnosis fertilizer recommendation",
        "ar": "تشخيص نقص العناصر الغذائية توصية السماد",
    },
    DiseaseType.WATER_STRESS: {
        "en": "crop water stress irrigation management",
        "ar": "إجهاد مائي إدارة الري",
    },
}

_PEST_QUERY_MAP: dict[PestType, dict[str, str]] = {
    PestType.APHIDS: {
        "en": "aphid infestation control IPM biological treatment",
        "ar": "مكافحة المن الإدارة المتكاملة العلاج البيولوجي",
    },
    PestType.LOCUSTS: {
        "en": "locust swarm control emergency response insecticide",
        "ar": "مكافحة أسراب الجراد استجابة طوارئ مبيد حشري",
    },
    PestType.RED_PALM_WEEVIL: {
        "en": "red palm weevil detection treatment pheromone trap injection",
        "ar": "سوسة النخيل الحمراء كشف علاج مصيدة فيرومونية حقن",
    },
    PestType.WHITEFLY: {
        "en": "whitefly control greenhouse field management",
        "ar": "مكافحة الذبابة البيضاء إدارة الحقل البيوت المحمية",
    },
    PestType.SPIDER_MITES: {
        "en": "spider mite treatment acaricide miticide",
        "ar": "علاج العنكبوت الأحمر مبيد عناكب",
    },
    PestType.ARMYWORM: {
        "en": "armyworm fall armyworm control management",
        "ar": "مكافحة دودة الحشد إدارة",
    },
    PestType.STEM_BORER: {
        "en": "stem borer control cereal crop management",
        "ar": "مكافحة حفار الساق محاصيل حبوب",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Vision Knowledge Bridge
# ─────────────────────────────────────────────────────────────────────────────


class VisionKnowledgeBridge:
    """Connects CropVision detections with the agricultural knowledge base.
    يربط كشف رؤية المحاصيل مع قاعدة المعرفة الزراعية

    Takes detection results from CropVisionAnalyzer and enriches them with
    evidence-based recommendations from PEST_KNOWLEDGE and CROP_KNOWLEDGE
    collections, validated through CRAG (Corrective Retrieval).

    Usage:
        bridge = VisionKnowledgeBridge(vector_store=my_store)
        vision_result = await analyzer.analyze_image(image_path)
        enriched = bridge.enrich_vision_result(vision_result)
        print(enriched.disease_recommendations[0].citations)
    """

    def __init__(
        self,
        vector_store: KnowledgeVectorStore | None = None,
        crag_engine: CorrectiveRetrievalEngine | None = None,
        top_k: int = 5,
        min_relevance_score: float = 0.3,
    ) -> None:
        self._vector_store = vector_store
        self._crag_engine = crag_engine or CorrectiveRetrievalEngine(
            correct_threshold=0.7,
            ambiguous_threshold=0.4,
            max_refined_chunks=10,
        )
        self._top_k = top_k
        self._min_relevance = min_relevance_score

        logger.info(
            "vision_knowledge_bridge_init",
            has_vector_store=vector_store is not None,
            top_k=top_k,
            min_relevance=min_relevance_score,
        )

    def enrich_vision_result(
        self,
        vision_result: VisionAnalysisResult,
        region: str = "",
    ) -> VisionKnowledgeResult:
        """Enrich a vision analysis result with knowledge base evidence.
        تعزيز نتيجة تحليل الرؤية بأدلة من قاعدة المعرفة

        Args:
            vision_result: Complete vision analysis result from CropVisionAnalyzer
            region: Target region for region-aware CRAG scoring

        Returns:
            VisionKnowledgeResult with enriched recommendations and citations
        """
        result = VisionKnowledgeResult(
            vision_result_id=vision_result.id,
            crop_type=vision_result.crop_type.value,
        )

        total_citations = 0
        all_confidences: list[float] = []

        # Enrich disease detections
        for detection in vision_result.disease_detections:
            if detection.disease_type == DiseaseType.HEALTHY:
                continue
            if detection.disease_type == DiseaseType.UNKNOWN:
                continue

            enriched = self._enrich_disease_detection(
                detection=detection,
                crop_type=vision_result.crop_type,
                region=region,
            )
            result.disease_recommendations.append(enriched)
            total_citations += len(enriched.citations)
            if enriched.confidence > 0:
                all_confidences.append(enriched.confidence)

        # Enrich pest detections
        for detection in vision_result.pest_detections:
            if detection.pest_type == PestType.NONE_DETECTED:
                continue
            if detection.pest_type == PestType.UNKNOWN:
                continue

            enriched = self._enrich_pest_detection(
                detection=detection,
                crop_type=vision_result.crop_type,
                region=region,
            )
            result.pest_recommendations.append(enriched)
            total_citations += len(enriched.citations)
            if enriched.confidence > 0:
                all_confidences.append(enriched.confidence)

        result.total_citations = total_citations
        result.knowledge_confidence = (
            sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        )

        # Generate general advisory summary
        result.general_advisory, result.general_advisory_ar = (
            self._generate_general_advisory(vision_result, result)
        )

        logger.info(
            "vision_knowledge_enrichment_complete",
            vision_id=vision_result.id,
            disease_recs=len(result.disease_recommendations),
            pest_recs=len(result.pest_recommendations),
            total_citations=total_citations,
            knowledge_confidence=round(result.knowledge_confidence, 3),
        )

        return result

    def _enrich_disease_detection(
        self,
        detection: DiseaseDetection,
        crop_type: CropType,
        region: str = "",
    ) -> EnrichedRecommendation:
        """Enrich a single disease detection with knowledge base evidence.
        تعزيز كشف مرض واحد بأدلة من قاعدة المعرفة"""

        # Build search query from disease type
        query_map = _DISEASE_QUERY_MAP.get(detection.disease_type, {})
        query_en = query_map.get("en", f"{detection.disease_type.value} treatment for {crop_type.value}")
        query_ar = query_map.get("ar", "")

        # Add crop type context to query
        query_en = f"{crop_type.value} {query_en}"

        # Search knowledge base
        search_results = self._search_knowledge(
            query=query_en,
            query_ar=query_ar,
            collections=[PEST_KNOWLEDGE, CROP_KNOWLEDGE],
        )

        # Apply CRAG validation
        crag_result = self._validate_with_crag(
            query=query_en,
            search_results=search_results,
            domain="pest_disease",
            region=region,
        )

        # Build enriched recommendation
        citations = self._build_citations(search_results, crag_result)

        # Combine original recommendations with knowledge-based ones
        combined_rec_en = "; ".join(detection.recommendations) if detection.recommendations else ""
        combined_rec_ar = "; ".join(detection.recommendations_ar) if detection.recommendations_ar else ""

        # Add knowledge-based treatment options
        treatment_options = self._extract_treatment_options(search_results, crag_result)

        # Enhance with knowledge context
        if crag_result and crag_result.refined_chunks:
            kb_context = " ".join(
                chunk.content[:200] for chunk in crag_result.refined_chunks[:2]
            )
            if kb_context and combined_rec_en:
                combined_rec_en += f". Knowledge base: {kb_context}"
            elif kb_context:
                combined_rec_en = kb_context

            kb_context_ar = " ".join(
                chunk.content_ar[:200]
                for chunk in crag_result.refined_chunks[:2]
                if chunk.content_ar
            )
            if kb_context_ar and combined_rec_ar:
                combined_rec_ar += f". قاعدة المعرفة: {kb_context_ar}"
            elif kb_context_ar:
                combined_rec_ar = kb_context_ar

        return EnrichedRecommendation(
            recommendation=combined_rec_en or f"Detected {detection.disease_type.value} - consult agricultural advisor",
            recommendation_ar=combined_rec_ar or f"تم كشف {detection.disease_type.value} - استشر مستشارًا زراعيًا",
            severity=detection.severity.value,
            confidence=detection.confidence,
            knowledge_validated=crag_result is not None and crag_result.action_taken == RetrievalAction.CORRECT,
            validation_action=crag_result.action_taken.value if crag_result else "none",
            citations=citations,
            treatment_options=treatment_options,
            metadata={
                "disease_type": detection.disease_type.value,
                "affected_area_percent": detection.affected_area_percent,
                "crop_type": crop_type.value,
                "crag_score": round(crag_result.evaluation.overall_score, 3) if crag_result else 0.0,
            },
        )

    def _enrich_pest_detection(
        self,
        detection: PestDetection,
        crop_type: CropType,
        region: str = "",
    ) -> EnrichedRecommendation:
        """Enrich a single pest detection with knowledge base evidence.
        تعزيز كشف آفة واحدة بأدلة من قاعدة المعرفة"""

        # Build search query from pest type
        query_map = _PEST_QUERY_MAP.get(detection.pest_type, {})
        query_en = query_map.get("en", f"{detection.pest_type.value} control for {crop_type.value}")
        query_ar = query_map.get("ar", "")

        # Add crop type context
        query_en = f"{crop_type.value} {query_en}"

        # Search knowledge base
        search_results = self._search_knowledge(
            query=query_en,
            query_ar=query_ar,
            collections=[PEST_KNOWLEDGE, CROP_KNOWLEDGE],
        )

        # Apply CRAG validation
        crag_result = self._validate_with_crag(
            query=query_en,
            search_results=search_results,
            domain="pest_disease",
            region=region,
        )

        # Build citations and treatment options
        citations = self._build_citations(search_results, crag_result)
        treatment_options = self._extract_treatment_options(search_results, crag_result)

        # Combine original + knowledge-based recommendations
        combined_rec_en = "; ".join(detection.recommendations) if detection.recommendations else ""
        combined_rec_ar = "; ".join(detection.recommendations_ar) if detection.recommendations_ar else ""

        if crag_result and crag_result.refined_chunks:
            kb_context = " ".join(
                chunk.content[:200] for chunk in crag_result.refined_chunks[:2]
            )
            if kb_context and combined_rec_en:
                combined_rec_en += f". Knowledge base: {kb_context}"
            elif kb_context:
                combined_rec_en = kb_context

            kb_context_ar = " ".join(
                chunk.content_ar[:200]
                for chunk in crag_result.refined_chunks[:2]
                if chunk.content_ar
            )
            if kb_context_ar and combined_rec_ar:
                combined_rec_ar += f". قاعدة المعرفة: {kb_context_ar}"
            elif kb_context_ar:
                combined_rec_ar = kb_context_ar

        return EnrichedRecommendation(
            recommendation=combined_rec_en or f"Detected {detection.pest_type.value} - apply IPM protocol",
            recommendation_ar=combined_rec_ar or f"تم كشف {detection.pest_type.value} - طبق بروتوكول الإدارة المتكاملة",
            severity=detection.severity.value,
            confidence=detection.confidence,
            knowledge_validated=crag_result is not None and crag_result.action_taken == RetrievalAction.CORRECT,
            validation_action=crag_result.action_taken.value if crag_result else "none",
            citations=citations,
            treatment_options=treatment_options,
            metadata={
                "pest_type": detection.pest_type.value,
                "count_estimate": detection.count_estimate,
                "treatment_urgency": detection.treatment_urgency,
                "crop_type": crop_type.value,
                "crag_score": round(crag_result.evaluation.overall_score, 3) if crag_result else 0.0,
            },
        )

    def _search_knowledge(
        self,
        query: str,
        query_ar: str = "",
        collections: list[str] | None = None,
    ) -> list[VectorSearchResult]:
        """Search the knowledge base for relevant information.
        البحث في قاعدة المعرفة عن معلومات ذات صلة"""
        if not self._vector_store:
            logger.debug("knowledge_search_skipped_no_store")
            return []

        all_results: list[VectorSearchResult] = []

        target_collections = collections or [PEST_KNOWLEDGE, CROP_KNOWLEDGE]

        for collection in target_collections:
            try:
                results = self._vector_store.search_bilingual(
                    query=query,
                    query_ar=query_ar,
                    collection=collection,
                    top_k=self._top_k,
                )
                all_results.extend(results)
            except Exception as e:
                logger.warning(
                    "knowledge_search_error",
                    collection=collection,
                    error=str(e),
                )

        # Sort by score descending and deduplicate
        all_results.sort(key=lambda r: r.score, reverse=True)

        # Deduplicate by document_id + content hash
        seen: set[str] = set()
        unique_results: list[VectorSearchResult] = []
        for r in all_results:
            key = f"{r.document_id}:{hash(r.content[:100])}"
            if key not in seen:
                seen.add(key)
                unique_results.append(r)

        return unique_results[: self._top_k * 2]

    def _validate_with_crag(
        self,
        query: str,
        search_results: list[VectorSearchResult],
        domain: str = "",
        region: str = "",
    ) -> CRAGResult | None:
        """Apply CRAG validation to search results.
        تطبيق التحقق بالاسترجاع التصحيحي على نتائج البحث"""
        if not search_results:
            return None

        # Convert VectorSearchResult to chunk dicts for CRAG engine
        chunks_for_crag: list[dict[str, Any]] = []
        for result in search_results:
            chunks_for_crag.append({
                "content": result.content,
                "content_ar": result.content_ar,
                "score": result.score,
                "collection": result.collection,
                "metadata": result.metadata,
            })

        try:
            crag_result = self._crag_engine.evaluate_and_refine(
                query=query,
                retrieved_chunks=chunks_for_crag,
                query_domain=domain,
                target_region=region,
            )

            logger.debug(
                "crag_validation_complete",
                action=crag_result.action_taken.value,
                score=round(crag_result.evaluation.overall_score, 3),
                chunks_in=crag_result.total_chunks_input,
                chunks_out=crag_result.total_chunks_output,
            )

            return crag_result

        except Exception as e:
            logger.warning("crag_validation_error", error=str(e))
            return None

    def _build_citations(
        self,
        search_results: list[VectorSearchResult],
        crag_result: CRAGResult | None,
    ) -> list[KnowledgeCitation]:
        """Build knowledge citations from search and CRAG results.
        بناء اقتباسات المعرفة من نتائج البحث والاسترجاع التصحيحي"""
        citations: list[KnowledgeCitation] = []

        # If CRAG refined chunks, use those as primary citations
        if crag_result and crag_result.refined_chunks:
            for chunk in crag_result.refined_chunks:
                if chunk.relevance_score >= self._min_relevance:
                    citations.append(
                        KnowledgeCitation(
                            source=chunk.source or chunk.collection,
                            content=chunk.content[:300],
                            content_ar=chunk.content_ar[:300] if chunk.content_ar else "",
                            relevance_score=chunk.relevance_score,
                            collection=chunk.collection,
                        )
                    )
        else:
            # Fall back to raw search results
            for result in search_results:
                if result.score >= self._min_relevance:
                    citations.append(
                        KnowledgeCitation(
                            source=result.metadata.get("source_name", result.collection),
                            content=result.content[:300],
                            content_ar=result.content_ar[:300] if result.content_ar else "",
                            relevance_score=result.score,
                            collection=result.collection,
                            document_id=result.document_id,
                        )
                    )

        return citations[:5]  # Limit to top 5 citations

    def _extract_treatment_options(
        self,
        search_results: list[VectorSearchResult],
        crag_result: CRAGResult | None,
    ) -> list[dict[str, str]]:
        """Extract treatment options from knowledge base results.
        استخراج خيارات العلاج من نتائج قاعدة المعرفة"""
        treatment_options: list[dict[str, str]] = []

        # Use CRAG refined chunks if available, otherwise raw results
        source_chunks: list[Any] = []
        if crag_result and crag_result.refined_chunks:
            source_chunks = crag_result.refined_chunks
        elif search_results:
            source_chunks = search_results

        for chunk in source_chunks[:3]:
            content = getattr(chunk, "content", "")
            content_ar = getattr(chunk, "content_ar", "")

            if not content and hasattr(chunk, "content"):
                content = chunk.content

            if content:
                # Extract first meaningful sentence as treatment option
                sentences = content.split(". ")
                for sentence in sentences[:2]:
                    sentence = sentence.strip()
                    if len(sentence) > 20 and any(
                        keyword in sentence.lower()
                        for keyword in [
                            "apply", "treat", "spray", "remove", "use",
                            "control", "manage", "prevent", "inject",
                        ]
                    ):
                        treatment_options.append({
                            "en": sentence[:200],
                            "ar": content_ar[:200] if content_ar else "",
                        })
                        break

        return treatment_options[:5]

    def _generate_general_advisory(
        self,
        vision_result: VisionAnalysisResult,
        knowledge_result: VisionKnowledgeResult,
    ) -> tuple[str, str]:
        """Generate a general advisory summary combining vision + knowledge.
        توليد ملخص استشاري عام يجمع بين الرؤية والمعرفة"""
        crop = vision_result.crop_type.value
        health = vision_result.overall_health_score

        # Build summary based on health score and findings
        if health >= 0.8:
            summary_en = (
                f"Crop ({crop}) appears healthy with overall health score {health:.0%}. "
                "Continue regular monitoring and maintenance."
            )
            summary_ar = (
                f"المحصول ({crop}) يبدو بصحة جيدة مع درجة صحة عامة {health:.0%}. "
                "استمر في المراقبة والصيانة المنتظمة."
            )
        elif health >= 0.5:
            issues = []
            issues_ar = []
            for rec in knowledge_result.disease_recommendations:
                issues.append(f"{rec.metadata.get('disease_type', 'unknown')} ({rec.severity})")
                issues_ar.append(f"{rec.metadata.get('disease_type', 'غير معروف')} ({rec.severity})")
            for rec in knowledge_result.pest_recommendations:
                issues.append(f"{rec.metadata.get('pest_type', 'unknown')} ({rec.severity})")
                issues_ar.append(f"{rec.metadata.get('pest_type', 'غير معروف')} ({rec.severity})")

            issue_list = ", ".join(issues) if issues else "minor issues"
            issue_list_ar = "، ".join(issues_ar) if issues_ar else "مشاكل بسيطة"

            summary_en = (
                f"Crop ({crop}) shows moderate health ({health:.0%}). "
                f"Issues detected: {issue_list}. "
                "Review treatment recommendations and act within 24-48 hours."
            )
            summary_ar = (
                f"المحصول ({crop}) يظهر صحة متوسطة ({health:.0%}). "
                f"المشاكل المكتشفة: {issue_list_ar}. "
                "راجع توصيات العلاج وتصرف خلال 24-48 ساعة."
            )
        else:
            summary_en = (
                f"ALERT: Crop ({crop}) health is critical ({health:.0%}). "
                "Immediate action required. Review all treatment recommendations below."
            )
            summary_ar = (
                f"تنبيه: صحة المحصول ({crop}) حرجة ({health:.0%}). "
                "إجراء فوري مطلوب. راجع جميع توصيات العلاج أدناه."
            )

        # Add knowledge confidence note
        if knowledge_result.total_citations > 0:
            summary_en += (
                f" ({knowledge_result.total_citations} knowledge base citations, "
                f"confidence: {knowledge_result.knowledge_confidence:.0%})"
            )
            summary_ar += (
                f" ({knowledge_result.total_citations} اقتباسات من قاعدة المعرفة، "
                f"الثقة: {knowledge_result.knowledge_confidence:.0%})"
            )

        return summary_en, summary_ar


# Export classes
__all__ = [
    "EnrichedRecommendation",
    "KnowledgeCitation",
    "VisionKnowledgeBridge",
    "VisionKnowledgeResult",
]
