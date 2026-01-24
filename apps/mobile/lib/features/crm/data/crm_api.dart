/// CRM API Service
/// خدمة API لإدارة علاقات العملاء (المزارعين)
///
/// Handles all CRM-related API calls
library;

import 'package:dio/dio.dart';

import '../../../core/config/api_config.dart';
import '../domain/models/farmer_profile.dart';
import '../domain/models/interaction.dart';
import '../domain/models/opportunity.dart';
import '../domain/models/activity_log.dart';

/// CRM API Service
/// خدمة API لإدارة علاقات المزارعين
class CrmApi {
  final Dio _dio;
  final String _baseUrl;

  CrmApi({Dio? dio, String? baseUrl})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: ApiConfig.effectiveBaseUrl,
              connectTimeout: ApiConfig.connectTimeout,
              sendTimeout: ApiConfig.sendTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            )),
        _baseUrl = baseUrl ?? '${ApiConfig.effectiveBaseUrl}/api/v1/crm';

  // ═══════════════════════════════════════════════════════════════════════════
  // Farmers API
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get all farmers with optional filters
  /// جلب جميع المزارعين مع فلاتر اختيارية
  Future<Response> getFarmers({
    String? search,
    FarmerStatus? status,
    FarmerSegment? segment,
    String? governorate,
    String? assignedAgentId,
    List<String>? tags,
    int limit = 50,
    int offset = 0,
    String? sortBy,
    String sortOrder = 'desc',
  }) async {
    final queryParams = <String, dynamic>{
      'limit': limit,
      'offset': offset,
      if (search != null && search.isNotEmpty) 'search': search,
      if (status != null) 'status': status.name,
      if (segment != null) 'segment': segment.name,
      if (governorate != null) 'governorate': governorate,
      if (assignedAgentId != null) 'assigned_agent_id': assignedAgentId,
      if (tags != null && tags.isNotEmpty) 'tags': tags.join(','),
      if (sortBy != null) 'sort_by': sortBy,
      'sort_order': sortOrder,
    };

    return _dio.get('$_baseUrl/farmers', queryParameters: queryParams);
  }

  /// Get farmer by ID
  /// جلب مزارع بواسطة المعرف
  Future<Response> getFarmerById(String farmerId) async {
    return _dio.get('$_baseUrl/farmers/$farmerId');
  }

  /// Create new farmer
  /// إنشاء مزارع جديد
  Future<Response> createFarmer(Map<String, dynamic> data) async {
    return _dio.post('$_baseUrl/farmers', data: data);
  }

  /// Update farmer
  /// تحديث مزارع
  Future<Response> updateFarmer(String farmerId, Map<String, dynamic> data) async {
    return _dio.put('$_baseUrl/farmers/$farmerId', data: data);
  }

  /// Delete farmer (soft delete)
  /// حذف مزارع
  Future<Response> deleteFarmer(String farmerId) async {
    return _dio.delete('$_baseUrl/farmers/$farmerId');
  }

  /// Search farmers
  /// البحث عن مزارعين
  Future<Response> searchFarmers(String query, {int limit = 20}) async {
    return _dio.get(
      '$_baseUrl/farmers/search',
      queryParameters: {'q': query, 'limit': limit},
    );
  }

  /// Get farmers nearby (by location)
  /// جلب المزارعين القريبين
  Future<Response> getFarmersNearby({
    required double latitude,
    required double longitude,
    double radiusKm = 10,
    int limit = 20,
  }) async {
    return _dio.get(
      '$_baseUrl/farmers/nearby',
      queryParameters: {
        'lat': latitude,
        'lon': longitude,
        'radius_km': radiusKm,
        'limit': limit,
      },
    );
  }

  /// Get farmer statistics
  /// جلب إحصائيات المزارع
  Future<Response> getFarmerStats(String farmerId) async {
    return _dio.get('$_baseUrl/farmers/$farmerId/stats');
  }

  /// Update farmer status
  /// تحديث حالة المزارع
  Future<Response> updateFarmerStatus(String farmerId, FarmerStatus status) async {
    return _dio.patch(
      '$_baseUrl/farmers/$farmerId/status',
      data: {'status': status.name},
    );
  }

  /// Update farmer segment
  /// تحديث شريحة المزارع
  Future<Response> updateFarmerSegment(String farmerId, FarmerSegment segment) async {
    return _dio.patch(
      '$_baseUrl/farmers/$farmerId/segment',
      data: {'segment': segment.name},
    );
  }

  /// Assign farmer to agent
  /// تعيين مزارع لوكيل
  Future<Response> assignFarmerToAgent(String farmerId, String agentId) async {
    return _dio.patch(
      '$_baseUrl/farmers/$farmerId/assign',
      data: {'agent_id': agentId},
    );
  }

  /// Add tags to farmer
  /// إضافة وسوم للمزارع
  Future<Response> addFarmerTags(String farmerId, List<String> tags) async {
    return _dio.post(
      '$_baseUrl/farmers/$farmerId/tags',
      data: {'tags': tags},
    );
  }

  /// Remove tags from farmer
  /// إزالة وسوم من المزارع
  Future<Response> removeFarmerTags(String farmerId, List<String> tags) async {
    return _dio.delete(
      '$_baseUrl/farmers/$farmerId/tags',
      data: {'tags': tags},
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Interactions API
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get interactions for a farmer
  /// جلب التفاعلات لمزارع
  Future<Response> getInteractions({
    String? farmerId,
    InteractionType? type,
    InteractionOutcome? outcome,
    DateTime? startDate,
    DateTime? endDate,
    int limit = 50,
    int offset = 0,
  }) async {
    final queryParams = <String, dynamic>{
      'limit': limit,
      'offset': offset,
      if (farmerId != null) 'farmer_id': farmerId,
      if (type != null) 'type': type.name,
      if (outcome != null) 'outcome': outcome.name,
      if (startDate != null) 'start_date': startDate.toIso8601String(),
      if (endDate != null) 'end_date': endDate.toIso8601String(),
    };

    return _dio.get('$_baseUrl/interactions', queryParameters: queryParams);
  }

  /// Get interaction by ID
  /// جلب تفاعل بواسطة المعرف
  Future<Response> getInteractionById(String interactionId) async {
    return _dio.get('$_baseUrl/interactions/$interactionId');
  }

  /// Create new interaction
  /// إنشاء تفاعل جديد
  Future<Response> createInteraction(Map<String, dynamic> data) async {
    return _dio.post('$_baseUrl/interactions', data: data);
  }

  /// Update interaction
  /// تحديث تفاعل
  Future<Response> updateInteraction(
    String interactionId,
    Map<String, dynamic> data,
  ) async {
    return _dio.put('$_baseUrl/interactions/$interactionId', data: data);
  }

  /// Delete interaction
  /// حذف تفاعل
  Future<Response> deleteInteraction(String interactionId) async {
    return _dio.delete('$_baseUrl/interactions/$interactionId');
  }

  /// Get pending follow-ups
  /// جلب المتابعات المعلقة
  Future<Response> getPendingFollowUps({
    String? agentId,
    bool overdueOnly = false,
    int limit = 50,
  }) async {
    return _dio.get(
      '$_baseUrl/interactions/follow-ups',
      queryParameters: {
        if (agentId != null) 'agent_id': agentId,
        'overdue_only': overdueOnly,
        'limit': limit,
      },
    );
  }

  /// Mark follow-up as complete
  /// إكمال المتابعة
  Future<Response> completeFollowUp(String interactionId, {String? notes}) async {
    return _dio.patch(
      '$_baseUrl/interactions/$interactionId/complete-follow-up',
      data: {'notes': notes},
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Opportunities API
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get opportunities
  /// جلب الفرص
  Future<Response> getOpportunities({
    String? farmerId,
    OpportunityStage? stage,
    OpportunityPriority? priority,
    String? assignedAgentId,
    bool openOnly = false,
    int limit = 50,
    int offset = 0,
  }) async {
    final queryParams = <String, dynamic>{
      'limit': limit,
      'offset': offset,
      if (farmerId != null) 'farmer_id': farmerId,
      if (stage != null) 'stage': stage.name,
      if (priority != null) 'priority': priority.name,
      if (assignedAgentId != null) 'assigned_agent_id': assignedAgentId,
      'open_only': openOnly,
    };

    return _dio.get('$_baseUrl/opportunities', queryParameters: queryParams);
  }

  /// Get opportunity by ID
  /// جلب فرصة بواسطة المعرف
  Future<Response> getOpportunityById(String opportunityId) async {
    return _dio.get('$_baseUrl/opportunities/$opportunityId');
  }

  /// Create new opportunity
  /// إنشاء فرصة جديدة
  Future<Response> createOpportunity(Map<String, dynamic> data) async {
    return _dio.post('$_baseUrl/opportunities', data: data);
  }

  /// Update opportunity
  /// تحديث فرصة
  Future<Response> updateOpportunity(
    String opportunityId,
    Map<String, dynamic> data,
  ) async {
    return _dio.put('$_baseUrl/opportunities/$opportunityId', data: data);
  }

  /// Delete opportunity
  /// حذف فرصة
  Future<Response> deleteOpportunity(String opportunityId) async {
    return _dio.delete('$_baseUrl/opportunities/$opportunityId');
  }

  /// Update opportunity stage
  /// تحديث مرحلة الفرصة
  Future<Response> updateOpportunityStage(
    String opportunityId,
    OpportunityStage stage, {
    String? notes,
  }) async {
    return _dio.patch(
      '$_baseUrl/opportunities/$opportunityId/stage',
      data: {
        'stage': stage.name,
        if (notes != null) 'notes': notes,
      },
    );
  }

  /// Close opportunity as won
  /// إغلاق الفرصة كناجحة
  Future<Response> closeOpportunityWon(
    String opportunityId, {
    required double actualAmount,
    String? notes,
    String? orderId,
  }) async {
    return _dio.patch(
      '$_baseUrl/opportunities/$opportunityId/close-won',
      data: {
        'actual_amount': actualAmount,
        if (notes != null) 'notes': notes,
        if (orderId != null) 'order_id': orderId,
      },
    );
  }

  /// Close opportunity as lost
  /// إغلاق الفرصة كخاسرة
  Future<Response> closeOpportunityLost(
    String opportunityId, {
    required LossReason reason,
    String? competitorName,
    String? notes,
  }) async {
    return _dio.patch(
      '$_baseUrl/opportunities/$opportunityId/close-lost',
      data: {
        'loss_reason': reason.name,
        if (competitorName != null) 'competitor_name': competitorName,
        if (notes != null) 'notes': notes,
      },
    );
  }

  /// Get pipeline summary
  /// جلب ملخص خط الأنابيب
  Future<Response> getPipelineSummary() async {
    return _dio.get('$_baseUrl/opportunities/pipeline');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Activity Log API
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get activity log for a farmer
  /// جلب سجل النشاط لمزارع
  Future<Response> getActivityLog({
    required String farmerId,
    ActivityType? activityType,
    DateTime? startDate,
    DateTime? endDate,
    int limit = 50,
    int offset = 0,
  }) async {
    final queryParams = <String, dynamic>{
      'farmer_id': farmerId,
      'limit': limit,
      'offset': offset,
      if (activityType != null) 'activity_type': activityType.name,
      if (startDate != null) 'start_date': startDate.toIso8601String(),
      if (endDate != null) 'end_date': endDate.toIso8601String(),
    };

    return _dio.get('$_baseUrl/activities', queryParameters: queryParams);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Statistics & Analytics API
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get CRM statistics
  /// جلب إحصائيات CRM
  Future<Response> getCrmStats() async {
    return _dio.get('$_baseUrl/stats');
  }

  /// Get farmer analytics
  /// جلب تحليلات المزارع
  Future<Response> getFarmerAnalytics(String farmerId) async {
    return _dio.get('$_baseUrl/farmers/$farmerId/analytics');
  }

  /// Get agent performance
  /// جلب أداء الوكيل
  Future<Response> getAgentPerformance(String agentId, {int days = 30}) async {
    return _dio.get(
      '$_baseUrl/agents/$agentId/performance',
      queryParameters: {'days': days},
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Sync API
  // ═══════════════════════════════════════════════════════════════════════════

  /// Sync farmers from server
  /// مزامنة المزارعين من السيرفر
  Future<Response> syncFarmers({DateTime? lastSyncAt}) async {
    return _dio.get(
      '$_baseUrl/farmers/sync',
      queryParameters: {
        if (lastSyncAt != null) 'since': lastSyncAt.toIso8601String(),
      },
    );
  }

  /// Sync interactions from server
  /// مزامنة التفاعلات من السيرفر
  Future<Response> syncInteractions({DateTime? lastSyncAt}) async {
    return _dio.get(
      '$_baseUrl/interactions/sync',
      queryParameters: {
        if (lastSyncAt != null) 'since': lastSyncAt.toIso8601String(),
      },
    );
  }

  /// Sync opportunities from server
  /// مزامنة الفرص من السيرفر
  Future<Response> syncOpportunities({DateTime? lastSyncAt}) async {
    return _dio.get(
      '$_baseUrl/opportunities/sync',
      queryParameters: {
        if (lastSyncAt != null) 'since': lastSyncAt.toIso8601String(),
      },
    );
  }

  /// Batch upload local changes
  /// رفع التغييرات المحلية
  Future<Response> batchUpload({
    List<Map<String, dynamic>>? farmers,
    List<Map<String, dynamic>>? interactions,
    List<Map<String, dynamic>>? opportunities,
  }) async {
    return _dio.post(
      '$_baseUrl/sync/upload',
      data: {
        if (farmers != null) 'farmers': farmers,
        if (interactions != null) 'interactions': interactions,
        if (opportunities != null) 'opportunities': opportunities,
      },
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Health Check
  // ═══════════════════════════════════════════════════════════════════════════

  /// Health check
  Future<Response> healthCheck() async {
    return _dio.get('$_baseUrl/healthz');
  }
}
