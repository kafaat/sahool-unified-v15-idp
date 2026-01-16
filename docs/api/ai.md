# AI/Analysis APIs

# واجهات برمجة تطبيقات الذكاء الاصطناعي

## Overview | نظرة عامة

AI and Analysis APIs provide intelligent agricultural advisory and analysis:

- Multi-agent AI system for agricultural questions
- Crop health analysis and disease detection
- Yield prediction
- Irrigation optimization
- Fertilizer recommendations
- RAG-based knowledge retrieval

توفر واجهات الذكاء الاصطناعي والتحليل استشارات وتحليلات زراعية ذكية:

- نظام ذكاء اصطناعي متعدد الوكلاء للأسئلة الزراعية
- تحليل صحة المحاصيل واكتشاف الأمراض
- التنبؤ بالمحصول
- تحسين الري
- توصيات الأسمدة
- استرجاع المعرفة القائم على RAG

## Base URLs

**AI Advisor:** `http://localhost:8083`
**Crop Health AI:** `http://localhost:8089`
**Agro Advisor:** `http://localhost:8084`

## AI Advisor | المستشار الذكي

Multi-agent system for comprehensive agricultural advisory.

### POST /api/v1/ask

Ask a general agricultural question.

**Request Body:**

```json
{
  "question": "What is the best time to plant wheat in Sanaa?",
  "language": "en",
  "context": {
    "field_id": "field-123",
    "location": "sanaa",
    "current_season": "winter"
  }
}
```

**Response:**

```json
{
  "answer": "The best time to plant wheat in Sanaa is from mid-October to mid-November. This timing allows the crop to benefit from winter rains and cooler temperatures during the growing season.",
  "answer_ar": "أفضل وقت لزراعة القمح في صنعاء هو من منتصف أكتوبر إلى منتصف نوفمبر...",
  "confidence": 0.92,
  "sources": [
    "Yemen Agricultural Research",
    "Local Farming Practices Database"
  ],
  "agent": "field_analyst",
  "follow_up_questions": [
    "What wheat variety is recommended for Sanaa?",
    "How much irrigation does wheat need?"
  ]
}
```

### POST /api/v1/diagnose

Diagnose crop diseases from symptoms or images.

**Request Body:**

```json
{
  "crop_type": "wheat",
  "symptoms": {
    "leaf_color": "yellow_spots",
    "leaf_texture": "powdery_coating",
    "stem_condition": "normal",
    "severity": "moderate"
  },
  "image_path": "/uploads/crop-image-123.jpg",
  "location": "sanaa"
}
```

**Response:**

```json
{
  "diagnosis": {
    "disease": "powdery_mildew",
    "disease_name_en": "Powdery Mildew",
    "disease_name_ar": "البياض الدقيقي",
    "confidence": 0.87,
    "severity": "moderate",
    "description": "Fungal disease causing white powdery growth on leaves",
    "description_ar": "مرض فطري يسبب نموًا أبيض مسحوقيًا على الأوراق"
  },
  "treatment": {
    "immediate_actions": [
      "Remove heavily infected leaves",
      "Improve air circulation"
    ],
    "chemical_treatment": {
      "fungicide": "Sulfur-based fungicide",
      "dosage": "3 g/L water",
      "frequency": "Every 7-10 days",
      "duration": "2-3 applications"
    },
    "organic_treatment": {
      "method": "Neem oil spray",
      "dosage": "5 ml/L water",
      "frequency": "Weekly"
    },
    "preventive_measures": [
      "Avoid overhead irrigation",
      "Plant resistant varieties",
      "Maintain proper spacing"
    ]
  },
  "estimated_yield_impact": {
    "if_treated": -5,
    "if_untreated": -25,
    "unit": "percent"
  }
}
```

### POST /api/v1/recommend

Get recommendations for irrigation, fertilization, or pest management.

**Request Body:**

```json
{
  "crop_type": "wheat",
  "growth_stage": "tillering",
  "recommendation_type": "fertilizer",
  "field_data": {
    "soil_type": "loamy",
    "soil_ph": 7.2,
    "area_hectares": 5.5,
    "last_fertilization": "2024-01-01"
  }
}
```

**Response:**

```json
{
  "recommendations": [
    {
      "type": "nitrogen_application",
      "priority": "high",
      "timing": "now",
      "details": {
        "fertilizer": "Urea (46-0-0)",
        "rate_kg_ha": 80,
        "total_amount_kg": 440,
        "application_method": "broadcast",
        "timing_note": "Apply during tillering stage for optimal uptake"
      },
      "rationale": "Wheat requires high nitrogen during tillering for strong stem development",
      "rationale_ar": "يحتاج القمح إلى نيتروجين عالي أثناء مرحلة التفريع لتطوير ساق قوي",
      "expected_benefit": "15-20% yield increase",
      "cost_estimate_yer": 26400
    }
  ]
}
```

### POST /api/v1/analyze-field

Comprehensive field analysis combining multiple data sources.

**Request Body:**

```json
{
  "field_id": "field-123",
  "crop_type": "wheat",
  "analysis_types": [
    "crop_health",
    "yield_prediction",
    "irrigation_needs",
    "pest_risk"
  ]
}
```

**Response:**

```json
{
  "field_id": "field-123",
  "analysis_date": "2024-01-15",
  "crop_health": {
    "overall_score": 78,
    "status": "good",
    "issues": [
      {
        "type": "minor_stress",
        "location": "northwest_corner",
        "severity": "low"
      }
    ]
  },
  "yield_prediction": {
    "predicted_yield_kg_ha": 3200,
    "confidence": 0.84,
    "factors": {
      "weather": "favorable",
      "soil_health": "good",
      "management": "optimal"
    }
  },
  "irrigation_needs": {
    "next_irrigation": "2024-01-17",
    "amount_mm": 25,
    "frequency_days": 7
  },
  "pest_risk": {
    "overall_risk": "low",
    "pests": [
      {
        "pest": "aphids",
        "risk_level": "low",
        "monitoring_recommended": true
      }
    ]
  }
}
```

## Crop Health Analysis | تحليل صحة المحاصيل

### POST /api/v1/health/analyze

Analyze crop health from satellite imagery or field data.

**Request Body:**

```json
{
  "field_id": "field-123",
  "analysis_date": "2024-01-15",
  "data_sources": ["ndvi", "field_sensors", "visual_inspection"]
}
```

**Response:**

```json
{
  "field_id": "field-123",
  "analysis_date": "2024-01-15",
  "overall_health_score": 82,
  "health_status": "good",
  "ndvi_analysis": {
    "average_ndvi": 0.72,
    "healthy_area_pct": 85,
    "stressed_area_pct": 10,
    "bare_soil_pct": 5,
    "zones": [
      {
        "zone_id": "zone-1",
        "ndvi": 0.75,
        "health": "excellent"
      }
    ]
  },
  "recommendations": [
    {
      "action": "Investigate zone-3 for water stress",
      "priority": "medium",
      "details": "NDVI below 0.4 indicates potential irrigation issues"
    }
  ]
}
```

## Yield Prediction | التنبؤ بالمحصول

### POST /api/v1/yield/predict

Predict crop yield based on current conditions.

**Request Body:**

```json
{
  "field_id": "field-123",
  "crop_type": "wheat",
  "planting_date": "2023-11-15",
  "area_hectares": 5.5,
  "current_growth_stage": "grain_filling",
  "weather_data": {
    "avg_temperature_c": 25,
    "total_precipitation_mm": 250,
    "sunny_days": 45
  }
}
```

**Response:**

```json
{
  "field_id": "field-123",
  "predicted_yield_kg": 17600,
  "predicted_yield_kg_ha": 3200,
  "confidence_interval": {
    "lower_kg": 15840,
    "upper_kg": 19360,
    "confidence_pct": 90
  },
  "factors": {
    "weather_impact": 0.95,
    "soil_health_impact": 0.88,
    "management_impact": 0.92
  },
  "harvest_date_estimate": "2024-04-20",
  "quality_prediction": {
    "grade": "A",
    "protein_content_pct": 12.5
  }
}
```

## Data Models | نماذج البيانات

### AI Question Request

```typescript
interface QuestionRequest {
  question: string;
  language: "en" | "ar";
  context?: {
    field_id?: string;
    location?: string;
    crop_type?: string;
    [key: string]: any;
  };
}
```

### Disease Diagnosis

```typescript
interface DiagnosisResult {
  diagnosis: {
    disease: string;
    disease_name_en: string;
    disease_name_ar: string;
    confidence: number;
    severity: "low" | "moderate" | "high" | "critical";
  };
  treatment: {
    immediate_actions: string[];
    chemical_treatment?: TreatmentDetails;
    organic_treatment?: TreatmentDetails;
    preventive_measures: string[];
  };
  estimated_yield_impact: {
    if_treated: number;
    if_untreated: number;
  };
}
```

---

_Last updated: 2026-01-02_
