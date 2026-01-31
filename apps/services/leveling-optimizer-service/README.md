# Leveling Optimizer Service

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/kafaat/sahool)
[![Coverage](https://img.shields.io/badge/coverage-83%25-green)](https://github.com/kafaat/sahool)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)

## خدمة تحسين التسوية

> **Agricultural field leveling optimization service for cut/fill calculation, cost estimation, equipment recommendation, and leveling plan generation with support for multiple leveling methods.**

> **خدمة تحسين تسوية الأراضي الزراعية لحساب القطع والردم وتقدير التكاليف وتوصيات المعدات وإنشاء خطط التسوية مع دعم طرق تسوية متعددة.**

---

## Architecture | البنية المعمارية

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Leveling Optimizer Service                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Survey     │  │  Cut/Fill   │  │    Cost     │  │  Equipment  │        │
│  │  Input      │  │ Calculator  │  │  Estimator  │  │  Recommender│        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │               │
│  ┌──────┴────────────────┴────────────────┴────────────────┴──────┐        │
│  │                   Leveling Algorithms Engine                    │        │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │        │
│  │  │Single Plane │  │ Dual Plane  │  │  Contour    │             │        │
│  │  │  Method     │  │   Method    │  │   Method    │             │        │
│  │  └─────────────┘  └─────────────┘  └─────────────┘             │        │
│  └────────────────────────────────────────────────────────────────┘        │
│                              │                                             │
│  ┌───────────────────────────┴───────────────────────────────────┐        │
│  │                   Cost Database (SAR)                          │        │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │        │
│  │  │Equipment │  │  Labor   │  │   Fuel   │  │ Surveying│       │        │
│  │  │  Rates   │  │  Costs   │  │   Costs  │  │   Costs  │       │        │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │        │
│  └────────────────────────────────────────────────────────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Port | المنفذ

```
8170
```

---

## Features | الميزات

### Cut/Fill Calculation | حساب القطع والردم

- Volume calculation using grid or TIN methods
- Cut/fill balance ratio optimization
- Maximum and average depth analysis
- Area breakdown (cut vs. fill zones)
- Haul distance estimation

### Cost Estimation | تقدير التكاليف

- Equipment rental costs (جرافة، كاشطة، ممهدة، مسوي ليزر)
- Labor costs (تكاليف العمالة)
- Fuel consumption calculation (استهلاك الوقود)
- Surveying costs (تكاليف المسح)
- Contingency (10% احتياطي)
- Cost per m3 and per hectare

### Equipment Recommendation | توصيات المعدات

- Optimal equipment selection based on volume
- Productivity-based recommendations
- Multi-equipment combinations
- Prioritized equipment list

### Leveling Methods | طرق التسوية

| Method | Arabic | Use Case |
|--------|--------|----------|
| **Single Plane** | مستوى واحد | Uniform fields, surface irrigation |
| **Dual Plane** | مستويين | Fields with multiple grades |
| **Contour** | كنتوري | Sloped terrain, erosion control |
| **Bench** | مصاطب | Steep slopes, terraced farming |

### Optimization Priorities | أولويات التحسين

| Priority | Arabic | Objective |
|----------|--------|-----------|
| **Minimize Cost** | تقليل التكلفة | Lowest total project cost |
| **Minimize Earthwork** | تقليل الحفر والردم | Least volume moved |
| **Optimal Drainage** | تصريف مثالي | Best drainage grades |
| **Irrigation Efficiency** | كفاءة الري | Optimal for irrigation |

---

## API Endpoints | نقاط النهاية

### Health Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Kubernetes liveness probe |
| `/readyz` | GET | Kubernetes readiness probe |
| `/metrics` | GET | Prometheus metrics |

### Leveling Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/leveling/analyze` | POST | Full leveling analysis with cost |
| `/api/v1/leveling/simulate` | POST | Simulate leveling scenario |
| `/api/v1/leveling/compare` | POST | Compare multiple scenarios |
| `/api/v1/leveling/plan/{field_id}` | GET | Get optimal leveling plan |

### Cut/Fill Calculation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/cutfill/calculate` | POST | Calculate cut/fill volumes |
| `/api/v1/cutfill/optimize` | POST | Find optimal design elevation |
| `/api/v1/cutfill/balance` | POST | Calculate balance point |

### Cost Estimation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/cost/estimate` | POST | Detailed cost estimation |
| `/api/v1/cost/equipment` | GET | Get equipment rates |
| `/api/v1/cost/update-rates` | PUT | Update cost rates |
| `/api/v1/leveling/cost/{field_id}` | GET | Get cost estimation |

### Equipment

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/equipment/recommend` | POST | Get equipment recommendations |
| `/api/v1/equipment/list` | GET | List available equipment types |
| `/api/v1/equipment/productivity` | GET | Get productivity rates |
| `/api/v1/leveling/equipment/{field_id}` | GET | Equipment recommendations |

---

## Request/Response Examples | أمثلة الطلبات

### Leveling Analysis Request

```bash
curl -X POST "http://localhost:8170/api/v1/leveling/analyze" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "FIELD-003",
    "elevation_points": [
      {"x": 0, "y": 0, "elevation": 150.5, "point_id": "P1"},
      {"x": 100, "y": 0, "elevation": 151.2, "point_id": "P2"},
      {"x": 100, "y": 100, "elevation": 152.1, "point_id": "P3"},
      {"x": 0, "y": 100, "elevation": 151.8, "point_id": "P4"},
      {"x": 50, "y": 50, "elevation": 151.5, "point_id": "P5"}
    ],
    "soil_type": "loamy",
    "target_grade_x": 0.2,
    "target_grade_y": 0.1,
    "method": "single_plane",
    "priority": "minimize_cost",
    "include_cost_estimate": true
  }'
```

### Leveling Analysis Response

```json
{
  "success": true,
  "field_id": "FIELD-003",
  "analysis_timestamp": "2026-01-31T10:30:00Z",
  "plan": {
    "plan_id": "plan-550e8400-e29b",
    "field_id": "FIELD-003",
    "design_plane": {
      "centroid_elevation": 151.42,
      "grade_x_percent": 0.2,
      "grade_y_percent": 0.1,
      "plane_equation": "z = 0.002*x + 0.001*y + 151.35",
      "coefficient_a": 0.002,
      "coefficient_b": 0.001,
      "coefficient_c": 151.35
    },
    "method": "single_plane",
    "cut_fill": {
      "cut_volume_m3": 1250.5,
      "fill_volume_m3": 1180.2,
      "net_volume_m3": 70.3,
      "cut_area_m2": 4500.0,
      "fill_area_m2": 5500.0,
      "balance_ratio": 1.06,
      "max_cut_depth_m": 0.85,
      "max_fill_depth_m": 0.72,
      "avg_cut_depth_m": 0.28,
      "avg_fill_depth_m": 0.21
    },
    "field_area_m2": 10000.0,
    "field_area_hectares": 1.0,
    "original_elevation_range": 1.6,
    "leveled_elevation_range": 0.22,
    "avg_haul_distance_m": 85.5,
    "equipment_recommendations": [
      {
        "equipment_type": "laser_leveler",
        "equipment_name_en": "Laser Land Leveler",
        "equipment_name_ar": "مسوي ليزر",
        "quantity": 1,
        "hours_required": 32.5,
        "cost_per_hour_sar": 450.0,
        "total_cost_sar": 14625.0,
        "productivity_m3_per_hour": 40.0,
        "recommended_for": "Precision leveling with optimal grade control",
        "priority": 1
      },
      {
        "equipment_type": "scraper",
        "equipment_name_en": "Scraper",
        "equipment_name_ar": "كاشطة",
        "quantity": 1,
        "hours_required": 20.8,
        "cost_per_hour_sar": 400.0,
        "total_cost_sar": 8320.0,
        "productivity_m3_per_hour": 120.0,
        "recommended_for": "High volume earth moving",
        "priority": 2
      }
    ],
    "cost_estimate": {
      "total_cost_sar": 32500.0,
      "earthwork_cost_sar": 22750.0,
      "equipment_cost_sar": 22945.0,
      "labor_cost_sar": 2665.0,
      "fuel_cost_sar": 3180.0,
      "surveying_cost_sar": 500.0,
      "contingency_sar": 2960.0,
      "cost_per_m3_sar": 13.4,
      "cost_per_hectare_sar": 32500.0,
      "estimated_duration_hours": 53.3,
      "estimated_duration_days": 6.7,
      "summary_en": "Total cost: 32,500 SAR for 1.0 hectares. Estimated duration: 7 working days.",
      "summary_ar": "التكلفة الإجمالية: 32,500 ريال لمساحة 1.0 هكتار. المدة المقدرة: 7 أيام عمل."
    },
    "summary_en": "Single plane leveling with 0.2% X-grade and 0.1% Y-grade. Cut/Fill ratio: 1.06 (balanced). Recommended equipment: Laser leveler for precision work.",
    "summary_ar": "تسوية بمستوى واحد بميل 0.2% باتجاه X و 0.1% باتجاه Y. نسبة القطع/الردم: 1.06 (متوازنة). المعدات الموصى بها: مسوي ليزر للعمل الدقيق.",
    "recommendations_en": [
      "Use laser leveler for best grade precision",
      "Schedule work during dry season",
      "Consider soil compaction after fill operations",
      "Install drainage channels in low areas"
    ],
    "recommendations_ar": [
      "استخدم مسوي ليزر لأفضل دقة في الميل",
      "جدول العمل خلال الموسم الجاف",
      "اعتبر دمك التربة بعد عمليات الردم",
      "قم بتركيب قنوات تصريف في المناطق المنخفضة"
    ]
  },
  "message_en": "Leveling analysis completed successfully",
  "message_ar": "اكتمل تحليل التسوية بنجاح"
}
```

---

## Equipment Types | أنواع المعدات

| Equipment | Arabic | Cost/Hour (SAR) | Productivity (m3/h) | Best For |
|-----------|--------|-----------------|---------------------|----------|
| **Bulldozer** | جرافة | 350 | 80 | Heavy earthmoving |
| **Scraper** | كاشطة | 400 | 120 | Long haul distances |
| **Grader** | ممهدة | 300 | 60 | Fine grading |
| **Laser Leveler** | مسوي ليزر | 450 | 40 | Precision leveling |
| **Excavator** | حفارة | 380 | 100 | Deep cuts, loading |
| **Dump Truck** | شاحنة قلابة | 200 | - | Material transport |

---

## Soil Types | أنواع التربة

| Type | Arabic | Expansion Factor | Compaction Factor |
|------|--------|------------------|-------------------|
| **Sandy** | رملية | 1.20 | 0.95 |
| **Loamy** | طفالية | 1.25 | 0.90 |
| **Clay** | طينية | 1.35 | 0.85 |
| **Silty** | طميية | 1.30 | 0.88 |
| **Rocky** | صخرية | 1.50 | 0.98 |

---

## Cost Factors | عوامل التكلفة

| Factor | Arabic | Default Value (SAR) |
|--------|--------|---------------------|
| Fuel cost per liter | تكلفة الوقود | 2.18 |
| Operator cost per hour | تكلفة المشغل | 50.0 |
| Surveying cost per hectare | تكلفة المسح | 500.0 |
| Contingency | احتياطي | 10% |

---

## Environment Variables | متغيرات البيئة

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `PORT` | `8170` | Service port | No |
| `HOST` | `0.0.0.0` | Bind address | No |
| `DEBUG` | `false` | Debug mode | No |
| `DATABASE_URL` | - | PostgreSQL connection | Yes |
| `NATS_URL` | - | NATS server URL | Yes |
| `REDIS_URL` | - | Redis connection | Yes |
| `JWT_SECRET_KEY` | - | JWT secret (32+ chars) | Yes |
| `BULLDOZER_COST_PER_HOUR` | `350.0` | Bulldozer rate (SAR) | No |
| `SCRAPER_COST_PER_HOUR` | `400.0` | Scraper rate (SAR) | No |
| `GRADER_COST_PER_HOUR` | `300.0` | Grader rate (SAR) | No |
| `LASER_LEVELER_COST_PER_HOUR` | `450.0` | Laser leveler rate (SAR) | No |
| `EXCAVATOR_COST_PER_HOUR` | `380.0` | Excavator rate (SAR) | No |
| `DUMP_TRUCK_COST_PER_HOUR` | `200.0` | Dump truck rate (SAR) | No |
| `BULLDOZER_PRODUCTIVITY` | `80.0` | Bulldozer m3/hour | No |
| `SCRAPER_PRODUCTIVITY` | `120.0` | Scraper m3/hour | No |
| `GRADER_PRODUCTIVITY` | `60.0` | Grader m3/hour | No |
| `LASER_LEVELER_PRODUCTIVITY` | `40.0` | Laser leveler m3/hour | No |
| `EXCAVATOR_PRODUCTIVITY` | `100.0` | Excavator m3/hour | No |
| `SOIL_EXPANSION_FACTOR` | `1.25` | Soil expansion factor | No |
| `SOIL_COMPACTION_FACTOR` | `0.90` | Soil compaction factor | No |
| `FUEL_COST_PER_LITER` | `2.18` | Fuel cost (SAR/L) | No |
| `OPERATOR_COST_PER_HOUR` | `50.0` | Operator cost (SAR/h) | No |
| `SURVEYING_COST_PER_HECTARE` | `500.0` | Survey cost (SAR/ha) | No |
| `DEFAULT_HAUL_DISTANCE` | `100.0` | Default haul distance (m) | No |
| `MIN_DRAINAGE_GRADE` | `0.1` | Min drainage grade (%) | No |
| `MAX_IRRIGATION_GRADE` | `0.5` | Max irrigation grade (%) | No |

---

## Cut/Fill Calculation Methodology | منهجية حساب القطع والردم

### Step 1: Design Plane Calculation

```
z = a*x + b*y + c

Where:
  a = target_grade_x / 100  (X-direction slope)
  b = target_grade_y / 100  (Y-direction slope)
  c = centroid elevation adjusted for balance
```

### Step 2: Volume Calculation

For each survey point:
```
cut_depth = max(0, original_elevation - design_elevation)
fill_depth = max(0, design_elevation - original_elevation)

volume = depth * cell_area * soil_factor
```

### Step 3: Balance Optimization

The service optimizes the design elevation to achieve:
- Minimum earthwork (cut = fill)
- Or user-specified priority (cost, drainage, irrigation)

### Haul Distance Calculation

Average haul distance is calculated as centroid-to-centroid distance between cut and fill areas, multiplied by a haul factor (1.2) for non-direct paths.

---

## Quick Start | البداية السريعة

### Local Development

```bash
# Navigate to service directory
cd apps/services/leveling-optimizer-service

# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn src.main:app --host 0.0.0.0 --port 8170 --reload
```

### Docker

```bash
# Build image
docker build -t sahool/leveling-optimizer-service .

# Run container
docker run -p 8170:8170 \
  -e DATABASE_URL=postgresql://user:pass@localhost:5432/sahool \
  -e NATS_URL=nats://localhost:4222 \
  -e REDIS_URL=redis://localhost:6379 \
  -e JWT_SECRET_KEY=your-32-char-secret-key-here-min \
  sahool/leveling-optimizer-service
```

---

## Events | الأحداث

### Produces

| Event | Description |
|-------|-------------|
| `LevelingPlanCreated.v1` | New leveling plan generated |
| `CostEstimateReady.v1` | Cost estimation completed |
| `LevelingSimulationCompleted.v1` | Simulation completed |

### Consumes

| Event | Description |
|-------|-------------|
| `SurveyDataUploaded.v1` | Process new survey data |
| `FieldBoundaryUpdated.v1` | Recalculate with new boundary |
| `TerrainAnalysisCompleted.v1` | Use terrain data for leveling |

---

## Testing | الاختبار

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_cutfill.py -v
```

---

## Troubleshooting | استكشاف الأخطاء

### Insufficient Survey Points

```
Error: Minimum 4 elevation points required
```

- Provide at least 4 survey points covering the field
- Ensure points are well-distributed

### Unbalanced Cut/Fill

- Adjust target grades to balance earthwork
- Use "minimize_earthwork" priority
- Consider contour leveling for steep terrain

### High Cost Estimates

- Review haul distances
- Consider different equipment combinations
- Evaluate alternative leveling methods

---

## License | الترخيص

Proprietary - KAFAAT

---

**Version**: 16.0.0
**Last Updated**: January 2026
