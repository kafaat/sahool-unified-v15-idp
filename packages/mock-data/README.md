# @sahool/mock-data

Development and testing mock data generators for the SAHOOL platform. Produces realistic agricultural data — fields, users, alerts, NDVI readings, and weather — with Yemen-specific geography and bilingual Arabic/English content.

**This package must only be used in development and testing environments.**

## Installation

```bash
npm install --save-dev @sahool/mock-data
```

## Usage

```typescript
import {
  generateMockField,
  generateMockFields,
  generateTenantFields,
  generateMockUser,
  generateMockUsers,
  generateMockAlert,
  generateMockAlerts,
  generateMockWeather,
  generateMockNDVI,
} from "@sahool/mock-data";
```

## Generators

### Fields

```typescript
// Single field with Yemen coordinates
const field = generateMockField();

// Override specific properties
const wheatField = generateMockField({
  crop: "قمح",
  status: "active",
  tenantId: "tenant-001",
});

// Batch generation
const fields = generateMockFields(10);

// All fields for a specific tenant
const tenantFields = generateTenantFields("tenant-001", 5);
```

MockField shape:
```typescript
interface MockField {
  id: string;
  name: string;           // Arabic name: "حقل قمح - صنعاء"
  area: number;           // Hectares (0.5–50)
  crop: string;           // Arabic crop name
  status: "active" | "inactive" | "deleted";
  cropStage: "seeding" | "growing" | "flowering" | "ripening" | "harvest";
  coordinates: [number, number]; // Yemen lat/lng range
  ndviScore: number;      // 0.3–0.9
  healthScore: number;    // 60–100
  irrigationStatus: "optimal" | "needs_water" | "overwatered";
  soilMoisture: number;   // 20–80 (%)
  tenantId: string;
}
```

Coordinates are constrained to Yemen's geographic bounding box (lat 12.5–17.0, lng 42.5–54.0).

### Users

```typescript
const user = generateMockUser();
const users = generateMockUsers(20);
const admins = generateMockUsers(3, { role: "admin" });
```

### Alerts

```typescript
const alert = generateMockAlert();
const alerts = generateMockAlerts(15);
const criticalAlerts = generateMockAlerts(5, { severity: "critical" });
```

### Weather

```typescript
const weather = generateMockWeather({ location: "صنعاء" });
```

### NDVI

```typescript
const ndvi = generateMockNDVI({ fieldId: "field-001" });
```

## Utility Functions

```typescript
import { generateId, randomItem, randomFloat, randomNumber, arabicNames } from "@sahool/mock-data";

generateId();                        // "id_1706000000000_abc123"
randomItem(["a", "b", "c"]);        // random element
randomFloat(0.3, 0.9, 2);           // e.g. 0.67
randomNumber(60, 100);              // e.g. 84

// Available Arabic name pools
arabicNames.crops;    // ["قمح", "ذرة", "شعير", "نخيل", ...]
arabicNames.regions;  // ["صنعاء", "عدن", "حضرموت", ...]
```

## Vitest Integration

```typescript
import { generateMockField } from "@sahool/mock-data";

describe("FieldCard", () => {
  it("renders field name", () => {
    const field = generateMockField({ crop: "قمح" });
    render(<FieldCard field={field} />);
    expect(screen.getByText(field.name)).toBeInTheDocument();
  });
});
```
