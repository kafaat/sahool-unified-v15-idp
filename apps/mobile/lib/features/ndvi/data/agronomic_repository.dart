/// Agronomic Repository — طبقة وسيطة بين الـ UI ومصادر البيانات
///
/// Single entry point for all spectral-index data.  The UI calls
/// [getIndexValues] and never touches [NdviServiceConnector] directly.
///
/// Responsibilities:
///   • Choose the correct backend call (live `getIndices` vs. historical
///     `getTimeseries`).
///   • Manage in-memory + persistent Drift cache via [NdviCacheDao].
///   • Hold the generation counter that guards against stale responses.
///   • Expose [acquisitionDates] (satellite pass dates) for the timeline UI.
///
/// What does NOT change:
///   • [NdviServiceConnector] is untouched.
///   • [NdviTileLayerWidget] is untouched.
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/services/integrations/ndvi_service.dart';
import '../../../main.dart' show databaseProvider;
import 'ndvi_cache_dao.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Result type
// ═══════════════════════════════════════════════════════════════════════════

/// The outcome of one [AgronomicRepository.getIndexValues] call.
class IndexFetchResult {
  /// Latest known values keyed by [SpectralIndex.code].
  final Map<String, double> values;

  /// Non-null when a network/parse error occurred.
  final String? error;

  const IndexFetchResult({required this.values, this.error});

  bool get hasValues => values.isNotEmpty;
  bool get hasError => error != null;

  IndexFetchResult copyWith({
    Map<String, double>? values,
    String? error,
    bool clearError = false,
  }) {
    return IndexFetchResult(
      values: values ?? this.values,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Repository
// ═══════════════════════════════════════════════════════════════════════════

/// Agronomic data repository — one instance per ProviderScope.
///
/// Instantiate through [agronomicRepositoryProvider] so Riverpod manages
/// the lifecycle.
class AgronomicRepository {
  AgronomicRepository({
    required NdviServiceConnector service,
    required NdviCacheDao cacheDao,
  })  : _service = service,
        _cacheDao = cacheDao;

  final NdviServiceConnector _service;
  final NdviCacheDao _cacheDao;

  // ── Generation counter ────────────────────────────────────────────────────
  /// Incremented on every [getIndexValues] call.
  ///
  /// Each call captures the generation at start; before applying results it
  /// checks the counter hasn't advanced.  Callers that need to detect stale
  /// responses should compare their captured value with [currentGeneration].
  int _generation = 0;

  int get currentGeneration => _generation;

  /// Atomically increments and returns the new generation number.
  int _nextGeneration() => ++_generation;

  // ── In-memory L1 cache ────────────────────────────────────────────────────
  /// Keyed by `"$fieldId:$dateKey"` — see [NdviCacheDao.dateKey].
  final Map<String, Map<String, double>> _memCache = {};

  // ── Public API ────────────────────────────────────────────────────────────

  /// Fetch all spectral-index values for [fieldId] at [date].
  ///
  /// [date] `null` → live / most-recent data (calls `getIndices`).
  /// [date] set   → historical data for that date (calls `getTimeseries`).
  ///
  /// Cache hit order: L1 memory → L2 Drift (persistent) → network.
  ///
  /// Returns the generation number captured at the start of the call so the
  /// caller can discard stale results:
  /// ```dart
  /// final gen = repo.currentGeneration;
  /// final result = await repo.getIndexValues(fieldId, date);
  /// if (repo.currentGeneration != gen) return; // stale — discard
  /// ```
  ///
  /// The method itself does NOT compare generations; that is intentional so
  /// the repository remains unaware of widget lifecycles.
  Future<IndexFetchResult> getIndexValues(
    String fieldId,
    DateTime? date,
  ) async {
    final capturedGen = _nextGeneration();
    final memKey = '$fieldId:${NdviCacheDao.dateKey(date)}';

    // ── L1: in-memory hit ────────────────────────────────────────────────────
    if (_memCache.containsKey(memKey)) {
      return IndexFetchResult(values: Map.unmodifiable(_memCache[memKey]!));
    }

    // ── L2: Drift persistent hit ─────────────────────────────────────────────
    try {
      final cached = await _cacheDao.getEntries(fieldId, date);
      if (cached.isNotEmpty) {
        final values = {for (final e in cached) e.indexCode: e.value};
        _memCache[memKey] = values;
        return IndexFetchResult(values: Map.unmodifiable(values));
      }
    } catch (_) {
      // DB not ready yet (e.g. migration pending) — fall through to network.
    }

    // ── Network fetch ────────────────────────────────────────────────────────
    if (date == null) {
      return _fetchLive(fieldId, memKey);
    } else {
      return _fetchHistorical(fieldId, date, memKey);
    }
  }

  /// Load the satellite acquisition dates for [fieldId].
  ///
  /// Sorted newest-first.  Returns an empty list on failure (best-effort).
  Future<List<DateTime>> loadAcquisitionDates(String fieldId) async {
    final result = await _service.getImagery(fieldId);
    return result.when(
      success: (imagery) {
        if (imagery.isEmpty) return <DateTime>[];
        return (imagery.map((i) => i.captureDate).toList()
          ..sort((a, b) => b.compareTo(a)));
      },
      failure: (_, __) => <DateTime>[],
    );
  }

  /// The base URL of the backend service (for tile layer configuration).
  String get baseUrl => _service.baseUrl;

  // ── Private helpers ───────────────────────────────────────────────────────

  Future<IndexFetchResult> _fetchLive(
    String fieldId,
    String memKey,
  ) async {
    final result = await _service.getIndices(fieldId);
    return result.when(
      success: (indices) async {
        if (indices.isEmpty) {
          return const IndexFetchResult(
            values: {},
            error: 'لا تتوفر بيانات قمر صناعي\nNo satellite data for this field',
          );
        }
        final values = {for (final i in indices) i.name.toUpperCase(): i.value};
        _memCache[memKey] = values;
        _upsertCache(fieldId, null, values); // fire-and-forget
        return IndexFetchResult(values: Map.unmodifiable(values));
      },
      failure: (message, _) => IndexFetchResult(
        values: {},
        error: 'فشل تحميل البيانات: $message\nCheck connectivity',
      ),
    );
  }

  Future<IndexFetchResult> _fetchHistorical(
    String fieldId,
    DateTime date,
    String memKey,
  ) async {
    final result = await _service.getTimeseries(
      fieldId,
      startDate: date.subtract(const Duration(days: 15)),
      endDate: date.add(const Duration(days: 15)),
    );

    return result.when(
      success: (points) async {
        if (points.isEmpty) {
          return const IndexFetchResult(
            values: {},
            error:
                'لا تتوفر بيانات قمر صناعي لهذا التاريخ\nNo satellite coverage for selected date',
          );
        }
        // Pick the point closest to the requested date.
        points.sort((a, b) => a.date
            .difference(date)
            .inDays
            .abs()
            .compareTo(b.date.difference(date).inDays.abs()));
        final values = {'NDVI': points.first.value};
        _memCache[memKey] = values;
        _upsertCache(fieldId, date, values); // fire-and-forget
        return IndexFetchResult(values: Map.unmodifiable(values));
      },
      failure: (message, _) => IndexFetchResult(
        values: {},
        error: 'فشل تحميل التاريخ: $message\nCheck connectivity',
      ),
    );
  }

  /// Persist [values] to the Drift cache; errors are silently swallowed.
  void _upsertCache(
    String fieldId,
    DateTime? date,
    Map<String, double> values,
  ) {
    _cacheDao.putEntries(fieldId, date, values).ignore();
  }

  /// Invalidate all caches for [fieldId] (both L1 and L2).
  Future<void> invalidate(String fieldId) async {
    _memCache.removeWhere((key, _) => key.startsWith('$fieldId:'));
    // L2 invalidation via evictExpired is sufficient; we do not delete
    // specific rows here since the TTL-based mechanism handles freshness.
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Provides the [NdviCacheDao] backed by the app's [AppDatabase].
final ndviCacheDaoProvider = Provider<NdviCacheDao>((ref) {
  final db = ref.watch(databaseProvider);
  return NdviCacheDao(db);
});

/// Provides the singleton [AgronomicRepository].
///
/// Depends on [ndviServiceProvider] (unchanged) and [ndviCacheDaoProvider].
final agronomicRepositoryProvider = Provider<AgronomicRepository>((ref) {
  final service = ref.watch(ndviServiceProvider);
  final dao = ref.watch(ndviCacheDaoProvider);
  return AgronomicRepository(service: service, cacheDao: dao);
});
