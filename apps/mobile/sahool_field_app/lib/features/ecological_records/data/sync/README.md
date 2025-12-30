# Ecological Records Sync Handler

## Overview

The `EcologicalSyncHandler` provides offline-first synchronization support for all ecological agriculture records in the Sahool Field mobile app. It follows the Outbox pattern to ensure reliable data sync between the mobile device and the server.

## Supported Record Types

The handler manages sync for the following ecological record types:

1. **Biodiversity Records** (`biodiversity_record`)
   - Species counts and monitoring
   - Insect surveys
   - Pollinator tracking
   - Habitat assessments

2. **Soil Health Records** (`soil_health_record`)
   - Soil testing and analysis
   - Nutrient levels
   - pH measurements
   - Organic matter content

3. **Water Conservation Records** (`water_conservation_record`)
   - Water usage tracking
   - Irrigation efficiency
   - Conservation practices
   - Source monitoring

4. **Farm Practice Records** (`farm_practice_record`)
   - Ecological farming practices
   - Implementation tracking
   - Effectiveness ratings
   - Benefits and challenges

## Architecture

### Offline-First Pattern

```
User Action → Local Database → Outbox Queue → Sync Engine → Server
                     ↓
                UI Updates
              (Immediate)
```

### Sync Flow

1. **Local Save**: Records are saved to the local database immediately
2. **Queue**: Added to the outbox table for later sync
3. **Background Sync**: Periodic sync process uploads queued records
4. **Conflict Resolution**: Server-wins strategy for conflicts
5. **Pull Updates**: Periodic pull of server data to local database

## Integration

The handler is automatically integrated into the main `SyncEngine`:

```dart
// In SyncEngine constructor
_ecologicalHandler = EcologicalSyncHandler(
  db: database,
  apiClient: _apiClient,
);

// In _processOutboxItem
if (_ecologicalHandler.handlers.containsKey(item.entityType)) {
  final handler = _ecologicalHandler.handlers[item.entityType]!;
  final success = await handler(item);
  return success ? _ItemResult.success : _ItemResult.failed;
}
```

## Usage

### 1. Saving Records (Repository Pattern)

Records are automatically queued for sync when saved through the repository:

```dart
// Example from EcologicalRepository
await _db.upsertBiodiversityRecord(record);
await _db.queueOutboxItem(
  tenantId: record.tenantId,
  entityType: 'biodiversity_record',
  entityId: record.id,
  apiEndpoint: '/api/v1/ecological/biodiversity',
  method: 'POST',
  payload: jsonEncode(record.toJson()),
);
```

### 2. Automatic Sync

The sync engine automatically processes queued records:

```dart
// Periodic sync (every 5 minutes by default)
syncEngine.startPeriodic();

// Manual sync
final result = await syncEngine.runOnce();
print('Synced: ${result.uploaded} records');
```

### 3. Batch Sync

For bulk operations, use the handler directly:

```dart
final result = await ecologicalHandler.syncAllPending(batchSize: 50);
print(result.statusMessageAr); // "تمت مزامنة 10 سجل بنجاح"
```

## API Endpoints

The handler expects the following API endpoints:

- `POST /api/v1/ecological/biodiversity` - Create/update biodiversity records
- `POST /api/v1/ecological/soil-health` - Create/update soil health records
- `POST /api/v1/ecological/water-conservation` - Create/update water records
- `POST /api/v1/ecological/practices` - Create/update practice records

### Expected Response Format

**Success Response (200/201):**
```json
{
  "id": "record-uuid",
  "status": "success",
  "message": "Record created successfully"
}
```

**Conflict Response (409):**
```json
{
  "error": "Conflict",
  "message": "Record was modified on server",
  "serverData": {
    // Latest server version of the record
  }
}
```

## Conflict Resolution

The handler uses a **server-wins** strategy for conflicts:

1. Detect conflict (HTTP 409)
2. Apply server version to local database
3. Create sync event for user notification
4. Mark outbox item as processed

```dart
// Conflict handling in sync handler
if (statusCode == 409) {
  await _handleConflict(item, e.response?.data, recordType);
  return true; // Resolved
}
```

## Database Methods

The following database methods are required and have been added to `AppDatabase`:

### Mark as Synced
- `markBiodiversitySynced(String recordId)`
- `markSoilHealthSynced(String recordId)`
- `markWaterConservationSynced(String recordId)`
- `markPracticeRecordSynced(String recordId)`

### Upsert from Server
- `upsertBiodiversityRecordsFromServer(List<Map<String, dynamic>> items)`
- `upsertSoilHealthRecordsFromServer(List<Map<String, dynamic>> items)`
- `upsertWaterConservationRecordsFromServer(List<Map<String, dynamic>> items)`
- `upsertPracticeRecordsFromServer(List<Map<String, dynamic>> items)`

## Error Handling

The handler includes comprehensive error handling:

```dart
try {
  final response = await _apiClient.post(endpoint, data: payload);
  if (_isSuccessResponse(response)) {
    await _db.markBiodiversitySynced(recordId);
    return true;
  }
  return false;
} on DioException catch (e) {
  // Handle HTTP errors
  if (e.response?.statusCode == 409) {
    // Conflict resolution
  } else if (e.response?.statusCode >= 500) {
    // Server error - will retry
  }
  return false;
} catch (e) {
  // Unknown errors
  await _logError('Unexpected error: $e', item);
  return false;
}
```

## Monitoring & Logging

All sync operations are logged to the `sync_logs` table:

```dart
await _db.logSync(
  type: 'ecological_sync',
  status: 'success',
  message: 'Biodiversity record synced: record-id',
);
```

Conflicts create sync events for user notification:

```dart
await _db.addSyncEvent(
  tenantId: tenantId,
  type: 'CONFLICT',
  message: 'تم تطبيق نسخة السيرفر بسبب تعارض في سجل التنوع البيولوجي',
  entityType: 'biodiversity_record',
  entityId: recordId,
);
```

## Testing

### Unit Tests

Test individual sync handlers:

```dart
test('should sync biodiversity record successfully', () async {
  final handler = EcologicalSyncHandler(db: mockDb, apiClient: mockApi);
  final item = OutboxData(/* ... */);

  final result = await handler.handlers['biodiversity_record']!(item);

  expect(result, true);
  verify(mockDb.markBiodiversitySynced(any)).called(1);
});
```

### Integration Tests

Test end-to-end sync flow:

```dart
test('should sync all ecological records', () async {
  final result = await syncEngine.runOnce();

  expect(result.success, true);
  expect(result.uploaded, greaterThan(0));
});
```

## Performance Considerations

1. **Batch Size**: Default is 50 records per sync cycle
2. **Retry Logic**: Failed items are retried with exponential backoff
3. **Network Detection**: Sync only runs when online
4. **Priority Queue**: Critical operations processed first

## Localization

The handler provides Arabic translations for all user-facing messages:

```dart
final result = await handler.syncAllPending();
print(result.statusMessageAr); // "تمت مزامنة 10 سجل بنجاح"
print(result.statusMessageEn); // "Successfully synced 10 records"
```

## Future Enhancements

- [ ] Client-wins conflict resolution option
- [ ] Differential sync (only changed fields)
- [ ] Compression for large payloads
- [ ] Offline queue prioritization UI
- [ ] Sync progress indicators
- [ ] Batch delete support

## Related Files

- Handler: `ecological_sync_handler.dart`
- Database: `../../../core/storage/database.dart`
- Tables: `../database/ecological_tables.dart`
- DAO: `../database/ecological_dao.dart`
- Repository: `../repositories/ecological_repository.dart`
- Sync Engine: `../../../core/sync/sync_engine.dart`

## Support

For issues or questions about the ecological sync handler, please refer to:
- Project documentation: `/docs/mobile/sync-architecture.md`
- Integration plan: `/docs/integration/ecological-agriculture-v2.md`
