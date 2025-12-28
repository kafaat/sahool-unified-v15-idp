# Yield Prediction Service (Unified)

**خدمة توقع الإنتاجية الموحدة**

> **Note**: This service consolidates `yield-engine` and `yield-prediction` into a single unified service.

## Overview | نظرة عامة

Unified yield prediction service using machine learning models for field-level, regional, and national crop yield forecasting.

خدمة توقع الإنتاجية الموحدة. تستخدم نماذج التعلم الآلي للتنبؤ بإنتاجية المحاصيل على مستوى الحقل والمنطقة والوطن.

## Port

```
8103
```

## Features | الميزات

### ML-Based Prediction | التوقع بالتعلم الآلي (from yield-engine)
- Random Forest models
- XGBoost models
- LSTM time series models
- Ensemble predictions (88-93% accuracy)

### Prediction Levels | مستويات التوقع (from yield-prediction)
- Field-level predictions (توقعات الحقل)
- Regional forecasts (توقعات إقليمية)
- National aggregates (تجميعات وطنية)

### Analysis Features | ميزات التحليل
- Seasonal forecasts (توقعات موسمية)
- Early predictions (توقعات مبكرة)
- Scenario analysis (تحليل السيناريوهات)
- Factor importance (أهمية العوامل)
- Historical comparison (مقارنة تاريخية)

### Risk Assessment | تقييم المخاطر
- Weather risk forecasting
- Pest risk integration
- Disease risk factors
- Drought impact estimation

### Optimization | التحسين
- Yield optimization recommendations
- Input optimization
- Resource allocation advice

## API Endpoints

### Health Check
- `GET /healthz` - Service health status

### Predictions
- `POST /predict` - Predict yield for field
- `POST /predict/batch` - Batch predictions
- `GET /predict/{field_id}` - Get latest prediction
- `POST /predict/regional` - Regional forecast
- `POST /predict/national` - National forecast

### Analysis
- `GET /analysis/{field_id}/factors` - Factor importance
- `GET /analysis/{field_id}/history` - Historical yields
- `POST /analysis/scenario` - Scenario comparison
- `GET /analysis/{field_id}/benchmark` - Benchmark comparison

### Models
- `GET /models` - Available models
- `GET /models/{model_id}/accuracy` - Model accuracy metrics
- `POST /models/retrain` - Trigger model retraining

### Risk
- `GET /risk/{field_id}` - Yield risk assessment
- `POST /risk/forecast` - Risk forecast

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8103 | Service port |
| `DATABASE_URL` | - | PostgreSQL connection |
| `REDIS_URL` | - | Redis for caching |
| `MODEL_PATH` | - | ML models directory |
| `WEATHER_SERVICE_URL` | - | Weather service URL |
| `SATELLITE_SERVICE_URL` | - | Satellite service URL |

## ML Models

| Model | Accuracy | Use Case |
|-------|----------|----------|
| Random Forest | 88% | General predictions |
| XGBoost | 91% | High-precision needs |
| LSTM | 89% | Time series patterns |
| Ensemble | 93% | Best accuracy |

## Migration from Previous Services

This service replaces:
- `yield-engine` (Port 8098) - ML models & scenario analysis
- `yield-prediction` (Port 8103) - Predictions & forecasting

All functionality is now available in this unified service.

## Docker

```bash
docker build -t yield-prediction-service .
docker run -p 8103:8103 yield-prediction-service
```

## Development

```bash
cd apps/services/yield-prediction-service
pip install -r requirements.txt
python -m uvicorn src.main:app --reload --port 8103
```
