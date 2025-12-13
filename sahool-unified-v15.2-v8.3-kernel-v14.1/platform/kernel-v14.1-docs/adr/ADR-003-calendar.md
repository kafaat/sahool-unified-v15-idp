# ADR-003: Yemeni Agricultural Calendar System

## Status
Accepted

## Date
2025-01-01

## Context

Traditional Yemeni agriculture relies on a stellar calendar system that:
1. Tracks 28 agricultural stars (منازل القمر)
2. Varies by region (المرتفعات، تهامة، حضرموت)
3. Contains centuries of accumulated wisdom in proverbs
4. Guides planting, irrigation, and harvesting decisions

This traditional knowledge is:
- Orally transmitted (at risk of being lost)
- Highly accurate for local conditions
- Not digitized in any existing platform
- A **unique competitive advantage**

## Decision

**Implement the Yemeni Astronomical Calendar as a Knowledge Signal System**

### Core Design

```yaml
Calendar as Signal Producer:
  Service: astro-agri-service
  Layer: 2 (Signal Producer)
  
  Responsibilities:
    - Track current star position
    - Emit events on star transitions
    - Provide relevant proverbs
    - Apply regional variations
  
  Events Produced:
    - astro.star.rising
    - astro.star.setting
    - astro.season.entered
    - astro.planting.window
    - astro.proverb.triggered
```

### Data Model

```sql
-- 28 Stars
agricultural_stars:
  - id: star_alab
  - name_ar: العلب
  - start_day_of_year: 197  -- Reference: docs/calendar/ASSUMPTIONS.md
  - duration_days: 13
  - season: خريف

-- Regional Variations
star_regional_variations:
  - star_id: star_alab
  - region: تهامة
  - calendar_type: الواسعي
  - offset_days: -4  -- 4 days earlier than highlands

-- Folk Proverbs
folk_proverbs:
  - text: "ما قيظ إلا قيظ العلب"
  - meaning: "الذرة تتحمل العطش إلا في العلب"
  - reliability_score: 0.90  -- For AI weighting
```

### Calendar Reference System

```yaml
Base Calendar: التقويم الحميري العنسي
Day 1 Reference: January 1 (Gregorian)
Year Length: 365 days (366 leap)

Regional Offsets:
  المرتفعات (Highlands): 0 days (reference)
  تهامة (Tihama): -4 days
  حضرموت (Hadramout): +3 days

See: docs/calendar/ASSUMPTIONS.md
```

### Integration with Modern Agriculture

```
Traditional Input          Modern Processing          Output
────────────────          ─────────────────          ──────
نجم العلب rising     →    crop-lifecycle analyzes  →  task.created
                          weather signals               "حرث الجنيد"
                          NDVI data
                          
مثل "ثورك والعلب"   →    advisor-core references  →  recommendation
                          scientific best practices    with cultural context
```

## Consequences

### Positive
- ✅ Preserves endangered traditional knowledge
- ✅ Unique feature no competitor offers
- ✅ Resonates deeply with Yemeni farmers
- ✅ Combines tradition with modern precision
- ✅ reliability_score enables AI learning

### Negative
- ❌ Requires expert validation of calendar data
- ❌ Regional variations add complexity
- ❌ Proverbs need careful translation

### Mitigations
- Partner with agricultural heritage experts
- Start with المرتفعات, expand to other regions
- Build feedback loop to improve reliability_score

## Technical Details

### Scheduler Implementation

```python
# Daily check at midnight
async def check_star_transitions():
    current_star = await get_current_star(region)
    
    if is_star_transition_day(current_star):
        await publish_event(
            EventTypes.ASTRO_STAR_RISING,
            payload={
                "star": current_star,
                "region": region,
                "proverbs": await get_star_proverbs(current_star.id)
            }
        )
```

### Leap Year Handling

```python
from datetime import date, timedelta

def get_star_for_date(target_date: date, region: str) -> Star:
    day_of_year = target_date.timetuple().tm_yday
    offset = get_regional_offset(region)
    adjusted_day = day_of_year - offset
    
    return find_star_by_day(adjusted_day)
```

## Related
- docs/calendar/ASSUMPTIONS.md
- data/seeds/01_stars.sql
- data/seeds/02_proverbs.sql
- services/astro-agri/
