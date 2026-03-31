/// Opportunity Model
/// نموذج الفرصة البيعية
///
/// Represents a potential sale or service opportunity with a farmer
library;

/// Opportunity stage
/// مرحلة الفرصة
enum OpportunityStage {
  lead,           // عميل محتمل
  qualified,      // مؤهل
  proposal,       // عرض سعر
  negotiation,    // تفاوض
  closedWon,      // مغلقة - ربح
  closedLost,     // مغلقة - خسارة
}

/// Opportunity priority
/// أولوية الفرصة
enum OpportunityPriority {
  low,      // منخفضة
  medium,   // متوسطة
  high,     // عالية
  urgent,   // عاجلة
}

/// Opportunity type
/// نوع الفرصة
enum OpportunityType {
  newSale,        // بيع جديد
  crossSell,      // بيع متقاطع
  upSell,         // بيع إضافي
  renewal,        // تجديد
  service,        // خدمة
  subscription,   // اشتراك
  partnership,    // شراكة
}

/// Loss reason
/// سبب الخسارة
enum LossReason {
  price,          // السعر
  competition,    // المنافسة
  timing,         // التوقيت
  noNeed,         // لا يحتاج
  noResponse,     // لا استجابة
  other,          // أخرى
}

/// Opportunity Model
/// نموذج الفرصة البيعية
class Opportunity {
  /// Unique identifier
  final String id;

  /// Tenant ID for multi-tenancy
  final String tenantId;

  /// Remote server ID
  final String? remoteId;

  /// Farmer ID
  final String farmerId;

  /// Farmer name (for display)
  final String? farmerName;

  /// Opportunity name/title
  final String name;

  /// Name in Arabic
  final String? nameAr;

  /// Description
  final String? description;

  /// Description in Arabic
  final String? descriptionAr;

  /// Opportunity type
  final OpportunityType type;

  /// Current stage
  final OpportunityStage stage;

  /// Priority level
  final OpportunityPriority priority;

  // ─────────────────────────────────────────────────────────────────────────────
  // Financial Information
  // ─────────────────────────────────────────────────────────────────────────────

  /// Expected amount/value
  final double expectedAmount;

  /// Currency code (default: YER for Yemeni Rial)
  final String currency;

  /// Probability percentage (0-100)
  final int probability;

  /// Weighted value (expectedAmount * probability / 100)
  double get weightedValue => expectedAmount * probability / 100;

  /// Actual amount (when closed)
  final double? actualAmount;

  // ─────────────────────────────────────────────────────────────────────────────
  // Products/Services
  // ─────────────────────────────────────────────────────────────────────────────

  /// Product/service IDs
  final List<String> productIds;

  /// Product names (for display)
  final List<String> productNames;

  /// Total quantity
  final int? quantity;

  /// Unit (bags, kg, liters, etc.)
  final String? unit;

  // ─────────────────────────────────────────────────────────────────────────────
  // Dates
  // ─────────────────────────────────────────────────────────────────────────────

  /// Expected close date
  final DateTime? expectedCloseDate;

  /// Actual close date
  final DateTime? actualCloseDate;

  /// Next follow-up date
  final DateTime? nextFollowUpAt;

  /// Last activity date
  final DateTime? lastActivityAt;

  // ─────────────────────────────────────────────────────────────────────────────
  // Assignment
  // ─────────────────────────────────────────────────────────────────────────────

  /// Assigned agent/salesperson ID
  final String? assignedAgentId;

  /// Assigned agent name
  final String? assignedAgentName;

  /// Lead source
  final String? leadSource;

  /// Campaign ID (if from marketing campaign)
  final String? campaignId;

  // ─────────────────────────────────────────────────────────────────────────────
  // Closure Information
  // ─────────────────────────────────────────────────────────────────────────────

  /// Loss reason (if stage is closedLost)
  final LossReason? lossReason;

  /// Competitor who won (if applicable)
  final String? competitorName;

  /// Close notes
  final String? closeNotes;

  // ─────────────────────────────────────────────────────────────────────────────
  // Related Entities
  // ─────────────────────────────────────────────────────────────────────────────

  /// Related field IDs
  final List<String> fieldIds;

  /// Related order ID (if converted)
  final String? orderId;

  /// Related quote/proposal ID
  final String? quoteId;

  // ─────────────────────────────────────────────────────────────────────────────
  // Metadata
  // ─────────────────────────────────────────────────────────────────────────────

  /// Tags for filtering
  final List<String> tags;

  /// Custom notes
  final String? notes;

  /// Is synced with server
  final bool synced;

  /// Is soft deleted
  final bool isDeleted;

  /// Created at timestamp
  final DateTime createdAt;

  /// Updated at timestamp
  final DateTime updatedAt;

  /// Additional metadata
  final Map<String, dynamic>? metadata;

  const Opportunity({
    required this.id,
    required this.tenantId,
    this.remoteId,
    required this.farmerId,
    this.farmerName,
    required this.name,
    this.nameAr,
    this.description,
    this.descriptionAr,
    this.type = OpportunityType.newSale,
    this.stage = OpportunityStage.lead,
    this.priority = OpportunityPriority.medium,
    required this.expectedAmount,
    this.currency = 'YER',
    this.probability = 50,
    this.actualAmount,
    this.productIds = const [],
    this.productNames = const [],
    this.quantity,
    this.unit,
    this.expectedCloseDate,
    this.actualCloseDate,
    this.nextFollowUpAt,
    this.lastActivityAt,
    this.assignedAgentId,
    this.assignedAgentName,
    this.leadSource,
    this.campaignId,
    this.lossReason,
    this.competitorName,
    this.closeNotes,
    this.fieldIds = const [],
    this.orderId,
    this.quoteId,
    this.tags = const [],
    this.notes,
    this.synced = false,
    this.isDeleted = false,
    required this.createdAt,
    required this.updatedAt,
    this.metadata,
  });

  // ============================================================
  // Computed Properties
  // ============================================================

  /// Display name (Arabic if available)
  String get displayName => nameAr ?? name;

  /// Display description (Arabic if available)
  String? get displayDescription => descriptionAr ?? description;

  /// Is opportunity open (not closed)
  bool get isOpen =>
      stage != OpportunityStage.closedWon && stage != OpportunityStage.closedLost;

  /// Is opportunity won
  bool get isWon => stage == OpportunityStage.closedWon;

  /// Is opportunity lost
  bool get isLost => stage == OpportunityStage.closedLost;

  /// Days in current stage
  int get daysInStage => DateTime.now().difference(updatedAt).inDays;

  /// Days until expected close
  int? get daysUntilClose {
    if (expectedCloseDate == null) return null;
    return expectedCloseDate!.difference(DateTime.now()).inDays;
  }

  /// Is overdue (past expected close date and still open)
  bool get isOverdue =>
      isOpen && expectedCloseDate != null && expectedCloseDate!.isBefore(DateTime.now());

  /// Has products
  bool get hasProducts => productIds.isNotEmpty;

  /// Stage in Arabic
  String get stageAr {
    switch (stage) {
      case OpportunityStage.lead:
        return 'عميل محتمل';
      case OpportunityStage.qualified:
        return 'مؤهل';
      case OpportunityStage.proposal:
        return 'عرض سعر';
      case OpportunityStage.negotiation:
        return 'تفاوض';
      case OpportunityStage.closedWon:
        return 'مغلقة - ربح';
      case OpportunityStage.closedLost:
        return 'مغلقة - خسارة';
    }
  }

  /// Priority in Arabic
  String get priorityAr {
    switch (priority) {
      case OpportunityPriority.low:
        return 'منخفضة';
      case OpportunityPriority.medium:
        return 'متوسطة';
      case OpportunityPriority.high:
        return 'عالية';
      case OpportunityPriority.urgent:
        return 'عاجلة';
    }
  }

  /// Type in Arabic
  String get typeAr {
    switch (type) {
      case OpportunityType.newSale:
        return 'بيع جديد';
      case OpportunityType.crossSell:
        return 'بيع متقاطع';
      case OpportunityType.upSell:
        return 'بيع إضافي';
      case OpportunityType.renewal:
        return 'تجديد';
      case OpportunityType.service:
        return 'خدمة';
      case OpportunityType.subscription:
        return 'اشتراك';
      case OpportunityType.partnership:
        return 'شراكة';
    }
  }

  /// Loss reason in Arabic
  String? get lossReasonAr {
    if (lossReason == null) return null;
    switch (lossReason!) {
      case LossReason.price:
        return 'السعر';
      case LossReason.competition:
        return 'المنافسة';
      case LossReason.timing:
        return 'التوقيت';
      case LossReason.noNeed:
        return 'لا يحتاج';
      case LossReason.noResponse:
        return 'لا استجابة';
      case LossReason.other:
        return 'أخرى';
    }
  }

  /// Formatted expected amount
  String get formattedExpectedAmount => '$expectedAmount $currency';

  /// Formatted actual amount
  String? get formattedActualAmount =>
      actualAmount != null ? '$actualAmount $currency' : null;

  /// Stage progress percentage (for pipeline visualization)
  int get stageProgress {
    switch (stage) {
      case OpportunityStage.lead:
        return 10;
      case OpportunityStage.qualified:
        return 30;
      case OpportunityStage.proposal:
        return 50;
      case OpportunityStage.negotiation:
        return 75;
      case OpportunityStage.closedWon:
        return 100;
      case OpportunityStage.closedLost:
        return 0;
    }
  }

  // ============================================================
  // JSON Serialization
  // ============================================================

  /// Create from JSON
  factory Opportunity.fromJson(Map<String, dynamic> json) {
    final now = DateTime.now();

    return Opportunity(
      id: json['id'] as String? ?? json['_id'] as String,
      tenantId: json['tenant_id'] as String? ?? '',
      remoteId: json['remote_id'] as String?,
      farmerId: json['farmer_id'] as String,
      farmerName: json['farmer_name'] as String?,
      name: json['name'] as String? ?? '',
      nameAr: json['name_ar'] as String?,
      description: json['description'] as String?,
      descriptionAr: json['description_ar'] as String?,
      type: _parseType(json['type'] as String?),
      stage: _parseStage(json['stage'] as String?),
      priority: _parsePriority(json['priority'] as String?),
      expectedAmount: (json['expected_amount'] as num?)?.toDouble() ?? 0,
      currency: json['currency'] as String? ?? 'YER',
      probability: json['probability'] as int? ?? 50,
      actualAmount: (json['actual_amount'] as num?)?.toDouble(),
      productIds: (json['product_ids'] as List?)?.cast<String>() ?? [],
      productNames: (json['product_names'] as List?)?.cast<String>() ?? [],
      quantity: json['quantity'] as int?,
      unit: json['unit'] as String?,
      expectedCloseDate: json['expected_close_date'] != null
          ? DateTime.tryParse(json['expected_close_date'] as String) ?? DateTime.now()
          : null,
      actualCloseDate: json['actual_close_date'] != null
          ? DateTime.tryParse(json['actual_close_date'] as String) ?? DateTime.now()
          : null,
      nextFollowUpAt: json['next_follow_up_at'] != null
          ? DateTime.tryParse(json['next_follow_up_at'] as String) ?? DateTime.now()
          : null,
      lastActivityAt: json['last_activity_at'] != null
          ? DateTime.tryParse(json['last_activity_at'] as String) ?? DateTime.now()
          : null,
      assignedAgentId: json['assigned_agent_id'] as String?,
      assignedAgentName: json['assigned_agent_name'] as String?,
      leadSource: json['lead_source'] as String?,
      campaignId: json['campaign_id'] as String?,
      lossReason: _parseLossReason(json['loss_reason'] as String?),
      competitorName: json['competitor_name'] as String?,
      closeNotes: json['close_notes'] as String?,
      fieldIds: (json['field_ids'] as List?)?.cast<String>() ?? [],
      orderId: json['order_id'] as String?,
      quoteId: json['quote_id'] as String?,
      tags: (json['tags'] as List?)?.cast<String>() ?? [],
      notes: json['notes'] as String?,
      synced: json['synced'] as bool? ?? true,
      isDeleted: json['is_deleted'] as bool? ?? false,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String) ?? DateTime.now()
          : now,
      updatedAt: json['updated_at'] != null
          ? DateTime.tryParse(json['updated_at'] as String) ?? DateTime.now()
          : now,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() => {
        'id': id,
        'tenant_id': tenantId,
        'remote_id': remoteId,
        'farmer_id': farmerId,
        'farmer_name': farmerName,
        'name': name,
        'name_ar': nameAr,
        'description': description,
        'description_ar': descriptionAr,
        'type': type.name,
        'stage': stage.name,
        'priority': priority.name,
        'expected_amount': expectedAmount,
        'currency': currency,
        'probability': probability,
        'actual_amount': actualAmount,
        'product_ids': productIds,
        'product_names': productNames,
        'quantity': quantity,
        'unit': unit,
        'expected_close_date': expectedCloseDate?.toIso8601String(),
        'actual_close_date': actualCloseDate?.toIso8601String(),
        'next_follow_up_at': nextFollowUpAt?.toIso8601String(),
        'last_activity_at': lastActivityAt?.toIso8601String(),
        'assigned_agent_id': assignedAgentId,
        'assigned_agent_name': assignedAgentName,
        'lead_source': leadSource,
        'campaign_id': campaignId,
        'loss_reason': lossReason?.name,
        'competitor_name': competitorName,
        'close_notes': closeNotes,
        'field_ids': fieldIds,
        'order_id': orderId,
        'quote_id': quoteId,
        'tags': tags,
        'notes': notes,
        'synced': synced,
        'is_deleted': isDeleted,
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
        'metadata': metadata,
      };

  /// Copy with
  Opportunity copyWith({
    String? id,
    String? tenantId,
    String? remoteId,
    String? farmerId,
    String? farmerName,
    String? name,
    String? nameAr,
    String? description,
    String? descriptionAr,
    OpportunityType? type,
    OpportunityStage? stage,
    OpportunityPriority? priority,
    double? expectedAmount,
    String? currency,
    int? probability,
    double? actualAmount,
    List<String>? productIds,
    List<String>? productNames,
    int? quantity,
    String? unit,
    DateTime? expectedCloseDate,
    DateTime? actualCloseDate,
    DateTime? nextFollowUpAt,
    DateTime? lastActivityAt,
    String? assignedAgentId,
    String? assignedAgentName,
    String? leadSource,
    String? campaignId,
    LossReason? lossReason,
    String? competitorName,
    String? closeNotes,
    List<String>? fieldIds,
    String? orderId,
    String? quoteId,
    List<String>? tags,
    String? notes,
    bool? synced,
    bool? isDeleted,
    DateTime? createdAt,
    DateTime? updatedAt,
    Map<String, dynamic>? metadata,
  }) {
    return Opportunity(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      remoteId: remoteId ?? this.remoteId,
      farmerId: farmerId ?? this.farmerId,
      farmerName: farmerName ?? this.farmerName,
      name: name ?? this.name,
      nameAr: nameAr ?? this.nameAr,
      description: description ?? this.description,
      descriptionAr: descriptionAr ?? this.descriptionAr,
      type: type ?? this.type,
      stage: stage ?? this.stage,
      priority: priority ?? this.priority,
      expectedAmount: expectedAmount ?? this.expectedAmount,
      currency: currency ?? this.currency,
      probability: probability ?? this.probability,
      actualAmount: actualAmount ?? this.actualAmount,
      productIds: productIds ?? this.productIds,
      productNames: productNames ?? this.productNames,
      quantity: quantity ?? this.quantity,
      unit: unit ?? this.unit,
      expectedCloseDate: expectedCloseDate ?? this.expectedCloseDate,
      actualCloseDate: actualCloseDate ?? this.actualCloseDate,
      nextFollowUpAt: nextFollowUpAt ?? this.nextFollowUpAt,
      lastActivityAt: lastActivityAt ?? this.lastActivityAt,
      assignedAgentId: assignedAgentId ?? this.assignedAgentId,
      assignedAgentName: assignedAgentName ?? this.assignedAgentName,
      leadSource: leadSource ?? this.leadSource,
      campaignId: campaignId ?? this.campaignId,
      lossReason: lossReason ?? this.lossReason,
      competitorName: competitorName ?? this.competitorName,
      closeNotes: closeNotes ?? this.closeNotes,
      fieldIds: fieldIds ?? this.fieldIds,
      orderId: orderId ?? this.orderId,
      quoteId: quoteId ?? this.quoteId,
      tags: tags ?? this.tags,
      notes: notes ?? this.notes,
      synced: synced ?? this.synced,
      isDeleted: isDeleted ?? this.isDeleted,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      metadata: metadata ?? this.metadata,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Opportunity && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() =>
      'Opportunity($id: $name, Stage: $stageAr, Value: $formattedExpectedAmount)';
}

// Helper functions
OpportunityType _parseType(String? type) {
  switch (type?.toLowerCase()) {
    case 'crosssell':
    case 'cross_sell':
      return OpportunityType.crossSell;
    case 'upsell':
    case 'up_sell':
      return OpportunityType.upSell;
    case 'renewal':
      return OpportunityType.renewal;
    case 'service':
      return OpportunityType.service;
    case 'subscription':
      return OpportunityType.subscription;
    case 'partnership':
      return OpportunityType.partnership;
    case 'newsale':
    case 'new_sale':
    default:
      return OpportunityType.newSale;
  }
}

OpportunityStage _parseStage(String? stage) {
  switch (stage?.toLowerCase()) {
    case 'qualified':
      return OpportunityStage.qualified;
    case 'proposal':
      return OpportunityStage.proposal;
    case 'negotiation':
      return OpportunityStage.negotiation;
    case 'closedwon':
    case 'closed_won':
    case 'won':
      return OpportunityStage.closedWon;
    case 'closedlost':
    case 'closed_lost':
    case 'lost':
      return OpportunityStage.closedLost;
    case 'lead':
    default:
      return OpportunityStage.lead;
  }
}

OpportunityPriority _parsePriority(String? priority) {
  switch (priority?.toLowerCase()) {
    case 'low':
      return OpportunityPriority.low;
    case 'high':
      return OpportunityPriority.high;
    case 'urgent':
      return OpportunityPriority.urgent;
    case 'medium':
    default:
      return OpportunityPriority.medium;
  }
}

LossReason? _parseLossReason(String? reason) {
  if (reason == null) return null;
  switch (reason.toLowerCase()) {
    case 'price':
      return LossReason.price;
    case 'competition':
      return LossReason.competition;
    case 'timing':
      return LossReason.timing;
    case 'noneed':
    case 'no_need':
      return LossReason.noNeed;
    case 'noresponse':
    case 'no_response':
      return LossReason.noResponse;
    case 'other':
    default:
      return LossReason.other;
  }
}
