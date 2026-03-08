"""
Feedback-Training-Experience Pipeline
======================================
خط أنابيب التغذية الراجعة والتدريب والخبرة

Connects FeedbackCollector, ModelTrainer, and ExperienceLearner into a unified
pipeline that:
1. Routes incoming feedback to the appropriate subsystem
2. Exports high-quality feedback as training examples
3. Auto-generates/updates SOPs from accumulated successful outcomes
4. Reports model improvement over time

يربط جامع التغذية الراجعة ومدرب النماذج ومتعلم الخبرة في خط أنابيب موحد:
١. توجيه التغذية الراجعة الواردة إلى النظام الفرعي المناسب
٢. تصدير التغذية الراجعة عالية الجودة كأمثلة تدريب
٣. توليد/تحديث إجراءات التشغيل القياسية تلقائياً من النتائج الناجحة المتراكمة
٤. تقرير تحسين النموذج عبر الزمن

Author: SAHOOL Platform Team
Updated: March 2026
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

from .experience_learning import (
    ExecutionStatus,
    ExecutionStep,
    ExperienceLearner,
    get_experience_learner,
)
from .feedback import (
    FeedbackCollector,
    FeedbackItem,
    FeedbackType,
    OutcomeStatus,
    RecommendationType,
    get_feedback_collector,
)
from .model_training import (
    DatasetBuilder,
    ModelTrainer,
    TrainingDataset,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_MIN_RATING_FOR_TRAINING = 4
DEFAULT_MIN_OUTCOMES_FOR_SOP = 3
DEFAULT_SOP_TRIGGER_WINDOW_DAYS = 30
DEFAULT_EXPORT_BATCH_SIZE = 100


class PipelineAction(StrEnum):
    """Actions taken by the pipeline | الإجراءات التي يتخذها خط الأنابيب"""

    TRAINING_EXPORT = "training_export"  # تصدير للتدريب
    SOP_UPDATE = "sop_update"  # تحديث إجراء تشغيل قياسي
    SOP_CREATE = "sop_create"  # إنشاء إجراء تشغيل قياسي
    EXPERIENCE_RECORD = "experience_record"  # تسجيل خبرة
    IGNORED = "ignored"  # تم التجاهل


@dataclass
class PipelineEvent:
    """
    Record of a pipeline action taken for a feedback item.
    سجل إجراء خط الأنابيب المتخذ لعنصر التغذية الراجعة.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    feedback_id: str = ""
    action: PipelineAction = PipelineAction.IGNORED
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "feedback_id": self.feedback_id,
            "action": self.action.value,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ImprovementSnapshot:
    """
    A snapshot of model/SOP improvement metrics at a point in time.
    لقطة لمقاييس تحسين النموذج/إجراء التشغيل القياسي في نقطة زمنية.
    """

    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    total_feedback: int = 0
    positive_feedback: int = 0
    negative_feedback: int = 0
    avg_rating: float = 0.0
    success_rate: float = 0.0
    training_examples_generated: int = 0
    sops_created: int = 0
    sops_updated: int = 0
    avg_yield_impact: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_feedback": self.total_feedback,
            "positive_feedback": self.positive_feedback,
            "negative_feedback": self.negative_feedback,
            "avg_rating": self.avg_rating,
            "success_rate": self.success_rate,
            "training_examples_generated": self.training_examples_generated,
            "sops_created": self.sops_created,
            "sops_updated": self.sops_updated,
            "avg_yield_impact": self.avg_yield_impact,
        }


@dataclass
class PipelineConfig:
    """
    Configuration for the feedback-training pipeline.
    إعدادات خط أنابيب التغذية الراجعة والتدريب.
    """

    min_rating_for_training: int = DEFAULT_MIN_RATING_FOR_TRAINING
    min_outcomes_for_sop: int = DEFAULT_MIN_OUTCOMES_FOR_SOP
    sop_trigger_window_days: int = DEFAULT_SOP_TRIGGER_WINDOW_DAYS
    export_batch_size: int = DEFAULT_EXPORT_BATCH_SIZE
    auto_sop_enabled: bool = True
    auto_training_export_enabled: bool = True
    include_corrections_in_training: bool = True
    # Minimum yield impact (%) for a successful outcome to count toward SOP
    min_yield_impact_for_sop: float = 0.0
    # Agent ID used when recording experience from feedback
    default_agent_id: str = "feedback_pipeline"

    def to_dict(self) -> dict[str, Any]:
        return {
            "min_rating_for_training": self.min_rating_for_training,
            "min_outcomes_for_sop": self.min_outcomes_for_sop,
            "sop_trigger_window_days": self.sop_trigger_window_days,
            "export_batch_size": self.export_batch_size,
            "auto_sop_enabled": self.auto_sop_enabled,
            "auto_training_export_enabled": self.auto_training_export_enabled,
            "include_corrections_in_training": self.include_corrections_in_training,
            "min_yield_impact_for_sop": self.min_yield_impact_for_sop,
            "default_agent_id": self.default_agent_id,
        }


class FeedbackTrainingPipeline:
    """
    Pipeline connecting feedback collection to model training and experience learning.
    خط أنابيب يربط جمع التغذية الراجعة بتدريب النماذج والتعلم من الخبرة.

    This pipeline:
    1. process_feedback() - routes each feedback item to the right subsystem
    2. export_training_data() - exports high-quality feedback as TrainingDataset
    3. trigger_sop_update() - updates SOPs when enough successful outcomes accumulate
    4. get_improvement_report() - summarizes model improvement over time

    هذا الخط:
    ١. process_feedback() - يوجه كل عنصر تغذية راجعة إلى النظام الفرعي المناسب
    ٢. export_training_data() - يصدر التغذية الراجعة عالية الجودة كمجموعة بيانات تدريب
    ٣. trigger_sop_update() - يحدث إجراءات التشغيل القياسية عند تراكم نتائج ناجحة كافية
    ٤. get_improvement_report() - يلخص تحسين النموذج عبر الزمن

    Example:
        pipeline = FeedbackTrainingPipeline(tenant_id="farm_001")

        # Process incoming feedback
        events = await pipeline.process_feedback(feedback_item)

        # Export training data
        dataset = await pipeline.export_training_data()

        # Check for SOP updates
        sop_events = await pipeline.trigger_sop_update(
            recommendation_type=RecommendationType.IRRIGATION
        )

        # Get improvement report
        report = await pipeline.get_improvement_report(days=30)
    """

    def __init__(
        self,
        tenant_id: str,
        collector: FeedbackCollector | None = None,
        learner: ExperienceLearner | None = None,
        trainer: ModelTrainer | None = None,
        config: PipelineConfig | None = None,
    ):
        """
        Initialize the pipeline.

        Args:
            tenant_id: Tenant identifier | معرف المستأجر
            collector: Feedback collector instance (default: auto-created)
            learner: Experience learner instance (default: global singleton)
            trainer: Model trainer instance (default: None, created on demand)
            config: Pipeline configuration
        """
        self.tenant_id = tenant_id
        self.config = config or PipelineConfig()
        self.collector = collector or get_feedback_collector(tenant_id)
        self.learner = learner or get_experience_learner()
        self._trainer = trainer

        # Internal tracking
        self._events: list[PipelineEvent] = []
        self._improvement_history: list[ImprovementSnapshot] = []
        self._training_examples_count = 0
        self._sops_created = 0
        self._sops_updated = 0

        logger.info(
            "FeedbackTrainingPipeline initialized for tenant=%s",
            tenant_id,
        )

    @property
    def trainer(self) -> ModelTrainer:
        """Lazily create ModelTrainer (requires httpx)."""
        if self._trainer is None:
            try:
                self._trainer = ModelTrainer()
            except ImportError:
                raise ImportError("httpx is required for ModelTrainer. Install with: pip install httpx")
        return self._trainer

    # ------------------------------------------------------------------
    # 1. process_feedback
    # ------------------------------------------------------------------

    async def process_feedback(self, feedback: FeedbackItem) -> list[PipelineEvent]:
        """
        Route a feedback item to the appropriate subsystem(s).
        توجيه عنصر تغذية راجعة إلى النظام (الأنظمة) الفرعي المناسب.

        Routing logic:
        - High-rated items (>= min_rating) -> training export queue
        - Corrections -> training export queue (as negative/corrected examples)
        - Outcome feedback -> experience learner for SOP generation
        - Successful outcomes with yield impact -> SOP trigger check

        Args:
            feedback: The feedback item to process

        Returns:
            List of PipelineEvent describing what actions were taken
        """
        events: list[PipelineEvent] = []

        # Route based on feedback type
        if feedback.feedback_type == FeedbackType.RATING:
            events.extend(await self._process_rating(feedback))

        elif feedback.feedback_type == FeedbackType.CORRECTION:
            events.extend(await self._process_correction(feedback))

        elif feedback.feedback_type == FeedbackType.OUTCOME:
            events.extend(await self._process_outcome(feedback))

        elif feedback.feedback_type == FeedbackType.THUMBS:
            events.extend(await self._process_thumbs(feedback))

        elif feedback.feedback_type == FeedbackType.COMMENT:
            # Comments are informational; record but don't trigger pipeline
            events.append(
                PipelineEvent(
                    feedback_id=feedback.id,
                    action=PipelineAction.IGNORED,
                    details={"reason": "comment_only", "sentiment": feedback.sentiment.value},
                )
            )

        self._events.extend(events)
        return events

    async def _process_rating(self, feedback: FeedbackItem) -> list[PipelineEvent]:
        """Process rating feedback - queue for training if high enough."""
        events: list[PipelineEvent] = []

        if feedback.rating and feedback.rating >= self.config.min_rating_for_training:
            self._training_examples_count += 1
            events.append(
                PipelineEvent(
                    feedback_id=feedback.id,
                    action=PipelineAction.TRAINING_EXPORT,
                    details={
                        "rating": feedback.rating,
                        "recommendation_type": feedback.recommendation_type.value,
                        "queued": True,
                    },
                )
            )
        else:
            events.append(
                PipelineEvent(
                    feedback_id=feedback.id,
                    action=PipelineAction.IGNORED,
                    details={
                        "reason": "rating_below_threshold",
                        "rating": feedback.rating,
                        "threshold": self.config.min_rating_for_training,
                    },
                )
            )

        return events

    async def _process_correction(self, feedback: FeedbackItem) -> list[PipelineEvent]:
        """Process correction feedback - always useful for training."""
        events: list[PipelineEvent] = []

        if self.config.include_corrections_in_training:
            self._training_examples_count += 1
            events.append(
                PipelineEvent(
                    feedback_id=feedback.id,
                    action=PipelineAction.TRAINING_EXPORT,
                    details={
                        "type": "correction",
                        "recommendation_type": feedback.recommendation_type.value,
                        "has_original": bool(feedback.context.get("original_recommendation")),
                    },
                )
            )

        return events

    async def _process_thumbs(self, feedback: FeedbackItem) -> list[PipelineEvent]:
        """Process thumbs feedback."""
        events: list[PipelineEvent] = []

        if feedback.thumbs_up:
            # Positive thumbs can supplement training data
            self._training_examples_count += 1
            events.append(
                PipelineEvent(
                    feedback_id=feedback.id,
                    action=PipelineAction.TRAINING_EXPORT,
                    details={
                        "thumbs_up": True,
                        "recommendation_type": feedback.recommendation_type.value,
                    },
                )
            )
        else:
            events.append(
                PipelineEvent(
                    feedback_id=feedback.id,
                    action=PipelineAction.IGNORED,
                    details={"reason": "thumbs_down_no_correction"},
                )
            )

        return events

    async def _process_outcome(self, feedback: FeedbackItem) -> list[PipelineEvent]:
        """
        Process outcome feedback - record experience and potentially trigger SOP.
        معالجة تغذية راجعة عن النتيجة - تسجيل الخبرة وربما تفعيل إجراء تشغيل قياسي.
        """
        events: list[PipelineEvent] = []

        if feedback.outcome is None:
            return events

        # Map outcome to execution status for the experience learner
        outcome_to_status = {
            OutcomeStatus.SUCCESS: ExecutionStatus.SUCCESS,
            OutcomeStatus.PARTIAL_SUCCESS: ExecutionStatus.PARTIAL,
            OutcomeStatus.PARTIAL: ExecutionStatus.PARTIAL,
            OutcomeStatus.FAILURE: ExecutionStatus.FAILURE,
            OutcomeStatus.NOT_APPLICABLE: ExecutionStatus.SUCCESS,
            OutcomeStatus.PENDING: ExecutionStatus.SUCCESS,
            OutcomeStatus.UNKNOWN: ExecutionStatus.PARTIAL,
            OutcomeStatus.NOT_APPLIED: ExecutionStatus.FAILURE,
        }
        exec_status = outcome_to_status.get(feedback.outcome, ExecutionStatus.PARTIAL)

        # Build execution steps from feedback context
        steps = [
            ExecutionStep(
                step_number=1,
                action=f"recommendation_{feedback.recommendation_type.value}",
                action_ar=f"توصية_{feedback.recommendation_type.value}",
                parameters={
                    "recommendation_id": feedback.recommendation_id,
                    "recommendation_type": feedback.recommendation_type.value,
                },
                result={
                    "outcome": feedback.outcome.value,
                    "yield_impact": feedback.yield_impact,
                    "cost_impact": feedback.cost_impact,
                },
                success=exec_status == ExecutionStatus.SUCCESS,
            ),
        ]

        # Record execution in experience learner
        task_type = f"advisory_{feedback.recommendation_type.value}"
        outcome_score = None
        if feedback.outcome == OutcomeStatus.SUCCESS:
            outcome_score = 1.0
        elif feedback.outcome in (OutcomeStatus.PARTIAL_SUCCESS, OutcomeStatus.PARTIAL):
            outcome_score = 0.5
        elif feedback.outcome == OutcomeStatus.FAILURE:
            outcome_score = 0.0

        execution = await self.learner.record_execution(
            task_type=task_type,
            task_description=feedback.outcome_details or f"Advisory outcome for {feedback.recommendation_type.value}",
            task_description_ar=feedback.outcome_details_ar,
            steps=steps,
            status=exec_status,
            context={
                "feedback_id": feedback.id,
                "recommendation_id": feedback.recommendation_id,
                "yield_impact": feedback.yield_impact,
                "cost_impact": feedback.cost_impact,
                **feedback.context,
            },
            tenant_id=self.tenant_id,
            agent_id=self.config.default_agent_id,
            outcome_score=outcome_score,
            metadata={"source": "feedback_pipeline"},
        )

        events.append(
            PipelineEvent(
                feedback_id=feedback.id,
                action=PipelineAction.EXPERIENCE_RECORD,
                details={
                    "execution_id": execution.id,
                    "task_type": task_type,
                    "status": exec_status.value,
                    "outcome_score": outcome_score,
                },
            )
        )

        # If successful outcome, also queue for training
        if feedback.outcome == OutcomeStatus.SUCCESS:
            self._training_examples_count += 1
            events.append(
                PipelineEvent(
                    feedback_id=feedback.id,
                    action=PipelineAction.TRAINING_EXPORT,
                    details={
                        "type": "successful_outcome",
                        "yield_impact": feedback.yield_impact,
                        "cost_impact": feedback.cost_impact,
                    },
                )
            )

        # Check if we should trigger automatic SOP update
        if self.config.auto_sop_enabled and feedback.outcome == OutcomeStatus.SUCCESS:
            sop_events = await self._maybe_trigger_sop(feedback, task_type)
            events.extend(sop_events)

        return events

    async def _maybe_trigger_sop(
        self,
        feedback: FeedbackItem,
        task_type: str,
    ) -> list[PipelineEvent]:
        """Check if enough successful outcomes have accumulated to create/update SOP."""
        events: list[PipelineEvent] = []

        successful_execs = await self.learner.store.get_executions_by_type(task_type, status=ExecutionStatus.SUCCESS)

        # Filter by yield impact threshold if configured
        if self.config.min_yield_impact_for_sop > 0:
            successful_execs = [e for e in successful_execs if (e.outcome_score or 0) >= 0.5]

        if len(successful_execs) >= self.config.min_outcomes_for_sop:
            existing_sops = await self.learner.store.get_sops_by_type(task_type)

            if existing_sops:
                self._sops_updated += 1
                events.append(
                    PipelineEvent(
                        feedback_id=feedback.id,
                        action=PipelineAction.SOP_UPDATE,
                        details={
                            "task_type": task_type,
                            "sop_id": existing_sops[0].id,
                            "successful_executions": len(successful_execs),
                            "confidence": existing_sops[0].confidence.value,
                        },
                    )
                )
            else:
                self._sops_created += 1
                events.append(
                    PipelineEvent(
                        feedback_id=feedback.id,
                        action=PipelineAction.SOP_CREATE,
                        details={
                            "task_type": task_type,
                            "successful_executions": len(successful_execs),
                        },
                    )
                )

        return events

    # ------------------------------------------------------------------
    # 2. export_training_data
    # ------------------------------------------------------------------

    async def export_training_data(
        self,
        recommendation_type: RecommendationType | None = None,
        min_rating: int | None = None,
        dataset_name: str | None = None,
        dataset_name_ar: str | None = None,
    ) -> TrainingDataset:
        """
        Export high-quality feedback as a TrainingDataset for model fine-tuning.
        تصدير التغذية الراجعة عالية الجودة كمجموعة بيانات تدريب لضبط النماذج.

        Collects:
        - Highly rated recommendations as positive examples
        - Corrections as negative/corrected example pairs
        - Successful outcomes with yield improvement as reinforcement examples

        Args:
            recommendation_type: Filter by recommendation type (None = all)
            min_rating: Override minimum rating (default from config)
            dataset_name: Custom dataset name
            dataset_name_ar: Custom dataset name in Arabic

        Returns:
            TrainingDataset ready for use with ModelTrainer
        """
        effective_min_rating = min_rating or self.config.min_rating_for_training

        # Get raw training data from collector
        raw_training_data = await self.collector.export_for_training(
            min_rating=effective_min_rating,
            include_corrections=self.config.include_corrections_in_training,
        )

        # Filter by recommendation type if specified
        if recommendation_type:
            raw_training_data = [
                d for d in raw_training_data if d.get("recommendation_type") == recommendation_type.value
            ]

        # Build the training dataset
        builder = DatasetBuilder()

        for item in raw_training_data:
            item_type = item.get("type", "")
            context = item.get("context", {})

            if item_type == "positive_example":
                # Use the recommendation context to create advisory training example
                query = context.get("query", context.get("original_query", ""))
                response = context.get("recommendation", context.get("original_recommendation", ""))
                crop = context.get("crop_type", None)

                if query and response:
                    builder.add_agricultural_advisory_example(
                        query=query,
                        response=response,
                        crop_type=crop,
                        language_code=context.get("language", "en"),
                    )

            elif item_type == "correction":
                corrected = item.get("corrected_response", "")
                query = context.get("query", context.get("original_query", ""))

                if query and corrected:
                    # Add the corrected version as a positive example
                    builder.add_agricultural_advisory_example(
                        query=query,
                        response=corrected,
                        crop_type=context.get("crop_type"),
                        language_code=context.get("language", "en"),
                    )

            elif item_type == "successful_outcome":
                query = context.get("query", context.get("original_query", ""))
                response = context.get("recommendation", context.get("original_recommendation", ""))
                crop = context.get("crop_type", None)
                yield_impact = item.get("yield_impact")

                if query and response:
                    # Successful outcomes are strong positive signals
                    metadata_note = ""
                    if yield_impact and yield_impact > 0:
                        metadata_note = f" [Verified: +{yield_impact:.1f}% yield]"
                    builder.add_agricultural_advisory_example(
                        query=query,
                        response=response + metadata_note,
                        crop_type=crop,
                        language_code=context.get("language", "en"),
                    )

        name = dataset_name or f"feedback-{self.tenant_id}-{datetime.now(UTC).strftime('%Y%m%d')}"
        name_ar = dataset_name_ar or f"تغذية-راجعة-{self.tenant_id}-{datetime.now(UTC).strftime('%Y%m%d')}"

        dataset = builder.build(
            name=name,
            name_ar=name_ar,
            description=f"Training dataset from {len(raw_training_data)} feedback items",
            description_ar=f"مجموعة بيانات تدريب من {len(raw_training_data)} عنصر تغذية راجعة",
        )

        logger.info(
            "Training data exported: %d examples from %d feedback items",
            len(dataset.examples),
            len(raw_training_data),
        )

        return dataset

    # ------------------------------------------------------------------
    # 3. trigger_sop_update
    # ------------------------------------------------------------------

    async def trigger_sop_update(
        self,
        recommendation_type: RecommendationType | None = None,
    ) -> list[PipelineEvent]:
        """
        Manually trigger SOP generation/update based on accumulated outcomes.
        تفعيل توليد/تحديث إجراء التشغيل القياسي يدوياً بناءً على النتائج المتراكمة.

        Scans all advisory task types (or a specific one) for enough successful
        outcomes to justify creating or updating an SOP.

        Args:
            recommendation_type: Specific type to check (None = check all)

        Returns:
            List of PipelineEvents describing SOP actions taken
        """
        events: list[PipelineEvent] = []

        if recommendation_type:
            types_to_check = [recommendation_type]
        else:
            types_to_check = list(RecommendationType)

        for rec_type in types_to_check:
            task_type = f"advisory_{rec_type.value}"
            successful_execs = await self.learner.store.get_executions_by_type(
                task_type, status=ExecutionStatus.SUCCESS
            )

            if len(successful_execs) < self.config.min_outcomes_for_sop:
                continue

            # Check recency - only consider executions within the window
            cutoff = datetime.now(UTC) - timedelta(days=self.config.sop_trigger_window_days)
            recent_successful = [e for e in successful_execs if e.timestamp >= cutoff]

            if len(recent_successful) < self.config.min_outcomes_for_sop:
                continue

            # Use the learner's internal SOP generation
            existing_sops = await self.learner.store.get_sops_by_type(task_type)
            sop = await self.learner._generate_or_update_sop(task_type, recent_successful)

            if existing_sops:
                self._sops_updated += 1
                events.append(
                    PipelineEvent(
                        feedback_id="",
                        action=PipelineAction.SOP_UPDATE,
                        details={
                            "task_type": task_type,
                            "sop_id": sop.id,
                            "successful_executions": len(recent_successful),
                            "confidence": sop.confidence.value,
                            "success_rate": f"{sop.success_rate:.1%}",
                        },
                    )
                )
            else:
                self._sops_created += 1
                events.append(
                    PipelineEvent(
                        feedback_id="",
                        action=PipelineAction.SOP_CREATE,
                        details={
                            "task_type": task_type,
                            "sop_id": sop.id,
                            "successful_executions": len(recent_successful),
                            "confidence": sop.confidence.value,
                        },
                    )
                )

            logger.info(
                "SOP %s for task_type=%s confidence=%s executions=%d",
                "updated" if existing_sops else "created",
                task_type,
                sop.confidence.value,
                len(recent_successful),
            )

        self._events.extend(events)
        return events

    # ------------------------------------------------------------------
    # 4. get_improvement_report
    # ------------------------------------------------------------------

    async def get_improvement_report(
        self,
        days: int = 30,
    ) -> dict[str, Any]:
        """
        Generate a report summarizing model improvement over time.
        توليد تقرير يلخص تحسين النموذج عبر الزمن.

        Combines feedback summary, training data stats, and SOP health
        into a unified improvement report.

        Args:
            days: Number of days to include in the report

        Returns:
            Dictionary with improvement metrics and trends
        """
        # Get feedback summary
        summary = await self.collector.get_summary(days=days)

        # Get experience stats
        learning_stats = await self.learner.get_learning_stats()

        # Build per-type breakdown
        type_breakdown: dict[str, dict[str, Any]] = {}
        for rec_type in RecommendationType:
            task_type = f"advisory_{rec_type.value}"
            type_execs = await self.learner.store.get_executions_by_type(task_type)
            type_sops = await self.learner.store.get_sops_by_type(task_type)
            best_sop = await self.learner.store.get_best_sop(task_type)

            if not type_execs and rec_type.value not in summary.by_recommendation_type:
                continue

            successful = len([e for e in type_execs if e.status == ExecutionStatus.SUCCESS])
            failed = len([e for e in type_execs if e.status == ExecutionStatus.FAILURE])

            type_breakdown[rec_type.value] = {
                "total_executions": len(type_execs),
                "successful": successful,
                "failed": failed,
                "success_rate": successful / len(type_execs) if type_execs else 0.0,
                "sops_count": len(type_sops),
                "best_sop_confidence": best_sop.confidence.value if best_sop else None,
                "best_sop_success_rate": f"{best_sop.success_rate:.1%}" if best_sop else None,
                "feedback": summary.by_recommendation_type.get(rec_type.value, {}),
            }

        # Create snapshot for history
        snapshot = ImprovementSnapshot(
            total_feedback=summary.total_feedback,
            positive_feedback=summary.positive_count,
            negative_feedback=summary.negative_count,
            avg_rating=summary.average_rating,
            success_rate=summary.success_rate,
            training_examples_generated=self._training_examples_count,
            sops_created=self._sops_created,
            sops_updated=self._sops_updated,
            avg_yield_impact=summary.average_yield_impact,
        )
        self._improvement_history.append(snapshot)

        # Compute trend from history (if we have multiple snapshots)
        trend = self._compute_trend()

        report = {
            "period_days": days,
            "generated_at": datetime.now(UTC).isoformat(),
            "generated_at_ar": datetime.now(UTC).strftime("%Y-%m-%d %H:%M"),
            "summary": {
                "total_feedback": summary.total_feedback,
                "average_rating": round(summary.average_rating, 2),
                "success_rate": round(summary.success_rate, 3),
                "average_yield_impact": round(summary.average_yield_impact, 2),
                "thumbs_up": summary.thumbs_up_count,
                "thumbs_down": summary.thumbs_down_count,
            },
            "summary_ar": {
                "إجمالي_التغذية_الراجعة": summary.total_feedback,
                "متوسط_التقييم": round(summary.average_rating, 2),
                "معدل_النجاح": round(summary.success_rate, 3),
                "متوسط_تأثير_الإنتاجية": round(summary.average_yield_impact, 2),
            },
            "training": {
                "examples_generated": self._training_examples_count,
                "pipeline_events": len(self._events),
            },
            "sops": {
                "created": self._sops_created,
                "updated": self._sops_updated,
                "total_sops": learning_stats.get("total_sops", 0),
                "high_confidence": learning_stats.get("high_confidence_sops", 0),
            },
            "experience": {
                "total_executions": learning_stats.get("total_executions", 0),
                "success_rate": learning_stats.get("success_rate", 0),
                "task_types_covered": learning_stats.get("task_types_covered", []),
            },
            "by_type": type_breakdown,
            "trend": trend,
        }

        return report

    def _compute_trend(self) -> dict[str, Any]:
        """Compute improvement trend from snapshot history."""
        if len(self._improvement_history) < 2:
            return {
                "available": False,
                "message": "Not enough data for trend analysis",
                "message_ar": "لا توجد بيانات كافية لتحليل الاتجاه",
            }

        latest = self._improvement_history[-1]
        previous = self._improvement_history[-2]

        rating_change = latest.avg_rating - previous.avg_rating
        success_change = latest.success_rate - previous.success_rate
        yield_change = latest.avg_yield_impact - previous.avg_yield_impact

        # Determine overall direction
        positive_signals = sum(
            [
                rating_change > 0,
                success_change > 0,
                yield_change > 0,
                latest.sops_created > 0 or latest.sops_updated > 0,
            ]
        )

        if positive_signals >= 3:
            direction = "improving"
            direction_ar = "تحسن"
        elif positive_signals >= 2:
            direction = "stable"
            direction_ar = "مستقر"
        else:
            direction = "declining"
            direction_ar = "تراجع"

        return {
            "available": True,
            "direction": direction,
            "direction_ar": direction_ar,
            "rating_change": round(rating_change, 2),
            "success_rate_change": round(success_change, 3),
            "yield_impact_change": round(yield_change, 2),
            "snapshots": len(self._improvement_history),
        }

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

    def get_pipeline_events(
        self,
        action: PipelineAction | None = None,
        limit: int = 100,
    ) -> list[PipelineEvent]:
        """
        Get pipeline event history with optional filtering.
        الحصول على سجل أحداث خط الأنابيب مع تصفية اختيارية.
        """
        events = self._events
        if action:
            events = [e for e in events if e.action == action]
        return events[-limit:]

    def get_config(self) -> dict[str, Any]:
        """Get pipeline configuration as dict."""
        return self.config.to_dict()


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------

_pipelines: dict[str, FeedbackTrainingPipeline] = {}


def get_feedback_training_pipeline(
    tenant_id: str,
    config: PipelineConfig | None = None,
) -> FeedbackTrainingPipeline:
    """
    Get or create a feedback training pipeline for a tenant.
    الحصول على أو إنشاء خط أنابيب تدريب التغذية الراجعة للمستأجر.
    """
    if tenant_id not in _pipelines:
        _pipelines[tenant_id] = FeedbackTrainingPipeline(
            tenant_id=tenant_id,
            config=config,
        )
    return _pipelines[tenant_id]
