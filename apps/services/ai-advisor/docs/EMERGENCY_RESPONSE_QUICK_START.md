# Emergency Response Agent - Quick Start Guide
# دليل البدء السريع لوكيل الاستجابة للطوارئ

## 5-Minute Quick Start | البدء السريع في 5 دقائق

### 1. Import the Agent | استيراد الوكيل

```python
from src.agents.emergency_response_agent import (
    EmergencyResponseAgent,
    EmergencyType,
    SeverityLevel
)
```

### 2. Create Agent Instance | إنشاء مثيل الوكيل

```python
agent = EmergencyResponseAgent()
```

### 3. Handle an Emergency | التعامل مع طوارئ

```python
# Define field conditions | تحديد حالة الحقل
field_data = {
    "field_id": "FIELD-001",
    "crop_type": "wheat",
    "soil_moisture": 12,  # Critical level
    "temperature": 42
}

# Quick assessment (< 5 seconds) | تقييم سريع
assessment = await agent.assess_emergency(
    emergency_type=EmergencyType.DROUGHT.value,
    field_data=field_data
)

# Get bilingual alerts | الحصول على تنبيهات ثنائية اللغة
print(assessment['alert_en'])  # English
print(assessment['alert_ar'])  # Arabic
```

## Common Emergency Scenarios | سيناريوهات الطوارئ الشائعة

### Drought Emergency | طوارئ الجفاف

```python
field_data = {
    "crop_type": "wheat",
    "soil_moisture": 10,  # Very low
    "temperature": 43
}

assessment = await agent.assess_emergency("drought", field_data)
plan = await agent.create_response_plan("drought", assessment)
```

### Flood Emergency | طوارئ الفيضان

```python
field_data = {
    "crop_type": "vegetables",
    "water_level_cm": 30,  # Critical
    "soil_saturation": 95
}

assessment = await agent.assess_emergency("flood", field_data)
```

### Pest Outbreak | تفشي الآفات

```python
field_data = {
    "crop_type": "tomatoes",
    "pest_type": "whitefly",
    "infestation_percentage": 75  # Severe
}

assessment = await agent.assess_emergency("pest_outbreak", field_data)

# Coordinate with pest management agent
coordination = await agent.coordinate_response(
    plan=plan,
    available_agents=["pest_management", "ecological_expert"]
)
```

### Frost Alert | تنبيه الصقيع

```python
field_data = {
    "crop_type": "citrus",
    "temperature": 1,
    "forecast_min_temp": -3,
    "hours_until_frost": 6
}

assessment = await agent.assess_emergency("frost", field_data)

# Prioritize immediate protective actions
actions = [
    {"action": "Deploy wind machines", "cost": 8000, "time_hours": 2},
    {"action": "Activate sprinklers", "cost": 3000, "time_hours": 1}
]
prioritized = await agent.prioritize_actions(
    actions,
    resources={"budget_sar": 10000},
    time_constraint=6
)
```

## 8 Core Methods | 8 طرق أساسية

| Method | Purpose | Response Time |
|--------|---------|---------------|
| `assess_emergency()` | Rapid assessment | < 5 seconds |
| `create_response_plan()` | Action planning | ~ 15-20s |
| `prioritize_actions()` | Resource optimization | ~ 5-8s |
| `coordinate_response()` | Multi-agent coordination | ~ 10-15s |
| `monitor_recovery()` | Track progress | ~ 20-25s |
| `estimate_damage()` | Financial impact | ~ 20-25s |
| `insurance_documentation()` | Generate claims | ~ 15-20s |
| `lessons_learned()` | Post-analysis | ~ 20-25s |

## Complete Workflow Example | مثال سير العمل الكامل

```python
async def handle_complete_emergency():
    agent = EmergencyResponseAgent()

    # 1. ASSESS | تقييم
    assessment = await agent.assess_emergency(
        emergency_type="heat_wave",
        field_data={
            "temperature": 46,
            "crop_type": "wheat",
            "growth_stage": "grain_filling"
        }
    )

    # 2. PLAN | تخطيط
    plan = await agent.create_response_plan(
        "heat_wave",
        assessment
    )

    # 3. PRIORITIZE | تحديد الأولويات
    actions = [
        {"action": "Emergency irrigation", "cost": 15000, "time_hours": 3},
        {"action": "Apply anti-transpirants", "cost": 8000, "time_hours": 6}
    ]
    prioritized = await agent.prioritize_actions(
        actions,
        resources={"budget_sar": 20000, "water_m3": 2000},
        time_constraint=24
    )

    # 4. COORDINATE | تنسيق
    coordination = await agent.coordinate_response(
        plan,
        available_agents=["irrigation_advisor", "yield_predictor"]
    )

    # 5. ESTIMATE | تقدير
    damage = await agent.estimate_damage(
        "heat_wave",
        affected_area=50.0,
        crop_data={"crop": "wheat", "area_hectares": 50}
    )

    # 6. DOCUMENT | توثيق
    insurance = await agent.insurance_documentation({
        "emergency_id": assessment['emergency_id'],
        "damage_estimate": damage
    })

    # 7. MONITOR | مراقبة
    recovery = await agent.monitor_recovery(
        "FIELD-001",
        "heat_wave"
    )

    # 8. ANALYZE | تحليل
    lessons = await agent.lessons_learned(
        assessment['emergency_id']
    )

    # 9. RESOLVE | حل
    agent.clear_emergency(assessment['emergency_id'])
```

## Emergency Types Quick Reference | مرجع سريع لأنواع الطوارئ

```python
# Use these strings or enum values
EmergencyType.DROUGHT.value          # "drought" | الجفاف
EmergencyType.FLOOD.value            # "flood" | الفيضان
EmergencyType.FROST.value            # "frost" | الصقيع
EmergencyType.HEAT_WAVE.value        # "heat_wave" | موجة الحر
EmergencyType.PEST_OUTBREAK.value    # "pest_outbreak" | تفشي الآفات
EmergencyType.DISEASE_EPIDEMIC.value # "disease_epidemic" | وباء المرض
EmergencyType.HAIL_DAMAGE.value      # "hail_damage" | أضرار البرد
EmergencyType.FIRE_RISK.value        # "fire_risk" | خطر الحريق
```

## Severity Levels | مستويات الشدة

```python
SeverityLevel.LOW.value       # "low" | منخفض
SeverityLevel.MODERATE.value  # "moderate" | متوسط
SeverityLevel.HIGH.value      # "high" | عالي
SeverityLevel.CRITICAL.value  # "critical" | حرج
```

## Bilingual Alerts | التنبيهات ثنائية اللغة

Every emergency assessment returns bilingual alerts:

```python
assessment = await agent.assess_emergency("drought", field_data)

# English alert
print(assessment['alert_en'])
# Output: "DROUGHT ALERT: Water scarcity detected. Immediate irrigation optimization required."

# Arabic alert
print(assessment['alert_ar'])
# Output: "تنبيه الجفاف: تم اكتشاف ندرة المياه. مطلوب تحسين الري الفوري."
```

## Resource Specification | تحديد الموارد

```python
resources = {
    "budget_sar": 50000,              # Budget in Saudi Riyals
    "water_m3": 2000,                 # Water in cubic meters
    "labor_hours": 40,                # Available labor hours
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

## Multi-Agent Coordination | التنسيق متعدد الوكلاء

Select agents based on emergency type:

```python
# Water-related emergencies
agents = ["irrigation_advisor", "soil_science"]

# Pest/disease emergencies
agents = ["pest_management", "disease_expert", "ecological_expert"]

# Weather events
agents = ["field_analyst", "yield_predictor"]

# Comprehensive response
agents = [
    "irrigation_advisor",
    "pest_management",
    "disease_expert",
    "soil_science",
    "field_analyst",
    "yield_predictor",
    "market_intelligence"
]

coordination = await agent.coordinate_response(plan, agents)
```

## Active Emergency Tracking | تتبع الطوارئ النشطة

```python
# Get all active emergencies
active = agent.get_active_emergencies()
print(f"Active emergencies: {len(active)}")

# Check specific emergency
if emergency_id in active:
    status = active[emergency_id]['status']
    print(f"Status: {status}")

# Clear resolved emergency
agent.clear_emergency(emergency_id)
```

## Error Handling | معالجة الأخطاء

```python
try:
    assessment = await agent.assess_emergency(
        emergency_type="drought",
        field_data=field_data
    )
except ValueError as e:
    print(f"Invalid emergency type: {e}")
except Exception as e:
    print(f"Emergency assessment failed: {e}")
    # Escalate to manual intervention
```

## Testing | الاختبار

Run the comprehensive examples:

```bash
# Navigate to ai-advisor directory
cd /home/user/sahool-unified-v15-idp/apps/services/ai-advisor

# Run examples
python3 examples/emergency_response_example.py

# Run unit tests
pytest tests/unit/test_emergency_response_agent.py -v
```

## Performance Tips | نصائح الأداء

1. **Fast Assessment**: First call should be `assess_emergency()` for rapid triage
2. **Parallel Operations**: Can run damage estimation and insurance docs in parallel
3. **Resource Caching**: Reuse agent instance for multiple emergencies
4. **Severity Override**: Only override severity when you have specific requirements
5. **Agent Selection**: Choose minimal set of agents needed for coordination

## Common Patterns | الأنماط الشائعة

### Pattern 1: Quick Triage

```python
# For immediate decision making
assessment = await agent.assess_emergency(type, field_data)
if assessment['severity'] == 'critical':
    # Immediate action
    pass
```

### Pattern 2: Resource-Constrained Response

```python
# When budget/time is limited
prioritized = await agent.prioritize_actions(
    actions,
    resources={"budget_sar": 5000},
    time_constraint=6
)
```

### Pattern 3: Insurance Claim

```python
# For insurance purposes
assessment = await agent.assess_emergency(type, field_data)
damage = await agent.estimate_damage(type, area, crop_data)
insurance = await agent.insurance_documentation({
    "emergency_id": assessment['emergency_id'],
    "damage_estimate": damage,
    "field_data": field_data
})
```

### Pattern 4: Learning from Past Emergencies

```python
# Post-emergency improvement
lessons = await agent.lessons_learned(emergency_id)
# Use insights to update preparedness plans
```

## Need Help? | تحتاج مساعدة؟

- Full Documentation: `docs/EMERGENCY_RESPONSE_AGENT.md`
- Usage Examples: `examples/emergency_response_example.py`
- Unit Tests: `tests/unit/test_emergency_response_agent.py`
- SAHOOL Documentation: Main project README

---

**Quick Reference Card**

| Emergency | Field Data Keys | Severity Indicators |
|-----------|----------------|---------------------|
| Drought | `soil_moisture`, `temperature` | < 10% critical |
| Flood | `water_level_cm`, `soil_saturation` | > 30cm critical |
| Frost | `temperature`, `forecast_min_temp` | < -5°C critical |
| Heat Wave | `temperature`, `humidity` | > 45°C critical |
| Pest | `infestation_percentage` | > 70% critical |
| Disease | `infestation_percentage` | > 70% critical |

---

**Version**: 1.0.0
**Last Updated**: December 2024
**Language**: English / العربية
