# AI Skills Metrics Integration Example

## Complete Service Example

Here's a complete example of integrating AI Skills Prometheus metrics into a FastAPI service:

```python
"""
AI Advisor Service - Metrics Integration Example
Demonstrates how to use AI metrics throughout a service
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import metrics utilities
from shared.ai.context_engineering import (
    ContextCompressor,
    CompressionStrategy,
    FarmMemory,
    MemoryType,
    RecommendationEvaluator,
    EvaluationCriteria,
    # Metrics
    track_compression,
    track_memory_operation,
    track_evaluation,
    record_memory_entry_stored,
    update_memory_usage,
    get_ai_metrics_registry,
)
from shared.monitoring.metrics import setup_metrics

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Request/Response Models
# ─────────────────────────────────────────────────────────────────────────────


class FieldData(BaseModel):
    """Field data for processing"""
    field_id: str
    soil_moisture: float
    temperature: float
    weather_forecast: str
    recent_observations: list[str]


class RecommendationRequest(BaseModel):
    """Request for fertilizer recommendation"""
    farm_id: str
    field_id: str
    recommendation: str
    context: dict


class CompressionRequest(BaseModel):
    """Request for context compression"""
    farm_id: str
    data: dict
    strategy: str = "hybrid"


# ─────────────────────────────────────────────────────────────────────────────
# Service Implementation
# ─────────────────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Service lifecycle management"""
    logger.info("Starting AI Advisor Service...")

    # Initialize AI metrics registry (optional - happens on first use)
    metrics = get_ai_metrics_registry()
    logger.info("AI metrics registry initialized")

    yield

    logger.info("Shutting down AI Advisor Service...")


app = FastAPI(
    title="AI Advisor Service",
    version="1.0.0",
    lifespan=lifespan
)

# Setup standard HTTP metrics (request count, latency, errors)
setup_metrics(app, service_name="ai_advisor_service")


# ─────────────────────────────────────────────────────────────────────────────
# Compression Endpoint
# ─────────────────────────────────────────────────────────────────────────────


@app.post("/api/v1/compression/compress-field-data")
@track_compression  # Metrics tracked automatically
async def compress_field_data(request: CompressionRequest):
    """
    Compress field data for efficient context windows.

    Automatically tracked metrics:
    - compression_operations_total
    - compression_latency_seconds
    - compression_original_tokens
    - compression_compressed_tokens
    - compression_ratio
    - compression_tokens_saved
    """
    try:
        compressor = ContextCompressor()

        strategy = CompressionStrategy(request.strategy)
        result = await compressor.compress(
            request.data,
            strategy=strategy
        )

        logger.info(
            f"Field data compressed: {result.compression_ratio:.2%} "
            f"compression from {result.original_tokens} to {result.compressed_tokens} tokens"
        )

        return {
            "status": "success",
            "original_tokens": result.original_tokens,
            "compressed_tokens": result.compressed_tokens,
            "compression_ratio": result.compression_ratio,
            "tokens_saved": result.tokens_saved,
            "compressed_text": result.compressed_text,
        }
    except Exception as e:
        logger.error(f"Compression failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Memory Management Endpoints
# ─────────────────────────────────────────────────────────────────────────────


@app.post("/api/v1/memory/store-observation")
@track_memory_operation(operation_type="store")
async def store_field_observation(request: FieldData):
    """
    Store field observation in memory.

    Automatically tracked metrics:
    - memory_operations_total
    - memory_storage_latency_seconds
    """
    try:
        memory = FarmMemory()

        observation = {
            "field_id": request.field_id,
            "soil_moisture": request.soil_moisture,
            "temperature": request.temperature,
            "weather": request.weather_forecast,
        }

        entry = await memory.add(
            tenant_id=request.field_id,
            data=observation,
            memory_type=MemoryType.OBSERVATION
        )

        # Record entry metadata
        entry_size = len(str(observation).encode())
        record_memory_entry_stored(
            entry_size_bytes=entry_size,
            entry_type=str(MemoryType.OBSERVATION)
        )

        # Update memory usage metrics
        total_entries = await memory.get_entry_count(request.field_id)
        total_bytes = await memory.get_total_size_bytes(request.field_id)
        update_memory_usage(total_entries, total_bytes)

        logger.info(
            f"Observation stored for field {request.field_id}: "
            f"{total_entries} entries, {total_bytes / 1000:.1f}KB used"
        )

        return {
            "status": "success",
            "entry_id": entry.id,
            "entries_count": total_entries,
            "memory_usage_kb": total_bytes / 1000,
        }
    except Exception as e:
        logger.error(f"Failed to store observation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/memory/get-recent-history")
@track_memory_operation(operation_type="retrieve")
async def get_recent_history(farm_id: str, limit: int = 10):
    """
    Retrieve recent memory entries.

    Automatically tracked metrics:
    - memory_operations_total
    - memory_retrieval_latency_seconds
    """
    try:
        memory = FarmMemory()

        entries = await memory.retrieve_by_type(
            tenant_id=farm_id,
            memory_type=MemoryType.CONVERSATION,
            limit=limit
        )

        logger.info(f"Retrieved {len(entries)} entries for farm {farm_id}")

        return {
            "status": "success",
            "entries_count": len(entries),
            "entries": [
                {
                    "id": entry.id,
                    "data": entry.data,
                    "created_at": entry.created_at.isoformat(),
                }
                for entry in entries
            ],
        }
    except Exception as e:
        logger.error(f"Failed to retrieve history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Evaluation Endpoint
# ─────────────────────────────────────────────────────────────────────────────


@app.post("/api/v1/recommendations/evaluate")
@track_evaluation(recommendation_type="fertilization")
async def evaluate_fertilizer_recommendation(request: RecommendationRequest):
    """
    Evaluate a fertilizer recommendation using LLM-as-Judge.

    Automatically tracked metrics:
    - evaluation_operations_total
    - evaluation_latency_seconds
    - evaluation_score_overall
    - evaluation_score_accuracy
    - evaluation_score_actionability
    - evaluation_score_safety
    - evaluation_score_relevance
    - evaluation_score_completeness
    - evaluation_score_clarity
    - evaluation_grades_total
    """
    try:
        evaluator = RecommendationEvaluator()

        result = await evaluator.evaluate(
            recommendation=request.recommendation,
            context=request.context,
            criteria=[
                EvaluationCriteria.ACCURACY,
                EvaluationCriteria.ACTIONABILITY,
                EvaluationCriteria.SAFETY,
                EvaluationCriteria.RELEVANCE,
                EvaluationCriteria.COMPLETENESS,
                EvaluationCriteria.CLARITY,
            ]
        )

        logger.info(
            f"Recommendation evaluated: score={result.overall_score:.2f}, "
            f"grade={result.grade}"
        )

        return {
            "status": "success",
            "overall_score": result.overall_score,
            "grade": result.grade,
            "criteria_scores": result.criteria_scores,
            "feedback": result.feedback,
        }
    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Metrics Endpoint
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/metrics")
async def metrics_endpoint():
    """
    Prometheus metrics endpoint.
    Exposes all metrics collected by the service.
    """
    from shared.monitoring.metrics import get_registry

    registry = get_registry("sahool_ai")
    return registry.export()


# ─────────────────────────────────────────────────────────────────────────────
# Health Checks
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/healthz")
async def liveness():
    """Liveness probe"""
    return {
        "status": "ok",
        "service": "ai_advisor_service",
        "version": "1.0.0"
    }


@app.get("/readyz")
async def readiness():
    """Readiness probe"""
    return {
        "status": "ok",
        "service": "ai_advisor_service",
        "dependencies": {
            "compression": "ready",
            "memory": "ready",
            "evaluation": "ready",
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
```

## Docker Compose Configuration

Add this service to your `docker-compose.yml`:

```yaml
services:
  ai-advisor-service:
    build:
      context: ./apps/services/ai-advisor
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://sahool:password@postgres:5432/sahool?sslmode=require
      NATS_URL: nats://nats:4222
      ENVIRONMENT: development
      LOG_LEVEL: INFO
    depends_on:
      - postgres
      - nats
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Prometheus Configuration

Add this scrape config to your `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'ai_advisor_service'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s
```

## Grafana Dashboards

### Dashboard 1: Compression Efficiency

```json
{
  "title": "AI Context Compression",
  "panels": [
    {
      "title": "Compression Ratio",
      "targets": [
        {
          "expr": "avg(sahool_ai_compression_ratio)"
        }
      ]
    },
    {
      "title": "Operations/sec",
      "targets": [
        {
          "expr": "rate(sahool_ai_compression_operations_total[1m])"
        }
      ]
    },
    {
      "title": "Latency (p95)",
      "targets": [
        {
          "expr": "histogram_quantile(0.95, rate(sahool_ai_compression_latency_seconds_bucket[5m]))"
        }
      ]
    }
  ]
}
```

### Dashboard 2: Memory Usage

```json
{
  "title": "AI Memory Management",
  "panels": [
    {
      "title": "Memory Usage (MB)",
      "targets": [
        {
          "expr": "sahool_ai_memory_usage_bytes / 1000000"
        }
      ]
    },
    {
      "title": "Entries Count",
      "targets": [
        {
          "expr": "sahool_ai_memory_entries_stored"
        }
      ]
    },
    {
      "title": "Evictions/min",
      "targets": [
        {
          "expr": "rate(sahool_ai_memory_evictions_total[1m])"
        }
      ]
    }
  ]
}
```

## Alert Rules

### Alert: High Compression Errors

```yaml
groups:
  - name: ai_compression
    rules:
      - alert: HighCompressionErrorRate
        expr: rate(sahool_ai_compression_errors_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High compression error rate"
          description: "Compression error rate is {{ $value }} errors/sec"
```

### Alert: Memory Growing

```yaml
groups:
  - name: ai_memory
    rules:
      - alert: HighMemoryUsage
        expr: sahool_ai_memory_usage_bytes > 500000000
        for: 5m
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ humanize $value }} bytes"
```

### Alert: High Evaluation Latency

```yaml
groups:
  - name: ai_evaluation
    rules:
      - alert: HighEvaluationLatency
        expr: histogram_quantile(0.95, rate(sahool_ai_evaluation_latency_seconds_bucket[5m])) > 10
        for: 5m
        annotations:
          summary: "High evaluation latency"
          description: "p95 latency is {{ $value }}s"
```

## Testing the Integration

```bash
# Start the service
python apps/services/ai-advisor/src/main.py

# Test compression endpoint
curl -X POST http://localhost:8000/api/v1/compression/compress-field-data \
  -H "Content-Type: application/json" \
  -d '{
    "farm_id": "farm_123",
    "data": {"field_data": "..."},
    "strategy": "hybrid"
  }'

# View metrics
curl http://localhost:8000/metrics

# Check health
curl http://localhost:8000/healthz
```

## Expected Metrics Output

After running some operations, you should see:

```
# HELP sahool_ai_compression_operations_total Total context compression operations performed
# TYPE sahool_ai_compression_operations_total counter
sahool_ai_compression_operations_total{service="ai_context_engineering",component="compression"} 5

# HELP sahool_ai_memory_entries_stored Current number of memory entries stored
# TYPE sahool_ai_memory_entries_stored gauge
sahool_ai_memory_entries_stored{service="ai_context_engineering",component="memory"} 42

# HELP sahool_ai_evaluation_operations_total Total recommendation evaluations performed
# TYPE sahool_ai_evaluation_operations_total counter
sahool_ai_evaluation_operations_total{service="ai_context_engineering",component="evaluation"} 3

# HELP sahool_ai_compression_latency_seconds Context compression latency in seconds
# TYPE sahool_ai_compression_latency_seconds histogram
sahool_ai_compression_latency_seconds_bucket{service="ai_context_engineering",component="compression",le="0.01"} 2
sahool_ai_compression_latency_seconds_bucket{service="ai_context_engineering",component="compression",le="0.025"} 4
...
sahool_ai_compression_latency_seconds_sum{service="ai_context_engineering",component="compression"} 0.15
sahool_ai_compression_latency_seconds_count{service="ai_context_engineering",component="compression"} 5
```

## Next Steps

1. Copy this example and adapt to your service
2. Add the decorators to your existing operations
3. Deploy and monitor the `/metrics` endpoint
4. Import dashboards into Grafana
5. Set up alerts based on your SLOs

---

_For more details, see `METRICS_INTEGRATION.md`_
