# Emergency Response Agent Documentation
# وثائق وكيل الاستجابة للطوارئ

## Overview | نظرة عامة

The Emergency Response Agent is a specialized AI agent designed for rapid agricultural crisis management within the SAHOOL multi-agent system. It provides fast, coordinated responses to agricultural emergencies with support for damage assessment, resource optimization, multi-agent coordination, and recovery monitoring.

وكيل الاستجابة للطوارئ هو وكيل ذكاء اصطناعي متخصص مصمم لإدارة الأزمات الزراعية السريعة ضمن نظام SAHOOL متعدد الوكلاء. يوفر استجابات سريعة ومنسقة للطوارئ الزراعية مع دعم تقييم الأضرار وتحسين الموارد والتنسيق متعدد الوكلاء ومراقبة التعافي.

## Features | الميزات

### Core Capabilities | القدرات الأساسية

- **⚡ Fast Response**: < 5 seconds for initial emergency assessment
- **🌍 Bilingual Support**: All messages in Arabic and English
- **🤖 Multi-Agent Coordination**: Seamless integration with specialized agents
- **📊 Damage Estimation**: Comprehensive financial and crop loss calculations
- **📄 Insurance Documentation**: Automated claim package generation
- **📈 Recovery Monitoring**: Track recovery progress and adapt strategies
- **🎯 Resource Optimization**: Prioritize actions based on constraints
- **📚 Continuous Learning**: Extract lessons from each emergency

### Emergency Types Handled | أنواع الطوارئ المعالجة

| Type | Code | Description (EN) | Description (AR) |
|------|------|------------------|------------------|
| 🏜️ | `DROUGHT` | Water scarcity crisis | أزمة ندرة المياه |
| 🌊 | `FLOOD` | Excess water/waterlogging | المياه الزائدة/التشبع بالمياه |
| ❄️ | `FROST` | Frost damage risk | خطر أضرار الصقيع |
| 🔥 | `HEAT_WAVE` | Extreme heat stress | إجهاد حراري شديد |
| 🐛 | `PEST_OUTBREAK` | Severe pest infestation | غزو آفات شديد |
| 🦠 | `DISEASE_EPIDEMIC` | Rapid disease spread | انتشار سريع للأمراض |
| 🌨️ | `HAIL_DAMAGE` | Post-hail recovery | التعافي بعد البرد |
| 🔥 | `FIRE_RISK` | Wildfire threats | تهديدات الحرائق |

### Severity Levels | مستويات الشدة

| Level | Description (EN) | Description (AR) | Response Time |
|-------|------------------|------------------|---------------|
| `LOW` | Monitoring required | مطلوب مراقبة | Scheduled |
| `MODERATE` | Action recommended | إجراء موصى به | 24-48 hours |
| `HIGH` | Immediate action needed | حاجة لإجراء فوري | Within hours |
| `CRITICAL` | Emergency response | استجابة طوارئ | Immediate |

## Architecture | البنية

```
EmergencyResponseAgent
├── Emergency Assessment (< 5s)
│   ├── Field data analysis
│   ├── Severity classification
│   └── Bilingual alerting
│
├── Response Planning
│   ├── Immediate actions (0-1h)
│   ├── Short-term actions (1-24h)
│   ├── Medium-term actions (1-7d)
│   └── Long-term recovery (1-4w)
│
├── Resource Optimization
│   ├── Action prioritization
│   ├── Budget allocation
│   ├── Time constraints
│   └── Resource efficiency
│
├── Multi-Agent Coordination
│   ├── Agent assignment
│   ├── Information sharing
│   ├── Conflict resolution
│   └── Synchronized execution
│
├── Damage & Recovery
│   ├── Crop damage estimation
│   ├── Financial impact analysis
│   ├── Recovery monitoring
│   └── Insurance documentation
│
└── Learning & Improvement
    ├── Lessons learned analysis
    ├── Performance metrics
    └── Knowledge base updates
```

## API Reference | مرجع API

### Class: `EmergencyResponseAgent`

Extends: `BaseAgent`

#### Constructor

```python
agent = EmergencyResponseAgent(
    tools: Optional[List[Tool]] = None,
    retriever: Optional[Any] = None
)
```

#### Methods | الطرق

##### 1. `assess_emergency()`

Rapid emergency assessment (target < 5 seconds).

```python
assessment = await agent.assess_emergency(
    emergency_type: str,           # e.g., "drought", "flood"
    field_data: Dict[str, Any],    # Field conditions and sensor data
    severity: Optional[str] = None # Override severity: "low", "moderate", "high", "critical"
) -> Dict[str, Any]
```

**Returns:**
```python
{
    "emergency_id": str,           # Unique emergency identifier
    "emergency_type": str,         # Type of emergency
    "severity": str,               # Severity level
    "alert_en": str,               # English alert message
    "alert_ar": str,               # Arabic alert message
    "assessment": str,             # Detailed assessment
    "response_time_seconds": float,# Response time
    "within_target": bool,         # Met 5s target?
    "timestamp": str               # ISO timestamp
}
```

**Example:**
```python
field_data = {
    "field_id": "FIELD-001",
    "crop_type": "wheat",
    "soil_moisture": 12,
    "temperature": 42
}

assessment = await agent.assess_emergency(
    emergency_type="drought",
    field_data=field_data
)

print(assessment['alert_ar'])  # Arabic alert
print(f"Severity: {assessment['severity']}")
```

##### 2. `create_response_plan()`

Create comprehensive emergency response action plan.

```python
plan = await agent.create_response_plan(
    emergency_type: str,
    assessment: Dict[str, Any]
) -> Dict[str, Any]
```

**Returns:**
```python
{
    "emergency_id": str,
    "plan": str,              # Detailed action plan
    "created_at": str         # ISO timestamp
}
```

**Plan Structure:**
- Immediate actions (0-1 hours)
- Short-term actions (1-24 hours)
- Medium-term actions (1-7 days)
- Long-term actions (1-4 weeks)

##### 3. `prioritize_actions()`

Prioritize emergency actions based on resources and time constraints.

```python
prioritized = await agent.prioritize_actions(
    actions: List[Dict[str, Any]],
    resources: Dict[str, Any],
    time_constraint: Optional[int] = None  # Hours
) -> Dict[str, Any]
```

**Example:**
```python
actions = [
    {"action": "Emergency irrigation", "cost": 5000, "time_hours": 2},
    {"action": "Apply mulch", "cost": 2000, "time_hours": 8}
]

resources = {
    "budget_sar": 8000,
    "water_m3": 500,
    "labor_hours": 16
}

result = await agent.prioritize_actions(
    actions=actions,
    resources=resources,
    time_constraint=12
)
```

##### 4. `coordinate_response()`

Coordinate emergency response with multiple specialized agents.

```python
coordination = await agent.coordinate_response(
    plan: Dict[str, Any],
    available_agents: List[str]
) -> Dict[str, Any]
```

**Available Agents:**
- `irrigation_advisor` - Water management
- `pest_management` - Pest control
- `disease_expert` - Disease management
- `soil_science` - Soil recovery
- `field_analyst` - Damage assessment
- `ecological_expert` - Environmental impact
- `market_intelligence` - Economic analysis
- `yield_predictor` - Crop loss estimation

**Example:**
```python
coordination = await agent.coordinate_response(
    plan=response_plan,
    available_agents=["irrigation_advisor", "soil_science", "yield_predictor"]
)
```

##### 5. `monitor_recovery()`

Monitor recovery progress after emergency.

```python
recovery = await agent.monitor_recovery(
    field_id: str,
    emergency_type: str
) -> Dict[str, Any]
```

**Returns:**
```python
{
    "field_id": str,
    "emergency_type": str,
    "recovery_status": str,    # Detailed status
    "monitored_at": str        # ISO timestamp
}
```

##### 6. `estimate_damage()`

Estimate damage and losses from emergency.

```python
damage = await agent.estimate_damage(
    emergency_type: str,
    affected_area: float,      # Hectares
    crop_data: Dict[str, Any]
) -> Dict[str, Any]
```

**Crop Data Fields:**
```python
crop_data = {
    "crop": "wheat",
    "area_hectares": 50,
    "growth_stage": "grain_filling",
    "expected_yield_tons": 150,
    "market_price_sar_per_ton": 1200,
    "investment_to_date": 180000
}
```

**Returns:**
```python
{
    "emergency_type": str,
    "affected_area_hectares": float,
    "damage_estimate": str,    # Detailed estimate
    "estimated_at": str
}
```

##### 7. `insurance_documentation()`

Generate insurance documentation for claims.

```python
insurance_docs = await agent.insurance_documentation(
    emergency_data: Dict[str, Any]
) -> Dict[str, Any]
```

**Returns:**
```python
{
    "insurance_package": str,  # Complete documentation
    "emergency_reference": str,
    "generated_at": str,
    "languages": ["English", "Arabic"]
}
```

**Documentation Includes:**
- Incident report
- Damage documentation
- Financial breakdown
- Preventive measures taken
- Expert assessments
- Claim requirements checklist

##### 8. `lessons_learned()`

Post-emergency analysis and lessons learned.

```python
lessons = await agent.lessons_learned(
    emergency_id: str
) -> Dict[str, Any]
```

**Returns:**
```python
{
    "emergency_id": str,
    "lessons_learned": str,    # Comprehensive analysis
    "analyzed_at": str,
    "status": "complete"
}
```

**Analysis Covers:**
- Response effectiveness
- Damage analysis
- Coordination assessment
- Recovery insights
- Prevention opportunities
- Knowledge transfer
- Recommendations

#### Utility Methods | الطرق المساعدة

##### `get_active_emergencies()`

Get all active emergencies being tracked.

```python
active = agent.get_active_emergencies()
# Returns: Dict[str, Dict[str, Any]]
```

##### `clear_emergency()`

Mark emergency as resolved and remove from active tracking.

```python
success = agent.clear_emergency(emergency_id="drought_20231215_143022")
# Returns: bool
```

## Usage Examples | أمثلة الاستخدام

### Example 1: Quick Drought Assessment

```python
from src.agents.emergency_response_agent import EmergencyResponseAgent

async def handle_drought():
    agent = EmergencyResponseAgent()

    # Field conditions
    field_data = {
        "field_id": "FIELD-001",
        "crop_type": "wheat",
        "soil_moisture": 12,  # Critical
        "temperature": 42
    }

    # Rapid assessment
    assessment = await agent.assess_emergency(
        emergency_type="drought",
        field_data=field_data
    )

    print(f"Severity: {assessment['severity']}")
    print(f"Alert (AR): {assessment['alert_ar']}")
    print(f"Response time: {assessment['response_time_seconds']:.2f}s")
```

### Example 2: Complete Emergency Workflow

```python
async def complete_emergency_workflow():
    agent = EmergencyResponseAgent()

    # 1. Assess
    assessment = await agent.assess_emergency(
        emergency_type="flood",
        field_data={"water_level_cm": 25, "crop_type": "vegetables"}
    )

    # 2. Plan
    plan = await agent.create_response_plan(
        emergency_type="flood",
        assessment=assessment
    )

    # 3. Prioritize
    actions = [...]  # Define actions
    resources = {...}  # Define resources
    prioritized = await agent.prioritize_actions(actions, resources, time_constraint=12)

    # 4. Coordinate
    coordination = await agent.coordinate_response(
        plan=plan,
        available_agents=["irrigation_advisor", "soil_science"]
    )

    # 5. Estimate Damage
    damage = await agent.estimate_damage(
        emergency_type="flood",
        affected_area=10.0,
        crop_data={...}
    )

    # 6. Insurance
    insurance = await agent.insurance_documentation(
        emergency_data={
            "emergency_id": assessment['emergency_id'],
            "damage_estimate": damage,
            ...
        }
    )

    # 7. Monitor Recovery
    recovery = await agent.monitor_recovery(
        field_id="FIELD-001",
        emergency_type="flood"
    )

    # 8. Analyze
    lessons = await agent.lessons_learned(
        emergency_id=assessment['emergency_id']
    )
```

### Example 3: Multi-Agent Coordination for Pest Outbreak

```python
async def handle_pest_outbreak():
    agent = EmergencyResponseAgent()

    assessment = await agent.assess_emergency(
        emergency_type="pest_outbreak",
        field_data={
            "pest_type": "whitefly",
            "infestation_percentage": 75,
            "spread_rate": "rapid"
        }
    )

    # Create comprehensive response plan
    plan = await agent.create_response_plan(
        emergency_type="pest_outbreak",
        assessment=assessment
    )

    # Coordinate with specialized agents
    coordination = await agent.coordinate_response(
        plan=plan,
        available_agents=[
            "pest_management",      # Primary agent for pest control
            "ecological_expert",    # Assess environmental impact
            "disease_expert",       # Check for disease complications
            "field_analyst"         # Monitor spread
        ]
    )

    print("Multi-agent response coordinated successfully!")
```

## Integration with SAHOOL System | التكامل مع نظام SAHOOL

### 1. Weather Service Integration

The agent integrates with weather services for:
- Real-time weather data
- Frost warnings
- Heat wave predictions
- Rainfall forecasts

### 2. IoT Sensor Integration

Receives real-time data from:
- Soil moisture sensors
- Temperature sensors
- Humidity sensors
- Water level monitors
- Weather stations

### 3. Alert Service Integration

Sends bilingual alerts through:
- SMS notifications
- Email alerts
- Mobile app push notifications
- Dashboard alerts

### 4. Database Integration

Stores and retrieves:
- Emergency history
- Response effectiveness metrics
- Recovery timelines
- Insurance claims
- Lessons learned

## Performance Metrics | مقاييس الأداء

### Response Time Targets

| Operation | Target | Typical |
|-----------|--------|---------|
| Emergency Assessment | < 5s | 2-3s |
| Response Plan Creation | < 30s | 15-20s |
| Action Prioritization | < 10s | 5-8s |
| Multi-Agent Coordination | < 20s | 10-15s |
| Damage Estimation | < 30s | 20-25s |

### Success Criteria

- ✅ Assessment accuracy > 90%
- ✅ Response time within target
- ✅ Resource optimization > 85%
- ✅ Multi-agent coordination success > 95%
- ✅ Recovery tracking accuracy > 90%

## Best Practices | أفضل الممارسات

### 1. Field Data Quality

Provide comprehensive field data:
```python
field_data = {
    "field_id": "FIELD-001",         # Required
    "location": "Region",            # Recommended
    "crop_type": "wheat",            # Required
    "growth_stage": "flowering",     # Required
    "area_hectares": 50,             # Required for damage estimation

    # Include relevant sensor data
    "soil_moisture": 12,
    "temperature": 42,
    "humidity": 15,

    # Context information
    "last_irrigation": "3_days_ago",
    "irrigation_system": "drip"
}
```

### 2. Severity Assessment

Let the agent infer severity unless you have specific requirements:
```python
# Preferred - let agent determine severity
assessment = await agent.assess_emergency(
    emergency_type="drought",
    field_data=field_data
)

# Override only when necessary
assessment = await agent.assess_emergency(
    emergency_type="frost",
    field_data=field_data,
    severity="critical"  # Manual override
)
```

### 3. Resource Specification

Be specific about available resources:
```python
resources = {
    "budget_sar": 50000,              # Total budget
    "water_m3": 2000,                 # Available water
    "labor_hours": 40,                # Labor capacity
    "equipment": [                     # Available equipment
        "drip_irrigation",
        "sprinklers",
        "weather_station"
    ],
    "materials": {                     # Available materials
        "fertilizer_kg": 500,
        "pesticides_liters": 100
    }
}
```

### 4. Multi-Agent Selection

Choose agents based on emergency type:

```python
# Drought/Flood
agents = ["irrigation_advisor", "soil_science", "yield_predictor"]

# Pest/Disease
agents = ["pest_management", "disease_expert", "ecological_expert"]

# Weather Events (Frost/Heat)
agents = ["field_analyst", "irrigation_advisor", "yield_predictor"]

# Comprehensive
agents = [
    "irrigation_advisor",
    "pest_management",
    "disease_expert",
    "soil_science",
    "field_analyst",
    "ecological_expert",
    "market_intelligence",
    "yield_predictor"
]
```

## Error Handling | معالجة الأخطاء

```python
from src.agents.emergency_response_agent import EmergencyResponseAgent
import structlog

logger = structlog.get_logger()

async def safe_emergency_handling():
    agent = EmergencyResponseAgent()

    try:
        assessment = await agent.assess_emergency(
            emergency_type="drought",
            field_data=field_data
        )

    except ValueError as e:
        logger.error("invalid_emergency_type", error=str(e))
        # Handle invalid emergency type

    except Exception as e:
        logger.error("emergency_assessment_failed", error=str(e))
        # Handle general errors
        # Escalate to manual intervention if needed
```

## Logging and Monitoring | التسجيل والمراقبة

The agent uses structured logging:

```python
# Automatic logging events
logger.info("emergency_assessed",
    emergency_id=emergency_id,
    emergency_type=emergency_type,
    severity=severity,
    response_time=response_time
)

logger.info("multi_agent_coordination_created",
    num_agents=len(available_agents)
)

logger.info("emergency_resolved",
    emergency_id=emergency_id
)
```

## Testing | الاختبار

Run the comprehensive example suite:

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/ai-advisor
python3 examples/emergency_response_example.py
```

This will run:
- Drought emergency example
- Flood emergency example
- Pest outbreak example
- Frost alert example
- Lessons learned example
- Comprehensive scenario

## Future Enhancements | التحسينات المستقبلية

- [ ] Real-time satellite imagery integration
- [ ] Predictive emergency detection using ML
- [ ] Automated drone deployment coordination
- [ ] Community emergency response network
- [ ] Historical emergency pattern analysis
- [ ] Climate change adaptation strategies
- [ ] Mobile app for field workers
- [ ] Voice-based emergency reporting (Arabic/English)

## Support | الدعم

For issues or questions:
- File an issue in the repository
- Contact the SAHOOL development team
- Consult the main SAHOOL documentation

## License | الترخيص

Part of the SAHOOL Unified Agricultural Platform.

---

**Version**: 1.0.0
**Last Updated**: December 2024
**Maintained by**: SAHOOL Development Team
