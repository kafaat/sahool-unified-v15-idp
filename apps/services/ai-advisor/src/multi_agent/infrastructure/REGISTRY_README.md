# Agent Registry Client - دليل عميل سجل الوكلاء

## Overview | نظرة عامة

The Agent Registry Client provides dynamic agent discovery and management for SAHOOL's multi-agent agricultural intelligence system. It enables agents to register themselves, advertise their capabilities, and be discovered by other components based on required skills.

يوفر عميل سجل الوكلاء اكتشافًا وإدارة ديناميكية للوكلاء لنظام الذكاء الزراعي متعدد الوكلاء في سهول. يمكّن الوكلاء من تسجيل أنفسهم والإعلان عن قدراتهم واكتشافهم بواسطة مكونات أخرى بناءً على المهارات المطلوبة.

## Features | الميزات

- ✅ **Redis-backed distributed registry** | سجل موزع مدعوم بـ Redis
- ✅ **A2A Protocol compatible** | متوافق مع بروتوكول A2A
- ✅ **Capability-based discovery** | اكتشاف قائم على القدرات
- ✅ **Performance tracking** | تتبع الأداء
- ✅ **Health monitoring** | مراقبة الصحة
- ✅ **In-memory caching** | تخزين مؤقت في الذاكرة
- ✅ **Automatic TTL management** | إدارة تلقائية لوقت انتهاء الصلاحية

## Architecture | البنية المعمارية

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Registry Client                     │
│                    عميل سجل الوكلاء                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Registration │  │  Discovery   │  │  Performance │      │
│  │   تسجيل      │  │   اكتشاف     │  │    أداء      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────────────────────────────────────────┐       │
│  │         In-Memory Cache | تخزين مؤقت            │       │
│  └──────────────────────────────────────────────────┘       │
│                          ↕                                   │
│  ┌──────────────────────────────────────────────────┐       │
│  │         Redis Backend | خلفية Redis              │       │
│  │  - Agent Cards | بطاقات الوكلاء                  │       │
│  │  - Capability Indexes | فهارس القدرات            │       │
│  │  - Performance Scores | درجات الأداء             │       │
│  └──────────────────────────────────────────────────┘       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Data Models | نماذج البيانات

### AgentStatus

Agent operational status | حالة تشغيل الوكيل

```python
class AgentStatus(str, Enum):
    ACTIVE = "active"        # نشط - Ready to process
    INACTIVE = "inactive"    # غير نشط - Not available
    BUSY = "busy"           # مشغول - Currently processing
    MAINTENANCE = "maintenance"  # صيانة - Under maintenance
```

### AgentCapability

Agricultural domain capabilities | قدرات المجال الزراعي

```python
class AgentCapability(str, Enum):
    # Crop Health | صحة المحاصيل
    DIAGNOSIS = "diagnosis"              # تشخيص الأمراض
    TREATMENT = "treatment"              # علاج

    # Water Management | إدارة المياه
    IRRIGATION = "irrigation"            # ري

    # Soil & Nutrition | التربة والتغذية
    FERTILIZATION = "fertilization"      # تسميد
    SOIL_SCIENCE = "soil_science"        # علم التربة

    # Pest & Disease | الآفات والأمراض
    PEST_MANAGEMENT = "pest_management"  # إدارة الآفات

    # Analytics | التحليل
    YIELD_PREDICTION = "yield_prediction"  # توقع المحصول
    MARKET_ANALYSIS = "market_analysis"    # تحليل السوق

    # Environmental | البيئة
    ECOLOGICAL = "ecological"              # بيئي
    WEATHER_ANALYSIS = "weather_analysis"  # تحليل الطقس

    # Remote Sensing | الاستشعار عن بعد
    IMAGE_ANALYSIS = "image_analysis"          # تحليل الصور
    SATELLITE_ANALYSIS = "satellite_analysis"  # تحليل الأقمار الصناعية
```

### AgentCard

Complete agent specification | مواصفات الوكيل الكاملة

```python
@dataclass
class AgentCard:
    # Core Identity | الهوية الأساسية
    agent_id: str                          # معرف فريد
    name: str                              # الاسم
    description: str                       # وصف إنجليزي
    description_ar: str                    # وصف عربي

    # Capabilities | القدرات
    capabilities: List[AgentCapability]    # القدرات
    skills: List[str]                      # المهارات

    # Configuration | الإعدادات
    model: str                             # نموذج اللغة
    endpoint: str                          # نقطة النهاية

    # Status | الحالة
    status: AgentStatus                    # الحالة
    performance_score: float               # درجة الأداء (0.0-1.0)
    last_heartbeat: datetime               # آخر نبضة

    # Metadata | البيانات الوصفية
    version: str                           # الإصدار
    tags: List[str]                        # علامات
    created_at: datetime                   # تاريخ الإنشاء
    updated_at: datetime                   # تاريخ التحديث
```

## Usage | الاستخدام

### 1. Initialization | التهيئة

```python
from multi_agent.infrastructure import AgentRegistryClient

# Create client instance
client = AgentRegistryClient(
    redis_url="redis://localhost:6379/0",
    key_prefix="sahool:agents:",
    cache_ttl=300,      # 5 minutes
    agent_ttl=3600,     # 1 hour
)

# Connect to Redis
await client.connect()

# Or use as context manager
async with AgentRegistryClient(redis_url="redis://localhost:6379/0") as client:
    # Use client
    pass
```

### 2. Agent Registration | تسجيل الوكلاء

```python
from multi_agent.infrastructure import (
    AgentCard,
    AgentCapability,
    AgentStatus,
)

# Create agent card
agent = AgentCard(
    agent_id="disease-expert",
    name="Disease Expert Agent",
    description="Specialized in diagnosing crop diseases",
    description_ar="متخصص في تشخيص أمراض المحاصيل",
    capabilities=[
        AgentCapability.DIAGNOSIS,
        AgentCapability.TREATMENT,
        AgentCapability.IMAGE_ANALYSIS,
    ],
    skills=["plant_pathology", "disease_identification"],
    model="claude-3-5-sonnet-20241022",
    endpoint="http://localhost:8112/agents/disease-expert",
    status=AgentStatus.ACTIVE,
    performance_score=0.92,
    tags=["disease", "diagnosis", "أمراض"],
)

# Register agent
await client.register_agent(agent)
```

### 3. Agent Discovery | اكتشاف الوكلاء

```python
# Discover agents by single capability
agents = await client.discover_agents([AgentCapability.DIAGNOSIS])

# Discover agents with multiple capabilities
agents = await client.discover_agents([
    AgentCapability.IRRIGATION,
    AgentCapability.WEATHER_ANALYSIS,
])

# Get best performing agent for a capability
best_agent = await client.get_best_agent(AgentCapability.DIAGNOSIS)
if best_agent:
    print(f"Best agent: {best_agent.name}")
    print(f"Performance: {best_agent.performance_score}")

# Get specific agent by ID
agent = await client.get_agent("disease-expert")
```

### 4. Status Management | إدارة الحالة

```python
# Update agent status
await client.update_status("disease-expert", AgentStatus.BUSY)

# Send heartbeat
await client.heartbeat("disease-expert")

# Update performance score
await client.update_performance("disease-expert", 0.95)
```

### 5. Deregistration | إلغاء التسجيل

```python
# Deregister agent
await client.deregister_agent("disease-expert")
```

### 6. Registry Statistics | إحصائيات السجل

```python
# Get registry statistics
stats = await client.get_registry_stats()

print(f"Total Agents: {stats['total_agents']}")
print(f"Average Performance: {stats['average_performance']}")
print(f"Status Distribution: {stats['status_distribution']}")
print(f"Capability Distribution: {stats['capability_distribution']}")
```

## Configuration | الإعدادات

Add to `config.py`:

```python
class Settings(BaseSettings):
    # Redis - Agent Registry
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_key_prefix: str = "sahool:agents:"
    agent_registry_ttl: int = 3600  # seconds
```

## Redis Data Structure | هيكل بيانات Redis

### Keys | المفاتيح

```
sahool:agents:agent:{agent_id}          # Agent card JSON
sahool:agents:agents                     # Set of all agent IDs
sahool:agents:capability:{capability}    # Set of agent IDs with capability
sahool:agents:performance:{agent_id}     # Performance score
```

### Example | مثال

```redis
# Agent card
SET sahool:agents:agent:disease-expert '{"agent_id": "disease-expert", ...}' EX 3600

# Agents set
SADD sahool:agents:agents disease-expert

# Capability index
SADD sahool:agents:capability:diagnosis disease-expert
EXPIRE sahool:agents:capability:diagnosis 3600

# Performance score
SET sahool:agents:performance:disease-expert "0.92" EX 3600
```

## Best Practices | أفضل الممارسات

### 1. Heartbeat Management | إدارة النبضات

Send heartbeats regularly to keep agents alive:

```python
import asyncio

async def heartbeat_loop(client, agent_id):
    """Send heartbeat every 5 minutes"""
    while True:
        await client.heartbeat(agent_id)
        await asyncio.sleep(300)  # 5 minutes
```

### 2. Performance Tracking | تتبع الأداء

Update performance scores based on actual agent performance:

```python
async def track_performance(client, agent_id, success_rate):
    """Update performance score based on success rate"""
    # Calculate score (0.0 - 1.0)
    score = min(1.0, max(0.0, success_rate))
    await client.update_performance(agent_id, score)
```

### 3. Graceful Shutdown | الإغلاق السلس

Always deregister agents on shutdown:

```python
async def shutdown_agent(client, agent_id):
    """Gracefully shutdown agent"""
    # Update status
    await client.update_status(agent_id, AgentStatus.INACTIVE)

    # Wait a bit for pending requests
    await asyncio.sleep(5)

    # Deregister
    await client.deregister_agent(agent_id)

    # Close connection
    await client.close()
```

### 4. Error Handling | معالجة الأخطاء

Always handle connection errors:

```python
try:
    await client.register_agent(agent)
except Exception as e:
    logger.error(f"Failed to register agent: {e}")
    # Retry logic or fallback
```

## Integration with Agents | التكامل مع الوكلاء

### Example Agent with Registry | مثال وكيل مع السجل

```python
from multi_agent.infrastructure import (
    AgentRegistryClient,
    AgentCard,
    AgentCapability,
    AgentStatus,
)

class DiseaseExpertAgent:
    def __init__(self):
        self.agent_id = "disease-expert"
        self.registry = AgentRegistryClient()

    async def start(self):
        """Start agent and register"""
        await self.registry.connect()

        # Create agent card
        card = AgentCard(
            agent_id=self.agent_id,
            name="Disease Expert",
            description="Disease diagnosis expert",
            description_ar="خبير تشخيص الأمراض",
            capabilities=[AgentCapability.DIAGNOSIS],
            model="claude-3-5-sonnet-20241022",
            endpoint=f"http://localhost:8112/agents/{self.agent_id}",
            status=AgentStatus.ACTIVE,
        )

        # Register
        await self.registry.register_agent(card)

        # Start heartbeat loop
        asyncio.create_task(self._heartbeat_loop())

    async def _heartbeat_loop(self):
        """Send periodic heartbeats"""
        while True:
            await self.registry.heartbeat(self.agent_id)
            await asyncio.sleep(300)  # 5 minutes

    async def stop(self):
        """Stop agent and deregister"""
        await self.registry.update_status(
            self.agent_id,
            AgentStatus.INACTIVE
        )
        await self.registry.deregister_agent(self.agent_id)
        await self.registry.close()
```

## Monitoring | المراقبة

### Health Checks | فحوصات الصحة

```python
async def check_registry_health(client):
    """Check registry health"""
    stats = await client.get_registry_stats()

    # Alert if no active agents
    if stats['status_distribution']['active'] == 0:
        logger.warning("No active agents in registry!")

    # Alert if average performance is low
    if stats['average_performance'] < 0.7:
        logger.warning(f"Low average performance: {stats['average_performance']}")
```

## Testing | الاختبار

See `registry_example.py` for a complete usage example.

```bash
# Run example
python -m multi_agent.infrastructure.registry_example
```

## Troubleshooting | استكشاف الأخطاء

### Connection Issues | مشاكل الاتصال

```python
# Check Redis connection
try:
    await client.connect()
except Exception as e:
    print(f"Redis connection failed: {e}")
    # Check redis_url configuration
```

### Cache Issues | مشاكل التخزين المؤقت

```python
# Clear cache if stale data
client._invalidate_cache()
```

### Missing Agents | وكلاء مفقودون

```python
# Check if agent exists
agent = await client.get_agent("agent-id")
if not agent:
    print("Agent not found - may have expired")
    # Re-register agent
```

## References | المراجع

- [A2A Protocol Specification](https://github.com/a2a-protocol/spec)
- [Redis Python Documentation](https://redis-py.readthedocs.io/)
- [SAHOOL Multi-Agent Architecture](../../../docs/multi-agent-architecture.md)

## Support | الدعم

For issues or questions:
- GitHub Issues: [sahool-unified-v15-idp/issues](https://github.com/sahool/sahool-unified-v15-idp/issues)
- Documentation: [docs.sahool.app](https://docs.sahool.app)
