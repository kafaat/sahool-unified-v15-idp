// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Multi-Weather Provider Service
// خدمة الطقس متعددة المزودين مع التبديل التلقائي
// ═══════════════════════════════════════════════════════════════════════════

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/providers_config.dart';

/// Weather data model
class WeatherData {
  final double temperature;
  final double humidity;
  final double windSpeed;
  final String windDirection;
  final double precipitation;
  final int cloudCover;
  final double uvIndex;
  final String condition;
  final String conditionAr;
  final String icon;
  final DateTime timestamp;
  final String provider;

  WeatherData({
    required this.temperature,
    required this.humidity,
    required this.windSpeed,
    required this.windDirection,
    required this.precipitation,
    required this.cloudCover,
    required this.uvIndex,
    required this.condition,
    required this.conditionAr,
    required this.icon,
    required this.timestamp,
    required this.provider,
  });

  Map<String, dynamic> toJson() => {
    'temperature': temperature,
    'humidity': humidity,
    'windSpeed': windSpeed,
    'windDirection': windDirection,
    'precipitation': precipitation,
    'cloudCover': cloudCover,
    'uvIndex': uvIndex,
    'condition': condition,
    'conditionAr': conditionAr,
    'icon': icon,
    'timestamp': timestamp.toIso8601String(),
    'provider': provider,
  };
}

/// Forecast data model
class ForecastDay {
  final DateTime date;
  final double tempMin;
  final double tempMax;
  final double precipitation;
  final int precipitationProbability;
  final double windSpeed;
  final String condition;
  final String conditionAr;
  final String icon;
  final DateTime? sunrise;
  final DateTime? sunset;

  ForecastDay({
    required this.date,
    required this.tempMin,
    required this.tempMax,
    required this.precipitation,
    required this.precipitationProbability,
    required this.windSpeed,
    required this.condition,
    required this.conditionAr,
    required this.icon,
    this.sunrise,
    this.sunset,
  });
}

/// Weather service result with fallback info
class WeatherResult<T> {
  final T? data;
  final String? error;
  final String? errorAr;
  final String usedProvider;
  final List<String> failedProviders;
  final bool isFromCache;

  WeatherResult({
    this.data,
    this.error,
    this.errorAr,
    required this.usedProvider,
    this.failedProviders = const [],
    this.isFromCache = false,
  });

  bool get success => data != null;
}

/// Multi-provider weather service with automatic fallback
class WeatherProviderService {
  final ProvidersConfig config;
  final Duration timeout;

  // Cache for rate limiting and performance
  final Map<String, _CacheEntry> _cache = {};
  final Duration _cacheDuration = const Duration(minutes: 10);

  WeatherProviderService({
    required this.config,
    this.timeout = const Duration(seconds: 10),
  });

  /// Get current weather with automatic provider fallback
  Future<WeatherResult<WeatherData>> getCurrentWeather(double lat, double lng) async {
    final cacheKey = 'current_${lat.toStringAsFixed(2)}_${lng.toStringAsFixed(2)}';

    // Check cache first
    final cached = _getFromCache<WeatherData>(cacheKey);
    if (cached != null) {
      return WeatherResult(
        data: cached,
        usedProvider: cached.provider,
        isFromCache: true,
      );
    }

    final failedProviders = <String>[];

    // Try providers in priority order
    for (final provider in config.weatherProviders) {
      if (!provider.isConfigured) continue;

      try {
        final result = await _fetchFromProvider(provider, lat, lng);
        if (result != null) {
          _saveToCache(cacheKey, result);
          return WeatherResult(
            data: result,
            usedProvider: provider.name,
            failedProviders: failedProviders,
          );
        }
      } catch (e) {
        failedProviders.add('${provider.name}: $e');
      }
    }

    return WeatherResult(
      error: 'All weather providers failed',
      errorAr: 'فشل جميع مزودي الطقس',
      usedProvider: 'none',
      failedProviders: failedProviders,
    );
  }

  /// Get weather forecast with automatic provider fallback
  Future<WeatherResult<List<ForecastDay>>> getForecast(
    double lat,
    double lng,
    {int days = 7}
  ) async {
    final cacheKey = 'forecast_${lat.toStringAsFixed(2)}_${lng.toStringAsFixed(2)}_$days';

    final cached = _getFromCache<List<ForecastDay>>(cacheKey);
    if (cached != null) {
      return WeatherResult(
        data: cached,
        usedProvider: 'cache',
        isFromCache: true,
      );
    }

    final failedProviders = <String>[];

    for (final provider in config.weatherProviders) {
      if (!provider.isConfigured) continue;

      try {
        final result = await _fetchForecastFromProvider(provider, lat, lng, days);
        if (result != null && result.isNotEmpty) {
          _saveToCache(cacheKey, result);
          return WeatherResult(
            data: result,
            usedProvider: provider.name,
            failedProviders: failedProviders,
          );
        }
      } catch (e) {
        failedProviders.add('${provider.name}: $e');
      }
    }

    return WeatherResult(
      error: 'All forecast providers failed',
      errorAr: 'فشل جميع مزودي التوقعات',
      usedProvider: 'none',
      failedProviders: failedProviders,
    );
  }

  /// Fetch current weather from specific provider
  Future<WeatherData?> _fetchFromProvider(
    WeatherProviderConfig provider,
    double lat,
    double lng,
  ) async {
    switch (provider.type) {
      case WeatherProviderType.openMeteo:
        return _fetchFromOpenMeteo(lat, lng, provider.name);
      case WeatherProviderType.openWeatherMap:
        return _fetchFromOpenWeatherMap(lat, lng, provider.apiKey!, provider.name);
      case WeatherProviderType.weatherApi:
        return _fetchFromWeatherApi(lat, lng, provider.apiKey!, provider.name);
      case WeatherProviderType.visualCrossing:
        return _fetchFromVisualCrossing(lat, lng, provider.apiKey!, provider.name);
    }
  }

  /// Fetch forecast from specific provider
  Future<List<ForecastDay>?> _fetchForecastFromProvider(
    WeatherProviderConfig provider,
    double lat,
    double lng,
    int days,
  ) async {
    switch (provider.type) {
      case WeatherProviderType.openMeteo:
        return _fetchForecastFromOpenMeteo(lat, lng, days);
      case WeatherProviderType.openWeatherMap:
        return _fetchForecastFromOpenWeatherMap(lat, lng, provider.apiKey!, days);
      case WeatherProviderType.weatherApi:
        return _fetchForecastFromWeatherApi(lat, lng, provider.apiKey!, days);
      case WeatherProviderType.visualCrossing:
        return _fetchForecastFromVisualCrossing(lat, lng, provider.apiKey!, days);
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // OPEN-METEO (FREE)
  // ─────────────────────────────────────────────────────────────────────────

  Future<WeatherData?> _fetchFromOpenMeteo(double lat, double lng, String providerName) async {
    final url = Uri.parse(
      'https://api.open-meteo.com/v1/forecast?'
      'latitude=$lat&longitude=$lng&'
      'current=temperature_2m,relative_humidity_2m,precipitation,cloud_cover,'
      'wind_speed_10m,wind_direction_10m,uv_index,weather_code&'
      'timezone=auto'
    );

    final response = await http.get(url).timeout(timeout);
    if (response.statusCode != 200) return null;

    final data = json.decode(response.body) as Map<String, dynamic>;
    final current = data['current'] as Map<String, dynamic>;

    return WeatherData(
      temperature: (current['temperature_2m'] as num).toDouble(),
      humidity: (current['relative_humidity_2m'] as num).toDouble(),
      windSpeed: (current['wind_speed_10m'] as num).toDouble(),
      windDirection: _degreeToDirection(current['wind_direction_10m'] as num),
      precipitation: (current['precipitation'] as num?)?.toDouble() ?? 0,
      cloudCover: (current['cloud_cover'] as num).toInt(),
      uvIndex: (current['uv_index'] as num?)?.toDouble() ?? 0,
      condition: _wmoCodeToCondition(current['weather_code'] as int),
      conditionAr: _wmoCodeToConditionAr(current['weather_code'] as int),
      icon: _wmoCodeToIcon(current['weather_code'] as int),
      timestamp: DateTime.now(),
      provider: providerName,
    );
  }

  Future<List<ForecastDay>?> _fetchForecastFromOpenMeteo(double lat, double lng, int days) async {
    final url = Uri.parse(
      'https://api.open-meteo.com/v1/forecast?'
      'latitude=$lat&longitude=$lng&'
      'daily=temperature_2m_max,temperature_2m_min,precipitation_sum,'
      'precipitation_probability_max,wind_speed_10m_max,weather_code,'
      'sunrise,sunset&'
      'forecast_days=$days&timezone=auto'
    );

    final response = await http.get(url).timeout(timeout);
    if (response.statusCode != 200) return null;

    final data = json.decode(response.body) as Map<String, dynamic>;
    final daily = data['daily'] as Map<String, dynamic>;

    final forecasts = <ForecastDay>[];
    final dates = daily['time'] as List;
    final tempMaxList = daily['temperature_2m_max'] as List;
    final tempMinList = daily['temperature_2m_min'] as List;
    final precipSumList = daily['precipitation_sum'] as List;
    final precipProbList = daily['precipitation_probability_max'] as List;
    final windSpeedList = daily['wind_speed_10m_max'] as List;
    final weatherCodeList = daily['weather_code'] as List;
    final sunriseList = daily['sunrise'] as List;
    final sunsetList = daily['sunset'] as List;

    for (var i = 0; i < dates.length; i++) {
      forecasts.add(ForecastDay(
        date: DateTime.parse(dates[i] as String),
        tempMax: (tempMaxList[i] as num).toDouble(),
        tempMin: (tempMinList[i] as num).toDouble(),
        precipitation: (precipSumList[i] as num?)?.toDouble() ?? 0,
        precipitationProbability: (precipProbList[i] as num?)?.toInt() ?? 0,
        windSpeed: (windSpeedList[i] as num).toDouble(),
        condition: _wmoCodeToCondition(weatherCodeList[i] as int),
        conditionAr: _wmoCodeToConditionAr(weatherCodeList[i] as int),
        icon: _wmoCodeToIcon(weatherCodeList[i] as int),
        sunrise: DateTime.tryParse((sunriseList[i] as String?) ?? ''),
        sunset: DateTime.tryParse((sunsetList[i] as String?) ?? ''),
      ));
    }

    return forecasts;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // OPENWEATHERMAP
  // ─────────────────────────────────────────────────────────────────────────

  Future<WeatherData?> _fetchFromOpenWeatherMap(
    double lat,
    double lng,
    String apiKey,
    String providerName,
  ) async {
    final url = Uri.parse(
      'https://api.openweathermap.org/data/2.5/weather?'
      'lat=$lat&lon=$lng&appid=$apiKey&units=metric'
    );

    final response = await http.get(url).timeout(timeout);
    if (response.statusCode != 200) return null;

    final data = json.decode(response.body) as Map<String, dynamic>;
    final main = data['main'] as Map<String, dynamic>;
    final wind = data['wind'] as Map<String, dynamic>;
    final rain = data['rain'] as Map<String, dynamic>?;
    final clouds = data['clouds'] as Map<String, dynamic>;
    final weatherList = data['weather'] as List;
    final weather0 = weatherList[0] as Map<String, dynamic>;

    return WeatherData(
      temperature: (main['temp'] as num).toDouble(),
      humidity: (main['humidity'] as num).toDouble(),
      windSpeed: (wind['speed'] as num).toDouble() * 3.6, // m/s to km/h
      windDirection: _degreeToDirection(wind['deg'] as num? ?? 0),
      precipitation: (rain?['1h'] as num?)?.toDouble() ?? 0,
      cloudCover: (clouds['all'] as num).toInt(),
      uvIndex: 0, // Not available in basic API
      condition: weather0['main'] as String,
      conditionAr: _owmConditionToAr(weather0['main'] as String),
      icon: 'https://openweathermap.org/img/wn/${weather0['icon']}@2x.png',
      timestamp: DateTime.now(),
      provider: providerName,
    );
  }

  Future<List<ForecastDay>?> _fetchForecastFromOpenWeatherMap(
    double lat,
    double lng,
    String apiKey,
    int days,
  ) async {
    final url = Uri.parse(
      'https://api.openweathermap.org/data/2.5/forecast?'
      'lat=$lat&lon=$lng&appid=$apiKey&units=metric&cnt=${days * 8}'
    );

    final response = await http.get(url).timeout(timeout);
    if (response.statusCode != 200) return null;

    final data = json.decode(response.body) as Map<String, dynamic>;
    final list = data['list'] as List;

    // Group by day
    final dailyData = <String, List<Map<String, dynamic>>>{};
    for (final item in list) {
      final itemMap = item as Map<String, dynamic>;
      final date = (itemMap['dt_txt'] as String).split(' ')[0];
      dailyData.putIfAbsent(date, () => []).add(itemMap);
    }

    return dailyData.entries.take(days).map((entry) {
      final dayItems = entry.value;
      final temps = dayItems.map((i) => ((i['main'] as Map<String, dynamic>)['temp'] as num).toDouble()).toList();
      final precips = dayItems.map((i) => ((i['rain'] as Map<String, dynamic>?)?['3h'] as num?)?.toDouble() ?? 0.0).toList();

      final firstItem = dayItems.first;
      final firstWind = firstItem['wind'] as Map<String, dynamic>;
      final firstWeatherList = firstItem['weather'] as List;
      final firstWeather0 = firstWeatherList[0] as Map<String, dynamic>;

      return ForecastDay(
        date: DateTime.parse(entry.key),
        tempMax: temps.reduce((a, b) => a > b ? a : b),
        tempMin: temps.reduce((a, b) => a < b ? a : b),
        precipitation: precips.reduce((a, b) => a + b),
        precipitationProbability: ((firstItem['pop'] as num?) ?? 0 * 100).toInt(),
        windSpeed: (firstWind['speed'] as num).toDouble() * 3.6,
        condition: firstWeather0['main'] as String,
        conditionAr: _owmConditionToAr(firstWeather0['main'] as String),
        icon: 'https://openweathermap.org/img/wn/${firstWeather0['icon']}@2x.png',
      );
    }).toList();
  }

  // ─────────────────────────────────────────────────────────────────────────
  // WEATHERAPI
  // ─────────────────────────────────────────────────────────────────────────

  Future<WeatherData?> _fetchFromWeatherApi(
    double lat,
    double lng,
    String apiKey,
    String providerName,
  ) async {
    final url = Uri.parse(
      'https://api.weatherapi.com/v1/current.json?'
      'key=$apiKey&q=$lat,$lng&aqi=no'
    );

    final response = await http.get(url).timeout(timeout);
    if (response.statusCode != 200) return null;

    final data = json.decode(response.body) as Map<String, dynamic>;
    final current = data['current'] as Map<String, dynamic>;
    final condition = current['condition'] as Map<String, dynamic>;

    return WeatherData(
      temperature: (current['temp_c'] as num).toDouble(),
      humidity: (current['humidity'] as num).toDouble(),
      windSpeed: (current['wind_kph'] as num).toDouble(),
      windDirection: current['wind_dir'] as String,
      precipitation: (current['precip_mm'] as num).toDouble(),
      cloudCover: (current['cloud'] as num).toInt(),
      uvIndex: (current['uv'] as num).toDouble(),
      condition: condition['text'] as String,
      conditionAr: condition['text'] as String, // Would need translation
      icon: 'https:${condition['icon']}',
      timestamp: DateTime.now(),
      provider: providerName,
    );
  }

  Future<List<ForecastDay>?> _fetchForecastFromWeatherApi(
    double lat,
    double lng,
    String apiKey,
    int days,
  ) async {
    final url = Uri.parse(
      'https://api.weatherapi.com/v1/forecast.json?'
      'key=$apiKey&q=$lat,$lng&days=$days&aqi=no'
    );

    final response = await http.get(url).timeout(timeout);
    if (response.statusCode != 200) return null;

    final data = json.decode(response.body) as Map<String, dynamic>;
    final forecast = data['forecast'] as Map<String, dynamic>;
    final forecastDays = forecast['forecastday'] as List;

    return forecastDays.map((day) {
      final dayMap = day as Map<String, dynamic>;
      final dayData = dayMap['day'] as Map<String, dynamic>;
      final dayCondition = dayData['condition'] as Map<String, dynamic>;
      final astro = dayMap['astro'] as Map<String, dynamic>;
      return ForecastDay(
        date: DateTime.parse(dayMap['date'] as String),
        tempMax: (dayData['maxtemp_c'] as num).toDouble(),
        tempMin: (dayData['mintemp_c'] as num).toDouble(),
        precipitation: (dayData['totalprecip_mm'] as num).toDouble(),
        precipitationProbability: (dayData['daily_chance_of_rain'] as num).toInt(),
        windSpeed: (dayData['maxwind_kph'] as num).toDouble(),
        condition: dayCondition['text'] as String,
        conditionAr: dayCondition['text'] as String,
        icon: 'https:${dayCondition['icon']}',
        sunrise: _parseTime(astro['sunrise'] as String?, dayMap['date'] as String),
        sunset: _parseTime(astro['sunset'] as String?, dayMap['date'] as String),
      );
    }).toList();
  }

  // ─────────────────────────────────────────────────────────────────────────
  // VISUAL CROSSING
  // ─────────────────────────────────────────────────────────────────────────

  Future<WeatherData?> _fetchFromVisualCrossing(
    double lat,
    double lng,
    String apiKey,
    String providerName,
  ) async {
    final url = Uri.parse(
      'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'
      '$lat,$lng/today?unitGroup=metric&key=$apiKey&include=current'
    );

    final response = await http.get(url).timeout(timeout);
    if (response.statusCode != 200) return null;

    final data = json.decode(response.body) as Map<String, dynamic>;
    final current = data['currentConditions'] as Map<String, dynamic>;

    return WeatherData(
      temperature: (current['temp'] as num).toDouble(),
      humidity: (current['humidity'] as num).toDouble(),
      windSpeed: (current['windspeed'] as num).toDouble(),
      windDirection: _degreeToDirection(current['winddir'] as num? ?? 0),
      precipitation: (current['precip'] as num?)?.toDouble() ?? 0,
      cloudCover: (current['cloudcover'] as num).toInt(),
      uvIndex: (current['uvindex'] as num?)?.toDouble() ?? 0,
      condition: current['conditions'] as String,
      conditionAr: current['conditions'] as String,
      icon: current['icon'] as String,
      timestamp: DateTime.now(),
      provider: providerName,
    );
  }

  Future<List<ForecastDay>?> _fetchForecastFromVisualCrossing(
    double lat,
    double lng,
    String apiKey,
    int days,
  ) async {
    final url = Uri.parse(
      'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'
      '$lat,$lng/next${days}days?unitGroup=metric&key=$apiKey&include=days'
    );

    final response = await http.get(url).timeout(timeout);
    if (response.statusCode != 200) return null;

    final data = json.decode(response.body) as Map<String, dynamic>;
    final forecastDays = data['days'] as List;

    return forecastDays.map((day) {
      final dayMap = day as Map<String, dynamic>;
      return ForecastDay(
        date: DateTime.parse(dayMap['datetime'] as String),
        tempMax: (dayMap['tempmax'] as num).toDouble(),
        tempMin: (dayMap['tempmin'] as num).toDouble(),
        precipitation: (dayMap['precip'] as num?)?.toDouble() ?? 0,
        precipitationProbability: (dayMap['precipprob'] as num?)?.toInt() ?? 0,
        windSpeed: (dayMap['windspeed'] as num).toDouble(),
        condition: dayMap['conditions'] as String,
        conditionAr: dayMap['conditions'] as String,
        icon: dayMap['icon'] as String,
        sunrise: _parseTime(dayMap['sunrise'] as String?, dayMap['datetime'] as String),
        sunset: _parseTime(dayMap['sunset'] as String?, dayMap['datetime'] as String),
      );
    }).toList();
  }

  // ─────────────────────────────────────────────────────────────────────────
  // HELPER FUNCTIONS
  // ─────────────────────────────────────────────────────────────────────────

  String _degreeToDirection(num degree) {
    const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                        'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
    final index = ((degree + 11.25) / 22.5).floor() % 16;
    return directions[index];
  }

  String _wmoCodeToCondition(int code) {
    if (code == 0) return 'Clear';
    if (code <= 3) return 'Partly Cloudy';
    if (code <= 49) return 'Foggy';
    if (code <= 59) return 'Drizzle';
    if (code <= 69) return 'Rain';
    if (code <= 79) return 'Snow';
    if (code <= 84) return 'Rain Showers';
    if (code <= 94) return 'Snow Showers';
    return 'Thunderstorm';
  }

  String _wmoCodeToConditionAr(int code) {
    if (code == 0) return 'صافي';
    if (code <= 3) return 'غائم جزئياً';
    if (code <= 49) return 'ضبابي';
    if (code <= 59) return 'رذاذ';
    if (code <= 69) return 'مطر';
    if (code <= 79) return 'ثلج';
    if (code <= 84) return 'زخات مطر';
    if (code <= 94) return 'زخات ثلجية';
    return 'عاصفة رعدية';
  }

  String _wmoCodeToIcon(int code) {
    if (code == 0) return '☀️';
    if (code <= 3) return '⛅';
    if (code <= 49) return '🌫️';
    if (code <= 59) return '🌧️';
    if (code <= 69) return '🌧️';
    if (code <= 79) return '❄️';
    if (code <= 84) return '🌦️';
    if (code <= 94) return '🌨️';
    return '⛈️';
  }

  String _owmConditionToAr(String condition) {
    const translations = {
      'Clear': 'صافي',
      'Clouds': 'غائم',
      'Rain': 'مطر',
      'Drizzle': 'رذاذ',
      'Thunderstorm': 'عاصفة رعدية',
      'Snow': 'ثلج',
      'Mist': 'ضباب خفيف',
      'Fog': 'ضباب',
      'Haze': 'ضباب دخاني',
    };
    return translations[condition] ?? condition;
  }

  DateTime? _parseTime(String? time, String date) {
    if (time == null) return null;
    try {
      // Handle "06:30 AM" format
      final parts = time.split(':');
      var hour = int.parse(parts[0]);
      final minute = int.parse(parts[1].split(' ')[0]);
      final isPM = time.toLowerCase().contains('pm');
      if (isPM && hour != 12) hour += 12;
      if (!isPM && hour == 12) hour = 0;

      final dateTime = DateTime.parse(date);
      return DateTime(dateTime.year, dateTime.month, dateTime.day, hour, minute);
    } catch (e) {
      return null;
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // CACHE MANAGEMENT
  // ─────────────────────────────────────────────────────────────────────────

  T? _getFromCache<T>(String key) {
    final entry = _cache[key];
    if (entry != null && !entry.isExpired(_cacheDuration)) {
      return entry.data as T?;
    }
    _cache.remove(key);
    return null;
  }

  void _saveToCache<T>(String key, T data) {
    _cache[key] = _CacheEntry(data: data);
  }

  void clearCache() {
    _cache.clear();
  }
}

class _CacheEntry {
  final dynamic data;
  final DateTime createdAt;

  _CacheEntry({required this.data}) : createdAt = DateTime.now();

  bool isExpired(Duration duration) {
    return DateTime.now().difference(createdAt) > duration;
  }
}
