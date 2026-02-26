# shared/integrations - External Integrations

حزمة تكاملات سهول

Third-party integrations for the SAHOOL agricultural platform. Currently provides a comprehensive WeChat messaging integration for farmer communication, with MCP protocol support and five specialized AI agents for chat management.

## File Structure

```
shared/integrations/
├── __init__.py
└── wechat/
    ├── __init__.py    # Full public API, re-exports all submodules
    ├── agents.py      # 5 AI chat agent implementations
    ├── client.py      # WeChatMCPClient (async HTTP, context manager)
    ├── config.py      # WeChatConfig, rate limiting, retry, cache settings
    └── models.py      # Pydantic models for messages, contacts, analysis
```

## WeChat Integration

### Configuration

```python
from shared.integrations.wechat import WeChatConfig, WeChatEnvironment, WeChatTransport

config = WeChatConfig.from_env()  # Reads from environment variables
# or:
config = WeChatConfig(
    environment=WeChatEnvironment.PRODUCTION,
    transport=WeChatTransport.STDIO,
    agent_model="claude-3-5-sonnet-20241022",
)
```

**`WeChatConfig`** fields: `environment` (development/staging/production), `transport` (stdio/sse/http), `agent_model`, plus nested `RateLimitConfig`, `RetryConfig`, `CacheConfig`.

### Client

**`WeChatMCPClient`** - Async context manager for MCP protocol communication:
- `fetch_messages(chat_id, limit)` - Retrieve recent messages
- `send_message(chat_id, content, content_ar)` - Send bilingual message
- Helper functions: `fetch_recent_messages()`, `send_quick_message()`, `wechat_client()` (async context manager factory)

Exceptions: `WeChatMCPError`, `ConnectionError`, `AuthenticationError`, `RateLimitError`, `MessageError`

### Models

| Category | Models |
|----------|--------|
| Enums | `MessageType`, `MessageDirection`, `ContactType`, `SentimentType`, `PriorityLevel`, `TopicCategory`, `AgentType` |
| Entities | `WeChatContact`, `WeChatGroup`, `WeChatMessage`, `WeChatMoment` |
| Analysis | `MessageAnalysis`, `ChatSummary`, `ChatInsight`, `MultiChatStatus`, `SearchResult` |
| Requests | `FetchMessagesRequest`, `SendMessageRequest`, `SearchMessagesRequest`, `PublishMomentRequest` |
| Responses | `AgentResponse`, `AutoReplyResponse`, `SummaryResponse`, `InsightsResponse` |
| Shared | `BilingualText`, `Location`, `Attachment` |

### AI Agents (5 Specialized)

All agents inherit from `BaseWeChatAgent` and accept an `AgentContext`.

| Agent | Class | Purpose |
|-------|-------|---------|
| Chat Summarizer | `ChatSummarizerAgent` | Summarize chat history, extract key agricultural info |
| Auto Replier | `AutoReplierAgent` | Generate contextual replies for farmer messages |
| Message Searcher | `MessageSearcherAgent` | Semantic search across chat history |
| Multi-Chat Checker | `MultiChatCheckerAgent` | Monitor multiple chats, surface urgent items |
| Chat Insights | `ChatInsightsAgent` | Analyze relationship dynamics and communication patterns |

**Factory function:** `create_wechat_agent(agent_type, client)` - Instantiate agent by `AgentType` enum.

## Usage Example

```python
from shared.integrations.wechat import (
    WeChatMCPClient, WeChatConfig,
    ChatSummarizerAgent, AutoReplierAgent,
)

config = WeChatConfig.from_env()

async with WeChatMCPClient(config) as client:
    # Fetch last 50 messages from a farmer chat
    messages = await client.fetch_messages("farmer_001", limit=50)

    # Send bilingual update
    await client.send_message(
        chat_id="farmer_001",
        content="Your irrigation schedule has been updated for tomorrow.",
        content_ar="تم تحديث جدول الري الخاص بك لغد."
    )

    # Summarize the last 24 hours of chat
    summarizer = ChatSummarizerAgent(client)
    summary = await summarizer.summarize_chat("farmer_001", hours=24)

    # Auto-reply to incoming message
    replier = AutoReplierAgent(client)
    reply = await replier.generate_reply(
        message="متى يجب أن أسقي القمح؟",
        chat_id="farmer_001"
    )
```

## Environment Variables

```bash
WECHAT_ENVIRONMENT=production        # development | staging | production
WECHAT_TRANSPORT=stdio               # stdio | sse | http
WECHAT_AGENT_MODEL=claude-3-5-sonnet-20241022
WECHAT_MCP_SERVER_URL=http://wechat-mcp:8000
```

## Notes

- The WeChat integration is exposed via the `wechat-service` microservice (port 8133).
- `BilingualText` is used throughout to ensure all user-facing content is available in both Arabic and English.
- The `whatsapp-bot-service` (port 8240) follows a similar pattern for WhatsApp integration.
- Adding new third-party integrations: create a new subdirectory under `shared/integrations/`, export from `__init__.py`.
