# Research Core - خدمة البحث العلمي

## نظرة عامة | Overview

خدمة دعم البحث العلمي الزراعي وإدارة التجارب والدراسات الميدانية.

Agricultural research support service for managing experiments and field studies.

**Port:** 8102
**Version:** 15.4.0

---

## الميزات | Features

### التجارب | Experiments

| النوع        | Type              | الوصف           |
| ------------ | ----------------- | --------------- |
| تجارب صنفية  | Variety Trials    | مقارنة أصناف    |
| تجارب تسميد  | Fertilizer Trials | اختبار أسمدة    |
| تجارب ري     | Irrigation Trials | طرق ري          |
| تجارب مبيدات | Pesticide Trials  | فعالية المبيدات |

### التحليل | Analysis

| الميزة       | Feature              | الوصف             |
| ------------ | -------------------- | ----------------- |
| تحليل إحصائي | Statistical Analysis | ANOVA, t-test     |
| تصميم تجارب  | Experiment Design    | RCB, Latin Square |
| تقارير علمية | Scientific Reports   | تقارير بحثية      |

---

## API Endpoints

### التجارب | Experiments

```http
# إنشاء تجربة
POST /experiments
{
    "title": "مقارنة أصناف القمح اليمني",
    "title_en": "Yemeni Wheat Variety Comparison",
    "type": "variety_trial",
    "design": {
        "type": "rcbd",
        "replications": 4,
        "treatments": ["local", "improved_1", "improved_2"],
        "plot_size_m2": 25
    },
    "field_id": "field-001",
    "start_date": "2024-01-15",
    "end_date": "2024-05-30",
    "researcher": {
        "name": "د. أحمد علي",
        "institution": "مركز البحوث الزراعية"
    }
}

# جلب التجارب
GET /experiments?status=active&type=variety_trial

# تفاصيل تجربة
GET /experiments/{experiment_id}

# تحديث تجربة
PATCH /experiments/{experiment_id}
{
    "status": "data_collection"
}
```

### المعاملات | Treatments

```http
# إضافة معاملة
POST /experiments/{experiment_id}/treatments
{
    "name": "الصنف المحلي",
    "name_en": "Local Variety",
    "code": "T1",
    "description": "صنف القمح المحلي اليمني"
}

# جلب المعاملات
GET /experiments/{experiment_id}/treatments
```

### القياسات | Observations

```http
# تسجيل قياس
POST /experiments/{experiment_id}/observations
{
    "treatment_code": "T1",
    "replication": 1,
    "date": "2024-03-15",
    "variables": {
        "plant_height_cm": 85.5,
        "tillers_count": 4,
        "leaf_area_cm2": 45.2,
        "chlorophyll_spad": 42.5
    },
    "notes": "نمو جيد"
}

# جلب القياسات
GET /experiments/{experiment_id}/observations?treatment=T1

# تصدير القياسات
GET /experiments/{experiment_id}/observations/export?format=csv
```

### التحليل الإحصائي | Statistical Analysis

```http
# تحليل ANOVA
POST /experiments/{experiment_id}/analysis/anova
{
    "variable": "yield_kg_ha",
    "confidence_level": 0.95
}

Response:
{
    "experiment_id": "exp-001",
    "variable": "yield_kg_ha",
    "anova": {
        "source": [
            {"name": "Treatment", "df": 2, "ss": 450000, "ms": 225000, "f": 15.2, "p_value": 0.0003},
            {"name": "Replication", "df": 3, "ss": 25000, "ms": 8333, "f": 0.56, "p_value": 0.65},
            {"name": "Error", "df": 6, "ss": 89000, "ms": 14833}
        ],
        "cv_percent": 8.5,
        "r_squared": 0.84
    },
    "means": {
        "T1": {"mean": 3200, "se": 61},
        "T2": {"mean": 3800, "se": 58},
        "T3": {"mean": 3550, "se": 65}
    },
    "lsd_0.05": 245,
    "significant_differences": ["T1-T2", "T1-T3"]
}

# مقارنة المتوسطات
POST /experiments/{experiment_id}/analysis/means-comparison
{
    "variable": "yield_kg_ha",
    "method": "tukey"
}

# تحليل الارتباط
POST /experiments/{experiment_id}/analysis/correlation
{
    "variables": ["plant_height_cm", "tillers_count", "yield_kg_ha"]
}
```

### التقارير | Reports

```http
# إنشاء تقرير
POST /experiments/{experiment_id}/reports
{
    "type": "final",
    "sections": ["introduction", "methods", "results", "conclusion"],
    "format": "pdf"
}

# جلب التقارير
GET /experiments/{experiment_id}/reports

# تنزيل تقرير
GET /reports/{report_id}/download
```

### مشاركة البيانات | Data Sharing

```http
# مشاركة تجربة
POST /experiments/{experiment_id}/share
{
    "access_level": "view",
    "users": ["user-002", "user-003"],
    "expires_at": "2024-12-31"
}

# البيانات المفتوحة
POST /experiments/{experiment_id}/publish
{
    "license": "cc-by-4.0",
    "doi_request": true
}
```

---

## نماذج البيانات | Data Models

### Experiment

```json
{
  "id": "exp-001",
  "title": "مقارنة أصناف القمح اليمني",
  "title_en": "Yemeni Wheat Variety Comparison",
  "type": "variety_trial",
  "status": "data_collection",
  "design": {
    "type": "rcbd",
    "replications": 4,
    "treatments_count": 3,
    "plot_size_m2": 25,
    "total_plots": 12
  },
  "field_id": "field-001",
  "location": {
    "region": "صنعاء",
    "coordinates": { "lat": 15.35, "lng": 44.15 }
  },
  "dates": {
    "start": "2024-01-15",
    "end": "2024-05-30",
    "planting": "2024-01-20",
    "harvest": "2024-05-25"
  },
  "researcher": {
    "name": "د. أحمد علي",
    "institution": "مركز البحوث الزراعية"
  },
  "created_at": "2024-01-10T00:00:00Z"
}
```

### Observation

```json
{
  "id": "obs-001",
  "experiment_id": "exp-001",
  "treatment_code": "T1",
  "replication": 1,
  "plot_number": 3,
  "date": "2024-03-15",
  "growth_stage": "heading",
  "variables": {
    "plant_height_cm": 85.5,
    "tillers_count": 4,
    "leaf_area_cm2": 45.2,
    "chlorophyll_spad": 42.5,
    "pest_damage_score": 1
  },
  "observer_id": "user-001",
  "notes": "نمو جيد، لا توجد إصابات",
  "created_at": "2024-03-15T10:30:00Z"
}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8102
HOST=0.0.0.0

# قاعدة البيانات
DATABASE_URL=postgresql://...

# التخزين
S3_BUCKET=sahool-research-data

# التحليل
R_SERVICE_URL=http://r-service:8200
```

---

## Health Check

```http
GET /healthz

Response:
{
    "status": "healthy",
    "service": "research-core",
    "version": "15.4.0"
}
```

---

## الترخيص | License

Proprietary - KAFAAT © 2024
