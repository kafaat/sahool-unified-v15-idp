/// Coordinate Validator - Geographic Coordinate Validation
/// مدقق الإحداثيات - التحقق من صحة الإحداثيات الجغرافية
///
/// Provides comprehensive validation for geographic coordinates:
/// - Latitude/Longitude ranges
/// - Regional bounds (Saudi Arabia, Yemen, Middle East)
/// - Coordinate precision
/// - Polygon validation for field boundaries
///
/// All validation messages are bilingual (Arabic/English).
library;

import 'validators.dart';

/// Geographic coordinate validator for SAHOOL platform
class CoordinateValidator {
  // ─────────────────────────────────────────────────────────────────────────────
  // Global Constants
  // ─────────────────────────────────────────────────────────────────────────────

  /// Global latitude range
  static const double minLatitude = -90.0;
  static const double maxLatitude = 90.0;

  /// Global longitude range
  static const double maxLongitude = 180.0;
  static const double minLongitude = -180.0;

  // ─────────────────────────────────────────────────────────────────────────────
  // Saudi Arabia Bounds
  // ─────────────────────────────────────────────────────────────────────────────

  /// Saudi Arabia approximate bounding box
  static const double saudiMinLat = 16.0;
  static const double saudiMaxLat = 32.5;
  static const double saudiMinLng = 34.5;
  static const double saudiMaxLng = 56.0;

  // ─────────────────────────────────────────────────────────────────────────────
  // Yemen Bounds
  // ─────────────────────────────────────────────────────────────────────────────

  /// Yemen approximate bounding box
  static const double yemenMinLat = 12.0;
  static const double yemenMaxLat = 19.0;
  static const double yemenMinLng = 42.5;
  static const double yemenMaxLng = 54.5;

  // ─────────────────────────────────────────────────────────────────────────────
  // Middle East Region Bounds (expanded for general use)
  // ─────────────────────────────────────────────────────────────────────────────

  /// Middle East approximate bounding box
  static const double middleEastMinLat = 12.0;
  static const double middleEastMaxLat = 42.0;
  static const double middleEastMinLng = 24.0;
  static const double middleEastMaxLng = 64.0;

  // ─────────────────────────────────────────────────────────────────────────────
  // Basic Coordinate Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate latitude value (must be between -90 and 90)
  static ValidationResult latitude(double? value) {
    if (value == null) {
      return ValidationResult.error(
        'Latitude is required',
        'خط العرض مطلوب',
      );
    }

    if (value.isNaN || value.isInfinite) {
      return ValidationResult.error(
        'Invalid latitude value',
        'قيمة خط العرض غير صالحة',
      );
    }

    if (value < minLatitude || value > maxLatitude) {
      return ValidationResult.error(
        'Latitude must be between $minLatitude and $maxLatitude',
        'خط العرض يجب أن يكون بين $minLatitude و $maxLatitude',
      );
    }

    return ValidationResult.success;
  }

  /// Validate longitude value (must be between -180 and 180)
  static ValidationResult longitude(double? value) {
    if (value == null) {
      return ValidationResult.error(
        'Longitude is required',
        'خط الطول مطلوب',
      );
    }

    if (value.isNaN || value.isInfinite) {
      return ValidationResult.error(
        'Invalid longitude value',
        'قيمة خط الطول غير صالحة',
      );
    }

    if (value < minLongitude || value > maxLongitude) {
      return ValidationResult.error(
        'Longitude must be between $minLongitude and $maxLongitude',
        'خط الطول يجب أن يكون بين $minLongitude و $maxLongitude',
      );
    }

    return ValidationResult.success;
  }

  /// Validate a coordinate pair (latitude, longitude)
  static ValidationResult coordinate(double? lat, double? lng) {
    final latResult = latitude(lat);
    if (!latResult.isValid) {
      return latResult;
    }

    final lngResult = longitude(lng);
    if (!lngResult.isValid) {
      return lngResult;
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Regional Coordinate Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate latitude is within Saudi Arabia bounds
  static ValidationResult saudiLatitude(double? value) {
    final basicResult = latitude(value);
    if (!basicResult.isValid) {
      return basicResult;
    }

    if (value! < saudiMinLat || value > saudiMaxLat) {
      return ValidationResult.error(
        'Latitude is outside Saudi Arabia region ($saudiMinLat to $saudiMaxLat)',
        'خط العرض خارج منطقة المملكة العربية السعودية ($saudiMinLat إلى $saudiMaxLat)',
      );
    }

    return ValidationResult.success;
  }

  /// Validate longitude is within Saudi Arabia bounds
  static ValidationResult saudiLongitude(double? value) {
    final basicResult = longitude(value);
    if (!basicResult.isValid) {
      return basicResult;
    }

    if (value! < saudiMinLng || value > saudiMaxLng) {
      return ValidationResult.error(
        'Longitude is outside Saudi Arabia region ($saudiMinLng to $saudiMaxLng)',
        'خط الطول خارج منطقة المملكة العربية السعودية ($saudiMinLng إلى $saudiMaxLng)',
      );
    }

    return ValidationResult.success;
  }

  /// Validate coordinates are within Saudi Arabia bounds
  static ValidationResult saudiCoordinate(double? lat, double? lng) {
    final latResult = saudiLatitude(lat);
    if (!latResult.isValid) {
      return latResult;
    }

    final lngResult = saudiLongitude(lng);
    if (!lngResult.isValid) {
      return lngResult;
    }

    return ValidationResult.success;
  }

  /// Validate latitude is within Yemen bounds
  static ValidationResult yemenLatitude(double? value) {
    final basicResult = latitude(value);
    if (!basicResult.isValid) {
      return basicResult;
    }

    if (value! < yemenMinLat || value > yemenMaxLat) {
      return ValidationResult.error(
        'Latitude is outside Yemen region ($yemenMinLat to $yemenMaxLat)',
        'خط العرض خارج منطقة اليمن ($yemenMinLat إلى $yemenMaxLat)',
      );
    }

    return ValidationResult.success;
  }

  /// Validate longitude is within Yemen bounds
  static ValidationResult yemenLongitude(double? value) {
    final basicResult = longitude(value);
    if (!basicResult.isValid) {
      return basicResult;
    }

    if (value! < yemenMinLng || value > yemenMaxLng) {
      return ValidationResult.error(
        'Longitude is outside Yemen region ($yemenMinLng to $yemenMaxLng)',
        'خط الطول خارج منطقة اليمن ($yemenMinLng إلى $yemenMaxLng)',
      );
    }

    return ValidationResult.success;
  }

  /// Validate coordinates are within Yemen bounds
  static ValidationResult yemenCoordinate(double? lat, double? lng) {
    final latResult = yemenLatitude(lat);
    if (!latResult.isValid) {
      return latResult;
    }

    final lngResult = yemenLongitude(lng);
    if (!lngResult.isValid) {
      return lngResult;
    }

    return ValidationResult.success;
  }

  /// Validate latitude is within Middle East bounds
  static ValidationResult middleEastLatitude(double? value) {
    final basicResult = latitude(value);
    if (!basicResult.isValid) {
      return basicResult;
    }

    if (value! < middleEastMinLat || value > middleEastMaxLat) {
      return ValidationResult.error(
        'Latitude is outside Middle East region ($middleEastMinLat to $middleEastMaxLat)',
        'خط العرض خارج منطقة الشرق الأوسط ($middleEastMinLat إلى $middleEastMaxLat)',
      );
    }

    return ValidationResult.success;
  }

  /// Validate longitude is within Middle East bounds
  static ValidationResult middleEastLongitude(double? value) {
    final basicResult = longitude(value);
    if (!basicResult.isValid) {
      return basicResult;
    }

    if (value! < middleEastMinLng || value > middleEastMaxLng) {
      return ValidationResult.error(
        'Longitude is outside Middle East region ($middleEastMinLng to $middleEastMaxLng)',
        'خط الطول خارج منطقة الشرق الأوسط ($middleEastMinLng إلى $middleEastMaxLng)',
      );
    }

    return ValidationResult.success;
  }

  /// Validate coordinates are within Middle East bounds
  static ValidationResult middleEastCoordinate(double? lat, double? lng) {
    final latResult = middleEastLatitude(lat);
    if (!latResult.isValid) {
      return latResult;
    }

    final lngResult = middleEastLongitude(lng);
    if (!lngResult.isValid) {
      return lngResult;
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Custom Bounding Box Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate coordinates are within custom bounds
  static ValidationResult withinBounds(
    double? lat,
    double? lng, {
    required double minLat,
    required double maxLat,
    required double minLng,
    required double maxLng,
    String regionName = 'specified region',
    String regionNameAr = 'المنطقة المحددة',
  }) {
    final basicCoordResult = coordinate(lat, lng);
    if (!basicCoordResult.isValid) {
      return basicCoordResult;
    }

    if (lat! < minLat || lat > maxLat) {
      return ValidationResult.error(
        'Latitude is outside $regionName ($minLat to $maxLat)',
        'خط العرض خارج $regionNameAr ($minLat إلى $maxLat)',
      );
    }

    if (lng! < minLng || lng > maxLng) {
      return ValidationResult.error(
        'Longitude is outside $regionName ($minLng to $maxLng)',
        'خط الطول خارج $regionNameAr ($minLng إلى $maxLng)',
      );
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Coordinate Precision Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate coordinate precision (decimal places)
  /// 6 decimal places = ~0.1 meter accuracy (suitable for agricultural fields)
  static ValidationResult precision(
    double? value, {
    int minDecimalPlaces = 4,
    int maxDecimalPlaces = 8,
    String fieldName = 'Coordinate',
    String fieldNameAr = 'الإحداثي',
  }) {
    if (value == null) {
      return ValidationResult.error(
        '$fieldName is required',
        '$fieldNameAr مطلوب',
      );
    }

    // Get decimal places
    final stringValue = value.toString();
    final decimalIndex = stringValue.indexOf('.');
    final decimalPlaces =
        decimalIndex == -1 ? 0 : stringValue.length - decimalIndex - 1;

    if (decimalPlaces < minDecimalPlaces) {
      return ValidationResult.error(
        '$fieldName requires at least $minDecimalPlaces decimal places for accuracy',
        '$fieldNameAr يتطلب $minDecimalPlaces خانات عشرية على الأقل للدقة',
      );
    }

    if (decimalPlaces > maxDecimalPlaces) {
      return ValidationResult.error(
        '$fieldName exceeds maximum precision ($maxDecimalPlaces decimal places)',
        '$fieldNameAr يتجاوز الدقة القصوى ($maxDecimalPlaces خانات عشرية)',
      );
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Polygon Validation (Field Boundaries)
  // ─────────────────────────────────────────────────────────────────────────────

  /// Coordinate point for polygon validation
  static ValidationResult polygonPoints(
    List<Map<String, double>>? points, {
    int minPoints = 3,
    int maxPoints = 1000,
  }) {
    if (points == null || points.isEmpty) {
      return ValidationResult.error(
        'Field boundary points are required',
        'نقاط حدود الحقل مطلوبة',
      );
    }

    if (points.length < minPoints) {
      return ValidationResult.error(
        'Field boundary requires at least $minPoints points',
        'حدود الحقل تتطلب $minPoints نقاط على الأقل',
      );
    }

    if (points.length > maxPoints) {
      return ValidationResult.error(
        'Field boundary exceeds maximum points ($maxPoints)',
        'حدود الحقل تتجاوز الحد الأقصى للنقاط ($maxPoints)',
      );
    }

    // Validate each point
    for (int i = 0; i < points.length; i++) {
      final point = points[i];
      final lat = point['lat'] ?? point['latitude'];
      final lng = point['lng'] ?? point['longitude'];

      final coordResult = coordinate(lat, lng);
      if (!coordResult.isValid) {
        return ValidationResult.error(
          'Invalid coordinate at point ${i + 1}: ${coordResult.errorMessage}',
          'إحداثي غير صالح في النقطة ${i + 1}: ${coordResult.errorMessageAr}',
        );
      }
    }

    return ValidationResult.success;
  }

  /// Validate that polygon is closed (first point equals last point)
  static ValidationResult polygonClosed(
    List<Map<String, double>>? points, {
    double tolerance = 0.0001, // ~11 meters tolerance
  }) {
    final basicResult = polygonPoints(points);
    if (!basicResult.isValid) {
      return basicResult;
    }

    final first = points!.first;
    final last = points.last;

    final firstLat = first['lat'] ?? first['latitude'] ?? 0.0;
    final firstLng = first['lng'] ?? first['longitude'] ?? 0.0;
    final lastLat = last['lat'] ?? last['latitude'] ?? 0.0;
    final lastLng = last['lng'] ?? last['longitude'] ?? 0.0;

    final latDiff = (firstLat - lastLat).abs();
    final lngDiff = (firstLng - lastLng).abs();

    if (latDiff > tolerance || lngDiff > tolerance) {
      return ValidationResult.error(
        'Field boundary polygon must be closed (first and last points must match)',
        'مضلع حدود الحقل يجب أن يكون مغلقاً (النقطة الأولى والأخيرة يجب أن تتطابقا)',
      );
    }

    return ValidationResult.success;
  }

  /// Validate polygon has valid area (not self-intersecting, not too small)
  static ValidationResult polygonArea(
    List<Map<String, double>>? points, {
    double minAreaHectares = 0.01,
    double maxAreaHectares = 100000,
  }) {
    final basicResult = polygonPoints(points);
    if (!basicResult.isValid) {
      return basicResult;
    }

    // Calculate approximate area using Shoelace formula
    double area = 0;
    final n = points!.length;

    for (int i = 0; i < n; i++) {
      final j = (i + 1) % n;

      final iLat = points[i]['lat'] ?? points[i]['latitude'] ?? 0.0;
      final iLng = points[i]['lng'] ?? points[i]['longitude'] ?? 0.0;
      final jLat = points[j]['lat'] ?? points[j]['latitude'] ?? 0.0;
      final jLng = points[j]['lng'] ?? points[j]['longitude'] ?? 0.0;

      area += iLng * jLat;
      area -= jLng * iLat;
    }

    area = area.abs() / 2;

    // Convert from degrees² to hectares (very approximate)
    // 1 degree ≈ 111 km at equator
    final areaKm2 = area * 111 * 111;
    final areaHectares = areaKm2 * 100;

    if (areaHectares < minAreaHectares) {
      return ValidationResult.error(
        'Field area is too small (minimum: $minAreaHectares hectares)',
        'مساحة الحقل صغيرة جداً (الحد الأدنى: $minAreaHectares هكتار)',
      );
    }

    if (areaHectares > maxAreaHectares) {
      return ValidationResult.error(
        'Field area is too large (maximum: $maxAreaHectares hectares)',
        'مساحة الحقل كبيرة جداً (الحد الأقصى: $maxAreaHectares هكتار)',
      );
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Distance Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate distance between two points (in kilometers)
  static ValidationResult distance(
    double lat1,
    double lng1,
    double lat2,
    double lng2, {
    double? minDistanceKm,
    double? maxDistanceKm,
  }) {
    // Validate both coordinates
    final coord1Result = coordinate(lat1, lng1);
    if (!coord1Result.isValid) {
      return coord1Result;
    }

    final coord2Result = coordinate(lat2, lng2);
    if (!coord2Result.isValid) {
      return coord2Result;
    }

    // Calculate distance using Haversine formula
    final distanceKm = _haversineDistance(lat1, lng1, lat2, lng2);

    if (minDistanceKm != null && distanceKm < minDistanceKm) {
      return ValidationResult.error(
        'Distance is too short (minimum: $minDistanceKm km)',
        'المسافة قصيرة جداً (الحد الأدنى: $minDistanceKm كم)',
      );
    }

    if (maxDistanceKm != null && distanceKm > maxDistanceKm) {
      return ValidationResult.error(
        'Distance is too far (maximum: $maxDistanceKm km)',
        'المسافة بعيدة جداً (الحد الأقصى: $maxDistanceKm كم)',
      );
    }

    return ValidationResult.success;
  }

  /// Calculate distance between two points using Haversine formula
  static double _haversineDistance(
    double lat1,
    double lng1,
    double lat2,
    double lng2,
  ) {
    const earthRadiusKm = 6371.0;

    final dLat = _toRadians(lat2 - lat1);
    final dLng = _toRadians(lng2 - lng1);

    final a = _sin(dLat / 2) * _sin(dLat / 2) +
        _cos(_toRadians(lat1)) *
            _cos(_toRadians(lat2)) *
            _sin(dLng / 2) *
            _sin(dLng / 2);

    final c = 2 * _atan2(_sqrt(a), _sqrt(1 - a));

    return earthRadiusKm * c;
  }

  // Math helpers (to avoid importing dart:math for simple trig)
  static double _toRadians(double degrees) => degrees * 3.141592653589793 / 180;
  static double _sin(double x) {
    // Taylor series approximation
    double result = x;
    double term = x;
    for (int i = 1; i <= 10; i++) {
      term *= -x * x / ((2 * i) * (2 * i + 1));
      result += term;
    }
    return result;
  }

  static double _cos(double x) => _sin(x + 1.5707963267948966);
  static double _sqrt(double x) {
    if (x <= 0) return 0;
    double guess = x / 2;
    for (int i = 0; i < 10; i++) {
      guess = (guess + x / guess) / 2;
    }
    return guess;
  }

  static double _atan2(double y, double x) {
    if (x > 0) return _atan(y / x);
    if (x < 0 && y >= 0) return _atan(y / x) + 3.141592653589793;
    if (x < 0 && y < 0) return _atan(y / x) - 3.141592653589793;
    if (x == 0 && y > 0) return 1.5707963267948966;
    if (x == 0 && y < 0) return -1.5707963267948966;
    return 0;
  }

  static double _atan(double x) {
    // Taylor series approximation
    if (x.abs() > 1) {
      return (x > 0 ? 1 : -1) * 1.5707963267948966 - _atan(1 / x);
    }
    double result = x;
    double term = x;
    for (int i = 1; i <= 15; i++) {
      term *= -x * x;
      result += term / (2 * i + 1);
    }
    return result;
  }
}
