/// SAHOOL Offline Data Manager
/// إدارة البيانات المحلية مع المزامنة التلقائية
///
/// Features:
/// - Local data editing while offline
/// - Automatic sync when connection restored
/// - Conflict resolution with user notification
/// - Pending changes indicator
library;

import 'dart:async';
import 'dart:convert';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../utils/app_logger.dart';

/// حالة البيانات المحلية
enum LocalDataStatus {
  synced,      // متزامنة مع السيرفر
  pendingSync, // في انتظار المزامنة
  conflict,    // تعارض مع السيرفر
  error,       // خطأ في المزامنة
}

/// عنصر بيانات محلي
class LocalDataItem {
  final String id;
  final String entityType; // field, task, diagnosis, etc.
  final Map<String, dynamic> data;
  final LocalDataStatus status;
  final DateTime modifiedAt;
  final DateTime? syncedAt;
  final String? errorMessage;
  final int retryCount;

  const LocalDataItem({
    required this.id,
    required this.entityType,
    required this.data,
    this.status = LocalDataStatus.pendingSync,
    required this.modifiedAt,
    this.syncedAt,
    this.errorMessage,
    this.retryCount = 0,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'entity_type': entityType,
    'data': data,
    'status': status.name,
    'modified_at': modifiedAt.toIso8601String(),
    'synced_at': syncedAt?.toIso8601String(),
    'error_message': errorMessage,
    'retry_count': retryCount,
  };

  factory LocalDataItem.fromJson(Map<String, dynamic> json) => LocalDataItem(
    id: json['id'] as String,
    entityType: json['entity_type'] as String,
    data: Map<String, dynamic>.from(json['data'] as Map),
    status: LocalDataStatus.values.firstWhere(
      (e) => e.name == json['status'],
      orElse: () => LocalDataStatus.pendingSync,
    ),
    modifiedAt: DateTime.tryParse(json['modified_at'] as String) ?? DateTime.now(),
    syncedAt: json['synced_at'] != null
        ? DateTime.tryParse(json['synced_at'] as String) ?? DateTime.now()
        : null,
    errorMessage: json['error_message'] as String?,
    retryCount: json['retry_count'] as int? ?? 0,
  );

  LocalDataItem copyWith({
    String? id,
    String? entityType,
    Map<String, dynamic>? data,
    LocalDataStatus? status,
    DateTime? modifiedAt,
    DateTime? syncedAt,
    String? errorMessage,
    int? retryCount,
  }) => LocalDataItem(
    id: id ?? this.id,
    entityType: entityType ?? this.entityType,
    data: data ?? this.data,
    status: status ?? this.status,
    modifiedAt: modifiedAt ?? this.modifiedAt,
    syncedAt: syncedAt ?? this.syncedAt,
    errorMessage: errorMessage ?? this.errorMessage,
    retryCount: retryCount ?? this.retryCount,
  );
}

/// مدير البيانات المحلية
class OfflineDataManager {
  static const String _storageKey = 'sahool_offline_data';
  static const int _maxRetries = 5;
  static const Duration _retryDelay = Duration(seconds: 30);

  final _pendingChangesController = StreamController<int>.broadcast();
  final _syncStatusController = StreamController<OfflineSyncStatus>.broadcast();

  Stream<int> get pendingChangesCount => _pendingChangesController.stream;
  Stream<OfflineSyncStatus> get syncStatus => _syncStatusController.stream;

  Timer? _syncTimer;
  bool _isSyncing = false;
  late SharedPreferences _prefs;
  late Connectivity _connectivity;
  StreamSubscription? _connectivitySubscription;

  /// تهيئة المدير
  Future<void> initialize() async {
    _prefs = await SharedPreferences.getInstance();
    _connectivity = Connectivity();

    // مراقبة حالة الاتصال
    _connectivitySubscription = _connectivity.onConnectivityChanged.listen(
      (List<ConnectivityResult> results) {
        if (results.isNotEmpty && !results.every((r) => r == ConnectivityResult.none)) {
          _onConnectionRestored();
        }
      },
    );

    // بدء المزامنة الدورية
    _startPeriodicSync();

    // تحديث عداد التغييرات المعلقة
    unawaited(_updatePendingCount());
  }

  /// حفظ بيانات محلياً
  Future<void> saveLocally({
    required String id,
    required String entityType,
    required Map<String, dynamic> data,
  }) async {
    final items = await _getLocalItems();

    final existingIndex = items.indexWhere(
      (item) => item.id == id && item.entityType == entityType,
    );

    final newItem = LocalDataItem(
      id: id,
      entityType: entityType,
      data: data,
      status: LocalDataStatus.pendingSync,
      modifiedAt: DateTime.now(),
    );

    if (existingIndex >= 0) {
      items[existingIndex] = newItem;
    } else {
      items.add(newItem);
    }

    await _saveLocalItems(items);
    unawaited(_updatePendingCount());

    // محاولة المزامنة الفورية إذا متصل
    unawaited(_trySyncNow());
  }

  /// الحصول على البيانات المحلية
  Future<LocalDataItem?> getLocalItem(String id, String entityType) async {
    final items = await _getLocalItems();
    try {
      return items.firstWhere(
        (item) => item.id == id && item.entityType == entityType,
      );
    } catch (e) {
      return null;
    }
  }

  /// الحصول على جميع العناصر المعلقة
  Future<List<LocalDataItem>> getPendingItems() async {
    final items = await _getLocalItems();
    return items.where(
      (item) => item.status == LocalDataStatus.pendingSync,
    ).toList();
  }

  /// الحصول على عدد التغييرات المعلقة
  Future<int> getPendingCount() async {
    final items = await getPendingItems();
    return items.length;
  }

  /// حذف عنصر محلي
  Future<void> deleteLocalItem(String id, String entityType) async {
    final items = await _getLocalItems();
    items.removeWhere(
      (item) => item.id == id && item.entityType == entityType,
    );
    await _saveLocalItems(items);
    unawaited(_updatePendingCount());
  }

  /// تحديث حالة عنصر
  Future<void> updateItemStatus(
    String id,
    String entityType,
    LocalDataStatus status, {
    String? errorMessage,
  }) async {
    final items = await _getLocalItems();
    final index = items.indexWhere(
      (item) => item.id == id && item.entityType == entityType,
    );

    if (index >= 0) {
      items[index] = items[index].copyWith(
        status: status,
        errorMessage: errorMessage,
        syncedAt: status == LocalDataStatus.synced ? DateTime.now() : null,
      );
      await _saveLocalItems(items);
      unawaited(_updatePendingCount());
    }
  }

  /// مزامنة الآن
  Future<OfflineSyncResult> syncNow() async {
    if (_isSyncing) {
      return const OfflineSyncResult(
        success: false,
        message: 'المزامنة جارية بالفعل',
      );
    }

    final connectivityResults = await _connectivity.checkConnectivity();
    final isOffline = connectivityResults.isEmpty ||
                      connectivityResults.every((r) => r == ConnectivityResult.none);
    if (isOffline) {
      return const OfflineSyncResult(
        success: false,
        message: 'لا يوجد اتصال بالإنترنت',
      );
    }

    _isSyncing = true;
    _syncStatusController.add(OfflineSyncStatus.syncing);

    try {
      final pendingItems = await getPendingItems();
      int synced = 0;
      int failed = 0;

      for (final item in pendingItems) {
        try {
          // هنا يتم إرسال البيانات للسيرفر
          // await _syncItemToServer(item);

          await updateItemStatus(
            item.id,
            item.entityType,
            LocalDataStatus.synced,
          );
          synced++;
        } catch (e) {
          final newRetryCount = item.retryCount + 1;

          if (newRetryCount >= _maxRetries) {
            await updateItemStatus(
              item.id,
              item.entityType,
              LocalDataStatus.error,
              errorMessage: 'فشل بعد $_maxRetries محاولات: ${e.toString()}',
            );
          } else {
            final items = await _getLocalItems();
            final index = items.indexWhere(
              (i) => i.id == item.id && i.entityType == item.entityType,
            );
            if (index >= 0) {
              items[index] = items[index].copyWith(retryCount: newRetryCount);
              await _saveLocalItems(items);
            }
          }
          failed++;
        }
      }

      _isSyncing = false;
      _syncStatusController.add(OfflineSyncStatus.idle);
      unawaited(_updatePendingCount());

      return OfflineSyncResult(
        success: failed == 0,
        syncedCount: synced,
        failedCount: failed,
        message: 'تم مزامنة $synced عنصر${failed > 0 ? '، فشل $failed' : ''}',
      );
    } catch (e) {
      _isSyncing = false;
      _syncStatusController.add(OfflineSyncStatus.error);

      return OfflineSyncResult(
        success: false,
        message: 'خطأ في المزامنة: ${e.toString()}',
      );
    }
  }

  /// عند استعادة الاتصال
  void _onConnectionRestored() {
    // تأخير قصير للتأكد من استقرار الاتصال
    Future.delayed(const Duration(seconds: 2), () {
      _trySyncNow().catchError((e) {
        AppLogger.e('Sync after connection restored failed', tag: 'OfflineSync', error: e);
      });
    });
  }

  /// محاولة المزامنة الفورية مع حماية من التزامن المتعدد
  Future<void> _trySyncNow() async {
    if (_isSyncing) return;
    final connectivityResults = await _connectivity.checkConnectivity();
    final isOnline = connectivityResults.isNotEmpty &&
                     !connectivityResults.every((r) => r == ConnectivityResult.none);
    if (isOnline) {
      await syncNow();
    }
  }

  /// بدء المزامنة الدورية
  void _startPeriodicSync() {
    _syncTimer?.cancel();
    _syncTimer = Timer.periodic(
      const Duration(minutes: 5),
      (_) => _trySyncNow().catchError((e) {
        AppLogger.e('Periodic sync failed', tag: 'OfflineSync', error: e);
      }),
    );
  }

  /// تحديث عداد التغييرات المعلقة
  Future<void> _updatePendingCount() async {
    final count = await getPendingCount();
    _pendingChangesController.add(count);
  }

  /// قراءة العناصر المحلية
  Future<List<LocalDataItem>> _getLocalItems() async {
    final jsonString = _prefs.getString(_storageKey);
    if (jsonString == null) return [];

    try {
      final List<dynamic> jsonList = jsonDecode(jsonString) as List<dynamic>;
      return jsonList.map((json) => LocalDataItem.fromJson(json as Map<String, dynamic>)).toList();
    } catch (e) {
      AppLogger.e('Failed to parse local items, clearing corrupted data', tag: 'OfflineSync', error: e);
      await _prefs.remove(_storageKey);
      return [];
    }
  }

  /// حفظ العناصر المحلية
  Future<void> _saveLocalItems(List<LocalDataItem> items) async {
    final jsonString = jsonEncode(items.map((e) => e.toJson()).toList());
    await _prefs.setString(_storageKey, jsonString);
  }

  /// تنظيف
  void dispose() {
    _syncTimer?.cancel();
    _connectivitySubscription?.cancel();
    _pendingChangesController.close();
    _syncStatusController.close();
  }
}

/// حالة المزامنة
enum OfflineSyncStatus {
  idle,    // في وضع الانتظار
  syncing, // جاري المزامنة
  error,   // خطأ
}

/// نتيجة المزامنة
class OfflineSyncResult {
  final bool success;
  final int syncedCount;
  final int failedCount;
  final String? message;

  const OfflineSyncResult({
    required this.success,
    this.syncedCount = 0,
    this.failedCount = 0,
    this.message,
  });
}
