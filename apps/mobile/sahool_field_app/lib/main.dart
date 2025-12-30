import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sentry_flutter/sentry_flutter.dart';
import 'app.dart';
import 'core/sync/sync_engine.dart';
import 'core/sync/background_sync_task.dart';
import 'core/storage/database.dart';
import 'core/config/env_config.dart';
import 'core/monitoring/sentry_service.dart';

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

    // Initialize Sentry for error tracking and performance monitoring
    try {
      await SentryService.initialize();
      if (SentryService.isEnabled) {
        SentryService.addBreadcrumb(
          'App initialization started',
          category: 'app.lifecycle',
        );
      }
    } catch (e) {
      debugPrint('⚠️ Sentry initialization failed (non-critical): $e');
      // Continue anyway - app can work without Sentry
    }

    // Initialize database
    late AppDatabase database;
    try {
      SentryService.addBreadcrumb('Initializing database', category: 'db');
      database = AppDatabase();
      SentryService.addBreadcrumb('Database initialized', category: 'db');
    } catch (e, stackTrace) {
      debugPrint('❌ Database initialization failed: $e');
      SentryService.captureException(e, stackTrace: stackTrace);
      rethrow;
    }

    // Initialize sync engine
    late SyncEngine syncEngine;
    try {
      SentryService.addBreadcrumb('Initializing sync engine', category: 'sync');
      syncEngine = SyncEngine(database: database);
      SentryService.addBreadcrumb('Sync engine initialized', category: 'sync');
    } catch (e, stackTrace) {
      debugPrint('❌ SyncEngine initialization failed: $e');
      SentryService.captureException(e, stackTrace: stackTrace);
      rethrow;
    }

    // Initialize background sync with Workmanager (non-critical)
    try {
      SentryService.addBreadcrumb('Initializing background sync', category: 'sync');
      await BackgroundSyncManager.initialize();
      await BackgroundSyncManager.registerPeriodicSync();
      SentryService.addBreadcrumb('Background sync initialized', category: 'sync');
      debugPrint('✅ Background sync initialized');
    } catch (e, stackTrace) {
      // Non-critical - app can work without background sync
      debugPrint('⚠️ Background sync init failed (non-critical): $e');
      SentryService.captureException(
        e,
        stackTrace: stackTrace,
      );
    }

    // Run the app with Sentry error boundary
    SentryService.addBreadcrumb('Starting app', category: 'app.lifecycle');
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
      SentryService.addBreadcrumb('Starting foreground sync', category: 'sync');
      syncEngine.startPeriodic();
    } catch (e, stackTrace) {
      debugPrint('⚠️ Foreground sync start failed: $e');
      SentryService.captureException(e, stackTrace: stackTrace);
    }
  }, (error, stackTrace) {
    // Global error handler
    debugPrint('❌ Uncaught error: $error');
    debugPrint('Stack trace: $stackTrace');

    // Send to Sentry crash reporting service
    SentryService.captureException(
      error,
      stackTrace: stackTrace,
    );
  });
}

// Global providers
final databaseProvider = Provider<AppDatabase>((ref) {
  throw UnimplementedError('Database not initialized');
});

final syncEngineProvider = Provider<SyncEngine>((ref) {
  throw UnimplementedError('SyncEngine not initialized');
});
