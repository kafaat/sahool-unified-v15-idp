# Enhanced Connectivity Module

## Overview

The Enhanced Connectivity Module provides comprehensive network monitoring and offline support for the SAHOOL mobile app. It goes beyond simple WiFi/cellular detection to verify actual internet availability through HTTP ping requests.

## Features

- **Real Internet Availability**: Not just WiFi connection, but actual internet access verification
- **Multiple Connection States**: Online, Poor Connection, Reconnecting, Offline, Unknown
- **Periodic Connectivity Checks**: Automatic background monitoring at configurable intervals
- **Connection Quality Detection**: Identifies poor/slow connections based on response times
- **Automatic Reconnection**: Smart retry logic with consecutive failure tracking
- **Stream-Based Updates**: Real-time connectivity status via Riverpod providers

## Architecture

### 1. ConnectivityService (`connectivity_service.dart`)

Core service that monitors network connectivity and internet availability.

**Key Features:**
- Monitors `connectivity_plus` for network changes
- Performs HTTP pings to verify internet access
- Periodic connectivity checks (default: 30 seconds)
- Multiple ping URLs with fallback
- Connection quality detection based on response time
- Consecutive failure tracking

**Usage:**
```dart
final service = ConnectivityService(
  pingUrls: ['https://www.google.com', 'https://1.1.1.1'],
  checkInterval: Duration(seconds: 30),
  pingTimeout: Duration(seconds: 5),
);

// Listen to status changes
service.statusStream.listen((status) {
  print('Connectivity: ${status.displayMessage}');
});

// Manual check
final status = await service.checkNow();

// Attempt reconnection
final success = await service.tryReconnect();
```

### 2. ConnectivityProvider (`connectivity_provider.dart`)

Riverpod providers for state management.

**Providers:**
- `enhancedConnectivityServiceProvider` - Service instance
- `connectivityStatusStreamProvider` - Status stream
- `currentConnectivityStatusProvider` - Current status
- `enhancedConnectivityStateProvider` - Full state with metadata
- `isOnlineProvider`, `isOfflineProvider`, `isPoorConnectionProvider` - Convenience providers

**Usage:**
```dart
// Watch connectivity status
final connectivity = ref.watch(enhancedConnectivityStateProvider);

if (connectivity.isOnline) {
  // Online actions
}

// Check if online
final isOnline = ref.watch(isOnlineProvider);

// Manual actions
ref.read(enhancedConnectivityStateProvider.notifier).checkNow();
ref.read(enhancedConnectivityStateProvider.notifier).reconnect();
```

### 3. UI Widgets

#### OfflineBanner (`/shared/widgets/offline_banner.dart`)

Animated banner that slides in when offline.

**Features:**
- Smooth slide-in/out animations
- Different colors for different states
- Auto-retry button
- Pending sync count display
- Auto-dismiss when back online

**Usage:**
```dart
// In your app scaffold
Scaffold(
  body: Column(
    children: [
      OfflineBanner(),
      Expanded(child: yourContent),
    ],
  ),
)

// Custom configuration
OfflineBanner(
  height: 50,
  showRetryButton: true,
  customMessage: 'Custom offline message',
)

// Compact indicator
ConnectivityStatusIndicator(
  size: 24,
  showLabel: true,
)

// Full-screen overlay
OfflineOverlay(
  showOverlay: true,
  child: YourWidget(),
)
```

#### ConnectivityAwareButton (`/shared/widgets/connectivity_aware_button.dart`)

Button that disables when offline for online-only actions.

**Features:**
- Auto-disables when offline
- Tooltip explaining why disabled
- Supports poor connection handling
- Multiple button styles (elevated, text, outlined)
- Icon button and FAB variants

**Usage:**
```dart
// Elevated button (requires online)
ConnectivityAwareButton.elevated(
  onPressed: () => syncData(),
  requiresOnline: true,
  allowPoorConnection: false,
  child: Text('Sync Data'),
)

// Text button (works offline)
ConnectivityAwareButton.text(
  onPressed: () => viewOfflineData(),
  requiresOnline: false,
  child: Text('View Data'),
)

// With icon
ConnectivityAwareButton.elevated(
  onPressed: () => upload(),
  icon: Icon(Icons.cloud_upload),
  showConnectivityIndicator: true,
  child: Text('Upload'),
)

// Icon button variant
ConnectivityAwareIconButton(
  icon: Icon(Icons.refresh),
  onPressed: () => refresh(),
  requiresOnline: true,
  tooltip: 'Refresh data',
)

// FAB variant
ConnectivityAwareFAB(
  onPressed: () => newItem(),
  requiresOnline: true,
  child: Icon(Icons.add),
)

// Action button with status
ConnectivityActionButton(
  label: 'Submit',
  icon: Icons.send,
  onPressed: () => submit(),
  showStatus: true,
)
```

## Connection States

### ConnectivityStatus Enum

1. **unknown** - Initial state, checking connectivity
2. **online** - Fully online with good connection (response time < 3 seconds)
3. **poorConnection** - Connected but slow (response time > 3 seconds)
4. **reconnecting** - First failure after being online
5. **offline** - No internet connection (2+ consecutive failures)

## Integration Guide

### Step 1: Add to App Root

Wrap your app with the offline banner:

```dart
import 'package:sahool_field_app/shared/widgets/widgets.dart';

class MyApp extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp(
      home: Scaffold(
        body: Column(
          children: [
            OfflineBanner(),
            Expanded(
              child: YourHomeWidget(),
            ),
          ],
        ),
      ),
    );
  }
}
```

### Step 2: Use Connectivity-Aware Buttons

Replace buttons that require internet with connectivity-aware variants:

```dart
// Before
ElevatedButton(
  onPressed: () => uploadData(),
  child: Text('Upload'),
)

// After
ConnectivityAwareButton.elevated(
  onPressed: () => uploadData(),
  requiresOnline: true,
  child: Text('Upload'),
)
```

### Step 3: Listen to Connectivity Changes

```dart
class MyWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectivity = ref.watch(enhancedConnectivityStateProvider);

    // Auto-sync when coming back online
    ref.listen<EnhancedConnectivityState>(
      enhancedConnectivityStateProvider,
      (previous, next) {
        if (previous?.isOffline == true && next.isOnline) {
          // Trigger sync
          syncPendingData();
        }
      },
    );

    return YourWidget();
  }
}
```

### Step 4: Check Connectivity Before Actions

```dart
Future<void> performOnlineAction() async {
  final isOnline = ref.read(isOnlineProvider);

  if (!isOnline) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('No internet connection')),
    );
    return;
  }

  // Perform action
}
```

## Configuration

### Custom Ping URLs

```dart
// In your provider setup
final enhancedConnectivityServiceProvider = Provider<ConnectivityService>((ref) {
  final service = ConnectivityService(
    pingUrls: [
      'https://your-api.com/health',
      'https://www.google.com',
      'https://1.1.1.1',
    ],
    checkInterval: Duration(seconds: 45),
    pingTimeout: Duration(seconds: 10),
  );

  ref.onDispose(() => service.dispose());
  return service;
});
```

### Sync Integration

```dart
class SyncManager extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen for online status
    ref.listen<EnhancedConnectivityState>(
      enhancedConnectivityStateProvider,
      (previous, next) {
        if (next.isOnline && next.hasPendingSync) {
          _performSync(ref);
        }
      },
    );

    return YourWidget();
  }

  Future<void> _performSync(WidgetRef ref) async {
    final notifier = ref.read(enhancedConnectivityStateProvider.notifier);

    try {
      // Perform sync
      await yourSyncLogic();
      notifier.clearPendingSync();
    } catch (e) {
      // Handle error
    }
  }
}
```

## Best Practices

1. **Use connectivity-aware widgets** for all online-only actions
2. **Don't block the UI** - Allow offline work and queue for sync
3. **Show clear feedback** - Use the offline banner to inform users
4. **Handle poor connections** - Consider allowing degraded functionality
5. **Test offline scenarios** - Use airplane mode and network throttling
6. **Respect user bandwidth** - Don't ping too frequently
7. **Provide manual retry** - Always give users control to retry

## Testing

### Simulate Offline Mode

```dart
// In your test
testWidgets('Button disables when offline', (tester) async {
  // Mock the provider to return offline state
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        enhancedConnectivityStateProvider.overrideWith(
          (ref) => EnhancedConnectivityNotifier(mockOfflineService),
        ),
      ],
      child: YourApp(),
    ),
  );

  // Verify button is disabled
  expect(find.byType(ElevatedButton), findsDisabled);
});
```

## Troubleshooting

### Issue: Banner flickers when switching networks
**Solution:** Increase `checkInterval` to reduce frequency of checks

### Issue: False offline detection
**Solution:** Add more reliable ping URLs or increase `pingTimeout`

### Issue: Slow connection not detected
**Solution:** Adjust the 3-second threshold in `_checkInternetAvailability()`

### Issue: Battery drain
**Solution:** Increase `checkInterval` or disable periodic checks when app is backgrounded

## Migration from Old ConnectivityWidget

The new system can coexist with the old `connectivity_widget.dart`. To migrate:

1. Replace `connectivityProvider` with `enhancedConnectivityStateProvider`
2. Replace `ConnectivityBanner` with `OfflineBanner`
3. Use `ConnectivityAwareButton` instead of manual checks
4. Update state properties (e.g., `isOnline` vs `status`)

## Dependencies

- `connectivity_plus: ^6.1.1` - Network connectivity detection
- `http: ^1.2.2` - HTTP ping requests
- `flutter_riverpod: ^2.6.1` - State management

## Files Created

1. `/core/connectivity/connectivity_service.dart` - Core service
2. `/core/connectivity/connectivity_provider.dart` - Riverpod providers
3. `/core/connectivity/connectivity.dart` - Module exports
4. `/shared/widgets/offline_banner.dart` - UI banner widgets
5. `/shared/widgets/connectivity_aware_button.dart` - Smart button widgets
6. `/shared/widgets/widgets.dart` - Shared widgets exports

## Next Steps

1. Integrate `OfflineBanner` in your main app scaffold
2. Replace online-only buttons with `ConnectivityAwareButton`
3. Add connectivity listeners to trigger auto-sync
4. Configure custom ping URLs if needed
5. Test offline scenarios thoroughly
