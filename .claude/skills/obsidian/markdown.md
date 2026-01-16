# Obsidian Markdown Skill for Farm Documentation

## Description

This skill enables generation of Obsidian-compatible Markdown documentation for SAHOOL agricultural operations. It supports Arabic/English bilingual content, farm field documentation, crop records, irrigation logs, and agricultural knowledge bases with proper Obsidian features like wikilinks, callouts, and frontmatter.

## Instructions

### Frontmatter Structure

Always include YAML frontmatter with agricultural metadata:

```yaml
---
title: Field Documentation Title
title_ar: عنوان توثيق الحقل
farm_id: FARM-XXX
field_id: FIELD-XXX
crop_type: wheat | barley | date_palm | tomato | cucumber
season: winter | summer | spring | fall
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - sahool
  - field-ops
  - crop-type
status: active | harvested | fallow | planned
---
```

### Wikilinks for Farm Knowledge Graph

Use Obsidian wikilinks to connect farm documentation:

- `[[Fields/FIELD-001]]` - Link to field records
- `[[Crops/Wheat-2024]]` - Link to crop documentation
- `[[Irrigation/Schedule-Winter-2024]]` - Link to irrigation plans
- `[[Advisory/Pest-Control-Wheat]]` - Link to advisory content
- `[[Equipment/Tractor-001]]` - Link to equipment records

### Callout Types for Agricultural Alerts

Use callouts for important farm information:

```markdown
> [!warning] تحذير - Pest Alert
> Aphid infestation detected in Field-003
> مطلوب رش مبيد حشري خلال 48 ساعة

> [!tip] نصيحة - Irrigation Recommendation
> Reduce irrigation by 20% due to expected rainfall
> تقليل الري بنسبة 20% بسبب هطول الأمطار المتوقع

> [!info] معلومات - Crop Stage
> Wheat entering flowering stage (Zadoks 60)
> القمح يدخل مرحلة الإزهار

> [!success] نجاح - Harvest Complete
> Field-002 wheat harvest completed: 4.2 tons/hectare
> اكتمل حصاد القمح: 4.2 طن/هكتار
```

### Bilingual Content Structure

Structure bilingual content with clear separation:

```markdown
## Field Overview | نظرة عامة على الحقل

**English:** This field covers 5 hectares of irrigated farmland suitable for winter wheat cultivation.

**العربية:** يغطي هذا الحقل 5 هكتارات من الأراضي الزراعية المروية المناسبة لزراعة القمح الشتوي.
```

### Tables for Agricultural Data

Use Markdown tables for structured farm data:

```markdown
| Metric | Value | الوحدة | القيمة |
|--------|-------|--------|--------|
| Area | 5.2 ha | المساحة | 5.2 هكتار |
| Soil pH | 7.2 | حموضة التربة | 7.2 |
| NDVI | 0.72 | مؤشر الغطاء النباتي | 0.72 |
| Irrigation | Drip | نوع الري | تنقيط |
```

### Task Lists for Farm Operations

Use task lists for operation checklists:

```markdown
## Pre-Planting Checklist | قائمة ما قبل الزراعة

- [x] Soil analysis completed | تحليل التربة مكتمل
- [x] Irrigation system tested | اختبار نظام الري
- [ ] Seeds ordered | طلب البذور
- [ ] Fertilizer prepared | تجهيز السماد
- [ ] Field boundaries marked | تحديد حدود الحقل
```

### Embedded Queries for Dynamic Content

Use Obsidian dataview-style queries:

```markdown
## Active Fields | الحقول النشطة

```dataview
TABLE crop_type, area, status
FROM "Fields"
WHERE status = "active"
SORT area DESC
```
```

### Tags Convention

Use hierarchical tags for organization:

- `#sahool/field` - Field-related
- `#sahool/crop/wheat` - Crop-specific
- `#sahool/irrigation` - Irrigation records
- `#sahool/advisory` - Advisory content
- `#sahool/harvest` - Harvest records
- `#sahool/equipment` - Equipment maintenance

## Examples

### Example 1: Field Documentation

```markdown
---
title: North Wheat Field Documentation
title_ar: توثيق حقل القمح الشمالي
farm_id: FARM-001
field_id: FIELD-003
crop_type: wheat
season: winter
created: 2024-11-15
updated: 2025-01-10
tags:
  - sahool/field
  - sahool/crop/wheat
  - winter-2024
status: active
---

# North Wheat Field | حقل القمح الشمالي

## Overview | نظرة عامة

This field is part of [[Farms/Al-Rashid-Farm]] and currently cultivates winter wheat variety **Sakha 95**.

هذا الحقل جزء من [[Farms/Al-Rashid-Farm]] ويزرع حالياً قمح شتوي صنف **سخا 95**.

## Field Specifications | مواصفات الحقل

| Parameter | Value | المعلمة | القيمة |
|-----------|-------|---------|--------|
| Total Area | 8.5 ha | المساحة الكلية | 8.5 هكتار |
| Soil Type | Clay loam | نوع التربة | طينية طميية |
| Irrigation | Center pivot | نظام الري | محوري |
| Planting Date | Nov 15, 2024 | تاريخ الزراعة | 15 نوفمبر 2024 |

## Current Status | الحالة الحالية

> [!info] Growth Stage | مرحلة النمو
> Tillering stage (Zadoks 25) - Good development
> مرحلة التفريع - نمو جيد

### NDVI History | تاريخ مؤشر الغطاء النباتي

- **2024-12-01**: 0.45 (Emergence)
- **2024-12-15**: 0.58 (Early tillering)
- **2025-01-10**: 0.72 (Full tillering)

## Related Records | السجلات المرتبطة

- [[Irrigation/FIELD-003-Schedule]]
- [[Advisory/Wheat-Fertilizer-Plan-2024]]
- [[Harvest/FIELD-003-Forecast]]

## Operations Log | سجل العمليات

- [x] 2024-11-15: Planting completed | اكتملت الزراعة
- [x] 2024-11-20: First irrigation | الرية الأولى
- [x] 2024-12-10: Nitrogen application (46 kg/ha) | إضافة النيتروجين
- [ ] 2025-01-20: Second nitrogen split | الدفعة الثانية من النيتروجين
- [ ] 2025-02-15: Fungicide application | رش مبيد فطري

#sahool/field #sahool/crop/wheat #winter-2024 #active
```

### Example 2: Irrigation Schedule Document

```markdown
---
title: Winter Irrigation Schedule - Field 003
title_ar: جدول الري الشتوي - الحقل 003
farm_id: FARM-001
field_id: FIELD-003
created: 2024-11-01
updated: 2025-01-05
tags:
  - sahool/irrigation
  - winter-2024
  - wheat
---

# Irrigation Schedule | جدول الري

## Target Field | الحقل المستهدف

Connected to: [[Fields/FIELD-003-North-Wheat]]

## Weekly Schedule | الجدول الأسبوعي

> [!tip] Water Management Tip | نصيحة إدارة المياه
> Adjust irrigation based on ET₀ readings from [[Weather/Station-001]]
> اضبط الري بناءً على قراءات التبخر من محطة الطقس

| Week | Volume (m³/ha) | الأسبوع | الكمية |
|------|----------------|---------|--------|
| Nov 15-21 | 450 | نوفمبر 15-21 | 450 م³/هكتار |
| Nov 22-28 | 400 | نوفمبر 22-28 | 400 م³/هكتار |
| Dec 1-7 | 350 | ديسمبر 1-7 | 350 م³/هكتار |
| Dec 8-14 | 350 | ديسمبر 8-14 | 350 م³/هكتار |

## Sensors | أجهزة الاستشعار

- Soil moisture sensor: [[Sensors/SMS-003-A]]
- Flow meter: [[Sensors/FM-003]]

#sahool/irrigation #water-management
```

### Example 3: Pest Advisory Document

```markdown
---
title: Aphid Control Advisory - Wheat
title_ar: إرشادات مكافحة المن - القمح
crop_type: wheat
pest_type: aphid
severity: moderate
created: 2025-01-08
tags:
  - sahool/advisory
  - pest-control
  - wheat
---

# Aphid Control Advisory | إرشادات مكافحة المن

> [!warning] Alert Level: Moderate | مستوى التنبيه: متوسط
> Action required within 72 hours
> مطلوب اتخاذ إجراء خلال 72 ساعة

## Affected Fields | الحقول المتأثرة

- [[Fields/FIELD-003]] - Moderate infestation | إصابة متوسطة
- [[Fields/FIELD-007]] - Light infestation | إصابة خفيفة

## Identification | التعريف

**English:** Bird cherry-oat aphid (Rhopalosiphum padi) detected on lower leaves. Colony size: 15-25 aphids per tiller.

**العربية:** تم اكتشاف من الشوفان على الأوراق السفلية. حجم المستعمرة: 15-25 حشرة لكل فرع.

## Recommended Action | الإجراء الموصى به

### Chemical Control | المكافحة الكيميائية

| Product | Rate | المنتج | المعدل |
|---------|------|--------|--------|
| Imidacloprid 20% | 100 ml/ha | إيميداكلوبريد | 100 مل/هكتار |
| Lambda-cyhalothrin | 200 ml/ha | لامبدا سيهالوثرين | 200 مل/هكتار |

### Application Timing | توقيت التطبيق

- [x] Scout fields for confirmation | مسح الحقول للتأكيد
- [ ] Apply early morning (before 9 AM) | التطبيق صباحاً قبل 9
- [ ] Re-scout after 7 days | إعادة المسح بعد 7 أيام

## Economic Threshold | العتبة الاقتصادية

> [!info] Decision Guide | دليل القرار
> Spray when >25 aphids/tiller before heading stage
> الرش عند تجاوز 25 حشرة/فرع قبل مرحلة السنبلة

See also: [[Advisory/Integrated-Pest-Management]]

#sahool/advisory #pest-control #aphid #wheat
```
