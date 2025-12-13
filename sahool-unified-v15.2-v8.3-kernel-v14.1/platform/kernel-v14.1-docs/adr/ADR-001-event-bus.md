# ADR-001: Event Bus Selection (NATS JetStream)

## Status
Accepted

## Date
2025-01-01

## Context

SAHOOL Platform requires an event bus for:
1. Asynchronous communication between microservices
2. Event persistence and replay
3. Multi-consumer support
4. Dead letter queue handling
5. Saga orchestration

Options considered:
- Redis Streams
- Apache Kafka
- RabbitMQ
- NATS JetStream

## Decision

**Use NATS JetStream as the primary event bus**

### Rationale

| Criteria | NATS JetStream | Kafka | Redis Streams |
|----------|---------------|-------|---------------|
| Operational Complexity | Low ⭐ | High | Low |
| Persistence | Yes ⭐ | Yes | Yes |
| Multi-Consumer | Yes ⭐ | Yes | Limited |
| KV Store (Saga State) | Built-in ⭐ | No | Separate |
| Memory Footprint | ~50MB ⭐ | ~1GB | ~100MB |
| Subject Wildcards | Yes ⭐ | No | No |
| Dead Letter Queue | Yes ⭐ | Yes | Manual |

### Configuration

```yaml
NATS:
  image: nats:2.10-alpine
  JetStream:
    enabled: true
    store_dir: /data
    max_memory: 1GB
    max_file: 10GB
  
  Streams:
    SAHOOL:
      subjects: ["astro.*.*", "weather.*.*", "crop.*.*", ...]
      retention: limits
      max_msgs: 1_000_000
      max_age: 7d
    
    SAHOOL_DLQ:
      subjects: ["dlq.*"]
      retention: limits
      max_age: 30d
```

### Key-Value Store Usage

```python
# Saga state management
kv = js.key_value("saga_states")
await kv.put(saga_id, state_json)
state = await kv.get(saga_id)
```

## Consequences

### Positive
- ✅ Single binary deployment
- ✅ Built-in persistence (JetStream)
- ✅ Built-in KV store for saga state
- ✅ Subject wildcards for flexible routing
- ✅ Low resource usage
- ✅ Simple configuration

### Negative
- ❌ Less ecosystem tooling than Kafka
- ❌ Smaller community
- ❌ No built-in schema registry (we build our own)

### Mitigations
- Build custom Schema Registry service
- Use NATS monitoring endpoints
- Document operational procedures

## Related
- ADR-004: Event Subject Naming
- services/process-manager/
- services/schema-registry/
