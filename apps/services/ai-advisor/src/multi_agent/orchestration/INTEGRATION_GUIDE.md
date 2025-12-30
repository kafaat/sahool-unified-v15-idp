# Council System Integration Guide
# دليل تكامل نظام المجلس

## Quick Start | البداية السريعة

### Installation | التثبيت

The Council and Consensus system is already integrated into the SAHOOL multi-agent framework. No additional installation required.

نظام المجلس والإجماع متكامل بالفعل في إطار عمل SAHOOL متعدد الوكلاء. لا يلزم تثبيت إضافي.

### Import | الاستيراد

```python
from multi_agent.orchestration import (
    CouncilManager,
    CouncilType,
    ConsensusStrategy,
    AgentOpinion,
    CouncilDecision,
)
```

---

## Integration Patterns | أنماط التكامل

### Pattern 1: Simple Council

**Use Case:** Quick decision with default settings

```python
from multi_agent.orchestration import CouncilManager, CouncilType

async def simple_diagnosis(query: str, agents: list):
    council = CouncilManager()

    decision = await council.convene_council(
        council_type=CouncilType.DIAGNOSIS_COUNCIL,
        query=query,
        agents=agents
    )

    return decision.decision
```

### Pattern 2: With Custom Strategy

**Use Case:** Specialized decision-making with expertise weighting

```python
from multi_agent.orchestration import (
    CouncilManager,
    CouncilType,
    ConsensusStrategy
)

async def expert_treatment_plan(query: str, agents: list, context: dict):
    council = CouncilManager()

    # Custom expertise weights for this domain
    context['expertise_weights'] = {
        'disease_expert': 1.8,      # High weight for disease expert
        'fertilizer_expert': 1.2,
        'irrigation_advisor': 1.0
    }

    decision = await council.convene_council(
        council_type=CouncilType.TREATMENT_COUNCIL,
        query=query,
        agents=agents,
        context=context,
        consensus_strategy=ConsensusStrategy.EXPERTISE_WEIGHTED,
        min_confidence=0.75
    )

    return decision
```

### Pattern 3: Emergency Response

**Use Case:** Critical decisions requiring unanimous agreement

```python
async def emergency_response(query: str, agents: list):
    council = CouncilManager()

    decision = await council.convene_council(
        council_type=CouncilType.EMERGENCY_COUNCIL,
        query=query,
        agents=agents,
        consensus_strategy=ConsensusStrategy.UNANIMOUS,
        min_confidence=0.85  # High threshold for emergencies
    )

    # Check if unanimous consensus was reached
    if decision.consensus_level < 1.0:
        # Escalate to human operator
        await escalate_to_human(decision)

    return decision
```

### Pattern 4: Strategy Comparison

**Use Case:** Compare multiple strategies and choose the best

```python
from multi_agent.orchestration import ConsensusEngine

async def adaptive_decision(opinions: list):
    engine = ConsensusEngine()

    # Compare all available strategies
    results = engine.compare_strategies(opinions)

    # Get the strategy with highest confidence
    best_strategy, best_result = engine.get_best_strategy(
        opinions,
        criteria='confidence'
    )

    logger.info(
        "best_strategy_selected",
        strategy=best_strategy.value,
        confidence=best_result['confidence']
    )

    return best_result
```

---

## Integration with Existing Agents | التكامل مع الوكلاء الحاليين

### Using with BaseAgent

All existing agents (DiseaseExpertAgent, IrrigationAdvisor, etc.) are compatible:

```python
from agents import (
    DiseaseExpertAgent,
    PestControlExpert,
    EcologicalExpertAgent
)
from multi_agent.orchestration import CouncilManager, CouncilType

async def diagnose_crop_issue(symptoms: dict, crop_type: str):
    # Initialize agents
    disease_expert = DiseaseExpertAgent()
    pest_expert = PestControlExpert()
    eco_expert = EcologicalExpertAgent()

    agents = [disease_expert, pest_expert, eco_expert]

    # Create council
    council = CouncilManager()

    # Convene for diagnosis
    decision = await council.convene_council(
        council_type=CouncilType.DIAGNOSIS_COUNCIL,
        query=f"Diagnose issue with {crop_type}",
        agents=agents,
        context={'symptoms': symptoms, 'crop_type': crop_type}
    )

    return {
        'diagnosis': decision.decision,
        'confidence': decision.confidence,
        'supporting_agents': [op.agent_id for op in decision.supporting_opinions],
        'conflicts': [c.description for c in decision.conflicts]
    }
```

### Integration with MasterAdvisor

Enhance the MasterAdvisor with council capabilities:

```python
from multi_agent.orchestration import MasterAdvisor, CouncilManager, CouncilType

class EnhancedMasterAdvisor(MasterAdvisor):
    def __init__(self):
        super().__init__()
        self.council_manager = CouncilManager()

    async def process_query(self, query: str, query_type: str):
        # Get relevant agents
        agents = await self.select_agents(query, query_type)

        # Determine if council is needed
        if self._requires_council(query_type):
            council_type = self._map_to_council_type(query_type)

            decision = await self.council_manager.convene_council(
                council_type=council_type,
                query=query,
                agents=agents,
                consensus_strategy=self._select_strategy(query_type)
            )

            return self._format_response(decision)
        else:
            # Single agent response
            return await agents[0].think(query)

    def _requires_council(self, query_type: str) -> bool:
        """Determine if query needs multi-agent council"""
        complex_types = [
            'diagnosis',
            'treatment_planning',
            'emergency',
            'resource_optimization'
        ]
        return query_type in complex_types

    def _map_to_council_type(self, query_type: str) -> CouncilType:
        """Map query type to council type"""
        mapping = {
            'diagnosis': CouncilType.DIAGNOSIS_COUNCIL,
            'treatment_planning': CouncilType.TREATMENT_COUNCIL,
            'emergency': CouncilType.EMERGENCY_COUNCIL,
            'water_management': CouncilType.RESOURCE_COUNCIL,
            'sustainability': CouncilType.SUSTAINABILITY_COUNCIL,
        }
        return mapping.get(query_type, CouncilType.DIAGNOSIS_COUNCIL)

    def _select_strategy(self, query_type: str) -> ConsensusStrategy:
        """Select appropriate consensus strategy"""
        if query_type == 'emergency':
            return ConsensusStrategy.UNANIMOUS
        elif query_type in ['diagnosis', 'treatment_planning']:
            return ConsensusStrategy.EXPERTISE_WEIGHTED
        else:
            return ConsensusStrategy.WEIGHTED_CONFIDENCE
```

---

## API Endpoints | نقاط النهاية

### REST API Integration

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from multi_agent.orchestration import CouncilManager, CouncilType, ConsensusStrategy

router = APIRouter()

class CouncilRequest(BaseModel):
    query: str
    council_type: str
    agent_ids: list[str]
    context: dict = {}
    strategy: str = "weighted_confidence"

class CouncilResponse(BaseModel):
    decision: str
    confidence: float
    consensus_level: float
    supporting_agents: list[str]
    conflicts: list[dict]

@router.post("/api/v1/council/convene", response_model=CouncilResponse)
async def convene_council(request: CouncilRequest):
    """
    Convene a council of agents to make a decision
    عقد مجلس من الوكلاء لاتخاذ قرار
    """
    try:
        # Get agents by IDs
        agents = await get_agents_by_ids(request.agent_ids)

        # Map string to enum
        council_type = CouncilType[request.council_type.upper()]
        strategy = ConsensusStrategy[request.strategy.upper()]

        # Create council
        council = CouncilManager()

        # Convene
        decision = await council.convene_council(
            council_type=council_type,
            query=request.query,
            agents=agents,
            context=request.context,
            consensus_strategy=strategy
        )

        # Format response
        return CouncilResponse(
            decision=decision.decision,
            confidence=decision.confidence,
            consensus_level=decision.consensus_level,
            supporting_agents=[op.agent_id for op in decision.supporting_opinions],
            conflicts=[
                {
                    'type': c.conflict_type,
                    'description': c.description,
                    'severity': c.severity
                }
                for c in decision.conflicts
            ]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Message Queue Integration | تكامل قائمة انتظار الرسائل

### NATS Integration

```python
from multi_agent.infrastructure import AgentNATSBridge
from multi_agent.orchestration import CouncilManager, CouncilType

class CouncilNATSHandler:
    def __init__(self):
        self.bridge = AgentNATSBridge()
        self.council = CouncilManager()

    async def handle_council_request(self, msg):
        """Handle council request from NATS"""
        data = json.loads(msg.data.decode())

        query = data['query']
        council_type = CouncilType[data['council_type']]
        agent_ids = data['agent_ids']

        # Get agents
        agents = await self.get_agents(agent_ids)

        # Convene council
        decision = await self.council.convene_council(
            council_type=council_type,
            query=query,
            agents=agents
        )

        # Publish result
        await self.bridge.publish(
            subject=f"council.result.{msg.reply}",
            data=decision.get_summary()
        )

    async def subscribe(self):
        """Subscribe to council requests"""
        await self.bridge.subscribe(
            subject="council.request.*",
            handler=self.handle_council_request
        )
```

---

## Testing | الاختبار

### Unit Tests

```python
import pytest
from multi_agent.orchestration import (
    CouncilManager,
    CouncilType,
    AgentOpinion,
    ConsensusStrategy
)

@pytest.mark.asyncio
async def test_council_basic():
    """Test basic council functionality"""
    council = CouncilManager()

    # Create mock agents
    agents = [MockAgent("agent1"), MockAgent("agent2")]

    decision = await council.convene_council(
        council_type=CouncilType.DIAGNOSIS_COUNCIL,
        query="Test query",
        agents=agents
    )

    assert decision is not None
    assert decision.confidence > 0
    assert len(decision.participating_agents) == 2

@pytest.mark.asyncio
async def test_consensus_strategies():
    """Test different consensus strategies"""
    opinions = [
        AgentOpinion(
            agent_id="agent1",
            agent_type="expert",
            recommendation="Option A",
            confidence=0.9
        ),
        AgentOpinion(
            agent_id="agent2",
            agent_type="expert",
            recommendation="Option A",
            confidence=0.8
        )
    ]

    engine = ConsensusEngine()

    result = engine.apply_strategy(
        opinions,
        strategy=ConsensusStrategy.MAJORITY_VOTE
    )

    assert result['decision'] == "Option A"
    assert result['confidence'] > 0.7
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_full_integration():
    """Test full integration with real agents"""
    from agents import DiseaseExpertAgent

    agent = DiseaseExpertAgent()
    council = CouncilManager()

    decision = await council.convene_council(
        council_type=CouncilType.DIAGNOSIS_COUNCIL,
        query="Diagnose tomato disease",
        agents=[agent],
        context={'crop_type': 'tomato'}
    )

    assert decision is not None
    assert 'tomato' in decision.decision.lower()
```

---

## Performance Optimization | تحسين الأداء

### 1. Agent Selection

Only select necessary agents:

```python
def select_relevant_agents(query_type: str, all_agents: list):
    """Select only agents relevant to query type"""
    relevance_map = {
        'diagnosis': ['disease_expert', 'pest_expert', 'eco_expert'],
        'irrigation': ['irrigation_advisor', 'weather_analyst'],
        'treatment': ['disease_expert', 'fertilizer_expert', 'eco_expert']
    }

    relevant_types = relevance_map.get(query_type, [])
    return [a for a in all_agents if a.name in relevant_types]
```

### 2. Caching

Cache council decisions:

```python
from functools import lru_cache
import hashlib

class CachedCouncilManager(CouncilManager):
    def __init__(self):
        super().__init__()
        self.cache = {}

    def _cache_key(self, query: str, agents: list) -> str:
        """Generate cache key"""
        agent_ids = sorted([a.name for a in agents])
        content = f"{query}:{'|'.join(agent_ids)}"
        return hashlib.md5(content.encode()).hexdigest()

    async def convene_council(self, **kwargs):
        """Cached council convening"""
        cache_key = self._cache_key(kwargs['query'], kwargs['agents'])

        if cache_key in self.cache:
            cached_decision, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).seconds < 3600:  # 1 hour cache
                return cached_decision

        # Not cached or expired
        decision = await super().convene_council(**kwargs)

        # Cache it
        self.cache[cache_key] = (decision, datetime.now())

        return decision
```

### 3. Parallel Processing

Process opinions in parallel:

```python
import asyncio

async def collect_opinions_parallel(agents, query, context):
    """Collect opinions in parallel"""
    tasks = [
        agent.think(query, context=context, use_rag=True)
        for agent in agents
    ]

    responses = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out exceptions
    valid_responses = [
        r for r in responses
        if not isinstance(r, Exception)
    ]

    return valid_responses
```

---

## Monitoring and Logging | المراقبة والتسجيل

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

# Log council activity
logger.info(
    "council_convened",
    council_type=council_type.value,
    num_agents=len(agents),
    strategy=strategy.value
)

logger.info(
    "council_decision_reached",
    confidence=decision.confidence,
    consensus_level=decision.consensus_level,
    conflicts=len(decision.conflicts)
)
```

### Metrics

Track key metrics:

```python
from prometheus_client import Counter, Histogram

council_requests = Counter(
    'council_requests_total',
    'Total council requests',
    ['council_type', 'strategy']
)

council_confidence = Histogram(
    'council_confidence',
    'Council decision confidence',
    ['council_type']
)

# Usage
council_requests.labels(
    council_type='diagnosis',
    strategy='expertise_weighted'
).inc()

council_confidence.labels(
    council_type='diagnosis'
).observe(decision.confidence)
```

---

## Error Handling | معالجة الأخطاء

### Graceful Degradation

```python
async def safe_council_decision(query: str, agents: list):
    """Council with fallback to single agent"""
    try:
        council = CouncilManager()
        decision = await council.convene_council(
            council_type=CouncilType.DIAGNOSIS_COUNCIL,
            query=query,
            agents=agents,
            min_confidence=0.6
        )

        # Check confidence
        if decision.confidence < 0.5:
            logger.warning(
                "low_confidence_decision",
                confidence=decision.confidence
            )
            # Escalate or request more information

        return decision

    except Exception as e:
        logger.error("council_failed", error=str(e))

        # Fallback to single expert agent
        if agents:
            response = await agents[0].think(query)
            return create_decision_from_response(response)

        raise
```

---

## Summary | الملخص

The Council and Consensus system provides:

1. **Multiple Council Types** for different scenarios
2. **7 Consensus Strategies** for various decision-making needs
3. **Conflict Detection and Resolution**
4. **Comprehensive Logging and Monitoring**
5. **Easy Integration** with existing agents and systems

Start with simple patterns and gradually adopt more advanced features as needed.

ابدأ بأنماط بسيطة واعتمد تدريجياً ميزات أكثر تقدماً حسب الحاجة.

---

**For more information:**
- Full Documentation: `COUNCIL_SYSTEM_README.md`
- Examples: `council_example.py`
- Source Code: `council_manager.py`, `consensus_engine.py`
