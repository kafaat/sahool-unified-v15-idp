# A2A Protocol Quick Start Guide

## 5-Minute Quick Start

### 1. Discover an Agent

```python
from a2a.client import AgentDiscovery

discovery = AgentDiscovery()
agent_card = await discovery.discover_agent("http://localhost:8001")

print(f"Found: {agent_card.name}")
for cap in agent_card.capabilities:
    print(f"  - {cap.name}")
```

### 2. Send a Task

```python
from a2a.client import A2AClient

client = A2AClient(sender_agent_id="my-app")

result = await client.send_task(
    agent_card=agent_card,
    task_type="crop-disease-diagnosis",
    task_description="Diagnose disease",
    parameters={
        "crop_type": "tomato",
        "symptoms": {"leaf_condition": "yellow spots"}
    }
)

print(f"Result: {result.result}")
```

### 3. Create Your Own Agent

```python
from a2a.agent import A2AAgent, AgentCapability
from a2a.protocol import TaskMessage

class MyAgent(A2AAgent):
    def get_capabilities(self):
        return [
            AgentCapability(
                capability_id="my-task",
                name="My Task",
                description="Does something useful",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
            )
        ]

# Initialize
agent = MyAgent(
    agent_id="my-agent",
    name="My Agent",
    version="1.0.0",
    description="My A2A agent",
    provider="Me",
    task_endpoint="http://localhost:8000/a2a/tasks"
)

# Register handler
async def my_handler(task: TaskMessage) -> dict:
    return {"status": "done", "input": task.parameters}

agent.register_task_handler("my-task", my_handler)
```

### 4. Expose Agent via FastAPI

```python
from fastapi import FastAPI
from a2a.server import create_a2a_router

app = FastAPI()

# Add A2A endpoints
router = create_a2a_router(agent, prefix="/a2a")
app.include_router(router)

# Now your agent is discoverable at:
# GET http://localhost:8000/a2a/.well-known/agent-card.json
```

## Common Tasks

### Stream a Task with Progress

```python
async for update in client.stream_task(
    agent_card=agent_card,
    task_type="field-analysis",
    task_description="Analyze field",
    parameters={"field_id": "123"}
):
    if update.is_final:
        print(f"Done: {update.result}")
    else:
        print(f"Progress: {update.progress * 100:.0f}%")
```

### Search for Agents by Capability

```python
# Discover multiple agents
agents = await discovery.discover_multiple([
    "http://localhost:8001",
    "http://localhost:8002",
    "http://localhost:8003"
])

# Find agents with specific capability
disease_agents = discovery.get_agents_by_capability(
    "crop-disease-diagnosis"
)

# Search by tags
agri_agents = discovery.search_agents(tags=["agriculture"])
```

### Send Batch Tasks

```python
tasks = [
    {
        "task_type": "task-1",
        "task_description": "First task",
        "parameters": {"data": "value1"}
    },
    {
        "task_type": "task-2",
        "task_description": "Second task",
        "parameters": {"data": "value2"}
    }
]

results = await client.batch_send_tasks(
    tasks=tasks,
    agent_card=agent_card
)

for result in results:
    print(f"Task {result.task_id}: {result.state}")
```

### Track Conversations

```python
conversation_id = "my-conversation-123"

# Turn 1
result1 = await client.send_task(
    agent_card=agent_card,
    task_type="general-query",
    task_description="First question",
    parameters={"question": "How to grow wheat?"},
    conversation_id=conversation_id
)

# Turn 2 - continues same conversation
result2 = await client.send_task(
    agent_card=agent_card,
    task_type="disease-check",
    task_description="Follow-up",
    parameters={"crop_type": "wheat"},
    conversation_id=conversation_id
)
```

## Running the Examples

```bash
# Run all examples
cd /home/user/sahool-unified-v15-idp/shared/a2a
python3 examples.py

# Or run specific example
python3 -c "
import asyncio
from examples import example_discover_agent
asyncio.run(example_discover_agent())
"
```

## Testing

```bash
# Run tests
cd /home/user/sahool-unified-v15-idp
pytest tests/a2a/test_protocol.py -v

# Run specific test
pytest tests/a2a/test_protocol.py::TestTaskMessage -v

# With coverage
pytest tests/a2a/ --cov=shared/a2a --cov-report=term-missing
```

## Accessing AI Advisor via A2A

The AI Advisor service is A2A-enabled at `http://localhost:8001/a2a/`:

```python
# Discover AI Advisor
advisor = await discovery.discover_agent("http://localhost:8001")

# Available capabilities:
# - crop-disease-diagnosis
# - irrigation-optimization
# - yield-prediction
# - field-analysis
# - general-agricultural-query

# Example: Diagnose disease
result = await client.send_task(
    agent_card=advisor,
    task_type="crop-disease-diagnosis",
    task_description="Diagnose tomato disease",
    parameters={
        "crop_type": "tomato",
        "symptoms": {
            "leaf_condition": "yellow spots",
            "color_changes": "browning"
        }
    }
)

print(f"Diagnosis: {result.result['diagnosis']}")
print(f"Treatment: {result.result['treatment_recommendations']}")
```

## Troubleshooting

### Agent Not Discovered
```python
# Check if service is running
curl http://localhost:8001/a2a/.well-known/agent-card.json

# Check logs
tail -f logs/ai-advisor.log
```

### Task Failed
```python
# Check task status
result = await client.send_task(...)
if result.state == TaskState.FAILED:
    print(f"Error: {result.result['error']}")
```

### WebSocket Issues
```python
# Ensure agent supports streaming
if not agent_card.supports_streaming:
    print("Agent doesn't support streaming")
else:
    # Use streaming
    async for update in client.stream_task(...):
        print(update)
```

## Configuration

### Client Timeout
```python
client = A2AClient(
    sender_agent_id="my-app",
    timeout=60,  # seconds
    max_retries=3
)
```

### Agent Cleanup
```python
# Clean old conversations periodically
removed = agent.cleanup_old_conversations(max_age_hours=24)
print(f"Removed {removed} old conversations")
```

### Agent Stats
```python
stats = agent.get_stats()
print(f"Tasks completed: {stats['tasks_completed']}")
print(f"Success rate: {stats['success_rate']:.1%}")
print(f"Avg time: {stats['average_execution_time_ms']:.0f}ms")
```

## Next Steps

1. Read the [full documentation](README.md)
2. Review [examples](examples.py)
3. Check [implementation summary](../../docs/A2A_IMPLEMENTATION_SUMMARY.md)
4. Explore [test cases](../../tests/a2a/test_protocol.py)

## Support

For questions or issues, refer to:
- `/shared/a2a/README.md` - Full documentation
- `/shared/a2a/examples.py` - Working examples
- `/tests/a2a/test_protocol.py` - Test cases

Happy agent building! 🤖
