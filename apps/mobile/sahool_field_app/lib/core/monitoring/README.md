# Sentry Error Tracking & Performance Monitoring

This module provides comprehensive error tracking and performance monitoring for the SAHOOL Field App using Sentry.

## Setup

### 1. Install Dependencies

The `sentry_flutter` package is already added to `pubspec.yaml`:

```yaml
dependencies:
  sentry_flutter: ^8.11.0
```

Run to install:
```bash
flutter pub get
```

### 2. Configure Sentry DSN

#### Option A: Using .env file (Recommended for Development)

Create a `.env` file in the app root (copy from `.env.example`):

```bash
cp .env.example .env
```

Add your Sentry DSN:

```env
SENTRY_DSN=https://your-key@o123456.ingest.sentry.io/123456
ENABLE_CRASH_REPORTING=true
```

#### Option B: Using dart-define (Recommended for Production)

Build with Sentry DSN as compile-time constant:

```bash
# Development
flutter run --dart-define=SENTRY_DSN=https://your-key@o123456.ingest.sentry.io/123456

# Production build
flutter build apk \
  --dart-define=ENV=production \
  --dart-define=SENTRY_DSN=https://your-key@o123456.ingest.sentry.io/123456 \
  --dart-define=ENABLE_CRASH_REPORTING=true
```

### 3. Get Your Sentry DSN

1. Sign up at [sentry.io](https://sentry.io)
2. Create a new project (select "Flutter" as platform)
3. Copy the DSN from project settings
4. DSN format: `https://[key]@o[org-id].ingest.sentry.io/[project-id]`

## Features

### ✅ Automatic Error Capture
- Uncaught exceptions are automatically sent to Sentry
- Flutter framework errors are captured
- Native crashes (iOS/Android) are tracked

### ✅ Performance Monitoring
- Transaction tracking for operations
- Span tracking for granular performance data
- Network request monitoring
- Screen load time tracking

### ✅ Breadcrumb Tracking
- User navigation history
- User actions and interactions
- State changes and data operations
- Network requests and responses

### ✅ User Context
- User identification for error attribution
- Custom user properties
- Session tracking

### ✅ Privacy & Security
- PII (Personally Identifiable Information) filtering
- Sensitive data redaction
- Request header filtering

## Usage

### Basic Error Capture

```dart
try {
  await riskyOperation();
} catch (e, stackTrace) {
  SentryService.captureException(e, stackTrace: stackTrace);
}
```

### Breadcrumb Tracking

```dart
SentryService.addBreadcrumb(
  'User opened settings',
  category: 'navigation',
);

SentryService.addBreadcrumb(
  'Data sync completed',
  category: 'sync',
  data: {'records_synced': 150},
);
```

### User Context

```dart
// On login
await SentryService.setUser(
  userId,
  email: 'user@example.com',
  extras: {'role': 'farmer', 'tenant': 'sahool-demo'},
);

// On logout
await SentryService.clearUser();
```

### Performance Monitoring

```dart
final transaction = SentryService.startTransaction('sync_data', 'task');

try {
  await performSync();
  transaction.status = SpanStatus.ok();
} catch (e) {
  transaction.status = SpanStatus.internalError();
  rethrow;
} finally {
  await transaction.finish();
}
```

### Custom Context & Tags

```dart
// Set custom context
await SentryService.setContext('device', {
  'battery_level': '75%',
  'network': 'WiFi',
});

// Set tags for filtering
await SentryService.setTag('tenant', 'sahool-demo');
await SentryService.setTag('feature', 'offline_sync');
```

## Configuration

### Environment-Based Configuration

Sentry automatically configures based on the app environment:

```dart
// Development
- Traces Sample Rate: 100% (all transactions sent)
- Debug Mode: Enabled
- Auto-Session Tracking: Enabled

// Production
- Traces Sample Rate: 10% (10% of transactions sent)
- Debug Mode: Disabled
- Auto-Session Tracking: Enabled
```

### Feature Flags

Control Sentry via environment variables:

```env
# Enable/disable crash reporting
ENABLE_CRASH_REPORTING=true

# Environment (affects Sentry environment tagging)
ENV=production
```

### Enabling Sentry

Sentry is enabled when **both** conditions are met:
1. `ENABLE_CRASH_REPORTING=true` (or not in development)
2. `SENTRY_DSN` is provided

## Integration Points

### 1. Main App Initialization (`main.dart`)

```dart
// Sentry is initialized early in the app lifecycle
await SentryService.initialize();
```

### 2. Global Error Handler

```dart
runZonedGuarded(() async {
  // App code
}, (error, stackTrace) {
  // All uncaught errors are sent to Sentry
  SentryService.captureException(error, stackTrace: stackTrace);
});
```

### 3. Throughout the App

- Repositories: Track database operations
- API Services: Monitor network requests
- UI Widgets: Track user interactions
- Background Tasks: Monitor sync operations

## Best Practices

### DO ✅

- **Capture context**: Add breadcrumbs before errors occur
- **Set user context**: Identify users on login
- **Track performance**: Use transactions for important operations
- **Add tags**: Use tags for filtering in Sentry dashboard
- **Clear user data**: Clear user context on logout

### DON'T ❌

- **Don't send PII**: Avoid sending passwords, tokens, or sensitive data
- **Don't spam**: Don't capture expected/handled errors
- **Don't capture in dev**: Sentry auto-disables in development (unless explicitly enabled)
- **Don't forget context**: Errors without context are hard to debug

## Testing

### Test Sentry Integration

```dart
// Trigger a test error
SentryService.captureException(
  Exception('Test error'),
  stackTrace: StackTrace.current,
);

// Send a test message
SentryService.captureMessage(
  'Test message from SAHOOL Field App',
  level: SentryLevel.info,
);
```

### Verify in Sentry Dashboard

1. Go to your Sentry project dashboard
2. Check "Issues" tab for errors
3. Check "Performance" tab for transactions
4. Look for your test error/message

## Monitoring Dashboard

Access your Sentry dashboard to:

- **View errors**: See all captured exceptions with stack traces
- **Track performance**: Analyze operation performance and bottlenecks
- **Monitor releases**: Track errors by app version
- **Filter by tags**: Filter by tenant, feature, user, etc.
- **Set alerts**: Get notified of critical errors

## Troubleshooting

### Sentry Not Sending Errors

1. **Check DSN is configured**:
   ```dart
   print(EnvConfig.sentryDsn); // Should print your DSN
   print(EnvConfig.isSentryEnabled); // Should be true
   ```

2. **Check environment**:
   - In development, `ENABLE_CRASH_REPORTING` is false by default
   - Set `ENABLE_CRASH_REPORTING=true` in `.env` to test

3. **Check logs**:
   - Look for "✅ Sentry initialized" in console
   - Look for "⚠️ Sentry disabled" if not enabled

### Errors Not Appearing in Dashboard

1. **Wait a few seconds**: Sentry batches events
2. **Check internet connection**: Errors are queued offline
3. **Verify DSN**: Ensure DSN is correct
4. **Check project**: Ensure you're viewing the correct Sentry project

## Examples

See `sentry_usage_example.dart` for comprehensive examples including:

1. Basic error capture
2. Breadcrumb tracking
3. User context management
4. Performance monitoring
5. Custom context and tags
6. Repository integration
7. UI widget integration
8. Network request monitoring
9. Message capture

## Resources

- [Sentry Flutter Documentation](https://docs.sentry.io/platforms/flutter/)
- [Sentry Performance Monitoring](https://docs.sentry.io/platforms/flutter/performance/)
- [Sentry Best Practices](https://docs.sentry.io/platforms/flutter/best-practices/)
- [SAHOOL EnvConfig Documentation](../config/env_config.dart)

## License

Part of the SAHOOL Field App - Internal Use Only
