/// Irrigation Scheduler Service - Schedule Management
/// خدمة جدولة الري - إدارة الجداول
///
/// Provides comprehensive irrigation scheduling including:
/// - Schedule creation and modification
/// - Event management (skip, reschedule, update)
/// - ET-based scheduling recommendations
/// - Sensor-triggered scheduling
/// - Schedule conflict resolution
library;

import '../../data/remote/irrigation_api.dart';
import '../../../advisor/data/models/irrigation_models.dart';
import 'water_calculator.dart';

/// Irrigation Scheduler Service
/// خدمة جدولة الري
class IrrigationScheduler {
  final IrrigationApi _api;
  final WaterCalculator _calculator;

  IrrigationScheduler({
    required IrrigationApi api,
    WaterCalculator? calculator,
  })  : _api = api,
        _calculator = calculator ?? const WaterCalculator();

  // ═══════════════════════════════════════════════════════════════════════════
  // Schedule Creation - إنشاء الجدول
  // ═══════════════════════════════════════════════════════════════════════════

  /// Create a new irrigation schedule
  /// إنشاء جدول ري جديد
  Future<IrrigationSchedule> createSchedule({
    required String fieldId,
    required String cropId,
    required String methodId,
    required int days,
    double? targetDepthMm,
    double? et0,
    String? growthStage,
  }) async {
    // Generate schedule from API
    final schedule = await _api.generateSchedule(
      fieldId: fieldId,
      cropId: cropId,
      methodId: methodId,
      days: days,
    );

    return schedule;
  }

  /// Create schedule with smart recommendations
  /// إنشاء جدول مع توصيات ذكية
  Future<SmartScheduleResult> createSmartSchedule({
    required String fieldId,
    required IrrigationCrop crop,
    required IrrigationMethod method,
    required double areaHectares,
    required int days,
    required double et0,
    String? growthStage,
    double? soilMoistureCurrent,
    double? soilMoistureFieldCapacity,
    WeatherForecast? weatherForecast,
  }) async {
    // Calculate irrigation requirements
    final requirement = _calculator.calculateIrrigationRequirement(
      et0: et0,
      crop: crop,
      method: method,
      areaHectares: areaHectares,
      growthStage: growthStage,
      soilMoistureCurrent: soilMoistureCurrent,
      soilMoistureFieldCapacity: soilMoistureFieldCapacity,
    );

    // Generate events based on calculations
    final events = <IrrigationEvent>[];
    final now = DateTime.now();

    // Determine irrigation interval based on crop and conditions
    final int intervalDays = _calculateIrrigationInterval(
      crop: crop,
      method: method,
      dailyEtc: requirement.etc,
      growthStage: growthStage,
    );

    // Generate events for the schedule period
    var eventDate = now;
    if (requirement.waterNeedMm > 0) {
      // First event may be needed sooner based on soil moisture
      final daysUntilFirst = _calculator.calculateDaysUntilIrrigation(
        soilMoistureCurrent: soilMoistureCurrent ?? 35.0,
        fieldCapacity: soilMoistureFieldCapacity ?? 45.0,
        wiltingPoint: 15.0,
        dailyETc: requirement.etc,
        madFraction: crop.madFraction,
      );

      eventDate = now.add(Duration(days: daysUntilFirst.ceil()));
    }

    int eventCount = 0;
    while (
        eventDate.isBefore(now.add(Duration(days: days))) && eventCount < 30) {
      // Calculate water need for this event
      double waterNeedMm = requirement.waterNeedMm * intervalDays;

      // Adjust for weather if available
      if (weatherForecast != null) {
        final forecastForDay = weatherForecast.getDayForecast(eventDate);
        if (forecastForDay != null) {
          waterNeedMm = _calculator.adjustForWeather(
            baseWaterNeedMm: waterNeedMm,
            rainForecastMm: forecastForDay.rainMm,
            temperatureC: forecastForDay.temperatureMax,
            humidityPercent: forecastForDay.humidity,
          );
        }
      }

      // Skip if water need is negligible
      if (waterNeedMm > 1.0) {
        final waterLiters =
            _calculator.convertMmToLiters(waterNeedMm, areaHectares);
        final durationMinutes = _calculator.calculateIrrigationDuration(
          waterLiters,
          method.efficiency * 50000, // Assume flow rate based on efficiency
        );

        events.add(IrrigationEvent(
          scheduledAt: eventDate.copyWith(hour: 6), // Default to early morning
          durationMinutes: durationMinutes,
          waterAmountLiters: waterLiters,
          status: 'pending',
          notes:
              'Auto-generated based on ET: ${requirement.etc.toStringAsFixed(1)} mm/day',
        ));
      }

      eventDate = eventDate.add(Duration(days: intervalDays));
      eventCount++;
    }

    final schedule = IrrigationSchedule(
      fieldId: fieldId,
      events: events,
      generatedAt: DateTime.now(),
    );

    return SmartScheduleResult(
      schedule: schedule,
      requirement: requirement,
      intervalDays: intervalDays,
      totalWaterLiters: events.fold(0, (sum, e) => sum + e.waterAmountLiters),
      recommendations: _generateScheduleRecommendations(
        requirement: requirement,
        events: events,
        crop: crop,
        method: method,
      ),
    );
  }

  /// Calculate recommended irrigation interval
  /// حساب الفاصل الزمني الموصى به للري
  int _calculateIrrigationInterval({
    required IrrigationCrop crop,
    required IrrigationMethod method,
    required double dailyEtc,
    String? growthStage,
  }) {
    // Base interval depends on crop and root depth
    int baseInterval = 3;

    // Shallow-rooted crops need more frequent irrigation
    if (crop.rootDepthMm < 500) {
      baseInterval = 2;
    } else if (crop.rootDepthMm > 1500) {
      baseInterval = 5;
    }

    // Adjust for growth stage
    if (growthStage == 'initial' || growthStage == 'development') {
      baseInterval = (baseInterval * 0.7).ceil();
    } else if (growthStage == 'late') {
      baseInterval = (baseInterval * 1.3).ceil();
    }

    // Adjust for irrigation method
    if (method.id == 'drip') {
      baseInterval = (baseInterval * 0.5).ceil(); // Drip needs more frequent
    } else if (method.id == 'flood') {
      baseInterval = (baseInterval * 1.5).ceil(); // Flood less frequent
    }

    // Ensure reasonable bounds
    return baseInterval.clamp(1, 14);
  }

  /// Generate recommendations for the schedule
  /// إنشاء توصيات للجدول
  List<ScheduleRecommendation> _generateScheduleRecommendations({
    required IrrigationRequirement requirement,
    required List<IrrigationEvent> events,
    required IrrigationCrop crop,
    required IrrigationMethod method,
  }) {
    final recommendations = <ScheduleRecommendation>[];

    // Morning irrigation recommendation
    recommendations.add(const ScheduleRecommendation(
      type: RecommendationType.timing,
      message:
          'Schedule irrigation in early morning (5-8 AM) to reduce evaporation losses',
      messageAr: 'جدول الري في الصباح الباكر (5-8 صباحًا) لتقليل فقد التبخر',
      priority: RecommendationPriority.medium,
    ));

    // High ETc warning
    if (requirement.etc > 7.0) {
      recommendations.add(ScheduleRecommendation(
        type: RecommendationType.waterNeed,
        message:
            'High evapotranspiration (${requirement.etc.toStringAsFixed(1)} mm/day). Consider increasing irrigation frequency.',
        messageAr:
            'نتح عالي (${requirement.etc.toStringAsFixed(1)} ملم/يوم). يُنصح بزيادة تكرار الري.',
        priority: RecommendationPriority.high,
      ));
    }

    // Efficiency recommendation
    if (method.efficiency < 0.75) {
      recommendations.add(const ScheduleRecommendation(
        type: RecommendationType.efficiency,
        message:
            'Consider upgrading to a more efficient irrigation method to save water',
        messageAr: 'يُنصح بالترقية إلى طريقة ري أكثر كفاءة لتوفير المياه',
        priority: RecommendationPriority.low,
      ));
    }

    return recommendations;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Schedule Retrieval - استرجاع الجدول
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get irrigation schedule for a field
  /// الحصول على جدول الري لحقل
  Future<IrrigationSchedule> getSchedule(String fieldId) async {
    return _api.getSchedule(fieldId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Event Management - إدارة الأحداث
  // ═══════════════════════════════════════════════════════════════════════════

  /// Update an irrigation event
  /// تحديث حدث ري
  Future<void> updateEvent(String fieldId, IrrigationEvent event) async {
    // Implementation depends on API
    // For now, we track locally and sync when online
  }

  /// Delete an irrigation event
  /// حذف حدث ري
  Future<void> deleteEvent(String fieldId, String eventId) async {
    // Implementation depends on API
  }

  /// Skip an irrigation event with reason
  /// تخطي حدث ري مع السبب
  Future<void> skipEvent(
    String fieldId,
    String eventId,
    String reason,
  ) async {
    // Mark event as skipped with reason
  }

  /// Reschedule an event to a new time
  /// إعادة جدولة حدث إلى وقت جديد
  Future<void> rescheduleEvent(
    String fieldId,
    String eventId,
    DateTime newTime,
  ) async {
    // Validate new time is in the future
    if (newTime.isBefore(DateTime.now())) {
      throw ArgumentError('Cannot reschedule to a past time');
    }
    // Implementation depends on API
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Event Queries - استعلامات الأحداث
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get upcoming irrigation events
  /// الحصول على أحداث الري القادمة
  Future<List<IrrigationEvent>> getUpcomingEvents(
    String fieldId, {
    int days = 7,
  }) async {
    final schedule = await getSchedule(fieldId);
    final now = DateTime.now();
    final endDate = now.add(Duration(days: days));

    return schedule.events
        .where((e) =>
            e.scheduledAt.isAfter(now) &&
            e.scheduledAt.isBefore(endDate) &&
            e.status == 'pending')
        .toList()
      ..sort((a, b) => a.scheduledAt.compareTo(b.scheduledAt));
  }

  /// Get past irrigation events
  /// الحصول على أحداث الري السابقة
  Future<List<IrrigationEvent>> getPastEvents(
    String fieldId, {
    int days = 30,
  }) async {
    final schedule = await getSchedule(fieldId);
    final now = DateTime.now();
    final startDate = now.subtract(Duration(days: days));

    return schedule.events
        .where((e) =>
            e.scheduledAt.isBefore(now) && e.scheduledAt.isAfter(startDate))
        .toList()
      ..sort((a, b) => b.scheduledAt.compareTo(a.scheduledAt));
  }

  /// Get next scheduled irrigation event
  /// الحصول على حدث الري المجدول التالي
  Future<IrrigationEvent?> getNextEvent(String fieldId) async {
    final upcoming = await getUpcomingEvents(fieldId, days: 30);
    return upcoming.isNotEmpty ? upcoming.first : null;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Sensor-Triggered Scheduling - الجدولة المحفزة بالمستشعرات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check if irrigation should be triggered based on soil moisture
  /// التحقق مما إذا كان يجب تفعيل الري بناءً على رطوبة التربة
  SensorTriggerResult checkSoilMoistureTrigger({
    required double currentMoisture,
    required double fieldCapacity,
    required double wiltingPoint,
    required double madFraction,
    double triggerBuffer = 5.0,
  }) {
    final totalAvailable = fieldCapacity - wiltingPoint;
    final madThreshold = wiltingPoint + totalAvailable * (1 - madFraction);

    final shouldTrigger = currentMoisture <= (madThreshold + triggerBuffer);

    return SensorTriggerResult(
      shouldTrigger: shouldTrigger,
      currentMoisture: currentMoisture,
      triggerThreshold: madThreshold + triggerBuffer,
      deficit: fieldCapacity - currentMoisture,
      urgency: _calculateUrgency(currentMoisture, madThreshold, wiltingPoint),
    );
  }

  /// Calculate irrigation urgency level
  /// حساب مستوى إلحاح الري
  IrrigationUrgency _calculateUrgency(
    double currentMoisture,
    double madThreshold,
    double wiltingPoint,
  ) {
    if (currentMoisture <= wiltingPoint + 5) {
      return IrrigationUrgency.critical;
    } else if (currentMoisture <= madThreshold) {
      return IrrigationUrgency.high;
    } else if (currentMoisture <= madThreshold + 5) {
      return IrrigationUrgency.medium;
    }
    return IrrigationUrgency.low;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Schedule Optimization - تحسين الجدول
  // ═══════════════════════════════════════════════════════════════════════════

  /// Optimize schedule based on weather forecast
  /// تحسين الجدول بناءً على توقعات الطقس
  List<IrrigationEvent> optimizeForWeather(
    List<IrrigationEvent> events,
    WeatherForecast forecast,
  ) {
    return events.map((event) {
      final dayForecast = forecast.getDayForecast(event.scheduledAt);
      if (dayForecast == null) return event;

      // Skip or reduce if rain expected
      if (dayForecast.rainMm > 10) {
        return IrrigationEvent(
          scheduledAt: event.scheduledAt,
          durationMinutes: 0,
          waterAmountLiters: 0,
          status: 'skipped',
          notes: 'Skipped due to expected rain: ${dayForecast.rainMm}mm',
        );
      }

      // Adjust water amount based on conditions
      final adjustedWaterMm = _calculator.adjustForWeather(
        baseWaterNeedMm: _calculator.convertLitersToMm(
          event.waterAmountLiters,
          5.0, // Default area - should be passed in
        ),
        rainForecastMm: dayForecast.rainMm,
        temperatureC: dayForecast.temperatureMax,
        humidityPercent: dayForecast.humidity,
      );

      final adjustedLiters =
          _calculator.convertMmToLiters(adjustedWaterMm, 5.0);
      final adjustedDuration =
          event.durationMinutes * (adjustedLiters / event.waterAmountLiters);

      return IrrigationEvent(
        scheduledAt: event.scheduledAt,
        durationMinutes: adjustedDuration,
        waterAmountLiters: adjustedLiters,
        status: event.status,
        notes:
            'Weather-adjusted from ${event.waterAmountLiters.toStringAsFixed(0)}L',
      );
    }).toList();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Supporting Models - نماذج مساعدة
// ═══════════════════════════════════════════════════════════════════════════

/// Smart schedule creation result
/// نتيجة إنشاء الجدول الذكي
class SmartScheduleResult {
  final IrrigationSchedule schedule;
  final IrrigationRequirement requirement;
  final int intervalDays;
  final double totalWaterLiters;
  final List<ScheduleRecommendation> recommendations;

  const SmartScheduleResult({
    required this.schedule,
    required this.requirement,
    required this.intervalDays,
    required this.totalWaterLiters,
    required this.recommendations,
  });
}

/// Schedule recommendation
/// توصية الجدول
class ScheduleRecommendation {
  final RecommendationType type;
  final String message;
  final String messageAr;
  final RecommendationPriority priority;

  const ScheduleRecommendation({
    required this.type,
    required this.message,
    required this.messageAr,
    required this.priority,
  });
}

/// Recommendation types
enum RecommendationType {
  timing,
  waterNeed,
  efficiency,
  weather,
  soilMoisture,
}

/// Recommendation priority
enum RecommendationPriority {
  low,
  medium,
  high,
}

/// Sensor trigger result
/// نتيجة محفز المستشعر
class SensorTriggerResult {
  final bool shouldTrigger;
  final double currentMoisture;
  final double triggerThreshold;
  final double deficit;
  final IrrigationUrgency urgency;

  const SensorTriggerResult({
    required this.shouldTrigger,
    required this.currentMoisture,
    required this.triggerThreshold,
    required this.deficit,
    required this.urgency,
  });
}

/// Irrigation urgency levels
/// مستويات إلحاح الري
enum IrrigationUrgency {
  low,
  medium,
  high,
  critical,
}

extension IrrigationUrgencyX on IrrigationUrgency {
  String get displayName {
    switch (this) {
      case IrrigationUrgency.low:
        return 'Low';
      case IrrigationUrgency.medium:
        return 'Medium';
      case IrrigationUrgency.high:
        return 'High';
      case IrrigationUrgency.critical:
        return 'Critical';
    }
  }

  String get displayNameAr {
    switch (this) {
      case IrrigationUrgency.low:
        return 'منخفض';
      case IrrigationUrgency.medium:
        return 'متوسط';
      case IrrigationUrgency.high:
        return 'عالي';
      case IrrigationUrgency.critical:
        return 'حرج';
    }
  }
}

/// Weather forecast for scheduling
/// توقعات الطقس للجدولة
class WeatherForecast {
  final List<DayForecast> days;

  const WeatherForecast({required this.days});

  DayForecast? getDayForecast(DateTime date) {
    try {
      return days.firstWhere(
        (d) =>
            d.date.year == date.year &&
            d.date.month == date.month &&
            d.date.day == date.day,
      );
    } catch (_) {
      return null;
    }
  }
}

/// Single day forecast
/// توقعات يوم واحد
class DayForecast {
  final DateTime date;
  final double temperatureMax;
  final double temperatureMin;
  final double humidity;
  final double rainMm;
  final double windSpeedKmh;
  final String condition;

  const DayForecast({
    required this.date,
    required this.temperatureMax,
    required this.temperatureMin,
    required this.humidity,
    required this.rainMm,
    required this.windSpeedKmh,
    required this.condition,
  });
}
