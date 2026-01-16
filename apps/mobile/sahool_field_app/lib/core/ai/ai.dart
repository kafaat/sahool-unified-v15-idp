/// AI Skills Integration - Core Module
///
/// Provides:
/// - Skill execution client (API integration)
/// - Context compression for efficient payloads
/// - Local memory storage with Drift (skill history, context cache, knowledge base)
/// - Farm context management
///
/// Usage:
/// ```dart
/// // Execute a skill
/// final skillClient = SkillClient(apiClient);
/// final request = SkillRequest(
///   skillName: 'crop-health-advisor',
///   query: 'What is the crop health status?',
///   context: {...},
/// );
/// final response = await skillClient.executeSkill(request);
///
/// // Compress context
/// final compressed = ContextCompressor.compress(largeContext);
///
/// // Store in memory
/// final memoryService = FarmMemoryService(database);
/// await memoryService.recordSkillInvocation(
///   tenantId: 'tenant-1',
///   skillName: 'crop-health-advisor',
///   request: request.toJson(),
///   response: response.toJson(),
///   executionTime: Duration(milliseconds: 500),
/// );
/// ```

export 'context_compressor.dart';
export 'farm_memory.dart';
export 'skill_client.dart';
