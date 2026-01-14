"""
AI Recommendation Evaluation Module
=====================================
وحدة تقييم توصيات الذكاء الاصطناعي

Implements LLM-as-Judge pattern for evaluating AI recommendations.
Provides structured evaluation across multiple criteria for agricultural advice.

المميزات:
- تقييم الدقة والموثوقية
- تقييم قابلية التنفيذ
- تقييم السلامة
- تقييم الصلة بالسياق الزراعي

Based on LLM-as-Judge best practices for agricultural domain.

Author: SAHOOL Platform Team
Updated: January 2025
"""

from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Constants & Configuration
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_PASSING_THRESHOLD = 0.7
MIN_SCORE = 0.0
MAX_SCORE = 1.0


# ─────────────────────────────────────────────────────────────────────────────
# Enums & Models
# ─────────────────────────────────────────────────────────────────────────────


class EvaluationCriteria(str, Enum):
    """
    Evaluation criteria for recommendations.
    معايير تقييم التوصيات

    Attributes:
        ACCURACY: الدقة - Technical correctness
        ACTIONABILITY: قابلية التنفيذ - Can be acted upon
        SAFETY: السلامة - Safe for implementation
        RELEVANCE: الصلة - Relevant to context
        COMPLETENESS: الاكتمال - Covers all aspects
        CLARITY: الوضوح - Clear and understandable
    """

    ACCURACY = "accuracy"  # الدقة
    ACTIONABILITY = "actionability"  # قابلية التنفيذ
    SAFETY = "safety"  # السلامة
    RELEVANCE = "relevance"  # الصلة
    COMPLETENESS = "completeness"  # الاكتمال
    CLARITY = "clarity"  # الوضوح


class EvaluationGrade(str, Enum):
    """
    Overall grade for evaluation.
    الدرجة الإجمالية للتقييم
    """

    EXCELLENT = "excellent"  # ممتاز (>= 0.9)
    GOOD = "good"  # جيد (>= 0.75)
    ACCEPTABLE = "acceptable"  # مقبول (>= 0.6)
    NEEDS_IMPROVEMENT = "needs_improvement"  # يحتاج تحسين (>= 0.4)
    POOR = "poor"  # ضعيف (< 0.4)


class RecommendationType(str, Enum):
    """
    Type of agricultural recommendation.
    نوع التوصية الزراعية
    """

    IRRIGATION = "irrigation"  # الري
    FERTILIZATION = "fertilization"  # التسميد
    PEST_CONTROL = "pest_control"  # مكافحة الآفات
    DISEASE = "disease"  # الأمراض
    HARVEST = "harvest"  # الحصاد
    PLANTING = "planting"  # الزراعة
    WEATHER = "weather"  # الطقس
    GENERAL = "general"  # عام


@dataclass
class CriteriaScore:
    """
    Score for a single evaluation criterion.
    درجة معيار تقييم واحد

    Attributes:
        criteria: المعيار - The evaluation criterion
        score: الدرجة - Score from 0.0 to 1.0
        explanation: التفسير - Explanation for the score
        explanation_ar: التفسير بالعربية - Arabic explanation
        evidence: الأدلة - Evidence supporting the score
    """

    criteria: EvaluationCriteria
    score: float
    explanation: str
    explanation_ar: str = ""
    evidence: list[str] = field(default_factory=list)

    def __post_init__(self):
        # Clamp score to valid range
        self.score = max(MIN_SCORE, min(MAX_SCORE, self.score))

    @property
    def is_passing(self) -> bool:
        """Check if score passes threshold / التحقق من اجتياز العتبة"""
        return self.score >= DEFAULT_PASSING_THRESHOLD

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary / التحويل إلى قاموس"""
        return {
            "criteria": self.criteria.value,
            "score": self.score,
            "explanation": self.explanation,
            "explanation_ar": self.explanation_ar,
            "evidence": self.evidence,
            "is_passing": self.is_passing,
        }


@dataclass
class EvaluationResult:
    """
    Complete evaluation result.
    نتيجة التقييم الكاملة

    Attributes:
        id: المعرف - Unique evaluation identifier
        recommendation_id: معرف التوصية - ID of evaluated recommendation
        recommendation_type: نوع التوصية - Type of recommendation
        scores: الدرجات - Individual criteria scores
        overall_score: الدرجة الإجمالية - Weighted overall score
        grade: الدرجة - Letter grade
        is_approved: موافق عليها - Whether recommendation is approved
        feedback: الملاحظات - General feedback
        feedback_ar: الملاحظات بالعربية - Arabic feedback
        improvements: التحسينات المقترحة - Suggested improvements
        evaluated_at: تاريخ التقييم - Evaluation timestamp
        metadata: البيانات الوصفية - Additional metadata
    """

    id: str
    recommendation_id: str | None
    recommendation_type: RecommendationType
    scores: dict[EvaluationCriteria, CriteriaScore]
    overall_score: float
    grade: EvaluationGrade
    is_approved: bool
    feedback: str
    feedback_ar: str
    improvements: list[str]
    evaluated_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        recommendation_type: RecommendationType,
        scores: dict[EvaluationCriteria, CriteriaScore],
        weights: dict[EvaluationCriteria, float] | None = None,
        recommendation_id: str | None = None,
        passing_threshold: float = DEFAULT_PASSING_THRESHOLD,
    ) -> EvaluationResult:
        """
        Factory method to create evaluation result.
        طريقة إنشاء نتيجة التقييم

        Args:
            recommendation_type: نوع التوصية - Type of recommendation
            scores: الدرجات - Criteria scores
            weights: الأوزان - Optional criteria weights
            recommendation_id: معرف التوصية - Optional recommendation ID
            passing_threshold: عتبة النجاح - Score threshold for approval

        Returns:
            EvaluationResult: نتيجة التقييم - Evaluation result
        """
        # Default weights for agricultural recommendations
        default_weights = {
            EvaluationCriteria.ACCURACY: 0.25,
            EvaluationCriteria.ACTIONABILITY: 0.20,
            EvaluationCriteria.SAFETY: 0.25,
            EvaluationCriteria.RELEVANCE: 0.15,
            EvaluationCriteria.COMPLETENESS: 0.10,
            EvaluationCriteria.CLARITY: 0.05,
        }
        weights = weights or default_weights

        # Calculate weighted overall score
        total_weight = 0.0
        weighted_sum = 0.0

        for criteria, score in scores.items():
            weight = weights.get(criteria, 0.1)
            weighted_sum += score.score * weight
            total_weight += weight

        overall_score = weighted_sum / max(total_weight, 0.01)

        # Determine grade
        grade = cls._score_to_grade(overall_score)

        # Check safety - if safety score is low, do not approve
        safety_score = scores.get(EvaluationCriteria.SAFETY)
        safety_failed = safety_score and safety_score.score < 0.5

        is_approved = overall_score >= passing_threshold and not safety_failed

        # Generate feedback
        feedback, feedback_ar = cls._generate_feedback(scores, grade, is_approved)

        # Generate improvements
        improvements = cls._generate_improvements(scores)

        return cls(
            id=str(uuid4()),
            recommendation_id=recommendation_id,
            recommendation_type=recommendation_type,
            scores=scores,
            overall_score=overall_score,
            grade=grade,
            is_approved=is_approved,
            feedback=feedback,
            feedback_ar=feedback_ar,
            improvements=improvements,
            evaluated_at=datetime.now(UTC),
        )

    @staticmethod
    def _score_to_grade(score: float) -> EvaluationGrade:
        """Convert score to grade"""
        if score >= 0.9:
            return EvaluationGrade.EXCELLENT
        elif score >= 0.75:
            return EvaluationGrade.GOOD
        elif score >= 0.6:
            return EvaluationGrade.ACCEPTABLE
        elif score >= 0.4:
            return EvaluationGrade.NEEDS_IMPROVEMENT
        else:
            return EvaluationGrade.POOR

    @staticmethod
    def _generate_feedback(
        scores: dict[EvaluationCriteria, CriteriaScore],
        grade: EvaluationGrade,
        is_approved: bool,
    ) -> tuple[str, str]:
        """Generate feedback text in English and Arabic"""
        if is_approved:
            if grade == EvaluationGrade.EXCELLENT:
                return (
                    "Excellent recommendation. Ready for implementation.",
                    "توصية ممتازة. جاهزة للتنفيذ.",
                )
            elif grade == EvaluationGrade.GOOD:
                return (
                    "Good recommendation with minor areas for improvement.",
                    "توصية جيدة مع بعض المجالات للتحسين.",
                )
            else:
                return (
                    "Acceptable recommendation. Consider the suggested improvements.",
                    "توصية مقبولة. يُرجى النظر في التحسينات المقترحة.",
                )
        else:
            safety_score = scores.get(EvaluationCriteria.SAFETY)
            if safety_score and safety_score.score < 0.5:
                return (
                    "Recommendation not approved due to safety concerns. "
                    "Please review safety guidelines.",
                    "لم تتم الموافقة على التوصية بسبب مخاوف تتعلق بالسلامة. "
                    "يرجى مراجعة إرشادات السلامة.",
                )
            else:
                return (
                    "Recommendation needs improvement before implementation. "
                    "Please address the noted concerns.",
                    "التوصية تحتاج إلى تحسين قبل التنفيذ. "
                    "يرجى معالجة الملاحظات المذكورة.",
                )

    @staticmethod
    def _generate_improvements(
        scores: dict[EvaluationCriteria, CriteriaScore],
    ) -> list[str]:
        """Generate list of suggested improvements"""
        improvements = []

        for criteria, score in scores.items():
            if score.score < DEFAULT_PASSING_THRESHOLD:
                improvement_map = {
                    EvaluationCriteria.ACCURACY: "Verify technical accuracy with domain experts",
                    EvaluationCriteria.ACTIONABILITY: "Provide more specific, actionable steps",
                    EvaluationCriteria.SAFETY: "Review safety implications and add precautions",
                    EvaluationCriteria.RELEVANCE: "Ensure recommendation addresses the specific context",
                    EvaluationCriteria.COMPLETENESS: "Add missing details or considerations",
                    EvaluationCriteria.CLARITY: "Simplify language and improve structure",
                }
                if criteria in improvement_map:
                    improvements.append(improvement_map[criteria])

        return improvements

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary / التحويل إلى قاموس"""
        return {
            "id": self.id,
            "recommendation_id": self.recommendation_id,
            "recommendation_type": self.recommendation_type.value,
            "scores": {k.value: v.to_dict() for k, v in self.scores.items()},
            "overall_score": self.overall_score,
            "grade": self.grade.value,
            "is_approved": self.is_approved,
            "feedback": self.feedback,
            "feedback_ar": self.feedback_ar,
            "improvements": self.improvements,
            "evaluated_at": self.evaluated_at.isoformat(),
            "metadata": self.metadata,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Evaluation Prompts
# ─────────────────────────────────────────────────────────────────────────────


class EvaluationPrompts:
    """
    Prompts for LLM-as-Judge evaluation.
    قوالب التقييم باستخدام نموذج اللغة كحكم
    """

    SYSTEM_PROMPT = """You are an expert agricultural advisor evaluating AI-generated recommendations for farmers in the Middle East.

Your role is to evaluate recommendations based on these criteria:
1. ACCURACY: Is the advice technically correct for the crop, region, and conditions?
2. ACTIONABILITY: Can the farmer realistically implement this advice?
3. SAFETY: Is the recommendation safe for crops, soil, water, and human health?
4. RELEVANCE: Does the advice address the farmer's specific situation?
5. COMPLETENESS: Are all necessary details included?
6. CLARITY: Is the advice easy to understand?

Consider the agricultural context of the Middle East:
- Arid/semi-arid climate conditions
- Water scarcity and irrigation challenges
- Local crop varieties (dates, wheat, vegetables)
- Traditional and modern farming practices
- Arabic language comprehension

Evaluate objectively and provide constructive feedback."""

    EVALUATION_TEMPLATE = """
Evaluate the following agricultural recommendation:

**User Context:**
{context}

**User Question/Request:**
{query}

**AI Recommendation:**
{recommendation}

**Recommendation Type:** {recommendation_type}

---

For each criterion, provide:
1. A score from 0.0 to 1.0
2. A brief explanation (1-2 sentences)
3. Key evidence from the recommendation

Format your response as JSON:
```json
{{
    "accuracy": {{
        "score": 0.0-1.0,
        "explanation": "...",
        "explanation_ar": "...",
        "evidence": ["..."]
    }},
    "actionability": {{
        "score": 0.0-1.0,
        "explanation": "...",
        "explanation_ar": "...",
        "evidence": ["..."]
    }},
    "safety": {{
        "score": 0.0-1.0,
        "explanation": "...",
        "explanation_ar": "...",
        "evidence": ["..."]
    }},
    "relevance": {{
        "score": 0.0-1.0,
        "explanation": "...",
        "explanation_ar": "...",
        "evidence": ["..."]
    }},
    "completeness": {{
        "score": 0.0-1.0,
        "explanation": "...",
        "explanation_ar": "...",
        "evidence": ["..."]
    }},
    "clarity": {{
        "score": 0.0-1.0,
        "explanation": "...",
        "explanation_ar": "...",
        "evidence": ["..."]
    }}
}}
```"""


# ─────────────────────────────────────────────────────────────────────────────
# Evaluator Base Class
# ─────────────────────────────────────────────────────────────────────────────


class BaseEvaluator(ABC):
    """
    Abstract base class for recommendation evaluators.
    الفئة الأساسية المجردة لمُقيّمي التوصيات
    """

    @abstractmethod
    def evaluate(
        self,
        recommendation: str,
        context: dict[str, Any] | None = None,
        query: str | None = None,
    ) -> EvaluationResult:
        """
        Evaluate a recommendation.
        تقييم توصية

        Args:
            recommendation: التوصية - The recommendation text
            context: السياق - Contextual information
            query: الاستعلام - Original user query

        Returns:
            EvaluationResult: نتيجة التقييم - Evaluation result
        """
        ...


# ─────────────────────────────────────────────────────────────────────────────
# Recommendation Evaluator
# ─────────────────────────────────────────────────────────────────────────────


class RecommendationEvaluator(BaseEvaluator):
    """
    LLM-as-Judge evaluator for agricultural recommendations.
    مُقيّم التوصيات الزراعية باستخدام نموذج اللغة كحكم

    Evaluates AI-generated recommendations for farmers using multiple criteria:
    - Accuracy: Technical correctness
    - Actionability: Practical implementation feasibility
    - Safety: Risk assessment for crops, environment, health
    - Relevance: Context appropriateness
    - Completeness: Coverage of necessary information
    - Clarity: Understandability

    يُقيّم التوصيات الزراعية المُولَّدة بالذكاء الاصطناعي باستخدام معايير متعددة:
    - الدقة: الصحة التقنية
    - قابلية التنفيذ: إمكانية التطبيق العملي
    - السلامة: تقييم المخاطر على المحاصيل والبيئة والصحة
    - الصلة: ملاءمة السياق
    - الاكتمال: تغطية المعلومات الضرورية
    - الوضوح: سهولة الفهم

    Example:
        >>> evaluator = RecommendationEvaluator(llm_client=my_llm)
        >>> result = evaluator.evaluate(
        ...     recommendation="Apply 2kg/hectare of nitrogen fertilizer...",
        ...     context={"crop": "wheat", "field_size": 10},
        ...     query="How should I fertilize my wheat field?"
        ... )
        >>> print(f"Approved: {result.is_approved}, Grade: {result.grade}")

    المثال:
        >>> evaluator = RecommendationEvaluator(llm_client=my_llm)
        >>> result = evaluator.evaluate(
        ...     recommendation="ضع 2 كجم/هكتار من سماد النيتروجين...",
        ...     context={"crop": "قمح", "field_size": 10},
        ...     query="كيف أسمد حقل القمح؟"
        ... )
        >>> print(f"موافق عليها: {result.is_approved}, الدرجة: {result.grade}")
    """

    def __init__(
        self,
        llm_client: Any | None = None,
        criteria_weights: dict[EvaluationCriteria, float] | None = None,
        passing_threshold: float = DEFAULT_PASSING_THRESHOLD,
        use_heuristics_fallback: bool = True,
    ):
        """
        Initialize the evaluator.
        تهيئة المُقيّم

        Args:
            llm_client: عميل نموذج اللغة - LLM client for evaluation (optional)
            criteria_weights: أوزان المعايير - Custom weights for criteria
            passing_threshold: عتبة النجاح - Threshold for approval
            use_heuristics_fallback: استخدام القواعد الاحتياطية - Use heuristics if no LLM
        """
        self.llm_client = llm_client
        self.passing_threshold = passing_threshold
        self.use_heuristics_fallback = use_heuristics_fallback

        # Default weights optimized for agricultural recommendations
        self.criteria_weights = criteria_weights or {
            EvaluationCriteria.ACCURACY: 0.25,
            EvaluationCriteria.ACTIONABILITY: 0.20,
            EvaluationCriteria.SAFETY: 0.25,  # High weight for safety
            EvaluationCriteria.RELEVANCE: 0.15,
            EvaluationCriteria.COMPLETENESS: 0.10,
            EvaluationCriteria.CLARITY: 0.05,
        }

        # Statistics
        self._stats = {
            "evaluations": 0,
            "approved": 0,
            "rejected": 0,
            "llm_evaluations": 0,
            "heuristic_evaluations": 0,
        }

        logger.info(
            f"RecommendationEvaluator initialized with threshold={passing_threshold}, "
            f"llm_available={llm_client is not None}"
        )

    def evaluate(
        self,
        recommendation: str,
        context: dict[str, Any] | None = None,
        query: str | None = None,
        recommendation_type: RecommendationType | None = None,
        recommendation_id: str | None = None,
    ) -> EvaluationResult:
        """
        Evaluate a recommendation using LLM-as-Judge or heuristics.
        تقييم توصية باستخدام نموذج اللغة كحكم أو القواعد

        Args:
            recommendation: التوصية - The recommendation text to evaluate
            context: السياق - Contextual information (field data, weather, etc.)
            query: الاستعلام - Original user query
            recommendation_type: نوع التوصية - Type of recommendation
            recommendation_id: معرف التوصية - Optional ID for tracking

        Returns:
            EvaluationResult: نتيجة التقييم - Complete evaluation result

        Example:
            >>> result = evaluator.evaluate(
            ...     recommendation="Water your tomatoes every 2 days in summer",
            ...     context={"crop": "tomato", "season": "summer"},
            ...     query="When should I water my tomatoes?"
            ... )
        """
        context = context or {}
        query = query or ""
        recommendation_type = recommendation_type or self._detect_recommendation_type(
            recommendation
        )

        self._stats["evaluations"] += 1

        # Try LLM evaluation first
        if self.llm_client:
            try:
                scores = self._evaluate_with_llm(
                    recommendation=recommendation,
                    context=context,
                    query=query,
                    recommendation_type=recommendation_type,
                )
                self._stats["llm_evaluations"] += 1
            except Exception as e:
                logger.warning(f"LLM evaluation failed, using heuristics: {e}")
                if self.use_heuristics_fallback:
                    scores = self._evaluate_with_heuristics(
                        recommendation=recommendation,
                        context=context,
                        query=query,
                        recommendation_type=recommendation_type,
                    )
                    self._stats["heuristic_evaluations"] += 1
                else:
                    raise
        else:
            scores = self._evaluate_with_heuristics(
                recommendation=recommendation,
                context=context,
                query=query,
                recommendation_type=recommendation_type,
            )
            self._stats["heuristic_evaluations"] += 1

        # Create evaluation result
        result = EvaluationResult.create(
            recommendation_type=recommendation_type,
            scores=scores,
            weights=self.criteria_weights,
            recommendation_id=recommendation_id,
            passing_threshold=self.passing_threshold,
        )

        # Update stats
        if result.is_approved:
            self._stats["approved"] += 1
        else:
            self._stats["rejected"] += 1

        logger.info(
            f"Evaluated recommendation: type={recommendation_type.value}, "
            f"score={result.overall_score:.2f}, approved={result.is_approved}"
        )

        return result

    def evaluate_batch(
        self,
        recommendations: list[dict[str, Any]],
    ) -> list[EvaluationResult]:
        """
        Evaluate multiple recommendations.
        تقييم توصيات متعددة

        Args:
            recommendations: قائمة التوصيات - List of dicts with recommendation details
                Each dict should have: 'recommendation', 'context' (optional),
                'query' (optional), 'type' (optional), 'id' (optional)

        Returns:
            list[EvaluationResult]: قائمة نتائج التقييم - List of evaluation results
        """
        results = []

        for rec in recommendations:
            result = self.evaluate(
                recommendation=rec.get("recommendation", ""),
                context=rec.get("context"),
                query=rec.get("query"),
                recommendation_type=rec.get("type"),
                recommendation_id=rec.get("id"),
            )
            results.append(result)

        return results

    def get_stats(self) -> dict[str, Any]:
        """
        Get evaluation statistics.
        الحصول على إحصائيات التقييم

        Returns:
            dict: الإحصائيات - Evaluation statistics
        """
        total = self._stats["evaluations"]
        return {
            **self._stats,
            "approval_rate": self._stats["approved"] / max(total, 1),
            "rejection_rate": self._stats["rejected"] / max(total, 1),
        }

    # ─────────────────────────────────────────────────────────────────────────
    # LLM-based Evaluation
    # ─────────────────────────────────────────────────────────────────────────

    def _evaluate_with_llm(
        self,
        recommendation: str,
        context: dict[str, Any],
        query: str,
        recommendation_type: RecommendationType,
    ) -> dict[EvaluationCriteria, CriteriaScore]:
        """Evaluate using LLM-as-Judge pattern"""
        import json

        # Build evaluation prompt
        prompt = EvaluationPrompts.EVALUATION_TEMPLATE.format(
            context=json.dumps(context, ensure_ascii=False, indent=2),
            query=query,
            recommendation=recommendation,
            recommendation_type=recommendation_type.value,
        )

        # Call LLM
        response = self.llm_client.generate(
            system_prompt=EvaluationPrompts.SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        # Parse response
        return self._parse_llm_response(response)

    def _parse_llm_response(
        self,
        response: str,
    ) -> dict[EvaluationCriteria, CriteriaScore]:
        """Parse LLM response into scores"""
        import json
        import re

        # Extract JSON from response
        json_match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_str = response

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")

        scores = {}
        for criteria in EvaluationCriteria:
            criteria_data = data.get(criteria.value, {})
            scores[criteria] = CriteriaScore(
                criteria=criteria,
                score=float(criteria_data.get("score", 0.5)),
                explanation=criteria_data.get("explanation", "No explanation provided"),
                explanation_ar=criteria_data.get("explanation_ar", ""),
                evidence=criteria_data.get("evidence", []),
            )

        return scores

    # ─────────────────────────────────────────────────────────────────────────
    # Heuristic-based Evaluation
    # ─────────────────────────────────────────────────────────────────────────

    def _evaluate_with_heuristics(
        self,
        recommendation: str,
        context: dict[str, Any],
        query: str,
        recommendation_type: RecommendationType,
    ) -> dict[EvaluationCriteria, CriteriaScore]:
        """Evaluate using rule-based heuristics"""
        scores = {}

        # Accuracy heuristics
        scores[EvaluationCriteria.ACCURACY] = self._evaluate_accuracy_heuristic(
            recommendation, context, recommendation_type
        )

        # Actionability heuristics
        scores[EvaluationCriteria.ACTIONABILITY] = self._evaluate_actionability_heuristic(
            recommendation
        )

        # Safety heuristics
        scores[EvaluationCriteria.SAFETY] = self._evaluate_safety_heuristic(
            recommendation, recommendation_type
        )

        # Relevance heuristics
        scores[EvaluationCriteria.RELEVANCE] = self._evaluate_relevance_heuristic(
            recommendation, query, context
        )

        # Completeness heuristics
        scores[EvaluationCriteria.COMPLETENESS] = self._evaluate_completeness_heuristic(
            recommendation, recommendation_type
        )

        # Clarity heuristics
        scores[EvaluationCriteria.CLARITY] = self._evaluate_clarity_heuristic(recommendation)

        return scores

    def _evaluate_accuracy_heuristic(
        self,
        recommendation: str,
        context: dict[str, Any],
        recommendation_type: RecommendationType,
    ) -> CriteriaScore:
        """Evaluate accuracy using heuristics"""
        score = 0.7  # Base score
        evidence = []

        rec_lower = recommendation.lower()

        # Check for specific numbers/quantities (more specific = more accurate)
        import re

        numbers = re.findall(r"\d+(?:\.\d+)?", recommendation)
        if numbers:
            score += 0.1
            evidence.append(f"Contains specific quantities: {numbers[:3]}")

        # Check for units (kg, liters, mm, etc.)
        units = re.findall(
            r"\b(kg|كجم|liter|لتر|mm|مم|hectare|هكتار|m2|متر|hour|ساعة)\b",
            rec_lower,
        )
        if units:
            score += 0.1
            evidence.append(f"Contains measurement units: {list(set(units))}")

        # Check context alignment
        crop = context.get("crop", context.get("المحصول", ""))
        if crop and crop.lower() in rec_lower:
            score += 0.1
            evidence.append(f"Mentions relevant crop: {crop}")

        return CriteriaScore(
            criteria=EvaluationCriteria.ACCURACY,
            score=min(score, 1.0),
            explanation="Accuracy evaluated based on specificity and context alignment",
            explanation_ar="تم تقييم الدقة بناءً على التحديد والتوافق مع السياق",
            evidence=evidence,
        )

    def _evaluate_actionability_heuristic(
        self,
        recommendation: str,
    ) -> CriteriaScore:
        """Evaluate actionability using heuristics"""
        score = 0.6  # Base score
        evidence = []

        rec_lower = recommendation.lower()

        # Check for action verbs
        action_verbs = [
            "apply",
            "water",
            "spray",
            "add",
            "remove",
            "harvest",
            "plant",
            "irrigate",
            "fertilize",
            "prune",
            # Arabic
            "ضع",
            "اسقِ",
            "رش",
            "أضف",
            "أزل",
            "احصد",
            "ازرع",
            "سمّد",
        ]
        found_verbs = [v for v in action_verbs if v in rec_lower]
        if found_verbs:
            score += 0.15
            evidence.append(f"Contains action verbs: {found_verbs[:3]}")

        # Check for time references
        time_refs = [
            "morning",
            "evening",
            "daily",
            "weekly",
            "hours",
            "days",
            "صباحاً",
            "مساءً",
            "يومياً",
            "أسبوعياً",
        ]
        found_times = [t for t in time_refs if t in rec_lower]
        if found_times:
            score += 0.15
            evidence.append(f"Contains timing guidance: {found_times[:3]}")

        # Check for step-by-step indicators
        step_indicators = re.findall(
            r"(\d+\.\s|\bstep\s+\d|\bأولاً|\bثانياً|\bثالثاً)", rec_lower
        )
        if step_indicators:
            score += 0.1
            evidence.append("Contains step-by-step instructions")

        return CriteriaScore(
            criteria=EvaluationCriteria.ACTIONABILITY,
            score=min(score, 1.0),
            explanation="Actionability evaluated based on action verbs and timing guidance",
            explanation_ar="تم تقييم قابلية التنفيذ بناءً على أفعال العمل وإرشادات التوقيت",
            evidence=evidence,
        )

    def _evaluate_safety_heuristic(
        self,
        recommendation: str,
        recommendation_type: RecommendationType,
    ) -> CriteriaScore:
        """Evaluate safety using heuristics"""
        score = 0.8  # Start optimistic
        evidence = []

        rec_lower = recommendation.lower()

        # Check for safety warnings
        safety_terms = [
            "caution",
            "warning",
            "careful",
            "avoid",
            "do not",
            "تحذير",
            "احذر",
            "تجنب",
            "لا تفعل",
        ]
        found_warnings = [t for t in safety_terms if t in rec_lower]
        if found_warnings:
            score += 0.1
            evidence.append(f"Contains safety guidance: {found_warnings[:3]}")

        # Check for protective equipment mentions
        ppe_terms = [
            "gloves",
            "mask",
            "goggles",
            "protective",
            "قفازات",
            "كمامة",
            "نظارات",
            "حماية",
        ]
        found_ppe = [t for t in ppe_terms if t in rec_lower]
        if found_ppe:
            score += 0.1
            evidence.append(f"Mentions protective equipment: {found_ppe}")

        # Check for dangerous chemicals without warnings
        dangerous_terms = [
            "pesticide",
            "herbicide",
            "fungicide",
            "chemical",
            "مبيد",
            "كيميائي",
        ]
        has_chemicals = any(t in rec_lower for t in dangerous_terms)
        has_warnings = any(t in rec_lower for t in safety_terms)

        if has_chemicals and not has_warnings:
            score -= 0.2
            evidence.append("Contains chemical references without safety warnings")

        # Penalize for excessive quantities
        import re

        quantities = re.findall(r"(\d+)\s*(kg|liter|كجم|لتر)", rec_lower)
        for qty, unit in quantities:
            if int(qty) > 100:  # Arbitrary threshold
                score -= 0.1
                evidence.append(f"Large quantity mentioned: {qty} {unit}")
                break

        return CriteriaScore(
            criteria=EvaluationCriteria.SAFETY,
            score=max(score, 0.0),
            explanation="Safety evaluated based on warnings and chemical handling guidance",
            explanation_ar="تم تقييم السلامة بناءً على التحذيرات وإرشادات التعامل مع المواد الكيميائية",
            evidence=evidence,
        )

    def _evaluate_relevance_heuristic(
        self,
        recommendation: str,
        query: str,
        context: dict[str, Any],
    ) -> CriteriaScore:
        """Evaluate relevance using heuristics"""
        score = 0.5  # Base score
        evidence = []

        rec_lower = recommendation.lower()
        query_lower = query.lower()

        # Check keyword overlap with query
        query_words = set(query_lower.split())
        rec_words = set(rec_lower.split())
        overlap = query_words.intersection(rec_words)

        if overlap:
            overlap_ratio = len(overlap) / max(len(query_words), 1)
            score += overlap_ratio * 0.3
            evidence.append(f"Query keyword overlap: {list(overlap)[:5]}")

        # Check context field mentions
        context_values = [str(v).lower() for v in context.values() if v]
        for val in context_values:
            if val in rec_lower:
                score += 0.1
                evidence.append(f"Mentions context value: {val}")

        # Agricultural relevance
        agri_terms = [
            "crop",
            "field",
            "soil",
            "water",
            "irrigation",
            "fertilizer",
            "harvest",
            "محصول",
            "حقل",
            "تربة",
            "ماء",
            "ري",
            "سماد",
            "حصاد",
        ]
        found_agri = [t for t in agri_terms if t in rec_lower]
        if found_agri:
            score += 0.2
            evidence.append(f"Agricultural relevance: {found_agri[:3]}")

        return CriteriaScore(
            criteria=EvaluationCriteria.RELEVANCE,
            score=min(score, 1.0),
            explanation="Relevance evaluated based on query and context alignment",
            explanation_ar="تم تقييم الصلة بناءً على التوافق مع الاستعلام والسياق",
            evidence=evidence,
        )

    def _evaluate_completeness_heuristic(
        self,
        recommendation: str,
        recommendation_type: RecommendationType,
    ) -> CriteriaScore:
        """Evaluate completeness using heuristics"""
        score = 0.5  # Base score
        evidence = []

        # Check for expected components based on recommendation type
        expected_components = {
            RecommendationType.IRRIGATION: [
                ("quantity", ["liter", "mm", "لتر", "مم"]),
                ("timing", ["morning", "evening", "صباحاً", "مساءً"]),
                ("frequency", ["daily", "weekly", "يومياً", "أسبوعياً"]),
            ],
            RecommendationType.FERTILIZATION: [
                ("type", ["nitrogen", "phosphorus", "potassium", "نيتروجين", "فوسفور"]),
                ("quantity", ["kg", "gram", "كجم", "غرام"]),
                ("application", ["apply", "spread", "ضع", "انشر"]),
            ],
            RecommendationType.PEST_CONTROL: [
                ("identification", ["pest", "insect", "آفة", "حشرة"]),
                ("treatment", ["spray", "apply", "رش", "ضع"]),
                ("prevention", ["prevent", "avoid", "تجنب", "منع"]),
            ],
        }

        rec_lower = recommendation.lower()
        components = expected_components.get(recommendation_type, [])

        for component_name, keywords in components:
            if any(kw in rec_lower for kw in keywords):
                score += 0.15
                evidence.append(f"Contains {component_name} information")

        # Length-based completeness
        word_count = len(recommendation.split())
        if word_count >= 50:
            score += 0.1
            evidence.append(f"Detailed response ({word_count} words)")
        elif word_count < 20:
            score -= 0.1
            evidence.append(f"Brief response ({word_count} words)")

        return CriteriaScore(
            criteria=EvaluationCriteria.COMPLETENESS,
            score=min(max(score, 0.0), 1.0),
            explanation="Completeness evaluated based on expected components",
            explanation_ar="تم تقييم الاكتمال بناءً على المكونات المتوقعة",
            evidence=evidence,
        )

    def _evaluate_clarity_heuristic(
        self,
        recommendation: str,
    ) -> CriteriaScore:
        """Evaluate clarity using heuristics"""
        score = 0.7  # Base score
        evidence = []

        # Check sentence structure
        sentences = re.split(r"[.!?،؟]", recommendation)
        sentences = [s.strip() for s in sentences if s.strip()]

        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)

            if 10 <= avg_sentence_length <= 25:
                score += 0.15
                evidence.append(f"Good sentence length (avg: {avg_sentence_length:.1f} words)")
            elif avg_sentence_length > 40:
                score -= 0.2
                evidence.append(f"Sentences too long (avg: {avg_sentence_length:.1f} words)")

        # Check for clear structure markers
        structure_markers = [
            "first",
            "second",
            "then",
            "finally",
            "أولاً",
            "ثانياً",
            "ثم",
            "أخيراً",
        ]
        found_markers = [m for m in structure_markers if m.lower() in recommendation.lower()]
        if found_markers:
            score += 0.1
            evidence.append("Contains structural markers")

        # Check for bullet points or numbered lists
        if re.search(r"[\-\•\*]\s|^\d+\.", recommendation, re.MULTILINE):
            score += 0.1
            evidence.append("Uses list formatting")

        return CriteriaScore(
            criteria=EvaluationCriteria.CLARITY,
            score=min(score, 1.0),
            explanation="Clarity evaluated based on sentence structure and formatting",
            explanation_ar="تم تقييم الوضوح بناءً على بنية الجملة والتنسيق",
            evidence=evidence,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Helper Methods
    # ─────────────────────────────────────────────────────────────────────────

    def _detect_recommendation_type(
        self,
        recommendation: str,
    ) -> RecommendationType:
        """Detect recommendation type from content"""
        rec_lower = recommendation.lower()

        type_keywords = {
            RecommendationType.IRRIGATION: [
                "water",
                "irrigat",
                "drip",
                "ري",
                "ماء",
                "رطوبة",
            ],
            RecommendationType.FERTILIZATION: [
                "fertiliz",
                "nutrient",
                "nitrogen",
                "سماد",
                "تسميد",
                "نيتروجين",
            ],
            RecommendationType.PEST_CONTROL: [
                "pest",
                "insect",
                "spray",
                "آفة",
                "حشرة",
                "مبيد",
            ],
            RecommendationType.DISEASE: [
                "disease",
                "fungus",
                "virus",
                "infection",
                "مرض",
                "فطر",
                "عدوى",
            ],
            RecommendationType.HARVEST: [
                "harvest",
                "pick",
                "collect",
                "حصاد",
                "قطف",
                "جمع",
            ],
            RecommendationType.PLANTING: [
                "plant",
                "seed",
                "sow",
                "زراعة",
                "بذور",
                "غرس",
            ],
            RecommendationType.WEATHER: [
                "weather",
                "rain",
                "temperature",
                "طقس",
                "مطر",
                "حرارة",
            ],
        }

        for rec_type, keywords in type_keywords.items():
            if any(kw in rec_lower for kw in keywords):
                return rec_type

        return RecommendationType.GENERAL
