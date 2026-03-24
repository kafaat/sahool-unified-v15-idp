/// VRA Models - نماذج التطبيق المتغير
/// Variable Rate Application - تطبيق الجرعات المتغيرة
library;

import 'package:flutter/foundation.dart';

/// نوع VRA
enum VRAType {
  fertilizer('fertilizer', 'سماد', 'Fertilizer'),
  seed('seed', 'بذور', 'Seed'),
  pesticide('pesticide', 'مبيد', 'Pesticide'),
  irrigation('irrigation', 'ري', 'Irrigation');

  final String value;
  final String nameAr;
  final String nameEn;

  const VRAType(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static VRAType fromString(String value) {
    return VRAType.values.firstWhere(
      (e) => e.value == value,
      orElse: () => VRAType.fertilizer,
    );
  }
}

/// حالة الوصفة
enum PrescriptionStatus {
  draft('draft', 'مسودة', 'Draft'),
  approved('approved', 'معتمد', 'Approved'),
  applied('applied', 'مطبق', 'Applied'),
  cancelled('cancelled', 'ملغي', 'Cancelled');

  final String value;
  final String nameAr;
  final String nameEn;

  const PrescriptionStatus(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static PrescriptionStatus fromString(String value) {
    return PrescriptionStatus.values.firstWhere(
      (e) => e.value == value,
      orElse: () => PrescriptionStatus.draft,
    );
  }
}

/// طريقة تقسيم المناطق
enum ZoningMethod {
  manual('manual', 'يدوي', 'Manual'),
  ndvi('ndvi', 'NDVI', 'NDVI'),
  soilType('soil_type', 'نوع التربة', 'Soil Type'),
  elevation('elevation', 'الارتفاع', 'Elevation'),
  yield('yield', 'الإنتاجية', 'Yield');

  final String value;
  final String nameAr;
  final String nameEn;

  const ZoningMethod(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static ZoningMethod fromString(String value) {
    return ZoningMethod.values.firstWhere(
      (e) => e.value == value,
      orElse: () => ZoningMethod.manual,
    );
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// Models
// ═════════════════════════════════════════════════════════════════════════════

/// نموذج منطقة الإدارة
@immutable
class ManagementZone {
  final String zoneId;
  final int zoneNumber;
  final String name;
  final String? nameAr;
  final double area; // بالهكتار
  final Map<String, dynamic> geometry; // GeoJSON geometry
  final double? averageNdvi;
  final double? averageElevation;
  final String? soilType;
  final String? soilTypeAr;
  final Map<String, dynamic>? properties;
  final DateTime createdAt;
  final DateTime updatedAt;

  const ManagementZone({
    required this.zoneId,
    required this.zoneNumber,
    required this.name,
    this.nameAr,
    required this.area,
    required this.geometry,
    this.averageNdvi,
    this.averageElevation,
    this.soilType,
    this.soilTypeAr,
    this.properties,
    required this.createdAt,
    required this.updatedAt,
  });

  /// Get display name based on locale
  String getDisplayName(String locale) {
    return locale == 'ar' && nameAr != null ? nameAr! : name;
  }

  /// Get soil type based on locale
  String? getSoilType(String locale) {
    return locale == 'ar' && soilTypeAr != null ? soilTypeAr : soilType;
  }

  factory ManagementZone.fromJson(Map<String, dynamic> json) {
    return ManagementZone(
      zoneId: json['zone_id'] as String,
      zoneNumber: json['zone_number'] as int,
      name: json['name'] as String,
      nameAr: json['name_ar'] as String?,
      area: (json['area'] as num).toDouble(),
      geometry: json['geometry'] as Map<String, dynamic>,
      averageNdvi: (json['average_ndvi'] as num?)?.toDouble(),
      averageElevation: (json['average_elevation'] as num?)?.toDouble(),
      soilType: json['soil_type'] as String?,
      soilTypeAr: json['soil_type_ar'] as String?,
      properties: json['properties'] as Map<String, dynamic>?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'zone_id': zoneId,
        'zone_number': zoneNumber,
        'name': name,
        'name_ar': nameAr,
        'area': area,
        'geometry': geometry,
        'average_ndvi': averageNdvi,
        'average_elevation': averageElevation,
        'soil_type': soilType,
        'soil_type_ar': soilTypeAr,
        'properties': properties,
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
      };
}

/// نموذج معدل التطبيق
@immutable
class ApplicationRate {
  final String rateId;
  final String zoneId;
  final double rate; // معدل التطبيق (kg/ha أو L/ha أو seeds/ha)
  final String unit; // وحدة القياس
  final String? unitAr;
  final String? productName;
  final String? productNameAr;
  final double? cost; // التكلفة لكل وحدة
  final String? notes;
  final String? notesAr;
  final Map<String, dynamic>? metadata;

  const ApplicationRate({
    required this.rateId,
    required this.zoneId,
    required this.rate,
    required this.unit,
    this.unitAr,
    this.productName,
    this.productNameAr,
    this.cost,
    this.notes,
    this.notesAr,
    this.metadata,
  });

  /// Get product name based on locale
  String? getProductName(String locale) {
    return locale == 'ar' && productNameAr != null ? productNameAr : productName;
  }

  /// Get unit based on locale
  String getUnit(String locale) {
    return locale == 'ar' && unitAr != null ? unitAr! : unit;
  }

  /// Get notes based on locale
  String? getNotes(String locale) {
    return locale == 'ar' && notesAr != null ? notesAr : notes;
  }

  /// حساب التكلفة الإجمالية
  double? getTotalCost(double area) {
    if (cost == null) return null;
    return cost! * rate * area;
  }

  factory ApplicationRate.fromJson(Map<String, dynamic> json) {
    return ApplicationRate(
      rateId: json['rate_id'] as String,
      zoneId: json['zone_id'] as String,
      rate: (json['rate'] as num).toDouble(),
      unit: json['unit'] as String,
      unitAr: json['unit_ar'] as String?,
      productName: json['product_name'] as String?,
      productNameAr: json['product_name_ar'] as String?,
      cost: (json['cost'] as num?)?.toDouble(),
      notes: json['notes'] as String?,
      notesAr: json['notes_ar'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'rate_id': rateId,
        'zone_id': zoneId,
        'rate': rate,
        'unit': unit,
        'unit_ar': unitAr,
        'product_name': productName,
        'product_name_ar': productNameAr,
        'cost': cost,
        'notes': notes,
        'notes_ar': notesAr,
        'metadata': metadata,
      };
}

/// نموذج وصفة VRA
@immutable
class VRAPrescription {
  final String prescriptionId;
  final String tenantId;
  final String fieldId;
  final String fieldName;
  final String? fieldNameAr;
  final String name;
  final String? nameAr;
  final VRAType vraType;
  final PrescriptionStatus status;
  final ZoningMethod zoningMethod;
  final int zonesCount;
  final double totalArea; // بالهكتار
  final List<ManagementZone> zones;
  final List<ApplicationRate> rates;
  final DateTime? scheduledDate;
  final DateTime? appliedDate;
  final String? createdBy;
  final String? createdByName;
  final String? approvedBy;
  final String? approvedByName;
  final DateTime? approvedAt;
  final String? notes;
  final String? notesAr;
  final Map<String, dynamic>? parameters;
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;
  final DateTime updatedAt;

  const VRAPrescription({
    required this.prescriptionId,
    required this.tenantId,
    required this.fieldId,
    required this.fieldName,
    this.fieldNameAr,
    required this.name,
    this.nameAr,
    required this.vraType,
    required this.status,
    required this.zoningMethod,
    required this.zonesCount,
    required this.totalArea,
    required this.zones,
    required this.rates,
    this.scheduledDate,
    this.appliedDate,
    this.createdBy,
    this.createdByName,
    this.approvedBy,
    this.approvedByName,
    this.approvedAt,
    this.notes,
    this.notesAr,
    this.parameters,
    this.metadata,
    required this.createdAt,
    required this.updatedAt,
  });

  /// Get display name based on locale
  String getDisplayName(String locale) {
    return locale == 'ar' && nameAr != null ? nameAr! : name;
  }

  /// Get field name based on locale
  String getFieldName(String locale) {
    return locale == 'ar' && fieldNameAr != null ? fieldNameAr! : fieldName;
  }

  /// Get notes based on locale
  String? getNotes(String locale) {
    return locale == 'ar' && notesAr != null ? notesAr : notes;
  }

  /// هل الوصفة قابلة للتعديل؟
  bool get isEditable => status == PrescriptionStatus.draft;

  /// هل الوصفة قابلة للاعتماد؟
  bool get canBeApproved => status == PrescriptionStatus.draft;

  /// هل الوصفة قابلة للتطبيق؟
  bool get canBeApplied => status == PrescriptionStatus.approved;

  /// هل تم تطبيق الوصفة؟
  bool get isApplied => status == PrescriptionStatus.applied;

  /// حساب التكلفة الإجمالية
  double getTotalCost() {
    double total = 0;
    for (final rate in rates) {
      final zone = zones.firstWhere((z) => z.zoneId == rate.zoneId);
      final zoneCost = rate.getTotalCost(zone.area);
      if (zoneCost != null) {
        total += zoneCost;
      }
    }
    return total;
  }

  /// حساب الكمية الإجمالية
  double getTotalQuantity() {
    double total = 0;
    for (final rate in rates) {
      final zone = zones.firstWhere((z) => z.zoneId == rate.zoneId);
      total += rate.rate * zone.area;
    }
    return total;
  }

  /// حساب متوسط معدل التطبيق
  double getAverageRate() {
    if (totalArea == 0) return 0;
    return getTotalQuantity() / totalArea;
  }

  factory VRAPrescription.fromJson(Map<String, dynamic> json) {
    return VRAPrescription(
      prescriptionId: json['prescription_id'] as String,
      tenantId: json['tenant_id'] as String,
      fieldId: json['field_id'] as String,
      fieldName: json['field_name'] as String,
      fieldNameAr: json['field_name_ar'] as String?,
      name: json['name'] as String,
      nameAr: json['name_ar'] as String?,
      vraType: VRAType.fromString(json['vra_type'] as String),
      status: PrescriptionStatus.fromString(json['status'] as String),
      zoningMethod: ZoningMethod.fromString(json['zoning_method'] as String),
      zonesCount: json['zones_count'] as int,
      totalArea: (json['total_area'] as num).toDouble(),
      zones: (json['zones'] as List)
          .map((e) => ManagementZone.fromJson(e as Map<String, dynamic>))
          .toList(),
      rates: (json['rates'] as List)
          .map((e) => ApplicationRate.fromJson(e as Map<String, dynamic>))
          .toList(),
      scheduledDate: json['scheduled_date'] != null
          ? DateTime.parse(json['scheduled_date'] as String)
          : null,
      appliedDate: json['applied_date'] != null
          ? DateTime.parse(json['applied_date'] as String)
          : null,
      createdBy: json['created_by'] as String?,
      createdByName: json['created_by_name'] as String?,
      approvedBy: json['approved_by'] as String?,
      approvedByName: json['approved_by_name'] as String?,
      approvedAt: json['approved_at'] != null
          ? DateTime.parse(json['approved_at'] as String)
          : null,
      notes: json['notes'] as String?,
      notesAr: json['notes_ar'] as String?,
      parameters: json['parameters'] as Map<String, dynamic>?,
      metadata: json['metadata'] as Map<String, dynamic>?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'prescription_id': prescriptionId,
        'tenant_id': tenantId,
        'field_id': fieldId,
        'field_name': fieldName,
        'field_name_ar': fieldNameAr,
        'name': name,
        'name_ar': nameAr,
        'vra_type': vraType.value,
        'status': status.value,
        'zoning_method': zoningMethod.value,
        'zones_count': zonesCount,
        'total_area': totalArea,
        'zones': zones.map((e) => e.toJson()).toList(),
        'rates': rates.map((e) => e.toJson()).toList(),
        'scheduled_date': scheduledDate?.toIso8601String(),
        'applied_date': appliedDate?.toIso8601String(),
        'created_by': createdBy,
        'created_by_name': createdByName,
        'approved_by': approvedBy,
        'approved_by_name': approvedByName,
        'approved_at': approvedAt?.toIso8601String(),
        'notes': notes,
        'notes_ar': notesAr,
        'parameters': parameters,
        'metadata': metadata,
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
      };

  VRAPrescription copyWith({
    String? prescriptionId,
    String? tenantId,
    String? fieldId,
    String? fieldName,
    String? fieldNameAr,
    String? name,
    String? nameAr,
    VRAType? vraType,
    PrescriptionStatus? status,
    ZoningMethod? zoningMethod,
    int? zonesCount,
    double? totalArea,
    List<ManagementZone>? zones,
    List<ApplicationRate>? rates,
    DateTime? scheduledDate,
    DateTime? appliedDate,
    String? createdBy,
    String? createdByName,
    String? approvedBy,
    String? approvedByName,
    DateTime? approvedAt,
    String? notes,
    String? notesAr,
    Map<String, dynamic>? parameters,
    Map<String, dynamic>? metadata,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return VRAPrescription(
      prescriptionId: prescriptionId ?? this.prescriptionId,
      tenantId: tenantId ?? this.tenantId,
      fieldId: fieldId ?? this.fieldId,
      fieldName: fieldName ?? this.fieldName,
      fieldNameAr: fieldNameAr ?? this.fieldNameAr,
      name: name ?? this.name,
      nameAr: nameAr ?? this.nameAr,
      vraType: vraType ?? this.vraType,
      status: status ?? this.status,
      zoningMethod: zoningMethod ?? this.zoningMethod,
      zonesCount: zonesCount ?? this.zonesCount,
      totalArea: totalArea ?? this.totalArea,
      zones: zones ?? this.zones,
      rates: rates ?? this.rates,
      scheduledDate: scheduledDate ?? this.scheduledDate,
      appliedDate: appliedDate ?? this.appliedDate,
      createdBy: createdBy ?? this.createdBy,
      createdByName: createdByName ?? this.createdByName,
      approvedBy: approvedBy ?? this.approvedBy,
      approvedByName: approvedByName ?? this.approvedByName,
      approvedAt: approvedAt ?? this.approvedAt,
      notes: notes ?? this.notes,
      notesAr: notesAr ?? this.notesAr,
      parameters: parameters ?? this.parameters,
      metadata: metadata ?? this.metadata,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

/// إحصائيات VRA
@immutable
class VRAStats {
  final int totalPrescriptions;
  final int draftPrescriptions;
  final int approvedPrescriptions;
  final int appliedPrescriptions;
  final double totalAreaCovered;
  final double totalCost;
  final Map<String, int> byType;

  const VRAStats({
    required this.totalPrescriptions,
    required this.draftPrescriptions,
    required this.approvedPrescriptions,
    required this.appliedPrescriptions,
    required this.totalAreaCovered,
    required this.totalCost,
    required this.byType,
  });

  factory VRAStats.fromJson(Map<String, dynamic> json) {
    return VRAStats(
      totalPrescriptions: json['total_prescriptions'] as int,
      draftPrescriptions: json['draft_prescriptions'] as int,
      approvedPrescriptions: json['approved_prescriptions'] as int,
      appliedPrescriptions: json['applied_prescriptions'] as int,
      totalAreaCovered: (json['total_area_covered'] as num).toDouble(),
      totalCost: (json['total_cost'] as num).toDouble(),
      byType: Map<String, int>.from(json['by_type'] as Map),
    );
  }
}
