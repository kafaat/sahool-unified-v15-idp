# ADR-007: Redis for Caching

## Status

Accepted

## Context

SAHOOL requires caching for:

1. **Satellite imagery**: NDVI analysis is computationally expensive
2. **Session data**: JWT validation and user context
3. **Rate limiting**: Kong rate limiter state
4. **Sync state**: Track pending sync operations across nodes

We needed a distributed caching solution for our microservices.

## Decision

We chose **Redis** as our distributed caching layer.

### Key Reasons

1. **Speed**: Sub-millisecond response times
2. **Data structures**: Beyond key-value (hashes, lists, sets)
3. **TTL support**: Automatic cache expiration
4. **Pub/Sub**: Real-time notifications
5. **Cluster mode**: Horizontal scaling
6. **Persistence options**: RDB/AOF for durability

### Implementation Pattern

```python
# Satellite service cache
from apps.services.satellite_service.cache import (
    get_cached_analysis,
    cache_analysis,
)

async def analyze_ndvi(field_id: str) -> dict:
    """Analyze NDVI with Redis caching."""

    # Check cache first
    cached = await get_cached_analysis(field_id)
    if cached:
        return cached

    # Compute expensive analysis
    result = await compute_ndvi_analysis(field_id)

    # Cache for 24 hours
    await cache_analysis(field_id, result, ttl=86400)

    return result
```

### Cache Key Patterns

```
sahool:
├── satellite:                    # Satellite service
│   ├── ndvi:{field_id}          # NDVI analysis results
│   └── timeseries:{field_id}    # Historical NDVI data
├── session:                      # User sessions
│   └── {session_id}             # Session data
├── ratelimit:                    # Kong rate limiting
│   └── {ip}:{endpoint}          # Request counts
└── sync:                         # Sync state
    └── {tenant}:{device}        # Last sync timestamp
```

### Configuration

```yaml
# Redis configuration for SAHOOL
redis:
  host: redis.sahool.internal
  port: 6379
  db: 0
  password: ${REDIS_PASSWORD}

  # Connection pool
  pool:
    min_size: 10
    max_size: 50

  # Timeouts
  socket_timeout: 5
  socket_connect_timeout: 5

  # Cluster mode (production)
  cluster:
    enabled: true
    nodes:
      - redis-0:6379
      - redis-1:6379
      - redis-2:6379
```

## Consequences

### Positive

- **Performance**: 99th percentile < 1ms latency
- **Reduced load**: Database queries reduced by 60%
- **Scalability**: Cluster mode for horizontal scaling
- **Simplicity**: Easy to understand and operate
- **Ecosystem**: Excellent client libraries (redis-py, aioredis)

### Negative

- **Memory cost**: All data in RAM
- **Eviction policies**: Need careful tuning
- **Persistence trade-offs**: Performance vs durability
- **Single point of failure**: Without clustering

### Neutral

- Requires memory capacity planning
- Sentinel or Cluster needed for HA

## Cache Strategies

### 1. Cache-Aside (NDVI Data)

```python
async def get_field_ndvi(field_id: str):
    # Check cache
    cached = await redis.get(f"sahool:satellite:ndvi:{field_id}")
    if cached:
        return json.loads(cached)

    # Load from service
    data = await satellite_service.analyze(field_id)

    # Store in cache
    await redis.setex(
        f"sahool:satellite:ndvi:{field_id}",
        86400,  # 24 hour TTL
        json.dumps(data)
    )

    return data
```

### 2. Write-Through (Session Data)

```python
async def update_session(session_id: str, data: dict):
    # Update cache immediately
    await redis.hset(
        f"sahool:session:{session_id}",
        mapping=data
    )
    await redis.expire(f"sahool:session:{session_id}", 3600)

    # Persist to database async
    await db.sessions.update(session_id, data)
```

### 3. Cache Invalidation (Field Updates)

```python
async def update_field(field_id: str, data: dict):
    # Update database
    await db.fields.update(field_id, data)

    # Invalidate related caches
    await redis.delete(
        f"sahool:satellite:ndvi:{field_id}",
        f"sahool:satellite:timeseries:{field_id}"
    )
```

## Alternatives Considered

### Alternative 1: Memcached

**Rejected because:**
- No persistence options
- Limited data structures
- No pub/sub capability
- Less feature-rich

### Alternative 2: Application-Level Cache

**Rejected because:**
- Not distributed (each node has own cache)
- Memory duplication across instances
- Cache invalidation complexity

### Alternative 3: CDN Caching (for satellite imagery)

**Considered for:**
- Satellite tile caching only

**Decision:**
- Will add CDN layer in Phase 3
- Redis remains primary cache for computed data

## Monitoring

```python
# Cache statistics endpoint
@app.get("/v1/cache/stats")
async def cache_stats():
    info = await redis.info()
    return {
        "hits": info.get("keyspace_hits", 0),
        "misses": info.get("keyspace_misses", 0),
        "hit_rate": calculate_hit_rate(info),
        "memory_used": info.get("used_memory_human"),
        "connected_clients": info.get("connected_clients"),
    }
```

## References

- [Redis Documentation](https://redis.io/docs/)
- [Redis Best Practices](https://redis.io/docs/management/optimization/)
- [SAHOOL Cache Implementation](../../apps/services/satellite-service/src/cache.py)
