# NATS Bridge Quick Start Guide
# دليل البدء السريع لجسر NATS

## Installation | التثبيت

The dependency is already included in the project:

```toml
# pyproject.toml
infrastructure = [
    "nats-py==2.9.0",
    ...
]
```

## Basic Usage in 5 Minutes | الاستخدام الأساسي في 5 دقائق

### Step 1: Import | الخطوة 1: الاستيراد

```python
from multi_agent.infrastructure import (
    AgentNATSBridge,
    MessagePriority,
    MessageType,
)
```

### Step 2: Initialize | الخطوة 2: التهيئة

```python
# Create bridge for your agent
bridge = AgentNATSBridge(
    agent_id="field-analyst",
    nats_url="nats://nats:4222"  # Or from settings.nats_url
)

# Connect to NATS
await bridge.connect()
```

### Step 3: Send Messages | الخطوة 3: إرسال الرسائل

```python
# Request opinion from another agent
response = await bridge.request_opinion(
    agent_id="disease-expert",
    query="What disease affects wheat with yellow leaves?",
    timeout=30.0
)

# Broadcast to all agents
await bridge.broadcast(
    content={"alert": "Heavy rain expected"},
    priority=MessagePriority.HIGH
)

# Send to specific agent
await bridge.publish_to_agent(
    agent_id="irrigation-advisor",
    content={"query": "Recommend irrigation schedule"}
)
```

### Step 4: Receive Messages | الخطوة 4: استقبال الرسائل

```python
# Define handler
async def handle_request(message):
    query = message.content.get('query')
    # Process query...
    result = {"answer": "..."}
    
    # Send response
    await bridge.send_response(
        recipient_id=message.sender_id,
        content=result,
        correlation_id=message.correlation_id
    )

# Subscribe to your agent's requests
await bridge.subscribe(
    f"sahool.agents.field-analyst.request",
    handle_request
)
```

### Step 5: Cleanup | الخطوة 5: التنظيف

```python
# Graceful shutdown
await bridge.disconnect()
```

## Integration with BaseAgent | التكامل مع BaseAgent

Add NATS communication to your existing agent:

```python
from agents.base_agent import BaseAgent
from multi_agent.infrastructure import AgentNATSBridge
from config import settings

class MultiAgentEnabled(BaseAgent):
    """Agent with multi-agent communication"""
    
    def __init__(self, name: str, role: str, **kwargs):
        super().__init__(name, role, **kwargs)
        
        # Add NATS bridge
        self.bridge = AgentNATSBridge(
            agent_id=name,
            nats_url=settings.nats_url
        )
    
    async def start(self):
        """Start agent and enable communication"""
        await self.bridge.connect()
        await self.bridge.subscribe(
            f"sahool.agents.{self.name}.request",
            self._handle_agent_request
        )
    
    async def _handle_agent_request(self, message):
        """Handle requests from other agents"""
        query = message.content.get('query')
        context = message.content.get('context')
        
        # Use existing think() method
        result = await self.think(query, context)
        
        # Send response
        await self.bridge.send_response(
            recipient_id=message.sender_id,
            content=result,
            correlation_id=message.correlation_id
        )
    
    async def ask_expert(self, expert_id: str, question: str):
        """Consult another agent"""
        return await self.bridge.request_opinion(
            agent_id=expert_id,
            query=question
        )
    
    async def stop(self):
        """Stop agent"""
        await self.bridge.disconnect()
```

## Real-World Example | مثال من العالم الحقيقي

```python
import asyncio
from agents.field_analyst import FieldAnalystAgent
from agents.disease_expert import DiseaseExpertAgent
from config import settings

async def multi_agent_consultation():
    # Create agents
    field_analyst = FieldAnalystAgent(
        name="field-analyst",
        role="Field Analysis Expert"
    )
    disease_expert = DiseaseExpertAgent(
        name="disease-expert",
        role="Disease Diagnosis Expert"
    )
    
    # Add NATS bridges
    field_analyst.bridge = AgentNATSBridge(
        agent_id="field-analyst",
        nats_url=settings.nats_url
    )
    disease_expert.bridge = AgentNATSBridge(
        agent_id="disease-expert",
        nats_url=settings.nats_url
    )
    
    # Connect both agents
    await field_analyst.bridge.connect()
    await disease_expert.bridge.connect()
    
    # Field analyst requests disease expert's opinion
    response = await field_analyst.bridge.request_opinion(
        agent_id="disease-expert",
        query="Diagnose wheat crop with yellow leaves and brown spots",
        context={
            "field_id": "A-12",
            "crop_type": "wheat",
            "symptoms": ["yellow_leaves", "brown_spots"]
        }
    )
    
    print(f"Disease Expert Opinion: {response}")
    
    # Cleanup
    await field_analyst.bridge.disconnect()
    await disease_expert.bridge.disconnect()

# Run
asyncio.run(multi_agent_consultation())
```

## Configuration | التكوين

Add to your `.env` or `config.py`:

```python
# NATS Configuration
NATS_URL=nats://nats:4222
NATS_SUBJECT_PREFIX=sahool.ai-advisor

# Agent Communication
AGENT_REQUEST_TIMEOUT=30
AGENT_MAX_RETRIES=3
```

## Troubleshooting | استكشاف الأخطاء

### Connection Failed

```python
# Check NATS is running
docker ps | grep nats

# Test connection
telnet nats 4222
```

### No Response from Agent

```python
# Check agent is subscribed
health = await bridge.health_check()
print(health['subscriptions'])

# Increase timeout
response = await bridge.request_opinion(
    agent_id="other-agent",
    query="...",
    timeout=60.0  # Increase from 30s
)
```

### Message Not Received

```python
# Verify topic name
topic = bridge._get_agent_topic("request")
print(f"Subscribed to: {topic}")

# Check handler is async
async def my_handler(message):  # ✓ Correct
    pass

def my_handler(message):  # ✗ Wrong - not async
    pass
```

## Testing | الاختبار

Run the example:

```bash
# Terminal 1: Start NATS
docker run -p 4222:4222 nats:latest

# Terminal 2: Run example
cd /home/user/sahool-unified-v15-idp/apps/services/ai-advisor/src/multi_agent/infrastructure
python example_usage.py
```

## API Reference | مرجع API

See `README.md` for complete API documentation.

## Support | الدعم

For questions: dev@kafaat.io

---

**Ready to use!** | جاهز للاستخدام!
