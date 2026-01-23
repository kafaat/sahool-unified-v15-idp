# Zones Map Layer Widget - طبقة خريطة المناطق الصحية

A Flutter widget for displaying field health zones on an interactive map with color-coded polygons based on NDVI values.

## Features - المميزات

### Core Features

- ✅ **Color-coded health zones**: Automatic coloring based on NDVI values
  - 🟢 Green (>0.6): Healthy zones
  - 🟡 Yellow (0.4-0.6): Moderate health
  - 🔴 Red (<0.4): Critical zones requiring attention

- ✅ **Interactive zone labels**: Display zone names and NDVI values on the map

- ✅ **Zone selection**: Tap to select zones with animated highlight effect

- ✅ **Detailed popup**: Comprehensive zone information modal showing:
  - Zone name (bilingual)
  - NDVI value
  - Area in hectares
  - Health trend (improving/declining/stable)
  - Actionable recommendations

- ✅ **Bilingual support**: Full Arabic and English support with RTL layout

- ✅ **Loading & empty states**: User-friendly UI for data loading and empty scenarios

- ✅ **Map controls**: Built-in zoom controls and legend

- ✅ **Responsive design**: Works on all screen sizes

## Installation - التثبيت

The widget is already part of the project. No additional dependencies required beyond what's in `pubspec.yaml`:

```yaml
dependencies:
  flutter_map: ^7.0.2
  latlong2: ^0.9.1
```

## Usage - الاستخدام

### Basic Example

```dart
import 'package:latlong2/latlong.dart';
import 'zones_map_layer.dart';

// Create zone data
final zones = [
  ZoneHealth(
    id: 'zone_1',
    name: 'North Zone',
    nameAr: 'المنطقة الشمالية',
    ndvi: 0.75,
    areaHectares: 2.5,
    boundary: [
      LatLng(24.7150, 46.6750),
      LatLng(24.7160, 46.6750),
      LatLng(24.7160, 46.6770),
      LatLng(24.7150, 46.6770),
      LatLng(24.7150, 46.6750),
    ],
    trend: 'up',
    recommendations: ['Maintain current irrigation schedule'],
    recommendationsAr: ['الحفاظ على جدول الري الحالي'],
    lastUpdated: DateTime.now(),
  ),
];

// Use the widget
ZonesMapLayer(
  zones: zones,
  onZoneTapped: (zone) {
    print('Zone tapped: ${zone.name}');
  },
  initialCenter: LatLng(24.7145, 46.6760),
  initialZoom: 15.0,
)
```

### Advanced Example with State Management

```dart
class FieldHealthScreen extends StatefulWidget {
  final String fieldId;

  const FieldHealthScreen({required this.fieldId});

  @override
  State<FieldHealthScreen> createState() => _FieldHealthScreenState();
}

class _FieldHealthScreenState extends State<FieldHealthScreen> {
  List<ZoneHealth> _zones = [];
  ZoneHealth? _selectedZone;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadZones();
  }

  Future<void> _loadZones() async {
    setState(() => _isLoading = true);

    // Fetch zones from API or database
    final zones = await fetchFieldZones(widget.fieldId);

    setState(() {
      _zones = zones;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Field Health Zones')),
      body: ZonesMapLayer(
        zones: _zones,
        selectedZone: _selectedZone,
        onZoneTapped: (zone) {
          setState(() => _selectedZone = zone);
        },
        isLoading: _isLoading,
        enableSelection: true,
        showLabels: true,
      ),
    );
  }
}
```

## Widget Parameters - معاملات الWidget

### ZonesMapLayer

| Parameter         | Type                    | Required | Default | Description                  |
| ----------------- | ----------------------- | -------- | ------- | ---------------------------- |
| `zones`           | `List<ZoneHealth>`      | ✅       | -       | List of zones to display     |
| `selectedZone`    | `ZoneHealth?`           | ❌       | null    | Currently selected zone      |
| `onZoneTapped`    | `Function(ZoneHealth)?` | ❌       | null    | Callback when zone is tapped |
| `mapController`   | `MapController?`        | ❌       | null    | Custom map controller        |
| `initialCenter`   | `LatLng?`               | ❌       | null    | Initial map center           |
| `initialZoom`     | `double`                | ❌       | 14.0    | Initial zoom level           |
| `showLabels`      | `bool`                  | ❌       | true    | Show zone labels on map      |
| `isLoading`       | `bool`                  | ❌       | false   | Show loading state           |
| `enableSelection` | `bool`                  | ❌       | true    | Enable zone selection        |

### ZoneHealth Model

```dart
class ZoneHealth {
  final String id;                      // Unique zone ID
  final String name;                    // Zone name (English)
  final String nameAr;                  // Zone name (Arabic)
  final double ndvi;                    // NDVI value (0.0 - 1.0)
  final double areaHectares;           // Zone area in hectares
  final List<LatLng> boundary;         // Zone polygon coordinates
  final String? trend;                 // 'up', 'down', 'stable'
  final List<String>? recommendations;  // English recommendations
  final List<String>? recommendationsAr; // Arabic recommendations
  final DateTime? lastUpdated;         // Last data update timestamp
}
```

## Health Status Classification - تصنيف الحالة الصحية

The widget automatically classifies zones based on NDVI values:

| NDVI Range | Status   | Color     | Arabic |
| ---------- | -------- | --------- | ------ |
| > 0.6      | Healthy  | 🟢 Green  | صحي    |
| 0.4 - 0.6  | Moderate | 🟡 Yellow | متوسط  |
| < 0.4      | Critical | 🔴 Red    | حرج    |

## Integration with Existing Models - التكامل مع النماذج الموجودة

### From Field Entity

```dart
import '../../domain/entities/field.dart';

// Convert Field to zones (if field has zones data)
List<ZoneHealth> convertFieldToZones(Field field) {
  // If your field has zone data, convert it here
  // This is a placeholder - adjust based on your actual data structure

  return [
    ZoneHealth(
      id: field.id,
      name: field.name,
      nameAr: field.name, // Add Arabic name if available
      ndvi: field.ndvi,
      areaHectares: field.areaHectares,
      boundary: field.boundary,
      trend: _determineTrend(field),
      recommendations: _generateRecommendations(field),
      lastUpdated: field.ndviUpdatedAt,
    ),
  ];
}
```

### From VRA ManagementZone

```dart
import '../../../vra/models/vra_models.dart';

// Convert ManagementZone to ZoneHealth
ZoneHealth convertManagementZone(ManagementZone zone) {
  return ZoneHealth(
    id: zone.zoneId,
    name: zone.name,
    nameAr: zone.nameAr ?? zone.name,
    ndvi: zone.averageNdvi ?? 0.0,
    areaHectares: zone.area,
    boundary: _extractBoundary(zone.geometry),
    lastUpdated: zone.updatedAt,
  );
}

List<LatLng> _extractBoundary(Map<String, dynamic> geometry) {
  final type = geometry['type'] as String;
  final coordinates = geometry['coordinates'];

  if (type == 'Polygon') {
    final ring = coordinates[0] as List;
    return ring.map((coord) {
      final c = coord as List;
      return LatLng(c[1] as double, c[0] as double);
    }).toList();
  }

  return [];
}
```

### From Crop Health Zone

```dart
import '../../../crop_health/domain/entities/crop_health_entities.dart';

// Convert crop health Zone to ZoneHealth
ZoneHealth convertCropHealthZone(
  Zone zone,
  VegetationIndices indices,
  List<DiagnosisAction> actions,
) {
  return ZoneHealth(
    id: zone.zoneId,
    name: zone.name,
    nameAr: zone.nameAr ?? zone.name,
    ndvi: indices.ndvi,
    areaHectares: zone.areaHectares ?? 0.0,
    boundary: _extractBoundary(zone.geometry ?? {}),
    trend: _calculateTrend(indices),
    recommendations: actions
        .where((a) => a.zoneId == zone.zoneId)
        .map((a) => a.titleEn ?? a.title)
        .toList(),
    recommendationsAr: actions
        .where((a) => a.zoneId == zone.zoneId)
        .map((a) => a.title)
        .toList(),
  );
}
```

## Styling & Customization - التخصيص

The widget uses the SAHOOL theme system and adapts to:

- **Colors**: Uses `SahoolColors` from `sahool_theme.dart`
- **Typography**: Uses IBM Plex Sans Arabic font
- **Organic Design**: Rounded corners, soft shadows
- **RTL Support**: Automatically adjusts layout for Arabic

### Custom Colors

If you need different health colors, modify the `_getHealthColor` method in the widget:

```dart
Color _getHealthColor(HealthStatus status, {bool isSelected = false}) {
  final baseColor = switch (status) {
    HealthStatus.healthy => Colors.blue,      // Custom color
    HealthStatus.moderate => Colors.orange,   // Custom color
    HealthStatus.critical => Colors.red,      // Custom color
  };

  return isSelected ? baseColor : baseColor.withOpacity(0.7);
}
```

## Performance Considerations - اعتبارات الأداء

- **Polygon Complexity**: For fields with many zones (>50), consider:
  - Simplifying polygon boundaries
  - Implementing zone clustering at low zoom levels
  - Lazy loading zones as user pans/zooms

- **Animation**: The pulse animation on selected zones uses `AnimationController`
  - Automatically disposed when widget is destroyed
  - Consider disabling for low-end devices if needed

- **Map Tiles**: Uses OpenStreetMap by default
  - For offline support, configure `flutter_map_tile_caching`
  - For custom tiles, modify the `TileLayer` configuration

## Testing - الاختبار

### Unit Testing Zone Health Logic

```dart
void main() {
  group('ZoneHealth', () {
    test('classifies healthy zone correctly', () {
      final zone = ZoneHealth(
        id: 'test',
        name: 'Test',
        nameAr: 'اختبار',
        ndvi: 0.75,
        areaHectares: 1.0,
        boundary: [],
      );

      expect(zone.healthStatus, HealthStatus.healthy);
    });

    test('classifies critical zone correctly', () {
      final zone = ZoneHealth(
        id: 'test',
        name: 'Test',
        nameAr: 'اختبار',
        ndvi: 0.3,
        areaHectares: 1.0,
        boundary: [],
      );

      expect(zone.healthStatus, HealthStatus.critical);
    });
  });
}
```

### Widget Testing

```dart
void main() {
  testWidgets('displays empty state when no zones', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: ZonesMapLayer(zones: []),
        ),
      ),
    );

    expect(find.text('No zones to display'), findsOneWidget);
  });
}
```

## Troubleshooting - حل المشكلات

### Common Issues

**1. Map not displaying**

- Ensure internet connection for tile downloads
- Check that coordinates are valid (latitude: -90 to 90, longitude: -180 to 180)

**2. Zones not visible**

- Verify boundary coordinates are in correct order (LatLng format)
- Check that zone boundaries are closed (first point = last point)

**3. Labels overlapping**

- Reduce number of visible zones
- Implement label collision detection
- Hide labels at low zoom levels

**4. Performance issues**

- Simplify polygon boundaries (reduce points)
- Implement zone clustering
- Consider using vector tiles

## Examples - أمثلة

See `zones_map_layer_example.dart` for a complete working example.

## Related Files - الملفات ذات الصلة

- Widget: `zones_map_layer.dart`
- Example: `zones_map_layer_example.dart`
- Theme: `/lib/core/theme/sahool_theme.dart`
- Organic Widgets: `/lib/core/theme/organic_widgets.dart`

## Future Enhancements - التحسينات المستقبلية

Potential improvements:

- [ ] Zone clustering for large fields
- [ ] Heatmap overlay option
- [ ] Time-series comparison (before/after)
- [ ] Export zone data as GeoJSON
- [ ] Drawing tools to create/edit zones
- [ ] Offline map caching
- [ ] 3D terrain visualization
- [ ] Integration with satellite imagery

## License - الترخيص

Part of the SAHOOL Unified Platform v15
© 2024-2026 SAHOOL Agricultural Technology

---

For questions or issues, contact the development team.
