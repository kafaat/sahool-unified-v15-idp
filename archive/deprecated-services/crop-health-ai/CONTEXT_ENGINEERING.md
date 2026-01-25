# Context Engineering Enhancements
# تحسينات هندسة السياق

## Overview

The crop-health-ai service has been enhanced with three powerful context engineering capabilities:

1. **Context Compression** - Optimizes image and field data for efficient AI processing
2. **Field Memory** - Maintains per-field disease history for contextual predictions
3. **Evaluation Scoring** - Tracks prediction quality and detects model drift

These features enable the AI to make more informed decisions by understanding historical patterns and maintaining accurate performance metrics.

---

## 1. Context Compression Service

### Purpose

Compresses image and field data into optimized representations, reducing context size while preserving diagnostic value.

**Location:** `src/services/context_compression.py`

### Features

- **Image Compression**: Resize, normalize, and encode images efficiently
- **Field Context Compression**: Compress historical disease patterns
- **Model Prompt Optimization**: Create optimized context for AI inference
- **Feature Extraction**: Calculate image features (brightness, color dominance)
- **Spatial Locality**: Hash location for geographic context
- **Temporal Pattern Analysis**: Detect disease patterns (seasonal, sporadic, persistent)

### Architecture

```
CompressedImageContext
├── image_hash: Deduplication key
├── image_size_bytes: Original size
├── compressed_size_bytes: After optimization
├── compression_ratio: Percentage reduction
├── image_features: Color/pattern statistics
└── preprocessing_applied: List of operations

CompressedFieldContext
├── field_id: Field identifier
├── crop_type: Type of crop
├── severity_score: Current severity
├── disease_frequency: Historical disease counts
├── avg_confidence: Average prediction confidence
├── historical_diseases: Past diseases detected
├── location_hash: Spatial locality indicator
├── temporal_pattern: Seasonal/sporadic/persistent
├── last_diagnosis_days_ago: Days since last diagnosis
├── field_health_score: Inverse of disease presence
└── compression_ratio: Context size reduction
```

### Usage Examples

#### Compress Image
```python
from services import context_compression_service

image_context = context_compression_service.compress_image_context(
    image_bytes=image_data,
)

print(f"Compression: {image_context.compression_ratio:.1f}%")
print(f"Features: {image_context.image_features}")
```

#### Compress Field Context
```python
field_context = context_compression_service.compress_field_context(
    field_id="field-001",
    crop_type="wheat",
    current_severity=0.6,
    disease_history=field_diagnoses,
    lat=15.35,
    lng=44.20,
)

print(f"Health Score: {field_context.field_health_score:.2f}")
print(f"Pattern: {field_context.temporal_pattern}")
```

#### Create Optimized Model Prompt
```python
prompt_context = context_compression_service.create_model_prompt_context(
    image_context=image_context,
    field_context=field_context,
    disease_candidates=["wheat_leaf_rust", "powdery_mildew"],
)

# Use prompt_context for AI model input
```

### API Endpoints

Currently integrated internally. Exposed through diagnosis endpoints.

### Performance Metrics

- Typical image compression: 40-60% reduction
- Field context compression: 70-85% reduction
- Preprocessing steps: 2-4 operations per image
- Feature extraction: <100ms per image

---

## 2. Field Memory Service

### Purpose

Maintains persistent memory of disease patterns per field for contextual diagnosis and pattern recognition.

**Location:** `src/services/field_memory.py`

### Features

- **Per-Field History Tracking**: Store last 100 diagnoses per field
- **Disease Pattern Analysis**: Frequency, severity, occurrence timing
- **Field Health Metrics**: Overall health score and infection trends
- **Disease Recurrence Prediction**: Likelihood of disease reoccurrence
- **Risk Assessment**: Comprehensive field risk analysis
- **Treatment Effectiveness**: Track intervention success rates

### Architecture

```
FieldMemory
├── field_histories: {field_id → deque of FieldDiagnosisRecord}
├── field_metrics_cache: Cached FieldHealthMetrics
├── patterns_cache: Cached disease patterns per field
└── max_records_per_field: 100 (configurable)

FieldDiagnosisRecord
├── diagnosis_id: Unique identifier
├── disease_id: Detected disease
├── disease_name_ar: Arabic name
├── confidence: Prediction confidence (0-1)
├── severity: Disease severity level
├── timestamp: When diagnosed
├── affected_area_percent: Area affected
└── treated: Whether treated

FieldHealthMetrics
├── field_id: Field identifier
├── total_diagnoses: Total count
├── healthy_diagnoses: Count of healthy
├── infected_diagnoses: Count of diseased
├── health_score: 0-1 health score
├── infection_trend: improving/stable/worsening
├── dominant_disease: Most common disease
├── disease_variety: Number of unique diseases
├── avg_confidence: Average prediction confidence
└── last_updated: Timestamp

DiseasePattern
├── disease_id: Disease identifier
├── disease_name_ar: Arabic name
├── occurrence_count: How many times detected
├── avg_confidence: Average confidence
├── severity_levels: Distribution of severities
├── last_occurred: Last occurrence date
├── days_between_occurrences: Intervals between detections
└── avg_severity: Most common severity
```

### Usage Examples

#### Record Diagnosis in Field Memory
```python
from services import field_memory

record = field_memory.record_diagnosis(
    field_id="field-001",
    diagnosis_id="diag-123",
    disease_id="wheat_leaf_rust",
    disease_name_ar="صدأ القمح",
    confidence=0.92,
    severity="high",
    affected_area_percent=25.0,
)
```

#### Get Field Health Metrics
```python
metrics = field_memory.calculate_field_metrics("field-001")

print(f"Health Score: {metrics.health_score:.2f}")
print(f"Total Diagnoses: {metrics.total_diagnoses}")
print(f"Infection Trend: {metrics.infection_trend}")
print(f"Dominant Disease: {metrics.dominant_disease}")
```

#### Get Disease Patterns
```python
patterns = field_memory.get_disease_patterns("field-001")

for disease_id, pattern in patterns.items():
    print(f"{pattern.disease_name_ar}:")
    print(f"  Occurrences: {pattern.occurrence_count}")
    print(f"  Avg Confidence: {pattern.avg_confidence:.2f}")
    print(f"  Last Occurred: {pattern.last_occurred}")
```

#### Predict Disease Recurrence
```python
prediction = field_memory.predict_disease_likelihood(
    field_id="field-001",
    disease_id="wheat_leaf_rust",
    days_ahead=7,
)

print(f"Likelihood: {prediction['likelihood']:.1%}")
print(f"Reasoning: {prediction['reasoning']}")
print(f"Days Since Last: {prediction['days_since_last']}")
```

#### Get Field Risk Assessment
```python
risk = field_memory.get_field_risk_assessment("field-001")

print(f"Overall Risk Score: {risk['overall_risk_score']:.2f}")
print(f"Risk Level: {risk['risk_level']}")
print(f"Top Threats: {risk['top_threats']}")
```

#### Track Treatment Effectiveness
```python
# Mark diagnosis as treated
field_memory.mark_diagnosis_treated("field-001", "diag-123")

# Get effectiveness metrics
effectiveness = field_memory.get_treatment_effectiveness("field-001")

print(f"Treatments Applied: {effectiveness['treatments_applied']}")
print(f"Effectiveness Rate: {effectiveness['effectiveness_rate']:.1%}")
print(f"Avg Recovery Days: {effectiveness['avg_recovery_days']}")
```

### API Endpoints

#### Get Field Health
```http
GET /v1/field/{field_id}/health

Response:
{
    "field_id": "field-001",
    "health_score": "0.78",
    "total_diagnoses": 15,
    "healthy_diagnoses": 12,
    "infected_diagnoses": 3,
    "infection_trend": "improving",
    "dominant_disease": "wheat_leaf_rust",
    "disease_variety": 2,
    "avg_confidence": "0.87"
}
```

#### Get Disease Patterns
```http
GET /v1/field/{field_id}/disease-patterns

Response:
{
    "field_id": "field-001",
    "patterns": [
        {
            "disease_id": "wheat_leaf_rust",
            "disease_name_ar": "صدأ القمح",
            "occurrence_count": 5,
            "avg_confidence": "0.89",
            "severity_levels": {"high": 3, "medium": 2},
            "last_occurred": "2025-01-10T10:30:00",
            "avg_days_between": 15.5,
            "avg_severity": "high"
        }
    ]
}
```

#### Get Field Risk Assessment
```http
GET /v1/field/{field_id}/risk-assessment

Response:
{
    "field_id": "field-001",
    "overall_risk_score": 0.35,
    "risk_level": "medium",
    "health_trend": "improving",
    "field_health_score": 0.78,
    "disease_variety": 2,
    "top_threats": [
        {
            "disease_id": "wheat_leaf_rust",
            "disease_name_ar": "صدأ القمح",
            "risk_score": 0.45,
            "occurrences": 5,
            "severity": "high"
        }
    ]
}
```

#### Mark Diagnosis as Treated
```http
POST /v1/field/{field_id}/diagnosis/{diagnosis_id}/mark-treated

Response:
{
    "success": true,
    "message": "Diagnosis marked as treated",
    "field_id": "field-001"
}
```

#### Get Treatment Effectiveness
```http
GET /v1/field/{field_id}/treatment-effectiveness

Response:
{
    "field_id": "field-001",
    "treatments_applied": 5,
    "successful_treatments": 4,
    "effectiveness_rate": 0.80,
    "avg_recovery_days": 12.5,
    "total_diagnoses": 15
}
```

#### Get All Fields Summary
```http
GET /v1/fields/summary

Response:
{
    "total_fields": 127,
    "total_diagnoses": 2543,
    "avg_health_score": 0.76,
    "fields_at_risk": 18,
    "timestamp": "2025-01-13T10:30:00"
}
```

---

## 3. Evaluation Scoring Service

### Purpose

Tracks prediction quality and confidence calibration. Detects model drift automatically.

**Location:** `src/services/evaluation_scorer.py`

### Features

- **Prediction Scoring**: Record predictions with confidence levels
- **Outcome Recording**: Update predictions with actual results
- **Accuracy Metrics**: Calculate per-disease, per-confidence-level accuracy
- **Confidence Calibration**: Measure if confidence matches actual accuracy
- **Model Drift Detection**: Identify performance degradation
- **Performance Reports**: Comprehensive evaluation reports
- **Error Rate Analysis**: False positive and false negative rates

### Architecture

```
EvaluationScorer
├── prediction_scores: List of PredictionScore
├── metrics_cache: Cached AccuracyMetrics
├── per_disease_cache: Per-disease metrics
├── per_crop_cache: Per-crop metrics
└── lookback_days: Historical lookback (90 days)

PredictionScore
├── diagnosis_id: Unique identifier
├── predicted_disease: Predicted disease ID
├── predicted_confidence: Confidence (0-1)
├── actual_disease: Ground truth (from expert review)
├── timestamp: When prediction made
├── field_id: Associated field
├── correct: True if prediction correct
└── confidence_error: |confidence - accuracy|

AccuracyMetrics
├── total_predictions: Total evaluated
├── correct_predictions: Number correct
├── accuracy: Overall accuracy rate
├── high_confidence_accuracy: Accuracy for conf > 0.7
├── medium_confidence_accuracy: Accuracy for 0.5-0.7
├── low_confidence_accuracy: Accuracy for conf < 0.5
├── confidence_mean: Average confidence
├── confidence_std: Std dev of confidence
└── calibration_score: Confidence calibration (0-1)

ModelDriftIndicators
├── accuracy_7day: Recent accuracy
├── accuracy_30day: Historical accuracy
├── accuracy_change_percent: Change in accuracy
├── confidence_trend: increasing/decreasing/stable
├── false_positive_rate: FP rate
├── false_negative_rate: FN rate
├── drift_detected: Boolean
└── drift_severity: none/mild/moderate/severe
```

### Usage Examples

#### Score a Prediction
```python
from services import evaluation_scorer

score = evaluation_scorer.score_prediction(
    diagnosis_id="diag-123",
    predicted_disease="wheat_leaf_rust",
    predicted_confidence=0.92,
    field_id="field-001",
)
```

#### Record Actual Outcome
```python
# After expert review confirms diagnosis
success = evaluation_scorer.record_outcome(
    diagnosis_id="diag-123",
    actual_disease="wheat_leaf_rust",  # or different if wrong
    notes="Expert confirmed diagnosis",
)

if success:
    print("Outcome recorded for evaluation")
```

#### Get Accuracy Metrics
```python
metrics = evaluation_scorer.get_accuracy_metrics(days_back=30)

print(f"Accuracy: {metrics.accuracy:.1%}")
print(f"High Conf Accuracy: {metrics.high_confidence_accuracy:.1%}")
print(f"Calibration Score: {metrics.calibration_score:.2f}")
print(f"Total Evaluated: {metrics.total_predictions}")
```

#### Get Per-Disease Metrics
```python
disease_metrics = evaluation_scorer.get_per_disease_metrics(days_back=30)

for disease_id, metrics in disease_metrics.items():
    print(f"{disease_id}:")
    print(f"  Accuracy: {metrics['accuracy']:.1%}")
    print(f"  Samples: {metrics['samples']}")
    print(f"  FPR: {metrics['false_positive_rate']:.1%}")
```

#### Detect Model Drift
```python
drift = evaluation_scorer.detect_model_drift(days_back=7)

if drift.drift_detected:
    print(f"⚠️ Drift Detected! Severity: {drift.drift_severity}")
    print(f"Accuracy Change: {drift.accuracy_change_percent:+.1f}%")
    print(f"Trend: {drift.confidence_trend}")
```

#### Generate Evaluation Report
```python
report = evaluation_scorer.get_evaluation_report(days_back=30)

print(f"Overall Accuracy: {report['overall_metrics']['accuracy']}")
print(f"Top Performing Diseases: {report['per_disease_performance']['top_5']}")
print(f"Drift Detected: {report['model_drift_indicators']['drift_detected']}")
print(f"Recommendations: {report['recommendations']}")
```

### API Endpoints

#### Record Outcome
```http
POST /v1/evaluation/record-outcome/{diagnosis_id}?actual_disease=wheat_leaf_rust&notes=Expert+confirmed

Response:
{
    "success": true,
    "diagnosis_id": "diag-123",
    "actual_disease": "wheat_leaf_rust",
    "message": "Outcome recorded for evaluation"
}
```

#### Get Accuracy Metrics
```http
GET /v1/evaluation/accuracy-metrics?days_back=30

Response:
{
    "period_days": 30,
    "total_evaluated": 287,
    "correct": 247,
    "accuracy": "86.1%",
    "high_confidence_accuracy": "91.3%",
    "medium_confidence_accuracy": "82.5%",
    "low_confidence_accuracy": "65.2%",
    "confidence_mean": "0.78",
    "confidence_std": "0.15",
    "calibration_score": "0.87"
}
```

#### Get Per-Disease Metrics
```http
GET /v1/evaluation/per-disease-metrics?days_back=30

Response:
{
    "period_days": 30,
    "disease_metrics": {
        "wheat_leaf_rust": {
            "samples": 45,
            "correct": 41,
            "accuracy": 0.911,
            "avg_confidence": 0.87,
            "std_confidence": 0.11,
            "false_positive_rate": 0.05
        },
        ...
    },
    "total_diseases": 8
}
```

#### Detect Model Drift
```http
GET /v1/evaluation/model-drift?recent_days=7

Response:
{
    "drift_detected": false,
    "drift_severity": "none",
    "recent_accuracy": "87.3%",
    "historical_accuracy": "86.1%",
    "accuracy_change": "+1.4%",
    "confidence_trend": "stable",
    "false_positive_rate": "4.2%",
    "false_negative_rate": "8.5%",
    "alert": "✅ Model performance stable"
}
```

#### Get Comprehensive Report
```http
GET /v1/evaluation/report?days_back=30

Response:
{
    "report_period_days": 30,
    "generated_at": "2025-01-13T10:30:00",
    "overall_metrics": {
        "total_evaluated": 287,
        "accuracy": "86.1%",
        "correct_predictions": 247,
        "high_conf_accuracy": "91.3%",
        "medium_conf_accuracy": "82.5%",
        "low_conf_accuracy": "65.2%",
        "confidence_calibration": "0.87"
    },
    "per_disease_performance": {
        "top_5": [
            {
                "disease": "wheat_leaf_rust",
                "accuracy": "91.1%",
                "samples": 45
            }
        ],
        "worst_5": [...],
        "total_diseases_evaluated": 8
    },
    "model_drift_indicators": {
        "7day_accuracy": "87.3%",
        "30day_accuracy": "86.1%",
        "accuracy_change": "+1.4%",
        "confidence_trend": "stable",
        "false_positive_rate": "4.2%",
        "false_negative_rate": "8.5%",
        "drift_detected": false,
        "drift_severity": "none"
    },
    "recommendations": [
        "Model performance is healthy. No action needed."
    ]
}
```

#### Get Evaluation Statistics
```http
GET /v1/evaluation/statistics

Response:
{
    "total_predictions": 450,
    "evaluated_predictions": 287,
    "unevaluated_predictions": 163,
    "evaluation_rate": 0.638,
    "timestamp": "2025-01-13T10:30:00"
}
```

---

## Integration Points

### In Diagnosis Service

When a diagnosis is created, the following integrations occur automatically:

1. **Field Memory**: Records diagnosis in field-specific history
2. **Evaluation Scorer**: Scores the prediction for future evaluation
3. **Context Compression**: Compresses field context (on demand)

```python
# In diagnosis_service.py diagnose() method:

# 1. Record in field memory
field_memory.record_diagnosis(
    field_id=field_id,
    diagnosis_id=diagnosis_id,
    disease_id=disease_key,
    disease_name_ar=disease_info["name_ar"],
    confidence=confidence,
    severity=severity.value,
    affected_area_percent=min(confidence * 100, 100),
)

# 2. Score for evaluation
evaluation_scorer.score_prediction(
    diagnosis_id=diagnosis_id,
    predicted_disease=disease_key,
    predicted_confidence=confidence,
    field_id=field_id,
)
```

### Configuration

All services are singletons and configured in `src/services/__init__.py`:

```python
from .context_compression import context_compression_service
from .field_memory import field_memory
from .evaluation_scorer import evaluation_scorer
```

---

## Performance Characteristics

### Memory Usage

- **Field Memory**: ~5KB per field history entry (100 max per field)
- **Evaluation Scorer**: ~1KB per prediction score
- **Context Compression**: On-demand, minimal cache overhead

### Processing Time

- **Image Compression**: 50-150ms per image
- **Field Context Compression**: 10-50ms per field
- **Field Health Metrics Calculation**: 5-20ms per field
- **Accuracy Metrics Calculation**: 20-100ms for 1000 predictions
- **Drift Detection**: 50-200ms

### Scalability

- **Fields Tracked**: Unlimited (limited by available memory)
- **Predictions Evaluated**: Unlimited (limited by available memory)
- **Lookback Period**: Configurable (default 90 days)
- **Per-Field History**: Max 100 records (configurable)

---

## Monitoring & Alerts

### Key Metrics to Monitor

1. **Field Health Score**: Trend towards 0 indicates increasing disease pressure
2. **Model Accuracy**: Should remain > 85% for production use
3. **Confidence Calibration**: Should be > 0.7 for reliable predictions
4. **Model Drift**: Severity should remain "none"
5. **Treatment Effectiveness**: Should be > 80% for validated treatments

### Drift Detection Thresholds

- **Mild**: Accuracy drop 2-5%
- **Moderate**: Accuracy drop 5-10%
- **Severe**: Accuracy drop > 10%

### Recommended Actions

| Condition | Action |
|-----------|--------|
| Accuracy < 70% | Retrain model |
| Drift detected | Investigate new disease patterns |
| Calibration < 0.5 | Adjust confidence thresholds |
| FPR > 20% | Review false positive cases |
| FNR > 15% | Add training data for missed cases |

---

## Future Enhancements

1. **Persistent Storage**: Migrate field memory and prediction scores to PostgreSQL
2. **Real-time Streaming**: Stream metrics to monitoring dashboard
3. **Automated Retraining**: Trigger model retraining on drift detection
4. **A/B Testing**: Support multiple model versions in parallel
5. **Federated Learning**: Aggregate patterns across multiple regions
6. **Seasonal Models**: Train separate models for different seasons

---

## References

- **Context Compression**: `src/services/context_compression.py`
- **Field Memory**: `src/services/field_memory.py`
- **Evaluation Scorer**: `src/services/evaluation_scorer.py`
- **Main Service**: `src/main.py`
- **Services Init**: `src/services/__init__.py`

---

_Last Updated: January 2025_
