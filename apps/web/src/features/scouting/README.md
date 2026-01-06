# SAHOOL Scouting Web UI

**Field Scouting System for Agricultural Platform**
نظام الكشافة الحقلية لمنصة ساحول الزراعية

## Overview

The Scouting feature provides a comprehensive web interface for field scouts to record observations during field inspections. It includes interactive map-based observation recording, photo uploads, severity tracking, and historical analysis.

## Features

### 🗺️ Interactive Map Scouting
- Click on map to add observation points
- Real-time marker visualization
- Custom color-coded markers by category and severity
- Field boundary overlays

### 📸 Observation Management
- Photo upload with drag & drop
- 6 observation categories (pests, diseases, weeds, nutrients, water, other)
- Subcategory classification
- 5-level severity scale
- Bilingual notes (Arabic/English)
- Optional task creation

### 📊 Session Tracking
- Start/end scouting sessions
- Session duration tracking
- Real-time observation counting
- Session summary statistics

### 📜 History & Analytics
- Past session viewing
- Advanced filtering (date, category, severity)
- Statistics dashboard
- PDF report generation

## File Structure

```
/apps/web/src/features/scouting/
├── types/
│   └── scouting.ts              # TypeScript types and interfaces
├── api/
│   └── scouting-api.ts          # API client with offline support
├── hooks/
│   └── useScouting.ts           # React Query hooks
├── components/
│   ├── ScoutingMode.tsx         # Main scouting interface
│   ├── ObservationForm.tsx      # Observation creation form
│   ├── ObservationMarker.tsx    # Custom map marker
│   ├── ScoutingHistory.tsx      # Past sessions viewer
│   └── index.ts                 # Component exports
├── index.ts                     # Feature exports
└── README.md                    # This file
```

## Usage

### Basic Implementation

```tsx
import { ScoutingMode } from '@/features/scouting';

function FieldPage() {
  return (
    <ScoutingMode
      fieldId="field-123"
      center={[24.7136, 46.6753]}
      zoom={15}
    />
  );
}
```

### With Field Boundary

```tsx
import { ScoutingMode } from '@/features/scouting';

function FieldPage() {
  const fieldBoundary = {
    type: 'Polygon',
    coordinates: [[[lng1, lat1], [lng2, lat2], ...]]
  };

  return (
    <ScoutingMode
      fieldId="field-123"
      fieldBoundary={fieldBoundary}
      center={[24.7136, 46.6753]}
      zoom={15}
    />
  );
}
```

### View Scouting History

```tsx
import { ScoutingHistory } from '@/features/scouting';

function HistoryPage() {
  return (
    <ScoutingHistory
      fieldId="field-123"
      showFilters={true}
      showStatistics={true}
      onSelectSession={(sessionId) => {
        // Navigate to session details
        router.push(`/scouting/${sessionId}`);
      }}
    />
  );
}
```

### Using Hooks Directly

```tsx
import { useScoutingSessionManager } from '@/features/scouting';

function CustomScoutingComponent() {
  const {
    session,
    observations,
    summary,
    isLoading,
    startSession,
    endSession,
    addObservation,
  } = useScoutingSessionManager('field-123');

  const handleStart = async () => {
    await startSession('Starting inspection');
  };

  const handleObservation = async (data) => {
    await addObservation(data);
  };

  return (
    <div>
      {!session && (
        <button onClick={handleStart}>Start Session</button>
      )}

      {session && (
        <div>
          <p>Active Session: {session.id}</p>
          <p>Observations: {observations.length}</p>
        </div>
      )}
    </div>
  );
}
```

## Types

### Main Types

```typescript
// Observation Categories
type ObservationCategory =
  | 'pest'      // حشرات
  | 'disease'   // فطريات/أمراض
  | 'weed'      // أعشاب ضارة
  | 'nutrient'  // نقص غذائي
  | 'water'     // جفاف/ري
  | 'other';    // أخرى

// Severity Level (1-5)
type Severity = 1 | 2 | 3 | 4 | 5;

// Session Status
type SessionStatus = 'active' | 'completed' | 'cancelled';

// Observation
interface Observation {
  id: string;
  sessionId: string;
  fieldId: string;
  location: GeoPoint;
  category: ObservationCategory;
  subcategory?: string;
  severity: Severity;
  notes: string;
  notesAr?: string;
  photos: AnnotatedPhoto[];
  taskCreated?: boolean;
  taskId?: string;
  createdAt: string;
  updatedAt: string;
}

// Scouting Session
interface ScoutingSession {
  id: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  status: SessionStatus;
  startTime: string;
  endTime?: string;
  duration?: number;
  scoutId: string;
  scoutName?: string;
  observationsCount: number;
  observations?: Observation[];
  categoryCounts?: Record<ObservationCategory, number>;
  severityDistribution?: Record<Severity, number>;
  averageSeverity?: number;
  weather?: {
    temperature?: number;
    humidity?: number;
    conditions?: string;
  };
  notes?: string;
  notesAr?: string;
  createdAt: string;
  updatedAt: string;
}
```

## API Endpoints

The feature expects the following REST API endpoints:

```
POST   /api/v1/scouting/sessions              - Start session
PUT    /api/v1/scouting/sessions/:id/end      - End session
GET    /api/v1/scouting/sessions/:id          - Get session
GET    /api/v1/scouting/sessions/active       - Get active session
GET    /api/v1/scouting/sessions/:id/summary  - Get session summary
GET    /api/v1/scouting/sessions              - List sessions (with filters)

POST   /api/v1/scouting/observations          - Create observation
PUT    /api/v1/scouting/observations/:id      - Update observation
DELETE /api/v1/scouting/observations/:id      - Delete observation
GET    /api/v1/scouting/sessions/:id/observations - List observations

POST   /api/v1/scouting/photos                - Upload photo
POST   /api/v1/scouting/sessions/:id/report   - Generate report

GET    /api/v1/scouting/statistics            - Get statistics
```

## Offline Support

The feature includes built-in offline support:

- **Offline Cache**: Observations are cached in localStorage when offline
- **Auto-Sync**: Automatically syncs cached data when connection is restored
- **Mock Responses**: Falls back to mock data when API is unavailable
- **Optimistic Updates**: UI updates immediately, syncs in background

### Manual Sync

```tsx
import { useSyncOfflineData } from '@/features/scouting';

function SyncButton() {
  const sync = useSyncOfflineData();

  const handleSync = async () => {
    const result = await sync.mutateAsync();
    console.log(`Synced: ${result.synced}, Failed: ${result.failed}`);
  };

  return <button onClick={handleSync}>Sync Offline Data</button>;
}
```

## Internationalization

All components support Arabic and English:

- RTL layout for Arabic
- Bilingual labels from `next-intl`
- Arabic and English field values
- Date/time localization

```tsx
// Automatic locale detection
const locale = useLocale();
const isArabic = locale === 'ar';

// Display localized content
<p>{isArabic ? labelAr : label}</p>
```

## Map Integration

Built with Leaflet and React Leaflet:

```tsx
import 'leaflet/dist/leaflet.css';
import { MapContainer, TileLayer } from 'react-leaflet';

// Custom marker icons
import L from 'leaflet';

const customIcon = L.divIcon({
  html: `<div style="...">...</div>`,
  className: 'custom-observation-marker',
  iconSize: [36, 36],
  iconAnchor: [18, 36],
  popupAnchor: [0, -36],
});
```

## Dependencies

- `react-leaflet` - Map components
- `leaflet` - Map library
- `@tanstack/react-query` - Data fetching/caching
- `next-intl` - Internationalization
- `axios` - HTTP client
- `date-fns` - Date formatting
- `lucide-react` - Icons
- `clsx` / `tailwind-merge` - Styling

## Styling

Uses Tailwind CSS with custom SAHOOL colors:

```css
/* Primary Colors */
--sahool-green-50: #f0fdf4;
--sahool-green-600: #16a34a;

/* Severity Colors */
--severity-1: #10b981; /* Very Low - Green */
--severity-2: #84cc16; /* Low - Lime */
--severity-3: #f59e0b; /* Moderate - Amber */
--severity-4: #f97316; /* High - Orange */
--severity-5: #ef4444; /* Critical - Red */
```

## Category Configuration

Categories are defined in `types/scouting.ts`:

```typescript
export const CATEGORY_OPTIONS: CategoryOption[] = [
  {
    value: 'pest',
    label: 'Pest',
    labelAr: 'حشرات',
    icon: 'Bug',
    color: '#ef4444',
    subcategories: [
      { value: 'aphid', label: 'Aphids', labelAr: 'من' },
      { value: 'caterpillar', label: 'Caterpillars', labelAr: 'دودة' },
      // ...
    ],
  },
  // ... more categories
];
```

## Performance Optimizations

- React Query caching (1-5 min stale time)
- Optimistic updates for mutations
- Image optimization for photo uploads
- Lazy loading for history list
- Debounced search filtering

## Testing

```bash
# Run unit tests
npm test

# Run type checking
npm run typecheck

# Run linting
npm run lint
```

## Future Enhancements

- [ ] Photo annotation tools (draw on images)
- [ ] Voice notes recording
- [ ] GPS accuracy indicator
- [ ] Weather integration
- [ ] AI-powered pest/disease identification
- [ ] Offline map tiles
- [ ] Multi-field session support
- [ ] Team collaboration features
- [ ] Export to Excel/CSV

## Support

For issues or questions, contact the SAHOOL development team.

---

**Version**: 1.0.0
**Last Updated**: 2026-01-06
**Maintained by**: SAHOOL Platform Team
