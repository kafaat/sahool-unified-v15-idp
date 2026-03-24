/// CRM Controller
/// متحكم إدارة علاقات المزارعين
///
/// StateNotifier controller for CRM CRUD operations
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/crm_repository.dart';
import '../domain/models/farmer_profile.dart';
import '../domain/models/interaction.dart';
import '../domain/models/opportunity.dart';
import 'crm_providers.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Farmer Controller
// ═══════════════════════════════════════════════════════════════════════════════

/// Farmer Controller
/// متحكم المزارعين
class FarmerController extends StateNotifier<AsyncValue<void>> {
  final CrmRepository _repo;
  final Ref _ref;

  FarmerController(this._repo, this._ref) : super(const AsyncValue.data(null));

  /// Create new farmer
  /// إنشاء مزارع جديد
  Future<FarmerProfile?> createFarmer(FarmerProfile farmer) async {
    state = const AsyncValue.loading();

    final result = await _repo.createFarmer(farmer);

    if (result.isSuccess && result.data != null) {
      state = const AsyncValue.data(null);
      _invalidateFarmerProviders();
      return result.data;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إنشاء المزارع',
      StackTrace.current,
    );
    return null;
  }

  /// Update farmer
  /// تحديث مزارع
  Future<bool> updateFarmer(String farmerId, Map<String, dynamic> updates) async {
    state = const AsyncValue.loading();

    final result = await _repo.updateFarmer(farmerId, updates);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _invalidateFarmerProviders();
      _ref.invalidate(farmerDetailsProvider(farmerId));
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تحديث المزارع',
      StackTrace.current,
    );
    return false;
  }

  /// Delete farmer
  /// حذف مزارع
  Future<bool> deleteFarmer(String farmerId) async {
    state = const AsyncValue.loading();

    final result = await _repo.deleteFarmer(farmerId);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _invalidateFarmerProviders();
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في حذف المزارع',
      StackTrace.current,
    );
    return false;
  }

  /// Update farmer status
  /// تحديث حالة المزارع
  Future<bool> updateStatus(String farmerId, FarmerStatus status) async {
    state = const AsyncValue.loading();

    final result = await _repo.updateFarmerStatus(farmerId, status);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _invalidateFarmerProviders();
      _ref.invalidate(farmerDetailsProvider(farmerId));
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تحديث الحالة',
      StackTrace.current,
    );
    return false;
  }

  /// Update farmer segment
  /// تحديث شريحة المزارع
  Future<bool> updateSegment(String farmerId, FarmerSegment segment) async {
    state = const AsyncValue.loading();

    final result = await _repo.updateFarmerSegment(farmerId, segment);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _invalidateFarmerProviders();
      _ref.invalidate(farmerDetailsProvider(farmerId));
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تحديث الشريحة',
      StackTrace.current,
    );
    return false;
  }

  /// Assign farmer to agent
  /// تعيين مزارع لوكيل
  Future<bool> assignToAgent(String farmerId, String agentId) async {
    state = const AsyncValue.loading();

    final result = await _repo.assignFarmerToAgent(farmerId, agentId);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _invalidateFarmerProviders();
      _ref.invalidate(farmerDetailsProvider(farmerId));
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تعيين المزارع',
      StackTrace.current,
    );
    return false;
  }

  void _invalidateFarmerProviders() {
    _ref.invalidate(farmersListProvider);
    _ref.invalidate(activeFarmersProvider);
    _ref.invalidate(crmStatsProvider);
  }
}

/// Farmer controller provider
/// مزود متحكم المزارعين
final farmerControllerProvider =
    StateNotifierProvider<FarmerController, AsyncValue<void>>((ref) {
  final repo = ref.watch(crmRepositoryProvider);
  return FarmerController(repo, ref);
});

// ═══════════════════════════════════════════════════════════════════════════════
// Interaction Controller
// ═══════════════════════════════════════════════════════════════════════════════

/// Interaction Controller
/// متحكم التفاعلات
class InteractionController extends StateNotifier<AsyncValue<void>> {
  final CrmRepository _repo;
  final Ref _ref;

  InteractionController(this._repo, this._ref) : super(const AsyncValue.data(null));

  /// Create new interaction
  /// إنشاء تفاعل جديد
  Future<Interaction?> createInteraction(Interaction interaction) async {
    state = const AsyncValue.loading();

    final result = await _repo.createInteraction(interaction);

    if (result.isSuccess && result.data != null) {
      state = const AsyncValue.data(null);
      _invalidateInteractionProviders(interaction.farmerId);
      return result.data;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إنشاء التفاعل',
      StackTrace.current,
    );
    return null;
  }

  /// Update interaction
  /// تحديث تفاعل
  Future<bool> updateInteraction(
    String interactionId,
    String farmerId,
    Map<String, dynamic> updates,
  ) async {
    state = const AsyncValue.loading();

    final result = await _repo.updateInteraction(interactionId, updates);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _invalidateInteractionProviders(farmerId);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تحديث التفاعل',
      StackTrace.current,
    );
    return false;
  }

  /// Delete interaction
  /// حذف تفاعل
  Future<bool> deleteInteraction(String interactionId, String farmerId) async {
    state = const AsyncValue.loading();

    final result = await _repo.deleteInteraction(interactionId);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _invalidateInteractionProviders(farmerId);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في حذف التفاعل',
      StackTrace.current,
    );
    return false;
  }

  /// Complete follow-up
  /// إكمال المتابعة
  Future<bool> completeFollowUp(
    String interactionId,
    String farmerId, {
    String? notes,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.completeFollowUp(interactionId, notes: notes);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _invalidateInteractionProviders(farmerId);
      _ref.invalidate(pendingFollowUpsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إكمال المتابعة',
      StackTrace.current,
    );
    return false;
  }

  /// Log a phone call
  /// تسجيل مكالمة هاتفية
  Future<Interaction?> logCall({
    required String farmerId,
    required String farmerName,
    required String subject,
    required InteractionOutcome outcome,
    String? description,
    int? durationMinutes,
    DateTime? followUpAt,
    String? followUpNotes,
  }) async {
    final now = DateTime.now();
    final interaction = Interaction(
      id: 'local_${now.millisecondsSinceEpoch}',
      tenantId: '', // Will be set by server
      farmerId: farmerId,
      farmerName: farmerName,
      type: InteractionType.call,
      direction: InteractionDirection.outbound,
      outcome: outcome,
      subject: subject,
      description: description,
      durationMinutes: durationMinutes,
      interactionAt: now,
      followUpAt: followUpAt,
      followUpNotes: followUpNotes,
      createdAt: now,
      updatedAt: now,
    );

    return createInteraction(interaction);
  }

  /// Log a visit
  /// تسجيل زيارة
  Future<Interaction?> logVisit({
    required String farmerId,
    required String farmerName,
    required String subject,
    required InteractionOutcome outcome,
    String? description,
    int? durationMinutes,
    double? latitude,
    double? longitude,
    String? locationName,
    String? fieldId,
    List<String>? photos,
    DateTime? followUpAt,
    String? followUpNotes,
  }) async {
    final now = DateTime.now();
    final interaction = Interaction(
      id: 'local_${now.millisecondsSinceEpoch}',
      tenantId: '', // Will be set by server
      farmerId: farmerId,
      farmerName: farmerName,
      type: InteractionType.visit,
      direction: InteractionDirection.outbound,
      outcome: outcome,
      subject: subject,
      description: description,
      durationMinutes: durationMinutes,
      interactionAt: now,
      latitude: latitude,
      longitude: longitude,
      locationName: locationName,
      fieldId: fieldId,
      photos: photos ?? [],
      followUpAt: followUpAt,
      followUpNotes: followUpNotes,
      createdAt: now,
      updatedAt: now,
    );

    return createInteraction(interaction);
  }

  /// Log a message (WhatsApp, SMS)
  /// تسجيل رسالة
  Future<Interaction?> logMessage({
    required String farmerId,
    required String farmerName,
    required InteractionType type, // whatsapp or sms
    required String subject,
    required InteractionOutcome outcome,
    String? description,
    InteractionDirection direction = InteractionDirection.outbound,
  }) async {
    final now = DateTime.now();
    final interaction = Interaction(
      id: 'local_${now.millisecondsSinceEpoch}',
      tenantId: '', // Will be set by server
      farmerId: farmerId,
      farmerName: farmerName,
      type: type,
      direction: direction,
      outcome: outcome,
      subject: subject,
      description: description,
      interactionAt: now,
      createdAt: now,
      updatedAt: now,
    );

    return createInteraction(interaction);
  }

  /// Add a note
  /// إضافة ملاحظة
  Future<Interaction?> addNote({
    required String farmerId,
    required String farmerName,
    required String subject,
    String? description,
  }) async {
    final now = DateTime.now();
    final interaction = Interaction(
      id: 'local_${now.millisecondsSinceEpoch}',
      tenantId: '', // Will be set by server
      farmerId: farmerId,
      farmerName: farmerName,
      type: InteractionType.note,
      outcome: InteractionOutcome.successful,
      subject: subject,
      description: description,
      interactionAt: now,
      createdAt: now,
      updatedAt: now,
    );

    return createInteraction(interaction);
  }

  void _invalidateInteractionProviders(String farmerId) {
    _ref.invalidate(interactionsListProvider);
    _ref.invalidate(farmerInteractionsProvider(farmerId));
    _ref.invalidate(farmerActivityLogProvider(farmerId));
    _ref.invalidate(farmerDetailsProvider(farmerId));
    _ref.invalidate(crmStatsProvider);
  }
}

/// Interaction controller provider
/// مزود متحكم التفاعلات
final interactionControllerProvider =
    StateNotifierProvider<InteractionController, AsyncValue<void>>((ref) {
  final repo = ref.watch(crmRepositoryProvider);
  return InteractionController(repo, ref);
});

// ═══════════════════════════════════════════════════════════════════════════════
// Opportunity Controller
// ═══════════════════════════════════════════════════════════════════════════════

/// Opportunity Controller
/// متحكم الفرص
class OpportunityController extends StateNotifier<AsyncValue<void>> {
  final CrmRepository _repo;
  final Ref _ref;

  OpportunityController(this._repo, this._ref) : super(const AsyncValue.data(null));

  /// Create new opportunity
  /// إنشاء فرصة جديدة
  Future<Opportunity?> createOpportunity(Opportunity opportunity) async {
    state = const AsyncValue.loading();

    final result = await _repo.createOpportunity(opportunity);

    if (result.isSuccess && result.data != null) {
      state = const AsyncValue.data(null);
      _invalidateOpportunityProviders(opportunity.farmerId);
      return result.data;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إنشاء الفرصة',
      StackTrace.current,
    );
    return null;
  }

  /// Update opportunity
  /// تحديث فرصة
  Future<bool> updateOpportunity(
    String opportunityId,
    String farmerId,
    Map<String, dynamic> updates,
  ) async {
    state = const AsyncValue.loading();

    final result = await _repo.updateOpportunity(opportunityId, updates);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _invalidateOpportunityProviders(farmerId);
      _ref.invalidate(opportunityDetailsProvider(opportunityId));
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تحديث الفرصة',
      StackTrace.current,
    );
    return false;
  }

  /// Delete opportunity
  /// حذف فرصة
  Future<bool> deleteOpportunity(String opportunityId, String farmerId) async {
    state = const AsyncValue.loading();

    final result = await _repo.deleteOpportunity(opportunityId);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _invalidateOpportunityProviders(farmerId);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في حذف الفرصة',
      StackTrace.current,
    );
    return false;
  }

  /// Update opportunity stage
  /// تحديث مرحلة الفرصة
  Future<bool> updateStage(
    String opportunityId,
    String farmerId,
    OpportunityStage stage, {
    String? notes,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.updateOpportunityStage(
      opportunityId,
      stage,
      notes: notes,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _invalidateOpportunityProviders(farmerId);
      _ref.invalidate(opportunityDetailsProvider(opportunityId));
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تحديث المرحلة',
      StackTrace.current,
    );
    return false;
  }

  /// Close opportunity as won
  /// إغلاق الفرصة كناجحة
  Future<bool> closeAsWon(
    String opportunityId,
    String farmerId, {
    required double actualAmount,
    String? notes,
    String? orderId,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.closeOpportunityWon(
      opportunityId,
      actualAmount: actualAmount,
      notes: notes,
      orderId: orderId,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _invalidateOpportunityProviders(farmerId);
      _ref.invalidate(opportunityDetailsProvider(opportunityId));
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إغلاق الفرصة',
      StackTrace.current,
    );
    return false;
  }

  /// Close opportunity as lost
  /// إغلاق الفرصة كخاسرة
  Future<bool> closeAsLost(
    String opportunityId,
    String farmerId, {
    required LossReason reason,
    String? competitorName,
    String? notes,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.closeOpportunityLost(
      opportunityId,
      reason: reason,
      competitorName: competitorName,
      notes: notes,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _invalidateOpportunityProviders(farmerId);
      _ref.invalidate(opportunityDetailsProvider(opportunityId));
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إغلاق الفرصة',
      StackTrace.current,
    );
    return false;
  }

  void _invalidateOpportunityProviders(String farmerId) {
    _ref.invalidate(opportunitiesListProvider);
    _ref.invalidate(farmerOpportunitiesProvider(farmerId));
    _ref.invalidate(openOpportunitiesProvider);
    _ref.invalidate(pipelineSummaryProvider);
    _ref.invalidate(farmerActivityLogProvider(farmerId));
    _ref.invalidate(crmStatsProvider);
  }
}

/// Opportunity controller provider
/// مزود متحكم الفرص
final opportunityControllerProvider =
    StateNotifierProvider<OpportunityController, AsyncValue<void>>((ref) {
  final repo = ref.watch(crmRepositoryProvider);
  return OpportunityController(repo, ref);
});
