# Crop Rotation Feature

A comprehensive Flutter feature for managing crop rotation plans with focus on Yemen agricultural practices.

## Overview

The Crop Rotation feature helps farmers optimize their planting schedules by:

- **Planning multi-year rotations** with different crop families
- **Analyzing soil health** trends over time
- **Checking crop compatibility** to avoid diseases and pests
- **Maximizing soil fertility** through strategic crop sequencing
- **Supporting Yemen crops**: قمح، ذرة رفيعة، بن، قات، طماطم، بصل، فول

## Features

### 1. **Rotation Plan Screen** (`rotation_plan_screen.dart`)

- Multi-year rotation view with timeline
- Year-by-year crop selection
- Soil health indicators (before/after planting)
- Compatibility warnings
- Generate new rotation plans with preferences

### 2. **Rotation Calendar Screen** (`rotation_calendar_screen.dart`)

- Timeline view of rotation plan
- Visual distinction between past, current, and future rotations
- Planting and harvest dates
- Crop details and yield information

### 3. **Crop Compatibility Screen** (`crop_compatibility_screen.dart`)

- Interactive compatibility matrix
- Color-coded compatibility ratings (green=good, red=avoid)
- Detailed compatibility explanations in English and Arabic
- Select two crops to check their compatibility

### 4. **Soil Health Chart Widget** (`soil_health_chart.dart`)

- Radar chart visualization of N, P, K, organic matter, water retention
- Trend indicators showing improvement/decline over time
- pH level indicator with visual scale
- Overall soil health score

### 5. **Rotation Timeline Widget** (`rotation_timeline_widget.dart`)

- Horizontal scrolling timeline
- Crop icons with family-specific colors
- Season indicators
- Current year highlighting

## Data Models

### Crop Families (15 families)

1. **Solanaceae** (الباذنجانيات) - Tomatoes, Potatoes, Peppers
2. **Fabaceae** (البقوليات) - Fava Beans, Lentils, Peas - _Nitrogen fixers!_
3. **Poaceae** (النجيليات) - Wheat, Sorghum, Corn
4. **Brassicaceae** (الصليبيات) - Cabbage, Broccoli, Cauliflower
5. **Cucurbitaceae** (القرعيات) - Cucumber, Squash, Melon
6. **Amaranthaceae** (القطيفيات) - Beet, Spinach, Chard
7. **Apiaceae** (الخيميات) - Carrot, Celery, Parsley
8. **Alliaceae** (الثومیات) - Onion, Garlic, Leek
9. **Asteraceae** (النجميات) - Lettuce, Sunflower
10. **Malvaceae** (الخبازيات) - Cotton, Okra
11. **Convolvulaceae** (العليقيات) - Sweet Potato
12. **Rubiaceae** (الفوية) - Coffee (بن)
13. **Celastraceae** (القاتيات) - Qat (قات)
14. **Rosaceae** (الورديات) - Strawberry, Apple
15. **Lamiaceae** (الشفويات) - Basil, Mint

### Yemen-Specific Crops

- **قمح (Wheat)** - Poaceae family, 120 days, Winter season
- **ذرة رفيعة (Sorghum)** - Poaceae family, 100 days, Summer season
- **بن (Coffee)** - Rubiaceae family, Perennial
- **قات (Qat)** - Celastraceae family, Perennial
- **طماطم (Tomato)** - Solanaceae family, 90 days, Spring season
- **بصل (Onion)** - Alliaceae family, 110 days, Winter season
- **فول (Fava Beans)** - Fabaceae family, 90 days, Winter season

### Rotation Principles

#### Excellent Compatibility (90%+)

- Legume → Heavy Feeder (e.g., Fava Beans → Tomato)
- Heavy Feeder → Legume (e.g., Tomato → Fava Beans)

#### Good Compatibility (70-89%)

- Different families with diverse nutrient needs
- Light feeder after heavy feeder

#### Poor Compatibility (<50%)

- Same family in consecutive years
- Increases disease and pest pressure

## Usage

### Basic Usage

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'features/rotation/rotation_feature.dart';

// Navigate to rotation plan
void showRotationPlan(BuildContext context, String fieldId) {
  Navigator.push(
    context,
    MaterialPageRoute(
      builder: (context) => RotationPlanScreen(fieldId: fieldId),
    ),
  );
}

// Navigate to compatibility matrix
void showCompatibilityMatrix(BuildContext context) {
  Navigator.push(
    context,
    MaterialPageRoute(
      builder: (context) => const CropCompatibilityScreen(),
    ),
  );
}
```

### Using Providers

```dart
// Get rotation plan for a field
final planAsync = ref.watch(rotationPlanProvider('field_123'));

planAsync.when(
  data: (plan) {
    // Use rotation plan
    print('Total years: ${plan.totalYears}');
    print('Current crop: ${plan.currentRotation?.crop?.nameEn}');
  },
  loading: () => CircularProgressIndicator(),
  error: (error, stack) => Text('Error: $error'),
);

// Get soil health trend
final trendAsync = ref.watch(soilHealthTrendProvider('field_123'));

// Get crop recommendations
final recommendationsAsync = ref.watch(
  recommendedCropsProvider(
    RecommendedCropsParams(
      fieldId: 'field_123',
      year: 2024,
    ),
  ),
);

// Check crop compatibility
final compatibilityAsync = ref.watch(
  cropCompatibilityProvider(
    CropCompatibilityParams(
      crop1: YemenCrops.crops[0], // Wheat
      crop2: YemenCrops.crops[6], // Fava Beans
    ),
  ),
);
```

### Generating Custom Rotation Plans

```dart
final notifier = ref.read(rotationPlanNotifierProvider.notifier);

await notifier.generatePlan(
  'field_123',
  5, // number of years
  {
    'prioritizeSoilHealth': true,
    'includeNitrogenFixers': true,
    'avoidSameFamily': true,
    'rotationCycleYears': 5,
  },
);

// The generated plan will be available in the provider
final generatedPlan = ref.watch(rotationPlanNotifierProvider);
```

## Architecture

```
rotation/
├── models/
│   └── rotation_models.dart          # Data models and entities
├── services/
│   └── rotation_service.dart         # Business logic and API calls
├── providers/
│   └── rotation_provider.dart        # Riverpod state management
├── screens/
│   ├── rotation_plan_screen.dart     # Main rotation planning UI
│   ├── rotation_calendar_screen.dart # Timeline view
│   └── crop_compatibility_screen.dart # Compatibility matrix
├── widgets/
│   ├── rotation_timeline_widget.dart # Horizontal timeline
│   └── soil_health_chart.dart        # Radar chart visualization
└── rotation_feature.dart             # Public API exports
```

## Key Components

### Models

- `CropFamily` - Enum with 15 crop families
- `CropFamilyInfo` - Metadata for each family
- `Crop` - Individual crop information
- `RotationYear` - Crop rotation for one year
- `RotationPlan` - Complete multi-year plan
- `SoilHealth` - N, P, K, pH, organic matter, water retention
- `CompatibilityScore` - Compatibility between two crops
- `CropRecommendation` - Recommended crops with scores

### Services

- `RotationService` - Main service class with methods:
  - `getRotationPlan(fieldId)` - Fetch existing plan
  - `generateRotationPlan(fieldId, years, preferences)` - Generate new plan
  - `getCropCompatibility(crop1, crop2)` - Check compatibility
  - `getSoilHealthTrend(fieldId)` - Get historical soil data
  - `getRecommendedCrops(fieldId, year)` - Get suggestions

### Providers

- `rotationPlanProvider` - Fetch rotation plan
- `soilHealthTrendProvider` - Get soil health history
- `cropCompatibilityProvider` - Check crop compatibility
- `recommendedCropsProvider` - Get crop recommendations
- `compatibilityMatrixProvider` - Full compatibility matrix
- `rotationPlanNotifierProvider` - Generate and manage plans

## Best Practices

### Rotation Guidelines

1. **Diversify crop families** - Never plant the same family consecutively
2. **Include nitrogen fixers** - Plant legumes every 2-3 years
3. **Follow heavy feeders with light feeders** - Or nitrogen fixers
4. **Monitor soil health** - Track N, P, K levels regularly
5. **Respect rotation cycles** - Most families need 2-4 year gaps

### Soil Health Management

- **Nitrogen (N)** - Depleted by heavy feeders, fixed by legumes
- **Phosphorus (P)** - Slowly depleted, replenish regularly
- **Potassium (K)** - Important for fruit crops
- **Organic Matter** - Increases with crop residues
- **pH** - Maintain between 6.0-7.5 for most crops

## Future Enhancements

- [ ] Integration with actual field data from backend API
- [ ] Weather-based planting recommendations
- [ ] Pest and disease risk prediction
- [ ] Yield optimization using ML models
- [ ] Market price integration for crop selection
- [ ] Community rotation plan sharing
- [ ] Irrigation scheduling based on rotation
- [ ] Fertilizer recommendations per rotation stage

## Dependencies

Required packages (add to `pubspec.yaml`):

```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_riverpod: ^2.4.0
```

## Testing

```dart
// Example test
void main() {
  test('Crop compatibility calculation', () async {
    final service = RotationService();
    final wheat = YemenCrops.crops.firstWhere((c) => c.id == 'wheat');
    final fava = YemenCrops.crops.firstWhere((c) => c.id == 'fava_beans');

    final compatibility = await service.getCropCompatibility(wheat, fava);

    expect(compatibility.score, greaterThan(0.7));
    expect(compatibility.level, 'Good');
  });
}
```

## License

Part of Sahool Unified v15 IDP

---

**Note**: This feature currently uses simulated data. Connect to your backend API by implementing the service methods in `rotation_service.dart`.
