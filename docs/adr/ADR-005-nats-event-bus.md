# ADR-005: NATS for Event-Driven Architecture

## Status

Accepted

## Context

SAHOOL requires an event-driven architecture for:

1. **Decoupled services**: Services communicate without direct coupling
2. **Async operations**: Sync queue processing, notifications
3. **Real-time updates**: Push updates to mobile clients
4. **Reliability**: At-least-once delivery for critical events
5. **Scalability**: Handle 10,000+ events/second at peak harvest season

We evaluated several message broker solutions.

## Decision

We chose **NATS with JetStream** as our event bus infrastructure.

### Key Reasons

1. **Lightweight**: Single binary, minimal resources (~30MB RAM)
2. **High performance**: Millions of messages/second
3. **JetStream**: Built-in persistence and exactly-once semantics
4. **Subject-based routing**: Flexible topic patterns
5. **Clustering**: Easy horizontal scaling
6. **Operational simplicity**: Simple to deploy and manage

### Implementation Pattern

```python
# Publisher example
from sahool_libs.nats import NatsClient

async def publish_field_created(field_id: str, tenant_id: str):
    """Publish field creation event"""
    nats = NatsClient()

    await nats.publish(
        subject=f"sahool.events.fields.{tenant_id}.created",
        message={
            "event_type": "field.created",
            "field_id": field_id,
            "tenant_id": tenant_id,
            "timestamp": datetime.now().isoformat()
        }
    )
```

```python
# Consumer example
from sahool_libs.nats import NatsClient

async def handle_field_events():
    """Subscribe to field events"""
    nats = NatsClient()

    # Durable subscription with JetStream
    async for msg in nats.subscribe(
        subject="sahool.events.fields.>",
        durable="field-processor",
        deliver_policy="all"
    ):
        event = json.loads(msg.data)
        await process_field_event(event)
        await msg.ack()
```

### Subject Hierarchy

```
sahool.
├── events.                    # Domain events
│   ├── fields.{tenant}.       # Field operations
│   │   ├── created
│   │   ├── updated
│   │   └── deleted
│   ├── tasks.{tenant}.        # Task operations
│   │   ├── assigned
│   │   ├── completed
│   │   └── overdue
│   └── sync.{tenant}.         # Sync events
│       ├── requested
│       └── completed
├── commands.                  # Command messages
│   ├── notifications.send
│   └── reports.generate
└── queries.                   # Request-response
    └── satellite.analyze
```

### JetStream Configuration

```yaml
# Stream for field events with retention
jetstream:
  streams:
    - name: FIELD_EVENTS
      subjects:
        - "sahool.events.fields.>"
      retention: limits
      max_msgs: 10000000
      max_bytes: 10737418240 # 10GB
      max_age: 604800000000000 # 7 days in nanoseconds
      storage: file
      replicas: 3
      discard: old

    - name: SYNC_OUTBOX
      subjects:
        - "sahool.events.sync.>"
      retention: workqueue
      max_msgs: 1000000
      max_bytes: 1073741824 # 1GB
      storage: file
      replicas: 3
```

## Consequences

### Positive

- **Performance**: Low latency (<1ms pub-sub in cluster)
- **Reliability**: JetStream provides persistence
- **Simplicity**: Easy to deploy and operate
- **Scalability**: Horizontal scaling with clustering
- **Subject filtering**: Granular subscription patterns
- **Multi-tenant**: Subject hierarchy supports isolation

### Negative

- **Learning curve**: Different from traditional queues
- **JetStream complexity**: Persistent streams require planning
- **Monitoring**: Need additional tools for visibility
- **No built-in DLQ**: Must implement dead-letter handling

### Neutral

- Requires client library in each service
- WebSocket bridge needed for browser clients

## Alternatives Considered

### Alternative 1: Apache Kafka

**Considered because:**

- Industry standard for event streaming
- Excellent persistence and replay
- Rich ecosystem

**Rejected because:**

- Operational complexity (ZooKeeper/KRaft)
- Resource heavy (3+ GB RAM per broker)
- Overkill for our current scale
- Team unfamiliar with Kafka operations

### Alternative 2: RabbitMQ

**Considered because:**

- Mature and well-documented
- AMQP protocol support
- Good management UI

**Rejected because:**

- Higher latency than NATS
- Complex routing configuration
- More resource intensive
- Less suitable for high-throughput scenarios

### Alternative 3: Redis Pub/Sub + Streams

**Considered because:**

- Already using Redis for caching
- Simpler architecture

**Rejected because:**

- No native clustering for pub/sub
- Less mature persistence
- Memory-bound
- Not designed primarily for messaging

## Event Patterns

### Outbox Pattern Integration

```python
# Outbox processor publishes to NATS
class OutboxProcessor:
    async def process(self):
        """Process outbox entries and publish to NATS"""
        pending = await db.outbox.get_pending()

        for entry in pending:
            try:
                await nats.publish(
                    subject=f"sahool.events.{entry.aggregate}.{entry.event_type}",
                    message=entry.payload
                )
                await db.outbox.mark_published(entry.id)
            except Exception as e:
                await db.outbox.mark_failed(entry.id, str(e))
```

### Request-Reply for Sync Operations

```python
# Synchronous satellite analysis request
async def analyze_field(field_id: str) -> dict:
    """Request satellite analysis and wait for response"""
    response = await nats.request(
        subject="sahool.queries.satellite.analyze",
        data={"field_id": field_id},
        timeout=30.0  # 30 second timeout
    )
    return json.loads(response.data)
```

## References

- [NATS Documentation](https://docs.nats.io/)
- [JetStream](https://docs.nats.io/nats-concepts/jetstream)
- [NATS Patterns](https://docs.nats.io/nats-concepts/core-nats/patterns)
- [SAHOOL Sync Architecture](../architecture/SYNC.md)
