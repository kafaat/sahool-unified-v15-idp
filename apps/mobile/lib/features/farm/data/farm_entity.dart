/// Farm entity representing a farm in the SAHOOL platform.
/// Reads camelCase keys from backend (field-management-service).
class FarmEntity {
  final String id;
  final String name;
  final String? nameAr;
  final String? region;
  final String? regionAr;
  final String? owner;
  final String? ownerId;
  final String? waterSource;
  final String? waterSourceAr;
  final String? status; // 'active' | 'inactive' | 'archived'
  final double totalAreaHa;
  final double? cultivatedAreaHa;
  final String? location;
  final String? locationAr;
  final double centerLat;
  final double centerLng;
  final int? zoom;
  final List<double>? bbox; // [minLng, minLat, maxLng, maxLat]
  final int? fieldsCount;
  final int? cropCount;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  const FarmEntity({
    required this.id,
    required this.name,
    this.nameAr,
    this.region,
    this.regionAr,
    this.owner,
    this.ownerId,
    this.waterSource,
    this.waterSourceAr,
    this.status,
    required this.totalAreaHa,
    this.cultivatedAreaHa,
    this.location,
    this.locationAr,
    required this.centerLat,
    required this.centerLng,
    this.zoom,
    this.bbox,
    this.fieldsCount,
    this.cropCount,
    this.createdAt,
    this.updatedAt,
  });

  factory FarmEntity.fromJson(Map<String, dynamic> json) {
    // Parse bbox from a JSON list of numbers
    List<double>? bbox;
    final rawBbox = json['bbox'];
    if (rawBbox is List && rawBbox.isNotEmpty) {
      bbox = rawBbox.map((v) => (v as num).toDouble()).toList();
    }

    return FarmEntity(
      id: json['id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      nameAr: json['nameAr'] as String?,
      region: json['region'] as String?,
      regionAr: json['regionAr'] as String?,
      owner: json['owner'] as String?,
      ownerId: json['ownerId'] as String?,
      waterSource: json['waterSource'] as String?,
      waterSourceAr: json['waterSourceAr'] as String?,
      status: json['status'] as String?,
      totalAreaHa: ((json['totalAreaHa'] ?? json['totalAreaHectares']) as num?)
              ?.toDouble() ??
          0.0,
      cultivatedAreaHa:
          ((json['cultivatedAreaHa'] ?? json['cultivatedAreaHectares']) as num?)
              ?.toDouble(),
      location: (json['location'] ?? json['locationLabel']) as String?,
      locationAr: (json['locationAr'] ?? json['locationLabelAr']) as String?,
      centerLat: (json['centerLat'] as num?)?.toDouble() ?? 0.0,
      centerLng: (json['centerLng'] as num?)?.toDouble() ?? 0.0,
      zoom: (json['zoom'] as num?)?.toInt(),
      bbox: bbox,
      fieldsCount: (json['fieldsCount'] as num?)?.toInt(),
      cropCount: (json['cropCount'] as num?)?.toInt(),
      createdAt: json['createdAt'] != null
          ? DateTime.tryParse(json['createdAt'] as String)
          : null,
      updatedAt: json['updatedAt'] != null
          ? DateTime.tryParse(json['updatedAt'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      if (nameAr != null) 'nameAr': nameAr,
      if (region != null) 'region': region,
      if (regionAr != null) 'regionAr': regionAr,
      if (owner != null) 'owner': owner,
      if (ownerId != null) 'ownerId': ownerId,
      if (waterSource != null) 'waterSource': waterSource,
      if (waterSourceAr != null) 'waterSourceAr': waterSourceAr,
      if (status != null) 'status': status,
      'totalAreaHa': totalAreaHa,
      if (cultivatedAreaHa != null) 'cultivatedAreaHa': cultivatedAreaHa,
      if (location != null) 'location': location,
      if (locationAr != null) 'locationAr': locationAr,
      'centerLat': centerLat,
      'centerLng': centerLng,
      if (zoom != null) 'zoom': zoom,
      if (bbox != null) 'bbox': bbox,
      if (fieldsCount != null) 'fieldsCount': fieldsCount,
      if (cropCount != null) 'cropCount': cropCount,
      if (createdAt != null) 'createdAt': createdAt!.toIso8601String(),
      if (updatedAt != null) 'updatedAt': updatedAt!.toIso8601String(),
    };
  }
}
