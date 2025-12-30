# Deep Links Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Initialize Deep Links in main.dart

Add this to your `lib/main.dart` **before** running the app:

```dart
import 'core/routes/app_router.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // ... other initialization ...

  // Initialize deep links (ADD THIS)
  await AppRouter.initializeDeepLinks();

  runApp(
    ProviderScope(
      // ... your existing code ...
      child: const SahoolFieldApp(),
    ),
  );
}
```

### Step 2: Test Deep Links

Open terminal and run:

```bash
# Make sure your app is running on an emulator or device
flutter run

# In a new terminal, test a deep link
adb shell am start -W -a android.intent.action.VIEW -d "https://sahool.app/field/123"
```

The app should navigate to the field details screen for field ID 123.

## 📱 Supported Links

Try these test commands:

```bash
# Field details
adb shell am start -W -a android.intent.action.VIEW -d "https://sahool.app/field/123"

# Field dashboard
adb shell am start -W -a android.intent.action.VIEW -d "https://sahool.app/field/123/dashboard"

# Field ecological records
adb shell am start -W -a android.intent.action.VIEW -d "https://sahool.app/field/123/ecological"

# Custom scheme (sahool://)
adb shell am start -W -a android.intent.action.VIEW -d "sahool://open/field/123"
```

## 🔧 What Was Changed?

### Modified Files:
1. ✅ `android/app/src/main/AndroidManifest.xml` - Added deep link intent filters
2. ✅ `android/app/src/main/kotlin/io/sahool/field/MainActivity.kt` - Native deep link handling
3. ✅ `lib/core/routes/app_router.dart` - Deep link integration
4. ✅ `lib/core/routing/deep_link_handler.dart` - NEW: Deep link parser

### New Files:
1. 📄 `lib/core/routing/deep_link_handler.dart` - Deep link logic
2. 📄 `lib/core/routing/routing.dart` - Routing exports
3. 📄 `android/app/assetlinks.json` - Asset links config (reference)
4. 📄 `android/app/ASSETLINKS_README.md` - Setup guide
5. 📄 `DEEP_LINKS_INTEGRATION.md` - Full integration guide
6. 📄 `DEEP_LINKS_QUICK_START.md` - This file

## 🌐 Production Deployment (Required for HTTPS links)

For production, you need to:

1. **Generate your release key SHA-256 fingerprint:**
   ```bash
   keytool -list -v -keystore /path/to/release.jks -alias your-alias
   ```

2. **Update `android/app/assetlinks.json`** with your fingerprint

3. **Deploy to your web server:**
   ```
   https://sahool.app/.well-known/assetlinks.json
   ```

4. **Verify it's working:**
   ```bash
   curl https://sahool.app/.well-known/assetlinks.json
   ```

See `DEEP_LINKS_INTEGRATION.md` for full details.

## ❓ Common Issues

### "Deep link doesn't work"
- Make sure app is running: `flutter run`
- Check ADB is connected: `adb devices`
- Verify package name matches: `io.sahool.field`

### "App opens but doesn't navigate"
- Check Flutter logs for errors
- Verify route exists in `app_router.dart`
- Make sure deep links are initialized in `main.dart`

### "HTTPS links don't auto-open app"
- This requires production setup with `assetlinks.json` on your server
- For now, use custom scheme: `sahool://open/field/123`

## 📚 Next Steps

- Read `DEEP_LINKS_INTEGRATION.md` for complete documentation
- Add crop and task routes (currently TODO)
- Set up production asset links
- Add analytics tracking for deep link usage

## 🧪 Debug Mode Testing

In your Flutter code, you can test deep links programmatically:

```dart
import 'package:flutter/foundation.dart';
import 'core/routing/routing.dart';

// In debug builds
if (kDebugMode) {
  // Test all deep link patterns
  DeepLinkTester.testDeepLinks(AppRouter.deepLinkHandler!);

  // Generate test links
  final link = DeepLinkTester.generateFieldLink('123');
  print('Test link: $link');
}
```

---

**Need help?** Check the full guide in `DEEP_LINKS_INTEGRATION.md`
