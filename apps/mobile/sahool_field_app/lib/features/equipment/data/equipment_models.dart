/// Equipment Models - نماذج المعدات
/// مطابقة لـ FastAPI Equipment Service
/// Enhanced for offline-first support
library;

import 'package:flutter/foundation.dart';

/// نوع الوقود - Fuel Type
enum FuelType {
  diesel('diesel', 'ديزل', 'Diesel'),
  gasoline('gasoline', 'بنزين', 'Gasoline'),
  electric('electric', 'كهربائي', 'Electric'),
  hybrid('hybrid', 'هجين', 'Hybrid'),
  lpg('lpg', 'غاز', 'LPG'),
  none('none', 'لا يوجد', 'None');

  final String value;
  final String nameAr;
  final String nameEn;

  const FuelType(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static FuelType fromString(String value) {
    return FuelType.values.firstWhere(
      (e) => e.value == value,
      orElse: () => FuelType.diesel,
    );
  }
}

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
  iotDevice('iot_device', 'جهاز إنترنت الأشياء', 'IoT Device'),
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

  /// Get icon name for the equipment type
  String get iconName {
    switch (this) {
      case EquipmentType.tractor:
        return 'agriculture';
      case EquipmentType.pump:
        return 'water';
      case EquipmentType.drone:
        return 'flight';
      case EquipmentType.harvester:
        return 'grass';
      case EquipmentType.sprayer:
        return 'shower';
      case EquipmentType.pivot:
        return 'rotate_right';
      case EquipmentType.sensor:
        return 'sensors';
      case EquipmentType.vehicle:
        return 'local_shipping';
      case EquipmentType.iotDevice:
        return 'router';
      case EquipmentType.other:
        return 'build';
    }
  }
}

/// حالة المعدة
enum EquipmentStatus {
  operational('operational', 'تعمل', 'Operational'),
  maintenance('maintenance', 'صيانة', 'Maintenance'),
  inactive('inactive', 'غير نشطة', 'Inactive'),
  repair('repair', 'إصلاح', 'Repair'),
  standby('standby', 'جاهزة', 'Standby'),
  inUse('in_use', 'قيد الاستخدام', 'In Use');

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

  /// Check if equipment is available for use
  bool get isAvailable =>
      this == EquipmentStatus.operational || this == EquipmentStatus.standby;
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

/// نوع عملية الوقود
enum FuelOperationType {
  refuel('refuel', 'تعبئة', 'Refuel'),
  consumption('consumption', 'استهلاك', 'Consumption'),
  transfer('transfer', 'تحويل', 'Transfer'),
  adjustment('adjustment', 'تعديل', 'Adjustment');

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

/// نوع الاستخدام
enum UsageType {
  fieldWork('field_work', 'عمل حقلي', 'Field Work'),
  transport('transport', 'نقل', 'Transport'),
  maintenance('maintenance', 'صيانة', 'Maintenance'),
  idle('idle', 'توقف', 'Idle'),
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

/// نوع النشاط الحقلي
enum FieldActivityType {
  plowing('plowing', 'حراثة', 'Plowing'),
  planting('planting', 'زراعة', 'Planting'),
  harvesting('harvesting', 'حصاد', 'Harvesting'),
  spraying('spraying', 'رش', 'Spraying'),
  irrigation('irrigation', 'ري', 'Irrigation'),
  fertilizing('fertilizing', 'تسميد', 'Fertilizing'),
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
  final FuelType fuelType;
  final double? fuelCapacityLiters;
  final double? currentFuelPercent;
  final double? currentFuelLiters;
  final double? currentHours;
  final double? totalHours;
  final double? currentLat;
  final double? currentLon;
  final DateTime? lastMaintenanceAt;
  final DateTime? nextMaintenanceAt;
  final double? nextMaintenanceHours;
  final DateTime createdAt;
  final DateTime updatedAt;
  final Map<String, dynamic>? metadata;
  final String? qrCode;
  final String? imageUrl;
  final List<String>? attachedFieldIds;
  final double? dailyRentalCost;
  final String? assignedTo;
  final bool isTracked;

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
    this.fuelType = FuelType.diesel,
    this.fuelCapacityLiters,
    this.currentFuelPercent,
    this.currentFuelLiters,
    this.currentHours,
    this.totalHours,
    this.currentLat,
    this.currentLon,
    this.lastMaintenanceAt,
    this.nextMaintenanceAt,
    this.nextMaintenanceHours,
    required this.createdAt,
    required this.updatedAt,
    this.metadata,
    this.qrCode,
    this.imageUrl,
    this.attachedFieldIds,
    this.dailyRentalCost,
    this.assignedTo,
    this.isTracked = false,
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

  /// Check if maintenance is overdue
  bool get isMaintenanceOverdue {
    if (nextMaintenanceAt != null) {
      return nextMaintenanceAt!.isBefore(DateTime.now());
    }
    if (nextMaintenanceHours != null && currentHours != null) {
      return currentHours! >= nextMaintenanceHours!;
    }
    return false;
  }

  /// Check if fuel is low (below 20%)
  bool get isLowFuel => currentFuelPercent != null && currentFuelPercent! < 20;

  /// Check if fuel is critical (below 10%)
  bool get isCriticalFuel =>
      currentFuelPercent != null && currentFuelPercent! < 10;

  /// Get fuel level category
  String getFuelLevelCategory(String locale) {
    if (currentFuelPercent == null) {
      return locale == 'ar' ? 'غير معروف' : 'Unknown';
    }
    if (currentFuelPercent! >= 75) return locale == 'ar' ? 'ممتلئ' : 'Full';
    if (currentFuelPercent! >= 50) return locale == 'ar' ? 'جيد' : 'Good';
    if (currentFuelPercent! >= 25) return locale == 'ar' ? 'متوسط' : 'Medium';
    if (currentFuelPercent! >= 10) return locale == 'ar' ? 'منخفض' : 'Low';
    return locale == 'ar' ? 'حرج' : 'Critical';
  }

  /// Check if equipment has GPS location
  bool get hasLocation => currentLat != null && currentLon != null;

  /// Get full location string
  String get locationString {
    if (!hasLocation) return '';
    return '${currentLat!.toStringAsFixed(6)}, ${currentLon!.toStringAsFixed(6)}';
  }

  /// Calculate age in years
  int? get ageInYears {
    if (year == null) return null;
    return DateTime.now().year - year!;
  }

  /// Get depreciated value (simple linear depreciation over 10 years)
  double? get currentValue {
    if (purchasePrice == null || year == null) return null;
    final age = ageInYears ?? 0;
    if (age >= 10) return purchasePrice! * 0.1; // 10% residual value
    return purchasePrice! * (1 - (age * 0.09)); // 9% per year
  }

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
      fuelType: json['fuel_type'] != null
          ? FuelType.fromString(json['fuel_type'] as String)
          : FuelType.diesel,
      fuelCapacityLiters: (json['fuel_capacity_liters'] as num?)?.toDouble(),
      currentFuelPercent: (json['current_fuel_percent'] as num?)?.toDouble(),
      currentFuelLiters: (json['current_fuel_liters'] as num?)?.toDouble(),
      currentHours: (json['current_hours'] as num?)?.toDouble(),
      totalHours: (json['total_hours'] as num?)?.toDouble(),
      currentLat: (json['current_lat'] as num?)?.toDouble(),
      currentLon: (json['current_lon'] as num?)?.toDouble(),
      lastMaintenanceAt: json['last_maintenance_at'] != null
          ? DateTime.parse(json['last_maintenance_at'] as String)
          : null,
      nextMaintenanceAt: json['next_maintenance_at'] != null
          ? DateTime.parse(json['next_maintenance_at'] as String)
          : null,
      nextMaintenanceHours:
          (json['next_maintenance_hours'] as num?)?.toDouble(),
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      metadata: json['metadata'] as Map<String, dynamic>?,
      qrCode: json['qr_code'] as String?,
      imageUrl: json['image_url'] as String?,
      attachedFieldIds: json['attached_field_ids'] != null
          ? List<String>.from(json['attached_field_ids'] as List)
          : null,
      dailyRentalCost: (json['daily_rental_cost'] as num?)?.toDouble(),
      assignedTo: json['assigned_to'] as String?,
      isTracked: json['is_tracked'] as bool? ?? false,
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
        'fuel_type': fuelType.value,
        'fuel_capacity_liters': fuelCapacityLiters,
        'current_fuel_percent': currentFuelPercent,
        'current_fuel_liters': currentFuelLiters,
        'current_hours': currentHours,
        'total_hours': totalHours,
        'current_lat': currentLat,
        'current_lon': currentLon,
        'last_maintenance_at': lastMaintenanceAt?.toIso8601String(),
        'next_maintenance_at': nextMaintenanceAt?.toIso8601String(),
        'next_maintenance_hours': nextMaintenanceHours,
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
        'metadata': metadata,
        'qr_code': qrCode,
        'image_url': imageUrl,
        'attached_field_ids': attachedFieldIds,
        'daily_rental_cost': dailyRentalCost,
        'assigned_to': assignedTo,
        'is_tracked': isTracked,
      };

  Equipment copyWith({
    String? equipmentId,
    String? tenantId,
    String? name,
    String? nameAr,
    EquipmentType? equipmentType,
    EquipmentStatus? status,
    String? brand,
    String? model,
    String? serialNumber,
    int? year,
    DateTime? purchaseDate,
    double? purchasePrice,
    String? fieldId,
    String? locationName,
    int? horsepower,
    FuelType? fuelType,
    double? fuelCapacityLiters,
    double? currentFuelPercent,
    double? currentFuelLiters,
    double? currentHours,
    double? totalHours,
    double? currentLat,
    double? currentLon,
    DateTime? lastMaintenanceAt,
    DateTime? nextMaintenanceAt,
    double? nextMaintenanceHours,
    DateTime? createdAt,
    DateTime? updatedAt,
    Map<String, dynamic>? metadata,
    String? qrCode,
    String? imageUrl,
    List<String>? attachedFieldIds,
    double? dailyRentalCost,
    String? assignedTo,
    bool? isTracked,
  }) {
    return Equipment(
      equipmentId: equipmentId ?? this.equipmentId,
      tenantId: tenantId ?? this.tenantId,
      name: name ?? this.name,
      nameAr: nameAr ?? this.nameAr,
      equipmentType: equipmentType ?? this.equipmentType,
      status: status ?? this.status,
      brand: brand ?? this.brand,
      model: model ?? this.model,
      serialNumber: serialNumber ?? this.serialNumber,
      year: year ?? this.year,
      purchaseDate: purchaseDate ?? this.purchaseDate,
      purchasePrice: purchasePrice ?? this.purchasePrice,
      fieldId: fieldId ?? this.fieldId,
      locationName: locationName ?? this.locationName,
      horsepower: horsepower ?? this.horsepower,
      fuelType: fuelType ?? this.fuelType,
      fuelCapacityLiters: fuelCapacityLiters ?? this.fuelCapacityLiters,
      currentFuelPercent: currentFuelPercent ?? this.currentFuelPercent,
      currentFuelLiters: currentFuelLiters ?? this.currentFuelLiters,
      currentHours: currentHours ?? this.currentHours,
      totalHours: totalHours ?? this.totalHours,
      currentLat: currentLat ?? this.currentLat,
      currentLon: currentLon ?? this.currentLon,
      lastMaintenanceAt: lastMaintenanceAt ?? this.lastMaintenanceAt,
      nextMaintenanceAt: nextMaintenanceAt ?? this.nextMaintenanceAt,
      nextMaintenanceHours: nextMaintenanceHours ?? this.nextMaintenanceHours,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      metadata: metadata ?? this.metadata,
      qrCode: qrCode ?? this.qrCode,
      imageUrl: imageUrl ?? this.imageUrl,
      attachedFieldIds: attachedFieldIds ?? this.attachedFieldIds,
      dailyRentalCost: dailyRentalCost ?? this.dailyRentalCost,
      assignedTo: assignedTo ?? this.assignedTo,
      isTracked: isTracked ?? this.isTracked,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Equipment &&
          runtimeType == other.runtimeType &&
          equipmentId == other.equipmentId;

  @override
  int get hashCode => equipmentId.hashCode;
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
    return locale == 'ar' && descriptionAr != null
        ? descriptionAr!
        : description;
  }

  factory MaintenanceAlert.fromJson(Map<String, dynamic> json) {
    return MaintenanceAlert(
      alertId: json['alert_id'] as String,
      equipmentId: json['equipment_id'] as String,
      equipmentName: json['equipment_name'] as String,
      maintenanceType:
          MaintenanceType.fromString(json['maintenance_type'] as String),
      description: json['description'] as String,
      descriptionAr: json['description_ar'] as String?,
      priority: MaintenancePriority.fromString(json['priority'] as String),
      dueAt: json['due_at'] != null
          ? DateTime.parse(json['due_at'] as String)
          : null,
      dueHours: (json['due_hours'] as num?)?.toDouble(),
      isOverdue: json['is_overdue'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'alert_id': alertId,
        'equipment_id': equipmentId,
        'equipment_name': equipmentName,
        'maintenance_type': maintenanceType.value,
        'description': description,
        'description_ar': descriptionAr,
        'priority': priority.value,
        'due_at': dueAt?.toIso8601String(),
        'due_hours': dueHours,
        'is_overdue': isOverdue,
        'created_at': createdAt.toIso8601String(),
      };
}

/// سجل صيانة
@immutable
class MaintenanceRecord {
  final String recordId;
  final String equipmentId;
  final MaintenanceType maintenanceType;
  final String description;
  final String? descriptionAr;
  final String? performedBy;
  final double? cost;
  final String? notes;
  final List<String>? partsReplaced;
  final double? hoursAtMaintenance;
  final DateTime performedAt;
  final DateTime createdAt;

  const MaintenanceRecord({
    required this.recordId,
    required this.equipmentId,
    required this.maintenanceType,
    required this.description,
    this.descriptionAr,
    this.performedBy,
    this.cost,
    this.notes,
    this.partsReplaced,
    this.hoursAtMaintenance,
    required this.performedAt,
    required this.createdAt,
  });

  String getDescription(String locale) {
    return locale == 'ar' && descriptionAr != null
        ? descriptionAr!
        : description;
  }

  factory MaintenanceRecord.fromJson(Map<String, dynamic> json) {
    return MaintenanceRecord(
      recordId: json['record_id'] as String? ?? json['id'] as String? ?? '',
      equipmentId: json['equipment_id'] as String,
      maintenanceType:
          MaintenanceType.fromString(json['maintenance_type'] as String),
      description: json['description'] as String,
      descriptionAr: json['description_ar'] as String?,
      performedBy: json['performed_by'] as String?,
      cost: (json['cost'] as num?)?.toDouble(),
      notes: json['notes'] as String?,
      partsReplaced: json['parts_replaced'] != null
          ? List<String>.from(json['parts_replaced'] as List)
          : null,
      hoursAtMaintenance: (json['hours_at_maintenance'] as num?)?.toDouble(),
      performedAt: json['performed_at'] != null
          ? DateTime.parse(json['performed_at'] as String)
          : DateTime.parse(json['created_at'] as String),
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'record_id': recordId,
        'equipment_id': equipmentId,
        'maintenance_type': maintenanceType.value,
        'description': description,
        'description_ar': descriptionAr,
        'performed_by': performedBy,
        'cost': cost,
        'notes': notes,
        'parts_replaced': partsReplaced,
        'hours_at_maintenance': hoursAtMaintenance,
        'performed_at': performedAt.toIso8601String(),
        'created_at': createdAt.toIso8601String(),
      };
}

/// صيانة مجدولة
@immutable
class ScheduledMaintenance {
  final String scheduleId;
  final String equipmentId;
  final String equipmentName;
  final MaintenanceType maintenanceType;
  final MaintenancePriority priority;
  final String description;
  final String? descriptionAr;
  final DateTime scheduledDate;
  final double? scheduledAtHours;
  final bool isRecurring;
  final int? recurringIntervalDays;
  final int? recurringIntervalHours;
  final bool isCompleted;
  final DateTime createdAt;

  const ScheduledMaintenance({
    required this.scheduleId,
    required this.equipmentId,
    required this.equipmentName,
    required this.maintenanceType,
    required this.priority,
    required this.description,
    this.descriptionAr,
    required this.scheduledDate,
    this.scheduledAtHours,
    this.isRecurring = false,
    this.recurringIntervalDays,
    this.recurringIntervalHours,
    this.isCompleted = false,
    required this.createdAt,
  });

  String getDescription(String locale) {
    return locale == 'ar' && descriptionAr != null
        ? descriptionAr!
        : description;
  }

  factory ScheduledMaintenance.fromJson(Map<String, dynamic> json) {
    return ScheduledMaintenance(
      scheduleId: json['schedule_id'] as String,
      equipmentId: json['equipment_id'] as String,
      equipmentName: json['equipment_name'] as String? ?? '',
      maintenanceType:
          MaintenanceType.fromString(json['maintenance_type'] as String),
      priority: MaintenancePriority.fromString(json['priority'] as String),
      description: json['description'] as String,
      descriptionAr: json['description_ar'] as String?,
      scheduledDate: DateTime.parse(json['scheduled_date'] as String),
      scheduledAtHours: (json['scheduled_at_hours'] as num?)?.toDouble(),
      isRecurring: json['is_recurring'] as bool? ?? false,
      recurringIntervalDays: json['recurring_interval_days'] as int?,
      recurringIntervalHours: json['recurring_interval_hours'] as int?,
      isCompleted: json['is_completed'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'schedule_id': scheduleId,
        'equipment_id': equipmentId,
        'equipment_name': equipmentName,
        'maintenance_type': maintenanceType.value,
        'priority': priority.value,
        'description': description,
        'description_ar': descriptionAr,
        'scheduled_date': scheduledDate.toIso8601String(),
        'scheduled_at_hours': scheduledAtHours,
        'is_recurring': isRecurring,
        'recurring_interval_days': recurringIntervalDays,
        'recurring_interval_hours': recurringIntervalHours,
        'is_completed': isCompleted,
        'created_at': createdAt.toIso8601String(),
      };
}

/// سجل الوقود
@immutable
class FuelLog {
  final String logId;
  final String equipmentId;
  final FuelOperationType operationType;
  final FuelType? fuelType;
  final double quantity;
  final double? pricePerLiter;
  final double? totalCost;
  final double? odometerReading;
  final String? odometerUnit;
  final double? fuelLevelBefore;
  final double? fuelLevelAfter;
  final String? stationName;
  final String? receiptNumber;
  final String? notes;
  final String? notesAr;
  final double? lat;
  final double? lon;
  final DateTime timestamp;
  final DateTime createdAt;

  const FuelLog({
    required this.logId,
    required this.equipmentId,
    required this.operationType,
    this.fuelType,
    required this.quantity,
    this.pricePerLiter,
    this.totalCost,
    this.odometerReading,
    this.odometerUnit,
    this.fuelLevelBefore,
    this.fuelLevelAfter,
    this.stationName,
    this.receiptNumber,
    this.notes,
    this.notesAr,
    this.lat,
    this.lon,
    required this.timestamp,
    required this.createdAt,
  });

  String getNotes(String locale) {
    return locale == 'ar' && notesAr != null ? notesAr! : (notes ?? '');
  }

  factory FuelLog.fromJson(Map<String, dynamic> json) {
    return FuelLog(
      logId: json['log_id'] as String? ?? json['id'] as String? ?? '',
      equipmentId: json['equipment_id'] as String,
      operationType:
          FuelOperationType.fromString(json['operation_type'] as String),
      fuelType: json['fuel_type'] != null
          ? FuelType.fromString(json['fuel_type'] as String)
          : null,
      quantity: (json['quantity'] as num).toDouble(),
      pricePerLiter: (json['price_per_liter'] as num?)?.toDouble(),
      totalCost: (json['total_cost'] as num?)?.toDouble(),
      odometerReading: (json['odometer_reading'] as num?)?.toDouble(),
      odometerUnit: json['odometer_unit'] as String?,
      fuelLevelBefore: (json['fuel_level_before'] as num?)?.toDouble(),
      fuelLevelAfter: (json['fuel_level_after'] as num?)?.toDouble(),
      stationName: json['station_name'] as String?,
      receiptNumber: json['receipt_number'] as String?,
      notes: json['notes'] as String?,
      notesAr: json['notes_ar'] as String?,
      lat: (json['lat'] as num?)?.toDouble(),
      lon: (json['lon'] as num?)?.toDouble(),
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'] as String)
          : DateTime.parse(json['created_at'] as String),
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'log_id': logId,
        'equipment_id': equipmentId,
        'operation_type': operationType.value,
        'fuel_type': fuelType?.value,
        'quantity': quantity,
        'price_per_liter': pricePerLiter,
        'total_cost': totalCost,
        'odometer_reading': odometerReading,
        'odometer_unit': odometerUnit,
        'fuel_level_before': fuelLevelBefore,
        'fuel_level_after': fuelLevelAfter,
        'station_name': stationName,
        'receipt_number': receiptNumber,
        'notes': notes,
        'notes_ar': notesAr,
        'lat': lat,
        'lon': lon,
        'timestamp': timestamp.toIso8601String(),
        'created_at': createdAt.toIso8601String(),
      };
}

/// سجل الاستخدام
@immutable
class UsageLog {
  final String logId;
  final String equipmentId;
  final UsageType usageType;
  final FieldActivityType? activityType;
  final String? fieldId;
  final String? operatorId;
  final String? operatorName;
  final DateTime startTime;
  final DateTime? endTime;
  final double? startHourReading;
  final double? endHourReading;
  final double? hoursUsed;
  final double? fuelUsed;
  final double? areaWorked;
  final double? distanceTraveled;
  final String? notes;
  final String? notesAr;
  final DateTime createdAt;

  const UsageLog({
    required this.logId,
    required this.equipmentId,
    required this.usageType,
    this.activityType,
    this.fieldId,
    this.operatorId,
    this.operatorName,
    required this.startTime,
    this.endTime,
    this.startHourReading,
    this.endHourReading,
    this.hoursUsed,
    this.fuelUsed,
    this.areaWorked,
    this.distanceTraveled,
    this.notes,
    this.notesAr,
    required this.createdAt,
  });

  /// Check if session is still active
  bool get isActive => endTime == null;

  /// Get duration of session
  Duration? get duration {
    if (endTime == null) return null;
    return endTime!.difference(startTime);
  }

  String getNotes(String locale) {
    return locale == 'ar' && notesAr != null ? notesAr! : (notes ?? '');
  }

  factory UsageLog.fromJson(Map<String, dynamic> json) {
    return UsageLog(
      logId: json['log_id'] as String? ?? json['id'] as String? ?? '',
      equipmentId: json['equipment_id'] as String,
      usageType: UsageType.fromString(json['usage_type'] as String),
      activityType: json['activity_type'] != null
          ? FieldActivityType.fromString(json['activity_type'] as String)
          : null,
      fieldId: json['field_id'] as String?,
      operatorId: json['operator_id'] as String?,
      operatorName: json['operator_name'] as String?,
      startTime: DateTime.parse(json['start_time'] as String),
      endTime: json['end_time'] != null
          ? DateTime.parse(json['end_time'] as String)
          : null,
      startHourReading: (json['start_hour_reading'] as num?)?.toDouble(),
      endHourReading: (json['end_hour_reading'] as num?)?.toDouble(),
      hoursUsed: (json['hours_used'] as num?)?.toDouble(),
      fuelUsed: (json['fuel_used'] as num?)?.toDouble(),
      areaWorked: (json['area_worked'] as num?)?.toDouble(),
      distanceTraveled: (json['distance_traveled'] as num?)?.toDouble(),
      notes: json['notes'] as String?,
      notesAr: json['notes_ar'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'log_id': logId,
        'equipment_id': equipmentId,
        'usage_type': usageType.value,
        'activity_type': activityType?.value,
        'field_id': fieldId,
        'operator_id': operatorId,
        'operator_name': operatorName,
        'start_time': startTime.toIso8601String(),
        'end_time': endTime?.toIso8601String(),
        'start_hour_reading': startHourReading,
        'end_hour_reading': endHourReading,
        'hours_used': hoursUsed,
        'fuel_used': fuelUsed,
        'area_worked': areaWorked,
        'distance_traveled': distanceTraveled,
        'notes': notes,
        'notes_ar': notesAr,
        'created_at': createdAt.toIso8601String(),
      };
}

/// ملخص استهلاك الوقود
@immutable
class FuelConsumptionSummary {
  final String equipmentId;
  final DateTime from;
  final DateTime to;
  final double totalConsumed;
  final double totalCost;
  final double averagePricePerLiter;
  final double averageConsumptionPerHour;
  final int refillCount;

  const FuelConsumptionSummary({
    required this.equipmentId,
    required this.from,
    required this.to,
    required this.totalConsumed,
    required this.totalCost,
    required this.averagePricePerLiter,
    required this.averageConsumptionPerHour,
    required this.refillCount,
  });

  factory FuelConsumptionSummary.fromJson(Map<String, dynamic> json) {
    return FuelConsumptionSummary(
      equipmentId: json['equipment_id'] as String,
      from: DateTime.parse(json['from'] as String),
      to: DateTime.parse(json['to'] as String),
      totalConsumed: (json['total_consumed'] as num).toDouble(),
      totalCost: (json['total_cost'] as num).toDouble(),
      averagePricePerLiter: (json['average_price_per_liter'] as num).toDouble(),
      averageConsumptionPerHour:
          (json['average_consumption_per_hour'] as num).toDouble(),
      refillCount: json['refill_count'] as int,
    );
  }

  Map<String, dynamic> toJson() => {
        'equipment_id': equipmentId,
        'from': from.toIso8601String(),
        'to': to.toIso8601String(),
        'total_consumed': totalConsumed,
        'total_cost': totalCost,
        'average_price_per_liter': averagePricePerLiter,
        'average_consumption_per_hour': averageConsumptionPerHour,
        'refill_count': refillCount,
      };
}

/// ملخص الاستخدام
@immutable
class UsageSummary {
  final String equipmentId;
  final DateTime from;
  final DateTime to;
  final double totalHours;
  final double totalFuelUsed;
  final double totalAreaWorked;
  final double totalDistanceTraveled;
  final int sessionCount;
  final Map<String, double> byUsageType;
  final Map<String, double> byActivityType;

  const UsageSummary({
    required this.equipmentId,
    required this.from,
    required this.to,
    required this.totalHours,
    required this.totalFuelUsed,
    required this.totalAreaWorked,
    required this.totalDistanceTraveled,
    required this.sessionCount,
    required this.byUsageType,
    required this.byActivityType,
  });

  factory UsageSummary.fromJson(Map<String, dynamic> json) {
    return UsageSummary(
      equipmentId: json['equipment_id'] as String,
      from: DateTime.parse(json['from'] as String),
      to: DateTime.parse(json['to'] as String),
      totalHours: (json['total_hours'] as num).toDouble(),
      totalFuelUsed: (json['total_fuel_used'] as num).toDouble(),
      totalAreaWorked: (json['total_area_worked'] as num).toDouble(),
      totalDistanceTraveled:
          (json['total_distance_traveled'] as num).toDouble(),
      sessionCount: json['session_count'] as int,
      byUsageType: Map<String, double>.from(
        (json['by_usage_type'] as Map)
            .map((k, v) => MapEntry(k.toString(), (v as num).toDouble())),
      ),
      byActivityType: Map<String, double>.from(
        (json['by_activity_type'] as Map)
            .map((k, v) => MapEntry(k.toString(), (v as num).toDouble())),
      ),
    );
  }

  Map<String, dynamic> toJson() => {
        'equipment_id': equipmentId,
        'from': from.toIso8601String(),
        'to': to.toIso8601String(),
        'total_hours': totalHours,
        'total_fuel_used': totalFuelUsed,
        'total_area_worked': totalAreaWorked,
        'total_distance_traveled': totalDistanceTraveled,
        'session_count': sessionCount,
        'by_usage_type': byUsageType,
        'by_activity_type': byActivityType,
      };
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
  final int lowFuel;
  final int needsMaintenance;
  final double totalValue;
  final double totalHours;
  final DateTime? lastUpdated;

  const EquipmentStats({
    required this.total,
    required this.byType,
    required this.byStatus,
    required this.operational,
    required this.maintenance,
    required this.inactive,
    this.lowFuel = 0,
    this.needsMaintenance = 0,
    this.totalValue = 0,
    this.totalHours = 0,
    this.lastUpdated,
  });

  factory EquipmentStats.fromJson(Map<String, dynamic> json) {
    return EquipmentStats(
      total: json['total'] as int,
      byType: Map<String, int>.from(json['by_type'] as Map),
      byStatus: Map<String, int>.from(json['by_status'] as Map),
      operational: json['operational'] as int,
      maintenance: json['maintenance'] as int,
      inactive: json['inactive'] as int,
      lowFuel: json['low_fuel'] as int? ?? 0,
      needsMaintenance: json['needs_maintenance'] as int? ?? 0,
      totalValue: (json['total_value'] as num?)?.toDouble() ?? 0,
      totalHours: (json['total_hours'] as num?)?.toDouble() ?? 0,
      lastUpdated: json['last_updated'] != null
          ? DateTime.parse(json['last_updated'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'total': total,
        'by_type': byType,
        'by_status': byStatus,
        'operational': operational,
        'maintenance': maintenance,
        'inactive': inactive,
        'low_fuel': lowFuel,
        'needs_maintenance': needsMaintenance,
        'total_value': totalValue,
        'total_hours': totalHours,
        'last_updated': lastUpdated?.toIso8601String(),
      };
}
