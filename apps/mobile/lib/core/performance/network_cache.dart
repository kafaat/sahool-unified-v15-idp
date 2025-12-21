import 'dart:async';
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../utils/app_logger.dart';

/// SAHOOL Network Cache
/// كاش الشبكة للطلبات API
///
/// Features:
/// - TTL-based caching
/// - Cache invalidation
/// - Offline fallback
/// - Cache size management

class NetworkCache {
  static NetworkCache? _instance;
  static NetworkCache get instance {
    _instance ??= NetworkCache._();
    return _instance!;
  }

  NetworkCache._();

  static const String _prefix = 'network_cache_';
  static const String _metaPrefix = 'network_meta_';

  SharedPreferences? _prefs;

  /// تهيئة الكاش
  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
    AppLogger.d('Network cache initialized', tag: 'NETWORK_CACHE');
  }

  /// الحصول على بيانات من الكاش
  Future<T?> get<T>(String key, {
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    final prefs = _prefs ?? await SharedPreferences.getInstance();

    // Check if cached and not expired
    final meta = prefs.getString('$_metaPrefix$key');
    if (meta == null) return null;

    final metaData = CacheMeta.fromJson(jsonDecode(meta));
    if (metaData.isExpired) {
      await remove(key);
      return null;
    }

    final data = prefs.getString('$_prefix$key');
    if (data == null) return null;

    try {
      final decoded = jsonDecode(data);

      if (fromJson != null && decoded is Map<String, dynamic>) {
        return fromJson(decoded);
      }

      return decoded as T;
    } catch (e) {
      AppLogger.e('Failed to decode cached data', tag: 'NETWORK_CACHE', error: e);
      return null;
    }
  }

  /// حفظ بيانات في الكاش
  Future<void> set<T>(String key, T data, {
    Duration ttl = const Duration(minutes: 5),
    CachePriority priority = CachePriority.normal,
  }) async {
    final prefs = _prefs ?? await SharedPreferences.getInstance();

    // Save data
    String encoded;
    if (data is String) {
      encoded = data;
    } else {
      encoded = jsonEncode(data);
    }
    await prefs.setString('$_prefix$key', encoded);

    // Save metadata
    final meta = CacheMeta(
      key: key,
      createdAt: DateTime.now(),
      ttl: ttl,
      priority: priority,
    );
    await prefs.setString('$_metaPrefix$key', jsonEncode(meta.toJson()));

    AppLogger.d('Cached: $key (TTL: ${ttl.inMinutes}m)', tag: 'NETWORK_CACHE');
  }

  /// حفظ قائمة في الكاش
  Future<void> setList<T>(String key, List<T> items, {
    Duration ttl = const Duration(minutes: 5),
    Map<String, dynamic> Function(T)? toJson,
  }) async {
    final data = items.map((item) {
      if (toJson != null) {
        return toJson(item);
      }
      return item;
    }).toList();

    await set(key, data, ttl: ttl);
  }

  /// الحصول على قائمة من الكاش
  Future<List<T>?> getList<T>(String key, {
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    final prefs = _prefs ?? await SharedPreferences.getInstance();

    // Check if cached and not expired
    final meta = prefs.getString('$_metaPrefix$key');
    if (meta == null) return null;

    final metaData = CacheMeta.fromJson(jsonDecode(meta));
    if (metaData.isExpired) {
      await remove(key);
      return null;
    }

    final data = prefs.getString('$_prefix$key');
    if (data == null) return null;

    try {
      final decoded = jsonDecode(data) as List;

      if (fromJson != null) {
        return decoded
            .map((item) => fromJson(item as Map<String, dynamic>))
            .toList();
      }

      return decoded.cast<T>();
    } catch (e) {
      AppLogger.e('Failed to decode cached list', tag: 'NETWORK_CACHE', error: e);
      return null;
    }
  }

  /// إزالة من الكاش
  Future<void> remove(String key) async {
    final prefs = _prefs ?? await SharedPreferences.getInstance();
    await prefs.remove('$_prefix$key');
    await prefs.remove('$_metaPrefix$key');
    AppLogger.d('Removed from cache: $key', tag: 'NETWORK_CACHE');
  }

  /// إزالة كاش بنمط معين
  Future<void> removePattern(String pattern) async {
    final prefs = _prefs ?? await SharedPreferences.getInstance();
    final keys = prefs.getKeys();

    int removed = 0;
    for (final key in keys) {
      if (key.startsWith(_prefix)) {
        final cacheKey = key.replaceFirst(_prefix, '');
        if (cacheKey.contains(pattern)) {
          await remove(cacheKey);
          removed++;
        }
      }
    }

    AppLogger.d('Removed $removed items matching: $pattern', tag: 'NETWORK_CACHE');
  }

  /// تنظيف الكاش المنتهي الصلاحية
  Future<void> cleanExpired() async {
    final prefs = _prefs ?? await SharedPreferences.getInstance();
    final keys = prefs.getKeys();

    int cleaned = 0;
    for (final key in keys) {
      if (key.startsWith(_metaPrefix)) {
        final meta = prefs.getString(key);
        if (meta != null) {
          final metaData = CacheMeta.fromJson(jsonDecode(meta));
          if (metaData.isExpired) {
            final cacheKey = key.replaceFirst(_metaPrefix, '');
            await remove(cacheKey);
            cleaned++;
          }
        }
      }
    }

    if (cleaned > 0) {
      AppLogger.i('Cleaned $cleaned expired cache entries', tag: 'NETWORK_CACHE');
    }
  }

  /// تنظيف كل الكاش
  Future<void> clear() async {
    final prefs = _prefs ?? await SharedPreferences.getInstance();
    final keys = prefs.getKeys().toList();

    for (final key in keys) {
      if (key.startsWith(_prefix) || key.startsWith(_metaPrefix)) {
        await prefs.remove(key);
      }
    }

    AppLogger.i('Network cache cleared', tag: 'NETWORK_CACHE');
  }

  /// الحصول على إحصائيات الكاش
  Future<CacheStats> getStats() async {
    final prefs = _prefs ?? await SharedPreferences.getInstance();
    final keys = prefs.getKeys();

    int count = 0;
    int expiredCount = 0;
    int totalSize = 0;

    for (final key in keys) {
      if (key.startsWith(_prefix)) {
        count++;
        final data = prefs.getString(key);
        if (data != null) {
          totalSize += data.length;
        }
      } else if (key.startsWith(_metaPrefix)) {
        final meta = prefs.getString(key);
        if (meta != null) {
          final metaData = CacheMeta.fromJson(jsonDecode(meta));
          if (metaData.isExpired) {
            expiredCount++;
          }
        }
      }
    }

    return CacheStats(
      entryCount: count,
      expiredCount: expiredCount,
      sizeBytes: totalSize,
    );
  }

  /// التحقق من وجود كاش صالح
  Future<bool> has(String key) async {
    final prefs = _prefs ?? await SharedPreferences.getInstance();

    final meta = prefs.getString('$_metaPrefix$key');
    if (meta == null) return false;

    final metaData = CacheMeta.fromJson(jsonDecode(meta));
    return !metaData.isExpired;
  }
}

/// أولوية الكاش
enum CachePriority {
  low,
  normal,
  high,
}

/// بيانات وصفية للكاش
class CacheMeta {
  final String key;
  final DateTime createdAt;
  final Duration ttl;
  final CachePriority priority;

  const CacheMeta({
    required this.key,
    required this.createdAt,
    required this.ttl,
    this.priority = CachePriority.normal,
  });

  bool get isExpired => DateTime.now().isAfter(createdAt.add(ttl));

  DateTime get expiresAt => createdAt.add(ttl);

  Map<String, dynamic> toJson() => {
    'key': key,
    'createdAt': createdAt.toIso8601String(),
    'ttlSeconds': ttl.inSeconds,
    'priority': priority.index,
  };

  factory CacheMeta.fromJson(Map<String, dynamic> json) => CacheMeta(
    key: json['key'] as String,
    createdAt: DateTime.parse(json['createdAt'] as String),
    ttl: Duration(seconds: json['ttlSeconds'] as int),
    priority: CachePriority.values[json['priority'] as int],
  );
}

/// إحصائيات الكاش
class CacheStats {
  final int entryCount;
  final int expiredCount;
  final int sizeBytes;

  const CacheStats({
    required this.entryCount,
    required this.expiredCount,
    required this.sizeBytes,
  });

  double get sizeMB => sizeBytes / (1024 * 1024);

  @override
  String toString() =>
      'CacheStats(entries: $entryCount, expired: $expiredCount, size: ${sizeMB.toStringAsFixed(2)} MB)';
}

/// Extension لسهولة استخدام الكاش مع Dio
extension CacheKey on String {
  String toCacheKey([Map<String, dynamic>? params]) {
    if (params == null || params.isEmpty) return this;
    final sortedParams = Map.fromEntries(
      params.entries.toList()..sort((a, b) => a.key.compareTo(b.key)),
    );
    return '$this?${sortedParams.entries.map((e) => '${e.key}=${e.value}').join('&')}';
  }
}
