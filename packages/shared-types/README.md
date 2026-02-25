# @sahool/shared-types

Centralized TypeScript type definitions and unified API contracts for the SAHOOL platform. This package is the single source of truth for service ports, API endpoint paths, error codes, and domain types consumed by all frontend applications, the API client, Kong Gateway configuration, and mobile (Dart codegen).

## Installation

```bash
npm install @sahool/shared-types
```

## Package Structure

```
src/
├── auth.ts           # User, Role, Permission, JWTPayload types
├── api.ts            # Generic API response and pagination types
├── express.ts        # Express request augmentation (AuthenticatedRequest)
├── websocket.ts      # WebSocket message types
├── monitoring.ts     # NDVI, satellite, crop health monitoring types
├── field.ts          # Field and farm domain types
├── vision.ts         # YOLO vision service types (pest/disease/weed detection)
├── terrain.ts        # Terrain analysis and DEM types
├── hydrology.ts      # Hydrology and watershed types
├── leveling.ts       # Field leveling optimization types
├── edge.ts           # Edge device (Jetson Orin) management types
└── contracts/
    ├── index.ts          # CONTRACT_VERSION, barrel export
    ├── service-ports.ts  # SERVICE_PORTS, SERVICE_REGISTRY, SERVICE_PORT_ALIASES
    ├── error-codes.ts    # ERROR_CODES, ERROR_MESSAGES (bilingual EN/AR)
    ├── api-endpoints.ts  # *_ENDPOINTS constants, buildUrl() helper
    └── api-responses.ts  # ApiResponse, PaginatedResponse shapes
```

## Usage

### Domain Types

```typescript
import type { User, UserRole, JWTPayload } from "@sahool/shared-types";
import type { Field, Farm } from "@sahool/shared-types";
```

### Unified Contracts (recommended import path)

```typescript
import {
  SERVICE_PORTS,
  AUTH_ENDPOINTS,
  ERROR_CODES,
  buildUrl,
  CONTRACT_VERSION,
} from "@sahool/shared-types/contracts";

// Service port lookup
const port = SERVICE_PORTS.ADVISORY; // 8093

// Build a URL with path parameters
const url = buildUrl(FIELD_ENDPOINTS.GET, { fieldId: "abc-123" });
// => "/api/v1/fields/abc-123"

// Localized error message
import { getLocalizedError } from "@sahool/shared-types/contracts";
const msg = getLocalizedError(ERROR_CODES.NOT_FOUND, "ar");
```

### Subpath Imports

```typescript
import type { User }     from "@sahool/shared-types/auth";
import type { Field }    from "@sahool/shared-types/field";
import type { NDVIData } from "@sahool/shared-types/monitoring";
import type { VisionDetectionResult } from "@sahool/shared-types/vision";
```

## Key Exports

| Module | Notable Exports |
|--------|----------------|
| `contracts` | `SERVICE_PORTS`, `SERVICE_REGISTRY`, `AUTH_ENDPOINTS`, `FIELD_ENDPOINTS`, `VISION_ENDPOINTS`, `ERROR_CODES`, `ERROR_MESSAGES`, `buildUrl()`, `getServiceUrl()`, `CONTRACT_VERSION` |
| `auth` | `User`, `UserRole`, `JWTPayload`, `LoginResponse`, `Permission`, `Role` |
| `field` | `Field`, `Farm`, `FieldStatus`, `CropStage` |
| `monitoring` | `NDVIData`, `CropHealthStatus`, `SatelliteAnalysis` |
| `vision` | `DetectionResult`, `PestDetection`, `DiseaseDetection` |
| `edge` | `EdgeDevice`, `ModelDeployment`, `SyncStatus` |

## CONTRACT_VERSION

Version `1.2.0` (semver). Bump on every contract change:
- **Patch** (1.0.x): New additive constants
- **Minor** (1.x.0): New modules or structural additions
- **Major** (x.0.0): Removed or renamed exports (breaking)

Deprecated ports are aliased in `SERVICE_PORT_ALIASES` with `@deprecated` JSDoc.

## ESLint Enforcement

An `no-restricted-imports` rule prevents defining local port or error constants. Always import from this package:

```typescript
// Correct
import { SERVICE_PORTS } from "@sahool/shared-types/contracts";

// Incorrect - will trigger ESLint error
const AUTH_PORT = 3025;
```
