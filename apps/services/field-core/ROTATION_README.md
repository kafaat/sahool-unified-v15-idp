# SAHOOL Crop Rotation Planning Service

**Crop rotation planning for soil health and disease prevention**
**تخطيط تدوير المحاصيل لصحة التربة ومنع الأمراض**

This service helps farmers plan optimal crop rotations based on agronomic principles, similar to features found in OneSoil and LiteFarm.

## Features

### Core Functionality

- **5-Year Rotation Planning**: Generate comprehensive multi-year rotation plans
- **Crop Family Management**: Track 15+ crop families with specific rotation rules
- **Disease Risk Assessment**: Identify and prevent disease buildup from repeated crops
- **Nitrogen Balance Tracking**: Monitor soil nitrogen levels across rotations
- **Soil Health Scoring**: Evaluate rotation plans for long-term soil health
- **Compatibility Checking**: Verify crop sequences follow agronomic best practices

### Yemen-Specific Features

- **50+ Yemen Crops**: Complete catalog of crops grown in Yemen
- **Regional Adaptation**: Crop suggestions based on Yemen's agricultural zones
- **Bilingual Support**: Full Arabic and English support
- **Local Varieties**: Integration with Yemen-specific crop varieties

### Rotation Principles

1. **No Monoculture**: Avoid repeating same crop family consecutively
2. **Legume Inclusion**: Include nitrogen-fixing crops every 3-4 years
3. **Root Depth Alternation**: Alternate between shallow and deep-rooted crops
4. **Disease Break**: Minimum 4 years between disease-prone families (e.g., Solanaceae)
5. **Nutrient Balance**: Follow heavy feeders with nitrogen fixers

## API Endpoints

### 1. Create Rotation Plan

**GET** `/v1/rotation/plan`

Query Parameters:

- `field_id`: Field identifier
- `field_name`: Name of the field
- `start_year`: Starting year (e.g., 2025)
- `num_years`: Number of years to plan (1-10, default: 5)

```bash
curl "http://localhost:8099/v1/rotation/plan?field_id=F001&field_name=Field1&start_year=2025&num_years=5"
```

**POST** `/v1/rotation/plan`

Request body with custom history:

```json
{
  "field_id": "F001",
  "field_name": "Field 1",
  "start_year": 2025,
  "num_years": 5,
  "history": [
    {
      "season_id": "F001_2024_winter",
      "year": 2024,
      "season": "winter",
      "crop_code": "WHEAT",
      "crop_name_ar": "قمح",
      "crop_name_en": "Wheat",
      "crop_family": "cereals"
    }
  ],
  "preferences": ["TOMATO", "WHEAT"]
}
```

Response:

```json
{
  "field_id": "F001",
  "field_name": "Field 1",
  "start_year": 2025,
  "end_year": 2029,
  "seasons": [...],
  "diversity_score": 75.0,
  "soil_health_score": 80.0,
  "disease_risk_score": 20.0,
  "nitrogen_balance": "positive",
  "recommendations_ar": ["..."],
  "recommendations_en": ["..."]
}
```

### 2. Suggest Next Crop

**GET** `/v1/rotation/suggest/{field_id}`

Query Parameters:

- `season`: Growing season (winter, summer, spring, autumn)

```bash
curl "http://localhost:8099/v1/rotation/suggest/F001?season=winter"
```

Response:

```json
{
  "field_id": "F001",
  "season": "winter",
  "suggestions": [
    {
      "crop_code": "FABA_BEAN",
      "crop_name_ar": "فول",
      "crop_name_en": "Faba Bean",
      "crop_family": "legumes",
      "suitability_score": 95.0,
      "reasons_ar": ["يثبت النيتروجين في التربة", "سلف جيد بعد الحبوب"],
      "reasons_en": ["Fixes nitrogen in soil", "Good successor after cereals"],
      "warnings_ar": [],
      "warnings_en": []
    }
  ]
}
```

### 3. Evaluate Rotation

**POST** `/v1/rotation/evaluate`

Request body:

```json
{
  "seasons": [
    {
      "season_id": "S1",
      "year": 2024,
      "season": "winter",
      "crop_code": "WHEAT",
      "crop_name_ar": "قمح",
      "crop_name_en": "Wheat",
      "crop_family": "cereals"
    },
    {
      "season_id": "S2",
      "year": 2025,
      "season": "winter",
      "crop_code": "FABA_BEAN",
      "crop_name_ar": "فول",
      "crop_name_en": "Faba Bean",
      "crop_family": "legumes"
    }
  ]
}
```

Response:

```json
{
  "evaluation": {
    "diversity_score": 80.0,
    "soil_health_score": 85.0,
    "disease_risk_score": 15.0,
    "nitrogen_balance": "positive",
    "recommendations_ar": ["..."],
    "recommendations_en": ["..."]
  }
}
```

### 4. Get Rotation Rules

**GET** `/v1/rotation/rules`

Returns all rotation rules by crop family:

```json
{
  "rules": {
    "cereals": {
      "min_years_between": 1,
      "good_predecessors": ["legumes", "fodder", "fallow"],
      "bad_predecessors": ["cereals"],
      "nitrogen_effect": "deplete",
      "disease_risk": {
        "fusarium": 0.3,
        "rust": 0.2
      },
      "root_depth": "medium",
      "nutrient_demand": "medium"
    }
  }
}
```

### 5. Get Crop Families

**GET** `/v1/rotation/families`

Returns all crop families and their crops:

```json
{
  "families": {
    "cereals": ["WHEAT", "BARLEY", "SORGHUM", "MAIZE"],
    "legumes": ["FABA_BEAN", "LENTIL", "CHICKPEA"],
    "solanaceae": ["TOMATO", "POTATO", "PEPPER"]
  },
  "total_families": 15,
  "total_crops": 50
}
```

### 6. Check Compatibility

**GET** `/v1/rotation/check`

Query Parameters:

- `crop_family`: Crop family to check
- `previous_crops`: Comma-separated list of previous crop codes

```bash
curl "http://localhost:8099/v1/rotation/check?crop_family=legumes&previous_crops=WHEAT,BARLEY"
```

Response:

```json
{
  "crop_family": "legumes",
  "is_compatible": true,
  "warnings_ar": [],
  "warnings_en": [],
  "nitrogen_balance": "positive",
  "disease_risk": {...}
}
```

## Crop Families

The service supports 15 crop families:

1. **Cereals** (الحبوب): Wheat, barley, sorghum, maize, millet, rice
2. **Legumes** (البقوليات): Faba bean, lentil, chickpea, cowpea, peanut
3. **Solanaceae** (الباذنجانيات): Tomato, potato, pepper, eggplant
4. **Cucurbits** (القرعيات): Cucumber, melon, watermelon, squash
5. **Brassicas** (الكرنبيات): Cabbage, cauliflower, broccoli
6. **Alliums** (الثوميات): Onion, garlic, leek
7. **Root Crops** (المحاصيل الجذرية): Carrot, beet, radish, turnip
8. **Fiber** (الألياف): Cotton
9. **Oilseeds** (البذور الزيتية): Sesame, sunflower
10. **Fodder** (الأعلاف): Alfalfa, clover
11. **Fruits** (الفواكه): Mango, banana, date palm, grapes
12. **Spices** (التوابل): Coriander, cumin, fenugreek
13. **Sugar** (السكريات): Sugarcane
14. **Stimulants** (المنبهات): Coffee, qat
15. **Fallow** (بور): Rest period

## Rotation Rules

### Example: Legumes

```python
{
  "min_years_between": 3,  # Wait 3 years before repeating
  "good_predecessors": ["cereals", "root_crops", "brassicas"],
  "bad_predecessors": ["legumes", "fodder"],
  "nitrogen_effect": "fix",  # Fixes nitrogen in soil
  "disease_risk": {
    "root_rot": 0.4,
    "fusarium": 0.3
  },
  "root_depth": "medium",
  "nutrient_demand": "light"
}
```

### Example: Solanaceae (Tomato, Potato, Pepper)

```python
{
  "min_years_between": 4,  # Wait 4 years before repeating
  "good_predecessors": ["cereals", "legumes", "fodder"],
  "bad_predecessors": ["solanaceae", "cucurbits"],
  "nitrogen_effect": "heavy_deplete",  # Depletes nitrogen heavily
  "disease_risk": {
    "bacterial_wilt": 0.5,
    "nematodes": 0.4,
    "verticillium": 0.3
  },
  "root_depth": "deep",
  "nutrient_demand": "heavy"
}
```

## Installation

### Local Development

1. Install dependencies:

```bash
pip install -r rotation-requirements.txt
```

2. Run the service:

```bash
python -m src.rotation_main
```

3. Access API documentation:

```
http://localhost:8099/docs
```

### Docker

1. Build the image:

```bash
docker build -f rotation-Dockerfile -t sahool-crop-rotation:latest .
```

2. Run the container:

```bash
docker run -p 8099:8099 sahool-crop-rotation:latest
```

### Docker Compose

Add to `docker-compose.yml`:

```yaml
services:
  crop-rotation:
    build:
      context: ./apps/services/field-core
      dockerfile: rotation-Dockerfile
    ports:
      - "8099:8099"
    environment:
      - PORT=8099
      - DATABASE_URL=postgresql://user:password@postgres/sahool_rotation
    depends_on:
      - postgres
```

## Database Schema

The service includes SQLAlchemy models for:

1. **rotation_plans**: Main rotation plans
2. **season_plans**: Individual season plans within rotations
3. **field_history**: Historical crop data for fields
4. **rotation_rule_overrides**: Custom rules for specific tenants/fields
5. **rotation_recommendations**: AI-generated recommendations

### Create Tables

```python
from src.rotation_models import create_tables
from sqlalchemy import create_engine

engine = create_engine("postgresql://user:password@localhost/sahool_rotation")
create_tables(engine)
```

## Integration with SAHOOL Platform

### With Field Service

```python
# Get field data
field = await field_service.get_field(field_id)

# Create rotation plan
plan = await rotation_service.create_rotation_plan(
    field_id=field.id,
    field_name=field.name,
    start_year=2025,
    num_years=5
)
```

### With Agro Advisor

```python
# Get crop recommendations
suggestions = await rotation_service.suggest_next_crop(field_id, season="winter")

# Get crop requirements
for suggestion in suggestions:
    requirements = await agro_advisor.get_crop_requirements(suggestion.crop_code)
```

### With Satellite Service

```python
# Track actual performance
actual_yield = await satellite_service.estimate_yield(field_id)

# Update season plan
await rotation_service.update_season_yield(season_id, actual_yield)
```

## Testing

Run tests:

```bash
pytest tests/ -v --cov=src
```

## API Documentation

Interactive API documentation is available at:

- Swagger UI: `http://localhost:8099/docs`
- ReDoc: `http://localhost:8099/redoc`

## Configuration

Environment variables:

- `PORT`: Service port (default: 8099)
- `DATABASE_URL`: PostgreSQL connection string
- `NATS_URL`: NATS server URL for event publishing (optional)

## References

This implementation is based on agronomic principles from:

- **OneSoil**: Field management and crop rotation planning
- **LiteFarm**: Sustainable farming practices
- **FAO Guidelines**: Crop rotation and soil health best practices
- **Yemen Agricultural Extension**: Local farming practices

## License

Part of the SAHOOL Unified Agricultural Platform
Copyright (c) 2025

## Support

For issues and questions:

- GitHub Issues: [sahool-unified-v15-idp](https://github.com/your-org/sahool-unified-v15-idp)
- Documentation: `/docs`
- Email: support@sahool.example

---

**Built with ❤️ for Yemen's farmers**
**بُني بحب لمزارعي اليمن**
