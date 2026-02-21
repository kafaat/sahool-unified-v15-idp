# SAHOOL Inventory Service | خدمة إدارة المخزون

> Agricultural inventory management with advanced analytics and forecasting

[![Version](https://img.shields.io/badge/version-16.0.0-blue.svg)](package.json)
[![Python](https://img.shields.io/badge/python-3.11-green.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128.5-red.svg)](https://fastapi.tiangolo.com)

## Overview | نظرة عامة

The Inventory Service provides comprehensive agricultural inventory management with advanced analytics, forecasting, and real-time alerts. It supports multi-tenant operations with full warehouse management capabilities.

خدمة إدارة المخزون توفر إدارة شاملة للمخزون الزراعي مع تحليلات متقدمة والتنبؤ والتنبيهات الفورية. تدعم العمليات متعددة المستأجرين مع إمكانيات كاملة لإدارة المستودعات.

## Features

### Core Functionality

- **Inventory Management**: Multi-tenant inventory tracking with categories, warehouses, and suppliers
- **Stock Movements**: Receipt, issue, transfer, adjustment, return, write-off tracking
- **Transaction Recording**: Purchase, sale, use, waste, and return transactions

### Analytics & Forecasting

- **Consumption Forecasting**: Moving average-based forecasting with seasonal adjustment
- **Inventory Valuation**: FIFO and weighted average cost valuation
- **ABC/Pareto Analysis**: Classify items by value contribution
- **Turnover Analysis**: Calculate inventory turnover ratios and days of inventory
- **Slow-Moving & Dead Stock**: Identify items with low turnover or near expiry
- **Seasonal Patterns**: Analyze seasonal consumption trends
- **Cost Analysis**: Track input costs by field, crop, and category
- **Waste Analysis**: Monitor write-offs, expired items, and losses
- **Reorder Recommendations**: Smart reorder suggestions based on consumption and lead times

## Health Endpoints | نقاط فحص الصحة

All health endpoints support Kubernetes probes and container health checks.

### GET /healthz - Liveness Probe

**Purpose**: Check if service is running (Kubernetes livenessProbe)

```json
{
    "status": "healthy",
    "service": "inventory-service",
    "version": "16.0.0"
}
```

### GET /readyz - Readiness Probe

**Purpose**: Check if service is ready to accept requests (Kubernetes readinessProbe)

```json
{
    "status": "ready",
    "service": "inventory-service",
    "database": true
}
```

**Details**:
- Returns `ready` only if database is accessible
- Returns `not_ready` if database check fails
- Use for load balancer health checks

### GET /health - Full Health Check

**Purpose**: Comprehensive health status with dependency details

```json
{
    "status": "healthy",
    "service": "inventory-service",
    "version": "16.0.0",
    "dependencies": {
        "postgres": "connected"
    }
}
```

**Details**:
- Includes database connection verification
- Full dependency status reporting
- Use for operational dashboards

### Kubernetes Deployment Example

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8116
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /readyz
    port: 8116
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

---

## API Endpoints | نقاط النهاية

### Category Management
```http
POST /v1/categories
```
Create new item category

### Analytics Endpoints

| Endpoint | Method | Purpose | الوصف |
|----------|--------|---------|-------|
| `/v1/analytics/forecast/{item_id}` | GET | Consumption forecast | توقع الاستهلاك |
| `/v1/analytics/forecasts` | GET | All forecasts | كل التوقعات |
| `/v1/analytics/reorder-recommendations` | GET | Reorder suggestions | توصيات إعادة الطلب |
| `/v1/analytics/valuation` | GET | Inventory valuation | تقييم المخزون |
| `/v1/analytics/turnover` | GET | Turnover analysis | تحليل دوران المخزون |
| `/v1/analytics/slow-moving` | GET | Slow moving items | العناصر بطيئة الحركة |
| `/v1/analytics/dead-stock` | GET | Dead stock items | المخزون الراكد |
| `/v1/analytics/abc-analysis` | GET | ABC/Pareto analysis | تحليل ABC |
| `/v1/analytics/seasonal-patterns/{item_id}` | GET | Seasonal patterns | الأنماط الموسمية |
| `/v1/analytics/cost-analysis` | GET | Cost analysis | تحليل التكاليف |
| `/v1/analytics/waste-analysis` | GET | Waste analysis | تحليل الهدر |
| `/v1/analytics/dashboard` | GET | Dashboard summary | ملخص لوحة التحكم |

See full endpoint documentation at `/docs`.

## Environment Variables

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/sahool_inventory
PORT=8116
SQL_ECHO=false
```

## Port

Default: **8116**
