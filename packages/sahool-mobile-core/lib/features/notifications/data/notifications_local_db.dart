/// SAHOOL Notifications Local Database
/// قاعدة بيانات الإشعارات المحلية
///
/// SQLite-based local storage for notifications
/// enabling offline-first functionality
library;

import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

import '../domain/models/notification.dart';
import '../domain/models/notification_category.dart';
import '../domain/models/notification_settings.dart';

/// Local database for notifications
class NotificationsLocalDb {
  static const String _dbName = 'notifications.db';
  static const int _dbVersion = 1;
  static const String _notificationsTable = 'notifications';
  static const String _settingsTable = 'notification_settings';

  Database? _database;
  bool _initialized = false;

  /// Initialize the database
  Future<void> initialize() async {
    if (_initialized) return;

    final dbPath = await getDatabasesPath();
    final path = join(dbPath, _dbName);

    _database = await openDatabase(
      path,
      version: _dbVersion,
      onCreate: _onCreate,
      onUpgrade: _onUpgrade,
    );

    _initialized = true;
    debugPrint('NotificationsLocalDb initialized');
  }

  Future<void> _onCreate(Database db, int version) async {
    // Create notifications table
    await db.execute('''
      CREATE TABLE $_notificationsTable (
        id TEXT PRIMARY KEY,
        remote_id TEXT,
        tenant_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        category TEXT NOT NULL,
        priority INTEGER NOT NULL DEFAULT 2,
        title TEXT NOT NULL,
        title_ar TEXT NOT NULL,
        body TEXT NOT NULL,
        body_ar TEXT NOT NULL,
        summary TEXT,
        summary_ar TEXT,
        status TEXT NOT NULL DEFAULT 'unread',
        actions TEXT,
        primary_action TEXT,
        group_id TEXT,
        group_title TEXT,
        related_entity_type TEXT,
        related_entity_id TEXT,
        image_url TEXT,
        icon_name TEXT,
        data TEXT,
        created_at TEXT NOT NULL,
        read_at TEXT,
        expires_at TEXT,
        snoozed_until TEXT,
        synced INTEGER NOT NULL DEFAULT 0,
        source TEXT NOT NULL DEFAULT 'local',
        updated_at TEXT NOT NULL
      )
    ''');

    // Create indexes
    await db.execute('''
      CREATE INDEX idx_notifications_user ON $_notificationsTable(user_id)
    ''');
    await db.execute('''
      CREATE INDEX idx_notifications_category ON $_notificationsTable(category)
    ''');
    await db.execute('''
      CREATE INDEX idx_notifications_status ON $_notificationsTable(status)
    ''');
    await db.execute('''
      CREATE INDEX idx_notifications_created ON $_notificationsTable(created_at DESC)
    ''');
    await db.execute('''
      CREATE INDEX idx_notifications_synced ON $_notificationsTable(synced)
    ''');

    // Create settings table
    await db.execute('''
      CREATE TABLE $_settingsTable (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL UNIQUE,
        settings_json TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
    ''');

    debugPrint('NotificationsLocalDb tables created');
  }

  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    // Handle migrations for future versions
    debugPrint('NotificationsLocalDb upgraded from v$oldVersion to v$newVersion');
  }

  /// Ensure database is initialized
  Database get _db {
    if (!_initialized || _database == null) {
      throw StateError('Database not initialized. Call initialize() first.');
    }
    return _database!;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Notifications CRUD
  // ─────────────────────────────────────────────────────────────────────────────

  /// Insert or update a notification
  Future<void> upsertNotification(AppNotification notification) async {
    final now = DateTime.now().toIso8601String();

    await _db.insert(
      _notificationsTable,
      {
        'id': notification.id,
        'remote_id': notification.remoteId,
        'tenant_id': notification.tenantId,
        'user_id': notification.userId,
        'category': notification.category.name,
        'priority': notification.priority.value,
        'title': notification.title,
        'title_ar': notification.titleAr,
        'body': notification.body,
        'body_ar': notification.bodyAr,
        'summary': notification.summary,
        'summary_ar': notification.summaryAr,
        'status': notification.status.name,
        'actions': notification.actions.isNotEmpty
            ? jsonEncode(notification.actions.map((a) => a.toJson()).toList())
            : null,
        'primary_action': notification.primaryAction != null
            ? jsonEncode(notification.primaryAction!.toJson())
            : null,
        'group_id': notification.groupId,
        'group_title': notification.groupTitle,
        'related_entity_type': notification.relatedEntityType,
        'related_entity_id': notification.relatedEntityId,
        'image_url': notification.imageUrl,
        'icon_name': notification.iconName,
        'data': notification.data != null ? jsonEncode(notification.data) : null,
        'created_at': notification.createdAt.toIso8601String(),
        'read_at': notification.readAt?.toIso8601String(),
        'expires_at': notification.expiresAt?.toIso8601String(),
        'snoozed_until': notification.snoozedUntil?.toIso8601String(),
        'synced': notification.synced ? 1 : 0,
        'source': notification.source,
        'updated_at': now,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  /// Insert multiple notifications
  Future<void> upsertNotifications(List<AppNotification> notifications) async {
    final batch = _db.batch();
    final now = DateTime.now().toIso8601String();

    for (final notification in notifications) {
      batch.insert(
        _notificationsTable,
        {
          'id': notification.id,
          'remote_id': notification.remoteId,
          'tenant_id': notification.tenantId,
          'user_id': notification.userId,
          'category': notification.category.name,
          'priority': notification.priority.value,
          'title': notification.title,
          'title_ar': notification.titleAr,
          'body': notification.body,
          'body_ar': notification.bodyAr,
          'summary': notification.summary,
          'summary_ar': notification.summaryAr,
          'status': notification.status.name,
          'actions': notification.actions.isNotEmpty
              ? jsonEncode(notification.actions.map((a) => a.toJson()).toList())
              : null,
          'primary_action': notification.primaryAction != null
              ? jsonEncode(notification.primaryAction!.toJson())
              : null,
          'group_id': notification.groupId,
          'group_title': notification.groupTitle,
          'related_entity_type': notification.relatedEntityType,
          'related_entity_id': notification.relatedEntityId,
          'image_url': notification.imageUrl,
          'icon_name': notification.iconName,
          'data':
              notification.data != null ? jsonEncode(notification.data) : null,
          'created_at': notification.createdAt.toIso8601String(),
          'read_at': notification.readAt?.toIso8601String(),
          'expires_at': notification.expiresAt?.toIso8601String(),
          'snoozed_until': notification.snoozedUntil?.toIso8601String(),
          'synced': notification.synced ? 1 : 0,
          'source': notification.source,
          'updated_at': now,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }

    await batch.commit(noResult: true);
  }

  /// Get all notifications for a user
  Future<List<AppNotification>> getNotifications({
    required String userId,
    NotificationCategory? category,
    NotificationStatus? status,
    int limit = 100,
    int offset = 0,
    bool includeExpired = false,
  }) async {
    final where = <String>['user_id = ?'];
    final whereArgs = <dynamic>[userId];

    if (category != null) {
      where.add('category = ?');
      whereArgs.add(category.name);
    }

    if (status != null) {
      where.add('status = ?');
      whereArgs.add(status.name);
    }

    if (!includeExpired) {
      where.add('(expires_at IS NULL OR expires_at > ?)');
      whereArgs.add(DateTime.now().toIso8601String());
    }

    // Exclude deleted
    where.add('status != ?');
    whereArgs.add(NotificationStatus.deleted.name);

    final results = await _db.query(
      _notificationsTable,
      where: where.join(' AND '),
      whereArgs: whereArgs,
      orderBy: 'created_at DESC',
      limit: limit,
      offset: offset,
    );

    return results.map(_mapRowToNotification).toList();
  }

  /// Get a single notification
  Future<AppNotification?> getNotification(String id) async {
    final results = await _db.query(
      _notificationsTable,
      where: 'id = ?',
      whereArgs: [id],
      limit: 1,
    );

    if (results.isEmpty) return null;
    return _mapRowToNotification(results.first);
  }

  /// Get unread count
  Future<int> getUnreadCount({
    required String userId,
    NotificationCategory? category,
  }) async {
    final where = <String>[
      'user_id = ?',
      'status = ?',
      '(expires_at IS NULL OR expires_at > ?)',
    ];
    final whereArgs = <dynamic>[
      userId,
      NotificationStatus.unread.name,
      DateTime.now().toIso8601String(),
    ];

    if (category != null) {
      where.add('category = ?');
      whereArgs.add(category.name);
    }

    final result = await _db.rawQuery(
      'SELECT COUNT(*) as count FROM $_notificationsTable WHERE ${where.join(' AND ')}',
      whereArgs,
    );

    return Sqflite.firstIntValue(result) ?? 0;
  }

  /// Get unread count by category
  Future<Map<NotificationCategory, int>> getUnreadCountByCategory({
    required String userId,
  }) async {
    final result = await _db.rawQuery(
      '''
      SELECT category, COUNT(*) as count
      FROM $_notificationsTable
      WHERE user_id = ?
        AND status = ?
        AND (expires_at IS NULL OR expires_at > ?)
      GROUP BY category
      ''',
      [
        userId,
        NotificationStatus.unread.name,
        DateTime.now().toIso8601String(),
      ],
    );

    final counts = <NotificationCategory, int>{};
    for (final row in result) {
      final category =
          NotificationCategoryExtension.fromString(row['category'] as String?);
      if (category != null) {
        counts[category] = row['count'] as int;
      }
    }

    return counts;
  }

  /// Update notification status
  Future<void> updateStatus(String id, NotificationStatus status) async {
    final updates = <String, dynamic>{
      'status': status.name,
      'updated_at': DateTime.now().toIso8601String(),
      'synced': 0, // Mark as unsynced
    };

    if (status == NotificationStatus.read) {
      updates['read_at'] = DateTime.now().toIso8601String();
    }

    await _db.update(
      _notificationsTable,
      updates,
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  /// Mark all as read
  Future<int> markAllAsRead({
    required String userId,
    NotificationCategory? category,
  }) async {
    final where = <String>['user_id = ?', 'status = ?'];
    final whereArgs = <dynamic>[userId, NotificationStatus.unread.name];

    if (category != null) {
      where.add('category = ?');
      whereArgs.add(category.name);
    }

    return _db.update(
      _notificationsTable,
      {
        'status': NotificationStatus.read.name,
        'read_at': DateTime.now().toIso8601String(),
        'updated_at': DateTime.now().toIso8601String(),
        'synced': 0,
      },
      where: where.join(' AND '),
      whereArgs: whereArgs,
    );
  }

  /// Snooze a notification
  Future<void> snoozeNotification(String id, DateTime until) async {
    await _db.update(
      _notificationsTable,
      {
        'status': NotificationStatus.snoozed.name,
        'snoozed_until': until.toIso8601String(),
        'updated_at': DateTime.now().toIso8601String(),
        'synced': 0,
      },
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  /// Delete a notification (soft delete)
  Future<void> deleteNotification(String id) async {
    await _db.update(
      _notificationsTable,
      {
        'status': NotificationStatus.deleted.name,
        'updated_at': DateTime.now().toIso8601String(),
        'synced': 0,
      },
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  /// Hard delete old notifications
  Future<int> purgeOldNotifications({int daysOld = 30}) async {
    final cutoff =
        DateTime.now().subtract(Duration(days: daysOld)).toIso8601String();

    return _db.delete(
      _notificationsTable,
      where: 'created_at < ? AND status = ?',
      whereArgs: [cutoff, NotificationStatus.deleted.name],
    );
  }

  /// Get unsynced notifications
  Future<List<AppNotification>> getUnsyncedNotifications({
    required String userId,
  }) async {
    final results = await _db.query(
      _notificationsTable,
      where: 'user_id = ? AND synced = 0',
      whereArgs: [userId],
    );

    return results.map(_mapRowToNotification).toList();
  }

  /// Mark notifications as synced
  Future<void> markAsSynced(List<String> ids) async {
    if (ids.isEmpty) return;

    final placeholders = List.filled(ids.length, '?').join(',');
    await _db.rawUpdate(
      'UPDATE $_notificationsTable SET synced = 1 WHERE id IN ($placeholders)',
      ids,
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Settings
  // ─────────────────────────────────────────────────────────────────────────────

  /// Save notification settings
  Future<void> saveSettings({
    required String userId,
    required NotificationSettingsModel settings,
  }) async {
    await _db.insert(
      _settingsTable,
      {
        'id': 'settings_$userId',
        'user_id': userId,
        'settings_json': jsonEncode(settings.toJson()),
        'updated_at': DateTime.now().toIso8601String(),
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  /// Get notification settings
  Future<NotificationSettingsModel?> getSettings({
    required String userId,
  }) async {
    final results = await _db.query(
      _settingsTable,
      where: 'user_id = ?',
      whereArgs: [userId],
      limit: 1,
    );

    if (results.isEmpty) return null;

    final settingsJson = results.first['settings_json'] as String;
    return NotificationSettingsModel.fromJson(
      jsonDecode(settingsJson) as Map<String, dynamic>,
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Helpers
  // ─────────────────────────────────────────────────────────────────────────────

  AppNotification _mapRowToNotification(Map<String, dynamic> row) {
    return AppNotification.fromJson({
      'id': row['id'],
      'remote_id': row['remote_id'],
      'tenant_id': row['tenant_id'],
      'user_id': row['user_id'],
      'category': row['category'],
      'priority': row['priority'],
      'title': row['title'],
      'title_ar': row['title_ar'],
      'body': row['body'],
      'body_ar': row['body_ar'],
      'summary': row['summary'],
      'summary_ar': row['summary_ar'],
      'status': row['status'],
      'actions': row['actions'] != null
          ? jsonDecode(row['actions'] as String)
          : null,
      'primary_action': row['primary_action'] != null
          ? jsonDecode(row['primary_action'] as String)
          : null,
      'group_id': row['group_id'],
      'group_title': row['group_title'],
      'related_entity_type': row['related_entity_type'],
      'related_entity_id': row['related_entity_id'],
      'image_url': row['image_url'],
      'icon_name': row['icon_name'],
      'data': row['data'] != null ? jsonDecode(row['data'] as String) : null,
      'created_at': row['created_at'],
      'read_at': row['read_at'],
      'expires_at': row['expires_at'],
      'snoozed_until': row['snoozed_until'],
      'synced': row['synced'] == 1,
      'source': row['source'],
    });
  }

  /// Close the database
  Future<void> close() async {
    if (_database != null) {
      await _database!.close();
      _database = null;
      _initialized = false;
    }
  }
}
