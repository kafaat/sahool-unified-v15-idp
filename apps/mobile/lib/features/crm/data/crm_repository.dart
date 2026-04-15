/// CRM Repository
/// مستودع إدارة علاقات المزارعين
///
/// Offline-first repository combining API and local database
library;

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/offline/offline_sync_engine.dart';
import '../../../core/utils/app_logger.dart';
import '../domain/models/farmer_profile.dart';
import '../domain/models/interaction.dart';
import '../domain/models/opportunity.dart';
import '../domain/models/activity_log.dart';
import 'crm_api.dart';

/// CRM Repository Provider
final crmRepositoryProvider = Provider<CrmRepository>((ref) {
  return CrmRepository();
});

/// API Result wrapper
/// غلاف نتيجة API
class ApiResult<T> {
  final T? data;
  final String? error;
  final String? errorAr;
  final bool isSuccess;

  const ApiResult._({this.data, this.error, this.errorAr, required this.isSuccess});

  factory ApiResult.success(T data) => ApiResult._(data: data, isSuccess: true);
  factory ApiResult.failure(String error, [String? errorAr]) =>
      ApiResult._(error: error, errorAr: errorAr, isSuccess: false);
}

/// CRM Repository
/// مستودع CRM - يجمع بين API والتخزين المحلي
class CrmRepository {
  final CrmApi _api;

  CrmRepository({CrmApi? api}) : _api = api ?? CrmApi();

  // ═══════════════════════════════════════════════════════════════════════════
  // Farmers
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get all farmers
  /// جلب جميع المزارعين
  Future<ApiResult<List<FarmerProfile>>> getFarmers({
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
    try {
      final response = await _api.getFarmers(
        search: search,
        status: status,
        segment: segment,
        governorate: governorate,
        assignedAgentId: assignedAgentId,
        tags: tags,
        limit: limit,
        offset: offset,
        sortBy: sortBy,
        sortOrder: sortOrder,
      );

      final data = response.data as Map<String, dynamic>;
      final farmers = (data['farmers'] as List? ?? data['data'] as List? ?? [])
          .map((e) => FarmerProfile.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(farmers);
    } on DioException catch (e) {
      return _handleDioError(e, 'فشل في جلب المزارعين');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Get farmer by ID
  /// جلب مزارع بواسطة المعرف
  Future<ApiResult<FarmerProfile>> getFarmerById(String farmerId) async {
    try {
      final response = await _api.getFarmerById(farmerId);
      return ApiResult.success(
        FarmerProfile.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Farmer not found', 'المزارع غير موجود');
      }
      return _handleDioError(e, 'فشل في جلب المزارع');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Create new farmer
  /// إنشاء مزارع جديد
  Future<ApiResult<FarmerProfile>> createFarmer(FarmerProfile farmer) async {
    final farmerData = farmer.toJson();
    try {
      final response = await _api.createFarmer(farmerData);

      AppLogger.i('Farmer created via API', tag: 'CrmRepo', data: {'farmer': farmer.id});

      return ApiResult.success(
        FarmerProfile.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      // Only enqueue for offline sync on transient/network errors, not 4xx client errors
      final isTransient = e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.connectionError ||
          (e.response?.statusCode != null && (e.response!.statusCode! >= 500 || e.response!.statusCode! == 429));

      if (isTransient) {
        await OfflineSyncEngine.instance.enqueueCreate(
          entityType: 'crm',
          data: {'type': 'farmer', ...farmerData},
          priority: SyncPriority.medium,
        );

        AppLogger.w('Farmer creation queued for offline sync (API unavailable)', tag: 'CrmRepo');
        return ApiResult.failure(
          'Saved offline - will sync when connected',
          'تم الحفظ محلياً - ستتم المزامنة عند الاتصال',
        );
      }

      return _handleDioError(e, 'فشل في إنشاء المزارع');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Update farmer
  /// تحديث مزارع
  Future<ApiResult<FarmerProfile>> updateFarmer(
    String farmerId,
    Map<String, dynamic> updates,
  ) async {
    try {
      final response = await _api.updateFarmer(farmerId, updates);

      AppLogger.i('Farmer updated via API', tag: 'CrmRepo', data: {'farmerId': farmerId});

      return ApiResult.success(
        FarmerProfile.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Farmer not found', 'المزارع غير موجود');
      }

      // Only enqueue for offline sync on transient/network errors, not 4xx client errors
      final isTransient = e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.connectionError ||
          (e.response?.statusCode != null && (e.response!.statusCode! >= 500 || e.response!.statusCode! == 429));

      if (isTransient) {
        await OfflineSyncEngine.instance.enqueueUpdate(
          entityType: 'crm',
          entityId: farmerId,
          data: {'type': 'farmer', ...updates},
          priority: SyncPriority.medium,
        );

        AppLogger.w('Farmer update queued for offline sync (API unavailable)', tag: 'CrmRepo');
        return ApiResult.failure(
          'Saved offline - will sync when connected',
          'تم الحفظ محلياً - ستتم المزامنة عند الاتصال',
        );
      }

      return _handleDioError(e, 'فشل في تحديث المزارع');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Delete farmer
  /// حذف مزارع
  Future<ApiResult<void>> deleteFarmer(String farmerId) async {
    try {
      await _api.deleteFarmer(farmerId);
      return ApiResult.success(null);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Farmer not found', 'المزارع غير موجود');
      }
      return _handleDioError(e, 'فشل في حذف المزارع');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Search farmers
  /// البحث عن مزارعين
  Future<ApiResult<List<FarmerProfile>>> searchFarmers(
    String query, {
    int limit = 20,
  }) async {
    try {
      final response = await _api.searchFarmers(query, limit: limit);
      final data = response.data as Map<String, dynamic>;
      final farmers = (data['farmers'] as List? ?? data['data'] as List? ?? [])
          .map((e) => FarmerProfile.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(farmers);
    } on DioException catch (e) {
      return _handleDioError(e, 'فشل في البحث');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Get farmers nearby
  /// جلب المزارعين القريبين
  Future<ApiResult<List<FarmerProfile>>> getFarmersNearby({
    required double latitude,
    required double longitude,
    double radiusKm = 10,
    int limit = 20,
  }) async {
    try {
      final response = await _api.getFarmersNearby(
        latitude: latitude,
        longitude: longitude,
        radiusKm: radiusKm,
        limit: limit,
      );
      final data = response.data as Map<String, dynamic>;
      final farmers = (data['farmers'] as List? ?? data['data'] as List? ?? [])
          .map((e) => FarmerProfile.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(farmers);
    } on DioException catch (e) {
      return _handleDioError(e, 'فشل في جلب المزارعين القريبين');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Update farmer status
  /// تحديث حالة المزارع
  Future<ApiResult<FarmerProfile>> updateFarmerStatus(
    String farmerId,
    FarmerStatus status,
  ) async {
    try {
      final response = await _api.updateFarmerStatus(farmerId, status);
      return ApiResult.success(
        FarmerProfile.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return _handleDioError(e, 'فشل في تحديث الحالة');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Update farmer segment
  /// تحديث شريحة المزارع
  Future<ApiResult<FarmerProfile>> updateFarmerSegment(
    String farmerId,
    FarmerSegment segment,
  ) async {
    try {
      final response = await _api.updateFarmerSegment(farmerId, segment);
      return ApiResult.success(
        FarmerProfile.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return _handleDioError(e, 'فشل في تحديث الشريحة');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Assign farmer to agent
  /// تعيين مزارع لوكيل
  Future<ApiResult<FarmerProfile>> assignFarmerToAgent(
    String farmerId,
    String agentId,
  ) async {
    try {
      final response = await _api.assignFarmerToAgent(farmerId, agentId);
      return ApiResult.success(
        FarmerProfile.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return _handleDioError(e, 'فشل في تعيين المزارع');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Interactions
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get interactions
  /// جلب التفاعلات
  Future<ApiResult<List<Interaction>>> getInteractions({
    String? farmerId,
    InteractionType? type,
    InteractionOutcome? outcome,
    DateTime? startDate,
    DateTime? endDate,
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final response = await _api.getInteractions(
        farmerId: farmerId,
        type: type,
        outcome: outcome,
        startDate: startDate,
        endDate: endDate,
        limit: limit,
        offset: offset,
      );

      final data = response.data as Map<String, dynamic>;
      final interactions =
          (data['interactions'] as List? ?? data['data'] as List? ?? [])
              .map((e) => Interaction.fromJson(e as Map<String, dynamic>))
              .toList();

      return ApiResult.success(interactions);
    } on DioException catch (e) {
      return _handleDioError(e, 'فشل في جلب التفاعلات');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Get interaction by ID
  /// جلب تفاعل بواسطة المعرف
  Future<ApiResult<Interaction>> getInteractionById(String interactionId) async {
    try {
      final response = await _api.getInteractionById(interactionId);
      return ApiResult.success(
        Interaction.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Interaction not found', 'التفاعل غير موجود');
      }
      return _handleDioError(e, 'فشل في جلب التفاعل');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Create new interaction
  /// إنشاء تفاعل جديد
  Future<ApiResult<Interaction>> createInteraction(Interaction interaction) async {
    final interactionData = interaction.toJson();
    try {
      final response = await _api.createInteraction(interactionData);

      AppLogger.i('Interaction created via API', tag: 'CrmRepo', data: {'interaction': interaction.id});

      return ApiResult.success(
        Interaction.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      // Only enqueue for offline sync on transient/network errors, not 4xx client errors
      final isTransient = e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.connectionError ||
          (e.response?.statusCode != null && (e.response!.statusCode! >= 500 || e.response!.statusCode! == 429));

      if (isTransient) {
        await OfflineSyncEngine.instance.enqueueCreate(
          entityType: 'crm',
          data: {'type': 'interaction', ...interactionData},
          priority: SyncPriority.medium,
        );

        AppLogger.w('Interaction creation queued for offline sync (API unavailable)', tag: 'CrmRepo');
        return ApiResult.failure(
          'Saved offline - will sync when connected',
          'تم الحفظ محلياً - ستتم المزامنة عند الاتصال',
        );
      }

      return _handleDioError(e, 'فشل في إنشاء التفاعل');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Update interaction
  /// تحديث تفاعل
  Future<ApiResult<Interaction>> updateInteraction(
    String interactionId,
    Map<String, dynamic> updates,
  ) async {
    try {
      final response = await _api.updateInteraction(interactionId, updates);

      AppLogger.i('Interaction updated via API', tag: 'CrmRepo', data: {'interactionId': interactionId});

      return ApiResult.success(
        Interaction.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Interaction not found', 'التفاعل غير موجود');
      }

      // Only enqueue for offline sync on transient/network errors, not 4xx client errors
      final isTransient = e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.connectionError ||
          (e.response?.statusCode != null && (e.response!.statusCode! >= 500 || e.response!.statusCode! == 429));

      if (isTransient) {
        await OfflineSyncEngine.instance.enqueueUpdate(
          entityType: 'crm',
          entityId: interactionId,
          data: {'type': 'interaction', ...updates},
          priority: SyncPriority.medium,
        );

        AppLogger.w('Interaction update queued for offline sync (API unavailable)', tag: 'CrmRepo');
        return ApiResult.failure(
          'Saved offline - will sync when connected',
          'تم الحفظ محلياً - ستتم المزامنة عند الاتصال',
        );
      }

      return _handleDioError(e, 'فشل في تحديث التفاعل');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Delete interaction
  /// حذف تفاعل
  Future<ApiResult<void>> deleteInteraction(String interactionId) async {
    try {
      await _api.deleteInteraction(interactionId);
      return ApiResult.success(null);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Interaction not found', 'التفاعل غير موجود');
      }
      return _handleDioError(e, 'فشل في حذف التفاعل');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Get pending follow-ups
  /// جلب المتابعات المعلقة
  Future<ApiResult<List<Interaction>>> getPendingFollowUps({
    String? agentId,
    bool overdueOnly = false,
    int limit = 50,
  }) async {
    try {
      final response = await _api.getPendingFollowUps(
        agentId: agentId,
        overdueOnly: overdueOnly,
        limit: limit,
      );

      final data = response.data as Map<String, dynamic>;
      final followUps =
          (data['follow_ups'] as List? ?? data['data'] as List? ?? [])
              .map((e) => Interaction.fromJson(e as Map<String, dynamic>))
              .toList();

      return ApiResult.success(followUps);
    } on DioException catch (e) {
      return _handleDioError(e, 'فشل في جلب المتابعات');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Complete follow-up
  /// إكمال المتابعة
  Future<ApiResult<Interaction>> completeFollowUp(
    String interactionId, {
    String? notes,
  }) async {
    try {
      final response = await _api.completeFollowUp(interactionId, notes: notes);
      return ApiResult.success(
        Interaction.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return _handleDioError(e, 'فشل في إكمال المتابعة');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Opportunities
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get opportunities
  /// جلب الفرص
  Future<ApiResult<List<Opportunity>>> getOpportunities({
    String? farmerId,
    OpportunityStage? stage,
    OpportunityPriority? priority,
    String? assignedAgentId,
    bool openOnly = false,
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final response = await _api.getOpportunities(
        farmerId: farmerId,
        stage: stage,
        priority: priority,
        assignedAgentId: assignedAgentId,
        openOnly: openOnly,
        limit: limit,
        offset: offset,
      );

      final data = response.data as Map<String, dynamic>;
      final opportunities =
          (data['opportunities'] as List? ?? data['data'] as List? ?? [])
              .map((e) => Opportunity.fromJson(e as Map<String, dynamic>))
              .toList();

      return ApiResult.success(opportunities);
    } on DioException catch (e) {
      return _handleDioError(e, 'فشل في جلب الفرص');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Get opportunity by ID
  /// جلب فرصة بواسطة المعرف
  Future<ApiResult<Opportunity>> getOpportunityById(String opportunityId) async {
    try {
      final response = await _api.getOpportunityById(opportunityId);
      return ApiResult.success(
        Opportunity.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Opportunity not found', 'الفرصة غير موجودة');
      }
      return _handleDioError(e, 'فشل في جلب الفرصة');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Create new opportunity
  /// إنشاء فرصة جديدة
  Future<ApiResult<Opportunity>> createOpportunity(Opportunity opportunity) async {
    final opportunityData = opportunity.toJson();
    try {
      final response = await _api.createOpportunity(opportunityData);

      AppLogger.i('Opportunity created via API', tag: 'CrmRepo', data: {'opportunity': opportunity.id});

      return ApiResult.success(
        Opportunity.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      // Only enqueue for offline sync on transient/network errors, not 4xx client errors
      final isTransient = e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.connectionError ||
          (e.response?.statusCode != null && (e.response!.statusCode! >= 500 || e.response!.statusCode! == 429));

      if (isTransient) {
        await OfflineSyncEngine.instance.enqueueCreate(
          entityType: 'crm',
          data: {'type': 'opportunity', ...opportunityData},
          priority: SyncPriority.medium,
        );

        AppLogger.w('Opportunity creation queued for offline sync (API unavailable)', tag: 'CrmRepo');
        return ApiResult.failure(
          'Saved offline - will sync when connected',
          'تم الحفظ محلياً - ستتم المزامنة عند الاتصال',
        );
      }

      return _handleDioError(e, 'فشل في إنشاء الفرصة');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Update opportunity
  /// تحديث فرصة
  Future<ApiResult<Opportunity>> updateOpportunity(
    String opportunityId,
    Map<String, dynamic> updates,
  ) async {
    try {
      final response = await _api.updateOpportunity(opportunityId, updates);

      AppLogger.i('Opportunity updated via API', tag: 'CrmRepo', data: {'opportunityId': opportunityId});

      return ApiResult.success(
        Opportunity.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Opportunity not found', 'الفرصة غير موجودة');
      }

      // Only enqueue for offline sync on transient/network errors, not 4xx client errors
      final isTransient = e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.connectionError ||
          (e.response?.statusCode != null && (e.response!.statusCode! >= 500 || e.response!.statusCode! == 429));

      if (isTransient) {
        await OfflineSyncEngine.instance.enqueueUpdate(
          entityType: 'crm',
          entityId: opportunityId,
          data: {'type': 'opportunity', ...updates},
          priority: SyncPriority.medium,
        );

        AppLogger.w('Opportunity update queued for offline sync (API unavailable)', tag: 'CrmRepo');
        return ApiResult.failure(
          'Saved offline - will sync when connected',
          'تم الحفظ محلياً - ستتم المزامنة عند الاتصال',
        );
      }

      return _handleDioError(e, 'فشل في تحديث الفرصة');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Delete opportunity
  /// حذف فرصة
  Future<ApiResult<void>> deleteOpportunity(String opportunityId) async {
    try {
      await _api.deleteOpportunity(opportunityId);
      return ApiResult.success(null);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Opportunity not found', 'الفرصة غير موجودة');
      }
      return _handleDioError(e, 'فشل في حذف الفرصة');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Update opportunity stage
  /// تحديث مرحلة الفرصة
  Future<ApiResult<Opportunity>> updateOpportunityStage(
    String opportunityId,
    OpportunityStage stage, {
    String? notes,
  }) async {
    try {
      final response = await _api.updateOpportunityStage(
        opportunityId,
        stage,
        notes: notes,
      );
      return ApiResult.success(
        Opportunity.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return _handleDioError(e, 'فشل في تحديث المرحلة');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Close opportunity as won
  /// إغلاق الفرصة كناجحة
  Future<ApiResult<Opportunity>> closeOpportunityWon(
    String opportunityId, {
    required double actualAmount,
    String? notes,
    String? orderId,
  }) async {
    try {
      final response = await _api.closeOpportunityWon(
        opportunityId,
        actualAmount: actualAmount,
        notes: notes,
        orderId: orderId,
      );
      return ApiResult.success(
        Opportunity.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return _handleDioError(e, 'فشل في إغلاق الفرصة');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Close opportunity as lost
  /// إغلاق الفرصة كخاسرة
  Future<ApiResult<Opportunity>> closeOpportunityLost(
    String opportunityId, {
    required LossReason reason,
    String? competitorName,
    String? notes,
  }) async {
    try {
      final response = await _api.closeOpportunityLost(
        opportunityId,
        reason: reason,
        competitorName: competitorName,
        notes: notes,
      );
      return ApiResult.success(
        Opportunity.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return _handleDioError(e, 'فشل في إغلاق الفرصة');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Get pipeline summary
  /// جلب ملخص خط الأنابيب
  Future<ApiResult<Map<String, dynamic>>> getPipelineSummary() async {
    try {
      final response = await _api.getPipelineSummary();
      return ApiResult.success(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      return _handleDioError(e, 'فشل في جلب ملخص الأنابيب');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Activity Log
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get activity log for a farmer
  /// جلب سجل النشاط لمزارع
  Future<ApiResult<List<ActivityLog>>> getActivityLog({
    required String farmerId,
    ActivityType? activityType,
    DateTime? startDate,
    DateTime? endDate,
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final response = await _api.getActivityLog(
        farmerId: farmerId,
        activityType: activityType,
        startDate: startDate,
        endDate: endDate,
        limit: limit,
        offset: offset,
      );

      final data = response.data as Map<String, dynamic>;
      final activities =
          (data['activities'] as List? ?? data['data'] as List? ?? [])
              .map((e) => ActivityLog.fromJson(e as Map<String, dynamic>))
              .toList();

      return ApiResult.success(activities);
    } on DioException catch (e) {
      return _handleDioError(e, 'فشل في جلب سجل النشاط');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Statistics & Analytics
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get CRM statistics
  /// جلب إحصائيات CRM
  Future<ApiResult<CrmStats>> getCrmStats() async {
    try {
      final response = await _api.getCrmStats();
      return ApiResult.success(
        CrmStats.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return _handleDioError(e, 'فشل في جلب الإحصائيات');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Get farmer analytics
  /// جلب تحليلات المزارع
  Future<ApiResult<FarmerAnalytics>> getFarmerAnalytics(String farmerId) async {
    try {
      final response = await _api.getFarmerAnalytics(farmerId);
      return ApiResult.success(
        FarmerAnalytics.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return _handleDioError(e, 'فشل في جلب التحليلات');
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Error Handling
  // ═══════════════════════════════════════════════════════════════════════════

  /// Handle Dio errors
  /// معالجة أخطاء Dio
  ApiResult<T> _handleDioError<T>(DioException e, String arabicMessage) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return ApiResult.failure('Connection timeout', 'انتهت مهلة الاتصال');
      case DioExceptionType.connectionError:
        return ApiResult.failure('No internet connection', 'لا يوجد اتصال بالإنترنت');
      case DioExceptionType.badResponse:
        final statusCode = e.response?.statusCode;
        final message = e.response?.data is Map
            ? (e.response!.data as Map)['message'] ??
                (e.response!.data as Map)['error'] ??
                e.message
            : e.message;
        return ApiResult.failure(
          message.toString(),
          statusCode == 401
              ? 'جلسة منتهية، يرجى تسجيل الدخول'
              : statusCode == 403
                  ? 'ليس لديك صلاحية'
                  : arabicMessage,
        );
      default:
        return ApiResult.failure(e.message ?? 'Unknown error', arabicMessage);
    }
  }
}
