# Crop Rotation Planning - Quick Start Guide

**Get started with SAHOOL Crop Rotation Planning in 5 minutes**

## Installation

### Option 1: Run with Python

1. Install dependencies:

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/field-core
pip install -r rotation-requirements.txt
```

2. Run the service:

```bash
python -m src.rotation_main
```

3. Access the API:

```
http://localhost:8099/docs
```

### Option 2: Run with Docker

```bash
docker build -f rotation-Dockerfile -t sahool-rotation:latest .
docker run -p 8099:8099 sahool-rotation:latest
```

## Quick Examples

### 1. Create a 5-Year Rotation Plan

```bash
curl "http://localhost:8099/v1/rotation/plan?field_id=F001&field_name=MyField&start_year=2025&num_years=5"
```

Response:

```json
{
  "field_id": "F001",
  "start_year": 2025,
  "end_year": 2029,
  "seasons": [
    {
      "year": 2025,
      "crop_name_en": "Wheat",
      "crop_family": "cereals"
    },
    {
      "year": 2026,
      "crop_name_en": "Faba Bean",
      "crop_family": "legumes"
    }
  ],
  "diversity_score": 75.0,
  "soil_health_score": 80.0,
  "nitrogen_balance": "positive"
}
```

### 2. Get Crop Suggestions

```bash
curl "http://localhost:8099/v1/rotation/suggest/F001?season=winter"
```

### 3. View Rotation Rules

```bash
curl "http://localhost:8099/v1/rotation/rules"
```

### 4. Check Compatibility

```bash
curl "http://localhost:8099/v1/rotation/check?crop_family=legumes&previous_crops=WHEAT,BARLEY"
```

## Run Example Script

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/field-core
python examples/rotation_example.py
```

This will demonstrate:

- Creating rotation plans
- Suggesting next crops
- Evaluating rotations
- Checking compatibility
- Viewing rotation rules

## Run Tests

```bash
pytest tests/test_rotation.py -v
```

## Key Endpoints

| Endpoint                          | Method   | Description          |
| --------------------------------- | -------- | -------------------- |
| `/v1/rotation/plan`               | GET/POST | Create rotation plan |
| `/v1/rotation/suggest/{field_id}` | GET      | Suggest next crop    |
| `/v1/rotation/evaluate`           | POST     | Evaluate rotation    |
| `/v1/rotation/rules`              | GET      | View rotation rules  |
| `/v1/rotation/families`           | GET      | List crop families   |
| `/v1/rotation/check`              | GET      | Check compatibility  |

## Crop Families Supported

- **Cereals** (الحبوب): Wheat, barley, sorghum, maize
- **Legumes** (البقوليات): Faba bean, lentil, chickpea
- **Solanaceae** (الباذنجانيات): Tomato, potato, pepper
- **Cucurbits** (القرعيات): Cucumber, melon, watermelon
- And 11 more families...

## Rotation Principles

1. ✅ **No monoculture** - Don't repeat same family
2. ✅ **Legumes every 3-4 years** - Fix nitrogen
3. ✅ **Alternate root depths** - Improve soil structure
4. ✅ **Disease breaks** - Wait 4+ years for disease-prone crops
5. ✅ **Heavy feeders after fixers** - Balance nutrients

## Need Help?

- Full documentation: `ROTATION_README.md`
- API docs: http://localhost:8099/docs
- Run examples: `python examples/rotation_example.py`

---

**Built for Yemen's farmers with ❤️**
