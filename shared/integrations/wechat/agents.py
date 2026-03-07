"""
WeChat Sub-Agents
=================
وكلاء WeChat الفرعيين

Specialized AI agents for WeChat integration with SAHOOL platform.
Inspired by WeChat-MCP architecture for agricultural messaging.

Agents:
1. ChatSummarizerAgent - Summarize chat history, extract key info
2. AutoReplierAgent - Generate contextual replies for farmers
3. MessageSearcherAgent - Search chat history with semantic understanding
4. MultiChatCheckerAgent - Monitor multiple chats, prioritize urgent items
5. ChatInsightsAgent - Analyze relationship dynamics and patterns

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import re
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

import structlog

from .client import WeChatMCPClient
from .config import WeChatConfig, get_wechat_config
from .models import (
    AgentResponse,
    AgentType,
    AutoReplyResponse,
    ChatInsight,
    ChatSummary,
    InsightsResponse,
    MultiChatStatus,
    PriorityLevel,
    SearchResult,
    SentimentType,
    SummaryResponse,
    TopicCategory,
    WeChatMessage,
)

logger = structlog.get_logger()


# =============================================================================
# Base Agent
# =============================================================================


@dataclass
class AgentContext:
    """
    Context for agent execution.
    سياق تنفيذ الوكيل
    """

    tenant_id: str = "sahool"
    farmer_id: str | None = None
    farm_id: str | None = None
    preferred_language: str = "ar"
    crops: list[str] = field(default_factory=list)
    region: str | None = None
    conversation_history: list[dict[str, str]] = field(default_factory=list)


class BaseWeChatAgent(ABC):
    """
    Base class for WeChat agents.
    الفئة الأساسية لوكلاء WeChat

    Provides common functionality for all WeChat sub-agents.
    """

    def __init__(
        self,
        client: WeChatMCPClient,
        config: WeChatConfig | None = None,
        context: AgentContext | None = None,
    ):
        """
        Initialize agent.

        Args:
            client: WeChat MCP client instance
            config: Configuration (uses default if None)
            context: Execution context
        """
        self.client = client
        self.config = config or get_wechat_config()
        self.context = context or AgentContext()

        # Statistics
        self.stats = {
            "executions": 0,
            "successful": 0,
            "failed": 0,
            "total_time_ms": 0,
        }

    @property
    @abstractmethod
    def agent_type(self) -> AgentType:
        """Agent type identifier."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name in English."""
        pass

    @property
    @abstractmethod
    def name_ar(self) -> str:
        """Agent name in Arabic."""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> AgentResponse:
        """
        Execute the agent's main function.
        تنفيذ الوظيفة الرئيسية للوكيل
        """
        pass

    def _create_response(
        self,
        success: bool,
        message: str,
        message_ar: str,
        data: dict[str, Any] | None = None,
        error: str | None = None,
        error_ar: str | None = None,
        execution_time_ms: float = 0,
    ) -> AgentResponse:
        """Create standardized response."""
        return AgentResponse(
            agent_type=self.agent_type,
            success=success,
            status="completed" if success else "failed",
            status_ar="مكتمل" if success else "فشل",
            message=message,
            message_ar=message_ar,
            data=data or {},
            error=error,
            error_ar=error_ar,
            execution_time_ms=execution_time_ms,
            request_id=str(uuid.uuid4()),
            tenant_id=self.context.tenant_id,
        )

    def _detect_language(self, text: str) -> str:
        """Detect text language (ar, en, zh)."""
        # Arabic characters
        if re.search(r"[\u0600-\u06FF]", text):
            return "ar"
        # Chinese characters
        if re.search(r"[\u4e00-\u9fff]", text):
            return "zh"
        return "en"

    def _detect_topics(self, text: str) -> list[TopicCategory]:
        """Detect agricultural topics in text."""
        text_lower = text.lower()
        topics = []

        # Irrigation keywords
        irrigation_keywords = ["water", "irrigation", "ري", "سقي", "ماء", "رطوبة", "moisture"]
        if any(kw in text_lower for kw in irrigation_keywords):
            topics.append(TopicCategory.IRRIGATION)

        # Fertilizer keywords
        fertilizer_keywords = [
            "fertilizer",
            "nutrient",
            "nitrogen",
            "سماد",
            "تسميد",
            "نيتروجين",
            "فوسفور",
        ]
        if any(kw in text_lower for kw in fertilizer_keywords):
            topics.append(TopicCategory.FERTILIZER)

        # Pest/disease keywords
        pest_keywords = [
            "pest",
            "disease",
            "yellow",
            "آفة",
            "مرض",
            "اصفرار",
            "حشرة",
            "fungus",
            "فطر",
        ]
        if any(kw in text_lower for kw in pest_keywords):
            topics.append(TopicCategory.PEST_DISEASE)

        # Weather keywords
        weather_keywords = [
            "weather",
            "rain",
            "temperature",
            "طقس",
            "مطر",
            "درجة",
            "حرارة",
            "frost",
            "صقيع",
        ]
        if any(kw in text_lower for kw in weather_keywords):
            topics.append(TopicCategory.WEATHER)

        # Harvest keywords
        harvest_keywords = ["harvest", "yield", "حصاد", "محصول", "إنتاج", "جني"]
        if any(kw in text_lower for kw in harvest_keywords):
            topics.append(TopicCategory.HARVEST)

        # Market keywords
        market_keywords = ["price", "market", "sell", "سعر", "سوق", "بيع", "شراء"]
        if any(kw in text_lower for kw in market_keywords):
            topics.append(TopicCategory.MARKET)

        # Equipment keywords
        equipment_keywords = ["tractor", "pump", "equipment", "جرار", "مضخة", "معدات", "آلة"]
        if any(kw in text_lower for kw in equipment_keywords):
            topics.append(TopicCategory.EQUIPMENT)

        # Urgent keywords
        urgent_keywords = [
            "urgent",
            "emergency",
            "immediately",
            "عاجل",
            "طوارئ",
            "فوراً",
            "critical",
            "حرج",
        ]
        if any(kw in text_lower for kw in urgent_keywords):
            topics.append(TopicCategory.URGENT)

        return topics or [TopicCategory.GENERAL]

    def _detect_sentiment(self, text: str) -> tuple[SentimentType, float]:
        """Simple sentiment detection."""
        text_lower = text.lower()

        # Positive indicators
        positive_words = [
            "good",
            "great",
            "excellent",
            "thanks",
            "happy",
            "جيد",
            "ممتاز",
            "شكراً",
            "سعيد",
            "نجاح",
        ]
        positive_count = sum(1 for w in positive_words if w in text_lower)

        # Negative indicators
        negative_words = [
            "bad",
            "problem",
            "issue",
            "worry",
            "fail",
            "سيء",
            "مشكلة",
            "قلق",
            "فشل",
            "خطر",
        ]
        negative_count = sum(1 for w in negative_words if w in text_lower)

        if positive_count > negative_count:
            score = min(positive_count / 5, 1.0)
            return SentimentType.POSITIVE, score
        elif negative_count > positive_count:
            score = min(negative_count / 5, -1.0)
            return SentimentType.NEGATIVE, score
        else:
            return SentimentType.NEUTRAL, 0.0

    def _detect_priority(self, text: str, topics: list[TopicCategory]) -> PriorityLevel:
        """Detect message priority."""
        text_lower = text.lower()

        # Critical indicators
        if TopicCategory.URGENT in topics:
            return PriorityLevel.CRITICAL

        critical_words = [
            "urgent",
            "emergency",
            "immediately",
            "dying",
            "عاجل",
            "طوارئ",
            "يموت",
            "critical",
        ]
        if any(w in text_lower for w in critical_words):
            return PriorityLevel.CRITICAL

        # High priority indicators
        high_words = ["asap", "soon", "today", "important", "مهم", "اليوم", "بسرعة"]
        if any(w in text_lower for w in high_words):
            return PriorityLevel.HIGH

        if TopicCategory.PEST_DISEASE in topics:
            return PriorityLevel.HIGH

        # Medium priority
        if TopicCategory.IRRIGATION in topics or TopicCategory.WEATHER in topics:
            return PriorityLevel.MEDIUM

        return PriorityLevel.LOW


# =============================================================================
# ChatSummarizerAgent
# =============================================================================


class ChatSummarizerAgent(BaseWeChatAgent):
    """
    Chat Summarizer Agent.
    وكيل تلخيص المحادثات

    Summarizes chat history and extracts key information for farmers.

    Features:
    - Bilingual summaries (Arabic/English)
    - Key point extraction
    - Action item identification
    - Topic categorization
    - Agricultural context awareness

    Example:
        agent = ChatSummarizerAgent(client)
        summary = await agent.summarize_chat(
            chat_id="farmer_001",
            hours=24
        )
    """

    @property
    def agent_type(self) -> AgentType:
        return AgentType.CHAT_SUMMARIZER

    @property
    def name(self) -> str:
        return "Chat Summarizer Agent"

    @property
    def name_ar(self) -> str:
        return "وكيل تلخيص المحادثات"

    async def execute(
        self,
        chat_id: str,
        hours: int = 24,
        include_action_items: bool = True,
        **kwargs,
    ) -> SummaryResponse:
        """
        Execute chat summarization.

        Args:
            chat_id: Chat to summarize
            hours: Hours of history to include
            include_action_items: Extract action items

        Returns:
            Summary response
        """
        return await self.summarize_chat(
            chat_id=chat_id,
            hours=hours,
            include_action_items=include_action_items,
        )

    async def summarize_chat(
        self,
        chat_id: str,
        hours: int = 24,
        include_action_items: bool = True,
    ) -> SummaryResponse:
        """
        Summarize a chat conversation.
        تلخيص محادثة

        Args:
            chat_id: Chat ID to summarize
            hours: Number of hours to look back
            include_action_items: Whether to extract action items

        Returns:
            Summary response with chat summary
        """
        start_time = datetime.now(UTC)

        try:
            # Fetch messages
            since = datetime.now(UTC) - timedelta(hours=hours)
            messages = await self.client.fetch_messages(
                chat_id=chat_id,
                since=since,
                limit=200,
            )

            if not messages:
                return SummaryResponse(
                    agent_type=self.agent_type,
                    success=True,
                    status="completed",
                    status_ar="مكتمل",
                    message="No messages found in the specified time period.",
                    message_ar="لم يتم العثور على رسائل في الفترة الزمنية المحددة.",
                    summary=None,
                )

            # Analyze messages
            topics: list[TopicCategory] = []
            sentiments: list[SentimentType] = []
            key_points: list[str] = []
            key_points_ar: list[str] = []
            action_items: list[str] = []
            action_items_ar: list[str] = []
            crops_mentioned: set[str] = set()
            fields_mentioned: set[str] = set()

            for msg in messages:
                # Detect topics
                msg_topics = self._detect_topics(msg.content)
                topics.extend(msg_topics)

                # Detect sentiment
                sentiment, _ = self._detect_sentiment(msg.content)
                sentiments.append(sentiment)

                # Extract crops mentioned
                crop_keywords = [
                    "wheat",
                    "قمح",
                    "barley",
                    "شعير",
                    "tomato",
                    "طماطم",
                    "date palm",
                    "نخيل",
                ]
                for crop in crop_keywords:
                    if crop.lower() in msg.content.lower():
                        crops_mentioned.add(crop)

                # Extract field IDs
                field_matches = re.findall(r"[Ff]ield[- ]?(\d+|[A-Z]-?\d+)", msg.content)
                fields_mentioned.update(field_matches)

                # Simple key point extraction (messages with questions or important info)
                if "?" in msg.content or any(kw in msg.content.lower() for kw in ["important", "مهم", "need", "احتاج"]):
                    key_points.append(msg.content[:100])

            # Calculate overall sentiment
            positive_count = sentiments.count(SentimentType.POSITIVE)
            negative_count = sentiments.count(SentimentType.NEGATIVE)

            if positive_count > negative_count:
                overall_sentiment = SentimentType.POSITIVE
            elif negative_count > positive_count:
                overall_sentiment = SentimentType.NEGATIVE
            else:
                overall_sentiment = SentimentType.NEUTRAL

            # Get unique topics
            unique_topics = list(set(topics))

            # Create summary
            summary_en = self._generate_summary_en(
                message_count=len(messages),
                unique_topics=unique_topics,
                overall_sentiment=overall_sentiment,
                crops=list(crops_mentioned),
            )

            summary_ar = self._generate_summary_ar(
                message_count=len(messages),
                unique_topics=unique_topics,
                overall_sentiment=overall_sentiment,
                crops=list(crops_mentioned),
            )

            chat_summary = ChatSummary(
                chat_id=chat_id,
                contact_id=messages[0].sender_id if messages else "",
                start_time=since,
                end_time=datetime.now(UTC),
                message_count=len(messages),
                summary=summary_en,
                summary_ar=summary_ar,
                key_points=key_points[:5],  # Top 5
                key_points_ar=key_points_ar[:5],
                action_items=action_items,
                action_items_ar=action_items_ar,
                main_topics=unique_topics[:5],
                overall_sentiment=overall_sentiment,
                crops_mentioned=list(crops_mentioned),
                fields_mentioned=list(fields_mentioned),
            )

            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

            return SummaryResponse(
                agent_type=self.agent_type,
                success=True,
                status="completed",
                status_ar="مكتمل",
                message=f"Successfully summarized {len(messages)} messages.",
                message_ar=f"تم تلخيص {len(messages)} رسالة بنجاح.",
                summary=chat_summary,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            logger.error("chat_summarization_failed", chat_id=chat_id, error=str(e))
            return SummaryResponse(
                agent_type=self.agent_type,
                success=False,
                status="failed",
                status_ar="فشل",
                message=f"Failed to summarize chat: {e}",
                message_ar=f"فشل تلخيص المحادثة: {e}",
                error=str(e),
                error_ar=str(e),
            )

    def _generate_summary_en(
        self,
        message_count: int,
        unique_topics: list[TopicCategory],
        overall_sentiment: SentimentType,
        crops: list[str],
    ) -> str:
        """Generate English summary."""
        topic_names = [t.value.replace("_", " ").title() for t in unique_topics[:3]]
        topics_str = ", ".join(topic_names) if topic_names else "general"

        crop_str = ", ".join(crops[:3]) if crops else "various crops"

        sentiment_word = {
            SentimentType.POSITIVE: "positive",
            SentimentType.NEGATIVE: "concerning",
            SentimentType.NEUTRAL: "neutral",
        }.get(overall_sentiment, "neutral")

        return (
            f"This conversation contains {message_count} messages discussing {topics_str}. "
            f"The overall tone is {sentiment_word}. "
            f"Crops mentioned: {crop_str}."
        )

    def _generate_summary_ar(
        self,
        message_count: int,
        unique_topics: list[TopicCategory],
        overall_sentiment: SentimentType,
        crops: list[str],
    ) -> str:
        """Generate Arabic summary."""
        topic_translations = {
            TopicCategory.IRRIGATION: "الري",
            TopicCategory.FERTILIZER: "التسميد",
            TopicCategory.PEST_DISEASE: "الآفات والأمراض",
            TopicCategory.WEATHER: "الطقس",
            TopicCategory.HARVEST: "الحصاد",
            TopicCategory.MARKET: "السوق",
            TopicCategory.EQUIPMENT: "المعدات",
            TopicCategory.GENERAL: "عام",
            TopicCategory.URGENT: "عاجل",
        }

        topic_names = [topic_translations.get(t, "عام") for t in unique_topics[:3]]
        topics_str = "، ".join(topic_names) if topic_names else "عام"

        crop_str = "، ".join(crops[:3]) if crops else "محاصيل متنوعة"

        sentiment_word = {
            SentimentType.POSITIVE: "إيجابي",
            SentimentType.NEGATIVE: "مقلق",
            SentimentType.NEUTRAL: "محايد",
        }.get(overall_sentiment, "محايد")

        return (
            f"تحتوي هذه المحادثة على {message_count} رسالة تناقش {topics_str}. "
            f"النبرة العامة {sentiment_word}. "
            f"المحاصيل المذكورة: {crop_str}."
        )


# =============================================================================
# AutoReplierAgent
# =============================================================================


class AutoReplierAgent(BaseWeChatAgent):
    """
    Auto-Replier Agent.
    وكيل الرد التلقائي

    Generates contextual, bilingual replies for farmers based on their messages.

    Features:
    - Agricultural-aware responses
    - Bilingual output (Arabic/English)
    - Intent detection
    - Suggested alternatives
    - Human escalation when needed

    Example:
        agent = AutoReplierAgent(client)
        reply = await agent.generate_reply(
            message="متى يجب أن أسقي القمح؟",
            chat_id="farmer_001"
        )
    """

    @property
    def agent_type(self) -> AgentType:
        return AgentType.AUTO_REPLIER

    @property
    def name(self) -> str:
        return "Auto-Replier Agent"

    @property
    def name_ar(self) -> str:
        return "وكيل الرد التلقائي"

    # Pre-defined response templates
    RESPONSE_TEMPLATES = {
        TopicCategory.IRRIGATION: {
            "en": "Based on the current conditions, I recommend checking your soil moisture levels. For wheat in tillering stage, aim for 45-60% soil moisture.",
            "ar": "بناءً على الظروف الحالية، أنصح بفحص مستويات رطوبة التربة. للقمح في مرحلة التفريع، استهدف رطوبة تربة 45-60%.",
        },
        TopicCategory.FERTILIZER: {
            "en": "For fertilizer recommendations, I need to know your current soil test results. Generally, wheat at tillering needs nitrogen supplementation.",
            "ar": "لتقديم توصيات التسميد، أحتاج معرفة نتائج تحليل التربة الحالية. عموماً، يحتاج القمح في مرحلة التفريع إلى مكملات نيتروجين.",
        },
        TopicCategory.PEST_DISEASE: {
            "en": "I understand you're concerned about crop health. Can you describe the symptoms or share a photo? This will help with accurate diagnosis.",
            "ar": "أفهم قلقك بشأن صحة المحصول. هل يمكنك وصف الأعراض أو مشاركة صورة؟ سيساعد هذا في التشخيص الدقيق.",
        },
        TopicCategory.WEATHER: {
            "en": "I'll check the weather forecast for your area. Please share your location or field ID for accurate information.",
            "ar": "سأتحقق من توقعات الطقس لمنطقتك. يرجى مشاركة موقعك أو معرف الحقل للحصول على معلومات دقيقة.",
        },
        TopicCategory.URGENT: {
            "en": "I understand this is urgent. Let me connect you with an agricultural advisor immediately.",
            "ar": "أفهم أن هذا أمر عاجل. دعني أوصلك بمستشار زراعي فوراً.",
        },
        TopicCategory.GENERAL: {
            "en": "Thank you for your message. How can I help you with your farming needs today?",
            "ar": "شكراً على رسالتك. كيف يمكنني مساعدتك في احتياجاتك الزراعية اليوم؟",
        },
    }

    async def execute(
        self,
        message: str,
        chat_id: str,
        **kwargs,
    ) -> AutoReplyResponse:
        """
        Execute auto-reply generation.

        Args:
            message: Incoming message to respond to
            chat_id: Chat ID for context

        Returns:
            Auto-reply response
        """
        return await self.generate_reply(message=message, chat_id=chat_id)

    async def generate_reply(
        self,
        message: str,
        chat_id: str,
        include_context: bool = True,
    ) -> AutoReplyResponse:
        """
        Generate a contextual reply for a farmer's message.
        إنشاء رد سياقي لرسالة المزارع

        Args:
            message: The incoming message
            chat_id: Chat ID for context
            include_context: Include recent chat context

        Returns:
            Auto-reply response with suggested reply
        """
        start_time = datetime.now(UTC)

        try:
            # Detect language
            language = self._detect_language(message)

            # Detect topics
            topics = self._detect_topics(message)
            main_topic = topics[0] if topics else TopicCategory.GENERAL

            # Detect intent
            intent, intent_ar = self._detect_intent(message)

            # Detect priority
            priority = self._detect_priority(message, topics)

            # Check if human escalation needed
            requires_human = (
                priority == PriorityLevel.CRITICAL
                or TopicCategory.URGENT in topics
                or self._contains_complex_question(message)
            )

            # Get response template
            template = self.RESPONSE_TEMPLATES.get(main_topic, self.RESPONSE_TEMPLATES[TopicCategory.GENERAL])

            # Generate reply
            reply_text = template["en"]
            reply_text_ar = template["ar"]

            # Generate alternative suggestions
            suggested_replies = self._generate_alternatives(main_topic, "en")
            suggested_replies_ar = self._generate_alternatives(main_topic, "ar")

            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

            # Determine confidence
            confidence = 0.9 if main_topic != TopicCategory.GENERAL else 0.7
            if requires_human:
                confidence = 0.5

            return AutoReplyResponse(
                agent_type=self.agent_type,
                success=True,
                status="completed",
                status_ar="مكتمل",
                message="Reply generated successfully.",
                message_ar="تم إنشاء الرد بنجاح.",
                reply_text=reply_text,
                reply_text_ar=reply_text_ar,
                suggested_replies=suggested_replies,
                suggested_replies_ar=suggested_replies_ar,
                detected_intent=intent,
                detected_intent_ar=intent_ar,
                confidence=confidence,
                requires_human_review=requires_human,
                escalation_reason="Complex query requires expert" if requires_human else None,
                execution_time_ms=execution_time,
                data={
                    "original_message": message,
                    "detected_language": language,
                    "topics": [t.value for t in topics],
                    "priority": priority.value,
                },
            )

        except Exception as e:
            logger.error("auto_reply_failed", error=str(e))
            return AutoReplyResponse(
                agent_type=self.agent_type,
                success=False,
                status="failed",
                status_ar="فشل",
                message=f"Failed to generate reply: {e}",
                message_ar=f"فشل إنشاء الرد: {e}",
                reply_text="",
                reply_text_ar="",
                error=str(e),
            )

    def _detect_intent(self, text: str) -> tuple[str, str]:
        """Detect user intent from message."""
        text_lower = text.lower()

        # Question intents
        if "?" in text or any(w in text_lower for w in ["when", "how", "what", "متى", "كيف", "ماذا"]):
            if any(w in text_lower for w in ["water", "irrigation", "ري", "سقي"]):
                return "irrigation_query", "استفسار عن الري"
            if any(w in text_lower for w in ["fertilizer", "سماد"]):
                return "fertilizer_query", "استفسار عن التسميد"
            return "general_question", "سؤال عام"

        # Request intents
        if any(w in text_lower for w in ["need", "want", "please", "احتاج", "أريد", "من فضلك"]):
            return "request", "طلب"

        # Report/notification intents
        if any(w in text_lower for w in ["noticed", "found", "see", "لاحظت", "وجدت", "أرى"]):
            return "report", "تقرير"

        return "statement", "بيان"

    def _contains_complex_question(self, text: str) -> bool:
        """Check if message contains complex question requiring expert."""
        complex_indicators = [
            "chemical",
            "كيميائي",
            "dosage",
            "جرعة",
            "prescription",
            "وصفة",
            "multiple",
            "متعدد",
            "combination",
            "تركيبة",
        ]
        return any(ind in text.lower() for ind in complex_indicators)

    def _generate_alternatives(self, topic: TopicCategory, language: str) -> list[str]:
        """Generate alternative reply suggestions."""
        alternatives = {
            TopicCategory.IRRIGATION: {
                "en": [
                    "Would you like me to check the weather forecast?",
                    "I can help you create an irrigation schedule.",
                    "Let me analyze your field's soil moisture data.",
                ],
                "ar": [
                    "هل تريد أن أتحقق من توقعات الطقس؟",
                    "يمكنني مساعدتك في إنشاء جدول ري.",
                    "دعني أحلل بيانات رطوبة تربة حقلك.",
                ],
            },
            TopicCategory.FERTILIZER: {
                "en": [
                    "Would you like a soil test recommendation?",
                    "I can suggest organic alternatives.",
                    "Let me calculate the optimal application rate.",
                ],
                "ar": [
                    "هل تريد توصية بتحليل التربة؟",
                    "يمكنني اقتراح بدائل عضوية.",
                    "دعني أحسب معدل التطبيق الأمثل.",
                ],
            },
        }

        topic_alts = alternatives.get(topic, {})
        return topic_alts.get(
            language,
            ["Would you like more information?" if language == "en" else "هل تريد مزيداً من المعلومات؟"],
        )


# =============================================================================
# MessageSearcherAgent
# =============================================================================


class MessageSearcherAgent(BaseWeChatAgent):
    """
    Message Searcher Agent.
    وكيل البحث في الرسائل

    Searches chat history with semantic understanding and agricultural context.

    Features:
    - Natural language search queries
    - Bilingual search support
    - Topic-based filtering
    - Date range filtering
    - Relevance scoring

    Example:
        agent = MessageSearcherAgent(client)
        results = await agent.search(
            query="irrigation problems with wheat",
            chat_ids=["farmer_001", "farmer_002"]
        )
    """

    @property
    def agent_type(self) -> AgentType:
        return AgentType.MESSAGE_SEARCHER

    @property
    def name(self) -> str:
        return "Message Searcher Agent"

    @property
    def name_ar(self) -> str:
        return "وكيل البحث في الرسائل"

    async def execute(
        self,
        query: str,
        chat_ids: list[str] | None = None,
        **kwargs,
    ) -> AgentResponse:
        """
        Execute message search.

        Args:
            query: Search query
            chat_ids: Optional list of chat IDs to search

        Returns:
            Search results
        """
        return await self.search(query=query, chat_ids=chat_ids, **kwargs)

    async def search(
        self,
        query: str,
        chat_ids: list[str] | None = None,
        topics: list[TopicCategory] | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 50,
    ) -> AgentResponse:
        """
        Search messages across chats.
        البحث في الرسائل عبر المحادثات

        Args:
            query: Search query (supports Arabic/English)
            chat_ids: Limit to specific chats
            topics: Filter by topics
            since: Search after this date
            until: Search before this date
            limit: Maximum results

        Returns:
            Search results with relevance scoring
        """
        start_time = datetime.now(UTC)

        try:
            # Detect query language
            query_language = self._detect_language(query)

            # Extract search keywords
            keywords = self._extract_keywords(query)

            # Detect query topics
            query_topics = self._detect_topics(query)

            # Search messages
            messages = await self.client.search_messages(
                query=query,
                chat_ids=chat_ids,
                since=since,
                until=until,
                limit=limit,
            )

            # Score and filter results
            scored_results: list[tuple[WeChatMessage, float]] = []
            for msg in messages:
                score = self._calculate_relevance(msg, keywords, query_topics)
                if score > 0.1:  # Minimum relevance threshold
                    scored_results.append((msg, score))

            # Sort by relevance
            scored_results.sort(key=lambda x: x[1], reverse=True)

            # Apply topic filter if specified
            if topics:
                scored_results = [
                    (msg, score)
                    for msg, score in scored_results
                    if any(t in self._detect_topics(msg.content) for t in topics)
                ]

            # Extract final results
            result_messages = [msg for msg, _ in scored_results[:limit]]
            relevance_scores = {msg.id: score for msg, score in scored_results[:limit]}

            # Group by contact
            by_contact: dict[str, int] = {}
            for msg in result_messages:
                by_contact[msg.sender_id] = by_contact.get(msg.sender_id, 0) + 1

            # Group by topic
            by_topic: dict[str, int] = {}
            for msg in result_messages:
                for topic in self._detect_topics(msg.content):
                    by_topic[topic.value] = by_topic.get(topic.value, 0) + 1

            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

            search_result = SearchResult(
                query=query,
                query_ar=query if query_language == "ar" else None,
                total_results=len(result_messages),
                messages=result_messages,
                relevance_scores=relevance_scores,
                by_contact=by_contact,
                by_topic=by_topic,
                search_time_ms=execution_time,
            )

            return self._create_response(
                success=True,
                message=f"Found {len(result_messages)} results for '{query[:30]}...'",
                message_ar=f"تم العثور على {len(result_messages)} نتيجة لـ '{query[:30]}...'",
                data={
                    "search_result": search_result.model_dump(),
                    "keywords": keywords,
                    "detected_topics": [t.value for t in query_topics],
                },
                execution_time_ms=execution_time,
            )

        except Exception as e:
            logger.error("message_search_failed", query=query, error=str(e))
            return self._create_response(
                success=False,
                message=f"Search failed: {e}",
                message_ar=f"فشل البحث: {e}",
                error=str(e),
            )

    def _extract_keywords(self, query: str) -> list[str]:
        """Extract keywords from search query."""
        # Simple keyword extraction - remove common words
        stop_words = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "in",
            "on",
            "at",
            "to",
            "for",
            "من",
            "في",
            "على",
            "إلى",
            "عن",
            "مع",
            "هل",
            "ما",
            "كيف",
            "متى",
        }

        words = re.findall(r"\b\w+\b", query.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        return keywords

    def _calculate_relevance(
        self,
        message: WeChatMessage,
        keywords: list[str],
        query_topics: list[TopicCategory],
    ) -> float:
        """Calculate relevance score for a message."""
        content_lower = message.content.lower()
        score = 0.0

        # Keyword matching (0.4 weight)
        keyword_matches = sum(1 for kw in keywords if kw in content_lower)
        keyword_score = min(keyword_matches / max(len(keywords), 1), 1.0)
        score += keyword_score * 0.4

        # Topic matching (0.3 weight)
        msg_topics = self._detect_topics(message.content)
        topic_matches = len(set(query_topics) & set(msg_topics))
        topic_score = min(topic_matches / max(len(query_topics), 1), 1.0)
        score += topic_score * 0.3

        # Recency boost (0.2 weight) - newer messages rank higher
        age_days = (datetime.now(UTC) - message.timestamp).days
        recency_score = max(0, 1 - (age_days / 30))  # Full score within 30 days
        score += recency_score * 0.2

        # Priority boost (0.1 weight)
        if message.priority in [PriorityLevel.HIGH, PriorityLevel.CRITICAL]:
            score += 0.1

        return score


# =============================================================================
# MultiChatCheckerAgent
# =============================================================================


class MultiChatCheckerAgent(BaseWeChatAgent):
    """
    Multi-Chat Checker Agent.
    وكيل فحص المحادثات المتعددة

    Monitors multiple chats simultaneously and prioritizes urgent items.

    Features:
    - Parallel chat monitoring
    - Priority-based sorting
    - Urgent message alerts
    - Agricultural alert detection
    - Summary generation

    Example:
        agent = MultiChatCheckerAgent(client)
        status = await agent.check_all_chats()
    """

    @property
    def agent_type(self) -> AgentType:
        return AgentType.MULTI_CHAT_CHECKER

    @property
    def name(self) -> str:
        return "Multi-Chat Checker Agent"

    @property
    def name_ar(self) -> str:
        return "وكيل فحص المحادثات المتعددة"

    async def execute(self, **kwargs) -> AgentResponse:
        """Execute multi-chat check."""
        return await self.check_all_chats(**kwargs)

    async def check_all_chats(
        self,
        chat_ids: list[str] | None = None,
        hours: int = 24,
    ) -> AgentResponse:
        """
        Check all chats for urgent items and generate status summary.
        فحص جميع المحادثات للعناصر العاجلة وإنشاء ملخص الحالة

        Args:
            chat_ids: Specific chats to check (all if None)
            hours: Hours to look back

        Returns:
            Multi-chat status summary
        """
        start_time = datetime.now(UTC)

        try:
            # Get contacts/chats
            if not chat_ids:
                contacts = await self.client.get_contacts(limit=100)
                chat_ids = [c.id for c in contacts]

            # Check chats in parallel
            tasks = [
                self._check_single_chat(chat_id, hours)
                for chat_id in chat_ids[:20]  # Limit to 20 chats for performance
            ]

            chat_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            urgent_chats: list[dict[str, Any]] = []
            high_priority_chats: list[dict[str, Any]] = []
            pending_responses: list[dict[str, Any]] = []
            agricultural_alerts: list[dict[str, Any]] = []

            total_unread = 0
            total_messages_today = 0

            for result in chat_results:
                if isinstance(result, Exception):
                    logger.warning("chat_check_error", error=str(result))
                    continue

                if not result:
                    continue

                total_unread += result.get("unread", 0)
                total_messages_today += result.get("messages_today", 0)

                # Categorize by priority
                if result.get("priority") == PriorityLevel.CRITICAL.value:
                    urgent_chats.append(result)
                elif result.get("priority") == PriorityLevel.HIGH.value:
                    high_priority_chats.append(result)

                # Check for pending responses
                if result.get("needs_response"):
                    pending_responses.append(result)

                # Check for agricultural alerts
                if result.get("agricultural_alerts"):
                    agricultural_alerts.extend(result["agricultural_alerts"])

            # Generate summary
            summary_en = self._generate_status_summary_en(
                total_chats=len(chat_ids),
                urgent_count=len(urgent_chats),
                pending_count=len(pending_responses),
            )

            summary_ar = self._generate_status_summary_ar(
                total_chats=len(chat_ids),
                urgent_count=len(urgent_chats),
                pending_count=len(pending_responses),
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(urgent_chats, high_priority_chats, agricultural_alerts)

            status = MultiChatStatus(
                total_chats=len(chat_ids),
                total_unread=total_unread,
                total_messages_today=total_messages_today,
                urgent_chats=urgent_chats,
                high_priority_chats=high_priority_chats,
                pending_responses=pending_responses,
                summary=summary_en,
                summary_ar=summary_ar,
                recommended_actions=[r["en"] for r in recommendations],
                recommended_actions_ar=[r["ar"] for r in recommendations],
                agricultural_alerts=agricultural_alerts,
            )

            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

            return self._create_response(
                success=True,
                message=f"Checked {len(chat_ids)} chats. {len(urgent_chats)} urgent items found.",
                message_ar=f"تم فحص {len(chat_ids)} محادثة. تم العثور على {len(urgent_chats)} عناصر عاجلة.",
                data={"status": status.model_dump()},
                execution_time_ms=execution_time,
            )

        except Exception as e:
            logger.error("multi_chat_check_failed", error=str(e))
            return self._create_response(
                success=False,
                message=f"Failed to check chats: {e}",
                message_ar=f"فشل فحص المحادثات: {e}",
                error=str(e),
            )

    async def _check_single_chat(
        self,
        chat_id: str,
        hours: int,
    ) -> dict[str, Any] | None:
        """Check a single chat for status."""
        try:
            since = datetime.now(UTC) - timedelta(hours=hours)
            messages = await self.client.fetch_messages(
                chat_id=chat_id,
                since=since,
                limit=50,
            )

            if not messages:
                return None

            # Analyze messages
            unread_count = sum(1 for m in messages if not m.is_read and m.sender_id != "self")
            last_message = messages[-1] if messages else None

            # Check priority
            highest_priority = PriorityLevel.LOW
            agricultural_alerts = []

            for msg in messages:
                topics = self._detect_topics(msg.content)
                priority = self._detect_priority(msg.content, topics)

                if priority.value < highest_priority.value:  # Lower value = higher priority
                    highest_priority = priority

                # Check for agricultural alerts
                if TopicCategory.URGENT in topics or TopicCategory.PEST_DISEASE in topics:
                    agricultural_alerts.append(
                        {
                            "message_id": msg.id,
                            "content": msg.content[:100],
                            "topics": [t.value for t in topics],
                            "timestamp": msg.timestamp.isoformat(),
                        }
                    )

            # Check if response needed
            needs_response = last_message and last_message.sender_id != "self" and not last_message.is_read

            return {
                "chat_id": chat_id,
                "unread": unread_count,
                "messages_today": len(messages),
                "priority": highest_priority.value,
                "needs_response": needs_response,
                "last_message": last_message.content[:100] if last_message else None,
                "last_message_time": last_message.timestamp.isoformat() if last_message else None,
                "agricultural_alerts": agricultural_alerts,
            }

        except Exception as e:
            logger.warning("single_chat_check_error", chat_id=chat_id, error=str(e))
            return None

    def _generate_status_summary_en(
        self,
        total_chats: int,
        urgent_count: int,
        pending_count: int,
    ) -> str:
        """Generate English status summary."""
        if urgent_count > 0:
            return f"ATTENTION: {urgent_count} urgent chat(s) require immediate attention out of {total_chats} monitored. {pending_count} pending responses."
        elif pending_count > 0:
            return f"You have {pending_count} pending response(s) across {total_chats} chats. No urgent items."
        else:
            return f"All clear! {total_chats} chats checked with no urgent items or pending responses."

    def _generate_status_summary_ar(
        self,
        total_chats: int,
        urgent_count: int,
        pending_count: int,
    ) -> str:
        """Generate Arabic status summary."""
        if urgent_count > 0:
            return f"انتباه: {urgent_count} محادثة عاجلة تتطلب اهتماماً فورياً من أصل {total_chats} محادثة مراقبة. {pending_count} رد معلق."
        elif pending_count > 0:
            return f"لديك {pending_count} رد معلق عبر {total_chats} محادثة. لا توجد عناصر عاجلة."
        else:
            return f"كل شيء على ما يرام! تم فحص {total_chats} محادثة بدون عناصر عاجلة أو ردود معلقة."

    def _generate_recommendations(
        self,
        urgent_chats: list[dict[str, Any]],
        high_priority_chats: list[dict[str, Any]],
        agricultural_alerts: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        """Generate action recommendations."""
        recommendations = []

        if urgent_chats:
            recommendations.append(
                {
                    "en": f"Respond to {len(urgent_chats)} urgent chat(s) immediately",
                    "ar": f"الرد على {len(urgent_chats)} محادثة عاجلة فوراً",
                }
            )

        if agricultural_alerts:
            recommendations.append(
                {
                    "en": f"Review {len(agricultural_alerts)} agricultural alert(s) - potential crop issues detected",
                    "ar": f"مراجعة {len(agricultural_alerts)} تنبيه زراعي - تم اكتشاف مشاكل محتملة في المحاصيل",
                }
            )

        if high_priority_chats:
            recommendations.append(
                {
                    "en": f"Follow up on {len(high_priority_chats)} high-priority conversation(s)",
                    "ar": f"متابعة {len(high_priority_chats)} محادثة ذات أولوية عالية",
                }
            )

        if not recommendations:
            recommendations.append(
                {
                    "en": "All caught up! Consider sharing helpful tips with your farmers.",
                    "ar": "كل شيء تحت السيطرة! فكر في مشاركة نصائح مفيدة مع مزارعيك.",
                }
            )

        return recommendations


# =============================================================================
# ChatInsightsAgent
# =============================================================================


class ChatInsightsAgent(BaseWeChatAgent):
    """
    Chat Insights Agent.
    وكيل رؤى المحادثات

    Analyzes chat relationship dynamics and communication patterns.

    Features:
    - Relationship strength scoring
    - Communication pattern analysis
    - Sentiment trends
    - Topic distribution
    - Engagement suggestions

    Example:
        agent = ChatInsightsAgent(client)
        insights = await agent.analyze_relationship(
            contact_id="farmer_001",
            days=30
        )
    """

    @property
    def agent_type(self) -> AgentType:
        return AgentType.CHAT_INSIGHTS

    @property
    def name(self) -> str:
        return "Chat Insights Agent"

    @property
    def name_ar(self) -> str:
        return "وكيل رؤى المحادثات"

    async def execute(
        self,
        contact_id: str,
        **kwargs,
    ) -> InsightsResponse:
        """Execute insights analysis."""
        return await self.analyze_relationship(contact_id=contact_id, **kwargs)

    async def analyze_relationship(
        self,
        contact_id: str,
        days: int = 30,
    ) -> InsightsResponse:
        """
        Analyze relationship dynamics with a contact.
        تحليل ديناميكيات العلاقة مع جهة اتصال

        Args:
            contact_id: Contact to analyze
            days: Number of days to analyze

        Returns:
            Insights response with relationship analysis
        """
        start_time = datetime.now(UTC)

        try:
            # Fetch message history
            since = datetime.now(UTC) - timedelta(days=days)
            messages = await self.client.fetch_messages(
                chat_id=contact_id,
                since=since,
                limit=500,
            )

            # Get contact info
            contact = await self.client.get_contact(contact_id)
            contact_name = contact.name if contact else contact_id

            if not messages:
                return InsightsResponse(
                    agent_type=self.agent_type,
                    success=True,
                    status="completed",
                    status_ar="مكتمل",
                    message="No messages found for analysis.",
                    message_ar="لم يتم العثور على رسائل للتحليل.",
                    insight=None,
                )

            # Calculate metrics
            total_messages = len(messages)
            incoming = [m for m in messages if m.sender_id != "self"]
            outgoing = [m for m in messages if m.sender_id == "self"]

            # Response time analysis
            response_times = self._calculate_response_times(messages)
            avg_response_time = sum(response_times) / len(response_times) if response_times else None

            # Sentiment analysis
            sentiments = [self._detect_sentiment(m.content)[0] for m in messages]
            positive_count = sentiments.count(SentimentType.POSITIVE)
            positive_rate = positive_count / len(sentiments) if sentiments else 0.5

            overall_sentiment = (
                SentimentType.POSITIVE
                if positive_rate > 0.6
                else SentimentType.NEGATIVE
                if positive_rate < 0.3
                else SentimentType.NEUTRAL
            )

            # Topic analysis
            all_topics: list[TopicCategory] = []
            for msg in messages:
                all_topics.extend(self._detect_topics(msg.content))

            topic_counts: dict[str, int] = {}
            for topic in all_topics:
                topic_counts[topic.value] = topic_counts.get(topic.value, 0) + 1

            total_topics = sum(topic_counts.values())
            topic_distribution = {k: v / total_topics for k, v in topic_counts.items()} if total_topics > 0 else {}

            frequent_topics = sorted(topic_counts.keys(), key=lambda t: topic_counts[t], reverse=True)[:5]

            # Activity analysis
            message_hours = [m.timestamp.hour for m in messages]
            hour_counts: dict[int, int] = {}
            for h in message_hours:
                hour_counts[h] = hour_counts.get(h, 0) + 1

            peak_hours = sorted(hour_counts.keys(), key=lambda h: hour_counts[h], reverse=True)[:3]

            # Relationship strength calculation
            relationship_strength = self._calculate_relationship_strength(
                total_messages=total_messages,
                days=days,
                response_rate=len(outgoing) / max(len(incoming), 1),
                positive_rate=positive_rate,
            )

            # Determine relationship type
            relationship_type, relationship_type_ar = self._determine_relationship_type(contact, frequent_topics)

            # Generate engagement suggestions
            suggestions = self._generate_engagement_suggestions(
                relationship_strength=relationship_strength,
                frequent_topics=[TopicCategory(t) for t in frequent_topics],
                avg_response_time=avg_response_time,
            )

            # Extract crops of interest
            crops_of_interest = self._extract_crops(messages)

            insight = ChatInsight(
                chat_id=contact_id,
                contact_id=contact_id,
                contact_name=contact_name,
                relationship_strength=relationship_strength,
                relationship_type=relationship_type,
                relationship_type_ar=relationship_type_ar,
                avg_response_time_minutes=avg_response_time,
                messages_per_week=total_messages / (days / 7),
                peak_activity_hours=peak_hours,
                overall_sentiment=overall_sentiment,
                positive_interaction_rate=positive_rate,
                frequent_topics=[TopicCategory(t) for t in frequent_topics],
                topic_distribution=topic_distribution,
                crops_of_interest=crops_of_interest,
                engagement_suggestions=[s["en"] for s in suggestions],
                engagement_suggestions_ar=[s["ar"] for s in suggestions],
                analysis_period_days=days,
            )

            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

            return InsightsResponse(
                agent_type=self.agent_type,
                success=True,
                status="completed",
                status_ar="مكتمل",
                message=f"Analysis complete for {contact_name}.",
                message_ar=f"اكتمل التحليل لـ {contact_name}.",
                insight=insight,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            logger.error("chat_insights_failed", contact_id=contact_id, error=str(e))
            return InsightsResponse(
                agent_type=self.agent_type,
                success=False,
                status="failed",
                status_ar="فشل",
                message=f"Analysis failed: {e}",
                message_ar=f"فشل التحليل: {e}",
                error=str(e),
            )

    def _calculate_response_times(self, messages: list[WeChatMessage]) -> list[float]:
        """Calculate response times in minutes."""
        response_times = []

        for i in range(1, len(messages)):
            prev = messages[i - 1]
            curr = messages[i]

            # Check if current is response to previous
            if prev.sender_id != curr.sender_id:
                diff = (curr.timestamp - prev.timestamp).total_seconds() / 60
                if 0 < diff < 1440:  # Within 24 hours
                    response_times.append(diff)

        return response_times

    def _calculate_relationship_strength(
        self,
        total_messages: int,
        days: int,
        response_rate: float,
        positive_rate: float,
    ) -> float:
        """Calculate relationship strength score (0-1)."""
        # Message frequency score
        messages_per_day = total_messages / max(days, 1)
        frequency_score = min(messages_per_day / 5, 1.0)  # Cap at 5 messages/day

        # Response rate score
        response_score = min(response_rate, 1.0)

        # Sentiment score
        sentiment_score = positive_rate

        # Weighted combination
        strength = frequency_score * 0.3 + response_score * 0.3 + sentiment_score * 0.4

        return round(strength, 2)

    def _determine_relationship_type(
        self,
        contact: Any,
        frequent_topics: list[str],
    ) -> tuple[str, str]:
        """Determine relationship type."""
        if contact and contact.farmer_id:
            return "farmer", "مزارع"

        if TopicCategory.MARKET.value in frequent_topics:
            return "buyer", "مشتري"

        if TopicCategory.EQUIPMENT.value in frequent_topics:
            return "supplier", "مورد"

        return "peer", "زميل"

    def _extract_crops(self, messages: list[WeChatMessage]) -> list[str]:
        """Extract crops mentioned in messages."""
        crops = set()
        crop_keywords = {
            "wheat": "wheat",
            "قمح": "wheat",
            "barley": "barley",
            "شعير": "barley",
            "tomato": "tomato",
            "طماطم": "tomato",
            "date": "date palm",
            "نخيل": "date palm",
            "corn": "corn",
            "ذرة": "corn",
        }

        for msg in messages:
            content_lower = msg.content.lower()
            for keyword, crop in crop_keywords.items():
                if keyword in content_lower:
                    crops.add(crop)

        return list(crops)

    def _generate_engagement_suggestions(
        self,
        relationship_strength: float,
        frequent_topics: list[TopicCategory],
        avg_response_time: float | None,
    ) -> list[dict[str, str]]:
        """Generate engagement suggestions."""
        suggestions = []

        if relationship_strength < 0.3:
            suggestions.append(
                {
                    "en": "Consider reaching out more frequently to strengthen this relationship.",
                    "ar": "فكر في التواصل بشكل أكثر تكراراً لتعزيز هذه العلاقة.",
                }
            )

        if avg_response_time and avg_response_time > 120:
            suggestions.append(
                {
                    "en": "Try to respond faster to messages - currently averaging 2+ hours.",
                    "ar": "حاول الرد بشكل أسرع على الرسائل - حالياً المتوسط أكثر من ساعتين.",
                }
            )

        if TopicCategory.IRRIGATION in frequent_topics:
            suggestions.append(
                {
                    "en": "This contact is interested in irrigation - share water-saving tips.",
                    "ar": "جهة الاتصال هذه مهتمة بالري - شارك نصائح توفير المياه.",
                }
            )

        if TopicCategory.PEST_DISEASE in frequent_topics:
            suggestions.append(
                {
                    "en": "They often ask about pest/disease issues - consider proactive alerts.",
                    "ar": "غالباً ما يسألون عن مشاكل الآفات/الأمراض - فكر في التنبيهات الاستباقية.",
                }
            )

        if not suggestions:
            suggestions.append(
                {
                    "en": "Good relationship! Keep up the regular communication.",
                    "ar": "علاقة جيدة! استمر في التواصل المنتظم.",
                }
            )

        return suggestions


# =============================================================================
# Agent Factory
# =============================================================================


def create_wechat_agent(
    agent_type: AgentType,
    client: WeChatMCPClient,
    config: WeChatConfig | None = None,
    context: AgentContext | None = None,
) -> BaseWeChatAgent:
    """
    Factory function to create WeChat agents.
    دالة المصنع لإنشاء وكلاء WeChat

    Args:
        agent_type: Type of agent to create
        client: WeChat MCP client
        config: Optional configuration
        context: Optional execution context

    Returns:
        Agent instance

    Example:
        agent = create_wechat_agent(
            AgentType.CHAT_SUMMARIZER,
            client
        )
    """
    agents = {
        AgentType.CHAT_SUMMARIZER: ChatSummarizerAgent,
        AgentType.AUTO_REPLIER: AutoReplierAgent,
        AgentType.MESSAGE_SEARCHER: MessageSearcherAgent,
        AgentType.MULTI_CHAT_CHECKER: MultiChatCheckerAgent,
        AgentType.CHAT_INSIGHTS: ChatInsightsAgent,
    }

    agent_class = agents.get(agent_type)
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}")

    return agent_class(client=client, config=config, context=context)
