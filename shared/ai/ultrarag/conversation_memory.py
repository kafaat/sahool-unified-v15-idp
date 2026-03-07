# ═══════════════════════════════════════════════════════════════════════════════
# UltraRAG Conversation Memory
# ذاكرة المحادثة لـ UltraRAG
# ═══════════════════════════════════════════════════════════════════════════════
#
# Provides session-based conversation memory for RAG pipelines:
#   - ConversationMemory: stores query/response history within a session
#   - RAGConversationManager: wraps RAGPipeline and injects context from history
#   - In-memory dict with configurable TTL for session expiration
#   - Bilingual support (Arabic/English)
#
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

import structlog

from .models import RAGRequest, RAGResult
from .pipeline import RAGPipeline, RAGStage

logger = structlog.get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class ConversationTurn:
    """A single turn in a conversation | جولة واحدة في المحادثة"""

    query: str
    query_ar: str | None = None
    answer: str = ""
    answer_ar: str | None = None
    confidence: float = 0.0
    sources_count: int = 0
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_context_string(self, language: str = "en") -> str:
        """Format this turn as context for injection into subsequent queries.
        تنسيق هذه الجولة كسياق للحقن في الاستعلامات التالية"""
        if language == "ar" and self.query_ar and self.answer_ar:
            return f"س: {self.query_ar}\nج: {self.answer_ar}"
        elif language == "both":
            parts = [f"Q: {self.query}\nA: {self.answer}"]
            if self.query_ar and self.answer_ar:
                parts.append(f"س: {self.query_ar}\nج: {self.answer_ar}")
            return "\n".join(parts)
        return f"Q: {self.query}\nA: {self.answer}"


@dataclass
class ConversationSession:
    """A conversation session with history | جلسة محادثة مع التاريخ"""

    session_id: str
    turns: list[ConversationTurn] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)
    tenant_id: str | None = None
    language: str = "en"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def turn_count(self) -> int:
        return len(self.turns)

    @property
    def is_empty(self) -> bool:
        return len(self.turns) == 0

    def touch(self) -> None:
        """Update last active timestamp | تحديث الطابع الزمني للنشاط الأخير"""
        self.last_active = time.time()


# ─────────────────────────────────────────────────────────────────────────────
# Conversation Memory
# ─────────────────────────────────────────────────────────────────────────────


class ConversationMemory:
    """In-memory conversation store with TTL-based session expiration.
    مخزن محادثات في الذاكرة مع انتهاء صلاحية الجلسات بناءً على TTL

    Features:
    - Session-based storage keyed by session_id
    - Configurable TTL for automatic session cleanup
    - Configurable max turns per session
    - Thread-safe for single-process async usage
    """

    def __init__(
        self,
        session_ttl_seconds: int = 3600,
        max_turns_per_session: int = 50,
        max_context_turns: int = 5,
    ) -> None:
        self._sessions: dict[str, ConversationSession] = {}
        self._session_ttl = session_ttl_seconds
        self._max_turns = max_turns_per_session
        self._max_context_turns = max_context_turns

        logger.info(
            "conversation_memory_init",
            ttl_seconds=session_ttl_seconds,
            max_turns=max_turns_per_session,
            max_context_turns=max_context_turns,
        )

    def create_session(
        self,
        session_id: str | None = None,
        tenant_id: str | None = None,
        language: str = "en",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Create a new conversation session. Returns session_id.
        إنشاء جلسة محادثة جديدة. يرجع معرف الجلسة"""
        sid = session_id or f"conv_{uuid.uuid4().hex[:12]}"

        self._sessions[sid] = ConversationSession(
            session_id=sid,
            tenant_id=tenant_id,
            language=language,
            metadata=metadata or {},
        )

        logger.debug("session_created", session_id=sid, tenant_id=tenant_id)
        return sid

    def get_session(self, session_id: str) -> ConversationSession | None:
        """Get session if it exists and is not expired.
        الحصول على الجلسة إذا كانت موجودة ولم تنتهِ صلاحيتها"""
        session = self._sessions.get(session_id)
        if session is None:
            return None

        # Check TTL
        if time.time() - session.last_active > self._session_ttl:
            logger.debug("session_expired", session_id=session_id)
            del self._sessions[session_id]
            return None

        return session

    def add_turn(
        self,
        session_id: str,
        query: str,
        answer: str,
        query_ar: str | None = None,
        answer_ar: str | None = None,
        confidence: float = 0.0,
        sources_count: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> ConversationTurn:
        """Add a conversation turn to a session.
        إضافة جولة محادثة إلى جلسة"""
        session = self.get_session(session_id)
        if session is None:
            # Auto-create session if it doesn't exist
            self.create_session(session_id=session_id)
            session = self._sessions[session_id]

        turn = ConversationTurn(
            query=query,
            query_ar=query_ar,
            answer=answer,
            answer_ar=answer_ar,
            confidence=confidence,
            sources_count=sources_count,
            metadata=metadata or {},
        )

        session.turns.append(turn)
        session.touch()

        # Evict oldest turns if over limit
        if len(session.turns) > self._max_turns:
            evicted = len(session.turns) - self._max_turns
            session.turns = session.turns[evicted:]
            logger.debug(
                "turns_evicted",
                session_id=session_id,
                evicted_count=evicted,
            )

        return turn

    def get_context(
        self,
        session_id: str,
        max_turns: int | None = None,
        language: str = "en",
    ) -> str:
        """Build conversation context string from recent turns.
        بناء سلسلة سياق المحادثة من الجولات الأخيرة

        Args:
            session_id: Session identifier
            max_turns: Override max context turns (default: self._max_context_turns)
            language: Language for context output (en, ar, both)

        Returns:
            Formatted conversation history string
        """
        session = self.get_session(session_id)
        if session is None or session.is_empty:
            return ""

        n = max_turns or self._max_context_turns
        recent = session.turns[-n:]

        context_parts = []
        for turn in recent:
            context_parts.append(turn.to_context_string(language))

        return "\n\n".join(context_parts)

    def get_recent_queries(
        self,
        session_id: str,
        max_count: int = 3,
    ) -> list[str]:
        """Get recent queries for query expansion.
        الحصول على الاستعلامات الأخيرة لتوسيع الاستعلام"""
        session = self.get_session(session_id)
        if session is None or session.is_empty:
            return []

        return [turn.query for turn in session.turns[-max_count:]]

    def delete_session(self, session_id: str) -> bool:
        """Delete a session. Returns True if session existed.
        حذف جلسة. يرجع True إذا كانت الجلسة موجودة"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.debug("session_deleted", session_id=session_id)
            return True
        return False

    def cleanup_expired(self) -> int:
        """Remove all expired sessions. Returns count of removed sessions.
        إزالة جميع الجلسات المنتهية الصلاحية. يرجع عدد الجلسات المحذوفة"""
        now = time.time()
        expired = [sid for sid, session in self._sessions.items() if now - session.last_active > self._session_ttl]

        for sid in expired:
            del self._sessions[sid]

        if expired:
            logger.info("sessions_cleanup", removed_count=len(expired))

        return len(expired)

    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics.
        الحصول على إحصائيات الذاكرة"""
        total_turns = sum(s.turn_count for s in self._sessions.values())
        return {
            "active_sessions": len(self._sessions),
            "total_turns": total_turns,
            "session_ttl_seconds": self._session_ttl,
            "max_turns_per_session": self._max_turns,
            "max_context_turns": self._max_context_turns,
        }


# ─────────────────────────────────────────────────────────────────────────────
# RAG Conversation Manager
# ─────────────────────────────────────────────────────────────────────────────


class RAGConversationManager:
    """Wraps a RAGPipeline and injects conversation context into queries.
    يغلف خط أنابيب RAG ويحقن سياق المحادثة في الاستعلامات

    Usage:
        pipeline = RAGPipeline(config=config, ...)
        manager = RAGConversationManager(pipeline=pipeline)

        session_id = manager.start_session(tenant_id="farm_001")

        result1 = await manager.query(session_id, "When should I irrigate wheat?")
        result2 = await manager.query(session_id, "What about barley?")
        # result2 will have conversation context from result1 injected
    """

    # Conversation context injection template
    _CONTEXT_PREFIX_EN = (
        "Previous conversation:\n{history}\n\nBased on the above conversation, answer the following question:\n"
    )
    _CONTEXT_PREFIX_AR = "المحادثة السابقة:\n{history}\n\nبناءً على المحادثة أعلاه، أجب عن السؤال التالي:\n"

    def __init__(
        self,
        pipeline: RAGPipeline,
        memory: ConversationMemory | None = None,
        inject_context: bool = True,
        context_turns: int = 3,
    ) -> None:
        self._pipeline = pipeline
        self._memory = memory or ConversationMemory()
        self._inject_context = inject_context
        self._context_turns = context_turns

        # Register a pre-hook on query processing to inject history
        if inject_context:
            self._pipeline.add_pre_hook(
                RAGStage.QUERY_PROCESSING,
                self._inject_conversation_context,
            )

        logger.info(
            "rag_conversation_manager_init",
            inject_context=inject_context,
            context_turns=context_turns,
        )

    @property
    def memory(self) -> ConversationMemory:
        """Access the underlying conversation memory.
        الوصول إلى ذاكرة المحادثة الأساسية"""
        return self._memory

    @property
    def pipeline(self) -> RAGPipeline:
        """Access the underlying RAG pipeline.
        الوصول إلى خط أنابيب RAG الأساسي"""
        return self._pipeline

    def start_session(
        self,
        session_id: str | None = None,
        tenant_id: str | None = None,
        language: str = "en",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Start a new conversation session. Returns session_id.
        بدء جلسة محادثة جديدة. يرجع معرف الجلسة"""
        return self._memory.create_session(
            session_id=session_id,
            tenant_id=tenant_id,
            language=language,
            metadata=metadata,
        )

    async def query(
        self,
        session_id: str,
        query: str,
        query_ar: str | None = None,
        collection: str = "default",
        top_k: int = 5,
        language: str = "en",
        **kwargs: Any,
    ) -> RAGResult:
        """Run a conversational RAG query with session context.
        تشغيل استعلام RAG محادثي مع سياق الجلسة

        The query is augmented with conversation history from the session
        before being sent to the RAG pipeline. The response is stored
        back in the session for future context injection.

        Args:
            session_id: Conversation session identifier
            query: User query in English
            query_ar: User query in Arabic (optional)
            collection: Knowledge base collection to search
            top_k: Number of results to retrieve
            language: Response language (en, ar, both)
            **kwargs: Additional RAGRequest parameters

        Returns:
            RAGResult with answer and sources
        """
        # Ensure session exists
        session = self._memory.get_session(session_id)
        if session is None:
            self._memory.create_session(session_id=session_id, language=language)

        # Store session_id in request context for the pre-hook
        request = RAGRequest(
            query=query,
            query_ar=query_ar,
            collection=collection,
            top_k=top_k,
            language=language,
            context={"session_id": session_id, **kwargs.pop("context", {})},
            **kwargs,
        )

        # Run pipeline (pre-hook will inject conversation context)
        result = await self._pipeline.run(request)

        # Store the turn in memory
        answer = ""
        answer_ar = None
        confidence = 0.0
        sources_count = len(result.retrieval_results)

        if result.generation_result:
            answer = result.generation_result.answer
            answer_ar = result.generation_result.answer_ar
            confidence = result.generation_result.confidence

        self._memory.add_turn(
            session_id=session_id,
            query=query,
            answer=answer,
            query_ar=query_ar,
            answer_ar=answer_ar,
            confidence=confidence,
            sources_count=sources_count,
        )

        return result

    async def _inject_conversation_context(self, ctx: Any) -> Any:
        """Pre-hook: inject conversation history into query context.
        الخطاف المسبق: حقن تاريخ المحادثة في سياق الاستعلام

        This is called by the RAG pipeline before query processing.
        It augments the query with recent conversation history so the
        retrieval and generation stages have conversational context.
        """
        session_id = ctx.request.context.get("session_id")
        if not session_id:
            return ctx

        # Get conversation history
        language = ctx.request.language or "en"
        history = self._memory.get_context(
            session_id=session_id,
            max_turns=self._context_turns,
            language=language,
        )

        if not history:
            return ctx

        # Inject history into query for retrieval context
        if language == "ar":
            augmented_query = self._CONTEXT_PREFIX_AR.format(history=history) + ctx.query
        else:
            augmented_query = self._CONTEXT_PREFIX_EN.format(history=history) + ctx.query

        # Store original query and set augmented one
        ctx.metadata["original_query"] = ctx.query
        ctx.metadata["conversation_history"] = history
        ctx.query = augmented_query

        logger.debug(
            "conversation_context_injected",
            session_id=session_id,
            history_turns=history.count("\n\n") + 1,
            original_query_length=len(ctx.metadata["original_query"]),
            augmented_query_length=len(ctx.query),
        )

        return ctx

    def end_session(self, session_id: str) -> bool:
        """End a conversation session.
        إنهاء جلسة محادثة"""
        return self._memory.delete_session(session_id)

    def get_session_stats(self, session_id: str) -> dict[str, Any] | None:
        """Get stats for a specific session.
        الحصول على إحصائيات لجلسة محددة"""
        session = self._memory.get_session(session_id)
        if session is None:
            return None

        return {
            "session_id": session.session_id,
            "turn_count": session.turn_count,
            "created_at": session.created_at,
            "last_active": session.last_active,
            "tenant_id": session.tenant_id,
            "language": session.language,
            "age_seconds": time.time() - session.created_at,
        }


# Export classes
__all__ = [
    "ConversationMemory",
    "ConversationSession",
    "ConversationTurn",
    "RAGConversationManager",
]
