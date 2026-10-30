# AI Skills Metrics Integration Guide
## دليل تكامل قياسات مهارات الذكاء الاصطناعي

This guide demonstrates how to integrate Prometheus metrics for AI context engineering operations with the SAHOOL monitoring system.

---

## Overview

The `metrics.py` module provides comprehensive Prometheus metrics for:

1. **Token Compression Metrics**
   - Compression operations count
   - Original/compressed token counts
   - Compression ratio distribution
   - Tokens saved
   - Latency histograms

2. **Memory Usage Metrics**
   - Memory entries stored
   - Memory usage in bytes
   - Entry size distribution
   - Entries by type
   - Evictions and TTL expirations

3. **Evaluation Score Metrics**
   - Overall evaluation scores
   - Individual criterion scores (accuracy, actionability, safety, relevance, completeness, clarity)
   - Evaluation grades distribution
   - Evaluations by recommendation type

4. **Latency Metrics**
   - Compression latency
   - Memory retrieval latency
   - Memory storage latency
   - Evaluation latency

---

## Quick Start

### 1. Basic Usage with Decorators

#### Tracking Compression Operations

```python
from shared.ai.context_engineering import track_compression, ContextCompressor

@track_compression
async def compress_field_data(field_data: dict) -> CompressionResult:
    compressor = ContextCompressor()
    result = await compressor.compress(
        field_data,
        strategy=CompressionStrategy.HYBRID
    )
    return result

# The decorator automatically records:
# - Compression operations count
# - Original/compressed token counts
# - Compression ratio
# - Tokens saved
# - Latency
# - Errors
```

#### Tracking Memory Operations

```python
from shared.ai.context_engineering import (
    track_memory_operation,
    FarmMemory,
    record_memory_entry_stored,
    update_memory_usage
)

@track_memory_operation(operation_type="retrieve")
async def retrieve_farm_history(farm_id: str) -> list[MemoryEntry]:
    memory = FarmMemory()
    entries = await memory.retrieve_by_type(
        tenant_id=farm_id,
        memory_type=MemoryType.CONVERSATION
    )
    return entries

@track_memory_operation(operation_type="store")
async def store_farm_observation(farm_id: str, observation: dict) -> MemoryEntry:
    memory = FarmMemory()
    entry = await memory.add(
        tenant_id=farm_id,
        data=observation,
        memory_type=MemoryType.OBSERVATION
    )

    # Record entry metadata
    record_memory_entry_stored(
        entry_size_bytes=len(str(observation).encode()),
        entry_type=str(MemoryType.OBSERVATION)
    )

    # Update overall memory usage
    total_entries = await memory.get_entry_count(farm_id)
    total_bytes = await memory.get_total_size_bytes(farm_id)
    update_memory_usage(total_entries, total_bytes)

    return entry
```

#### Tracking Evaluation Operations

```python
from shared.ai.context_engineering import (
    track_evaluation,
    RecommendationEvaluator,
    RecommendationType
)

@track_evaluation(recommendation_type=RecommendationType.FERTILIZATION)
async def evaluate_fertilizer_recommendation(
    recommendation: str,
    context: dict
) -> EvaluationResult:
    evaluator = RecommendationEvaluator()
    result = await evaluator.evaluate(
        recommendation=recommendation,
        context=context,
        criteria=[
            EvaluationCriteria.ACCURACY,
            EvaluationCriteria.ACTIONABILITY,
            EvaluationCriteria.SAFETY,
            EvaluationCriteria.RELEVANCE,
            EvaluationCriteria.COMPLETENESS,
            EvaluationCriteria.CLARITY,
        ]
    )
    return result
```

### 2. Manual Metric Recording

For operations not wrapped by decorators:

```python
from shared.ai.context_engineering import (
    record_memory_eviction,
    record_memory_ttl_expiration,
    update_memory_usage
)

# When evicting old entries
async def cleanup_old_entries(farm_id: str):
    memory = FarmMemory()
    evicted_count = await memory.cleanup_by_limit()

    for _ in range(evicted_count):
        record_memory_eviction(entry_type="old_entries")

    # Update metrics
    total_entries = await memory.get_entry_count(farm_id)
    total_bytes = await memory.get_total_size_bytes(farm_id)
    update_memory_usage(total_entries, total_bytes)

# When handling TTL expirations
async def expire_ttl_entries(farm_id: str):
    memory = FarmMemory()
    expired_count = await memory.cleanup_by_ttl()

    for _ in range(expired_count):
        record_memory_ttl_expiration(entry_type="expired_entries")
```

### 3. Using Context Managers

For more granular control:

```python
from shared.ai.context_engineering import track_operation_async

async def complex_ai_operation():
    async with track_operation_async("complex_operation"):
        # Your operation code
        await compress_data()
        await retrieve_memory()
        await evaluate_recommendation()
        # Metrics automatically recorded on success or error
```

---

## Integration with FastAPI Services

### Example Service Setup

```python
from fastapi import FastAPI
from shared.monitoring.metrics import setup_metrics
from shared.ai.context_engineering import get_ai_metrics_registry

app = FastAPI(title="AI Advisor Service", version="1.0.0")

# Setup standard HTTP metrics
setup_metrics(app, service_name="ai_advisor_service")

# AI metrics are automatically available
@app.on_event("startup")
async def startup_event():
    # Initialize AI metrics registry (optional - happens on first use)
    metrics = get_ai_metrics_registry()
    logger.info("AI metrics registry initialized")

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    registry = get_registry("sahool_ai")
    return registry.export()

@app.post("/api/v1/recommendations/evaluate")
@track_evaluation(recommendation_type="irrigation")
async def evaluate_irrigation_recommendation(request: dict):
    # Your evaluation logic
    pass

@app.post("/api/v1/context/compress")
@track_compression
async def compress_context(request: dict):
    # Your compression logic
    pass
```

---

## Prometheus Queries

### Token Compression

```promql
# Average compression ratio
avg(sahool_ai_compression_ratio_bucket{le="1.0"})

# Tokens saved per operation
rate(sahool_ai_compression_tokens_saved_sum[5m])

# Compression latency (95th percentile)
histogram_quantile(0.95, rate(sahool_ai_compression_latency_seconds_bucket[5m]))

# Compression error rate
rate(sahool_ai_compression_errors_total[5m])
```

### Memory Usage

```promql
# Current memory entries stored
sahool_ai_memory_entries_stored

# Memory usage in MB
sahool_ai_memory_usage_bytes / 1000000

# Memory operations per second
rate(sahool_ai_memory_operations_total[1m])

# Average entry size
sahool_ai_memory_entry_size_sum / sahool_ai_memory_entry_size_count
```

### Evaluation Scores

```promql
# Average accuracy score across all evaluations
avg(sahool_ai_evaluation_score_accuracy)

# Overall evaluation score distribution (99th percentile)
histogram_quantile(0.99, sahool_ai_evaluation_score_overall_bucket)

# Evaluation grade distribution
count(sahool_ai_evaluation_grades_total)

# Evaluation latency (p95)
histogram_quantile(0.95, rate(sahool_ai_evaluation_latency_seconds_bucket[5m]))
```

### Latency Monitoring

```promql
# Compression latency p99
histogram_quantile(0.99, rate(sahool_ai_compression_latency_seconds_bucket[5m]))

# Memory retrieval latency p95
histogram_quantile(0.95, rate(sahool_ai_memory_retrieval_latency_seconds_bucket[5m]))

# Memory storage latency p95
histogram_quantile(0.95, rate(sahool_ai_memory_storage_latency_seconds_bucket[5m]))

# Evaluation latency p99
histogram_quantile(0.99, rate(sahool_ai_evaluation_latency_seconds_bucket[5m]))
```

---

## Grafana Dashboard Integration

### Key Dashboard Panels

#### 1. Compression Efficiency
- **X-Axis**: Time
- **Y-Axis**: Compression Ratio
- **Query**: `avg(sahool_ai_compression_ratio)`
- **Alert**: Trigger if ratio > 0.9 (less effective compression)

#### 2. Memory Usage Trends
- **X-Axis**: Time
- **Y-Axis**: Memory (Bytes)
- **Query**: `sahool_ai_memory_usage_bytes`
- **Alert**: Trigger if > 500MB

#### 3. Evaluation Score Distribution
- **Chart Type**: Heatmap
- **X-Axis**: Time
- **Y-Axis**: Score Range
- **Query**: `sahool_ai_evaluation_score_overall`

#### 4. Operation Latencies
- **Chart Type**: Graph with percentiles
- **Query**:
  - p50: `histogram_quantile(0.5, ...)`
  - p95: `histogram_quantile(0.95, ...)`
  - p99: `histogram_quantile(0.99, ...)`

#### 5. Error Rates
- **X-Axis**: Time
- **Y-Axis**: Errors/sec
- **Query**: `rate(sahool_ai_*_errors_total[5m])`

---

## Best Practices

### 1. Decorator Usage
- **Always use decorators** for standardized operation tracking
- **Choose appropriate operation types** for memory operations
- **Ensure result objects** have expected attributes for automatic metric extraction

### 2. Memory Tracking
- **Call `update_memory_usage()`** after modifying memory state
- **Record entry metadata** when storing new entries
- **Track evictions and expirations** separately for debugging

### 3. Latency Monitoring
- **Track p95 and p99** percentiles for latency-sensitive operations
- **Establish baselines** for each operation type
- **Alert on sudden increases** (> 2x baseline)

### 4. Error Handling
- **All decorators catch exceptions** and record errors
- **Re-raise exceptions** after recording metrics
- **Monitor error rates** by operation type

### 5. Tenant Isolation
- **Metrics include service and component labels**
- **No tenant-specific information** in metric names
- **Use labels for grouping** if needed

---

## Metric Reference

### Counter Metrics

| Name | Description | Labels |
|------|-------------|--------|
| `compression_operations_total` | Total compression operations | service, component |
| `compression_errors_total` | Total compression errors | service, component |
| `memory_operations_total` | Total memory operations | service, component |
| `memory_errors_total` | Total memory errors | service, component |
| `memory_entries_by_type_total` | Entries by type | service, component |
| `memory_evictions_total` | Total evictions | service, component |
| `memory_ttl_expirations_total` | Total TTL expirations | service, component |
| `evaluation_operations_total` | Total evaluations | service, component |
| `evaluation_errors_total` | Total evaluation errors | service, component |
| `evaluation_grades_total` | Evaluations by grade | service, component |
| `evaluations_by_type_total` | Evaluations by type | service, component |

### Gauge Metrics

| Name | Description | Unit |
|------|-------------|------|
| `memory_entries_stored` | Current entries in memory | count |
| `memory_usage_bytes` | Current memory usage | bytes |

### Histogram Metrics

| Name | Description | Buckets |
|------|-------------|---------|
| `compression_original_tokens` | Original token count | 100, 250, 500, ... 32000 |
| `compression_compressed_tokens` | Compressed token count | 50, 100, 250, ... 16000 |
| `compression_ratio` | Compression ratio | 0.1, 0.2, ... 1.0 |
| `compression_tokens_saved` | Tokens saved | 10, 50, 100, ... 20000 |
| `memory_entry_size_bytes` | Entry size | 100, 500, 1000, ... 1000000 |
| `compression_latency_seconds` | Compression latency | 0.01, 0.025, ... 5.0 |
| `memory_retrieval_latency_seconds` | Retrieval latency | 0.001, 0.005, ... 1.0 |
| `memory_storage_latency_seconds` | Storage latency | 0.001, 0.005, ... 1.0 |
| `evaluation_latency_seconds` | Evaluation latency | 0.1, 0.25, ... 60.0 |
| `evaluation_score_*` | Criterion scores | 0.1, 0.2, ... 1.0 |

---

## Testing

### Unit Test Example

```python
import pytest
from shared.ai.context_engineering import (
    get_ai_metrics_registry,
    record_memory_entry_stored
)

@pytest.mark.unit
def test_memory_metrics_recording():
    """Test memory metrics are recorded correctly"""
    metrics = get_ai_metrics_registry()

    # Record entries
    record_memory_entry_stored(1000, "conversation")
    record_memory_entry_stored(2000, "field_state")

    # Verify metrics
    assert metrics.memory_operations.value >= 0
    assert metrics.memory_entries_by_type.value >= 2
```

---

## Troubleshooting

### Metrics Not Appearing

1. **Verify decorator applied**: Check that function is decorated
2. **Check exception handling**: Ensure no exceptions suppress metrics
3. **Verify registry initialization**: Call `get_ai_metrics_registry()` explicitly
4. **Check metric endpoint**: Ensure `/metrics` endpoint is accessible

### High Latency Alerts

1. **Check compression ratio**: May indicate inefficient compression strategy
2. **Monitor memory size**: Larger memories slow retrieval
3. **Check evaluation load**: LLM calls are inherently slow
4. **Review database performance**: Memory operations depend on DB

### Memory Growth

1. **Check TTL configuration**: Expired entries not being cleaned
2. **Review eviction policy**: Max entries limit may be too high
3. **Monitor entry sizes**: Large entries consume memory quickly
4. **Check compression effectiveness**: Compression should reduce memory

---

## Support

For issues or questions about AI metrics integration:

1. Check the `CLAUDE.md` file in the repository root
2. Review the `docs/` directory for additional documentation
3. Consult the monitoring team for Prometheus/Grafana questions
4. File issues in the SAHOOL issue tracker

---

_Last Updated: January 2025_
