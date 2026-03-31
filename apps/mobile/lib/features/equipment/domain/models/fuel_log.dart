/// Fuel Log Models - نماذج سجل الوقود
/// Fuel tracking, consumption analysis, and cost management
library;

import 'package:flutter/foundation.dart';
import 'equipment.dart';

/// نوع عملية الوقود - Fuel Operation Type
enum FuelOperationType {
  refuel('refuel', 'تعبئة', 'Refuel'),
  consumption('consumption', 'استهلاك', 'Consumption'),
  transfer('transfer', 'نقل', 'Transfer'),
  adjustment('adjustment', 'تعديل', 'Adjustment'),
  leak('leak', 'تسرب', 'Leak');

  final String value;
  final String nameAr;
  final String nameEn;

  const FuelOperationType(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static FuelOperationType fromString(String value) {
    return FuelOperationType.values.firstWhere(
      (e) => e.value == value,
      orElse: () => FuelOperationType.refuel,
    );
  }
}

/// سجل الوقود - Fuel Log Entry
@immutable
class FuelLog {
  final String logId;
  final String equipmentId;
  final FuelOperationType operationType;
  final FuelType fuelType;
  final double quantity; // Liters
  final double? pricePerLiter;
  final double? totalCost;
  final String? currency;
  final double? odometerReading; // km or hours
  final String? odometerUnit;
  final double? fuelLevelBefore; // Percentage
  final double? fuelLevelAfter; // Percentage
  final String? stationName;
  final String? receiptNumber;
  final String? notes;
  final String? notesAr;
  final DateTime timestamp;
  final DateTime createdAt;
  final String? createdBy;
  final double? lat;
  final double? lon;
  final List<String>? attachments;
  final Map<String, dynamic>? metadata;

  const FuelLog({
    required this.logId,
    required this.equipmentId,
    required this.operationType,
    this.fuelType = FuelType.diesel,
    required this.quantity,
    this.pricePerLiter,
    this.totalCost,
    this.currency = 'SAR',
    this.odometerReading,
    this.odometerUnit = 'hours',
    this.fuelLevelBefore,
    this.fuelLevelAfter,
    this.stationName,
    this.receiptNumber,
    this.notes,
    this.notesAr,
    required this.timestamp,
    required this.createdAt,
    this.createdBy,
    this.lat,
    this.lon,
    this.attachments,
    this.metadata,
  });

  /// Get notes based on locale
  String? getNotes(String locale) {
    if (notes == null && notesAr == null) return null;
    return locale == 'ar' && notesAr != null ? notesAr : notes;
  }

  /// Calculate total cost if not provided
  double get calculatedCost {
    if (totalCost != null) return totalCost!;
    if (pricePerLiter != null) return quantity * pricePerLiter!;
    return 0;
  }

  /// Formatted cost string
  String get formattedCost {
    final cost = calculatedCost;
    if (cost == 0) return '-';
    return '${cost.toStringAsFixed(2)} ${currency ?? 'SAR'}';
  }

  /// Formatted quantity
  String get formattedQuantity => '${quantity.toStringAsFixed(1)} L';

  /// Check if has location
  bool get hasLocation => lat != null && lon != null;

  factory FuelLog.fromJson(Map<String, dynamic> json) {
    return FuelLog(
      logId: json['log_id'] as String,
      equipmentId: json['equipment_id'] as String,
      operationType:
          FuelOperationType.fromString(json['operation_type'] as String),
      fuelType: json['fuel_type'] != null
          ? FuelType.fromString(json['fuel_type'] as String)
          : FuelType.diesel,
      quantity: (json['quantity'] as num).toDouble(),
      pricePerLiter: (json['price_per_liter'] as num?)?.toDouble(),
      totalCost: (json['total_cost'] as num?)?.toDouble(),
      currency: json['currency'] as String? ?? 'SAR',
      odometerReading: (json['odometer_reading'] as num?)?.toDouble(),
      odometerUnit: json['odometer_unit'] as String? ?? 'hours',
      fuelLevelBefore: (json['fuel_level_before'] as num?)?.toDouble(),
      fuelLevelAfter: (json['fuel_level_after'] as num?)?.toDouble(),
      stationName: json['station_name'] as String?,
      receiptNumber: json['receipt_number'] as String?,
      notes: json['notes'] as String?,
      notesAr: json['notes_ar'] as String?,
      timestamp: DateTime.tryParse(json['timestamp'] as String) ?? DateTime.now(),
      createdAt: DateTime.tryParse(json['created_at'] as String) ?? DateTime.now(),
      createdBy: json['created_by'] as String?,
      lat: (json['lat'] as num?)?.toDouble(),
      lon: (json['lon'] as num?)?.toDouble(),
      attachments: json['attachments'] != null
          ? List<String>.from(json['attachments'] as List)
          : null,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'log_id': logId,
        'equipment_id': equipmentId,
        'operation_type': operationType.value,
        'fuel_type': fuelType.value,
        'quantity': quantity,
        'price_per_liter': pricePerLiter,
        'total_cost': totalCost,
        'currency': currency,
        'odometer_reading': odometerReading,
        'odometer_unit': odometerUnit,
        'fuel_level_before': fuelLevelBefore,
        'fuel_level_after': fuelLevelAfter,
        'station_name': stationName,
        'receipt_number': receiptNumber,
        'notes': notes,
        'notes_ar': notesAr,
        'timestamp': timestamp.toIso8601String(),
        'created_at': createdAt.toIso8601String(),
        'created_by': createdBy,
        'lat': lat,
        'lon': lon,
        'attachments': attachments,
        'metadata': metadata,
      };
}

/// ملخص استهلاك الوقود - Fuel Consumption Summary
@immutable
class FuelConsumptionSummary {
  final String equipmentId;
  final double totalFuelConsumed; // Liters
  final double totalCost;
  final String currency;
  final double averageConsumptionPerHour; // Liters/hour
  final double averagePricePerLiter;
  final int refuelCount;
  final double totalHoursOperated;
  final DateTime periodStart;
  final DateTime periodEnd;
  final List<FuelConsumptionByDay>? dailyBreakdown;

  const FuelConsumptionSummary({
    required this.equipmentId,
    required this.totalFuelConsumed,
    required this.totalCost,
    this.currency = 'SAR',
    required this.averageConsumptionPerHour,
    required this.averagePricePerLiter,
    required this.refuelCount,
    required this.totalHoursOperated,
    required this.periodStart,
    required this.periodEnd,
    this.dailyBreakdown,
  });

  /// Cost per hour
  double get costPerHour {
    if (totalHoursOperated == 0) return 0;
    return totalCost / totalHoursOperated;
  }

  /// Efficiency rating (1-5 stars based on consumption)
  int get efficiencyRating {
    // Based on typical tractor consumption (10-15 L/hour is average)
    if (averageConsumptionPerHour <= 8) return 5;
    if (averageConsumptionPerHour <= 12) return 4;
    if (averageConsumptionPerHour <= 15) return 3;
    if (averageConsumptionPerHour <= 20) return 2;
    return 1;
  }

  factory FuelConsumptionSummary.fromJson(Map<String, dynamic> json) {
    return FuelConsumptionSummary(
      equipmentId: json['equipment_id'] as String,
      totalFuelConsumed: (json['total_fuel_consumed'] as num).toDouble(),
      totalCost: (json['total_cost'] as num).toDouble(),
      currency: json['currency'] as String? ?? 'SAR',
      averageConsumptionPerHour:
          (json['average_consumption_per_hour'] as num).toDouble(),
      averagePricePerLiter:
          (json['average_price_per_liter'] as num).toDouble(),
      refuelCount: json['refuel_count'] as int,
      totalHoursOperated: (json['total_hours_operated'] as num).toDouble(),
      periodStart: DateTime.tryParse(json['period_start'] as String) ?? DateTime.now(),
      periodEnd: DateTime.tryParse(json['period_end'] as String) ?? DateTime.now(),
      dailyBreakdown: json['daily_breakdown'] != null
          ? (json['daily_breakdown'] as List)
              .map((e) =>
                  FuelConsumptionByDay.fromJson(e as Map<String, dynamic>))
              .toList()
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'equipment_id': equipmentId,
        'total_fuel_consumed': totalFuelConsumed,
        'total_cost': totalCost,
        'currency': currency,
        'average_consumption_per_hour': averageConsumptionPerHour,
        'average_price_per_liter': averagePricePerLiter,
        'refuel_count': refuelCount,
        'total_hours_operated': totalHoursOperated,
        'period_start': periodStart.toIso8601String(),
        'period_end': periodEnd.toIso8601String(),
        'daily_breakdown':
            dailyBreakdown?.map((e) => e.toJson()).toList(),
      };
}

/// استهلاك الوقود اليومي - Daily Fuel Consumption
@immutable
class FuelConsumptionByDay {
  final DateTime date;
  final double fuelConsumed;
  final double cost;
  final double hoursOperated;
  final double consumptionRate;

  const FuelConsumptionByDay({
    required this.date,
    required this.fuelConsumed,
    required this.cost,
    required this.hoursOperated,
    required this.consumptionRate,
  });

  factory FuelConsumptionByDay.fromJson(Map<String, dynamic> json) {
    return FuelConsumptionByDay(
      date: DateTime.tryParse(json['date'] as String) ?? DateTime.now(),
      fuelConsumed: (json['fuel_consumed'] as num).toDouble(),
      cost: (json['cost'] as num).toDouble(),
      hoursOperated: (json['hours_operated'] as num).toDouble(),
      consumptionRate: (json['consumption_rate'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'date': date.toIso8601String(),
        'fuel_consumed': fuelConsumed,
        'cost': cost,
        'hours_operated': hoursOperated,
        'consumption_rate': consumptionRate,
      };
}

/// تنبيه الوقود - Fuel Alert
@immutable
class FuelAlert {
  final String alertId;
  final String equipmentId;
  final String equipmentName;
  final double currentFuelPercent;
  final double threshold;
  final String message;
  final String? messageAr;
  final DateTime createdAt;
  final bool isAcknowledged;

  const FuelAlert({
    required this.alertId,
    required this.equipmentId,
    required this.equipmentName,
    required this.currentFuelPercent,
    required this.threshold,
    required this.message,
    this.messageAr,
    required this.createdAt,
    this.isAcknowledged = false,
  });

  String getMessage(String locale) {
    return locale == 'ar' && messageAr != null ? messageAr! : message;
  }

  /// Is critical (below 10%)
  bool get isCritical => currentFuelPercent < 10;

  factory FuelAlert.fromJson(Map<String, dynamic> json) {
    return FuelAlert(
      alertId: json['alert_id'] as String,
      equipmentId: json['equipment_id'] as String,
      equipmentName: json['equipment_name'] as String,
      currentFuelPercent: (json['current_fuel_percent'] as num).toDouble(),
      threshold: (json['threshold'] as num).toDouble(),
      message: json['message'] as String,
      messageAr: json['message_ar'] as String?,
      createdAt: DateTime.tryParse(json['created_at'] as String) ?? DateTime.now(),
      isAcknowledged: json['is_acknowledged'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
        'alert_id': alertId,
        'equipment_id': equipmentId,
        'equipment_name': equipmentName,
        'current_fuel_percent': currentFuelPercent,
        'threshold': threshold,
        'message': message,
        'message_ar': messageAr,
        'created_at': createdAt.toIso8601String(),
        'is_acknowledged': isAcknowledged,
      };
}
