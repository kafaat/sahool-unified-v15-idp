"""
SAHOOL Feedback Module
User feedback on AI recommendations
"""

from .models import AdvisorFeedback, FeedbackRating, FeedbackType
from .service import FeedbackService

__all__ = [
    "AdvisorFeedback",
    "FeedbackType",
    "FeedbackRating",
    "FeedbackService",
]
