import 'package:latlong2/latlong.dart';
import '../../../field/domain/entities/field.dart' as field_domain;

/// Field Entity - كيان الحقل
class FieldEntity {
  final String id;
  final String tenantId;
  final String name;
  final String? farmId;
  final String? farmName;
  final double areaHectares;
  final String cropType;
  final double healthScore;
  final double? ndviValue;
  final double? ndwiValue;
  final String? soilType;
  final String? irrigationType;
  final DateTime? lastIrrigation;
  final DateTime? plantingDate;
  final DateTime? expectedHarvest;
  final FieldStatus status;
  final GeoLocation? center;
  final List<GeoLocation>? boundary;
  final DateTime createdAt;
  final DateTime updatedAt;

  const FieldEntity({
    required this.id,
    required this.tenantId,
    required this.name,
    this.farmId,
    this.farmName,
    required this.areaHectares,
    required this.cropType,
    this.healthScore = 0.0,
    this.ndviValue,
    this.ndwiValue,
    this.soilType,
    this.irrigationType,
    this.lastIrrigation,
    this.plantingDate,
    this.expectedHarvest,
    this.status = FieldStatus.active,
    this.center,
    this.boundary,
    required this.createdAt,
    required this.updatedAt,
  });

  /// Create a FieldEntity from the GIS-enabled Field domain model.
  /// يتيح تحويل كيان الحقل من نموذج Field الأساسي (GIS)
  factory FieldEntity.fromField(field_domain.Field field) {
    return FieldEntity(
      id: field.id,
      tenantId: field.tenantId,
      name: field.name,
      farmId: field.farmId,
      areaHectares: field.areaHectares,
      cropType: field.cropType ?? '',
      healthScore: field.ndvi,
      ndviValue: field.ndviCurrent,
      status: FieldStatus.fromString(field.status ?? 'active'),
      center: field.centroid != null
          ? GeoLocation(
              latitude: field.centroid!.latitude,
              longitude: field.centroid!.longitude,
            )
          : null,
      boundary: field.boundary.isNotEmpty
          ? field.boundary
              .map((p) => GeoLocation(
                    latitude: p.latitude,
                    longitude: p.longitude,
                  ))
              .toList()
          : null,
      createdAt: field.createdAt,
      updatedAt: field.updatedAt,
    );
  }

  factory FieldEntity.fromJson(Map<String, dynamic> json) {
    return FieldEntity(
      id: json['id'] as String,
      tenantId: json['tenant_id'] as String,
      name: json['name'] as String,
      farmId: json['farm_id'] as String?,
      farmName: json['farm_name'] as String?,
      areaHectares: (json['area_hectares'] as num).toDouble(),
      cropType: json['crop_type'] as String,
      healthScore: (json['health_score'] as num?)?.toDouble() ?? 0.0,
      ndviValue: (json['ndvi_value'] as num?)?.toDouble(),
      ndwiValue: (json['ndwi_value'] as num?)?.toDouble(),
      soilType: json['soil_type'] as String?,
      irrigationType: json['irrigation_type'] as String?,
      lastIrrigation: json['last_irrigation'] != null
          ? DateTime.parse(json['last_irrigation'] as String)
          : null,
      plantingDate: json['planting_date'] != null
          ? DateTime.parse(json['planting_date'] as String)
          : null,
      expectedHarvest: json['expected_harvest'] != null
          ? DateTime.parse(json['expected_harvest'] as String)
          : null,
      status: FieldStatus.fromString(json['status'] as String? ?? 'active'),
      center: json['center'] != null
          ? GeoLocation.fromJson(json['center'] as Map<String, dynamic>)
          : null,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'tenant_id': tenantId,
      'name': name,
      'farm_id': farmId,
      'farm_name': farmName,
      'area_hectares': areaHectares,
      'crop_type': cropType,
      'health_score': healthScore,
      'ndvi_value': ndviValue,
      'ndwi_value': ndwiValue,
      'soil_type': soilType,
      'irrigation_type': irrigationType,
      'last_irrigation': lastIrrigation?.toIso8601String(),
      'planting_date': plantingDate?.toIso8601String(),
      'expected_harvest': expectedHarvest?.toIso8601String(),
      'status': status.value,
      'center': center?.toJson(),
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  /// Get health status label in Arabic
  String get healthLabel {
    if (healthScore >= 0.8) return 'ممتاز';
    if (healthScore >= 0.6) return 'جيد';
    if (healthScore >= 0.4) return 'متوسط';
    return 'ضعيف';
  }

  /// Get crop emoji
  String get cropEmoji {
    switch (cropType.toLowerCase()) {
      case 'قمح':
      case 'wheat':
        return '🌾';
      case 'شعير':
      case 'barley':
        return '🌾';
      case 'برسيم':
      case 'alfalfa':
        return '🌿';
      case 'ذرة':
      case 'corn':
        return '🌽';
      case 'نخيل':
      case 'palm':
        return '🌴';
      case 'بطاطس':
      case 'potato':
        return '🥔';
      case 'طماطم':
      case 'tomato':
        return '🍅';
      case 'خيار':
      case 'cucumber':
        return '🥒';
      case 'فلفل':
      case 'pepper':
        return '🌶️';
      case 'بصل':
      case 'onion':
        return '🧅';
      default:
        return '🌱';
    }
  }

  /// Days since planting
  int? get daysSincePlanting {
    if (plantingDate == null) return null;
    return DateTime.now().difference(plantingDate!).inDays;
  }

  /// Days until harvest
  int? get daysUntilHarvest {
    if (expectedHarvest == null) return null;
    return expectedHarvest!.difference(DateTime.now()).inDays;
  }
}

/// Field Status
enum FieldStatus {
  active('active', 'نشط'),
  fallow('fallow', 'بور'),
  preparing('preparing', 'تجهيز'),
  harvested('harvested', 'تم الحصاد'),
  inactive('inactive', 'غير نشط');

  final String value;
  final String arabicLabel;

  const FieldStatus(this.value, this.arabicLabel);

  static FieldStatus fromString(String value) {
    return FieldStatus.values.firstWhere(
      (s) => s.value == value,
      orElse: () => FieldStatus.active,
    );
  }
}

/// Geographic Location
class GeoLocation {
  final double latitude;
  final double longitude;

  const GeoLocation({
    required this.latitude,
    required this.longitude,
  });

  factory GeoLocation.fromJson(Map<String, dynamic> json) {
    return GeoLocation(
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'latitude': latitude,
      'longitude': longitude,
    };
  }
}
