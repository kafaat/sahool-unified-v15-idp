---
name: obsidian-canvas
description: Use when creating Obsidian JSON Canvas (.canvas) files for visual problem mapping in SAHOOL — farm layouts, crop rotation plans, irrigation network maps, pest spread tracking, decision flowcharts. TRIGGER when the user asks for "canvas", "visual map", "farm diagram", "rotation visualization", or "decision flowchart"; or when writing/editing any file with a .canvas extension. Emits valid JSON Canvas schema with bilingual Arabic/English labels and agricultural iconography.
---

# JSON Canvas Skill for Visual Problem Mapping

## Description

This skill enables creation of Obsidian JSON Canvas files for visual problem mapping in SAHOOL agricultural operations. Use this for farm layout visualization, crop rotation planning, irrigation network mapping, pest spread tracking, and decision flowcharts. Supports bilingual Arabic/English labels and agricultural iconography.

## Instructions

### Canvas File Structure

JSON Canvas files use the `.canvas` extension and follow this structure:

```json
{
  "nodes": [],
  "edges": []
}
```

### Node Types

#### Text Nodes (for labels and descriptions)

```json
{
  "id": "node-001",
  "type": "text",
  "x": 0,
  "y": 0,
  "width": 250,
  "height": 100,
  "text": "Field Status\nحالة الحقل",
  "color": "1"
}
```

#### File Nodes (link to farm documentation)

```json
{
  "id": "node-002",
  "type": "file",
  "file": "Fields/FIELD-003.md",
  "x": 300,
  "y": 0,
  "width": 400,
  "height": 300
}
```

#### Link Nodes (external resources)

```json
{
  "id": "node-003",
  "type": "link",
  "url": "https://sahool.app/field/FIELD-003",
  "x": 750,
  "y": 0,
  "width": 300,
  "height": 200
}
```

#### Group Nodes (for categorization)

```json
{
  "id": "group-001",
  "type": "group",
  "x": -50,
  "y": -50,
  "width": 600,
  "height": 400,
  "label": "North Farm Section | القسم الشمالي"
}
```

### Color Coding Convention for Agriculture

Use consistent colors for agricultural status:

| Color Code | Meaning | المعنى |
|------------|---------|--------|
| `"1"` (Red) | Alert/Problem | تنبيه/مشكلة |
| `"2"` (Orange) | Warning/Attention | تحذير/انتباه |
| `"3"` (Yellow) | Pending/Planning | معلق/تخطيط |
| `"4"` (Green) | Healthy/Complete | صحي/مكتمل |
| `"5"` (Cyan) | Irrigation/Water | ري/مياه |
| `"6"` (Purple) | Advisory/AI | استشارة/ذكاء |

### Edge Connections

```json
{
  "id": "edge-001",
  "fromNode": "node-001",
  "fromSide": "right",
  "toNode": "node-002",
  "toSide": "left",
  "color": "4",
  "label": "Irrigation flow | تدفق الري"
}
```

Edge sides: `"top"`, `"right"`, `"bottom"`, `"left"`

### Grid Layout Guidelines

- Use 50px grid spacing for alignment
- Standard node sizes:
  - Small label: 150x60
  - Medium card: 250x150
  - Large detail: 400x300
  - Field map: 500x400
- Group padding: 50px on all sides

### Bilingual Text Formatting

Always include both languages in node text:

```json
{
  "text": "Wheat Field 003\nحقل القمح 003\n\nStatus: Active\nالحالة: نشط"
}
```

## Examples

### Example 1: Farm Layout Canvas

```json
{
  "nodes": [
    {
      "id": "title",
      "type": "text",
      "x": 200,
      "y": -150,
      "width": 400,
      "height": 80,
      "text": "# Al-Rashid Farm Layout\n# مخطط مزرعة الراشد",
      "color": "6"
    },
    {
      "id": "group-north",
      "type": "group",
      "x": 0,
      "y": 0,
      "width": 800,
      "height": 400,
      "label": "North Section | القسم الشمالي",
      "color": "4"
    },
    {
      "id": "field-001",
      "type": "text",
      "x": 50,
      "y": 50,
      "width": 200,
      "height": 150,
      "text": "**FIELD-001**\nWheat | قمح\n\nArea: 5.2 ha\nNDVI: 0.72\nStatus: Active",
      "color": "4"
    },
    {
      "id": "field-002",
      "type": "text",
      "x": 300,
      "y": 50,
      "width": 200,
      "height": 150,
      "text": "**FIELD-002**\nBarley | شعير\n\nArea: 3.8 ha\nNDVI: 0.68\nStatus: Active",
      "color": "4"
    },
    {
      "id": "field-003",
      "type": "text",
      "x": 550,
      "y": 50,
      "width": 200,
      "height": 150,
      "text": "**FIELD-003**\nWheat | قمح\n\nArea: 8.5 ha\nNDVI: 0.45\nStatus: Alert",
      "color": "1"
    },
    {
      "id": "group-south",
      "type": "group",
      "x": 0,
      "y": 450,
      "width": 800,
      "height": 400,
      "label": "South Section | القسم الجنوبي",
      "color": "5"
    },
    {
      "id": "field-004",
      "type": "text",
      "x": 50,
      "y": 500,
      "width": 200,
      "height": 150,
      "text": "**FIELD-004**\nDate Palm | نخيل\n\nTrees: 450\nAge: 8 years\nStatus: Healthy",
      "color": "4"
    },
    {
      "id": "field-005",
      "type": "text",
      "x": 300,
      "y": 500,
      "width": 200,
      "height": 150,
      "text": "**FIELD-005**\nTomato | طماطم\n\nArea: 2.1 ha\nGreenhouse\nStatus: Planning",
      "color": "3"
    },
    {
      "id": "water-source",
      "type": "text",
      "x": 550,
      "y": 500,
      "width": 200,
      "height": 150,
      "text": "**WATER-001**\nWell | بئر\n\nCapacity: 500 m³/day\nDepth: 120m\nStatus: Active",
      "color": "5"
    },
    {
      "id": "alert-box",
      "type": "text",
      "x": 850,
      "y": 50,
      "width": 250,
      "height": 200,
      "text": "## Alerts | التنبيهات\n\n⚠️ FIELD-003:\nLow NDVI detected\nانخفاض مؤشر الغطاء\n\nAction: Investigate\nالإجراء: فحص",
      "color": "1"
    }
  ],
  "edges": [
    {
      "id": "edge-water-1",
      "fromNode": "water-source",
      "fromSide": "top",
      "toNode": "field-001",
      "toSide": "bottom",
      "color": "5",
      "label": "Main line"
    },
    {
      "id": "edge-water-2",
      "fromNode": "water-source",
      "fromSide": "top",
      "toNode": "field-002",
      "toSide": "bottom",
      "color": "5"
    },
    {
      "id": "edge-water-3",
      "fromNode": "water-source",
      "fromSide": "top",
      "toNode": "field-003",
      "toSide": "bottom",
      "color": "5"
    },
    {
      "id": "edge-alert",
      "fromNode": "field-003",
      "fromSide": "right",
      "toNode": "alert-box",
      "toSide": "left",
      "color": "1",
      "label": "Alert"
    }
  ]
}
```

### Example 2: Crop Rotation Planning Canvas

```json
{
  "nodes": [
    {
      "id": "title",
      "type": "text",
      "x": 300,
      "y": -100,
      "width": 400,
      "height": 60,
      "text": "# 3-Year Rotation Plan | خطة الدورة الزراعية",
      "color": "6"
    },
    {
      "id": "year1-group",
      "type": "group",
      "x": 0,
      "y": 0,
      "width": 300,
      "height": 500,
      "label": "Year 1 (2024) | السنة 1",
      "color": "4"
    },
    {
      "id": "y1-wheat",
      "type": "text",
      "x": 50,
      "y": 50,
      "width": 200,
      "height": 100,
      "text": "**Winter Wheat**\nقمح شتوي\n\nNov-May\nN requirement: High",
      "color": "3"
    },
    {
      "id": "y1-fallow",
      "type": "text",
      "x": 50,
      "y": 180,
      "width": 200,
      "height": 80,
      "text": "**Summer Fallow**\nراحة صيفية\n\nJun-Oct",
      "color": "2"
    },
    {
      "id": "y1-legume",
      "type": "text",
      "x": 50,
      "y": 290,
      "width": 200,
      "height": 100,
      "text": "**Cover Crop**\nمحصول تغطية\n\nClover | برسيم\nN-fixing",
      "color": "4"
    },
    {
      "id": "year2-group",
      "type": "group",
      "x": 350,
      "y": 0,
      "width": 300,
      "height": 500,
      "label": "Year 2 (2025) | السنة 2",
      "color": "4"
    },
    {
      "id": "y2-barley",
      "type": "text",
      "x": 400,
      "y": 50,
      "width": 200,
      "height": 100,
      "text": "**Winter Barley**\nشعير شتوي\n\nOct-Apr\nN requirement: Medium",
      "color": "3"
    },
    {
      "id": "y2-tomato",
      "type": "text",
      "x": 400,
      "y": 180,
      "width": 200,
      "height": 100,
      "text": "**Summer Tomato**\nطماطم صيفية\n\nMay-Sep\nIrrigation: High",
      "color": "1"
    },
    {
      "id": "y2-prep",
      "type": "text",
      "x": 400,
      "y": 310,
      "width": 200,
      "height": 80,
      "text": "**Soil Prep**\nتجهيز التربة\n\nOct-Nov",
      "color": "2"
    },
    {
      "id": "year3-group",
      "type": "group",
      "x": 700,
      "y": 0,
      "width": 300,
      "height": 500,
      "label": "Year 3 (2026) | السنة 3",
      "color": "4"
    },
    {
      "id": "y3-legume",
      "type": "text",
      "x": 750,
      "y": 50,
      "width": 200,
      "height": 100,
      "text": "**Faba Bean**\nفول\n\nNov-Mar\nN-fixing crop",
      "color": "4"
    },
    {
      "id": "y3-cucumber",
      "type": "text",
      "x": 750,
      "y": 180,
      "width": 200,
      "height": 100,
      "text": "**Summer Cucumber**\nخيار صيفي\n\nApr-Aug\nGreenhouse",
      "color": "4"
    },
    {
      "id": "y3-wheat",
      "type": "text",
      "x": 750,
      "y": 310,
      "width": 200,
      "height": 100,
      "text": "**Winter Wheat**\nقمح شتوي\n\nNov-May\nCycle restart",
      "color": "3"
    },
    {
      "id": "benefits",
      "type": "text",
      "x": 350,
      "y": 550,
      "width": 300,
      "height": 150,
      "text": "## Benefits | الفوائد\n\n✓ Soil health | صحة التربة\n✓ Pest break | كسر دورة الآفات\n✓ N management | إدارة النيتروجين\n✓ Risk reduction | تقليل المخاطر",
      "color": "6"
    }
  ],
  "edges": [
    {
      "id": "e-y1-y2",
      "fromNode": "y1-legume",
      "fromSide": "right",
      "toNode": "y2-barley",
      "toSide": "left",
      "color": "4",
      "label": "N transfer"
    },
    {
      "id": "e-y2-y3",
      "fromNode": "y2-prep",
      "fromSide": "right",
      "toNode": "y3-legume",
      "toSide": "left",
      "color": "4"
    },
    {
      "id": "e-cycle",
      "fromNode": "y3-wheat",
      "fromSide": "bottom",
      "toNode": "benefits",
      "toSide": "right",
      "color": "6",
      "label": "Cycle complete"
    }
  ]
}
```

### Example 3: Pest Spread Tracking Canvas

```json
{
  "nodes": [
    {
      "id": "title",
      "type": "text",
      "x": 250,
      "y": -120,
      "width": 500,
      "height": 80,
      "text": "# Aphid Infestation Spread Map\n# خريطة انتشار إصابة المن",
      "color": "1"
    },
    {
      "id": "legend",
      "type": "text",
      "x": 850,
      "y": 0,
      "width": 200,
      "height": 200,
      "text": "## Legend | الدليل\n\n🔴 Severe | شديد\n🟠 Moderate | متوسط\n🟡 Light | خفيف\n🟢 Clear | نظيف\n\n→ Spread direction\nاتجاه الانتشار",
      "color": "6"
    },
    {
      "id": "origin",
      "type": "text",
      "x": 100,
      "y": 100,
      "width": 200,
      "height": 150,
      "text": "**FIELD-007**\n\nInfestation Origin\nمصدر الإصابة\n\nDetected: Jan 5\nSeverity: Severe\nالشدة: شديدة",
      "color": "1"
    },
    {
      "id": "spread-1",
      "type": "text",
      "x": 350,
      "y": 50,
      "width": 200,
      "height": 120,
      "text": "**FIELD-003**\n\nSecondary spread\nانتشار ثانوي\n\nDetected: Jan 8\nSeverity: Moderate",
      "color": "2"
    },
    {
      "id": "spread-2",
      "type": "text",
      "x": 350,
      "y": 200,
      "width": 200,
      "height": 120,
      "text": "**FIELD-005**\n\nSecondary spread\nانتشار ثانوي\n\nDetected: Jan 9\nSeverity: Light",
      "color": "3"
    },
    {
      "id": "at-risk",
      "type": "text",
      "x": 600,
      "y": 100,
      "width": 200,
      "height": 150,
      "text": "**FIELD-001**\n\n⚠️ AT RISK\nمعرض للخطر\n\nDownwind location\nموقع مع اتجاه الريح\n\nAction: Monitor daily",
      "color": "3"
    },
    {
      "id": "clear",
      "type": "text",
      "x": 100,
      "y": 300,
      "width": 200,
      "height": 100,
      "text": "**FIELD-002**\n\n✓ Clear\nنظيف\n\nUpwind, isolated\nمعزول",
      "color": "4"
    },
    {
      "id": "action-box",
      "type": "text",
      "x": 350,
      "y": 380,
      "width": 450,
      "height": 150,
      "text": "## Recommended Actions | الإجراءات الموصى بها\n\n1. Spray FIELD-007 immediately | رش الحقل 007 فوراً\n2. Preventive spray FIELD-003, 005 | رش وقائي للحقول 003، 005\n3. Daily monitoring FIELD-001 | مراقبة يومية للحقل 001\n4. Document wind patterns | توثيق أنماط الرياح",
      "color": "6"
    },
    {
      "id": "wind",
      "type": "text",
      "x": 600,
      "y": 300,
      "width": 150,
      "height": 60,
      "text": "Wind: NW→SE\nالرياح: شمال غرب",
      "color": "5"
    }
  ],
  "edges": [
    {
      "id": "spread-e1",
      "fromNode": "origin",
      "fromSide": "right",
      "toNode": "spread-1",
      "toSide": "left",
      "color": "1",
      "label": "Jan 8"
    },
    {
      "id": "spread-e2",
      "fromNode": "origin",
      "fromSide": "right",
      "toNode": "spread-2",
      "toSide": "left",
      "color": "2",
      "label": "Jan 9"
    },
    {
      "id": "risk-e1",
      "fromNode": "spread-1",
      "fromSide": "right",
      "toNode": "at-risk",
      "toSide": "left",
      "color": "3",
      "label": "Risk path"
    },
    {
      "id": "wind-e",
      "fromNode": "wind",
      "fromSide": "top",
      "toNode": "at-risk",
      "toSide": "bottom",
      "color": "5",
      "label": "Wind vector"
    }
  ]
}
```

### Example 4: Decision Flowchart Canvas

```json
{
  "nodes": [
    {
      "id": "title",
      "type": "text",
      "x": 200,
      "y": -100,
      "width": 400,
      "height": 60,
      "text": "# Irrigation Decision Flow | مخطط قرار الري",
      "color": "6"
    },
    {
      "id": "start",
      "type": "text",
      "x": 300,
      "y": 0,
      "width": 200,
      "height": 60,
      "text": "**START**\nCheck soil moisture\nفحص رطوبة التربة",
      "color": "6"
    },
    {
      "id": "check-moisture",
      "type": "text",
      "x": 300,
      "y": 100,
      "width": 200,
      "height": 80,
      "text": "Moisture < 40%?\nالرطوبة < 40%؟",
      "color": "3"
    },
    {
      "id": "check-rain",
      "type": "text",
      "x": 300,
      "y": 220,
      "width": 200,
      "height": 80,
      "text": "Rain forecast\n48hrs?\nتوقع مطر؟",
      "color": "5"
    },
    {
      "id": "check-et",
      "type": "text",
      "x": 300,
      "y": 340,
      "width": 200,
      "height": 80,
      "text": "ET₀ > 5mm/day?\nالتبخر > 5 مم؟",
      "color": "5"
    },
    {
      "id": "irrigate-full",
      "type": "text",
      "x": 550,
      "y": 340,
      "width": 180,
      "height": 80,
      "text": "**IRRIGATE**\nFull dose\nري كامل",
      "color": "4"
    },
    {
      "id": "irrigate-half",
      "type": "text",
      "x": 50,
      "y": 340,
      "width": 180,
      "height": 80,
      "text": "**IRRIGATE**\n50% dose\nنصف الكمية",
      "color": "4"
    },
    {
      "id": "wait",
      "type": "text",
      "x": 50,
      "y": 220,
      "width": 180,
      "height": 80,
      "text": "**WAIT**\nRe-check 24hrs\nإعادة الفحص",
      "color": "2"
    },
    {
      "id": "no-action",
      "type": "text",
      "x": 550,
      "y": 100,
      "width": 180,
      "height": 80,
      "text": "**NO ACTION**\nMoisture OK\nالرطوبة كافية",
      "color": "4"
    }
  ],
  "edges": [
    {
      "id": "e1",
      "fromNode": "start",
      "fromSide": "bottom",
      "toNode": "check-moisture",
      "toSide": "top",
      "color": "6"
    },
    {
      "id": "e2-yes",
      "fromNode": "check-moisture",
      "fromSide": "bottom",
      "toNode": "check-rain",
      "toSide": "top",
      "color": "4",
      "label": "Yes | نعم"
    },
    {
      "id": "e2-no",
      "fromNode": "check-moisture",
      "fromSide": "right",
      "toNode": "no-action",
      "toSide": "left",
      "color": "4",
      "label": "No | لا"
    },
    {
      "id": "e3-yes",
      "fromNode": "check-rain",
      "fromSide": "left",
      "toNode": "wait",
      "toSide": "right",
      "color": "5",
      "label": "Yes | نعم"
    },
    {
      "id": "e3-no",
      "fromNode": "check-rain",
      "fromSide": "bottom",
      "toNode": "check-et",
      "toSide": "top",
      "color": "5",
      "label": "No | لا"
    },
    {
      "id": "e4-high",
      "fromNode": "check-et",
      "fromSide": "right",
      "toNode": "irrigate-full",
      "toSide": "left",
      "color": "4",
      "label": "High | عالي"
    },
    {
      "id": "e4-low",
      "fromNode": "check-et",
      "fromSide": "left",
      "toNode": "irrigate-half",
      "toSide": "right",
      "color": "4",
      "label": "Low | منخفض"
    }
  ]
}
```
