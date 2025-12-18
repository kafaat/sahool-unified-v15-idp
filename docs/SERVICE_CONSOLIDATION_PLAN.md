# خطة توحيد وتحسين الخدمات - SAHOOL

## نظرة عامة

هذه الخطة تهدف إلى توحيد الخدمات المكررة ودمج أفضل الميزات من كل إصدار.

---

## المرحلة 1: الأولوية العالية (منخفضة المخاطر)

### 1.1 تحسين Weather Core
**المصدر**: `kernel/services/weather_core/`
**للدمج من**: `legacy/archived-versions/kernel-services-v15.3/weather-advanced/`

| الميزة | الوصف | الملف المصدر |
|--------|-------|-------------|
| GDD Calculation | حساب درجات النمو التراكمية | `weather-advanced/src/main.py:calculate_gdd()` |
| ET0 Computation | حساب التبخر-نتح المرجعي | `weather-advanced/src/main.py:calculate_et0()` |
| Spray Windows | اكتشاف نوافذ الرش المناسبة | `weather-advanced/src/main.py:get_spray_windows()` |
| Crop Calendars | تقويمات المحاصيل الموسمية | `weather-advanced/src/main.py:agricultural_calendar` |

**التنفيذ**:
```python
# إضافة endpoints جديدة في weather_core/src/main.py

@app.get("/gdd/{crop}")
async def get_growing_degree_days(crop: str, lat: float, lon: float):
    """حساب درجات النمو التراكمية للمحصول"""
    pass

@app.get("/et0")
async def get_evapotranspiration(lat: float, lon: float):
    """حساب التبخر-نتح المرجعي (Penman-Monteith)"""
    pass

@app.get("/spray-windows")
async def get_spray_windows(lat: float, lon: float, days: int = 7):
    """اكتشاف نوافذ الرش المناسبة"""
    pass
```

---

### 1.2 تحسين NDVI Engine
**المصدر**: `kernel/services/ndvi_engine/`
**للدمج من**: `legacy/archived-versions/kernel-services-v15.3/satellite-service/`

| الميزة | الوصف |
|--------|-------|
| Multi-Satellite | دعم Landsat-8/9, MODIS بالإضافة لـ Sentinel-2 |
| Vegetation Indices | NDWI, EVI, SAVI, LAI, NDMI |
| Band Mapping | خريطة شاملة للنطاقات الطيفية |

**التنفيذ**:
```python
# إضافة في ndvi_engine/src/compute.py

class VegetationIndex(str, Enum):
    NDVI = "ndvi"   # Normalized Difference Vegetation Index
    NDWI = "ndwi"   # Water Index
    EVI = "evi"     # Enhanced Vegetation Index
    SAVI = "savi"   # Soil-Adjusted Vegetation Index
    LAI = "lai"     # Leaf Area Index
    NDMI = "ndmi"   # Moisture Index

class SatelliteSource(str, Enum):
    SENTINEL2 = "sentinel-2"
    LANDSAT8 = "landsat-8"
    LANDSAT9 = "landsat-9"
    MODIS = "modis"
```

---

### 1.3 تحسين Crop Health
**المصدر**: `kernel/services/crop_health/`
**للدمج من**: `legacy/archived-versions/kernel-services-v15.3/crop-health-ai/`

| الميزة | الوصف |
|--------|-------|
| ML Prediction | خدمة التنبؤ بالأمراض باستخدام ML |
| Image Classification | تصنيف صور الأمراض |

**التنفيذ**:
```python
# إضافة src/prediction_service.py

class DiseasePredictionService:
    """خدمة التنبؤ بالأمراض باستخدام ML"""

    async def predict_disease(self, image_data: bytes) -> dict:
        """تنبؤ بالمرض من صورة"""
        pass

    async def predict_severity(self, symptoms: list) -> float:
        """تقدير شدة الإصابة"""
        pass
```

---

## المرحلة 2: الأولوية العالية (متوسطة المخاطر)

### 2.1 تحسين Agro Advisor
**المصدر**: `kernel/services/agro_advisor/`
**للدمج من**: `legacy/archived-versions/kernel-services-v15.3/fertilizer-advisor/`

| الميزة | الوصف |
|--------|-------|
| Soil Analysis | تحليل شامل للتربة (pH, NPK, EC, OM) |
| Yemen Crops DB | قاعدة بيانات 13+ محصول يمني |
| Cost Estimation | تقدير تكاليف الأسمدة بالريال |

**التنفيذ**:
```python
# إضافة src/soil_analysis.py

@dataclass
class SoilAnalysis:
    ph: float           # 0-14
    nitrogen_ppm: float # N
    phosphorus_ppm: float  # P
    potassium_ppm: float   # K
    organic_matter: float  # %
    ec_ds_m: float      # Electrical Conductivity

class SoilAnalyzer:
    def analyze(self, sample: SoilAnalysis) -> dict:
        """تحليل شامل للتربة مع توصيات"""
        pass

    def recommend_fertilizer(self, soil: SoilAnalysis, crop: str) -> list:
        """توصية بالأسمدة المناسبة"""
        pass
```

---

### 2.2 تحقيق IoT Service
**التحقيق مطلوب**: `iot-service` أكبر 5.5x من `iot_gateway`

**المهام**:
1. [ ] مراجعة هيكلية `legacy/kernel-services-v15.3/iot-service/`
2. [ ] تحديد البروتوكولات الإضافية المدعومة
3. [ ] تقييم إمكانية الدمج

---

## المرحلة 3: تحقيق إضافي

### 3.1 Chat Services
**الفرق**: `community-chat` أكبر 44x من `field_chat`

**المهام**:
1. [ ] فحص سبب الحجم الكبير (node_modules؟)
2. [ ] مقارنة Real-time capabilities
3. [ ] تقييم WebSocket implementation

---

## جدول التنفيذ

| المرحلة | الخدمة | الأولوية | المدة المقدرة | المخاطر |
|---------|--------|----------|--------------|---------|
| 1.1 | Weather + GDD/ET0 | 🔴 عالية | Sprint 1 | منخفضة |
| 1.2 | NDVI + Multi-satellite | 🔴 عالية | Sprint 1 | منخفضة |
| 1.3 | Crop Health + ML | 🔴 عالية | Sprint 2 | منخفضة |
| 2.1 | Advisor + Soil | 🟡 متوسطة | Sprint 2 | متوسطة |
| 2.2 | IoT Investigation | 🟡 متوسطة | Sprint 3 | متوسطة |
| 3.1 | Chat Investigation | 🟢 منخفضة | Sprint 4 | عالية |

---

## مصفوفة Source of Truth النهائية

```
kernel/services/
├── weather_core/      ✅ SOT + v15.3 features
├── iot_gateway/       ⚠️ SOT (pending investigation)
├── ndvi_engine/       ✅ SOT + multi-satellite
├── crop_health/       ✅ SOT + ML prediction
├── agro_advisor/      ✅ SOT + soil analysis
├── field_chat/        ⚠️ SOT (pending investigation)
├── field_core/        ✅ SOT (TypeScript)
├── field_ops/         ✅ SOT
├── ws_gateway/        ✅ SOT
└── vector_service/    ✅ SOT + MCP Server
```

---

## الموارد المطلوبة

### Dependencies للدمج:
```txt
# Weather improvements
python-meteostat>=0.2.0  # Historical weather data

# NDVI improvements
sentinelsat>=1.2.0       # Sentinel API
landsatxplore>=0.13.0    # Landsat API

# ML improvements
scikit-learn>=1.3.0
tensorflow-lite>=2.14.0  # Edge inference

# Soil analysis
numpy>=2.0.0
scipy>=1.11.0
```

---

## معايير النجاح

1. **التوحيد**: مصدر حقيقة واحد لكل خدمة
2. **الشمولية**: دمج 100% من الميزات القيمة
3. **التوافق**: Backward compatibility للـ APIs
4. **الأداء**: لا تدهور في الأداء
5. **التوثيق**: توثيق كامل للـ endpoints الجديدة

---

*آخر تحديث: 2024-12-18*
