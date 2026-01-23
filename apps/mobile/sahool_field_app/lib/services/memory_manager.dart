import 'dart:async';
import 'package:flutter/foundation.dart';

/// SAHOOL Memory Manager
///
/// Provides automatic memory management, cache eviction,
/// and pagination support for optimal mobile performance.
///
/// Features:
/// - Automatic LRU cache eviction
/// - Pagination for large datasets
/// - Memory usage monitoring
/// - Stale data cleanup
class MemoryManager {
  static final MemoryManager _instance = MemoryManager._internal();
  factory MemoryManager() => _instance;
  MemoryManager._internal();

  /// Maximum number of fields to cache
  static const int maxCacheSize = 50;

  /// Maximum age of cached data in days
  static const int maxCacheAgeDays = 7;

  /// Memory usage threshold for eviction (0.0 - 1.0)
  static const double memoryThreshold = 0.8;

  /// Access log for LRU tracking
  final Map<String, DateTime> _accessLog = {};

  /// Generic cache storage
  final Map<String, dynamic> _cache = {};

  /// Cache metadata
  final Map<String, DateTime> _cacheTimestamps = {};

  /// Timer for periodic cleanup
  Timer? _cleanupTimer;

  /// Initialize memory manager
  void initialize() {
    // Start periodic cleanup (every 5 minutes)
    _cleanupTimer?.cancel();
    _cleanupTimer = Timer.periodic(
      const Duration(minutes: 5),
      (_) => autoEvict(),
    );

    debugPrint('MemoryManager initialized');
  }

  /// Dispose and cleanup
  void dispose() {
    _cleanupTimer?.cancel();
    _cache.clear();
    _accessLog.clear();
    _cacheTimestamps.clear();
  }

  /// Store data in cache
  void put<T>(String key, T data) {
    _cache[key] = data;
    _accessLog[key] = DateTime.now();
    _cacheTimestamps[key] = DateTime.now();

    // Check if we need to evict
    if (_cache.length > maxCacheSize) {
      _evictLeastRecentlyUsed();
    }
  }

  /// Get data from cache
  T? get<T>(String key) {
    if (_cache.containsKey(key)) {
      _accessLog[key] = DateTime.now();
      return _cache[key] as T?;
    }
    return null;
  }

  /// Check if key exists in cache
  bool has(String key) => _cache.containsKey(key);

  /// Remove specific key from cache
  void remove(String key) {
    _cache.remove(key);
    _accessLog.remove(key);
    _cacheTimestamps.remove(key);
  }

  /// Clear all cache
  void clear() {
    _cache.clear();
    _accessLog.clear();
    _cacheTimestamps.clear();
  }

  /// Automatic eviction based on memory and age
  Future<void> autoEvict() async {
    final now = DateTime.now();
    final cutoff = now.subtract(Duration(days: maxCacheAgeDays));

    // Remove stale entries
    final staleKeys = <String>[];
    _cacheTimestamps.forEach((key, timestamp) {
      if (timestamp.isBefore(cutoff)) {
        staleKeys.add(key);
      }
    });

    for (final key in staleKeys) {
      remove(key);
    }

    // Check memory usage and evict if needed
    final usage = await getMemoryUsage();
    if (usage > memoryThreshold) {
      await _evictOldestEntries(count: 10);
    }

    if (staleKeys.isNotEmpty || usage > memoryThreshold) {
      debugPrint(
        'MemoryManager: Evicted ${staleKeys.length} stale entries, '
        'memory usage: ${(usage * 100).toStringAsFixed(1)}%',
      );
    }
  }

  /// Evict least recently used entries
  void _evictLeastRecentlyUsed() {
    if (_accessLog.isEmpty) return;

    // Sort by last access time
    final sorted = _accessLog.entries.toList()
      ..sort((a, b) => a.value.compareTo(b.value));

    // Remove oldest 20%
    final toRemove = (sorted.length * 0.2).ceil();
    for (var i = 0; i < toRemove && i < sorted.length; i++) {
      remove(sorted[i].key);
    }

    debugPrint('MemoryManager: Evicted $toRemove LRU entries');
  }

  /// Evict oldest entries by count
  Future<void> _evictOldestEntries({int count = 10}) async {
    final sorted = _accessLog.entries.toList()
      ..sort((a, b) => a.value.compareTo(b.value));

    for (var i = 0; i < count && i < sorted.length; i++) {
      remove(sorted[i].key);
    }
  }

  /// Get approximate memory usage (0.0 - 1.0)
  Future<double> getMemoryUsage() async {
    // On web, we can't accurately measure memory
    if (kIsWeb) return 0.5;

    // Estimate based on cache size
    // Real implementation would use platform channels
    final cacheRatio = _cache.length / maxCacheSize;
    return cacheRatio.clamp(0.0, 1.0);
  }

  /// Get paginated data with caching
  Future<List<T>> getPaginated<T>({
    required String cacheKey,
    required int page,
    required int pageSize,
    required Future<List<T>> Function(int page, int pageSize) fetcher,
  }) async {
    final paginatedKey = '$cacheKey:page:$page:size:$pageSize';

    // Check cache first
    final cached = get<List<T>>(paginatedKey);
    if (cached != null) {
      return cached;
    }

    // Fetch from source
    final data = await fetcher(page, pageSize);

    // Cache the result
    put(paginatedKey, data);

    return data;
  }

  /// Get cache statistics
  Map<String, dynamic> getStats() {
    return {
      'cacheSize': _cache.length,
      'maxSize': maxCacheSize,
      'utilizationPercent': (_cache.length / maxCacheSize * 100).toStringAsFixed(1),
      'oldestEntry': _accessLog.isEmpty
          ? null
          : _accessLog.values.reduce((a, b) => a.isBefore(b) ? a : b).toIso8601String(),
      'newestEntry': _accessLog.isEmpty
          ? null
          : _accessLog.values.reduce((a, b) => a.isAfter(b) ? a : b).toIso8601String(),
    };
  }

  /// Preload commonly accessed data
  Future<void> preload<T>({
    required String key,
    required Future<T> Function() loader,
  }) async {
    if (!has(key)) {
      try {
        final data = await loader();
        put(key, data);
        debugPrint('MemoryManager: Preloaded $key');
      } catch (e) {
        debugPrint('MemoryManager: Failed to preload $key: $e');
      }
    }
  }

  /// Invalidate cache by pattern
  void invalidateByPattern(String pattern) {
    final regex = RegExp(pattern);
    final keysToRemove = _cache.keys.where((key) => regex.hasMatch(key)).toList();

    for (final key in keysToRemove) {
      remove(key);
    }

    debugPrint('MemoryManager: Invalidated ${keysToRemove.length} entries matching $pattern');
  }
}

/// Extension for easy memory management integration
extension MemoryManagerExtension on Future<List<dynamic>> {
  /// Cache the result of this future
  Future<List<T>> cached<T>(String key) async {
    final manager = MemoryManager();
    final cached = manager.get<List<T>>(key);
    if (cached != null) return cached;

    final result = await this as List<T>;
    manager.put(key, result);
    return result;
  }
}
