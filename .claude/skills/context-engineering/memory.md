# Memory System Skill for Farm History

## Description

This skill enables persistent memory management for SAHOOL agricultural operations. It provides structured storage and retrieval of farm history, crop cycles, treatment records, yield data, and farmer preferences. Designed for offline-first environments with eventual synchronization, supporting Arabic/English bilingual agricultural knowledge.

## Instructions

### Memory Structure

Organize farm memory into hierarchical namespaces:

```
farm_memory/
├── entities/           # Farmers, farms, fields, equipment
├── events/             # Planting, harvesting, treatments
├── observations/       # Sensor readings, inspections, weather
├── decisions/          # Advisory given, actions taken
├── outcomes/           # Yields, quality, issues resolved
└── preferences/        # Farmer preferences, constraints
```

### Entity Memory Schema

#### Farm Entity
```yaml
entity_type: farm
id: FARM-001
name: Al-Rashid Farm | مزرعة الراشد
owner: Ahmed Al-Rashid | أحمد الراشد
location:
  coordinates: [lat, lon]
  region: Central | الوسطى
  governorate: Riyadh | الرياض
created: 2020-03-15
total_area: 45.5 ha
fields: [FIELD-001, FIELD-002, FIELD-003, FIELD-004, FIELD-005]
water_sources: [WELL-001]
equipment: [TRACTOR-001, PIVOT-001, PIVOT-002]
```

#### Field Entity
```yaml
entity_type: field
id: FIELD-003
farm_id: FARM-001
name: North Wheat Field | حقل القمح الشمالي
area: 8.5 ha
soil_type: clay_loam | طينية طميية
irrigation_type: center_pivot | محوري
boundary: [[lat1,lon1], [lat2,lon2], ...]
history:
  - season: 2024-winter
    crop: wheat
    variety: Sakha-95
    yield: 4.2 t/ha
  - season: 2024-summer
    status: fallow
  - season: 2023-winter
    crop: barley
    variety: Giza-126
    yield: 3.8 t/ha
```

### Event Memory Schema

#### Planting Event
```yaml
event_type: planting
id: EVT-2024-001
field_id: FIELD-003
timestamp: 2024-11-15T08:00:00Z
crop: wheat | قمح
variety: Sakha-95 | سخا 95
seed_rate: 120 kg/ha
method: drill | تسطير
operator: Mohammed | محمد
weather_conditions:
  temperature: 22
  humidity: 45
  wind: light
notes: Good soil moisture, optimal conditions | رطوبة جيدة، ظروف مثالية
```

#### Treatment Event
```yaml
event_type: treatment
id: EVT-2024-015
field_id: FIELD-003
timestamp: 2024-12-10T07:30:00Z
treatment_type: fertilizer | سماد
product: Urea 46% | يوريا
rate: 46 kg/ha
method: broadcast | نثر
target_issue: nitrogen_deficiency | نقص نيتروجين
weather_at_application:
  temperature: 15
  dew_present: true
cost: 850 SAR
operator: Ahmed | أحمد
```

#### Harvest Event
```yaml
event_type: harvest
id: EVT-2024-050
field_id: FIELD-003
start_date: 2024-05-18
end_date: 2024-05-20
crop: wheat | قمح
total_yield: 35.7 tons
yield_per_ha: 4.2 t/ha
moisture_content: 12.5%
quality_grade: A
storage_location: SILO-001
buyer: Grain Corp | شركة الحبوب
sale_price: 1850 SAR/ton
notes: Excellent quality, above average yield | جودة ممتازة، إنتاج فوق المتوسط
```

### Observation Memory Schema

#### Field Inspection
```yaml
observation_type: inspection
id: OBS-2025-012
field_id: FIELD-003
timestamp: 2025-01-10T09:00:00Z
inspector: Ahmed | أحمد
growth_stage: tillering | تفريع
zadoks_scale: 25
plant_population: 320 plants/m²
observations:
  - type: pest
    finding: aphid_presence
    severity: light
    location: eastern_border
    count: 12 per tiller
  - type: nutrient
    finding: yellowing
    severity: moderate
    location: eastern_corner
    suspected_cause: nitrogen_deficiency
photos: [IMG-2025-012-A.jpg, IMG-2025-012-B.jpg]
recommendations:
  - action: soil_test
    priority: high
  - action: monitor_aphids
    priority: medium
```

#### Sensor Reading (aggregated)
```yaml
observation_type: sensor_daily
id: OBS-SENSOR-2025-013
field_id: FIELD-003
date: 2025-01-13
soil_moisture:
  avg_10cm: 38.5
  avg_30cm: 42.1
  avg_60cm: 49.2
  trend: decreasing
soil_temperature:
  avg: 13.5
  min: 10.2
  max: 16.8
ec_avg: 1.85
ndvi: 0.72
ndvi_change: -0.03
```

### Decision Memory Schema

#### Advisory Decision
```yaml
decision_type: advisory
id: DEC-2025-005
field_id: FIELD-003
timestamp: 2025-01-13T10:00:00Z
context:
  soil_moisture: 38%
  nitrogen_level: 18 ppm
  growth_stage: tillering
  weather_forecast: dry_5days
recommendations:
  - action: irrigate
    urgency: high
    specification: 500 m³/ha within 24h
    rationale: SM below threshold, no rain forecast
  - action: fertilize
    urgency: high
    specification: Urea 46 kg/ha
    rationale: N deficiency confirmed by soil test
  - action: scout
    urgency: medium
    specification: daily aphid monitoring
    rationale: neighboring field infestation
farmer_response: accepted | مقبول
execution_date: 2025-01-14
```

### Outcome Memory Schema

#### Season Outcome
```yaml
outcome_type: season_summary
id: OUT-2024-W-003
field_id: FIELD-003
season: 2024-winter
crop: wheat
variety: Sakha-95
planting_date: 2024-11-15
harvest_date: 2024-05-20
total_days: 186
yield:
  actual: 4.2 t/ha
  target: 4.0 t/ha
  variance: +5%
quality:
  grade: A
  moisture: 12.5%
  protein: 13.2%
inputs:
  seed: 120 kg/ha | 1020 SAR
  fertilizer_n: 150 kg/ha | 2550 SAR
  fertilizer_p: 40 kg/ha | 680 SAR
  water: 4500 m³/ha | 900 SAR
  pesticides: 2 applications | 1200 SAR
total_cost: 6350 SAR/ha
revenue: 7770 SAR/ha
profit: 1420 SAR/ha
lessons_learned:
  - success: early_planting_optimal
  - issue: nitrogen_split_timing
  - recommendation: apply_n_earlier_next_season
```

### Preference Memory Schema

#### Farmer Preferences
```yaml
preference_type: farmer
farmer_id: FARMER-001
name: Ahmed Al-Rashid | أحمد الراشد
language: ar | العربية
notification_preferences:
  channels: [sms, app]
  timing: morning
  urgency_only: false
farming_preferences:
  organic_interest: low
  technology_adoption: high
  risk_tolerance: medium
  preferred_crops: [wheat, barley, date_palm]
  avoided_crops: [rice]
constraints:
  water_limit: 5000 m³/day
  labor_availability: limited_weekends
  budget_preference: minimize_upfront
advisory_style:
  detail_level: moderate
  include_costs: always
  compare_options: yes
historical_acceptance:
  irrigation_advice: 92%
  fertilizer_advice: 85%
  pest_control_advice: 78%
```

### Memory Retrieval Patterns

#### Query by Field History
```
QUERY: field_history(FIELD-003, last_3_seasons)
RETURNS: [planting, treatment, harvest events]
```

#### Query by Similar Conditions
```
QUERY: similar_situations(
  crop: wheat,
  stage: tillering,
  issue: aphid_infestation,
  severity: moderate
)
RETURNS: [past decisions, outcomes, effectiveness]
```

#### Query by Outcome Success
```
QUERY: successful_treatments(
  crop: wheat,
  issue: nitrogen_deficiency,
  min_yield_improvement: 10%
)
RETURNS: [treatment events with positive outcomes]
```

### Memory Update Protocol

1. **Immediate Write**: Alerts, treatments, critical observations
2. **Batch Write**: Sensor readings, routine inspections
3. **Season Write**: Yield outcomes, cost summaries, lessons learned
4. **Sync Priority**: Offline writes sync when connectivity restored

## Examples

### Example 1: Store New Treatment Event

**Input:**
```
Ahmed applied 46 kg/ha of urea to Field 003 this morning at 7:30 AM.
Dew was present and temperature was 14°C. This was to address the
nitrogen deficiency we identified last week. Cost was 850 SAR.
```

**Memory Write:**
```yaml
event_type: treatment
id: EVT-2025-003
field_id: FIELD-003
timestamp: 2025-01-14T07:30:00Z
treatment_type: fertilizer
product: Urea 46%
product_ar: يوريا 46%
rate: 46 kg/ha
method: broadcast
target_issue: nitrogen_deficiency
related_observation: OBS-2025-012
weather_at_application:
  temperature: 14
  dew_present: true
  conditions: optimal
cost: 850 SAR
operator: Ahmed
operator_ar: أحمد
status: completed
next_action:
  type: soil_retest
  date: 2025-01-28
  purpose: verify_n_recovery
```

### Example 2: Retrieve Field History for Advisory

**Query:**
```
Get complete history for FIELD-003 to inform current season advisory.
Include past 3 seasons, all treatments, and yield outcomes.
```

**Memory Retrieval:**
```yaml
field_history:
  field_id: FIELD-003
  name: North Wheat Field | حقل القمح الشمالي
  area: 8.5 ha

  seasons:
    - season: 2024-winter (current)
      crop: wheat
      variety: Sakha-95
      planted: 2024-11-15
      current_stage: tillering
      treatments_applied:
        - 2024-11-20: initial_irrigation
        - 2024-12-10: nitrogen_46kg/ha
        - 2025-01-14: nitrogen_46kg/ha (pending confirmation)
      issues_encountered:
        - 2025-01-08: nitrogen_deficiency_detected
        - 2025-01-10: aphid_light_infestation

    - season: 2024-summer
      status: fallow
      notes: soil_rest_period

    - season: 2023-winter
      crop: barley
      variety: Giza-126
      planted: 2023-11-10
      harvested: 2024-04-25
      yield: 3.8 t/ha
      quality: A
      issues: none_significant
      treatments: 3_irrigations, 2_fertilizer_applications
      profit: 1280 SAR/ha

    - season: 2023-summer
      crop: sorghum (silage)
      planted: 2023-06-01
      harvested: 2023-09-15
      yield: 45 t/ha (fresh)
      notes: good_rotation_crop

  patterns_identified:
    - wheat_performs_well_after_legume_or_fallow
    - field_tends_toward_n_deficiency_mid_season
    - aphid_pressure_typically_january_february

  recommendations_from_history:
    - split_nitrogen_into_3_applications
    - scout_for_aphids_from_december
    - consider_cover_crop_in_fallow_periods
```

### Example 3: Store Farmer Feedback on Advisory

**Input:**
```
Ahmed said he followed the irrigation advice but delayed the fertilizer
application by 3 days due to labor shortage. He prefers to receive
recommendations earlier in the week so he can plan labor.
```

**Memory Write:**
```yaml
feedback_type: advisory_response
id: FBK-2025-001
farmer_id: FARMER-001
advisory_id: DEC-2025-005
timestamp: 2025-01-17T10:00:00Z

actions_taken:
  - recommendation: irrigate
    status: completed
    timing: on_time
    notes: executed_as_advised
  - recommendation: fertilize
    status: completed
    timing: delayed_3_days
    reason: labor_shortage
    notes: applied_2025-01-17_instead_of_2025-01-14
  - recommendation: scout
    status: ongoing
    timing: as_advised
    notes: daily_morning_inspection

farmer_feedback:
  satisfaction: moderate
  suggestions:
    - earlier_notification: true
    - preferred_lead_time: 5_days
    - reason: labor_planning

preference_update:
  notification_timing: early_week
  lead_time_preference: 5_days_minimum
  labor_constraint: weekend_limited

lessons_for_system:
  - consider_labor_availability_in_timing
  - provide_5_day_advance_notice_when_possible
  - flag_weekend_treatments_as_potential_delay
```

### Example 4: Query Similar Historical Situations

**Query:**
```
Find past situations where wheat at tillering stage had aphid
infestation in this region. What treatments were used and
what were the outcomes?
```

**Memory Retrieval:**
```yaml
similar_situations:
  query_parameters:
    crop: wheat
    stage: tillering
    issue: aphid_infestation
    region: Central

  matches:
    - match_id: SIT-2023-015
      field: FIELD-007 (Al-Fahd Farm)
      date: 2023-01-22
      severity: moderate (25 aphids/tiller)
      treatment:
        product: Imidacloprid 20%
        rate: 100 ml/ha
        timing: immediate
      outcome:
        effectiveness: 95% reduction in 7 days
        yield_impact: none (treated early)
        cost: 450 SAR/ha
      lesson: early_treatment_prevents_yield_loss

    - match_id: SIT-2022-008
      field: FIELD-003 (same field)
      date: 2022-02-05
      severity: severe (40 aphids/tiller)
      treatment:
        product: Lambda-cyhalothrin
        rate: 200 ml/ha
        timing: delayed_5_days
      outcome:
        effectiveness: 80% reduction
        yield_impact: -8% estimated
        cost: 380 SAR/ha
      lesson: delayed_treatment_reduced_effectiveness

    - match_id: SIT-2024-003
      field: FIELD-002 (Al-Rashid Farm)
      date: 2024-01-18
      severity: light (15 aphids/tiller)
      treatment:
        product: none (below threshold)
        action: monitoring_only
      outcome:
        natural_control: beneficial_insects_appeared
        yield_impact: none
        cost: 0
      lesson: light_infestation_may_self_resolve

  recommendation_from_history:
    current_severity: light (12 aphids/tiller)
    suggested_action: monitor_daily_for_3_days
    threshold_for_spray: 25 aphids/tiller
    preferred_product: Imidacloprid (best_outcome_history)
    timing_critical: spray_within_48h_if_threshold_exceeded
```

### Example 5: Generate Season Summary Memory

**Input:**
After harvest completion, generate a season summary for FIELD-003.

**Memory Write:**
```yaml
outcome_type: season_summary
id: OUT-2025-W-003
field_id: FIELD-003
farm_id: FARM-001
farmer_id: FARMER-001

season_details:
  season: 2024-2025-winter
  crop: wheat | قمح
  variety: Sakha-95 | سخا 95

timeline:
  planting_date: 2024-11-15
  emergence_date: 2024-11-22
  tillering_start: 2024-12-15
  heading_date: 2025-03-12
  harvest_start: 2025-05-18
  harvest_end: 2025-05-20
  total_days: 186

yield_results:
  total_production: 35.7 tons
  yield_per_ha: 4.2 t/ha
  target_yield: 4.0 t/ha
  variance: +5%
  quality_grade: A
  moisture: 12.5%
  protein: 13.2%
  test_weight: 78 kg/hl

input_summary:
  seed:
    amount: 1020 kg (120 kg/ha)
    cost: 1020 SAR
  nitrogen:
    total: 1275 kg (150 kg/ha)
    applications: 3
    cost: 2550 SAR
  phosphorus:
    total: 340 kg (40 kg/ha)
    applications: 1
    cost: 680 SAR
  water:
    total: 38250 m³ (4500 m³/ha)
    irrigations: 12
    cost: 900 SAR
  pesticides:
    applications: 1 (aphid control)
    cost: 450 SAR
  labor:
    total_hours: 85
    cost: 1700 SAR

financial_summary:
  total_input_cost: 7300 SAR/ha
  total_revenue: 7770 SAR/ha (4.2t × 1850 SAR/t)
  gross_profit: 470 SAR/ha
  roi: 6.4%

issues_encountered:
  - issue: nitrogen_deficiency
    date_detected: 2025-01-08
    resolution: additional_urea_application
    impact: addressed_timely_no_yield_loss
  - issue: aphid_infestation
    date_detected: 2025-01-25
    resolution: imidacloprid_spray
    impact: controlled_within_threshold

lessons_learned:
  successes:
    - early_planting_optimal_for_yield
    - three_way_nitrogen_split_effective
    - prompt_pest_response_prevented_loss
  improvements_needed:
    - earlier_n_deficiency_detection
    - better_labor_planning_for_treatments
  recommendations_next_season:
    - start_nitrogen_monitoring_at_emergence
    - schedule_treatments_mid_week
    - consider_slow_release_n_fertilizer

comparison_to_history:
  vs_last_wheat_season: +10% yield
  vs_farm_average: +5% yield
  vs_regional_average: +12% yield

arabic_summary: |
  موسم القمح 2024-2025 - الحقل 003
  الإنتاج: 4.2 طن/هكتار (+5% عن المستهدف)
  الجودة: ممتازة (درجة أ)
  الربح: 470 ريال/هكتار
  الدروس: التسميد المبكر والمراقبة الدقيقة للآفات
```
