/// NDVI Test Mocks - كائنات وهمية لاختبار NDVI
///
/// Mock classes for NDVI feature testing using mocktail
library;

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/features/satellite/data/models/ndvi_data.dart';
import 'package:sahool_field_app/features/ndvi/domain/ndvi_value.dart';

// ═══════════════════════════════════════════════════════════════════════════
// HTTP Mocks - كائنات HTTP الوهمية
// ═══════════════════════════════════════════════════════════════════════════

/// Mock HTTP Client for API testing
class MockHttpClient extends Mock implements http.Client {}

/// Mock HTTP Response
class MockHttpResponse extends Mock implements http.Response {}

/// Fake URI for mocktail fallback
class FakeUri extends Fake implements Uri {}

// ═══════════════════════════════════════════════════════════════════════════
// NDVI Repository Mock - مستودع NDVI الوهمي
// ═══════════════════════════════════════════════════════════════════════════

/// Abstract interface for NDVI Repository (for testing)
abstract class NdviRepository {
  /// Fetch NDVI analysis for a field
  Future<NdviAnalysis> getFieldNdvi(String fieldId);

  /// Fetch NDVI time series for a field
  Future<List<NdviDataPoint>> getNdviTimeSeries(
    String fieldId, {
    DateTime? startDate,
    DateTime? endDate,
  });

  /// Fetch latest NDVI value for a field
  Future<double> getLatestNdvi(String fieldId);

  /// Fetch NDVI alerts for a field
  Future<List<Map<String, dynamic>>> getNdviAlerts(String fieldId);

  /// Check if NDVI data is available for field
  Future<bool> hasNdviData(String fieldId);
}

/// Mock NDVI Repository
class MockNdviRepository extends Mock implements NdviRepository {}

// ═══════════════════════════════════════════════════════════════════════════
// NDVI Service Mock - خدمة NDVI الوهمية
// ═══════════════════════════════════════════════════════════════════════════

/// Abstract interface for NDVI Service
abstract class NdviService {
  /// Calculate NDVI from red and NIR bands
  double calculateNdvi(double red, double nir);

  /// Classify NDVI value into health category
  VegetationHealth classifyHealth(double ndvi);

  /// Calculate trend from time series
  double calculateTrend(List<NdviDataPoint> timeSeries);

  /// Check if NDVI indicates vegetation stress
  bool isVegetationStressed(double ndvi);

  /// Get color for NDVI value
  Color getNdviColor(double ndvi);
}

/// Mock NDVI Service
class MockNdviService extends Mock implements NdviService {}

// ═══════════════════════════════════════════════════════════════════════════
// NDVI Calculator Mock - حاسبة NDVI الوهمية
// ═══════════════════════════════════════════════════════════════════════════

/// Abstract interface for NDVI calculations
abstract class NdviCalculator {
  /// Calculate NDVI from reflectance values
  double calculate(double red, double nir);

  /// Calculate statistics from time series
  NdviStatistics calculateStatistics(List<NdviTimePoint> history);

  /// Calculate change rate between two values
  double calculateChangeRate(double current, double previous);

  /// Determine trend direction from time series
  TrendDirection determineTrend(List<NdviTimePoint> history);

  /// Validate NDVI value is in valid range
  bool isValidNdvi(double value);
}

/// Mock NDVI Calculator
class MockNdviCalculator extends Mock implements NdviCalculator {}

// ═══════════════════════════════════════════════════════════════════════════
// NDVI Alert Service Mock - خدمة تنبيهات NDVI الوهمية
// ═══════════════════════════════════════════════════════════════════════════

/// Alert types for NDVI
enum NdviAlertType {
  critical,
  warning,
  info,
}

/// Abstract interface for NDVI Alert Service
abstract class NdviAlertService {
  /// Check for low vegetation alerts
  Future<List<Map<String, dynamic>>> checkLowVegetationAlerts(
    String fieldId,
    double currentNdvi,
  );

  /// Check for declining trend alerts
  Future<List<Map<String, dynamic>>> checkDecliningTrendAlerts(
    String fieldId,
    List<NdviDataPoint> history,
  );

  /// Get all active alerts for field
  Future<List<Map<String, dynamic>>> getActiveAlerts(String fieldId);

  /// Dismiss an alert
  Future<void> dismissAlert(String alertId);

  /// Get alert threshold for field
  double getAlertThreshold(String fieldId);
}

/// Mock NDVI Alert Service
class MockNdviAlertService extends Mock implements NdviAlertService {}

// ═══════════════════════════════════════════════════════════════════════════
// Test Setup Helpers - مساعدات إعداد الاختبار
// ═══════════════════════════════════════════════════════════════════════════

/// Setup common mocktail fallback values
void setupNdviMocktailFallbacks() {
  registerFallbackValue(FakeUri());
  registerFallbackValue(DateTime.now());
}

/// Create mock NdviDataPoint list from JSON
List<NdviDataPoint> createMockDataPoints(List<Map<String, dynamic>> json) {
  return json.map((e) => NdviDataPoint.fromJson(e)).toList();
}

/// Create mock NdviTimePoint list
List<NdviTimePoint> createMockTimePoints(List<Map<String, dynamic>> json) {
  return json
      .map((e) => NdviTimePoint(
            date: DateTime.parse(e['date'] as String),
            value: (e['value'] as num).toDouble(),
            cloudCover: e['cloud_coverage'] != null
                ? (e['cloud_coverage'] as num).toDouble()
                : null,
          ))
      .toList();
}

/// Create mock NdviAnalysis from JSON
NdviAnalysis createMockAnalysis(Map<String, dynamic> json) {
  return NdviAnalysis.fromJson(json);
}

/// Create mock NdviStatistics
NdviStatistics createMockStatistics({
  required double current,
  required double average,
  required double min,
  required double max,
  required double trend,
  List<NdviTimePoint>? history,
  DateTime? lastUpdated,
}) {
  return NdviStatistics(
    current: current,
    average: average,
    min: min,
    max: max,
    trend: trend,
    history: history ?? [],
    lastUpdated: lastUpdated ?? DateTime.now(),
  );
}

/// Create mock NdviValue
NdviValue createMockNdviValue({
  required double value,
  DateTime? capturedAt,
  String? source,
}) {
  return NdviValue(
    value: value,
    capturedAt: capturedAt ?? DateTime.now(),
    source: source,
  );
}
