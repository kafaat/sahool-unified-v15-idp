# Agro Rules Service

**قواعد الزراعة الآلية - توليد المهام تلقائياً**

## Overview | نظرة عامة

Event-driven rules engine for automatic task generation based on NDVI data, weather conditions, and IoT sensor readings.

محرك قواعد يعمل بالأحداث لتوليد المهام الزراعية تلقائياً بناءً على بيانات NDVI والظروف الجوية وقراءات حساسات IoT.

## Type

**Worker Service** - No HTTP API, consumes events from NATS

## Features | الميزات

### NDVI Rules | قواعد NDVI

- Severe NDVI drop detection (urgent inspection)
- Low NDVI warnings
- Trend analysis (7-day)

### Weather Rules | قواعد الطقس

- Heat stress alerts
- Frost warnings
- Heavy rain preparation
- Strong wind alerts
- Disease risk conditions

### Combined Rules | قواعد مركبة

- Heat + NDVI decline = compound stress
- High humidity + Low NDVI = disease risk

### Irrigation Rules | قواعد الري

- Automatic adjustment recommendations
- Dry conditions increase
- Wet conditions reduction

## Rule Types | أنواع القواعد

| Rule             | Trigger        | Priority | Urgency  |
| ---------------- | -------------- | -------- | -------- |
| Severe NDVI Drop | trend ≤ -0.15  | urgent   | 6 hours  |
| Heat Wave        | temp critical  | urgent   | 2 hours  |
| Frost            | frost risk     | urgent   | 2 hours  |
| Low NDVI         | ndvi < 0.35    | medium   | 48 hours |
| Disease Risk     | humidity ≥ 80% | high     | 12 hours |

## Task Types Generated

- `inspection` - Field inspection required
- `emergency` - Emergency action needed
- `irrigation` - Irrigation adjustment
- `spray` - Pesticide/fungicide application
- `preparation` - Prepare for weather event
- `monitoring` - Ongoing monitoring

## Priority Levels

| Priority | Arabic | Response Time |
| -------- | ------ | ------------- |
| `urgent` | عاجل   | < 6 hours     |
| `high`   | مرتفع  | < 24 hours    |
| `medium` | متوسط  | < 48 hours    |
| `low`    | منخفض  | < 1 week      |

## Dependencies

- NATS (event consumption)
- field-ops service (task creation)

## Environment Variables

| Variable       | Description           | Default |
| -------------- | --------------------- | ------- |
| `NATS_URL`     | NATS server URL       | -       |
| `FIELDOPS_URL` | Field Ops service URL | -       |

## Events Consumed

- `ndvi.computed` - NDVI computation results
- `weather.alert` - Weather alerts
- `iot.reading` - Sensor readings
- `irrigation.adjustment` - Irrigation adjustments

## Events Published

- `task.created` - New task generated from rules
