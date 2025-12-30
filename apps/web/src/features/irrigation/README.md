# Irrigation Zone Management

A comprehensive irrigation zone management component for the SAHOOL unified platform, designed for precision agriculture similar to Climate FieldView and John Deere Operations Center.

## Features

### Core Functionality
- **Zone Status Monitoring**: Real-time status indicators (optimal, dry, wet, alert, irrigating)
- **Sensor Readings**: Live soil moisture and temperature monitoring per zone
- **Irrigation Control**: Manual start/stop controls with loading states
- **Smart Scheduling**: Per-zone irrigation scheduling with frequency options
- **Efficiency Metrics**: Water usage tracking and efficiency scoring
- **Bilingual Support**: Full Arabic/English support with RTL layout

### User Experience
- Responsive design (mobile-first approach)
- Visual status cards with color-coded indicators
- Loading states for all async operations
- Error handling with user-friendly messages
- Animated status badges for active irrigation
- Relative time formatting for sensor updates

## Installation

```bash
# Already included in the SAHOOL platform
# Located at: apps/web/src/features/irrigation/components
```

## Usage

### Basic Implementation

```tsx
import { IrrigationZoneManager } from '@/features/irrigation/components';

function IrrigationPage() {
  return (
    <div>
      <IrrigationZoneManager />
    </div>
  );
}
```

### With Custom Layout

```tsx
import { IrrigationZoneManager } from '@/features/irrigation/components';

function FarmDashboard() {
  return (
    <div className="container mx-auto">
      <header>
        <h1>Farm Dashboard</h1>
      </header>

      <main>
        <IrrigationZoneManager />
      </main>
    </div>
  );
}
```

## TypeScript Interfaces

### IrrigationZone

```typescript
interface IrrigationZone {
  id: string;
  name: string;
  nameAr: string;
  location: string;
  locationAr: string;
  area: number; // hectares
  status: 'optimal' | 'dry' | 'wet' | 'alert' | 'irrigating';
  sensors: ZoneSensor[];
  schedule: ZoneSchedule;
  metrics: {
    waterUsage: number; // liters
    efficiency: number; // percentage
    lastIrrigation: Date;
    cropType: string;
    cropTypeAr: string;
  };
  isActive: boolean;
}
```

### ZoneSensor

```typescript
interface ZoneSensor {
  id: string;
  type: 'soil_moisture' | 'temperature' | 'humidity';
  value: number;
  unit: string;
  lastUpdate: Date;
  status: 'normal' | 'warning' | 'critical';
}
```

### ZoneSchedule

```typescript
interface ZoneSchedule {
  id: string;
  enabled: boolean;
  startTime: string;
  duration: number; // minutes
  frequency: 'daily' | 'weekly' | 'custom';
  daysOfWeek?: number[]; // 0-6 (Sunday-Saturday)
  nextRun?: Date;
}
```

## Component Structure

```
IrrigationZoneManager/
├── Header Section
│   ├── Title (Bilingual)
│   ├── Language Toggle
│   └── Summary Stats
│       ├── Total Zones
│       ├── Active Zones
│       ├── Alert Count
│       └── Average Efficiency
│
├── Zone Cards Grid
│   └── For each zone:
│       ├── Zone Header
│       │   ├── Name & Location
│       │   └── Status Badge
│       │
│       ├── Sensor Readings
│       │   ├── Soil Moisture
│       │   └── Temperature
│       │
│       ├── Metrics Display
│       │   ├── Water Usage
│       │   ├── Efficiency
│       │   └── Last Irrigation
│       │
│       ├── Schedule Info
│       │   ├── Schedule Time
│       │   ├── Duration
│       │   └── Next Run
│       │
│       └── Control Buttons
│           ├── Start/Stop
│           ├── Toggle Schedule
│           ├── Refresh Data
│           └── Settings
│
└── Footer
    └── Last Updated Timestamp
```

## Status Indicators

### Zone Status Types

- **Optimal** (Green): Soil moisture is in optimal range
- **Dry** (Orange): Soil moisture is below optimal, irrigation recommended
- **Wet** (Blue): Soil moisture is above optimal
- **Alert** (Red): Critical condition requiring immediate attention
- **Irrigating** (Cyan): Currently irrigating with animated indicator

### Sensor Status Types

- **Normal** (Green): Reading is within acceptable range
- **Warning** (Orange): Reading is approaching critical levels
- **Critical** (Red): Reading requires immediate attention

## API Integration

### Current Implementation

The component uses mock data for demonstration. To integrate with real APIs:

1. Replace mock data generation with API calls
2. Update handler functions to call backend endpoints
3. Implement proper error handling for network failures
4. Add retry logic for failed requests

### Example API Integration

```typescript
// In handleStartIrrigation
const handleStartIrrigation = async (zoneId: string) => {
  try {
    setLoadingZones((prev) => new Set(prev).add(zoneId));
    setError(null);

    // Replace with actual API call
    const response = await fetch(`/api/irrigation/zones/${zoneId}/start`, {
      method: 'POST',
    });

    if (!response.ok) throw new Error('Failed to start irrigation');

    const data = await response.json();

    setZones((prevZones) =>
      prevZones.map((zone) =>
        zone.id === zoneId ? { ...zone, ...data } : zone
      )
    );
  } catch (err) {
    setError(`Failed to start irrigation for zone ${zoneId}`);
    console.error('Start irrigation error:', err);
  } finally {
    setLoadingZones((prev) => {
      const newSet = new Set(prev);
      newSet.delete(zoneId);
      return newSet;
    });
  }
};
```

## Customization

### Changing Default Language

```tsx
const [language, setLanguage] = useState<'en' | 'ar'>('ar'); // Default to Arabic
```

### Modifying Zone Status Colors

Edit the `getStatusColor` function:

```typescript
const getStatusColor = (status: IrrigationZone['status']) => {
  switch (status) {
    case 'optimal':
      return 'bg-green-100 border-green-500 text-green-800';
    // ... customize other colors
  }
};
```

### Adding New Sensor Types

1. Update the `ZoneSensor` type definition
2. Add rendering logic in the `renderZoneCard` function
3. Update mock data generation

## Performance Considerations

- Uses React state management for efficient re-renders
- Loading states prevent duplicate API calls
- Optimized re-renders with proper state updates
- Responsive design for all screen sizes

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- RTL support for Arabic language

## Dependencies

- **React**: ^18.0.0
- **lucide-react**: Icons library
- **Tailwind CSS**: Styling framework

## Icons Used

All icons from lucide-react:
- Droplets: Irrigation/moisture indicator
- MapPin: Location marker
- Clock: Scheduling
- Play/Pause: Control buttons
- Settings: Configuration
- AlertCircle: Alerts and warnings
- Check: Success indicators
- RefreshCw: Refresh/loading
- TrendingUp: Temperature/metrics

## Yemen Market Considerations

- Arabic language support with proper RTL layout
- Units in hectares (ha) and liters (L)
- Temperature in Celsius
- Date/time formatting for ar-YE locale
- Cultural considerations for UI/UX

## Future Enhancements

- [ ] Real-time WebSocket updates for sensor data
- [ ] Historical data charts and trends
- [ ] Weather integration for smart scheduling
- [ ] Zone grouping and bulk operations
- [ ] Mobile app integration
- [ ] Push notifications for critical alerts
- [ ] Advanced scheduling algorithms
- [ ] Water usage cost calculations
- [ ] Export reports (PDF/Excel)
- [ ] Map view with zone visualization

## Troubleshooting

### Icons not showing
Ensure lucide-react is installed:
```bash
npm install lucide-react
```

### Tailwind classes not working
Verify Tailwind CSS is configured in your project.

### TypeScript errors
Ensure TypeScript is configured and dependencies are installed:
```bash
npm install --save-dev typescript @types/react @types/node
```

## Support

For issues or questions, contact the SAHOOL platform development team.

## License

Proprietary - SAHOOL Unified Platform
