# AI Skills Integration Guide

Complete guide for integrating AI skills into the SAHOOL mobile app.

## Overview

The AI skills integration provides three core components:

1. **SkillClient** - API client for remote skill execution
2. **ContextCompressor** - Client-side context compression
3. **FarmMemoryService** - Local memory with Drift for skill history and learning

## Architecture

```
┌─────────────────────────────────────────────┐
│         Flutter Widget Layer                │
└────────────┬────────────────────────────────┘
             │
             ├─ SkillClient (executeSkill)
             │  └─ ApiClient → /skills/*/execute
             │
             ├─ ContextCompressor (compress/decompress)
             │  └─ Pure utility functions
             │
             └─ FarmMemoryService (record/query)
                └─ Drift Database (local storage)
                   ├─ AiMemoryTable
                   ├─ AiContextCacheTable
                   └─ AiKnowledgeBaseTable
```

## Quick Start

### 1. Execute a Skill

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sahool_field_app/core/ai/ai.dart';

// In your widget
class FieldHealthWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return FutureBuilder(
      future: _executeHealthSkill(ref),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const CircularProgressIndicator();
        }

        if (snapshot.hasError) {
          return Text('Error: ${snapshot.error}');
        }

        final response = snapshot.data as SkillResponse;
        return Text('Health Status: ${response.explanation}');
      },
    );
  }

  Future<SkillResponse> _executeHealthSkill(WidgetRef ref) async {
    final skillClient = ref.read(skillClientProvider);

    final request = SkillRequest(
      skillName: 'crop-health-advisor',
      query: 'What is the current health status of my field?',
      context: {
        'field_id': 'field-123',
        'ndvi_current': 0.65,
        'soil_moisture': 0.45,
        'temperature': 28.5,
        'crop_type': 'wheat',
      },
      parameters: {
        'include_recommendations': true,
      },
    );

    return skillClient.executeSkill(request);
  }
}
```

### 2. Compress Context

```dart
import 'package:sahool_field_app/core/ai/context_compressor.dart';

// Before sending large context to skill
final largeContext = {
  'field': {...},
  'weather': {...},
  'history': [...], // lots of historical data
};

final compressed = ContextCompressor.compress(
  largeContext,
  aggressive: false, // true to remove non-essential fields
);

// compressed['context'] - the compressed payload
// compressed['metadata'] - compression stats
```

### 3. Store in Memory

```dart
import 'package:sahool_field_app/core/ai/farm_memory.dart';

// After skill execution, record in local memory
final memoryService = FarmMemoryService(database);

await memoryService.recordSkillInvocation(
  tenantId: 'tenant-1',
  fieldId: 'field-123',
  skillName: 'crop-health-advisor',
  request: request.toJson(),
  response: response.toJson(),
  executionTime: Duration(milliseconds: 500),
  confidence: response.confidence,
  errorMessage: response.errorMessage,
);
```

## Using Riverpod Providers

All AI modules are integrated with Riverpod for state management.

### Available Providers

```dart
import 'package:sahool_field_app/core/di/ai_providers.dart';

// 1. Skill Client
final skillClient = ref.read(skillClientProvider);

// 2. Farm Memory
final memory = ref.read(farmMemoryProvider);

// 3. Skill Availability
ref.watch(skillServiceAvailabilityProvider); // FutureProvider<bool>

// 4. List Skills
ref.watch(availableSkillsProvider(null)); // FutureProvider<List>

// 5. Execute Skill
final response = await ref.read(
  executeSkillProvider(skillRequest).future,
);

// 6. Memory Stats
ref.watch(farmMemoryStatsProvider('tenant-1')); // FutureProvider

// 7. Skill History
ref.watch(skillHistoryProvider((
  fieldId: 'field-123',
  skillName: 'crop-health-advisor',
))); // FutureProvider<List>

// 8. Cached Context
ref.watch(cachedContextProvider('field-123')); // FutureProvider
```

## Complete Example: Crop Health Advisory Widget

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sahool_field_app/core/core.dart';
import 'package:sahool_field_app/core/di/ai_providers.dart';

class CropHealthAdvisoryScreen extends ConsumerWidget {
  final String fieldId;
  final String tenantId;

  const CropHealthAdvisoryScreen({
    required this.fieldId,
    required this.tenantId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Step 1: Get cached context if available
    final cachedContextAsync = ref.watch(cachedContextProvider(fieldId));

    // Step 2: Get previous skill history
    final historyAsync = ref.watch(
      skillHistoryProvider((
        fieldId: fieldId,
        skillName: 'crop-health-advisor',
      )),
    );

    // Step 3: Check service availability
    final availabilityAsync = ref.watch(skillServiceAvailabilityProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Crop Health Advisory')),
      body: Stack(
        children: [
          cachedContextAsync.when(
            data: (context) {
              if (context == null) {
                return _buildAdvisoryForm(ref);
              }
              return _buildAdvisoryWithContext(ref, context);
            },
            loading: () => const Center(
              child: CircularProgressIndicator(),
            ),
            error: (error, stack) => _buildAdvisoryForm(ref),
          ),
          // Service status indicator
          _buildServiceStatus(availabilityAsync),
        ],
      ),
    );
  }

  Widget _buildAdvisoryForm(WidgetRef ref) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: () => _executeHealthAdvisory(ref),
            icon: const Icon(Icons.lightbulb),
            label: const Text('Get Health Advisory'),
          ),
          const SizedBox(height: 24),
          _buildHistorySection(ref),
        ],
      ),
    );
  }

  Widget _buildAdvisoryWithContext(
    WidgetRef ref,
    Map<String, dynamic> context,
  ) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Field Context',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  _buildContextDisplay(context),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: () => _executeHealthAdvisory(ref),
            icon: const Icon(Icons.refresh),
            label: const Text('Refresh Advisory'),
          ),
        ],
      ),
    );
  }

  Future<void> _executeHealthAdvisory(WidgetRef ref) async {
    final skillClient = ref.read(skillClientProvider);
    final memory = ref.read(farmMemoryProvider);

    // Build request
    final request = SkillRequest(
      skillName: 'crop-health-advisor',
      query: 'Provide current health assessment and recommendations',
      context: {
        'field_id': fieldId,
        'tenant_id': tenantId,
        // Add field data from database
      },
      parameters: {
        'include_history': true,
        'include_recommendations': true,
      },
    );

    try {
      // Execute skill
      final response = await skillClient.executeSkill(request);

      // Store in local memory
      await memory.recordSkillInvocation(
        tenantId: tenantId,
        fieldId: fieldId,
        skillName: 'crop-health-advisor',
        request: request.toJson(),
        response: response.toJson(),
        executionTime: Duration(
          milliseconds: response.executionTimeMs ?? 0,
        ),
        confidence: response.confidence,
      );

      // Update UI with response
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Advisory: ${response.explanation ?? 'Success'}'),
          ),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  Widget _buildContextDisplay(Map<String, dynamic> context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: context.entries
          .map((e) => Text('${e.key}: ${e.value}'))
          .toList(),
    );
  }

  Widget _buildHistorySection(WidgetRef ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Recent Advisory History',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        ref.watch(
          skillHistoryProvider((
            fieldId: fieldId,
            skillName: 'crop-health-advisor',
          )),
        ).when(
          data: (history) => Column(
            children: history
                .map((item) => ListTile(
                      title: Text('Advisory from ${item.createdAt}'),
                      subtitle: Text(
                        'Confidence: ${item.confidence?.toStringAsFixed(2) ?? "N/A"}',
                      ),
                    ))
                .toList(),
          ),
          loading: () => const CircularProgressIndicator(),
          error: (e, st) => Text('Error: $e'),
        ),
      ],
    );
  }

  Widget _buildServiceStatus(AsyncValue<bool> availability) {
    return availability.when(
      data: (available) => Positioned(
        top: 16,
        right: 16,
        child: Container(
          padding: const EdgeInsets.symmetric(
            horizontal: 12,
            vertical: 8,
          ),
          decoration: BoxDecoration(
            color: available ? Colors.green : Colors.red,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            available ? 'Online' : 'Offline',
            style: const TextStyle(color: Colors.white),
          ),
        ),
      ),
      loading: () => const Positioned(
        top: 16,
        right: 16,
        child: CircularProgressIndicator(),
      ),
      error: (_, __) => Positioned(
        top: 16,
        right: 16,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: Colors.red,
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Text(
            'Error',
            style: TextStyle(color: Colors.white),
          ),
        ),
      ),
    );
  }
}
```

## Context Compression Best Practices

### When to Compress

```dart
// Check if compression needed
if (ContextCompressor.needsCompression(context)) {
  final compressed = ContextCompressor.compress(context);
  // Use compressed['context'] for skill request
}
```

### Aggressive Compression

Use aggressive mode for very large contexts (>1MB):

```dart
final compressed = ContextCompressor.compress(
  context,
  aggressive: true, // Removes non-essential fields
);
```

### Decompression

Always verify decompressed data:

```dart
try {
  final original = ContextCompressor.decompress(payload);
  // Use original context
} catch (e) {
  debugPrint('Context corruption detected: $e');
  // Handle gracefully
}
```

## Memory Management

### Record Skill Invocations

```dart
await memory.recordSkillInvocation(
  tenantId: 'tenant-1',
  skillName: 'crop-health-advisor',
  request: {...},
  response: {...},
  executionTime: Duration(milliseconds: 500),
  confidence: 0.85,
  fieldId: 'field-123',
);
```

### Retrieve History

```dart
final history = await memory.getSkillHistory(
  fieldId: 'field-123',
  skillName: 'crop-health-advisor',
  limit: 20, // Last 20 invocations
);
```

### Knowledge Base

Record learned patterns:

```dart
await memory.recordKnowledge(
  tenantId: 'tenant-1',
  knowledgeType: 'pattern',
  domain: 'field_health',
  condition: {
    'ndvi': {'min': 0.4, 'max': 0.6},
    'crop_type': 'wheat',
  },
  recommendation: 'Apply nitrogen fertilizer',
  sourceSkill: 'crop-health-advisor',
  accuracy: 0.85,
);
```

### Clean Up Old Data

```dart
// Remove memories older than 30 days
await memory.cleanupOldMemory(
  olderThan: Duration(days: 30),
);

// Clean expired cache
await memory.cleanupExpiredCache();
```

## Error Handling

### Skill Execution Errors

```dart
final response = await skillClient.executeSkill(request);

if (!response.isSuccess) {
  switch (response.status) {
    case SkillStatus.timeout:
      // Handle timeout - maybe use cached response
      break;
    case SkillStatus.error:
      debugPrint('Error: ${response.errorMessage}');
      break;
    case SkillStatus.unavailable:
      // Fallback to offline mode
      break;
    default:
      break;
  }
}
```

### Offline Fallback

```dart
Future<SkillResponse?> executeWithFallback(
  SkillRequest request,
  WidgetRef ref,
) async {
  final skillClient = ref.read(skillClientProvider);
  final memory = ref.read(farmMemoryProvider);

  try {
    // Try live execution
    return await skillClient.executeSkill(request);
  } catch (e) {
    // Fallback to cached response
    final history = await memory.getSkillHistory(
      fieldId: request.context?['field_id'] ?? '',
      skillName: request.skillName,
      limit: 1,
    );

    if (history.isNotEmpty) {
      final lastResponse = history.first.response;
      if (lastResponse != null) {
        return SkillResponse.fromJson(
          'cached_${DateTime.now().millisecondsSinceEpoch}',
          jsonDecode(lastResponse),
        );
      }
    }
    rethrow;
  }
}
```

## Performance Optimization

### Batch Execution

Execute multiple skills in parallel:

```dart
final responses = await skillClient.executeSkillBatch([
  SkillRequest(skillName: 'crop-health-advisor', query: '...'),
  SkillRequest(skillName: 'irrigation-advisor', query: '...'),
  SkillRequest(skillName: 'fertilizer-advisor', query: '...'),
]);

// responses['crop-health-advisor']
// responses['irrigation-advisor']
// responses['fertilizer-advisor']
```

### Context Caching

Cache field context to avoid recompression:

```dart
final cached = await memory.getCachedContext(fieldId);
if (cached != null) {
  // Use cached context instead of reading fresh
  return cached;
}

// Otherwise compute and cache
final fresh = buildContext();
await memory.cacheContextSnapshot(
  tenantId: tenantId,
  fieldId: fieldId,
  context: fresh,
  sizeBytes: jsonEncode(fresh).length,
  ttl: Duration(hours: 6),
);
```

## Monitoring and Debugging

### Memory Statistics

```dart
final stats = await memory.getMemoryStats(tenantId);
debugPrint('Memory entries: ${stats['memory_entries']}');
debugPrint('Cache entries: ${stats['cache_entries']}');
debugPrint('Knowledge base: ${stats['knowledge_base_entries']}');
```

### Compression Metrics

```dart
final compressed = ContextCompressor.compress(context);
final metadata = compressed['metadata'] as Map<String, dynamic>;
debugPrint('Compression ratio: ${metadata['compression_ratio']}%');
debugPrint('Original: ${metadata['original_size']}B');
debugPrint('Compressed: ${metadata['compressed_size']}B');
```

### Service Health

```dart
final available = await skillClient.isAvailable();
final status = await skillClient.getServiceStatus();
debugPrint('Skill service available: $available');
debugPrint('Status: $status');
```

## Database Schema

The AI integration adds three new Drift tables:

### AiMemoryTable
- Stores skill invocations and responses
- Indexed by tenantId, fieldId, skillName
- TTL-based cleanup

### AiContextCacheTable
- Caches compressed context snapshots
- Access count tracking for hot data detection
- TTL-based expiration

### AiKnowledgeBaseTable
- Stores learned patterns from skills
- Accuracy tracking and validation
- Domain-based organization

## Migration

To add AI tables to existing app:

1. Update schema version in `database.dart`
2. Add migration in `MigrationStrategy`:

```dart
if (from < 6) {
  // Migration to v6: Add AI tables
  await m.createTable(aiMemoryTable);
  await m.createTable(aiContextCacheTable);
  await m.createTable(aiKnowledgeBaseTable);
}
```

3. Run database migrations:

```bash
flutter clean
flutter pub get
flutter run
```

## Troubleshooting

### Skill timeout
- Increase timeout: `executeSkill(request, timeout: Duration(seconds: 60))`
- Check network connectivity
- Verify skill service is running

### Context too large
- Use aggressive compression: `compress(context, aggressive: true)`
- Filter context to essential fields
- Consider streaming large responses

### Memory growing
- Clean up old entries: `memory.cleanupOldMemory()`
- Monitor cache stats: `memory.getCacheStats(tenantId)`
- Set appropriate TTL values

## Additional Resources

- [Drift Database Documentation](https://drift.simonbinder.eu/)
- [Riverpod Documentation](https://riverpod.dev/)
- [SAHOOL Architecture](../../../docs)
- [Skills Service API](../../../docs/SKILLS_API.md)
