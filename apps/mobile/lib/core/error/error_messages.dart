/// SAHOOL Error Messages - Bilingual Support (Arabic/English)
/// رسائل الأخطاء - دعم ثنائي اللغة (عربي/إنجليزي)
///
/// Provides localized error messages for the SAHOOL mobile application.
/// Supports RTL layout for Arabic language.
library;

import 'package:flutter/material.dart';

/// Error message types for different error categories
enum ErrorType {
  /// Generic/unknown errors
  unknown,

  /// Network connectivity errors
  network,

  /// Server-side errors
  server,

  /// Authentication/authorization errors
  authentication,

  /// Data validation errors
  validation,

  /// Local storage/database errors
  storage,

  /// Permission errors
  permission,

  /// Timeout errors
  timeout,

  /// Sync errors
  sync,

  /// GPS/Location errors
  location,

  /// Camera/media errors
  media,

  /// Offline mode errors
  offline,
}

/// Bilingual error message with Arabic and English support
class ErrorMessage {
  final String titleEn;
  final String titleAr;
  final String messageEn;
  final String messageAr;
  final String? actionEn;
  final String? actionAr;
  final IconData icon;
  final Color? color;

  const ErrorMessage({
    required this.titleEn,
    required this.titleAr,
    required this.messageEn,
    required this.messageAr,
    this.actionEn,
    this.actionAr,
    this.icon = Icons.error_outline,
    this.color,
  });

  /// Get title based on locale
  String getTitle(Locale locale) {
    return locale.languageCode == 'ar' ? titleAr : titleEn;
  }

  /// Get message based on locale
  String getMessage(Locale locale) {
    return locale.languageCode == 'ar' ? messageAr : messageEn;
  }

  /// Get action text based on locale
  String? getAction(Locale locale) {
    if (actionEn == null && actionAr == null) return null;
    return locale.languageCode == 'ar' ? actionAr : actionEn;
  }

  /// Check if locale is RTL
  static bool isRtl(Locale locale) {
    return locale.languageCode == 'ar';
  }

  /// Get text direction based on locale
  static TextDirection getTextDirection(Locale locale) {
    return isRtl(locale) ? TextDirection.rtl : TextDirection.ltr;
  }
}

/// Predefined error messages for common error scenarios
class ErrorMessages {
  ErrorMessages._();

  /// Common action texts
  static const String retryEn = 'Try Again';
  static const String retryAr = 'إعادة المحاولة';
  static const String goBackEn = 'Go Back';
  static const String goBackAr = 'رجوع';
  static const String refreshEn = 'Refresh';
  static const String refreshAr = 'تحديث';
  static const String settingsEn = 'Settings';
  static const String settingsAr = 'الإعدادات';
  static const String contactSupportEn = 'Contact Support';
  static const String contactSupportAr = 'اتصل بالدعم';
  static const String viewDetailsEn = 'View Details';
  static const String viewDetailsAr = 'عرض التفاصيل';
  static const String dismissEn = 'Dismiss';
  static const String dismissAr = 'إغلاق';
  static const String loginEn = 'Login';
  static const String loginAr = 'تسجيل الدخول';

  /// Unknown/Generic error
  static const ErrorMessage unknown = ErrorMessage(
    titleEn: 'Something Went Wrong',
    titleAr: 'حدث خطأ غير متوقع',
    messageEn: 'An unexpected error occurred. Please try again.',
    messageAr: 'حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.',
    actionEn: retryEn,
    actionAr: retryAr,
    icon: Icons.error_outline,
  );

  /// Network connectivity error
  static const ErrorMessage network = ErrorMessage(
    titleEn: 'No Internet Connection',
    titleAr: 'لا يوجد اتصال بالإنترنت',
    messageEn: 'Please check your internet connection and try again.',
    messageAr: 'يرجى التحقق من اتصالك بالإنترنت والمحاولة مرة أخرى.',
    actionEn: retryEn,
    actionAr: retryAr,
    icon: Icons.wifi_off_rounded,
  );

  /// Server error
  static const ErrorMessage server = ErrorMessage(
    titleEn: 'Server Error',
    titleAr: 'خطأ في الخادم',
    messageEn: 'Our servers are temporarily unavailable. Please try again later.',
    messageAr: 'الخوادم غير متاحة مؤقتاً. يرجى المحاولة لاحقاً.',
    actionEn: retryEn,
    actionAr: retryAr,
    icon: Icons.cloud_off_rounded,
  );

  /// Authentication error
  static const ErrorMessage authentication = ErrorMessage(
    titleEn: 'Authentication Required',
    titleAr: 'يتطلب تسجيل الدخول',
    messageEn: 'Your session has expired. Please log in again.',
    messageAr: 'انتهت صلاحية جلستك. يرجى تسجيل الدخول مرة أخرى.',
    actionEn: loginEn,
    actionAr: loginAr,
    icon: Icons.lock_outline_rounded,
  );

  /// Validation error
  static const ErrorMessage validation = ErrorMessage(
    titleEn: 'Invalid Input',
    titleAr: 'إدخال غير صالح',
    messageEn: 'Please check your input and try again.',
    messageAr: 'يرجى التحقق من البيانات المدخلة والمحاولة مرة أخرى.',
    actionEn: goBackEn,
    actionAr: goBackAr,
    icon: Icons.warning_amber_rounded,
  );

  /// Storage error
  static const ErrorMessage storage = ErrorMessage(
    titleEn: 'Storage Error',
    titleAr: 'خطأ في التخزين',
    messageEn: 'Unable to save or load data. Please check your device storage.',
    messageAr: 'تعذر حفظ أو تحميل البيانات. يرجى التحقق من مساحة التخزين.',
    actionEn: retryEn,
    actionAr: retryAr,
    icon: Icons.storage_rounded,
  );

  /// Permission error
  static const ErrorMessage permission = ErrorMessage(
    titleEn: 'Permission Required',
    titleAr: 'يتطلب إذن',
    messageEn: 'This feature requires additional permissions. Please grant access in settings.',
    messageAr: 'هذه الميزة تتطلب أذونات إضافية. يرجى منح الوصول من الإعدادات.',
    actionEn: settingsEn,
    actionAr: settingsAr,
    icon: Icons.security_rounded,
  );

  /// Timeout error
  static const ErrorMessage timeout = ErrorMessage(
    titleEn: 'Request Timeout',
    titleAr: 'انتهت مهلة الطلب',
    messageEn: 'The request took too long. Please check your connection and try again.',
    messageAr: 'استغرق الطلب وقتاً طويلاً. يرجى التحقق من الاتصال والمحاولة مرة أخرى.',
    actionEn: retryEn,
    actionAr: retryAr,
    icon: Icons.timer_off_rounded,
  );

  /// Sync error
  static const ErrorMessage sync = ErrorMessage(
    titleEn: 'Sync Error',
    titleAr: 'خطأ في المزامنة',
    messageEn: 'Unable to sync your data. Changes will be saved locally.',
    messageAr: 'تعذرت مزامنة بياناتك. سيتم حفظ التغييرات محلياً.',
    actionEn: retryEn,
    actionAr: retryAr,
    icon: Icons.sync_problem_rounded,
  );

  /// Location error
  static const ErrorMessage location = ErrorMessage(
    titleEn: 'Location Error',
    titleAr: 'خطأ في الموقع',
    messageEn: 'Unable to get your location. Please enable GPS and try again.',
    messageAr: 'تعذر الحصول على موقعك. يرجى تفعيل GPS والمحاولة مرة أخرى.',
    actionEn: settingsEn,
    actionAr: settingsAr,
    icon: Icons.location_off_rounded,
  );

  /// Media/Camera error
  static const ErrorMessage media = ErrorMessage(
    titleEn: 'Camera Error',
    titleAr: 'خطأ في الكاميرا',
    messageEn: 'Unable to access camera. Please check permissions.',
    messageAr: 'تعذر الوصول إلى الكاميرا. يرجى التحقق من الأذونات.',
    actionEn: settingsEn,
    actionAr: settingsAr,
    icon: Icons.camera_alt_outlined,
  );

  /// Offline mode error
  static const ErrorMessage offline = ErrorMessage(
    titleEn: 'Offline Mode',
    titleAr: 'وضع عدم الاتصال',
    messageEn: 'You are currently offline. Some features may be limited.',
    messageAr: 'أنت حالياً غير متصل. قد تكون بعض الميزات محدودة.',
    actionEn: refreshEn,
    actionAr: refreshAr,
    icon: Icons.cloud_off_rounded,
  );

  /// Field not found error
  static const ErrorMessage fieldNotFound = ErrorMessage(
    titleEn: 'Field Not Found',
    titleAr: 'الحقل غير موجود',
    messageEn: 'The requested field could not be found.',
    messageAr: 'تعذر العثور على الحقل المطلوب.',
    actionEn: goBackEn,
    actionAr: goBackAr,
    icon: Icons.landscape_outlined,
  );

  /// Data loading error
  static const ErrorMessage dataLoading = ErrorMessage(
    titleEn: 'Loading Error',
    titleAr: 'خطأ في التحميل',
    messageEn: 'Unable to load data. Please try again.',
    messageAr: 'تعذر تحميل البيانات. يرجى المحاولة مرة أخرى.',
    actionEn: retryEn,
    actionAr: retryAr,
    icon: Icons.refresh_rounded,
  );

  /// Map loading error
  static const ErrorMessage mapLoading = ErrorMessage(
    titleEn: 'Map Error',
    titleAr: 'خطأ في الخريطة',
    messageEn: 'Unable to load the map. Please try again.',
    messageAr: 'تعذر تحميل الخريطة. يرجى المحاولة مرة أخرى.',
    actionEn: retryEn,
    actionAr: retryAr,
    icon: Icons.map_outlined,
  );

  /// Weather data error
  static const ErrorMessage weatherData = ErrorMessage(
    titleEn: 'Weather Data Error',
    titleAr: 'خطأ في بيانات الطقس',
    messageEn: 'Unable to load weather information.',
    messageAr: 'تعذر تحميل معلومات الطقس.',
    actionEn: retryEn,
    actionAr: retryAr,
    icon: Icons.cloud_outlined,
  );

  /// Get error message by type
  static ErrorMessage getByType(ErrorType type) {
    switch (type) {
      case ErrorType.network:
        return network;
      case ErrorType.server:
        return server;
      case ErrorType.authentication:
        return authentication;
      case ErrorType.validation:
        return validation;
      case ErrorType.storage:
        return storage;
      case ErrorType.permission:
        return permission;
      case ErrorType.timeout:
        return timeout;
      case ErrorType.sync:
        return sync;
      case ErrorType.location:
        return location;
      case ErrorType.media:
        return media;
      case ErrorType.offline:
        return offline;
      case ErrorType.unknown:
      default:
        return unknown;
    }
  }

  /// Detect error type from exception
  static ErrorType detectErrorType(Object error) {
    final errorString = error.toString().toLowerCase();

    if (errorString.contains('socket') ||
        errorString.contains('network') ||
        errorString.contains('connection refused') ||
        errorString.contains('no internet')) {
      return ErrorType.network;
    }

    if (errorString.contains('timeout') || errorString.contains('timed out')) {
      return ErrorType.timeout;
    }

    if (errorString.contains('401') ||
        errorString.contains('403') ||
        errorString.contains('unauthorized') ||
        errorString.contains('unauthenticated')) {
      return ErrorType.authentication;
    }

    if (errorString.contains('500') ||
        errorString.contains('502') ||
        errorString.contains('503') ||
        errorString.contains('server error')) {
      return ErrorType.server;
    }

    if (errorString.contains('permission') || errorString.contains('denied')) {
      return ErrorType.permission;
    }

    if (errorString.contains('storage') ||
        errorString.contains('database') ||
        errorString.contains('disk')) {
      return ErrorType.storage;
    }

    if (errorString.contains('sync') || errorString.contains('conflict')) {
      return ErrorType.sync;
    }

    if (errorString.contains('location') ||
        errorString.contains('gps') ||
        errorString.contains('geolocation')) {
      return ErrorType.location;
    }

    if (errorString.contains('camera') ||
        errorString.contains('photo') ||
        errorString.contains('media')) {
      return ErrorType.media;
    }

    if (errorString.contains('validation') ||
        errorString.contains('invalid') ||
        errorString.contains('required')) {
      return ErrorType.validation;
    }

    return ErrorType.unknown;
  }

  /// Get error message from exception
  static ErrorMessage fromException(Object error) {
    final type = detectErrorType(error);
    return getByType(type);
  }
}

/// Extension for easy access to localized strings
extension ErrorMessageLocalization on ErrorMessage {
  /// Get localized title from context
  String localizedTitle(BuildContext context) {
    final locale = Localizations.localeOf(context);
    return getTitle(locale);
  }

  /// Get localized message from context
  String localizedMessage(BuildContext context) {
    final locale = Localizations.localeOf(context);
    return getMessage(locale);
  }

  /// Get localized action from context
  String? localizedAction(BuildContext context) {
    final locale = Localizations.localeOf(context);
    return getAction(locale);
  }
}
