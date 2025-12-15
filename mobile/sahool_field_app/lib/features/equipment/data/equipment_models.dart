/// Equipment Models - نماذج المعدات
/// مطابقة لـ FastAPI Equipment Service
library;

import 'package:flutter/foundation.dart';

/// نوع المعدة
enum EquipmentType {
  tractor('tractor', 'جرار', 'Tractor'),
  pump('pump', 'مضخة', 'Pump'),
  drone('drone', 'طائرة مسيرة', 'Drone'),
  harvester('harvester', 'حاصدة', 'Harvester'),
  sprayer('sprayer', 'رشاش', 'Sprayer'),
  pivot('pivot', 'رشاش محوري', 'Center Pivot'),
  sensor('sensor', 'حساس', 'Sensor'),
  vehicle('vehicle', 'مركبة', 'Vehicle'),
  other('other', 'أخرى', 'Other');

  final String value;
  final String nameAr;
  final String nameEn;

  const EquipmentType(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static EquipmentType fromString(String value) {
    return EquipmentType.values.firstWhere(
      (e) => e.value == value,
      orElse: () => EquipmentType.other,
    );
  }
}

/// حالة المعدة
enum EquipmentStatus {
  operational('operational', 'تعمل', 'Operational'),
  maintenance('maintenance', 'صيانة', 'Maintenance'),
  inactive('inactive', 'غير نشطة', 'Inactive'),
  repair('repair', 'إصلاح', 'Repair');

  final String value;
  final String nameAr;
  final String nameEn;

  const EquipmentStatus(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static EquipmentStatus fromString(String value) {
    return EquipmentStatus.values.firstWhere(
      (e) => e.value == value,
      orElse: () => EquipmentStatus.inactive,
    );
  }
}

/// أولوية الصيانة
enum MaintenancePriority {
  low('low', 'منخفضة', 'Low'),
  medium('medium', 'متوسطة', 'Medium'),
  high('high', 'عالية', 'High'),
  critical('critical', 'حرجة', 'Critical');

  final String value;
  final String nameAr;
  final String nameEn;

  const MaintenancePriority(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static MaintenancePriority fromString(String value) {
    return MaintenancePriority.values.firstWhere(
      (e) => e.value == value,
      orElse: () => MaintenancePriority.low,
    );
  }
}

/// نوع الصيانة
enum MaintenanceType {
  oilChange('oil_change', 'تغيير زيت', 'Oil Change'),
  filterChange('filter_change', 'تغيير فلتر', 'Filter Change'),
  tireCheck('tire_check', 'فحص إطارات', 'Tire Check'),
  batteryCheck('battery_check', 'فحص بطارية', 'Battery Check'),
  calibration('calibration', 'معايرة', 'Calibration'),
  generalService('general_service', 'صيانة عامة', 'General Service'),
  repair('repair', 'إصلاح', 'Repair'),
  other('other', 'أخرى', 'Other');

  final String value;
  final String nameAr;
  final String nameEn;

  const MaintenanceType(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static MaintenanceType fromString(String value) {
    return MaintenanceType.values.firstWhere(
      (e) => e.value == value,
      orElse: () => MaintenanceType.other,
    );
  }
}

/// نموذج المعدة
@immutable
class Equipment {
  final String equipmentId;
  final String tenantId;
  final String name;
  final String? nameAr;
  final EquipmentType equipmentType;
  final EquipmentStatus status;
  final String? brand;
  final String? model;
  final String? serialNumber;
  final int? year;
  final DateTime? purchaseDate;
  final double? purchasePrice;
  final String? fieldId;
  final String? locationName;
  final int? horsepower;
  final double? fuelCapacityLiters;
  final double? currentFuelPercent;
  final double? currentHours;
  final double? currentLat;
  final double? currentLon;
  final DateTime? lastMaintenanceAt;
  final DateTime? nextMaintenanceAt;
  final double? nextMaintenanceHours;
  final DateTime createdAt;
  final DateTime updatedAt;
  final Map<String, dynamic>? metadata;
  final String? qrCode;

  const Equipment({
    required this.equipmentId,
    required this.tenantId,
    required this.name,
    this.nameAr,
    required this.equipmentType,
    required this.status,
    this.brand,
    this.model,
    this.serialNumber,
    this.year,
    this.purchaseDate,
    this.purchasePrice,
    this.fieldId,
    this.locationName,
    this.horsepower,
    this.fuelCapacityLiters,
    this.currentFuelPercent,
    this.currentHours,
    this.currentLat,
    this.currentLon,
    this.lastMaintenanceAt,
    this.nextMaintenanceAt,
    this.nextMaintenanceHours,
    required this.createdAt,
    required this.updatedAt,
    this.metadata,
    this.qrCode,
  });

  /// Get display name based on locale
  String getDisplayName(String locale) {
    return locale == 'ar' && nameAr != null ? nameAr! : name;
  }

  /// Check if equipment needs maintenance soon
  bool get needsMaintenanceSoon {
    if (nextMaintenanceAt != null) {
      return nextMaintenanceAt!.difference(DateTime.now()).inDays <= 7;
    }
    if (nextMaintenanceHours != null && currentHours != null) {
      return (nextMaintenanceHours! - currentHours!) <= 50;
    }
    return false;
  }

  /// Check if fuel is low
  bool get isLowFuel => currentFuelPercent != null && currentFuelPercent! < 20;

  factory Equipment.fromJson(Map<String, dynamic> json) {
    return Equipment(
      equipmentId: json['equipment_id'] as String,
      tenantId: json['tenant_id'] as String,
      name: json['name'] as String,
      nameAr: json['name_ar'] as String?,
      equipmentType: EquipmentType.fromString(json['equipment_type'] as String),
      status: EquipmentStatus.fromString(json['status'] as String),
      brand: json['brand'] as String?,
      model: json['model'] as String?,
      serialNumber: json['serial_number'] as String?,
      year: json['year'] as int?,
      purchaseDate: json['purchase_date'] != null
          ? DateTime.parse(json['purchase_date'] as String)
          : null,
      purchasePrice: (json['purchase_price'] as num?)?.toDouble(),
      fieldId: json['field_id'] as String?,
      locationName: json['location_name'] as String?,
      horsepower: json['horsepower'] as int?,
      fuelCapacityLiters: (json['fuel_capacity_liters'] as num?)?.toDouble(),
      currentFuelPercent: (json['current_fuel_percent'] as num?)?.toDouble(),
      currentHours: (json['current_hours'] as num?)?.toDouble(),
      currentLat: (json['current_lat'] as num?)?.toDouble(),
      currentLon: (json['current_lon'] as num?)?.toDouble(),
      lastMaintenanceAt: json['last_maintenance_at'] != null
          ? DateTime.parse(json['last_maintenance_at'] as String)
          : null,
      nextMaintenanceAt: json['next_maintenance_at'] != null
          ? DateTime.parse(json['next_maintenance_at'] as String)
          : null,
      nextMaintenanceHours: (json['next_maintenance_hours'] as num?)?.toDouble(),
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      metadata: json['metadata'] as Map<String, dynamic>?,
      qrCode: json['qr_code'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'equipment_id': equipmentId,
    'tenant_id': tenantId,
    'name': name,
    'name_ar': nameAr,
    'equipment_type': equipmentType.value,
    'status': status.value,
    'brand': brand,
    'model': model,
    'serial_number': serialNumber,
    'year': year,
    'purchase_date': purchaseDate?.toIso8601String(),
    'purchase_price': purchasePrice,
    'field_id': fieldId,
    'location_name': locationName,
    'horsepower': horsepower,
    'fuel_capacity_liters': fuelCapacityLiters,
    'current_fuel_percent': currentFuelPercent,
    'current_hours': currentHours,
    'current_lat': currentLat,
    'current_lon': currentLon,
    'last_maintenance_at': lastMaintenanceAt?.toIso8601String(),
    'next_maintenance_at': nextMaintenanceAt?.toIso8601String(),
    'next_maintenance_hours': nextMaintenanceHours,
    'created_at': createdAt.toIso8601String(),
    'updated_at': updatedAt.toIso8601String(),
    'metadata': metadata,
    'qr_code': qrCode,
  };
}

/// تنبيه الصيانة
@immutable
class MaintenanceAlert {
  final String alertId;
  final String equipmentId;
  final String equipmentName;
  final MaintenanceType maintenanceType;
  final String description;
  final String? descriptionAr;
  final MaintenancePriority priority;
  final DateTime? dueAt;
  final double? dueHours;
  final bool isOverdue;
  final DateTime createdAt;

  const MaintenanceAlert({
    required this.alertId,
    required this.equipmentId,
    required this.equipmentName,
    required this.maintenanceType,
    required this.description,
    this.descriptionAr,
    required this.priority,
    this.dueAt,
    this.dueHours,
    required this.isOverdue,
    required this.createdAt,
  });

  String getDescription(String locale) {
    return locale == 'ar' && descriptionAr != null ? descriptionAr! : description;
  }

  factory MaintenanceAlert.fromJson(Map<String, dynamic> json) {
    return MaintenanceAlert(
      alertId: json['alert_id'] as String,
      equipmentId: json['equipment_id'] as String,
      equipmentName: json['equipment_name'] as String,
      maintenanceType: MaintenanceType.fromString(json['maintenance_type'] as String),
      description: json['description'] as String,
      descriptionAr: json['description_ar'] as String?,
      priority: MaintenancePriority.fromString(json['priority'] as String),
      dueAt: json['due_at'] != null ? DateTime.parse(json['due_at'] as String) : null,
      dueHours: (json['due_hours'] as num?)?.toDouble(),
      isOverdue: json['is_overdue'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

/// إحصائيات المعدات
@immutable
class EquipmentStats {
  final int total;
  final Map<String, int> byType;
  final Map<String, int> byStatus;
  final int operational;
  final int maintenance;
  final int inactive;

  const EquipmentStats({
    required this.total,
    required this.byType,
    required this.byStatus,
    required this.operational,
    required this.maintenance,
    required this.inactive,
  });

  factory EquipmentStats.fromJson(Map<String, dynamic> json) {
    return EquipmentStats(
      total: json['total'] as int,
      byType: Map<String, int>.from(json['by_type'] as Map),
      byStatus: Map<String, int>.from(json['by_status'] as Map),
      operational: json['operational'] as int,
      maintenance: json['maintenance'] as int,
      inactive: json['inactive'] as int,
    );
  }
}
