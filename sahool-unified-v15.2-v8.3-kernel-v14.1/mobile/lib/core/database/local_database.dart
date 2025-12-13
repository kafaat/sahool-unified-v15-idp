// ============================================
// SAHOOL - Local Database
// قاعدة البيانات المحلية للعمل بدون اتصال
// ============================================

import 'package:hive_flutter/hive_flutter.dart';
import 'package:path_provider/path_provider.dart';

class LocalDatabase {
  static const String _userBox = 'user';
  static const String _fieldsBox = 'fields';
  static const String _tasksBox = 'tasks';
  static const String _calendarBox = 'calendar';
  static const String _settingsBox = 'settings';
  static const String _cacheBox = 'cache';

  bool _isInitialized = false;

  Future<void> init() async {
    if (_isInitialized) return;

    final appDir = await getApplicationDocumentsDirectory();
    await Hive.initFlutter(appDir.path);

    // Open boxes
    await Hive.openBox(_userBox);
    await Hive.openBox(_fieldsBox);
    await Hive.openBox(_tasksBox);
    await Hive.openBox(_calendarBox);
    await Hive.openBox(_settingsBox);
    await Hive.openBox(_cacheBox);

    _isInitialized = true;
  }

  // ============================================
  // USER
  // ============================================

  Future<void> saveUser(Map<String, dynamic> user) async {
    final box = Hive.box(_userBox);
    await box.put('current_user', user);
  }

  Map<String, dynamic>? getUser() {
    final box = Hive.box(_userBox);
    return box.get('current_user');
  }

  Future<void> clearUser() async {
    final box = Hive.box(_userBox);
    await box.delete('current_user');
  }

  // ============================================
  // FIELDS
  // ============================================

  Future<void> saveFields(List<Map<String, dynamic>> fields) async {
    final box = Hive.box(_fieldsBox);
    await box.put('all_fields', fields);
    await box.put('last_sync', DateTime.now().toIso8601String());
  }

  List<Map<String, dynamic>> getFields() {
    final box = Hive.box(_fieldsBox);
    final data = box.get('all_fields');
    if (data == null) return [];
    return List<Map<String, dynamic>>.from(data);
  }

  Future<void> saveField(String id, Map<String, dynamic> field) async {
    final box = Hive.box(_fieldsBox);
    await box.put('field_$id', field);
  }

  Map<String, dynamic>? getField(String id) {
    final box = Hive.box(_fieldsBox);
    return box.get('field_$id');
  }

  // ============================================
  // TASKS
  // ============================================

  Future<void> saveTasks(List<Map<String, dynamic>> tasks) async {
    final box = Hive.box(_tasksBox);
    await box.put('all_tasks', tasks);
    await box.put('last_sync', DateTime.now().toIso8601String());
  }

  List<Map<String, dynamic>> getTasks() {
    final box = Hive.box(_tasksBox);
    final data = box.get('all_tasks');
    if (data == null) return [];
    return List<Map<String, dynamic>>.from(data);
  }

  Future<void> savePendingTask(Map<String, dynamic> task) async {
    final box = Hive.box(_tasksBox);
    final pending = getPendingTasks();
    pending.add(task);
    await box.put('pending_tasks', pending);
  }

  List<Map<String, dynamic>> getPendingTasks() {
    final box = Hive.box(_tasksBox);
    final data = box.get('pending_tasks');
    if (data == null) return [];
    return List<Map<String, dynamic>>.from(data);
  }

  Future<void> clearPendingTasks() async {
    final box = Hive.box(_tasksBox);
    await box.delete('pending_tasks');
  }

  // ============================================
  // CALENDAR
  // ============================================

  Future<void> saveCurrentNaw(Map<String, dynamic> naw) async {
    final box = Hive.box(_calendarBox);
    await box.put('current_naw', naw);
    await box.put('last_update', DateTime.now().toIso8601String());
  }

  Map<String, dynamic>? getCurrentNaw() {
    final box = Hive.box(_calendarBox);
    return box.get('current_naw');
  }

  Future<void> saveAllAnwa(List<Map<String, dynamic>> anwa) async {
    final box = Hive.box(_calendarBox);
    await box.put('all_anwa', anwa);
  }

  List<Map<String, dynamic>> getAllAnwa() {
    final box = Hive.box(_calendarBox);
    final data = box.get('all_anwa');
    if (data == null) return [];
    return List<Map<String, dynamic>>.from(data);
  }

  // ============================================
  // SETTINGS
  // ============================================

  Future<void> saveSetting(String key, dynamic value) async {
    final box = Hive.box(_settingsBox);
    await box.put(key, value);
  }

  T? getSetting<T>(String key, {T? defaultValue}) {
    final box = Hive.box(_settingsBox);
    return box.get(key, defaultValue: defaultValue);
  }

  String getLanguage() => getSetting('language', defaultValue: 'ar')!;
  bool isDarkMode() => getSetting('dark_mode', defaultValue: false)!;
  bool isOfflineMode() => getSetting('offline_mode', defaultValue: false)!;
  bool areNotificationsEnabled() => getSetting('notifications', defaultValue: true)!;

  // ============================================
  // CACHE
  // ============================================

  Future<void> cacheData(String key, dynamic data, {Duration? expiry}) async {
    final box = Hive.box(_cacheBox);
    final cacheEntry = {
      'data': data,
      'timestamp': DateTime.now().toIso8601String(),
      'expiry': expiry?.inMilliseconds,
    };
    await box.put(key, cacheEntry);
  }

  dynamic getCachedData(String key) {
    final box = Hive.box(_cacheBox);
    final entry = box.get(key);
    
    if (entry == null) return null;
    
    // Check expiry
    if (entry['expiry'] != null) {
      final timestamp = DateTime.parse(entry['timestamp']);
      final expiry = Duration(milliseconds: entry['expiry']);
      if (DateTime.now().isAfter(timestamp.add(expiry))) {
        box.delete(key);
        return null;
      }
    }
    
    return entry['data'];
  }

  Future<void> clearCache() async {
    final box = Hive.box(_cacheBox);
    await box.clear();
  }

  // ============================================
  // SYNC STATUS
  // ============================================

  DateTime? getLastSync(String boxName) {
    final box = Hive.box(boxName);
    final lastSync = box.get('last_sync');
    if (lastSync == null) return null;
    return DateTime.parse(lastSync);
  }

  bool needsSync(String boxName, {Duration maxAge = const Duration(hours: 1)}) {
    final lastSync = getLastSync(boxName);
    if (lastSync == null) return true;
    return DateTime.now().isAfter(lastSync.add(maxAge));
  }

  // ============================================
  // CLEAR ALL
  // ============================================

  Future<void> clearAll() async {
    await Hive.box(_userBox).clear();
    await Hive.box(_fieldsBox).clear();
    await Hive.box(_tasksBox).clear();
    await Hive.box(_calendarBox).clear();
    await Hive.box(_settingsBox).clear();
    await Hive.box(_cacheBox).clear();
  }
}
