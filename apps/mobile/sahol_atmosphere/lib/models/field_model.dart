// ═══════════════════════════════════════════════════════════════════════════════════════
// SAHOOL ATMOSPHERE - Field Model
// نموذج الحقل الزراعي
// ═══════════════════════════════════════════════════════════════════════════════════════

import 'package:latlong2/latlong.dart';

/// Field health status based on NDVI
/// حالة صحة الحقل بناءً على NDVI
enum FieldHealthStatus {
  /// Healthy - NDVI > 0.6
  /// صحي
  healthy,

  /// Stressed - NDVI 0.4-0.6
  /// متوتر
  stressed,

  /// Critical - NDVI < 0.4
  /// حرج
  critical,

  /// Unknown - No data
  /// غير معروف
  unknown,
}

/// Field crop type
/// نوع المحصول
enum CropType {
  wheat('قمح', 'Wheat', '🌾'),
  tomato('طماطم', 'Tomato', '🍅'),
  palm('نخيل', 'Palm', '🌴'),
  lettuce('خس', 'Lettuce', '🥬'),
  corn('ذرة', 'Corn', '🌽'),
  barley('شعير', 'Barley', '🌾'),
  cotton('قطن', 'Cotton', '☁️'),
  coffee('بن', 'Coffee', '☕'),
  grapes('عنب', 'Grapes', '🍇'),
  other('أخرى', 'Other', '🌱');

  final String nameAr;
  final String nameEn;
  final String emoji;

  const CropType(this.nameAr, this.nameEn, this.emoji);
}

/// Simplified Field model for Atmosphere app
/// نموذج الحقل المبسط لتطبيق أتموسفير
class FieldModel {
  /// Unique identifier
  /// المعرف الفريد
  final String id;

  /// Field name in Arabic
  /// اسم الحقل بالعربية
  final String nameAr;

  /// Field name in English
  /// اسم الحقل بالإنجليزية
  final String nameEn;

  /// Crop type
  /// نوع المحصول
  final CropType cropType;

  /// Area in hectares
  /// المساحة بالهكتار
  final double areaHectares;

  /// Current NDVI value (0.0 - 1.0)
  /// قيمة NDVI الحالية
  final double ndviValue;

  /// Current soil moisture percentage
  /// نسبة رطوبة التربة
  final int moisturePercent;

  /// Current temperature in Celsius
  /// درجة الحرارة بالسيلسيوس
  final int temperatureCelsius;

  /// Current sunlight percentage
  /// نسبة الإضاءة
  final int sunlightPercent;

  /// Field boundary coordinates
  /// إحداثيات حدود الحقل
  final List<LatLng> boundary;

  /// Field center point
  /// مركز الحقل
  final LatLng? center;

  /// Last updated timestamp
  /// آخر تحديث
  final DateTime lastUpdated;

  /// Has pending alerts
  /// يوجد تنبيهات معلقة
  final bool hasAlerts;

  /// Number of pending tasks
  /// عدد المهام المعلقة
  final int pendingTasks;

  const FieldModel({
    required this.id,
    required this.nameAr,
    required this.nameEn,
    required this.cropType,
    required this.areaHectares,
    required this.ndviValue,
    required this.moisturePercent,
    required this.temperatureCelsius,
    required this.sunlightPercent,
    this.boundary = const [],
    this.center,
    required this.lastUpdated,
    this.hasAlerts = false,
    this.pendingTasks = 0,
  });

  /// Get health status based on NDVI
  /// الحصول على حالة الصحة بناءً على NDVI
  FieldHealthStatus get healthStatus {
    if (ndviValue >= 0.6) return FieldHealthStatus.healthy;
    if (ndviValue >= 0.4) return FieldHealthStatus.stressed;
    if (ndviValue > 0) return FieldHealthStatus.critical;
    return FieldHealthStatus.unknown;
  }

  /// Check if field needs attention
  /// التحقق إذا كان الحقل يحتاج اهتمام
  bool get needsAttention =>
      healthStatus == FieldHealthStatus.critical ||
      healthStatus == FieldHealthStatus.stressed ||
      hasAlerts;

  /// Health as percentage
  /// الصحة كنسبة مئوية
  int get healthPercent => (ndviValue * 100).round();

  /// Area formatted string
  /// المساحة منسقة
  String get areaFormatted => '${areaHectares.toStringAsFixed(1)} هكتار';

  /// Create from JSON
  factory FieldModel.fromJson(Map<String, dynamic> json) {
    final cropTypeStr = json['crop_type'] as String? ?? 'other';
    final cropType = CropType.values.firstWhere(
      (c) => c.name == cropTypeStr,
      orElse: () => CropType.other,
    );

    List<LatLng> boundary = [];
    if (json['boundary'] != null) {
      final coords = json['boundary'] as List;
      boundary = coords.map((c) {
        final coord = c as List;
        return LatLng(
          (coord[1] as num).toDouble(),
          (coord[0] as num).toDouble(),
        );
      }).toList();
    }

    LatLng? center;
    if (json['center'] != null) {
      final c = json['center'] as List;
      center = LatLng(
        (c[1] as num).toDouble(),
        (c[0] as num).toDouble(),
      );
    }

    return FieldModel(
      id: json['id'] as String,
      nameAr: json['name_ar'] as String? ?? json['name'] as String? ?? 'غير محدد',
      nameEn: json['name_en'] as String? ?? json['name'] as String? ?? 'Unnamed',
      cropType: cropType,
      areaHectares: (json['area_hectares'] as num?)?.toDouble() ?? 0.0,
      ndviValue: (json['ndvi'] as num?)?.toDouble() ?? 0.0,
      moisturePercent: (json['moisture'] as num?)?.toInt() ?? 0,
      temperatureCelsius: (json['temperature'] as num?)?.toInt() ?? 0,
      sunlightPercent: (json['sunlight'] as num?)?.toInt() ?? 0,
      boundary: boundary,
      center: center,
      lastUpdated: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : DateTime.now(),
      hasAlerts: json['has_alerts'] as bool? ?? false,
      pendingTasks: json['pending_tasks'] as int? ?? 0,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() => {
        'id': id,
        'name_ar': nameAr,
        'name_en': nameEn,
        'crop_type': cropType.name,
        'area_hectares': areaHectares,
        'ndvi': ndviValue,
        'moisture': moisturePercent,
        'temperature': temperatureCelsius,
        'sunlight': sunlightPercent,
        'boundary': boundary.map((p) => [p.longitude, p.latitude]).toList(),
        'center': center != null ? [center!.longitude, center!.latitude] : null,
        'updated_at': lastUpdated.toIso8601String(),
        'has_alerts': hasAlerts,
        'pending_tasks': pendingTasks,
      };

  /// Copy with modifications
  FieldModel copyWith({
    String? id,
    String? nameAr,
    String? nameEn,
    CropType? cropType,
    double? areaHectares,
    double? ndviValue,
    int? moisturePercent,
    int? temperatureCelsius,
    int? sunlightPercent,
    List<LatLng>? boundary,
    LatLng? center,
    DateTime? lastUpdated,
    bool? hasAlerts,
    int? pendingTasks,
  }) {
    return FieldModel(
      id: id ?? this.id,
      nameAr: nameAr ?? this.nameAr,
      nameEn: nameEn ?? this.nameEn,
      cropType: cropType ?? this.cropType,
      areaHectares: areaHectares ?? this.areaHectares,
      ndviValue: ndviValue ?? this.ndviValue,
      moisturePercent: moisturePercent ?? this.moisturePercent,
      temperatureCelsius: temperatureCelsius ?? this.temperatureCelsius,
      sunlightPercent: sunlightPercent ?? this.sunlightPercent,
      boundary: boundary ?? this.boundary,
      center: center ?? this.center,
      lastUpdated: lastUpdated ?? this.lastUpdated,
      hasAlerts: hasAlerts ?? this.hasAlerts,
      pendingTasks: pendingTasks ?? this.pendingTasks,
    );
  }

  @override
  String toString() =>
      'FieldModel($id: $nameAr, ${areaHectares}ha, NDVI: $ndviValue)';
}

/// Sample fields for demo
/// حقول تجريبية للعرض
class SampleFields {
  static List<FieldModel> get all => [
        FieldModel(
          id: 'field_001',
          nameAr: 'حقل رقم 04 - قمح',
          nameEn: 'Field #04 - Wheat',
          cropType: CropType.wheat,
          areaHectares: 12.5,
          ndviValue: 0.72,
          moisturePercent: 64,
          temperatureCelsius: 28,
          sunlightPercent: 85,
          boundary: [
            const LatLng(15.3694, 44.1910),
            const LatLng(15.3700, 44.1920),
            const LatLng(15.3695, 44.1930),
            const LatLng(15.3685, 44.1925),
            const LatLng(15.3694, 44.1910),
          ],
          center: const LatLng(15.3693, 44.1920),
          lastUpdated: DateTime.now(),
          pendingTasks: 2,
        ),
        FieldModel(
          id: 'field_002',
          nameAr: 'حقل رقم 07 - طماطم',
          nameEn: 'Field #07 - Tomato',
          cropType: CropType.tomato,
          areaHectares: 5.2,
          ndviValue: 0.48,
          moisturePercent: 38,
          temperatureCelsius: 34,
          sunlightPercent: 92,
          boundary: [
            const LatLng(15.3710, 44.1940),
            const LatLng(15.3720, 44.1950),
            const LatLng(15.3715, 44.1960),
            const LatLng(15.3705, 44.1955),
            const LatLng(15.3710, 44.1940),
          ],
          center: const LatLng(15.3712, 44.1950),
          lastUpdated: DateTime.now().subtract(const Duration(hours: 2)),
          hasAlerts: true,
          pendingTasks: 5,
        ),
        FieldModel(
          id: 'field_003',
          nameAr: 'حقل رقم 12 - نخيل',
          nameEn: 'Field #12 - Palm',
          cropType: CropType.palm,
          areaHectares: 25.0,
          ndviValue: 0.68,
          moisturePercent: 72,
          temperatureCelsius: 29,
          sunlightPercent: 78,
          boundary: [
            const LatLng(15.3650, 44.1870),
            const LatLng(15.3670, 44.1890),
            const LatLng(15.3660, 44.1910),
            const LatLng(15.3640, 44.1890),
            const LatLng(15.3650, 44.1870),
          ],
          center: const LatLng(15.3655, 44.1890),
          lastUpdated: DateTime.now().subtract(const Duration(minutes: 30)),
          pendingTasks: 1,
        ),
        FieldModel(
          id: 'field_004',
          nameAr: 'حقل رقم 15 - خس',
          nameEn: 'Field #15 - Lettuce',
          cropType: CropType.lettuce,
          areaHectares: 3.8,
          ndviValue: 0.32,
          moisturePercent: 25,
          temperatureCelsius: 36,
          sunlightPercent: 95,
          boundary: [
            const LatLng(15.3730, 44.1880),
            const LatLng(15.3740, 44.1890),
            const LatLng(15.3735, 44.1900),
            const LatLng(15.3725, 44.1895),
            const LatLng(15.3730, 44.1880),
          ],
          center: const LatLng(15.3732, 44.1890),
          lastUpdated: DateTime.now().subtract(const Duration(hours: 1)),
          hasAlerts: true,
          pendingTasks: 8,
        ),
        FieldModel(
          id: 'field_005',
          nameAr: 'حقل رقم 20 - بن',
          nameEn: 'Field #20 - Coffee',
          cropType: CropType.coffee,
          areaHectares: 8.0,
          ndviValue: 0.65,
          moisturePercent: 55,
          temperatureCelsius: 26,
          sunlightPercent: 60,
          boundary: [
            const LatLng(15.3600, 44.1920),
            const LatLng(15.3620, 44.1940),
            const LatLng(15.3610, 44.1960),
            const LatLng(15.3590, 44.1940),
            const LatLng(15.3600, 44.1920),
          ],
          center: const LatLng(15.3605, 44.1940),
          lastUpdated: DateTime.now().subtract(const Duration(hours: 4)),
          pendingTasks: 0,
        ),
      ];

  /// Get total area
  static double get totalArea =>
      all.fold(0.0, (sum, field) => sum + field.areaHectares);

  /// Get average health
  static double get averageHealth =>
      all.fold(0.0, (sum, field) => sum + field.ndviValue) / all.length;

  /// Get fields needing attention
  static List<FieldModel> get needingAttention =>
      all.where((f) => f.needsAttention).toList();
}
