import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../ai/ai.dart';
import '../http/api_client.dart';
import '../storage/database.dart';

// ============================================================
// Skill Client Provider
// ============================================================

/// Skill Client Provider
///
/// Provides access to the skills service API client
final skillClientProvider = Provider<SkillClient>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return SkillClient(apiClient);
});

// ============================================================
// Farm Memory Service Provider
// ============================================================

/// Farm Memory Service Provider
///
/// Provides AI memory management with local storage
final farmMemoryProvider = Provider<FarmMemoryService>((ref) {
  final db = ref.watch(databaseProvider);
  return FarmMemoryService(db);
});

// ============================================================
// Context Compressor (Stateless)
// ============================================================

/// Context Compressor - utility for context compression
///
/// No provider needed as it's a pure utility function
/// Usage: ContextCompressor.compress(context)

// ============================================================
// Skill Service Availability
// ============================================================

/// Watch skill service availability
final skillServiceAvailabilityProvider = FutureProvider<bool>((ref) async {
  final skillClient = ref.watch(skillClientProvider);
  return skillClient.isAvailable();
});

/// Watch skill service status
final skillServiceStatusProvider =
    FutureProvider<Map<String, dynamic>?>((ref) async {
  final skillClient = ref.watch(skillClientProvider);
  return skillClient.getServiceStatus();
});

// ============================================================
// Skill Discovery
// ============================================================

/// Watch available skills
///
/// Filters by domain if provided
final availableSkillsProvider =
    FutureProvider.family<List<Map<String, dynamic>>, String?>((ref, domain) async {
  final skillClient = ref.watch(skillClientProvider);
  return skillClient.listSkills(domain: domain);
});

/// Watch specific skill metadata
final skillInfoProvider = FutureProvider.family<Map<String, dynamic>?, String>((ref, skillName) async {
  final skillClient = ref.watch(skillClientProvider);
  return skillClient.getSkillInfo(skillName);
});

// ============================================================
// Memory Statistics
// ============================================================

/// Watch farm memory statistics
final farmMemoryStatsProvider = FutureProvider.family<Map<String, dynamic>, String>((ref, tenantId) async {
  final farmMemory = ref.watch(farmMemoryProvider);
  return farmMemory.getMemoryStats(tenantId);
});

/// Watch context cache statistics
final contextCacheStatsProvider = FutureProvider.family<Map<String, dynamic>, String>((ref, tenantId) async {
  final farmMemory = ref.watch(farmMemoryProvider);
  return farmMemory.getCacheStats(tenantId);
});

// ============================================================
// Skill Execution History
// ============================================================

/// Watch skill execution history for a field
///
/// Parameters: (fieldId, skillName)
final skillHistoryProvider = FutureProvider.family<
    List<AiMemoryTableData>,
    ({String fieldId, String skillName})>((ref, params) async {
  final farmMemory = ref.watch(farmMemoryProvider);
  return farmMemory.getSkillHistory(
    fieldId: params.fieldId,
    skillName: params.skillName,
  );
});

// ============================================================
// API Client Provider (imported from existing)
// ============================================================

// Note: apiClientProvider is defined in providers.dart
// Note: databaseProvider is defined in providers.dart

// ============================================================
// Skill Execution (Manual Invocation)
// ============================================================

/// Async provider family for skill execution
///
/// Usage in widgets:
/// ```dart
/// final response = await ref.read(
///   executeSkillProvider((
///     skillName: 'crop-health-advisor',
///     query: 'Health status?',
///     context: {...},
///   )).future,
/// );
/// ```
final executeSkillProvider = FutureProvider.autoDispose
    .family<SkillResponse, SkillRequest>((ref, request) async {
  final skillClient = ref.watch(skillClientProvider);
  return skillClient.executeSkill(request);
});

// ============================================================
// Batch Skill Execution
// ============================================================

/// Execute multiple skills in parallel
final executeSkillBatchProvider = FutureProvider.autoDispose
    .family<Map<String, SkillResponse>, List<SkillRequest>>(
        (ref, requests) async {
  final skillClient = ref.watch(skillClientProvider);
  return skillClient.executeSkillBatch(requests);
});

// ============================================================
// Knowledge Base
// ============================================================

/// Get applicable knowledge for a condition
///
/// Parameters: (tenantId, knowledgeType, domain)
final applicableKnowledgeProvider = FutureProvider.family<
    List<AiKnowledgeBaseTableData>,
    ({
      String tenantId,
      String knowledgeType,
      String? domain,
    })>((ref, params) async {
  final farmMemory = ref.watch(farmMemoryProvider);
  return farmMemory.getApplicableKnowledge(
    tenantId: params.tenantId,
    knowledgeType: params.knowledgeType,
    domain: params.domain,
  );
});

// ============================================================
// Context Caching
// ============================================================

/// Get cached context for a field
final cachedContextProvider = FutureProvider.autoDispose
    .family<Map<String, dynamic>?, String>((ref, fieldId) async {
  final farmMemory = ref.watch(farmMemoryProvider);
  return farmMemory.getCachedContext(fieldId);
});

// ============================================================
// Options
// ============================================================

/// Skill service configuration options
final skillServiceOptionsProvider = Provider<SkillServiceOptions>((ref) {
  return SkillServiceOptions(
    enableCaching: true,
    cacheTtl: const Duration(hours: 1),
    enableFallback: true,
    enableCompression: true,
    maxRetries: 3,
    retryDelay: const Duration(seconds: 1),
  );
});

// ============================================================
// Compression Configuration
// ============================================================

/// Context compression settings
final compressionConfigProvider = Provider<Map<String, dynamic>>((ref) {
  return {
    'enabled': true,
    'threshold': ContextCompressor.compressionThreshold,
    'max_size': ContextCompressor.maxContextSize,
    'coordinate_precision': ContextCompressor.coordinatePrecision,
  };
});
