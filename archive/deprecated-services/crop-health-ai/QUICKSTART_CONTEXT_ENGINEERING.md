# Quick Start: Context Engineering Features

## Get Started in 5 Minutes

### 1. Field Health Monitoring

Check the health of a specific field:

```bash
# Get field health metrics
curl http://localhost:8095/v1/field/field-001/health

# Response:
{
  "field_id": "field-001",
  "health_score": "0.85",
  "total_diagnoses": 25,
  "healthy_diagnoses": 21,
  "infected_diagnoses": 4,
  "infection_trend": "improving",
  "dominant_disease": "wheat_leaf_rust",
  "disease_variety": 2,
  "avg_confidence": "0.88"
}
```

### 2. Disease Pattern Analysis

Understand what diseases have affected a field:

```bash
# Get disease patterns
curl http://localhost:8095/v1/field/field-001/disease-patterns

# Response shows:
# - How many times each disease occurred
# - Average confidence for each disease
# - Severity distribution
# - Days between occurrences
```

### 3. Risk Assessment

Get actionable risk insights:

```bash
# Get field risk assessment
curl http://localhost:8095/v1/field/field-001/risk-assessment

# Response shows:
# - Overall risk score (0-1)
# - Risk level (low/medium/high/critical)
# - Top threats (diseases likely to recur)
# - Health trend (improving/stable/worsening)
```

### 4. Treatment Success Tracking

Monitor how well treatments are working:

```bash
# Mark a diagnosis as treated
curl -X POST http://localhost:8095/v1/field/field-001/diagnosis/diag-123/mark-treated

# Get treatment effectiveness
curl http://localhost:8095/v1/field/field-001/treatment-effectiveness

# Response shows:
# - Treatments applied: 8
# - Successful treatments: 7
# - Effectiveness rate: 87.5%
# - Average recovery days: 12
```

### 5. Model Performance Evaluation

Track prediction accuracy over time:

```bash
# After expert review confirms actual disease:
curl -X POST "http://localhost:8095/v1/evaluation/record-outcome/diag-123?actual_disease=wheat_leaf_rust"

# Get overall accuracy metrics
curl http://localhost:8095/v1/evaluation/accuracy-metrics?days_back=30

# Response shows:
# - Overall accuracy: 87.3%
# - High confidence accuracy: 92.1%
# - Low confidence accuracy: 71.5%
# - Confidence calibration: 0.88
```

### 6. Model Drift Detection

Check if model performance is degrading:

```bash
# Detect model drift
curl http://localhost:8095/v1/evaluation/model-drift?recent_days=7

# Response shows:
# - Drift detected: false
# - Recent accuracy: 87.3%
# - Historical accuracy: 86.1%
# - Accuracy change: +1.4%
# - Alert status: ✅ Model performance stable
```

---

## Common Use Cases

### Use Case 1: Weekly Field Health Report

```python
import requests

field_id = "field-001"
base_url = "http://localhost:8095"

# Get all field data
health = requests.get(f"{base_url}/v1/field/{field_id}/health").json()
patterns = requests.get(f"{base_url}/v1/field/{field_id}/disease-patterns").json()
risk = requests.get(f"{base_url}/v1/field/{field_id}/risk-assessment").json()

# Generate report
print(f"Field {field_id} Weekly Report")
print(f"Health Score: {health['health_score']}")
print(f"Trend: {health['infection_trend']}")
print(f"Risk Level: {risk['risk_level']}")
print(f"Top Threats: {[t['disease_name_ar'] for t in risk['top_threats']]}")
```

### Use Case 2: Monitor Treatment Success

```python
# When farmer applies treatment
diagnosis_id = "diag-123"

# Mark as treated
requests.post(f"{base_url}/v1/field/{field_id}/diagnosis/{diagnosis_id}/mark-treated")

# Follow up after 2 weeks
effectiveness = requests.get(f"{base_url}/v1/field/{field_id}/treatment-effectiveness").json()

if effectiveness['effectiveness_rate'] > 0.8:
    print("Treatment is working well!")
else:
    print("Treatment effectiveness is low. Consider alternatives.")
```

### Use Case 3: Expert Review & Evaluation

```python
# After expert reviews diagnosis and confirms actual disease
actual_disease = "wheat_leaf_rust"
diagnosis_id = "diag-123"
notes = "Expert confirmed. Severity consistent with field history."

# Record outcome
requests.post(
    f"{base_url}/v1/evaluation/record-outcome/{diagnosis_id}",
    params={
        "actual_disease": actual_disease,
        "notes": notes
    }
)

# Check if model is performing well
metrics = requests.get(f"{base_url}/v1/evaluation/accuracy-metrics?days_back=30").json()

if metrics['accuracy'] < 0.85:
    print("⚠️ Model accuracy below 85%. Consider retraining.")
```

### Use Case 4: Predict Disease Recurrence

```python
# Get disease patterns to understand recurrence
patterns = requests.get(f"{base_url}/v1/field/{field_id}/disease-patterns").json()

for pattern in patterns['patterns']:
    disease = pattern['disease_id']
    avg_interval = pattern.get('avg_days_between', 30)
    last_occurred = pattern['last_occurred']

    # Calculate days since last occurrence
    from datetime import datetime
    last_date = datetime.fromisoformat(last_occurred.replace('Z', '+00:00'))
    days_since = (datetime.utcnow() - last_date).days

    # If close to typical interval, disease may recur soon
    if 0.5 < days_since / avg_interval < 1.5:
        print(f"⚠️ {disease} may recur soon! Last occurred {days_since} days ago.")
```

### Use Case 5: Generate Performance Report

```python
# Get comprehensive evaluation report
report = requests.get(f"{base_url}/v1/evaluation/report?days_back=30").json()

print("Performance Report")
print(f"Accuracy: {report['overall_metrics']['accuracy']}")
print(f"Calibration: {report['overall_metrics']['confidence_calibration']}")
print(f"Drift: {report['model_drift_indicators']['drift_detected']}")

print("\nTop Performing Diseases:")
for disease in report['per_disease_performance']['top_5']:
    print(f"  {disease['disease']}: {disease['accuracy']}")

print("\nRecommendations:")
for rec in report['recommendations']:
    print(f"  - {rec}")
```

---

## API Response Examples

### Field Health Response
```json
{
  "field_id": "field-001",
  "health_score": "0.78",
  "total_diagnoses": 15,
  "healthy_diagnoses": 12,
  "infected_diagnoses": 3,
  "infection_trend": "improving",
  "dominant_disease": "wheat_leaf_rust",
  "disease_variety": 2,
  "avg_confidence": "0.87",
  "last_updated": "2025-01-13T10:30:00"
}
```

### Risk Assessment Response
```json
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
  ],
  "last_updated": "2025-01-13T10:30:00"
}
```

### Accuracy Metrics Response
```json
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

### Model Drift Response
```json
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

---

## Key Concepts

### Health Score
- **Range**: 0-1 (higher is better)
- **Meaning**: Ratio of healthy diagnoses to total diagnoses
- **Action**: Score < 0.5 indicates serious disease pressure

### Infection Trend
- **Improving**: Recently more healthy diagnoses than before
- **Stable**: Ratio of healthy/diseased relatively constant
- **Worsening**: Recently more diseased diagnoses than before
- **Action**: Worsening trend may indicate new disease introduction

### Risk Score
- **Range**: 0-1 (higher is riskier)
- **Inverse of Health Score**: 1 - health_score
- **Boosted by**: Worsening trend, multiple disease variety
- **Action**: Risk > 0.7 = critical intervention needed

### Disease Frequency
- **Definition**: How many times a disease was detected in history
- **Used for**: Predicting recurrence likelihood
- **Example**: If wheat_leaf_rust detected 5 times, it's a persistent threat

### Temporal Pattern
- **Persistent**: > 70% of recent diagnoses are diseased
- **Seasonal**: 40-70% of recent diagnoses are diseased
- **Sporadic**: 10-40% of recent diagnoses are diseased
- **Improving**: < 10% of recent diagnoses are diseased

### Accuracy Metrics
- **Overall Accuracy**: Correct predictions / Total predictions
- **Confidence Levels**: Measured by prediction confidence buckets
- **Calibration**: How well confidence aligns with actual accuracy
- **Action**: Calibration < 0.5 means model is not trustworthy

### Model Drift
- **Mild**: 2-5% accuracy drop
- **Moderate**: 5-10% accuracy drop
- **Severe**: > 10% accuracy drop
- **Action**: Severe drift requires model retraining

---

## Troubleshooting

### "Field not found" when accessing health
- Field must have at least one diagnosis recorded
- Check if diagnosis was recorded with correct field_id
- Use `/v1/fields/summary` to see all tracked fields

### Low accuracy metrics
- May need more evaluated diagnoses for accurate metrics
- Use `/v1/evaluation/statistics` to check evaluation rate
- Ensure outcomes are being recorded after expert review

### Model drift detected
- Check `/v1/evaluation/per-disease-metrics` to identify problem diseases
- Consider retraining model with recent data
- Review `/v1/evaluation/report` for detailed recommendations

### Unexpected risk scores
- Risk is calculated from multiple factors (health, trend, variety)
- Use `/v1/field/{field_id}/disease-patterns` to understand why
- Check if recent treatment has reduced disease pressure

---

## Performance Tips

1. **Cache field metrics**: Health metrics are cached, clear cache if data changes
2. **Batch operations**: Use `/v1/fields/summary` instead of querying each field
3. **Limit history queries**: Use date filters to limit data retrieval
4. **Monitor drift regularly**: Check drift detection weekly
5. **Review reports monthly**: Use comprehensive reports for long-term insights

---

## Integration Examples

### Python Integration
```python
import requests
import json

class FieldHealthMonitor:
    def __init__(self, service_url="http://localhost:8095"):
        self.url = service_url

    def get_field_status(self, field_id):
        health = requests.get(f"{self.url}/v1/field/{field_id}/health").json()
        risk = requests.get(f"{self.url}/v1/field/{field_id}/risk-assessment").json()
        return {
            "health_score": health['health_score'],
            "risk_level": risk['risk_level'],
            "status": "⚠️ At Risk" if risk['overall_risk_score'] > 0.5 else "✅ Healthy"
        }

# Usage
monitor = FieldHealthMonitor()
status = monitor.get_field_status("field-001")
print(status)
```

### JavaScript Integration
```javascript
async function getFieldHealth(fieldId) {
  const response = await fetch(`http://localhost:8095/v1/field/${fieldId}/health`);
  const health = await response.json();

  return {
    healthScore: parseFloat(health.health_score),
    trend: health.infection_trend,
    diseaseCount: health.disease_variety
  };
}

// Usage
const health = await getFieldHealth("field-001");
console.log(`Field Health: ${health.healthScore * 100}%`);
```

---

## Next Steps

1. **Deploy to Staging**: Test with real field data
2. **Configure Alerts**: Set up monitoring for drift/health
3. **Enable Expert Review**: Start recording outcomes
4. **Generate Reports**: Use evaluation reports monthly
5. **Plan for Scale**: Consider PostgreSQL migration for production

---

## Additional Resources

- **Full Documentation**: See `CONTEXT_ENGINEERING.md`
- **Architecture Details**: See `ENHANCEMENT_SUMMARY.md`
- **API Endpoints**: Check `src/main.py`
- **Service Code**: See `src/services/` directory

---

_Last Updated: January 2025_
