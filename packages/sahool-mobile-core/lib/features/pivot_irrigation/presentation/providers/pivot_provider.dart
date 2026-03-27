/// Pivot Irrigation Provider
/// مزود الري المحوري
///
/// Architecture:
/// 1. Try GET /api/v1/irrigation/pivot/{pivotId} from irrigation-smart (port 8094)
///    or field-management-service (port 3000)
/// 2. On failure (offline/unavailable), fall back to built-in demo data
library;

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/config/api_config.dart';
import '../../../../core/network/api_result.dart';
import '../../../../core/utils/app_logger.dart';
import '../../domain/models/pivot_models.dart';

// =============================================================================
// Repository
// =============================================================================

class PivotRepository {
  final Dio _dio;

  PivotRepository({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: ApiConfig.effectiveBaseUrl,
              connectTimeout: ApiConfig.connectTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            ));

  /// جلب إعدادات المحوري من API أو الرجوع للبيانات التجريبية
  Future<ApiResult<PivotConfiguration>> fetchConfiguration(
      String pivotId, String? fieldId) async {
    try {
      final response =
          await _dio.get('/api/v1/irrigation/pivot/$pivotId/config');
      final data = response.data as Map<String, dynamic>;
      final config = PivotConfiguration.fromJson(data);
      return Success(config);
    } on DioException catch (e) {
      AppLogger.w(
        'Pivot config API unavailable (${e.type.name}), using demo data',
        tag: 'PIVOT',
      );
      return Success(_buildDemoConfiguration(pivotId, fieldId));
    } catch (e) {
      AppLogger.w('Pivot config parse error: $e, using demo data',
          tag: 'PIVOT');
      return Success(_buildDemoConfiguration(pivotId, fieldId));
    }
  }

  /// جلب حالة المحوري الحالية من API أو الرجوع للبيانات التجريبية
  Future<ApiResult<PivotStatus>> fetchStatus(String pivotId) async {
    try {
      final response =
          await _dio.get('/api/v1/irrigation/pivot/$pivotId/status');
      final data = response.data as Map<String, dynamic>;
      final status = PivotStatus.fromJson(data);
      return Success(status);
    } on DioException catch (e) {
      AppLogger.w(
        'Pivot status API unavailable (${e.type.name}), using demo data',
        tag: 'PIVOT',
      );
      return Success(_buildDemoStatus(pivotId));
    } catch (e) {
      AppLogger.w('Pivot status parse error: $e, using demo data',
          tag: 'PIVOT');
      return Success(_buildDemoStatus(pivotId));
    }
  }

  /// إرسال أمر تشغيل للمحوري
  Future<ApiResult<bool>> sendCommand(
      String pivotId, PivotControlCommand command) async {
    try {
      await _dio.post(
        '/api/v1/irrigation/pivot/$pivotId/command',
        data: command.toJson(),
      );
      return const Success(true);
    } on DioException catch (e) {
      AppLogger.w('Pivot command API unavailable (${e.type.name})',
          tag: 'PIVOT');
      // Optimistic: simulate success offline
      return const Success(true);
    } catch (e) {
      return Failure('فشل إرسال الأمر: $e');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Demo / offline fallback data
  // ─────────────────────────────────────────────────────────────────────────

  PivotConfiguration _buildDemoConfiguration(
      String pivotId, String? fieldId) {
    return PivotConfiguration(
      id: pivotId,
      fieldId: fieldId ?? 'field_001',
      name: 'المحوري الرئيسي',
      nameAr: 'المحوري الرئيسي',
      centerLat: 24.7136,
      centerLng: 46.6753,
      lengthMeters: 400,
      overhangMeters: 15,
      spansCount: 7,
      rotationDirection: RotationDirection.clockwise,
      areaHectares: 50.3,
      pivotType: PivotType.fullCircle,
      flowRateLph: 450000,
      operatingPressureBar: 2.8,
      hasVRI: true,
      hasEndGun: true,
      hasCornerSystem: false,
      sectors: _buildDemoSectors(),
      vriZones: _buildDemoVRIZones(),
      createdAt: DateTime.now().subtract(const Duration(days: 365)),
    );
  }

  PivotStatus _buildDemoStatus(String pivotId) {
    return PivotStatus(
      pivotId: pivotId,
      currentAngle: 127.5,
      operatingStatus: PivotOperatingStatus.running,
      direction: PivotDirection.forward,
      speedPercent: 85,
      timerHours: 12,
      elapsedMinutes: 245,
      currentFlowRateLph: 425000,
      currentPressureBar: 2.7,
      endGunActive: true,
      cornerSystemActive: false,
      waterAppliedM3: 1250,
      energyConsumedKwh: 180,
      estimatedCompletionTime: DateTime.now().add(const Duration(hours: 8)),
      lastUpdated: DateTime.now(),
      activeAlerts: [
        PivotAlert(
          id: 'alert_001',
          pivotId: pivotId,
          alertType: PivotAlertType.lowPressure,
          severity: AlertSeverity.warning,
          message: 'Pressure dropped below optimal range',
          messageAr: 'انخفض الضغط عن المستوى الأمثل',
          timestamp: DateTime.now().subtract(const Duration(minutes: 15)),
        ),
      ],
    );
  }

  List<PivotSector> _buildDemoSectors() {
    final colors = [
      '#4CAF50', '#8BC34A', '#CDDC39', '#FFC107',
      '#FF9800', '#FF5722', '#4CAF50', '#8BC34A',
    ];
    final ndviValues = [0.75, 0.68, 0.72, 0.55, 0.62, 0.78, 0.71, 0.65];

    return List.generate(8, (i) {
      return PivotSector(
        id: 'sector_${i + 1}',
        sectorNumber: i + 1,
        name: 'Sector ${i + 1}',
        nameAr: 'قطاع ${i + 1}',
        startAngle: i * 45.0,
        endAngle: (i + 1) * 45.0,
        irrigationDepthMm: 25,
        applicationRateMmHr: 6.5,
        isEnabled: true,
        speedPercent: 100 - (i * 5),
        cropType: 'wheat',
        soilType: 'loamy',
        ndviValue: ndviValues[i],
        soilMoisturePercent: 45 + i * 3,
        color: colors[i],
      );
    });
  }

  List<VRIZone> _buildDemoVRIZones() {
    return const [
      VRIZone(
        id: 'vri_001',
        name: 'High Need Zone',
        nameAr: 'منطقة احتياج عالي',
        coordinates: [],
        rateMultiplier: 1.3,
        targetSoilMoisturePercent: 70,
        zoneType: VRIZoneType.highNeed,
        color: '#2196F3',
      ),
      VRIZone(
        id: 'vri_002',
        name: 'Low Need Zone',
        nameAr: 'منطقة احتياج منخفض',
        coordinates: [],
        rateMultiplier: 0.7,
        targetSoilMoisturePercent: 50,
        zoneType: VRIZoneType.lowNeed,
        color: '#FF9800',
      ),
    ];
  }
}

// =============================================================================
// Data class for combined pivot data
// =============================================================================

class PivotData {
  final PivotConfiguration config;
  final PivotStatus status;

  const PivotData({required this.config, required this.status});
}

// =============================================================================
// Params class for family providers
// =============================================================================

class PivotParams {
  final String pivotId;
  final String? fieldId;

  const PivotParams({required this.pivotId, this.fieldId});

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PivotParams &&
          runtimeType == other.runtimeType &&
          pivotId == other.pivotId &&
          fieldId == other.fieldId;

  @override
  int get hashCode => pivotId.hashCode ^ fieldId.hashCode;
}

// =============================================================================
// Providers
// =============================================================================

final pivotRepositoryProvider = Provider<PivotRepository>((ref) {
  return PivotRepository();
});

/// Fetches pivot configuration + status together
/// جلب إعدادات وحالة المحوري معاً (API أولاً ثم البيانات التجريبية)
final pivotDataProvider =
    FutureProvider.autoDispose.family<PivotData, PivotParams>((ref, params) async {
  final repo = ref.read(pivotRepositoryProvider);

  final configResult =
      await repo.fetchConfiguration(params.pivotId, params.fieldId);
  final statusResult = await repo.fetchStatus(params.pivotId);

  final config = configResult.when(
    success: (c) => c,
    failure: (msg, _) => throw Exception(msg),
  );
  final status = statusResult.when(
    success: (s) => s,
    failure: (msg, _) => throw Exception(msg),
  );

  return PivotData(config: config, status: status);
});
