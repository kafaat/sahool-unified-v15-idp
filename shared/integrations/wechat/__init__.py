"""
SAHOOL WeChat Integration Module
================================
وحدة تكامل WeChat لسهول

Comprehensive WeChat integration for SAHOOL agricultural platform,
providing messaging, contact management, and AI-powered agents for
farmer communication.

Inspired by WeChat-MCP architecture for agricultural messaging.

Components:
- client: WeChatMCPClient for MCP protocol communication
- agents: 5 specialized AI agents for chat management
- models: Pydantic models for WeChat entities
- config: Configuration management

Agents:
1. ChatSummarizerAgent - Summarize chat history, extract key info
2. AutoReplierAgent - Generate contextual replies for farmers
3. MessageSearcherAgent - Search chat history with semantic understanding
4. MultiChatCheckerAgent - Monitor multiple chats, prioritize urgent items
5. ChatInsightsAgent - Analyze relationship dynamics and patterns

Example Usage:
    from shared.integrations.wechat import (
        WeChatMCPClient,
        WeChatConfig,
        ChatSummarizerAgent,
        AutoReplierAgent,
    )

    # Initialize client
    config = WeChatConfig.from_env()
    async with WeChatMCPClient(config) as client:
        # Fetch messages
        messages = await client.fetch_messages("farmer_001", limit=50)

        # Send message
        await client.send_message(
            chat_id="farmer_001",
            content="The irrigation schedule has been updated.",
            content_ar="تم تحديث جدول الري."
        )

        # Use agents
        summarizer = ChatSummarizerAgent(client)
        summary = await summarizer.summarize_chat("farmer_001", hours=24)

        auto_replier = AutoReplierAgent(client)
        reply = await auto_replier.generate_reply(
            message="متى يجب أن أسقي القمح؟",
            chat_id="farmer_001"
        )

Author: SAHOOL Platform Team
Updated: January 2026
"""

# Configuration
from .config import (
    AgentModel,
    CacheConfig,
    RateLimitConfig,
    RetryConfig,
    WeChatConfig,
    WeChatEnvironment,
    WeChatTransport,
    get_wechat_config,
    reset_config,
)

# Models
from .models import (
    # Enums
    AgentType,
    ContactType,
    MessageDirection,
    MessageType,
    MomentVisibility,
    PriorityLevel,
    SentimentType,
    TopicCategory,
    # Base models
    Attachment,
    BilingualText,
    Location,
    # Contact models
    WeChatContact,
    WeChatGroup,
    # Message models
    WeChatMessage,
    WeChatMoment,
    # Analysis models
    ChatInsight,
    ChatSummary,
    MessageAnalysis,
    MultiChatStatus,
    SearchResult,
    # Response models
    AgentResponse,
    AutoReplyResponse,
    InsightsResponse,
    SummaryResponse,
    # Request models
    FetchMessagesRequest,
    PublishMomentRequest,
    SearchMessagesRequest,
    SendMessageRequest,
)

# Client
from .client import (
    AuthenticationError,
    ConnectionError,
    MessageError,
    RateLimitError,
    WeChatMCPClient,
    WeChatMCPError,
    fetch_recent_messages,
    send_quick_message,
    wechat_client,
)

# Agents
from .agents import (
    # Base
    AgentContext,
    BaseWeChatAgent,
    # Specialized agents
    AutoReplierAgent,
    ChatInsightsAgent,
    ChatSummarizerAgent,
    MessageSearcherAgent,
    MultiChatCheckerAgent,
    # Factory
    create_wechat_agent,
)

__all__ = [
    # ===== Configuration =====
    "WeChatConfig",
    "WeChatEnvironment",
    "WeChatTransport",
    "AgentModel",
    "RateLimitConfig",
    "RetryConfig",
    "CacheConfig",
    "get_wechat_config",
    "reset_config",
    # ===== Enums =====
    "MessageType",
    "MessageDirection",
    "ContactType",
    "MomentVisibility",
    "SentimentType",
    "PriorityLevel",
    "TopicCategory",
    "AgentType",
    # ===== Base Models =====
    "BilingualText",
    "Location",
    "Attachment",
    # ===== Contact Models =====
    "WeChatContact",
    "WeChatGroup",
    # ===== Message Models =====
    "WeChatMessage",
    "WeChatMoment",
    # ===== Analysis Models =====
    "MessageAnalysis",
    "ChatSummary",
    "ChatInsight",
    "MultiChatStatus",
    "SearchResult",
    # ===== Response Models =====
    "AgentResponse",
    "AutoReplyResponse",
    "SummaryResponse",
    "InsightsResponse",
    # ===== Request Models =====
    "FetchMessagesRequest",
    "SendMessageRequest",
    "SearchMessagesRequest",
    "PublishMomentRequest",
    # ===== Client =====
    "WeChatMCPClient",
    "WeChatMCPError",
    "ConnectionError",
    "AuthenticationError",
    "RateLimitError",
    "MessageError",
    "wechat_client",
    "fetch_recent_messages",
    "send_quick_message",
    # ===== Agents =====
    "BaseWeChatAgent",
    "AgentContext",
    "ChatSummarizerAgent",
    "AutoReplierAgent",
    "MessageSearcherAgent",
    "MultiChatCheckerAgent",
    "ChatInsightsAgent",
    "create_wechat_agent",
]

__version__ = "1.0.0"
__author__ = "SAHOOL Platform Team"
