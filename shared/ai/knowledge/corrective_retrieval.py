# ═══════════════════════════════════════════════════════════════════════════════
# Corrective Retrieval Augmented Generation (CRAG)
# الاسترجاع التصحيحي المعزز للتوليد
# ═══════════════════════════════════════════════════════════════════════════════
#
# Based on CRAG (arXiv:2401.15884):
#   - Lightweight retrieval evaluator scores relevance of retrieved documents
#   - Three actions: CORRECT (use as-is), AMBIGUOUS (refine), INCORRECT (fallback)
#   - Knowledge refinement strips irrelevant sentences from retrieved chunks
#   - Fallback to broader knowledge base search when retrieval quality is low
#
# Also incorporates patterns from:
#   - AgriRegion (arXiv:2512.10114): region-aware re-ranking
#   - AgroAskAI (arXiv:2512.14910): reviewer agent pattern
#   - RAGOps (arXiv:2506.03401): pipeline monitoring
#
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class RetrievalAction(StrEnum):
    """Action to take based on retrieval quality evaluation."""

    CORRECT = "correct"  # Retrieved docs are relevant - use directly
    AMBIGUOUS = "ambiguous"  # Partially relevant - refine and supplement
    INCORRECT = "incorrect"  # Not relevant - fallback to broader search


class ConfidenceLevel(StrEnum):
    """Confidence in the retrieval quality."""

    HIGH = "high"  # Score >= 0.7
    MEDIUM = "medium"  # Score 0.4 - 0.7
    LOW = "low"  # Score < 0.4


@dataclass
class RetrievalEvaluation:
    """Result of evaluating retrieved document relevance."""

    action: RetrievalAction
    confidence: ConfidenceLevel
    relevance_score: float = 0.0
    region_score: float = 0.0
    freshness_score: float = 0.0
    overall_score: float = 0.0
    reasoning: str = ""
    reasoning_ar: str = ""


@dataclass
class RefinedChunk:
    """A knowledge chunk after CRAG refinement."""

    content: str
    content_ar: str = ""
    relevance_score: float = 0.0
    source: str = ""
    collection: str = ""
    agrovoc_concepts: list[str] = field(default_factory=list)
    region_relevance: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CRAGResult:
    """Complete result of the CRAG pipeline."""

    action_taken: RetrievalAction
    evaluation: RetrievalEvaluation
    refined_chunks: list[RefinedChunk] = field(default_factory=list)
    fallback_used: bool = False
    fallback_source: str = ""
    total_chunks_input: int = 0
    total_chunks_output: int = 0
    refinement_ratio: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action_taken.value,
            "confidence": self.evaluation.confidence.value,
            "overall_score": self.evaluation.overall_score,
            "chunks_in": self.total_chunks_input,
            "chunks_out": self.total_chunks_output,
            "refinement_ratio": round(self.refinement_ratio, 3),
            "fallback_used": self.fallback_used,
        }


class CorrectiveRetrievalEngine:
    """CRAG-based engine for evaluating and refining retrieved knowledge chunks.

    Implements the three-action corrective retrieval pattern:
    1. CORRECT: High-quality retrieval → use documents directly
    2. AMBIGUOUS: Mixed quality → refine chunks, remove irrelevant sentences
    3. INCORRECT: Poor quality → fallback to broader collections or web search

    Features:
    - Agricultural domain-aware relevance scoring
    - Region-aware evaluation (AgriRegion pattern)
    - Freshness scoring for time-sensitive agricultural advice
    - Knowledge refinement (sentence-level filtering)
    - Bilingual (AR/EN) support
    """

    # Relevance thresholds
    CORRECT_THRESHOLD = 0.7
    AMBIGUOUS_THRESHOLD = 0.4

    # Domain-specific relevance keywords (weighted)
    _DOMAIN_SIGNALS: dict[str, list[str]] = {
        "crops": ["variety", "cultivar", "growth stage", "yield", "harvest", "صنف", "محصول", "حصاد"],
        "irrigation": ["water", "moisture", "ET", "drip", "schedule", "ري", "رطوبة", "تنقيط"],
        "pest_disease": ["pest", "disease", "insect", "fungus", "treatment", "آفة", "مرض", "مكافحة"],
        "fertilizer": ["nitrogen", "phosphorus", "potassium", "urea", "NPK", "سماد", "نيتروجين"],
        "soil": ["pH", "EC", "organic matter", "texture", "drainage", "تربة", "حموضة"],
        "weather": ["temperature", "rainfall", "frost", "drought", "wind", "حرارة", "أمطار", "جفاف"],
        "remote_sensing": ["NDVI", "satellite", "Sentinel", "LAI", "spectral", "استشعار عن بعد", "قمر صناعي"],
        "smart_agriculture": ["IoT", "drone", "sensor", "blockchain", "edge", "إنترنت الأشياء", "مزرعة ذكية"],
        "precision_farming": ["VRA", "variable rate", "GPS", "RTK", "yield map", "زراعة دقيقة", "معدل متغير"],
        "digital_twin": ["digital twin", "simulation", "virtual model", "3D", "توأم رقمي", "محاكاة", "نموذج افتراضي"],
    }

    # Safety-critical keywords that boost relevance for safety queries
    _SAFETY_SIGNALS = [
        "PHI", "pre-harvest interval", "re-entry interval", "REI",
        "toxicity", "LD50", "banned", "restricted",
        "فترة ما قبل الحصاد", "سمية", "محظور", "مقيد",
    ]

    def __init__(
        self,
        correct_threshold: float = 0.7,
        ambiguous_threshold: float = 0.4,
        max_refined_chunks: int = 10,
        min_sentence_relevance: float = 0.3,
    ) -> None:
        self.CORRECT_THRESHOLD = correct_threshold
        self.AMBIGUOUS_THRESHOLD = ambiguous_threshold
        self._max_refined = max_refined_chunks
        self._min_sentence_relevance = min_sentence_relevance

    def evaluate_and_refine(
        self,
        query: str,
        retrieved_chunks: list[dict[str, Any]],
        query_domain: str = "",
        target_region: str = "",
    ) -> CRAGResult:
        """Main CRAG pipeline: evaluate retrieval quality and refine chunks.

        Args:
            query: The user's agricultural query (EN or AR)
            retrieved_chunks: List of chunks from vector store retrieval
            query_domain: Detected domain of the query (crops, irrigation, etc.)
            target_region: Target region for region-aware scoring

        Returns:
            CRAGResult with action taken, refined chunks, and metadata
        """
        result = CRAGResult(
            action_taken=RetrievalAction.CORRECT,
            evaluation=RetrievalEvaluation(
                action=RetrievalAction.CORRECT,
                confidence=ConfidenceLevel.HIGH,
            ),
            total_chunks_input=len(retrieved_chunks),
        )

        if not retrieved_chunks:
            result.action_taken = RetrievalAction.INCORRECT
            result.evaluation.action = RetrievalAction.INCORRECT
            result.evaluation.confidence = ConfidenceLevel.LOW
            result.evaluation.overall_score = 0.0
            result.fallback_used = True
            result.fallback_source = "empty_retrieval"
            return result

        # Step 1: Evaluate retrieval quality
        evaluation = self._evaluate_retrieval(query, retrieved_chunks, query_domain, target_region)
        result.evaluation = evaluation
        result.action_taken = evaluation.action

        # Step 2: Take action based on evaluation
        if evaluation.action == RetrievalAction.CORRECT:
            # High quality → use chunks with light filtering
            result.refined_chunks = self._light_refine(query, retrieved_chunks, query_domain)

        elif evaluation.action == RetrievalAction.AMBIGUOUS:
            # Mixed quality → aggressive refinement
            result.refined_chunks = self._deep_refine(query, retrieved_chunks, query_domain)
            if len(result.refined_chunks) < 2:
                result.fallback_used = True
                result.fallback_source = "insufficient_after_refinement"

        else:  # INCORRECT
            # Poor quality → mark for fallback
            result.fallback_used = True
            result.fallback_source = "low_relevance"
            # Still try to salvage any usable content
            result.refined_chunks = self._salvage_refine(query, retrieved_chunks, query_domain)

        result.total_chunks_output = len(result.refined_chunks)
        if result.total_chunks_input > 0:
            result.refinement_ratio = result.total_chunks_output / result.total_chunks_input

        logger.info(
            "crag_pipeline_complete",
            action=result.action_taken.value,
            confidence=result.evaluation.confidence.value,
            score=round(result.evaluation.overall_score, 3),
            chunks_in=result.total_chunks_input,
            chunks_out=result.total_chunks_output,
            fallback=result.fallback_used,
        )

        return result

    # ─── Evaluation ───────────────────────────────────────────────────────────

    def _evaluate_retrieval(
        self,
        query: str,
        chunks: list[dict[str, Any]],
        query_domain: str,
        target_region: str,
    ) -> RetrievalEvaluation:
        """Evaluate overall retrieval quality."""
        # Score each chunk
        chunk_scores = []
        for chunk in chunks:
            score = self._score_chunk_relevance(query, chunk, query_domain)
            chunk_scores.append(score)

        if not chunk_scores:
            return RetrievalEvaluation(
                action=RetrievalAction.INCORRECT,
                confidence=ConfidenceLevel.LOW,
            )

        # Aggregate scores
        avg_score = sum(chunk_scores) / len(chunk_scores)
        max_score = max(chunk_scores)
        top_3_avg = sum(sorted(chunk_scores, reverse=True)[:3]) / min(3, len(chunk_scores))

        # Region scoring
        region_score = self._score_region_relevance(chunks, target_region) if target_region else 0.5

        # Freshness scoring
        freshness_score = self._score_freshness(chunks)

        # Weighted overall score
        overall = (
            0.45 * top_3_avg
            + 0.25 * avg_score
            + 0.15 * region_score
            + 0.10 * freshness_score
            + 0.05 * (max_score - avg_score)  # Bonus for having at least one great match
        )

        # Determine action
        if overall >= self.CORRECT_THRESHOLD:
            action = RetrievalAction.CORRECT
            confidence = ConfidenceLevel.HIGH
        elif overall >= self.AMBIGUOUS_THRESHOLD:
            action = RetrievalAction.AMBIGUOUS
            confidence = ConfidenceLevel.MEDIUM
        else:
            action = RetrievalAction.INCORRECT
            confidence = ConfidenceLevel.LOW

        return RetrievalEvaluation(
            action=action,
            confidence=confidence,
            relevance_score=top_3_avg,
            region_score=region_score,
            freshness_score=freshness_score,
            overall_score=overall,
        )

    def _score_chunk_relevance(
        self, query: str, chunk: dict[str, Any], query_domain: str
    ) -> float:
        """Score a single chunk's relevance to the query."""
        content = chunk.get("content", "") or chunk.get("text", "")
        metadata = chunk.get("metadata", {})

        if not content:
            return 0.0

        score = 0.0
        query_lower = query.lower()
        content_lower = content.lower()

        # 1. Term overlap (word-level)
        query_words = set(query_lower.split())
        content_words = set(content_lower.split())
        if query_words:
            overlap = len(query_words & content_words) / len(query_words)
            score += 0.3 * overlap

        # 2. Domain signal matching
        if query_domain and query_domain in self._DOMAIN_SIGNALS:
            signals = self._DOMAIN_SIGNALS[query_domain]
            signal_hits = sum(1 for s in signals if s.lower() in content_lower)
            score += 0.25 * min(1.0, signal_hits / max(3, len(signals) * 0.3))

        # 3. Metadata domain alignment
        chunk_domain = metadata.get("domain", "")
        if chunk_domain and query_domain:
            if chunk_domain == query_domain:
                score += 0.2
            elif chunk_domain in ("general", "general_agriculture"):
                score += 0.05

        # 4. Source credibility bonus
        credibility = metadata.get("source_credibility", 1)
        if isinstance(credibility, (int, float)):
            score += 0.1 * min(1.0, credibility / 5.0)

        # 5. AGROVOC concept alignment
        agrovoc = metadata.get("agrovoc_concepts", [])
        if agrovoc:
            score += 0.05

        # 6. Safety-critical boost
        if any(s.lower() in query_lower for s in self._SAFETY_SIGNALS):
            if any(s.lower() in content_lower for s in self._SAFETY_SIGNALS):
                score += 0.1

        return min(1.0, score)

    def _score_region_relevance(self, chunks: list[dict[str, Any]], target_region: str) -> float:
        """Score how well chunks match the target region."""
        if not target_region:
            return 0.5

        region_lower = target_region.lower()
        regional_chunks = 0
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            regions = metadata.get("applicable_regions", [])
            geo = metadata.get("geospatial", {})
            if isinstance(geo, dict):
                regions = regions or geo.get("applicable_regions", [])

            if any(region_lower in r.lower() for r in regions):
                regional_chunks += 1
            elif not regions:
                regional_chunks += 0.3  # General content gets partial credit

        return min(1.0, regional_chunks / max(1, len(chunks)))

    def _score_freshness(self, chunks: list[dict[str, Any]]) -> float:
        """Score the freshness/recency of retrieved chunks."""
        from datetime import datetime

        now = datetime.utcnow()
        freshness_scores = []

        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            fresh = metadata.get("fresh", {})
            exp_date = fresh.get("expiration_date") if isinstance(fresh, dict) else None

            if exp_date:
                try:
                    if isinstance(exp_date, str):
                        exp = datetime.fromisoformat(exp_date)
                    else:
                        exp = exp_date
                    days_until_expiry = (exp - now).days
                    if days_until_expiry < 0:
                        freshness_scores.append(0.2)  # Expired but might still be useful
                    elif days_until_expiry < 90:
                        freshness_scores.append(0.6)
                    else:
                        freshness_scores.append(1.0)
                except (ValueError, TypeError):
                    freshness_scores.append(0.5)
            else:
                freshness_scores.append(0.5)  # Unknown freshness

        return sum(freshness_scores) / max(1, len(freshness_scores))

    # ─── Refinement ───────────────────────────────────────────────────────────

    def _light_refine(
        self, query: str, chunks: list[dict[str, Any]], query_domain: str
    ) -> list[RefinedChunk]:
        """Light refinement for high-quality retrievals - keep most content."""
        refined = []
        for chunk in chunks[:self._max_refined]:
            content = chunk.get("content", "") or chunk.get("text", "")
            content_ar = chunk.get("content_ar", "")
            metadata = chunk.get("metadata", {})

            score = self._score_chunk_relevance(query, chunk, query_domain)
            if score < 0.1:
                continue

            refined.append(RefinedChunk(
                content=content,
                content_ar=content_ar,
                relevance_score=score,
                source=metadata.get("source", chunk.get("source", "")),
                collection=metadata.get("collection", chunk.get("collection", "")),
                agrovoc_concepts=metadata.get("agrovoc_concepts", []),
                region_relevance=metadata.get("region_relevance", {}).get("overall_score", 0.5)
                if isinstance(metadata.get("region_relevance"), dict)
                else 0.5,
                metadata=metadata,
            ))

        refined.sort(key=lambda r: r.relevance_score, reverse=True)
        return refined

    def _deep_refine(
        self, query: str, chunks: list[dict[str, Any]], query_domain: str
    ) -> list[RefinedChunk]:
        """Deep refinement for ambiguous retrievals - filter at sentence level."""
        refined = []
        query_lower = query.lower()
        query_words = set(query_lower.split())

        for chunk in chunks:
            content = chunk.get("content", "") or chunk.get("text", "")
            metadata = chunk.get("metadata", {})

            if not content:
                continue

            # Sentence-level filtering
            sentences = self._split_sentences(content)
            relevant_sentences = []

            for sentence in sentences:
                sentence_lower = sentence.lower()
                sentence_words = set(sentence_lower.split())

                # Score sentence relevance
                word_overlap = len(query_words & sentence_words) / max(1, len(query_words))

                domain_signal = 0.0
                if query_domain and query_domain in self._DOMAIN_SIGNALS:
                    signals = self._DOMAIN_SIGNALS[query_domain]
                    hits = sum(1 for s in signals if s.lower() in sentence_lower)
                    domain_signal = hits / max(1, len(signals))

                sentence_score = 0.5 * word_overlap + 0.5 * domain_signal

                if sentence_score >= self._min_sentence_relevance:
                    relevant_sentences.append(sentence)

            if relevant_sentences:
                refined_content = " ".join(relevant_sentences)
                chunk_score = self._score_chunk_relevance(query, chunk, query_domain)

                refined.append(RefinedChunk(
                    content=refined_content,
                    content_ar=chunk.get("content_ar", ""),
                    relevance_score=chunk_score,
                    source=metadata.get("source", ""),
                    collection=metadata.get("collection", ""),
                    agrovoc_concepts=metadata.get("agrovoc_concepts", []),
                    metadata=metadata,
                ))

        refined.sort(key=lambda r: r.relevance_score, reverse=True)
        return refined[:self._max_refined]

    def _salvage_refine(
        self, query: str, chunks: list[dict[str, Any]], query_domain: str
    ) -> list[RefinedChunk]:
        """Salvage any usable content from low-quality retrievals."""
        refined = []
        for chunk in chunks:
            score = self._score_chunk_relevance(query, chunk, query_domain)
            if score >= 0.2:  # Very low bar - just salvage what we can
                content = chunk.get("content", "") or chunk.get("text", "")
                metadata = chunk.get("metadata", {})
                refined.append(RefinedChunk(
                    content=content,
                    relevance_score=score,
                    source=metadata.get("source", ""),
                    collection=metadata.get("collection", ""),
                    metadata=metadata,
                ))

        refined.sort(key=lambda r: r.relevance_score, reverse=True)
        return refined[:3]  # Only keep top 3 salvaged chunks

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences, handling both English and Arabic."""
        import re

        # Split on sentence-ending punctuation
        sentences = re.split(r'[.!?؟。]\s+', text)
        # Filter very short sentences (likely artifacts)
        return [s.strip() for s in sentences if len(s.strip()) > 20]

    # ─── Fallback Collection Suggestions ──────────────────────────────────────

    def suggest_fallback_collections(
        self, query_domain: str, current_collection: str
    ) -> list[str]:
        """Suggest alternative collections to search when retrieval fails."""
        from .collections import (
            CROP_KNOWLEDGE,
            CROP_WATER_REQUIREMENTS,
            FERTILIZER_KNOWLEDGE,
            GENERAL_AGRICULTURE,
            IRRIGATION_PRACTICES,
            PEST_KNOWLEDGE,
            SOIL_KNOWLEDGE,
            WEATHER_KNOWLEDGE,
        )

        # Domain-to-fallback mapping (ordered by relevance)
        fallback_map: dict[str, list[str]] = {
            "crops": [PEST_KNOWLEDGE, FERTILIZER_KNOWLEDGE, IRRIGATION_PRACTICES, GENERAL_AGRICULTURE],
            "irrigation": [CROP_WATER_REQUIREMENTS, SOIL_KNOWLEDGE, WEATHER_KNOWLEDGE, GENERAL_AGRICULTURE],
            "pest_disease": [CROP_KNOWLEDGE, GENERAL_AGRICULTURE],
            "fertilizer": [SOIL_KNOWLEDGE, CROP_KNOWLEDGE, GENERAL_AGRICULTURE],
            "soil": [FERTILIZER_KNOWLEDGE, IRRIGATION_PRACTICES, GENERAL_AGRICULTURE],
            "weather": [CROP_KNOWLEDGE, IRRIGATION_PRACTICES, GENERAL_AGRICULTURE],
            "remote_sensing": [CROP_KNOWLEDGE, GENERAL_AGRICULTURE],
            "smart_agriculture": [CROP_KNOWLEDGE, IRRIGATION_PRACTICES, GENERAL_AGRICULTURE],
            "precision_farming": [CROP_KNOWLEDGE, IRRIGATION_PRACTICES, GENERAL_AGRICULTURE],
            "digital_twin": [CROP_KNOWLEDGE, IRRIGATION_PRACTICES, GENERAL_AGRICULTURE],
            "general": [CROP_KNOWLEDGE, IRRIGATION_PRACTICES, PEST_KNOWLEDGE],
        }

        suggestions = fallback_map.get(query_domain, [GENERAL_AGRICULTURE])
        return [s for s in suggestions if s != current_collection]
