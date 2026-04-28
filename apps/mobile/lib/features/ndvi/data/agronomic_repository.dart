/// Agronomic Repository — طبقة وسيطة بين الـ UI ومصادر البيانات
///
/// Single entry point for all spectral-index data.  The UI calls
/// [getIndexValues] (bulk) or [getIndexValue] (single index) and never touches
/// [NdviServiceConnector] directly.
///
/// Responsibilities:
///   • Choose the correct backend call (live `getIndices` vs. historical
///     `getTimeseries`).
///   • Manage in-memory + persistent Drift cache via [NdviCacheDao].
///   • Own TTL policy for both live and historical entries.
///   • Hold the generation counter that guards against stale responses.
///   • Enforce [SpectralIndex.requiresHistorical] so callers cannot
///     accidentally request live data for historical-only indices.
///   • Expose [acquisitionDates] (satellite pass dates) for the timeline UI.
///
/// What does NOT change:
///   • [NdviServiceConnector] is untouched.
///   • [NdviTileLayerWidget] is untouched.
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/services/integrations/ndvi_service.dart';
import '../../../main.dart' show databaseProvider;
import '../domain/spectral_index.dart';
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

  // ── TTL policy (owned here, not in the DAO) ───────────────────────────────
  /// Live / most-recent data expires quickly (server may update it hourly).
  static const Duration _liveTtl = Duration(hours: 1);

  /// Historical satellite data is immutable — long TTL reduces network calls.
  static const Duration _historicalTtl = Duration(hours: 24);

  // ── Generation counter ────────────────────────────────────────────────────
  /// Seeded from the current epoch milliseconds so that two repository
  /// instances (e.g. after a ProviderScope recreation) never start from the
  /// same generation value, preventing cross-instance stale-check confusion.
  ///
  /// Incremented on every [getIndexValues] call.  Each call captures the
  /// generation at start; before applying results it checks the counter hasn't
  /// advanced (see caller pattern in [FieldMapScreen._loadIndexValues]).
  int _generation = DateTime.now().millisecondsSinceEpoch;

  int get currentGeneration => _generation;

  /// Increments the generation counter and returns the new value.
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
  /// Call pattern for stale-response detection:
  /// ```dart
  /// final genAtStart = repo.currentGeneration;
  /// final result = await repo.getIndexValues(fieldId, date);
  /// if (repo.currentGeneration != genAtStart + 1) return; // stale — discard
  /// ```
  Future<IndexFetchResult> getIndexValues(
    String fieldId,
    DateTime? date,
  ) async {
    _nextGeneration();
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

  /// Returns the value for a single [index] at [date] for [fieldId].
  ///
  /// This is the single-index API described in the Agronomic Layer v2 design.
  /// It enforces [SpectralIndex.requiresHistorical]: if [date] is `null` and
  /// the index is only available from the historical timeseries endpoint, an
  /// [ArgumentError] is thrown to prevent silent data gaps.
  ///
  /// Returns `null` if the bulk fetch succeeded but the index was absent from
  /// the response (e.g. sensor not available for the field).
  Future<double?> getIndexValue(
    String fieldId,
    DateTime? date,
    SpectralIndex index,
  ) async {
    if (date == null && index.requiresHistorical) {
      throw ArgumentError(
        '${index.code} is only available from the historical timeseries '
        'endpoint. Pass a non-null date, or choose a different index for '
        'live display.',
      );
    }
    final result = await getIndexValues(fieldId, date);
    return result.values[index.code];
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

  /// Invalidate all caches for [fieldId] (both L1 in-memory and L2 Drift).
  ///
  /// Call when external factors make the cached data stale — e.g. a field
  /// boundary change, an API version bump, or an explicit user refresh.
  Future<void> invalidate(String fieldId) async {
    _memCache.removeWhere((key, _) => key.startsWith('$fieldId:'));
    await _cacheDao.deleteField(fieldId);
  }

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
        final raw = {for (final i in indices) i.name.toUpperCase(): i.value};

        // Guard: only cache values that are finite numbers (no NaN / ±Inf).
        final values = Map.unmodifiable(
          {for (final e in raw.entries) if (e.value.isFinite) e.key: e.value},
        );

        if (values.isEmpty) {
          return const IndexFetchResult(
            values: {},
            error: 'بيانات المؤشرات غير صالحة\nIndex values returned invalid data',
          );
        }

        _memCache[memKey] = values;
        _upsertCache(fieldId, null, values);
        return IndexFetchResult(values: values);
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
        final raw = {'NDVI': points.first.value};

        // Guard: only cache values that are finite numbers (no NaN / ±Inf).
        final values = Map.unmodifiable(
          {for (final e in raw.entries) if (e.value.isFinite) e.key: e.value},
        );

        if (values.isEmpty) {
          return const IndexFetchResult(
            values: {},
            error: 'بيانات المؤشرات غير صالحة\nIndex values returned invalid data',
          );
        }

        _memCache[memKey] = values;
        _upsertCache(fieldId, date, values);
        return IndexFetchResult(values: values);
      },
      failure: (message, _) => IndexFetchResult(
        values: {},
        error: 'فشل تحميل التاريخ: $message\nCheck connectivity',
      ),
    );
  }

  /// Persist [values] to the Drift cache; errors are silently swallowed.
  ///
  /// TTL is computed here (repository policy), not in the DAO.
  void _upsertCache(
    String fieldId,
    DateTime? date,
    Map<String, double> values,
  ) {
    final ttl = date == null ? _liveTtl : _historicalTtl;
    final expiresAt = DateTime.now().add(ttl);
    _cacheDao.putEntries(fieldId, date, values, expiresAt).ignore();
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
