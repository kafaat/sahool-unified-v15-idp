/// Interaction Model
/// نموذج التفاعل
///
/// Represents an interaction with a farmer (call, visit, message, note)
library;

/// Interaction type
/// نوع التفاعل
enum InteractionType {
  call,         // مكالمة هاتفية
  visit,        // زيارة ميدانية
  whatsapp,     // رسالة واتساب
  sms,          // رسالة نصية
  email,        // بريد إلكتروني
  meeting,      // اجتماع
  note,         // ملاحظة
  task,         // مهمة
  demo,         // عرض توضيحي
  training,     // تدريب
  complaint,    // شكوى
  feedback,     // ملاحظات
  sale,         // بيع
  followUp,     // متابعة
}

/// Interaction outcome
/// نتيجة التفاعل
enum InteractionOutcome {
  successful,   // ناجح
  noAnswer,     // لم يرد
  busy,         // مشغول
  rescheduled,  // تم إعادة الجدولة
  notInterested,// غير مهتم
  interested,   // مهتم
  converted,    // تم التحويل
  pending,      // قيد الانتظار
  cancelled,    // ملغي
}

/// Interaction direction
/// اتجاه التفاعل
enum InteractionDirection {
  outbound,     // صادر (من الوكيل للمزارع)
  inbound,      // وارد (من المزارع للوكيل)
}

/// Interaction Model
/// نموذج التفاعل مع المزارع
class Interaction {
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

  /// Interaction type
  final InteractionType type;

  /// Interaction direction
  final InteractionDirection direction;

  /// Interaction outcome
  final InteractionOutcome outcome;

  /// Subject/title
  final String subject;

  /// Subject in Arabic
  final String? subjectAr;

  /// Detailed description/notes
  final String? description;

  /// Description in Arabic
  final String? descriptionAr;

  /// Duration in minutes (for calls/visits)
  final int? durationMinutes;

  /// Interaction date and time
  final DateTime interactionAt;

  /// Scheduled follow-up date
  final DateTime? followUpAt;

  /// Follow-up notes
  final String? followUpNotes;

  /// Agent/salesperson who made the interaction
  final String? agentId;

  /// Agent name
  final String? agentName;

  // ─────────────────────────────────────────────────────────────────────────────
  // Location Information (for visits)
  // ─────────────────────────────────────────────────────────────────────────────

  /// GPS latitude (for field visits)
  final double? latitude;

  /// GPS longitude (for field visits)
  final double? longitude;

  /// Location name/address
  final String? locationName;

  /// Field ID (if visiting a specific field)
  final String? fieldId;

  // ─────────────────────────────────────────────────────────────────────────────
  // Attachments
  // ─────────────────────────────────────────────────────────────────────────────

  /// Attached photos (URLs)
  final List<String> photos;

  /// Attached documents (URLs)
  final List<String> documents;

  /// Voice recording URL
  final String? voiceRecordingUrl;

  // ─────────────────────────────────────────────────────────────────────────────
  // Related Entities
  // ─────────────────────────────────────────────────────────────────────────────

  /// Related opportunity ID
  final String? opportunityId;

  /// Related task ID
  final String? taskId;

  /// Related order ID
  final String? orderId;

  // ─────────────────────────────────────────────────────────────────────────────
  // Metadata
  // ─────────────────────────────────────────────────────────────────────────────

  /// Tags for filtering
  final List<String> tags;

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

  const Interaction({
    required this.id,
    required this.tenantId,
    this.remoteId,
    required this.farmerId,
    this.farmerName,
    required this.type,
    this.direction = InteractionDirection.outbound,
    this.outcome = InteractionOutcome.pending,
    required this.subject,
    this.subjectAr,
    this.description,
    this.descriptionAr,
    this.durationMinutes,
    required this.interactionAt,
    this.followUpAt,
    this.followUpNotes,
    this.agentId,
    this.agentName,
    this.latitude,
    this.longitude,
    this.locationName,
    this.fieldId,
    this.photos = const [],
    this.documents = const [],
    this.voiceRecordingUrl,
    this.opportunityId,
    this.taskId,
    this.orderId,
    this.tags = const [],
    this.synced = false,
    this.isDeleted = false,
    required this.createdAt,
    required this.updatedAt,
    this.metadata,
  });

  // ============================================================
  // Computed Properties
  // ============================================================

  /// Display subject (Arabic if available)
  String get displaySubject => subjectAr ?? subject;

  /// Display description (Arabic if available)
  String? get displayDescription => descriptionAr ?? description;

  /// Has location coordinates
  bool get hasCoordinates => latitude != null && longitude != null;

  /// Has follow-up scheduled
  bool get hasFollowUp => followUpAt != null;

  /// Is follow-up overdue
  bool get isFollowUpOverdue =>
      followUpAt != null && followUpAt!.isBefore(DateTime.now());

  /// Has attachments
  bool get hasAttachments =>
      photos.isNotEmpty || documents.isNotEmpty || voiceRecordingUrl != null;

  /// Interaction type in Arabic
  String get typeAr {
    switch (type) {
      case InteractionType.call:
        return 'مكالمة هاتفية';
      case InteractionType.visit:
        return 'زيارة ميدانية';
      case InteractionType.whatsapp:
        return 'رسالة واتساب';
      case InteractionType.sms:
        return 'رسالة نصية';
      case InteractionType.email:
        return 'بريد إلكتروني';
      case InteractionType.meeting:
        return 'اجتماع';
      case InteractionType.note:
        return 'ملاحظة';
      case InteractionType.task:
        return 'مهمة';
      case InteractionType.demo:
        return 'عرض توضيحي';
      case InteractionType.training:
        return 'تدريب';
      case InteractionType.complaint:
        return 'شكوى';
      case InteractionType.feedback:
        return 'ملاحظات';
      case InteractionType.sale:
        return 'بيع';
      case InteractionType.followUp:
        return 'متابعة';
    }
  }

  /// Interaction outcome in Arabic
  String get outcomeAr {
    switch (outcome) {
      case InteractionOutcome.successful:
        return 'ناجح';
      case InteractionOutcome.noAnswer:
        return 'لم يرد';
      case InteractionOutcome.busy:
        return 'مشغول';
      case InteractionOutcome.rescheduled:
        return 'تم إعادة الجدولة';
      case InteractionOutcome.notInterested:
        return 'غير مهتم';
      case InteractionOutcome.interested:
        return 'مهتم';
      case InteractionOutcome.converted:
        return 'تم التحويل';
      case InteractionOutcome.pending:
        return 'قيد الانتظار';
      case InteractionOutcome.cancelled:
        return 'ملغي';
    }
  }

  /// Direction in Arabic
  String get directionAr {
    switch (direction) {
      case InteractionDirection.outbound:
        return 'صادر';
      case InteractionDirection.inbound:
        return 'وارد';
    }
  }

  /// Icon for interaction type
  String get typeIcon {
    switch (type) {
      case InteractionType.call:
        return 'phone';
      case InteractionType.visit:
        return 'location_on';
      case InteractionType.whatsapp:
        return 'chat';
      case InteractionType.sms:
        return 'sms';
      case InteractionType.email:
        return 'email';
      case InteractionType.meeting:
        return 'groups';
      case InteractionType.note:
        return 'note';
      case InteractionType.task:
        return 'task_alt';
      case InteractionType.demo:
        return 'play_circle';
      case InteractionType.training:
        return 'school';
      case InteractionType.complaint:
        return 'report_problem';
      case InteractionType.feedback:
        return 'feedback';
      case InteractionType.sale:
        return 'shopping_cart';
      case InteractionType.followUp:
        return 'replay';
    }
  }

  /// Duration formatted string
  String? get durationFormatted {
    if (durationMinutes == null) return null;
    if (durationMinutes! < 60) return '$durationMinutes دقيقة';
    final hours = durationMinutes! ~/ 60;
    final mins = durationMinutes! % 60;
    if (mins == 0) return '$hours ساعة';
    return '$hours ساعة و $mins دقيقة';
  }

  // ============================================================
  // JSON Serialization
  // ============================================================

  /// Create from JSON
  factory Interaction.fromJson(Map<String, dynamic> json) {
    final now = DateTime.now();

    return Interaction(
      id: json['id'] as String? ?? json['_id'] as String,
      tenantId: json['tenant_id'] as String? ?? '',
      remoteId: json['remote_id'] as String?,
      farmerId: json['farmer_id'] as String,
      farmerName: json['farmer_name'] as String?,
      type: _parseType(json['type'] as String?),
      direction: _parseDirection(json['direction'] as String?),
      outcome: _parseOutcome(json['outcome'] as String?),
      subject: json['subject'] as String? ?? '',
      subjectAr: json['subject_ar'] as String?,
      description: json['description'] as String?,
      descriptionAr: json['description_ar'] as String?,
      durationMinutes: json['duration_minutes'] as int?,
      interactionAt: json['interaction_at'] != null
          ? DateTime.tryParse(json['interaction_at'] as String) ?? DateTime.now()
          : now,
      followUpAt: json['follow_up_at'] != null
          ? DateTime.tryParse(json['follow_up_at'] as String) ?? DateTime.now()
          : null,
      followUpNotes: json['follow_up_notes'] as String?,
      agentId: json['agent_id'] as String?,
      agentName: json['agent_name'] as String?,
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      locationName: json['location_name'] as String?,
      fieldId: json['field_id'] as String?,
      photos: (json['photos'] as List?)?.cast<String>() ?? [],
      documents: (json['documents'] as List?)?.cast<String>() ?? [],
      voiceRecordingUrl: json['voice_recording_url'] as String?,
      opportunityId: json['opportunity_id'] as String?,
      taskId: json['task_id'] as String?,
      orderId: json['order_id'] as String?,
      tags: (json['tags'] as List?)?.cast<String>() ?? [],
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
        'type': type.name,
        'direction': direction.name,
        'outcome': outcome.name,
        'subject': subject,
        'subject_ar': subjectAr,
        'description': description,
        'description_ar': descriptionAr,
        'duration_minutes': durationMinutes,
        'interaction_at': interactionAt.toIso8601String(),
        'follow_up_at': followUpAt?.toIso8601String(),
        'follow_up_notes': followUpNotes,
        'agent_id': agentId,
        'agent_name': agentName,
        'latitude': latitude,
        'longitude': longitude,
        'location_name': locationName,
        'field_id': fieldId,
        'photos': photos,
        'documents': documents,
        'voice_recording_url': voiceRecordingUrl,
        'opportunity_id': opportunityId,
        'task_id': taskId,
        'order_id': orderId,
        'tags': tags,
        'synced': synced,
        'is_deleted': isDeleted,
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
        'metadata': metadata,
      };

  /// Copy with
  Interaction copyWith({
    String? id,
    String? tenantId,
    String? remoteId,
    String? farmerId,
    String? farmerName,
    InteractionType? type,
    InteractionDirection? direction,
    InteractionOutcome? outcome,
    String? subject,
    String? subjectAr,
    String? description,
    String? descriptionAr,
    int? durationMinutes,
    DateTime? interactionAt,
    DateTime? followUpAt,
    String? followUpNotes,
    String? agentId,
    String? agentName,
    double? latitude,
    double? longitude,
    String? locationName,
    String? fieldId,
    List<String>? photos,
    List<String>? documents,
    String? voiceRecordingUrl,
    String? opportunityId,
    String? taskId,
    String? orderId,
    List<String>? tags,
    bool? synced,
    bool? isDeleted,
    DateTime? createdAt,
    DateTime? updatedAt,
    Map<String, dynamic>? metadata,
  }) {
    return Interaction(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      remoteId: remoteId ?? this.remoteId,
      farmerId: farmerId ?? this.farmerId,
      farmerName: farmerName ?? this.farmerName,
      type: type ?? this.type,
      direction: direction ?? this.direction,
      outcome: outcome ?? this.outcome,
      subject: subject ?? this.subject,
      subjectAr: subjectAr ?? this.subjectAr,
      description: description ?? this.description,
      descriptionAr: descriptionAr ?? this.descriptionAr,
      durationMinutes: durationMinutes ?? this.durationMinutes,
      interactionAt: interactionAt ?? this.interactionAt,
      followUpAt: followUpAt ?? this.followUpAt,
      followUpNotes: followUpNotes ?? this.followUpNotes,
      agentId: agentId ?? this.agentId,
      agentName: agentName ?? this.agentName,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      locationName: locationName ?? this.locationName,
      fieldId: fieldId ?? this.fieldId,
      photos: photos ?? this.photos,
      documents: documents ?? this.documents,
      voiceRecordingUrl: voiceRecordingUrl ?? this.voiceRecordingUrl,
      opportunityId: opportunityId ?? this.opportunityId,
      taskId: taskId ?? this.taskId,
      orderId: orderId ?? this.orderId,
      tags: tags ?? this.tags,
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
      other is Interaction && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() => 'Interaction($id: $typeAr - $subject)';
}

// Helper functions
InteractionType _parseType(String? type) {
  switch (type?.toLowerCase()) {
    case 'call':
      return InteractionType.call;
    case 'visit':
      return InteractionType.visit;
    case 'whatsapp':
      return InteractionType.whatsapp;
    case 'sms':
      return InteractionType.sms;
    case 'email':
      return InteractionType.email;
    case 'meeting':
      return InteractionType.meeting;
    case 'note':
      return InteractionType.note;
    case 'task':
      return InteractionType.task;
    case 'demo':
      return InteractionType.demo;
    case 'training':
      return InteractionType.training;
    case 'complaint':
      return InteractionType.complaint;
    case 'feedback':
      return InteractionType.feedback;
    case 'sale':
      return InteractionType.sale;
    case 'followup':
    case 'follow_up':
      return InteractionType.followUp;
    default:
      return InteractionType.note;
  }
}

InteractionDirection _parseDirection(String? direction) {
  switch (direction?.toLowerCase()) {
    case 'inbound':
      return InteractionDirection.inbound;
    case 'outbound':
    default:
      return InteractionDirection.outbound;
  }
}

InteractionOutcome _parseOutcome(String? outcome) {
  switch (outcome?.toLowerCase()) {
    case 'successful':
      return InteractionOutcome.successful;
    case 'noanswer':
    case 'no_answer':
      return InteractionOutcome.noAnswer;
    case 'busy':
      return InteractionOutcome.busy;
    case 'rescheduled':
      return InteractionOutcome.rescheduled;
    case 'notinterested':
    case 'not_interested':
      return InteractionOutcome.notInterested;
    case 'interested':
      return InteractionOutcome.interested;
    case 'converted':
      return InteractionOutcome.converted;
    case 'cancelled':
      return InteractionOutcome.cancelled;
    case 'pending':
    default:
      return InteractionOutcome.pending;
  }
}
