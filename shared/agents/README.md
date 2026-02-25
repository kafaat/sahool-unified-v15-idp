# shared/agents - CrewAI Multi-Agent Orchestration

وحدة تنسيق الوكلاء المتعددين باستخدام CrewAI

## Overview

Role-based multi-agent orchestration for agricultural advisory using CrewAI. Eight domain-specialist agents (crop advisor, irrigation expert, disease diagnostician, pest controller, soil analyst, yield predictor, market analyst, coordinator) collaborate to answer farmer queries in Arabic and English. Query routing is automatic based on keyword detection. Falls back to rule-based responses when CrewAI is not installed.

## File Structure

```
shared/agents/
├── __init__.py              # Exports: CrewAIOrchestrator, AgentRole, AgriculturalCrew, TaskResult
└── crewai_orchestrator.py   # Agent configs, crew execution, routing, fallback logic
```

## Key Components

### `AgentRole` (StrEnum)

Eight pre-defined agricultural specialist roles:

| Role | Goal (EN) | Goal (AR) |
|---|---|---|
| `CROP_ADVISOR` | Comprehensive crop management advice | نصائح شاملة لإدارة المحاصيل |
| `IRRIGATION_EXPERT` | Optimize irrigation and water efficiency | تحسين الري وكفاءة المياه |
| `DISEASE_DIAGNOSTICIAN` | Diagnose crop diseases | تشخيص أمراض المحاصيل |
| `PEST_CONTROLLER` | Identify pests and IPM solutions | تحديد الآفات وحلول المكافحة المتكاملة |
| `SOIL_ANALYST` | Analyze soil and recommend amendments | تحليل التربة والتوصية بالتعديلات |
| `YIELD_PREDICTOR` | Predict crop yields | التنبؤ بإنتاجية المحاصيل |
| `MARKET_ANALYST` | Market prices and selling strategy | أسعار السوق واستراتيجيات البيع |
| `COORDINATOR` | Coordinate between specialists | تنسيق بين المتخصصين |

### `AGRICULTURAL_AGENTS`

Pre-built `AgentConfig` for each role containing bilingual goal, backstory, and tools list (e.g., `weather_api`, `soil_moisture_sensor`, `image_classifier`, `pest_identifier`). The `COORDINATOR` role has `allow_delegation=True`.

### `AgriculturalCrew`

Wraps a subset of agents into an executable CrewAI crew. Automatic keyword-based routing selects relevant agents from the query before execution:

| Keywords (EN / AR) | Agent Selected |
|---|---|
| disease, مرض, اصفرار, rust, blight | `DISEASE_DIAGNOSTICIAN` |
| pest, آفة, سوسة, حشرة, weevil, insect | `PEST_CONTROLLER` |
| water, irrigation, ري, ماء, سقي, رطوبة | `IRRIGATION_EXPERT` |
| soil, fertilizer, تربة, سماد, nitrogen | `SOIL_ANALYST` |
| yield, harvest, إنتاج, محصول, حصاد | `YIELD_PREDICTOR` |
| price, market, سعر, سوق, sell, بيع | `MARKET_ANALYST` |
| (no match) | `CROP_ADVISOR` (default) |

### `CrewAIOrchestrator`

Top-level entry point. Manages named crews and a default crew (`COORDINATOR`, `CROP_ADVISOR`, `IRRIGATION_EXPERT`, `DISEASE_DIAGNOSTICIAN`). Exposes `query()`, `create_crew()`, and `get_available_agents()`.

### Data Classes

| Class | Key Fields |
|---|---|
| `AgentConfig` | role, goal, goal_ar, backstory, backstory_ar, tools, allow_delegation |
| `TaskResult` | agent_role, result, result_ar, confidence (0-1), execution_time_ms |
| `CrewResult` | query, final_answer, final_answer_ar, total_time_ms, agents_used |

## Usage Example

```python
from shared.agents import CrewAIOrchestrator, AgentRole, AgriculturalCrew

orchestrator = CrewAIOrchestrator()
await orchestrator.initialize()

# Simple query - agent selected automatically from keywords
result = await orchestrator.query("متى أسقي القمح؟")
print(result.final_answer)       # English answer
print(result.final_answer_ar)    # Arabic answer
print(result.agents_used)        # [AgentRole.IRRIGATION_EXPERT]
print(f"Time: {result.total_time_ms:.0f}ms")

# Query with field context
result = await orchestrator.query(
    "القمح يعاني من اصفرار الأوراق",
    context={"field_id": "FIELD-003", "crop_stage": "tillering", "ndvi": 0.52},
)

# Create a specialized crew for pest response
pest_crew = orchestrator.create_crew(
    name="pest_response",
    roles=[AgentRole.PEST_CONTROLLER, AgentRole.DISEASE_DIAGNOSTICIAN],
    llm_provider="ollama",
)
result = await orchestrator.query(
    "Red palm weevil detected in grove Block-B",
    crew_name="pest_response",
)

# List all available agents
agents = orchestrator.get_available_agents()
for agent in agents:
    print(f"{agent['role']}: {agent['goal_ar']}")
```

## Fallback Behavior

When `crewai` is not installed, `AgriculturalCrew._fallback_execute()` generates rule-based bilingual responses based on the detected intent. Fallback results carry `metadata={"fallback": True}` and a confidence of 0.7.

## Dependencies

```
crewai       # Optional - install with: pip install crewai
structlog    # Structured logging
```

LLM backend defaults to `ollama` with model `llama3.2`. Override per crew:

```python
crew = orchestrator.create_crew("advisory", roles, llm_provider="ollama", model="llama3.2")
```

## Integration

This module is exposed via the LLM Orchestrator Service (port 8164):
- `POST /api/v1/integrations/crew/query` - submit a query
- `GET /api/v1/integrations/crew/agents` - list available agents
