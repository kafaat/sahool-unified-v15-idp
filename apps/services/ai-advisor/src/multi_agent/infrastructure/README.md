# Multi-Agent System Infrastructure
# البنية التحتية لنظام الوكلاء المتعددين

## Overview | نظرة عامة

This module provides comprehensive infrastructure for the SAHOOL multi-agent system, including:
1. **NATS-based Communication** - Asynchronous message passing between agents
2. **Shared Context Store** - Centralized Redis-based context storage for agent collaboration
3. **Agent Registry** - Dynamic agent discovery and registration

توفر هذه الوحدة بنية تحتية شاملة لنظام الوكلاء المتعددين في SAHOOL، بما في ذلك:
1. **اتصالات تعتمد على NATS** - تمرير الرسائل غير المتزامن بين الوكلاء
2. **مخزن السياق المشترك** - تخزين سياق مركزي يعتمد على Redis للتعاون بين الوكلاء
3. **سجل الوكلاء** - اكتشاف وتسجيل ديناميكي للوكلاء

---

# 1. Shared Context Store | مخزن السياق المشترك

## Overview | نظرة عامة

The Shared Context Store provides a centralized Redis-based storage for farm context data that multiple agents can access and contribute to during decision-making. It enables agents to share observations, analysis results, and recommendations.

يوفر مخزن السياق المشترك تخزيناً مركزياً يعتمد على Redis لبيانات سياق المزرعة التي يمكن لعدة وكلاء الوصول إليها والمساهمة فيها أثناء اتخاذ القرارات. يمكّن الوكلاء من مشاركة الملاحظات ونتائج التحليل والتوصيات.

## Features | الميزات

- **Centralized Context Storage** - Single source of truth for field data
- **Agent Collaboration** - Track opinions from multiple specialized agents
- **Fast Redis Access** - High-performance data retrieval
- **TTL Management** - Automatic context expiry
- **Type-Safe Data Classes** - Structured data models for all context types
- **Thread-Safe Operations** - Safe concurrent access from multiple agents

## Data Structures | هياكل البيانات

### FarmContext

Main context dataclass containing all field information:

```python
from multi_agent.infrastructure import FarmContext, SoilAnalysis, WeatherData

context = FarmContext(
    farm_id="FARM001",
    field_id="FLD001",
    tenant_id="TENANT001",
    crop_type="tomato",
    growth_stage="flowering",
    planting_date="2025-10-15",
    soil_data=SoilAnalysis(...),
    weather_data=WeatherData(...),
    satellite_indices=SatelliteIndices(...),
    recent_actions=[...],
    active_issues=[...]
)
```

### Supporting Data Classes

- **SoilAnalysis** - pH, NPK, organic matter, texture, moisture, EC
- **WeatherData** - Temperature, humidity, precipitation, wind, forecasts
- **SatelliteIndices** - NDVI, NDWI, EVI, SAVI, NDMI
- **FarmAction** - Historical farm operations (irrigation, fertilization, etc.)
- **Issue** - Current problems (diseases, pests, nutrient deficiencies)

## Usage | الاستخدام

### Initialize Store | تهيئة المخزن

```python
from multi_agent.infrastructure import get_shared_context_store

# Get singleton instance
store = get_shared_context_store(
    ttl=3600,  # Context expires after 1 hour
    key_prefix="sahool:multi_agent:context"
)
```

### Store Context | تخزين السياق

```python
from multi_agent.infrastructure import (
    FarmContext,
    SoilAnalysis,
    WeatherData,
    SatelliteIndices
)

# Create context
context = FarmContext(
    farm_id="FARM001",
    field_id="FLD001",
    tenant_id="TENANT001",
    crop_type="wheat",
    growth_stage="heading",
    planting_date="2025-11-01",
    soil_data=SoilAnalysis(
        ph=6.5,
        nitrogen=40.0,
        phosphorus=18.0,
        potassium=120.0,
        organic_matter=3.2,
        texture="loamy"
    ),
    weather_data=WeatherData(
        temperature=24.0,
        humidity=60.0,
        precipitation=0.0,
        wind_speed=10.0
    ),
    satellite_indices=SatelliteIndices(
        ndvi=0.72,
        ndwi=0.38
    )
)

# Store in Redis
store.set_context("FLD001", context)
```

### Retrieve Context | استرجاع السياق

```python
# Get context for a field
context = store.get_context("FLD001")

if context:
    print(f"Crop: {context.crop_type}")
    print(f"Stage: {context.growth_stage}")
    print(f"Soil pH: {context.soil_data.ph}")
    print(f"NDVI: {context.satellite_indices.ndvi}")
```

### Update Context | تحديث السياق

```python
# Update specific fields
store.update_context("FLD001", {
    "growth_stage": "grain_filling"
})
```

### Add Agent Opinions | إضافة آراء الوكلاء

```python
# Disease Expert adds opinion
disease_opinion = {
    "diagnosis": "Powdery Mildew",
    "confidence": 0.85,
    "severity": "medium",
    "recommendation": "Apply sulfur-based fungicide",
    "priority": "high"
}
store.add_agent_opinion("FLD001", "disease_expert", disease_opinion)

# Irrigation Advisor adds opinion
irrigation_opinion = {
    "current_status": "adequate",
    "recommendation": "Maintain schedule",
    "next_irrigation": "2025-12-30",
    "estimated_water_need": "450 m3"
}
store.add_agent_opinion("FLD001", "irrigation_advisor", irrigation_opinion)

# Field Analyst adds opinion
field_opinion = {
    "overall_health": "good",
    "ndvi_trend": "stable",
    "areas_of_concern": ["Northeast corner"],
    "recommendation": "Focus treatment on affected area"
}
store.add_agent_opinion("FLD001", "field_analyst", field_opinion)
```

### Retrieve All Opinions | استرجاع جميع الآراء

```python
# Get all agent opinions
opinions = store.get_all_opinions("FLD001")

for agent_id, opinion in opinions.items():
    print(f"Agent: {agent_id}")
    print(f"Recommendation: {opinion.get('recommendation')}")
    print(f"Priority: {opinion.get('priority')}")
```

### Clear Opinions | مسح الآراء

```python
# After decision is made, clear opinions for next round
store.clear_opinions("FLD001")
```

### TTL Management | إدارة TTL

```python
# Check remaining TTL
ttl = store.get_ttl("FLD001")
print(f"Context expires in {ttl} seconds")

# Refresh TTL
store.refresh_ttl("FLD001")
```

### Health Check | فحص الصحة

```python
health = store.health_check()
print(f"Status: {health['status']}")
print(f"Redis Connected: {health['redis_connected']}")
```

## Integration with Multi-Agent System | التكامل مع نظام متعدد الوكلاء

```python
from agents.base_agent import BaseAgent
from multi_agent.infrastructure import get_shared_context_store

class CollaborativeAgent(BaseAgent):
    """Agent with shared context capabilities"""

    def __init__(self, name: str, role: str, **kwargs):
        super().__init__(name, role, **kwargs)
        self.context_store = get_shared_context_store()

    async def analyze_field(self, field_id: str):
        """Analyze field and add opinion to shared context"""

        # 1. Get shared context
        context = self.context_store.get_context(field_id)

        if not context:
            logger.warning(f"No context found for field {field_id}")
            return

        # 2. Perform analysis using agent's expertise
        query = f"Analyze {context.crop_type} at {context.growth_stage} stage"
        result = await self.think(query, context=context.to_dict())

        # 3. Add opinion to shared context
        opinion = {
            "analysis": result['response'],
            "confidence": result['confidence'],
            "timestamp": datetime.now().isoformat()
        }
        self.context_store.add_agent_opinion(
            field_id,
            self.name,
            opinion
        )

        # 4. Check other agents' opinions
        all_opinions = self.context_store.get_all_opinions(field_id)
        logger.info(f"Total opinions: {len(all_opinions)}")

        return result
```

## Example Workflow | سير عمل مثالي

```python
# 1. Master Advisor receives query
query = "My tomato plants have yellow leaves"
field_id = "FLD001"

# 2. Master creates/updates shared context
context = create_field_context(field_id)
store.set_context(field_id, context)

# 3. Consult specialist agents
await field_analyst.analyze_field(field_id)
await disease_expert.analyze_field(field_id)
await irrigation_advisor.analyze_field(field_id)

# 4. Collect all opinions
opinions = store.get_all_opinions(field_id)

# 5. Synthesize final recommendation
final_recommendation = synthesize_opinions(opinions)

# 6. Clear opinions for next query
store.clear_opinions(field_id)
```

## Running the Example | تشغيل المثال

```bash
# Make sure Redis is running
docker ps | grep redis

# Run the example
cd /home/user/sahool-unified-v15-idp/apps/services/ai-advisor/src/multi_agent/infrastructure
python shared_context_example.py
```

---

# 2. NATS Communication Infrastructure | البنية التحتية لاتصالات NATS

## Overview | نظرة عامة

NATS-based communication infrastructure enables agents to communicate asynchronously, request opinions from other agents, broadcast messages, and participate in council discussions.

توفر البنية التحتية للاتصالات تعتمد على NATS وتمكن الوكلاء من التواصل بشكل غير متزامن، وطلب آراء من وكلاء آخرين، وبث الرسائل، والمشاركة في مناقشات المجلس.

## Features | الميزات

- **Point-to-Point Communication** | اتصال من نقطة إلى نقطة
  - Send messages to specific agents
  - Request and wait for responses with timeout
  - Automatic retry logic

- **Broadcast Communication** | اتصال البث
  - Send messages to all agents simultaneously
  - Priority-based message handling

- **Council Communication** | اتصال المجلس
  - Group discussions between multiple agents
  - Topic-based subscriptions

- **Reliability** | الموثوقية
  - Automatic reconnection on connection loss
  - Retry logic with configurable attempts
  - Error handling and logging

- **Message Types** | أنواع الرسائل
  - REQUEST: Request for information
  - RESPONSE: Response to a request
  - BROADCAST: Message to all agents
  - COUNCIL: Council group message
  - NOTIFICATION: System notifications
  - HEARTBEAT: Health check messages

## Architecture | الهندسة المعمارية

### Topics Structure | هيكل المواضيع

```
sahool.agents.{agent_id}.request   - Incoming requests for specific agent
sahool.agents.{agent_id}.response  - Responses to specific agent
sahool.agents.broadcast            - Broadcast to all agents
sahool.agents.council.{council_id} - Council group communications
```

### Message Flow | تدفق الرسائل

```
Agent A                NATS Broker              Agent B
   |                        |                      |
   |------ Request -------->|                      |
   |                        |------ Request ------>|
   |                        |                      |
   |                        |<----- Response ------|
   |<----- Response --------|                      |
```

## Installation | التثبيت

The required dependency is already included in the project:

```bash
# Already in pyproject.toml
nats-py==2.9.0
```

## Usage | الاستخدام

### Basic Setup | الإعداد الأساسي

```python
from multi_agent.infrastructure import AgentNATSBridge, MessagePriority

# Initialize the bridge
bridge = AgentNATSBridge(
    agent_id="field-analyst",
    nats_url="nats://localhost:4222"
)

# Connect to NATS
await bridge.connect()

# Check connection status
if bridge.is_connected:
    print("Connected to NATS!")
```

### Request-Response Pattern | نمط الطلب-الاستجابة

```python
# Request opinion from another agent
response = await bridge.request_opinion(
    agent_id="disease-expert",
    query="What disease affects wheat with yellow leaves?",
    context={"field_id": "A-12", "crop_type": "wheat"},
    timeout=30.0,
    max_retries=3
)

print(f"Response: {response}")
```

### Send Direct Message | إرسال رسالة مباشرة

```python
# Send message to specific agent
message_id = await bridge.publish_to_agent(
    agent_id="irrigation-advisor",
    content={
        "query": "Recommend irrigation schedule",
        "field_data": {...}
    },
    priority=MessagePriority.HIGH
)
```

### Broadcast to All Agents | البث إلى جميع الوكلاء

```python
# Broadcast announcement
message_id = await bridge.broadcast(
    content={
        "type": "weather_alert",
        "message": "Heavy rain expected in 24 hours",
        "severity": "high"
    },
    priority=MessagePriority.URGENT
)
```

### Council Communication | اتصال المجلس

```python
# Join a council
await bridge.subscribe_to_council(
    council_id="crop-management-council",
    handler=handle_council_message
)

# Send message to council
await bridge.publish_to_council(
    council_id="crop-management-council",
    content={
        "topic": "Crop Health Assessment",
        "message": "Need expert input on sector A-12"
    }
)
```

### Custom Message Handlers | معالجات الرسائل المخصصة

```python
async def handle_request(message: AgentMessage):
    """Handle incoming requests"""
    print(f"Received from {message.sender_id}: {message.content}")
    
    # Process the request
    result = await process_query(message.content['query'])
    
    # Send response
    await bridge.send_response(
        recipient_id=message.sender_id,
        content={"answer": result},
        correlation_id=message.correlation_id
    )

# Subscribe to custom topic
await bridge.subscribe(
    topic="sahool.agents.field-analyst.custom",
    handler=handle_request
)
```

### Health Check | فحص الصحة

```python
# Get health status
health = await bridge.health_check()
print(f"Connected: {health['connected']}")
print(f"Subscriptions: {health['subscriptions']}")
print(f"Pending Requests: {health['pending_requests']}")
```

### Graceful Shutdown | إيقاف نظيف

```python
# Disconnect from NATS
await bridge.disconnect()
```

## Integration with Existing Agents | التكامل مع الوكلاء الموجودين

To integrate the NATS bridge with existing agents (like `FieldAnalystAgent`, `DiseaseExpertAgent`, etc.):

```python
from agents.base_agent import BaseAgent
from multi_agent.infrastructure import AgentNATSBridge, AgentMessage

class EnhancedAgent(BaseAgent):
    """Agent with NATS communication capabilities"""
    
    def __init__(self, name: str, role: str, **kwargs):
        super().__init__(name, role, **kwargs)
        
        # Initialize NATS bridge
        self.bridge = AgentNATSBridge(
            agent_id=name,
            nats_url=settings.nats_url
        )
    
    async def start(self):
        """Start agent and connect to NATS"""
        await self.bridge.connect()
        
        # Subscribe to incoming requests
        await self.bridge.subscribe(
            f"sahool.agents.{self.name}.request",
            self.handle_agent_request
        )
    
    async def handle_agent_request(self, message: AgentMessage):
        """Handle requests from other agents"""
        query = message.content.get('query')
        context = message.content.get('context', {})
        
        # Use existing think() method
        result = await self.think(query, context)
        
        # Send response back
        await self.bridge.send_response(
            recipient_id=message.sender_id,
            content=result,
            correlation_id=message.correlation_id
        )
    
    async def consult_agent(self, agent_id: str, query: str):
        """Consult another agent"""
        return await self.bridge.request_opinion(
            agent_id=agent_id,
            query=query,
            timeout=30.0
        )
    
    async def stop(self):
        """Stop agent and disconnect"""
        await self.bridge.disconnect()
```

## Configuration | التكوين

Update your `config.py` or environment variables:

```python
# config.py
class Settings(BaseSettings):
    # NATS Configuration
    nats_url: str = "nats://nats:4222"
    nats_subject_prefix: str = "sahool.ai-advisor"
    
    # Agent Configuration
    agent_request_timeout: int = 30  # seconds
    agent_max_retries: int = 3
    nats_max_reconnect_attempts: int = 10
    nats_reconnect_time_wait: int = 2
```

## Error Handling | معالجة الأخطاء

The bridge includes comprehensive error handling:

```python
try:
    response = await bridge.request_opinion(
        agent_id="disease-expert",
        query="Diagnose crop issue",
        timeout=10.0
    )
except TimeoutError:
    print("Request timed out - agent may be unavailable")
except ConnectionError:
    print("Not connected to NATS")
except Exception as e:
    print(f"Error: {e}")
```

## Message Priority | أولوية الرسائل

Messages can have different priority levels:

- `MessagePriority.LOW` - Low priority background tasks
- `MessagePriority.NORMAL` - Default priority
- `MessagePriority.HIGH` - Important messages
- `MessagePriority.URGENT` - Critical alerts

```python
await bridge.broadcast(
    content={"alert": "System maintenance"},
    priority=MessagePriority.URGENT
)
```

## Testing | الاختبار

Run the example to test the infrastructure:

```bash
# Start NATS server (if not running in Docker)
docker run -p 4222:4222 nats:latest

# Run the example
cd /home/user/sahool-unified-v15-idp/apps/services/ai-advisor/src/multi_agent/infrastructure
python example_usage.py
```

## Monitoring | المراقبة

The bridge logs all communication events using `structlog`:

```python
# Events logged:
- nats_bridge_initialized
- nats_connected
- message_published
- broadcast_published
- opinion_requested
- opinion_received
- request_received
- response_sent
- nats_error
- nats_disconnected
- nats_reconnected
```

## Performance Considerations | اعتبارات الأداء

- Messages are processed asynchronously for high throughput
- Connection pooling and automatic reconnection
- Configurable timeouts and retry logic
- Queue groups for load balancing (optional)

## Security | الأمان

For production deployments:

1. Enable NATS authentication:
   ```python
   bridge = AgentNATSBridge(
       agent_id="field-analyst",
       nats_url="nats://user:password@nats:4222"
   )
   ```

2. Use TLS encryption:
   ```python
   nats_url = "tls://nats:4222"
   ```

3. Implement message validation in handlers
4. Use correlation IDs to prevent replay attacks

## Troubleshooting | استكشاف الأخطاء

### Common Issues | المشاكل الشائعة

1. **Connection Failed**
   - Check NATS server is running
   - Verify NATS URL is correct
   - Check firewall/network settings

2. **Timeout on Requests**
   - Increase timeout value
   - Check target agent is connected
   - Verify agent ID is correct

3. **Messages Not Received**
   - Ensure subscription is active
   - Check topic naming matches
   - Verify handler function is async

## License | الترخيص

Proprietary - KAFAAT Team

## Support | الدعم

For questions or issues, contact: dev@kafaat.io
