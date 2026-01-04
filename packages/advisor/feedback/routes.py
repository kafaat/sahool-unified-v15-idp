"""
SAHOOL AI Feedback API Routes
نقاط API للتغذية الراجعة
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .models import FeedbackType
from .service import get_feedback_stats, submit_feedback

router = APIRouter(prefix="/ai/feedback", tags=["ai-feedback"])


class FeedbackRequest(BaseModel):
    """طلب تقديم تغذية راجعة."""

    trace_id: str
    query: str
    feedback_type: FeedbackType
    rating: int | None = Field(None, ge=1, le=5)
    comment: str | None = Field(None, max_length=1000)
    correct_answer: str | None = None


class FeedbackResponse(BaseModel):
    """استجابة بعد تقديم التغذية الراجعة."""

    id: str
    status: str
    message: str


@router.post("", response_model=FeedbackResponse)
def submit(
    tenant_id: str,
    user_id: str,
    field_id: str,
    req: FeedbackRequest,
):
    """تقديم تغذية راجعة لتوصية الذكاء الاصطناعي."""
    try:
        feedback = submit_feedback(
            tenant_id=UUID(tenant_id),
            user_id=UUID(user_id),
            field_id=UUID(field_id),
            trace_id=req.trace_id,
            query=req.query,
            feedback_type=req.feedback_type,
            rating=req.rating,
            comment=req.comment,
            correct_answer=req.correct_answer,
        )

        return FeedbackResponse(
            id=str(feedback.id),
            status="ok",
            message="شكراً على تقييمك",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats")
def stats(tenant_id: str, days: int = 30):
    """الحصول على إحصائيات التغذية الراجعة."""
    return get_feedback_stats(UUID(tenant_id), days)
