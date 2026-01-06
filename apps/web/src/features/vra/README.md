# VRA (Variable Rate Application) Web UI

**نظام التطبيق المتغير المعدل - واجهة الويب**

Complete Variable Rate Application prescription map generation and management system for SAHOOL precision agriculture platform.

## 📋 Overview

The VRA feature enables farmers and agronomists to create precision agriculture prescription maps for variable-rate application of:

- **Fertilizers** (تسميد) - Optimize nitrogen/fertilizer application based on crop vigor
- **Seeds** (بذار) - Variable seeding rates based on field potential
- **Lime** (جير) - pH correction with variable lime application
- **Pesticides** (مبيدات) - Target problem areas with variable pesticide rates
- **Irrigation** (ري) - Variable water application based on stress indicators

## 🗂️ File Structure

```
/apps/web/src/features/vra/
├── api/
│   └── vra-api.ts              # API client for VRA endpoints
├── components/
│   ├── VRAPanel.tsx            # Main VRA panel with configuration
│   ├── PrescriptionMap.tsx     # Leaflet map with GeoJSON zones
│   ├── PrescriptionTable.tsx   # Zone details table with exports
│   └── VRAHistory.tsx          # Historical prescriptions list
├── hooks/
│   └── useVRA.ts               # React Query hooks
├── types/
│   └── vra.ts                  # TypeScript definitions
├── index.ts                    # Public exports
└── README.md                   # This file
```

## 🚀 Features

### ✅ Implemented Features

1. **Interactive Configuration Panel**
   - VRA type selection (fertilizer, seed, lime, pesticide, irrigation)
   - Target rate input with unit selection
   - Zone count selection (3 or 5 zones)
   - Zone classification method (NDVI, yield, soil, combined)
   - Optional product price for cost savings calculation

2. **Leaflet Map Visualization**
   - GeoJSON prescription zones rendering
   - Color-coded zones by NDVI/vigor level
   - Interactive zone popups with details
   - Hover effects and highlighting
   - OpenStreetMap base layer
   - Auto-zoom to fit zones

3. **Zone Details Table**
   - Comprehensive zone statistics
   - Application rates per zone
   - Area and percentage calculations
   - Savings analysis vs. flat rate
   - Export functionality (CSV, GeoJSON)

4. **Prescription History**
   - List of past prescriptions
   - View details and maps
   - Delete prescriptions
   - Export historical data

5. **Real-time Data Management**
   - TanStack Query integration
   - Optimistic updates
   - Cache invalidation
   - Loading and error states
   - Automatic refetching

6. **Bilingual Support**
   - Arabic/English labels throughout
   - RTL-aware UI components
   - Localized error messages

## 📦 Components

### VRAPanel

Main component for generating VRA prescriptions.

**Props:**
```typescript
interface VRAPanelProps {
  fieldId: string;
  fieldName?: string;
  fieldNameAr?: string;
  latitude: number;
  longitude: number;
  onPrescriptionGenerated?: (prescription: PrescriptionResponse) => void;
}
```

**Usage:**
```tsx
<VRAPanel
  fieldId="field_123"
  fieldName="North Field"
  fieldNameAr="الحقل الشمالي"
  latitude={15.5}
  longitude={44.2}
  onPrescriptionGenerated={(prescription) => {
    console.log('Generated prescription:', prescription.id);
  }}
/>
```

### PrescriptionMap

Leaflet map component for visualizing VRA zones.

**Props:**
```typescript
interface PrescriptionMapProps {
  prescription: PrescriptionResponse;
  height?: string;
}
```

**Features:**
- GeoJSON polygon rendering
- Color-coded zones by vigor level
- Interactive popups with zone details
- Hover effects and highlighting
- Auto-centering and zoom

**Usage:**
```tsx
<PrescriptionMap
  prescription={prescription}
  height="600px"
/>
```

### PrescriptionTable

Table view of zone details with export functionality.

**Props:**
```typescript
interface PrescriptionTableProps {
  prescription: PrescriptionResponse;
  showExport?: boolean;
}
```

**Features:**
- Zone-by-zone breakdown
- NDVI ranges, areas, percentages
- Recommended rates and total product
- Savings calculation
- CSV and GeoJSON export

**Usage:**
```tsx
<PrescriptionTable
  prescription={prescription}
  showExport={true}
/>
```

### VRAHistory

List of historical prescriptions for a field.

**Props:**
```typescript
interface VRAHistoryProps {
  fieldId: string;
  fieldName?: string;
  fieldNameAr?: string;
  limit?: number;
}
```

**Usage:**
```tsx
<VRAHistory
  fieldId="field_123"
  fieldName="North Field"
  limit={20}
/>
```

## 🔧 Hooks

### useVRA

Composite hook providing all VRA functionality.

```typescript
const vra = useVRA(fieldId, { enabled: true, limit: 10 });

// History
vra.history.data          // PrescriptionHistoryResponse
vra.history.isLoading     // boolean
vra.history.error         // Error | null

// Generate prescription
vra.generate.mutate({ fieldId, vraType, targetRate, ... })
vra.generate.isPending    // boolean
vra.generate.data         // PrescriptionResponse

// Export prescription
vra.export.mutate({ prescriptionId, format: 'geojson' })

// Delete prescription
vra.delete.mutate(prescriptionId)
```

### Individual Hooks

- `usePrescriptionHistory(fieldId, options)` - Fetch prescription history
- `usePrescriptionDetails(prescriptionId, options)` - Get prescription details
- `useGeneratePrescription()` - Generate new prescription
- `useExportPrescription()` - Export prescription
- `useDeletePrescription()` - Delete prescription

## 🌐 API Client

### Functions

```typescript
// Generate prescription
const response = await generatePrescription({
  fieldId: 'field_123',
  latitude: 15.5,
  longitude: 44.2,
  vraType: 'fertilizer',
  targetRate: 100,
  unit: 'kg/ha',
  numZones: 3,
  zoneMethod: 'ndvi',
  productPricePerUnit: 2.5,
});

// Get history
const history = await getPrescriptionHistory('field_123', 10);

// Get details
const details = await getPrescriptionDetails('prescription_456');

// Export
const exported = await exportPrescription('prescription_456', 'geojson');

// Delete
await deletePrescription('prescription_456');
```

### Query Keys

```typescript
import { vraKeys } from '@/features/vra';

// For cache invalidation and refetching
vraKeys.all                                      // ['vra']
vraKeys.prescriptions()                          // ['vra', 'prescriptions']
vraKeys.prescription(id)                         // ['vra', 'prescriptions', id]
vraKeys.history(fieldId)                         // ['vra', 'history', fieldId]
vraKeys.export(prescriptionId, format)           // ['vra', 'export', id, format]
```

## 📊 Types

### Core Types

```typescript
type VRAType = 'fertilizer' | 'seed' | 'lime' | 'pesticide' | 'irrigation';
type VRAMethod = 'ndvi' | 'yield' | 'soil' | 'combined';
type ZoneLevel = 'very_low' | 'low' | 'medium' | 'high' | 'very_high';
type ExportFormat = 'geojson' | 'csv' | 'shapefile' | 'isoxml';
```

### Request/Response Models

See `/types/vra.ts` for full type definitions:
- `PrescriptionRequest` - Request payload for generation
- `PrescriptionResponse` - Complete prescription with zones
- `ZoneResult` - Individual management zone details
- `PrescriptionSummary` - Summary for history list
- `PrescriptionHistoryResponse` - History response

## 🎨 Configuration

### VRA Types

```typescript
import { VRA_TYPES } from '@/features/vra';

VRA_TYPES.fertilizer  // { name, nameAr, description, defaultUnit, strategy }
VRA_TYPES.seed        // ...
VRA_TYPES.lime
VRA_TYPES.pesticide
VRA_TYPES.irrigation
```

### Zone Methods

```typescript
import { ZONE_METHODS } from '@/features/vra';

ZONE_METHODS.ndvi      // NDVI-based classification
ZONE_METHODS.yield     // Yield map-based
ZONE_METHODS.soil      // Soil analysis-based
ZONE_METHODS.combined  // Multi-factor
```

### Zone Colors

```typescript
import { ZONE_COLORS } from '@/features/vra';

ZONE_COLORS.very_low   // '#d62728' (red)
ZONE_COLORS.low        // '#ff7f0e' (orange)
ZONE_COLORS.medium     // '#ffdd00' (yellow)
ZONE_COLORS.high       // '#98df8a' (light green)
ZONE_COLORS.very_high  // '#2ca02c' (dark green)
```

## 🔐 Backend Integration

The VRA frontend connects to the backend API at:

```
POST   /v1/vra/generate                    # Generate prescription
GET    /v1/vra/prescriptions/:fieldId      # Get history
GET    /v1/vra/prescription/:id            # Get details
GET    /v1/vra/export/:id?format=geojson   # Export
DELETE /v1/vra/prescription/:id            # Delete
```

Backend implementation:
- `/apps/services/satellite-service/src/vra_generator.py`
- `/apps/services/satellite-service/src/vra_endpoints.py`

## 💡 Usage Examples

### Complete VRA Workflow

```tsx
import { VRAPanel, PrescriptionMap, PrescriptionTable } from '@/features/vra';

function FieldPrecisionAgriculturePage({ field }) {
  const [prescription, setPrescription] = useState(null);

  return (
    <div className="space-y-6">
      {/* Configuration and Generation */}
      <VRAPanel
        fieldId={field.id}
        fieldName={field.name}
        fieldNameAr={field.nameAr}
        latitude={field.latitude}
        longitude={field.longitude}
        onPrescriptionGenerated={setPrescription}
      />

      {/* Results - Map and Table are already included in VRAPanel */}
    </div>
  );
}
```

### Custom Hook Integration

```tsx
import { useVRA, PrescriptionMap } from '@/features/vra';

function CustomVRAInterface({ fieldId }) {
  const vra = useVRA(fieldId);
  const [selectedId, setSelectedId] = useState(null);

  const handleGenerate = async () => {
    const prescription = await vra.generate.mutateAsync({
      fieldId,
      latitude: 15.5,
      longitude: 44.2,
      vraType: 'fertilizer',
      targetRate: 100,
      unit: 'kg/ha',
      numZones: 3,
      zoneMethod: 'ndvi',
    });

    setSelectedId(prescription.id);
  };

  return (
    <div>
      {/* Custom UI */}
      <button onClick={handleGenerate} disabled={vra.generate.isPending}>
        Generate VRA Prescription
      </button>

      {/* History */}
      {vra.history.data?.prescriptions.map(p => (
        <div key={p.id} onClick={() => setSelectedId(p.id)}>
          {p.vraType} - {p.savingsPercent}% savings
        </div>
      ))}

      {/* Selected prescription map */}
      {selectedId && vra.generate.data && (
        <PrescriptionMap prescription={vra.generate.data} />
      )}
    </div>
  );
}
```

## 🧪 Testing

To test the VRA feature:

1. Navigate to a field page
2. Access the VRA panel
3. Configure prescription parameters
4. Click "Generate Prescription"
5. View the interactive map with zones
6. Inspect zone details in the table
7. Export prescription in desired format

## 📝 Notes

- **Leaflet CSS**: Already imported globally in `/apps/web/src/app/layout.tsx`
- **Dynamic Imports**: Components use Next.js dynamic imports to avoid SSR issues with Leaflet
- **GeoJSON Support**: Full support for polygon rendering from backend
- **Error Handling**: Comprehensive error states with bilingual messages
- **Loading States**: Loading indicators throughout the workflow
- **Cache Management**: Automatic invalidation and refetching with TanStack Query

## 🔄 Data Flow

```
User Input (VRAPanel)
  ↓
Generate Request (useGeneratePrescription)
  ↓
API Call (generatePrescription)
  ↓
Backend VRA Generator (/apps/services/satellite-service/src/vra_generator.py)
  ↓
Prescription Response with Zones
  ↓
Display Results (PrescriptionMap + PrescriptionTable)
  ↓
Cache & History Update
```

## 🛠️ Development

### Adding New VRA Types

1. Update backend `VRAType` enum in `vra_generator.py`
2. Update frontend `VRAType` in `/types/vra.ts`
3. Add configuration to `VRA_TYPES` constant
4. Update rate adjustment strategy in backend

### Adding New Export Formats

1. Implement export in backend `vra_generator.py`
2. Update `ExportFormat` type in `/types/vra.ts`
3. Add format to `EXPORT_FORMAT_LABELS`
4. Update `PrescriptionTable` export buttons

## 📚 Related Documentation

- [Backend VRA Generator](/apps/services/satellite-service/src/vra_generator.py)
- [API Endpoints](/apps/services/satellite-service/src/vra_endpoints.py)
- [NDVI Analysis](/apps/web/src/features/ndvi/)
- [Field Management](/apps/web/src/features/fields/)

## 🤝 Contributing

When adding features to the VRA module:

1. Maintain bilingual support (Arabic/English)
2. Include loading and error states
3. Use TanStack Query for data fetching
4. Follow existing TypeScript types
5. Add comprehensive JSDoc comments
6. Update this README with new features

---

**Last Updated**: 2026-01-06
**Version**: 1.0.0
**Maintainer**: SAHOOL Development Team
