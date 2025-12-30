// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Connectivity Module Usage Examples
// أمثلة استخدام وحدة الاتصال
// ═══════════════════════════════════════════════════════════════════════════

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/widgets/offline_banner.dart';
import '../../shared/widgets/connectivity_aware_button.dart';
import 'connectivity_provider.dart';

/// Example app demonstrating connectivity features
/// تطبيق مثال يوضح ميزات الاتصال
class ConnectivityExampleApp extends ConsumerWidget {
  const ConnectivityExampleApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp(
      title: 'Connectivity Example',
      theme: ThemeData(
        primarySwatch: Colors.green,
        fontFamily: 'IBMPlexSansArabic',
      ),
      home: const ConnectivityExampleHome(),
    );
  }
}

/// Example home screen with all connectivity widgets
class ConnectivityExampleHome extends ConsumerStatefulWidget {
  const ConnectivityExampleHome({super.key});

  @override
  ConsumerState<ConnectivityExampleHome> createState() =>
      _ConnectivityExampleHomeState();
}

class _ConnectivityExampleHomeState
    extends ConsumerState<ConnectivityExampleHome> {
  int _syncCount = 0;

  @override
  void initState() {
    super.initState();
    // Listen for connectivity changes
    _setupConnectivityListener();
  }

  void _setupConnectivityListener() {
    // Listen to connectivity changes and auto-sync
    ref.listenManual<EnhancedConnectivityState>(
      enhancedConnectivityStateProvider,
      (previous, next) {
        if (previous?.isOffline == true && next.isOnline) {
          _showSnackBar('متصل بالإنترنت!', Colors.green);
          if (next.hasPendingSync) {
            _performAutoSync();
          }
        } else if (previous?.isOnline == true && next.isOffline) {
          _showSnackBar('انقطع الاتصال', Colors.red);
        } else if (next.isPoorConnection) {
          _showSnackBar('الاتصال ضعيف', Colors.orange);
        }
      },
    );
  }

  void _showSnackBar(String message, Color color) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: color,
          duration: const Duration(seconds: 2),
        ),
      );
    }
  }

  Future<void> _performAutoSync() async {
    await Future.delayed(const Duration(seconds: 1));
    _showSnackBar('تمت المزامنة تلقائياً', Colors.blue);
    ref.read(enhancedConnectivityStateProvider.notifier).clearPendingSync();
  }

  @override
  Widget build(BuildContext context) {
    final connectivity = ref.watch(enhancedConnectivityStateProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Connectivity Examples'),
        actions: [
          // Inline connectivity indicator
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: ConnectivityStatusIndicator(
              size: 32,
              showLabel: false,
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          // Offline banner at the top
          const OfflineBanner(
            showRetryButton: true,
          ),

          // Main content
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _buildStatusCard(connectivity),
                const SizedBox(height: 16),
                _buildButtonExamples(),
                const SizedBox(height: 16),
                _buildAdvancedExamples(),
                const SizedBox(height: 16),
                _buildSyncSection(connectivity),
              ],
            ),
          ),
        ],
      ),

      // Connectivity-aware FAB
      floatingActionButton: ConnectivityAwareFAB(
        onPressed: () => _uploadData(),
        requiresOnline: true,
        tooltip: 'Upload data',
        child: const Icon(Icons.cloud_upload),
      ),
    );
  }

  /// Status card showing current connectivity state
  Widget _buildStatusCard(EnhancedConnectivityState connectivity) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                ConnectivityStatusIndicator(size: 40),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'حالة الاتصال',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      Text(
                        connectivity.status.displayMessage,
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const Divider(height: 24),
            _buildStatusRow('متصل', connectivity.isOnline),
            _buildStatusRow('ضعيف', connectivity.isPoorConnection),
            _buildStatusRow('إعادة الاتصال', connectivity.isReconnecting),
            _buildStatusRow('غير متصل', connectivity.isOffline),
            if (connectivity.lastOnlineTime != null) ...[
              const Divider(height: 24),
              Text(
                'آخر اتصال: ${_formatTime(connectivity.lastOnlineTime!)}',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatusRow(String label, bool value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Icon(
            value ? Icons.check_circle : Icons.cancel,
            color: value ? Colors.green : Colors.grey,
            size: 20,
          ),
        ],
      ),
    );
  }

  /// Button examples section
  Widget _buildButtonExamples() {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'أمثلة الأزرار',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 16),

            // Elevated button (requires online)
            SizedBox(
              width: double.infinity,
              child: ConnectivityAwareButton.elevated(
                onPressed: () => _showSnackBar('تم الرفع!', Colors.green),
                requiresOnline: true,
                icon: const Icon(Icons.cloud_upload),
                showConnectivityIndicator: true,
                child: const Text('رفع البيانات (يتطلب اتصال)'),
              ),
            ),
            const SizedBox(height: 8),

            // Text button (works offline)
            SizedBox(
              width: double.infinity,
              child: ConnectivityAwareButton.text(
                onPressed: () => _showSnackBar('عرض محلي', Colors.blue),
                requiresOnline: false,
                icon: const Icon(Icons.folder),
                child: const Text('عرض البيانات المحلية'),
              ),
            ),
            const SizedBox(height: 8),

            // Outlined button (allows poor connection)
            SizedBox(
              width: double.infinity,
              child: ConnectivityAwareButton.outlined(
                onPressed: () => _showSnackBar('تحديث', Colors.orange),
                requiresOnline: true,
                allowPoorConnection: true,
                icon: const Icon(Icons.refresh),
                child: const Text('تحديث (يسمح بالاتصال الضعيف)'),
              ),
            ),
            const SizedBox(height: 8),

            // Icon buttons row
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ConnectivityAwareIconButton(
                  icon: const Icon(Icons.share),
                  onPressed: () => _showSnackBar('مشاركة', Colors.blue),
                  requiresOnline: true,
                  tooltip: 'مشاركة',
                ),
                ConnectivityAwareIconButton(
                  icon: const Icon(Icons.download),
                  onPressed: () => _showSnackBar('تنزيل', Colors.green),
                  requiresOnline: true,
                  tooltip: 'تنزيل',
                ),
                ConnectivityAwareIconButton(
                  icon: const Icon(Icons.save),
                  onPressed: () => _showSnackBar('حفظ', Colors.blue),
                  requiresOnline: false,
                  tooltip: 'حفظ محلياً',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// Advanced examples
  Widget _buildAdvancedExamples() {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'أمثلة متقدمة',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 16),

            // Action button with status
            SizedBox(
              width: double.infinity,
              child: ConnectivityActionButton(
                label: 'إرسال',
                icon: Icons.send,
                onPressed: () => _submitForm(),
                showStatus: true,
              ),
            ),
            const SizedBox(height: 8),

            // Manual connectivity check
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => _checkConnectivity(),
                icon: const Icon(Icons.network_check),
                label: const Text('فحص الاتصال'),
              ),
            ),
            const SizedBox(height: 8),

            // Manual reconnect
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () => _reconnect(),
                icon: const Icon(Icons.refresh),
                label: const Text('إعادة الاتصال'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Sync section
  Widget _buildSyncSection(EnhancedConnectivityState connectivity) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'إدارة المزامنة',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('عناصر في الانتظار:'),
                Text(
                  '${connectivity.pendingSyncCount}',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 18,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _addToSync(),
                    icon: const Icon(Icons.add),
                    label: const Text('إضافة'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ConnectivityAwareButton.elevated(
                    onPressed: connectivity.hasPendingSync ? () => _sync() : null,
                    requiresOnline: true,
                    icon: const Icon(Icons.sync),
                    child: const Text('مزامنة'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // Action methods

  Future<void> _uploadData() async {
    _showSnackBar('جاري الرفع...', Colors.blue);
    await Future.delayed(const Duration(seconds: 1));
    _showSnackBar('تم الرفع بنجاح!', Colors.green);
  }

  Future<void> _submitForm() async {
    _showSnackBar('جاري الإرسال...', Colors.blue);
    await Future.delayed(const Duration(seconds: 1));
    _showSnackBar('تم الإرسال!', Colors.green);
  }

  Future<void> _checkConnectivity() async {
    _showSnackBar('جاري الفحص...', Colors.blue);
    await ref.read(enhancedConnectivityStateProvider.notifier).checkNow();
    _showSnackBar('تم الفحص', Colors.green);
  }

  Future<void> _reconnect() async {
    _showSnackBar('جاري إعادة الاتصال...', Colors.blue);
    final success =
        await ref.read(enhancedConnectivityStateProvider.notifier).reconnect();
    _showSnackBar(
      success ? 'تم إعادة الاتصال!' : 'فشلت إعادة الاتصال',
      success ? Colors.green : Colors.red,
    );
  }

  void _addToSync() {
    setState(() => _syncCount++);
    ref.read(enhancedConnectivityStateProvider.notifier).addPendingSync(1);
    _showSnackBar('تمت الإضافة للمزامنة', Colors.blue);
  }

  Future<void> _sync() async {
    _showSnackBar('جاري المزامنة...', Colors.blue);
    await Future.delayed(const Duration(seconds: 2));
    ref.read(enhancedConnectivityStateProvider.notifier).clearPendingSync();
    _showSnackBar('تمت المزامنة!', Colors.green);
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final diff = now.difference(time);

    if (diff.inSeconds < 60) {
      return 'الآن';
    } else if (diff.inMinutes < 60) {
      return 'منذ ${diff.inMinutes} دقيقة';
    } else if (diff.inHours < 24) {
      return 'منذ ${diff.inHours} ساعة';
    } else {
      return 'منذ ${diff.inDays} يوم';
    }
  }
}

/// Example: Conditional widget based on connectivity
/// مثال: عنصر واجهة مشروط بناءً على الاتصال
class ConditionalConnectivityExample extends ConsumerWidget {
  const ConditionalConnectivityExample({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isOnline = ref.watch(isOnlineProvider);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            if (isOnline)
              const Text('محتوى متاح عند الاتصال فقط')
            else
              const Text('محتوى متاح دون اتصال'),

            const Divider(height: 24),

            // Different UI based on connectivity
            isOnline
                ? ElevatedButton(
                    onPressed: () {},
                    child: const Text('تحميل من الإنترنت'),
                  )
                : ElevatedButton(
                    onPressed: () {},
                    child: const Text('عرض من الذاكرة المحلية'),
                  ),
          ],
        ),
      ),
    );
  }
}

/// Example: Full screen with overlay
/// مثال: شاشة كاملة مع طبقة
class FullScreenOverlayExample extends ConsumerWidget {
  const FullScreenOverlayExample({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Overlay Example'),
      ),
      body: OfflineOverlay(
        showOverlay: true,
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text('محتوى التطبيق'),
              const SizedBox(height: 16),
              ConnectivityAwareButton.elevated(
                onPressed: () {},
                requiresOnline: true,
                child: const Text('إجراء يتطلب اتصال'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
