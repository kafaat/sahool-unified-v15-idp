# خطة تكامل خدمات YOLO26 وتحليل التضاريس
# SAHOOL Platform Integration Plan - YOLO26 & Terrain Analysis

> **Version**: 1.0.0
> **Created**: February 2026
> **Status**: Approved for Implementation
> **Document Owner**: KAFAAT Engineering Team

---

## الملخص التنفيذي | Executive Summary

### Project Overview | نظرة عامة على المشروع

This integration plan outlines the deployment of five new agricultural intelligence services to the SAHOOL platform, introducing advanced computer vision capabilities (YOLO26), terrain analysis, hydrology modeling, land leveling optimization, and edge computing infrastructure for real-time field processing.

هذه الخطة تحدد نشر خمس خدمات ذكاء زراعي جديدة لمنصة سهول، تشمل قدرات الرؤية الحاسوبية المتقدمة (YOLO26)، وتحليل التضاريس، ونمذجة الهيدرولوجيا، وتحسين تسوية الأراضي، والبنية التحتية للحوسبة الطرفية للمعالجة الميدانية الفورية.

### Key Metrics | المقاييس الرئيسية

| Metric | Value | القيمة | المقياس |
|--------|-------|--------|---------|
| **Timeline** | 16 weeks (Feb 1 - May 23, 2026) | 16 أسبوع | **الجدول الزمني** |
| **Budget** | $136,047 USD | 510,176 ريال سعودي | **الميزانية** |
| **Expected ROI** | 120% (Year 1) | 120% | **العائد المتوقع** |
| **New Services** | 5 microservices | 5 خدمات | **الخدمات الجديدة** |
| **New Ports** | 8150-8180 range | نطاق 8150-8180 | **المنافذ الجديدة** |
| **Edge Devices** | 50 Jetson Orin units | 50 وحدة | **أجهزة الحافة** |

### Strategic Goals | الأهداف الاستراتيجية

1. **Pest & Disease Detection | كشف الآفات والأمراض**: Real-time identification of 20+ pest species and 30+ crop diseases with >90% accuracy
2. **Terrain Intelligence | ذكاء التضاريس**: Comprehensive terrain analysis for irrigation planning and land management
3. **Edge Computing | الحوسبة الطرفية**: Sub-second inference at field level without cloud dependency
4. **Cost Optimization | تحسين التكاليف**: Reduce manual scouting costs by 60% and water waste by 25%

---

## نظرة عامة على الخدمات الجديدة | New Services Overview

### Service Summary Table | جدول ملخص الخدمات

| Service | Port | Type | Layer | Description |
|---------|------|------|-------|-------------|
| **YOLO26 Vision Service** | 8150 | Python/FastAPI | Intelligence | Computer vision for pest, disease, weed detection |
| **Terrain Core Service** | 8160 | Python/FastAPI | Intelligence | DEM processing and terrain indicator calculation |
| **Hydrology Service** | 8165 | Python/FastAPI | Intelligence | Drainage network and waterlogging prediction |
| **Leveling Optimizer Service** | 8170 | Python/FastAPI | Decision | Cut/fill volume calculation and cost estimation |
| **Edge Orchestrator Service** | 8180 | Python/FastAPI | Acquisition | Jetson Orin device management and model deployment |

---

### 1. YOLO26 Vision Service (Port 8150)

#### خدمة الرؤية الحاسوبية YOLO26

```yaml
service_name: yolo26-vision-service
name_ar: خدمة الرؤية YOLO26
port: 8150
type: python
framework: FastAPI
layer: intelligence
category: analytics

description: |
  Advanced computer vision service using YOLOv10/v11 architecture
  optimized for agricultural applications. Provides real-time detection
  and classification of pests, diseases, weeds, and crop health indicators.

description_ar: |
  خدمة رؤية حاسوبية متقدمة باستخدام معمارية YOLO المحسنة للتطبيقات
  الزراعية. توفر الكشف والتصنيف الفوري للآفات والأمراض والأعشاب
  ومؤشرات صحة المحاصيل.

dependencies:
  - torch>=2.2.0
  - ultralytics>=8.1.0
  - opencv-python>=4.9.0
  - onnxruntime-gpu>=1.17.0
  - albumentations>=1.3.0

hardware_requirements:
  gpu: "NVIDIA T4/A10G (16GB VRAM minimum)"
  cpu: "8 cores"
  memory: "32GB RAM"
  storage: "100GB SSD (model weights + cache)"
```

#### Detection Capabilities | قدرات الكشف

##### Pest Detection | كشف الآفات (20+ Species)

| Category | Species | Arabic | Accuracy |
|----------|---------|--------|----------|
| **Locusts** | Desert Locust | الجراد الصحراوي | 96.2% |
| | Migratory Locust | الجراد المهاجر | 94.8% |
| **Borers** | Date Palm Borer | حفار النخيل | 93.5% |
| | Stem Borer | حفار الساق | 92.1% |
| **Weevils** | Red Palm Weevil | سوسة النخيل الحمراء | 97.3% |
| | Grain Weevil | سوسة الحبوب | 91.4% |
| **Aphids** | Wheat Aphid | من القمح | 89.7% |
| | Cotton Aphid | من القطن | 88.9% |
| **Mites** | Spider Mite | العنكبوت الأحمر | 87.3% |
| **Whiteflies** | Bemisia tabaci | الذبابة البيضاء | 90.2% |
| **Moths** | Tuta absoluta | توتا أبسولوتا | 91.8% |
| | Fall Armyworm | دودة الحشد الخريفية | 93.4% |
| **Thrips** | Onion Thrips | تربس البصل | 86.5% |
| **Beetles** | Flour Beetle | خنفساء الدقيق | 88.1% |
| **Flies** | Fruit Fly | ذبابة الفاكهة | 92.6% |
| | Olive Fly | ذبابة الزيتون | 90.8% |
| **Caterpillars** | Cotton Bollworm | دودة اللوز | 94.1% |
| | Tomato Leafminer | نافقة أوراق الطماطم | 89.3% |
| **Scale Insects** | Date Scale | حشرة التمر القشرية | 85.7% |
| **Nematodes** | Root-knot Nematode | نيماتودا تعقد الجذور | 82.4%* |

*Requires soil sample imaging

##### Disease Detection | كشف الأمراض (30+ Diseases)

| Crop | Disease | Arabic | Accuracy |
|------|---------|--------|----------|
| **Wheat** | Stem Rust | صدأ الساق | 95.7% |
| | Leaf Rust | صدأ الأوراق | 94.2% |
| | Stripe Rust | الصدأ المخطط | 93.8% |
| | Powdery Mildew | البياض الدقيقي | 92.4% |
| | Septoria | سبتوريا | 89.6% |
| | Fusarium Head Blight | لفحة السنابل | 88.3% |
| **Date Palm** | Bayoud Disease | مرض البيوض | 91.2% |
| | Black Scorch | اللفحة السوداء | 90.7% |
| | Leaf Spot | تبقع الأوراق | 87.9% |
| **Tomato** | Early Blight | اللفحة المبكرة | 94.5% |
| | Late Blight | اللفحة المتأخرة | 95.1% |
| | Bacterial Wilt | الذبول البكتيري | 88.6% |
| | Mosaic Virus | فيروس الموزاييك | 86.2% |
| | Leaf Curl Virus | فيروس تجعد الأوراق | 85.8% |
| **Potato** | Late Blight | اللفحة المتأخرة | 94.9% |
| | Common Scab | الجرب العادي | 83.7% |
| **Citrus** | Citrus Greening (HLB) | الاخضرار | 89.4% |
| | Canker | تقرح الموالح | 91.3% |
| | Melanose | الميلانوز | 85.2% |
| **Olive** | Verticillium Wilt | الذبول الفرتسيلي | 87.8% |
| | Peacock Spot | عين الطاووس | 90.1% |
| **Rice** | Blast | لفحة الأرز | 93.6% |
| | Brown Spot | التبقع البني | 88.4% |
| | Sheath Blight | لفحة الغمد | 86.9% |
| **Cotton** | Bacterial Blight | اللفحة البكتيرية | 89.7% |
| | Verticillium Wilt | الذبول | 88.2% |
| **Grape** | Downy Mildew | البياض الزغبي | 92.8% |
| | Powdery Mildew | البياض الدقيقي | 93.4% |
| | Gray Mold (Botrytis) | العفن الرمادي | 87.5% |
| **Cucumber** | Downy Mildew | البياض الزغبي | 91.6% |
| | Anthracnose | أنثراكنوز | 84.3% |

##### Additional Capabilities | قدرات إضافية

```yaml
weed_detection:
  species_count: 15
  accuracy: 88-94%
  weeds:
    - Bermuda grass | النجيل
    - Cyperus rotundus | السعد
    - Amaranthus | القطيفة
    - Portulaca | الرجلة
    - Convolvulus | العليق
    - Wild Oat | الشوفان البري
    - Rumex | الحميض
    - Chenopodium | رجل الأوزة

plant_counting:
  crops: [wheat, rice, corn, cotton, tomato, potato]
  accuracy: 95-98%
  max_density: 500 plants/m²
  use_cases:
    - Germination rate calculation
    - Stand count assessment
    - Yield estimation

fruit_ripeness:
  crops: [tomato, date, grape, citrus, olive]
  stages: [immature, mature, ripe, overripe]
  accuracy: 91-96%
  use_cases:
    - Harvest timing optimization
    - Quality grading
    - Post-harvest sorting

leaf_segmentation:
  capabilities:
    - Individual leaf isolation
    - Leaf area calculation
    - Damage percentage estimation
    - Chlorosis mapping
  accuracy: 93.2%
```

#### API Endpoints | نقاط الوصول

```yaml
endpoints:
  # Health & Status
  - path: /healthz
    method: GET
    description: Liveness probe

  - path: /readyz
    method: GET
    description: Readiness probe with model status

  - path: /metrics
    method: GET
    description: Prometheus metrics

  # Detection Endpoints
  - path: /api/v1/detect/pest
    method: POST
    description: Detect pests in image
    request:
      content_type: multipart/form-data
      fields:
        - name: image
          type: file
          required: true
        - name: field_id
          type: string
          required: false
        - name: confidence_threshold
          type: float
          default: 0.5
    response:
      detections:
        - class: "red_palm_weevil"
          class_ar: "سوسة النخيل الحمراء"
          confidence: 0.97
          bbox: [x1, y1, x2, y2]
          severity: "high"
          action_required: true

  - path: /api/v1/detect/disease
    method: POST
    description: Detect diseases in plant image

  - path: /api/v1/detect/weed
    method: POST
    description: Detect weeds in field image

  - path: /api/v1/count/plants
    method: POST
    description: Count plants in image

  - path: /api/v1/classify/ripeness
    method: POST
    description: Classify fruit ripeness stage

  - path: /api/v1/segment/leaf
    method: POST
    description: Segment and analyze leaves

  # Batch Processing
  - path: /api/v1/batch/analyze
    method: POST
    description: Batch process multiple images
    max_images: 100
    async: true

  # Model Management
  - path: /api/v1/models
    method: GET
    description: List available models

  - path: /api/v1/models/{model_id}/info
    method: GET
    description: Get model metadata and performance stats
```

---

### 2. Terrain Core Service (Port 8160)

#### خدمة تحليل التضاريس الأساسية

```yaml
service_name: terrain-core-service
name_ar: خدمة التضاريس الأساسية
port: 8160
type: python
framework: FastAPI
layer: intelligence
category: analytics

description: |
  Processes Digital Elevation Models (DEM) from multiple sources to
  calculate terrain indicators essential for irrigation planning,
  drainage design, and land management decisions.

description_ar: |
  معالجة نماذج الارتفاعات الرقمية من مصادر متعددة لحساب مؤشرات
  التضاريس الأساسية لتخطيط الري وتصميم الصرف وقرارات إدارة الأراضي.

dependencies:
  - rasterio>=1.3.9
  - pysheds>=0.3.5
  - richdem>=0.3.4
  - whitebox>=2.3.1
  - xarray>=2024.1.0
  - geopandas>=0.14.0
```

#### DEM Data Sources | مصادر بيانات الارتفاعات (4 Sources)

| Source | Resolution | Coverage | Update Freq | Cost |
|--------|------------|----------|-------------|------|
| **SRTM** | 30m | Global | Static | Free |
| **ALOS PALSAR** | 12.5m | Global | Static | Free |
| **Copernicus DEM** | 30m/90m | Global | Annual | Free |
| **Drone Survey** | 5-10cm | On-demand | Per survey | Variable |

```yaml
dem_sources:
  srtm:
    name: "Shuttle Radar Topography Mission"
    name_ar: "مهمة مكوك الرادار الطوبوغرافية"
    resolution: 30m
    vertical_accuracy: 16m
    coverage: "60°N to 56°S"
    api: "https://earthexplorer.usgs.gov/api"

  alos_palsar:
    name: "ALOS PALSAR DEM"
    name_ar: "نموذج ارتفاعات ALOS"
    resolution: 12.5m
    vertical_accuracy: 5m
    coverage: "Global"
    api: "https://www.eorc.jaxa.jp/ALOS/en/dataset/aw3d_e.htm"

  copernicus:
    name: "Copernicus DEM"
    name_ar: "نموذج كوبرنيكوس"
    resolution: "30m (GLO-30) / 90m (GLO-90)"
    vertical_accuracy: 4m
    coverage: "Global"
    api: "https://dataspace.copernicus.eu/"

  drone_rtk:
    name: "Drone RTK Survey"
    name_ar: "مسح الطائرات بدون طيار RTK"
    resolution: "5-10cm"
    vertical_accuracy: "2-5cm"
    coverage: "Field-level"
    processing: "Pix4D / OpenDroneMap"
```

#### Terrain Indicators | مؤشرات التضاريس (7 Indicators)

| # | Indicator | Arabic | Unit | Use Case |
|---|-----------|--------|------|----------|
| 1 | **Slope** | الانحدار | % or ° | Erosion risk, machinery access |
| 2 | **Aspect** | الاتجاه | ° (0-360) | Solar exposure, crop selection |
| 3 | **Curvature** | التقعر/التحدب | 1/m | Water accumulation patterns |
| 4 | **TWI** | مؤشر الرطوبة الطوبوغرافي | - | Soil moisture prediction |
| 5 | **Flow Accumulation** | تراكم التدفق | cells | Drainage network delineation |
| 6 | **Flow Direction** | اتجاه التدفق | D8/D-Inf | Water routing |
| 7 | **TPI** | مؤشر الموضع الطوبوغرافي | m | Landform classification |

```yaml
indicators:
  slope:
    name: "Slope"
    name_ar: "الانحدار"
    algorithm: "Horn (1981)"
    output_units: ["percent", "degrees"]
    classifications:
      flat: "0-2%"
      gentle: "2-5%"
      moderate: "5-10%"
      steep: "10-15%"
      very_steep: ">15%"
    agricultural_thresholds:
      gravity_irrigation: "<2%"
      sprinkler_irrigation: "<15%"
      center_pivot: "<5%"
      machinery_safe: "<10%"

  aspect:
    name: "Aspect (Slope Direction)"
    name_ar: "اتجاه الانحدار"
    output_units: "degrees"
    classifications:
      north: "337.5-22.5°"
      northeast: "22.5-67.5°"
      east: "67.5-112.5°"
      southeast: "112.5-157.5°"
      south: "157.5-202.5°"
      southwest: "202.5-247.5°"
      west: "247.5-292.5°"
      northwest: "292.5-337.5°"

  curvature:
    name: "Curvature"
    name_ar: "الانحناء"
    types:
      plan_curvature: "Convergence/divergence of flow"
      profile_curvature: "Acceleration/deceleration of flow"
      total_curvature: "Combined surface shape"
    interpretation:
      negative: "Concave (water accumulates)"
      zero: "Flat/linear"
      positive: "Convex (water disperses)"

  twi:
    name: "Topographic Wetness Index"
    name_ar: "مؤشر الرطوبة الطوبوغرافي"
    formula: "ln(a / tan(β))"
    description: "Predicts soil moisture distribution"
    classifications:
      dry: "<6"
      moderate: "6-9"
      wet: "9-12"
      saturated: ">12"

  flow_accumulation:
    name: "Flow Accumulation"
    name_ar: "تراكم التدفق"
    algorithms: ["D8", "D-Infinity", "Multiple Flow Direction"]
    uses:
      - "Stream network delineation"
      - "Watershed boundary definition"
      - "Drainage density calculation"

  flow_direction:
    name: "Flow Direction"
    name_ar: "اتجاه التدفق"
    algorithms:
      D8: "Single flow to steepest neighbor"
      D_Inf: "Proportional flow to multiple neighbors"
    output: "Raster with direction codes"

  tpi:
    name: "Topographic Position Index"
    name_ar: "مؤشر الموضع الطوبوغرافي"
    formula: "elevation - mean(neighborhood elevation)"
    scale_dependent: true
    classifications:
      valley: "TPI < -1 SD"
      lower_slope: "-1 SD < TPI < -0.5 SD"
      flat: "-0.5 SD < TPI < 0.5 SD"
      upper_slope: "0.5 SD < TPI < 1 SD"
      ridge: "TPI > 1 SD"
```

#### API Endpoints | نقاط الوصول

```yaml
endpoints:
  - path: /api/v1/dem/upload
    method: POST
    description: Upload DEM file for processing

  - path: /api/v1/dem/fetch
    method: POST
    description: Fetch DEM from external source
    body:
      source: "srtm|alos|copernicus"
      bbox: [west, south, east, north]

  - path: /api/v1/indicators/slope
    method: POST
    description: Calculate slope from DEM

  - path: /api/v1/indicators/aspect
    method: POST
    description: Calculate aspect from DEM

  - path: /api/v1/indicators/twi
    method: POST
    description: Calculate Topographic Wetness Index

  - path: /api/v1/indicators/all
    method: POST
    description: Calculate all 7 indicators

  - path: /api/v1/terrain/report
    method: POST
    description: Generate comprehensive terrain report
    response:
      field_id: string
      dem_source: string
      resolution: float
      indicators:
        slope_mean: float
        slope_max: float
        dominant_aspect: string
        twi_mean: float
        drainage_density: float
      recommendations:
        - "Suitable for drip irrigation"
        - "مناسب للري بالتنقيط"
```

---

### 3. Hydrology Service (Port 8165)

#### خدمة الهيدرولوجيا

```yaml
service_name: hydrology-service
name_ar: خدمة الهيدرولوجيا
port: 8165
type: python
framework: FastAPI
layer: intelligence
category: analytics

description: |
  Analyzes surface water flow patterns, delineates drainage networks,
  and predicts waterlogging risk areas using terrain data and
  meteorological inputs.

description_ar: |
  تحليل أنماط تدفق المياه السطحية، وتحديد شبكات الصرف، والتنبؤ
  بمناطق التشبع المائي باستخدام بيانات التضاريس والمدخلات الجوية.

dependencies:
  - pysheds>=0.3.5
  - whitebox>=2.3.1
  - hydromt>=0.9.0
  - wflow>=2024.1
```

#### Capabilities | القدرات

##### Drainage Network Analysis | تحليل شبكة الصرف

```yaml
drainage_analysis:
  stream_network:
    description: "Delineate stream/drainage channels"
    methods:
      - D8 flow routing
      - Channel head detection
      - Strahler stream ordering
    outputs:
      - Stream network vector
      - Stream order classification
      - Drainage density (km/km²)

  watershed_delineation:
    description: "Define catchment boundaries"
    methods:
      - Pour point identification
      - Upstream area calculation
      - Sub-basin division
    outputs:
      - Watershed polygons
      - Drainage area (ha)
      - Time of concentration

  channel_morphology:
    description: "Analyze channel characteristics"
    parameters:
      - Channel slope
      - Sinuosity index
      - Valley width
    outputs:
      - Longitudinal profile
      - Cross-section estimates
```

##### Waterlogging Prediction | التنبؤ بالتشبع المائي

```yaml
waterlogging_prediction:
  risk_factors:
    topographic:
      - TWI (Topographic Wetness Index)
      - Depression areas (sinks)
      - Flow convergence zones
      - Distance to drainage

    soil:
      - Infiltration rate (Ksat)
      - Clay content
      - Soil depth
      - Water table depth

    climatic:
      - Rainfall intensity
      - Antecedent moisture
      - Evapotranspiration

  risk_levels:
    very_high: "TWI > 12, clay > 40%, Ksat < 0.1 cm/hr"
    high: "TWI 10-12, clay 30-40%"
    moderate: "TWI 8-10, clay 20-30%"
    low: "TWI 6-8, clay < 20%"
    very_low: "TWI < 6, well-drained"

  outputs:
    - Risk map (raster)
    - Affected area statistics
    - Drainage recommendations
    - Alert thresholds
```

##### Runoff Estimation | تقدير الجريان السطحي

```yaml
runoff_estimation:
  methods:
    rational_method:
      formula: "Q = C × I × A"
      use_case: "Small watersheds < 80 ha"
      inputs:
        - Runoff coefficient (C)
        - Rainfall intensity (I)
        - Drainage area (A)

    scs_cn_method:
      formula: "Q = (P - Ia)² / (P - Ia + S)"
      use_case: "Agricultural watersheds"
      inputs:
        - Precipitation (P)
        - Initial abstraction (Ia)
        - Potential retention (S)
        - Curve Number (CN)

    unit_hydrograph:
      description: "Event-based runoff routing"
      types:
        - SCS dimensionless
        - Clark
        - Snyder
```

#### API Endpoints | نقاط الوصول

```yaml
endpoints:
  - path: /api/v1/drainage/network
    method: POST
    description: Extract drainage network from DEM

  - path: /api/v1/drainage/watershed
    method: POST
    description: Delineate watershed boundaries

  - path: /api/v1/waterlogging/risk
    method: POST
    description: Calculate waterlogging risk map
    body:
      field_id: string
      soil_data: object
      weather_forecast: object

  - path: /api/v1/runoff/estimate
    method: POST
    description: Estimate runoff for design storm

  - path: /api/v1/hydrology/report
    method: POST
    description: Comprehensive hydrology report
```

---

### 4. Leveling Optimizer Service (Port 8170)

#### خدمة تحسين التسوية

```yaml
service_name: leveling-optimizer-service
name_ar: خدمة تحسين التسوية
port: 8170
type: python
framework: FastAPI
layer: decision
category: analytics

description: |
  Calculates optimal land leveling design, cut/fill volumes, and
  cost estimates for field preparation. Supports multiple design
  objectives including minimum earthwork, target slope, and
  irrigation efficiency.

description_ar: |
  حساب التصميم الأمثل لتسوية الأراضي وأحجام الحفر والردم وتقديرات
  التكلفة لإعداد الحقول. يدعم أهداف تصميم متعددة بما في ذلك الحد
  الأدنى من أعمال الحفر والانحدار المستهدف وكفاءة الري.

dependencies:
  - numpy>=1.26.0
  - scipy>=1.12.0
  - cvxpy>=1.4.0
  - rasterio>=1.3.9
```

#### Capabilities | القدرات

##### Cut/Fill Volume Calculation | حساب أحجام الحفر والردم

```yaml
volume_calculation:
  methods:
    grid_method:
      description: "Prism-based volume calculation"
      accuracy: "High for regular terrain"
      cell_sizes: [1m, 5m, 10m]

    cross_section:
      description: "Section-based volume"
      accuracy: "Very high"
      spacing: [10m, 20m, 50m]

    tin_method:
      description: "Triangulated Irregular Network"
      accuracy: "Highest for complex terrain"

  outputs:
    cut_volume_m3: "Total excavation volume"
    fill_volume_m3: "Total fill volume"
    balance: "Cut - Fill (haul requirement)"
    shrinkage_factor: 1.15  # Typical 15% compaction

  visualization:
    - Cut/fill depth map
    - Isopach contours
    - Volume distribution chart
```

##### Cost Estimation | تقدير التكلفة

```yaml
cost_estimation:
  unit_costs_sar:
    excavation:
      soft_soil: 8.50  # SAR/m³
      medium_soil: 12.00
      hard_soil: 18.00
      rock: 45.00

    fill_placement:
      loose: 6.00
      compacted: 9.50

    haul_distance:
      per_100m: 1.50  # SAR/m³ per 100m

    equipment:
      dozer_d6: 350  # SAR/hour
      dozer_d8: 480
      grader: 280
      scraper: 420
      laser_system: 150  # per day rental

    survey:
      rtk_survey: 500  # SAR/ha
      control_points: 200  # per point

  cost_components:
    - Excavation cost
    - Fill placement cost
    - Haul cost
    - Equipment mobilization
    - Survey and staking
    - Quality control
    - Contingency (10%)
```

##### Optimization Algorithms | خوارزميات التحسين

```yaml
optimization:
  objectives:
    minimum_earthwork:
      description: "Minimize total cut + fill volume"
      constraint: "Balance cut = fill"
      algorithm: "Linear programming"

    target_slope:
      description: "Achieve specified design slope"
      parameters:
        - Design slope (%)
        - Slope direction (°)
      uses: "Gravity irrigation systems"

    minimum_cost:
      description: "Minimize total leveling cost"
      considers:
        - Haul distances
        - Soil types
        - Equipment constraints

    maximum_efficiency:
      description: "Optimize for irrigation efficiency"
      factors:
        - Water distribution uniformity
        - Application efficiency
        - Runoff minimization

  constraints:
    - Maximum cut depth
    - Maximum fill depth
    - Haul distance limits
    - Equipment capacity
    - Project timeline
```

#### API Endpoints | نقاط الوصول

```yaml
endpoints:
  - path: /api/v1/leveling/design
    method: POST
    description: Generate optimal leveling design
    body:
      field_id: string
      dem_data: binary
      objective: "minimum_earthwork|target_slope|minimum_cost"
      target_slope: float  # optional
      constraints: object

  - path: /api/v1/leveling/volumes
    method: POST
    description: Calculate cut/fill volumes

  - path: /api/v1/leveling/cost
    method: POST
    description: Generate cost estimate
    body:
      volumes: object
      soil_type: string
      haul_distance: float

  - path: /api/v1/leveling/optimize
    method: POST
    description: Run optimization algorithm

  - path: /api/v1/leveling/report
    method: POST
    description: Generate comprehensive leveling report
    response:
      design_summary:
        total_area_ha: float
        design_slope: float
        slope_direction: string
      volumes:
        cut_m3: float
        fill_m3: float
        balance_m3: float
      costs:
        total_sar: float
        per_ha_sar: float
        breakdown: object
      schedule:
        estimated_days: int
        equipment_hours: object
      maps:
        design_surface: url
        cut_fill_depth: url
        haul_routes: url
```

---

### 5. Edge Orchestrator Service (Port 8180)

#### خدمة إدارة الحوسبة الطرفية

```yaml
service_name: edge-orchestrator-service
name_ar: خدمة إدارة الحافة
port: 8180
type: python
framework: FastAPI
layer: acquisition
category: integration

description: |
  Manages fleet of NVIDIA Jetson Orin edge devices deployed in fields.
  Handles model deployment, device monitoring, OTA updates, and
  inference result aggregation. Enables real-time field processing
  without cloud dependency.

description_ar: |
  إدارة أسطول أجهزة NVIDIA Jetson Orin المنشورة في الحقول. تتولى
  نشر النماذج ومراقبة الأجهزة والتحديثات عن بُعد وتجميع نتائج
  الاستدلال. تمكّن المعالجة الميدانية الفورية دون الاعتماد على السحابة.

dependencies:
  - jetson-inference>=1.0.0
  - onnxruntime>=1.17.0
  - paho-mqtt>=2.0.0
  - prometheus-client>=0.19.0
```

#### Jetson Orin Device Specifications | مواصفات جهاز Jetson Orin

```yaml
device_profiles:
  jetson_orin_nano:
    name: "NVIDIA Jetson Orin Nano"
    name_ar: "جيتسون أورين نانو"
    compute:
      gpu: "1024 CUDA cores, 32 Tensor cores"
      cpu: "6-core Arm Cortex-A78AE"
      memory: "8GB LPDDR5"
      storage: "128GB NVMe SSD (recommended)"
    performance:
      ai_tops: 40
      power_modes: [7W, 15W]
      yolo_fps: "30-45 FPS @ 640px"
    connectivity:
      ethernet: "Gigabit"
      wifi: "802.11ax (optional)"
      cellular: "4G LTE (optional module)"
    environment:
      temperature: "-25°C to 50°C"
      humidity: "85% RH (non-condensing)"
      ip_rating: "IP65 enclosure"
    price_usd: 499

  jetson_orin_nx:
    name: "NVIDIA Jetson Orin NX"
    name_ar: "جيتسون أورين NX"
    compute:
      gpu: "1024 CUDA cores, 32 Tensor cores"
      cpu: "8-core Arm Cortex-A78AE"
      memory: "16GB LPDDR5"
    performance:
      ai_tops: 100
      yolo_fps: "60-90 FPS @ 640px"
    price_usd: 899

fleet_deployment:
  initial_units: 50
  coverage: "1 device per 50-100 ha"
  deployment_zones:
    - Central Saudi Arabia
    - Al-Qassim Region
    - Eastern Province
```

#### Device Management Capabilities | قدرات إدارة الأجهزة

```yaml
device_management:
  registration:
    - Automatic device discovery
    - Secure enrollment (mTLS)
    - Farm/field assignment
    - Configuration provisioning

  monitoring:
    metrics:
      - CPU/GPU utilization
      - Memory usage
      - Temperature
      - Storage capacity
      - Network connectivity
      - Inference latency
      - Power consumption
    alerting:
      - Device offline > 5 minutes
      - Temperature > 70°C
      - Storage > 90%
      - Inference errors > threshold

  ota_updates:
    capabilities:
      - Model weight updates
      - Firmware updates
      - Configuration changes
      - Security patches
    features:
      - Delta updates (bandwidth efficient)
      - Rollback support
      - Staged rollout (canary)
      - Offline queue

  model_deployment:
    formats:
      - ONNX (optimized)
      - TensorRT (maximum performance)
    optimization:
      - INT8 quantization
      - Layer fusion
      - Memory optimization
    deployment_methods:
      - Push (cloud-initiated)
      - Pull (device-initiated)
      - Peer-to-peer (mesh network)
```

#### Real-time Processing Pipeline | خط المعالجة الفوري

```yaml
processing_pipeline:
  input_sources:
    - USB cameras (4K @ 30fps)
    - IP cameras (RTSP)
    - Drone feeds (RTMP)
    - Image uploads

  inference_modes:
    continuous:
      description: "Always-on monitoring"
      use_case: "Pest traps, greenhouse"
      fps: 15-30

    triggered:
      description: "Event-based inference"
      triggers:
        - Motion detection
        - Schedule (hourly)
        - Manual request

    batch:
      description: "Offline image processing"
      use_case: "Drone survey images"

  result_handling:
    local_storage:
      format: "SQLite + images"
      retention: "7 days"

    cloud_sync:
      protocol: "MQTT over TLS"
      topics:
        - sahool/edge/{device_id}/detections
        - sahool/edge/{device_id}/status
        - sahool/edge/{device_id}/alerts
      priority_queue:
        - Alerts (immediate)
        - Detections (batch 5min)
        - Status (periodic 15min)

    offline_mode:
      buffer: "Local queue up to 10,000 events"
      sync_on_reconnect: true
```

#### API Endpoints | نقاط الوصول

```yaml
endpoints:
  # Device Management
  - path: /api/v1/devices
    method: GET
    description: List all registered devices

  - path: /api/v1/devices/{device_id}
    method: GET
    description: Get device details and status

  - path: /api/v1/devices/{device_id}/configure
    method: POST
    description: Update device configuration

  - path: /api/v1/devices/{device_id}/restart
    method: POST
    description: Restart device remotely

  # Model Deployment
  - path: /api/v1/models/deploy
    method: POST
    description: Deploy model to device(s)
    body:
      model_id: string
      device_ids: array
      strategy: "immediate|scheduled|canary"

  - path: /api/v1/models/rollback
    method: POST
    description: Rollback to previous model version

  # OTA Updates
  - path: /api/v1/ota/firmware
    method: POST
    description: Schedule firmware update

  - path: /api/v1/ota/status
    method: GET
    description: Get OTA update status

  # Inference Results
  - path: /api/v1/results/stream
    method: WebSocket
    description: Real-time inference results stream

  - path: /api/v1/results/history
    method: GET
    description: Query historical inference results

  # Fleet Analytics
  - path: /api/v1/fleet/dashboard
    method: GET
    description: Fleet-wide metrics and status

  - path: /api/v1/fleet/coverage
    method: GET
    description: Geographic coverage analysis
```

---

## مخطط البنية التقنية | Architecture Diagram

### System Architecture | بنية النظام

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    SAHOOL Platform                                   │
│                                   منصة سهول الزراعية                                │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                           │
        ┌──────────────────────────────────┼──────────────────────────────────┐
        │                                  │                                  │
        ▼                                  ▼                                  ▼
┌───────────────────┐            ┌───────────────────┐            ┌───────────────────┐
│   Mobile App      │            │   Web Dashboard   │            │   Admin Portal    │
│ تطبيق الجوال     │            │  لوحة المعلومات   │            │  بوابة الإدارة    │
│   (Flutter)       │            │   (Next.js)       │            │    (React)        │
└─────────┬─────────┘            └─────────┬─────────┘            └─────────┬─────────┘
          │                                │                                │
          └────────────────────────────────┼────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                               Kong API Gateway                                       │
│                               بوابة الـ API                                         │
│                          (Authentication, Rate Limiting)                             │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                           │
          ┌────────────────────────────────┼────────────────────────────────┐
          │                                │                                │
          ▼                                ▼                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              NATS JetStream Message Bus                              │
│                              ناقل الرسائل (NATS)                                    │
│                     Subject: sahool.{tenant_id}.{event_type}                        │
└─────────────────────────────────────────────────────────────────────────────────────┘
          │                    │                    │                    │
          ▼                    ▼                    ▼                    ▼

═══════════════════════════════════════════════════════════════════════════════════════
                    ACQUISITION LAYER | طبقة جمع البيانات
═══════════════════════════════════════════════════════════════════════════════════════

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Edge Orchestrator│  │  IoT Service    │  │ Weather Service │  │ Ground Vision   │
│    :8180        │  │    :8117        │  │    :8092        │  │    :8155        │
│ إدارة الحافة    │  │ خدمة IoT       │  │ خدمة الطقس     │  │ الرؤية الأرضية │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │                    │
    ┌────┴────┐               │                    │                    │
    ▼         ▼               │                    │                    │
┌───────┐ ┌───────┐           │                    │                    │
│Jetson │ │Jetson │           │                    │                    │
│ Orin  │ │ Orin  │           │                    │                    │
│(Field)│ │(Field)│           │                    │                    │
└───────┘ └───────┘           │                    │                    │
                              │                    │                    │
═══════════════════════════════════════════════════════════════════════════════════════
                    INTELLIGENCE LAYER | طبقة الذكاء
═══════════════════════════════════════════════════════════════════════════════════════

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ YOLO26 Vision   │  │  Terrain Core   │  │   Hydrology     │  │ Crop Intel.     │
│    :8150        │  │    :8160        │  │    :8165        │  │    :8095        │
│ الرؤية YOLO26  │  │  التضاريس      │  │ الهيدرولوجيا   │  │ ذكاء المحاصيل │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ • Pest (20+)    │  │ • DEM Processing│  │ • Drainage      │  │ • Disease AI    │
│ • Disease (30+) │  │ • 7 Indicators  │  │ • Waterlogging  │  │ • Growth Stage  │
│ • Weed          │  │ • Slope/Aspect  │  │ • Runoff        │  │ • Stress        │
│ • Plant Count   │  │ • TWI/TPI       │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  NDVI Processor │  │ Field Intel.    │  │ Indicators      │
│    :8118        │  │    :8120        │  │    :8091        │
│ معالج NDVI     │  │ ذكاء الحقل     │  │  المؤشرات      │
└─────────────────┘  └─────────────────┘  └─────────────────┘

═══════════════════════════════════════════════════════════════════════════════════════
                    DECISION LAYER | طبقة القرار
═══════════════════════════════════════════════════════════════════════════════════════

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│Leveling Optimizer│  │ Advisory Service│  │ Irrigation Smart│  │ Yield Engine    │
│    :8170        │  │    :8093        │  │    :8094        │  │    :8098        │
│ تحسين التسوية  │  │ خدمة التوصيات  │  │   الري الذكي   │  │ محرك الإنتاج  │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ • Cut/Fill Vol  │  │ • Crop Advisory │  │ • ETc Calc      │  │ • Yield Predict │
│ • Cost Estimate │  │ • Pest Control  │  │ • Scheduling    │  │ • Harvest Time  │
│ • Optimization  │  │ • Fertilizer    │  │ • Water Balance │  │ • Quality Est.  │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘

═══════════════════════════════════════════════════════════════════════════════════════
                    BUSINESS LAYER | طبقة الأعمال
═══════════════════════════════════════════════════════════════════════════════════════

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Notification    │  │ Field Mgmt      │  │ Task Service    │  │ Alert Service   │
│    :8110        │  │    :3000        │  │    :8103        │  │    :8113        │
│  الإشعارات     │  │ إدارة الحقول  │  │  المهام        │  │  التنبيهات     │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘

═══════════════════════════════════════════════════════════════════════════════════════
                    DATA LAYER | طبقة البيانات
═══════════════════════════════════════════════════════════════════════════════════════

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   PostgreSQL    │  │     Redis       │  │   MinIO/S3      │  │  Qdrant Vector  │
│   + PostGIS     │  │    (Cache)      │  │ (Object Storage)│  │    (RAG)        │
│   :5432         │  │    :6379        │  │    :9000        │  │    :6333        │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Data Flow Diagram | مخطط تدفق البيانات

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           IMAGE PROCESSING PIPELINE                                  │
│                           خط معالجة الصور                                           │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌──────────┐    ┌──────────┐    ┌──────────────┐    ┌────────────┐    ┌────────────┐
│  Camera  │───▶│  Jetson  │───▶│ Edge Process │───▶│   NATS     │───▶│  YOLO26    │
│  Drone   │    │   Orin   │    │  (< 100ms)   │    │  (Async)   │    │  (Cloud)   │
│  Upload  │    │          │    │              │    │            │    │            │
└──────────┘    └──────────┘    └──────────────┘    └────────────┘    └────────────┘
                     │                                                      │
                     │ Local Detection                                      │ Full Analysis
                     ▼                                                      ▼
              ┌─────────────┐                                        ┌─────────────┐
              │ Alert (MQTT)│                                        │  PostgreSQL │
              │ if Critical │                                        │  + PostGIS  │
              └─────────────┘                                        └─────────────┘
                     │                                                      │
                     ▼                                                      ▼
              ┌─────────────┐                                        ┌─────────────┐
              │ Mobile Push │                                        │  Advisory   │
              │ Notification│                                        │  Service    │
              └─────────────┘                                        └─────────────┘


┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           TERRAIN ANALYSIS PIPELINE                                  │
│                           خط تحليل التضاريس                                         │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────────┐
│  DEM     │───▶│ Terrain Core │───▶│  Hydrology   │───▶│    Leveling    │
│  Source  │    │   Service    │    │   Service    │    │   Optimizer    │
│ (4 types)│    │   :8160      │    │   :8165      │    │     :8170      │
└──────────┘    └──────────────┘    └──────────────┘    └────────────────┘
     │               │                    │                     │
     │               ▼                    ▼                     ▼
     │         ┌──────────┐         ┌──────────┐         ┌──────────┐
     │         │ 7 Terrain│         │ Drainage │         │ Cut/Fill │
     │         │Indicators│         │ Network  │         │ Volumes  │
     │         └──────────┘         └──────────┘         └──────────┘
     │               │                    │                     │
     │               └────────────────────┼─────────────────────┘
     │                                    ▼
     │                           ┌─────────────────┐
     │                           │ Integrated      │
     │                           │ Terrain Report  │
     │                           │ + Cost Estimate │
     │                           └─────────────────┘
     │                                    │
     ▼                                    ▼
┌──────────┐                     ┌─────────────────┐
│ MinIO S3 │◀────────────────────│ Field Mgmt      │
│ (Rasters)│                     │ Service         │
└──────────┘                     └─────────────────┘
```

---

## تغييرات مخطط قاعدة البيانات | Database Schema Changes

### New Tables | الجداول الجديدة

```sql
-- ═══════════════════════════════════════════════════════════════════════════
-- YOLO26 Vision Service Tables
-- جداول خدمة الرؤية YOLO26
-- ═══════════════════════════════════════════════════════════════════════════

-- Detection results storage
CREATE TABLE vision_detections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    field_id UUID REFERENCES fields(id),
    device_id UUID REFERENCES edge_devices(id),

    -- Detection metadata
    detection_type VARCHAR(50) NOT NULL,  -- pest, disease, weed, plant_count, ripeness
    detection_class VARCHAR(100) NOT NULL, -- e.g., 'red_palm_weevil'
    detection_class_ar VARCHAR(100),       -- e.g., 'سوسة النخيل الحمراء'
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    severity VARCHAR(20),                  -- low, medium, high, critical

    -- Spatial data
    location GEOMETRY(Point, 4326),
    bbox_json JSONB,                       -- Bounding box coordinates

    -- Image reference
    image_url TEXT NOT NULL,
    thumbnail_url TEXT,

    -- Processing info
    model_version VARCHAR(50) NOT NULL,
    inference_time_ms INTEGER,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Indexes
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_vision_detections_tenant ON vision_detections(tenant_id);
CREATE INDEX idx_vision_detections_field ON vision_detections(field_id);
CREATE INDEX idx_vision_detections_type ON vision_detections(detection_type);
CREATE INDEX idx_vision_detections_class ON vision_detections(detection_class);
CREATE INDEX idx_vision_detections_created ON vision_detections(created_at);
CREATE INDEX idx_vision_detections_location ON vision_detections USING GIST(location);

-- Model registry for vision models
CREATE TABLE vision_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    version VARCHAR(50) NOT NULL,
    model_type VARCHAR(50) NOT NULL,       -- pest, disease, weed, etc.

    -- Model artifacts
    weights_url TEXT NOT NULL,
    config_json JSONB,

    -- Performance metrics
    accuracy FLOAT,
    precision_score FLOAT,
    recall_score FLOAT,
    f1_score FLOAT,
    inference_fps FLOAT,

    -- Metadata
    supported_classes TEXT[],
    input_size INTEGER NOT NULL,           -- e.g., 640
    quantization VARCHAR(20),              -- fp32, fp16, int8

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════════════
-- Terrain Core Service Tables
-- جداول خدمة التضاريس
-- ═══════════════════════════════════════════════════════════════════════════

-- DEM data storage
CREATE TABLE terrain_dem (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    field_id UUID REFERENCES fields(id),

    -- DEM metadata
    source VARCHAR(50) NOT NULL,           -- srtm, alos, copernicus, drone
    resolution_m FLOAT NOT NULL,
    vertical_accuracy_m FLOAT,
    acquisition_date DATE,

    -- Spatial extent
    bbox GEOMETRY(Polygon, 4326) NOT NULL,
    raster_url TEXT NOT NULL,              -- MinIO/S3 path

    -- Processing status
    processed BOOLEAN DEFAULT false,
    processed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_terrain_dem_field ON terrain_dem(field_id);
CREATE INDEX idx_terrain_dem_bbox ON terrain_dem USING GIST(bbox);

-- Terrain indicators per field
CREATE TABLE terrain_indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dem_id UUID NOT NULL REFERENCES terrain_dem(id),
    field_id UUID NOT NULL REFERENCES fields(id),

    -- Slope metrics
    slope_mean FLOAT,
    slope_max FLOAT,
    slope_min FLOAT,
    slope_std FLOAT,
    slope_class VARCHAR(20),               -- flat, gentle, moderate, steep

    -- Aspect
    dominant_aspect VARCHAR(20),           -- N, NE, E, SE, S, SW, W, NW
    aspect_diversity FLOAT,

    -- Curvature
    curvature_mean FLOAT,
    plan_curvature_mean FLOAT,
    profile_curvature_mean FLOAT,

    -- Wetness
    twi_mean FLOAT,
    twi_max FLOAT,
    wet_area_pct FLOAT,

    -- Topographic Position
    tpi_mean FLOAT,
    landform_class VARCHAR(50),            -- valley, lower_slope, flat, upper_slope, ridge

    -- Derived metrics
    drainage_density FLOAT,                -- km/km²
    relief_ratio FLOAT,

    -- Raster outputs (MinIO paths)
    slope_raster_url TEXT,
    aspect_raster_url TEXT,
    twi_raster_url TEXT,

    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_terrain_indicators_field ON terrain_indicators(field_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- Hydrology Service Tables
-- جداول خدمة الهيدرولوجيا
-- ═══════════════════════════════════════════════════════════════════════════

-- Drainage network
CREATE TABLE drainage_network (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dem_id UUID NOT NULL REFERENCES terrain_dem(id),
    field_id UUID NOT NULL REFERENCES fields(id),

    -- Network geometry
    stream_network GEOMETRY(MultiLineString, 4326),
    total_length_m FLOAT,
    stream_count INTEGER,
    max_order INTEGER,                     -- Strahler order

    -- Watershed boundary
    watershed_boundary GEOMETRY(Polygon, 4326),
    watershed_area_ha FLOAT,

    -- Network metrics
    drainage_density FLOAT,                -- km/km²
    bifurcation_ratio FLOAT,

    -- Raster outputs
    flow_direction_url TEXT,
    flow_accumulation_url TEXT,

    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_drainage_field ON drainage_network(field_id);
CREATE INDEX idx_drainage_network_geom ON drainage_network USING GIST(stream_network);

-- Waterlogging risk zones
CREATE TABLE waterlogging_risk (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    field_id UUID NOT NULL REFERENCES fields(id),

    -- Risk assessment inputs
    twi_threshold FLOAT,
    soil_ksat FLOAT,                       -- Saturated hydraulic conductivity
    clay_content FLOAT,

    -- Risk zones
    very_high_risk_area_ha FLOAT,
    high_risk_area_ha FLOAT,
    moderate_risk_area_ha FLOAT,
    low_risk_area_ha FLOAT,

    -- Risk map
    risk_map_url TEXT,
    risk_zones GEOMETRY(MultiPolygon, 4326),

    -- Recommendations
    recommendations JSONB,

    assessed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_waterlogging_field ON waterlogging_risk(field_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- Leveling Optimizer Service Tables
-- جداول خدمة تحسين التسوية
-- ═══════════════════════════════════════════════════════════════════════════

-- Leveling projects
CREATE TABLE leveling_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    field_id UUID NOT NULL REFERENCES fields(id),

    -- Project info
    project_name VARCHAR(200),
    project_name_ar VARCHAR(200),
    status VARCHAR(50) DEFAULT 'draft',    -- draft, approved, in_progress, completed

    -- Design parameters
    design_objective VARCHAR(50),          -- minimum_earthwork, target_slope, minimum_cost
    target_slope_pct FLOAT,
    slope_direction_deg FLOAT,

    -- Input DEM
    input_dem_id UUID REFERENCES terrain_dem(id),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Leveling design results
CREATE TABLE leveling_designs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES leveling_projects(id),

    -- Volumes
    cut_volume_m3 FLOAT NOT NULL,
    fill_volume_m3 FLOAT NOT NULL,
    balance_m3 FLOAT,                      -- Cut - Fill
    shrinkage_applied BOOLEAN DEFAULT true,

    -- Design surface
    design_surface_url TEXT,               -- Designed elevation raster
    cut_fill_depth_url TEXT,               -- Cut/fill depth map

    -- Cost breakdown (SAR)
    excavation_cost FLOAT,
    fill_cost FLOAT,
    haul_cost FLOAT,
    equipment_cost FLOAT,
    survey_cost FLOAT,
    contingency FLOAT,
    total_cost_sar FLOAT,
    cost_per_ha_sar FLOAT,

    -- Schedule
    estimated_days INTEGER,
    equipment_hours JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_leveling_designs_project ON leveling_designs(project_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- Edge Orchestrator Service Tables
-- جداول خدمة إدارة الحافة
-- ═══════════════════════════════════════════════════════════════════════════

-- Edge devices registry
CREATE TABLE edge_devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),

    -- Device identification
    device_serial VARCHAR(100) NOT NULL UNIQUE,
    device_name VARCHAR(200),
    device_type VARCHAR(50) NOT NULL,      -- jetson_orin_nano, jetson_orin_nx

    -- Assignment
    farm_id UUID REFERENCES farms(id),
    field_id UUID REFERENCES fields(id),

    -- Location
    location GEOMETRY(Point, 4326),
    installation_date DATE,

    -- Status
    status VARCHAR(50) DEFAULT 'offline',  -- online, offline, maintenance
    last_seen_at TIMESTAMPTZ,

    -- Hardware info
    firmware_version VARCHAR(50),
    ip_address INET,
    mac_address MACADDR,

    -- Configuration
    config JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_edge_devices_tenant ON edge_devices(tenant_id);
CREATE INDEX idx_edge_devices_field ON edge_devices(field_id);
CREATE INDEX idx_edge_devices_status ON edge_devices(status);

-- Device metrics (time-series)
CREATE TABLE edge_device_metrics (
    time TIMESTAMPTZ NOT NULL,
    device_id UUID NOT NULL REFERENCES edge_devices(id),

    -- System metrics
    cpu_usage_pct FLOAT,
    gpu_usage_pct FLOAT,
    memory_usage_pct FLOAT,
    storage_usage_pct FLOAT,
    temperature_c FLOAT,
    power_watts FLOAT,

    -- Inference metrics
    inference_count INTEGER DEFAULT 0,
    inference_latency_ms FLOAT,
    detection_count INTEGER DEFAULT 0,

    -- Network
    network_rx_bytes BIGINT,
    network_tx_bytes BIGINT,
    mqtt_connected BOOLEAN
);

-- TimescaleDB hypertable (if using TimescaleDB)
-- SELECT create_hypertable('edge_device_metrics', 'time');
CREATE INDEX idx_device_metrics_device ON edge_device_metrics(device_id, time DESC);

-- Model deployments tracking
CREATE TABLE model_deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL REFERENCES edge_devices(id),
    model_id UUID NOT NULL REFERENCES vision_models(id),

    -- Deployment info
    deployment_status VARCHAR(50),         -- pending, downloading, installing, active, failed
    deployed_at TIMESTAMPTZ,

    -- Version tracking
    previous_model_id UUID REFERENCES vision_models(id),

    -- Performance post-deployment
    avg_inference_ms FLOAT,
    error_rate FLOAT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_model_deployments_device ON model_deployments(device_id);

-- OTA update history
CREATE TABLE ota_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL REFERENCES edge_devices(id),

    update_type VARCHAR(50) NOT NULL,      -- firmware, model, config
    from_version VARCHAR(50),
    to_version VARCHAR(50) NOT NULL,

    status VARCHAR(50) NOT NULL,           -- pending, downloading, installing, completed, failed, rolled_back
    progress_pct INTEGER DEFAULT 0,

    scheduled_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    error_message TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ota_updates_device ON ota_updates(device_id);
CREATE INDEX idx_ota_updates_status ON ota_updates(status);
```

### Schema Migration Script | سكريبت ترحيل المخطط

```sql
-- Migration: V20260201__yolo26_terrain_integration.sql
-- Description: Add tables for YOLO26 Vision and Terrain Analysis services

BEGIN;

-- Verify prerequisites
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis') THEN
        RAISE EXCEPTION 'PostGIS extension required';
    END IF;
END $$;

-- Create all tables from above schema...
-- (Include all CREATE TABLE statements)

-- Add foreign key constraints for existing tables
ALTER TABLE fields ADD COLUMN IF NOT EXISTS
    terrain_indicator_id UUID REFERENCES terrain_indicators(id);

ALTER TABLE fields ADD COLUMN IF NOT EXISTS
    waterlogging_risk_id UUID REFERENCES waterlogging_risk(id);

-- Create aggregated views
CREATE OR REPLACE VIEW v_field_terrain_summary AS
SELECT
    f.id AS field_id,
    f.name AS field_name,
    ti.slope_mean,
    ti.slope_class,
    ti.dominant_aspect,
    ti.twi_mean,
    ti.landform_class,
    wr.very_high_risk_area_ha,
    wr.high_risk_area_ha
FROM fields f
LEFT JOIN terrain_indicators ti ON f.terrain_indicator_id = ti.id
LEFT JOIN waterlogging_risk wr ON f.waterlogging_risk_id = wr.id;

CREATE OR REPLACE VIEW v_field_detection_summary AS
SELECT
    field_id,
    detection_type,
    detection_class,
    COUNT(*) AS detection_count,
    AVG(confidence) AS avg_confidence,
    MAX(created_at) AS last_detected
FROM vision_detections
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY field_id, detection_type, detection_class;

COMMIT;
```

---

## ملخص نقاط الوصول API | API Endpoints Summary

### Complete Endpoint Registry | سجل نقاط الوصول الكامل

| Service | Endpoint | Method | Description | Arabic |
|---------|----------|--------|-------------|--------|
| **YOLO26 Vision** |||||
| | `/api/v1/detect/pest` | POST | Detect pests | كشف الآفات |
| | `/api/v1/detect/disease` | POST | Detect diseases | كشف الأمراض |
| | `/api/v1/detect/weed` | POST | Detect weeds | كشف الأعشاب |
| | `/api/v1/count/plants` | POST | Count plants | عد النباتات |
| | `/api/v1/classify/ripeness` | POST | Classify ripeness | تصنيف النضج |
| | `/api/v1/segment/leaf` | POST | Segment leaves | تجزئة الأوراق |
| | `/api/v1/batch/analyze` | POST | Batch analysis | تحليل دفعي |
| | `/api/v1/models` | GET | List models | قائمة النماذج |
| **Terrain Core** |||||
| | `/api/v1/dem/upload` | POST | Upload DEM | رفع DEM |
| | `/api/v1/dem/fetch` | POST | Fetch from source | جلب من المصدر |
| | `/api/v1/indicators/slope` | POST | Calculate slope | حساب الانحدار |
| | `/api/v1/indicators/aspect` | POST | Calculate aspect | حساب الاتجاه |
| | `/api/v1/indicators/twi` | POST | Calculate TWI | حساب TWI |
| | `/api/v1/indicators/all` | POST | All indicators | جميع المؤشرات |
| | `/api/v1/terrain/report` | POST | Terrain report | تقرير التضاريس |
| **Hydrology** |||||
| | `/api/v1/drainage/network` | POST | Extract network | استخراج الشبكة |
| | `/api/v1/drainage/watershed` | POST | Delineate watershed | تحديد الحوض |
| | `/api/v1/waterlogging/risk` | POST | Risk assessment | تقييم المخاطر |
| | `/api/v1/runoff/estimate` | POST | Estimate runoff | تقدير الجريان |
| | `/api/v1/hydrology/report` | POST | Full report | التقرير الكامل |
| **Leveling Optimizer** |||||
| | `/api/v1/leveling/design` | POST | Create design | إنشاء التصميم |
| | `/api/v1/leveling/volumes` | POST | Calculate volumes | حساب الأحجام |
| | `/api/v1/leveling/cost` | POST | Cost estimate | تقدير التكلفة |
| | `/api/v1/leveling/optimize` | POST | Run optimization | تشغيل التحسين |
| | `/api/v1/leveling/report` | POST | Generate report | إنشاء التقرير |
| **Edge Orchestrator** |||||
| | `/api/v1/devices` | GET | List devices | قائمة الأجهزة |
| | `/api/v1/devices/{id}` | GET | Device details | تفاصيل الجهاز |
| | `/api/v1/devices/{id}/configure` | POST | Configure device | تكوين الجهاز |
| | `/api/v1/devices/{id}/restart` | POST | Restart device | إعادة تشغيل |
| | `/api/v1/models/deploy` | POST | Deploy model | نشر النموذج |
| | `/api/v1/models/rollback` | POST | Rollback model | التراجع |
| | `/api/v1/ota/firmware` | POST | Firmware update | تحديث البرامج |
| | `/api/v1/ota/status` | GET | Update status | حالة التحديث |
| | `/api/v1/results/stream` | WS | Results stream | بث النتائج |
| | `/api/v1/results/history` | GET | Historical results | النتائج التاريخية |
| | `/api/v1/fleet/dashboard` | GET | Fleet dashboard | لوحة الأسطول |
| | `/api/v1/fleet/coverage` | GET | Coverage map | خريطة التغطية |

### Common Endpoints (All Services) | نقاط الوصول المشتركة

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Liveness probe |
| `/readyz` | GET | Readiness probe |
| `/health` | GET | Combined health status |
| `/metrics` | GET | Prometheus metrics |
| `/api/v1/docs` | GET | OpenAPI documentation |

---

## استراتيجية النشر | Deployment Strategy

### Phase Overview | نظرة عامة على المراحل

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         16-WEEK DEPLOYMENT TIMELINE                                  │
│                         الجدول الزمني للنشر (16 أسبوع)                             │
└─────────────────────────────────────────────────────────────────────────────────────┘

Week:    1    2    3    4    5    6    7    8    9   10   11   12   13   14   15   16
         │    │    │    │    │    │    │    │    │    │    │    │    │    │    │    │
Phase 1: ████████                                                   Cloud Infrastructure
         YOLO26 Cloud                                              البنية السحابية

Phase 2:           ████████████████                                Terrain Analysis
                   Terrain Core + Hydrology + Leveling             تحليل التضاريس

Phase 3:                              ████████████████             Edge Computing
                                      Edge Orchestrator + Devices   الحوسبة الطرفية

Phase 4:                                                 ██████████ Mobile Integration
                                                         Flutter UI  تكامل الجوال

Phase 5:                                                           ████ Integration
                                                                   Full System  التكامل

         │─────── Feb 2026 ───────│─────── Mar 2026 ───────│─────── Apr 2026 ───────│─── May ───│
```

### Phase 1: Cloud Infrastructure (Week 1-2)

#### البنية السحابية | Cloud Setup

```yaml
phase_1:
  name: "Cloud Infrastructure"
  name_ar: "البنية السحابية"
  duration: "Week 1-2 (Feb 1-14, 2026)"

  objectives:
    - Deploy YOLO26 Vision Service to cloud
    - Configure GPU instances (NVIDIA T4/A10G)
    - Setup model artifact storage (MinIO)
    - Integrate with NATS message bus

  deliverables:
    week_1:
      - GPU Kubernetes node pool provisioned
      - YOLO26 service Docker image built
      - Model weights uploaded to MinIO
      - Basic inference endpoint working

    week_2:
      - All detection endpoints operational
      - Integration with field-management-service
      - NATS event publishing configured
      - Load testing completed (target: 100 req/min)

  infrastructure:
    cloud_provider: "AWS/Azure/GCP"
    compute:
      - type: "g4dn.xlarge (AWS) / NC4as_T4 (Azure)"
        count: 2
        gpu: "NVIDIA T4 16GB"
        cost_hourly: $0.526
    storage:
      - MinIO: 500GB (model weights, images)
      - PostgreSQL: Existing cluster

  success_criteria:
    - Pest detection accuracy >= 90%
    - Disease detection accuracy >= 88%
    - Inference latency < 500ms (p95)
    - Service uptime >= 99.5%
```

### Phase 2: Terrain Services (Week 3-6)

#### خدمات التضاريس | Terrain Services

```yaml
phase_2:
  name: "Terrain Analysis Services"
  name_ar: "خدمات تحليل التضاريس"
  duration: "Week 3-6 (Feb 15 - Mar 14, 2026)"

  objectives:
    - Deploy Terrain Core Service
    - Deploy Hydrology Service
    - Deploy Leveling Optimizer Service
    - Integrate with DEM data sources

  deliverables:
    week_3_4:
      - Terrain Core Service deployed
      - DEM ingestion from 4 sources working
      - 7 terrain indicators calculated
      - PostGIS raster storage configured

    week_5_6:
      - Hydrology Service deployed
      - Leveling Optimizer deployed
      - End-to-end terrain analysis pipeline
      - Field management UI integration

  infrastructure:
    compute:
      - type: "c5.2xlarge (AWS) / D4s_v3 (Azure)"
        count: 3
        cpu: 8 cores
        memory: 16GB
    storage:
      - PostGIS: +100GB for rasters
      - MinIO: +200GB for DEM tiles

  data_sources_integration:
    srtm:
      api: "USGS EarthExplorer"
      automation: "Scheduled fetch for new fields"
    copernicus:
      api: "Copernicus Data Space"
      credentials: "Service account"
    drone:
      format: "GeoTIFF"
      upload: "Manual via API"

  success_criteria:
    - DEM processing < 5 min per 100 ha
    - All 7 indicators calculated correctly
    - Drainage network extraction validated
    - Cost estimation within 15% accuracy
```

### Phase 3: Edge Computing (Week 7-10)

#### الحوسبة الطرفية | Edge Deployment

```yaml
phase_3:
  name: "Edge Computing Infrastructure"
  name_ar: "البنية الطرفية"
  duration: "Week 7-10 (Mar 15 - Apr 11, 2026)"

  objectives:
    - Deploy Edge Orchestrator Service
    - Provision 50 Jetson Orin devices
    - Configure MQTT broker cluster
    - Implement OTA update system

  deliverables:
    week_7_8:
      - Edge Orchestrator deployed
      - MQTT broker (EMQX) configured
      - Device provisioning workflow
      - First 10 devices online

    week_9_10:
      - All 50 devices deployed
      - Model deployment pipeline working
      - Real-time detection streaming
      - Offline mode tested

  hardware_deployment:
    devices:
      model: "NVIDIA Jetson Orin Nano"
      count: 50
      unit_cost: $499
      total: $24,950

    enclosures:
      spec: "IP65, -25°C to 50°C"
      count: 50
      unit_cost: $150
      total: $7,500

    cameras:
      spec: "4K USB, IP67"
      count: 100 (2 per device)
      unit_cost: $120
      total: $12,000

    network:
      cellular: "4G LTE modems"
      count: 50
      unit_cost: $80
      data_plan: "$20/month/device"

  deployment_locations:
    - Al-Qassim Region: 20 devices
    - Central Saudi Arabia: 15 devices
    - Eastern Province: 15 devices

  success_criteria:
    - 95% device uptime
    - Edge inference < 100ms latency
    - Offline buffer works for 7 days
    - OTA update success rate > 98%
```

### Phase 4: Mobile Integration (Week 11-14)

#### تكامل الجوال | Mobile App

```yaml
phase_4:
  name: "Mobile App Integration"
  name_ar: "تكامل تطبيق الجوال"
  duration: "Week 11-14 (Apr 12 - May 9, 2026)"

  objectives:
    - Add YOLO26 detection UI to Flutter app
    - Integrate terrain analysis visualization
    - Implement camera capture for pest detection
    - Add leveling project management

  deliverables:
    week_11_12:
      - Pest/disease detection camera feature
      - Detection results display with Arabic labels
      - Offline detection using edge devices
      - Push notifications for critical alerts

    week_13_14:
      - Terrain analysis visualization (MapLibre)
      - Leveling project creation workflow
      - Cut/fill volume visualizer
      - Cost estimation display

  flutter_features:
    camera_detection:
      - Live preview with detection overlay
      - Manual photo capture
      - Gallery selection
      - Results history

    terrain_visualization:
      - Slope heatmap layer
      - Aspect compass overlay
      - TWI wetness display
      - Drainage network layer

    leveling_tools:
      - Project wizard (3 steps)
      - Volume calculator
      - Cost breakdown view
      - PDF report generation

  localization:
    languages: ["ar", "en"]
    new_strings: 450+

  success_criteria:
    - Detection feature usable offline
    - Terrain maps load in < 3 seconds
    - App size increase < 15MB
    - User testing approval (80%+ satisfaction)
```

### Phase 5: System Integration (Week 15-16)

#### التكامل الكامل | Full Integration

```yaml
phase_5:
  name: "System Integration & Testing"
  name_ar: "التكامل والاختبار"
  duration: "Week 15-16 (May 10-23, 2026)"

  objectives:
    - End-to-end integration testing
    - Performance optimization
    - Security audit
    - Documentation completion

  deliverables:
    week_15:
      - Integration test suite (50+ scenarios)
      - Load testing at scale (10x normal)
      - Security penetration testing
      - Bug fixes and optimization

    week_16:
      - Production deployment
      - Monitoring dashboards
      - Runbook documentation
      - Training materials

  testing_scope:
    integration_tests:
      - Mobile → Edge → Cloud flow
      - Terrain analysis pipeline
      - Leveling cost calculation
      - Alert propagation

    load_tests:
      - 1000 concurrent detections
      - 50 edge devices reporting
      - 100 terrain analysis jobs

    security_tests:
      - API authentication
      - Device authentication (mTLS)
      - Data encryption at rest
      - Network segmentation

  documentation:
    - API reference (OpenAPI)
    - Integration guide
    - Troubleshooting runbook
    - Arabic user guide

  success_criteria:
    - All integration tests passing
    - p99 latency within SLA
    - Zero critical security issues
    - Production sign-off
```

---

## مقاييس النجاح | Success Metrics

### Key Performance Indicators (KPIs) | مؤشرات الأداء الرئيسية

#### Technical Metrics | المقاييس التقنية

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Detection Accuracy** | >= 90% | F1-score on test dataset |
| **Inference Latency (Cloud)** | < 500ms | p95 response time |
| **Inference Latency (Edge)** | < 100ms | p95 local processing |
| **System Uptime** | >= 99.5% | Monthly availability |
| **Edge Device Uptime** | >= 95% | Device online percentage |
| **API Error Rate** | < 1% | 5xx responses |
| **Model Deployment Success** | >= 98% | OTA success rate |

#### Business Metrics | مقاييس الأعمال

| Metric | Target | Arabic | المقياس |
|--------|--------|--------|---------|
| **Pest Detection Coverage** | 20+ species | 20+ نوع | تغطية كشف الآفات |
| **Disease Detection Coverage** | 30+ diseases | 30+ مرض | تغطية كشف الأمراض |
| **Fields with Terrain Analysis** | 500+ fields | 500+ حقل | الحقول المحللة |
| **Edge Devices Deployed** | 50 units | 50 وحدة | الأجهزة المنشورة |
| **Manual Scouting Reduction** | 60% | 60% | تقليل الجولات اليدوية |
| **Water Waste Reduction** | 25% | 25% | تقليل هدر المياه |
| **Cost Savings per Hectare** | 500 SAR/year | 500 ريال/سنة | توفير التكاليف |

#### ROI Calculation | حساب العائد على الاستثمار

```yaml
investment:
  development_cost: $56,000
  infrastructure_cost: $24,000
  hardware_cost: $44,497
  contingency: $11,550
  total_investment: $136,047

annual_benefits:
  pest_loss_reduction:
    description: "Early detection reduces crop loss"
    affected_area: 5000 ha
    loss_reduction: 5%
    value_per_ha: 2000 SAR
    total: 500,000 SAR ($133,333)

  water_savings:
    description: "Terrain-informed irrigation"
    affected_area: 5000 ha
    water_reduction: 25%
    cost_per_ha: 400 SAR
    total: 500,000 SAR ($133,333)

  labor_savings:
    description: "Reduced manual scouting"
    scouts_replaced: 10
    annual_cost_per_scout: 60,000 SAR
    total: 600,000 SAR ($160,000)

  total_annual_benefit: $426,666

roi_calculation:
  year_1_roi: "(426,666 - 136,047) / 136,047 = 213%"
  payback_period: "4 months"
  5_year_npv: "$1,650,000"
```

---

## إدارة المخاطر | Risk Management

### Risk Register | سجل المخاطر

| ID | Risk | Arabic | Probability | Impact | Mitigation |
|----|------|--------|-------------|--------|------------|
| R1 | GPU shortage delays cloud deployment | تأخر توفر GPU | Medium | High | Pre-reserve instances; multi-cloud fallback |
| R2 | Jetson device supply chain issues | مشاكل توريد Jetson | Medium | High | Order 3 months early; alternative supplier |
| R3 | Model accuracy below target | دقة النموذج أقل من المطلوب | Low | High | Extended training; expert annotation review |
| R4 | Network connectivity in remote fields | ضعف الشبكة في المناطق النائية | High | Medium | Offline-first design; mesh networking |
| R5 | Integration complexity with legacy services | تعقيد التكامل | Medium | Medium | Phased rollout; feature flags |
| R6 | User adoption resistance | مقاومة المستخدمين | Medium | Medium | Training program; Arabic UI; voice support |
| R7 | Edge device environmental damage | تلف الأجهزة الطرفية | Low | Low | IP65 enclosures; maintenance schedule |
| R8 | Security vulnerabilities in edge fleet | ثغرات أمنية | Low | Critical | mTLS; regular security audits; OTA patching |

### Risk Mitigation Strategies | استراتيجيات التخفيف

```yaml
mitigation_strategies:
  hardware_risks:
    - Maintain 10% spare device inventory
    - Multi-supplier procurement strategy
    - Local repair partnership in each region

  software_risks:
    - Comprehensive test suite (>80% coverage)
    - Canary deployments for model updates
    - Automatic rollback on error spike

  operational_risks:
    - 24/7 monitoring with PagerDuty
    - On-call rotation for edge issues
    - Regional support teams

  adoption_risks:
    - Pilot with 5 farms before full rollout
    - Bilingual training materials
    - Success stories and ROI reports
```

### Contingency Plans | خطط الطوارئ

```yaml
contingency_plans:
  cloud_gpu_unavailable:
    trigger: "No GPU instances available for >48h"
    action:
      - Failover to CPU-only inference (slower)
      - Queue non-urgent requests
      - Escalate to cloud provider

  edge_device_failure:
    trigger: "Device offline >24h"
    action:
      - Remote diagnostic
      - Dispatch replacement if hardware issue
      - Reroute to cloud inference temporarily

  model_performance_degradation:
    trigger: "F1-score drops >5% in production"
    action:
      - Automatic rollback to previous model
      - Trigger retraining pipeline
      - Expert review of failure cases

  security_incident:
    trigger: "Suspicious activity detected"
    action:
      - Isolate affected devices
      - Revoke compromised credentials
      - Forensic investigation
      - Patch deployment
```

---

## Budget Breakdown | تفصيل الميزانية

### Cost Summary | ملخص التكاليف

| Category | Amount (USD) | Amount (SAR) | % of Total |
|----------|--------------|--------------|------------|
| **Development** | $56,000 | 210,000 | 41.2% |
| **Cloud Infrastructure** | $24,000 | 90,000 | 17.6% |
| **Edge Hardware** | $44,497 | 166,863 | 32.7% |
| **Contingency (10%)** | $11,550 | 43,313 | 8.5% |
| **Total** | **$136,047** | **510,176** | 100% |

### Detailed Cost Breakdown | التفصيل المفصل

```yaml
development_costs:
  yolo26_service:
    model_development: $15,000
    api_development: $8,000
    testing: $5,000
    subtotal: $28,000

  terrain_services:
    terrain_core: $6,000
    hydrology: $5,000
    leveling: $5,000
    subtotal: $16,000

  edge_orchestrator:
    service_development: $6,000
    device_firmware: $4,000
    subtotal: $10,000

  mobile_integration:
    flutter_features: $2,000
    subtotal: $2,000

  total_development: $56,000

infrastructure_costs:
  cloud_compute:
    gpu_instances: "$0.53/hr × 2 × 730hr × 12mo = $9,291"
    cpu_instances: "$0.34/hr × 3 × 730hr × 12mo = $8,935"
    subtotal: $18,226

  storage:
    minio_s3: "$0.023/GB × 1000GB × 12mo = $276"
    postgresql: "Existing cluster (no additional cost)"
    subtotal: $276

  networking:
    data_transfer: "$0.09/GB × 500GB × 12mo = $540"
    load_balancer: "$20/mo × 12mo = $240"
    subtotal: $780

  monitoring:
    prometheus_grafana: "Self-hosted (no cost)"
    alerting: "$200/mo × 12mo = $2,400"
    subtotal: $2,400

  mqtt_broker:
    emqx_cluster: "$175/mo × 12mo = $2,100"

  total_infrastructure: $23,782 (rounded to $24,000)

hardware_costs:
  jetson_devices:
    unit_cost: $499
    quantity: 50
    subtotal: $24,950

  enclosures:
    unit_cost: $150
    quantity: 50
    subtotal: $7,500

  cameras:
    unit_cost: $120
    quantity: 100
    subtotal: $12,000

  accessories:
    cables_mounts: $47
    subtotal: $47

  total_hardware: $44,497

contingency:
  rate: 10%
  amount: $11,550
```

---

## Appendices | الملاحق

### Appendix A: Service Registry Update | تحديث سجل الخدمات

```yaml
# Add to governance/services.yaml

services:
  # ═══════════════════════════════════════════════════════════════════════════
  # YOLO26 VISION SERVICE - خدمة الرؤية YOLO26
  # ═══════════════════════════════════════════════════════════════════════════
  yolo26-vision-service:
    name: "YOLO26 Vision Service"
    name_ar: "خدمة الرؤية YOLO26"
    type: python
    category: analytics
    layer: intelligence
    port: 8150
    status: planned
    planned_date: "2026-02-01"
    owner: "ML Team"
    description: "Computer vision for pest, disease, and weed detection"
    endpoints:
      - "/api/v1/detect/pest"
      - "/api/v1/detect/disease"
      - "/api/v1/detect/weed"
      - "/api/v1/count/plants"
    dependencies:
      - field-management-service
      - notification-service
      - minio
    events:
      publishes:
        - sahool.vision.pest.detected
        - sahool.vision.disease.detected
        - sahool.vision.weed.detected
      subscribes:
        - sahool.edge.image.uploaded

  # ═══════════════════════════════════════════════════════════════════════════
  # TERRAIN CORE SERVICE - خدمة التضاريس الأساسية
  # ═══════════════════════════════════════════════════════════════════════════
  terrain-core-service:
    name: "Terrain Core Service"
    name_ar: "خدمة التضاريس الأساسية"
    type: python
    category: analytics
    layer: intelligence
    port: 8160
    status: planned
    planned_date: "2026-02-15"
    owner: "GIS Team"
    description: "DEM processing and terrain indicator calculation"
    endpoints:
      - "/api/v1/dem/upload"
      - "/api/v1/indicators/all"
      - "/api/v1/terrain/report"
    dependencies:
      - field-management-service
      - minio

  # ═══════════════════════════════════════════════════════════════════════════
  # HYDROLOGY SERVICE - خدمة الهيدرولوجيا
  # ═══════════════════════════════════════════════════════════════════════════
  hydrology-service:
    name: "Hydrology Service"
    name_ar: "خدمة الهيدرولوجيا"
    type: python
    category: analytics
    layer: intelligence
    port: 8165
    status: planned
    planned_date: "2026-03-01"
    owner: "GIS Team"
    description: "Drainage network analysis and waterlogging prediction"
    dependencies:
      - terrain-core-service
      - weather-service

  # ═══════════════════════════════════════════════════════════════════════════
  # LEVELING OPTIMIZER SERVICE - خدمة تحسين التسوية
  # ═══════════════════════════════════════════════════════════════════════════
  leveling-optimizer-service:
    name: "Leveling Optimizer Service"
    name_ar: "خدمة تحسين التسوية"
    type: python
    category: analytics
    layer: decision
    port: 8170
    status: planned
    planned_date: "2026-03-01"
    owner: "Engineering Team"
    description: "Cut/fill volume calculation and cost estimation"
    dependencies:
      - terrain-core-service

  # ═══════════════════════════════════════════════════════════════════════════
  # EDGE ORCHESTRATOR SERVICE - خدمة إدارة الحافة
  # ═══════════════════════════════════════════════════════════════════════════
  edge-orchestrator-service:
    name: "Edge Orchestrator Service"
    name_ar: "خدمة إدارة الحافة"
    type: python
    category: integration
    layer: acquisition
    port: 8180
    status: planned
    planned_date: "2026-03-15"
    owner: "Platform Team"
    description: "Jetson Orin device management and model deployment"
    endpoints:
      - "/api/v1/devices"
      - "/api/v1/models/deploy"
      - "/api/v1/ota/firmware"
    dependencies:
      - yolo26-vision-service
      - mqtt-broker
```

### Appendix B: NATS Event Definitions | تعريفات أحداث NATS

```yaml
# Add to packages/shared-events/events.yaml

events:
  # Vision Events
  sahool.vision.pest.detected:
    description: "Pest detected in field image"
    schema:
      field_id: uuid
      device_id: uuid
      detection_class: string
      confidence: float
      severity: string
      image_url: string
      location: object
      timestamp: datetime

  sahool.vision.disease.detected:
    description: "Disease detected in plant image"
    schema:
      field_id: uuid
      crop_type: string
      disease_class: string
      confidence: float
      severity: string
      image_url: string

  sahool.vision.alert.critical:
    description: "Critical detection requiring immediate attention"
    priority: high

  # Terrain Events
  sahool.terrain.analysis.completed:
    description: "Terrain analysis completed for field"
    schema:
      field_id: uuid
      dem_source: string
      indicators: object

  sahool.terrain.waterlogging.risk:
    description: "Waterlogging risk assessment updated"

  # Edge Events
  sahool.edge.device.online:
    description: "Edge device came online"

  sahool.edge.device.offline:
    description: "Edge device went offline"

  sahool.edge.model.deployed:
    description: "Model deployed to edge device"

  sahool.edge.inference.completed:
    description: "Inference completed on edge device"
```

### Appendix C: Environment Variables | متغيرات البيئة

```bash
# Add to .env.example

# ═══════════════════════════════════════════════════════════════════════════
# YOLO26 Vision Service
# ═══════════════════════════════════════════════════════════════════════════
YOLO26_MODEL_PATH=/models/yolo26
YOLO26_CONFIDENCE_THRESHOLD=0.5
YOLO26_NMS_THRESHOLD=0.45
YOLO26_INPUT_SIZE=640
YOLO26_BATCH_SIZE=8
YOLO26_GPU_DEVICE=0

# ═══════════════════════════════════════════════════════════════════════════
# Terrain Services
# ═══════════════════════════════════════════════════════════════════════════
TERRAIN_DEM_CACHE_DIR=/data/dem_cache
TERRAIN_RASTER_OUTPUT_DIR=/data/rasters
COPERNICUS_API_KEY=xxx
USGS_USERNAME=xxx
USGS_PASSWORD=xxx

# ═══════════════════════════════════════════════════════════════════════════
# Edge Orchestrator
# ═══════════════════════════════════════════════════════════════════════════
MQTT_BROKER_URL=mqtt://mqtt.sahool.local:1883
MQTT_USERNAME=edge_orchestrator
MQTT_PASSWORD=xxx
EDGE_DEVICE_TIMEOUT_SEC=300
OTA_UPDATE_SERVER=https://ota.sahool.local

# ═══════════════════════════════════════════════════════════════════════════
# MinIO Object Storage
# ═══════════════════════════════════════════════════════════════════════════
MINIO_ENDPOINT=minio.sahool.local:9000
MINIO_ACCESS_KEY=xxx
MINIO_SECRET_KEY=xxx
MINIO_BUCKET_IMAGES=vision-images
MINIO_BUCKET_MODELS=model-weights
MINIO_BUCKET_RASTERS=terrain-rasters
```

---

## Document Control | التحكم بالوثيقة

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-02-01 | KAFAAT Engineering | Initial release |

### Approvals | الموافقات

| Role | Name | Date | Signature |
|------|------|------|-----------|
| **Project Manager** | | | |
| **Technical Lead** | | | |
| **Security Officer** | | | |
| **Product Owner** | | | |

---

*Last Updated: February 2026*

*This document is part of the SAHOOL Platform documentation. For questions, contact the Platform Engineering team.*

*هذه الوثيقة جزء من وثائق منصة سهول. للاستفسارات، تواصل مع فريق هندسة المنصة.*
