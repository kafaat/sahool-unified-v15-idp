/// Usage Log Models - نماذج سجل الاستخدام
/// Usage tracking, hours logging, and operator management
library;

import 'package:flutter/foundation.dart';

/// نوع الاستخدام - Usage Type
enum UsageType {
  fieldWork('field_work', 'عمل حقلي', 'Field Work'),
  transport('transport', 'نقل', 'Transport'),
  idle('idle', 'خامل', 'Idle'),
  maintenance('maintenance', 'صيانة', 'Maintenance'),
  training('training', 'تدريب', 'Training'),
  rental('rental', 'إيجار', 'Rental'),
  other('other', 'أخرى', 'Other');

  final String value;
  final String nameAr;
  final String nameEn;

  const UsageType(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static UsageType fromString(String value) {
    return UsageType.values.firstWhere(
      (e) => e.value == value,
      orElse: () => UsageType.other,
    );
  }
}

/// نوع نشاط الحقل - Field Activity Type
enum FieldActivityType {
  plowing('plowing', 'حراثة', 'Plowing'),
  seeding('seeding', 'بذر', 'Seeding'),
  spraying('spraying', 'رش', 'Spraying'),
  harvesting('harvesting', 'حصاد', 'Harvesting'),
  irrigation('irrigation', 'ري', 'Irrigation'),
  fertilizing('fertilizing', 'تسميد', 'Fertilizing'),
  weeding('weeding', 'إزالة أعشاب', 'Weeding'),
  transport('transport', 'نقل', 'Transport'),
  other('other', 'أخرى', 'Other');

  final String value;
  final String nameAr;
  final String nameEn;

  const FieldActivityType(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static FieldActivityType fromString(String value) {
    return FieldActivityType.values.firstWhere(
      (e) => e.value == value,
      orElse: () => FieldActivityType.other,
    );
  }
}

/// سجل الاستخدام - Usage Log Entry
@immutable
class UsageLog {
  final String logId;
  final String equipmentId;
  final UsageType usageType;
  final FieldActivityType? activityType;
  final String? fieldId;
  final String? fieldName;
  final String? operatorId;
  final String? operatorName;
  final DateTime startTime;
  final DateTime? endTime;
  final double? hoursUsed;
  final double? startHourReading;
  final double? endHourReading;
  final double? fuelUsed; // Liters
  final double? areaWorked; // Hectares
  final double? distanceTraveled; // Kilometers
  final String? notes;
  final String? notesAr;
  final List<LocationPoint>? route;
  final DateTime createdAt;
  final DateTime updatedAt;
  final Map<String, dynamic>? metadata;

  const UsageLog({
    required this.logId,
    required this.equipmentId,
    required this.usageType,
    this.activityType,
    this.fieldId,
    this.fieldName,
    this.operatorId,
    this.operatorName,
    required this.startTime,
    this.endTime,
    this.hoursUsed,
    this.startHourReading,
    this.endHourReading,
    this.fuelUsed,
    this.areaWorked,
    this.distanceTraveled,
    this.notes,
    this.notesAr,
    this.route,
    required this.createdAt,
    required this.updatedAt,
    this.metadata,
  });

  /// Get notes based on locale
  String? getNotes(String locale) {
    if (notes == null && notesAr == null) return null;
    return locale == 'ar' && notesAr != null ? notesAr : notes;
  }

  /// Calculate hours if not provided
  double get calculatedHours {
    if (hoursUsed != null) return hoursUsed!;
    if (startHourReading != null && endHourReading != null) {
      return endHourReading! - startHourReading!;
    }
    if (endTime != null) {
      return endTime!.difference(startTime).inMinutes / 60.0;
    }
    return 0;
  }

  /// Is session still active
  bool get isActive => endTime == null;

  /// Session duration
  Duration get duration {
    final end = endTime ?? DateTime.now();
    return end.difference(startTime);
  }

  /// Fuel efficiency (L/hour)
  double? get fuelEfficiency {
    if (fuelUsed == null || calculatedHours == 0) return null;
    return fuelUsed! / calculatedHours;
  }

  /// Productivity (hectares/hour)
  double? get productivity {
    if (areaWorked == null || calculatedHours == 0) return null;
    return areaWorked! / calculatedHours;
  }

  factory UsageLog.fromJson(Map<String, dynamic> json) {
    return UsageLog(
      logId: json['log_id'] as String,
      equipmentId: json['equipment_id'] as String,
      usageType: UsageType.fromString(json['usage_type'] as String),
      activityType: json['activity_type'] != null
          ? FieldActivityType.fromString(json['activity_type'] as String)
          : null,
      fieldId: json['field_id'] as String?,
      fieldName: json['field_name'] as String?,
      operatorId: json['operator_id'] as String?,
      operatorName: json['operator_name'] as String?,
      startTime: DateTime.tryParse(json['start_time'] as String) ?? DateTime.now(),
      endTime: json['end_time'] != null
          ? DateTime.tryParse(json['end_time'] as String) ?? DateTime.now()
          : null,
      hoursUsed: (json['hours_used'] as num?)?.toDouble(),
      startHourReading: (json['start_hour_reading'] as num?)?.toDouble(),
      endHourReading: (json['end_hour_reading'] as num?)?.toDouble(),
      fuelUsed: (json['fuel_used'] as num?)?.toDouble(),
      areaWorked: (json['area_worked'] as num?)?.toDouble(),
      distanceTraveled: (json['distance_traveled'] as num?)?.toDouble(),
      notes: json['notes'] as String?,
      notesAr: json['notes_ar'] as String?,
      route: json['route'] != null
          ? (json['route'] as List? ?? [])
              .map((e) => LocationPoint.fromJson(e as Map<String, dynamic>))
              .toList()
          : null,
      createdAt: DateTime.tryParse(json['created_at'] as String) ?? DateTime.now(),
      updatedAt: DateTime.tryParse(json['updated_at'] as String) ?? DateTime.now(),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'log_id': logId,
        'equipment_id': equipmentId,
        'usage_type': usageType.value,
        'activity_type': activityType?.value,
        'field_id': fieldId,
        'field_name': fieldName,
        'operator_id': operatorId,
        'operator_name': operatorName,
        'start_time': startTime.toIso8601String(),
        'end_time': endTime?.toIso8601String(),
        'hours_used': hoursUsed,
        'start_hour_reading': startHourReading,
        'end_hour_reading': endHourReading,
        'fuel_used': fuelUsed,
        'area_worked': areaWorked,
        'distance_traveled': distanceTraveled,
        'notes': notes,
        'notes_ar': notesAr,
        'route': route?.map((e) => e.toJson()).toList(),
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
        'metadata': metadata,
      };

  UsageLog copyWith({
    DateTime? endTime,
    double? hoursUsed,
    double? endHourReading,
    double? fuelUsed,
    double? areaWorked,
    double? distanceTraveled,
    String? notes,
    String? notesAr,
    List<LocationPoint>? route,
    DateTime? updatedAt,
  }) {
    return UsageLog(
      logId: logId,
      equipmentId: equipmentId,
      usageType: usageType,
      activityType: activityType,
      fieldId: fieldId,
      fieldName: fieldName,
      operatorId: operatorId,
      operatorName: operatorName,
      startTime: startTime,
      endTime: endTime ?? this.endTime,
      hoursUsed: hoursUsed ?? this.hoursUsed,
      startHourReading: startHourReading,
      endHourReading: endHourReading ?? this.endHourReading,
      fuelUsed: fuelUsed ?? this.fuelUsed,
      areaWorked: areaWorked ?? this.areaWorked,
      distanceTraveled: distanceTraveled ?? this.distanceTraveled,
      notes: notes ?? this.notes,
      notesAr: notesAr ?? this.notesAr,
      route: route ?? this.route,
      createdAt: createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      metadata: metadata,
    );
  }
}

/// نقطة موقع - Location Point
@immutable
class LocationPoint {
  final double lat;
  final double lon;
  final DateTime timestamp;
  final double? speed; // km/h
  final double? heading; // degrees

  const LocationPoint({
    required this.lat,
    required this.lon,
    required this.timestamp,
    this.speed,
    this.heading,
  });

  factory LocationPoint.fromJson(Map<String, dynamic> json) {
    return LocationPoint(
      lat: (json['lat'] as num).toDouble(),
      lon: (json['lon'] as num).toDouble(),
      timestamp: DateTime.tryParse(json['timestamp'] as String) ?? DateTime.now(),
      speed: (json['speed'] as num?)?.toDouble(),
      heading: (json['heading'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'lat': lat,
        'lon': lon,
        'timestamp': timestamp.toIso8601String(),
        'speed': speed,
        'heading': heading,
      };
}

/// ملخص الاستخدام - Usage Summary
@immutable
class UsageSummary {
  final String equipmentId;
  final double totalHours;
  final double totalFuel;
  final double totalArea; // Hectares
  final double totalDistance; // Kilometers
  final int sessionCount;
  final Map<String, double> hoursByActivity;
  final Map<String, double> hoursByOperator;
  final DateTime periodStart;
  final DateTime periodEnd;
  final List<DailyUsage>? dailyBreakdown;

  const UsageSummary({
    required this.equipmentId,
    required this.totalHours,
    required this.totalFuel,
    required this.totalArea,
    required this.totalDistance,
    required this.sessionCount,
    this.hoursByActivity = const {},
    this.hoursByOperator = const {},
    required this.periodStart,
    required this.periodEnd,
    this.dailyBreakdown,
  });

  /// Average session length
  double get averageSessionLength {
    if (sessionCount == 0) return 0;
    return totalHours / sessionCount;
  }

  /// Average fuel consumption per hour
  double get averageFuelPerHour {
    if (totalHours == 0) return 0;
    return totalFuel / totalHours;
  }

  /// Utilization rate (hours per day in period)
  double get utilizationRate {
    final days = periodEnd.difference(periodStart).inDays + 1;
    if (days == 0) return 0;
    return totalHours / days;
  }

  factory UsageSummary.fromJson(Map<String, dynamic> json) {
    return UsageSummary(
      equipmentId: json['equipment_id'] as String,
      totalHours: (json['total_hours'] as num).toDouble(),
      totalFuel: (json['total_fuel'] as num).toDouble(),
      totalArea: (json['total_area'] as num).toDouble(),
      totalDistance: (json['total_distance'] as num).toDouble(),
      sessionCount: json['session_count'] as int,
      hoursByActivity: json['hours_by_activity'] != null
          ? Map<String, double>.from(
              (json['hours_by_activity'] as Map).map(
                (k, v) => MapEntry(k as String, (v as num).toDouble()),
              ),
            )
          : {},
      hoursByOperator: json['hours_by_operator'] != null
          ? Map<String, double>.from(
              (json['hours_by_operator'] as Map).map(
                (k, v) => MapEntry(k as String, (v as num).toDouble()),
              ),
            )
          : {},
      periodStart: DateTime.tryParse(json['period_start'] as String) ?? DateTime.now(),
      periodEnd: DateTime.tryParse(json['period_end'] as String) ?? DateTime.now(),
      dailyBreakdown: json['daily_breakdown'] != null
          ? (json['daily_breakdown'] as List? ?? [])
              .map((e) => DailyUsage.fromJson(e as Map<String, dynamic>))
              .toList()
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'equipment_id': equipmentId,
        'total_hours': totalHours,
        'total_fuel': totalFuel,
        'total_area': totalArea,
        'total_distance': totalDistance,
        'session_count': sessionCount,
        'hours_by_activity': hoursByActivity,
        'hours_by_operator': hoursByOperator,
        'period_start': periodStart.toIso8601String(),
        'period_end': periodEnd.toIso8601String(),
        'daily_breakdown': dailyBreakdown?.map((e) => e.toJson()).toList(),
      };
}

/// الاستخدام اليومي - Daily Usage
@immutable
class DailyUsage {
  final DateTime date;
  final double hours;
  final double fuel;
  final double area;
  final int sessions;

  const DailyUsage({
    required this.date,
    required this.hours,
    required this.fuel,
    required this.area,
    required this.sessions,
  });

  factory DailyUsage.fromJson(Map<String, dynamic> json) {
    return DailyUsage(
      date: DateTime.tryParse(json['date'] as String) ?? DateTime.now(),
      hours: (json['hours'] as num).toDouble(),
      fuel: (json['fuel'] as num).toDouble(),
      area: (json['area'] as num).toDouble(),
      sessions: json['sessions'] as int,
    );
  }

  Map<String, dynamic> toJson() => {
        'date': date.toIso8601String(),
        'hours': hours,
        'fuel': fuel,
        'area': area,
        'sessions': sessions,
      };
}

/// معلومات المشغل - Operator Info
@immutable
class OperatorInfo {
  final String operatorId;
  final String name;
  final String? nameAr;
  final String? phone;
  final String? licenseNumber;
  final DateTime? licenseExpiry;
  final List<String>? certifications;
  final double totalHoursOperated;
  final int sessionsCount;
  final bool isActive;

  const OperatorInfo({
    required this.operatorId,
    required this.name,
    this.nameAr,
    this.phone,
    this.licenseNumber,
    this.licenseExpiry,
    this.certifications,
    this.totalHoursOperated = 0,
    this.sessionsCount = 0,
    this.isActive = true,
  });

  String getName(String locale) {
    return locale == 'ar' && nameAr != null ? nameAr! : name;
  }

  /// Check if license is valid
  bool get hasValidLicense {
    if (licenseExpiry == null) return true;
    return licenseExpiry!.isAfter(DateTime.now());
  }

  factory OperatorInfo.fromJson(Map<String, dynamic> json) {
    return OperatorInfo(
      operatorId: json['operator_id'] as String,
      name: json['name'] as String,
      nameAr: json['name_ar'] as String?,
      phone: json['phone'] as String?,
      licenseNumber: json['license_number'] as String?,
      licenseExpiry: json['license_expiry'] != null
          ? DateTime.tryParse(json['license_expiry'] as String) ?? DateTime.now()
          : null,
      certifications: json['certifications'] != null
          ? List<String>.from(json['certifications'] as List? ?? [])
          : null,
      totalHoursOperated:
          (json['total_hours_operated'] as num?)?.toDouble() ?? 0,
      sessionsCount: json['sessions_count'] as int? ?? 0,
      isActive: json['is_active'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() => {
        'operator_id': operatorId,
        'name': name,
        'name_ar': nameAr,
        'phone': phone,
        'license_number': licenseNumber,
        'license_expiry': licenseExpiry?.toIso8601String(),
        'certifications': certifications,
        'total_hours_operated': totalHoursOperated,
        'sessions_count': sessionsCount,
        'is_active': isActive,
      };
}
