# Spray Advisor Feature - مستشار الرش

## Overview - نظرة عامة

The Spray Advisor feature provides farmers with intelligent recommendations for optimal spray timing, product selection, and application tracking. It integrates weather data to suggest the best spray windows and helps farmers log their spray applications.

## Features - المميزات

### 1. **Dashboard** - لوحة المعلومات

- Current weather conditions display
- Next 7-day spray windows timeline
- Active spray recommendations
- Quick actions (log spray, view calendar, history, products)

### 2. **Calendar View** - عرض التقويم

- Monthly calendar with color-coded spray windows:
  - **Green**: Optimal spray conditions
  - **Orange**: Caution - check conditions
  - **Red**: Avoid spraying
- Tap any day to see detailed spray windows
- Visual timeline for selected day

### 3. **Spray Log** - سجل الرش

- Form to log spray applications
- Product selection by spray type
- Rate, area, and application date
- Photo upload (camera/gallery)
- Current weather conditions display
- Links to recommendations

## File Structure - هيكل الملفات

```
lib/features/spray/
├── models/
│   └── spray_models.dart          # Data models
├── services/
│   └── spray_service.dart         # API service layer
├── providers/
│   └── spray_provider.dart        # Riverpod state management
├── screens/
│   ├── spray_dashboard_screen.dart    # Main dashboard
│   ├── spray_calendar_screen.dart     # Calendar view
│   └── spray_log_screen.dart          # Log application form
└── widgets/
    ├── weather_card_widget.dart       # Weather display
    └── spray_window_card.dart         # Spray window display
```

## Models - النماذج

### SprayType Enum

- `herbicide` - مبيد أعشاب
- `fungicide` - مبيد فطري
- `insecticide` - مبيد حشري
- `foliar` - سماد ورقي

### SprayWindowStatus Enum

- `optimal` - مثالي
- `caution` - حذر
- `avoid` - تجنب

### RecommendationStatus Enum

- `active` - نشط
- `completed` - مكتمل
- `expired` - منتهي
- `cancelled` - ملغي

### Main Models

1. **WeatherCondition** - الظروف الجوية
   - Temperature, humidity, wind speed, rain probability
   - Spray suitability score (0-100)

2. **SprayProduct** - منتج الرش
   - Product details (name, manufacturer, active ingredient)
   - Recommended rates (min, max, recommended)
   - PHI (Pre-Harvest Interval) and REI (Re-Entry Interval)
   - Yemen-specific products flag

3. **SprayWindow** - نافذة الرش
   - Time range (start/end)
   - Status (optimal/caution/avoid)
   - Weather conditions
   - Confidence score
   - Warnings

4. **SprayRecommendation** - توصية الرش
   - Spray type and product recommendations
   - Target date and priority
   - Optimal spray windows
   - Estimated costs

5. **SprayApplicationLog** - سجل تطبيق الرش
   - Applied product and rate
   - Area covered
   - Weather conditions during application
   - Photos and notes

## API Endpoints

The service communicates with a backend spray advisor API (port 8098). Main endpoints:

### Recommendations

- `GET /v1/spray/recommendations` - Get spray recommendations
- `POST /v1/spray/recommendations` - Create recommendation
- `PUT /v1/spray/recommendations/:id/status` - Update status

### Spray Windows

- `GET /v1/spray/windows` - Get optimal spray windows
- `GET /v1/spray/windows/:id` - Get specific window

### Weather

- `GET /v1/spray/weather/current` - Current weather
- `GET /v1/spray/weather/forecast` - Weather forecast

### Products

- `GET /v1/spray/products` - Get spray products
- `GET /v1/spray/products/:id` - Get product details

### Logs

- `POST /v1/spray/logs` - Log spray application
- `GET /v1/spray/logs` - Get spray logs
- `POST /v1/spray/upload` - Upload photo

## Dependencies - التبعيات

Add these packages to your `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_riverpod: ^2.4.0
  dio: ^5.3.2
  intl: ^0.18.1
  table_calendar: ^3.0.9 # For calendar view
  image_picker: ^1.0.4 # For photo upload
```

Then run:

```bash
flutter pub get
```

## Setup - الإعداد

### 1. Update API Config

The API configuration has been updated in `/home/user/sahool-unified-v15-idp/apps/mobile/lib/core/config/api_config.dart`:

- Added `spray` service port (8098)
- Added `sprayServiceUrl` getter
- Added spray service to health checks

### 2. Backend Integration

Ensure the Spray Advisor backend service is running on port 8098. The service should implement all the endpoints listed above.

### 3. Yemen-Specific Products

The system supports Yemen-specific agricultural products. Populate the backend database with:

- Local pesticides and fertilizers
- Arabic translations for product names
- Local manufacturer information

## Usage Examples - أمثلة الاستخدام

### Opening the Dashboard

```dart
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (_) => SprayDashboardScreen(fieldId: 'field_123'),
  ),
);
```

### Opening the Calendar

```dart
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (_) => SprayCalendarScreen(fieldId: 'field_123'),
  ),
);
```

### Logging a Spray Application

```dart
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (_) => SprayLogScreen(
      fieldId: 'field_123',
      recommendationId: 'rec_456', // Optional
    ),
  ),
);
```

### Using Providers Directly

```dart
// Get current weather
final weatherAsync = ref.watch(currentWeatherProvider('field_123'));

// Get spray windows
final windowsAsync = ref.watch(sprayWindowsProvider(
  SprayWindowParams(fieldId: 'field_123', days: 7),
));

// Get recommendations
final recommendationsAsync = ref.watch(sprayRecommendationsProvider(
  SprayRecommendationFilter(
    fieldId: 'field_123',
    status: RecommendationStatus.active,
  ),
));

// Log spray application
final controller = ref.read(sprayControllerProvider.notifier);
final log = await controller.logSprayApplication(
  fieldId: 'field_123',
  sprayType: SprayType.insecticide,
  productId: 'product_789',
  appliedRate: 2.5,
  unit: 'L/ha',
  area: 5.0,
  applicationDate: DateTime.now(),
);
```

## Localization - الترجمة

The feature supports both Arabic and English:

- All UI text is bilingual
- Models include both `name` and `nameAr` fields
- Weather conditions, product names, and warnings are localized
- Date/time formatting respects locale

## Features to Implement - مميزات للتنفيذ

The following features are referenced but need implementation:

1. Navigation between screens (currently commented out)
2. Detailed recommendation view
3. Product catalog screen
4. Spray history list view
5. Integration with field selection
6. Push notifications for optimal spray windows
7. Offline caching for recommendations and weather data

## Testing - الاختبار

### Mock Data

For testing without a backend, you can create mock providers:

```dart
// In your test file or development mode
final mockWeatherProvider = Provider<WeatherCondition>((ref) {
  return WeatherCondition(
    conditionId: 'test_1',
    timestamp: DateTime.now(),
    temperature: 22.0,
    humidity: 60.0,
    windSpeed: 10.0,
    windDirection: 'N',
    windDirectionAr: 'شمال',
    rainProbability: 5.0,
    condition: 'clear',
    conditionAr: 'صافي',
  );
});
```

## Best Practices - أفضل الممارسات

1. **Always check spray windows** before application
2. **Log all spray applications** for record-keeping and compliance
3. **Use recommended products** from the database
4. **Respect PHI and REI** intervals
5. **Take photos** of applications for documentation
6. **Review weather conditions** before spraying

## Troubleshooting - استكشاف الأخطاء

### Common Issues

1. **"Failed to load weather data"**
   - Check internet connection
   - Verify backend service is running on port 8098
   - Check field coordinates are valid

2. **"No spray windows available"**
   - Weather data may be unavailable
   - All conditions may be unsuitable for spraying
   - Extend the forecast period

3. **Photo upload fails**
   - Check camera/gallery permissions
   - Verify image size is within limits
   - Check network connectivity

## Contact

For questions or issues, contact the development team.

---

**Version**: 1.0.0
**Last Updated**: 2025-12-26
**Platform**: Flutter
**Minimum SDK**: Flutter 3.0+
