/// Irrigation Mocks
/// فئات وهمية للري للاختبارات
///
/// Provides mock implementations for irrigation feature unit tests.
/// يوفر تطبيقات وهمية لاختبارات وحدة ميزة الري
library;

import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/features/irrigation/data/remote/irrigation_api.dart';
import 'package:sahool_field_app/features/advisor/data/models/irrigation_models.dart'
    hide IrrigationEvent, IrrigationCalculation, IrrigationSchedule; // Hide to avoid conflict with irrigation_api
import 'package:sahool_field_app/features/pivot_irrigation/domain/models/pivot_models.dart';
import 'package:sahool_field_app/features/pivot_irrigation/domain/models/span_zone_models.dart';

import 'irrigation_fixtures.dart';

// ═══════════════════════════════════════════════════════════════════════════
// HTTP Client Mock - محاكاة عميل HTTP
// ═══════════════════════════════════════════════════════════════════════════

/// Mock HTTP Client for testing irrigation API calls
class MockHttpClient extends Mock implements http.Client {}

/// Mock HTTP Response for simulating API responses
class MockHttpResponse extends Mock implements http.Response {}

// ═══════════════════════════════════════════════════════════════════════════
// Irrigation API Mock - محاكاة API الري
// ═══════════════════════════════════════════════════════════════════════════

/// Mock IrrigationApi for testing controllers and repositories
class MockIrrigationApi extends Mock implements IrrigationApi {
  bool _shouldFail = false;
  int _failureStatusCode = 500;
  String _failureMessage = 'Server error';

  /// Configure mock to return error responses
  void setFailureMode(bool fail, {int statusCode = 500, String message = 'Server error'}) {
    _shouldFail = fail;
    _failureStatusCode = statusCode;
    _failureMessage = message;
  }

  /// Setup default mock behaviors
  void setupDefaults() {
    // Get crops
    when(() => getCrops()).thenAnswer((_) async {
      if (_shouldFail) {
        throw IrrigationApiException(_failureMessage, statusCode: _failureStatusCode);
      }
      return IrrigationApiFixtures.sampleCrops;
    });

    // Get methods
    when(() => getMethods()).thenAnswer((_) async {
      if (_shouldFail) {
        throw IrrigationApiException(_failureMessage, statusCode: _failureStatusCode);
      }
      return IrrigationApiFixtures.sampleMethods;
    });

    // Calculate irrigation
    when(() => calculate(any())).thenAnswer((_) async {
      if (_shouldFail) {
        throw IrrigationApiException(_failureMessage, statusCode: _failureStatusCode);
      }
      return IrrigationApiFixtures.sampleCalculation;
    });

    // Calculate water balance
    when(() => calculateWaterBalance(
      fieldId: any(named: 'fieldId'),
      from: any(named: 'from'),
      to: any(named: 'to'),
    )).thenAnswer((_) async {
      if (_shouldFail) {
        throw IrrigationApiException(_failureMessage, statusCode: _failureStatusCode);
      }
      return IrrigationApiFixtures.sampleWaterBalance;
    });

    // Calculate efficiency
    when(() => calculateEfficiency(
      methodId: any(named: 'methodId'),
      appliedWaterMm: any(named: 'appliedWaterMm'),
      consumedWaterMm: any(named: 'consumedWaterMm'),
    )).thenAnswer((_) async {
      if (_shouldFail) {
        throw IrrigationApiException(_failureMessage, statusCode: _failureStatusCode);
      }
      return IrrigationApiFixtures.sampleEfficiency;
    });

    // Get schedule
    when(() => getSchedule(any())).thenAnswer((_) async {
      if (_shouldFail) {
        throw IrrigationApiException(_failureMessage, statusCode: _failureStatusCode);
      }
      return IrrigationApiFixtures.sampleSchedule;
    });

    // Generate schedule
    when(() => generateSchedule(
      fieldId: any(named: 'fieldId'),
      cropId: any(named: 'cropId'),
      methodId: any(named: 'methodId'),
      days: any(named: 'days'),
    )).thenAnswer((_) async {
      if (_shouldFail) {
        throw IrrigationApiException(_failureMessage, statusCode: _failureStatusCode);
      }
      return IrrigationApiFixtures.sampleSchedule;
    });

    // Record sensor reading
    when(() => recordSensorReading(
      fieldId: any(named: 'fieldId'),
      sensorType: any(named: 'sensorType'),
      value: any(named: 'value'),
      unit: any(named: 'unit'),
    )).thenAnswer((_) async {
      if (_shouldFail) {
        throw IrrigationApiException(_failureMessage, statusCode: _failureStatusCode);
      }
    });

    // Dispose
    when(() => dispose()).thenReturn(null);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Pivot Controller Mock - محاكاة متحكم المحوري
// ═══════════════════════════════════════════════════════════════════════════

/// Abstract interface for pivot controller to enable mocking
abstract class IPivotController {
  Future<PivotConfiguration?> getPivotConfiguration(String pivotId);
  Future<PivotStatus> getPivotStatus(String pivotId);
  Future<List<PivotSector>> getSectors(String pivotId);
  Future<void> updateSector(String pivotId, PivotSector sector);
  Future<void> sendCommand(PivotControlCommand command);
  Future<List<PivotSchedule>> getSchedules(String pivotId);
  Future<void> createSchedule(PivotSchedule schedule);
  Future<void> updateSchedule(PivotSchedule schedule);
  Future<void> deleteSchedule(String scheduleId);
  Future<List<PivotRunHistory>> getRunHistory(String pivotId, {int limit = 10});
  Future<PivotStatistics> getStatistics(String pivotId, String period);
  Stream<PivotStatus> watchPivotStatus(String pivotId);
  Future<void> startIrrigation(String pivotId, {
    required double speedPercent,
    required PivotDirection direction,
    double? timerHours,
    double? startAngle,
    double? endAngle,
  });
  Future<void> stopIrrigation(String pivotId);
  Future<void> emergencyStop(String pivotId);
}

/// Mock implementation of pivot controller
class MockPivotController extends Mock implements IPivotController {
  bool _shouldFail = false;
  String _failureMessage = 'Pivot controller error';

  /// Configure mock to simulate failures
  void setFailureMode(bool fail, {String message = 'Pivot controller error'}) {
    _shouldFail = fail;
    _failureMessage = message;
  }

  /// Setup default mock behaviors
  void setupDefaults() {
    when(() => getPivotConfiguration(any())).thenAnswer((_) async {
      if (_shouldFail) throw Exception(_failureMessage);
      return PivotFixtures.sampleFullCirclePivot;
    });

    when(() => getPivotStatus(any())).thenAnswer((_) async {
      if (_shouldFail) throw Exception(_failureMessage);
      return PivotFixtures.runningStatus;
    });

    when(() => getSectors(any())).thenAnswer((_) async {
      if (_shouldFail) throw Exception(_failureMessage);
      return PivotFixtures.sampleSectors;
    });

    when(() => updateSector(any(), any())).thenAnswer((_) async {
      if (_shouldFail) throw Exception(_failureMessage);
    });

    when(() => sendCommand(any())).thenAnswer((_) async {
      if (_shouldFail) throw Exception(_failureMessage);
    });

    when(() => getSchedules(any())).thenAnswer((_) async {
      if (_shouldFail) throw Exception(_failureMessage);
      return [PivotFixtures.dailySchedule, PivotFixtures.weeklySchedule];
    });

    when(() => createSchedule(any())).thenAnswer((_) async {
      if (_shouldFail) throw Exception(_failureMessage);
    });

    when(() => updateSchedule(any())).thenAnswer((_) async {
      if (_shouldFail) throw Exception(_failureMessage);
    });

    when(() => deleteSchedule(any())).thenAnswer((_) async {
      if (_shouldFail) throw Exception(_failureMessage);
    });

    when(() => getRunHistory(any(), limit: any(named: 'limit'))).thenAnswer((_) async {
      if (_shouldFail) throw Exception(_failureMessage);
      return [PivotFixtures.completedRun, PivotFixtures.faultedRun];
    });

    when(() => getStatistics(any(), any())).thenAnswer((invocation) async {
      if (_shouldFail) throw Exception(_failureMessage);
      final period = invocation.positionalArguments[1] as String;
      return period == 'weekly' ? PivotFixtures.weeklyStats : PivotFixtures.monthlyStats;
    });

    when(() => watchPivotStatus(any())).thenAnswer((_) {
      if (_shouldFail) {
        return Stream.error(Exception(_failureMessage));
      }
      return Stream.fromIterable([
        PivotFixtures.stoppedStatus,
        PivotFixtures.runningStatus,
      ]);
    });

    when(() => startIrrigation(
      any(),
      speedPercent: any(named: 'speedPercent'),
      direction: any(named: 'direction'),
      timerHours: any(named: 'timerHours'),
      startAngle: any(named: 'startAngle'),
      endAngle: any(named: 'endAngle'),
    )).thenAnswer((_) async {
      if (_shouldFail) throw Exception(_failureMessage);
    });

    when(() => stopIrrigation(any())).thenAnswer((_) async {
      if (_shouldFail) throw Exception(_failureMessage);
    });

    when(() => emergencyStop(any())).thenAnswer((_) async {
      if (_shouldFail) throw Exception(_failureMessage);
    });
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Irrigation Scheduler Mock - محاكاة مجدول الري
// ═══════════════════════════════════════════════════════════════════════════

/// Abstract interface for irrigation scheduler
abstract class IIrrigationScheduler {
  Future<IrrigationSchedule> createSchedule({
    required String fieldId,
    required String cropId,
    required String methodId,
    required int days,
    double? targetDepthMm,
  });
  Future<IrrigationSchedule> getSchedule(String fieldId);
  Future<void> updateEvent(String fieldId, IrrigationEvent event);
  Future<void> deleteEvent(String fieldId, String eventId);
  Future<void> skipEvent(String fieldId, String eventId, String reason);
  Future<void> rescheduleEvent(String fieldId, String eventId, DateTime newTime);
  Future<List<IrrigationEvent>> getUpcomingEvents(String fieldId, {int days = 7});
  Future<List<IrrigationEvent>> getPastEvents(String fieldId, {int days = 30});
}

/// Mock implementation of irrigation scheduler
class MockIrrigationScheduler extends Mock implements IIrrigationScheduler {
  bool _shouldFail = false;

  void setFailureMode(bool fail) {
    _shouldFail = fail;
  }

  void setupDefaults() {
    when(() => createSchedule(
      fieldId: any(named: 'fieldId'),
      cropId: any(named: 'cropId'),
      methodId: any(named: 'methodId'),
      days: any(named: 'days'),
      targetDepthMm: any(named: 'targetDepthMm'),
    )).thenAnswer((_) async {
      if (_shouldFail) throw Exception('Failed to create schedule');
      return IrrigationApiFixtures.sampleSchedule;
    });

    when(() => getSchedule(any())).thenAnswer((_) async {
      if (_shouldFail) throw Exception('Failed to get schedule');
      return IrrigationApiFixtures.sampleSchedule;
    });

    when(() => updateEvent(any(), any())).thenAnswer((_) async {
      if (_shouldFail) throw Exception('Failed to update event');
    });

    when(() => deleteEvent(any(), any())).thenAnswer((_) async {
      if (_shouldFail) throw Exception('Failed to delete event');
    });

    when(() => skipEvent(any(), any(), any())).thenAnswer((_) async {
      if (_shouldFail) throw Exception('Failed to skip event');
    });

    when(() => rescheduleEvent(any(), any(), any())).thenAnswer((_) async {
      if (_shouldFail) throw Exception('Failed to reschedule event');
    });

    when(() => getUpcomingEvents(any(), days: any(named: 'days'))).thenAnswer((_) async {
      if (_shouldFail) throw Exception('Failed to get upcoming events');
      return IrrigationApiFixtures.sampleEvents;
    });

    when(() => getPastEvents(any(), days: any(named: 'days'))).thenAnswer((_) async {
      if (_shouldFail) throw Exception('Failed to get past events');
      return [];
    });
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Water Calculator Mock - محاكاة حاسبة المياه
// ═══════════════════════════════════════════════════════════════════════════

/// Abstract interface for water calculator
abstract class IWaterCalculator {
  double calculateETc(double et0, double kc);
  double calculateWaterNeedMm(double etc, double efficiency, {double? soilMoistureDeficit});
  double convertMmToLiters(double mm, double areaHectares);
  double convertLitersToM3(double liters);
  double calculateIrrigationDuration(double waterLiters, double flowRateLph);
  double calculatePivotWaterVolume({
    required double radiusMeters,
    required double depthMm,
    double? startAngle,
    double? endAngle,
  });
  double calculateSectorArea(double radiusMeters, double startAngle, double endAngle);
  double calculateEfficiency(double appliedMm, double consumedMm);
  WaterBalance calculateWaterBalance({
    required double soilMoisture,
    required double fieldCapacity,
    required double wiltingPoint,
    required double madFraction,
    required double rootDepthMm,
  });
  DateTime calculateNextIrrigationDate({
    required double currentSoilMoisture,
    required double fieldCapacity,
    required double dailyETc,
    required double madFraction,
  });
}

/// Mock implementation of water calculator
class MockWaterCalculator extends Mock implements IWaterCalculator {
  void setupDefaults() {
    when(() => calculateETc(any(), any())).thenAnswer((invocation) {
      final et0 = invocation.positionalArguments[0] as double;
      final kc = invocation.positionalArguments[1] as double;
      return et0 * kc;
    });

    when(() => calculateWaterNeedMm(any(), any(), soilMoistureDeficit: any(named: 'soilMoistureDeficit')))
        .thenAnswer((invocation) {
      final etc = invocation.positionalArguments[0] as double;
      final efficiency = invocation.positionalArguments[1] as double;
      return etc / efficiency;
    });

    when(() => convertMmToLiters(any(), any())).thenAnswer((invocation) {
      final mm = invocation.positionalArguments[0] as double;
      final areaHa = invocation.positionalArguments[1] as double;
      return mm * areaHa * 10000; // 1mm on 1ha = 10,000 liters
    });

    when(() => convertLitersToM3(any())).thenAnswer((invocation) {
      final liters = invocation.positionalArguments[0] as double;
      return liters / 1000;
    });

    when(() => calculateIrrigationDuration(any(), any())).thenAnswer((invocation) {
      final waterLiters = invocation.positionalArguments[0] as double;
      final flowRate = invocation.positionalArguments[1] as double;
      return (waterLiters / flowRate) * 60; // Convert hours to minutes
    });

    when(() => calculatePivotWaterVolume(
      radiusMeters: any(named: 'radiusMeters'),
      depthMm: any(named: 'depthMm'),
      startAngle: any(named: 'startAngle'),
      endAngle: any(named: 'endAngle'),
    )).thenAnswer((invocation) {
      final radius = invocation.namedArguments[#radiusMeters] as double;
      final depth = invocation.namedArguments[#depthMm] as double;
      final startAngle = invocation.namedArguments[#startAngle] as double? ?? 0;
      final endAngle = invocation.namedArguments[#endAngle] as double? ?? 360;
      final angleFraction = (endAngle - startAngle) / 360;
      final areaM2 = 3.14159 * radius * radius * angleFraction;
      return areaM2 * (depth / 1000) * 1000; // Convert to liters
    });

    when(() => calculateSectorArea(any(), any(), any())).thenAnswer((invocation) {
      final radius = invocation.positionalArguments[0] as double;
      final startAngle = invocation.positionalArguments[1] as double;
      final endAngle = invocation.positionalArguments[2] as double;
      final angleFraction = (endAngle - startAngle) / 360;
      return 3.14159 * radius * radius * angleFraction / 10000; // Convert to hectares
    });

    when(() => calculateEfficiency(any(), any())).thenAnswer((invocation) {
      final applied = invocation.positionalArguments[0] as double;
      final consumed = invocation.positionalArguments[1] as double;
      return (consumed / applied) * 100;
    });

    when(() => calculateWaterBalance(
      soilMoisture: any(named: 'soilMoisture'),
      fieldCapacity: any(named: 'fieldCapacity'),
      wiltingPoint: any(named: 'wiltingPoint'),
      madFraction: any(named: 'madFraction'),
      rootDepthMm: any(named: 'rootDepthMm'),
    )).thenReturn(IrrigationModelFixtures.optimalWaterBalance);

    when(() => calculateNextIrrigationDate(
      currentSoilMoisture: any(named: 'currentSoilMoisture'),
      fieldCapacity: any(named: 'fieldCapacity'),
      dailyETc: any(named: 'dailyETc'),
      madFraction: any(named: 'madFraction'),
    )).thenReturn(DateTime.now().add(const Duration(days: 3)));
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Sensor Service Mock - محاكاة خدمة المستشعرات
// ═══════════════════════════════════════════════════════════════════════════

/// Abstract interface for sensor service
abstract class ISensorService {
  Future<List<SensorReading>> getReadings(String fieldId, {String? sensorType});
  Future<SensorReading?> getLatestReading(String fieldId, String sensorType);
  Future<double?> getCurrentSoilMoisture(String fieldId);
  Future<Map<String, double>> getSoilMoistureByZone(String fieldId);
  Future<void> recordReading(SensorReading reading);
  Stream<SensorReading> watchSensorReadings(String fieldId);
}

/// Mock implementation of sensor service
class MockSensorService extends Mock implements ISensorService {
  void setupDefaults() {
    when(() => getReadings(any(), sensorType: any(named: 'sensorType')))
        .thenAnswer((_) async => IrrigationModelFixtures.sampleReadings);

    when(() => getLatestReading(any(), any()))
        .thenAnswer((invocation) async {
      final sensorType = invocation.positionalArguments[1] as String;
      return IrrigationModelFixtures.sampleReadings
          .where((r) => r.sensorType == sensorType)
          .firstOrNull;
    });

    when(() => getCurrentSoilMoisture(any()))
        .thenAnswer((_) async => 38.5);

    when(() => getSoilMoistureByZone(any()))
        .thenAnswer((_) async => {
          'zone_1': 38.5,
          'zone_2': 35.0,
          'zone_3': 42.0,
          'zone_4': 28.0,
        });

    when(() => recordReading(any())).thenAnswer((_) async {});

    when(() => watchSensorReadings(any())).thenAnswer((_) {
      return Stream.fromIterable(IrrigationModelFixtures.sampleReadings);
    });
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// VRI Zone Manager Mock - محاكاة مدير مناطق VRI
// ═══════════════════════════════════════════════════════════════════════════

/// Abstract interface for VRI zone manager
abstract class IVRIZoneManager {
  Future<VRIZoneGrid> getZoneGrid(String pivotId);
  Future<void> updateZoneGrid(String pivotId, VRIZoneGrid grid);
  Future<VRIZoneGrid> createUniformGrid(String pivotId, int spans, int divisions);
  Future<VRIZoneGrid> createGridFromNDVI(String pivotId, Map<String, double> ndviValues);
  Future<void> updateZoneRate(String pivotId, String zoneId, double rate);
  Future<void> enableZone(String pivotId, String zoneId);
  Future<void> disableZone(String pivotId, String zoneId);
  Future<PrescriptionMap> createPrescription(String pivotId, PrescriptionType type);
  Future<VRIZoneStatistics> getZoneStatistics(String pivotId);
}

/// Mock implementation of VRI zone manager
class MockVRIZoneManager extends Mock implements IVRIZoneManager {
  void setupDefaults() {
    when(() => getZoneGrid(any()))
        .thenAnswer((_) async => SpanZoneFixtures.uniformGrid);

    when(() => updateZoneGrid(any(), any())).thenAnswer((_) async {});

    when(() => createUniformGrid(any(), any(), any()))
        .thenAnswer((invocation) async {
      final pivotId = invocation.positionalArguments[0] as String;
      final spans = invocation.positionalArguments[1] as int;
      final divisions = invocation.positionalArguments[2] as int;
      return VRIZoneGridBuilder.createUniformGrid(
        pivotId: pivotId,
        spanCount: spans,
        angularDivisions: divisions,
      );
    });

    when(() => createGridFromNDVI(any(), any()))
        .thenAnswer((_) async => SpanZoneFixtures.variableGrid);

    when(() => updateZoneRate(any(), any(), any())).thenAnswer((_) async {});

    when(() => enableZone(any(), any())).thenAnswer((_) async {});

    when(() => disableZone(any(), any())).thenAnswer((_) async {});

    when(() => createPrescription(any(), any()))
        .thenAnswer((_) async => SpanZoneFixtures.irrigationPrescription);

    when(() => getZoneStatistics(any()))
        .thenAnswer((_) async => VRIZoneStatistics.fromGrid(SpanZoneFixtures.uniformGrid));
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// HTTP Response Helpers - مساعدات استجابة HTTP
// ═══════════════════════════════════════════════════════════════════════════

/// Helper class for creating mock HTTP responses
class MockHttpResponses {
  static http.Response success(dynamic data) {
    return http.Response(
      jsonEncode({'success': true, 'data': data}),
      200,
      headers: {'content-type': 'application/json'},
    );
  }

  static http.Response error(String message, {int statusCode = 400}) {
    return http.Response(
      jsonEncode({'success': false, 'message': message}),
      statusCode,
      headers: {'content-type': 'application/json'},
    );
  }

  static http.Response serverError() {
    return http.Response(
      'Internal Server Error',
      500,
      headers: {'content-type': 'text/plain'},
    );
  }

  static http.Response unauthorized() {
    return http.Response(
      jsonEncode({'message': 'Unauthorized'}),
      401,
      headers: {'content-type': 'application/json'},
    );
  }

  static http.Response notFound() {
    return http.Response(
      jsonEncode({'message': 'Not found'}),
      404,
      headers: {'content-type': 'application/json'},
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Fallback Value Registration - تسجيل القيم الاحتياطية
// ═══════════════════════════════════════════════════════════════════════════

/// Register fallback values for mocktail
void registerIrrigationFallbackValues() {
  registerFallbackValue(DateTime.now());
  registerFallbackValue(<String, dynamic>{});
  registerFallbackValue(IrrigationApiFixtures.sampleCalculationRequest);
  registerFallbackValue(IrrigationApiFixtures.sampleEvents.first);
  registerFallbackValue(IrrigationApiFixtures.sampleSchedule);
  registerFallbackValue(PivotFixtures.sampleFullCirclePivot);
  registerFallbackValue(PivotFixtures.sampleSectors.first);
  registerFallbackValue(PivotFixtures.startCommand);
  registerFallbackValue(PivotFixtures.dailySchedule);
  registerFallbackValue(PivotDirection.forward);
  registerFallbackValue(SpanZoneFixtures.uniformGrid);
  registerFallbackValue(IrrigationModelFixtures.soilMoistureReading);
  registerFallbackValue(PrescriptionType.irrigation);
  registerFallbackValue(Uri.parse('https://api.sahool.app'));
}
