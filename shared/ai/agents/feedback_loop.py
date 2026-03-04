"""
Structured Feedback Loop for AI Agents
======================================
حلقة التغذية الراجعة المنظمة لوكلاء الذكاء الاصطناعي

Implements comprehensive feedback collection and learning:
- LLM-as-Judge for quality assessment
- Human feedback integration
- Outcome tracking
- Reward model training data
- Continuous improvement loop

Based on RLHF and constitutional AI principles.

Author: SAHOOL Platform Team
Updated: January 2026
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

import structlog

logger = structlog.get_logger()


# ============================================================================
# ENUMS & TYPES
# ============================================================================


class FeedbackType(StrEnum):
    """أنواع التغذية الراجعة"""

    LLM_JUDGE = "llm_judge"  # Automatic LLM evaluation
    HUMAN_RATING = "human_rating"  # Human star rating
    HUMAN_THUMBS = "human_thumbs"  # Human thumbs up/down
    HUMAN_TEXT = "human_text"  # Human text feedback
    OUTCOME = "outcome"  # Measured outcome
    CORRECTION = "correction"  # User correction


class QualityDimension(StrEnum):
    """أبعاد الجودة"""

    ACCURACY = "accuracy"  # Technical correctness
    RELEVANCE = "relevance"  # Contextual appropriateness
    ACTIONABILITY = "actionability"  # Can the advice be acted upon
    TIMELINESS = "timeliness"  # Is the timing right
    SAFETY = "safety"  # Risk awareness
    CLARITY = "clarity"  # Clear communication
    COMPLETENESS = "completeness"  # Nothing important missing


# Import canonical OutcomeStatus from shared.ai.feedback
from shared.ai.feedback import OutcomeStatus  # noqa: E402, F811


class EscalationLevel(StrEnum):
    """مستوى التصعيد"""

    NONE = "none"  # No escalation needed
    EXPERT_REVIEW = "expert"  # Needs expert review
    HUMAN_REQUIRED = "human"  # Human decision required
    RETRAINING = "retraining"  # Model needs retraining


# ============================================================================
# EVALUATION RUBRICS
# ============================================================================


@dataclass
class DimensionScore:
    """
    Score for a single quality dimension.
    درجة لبُعد جودة واحد
    """

    dimension: QualityDimension
    score: int  # 1-5 scale
    max_score: int = 5
    weight: float = 1.0  # Weight in overall score
    explanation: str = ""
    explanation_ar: str = ""
    improvement_suggestions: list[str] = field(default_factory=list)

    @property
    def normalized_score(self) -> float:
        """Get normalized score (0-1)."""
        return self.score / self.max_score

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension.value,
            "score": self.score,
            "max_score": self.max_score,
            "weight": self.weight,
            "normalized_score": self.normalized_score,
            "explanation": self.explanation,
            "explanation_ar": self.explanation_ar,
            "improvement_suggestions": self.improvement_suggestions,
        }


@dataclass
class QualityRubric:
    """
    Evaluation rubric for quality assessment.
    معيار التقييم لتقييم الجودة
    """

    rubric_id: str
    name: str
    name_ar: str
    description: str
    description_ar: str
    dimensions: list[QualityDimension]
    dimension_weights: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        # Set default weights if not provided
        if not self.dimension_weights:
            equal_weight = 1.0 / len(self.dimensions)
            self.dimension_weights = {d.value: equal_weight for d in self.dimensions}

    def to_dict(self) -> dict[str, Any]:
        return {
            "rubric_id": self.rubric_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "dimensions": [d.value for d in self.dimensions],
            "dimension_weights": self.dimension_weights,
        }


# Default rubrics
CODE_FIX_RUBRIC = QualityRubric(
    rubric_id="code_fix_rubric_v1",
    name="Code Fix Quality Rubric",
    name_ar="معيار جودة إصلاح الكود",
    description="Evaluates code fix quality across multiple dimensions",
    description_ar="تقييم جودة إصلاح الكود عبر أبعاد متعددة",
    dimensions=[
        QualityDimension.ACCURACY,
        QualityDimension.SAFETY,
        QualityDimension.COMPLETENESS,
        QualityDimension.CLARITY,
    ],
    dimension_weights={
        QualityDimension.ACCURACY.value: 0.35,
        QualityDimension.SAFETY.value: 0.30,
        QualityDimension.COMPLETENESS.value: 0.20,
        QualityDimension.CLARITY.value: 0.15,
    },
)

ADVISORY_RUBRIC = QualityRubric(
    rubric_id="advisory_rubric_v1",
    name="Advisory Quality Rubric",
    name_ar="معيار جودة الاستشارات",
    description="Evaluates agricultural advisory quality",
    description_ar="تقييم جودة الاستشارات الزراعية",
    dimensions=[
        QualityDimension.ACCURACY,
        QualityDimension.RELEVANCE,
        QualityDimension.ACTIONABILITY,
        QualityDimension.TIMELINESS,
        QualityDimension.SAFETY,
    ],
    dimension_weights={
        QualityDimension.ACCURACY.value: 0.30,
        QualityDimension.RELEVANCE.value: 0.25,
        QualityDimension.ACTIONABILITY.value: 0.20,
        QualityDimension.TIMELINESS.value: 0.15,
        QualityDimension.SAFETY.value: 0.10,
    },
)


# ============================================================================
# FEEDBACK ENTRIES
# ============================================================================


@dataclass
class JudgeEvaluation:
    """
    LLM-as-Judge evaluation result.
    نتيجة تقييم القاضي LLM
    """

    evaluation_id: str
    execution_id: str  # What was evaluated
    rubric: QualityRubric
    dimension_scores: list[DimensionScore]
    overall_score: float  # Weighted average (0-1)
    grade: str  # Letter grade (A/B/C/D/F)
    summary: str  # Summary explanation
    summary_ar: str
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    escalation_level: EscalationLevel = EscalationLevel.NONE
    escalation_reason: str | None = None
    judge_model: str = ""
    judge_confidence: float = 0.8
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "evaluation_id": self.evaluation_id,
            "execution_id": self.execution_id,
            "rubric": self.rubric.to_dict(),
            "dimension_scores": [s.to_dict() for s in self.dimension_scores],
            "overall_score": self.overall_score,
            "grade": self.grade,
            "summary": self.summary,
            "summary_ar": self.summary_ar,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "suggestions": self.suggestions,
            "escalation_level": self.escalation_level.value,
            "escalation_reason": self.escalation_reason,
            "judge_model": self.judge_model,
            "judge_confidence": self.judge_confidence,
            "evaluated_at": self.evaluated_at.isoformat(),
        }


@dataclass
class HumanFeedback:
    """
    Human feedback entry.
    إدخال تغذية راجعة بشرية
    """

    feedback_id: str
    execution_id: str  # What was evaluated
    feedback_type: FeedbackType
    user_id: str | None = None
    rating: int | None = None  # 1-5 stars
    thumbs_up: bool | None = None  # True = positive
    comment: str = ""
    comment_ar: str = ""
    correction: str | None = None  # User's correction
    metadata: dict[str, Any] = field(default_factory=dict)
    received_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "feedback_id": self.feedback_id,
            "execution_id": self.execution_id,
            "feedback_type": self.feedback_type.value,
            "user_id": self.user_id,
            "rating": self.rating,
            "thumbs_up": self.thumbs_up,
            "comment": self.comment,
            "comment_ar": self.comment_ar,
            "correction": self.correction,
            "metadata": self.metadata,
            "received_at": self.received_at.isoformat(),
        }


@dataclass
class OutcomeFeedback:
    """
    Measured outcome feedback.
    تغذية راجعة للنتائج المقاسة
    """

    outcome_id: str
    execution_id: str  # What was executed
    outcome_status: OutcomeStatus
    metrics: dict[str, float] = field(default_factory=dict)  # e.g., yield_improvement, cost_savings
    details: str = ""
    details_ar: str = ""
    measured_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    time_to_measure_hours: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome_id": self.outcome_id,
            "execution_id": self.execution_id,
            "outcome_status": self.outcome_status.value,
            "metrics": self.metrics,
            "details": self.details,
            "details_ar": self.details_ar,
            "measured_at": self.measured_at.isoformat(),
            "time_to_measure_hours": self.time_to_measure_hours,
        }


@dataclass
class FeedbackRecord:
    """
    Complete feedback record for an execution.
    سجل التغذية الراجعة الكامل للتنفيذ
    """

    record_id: str
    execution_id: str
    agent_id: str
    task_type: str  # Type of task (code_fix, advisory, etc.)
    judge_evaluation: JudgeEvaluation | None = None
    human_feedback: list[HumanFeedback] = field(default_factory=list)
    outcome: OutcomeFeedback | None = None
    combined_score: float = 0.0  # Weighted combination of all feedback
    reward: float = 0.0  # Reward signal for learning
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def calculate_combined_score(self) -> float:
        """Calculate combined score from all feedback sources."""
        scores = []
        weights = []

        # LLM judge score (highest weight)
        if self.judge_evaluation:
            scores.append(self.judge_evaluation.overall_score)
            weights.append(0.4)

        # Human ratings
        for hf in self.human_feedback:
            if hf.rating:
                scores.append(hf.rating / 5.0)
                weights.append(0.3)
            elif hf.thumbs_up is not None:
                scores.append(1.0 if hf.thumbs_up else 0.0)
                weights.append(0.2)

        # Outcome
        if self.outcome:
            outcome_scores = {
                OutcomeStatus.SUCCESS: 1.0,
                OutcomeStatus.PARTIAL_SUCCESS: 0.6,
                OutcomeStatus.FAILURE: 0.0,
                OutcomeStatus.UNKNOWN: 0.5,
                OutcomeStatus.NOT_APPLIED: 0.5,
            }
            scores.append(outcome_scores.get(self.outcome.outcome_status, 0.5))
            weights.append(0.3)

        if not scores:
            return 0.0

        # Normalize weights
        total_weight = sum(weights)
        if total_weight == 0:
            return 0.0

        combined = sum(s * w for s, w in zip(scores, weights)) / total_weight
        return round(combined, 3)

    def calculate_reward(self) -> float:
        """Calculate reward signal for learning."""
        # Base reward from combined score
        reward = self.combined_score * 2 - 1  # Scale to [-1, 1]

        # Bonus for high human ratings
        for hf in self.human_feedback:
            if hf.rating and hf.rating >= 4:
                reward += 0.1
            elif hf.thumbs_up:
                reward += 0.05

        # Bonus for successful outcomes
        if self.outcome and self.outcome.outcome_status == OutcomeStatus.SUCCESS:
            reward += 0.2

        # Penalty for safety issues
        if self.judge_evaluation:
            for score in self.judge_evaluation.dimension_scores:
                if score.dimension == QualityDimension.SAFETY and score.score <= 2:
                    reward -= 0.3

        return round(max(-1.0, min(1.0, reward)), 3)

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "execution_id": self.execution_id,
            "agent_id": self.agent_id,
            "task_type": self.task_type,
            "judge_evaluation": self.judge_evaluation.to_dict() if self.judge_evaluation else None,
            "human_feedback": [hf.to_dict() for hf in self.human_feedback],
            "outcome": self.outcome.to_dict() if self.outcome else None,
            "combined_score": self.combined_score,
            "reward": self.reward,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# ============================================================================
# LLM-AS-JUDGE
# ============================================================================


class LLMJudge:
    """
    LLM-based quality evaluator.
    مقيم الجودة القائم على LLM

    Uses a language model to evaluate agent outputs against rubrics.
    """

    # Scoring prompt template
    JUDGE_PROMPT_TEMPLATE = """You are an expert evaluator. Assess the following agent output against the quality rubric.

## Task Description
{task_description}

## Agent Output
{agent_output}

## Evaluation Rubric: {rubric_name}
{rubric_description}

Evaluate each dimension on a 1-5 scale:
1 = Poor - Major issues, not acceptable
2 = Fair - Significant issues, needs improvement
3 = Good - Acceptable, some minor issues
4 = Very Good - High quality, minor improvements possible
5 = Excellent - Outstanding, meets all criteria

## Dimensions to Evaluate:
{dimensions}

For each dimension, provide:
- Score (1-5)
- Brief explanation (1-2 sentences)
- Improvement suggestion (if score < 5)

Then provide:
- Overall strengths (2-3 bullet points)
- Overall weaknesses (2-3 bullet points)
- Recommended improvements (2-3 bullet points)

Respond in JSON format:
```json
{{
  "dimension_scores": [
    {{"dimension": "...", "score": N, "explanation": "...", "suggestion": "..."}}
  ],
  "strengths": ["..."],
  "weaknesses": ["..."],
  "suggestions": ["..."],
  "summary": "One paragraph summary"
}}
```
"""

    def __init__(
        self,
        llm_client: Any = None,
        model_name: str = "claude-3-haiku",
        timeout_seconds: int = 30,
    ):
        self.llm_client = llm_client
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

        logger.info(
            "llm_judge_initialized",
            model=model_name,
        )

    async def evaluate(
        self,
        execution_id: str,
        task_description: str,
        agent_output: str,
        rubric: QualityRubric,
        context: dict[str, Any] | None = None,
    ) -> JudgeEvaluation:
        """
        Evaluate agent output against rubric.
        تقييم مخرجات الوكيل مقابل المعيار
        """
        # Build prompt
        dimensions_text = "\n".join([f"- {d.value}: {self._get_dimension_description(d)}" for d in rubric.dimensions])

        prompt = self.JUDGE_PROMPT_TEMPLATE.format(
            task_description=task_description,
            agent_output=agent_output[:5000],  # Truncate if too long
            rubric_name=rubric.name,
            rubric_description=rubric.description,
            dimensions=dimensions_text,
        )

        try:
            # Call LLM (mock if no client)
            if self.llm_client:
                response = await self._call_llm(prompt)
                result = self._parse_response(response, rubric)
            else:
                # Mock evaluation for testing
                result = self._mock_evaluation(rubric)

            # Calculate overall score
            overall_score = sum(
                s.normalized_score * rubric.dimension_weights.get(s.dimension.value, 0.25)
                for s in result["dimension_scores"]
            )

            # Determine grade
            grade = self._score_to_grade(overall_score)

            # Check for escalation
            escalation_level, escalation_reason = self._check_escalation(result["dimension_scores"], overall_score)

            return JudgeEvaluation(
                evaluation_id=str(uuid.uuid4()),
                execution_id=execution_id,
                rubric=rubric,
                dimension_scores=result["dimension_scores"],
                overall_score=overall_score,
                grade=grade,
                summary=result.get("summary", ""),
                summary_ar=result.get("summary_ar", ""),
                strengths=result.get("strengths", []),
                weaknesses=result.get("weaknesses", []),
                suggestions=result.get("suggestions", []),
                escalation_level=escalation_level,
                escalation_reason=escalation_reason,
                judge_model=self.model_name,
                judge_confidence=0.8,
            )

        except Exception as e:
            logger.error("judge_evaluation_failed", error=str(e))
            # Return default evaluation on error
            return self._default_evaluation(execution_id, rubric, str(e))

    async def _call_llm(self, prompt: str) -> str:
        """Call LLM and get response."""
        if hasattr(self.llm_client, "generate"):
            response = await self.llm_client.generate(prompt=prompt)
            return response.text if hasattr(response, "text") else str(response)
        return ""

    def _parse_response(self, response: str, rubric: QualityRubric) -> dict[str, Any]:
        """Parse LLM response into structured format."""
        try:
            # Extract JSON from response
            import re

            json_match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
            else:
                data = json.loads(response)

            # Convert to DimensionScore objects
            dimension_scores = []
            for ds in data.get("dimension_scores", []):
                dim = QualityDimension(ds["dimension"])
                dimension_scores.append(
                    DimensionScore(
                        dimension=dim,
                        score=ds["score"],
                        weight=rubric.dimension_weights.get(dim.value, 0.25),
                        explanation=ds.get("explanation", ""),
                        improvement_suggestions=[ds.get("suggestion")] if ds.get("suggestion") else [],
                    )
                )

            return {
                "dimension_scores": dimension_scores,
                "strengths": data.get("strengths", []),
                "weaknesses": data.get("weaknesses", []),
                "suggestions": data.get("suggestions", []),
                "summary": data.get("summary", ""),
            }

        except Exception as e:
            logger.warning(f"Failed to parse judge response: {e}")
            return self._mock_evaluation(rubric)

    def _mock_evaluation(self, rubric: QualityRubric) -> dict[str, Any]:
        """Generate mock evaluation for testing."""
        import random

        return {
            "dimension_scores": [
                DimensionScore(
                    dimension=dim,
                    score=random.randint(3, 5),
                    weight=rubric.dimension_weights.get(dim.value, 0.25),
                    explanation=f"Mock evaluation for {dim.value}",
                )
                for dim in rubric.dimensions
            ],
            "strengths": ["Mock strength 1", "Mock strength 2"],
            "weaknesses": ["Mock weakness 1"],
            "suggestions": ["Mock suggestion 1"],
            "summary": "Mock evaluation summary",
        }

    def _default_evaluation(
        self,
        execution_id: str,
        rubric: QualityRubric,
        error: str,
    ) -> JudgeEvaluation:
        """Return default evaluation on error."""
        dimension_scores = [
            DimensionScore(
                dimension=dim,
                score=3,  # Neutral score
                weight=rubric.dimension_weights.get(dim.value, 0.25),
                explanation="Evaluation failed, default score assigned",
            )
            for dim in rubric.dimensions
        ]

        return JudgeEvaluation(
            evaluation_id=str(uuid.uuid4()),
            execution_id=execution_id,
            rubric=rubric,
            dimension_scores=dimension_scores,
            overall_score=0.6,
            grade="C",
            summary=f"Evaluation failed: {error}",
            summary_ar=f"فشل التقييم: {error}",
            escalation_level=EscalationLevel.EXPERT_REVIEW,
            escalation_reason="Automatic evaluation failed",
            judge_model=self.model_name,
            judge_confidence=0.0,
        )

    def _get_dimension_description(self, dimension: QualityDimension) -> str:
        """Get description for a quality dimension."""
        descriptions = {
            QualityDimension.ACCURACY: "Is the information technically correct?",
            QualityDimension.RELEVANCE: "Is it relevant to the specific context?",
            QualityDimension.ACTIONABILITY: "Can the user act on this advice?",
            QualityDimension.TIMELINESS: "Is the timing appropriate?",
            QualityDimension.SAFETY: "Are risks and safety considered?",
            QualityDimension.CLARITY: "Is the communication clear?",
            QualityDimension.COMPLETENESS: "Is anything important missing?",
        }
        return descriptions.get(dimension, "")

    def _score_to_grade(self, score: float) -> str:
        """Convert numerical score to letter grade."""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"

    def _check_escalation(
        self,
        dimension_scores: list[DimensionScore],
        overall_score: float,
    ) -> tuple[EscalationLevel, str | None]:
        """Check if escalation is needed."""
        # Check for critical failures
        for score in dimension_scores:
            if score.dimension == QualityDimension.SAFETY and score.score <= 2:
                return EscalationLevel.HUMAN_REQUIRED, "Safety score critically low"
            if score.score <= 1:
                return EscalationLevel.EXPERT_REVIEW, f"Critical failure in {score.dimension.value}"

        # Check overall score
        if overall_score < 0.5:
            return EscalationLevel.EXPERT_REVIEW, "Overall score below threshold"

        return EscalationLevel.NONE, None


# ============================================================================
# FEEDBACK LOOP MANAGER
# ============================================================================


class AgentFeedbackLoop:
    """
    Manages the complete feedback loop for an agent.
    إدارة حلقة التغذية الراجعة الكاملة للوكيل

    Provides:
    - Automatic LLM-based evaluation
    - Human feedback collection
    - Outcome tracking
    - Reward calculation
    - Training data export
    """

    def __init__(
        self,
        agent_id: str,
        llm_judge: LLMJudge | None = None,
        default_rubric: QualityRubric | None = None,
        enable_auto_evaluate: bool = True,
        confidence_threshold: float = 0.7,
    ):
        self.agent_id = agent_id
        self.llm_judge = llm_judge or LLMJudge()
        self.default_rubric = default_rubric or CODE_FIX_RUBRIC
        self.enable_auto_evaluate = enable_auto_evaluate
        self.confidence_threshold = confidence_threshold

        # Feedback storage
        self.records: dict[str, FeedbackRecord] = {}

        logger.info(
            "feedback_loop_initialized",
            agent_id=agent_id,
            auto_evaluate=enable_auto_evaluate,
        )

    async def evaluate_execution(
        self,
        execution_id: str,
        task_description: str,
        agent_output: str,
        task_type: str = "code_fix",
        rubric: QualityRubric | None = None,
        context: dict[str, Any] | None = None,
    ) -> JudgeEvaluation:
        """
        Evaluate an agent execution using LLM-as-Judge.
        تقييم تنفيذ الوكيل باستخدام القاضي LLM
        """
        rubric = rubric or self.default_rubric

        evaluation = await self.llm_judge.evaluate(
            execution_id=execution_id,
            task_description=task_description,
            agent_output=agent_output,
            rubric=rubric,
            context=context,
        )

        # Store in record
        if execution_id not in self.records:
            self.records[execution_id] = FeedbackRecord(
                record_id=str(uuid.uuid4()),
                execution_id=execution_id,
                agent_id=self.agent_id,
                task_type=task_type,
            )

        record = self.records[execution_id]
        record.judge_evaluation = evaluation
        record.updated_at = datetime.now(UTC)

        # Update scores
        record.combined_score = record.calculate_combined_score()
        record.reward = record.calculate_reward()

        logger.info(
            "execution_evaluated",
            execution_id=execution_id,
            overall_score=evaluation.overall_score,
            grade=evaluation.grade,
        )

        return evaluation

    async def collect_human_rating(
        self,
        execution_id: str,
        rating: int,
        user_id: str | None = None,
        comment: str = "",
        comment_ar: str = "",
    ) -> HumanFeedback:
        """
        Collect human rating (1-5 stars).
        جمع تقييم بشري (1-5 نجوم)
        """
        feedback = HumanFeedback(
            feedback_id=str(uuid.uuid4()),
            execution_id=execution_id,
            feedback_type=FeedbackType.HUMAN_RATING,
            user_id=user_id,
            rating=max(1, min(5, rating)),  # Clamp to 1-5
            comment=comment,
            comment_ar=comment_ar,
        )

        self._add_human_feedback(execution_id, feedback)
        return feedback

    async def collect_thumbs_feedback(
        self,
        execution_id: str,
        thumbs_up: bool,
        user_id: str | None = None,
    ) -> HumanFeedback:
        """
        Collect thumbs up/down feedback.
        جمع تغذية راجعة إيجابية/سلبية
        """
        feedback = HumanFeedback(
            feedback_id=str(uuid.uuid4()),
            execution_id=execution_id,
            feedback_type=FeedbackType.HUMAN_THUMBS,
            user_id=user_id,
            thumbs_up=thumbs_up,
        )

        self._add_human_feedback(execution_id, feedback)
        return feedback

    async def collect_correction(
        self,
        execution_id: str,
        correction: str,
        user_id: str | None = None,
    ) -> HumanFeedback:
        """
        Collect user correction.
        جمع تصحيح المستخدم
        """
        feedback = HumanFeedback(
            feedback_id=str(uuid.uuid4()),
            execution_id=execution_id,
            feedback_type=FeedbackType.CORRECTION,
            user_id=user_id,
            correction=correction,
        )

        self._add_human_feedback(execution_id, feedback)
        return feedback

    async def record_outcome(
        self,
        execution_id: str,
        status: OutcomeStatus,
        metrics: dict[str, float] | None = None,
        details: str = "",
        details_ar: str = "",
    ) -> OutcomeFeedback:
        """
        Record the measured outcome.
        تسجيل النتيجة المقاسة
        """
        # Calculate time to measure
        record = self.records.get(execution_id)
        time_to_measure = 0.0
        if record:
            time_to_measure = (datetime.now(UTC) - record.created_at).total_seconds() / 3600

        outcome = OutcomeFeedback(
            outcome_id=str(uuid.uuid4()),
            execution_id=execution_id,
            outcome_status=status,
            metrics=metrics or {},
            details=details,
            details_ar=details_ar,
            time_to_measure_hours=time_to_measure,
        )

        # Store in record
        if execution_id not in self.records:
            self.records[execution_id] = FeedbackRecord(
                record_id=str(uuid.uuid4()),
                execution_id=execution_id,
                agent_id=self.agent_id,
                task_type="unknown",
            )

        record = self.records[execution_id]
        record.outcome = outcome
        record.updated_at = datetime.now(UTC)

        # Update scores
        record.combined_score = record.calculate_combined_score()
        record.reward = record.calculate_reward()

        logger.info(
            "outcome_recorded",
            execution_id=execution_id,
            status=status.value,
            reward=record.reward,
        )

        return outcome

    def _add_human_feedback(self, execution_id: str, feedback: HumanFeedback) -> None:
        """Add human feedback to record."""
        if execution_id not in self.records:
            self.records[execution_id] = FeedbackRecord(
                record_id=str(uuid.uuid4()),
                execution_id=execution_id,
                agent_id=self.agent_id,
                task_type="unknown",
            )

        record = self.records[execution_id]
        record.human_feedback.append(feedback)
        record.updated_at = datetime.now(UTC)

        # Update scores
        record.combined_score = record.calculate_combined_score()
        record.reward = record.calculate_reward()

    def get_record(self, execution_id: str) -> FeedbackRecord | None:
        """Get feedback record for an execution."""
        return self.records.get(execution_id)

    def get_reward(self, execution_id: str) -> float:
        """Get reward signal for an execution."""
        record = self.records.get(execution_id)
        return record.reward if record else 0.0

    def should_escalate(self, execution_id: str) -> tuple[bool, str | None]:
        """Check if execution should be escalated."""
        record = self.records.get(execution_id)
        if not record or not record.judge_evaluation:
            return False, None

        if record.judge_evaluation.escalation_level != EscalationLevel.NONE:
            return True, record.judge_evaluation.escalation_reason

        # Check confidence threshold
        if record.judge_evaluation.judge_confidence < self.confidence_threshold:
            return True, "Judge confidence below threshold"

        return False, None

    def export_for_training(
        self,
        min_score: float = 0.7,
        include_corrections: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Export feedback data for model training.
        تصدير بيانات التغذية الراجعة لتدريب النموذج
        """
        training_data = []

        for record in self.records.values():
            if record.combined_score < min_score:
                continue

            entry = {
                "execution_id": record.execution_id,
                "agent_id": record.agent_id,
                "task_type": record.task_type,
                "combined_score": record.combined_score,
                "reward": record.reward,
            }

            # Add judge scores
            if record.judge_evaluation:
                entry["judge_scores"] = {s.dimension.value: s.score for s in record.judge_evaluation.dimension_scores}

            # Add corrections if available
            if include_corrections:
                corrections = [hf.correction for hf in record.human_feedback if hf.correction]
                if corrections:
                    entry["corrections"] = corrections

            training_data.append(entry)

        return training_data

    def get_summary_stats(self) -> dict[str, Any]:
        """Get summary statistics."""
        if not self.records:
            return {"total_records": 0}

        scores = [r.combined_score for r in self.records.values()]
        rewards = [r.reward for r in self.records.values()]

        return {
            "total_records": len(self.records),
            "average_score": sum(scores) / len(scores),
            "average_reward": sum(rewards) / len(rewards),
            "min_score": min(scores),
            "max_score": max(scores),
            "high_score_count": sum(1 for s in scores if s >= 0.8),
            "low_score_count": sum(1 for s in scores if s < 0.5),
            "escalation_count": sum(
                1
                for r in self.records.values()
                if r.judge_evaluation and r.judge_evaluation.escalation_level != EscalationLevel.NONE
            ),
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def create_feedback_loop(
    agent_id: str,
    rubric: QualityRubric | None = None,
) -> AgentFeedbackLoop:
    """Factory function to create a feedback loop."""
    return AgentFeedbackLoop(
        agent_id=agent_id,
        default_rubric=rubric,
    )


def get_code_fix_rubric() -> QualityRubric:
    """Get the code fix quality rubric."""
    return CODE_FIX_RUBRIC


def get_advisory_rubric() -> QualityRubric:
    """Get the advisory quality rubric."""
    return ADVISORY_RUBRIC
