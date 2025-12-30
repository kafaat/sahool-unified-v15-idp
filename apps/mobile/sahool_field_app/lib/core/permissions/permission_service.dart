import 'package:flutter/material.dart';
// NOTE: Add 'permission_handler: ^11.3.1' to pubspec.yaml dependencies
// import 'package:permission_handler/permission_handler.dart';

/// SAHOOL Runtime Permission Service
/// خدمة صلاحيات النظام (Android/iOS)
///
/// Handles runtime permissions for Android 6.0+ and iOS
/// Features:
/// - Location permission management
/// - Camera permission management
/// - Storage permission management
/// - Notification permission management
/// - Permission rationale dialogs
/// - Settings navigation

// ═══════════════════════════════════════════════════════════════════════════
// Permission Status Models
// ═══════════════════════════════════════════════════════════════════════════

/// Permission request result
class PermissionResult {
  final bool isGranted;
  final bool isPermanentlyDenied;
  final String message;

  const PermissionResult({
    required this.isGranted,
    this.isPermanentlyDenied = false,
    this.message = '',
  });

  const PermissionResult.granted()
      : isGranted = true,
        isPermanentlyDenied = false,
        message = 'تم منح الصلاحية';

  const PermissionResult.denied({this.message = 'تم رفض الصلاحية'})
      : isGranted = false,
        isPermanentlyDenied = false;

  const PermissionResult.permanentlyDenied({this.message = 'تم رفض الصلاحية نهائياً'})
      : isGranted = false,
        isPermanentlyDenied = true;
}

/// Permission type enum
enum PermissionType {
  location('الموقع', 'Location', Icons.location_on),
  camera('الكاميرا', 'Camera', Icons.camera_alt),
  storage('التخزين', 'Storage', Icons.storage),
  photos('الصور', 'Photos', Icons.photo_library),
  notification('الإشعارات', 'Notifications', Icons.notifications);

  final String arabicName;
  final String englishName;
  final IconData icon;

  const PermissionType(this.arabicName, this.englishName, this.icon);
}

// ═══════════════════════════════════════════════════════════════════════════
// Permission Service
// ═══════════════════════════════════════════════════════════════════════════

/// Service for handling runtime permissions
///
/// IMPORTANT: This service requires the `permission_handler` package.
/// Add to pubspec.yaml:
/// ```yaml
/// dependencies:
///   permission_handler: ^11.3.1
/// ```
///
/// Also configure platform-specific permissions:
///
/// Android (android/app/src/main/AndroidManifest.xml):
/// ```xml
/// <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
/// <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
/// <uses-permission android:name="android.permission.CAMERA" />
/// <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
/// <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"
///                  android:maxSdkVersion="32" />
/// <uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
/// <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
/// ```
///
/// iOS (ios/Runner/Info.plist):
/// ```xml
/// <key>NSLocationWhenInUseUsageDescription</key>
/// <string>نحتاج إلى الموقع لتحديد مواقع الحقول</string>
/// <key>NSCameraUsageDescription</key>
/// <string>نحتاج إلى الكاميرا لالتقاط صور المحاصيل</string>
/// <key>NSPhotoLibraryUsageDescription</key>
/// <string>نحتاج إلى الوصول للصور لإرفاقها بالتقارير</string>
/// ```
class PermissionService {
  // Singleton pattern
  static final PermissionService _instance = PermissionService._internal();
  factory PermissionService() => _instance;
  PermissionService._internal();

  // ─────────────────────────────────────────────────────────────────────────
  // Location Permissions
  // ─────────────────────────────────────────────────────────────────────────

  /// Request location permission with rationale
  ///
  /// Returns true if permission is granted
  Future<bool> requestLocationPermission({BuildContext? context}) async {
    // TODO: Uncomment when permission_handler is added to pubspec.yaml
    /*
    final status = await Permission.location.status;

    if (status.isGranted) {
      return true;
    }

    // Show rationale if needed
    if (context != null && !status.isPermanentlyDenied) {
      final shouldRequest = await _showPermissionRationale(
        context: context,
        type: PermissionType.location,
        message: 'نحتاج إلى صلاحية الموقع لتحديد مواقع الحقول والمزارع على الخريطة.',
      );

      if (!shouldRequest) {
        return false;
      }
    }

    final result = await Permission.location.request();

    if (result.isPermanentlyDenied && context != null) {
      await _showPermanentlyDeniedDialog(
        context: context,
        type: PermissionType.location,
      );
      return false;
    }

    return result.isGranted;
    */

    // Placeholder until permission_handler is added
    debugPrint('⚠️ permission_handler package not installed. Add it to pubspec.yaml');
    return false;
  }

  /// Request precise location permission (Android 12+)
  Future<bool> requestPreciseLocationPermission({BuildContext? context}) async {
    // TODO: Uncomment when permission_handler is added
    /*
    final status = await Permission.locationWhenInUse.status;

    if (status.isGranted) {
      return true;
    }

    if (context != null && !status.isPermanentlyDenied) {
      final shouldRequest = await _showPermissionRationale(
        context: context,
        type: PermissionType.location,
        message: 'نحتاج إلى الموقع الدقيق لتحديد مواقع الحقول بدقة عالية.',
      );

      if (!shouldRequest) {
        return false;
      }
    }

    final result = await Permission.locationWhenInUse.request();

    if (result.isPermanentlyDenied && context != null) {
      await _showPermanentlyDeniedDialog(
        context: context,
        type: PermissionType.location,
      );
      return false;
    }

    return result.isGranted;
    */

    debugPrint('⚠️ permission_handler package not installed. Add it to pubspec.yaml');
    return false;
  }

  /// Check location permission status
  Future<PermissionStatus> checkLocationPermission() async {
    // TODO: Uncomment when permission_handler is added
    /*
    return await Permission.location.status;
    */

    // Placeholder
    return PermissionStatus.denied;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Camera Permissions
  // ─────────────────────────────────────────────────────────────────────────

  /// Request camera permission
  Future<bool> requestCameraPermission({BuildContext? context}) async {
    // TODO: Uncomment when permission_handler is added
    /*
    final status = await Permission.camera.status;

    if (status.isGranted) {
      return true;
    }

    if (context != null && !status.isPermanentlyDenied) {
      final shouldRequest = await _showPermissionRationale(
        context: context,
        type: PermissionType.camera,
        message: 'نحتاج إلى صلاحية الكاميرا لالتقاط صور المحاصيل والآفات والأمراض.',
      );

      if (!shouldRequest) {
        return false;
      }
    }

    final result = await Permission.camera.request();

    if (result.isPermanentlyDenied && context != null) {
      await _showPermanentlyDeniedDialog(
        context: context,
        type: PermissionType.camera,
      );
      return false;
    }

    return result.isGranted;
    */

    debugPrint('⚠️ permission_handler package not installed. Add it to pubspec.yaml');
    return false;
  }

  /// Check camera permission status
  Future<PermissionStatus> checkCameraPermission() async {
    // TODO: Uncomment when permission_handler is added
    /*
    return await Permission.camera.status;
    */

    // Placeholder
    return PermissionStatus.denied;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Storage/Photos Permissions
  // ─────────────────────────────────────────────────────────────────────────

  /// Request storage/photos permission
  ///
  /// For Android 13+ (API 33+), requests READ_MEDIA_IMAGES
  /// For Android 10-12 (API 29-32), requests READ_EXTERNAL_STORAGE
  /// For iOS, requests Photo Library access
  Future<bool> requestStoragePermission({BuildContext? context}) async {
    // TODO: Uncomment when permission_handler is added
    /*
    Permission permission;

    // Use photos permission for Android 13+ and iOS
    if (await _isAndroid13OrHigher()) {
      permission = Permission.photos;
    } else {
      permission = Permission.storage;
    }

    final status = await permission.status;

    if (status.isGranted || status.isLimited) {
      return true;
    }

    if (context != null && !status.isPermanentlyDenied) {
      final shouldRequest = await _showPermissionRationale(
        context: context,
        type: PermissionType.storage,
        message: 'نحتاج إلى صلاحية الوصول للصور لإرفاقها بالتقارير والمهام.',
      );

      if (!shouldRequest) {
        return false;
      }
    }

    final result = await permission.request();

    if (result.isPermanentlyDenied && context != null) {
      await _showPermanentlyDeniedDialog(
        context: context,
        type: PermissionType.storage,
      );
      return false;
    }

    return result.isGranted || result.isLimited;
    */

    debugPrint('⚠️ permission_handler package not installed. Add it to pubspec.yaml');
    return false;
  }

  /// Check storage permission status
  Future<PermissionStatus> checkStoragePermission() async {
    // TODO: Uncomment when permission_handler is added
    /*
    if (await _isAndroid13OrHigher()) {
      return await Permission.photos.status;
    } else {
      return await Permission.storage.status;
    }
    */

    // Placeholder
    return PermissionStatus.denied;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Notification Permissions
  // ─────────────────────────────────────────────────────────────────────────

  /// Request notification permission (Android 13+, iOS)
  Future<bool> requestNotificationPermission({BuildContext? context}) async {
    // TODO: Uncomment when permission_handler is added
    /*
    final status = await Permission.notification.status;

    if (status.isGranted) {
      return true;
    }

    if (context != null && !status.isPermanentlyDenied) {
      final shouldRequest = await _showPermissionRationale(
        context: context,
        type: PermissionType.notification,
        message: 'نحتاج إلى صلاحية الإشعارات لإرسال تنبيهات المهام والتحديثات المهمة.',
      );

      if (!shouldRequest) {
        return false;
      }
    }

    final result = await Permission.notification.request();

    if (result.isPermanentlyDenied && context != null) {
      await _showPermanentlyDeniedDialog(
        context: context,
        type: PermissionType.notification,
      );
      return false;
    }

    return result.isGranted;
    */

    debugPrint('⚠️ permission_handler package not installed. Add it to pubspec.yaml');
    return false;
  }

  /// Check notification permission status
  Future<PermissionStatus> checkNotificationPermission() async {
    // TODO: Uncomment when permission_handler is added
    /*
    return await Permission.notification.status;
    */

    // Placeholder
    return PermissionStatus.denied;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Generic Permission Methods
  // ─────────────────────────────────────────────────────────────────────────

  /// Check any permission status
  ///
  /// TODO: Uncomment when permission_handler is added
  /*
  Future<PermissionStatus> checkPermission(Permission permission) async {
    return await permission.status;
  }
  */

  /// Request any permission
  ///
  /// TODO: Uncomment when permission_handler is added
  /*
  Future<PermissionResult> requestPermission(
    Permission permission, {
    BuildContext? context,
    PermissionType? type,
    String? customMessage,
  }) async {
    final status = await permission.status;

    if (status.isGranted) {
      return const PermissionResult.granted();
    }

    if (context != null && type != null && !status.isPermanentlyDenied) {
      final shouldRequest = await _showPermissionRationale(
        context: context,
        type: type,
        message: customMessage,
      );

      if (!shouldRequest) {
        return const PermissionResult.denied(message: 'ألغى المستخدم طلب الصلاحية');
      }
    }

    final result = await permission.request();

    if (result.isPermanentlyDenied) {
      if (context != null && type != null) {
        await _showPermanentlyDeniedDialog(context: context, type: type);
      }
      return const PermissionResult.permanentlyDenied();
    }

    if (result.isGranted) {
      return const PermissionResult.granted();
    }

    return const PermissionResult.denied();
  }
  */

  /// Open app settings
  Future<bool> openSettings() async {
    // TODO: Uncomment when permission_handler is added
    /*
    return await openAppSettings();
    */

    debugPrint('⚠️ permission_handler package not installed. Add it to pubspec.yaml');
    return false;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Bulk Permission Requests
  // ─────────────────────────────────────────────────────────────────────────

  /// Request multiple permissions for field operations
  /// Requests: Location, Camera, Storage
  Future<Map<PermissionType, bool>> requestFieldOperationsPermissions({
    BuildContext? context,
  }) async {
    final results = <PermissionType, bool>{};

    results[PermissionType.location] =
        await requestLocationPermission(context: context);
    results[PermissionType.camera] =
        await requestCameraPermission(context: context);
    results[PermissionType.storage] =
        await requestStoragePermission(context: context);

    return results;
  }

  /// Request all app permissions
  Future<Map<PermissionType, bool>> requestAllPermissions({
    BuildContext? context,
  }) async {
    final results = <PermissionType, bool>{};

    results[PermissionType.location] =
        await requestLocationPermission(context: context);
    results[PermissionType.camera] =
        await requestCameraPermission(context: context);
    results[PermissionType.storage] =
        await requestStoragePermission(context: context);
    results[PermissionType.notification] =
        await requestNotificationPermission(context: context);

    return results;
  }

  /// Check all permissions status
  Future<Map<PermissionType, PermissionStatus>> checkAllPermissions() async {
    final results = <PermissionType, PermissionStatus>{};

    results[PermissionType.location] = await checkLocationPermission();
    results[PermissionType.camera] = await checkCameraPermission();
    results[PermissionType.storage] = await checkStoragePermission();
    results[PermissionType.notification] = await checkNotificationPermission();

    return results;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Helper Methods
  // ─────────────────────────────────────────────────────────────────────────

  /// Check if Android 13 or higher
  Future<bool> _isAndroid13OrHigher() async {
    // TODO: Implement proper platform check
    // For now, return false as placeholder
    return false;
  }

  /// Show permission rationale dialog
  Future<bool> _showPermissionRationale({
    required BuildContext context,
    required PermissionType type,
    String? message,
  }) async {
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        icon: Icon(type.icon, size: 48, color: Theme.of(context).primaryColor),
        title: Text('نحتاج إلى صلاحية ${type.arabicName}'),
        content: Text(
          message ?? 'هذه الصلاحية مطلوبة لتشغيل التطبيق بشكل صحيح.',
          textAlign: TextAlign.right,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('متابعة'),
          ),
        ],
      ),
    );

    return result ?? false;
  }

  /// Show permanently denied dialog
  Future<void> _showPermanentlyDeniedDialog({
    required BuildContext context,
    required PermissionType type,
  }) async {
    await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        icon: Icon(
          Icons.warning_rounded,
          size: 48,
          color: Theme.of(context).colorScheme.error,
        ),
        title: const Text('صلاحية مطلوبة'),
        content: Text(
          'تم رفض صلاحية ${type.arabicName} نهائياً. '
          'يرجى فتح الإعدادات والسماح بالصلاحية يدوياً.',
          textAlign: TextAlign.right,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.pop(context);
              openSettings();
            },
            child: const Text('فتح الإعدادات'),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Permission Status Extension
// ═══════════════════════════════════════════════════════════════════════════

/// Placeholder for PermissionStatus until permission_handler is added
enum PermissionStatus {
  denied,
  granted,
  restricted,
  limited,
  permanentlyDenied,
  provisional;

  bool get isGranted => this == PermissionStatus.granted;
  bool get isDenied => this == PermissionStatus.denied;
  bool get isPermanentlyDenied => this == PermissionStatus.permanentlyDenied;
  bool get isRestricted => this == PermissionStatus.restricted;
  bool get isLimited => this == PermissionStatus.limited;
  bool get isProvisional => this == PermissionStatus.provisional;
}
