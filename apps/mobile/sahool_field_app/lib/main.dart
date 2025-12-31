import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';
import 'core/sync/sync_engine.dart';
import 'core/sync/background_sync_task.dart';
import 'core/storage/database.dart';
import 'core/config/env_config.dart';
import 'core/security/device_security_service.dart';
import 'core/security/security_config.dart';
import 'core/security/screen_security_service.dart';

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

    // Initialize security configuration
    final securityConfig = const SecurityConfig(level: SecurityLevel.medium);

    // CRITICAL: Check device security before initializing app
    try {
      final deviceSecurityService = DeviceSecurityService(config: securityConfig);
      final securityResult = await deviceSecurityService.checkDeviceSecurity(
        skipInDebugMode: securityConfig.allowSecurityBypassInDebug,
      );

      debugPrint('🔐 Device Security Check: ${securityResult.isSecure ? "PASS" : "FAIL"}');

      // Handle security threats based on action
      if (securityResult.recommendedAction == SecurityAction.block) {
        debugPrint('❌ Device security check BLOCKED app launch');
        debugPrint('   Threats: ${securityResult.threats.map((t) => t.type).join(", ")}');

        // Show security warning screen and block app
        runApp(
          MaterialApp(
            home: SecurityBlockedScreen(
              result: securityResult,
              locale: const Locale('ar'),
            ),
            debugShowCheckedModeBanner: false,
          ),
        );
        return; // Stop app initialization
      } else if (securityResult.recommendedAction == SecurityAction.warn) {
        debugPrint('⚠️ Device security check WARNING');
        debugPrint('   Threats: ${securityResult.threats.map((t) => t.type).join(", ")}');
        // Continue but show warning (will be shown in app)
      }
    } catch (e) {
      debugPrint('⚠️ Device security check error (non-critical): $e');
      // Continue anyway - security check failure shouldn't block app in medium/low security
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

    // Initialize screen security service (non-critical)
    try {
      final screenSecurity = ScreenSecurityService();
      await screenSecurity.initialize();
      debugPrint('✅ Screen security initialized');
    } catch (e) {
      // Non-critical - app can work without screen security
      debugPrint('⚠️ Screen security init failed (non-critical): $e');
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

// ═══════════════════════════════════════════════════════════════════════════
// Security Blocked Screen
// ═══════════════════════════════════════════════════════════════════════════

/// Screen shown when device security check fails
/// شاشة تظهر عند فشل فحص أمان الجهاز
class SecurityBlockedScreen extends StatelessWidget {
  final DeviceSecurityResult result;
  final Locale locale;

  const SecurityBlockedScreen({
    super.key,
    required this.result,
    required this.locale,
  });

  @override
  Widget build(BuildContext context) {
    final isArabic = locale.languageCode == 'ar';

    return Directionality(
      textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
      child: Scaffold(
        backgroundColor: const Color(0xFFF5F5F5),
        body: SafeArea(
          child: Center(
            child: Padding(
              padding: const EdgeInsets.all(32.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Security Icon
                  Container(
                    width: 120,
                    height: 120,
                    decoration: BoxDecoration(
                      color: Colors.red.shade50,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.security_outlined,
                      size: 64,
                      color: Colors.red.shade700,
                    ),
                  ),
                  const SizedBox(height: 32),

                  // Title
                  Text(
                    isArabic ? 'تحذير أمني' : 'Security Warning',
                    style: TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: Colors.red.shade700,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 16),

                  // Message
                  Text(
                    isArabic ? result.messageAr : result.messageEn,
                    style: const TextStyle(
                      fontSize: 18,
                      color: Colors.black87,
                      height: 1.5,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 32),

                  // Threat Details
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.red.shade200),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          isArabic ? 'المخاطر المكتشفة:' : 'Detected Threats:',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.red.shade700,
                          ),
                        ),
                        const SizedBox(height: 12),
                        ...result.threats.map((threat) => Padding(
                              padding: const EdgeInsets.only(bottom: 8.0),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Icon(
                                    Icons.warning_rounded,
                                    size: 20,
                                    color: Colors.orange.shade700,
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      isArabic ? threat.messageAr : threat.messageEn,
                                      style: const TextStyle(
                                        fontSize: 14,
                                        color: Colors.black87,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            )),
                      ],
                    ),
                  ),
                  const SizedBox(height: 32),

                  // Info Text
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.blue.shade50,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          Icons.info_outline,
                          color: Colors.blue.shade700,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            isArabic
                                ? 'لا يمكن استخدام التطبيق على هذا الجهاز لأسباب أمنية. الرجاء استخدام جهاز غير معدل أو محمي.'
                                : 'This app cannot run on this device for security reasons. Please use an unmodified or non-rooted device.',
                            style: TextStyle(
                              fontSize: 13,
                              color: Colors.blue.shade900,
                              height: 1.4,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Contact Support (optional)
                  if (kDebugMode)
                    TextButton(
                      onPressed: () {
                        // For development: show more details
                        showDialog(
                          context: context,
                          builder: (context) => AlertDialog(
                            title: Text(isArabic ? 'تفاصيل التطوير' : 'Debug Details'),
                            content: SingleChildScrollView(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Text('Debug Mode: $kDebugMode'),
                                  Text('Release Mode: $kReleaseMode'),
                                  const SizedBox(height: 8),
                                  const Text('Threats:'),
                                  ...result.threats.map((t) => Text(
                                        '- ${t.type}: ${t.severity}',
                                        style: const TextStyle(fontSize: 12),
                                      )),
                                ],
                              ),
                            ),
                            actions: [
                              TextButton(
                                onPressed: () => Navigator.pop(context),
                                child: Text(isArabic ? 'إغلاق' : 'Close'),
                              ),
                            ],
                          ),
                        );
                      },
                      child: Text(
                        isArabic ? 'تفاصيل التطوير' : 'Debug Details',
                        style: const TextStyle(fontSize: 14),
                      ),
                    ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
