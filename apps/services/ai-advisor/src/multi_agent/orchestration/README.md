# Master Advisor - Central Orchestrator
# المستشار الرئيسي - المنسق المركزي

## Overview | نظرة عامة

The **MasterAdvisor** is the central orchestrator for the SAHOOL multi-agent agricultural advisory system. It intelligently analyzes farmer queries, routes them to appropriate specialized agents, executes them in the optimal mode (parallel, sequential, or council), and aggregates responses into comprehensive, actionable advice.

**المستشار الرئيسي** هو المنسق المركزي لنظام SAHOOL الاستشاري الزراعي متعدد الوكلاء. يحلل بذكاء استفسارات المزارعين، يوجهها للوكلاء المتخصصين المناسبين، ينفذها في الوضع الأمثل (متوازي، متتابع، أو مجلس)، ويجمع الاستجابات في نصائح شاملة وقابلة للتنفيذ.

---

## Architecture | البنية المعمارية

### Core Components | المكونات الأساسية

```
MasterAdvisor
├── AgentRegistry          # Manages available agents and capabilities
├── ContextStore          # Stores conversation history and context
├── NATSBridge           # Messaging infrastructure (future)
└── Claude LLM           # For query analysis and response synthesis
```

### Execution Modes | أوضاع التنفيذ

1. **PARALLEL** (متوازي): Multiple agents work simultaneously on independent aspects
2. **SEQUENTIAL** (متتابع): Agents execute in order, building on each other's results
3. **COUNCIL** (مجلس): Agents deliberate together for critical decisions requiring consensus
4. **SINGLE_AGENT** (وكيل واحد): Single specialized agent handles the query

---

## Query Types | أنواع الاستفسارات

The system recognizes and handles 12 distinct query types:

| Query Type | Description (EN) | الوصف (AR) | Typical Agents |
|------------|------------------|------------|----------------|
| `DIAGNOSIS` | Crop disease diagnosis | تشخيص أمراض المحاصيل | disease_expert |
| `TREATMENT` | Treatment recommendations | توصيات العلاج | disease_expert |
| `IRRIGATION` | Water management | إدارة المياه | irrigation_advisor |
| `FERTILIZATION` | Nutrient management | إدارة المغذيات | irrigation_advisor, field_analyst |
| `PEST_MANAGEMENT` | Pest control | مكافحة الآفات | disease_expert |
| `HARVEST_PLANNING` | Harvest timing | توقيت الحصاد | yield_predictor |
| `EMERGENCY` | Urgent issues | قضايا عاجلة | Multiple (council mode) |
| `ECOLOGICAL_TRANSITION` | Sustainable farming | الزراعة المستدامة | ecological_expert |
| `MARKET_ANALYSIS` | Market insights | تحليل السوق | Multiple |
| `FIELD_ANALYSIS` | Field assessment | تقييم الحقل | field_analyst |
| `YIELD_PREDICTION` | Yield forecasting | التنبؤ بالمحصول | yield_predictor |
| `GENERAL_ADVISORY` | General questions | أسئلة عامة | Multiple |

---

## Usage | الاستخدام

### 1. Initialize Components | تهيئة المكونات

```python
from multi_agent.orchestration import (
    MasterAdvisor,
    AgentRegistry,
    ContextStore,
    NATSBridge,
    FarmerQuery,
    QueryType
)
from agents import (
    FieldAnalystAgent,
    DiseaseExpertAgent,
    IrrigationAdvisorAgent,
    YieldPredictorAgent,
    EcologicalExpertAgent
)

# Create agent registry
registry = AgentRegistry()

# Register agents with their capabilities
registry.register_agent(
    "disease_expert",
    DiseaseExpertAgent(...),
    [QueryType.DIAGNOSIS, QueryType.TREATMENT, QueryType.PEST_MANAGEMENT]
)

registry.register_agent(
    "irrigation_advisor",
    IrrigationAdvisorAgent(...),
    [QueryType.IRRIGATION, QueryType.FERTILIZATION]
)

# ... register other agents

# Initialize support components
context_store = ContextStore()
nats_bridge = NATSBridge("nats://nats:4222")

# Create MasterAdvisor
master_advisor = MasterAdvisor(
    agent_registry=registry,
    context_store=context_store,
    nats_bridge=nats_bridge,
    anthropic_api_key="your-api-key",
    model="claude-3-5-sonnet-20241022"
)
```

### 2. Process Queries | معالجة الاستفسارات

```python
# Create a farmer query
query = FarmerQuery(
    query="أوراق الطماطم تتحول إلى اللون الأصفر. ما المشكلة؟",
    farmer_id="farmer_123",
    field_id="field_456",
    crop_type="tomato",
    language="ar",
    priority="normal"
)

# Process through MasterAdvisor
response = await master_advisor.process_query(
    query=query,
    session_id="session_1"  # Optional: for context tracking
)

# Access results
print(f"Answer: {response.answer}")
print(f"Query Type: {response.query_type}")
print(f"Agents: {response.agents_consulted}")
print(f"Confidence: {response.confidence}")
print(f"Recommendations: {response.recommendations}")
```

### 3. Handle Different Query Types | معالجة أنواع مختلفة من الاستفسارات

#### Emergency Queries (Council Mode) | استفسارات طارئة (وضع المجلس)

```python
emergency_query = FarmerQuery(
    query="المحصول يموت بسرعة! ماذا أفعل؟",
    crop_type="wheat",
    language="ar",
    priority="emergency"  # Triggers council mode
)

response = await master_advisor.process_query(emergency_query)
# Multiple agents will deliberate and reach consensus
```

#### Complex Multi-Agent Queries | استفسارات معقدة متعددة الوكلاء

```python
complex_query = FarmerQuery(
    query="How do I maximize corn yield with limited water?",
    crop_type="corn",
    language="en",
    context={
        "field_size_hectares": 10,
        "water_availability": "limited",
        "soil_type": "sandy"
    }
)

response = await master_advisor.process_query(complex_query)
# Parallel execution: irrigation_advisor, yield_predictor, field_analyst
```

#### Simple Single-Agent Queries | استفسارات بسيطة لوكيل واحد

```python
simple_query = FarmerQuery(
    query="What is the ideal irrigation schedule for wheat?",
    crop_type="wheat",
    language="en"
)

response = await master_advisor.process_query(simple_query)
# Single agent: irrigation_advisor
```

---

## Response Structure | هيكل الاستجابة

### AdvisoryResponse

```python
@dataclass
class AdvisoryResponse:
    query: str                      # Original query
    answer: str                     # Comprehensive answer
    query_type: QueryType          # Detected query type
    agents_consulted: List[str]    # Agents that participated
    execution_mode: ExecutionMode  # How it was executed
    confidence: float              # Confidence score (0-1)
    recommendations: List[str]     # Actionable recommendations
    warnings: List[str]            # Important warnings
    next_steps: List[str]          # Suggested next actions
    metadata: Dict[str, Any]       # Additional metadata
    language: str                  # Response language
    timestamp: datetime            # When processed
```

---

## Query Analysis | تحليل الاستفسار

The MasterAdvisor uses Claude to analyze queries and determine:

1. **Query Type**: What kind of agricultural question is this?
2. **Required Agents**: Which specialized agents are needed?
3. **Execution Mode**: Parallel, sequential, council, or single?
4. **Consensus Need**: Does this require expert agreement?
5. **Complexity**: Low, medium, or high complexity?

### Analysis Process | عملية التحليل

```python
analysis = await master_advisor.analyze_query(query)

# Results
print(f"Type: {analysis.query_type}")
print(f"Agents: {analysis.required_agents}")
print(f"Mode: {analysis.execution_mode}")
print(f"Needs Consensus: {analysis.needs_consensus}")
print(f"Complexity: {analysis.estimated_complexity}")
print(f"Reasoning: {analysis.reasoning}")
```

---

## Execution Modes in Detail | أوضاع التنفيذ بالتفصيل

### Parallel Execution | التنفيذ المتوازي

**When used**: Agents can work independently on different aspects

```python
# Example: Comprehensive field analysis
# - field_analyst: Satellite and field health
# - disease_expert: Disease risk assessment
# - irrigation_advisor: Water management
# All run simultaneously

agents = ["field_analyst", "disease_expert", "irrigation_advisor"]
responses = await master_advisor.execute_parallel(agents, query, context)
```

**Benefits**:
- Fastest execution
- Multiple perspectives
- Independent analysis

### Sequential Execution | التنفيذ المتتابع

**When used**: Agents need to build on each other's results

```python
# Example: Progressive diagnosis
# 1. field_analyst: Analyze field conditions
# 2. disease_expert: Diagnose based on field analysis
# 3. irrigation_advisor: Recommend treatment + irrigation

agents = ["field_analyst", "disease_expert", "irrigation_advisor"]
responses = await master_advisor.execute_sequential(agents, query, context)
```

**Benefits**:
- Coherent analysis chain
- Each agent has full context from previous agents
- Builds comprehensive solution

### Council Execution | التنفيذ في وضع المجلس

**When used**: Critical decisions requiring expert consensus

```python
# Example: Emergency crop failure
# 1. All experts analyze independently
# 2. Check for consensus
# 3. If disagreement, run deliberation round
# 4. Reach final consensus

agents = ["disease_expert", "irrigation_advisor", "field_analyst"]
responses = await master_advisor.execute_council(agents, query, context)
```

**Phases**:
1. **Independent Analysis**: All agents analyze in parallel
2. **Consensus Check**: Compare opinions for agreement
3. **Deliberation** (if needed): Agents discuss disagreements
4. **Final Decision**: Consensus recommendation

---

## Context Management | إدارة السياق

### Session Context | سياق الجلسة

The ContextStore maintains conversation history:

```python
# Store context
context_store.store_context(
    session_id="session_123",
    query="Previous query",
    response=response_object
)

# Retrieve context
previous_context = context_store.get_context("session_123")

# Clear context
context_store.clear_context("session_123")
```

### Context in Queries | السياق في الاستفسارات

```python
query = FarmerQuery(
    query="Should I harvest now?",
    crop_type="wheat",
    context={
        "field_size_hectares": 50,
        "growth_stage": "maturity",
        "last_irrigation": "7 days ago",
        "weather_forecast": "rain expected in 3 days",
        "soil_moisture": 25
    }
)
```

---

## Agent Registry | سجل الوكلاء

### Register Agents | تسجيل الوكلاء

```python
registry = AgentRegistry()

# Register with capabilities
registry.register_agent(
    name="disease_expert",
    agent=disease_expert_instance,
    capabilities=[
        QueryType.DIAGNOSIS,
        QueryType.TREATMENT,
        QueryType.PEST_MANAGEMENT
    ]
)
```

### Query Registry | الاستعلام عن السجل

```python
# Get agent by name
agent = registry.get_agent("disease_expert")

# Get agents for query type
agents = registry.get_agents_for_query_type(QueryType.IRRIGATION)

# List all agents
all_agents = registry.list_agents()
```

---

## Error Handling | معالجة الأخطاء

The MasterAdvisor handles errors gracefully:

```python
try:
    response = await master_advisor.process_query(query)
except Exception as e:
    # Returns error response in appropriate language
    response.answer  # Contains error message
    response.confidence  # 0.0
    response.metadata["error"]  # Error details
```

### Bilingual Error Messages | رسائل الخطأ ثنائية اللغة

```python
# If query.language == "ar"
"عذراً، حدث خطأ أثناء معالجة استفسارك"

# If query.language == "en"
"Sorry, an error occurred while processing your query"
```

---

## Performance Considerations | اعتبارات الأداء

### Execution Times | أوقات التنفيذ

- **Single Agent**: ~2-5 seconds
- **Parallel (3 agents)**: ~3-7 seconds
- **Sequential (3 agents)**: ~6-15 seconds
- **Council (with deliberation)**: ~10-20 seconds

### Optimization Tips | نصائح التحسين

1. **Use Parallel Mode** when possible for faster response
2. **Cache RAG results** to reduce retrieval time
3. **Limit agent count** to essential agents only
4. **Set appropriate timeouts** for agent execution
5. **Use session context** to avoid redundant analysis

---

## Integration with NATS | التكامل مع NATS

### Future Implementation | التنفيذ المستقبلي

```python
# Connect to NATS
nats_bridge = NATSBridge("nats://nats:4222")
await nats_bridge.connect()

# Publish events
await nats_bridge.publish(
    subject="sahool.advisory.completed",
    message={
        "query": query.query,
        "response": response.answer,
        "farmer_id": query.farmer_id
    }
)

# Subscribe to events
await nats_bridge.subscribe(
    subject="sahool.advisory.request",
    callback=handle_advisory_request
)
```

---

## Testing | الاختبار

### Run Example

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/ai-advisor/src/multi_agent/orchestration
python3 example_usage.py
```

### Unit Tests

```python
import pytest
from master_advisor import MasterAdvisor, AgentRegistry, FarmerQuery

@pytest.mark.asyncio
async def test_query_analysis():
    registry = AgentRegistry()
    # ... setup agents

    advisor = MasterAdvisor(agent_registry=registry)

    query = FarmerQuery(
        query="Tomato leaves are yellow",
        crop_type="tomato",
        language="en"
    )

    analysis = await advisor.analyze_query(query)

    assert analysis.query_type == QueryType.DIAGNOSIS
    assert "disease_expert" in analysis.required_agents
```

---

## API Integration | التكامل مع واجهة برمجة التطبيقات

### FastAPI Endpoint

```python
from fastapi import FastAPI
from multi_agent.orchestration import MasterAdvisor, FarmerQuery

app = FastAPI()
master_advisor = None  # Initialize on startup

@app.post("/api/v1/advisory")
async def get_advisory(request: FarmerQuery):
    response = await master_advisor.process_query(
        query=request,
        session_id=request.farmer_id
    )
    return response
```

---

## Monitoring and Logging | المراقبة والتسجيل

The MasterAdvisor uses structured logging:

```python
import structlog

# Logs include:
# - query_analyzed: Analysis results
# - executing_parallel/sequential/council: Execution mode
# - query_processed_successfully: Completion
# - query_processing_failed: Errors
```

### Log Example

```json
{
  "event": "query_processed_successfully",
  "query_type": "diagnosis",
  "agents_consulted": 2,
  "execution_time": 4.23,
  "timestamp": "2025-12-29T10:30:00Z"
}
```

---

## Best Practices | أفضل الممارسات

1. **Always provide crop_type** for better routing
2. **Set appropriate priority** (emergency queries use council mode)
3. **Use session_id** for conversational context
4. **Include relevant context** (soil, weather, field data)
5. **Specify language** for better responses
6. **Handle errors gracefully** in production
7. **Monitor execution times** and optimize agent selection
8. **Review confidence scores** before acting on advice

---

## Troubleshooting | استكشاف الأخطاء

### Common Issues | المشاكل الشائعة

**Issue**: Query takes too long
**Solution**: Check if council mode is being triggered unnecessarily. Use parallel mode when possible.

**Issue**: Low confidence scores
**Solution**: Ensure agents have access to RAG retriever and relevant tools.

**Issue**: Agent not found
**Solution**: Verify agent is registered in AgentRegistry with correct name.

**Issue**: Response synthesis fails
**Solution**: Check Claude API key is valid and has sufficient credits.

---

## Future Enhancements | التحسينات المستقبلية

- [ ] Full NATS integration for distributed messaging
- [ ] Agent performance metrics and optimization
- [ ] Dynamic agent loading based on query complexity
- [ ] Multi-language support beyond Arabic/English
- [ ] Real-time streaming responses
- [ ] Agent voting and confidence weighting
- [ ] Persistent context storage (Redis/PostgreSQL)
- [ ] GraphQL API support

---

## Support | الدعم

For questions or issues:
- **Email**: support@sahool.ag
- **Docs**: https://docs.sahool.ag
- **GitHub**: https://github.com/sahool/multi-agent-system

---

## License | الترخيص

Copyright © 2025 SAHOOL Agricultural Platform. All rights reserved.
