/// Weather Test Fixtures - Mock Data for Weather Tests
/// بيانات وهمية لاختبارات الطقس
///
/// Provides comprehensive mock data for testing weather features including:
/// - Current weather data (بيانات الطقس الحالية)
/// - Forecasts (التوقعات)
/// - Weather alerts (تنبيهات الطقس)
/// - Agricultural impacts (التأثيرات الزراعية)
/// - Arabic descriptions and translations
library;

/// Mock JSON responses for API testing
class WeatherFixtures {
  WeatherFixtures._();

  // ═══════════════════════════════════════════════════════════════════════════
  // Current Weather Data - بيانات الطقس الحالية
  // ═══════════════════════════════════════════════════════════════════════════

  /// Sample current weather JSON response
  static Map<String, dynamic> get currentWeatherJson => {
        'current': {
          'temperature': 28.5,
          'feels_like': 30.2,
          'humidity': 65,
          'wind_speed': 12.5, // km/h
          'wind_direction': 'NW',
          'condition': 'Partly Cloudy',
          'condition_ar': 'غائم جزئياً',
          'icon': '⛅',
          'precipitation': 0.0,
          'uv_index': 7.5,
          'timestamp': '2026-01-23T10:30:00Z',
        },
        'hourly': hourlyForecastsJson,
        'daily': dailyForecastsJson,
        'alerts': weatherAlertsJson,
        'impacts': agriculturalImpactsJson,
      };

  /// Clear weather JSON (صافي)
  static Map<String, dynamic> get clearWeatherJson => {
        'current': {
          'temperature': 35.0,
          'feels_like': 38.0,
          'humidity': 25,
          'wind_speed': 8.0,
          'wind_direction': 'S',
          'condition': 'Clear',
          'condition_ar': 'صافي',
          'icon': '☀️',
          'precipitation': 0.0,
          'uv_index': 9.5,
          'timestamp': '2026-01-23T14:00:00Z',
        },
        'hourly': <dynamic>[],
        'daily': <dynamic>[],
        'alerts': <dynamic>[],
        'impacts': <dynamic>[],
      };

  /// Rainy weather JSON (مطر)
  static Map<String, dynamic> get rainyWeatherJson => {
        'current': {
          'temperature': 18.5,
          'feels_like': 17.0,
          'humidity': 85,
          'wind_speed': 25.0,
          'wind_direction': 'NE',
          'condition': 'Rain',
          'condition_ar': 'مطر',
          'icon': '🌧️',
          'precipitation': 15.5,
          'uv_index': 2.0,
          'timestamp': '2026-01-23T16:00:00Z',
        },
        'hourly': <dynamic>[],
        'daily': <dynamic>[],
        'alerts': [
          {
            'id': 'alert-rain-001',
            'type': 'rain',
            'severity': 'warning',
            'title': 'Heavy Rain Warning',
            'title_ar': 'تحذير من أمطار غزيرة',
            'description': 'Heavy rainfall expected in the next 24 hours',
            'start_time': '2026-01-23T16:00:00Z',
            'end_time': '2026-01-24T16:00:00Z',
          }
        ],
        'impacts': <dynamic>[],
      };

  /// Thunderstorm weather JSON (عاصفة رعدية)
  static Map<String, dynamic> get thunderstormWeatherJson => {
        'current': {
          'temperature': 22.0,
          'feels_like': 20.5,
          'humidity': 90,
          'wind_speed': 45.0,
          'wind_direction': 'W',
          'condition': 'Thunderstorm',
          'condition_ar': 'عاصفة رعدية',
          'icon': '⛈️',
          'precipitation': 35.0,
          'uv_index': 1.0,
          'timestamp': '2026-01-23T18:00:00Z',
        },
        'hourly': <dynamic>[],
        'daily': <dynamic>[],
        'alerts': [
          {
            'id': 'alert-storm-001',
            'type': 'thunderstorm',
            'severity': 'warning',
            'title': 'Severe Thunderstorm Warning',
            'title_ar': 'تحذير من عاصفة رعدية شديدة',
            'description': 'Severe thunderstorms with potential hail',
            'start_time': '2026-01-23T17:00:00Z',
            'end_time': '2026-01-23T23:00:00Z',
          }
        ],
        'impacts': <dynamic>[],
      };

  /// Foggy weather JSON (ضبابي)
  static Map<String, dynamic> get foggyWeatherJson => {
        'current': {
          'temperature': 12.0,
          'feels_like': 10.0,
          'humidity': 95,
          'wind_speed': 3.0,
          'wind_direction': 'E',
          'condition': 'Foggy',
          'condition_ar': 'ضبابي',
          'icon': '🌫️',
          'precipitation': 0.0,
          'uv_index': 0.5,
          'timestamp': '2026-01-23T06:00:00Z',
        },
        'hourly': <dynamic>[],
        'daily': <dynamic>[],
        'alerts': <dynamic>[],
        'impacts': <dynamic>[],
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Hourly Forecasts - التوقعات الساعية
  // ═══════════════════════════════════════════════════════════════════════════

  static List<Map<String, dynamic>> get hourlyForecastsJson => [
        {
          'time': '2026-01-23T11:00:00Z',
          'temperature': 29.0,
          'condition': 'Partly Cloudy',
          'icon': '⛅',
          'precipitation_chance': 10,
          'humidity': 60,
        },
        {
          'time': '2026-01-23T12:00:00Z',
          'temperature': 30.5,
          'condition': 'Partly Cloudy',
          'icon': '⛅',
          'precipitation_chance': 15,
          'humidity': 55,
        },
        {
          'time': '2026-01-23T13:00:00Z',
          'temperature': 32.0,
          'condition': 'Clear',
          'icon': '☀️',
          'precipitation_chance': 5,
          'humidity': 50,
        },
        {
          'time': '2026-01-23T14:00:00Z',
          'temperature': 33.5,
          'condition': 'Clear',
          'icon': '☀️',
          'precipitation_chance': 5,
          'humidity': 45,
        },
        {
          'time': '2026-01-23T15:00:00Z',
          'temperature': 34.0,
          'condition': 'Clear',
          'icon': '☀️',
          'precipitation_chance': 0,
          'humidity': 40,
        },
      ];

  // ═══════════════════════════════════════════════════════════════════════════
  // Daily Forecasts - التوقعات اليومية
  // ═══════════════════════════════════════════════════════════════════════════

  static List<Map<String, dynamic>> get dailyForecastsJson => [
        {
          'date': '2026-01-23',
          'temp_min': 18.0,
          'temp_max': 34.0,
          'condition': 'Partly Cloudy',
          'condition_ar': 'غائم جزئياً',
          'icon': '⛅',
          'precipitation_chance': 10,
          'precipitation_amount': 0.0,
          'humidity': 55,
          'wind_speed': 12.0,
        },
        {
          'date': '2026-01-24',
          'temp_min': 17.0,
          'temp_max': 32.0,
          'condition': 'Clear',
          'condition_ar': 'صافي',
          'icon': '☀️',
          'precipitation_chance': 0,
          'precipitation_amount': 0.0,
          'humidity': 50,
          'wind_speed': 10.0,
        },
        {
          'date': '2026-01-25',
          'temp_min': 16.0,
          'temp_max': 30.0,
          'condition': 'Rain',
          'condition_ar': 'مطر',
          'icon': '🌧️',
          'precipitation_chance': 70,
          'precipitation_amount': 15.0,
          'humidity': 75,
          'wind_speed': 20.0,
        },
        {
          'date': '2026-01-26',
          'temp_min': 15.0,
          'temp_max': 28.0,
          'condition': 'Cloudy',
          'condition_ar': 'غائم',
          'icon': '☁️',
          'precipitation_chance': 30,
          'precipitation_amount': 2.0,
          'humidity': 65,
          'wind_speed': 15.0,
        },
        {
          'date': '2026-01-27',
          'temp_min': 16.0,
          'temp_max': 31.0,
          'condition': 'Clear',
          'condition_ar': 'صافي',
          'icon': '☀️',
          'precipitation_chance': 0,
          'precipitation_amount': 0.0,
          'humidity': 45,
          'wind_speed': 8.0,
        },
        {
          'date': '2026-01-28',
          'temp_min': 17.0,
          'temp_max': 33.0,
          'condition': 'Clear',
          'condition_ar': 'صافي',
          'icon': '☀️',
          'precipitation_chance': 5,
          'precipitation_amount': 0.0,
          'humidity': 40,
          'wind_speed': 10.0,
        },
        {
          'date': '2026-01-29',
          'temp_min': 18.0,
          'temp_max': 35.0,
          'condition': 'Clear',
          'condition_ar': 'صافي',
          'icon': '☀️',
          'precipitation_chance': 0,
          'precipitation_amount': 0.0,
          'humidity': 35,
          'wind_speed': 12.0,
        },
      ];

  // ═══════════════════════════════════════════════════════════════════════════
  // Weather Alerts - تنبيهات الطقس
  // ═══════════════════════════════════════════════════════════════════════════

  static List<Map<String, dynamic>> get weatherAlertsJson => [
        {
          'id': 'alert-001',
          'type': 'heat',
          'severity': 'warning',
          'title': 'Heat Wave Warning',
          'title_ar': 'تحذير من موجة حر',
          'description':
              'High temperatures expected. Stay hydrated and avoid outdoor activities.',
          'start_time': '2026-01-23T10:00:00Z',
          'end_time': '2026-01-25T18:00:00Z',
        },
        {
          'id': 'alert-002',
          'type': 'wind',
          'severity': 'watch',
          'title': 'Wind Advisory',
          'title_ar': 'إرشاد بشأن الرياح',
          'description':
              'Strong winds expected. Secure loose objects outdoors.',
          'start_time': '2026-01-24T06:00:00Z',
          'end_time': '2026-01-24T20:00:00Z',
        },
      ];

  /// Active weather alert (currently ongoing)
  static Map<String, dynamic> get activeAlertJson => {
        'id': 'alert-active-001',
        'type': 'dust',
        'severity': 'warning',
        'title': 'Dust Storm Warning',
        'title_ar': 'تحذير من عاصفة رملية',
        'description': 'Visibility reduced. Avoid outdoor activities.',
        'start_time': DateTime.now().subtract(const Duration(hours: 2)).toIso8601String(),
        'end_time': DateTime.now().add(const Duration(hours: 6)).toIso8601String(),
      };

  /// Expired weather alert (past endTime)
  static Map<String, dynamic> get expiredAlertJson => {
        'id': 'alert-expired-001',
        'type': 'frost',
        'severity': 'advisory',
        'title': 'Frost Advisory',
        'title_ar': 'إرشاد بشأن الصقيع',
        'description': 'Temperatures may reach freezing overnight.',
        'start_time': DateTime.now().subtract(const Duration(days: 2)).toIso8601String(),
        'end_time': DateTime.now().subtract(const Duration(days: 1)).toIso8601String(),
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Agricultural Impacts - التأثيرات الزراعية
  // ═══════════════════════════════════════════════════════════════════════════

  static List<Map<String, dynamic>> get agriculturalImpactsJson => [
        {
          'category': 'irrigation',
          'recommendation': 'Reduce irrigation by 20% due to expected rainfall',
          'recommendation_ar': 'تقليل الري بنسبة 20% بسبب هطول الأمطار المتوقعة',
          'status': 'caution',
          'reasons': ['Expected rainfall 15mm', 'Soil moisture at 75%'],
        },
        {
          'category': 'spraying',
          'recommendation': 'Good conditions for pesticide application in early morning',
          'recommendation_ar': 'ظروف جيدة لرش المبيدات في الصباح الباكر',
          'status': 'favorable',
          'reasons': ['Low wind speed <10 km/h', 'No rain expected for 48h'],
        },
        {
          'category': 'harvesting',
          'recommendation': 'Postpone harvesting due to rain forecast',
          'recommendation_ar': 'تأجيل الحصاد بسبب توقعات المطر',
          'status': 'unfavorable',
          'reasons': ['Rain forecast in 2 days', 'High humidity expected'],
        },
        {
          'category': 'planting',
          'recommendation': 'Ideal conditions for planting wheat',
          'recommendation_ar': 'ظروف مثالية لزراعة القمح',
          'status': 'favorable',
          'reasons': ['Soil temperature optimal', 'Adequate moisture'],
        },
      ];

  // ═══════════════════════════════════════════════════════════════════════════
  // Weather Locations - مواقع الطقس
  // ═══════════════════════════════════════════════════════════════════════════

  static List<Map<String, dynamic>> get locationsJson => [
        {
          'id': 'sanaa',
          'name': "Sana'a",
          'name_ar': 'صنعاء',
          'latitude': 15.3694,
          'longitude': 44.1910,
          'region': 'highland',
          'region_ar': 'مرتفعات',
        },
        {
          'id': 'aden',
          'name': 'Aden',
          'name_ar': 'عدن',
          'latitude': 12.7855,
          'longitude': 45.0187,
          'region': 'coastal',
          'region_ar': 'ساحلية',
        },
        {
          'id': 'taiz',
          'name': 'Taiz',
          'name_ar': 'تعز',
          'latitude': 13.5789,
          'longitude': 44.0219,
          'region': 'highland',
          'region_ar': 'مرتفعات',
        },
        {
          'id': 'hodeidah',
          'name': 'Hodeidah',
          'name_ar': 'الحديدة',
          'latitude': 14.7980,
          'longitude': 42.9510,
          'region': 'coastal',
          'region_ar': 'ساحلية',
        },
        {
          'id': 'marib',
          'name': 'Marib',
          'name_ar': 'مأرب',
          'latitude': 15.4543,
          'longitude': 45.3269,
          'region': 'desert',
          'region_ar': 'صحراوية',
        },
      ];

  // ═══════════════════════════════════════════════════════════════════════════
  // Error Responses - استجابات الأخطاء
  // ═══════════════════════════════════════════════════════════════════════════

  /// Network error message
  static String get networkErrorMessage => 'Unable to connect to weather service';

  /// Arabic network error message
  static String get networkErrorMessageAr => 'تعذر الاتصال بخدمة الطقس';

  /// API error JSON
  static Map<String, dynamic> get apiErrorJson => {
        'error': 'Service unavailable',
        'error_ar': 'الخدمة غير متاحة',
        'status_code': 503,
      };

  /// Rate limit error JSON
  static Map<String, dynamic> get rateLimitErrorJson => {
        'error': 'Rate limit exceeded',
        'error_ar': 'تجاوز حد الطلبات',
        'status_code': 429,
        'retry_after': 60,
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Open-Meteo Provider Responses - استجابات Open-Meteo
  // ═══════════════════════════════════════════════════════════════════════════

  /// Open-Meteo current weather response
  static Map<String, dynamic> get openMeteoCurrentJson => {
        'current': {
          'temperature_2m': 28.5,
          'relative_humidity_2m': 65,
          'precipitation': 0.0,
          'cloud_cover': 40,
          'wind_speed_10m': 12.5,
          'wind_direction_10m': 315, // NW
          'uv_index': 7.5,
          'weather_code': 2, // Partly Cloudy
        },
      };

  /// Open-Meteo forecast response
  static Map<String, dynamic> get openMeteoForecastJson => {
        'daily': {
          'time': [
            '2026-01-23',
            '2026-01-24',
            '2026-01-25',
          ],
          'temperature_2m_max': [34.0, 32.0, 30.0],
          'temperature_2m_min': [18.0, 17.0, 16.0],
          'precipitation_sum': [0.0, 0.0, 15.0],
          'precipitation_probability_max': [10, 0, 70],
          'wind_speed_10m_max': [12.0, 10.0, 20.0],
          'weather_code': [2, 0, 61],
          'sunrise': [
            '2026-01-23T06:30:00',
            '2026-01-24T06:31:00',
            '2026-01-25T06:31:00',
          ],
          'sunset': [
            '2026-01-23T17:45:00',
            '2026-01-24T17:46:00',
            '2026-01-25T17:47:00',
          ],
        },
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Test Data Generators - مولدات بيانات الاختبار
  // ═══════════════════════════════════════════════════════════════════════════

  /// Generate weather data with specific temperature
  static Map<String, dynamic> generateWeatherWithTemperature(double temp) => {
        'current': {
          'temperature': temp,
          'feels_like': temp + 2,
          'humidity': 50,
          'wind_speed': 10.0,
          'wind_direction': 'N',
          'condition': temp > 30 ? 'Hot' : (temp < 15 ? 'Cold' : 'Moderate'),
          'condition_ar': temp > 30 ? 'حار' : (temp < 15 ? 'بارد' : 'معتدل'),
          'icon': temp > 30 ? '☀️' : (temp < 15 ? '❄️' : '⛅'),
          'precipitation': 0.0,
          'uv_index': 5.0,
          'timestamp': DateTime.now().toIso8601String(),
        },
        'hourly': <dynamic>[],
        'daily': <dynamic>[],
        'alerts': <dynamic>[],
        'impacts': <dynamic>[],
      };

  /// Generate forecast for specified number of days
  static List<Map<String, dynamic>> generateForecastDays(int days) {
    final forecasts = <Map<String, dynamic>>[];
    final baseDate = DateTime.now();

    for (var i = 0; i < days; i++) {
      final date = baseDate.add(Duration(days: i));
      forecasts.add({
        'date': date.toIso8601String().split('T')[0],
        'temp_min': 15.0 + i,
        'temp_max': 30.0 + i,
        'condition': 'Clear',
        'condition_ar': 'صافي',
        'icon': '☀️',
        'precipitation_chance': i * 5,
        'precipitation_amount': 0.0,
        'humidity': 50 - i,
        'wind_speed': 10.0 + i,
      });
    }

    return forecasts;
  }

  /// Generate alert with specified severity
  static Map<String, dynamic> generateAlert({
    required String severity,
    required String type,
    bool isActive = true,
  }) {
    final now = DateTime.now();
    return {
      'id': 'alert-$type-${now.millisecondsSinceEpoch}',
      'type': type,
      'severity': severity,
      'title': '$type Alert',
      'title_ar': 'تنبيه $type',
      'description': 'Test alert description',
      'start_time': isActive
          ? now.subtract(const Duration(hours: 1)).toIso8601String()
          : now.subtract(const Duration(days: 2)).toIso8601String(),
      'end_time': isActive
          ? now.add(const Duration(hours: 6)).toIso8601String()
          : now.subtract(const Duration(days: 1)).toIso8601String(),
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Arabic Weather Condition Translations - ترجمات حالات الطقس
// ═══════════════════════════════════════════════════════════════════════════

/// Arabic translations for weather conditions
class ArabicWeatherConditions {
  ArabicWeatherConditions._();

  static const Map<String, String> conditions = {
    'Clear': 'صافي',
    'Partly Cloudy': 'غائم جزئياً',
    'Cloudy': 'غائم',
    'Overcast': 'ملبد بالغيوم',
    'Foggy': 'ضبابي',
    'Mist': 'ضباب خفيف',
    'Drizzle': 'رذاذ',
    'Rain': 'مطر',
    'Heavy Rain': 'مطر غزير',
    'Thunderstorm': 'عاصفة رعدية',
    'Snow': 'ثلج',
    'Hail': 'برد',
    'Dust': 'غبار',
    'Sandstorm': 'عاصفة رملية',
    'Hot': 'حار',
    'Cold': 'بارد',
    'Windy': 'عاصف',
  };

  static const Map<String, String> windDirections = {
    'N': 'شمال',
    'NNE': 'شمال شمال شرق',
    'NE': 'شمال شرق',
    'ENE': 'شرق شمال شرق',
    'E': 'شرق',
    'ESE': 'شرق جنوب شرق',
    'SE': 'جنوب شرق',
    'SSE': 'جنوب جنوب شرق',
    'S': 'جنوب',
    'SSW': 'جنوب جنوب غرب',
    'SW': 'جنوب غرب',
    'WSW': 'غرب جنوب غرب',
    'W': 'غرب',
    'WNW': 'غرب شمال غرب',
    'NW': 'شمال غرب',
    'NNW': 'شمال شمال غرب',
  };

  static const Map<String, String> alertTypes = {
    'heat': 'موجة حر',
    'cold': 'موجة برد',
    'rain': 'أمطار',
    'wind': 'رياح',
    'dust': 'غبار',
    'frost': 'صقيع',
    'thunderstorm': 'عاصفة رعدية',
    'flood': 'فيضان',
  };

  static const Map<String, String> severities = {
    'warning': 'تحذير',
    'watch': 'مراقبة',
    'advisory': 'إرشادي',
    'normal': 'عادي',
  };

  static const Map<String, String> agriculturalCategories = {
    'irrigation': 'الري',
    'spraying': 'الرش',
    'harvesting': 'الحصاد',
    'planting': 'الزراعة',
  };

  static const Map<String, String> impactStatuses = {
    'favorable': 'مناسب',
    'caution': 'تحذير',
    'unfavorable': 'غير مناسب',
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Weather Units - وحدات الطقس
// ═══════════════════════════════════════════════════════════════════════════

/// Weather unit formatting helpers
class WeatherUnits {
  WeatherUnits._();

  /// Format temperature in Celsius (درجة مئوية)
  static String formatTemperature(double temp) => '${temp.round()}°C';

  /// Format temperature in Celsius (Arabic)
  static String formatTemperatureAr(double temp) => '${temp.round()}° م';

  /// Format wind speed in km/h (كم/ساعة)
  static String formatWindSpeed(double speed) => '${speed.round()} km/h';

  /// Format wind speed in Arabic
  static String formatWindSpeedAr(double speed) => '${speed.round()} كم/س';

  /// Format humidity percentage (نسبة الرطوبة)
  static String formatHumidity(int humidity) => '$humidity%';

  /// Format precipitation in mm (ملم)
  static String formatPrecipitation(double mm) => '${mm.toStringAsFixed(1)} mm';

  /// Format precipitation in Arabic
  static String formatPrecipitationAr(double mm) => '${mm.toStringAsFixed(1)} ملم';

  /// Format UV index
  static String formatUvIndex(double uv) => uv.toStringAsFixed(1);
}
