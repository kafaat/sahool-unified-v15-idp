# ADR-003: Drift for Local Database

## Status

Accepted

## Context

SAHOOL's offline-first architecture requires a robust local database for:

1. **Structured data**: Fields, crops, tasks, equipment
2. **Complex queries**: Joins, aggregations, filters
3. **Large datasets**: 500+ fields per farmer possible
4. **Migrations**: Schema evolution over app updates
5. **Type safety**: Compile-time query validation

We evaluated several Flutter local database solutions.

## Decision

We chose **Drift (formerly Moor)** as our local database solution.

### Key Reasons

1. **Type-safe SQL**: Queries validated at compile time
2. **Full SQL power**: Complex queries, joins, transactions
3. **Code generation**: Tables and DAOs generated from Dart
4. **Migrations**: Built-in schema migration system
5. **Reactive queries**: Stream-based query results
6. **SQLite foundation**: Proven, performant database engine

### Implementation Pattern

```dart
// Table definition
class Fields extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get name => text().withLength(min: 1, max: 100)();
  RealColumn get areaHectares => real()();
  TextColumn get geometry => text()(); // GeoJSON
  IntColumn get cropId => integer().nullable().references(Crops, #id)();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get syncedAt => dateTime().nullable()();
}

// DAO with queries
@DriftAccessor(tables: [Fields, Crops])
class FieldDao extends DatabaseAccessor<AppDatabase> with _$FieldDaoMixin {
  FieldDao(AppDatabase db) : super(db);

  // Reactive query
  Stream<List<FieldWithCrop>> watchAllWithCrop() {
    return (select(fields)
      ..orderBy([(t) => OrderingTerm.desc(t.createdAt)]))
      .join([leftOuterJoin(crops, crops.id.equalsExp(fields.cropId))])
      .watch()
      .map((rows) => rows.map((row) => FieldWithCrop(
        field: row.readTable(fields),
        crop: row.readTableOrNull(crops),
      )).toList());
  }

  // Complex query
  Future<List<Field>> getFieldsNeedingSync() {
    return (select(fields)
      ..where((t) => t.syncedAt.isNull() | t.syncedAt.isSmallerThan(t.updatedAt)))
      .get();
  }
}
```

## Consequences

### Positive

- **SQL expertise reusable**: Team knows SQL
- **Complex queries**: Full SQL capabilities
- **Performance**: SQLite is highly optimized
- **Debugging**: Can inspect .db file directly
- **Migrations**: Structured schema evolution
- **Stability**: Drift is mature and well-maintained

### Negative

- **Code generation**: Adds build step complexity
- **Build time**: Large schemas slow down builds
- **Learning curve**: Need to understand Drift patterns
- **Verbose**: More code than NoSQL alternatives

### Neutral

- Requires understanding of SQL
- Database file management needed

## Alternatives Considered

### Alternative 1: Isar

**Considered because:**
- NoSQL (simpler for some use cases)
- Very fast performance
- No code generation needed

**Rejected because:**
- Less mature than Drift
- Complex queries harder
- Schema migrations less robust
- Team expertise in SQL

### Alternative 2: Hive

**Rejected because:**
- No relational capabilities
- Limited query options
- Not suitable for complex data models
- No migrations system

### Alternative 3: sqflite (raw)

**Rejected because:**
- No type safety
- Manual query strings
- No migration framework
- Error-prone

## Migration Strategy

```dart
// Migration example
MigrationStrategy get migration => MigrationStrategy(
  onCreate: (Migrator m) => m.createAll(),
  onUpgrade: (Migrator m, int from, int to) async {
    if (from < 2) {
      await m.addColumn(fields, fields.syncedAt);
    }
    if (from < 3) {
      await m.createTable(equipment);
    }
  },
);
```

## References

- [Drift Documentation](https://drift.simonbinder.eu/)
- [SQLite Documentation](https://sqlite.org/docs.html)
- [drift_dev package](https://pub.dev/packages/drift_dev)
