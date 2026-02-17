# Digital Twin Engine - محرك التوأم الرقمي

## نظرة عامة | Overview

خدمة محاكاة التوأم الرقمي المتقدمة لمحاكاة حالة الحقل الزراعي وتحسين السيناريوهات متعددة الأهداف باستخدام تصفية كالمان وتقديرات الحالة بدقة تتجاوز 92%.

Advanced digital twin simulation service for agricultural field state modeling with multi-objective scenario optimization using Kalman filtering and state estimation with >92% accuracy. Includes specialized Yemen crop varieties, climate data, and salinity-aware field modeling.

**Port:** 8253
**Version:** 16.0.0
**Framework:** FastAPI 0.128.5
**Python:** >= 3.11

---

## الميزات | Features

### محاكاة الحقل | Field Simulation

| الميزة | Feature | الوصف |
|--------|---------|-------|
| محاكاة الحالة | State Simulation | تقدير حالة الحقل الزراعي الديناميكية |
| تصفية كالمان | Kalman Filtering | تقدير الحالة بدقة >92% |
| سيناريوهات الري | Irrigation Scenarios | مقارنة سيناريوهات الري متعددة |
| نمذجة الملوحة | Salinity Modeling | إدارة ملوحة التربة والمياه |
| بيانات اليمن | Yemen-Specific Data | محاصيل وبيانات مناخية يمنية خاصة |

### التحسين متعدد الأهداف | Multi-Objective Optimization

| الهدف | Objective | الوصف |
|------|-----------|-------|
| تقليل المياه | MINIMIZE_WATER | تقليل استهلاك المياه |
| زيادة الإنتاج | MAXIMIZE_YIELD | تعظيم إنتاجية المحصول |
| تقليل التكاليف | MINIMIZE_COST | تقليل التكاليف التشغيلية |
| الأثر البيئي | MINIMIZE_ENVIRONMENTAL_IMPACT | تقليل الأثر البيئي السلبي |
| متوازن | BALANCED | تحسين متوازن لجميع الأهداف |

### خوارزميات التحسين | Optimization Algorithms

- **Genetic Algorithm (GA)**: للبحث العام عن الحلول المثلى
- **Particle Swarm Optimization (PSO)**: للبحث السريع عن الأفضليات المحلية
- **Weighted Sum Scalarization**: لتحويل متعدد الأهداف إلى أحادي الهدف
- **Pareto Front Analysis**: لتحديد الحلول الفعالة غير المهيمن عليها

### معايرة الحالة | State Estimation

| المعامل | Parameter | الوحدة |
|---------|-----------|-------|
| رطوبة التربة | Soil Moisture | % |
| درجة الحرارة | Temperature | °C |
| درجة ملوحة التربة | Soil Salinity (EC) | dS/m |
| النيتروجين المتاح | Available Nitrogen | ppm |
| الفسفور المتاح | Available Phosphorus | ppm |
| المستويات الأيونية | Ion Concentrations | mmol/L |

---

## API Endpoints

### Health Check | فحص الصحة

```http
GET /healthz
GET /readyz
GET /health

Response:
{
    "status": "ok",
    "service": "digital-twin-engine",
    "version": "16.0.0",
    "database": true,
    "nats": true
}
```

### معلومات القدرات | Service Information

```http
GET /api/v1/digital-twin/info

Response:
{
    "service": "digital-twin-engine",
    "version": "16.0.0",
    "capabilities": {
        "field_simulation": true,
        "state_estimation": true,
        "scenario_comparison": true,
        "multi_objective_optimization": true,
        "kalman_filtering": true,
        "yemen_models": true,
        "salinity_management": true
    },
    "optimization_objectives": [
        "MINIMIZE_WATER",
        "MAXIMIZE_YIELD",
        "MINIMIZE_COST",
        "MINIMIZE_ENVIRONMENTAL_IMPACT",
        "BALANCED"
    ],
    "supported_crops": [
        "wheat",
        "barley",
        "date_palm",
        "sorghum",
        "millet",
        "tomato",
        "cucumber"
    ],
    "max_simulation_days": 365,
    "state_estimation_accuracy": ">92%"
}
```

### محاكاة حالة الحقل | Field State Simulation

```http
POST /api/v1/digital-twin/simulate

Request:
{
    "field_id": "FIELD-003",
    "crop_type": "wheat",
    "crop_variety": "sakha_95",
    "simulation_start_date": "2025-01-15",
    "simulation_days": 120,
    "initial_state": {
        "soil_moisture_percent": 65,
        "soil_temperature_celsius": 18,
        "soil_salinity_ec": 0.8,
        "available_nitrogen_ppm": 22,
        "available_phosphorus_ppm": 12,
        "plant_height_cm": 5,
        "leaf_area_index": 0.1
    },
    "management_practices": {
        "irrigation_method": "drip",
        "irrigation_schedule": [
            {
                "day": 20,
                "amount_mm": 25,
                "method": "drip"
            },
            {
                "day": 35,
                "amount_mm": 25,
                "method": "drip"
            }
        ],
        "fertilizer_applications": [
            {
                "day": 15,
                "type": "urea",
                "rate_kg_ha": 46,
                "method": "broadcast"
            }
        ],
        "pest_management": [
            {
                "day": 45,
                "treatment": "spray",
                "product": "insecticide_x",
                "coverage_percent": 95
            }
        ]
    },
    "weather_scenario": "historical",
    "include_daily_outputs": true
}

Response:
{
    "simulation_id": "sim_20250116_001",
    "field_id": "FIELD-003",
    "crop_type": "wheat",
    "status": "completed",
    "simulation_period": {
        "start_date": "2025-01-15",
        "end_date": "2025-05-15",
        "total_days": 120
    },
    "final_state": {
        "soil_moisture_percent": 42,
        "soil_temperature_celsius": 28,
        "soil_salinity_ec": 1.2,
        "available_nitrogen_ppm": 8,
        "plant_height_cm": 85,
        "leaf_area_index": 4.5,
        "biomass_kg_ha": 8200,
        "predicted_yield_kg_ha": 3800
    },
    "summary_metrics": {
        "total_water_used_mm": 275,
        "total_nitrogen_used_kg_ha": 120,
        "total_cost_sar_ha": 2850,
        "predicted_yield_kg_ha": 3800,
        "predicted_yield_increase_percent": 15.5,
        "environmental_impact_score": 72.0
    },
    "daily_outputs": [
        {
            "day": 1,
            "date": "2025-01-15",
            "growth_stage": "V0",
            "soil_moisture": 65,
            "temperature": 18.5,
            "plant_height": 5.2,
            "lai": 0.12,
            "biomass": 45,
            "water_stress_index": 0.0
        },
        {
            "day": 120,
            "date": "2025-05-15",
            "growth_stage": "R6",
            "soil_moisture": 42,
            "temperature": 28.2,
            "plant_height": 85.5,
            "lai": 4.5,
            "biomass": 8200,
            "water_stress_index": 0.15
        }
    ],
    "created_at": "2025-01-16T10:30:00Z",
    "completed_at": "2025-01-16T10:31:45Z"
}
```

### مقارنة السيناريوهات | Scenario Comparison

```http
POST /api/v1/digital-twin/scenarios

Request:
{
    "field_id": "FIELD-003",
    "crop_type": "wheat",
    "crop_variety": "sakha_95",
    "simulation_start_date": "2025-01-15",
    "simulation_days": 120,
    "initial_state": {
        "soil_moisture_percent": 65,
        "soil_temperature_celsius": 18,
        "soil_salinity_ec": 0.8,
        "available_nitrogen_ppm": 22
    },
    "scenarios": [
        {
            "name": "current_practice",
            "name_ar": "الممارسة الحالية",
            "description": "سيناريو الممارسات الحالية للمزارع",
            "irrigation_schedule": [
                {"day": 20, "amount_mm": 25},
                {"day": 35, "amount_mm": 25},
                {"day": 55, "amount_mm": 25},
                {"day": 75, "amount_mm": 20}
            ],
            "fertilizer_applications": [
                {"day": 15, "type": "urea", "rate_kg_ha": 50}
            ]
        },
        {
            "name": "optimized_water",
            "name_ar": "تحسين استهلاك المياه",
            "description": "سيناريو تحسين كفاءة استخدام المياه",
            "irrigation_schedule": [
                {"day": 22, "amount_mm": 20},
                {"day": 38, "amount_mm": 22},
                {"day": 58, "amount_mm": 20},
                {"day": 80, "amount_mm": 18}
            ],
            "fertilizer_applications": [
                {"day": 15, "type": "urea", "rate_kg_ha": 46}
            ]
        },
        {
            "name": "high_yield",
            "name_ar": "تحسين الإنتاجية",
            "description": "سيناريو تعظيم إنتاجية المحصول",
            "irrigation_schedule": [
                {"day": 20, "amount_mm": 30},
                {"day": 35, "amount_mm": 30},
                {"day": 55, "amount_mm": 28},
                {"day": 75, "amount_mm": 25}
            ],
            "fertilizer_applications": [
                {"day": 15, "type": "urea", "rate_kg_ha": 60}
            ]
        }
    ]
}

Response:
{
    "comparison_id": "comp_20250116_001",
    "field_id": "FIELD-003",
    "crop_type": "wheat",
    "simulation_period": "120 days",
    "scenarios": [
        {
            "scenario_name": "current_practice",
            "scenario_name_ar": "الممارسة الحالية",
            "final_state": {
                "soil_moisture_percent": 42,
                "plant_height_cm": 85,
                "biomass_kg_ha": 8200
            },
            "metrics": {
                "total_water_mm": 295,
                "total_nitrogen_kg_ha": 125,
                "total_cost_sar_ha": 2950,
                "predicted_yield_kg_ha": 3650,
                "environmental_impact_score": 68
            },
            "water_efficiency_index": 0.78,
            "cost_effectiveness_ratio": 1.24,
            "sustainability_score": 68
        },
        {
            "scenario_name": "optimized_water",
            "scenario_name_ar": "تحسين استهلاك المياه",
            "final_state": {
                "soil_moisture_percent": 38,
                "plant_height_cm": 82,
                "biomass_kg_ha": 7850
            },
            "metrics": {
                "total_water_mm": 260,
                "total_nitrogen_kg_ha": 115,
                "total_cost_sar_ha": 2750,
                "predicted_yield_kg_ha": 3450,
                "environmental_impact_score": 78
            },
            "water_efficiency_index": 0.88,
            "cost_effectiveness_ratio": 1.25,
            "sustainability_score": 82
        },
        {
            "scenario_name": "high_yield",
            "scenario_name_ar": "تحسين الإنتاجية",
            "final_state": {
                "soil_moisture_percent": 45,
                "plant_height_cm": 88,
                "biomass_kg_ha": 8650
            },
            "metrics": {
                "total_water_mm": 330,
                "total_nitrogen_kg_ha": 150,
                "total_cost_sar_ha": 3300,
                "predicted_yield_kg_ha": 4150,
                "environmental_impact_score": 62
            },
            "water_efficiency_index": 0.71,
            "cost_effectiveness_ratio": 1.26,
            "sustainability_score": 62
        }
    ],
    "recommendations": {
        "best_for_yield": {
            "scenario": "high_yield",
            "predicted_yield_kg_ha": 4150,
            "additional_yield_vs_current": 500,
            "additional_cost_sar_ha": 350
        },
        "best_for_sustainability": {
            "scenario": "optimized_water",
            "sustainability_score": 82,
            "water_savings_mm": 35,
            "cost_savings_sar_ha": 200
        },
        "best_balanced": {
            "scenario": "current_practice",
            "balanced_score": 72,
            "reason": "توازن جيد بين الإنتاجية والاستدامة"
        }
    }
}
```

### التحسين متعدد الأهداف | Multi-Objective Optimization

```http
POST /api/v1/digital-twin/optimize

Request:
{
    "field_id": "FIELD-003",
    "crop_type": "wheat",
    "crop_variety": "sakha_95",
    "simulation_start_date": "2025-01-15",
    "simulation_days": 120,
    "initial_state": {
        "soil_moisture_percent": 65,
        "soil_temperature_celsius": 18,
        "soil_salinity_ec": 0.8,
        "available_nitrogen_ppm": 22
    },
    "optimization_objective": "BALANCED",
    "objective_weights": {
        "water_efficiency": 0.25,
        "yield_maximization": 0.30,
        "cost_minimization": 0.20,
        "environmental_impact": 0.25
    },
    "constraints": {
        "max_water_mm": 350,
        "max_nitrogen_kg_ha": 150,
        "max_cost_sar_ha": 3500,
        "min_yield_kg_ha": 3000,
        "acceptable_salinity_ec": 2.5
    },
    "optimization_algorithm": "genetic_algorithm",
    "population_size": 50,
    "generations": 100,
    "mutation_rate": 0.15
}

Response:
{
    "optimization_id": "opt_20250116_001",
    "field_id": "FIELD-003",
    "crop_type": "wheat",
    "optimization_objective": "BALANCED",
    "status": "completed",
    "convergence_iterations": 87,
    "execution_time_seconds": 125.4,
    "optimal_solution": {
        "name": "optimized_scenario_001",
        "description": "سيناريو محسّن متوازن",
        "irrigation_schedule": [
            {
                "day": 21,
                "amount_mm": 23,
                "method": "drip",
                "timing": "early_morning"
            },
            {
                "day": 36,
                "amount_mm": 24,
                "method": "drip",
                "timing": "early_morning"
            },
            {
                "day": 56,
                "amount_mm": 22,
                "method": "drip",
                "timing": "early_morning"
            },
            {
                "day": 77,
                "amount_mm": 19,
                "method": "drip",
                "timing": "early_morning"
            }
        ],
        "fertilizer_applications": [
            {
                "day": 15,
                "type": "urea",
                "rate_kg_ha": 48,
                "method": "broadcast",
                "timing": "with_irrigation"
            },
            {
                "day": 40,
                "type": "urea",
                "rate_kg_ha": 32,
                "method": "fertigation",
                "timing": "with_irrigation"
            },
            {
                "day": 65,
                "type": "dap",
                "rate_kg_ha": 20,
                "method": "fertigation",
                "timing": "with_irrigation"
            }
        ]
    },
    "predicted_outcomes": {
        "total_water_mm": 288,
        "total_nitrogen_kg_ha": 120,
        "total_cost_sar_ha": 2875,
        "predicted_yield_kg_ha": 3925,
        "environmental_impact_score": 74,
        "overall_optimization_score": 78.5
    },
    "pareto_front": [
        {
            "rank": 1,
            "water_mm": 260,
            "yield_kg_ha": 3400,
            "cost_sar_ha": 2650,
            "environment_score": 82
        },
        {
            "rank": 2,
            "water_mm": 275,
            "yield_kg_ha": 3650,
            "cost_sar_ha": 2800,
            "environment_score": 78
        },
        {
            "rank": 3,
            "water_mm": 288,
            "yield_kg_ha": 3925,
            "cost_sar_ha": 2875,
            "environment_score": 74
        }
    ],
    "improvement_over_baseline": {
        "water_efficiency_improvement_percent": 12.5,
        "yield_improvement_kg_ha": 275,
        "cost_saving_sar_ha": 75,
        "environmental_improvement_percent": 6
    }
}
```

### تحديث حالة الحقل (تصفية كالمان) | Field State Update (Kalman Filtering)

```http
POST /api/v1/digital-twin/state/update

Request:
{
    "field_id": "FIELD-003",
    "measurement_timestamp": "2025-02-15T10:30:00Z",
    "sensor_measurements": {
        "soil_moisture_percent": 45,
        "soil_temperature_celsius": 22,
        "soil_salinity_ec": 1.1,
        "available_nitrogen_ppm": 18,
        "available_phosphorus_ppm": 10,
        "plant_height_cm": 42,
        "leaf_area_index": 2.1,
        "air_temperature_celsius": 20,
        "relative_humidity_percent": 55
    },
    "measurement_uncertainties": {
        "soil_moisture_uncertainty": 2.0,
        "temperature_uncertainty": 0.5,
        "salinity_uncertainty": 0.15,
        "nitrogen_uncertainty": 1.5
    },
    "sensor_reliability": {
        "soil_moisture_sensor": 0.95,
        "temperature_sensor": 0.98,
        "salinity_sensor": 0.92
    }
}

Response:
{
    "field_id": "FIELD-003",
    "update_timestamp": "2025-02-15T10:30:00Z",
    "kalman_filter_state": {
        "soil_moisture_percent": 44.8,
        "soil_temperature_celsius": 21.95,
        "soil_salinity_ec": 1.08,
        "available_nitrogen_ppm": 17.9,
        "available_phosphorus_ppm": 10.2,
        "plant_height_cm": 42.1,
        "leaf_area_index": 2.08
    },
    "state_estimation_confidence": {
        "overall_accuracy_percent": 94.2,
        "soil_moisture_confidence": 0.95,
        "temperature_confidence": 0.97,
        "salinity_confidence": 0.92,
        "nitrogen_confidence": 0.91
    },
    "innovation": {
        "innovation_sequence": 0.2,
        "residuals": {
            "soil_moisture_residual": 0.2,
            "temperature_residual": 0.05,
            "salinity_residual": 0.02
        }
    },
    "covariance_matrix_trace": 0.45,
    "state_health": "healthy",
    "next_update_recommendation": {
        "suggested_interval_days": 3,
        "critical_measurements": ["soil_moisture", "nitrogen"],
        "next_measurement_date": "2025-02-18T10:30:00Z"
    }
}
```

### معلومات محصول اليمن | Yemen-Specific Crop Information

```http
GET /api/v1/digital-twin/yemen/crops

Response:
{
    "yemen_crops": [
        {
            "crop_id": "wheat_yemen",
            "crop_type": "wheat",
            "crop_name_ar": "القمح",
            "varieties_ar": [
                "سخا 95",
                "سخا 94",
                "جيزة 168",
                "محلي يمني"
            ],
            "optimal_planting_date": "2024-11-15",
            "optimal_planting_date_ar": "منتصف نوفمبر",
            "growing_season_days": 120,
            "water_requirement_mm": 400,
            "climate_adaptation": "cold_tolerant",
            "salinity_tolerance_ec": 4.0,
            "typical_yield_kg_ha": 3500
        },
        {
            "crop_id": "date_palm_yemen",
            "crop_type": "date_palm",
            "crop_name_ar": "نخيل التمر",
            "varieties_ar": [
                "البرحي",
                "الفردوس",
                "الزهيدي",
                "الخضراوي"
            ],
            "optimal_planting_date": "2025-02-01",
            "growing_season_days": 180,
            "water_requirement_mm": 800,
            "climate_adaptation": "heat_tolerant",
            "salinity_tolerance_ec": 6.0,
            "typical_yield_kg_ha": 25000
        },
        {
            "crop_id": "sorghum_yemen",
            "crop_type": "sorghum",
            "crop_name_ar": "الذرة الرفيعة",
            "varieties_ar": [
                "محلي عريش",
                "محلي جنوب اليمن"
            ],
            "optimal_planting_date": "2025-04-01",
            "growing_season_days": 90,
            "water_requirement_mm": 300,
            "climate_adaptation": "drought_tolerant",
            "salinity_tolerance_ec": 5.0,
            "typical_yield_kg_ha": 2000
        }
    ]
}
```

---

## نماذج البيانات | Data Models

### FieldState | حالة الحقل

```json
{
  "field_id": "FIELD-003",
  "timestamp": "2025-02-15T10:30:00Z",
  "crop_type": "wheat",
  "growth_stage": "V4",
  "growth_stage_ar": "الإطراق (4 أوراق)",
  "state_variables": {
    "soil_moisture_percent": 44.8,
    "soil_temperature_celsius": 21.95,
    "soil_salinity_ec": 1.08,
    "available_nitrogen_ppm": 17.9,
    "available_phosphorus_ppm": 10.2,
    "available_potassium_ppm": 185,
    "plant_height_cm": 42.1,
    "leaf_area_index": 2.08,
    "biomass_kg_ha": 1850,
    "root_depth_cm": 35,
    "water_stress_index": 0.15
  },
  "measurement_confidence": {
    "overall_accuracy_percent": 94.2,
    "kalman_filter_type": "extended_kalman_filter",
    "state_estimation_method": "bayesian"
  }
}
```

### SimulationResult | نتيجة المحاكاة

```json
{
  "simulation_id": "sim_20250116_001",
  "field_id": "FIELD-003",
  "crop_type": "wheat",
  "crop_variety": "sakha_95",
  "simulation_period": {
    "start_date": "2025-01-15",
    "end_date": "2025-05-15",
    "total_days": 120
  },
  "management_practices": {
    "irrigation_schedule": [],
    "fertilizer_applications": [],
    "pest_management": []
  },
  "final_state": {
    "soil_moisture_percent": 42,
    "plant_height_cm": 85,
    "leaf_area_index": 4.5,
    "biomass_kg_ha": 8200,
    "predicted_yield_kg_ha": 3800
  },
  "daily_outputs": [],
  "performance_metrics": {
    "water_use_efficiency_kg_mm_ha": 1.31,
    "nitrogen_use_efficiency_kg_kg": 31.67,
    "harvest_index": 0.47
  },
  "status": "completed",
  "created_at": "2025-01-16T10:30:00Z"
}
```

### OptimizationResult | نتيجة التحسين

```json
{
  "optimization_id": "opt_20250116_001",
  "field_id": "FIELD-003",
  "objective": "BALANCED",
  "algorithm": "genetic_algorithm",
  "convergence_iterations": 87,
  "execution_time_seconds": 125.4,
  "optimal_solution": {
    "irrigation_schedule": [],
    "fertilizer_applications": []
  },
  "predicted_outcomes": {
    "total_water_mm": 288,
    "predicted_yield_kg_ha": 3925,
    "total_cost_sar_ha": 2875,
    "environmental_impact_score": 74,
    "overall_optimization_score": 78.5
  },
  "improvement_metrics": {
    "water_efficiency_improvement_percent": 12.5,
    "cost_improvement_percent": 2.5,
    "environmental_improvement_percent": 6
  },
  "pareto_front": [],
  "status": "completed"
}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم | Server
PORT=8253
HOST=0.0.0.0
ENVIRONMENT=production|staging|development|test

# قاعدة البيانات | Database
DATABASE_URL=postgresql://user:password@pgbouncer:6432/sahool?sslmode=require
POSTGRES_USER=sahool
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=sahool

# Redis
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=secure_password

# NATS
NATS_URL=nats://nats:4222
NATS_USER=sahool
NATS_PASSWORD=secure_password

# JWT / Authentication
JWT_SECRET_KEY=your_secret_key_minimum_32_characters
JWT_ALGORITHM=HS256

# Logging
LOG_LEVEL=INFO|DEBUG|WARNING|ERROR
LOG_FORMAT=json

# Tenant
TENANT_ID=sahool_default

# Simulation Configuration
MAX_SIMULATION_DAYS=365
DEFAULT_SIMULATION_TIMESTEP=1
KALMAN_FILTER_TYPE=extended_kalman_filter
STATE_ESTIMATION_ACCURACY_TARGET=0.92

# Optimization Configuration
OPTIMIZATION_DEFAULT_ALGORITHM=genetic_algorithm
GENETIC_ALGORITHM_POPULATION_SIZE=50
GENETIC_ALGORITHM_GENERATIONS=100
GENETIC_ALGORITHM_MUTATION_RATE=0.15

# Metrics
PROMETHEUS_METRICS_ENABLED=true
METRICS_PORT=9090
```

---

## التثبيت | Installation

### المتطلبات | Requirements

```bash
Python >= 3.11
PostgreSQL >= 16
Redis >= 7.0
NATS >= 2.10
```

### بناء الصورة | Build Docker Image

```bash
docker build -t sahool/digital-twin-engine:16.0.0 .
```

### تشغيل الخدمة | Run Service

```bash
# Docker Compose
docker-compose up digital-twin-engine

# Docker
docker run -p 8253:8253 \
  -e DATABASE_URL=postgresql://... \
  -e NATS_URL=nats://nats:4222 \
  sahool/digital-twin-engine:16.0.0
```

---

## الأمثلة | Examples

### مثال 1: محاكاة بسيطة | Simple Simulation

```bash
curl -X POST "http://localhost:8253/api/v1/digital-twin/simulate" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "FIELD-003",
    "crop_type": "wheat",
    "crop_variety": "sakha_95",
    "simulation_start_date": "2025-01-15",
    "simulation_days": 120,
    "initial_state": {
      "soil_moisture_percent": 65,
      "soil_temperature_celsius": 18,
      "soil_salinity_ec": 0.8,
      "available_nitrogen_ppm": 22
    },
    "management_practices": {
      "irrigation_schedule": [
        {"day": 20, "amount_mm": 25},
        {"day": 35, "amount_mm": 25}
      ]
    }
  }'
```

### مثال 2: تحديث الحالة مع تصفية كالمان | State Update with Kalman Filter

```bash
curl -X POST "http://localhost:8253/api/v1/digital-twin/state/update" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "FIELD-003",
    "measurement_timestamp": "2025-02-15T10:30:00Z",
    "sensor_measurements": {
      "soil_moisture_percent": 45,
      "soil_temperature_celsius": 22,
      "soil_salinity_ec": 1.1,
      "available_nitrogen_ppm": 18
    },
    "measurement_uncertainties": {
      "soil_moisture_uncertainty": 2.0,
      "temperature_uncertainty": 0.5
    }
  }'
```

### مثال 3: تحسين متعدد الأهداف | Multi-Objective Optimization

```bash
curl -X POST "http://localhost:8253/api/v1/digital-twin/optimize" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "FIELD-003",
    "crop_type": "wheat",
    "crop_variety": "sakha_95",
    "simulation_start_date": "2025-01-15",
    "simulation_days": 120,
    "initial_state": {
      "soil_moisture_percent": 65,
      "soil_temperature_celsius": 18,
      "soil_salinity_ec": 0.8,
      "available_nitrogen_ppm": 22
    },
    "optimization_objective": "BALANCED",
    "constraints": {
      "max_water_mm": 350,
      "max_nitrogen_kg_ha": 150,
      "min_yield_kg_ha": 3000
    }
  }'
```

---

## الاختبار | Testing

### اختبارات الوحدة | Unit Tests

```bash
# تشغيل جميع الاختبارات
make test-python

# اختبارات محددة
pytest tests/unit/ -v

# تغطية الكود
pytest tests/ --cov=src --cov-report=html
```

### اختبارات التكامل | Integration Tests

```bash
pytest tests/integration/ -v -s
```

### اختبارات الأداء | Performance Tests

```bash
# اختبار أداء المحاكاة
pytest tests/performance/test_simulation_performance.py -v

# اختبار أداء التحسين
pytest tests/performance/test_optimization_performance.py -v
```

---

## معايرة الأداء | Performance Benchmarks

| العملية | Operation | الوقت النموذجي | Typical Time |
|---------|-----------|---------------|--------------|
| محاكاة 120 يوم | 120-day simulation | 45-60 ثانية | 45-60 seconds |
| تحديث حالة كالمان | Kalman state update | 150-250 ملي ثانية | 150-250 ms |
| تحسين متعدد الأهداف | Multi-obj optimization | 120-180 ثانية | 120-180 seconds |
| مقارنة 5 سيناريوهات | 5-scenario comparison | 250-350 ثانية | 250-350 seconds |

---

## الاعتبارات الأمنية | Security Considerations

- جميع الاتصالات محمية بـ TLS/SSL
- JWT للمصادقة والتفويض
- التحقق من صحة جميع المدخلات (Pydantic v2)
- تسجيل جميع العمليات الحرجة
- حماية ضد SQL Injection و XSS
- تحديد معدل الطلب (Rate Limiting)

---

## نماذج البحث المدعومة | Supported Research Models

### محاصيل اليمن | Yemen Crops

**القمح (Wheat):**
- Sakha 95, Sakha 94, Giza 168
- محلي يمني
- نماذج خاصة لظروف اليمن المناخية

**نخيل التمر (Date Palm):**
- البرحي، الفردوس، الزهيدي، الخضراوي
- إدارة خاصة للملوحة
- موسم الإزهار والتلقيح

**الذرة الرفيعة (Sorghum):**
- محلي عريش
- مقاومة الجفاف
- محلي جنوب اليمن

### تصفية كالمان | Kalman Filtering

- Extended Kalman Filter (EKF)
- Unscented Kalman Filter (UKF)
- دقة تقدير الحالة > 92%

### خوارزميات التحسين | Optimization Algorithms

- Genetic Algorithm (GA)
- Particle Swarm Optimization (PSO)
- Weighted Sum Scalarization
- Pareto Front Analysis

---

## الترخيص | License

Proprietary - KAFAAT © 2026

---

## الدعم | Support

للأسئلة والمساعدة التقنية:

**Technical Support:**
- GitHub Issues: https://github.com/kafaat/sahool
- Email: support@sahool.app
- Documentation: https://docs.sahool.app

**أوقات العمل | Business Hours:**
- الأحد - الخميس | Sunday - Thursday
- 9:00 AM - 6:00 PM (Arabia Standard Time)

---

_Last Updated: February 2026_
_Version: 16.0.0_
