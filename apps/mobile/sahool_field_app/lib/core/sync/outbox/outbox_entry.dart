import 'dart:convert';

/// SAHOOL Outbox Entry Model
/// نموذج عنصر صندوق الصادر للمزامنة
///
/// Implements the transactional outbox pattern for reliable
/// offline-first data synchronization with:
/// - Priority-based processing
/// - Idempotency keys for duplicate detection
/// - ETag support for optimistic locking
/// - Comprehensive metadata tracking

/// Operation types for outbox entries
enum OutboxOperation {
  create('CREATE'),
  update('UPDATE'),
  delete('DELETE'),
  patch('PATCH');

  const OutboxOperation(this.value);
  final String value;

  static OutboxOperation fromString(String value) {
    return OutboxOperation.values.firstWhere(
      (e) => e.value.toUpperCase() == value.toUpperCase(),
      orElse: () => OutboxOperation.create,
    );
  }

  String toHttpMethod() {
    switch (this) {
      case OutboxOperation.create:
        return 'POST';
      case OutboxOperation.update:
        return 'PUT';
      case OutboxOperation.delete:
        return 'DELETE';
      case OutboxOperation.patch:
        return 'PATCH';
    }
  }
}

/// Priority levels for outbox processing
enum OutboxPriority {
  /// Critical operations processed first (e.g., delete, auth)
  critical(0),

  /// High priority (e.g., task completion, important updates)
  high(1),

  /// Normal priority (e.g., regular updates)
  normal(2),

  /// Low priority (e.g., analytics, non-critical metadata)
  low(3),

  /// Background priority (e.g., sync logs, cleanup)
  background(4);

  const OutboxPriority(this.value);
  final int value;

  static OutboxPriority fromValue(int value) {
    return OutboxPriority.values.firstWhere(
      (e) => e.value == value,
      orElse: () => OutboxPriority.normal,
    );
  }

  /// Arabic label for priority
  String get labelAr {
    switch (this) {
      case OutboxPriority.critical:
        return 'حرج';
      case OutboxPriority.high:
        return 'عالي';
      case OutboxPriority.normal:
        return 'عادي';
      case OutboxPriority.low:
        return 'منخفض';
      case OutboxPriority.background:
        return 'خلفية';
    }
  }

  /// English label for priority
  String get labelEn {
    switch (this) {
      case OutboxPriority.critical:
        return 'Critical';
      case OutboxPriority.high:
        return 'High';
      case OutboxPriority.normal:
        return 'Normal';
      case OutboxPriority.low:
        return 'Low';
      case OutboxPriority.background:
        return 'Background';
    }
  }
}

/// Status of an outbox entry
enum OutboxEntryStatus {
  /// Waiting to be processed
  pending('pending'),

  /// Currently being processed
  processing('processing'),

  /// Successfully synchronized
  completed('completed'),

  /// Failed to sync (will be retried)
  failed('failed'),

  /// Conflict detected with server
  conflict('conflict'),

  /// Permanently failed after max retries
  dead('dead');

  const OutboxEntryStatus(this.value);
  final String value;

  static OutboxEntryStatus fromString(String value) {
    return OutboxEntryStatus.values.firstWhere(
      (e) => e.value == value,
      orElse: () => OutboxEntryStatus.pending,
    );
  }

  bool get isTerminal =>
      this == OutboxEntryStatus.completed || this == OutboxEntryStatus.dead;

  bool get canRetry =>
      this == OutboxEntryStatus.pending ||
      this == OutboxEntryStatus.failed ||
      this == OutboxEntryStatus.conflict;

  /// Arabic label
  String get labelAr {
    switch (this) {
      case OutboxEntryStatus.pending:
        return 'قيد الانتظار';
      case OutboxEntryStatus.processing:
        return 'قيد المعالجة';
      case OutboxEntryStatus.completed:
        return 'مكتمل';
      case OutboxEntryStatus.failed:
        return 'فشل';
      case OutboxEntryStatus.conflict:
        return 'تعارض';
      case OutboxEntryStatus.dead:
        return 'متوقف نهائياً';
    }
  }

  /// English label
  String get labelEn {
    switch (this) {
      case OutboxEntryStatus.pending:
        return 'Pending';
      case OutboxEntryStatus.processing:
        return 'Processing';
      case OutboxEntryStatus.completed:
        return 'Completed';
      case OutboxEntryStatus.failed:
        return 'Failed';
      case OutboxEntryStatus.conflict:
        return 'Conflict';
      case OutboxEntryStatus.dead:
        return 'Dead';
    }
  }
}

/// Enhanced Outbox Entry for offline sync
class OutboxEntry {
  /// Unique identifier for the entry
  final String id;

  /// Tenant isolation key
  final String tenantId;

  /// Type of entity (field, task, etc.)
  final String entityType;

  /// ID of the entity being modified
  final String entityId;

  /// Operation type (create, update, delete)
  final OutboxOperation operation;

  /// API endpoint to call
  final String apiEndpoint;

  /// HTTP method (derived from operation)
  final String httpMethod;

  /// JSON payload for the request
  final Map<String, dynamic> payload;

  /// Previous data for conflict detection (updates only)
  final Map<String, dynamic>? previousData;

  /// ETag for optimistic locking
  final String? ifMatch;

  /// Idempotency key to prevent duplicate processing
  final String idempotencyKey;

  /// Processing priority
  final OutboxPriority priority;

  /// Current status
  final OutboxEntryStatus status;

  /// Number of retry attempts
  final int retryCount;

  /// Maximum allowed retries
  final int maxRetries;

  /// Last error message
  final String? lastError;

  /// Last error code (HTTP status or error type)
  final String? lastErrorCode;

  /// Timestamp when the entry was created
  final DateTime createdAt;

  /// Timestamp when the entry was last updated
  final DateTime updatedAt;

  /// Timestamp when processing was last attempted
  final DateTime? lastAttemptAt;

  /// Timestamp when next retry should be attempted
  final DateTime? nextRetryAt;

  /// Timestamp when the entry was completed
  final DateTime? completedAt;

  /// Custom metadata for tracking
  final Map<String, dynamic>? metadata;

  /// Whether this entry should be aggregated with similar entries
  final bool canAggregate;

  /// Source of the entry (user action, background sync, etc.)
  final String? source;

  const OutboxEntry({
    required this.id,
    required this.tenantId,
    required this.entityType,
    required this.entityId,
    required this.operation,
    required this.apiEndpoint,
    required this.httpMethod,
    required this.payload,
    this.previousData,
    this.ifMatch,
    required this.idempotencyKey,
    this.priority = OutboxPriority.normal,
    this.status = OutboxEntryStatus.pending,
    this.retryCount = 0,
    this.maxRetries = 5,
    this.lastError,
    this.lastErrorCode,
    required this.createdAt,
    required this.updatedAt,
    this.lastAttemptAt,
    this.nextRetryAt,
    this.completedAt,
    this.metadata,
    this.canAggregate = false,
    this.source,
  });

  /// Create a new entry for create operation
  factory OutboxEntry.create({
    required String id,
    required String tenantId,
    required String entityType,
    required String entityId,
    required String apiEndpoint,
    required Map<String, dynamic> payload,
    OutboxPriority priority = OutboxPriority.normal,
    Map<String, dynamic>? metadata,
    String? source,
  }) {
    final now = DateTime.now();
    return OutboxEntry(
      id: id,
      tenantId: tenantId,
      entityType: entityType,
      entityId: entityId,
      operation: OutboxOperation.create,
      apiEndpoint: apiEndpoint,
      httpMethod: 'POST',
      payload: payload,
      idempotencyKey:
          'create_${entityType}_${entityId}_${now.millisecondsSinceEpoch}',
      priority: priority,
      createdAt: now,
      updatedAt: now,
      metadata: metadata,
      source: source,
    );
  }

  /// Create a new entry for update operation
  factory OutboxEntry.update({
    required String id,
    required String tenantId,
    required String entityType,
    required String entityId,
    required String apiEndpoint,
    required Map<String, dynamic> payload,
    Map<String, dynamic>? previousData,
    String? ifMatch,
    OutboxPriority priority = OutboxPriority.normal,
    Map<String, dynamic>? metadata,
    String? source,
    bool canAggregate = true,
  }) {
    final now = DateTime.now();
    return OutboxEntry(
      id: id,
      tenantId: tenantId,
      entityType: entityType,
      entityId: entityId,
      operation: OutboxOperation.update,
      apiEndpoint: apiEndpoint,
      httpMethod: 'PUT',
      payload: payload,
      previousData: previousData,
      ifMatch: ifMatch,
      idempotencyKey:
          'update_${entityType}_${entityId}_${now.millisecondsSinceEpoch}',
      priority: priority,
      createdAt: now,
      updatedAt: now,
      metadata: metadata,
      canAggregate: canAggregate,
      source: source,
    );
  }

  /// Create a new entry for delete operation
  factory OutboxEntry.delete({
    required String id,
    required String tenantId,
    required String entityType,
    required String entityId,
    required String apiEndpoint,
    String? ifMatch,
    OutboxPriority priority = OutboxPriority.high,
    Map<String, dynamic>? metadata,
    String? source,
  }) {
    final now = DateTime.now();
    return OutboxEntry(
      id: id,
      tenantId: tenantId,
      entityType: entityType,
      entityId: entityId,
      operation: OutboxOperation.delete,
      apiEndpoint: apiEndpoint,
      httpMethod: 'DELETE',
      payload: const {},
      ifMatch: ifMatch,
      idempotencyKey: 'delete_${entityType}_$entityId',
      priority: priority,
      createdAt: now,
      updatedAt: now,
      metadata: metadata,
      source: source,
    );
  }

  /// Create a copy with updated fields
  OutboxEntry copyWith({
    String? id,
    String? tenantId,
    String? entityType,
    String? entityId,
    OutboxOperation? operation,
    String? apiEndpoint,
    String? httpMethod,
    Map<String, dynamic>? payload,
    Map<String, dynamic>? previousData,
    String? ifMatch,
    String? idempotencyKey,
    OutboxPriority? priority,
    OutboxEntryStatus? status,
    int? retryCount,
    int? maxRetries,
    String? lastError,
    String? lastErrorCode,
    DateTime? createdAt,
    DateTime? updatedAt,
    DateTime? lastAttemptAt,
    DateTime? nextRetryAt,
    DateTime? completedAt,
    Map<String, dynamic>? metadata,
    bool? canAggregate,
    String? source,
  }) {
    return OutboxEntry(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      entityType: entityType ?? this.entityType,
      entityId: entityId ?? this.entityId,
      operation: operation ?? this.operation,
      apiEndpoint: apiEndpoint ?? this.apiEndpoint,
      httpMethod: httpMethod ?? this.httpMethod,
      payload: payload ?? this.payload,
      previousData: previousData ?? this.previousData,
      ifMatch: ifMatch ?? this.ifMatch,
      idempotencyKey: idempotencyKey ?? this.idempotencyKey,
      priority: priority ?? this.priority,
      status: status ?? this.status,
      retryCount: retryCount ?? this.retryCount,
      maxRetries: maxRetries ?? this.maxRetries,
      lastError: lastError ?? this.lastError,
      lastErrorCode: lastErrorCode ?? this.lastErrorCode,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      lastAttemptAt: lastAttemptAt ?? this.lastAttemptAt,
      nextRetryAt: nextRetryAt ?? this.nextRetryAt,
      completedAt: completedAt ?? this.completedAt,
      metadata: metadata ?? this.metadata,
      canAggregate: canAggregate ?? this.canAggregate,
      source: source ?? this.source,
    );
  }

  /// Mark as processing
  OutboxEntry markProcessing() {
    return copyWith(
      status: OutboxEntryStatus.processing,
      lastAttemptAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
  }

  /// Mark as completed successfully
  OutboxEntry markCompleted() {
    return copyWith(
      status: OutboxEntryStatus.completed,
      completedAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
  }

  /// Mark as failed with error
  OutboxEntry markFailed(String error, {String? errorCode}) {
    final newRetryCount = retryCount + 1;
    final nextRetry = _calculateNextRetry(newRetryCount);
    final newStatus = newRetryCount >= maxRetries
        ? OutboxEntryStatus.dead
        : OutboxEntryStatus.failed;

    return copyWith(
      status: newStatus,
      retryCount: newRetryCount,
      lastError: error,
      lastErrorCode: errorCode,
      nextRetryAt: nextRetry,
      updatedAt: DateTime.now(),
    );
  }

  /// Mark as conflict
  OutboxEntry markConflict(String error) {
    return copyWith(
      status: OutboxEntryStatus.conflict,
      lastError: error,
      lastErrorCode: '409',
      updatedAt: DateTime.now(),
    );
  }

  /// Reset for retry
  OutboxEntry resetForRetry() {
    return copyWith(
      status: OutboxEntryStatus.pending,
      updatedAt: DateTime.now(),
      nextRetryAt: null,
    );
  }

  /// Calculate next retry time with exponential backoff
  DateTime _calculateNextRetry(int attempt) {
    // Exponential backoff: 2^attempt seconds with jitter
    // Attempt 1: ~2s, Attempt 2: ~4s, Attempt 3: ~8s, etc.
    final baseSeconds = 1 << attempt; // 2^attempt
    final jitterMs = DateTime.now().millisecond % 1000;
    final delayMs = (baseSeconds * 1000) + jitterMs;
    final cappedDelayMs = delayMs.clamp(1000, 300000); // Max 5 minutes

    return DateTime.now().add(Duration(milliseconds: cappedDelayMs));
  }

  /// Check if entry can be retried now
  bool get canRetryNow {
    if (!status.canRetry) return false;
    if (nextRetryAt == null) return true;
    return DateTime.now().isAfter(nextRetryAt!);
  }

  /// Check if entry has exceeded max retries
  bool get hasExceededRetries => retryCount >= maxRetries;

  /// Time since last attempt
  Duration? get timeSinceLastAttempt {
    if (lastAttemptAt == null) return null;
    return DateTime.now().difference(lastAttemptAt!);
  }

  /// Time until next retry
  Duration? get timeUntilNextRetry {
    if (nextRetryAt == null) return null;
    final diff = nextRetryAt!.difference(DateTime.now());
    return diff.isNegative ? Duration.zero : diff;
  }

  /// Convert to JSON for serialization
  Map<String, dynamic> toJson() => {
        'id': id,
        'tenant_id': tenantId,
        'entity_type': entityType,
        'entity_id': entityId,
        'operation': operation.value,
        'api_endpoint': apiEndpoint,
        'http_method': httpMethod,
        'payload': jsonEncode(payload),
        'previous_data': previousData != null ? jsonEncode(previousData) : null,
        'if_match': ifMatch,
        'idempotency_key': idempotencyKey,
        'priority': priority.value,
        'status': status.value,
        'retry_count': retryCount,
        'max_retries': maxRetries,
        'last_error': lastError,
        'last_error_code': lastErrorCode,
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
        'last_attempt_at': lastAttemptAt?.toIso8601String(),
        'next_retry_at': nextRetryAt?.toIso8601String(),
        'completed_at': completedAt?.toIso8601String(),
        'metadata': metadata != null ? jsonEncode(metadata) : null,
        'can_aggregate': canAggregate,
        'source': source,
      };

  /// Create from JSON
  factory OutboxEntry.fromJson(Map<String, dynamic> json) {
    return OutboxEntry(
      id: json['id'] as String,
      tenantId: json['tenant_id'] as String,
      entityType: json['entity_type'] as String,
      entityId: json['entity_id'] as String,
      operation: OutboxOperation.fromString(json['operation'] as String),
      apiEndpoint: json['api_endpoint'] as String,
      httpMethod: json['http_method'] as String,
      payload: json['payload'] is String
          ? jsonDecode(json['payload'] as String) as Map<String, dynamic>
          : json['payload'] as Map<String, dynamic>,
      previousData: json['previous_data'] != null
          ? (json['previous_data'] is String
              ? jsonDecode(json['previous_data'] as String)
                  as Map<String, dynamic>
              : json['previous_data'] as Map<String, dynamic>)
          : null,
      ifMatch: json['if_match'] as String?,
      idempotencyKey: json['idempotency_key'] as String,
      priority: OutboxPriority.fromValue(json['priority'] as int),
      status: OutboxEntryStatus.fromString(json['status'] as String),
      retryCount: json['retry_count'] as int? ?? 0,
      maxRetries: json['max_retries'] as int? ?? 5,
      lastError: json['last_error'] as String?,
      lastErrorCode: json['last_error_code'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      lastAttemptAt: json['last_attempt_at'] != null
          ? DateTime.parse(json['last_attempt_at'] as String)
          : null,
      nextRetryAt: json['next_retry_at'] != null
          ? DateTime.parse(json['next_retry_at'] as String)
          : null,
      completedAt: json['completed_at'] != null
          ? DateTime.parse(json['completed_at'] as String)
          : null,
      metadata: json['metadata'] != null
          ? (json['metadata'] is String
              ? jsonDecode(json['metadata'] as String) as Map<String, dynamic>
              : json['metadata'] as Map<String, dynamic>)
          : null,
      canAggregate: json['can_aggregate'] as bool? ?? false,
      source: json['source'] as String?,
    );
  }

  @override
  String toString() {
    return 'OutboxEntry(id: $id, entity: $entityType/$entityId, '
        'op: ${operation.value}, status: ${status.value}, retry: $retryCount)';
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is OutboxEntry &&
          runtimeType == other.runtimeType &&
          id == other.id;

  @override
  int get hashCode => id.hashCode;
}

/// Extension for determining priority based on entity and operation
extension OutboxPriorityHelper on OutboxEntry {
  /// Get recommended priority based on entity type and operation
  static OutboxPriority getRecommendedPriority(
    String entityType,
    OutboxOperation operation,
  ) {
    // Delete operations are always high priority
    if (operation == OutboxOperation.delete) {
      return OutboxPriority.high;
    }

    // Task completions are high priority
    if (entityType == 'task' && operation == OutboxOperation.update) {
      return OutboxPriority.high;
    }

    // Field operations are normal priority
    if (entityType == 'field') {
      return OutboxPriority.normal;
    }

    // Analytics and logs are low priority
    if (entityType == 'analytics' || entityType == 'log') {
      return OutboxPriority.low;
    }

    return OutboxPriority.normal;
  }
}
