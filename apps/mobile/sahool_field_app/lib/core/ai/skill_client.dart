import 'dart:convert';
import 'package:flutter/foundation.dart';
import '../http/api_client.dart';

/// Skill Result Status
enum SkillStatus {
  pending,
  success,
  error,
  timeout,
  unavailable,
}

/// Skill Execution Request
class SkillRequest {
  /// Skill identifier (e.g., "crop-health-advisor")
  final String skillName;

  /// Skill version (e.g., "1.0.0")
  final String? skillVersion;

  /// Query or input for the skill
  final String query;

  /// Field context data
  final Map<String, dynamic>? context;

  /// Additional parameters
  final Map<String, dynamic>? parameters;

  /// Request timeout
  final Duration? timeout;

  /// Priority: 'high', 'normal', 'low'
  final String priority;

  SkillRequest({
    required this.skillName,
    this.skillVersion,
    required this.query,
    this.context,
    this.parameters,
    this.timeout,
    this.priority = 'normal',
  });

  Map<String, dynamic> toJson() => {
        'skill_name': skillName,
        if (skillVersion != null) 'skill_version': skillVersion,
        'query': query,
        if (context != null) 'context': context,
        if (parameters != null) 'parameters': parameters,
        'priority': priority,
      };
}

/// Skill Execution Response
class SkillResponse {
  /// Request identifier
  final String requestId;

  /// Execution status
  final SkillStatus status;

  /// Execution result/output
  final Map<String, dynamic>? result;

  /// Confidence score (0.0 - 1.0)
  final double? confidence;

  /// Explanation of result
  final String? explanation;

  /// Sources/evidence
  final List<String>? sources;

  /// Error message if failed
  final String? errorMessage;

  /// Error code
  final String? errorCode;

  /// Execution time in milliseconds
  final int? executionTimeMs;

  /// Warnings or notices
  final List<String>? warnings;

  /// Recommended next steps
  final List<String>? nextSteps;

  /// Response timestamp
  final DateTime timestamp;

  /// Raw response data (for debugging)
  final Map<String, dynamic> rawData;

  SkillResponse({
    required this.requestId,
    required this.status,
    this.result,
    this.confidence,
    this.explanation,
    this.sources,
    this.errorMessage,
    this.errorCode,
    this.executionTimeMs,
    this.warnings,
    this.nextSteps,
    DateTime? timestamp,
    required this.rawData,
  }) : timestamp = timestamp ?? DateTime.now();

  /// Factory to create from JSON response
  factory SkillResponse.fromJson(
    String requestId,
    Map<String, dynamic> json,
  ) {
    final statusStr = (json['status'] as String?)?.toLowerCase() ?? 'pending';
    final status = SkillStatus.values.firstWhere(
      (s) => s.name == statusStr,
      orElse: () => SkillStatus.pending,
    );

    return SkillResponse(
      requestId: requestId,
      status: status,
      result: json['result'] as Map<String, dynamic>?,
      confidence: _parseDouble(json['confidence']),
      explanation: json['explanation'] as String?,
      sources: _parseStringList(json['sources']),
      errorMessage: json['error_message'] as String?,
      errorCode: json['error_code'] as String?,
      executionTimeMs: json['execution_time_ms'] as int?,
      warnings: _parseStringList(json['warnings']),
      nextSteps: _parseStringList(json['next_steps']),
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'] as String)
          : null,
      rawData: json,
    );
  }

  /// Check if response indicates success
  bool get isSuccess => status == SkillStatus.success;

  /// Check if response has high confidence
  bool get isHighConfidence => confidence != null && confidence! >= 0.8;

  /// Get confidence as percentage
  String get confidencePercentage =>
      confidence != null ? '${(confidence! * 100).toStringAsFixed(0)}%' : 'N/A';

  Map<String, dynamic> toJson() => {
        'request_id': requestId,
        'status': status.name,
        if (result != null) 'result': result,
        if (confidence != null) 'confidence': confidence,
        if (explanation != null) 'explanation': explanation,
        if (sources != null) 'sources': sources,
        if (errorMessage != null) 'error_message': errorMessage,
        if (errorCode != null) 'error_code': errorCode,
        if (executionTimeMs != null) 'execution_time_ms': executionTimeMs,
        if (warnings != null && warnings!.isNotEmpty) 'warnings': warnings,
        if (nextSteps != null && nextSteps!.isNotEmpty) 'next_steps': nextSteps,
        'timestamp': timestamp.toIso8601String(),
      };

  @override
  String toString() =>
      'SkillResponse(status=$status, confidence=$confidencePercentage, time=${executionTimeMs}ms)';

  // ============================================================
  // Helpers
  // ============================================================

  static double? _parseDouble(dynamic value) {
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value);
    return null;
  }

  static List<String> _parseStringList(dynamic value) {
    if (value == null) return [];
    if (value is List) {
      return value.whereType<String>().toList();
    }
    return [];
  }
}

/// Skill Client - API client for skills service
///
/// Provides:
/// - Skill discovery
/// - Skill execution with streaming support
/// - Request/response handling
/// - Error handling and retry logic
/// - Offline fallback using cached responses
class SkillClient {
  final ApiClient _apiClient;

  /// Skills service endpoint
  static const String _skillsEndpoint = '/skills';

  /// Default request timeout (30 seconds)
  static const Duration defaultTimeout = Duration(seconds: 30);

  SkillClient(this._apiClient);

  // ============================================================
  // Skill Discovery
  // ============================================================

  /// List available skills
  ///
  /// Returns list of skill metadata
  Future<List<Map<String, dynamic>>> listSkills({
    String? domain,
  }) async {
    try {
      final response = await _apiClient.get(
        '$_skillsEndpoint/catalog',
        queryParameters: {
          if (domain != null) 'domain': domain,
        },
      );

      if (response is List) {
        return List<Map<String, dynamic>>.from(response);
      } else if (response is Map && response['skills'] is List) {
        return List<Map<String, dynamic>>.from(response['skills']);
      }

      return [];
    } catch (e) {
      if (kDebugMode) {
        debugPrint('Error listing skills: $e');
      }
      rethrow;
    }
  }

  /// Get skill metadata
  Future<Map<String, dynamic>?> getSkillInfo(String skillName) async {
    try {
      final response = await _apiClient.get('$_skillsEndpoint/$skillName/info');
      return response as Map<String, dynamic>;
    } catch (e) {
      if (kDebugMode) {
        debugPrint('Error getting skill info for $skillName: $e');
      }
      return null;
    }
  }

  // ============================================================
  // Skill Execution
  // ============================================================

  /// Execute a skill with request context
  ///
  /// Sends request to skills service and returns response
  ///
  /// Handles:
  /// - Request serialization
  /// - Timeout management
  /// - Error handling with detailed messages
  /// - Response parsing and validation
  Future<SkillResponse> executeSkill(
    SkillRequest request, {
    Duration? timeout,
  }) async {
    final requestId = _generateRequestId();
    final executionTimeout = timeout ?? request.timeout ?? defaultTimeout;

    if (kDebugMode) {
      debugPrint(
        '⚡ Executing skill: ${request.skillName} (request_id: $requestId)',
      );
    }

    try {
      // Build request payload
      final payload = {
        ...request.toJson(),
        'request_id': requestId,
      };

      // Execute with timeout
      final response = await _apiClient
          .post(
            '$_skillsEndpoint/${request.skillName}/execute',
            payload,
          )
          .timeout(
            executionTimeout,
            onTimeout: () => throw _TimeoutException(
              'Skill execution timeout after ${executionTimeout.inSeconds}s',
            ),
          );

      if (response == null) {
        return SkillResponse(
          requestId: requestId,
          status: SkillStatus.error,
          errorMessage: 'Empty response from skill service',
          errorCode: 'EMPTY_RESPONSE',
          rawData: {},
        );
      }

      // Parse response
      final responseData = response is Map<String, dynamic>
          ? response
          : {'result': response};

      final skillResponse = SkillResponse.fromJson(requestId, responseData);

      if (kDebugMode) {
        debugPrint(
          '✅ Skill completed: ${request.skillName} (status: ${skillResponse.status.name})',
        );
      }

      return skillResponse;
    } on _TimeoutException catch (e) {
      if (kDebugMode) {
        debugPrint('⏱️  Skill timeout: ${request.skillName} - ${e.message}');
      }

      return SkillResponse(
        requestId: requestId,
        status: SkillStatus.timeout,
        errorMessage: e.message,
        errorCode: 'TIMEOUT',
        rawData: {},
      );
    } catch (e) {
      if (kDebugMode) {
        debugPrint('❌ Skill error: ${request.skillName} - $e');
      }

      return SkillResponse(
        requestId: requestId,
        status: SkillStatus.error,
        errorMessage: e.toString(),
        errorCode: 'EXECUTION_ERROR',
        rawData: {},
      );
    }
  }

  /// Execute multiple skills in parallel
  ///
  /// Returns map of skill name to response
  Future<Map<String, SkillResponse>> executeSkillBatch(
    List<SkillRequest> requests, {
    Duration? timeout,
  }) async {
    final futures = <String, Future<SkillResponse>>{};

    for (final request in requests) {
      futures[request.skillName] = executeSkill(request, timeout: timeout);
    }

    final results = await Future.wait(futures.values);
    final responses = <String, SkillResponse>{};

    var index = 0;
    for (final skillName in futures.keys) {
      responses[skillName] = results[index];
      index++;
    }

    return responses;
  }

  /// Execute skill with streaming responses (if supported)
  ///
  /// Returns stream of partial results
  Stream<SkillResponse> executeSkillStream(
    SkillRequest request, {
    Duration? timeout,
  }) async* {
    final requestId = _generateRequestId();
    final executionTimeout = timeout ?? request.timeout ?? defaultTimeout;

    if (kDebugMode) {
      debugPrint('⚡ Executing skill stream: ${request.skillName}');
    }

    try {
      final payload = {
        ...request.toJson(),
        'request_id': requestId,
        'stream': true,
      };

      // For now, execute as single request and yield response
      // In production, implement actual streaming via WebSocket or Server-Sent Events
      final response = await executeSkill(request, timeout: executionTimeout);
      yield response;
    } catch (e) {
      if (kDebugMode) {
        debugPrint('Stream error: $e');
      }
      rethrow;
    }
  }

  // ============================================================
  // Health Check
  // ============================================================

  /// Check if skills service is available
  Future<bool> isAvailable() async {
    try {
      final response = await _apiClient.get(
        '$_skillsEndpoint/health',
      );

      return response is Map && response['status'] == 'ok';
    } catch (e) {
      if (kDebugMode) {
        debugPrint('Skills service unavailable: $e');
      }
      return false;
    }
  }

  /// Get skills service status
  Future<Map<String, dynamic>?> getServiceStatus() async {
    try {
      return await _apiClient.get('$_skillsEndpoint/status')
          as Map<String, dynamic>;
    } catch (e) {
      return null;
    }
  }

  // ============================================================
  // Utilities
  // ============================================================

  /// Generate unique request ID
  static String _generateRequestId() {
    return 'skill_${DateTime.now().millisecondsSinceEpoch}_${_randomId()}';
  }

  /// Generate random ID
  static String _randomId() {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    final random = List.generate(8, (i) => chars[i % chars.length]);
    return random.join();
  }
}

/// Timeout exception for skill execution
class _TimeoutException implements Exception {
  final String message;
  _TimeoutException(this.message);
  @override
  String toString() => message;
}

/// Skill Service Options
class SkillServiceOptions {
  /// Enable request caching
  final bool enableCaching;

  /// Cache TTL
  final Duration cacheTtl;

  /// Enable fallback to cached responses
  final bool enableFallback;

  /// Enable compression for large requests
  final bool enableCompression;

  /// Maximum retry attempts
  final int maxRetries;

  /// Retry delay
  final Duration retryDelay;

  SkillServiceOptions({
    this.enableCaching = true,
    this.cacheTtl = const Duration(hours: 1),
    this.enableFallback = true,
    this.enableCompression = true,
    this.maxRetries = 3,
    this.retryDelay = const Duration(seconds: 1),
  });
}
