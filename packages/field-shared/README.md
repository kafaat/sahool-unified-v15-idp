# @sahool/field-shared

Shared field management functionality for SAHOOL field services.

## Overview

This package contains the core field management functionality that was previously duplicated across multiple services (`field-core` and `field-management-service`). By extracting the common code into a shared package, we've eliminated over 2,600 lines of code duplication.

## What's Included

### Entities
- **Field** - Core field entity with geospatial data, crop information, and health metrics
- **FieldBoundaryHistory** - Track changes to field boundaries over time
- **SyncStatus** - Mobile device sync status tracking

### Middleware
- **etag** - ETag-based optimistic locking for conflict resolution
- **validation** - GeoJSON and polygon coordinate validation
- **logger** - Request logging middleware

### Database
- **data-source** - TypeORM data source configuration

### Application
- **createFieldApp()** - Factory function to create a configured Express application
- **startFieldService()** - Convenience function to initialize database and start the service

## API Endpoints

The shared package provides a complete REST API for field management:

### Field CRUD
- `GET /api/v1/fields` - List all fields with filtering
- `GET /api/v1/fields/:id` - Get a single field (with ETag)
- `POST /api/v1/fields` - Create a new field
- `PUT /api/v1/fields/:id` - Update a field (with conflict detection)
- `DELETE /api/v1/fields/:id` - Delete a field
- `GET /api/v1/fields/nearby` - Geospatial search for nearby fields

### NDVI Analysis
- `GET /api/v1/fields/:id/ndvi` - Get NDVI analysis for a field
- `PUT /api/v1/fields/:id/ndvi` - Update NDVI value
- `GET /api/v1/ndvi/summary` - Tenant-wide NDVI summary

### Mobile Sync (Delta Sync)
- `GET /api/v1/fields/sync` - Delta sync for mobile clients
- `POST /api/v1/fields/sync/batch` - Batch upload with conflict detection
- `GET /api/v1/sync/status` - Get device sync status
- `PUT /api/v1/sync/status` - Update sync status

### Boundary History
- `GET /api/v1/fields/:id/boundary-history` - Get boundary change history
- `POST /api/v1/fields/:id/boundary-history/rollback` - Rollback to previous boundary

### Health Checks
- `GET /healthz` - Health check
- `GET /readyz` - Readiness check (includes database connectivity)

## Usage

### Basic Usage

```typescript
import { startFieldService } from '@sahool/field-shared';

const PORT = parseInt(process.env.PORT || "3000");
const SERVICE_NAME = "my-field-service";

startFieldService(SERVICE_NAME, PORT)
    .catch((error) => {
        console.error("Failed to start service:", error);
        process.exit(1);
    });
```

### Advanced Usage (Custom Configuration)

```typescript
import { createFieldApp, AppDataSource } from '@sahool/field-shared';

const app = createFieldApp("my-custom-service");

// Add custom middleware or routes here
app.use('/custom', customRouter);

// Initialize database and start server
await AppDataSource.initialize();
app.listen(3000, () => {
    console.log("Custom field service started");
});
```

### Importing Entities and Middleware

```typescript
import {
    Field,
    FieldBoundaryHistory,
    SyncStatus,
    generateETag,
    validatePolygonCoordinates,
    AppDataSource
} from '@sahool/field-shared';

// Use entities directly
const fieldRepo = AppDataSource.getRepository(Field);
const fields = await fieldRepo.find();

// Use validation
const result = validatePolygonCoordinates(coordinates);
if (!result.valid) {
    console.error("Invalid coordinates:", result.errors);
}

// Generate ETags for conflict resolution
const etag = generateETag(field.id, field.version);
```

## Features

### Geospatial Support
- PostGIS integration for spatial queries
- GeoJSON polygon validation
- Area calculation in hectares
- Nearby field search with configurable radius

### Optimistic Locking
- ETag-based conflict resolution
- Version tracking for all field updates
- Conflict response with server data
- Mobile-friendly sync protocol

### Mobile Sync
- Delta sync with timestamp-based filtering
- Batch operations for offline-first apps
- Device-level sync status tracking
- Conflict detection and resolution

### NDVI Health Monitoring
- Vegetation health analysis
- Historical trend tracking
- Category-based health scoring
- Tenant-wide analytics

## Environment Variables

```bash
PORT=3000                    # Service port (default: 3000)
DATABASE_URL=postgresql://...  # PostgreSQL connection string
NODE_ENV=development         # Environment (development/production)
```

## Database Requirements

This package requires PostgreSQL with the PostGIS extension:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

The package will automatically attempt to enable PostGIS on startup.

## Code Duplication Eliminated

**Before:** 2,600+ lines of duplicated code across:
- `apps/services/field-core/src/index.ts` (1,312 lines)
- `apps/services/field-management-service/src/index.ts` (1,312 lines)
- Plus duplicated entities, middleware, and utilities

**After:** Shared package with single source of truth
- Both services now just ~10 lines of code each
- Entities, middleware, and core logic maintained in one place
- Easier to maintain, test, and extend

## Migration Guide

If you're migrating from the old duplicated code:

1. Update package.json to include `@sahool/field-shared`
2. Replace the entire `src/index.ts` with the simple usage pattern above
3. Remove duplicated `entity/`, `middleware/`, `api/`, and `data-source.ts` files
4. Update any imports to use `@sahool/field-shared`

## License

SAHOOL Proprietary License
