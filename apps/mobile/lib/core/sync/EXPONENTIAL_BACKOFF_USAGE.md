# Exponential Backoff Implementation Guide

## Overview

The sync engine now includes comprehensive exponential backoff and circuit breaker functionality to prevent excessive API calls and handle failures gracefully.

## Key Features

### 1. Exponential Backoff Algorithm
- **Initial delay**: 1 second
- **Multiplier**: 2x per retry
- **Max delay**: 5 minutes (300 seconds)
- **Max retries**: 5 attempts
- **Jitter**: 0-25% random variation to prevent thundering herd

### 2. Circuit Breaker Pattern
- **Closed**: Normal operation (healthy)
- **Open**: Too many failures, requests fail fast
- **Half-Open**: Testing if service recovered

Circuit breaker thresholds:
- Failure threshold: 5 failures
- Open timeout: 2 minutes
- Half-open max attempts: 3

### 3. Per-Endpoint Tracking
Each API endpoint is tracked independently with its own:
- Retry counter
- Next retry time
- Circuit breaker state
- Failure history

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              SyncEngine                              │
│  ┌───────────────────────────────────────────────┐ │
│  │      EndpointRetryTracker                     │ │
│  │  ┌──────────────────────────────────────────┐ │ │
│  │  │   ExponentialBackoff Policy              │ │ │
│  │  │   - Initial: 1s                          │ │ │
│  │  │   - Multiplier: 2x                       │ │ │
│  │  │   - Max: 5 minutes                       │ │ │
│  │  └──────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────┐ │ │
│  │  │   Circuit Breakers (per endpoint)       │ │ │
│  │  │   - /tasks → Closed                      │ │ │
│  │  │   - /fields → Closed                     │ │ │
│  │  │   - /outbox → Open (backoff 32s)        │ │ │
│  │  └──────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## How It Works

### Retry Flow

1. **First Attempt** (retry 0)
   - Immediate attempt
   - On failure → retry_count = 1

2. **Retry 1**
   - Wait: 1 second (+ jitter)
   - Attempt again
   - On failure → retry_count = 2

3. **Retry 2**
   - Wait: 2 seconds (+ jitter)
   - Attempt again
   - On failure → retry_count = 3

4. **Retry 3**
   - Wait: 4 seconds (+ jitter)
   - Attempt again
   - On failure → retry_count = 4

5. **Retry 4**
   - Wait: 8 seconds (+ jitter)
   - Attempt again
   - On failure → retry_count = 5

6. **Retry 5**
   - Wait: 16 seconds (+ jitter)
   - Attempt again
   - On failure → Circuit opens

7. **Circuit Open**
   - All requests fail fast for 2 minutes
   - No API calls made
   - After 2 minutes → Half-Open

8. **Half-Open**
   - Allow 3 test requests
   - If successful → Circuit Closed
   - If failed → Circuit Open again

### Backoff Delays Table

| Retry # | Base Delay | With Max Jitter (25%) | Max Total Wait |
|---------|------------|----------------------|----------------|
| 0       | 0s         | 0s                   | 0s             |
| 1       | 1s         | 1.25s                | 1.25s          |
| 2       | 2s         | 2.5s                 | 3.75s          |
| 3       | 4s         | 5s                   | 8.75s          |
| 4       | 8s         | 10s                  | 18.75s         |
| 5       | 16s        | 20s                  | 38.75s         |
| 6+      | 300s       | 375s (capped at 5m)  | -              |

## Usage

### Monitoring Backoff Status (UI Integration)

```dart
// Listen to backoff status stream
syncEngine.backoffStatus.listen((status) {
  if (status.isBackoffActive) {
    // Show warning to user
    print('⚠️ ${status.statusMessage}');

    // Show time until next retry
    final nextRetry = status.nextRetryIn;
    if (nextRetry != null) {
      print('Next retry in: ${nextRetry.inSeconds}s');
    }

    // Show affected endpoints
    for (final endpoint in status.affectedEndpoints) {
      print('${endpoint.endpoint}: ${endpoint.statusDescription}');
    }
  } else {
    // All endpoints healthy
    print('✅ All endpoints healthy');
  }
});
```

### Getting Sync Statistics

```dart
final stats = syncEngine.getStatistics();

print('Consecutive failures: ${stats.consecutiveFailures}');
print('Last successful sync: ${stats.lastSuccessfulSync}');
print('Unhealthy endpoints: ${stats.unhealthyEndpoints}');
print('Is healthy: ${stats.isHealthy}');

if (stats.timeSinceLastSync != null) {
  print('Time since last sync: ${stats.timeSinceLastSync!.inMinutes} minutes');
}
```

### Getting Endpoint-Specific Status

```dart
// Get status for all endpoints
final statuses = syncEngine.getBackoffStatuses();

for (final entry in statuses.entries) {
  final endpoint = entry.key;
  final status = entry.value;

  print('Endpoint: $endpoint');
  print('  State: ${status.circuitState}');
  print('  Retry count: ${status.retryCount}');
  print('  Failure count: ${status.failureCount}');
  print('  Can retry: ${status.canRetry}');

  if (status.nextRetryTime != null) {
    print('  Next retry: ${status.nextRetryTime}');
  }

  if (status.timeUntilRetry != null) {
    print('  Time until retry: ${status.timeUntilRetry!.inSeconds}s');
  }
}
```

### Resetting Backoff (Admin/Debug)

```dart
// Reset specific endpoint
syncEngine.resetEndpointBackoff('/tasks');

// Reset all endpoints
syncEngine.resetAllBackoff();
```

## UI Integration Examples

### Show Backoff Warning Banner

```dart
StreamBuilder<BackoffStatus>(
  stream: syncEngine.backoffStatus,
  builder: (context, snapshot) {
    final status = snapshot.data;

    if (status == null || !status.isBackoffActive) {
      return SizedBox.shrink();
    }

    return Container(
      padding: EdgeInsets.all(8),
      color: Colors.orange.shade100,
      child: Row(
        children: [
          Icon(Icons.warning, color: Colors.orange),
          SizedBox(width: 8),
          Expanded(
            child: Text(
              status.statusMessage,
              style: TextStyle(fontSize: 12),
            ),
          ),
          if (status.nextRetryIn != null)
            Text(
              '${status.nextRetryIn!.inSeconds}s',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
        ],
      ),
    );
  },
)
```

### Show Sync Health Indicator

```dart
Widget buildSyncHealthIndicator(SyncStatistics stats) {
  final isHealthy = stats.isHealthy;
  final color = isHealthy ? Colors.green : Colors.red;
  final icon = isHealthy ? Icons.check_circle : Icons.error;

  return Row(
    children: [
      Icon(icon, color: color, size: 16),
      SizedBox(width: 4),
      Text(
        isHealthy ? 'Sync healthy' : 'Sync issues',
        style: TextStyle(color: color, fontSize: 12),
      ),
      if (stats.unhealthyEndpoints > 0)
        Text(
          ' (${stats.unhealthyEndpoints} endpoints)',
          style: TextStyle(fontSize: 10),
        ),
    ],
  );
}
```

## Benefits

### 1. Prevents Excessive API Calls
- Automatic backoff prevents hammering failing endpoints
- Rate limit protection built-in
- Jitter prevents synchronized retries

### 2. Resilient to Failures
- Circuit breaker prevents cascading failures
- Per-endpoint tracking isolates issues
- Automatic recovery detection

### 3. Better User Experience
- UI feedback via backoff status stream
- Predictable retry behavior
- Clear error states

### 4. Resource Efficiency
- Reduces battery drain from failed requests
- Minimizes network usage
- Prevents server overload

## Logs and Debugging

The implementation provides detailed logging:

```
📶 Network restored - triggering sync
⏸️ Skipping 42 - Retry in 4s
❌ Outbox item failed: 43 - Connection timeout
⏸️ Skipped 5 items due to backoff/circuit breaker
🔴 Circuit breaker [/tasks] OPEN - too many failures
🟡 Circuit breaker [/tasks] HALF-OPEN - testing recovery
🟢 Circuit breaker [/tasks] CLOSED - service recovered
```

## Configuration

To adjust backoff parameters, modify the `EndpointRetryTracker` initialization in `sync_engine.dart`:

```dart
final EndpointRetryTracker _retryTracker = EndpointRetryTracker(
  backoffPolicy: ExponentialBackoff(
    initialDelayMs: 1000,    // First retry after 1s
    multiplier: 2.0,         // Double each time
    maxDelayMs: 300000,      // Max 5 minutes
    maxRetries: 5,           // Try 5 times
    enableJitter: true,      // Add randomness
  ),
);
```

## Testing

To test the backoff behavior:

1. **Simulate failures**: Disconnect network or use invalid endpoint
2. **Monitor logs**: Watch retry delays increase exponentially
3. **Check circuit breaker**: Observe state transitions
4. **Verify recovery**: Reconnect and watch circuit close

## Migration Notes

The implementation is **backward compatible**:
- Existing retry count in database is preserved
- Outbox items continue to work as before
- Additional tracking is in-memory only

No database schema changes required for basic functionality.

## Future Enhancements

Potential improvements:
- [ ] Persist circuit breaker state to database
- [ ] Add metrics/analytics for retry patterns
- [ ] Configurable backoff policies per endpoint type
- [ ] Admin dashboard for circuit breaker management
- [ ] Automatic circuit breaker tuning based on patterns
