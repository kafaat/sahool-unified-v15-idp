# Agent-to-Agent (A2A) Protocol Tests

Tests for the A2A inter-agent communication protocol implementation (`shared/a2a/`). The A2A protocol follows the Linux Foundation A2A specification and enables SAHOOL's AI agents to delegate tasks, share results, and coordinate workflows autonomously.

## Running

```bash
# All A2A tests
pytest tests/a2a/ -v

# Single test file
pytest tests/a2a/test_protocol.py -v

# With verbose output for debugging agent messages
pytest tests/a2a/ -v -s
```

## Test Files

### `test_protocol.py`

Comprehensive tests for the A2A protocol layer covering all message types and agent lifecycle:

**Message Types**
- `TestTaskMessage` — Task creation, priority, parameters, and default message type assignment
- `TestTaskResultMessage` — Success/failure results, output data, and error message propagation
- `TestErrorMessage` — Error code, description, and recoverable flag handling
- `TestConversationContext` — Multi-turn conversation state, message history management

**Protocol Infrastructure**
- `TestTaskQueue` — FIFO task queue ordering, priority queue behavior, queue capacity limits
- `TestMessageType` — Enum values for TASK, RESULT, ERROR, PING, PONG, DISCOVERY

**Agent Components**
- `TestA2AAgent` — Agent card creation, capability registration, task handler dispatch
- `TestAgentCapability` — Capability schema validation, input/output type definitions
- `TestAgentCard` — Agent metadata (ID, name, description, capabilities, endpoint URL)

**Client & Discovery**
- `TestA2AClient` — Client initialization, agent endpoint resolution, task submission
- `TestAgentDiscovery` — Agent registry lookup, capability-based discovery

## Key Concepts Tested

```python
from shared.a2a.protocol import TaskMessage, TaskState, MessageType
from shared.a2a.agent import A2AAgent, AgentCapability, AgentCard
from shared.a2a.client import A2AClient, AgentDiscovery

# Task state lifecycle: PENDING → IN_PROGRESS → COMPLETED / FAILED
task = TaskMessage(
    sender_agent_id="crop-advisor",
    receiver_agent_id="irrigation-expert",
    task_type="irrigation-schedule",
    task_description="Calculate weekly irrigation for wheat field",
    parameters={"field_id": "FIELD-003", "crop_stage": "tillering"},
    priority=8,  # 1-10, higher = more urgent
)
assert task.message_type == MessageType.TASK
```

## Related

- Implementation: `shared/a2a/`
- Agent definitions: `governance/agents.yaml`
- A2A integration tests: `tests/integration/`
- Agent evaluation: `tests/evaluation/`
