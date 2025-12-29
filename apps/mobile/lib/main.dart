import 'dart:async';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';
import 'core/config/config.dart';
import 'core/sync/sync_engine.dart';
import 'core/sync/background_sync_task.dart';
import 'core/storage/database.dart';
import 'core/config/env_config.dart';
import 'core/notifications/firebase_messaging_service.dart';

void main() async {
  // Catch all errors to prevent crashes
  await runZonedGuarded(() async {
    WidgetsFlutterBinding.ensureInitialized();

    // Load environment configuration first (non-critical)
    try {
      await EnvConfig.load();
    } catch (e) {
      debugPrint('⚠️ EnvConfig load failed: $e');
      // Continue anyway - defaults will be used
    }

    // Initialize Firebase (for push notifications)
    if (AppConfig.enablePushNotifications) {
      try {
        await Firebase.initializeApp();
        debugPrint('✅ Firebase initialized');
      } catch (e) {
        debugPrint('⚠️ Firebase initialization failed (non-critical): $e');
        // Continue anyway - app can work without push notifications
      }
    }

    // Initialize database
    late AppDatabase database;
    try {
      database = AppDatabase();
    } catch (e) {
      debugPrint('❌ Database initialization failed: $e');
      rethrow;
    }

    // Initialize sync engine
    late SyncEngine syncEngine;
    try {
      syncEngine = SyncEngine(database: database);
    } catch (e) {
      debugPrint('❌ SyncEngine initialization failed: $e');
      rethrow;
    }

    // Initialize background sync with Workmanager (non-critical)
    try {
      await BackgroundSyncManager.initialize();
      await BackgroundSyncManager.registerPeriodicSync();
      debugPrint('✅ Background sync initialized');
    } catch (e) {
      // Non-critical - app can work without background sync
      debugPrint('⚠️ Background sync init failed (non-critical): $e');
    }

    // Initialize Firebase Messaging Service (non-critical)
    if (AppConfig.enablePushNotifications) {
      try {
        await FirebaseMessagingService.instance.initialize();
        debugPrint('✅ Firebase Messaging Service initialized');
      } catch (e) {
        debugPrint('⚠️ Firebase Messaging init failed (non-critical): $e');
      }
    }

    // Run the app
    runApp(
      ProviderScope(
        overrides: [
          databaseProvider.overrideWithValue(database),
          syncEngineProvider.overrideWithValue(syncEngine),
        ],
        child: const SahoolFieldApp(),
      ),
    );

    // Start foreground sync when app is active (non-blocking)
    try {
      syncEngine.startPeriodic();
    } catch (e) {
      debugPrint('⚠️ Foreground sync start failed: $e');
    }
  }, (error, stackTrace) {
    // Global error handler
    debugPrint('❌ Uncaught error: $error');
    debugPrint('Stack trace: $stackTrace');

    // In production, send to crash reporting service
    if (kReleaseMode) {
      // TODO: Send to crash reporting service
    }
  });
}

// Global providers
final databaseProvider = Provider<AppDatabase>((ref) {
  throw UnimplementedError('Database not initialized');
});

final syncEngineProvider = Provider<SyncEngine>((ref) {
  throw UnimplementedError('SyncEngine not initialized');
});
