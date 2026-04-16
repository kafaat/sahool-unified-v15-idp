---
id: ai-chat-advisory
name: AI Chat Advisory
version: 1.0.0
summary: A farmer asks a question via chat; the LLM orchestrator coordinates with the advisory service to return a contextual answer.
steps:
  - id: sahool.chat.message_received
    title: Chat Message Received
    service: copilot-api
  - id: sahool.llm.query_processed
    title: LLM Query Processed
    service: llm-orchestrator-service
  - id: sahool.advisory.generated
    title: Advisory Generated
    service: advisory-service
  - id: sahool.chat.response_sent
    title: Response Sent
    service: copilot-api
---

The farmer sends a natural-language question (Arabic or English) via the mobile chat interface. Kong routes to copilot-api which forwards the query to the llm-orchestrator-service. The orchestrator performs RAG retrieval from the knowledge base, optionally consults the advisory-service for agronomic context, and returns a bilingual answer streamed back to the farmer.

```mermaid
sequenceDiagram
    participant F as Farmer (Mobile)
    participant K as Kong Gateway
    participant CP as copilot-api
    participant LLM as llm-orchestrator-service
    participant KB as Knowledge Base (Qdrant)
    participant ADV as advisory-service

    F->>K: POST /api/v1/chat/message
    K->>CP: forward chat message
    CP->>LLM: query (text, field context, language)
    LLM->>KB: RAG retrieval (semantic search)
    KB-->>LLM: relevant documents
    LLM->>ADV: request agronomic context
    ADV-->>LLM: crop/field advisory data
    LLM->>LLM: generate answer (bilingual)
    LLM-->>CP: streamed response
    CP-->>K: SSE stream
    K-->>F: advisory response (AR/EN)
```
