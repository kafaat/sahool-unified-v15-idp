import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/notification_entities.dart';
import '../providers/notification_provider.dart';
import '../../../../core/routes/app_router.dart';

/// شاشة الإشعارات
class NotificationsScreen extends ConsumerStatefulWidget {
  const NotificationsScreen({super.key});

  @override
  ConsumerState<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends ConsumerState<NotificationsScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(notificationsProvider.notifier).loadNotifications();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(notificationsProvider);
    final filteredNotifications = ref.watch(filteredNotificationsProvider);

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('الإشعارات'),
          backgroundColor: const Color(0xFF367C2B),
          foregroundColor: Colors.white,
          actions: [
            if (state.unreadCount > 0)
              IconButton(
                icon: const Icon(Icons.done_all),
                onPressed: () {
                  ref.read(notificationsProvider.notifier).markAllAsRead();
                },
                tooltip: 'تحديد الكل كمقروء',
              ),
            IconButton(
              icon: const Icon(Icons.settings),
              onPressed: () => _showSettings(context),
              tooltip: 'الإعدادات',
            ),
          ],
        ),
        body: Column(
          children: [
            // فلتر النوع
            _buildTypeFilter(),

            // قائمة الإشعارات
            Expanded(
              child: state.isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : filteredNotifications.isEmpty
                      ? _buildEmptyView()
                      : RefreshIndicator(
                          onRefresh: () async {
                            await ref
                                .read(notificationsProvider.notifier)
                                .loadNotifications();
                          },
                          child: ListView.builder(
                            padding: const EdgeInsets.all(16),
                            itemCount: filteredNotifications.length,
                            itemBuilder: (context, index) {
                              final notification = filteredNotifications[index];
                              return _buildNotificationCard(notification);
                            },
                            // Keys are handled by Dismissible widget with Key(notification.id)
                          ),
                        ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTypeFilter() {
    final currentFilter = ref.watch(notificationFilterProvider);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: [
            _buildFilterChip('الكل', null, currentFilter),
            const SizedBox(width: 8),
            _buildFilterChip('⚠️ تنبيهات', 'alert', currentFilter),
            const SizedBox(width: 8),
            _buildFilterChip('📋 إجراءات', 'action', currentFilter),
            const SizedBox(width: 8),
            _buildFilterChip('🌤️ طقس', 'weather', currentFilter),
            const SizedBox(width: 8),
            _buildFilterChip('🌱 صحة المحصول', 'crop_health', currentFilter),
          ],
        ),
      ),
    );
  }

  Widget _buildFilterChip(String label, String? value, String? current) {
    final isSelected = current == value;
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (_) {
        ref.read(notificationFilterProvider.notifier).state = value;
      },
      selectedColor: const Color(0xFF367C2B).withOpacity(0.2),
      checkmarkColor: const Color(0xFF367C2B),
    );
  }

  Widget _buildNotificationCard(AppNotification notification) {
    return Dismissible(
      key: Key(notification.id),
      direction: DismissDirection.endToStart,
      background: Container(
        alignment: Alignment.centerLeft,
        padding: const EdgeInsets.only(left: 20),
        color: Colors.red,
        child: const Icon(Icons.delete, color: Colors.white),
      ),
      onDismissed: (_) {
        ref.read(notificationsProvider.notifier).deleteNotification(notification.id);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('تم حذف الإشعار')),
        );
      },
      child: Card(
        elevation: notification.isRead ? 1 : 3,
        margin: const EdgeInsets.only(bottom: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: notification.isRead
              ? BorderSide.none
              : const BorderSide(color: Color(0xFF367C2B), width: 2),
        ),
        child: InkWell(
          onTap: () {
            if (!notification.isRead) {
              ref.read(notificationsProvider.notifier).markAsRead(notification.id);
            }
            _showNotificationDetails(notification);
          },
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // أيقونة النوع
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: notification.isRead
                        ? Colors.grey[200]
                        : const Color(0xFF367C2B).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Center(
                    child: Text(
                      notification.typeIcon,
                      style: const TextStyle(fontSize: 24),
                    ),
                  ),
                ),

                const SizedBox(width: 12),

                // المحتوى
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              notification.titleAr,
                              style: TextStyle(
                                fontWeight: notification.isRead
                                    ? FontWeight.normal
                                    : FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                          ),
                          Text(
                            notification.timeAgo,
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey[500],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        notification.bodyAr,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.grey[200],
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          notification.typeLabel,
                          style: TextStyle(
                            fontSize: 11,
                            color: Colors.grey[700],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                // مؤشر غير مقروء
                if (!notification.isRead)
                  Container(
                    width: 10,
                    height: 10,
                    decoration: const BoxDecoration(
                      color: Color(0xFF367C2B),
                      shape: BoxShape.circle,
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyView() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.notifications_off, size: 64, color: Colors.grey),
          SizedBox(height: 16),
          Text(
            'لا توجد إشعارات',
            style: TextStyle(fontSize: 18, color: Colors.grey),
          ),
        ],
      ),
    );
  }

  void _showNotificationDetails(AppNotification notification) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // الرأس
              Row(
                children: [
                  Text(
                    notification.typeIcon,
                    style: const TextStyle(fontSize: 32),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          notification.titleAr,
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        Text(
                          notification.timeAgo,
                          style: TextStyle(color: Colors.grey[600]),
                        ),
                      ],
                    ),
                  ),
                ],
              ),

              const Divider(height: 32),

              // المحتوى
              Text(
                notification.bodyAr,
                style: Theme.of(context).textTheme.bodyLarge,
              ),

              const SizedBox(height: 24),

              // أزرار الإجراء
              if (notification.actionUrl != null)
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () {
                      Navigator.pop(context);
                      _navigateToActionUrl(notification.actionUrl!);
                    },
                    icon: const Icon(Icons.open_in_new),
                    label: const Text('فتح التفاصيل'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF367C2B),
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),

              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  void _showSettings(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const NotificationSettingsScreen(),
      ),
    );
  }

  /// Navigate to the action URL based on its scheme
  /// يقوم بالتنقل إلى عنوان الإجراء بناءً على نوعه
  void _navigateToActionUrl(String actionUrl) {
    try {
      final uri = Uri.tryParse(actionUrl);

      if (uri == null || actionUrl.isEmpty) {
        _showNavigationError('عنوان غير صالح');
        return;
      }

      // Handle different URL schemes
      if (_isInternalRoute(actionUrl)) {
        // Internal route (e.g., /field/123, /tasks, /weather)
        _navigateToInternalRoute(actionUrl);
      } else if (_isExternalUrl(uri)) {
        // External HTTP/HTTPS URL
        _handleExternalUrl(uri);
      } else if (_isSahoolScheme(uri)) {
        // Custom sahool:// scheme (e.g., sahool://field/123)
        _navigateToSahoolScheme(uri);
      } else {
        // Unknown scheme - try as internal route
        _navigateToInternalRoute(actionUrl);
      }
    } catch (e) {
      debugPrint('Error navigating to action URL: $e');
      _showNavigationError('حدث خطأ أثناء التنقل');
    }
  }

  /// Check if the URL is an internal route (starts with /)
  bool _isInternalRoute(String url) {
    return url.startsWith('/');
  }

  /// Check if the URI is an external HTTP/HTTPS URL
  bool _isExternalUrl(Uri uri) {
    return uri.scheme == 'http' || uri.scheme == 'https';
  }

  /// Check if the URI uses the custom sahool:// scheme
  bool _isSahoolScheme(Uri uri) {
    return uri.scheme == 'sahool';
  }

  /// Navigate to an internal route using go_router
  void _navigateToInternalRoute(String route) {
    try {
      // Parse the route to extract path and query parameters
      final uri = Uri.tryParse(route.startsWith('/') ? 'app:/$route' : route);

      if (uri == null) {
        // Fallback to direct navigation
        AppRouter.router.go(route);
        return;
      }

      final path = uri.path;
      final queryParams = uri.queryParameters;

      // Map routes to appropriate screens
      if (path.startsWith('/field/') || path.startsWith('//field/')) {
        // Field details route: /field/:id
        final fieldId = _extractFieldId(path);
        if (fieldId != null) {
          AppRouter.router.go('/field/$fieldId', extra: queryParams);
        } else {
          AppRouter.router.go('/fields');
        }
      } else if (path.contains('/tasks') || path.contains('//tasks')) {
        // Tasks route
        Navigator.pushNamed(context, '/tasks');
      } else if (path.contains('/weather') || path.contains('//weather')) {
        // Weather route
        final fieldId = queryParams['fieldId'];
        Navigator.pushNamed(
          context,
          '/weather',
          arguments: fieldId != null ? {'fieldId': fieldId} : null,
        );
      } else if (path.contains('/crop-health') || path.contains('//crop-health')) {
        // Crop health route
        final fieldId = queryParams['fieldId'] ?? _extractFieldId(path);
        Navigator.pushNamed(
          context,
          '/crop-health',
          arguments: fieldId != null ? {'fieldId': fieldId} : null,
        );
      } else if (path.contains('/map') || path.contains('//map')) {
        // Map route
        final fieldId = queryParams['fieldId'];
        Navigator.pushNamed(
          context,
          '/map',
          arguments: fieldId != null ? {'fieldId': fieldId} : null,
        );
      } else if (path.contains('/alerts') || path.contains('//alerts')) {
        // Alerts route
        AppRouter.router.go('/alerts');
      } else if (path.contains('/advisor') || path.contains('//advisor')) {
        // AI Advisor route
        AppRouter.router.go('/advisor');
      } else if (path.contains('/sync') || path.contains('//sync')) {
        // Sync route
        AppRouter.router.go('/sync');
      } else if (path.contains('/profile') || path.contains('//profile')) {
        // Profile route
        AppRouter.router.go('/profile');
      } else if (path.contains('/scanner') || path.contains('//scanner')) {
        // Scanner route
        AppRouter.router.go('/scanner');
      } else if (path.contains('/scouting') || path.contains('//scouting')) {
        // Scouting route
        AppRouter.router.go('/scouting');
      } else {
        // Default: try to navigate to the route directly
        AppRouter.router.go(route);
      }
    } catch (e) {
      debugPrint('Error navigating to internal route: $e');
      _showNavigationError('تعذر فتح الصفحة المطلوبة');
    }
  }

  /// Extract field ID from a path like /field/123 or //field/123
  String? _extractFieldId(String path) {
    final regex = RegExp(r'/+field/([^/?]+)');
    final match = regex.firstMatch(path);
    return match?.group(1);
  }

  /// Handle external HTTP/HTTPS URLs
  /// For security, we show a confirmation dialog before opening external links
  void _handleExternalUrl(Uri uri) {
    showDialog(
      context: context,
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: AlertDialog(
          title: const Text('فتح رابط خارجي'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('هل تريد فتح هذا الرابط في المتصفح؟'),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.grey[200],
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  uri.toString(),
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[700],
                    fontFamily: 'monospace',
                  ),
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('إلغاء'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                _launchExternalUrl(uri);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF367C2B),
              ),
              child: const Text('فتح'),
            ),
          ],
        ),
      ),
    );
  }

  /// Launch external URL using platform channel
  /// Since url_launcher may not be available, we use a platform channel approach
  Future<void> _launchExternalUrl(Uri uri) async {
    try {
      // Try to launch using platform-specific method
      const platform = MethodChannel('sahool/url_launcher');
      final launched = await platform.invokeMethod<bool>(
        'launchUrl',
        {'url': uri.toString()},
      );

      if (launched != true) {
        // Fallback: Copy URL to clipboard and show message
        await Clipboard.setData(ClipboardData(text: uri.toString()));
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('تم نسخ الرابط. الصقه في المتصفح لفتحه'),
              duration: Duration(seconds: 3),
            ),
          );
        }
      }
    } on PlatformException catch (_) {
      // Platform channel not available - copy URL to clipboard
      await Clipboard.setData(ClipboardData(text: uri.toString()));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('تم نسخ الرابط. الصقه في المتصفح لفتحه'),
            duration: Duration(seconds: 3),
          ),
        );
      }
    } catch (e) {
      debugPrint('Error launching external URL: $e');
      _showNavigationError('تعذر فتح الرابط الخارجي');
    }
  }

  /// Navigate based on sahool:// custom scheme
  /// e.g., sahool://field/123 -> /field/123
  void _navigateToSahoolScheme(Uri uri) {
    // Convert sahool:// scheme to internal route
    // sahool://field/123 -> /field/123
    // sahool://tasks -> /tasks
    final path = '/${uri.host}${uri.path}';
    final queryString = uri.query.isNotEmpty ? '?${uri.query}' : '';
    _navigateToInternalRoute('$path$queryString');
  }

  /// Show navigation error message
  void _showNavigationError(String message) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: Colors.red[700],
        ),
      );
    }
  }
}

/// شاشة إعدادات الإشعارات
class NotificationSettingsScreen extends ConsumerStatefulWidget {
  const NotificationSettingsScreen({super.key});

  @override
  ConsumerState<NotificationSettingsScreen> createState() =>
      _NotificationSettingsScreenState();
}

class _NotificationSettingsScreenState
    extends ConsumerState<NotificationSettingsScreen> {
  // ✅ لا حاجة لـ initState - الإعدادات تُحمّل تلقائياً في constructor الـ Notifier

  @override
  Widget build(BuildContext context) {
    final settings = ref.watch(settingsProvider).settings;

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('إعدادات الإشعارات'),
          backgroundColor: const Color(0xFF367C2B),
          foregroundColor: Colors.white,
        ),
        body: ListView(
          children: [
            // التفعيل العام
            SwitchListTile(
              title: const Text('تفعيل الإشعارات'),
              subtitle: const Text('إيقاف جميع الإشعارات'),
              value: settings.enabled,
              activeColor: const Color(0xFF367C2B),
              onChanged: (value) {
                ref.read(settingsProvider.notifier).toggleEnabled(value);
              },
            ),

            const Divider(),

            // أنواع الإشعارات
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text(
                'أنواع الإشعارات',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ),

            SwitchListTile(
              title: const Text('التنبيهات'),
              subtitle: const Text('تنبيهات عاجلة ومهمة'),
              secondary: const Text('⚠️', style: TextStyle(fontSize: 24)),
              value: settings.alertsEnabled,
              activeColor: const Color(0xFF367C2B),
              onChanged: settings.enabled
                  ? (value) => ref.read(settingsProvider.notifier).toggleAlerts(value)
                  : null,
            ),

            SwitchListTile(
              title: const Text('الإجراءات'),
              subtitle: const Text('إجراءات مطلوبة للحقول'),
              secondary: const Text('📋', style: TextStyle(fontSize: 24)),
              value: settings.actionsEnabled,
              activeColor: const Color(0xFF367C2B),
              onChanged: settings.enabled
                  ? (value) => ref.read(settingsProvider.notifier).toggleActions(value)
                  : null,
            ),

            SwitchListTile(
              title: const Text('الطقس'),
              subtitle: const Text('تنبيهات وتحديثات الطقس'),
              secondary: const Text('🌤️', style: TextStyle(fontSize: 24)),
              value: settings.weatherEnabled,
              activeColor: const Color(0xFF367C2B),
              onChanged: settings.enabled
                  ? (value) => ref.read(settingsProvider.notifier).toggleWeather(value)
                  : null,
            ),

            SwitchListTile(
              title: const Text('صحة المحصول'),
              subtitle: const Text('تشخيصات NDVI والتوصيات'),
              secondary: const Text('🌱', style: TextStyle(fontSize: 24)),
              value: settings.cropHealthEnabled,
              activeColor: const Color(0xFF367C2B),
              onChanged: settings.enabled
                  ? (value) => ref.read(settingsProvider.notifier).toggleCropHealth(value)
                  : null,
            ),

            const Divider(),

            // إعدادات الصوت والاهتزاز
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text(
                'الصوت والاهتزاز',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ),

            SwitchListTile(
              title: const Text('الصوت'),
              subtitle: const Text('تشغيل صوت عند الإشعار'),
              secondary: const Icon(Icons.volume_up),
              value: settings.soundEnabled,
              activeColor: const Color(0xFF367C2B),
              onChanged: settings.enabled
                  ? (value) => ref.read(settingsProvider.notifier).toggleSound(value)
                  : null,
            ),

            SwitchListTile(
              title: const Text('الاهتزاز'),
              subtitle: const Text('اهتزاز الجهاز عند الإشعار'),
              secondary: const Icon(Icons.vibration),
              value: settings.vibrationEnabled,
              activeColor: const Color(0xFF367C2B),
              onChanged: settings.enabled
                  ? (value) => ref.read(settingsProvider.notifier).toggleVibration(value)
                  : null,
            ),
          ],
        ),
      ),
    );
  }
}
