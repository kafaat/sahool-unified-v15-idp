# ⚠️ DEPRECATED - Use field-management-service instead

This service has been deprecated and merged into `field-management-service`.
Please update your references to use `field-management-service` on port 3000.

---


# Field Operations Service

**خدمة العمليات الميدانية - إدارة الحقول والعمليات الزراعية**

## Overview | نظرة عامة

Core agricultural field management service handling field operations, task management, and activity logging. Acts as the central hub for field-related business logic.

خدمة إدارة الحقول الزراعية الأساسية التي تتعامل مع عمليات الحقول وإدارة المهام وتسجيل النشاطات. تعمل كمركز رئيسي لمنطق العمل المتعلق بالحقول.

## Port

```
8080
```

## Features | الميزات

### Field Management | إدارة الحقول
- Field CRUD operations
- Crop assignment
- Growth stage tracking
- Area calculations

### Task Management | إدارة المهام
- Task creation and assignment
- Priority management
- Status tracking
- Due date monitoring

### Activity Logging | سجل النشاطات
- Operation history
- User activity tracking
- Audit trail

### Event Integration | تكامل الأحداث
- NATS event publishing
- Cross-service communication
- Real-time notifications

## API Endpoints

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Health check |
| GET | `/readyz` | Readiness check |

### Fields
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/fields` | List fields |
| POST | `/api/v1/fields` | Create field |
| GET | `/api/v1/fields/{id}` | Get field |
| PUT | `/api/v1/fields/{id}` | Update field |
| DELETE | `/api/v1/fields/{id}` | Delete field |

### Tasks
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/fields/{field_id}/tasks` | List field tasks |
| POST | `/api/v1/fields/{field_id}/tasks` | Create task |
| GET | `/api/v1/tasks/{id}` | Get task |
| PUT | `/api/v1/tasks/{id}` | Update task |
| POST | `/api/v1/tasks/{id}/complete` | Complete task |

### Activities
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/fields/{field_id}/activities` | List activities |
| POST | `/api/v1/fields/{field_id}/activities` | Log activity |

## Usage Examples | أمثلة الاستخدام

### Create Field
```bash
curl -X POST http://localhost:8080/api/v1/fields \
  -H "Content-Type: application/json" \
  -d '{
    "name": "الحقل الشمالي",
    "name_en": "North Field",
    "tenant_id": "tenant_001",
    "crop_type": "wheat",
    "area_hectares": 15.5,
    "irrigation_type": "drip"
  }'
```

### Create Task
```bash
curl -X POST http://localhost:8080/api/v1/fields/field_001/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "فحص صحة المحصول",
    "title_en": "Crop Health Inspection",
    "priority": "high",
    "type": "inspection",
    "due_date": "2025-12-25T10:00:00Z",
    "assigned_to": "user_001"
  }'
```

### Log Activity
```bash
curl -X POST http://localhost:8080/api/v1/fields/field_001/activities \
  -H "Content-Type: application/json" \
  -d '{
    "type": "irrigation",
    "description": "تم الري لمدة ساعتين",
    "duration_minutes": 120,
    "user_id": "user_001"
  }'
```

## Task Types

| Type | Arabic | Description |
|------|--------|-------------|
| `inspection` | فحص | Field inspection |
| `irrigation` | ري | Irrigation task |
| `fertilization` | تسميد | Fertilizer application |
| `spray` | رش | Pesticide/herbicide |
| `harvest` | حصاد | Harvesting |
| `maintenance` | صيانة | Equipment maintenance |

## Priority Levels

| Priority | Arabic | Description |
|----------|--------|-------------|
| `urgent` | عاجل | Immediate action |
| `high` | مرتفع | Within 24 hours |
| `medium` | متوسط | Within 48 hours |
| `low` | منخفض | When convenient |

## Dependencies

- FastAPI
- asyncpg (PostgreSQL)
- NATS

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | `8080` |
| `DATABASE_URL` | PostgreSQL connection | - |
| `NATS_URL` | NATS server URL | - |

## Events Published

- `field.created` - New field created
- `field.updated` - Field modified
- `task.created` - New task created
- `task.completed` - Task marked complete
- `activity.logged` - Activity recorded
