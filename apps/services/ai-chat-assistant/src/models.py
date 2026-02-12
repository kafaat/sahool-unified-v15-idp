"""
Data models for AI Chat Assistant.
نماذج البيانات لمساعد الشات الذكي.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AIQuery(BaseModel):
    """AI query from chat service."""
    
    query: str = Field(..., description="User question in Arabic or English")
    language: str = Field(default="ar", description="Query language (ar/en)")
    user_id: str = Field(..., description="User ID")
    conversation_id: str = Field(..., description="Conversation ID")
    field_id: Optional[str] = Field(None, description="Field ID for context")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AIResponse(BaseModel):
    """AI response to send back to chat."""
    
    conversation_id: str
    answer: str = Field(..., description="Answer in query language")
    answer_en: Optional[str] = Field(None, description="English translation if query was Arabic")
    metadata: "ResponseMetadata"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ResponseMetadata(BaseModel):
    """Metadata about the AI response."""
    
    confidence: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    agents_used: List[str] = Field(default_factory=list, description="AI agents that contributed")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    cached: bool = Field(default=False, description="Whether response was cached")
    intent: Optional[str] = Field(None, description="Detected intent")
    should_escalate: bool = Field(default=False, description="Should escalate to human expert")
    escalation_reason: Optional[str] = Field(None, description="Reason for escalation")


class CachedResponse(BaseModel):
    """Cached AI response."""
    
    query: str
    answer: str
    answer_en: Optional[str] = None
    metadata: ResponseMetadata
    cached_at: datetime = Field(default_factory=datetime.utcnow)
    hit_count: int = Field(default=1, description="Number of times this cache was hit")


class RateLimitInfo(BaseModel):
    """Rate limit information for a user."""
    
    user_id: str
    queries_count: int = 0
    window_start: datetime = Field(default_factory=datetime.utcnow)
    is_limited: bool = False
    reset_at: Optional[datetime] = None
