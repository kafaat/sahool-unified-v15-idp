# Leveling Optimizer Service | خدمة تحسين التسوية

Agricultural field leveling optimization service for the SAHOOL platform.

خدمة تحسين تسوية الحقول الزراعية لمنصة سهول

## Overview | نظرة عامة

This service provides optimal field leveling calculations for agricultural land preparation, enabling farmers to efficiently prepare fields for irrigation and cultivation.

توفر هذه الخدمة حسابات التسوية المثلى للحقول الزراعية لإعداد الأرض، مما يمكّن المزارعين من إعداد الحقول بكفاءة للري والزراعة.

## Features | الميزات

- **Cut/Fill Volume Calculation** | حساب أحجام القطع والردم
- **Optimal Grade Plane Computation** | حساب مستوى الميل الأمثل
- **Multi-Plane Optimization** | تحسين المستويات المتعددة
- **Equipment Recommendations** | توصيات المعدات
- **Cost Estimation in SAR** | تقدير التكلفة بالريال السعودي
- **Leveling Simulation** | محاكاة التسوية
- **Bilingual Output (Arabic/English)** | مخرجات ثنائية اللغة

## Port | المنفذ

```
8170
```

## API Endpoints | نقاط النهاية

### Leveling Operations | عمليات التسوية

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/leveling/analyze` | Analyze field for leveling needs |
| GET | `/api/v1/leveling/plan/{field_id}` | Get optimal leveling plan |
| GET | `/api/v1/leveling/cost/{field_id}` | Get cost estimation |
| GET | `/api/v1/leveling/equipment/{field_id}` | Equipment recommendations |
| POST | `/api/v1/leveling/simulate` | Simulate leveling scenario |

### Health Endpoints | نقاط الصحة

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/healthz` | Liveness probe |
| GET | `/readyz` | Readiness probe |
| GET | `/health` | Combined health status |

## Leveling Methods | طرق التسوية

| Method | Description EN | Description AR |
|--------|----------------|----------------|
| `single_plane` | Single uniform plane | مستوى واحد موحد |
| `dual_plane` | Two-directional slopes | ميول باتجاهين |
| `contour` | Following natural contours | اتباع الخطوط الكنتورية |
| `bench` | Terraced/stepped | مصاطب/متدرج |

## Optimization Priorities | أولويات التحسين

| Priority | Description EN | Description AR |
|----------|----------------|----------------|
| `minimize_cost` | Minimize total cost | تقليل التكلفة الإجمالية |
| `minimize_earthwork` | Balance cut and fill | توازن القطع والردم |
| `optimal_drainage` | Ensure proper drainage | ضمان التصريف السليم |
| `irrigation_efficiency` | Optimize for irrigation | التحسين لكفاءة الري |

## Equipment Types | أنواع المعدات

| Type | Name EN | Name AR | Cost/Hour (SAR) |
|------|---------|---------|-----------------|
| `bulldozer` | Bulldozer | جرافة | 350 |
| `scraper` | Scraper | كاشطة | 400 |
| `grader` | Motor Grader | ممهدة | 300 |
| `laser_leveler` | Laser Leveler | مسوي ليزر | 450 |
| `excavator` | Excavator | حفارة | 380 |
| `dump_truck` | Dump Truck | شاحنة قلابة | 200 |

## Usage Example | مثال الاستخدام

### Analyze Field | تحليل الحقل

```bash
curl -X POST http://localhost:8170/api/v1/leveling/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "FIELD-001",
    "elevation_points": [
      {"x": 0, "y": 0, "elevation": 100.0, "point_id": "P1"},
      {"x": 100, "y": 0, "elevation": 100.2, "point_id": "P2"},
      {"x": 0, "y": 100, "elevation": 100.1, "point_id": "P3"},
      {"x": 100, "y": 100, "elevation": 100.4, "point_id": "P4"}
    ],
    "soil_type": "loamy",
    "method": "single_plane",
    "priority": "minimize_cost",
    "include_cost_estimate": true
  }'
```

### Response Example | مثال الاستجابة

```json
{
  "success": true,
  "field_id": "FIELD-001",
  "plan": {
    "design_plane": {
      "centroid_elevation": 100.175,
      "grade_x_percent": 0.2,
      "grade_y_percent": 0.15
    },
    "cut_fill": {
      "cut_volume_m3": 2500.0,
      "fill_volume_m3": 2300.0,
      "balance_ratio": 1.09
    },
    "cost_estimate": {
      "total_cost_sar": 45000.0,
      "cost_per_hectare_sar": 18000.0,
      "summary_en": "Total estimated cost: 45,000 SAR...",
      "summary_ar": "إجمالي التكلفة المقدرة: 45,000 ريال..."
    }
  }
}
```

## Development | التطوير

### Run Locally | التشغيل محلياً

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python -m uvicorn src.main:app --host 0.0.0.0 --port 8170 --reload
```

### Run Tests | تشغيل الاختبارات

```bash
pytest tests/ -v
```

### Docker | دوكر

```bash
# Build image
docker build -t leveling-optimizer-service .

# Run container
docker run -p 8170:8170 leveling-optimizer-service
```

## Environment Variables | متغيرات البيئة

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8170 |
| `DEBUG` | Debug mode | false |
| `DATABASE_URL` | PostgreSQL URL | None |
| `NATS_URL` | NATS URL | None |
| `BULLDOZER_COST_PER_HOUR` | Bulldozer hourly cost (SAR) | 350 |
| `SCRAPER_COST_PER_HOUR` | Scraper hourly cost (SAR) | 400 |
| `LASER_LEVELER_COST_PER_HOUR` | Laser leveler hourly cost (SAR) | 450 |

## Algorithm Details | تفاصيل الخوارزمية

### Optimal Plane Computation | حساب المستوى الأمثل

The service uses least squares regression to compute the optimal design plane:

```
z = a*x + b*y + c
```

Where:
- `a` = Grade in X direction (m/m)
- `b` = Grade in Y direction (m/m)
- `c` = Elevation offset at origin (m)

### Cut/Fill Balance | توازن القطع والردم

The algorithm accounts for soil factors:
- **Expansion Factor** (معامل الانتفاخ): 1.25 - Soil expands when excavated
- **Compaction Factor** (معامل الدمك): 0.90 - Soil compacts when placed

### Haul Distance | مسافة النقل

Average haul distance is calculated as centroid-to-centroid distance between cut and fill areas, multiplied by a haul factor (1.2) for non-direct paths.

## Version | الإصدار

16.0.0

## License | الرخصة

Proprietary - KAFAAT
