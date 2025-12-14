/// Field Domain Entity
/// كيان الحقل - Domain Layer نظيف (بدون Flutter)
///
/// يمثل الحقل الزراعي مع جميع خصائصه

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

/// كيان الحقل الزراعي
class Field {
  /// معرف فريد
  final String id;

  /// اسم الحقل
  final String name;

  /// نوع المحصول
  final String cropType;

  /// المساحة بالهكتار
  final double areaHa;

  /// قيمة NDVI (0.0 - 1.0)
  final double ndvi;

  /// حالة الحقل
  final FieldStatus status;

  /// إحداثيات المركز (latitude, longitude)
  final double? centerLat;
  final double? centerLng;

  /// عدد المهام المعلقة
  final int pendingTasks;

  /// آخر تحديث للبيانات
  final DateTime? lastUpdate;

  /// ملاحظات إضافية
  final String? notes;

  const Field({
    required this.id,
    required this.name,
    required this.cropType,
    required this.areaHa,
    required this.ndvi,
    required this.status,
    this.centerLat,
    this.centerLng,
    this.pendingTasks = 0,
    this.lastUpdate,
    this.notes,
  });

  /// هل الحقل يحتاج انتباه عاجل؟
  bool get needsAttention =>
      status == FieldStatus.critical || status == FieldStatus.stressed;

  /// هل الحقل في حالة حرجة؟
  bool get isCritical => status == FieldStatus.critical;

  /// تقييم الصحة كنسبة مئوية
  int get healthPercentage => (ndvi * 100).round();

  /// حساب الحالة من قيمة NDVI
  static FieldStatus statusFromNdvi(double ndvi) {
    if (ndvi >= 0.6) return FieldStatus.healthy;
    if (ndvi >= 0.4) return FieldStatus.stressed;
    if (ndvi > 0) return FieldStatus.critical;
    return FieldStatus.unknown;
  }

  /// إنشاء حقل من JSON
  factory Field.fromJson(Map<String, dynamic> json) {
    final ndvi = (json['ndvi'] as num?)?.toDouble() ?? 0.0;
    return Field(
      id: json['id'] as String,
      name: json['name'] as String,
      cropType: json['crop_type'] as String? ?? 'غير محدد',
      areaHa: (json['area_ha'] as num?)?.toDouble() ?? 0.0,
      ndvi: ndvi,
      status: FieldStatus.values.firstWhere(
        (s) => s.name == json['status'],
        orElse: () => statusFromNdvi(ndvi),
      ),
      centerLat: (json['center_lat'] as num?)?.toDouble(),
      centerLng: (json['center_lng'] as num?)?.toDouble(),
      pendingTasks: json['pending_tasks'] as int? ?? 0,
      lastUpdate: json['last_update'] != null
          ? DateTime.parse(json['last_update'] as String)
          : null,
      notes: json['notes'] as String?,
    );
  }

  /// تحويل إلى JSON
  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'crop_type': cropType,
        'area_ha': areaHa,
        'ndvi': ndvi,
        'status': status.name,
        'center_lat': centerLat,
        'center_lng': centerLng,
        'pending_tasks': pendingTasks,
        'last_update': lastUpdate?.toIso8601String(),
        'notes': notes,
      };

  /// نسخة معدلة
  Field copyWith({
    String? id,
    String? name,
    String? cropType,
    double? areaHa,
    double? ndvi,
    FieldStatus? status,
    double? centerLat,
    double? centerLng,
    int? pendingTasks,
    DateTime? lastUpdate,
    String? notes,
  }) {
    return Field(
      id: id ?? this.id,
      name: name ?? this.name,
      cropType: cropType ?? this.cropType,
      areaHa: areaHa ?? this.areaHa,
      ndvi: ndvi ?? this.ndvi,
      status: status ?? this.status,
      centerLat: centerLat ?? this.centerLat,
      centerLng: centerLng ?? this.centerLng,
      pendingTasks: pendingTasks ?? this.pendingTasks,
      lastUpdate: lastUpdate ?? this.lastUpdate,
      notes: notes ?? this.notes,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Field && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() => 'Field($id: $name, NDVI: $ndvi, Status: ${status.name})';
}
