/// SAHOOL Enhanced State Management
/// نظام إدارة الحالة المحسّن
///
/// Features:
/// - AsyncValue extensions for better error handling
/// - Cached providers for offline-first data
/// - Retry logic with exponential backoff
/// - State persistence utilities
/// - Connectivity-aware providers
library;

import 'dart:async';
import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../utils/app_logger.dart';
import '../offline/offline_ui_components.dart' show networkStatusProvider;

// =============================================================================
// AsyncValue Extensions - إضافات القيم غير المتزامنة
// =============================================================================

/// Enhanced AsyncValue extensions for consistent state handling
extension SahoolAsyncValueX<T> on AsyncValue<T> {
  /// Returns true if loading or refreshing
  bool get isLoadingOrRefreshing => isLoading || isRefreshing;

  /// Safely get value or null (use built-in valueOrNull for simple cases)
  T? get safeValueOrNull => when(
        data: (data) => data,
        loading: () => null,
        error: (_, __) => null,
      );

  /// Transform data with a mapper function
  AsyncValue<R> mapData<R>(R Function(T data) mapper) {
    return when(
      data: (data) => AsyncData(mapper(data)),
      loading: () => const AsyncLoading(),
      error: (error, stack) => AsyncError(error, stack),
    );
  }

  /// Execute different callbacks based on state
  void execute({
    void Function(T data)? onData,
    void Function()? onLoading,
    void Function(Object error, StackTrace? stack)? onError,
  }) {
    when(
      data: (data) {
        onData?.call(data);
        return null;
      },
      loading: () {
        onLoading?.call();
        return null;
      },
      error: (error, stack) {
        onError?.call(error, stack);
        return null;
      },
    );
  }
}

// =============================================================================
// Cached Provider - مزود مع تخزين مؤقت
// =============================================================================

/// Creates a provider with local cache fallback
/// يُنشئ مزود مع دعم التخزين المؤقت المحلي
class CachedAsyncNotifier<T> extends AutoDisposeAsyncNotifier<T> {
  final String cacheKey;
  final Future<T> Function() fetchData;
  final T Function(Map<String, dynamic> json)? fromJson;
  final Map<String, dynamic> Function(T data)? toJson;
  final Duration cacheDuration;
  final bool offlineFirst;

  CachedAsyncNotifier({
    required this.cacheKey,
    required this.fetchData,
    this.fromJson,
    this.toJson,
    this.cacheDuration = const Duration(hours: 1),
    this.offlineFirst = true,
  });

  SharedPreferences? _prefs;

  @override
  Future<T> build() async {
    _prefs ??= await SharedPreferences.getInstance();

    if (offlineFirst) {
      // Try cache first
      final cached = await _getCachedData();
      if (cached != null) {
        // Return cached data immediately, refresh in background
        _refreshInBackground();
        return cached;
      }
    }

    try {
      final data = await fetchData();
      await _cacheData(data);
      return data;
    } catch (e) {
      // If fetch fails, try cache as fallback
      final cached = await _getCachedData();
      if (cached != null) {
        AppLogger.w('Using cached data due to fetch error: $e', tag: 'CACHE');
        return cached;
      }
      rethrow;
    }
  }

  Future<T?> _getCachedData() async {
    if (fromJson == null) return null;

    final jsonStr = _prefs?.getString(cacheKey);
    final timestamp = _prefs?.getInt('${cacheKey}_timestamp');

    if (jsonStr == null || timestamp == null) return null;

    // Check if cache is expired
    final cacheTime = DateTime.fromMillisecondsSinceEpoch(timestamp);
    if (DateTime.now().difference(cacheTime) > cacheDuration) {
      return null;
    }

    try {
      final json = jsonDecode(jsonStr) as Map<String, dynamic>;
      return fromJson!(json);
    } catch (e) {
      AppLogger.e('Failed to parse cached data', tag: 'CACHE', error: e);
      return null;
    }
  }

  Future<void> _cacheData(T data) async {
    if (toJson == null) return;

    try {
      final json = toJson!(data);
      await _prefs?.setString(cacheKey, jsonEncode(json));
      await _prefs?.setInt(
        '${cacheKey}_timestamp',
        DateTime.now().millisecondsSinceEpoch,
      );
    } catch (e) {
      AppLogger.e('Failed to cache data', tag: 'CACHE', error: e);
    }
  }

  void _refreshInBackground() {
    Future(() async {
      try {
        final data = await fetchData();
        await _cacheData(data);
        state = AsyncData(data);
      } catch (e) {
        // Silent fail for background refresh
        AppLogger.w('Background refresh failed: $e', tag: 'CACHE');
      }
    });
  }

  /// Force refresh from network
  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final data = await fetchData();
      await _cacheData(data);
      return data;
    });
  }

  /// Clear cached data
  Future<void> clearCache() async {
    await _prefs?.remove(cacheKey);
    await _prefs?.remove('${cacheKey}_timestamp');
  }
}

// =============================================================================
// Retry Logic - منطق إعادة المحاولة
// =============================================================================

/// Retry configuration
/// تكوين إعادة المحاولة
class RetryConfig {
  final int maxRetries;
  final Duration initialDelay;
  final double backoffMultiplier;
  final Duration maxDelay;
  final bool Function(Exception)? shouldRetry;

  const RetryConfig({
    this.maxRetries = 3,
    this.initialDelay = const Duration(seconds: 1),
    this.backoffMultiplier = 2.0,
    this.maxDelay = const Duration(seconds: 30),
    this.shouldRetry,
  });

  static const RetryConfig none = RetryConfig(maxRetries: 0);
  static const RetryConfig standard = RetryConfig();
  static const RetryConfig aggressive = RetryConfig(
    maxRetries: 5,
    initialDelay: Duration(milliseconds: 500),
    backoffMultiplier: 1.5,
  );
}

/// Execute function with retry logic
/// تنفيذ دالة مع منطق إعادة المحاولة
Future<T> withRetry<T>(
  Future<T> Function() fn, {
  RetryConfig config = RetryConfig.standard,
  void Function(int attempt, Exception error)? onRetry,
}) async {
  int attempt = 0;
  Duration delay = config.initialDelay;

  while (true) {
    try {
      return await fn();
    } on Exception catch (e) {
      attempt++;

      // Check if we should retry
      if (attempt >= config.maxRetries) rethrow;
      if (config.shouldRetry != null && !config.shouldRetry!(e)) rethrow;

      // Notify retry
      onRetry?.call(attempt, e);
      AppLogger.w('Retry attempt $attempt after error: $e', tag: 'RETRY');

      // Wait with exponential backoff
      await Future<void>.delayed(delay);
      delay = Duration(
        milliseconds: (delay.inMilliseconds * config.backoffMultiplier).toInt(),
      );
      if (delay > config.maxDelay) delay = config.maxDelay;
    }
  }
}

// =============================================================================
// Connectivity-Aware Provider - مزود مُدرك للاتصال
// =============================================================================

/// State for connectivity-aware data
/// حالة البيانات المُدركة للاتصال
class ConnectivityAwareState<T> {
  final T? data;
  final bool isOnline;
  final bool isStale;
  final DateTime? lastUpdated;
  final Object? error;

  const ConnectivityAwareState({
    this.data,
    this.isOnline = true,
    this.isStale = false,
    this.lastUpdated,
    this.error,
  });

  ConnectivityAwareState<T> copyWith({
    T? data,
    bool? isOnline,
    bool? isStale,
    DateTime? lastUpdated,
    Object? error,
  }) {
    return ConnectivityAwareState(
      data: data ?? this.data,
      isOnline: isOnline ?? this.isOnline,
      isStale: isStale ?? this.isStale,
      lastUpdated: lastUpdated ?? this.lastUpdated,
      error: error,
    );
  }

  bool get hasData => data != null;
  bool get hasError => error != null;
  bool get needsRefresh => isStale || (isOnline && !hasData);
}

/// Provider that handles online/offline state transitions
/// مزود يتعامل مع تحولات حالة الاتصال
abstract class ConnectivityAwareNotifier<T>
    extends AutoDisposeNotifier<ConnectivityAwareState<T>> {
  /// Fetch data from network
  Future<T> fetchFromNetwork();

  /// Load data from local cache
  Future<T?> loadFromCache();

  /// Save data to local cache
  Future<void> saveToCache(T data);

  /// Duration after which data is considered stale
  Duration get staleDuration => const Duration(minutes: 30);

  @override
  ConnectivityAwareState<T> build() {
    _initialize();
    return const ConnectivityAwareState();
  }

  Future<void> _initialize() async {
    // Load cached data first
    final cached = await loadFromCache();
    if (cached != null) {
      state = state.copyWith(
        data: cached,
        isStale: true,
      );
    }

    // Listen to network changes
    ref.listen(networkStatusProvider, (previous, next) {
      if (next.isOnline && !(previous?.isOnline ?? false)) {
        // Just came online, refresh
        refresh();
      }
      state = state.copyWith(isOnline: next.isOnline);
    });

    // Initial network check
    final isOnline = ref.read(networkStatusProvider).isOnline;
    state = state.copyWith(isOnline: isOnline);

    if (isOnline) {
      await refresh();
    }
  }

  /// Refresh data from network
  Future<void> refresh() async {
    if (!state.isOnline) {
      AppLogger.w('Cannot refresh while offline', tag: 'CONNECTIVITY');
      return;
    }

    try {
      final data = await fetchFromNetwork();
      await saveToCache(data);
      state = state.copyWith(
        data: data,
        isStale: false,
        lastUpdated: DateTime.now(),
        error: null,
      );
    } catch (e) {
      state = state.copyWith(error: e);
      AppLogger.e('Failed to refresh data', tag: 'CONNECTIVITY', error: e);
    }
  }

  /// Check if data should be refreshed
  bool _isDataStale() {
    if (state.lastUpdated == null) return true;
    return DateTime.now().difference(state.lastUpdated!) > staleDuration;
  }
}

// =============================================================================
// Debounced Provider - مزود مع تأخير
// =============================================================================

/// Provider that debounces rapid state changes
/// مزود يؤخر تغييرات الحالة السريعة
mixin DebouncedNotifier<T> on AutoDisposeNotifier<T> {
  Timer? _debounceTimer;

  /// Update state with debouncing
  void updateDebounced(
    T newState, {
    Duration duration = const Duration(milliseconds: 300),
  }) {
    _debounceTimer?.cancel();
    _debounceTimer = Timer(duration, () {
      state = newState;
    });
  }

  @override
  void dispose() {
    _debounceTimer?.cancel();
  }
}

// =============================================================================
// Pagination Support - دعم التصفح
// =============================================================================

/// State for paginated data
/// حالة البيانات المُقسمة لصفحات
class PaginatedState<T> {
  final List<T> items;
  final int page;
  final int pageSize;
  final bool hasMore;
  final bool isLoadingMore;
  final Object? error;

  const PaginatedState({
    this.items = const [],
    this.page = 0,
    this.pageSize = 20,
    this.hasMore = true,
    this.isLoadingMore = false,
    this.error,
  });

  PaginatedState<T> copyWith({
    List<T>? items,
    int? page,
    int? pageSize,
    bool? hasMore,
    bool? isLoadingMore,
    Object? error,
  }) {
    return PaginatedState(
      items: items ?? this.items,
      page: page ?? this.page,
      pageSize: pageSize ?? this.pageSize,
      hasMore: hasMore ?? this.hasMore,
      isLoadingMore: isLoadingMore ?? this.isLoadingMore,
      error: error,
    );
  }

  bool get isEmpty => items.isEmpty;
  bool get isNotEmpty => items.isNotEmpty;
  int get length => items.length;
}

/// Base class for paginated data providers
/// فئة أساسية لمزودي البيانات المُقسمة لصفحات
abstract class PaginatedNotifier<T>
    extends AutoDisposeNotifier<AsyncValue<PaginatedState<T>>> {
  /// Fetch a page of data
  Future<List<T>> fetchPage(int page, int pageSize);

  int get pageSize => 20;

  @override
  AsyncValue<PaginatedState<T>> build() {
    _loadInitialPage();
    return const AsyncLoading();
  }

  Future<void> _loadInitialPage() async {
    state = await AsyncValue.guard(() async {
      final items = await fetchPage(0, pageSize);
      return PaginatedState(
        items: items,
        page: 0,
        pageSize: pageSize,
        hasMore: items.length >= pageSize,
      );
    });
  }

  /// Load next page
  Future<void> loadMore() async {
    final current = state.valueOrNull;
    if (current == null || !current.hasMore || current.isLoadingMore) return;

    state = AsyncData(current.copyWith(isLoadingMore: true));

    try {
      final nextPage = current.page + 1;
      final newItems = await fetchPage(nextPage, pageSize);

      state = AsyncData(current.copyWith(
        items: [...current.items, ...newItems],
        page: nextPage,
        hasMore: newItems.length >= pageSize,
        isLoadingMore: false,
      ));
    } catch (e) {
      state = AsyncData(current.copyWith(
        isLoadingMore: false,
        error: e,
      ));
    }
  }

  /// Refresh all data
  Future<void> refresh() async {
    state = const AsyncLoading();
    await _loadInitialPage();
  }
}

// =============================================================================
// State Persistence - حفظ الحالة
// =============================================================================

/// Mixin for persisting provider state to local storage
/// خلط لحفظ حالة المزود في التخزين المحلي
mixin PersistentStateMixin<T> on AutoDisposeNotifier<T> {
  String get persistenceKey;

  /// Convert state to JSON for storage
  Map<String, dynamic>? toJson(T state);

  /// Create state from stored JSON
  T? fromJson(Map<String, dynamic> json);

  SharedPreferences? _prefs;

  /// Load persisted state
  Future<T?> loadPersistedState() async {
    _prefs ??= await SharedPreferences.getInstance();
    final jsonStr = _prefs?.getString(persistenceKey);
    if (jsonStr == null) return null;

    try {
      final json = jsonDecode(jsonStr) as Map<String, dynamic>;
      return fromJson(json);
    } catch (e) {
      AppLogger.e('Failed to load persisted state', tag: 'PERSIST', error: e);
      return null;
    }
  }

  /// Persist current state
  Future<void> persistState() async {
    _prefs ??= await SharedPreferences.getInstance();
    final json = toJson(state);
    if (json != null) {
      await _prefs?.setString(persistenceKey, jsonEncode(json));
    }
  }

  /// Clear persisted state
  Future<void> clearPersistedState() async {
    _prefs ??= await SharedPreferences.getInstance();
    await _prefs?.remove(persistenceKey);
  }
}
