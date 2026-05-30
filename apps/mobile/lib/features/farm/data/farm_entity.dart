/// Farm entity representing a farm in the SAHOOL platform
class FarmEntity {
  final String id;
  final String name;
  final String? nameAr;
  final String location;
  final String? locationAr;
  final double totalAreaHa;
  final String waterSource;
  final double centerLat;
  final double centerLng;
  final List<List<double>>? polygonCoords; // [[lng,lat],...]
  final String? status;
  final DateTime? createdAt;

  const FarmEntity({
    required this.id,
    required this.name,
    this.nameAr,
    required this.location,
    this.locationAr,
    required this.totalAreaHa,
    required this.waterSource,
    required this.centerLat,
    required this.centerLng,
    this.polygonCoords,
    this.status,
    this.createdAt,
  });

  factory FarmEntity.fromJson(Map<String, dynamic> json) {
    List<List<double>>? coords;
    final rawCoords = json['polygon_coords'];
    if (rawCoords is List) {
      coords = rawCoords
          .map((item) => (item as List).map((v) => (v as num).toDouble()).toList())
          .toList();
    }

    return FarmEntity(
      id: json['id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      nameAr: json['name_ar'] as String?,
      location: json['location'] as String? ?? '',
      locationAr: json['location_ar'] as String?,
      totalAreaHa: (json['total_area_ha'] as num?)?.toDouble() ?? 0.0,
      waterSource: json['water_source'] as String? ?? '',
      centerLat: (json['center_lat'] as num?)?.toDouble() ?? 0.0,
      centerLng: (json['center_lng'] as num?)?.toDouble() ?? 0.0,
      polygonCoords: coords,
      status: json['status'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      if (nameAr != null) 'name_ar': nameAr,
      'location': location,
      if (locationAr != null) 'location_ar': locationAr,
      'total_area_ha': totalAreaHa,
      'water_source': waterSource,
      'center_lat': centerLat,
      'center_lng': centerLng,
      if (polygonCoords != null) 'polygon_coords': polygonCoords,
      if (status != null) 'status': status,
      if (createdAt != null) 'created_at': createdAt!.toIso8601String(),
    };
  }
}
