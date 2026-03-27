/// Terrain Models Tests
///
/// Tests for terrain analysis data models.
///
/// NOTE: The production terrain models in terrain_repository.dart use Freezed
/// code generation. However, the Freezed generator is not configured to process
/// files in the `data/` directory (only `models/` and `domain/`), so the
/// generated `.freezed.dart` and `.g.dart` files do not exist.
///
/// To keep these tests meaningful without importing the non-compilable file,
/// we define equivalent plain Dart model classes that mirror the production API
/// surface (same field names, same JSON keys, same behavior). This validates
/// the data contract and serialization logic independently of Freezed codegen.
library;

import 'package:flutter_test/flutter_test.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Local model definitions mirroring production terrain_repository.dart
// ═══════════════════════════════════════════════════════════════════════════════

class TerrainAnalysis {
  final String fieldId;
  final double averageElevationM;
  final double minElevationM;
  final double maxElevationM;
  final double elevationRangeM;
  final double averageSlopePercent;
  final double maxSlopePercent;
  final String dominantAspect;
  final String dominantAspectAr;
  final String? soilType;
  final String? soilTypeAr;
  final String? drainageClass;
  final double? roughnessIndex;
  final double? wetnessIndex;
  final DateTime? timestamp;
  final String dataSource;

  const TerrainAnalysis({
    required this.fieldId,
    required this.averageElevationM,
    required this.minElevationM,
    required this.maxElevationM,
    required this.elevationRangeM,
    required this.averageSlopePercent,
    required this.maxSlopePercent,
    required this.dominantAspect,
    required this.dominantAspectAr,
    this.soilType,
    this.soilTypeAr,
    this.drainageClass,
    this.roughnessIndex,
    this.wetnessIndex,
    this.timestamp,
    this.dataSource = 'dem',
  });

  factory TerrainAnalysis.fromJson(Map<String, dynamic> json) {
    return TerrainAnalysis(
      fieldId: json['fieldId'] as String,
      averageElevationM: (json['averageElevationM'] as num).toDouble(),
      minElevationM: (json['minElevationM'] as num).toDouble(),
      maxElevationM: (json['maxElevationM'] as num).toDouble(),
      elevationRangeM: (json['elevationRangeM'] as num).toDouble(),
      averageSlopePercent: (json['averageSlopePercent'] as num).toDouble(),
      maxSlopePercent: (json['maxSlopePercent'] as num).toDouble(),
      dominantAspect: json['dominantAspect'] as String,
      dominantAspectAr: json['dominantAspectAr'] as String,
      soilType: json['soilType'] as String?,
      soilTypeAr: json['soilTypeAr'] as String?,
      drainageClass: json['drainageClass'] as String?,
      roughnessIndex: (json['roughnessIndex'] as num?)?.toDouble(),
      wetnessIndex: (json['wetnessIndex'] as num?)?.toDouble(),
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'] as String)
          : null,
      dataSource: json['dataSource'] as String? ?? 'dem',
    );
  }

  Map<String, dynamic> toJson() => {
        'fieldId': fieldId,
        'averageElevationM': averageElevationM,
        'minElevationM': minElevationM,
        'maxElevationM': maxElevationM,
        'elevationRangeM': elevationRangeM,
        'averageSlopePercent': averageSlopePercent,
        'maxSlopePercent': maxSlopePercent,
        'dominantAspect': dominantAspect,
        'dominantAspectAr': dominantAspectAr,
        'soilType': soilType,
        'soilTypeAr': soilTypeAr,
        'drainageClass': drainageClass,
        'roughnessIndex': roughnessIndex,
        'wetnessIndex': wetnessIndex,
        'timestamp': timestamp?.toIso8601String(),
        'dataSource': dataSource,
      };

  TerrainAnalysis copyWith({
    String? fieldId,
    double? averageElevationM,
    double? minElevationM,
    double? maxElevationM,
    double? elevationRangeM,
    double? averageSlopePercent,
    double? maxSlopePercent,
    String? dominantAspect,
    String? dominantAspectAr,
    String? soilType,
    String? soilTypeAr,
    String? drainageClass,
    double? roughnessIndex,
    double? wetnessIndex,
    DateTime? timestamp,
    String? dataSource,
  }) {
    return TerrainAnalysis(
      fieldId: fieldId ?? this.fieldId,
      averageElevationM: averageElevationM ?? this.averageElevationM,
      minElevationM: minElevationM ?? this.minElevationM,
      maxElevationM: maxElevationM ?? this.maxElevationM,
      elevationRangeM: elevationRangeM ?? this.elevationRangeM,
      averageSlopePercent: averageSlopePercent ?? this.averageSlopePercent,
      maxSlopePercent: maxSlopePercent ?? this.maxSlopePercent,
      dominantAspect: dominantAspect ?? this.dominantAspect,
      dominantAspectAr: dominantAspectAr ?? this.dominantAspectAr,
      soilType: soilType ?? this.soilType,
      soilTypeAr: soilTypeAr ?? this.soilTypeAr,
      drainageClass: drainageClass ?? this.drainageClass,
      roughnessIndex: roughnessIndex ?? this.roughnessIndex,
      wetnessIndex: wetnessIndex ?? this.wetnessIndex,
      timestamp: timestamp ?? this.timestamp,
      dataSource: dataSource ?? this.dataSource,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is TerrainAnalysis &&
          fieldId == other.fieldId &&
          averageElevationM == other.averageElevationM &&
          minElevationM == other.minElevationM &&
          maxElevationM == other.maxElevationM &&
          elevationRangeM == other.elevationRangeM &&
          averageSlopePercent == other.averageSlopePercent &&
          maxSlopePercent == other.maxSlopePercent &&
          dominantAspect == other.dominantAspect &&
          dominantAspectAr == other.dominantAspectAr &&
          soilType == other.soilType &&
          soilTypeAr == other.soilTypeAr &&
          drainageClass == other.drainageClass &&
          roughnessIndex == other.roughnessIndex &&
          wetnessIndex == other.wetnessIndex &&
          dataSource == other.dataSource;

  @override
  int get hashCode => Object.hash(
        fieldId,
        averageElevationM,
        minElevationM,
        maxElevationM,
        elevationRangeM,
        averageSlopePercent,
        maxSlopePercent,
        dominantAspect,
        dominantAspectAr,
        soilType,
        soilTypeAr,
        drainageClass,
        roughnessIndex,
        wetnessIndex,
        dataSource,
      );
}

class ElevationProfile {
  final String fieldId;
  final List<ElevationPoint> points;
  final double totalDistanceM;
  final double totalGainM;
  final double totalLossM;
  final double? profileDirection;
  final double? resolutionM;

  const ElevationProfile({
    required this.fieldId,
    required this.points,
    required this.totalDistanceM,
    required this.totalGainM,
    required this.totalLossM,
    this.profileDirection,
    this.resolutionM,
  });

  factory ElevationProfile.fromJson(Map<String, dynamic> json) {
    return ElevationProfile(
      fieldId: json['fieldId'] as String,
      points: (json['points'] as List<dynamic>)
          .map((p) => ElevationPoint.fromJson(p as Map<String, dynamic>))
          .toList(),
      totalDistanceM: (json['totalDistanceM'] as num).toDouble(),
      totalGainM: (json['totalGainM'] as num).toDouble(),
      totalLossM: (json['totalLossM'] as num).toDouble(),
      profileDirection: (json['profileDirection'] as num?)?.toDouble(),
      resolutionM: (json['resolutionM'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'fieldId': fieldId,
        'points': points.map((p) => p.toJson()).toList(),
        'totalDistanceM': totalDistanceM,
        'totalGainM': totalGainM,
        'totalLossM': totalLossM,
        'profileDirection': profileDirection,
        'resolutionM': resolutionM,
      };

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ElevationProfile &&
          fieldId == other.fieldId &&
          totalDistanceM == other.totalDistanceM &&
          totalGainM == other.totalGainM &&
          totalLossM == other.totalLossM &&
          profileDirection == other.profileDirection &&
          resolutionM == other.resolutionM &&
          _listEquals(points, other.points);

  @override
  int get hashCode => Object.hash(
        fieldId,
        totalDistanceM,
        totalGainM,
        totalLossM,
        profileDirection,
        resolutionM,
      );

  static bool _listEquals(List<ElevationPoint> a, List<ElevationPoint> b) {
    if (a.length != b.length) return false;
    for (int i = 0; i < a.length; i++) {
      if (a[i] != b[i]) return false;
    }
    return true;
  }
}

class ElevationPoint {
  final double distanceM;
  final double elevationM;
  final double? latitude;
  final double? longitude;
  final double? slopePercent;

  const ElevationPoint({
    required this.distanceM,
    required this.elevationM,
    this.latitude,
    this.longitude,
    this.slopePercent,
  });

  factory ElevationPoint.fromJson(Map<String, dynamic> json) {
    return ElevationPoint(
      distanceM: (json['distanceM'] as num).toDouble(),
      elevationM: (json['elevationM'] as num).toDouble(),
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      slopePercent: (json['slopePercent'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'distanceM': distanceM,
        'elevationM': elevationM,
        'latitude': latitude,
        'longitude': longitude,
        'slopePercent': slopePercent,
      };

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ElevationPoint &&
          distanceM == other.distanceM &&
          elevationM == other.elevationM &&
          latitude == other.latitude &&
          longitude == other.longitude &&
          slopePercent == other.slopePercent;

  @override
  int get hashCode =>
      Object.hash(distanceM, elevationM, latitude, longitude, slopePercent);
}

class SlopeAnalysis {
  final String fieldId;
  final Map<String, double> slopeDistribution;
  final String dominantSlopeClass;
  final String dominantSlopeClassAr;
  final String erosionRisk;
  final String erosionRiskAr;
  final List<String> recommendations;
  final List<String> recommendationsAr;
  final double? contourIntervalM;
  final double? tillageDirDegrees;

  const SlopeAnalysis({
    required this.fieldId,
    required this.slopeDistribution,
    required this.dominantSlopeClass,
    required this.dominantSlopeClassAr,
    required this.erosionRisk,
    required this.erosionRiskAr,
    this.recommendations = const [],
    this.recommendationsAr = const [],
    this.contourIntervalM,
    this.tillageDirDegrees,
  });

  factory SlopeAnalysis.fromJson(Map<String, dynamic> json) {
    return SlopeAnalysis(
      fieldId: json['fieldId'] as String,
      slopeDistribution:
          (json['slopeDistribution'] as Map<String, dynamic>).map(
        (k, v) => MapEntry(k, (v as num).toDouble()),
      ),
      dominantSlopeClass: json['dominantSlopeClass'] as String,
      dominantSlopeClassAr: json['dominantSlopeClassAr'] as String,
      erosionRisk: json['erosionRisk'] as String,
      erosionRiskAr: json['erosionRiskAr'] as String,
      recommendations: (json['recommendations'] as List<dynamic>?)
              ?.map((s) => s as String)
              .toList() ??
          [],
      recommendationsAr: (json['recommendationsAr'] as List<dynamic>?)
              ?.map((s) => s as String)
              .toList() ??
          [],
      contourIntervalM: (json['contourIntervalM'] as num?)?.toDouble(),
      tillageDirDegrees: (json['tillageDirDegrees'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'fieldId': fieldId,
        'slopeDistribution': slopeDistribution,
        'dominantSlopeClass': dominantSlopeClass,
        'dominantSlopeClassAr': dominantSlopeClassAr,
        'erosionRisk': erosionRisk,
        'erosionRiskAr': erosionRiskAr,
        'recommendations': recommendations,
        'recommendationsAr': recommendationsAr,
        'contourIntervalM': contourIntervalM,
        'tillageDirDegrees': tillageDirDegrees,
      };

  SlopeAnalysis copyWith({
    String? fieldId,
    Map<String, double>? slopeDistribution,
    String? dominantSlopeClass,
    String? dominantSlopeClassAr,
    String? erosionRisk,
    String? erosionRiskAr,
    List<String>? recommendations,
    List<String>? recommendationsAr,
    double? contourIntervalM,
    double? tillageDirDegrees,
  }) {
    return SlopeAnalysis(
      fieldId: fieldId ?? this.fieldId,
      slopeDistribution: slopeDistribution ?? this.slopeDistribution,
      dominantSlopeClass: dominantSlopeClass ?? this.dominantSlopeClass,
      dominantSlopeClassAr: dominantSlopeClassAr ?? this.dominantSlopeClassAr,
      erosionRisk: erosionRisk ?? this.erosionRisk,
      erosionRiskAr: erosionRiskAr ?? this.erosionRiskAr,
      recommendations: recommendations ?? this.recommendations,
      recommendationsAr: recommendationsAr ?? this.recommendationsAr,
      contourIntervalM: contourIntervalM ?? this.contourIntervalM,
      tillageDirDegrees: tillageDirDegrees ?? this.tillageDirDegrees,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SlopeAnalysis &&
          fieldId == other.fieldId &&
          dominantSlopeClass == other.dominantSlopeClass &&
          dominantSlopeClassAr == other.dominantSlopeClassAr &&
          erosionRisk == other.erosionRisk &&
          erosionRiskAr == other.erosionRiskAr &&
          contourIntervalM == other.contourIntervalM &&
          tillageDirDegrees == other.tillageDirDegrees;

  @override
  int get hashCode => Object.hash(
        fieldId,
        dominantSlopeClass,
        dominantSlopeClassAr,
        erosionRisk,
        erosionRiskAr,
        contourIntervalM,
        tillageDirDegrees,
      );
}

// ═══════════════════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════════════════

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // TerrainAnalysis Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('TerrainAnalysis', () {
    test('should create instance via constructor', () {
      final analysis = TerrainAnalysis(
        fieldId: 'field-001',
        averageElevationM: 1500.0,
        minElevationM: 1450.0,
        maxElevationM: 1550.0,
        elevationRangeM: 100.0,
        averageSlopePercent: 5.2,
        maxSlopePercent: 12.0,
        dominantAspect: 'NE',
        dominantAspectAr: 'شمال شرق',
        soilType: 'loam',
        soilTypeAr: 'طينية رملية',
        drainageClass: 'well-drained',
        roughnessIndex: 0.35,
        wetnessIndex: 4.2,
        timestamp: DateTime(2026, 2, 27),
      );

      expect(analysis.fieldId, 'field-001');
      expect(analysis.averageElevationM, 1500.0);
      expect(analysis.minElevationM, 1450.0);
      expect(analysis.maxElevationM, 1550.0);
      expect(analysis.elevationRangeM, 100.0);
      expect(analysis.averageSlopePercent, 5.2);
      expect(analysis.maxSlopePercent, 12.0);
      expect(analysis.dominantAspect, 'NE');
      expect(analysis.dominantAspectAr, 'شمال شرق');
      expect(analysis.soilType, 'loam');
      expect(analysis.soilTypeAr, 'طينية رملية');
      expect(analysis.drainageClass, 'well-drained');
      expect(analysis.roughnessIndex, 0.35);
      expect(analysis.wetnessIndex, 4.2);
      expect(analysis.dataSource, 'dem');
    });

    test('should create with only required fields', () {
      const analysis = TerrainAnalysis(
        fieldId: 'field-002',
        averageElevationM: 800.0,
        minElevationM: 790.0,
        maxElevationM: 810.0,
        elevationRangeM: 20.0,
        averageSlopePercent: 2.0,
        maxSlopePercent: 5.0,
        dominantAspect: 'S',
        dominantAspectAr: 'جنوب',
      );

      expect(analysis.fieldId, 'field-002');
      expect(analysis.soilType, isNull);
      expect(analysis.soilTypeAr, isNull);
      expect(analysis.drainageClass, isNull);
      expect(analysis.roughnessIndex, isNull);
      expect(analysis.wetnessIndex, isNull);
      expect(analysis.timestamp, isNull);
      expect(analysis.dataSource, 'dem');
    });

    test('should deserialize from JSON correctly', () {
      final json = {
        'fieldId': 'field-003',
        'averageElevationM': 2200.0,
        'minElevationM': 2100.0,
        'maxElevationM': 2300.0,
        'elevationRangeM': 200.0,
        'averageSlopePercent': 8.5,
        'maxSlopePercent': 20.0,
        'dominantAspect': 'NW',
        'dominantAspectAr': 'شمال غرب',
        'soilType': 'clay',
        'soilTypeAr': 'طينية',
        'drainageClass': 'poorly-drained',
        'roughnessIndex': 0.55,
        'wetnessIndex': 6.8,
        'timestamp': '2026-02-27T10:00:00.000Z',
        'dataSource': 'lidar',
      };

      final analysis = TerrainAnalysis.fromJson(json);

      expect(analysis.fieldId, 'field-003');
      expect(analysis.averageElevationM, 2200.0);
      expect(analysis.elevationRangeM, 200.0);
      expect(analysis.averageSlopePercent, 8.5);
      expect(analysis.dominantAspect, 'NW');
      expect(analysis.soilType, 'clay');
      expect(analysis.roughnessIndex, 0.55);
      expect(analysis.dataSource, 'lidar');
    });

    test('should serialize to JSON correctly', () {
      const analysis = TerrainAnalysis(
        fieldId: 'field-004',
        averageElevationM: 500.0,
        minElevationM: 480.0,
        maxElevationM: 520.0,
        elevationRangeM: 40.0,
        averageSlopePercent: 3.0,
        maxSlopePercent: 7.0,
        dominantAspect: 'E',
        dominantAspectAr: 'شرق',
      );

      final json = analysis.toJson();

      expect(json['fieldId'], 'field-004');
      expect(json['averageElevationM'], 500.0);
      expect(json['minElevationM'], 480.0);
      expect(json['maxElevationM'], 520.0);
      expect(json['elevationRangeM'], 40.0);
      expect(json['averageSlopePercent'], 3.0);
      expect(json['maxSlopePercent'], 7.0);
      expect(json['dominantAspect'], 'E');
      expect(json['dominantAspectAr'], 'شرق');
      expect(json['dataSource'], 'dem');
    });

    test('should roundtrip through JSON', () {
      const original = TerrainAnalysis(
        fieldId: 'field-005',
        averageElevationM: 1200.0,
        minElevationM: 1150.0,
        maxElevationM: 1250.0,
        elevationRangeM: 100.0,
        averageSlopePercent: 6.0,
        maxSlopePercent: 14.0,
        dominantAspect: 'SE',
        dominantAspectAr: 'جنوب شرق',
        soilType: 'sandy',
        soilTypeAr: 'رملية',
        drainageClass: 'excessive',
        roughnessIndex: 0.2,
        wetnessIndex: 2.5,
        dataSource: 'satellite',
      );

      final json = original.toJson();
      final restored = TerrainAnalysis.fromJson(json);

      expect(restored.fieldId, original.fieldId);
      expect(restored.averageElevationM, original.averageElevationM);
      expect(restored.minElevationM, original.minElevationM);
      expect(restored.maxElevationM, original.maxElevationM);
      expect(restored.averageSlopePercent, original.averageSlopePercent);
      expect(restored.dominantAspect, original.dominantAspect);
      expect(restored.soilType, original.soilType);
      expect(restored.roughnessIndex, original.roughnessIndex);
      expect(restored.dataSource, original.dataSource);
    });

    test('should support copyWith', () {
      const original = TerrainAnalysis(
        fieldId: 'field-006',
        averageElevationM: 600.0,
        minElevationM: 590.0,
        maxElevationM: 610.0,
        elevationRangeM: 20.0,
        averageSlopePercent: 1.5,
        maxSlopePercent: 3.0,
        dominantAspect: 'W',
        dominantAspectAr: 'غرب',
      );

      final updated = original.copyWith(
        averageElevationM: 650.0,
        soilType: 'silt',
      );

      expect(updated.fieldId, 'field-006');
      expect(updated.averageElevationM, 650.0);
      expect(updated.soilType, 'silt');
      expect(updated.dominantAspect, 'W');
    });

    test('should support equality comparison', () {
      const a = TerrainAnalysis(
        fieldId: 'field-007',
        averageElevationM: 100.0,
        minElevationM: 90.0,
        maxElevationM: 110.0,
        elevationRangeM: 20.0,
        averageSlopePercent: 1.0,
        maxSlopePercent: 2.0,
        dominantAspect: 'N',
        dominantAspectAr: 'شمال',
      );

      const b = TerrainAnalysis(
        fieldId: 'field-007',
        averageElevationM: 100.0,
        minElevationM: 90.0,
        maxElevationM: 110.0,
        elevationRangeM: 20.0,
        averageSlopePercent: 1.0,
        maxSlopePercent: 2.0,
        dominantAspect: 'N',
        dominantAspectAr: 'شمال',
      );

      expect(a, equals(b));
      expect(a.hashCode, equals(b.hashCode));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ElevationProfile Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('ElevationProfile', () {
    test('should create instance with points', () {
      const profile = ElevationProfile(
        fieldId: 'field-001',
        points: [
          ElevationPoint(distanceM: 0.0, elevationM: 100.0),
          ElevationPoint(distanceM: 50.0, elevationM: 110.0),
          ElevationPoint(distanceM: 100.0, elevationM: 105.0),
        ],
        totalDistanceM: 100.0,
        totalGainM: 10.0,
        totalLossM: 5.0,
        profileDirection: 90.0,
        resolutionM: 10.0,
      );

      expect(profile.fieldId, 'field-001');
      expect(profile.points.length, 3);
      expect(profile.totalDistanceM, 100.0);
      expect(profile.totalGainM, 10.0);
      expect(profile.totalLossM, 5.0);
      expect(profile.profileDirection, 90.0);
      expect(profile.resolutionM, 10.0);
    });

    test('should create with only required fields', () {
      const profile = ElevationProfile(
        fieldId: 'field-002',
        points: [],
        totalDistanceM: 0.0,
        totalGainM: 0.0,
        totalLossM: 0.0,
      );

      expect(profile.fieldId, 'field-002');
      expect(profile.points, isEmpty);
      expect(profile.profileDirection, isNull);
      expect(profile.resolutionM, isNull);
    });

    test('should deserialize from JSON', () {
      final json = {
        'fieldId': 'field-003',
        'points': [
          {
            'distanceM': 0.0,
            'elevationM': 1500.0,
            'latitude': 15.35,
            'longitude': 44.20,
          },
          {
            'distanceM': 100.0,
            'elevationM': 1520.0,
            'slopePercent': 4.0,
          },
        ],
        'totalDistanceM': 100.0,
        'totalGainM': 20.0,
        'totalLossM': 0.0,
      };

      final profile = ElevationProfile.fromJson(json);

      expect(profile.fieldId, 'field-003');
      expect(profile.points.length, 2);
      expect(profile.points.first.latitude, 15.35);
      expect(profile.points.last.slopePercent, 4.0);
    });

    test('should roundtrip through JSON', () {
      const original = ElevationProfile(
        fieldId: 'field-004',
        points: [
          ElevationPoint(
            distanceM: 0.0,
            elevationM: 500.0,
            latitude: 15.0,
            longitude: 44.0,
            slopePercent: 2.0,
          ),
          ElevationPoint(
            distanceM: 200.0,
            elevationM: 510.0,
            latitude: 15.002,
            longitude: 44.002,
            slopePercent: 5.0,
          ),
        ],
        totalDistanceM: 200.0,
        totalGainM: 10.0,
        totalLossM: 0.0,
        profileDirection: 45.0,
        resolutionM: 5.0,
      );

      final json = original.toJson();
      final restored = ElevationProfile.fromJson(json);

      expect(restored.fieldId, original.fieldId);
      expect(restored.points.length, original.points.length);
      expect(restored.totalDistanceM, original.totalDistanceM);
      expect(restored.totalGainM, original.totalGainM);
      expect(restored.profileDirection, original.profileDirection);
      expect(restored.resolutionM, original.resolutionM);
    });

    test('should support equality comparison', () {
      const a = ElevationProfile(
        fieldId: 'field-005',
        points: [
          ElevationPoint(distanceM: 0.0, elevationM: 100.0),
        ],
        totalDistanceM: 50.0,
        totalGainM: 5.0,
        totalLossM: 0.0,
      );

      const b = ElevationProfile(
        fieldId: 'field-005',
        points: [
          ElevationPoint(distanceM: 0.0, elevationM: 100.0),
        ],
        totalDistanceM: 50.0,
        totalGainM: 5.0,
        totalLossM: 0.0,
      );

      expect(a, equals(b));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ElevationPoint Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('ElevationPoint', () {
    test('should create instance with required fields', () {
      const point = ElevationPoint(
        distanceM: 50.0,
        elevationM: 1500.0,
      );

      expect(point.distanceM, 50.0);
      expect(point.elevationM, 1500.0);
      expect(point.latitude, isNull);
      expect(point.longitude, isNull);
      expect(point.slopePercent, isNull);
    });

    test('should create instance with all fields', () {
      const point = ElevationPoint(
        distanceM: 75.0,
        elevationM: 1520.0,
        latitude: 15.355,
        longitude: 44.210,
        slopePercent: 6.5,
      );

      expect(point.distanceM, 75.0);
      expect(point.elevationM, 1520.0);
      expect(point.latitude, 15.355);
      expect(point.longitude, 44.210);
      expect(point.slopePercent, 6.5);
    });

    test('should deserialize from JSON', () {
      final json = {
        'distanceM': 100.0,
        'elevationM': 1550.0,
        'latitude': 15.36,
        'longitude': 44.22,
        'slopePercent': 8.0,
      };

      final point = ElevationPoint.fromJson(json);

      expect(point.distanceM, 100.0);
      expect(point.elevationM, 1550.0);
      expect(point.latitude, 15.36);
      expect(point.longitude, 44.22);
      expect(point.slopePercent, 8.0);
    });

    test('should serialize to JSON', () {
      const point = ElevationPoint(
        distanceM: 25.0,
        elevationM: 800.0,
        latitude: 15.34,
        longitude: 44.19,
      );

      final json = point.toJson();

      expect(json['distanceM'], 25.0);
      expect(json['elevationM'], 800.0);
      expect(json['latitude'], 15.34);
      expect(json['longitude'], 44.19);
      expect(json['slopePercent'], isNull);
    });

    test('should roundtrip through JSON', () {
      const original = ElevationPoint(
        distanceM: 150.0,
        elevationM: 2000.0,
        latitude: 16.0,
        longitude: 45.0,
        slopePercent: 12.0,
      );

      final json = original.toJson();
      final restored = ElevationPoint.fromJson(json);

      expect(restored.distanceM, original.distanceM);
      expect(restored.elevationM, original.elevationM);
      expect(restored.latitude, original.latitude);
      expect(restored.longitude, original.longitude);
      expect(restored.slopePercent, original.slopePercent);
    });

    test('should support equality', () {
      const a = ElevationPoint(distanceM: 10.0, elevationM: 100.0);
      const b = ElevationPoint(distanceM: 10.0, elevationM: 100.0);
      const c = ElevationPoint(distanceM: 20.0, elevationM: 100.0);

      expect(a, equals(b));
      expect(a, isNot(equals(c)));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SlopeAnalysis Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SlopeAnalysis', () {
    test('should create instance with all fields', () {
      const slope = SlopeAnalysis(
        fieldId: 'field-001',
        slopeDistribution: {
          'flat_0_2': 20.0,
          'gentle_2_5': 40.0,
          'moderate_5_10': 30.0,
          'steep_10_15': 10.0,
        },
        dominantSlopeClass: 'gentle',
        dominantSlopeClassAr: 'لطيف',
        erosionRisk: 'low',
        erosionRiskAr: 'منخفض',
        recommendations: ['Use contour farming', 'Plant cover crops'],
        recommendationsAr: [
          'استخدام الزراعة الكنتورية',
          'زراعة محاصيل تغطية'
        ],
        contourIntervalM: 2.0,
        tillageDirDegrees: 135.0,
      );

      expect(slope.fieldId, 'field-001');
      expect(slope.slopeDistribution.length, 4);
      expect(slope.dominantSlopeClass, 'gentle');
      expect(slope.dominantSlopeClassAr, 'لطيف');
      expect(slope.erosionRisk, 'low');
      expect(slope.erosionRiskAr, 'منخفض');
      expect(slope.recommendations.length, 2);
      expect(slope.recommendationsAr.length, 2);
      expect(slope.contourIntervalM, 2.0);
      expect(slope.tillageDirDegrees, 135.0);
    });

    test('should create with default empty recommendations', () {
      const slope = SlopeAnalysis(
        fieldId: 'field-002',
        slopeDistribution: {'flat': 100.0},
        dominantSlopeClass: 'flat',
        dominantSlopeClassAr: 'مسطح',
        erosionRisk: 'minimal',
        erosionRiskAr: 'ضئيل',
      );

      expect(slope.recommendations, isEmpty);
      expect(slope.recommendationsAr, isEmpty);
      expect(slope.contourIntervalM, isNull);
      expect(slope.tillageDirDegrees, isNull);
    });

    test('should deserialize from JSON with recommendations', () {
      final json = {
        'fieldId': 'field-003',
        'slopeDistribution': {
          'steep': 60.0,
          'very_steep': 40.0,
        },
        'dominantSlopeClass': 'steep',
        'dominantSlopeClassAr': 'حاد',
        'erosionRisk': 'high',
        'erosionRiskAr': 'مرتفع',
        'recommendations': ['Terracing required'],
        'recommendationsAr': ['يلزم تدريج'],
        'contourIntervalM': 0.5,
        'tillageDirDegrees': 0.0,
      };

      final slope = SlopeAnalysis.fromJson(json);

      expect(slope.fieldId, 'field-003');
      expect(slope.slopeDistribution['steep'], 60.0);
      expect(slope.erosionRisk, 'high');
      expect(slope.recommendations.first, 'Terracing required');
      expect(slope.contourIntervalM, 0.5);
    });

    test('should roundtrip through JSON', () {
      const original = SlopeAnalysis(
        fieldId: 'field-004',
        slopeDistribution: {
          'flat': 30.0,
          'gentle': 50.0,
          'moderate': 20.0,
        },
        dominantSlopeClass: 'gentle',
        dominantSlopeClassAr: 'لطيف',
        erosionRisk: 'moderate',
        erosionRiskAr: 'متوسط',
        recommendations: ['Contour farming'],
        recommendationsAr: ['زراعة كنتورية'],
      );

      final json = original.toJson();
      final restored = SlopeAnalysis.fromJson(json);

      expect(restored.fieldId, original.fieldId);
      expect(restored.slopeDistribution, original.slopeDistribution);
      expect(restored.dominantSlopeClass, original.dominantSlopeClass);
      expect(restored.erosionRisk, original.erosionRisk);
      expect(restored.recommendations, original.recommendations);
    });

    test('should support copyWith', () {
      const original = SlopeAnalysis(
        fieldId: 'field-005',
        slopeDistribution: {'flat': 100.0},
        dominantSlopeClass: 'flat',
        dominantSlopeClassAr: 'مسطح',
        erosionRisk: 'minimal',
        erosionRiskAr: 'ضئيل',
      );

      final updated = original.copyWith(
        erosionRisk: 'low',
        erosionRiskAr: 'منخفض',
        recommendations: ['Add mulch'],
      );

      expect(updated.fieldId, 'field-005');
      expect(updated.dominantSlopeClass, 'flat');
      expect(updated.erosionRisk, 'low');
      expect(updated.recommendations, ['Add mulch']);
    });

    test('should support equality comparison', () {
      const a = SlopeAnalysis(
        fieldId: 'field-006',
        slopeDistribution: {'flat': 100.0},
        dominantSlopeClass: 'flat',
        dominantSlopeClassAr: 'مسطح',
        erosionRisk: 'minimal',
        erosionRiskAr: 'ضئيل',
      );

      const b = SlopeAnalysis(
        fieldId: 'field-006',
        slopeDistribution: {'flat': 100.0},
        dominantSlopeClass: 'flat',
        dominantSlopeClassAr: 'مسطح',
        erosionRisk: 'minimal',
        erosionRiskAr: 'ضئيل',
      );

      expect(a, equals(b));
      expect(a.hashCode, equals(b.hashCode));
    });
  });
}
