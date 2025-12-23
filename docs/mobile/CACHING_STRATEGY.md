# Caching Strategy
# استراتيجية التخزين المؤقت

> **الهدف:** تحسين الأداء وتقليل استهلاك البيانات مع ضمان حداثة المعلومات

---

## نظرة عامة | Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      CACHE HIERARCHY                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ L1: Memory Cache (Riverpod Providers)                       ││
│  │ • سرعة: < 1ms                                               ││
│  │ • حجم: ~50MB                                                ││
│  │ • مدة: جلسة التطبيق                                          ││
│  └─────────────────────────────────────────────────────────────┘│
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ L2: SQLite Database (Drift)                                 ││
│  │ • سرعة: < 10ms                                              ││
│  │ • حجم: ~500MB                                               ││
│  │ • مدة: دائم                                                  ││
│  └─────────────────────────────────────────────────────────────┘│
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ L3: File Cache (Images, Documents)                          ││
│  │ • سرعة: < 100ms                                             ││
│  │ • حجم: ~1GB                                                 ││
│  │ • مدة: قابلة للتنظيف                                         ││
│  └─────────────────────────────────────────────────────────────┘│
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ L4: Network (API)                                           ││
│  │ • سرعة: 100ms - 5s                                          ││
│  │ • حجم: غير محدود                                            ││
│  │ • مدة: المصدر الأساسي                                        ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## سياسات التخزين المؤقت | Cache Policies

### حسب نوع البيانات

```dart
enum CachePolicy {
  /// لا تخزين - دائماً من الشبكة
  noCache,

  /// تخزين مع تحديث في الخلفية
  cacheFirst,

  /// شبكة أولاً مع fallback للكاش
  networkFirst,

  /// فقط من الكاش (offline)
  cacheOnly,

  /// تخزين لفترة محددة
  staleWhileRevalidate,
}

class CacheConfig {
  static const Map<String, CacheSettings> settings = {
    // بيانات المستخدم - دائمة مع تحديث
    'user_profile': CacheSettings(
      policy: CachePolicy.cacheFirst,
      maxAge: Duration(days: 7),
      staleAge: Duration(days: 30),
    ),

    // الحقول - دائمة تقريباً
    'fields': CacheSettings(
      policy: CachePolicy.cacheFirst,
      maxAge: Duration(days: 30),
      staleAge: Duration(days: 365),
    ),

    // المهام - تحديث متكرر
    'tasks': CacheSettings(
      policy: CachePolicy.staleWhileRevalidate,
      maxAge: Duration(hours: 1),
      staleAge: Duration(days: 7),
    ),

    // الطقس - قصير المدى
    'weather': CacheSettings(
      policy: CachePolicy.networkFirst,
      maxAge: Duration(minutes: 30),
      staleAge: Duration(hours: 2),
    ),

    // صور الأقمار الصناعية - متوسط
    'satellite_images': CacheSettings(
      policy: CachePolicy.cacheFirst,
      maxAge: Duration(hours: 6),
      staleAge: Duration(days: 3),
    ),

    // التنبيهات - تحديث سريع
    'alerts': CacheSettings(
      policy: CachePolicy.networkFirst,
      maxAge: Duration(minutes: 5),
      staleAge: Duration(hours: 1),
    ),
  };
}
```

---

## L1: Memory Cache (Riverpod)

### إعداد Providers

```dart
/// Provider مع تخزين تلقائي
@riverpod
class TasksNotifier extends _$TasksNotifier {
  @override
  Future<List<Task>> build() async {
    // إلغاء التخزين عند التغيير
    ref.onDispose(() => _cancelSubscription());

    // جلب من الكاش أولاً
    final cached = await ref.watch(tasksCacheProvider.future);
    if (cached != null && !cached.isStale) {
      _refreshInBackground();
      return cached.data;
    }

    // جلب من الشبكة
    return _fetchAndCache();
  }

  void _refreshInBackground() {
    Future.microtask(() async {
      try {
        final fresh = await _repository.getTasks();
        state = AsyncData(fresh);
      } catch (_) {
        // فشل صامت - البيانات المحلية كافية
      }
    });
  }
}

/// التحكم في انتهاء الصلاحية
@riverpod
class CacheManager extends _$CacheManager {
  void invalidate(String key) {
    ref.invalidate(switch (key) {
      'tasks' => tasksNotifierProvider,
      'fields' => fieldsNotifierProvider,
      'weather' => weatherNotifierProvider,
      _ => throw UnknownCacheKey(key),
    });
  }

  void invalidateAll() {
    ref.invalidate(tasksNotifierProvider);
    ref.invalidate(fieldsNotifierProvider);
    ref.invalidate(weatherNotifierProvider);
  }
}
```

---

## L2: SQLite Cache (Drift)

### جدول البيانات المؤقتة

```dart
@DataClassName('CacheEntry')
class CacheEntries extends Table {
  TextColumn get key => text()();
  TextColumn get data => text()();  // JSON
  IntColumn get createdAt => integer()();
  IntColumn get expiresAt => integer()();
  TextColumn get etag => text().nullable()();
  IntColumn get version => integer().withDefault(const Constant(1))();

  @override
  Set<Column> get primaryKey => {key};
}

/// DAO للتعامل مع الكاش
@DriftAccessor(tables: [CacheEntries])
class CacheDao extends DatabaseAccessor<AppDatabase> with _$CacheDaoMixin {
  CacheDao(AppDatabase db) : super(db);

  /// حفظ في الكاش
  Future<void> put(String key, dynamic data, Duration ttl) async {
    final now = DateTime.now();
    await into(cacheEntries).insertOnConflictUpdate(
      CacheEntriesCompanion(
        key: Value(key),
        data: Value(jsonEncode(data)),
        createdAt: Value(now.millisecondsSinceEpoch),
        expiresAt: Value(now.add(ttl).millisecondsSinceEpoch),
      ),
    );
  }

  /// قراءة من الكاش
  Future<CacheResult<T>?> get<T>(String key, T Function(Map) fromJson) async {
    final entry = await (select(cacheEntries)
          ..where((t) => t.key.equals(key)))
        .getSingleOrNull();

    if (entry == null) return null;

    final isExpired = DateTime.now().millisecondsSinceEpoch > entry.expiresAt;
    final data = fromJson(jsonDecode(entry.data));

    return CacheResult(
      data: data,
      isStale: isExpired,
      createdAt: DateTime.fromMillisecondsSinceEpoch(entry.createdAt),
    );
  }

  /// تنظيف المنتهي
  Future<int> cleanExpired() async {
    return (delete(cacheEntries)
          ..where((t) => t.expiresAt.isSmallerThan(Variable(
              DateTime.now().millisecondsSinceEpoch))))
        .go();
  }
}
```

---

## L3: File Cache

### تخزين الصور

```dart
class ImageCacheManager {
  final Directory _cacheDir;
  static const int maxCacheSize = 500 * 1024 * 1024; // 500MB

  /// تحميل صورة مع تخزين
  Future<File> getImage(String url) async {
    final cacheKey = _hashUrl(url);
    final cachedFile = File('${_cacheDir.path}/$cacheKey');

    // تحقق من الكاش
    if (await cachedFile.exists()) {
      await _updateAccessTime(cachedFile);
      return cachedFile;
    }

    // تحميل وحفظ
    final response = await _dio.get(
      url,
      options: Options(responseType: ResponseType.bytes),
    );

    await cachedFile.writeAsBytes(response.data);
    await _trimCacheIfNeeded();

    return cachedFile;
  }

  /// تنظيف الكاش (LRU)
  Future<void> _trimCacheIfNeeded() async {
    final files = await _cacheDir.list().toList();
    int totalSize = 0;

    // حساب الحجم الإجمالي
    for (final file in files) {
      if (file is File) {
        totalSize += await file.length();
      }
    }

    // حذف الأقدم إذا تجاوز الحد
    if (totalSize > maxCacheSize) {
      files.sort((a, b) => a.statSync().accessed.compareTo(b.statSync().accessed));

      for (final file in files) {
        if (totalSize <= maxCacheSize * 0.8) break;
        if (file is File) {
          totalSize -= await file.length();
          await file.delete();
        }
      }
    }
  }
}
```

### تخزين المستندات

```dart
class DocumentCacheManager {
  /// تحميل PDF مع تخزين
  Future<File> getPDF(String url, String filename) async {
    final cacheDir = await getApplicationDocumentsDirectory();
    final file = File('${cacheDir.path}/documents/$filename');

    if (await file.exists()) {
      return file;
    }

    await _downloadWithProgress(url, file);
    return file;
  }

  Future<void> _downloadWithProgress(String url, File file) async {
    await _dio.download(
      url,
      file.path,
      onReceiveProgress: (received, total) {
        if (total != -1) {
          _progressController.add(received / total);
        }
      },
    );
  }
}
```

---

## HTTP Caching

### تكوين Dio

```dart
Dio createDio() {
  final dio = Dio(BaseOptions(
    baseUrl: apiBaseUrl,
    connectTimeout: Duration(seconds: 30),
    receiveTimeout: Duration(seconds: 30),
  ));

  // Interceptor للتخزين المؤقت
  dio.interceptors.add(CacheInterceptor());

  return dio;
}

class CacheInterceptor extends Interceptor {
  final CacheDao _cacheDao;

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    // التحقق من ETag
    final cached = await _cacheDao.getMetadata(options.path);
    if (cached?.etag != null) {
      options.headers['If-None-Match'] = cached!.etag;
    }

    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) async {
    // حفظ ETag الجديد
    final etag = response.headers.value('ETag');
    if (etag != null) {
      await _cacheDao.saveMetadata(response.requestOptions.path, etag);
    }

    // 304 Not Modified - استخدم الكاش
    if (response.statusCode == 304) {
      final cached = await _cacheDao.get(response.requestOptions.path);
      response.data = cached;
    }

    handler.next(response);
  }
}
```

---

## تنظيف الكاش | Cache Cleanup

### تنظيف تلقائي

```dart
class CacheCleanupService {
  /// تنظيف يومي
  Future<void> dailyCleanup() async {
    // تنظيف SQLite
    final expiredCount = await _cacheDao.cleanExpired();
    _logger.info('Cleaned $expiredCount expired cache entries');

    // تنظيف الصور
    await _imageCacheManager.trimCache();

    // تنظيف المستندات القديمة
    await _documentCacheManager.cleanOldDocuments(Duration(days: 30));
  }

  /// تنظيف كامل
  Future<CacheStats> fullCleanup() async {
    final beforeSize = await _calculateTotalSize();

    await _cacheDao.clearAll();
    await _imageCacheManager.clearAll();
    await _documentCacheManager.clearAll();

    final afterSize = await _calculateTotalSize();

    return CacheStats(
      freedSpace: beforeSize - afterSize,
      cleanedAt: DateTime.now(),
    );
  }
}
```

### واجهة إدارة الكاش

```dart
class CacheSettingsScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cacheStats = ref.watch(cacheStatsProvider);

    return Scaffold(
      appBar: AppBar(title: Text('إدارة التخزين المؤقت')),
      body: Column(
        children: [
          // إحصائيات الكاش
          Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Column(
                children: [
                  _StatRow('الصور', cacheStats.imagesSize),
                  _StatRow('قاعدة البيانات', cacheStats.databaseSize),
                  _StatRow('المستندات', cacheStats.documentsSize),
                  Divider(),
                  _StatRow('الإجمالي', cacheStats.totalSize, bold: true),
                ],
              ),
            ),
          ),

          // أزرار التنظيف
          ListTile(
            title: Text('تنظيف الصور المؤقتة'),
            trailing: TextButton(
              onPressed: () => _cleanImages(ref),
              child: Text('تنظيف'),
            ),
          ),

          ListTile(
            title: Text('تنظيف كل البيانات المؤقتة'),
            trailing: TextButton(
              onPressed: () => _cleanAll(ref),
              style: TextButton.styleFrom(foregroundColor: Colors.red),
              child: Text('تنظيف الكل'),
            ),
          ),
        ],
      ),
    );
  }
}
```

---

## مقاييس الكاش | Cache Metrics

```dart
class CacheMetrics {
  /// نسبة الإصابة (Cache Hit Rate)
  double hitRate;

  /// متوسط وقت الاستجابة
  Duration avgResponseTime;

  /// حجم الكاش الحالي
  int currentSize;

  /// عدد العناصر المخزنة
  int itemCount;

  /// آخر تنظيف
  DateTime lastCleanup;
}

class CacheAnalytics {
  void trackCacheHit(String key) {
    _hits++;
    _analytics.track('cache_hit', {'key': key});
  }

  void trackCacheMiss(String key) {
    _misses++;
    _analytics.track('cache_miss', {'key': key});
  }

  double get hitRate => _hits / (_hits + _misses) * 100;
}
```

---

## أفضل الممارسات | Best Practices

### Do's ✅

1. **استخدم TTL مناسب** - ليس قصير جداً ولا طويل جداً
2. **نظّف دورياً** - لا تترك الكاش يمتلئ
3. **راقب Hit Rate** - يجب أن تكون > 80%
4. **خزّن بالأولوية** - البيانات المهمة أولاً
5. **احترم حدود الذاكرة** - لا تفرط في التخزين

### Don'ts ❌

1. **لا تخزّن كل شيء** - فقط ما يُستخدم
2. **لا تنسَ التنظيف** - الكاش يستهلك مساحة
3. **لا تعتمد على الكاش وحده** - قد يُمسح
4. **لا تخزّن بيانات حساسة** - بدون تشفير

---

## الموارد | Resources

- [OFFLINE_FIRST.md](./OFFLINE_FIRST.md)
- [SYNC_ENGINE.md](./SYNC_ENGINE.md)
- [ADR-003: Drift Local Database](../adr/ADR-003-drift-local-database.md)

---

<p align="center">
  <sub>SAHOOL Mobile - Caching Strategy</sub>
</p>
