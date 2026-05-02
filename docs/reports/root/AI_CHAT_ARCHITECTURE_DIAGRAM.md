# AI Chat Integration - Architecture Diagram
# مخطط معماري: دمج AI مع الشات

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║                    SAHOOL AI Chat Integration Architecture                    ║
║                       البنية المعمارية لدمج AI مع الشات                      ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│                             👤 User Layer                                    │
│                            طبقة المستخدمين                                  │
└────────────────┬────────────────────────────────────────────────────────────┘
                 │
                 ├─► 📱 Mobile App (Flutter)
                 ├─► 🌐 Web App (Next.js)
                 └─► 💬 WhatsApp Bot
                 │
                 ▼ (Socket.IO WebSocket + REST)
┌─────────────────────────────────────────────────────────────────────────────┐
│                         💬 Chat Service Layer                                │
│                           طبقة خدمات الشات                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │ chat-service     │  │ community-chat   │  │ field-chat       │          │
│  │ Port: 8115       │  │ Port: 8097       │  │ Port: 8099       │          │
│  │ Tech: NestJS     │  │ Tech: NestJS     │  │ Tech: Python     │          │
│  │ - Socket.IO      │  │ - Community chat │  │ - Field specific │          │
│  │ - Marketplace    │  │ - Forums         │  │ - Real-time      │          │
│  └────────┬─────────┘  └──────────────────┘  └──────────────────┘          │
│           │                                                                  │
│           │ Detects AI mention: "@ai", "/ask", "سؤال"                      │
│           │                                                                  │
└───────────┼──────────────────────────────────────────────────────────────────┘
            │
            ▼ NATS Event: "sahool.chat.ai_query"
┌─────────────────────────────────────────────────────────────────────────────┐
│                      🤖 AI Chat Assistant (NEW)                              │
│                      مساعد الشات الذكي (جديد)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  📝 Lightweight Service (~2000 lines)                                        │
│  🐍 Python 3.11 + FastAPI                                                    │
│  🔌 Port: 8230                                                               │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────┐             │
│  │ 1. Parse Query                                              │             │
│  │    ├─ Language detection (AR/EN)                            │             │
│  │    ├─ Extract context (field_id, user_id)                   │             │
│  │    └─ Sanitize input (security)                             │             │
│  │                                                             │             │
│  │ 2. Check Cache (Redis)                                      │             │
│  │    ├─ Semantic similarity search                            │             │
│  │    ├─ Cache hit (70% expected) → Return                     │             │
│  │    └─ Cache miss → Continue                                 │             │
│  │                                                             │             │
│  │ 3. Route to LLM Orchestrator                                │             │
│  │    ├─ Format request                                        │             │
│  │    ├─ Call orchestrator API                                 │             │
│  │    └─ Handle timeout/retry                                  │             │
│  │                                                             │             │
│  │ 4. Format Response                                          │             │
│  │    ├─ Add metadata (confidence, agents_used)                │             │
│  │    ├─ Format for UI (markdown, emojis)                      │             │
│  │    └─ Bilingual support (AR/EN)                             │             │
│  │                                                             │             │
│  │ 5. Cache & Return                                           │             │
│  │    ├─ Store in Redis (TTL: 7 days)                          │             │
│  │    ├─ Emit NATS event                                       │             │
│  │    └─ Log metrics                                           │             │
│  └────────────────────────────────────────────────────────────┘             │
│                                                                              │
└───────────┬──────────────────────────────────────────────────────────────────┘
            │
            ▼ HTTP Call
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🧠 LLM Orchestrator Service (EXISTING)                    │
│                      خدمة تنسيق النماذج اللغوية (موجود)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Port: 8164 | Python + FastAPI                                              │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────┐             │
│  │ Intent Classification (11 types)                           │             │
│  │ ┌─────────────────────────────────────────────────────┐   │             │
│  │ │ crop_disease    │ irrigation_query │ pest_detection │   │             │
│  │ │ fertilizer      │ weather_query    │ yield_pred     │   │             │
│  │ │ field_analysis  │ terrain_analysis │ hydrology      │   │             │
│  │ │ leveling_query  │ image_analysis   │                │   │             │
│  │ └─────────────────────────────────────────────────────┘   │             │
│  │                                                             │             │
│  │ Multi-Agent Routing                                        │             │
│  │ ├─ Parallel execution                                      │             │
│  │ ├─ Response synthesis                                      │             │
│  │ └─ Action recommendations                                  │             │
│  └────────────────────────────────────────────────────────────┘             │
│                                                                              │
└───────────┬──────────────────────────────────────────────────────────────────┘
            │
      ┌─────┴──────┬──────────┬──────────┬──────────┬──────────┐
      ▼            ▼          ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        🤖 Specialized AI Agents (EXISTING)                   │
│                          وكلاء الذكاء الاصطناعي المتخصصون                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ ai-advisor   │  │ field-intel  │  │ weather      │  │ crop-intel   │   │
│  │ Port: 8112   │  │ Port: 8120   │  │ Port: 8092   │  │ Port: 8095   │   │
│  │              │  │              │  │              │  │              │   │
│  │ • Disease    │  │ • NDVI       │  │ • Forecast   │  │ • Health AI  │   │
│  │ • Treatment  │  │ • Analytics  │  │ • Alerts     │  │ • Detection  │   │
│  │ • Yield      │  │ • Rules      │  │ • Historical │  │ • Diagnosis  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ terrain-core │  │ hydrology    │  │ leveling     │  │ ai-agents    │   │
│  │ Port: 8185   │  │ Port: 8165   │  │ Port: 8170   │  │ Port: 8130   │   │
│  │              │  │              │  │              │  │              │   │
│  │ • DEM        │  │ • Drainage   │  │ • Optimize   │  │ • Custom     │   │
│  │ • Slope      │  │ • Flow       │  │ • Cost       │  │ • Registry   │   │
│  │ • Aspect     │  │ • Watershed  │  │ • Cut/Fill   │  │ • Deploy     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           💾 Data & Support Layers                           │
│                            طبقات البيانات والدعم                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ PostgreSQL   │  │ Redis        │  │ NATS         │  │ Qdrant       │   │
│  │              │  │              │  │              │  │              │   │
│  │ • Messages   │  │ • Cache      │  │ • Events     │  │ • RAG        │   │
│  │ • Users      │  │ • Sessions   │  │ • Pub/Sub    │  │ • Embeddings │   │
│  │ • Fields     │  │ • Rate limit │  │ • Streams    │  │ • Search     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │ Ollama       │  │ Claude API   │  │ Shared AI    │                      │
│  │              │  │              │  │              │                      │
│  │ • Local LLM  │  │ • Cloud LLM  │  │ • Arabic NLP │                      │
│  │ • Fast       │  │ • Powerful   │  │ • Embeddings │                      │
│  │ • Free       │  │ • Accurate   │  │ • RAG        │                      │
│  └──────────────┘  └──────────────┘  └──────────────┘                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════════╗
║                          Message Flow Example                                  ║
║                           مثال تدفق الرسائل                                   ║
╚═══════════════════════════════════════════════════════════════════════════════╝

User → Chat                → AI Assistant      → Orchestrator    → Agents
👤    💬                   🤖                   🧠                 🔧

"متى أسقي القمح؟"
│
├─► Socket.IO:send_message
│   {
│     content: "متى أسقي القمح؟",
│     type: "TEXT"
│   }
│
│   Detects: AI mention
│
├─► NATS: ai_query
│   {
│     query: "متى أسقي القمح؟",
│     language: "ar",
│     user_id: "user123",
│     field_id: "field456"
│   }
│
│                          ├─► Parse & Validate
│                          │
│                          ├─► Check Cache (Redis)
│                          │   └─► MISS
│                          │
│                          ├─► POST /orchestrate
│                          │   {
│                          │     text: "متى أسقي القمح؟",
│                          │     language: "ar",
│                          │     field_id: "field456"
│                          │   }
│                          │
│                          │                    ├─► Classify Intent
│                          │                    │   └─► "irrigation_query"
│                          │                    │
│                          │                    ├─► Route to Agents
│                          │                    │   ├─► ai-advisor
│                          │                    │   ├─► field-intel
│                          │                    │   └─► weather
│                          │                    │
│                          │                    ├─► Parallel Execute
│                          │                    │   ├─► Get irrigation schedule
│                          │                    │   ├─► Get field data (NDVI)
│                          │                    │   └─► Get weather forecast
│                          │                    │
│                          │                    └─► Synthesize Response
│                          │                        {
│                          │                          answer: "...",
│                          │                          confidence: 0.92,
│                          │                          agents_used: [...]
│                          │                        }
│                          │
│                          ├─► Format Response (AR)
│                          │   ├─► Add emojis
│                          │   ├─► Structure content
│                          │   └─► Add metadata
│                          │
│                          ├─► Cache (Redis, 7 days)
│                          │
│                          └─► NATS: ai_response
│                              {
│                                answer: "الري الأمثل...",
│                                confidence: 92,
│                                agents: ["ai-advisor"],
│                                cached: false
│                              }
│
├─► Socket.IO:message_received
│   {
│     type: "AI_RESPONSE",
│     content: "الري الأمثل للقمح...",
│     metadata: {
│       confidence: 92,
│       agents_used: ["ai-advisor"],
│       processing_time: 1200
│     }
│   }
│
└─► Display to User
    ┌────────────────────────────┐
    │ 🤖 AI Assistant:           │
    │                            │
    │ الري الأمثل للقمح:         │
    │                            │
    │ ⏰ التوقيت:                │
    │ • كل 7-10 أيام            │
    │ • صباحاً (6-8 ص)          │
    │                            │
    │ 💧 الكمية: 50-60 ملم       │
    │                            │
    │ 👍 مفيد؟ 👎               │
    └────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════════╗
║                        Performance Optimizations                               ║
║                          تحسينات الأداء                                       ║
╚═══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│                         🚀 Caching Strategy                                  │
│                         استراتيجية التخزين المؤقت                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Layer 1: Exact Match (Redis)                                               │
│  ┌──────────────────────────────────────────┐                               │
│  │ Key: hash(query + language + field_id)   │                               │
│  │ TTL: 7 days                               │                               │
│  │ Hit Rate: 30%                             │                               │
│  │ Speed: <10ms                              │                               │
│  └──────────────────────────────────────────┘                               │
│                                                                              │
│  Layer 2: Semantic Similarity (Embeddings)                                  │
│  ┌──────────────────────────────────────────┐                               │
│  │ Similarity threshold: >0.9                │                               │
│  │ TTL: 7 days                               │                               │
│  │ Hit Rate: 40%                             │                               │
│  │ Speed: <100ms                             │                               │
│  └──────────────────────────────────────────┘                               │
│                                                                              │
│  Layer 3: LLM Call (Ollama/Claude)                                          │
│  ┌──────────────────────────────────────────┐                               │
│  │ Cache Miss: Call LLM                      │                               │
│  │ Hit Rate: 30%                             │                               │
│  │ Speed: 1-3s                               │                               │
│  └──────────────────────────────────────────┘                               │
│                                                                              │
│  Overall Cache Hit Rate: 70%                                                │
│  Average Response Time: <500ms (with cache), <2s (without)                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        ⚡ Cost Optimization                                  │
│                        تحسين التكلفة                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Simple Queries → Ollama (Local, Free)                                      │
│  ├─ "ما هو موسم الري؟"                                                     │
│  ├─ "متى يزرع القمح؟"                                                      │
│  └─ Cost: $0                                                                │
│                                                                              │
│  Complex Queries → Claude API (Cloud, Paid)                                 │
│  ├─ "حلل صحة المحصول من الصورة"                                            │
│  ├─ "خطة كاملة لموسم القمح"                                                │
│  └─ Cost: $0.015 per query (avg)                                           │
│                                                                              │
│  Estimated Monthly Cost:                                                    │
│  - 10,000 queries/month                                                     │
│  - 70% cache hit → 3,000 LLM calls                                          │
│  - 60% local (Ollama) → 1,800 free                                          │
│  - 40% cloud (Claude) → 1,200 × $0.015 = $18                                │
│                                                                              │
│  Total: $18-45/month (with optimizations)                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════════╗
║                              END OF DIAGRAM                                    ║
║                             نهاية المخطط                                      ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```
