/// Activity Log Model
/// نموذج سجل النشاط
///
/// Represents all farmer interactions and activities in a unified log
library;

/// Activity type
/// نوع النشاط
enum ActivityType {
  // Interaction activities
  call,               // مكالمة
  visit,              // زيارة
  message,            // رسالة
  meeting,            // اجتماع

  // CRM activities
  farmerCreated,      // إنشاء مزارع
  farmerUpdated,      // تحديث مزارع
  statusChanged,      // تغيير الحالة
  segmentChanged,     // تغيير الشريحة

  // Opportunity activities
  opportunityCreated, // إنشاء فرصة
  opportunityUpdated, // تحديث فرصة
  stageChanged,       // تغيير المرحلة
  opportunityWon,     // فرصة ناجحة
  opportunityLost,    // فرصة خاسرة

  // Sales activities
  orderCreated,       // إنشاء طلب
  orderCompleted,     // اكتمال طلب
  paymentReceived,    // استلام دفعة

  // Field activities
  fieldAssigned,      // تعيين حقل
  fieldVisit,         // زيارة حقل

  // System activities
  noteAdded,          // إضافة ملاحظة
  tagAdded,           // إضافة وسم
  assignmentChanged,  // تغيير التعيين
  reminderSet,        // تعيين تذكير
}

/// Activity source
/// مصدر النشاط
enum ActivitySource {
  manual,       // يدوي
  system,       // تلقائي
  import,       // استيراد
  sync,         // مزامنة
  integration,  // تكامل
}

/// Activity Log Entry
/// سجل النشاط
class ActivityLog {
  /// Unique identifier
  final String id;

  /// Tenant ID for multi-tenancy
  final String tenantId;

  /// Farmer ID
  final String farmerId;

  /// Farmer name (for display)
  final String? farmerName;

  /// Activity type
  final ActivityType activityType;

  /// Activity source
  final ActivitySource source;

  /// Activity title
  final String title;

  /// Title in Arabic
  final String? titleAr;

  /// Activity description
  final String? description;

  /// Description in Arabic
  final String? descriptionAr;

  // ─────────────────────────────────────────────────────────────────────────────
  // Related Entities
  // ─────────────────────────────────────────────────────────────────────────────

  /// Related interaction ID
  final String? interactionId;

  /// Related opportunity ID
  final String? opportunityId;

  /// Related order ID
  final String? orderId;

  /// Related field ID
  final String? fieldId;

  /// Related task ID
  final String? taskId;

  // ─────────────────────────────────────────────────────────────────────────────
  // Actor Information
  // ─────────────────────────────────────────────────────────────────────────────

  /// User who performed the action
  final String? userId;

  /// User name
  final String? userName;

  /// Agent/salesperson ID
  final String? agentId;

  /// Agent name
  final String? agentName;

  // ─────────────────────────────────────────────────────────────────────────────
  // Change Tracking
  // ─────────────────────────────────────────────────────────────────────────────

  /// Previous value (for changes)
  final String? previousValue;

  /// New value (for changes)
  final String? newValue;

  /// Field/attribute that was changed
  final String? changedField;

  // ─────────────────────────────────────────────────────────────────────────────
  // Metadata
  // ─────────────────────────────────────────────────────────────────────────────

  /// Activity timestamp
  final DateTime activityAt;

  /// Duration in minutes (if applicable)
  final int? durationMinutes;

  /// Monetary amount (if applicable)
  final double? amount;

  /// Currency code
  final String? currency;

  /// Is important/starred
  final bool isImportant;

  /// Tags
  final List<String> tags;

  /// Additional metadata
  final Map<String, dynamic>? metadata;

  /// Created at timestamp
  final DateTime createdAt;

  const ActivityLog({
    required this.id,
    required this.tenantId,
    required this.farmerId,
    this.farmerName,
    required this.activityType,
    this.source = ActivitySource.manual,
    required this.title,
    this.titleAr,
    this.description,
    this.descriptionAr,
    this.interactionId,
    this.opportunityId,
    this.orderId,
    this.fieldId,
    this.taskId,
    this.userId,
    this.userName,
    this.agentId,
    this.agentName,
    this.previousValue,
    this.newValue,
    this.changedField,
    required this.activityAt,
    this.durationMinutes,
    this.amount,
    this.currency,
    this.isImportant = false,
    this.tags = const [],
    this.metadata,
    required this.createdAt,
  });

  // ============================================================
  // Computed Properties
  // ============================================================

  /// Display title (Arabic if available)
  String get displayTitle => titleAr ?? title;

  /// Display description (Arabic if available)
  String? get displayDescription => descriptionAr ?? description;

  /// Actor name (user or agent)
  String? get actorName => userName ?? agentName;

  /// Has change tracking
  bool get hasChangeTracking =>
      previousValue != null || newValue != null || changedField != null;

  /// Is related to interaction
  bool get hasInteraction => interactionId != null;

  /// Is related to opportunity
  bool get hasOpportunity => opportunityId != null;

  /// Is related to order
  bool get hasOrder => orderId != null;

  /// Is related to field
  bool get hasField => fieldId != null;

  /// Activity type in Arabic
  String get activityTypeAr {
    switch (activityType) {
      case ActivityType.call:
        return 'مكالمة';
      case ActivityType.visit:
        return 'زيارة';
      case ActivityType.message:
        return 'رسالة';
      case ActivityType.meeting:
        return 'اجتماع';
      case ActivityType.farmerCreated:
        return 'إنشاء مزارع';
      case ActivityType.farmerUpdated:
        return 'تحديث مزارع';
      case ActivityType.statusChanged:
        return 'تغيير الحالة';
      case ActivityType.segmentChanged:
        return 'تغيير الشريحة';
      case ActivityType.opportunityCreated:
        return 'إنشاء فرصة';
      case ActivityType.opportunityUpdated:
        return 'تحديث فرصة';
      case ActivityType.stageChanged:
        return 'تغيير المرحلة';
      case ActivityType.opportunityWon:
        return 'فرصة ناجحة';
      case ActivityType.opportunityLost:
        return 'فرصة خاسرة';
      case ActivityType.orderCreated:
        return 'إنشاء طلب';
      case ActivityType.orderCompleted:
        return 'اكتمال طلب';
      case ActivityType.paymentReceived:
        return 'استلام دفعة';
      case ActivityType.fieldAssigned:
        return 'تعيين حقل';
      case ActivityType.fieldVisit:
        return 'زيارة حقل';
      case ActivityType.noteAdded:
        return 'إضافة ملاحظة';
      case ActivityType.tagAdded:
        return 'إضافة وسم';
      case ActivityType.assignmentChanged:
        return 'تغيير التعيين';
      case ActivityType.reminderSet:
        return 'تعيين تذكير';
    }
  }

  /// Activity source in Arabic
  String get sourceAr {
    switch (source) {
      case ActivitySource.manual:
        return 'يدوي';
      case ActivitySource.system:
        return 'تلقائي';
      case ActivitySource.import:
        return 'استيراد';
      case ActivitySource.sync:
        return 'مزامنة';
      case ActivitySource.integration:
        return 'تكامل';
    }
  }

  /// Icon name for activity type
  String get activityIcon {
    switch (activityType) {
      case ActivityType.call:
        return 'phone';
      case ActivityType.visit:
        return 'location_on';
      case ActivityType.message:
        return 'chat';
      case ActivityType.meeting:
        return 'groups';
      case ActivityType.farmerCreated:
        return 'person_add';
      case ActivityType.farmerUpdated:
        return 'edit';
      case ActivityType.statusChanged:
        return 'toggle_on';
      case ActivityType.segmentChanged:
        return 'category';
      case ActivityType.opportunityCreated:
        return 'lightbulb';
      case ActivityType.opportunityUpdated:
        return 'update';
      case ActivityType.stageChanged:
        return 'trending_up';
      case ActivityType.opportunityWon:
        return 'emoji_events';
      case ActivityType.opportunityLost:
        return 'sentiment_dissatisfied';
      case ActivityType.orderCreated:
        return 'shopping_cart';
      case ActivityType.orderCompleted:
        return 'check_circle';
      case ActivityType.paymentReceived:
        return 'payments';
      case ActivityType.fieldAssigned:
        return 'landscape';
      case ActivityType.fieldVisit:
        return 'agriculture';
      case ActivityType.noteAdded:
        return 'note_add';
      case ActivityType.tagAdded:
        return 'label';
      case ActivityType.assignmentChanged:
        return 'assignment_ind';
      case ActivityType.reminderSet:
        return 'alarm';
    }
  }

  /// Activity category for grouping
  String get activityCategory {
    switch (activityType) {
      case ActivityType.call:
      case ActivityType.visit:
      case ActivityType.message:
      case ActivityType.meeting:
        return 'interaction';
      case ActivityType.farmerCreated:
      case ActivityType.farmerUpdated:
      case ActivityType.statusChanged:
      case ActivityType.segmentChanged:
        return 'farmer';
      case ActivityType.opportunityCreated:
      case ActivityType.opportunityUpdated:
      case ActivityType.stageChanged:
      case ActivityType.opportunityWon:
      case ActivityType.opportunityLost:
        return 'opportunity';
      case ActivityType.orderCreated:
      case ActivityType.orderCompleted:
      case ActivityType.paymentReceived:
        return 'sales';
      case ActivityType.fieldAssigned:
      case ActivityType.fieldVisit:
        return 'field';
      case ActivityType.noteAdded:
      case ActivityType.tagAdded:
      case ActivityType.assignmentChanged:
      case ActivityType.reminderSet:
        return 'system';
    }
  }

  /// Change description
  String? get changeDescription {
    if (!hasChangeTracking) return null;
    if (changedField != null && previousValue != null && newValue != null) {
      return '$changedField: $previousValue → $newValue';
    }
    return null;
  }

  // ============================================================
  // JSON Serialization
  // ============================================================

  /// Create from JSON
  factory ActivityLog.fromJson(Map<String, dynamic> json) {
    final now = DateTime.now();

    return ActivityLog(
      id: json['id'] as String? ?? json['_id'] as String,
      tenantId: json['tenant_id'] as String? ?? '',
      farmerId: json['farmer_id'] as String,
      farmerName: json['farmer_name'] as String?,
      activityType: _parseActivityType(json['activity_type'] as String?),
      source: _parseSource(json['source'] as String?),
      title: json['title'] as String? ?? '',
      titleAr: json['title_ar'] as String?,
      description: json['description'] as String?,
      descriptionAr: json['description_ar'] as String?,
      interactionId: json['interaction_id'] as String?,
      opportunityId: json['opportunity_id'] as String?,
      orderId: json['order_id'] as String?,
      fieldId: json['field_id'] as String?,
      taskId: json['task_id'] as String?,
      userId: json['user_id'] as String?,
      userName: json['user_name'] as String?,
      agentId: json['agent_id'] as String?,
      agentName: json['agent_name'] as String?,
      previousValue: json['previous_value'] as String?,
      newValue: json['new_value'] as String?,
      changedField: json['changed_field'] as String?,
      activityAt: json['activity_at'] != null
          ? DateTime.parse(json['activity_at'] as String)
          : now,
      durationMinutes: json['duration_minutes'] as int?,
      amount: (json['amount'] as num?)?.toDouble(),
      currency: json['currency'] as String?,
      isImportant: json['is_important'] as bool? ?? false,
      tags: (json['tags'] as List?)?.cast<String>() ?? [],
      metadata: json['metadata'] as Map<String, dynamic>?,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : now,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() => {
        'id': id,
        'tenant_id': tenantId,
        'farmer_id': farmerId,
        'farmer_name': farmerName,
        'activity_type': activityType.name,
        'source': source.name,
        'title': title,
        'title_ar': titleAr,
        'description': description,
        'description_ar': descriptionAr,
        'interaction_id': interactionId,
        'opportunity_id': opportunityId,
        'order_id': orderId,
        'field_id': fieldId,
        'task_id': taskId,
        'user_id': userId,
        'user_name': userName,
        'agent_id': agentId,
        'agent_name': agentName,
        'previous_value': previousValue,
        'new_value': newValue,
        'changed_field': changedField,
        'activity_at': activityAt.toIso8601String(),
        'duration_minutes': durationMinutes,
        'amount': amount,
        'currency': currency,
        'is_important': isImportant,
        'tags': tags,
        'metadata': metadata,
        'created_at': createdAt.toIso8601String(),
      };

  /// Copy with
  ActivityLog copyWith({
    String? id,
    String? tenantId,
    String? farmerId,
    String? farmerName,
    ActivityType? activityType,
    ActivitySource? source,
    String? title,
    String? titleAr,
    String? description,
    String? descriptionAr,
    String? interactionId,
    String? opportunityId,
    String? orderId,
    String? fieldId,
    String? taskId,
    String? userId,
    String? userName,
    String? agentId,
    String? agentName,
    String? previousValue,
    String? newValue,
    String? changedField,
    DateTime? activityAt,
    int? durationMinutes,
    double? amount,
    String? currency,
    bool? isImportant,
    List<String>? tags,
    Map<String, dynamic>? metadata,
    DateTime? createdAt,
  }) {
    return ActivityLog(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      farmerId: farmerId ?? this.farmerId,
      farmerName: farmerName ?? this.farmerName,
      activityType: activityType ?? this.activityType,
      source: source ?? this.source,
      title: title ?? this.title,
      titleAr: titleAr ?? this.titleAr,
      description: description ?? this.description,
      descriptionAr: descriptionAr ?? this.descriptionAr,
      interactionId: interactionId ?? this.interactionId,
      opportunityId: opportunityId ?? this.opportunityId,
      orderId: orderId ?? this.orderId,
      fieldId: fieldId ?? this.fieldId,
      taskId: taskId ?? this.taskId,
      userId: userId ?? this.userId,
      userName: userName ?? this.userName,
      agentId: agentId ?? this.agentId,
      agentName: agentName ?? this.agentName,
      previousValue: previousValue ?? this.previousValue,
      newValue: newValue ?? this.newValue,
      changedField: changedField ?? this.changedField,
      activityAt: activityAt ?? this.activityAt,
      durationMinutes: durationMinutes ?? this.durationMinutes,
      amount: amount ?? this.amount,
      currency: currency ?? this.currency,
      isImportant: isImportant ?? this.isImportant,
      tags: tags ?? this.tags,
      metadata: metadata ?? this.metadata,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ActivityLog && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() => 'ActivityLog($id: $activityTypeAr - $title)';
}

// ============================================================
// CRM Statistics Models
// ============================================================

/// CRM Statistics Summary
/// ملخص إحصائيات CRM
class CrmStats {
  final int totalFarmers;
  final int activeFarmers;
  final int newFarmersThisMonth;
  final int totalInteractions;
  final int interactionsThisWeek;
  final int pendingFollowUps;
  final int overdueFollowUps;
  final int totalOpportunities;
  final int openOpportunities;
  final double pipelineValue;
  final double closedWonValue;
  final double conversionRate;

  const CrmStats({
    this.totalFarmers = 0,
    this.activeFarmers = 0,
    this.newFarmersThisMonth = 0,
    this.totalInteractions = 0,
    this.interactionsThisWeek = 0,
    this.pendingFollowUps = 0,
    this.overdueFollowUps = 0,
    this.totalOpportunities = 0,
    this.openOpportunities = 0,
    this.pipelineValue = 0,
    this.closedWonValue = 0,
    this.conversionRate = 0,
  });

  factory CrmStats.fromJson(Map<String, dynamic> json) {
    return CrmStats(
      totalFarmers: json['total_farmers'] as int? ?? 0,
      activeFarmers: json['active_farmers'] as int? ?? 0,
      newFarmersThisMonth: json['new_farmers_this_month'] as int? ?? 0,
      totalInteractions: json['total_interactions'] as int? ?? 0,
      interactionsThisWeek: json['interactions_this_week'] as int? ?? 0,
      pendingFollowUps: json['pending_follow_ups'] as int? ?? 0,
      overdueFollowUps: json['overdue_follow_ups'] as int? ?? 0,
      totalOpportunities: json['total_opportunities'] as int? ?? 0,
      openOpportunities: json['open_opportunities'] as int? ?? 0,
      pipelineValue: (json['pipeline_value'] as num?)?.toDouble() ?? 0,
      closedWonValue: (json['closed_won_value'] as num?)?.toDouble() ?? 0,
      conversionRate: (json['conversion_rate'] as num?)?.toDouble() ?? 0,
    );
  }

  Map<String, dynamic> toJson() => {
        'total_farmers': totalFarmers,
        'active_farmers': activeFarmers,
        'new_farmers_this_month': newFarmersThisMonth,
        'total_interactions': totalInteractions,
        'interactions_this_week': interactionsThisWeek,
        'pending_follow_ups': pendingFollowUps,
        'overdue_follow_ups': overdueFollowUps,
        'total_opportunities': totalOpportunities,
        'open_opportunities': openOpportunities,
        'pipeline_value': pipelineValue,
        'closed_won_value': closedWonValue,
        'conversion_rate': conversionRate,
      };
}

/// Farmer Analytics
/// تحليلات المزارع
class FarmerAnalytics {
  final String farmerId;
  final int totalInteractions;
  final int callCount;
  final int visitCount;
  final int messageCount;
  final DateTime? lastInteractionAt;
  final int avgResponseDays;
  final int totalOpportunities;
  final int wonOpportunities;
  final double totalPurchaseValue;
  final double avgOrderValue;
  final List<Map<String, dynamic>> interactionTrend;
  final Map<String, int> interactionByType;

  const FarmerAnalytics({
    required this.farmerId,
    this.totalInteractions = 0,
    this.callCount = 0,
    this.visitCount = 0,
    this.messageCount = 0,
    this.lastInteractionAt,
    this.avgResponseDays = 0,
    this.totalOpportunities = 0,
    this.wonOpportunities = 0,
    this.totalPurchaseValue = 0,
    this.avgOrderValue = 0,
    this.interactionTrend = const [],
    this.interactionByType = const {},
  });

  factory FarmerAnalytics.fromJson(Map<String, dynamic> json) {
    return FarmerAnalytics(
      farmerId: json['farmer_id'] as String,
      totalInteractions: json['total_interactions'] as int? ?? 0,
      callCount: json['call_count'] as int? ?? 0,
      visitCount: json['visit_count'] as int? ?? 0,
      messageCount: json['message_count'] as int? ?? 0,
      lastInteractionAt: json['last_interaction_at'] != null
          ? DateTime.parse(json['last_interaction_at'] as String)
          : null,
      avgResponseDays: json['avg_response_days'] as int? ?? 0,
      totalOpportunities: json['total_opportunities'] as int? ?? 0,
      wonOpportunities: json['won_opportunities'] as int? ?? 0,
      totalPurchaseValue: (json['total_purchase_value'] as num?)?.toDouble() ?? 0,
      avgOrderValue: (json['avg_order_value'] as num?)?.toDouble() ?? 0,
      interactionTrend:
          (json['interaction_trend'] as List?)?.cast<Map<String, dynamic>>() ?? [],
      interactionByType: Map<String, int>.from((json['interaction_by_type'] as Map?) ?? {}),
    );
  }

  Map<String, dynamic> toJson() => {
        'farmer_id': farmerId,
        'total_interactions': totalInteractions,
        'call_count': callCount,
        'visit_count': visitCount,
        'message_count': messageCount,
        'last_interaction_at': lastInteractionAt?.toIso8601String(),
        'avg_response_days': avgResponseDays,
        'total_opportunities': totalOpportunities,
        'won_opportunities': wonOpportunities,
        'total_purchase_value': totalPurchaseValue,
        'avg_order_value': avgOrderValue,
        'interaction_trend': interactionTrend,
        'interaction_by_type': interactionByType,
      };

  /// Win rate percentage
  double get winRate =>
      totalOpportunities > 0 ? (wonOpportunities / totalOpportunities) * 100 : 0;

  /// Engagement score (0-100) computed from interaction frequency and types
  double get engagementScore {
    if (totalInteractions == 0) return 0;
    final recency = daysSinceLastInteraction != null
        ? (30 - (daysSinceLastInteraction! > 30 ? 30 : daysSinceLastInteraction!)) / 30 * 40
        : 0.0;
    final frequency = (totalInteractions > 20 ? 20 : totalInteractions) / 20 * 30;
    final diversity = ((callCount > 0 ? 1 : 0) + (visitCount > 0 ? 1 : 0) + (messageCount > 0 ? 1 : 0)) / 3 * 30;
    return recency + frequency + diversity;
  }

  /// Days since last interaction (null if no interaction)
  int? get daysSinceLastInteraction {
    if (lastInteractionAt == null) return null;
    return DateTime.now().difference(lastInteractionAt!).inDays;
  }

  /// Average interaction duration (placeholder, derived from avgResponseDays)
  double? get averageInteractionDuration => avgResponseDays > 0 ? avgResponseDays.toDouble() : null;

  /// Success rate as fraction (0.0-1.0)
  double get successRate =>
      totalOpportunities > 0 ? wonOpportunities / totalOpportunities : 0;

  /// Interactions grouped by type
  Map<String, int> get interactionsByType => interactionByType;

  /// Interactions grouped by outcome
  Map<String, int> get interactionsByOutcome => {
        'won': wonOpportunities,
        'total': totalOpportunities,
        'lost': totalOpportunities - wonOpportunities,
      };

  /// Monthly activity data from interaction trend as month -> count map
  Map<String, dynamic> get monthlyActivity {
    final result = <String, dynamic>{};
    for (final entry in interactionTrend) {
      final month = entry['month'] as String? ?? entry['date'] as String? ?? '';
      final count = entry['count'] ?? entry['value'] ?? 0;
      if (month.isNotEmpty) result[month] = count;
    }
    return result;
  }

  /// Preferred contact time (placeholder)
  String? get preferredContactTime => null;

  /// Preferred communication channel
  String? get preferredChannel {
    if (callCount >= visitCount && callCount >= messageCount) return 'اتصال';
    if (visitCount >= callCount && visitCount >= messageCount) return 'زيارة';
    if (messageCount > 0) return 'رسالة';
    return null;
  }

  /// Response rate (fraction 0.0-1.0)
  double get responseRate =>
      totalInteractions > 0 ? (totalInteractions - avgResponseDays).clamp(0, totalInteractions) / totalInteractions : 0;

  /// Average response time in days
  int? get averageResponseTime => avgResponseDays > 0 ? avgResponseDays : null;
}

// Helper functions
ActivityType _parseActivityType(String? type) {
  switch (type?.toLowerCase()) {
    case 'call':
      return ActivityType.call;
    case 'visit':
      return ActivityType.visit;
    case 'message':
      return ActivityType.message;
    case 'meeting':
      return ActivityType.meeting;
    case 'farmercreated':
    case 'farmer_created':
      return ActivityType.farmerCreated;
    case 'farmerupdated':
    case 'farmer_updated':
      return ActivityType.farmerUpdated;
    case 'statuschanged':
    case 'status_changed':
      return ActivityType.statusChanged;
    case 'segmentchanged':
    case 'segment_changed':
      return ActivityType.segmentChanged;
    case 'opportunitycreated':
    case 'opportunity_created':
      return ActivityType.opportunityCreated;
    case 'opportunityupdated':
    case 'opportunity_updated':
      return ActivityType.opportunityUpdated;
    case 'stagechanged':
    case 'stage_changed':
      return ActivityType.stageChanged;
    case 'opportunitywon':
    case 'opportunity_won':
      return ActivityType.opportunityWon;
    case 'opportunitylost':
    case 'opportunity_lost':
      return ActivityType.opportunityLost;
    case 'ordercreated':
    case 'order_created':
      return ActivityType.orderCreated;
    case 'ordercompleted':
    case 'order_completed':
      return ActivityType.orderCompleted;
    case 'paymentreceived':
    case 'payment_received':
      return ActivityType.paymentReceived;
    case 'fieldassigned':
    case 'field_assigned':
      return ActivityType.fieldAssigned;
    case 'fieldvisit':
    case 'field_visit':
      return ActivityType.fieldVisit;
    case 'noteadded':
    case 'note_added':
      return ActivityType.noteAdded;
    case 'tagadded':
    case 'tag_added':
      return ActivityType.tagAdded;
    case 'assignmentchanged':
    case 'assignment_changed':
      return ActivityType.assignmentChanged;
    case 'reminderset':
    case 'reminder_set':
      return ActivityType.reminderSet;
    default:
      return ActivityType.noteAdded;
  }
}

ActivitySource _parseSource(String? source) {
  switch (source?.toLowerCase()) {
    case 'system':
      return ActivitySource.system;
    case 'import':
      return ActivitySource.import;
    case 'sync':
      return ActivitySource.sync;
    case 'integration':
      return ActivitySource.integration;
    case 'manual':
    default:
      return ActivitySource.manual;
  }
}
