# Field Health Widget - Integration Guide

## Quick Start

This guide will help you integrate the Field Health Widget into your existing SAHOOL mobile app screens.

## Prerequisites

✅ Flutter SDK installed
✅ Project dependencies installed (`flutter pub get`)
✅ Field entity available in your app
✅ Riverpod providers configured

## Step-by-Step Integration

### Step 1: Import the Widget

Add the import to your screen file:

```dart
import 'package:mobile/features/field/presentation/widgets/field_health_widget.dart';
```

### Step 2: Add to Field Details Screen

**File**: `/lib/features/field/ui/field_details_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../presentation/widgets/field_health_widget.dart';

class FieldDetailsScreen extends ConsumerWidget {
  final String fieldId;

  const FieldDetailsScreen({super.key, required this.fieldId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get field data from your existing provider
    final fieldsState = ref.watch(fieldsStreamProvider('your-tenant-id'));

    return Scaffold(
      appBar: AppBar(title: const Text('تفاصيل الحقل')),
      body: fieldsState.when(
        data: (fields) {
          final field = fields.firstWhere((f) => f.id == fieldId);

          return SingleChildScrollView(
            child: Column(
              children: [
                const SizedBox(height: 16),

                // 🎯 Add the Field Health Widget here
                FieldHealthWidget(field: field),

                const SizedBox(height: 16),

                // ... your other widgets ...
              ],
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(child: Text('Error: $error')),
      ),
    );
  }
}
```

### Step 3: Add to Fields List Screen

**File**: `/lib/features/field/ui/fields_list_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../presentation/widgets/field_health_widget.dart';

class FieldsListScreen extends ConsumerWidget {
  const FieldsListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final fieldsState = ref.watch(fieldsStreamProvider('your-tenant-id'));

    return Scaffold(
      appBar: AppBar(title: const Text('حقولي')),
      body: fieldsState.when(
        data: (fields) => ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: fields.length,
          itemBuilder: (context, index) {
            final field = fields[index];

            return Column(
              children: [
                // Field header card
                _buildFieldHeader(context, field),

                // 🎯 Add compact health widget
                FieldHealthWidget(
                  field: field,
                  compact: true,  // Use compact mode in lists
                ),

                const SizedBox(height: 16),
              ],
            );
          },
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(child: Text('Error: $error')),
      ),
    );
  }

  Widget _buildFieldHeader(BuildContext context, Field field) {
    return Card(
      child: ListTile(
        leading: Icon(Icons.agriculture_rounded),
        title: Text(field.name),
        subtitle: Text(field.cropType ?? 'غير محدد'),
        trailing: Icon(Icons.chevron_left_rounded),
        onTap: () {
          // Navigate to field details
        },
      ),
    );
  }
}
```

### Step 4: Add to Home Dashboard

**File**: `/lib/features/home/ui/home_dashboard_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../field/presentation/widgets/field_health_widget.dart';

class HomeDashboardScreen extends ConsumerWidget {
  const HomeDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final fieldsState = ref.watch(fieldsStreamProvider('your-tenant-id'));

    return Scaffold(
      appBar: AppBar(title: const Text('لوحة التحكم')),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 16),

            // Section: Fields Needing Attention
            fieldsState.when(
              data: (fields) {
                final criticalFields = fields
                    .where((f) => f.needsAttention)
                    .toList();

                if (criticalFields.isEmpty) {
                  return const SizedBox();
                }

                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Row(
                        children: [
                          Icon(Icons.warning_amber_rounded,
                               color: Colors.orange),
                          const SizedBox(width: 8),
                          Text(
                            'حقول تحتاج انتباه',
                            style: Theme.of(context)
                                .textTheme
                                .titleMedium
                                ?.copyWith(fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),

                    // 🎯 Horizontal scrolling health widgets
                    SizedBox(
                      height: 200,
                      child: ListView.builder(
                        scrollDirection: Axis.horizontal,
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        itemCount: criticalFields.length,
                        itemBuilder: (context, index) {
                          return SizedBox(
                            width: MediaQuery.of(context).size.width - 32,
                            child: FieldHealthWidget(
                              field: criticalFields[index],
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                );
              },
              loading: () => const SizedBox(),
              error: (_, __) => const SizedBox(),
            ),

            const SizedBox(height: 24),

            // ... other dashboard sections ...
          ],
        ),
      ),
    );
  }
}
```

## Advanced Integration

### 1. Custom Task Creation

Override the task creation behavior:

```dart
class CustomFieldHealthWidget extends FieldHealthWidget {
  const CustomFieldHealthWidget({
    super.key,
    required super.field,
    super.compact,
  });

  @override
  Future<void> _createTaskFromRecommendation(
    BuildContext context,
    HealthRecommendation recommendation,
  ) async {
    // Your custom task creation logic
    final taskService = ref.read(taskServiceProvider);

    await taskService.createTask(
      fieldId: field.id,
      title: recommendation.titleArabic,
      description: recommendation.descriptionArabic,
      priority: recommendation.priority,
      dueDate: DateTime.now().add(const Duration(days: 7)),
    );

    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('تم إنشاء المهمة بنجاح')),
      );
    }
  }
}
```

### 2. Custom Recommendations

Provide your own recommendations:

```dart
List<HealthRecommendation> _generateCustomRecommendations(Field field) {
  final recommendations = <HealthRecommendation>[];

  // Add custom business logic
  if (field.cropType == 'قمح' && field.ndvi < 0.5) {
    recommendations.add(
      HealthRecommendation(
        type: RecommendationType.fertilization,
        priority: RecommendationPriority.high,
        titleArabic: 'تسميد القمح',
        titleEnglish: 'Wheat Fertilization',
        descriptionArabic: 'يحتاج محصول القمح إلى تسميد نيتروجيني',
        descriptionEnglish: 'Wheat crop needs nitrogen fertilization',
        icon: Icons.science_rounded,
        canCreateTask: true,
      ),
    );
  }

  return recommendations;
}
```

### 3. Real-time Updates

Listen to field changes and update widget:

```dart
class RealTimeFieldHealthWidget extends ConsumerWidget {
  final String fieldId;

  const RealTimeFieldHealthWidget({
    super.key,
    required this.fieldId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Watch for real-time updates
    final fieldStream = ref.watch(
      singleFieldStreamProvider(fieldId),
    );

    return fieldStream.when(
      data: (field) => FieldHealthWidget(field: field),
      loading: () => const CircularProgressIndicator(),
      error: (error, stack) => Text('Error: $error'),
    );
  }
}

// Provider for single field stream
final singleFieldStreamProvider =
    StreamProvider.family<Field, String>((ref, fieldId) {
  final repo = ref.watch(fieldsRepoProvider);
  return repo.watchField(fieldId);
});
```

### 4. Analytics Integration

Track widget interactions:

```dart
class AnalyticsFieldHealthWidget extends FieldHealthWidget {
  const AnalyticsFieldHealthWidget({
    super.key,
    required super.field,
    super.compact,
  });

  @override
  void _toggleExpanded() {
    super._toggleExpanded();

    // Track expansion
    AnalyticsService.logEvent(
      'field_health_expanded',
      parameters: {
        'field_id': field.id,
        'health_score': _calculateHealthData(field).score,
      },
    );
  }

  @override
  Future<void> _createTaskFromRecommendation(
    BuildContext context,
    HealthRecommendation recommendation,
  ) async {
    // Track task creation
    AnalyticsService.logEvent(
      'task_created_from_recommendation',
      parameters: {
        'field_id': field.id,
        'recommendation_type': recommendation.type.toString(),
        'priority': recommendation.priority.toString(),
      },
    );

    await super._createTaskFromRecommendation(context, recommendation);
  }
}
```

## Styling Customization

### Custom Colors

Override health colors in your theme:

```dart
// In sahool_theme.dart
class CustomSahoolColors extends SahoolColors {
  static const Color healthExcellent = Color(0xFF00C853);
  static const Color healthGood = Color(0xFF64DD17);
  static const Color healthModerate = Color(0xFFFFAB00);
  static const Color healthPoor = Color(0xFFDD2C00);
}
```

### Custom Dimensions

Modify widget sizes:

```dart
// Larger circular progress
SizedBox(
  width: 120,  // Default: 100
  height: 120, // Default: 100
  child: CircularProgressIndicator(/* ... */),
)

// Custom mini indicator size
Container(
  padding: const EdgeInsets.all(12),  // Default: 10
  child: Icon(icon, size: 24),        // Default: 20
)
```

## Testing

### Widget Test Example

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  testWidgets('FieldHealthWidget displays correctly', (tester) async {
    final mockField = Field(
      id: 'test-1',
      tenantId: 'tenant-1',
      name: 'Test Field',
      ndviCurrent: 0.75,
      pendingTasks: 2,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          home: Scaffold(
            body: FieldHealthWidget(field: mockField),
          ),
        ),
      ),
    );

    // Verify health score is displayed
    expect(find.text('75'), findsOneWidget);

    // Verify NDVI value is displayed
    expect(find.text('0.75'), findsOneWidget);

    // Verify pending tasks count
    expect(find.text('2'), findsOneWidget);
  });

  testWidgets('Expands on tap', (tester) async {
    final mockField = Field(/* ... */);

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          home: Scaffold(
            body: FieldHealthWidget(field: mockField),
          ),
        ),
      ),
    );

    // Find and tap the widget
    await tester.tap(find.byType(InkWell).first);
    await tester.pumpAndSettle();

    // Verify recommendations section is visible
    expect(find.text('التوصيات / Recommendations'), findsOneWidget);
  });
}
```

## Troubleshooting

### Issue: Widget not displaying

**Symptom**: Widget appears blank or throws error

**Solution**: Check field data validity
```dart
// Ensure NDVI is in valid range
assert(field.ndviCurrent >= 0 && field.ndviCurrent <= 1);

// Ensure pending tasks is non-negative
assert(field.pendingTasks >= 0);
```

### Issue: Task creation fails

**Symptom**: Tapping "Create Task" does nothing

**Solution**: Configure task creation route
```dart
// In your router configuration
GoRoute(
  path: '/tasks/create',
  builder: (context, state) {
    final extra = state.extra as Map<String, dynamic>?;
    return CreateTaskScreen(initialData: extra);
  },
),
```

### Issue: Performance issues in lists

**Symptom**: List scrolling is laggy

**Solution**: Always use compact mode in lists
```dart
// ✅ Good
ListView.builder(
  itemBuilder: (context, index) => FieldHealthWidget(
    field: fields[index],
    compact: true,  // Compact mode
  ),
)

// ❌ Bad
ListView.builder(
  itemBuilder: (context, index) => FieldHealthWidget(
    field: fields[index],  // Full mode in list
  ),
)
```

## Next Steps

1. ✅ Integrate widget into your screens
2. ✅ Test with real field data
3. ✅ Customize colors and styling
4. ✅ Add analytics tracking
5. ✅ Connect to real irrigation/weather APIs
6. ✅ Implement historical trend tracking

## Support

- **Documentation**: See README.md for detailed API docs
- **Examples**: See field_health_widget_example.dart for usage examples
- **Issues**: Report bugs via GitHub Issues

## Resources

- [Field Entity Documentation](../domain/entities/field.dart)
- [SAHOOL Theme Guide](../../../../core/theme/sahool_theme.dart)
- [Task Provider Documentation](../../../tasks/providers/tasks_provider.dart)

---

**Last Updated**: 2026-01-05
**Version**: 1.0.0
