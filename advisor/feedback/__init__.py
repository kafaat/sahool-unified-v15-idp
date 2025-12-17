"""
SAHOOL Feedback Module
User feedback on AI recommendations
"""

from .models import AdvisorFeedback, FeedbackType, FeedbackRating
from .service import FeedbackService

__all__ = [
    "AdvisorFeedback",
    "FeedbackType",
    "FeedbackRating",
    "FeedbackService",
]
