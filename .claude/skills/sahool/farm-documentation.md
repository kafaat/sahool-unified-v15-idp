# Farm Documentation Generation Skill

## Description

This skill enables automated generation of comprehensive farm documentation for SAHOOL agricultural platform. It creates standardized records for field operations, crop cycles, input applications, yield records, and compliance documentation. Supports Arabic/English bilingual output with structured formats suitable for regulatory submission, farm management, and knowledge transfer.

## Instructions

### Documentation Types

Generate the following documentation types:

```yaml
documentation_types:
  operational:
    - field_record: Individual field documentation
    - season_report: Seasonal crop cycle summary
    - operations_log: Daily/weekly activities
    - input_register: Fertilizer, pesticide applications

  compliance:
    - pesticide_log: Regulatory pesticide record
    - water_usage: Irrigation water accounting
    - gmp_checklist: Good Agricultural Practices
    - traceability: Crop origin documentation

  planning:
    - crop_plan: Season planning document
    - rotation_schedule: Multi-year rotation plan
    - budget_forecast: Input and revenue projections

  knowledge:
    - best_practices: Field-specific learnings
    - variety_performance: Variety comparison records
    - problem_resolution: Issue documentation
```

### Document Structure Standards

#### Header Block (Required for all documents)
```yaml
document_header:
  doc_type: [type]
  doc_id: [unique identifier]
  version: [x.y]
  language: [ar|en|bilingual]
  farm_id: [FARM-XXX]
  field_id: [FIELD-XXX] (if applicable)
  created_by: [name/system]
  created_date: [ISO-8601]
  last_updated: [ISO-8601]
  status: [draft|active|archived]
```

#### Metadata Block
```yaml
metadata:
  season: [year-season]
  crop: [crop_type]
  variety: [variety_name]
  area: [hectares]
  location:
    region: [region_name]
    coordinates: [lat, lon]
```

### Template: Field Record Document

```markdown
---
doc_type: field_record
doc_id: FR-[FIELD-ID]-[YEAR]
version: 1.0
language: bilingual
---

# Field Record | سجل الحقل
## [Field Name] | [اسم الحقل]

### Basic Information | المعلومات الأساسية

| Parameter (EN) | Value | المعلمة (AR) | القيمة |
|----------------|-------|--------------|--------|
| Field ID | [ID] | رقم الحقل | [ID] |
| Farm | [Farm Name] | المزرعة | [اسم المزرعة] |
| Area | [X.X] ha | المساحة | [X.X] هكتار |
| Soil Type | [type] | نوع التربة | [النوع] |
| Irrigation | [system] | نظام الري | [النظام] |
| GPS Center | [lat, lon] | الإحداثيات | [lat, lon] |

### Current Season | الموسم الحالي

**Crop:** [Crop] ([Variety]) | **المحصول:** [المحصول] ([الصنف])
**Season:** [Year-Season] | **الموسم:** [السنة-الموسم]

#### Timeline | الجدول الزمني
| Event | Date | الحدث | التاريخ |
|-------|------|-------|---------|
| Planting | [date] | الزراعة | [تاريخ] |
| Emergence | [date] | الإنبات | [تاريخ] |
| Harvest (expected) | [date] | الحصاد (متوقع) | [تاريخ] |

### Soil Analysis | تحليل التربة

**Date:** [analysis_date] | **التاريخ:** [تاريخ التحليل]

| Parameter | Value | Unit | المعلمة | القيمة | الوحدة |
|-----------|-------|------|---------|--------|--------|
| pH | [X.X] | - | الحموضة | [X.X] | - |
| EC | [X.X] | dS/m | التوصيل | [X.X] | |
| Nitrogen (N) | [XX] | ppm | نيتروجين | [XX] | جزء/مليون |
| Phosphorus (P) | [XX] | ppm | فوسفور | [XX] | جزء/مليون |
| Potassium (K) | [XXX] | ppm | بوتاسيوم | [XXX] | جزء/مليون |
| Organic Matter | [X.X] | % | مادة عضوية | [X.X] | % |

### Input Applications | تطبيقات المدخلات

#### Fertilizers | الأسمدة
| Date | Product | Rate | Method | التاريخ | المنتج | المعدل | الطريقة |
|------|---------|------|--------|---------|--------|--------|---------|
| [date] | [product] | [kg/ha] | [method] | [تاريخ] | [منتج] | [كغ/هـ] | [طريقة] |

#### Pesticides | المبيدات
| Date | Product | Target | Rate | PHI | التاريخ | المنتج | الهدف | المعدل | فترة الأمان |
|------|---------|--------|------|-----|---------|--------|-------|--------|-------------|
| [date] | [product] | [pest] | [ml/ha] | [days] | [تاريخ] | [منتج] | [آفة] | [مل/هـ] | [أيام] |

### Irrigation Record | سجل الري

| Date | Volume | Method | Notes | التاريخ | الكمية | الطريقة | ملاحظات |
|------|--------|--------|-------|---------|--------|---------|---------|
| [date] | [m³/ha] | [method] | [notes] | [تاريخ] | [م³/هـ] | [طريقة] | [ملاحظات] |

**Total Season Water:** [XXXX] m³/ha | **إجمالي مياه الموسم:** [XXXX] م³/هـ

### Observations | الملاحظات

[Date-stamped observations in chronological order]

### Attachments | المرفقات
- [ ] Soil analysis report | تقرير تحليل التربة
- [ ] Satellite imagery | صور الأقمار الصناعية
- [ ] Field photos | صور الحقل
- [ ] Sensor data export | تصدير بيانات الحساسات

---
**Document Generated:** [timestamp] | **إنشاء المستند:** [التوقيت]
**System:** SAHOOL Farm Documentation | **النظام:** توثيق سهول الزراعي
```

### Template: Season Report

```markdown
---
doc_type: season_report
doc_id: SR-[FIELD-ID]-[SEASON]
version: 1.0
---

# Season Report | تقرير الموسم
## [Season Year] - [Crop] | [سنة الموسم] - [المحصول]

### Executive Summary | الملخص التنفيذي

**English:**
[2-3 sentence summary of season performance, key metrics, and notable events]

**العربية:**
[ملخص من 2-3 جمل عن أداء الموسم والمؤشرات الرئيسية والأحداث البارزة]

### Season Overview | نظرة عامة على الموسم

| Metric | Target | Actual | Variance | المؤشر | المستهدف | الفعلي | الفرق |
|--------|--------|--------|----------|--------|----------|--------|-------|
| Yield (t/ha) | [X.X] | [X.X] | [±X%] | الإنتاج | [X.X] | [X.X] | [±X%] |
| Quality Grade | [A/B] | [A/B] | - | درجة الجودة | [أ/ب] | [أ/ب] | - |
| Water Use (m³/ha) | [XXXX] | [XXXX] | [±X%] | استخدام المياه | [XXXX] | [XXXX] | [±X%] |
| Input Cost (SAR/ha) | [XXXX] | [XXXX] | [±X%] | تكلفة المدخلات | [XXXX] | [XXXX] | [±X%] |
| Revenue (SAR/ha) | [XXXX] | [XXXX] | [±X%] | الإيرادات | [XXXX] | [XXXX] | [±X%] |
| Profit (SAR/ha) | [XXXX] | [XXXX] | [±X%] | الربح | [XXXX] | [XXXX] | [±X%] |

### Timeline Performance | أداء الجدول الزمني

| Stage | Planned | Actual | Days Variance | المرحلة | المخطط | الفعلي | فرق الأيام |
|-------|---------|--------|---------------|---------|--------|--------|------------|
| Planting | [date] | [date] | [±X] | الزراعة | [تاريخ] | [تاريخ] | [±X] |
| Emergence | [date] | [date] | [±X] | الإنبات | [تاريخ] | [تاريخ] | [±X] |
| Flowering | [date] | [date] | [±X] | الإزهار | [تاريخ] | [تاريخ] | [±X] |
| Harvest | [date] | [date] | [±X] | الحصاد | [تاريخ] | [تاريخ] | [±X] |

### Input Summary | ملخص المدخلات

#### Seed | البذور
| Item | Quantity | Cost | البند | الكمية | التكلفة |
|------|----------|------|-------|--------|---------|
| [Variety] | [kg/ha] | [SAR/ha] | [الصنف] | [كغ/هـ] | [ريال/هـ] |

#### Fertilizers | الأسمدة
| Product | Total Applied | Cost | المنتج | الإجمالي المطبق | التكلفة |
|---------|---------------|------|--------|-----------------|---------|
| [product] | [kg/ha] | [SAR/ha] | [منتج] | [كغ/هـ] | [ريال/هـ] |

#### Crop Protection | حماية المحاصيل
| Product | Applications | Total Cost | المنتج | التطبيقات | التكلفة الإجمالية |
|---------|--------------|------------|--------|-----------|-------------------|
| [product] | [X] | [SAR/ha] | [منتج] | [X] | [ريال/هـ] |

#### Water | المياه
| Source | Volume | Cost | المصدر | الكمية | التكلفة |
|--------|--------|------|--------|--------|---------|
| [source] | [m³/ha] | [SAR/ha] | [مصدر] | [م³/هـ] | [ريال/هـ] |

### Issues Encountered | المشاكل المواجهة

| Issue | Date Detected | Resolution | Impact | المشكلة | تاريخ الاكتشاف | الحل | الأثر |
|-------|---------------|------------|--------|---------|----------------|------|-------|
| [issue] | [date] | [action] | [impact] | [مشكلة] | [تاريخ] | [إجراء] | [أثر] |

### Lessons Learned | الدروس المستفادة

#### What Worked Well | ما نجح
1. [Success point 1] | [نقطة نجاح 1]
2. [Success point 2] | [نقطة نجاح 2]

#### Areas for Improvement | مجالات التحسين
1. [Improvement area 1] | [مجال تحسين 1]
2. [Improvement area 2] | [مجال تحسين 2]

#### Recommendations for Next Season | توصيات للموسم القادم
1. [Recommendation 1] | [توصية 1]
2. [Recommendation 2] | [توصية 2]

### Financial Summary | الملخص المالي

| Category | Amount (SAR/ha) | الفئة | المبلغ (ريال/هـ) |
|----------|-----------------|-------|------------------|
| **Inputs** | | **المدخلات** | |
| Seed | [XXX] | البذور | [XXX] |
| Fertilizer | [XXX] | الأسمدة | [XXX] |
| Pesticides | [XXX] | المبيدات | [XXX] |
| Water | [XXX] | المياه | [XXX] |
| Labor | [XXX] | العمالة | [XXX] |
| Equipment | [XXX] | المعدات | [XXX] |
| **Total Cost** | **[XXXX]** | **إجمالي التكلفة** | **[XXXX]** |
| | | | |
| **Revenue** | | **الإيرادات** | |
| Grain sales | [XXXX] | مبيعات الحبوب | [XXXX] |
| Straw sales | [XXX] | مبيعات القش | [XXX] |
| **Total Revenue** | **[XXXX]** | **إجمالي الإيرادات** | **[XXXX]** |
| | | | |
| **Gross Profit** | **[XXXX]** | **إجمالي الربح** | **[XXXX]** |
| **ROI** | **[XX%]** | **العائد على الاستثمار** | **[XX%]** |

---
**Report Generated:** [timestamp]
**Approved By:** [name/signature]
```

### Template: Pesticide Application Log (Compliance)

```markdown
---
doc_type: pesticide_log
doc_id: PL-[FARM-ID]-[YEAR]
version: 1.0
regulatory_compliance: true
---

# Pesticide Application Log | سجل تطبيق المبيدات
## [Farm Name] - [Year] | [اسم المزرعة] - [السنة]

### Regulatory Statement | البيان التنظيمي

This log is maintained in compliance with [regulatory body] requirements
for agricultural pesticide record-keeping.

يتم الاحتفاظ بهذا السجل امتثالاً لمتطلبات [الجهة التنظيمية] لحفظ
سجلات المبيدات الزراعية.

### Application Records | سجلات التطبيق

#### Application #[X]

| Field | 字段 |
|-------|------|
| **Application ID** | APP-[YEAR]-[XXX] |
| **Date/Time** التاريخ/الوقت | [YYYY-MM-DD HH:MM] |
| **Field ID** رقم الحقل | [FIELD-XXX] |
| **Field Area** مساحة الحقل | [X.X] ha/هكتار |
| **Treated Area** المساحة المعالجة | [X.X] ha/هكتار |
| **Crop** المحصول | [crop] / [المحصول] |
| **Growth Stage** مرحلة النمو | [stage] / [المرحلة] |

**Target Pest/Disease | الآفة/المرض المستهدف:**
[pest name] / [اسم الآفة]

**Product Information | معلومات المنتج:**

| Parameter | Value | المعلمة | القيمة |
|-----------|-------|---------|--------|
| Trade Name | [name] | الاسم التجاري | [الاسم] |
| Active Ingredient | [ingredient] | المادة الفعالة | [المادة] |
| Concentration | [X%] | التركيز | [X%] |
| Registration No. | [number] | رقم التسجيل | [الرقم] |
| Formulation | [type] | التركيبة | [النوع] |

**Application Details | تفاصيل التطبيق:**

| Parameter | Value | المعلمة | القيمة |
|-----------|-------|---------|--------|
| Rate | [X] ml/L or kg/ha | المعدل | [X] مل/لتر أو كغ/هـ |
| Total Product Used | [X] L or kg | إجمالي المنتج المستخدم | [X] لتر أو كغ |
| Water Volume | [XXX] L/ha | حجم المياه | [XXX] لتر/هـ |
| Application Method | [method] | طريقة التطبيق | [الطريقة] |
| Equipment | [equipment] | المعدات | [المعدات] |
| Nozzle Type | [type] | نوع الفوهة | [النوع] |

**Timing Restrictions | قيود التوقيت:**

| Restriction | Value | القيد | القيمة |
|-------------|-------|-------|--------|
| PHI (Pre-Harvest Interval) | [X] days | فترة ما قبل الحصاد | [X] يوم |
| REI (Re-Entry Interval) | [X] hours | فترة إعادة الدخول | [X] ساعة |
| Earliest Harvest Date | [date] | أقرب تاريخ للحصاد | [التاريخ] |
| Re-entry Allowed After | [datetime] | السماح بالدخول بعد | [التاريخ والوقت] |

**Weather Conditions at Application | الظروف الجوية عند التطبيق:**

| Condition | Value | الظرف | القيمة |
|-----------|-------|-------|--------|
| Temperature | [X]°C | الحرارة | [X] درجة |
| Humidity | [X]% | الرطوبة | [X]% |
| Wind Speed | [X] km/h | سرعة الرياح | [X] كم/س |
| Wind Direction | [direction] | اتجاه الرياح | [الاتجاه] |

**Applicator Information | معلومات المطبق:**

| Field | Value | الحقل | القيمة |
|-------|-------|-------|--------|
| Name | [name] | الاسم | [الاسم] |
| Certification No. | [number] | رقم الشهادة | [الرقم] |
| PPE Used | [list] | معدات الوقاية | [القائمة] |

**Justification | المبرر:**
[Reason for application, pest pressure level, threshold exceeded]
[سبب التطبيق، مستوى ضغط الآفة، تجاوز العتبة]

**Supervisor Approval | موافقة المشرف:**
Name/الاسم: ________________
Signature/التوقيع: ________________
Date/التاريخ: ________________

---

### Annual Summary | الملخص السنوي

| Active Ingredient | Total Used | Applications | المادة الفعالة | الإجمالي المستخدم | التطبيقات |
|-------------------|------------|--------------|----------------|-------------------|-----------|
| [ingredient 1] | [X] kg/L | [X] | [مادة 1] | [X] كغ/لتر | [X] |
| [ingredient 2] | [X] kg/L | [X] | [مادة 2] | [X] كغ/لتر | [X] |

### Certification | الشهادة

I certify that this pesticide application log is accurate and complete
to the best of my knowledge.

أشهد أن سجل تطبيق المبيدات هذا دقيق وكامل على حد علمي.

**Farm Manager | مدير المزرعة:**
Name/الاسم: ________________
Signature/التوقيع: ________________
Date/التاريخ: ________________
```

### Template: Traceability Document

```markdown
---
doc_type: traceability
doc_id: TR-[BATCH-ID]
version: 1.0
---

# Product Traceability Document | وثيقة تتبع المنتج
## Batch: [BATCH-ID] | الدفعة: [رقم الدفعة]

### Product Identification | تعريف المنتج

| Field | Value | الحقل | القيمة |
|-------|-------|-------|--------|
| Product | [crop type] | المنتج | [نوع المحصول] |
| Variety | [variety] | الصنف | [الصنف] |
| Batch ID | [BATCH-XXX] | رقم الدفعة | [BATCH-XXX] |
| Quantity | [X] tons | الكمية | [X] طن |
| Harvest Date | [date] | تاريخ الحصاد | [التاريخ] |
| Pack Date | [date] | تاريخ التعبئة | [التاريخ] |

### Origin Information | معلومات المنشأ

#### Farm Details | تفاصيل المزرعة
| Field | Value | الحقل | القيمة |
|-------|-------|-------|--------|
| Farm Name | [name] | اسم المزرعة | [الاسم] |
| Farm ID | [FARM-XXX] | رقم المزرعة | [FARM-XXX] |
| Location | [region] | الموقع | [المنطقة] |
| Coordinates | [lat, lon] | الإحداثيات | [lat, lon] |
| Field ID | [FIELD-XXX] | رقم الحقل | [FIELD-XXX] |
| Certification | [GAP/Organic/None] | الشهادة | [GAP/عضوي/لا يوجد] |

### Production History | تاريخ الإنتاج

#### Planting | الزراعة
- **Date:** [date] | **التاريخ:** [التاريخ]
- **Seed Source:** [source] | **مصدر البذور:** [المصدر]
- **Seed Lot:** [lot number] | **رقم دفعة البذور:** [الرقم]

#### Inputs Applied | المدخلات المطبقة

**Fertilizers | الأسمدة:**
| Date | Product | Rate | التاريخ | المنتج | المعدل |
|------|---------|------|---------|--------|--------|
| [date] | [product] | [rate] | [تاريخ] | [منتج] | [معدل] |

**Crop Protection | حماية المحاصيل:**
| Date | Product | PHI Compliance | التاريخ | المنتج | امتثال PHI |
|------|---------|----------------|---------|--------|------------|
| [date] | [product] | ✓ Yes | [تاريخ] | [منتج] | ✓ نعم |

#### Harvest | الحصاد
- **Date:** [date] | **التاريخ:** [التاريخ]
- **Method:** [method] | **الطريقة:** [الطريقة]
- **Equipment ID:** [ID] | **رقم المعدات:** [الرقم]

### Quality Analysis | تحليل الجودة

| Parameter | Result | Standard | Pass | المعلمة | النتيجة | المعيار | نجاح |
|-----------|--------|----------|------|---------|---------|---------|------|
| Moisture | [X%] | <14% | ✓ | الرطوبة | [X%] | <14% | ✓ |
| Impurities | [X%] | <2% | ✓ | الشوائب | [X%] | <2% | ✓ |
| Pesticide Residue | [result] | MRL | ✓ | متبقيات المبيدات | [نتيجة] | الحد | ✓ |

### Chain of Custody | سلسلة الحيازة

| Date | Location | Handler | Activity | التاريخ | الموقع | المتعامل | النشاط |
|------|----------|---------|----------|---------|--------|----------|--------|
| [date] | Field | [name] | Harvest | [تاريخ] | الحقل | [اسم] | حصاد |
| [date] | Farm storage | [name] | Storage | [تاريخ] | مخزن المزرعة | [اسم] | تخزين |
| [date] | Transport | [name] | Delivery | [تاريخ] | نقل | [اسم] | توصيل |
| [date] | Buyer | [name] | Receipt | [تاريخ] | المشتري | [اسم] | استلام |

### Certification | الشهادة

This document certifies the origin and production history of the
above-identified product batch.

تشهد هذه الوثيقة على منشأ وتاريخ إنتاج دفعة المنتج المذكورة أعلاه.

**Authorized Signatory | الموقع المخول:**

Name/الاسم: ________________
Position/المنصب: ________________
Signature/التوقيع: ________________
Date/التاريخ: ________________

**QR Code:** [Generated QR linking to digital record]
```

## Examples

### Example 1: Generate Field Record

**Input:**
Generate a field record for FIELD-003 with current season data.

**Output:**
[Complete Field Record document as per template, populated with actual field data]

### Example 2: Generate Season Report

**Input:**
Create an end-of-season report for FIELD-003 wheat crop 2024-2025.

**Output:**
[Complete Season Report with all metrics, inputs, financials, and lessons learned]

### Example 3: Generate Compliance Log

**Input:**
Document the imidacloprid application on FIELD-003 from January 25, 2025.

**Output:**
[Complete Pesticide Application Log entry with all regulatory fields]

### Example 4: Generate Traceability Document

**Input:**
Create traceability documentation for wheat batch from FIELD-003 harvest.

**Output:**
[Complete Traceability Document with full chain of custody]

## Automation Guidelines

### Auto-Population Rules

1. **From Sensors:** Soil moisture, temperature, weather data
2. **From Events:** Planting, irrigation, treatment, harvest dates
3. **From Calculations:** Totals, averages, variances, ROI
4. **From Reference:** Crop parameters, thresholds, standards

### Validation Checks

Before generating final document:
- [ ] All required fields populated
- [ ] Dates in chronological order
- [ ] Numeric values within valid ranges
- [ ] Cross-references verified
- [ ] Bilingual content consistent
- [ ] Compliance fields complete

### Output Formats

Support generation in:
- Markdown (primary)
- PDF (for official submission)
- JSON (for system integration)
- Excel (for data analysis)
