# Database Tests

Tests for database operations, geospatial queries, and connection pooling behavior. The test files use mock implementations so they run without a live PostgreSQL/PostGIS instance, while the audit reports document the results of real database analysis passes.

## Running

```bash
# All database tests
pytest tests/database/ -v

# Geospatial tests
pytest tests/database/test_postgis_spatial.py -v

# Connection pool tests
pytest tests/database/test_postgres_operations.py -v

# With a live database (integration mode)
DATABASE_URL=postgresql://sahool:pass@localhost:5432/sahool \
  pytest tests/database/ -v -m integration

# Via Makefile
make db-shell       # Connect to database for manual inspection
```

## Test Files

### `test_postgis_spatial.py`

Validates GeoJSON geometry operations and PostGIS query patterns:

- `GeoJSONPolygon` and `GeoJSONPoint` dataclass construction
- `GeometryValidator` — ring closure check, minimum 4 coordinates per ring, nested polygon support
- Area and distance calculation patterns (Haversine, ST_Area)
- Bounding box computation from polygon coordinates
- Point-in-polygon containment tests (ray casting algorithm)
- Coordinate precision and rounding for 6 decimal places (sub-meter accuracy)
- Multi-polygon and geometry collection handling

### `test_postgres_operations.py`

Validates asyncpg connection pool and transaction patterns:

- `MockAsyncConnection` — `execute`, `fetch`, `fetchrow`, `fetchval` async methods
- `MockConnectionPool` — pool acquisition, release, min/max size enforcement
- Transaction context manager: commit, rollback, nested transaction isolation
- Parameterized query building — positional `$1, $2, ...` placeholders
- Prepared statement caching behavior
- Concurrent query execution patterns (asyncio gather)
- Connection close and pool exhaustion handling

## Audit Reports

Generated reference reports from full database review passes:

| Report | Contents |
|--------|----------|
| `POSTGRESQL_AUDIT.md` | PostgreSQL 16 configuration audit |
| `PGBOUNCER_AUDIT.md` | PgBouncer pool settings analysis |
| `PGBOUNCER_OPTIMIZATION_SUMMARY.md` | Optimization recommendations |
| `INDEX_AUDIT.md` | Index usage and missing index analysis |
| `QUERY_PATTERNS_AUDIT.md` | Slow query patterns and N+1 issues |
| `PRISMA_SCHEMAS_AUDIT.md` | Prisma schema consistency across Node.js services |
| `DATABASE_SECURITY_AUDIT.md` | SSL, user privileges, and row-level security |
| `BACKUP_AUDIT.md` | WAL-G backup configuration |
| `REDIS_AUDIT.md` | Redis configuration and eviction policies |
| `NATS_AUDIT.md` | JetStream stream and consumer configuration |
| `DISASTER_RECOVERY_AUDIT.md` | RTO/RPO analysis and failover procedures |

## Related

- Database connection pattern: `shared/db/`
- PostGIS field boundary logic: `shared/field_boundaries/`
- Migration commands: `make db-migrate`, `make db-seed`, `make db-reset`
- Production DB config: `config/postgres/`, `docker/core/pgbouncer/`
