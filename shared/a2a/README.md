# Agent-to-Agent (A2A) Protocol Implementation

## Overview

This package provides a production-ready implementation of the **Linux Foundation Agent-to-Agent (A2A) Protocol** for SAHOOL. The A2A protocol enables standardized communication between AI agents, allowing them to discover each other, exchange tasks, and collaborate on complex workflows.

## Features

- ✅ **Full A2A Protocol Compliance** - Implements Linux Foundation A2A specification
- ✅ **Agent Discovery** - Standard `.well-known/agent-card.json` endpoint
- ✅ **Task Management** - Complete task lifecycle with state tracking
- ✅ **Streaming Support** - Real-time task progress via WebSocket
- ✅ **Conversation Tracking** - Multi-turn conversations with context management
- ✅ **Priority Queuing** - Task prioritization and queue management
- ✅ **Error Handling** - Comprehensive error messages and recovery
- ✅ **Production Ready** - Logging, metrics, and health checks

## Architecture

```
shared/a2a/
├── __init__.py          # Package exports
├── protocol.py          # Message types and state management
├── agent.py             # Base A2A agent class
├── client.py            # Client for discovering and communicating with agents
├── server.py            # FastAPI router with WebSocket support
└── README.md            # This file
```

## Core Components

### 1. Protocol Messages (`protocol.py`)

Defines standard A2A message types:

- **TaskMessage** - Task request from one agent to another
- **TaskResultMessage** - Task execution results
- **ErrorMessage** - Error notifications
- **HeartbeatMessage** - Connection monitoring
- **CancelMessage** - Task cancellation requests

```python
from a2a.protocol import TaskMessage, TaskState

# Create a task
task = TaskMessage(
    sender_agent_id="agent-1",
    receiver_agent_id="agent-2",
    task_type="crop-disease-diagnosis",
    task_description="Diagnose tomato plant disease",
    parameters={
        "crop_type": "tomato",
        "symptoms": {"leaf_condition": "yellow spots"}
    },
    priority=8
)
```

### 2. A2A Agent (`agent.py`)

Base class for creating A2A-compatible agents:

```python
from a2a.agent import A2AAgent, AgentCapability

class MyAgent(A2AAgent):
    def get_capabilities(self):
        return [
            AgentCapability(
                capability_id="my-capability",
                name="My Capability",
                description="What my agent can do",
                input_schema={"type": "object", "properties": {...}},
                output_schema={"type": "object", "properties": {...}},
                tags=["agriculture", "advisory"]
            )
        ]

# Initialize agent
agent = MyAgent(
    agent_id="my-agent",
    name="My Agricultural Agent",
    version="1.0.0",
    description="Provides agricultural advice",
    provider="SAHOOL",
    task_endpoint="http://localhost:8000/a2a/tasks"
)

# Register task handlers
async def handle_my_task(task: TaskMessage) -> dict:
    # Process task
    return {"result": "success"}

agent.register_task_handler("my-capability", handle_my_task)
```

### 3. A2A Client (`client.py`)

Client for discovering and communicating with other agents:

```python
from a2a.client import A2AClient, AgentDiscovery

# Discover agents
discovery = AgentDiscovery()
agent_card = await discovery.discover_agent("http://localhost:8000")

# Send task
client = A2AClient(sender_agent_id="my-client")
result = await client.send_task(
    agent_card=agent_card,
    task_type="crop-disease-diagnosis",
    task_description="Diagnose disease",
    parameters={"crop_type": "wheat", "symptoms": {...}}
)

# Stream task with progress updates
async for update in client.stream_task(
    agent_card=agent_card,
    task_type="field-analysis",
    task_description="Analyze field",
    parameters={"field_id": "field-123"}
):
    print(f"Progress: {update.progress}")
    if update.is_final:
        print(f"Result: {update.result}")
```

### 4. A2A Server (`server.py`)

FastAPI router for exposing A2A endpoints:

```python
from fastapi import FastAPI
from a2a.server import create_a2a_router

app = FastAPI()

# Add A2A routes
a2a_router = create_a2a_router(agent, prefix="/a2a")
app.include_router(a2a_router)
```

This creates the following endpoints:

- `GET /a2a/.well-known/agent-card.json` - Agent discovery
- `POST /a2a/tasks` - Submit task
- `GET /a2a/tasks/{task_id}/status` - Query task status
- `DELETE /a2a/tasks/{task_id}` - Cancel task
- `GET /a2a/stats` - Agent statistics
- `GET /a2a/conversations/{id}` - Conversation history
- `GET /a2a/health` - Health check
- `WS /a2a/ws/{client_id}` - WebSocket for streaming

## Usage Examples

### Example 1: Basic Task Submission

```python
import asyncio
from a2a.client import A2AClient, AgentDiscovery

async def main():
    # Discover agent
    discovery = AgentDiscovery()
    agent_card = await discovery.discover_agent("http://localhost:8001")

    # Create client
    client = A2AClient(sender_agent_id="my-app")

    # Send task
    result = await client.send_task(
        agent_card=agent_card,
        task_type="irrigation-optimization",
        task_description="Get irrigation recommendations",
        parameters={
            "crop_type": "corn",
            "growth_stage": "vegetative",
            "soil_data": {"moisture_level": 0.3}
        }
    )

    print(f"Task completed: {result.state}")
    print(f"Result: {result.result}")

asyncio.run(main())
```

### Example 2: Streaming Task with Progress

```python
async def stream_field_analysis():
    discovery = AgentDiscovery()
    agent_card = await discovery.discover_agent("http://localhost:8001")

    client = A2AClient(sender_agent_id="my-app")

    async for update in client.stream_task(
        agent_card=agent_card,
        task_type="field-analysis",
        task_description="Comprehensive field analysis",
        parameters={
            "field_id": "field-42",
            "crop_type": "wheat",
            "include_disease_check": True,
            "include_yield_prediction": True
        }
    ):
        if update.is_final:
            print(f"✅ Analysis complete: {update.result}")
        else:
            print(f"⏳ Progress: {update.progress * 100:.1f}%")
            if update.partial_result:
                print(f"   Partial: {update.partial_result}")

asyncio.run(stream_field_analysis())
```

### Example 3: Multi-Agent Coordination

```python
async def coordinate_multiple_agents():
    discovery = AgentDiscovery()

    # Discover multiple agents
    agent_urls = [
        "http://localhost:8001",  # AI Advisor
        "http://localhost:8002",  # Weather Service
        "http://localhost:8003",  # Satellite Analysis
    ]

    agents = await discovery.discover_multiple(agent_urls)

    # Find agents by capability
    disease_experts = discovery.get_agents_by_capability("crop-disease-diagnosis")

    # Send tasks to multiple agents in parallel
    client = A2AClient(sender_agent_id="orchestrator")

    tasks = []
    for agent_card in agents:
        for capability in agent_card.capabilities:
            tasks.append(client.send_task(
                agent_card=agent_card,
                task_type=capability.capability_id,
                task_description=f"Execute {capability.name}",
                parameters={"field_id": "field-123"}
            ))

    results = await asyncio.gather(*tasks)

    for result in results:
        print(f"Agent result: {result.state} - {result.result}")

asyncio.run(coordinate_multiple_agents())
```

## Integration with AI Advisor

The AI Advisor service has been integrated with A2A protocol. See `/apps/services/ai-advisor/src/a2a_adapter.py` for the implementation.

### Accessing AI Advisor via A2A

```python
from a2a.client import AgentDiscovery, A2AClient

# Discover AI Advisor
discovery = AgentDiscovery()
advisor = await discovery.discover_agent("http://localhost:8001")

# View capabilities
for capability in advisor.capabilities:
    print(f"- {capability.name}: {capability.description}")

# Use disease diagnosis capability
client = A2AClient(sender_agent_id="farmer-app")
result = await client.send_task(
    agent_card=advisor,
    task_type="crop-disease-diagnosis",
    task_description="Diagnose wheat disease",
    parameters={
        "crop_type": "wheat",
        "symptoms": {
            "leaf_condition": "rust-colored spots",
            "color_changes": "yellowing"
        },
        "location": "field-456"
    }
)

print(f"Diagnosis: {result.result['diagnosis']}")
print(f"Confidence: {result.result['confidence']}")
print(f"Treatment: {result.result['treatment_recommendations']}")
```

## Agent Discovery

Agents expose their capabilities via the standard `.well-known/agent-card.json` endpoint:

```bash
curl http://localhost:8001/a2a/.well-known/agent-card.json
```

Response:
```json
{
  "agent_id": "sahool-ai-advisor",
  "name": "SAHOOL AI Agricultural Advisor",
  "version": "1.0.0",
  "description": "Multi-agent AI system for agricultural advisory",
  "provider": "SAHOOL Agricultural Platform",
  "capabilities": [
    {
      "capability_id": "crop-disease-diagnosis",
      "name": "Crop Disease Diagnosis",
      "description": "Diagnose crop diseases...",
      "input_schema": {...},
      "output_schema": {...},
      "tags": ["agriculture", "disease", "diagnosis"]
    }
  ],
  "task_endpoint": "http://localhost:8001/a2a/tasks",
  "websocket_endpoint": "ws://localhost:8001/a2a/ws",
  "protocol_version": "1.0",
  "supports_streaming": true
}
```

## Testing

Run the comprehensive test suite:

```bash
# Run all A2A tests
pytest tests/a2a/test_protocol.py -v

# Run specific test
pytest tests/a2a/test_protocol.py::TestTaskMessage -v

# Run with coverage
pytest tests/a2a/ --cov=shared/a2a --cov-report=html
```

## Configuration

### Environment Variables

- `SERVICE_BASE_URL` - Base URL for the service (used in agent card)
- `A2A_ENABLE_STREAMING` - Enable WebSocket streaming (default: true)
- `A2A_TASK_TIMEOUT` - Default task timeout in seconds (default: 300)
- `A2A_MAX_RETRIES` - Maximum retry attempts (default: 3)

### Agent Configuration

```python
agent = MyAgent(
    agent_id="unique-agent-id",
    name="My Agent",
    version="1.0.0",
    description="Agent description",
    provider="Organization Name",
    task_endpoint="http://host:port/a2a/tasks",
    websocket_endpoint="ws://host:port/a2a/ws"  # Optional
)
```

## Production Considerations

### Security

- **Authentication**: Implement API key or OAuth2 authentication
- **Rate Limiting**: Use agent card `rate_limit` field to communicate limits
- **Input Validation**: Validate task parameters against capability schemas
- **CORS**: Configure appropriate CORS policies for web clients

### Monitoring

The A2A implementation includes built-in metrics:

```python
# Get agent statistics
stats = agent.get_stats()
# {
#     "tasks_received": 150,
#     "tasks_completed": 145,
#     "tasks_failed": 5,
#     "success_rate": 0.967,
#     "average_execution_time_ms": 234.5,
#     "queue_stats": {...},
#     "active_conversations": 12
# }
```

### Logging

All operations are logged using `structlog`:

```python
import structlog
logger = structlog.get_logger()

# Logs include structured context
# {"event": "task_completed", "task_id": "...", "execution_time_ms": 123}
```

### Health Checks

```bash
curl http://localhost:8001/a2a/health
```

### Cleanup

Periodically clean old conversations:

```python
# Remove conversations older than 24 hours
removed = agent.cleanup_old_conversations(max_age_hours=24)
```

## Best Practices

1. **Capability Design**: Define clear, focused capabilities with well-documented schemas
2. **Error Handling**: Always catch exceptions in task handlers and return meaningful errors
3. **Timeouts**: Set appropriate timeouts based on task complexity
4. **Idempotency**: Design task handlers to be idempotent when possible
5. **Versioning**: Use semantic versioning for agents and capabilities
6. **Documentation**: Provide examples in capability definitions
7. **Testing**: Write tests for each capability

## Roadmap

- [ ] OAuth2 authentication support
- [ ] Agent registry service
- [ ] Batch task optimization
- [ ] Task retry policies
- [ ] Circuit breaker pattern
- [ ] Distributed tracing integration
- [ ] GraphQL endpoint
- [ ] Agent marketplace

## References

- [Linux Foundation A2A Specification](https://www.linuxfoundation.org/a2a)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)

## License

This implementation is part of the SAHOOL platform.

## Support

For issues or questions, please contact the SAHOOL development team.
