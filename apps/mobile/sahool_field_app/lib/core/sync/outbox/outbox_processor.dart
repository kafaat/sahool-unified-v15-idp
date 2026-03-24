import 'dart:async';
import 'dart:convert';
import 'dart:math';

import '../../storage/database.dart';
import '../../http/api_client.dart';
import '../../error_handling/app_exceptions.dart';
import '../../utils/app_logger.dart';
import '../network_status.dart';
import 'outbox_service.dart';

/// SAHOOL Outbox Processor
/// معالج صندوق الصادر
///
/// Processes outbox entries when connectivity is available.
/// Implements:
/// - Connectivity-aware processing
/// - Priority-based ordering
/// - Exponential backoff retry
/// - Circuit breaker pattern
/// - Conflict detection and resolution
/// - Rate limiting

class OutboxProcessor {
  final AppDatabase _db;
  final OutboxService _outboxService;
  final NetworkStatus _networkStatus;
  late final ApiClient _apiClient;

  // Processing state
  bool _isProcessing = false;
  bool _isPaused = false;
  int _consecutiveFailures = 0;
  Timer? _processTimer;
  Timer? _retryTimer;
  StreamSubscription<bool>? _connectivitySubscription;

  // Configuration
  final ProcessorConfig config;

  // Circuit breaker state per endpoint
  final Map<String, CircuitBreakerState> _circuitBreakers = {};

  // Stream controllers
  final _stateController = StreamController<ProcessorState>.broadcast();
  final _progressController = StreamController<ProcessingProgress>.broadcast();

  ProcessorState _currentState = ProcessorState.idle;

  OutboxProcessor({
    required AppDatabase database,
    required OutboxService outboxService,
    NetworkStatus? networkStatus,
    ApiClient? apiClient,
    this.config = const ProcessorConfig(),
  })  : _db = database,
        _outboxService = outboxService,
        _networkStatus = networkStatus ?? NetworkStatus() {
    _apiClient = apiClient ?? ApiClient();
  }

  /// Stream of processor state changes
  Stream<ProcessorState> get stateStream => _stateController.stream;

  /// Stream of processing progress
  Stream<ProcessingProgress> get progressStream => _progressController.stream;

  /// Current processor state
  ProcessorState get currentState => _currentState;

  /// Whether processor is currently processing
  bool get isProcessing => _isProcessing;

  /// Whether processor is paused
  bool get isPaused => _isPaused;

  // ═══════════════════════════════════════════════════════════════════════════
  // Lifecycle Management - إدارة دورة الحياة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Start the processor
  Future<void> start() async {
    AppLogger.i('Starting outbox processor', tag: 'PROCESSOR');

    // Subscribe to connectivity changes
    _connectivitySubscription = _networkStatus.onlineStream.listen((isOnline) {
      if (isOnline) {
        AppLogger.i('Network restored - triggering outbox processing',
            tag: 'PROCESSOR');
        _triggerProcessing();
      } else {
        AppLogger.i('Network lost - pausing outbox processing',
            tag: 'PROCESSOR');
        _updateState(ProcessorState.offline);
      }
    });

    // Start periodic processing
    _processTimer = Timer.periodic(
      config.periodicInterval,
      (_) => _triggerProcessing(),
    );

    // Initial processing
    await _triggerProcessing();
  }

  /// Stop the processor
  void stop() {
    AppLogger.i('Stopping outbox processor', tag: 'PROCESSOR');

    _processTimer?.cancel();
    _retryTimer?.cancel();
    _connectivitySubscription?.cancel();

    _isProcessing = false;
    _updateState(ProcessorState.stopped);
  }

  /// Pause processing
  void pause() {
    _isPaused = true;
    _updateState(ProcessorState.paused);
    AppLogger.i('Outbox processor paused', tag: 'PROCESSOR');
  }

  /// Resume processing
  void resume() {
    _isPaused = false;
    _triggerProcessing();
    AppLogger.i('Outbox processor resumed', tag: 'PROCESSOR');
  }

  /// Force immediate processing
  Future<ProcessingResult> processNow() async {
    return _processOutbox(force: true);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Processing Logic - منطق المعالجة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Trigger processing if conditions allow
  Future<void> _triggerProcessing() async {
    if (_isProcessing || _isPaused) return;

    if (!await _networkStatus.checkOnline()) {
      _updateState(ProcessorState.offline);
      return;
    }

    await _processOutbox();
  }

  /// Process all pending outbox entries
  Future<ProcessingResult> _processOutbox({bool force = false}) async {
    if (_isProcessing && !force) {
      return const ProcessingResult(
        success: false,
        message: 'Processing already in progress',
      );
    }

    _isProcessing = true;
    _updateState(ProcessorState.processing);

    int processed = 0;
    int failed = 0;
    int conflicts = 0;
    int skipped = 0;
    final errors = <String>[];

    try {
      final entries = await _outboxService.getPendingEntries(
        limit: config.batchSize,
      );

      if (entries.isEmpty) {
        _updateState(ProcessorState.idle);
        _isProcessing = false;
        return const ProcessingResult(
          success: true,
          message: 'No pending entries',
        );
      }

      AppLogger.i('Processing ${entries.length} outbox entries',
          tag: 'PROCESSOR');

      // Sort by priority (using retry count as proxy since we don't have priority column yet)
      entries.sort((a, b) => a.retryCount.compareTo(b.retryCount));

      for (int i = 0; i < entries.length; i++) {
        final entry = entries[i];

        // Emit progress
        _progressController.add(ProcessingProgress(
          current: i + 1,
          total: entries.length,
          currentEntity: '${entry.entityType}/${entry.entityId}',
        ));

        // Check circuit breaker
        if (!_canProcessEndpoint(entry.apiEndpoint)) {
          skipped++;
          AppLogger.d(
              'Skipping ${entry.entityType}/${entry.entityId} - circuit open',
              tag: 'PROCESSOR');
          continue;
        }

        // Check if we've exceeded max consecutive failures
        if (_consecutiveFailures >= config.maxConsecutiveFailures) {
          AppLogger.w('Too many consecutive failures, scheduling retry',
              tag: 'PROCESSOR');
          _scheduleRetry();
          break;
        }

        // Add delay between items to respect rate limits
        if (processed > 0) {
          await Future<void>.delayed(config.itemDelay);
        }

        final result = await _processEntry(entry);

        switch (result.status) {
          case ProcessEntryStatus.success:
            processed++;
            _consecutiveFailures = 0;
            _recordSuccess(entry.apiEndpoint);
            break;

          case ProcessEntryStatus.conflict:
            conflicts++;
            errors.add(
                '${entry.entityType}/${entry.entityId}: ${result.message}');
            break;

          case ProcessEntryStatus.failed:
            failed++;
            _consecutiveFailures++;
            _recordFailure(entry.apiEndpoint);
            errors.add(
                '${entry.entityType}/${entry.entityId}: ${result.message}');
            break;

          case ProcessEntryStatus.skipped:
            skipped++;
            break;

          case ProcessEntryStatus.rateLimited:
            // Stop processing and wait
            AppLogger.w('Rate limited, pausing processing', tag: 'PROCESSOR');
            await Future<void>.delayed(config.rateLimitDelay);
            skipped++;
            break;
        }
      }

      final success = failed == 0;
      final state =
          success ? ProcessorState.idle : ProcessorState.partialFailure;
      _updateState(state);

      final result = ProcessingResult(
        success: success,
        processed: processed,
        failed: failed,
        conflicts: conflicts,
        skipped: skipped,
        errors: errors,
        message: 'Processed: $processed, Failed: $failed, '
            'Conflicts: $conflicts, Skipped: $skipped',
      );

      AppLogger.sync('Outbox processing completed',
          success: result.success, details: result.message);

      // Refresh stats
      await _outboxService.getStats(forceRefresh: true);

      return result;
    } catch (e) {
      AppLogger.e('Outbox processing error', tag: 'PROCESSOR', error: e);
      _updateState(ProcessorState.error);
      _scheduleRetry();

      return ProcessingResult(
        success: false,
        message: 'Processing failed: $e',
        errors: [e.toString()],
      );
    } finally {
      _isProcessing = false;
    }
  }

  /// Process a single outbox entry
  Future<ProcessEntryResult> _processEntry(OutboxData entry) async {
    await _outboxService.markProcessing(entry.id);

    try {
      final payload = jsonDecode(entry.payload) as Map<String, dynamic>;

      // Build headers
      final headers = <String, String>{
        'Content-Type': 'application/json',
        'X-Idempotency-Key':
            '${entry.entityType}_${entry.entityId}_${entry.createdAt.millisecondsSinceEpoch}',
      };

      // Add If-Match for optimistic locking
      if (entry.ifMatch != null && entry.ifMatch!.isNotEmpty) {
        headers['If-Match'] = entry.ifMatch!;
      }

      // Make API request
      switch (entry.method.toUpperCase()) {
        case 'POST':
          await _apiClient.post(
            entry.apiEndpoint,
            payload,
            headers: headers,
          );
          break;
        case 'PUT':
          await _apiClient.put(
            entry.apiEndpoint,
            payload,
            headers: headers,
          );
          break;
        case 'PATCH':
          await _apiClient.put(
            entry.apiEndpoint,
            payload,
            headers: headers,
          );
          break;
        case 'DELETE':
          await _apiClient.delete(
            entry.apiEndpoint,
            headers: headers,
          );
          break;
        default:
          await _apiClient.post(
            entry.apiEndpoint,
            payload,
            headers: headers,
          );
      }

      // Mark as completed
      await _outboxService.markCompleted(entry.id);

      // Log success
      await _db.logSync(
        type: 'outbox_sync',
        status: 'success',
        message: '${entry.entityType}/${entry.entityId} synced successfully',
      );

      return const ProcessEntryResult(
        status: ProcessEntryStatus.success,
        message: 'Synced successfully',
      );
    } on AppException catch (e) {
      return _handleAppError(entry, e);
    } catch (e) {
      await _outboxService.markFailed(entry.id, e.toString());

      await _db.logSync(
        type: 'outbox_sync',
        status: 'failed',
        message:
            '${entry.entityType}/${entry.entityId} failed: ${e.toString()}',
      );

      return ProcessEntryResult(
        status: ProcessEntryStatus.failed,
        message: e.toString(),
      );
    }
  }

  /// Handle AppException errors from API client
  Future<ProcessEntryResult> _handleAppError(
    OutboxData entry,
    AppException e,
  ) async {
    final statusCode = e.statusCode;

    // Handle 409 Conflict
    if (statusCode == 409) {
      await _handleConflict(entry, null);
      await _outboxService.markConflict(entry.id, 'Conflict with server');

      return const ProcessEntryResult(
        status: ProcessEntryStatus.conflict,
        message: 'Conflict detected',
      );
    }

    // Handle 429 Rate Limit
    if (statusCode == 429) {
      return const ProcessEntryResult(
        status: ProcessEntryStatus.rateLimited,
        message: 'Rate limited',
      );
    }

    // Handle server errors (5xx) - retry later
    if (statusCode != null && statusCode >= 500) {
      await _outboxService.markFailed(
        entry.id,
        'Server error: $statusCode',
        errorCode: statusCode.toString(),
      );

      return ProcessEntryResult(
        status: ProcessEntryStatus.failed,
        message: 'Server error: $statusCode',
      );
    }

    // Handle client errors (4xx except 409, 429) - mark as dead
    if (statusCode != null && statusCode >= 400 && statusCode < 500) {
      await _outboxService.markDead(entry.id);

      return ProcessEntryResult(
        status: ProcessEntryStatus.failed,
        message: 'Client error: $statusCode - ${e.message}',
      );
    }

    // Retryable errors - retry
    if (e.isRetryable) {
      await _outboxService.markFailed(entry.id, e.message);

      return ProcessEntryResult(
        status: ProcessEntryStatus.failed,
        message: e.message,
      );
    }

    // Non-retryable errors - mark as dead
    await _outboxService.markDead(entry.id);

    return ProcessEntryResult(
      status: ProcessEntryStatus.failed,
      message: e.message,
    );
  }

  /// Handle conflict by applying server version
  Future<void> _handleConflict(OutboxData entry, dynamic serverResponse) async {
    Map<String, dynamic>? serverData;

    if (serverResponse is Map<String, dynamic>) {
      serverData = serverResponse['serverData'] as Map<String, dynamic>?;
    }

    // Add conflict event for UI notification
    await _db.addSyncEvent(
      tenantId: entry.tenantId,
      type: 'CONFLICT',
      message:
          'تم تطبيق نسخة السيرفر بسبب تعارض في ${_getEntityTypeAr(entry.entityType)}',
      entityType: entry.entityType,
      entityId: entry.entityId,
    );

    // Apply server data if available
    if (serverData != null && entry.entityType == 'field') {
      try {
        await _db.upsertFieldsFromServer([serverData]);
      } catch (e) {
        AppLogger.e('Failed to apply server data for conflict',
            tag: 'PROCESSOR', error: e);
      }
    }

    await _db.logSync(
      type: 'conflict',
      status: 'resolved',
      message:
          'Conflict resolved by applying server version for: ${entry.entityType}/${entry.entityId}',
    );

    AppLogger.i('Conflict resolved: ${entry.entityType}/${entry.entityId}',
        tag: 'PROCESSOR');
  }

  String _getEntityTypeAr(String type) {
    switch (type) {
      case 'field':
        return 'الحقل';
      case 'task':
        return 'المهمة';
      default:
        return 'البيانات';
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Circuit Breaker - قاطع الدائرة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check if endpoint can be processed
  bool _canProcessEndpoint(String endpoint) {
    final state = _circuitBreakers[endpoint];
    if (state == null) return true;

    switch (state.status) {
      case CircuitStatus.closed:
        return true;
      case CircuitStatus.open:
        // Check if enough time has passed to try again
        if (DateTime.now().difference(state.lastFailure) >
            config.circuitResetTimeout) {
          _circuitBreakers[endpoint] = state.copyWith(
            status: CircuitStatus.halfOpen,
          );
          return true;
        }
        return false;
      case CircuitStatus.halfOpen:
        return true;
    }
  }

  /// Record success for circuit breaker
  void _recordSuccess(String endpoint) {
    _circuitBreakers[endpoint] = CircuitBreakerState(
      status: CircuitStatus.closed,
      failureCount: 0,
      lastFailure: DateTime.now(),
    );
  }

  /// Record failure for circuit breaker
  void _recordFailure(String endpoint) {
    final state = _circuitBreakers[endpoint] ??
        CircuitBreakerState(
          status: CircuitStatus.closed,
          failureCount: 0,
          lastFailure: DateTime.now(),
        );

    final newFailureCount = state.failureCount + 1;
    final newStatus = newFailureCount >= config.circuitFailureThreshold
        ? CircuitStatus.open
        : CircuitStatus.closed;

    _circuitBreakers[endpoint] = CircuitBreakerState(
      status: newStatus,
      failureCount: newFailureCount,
      lastFailure: DateTime.now(),
    );
  }

  /// Reset circuit breaker for endpoint
  void resetCircuitBreaker(String endpoint) {
    _circuitBreakers.remove(endpoint);
  }

  /// Reset all circuit breakers
  void resetAllCircuitBreakers() {
    _circuitBreakers.clear();
    _consecutiveFailures = 0;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Retry Scheduling - جدولة إعادة المحاولة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Schedule retry with exponential backoff
  void _scheduleRetry() {
    _retryTimer?.cancel();

    final backoffMs = _calculateBackoff(_consecutiveFailures);
    final delay = Duration(milliseconds: backoffMs);

    AppLogger.d('Scheduling retry in ${delay.inSeconds}s', tag: 'PROCESSOR');

    _retryTimer = Timer(delay, () {
      _consecutiveFailures = 0;
      _triggerProcessing();
    });

    _updateState(ProcessorState.backoff);
  }

  /// Calculate exponential backoff with jitter
  int _calculateBackoff(int failures) {
    final baseMs = config.baseBackoffMs * pow(2, failures.clamp(0, 10)).toInt();
    final jitterMs = Random().nextInt(1000);
    return (baseMs + jitterMs).clamp(1000, config.maxBackoffMs);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // State Management - إدارة الحالة
  // ═══════════════════════════════════════════════════════════════════════════

  void _updateState(ProcessorState state) {
    _currentState = state;
    _stateController.add(state);
  }

  /// Dispose of resources
  void dispose() {
    stop();
    _stateController.close();
    _progressController.close();
  }
}

/// Processor configuration
class ProcessorConfig {
  /// Interval for periodic processing checks
  final Duration periodicInterval;

  /// Maximum entries to process in one batch
  final int batchSize;

  /// Delay between processing individual items
  final Duration itemDelay;

  /// Delay after rate limit is hit
  final Duration rateLimitDelay;

  /// Maximum consecutive failures before backing off
  final int maxConsecutiveFailures;

  /// Base backoff time in milliseconds
  final int baseBackoffMs;

  /// Maximum backoff time in milliseconds
  final int maxBackoffMs;

  /// Number of failures before opening circuit
  final int circuitFailureThreshold;

  /// Time before attempting to close an open circuit
  final Duration circuitResetTimeout;

  const ProcessorConfig({
    this.periodicInterval = const Duration(minutes: 2),
    this.batchSize = 50,
    this.itemDelay = const Duration(milliseconds: 100),
    this.rateLimitDelay = const Duration(seconds: 5),
    this.maxConsecutiveFailures = 5,
    this.baseBackoffMs = 1000,
    this.maxBackoffMs = 300000, // 5 minutes
    this.circuitFailureThreshold = 5,
    this.circuitResetTimeout = const Duration(minutes: 1),
  });
}

/// Processor state
enum ProcessorState {
  idle,
  processing,
  paused,
  stopped,
  offline,
  backoff,
  partialFailure,
  error,
}

/// Extension for processor state labels
extension ProcessorStateExtension on ProcessorState {
  String get labelAr {
    switch (this) {
      case ProcessorState.idle:
        return 'خامل';
      case ProcessorState.processing:
        return 'جاري المعالجة';
      case ProcessorState.paused:
        return 'متوقف مؤقتاً';
      case ProcessorState.stopped:
        return 'متوقف';
      case ProcessorState.offline:
        return 'غير متصل';
      case ProcessorState.backoff:
        return 'في انتظار إعادة المحاولة';
      case ProcessorState.partialFailure:
        return 'فشل جزئي';
      case ProcessorState.error:
        return 'خطأ';
    }
  }

  String get labelEn {
    switch (this) {
      case ProcessorState.idle:
        return 'Idle';
      case ProcessorState.processing:
        return 'Processing';
      case ProcessorState.paused:
        return 'Paused';
      case ProcessorState.stopped:
        return 'Stopped';
      case ProcessorState.offline:
        return 'Offline';
      case ProcessorState.backoff:
        return 'Waiting for retry';
      case ProcessorState.partialFailure:
        return 'Partial failure';
      case ProcessorState.error:
        return 'Error';
    }
  }

  bool get isActive =>
      this == ProcessorState.processing || this == ProcessorState.backoff;
}

/// Processing result
class ProcessingResult {
  final bool success;
  final int processed;
  final int failed;
  final int conflicts;
  final int skipped;
  final List<String> errors;
  final String message;

  const ProcessingResult({
    required this.success,
    this.processed = 0,
    this.failed = 0,
    this.conflicts = 0,
    this.skipped = 0,
    this.errors = const [],
    required this.message,
  });
}

/// Processing progress for UI updates
class ProcessingProgress {
  final int current;
  final int total;
  final String currentEntity;

  const ProcessingProgress({
    required this.current,
    required this.total,
    required this.currentEntity,
  });

  double get percentage => total > 0 ? current / total : 0;
}

/// Single entry processing result
enum ProcessEntryStatus {
  success,
  failed,
  conflict,
  skipped,
  rateLimited,
}

class ProcessEntryResult {
  final ProcessEntryStatus status;
  final String message;

  const ProcessEntryResult({
    required this.status,
    required this.message,
  });
}

/// Circuit breaker status
enum CircuitStatus {
  closed,
  open,
  halfOpen,
}

/// Circuit breaker state
class CircuitBreakerState {
  final CircuitStatus status;
  final int failureCount;
  final DateTime lastFailure;

  const CircuitBreakerState({
    required this.status,
    required this.failureCount,
    required this.lastFailure,
  });

  CircuitBreakerState copyWith({
    CircuitStatus? status,
    int? failureCount,
    DateTime? lastFailure,
  }) {
    return CircuitBreakerState(
      status: status ?? this.status,
      failureCount: failureCount ?? this.failureCount,
      lastFailure: lastFailure ?? this.lastFailure,
    );
  }
}
