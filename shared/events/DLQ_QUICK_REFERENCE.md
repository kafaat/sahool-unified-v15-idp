# DLQ Quick Reference Card

## Common Commands

### Start DLQ Service

```bash
./scripts/dlq-quickstart.sh start
```

### View Statistics

```bash
./scripts/dlq-quickstart.sh stats
# or
curl http://localhost:8090/dlq/stats | jq
```

### List Messages

```bash
./scripts/dlq-quickstart.sh messages
# or with pagination
./scripts/dlq-quickstart.sh messages 2 20  # page 2, 20 per page
```

### Replay Messages

```bash
# Single message
./scripts/dlq-quickstart.sh replay 123

# Multiple messages
./scripts/dlq-quickstart.sh replay 123 124 125
```

### Stop DLQ Service

```bash
./scripts/dlq-quickstart.sh stop
```

## API Endpoints

| Endpoint                                     | Method | Description                                   |
| -------------------------------------------- | ------ | --------------------------------------------- |
| `/dlq/stats`                                 | GET    | Get DLQ statistics                            |
| `/dlq/messages`                              | GET    | List messages (supports ?page=1&page_size=50) |
| `/dlq/messages?subject=sahool.field.created` | GET    | Filter by subject                             |
| `/dlq/messages?error_type=ConnectionError`   | GET    | Filter by error type                          |
| `/dlq/replay/123`                            | POST   | Replay single message                         |
| `/dlq/replay/bulk`                           | POST   | Replay multiple (body: {message_seqs: [...]}) |

## Environment Variables

```bash
DLQ_ENABLED=true              # Enable/disable DLQ
DLQ_MAX_RETRIES=3            # Max retry attempts
DLQ_INITIAL_DELAY=1.0        # First retry delay (seconds)
DLQ_MAX_DELAY=60.0           # Max retry delay (seconds)
DLQ_ALERT_THRESHOLD=100      # Alert when message count exceeds
```

## Troubleshooting

### High DLQ Count

```bash
# 1. Check what's failing
./scripts/dlq-quickstart.sh messages | jq '.messages[].metadata.error_type'

# 2. Check which services
./scripts/dlq-quickstart.sh messages | jq '.messages[].metadata.consumer_service'

# 3. Fix the issue in your code/config

# 4. Replay messages
./scripts/dlq-quickstart.sh replay <seqs>
```

### Messages Not Moving to DLQ

Check logs:

```bash
docker-compose logs notification-service | grep DLQ
```

Verify DLQ is enabled:

```python
subscriber.stats['dlq_enabled']  # Should be True
```

## Code Integration

### Default (DLQ enabled automatically)

```python
from shared.events import EventSubscriber

subscriber = EventSubscriber()
await subscriber.connect()  # DLQ initialized here
await subscriber.subscribe(subject, handler)
```

### Custom Configuration

```python
from shared.events import EventSubscriber, DLQConfig, SubscriberConfig

dlq_config = DLQConfig(
    max_retry_attempts=5,
    initial_retry_delay=2.0,
)

config = SubscriberConfig(dlq_config=dlq_config)
subscriber = EventSubscriber(config=config)
```

### Get Statistics

```python
stats = subscriber.stats
print(f"DLQ count: {stats['dlq_count']}")
print(f"Retry count: {stats['retry_count']}")

dlq_stats = await subscriber.get_dlq_stats()
print(f"Total in DLQ: {dlq_stats['message_count']}")
```

## Error Types

**Non-Retriable (immediate DLQ):**

- ValidationError
- ValueError
- KeyError
- TypeError

**Retriable (with backoff):**

- ConnectionError
- TimeoutError
- Other exceptions

## Retry Timeline

With default config (3 retries, 2x multiplier):

- Attempt 1: Immediate
- Attempt 2: 1s delay
- Attempt 3: 2s delay
- Attempt 4: 4s delay
- After 4 failures → DLQ

## Monitoring

### Check DLQ Size

```bash
curl -s http://localhost:8090/dlq/stats | jq '.total_messages'
```

### Alert if threshold exceeded

```bash
count=$(curl -s http://localhost:8090/dlq/stats | jq '.total_messages')
if [ "$count" -gt 100 ]; then
  echo "Alert: DLQ has $count messages!"
fi
```

### Set up monitoring

```python
from shared.events.dlq_monitoring import DLQMonitor

async def alert_handler(alert):
    print(f"ALERT: {alert.message}")
    # Send to Slack, PagerDuty, etc.

monitor = DLQMonitor(alert_callback=alert_handler)
await monitor.start()
```

## Production Checklist

- [ ] DLQ environment variables configured
- [ ] DLQ management service deployed
- [ ] Monitoring/alerting configured
- [ ] Team trained on replay procedure
- [ ] Access control added to DLQ API
- [ ] Regular cleanup scheduled (weekly)
- [ ] Runbook documented

## Resources

- Full Guide: `shared/events/DLQ_README.md`
- Implementation: `DLQ_IMPLEMENTATION_SUMMARY.md`
- Changelog: `CHANGELOG_DLQ.md`
- Examples: `shared/events/DLQ_ENV_EXAMPLE.env`
