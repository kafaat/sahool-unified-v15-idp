import 'dart:async';
import 'dart:convert';
import 'dart:ui' as ui;
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../utils/app_logger.dart';

/// App State Manager - Manages app lifecycle and screen state persistence
/// مدير حالة التطبيق - يدير دورة حياة التطبيق وحفظ حالة الشاشة
///
/// Features:
/// - Save current screen on app background
/// - Restore to last screen on app resume
/// - Track app lifecycle events
/// - Persist navigation state
///
/// Usage:
/// 1. Initialize in main.dart using AppLifecycleObserver
/// 2. Call saveCurrentScreen() when navigating
/// 3. Call getLastScreen() to restore state

// ============================================================
// Constants
// ============================================================

const String _keyLastScreen = 'app_state_last_screen';
const String _keyLastScreenArgs = 'app_state_last_screen_args';
const String _keyLastActiveTime = 'app_state_last_active_time';
const String _keyAppWasBackgrounded = 'app_state_was_backgrounded';
const String _keyNavigationStack = 'app_state_navigation_stack';
const String _keyBottomNavIndex = 'app_state_bottom_nav_index';

// ============================================================
// Data Models
// ============================================================

/// Represents a navigation state that can be saved and restored
/// يمثل حالة التنقل التي يمكن حفظها واستعادتها
class NavigationState {
  final String routeName;
  final Map<String, dynamic>? arguments;
  final int? bottomNavIndex;
  final DateTime timestamp;

  const NavigationState({
    required this.routeName,
    this.arguments,
    this.bottomNavIndex,
    required this.timestamp,
  });

  Map<String, dynamic> toJson() => {
        'routeName': routeName,
        'arguments': arguments,
        'bottomNavIndex': bottomNavIndex,
        'timestamp': timestamp.toIso8601String(),
      };

  factory NavigationState.fromJson(Map<String, dynamic> json) {
    return NavigationState(
      routeName: json['routeName'] as String,
      arguments: json['arguments'] as Map<String, dynamic>?,
      bottomNavIndex: json['bottomNavIndex'] as int?,
      timestamp: DateTime.parse(json['timestamp'] as String),
    );
  }

  @override
  String toString() =>
      'NavigationState(route: $routeName, navIndex: $bottomNavIndex)';
}

// ============================================================
// App State Manager Service
// ============================================================

/// Service for managing app state persistence
/// خدمة إدارة حفظ حالة التطبيق
class AppStateManager {
  late SharedPreferences _prefs;
  bool _isInitialized = false;

  // Callbacks for lifecycle events
  final List<VoidCallback> _onBackgroundCallbacks = [];
  final List<VoidCallback> _onForegroundCallbacks = [];

  /// Initialize the app state manager
  /// تهيئة مدير حالة التطبيق
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      _prefs = await SharedPreferences.getInstance();
      _isInitialized = true;
      AppLogger.i('AppStateManager initialized', tag: 'AppState');
    } catch (e) {
      AppLogger.e('Failed to initialize AppStateManager',
          tag: 'AppState', error: e);
      rethrow;
    }
  }

  /// Ensure manager is initialized
  void _ensureInitialized() {
    if (!_isInitialized) {
      throw StateError(
        'AppStateManager not initialized. Call initialize() first.',
      );
    }
  }

  // ============================================================
  // Screen State Management
  // ============================================================

  /// Save current screen state
  /// حفظ حالة الشاشة الحالية
  Future<void> saveCurrentScreen({
    required String routeName,
    Map<String, dynamic>? arguments,
    int? bottomNavIndex,
  }) async {
    _ensureInitialized();

    try {
      await Future.wait([
        _prefs.setString(_keyLastScreen, routeName),
        if (arguments != null)
          _prefs.setString(_keyLastScreenArgs, jsonEncode(arguments)),
        if (bottomNavIndex != null)
          _prefs.setInt(_keyBottomNavIndex, bottomNavIndex),
        _prefs.setString(
          _keyLastActiveTime,
          DateTime.now().toIso8601String(),
        ),
      ]);

      AppLogger.d(
        'Saved screen state',
        tag: 'AppState',
        data: {
          'route': routeName,
          'navIndex': bottomNavIndex,
        },
      );
    } catch (e) {
      AppLogger.e('Failed to save screen state', tag: 'AppState', error: e);
    }
  }

  /// Get last saved screen state
  /// الحصول على حالة الشاشة المحفوظة الأخيرة
  Future<NavigationState?> getLastScreen() async {
    _ensureInitialized();

    try {
      final routeName = _prefs.getString(_keyLastScreen);
      if (routeName == null) return null;

      final argsJson = _prefs.getString(_keyLastScreenArgs);
      final bottomNavIndex = _prefs.getInt(_keyBottomNavIndex);
      final timestampStr = _prefs.getString(_keyLastActiveTime);

      Map<String, dynamic>? arguments;
      if (argsJson != null) {
        arguments = jsonDecode(argsJson) as Map<String, dynamic>;
      }

      DateTime timestamp;
      if (timestampStr != null) {
        timestamp = DateTime.parse(timestampStr);
      } else {
        timestamp = DateTime.now();
      }

      return NavigationState(
        routeName: routeName,
        arguments: arguments,
        bottomNavIndex: bottomNavIndex,
        timestamp: timestamp,
      );
    } catch (e) {
      AppLogger.e('Failed to get last screen', tag: 'AppState', error: e);
      return null;
    }
  }

  /// Save bottom navigation index
  /// حفظ فهرس التنقل السفلي
  Future<void> saveBottomNavIndex(int index) async {
    _ensureInitialized();

    try {
      await _prefs.setInt(_keyBottomNavIndex, index);
      AppLogger.d('Saved bottom nav index: $index', tag: 'AppState');
    } catch (e) {
      AppLogger.e('Failed to save bottom nav index', tag: 'AppState', error: e);
    }
  }

  /// Get saved bottom navigation index
  /// الحصول على فهرس التنقل السفلي المحفوظ
  int? getBottomNavIndex() {
    _ensureInitialized();
    return _prefs.getInt(_keyBottomNavIndex);
  }

  /// Clear saved screen state
  /// مسح حالة الشاشة المحفوظة
  Future<void> clearScreenState() async {
    _ensureInitialized();

    try {
      await Future.wait([
        _prefs.remove(_keyLastScreen),
        _prefs.remove(_keyLastScreenArgs),
        _prefs.remove(_keyBottomNavIndex),
        _prefs.remove(_keyLastActiveTime),
      ]);
      AppLogger.d('Cleared screen state', tag: 'AppState');
    } catch (e) {
      AppLogger.e('Failed to clear screen state', tag: 'AppState', error: e);
    }
  }

  // ============================================================
  // Navigation Stack Management
  // ============================================================

  /// Save navigation stack for deep restoration
  /// حفظ مكدس التنقل للاستعادة العميقة
  Future<void> saveNavigationStack(List<NavigationState> stack) async {
    _ensureInitialized();

    try {
      final jsonList = stack.map((s) => s.toJson()).toList();
      await _prefs.setString(_keyNavigationStack, jsonEncode(jsonList));
      AppLogger.d('Saved navigation stack: ${stack.length} items',
          tag: 'AppState');
    } catch (e) {
      AppLogger.e('Failed to save navigation stack', tag: 'AppState', error: e);
    }
  }

  /// Get saved navigation stack
  /// الحصول على مكدس التنقل المحفوظ
  Future<List<NavigationState>> getNavigationStack() async {
    _ensureInitialized();

    try {
      final jsonStr = _prefs.getString(_keyNavigationStack);
      if (jsonStr == null) return [];

      final jsonList = jsonDecode(jsonStr) as List;
      return jsonList
          .map((j) => NavigationState.fromJson(j as Map<String, dynamic>))
          .toList();
    } catch (e) {
      AppLogger.e('Failed to get navigation stack', tag: 'AppState', error: e);
      return [];
    }
  }

  /// Clear navigation stack
  /// مسح مكدس التنقل
  Future<void> clearNavigationStack() async {
    _ensureInitialized();

    try {
      await _prefs.remove(_keyNavigationStack);
      AppLogger.d('Cleared navigation stack', tag: 'AppState');
    } catch (e) {
      AppLogger.e('Failed to clear navigation stack',
          tag: 'AppState', error: e);
    }
  }

  // ============================================================
  // Lifecycle Management
  // ============================================================

  /// Called when app goes to background
  /// يُستدعى عندما ينتقل التطبيق إلى الخلفية
  Future<void> onAppBackgrounded() async {
    _ensureInitialized();

    try {
      await _prefs.setBool(_keyAppWasBackgrounded, true);
      await _prefs.setString(
        _keyLastActiveTime,
        DateTime.now().toIso8601String(),
      );

      // Execute callbacks
      for (final callback in _onBackgroundCallbacks) {
        callback();
      }

      AppLogger.i('App backgrounded', tag: 'AppState');
    } catch (e) {
      AppLogger.e('Error in onAppBackgrounded', tag: 'AppState', error: e);
    }
  }

  /// Called when app comes to foreground
  /// يُستدعى عندما ينتقل التطبيق إلى المقدمة
  Future<void> onAppResumed() async {
    _ensureInitialized();

    try {
      await _prefs.setBool(_keyAppWasBackgrounded, false);

      // Execute callbacks
      for (final callback in _onForegroundCallbacks) {
        callback();
      }

      AppLogger.i('App resumed', tag: 'AppState');
    } catch (e) {
      AppLogger.e('Error in onAppResumed', tag: 'AppState', error: e);
    }
  }

  /// Check if app was backgrounded
  /// التحقق مما إذا كان التطبيق قد انتقل إلى الخلفية
  bool wasAppBackgrounded() {
    _ensureInitialized();
    return _prefs.getBool(_keyAppWasBackgrounded) ?? false;
  }

  /// Get last active time
  /// الحصول على آخر وقت نشاط
  DateTime? getLastActiveTime() {
    _ensureInitialized();

    final timestampStr = _prefs.getString(_keyLastActiveTime);
    if (timestampStr == null) return null;

    try {
      return DateTime.parse(timestampStr);
    } catch (_) {
      return null;
    }
  }

  /// Check if session expired (e.g., after 30 minutes of inactivity)
  /// التحقق مما إذا كانت الجلسة قد انتهت
  bool isSessionExpired({Duration timeout = const Duration(minutes: 30)}) {
    final lastActive = getLastActiveTime();
    if (lastActive == null) return false;

    return DateTime.now().difference(lastActive) > timeout;
  }

  // ============================================================
  // Lifecycle Callbacks
  // ============================================================

  /// Register callback for when app goes to background
  /// تسجيل دالة استدعاء عند انتقال التطبيق إلى الخلفية
  void addOnBackgroundCallback(VoidCallback callback) {
    _onBackgroundCallbacks.add(callback);
  }

  /// Remove background callback
  /// إزالة دالة استدعاء الخلفية
  void removeOnBackgroundCallback(VoidCallback callback) {
    _onBackgroundCallbacks.remove(callback);
  }

  /// Register callback for when app comes to foreground
  /// تسجيل دالة استدعاء عند انتقال التطبيق إلى المقدمة
  void addOnForegroundCallback(VoidCallback callback) {
    _onForegroundCallbacks.add(callback);
  }

  /// Remove foreground callback
  /// إزالة دالة استدعاء المقدمة
  void removeOnForegroundCallback(VoidCallback callback) {
    _onForegroundCallbacks.remove(callback);
  }

  // ============================================================
  // Cleanup
  // ============================================================

  /// Clear all app state
  /// مسح جميع حالات التطبيق
  Future<void> clearAll() async {
    _ensureInitialized();

    try {
      await Future.wait([
        clearScreenState(),
        clearNavigationStack(),
        _prefs.remove(_keyAppWasBackgrounded),
      ]);
      AppLogger.i('Cleared all app state', tag: 'AppState');
    } catch (e) {
      AppLogger.e('Failed to clear all app state', tag: 'AppState', error: e);
    }
  }
}

// ============================================================
// App Lifecycle Observer (WidgetsBindingObserver)
// ============================================================

/// Observer for app lifecycle events that integrates with AppStateManager
/// مراقب أحداث دورة حياة التطبيق المتكامل مع AppStateManager
class AppLifecycleObserver with WidgetsBindingObserver {
  final AppStateManager _stateManager;
  final VoidCallback? onBackground;
  final VoidCallback? onForeground;
  final void Function(String routeName)? getCurrentRoute;

  AppLifecycleObserver({
    required AppStateManager stateManager,
    this.onBackground,
    this.onForeground,
    this.getCurrentRoute,
  }) : _stateManager = stateManager;

  /// Register the observer
  /// تسجيل المراقب
  void register() {
    WidgetsBinding.instance.addObserver(this);
    AppLogger.d('AppLifecycleObserver registered', tag: 'AppState');
  }

  /// Unregister the observer
  /// إلغاء تسجيل المراقب
  void unregister() {
    WidgetsBinding.instance.removeObserver(this);
    AppLogger.d('AppLifecycleObserver unregistered', tag: 'AppState');
  }

  @override
  void didChangeAppLifecycleState(ui.AppLifecycleState state) {
    AppLogger.d('App lifecycle state changed: $state', tag: 'AppState');

    switch (state) {
      case ui.AppLifecycleState.paused:
      case ui.AppLifecycleState.inactive:
        _handleAppBackground();
        break;
      case ui.AppLifecycleState.resumed:
        _handleAppForeground();
        break;
      case ui.AppLifecycleState.detached:
      case ui.AppLifecycleState.hidden:
        // App is being destroyed or hidden
        break;
    }
  }

  void _handleAppBackground() {
    // Save current route if available
    if (getCurrentRoute != null) {
      // The getCurrentRoute callback should be provided by the app
      // to get the current route name
    }

    _stateManager.onAppBackgrounded();
    onBackground?.call();
  }

  void _handleAppForeground() {
    _stateManager.onAppResumed();
    onForeground?.call();
  }
}

// ============================================================
// Riverpod Providers
// ============================================================

/// Provider for AppStateManager
final appStateManagerProvider = Provider<AppStateManager>((ref) {
  return AppStateManager();
});

/// Provider for last navigation state
final lastNavigationStateProvider =
    FutureProvider<NavigationState?>((ref) async {
  final manager = ref.watch(appStateManagerProvider);
  await manager.initialize();
  return manager.getLastScreen();
});

/// Provider for bottom nav index
final savedBottomNavIndexProvider = Provider<int?>((ref) {
  final manager = ref.watch(appStateManagerProvider);
  try {
    return manager.getBottomNavIndex();
  } catch (_) {
    return null;
  }
});
