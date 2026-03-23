import 'dart:convert';
import 'package:drift/drift.dart';
import 'package:flutter/foundation.dart';
import '../storage/database.dart';

// ============================================================
// Farm Memory Service
// ============================================================

/// Farm Memory Service - manages AI memory operations
///
/// Provides:
/// - Skill memory storage (invocations, results)
/// - Context caching with compression
/// - Knowledge base learning from skills
/// - Memory cleanup and maintenance
class FarmMemoryService {
  final AppDatabase _db;

  FarmMemoryService(this._db);

  // ============================================================
  // Memory Operations
  // ============================================================

  /// Record skill invocation in memory
  ///
  /// Stores request, response, and execution metrics for future learning
  Future<int> recordSkillInvocation({
    required String tenantId,
    required String skillName,
    required Map<String, dynamic> request,
    required Map<String, dynamic>? response,
    required Duration executionTime,
    double? confidence,
    String? errorMessage,
    String? errorStack,
    String? fieldId,
    String? farmId,
  }) async {
    if (kDebugMode) {
      debugPrint(
        '💾 Recording skill invocation: $skillName (${executionTime.inMilliseconds}ms)',
      );
    }

    // Calculate checksum for sync
    final checksum = _calculateChecksum(response ?? request);

    final result = await _db.into(_db.aiMemoryTable).insert(
          AiMemoryTableCompanion.insert(
            tenantId: tenantId,
            fieldId: Value(fieldId),
            farmId: Value(farmId),
            skillName: skillName,
            request: jsonEncode(request),
            response: Value(response != null ? jsonEncode(response) : null),
            executionTimeMs: Value(executionTime.inMilliseconds),
            confidence: Value(confidence),
            status: Value(response != null ? 'success' : 'error'),
            errorMessage: Value(errorMessage),
            errorStack: Value(errorStack),
            completedAt: Value(response != null ? DateTime.now() : null),
            syncChecksum: Value(checksum),
          ),
        );

    return result;
  }

  /// Get skill memory history for a field
  Future<List<AiMemoryTableData>> getSkillHistory({
    required String fieldId,
    required String skillName,
    int limit = 20,
  }) {
    return (_db.select(_db.aiMemoryTable)
          ..where((m) => m.fieldId.equals(fieldId))
          ..where((m) => m.skillName.equals(skillName))
          ..orderBy([(m) => OrderingTerm.desc(m.createdAt)])
          ..limit(limit))
        .get();
  }

  /// Get all skill invocations for tenant
  Future<List<AiMemoryTableData>> getTenantMemory({
    required String tenantId,
    String? skillName,
    int limit = 100,
  }) {
    var query = _db.select(_db.aiMemoryTable)
      ..where((m) => m.tenantId.equals(tenantId));

    if (skillName != null) {
      query = query..where((m) => m.skillName.equals(skillName));
    }

    return (query
          ..orderBy([(m) => OrderingTerm.desc(m.createdAt)])
          ..limit(limit))
        .get();
  }

  /// Mark memory items as synced
  Future<void> markMemorySynced(List<int> ids) async {
    await _db.batch((batch) {
      for (final id in ids) {
        batch.update(
          _db.aiMemoryTable,
          AiMemoryTableCompanion(
            synced: const Value(true),
            syncedAt: Value(DateTime.now()),
          ),
          where: (m) => m.id.equals(id),
        );
      }
    });
  }

  /// Clean up old memory entries
  Future<int> cleanupOldMemory(
      {Duration olderThan = const Duration(days: 30)}) async {
    final cutoff = DateTime.now().subtract(olderThan);
    return (_db.delete(_db.aiMemoryTable)
          ..where((m) => m.createdAt.isSmallerThanValue(cutoff)))
        .go();
  }

  // ============================================================
  // Context Caching
  // ============================================================

  /// Cache compressed context snapshot
  ///
  /// Returns cache ID for reference
  Future<int> cacheContextSnapshot({
    required String tenantId,
    required String fieldId,
    required Map<String, dynamic> context,
    required int sizeBytes,
    double? compressionRatio,
    Duration ttl = const Duration(hours: 6),
  }) async {
    final hash = _calculateChecksum(context);

    if (kDebugMode) {
      debugPrint(
        '📦 Caching context snapshot: $fieldId (${sizeBytes}B, $compressionRatio%)',
      );
    }

    return _db.into(_db.aiContextCacheTable).insert(
          AiContextCacheTableCompanion.insert(
            tenantId: tenantId,
            fieldId: fieldId,
            context: jsonEncode(context),
            contextHash: hash,
            sizeBytes: sizeBytes,
            compressionRatio: Value(compressionRatio),
            expiresAt: DateTime.now().add(ttl),
          ),
        );
  }

  /// Get cached context
  Future<Map<String, dynamic>?> getCachedContext(String fieldId) async {
    final item = await (_db.select(_db.aiContextCacheTable)
          ..where((c) => c.fieldId.equals(fieldId))
          ..where((c) => c.isExpired.equals(false))
          ..orderBy([(c) => OrderingTerm.desc(c.createdAt)])
          ..limit(1))
        .getSingleOrNull();

    if (item == null) return null;

    // Update access metadata
    await _db.update(_db.aiContextCacheTable).replace(
          item.copyWith(
            accessCount: item.accessCount + 1,
            lastAccessedAt: Value(DateTime.now()),
          ),
        );

    return jsonDecode(item.context) as Map<String, dynamic>;
  }

  /// Invalidate expired cache entries
  Future<int> cleanupExpiredCache() async {
    return (_db.update(_db.aiContextCacheTable)
          ..where((c) => c.expiresAt.isSmallerThanValue(DateTime.now())))
        .write(const AiContextCacheTableCompanion(isExpired: Value(true)));
  }

  /// Get cache statistics
  Future<Map<String, dynamic>> getCacheStats(String tenantId) async {
    final query = _db.select(_db.aiContextCacheTable)
      ..where((c) => c.tenantId.equals(tenantId))
      ..where((c) => c.isExpired.equals(false));

    final items = await query.get();

    return {
      'total_entries': items.length,
      'total_size_bytes':
          items.fold<int>(0, (sum, item) => sum + item.sizeBytes),
      'avg_compression_ratio': items.isEmpty
          ? 0
          : items.fold<double>(
                  0, (sum, item) => sum + (item.compressionRatio ?? 1)) /
              items.length,
      'hot_fields': items.map((i) => i.fieldId).toSet().length,
    };
  }

  // ============================================================
  // Knowledge Base
  // ============================================================

  /// Record learning from skill result
  ///
  /// Stores patterns discovered during skill execution
  Future<int> recordKnowledge({
    required String tenantId,
    required String knowledgeType,
    required Map<String, dynamic> condition,
    required String recommendation,
    required String sourceSkill,
    String? domain,
    String? reasoning,
    double accuracy = 0.8,
    Map<String, dynamic>? metadata,
  }) async {
    if (kDebugMode) {
      debugPrint('🧠 Recording knowledge: $knowledgeType from $sourceSkill');
    }

    return _db.into(_db.aiKnowledgeBaseTable).insert(
          AiKnowledgeBaseTableCompanion.insert(
            tenantId: tenantId,
            knowledgeType: knowledgeType,
            domain: Value(domain),
            condition: jsonEncode(condition),
            recommendation: recommendation,
            reasoning: Value(reasoning),
            accuracy: accuracy,
            sourceSkill: sourceSkill,
            metadata: Value(metadata != null ? jsonEncode(metadata) : null),
          ),
        );
  }

  /// Get applicable knowledge for a condition
  Future<List<AiKnowledgeBaseTableData>> getApplicableKnowledge({
    required String tenantId,
    required String knowledgeType,
    String? domain,
    int limit = 10,
  }) {
    var query = _db.select(_db.aiKnowledgeBaseTable)
      ..where((k) => k.tenantId.equals(tenantId))
      ..where((k) => k.knowledgeType.equals(knowledgeType));

    if (domain != null) {
      query = query..where((k) => k.domain.equals(domain));
    }

    return (query
          ..orderBy([(k) => OrderingTerm.desc(k.accuracy)])
          ..limit(limit))
        .get();
  }

  /// Update knowledge accuracy based on validation
  Future<void> updateKnowledgeAccuracy({
    required int knowledgeId,
    required bool success,
  }) async {
    final item = await (_db.select(_db.aiKnowledgeBaseTable)
          ..where((k) => k.id.equals(knowledgeId)))
        .getSingleOrNull();

    if (item == null) return;

    final newApplicableCount = item.applicableCount + 1;
    final newSuccessCount = success ? item.successCount + 1 : item.successCount;
    final newAccuracy = newApplicableCount > 0
        ? newSuccessCount / newApplicableCount
        : item.accuracy;

    await _db.update(_db.aiKnowledgeBaseTable).replace(
          item.copyWith(
            applicableCount: newApplicableCount,
            successCount: newSuccessCount,
            accuracy: newAccuracy,
            lastValidatedAt: Value(DateTime.now()),
          ),
        );
  }

  // ============================================================
  // Utilities
  // ============================================================

  /// Calculate SHA256 checksum of data
  static String _calculateChecksum(Map<String, dynamic> data) {
    final json = jsonEncode(data);
    // For production, use: sha256.convert(utf8.encode(json)).toString().substring(0, 16)
    // For now, use simple hash
    return json.hashCode.toString();
  }

  /// Get memory stats for dashboard
  Future<Map<String, dynamic>> getMemoryStats(String tenantId) async {
    final memoryCount = await (_db.select(_db.aiMemoryTable)
          ..where((m) => m.tenantId.equals(tenantId)))
        .get()
        .then((list) => list.length);

    final cacheCount = await (_db.select(_db.aiContextCacheTable)
          ..where((c) => c.tenantId.equals(tenantId))
          ..where((c) => c.isExpired.equals(false)))
        .get()
        .then((list) => list.length);

    final kbCount = await (_db.select(_db.aiKnowledgeBaseTable)
          ..where((k) => k.tenantId.equals(tenantId)))
        .get()
        .then((list) => list.length);

    return {
      'memory_entries': memoryCount,
      'cache_entries': cacheCount,
      'knowledge_base_entries': kbCount,
      'total_tracked_entities': memoryCount + cacheCount + kbCount,
    };
  }
}
