/// CRM Providers
/// مزودات بيانات إدارة علاقات المزارعين
///
/// Riverpod providers for CRM state management
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/crm_repository.dart';
import '../domain/models/farmer_profile.dart';
import '../domain/models/interaction.dart';
import '../domain/models/opportunity.dart';
import '../domain/models/activity_log.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Filters
// ═══════════════════════════════════════════════════════════════════════════════

/// Farmer filter
/// فلتر المزارعين
class FarmerFilter {
  final String? search;
  final FarmerStatus? status;
  final FarmerSegment? segment;
  final String? governorate;
  final String? assignedAgentId;
  final List<String>? tags;
  final String? sortBy;
  final String sortOrder;

  const FarmerFilter({
    this.search,
    this.status,
    this.segment,
    this.governorate,
    this.assignedAgentId,
    this.tags,
    this.sortBy,
    this.sortOrder = 'desc',
  });

  FarmerFilter copyWith({
    String? search,
    FarmerStatus? status,
    FarmerSegment? segment,
    String? governorate,
    String? assignedAgentId,
    List<String>? tags,
    String? sortBy,
    String? sortOrder,
    bool clearSearch = false,
    bool clearStatus = false,
    bool clearSegment = false,
    bool clearGovernorate = false,
    bool clearAgent = false,
    bool clearTags = false,
  }) {
    return FarmerFilter(
      search: clearSearch ? null : (search ?? this.search),
      status: clearStatus ? null : (status ?? this.status),
      segment: clearSegment ? null : (segment ?? this.segment),
      governorate: clearGovernorate ? null : (governorate ?? this.governorate),
      assignedAgentId: clearAgent ? null : (assignedAgentId ?? this.assignedAgentId),
      tags: clearTags ? null : (tags ?? this.tags),
      sortBy: sortBy ?? this.sortBy,
      sortOrder: sortOrder ?? this.sortOrder,
    );
  }

  bool get hasFilters =>
      search != null ||
      status != null ||
      segment != null ||
      governorate != null ||
      assignedAgentId != null ||
      (tags != null && tags!.isNotEmpty);

  FarmerFilter clear() => const FarmerFilter();
}

/// Interaction filter
/// فلتر التفاعلات
class InteractionFilter {
  final String? farmerId;
  final InteractionType? type;
  final InteractionOutcome? outcome;
  final DateTime? startDate;
  final DateTime? endDate;

  const InteractionFilter({
    this.farmerId,
    this.type,
    this.outcome,
    this.startDate,
    this.endDate,
  });

  InteractionFilter copyWith({
    String? farmerId,
    InteractionType? type,
    InteractionOutcome? outcome,
    DateTime? startDate,
    DateTime? endDate,
    bool clearFarmer = false,
    bool clearType = false,
    bool clearOutcome = false,
    bool clearDates = false,
  }) {
    return InteractionFilter(
      farmerId: clearFarmer ? null : (farmerId ?? this.farmerId),
      type: clearType ? null : (type ?? this.type),
      outcome: clearOutcome ? null : (outcome ?? this.outcome),
      startDate: clearDates ? null : (startDate ?? this.startDate),
      endDate: clearDates ? null : (endDate ?? this.endDate),
    );
  }

  bool get hasFilters =>
      type != null || outcome != null || startDate != null || endDate != null;
}

/// Opportunity filter
/// فلتر الفرص
class OpportunityFilter {
  final String? farmerId;
  final OpportunityStage? stage;
  final OpportunityPriority? priority;
  final String? assignedAgentId;
  final bool openOnly;

  const OpportunityFilter({
    this.farmerId,
    this.stage,
    this.priority,
    this.assignedAgentId,
    this.openOnly = false,
  });

  OpportunityFilter copyWith({
    String? farmerId,
    OpportunityStage? stage,
    OpportunityPriority? priority,
    String? assignedAgentId,
    bool? openOnly,
    bool clearFarmer = false,
    bool clearStage = false,
    bool clearPriority = false,
    bool clearAgent = false,
  }) {
    return OpportunityFilter(
      farmerId: clearFarmer ? null : (farmerId ?? this.farmerId),
      stage: clearStage ? null : (stage ?? this.stage),
      priority: clearPriority ? null : (priority ?? this.priority),
      assignedAgentId: clearAgent ? null : (assignedAgentId ?? this.assignedAgentId),
      openOnly: openOnly ?? this.openOnly,
    );
  }

  bool get hasFilters =>
      stage != null || priority != null || assignedAgentId != null || openOnly;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Filter State Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Selected farmer filter
/// فلتر المزارعين المحدد
final farmerFilterProvider = StateProvider<FarmerFilter>((ref) => const FarmerFilter());

/// Selected interaction filter
/// فلتر التفاعلات المحدد
final interactionFilterProvider = StateProvider<InteractionFilter>((ref) => const InteractionFilter());

/// Selected opportunity filter
/// فلتر الفرص المحدد
final opportunityFilterProvider = StateProvider<OpportunityFilter>((ref) => const OpportunityFilter());

/// Selected farmer ID for detail views
/// معرف المزارع المحدد للعرض التفصيلي
final selectedFarmerIdProvider = StateProvider<String?>((ref) => null);

// ═══════════════════════════════════════════════════════════════════════════════
// Farmers Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Farmers list provider
/// مزود قائمة المزارعين
final farmersListProvider = FutureProvider.autoDispose
    .family<List<FarmerProfile>, FarmerFilter?>((ref, filter) async {
  final repo = ref.watch(crmRepositoryProvider);
  final result = await repo.getFarmers(
    search: filter?.search,
    status: filter?.status,
    segment: filter?.segment,
    governorate: filter?.governorate,
    assignedAgentId: filter?.assignedAgentId,
    tags: filter?.tags,
    sortBy: filter?.sortBy,
    sortOrder: filter?.sortOrder ?? 'desc',
  );

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب المزارعين');
});

/// Active farmers list (convenience provider)
/// قائمة المزارعين النشطين
final activeFarmersProvider = FutureProvider.autoDispose<List<FarmerProfile>>((ref) async {
  final repo = ref.watch(crmRepositoryProvider);
  final result = await repo.getFarmers(status: FarmerStatus.active);

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب المزارعين');
});

/// Farmer details provider
/// مزود تفاصيل المزارع
final farmerDetailsProvider = FutureProvider.autoDispose
    .family<FarmerProfile, String>((ref, farmerId) async {
  final repo = ref.watch(crmRepositoryProvider);
  final result = await repo.getFarmerById(farmerId);

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'المزارع غير موجود');
});

/// Farmer search provider
/// مزود البحث عن مزارعين
final farmerSearchProvider = FutureProvider.autoDispose
    .family<List<FarmerProfile>, String>((ref, query) async {
  if (query.isEmpty) return [];

  final repo = ref.watch(crmRepositoryProvider);
  final result = await repo.searchFarmers(query);

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في البحث');
});

/// Nearby farmers provider
/// مزود المزارعين القريبين
final nearbyFarmersProvider = FutureProvider.autoDispose
    .family<List<FarmerProfile>, ({double lat, double lng, double radius})>((ref, params) async {
  final repo = ref.watch(crmRepositoryProvider);
  final result = await repo.getFarmersNearby(
    latitude: params.lat,
    longitude: params.lng,
    radiusKm: params.radius,
  );

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب المزارعين القريبين');
});

// ═══════════════════════════════════════════════════════════════════════════════
// Interactions Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Interactions list provider
/// مزود قائمة التفاعلات
final interactionsListProvider = FutureProvider.autoDispose
    .family<List<Interaction>, InteractionFilter?>((ref, filter) async {
  final repo = ref.watch(crmRepositoryProvider);
  final result = await repo.getInteractions(
    farmerId: filter?.farmerId,
    type: filter?.type,
    outcome: filter?.outcome,
    startDate: filter?.startDate,
    endDate: filter?.endDate,
  );

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب التفاعلات');
});

/// Farmer interactions provider
/// مزود تفاعلات المزارع
final farmerInteractionsProvider = FutureProvider.autoDispose
    .family<List<Interaction>, String>((ref, farmerId) async {
  final repo = ref.watch(crmRepositoryProvider);
  final result = await repo.getInteractions(farmerId: farmerId);

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب التفاعلات');
});

/// Pending follow-ups provider
/// مزود المتابعات المعلقة
final pendingFollowUpsProvider = FutureProvider.autoDispose
    .family<List<Interaction>, bool>((ref, overdueOnly) async {
  final repo = ref.watch(crmRepositoryProvider);
  final result = await repo.getPendingFollowUps(overdueOnly: overdueOnly);

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب المتابعات');
});

/// Overdue follow-ups count provider
/// مزود عدد المتابعات المتأخرة
final overdueFollowUpsCountProvider = FutureProvider.autoDispose<int>((ref) async {
  final followUps = await ref.watch(pendingFollowUpsProvider(true).future);
  return followUps.length;
});

// ═══════════════════════════════════════════════════════════════════════════════
// Opportunities Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Opportunities list provider
/// مزود قائمة الفرص
final opportunitiesListProvider = FutureProvider.autoDispose
    .family<List<Opportunity>, OpportunityFilter?>((ref, filter) async {
  final repo = ref.watch(crmRepositoryProvider);
  final result = await repo.getOpportunities(
    farmerId: filter?.farmerId,
    stage: filter?.stage,
    priority: filter?.priority,
    assignedAgentId: filter?.assignedAgentId,
    openOnly: filter?.openOnly ?? false,
  );

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب الفرص');
});

/// Farmer opportunities provider
/// مزود فرص المزارع
final farmerOpportunitiesProvider = FutureProvider.autoDispose
    .family<List<Opportunity>, String>((ref, farmerId) async {
  final repo = ref.watch(crmRepositoryProvider);
  final result = await repo.getOpportunities(farmerId: farmerId);

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب الفرص');
});

/// Open opportunities provider
/// مزود الفرص المفتوحة
final openOpportunitiesProvider = FutureProvider.autoDispose<List<Opportunity>>((ref) async {
  final repo = ref.watch(crmRepositoryProvider);
  final result = await repo.getOpportunities(openOnly: true);

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب الفرص');
});

/// Opportunity details provider
/// مزود تفاصيل الفرصة
final opportunityDetailsProvider = FutureProvider.autoDispose
    .family<Opportunity, String>((ref, opportunityId) async {
  final repo = ref.watch(crmRepositoryProvider);
  final result = await repo.getOpportunityById(opportunityId);

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'الفرصة غير موجودة');
});

/// Pipeline summary provider
/// مزود ملخص خط الأنابيب
final pipelineSummaryProvider = FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  final repo = ref.watch(crmRepositoryProvider);
  final result = await repo.getPipelineSummary();

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب ملخص الأنابيب');
});

// ═══════════════════════════════════════════════════════════════════════════════
// Activity Log Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Farmer activity log provider
/// مزود سجل نشاط المزارع
final farmerActivityLogProvider = FutureProvider.autoDispose
    .family<List<ActivityLog>, String>((ref, farmerId) async {
  final repo = ref.watch(crmRepositoryProvider);
  final result = await repo.getActivityLog(farmerId: farmerId);

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب سجل النشاط');
});

// ═══════════════════════════════════════════════════════════════════════════════
// Statistics & Analytics Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// CRM statistics provider
/// مزود إحصائيات CRM
final crmStatsProvider = FutureProvider.autoDispose<CrmStats>((ref) async {
  final repo = ref.watch(crmRepositoryProvider);
  final result = await repo.getCrmStats();

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب الإحصائيات');
});

/// Farmer analytics provider
/// مزود تحليلات المزارع
final farmerAnalyticsProvider = FutureProvider.autoDispose
    .family<FarmerAnalytics, String>((ref, farmerId) async {
  final repo = ref.watch(crmRepositoryProvider);
  final result = await repo.getFarmerAnalytics(farmerId);

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب التحليلات');
});
