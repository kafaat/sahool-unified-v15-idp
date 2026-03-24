/// SAHOOL App Update Checker Service
/// خدمة التحقق من تحديثات التطبيق
///
/// Features:
/// - Check for updates on app start
/// - Check periodically (every 24 hours)
/// - Force update for major versions
/// - Optional update for minor versions
/// - Store "remind me later" preference
/// - Deep link to app store
library;

import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';

import '../config/api_config.dart';
import '../utils/app_logger.dart';
import 'version_comparator.dart';

/// Storage keys for update preferences
/// مفاتيح تخزين تفضيلات التحديث
class UpdateStorageKeys {
  static const String lastCheckTime = 'sahool_update_last_check';
  static const String remindLaterTime = 'sahool_update_remind_later';
  static const String skippedVersion = 'sahool_update_skipped_version';
  static const String cachedUpdateInfo = 'sahool_update_cached_info';
}

/// App store URLs
/// روابط متاجر التطبيقات
class AppStoreUrls {
  /// iOS App Store URL
  static const String iosAppStore =
      'https://apps.apple.com/app/sahool/id1234567890';

  /// Android Play Store URL
  static const String androidPlayStore =
      'https://play.google.com/store/apps/details?id=com.kafaat.sahool';

  /// Huawei AppGallery URL (for devices without Google Play)
  static const String huaweiAppGallery =
      'https://appgallery.huawei.com/app/C123456789';
}

/// Update information from the API
/// معلومات التحديث من واجهة برمجة التطبيقات
class UpdateInfo {
  /// Latest available version
  /// أحدث إصدار متاح
  final String latestVersion;

  /// Minimum required version (for force updates)
  /// الحد الأدنى للإصدار المطلوب (للتحديثات الإجبارية)
  final String minimumVersion;

  /// Release notes in English
  /// ملاحظات الإصدار بالإنجليزية
  final String releaseNotesEn;

  /// Release notes in Arabic
  /// ملاحظات الإصدار بالعربية
  final String releaseNotesAr;

  /// Release date
  /// تاريخ الإصدار
  final DateTime? releaseDate;

  /// Whether the update is critical (security fix, etc.)
  /// ما إذا كان التحديث حرجًا (إصلاح أمني، إلخ.)
  final bool isCritical;

  /// Custom app store URL (if different from defaults)
  /// رابط متجر مخصص (إذا كان مختلفًا عن الافتراضي)
  final String? customStoreUrl;

  /// List of new features
  /// قائمة الميزات الجديدة
  final List<String> newFeaturesEn;
  final List<String> newFeaturesAr;

  const UpdateInfo({
    required this.latestVersion,
    required this.minimumVersion,
    this.releaseNotesEn = '',
    this.releaseNotesAr = '',
    this.releaseDate,
    this.isCritical = false,
    this.customStoreUrl,
    this.newFeaturesEn = const [],
    this.newFeaturesAr = const [],
  });

  /// Parse from API response
  /// تحليل من استجابة واجهة برمجة التطبيقات
  factory UpdateInfo.fromJson(Map<String, dynamic> json) {
    return UpdateInfo(
      latestVersion: json['latest_version'] as String? ??
          json['latestVersion'] as String? ??
          '0.0.0',
      minimumVersion: json['minimum_version'] as String? ??
          json['minimumVersion'] as String? ??
          '0.0.0',
      releaseNotesEn: json['release_notes_en'] as String? ??
          json['releaseNotesEn'] as String? ??
          json['release_notes'] as String? ??
          '',
      releaseNotesAr: json['release_notes_ar'] as String? ??
          json['releaseNotesAr'] as String? ??
          '',
      releaseDate: json['release_date'] != null
          ? DateTime.tryParse(json['release_date'] as String)
          : null,
      isCritical: json['is_critical'] as bool? ??
          json['isCritical'] as bool? ??
          false,
      customStoreUrl:
          json['store_url'] as String? ?? json['storeUrl'] as String?,
      newFeaturesEn: (json['new_features_en'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          (json['newFeaturesEn'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      newFeaturesAr: (json['new_features_ar'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          (json['newFeaturesAr'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
    );
  }

  /// Convert to JSON for caching
  /// تحويل إلى JSON للتخزين المؤقت
  Map<String, dynamic> toJson() => {
        'latest_version': latestVersion,
        'minimum_version': minimumVersion,
        'release_notes_en': releaseNotesEn,
        'release_notes_ar': releaseNotesAr,
        'release_date': releaseDate?.toIso8601String(),
        'is_critical': isCritical,
        'store_url': customStoreUrl,
        'new_features_en': newFeaturesEn,
        'new_features_ar': newFeaturesAr,
      };
}

/// Result of update check
/// نتيجة التحقق من التحديث
class UpdateCheckResult {
  /// Whether an update is available
  /// ما إذا كان التحديث متاحًا
  final bool updateAvailable;

  /// Whether the update is required (force update)
  /// ما إذا كان التحديث مطلوبًا (تحديث إجباري)
  final bool forceUpdate;

  /// Type of update
  /// نوع التحديث
  final UpdateType updateType;

  /// Current app version
  /// الإصدار الحالي للتطبيق
  final String currentVersion;

  /// Update information from API
  /// معلومات التحديث من واجهة برمجة التطبيقات
  final UpdateInfo? updateInfo;

  /// Error message if check failed
  /// رسالة الخطأ إذا فشل التحقق
  final String? error;

  /// Whether the user has chosen to skip this version
  /// ما إذا كان المستخدم قد اختار تخطي هذا الإصدار
  final bool skipped;

  /// Whether the user has chosen to remind later
  /// ما إذا كان المستخدم قد اختار التذكير لاحقًا
  final bool remindLater;

  const UpdateCheckResult({
    required this.updateAvailable,
    required this.forceUpdate,
    required this.updateType,
    required this.currentVersion,
    this.updateInfo,
    this.error,
    this.skipped = false,
    this.remindLater = false,
  });

  /// Create a result for no update available
  factory UpdateCheckResult.noUpdate(String currentVersion) {
    return UpdateCheckResult(
      updateAvailable: false,
      forceUpdate: false,
      updateType: UpdateType.none,
      currentVersion: currentVersion,
    );
  }

  /// Create a result for an error
  factory UpdateCheckResult.error(String currentVersion, String error) {
    return UpdateCheckResult(
      updateAvailable: false,
      forceUpdate: false,
      updateType: UpdateType.none,
      currentVersion: currentVersion,
      error: error,
    );
  }
}

/// State for update checker
/// حالة مدقق التحديثات
class UpdateCheckerState {
  final bool isChecking;
  final UpdateCheckResult? lastResult;
  final DateTime? lastCheckTime;

  const UpdateCheckerState({
    this.isChecking = false,
    this.lastResult,
    this.lastCheckTime,
  });

  UpdateCheckerState copyWith({
    bool? isChecking,
    UpdateCheckResult? lastResult,
    DateTime? lastCheckTime,
  }) {
    return UpdateCheckerState(
      isChecking: isChecking ?? this.isChecking,
      lastResult: lastResult ?? this.lastResult,
      lastCheckTime: lastCheckTime ?? this.lastCheckTime,
    );
  }
}

/// Update checker service with Riverpod state management
/// خدمة التحقق من التحديثات مع إدارة الحالة بـ Riverpod
class UpdateCheckerNotifier extends StateNotifier<UpdateCheckerState> {
  final Dio _dio;
  Timer? _periodicCheckTimer;

  /// Check interval in hours (default: 24 hours)
  /// فترة التحقق بالساعات (افتراضي: 24 ساعة)
  static const int checkIntervalHours = 24;

  /// Remind later duration in hours (default: 24 hours)
  /// مدة التذكير لاحقًا بالساعات (افتراضي: 24 ساعة)
  static const int remindLaterHours = 24;

  UpdateCheckerNotifier({Dio? dio})
      : _dio = dio ?? Dio(),
        super(const UpdateCheckerState());

  /// Initialize and start periodic checks
  /// التهيئة وبدء التحقق الدوري
  Future<void> initialize() async {
    // Check if we need to check for updates
    final shouldCheck = await _shouldCheckForUpdates();
    if (shouldCheck) {
      await checkForUpdates();
    } else {
      // Load cached result
      await _loadCachedResult();
    }

    // Start periodic timer
    _startPeriodicCheck();
  }

  /// Check if we should check for updates now
  /// التحقق مما إذا كان يجب التحقق من التحديثات الآن
  Future<bool> _shouldCheckForUpdates() async {
    final prefs = await SharedPreferences.getInstance();

    // Check remind later time
    final remindLaterTimeMs = prefs.getInt(UpdateStorageKeys.remindLaterTime);
    if (remindLaterTimeMs != null) {
      final remindLaterTime =
          DateTime.fromMillisecondsSinceEpoch(remindLaterTimeMs);
      if (DateTime.now().isBefore(remindLaterTime)) {
        return false;
      }
    }

    // Check last check time
    final lastCheckTimeMs = prefs.getInt(UpdateStorageKeys.lastCheckTime);
    if (lastCheckTimeMs == null) {
      return true;
    }

    final lastCheckTime =
        DateTime.fromMillisecondsSinceEpoch(lastCheckTimeMs);
    final hoursSinceLastCheck =
        DateTime.now().difference(lastCheckTime).inHours;

    return hoursSinceLastCheck >= checkIntervalHours;
  }

  /// Load cached update result
  /// تحميل نتيجة التحديث المخزنة مؤقتًا
  Future<void> _loadCachedResult() async {
    final prefs = await SharedPreferences.getInstance();
    final cachedJson = prefs.getString(UpdateStorageKeys.cachedUpdateInfo);
    final lastCheckMs = prefs.getInt(UpdateStorageKeys.lastCheckTime);

    if (cachedJson != null && lastCheckMs != null) {
      try {
        final packageInfo = await PackageInfo.fromPlatform();
        final currentVersion = packageInfo.version;
        final updateInfo = UpdateInfo.fromJson(json.decode(cachedJson) as Map<String, dynamic>);

        final result = await _evaluateUpdate(currentVersion, updateInfo);
        state = state.copyWith(
          lastResult: result,
          lastCheckTime: DateTime.fromMillisecondsSinceEpoch(lastCheckMs),
        );
      } catch (e) {
        AppLogger.w('Failed to load cached update info: $e');
      }
    }
  }

  /// Start periodic update check timer
  /// بدء مؤقت التحقق الدوري
  void _startPeriodicCheck() {
    _periodicCheckTimer?.cancel();
    _periodicCheckTimer = Timer.periodic(
      const Duration(hours: checkIntervalHours),
      (_) => checkForUpdates(),
    );
  }

  /// Stop periodic checks
  /// إيقاف التحقق الدوري
  void stopPeriodicChecks() {
    _periodicCheckTimer?.cancel();
    _periodicCheckTimer = null;
  }

  /// Check for updates from the API
  /// التحقق من التحديثات من واجهة برمجة التطبيقات
  Future<UpdateCheckResult> checkForUpdates({bool force = false}) async {
    if (state.isChecking) {
      return state.lastResult ?? UpdateCheckResult.noUpdate('unknown');
    }

    state = state.copyWith(isChecking: true);

    try {
      // Get current app version
      final packageInfo = await PackageInfo.fromPlatform();
      final currentVersion = packageInfo.version;

      AppLogger.i(
        'Checking for updates',
        data: {'current_version': currentVersion},
      );

      // Make API request
      final response = await _dio.get<Map<String, dynamic>>(
        _getUpdateEndpoint(),
        queryParameters: {
          'platform': Platform.isIOS ? 'ios' : 'android',
          'current_version': currentVersion,
        },
        options: Options(
          headers: ApiConfig.defaultHeaders,
          receiveTimeout: ApiConfig.receiveTimeout,
          sendTimeout: ApiConfig.sendTimeout,
        ),
      );

      if (response.statusCode == 200 && response.data != null) {
        final updateInfo = UpdateInfo.fromJson(response.data!);

        // Cache the result
        await _cacheUpdateInfo(updateInfo);

        // Evaluate the update
        final result = await _evaluateUpdate(currentVersion, updateInfo);

        state = state.copyWith(
          isChecking: false,
          lastResult: result,
          lastCheckTime: DateTime.now(),
        );

        return result;
      } else {
        throw Exception('Invalid response from update server');
      }
    } on DioException catch (e) {
      AppLogger.e(
        'Failed to check for updates',
        error: e,
        data: {'type': e.type.toString()},
      );

      final packageInfo = await PackageInfo.fromPlatform();
      final result = UpdateCheckResult.error(
        packageInfo.version,
        _getDioErrorMessage(e),
      );

      state = state.copyWith(isChecking: false, lastResult: result);
      return result;
    } catch (e) {
      AppLogger.e('Unexpected error checking for updates', error: e);

      final packageInfo = await PackageInfo.fromPlatform();
      final result = UpdateCheckResult.error(
        packageInfo.version,
        e.toString(),
      );

      state = state.copyWith(isChecking: false, lastResult: result);
      return result;
    }
  }

  /// Get the update check endpoint
  /// الحصول على نقطة نهاية التحقق من التحديث
  String _getUpdateEndpoint() {
    // Use gateway URL for update endpoint
    return '${ApiConfig.gatewayUrl}/api/v1/app/version';
  }

  /// Get error message from Dio exception
  /// الحصول على رسالة الخطأ من استثناء Dio
  String _getDioErrorMessage(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
        return 'Connection timeout';
      case DioExceptionType.sendTimeout:
        return 'Send timeout';
      case DioExceptionType.receiveTimeout:
        return 'Receive timeout';
      case DioExceptionType.connectionError:
        return 'No internet connection';
      case DioExceptionType.badResponse:
        return 'Server error: ${e.response?.statusCode}';
      default:
        return e.message ?? 'Unknown error';
    }
  }

  /// Cache update info for offline access
  /// تخزين معلومات التحديث مؤقتًا للوصول دون اتصال
  Future<void> _cacheUpdateInfo(UpdateInfo info) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      UpdateStorageKeys.cachedUpdateInfo,
      json.encode(info.toJson()),
    );
    await prefs.setInt(
      UpdateStorageKeys.lastCheckTime,
      DateTime.now().millisecondsSinceEpoch,
    );
  }

  /// Evaluate if update is needed
  /// تقييم ما إذا كان التحديث مطلوبًا
  Future<UpdateCheckResult> _evaluateUpdate(
    String currentVersion,
    UpdateInfo updateInfo,
  ) async {
    final current = SemanticVersion.parse(currentVersion);
    final latest = SemanticVersion.parse(updateInfo.latestVersion);
    final minimum = SemanticVersion.parse(updateInfo.minimumVersion);

    final updateType = VersionComparator.compareVersions(current, latest);
    final forceUpdate = VersionComparator.isForceUpdateRequired(current, minimum) ||
        updateInfo.isCritical;

    // Check if user has skipped this version
    final prefs = await SharedPreferences.getInstance();
    final skippedVersion = prefs.getString(UpdateStorageKeys.skippedVersion);
    final skipped = skippedVersion == updateInfo.latestVersion && !forceUpdate;

    // Check remind later
    final remindLaterTimeMs = prefs.getInt(UpdateStorageKeys.remindLaterTime);
    final remindLater = remindLaterTimeMs != null &&
        DateTime.now().isBefore(
          DateTime.fromMillisecondsSinceEpoch(remindLaterTimeMs),
        ) &&
        !forceUpdate;

    return UpdateCheckResult(
      updateAvailable: updateType != UpdateType.none,
      forceUpdate: forceUpdate,
      updateType: updateType,
      currentVersion: currentVersion,
      updateInfo: updateInfo,
      skipped: skipped,
      remindLater: remindLater,
    );
  }

  /// Skip this version (won't show again unless force update)
  /// تخطي هذا الإصدار (لن يظهر مرة أخرى إلا إذا كان تحديثًا إجباريًا)
  Future<void> skipVersion() async {
    final updateInfo = state.lastResult?.updateInfo;
    if (updateInfo == null) return;

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      UpdateStorageKeys.skippedVersion,
      updateInfo.latestVersion,
    );

    // Update state with skipped flag
    if (state.lastResult != null) {
      state = state.copyWith(
        lastResult: UpdateCheckResult(
          updateAvailable: state.lastResult!.updateAvailable,
          forceUpdate: state.lastResult!.forceUpdate,
          updateType: state.lastResult!.updateType,
          currentVersion: state.lastResult!.currentVersion,
          updateInfo: state.lastResult!.updateInfo,
          skipped: true,
          remindLater: state.lastResult!.remindLater,
        ),
      );
    }
  }

  /// Remind later (will check again after remindLaterHours)
  /// التذكير لاحقًا (سيتم التحقق مرة أخرى بعد remindLaterHours)
  Future<void> remindLater() async {
    final prefs = await SharedPreferences.getInstance();
    final remindTime = DateTime.now().add(const Duration(hours: remindLaterHours));
    await prefs.setInt(
      UpdateStorageKeys.remindLaterTime,
      remindTime.millisecondsSinceEpoch,
    );

    // Update state with remind later flag
    if (state.lastResult != null) {
      state = state.copyWith(
        lastResult: UpdateCheckResult(
          updateAvailable: state.lastResult!.updateAvailable,
          forceUpdate: state.lastResult!.forceUpdate,
          updateType: state.lastResult!.updateType,
          currentVersion: state.lastResult!.currentVersion,
          updateInfo: state.lastResult!.updateInfo,
          skipped: state.lastResult!.skipped,
          remindLater: true,
        ),
      );
    }
  }

  /// Clear remind later preference
  /// مسح تفضيل التذكير لاحقًا
  Future<void> clearRemindLater() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(UpdateStorageKeys.remindLaterTime);
  }

  /// Clear skipped version preference
  /// مسح تفضيل الإصدار المتخطى
  Future<void> clearSkippedVersion() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(UpdateStorageKeys.skippedVersion);
  }

  /// Open app store to download update
  /// فتح متجر التطبيقات لتحميل التحديث
  Future<bool> openAppStore() async {
    final customUrl = state.lastResult?.updateInfo?.customStoreUrl;

    String storeUrl;
    if (customUrl != null && customUrl.isNotEmpty) {
      storeUrl = customUrl;
    } else if (Platform.isIOS) {
      storeUrl = AppStoreUrls.iosAppStore;
    } else {
      storeUrl = AppStoreUrls.androidPlayStore;
    }

    try {
      final uri = Uri.parse(storeUrl);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
        return true;
      } else {
        AppLogger.w('Cannot launch app store URL: $storeUrl');
        return false;
      }
    } catch (e) {
      AppLogger.e('Error opening app store', error: e);
      return false;
    }
  }

  @override
  void dispose() {
    stopPeriodicChecks();
    super.dispose();
  }
}

/// Provider for update checker
/// مزود للتحقق من التحديثات
final updateCheckerProvider =
    StateNotifierProvider<UpdateCheckerNotifier, UpdateCheckerState>((ref) {
  return UpdateCheckerNotifier();
});

/// Provider for update check result
/// مزود لنتيجة التحقق من التحديث
final updateCheckResultProvider = Provider<UpdateCheckResult?>((ref) {
  return ref.watch(updateCheckerProvider).lastResult;
});

/// Provider for checking if update is available
/// مزود للتحقق مما إذا كان التحديث متاحًا
final updateAvailableProvider = Provider<bool>((ref) {
  final result = ref.watch(updateCheckResultProvider);
  if (result == null) return false;
  return result.updateAvailable && !result.skipped && !result.remindLater;
});

/// Provider for checking if force update is required
/// مزود للتحقق مما إذا كان التحديث الإجباري مطلوبًا
final forceUpdateRequiredProvider = Provider<bool>((ref) {
  final result = ref.watch(updateCheckResultProvider);
  return result?.forceUpdate ?? false;
});
