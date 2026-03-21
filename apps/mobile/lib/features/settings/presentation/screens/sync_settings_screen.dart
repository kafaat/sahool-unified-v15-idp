import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/config/theme.dart';
import '../../state/settings_providers.dart';
import '../widgets/widgets.dart';

/// Sync Settings Screen
/// شاشة إعدادات المزامنة
class SyncSettingsScreen extends ConsumerWidget {
  const SyncSettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(appSettingsProvider);
    final syncStatus = ref.watch(syncStatusProvider);
    final storageInfo = ref.watch(storageInfoProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: isDark ? Colors.black : Colors.grey[100],
        appBar: AppBar(
          backgroundColor: isDark ? Colors.grey[900] : Colors.white,
          elevation: 0,
          title: Text(
            'المزامنة والتخزين',
            style: TextStyle(
              color: isDark ? Colors.white : Colors.black87,
              fontWeight: FontWeight.bold,
            ),
          ),
          centerTitle: true,
          leading: IconButton(
            icon: const Icon(Icons.arrow_forward_ios),
            color: isDark ? Colors.white : Colors.black87,
            onPressed: () => Navigator.pop(context),
          ),
        ),
        body: ListView(
          padding: const EdgeInsets.only(bottom: 32),
          children: [
            // Sync Status Card
            _SyncStatusCard(
              syncStatus: syncStatus,
              onSyncNow: () {
                ref.read(syncStatusProvider.notifier).triggerSync();
              },
            ),

            // Sync Settings Section
            SettingsSection(
              title: 'Sync Settings',
              titleAr: 'إعدادات المزامنة',
              icon: Icons.sync_outlined,
              showDividers: true,
              children: [
                SwitchSettingsTile(
                  title: 'Auto Sync',
                  titleAr: 'المزامنة التلقائية',
                  icon: Icons.autorenew_rounded,
                  value: settings.autoSyncEnabled,
                  dynamicSubtitle: (v) => v
                      ? 'مزامنة تلقائية كل ${settings.syncIntervalMinutes} دقيقة'
                      : 'المزامنة اليدوية فقط',
                  onChanged: (value) {
                    ref.read(appSettingsProvider.notifier).setAutoSyncEnabled(value);
                  },
                ),
                DropdownSettingsTile<int>(
                  title: 'Sync Interval',
                  titleAr: 'فترة المزامنة',
                  icon: Icons.timer_rounded,
                  value: settings.syncIntervalMinutes,
                  enabled: settings.autoSyncEnabled,
                  options: const [
                    DropdownOption(value: 5, label: '5 minutes', labelAr: '5 دقائق'),
                    DropdownOption(value: 15, label: '15 minutes', labelAr: '15 دقيقة'),
                    DropdownOption(value: 30, label: '30 minutes', labelAr: '30 دقيقة'),
                    DropdownOption(value: 60, label: '1 hour', labelAr: 'ساعة'),
                    DropdownOption(value: 120, label: '2 hours', labelAr: 'ساعتان'),
                  ],
                  onChanged: (value) {
                    if (value != null) {
                      ref.read(appSettingsProvider.notifier).setSyncInterval(value);
                    }
                  },
                ),
                SwitchSettingsTile(
                  title: 'WiFi Only',
                  titleAr: 'واي فاي فقط',
                  icon: Icons.wifi_rounded,
                  iconColor: SahoolTheme.info,
                  value: settings.wifiOnlySyncEnabled,
                  subtitle: 'مزامنة البيانات الكبيرة عبر واي فاي فقط',
                  onChanged: (value) {
                    ref.read(appSettingsProvider.notifier).setWifiOnlySyncEnabled(value);
                  },
                ),
                SwitchSettingsTile(
                  title: 'Background Sync',
                  titleAr: 'المزامنة في الخلفية',
                  icon: Icons.sync_disabled_rounded,
                  value: settings.backgroundSyncEnabled,
                  subtitle: 'المزامنة حتى عند إغلاق التطبيق',
                  onChanged: (value) {
                    ref.read(appSettingsProvider.notifier).setBackgroundSyncEnabled(value);
                  },
                ),
              ],
            ),

            // Pending Operations
            if (syncStatus.pendingOperations > 0)
              SettingsSection(
                title: 'Pending Operations',
                titleAr: 'العمليات المعلقة',
                icon: Icons.pending_outlined,
                children: [
                  _PendingOperationsTile(count: syncStatus.pendingOperations),
                ],
              ),

            // Storage Section
            SettingsSection(
              title: 'Storage',
              titleAr: 'التخزين',
              icon: Icons.storage_outlined,
              children: [
                _StorageOverviewTile(storageInfo: storageInfo),
              ],
            ),

            // Storage Breakdown
            SettingsSection(
              title: 'Storage Breakdown',
              titleAr: 'تفاصيل التخزين',
              icon: Icons.pie_chart_outline,
              showDividers: true,
              children: [
                _StorageItemTile(
                  label: 'الخرائط',
                  size: storageInfo.mapsFormatted,
                  color: Colors.blue,
                  icon: Icons.map_rounded,
                ),
                _StorageItemTile(
                  label: 'الصور',
                  size: storageInfo.imagesFormatted,
                  color: Colors.orange,
                  icon: Icons.image_rounded,
                ),
                _StorageItemTile(
                  label: 'البيانات',
                  size: storageInfo.dataFormatted,
                  color: SahoolTheme.success,
                  icon: Icons.data_usage_rounded,
                ),
                _StorageItemTile(
                  label: 'ذاكرة التخزين المؤقت',
                  size: storageInfo.cacheFormatted,
                  color: Colors.grey,
                  icon: Icons.cached_rounded,
                ),
              ],
            ),

            // Offline Maps Section
            SettingsSection(
              title: 'Offline Maps',
              titleAr: 'الخرائط دون اتصال',
              icon: Icons.map_outlined,
              showDividers: true,
              children: [
                SwitchSettingsTile(
                  title: 'Offline Maps',
                  titleAr: 'تمكين الخرائط دون اتصال',
                  icon: Icons.offline_pin_rounded,
                  value: settings.offlineMapsEnabled,
                  onChanged: (value) {
                    ref.read(appSettingsProvider.notifier).setOfflineMapsEnabled(value);
                  },
                ),
                const _OfflineMapTile(
                  regionName: 'صنعاء وضواحيها',
                  size: '150 MB',
                  isDownloaded: true,
                ),
                const _OfflineMapTile(
                  regionName: 'إب وتعز',
                  size: '120 MB',
                  isDownloaded: false,
                ),
                SettingsTile(
                  title: 'Download New Region',
                  titleAr: 'تنزيل منطقة جديدة',
                  icon: Icons.download_rounded,
                  iconColor: SahoolTheme.primary,
                  onTap: () => _showDownloadRegionDialog(context),
                ),
              ],
            ),

            // Actions Section
            SettingsSection(
              title: 'Actions',
              titleAr: 'إجراءات',
              showDividers: true,
              children: [
                SettingsTile(
                  title: 'Clear Cache',
                  titleAr: 'مسح ذاكرة التخزين المؤقت',
                  icon: Icons.cleaning_services_rounded,
                  iconColor: SahoolTheme.warning,
                  subtitle: 'يمكن تحرير ${storageInfo.cacheFormatted}',
                  onTap: () => _showClearCacheDialog(context, ref),
                ),
                SettingsTile(
                  title: 'Clear Offline Data',
                  titleAr: 'مسح البيانات دون اتصال',
                  icon: Icons.delete_outline_rounded,
                  iconColor: SahoolTheme.error,
                  subtitle: 'حذف جميع البيانات المحفوظة محلياً',
                  onTap: () => _showClearOfflineDataDialog(context, ref),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _showDownloadRegionDialog(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => DecoratedBox(
        decoration: BoxDecoration(
          color: Theme.of(context).brightness == Brightness.dark
              ? Colors.grey[900]
              : Colors.white,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              margin: const EdgeInsets.only(top: 12),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[400],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text(
                'تنزيل منطقة جديدة',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            ListTile(
              leading: const Icon(Icons.location_on),
              title: const Text('الحديدة'),
              subtitle: const Text('~80 MB'),
              onTap: () {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('بدء تنزيل منطقة الحديدة...')),
                );
              },
            ),
            ListTile(
              leading: const Icon(Icons.location_on),
              title: const Text('عدن'),
              subtitle: const Text('~90 MB'),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: const Icon(Icons.location_on),
              title: const Text('مأرب'),
              subtitle: const Text('~60 MB'),
              onTap: () => Navigator.pop(context),
            ),
            const SizedBox(height: 8),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: OutlinedButton.icon(
                onPressed: () => Navigator.pop(context),
                icon: const Icon(Icons.map),
                label: const Text('تحديد على الخريطة'),
              ),
            ),
            SizedBox(height: MediaQuery.of(context).padding.bottom + 16),
          ],
        ),
      ),
    );
  }

  void _showClearCacheDialog(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('مسح ذاكرة التخزين المؤقت'),
        content: const Text(
          'سيتم مسح الملفات المؤقتة والصور المخزنة مؤقتاً.\n\n'
          'قد يؤدي هذا إلى بطء التحميل مؤقتاً حتى يتم إعادة تخزين البيانات.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context);
              await ref.read(storageInfoProvider.notifier).clearCache();
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('تم مسح ذاكرة التخزين المؤقت'),
                    backgroundColor: SahoolTheme.success,
                  ),
                );
              }
            },
            child: const Text('مسح'),
          ),
        ],
      ),
    );
  }

  void _showClearOfflineDataDialog(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.warning_rounded, color: SahoolTheme.warning),
            SizedBox(width: 8),
            Text('مسح البيانات'),
          ],
        ),
        content: const Text(
          'سيتم حذف جميع البيانات المحفوظة محلياً بما في ذلك:\n'
          '- الخرائط دون اتصال\n'
          '- الصور المخزنة\n'
          '- بيانات الحقول المحلية\n\n'
          'ستحتاج إلى إعادة مزامنة البيانات من الخادم.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('تم مسح البيانات المحلية'),
                  backgroundColor: SahoolTheme.success,
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: SahoolTheme.error,
            ),
            child: const Text('مسح'),
          ),
        ],
      ),
    );
  }
}

/// Sync Status Card
class _SyncStatusCard extends StatelessWidget {
  final SyncStatus syncStatus;
  final VoidCallback onSyncNow;

  const _SyncStatusCard({
    required this.syncStatus,
    required this.onSyncNow,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: isDark ? Colors.grey[900] : Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: isDark ? 0.3 : 0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  color: (syncStatus.isSyncing
                          ? SahoolTheme.warning
                          : SahoolTheme.success)
                      .withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                ),
                child: syncStatus.isSyncing
                    ? const Padding(
                        padding: EdgeInsets.all(14),
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(
                        Icons.check_circle_rounded,
                        color: SahoolTheme.success,
                        size: 32,
                      ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      syncStatus.isSyncing ? 'جاري المزامنة...' : 'متزامن',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: syncStatus.isSyncing
                            ? SahoolTheme.warning
                            : SahoolTheme.success,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'آخر مزامنة: ${syncStatus.lastSyncDisplayAr}',
                      style: TextStyle(
                        fontSize: 14,
                        color: isDark ? Colors.grey[400] : Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: syncStatus.isSyncing ? null : onSyncNow,
              icon: const Icon(Icons.sync),
              label: Text(syncStatus.isSyncing ? 'جاري المزامنة...' : 'مزامنة الآن'),
            ),
          ),
        ],
      ),
    );
  }
}

/// Pending Operations Tile
class _PendingOperationsTile extends StatelessWidget {
  final int count;

  const _PendingOperationsTile({required this.count});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: SahoolTheme.warning.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: SahoolTheme.warning.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.pending_actions, color: SahoolTheme.warning),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              'لديك $count عمليات في انتظار المزامنة',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
        ],
      ),
    );
  }
}

/// Storage Overview Tile
class _StorageOverviewTile extends StatelessWidget {
  final StorageInfo storageInfo;

  const _StorageOverviewTile({required this.storageInfo});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'المستخدم: ${storageInfo.usedFormatted}',
                style: const TextStyle(fontWeight: FontWeight.w500),
              ),
              Text(
                'المتاح: ${storageInfo.availableFormatted}',
                style: TextStyle(color: Colors.grey[600]),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: LinearProgressIndicator(
              value: storageInfo.usagePercent,
              backgroundColor: Colors.grey[200],
              valueColor: AlwaysStoppedAnimation<Color>(
                storageInfo.usagePercent > 0.8
                    ? SahoolTheme.error
                    : SahoolTheme.primary,
              ),
              minHeight: 10,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '${(storageInfo.usagePercent * 100).toStringAsFixed(1)}% مستخدم من ${storageInfo.totalFormatted}',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }
}

/// Storage Item Tile
class _StorageItemTile extends StatelessWidget {
  final String label;
  final String size;
  final Color color;
  final IconData icon;

  const _StorageItemTile({
    required this.label,
    required this.size,
    required this.color,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: color.withValues(alpha: isDark ? 0.2 : 0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: color, size: 22),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              label,
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w500,
                color: isDark ? Colors.white : Colors.black87,
              ),
            ),
          ),
          Text(
            size,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

/// Offline Map Tile
class _OfflineMapTile extends StatelessWidget {
  final String regionName;
  final String size;
  final bool isDownloaded;

  const _OfflineMapTile({
    required this.regionName,
    required this.size,
    required this.isDownloaded,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: Colors.blue.withValues(alpha: isDark ? 0.2 : 0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Icon(Icons.map, color: Colors.blue, size: 22),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  regionName,
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w500,
                    color: isDark ? Colors.white : Colors.black87,
                  ),
                ),
                Text(
                  size,
                  style: TextStyle(
                    fontSize: 13,
                    color: isDark ? Colors.grey[400] : Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
          if (isDownloaded)
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.check_circle, color: SahoolTheme.success, size: 20),
                const SizedBox(width: 8),
                IconButton(
                  icon: const Icon(Icons.delete_outline, size: 20),
                  color: SahoolTheme.error,
                  onPressed: () {},
                ),
              ],
            )
          else
            OutlinedButton(
              onPressed: () {},
              child: const Text('تنزيل'),
            ),
        ],
      ),
    );
  }
}
