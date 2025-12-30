# Council and Consensus System Documentation
# توثيق نظام المجلس والإجماع

## Overview | نظرة عامة

The Council and Consensus System is a sophisticated framework for multi-agent collaborative decision-making in the SAHOOL agricultural intelligence platform. It enables multiple AI agents with different expertise to collaborate, debate, and reach consensus on complex agricultural decisions.

نظام المجلس والإجماع هو إطار عمل متطور لاتخاذ القرارات التعاونية متعددة الوكلاء في منصة SAHOOL للذكاء الزراعي. يمكّن وكلاء الذكاء الاصطناعي المتعددين بخبرات مختلفة من التعاون والنقاش والوصول إلى إجماع بشأن القرارات الزراعية المعقدة.

## Architecture | البنية المعمارية

The system consists of two main components:

### 1. Council Manager (`council_manager.py`)
Orchestrates agent councils and manages the decision-making process.

**Key Classes:**
- `CouncilManager`: Main orchestrator for council meetings
- `AgentOpinion`: Represents a single agent's opinion
- `CouncilDecision`: Final consensus decision
- `Conflict`: Represents disagreements between agents
- `CouncilType`: Enum of different council types

### 2. Consensus Engine (`consensus_engine.py`)
Implements various consensus algorithms for aggregating agent opinions.

**Key Classes:**
- `ConsensusEngine`: Applies different consensus strategies
- `ConsensusStrategy`: Enum of available strategies

---

## Council Types | أنواع المجالس

### 1. DIAGNOSIS_COUNCIL | مجلس التشخيص
**Purpose:** Disease and pest diagnosis
**Participating Agents:** Disease experts, pest control experts, ecological experts
**Use Case:** "What disease is affecting my tomato plants?"

```python
decision = await council_manager.convene_council(
    council_type=CouncilType.DIAGNOSIS_COUNCIL,
    query="Diagnose disease from symptoms",
    agents=[disease_expert, pest_expert, eco_expert],
    consensus_strategy=ConsensusStrategy.EXPERTISE_WEIGHTED
)
```

### 2. TREATMENT_COUNCIL | مجلس العلاج
**Purpose:** Treatment planning and strategy
**Participating Agents:** Treatment specialists, agronomists, organic experts
**Use Case:** "What treatment should we apply for early blight?"

```python
decision = await council_manager.convene_council(
    council_type=CouncilType.TREATMENT_COUNCIL,
    query="Recommend treatment for early blight",
    agents=[disease_expert, fertilizer_expert, eco_expert],
    consensus_strategy=ConsensusStrategy.WEIGHTED_CONFIDENCE
)
```

### 3. RESOURCE_COUNCIL | مجلس الموارد
**Purpose:** Water and fertilizer optimization
**Participating Agents:** Irrigation advisors, fertilizer experts, soil analysts
**Use Case:** "How should we optimize irrigation for this field?"

### 4. EMERGENCY_COUNCIL | مجلس الطوارئ
**Purpose:** Crisis response and urgent decisions
**Participating Agents:** All available experts
**Use Case:** "Severe pest outbreak - immediate action needed"
**Recommended Strategy:** `UNANIMOUS` for critical decisions

### 5. SUSTAINABILITY_COUNCIL | مجلس الاستدامة
**Purpose:** Ecological and sustainability decisions
**Participating Agents:** Ecological experts, climate specialists, organic advisors
**Use Case:** "How can we improve farm sustainability?"

---

## Consensus Strategies | استراتيجيات الإجماع

### 1. MAJORITY_VOTE | التصويت بالأغلبية
Simple majority wins. Best for straightforward decisions.

**Formula:** Most common recommendation
**Confidence:** (vote_ratio × 0.6) + (avg_agent_confidence × 0.4)

**When to use:**
- Simple yes/no decisions
- When all agents have equal expertise
- Quick decisions needed

```python
consensus_strategy=ConsensusStrategy.MAJORITY_VOTE
```

### 2. WEIGHTED_CONFIDENCE | الثقة المرجحة
Weights recommendations by agent confidence scores.

**Formula:** Weighted sum of confidence scores
**Confidence:** (weight_ratio × 0.7) + (agent_ratio × 0.3)

**When to use:**
- Agents have varying confidence levels
- Need to factor in uncertainty
- Default strategy for most cases

```python
consensus_strategy=ConsensusStrategy.WEIGHTED_CONFIDENCE
```

### 3. EXPERTISE_WEIGHTED | الخبرة المرجحة
Weights by agent expertise in the specific domain.

**Formula:** confidence × expertise_weight
**Expertise Weights:**
- Disease Expert: 1.5
- Irrigation Advisor: 1.3
- Ecological Expert: 1.4
- Fertilizer Expert: 1.3
- Default: 1.0

**When to use:**
- Specialized domain decisions
- Some agents are more qualified
- Medical/diagnostic decisions

```python
consensus_strategy=ConsensusStrategy.EXPERTISE_WEIGHTED,
context={'expertise_weights': {'custom_agent': 1.6}}
```

### 4. UNANIMOUS | الإجماع الكامل
Requires all agents to agree.

**When to use:**
- Critical safety decisions
- Emergency responses
- High-stakes situations

**Fallback:** If unanimous agreement not reached, falls back to MAJORITY_VOTE with reduced confidence.

```python
consensus_strategy=ConsensusStrategy.UNANIMOUS
```

### 5. SUPERMAJORITY | الأغلبية العظمى
Requires 2/3 or more agreement.

**Default Threshold:** 66.7% (2/3)
**Fallback:** WEIGHTED_CONFIDENCE if threshold not met

**When to use:**
- Important but not critical decisions
- Policy changes
- Resource allocation

```python
consensus_strategy=ConsensusStrategy.SUPERMAJORITY,
context={'supermajority_threshold': 0.75}  # 75% threshold
```

### 6. BAYESIAN | البايزي
Bayesian belief aggregation using probability theory.

**Formula:** P(recommendation | evidence) ∝ P(evidence | recommendation) × P(recommendation)

**When to use:**
- Statistical decision-making
- Multiple evidence sources
- Probabilistic reasoning

```python
consensus_strategy=ConsensusStrategy.BAYESIAN
```

### 7. RANKED_CHOICE | الاختيار المصنف
Ranked choice voting with confidence as ranking.

**Formula:** Ranked_score = Σ(confidence²)

**When to use:**
- Multiple options to choose from
- Preference-based decisions
- Complex trade-offs

```python
consensus_strategy=ConsensusStrategy.RANKED_CHOICE
```

---

## Usage Examples | أمثلة الاستخدام

### Basic Council Example

```python
from multi_agent.orchestration import (
    CouncilManager,
    CouncilType,
    ConsensusStrategy
)

# Initialize
council_manager = CouncilManager()

# Prepare agents
agents = [disease_expert, pest_expert, eco_expert]

# Convene council
decision = await council_manager.convene_council(
    council_type=CouncilType.DIAGNOSIS_COUNCIL,
    query="What disease is affecting my crops?",
    agents=agents,
    context={'crop_type': 'tomato', 'symptoms': ['wilting', 'spots']},
    consensus_strategy=ConsensusStrategy.EXPERTISE_WEIGHTED,
    min_confidence=0.6
)

# Access results
print(f"Decision: {decision.decision}")
print(f"Confidence: {decision.confidence:.2f}")
print(f"Consensus Level: {decision.consensus_level:.2f}")
print(f"Supporting Agents: {len(decision.supporting_opinions)}")
print(f"Conflicts: {len(decision.conflicts)}")
```

### Comparing Strategies

```python
from multi_agent.orchestration import ConsensusEngine

engine = ConsensusEngine()

# Compare all strategies
results = engine.compare_strategies(opinions)

for strategy, result in results.items():
    print(f"{strategy.value}: {result['confidence']:.2f}")

# Get best strategy
best_strategy, best_result = engine.get_best_strategy(
    opinions,
    criteria='confidence'
)
```

### Handling Conflicts

```python
# Convene council
decision = await council_manager.convene_council(...)

# Check for conflicts
if decision.conflicts:
    print(f"⚠ {len(decision.conflicts)} conflicts detected")

    for conflict in decision.conflicts:
        print(f"Type: {conflict.conflict_type}")
        print(f"Severity: {conflict.severity:.2f}")
        print(f"Description: {conflict.description}")
        print(f"Suggestion: {conflict.resolution_suggestion}")
```

### Council History

```python
# Get all history
history = council_manager.get_council_history(limit=10)

# Filter by type
emergency_decisions = council_manager.get_council_history(
    council_type=CouncilType.EMERGENCY_COUNCIL,
    limit=5
)

# Clear history
council_manager.clear_history()
```

---

## Data Models | نماذج البيانات

### AgentOpinion

```python
@dataclass
class AgentOpinion:
    agent_id: str                    # Unique agent identifier
    agent_type: str                  # Agent role/expertise
    recommendation: str              # The agent's recommendation
    confidence: float                # 0-1 confidence score
    evidence: List[str]              # Supporting evidence
    dissenting_points: List[str]     # Concerns or caveats
    reasoning: str                   # Detailed reasoning
    metadata: Dict[str, Any]         # Additional data
    timestamp: datetime              # When opinion was given
```

### CouncilDecision

```python
@dataclass
class CouncilDecision:
    decision: str                    # Final consensus decision
    confidence: float                # Overall confidence (0-1)
    consensus_level: float           # Agreement level (0-1)
    participating_agents: List[str]  # All agent IDs
    supporting_opinions: List[AgentOpinion]   # Agreeing opinions
    dissenting_opinions: List[AgentOpinion]   # Disagreeing opinions
    resolution_notes: str            # Conflict resolution notes
    conflicts: List[Conflict]        # Identified conflicts
    council_type: CouncilType        # Type of council
    consensus_strategy: ConsensusStrategy  # Strategy used
    metadata: Dict[str, Any]         # Additional data
    timestamp: datetime              # Decision timestamp
```

### Conflict

```python
@dataclass
class Conflict:
    conflicting_agents: List[str]    # IDs of conflicting agents
    conflict_type: str               # "recommendation", "evidence", etc.
    description: str                 # What the conflict is about
    severity: float                  # 0-1 severity score
    resolution_suggestion: str       # How to resolve it
```

---

## Best Practices | أفضل الممارسات

### 1. Choosing the Right Strategy

| Scenario | Recommended Strategy |
|----------|---------------------|
| Medical diagnosis | EXPERTISE_WEIGHTED |
| Emergency response | UNANIMOUS |
| Resource optimization | WEIGHTED_CONFIDENCE |
| General decision | MAJORITY_VOTE |
| Statistical analysis | BAYESIAN |
| Multiple options | RANKED_CHOICE |

### 2. Minimum Confidence Thresholds

- **Critical decisions:** min_confidence=0.8
- **Important decisions:** min_confidence=0.7
- **General decisions:** min_confidence=0.6
- **Exploratory:** min_confidence=0.5

### 3. Handling Low Consensus

```python
if decision.consensus_level < 0.5:
    # Low consensus - consider:
    # 1. Gathering more information
    # 2. Consulting additional experts
    # 3. Using a different strategy
    # 4. Escalating to human review

    logger.warning(
        "low_consensus_detected",
        level=decision.consensus_level,
        conflicts=len(decision.conflicts)
    )
```

### 4. Context Matters

Always provide rich context to help agents make informed decisions:

```python
context = {
    'crop_type': 'tomato',
    'growth_stage': 'flowering',
    'symptoms': ['wilting', 'yellow spots'],
    'weather': {'temp': 28, 'humidity': 85},
    'soil_data': {...},
    'history': [...],
    'farmer_preferences': {'organic_only': True}
}
```

---

## Integration with Master Advisor | التكامل مع المستشار الرئيسي

The Council system integrates seamlessly with the MasterAdvisor:

```python
from multi_agent.orchestration import MasterAdvisor, CouncilManager

class EnhancedMasterAdvisor(MasterAdvisor):
    def __init__(self):
        super().__init__()
        self.council_manager = CouncilManager()

    async def handle_complex_query(self, query: str, agents: List):
        # Use council for complex decisions
        decision = await self.council_manager.convene_council(
            council_type=self._determine_council_type(query),
            query=query,
            agents=agents,
            consensus_strategy=self._select_strategy(query)
        )

        return decision
```

---

## Performance Considerations | اعتبارات الأداء

### Parallel Opinion Collection
Opinions are collected in parallel for better performance:

```python
# Opinions collected concurrently
opinions = await council_manager.collect_opinions(agents, query)
```

### Caching Decisions
Consider caching council decisions for similar queries:

```python
# Check cache first
cached = cache.get(query_hash)
if cached and is_recent(cached):
    return cached

# Otherwise, convene council
decision = await council_manager.convene_council(...)
cache.set(query_hash, decision)
```

### Agent Selection
Only select relevant agents for each council type:

```python
# Don't include all agents
relevant_agents = agent_registry.get_agents_for_council_type(
    council_type=CouncilType.DIAGNOSIS_COUNCIL
)
```

---

## Testing | الاختبار

Run the examples:

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/ai-advisor
python -m src.multi_agent.orchestration.council_example
```

Run unit tests:

```bash
pytest tests/multi_agent/test_council_manager.py
pytest tests/multi_agent/test_consensus_engine.py
```

---

## Error Handling | معالجة الأخطاء

```python
try:
    decision = await council_manager.convene_council(...)
except ValueError as e:
    # Invalid input parameters
    logger.error("invalid_council_params", error=str(e))
except Exception as e:
    # Unexpected error
    logger.error("council_failed", error=str(e), exc_info=True)
    # Provide fallback decision
    decision = create_fallback_decision()
```

---

## Logging | تسجيل السجلات

The system uses structured logging with `structlog`:

```python
import structlog

logger = structlog.get_logger()

# Logs include:
# - council_convened
# - opinions_collected
# - consensus_result
# - conflict_resolution_completed
# - council_decision_reached
```

---

## Future Enhancements | التحسينات المستقبلية

1. **Machine Learning Integration**: Learn optimal strategies from historical decisions
2. **Real-time Collaboration**: Live agent debates with streaming
3. **Explainability**: Detailed explanations of consensus process
4. **Multi-round Deliberation**: Iterative refinement of decisions
5. **Stakeholder Input**: Incorporate farmer preferences and constraints
6. **Federated Learning**: Privacy-preserving consensus across farms

---

## Support | الدعم

For questions or issues:
- Documentation: This README
- Examples: `council_example.py`
- Code: `council_manager.py`, `consensus_engine.py`
- Contact: SAHOOL Development Team

---

## License | الترخيص

Copyright © 2024 SAHOOL Agricultural Intelligence Platform

---

**Last Updated:** 2024-12-29
**Version:** 1.0.0
**Maintainer:** SAHOOL AI Team
