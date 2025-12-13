"""
SAHOOL Advisor Core Service - Intelligent Agricultural Advisory
================================================================
Layer: Decision Services (Layer 3)
Purpose: AI-powered agricultural recommendations combining all signals
"""

import os
import asyncio
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any, Tuple
from contextlib import asynccontextmanager
import uuid
import json

from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, ForeignKey, Integer, Float, Date, select, update, delete, func, and_, or_
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import structlog
import enum

# Shared imports
import sys
sys.path.insert(0, '/app/shared')
from database import Database, BaseModel as DBBaseModel
from events.base_event import BaseEvent, EventBus
from utils.logging import setup_logging
from metrics import MetricsManager

# ============================================================================
# Configuration
# ============================================================================

class Settings:
    """Advisor Core service configuration"""
    SERVICE_NAME = "advisor-core"
    SERVICE_PORT = int(os.getenv("ADVISOR_CORE_PORT", "8090"))
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://sahool:sahool@postgres:5432/sahool_advisor")
    NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # AI Model Settings
    AI_MODEL_ENDPOINT = os.getenv("AI_MODEL_ENDPOINT", "")
    USE_LOCAL_MODEL = os.getenv("USE_LOCAL_MODEL", "true").lower() == "true"

settings = Settings()

# ============================================================================
# Logging & Metrics
# ============================================================================

setup_logging(settings.SERVICE_NAME)
logger = structlog.get_logger()

advisory_requests = Counter('advisory_requests_total', 'Advisory requests', ['advisory_type', 'status'])
advisory_latency = Histogram('advisory_latency_seconds', 'Advisory generation latency')

# ============================================================================
# Database Models
# ============================================================================

class AdvisoryCategory(str, enum.Enum):
    PLANTING = "planting"
    IRRIGATION = "irrigation"
    FERTILIZATION = "fertilization"
    PEST_CONTROL = "pest_control"
    DISEASE_MANAGEMENT = "disease_management"
    HARVESTING = "harvesting"
    WEATHER_ALERT = "weather_alert"
    MARKET = "market"
    GENERAL = "general"

class AdvisoryPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class AdvisoryStatus(str, enum.Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    COMPLETED = "completed"
    DISMISSED = "dismissed"
    EXPIRED = "expired"

class Advisory(DBBaseModel):
    """Agricultural advisory/recommendation"""
    __tablename__ = "advisories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Target
    field_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    field_name = Column(String(255), nullable=True)
    crop_id = Column(UUID(as_uuid=True), nullable=True)
    crop_name = Column(String(100), nullable=True)
    
    # Advisory Details
    category = Column(String(50), nullable=False)
    priority = Column(String(20), default=AdvisoryPriority.MEDIUM.value)
    
    title = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=False)
    
    summary = Column(Text, nullable=False)
    summary_ar = Column(Text, nullable=False)
    
    detailed_recommendation = Column(Text, nullable=True)
    detailed_recommendation_ar = Column(Text, nullable=True)
    
    # Reasoning
    reasoning = Column(Text, nullable=True)  # Why this recommendation
    reasoning_ar = Column(Text, nullable=True)
    
    # Source Signals (what triggered this advisory)
    source_signals = Column(JSON, default=[])  # [{signal_type, signal_id, summary}]
    
    # Actions
    recommended_actions = Column(JSON, default=[])  # [{action, description_ar, description_en, due_date}]
    
    # Timing
    action_window_start = Column(DateTime, nullable=True)
    action_window_end = Column(DateTime, nullable=True)
    optimal_time = Column(String(100), nullable=True)  # e.g., "early morning", "بعد الفجر"
    
    # Impact
    expected_impact = Column(Text, nullable=True)
    expected_impact_ar = Column(Text, nullable=True)
    risk_if_ignored = Column(Text, nullable=True)
    risk_if_ignored_ar = Column(Text, nullable=True)
    
    # Related Resources
    related_resources = Column(JSON, default=[])  # [{type, title, url}]
    
    # Traditional Knowledge
    related_proverb = Column(Text, nullable=True)  # Arabic agricultural proverb
    traditional_practice = Column(Text, nullable=True)
    
    # Status
    status = Column(String(20), default=AdvisoryStatus.ACTIVE.value)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(UUID(as_uuid=True), nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Feedback
    user_feedback = Column(String(20), nullable=True)  # helpful, not_helpful, partially_helpful
    feedback_notes = Column(Text, nullable=True)
    
    # AI/Model Info
    model_version = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Expiry
    expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AdvisoryTemplate(DBBaseModel):
    """Reusable advisory templates"""
    __tablename__ = "advisory_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    code = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=False)
    
    title_template = Column(String(500), nullable=False)
    title_template_ar = Column(String(500), nullable=False)
    
    summary_template = Column(Text, nullable=False)
    summary_template_ar = Column(Text, nullable=False)
    
    detailed_template = Column(Text, nullable=True)
    detailed_template_ar = Column(Text, nullable=True)
    
    default_priority = Column(String(20), default="medium")
    
    # Trigger conditions
    trigger_conditions = Column(JSON, default={})
    
    # Default actions
    default_actions = Column(JSON, default=[])
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ConversationSession(DBBaseModel):
    """Chat session with AI advisor"""
    __tablename__ = "conversation_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Context
    field_id = Column(UUID(as_uuid=True), nullable=True)
    crop_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Session
    is_active = Column(Boolean, default=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    
    # Messages stored in separate table
    messages = relationship("ConversationMessage", back_populates="session", cascade="all, delete-orphan")

class ConversationMessage(DBBaseModel):
    """Individual message in conversation"""
    __tablename__ = "conversation_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('conversation_sessions.id', ondelete='CASCADE'), nullable=False)
    
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    content_ar = Column(Text, nullable=True)
    
    # For assistant messages
    sources_used = Column(JSON, default=[])  # What data was used to generate response
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("ConversationSession", back_populates="messages")

# ============================================================================
# Pydantic Schemas
# ============================================================================

class AdvisoryCreate(BaseModel):
    """Create advisory request"""
    tenant_id: uuid.UUID
    field_id: Optional[uuid.UUID] = None
    field_name: Optional[str] = None
    crop_id: Optional[uuid.UUID] = None
    crop_name: Optional[str] = None
    category: str
    priority: str = "medium"
    title: str
    title_ar: str
    summary: str
    summary_ar: str
    detailed_recommendation: Optional[str] = None
    detailed_recommendation_ar: Optional[str] = None
    reasoning: Optional[str] = None
    reasoning_ar: Optional[str] = None
    source_signals: Optional[List[Dict[str, Any]]] = []
    recommended_actions: Optional[List[Dict[str, Any]]] = []
    action_window_start: Optional[datetime] = None
    action_window_end: Optional[datetime] = None
    related_proverb: Optional[str] = None
    expires_at: Optional[datetime] = None
    confidence_score: Optional[float] = None

class AdvisoryResponse(BaseModel):
    """Advisory response"""
    id: uuid.UUID
    tenant_id: uuid.UUID
    field_id: Optional[uuid.UUID]
    field_name: Optional[str]
    crop_id: Optional[uuid.UUID]
    crop_name: Optional[str]
    category: str
    priority: str
    title: str
    title_ar: str
    summary: str
    summary_ar: str
    detailed_recommendation: Optional[str]
    detailed_recommendation_ar: Optional[str]
    reasoning: Optional[str]
    reasoning_ar: Optional[str]
    source_signals: List[Dict[str, Any]]
    recommended_actions: List[Dict[str, Any]]
    action_window_start: Optional[datetime]
    action_window_end: Optional[datetime]
    optimal_time: Optional[str]
    expected_impact: Optional[str]
    expected_impact_ar: Optional[str]
    risk_if_ignored: Optional[str]
    risk_if_ignored_ar: Optional[str]
    related_resources: List[Dict[str, Any]]
    related_proverb: Optional[str]
    traditional_practice: Optional[str]
    status: str
    acknowledged_at: Optional[datetime]
    confidence_score: Optional[float]
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AdvisoryGenerateRequest(BaseModel):
    """Request to generate advisory based on context"""
    tenant_id: uuid.UUID
    field_id: Optional[uuid.UUID] = None
    crop_name: Optional[str] = None
    category: Optional[str] = None  # If not specified, generate all relevant
    include_weather: bool = True
    include_ndvi: bool = True
    include_calendar: bool = True
    include_disease_risk: bool = True

class ChatMessage(BaseModel):
    """Chat message"""
    content: str
    language: str = "ar"  # ar or en

class ChatResponse(BaseModel):
    """Chat response"""
    message: str
    message_ar: Optional[str]
    sources: List[Dict[str, Any]]
    suggested_actions: List[str]
    related_advisories: List[uuid.UUID]

class FeedbackRequest(BaseModel):
    """Advisory feedback"""
    feedback: str  # helpful, not_helpful, partially_helpful
    notes: Optional[str] = None

# ============================================================================
# Advisory Engine
# ============================================================================

class AdvisoryEngine:
    """AI-powered advisory generation engine"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.model_version = "sahool-advisor-v1.0"
        
        # Load templates and knowledge base
        self._load_templates()
        self._load_knowledge_base()
    
    def _load_templates(self):
        """Load advisory templates"""
        self.templates = {
            "irrigation_needed": {
                "title_ar": "تنبيه: الحقل يحتاج للري",
                "title_en": "Alert: Field needs irrigation",
                "priority": "high"
            },
            "optimal_planting": {
                "title_ar": "فرصة: وقت مثالي للزراعة",
                "title_en": "Opportunity: Optimal planting time",
                "priority": "medium"
            },
            "disease_risk": {
                "title_ar": "تحذير: خطر إصابة بالأمراض",
                "title_en": "Warning: Disease risk detected",
                "priority": "high"
            },
            "harvest_ready": {
                "title_ar": "إشعار: المحصول جاهز للحصاد",
                "title_en": "Notice: Crop ready for harvest",
                "priority": "high"
            },
            "weather_alert": {
                "title_ar": "تنبيه طقس: اتخذ الاحتياطات",
                "title_en": "Weather Alert: Take precautions",
                "priority": "urgent"
            }
        }
    
    def _load_knowledge_base(self):
        """Load traditional agricultural knowledge"""
        self.proverbs = {
            "planting": [
                "ازرع في وقته تحصد في وقته",
                "من زرع حصد",
                "الأرض لا تخون من أحسن إليها"
            ],
            "irrigation": [
                "الماء عصب الحياة",
                "قليل الماء في وقته خير من كثيره في غير وقته"
            ],
            "weather": [
                "إذا هبت الرياح فانظر في السماء",
                "الغيوم الحمراء في المساء بشرى بيوم صاف"
            ],
            "harvesting": [
                "اجمع محصولك قبل أن يجمعه غيرك",
                "الحصاد في وقته بركة"
            ]
        }
        
        self.crop_knowledge = {
            "قمح": {
                "optimal_planting_months": [10, 11],
                "harvest_months": [4, 5],
                "water_needs": "medium",
                "common_diseases": ["صدأ الساق", "البياض الدقيقي"]
            },
            "قهوة": {
                "optimal_planting_months": [3, 4],
                "harvest_months": [10, 11, 12],
                "water_needs": "high",
                "altitude_preference": "high"
            },
            "طماطم": {
                "optimal_planting_months": [2, 3, 9, 10],
                "harvest_months": [5, 6, 7, 11, 12],
                "water_needs": "high",
                "common_diseases": ["اللفحة المتأخرة", "ذبول الفيوزاريوم"]
            }
        }
    
    async def generate_advisory(
        self,
        context: Dict[str, Any],
        category: Optional[str] = None
    ) -> List[Advisory]:
        """Generate advisories based on context"""
        advisories = []
        
        # Analyze context and generate relevant advisories
        if context.get("weather_data"):
            weather_advisories = await self._analyze_weather(context)
            advisories.extend(weather_advisories)
        
        if context.get("ndvi_data"):
            ndvi_advisories = await self._analyze_ndvi(context)
            advisories.extend(ndvi_advisories)
        
        if context.get("disease_risk"):
            disease_advisories = await self._analyze_disease_risk(context)
            advisories.extend(disease_advisories)
        
        if context.get("calendar_data"):
            calendar_advisories = await self._analyze_calendar(context)
            advisories.extend(calendar_advisories)
        
        # Filter by category if specified
        if category:
            advisories = [a for a in advisories if a.get("category") == category]
        
        return advisories
    
    async def _analyze_weather(self, context: Dict) -> List[Dict]:
        """Generate weather-based advisories"""
        advisories = []
        weather = context.get("weather_data", {})
        
        # High temperature alert
        if weather.get("max_temp", 0) > 40:
            advisories.append({
                "category": AdvisoryCategory.WEATHER_ALERT.value,
                "priority": AdvisoryPriority.URGENT.value,
                "title": "Extreme heat warning",
                "title_ar": "تحذير: موجة حر شديدة",
                "summary": f"Temperature expected to reach {weather.get('max_temp')}°C. Protect crops and increase irrigation.",
                "summary_ar": f"درجة الحرارة ستصل إلى {weather.get('max_temp')} درجة مئوية. احمِ المحاصيل وزد الري.",
                "recommended_actions": [
                    {"action": "increase_irrigation", "description_ar": "زيادة الري في الصباح الباكر والمساء"},
                    {"action": "shade_crops", "description_ar": "توفير الظل للمحاصيل الحساسة"}
                ],
                "related_proverb": "الماء عصب الحياة"
            })
        
        # Rain forecast
        if weather.get("rain_probability", 0) > 70:
            advisories.append({
                "category": AdvisoryCategory.WEATHER_ALERT.value,
                "priority": AdvisoryPriority.HIGH.value,
                "title": "Rain expected - adjust irrigation",
                "title_ar": "أمطار متوقعة - اضبط الري",
                "summary": f"Rain probability: {weather.get('rain_probability')}%. Consider reducing irrigation.",
                "summary_ar": f"احتمالية الأمطار: {weather.get('rain_probability')}%. فكر في تقليل الري.",
                "recommended_actions": [
                    {"action": "reduce_irrigation", "description_ar": "تقليل الري لتجنب الإفراط في الماء"},
                    {"action": "check_drainage", "description_ar": "تفقد نظام الصرف"}
                ]
            })
        
        return advisories
    
    async def _analyze_ndvi(self, context: Dict) -> List[Dict]:
        """Generate NDVI-based advisories"""
        advisories = []
        ndvi = context.get("ndvi_data", {})
        
        ndvi_value = ndvi.get("ndvi_mean", 0.5)
        
        if ndvi_value < 0.3:
            advisories.append({
                "category": AdvisoryCategory.GENERAL.value,
                "priority": AdvisoryPriority.HIGH.value,
                "title": "Low vegetation health detected",
                "title_ar": "انخفاض في صحة النباتات",
                "summary": f"NDVI value ({ndvi_value:.2f}) indicates stressed vegetation. Investigate cause.",
                "summary_ar": f"قيمة NDVI ({ndvi_value:.2f}) تشير إلى إجهاد في النباتات. تحقق من السبب.",
                "reasoning": "Low NDVI values typically indicate water stress, nutrient deficiency, or disease.",
                "reasoning_ar": "قيم NDVI المنخفضة عادة تشير إلى إجهاد مائي أو نقص مغذيات أو مرض.",
                "recommended_actions": [
                    {"action": "inspect_field", "description_ar": "فحص الحقل للتحقق من المشاكل"},
                    {"action": "check_irrigation", "description_ar": "التحقق من نظام الري"},
                    {"action": "soil_test", "description_ar": "إجراء اختبار للتربة"}
                ]
            })
        
        return advisories
    
    async def _analyze_disease_risk(self, context: Dict) -> List[Dict]:
        """Generate disease risk advisories"""
        advisories = []
        risk_data = context.get("disease_risk", {})
        
        if risk_data.get("risk_level") in ["high", "critical"]:
            disease_name = risk_data.get("disease_name", "Unknown")
            advisories.append({
                "category": AdvisoryCategory.DISEASE_MANAGEMENT.value,
                "priority": AdvisoryPriority.URGENT.value,
                "title": f"High disease risk: {disease_name}",
                "title_ar": f"خطر مرتفع: {risk_data.get('disease_name_ar', disease_name)}",
                "summary": f"Conditions favor {disease_name}. Take preventive action.",
                "summary_ar": f"الظروف مناسبة لـ{risk_data.get('disease_name_ar', disease_name)}. اتخذ إجراءات وقائية.",
                "risk_if_ignored": f"Crop damage can reach {risk_data.get('potential_damage', '30')}% if not treated.",
                "risk_if_ignored_ar": f"قد تصل الأضرار إلى {risk_data.get('potential_damage', '30')}% إذا لم تُعالج.",
                "recommended_actions": risk_data.get("recommended_actions", [])
            })
        
        return advisories
    
    async def _analyze_calendar(self, context: Dict) -> List[Dict]:
        """Generate calendar-based advisories (Yemeni agricultural calendar)"""
        advisories = []
        calendar = context.get("calendar_data", {})
        
        current_star = calendar.get("current_star")
        if current_star:
            # Check if any planting recommendations
            planting_crops = calendar.get("recommended_planting", [])
            if planting_crops:
                advisories.append({
                    "category": AdvisoryCategory.PLANTING.value,
                    "priority": AdvisoryPriority.MEDIUM.value,
                    "title": f"Optimal planting period - {current_star.get('name_ar', '')}",
                    "title_ar": f"فترة زراعة مثالية - نوء {current_star.get('name_ar', '')}",
                    "summary": f"Current star period is ideal for planting: {', '.join(planting_crops)}",
                    "summary_ar": f"الفترة الحالية مناسبة لزراعة: {', '.join(planting_crops)}",
                    "traditional_practice": current_star.get("agricultural_advice_ar"),
                    "related_proverb": self.proverbs["planting"][0] if self.proverbs["planting"] else None,
                    "action_window_start": datetime.utcnow(),
                    "action_window_end": datetime.utcnow() + timedelta(days=calendar.get("days_remaining", 7))
                })
        
        return advisories
    
    async def chat_response(
        self,
        message: str,
        context: Dict[str, Any],
        language: str = "ar"
    ) -> Dict[str, Any]:
        """Generate chat response with context"""
        # Simple rule-based responses for now
        # Can be enhanced with actual LLM integration
        
        response = {
            "message": "",
            "message_ar": "",
            "sources": [],
            "suggested_actions": [],
            "related_advisories": []
        }
        
        # Analyze question intent
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["ري", "irrigation", "water", "ماء"]):
            response["message_ar"] = "بناءً على بيانات الطقس والتربة المتاحة، أنصح بالري في الصباح الباكر لتقليل التبخر. تأكد من أن التربة رطبة حتى عمق 15-20 سم."
            response["message"] = "Based on available weather and soil data, I recommend irrigation early morning to reduce evaporation. Ensure soil is moist to 15-20cm depth."
            response["suggested_actions"] = ["schedule_irrigation", "check_soil_moisture"]
        
        elif any(word in message_lower for word in ["مرض", "disease", "آفة", "pest"]):
            response["message_ar"] = "للوقاية من الأمراض، تأكد من التهوية الجيدة بين النباتات وتجنب الري العلوي. إذا لاحظت أعراضاً، أرسل صورة للتشخيص."
            response["message"] = "For disease prevention, ensure good ventilation between plants and avoid overhead irrigation. If you notice symptoms, send an image for diagnosis."
            response["suggested_actions"] = ["upload_image", "view_disease_guide"]
        
        elif any(word in message_lower for word in ["زراعة", "planting", "plant", "زرع"]):
            response["message_ar"] = "أفضل وقت للزراعة يعتمد على نوع المحصول والظروف المناخية. حسب التقويم الفلكي اليمني، الفترة الحالية مناسبة لـ..."
            response["message"] = "Best planting time depends on crop type and climate conditions. According to the Yemeni astronomical calendar, the current period is suitable for..."
            response["suggested_actions"] = ["view_calendar", "check_crop_guide"]
        
        else:
            response["message_ar"] = "شكراً على سؤالك. يمكنني مساعدتك في الري، مكافحة الأمراض، أوقات الزراعة، وتوصيات المحاصيل. كيف يمكنني مساعدتك؟"
            response["message"] = "Thank you for your question. I can help with irrigation, disease control, planting times, and crop recommendations. How can I help you?"
        
        return response

# ============================================================================
# Advisor Service
# ============================================================================

class AdvisorService:
    """Core advisor service"""
    
    def __init__(self, db: Database, event_bus: EventBus):
        self.db = db
        self.event_bus = event_bus
        self.engine = AdvisoryEngine(event_bus)
    
    async def create_advisory(self, data: AdvisoryCreate) -> Advisory:
        """Create new advisory"""
        async with self.db.session() as session:
            advisory = Advisory(
                tenant_id=data.tenant_id,
                field_id=data.field_id,
                field_name=data.field_name,
                crop_id=data.crop_id,
                crop_name=data.crop_name,
                category=data.category,
                priority=data.priority,
                title=data.title,
                title_ar=data.title_ar,
                summary=data.summary,
                summary_ar=data.summary_ar,
                detailed_recommendation=data.detailed_recommendation,
                detailed_recommendation_ar=data.detailed_recommendation_ar,
                reasoning=data.reasoning,
                reasoning_ar=data.reasoning_ar,
                source_signals=data.source_signals or [],
                recommended_actions=data.recommended_actions or [],
                action_window_start=data.action_window_start,
                action_window_end=data.action_window_end,
                related_proverb=data.related_proverb,
                expires_at=data.expires_at,
                confidence_score=data.confidence_score,
                model_version=self.engine.model_version
            )
            
            session.add(advisory)
            await session.commit()
            await session.refresh(advisory)
            
            # Emit event
            await self.event_bus.publish(
                "advisor.advisory.created",
                {
                    "advisory_id": str(advisory.id),
                    "tenant_id": str(advisory.tenant_id),
                    "field_id": str(advisory.field_id) if advisory.field_id else None,
                    "category": advisory.category,
                    "priority": advisory.priority
                }
            )
            
            logger.info("Advisory created", advisory_id=str(advisory.id), category=advisory.category)
            return advisory
    
    async def get_advisory(self, advisory_id: uuid.UUID, tenant_id: Optional[uuid.UUID] = None) -> Optional[Advisory]:
        """Get advisory by ID"""
        async with self.db.session() as session:
            query = select(Advisory).where(Advisory.id == advisory_id)
            if tenant_id:
                query = query.where(Advisory.tenant_id == tenant_id)
            
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    async def list_advisories(
        self,
        tenant_id: uuid.UUID,
        field_id: Optional[uuid.UUID] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        status_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Advisory], int]:
        """List advisories with filters"""
        async with self.db.session() as session:
            query = select(Advisory).where(Advisory.tenant_id == tenant_id)
            count_query = select(func.count(Advisory.id)).where(Advisory.tenant_id == tenant_id)
            
            if field_id:
                query = query.where(Advisory.field_id == field_id)
                count_query = count_query.where(Advisory.field_id == field_id)
            
            if category:
                query = query.where(Advisory.category == category)
                count_query = count_query.where(Advisory.category == category)
            
            if priority:
                query = query.where(Advisory.priority == priority)
                count_query = count_query.where(Advisory.priority == priority)
            
            if status_filter:
                query = query.where(Advisory.status == status_filter)
                count_query = count_query.where(Advisory.status == status_filter)
            else:
                # By default, exclude expired
                query = query.where(Advisory.status != AdvisoryStatus.EXPIRED.value)
                count_query = count_query.where(Advisory.status != AdvisoryStatus.EXPIRED.value)
            
            # Get total
            total_result = await session.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size).order_by(
                Advisory.priority.desc(),
                Advisory.created_at.desc()
            )
            
            result = await session.execute(query)
            advisories = result.scalars().all()
            
            return advisories, total
    
    async def acknowledge_advisory(self, advisory_id: uuid.UUID, tenant_id: uuid.UUID, user_id: uuid.UUID) -> Advisory:
        """Acknowledge advisory"""
        async with self.db.session() as session:
            result = await session.execute(
                select(Advisory).where(
                    Advisory.id == advisory_id,
                    Advisory.tenant_id == tenant_id
                )
            )
            advisory = result.scalar_one_or_none()
            
            if not advisory:
                raise HTTPException(status_code=404, detail="Advisory not found")
            
            advisory.status = AdvisoryStatus.ACKNOWLEDGED.value
            advisory.acknowledged_at = datetime.utcnow()
            advisory.acknowledged_by = user_id
            advisory.updated_at = datetime.utcnow()
            
            await session.commit()
            await session.refresh(advisory)
            
            return advisory
    
    async def complete_advisory(self, advisory_id: uuid.UUID, tenant_id: uuid.UUID) -> Advisory:
        """Mark advisory as completed"""
        async with self.db.session() as session:
            result = await session.execute(
                select(Advisory).where(
                    Advisory.id == advisory_id,
                    Advisory.tenant_id == tenant_id
                )
            )
            advisory = result.scalar_one_or_none()
            
            if not advisory:
                raise HTTPException(status_code=404, detail="Advisory not found")
            
            advisory.status = AdvisoryStatus.COMPLETED.value
            advisory.completed_at = datetime.utcnow()
            advisory.updated_at = datetime.utcnow()
            
            await session.commit()
            await session.refresh(advisory)
            
            # Emit event
            await self.event_bus.publish(
                "advisor.advisory.completed",
                {
                    "advisory_id": str(advisory_id),
                    "tenant_id": str(tenant_id)
                }
            )
            
            return advisory
    
    async def submit_feedback(
        self,
        advisory_id: uuid.UUID,
        tenant_id: uuid.UUID,
        feedback: str,
        notes: Optional[str] = None
    ) -> Advisory:
        """Submit feedback on advisory"""
        async with self.db.session() as session:
            result = await session.execute(
                select(Advisory).where(
                    Advisory.id == advisory_id,
                    Advisory.tenant_id == tenant_id
                )
            )
            advisory = result.scalar_one_or_none()
            
            if not advisory:
                raise HTTPException(status_code=404, detail="Advisory not found")
            
            advisory.user_feedback = feedback
            advisory.feedback_notes = notes
            advisory.updated_at = datetime.utcnow()
            
            await session.commit()
            await session.refresh(advisory)
            
            # Emit event for learning
            await self.event_bus.publish(
                "advisor.feedback.received",
                {
                    "advisory_id": str(advisory_id),
                    "feedback": feedback,
                    "category": advisory.category
                }
            )
            
            return advisory
    
    async def generate_advisories(self, request: AdvisoryGenerateRequest) -> List[Advisory]:
        """Generate advisories based on context"""
        # Gather context from various sources
        context = {
            "tenant_id": str(request.tenant_id),
            "field_id": str(request.field_id) if request.field_id else None,
            "crop_name": request.crop_name
        }
        
        # In real implementation, fetch data from other services
        # For now, use mock data
        if request.include_weather:
            context["weather_data"] = {
                "max_temp": 35,
                "min_temp": 22,
                "rain_probability": 20,
                "humidity": 45
            }
        
        if request.include_ndvi:
            context["ndvi_data"] = {
                "ndvi_mean": 0.45,
                "ndvi_trend": "stable"
            }
        
        if request.include_calendar:
            context["calendar_data"] = {
                "current_star": {
                    "name_ar": "الثريا",
                    "agricultural_advice_ar": "فترة مناسبة لزراعة الحبوب"
                },
                "recommended_planting": ["قمح", "شعير"],
                "days_remaining": 10
            }
        
        # Generate advisories
        advisory_data_list = await self.engine.generate_advisory(context, request.category)
        
        # Create advisories in database
        created_advisories = []
        for advisory_data in advisory_data_list:
            advisory_create = AdvisoryCreate(
                tenant_id=request.tenant_id,
                field_id=request.field_id,
                **advisory_data
            )
            advisory = await self.create_advisory(advisory_create)
            created_advisories.append(advisory)
        
        return created_advisories
    
    async def chat(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        message: str,
        session_id: Optional[uuid.UUID] = None,
        field_id: Optional[uuid.UUID] = None,
        language: str = "ar"
    ) -> Dict[str, Any]:
        """Chat with AI advisor"""
        async with self.db.session() as session:
            # Get or create session
            if session_id:
                result = await session.execute(
                    select(ConversationSession).where(ConversationSession.id == session_id)
                )
                chat_session = result.scalar_one_or_none()
            else:
                chat_session = ConversationSession(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    field_id=field_id
                )
                session.add(chat_session)
                await session.flush()
            
            # Save user message
            user_msg = ConversationMessage(
                session_id=chat_session.id,
                role="user",
                content=message
            )
            session.add(user_msg)
            
            # Generate response
            context = {
                "tenant_id": str(tenant_id),
                "field_id": str(field_id) if field_id else None
            }
            response = await self.engine.chat_response(message, context, language)
            
            # Save assistant response
            assistant_msg = ConversationMessage(
                session_id=chat_session.id,
                role="assistant",
                content=response["message"],
                content_ar=response["message_ar"],
                sources_used=response["sources"]
            )
            session.add(assistant_msg)
            
            await session.commit()
            
            response["session_id"] = str(chat_session.id)
            return response
    
    async def get_dashboard_summary(self, tenant_id: uuid.UUID) -> Dict[str, Any]:
        """Get advisory dashboard summary"""
        async with self.db.session() as session:
            # Count by priority
            result = await session.execute(
                select(
                    Advisory.priority,
                    func.count(Advisory.id)
                ).where(
                    Advisory.tenant_id == tenant_id,
                    Advisory.status == AdvisoryStatus.ACTIVE.value
                ).group_by(Advisory.priority)
            )
            priority_counts = {r[0]: r[1] for r in result.fetchall()}
            
            # Count by category
            result = await session.execute(
                select(
                    Advisory.category,
                    func.count(Advisory.id)
                ).where(
                    Advisory.tenant_id == tenant_id,
                    Advisory.status == AdvisoryStatus.ACTIVE.value
                ).group_by(Advisory.category)
            )
            category_counts = {r[0]: r[1] for r in result.fetchall()}
            
            # Recent urgent
            result = await session.execute(
                select(Advisory)
                .where(
                    Advisory.tenant_id == tenant_id,
                    Advisory.status == AdvisoryStatus.ACTIVE.value,
                    Advisory.priority == AdvisoryPriority.URGENT.value
                )
                .order_by(Advisory.created_at.desc())
                .limit(5)
            )
            urgent_advisories = result.scalars().all()
            
            return {
                "total_active": sum(priority_counts.values()),
                "by_priority": priority_counts,
                "by_category": category_counts,
                "urgent_advisories": urgent_advisories
            }

# ============================================================================
# Event Handlers
# ============================================================================

async def handle_weather_event(event: Dict[str, Any], service: AdvisorService):
    """Handle weather signal and potentially generate advisory"""
    logger.info("Received weather event", event_id=event.get("event_id"))
    # Analyze and potentially create advisory

async def handle_ndvi_event(event: Dict[str, Any], service: AdvisorService):
    """Handle NDVI signal and potentially generate advisory"""
    logger.info("Received NDVI event", event_id=event.get("event_id"))

async def handle_disease_risk_event(event: Dict[str, Any], service: AdvisorService):
    """Handle disease risk signal and generate advisory"""
    logger.info("Received disease risk event", event_id=event.get("event_id"))

# ============================================================================
# Dependencies
# ============================================================================

db: Database = None
event_bus: EventBus = None
advisor_service: AdvisorService = None

# ============================================================================
# FastAPI Application
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global db, event_bus, advisor_service
    
    logger.info("Starting Advisor Core Service...")
    
    db = Database(settings.DATABASE_URL)
    await db.connect()
    
    event_bus = EventBus(settings.NATS_URL)
    await event_bus.connect()
    
    advisor_service = AdvisorService(db, event_bus)
    
    # Subscribe to events
    await event_bus.subscribe("weather.forecast.received", lambda e: handle_weather_event(e, advisor_service))
    await event_bus.subscribe("ndvi.analysis.completed", lambda e: handle_ndvi_event(e, advisor_service))
    await event_bus.subscribe("disease.risk.assessed", lambda e: handle_disease_risk_event(e, advisor_service))
    
    logger.info("Advisor Core Service started successfully")
    
    yield
    
    logger.info("Shutting down Advisor Core Service...")
    await event_bus.close()
    await db.disconnect()

app = FastAPI(
    title="SAHOOL Advisor Core Service",
    description="AI-Powered Agricultural Advisory Service",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Advisory CRUD
@app.post("/api/v1/advisories", response_model=AdvisoryResponse, status_code=status.HTTP_201_CREATED)
async def create_advisory(data: AdvisoryCreate):
    """Create new advisory"""
    advisory = await advisor_service.create_advisory(data)
    advisory_requests.labels(advisory_type=data.category, status="success").inc()
    return advisory

@app.get("/api/v1/advisories/{advisory_id}", response_model=AdvisoryResponse)
async def get_advisory(advisory_id: uuid.UUID, tenant_id: uuid.UUID = Query(...)):
    """Get advisory by ID"""
    advisory = await advisor_service.get_advisory(advisory_id, tenant_id)
    if not advisory:
        raise HTTPException(status_code=404, detail="Advisory not found")
    return advisory

@app.get("/api/v1/advisories")
async def list_advisories(
    tenant_id: uuid.UUID,
    field_id: Optional[uuid.UUID] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """List advisories with filters"""
    advisories, total = await advisor_service.list_advisories(
        tenant_id=tenant_id,
        field_id=field_id,
        category=category,
        priority=priority,
        status_filter=status_filter,
        page=page,
        page_size=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": advisories,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

# Advisory Actions
@app.post("/api/v1/advisories/{advisory_id}/acknowledge", response_model=AdvisoryResponse)
async def acknowledge_advisory(advisory_id: uuid.UUID, tenant_id: uuid.UUID, user_id: uuid.UUID):
    """Acknowledge advisory"""
    return await advisor_service.acknowledge_advisory(advisory_id, tenant_id, user_id)

@app.post("/api/v1/advisories/{advisory_id}/complete", response_model=AdvisoryResponse)
async def complete_advisory(advisory_id: uuid.UUID, tenant_id: uuid.UUID):
    """Mark advisory as completed"""
    return await advisor_service.complete_advisory(advisory_id, tenant_id)

@app.post("/api/v1/advisories/{advisory_id}/feedback", response_model=AdvisoryResponse)
async def submit_feedback(advisory_id: uuid.UUID, tenant_id: uuid.UUID, data: FeedbackRequest):
    """Submit feedback on advisory"""
    return await advisor_service.submit_feedback(advisory_id, tenant_id, data.feedback, data.notes)

# Advisory Generation
@app.post("/api/v1/advisories/generate", response_model=List[AdvisoryResponse])
@advisory_latency.time()
async def generate_advisories(request: AdvisoryGenerateRequest):
    """Generate advisories based on context"""
    advisories = await advisor_service.generate_advisories(request)
    return advisories

# Chat/Conversation
@app.post("/api/v1/advisor/chat", response_model=ChatResponse)
async def chat_with_advisor(
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    message: ChatMessage,
    session_id: Optional[uuid.UUID] = None,
    field_id: Optional[uuid.UUID] = None
):
    """Chat with AI advisor"""
    response = await advisor_service.chat(
        tenant_id=tenant_id,
        user_id=user_id,
        message=message.content,
        session_id=session_id,
        field_id=field_id,
        language=message.language
    )
    return response

# Dashboard
@app.get("/api/v1/tenants/{tenant_id}/advisor-dashboard")
async def get_advisor_dashboard(tenant_id: uuid.UUID):
    """Get advisory dashboard summary"""
    return await advisor_service.get_dashboard_summary(tenant_id)

# Categories (static)
@app.get("/api/v1/advisory-categories")
async def get_advisory_categories():
    """Get available advisory categories"""
    return {
        "categories": [
            {"code": "planting", "name_en": "Planting", "name_ar": "الزراعة"},
            {"code": "irrigation", "name_en": "Irrigation", "name_ar": "الري"},
            {"code": "fertilization", "name_en": "Fertilization", "name_ar": "التسميد"},
            {"code": "pest_control", "name_en": "Pest Control", "name_ar": "مكافحة الآفات"},
            {"code": "disease_management", "name_en": "Disease Management", "name_ar": "إدارة الأمراض"},
            {"code": "harvesting", "name_en": "Harvesting", "name_ar": "الحصاد"},
            {"code": "weather_alert", "name_en": "Weather Alert", "name_ar": "تنبيه طقس"},
            {"code": "market", "name_en": "Market", "name_ar": "الأسواق"},
            {"code": "general", "name_en": "General", "name_ar": "عام"}
        ]
    }

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
