# Field Health Widget

## Overview

The **Field Health Widget** is a comprehensive Flutter widget designed to display field health scores in the SAHOOL mobile app. It provides an at-a-glance view of field health status with detailed recommendations and quick actions.

![Field Health Widget](./assets/field_health_widget_demo.png)

## Features

### ✅ Core Features

1. **Circular Progress Indicator**
   - Visual representation of overall health score (0-100)
   - Color-coded based on health status
   - Animated transitions

2. **Four Mini Indicators**
   - 🌱 **NDVI**: Vegetation health index
   - 💧 **Irrigation**: Water management status
   - ✓ **Tasks**: Pending tasks count
   - ☀️ **Weather**: Weather suitability

3. **Trend Indicator**
   - ↗️ Upward trend (improving)
   - → Stable trend (maintaining)
   - ↘️ Downward trend (declining)
   - Shows percentage change

4. **Alert Badge**
   - Red badge showing critical alert count
   - Pulsing animation for urgent alerts
   - Border highlight when alerts present

5. **Expandable Details**
   - Tap to expand/collapse recommendations
   - Smooth animation transitions
   - Comprehensive health breakdown

6. **Recommendations List**
   - AI-generated recommendations
   - Priority-based sorting (High/Medium/Low)
   - Category icons (irrigation, fertilization, pest control, etc.)
   - Quick action buttons

7. **Task Creation**
   - One-tap task creation from recommendations
   - Pre-filled task details
   - Seamless navigation to task screen

8. **Localization**
   - Full Arabic and English support
   - RTL layout support
   - Bilingual labels throughout

9. **Dark Mode**
   - Automatic theme adaptation
   - Optimized contrast for both themes
   - Consistent color scheme

## Usage

### Basic Usage

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'field_health_widget.dart';

class MyFieldScreen extends ConsumerWidget {
  final Field field;

  const MyFieldScreen({super.key, required this.field});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Full mode (expandable)
            FieldHealthWidget(field: field),
          ],
        ),
      ),
    );
  }
}
```

### Compact Mode

Use compact mode for lists or grid views:

```dart
// In a ListView
ListView.builder(
  itemBuilder: (context, index) {
    return FieldHealthWidget(
      field: fields[index],
      compact: true,  // Compact mode
    );
  },
)

// In a GridView
GridView.builder(
  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
    crossAxisCount: 2,
    childAspectRatio: 1.5,
  ),
  itemBuilder: (context, index) {
    return FieldHealthWidget(
      field: fields[index],
      compact: true,
    );
  },
)
```

### Integration with Providers

```dart
class FieldDetailsScreen extends ConsumerWidget {
  final String fieldId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final fieldsState = ref.watch(fieldsStreamProvider(tenantId));

    return fieldsState.when(
      data: (fields) {
        final field = fields.firstWhere((f) => f.id == fieldId);
        return FieldHealthWidget(field: field);
      },
      loading: () => CircularProgressIndicator(),
      error: (error, stack) => ErrorWidget(error),
    );
  }
}
```

## Architecture

### Data Flow

```
Field Entity
    ↓
FieldHealthWidget
    ↓
_calculateHealthData()
    ↓
FieldHealthData
    ↓
UI Components
```

### Health Score Calculation

The overall health score is calculated using a weighted average:

- **NDVI**: 50% (vegetation health)
- **Tasks**: 20% (task completion rate)
- **Irrigation**: 15% (water management)
- **Weather**: 15% (environmental conditions)

```dart
overallScore = (ndviScore * 0.5) +
               (tasksScore * 0.2) +
               (irrigationScore * 0.15) +
               (weatherScore * 0.15)
```

### Health Status Levels

| Score Range | Status | Color | Arabic |
|------------|--------|-------|--------|
| 80-100 | Excellent | Green | ممتاز |
| 60-79 | Good | Light Green | جيد |
| 40-59 | Moderate | Orange | متوسط |
| 0-39 | Poor | Red | ضعيف |

## Customization

### Theme Integration

The widget automatically adapts to your app's theme:

```dart
// Light theme
ThemeData.light() → White background, dark text

// Dark theme
ThemeData.dark() → Dark background, light text
```

### Color Customization

Colors are defined in `sahool_theme.dart`:

```dart
// Health colors
SahoolColors.healthExcellent  // #2E7D32
SahoolColors.healthGood       // #4CAF50
SahoolColors.healthModerate   // #FF9800
SahoolColors.healthPoor       // #F44336
```

### Recommendation Types

```dart
enum RecommendationType {
  irrigation,      // Water management
  fertilization,   // Nutrient application
  pestControl,     // Pest/disease management
  monitoring,      // Regular inspections
  harvesting,      // Harvest timing
}
```

### Priority Levels

```dart
enum RecommendationPriority {
  high,    // Urgent action required
  medium,  // Action needed soon
  low,     // Optional improvement
}
```

## API Integration

### Required Data

The widget expects a `Field` entity with:

```dart
class Field {
  final String id;
  final String name;
  final String? cropType;
  final double ndviCurrent;      // NDVI value (0.0-1.0)
  final DateTime? ndviUpdatedAt; // Last NDVI update
  final int pendingTasks;        // Number of pending tasks
  // ... other fields
}
```

### Optional Integrations

#### 1. Irrigation Data

Connect to your irrigation system:

```dart
int _getIrrigationScore() {
  final status = ref.watch(irrigationProvider(field.id));
  // Calculate score based on soil moisture, schedule, etc.
  return calculateScore(status);
}
```

#### 2. Weather Data

Connect to weather API:

```dart
int _getWeatherScore() {
  final weather = ref.watch(weatherProvider(field.location));
  // Calculate score based on temperature, rainfall, etc.
  return calculateScore(weather);
}
```

#### 3. Historical Trends

Compare with historical data:

```dart
HealthTrend _calculateTrend(Field field) {
  final history = ref.watch(ndviHistoryProvider(field.id));
  final change = field.ndviCurrent - history.last30DaysAverage;

  if (change > 0.05) return HealthTrend.up;
  if (change < -0.05) return HealthTrend.down;
  return HealthTrend.stable;
}
```

## Navigation & Actions

### Task Creation

When user taps "Create Task" on a recommendation:

```dart
// Navigate to task creation screen with pre-filled data
context.push('/tasks/create', extra: {
  'fieldId': field.id,
  'title': recommendation.titleArabic,
  'description': recommendation.descriptionArabic,
  'priority': recommendation.priority,
});
```

### Required Routes

Ensure these routes are configured in your router:

```dart
GoRouter(
  routes: [
    GoRoute(
      path: '/tasks/create',
      builder: (context, state) => CreateTaskScreen(
        initialData: state.extra as Map<String, dynamic>?,
      ),
    ),
  ],
);
```

## Testing

### Unit Tests

```dart
void main() {
  group('FieldHealthWidget', () {
    testWidgets('displays health score', (tester) async {
      final field = Field(/* ... */);

      await tester.pumpWidget(
        MaterialApp(
          home: FieldHealthWidget(field: field),
        ),
      );

      expect(find.text('72'), findsOneWidget);
    });

    testWidgets('expands on tap', (tester) async {
      final field = Field(/* ... */);

      await tester.pumpWidget(
        MaterialApp(
          home: FieldHealthWidget(field: field),
        ),
      );

      // Initially collapsed
      expect(find.text('التوصيات'), findsNothing);

      // Tap to expand
      await tester.tap(find.byType(InkWell).first);
      await tester.pumpAndSettle();

      // Now expanded
      expect(find.text('التوصيات'), findsOneWidget);
    });
  });
}
```

### Widget Tests

See `field_health_widget_example.dart` for usage examples.

## Performance Considerations

### Optimization Tips

1. **Use `const` constructors** where possible
2. **Avoid rebuilding** when field data hasn't changed
3. **Lazy load** recommendations (only calculate when expanded)
4. **Cache** health calculations for short periods
5. **Use `AutomaticKeepAliveClientMixin`** in lists

### Example Optimization

```dart
class OptimizedFieldList extends StatefulWidget {
  @override
  State<OptimizedFieldList> createState() => _OptimizedFieldListState();
}

class _OptimizedFieldListState extends State<OptimizedFieldList>
    with AutomaticKeepAliveClientMixin {

  @override
  bool get wantKeepAlive => true;

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return ListView.builder(
      itemBuilder: (context, index) {
        return FieldHealthWidget(
          field: fields[index],
          compact: true,
        );
      },
    );
  }
}
```

## Accessibility

### Screen Reader Support

All elements have semantic labels:

```dart
Semantics(
  label: 'Field health score: ${healthData.score} out of 100',
  child: CircularProgressIndicator(/* ... */),
)
```

### Touch Targets

Minimum touch target size is 48x48 pixels:

```dart
// Alert badge
Container(
  padding: EdgeInsets.all(8),  // Ensures 48px+ touch target
  child: Badge(/* ... */),
)
```

## Troubleshooting

### Common Issues

#### 1. Widget not displaying

**Problem**: Widget shows blank or error

**Solution**: Ensure Field entity has valid data:
```dart
// Check NDVI value
assert(field.ndviCurrent >= 0 && field.ndviCurrent <= 1);

// Check pending tasks
assert(field.pendingTasks >= 0);
```

#### 2. Recommendations not showing

**Problem**: Expanded view has no recommendations

**Solution**: Check health score calculation:
```dart
final healthData = _calculateHealthData(field);
print('Health score: ${healthData.score}');
print('Recommendations: ${healthData.recommendations.length}');
```

#### 3. Task creation not working

**Problem**: Tap on "Create Task" does nothing

**Solution**: Verify route is configured:
```dart
// In router configuration
GoRoute(path: '/tasks/create', builder: /* ... */),
```

## Best Practices

### 1. Data Freshness

Update NDVI data regularly:

```dart
// Refresh every 3 days
if (field.ndviUpdatedAt.difference(DateTime.now()).inDays > 3) {
  ref.read(fieldsProvider.notifier).refreshNdvi(field.id);
}
```

### 2. Error Handling

Gracefully handle missing data:

```dart
final ndviValue = field.ndviCurrent ?? 0.0;
final pendingTasks = field.pendingTasks ?? 0;
```

### 3. Performance

Use compact mode in lists:

```dart
// ✅ Good - compact mode
ListView.builder(
  itemBuilder: (context, index) => FieldHealthWidget(
    field: fields[index],
    compact: true,
  ),
)

// ❌ Bad - full mode in list
ListView.builder(
  itemBuilder: (context, index) => FieldHealthWidget(
    field: fields[index],
  ),
)
```

## Roadmap

### Planned Features

- [ ] Historical trend chart
- [ ] Weather forecast integration
- [ ] Soil moisture sensors
- [ ] Custom recommendation rules
- [ ] Export health reports
- [ ] Push notifications for alerts
- [ ] Offline mode support
- [ ] Multi-field comparison

## Contributing

See the main project CONTRIBUTING.md for guidelines.

## License

Part of the SAHOOL Unified Platform.

## Support

For issues or questions:
- GitHub Issues: [sahool-unified-v15-idp/issues]
- Documentation: [docs/field-health-widget.md]
- Email: support@sahool.com

---

**Version**: 1.0.0
**Last Updated**: 2026-01-05
**Author**: SAHOOL Development Team
