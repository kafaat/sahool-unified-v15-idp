import 'package:drift/drift.dart';

/// SAHOOL Enhanced Outbox Table
/// جدول صندوق الصادر المحسّن للمزامنة
///
/// This table stores all pending write operations that need to be
/// synchronized with the server when connectivity is available.
///
/// Features:
/// - Priority-based processing
/// - Idempotency key for duplicate detection
/// - ETag support for optimistic locking
/// - Comprehensive retry tracking
/// - Exponential backoff scheduling

/// Enhanced Outbox Table for offline-first sync pattern
@TableIndex(name: 'outbox_v2_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'outbox_v2_status_idx', columns: {#status})
@TableIndex(name: 'outbox_v2_entity_idx', columns: {#entityType, #entityId})
@TableIndex(
    name: 'outbox_v2_priority_status_idx', columns: {#priority, #status})
@TableIndex(name: 'outbox_v2_tenant_status_idx', columns: {#tenantId, #status})
@TableIndex(name: 'outbox_v2_next_retry_idx', columns: {#nextRetryAt})
@TableIndex(name: 'outbox_v2_idempotency_idx', columns: {#idempotencyKey})
@TableIndex(name: 'outbox_v2_created_idx', columns: {#createdAt})
class OutboxEntriesV2 extends Table {
  /// Unique identifier (UUID)
  TextColumn get id => text()();

  /// Tenant isolation key
  TextColumn get tenantId => text()();

  /// Type of entity (field, task, etc.)
  TextColumn get entityType => text()();

  /// ID of the entity being modified
  TextColumn get entityId => text()();

  /// Operation type (CREATE, UPDATE, DELETE, PATCH)
  TextColumn get operation => text()();

  /// API endpoint to call
  TextColumn get apiEndpoint => text()();

  /// HTTP method (POST, PUT, DELETE, PATCH)
  TextColumn get httpMethod => text()();

  /// JSON payload for the request
  TextColumn get payload => text()();

  /// Previous data for conflict detection (JSON, optional)
  TextColumn get previousData => text().nullable()();

  /// ETag for optimistic locking (If-Match header)
  TextColumn get ifMatch => text().nullable()();

  /// Idempotency key to prevent duplicate processing
  TextColumn get idempotencyKey => text()();

  /// Processing priority (0=critical, 1=high, 2=normal, 3=low, 4=background)
  IntColumn get priority => integer().withDefault(const Constant(2))();

  /// Current status (pending, processing, completed, failed, conflict, dead)
  TextColumn get status => text().withDefault(const Constant('pending'))();

  /// Number of retry attempts
  IntColumn get retryCount => integer().withDefault(const Constant(0))();

  /// Maximum allowed retries
  IntColumn get maxRetries => integer().withDefault(const Constant(5))();

  /// Last error message
  TextColumn get lastError => text().nullable()();

  /// Last error code (HTTP status or error type)
  TextColumn get lastErrorCode => text().nullable()();

  /// Timestamp when the entry was created
  DateTimeColumn get createdAt => dateTime()();

  /// Timestamp when the entry was last updated
  DateTimeColumn get updatedAt => dateTime()();

  /// Timestamp when processing was last attempted
  DateTimeColumn get lastAttemptAt => dateTime().nullable()();

  /// Timestamp when next retry should be attempted (for exponential backoff)
  DateTimeColumn get nextRetryAt => dateTime().nullable()();

  /// Timestamp when the entry was completed
  DateTimeColumn get completedAt => dateTime().nullable()();

  /// Custom metadata for tracking (JSON, optional)
  TextColumn get metadata => text().nullable()();

  /// Whether this entry can be aggregated with similar entries
  BoolColumn get canAggregate => boolean().withDefault(const Constant(false))();

  /// Source of the entry (user_action, background_sync, etc.)
  TextColumn get source => text().nullable()();

  @override
  Set<Column> get primaryKey => {id};
}

/// Outbox Processing Log Table
/// جدول سجل معالجة صندوق الصادر
///
/// Tracks processing attempts and results for audit trail
@TableIndex(name: 'outbox_log_entry_idx', columns: {#outboxEntryId})
@TableIndex(name: 'outbox_log_timestamp_idx', columns: {#timestamp})
class OutboxProcessingLogs extends Table {
  /// Auto-increment ID
  IntColumn get id => integer().autoIncrement()();

  /// Reference to the outbox entry
  TextColumn get outboxEntryId => text()();

  /// Attempt number
  IntColumn get attemptNumber => integer()();

  /// Processing result (success, failure, conflict, timeout)
  TextColumn get result => text()();

  /// HTTP status code (if applicable)
  IntColumn get httpStatusCode => integer().nullable()();

  /// Error message (if failed)
  TextColumn get errorMessage => text().nullable()();

  /// Response body summary (truncated)
  TextColumn get responseSummary => text().nullable()();

  /// Duration of the attempt in milliseconds
  IntColumn get durationMs => integer().nullable()();

  /// Timestamp of the attempt
  DateTimeColumn get timestamp => dateTime()();
}

/// Outbox Aggregation Rules Table
/// جدول قواعد تجميع صندوق الصادر
///
/// Defines how similar outbox entries can be combined
class OutboxAggregationRules extends Table {
  /// Auto-increment ID
  IntColumn get id => integer().autoIncrement()();

  /// Entity type this rule applies to
  TextColumn get entityType => text()();

  /// Whether to aggregate consecutive updates
  BoolColumn get aggregateUpdates =>
      boolean().withDefault(const Constant(true))();

  /// Maximum number of updates to aggregate
  IntColumn get maxAggregateCount =>
      integer().withDefault(const Constant(10))();

  /// Time window for aggregation (milliseconds)
  IntColumn get aggregateWindowMs =>
      integer().withDefault(const Constant(5000))();

  /// Fields to merge (JSON array, null means all)
  TextColumn get mergeFields => text().nullable()();

  /// Whether to keep the latest value for conflicts
  BoolColumn get keepLatest => boolean().withDefault(const Constant(true))();
}

/// Extension methods for working with outbox status
extension OutboxStatusExtension on String {
  bool get isPending => this == 'pending';
  bool get isProcessing => this == 'processing';
  bool get isCompleted => this == 'completed';
  bool get isFailed => this == 'failed';
  bool get isConflict => this == 'conflict';
  bool get isDead => this == 'dead';
  bool get isTerminal => isCompleted || isDead;
  bool get canRetry => isPending || isFailed || isConflict;
}

/// Extension methods for working with outbox priority
extension OutboxPriorityExtension on int {
  bool get isCritical => this == 0;
  bool get isHigh => this == 1;
  bool get isNormal => this == 2;
  bool get isLow => this == 3;
  bool get isBackground => this == 4;

  String get priorityName {
    switch (this) {
      case 0:
        return 'critical';
      case 1:
        return 'high';
      case 2:
        return 'normal';
      case 3:
        return 'low';
      case 4:
        return 'background';
      default:
        return 'normal';
    }
  }
}
