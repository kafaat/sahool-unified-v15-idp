# SAHOOL Runtime Permissions

Runtime permission handling for Android 6.0+ and iOS in the SAHOOL Field App.

## 📦 Installation

### 1. Add permission_handler Package

Add to `pubspec.yaml`:

```yaml
dependencies:
  permission_handler: ^11.3.1
```

Then run:

```bash
flutter pub get
```

### 2. Configure Android Permissions

Add to `android/app/src/main/AndroidManifest.xml`:

```xml
<manifest>
    <!-- Location -->
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />

    <!-- Camera -->
    <uses-permission android:name="android.permission.CAMERA" />

    <!-- Storage (Android 12 and below) -->
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"
                     android:maxSdkVersion="32" />

    <!-- Photos/Media (Android 13+) -->
    <uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />

    <!-- Notifications (Android 13+) -->
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <application>
        <!-- Your app config -->
    </application>
</manifest>
```

### 3. Configure iOS Permissions

Add to `ios/Runner/Info.plist`:

```xml
<dict>
    <!-- Location -->
    <key>NSLocationWhenInUseUsageDescription</key>
    <string>نحتاج إلى الموقع لتحديد مواقع الحقول والمزارع على الخريطة</string>

    <key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
    <string>نحتاج إلى الموقع لتتبع العمل الميداني</string>

    <!-- Camera -->
    <key>NSCameraUsageDescription</key>
    <string>نحتاج إلى الكاميرا لالتقاط صور المحاصيل والآفات</string>

    <!-- Photos -->
    <key>NSPhotoLibraryUsageDescription</key>
    <string>نحتاج إلى الوصول للصور لإرفاقها بالتقارير والمهام</string>

    <key>NSPhotoLibraryAddUsageDescription</key>
    <string>نحتاج لحفظ الصور الملتقطة في معرض الصور</string>
</dict>
```

### 4. Uncomment Code in Permission Service

After installing `permission_handler`, uncomment the TODO sections in:
- `lib/core/permissions/permission_service.dart`

## 🚀 Usage

### Basic Permission Request

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sahool_field_app/core/permissions/permission_provider.dart';

class MyWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ElevatedButton(
      onPressed: () async {
        // Request camera permission
        final controller = ref.read(permissionControllerProvider);
        final granted = await controller.requestCamera();

        if (granted) {
          // Permission granted, open camera
        }
      },
      child: Text('Take Photo'),
    );
  }
}
```

### Using Permission Gate

Show/hide widgets based on permission status:

```dart
import 'package:sahool_field_app/core/permissions/permission_widgets.dart';

RuntimePermissionGate(
  permission: PermissionType.camera,
  child: CameraButton(),
  // Optional: auto-request permission
  autoRequest: true,
  // Optional: callback when denied
  onPermissionDenied: () {
    print('Camera permission denied');
  },
)
```

### Request Multiple Permissions

```dart
final controller = ref.read(permissionControllerProvider);

// Request all field operations permissions
final results = await controller.requestFieldOperationsPermissions();

if (results[PermissionType.location] == true &&
    results[PermissionType.camera] == true &&
    results[PermissionType.storage] == true) {
  // All permissions granted
  Navigator.push(context, MaterialPageRoute(
    builder: (_) => FieldWorkScreen(),
  ));
}
```

### Check Permission Status

```dart
// Watch permission state
final state = ref.watch(permissionStateProvider);

// Check specific permission
final hasCamera = state.isGranted(PermissionType.camera);

// Check all field operations permissions
final hasAllPermissions = ref.watch(hasFieldOperationsPermissionsProvider);

// Get missing permissions
final missing = ref.watch(missingFieldOperationsPermissionsProvider);
```

### Permission Status Card

Display permission status with action button:

```dart
import 'package:sahool_field_app/core/permissions/permission_widgets.dart';

PermissionStatusCard(
  permission: PermissionType.location,
  description: 'نحتاج إلى الموقع لتحديد مواقع الحقول',
)
```

### Permissions Overview Screen

Show all permissions with status:

```dart
import 'package:sahool_field_app/core/permissions/permission_widgets.dart';

PermissionsOverview(
  showOnlyRequired: true, // Show only required permissions
)
```

### Field Operations Permission Dialog

Show dialog requesting all field operations permissions:

```dart
final allGranted = await FieldOperationsPermissionDialog.show(context);

if (allGranted) {
  // Proceed with field operations
}
```

### Full Permission Screen (Onboarding)

Use as a permission request screen during onboarding:

```dart
PermissionRequiredScreen(
  requiredPermissions: [
    PermissionType.location,
    PermissionType.camera,
    PermissionType.storage,
  ],
  onAllGranted: () {
    // Navigate to main app
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => MainApp()),
    );
  },
)
```

## 🎯 Permission Types

Available permission types:

- `PermissionType.location` - GPS location access
- `PermissionType.camera` - Camera access
- `PermissionType.storage` - File storage access (Android < 13)
- `PermissionType.photos` - Photo library access (Android 13+, iOS)
- `PermissionType.notification` - Push notifications (Android 13+)

## 🔄 State Management

### Providers

- `permissionServiceProvider` - Permission service singleton
- `permissionStateProvider` - Permission state notifier
- `permissionControllerProvider` - Permission request controller
- `hasLocationPermissionProvider` - Location permission status
- `hasCameraPermissionProvider` - Camera permission status
- `hasStoragePermissionProvider` - Storage permission status
- `hasNotificationPermissionProvider` - Notification permission status
- `hasFieldOperationsPermissionsProvider` - All field ops permissions
- `missingFieldOperationsPermissionsProvider` - Missing permissions list

### WidgetRef Extension

Quick access via extension methods:

```dart
class MyWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Check permission
    if (ref.hasPermission(PermissionType.camera)) {
      // Has camera permission
    }

    // Check all field operations permissions
    if (ref.hasFieldOperationsPermissions) {
      // Has all required permissions
    }

    // Request permission
    await ref.permissions.requestCamera();
  }
}
```

## 📱 Platform-Specific Notes

### Android

- **API 23-28**: REQUEST_STORAGE permission
- **API 29-32**: READ_EXTERNAL_STORAGE permission
- **API 33+**: READ_MEDIA_IMAGES permission
- **API 33+**: POST_NOTIFICATIONS permission required

### iOS

- Always requires usage descriptions in Info.plist
- Limited photo access available (user can select specific photos)
- Background location requires additional configuration

## 🔐 Best Practices

1. **Request at the Right Time**: Request permissions when needed, not on app startup
2. **Provide Context**: Use rationale dialogs to explain why permissions are needed
3. **Handle Denials**: Gracefully handle permanently denied permissions
4. **Check Before Use**: Always check permission status before using protected features
5. **Update State**: Refresh permission state after requests

## 🐛 Troubleshooting

### Permission Always Denied

1. Check manifest/Info.plist configuration
2. Verify permission_handler package is installed
3. Check if permission was permanently denied (open settings)
4. Uninstall and reinstall app to reset permissions

### Build Errors

1. Ensure permission_handler is added to pubspec.yaml
2. Run `flutter clean && flutter pub get`
3. Rebuild the app

## 📚 Examples

See usage examples in:
- Field operations screens
- Camera/photo capture flows
- Location tracking features
- Settings screen

## 🔗 References

- [permission_handler package](https://pub.dev/packages/permission_handler)
- [Android Permissions](https://developer.android.com/guide/topics/permissions/overview)
- [iOS Permissions](https://developer.apple.com/documentation/uikit/protecting_the_user_s_privacy)
