/// Weather DAO Tests - Weather Data Caching Operations
/// اختبارات تخزين بيانات الطقس للعمل بدون اتصال
///
/// Tests for:
/// - Weather data caching for offline-first access
/// - Cache expiration handling
/// - Location-based weather queries
/// - Forecast data management
/// - Cache cleanup operations
///
/// Note: Weather caching supports offline-first architecture by
/// storing weather data locally for access when network is unavailable.
import 'dart:convert';

import 'package:drift/drift.dart' hide isNull, isNotNull;
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';

part 'weather_dao_test.g.dart';

/// Weather Cache Table - stores weather data for offline access
@TableIndex(name: 'weather_cache_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'weather_cache_location_idx', columns: {#locationId})
@TableIndex(name: 'weather_cache_expiry_idx', columns: {#expiresAt})
class WeatherCache extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get tenantId => text()();
  TextColumn get locationId => text()(); // Can be field ID or coordinates
  RealColumn get latitude => real()();
  RealColumn get longitude => real()();
  TextColumn get weatherType => text()(); // 'current', 'hourly', 'daily'
  TextColumn get data => text()(); // JSON weather data
  DateTimeColumn get fetchedAt => dateTime()();
  DateTimeColumn get expiresAt => dateTime()();
  DateTimeColumn get forecastDate => dateTime().nullable()(); // For forecast data
}

/// Weather Alerts Table - stores weather alerts
@TableIndex(name: 'weather_alerts_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'weather_alerts_read_idx', columns: {#isRead})
@TableIndex(name: 'weather_alerts_active_idx', columns: {#isActive})
class WeatherAlerts extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get tenantId => text()();
  TextColumn get alertId => text()(); // External alert ID
  TextColumn get alertType => text()(); // 'frost', 'heat', 'rain', 'wind', etc.
  TextColumn get severity => text()(); // 'low', 'medium', 'high', 'critical'
  TextColumn get title => text()();
  TextColumn get titleAr => text().nullable()();
  TextColumn get description => text()();
  TextColumn get descriptionAr => text().nullable()();
  RealColumn get latitude => real().nullable()();
  RealColumn get longitude => real().nullable()();
  RealColumn get radius => real().nullable()(); // Affected radius in km
  DateTimeColumn get startsAt => dateTime()();
  DateTimeColumn get expiresAt => dateTime()();
  BoolColumn get isRead => boolean().withDefault(const Constant(false))();
  BoolColumn get isActive => boolean().withDefault(const Constant(true))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

/// Weather Statistics Table - aggregated weather data for analytics
@TableIndex(name: 'weather_stats_field_idx', columns: {#fieldId})
@TableIndex(name: 'weather_stats_date_idx', columns: {#date})
class WeatherStatistics extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get fieldId => text()();
  DateTimeColumn get date => dateTime()();
  RealColumn get tempMin => real().nullable()();
  RealColumn get tempMax => real().nullable()();
  RealColumn get tempAvg => real().nullable()();
  RealColumn get humidity => real().nullable()();
  RealColumn get precipitation => real().nullable()();
  RealColumn get windSpeed => real().nullable()();
  RealColumn get solarRadiation => real().nullable()();
  RealColumn get evapotranspiration => real().nullable()();
  IntColumn get growingDegreeDays => integer().nullable()();
}

/// Weather DAO Test Database
@DriftDatabase(tables: [WeatherCache, WeatherAlerts, WeatherStatistics])
class WeatherDaoTestDatabase extends _$WeatherDaoTestDatabase {
  WeatherDaoTestDatabase() : super(NativeDatabase.memory());

  @override
  int get schemaVersion => 1;

  // ============================================================
  // Weather Cache Operations
  // ============================================================

  /// Get cached weather for location
  Future<WeatherCacheData?> getCachedWeather({
    required String tenantId,
    required String locationId,
    required String weatherType,
  }) async {
    return (select(weatherCache)
          ..where((w) => w.tenantId.equals(tenantId))
          ..where((w) => w.locationId.equals(locationId))
          ..where((w) => w.weatherType.equals(weatherType))
          ..where((w) => w.expiresAt.isBiggerThanValue(DateTime.now())))
        .getSingleOrNull();
  }

  /// Get cached weather by coordinates
  Future<WeatherCacheData?> getCachedWeatherByCoords({
    required String tenantId,
    required double latitude,
    required double longitude,
    required String weatherType,
    double tolerance = 0.01, // ~1km tolerance
  }) async {
    final latMin = latitude - tolerance;
    final latMax = latitude + tolerance;
    final lonMin = longitude - tolerance;
    final lonMax = longitude + tolerance;

    return (select(weatherCache)
          ..where((w) => w.tenantId.equals(tenantId))
          ..where((w) => w.weatherType.equals(weatherType))
          ..where((w) => w.latitude.isBetweenValues(latMin, latMax))
          ..where((w) => w.longitude.isBetweenValues(lonMin, lonMax))
          ..where((w) => w.expiresAt.isBiggerThanValue(DateTime.now())))
        .getSingleOrNull();
  }

  /// Save weather to cache
  Future<int> cacheWeather(WeatherCacheCompanion weather) {
    return into(weatherCache).insert(weather);
  }

  /// Update or insert weather cache
  Future<void> upsertWeatherCache(WeatherCacheCompanion weather) async {
    // Delete existing cache for same location and type
    await (delete(weatherCache)
          ..where((w) => w.tenantId.equals(weather.tenantId.value))
          ..where((w) => w.locationId.equals(weather.locationId.value))
          ..where((w) => w.weatherType.equals(weather.weatherType.value)))
        .go();

    // Insert new
    await into(weatherCache).insert(weather);
  }

  /// Delete expired cache entries
  Future<int> cleanupExpiredCache() async {
    return await (delete(weatherCache)
          ..where((w) => w.expiresAt.isSmallerThanValue(DateTime.now())))
        .go();
  }

  /// Delete all cache for tenant
  Future<int> clearCacheForTenant(String tenantId) async {
    return await (delete(weatherCache)
          ..where((w) => w.tenantId.equals(tenantId)))
        .go();
  }

  /// Get all cached weather for tenant (for debugging/sync)
  Future<List<WeatherCacheData>> getAllCachedWeather(String tenantId) {
    return (select(weatherCache)
          ..where((w) => w.tenantId.equals(tenantId))
          ..orderBy([(w) => OrderingTerm.desc(w.fetchedAt)]))
        .get();
  }

  /// Get forecast for date range
  Future<List<WeatherCacheData>> getForecastForRange({
    required String tenantId,
    required String locationId,
    required DateTime startDate,
    required DateTime endDate,
  }) {
    return (select(weatherCache)
          ..where((w) => w.tenantId.equals(tenantId))
          ..where((w) => w.locationId.equals(locationId))
          ..where((w) => w.weatherType.equals('daily'))
          ..where((w) => w.forecastDate.isBiggerOrEqualValue(startDate))
          ..where((w) => w.forecastDate.isSmallerOrEqualValue(endDate))
          ..orderBy([(w) => OrderingTerm.asc(w.forecastDate)]))
        .get();
  }

  // ============================================================
  // Weather Alerts Operations
  // ============================================================

  /// Get active alerts for tenant
  Future<List<WeatherAlert>> getActiveAlerts(String tenantId) {
    return (select(weatherAlerts)
          ..where((a) => a.tenantId.equals(tenantId))
          ..where((a) => a.isActive.equals(true))
          ..where((a) => a.expiresAt.isBiggerThanValue(DateTime.now()))
          ..orderBy([(a) => OrderingTerm.desc(a.startsAt)]))
        .get();
  }

  /// Get unread alerts for tenant (only non-expired)
  Future<List<WeatherAlert>> getUnreadAlerts(String tenantId) {
    return (select(weatherAlerts)
          ..where((a) => a.tenantId.equals(tenantId))
          ..where((a) => a.isRead.equals(false))
          ..where((a) => a.isActive.equals(true))
          ..where((a) => a.expiresAt.isBiggerThanValue(DateTime.now()))
          ..orderBy([(a) => OrderingTerm.desc(a.startsAt)]))
        .get();
  }

  /// Watch unread alerts count
  Stream<int> watchUnreadAlertsCount(String tenantId) {
    final query = selectOnly(weatherAlerts)
      ..where(weatherAlerts.tenantId.equals(tenantId))
      ..where(weatherAlerts.isRead.equals(false))
      ..where(weatherAlerts.isActive.equals(true))
      ..addColumns([weatherAlerts.id.count()]);
    return query.map((row) => row.read(weatherAlerts.id.count()) ?? 0).watchSingle();
  }

  /// Save weather alert
  Future<int> saveAlert(WeatherAlertsCompanion alert) {
    return into(weatherAlerts).insert(alert);
  }

  /// Mark alert as read
  Future<void> markAlertRead(int alertId) async {
    await (update(weatherAlerts)..where((a) => a.id.equals(alertId))).write(
      const WeatherAlertsCompanion(isRead: Value(true)),
    );
  }

  /// Mark all alerts as read
  Future<void> markAllAlertsRead(String tenantId) async {
    await (update(weatherAlerts)
          ..where((a) => a.tenantId.equals(tenantId))
          ..where((a) => a.isRead.equals(false)))
        .write(const WeatherAlertsCompanion(isRead: Value(true)));
  }

  /// Deactivate expired alerts
  Future<int> deactivateExpiredAlerts() async {
    return await (update(weatherAlerts)
          ..where((a) => a.expiresAt.isSmallerThanValue(DateTime.now()))
          ..where((a) => a.isActive.equals(true)))
        .write(const WeatherAlertsCompanion(isActive: Value(false)));
  }

  /// Get alerts by severity
  Future<List<WeatherAlert>> getAlertsBySeverity(String tenantId, String severity) {
    return (select(weatherAlerts)
          ..where((a) => a.tenantId.equals(tenantId))
          ..where((a) => a.severity.equals(severity))
          ..where((a) => a.isActive.equals(true)))
        .get();
  }

  // ============================================================
  // Weather Statistics Operations
  // ============================================================

  /// Save daily weather statistics
  Future<int> saveDailyStats(WeatherStatisticsCompanion stats) {
    return into(weatherStatistics).insert(stats);
  }

  /// Get statistics for field and date range
  Future<List<WeatherStatistic>> getStatsForDateRange({
    required String fieldId,
    required DateTime startDate,
    required DateTime endDate,
  }) {
    return (select(weatherStatistics)
          ..where((s) => s.fieldId.equals(fieldId))
          ..where((s) => s.date.isBiggerOrEqualValue(startDate))
          ..where((s) => s.date.isSmallerOrEqualValue(endDate))
          ..orderBy([(s) => OrderingTerm.asc(s.date)]))
        .get();
  }

  /// Get average temperature for field
  Future<double?> getAverageTemperature({
    required String fieldId,
    required DateTime startDate,
    required DateTime endDate,
  }) async {
    final result = await customSelect(
      'SELECT AVG(temp_avg) as avg_temp FROM weather_statistics WHERE field_id = ? AND date >= ? AND date <= ?',
      variables: [
        Variable.withString(fieldId),
        Variable.withDateTime(startDate),
        Variable.withDateTime(endDate),
      ],
    ).getSingle();
    return result.read<double?>('avg_temp');
  }

  /// Get total precipitation for field
  Future<double?> getTotalPrecipitation({
    required String fieldId,
    required DateTime startDate,
    required DateTime endDate,
  }) async {
    final result = await customSelect(
      'SELECT SUM(precipitation) as total_precip FROM weather_statistics WHERE field_id = ? AND date >= ? AND date <= ?',
      variables: [
        Variable.withString(fieldId),
        Variable.withDateTime(startDate),
        Variable.withDateTime(endDate),
      ],
    ).getSingle();
    return result.read<double?>('total_precip');
  }

  /// Get cumulative growing degree days
  Future<int?> getCumulativeGDD({
    required String fieldId,
    required DateTime startDate,
    required DateTime endDate,
  }) async {
    final result = await customSelect(
      'SELECT SUM(growing_degree_days) as total_gdd FROM weather_statistics WHERE field_id = ? AND date >= ? AND date <= ?',
      variables: [
        Variable.withString(fieldId),
        Variable.withDateTime(startDate),
        Variable.withDateTime(endDate),
      ],
    ).getSingle();
    return result.read<int?>('total_gdd');
  }
}

/// Test fixtures for Weather DAO
class WeatherDaoFixtures {
  static Map<String, dynamic> createCurrentWeatherData() {
    return {
      'temperature': 28.5,
      'humidity': 45,
      'description': 'Sunny',
      'description_ar': 'مشمس',
      'wind_speed': 12.5,
      'wind_direction': 'NE',
      'pressure': 1013,
      'uv_index': 7,
      'visibility': 10000,
      'feels_like': 30.0,
      'icon': 'sunny',
    };
  }

  static Map<String, dynamic> createDailyForecastData(DateTime date) {
    return {
      'date': date.toIso8601String(),
      'temp_min': 18.0,
      'temp_max': 32.0,
      'humidity': 40,
      'description': 'Partly Cloudy',
      'description_ar': 'غائم جزئيا',
      'precipitation_chance': 10,
      'wind_speed': 15.0,
    };
  }

  static WeatherCacheCompanion createCacheEntry({
    String tenantId = 'tenant-1',
    String locationId = 'field-1',
    double latitude = 15.3694,
    double longitude = 44.1910,
    String weatherType = 'current',
    Map<String, dynamic>? data,
    Duration? expiresIn,
    DateTime? forecastDate,
  }) {
    return WeatherCacheCompanion.insert(
      tenantId: tenantId,
      locationId: locationId,
      latitude: latitude,
      longitude: longitude,
      weatherType: weatherType,
      data: jsonEncode(data ?? createCurrentWeatherData()),
      fetchedAt: DateTime.now(),
      expiresAt: DateTime.now().add(expiresIn ?? const Duration(hours: 1)),
      forecastDate: Value(forecastDate),
    );
  }

  static WeatherAlertsCompanion createAlert({
    String tenantId = 'tenant-1',
    String alertId = 'alert-001',
    String alertType = 'frost',
    String severity = 'high',
    String title = 'Frost Warning',
    String? titleAr = 'تحذير من الصقيع',
    String description = 'Frost expected tonight. Protect sensitive crops.',
    String? descriptionAr = 'متوقع صقيع الليلة. احم المحاصيل الحساسة.',
    Duration? expiresIn,
    double? latitude,
    double? longitude,
  }) {
    return WeatherAlertsCompanion.insert(
      tenantId: tenantId,
      alertId: alertId,
      alertType: alertType,
      severity: severity,
      title: title,
      titleAr: Value(titleAr),
      description: description,
      descriptionAr: Value(descriptionAr),
      latitude: Value(latitude),
      longitude: Value(longitude),
      startsAt: DateTime.now(),
      expiresAt: DateTime.now().add(expiresIn ?? const Duration(hours: 24)),
    );
  }

  static WeatherStatisticsCompanion createDailyStats({
    String fieldId = 'field-1',
    required DateTime date,
    double? tempMin = 18.0,
    double? tempMax = 32.0,
    double? tempAvg = 25.0,
    double? humidity = 45.0,
    double? precipitation = 0.0,
    double? windSpeed = 12.0,
    double? solarRadiation = 250.0,
    double? evapotranspiration = 5.5,
    int? growingDegreeDays = 15,
  }) {
    return WeatherStatisticsCompanion.insert(
      fieldId: fieldId,
      date: date,
      tempMin: Value(tempMin),
      tempMax: Value(tempMax),
      tempAvg: Value(tempAvg),
      humidity: Value(humidity),
      precipitation: Value(precipitation),
      windSpeed: Value(windSpeed),
      solarRadiation: Value(solarRadiation),
      evapotranspiration: Value(evapotranspiration),
      growingDegreeDays: Value(growingDegreeDays),
    );
  }
}

void main() {
  group('Weather Cache - Insert Operations', () {
    late WeatherDaoTestDatabase db;

    setUp(() {
      db = WeatherDaoTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should cache current weather', () async {
      final cache = WeatherDaoFixtures.createCacheEntry(
        weatherType: 'current',
      );

      final id = await db.cacheWeather(cache);
      expect(id, greaterThan(0));

      final cached = await db.getCachedWeather(
        tenantId: 'tenant-1',
        locationId: 'field-1',
        weatherType: 'current',
      );

      expect(cached, isNotNull);
      expect(cached!.weatherType, equals('current'));
    });

    test('should cache daily forecast', () async {
      final forecastDate = DateTime.now().add(const Duration(days: 1));

      final cache = WeatherDaoFixtures.createCacheEntry(
        weatherType: 'daily',
        data: WeatherDaoFixtures.createDailyForecastData(forecastDate),
        forecastDate: forecastDate,
      );

      await db.cacheWeather(cache);

      final cached = await db.getCachedWeather(
        tenantId: 'tenant-1',
        locationId: 'field-1',
        weatherType: 'daily',
      );

      expect(cached, isNotNull);
      expect(cached!.forecastDate, isNotNull);
    });

    test('should upsert weather cache', () async {
      // Insert initial
      await db.cacheWeather(WeatherDaoFixtures.createCacheEntry(
        data: {'temperature': 25.0},
      ));

      // Upsert with new data
      await db.upsertWeatherCache(WeatherDaoFixtures.createCacheEntry(
        data: {'temperature': 30.0},
      ));

      final allCached = await db.getAllCachedWeather('tenant-1');
      expect(allCached.length, equals(1));

      final data = jsonDecode(allCached.first.data);
      expect(data['temperature'], equals(30.0));
    });
  });

  group('Weather Cache - Read Operations', () {
    late WeatherDaoTestDatabase db;

    setUp(() async {
      db = WeatherDaoTestDatabase();

      // Insert test data
      await db.cacheWeather(WeatherDaoFixtures.createCacheEntry(
        tenantId: 'tenant-1',
        locationId: 'field-1',
        latitude: 15.370,
        longitude: 44.190,
        weatherType: 'current',
      ));

      await db.cacheWeather(WeatherDaoFixtures.createCacheEntry(
        tenantId: 'tenant-1',
        locationId: 'field-2',
        latitude: 15.380,
        longitude: 44.200,
        weatherType: 'current',
      ));

      // Add forecast data
      for (int i = 0; i < 7; i++) {
        final forecastDate = DateTime.now().add(Duration(days: i));
        await db.cacheWeather(WeatherDaoFixtures.createCacheEntry(
          locationId: 'field-1',
          weatherType: 'daily',
          data: WeatherDaoFixtures.createDailyForecastData(forecastDate),
          forecastDate: forecastDate,
        ));
      }
    });

    tearDown(() async {
      await db.close();
    });

    test('should get cached weather by location ID', () async {
      final cached = await db.getCachedWeather(
        tenantId: 'tenant-1',
        locationId: 'field-1',
        weatherType: 'current',
      );

      expect(cached, isNotNull);
      expect(cached!.locationId, equals('field-1'));
    });

    test('should get cached weather by coordinates', () async {
      final cached = await db.getCachedWeatherByCoords(
        tenantId: 'tenant-1',
        latitude: 15.370, // Exact match to field-1
        longitude: 44.190, // Exact match to field-1
        weatherType: 'current',
        tolerance: 0.005, // Tight tolerance to only match field-1 (not field-2 at 15.380)
      );

      expect(cached, isNotNull);
      expect(cached!.locationId, equals('field-1'));
    });

    test('should return null for non-cached location', () async {
      final cached = await db.getCachedWeather(
        tenantId: 'tenant-1',
        locationId: 'non-existent',
        weatherType: 'current',
      );

      expect(cached, isNull);
    });

    test('should get forecast for date range', () async {
      final startDate = DateTime.now();
      final endDate = DateTime.now().add(const Duration(days: 5));

      final forecast = await db.getForecastForRange(
        tenantId: 'tenant-1',
        locationId: 'field-1',
        startDate: startDate,
        endDate: endDate,
      );

      expect(forecast.length, greaterThan(0));
      expect(forecast.length, lessThanOrEqualTo(6));
    });

    test('should get all cached weather for tenant', () async {
      final allCached = await db.getAllCachedWeather('tenant-1');

      // 2 current + 7 daily forecasts
      expect(allCached.length, equals(9));
    });
  });

  group('Weather Cache - Expiration', () {
    late WeatherDaoTestDatabase db;

    setUp(() async {
      db = WeatherDaoTestDatabase();

      // Insert expired cache
      await db.cacheWeather(WeatherDaoFixtures.createCacheEntry(
        locationId: 'expired-1',
        expiresIn: const Duration(hours: -1), // Already expired
      ));

      // Insert valid cache
      await db.cacheWeather(WeatherDaoFixtures.createCacheEntry(
        locationId: 'valid-1',
        expiresIn: const Duration(hours: 2),
      ));
    });

    tearDown(() async {
      await db.close();
    });

    test('should not return expired cache', () async {
      final cached = await db.getCachedWeather(
        tenantId: 'tenant-1',
        locationId: 'expired-1',
        weatherType: 'current',
      );

      expect(cached, isNull);
    });

    test('should return valid cache', () async {
      final cached = await db.getCachedWeather(
        tenantId: 'tenant-1',
        locationId: 'valid-1',
        weatherType: 'current',
      );

      expect(cached, isNotNull);
    });

    test('should cleanup expired cache', () async {
      final deleted = await db.cleanupExpiredCache();
      expect(deleted, equals(1));

      final allCached = await db.getAllCachedWeather('tenant-1');
      expect(allCached.length, equals(1));
      expect(allCached.first.locationId, equals('valid-1'));
    });

    test('should clear all cache for tenant', () async {
      await db.clearCacheForTenant('tenant-1');

      final allCached = await db.getAllCachedWeather('tenant-1');
      expect(allCached, isEmpty);
    });
  });

  group('Weather Alerts - Insert Operations', () {
    late WeatherDaoTestDatabase db;

    setUp(() {
      db = WeatherDaoTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should save weather alert', () async {
      final alert = WeatherDaoFixtures.createAlert();

      final id = await db.saveAlert(alert);
      expect(id, greaterThan(0));
    });

    test('should save alert with Arabic content', () async {
      final alert = WeatherDaoFixtures.createAlert(
        title: 'Heat Wave Warning',
        titleAr: 'تحذير من موجة حر',
        description: 'Extreme heat expected',
        descriptionAr: 'متوقع حرارة شديدة',
      );

      await db.saveAlert(alert);

      final alerts = await db.getActiveAlerts('tenant-1');
      expect(alerts.length, equals(1));
      expect(alerts.first.titleAr, equals('تحذير من موجة حر'));
    });

    test('should save alert with location', () async {
      final alert = WeatherDaoFixtures.createAlert(
        latitude: 15.370,
        longitude: 44.190,
      );

      await db.saveAlert(alert);

      final alerts = await db.getActiveAlerts('tenant-1');
      expect(alerts.first.latitude, equals(15.370));
      expect(alerts.first.longitude, equals(44.190));
    });
  });

  group('Weather Alerts - Read Operations', () {
    late WeatherDaoTestDatabase db;

    setUp(() async {
      db = WeatherDaoTestDatabase();

      // Insert various alerts
      await db.saveAlert(WeatherDaoFixtures.createAlert(
        alertId: 'alert-1',
        severity: 'high',
        expiresIn: const Duration(hours: 24),
      ));

      await db.saveAlert(WeatherDaoFixtures.createAlert(
        alertId: 'alert-2',
        severity: 'medium',
        expiresIn: const Duration(hours: 12),
      ));

      await db.saveAlert(WeatherDaoFixtures.createAlert(
        alertId: 'alert-3',
        severity: 'low',
        expiresIn: const Duration(hours: -1), // Expired
      ));

      await db.saveAlert(WeatherDaoFixtures.createAlert(
        tenantId: 'tenant-2',
        alertId: 'alert-4',
      ));
    });

    tearDown(() async {
      await db.close();
    });

    test('should get active alerts for tenant', () async {
      final alerts = await db.getActiveAlerts('tenant-1');

      expect(alerts.length, equals(2));
      expect(alerts.every((a) => a.tenantId == 'tenant-1'), isTrue);
    });

    test('should isolate alerts by tenant', () async {
      final tenant1Alerts = await db.getActiveAlerts('tenant-1');
      final tenant2Alerts = await db.getActiveAlerts('tenant-2');

      expect(tenant1Alerts.length, equals(2));
      expect(tenant2Alerts.length, equals(1));
    });

    test('should get unread alerts', () async {
      final unread = await db.getUnreadAlerts('tenant-1');

      expect(unread.length, equals(2));
      expect(unread.every((a) => !a.isRead), isTrue);
    });

    test('should get alerts by severity', () async {
      final highAlerts = await db.getAlertsBySeverity('tenant-1', 'high');

      expect(highAlerts.length, equals(1));
      expect(highAlerts.first.severity, equals('high'));
    });
  });

  group('Weather Alerts - Update Operations', () {
    late WeatherDaoTestDatabase db;

    setUp(() async {
      db = WeatherDaoTestDatabase();

      await db.saveAlert(WeatherDaoFixtures.createAlert(alertId: 'alert-1'));
      await db.saveAlert(WeatherDaoFixtures.createAlert(alertId: 'alert-2'));
    });

    tearDown(() async {
      await db.close();
    });

    test('should mark alert as read', () async {
      final alerts = await db.getActiveAlerts('tenant-1');
      await db.markAlertRead(alerts.first.id);

      final unread = await db.getUnreadAlerts('tenant-1');
      expect(unread.length, equals(1));
    });

    test('should mark all alerts as read', () async {
      await db.markAllAlertsRead('tenant-1');

      final unread = await db.getUnreadAlerts('tenant-1');
      expect(unread, isEmpty);
    });

    test('should deactivate expired alerts', () async {
      // Insert expired alert
      await db.saveAlert(WeatherDaoFixtures.createAlert(
        alertId: 'expired-alert',
        expiresIn: const Duration(hours: -1),
      ));

      final deactivated = await db.deactivateExpiredAlerts();
      expect(deactivated, greaterThan(0));
    });
  });

  group('Weather Alerts - Watch Streams', () {
    late WeatherDaoTestDatabase db;

    setUp(() {
      db = WeatherDaoTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should watch unread alerts count', () async {
      final stream = db.watchUnreadAlertsCount('tenant-1');

      // Initial count
      expect(await stream.first, equals(0));

      // Add alert
      await db.saveAlert(WeatherDaoFixtures.createAlert());

      // Allow stream to update
      await Future<void>.delayed(const Duration(milliseconds: 50));

      // Count should now be 1
      expect(await stream.first, equals(1));
    });
  });

  group('Weather Statistics - Insert Operations', () {
    late WeatherDaoTestDatabase db;

    setUp(() {
      db = WeatherDaoTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should save daily statistics', () async {
      final stats = WeatherDaoFixtures.createDailyStats(
        date: DateTime.now(),
      );

      final id = await db.saveDailyStats(stats);
      expect(id, greaterThan(0));
    });

    test('should save statistics with all fields', () async {
      final date = DateTime.now();
      final stats = WeatherDaoFixtures.createDailyStats(
        fieldId: 'field-1',
        date: date,
        tempMin: 15.0,
        tempMax: 35.0,
        tempAvg: 25.0,
        humidity: 50.0,
        precipitation: 2.5,
        windSpeed: 10.0,
        solarRadiation: 280.0,
        evapotranspiration: 6.0,
        growingDegreeDays: 18,
      );

      await db.saveDailyStats(stats);

      final result = await db.getStatsForDateRange(
        fieldId: 'field-1',
        startDate: date.subtract(const Duration(hours: 1)),
        endDate: date.add(const Duration(hours: 1)),
      );

      expect(result.length, equals(1));
      expect(result.first.tempMax, equals(35.0));
      expect(result.first.growingDegreeDays, equals(18));
    });
  });

  group('Weather Statistics - Aggregations', () {
    late WeatherDaoTestDatabase db;

    setUp(() async {
      db = WeatherDaoTestDatabase();

      // Insert 30 days of statistics
      for (int i = 0; i < 30; i++) {
        final date = DateTime.now().subtract(Duration(days: i));
        await db.saveDailyStats(WeatherDaoFixtures.createDailyStats(
          fieldId: 'field-1',
          date: date,
          tempMin: 15.0 + (i % 5),
          tempMax: 30.0 + (i % 5),
          tempAvg: 22.5 + (i % 5),
          precipitation: i % 3 == 0 ? 5.0 : 0.0,
          growingDegreeDays: 12 + (i % 5),
        ));
      }
    });

    tearDown(() async {
      await db.close();
    });

    test('should get statistics for date range', () async {
      final stats = await db.getStatsForDateRange(
        fieldId: 'field-1',
        startDate: DateTime.now().subtract(const Duration(days: 7)),
        endDate: DateTime.now(),
      );

      expect(stats.length, greaterThan(0));
      expect(stats.length, lessThanOrEqualTo(8));
    });

    test('should calculate average temperature', () async {
      final avgTemp = await db.getAverageTemperature(
        fieldId: 'field-1',
        startDate: DateTime.now().subtract(const Duration(days: 30)),
        endDate: DateTime.now(),
      );

      expect(avgTemp, isNotNull);
      expect(avgTemp, greaterThan(20.0));
      expect(avgTemp, lessThan(30.0));
    });

    test('should calculate total precipitation', () async {
      final totalPrecip = await db.getTotalPrecipitation(
        fieldId: 'field-1',
        startDate: DateTime.now().subtract(const Duration(days: 30)),
        endDate: DateTime.now(),
      );

      expect(totalPrecip, isNotNull);
      expect(totalPrecip, greaterThan(0));
    });

    test('should calculate cumulative GDD', () async {
      final totalGDD = await db.getCumulativeGDD(
        fieldId: 'field-1',
        startDate: DateTime.now().subtract(const Duration(days: 30)),
        endDate: DateTime.now(),
      );

      expect(totalGDD, isNotNull);
      expect(totalGDD, greaterThan(300)); // ~30 days * ~12+ GDD
    });
  });

  group('Weather Data - JSON Handling', () {
    late WeatherDaoTestDatabase db;

    setUp(() {
      db = WeatherDaoTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should store and retrieve complex JSON data', () async {
      final complexData = {
        'temperature': 28.5,
        'humidity': 45,
        'wind': {
          'speed': 12.5,
          'direction': 'NE',
          'gusts': 25.0,
        },
        'forecast': [
          {'hour': 0, 'temp': 22},
          {'hour': 6, 'temp': 20},
          {'hour': 12, 'temp': 28},
          {'hour': 18, 'temp': 25},
        ],
        'metadata': {
          'source': 'OpenWeatherMap',
          'station_id': 'STATION-001',
        },
      };

      await db.cacheWeather(WeatherDaoFixtures.createCacheEntry(
        data: complexData,
      ));

      final cached = await db.getCachedWeather(
        tenantId: 'tenant-1',
        locationId: 'field-1',
        weatherType: 'current',
      );

      final retrieved = jsonDecode(cached!.data);
      expect(retrieved['wind']['speed'], equals(12.5));
      expect(retrieved['forecast'], hasLength(4));
      expect(retrieved['metadata']['source'], equals('OpenWeatherMap'));
    });

    test('should handle Arabic text in JSON', () async {
      final arabicData = {
        'description': 'Sunny',
        'description_ar': 'مشمس جزئيا مع رياح خفيفة',
        'alerts': [
          {'title_ar': 'تحذير من الحرارة'},
        ],
      };

      await db.cacheWeather(WeatherDaoFixtures.createCacheEntry(
        data: arabicData,
      ));

      final cached = await db.getCachedWeather(
        tenantId: 'tenant-1',
        locationId: 'field-1',
        weatherType: 'current',
      );

      final retrieved = jsonDecode(cached!.data);
      expect(retrieved['description_ar'], contains('مشمس'));
    });
  });
}
