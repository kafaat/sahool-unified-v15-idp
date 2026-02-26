# Snapshot Tests

Snapshot tests detect unintended changes to API response shapes and NATS event schemas. Tests generate normalized snapshots on first run, then compare subsequent runs against the stored baseline. Volatile fields (IDs, timestamps, tokens) are replaced with `<VOLATILE>` before comparison.

## Running

```bash
# Run snapshot tests (compare against stored snapshots)
pytest tests/snapshots/ -v

# Update snapshots (regenerate baselines after intentional changes)
UPDATE_SNAPSHOTS=true pytest tests/snapshots/ -v

# API response snapshots only
pytest tests/snapshots/test_api_snapshots.py -v

# Event schema snapshots only
pytest tests/snapshots/test_event_snapshots.py -v
```

## Test Files

### `test_api_snapshots.py`

Verifies that API response structures remain stable across code changes:

**Normalization**

Before comparison, all responses are normalized by `normalize_api_response()`:
- Volatile fields replaced with `"<VOLATILE>"`: `id`, `created_at`, `updated_at`, `timestamp`, `request_id`, `correlation_id`, `token`, `access_token`, `refresh_token`
- Keys sorted alphabetically for deterministic comparison
- Nested objects and arrays recursively normalized

**Snapshot Storage**

Snapshots saved to `tests/snapshots/api_snapshots/` as JSON files, one per API endpoint shape.

**Covered Shapes**
- Authentication responses: login, token refresh, logout
- Field management: create, read, list (paginated), update, delete
- Advisory responses: recommendations with factor breakdowns
- Error responses: 400, 401, 403, 404, 422 shapes

### `test_event_snapshots.py`

Verifies NATS event schemas remain stable between releases:

**Event Types Covered**

| Event Class | Subject |
|-------------|---------|
| `FieldCreatedEvent` | `sahool.field.created` |
| `FieldUpdatedEvent` | `sahool.field.updated` |
| `WeatherForecastEvent` | `sahool.weather.forecast` |
| `SatelliteDataReadyEvent` | `sahool.satellite.data_ready` |
| `DiseaseDetectedEvent` | `sahool.vision.disease_detected` |
| `AgentExecutionCompletedEvent` | `sahool.agent.execution_completed` |

**Deterministic UUIDs**

Tests use fixed UUIDs (`00000000-0000-0000-0000-000000000001` etc.) to produce reproducible snapshots regardless of when the test runs.

**Stored Snapshots**

Pre-generated JSON baselines in `tests/snapshots/event_snapshots/`:
- `field_created.json`
- `field_updated.json`
- `weather_forecast.json`
- `satellite_data_ready.json`
- `disease_detected.json`
- `agent_execution_completed.json`

## Updating Snapshots

When making intentional schema changes, regenerate baselines:

```bash
UPDATE_SNAPSHOTS=true pytest tests/snapshots/ -v
git add tests/snapshots/event_snapshots/ tests/snapshots/api_snapshots/
git commit -m "chore: update API and event snapshots for v16.x changes"
```

Always review the diff before committing to confirm only intended fields changed.

## Related

- Event contracts: `shared/events/contracts.py`
- API contracts: `packages/shared-types/src/contracts/`
- Event schema governance: `governance/events/schemas/`
- CI guard: `.github/workflows/event-contracts-guard.yml`, `api-contracts-guard.yml`
