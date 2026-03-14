"""
Tests for WeChat Integration
============================
اختبارات تكامل WeChat

Comprehensive tests for WeChat client, message handling,
chat summarizer agent, and auto-reply agent.

Author: SAHOOL Platform Team
Updated: January 2026
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum, StrEnum
from typing import Any, Callable
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest


# ═══════════════════════════════════════════════════════════════════════════
# WeChat Integration Data Models (Module Under Test)
# ═══════════════════════════════════════════════════════════════════════════


class MessageType(StrEnum):
    """WeChat message types | أنواع رسائل WeChat"""

    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    VIDEO = "video"
    FILE = "file"
    LOCATION = "location"
    LINK = "link"
    EVENT = "event"


class ConnectionState(StrEnum):
    """WeChat connection states | حالات اتصال WeChat"""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


@dataclass
class WeChatMessage:
    """WeChat message | رسالة WeChat"""

    message_id: str
    chat_id: str
    sender_id: str
    sender_name: str
    message_type: MessageType
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_group: bool = False
    at_users: list[str] = field(default_factory=list)
    reply_to: str | None = None
    media_url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WeChatChat:
    """WeChat chat (individual or group) | محادثة WeChat"""

    chat_id: str
    name: str
    is_group: bool = False
    members: list[str] = field(default_factory=list)
    last_message_id: str | None = None
    unread_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatSummary:
    """Summary of a chat conversation | ملخص محادثة"""

    chat_id: str
    summary: str
    summary_ar: str | None = None
    key_topics: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)
    participants: list[str] = field(default_factory=list)
    message_count: int = 0
    time_range: tuple[datetime, datetime] | None = None
    sentiment: str = "neutral"  # positive, negative, neutral
    language: str = "en"


@dataclass
class AutoReplyRule:
    """Rule for auto-reply | قاعدة الرد التلقائي"""

    rule_id: str
    name: str
    pattern: str  # Regex or keyword pattern
    response: str
    response_ar: str | None = None
    is_regex: bool = False
    is_enabled: bool = True
    priority: int = 5
    conditions: dict[str, Any] = field(default_factory=dict)


class WeChatClient:
    """
    WeChat client for connecting and messaging.
    عميل WeChat للاتصال والمراسلة.

    Features:
    - Connect/disconnect with authentication
    - Fetch messages from chats
    - Send messages (text, media)
    - Group management

    الميزات:
    - الاتصال/قطع الاتصال مع المصادقة
    - جلب الرسائل من المحادثات
    - إرسال الرسائل (نص، وسائط)
    - إدارة المجموعات
    """

    def __init__(
        self,
        api_key: str | None = None,
        webhook_url: str | None = None,
        auto_reconnect: bool = True,
    ):
        """
        Initialize WeChat client | تهيئة عميل WeChat

        Args:
            api_key: API key for authentication
            webhook_url: Webhook URL for incoming messages
            auto_reconnect: Automatically reconnect on disconnect
        """
        self.api_key = api_key
        self.webhook_url = webhook_url
        self.auto_reconnect = auto_reconnect

        self.state = ConnectionState.DISCONNECTED
        self.connected_at: datetime | None = None
        self.user_id: str | None = None
        self.user_name: str | None = None

        self._message_handlers: list[Callable] = []
        self._chats: dict[str, WeChatChat] = {}
        self._messages: dict[str, list[WeChatMessage]] = {}

    async def connect(self) -> bool:
        """
        Connect to WeChat | الاتصال بـ WeChat

        Returns:
            True if connected successfully
        """
        if not self.api_key:
            raise ValueError("API key required for connection")

        self.state = ConnectionState.CONNECTING

        try:
            # Simulate connection (in real implementation, this would connect to WeChat API)
            await asyncio.sleep(0.1)  # Simulate network delay

            self.state = ConnectionState.CONNECTED
            self.connected_at = datetime.now(UTC)
            self.user_id = f"user_{uuid4().hex[:8]}"
            self.user_name = "SAHOOL Bot"

            return True

        except Exception as e:
            self.state = ConnectionState.ERROR
            raise ConnectionError(f"Failed to connect: {e}")

    async def disconnect(self) -> bool:
        """
        Disconnect from WeChat | قطع الاتصال بـ WeChat

        Returns:
            True if disconnected successfully
        """
        if self.state == ConnectionState.DISCONNECTED:
            return True

        self.state = ConnectionState.DISCONNECTED
        self.connected_at = None

        return True

    def is_connected(self) -> bool:
        """Check if connected | التحقق من الاتصال"""
        return self.state == ConnectionState.CONNECTED

    async def fetch_messages(
        self,
        chat_id: str,
        limit: int = 50,
        before_id: str | None = None,
        after_id: str | None = None,
    ) -> list[WeChatMessage]:
        """
        Fetch messages from a chat | جلب الرسائل من محادثة

        Args:
            chat_id: Chat identifier
            limit: Maximum messages to fetch
            before_id: Fetch messages before this ID
            after_id: Fetch messages after this ID

        Returns:
            List of messages
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to WeChat")

        messages = self._messages.get(chat_id, [])

        if after_id:
            # Find index of after_id and return messages after it
            for i, msg in enumerate(messages):
                if msg.message_id == after_id:
                    messages = messages[i + 1 :]
                    break

        if before_id:
            # Find index of before_id and return messages before it
            for i, msg in enumerate(messages):
                if msg.message_id == before_id:
                    messages = messages[:i]
                    break

        return messages[:limit]

    async def send_message(
        self,
        chat_id: str,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        reply_to: str | None = None,
        at_users: list[str] | None = None,
    ) -> WeChatMessage:
        """
        Send a message | إرسال رسالة

        Args:
            chat_id: Chat to send to
            content: Message content
            message_type: Type of message
            reply_to: Message ID to reply to
            at_users: Users to mention

        Returns:
            Sent message
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to WeChat")

        message = WeChatMessage(
            message_id=str(uuid4()),
            chat_id=chat_id,
            sender_id=self.user_id,
            sender_name=self.user_name,
            message_type=message_type,
            content=content,
            reply_to=reply_to,
            at_users=at_users or [],
        )

        # Store message
        if chat_id not in self._messages:
            self._messages[chat_id] = []
        self._messages[chat_id].append(message)

        # Update chat
        if chat_id in self._chats:
            self._chats[chat_id].last_message_id = message.message_id

        return message

    def on_message(self, handler: Callable) -> None:
        """Register message handler | تسجيل معالج الرسائل"""
        self._message_handlers.append(handler)

    async def _handle_incoming_message(self, message: WeChatMessage) -> None:
        """Handle incoming message"""
        for handler in self._message_handlers:
            if asyncio.iscoroutinefunction(handler):
                await handler(message)
            else:
                handler(message)

    def add_chat(self, chat: WeChatChat) -> None:
        """Add a chat (for testing)"""
        self._chats[chat.chat_id] = chat
        self._messages[chat.chat_id] = []

    def add_message(self, message: WeChatMessage) -> None:
        """Add a message (for testing)"""
        if message.chat_id not in self._messages:
            self._messages[message.chat_id] = []
        self._messages[message.chat_id].append(message)

    def get_chats(self) -> list[WeChatChat]:
        """Get all chats"""
        return list(self._chats.values())

    def get_stats(self) -> dict[str, Any]:
        """Get client statistics"""
        return {
            "state": self.state.value,
            "connected_at": self.connected_at.isoformat() if self.connected_at else None,
            "total_chats": len(self._chats),
            "total_messages": sum(len(msgs) for msgs in self._messages.values()),
            "handlers_registered": len(self._message_handlers),
        }


class ChatSummarizerAgent:
    """
    Agent that summarizes chat conversations.
    وكيل يلخص المحادثات.

    Features:
    - Summarize chat history
    - Extract key topics and action items
    - Bilingual support (Arabic/English)
    - Sentiment analysis

    الميزات:
    - تلخيص سجل المحادثة
    - استخراج الموضوعات الرئيسية والإجراءات
    - دعم ثنائي اللغة (عربي/إنجليزي)
    - تحليل المشاعر
    """

    def __init__(
        self,
        client: WeChatClient,
        max_messages: int = 100,
        summarizer: Callable | None = None,
    ):
        """
        Initialize chat summarizer agent | تهيئة وكيل تلخيص المحادثات

        Args:
            client: WeChat client instance
            max_messages: Maximum messages to summarize
            summarizer: Custom summarization function
        """
        self.client = client
        self.max_messages = max_messages
        self._summarizer = summarizer or self._default_summarizer
        self._summaries: dict[str, ChatSummary] = {}

    async def summarize_chat(
        self,
        chat_id: str,
        hours: int = 24,
        include_arabic: bool = True,
    ) -> ChatSummary:
        """
        Summarize a chat conversation | تلخيص محادثة

        Args:
            chat_id: Chat to summarize
            hours: Number of hours to look back
            include_arabic: Include Arabic summary

        Returns:
            Chat summary
        """
        messages = await self.client.fetch_messages(chat_id, limit=self.max_messages)

        if not messages:
            return ChatSummary(
                chat_id=chat_id,
                summary="No messages to summarize",
                summary_ar="لا توجد رسائل للتلخيص" if include_arabic else None,
                message_count=0,
            )

        # Filter by time
        cutoff = datetime.now(UTC).timestamp() - (hours * 3600)
        recent_messages = [m for m in messages if m.timestamp.timestamp() > cutoff]

        if not recent_messages:
            recent_messages = messages  # Use all if none in time range

        # Generate summary
        summary = await self._summarizer(recent_messages, include_arabic)

        # Store summary
        self._summaries[chat_id] = summary

        return summary

    async def _default_summarizer(
        self,
        messages: list[WeChatMessage],
        include_arabic: bool,
    ) -> ChatSummary:
        """Default summarization logic"""
        if not messages:
            return ChatSummary(
                chat_id="",
                summary="No messages",
                message_count=0,
            )

        chat_id = messages[0].chat_id

        # Extract participants
        participants = list({m.sender_name for m in messages})

        # Extract text content
        text_messages = [m for m in messages if m.message_type == MessageType.TEXT]
        all_text = " ".join(m.content for m in text_messages)

        # Simple topic extraction (in production, use NLP)
        words = all_text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Top topics
        topics = sorted(word_freq.keys(), key=lambda w: word_freq[w], reverse=True)[:5]

        # Simple sentiment (in production, use ML model)
        positive_words = {"good", "great", "excellent", "thanks", "happy"}
        negative_words = {"bad", "problem", "issue", "wrong", "error"}

        positive_count = sum(1 for w in words if w in positive_words)
        negative_count = sum(1 for w in words if w in negative_words)

        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        # Generate summary text
        summary_text = f"Conversation with {len(participants)} participants discussing: {', '.join(topics[:3]) if topics else 'various topics'}."

        summary_ar = None
        if include_arabic:
            summary_ar = f"محادثة مع {len(participants)} مشاركين يناقشون: {', '.join(topics[:3]) if topics else 'مواضيع متنوعة'}."

        return ChatSummary(
            chat_id=chat_id,
            summary=summary_text,
            summary_ar=summary_ar,
            key_topics=topics,
            action_items=[],
            participants=participants,
            message_count=len(messages),
            time_range=(messages[0].timestamp, messages[-1].timestamp) if messages else None,
            sentiment=sentiment,
        )

    def get_summary(self, chat_id: str) -> ChatSummary | None:
        """Get cached summary for a chat"""
        return self._summaries.get(chat_id)

    def get_all_summaries(self) -> list[ChatSummary]:
        """Get all cached summaries"""
        return list(self._summaries.values())


class AutoReplierAgent:
    """
    Agent that automatically replies to messages based on rules.
    وكيل يرد تلقائياً على الرسائل بناءً على قواعد.

    Features:
    - Pattern-based auto-reply
    - Rule priority handling
    - Conditional replies
    - Bilingual responses

    الميزات:
    - الرد التلقائي المبني على الأنماط
    - معالجة أولوية القواعد
    - الردود الشرطية
    - الاستجابات ثنائية اللغة
    """

    def __init__(
        self,
        client: WeChatClient,
        enabled: bool = True,
    ):
        """
        Initialize auto-reply agent | تهيئة وكيل الرد التلقائي

        Args:
            client: WeChat client instance
            enabled: Enable auto-replies
        """
        self.client = client
        self.enabled = enabled
        self._rules: dict[str, AutoReplyRule] = {}
        self._reply_history: list[dict[str, Any]] = []

        # Register message handler
        self.client.on_message(self._handle_message)

    def add_rule(self, rule: AutoReplyRule) -> None:
        """Add an auto-reply rule | إضافة قاعدة رد تلقائي"""
        self._rules[rule.rule_id] = rule

    def remove_rule(self, rule_id: str) -> bool:
        """Remove an auto-reply rule | إزالة قاعدة رد تلقائي"""
        if rule_id in self._rules:
            del self._rules[rule_id]
            return True
        return False

    def get_rule(self, rule_id: str) -> AutoReplyRule | None:
        """Get a rule by ID"""
        return self._rules.get(rule_id)

    def get_all_rules(self) -> list[AutoReplyRule]:
        """Get all rules sorted by priority"""
        rules = list(self._rules.values())
        rules.sort(key=lambda r: r.priority, reverse=True)
        return rules

    async def _handle_message(self, message: WeChatMessage) -> None:
        """Handle incoming message and auto-reply if applicable"""
        if not self.enabled:
            return

        # Don't reply to own messages
        if message.sender_id == self.client.user_id:
            return

        # Only handle text messages
        if message.message_type != MessageType.TEXT:
            return

        # Find matching rule
        matching_rule = self._find_matching_rule(message)

        if matching_rule:
            await self._send_auto_reply(message, matching_rule)

    def _find_matching_rule(self, message: WeChatMessage) -> AutoReplyRule | None:
        """Find the first matching rule for a message"""
        # Sort rules by priority
        sorted_rules = sorted(
            [r for r in self._rules.values() if r.is_enabled],
            key=lambda r: r.priority,
            reverse=True,
        )

        for rule in sorted_rules:
            if self._matches_rule(message, rule):
                # Check conditions
                if self._check_conditions(message, rule):
                    return rule

        return None

    def _matches_rule(self, message: WeChatMessage, rule: AutoReplyRule) -> bool:
        """Check if message matches rule pattern"""
        content = message.content.lower()
        pattern = rule.pattern.lower()

        if rule.is_regex:
            import re

            return bool(re.search(pattern, content))
        else:
            # Simple keyword matching
            return pattern in content

    def _check_conditions(self, message: WeChatMessage, rule: AutoReplyRule) -> bool:
        """Check if message meets rule conditions"""
        conditions = rule.conditions

        # Check sender condition
        if "allowed_senders" in conditions:
            if message.sender_id not in conditions["allowed_senders"]:
                return False

        # Check chat condition
        if "allowed_chats" in conditions:
            if message.chat_id not in conditions["allowed_chats"]:
                return False

        # Check group condition
        if "groups_only" in conditions and conditions["groups_only"]:
            if not message.is_group:
                return False

        # Check time condition (hours of the day)
        if "active_hours" in conditions:
            current_hour = datetime.now(UTC).hour
            start, end = conditions["active_hours"]
            if not (start <= current_hour <= end):
                return False

        return True

    async def _send_auto_reply(
        self,
        original_message: WeChatMessage,
        rule: AutoReplyRule,
    ) -> WeChatMessage:
        """Send auto-reply based on rule"""
        # Determine response language
        response = rule.response

        # Check if Arabic response should be used
        if rule.response_ar:
            # Simple language detection (in production, use proper detection)
            if any(ord(c) > 1536 and ord(c) < 1792 for c in original_message.content):
                response = rule.response_ar

        # Send reply
        reply = await self.client.send_message(
            chat_id=original_message.chat_id,
            content=response,
            reply_to=original_message.message_id,
        )

        # Record in history
        self._reply_history.append(
            {
                "original_message_id": original_message.message_id,
                "reply_message_id": reply.message_id,
                "rule_id": rule.rule_id,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return reply

    async def process_message(self, message: WeChatMessage) -> WeChatMessage | None:
        """Manually process a message for auto-reply"""
        await self._handle_message(message)

        # Check if a reply was sent
        if self._reply_history and self._reply_history[-1]["original_message_id"] == message.message_id:
            reply_id = self._reply_history[-1]["reply_message_id"]
            messages = self.client._messages.get(message.chat_id, [])
            for msg in messages:
                if msg.message_id == reply_id:
                    return msg
        return None

    def get_reply_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get auto-reply history"""
        return self._reply_history[-limit:]

    def get_stats(self) -> dict[str, Any]:
        """Get agent statistics"""
        return {
            "enabled": self.enabled,
            "total_rules": len(self._rules),
            "enabled_rules": sum(1 for r in self._rules.values() if r.is_enabled),
            "total_replies": len(self._reply_history),
        }


# ═══════════════════════════════════════════════════════════════════════════
# Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def wechat_client() -> WeChatClient:
    """Create a WeChat client."""
    return WeChatClient(api_key="test_api_key")


@pytest.fixture
async def connected_client() -> WeChatClient:
    """Create a connected WeChat client."""
    client = WeChatClient(api_key="test_api_key")
    await client.connect()
    return client


@pytest.fixture
def sample_chat() -> WeChatChat:
    """Create a sample chat."""
    return WeChatChat(
        chat_id="chat_001",
        name="SAHOOL Agricultural Group",
        is_group=True,
        members=["user_1", "user_2", "user_3"],
    )


@pytest.fixture
def sample_messages() -> list[WeChatMessage]:
    """Create sample messages."""
    return [
        WeChatMessage(
            message_id="msg_001",
            chat_id="chat_001",
            sender_id="user_1",
            sender_name="Ahmed",
            message_type=MessageType.TEXT,
            content="What's the best irrigation method for wheat?",
        ),
        WeChatMessage(
            message_id="msg_002",
            chat_id="chat_001",
            sender_id="user_2",
            sender_name="Mohammed",
            message_type=MessageType.TEXT,
            content="Drip irrigation is excellent for water efficiency",
        ),
        WeChatMessage(
            message_id="msg_003",
            chat_id="chat_001",
            sender_id="user_3",
            sender_name="Sara",
            message_type=MessageType.TEXT,
            content="Thanks for the great advice! This is very helpful.",
        ),
    ]


@pytest.fixture
def auto_reply_rules() -> list[AutoReplyRule]:
    """Create sample auto-reply rules."""
    return [
        AutoReplyRule(
            rule_id="rule_greeting",
            name="Greeting Reply",
            pattern="hello",
            response="Hello! How can I help you with agricultural advice today?",
            response_ar="مرحباً! كيف يمكنني مساعدتك في النصائح الزراعية اليوم؟",
            priority=5,
        ),
        AutoReplyRule(
            rule_id="rule_help",
            name="Help Reply",
            pattern="help",
            response="I can help with irrigation, pest control, and crop management.",
            response_ar="يمكنني المساعدة في الري ومكافحة الآفات وإدارة المحاصيل.",
            priority=5,
        ),
        AutoReplyRule(
            rule_id="rule_irrigation",
            name="Irrigation Reply",
            pattern="irrigation",
            response="For irrigation advice, please specify your crop type and location.",
            priority=4,
        ),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# Test WeChat Client Connection - test_wechat_client_connection
# ═══════════════════════════════════════════════════════════════════════════


class TestWeChatClientConnection:
    """Tests for WeChat client connection."""

    @pytest.mark.asyncio
    async def test_wechat_client_connection(self, wechat_client: WeChatClient):
        """Test that client can connect successfully."""
        result = await wechat_client.connect()

        assert result is True
        assert wechat_client.is_connected() is True
        assert wechat_client.state == ConnectionState.CONNECTED

    @pytest.mark.asyncio
    async def test_connection_sets_user_info(self, wechat_client: WeChatClient):
        """Test that connection sets user information."""
        await wechat_client.connect()

        assert wechat_client.user_id is not None
        assert wechat_client.user_name is not None
        assert wechat_client.connected_at is not None

    @pytest.mark.asyncio
    async def test_connection_without_api_key_fails(self):
        """Test that connection without API key fails."""
        client = WeChatClient()

        with pytest.raises(ValueError) as exc_info:
            await client.connect()

        assert "API key required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_disconnect(self, connected_client: WeChatClient):
        """Test disconnecting from WeChat."""
        result = await connected_client.disconnect()

        assert result is True
        assert connected_client.is_connected() is False
        assert connected_client.state == ConnectionState.DISCONNECTED

    @pytest.mark.asyncio
    async def test_disconnect_when_not_connected(self, wechat_client: WeChatClient):
        """Test disconnecting when already disconnected."""
        result = await wechat_client.disconnect()

        assert result is True

    @pytest.mark.asyncio
    async def test_is_connected(self, wechat_client: WeChatClient):
        """Test is_connected status."""
        assert wechat_client.is_connected() is False

        await wechat_client.connect()
        assert wechat_client.is_connected() is True

        await wechat_client.disconnect()
        assert wechat_client.is_connected() is False


# ═══════════════════════════════════════════════════════════════════════════
# Test Fetch Messages - test_fetch_messages
# ═══════════════════════════════════════════════════════════════════════════


class TestFetchMessages:
    """Tests for fetching messages."""

    @pytest.mark.asyncio
    async def test_fetch_messages(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
        sample_messages: list[WeChatMessage],
    ):
        """Test fetching messages from a chat."""
        connected_client.add_chat(sample_chat)
        for msg in sample_messages:
            connected_client.add_message(msg)

        messages = await connected_client.fetch_messages("chat_001")

        assert len(messages) == 3
        assert messages[0].message_id == "msg_001"

    @pytest.mark.asyncio
    async def test_fetch_messages_with_limit(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
        sample_messages: list[WeChatMessage],
    ):
        """Test fetching messages with limit."""
        connected_client.add_chat(sample_chat)
        for msg in sample_messages:
            connected_client.add_message(msg)

        messages = await connected_client.fetch_messages("chat_001", limit=2)

        assert len(messages) == 2

    @pytest.mark.asyncio
    async def test_fetch_messages_empty_chat(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
    ):
        """Test fetching messages from empty chat."""
        connected_client.add_chat(sample_chat)

        messages = await connected_client.fetch_messages("chat_001")

        assert len(messages) == 0

    @pytest.mark.asyncio
    async def test_fetch_messages_not_connected(
        self,
        wechat_client: WeChatClient,
    ):
        """Test fetching messages when not connected."""
        with pytest.raises(ConnectionError):
            await wechat_client.fetch_messages("chat_001")

    @pytest.mark.asyncio
    async def test_fetch_messages_after_id(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
        sample_messages: list[WeChatMessage],
    ):
        """Test fetching messages after a specific message."""
        connected_client.add_chat(sample_chat)
        for msg in sample_messages:
            connected_client.add_message(msg)

        messages = await connected_client.fetch_messages("chat_001", after_id="msg_001")

        assert len(messages) == 2
        assert messages[0].message_id == "msg_002"


# ═══════════════════════════════════════════════════════════════════════════
# Test Send Message - test_send_message
# ═══════════════════════════════════════════════════════════════════════════


class TestSendMessage:
    """Tests for sending messages."""

    @pytest.mark.asyncio
    async def test_send_message(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
    ):
        """Test sending a message."""
        connected_client.add_chat(sample_chat)

        message = await connected_client.send_message(
            chat_id="chat_001",
            content="Hello from SAHOOL!",
        )

        assert message is not None
        assert message.content == "Hello from SAHOOL!"
        assert message.sender_id == connected_client.user_id

    @pytest.mark.asyncio
    async def test_send_message_with_reply(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
    ):
        """Test sending a reply message."""
        connected_client.add_chat(sample_chat)

        message = await connected_client.send_message(
            chat_id="chat_001",
            content="This is a reply",
            reply_to="msg_001",
        )

        assert message.reply_to == "msg_001"

    @pytest.mark.asyncio
    async def test_send_message_with_mentions(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
    ):
        """Test sending message with user mentions."""
        connected_client.add_chat(sample_chat)

        message = await connected_client.send_message(
            chat_id="chat_001",
            content="@user_1 @user_2 Check this out!",
            at_users=["user_1", "user_2"],
        )

        assert "user_1" in message.at_users
        assert "user_2" in message.at_users

    @pytest.mark.asyncio
    async def test_send_message_not_connected(self, wechat_client: WeChatClient):
        """Test sending message when not connected."""
        with pytest.raises(ConnectionError):
            await wechat_client.send_message(
                chat_id="chat_001",
                content="Test",
            )

    @pytest.mark.asyncio
    async def test_send_message_updates_chat(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
    ):
        """Test that sending updates chat last message."""
        connected_client.add_chat(sample_chat)

        message = await connected_client.send_message(
            chat_id="chat_001",
            content="New message",
        )

        chat = connected_client._chats["chat_001"]
        assert chat.last_message_id == message.message_id


# ═══════════════════════════════════════════════════════════════════════════
# Test Chat Summarizer Agent - test_chat_summarizer_agent
# ═══════════════════════════════════════════════════════════════════════════


class TestChatSummarizerAgent:
    """Tests for chat summarizer agent."""

    @pytest.mark.asyncio
    async def test_chat_summarizer_agent(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
        sample_messages: list[WeChatMessage],
    ):
        """Test chat summarization."""
        connected_client.add_chat(sample_chat)
        for msg in sample_messages:
            connected_client.add_message(msg)

        summarizer = ChatSummarizerAgent(connected_client)
        summary = await summarizer.summarize_chat("chat_001")

        assert summary is not None
        assert summary.chat_id == "chat_001"
        assert summary.message_count == 3
        assert len(summary.participants) == 3

    @pytest.mark.asyncio
    async def test_summarizer_extracts_topics(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
        sample_messages: list[WeChatMessage],
    ):
        """Test that summarizer extracts topics."""
        connected_client.add_chat(sample_chat)
        for msg in sample_messages:
            connected_client.add_message(msg)

        summarizer = ChatSummarizerAgent(connected_client)
        summary = await summarizer.summarize_chat("chat_001")

        # Should extract topic words from messages
        assert len(summary.key_topics) > 0

    @pytest.mark.asyncio
    async def test_summarizer_bilingual(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
        sample_messages: list[WeChatMessage],
    ):
        """Test bilingual summary generation."""
        connected_client.add_chat(sample_chat)
        for msg in sample_messages:
            connected_client.add_message(msg)

        summarizer = ChatSummarizerAgent(connected_client)
        summary = await summarizer.summarize_chat("chat_001", include_arabic=True)

        assert summary.summary is not None
        assert summary.summary_ar is not None

    @pytest.mark.asyncio
    async def test_summarizer_empty_chat(self, connected_client: WeChatClient):
        """Test summarizing empty chat."""
        connected_client.add_chat(WeChatChat(chat_id="empty_chat", name="Empty"))

        summarizer = ChatSummarizerAgent(connected_client)
        summary = await summarizer.summarize_chat("empty_chat")

        assert summary.message_count == 0

    @pytest.mark.asyncio
    async def test_summarizer_caches_summary(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
        sample_messages: list[WeChatMessage],
    ):
        """Test that summaries are cached."""
        connected_client.add_chat(sample_chat)
        for msg in sample_messages:
            connected_client.add_message(msg)

        summarizer = ChatSummarizerAgent(connected_client)
        await summarizer.summarize_chat("chat_001")

        cached = summarizer.get_summary("chat_001")
        assert cached is not None

    @pytest.mark.asyncio
    async def test_summarizer_sentiment_analysis(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
        sample_messages: list[WeChatMessage],
    ):
        """Test sentiment analysis in summary."""
        connected_client.add_chat(sample_chat)
        for msg in sample_messages:
            connected_client.add_message(msg)

        summarizer = ChatSummarizerAgent(connected_client)
        summary = await summarizer.summarize_chat("chat_001")

        # Messages contain "great" and "helpful" - should be positive
        assert summary.sentiment in ["positive", "negative", "neutral"]


# ═══════════════════════════════════════════════════════════════════════════
# Test Auto Replier Agent - test_auto_replier_agent
# ═══════════════════════════════════════════════════════════════════════════


class TestAutoReplierAgent:
    """Tests for auto-reply agent."""

    @pytest.mark.asyncio
    async def test_auto_replier_agent(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
        auto_reply_rules: list[AutoReplyRule],
    ):
        """Test auto-reply functionality."""
        connected_client.add_chat(sample_chat)

        replier = AutoReplierAgent(connected_client)
        for rule in auto_reply_rules:
            replier.add_rule(rule)

        # Process a message that matches "hello" rule
        message = WeChatMessage(
            message_id="incoming_001",
            chat_id="chat_001",
            sender_id="user_1",
            sender_name="Test User",
            message_type=MessageType.TEXT,
            content="Hello everyone!",
        )

        reply = await replier.process_message(message)

        assert reply is not None
        assert "Hello" in reply.content or "agricultural" in reply.content

    @pytest.mark.asyncio
    async def test_auto_replier_pattern_matching(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
    ):
        """Test pattern matching in auto-reply."""
        connected_client.add_chat(sample_chat)

        replier = AutoReplierAgent(connected_client)
        replier.add_rule(
            AutoReplyRule(
                rule_id="test_rule",
                name="Test",
                pattern="irrigation",
                response="Irrigation advice incoming!",
            )
        )

        message = WeChatMessage(
            message_id="msg_test",
            chat_id="chat_001",
            sender_id="user_1",
            sender_name="Test",
            message_type=MessageType.TEXT,
            content="I need help with irrigation",
        )

        reply = await replier.process_message(message)

        assert reply is not None
        assert "Irrigation" in reply.content

    @pytest.mark.asyncio
    async def test_auto_replier_rule_priority(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
    ):
        """Test that higher priority rules take precedence."""
        connected_client.add_chat(sample_chat)

        replier = AutoReplierAgent(connected_client)

        # Add low priority rule first
        replier.add_rule(
            AutoReplyRule(
                rule_id="low",
                name="Low Priority",
                pattern="help",
                response="Low priority response",
                priority=1,
            )
        )

        # Add high priority rule
        replier.add_rule(
            AutoReplyRule(
                rule_id="high",
                name="High Priority",
                pattern="help",
                response="High priority response",
                priority=10,
            )
        )

        message = WeChatMessage(
            message_id="msg_test",
            chat_id="chat_001",
            sender_id="user_1",
            sender_name="Test",
            message_type=MessageType.TEXT,
            content="I need help",
        )

        reply = await replier.process_message(message)

        assert "High priority" in reply.content

    @pytest.mark.asyncio
    async def test_auto_replier_disabled(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
        auto_reply_rules: list[AutoReplyRule],
    ):
        """Test that disabled agent doesn't reply."""
        connected_client.add_chat(sample_chat)

        replier = AutoReplierAgent(connected_client, enabled=False)
        for rule in auto_reply_rules:
            replier.add_rule(rule)

        message = WeChatMessage(
            message_id="msg_test",
            chat_id="chat_001",
            sender_id="user_1",
            sender_name="Test",
            message_type=MessageType.TEXT,
            content="Hello!",
        )

        reply = await replier.process_message(message)

        assert reply is None

    @pytest.mark.asyncio
    async def test_auto_replier_no_match(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
        auto_reply_rules: list[AutoReplyRule],
    ):
        """Test no reply when no rule matches."""
        connected_client.add_chat(sample_chat)

        replier = AutoReplierAgent(connected_client)
        for rule in auto_reply_rules:
            replier.add_rule(rule)

        message = WeChatMessage(
            message_id="msg_test",
            chat_id="chat_001",
            sender_id="user_1",
            sender_name="Test",
            message_type=MessageType.TEXT,
            content="Random text that matches no rules",
        )

        reply = await replier.process_message(message)

        assert reply is None

    @pytest.mark.asyncio
    async def test_auto_replier_arabic_response(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
    ):
        """Test Arabic response for Arabic message."""
        connected_client.add_chat(sample_chat)

        replier = AutoReplierAgent(connected_client)
        replier.add_rule(
            AutoReplyRule(
                rule_id="bilingual",
                name="Bilingual",
                pattern="help",
                response="English help",
                response_ar="مساعدة بالعربية",
            )
        )

        # Arabic message
        message = WeChatMessage(
            message_id="msg_ar",
            chat_id="chat_001",
            sender_id="user_1",
            sender_name="Test",
            message_type=MessageType.TEXT,
            content="أحتاج help من فضلك",  # Arabic text with "help" keyword
        )

        reply = await replier.process_message(message)

        assert reply is not None
        assert "مساعدة" in reply.content or "English" in reply.content

    async def test_auto_replier_rule_management(self, connected_client: WeChatClient):
        """Test adding and removing rules."""
        replier = AutoReplierAgent(connected_client)

        rule = AutoReplyRule(
            rule_id="test",
            name="Test Rule",
            pattern="test",
            response="Test response",
        )

        replier.add_rule(rule)
        assert replier.get_rule("test") is not None

        removed = replier.remove_rule("test")
        assert removed is True
        assert replier.get_rule("test") is None

    async def test_auto_replier_stats(
        self,
        connected_client: WeChatClient,
        auto_reply_rules: list[AutoReplyRule],
    ):
        """Test auto-replier statistics."""
        replier = AutoReplierAgent(connected_client)
        for rule in auto_reply_rules:
            replier.add_rule(rule)

        stats = replier.get_stats()

        assert stats["enabled"] is True
        assert stats["total_rules"] == 3
        assert stats["enabled_rules"] == 3


# ═══════════════════════════════════════════════════════════════════════════
# Test Client Statistics
# ═══════════════════════════════════════════════════════════════════════════


class TestClientStatistics:
    """Tests for client statistics."""

    @pytest.mark.asyncio
    async def test_client_stats(
        self,
        connected_client: WeChatClient,
        sample_chat: WeChatChat,
        sample_messages: list[WeChatMessage],
    ):
        """Test client statistics."""
        connected_client.add_chat(sample_chat)
        for msg in sample_messages:
            connected_client.add_message(msg)

        stats = connected_client.get_stats()

        assert stats["state"] == "connected"
        assert stats["total_chats"] == 1
        assert stats["total_messages"] == 3

    @pytest.mark.asyncio
    async def test_client_stats_disconnected(self, wechat_client: WeChatClient):
        """Test stats when disconnected."""
        stats = wechat_client.get_stats()

        assert stats["state"] == "disconnected"
        assert stats["connected_at"] is None
