import 'package:latlong2/latlong.dart';

/// Field Domain Entity
/// كيان الحقل - Domain Layer نظيف (بدون Flutter)
///
/// يمثل الحقل الزراعي مع جميع خصائصه GIS

/// حالة صحة الحقل
enum FieldStatus {
  /// صحي - NDVI > 0.6
  healthy,

  /// إجهاد - NDVI 0.4-0.6
  stressed,

  /// حرج - NDVI < 0.4
  critical,

  /// غير معروف - لا توجد بيانات
  unknown,
}

/// كيان الحقل الزراعي (GIS-enabled)
class Field {
  /// معرف فريد محلي
  final String id;

  /// معرف السيرفر (PostGIS)
  final String? remoteId;

  /// معرف المستأجر
  final String tenantId;

  /// معرف المزرعة
  final String? farmId;

  /// اسم الحقل
  final String name;

  /// نوع المحصول
  final String? cropType;

  /// حدود الحقل (GIS Polygon)
  final List<LatLng> boundary;

  /// مركز الحقل (GIS Point)
  final LatLng? centroid;

  /// المساحة بالهكتار (محسوبة من الحدود)
  final double areaHectares;

  /// حالة الحقل (active, fallow, etc.)
  final String? status;

  /// قيمة NDVI الحالية (0.0 - 1.0)
  final double? ndviCurrent;

  /// تاريخ تحديث NDVI
  final DateTime? ndviUpdatedAt;

  /// هل تم المزامنة مع السيرفر؟
  final bool synced;

  /// هل تم حذفه (Soft Delete)؟
  final bool isDeleted;

  /// تاريخ الإنشاء
  final DateTime createdAt;

  /// تاريخ التحديث
  final DateTime updatedAt;

  /// عدد المهام المعلقة (UI convenience)
  final int pendingTasks;

  const Field({
    required this.id,
    this.remoteId,
    required this.tenantId,
    this.farmId,
    required this.name,
    this.cropType,
    this.boundary = const [],
    this.centroid,
    this.areaHectares = 0,
    this.status,
    this.ndviCurrent,
    this.ndviUpdatedAt,
    this.synced = false,
    this.isDeleted = false,
    required this.createdAt,
    required this.updatedAt,
    this.pendingTasks = 0,
  });

  // ============================================================
  // Computed Properties (UI Convenience)
  // ============================================================

  /// قيمة NDVI للعرض
  double get ndvi => ndviCurrent ?? 0.0;

  /// المساحة (للتوافق مع الكود القديم)
  double get areaHa => areaHectares;

  /// إحداثيات المركز (للتوافق مع الكود القديم)
  double? get centerLat => centroid?.latitude;
  double? get centerLng => centroid?.longitude;

  /// حالة الصحة المحسوبة من NDVI
  FieldStatus get healthStatus => statusFromNdvi(ndvi);

  /// هل الحقل يحتاج انتباه عاجل؟
  bool get needsAttention =>
      healthStatus == FieldStatus.critical || healthStatus == FieldStatus.stressed;

  /// هل الحقل في حالة حرجة؟
  bool get isCritical => healthStatus == FieldStatus.critical;

  /// تقييم الصحة كنسبة مئوية
  int get healthPercentage => (ndvi * 100).round();

  /// هل الحدود معرفة؟
  bool get hasBoundary => boundary.isNotEmpty;

  /// عدد نقاط الحدود
  int get boundaryPointCount => boundary.length;

  /// حساب الحالة من قيمة NDVI
  static FieldStatus statusFromNdvi(double ndvi) {
    if (ndvi >= 0.6) return FieldStatus.healthy;
    if (ndvi >= 0.4) return FieldStatus.stressed;
    if (ndvi > 0) return FieldStatus.critical;
    return FieldStatus.unknown;
  }

  /// إنشاء حقل من JSON (GeoJSON Feature)
  factory Field.fromJson(Map<String, dynamic> json) {
    // Parse GeoJSON geometry if present
    List<LatLng> boundary = [];
    LatLng? centroid;

    final geometry = json['geometry'];
    if (geometry != null && geometry['type'] == 'Polygon') {
      final coords = (geometry['coordinates'] as List?)?.first as List?;
      if (coords != null) {
        boundary = coords.map((c) {
          final coord = c as List;
          return LatLng(
            (coord[1] as num).toDouble(),
            (coord[0] as num).toDouble(),
          );
        }).toList();

        // Calculate centroid
        if (boundary.isNotEmpty) {
          double sumLat = 0, sumLng = 0;
          for (final p in boundary) {
            sumLat += p.latitude;
            sumLng += p.longitude;
          }
          centroid = LatLng(sumLat / boundary.length, sumLng / boundary.length);
        }
      }
    }

    final props = json['properties'] as Map<String, dynamic>? ?? json;
    final now = DateTime.now();

    return Field(
      id: json['id']?.toString() ?? props['id']?.toString() ?? '',
      remoteId: json['remote_id']?.toString(),
      tenantId: props['tenant_id']?.toString() ?? '',
      farmId: props['farm_id']?.toString(),
      name: props['name'] as String? ?? 'غير محدد',
      cropType: props['crop_type'] as String?,
      boundary: boundary,
      centroid: centroid,
      areaHectares: (props['area_hectares'] as num?)?.toDouble() ?? 0.0,
      status: props['status'] as String?,
      ndviCurrent: (props['ndvi_current'] as num?)?.toDouble(),
      ndviUpdatedAt: props['ndvi_updated_at'] != null
          ? DateTime.parse(props['ndvi_updated_at'] as String)
          : null,
      synced: props['synced'] as bool? ?? true,
      isDeleted: props['is_deleted'] as bool? ?? false,
      createdAt: props['created_at'] != null
          ? DateTime.parse(props['created_at'] as String)
          : now,
      updatedAt: props['updated_at'] != null
          ? DateTime.parse(props['updated_at'] as String)
          : now,
      pendingTasks: props['pending_tasks'] as int? ?? 0,
    );
  }

  /// تحويل إلى JSON (GeoJSON Feature)
  Map<String, dynamic> toJson() => {
        'type': 'Feature',
        'id': id,
        'geometry': hasBoundary
            ? {
                'type': 'Polygon',
                'coordinates': [
                  boundary.map((p) => [p.longitude, p.latitude]).toList(),
                ],
              }
            : null,
        'properties': {
          'id': id,
          'remote_id': remoteId,
          'tenant_id': tenantId,
          'farm_id': farmId,
          'name': name,
          'crop_type': cropType,
          'area_hectares': areaHectares,
          'status': status,
          'ndvi_current': ndviCurrent,
          'ndvi_updated_at': ndviUpdatedAt?.toIso8601String(),
          'synced': synced,
          'is_deleted': isDeleted,
          'created_at': createdAt.toIso8601String(),
          'updated_at': updatedAt.toIso8601String(),
          'pending_tasks': pendingTasks,
        },
      };

  /// نسخة معدلة
  Field copyWith({
    String? id,
    String? remoteId,
    String? tenantId,
    String? farmId,
    String? name,
    String? cropType,
    List<LatLng>? boundary,
    LatLng? centroid,
    double? areaHectares,
    String? status,
    double? ndviCurrent,
    DateTime? ndviUpdatedAt,
    bool? synced,
    bool? isDeleted,
    DateTime? createdAt,
    DateTime? updatedAt,
    int? pendingTasks,
  }) {
    return Field(
      id: id ?? this.id,
      remoteId: remoteId ?? this.remoteId,
      tenantId: tenantId ?? this.tenantId,
      farmId: farmId ?? this.farmId,
      name: name ?? this.name,
      cropType: cropType ?? this.cropType,
      boundary: boundary ?? this.boundary,
      centroid: centroid ?? this.centroid,
      areaHectares: areaHectares ?? this.areaHectares,
      status: status ?? this.status,
      ndviCurrent: ndviCurrent ?? this.ndviCurrent,
      ndviUpdatedAt: ndviUpdatedAt ?? this.ndviUpdatedAt,
      synced: synced ?? this.synced,
      isDeleted: isDeleted ?? this.isDeleted,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      pendingTasks: pendingTasks ?? this.pendingTasks,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Field && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() =>
      'Field($id: $name, Area: ${areaHectares.toStringAsFixed(2)}ha, NDVI: ${ndvi.toStringAsFixed(2)})';
}
