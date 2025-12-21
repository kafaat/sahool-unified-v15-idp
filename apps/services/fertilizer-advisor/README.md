# Fertilizer Advisor - مستشار التسميد

## نظرة عامة | Overview

خدمة تقديم توصيات التسميد الذكية بناءً على تحليل التربة واحتياجات المحاصيل.

Smart fertilizer recommendation service based on soil analysis and crop requirements.

**Port:** 8093
**Version:** 15.4.0

---

## الميزات | Features

### التحليل | Analysis
| الميزة | Feature | الوصف |
|--------|---------|--------|
| تحليل التربة | Soil Analysis | تحليل خصائص التربة |
| احتياجات المحصول | Crop Needs | حساب الاحتياجات |
| توصيات مخصصة | Custom Recommendations | خطط تسميد فردية |
| جدولة التسميد | Fertilization Schedule | مواعيد التطبيق |

### العناصر | Nutrients
| العنصر | Element | الرمز |
|--------|---------|--------|
| نيتروجين | Nitrogen | N |
| فوسفور | Phosphorus | P |
| بوتاسيوم | Potassium | K |
| كالسيوم | Calcium | Ca |
| مغنيسيوم | Magnesium | Mg |
| كبريت | Sulfur | S |
| عناصر صغرى | Micronutrients | Fe, Zn, Mn, Cu, B |

---

## API Endpoints

### تحليل التربة | Soil Analysis

```http
# إدخال نتائج تحليل التربة
POST /soil-analysis
{
    "field_id": "field-001",
    "analysis_date": "2024-01-15",
    "lab_name": "مختبر الزراعة المركزي",
    "results": {
        "ph": 7.2,
        "ec_ds_m": 1.5,
        "organic_matter_percent": 2.1,
        "nitrogen_ppm": 45,
        "phosphorus_ppm": 22,
        "potassium_ppm": 180,
        "calcium_ppm": 2500,
        "magnesium_ppm": 350,
        "texture": "sandy_loam"
    }
}

# جلب تحليل التربة
GET /fields/{field_id}/soil-analysis?latest=true

# تاريخ التحليلات
GET /fields/{field_id}/soil-analysis/history
```

### التوصيات | Recommendations

```http
# الحصول على توصيات التسميد
POST /recommendations
{
    "field_id": "field-001",
    "crop_type": "wheat",
    "growth_stage": "tillering",
    "target_yield_kg_ha": 4000,
    "irrigation_method": "drip"
}

Response:
{
    "field_id": "field-001",
    "recommendations": {
        "nitrogen": {
            "total_kg_ha": 150,
            "current_application_kg_ha": 40,
            "source": "يوريا 46%",
            "amount_kg_ha": 87,
            "timing": "فوري - مرحلة التفريع"
        },
        "phosphorus": {
            "total_kg_ha": 60,
            "current_application_kg_ha": 0,
            "source": "سوبر فوسفات ثلاثي",
            "amount_kg_ha": 130,
            "timing": "تم التطبيق عند الزراعة"
        },
        "potassium": {
            "total_kg_ha": 80,
            "current_application_kg_ha": 25,
            "source": "سلفات البوتاسيوم",
            "amount_kg_ha": 50,
            "timing": "بعد أسبوعين"
        }
    },
    "schedule": [...],
    "estimated_cost_sar": 850
}
```

### خطة التسميد | Fertilization Plan

```http
# إنشاء خطة موسمية
POST /fertilization-plan
{
    "field_id": "field-001",
    "crop_type": "wheat",
    "season": "2024_winter",
    "planting_date": "2024-01-15",
    "target_yield_kg_ha": 4000
}

Response:
{
    "plan_id": "plan-001",
    "applications": [
        {
            "stage": "قبل الزراعة",
            "date": "2024-01-10",
            "fertilizers": [
                {
                    "name": "DAP 18-46-0",
                    "amount_kg_ha": 100,
                    "method": "نثر وخلط"
                }
            ]
        },
        {
            "stage": "التفريع",
            "date": "2024-02-15",
            "fertilizers": [
                {
                    "name": "يوريا 46%",
                    "amount_kg_ha": 50,
                    "method": "رش مع الري"
                }
            ]
        },
        {
            "stage": "الإزهار",
            "date": "2024-03-20",
            "fertilizers": [
                {
                    "name": "NPK 20-20-20",
                    "amount_kg_ha": 30,
                    "method": "رش ورقي"
                }
            ]
        }
    ],
    "total_cost_sar": 2500
}

# جلب الخطة
GET /fertilization-plan/{plan_id}

# تسجيل تطبيق
POST /fertilization-plan/{plan_id}/applications/{app_id}/record
{
    "applied_date": "2024-02-15",
    "actual_amount_kg_ha": 48,
    "notes": "تم التطبيق صباحاً"
}
```

### الأسمدة | Fertilizers

```http
# قائمة الأسمدة المتاحة
GET /fertilizers?type=nitrogen

# تفاصيل سماد
GET /fertilizers/{fertilizer_id}

# حساب الكمية
POST /fertilizers/calculate
{
    "fertilizer_id": "urea-46",
    "nutrient": "N",
    "required_kg_ha": 50
}

Response:
{
    "fertilizer": "يوريا 46%",
    "nutrient_content_percent": 46,
    "required_amount_kg_ha": 108.7,
    "cost_per_kg_sar": 2.5,
    "total_cost_sar": 271.75
}
```

---

## نماذج البيانات | Data Models

### SoilAnalysis
```json
{
    "id": "analysis-001",
    "field_id": "field-001",
    "analysis_date": "2024-01-15",
    "results": {
        "ph": 7.2,
        "ec_ds_m": 1.5,
        "organic_matter_percent": 2.1,
        "nutrients": {
            "N": {"value": 45, "unit": "ppm", "status": "low"},
            "P": {"value": 22, "unit": "ppm", "status": "adequate"},
            "K": {"value": 180, "unit": "ppm", "status": "adequate"}
        },
        "texture": {
            "sand_percent": 55,
            "silt_percent": 30,
            "clay_percent": 15,
            "class": "sandy_loam"
        }
    },
    "interpretation": {
        "ph_status": "قلوي قليلاً",
        "salinity_status": "طبيعي",
        "fertility_rating": "متوسطة"
    }
}
```

### FertilizerRecommendation
```json
{
    "nutrient": "N",
    "deficiency_kg_ha": 50,
    "recommended_source": {
        "id": "urea-46",
        "name": "يوريا 46%",
        "name_en": "Urea 46%"
    },
    "application": {
        "amount_kg_ha": 108.7,
        "method": "fertigation",
        "timing": "مرحلة التفريع",
        "splits": 2
    }
}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8093
HOST=0.0.0.0

# قاعدة البيانات
DATABASE_URL=postgresql://...
REDIS_URL=redis://redis:6379
NATS_URL=nats://nats:4222

# الحدود
DEFAULT_YIELD_TARGET=3500
```

---

## Health Check

```http
GET /healthz

Response:
{
    "status": "healthy",
    "service": "fertilizer-advisor",
    "version": "15.4.0"
}
```

---

## الترخيص | License

Proprietary - KAFAAT © 2024
