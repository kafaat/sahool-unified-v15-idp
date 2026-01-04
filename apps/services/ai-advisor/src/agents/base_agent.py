"""
Base Agent Class
فئة الوكيل الأساسي

Base class for all AI agents in the system.
الفئة الأساسية لجميع وكلاء الذكاء الاصطناعي في النظام.
"""

import sys
from abc import ABC, abstractmethod
from collections import deque
from typing import Any

import structlog
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import Tool

from ..config import settings

logger = structlog.get_logger()


class ConversationMemory:
    """Manages conversation history with size limits"""

    def __init__(self, max_messages: int = 50, max_tokens: int = 8000):
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self._messages = deque(maxlen=max_messages)
        self._token_count = 0

    def add_message(self, role: str, content: str):
        """Add a message to history"""
        # Estimate token count (rough: 4 chars per token)
        tokens = len(content) // 4

        # Remove old messages if needed
        while self._token_count + tokens > self.max_tokens and self._messages:
            old_msg = self._messages.popleft()
            self._token_count -= len(old_msg.get("content", "")) // 4

        self._messages.append({"role": role, "content": content})
        self._token_count += tokens

    def get_messages(self) -> list:
        """Get all messages"""
        return list(self._messages)

    def clear(self):
        """Clear all messages"""
        self._messages.clear()
        self._token_count = 0

    def get_memory_usage(self) -> dict:
        """Get current memory usage stats"""
        return {
            "message_count": len(self._messages),
            "estimated_tokens": self._token_count,
            "memory_bytes": sys.getsizeof(self._messages),
        }


class BaseAgent(ABC):
    """
    Base class for all specialized agents
    الفئة الأساسية لجميع الوكلاء المتخصصين

    Each agent has:
    - A specific role and expertise area
    - Access to specialized tools
    - Connection to Claude LLM
    - RAG capabilities for knowledge retrieval

    كل وكيل لديه:
    - دور ومجال خبرة محدد
    - الوصول إلى أدوات متخصصة
    - اتصال بنموذج Claude
    - قدرات RAG لاسترجاع المعرفة
    """

    def __init__(
        self,
        name: str,
        role: str,
        tools: list[Tool] | None = None,
        retriever: Any | None = None,
    ):
        """
        Initialize the base agent
        تهيئة الوكيل الأساسي

        Args:
            name: Agent name | اسم الوكيل
            role: Agent's role description | وصف دور الوكيل
            tools: List of tools available to agent | قائمة الأدوات المتاحة
            retriever: RAG retriever instance | مثيل مسترجع RAG
        """
        self.name = name
        self.role = role
        self.tools = tools or []
        self.retriever = retriever

        # Initialize Claude LLM | تهيئة نموذج Claude
        self.llm = ChatAnthropic(
            anthropic_api_key=settings.anthropic_api_key,
            model=settings.claude_model,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
        )

        # Conversation memory with cleanup | ذاكرة المحادثة مع التنظيف
        self.conversation_memory = ConversationMemory(
            max_messages=50,  # Maximum 50 messages
            max_tokens=8000,  # Maximum ~8000 tokens
        )

        logger.info(
            "agent_initialized",
            agent_name=self.name,
            role=self.role,
            num_tools=len(self.tools),
        )

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent
        الحصول على موجه النظام لهذا الوكيل

        Returns:
            System prompt string | نص موجه النظام
        """
        pass

    def _retrieve_context(self, query: str) -> str:
        """
        Retrieve relevant context from RAG system
        استرجاع السياق ذي الصلة من نظام RAG

        Args:
            query: Search query | استعلام البحث

        Returns:
            Retrieved context | السياق المسترجع
        """
        if not self.retriever:
            return ""

        try:
            docs = self.retriever.retrieve(query, top_k=settings.rag_top_k)
            context = "\n\n".join([doc.page_content for doc in docs])
            logger.debug("rag_context_retrieved", num_docs=len(docs))
            return context
        except Exception as e:
            logger.error("rag_retrieval_failed", error=str(e))
            return ""

    async def think(
        self, query: str, context: dict[str, Any] | None = None, use_rag: bool = True
    ) -> dict[str, Any]:
        """
        Process a query and generate a response
        معالجة استعلام وإنشاء استجابة

        Args:
            query: User query | استعلام المستخدم
            context: Additional context | سياق إضافي
            use_rag: Whether to use RAG retrieval | استخدام RAG أم لا

        Returns:
            Agent response | استجابة الوكيل
        """
        try:
            # Build messages | بناء الرسائل
            messages = [SystemMessage(content=self.get_system_prompt())]

            # Add RAG context if enabled | إضافة سياق RAG إذا كان مفعلاً
            if use_rag:
                rag_context = self._retrieve_context(query)
                if rag_context:
                    context = context or {}
                    context["knowledge_base"] = rag_context

            # Add context if provided | إضافة السياق إذا تم توفيره
            if context:
                context_str = self._format_context(context)
                messages.append(HumanMessage(content=f"Context:\n{context_str}"))

            # Add user query | إضافة استعلام المستخدم
            messages.append(HumanMessage(content=query))

            # Get response from Claude | الحصول على استجابة من Claude
            response = await self.llm.ainvoke(messages)

            # Store in conversation memory | تخزين في ذاكرة المحادثة
            self.conversation_memory.add_message("user", query)
            self.conversation_memory.add_message("assistant", response.content)

            logger.info(
                "agent_response_generated",
                agent_name=self.name,
                query_length=len(query),
                response_length=len(response.content),
                memory_usage=self.conversation_memory.get_memory_usage(),
            )

            return {
                "agent": self.name,
                "role": self.role,
                "response": response.content,
                "confidence": self._calculate_confidence(response),
            }

        except Exception as e:
            logger.error("agent_thinking_failed", agent_name=self.name, error=str(e))
            raise

    def _format_context(self, context: dict[str, Any]) -> str:
        """
        Format context dictionary into a string
        تنسيق قاموس السياق إلى نص

        Args:
            context: Context dictionary | قاموس السياق

        Returns:
            Formatted context string | نص السياق المنسق
        """
        lines = []
        for key, value in context.items():
            if isinstance(value, dict | list):
                import json

                value = json.dumps(value, ensure_ascii=False, indent=2)
            lines.append(f"{key}: {value}")
        return "\n".join(lines)

    def _calculate_confidence(self, response: AIMessage) -> float:
        """
        Calculate confidence score for the response
        حساب درجة الثقة للاستجابة

        Args:
            response: AI response message | رسالة استجابة الذكاء الاصطناعي

        Returns:
            Confidence score (0-1) | درجة الثقة (0-1)
        """
        # Simple heuristic based on response length and certainty markers
        # استدلال بسيط بناءً على طول الاستجابة وعلامات اليقين
        content = response.content.lower()

        # Check for uncertainty markers | التحقق من علامات عدم اليقين
        uncertainty_markers = [
            "i'm not sure",
            "maybe",
            "possibly",
            "might",
            "could be",
            "لست متأكداً",
            "ربما",
            "من المحتمل",
            "قد يكون",
        ]

        confidence = 0.8  # Default confidence | الثقة الافتراضية

        for marker in uncertainty_markers:
            if marker in content:
                confidence -= 0.1

        return max(0.3, min(1.0, confidence))

    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Execute a specific tool
        تنفيذ أداة محددة

        Args:
            tool_name: Name of the tool to use | اسم الأداة المراد استخدامها
            **kwargs: Tool arguments | معاملات الأداة

        Returns:
            Tool result | نتيجة الأداة
        """
        for tool in self.tools:
            if tool.name == tool_name:
                try:
                    result = await tool.arun(**kwargs)
                    logger.info(
                        "tool_executed", agent_name=self.name, tool_name=tool_name
                    )
                    return result
                except Exception as e:
                    logger.error(
                        "tool_execution_failed",
                        agent_name=self.name,
                        tool_name=tool_name,
                        error=str(e),
                    )
                    raise

        raise ValueError(f"Tool '{tool_name}' not found for agent '{self.name}'")

    def reset_conversation(self):
        """
        Clear conversation memory
        مسح ذاكرة المحادثة
        """
        self.conversation_memory.clear()
        logger.debug("conversation_reset", agent_name=self.name)

    def get_info(self) -> dict[str, Any]:
        """
        Get agent information
        الحصول على معلومات الوكيل

        Returns:
            Agent metadata | بيانات تعريف الوكيل
        """
        memory_usage = self.conversation_memory.get_memory_usage()
        return {
            "name": self.name,
            "role": self.role,
            "tools": [tool.name for tool in self.tools],
            "has_rag": self.retriever is not None,
            "conversation_length": memory_usage["message_count"],
            "memory_usage": memory_usage,
        }
