import '../../../../core/http/api_client.dart';
import '../../domain/entities/ecological_entities.dart';

/// عميل API للسجلات الإيكولوجية
/// API client for ecological records
///
/// يتواصل مع واجهة برمجة التطبيقات الخلفية لإدارة البيانات الإيكولوجية
/// Communicates with the backend API to manage ecological data
class EcologicalApi {
  final ApiClient _client;

  EcologicalApi(this._client);

  // ═══════════════════════════════════════════════════════════════════════════
  // Biodiversity Records | سجلات التنوع البيولوجي
  // ═══════════════════════════════════════════════════════════════════════════

  /// جلب سجلات التنوع البيولوجي
  /// Fetch biodiversity records
  Future<List<BiodiversityRecord>> getBiodiversityRecords({
    String? farmId,
  }) async {
    final queryParams = <String, dynamic>{
      'tenant_id': _client.tenantId,
    };

    if (farmId != null) {
      queryParams['farm_id'] = farmId;
    }

    final response = await _client.get(
      '/ecological/biodiversity',
      queryParameters: queryParams,
    );

    if (response is List) {
      return response
          .cast<Map<String, dynamic>>()
          .map((json) => BiodiversityRecord.fromJson(json))
          .toList();
    }

    return [];
  }

  /// إنشاء سجل تنوع بيولوجي جديد
  /// Create a new biodiversity record
  Future<BiodiversityRecord?> createBiodiversityRecord(
    BiodiversityRecord record,
  ) async {
    try {
      final response = await _client.post(
        '/ecological/biodiversity',
        record.toJson(),
      );

      if (response is Map<String, dynamic>) {
        return BiodiversityRecord.fromJson(response);
      }
    } catch (e) {
      print('❌ Failed to create biodiversity record: $e');
    }

    return null;
  }

  /// تحديث سجل تنوع بيولوجي
  /// Update biodiversity record
  Future<BiodiversityRecord?> updateBiodiversityRecord(
    BiodiversityRecord record,
  ) async {
    try {
      final response = await _client.put(
        '/ecological/biodiversity/${record.id}',
        record.toJson(),
      );

      if (response is Map<String, dynamic>) {
        return BiodiversityRecord.fromJson(response);
      }
    } catch (e) {
      print('❌ Failed to update biodiversity record: $e');
    }

    return null;
  }

  /// حذف سجل تنوع بيولوجي
  /// Delete biodiversity record
  Future<bool> deleteBiodiversityRecord(String recordId) async {
    try {
      await _client.delete('/ecological/biodiversity/$recordId');
      return true;
    } catch (e) {
      print('❌ Failed to delete biodiversity record: $e');
      return false;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Soil Health Records | سجلات صحة التربة
  // ═══════════════════════════════════════════════════════════════════════════

  /// جلب سجلات صحة التربة
  /// Fetch soil health records
  Future<List<SoilHealthRecord>> getSoilHealthRecords({
    String? fieldId,
  }) async {
    final queryParams = <String, dynamic>{
      'tenant_id': _client.tenantId,
    };

    if (fieldId != null) {
      queryParams['field_id'] = fieldId;
    }

    final response = await _client.get(
      '/ecological/soil-health',
      queryParameters: queryParams,
    );

    if (response is List) {
      return response
          .cast<Map<String, dynamic>>()
          .map((json) => SoilHealthRecord.fromJson(json))
          .toList();
    }

    return [];
  }

  /// إنشاء سجل صحة تربة جديد
  /// Create a new soil health record
  Future<SoilHealthRecord?> createSoilHealthRecord(
    SoilHealthRecord record,
  ) async {
    try {
      final response = await _client.post(
        '/ecological/soil-health',
        record.toJson(),
      );

      if (response is Map<String, dynamic>) {
        return SoilHealthRecord.fromJson(response);
      }
    } catch (e) {
      print('❌ Failed to create soil health record: $e');
    }

    return null;
  }

  /// تحديث سجل صحة التربة
  /// Update soil health record
  Future<SoilHealthRecord?> updateSoilHealthRecord(
    SoilHealthRecord record,
  ) async {
    try {
      final response = await _client.put(
        '/ecological/soil-health/${record.id}',
        record.toJson(),
      );

      if (response is Map<String, dynamic>) {
        return SoilHealthRecord.fromJson(response);
      }
    } catch (e) {
      print('❌ Failed to update soil health record: $e');
    }

    return null;
  }

  /// حذف سجل صحة التربة
  /// Delete soil health record
  Future<bool> deleteSoilHealthRecord(String recordId) async {
    try {
      await _client.delete('/ecological/soil-health/$recordId');
      return true;
    } catch (e) {
      print('❌ Failed to delete soil health record: $e');
      return false;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Water Conservation Records | سجلات الحفاظ على المياه
  // ═══════════════════════════════════════════════════════════════════════════

  /// جلب سجلات الحفاظ على المياه
  /// Fetch water conservation records
  Future<List<WaterConservationRecord>> getWaterConservationRecords({
    String? farmId,
    String? fieldId,
  }) async {
    final queryParams = <String, dynamic>{
      'tenant_id': _client.tenantId,
    };

    if (farmId != null) {
      queryParams['farm_id'] = farmId;
    }

    if (fieldId != null) {
      queryParams['field_id'] = fieldId;
    }

    final response = await _client.get(
      '/ecological/water-conservation',
      queryParameters: queryParams,
    );

    if (response is List) {
      return response
          .cast<Map<String, dynamic>>()
          .map((json) => WaterConservationRecord.fromJson(json))
          .toList();
    }

    return [];
  }

  /// إنشاء سجل حفاظ على المياه جديد
  /// Create a new water conservation record
  Future<WaterConservationRecord?> createWaterConservationRecord(
    WaterConservationRecord record,
  ) async {
    try {
      final response = await _client.post(
        '/ecological/water-conservation',
        record.toJson(),
      );

      if (response is Map<String, dynamic>) {
        return WaterConservationRecord.fromJson(response);
      }
    } catch (e) {
      print('❌ Failed to create water conservation record: $e');
    }

    return null;
  }

  /// تحديث سجل الحفاظ على المياه
  /// Update water conservation record
  Future<WaterConservationRecord?> updateWaterConservationRecord(
    WaterConservationRecord record,
  ) async {
    try {
      final response = await _client.put(
        '/ecological/water-conservation/${record.id}',
        record.toJson(),
      );

      if (response is Map<String, dynamic>) {
        return WaterConservationRecord.fromJson(response);
      }
    } catch (e) {
      print('❌ Failed to update water conservation record: $e');
    }

    return null;
  }

  /// حذف سجل الحفاظ على المياه
  /// Delete water conservation record
  Future<bool> deleteWaterConservationRecord(String recordId) async {
    try {
      await _client.delete('/ecological/water-conservation/$recordId');
      return true;
    } catch (e) {
      print('❌ Failed to delete water conservation record: $e');
      return false;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Farm Practice Records | سجلات الممارسات الزراعية
  // ═══════════════════════════════════════════════════════════════════════════

  /// جلب سجلات الممارسات
  /// Fetch practice records
  Future<List<FarmPracticeRecord>> getPracticeRecords({
    String? farmId,
    String? fieldId,
    PracticeStatus? status,
  }) async {
    final queryParams = <String, dynamic>{
      'tenant_id': _client.tenantId,
    };

    if (farmId != null) {
      queryParams['farm_id'] = farmId;
    }

    if (fieldId != null) {
      queryParams['field_id'] = fieldId;
    }

    if (status != null) {
      queryParams['status'] = status.value;
    }

    final response = await _client.get(
      '/ecological/practices',
      queryParameters: queryParams,
    );

    if (response is List) {
      return response
          .cast<Map<String, dynamic>>()
          .map((json) => FarmPracticeRecord.fromJson(json))
          .toList();
    }

    return [];
  }

  /// إنشاء سجل ممارسة جديد
  /// Create a new practice record
  Future<FarmPracticeRecord?> createPracticeRecord(
    FarmPracticeRecord record,
  ) async {
    try {
      final response = await _client.post(
        '/ecological/practices',
        record.toJson(),
      );

      if (response is Map<String, dynamic>) {
        return FarmPracticeRecord.fromJson(response);
      }
    } catch (e) {
      print('❌ Failed to create practice record: $e');
    }

    return null;
  }

  /// تحديث سجل الممارسة
  /// Update practice record
  Future<FarmPracticeRecord?> updatePracticeRecord(
    FarmPracticeRecord record,
  ) async {
    try {
      final response = await _client.put(
        '/ecological/practices/${record.id}',
        record.toJson(),
      );

      if (response is Map<String, dynamic>) {
        return FarmPracticeRecord.fromJson(response);
      }
    } catch (e) {
      print('❌ Failed to update practice record: $e');
    }

    return null;
  }

  /// تحديث حالة الممارسة
  /// Update practice status
  Future<bool> updatePracticeStatus({
    required String practiceId,
    required PracticeStatus status,
  }) async {
    try {
      await _client.put(
        '/ecological/practices/$practiceId/status',
        {'status': status.value},
      );
      return true;
    } catch (e) {
      print('❌ Failed to update practice status: $e');
      return false;
    }
  }

  /// حذف سجل الممارسة
  /// Delete practice record
  Future<bool> deletePracticeRecord(String recordId) async {
    try {
      await _client.delete('/ecological/practices/$recordId');
      return true;
    } catch (e) {
      print('❌ Failed to delete practice record: $e');
      return false;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Dashboard | لوحة التحكم
  // ═══════════════════════════════════════════════════════════════════════════

  /// جلب بيانات لوحة المعلومات الإيكولوجية
  /// Fetch ecological dashboard data
  Future<EcologicalDashboardData?> getDashboardData({
    required String farmId,
    String? fieldId,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'tenant_id': _client.tenantId,
        'farm_id': farmId,
      };

      if (fieldId != null) {
        queryParams['field_id'] = fieldId;
      }

      final response = await _client.get(
        '/ecological/dashboard',
        queryParameters: queryParams,
      );

      if (response is Map<String, dynamic>) {
        return EcologicalDashboardData.fromJson(response);
      }
    } catch (e) {
      print('❌ Failed to fetch dashboard data: $e');
    }

    return null;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // AI Advisor Integration | تكامل المستشار الذكي
  // ═══════════════════════════════════════════════════════════════════════════

  /// الحصول على تقييم إيكولوجي من المستشار الذكي
  /// Get ecological assessment from AI advisor
  Future<Map<String, dynamic>?> getEcologicalAssessment({
    required String farmId,
    required Map<String, dynamic> farmData,
    required Map<String, dynamic> currentPractices,
  }) async {
    try {
      final response = await _client.post(
        '/advisor/ecological/assess',
        {
          'farm_id': farmId,
          'farm_data': farmData,
          'current_practices': currentPractices,
        },
      );

      if (response is Map<String, dynamic>) {
        return response;
      }
    } catch (e) {
      print('❌ Failed to get ecological assessment: $e');
    }

    return null;
  }

  /// الحصول على توصيات ممارسات من المستشار الذكي
  /// Get practice recommendations from AI advisor
  Future<Map<String, dynamic>?> getPracticeRecommendations({
    required String cropType,
    required String soilType,
    required String climate,
    required List<String> goals,
  }) async {
    try {
      final response = await _client.post(
        '/advisor/ecological/practices',
        {
          'crop_type': cropType,
          'soil_type': soilType,
          'climate': climate,
          'goals': goals,
        },
      );

      if (response is Map<String, dynamic>) {
        return response;
      }
    } catch (e) {
      print('❌ Failed to get practice recommendations: $e');
    }

    return null;
  }

  /// تشخيص المزالق الزراعية
  /// Diagnose agricultural pitfalls
  Future<Map<String, dynamic>?> diagnosePitfalls({
    required String farmId,
    required List<String> observedSymptoms,
  }) async {
    try {
      final response = await _client.post(
        '/advisor/ecological/diagnose-pitfalls',
        {
          'farm_id': farmId,
          'observed_symptoms': observedSymptoms,
        },
      );

      if (response is Map<String, dynamic>) {
        return response;
      }
    } catch (e) {
      print('❌ Failed to diagnose pitfalls: $e');
    }

    return null;
  }

  /// الحصول على خطة زراعة تصاحبية
  /// Get companion planting plan
  Future<Map<String, dynamic>?> getCompanionPlantingPlan({
    required String fieldId,
    required String primaryCrop,
    required double fieldSizeHectares,
  }) async {
    try {
      final response = await _client.post(
        '/advisor/ecological/companion-planting',
        {
          'field_id': fieldId,
          'primary_crop': primaryCrop,
          'field_size_hectares': fieldSizeHectares,
        },
      );

      if (response is Map<String, dynamic>) {
        return response;
      }
    } catch (e) {
      print('❌ Failed to get companion planting plan: $e');
    }

    return null;
  }

  /// الحصول على استراتيجية استعادة التربة
  /// Get soil restoration strategy
  Future<Map<String, dynamic>?> getSoilRestorationStrategy({
    required String fieldId,
    required Map<String, dynamic> soilAnalysis,
  }) async {
    try {
      final response = await _client.post(
        '/advisor/ecological/soil-restoration',
        {
          'field_id': fieldId,
          'soil_analysis': soilAnalysis,
        },
      );

      if (response is Map<String, dynamic>) {
        return response;
      }
    } catch (e) {
      print('❌ Failed to get soil restoration strategy: $e');
    }

    return null;
  }

  /// الحصول على استراتيجية الحفاظ على المياه
  /// Get water conservation strategy
  Future<Map<String, dynamic>?> getWaterConservationStrategy({
    required String farmId,
    required double currentWaterUsage,
    required String irrigationMethod,
  }) async {
    try {
      final response = await _client.post(
        '/advisor/ecological/water-conservation',
        {
          'farm_id': farmId,
          'current_water_usage': currentWaterUsage,
          'irrigation_method': irrigationMethod,
        },
      );

      if (response is Map<String, dynamic>) {
        return response;
      }
    } catch (e) {
      print('❌ Failed to get water conservation strategy: $e');
    }

    return null;
  }

  /// التحقق من امتثال GlobalGAP
  /// Check GlobalGAP compliance alignment
  Future<Map<String, dynamic>?> checkGlobalGapAlignment({
    required String farmId,
    required List<String> implementedPractices,
  }) async {
    try {
      final response = await _client.post(
        '/advisor/ecological/globalgap-alignment',
        {
          'farm_id': farmId,
          'implemented_practices': implementedPractices,
        },
      );

      if (response is Map<String, dynamic>) {
        return response;
      }
    } catch (e) {
      print('❌ Failed to check GlobalGAP alignment: $e');
    }

    return null;
  }
}
