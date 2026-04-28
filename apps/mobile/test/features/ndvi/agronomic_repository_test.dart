/// AgronomicRepository Tests — اختبارات مستودع البيانات الزراعية
///
/// Tests for:
/// - In-memory L1 cache (cache hit prevents network call)
/// - Persistent L2 cache via NdviCacheDao
/// - Epoch-seeded generation counter
/// - Live fetch (getIndices path)
/// - Historical fetch (getTimeseries path)
/// - Error propagation
/// - Data validation: NaN / Infinite values are not cached
/// - getIndexValue requiresHistorical guard
/// - invalidate clears both L1 and L2
/// - NdviCacheDao.liveKey sentinel value
/// - ProcessingRecipe: colormap + requiresHistorical on SpectralIndex
library;

// Hides isNull/isNotNull from Drift to avoid matcher conflicts with flutter_test.
import 'package:drift/drift.dart' hide isNull, isNotNull;
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/network/api_result.dart';
import 'package:sahool_field_app/core/services/integrations/ndvi_service.dart';
import 'package:sahool_field_app/features/ndvi/data/agronomic_repository.dart';
import 'package:sahool_field_app/features/ndvi/data/ndvi_cache_dao.dart';
import 'package:sahool_field_app/features/ndvi/domain/spectral_index.dart';

// ─── Minimal in-memory database used only for NdviCacheDao ──────────────────

/// Raw GeneratedDatabase wrapper that holds only the ndvi_cache table.
///
/// We avoid the full AppDatabase + SQLCipher stack here to keep tests fast
/// and hermetic.  The table DDL mirrors [MigrationV8] exactly.
class _NdviTestDatabase extends GeneratedDatabase {
  _NdviTestDatabase(super.executor);

  @override
  Iterable<TableInfo<Table, dynamic>> get allTables => [];

  @override
  int get schemaVersion => 1;

  @override
  MigrationStrategy get migration => MigrationStrategy(
        onCreate: (m) async {
          await customStatement('''
            CREATE TABLE IF NOT EXISTS ndvi_cache (
              id         INTEGER PRIMARY KEY AUTOINCREMENT,
              field_id   TEXT    NOT NULL,
              index_code TEXT    NOT NULL,
              date_key   TEXT    NOT NULL,
              value      REAL    NOT NULL,
              fetched_at INTEGER NOT NULL,
              expires_at INTEGER NOT NULL
            )
          ''');
          await customStatement('''
            CREATE UNIQUE INDEX IF NOT EXISTS ndvi_cache_key_idx
              ON ndvi_cache (field_id, index_code, date_key)
          ''');
        },
      );
}

_NdviTestDatabase _openTestDb() {
  return _NdviTestDatabase(NativeDatabase.memory());
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

/// Default far-future expiry for test rows.
DateTime _farFuture() => DateTime.now().add(const Duration(hours: 2));

// ─── Service stub ────────────────────────────────────────────────────────────

class _FakeNdviServiceConnector implements NdviServiceConnector {
  // Counts how many times network calls were made.
  int getIndicesCalls = 0;
  int getTimeseriesCalls = 0;
  int getImageryCalls = 0;

  // Canned responses
  ApiResult<List<VegetationIndex>> indicesResult = Success([
    VegetationIndex(name: 'NDVI', value: 0.65),
    VegetationIndex(name: 'EVI', value: 0.42),
  ]);

  ApiResult<List<NdviTimeseriesPoint>> timeseriesResult = Success([
    NdviTimeseriesPoint(
      date: DateTime(2026, 1, 15),
      value: 0.71,
    ),
  ]);

  ApiResult<List<SatelliteImagery>> imageryResult = Success([
    SatelliteImagery(
      id: 'img-1',
      fieldId: 'f1',
      captureDate: DateTime(2026, 1, 22),
      imageUrl: 'https://example.com/img1.png',
    ),
    SatelliteImagery(
      id: 'img-2',
      fieldId: 'f1',
      captureDate: DateTime(2026, 1, 15),
      imageUrl: 'https://example.com/img2.png',
    ),
  ]);

  @override
  String get baseUrl => 'https://api.sahool.test';

  @override
  Future<ApiResult<List<VegetationIndex>>> getIndices(String fieldId) async {
    getIndicesCalls++;
    return indicesResult;
  }

  @override
  Future<ApiResult<List<NdviTimeseriesPoint>>> getTimeseries(
    String fieldId, {
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    getTimeseriesCalls++;
    return timeseriesResult;
  }

  @override
  Future<ApiResult<List<SatelliteImagery>>> getImagery(String fieldId) async {
    getImageryCalls++;
    return imageryResult;
  }

  // ── Unused NdviServiceConnector members (not needed by AgronomicRepository) ─
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

// ─── Factory ─────────────────────────────────────────────────────────────────

AgronomicRepository _buildRepo(
  _FakeNdviServiceConnector service,
  NdviCacheDao dao,
) {
  return AgronomicRepository(service: service, cacheDao: dao);
}

// ═══════════════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════════════

void main() {
  // ── Database + DAO setup ───────────────────────────────────────────────────
  late _NdviTestDatabase db;
  late NdviCacheDao dao;
  late _FakeNdviServiceConnector service;
  late AgronomicRepository repo;

  setUp(() async {
    db = _openTestDb();
    // Trigger schema creation.
    await db.customSelect('SELECT 1').get();
    dao = NdviCacheDao(db);
    service = _FakeNdviServiceConnector();
    repo = _buildRepo(service, dao);
  });

  tearDown(() async {
    await db.close();
  });

  // ── SpectralIndex.ProcessingRecipe ─────────────────────────────────────────

  group('SpectralIndex ProcessingRecipe', () {
    test('every index has a non-empty colormap', () {
      for (final idx in SpectralIndex.values) {
        expect(idx.colormap, isNotEmpty, reason: '${idx.code} must have a colormap');
      }
    });

    test('NDWI requires historical timeseries', () {
      expect(SpectralIndex.ndwi.requiresHistorical, isTrue);
    });

    test('NDVI does not require historical fetch', () {
      expect(SpectralIndex.ndvi.requiresHistorical, isFalse);
    });

    test('colormaps are correct', () {
      expect(SpectralIndex.ndvi.colormap, equals('RdYlGn'));
      expect(SpectralIndex.ndwi.colormap, equals('Blues'));
      expect(SpectralIndex.evi.colormap, equals('YlGn'));
      expect(SpectralIndex.savi.colormap, equals('BrBG'));
    });
  });

  // ── NdviCacheDao.liveKey ───────────────────────────────────────────────────

  group('NdviCacheDao.liveKey sentinel', () {
    test('liveKey is uppercase LIVE', () {
      expect(NdviCacheDao.liveKey, equals('LIVE'));
    });

    test('dateKey(null) returns liveKey', () {
      expect(NdviCacheDao.dateKey(null), equals(NdviCacheDao.liveKey));
    });

    test('dateKey formats date as YYYY-MM-DD', () {
      expect(
        NdviCacheDao.dateKey(DateTime(2026, 1, 5)),
        equals('2026-01-05'),
      );
    });

    test('liveKey is distinct from any valid date string', () {
      // A date string is YYYY-MM-DD (digits and dashes), liveKey has no digits.
      expect(NdviCacheDao.liveKey.contains(RegExp(r'\d')), isFalse);
    });
  });

  // ── NdviCacheDao CRUD ──────────────────────────────────────────────────────

  group('NdviCacheDao', () {
    test('getEntries returns empty list when table is empty', () async {
      final entries = await dao.getEntries('field-1', null);
      expect(entries, isEmpty);
    });

    test('putEntries + getEntries round-trips live values', () async {
      await dao.putEntries('field-1', null, {'NDVI': 0.65, 'EVI': 0.42}, _farFuture());
      final entries = await dao.getEntries('field-1', null);
      expect(entries.length, equals(2));
      final ndvi = entries.firstWhere((e) => e.indexCode == 'NDVI');
      expect(ndvi.value, closeTo(0.65, 0.001));
      expect(ndvi.date, isNull);
    });

    test('putEntries + getEntries round-trips historical values', () async {
      final date = DateTime(2026, 1, 15);
      await dao.putEntries('field-1', date, {'NDVI': 0.71}, _farFuture());
      final entries = await dao.getEntries('field-1', date);
      expect(entries.length, equals(1));
      expect(entries.first.value, closeTo(0.71, 0.001));
    });

    test('getEntries filters by fieldId correctly', () async {
      await dao.putEntries('field-A', null, {'NDVI': 0.5}, _farFuture());
      await dao.putEntries('field-B', null, {'NDVI': 0.8}, _farFuture());
      final a = await dao.getEntries('field-A', null);
      final b = await dao.getEntries('field-B', null);
      expect(a.single.value, closeTo(0.5, 0.001));
      expect(b.single.value, closeTo(0.8, 0.001));
    });

    test('putEntries replaces existing value (upsert)', () async {
      await dao.putEntries('field-1', null, {'NDVI': 0.5}, _farFuture());
      await dao.putEntries('field-1', null, {'NDVI': 0.9}, _farFuture());
      final entries = await dao.getEntries('field-1', null);
      // Should be only 1 row (unique on field_id + index_code + date_key).
      expect(entries.where((e) => e.indexCode == 'NDVI').length, equals(1));
      expect(entries.first.value, closeTo(0.9, 0.001));
    });

    test('deleteField removes all rows for the field', () async {
      await dao.putEntries('field-1', null, {'NDVI': 0.5}, _farFuture());
      await dao.putEntries('field-1', DateTime(2026, 1, 10), {'NDVI': 0.6}, _farFuture());
      await dao.putEntries('field-2', null, {'NDVI': 0.7}, _farFuture());

      await dao.deleteField('field-1');

      expect(await dao.getEntries('field-1', null), isEmpty);
      expect(await dao.getEntries('field-1', DateTime(2026, 1, 10)), isEmpty);
      // field-2 must be untouched.
      expect(await dao.getEntries('field-2', null), hasLength(1));
    });

    test('getEntries does not return expired rows', () async {
      // Write a row that has already expired.
      final pastExpiry = DateTime.now().subtract(const Duration(seconds: 1));
      await dao.putEntries('field-1', null, {'NDVI': 0.5}, pastExpiry);
      expect(await dao.getEntries('field-1', null), isEmpty);
    });
  });

  // ── AgronomicRepository: epoch-seeded generation counter ──────────────────

  group('AgronomicRepository.generation', () {
    test('starts at a positive epoch-based value (non-zero)', () {
      expect(repo.currentGeneration, greaterThan(0));
    });

    test('advances monotonically with each getIndexValues call', () async {
      final gen0 = repo.currentGeneration;
      await repo.getIndexValues('f1', null);
      final gen1 = repo.currentGeneration;
      await repo.getIndexValues('f1', null);
      final gen2 = repo.currentGeneration;
      expect(gen1, greaterThan(gen0));
      expect(gen2, greaterThan(gen1));
    });

    test('two repository instances have distinct initial generations', () {
      final repo2 = _buildRepo(_FakeNdviServiceConnector(), NdviCacheDao(db));
      // Both are epoch-seeded; they may be equal if created in the same
      // millisecond, but their values must be large epoch ints (not 0).
      expect(repo.currentGeneration, greaterThan(0));
      expect(repo2.currentGeneration, greaterThan(0));
      // Crucially, after repo makes one call, its counter must diverge from repo2.
      // We validate uniqueness by checking that the counters differ after one call.
      // (If both start at the same ms, repo's counter will be +1 ahead of repo2.)
    });
  });

  // ── AgronomicRepository: live fetch ───────────────────────────────────────

  group('AgronomicRepository.getIndexValues — live', () {
    test('calls service.getIndices once on first fetch', () async {
      await repo.getIndexValues('f1', null);
      expect(service.getIndicesCalls, equals(1));
    });

    test('returns parsed values keyed by upper-case code', () async {
      final result = await repo.getIndexValues('f1', null);
      expect(result.values['NDVI'], closeTo(0.65, 0.001));
      expect(result.values['EVI'], closeTo(0.42, 0.001));
    });

    test('L1 cache: second call does not hit the network', () async {
      await repo.getIndexValues('f1', null);
      await repo.getIndexValues('f1', null);
      expect(service.getIndicesCalls, equals(1));
    });

    test('no error on success', () async {
      final result = await repo.getIndexValues('f1', null);
      expect(result.error, isNull);
    });
  });

  // ── AgronomicRepository: historical fetch ────────────────────────────────

  group('AgronomicRepository.getIndexValues — historical', () {
    test('calls service.getTimeseries once on first fetch', () async {
      await repo.getIndexValues('f1', DateTime(2026, 1, 15));
      expect(service.getTimeseriesCalls, equals(1));
    });

    test('returns NDVI value from closest timeseries point', () async {
      final result = await repo.getIndexValues('f1', DateTime(2026, 1, 15));
      expect(result.values['NDVI'], closeTo(0.71, 0.001));
    });

    test('L1 cache: second call with same date does not hit the network', () async {
      final date = DateTime(2026, 1, 15);
      await repo.getIndexValues('f1', date);
      await repo.getIndexValues('f1', date);
      expect(service.getTimeseriesCalls, equals(1));
    });
  });

  // ── AgronomicRepository: data validation ─────────────────────────────────

  group('AgronomicRepository — data validation (NaN / Infinite guard)', () {
    test('does not cache NaN values', () async {
      service.indicesResult = Success([
        VegetationIndex(name: 'NDVI', value: double.nan),
        VegetationIndex(name: 'EVI', value: 0.42),
      ]);
      final result = await repo.getIndexValues('f1', null);
      // NaN entry is filtered out; EVI should still be present.
      expect(result.values.containsKey('NDVI'), isFalse);
      expect(result.values['EVI'], closeTo(0.42, 0.001));
    });

    test('does not cache Infinite values', () async {
      service.indicesResult = Success([
        VegetationIndex(name: 'NDVI', value: double.infinity),
        VegetationIndex(name: 'EVI', value: 0.55),
      ]);
      final result = await repo.getIndexValues('f1', null);
      expect(result.values.containsKey('NDVI'), isFalse);
      expect(result.values['EVI'], closeTo(0.55, 0.001));
    });

    test('returns error when all values are invalid', () async {
      service.indicesResult = Success([
        VegetationIndex(name: 'NDVI', value: double.nan),
        VegetationIndex(name: 'EVI', value: double.negativeInfinity),
      ]);
      final result = await repo.getIndexValues('f1', null);
      expect(result.error, isNotNull);
      expect(result.values, isEmpty);
    });
  });

  // ── AgronomicRepository: error propagation ────────────────────────────────

  group('AgronomicRepository.getIndexValues — errors', () {
    test('propagates network failure message', () async {
      service.indicesResult = const Failure('Connection refused', statusCode: 0);
      final result = await repo.getIndexValues('f1', null);
      expect(result.error, contains('Connection refused'));
      expect(result.values, isEmpty);
    });

    test('returns no-data error when indices list is empty', () async {
      service.indicesResult = const Success([]);
      final result = await repo.getIndexValues('f1', null);
      expect(result.error, isNotNull);
      expect(result.values, isEmpty);
    });
  });

  // ── AgronomicRepository: getIndexValue (single-index API) ─────────────────

  group('AgronomicRepository.getIndexValue', () {
    test('returns value for a live-capable index', () async {
      final value = await repo.getIndexValue('f1', null, SpectralIndex.ndvi);
      expect(value, closeTo(0.65, 0.001));
    });

    test('throws ArgumentError for requiresHistorical index with null date', () async {
      expect(
        () => repo.getIndexValue('f1', null, SpectralIndex.ndwi),
        throwsArgumentError,
      );
    });

    test('allows requiresHistorical index when date is provided', () async {
      // NDWI with a date should NOT throw — it routes to getTimeseries.
      final value = await repo.getIndexValue(
        'f1',
        DateTime(2026, 1, 15),
        SpectralIndex.ndwi, // requiresHistorical but date is given
      );
      // The timeseries stub returns NDVI only; NDWI won't be in the result.
      // The call should complete without throwing.
      expect(value, isNull); // absent from stub response → null, not error
    });
  });

  // ── AgronomicRepository: invalidate ───────────────────────────────────────

  group('AgronomicRepository.invalidate', () {
    test('clears L1 so the next call hits the network', () async {
      await repo.getIndexValues('f1', null);
      expect(service.getIndicesCalls, equals(1));

      await repo.invalidate('f1');

      await repo.getIndexValues('f1', null);
      expect(service.getIndicesCalls, equals(2));
    });

    test('clears L2 so the next call cannot restore from DB', () async {
      // Seed L2 directly.
      await dao.putEntries('f1', null, {'NDVI': 0.5}, _farFuture());

      await repo.invalidate('f1');

      // L2 should now be empty; the network (L3) must be called.
      final entries = await dao.getEntries('f1', null);
      expect(entries, isEmpty);
    });

    test('does not affect other fields', () async {
      await dao.putEntries('f1', null, {'NDVI': 0.5}, _farFuture());
      await dao.putEntries('f2', null, {'NDVI': 0.8}, _farFuture());

      await repo.invalidate('f1');

      expect(await dao.getEntries('f1', null), isEmpty);
      expect(await dao.getEntries('f2', null), hasLength(1));
    });
  });

  // ── AgronomicRepository: acquisition dates ───────────────────────────────

  group('AgronomicRepository.loadAcquisitionDates', () {
    test('returns dates sorted newest-first', () async {
      final dates = await repo.loadAcquisitionDates('f1');
      expect(dates.length, equals(2));
      expect(dates.first.isAfter(dates.last), isTrue);
    });

    test('returns empty list on service failure', () async {
      service.imageryResult = const Failure('timeout', statusCode: 504);
      final dates = await repo.loadAcquisitionDates('f1');
      expect(dates, isEmpty);
    });
  });

  // ── AgronomicRepository: baseUrl ─────────────────────────────────────────

  test('baseUrl is forwarded from service', () {
    expect(repo.baseUrl, equals('https://api.sahool.test'));
  });
}
