/// Span/Tower Zone Models - نماذج مناطق الأبراج
/// VRI management at tower level for precision irrigation
library;

import 'package:freezed_annotation/freezed_annotation.dart';

part 'span_zone_models.freezed.dart';
part 'span_zone_models.g.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Span Configuration - تهيئة البرج
// ═══════════════════════════════════════════════════════════════════════════

/// Individual span/tower configuration
/// تهيئة البرج الفردي
@freezed
class SpanConfiguration with _$SpanConfiguration {
  const factory SpanConfiguration({
    required String id,
    required int spanNumber,

    /// Distance from center in meters - المسافة من المركز
    required double distanceFromCenter,

    /// Span length in meters - طول البرج
    required double spanLengthMeters,

    /// Number of nozzles on this span - عدد الفوهات
    @Default(10) int nozzleCount,

    /// Nozzle package type - نوع حزمة الفوهات
    @Default(NozzlePackage.standard) NozzlePackage nozzlePackage,

    /// Base application rate (mm/hr) - معدل التطبيق الأساسي
    @Default(6.0) double baseApplicationRateMmHr,

    /// Span zones for VRI - مناطق البرج لـ VRI
    @Default([]) List<SpanZone> zones,

    /// Is span operational - البرج يعمل
    @Default(true) bool isOperational,

    /// Last maintenance date
    DateTime? lastMaintenanceDate,
  }) = _SpanConfiguration;

  factory SpanConfiguration.fromJson(Map<String, dynamic> json) =>
      _$SpanConfigurationFromJson(json);
}

/// Nozzle package types
enum NozzlePackage {
  @JsonValue('standard')
  standard,
  @JsonValue('low_pressure')
  lowPressure,
  @JsonValue('high_capacity')
  highCapacity,
  @JsonValue('precision')
  precision,
  @JsonValue('lesa')
  lesa, // Low Energy Sprinkler Application
  @JsonValue('lepa')
  lepa, // Low Energy Precision Application
}

// ═══════════════════════════════════════════════════════════════════════════
// Span Zone - منطقة البرج
// ═══════════════════════════════════════════════════════════════════════════

/// Zone within a span for VRI control
/// منطقة داخل البرج للتحكم في VRI
@freezed
class SpanZone with _$SpanZone {
  const factory SpanZone({
    required String id,

    /// Span number this zone belongs to - رقم البرج
    required int spanNumber,

    /// Zone number within the span - رقم المنطقة داخل البرج
    required int zoneNumber,

    /// Start angle in degrees - زاوية البداية
    required double startAngle,

    /// End angle in degrees - زاوية النهاية
    required double endAngle,

    /// Application rate percentage (0-150%) - نسبة معدل التطبيق
    /// 100 = normal, 50 = half, 150 = 1.5x, 0 = off
    @Default(100) double applicationRatePercent,

    /// Zone prescription (for VRA maps) - وصفة المنطقة
    String? prescriptionId,

    /// NDVI value if available - قيمة NDVI
    double? ndviValue,

    /// Soil type for this zone - نوع التربة
    @Default('') String soilType,

    /// Crop type for this zone - نوع المحصول
    @Default('') String cropType,

    /// Zone enabled - المنطقة مفعلة
    @Default(true) bool isEnabled,

    /// Color for visualization
    @Default('#4CAF50') String color,

    /// Zone notes
    @Default('') String notes,
    @Default('') String notesAr,
  }) = _SpanZone;

  factory SpanZone.fromJson(Map<String, dynamic> json) =>
      _$SpanZoneFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════
// VRI Zone Grid - شبكة مناطق VRI
// ═══════════════════════════════════════════════════════════════════════════

/// Complete VRI zone grid for a pivot
/// شبكة VRI الكاملة للمحوري
@freezed
class VRIZoneGrid with _$VRIZoneGrid {
  const factory VRIZoneGrid({
    required String pivotId,

    /// Number of spans - عدد الأبراج
    required int spanCount,

    /// Number of angular divisions per span - عدد التقسيمات الزاوية لكل برج
    required int angularDivisions,

    /// Grid of zones [span][angle] - شبكة المناطق
    required List<List<SpanZone>> grid,

    /// Total zone count - إجمالي عدد المناطق
    int? totalZones,

    /// Grid resolution (degrees per angular division)
    double? angularResolution,

    /// Created timestamp
    DateTime? createdAt,

    /// Last updated timestamp
    DateTime? updatedAt,
  }) = _VRIZoneGrid;

  factory VRIZoneGrid.fromJson(Map<String, dynamic> json) =>
      _$VRIZoneGridFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════
// Prescription Map - خريطة الوصفات
// ═══════════════════════════════════════════════════════════════════════════

/// VRI prescription map for applying variable rates
/// خريطة وصفات VRI لتطبيق معدلات متغيرة
@freezed
class PrescriptionMap with _$PrescriptionMap {
  const factory PrescriptionMap({
    required String id,
    required String pivotId,
    required String name,
    @Default('') String nameAr,

    /// Prescription type - نوع الوصفة
    required PrescriptionType prescriptionType,

    /// Source of prescription data - مصدر بيانات الوصفة
    required PrescriptionSource source,

    /// Zone values - قيم المناطق
    required Map<String, double> zoneValues,

    /// Minimum value
    @Default(0) double minValue,

    /// Maximum value
    @Default(150) double maxValue,

    /// Unit for values
    @Default('%') String unit,

    /// Valid from date
    DateTime? validFrom,

    /// Valid until date
    DateTime? validUntil,

    /// Is active
    @Default(true) bool isActive,

    /// Created timestamp
    DateTime? createdAt,

    /// Notes
    @Default('') String notes,
    @Default('') String notesAr,
  }) = _PrescriptionMap;

  factory PrescriptionMap.fromJson(Map<String, dynamic> json) =>
      _$PrescriptionMapFromJson(json);
}

/// Prescription types
enum PrescriptionType {
  @JsonValue('irrigation')
  irrigation,
  @JsonValue('fertigation')
  fertigation,
  @JsonValue('chemigation')
  chemigation,
}

/// Prescription data sources
enum PrescriptionSource {
  @JsonValue('manual')
  manual,
  @JsonValue('ndvi')
  ndvi,
  @JsonValue('soil_map')
  soilMap,
  @JsonValue('yield_map')
  yieldMap,
  @JsonValue('sensor_data')
  sensorData,
  @JsonValue('ai_recommendation')
  aiRecommendation,
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Extensions
// ═══════════════════════════════════════════════════════════════════════════

extension SpanConfigurationX on SpanConfiguration {
  /// Calculate arc length covered by this span at its distance
  double get arcLengthAt360 {
    return 2 * 3.14159 * distanceFromCenter;
  }

  /// Get effective application rate considering zone multipliers
  double effectiveRateForAngle(double angle) {
    for (final zone in zones) {
      if (angle >= zone.startAngle && angle < zone.endAngle) {
        return baseApplicationRateMmHr * (zone.applicationRatePercent / 100);
      }
    }
    return baseApplicationRateMmHr;
  }
}

extension VRIZoneGridX on VRIZoneGrid {
  /// Get zone at specific span and angle
  SpanZone? getZoneAt(int spanIndex, double angle) {
    if (spanIndex < 0 || spanIndex >= grid.length) return null;

    for (final zone in grid[spanIndex]) {
      if (angle >= zone.startAngle && angle < zone.endAngle) {
        return zone;
      }
    }
    return null;
  }

  /// Get all zones for a specific angle (across all spans)
  List<SpanZone> getZonesAtAngle(double angle) {
    return grid
        .expand((spanZones) => spanZones)
        .where((zone) => angle >= zone.startAngle && angle < zone.endAngle)
        .toList();
  }

  /// Calculate average application rate for an angle
  double avgApplicationRateAtAngle(double angle) {
    final zones = getZonesAtAngle(angle);
    if (zones.isEmpty) return 100;
    return zones.map((z) => z.applicationRatePercent).reduce((a, b) => a + b) /
        zones.length;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Zone Grid Builder - بناء شبكة المناطق
// ═══════════════════════════════════════════════════════════════════════════

/// Helper class to build VRI zone grids
class VRIZoneGridBuilder {
  /// Create a uniform grid with equal zones
  static VRIZoneGrid createUniformGrid({
    required String pivotId,
    required int spanCount,
    required int angularDivisions,
    double defaultApplicationRate = 100,
  }) {
    final angularResolution = 360.0 / angularDivisions;

    final grid = List.generate(spanCount, (spanIndex) {
      return List.generate(angularDivisions, (angleIndex) {
        return SpanZone(
          id: 'zone_${spanIndex}_$angleIndex',
          spanNumber: spanIndex + 1,
          zoneNumber: angleIndex + 1,
          startAngle: angleIndex * angularResolution,
          endAngle: (angleIndex + 1) * angularResolution,
          applicationRatePercent: defaultApplicationRate,
          color: _getZoneColor(defaultApplicationRate),
        );
      });
    });

    return VRIZoneGrid(
      pivotId: pivotId,
      spanCount: spanCount,
      angularDivisions: angularDivisions,
      grid: grid,
      totalZones: spanCount * angularDivisions,
      angularResolution: angularResolution,
      createdAt: DateTime.now(),
    );
  }

  /// Create grid from NDVI values
  static VRIZoneGrid createFromNDVI({
    required String pivotId,
    required int spanCount,
    required int angularDivisions,
    required Map<String, double> ndviValues,
  }) {
    final angularResolution = 360.0 / angularDivisions;

    final grid = List.generate(spanCount, (spanIndex) {
      return List.generate(angularDivisions, (angleIndex) {
        final key = '${spanIndex}_$angleIndex';
        final ndvi = ndviValues[key] ?? 0.5;

        // Convert NDVI to application rate
        // Low NDVI = higher water need = higher application rate
        // High NDVI = lower water need = lower application rate
        double appRate;
        if (ndvi < 0.3) {
          appRate = 130; // Stressed - needs more water
        } else if (ndvi < 0.5) {
          appRate = 115;
        } else if (ndvi < 0.7) {
          appRate = 100; // Normal
        } else {
          appRate = 85; // Healthy - needs less water
        }

        return SpanZone(
          id: 'zone_${spanIndex}_$angleIndex',
          spanNumber: spanIndex + 1,
          zoneNumber: angleIndex + 1,
          startAngle: angleIndex * angularResolution,
          endAngle: (angleIndex + 1) * angularResolution,
          applicationRatePercent: appRate,
          ndviValue: ndvi,
          color: _getZoneColor(appRate),
        );
      });
    });

    return VRIZoneGrid(
      pivotId: pivotId,
      spanCount: spanCount,
      angularDivisions: angularDivisions,
      grid: grid,
      totalZones: spanCount * angularDivisions,
      angularResolution: angularResolution,
      createdAt: DateTime.now(),
    );
  }

  /// Get color based on application rate
  static String _getZoneColor(double applicationRate) {
    if (applicationRate <= 0) return '#9E9E9E'; // Off - grey
    if (applicationRate < 70) return '#FF9800'; // Low - orange
    if (applicationRate < 90) return '#FFC107'; // Below normal - yellow
    if (applicationRate <= 110) return '#4CAF50'; // Normal - green
    if (applicationRate <= 130) return '#2196F3'; // Above normal - blue
    return '#3F51B5'; // High - indigo
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Zone Statistics - إحصائيات المناطق
// ═══════════════════════════════════════════════════════════════════════════

/// Statistics for VRI zone grid
@freezed
class VRIZoneStatistics with _$VRIZoneStatistics {
  // Private constructor required for custom factory constructors in freezed
  const VRIZoneStatistics._();

  const factory VRIZoneStatistics({
    required int totalZones,
    required int activeZones,
    required int offZones,
    required double avgApplicationRate,
    required double minApplicationRate,
    required double maxApplicationRate,
    required Map<String, int> rateDistribution,
    required double waterSavingsPercent,
  }) = _VRIZoneStatistics;

  factory VRIZoneStatistics.fromJson(Map<String, dynamic> json) =>
      _$VRIZoneStatisticsFromJson(json);

  /// Calculate statistics from a grid
  factory VRIZoneStatistics.fromGrid(VRIZoneGrid grid) {
    final allZones = grid.grid.expand((zones) => zones).toList();
    final activeZonesList = allZones
        .where((z) => z.isEnabled && z.applicationRatePercent > 0)
        .toList();
    final offZonesList = allZones
        .where((z) => !z.isEnabled || z.applicationRatePercent == 0)
        .toList();

    final rates = activeZonesList.map((z) => z.applicationRatePercent).toList();
    final avgRate =
        rates.isEmpty ? 0.0 : rates.reduce((a, b) => a + b) / rates.length;
    final minRate = rates.isEmpty ? 0.0 : rates.reduce((a, b) => a < b ? a : b);
    final maxRate = rates.isEmpty ? 0.0 : rates.reduce((a, b) => a > b ? a : b);

    // Rate distribution
    final distribution = <String, int>{
      'off': 0,
      'low': 0,
      'normal': 0,
      'high': 0,
    };

    for (final zone in allZones) {
      final rate = zone.applicationRatePercent;
      if (rate <= 0) {
        distribution['off'] = (distribution['off'] ?? 0) + 1;
      } else if (rate < 90) {
        distribution['low'] = (distribution['low'] ?? 0) + 1;
      } else if (rate <= 110) {
        distribution['normal'] = (distribution['normal'] ?? 0) + 1;
      } else {
        distribution['high'] = (distribution['high'] ?? 0) + 1;
      }
    }

    // Water savings compared to uniform 100%
    final waterSavings = 100 - avgRate;

    return VRIZoneStatistics(
      totalZones: allZones.length,
      activeZones: activeZonesList.length,
      offZones: offZonesList.length,
      avgApplicationRate: avgRate,
      minApplicationRate: minRate,
      maxApplicationRate: maxRate,
      rateDistribution: distribution,
      waterSavingsPercent: waterSavings > 0 ? waterSavings : 0,
    );
  }
}
