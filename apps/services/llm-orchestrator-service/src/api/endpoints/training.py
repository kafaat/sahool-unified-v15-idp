"""
Training API Endpoints
نقاط نهاية API للتدريب

Agent Lightning integration for automatic agent optimization.
"""

from datetime import UTC, datetime
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from ...training import (
    AGLTrainer,
    FeedbackCollector,
    TrainingConfig,
    TrainingResult,
)
from ...training.agl_trainer import OptimizationAlgorithm, TrainingStatus
from ...training.feedback_collector import FeedbackType, OutcomeStatus

# Authentication dependency
try:
    from shared.auth.dependencies import get_current_user
except ImportError:
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
    _bearer_scheme = HTTPBearer(auto_error=False)
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    ):
        """Lightweight auth - validates Authorization header presence."""
        if not credentials:
            raise HTTPException(status_code=401, detail="Authentication required")
        return {"token": credentials.credentials}

logger = structlog.get_logger()

router = APIRouter(
    prefix="/api/v1/training",
    tags=["Training | التدريب"],
)

# Global instances (initialized in main.py lifespan)
trainer: AGLTrainer | None = None
feedback_collector: FeedbackCollector | None = None


def get_trainer() -> AGLTrainer:
    """Get trainer instance."""
    if trainer is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Training service not initialized",
        )
    return trainer


def get_feedback_collector() -> FeedbackCollector:
    """Get feedback collector instance."""
    if feedback_collector is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Feedback collector not initialized",
        )
    return feedback_collector


# ==============================================================================
# Schemas
# ==============================================================================


class TrainingRequest(BaseModel):
    """Request to start agent training."""

    agent_names: list[str] = Field(
        ...,
        description="Names of agents to train | أسماء الوكلاء للتدريب",
        examples=[["crop-intelligence", "advisory"]],
    )
    algorithm: OptimizationAlgorithm = Field(
        default=OptimizationAlgorithm.APO,
        description="Optimization algorithm | خوارزمية التحسين",
    )
    num_iterations: int = Field(
        default=100,
        ge=10,
        le=1000,
        description="Number of training iterations | عدد تكرارات التدريب",
    )
    learning_rate: float = Field(
        default=1e-4,
        gt=0,
        lt=1,
        description="Learning rate | معدل التعلم",
    )


class TrainingResponse(BaseModel):
    """Response for training operations."""

    success: bool
    job_id: str | None = None
    status: TrainingStatus | None = None
    message: str | None = None
    message_ar: str | None = None


class TrainingJobResponse(BaseModel):
    """Detailed training job response."""

    job_id: str
    status: TrainingStatus
    agent_name: str
    algorithm: OptimizationAlgorithm
    initial_reward: float
    final_reward: float
    improvement_percent: float
    iterations_completed: int
    started_at: datetime | None
    completed_at: datetime | None
    duration_seconds: float
    optimized_prompt: str | None = None
    error_message: str | None = None


class FeedbackRequest(BaseModel):
    """Request to record feedback."""

    session_id: str = Field(..., description="Session ID | معرف الجلسة")
    agent_name: str = Field(..., description="Agent name | اسم الوكيل")
    user_input: str = Field(..., description="Original user input | مدخل المستخدم الأصلي")
    agent_response: str = Field(..., description="Agent's response | استجابة الوكيل")
    feedback_type: FeedbackType = Field(
        ...,
        description="Type of feedback | نوع التغذية الراجعة",
    )
    rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
        description="Rating 1-5 | التقييم 1-5",
    )
    correction: str | None = Field(
        default=None,
        description="User's correction | تصحيح المستخدم",
    )
    user_id: str | None = None
    tenant_id: str | None = None
    field_id: str | None = None
    crop_type: str | None = None
    intent_type: str | None = None


class FeedbackResponse(BaseModel):
    """Response for feedback operations."""

    success: bool
    feedback_id: str | None = None
    message: str | None = None
    message_ar: str | None = None


class OutcomeRequest(BaseModel):
    """Request to record outcome."""

    feedback_id: str = Field(..., description="Feedback ID | معرف التغذية الراجعة")
    outcome: OutcomeStatus = Field(..., description="Outcome status | حالة النتيجة")
    notes: str | None = Field(default=None, description="Notes | ملاحظات")


class StatisticsResponse(BaseModel):
    """Feedback statistics response."""

    total: int
    positive_count: int
    negative_count: int
    positive_rate: float
    average_rating: float
    ratings_count: int
    corrections_count: int
    with_outcomes: int
    success_rate: float
    by_type: dict[str, int]


# ==============================================================================
# Training Endpoints
# ==============================================================================


@router.post("/start", response_model=TrainingResponse)
async def start_training(request: TrainingRequest, _user=Depends(get_current_user)) -> TrainingResponse:
    """
    Start a training job for specified agents.
    بدء مهمة تدريب للوكلاء المحددين

    Uses Agent Lightning for:
    - APO: Automatic Prompt Optimization
    - SFT: Supervised Fine-Tuning
    - RL: Reinforcement Learning (REINFORCE, PPO)
    - DPO: Direct Preference Optimization
    """
    t = get_trainer()
    fc = get_feedback_collector()

    # Get training data from feedback
    training_data = await fc.get_training_data(agent_name=request.agent_names[0] if request.agent_names else None)

    config = TrainingConfig(
        agent_names=request.agent_names,
        algorithm=request.algorithm,
        num_iterations=request.num_iterations,
        learning_rate=request.learning_rate,
    )

    result = await t.start_training(config, training_data)

    if result.status == TrainingStatus.FAILED:
        return TrainingResponse(
            success=False,
            job_id=result.job_id,
            status=result.status,
            message=result.error_message,
            message_ar="فشل بدء التدريب",
        )

    return TrainingResponse(
        success=True,
        job_id=result.job_id,
        status=result.status,
        message=f"Training started for agents: {', '.join(request.agent_names)}",
        message_ar=f"بدأ التدريب للوكلاء: {', '.join(request.agent_names)}",
    )


@router.get("/jobs/{job_id}", response_model=TrainingJobResponse)
async def get_training_job(job_id: str) -> TrainingJobResponse:
    """
    Get status of a training job.
    الحصول على حالة مهمة التدريب
    """
    t = get_trainer()
    result = await t.get_job_status(job_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training job {job_id} not found",
        )

    return TrainingJobResponse(
        job_id=result.job_id,
        status=result.status,
        agent_name=result.agent_name,
        algorithm=result.algorithm,
        initial_reward=result.initial_reward,
        final_reward=result.final_reward,
        improvement_percent=result.improvement_percent,
        iterations_completed=result.iterations_completed,
        started_at=result.started_at,
        completed_at=result.completed_at,
        duration_seconds=result.duration_seconds,
        optimized_prompt=result.optimized_prompt,
        error_message=result.error_message,
    )


@router.get("/jobs", response_model=list[TrainingJobResponse])
async def list_training_jobs(
    status_filter: TrainingStatus | None = Query(
        default=None,
        description="Filter by status | تصفية حسب الحالة",
    ),
    limit: int = Query(default=10, ge=1, le=100),
) -> list[TrainingJobResponse]:
    """
    List training jobs.
    عرض قائمة مهام التدريب
    """
    t = get_trainer()
    jobs = await t.list_jobs(status=status_filter, limit=limit)

    return [
        TrainingJobResponse(
            job_id=j.job_id,
            status=j.status,
            agent_name=j.agent_name,
            algorithm=j.algorithm,
            initial_reward=j.initial_reward,
            final_reward=j.final_reward,
            improvement_percent=j.improvement_percent,
            iterations_completed=j.iterations_completed,
            started_at=j.started_at,
            completed_at=j.completed_at,
            duration_seconds=j.duration_seconds,
            optimized_prompt=j.optimized_prompt,
            error_message=j.error_message,
        )
        for j in jobs
    ]


@router.post("/jobs/{job_id}/cancel", response_model=TrainingResponse)
async def cancel_training_job(job_id: str) -> TrainingResponse:
    """
    Cancel a running training job.
    إلغاء مهمة تدريب جارية
    """
    t = get_trainer()
    success = await t.cancel_job(job_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job {job_id} - not running or not found",
        )

    return TrainingResponse(
        success=True,
        job_id=job_id,
        status=TrainingStatus.CANCELLED,
        message="Training job cancelled",
        message_ar="تم إلغاء مهمة التدريب",
    )


@router.get("/prompts/{agent_name}")
async def get_optimized_prompt(agent_name: str) -> dict[str, Any]:
    """
    Get the optimized prompt for an agent.
    الحصول على الموجه المحسن للوكيل
    """
    t = get_trainer()
    prompt = await t.get_optimized_prompt(agent_name)

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No optimized prompt found for agent: {agent_name}",
        )

    return {
        "agent_name": agent_name,
        "optimized_prompt": prompt,
        "retrieved_at": datetime.now(UTC).isoformat(),
    }


# ==============================================================================
# Feedback Endpoints
# ==============================================================================


@router.post("/feedback", response_model=FeedbackResponse)
async def record_feedback(request: FeedbackRequest) -> FeedbackResponse:
    """
    Record feedback on an agent's response.
    تسجيل تغذية راجعة على استجابة الوكيل

    Feedback types:
    - thumbs_up: User liked the response
    - thumbs_down: User disliked the response
    - rating: 1-5 star rating
    - correction: User provides the correct answer
    - outcome: Did following the advice work?
    """
    fc = get_feedback_collector()

    feedback = await fc.record_feedback(
        session_id=request.session_id,
        agent_name=request.agent_name,
        user_input=request.user_input,
        agent_response=request.agent_response,
        feedback_type=request.feedback_type,
        rating=request.rating,
        correction=request.correction,
        user_id=request.user_id,
        tenant_id=request.tenant_id,
        field_id=request.field_id,
        crop_type=request.crop_type,
        intent_type=request.intent_type,
    )

    return FeedbackResponse(
        success=True,
        feedback_id=feedback.feedback_id,
        message="Feedback recorded successfully",
        message_ar="تم تسجيل التغذية الراجعة بنجاح",
    )


@router.post("/feedback/outcome", response_model=FeedbackResponse)
async def record_outcome(request: OutcomeRequest) -> FeedbackResponse:
    """
    Record the outcome after following agent advice.
    تسجيل النتيجة بعد اتباع نصيحة الوكيل

    Outcome statuses:
    - success: The advice worked perfectly
    - partial: The advice partially helped
    - failure: The advice didn't help
    - unknown: Not yet determined
    """
    fc = get_feedback_collector()

    feedback = await fc.record_outcome(
        feedback_id=request.feedback_id,
        outcome=request.outcome,
        notes=request.notes,
    )

    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback {request.feedback_id} not found",
        )

    return FeedbackResponse(
        success=True,
        feedback_id=feedback.feedback_id,
        message="Outcome recorded successfully",
        message_ar="تم تسجيل النتيجة بنجاح",
    )


@router.get("/feedback/statistics", response_model=StatisticsResponse)
async def get_feedback_statistics(
    agent_name: str | None = Query(
        default=None,
        description="Filter by agent | تصفية حسب الوكيل",
    ),
) -> StatisticsResponse:
    """
    Get feedback statistics.
    الحصول على إحصائيات التغذية الراجعة
    """
    fc = get_feedback_collector()
    stats = await fc.get_statistics(agent_name=agent_name)
    return StatisticsResponse(**stats)


@router.get("/feedback/export")
async def export_training_data(
    agent_name: str | None = Query(default=None),
    min_rating: int | None = Query(default=None, ge=1, le=5),
    outcome_filter: OutcomeStatus | None = Query(default=None),
) -> dict[str, Any]:
    """
    Export feedback as training data.
    تصدير التغذية الراجعة كبيانات تدريب
    """
    fc = get_feedback_collector()
    data = await fc.get_training_data(
        agent_name=agent_name,
        min_rating=min_rating,
        outcome_filter=outcome_filter,
    )

    return {
        "count": len(data),
        "exported_at": datetime.now(UTC).isoformat(),
        "filters": {
            "agent_name": agent_name,
            "min_rating": min_rating,
            "outcome_filter": outcome_filter.value if outcome_filter else None,
        },
        "data": data,
    }


# ==============================================================================
# Health Check
# ==============================================================================


@router.get("/health")
async def training_health() -> dict[str, Any]:
    """
    Check training service health.
    فحص صحة خدمة التدريب
    """
    t = get_trainer() if trainer else None
    agl_available = await t.check_availability() if t else False

    return {
        "status": "ok" if t else "degraded",
        "trainer_enabled": t.enabled if t else False,
        "agl_available": agl_available,
        "feedback_collector": feedback_collector is not None,
        "timestamp": datetime.now(UTC).isoformat(),
    }
