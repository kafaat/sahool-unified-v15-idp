# SAHOOL Skills CLI - Real-World Examples

دليل الأمثلة العملية لأداة اختبار مهارات سهول

This document contains practical, production-ready examples for using the SAHOOL Skills CLI tool.

## Table of Contents

1. [Agricultural Advisory Scenarios](#agricultural-advisory-scenarios)
2. [Farm History Management](#farm-history-management)
3. [Data Compression for Offline Sync](#data-compression-for-offline-sync)
4. [Quality Assurance Workflows](#quality-assurance-workflows)
5. [Integration Examples](#integration-examples)

---

## Agricultural Advisory Scenarios

### Scenario 1: Irrigation Advisory for Wheat Field

**Situation**: Farmer Ahmed has a wheat field at tillering stage. Soil moisture is 38%, weather forecast shows 5 days without rain, and ET is 5.8mm/day.

#### Step 1: Store Field Observation

```bash
python scripts/skills_cli.py remember \
  --tenant-id farm_rashid \
  --field-id field_003_north_wheat \
  --type observation \
  --json '{
    "crop_stage": "tillering",
    "issue": "low_soil_moisture",
    "soil_moisture_percent": 38,
    "threshold_percent": 40,
    "et_mm_per_day": 5.8,
    "weather_forecast": "no_rain_5_days",
    "inspection_date": "2025-01-13",
    "inspector": "field_officer_001"
  }' \
  --output /tmp/observation_soil_moisture.json
```

**Output:**
```json
{
  "id": "obs-2025-001",
  "tenant_id": "farm_rashid",
  "field_id": "field_003_north_wheat",
  "memory_type": "observation",
  "content": {...},
  "timestamp": "2025-01-13T10:30:00",
  "language": "en"
}
```

#### Step 2: Compress Advisory for Transmission

Since the farmer has limited connectivity, compress the advisory before sending:

```bash
python scripts/skills_cli.py compress \
  --json '{
    "field_id": "F003",
    "field_name": "North Wheat Field",
    "area_hectares": 8.5,
    "crop": "wheat",
    "variety": "Sakha-95",
    "current_stage": "Zadoks-25 (main shoot and 5 tillers)",
    "soil_moisture": 38,
    "threshold": 40,
    "et_rate": 5.8,
    "weather_forecast": "Clear, no rain 5 days",
    "irrigation_system": "center_pivot_8_5ha",
    "soil_type": "clay_loam",
    "ph": 7.2
  }' \
  --level light \
  --output /tmp/field_data_compressed.json
```

**Output:**
```json
{
  "compression_ratio": 0.65,
  "tokens_saved": 35,
  "savings_percentage": 35.0,
  "original_tokens": 100,
  "compressed_tokens": 65
}
```

#### Step 3: Generate and Evaluate Advisory

```bash
python scripts/skills_cli.py evaluate \
  --type irrigation \
  --text "Soil moisture is 38%, below critical threshold of 40% for wheat at tillering stage. \
With 5-day dry forecast and ET of 5.8mm/day, water stress is imminent. \
RECOMMENDATION: Irrigate immediately (within 24 hours). \
Volume: 500 m³/ha using center pivot system. \
Timing: Early morning (6-8 AM) to minimize evaporation. \
Target: Bring soil moisture to 55% (field capacity). \
Method: Run center pivot at 50% speed for approximately 4 hours. \
Important: Avoid evening irrigation to prevent foliar disease. \
Monitor: Re-check soil moisture in 7 days." \
  --context '{
    "field_id": "F003",
    "crop": "wheat",
    "stage": "tillering_zadoks_25",
    "soil_moisture": 38,
    "threshold": 40,
    "et": 5.8,
    "rain_forecast": "0mm_5_days",
    "equipment": "center_pivot",
    "soil_type": "clay_loam",
    "field_size": 8.5
  }' \
  --output /tmp/irrigation_advisory_eval.json
```

**Evaluation Result:**
```json
{
  "advisory_id": "ADV-2025-001",
  "advisory_type": "irrigation",
  "overall_score": 4.2,
  "grade": "Good",
  "scores": {
    "accuracy": 4.5,
    "relevance": 4.5,
    "actionability": 4.0,
    "timeliness": 4.0,
    "safety": 3.5
  },
  "strengths": [
    "Specific water volume and timing",
    "Equipment-specific instructions",
    "Disease risk awareness",
    "Follow-up monitoring plan"
  ],
  "weaknesses": [
    "Could specify pivot speed percentage more clearly"
  ]
}
```

#### Step 4: Store Action Taken by Farmer

After farmer implements the recommendation:

```bash
python scripts/skills_cli.py remember \
  --tenant-id farm_rashid \
  --field-id field_003_north_wheat \
  --type action \
  --json '{
    "action": "irrigation",
    "applied_volume_m3_per_ha": 500,
    "system": "center_pivot",
    "start_time": "2025-01-14T07:15Z",
    "end_time": "2025-01-14T11:20Z",
    "duration_hours": 4.08,
    "water_source": "well_001",
    "operator": "Mohammed",
    "efficiency_percent": 92,
    "notes": "Applied as recommended. Water level good. No equipment issues.",
    "farmer_satisfaction": "satisfied"
  }' \
  --output /tmp/action_irrigation_applied.json
```

#### Step 5: Retrieve Complete Field History

Later, when planning the next action:

```bash
python scripts/skills_cli.py recall \
  --tenant-id farm_rashid \
  --field-id field_003_north_wheat \
  --limit 20 \
  --output /tmp/field_003_complete_history.json
```

**Result shows:**
- Observation: Low soil moisture detected
- Advisory: Irrigation recommended
- Action: Irrigation applied successfully
- Weather: No rain since advisory
- Next step: Schedule follow-up soil test

---

### Scenario 2: Nitrogen Deficiency Advisory in Arabic

**Situation**: Farmer sees yellowing in wheat field. Lab confirms nitrogen deficiency (18 ppm vs 25 ppm target).

#### Step 1: Store Observation with Photos

```bash
python scripts/skills_cli.py remember \
  --tenant-id farm_rashid \
  --field-id field_003_north_wheat \
  --type observation \
  --content "تم اكتشاف اصفرار في الأوراق في الزاوية الشرقية من الحقل. فحص التربة يؤكد نقص النيتروجين (18 جزء في المليون)." \
  --language ar \
  --output /tmp/observation_nitrogen_ar.json
```

#### Step 2: Evaluate Fertilizer Advisory (Bilingual)

```bash
python scripts/skills_cli.py evaluate \
  --type fertilizer \
  --text "الاصفرار المكتشف يشير إلى نقص النيتروجين، مؤكد بفحص التربة (18 جزء في المليون مقابل 25 المستهدف). \
التوصية: تطبيق اليوريا 46% بمعدل 46 كغ/هكتار كتسميد سطحي. \
التوقيت: الصباح عند وجود الندى لتحسين الامتصاص. \
الطريقة: نثر متساوٍ، تجنب التطبيق قبل الأمطار مباشرة. \
النتيجة المتوقعة: تخضير مرئي خلال 7-10 أيام. \
التكلفة: حوالي 100 ريال/هكتار. \
متابعة: إذا استمر الاصفرار بعد 14 يوم، طلب فحص تربة إضافي." \
  --context '{
    "field": "F003",
    "current_n_ppm": 18,
    "target_n_ppm": 25,
    "crop": "wheat",
    "stage": "tillering",
    "soil_test_date": "2025-01-10",
    "weather": "conditions_favorable"
  }' \
  --output /tmp/fertilizer_advisory_eval_ar.json
```

#### Step 3: Store in Arabic, Retrieve in Mixed Language

```bash
# Store recommendation in Arabic
python scripts/skills_cli.py remember \
  --tenant-id farm_rashid \
  --field-id field_003_north_wheat \
  --type recommendation \
  --content "تطبيق اليوريا بمعدل 46 كغ/هكتار في الصباح مع وجود الندى. التكلفة المتوقعة 100 ريال/هكتار." \
  --language ar

# Retrieve all field entries (mixed languages)
python scripts/skills_cli.py recall \
  --tenant-id farm_rashid \
  --field-id field_003_north_wheat \
  --limit 10 \
  --output /tmp/field_complete_history_mixed_lang.json
```

---

## Farm History Management

### Scenario 3: Complete Season Tracking

**Track a complete wheat season from planting to harvest.**

#### Planting

```bash
python scripts/skills_cli.py remember \
  --tenant-id farm_rashid \
  --field-id field_003_north_wheat \
  --type action \
  --json '{
    "event": "planting",
    "crop": "wheat",
    "variety": "Sakha-95",
    "planting_date": "2024-11-15",
    "seed_rate_kg_per_ha": 120,
    "method": "mechanical_drill",
    "operator": "Mohammed",
    "soil_moisture": "excellent",
    "weather": "clear_cool",
    "expected_emergence": "2024-11-22"
  }'
```

#### Growth Monitoring

```bash
# Week 2
python scripts/skills_cli.py remember \
  --tenant-id farm_rashid \
  --field-id field_003_north_wheat \
  --type observation \
  --json '{
    "date": "2024-11-22",
    "event": "emergence",
    "status": "uniform_emergence_observed",
    "plant_density": "320_plants_per_m2",
    "weather_since_planting": "favorable"
  }'

# Week 4 - First nitrogen application
python scripts/skills_cli.py remember \
  --tenant-id farm_rashid \
  --field-id field_003_north_wheat \
  --type action \
  --json '{
    "date": "2024-12-01",
    "event": "nitrogen_application_1",
    "product": "urea_46_percent",
    "rate_kg_per_ha": 50,
    "method": "broadcast",
    "operator": "Ahmed",
    "cost_sar": 850
  }'

# Week 6 - Booting stage observations
python scripts/skills_cli.py remember \
  --tenant-id farm_rashid \
  --field-id field_003_north_wheat \
  --type observation \
  --json '{
    "date": "2024-12-15",
    "event": "growth_stage_check",
    "zadoks_stage": 45,
    "growth_description": "boot_stage_boot_swollen",
    "plant_health": "good",
    "pest_observation": "none_detected"
  }'

# Week 8 - Second nitrogen application
python scripts/skills_cli.py remember \
  --tenant-id farm_rashid \
  --field-id field_003_north_wheat \
  --type action \
  --json '{
    "date": "2024-12-29",
    "event": "nitrogen_application_2",
    "rate_kg_per_ha": 50,
    "notes": "applied_before_heading_for_grain_quality"
  }'

# Week 14 - Heading
python scripts/skills_cli.py remember \
  --tenant-id farm_rashid \
  --field-id field_003_north_wheat \
  --type observation \
  --json '{
    "date": "2025-01-15",
    "event": "heading",
    "zadoks_stage": 55,
    "heading_completion_percent": 100,
    "grain_filling_stage": "early",
    "water_requirement": "moderate"
  }'

# Week 22 - Maturity
python scripts/skills_cli.py remember \
  --tenant-id farm_rashid \
  --field-id field_003_north_wheat \
  --type observation \
  --json '{
    "date": "2025-05-10",
    "event": "maturity",
    "zadoks_stage": 92,
    "grain_moisture": "25_percent",
    "color": "golden",
    "ready_for_harvest": "10_days"
  }'

# Harvest
python scripts/skills_cli.py remember \
  --tenant-id farm_rashid \
  --field-id field_003_north_wheat \
  --type action \
  --json '{
    "date": "2025-05-18",
    "event": "harvest",
    "total_production_tons": 35.7,
    "yield_t_per_ha": 4.2,
    "target_yield_t_per_ha": 4.0,
    "performance_percent": 105,
    "quality_grade": "A",
    "moisture_content_percent": 12.5,
    "protein_percent": 13.2,
    "test_weight_kg_hl": 78,
    "storage": "silo_001"
  }'
```

#### Season Summary

```bash
# Retrieve complete season history
python scripts/skills_cli.py recall \
  --tenant-id farm_rashid \
  --field-id field_003_north_wheat \
  --output /tmp/season_2024_2025_complete.json
```

---

## Data Compression for Offline Sync

### Scenario 4: Preparing Large Dataset for Offline Sync

Farmer is about to go offline for 3 days. Need to sync data efficiently.

#### Compress Field Summary

```bash
# Create comprehensive field summary
cat > /tmp/field_summary.json << 'EOF'
{
  "farm_id": "FARM-001",
  "farm_name": "Al-Rashid Farm",
  "location": {"lat": 24.7136, "lon": 46.6753, "region": "Riyadh"},
  "total_area_hectares": 45.5,
  "fields": [
    {
      "field_id": "F001",
      "name": "South Field",
      "area": 12.3,
      "current_crop": "barley",
      "variety": "Giza-126",
      "planting_date": "2024-11-20",
      "current_stage": "heading",
      "health_status": "good",
      "ndvi": 0.68,
      "soil_moisture": 45,
      "last_irrigation": "2025-01-10",
      "pest_status": "clear",
      "disease_status": "clear",
      "projected_yield": 3.8
    },
    {
      "field_id": "F003",
      "name": "North Wheat Field",
      "area": 8.5,
      "current_crop": "wheat",
      "variety": "Sakha-95",
      "planting_date": "2024-11-15",
      "current_stage": "grain_filling",
      "health_status": "good",
      "ndvi": 0.72,
      "soil_moisture": 38,
      "last_irrigation": "2025-01-14",
      "pest_status": "light_aphids_monitored",
      "disease_status": "clear",
      "projected_yield": 4.2
    },
    {
      "field_id": "F004",
      "name": "Date Palm Grove",
      "area": 4.2,
      "current_crop": "date_palm",
      "trees_count": 450,
      "variety": "Ajwa",
      "health_status": "good",
      "pest_status": "3_rpw_affected_treated",
      "treatment_status": "ongoing",
      "expected_harvest": "August_2025"
    }
  ],
  "equipment": [
    {"id": "TRACTOR-001", "type": "john_deere_7530", "status": "operational"},
    {"id": "PIVOT-001", "type": "center_pivot_8_5ha", "status": "operational"},
    {"id": "PIVOT-002", "type": "center_pivot_12_3ha", "status": "operational"}
  ],
  "water_sources": [
    {"id": "WELL-001", "type": "deep_well", "capacity_m3": 150, "current_level": 120}
  ],
  "recent_activities": [
    {"date": "2025-01-14", "activity": "irrigation_f003", "duration": "4_hours", "status": "completed"},
    {"date": "2025-01-12", "activity": "pest_scouting_all_fields", "status": "completed"},
    {"date": "2025-01-10", "activity": "soil_sampling_f003", "status": "completed"}
  ]
}
EOF

# Compress for offline sync
python scripts/skills_cli.py compress \
  --json "$(cat /tmp/field_summary.json)" \
  --level light \
  --output /tmp/farm_summary_for_offline.json

# Check compression efficiency
cat /tmp/farm_summary_for_offline.json | jq '{
  original_tokens,
  compressed_tokens,
  compression_ratio,
  savings_percentage
}'
```

**Result:**
```json
{
  "original_tokens": 520,
  "compressed_tokens": 416,
  "compression_ratio": 0.8,
  "savings_percentage": 20.0
}
```

#### Compress for Mobile App

For ultra-low bandwidth (2G/3G):

```bash
python scripts/skills_cli.py compress \
  --json "$(cat /tmp/field_summary.json)" \
  --level heavy \
  --output /tmp/farm_summary_ultra_light.json

cat /tmp/farm_summary_ultra_light.json | jq '.savings_percentage'
# Output: 72.5
```

---

## Quality Assurance Workflows

### Scenario 5: Batch Evaluation of Advisory Quality

QA team evaluates 10 advisories generated by the system in the past week.

#### Create Advisory Samples

```bash
cat > /tmp/advisories_for_qa.csv << 'EOF'
type,advisory_text,field,crop,stage
irrigation,Irrigate 500m³/ha tomorrow morning,F003,wheat,tillering
irrigation,Water the field with 450m³/ha,F001,barley,heading
fertilizer,Apply urea 46kg/ha,F003,wheat,tillering
fertilizer,Use NPK 20-20-20 at 100kg/ha,F001,barley,heading
pest,Spray for aphids if found,F003,wheat,grain_filling
pest,Apply imidacloprid for whitefly control,F002,vegetables,flowering
EOF
```

#### Evaluate Each Advisory

```bash
#!/bin/bash

# Create results directory
mkdir -p /tmp/qa_results

# Read CSV and evaluate
tail -n +2 /tmp/advisories_for_qa.csv | while IFS=',' read type text field crop stage; do
  python scripts/skills_cli.py evaluate \
    --type "$type" \
    --text "$text" \
    --context "{\"field\":\"$field\",\"crop\":\"$crop\",\"stage\":\"$stage\"}" \
    --output "/tmp/qa_results/eval_${type}_${field}.json"
done

# Generate summary report
echo "QA Evaluation Summary:"
echo "====================="
for file in /tmp/qa_results/*.json; do
  score=$(jq '.overall_score' "$file")
  grade=$(jq -r '.grade' "$file")
  type=$(jq -r '.advisory_type' "$file")
  printf "%-15s %-12s %s\n" "$type" "$grade" "$score/5.0"
done | sort | uniq -c
```

#### Identify Improvement Areas

```bash
# Find low-scoring advisories
echo "Advisories Below 3.5 Score:"
for file in /tmp/qa_results/*.json; do
  score=$(jq '.overall_score' "$file")
  if (( $(echo "$score < 3.5" | bc -l) )); then
    echo "File: $(basename $file)"
    jq '{overall_score, grade, weaknesses}' "$file"
  fi
done
```

---

## Integration Examples

### Scenario 6: Integration with External APIs

#### Upload Memory to Backend Server

```bash
# Create memory entry
python scripts/skills_cli.py remember \
  --tenant-id farm_001 \
  --field-id f003 \
  --type observation \
  --json '{"ndvi": 0.72, "moisture": 38}' \
  --output /tmp/memory.json

# Upload to API server
curl -X POST https://api.sahool.local/v1/memory \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d @/tmp/memory.json
```

#### Compress Before Sending to Limited Bandwidth Devices

```bash
# Get field data
FIELD_DATA=$(jq -c '.fields[0]' /tmp/field_summary.json)

# Compress for mobile
COMPRESSED=$(python scripts/skills_cli.py compress \
  --json "$FIELD_DATA" \
  --level heavy --json | jq -r '.compressed_text')

# Send to mobile device (only compressed data)
curl -X POST https://mobile.app/sync \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$COMPRESSED\",\"compressed\":true}"
```

#### Evaluate Advisory Before Sending to Farmer

```bash
# AI system generates advisory
ADVISORY="Soil moisture is 38%, apply 500m³/ha irrigation..."

# Evaluate quality first
python scripts/skills_cli.py evaluate \
  --type irrigation \
  --text "$ADVISORY" \
  --output /tmp/advisory_check.json

# Check if quality is acceptable
SCORE=$(jq '.overall_score' /tmp/advisory_check.json)
if (( $(echo "$SCORE >= 3.5" | bc -l) )); then
  # Send to farmer
  echo "$ADVISORY" | mail -s "Irrigation Advisory" farmer@email.com
else
  # Hold for manual review
  echo "Advisory quality too low: $SCORE/5"
  # Alert QA team
fi
```

### Scenario 7: Offline-First Mobile App Sync

Farmer uses app offline for 2 days, then syncs when back online.

```bash
#!/bin/bash

# On mobile device (offline):
# App stores local observations
python scripts/skills_cli.py remember \
  --tenant-id farm_001 \
  --field-id f003 \
  --type observation \
  --content "Wheat health looks good" \
  --output ~/app_data/local_memory_1.json

# When connectivity restored:
# Compress all local data
cat > /tmp/sync_bundle.json << 'EOF'
{
  "device_id": "mobile-app-01",
  "sync_timestamp": "2025-01-14T15:30:00Z",
  "entries": []
}
EOF

# Add compressed entries
for file in ~/app_data/local_memory_*.json; do
  COMPRESSED=$(python scripts/skills_cli.py compress \
    --json "$(cat $file)" \
    --level medium \
    --json | jq '.compressed_text')

  jq --arg entry "$COMPRESSED" \
    '.entries += [$entry]' /tmp/sync_bundle.json > /tmp/sync_bundle_temp.json
  mv /tmp/sync_bundle_temp.json /tmp/sync_bundle.json
done

# Send compressed bundle to server
curl -X POST https://api.sahool.local/v1/sync/upload \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DEVICE_TOKEN" \
  -d @/tmp/sync_bundle.json

echo "Sync completed successfully"
```

### Scenario 8: Building a Farm Dashboard

```bash
#!/bin/bash

# Collect data from all fields
python scripts/skills_cli.py recall \
  --tenant-id farm_001 \
  --limit 100 \
  --output /tmp/farm_data.json

# Create dashboard JSON
jq '{
  farm_id: "FARM-001",
  last_updated: now | strftime("%Y-%m-%d %H:%M:%S"),
  fields: [
    {
      field_id: "F001",
      name: "South Field",
      latest_ndvi: .entries[] | select(.memory_type == "observation") | .content.ndvi | last,
      latest_moisture: .entries[] | select(.memory_type == "observation") | .content.moisture | last,
      status: "healthy"
    },
    {
      field_id: "F003",
      name: "North Wheat",
      latest_ndvi: .entries[] | select(.memory_type == "observation") | .content.ndvi | last,
      latest_moisture: .entries[] | select(.memory_type == "observation") | .content.moisture | last,
      status: "under_observation"
    }
  ],
  total_entries: (.entries | length),
  data_freshness_hours: (now - (.entries[0].timestamp | fromdate) | . / 3600)
}' /tmp/farm_data.json > /tmp/dashboard.json

# Display dashboard
echo "Farm Dashboard - $(date)"
echo "========================================"
jq .fields[] /tmp/dashboard.json | jq -c '{field_id, name, status}'
```

---

## Best Practices

### 1. Always Compress Before Transmission

```bash
# For API calls - use compression
python scripts/skills_cli.py compress \
  --json "$(cat data.json)" \
  --level light  # For detailed info
  # or --level heavy for minimal data
```

### 2. Store Structured, Retrieve Flexible

```bash
# Store with rich metadata
python scripts/skills_cli.py remember \
  --tenant-id farm \
  --field-id field \
  --type observation \
  --json '{
    "metric_name": "soil_moisture",
    "value": 38,
    "unit": "percent",
    "measurement_date": "2025-01-14",
    "sensor_id": "SM-003-A"
  }'

# Retrieve and filter
python scripts/skills_cli.py recall --tenant-id farm --field-id field
```

### 3. Always Evaluate Before Deployment

```bash
# Before sending advisory to farmer
python scripts/skills_cli.py evaluate \
  --type [type] \
  --text "[advisory]" \
  # Check overall_score >= 3.5
```

### 4. Maintain Bilingual Records

```bash
# Store decisions in both languages
python scripts/skills_cli.py remember \
  --content "English advisory"
python scripts/skills_cli.py remember \
  --content "النصيحة باللغة العربية" \
  --language ar
```

---

## Troubleshooting Common Issues

### Issue: JSON Parse Error

```bash
# Solution: Use jq to validate
cat data.json | jq . > /dev/null && \
  python scripts/skills_cli.py compress --json "$(cat data.json)"
```

### Issue: Arabic Text Encoding

```bash
# Solution: Ensure UTF-8
export PYTHONIOENCODING=utf-8
python scripts/skills_cli.py remember --content "نص عربي"
```

### Issue: Large File Compression

```bash
# Solution: Use files instead of inline JSON
python scripts/skills_cli.py compress --json "$(cat large_file.json)"
# Or for huge files, use jq streaming
```

---

For more information, see `SKILLS_CLI_README.md`
