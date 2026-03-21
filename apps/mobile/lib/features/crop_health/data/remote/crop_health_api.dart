import '../../../../core/http/api_client.dart';
import '../../domain/entities/crop_health_entities.dart';

/// Crop Health API Client
/// واجهة برمجة تطبيقات صحة المحاصيل
class CropHealthApi {
  final ApiClient _client;

  /// Base URL for crop health service (via Kong API Gateway)
  /// Note: apiBaseUrl already includes /api/v1, so we only add /crop-health
  static const String _baseUrl = '/crop-health';

  CropHealthApi(this._client);

  // ═══════════════════════════════════════════════════════════════
  // Zones
  // ═══════════════════════════════════════════════════════════════

  /// قائمة المناطق في الحقل
  Future<List<Zone>> getZones(String fieldId) async {
    final response = await _client.get('$_baseUrl/fields/$fieldId/zones');
    final data = response as Map<String, dynamic>;
    final zones = data['zones'] as List;
    return zones.map((z) => Zone.fromJson(z as Map<String, dynamic>)).toList();
  }

  /// إنشاء منطقة جديدة
  Future<String> createZone(
    String fieldId, {
    required String name,
    String? nameAr,
    double? areaHectares,
    Map<String, dynamic>? geometry,
  }) async {
    final response = await _client.post(
      '$_baseUrl/fields/$fieldId/zones',
      {
        'name': name,
        'name_ar': nameAr,
        'area_hectares': areaHectares,
        'geometry': geometry,
      },
    );
    return response['zone_id'] as String;
  }

  /// GeoJSON للمناطق
  Future<Map<String, dynamic>> getZonesGeoJson(String fieldId) async {
    return await _client.get('$_baseUrl/fields/$fieldId/zones.geojson') as Map<String, dynamic>;
  }

  // ═══════════════════════════════════════════════════════════════
  // Observations
  // ═══════════════════════════════════════════════════════════════

  /// تسجيل رصد جديد
  Future<String> ingestObservation(
    String fieldId,
    String zoneId, {
    required DateTime capturedAt,
    required String source,
    required GrowthStage growthStage,
    required VegetationIndices indices,
    double cloudPct = 0.0,
    String? notes,
  }) async {
    final response = await _client.post(
      '$_baseUrl/fields/$fieldId/zones/$zoneId/observations',
      {
        'captured_at': capturedAt.toIso8601String(),
        'source': source,
        'growth_stage': growthStage.value,
        'indices': indices.toJson(),
        'cloud_pct': cloudPct,
        'notes': notes,
      },
    );
    return response['observation_id'] as String;
  }

  /// قائمة الأرصاد للمنطقة
  Future<List<Map<String, dynamic>>> getObservations(
    String fieldId,
    String zoneId, {
    int limit = 50,
  }) async {
    final response = await _client.get(
      '$_baseUrl/fields/$fieldId/zones/$zoneId/observations',
      queryParameters: {'limit': limit},
    );
    final data = response as Map<String, dynamic>;
    return List<Map<String, dynamic>>.from(data['observations'] as Iterable);
  }

  // ═══════════════════════════════════════════════════════════════
  // Diagnosis
  // ═══════════════════════════════════════════════════════════════

  /// تشخيص كامل للحقل
  Future<FieldDiagnosis> getDiagnosis(
    String fieldId, {
    required DateTime date,
  }) async {
    final dateStr =
        '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';

    final response = await _client.get(
      '$_baseUrl/fields/$fieldId/diagnosis',
      queryParameters: {'date': dateStr},
    );
    return FieldDiagnosis.fromJson(response as Map<String, dynamic>);
  }

  /// تشخيص سريع (بدون حفظ)
  Future<Map<String, dynamic>> quickDiagnose({
    required DateTime capturedAt,
    required String source,
    required GrowthStage growthStage,
    required VegetationIndices indices,
    String zoneId = 'zone_temp',
  }) async {
    final response = await _client.post(
      '$_baseUrl/diagnose',
      {
        'captured_at': capturedAt.toIso8601String(),
        'source': source,
        'growth_stage': growthStage.value,
        'indices': indices.toJson(),
      },
      queryParameters: {'zone_id': zoneId},
    );
    return response as Map<String, dynamic>;
  }

  // ═══════════════════════════════════════════════════════════════
  // Timeline
  // ═══════════════════════════════════════════════════════════════

  /// السلسلة الزمنية للمنطقة
  Future<ZoneTimeline> getTimeline(
    String fieldId,
    String zoneId, {
    required DateTime from,
    required DateTime to,
  }) async {
    final fromStr =
        '${from.year}-${from.month.toString().padLeft(2, '0')}-${from.day.toString().padLeft(2, '0')}';
    final toStr =
        '${to.year}-${to.month.toString().padLeft(2, '0')}-${to.day.toString().padLeft(2, '0')}';

    final response = await _client.get(
      '$_baseUrl/fields/$fieldId/zones/$zoneId/timeline',
      queryParameters: {
        'from': fromStr,
        'to': toStr,
      },
    );
    return ZoneTimeline.fromJson(response as Map<String, dynamic>);
  }

  // ═══════════════════════════════════════════════════════════════
  // VRT Export
  // ═══════════════════════════════════════════════════════════════

  /// تصدير VRT للعمليات الزراعية
  Future<Map<String, dynamic>> exportVrt(
    String fieldId, {
    required DateTime date,
    String? actionType,
  }) async {
    final dateStr =
        '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';

    final params = <String, dynamic>{'date': dateStr};
    if (actionType != null) {
      params['action_type'] = actionType;
    }

    return await _client.get(
      '$_baseUrl/fields/$fieldId/vrt',
      queryParameters: params,
    ) as Map<String, dynamic>;
  }

  // ═══════════════════════════════════════════════════════════════
  // Actions
  // ═══════════════════════════════════════════════════════════════

  /// تحديد الإجراء كمنفذ
  Future<void> markActionCompleted(
    String fieldId,
    String zoneId,
    String actionType, {
    String? notes,
  }) async {
    await _client.post(
      '$_baseUrl/fields/$fieldId/zones/$zoneId/actions/complete',
      {
        'action_type': actionType,
        'completed_at': DateTime.now().toIso8601String(),
        'notes': notes,
      },
    );
  }
}
