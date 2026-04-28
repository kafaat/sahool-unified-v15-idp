/// NDVI Cache DAO — Persistent spectral-index value cache
/// DAO الكاش المستمر لقيم المؤشرات الطيفية
///
/// Uses raw SQL via Drift's `customSelect` / `customStatement` so the table
/// can be added without regenerating `database.g.dart`.  The actual table is
/// created by [MigrationV8].
///
/// This DAO is a pure **persistence** layer.  TTL policy (when entries expire)
/// lives in [AgronomicRepository], which passes the computed [expiresAt] to
/// [putEntries].  The DAO itself has no opinion on how long data should be kept.
library;

import 'package:drift/drift.dart';

/// A single cached spectral-index value row.
class NdviCacheEntry {
  final String fieldId;
  final String indexCode;

  /// ISO-8601 date string, or `null` for the live / most-recent value.
  final String? date;

  final double value;
  final DateTime fetchedAt;
  final DateTime expiresAt;

  const NdviCacheEntry({
    required this.fieldId,
    required this.indexCode,
    this.date,
    required this.value,
    required this.fetchedAt,
    required this.expiresAt,
  });

  bool get isExpired => DateTime.now().isAfter(expiresAt);
}

/// DAO that reads/writes the `ndvi_cache` table using raw SQL.
///
/// Inject via [agronomicRepositoryProvider] — do not use directly from the UI.
class NdviCacheDao {
  /// Accepts any [GeneratedDatabase] so it is testable with in-memory DBs.
  final GeneratedDatabase _db;

  const NdviCacheDao(this._db);

  // ── Date key ──────────────────────────────────────────────────────────────

  /// Sentinel `date_key` value for live / most-recent entries.
  ///
  /// Uppercase to make misuse (typo of a real date) harder; and to allow
  /// future migration to an enum-backed column without ambiguity.
  static const String liveKey = 'LIVE';

  /// Canonical `date_key` column value.
  ///
  /// Returns [liveKey] when [date] is `null` (live/most-recent entry).
  /// SQLite UNIQUE index cannot cover NULL values reliably, so we use a
  /// known sentinel instead.
  static String dateKey(DateTime? date) {
    if (date == null) return liveKey;
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-'
        '${date.day.toString().padLeft(2, '0')}';
  }

  // ── Read ──────────────────────────────────────────────────────────────────

  /// Returns all non-expired entries for the given [fieldId] and [date].
  ///
  /// [date] `null` → live cache entry.
  Future<List<NdviCacheEntry>> getEntries(
    String fieldId,
    DateTime? date,
  ) async {
    final key = dateKey(date);
    final rows = await _db.customSelect(
      'SELECT index_code, value, fetched_at, expires_at '
      'FROM ndvi_cache '
      'WHERE field_id = ? AND date_key = ? AND expires_at > ?',
      variables: [
        Variable.withString(fieldId),
        Variable.withString(key),
        Variable.withInt(DateTime.now().millisecondsSinceEpoch),
      ],
    ).get();

    return rows.map((row) {
      final fetchedMs = row.read<int>('fetched_at');
      final expiresMs = row.read<int>('expires_at');
      return NdviCacheEntry(
        fieldId: fieldId,
        indexCode: row.read<String>('index_code'),
        date: date == null ? null : key,
        value: row.read<double>('value'),
        fetchedAt: DateTime.fromMillisecondsSinceEpoch(fetchedMs),
        expiresAt: DateTime.fromMillisecondsSinceEpoch(expiresMs),
      );
    }).toList();
  }

  // ── Write ─────────────────────────────────────────────────────────────────

  /// Upserts a batch of [values] for [fieldId] / [date].
  ///
  /// [expiresAt] must be supplied by the caller (typically [AgronomicRepository]).
  /// This keeps TTL policy out of the DAO and in the business logic layer.
  ///
  /// Each call replaces any existing row for the same
  /// `(field_id, index_code, date_key)` triple.
  Future<void> putEntries(
    String fieldId,
    DateTime? date,
    Map<String, double> values,
    DateTime expiresAt,
  ) async {
    final key = dateKey(date);
    final now = DateTime.now();

    await _db.transaction(() async {
      for (final entry in values.entries) {
        await _db.customStatement(
          'INSERT OR REPLACE INTO ndvi_cache '
          '(field_id, index_code, date_key, value, fetched_at, expires_at) '
          'VALUES (?, ?, ?, ?, ?, ?)',
          [
            fieldId,
            entry.key,
            key,
            entry.value,
            now.millisecondsSinceEpoch,
            expiresAt.millisecondsSinceEpoch,
          ],
        );
      }
    });
  }

  // ── Delete ────────────────────────────────────────────────────────────────

  /// Deletes all cached rows for [fieldId] (both live and historical).
  ///
  /// Called by [AgronomicRepository.invalidate] when the field's data must
  /// be fully re-fetched (e.g. boundary change, API version bump).
  Future<void> deleteField(String fieldId) async {
    await _db.customStatement(
      'DELETE FROM ndvi_cache WHERE field_id = ?',
      [fieldId],
    );
  }

  // ── Cleanup ───────────────────────────────────────────────────────────────

  /// Deletes all rows whose TTL has elapsed.  Call periodically (e.g. on app
  /// start) to keep the table lean.
  Future<void> evictExpired() async {
    await _db.customStatement(
      'DELETE FROM ndvi_cache WHERE expires_at <= ?',
      [DateTime.now().millisecondsSinceEpoch],
    );
  }
}
