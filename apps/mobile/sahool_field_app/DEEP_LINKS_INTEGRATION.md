# Android App Links (Deep Links) Integration Guide

This document explains how to integrate and use Android App Links in the SAHOOL Field App.

## Overview

The app supports two types of deep links:

1. **HTTPS App Links** (Auto-verified): `https://sahool.app/field/{fieldId}`
2. **Custom Scheme**: `sahool://open/{path}`

## Supported Deep Link Patterns

| Pattern | Example | Description |
|---------|---------|-------------|
| `/field/{fieldId}` | `https://sahool.app/field/123` | Opens field details screen |
| `/field/{fieldId}/dashboard` | `https://sahool.app/field/123/dashboard` | Opens field dashboard |
| `/field/{fieldId}/ecological` | `https://sahool.app/field/123/ecological` | Opens field ecological records |
| `/crop/{cropId}` | `https://sahool.app/crop/456` | Opens crop details (TODO) |
| `/task/{taskId}` | `https://sahool.app/task/789` | Opens task details (TODO) |
| `sahool://open/{path}` | `sahool://open/field/123` | Custom scheme for any path |

## Integration Steps

### 1. Initialize Deep Links in Your App

Add deep link initialization to your app's startup sequence. Example in `lib/main.dart`:

```dart
import 'core/routes/app_router.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // ... other initialization code ...

  // Initialize deep link handling
  await AppRouter.initializeDeepLinks();

  runApp(const MyApp());
}
```

### 2. Update Your MaterialApp to Use GoRouter

If you're using the old `app.dart` with basic routing, you should migrate to use `AppRouter.router`:

```dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'core/routes/app_router.dart';

class SahoolFieldApp extends StatelessWidget {
  const SahoolFieldApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      routerConfig: AppRouter.router,
      title: 'سهول',
      // ... other configuration ...
    );
  }
}
```

### 3. Deploy Asset Links File

For HTTPS App Links to work with auto-verification, you must host the `assetlinks.json` file on your web server:

1. Get SHA-256 fingerprints for your signing keys:
   ```bash
   # Debug key
   keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android

   # Release key
   keytool -list -v -keystore /path/to/release.jks -alias your-alias
   ```

2. Update `android/app/assetlinks.json` with your fingerprints

3. Upload the file to:
   - `https://sahool.app/.well-known/assetlinks.json`
   - `https://www.sahool.app/.well-known/assetlinks.json`

4. Ensure the file is served with:
   - HTTPS (not HTTP)
   - Content-Type: `application/json`
   - No redirects

## Testing Deep Links

### Test with ADB (Android Debug Bridge)

```bash
# Test HTTPS deep link to field
adb shell am start -W -a android.intent.action.VIEW -d "https://sahool.app/field/123"

# Test HTTPS deep link to field dashboard
adb shell am start -W -a android.intent.action.VIEW -d "https://sahool.app/field/123/dashboard"

# Test custom scheme
adb shell am start -W -a android.intent.action.VIEW -d "sahool://open/field/123"

# Test crop deep link (will navigate to home if not implemented)
adb shell am start -W -a android.intent.action.VIEW -d "https://sahool.app/crop/456"
```

### Test in Development

Use the `DeepLinkTester` utility in your Flutter app:

```dart
import 'core/routing/deep_link_handler.dart';

// In debug mode
if (kDebugMode) {
  DeepLinkTester.testDeepLinks(AppRouter.deepLinkHandler!);
}

// Generate test links
final fieldLink = DeepLinkTester.generateFieldLink('123');
print(fieldLink); // https://sahool.app/field/123

final customLink = DeepLinkTester.generateFieldLink('123', useCustomScheme: true);
print(customLink); // sahool://open/field/123
```

### Verify Asset Links Setup

After deploying `assetlinks.json`, verify it's working:

```bash
# Check if file is accessible
curl https://sahool.app/.well-known/assetlinks.json

# Use Google's Digital Asset Links API
curl "https://digitalassetlinks.googleapis.com/v1/statements:list?source.web.site=https://sahool.app&relation=delegate_permission/common.handle_all_urls"
```

## Adding New Deep Link Routes

To add a new deep link pattern:

### 1. Update Deep Link Handler

Edit `lib/core/routing/deep_link_handler.dart` and add your pattern in the `_parseHttpsLink` method:

```dart
// Pattern: /your-route/{id}
if (pathSegments.length == 2 && pathSegments[0] == 'your-route') {
  final id = pathSegments[1];
  return '/your-route/$id';
}
```

### 2. Add Route to AppRouter

Edit `lib/core/routes/app_router.dart` and add the corresponding GoRoute:

```dart
GoRoute(
  path: '/your-route/:id',
  name: 'your-route',
  builder: (context, state) {
    final id = state.pathParameters['id']!;
    return YourRouteScreen(id: id);
  },
),
```

### 3. Test Your New Route

```bash
adb shell am start -W -a android.intent.action.VIEW -d "https://sahool.app/your-route/123"
```

## Files Modified

### Android Native
- `/android/app/src/main/AndroidManifest.xml` - Added intent filters for deep links
- `/android/app/src/main/kotlin/io/sahool/field/MainActivity.kt` - Added native deep link handling

### Flutter
- `/lib/core/routing/deep_link_handler.dart` - Deep link parsing and routing logic
- `/lib/core/routes/app_router.dart` - Integration with GoRouter

### Documentation
- `/android/app/assetlinks.json` - Asset links configuration (reference copy)
- `/android/app/ASSETLINKS_README.md` - Asset links setup guide
- `/DEEP_LINKS_INTEGRATION.md` - This integration guide

## Troubleshooting

### Deep links not working?

1. **Check AndroidManifest.xml** - Ensure intent filters are correctly configured
2. **Verify Package Name** - Must match in `build.gradle.kts` and `MainActivity.kt`
3. **Check Asset Links** - File must be accessible at `https://sahool.app/.well-known/assetlinks.json`
4. **SHA-256 Fingerprints** - Must match your app's signing key
5. **Test with ADB** - Use `adb shell am start` commands to test

### App opens but doesn't navigate to the right screen?

1. **Check Logs** - Look for deep link handler debug messages in logcat
2. **Verify Route Exists** - Ensure the route is defined in `app_router.dart`
3. **Test Pattern Matching** - Use `DeepLinkTester.testDeepLinks()` to debug

### Asset links verification failing?

1. **HTTPS Required** - File must be served over HTTPS, not HTTP
2. **No Redirects** - Direct access only, no 301/302 redirects
3. **Correct Content-Type** - Must be `application/json`
4. **Valid JSON** - Check JSON syntax with `curl` or online validator
5. **Both Domains** - Deploy to both `sahool.app` and `www.sahool.app`

## Production Checklist

Before releasing to production:

- [ ] Generate SHA-256 fingerprint for release signing key
- [ ] Update `assetlinks.json` with release key fingerprint
- [ ] Deploy `assetlinks.json` to production server
- [ ] Verify asset links with Digital Asset Links API
- [ ] Test deep links with production APK on physical device
- [ ] Test both HTTPS and custom scheme deep links
- [ ] Verify deep links work when app is closed
- [ ] Verify deep links work when app is in background
- [ ] Add analytics tracking for deep link usage (optional)
- [ ] Document all deep link patterns for marketing/support teams

## Reference Links

- [Android App Links Documentation](https://developer.android.com/training/app-links)
- [Digital Asset Links](https://developers.google.com/digital-asset-links)
- [GoRouter Documentation](https://pub.dev/packages/go_router)
- [Flutter Deep Linking Guide](https://docs.flutter.dev/ui/navigation/deep-linking)
