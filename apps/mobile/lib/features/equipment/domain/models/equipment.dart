/// Equipment Domain Model - نموذج المعدة
/// Enhanced equipment model with full specifications
library;

import 'package:flutter/foundation.dart';

/// نوع المعدة - Equipment Type
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

/// حالة المعدة - Equipment Status
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

/// نموذج المعدة الكامل - Full Equipment Model
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
    if (currentFuelPercent == null) return locale == 'ar' ? 'غير معروف' : 'Unknown';
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
