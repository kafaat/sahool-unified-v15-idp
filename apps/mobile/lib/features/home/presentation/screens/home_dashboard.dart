import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/config/theme.dart';
import '../../../../core/logging/logging.dart';
import '../../../notifications/presentation/providers/notification_provider.dart';
import '../../../weather/presentation/providers/weather_provider.dart';
import '../../logic/home_providers.dart';
import '../widgets/quick_stats_card.dart';
import '../widgets/weather_widget.dart';
import '../widgets/field_card.dart';
import '../widgets/action_summary_widget.dart';
import '../widgets/alert_banner.dart';

/// شاشة الرئيسية الموحدة
/// Unified Home Dashboard
class HomeDashboard extends ConsumerStatefulWidget {
  const HomeDashboard({super.key});

  @override
  ConsumerState<HomeDashboard> createState() => _HomeDashboardState();
}

class _HomeDashboardState extends ConsumerState<HomeDashboard> {
  @override
  void initState() {
    super.initState();
    // Log screen navigation
    Logger.navigation('/home', routeNameAr: 'الرئيسية');
    _loadInitialData();
  }

  void _loadInitialData() {
    Logger.debug('Loading home dashboard data', tag: 'HOME');
    Future.microtask(() async {
      await ref.read(notificationsProvider.notifier).loadNotifications();
      // Load weather data
      await ref.read(weatherProvider.notifier).loadWeatherByLocation(15.3694, 44.1910);
      Logger.info(
        'Home data loaded',
        messageAr: 'تم تحميل بيانات الرئيسية',
        tag: 'HOME',
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final unreadCount = ref.watch(unreadCountProvider);

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: _buildAppBar(unreadCount),
        body: RefreshIndicator(
          onRefresh: () async {
            Logger.user('Pull to refresh', actionAr: 'سحب للتحديث', screen: 'home');
            _loadInitialData();
            ref.invalidate(dashboardFieldsProvider);
          },
          color: SahoolTheme.primary,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // شريط التنبيهات
                const Padding(
                  padding: EdgeInsets.fromLTRB(16, 16, 16, 0),
                  child: AlertBanner(),
                ),

                // ويدجت الطقس
                const Padding(
                  padding: EdgeInsets.fromLTRB(16, 16, 16, 0),
                  child: WeatherWidget(),
                ),

                // إحصائيات سريعة
                _buildSectionHeader('نظرة سريعة'),
                const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 16),
                  child: QuickStatsCard(),
                ),

                // ملخص الإجراءات
                _buildSectionHeader('الإجراءات المطلوبة'),
                const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 16),
                  child: ActionSummaryWidget(),
                ),

                // الحقول
                _buildFieldsSection(),

                // مساحة للتنقل السفلي
                const SizedBox(height: 100),
              ],
            ),
          ),
        ),
      ),
    );
  }

  PreferredSizeWidget _buildAppBar(int unreadCount) {
    return AppBar(
      title: Row(
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(Icons.agriculture, color: Colors.white, size: 24),
          ),
          const SizedBox(width: 10),
          const Text(
            'سهول',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 22,
            ),
          ),
        ],
      ),
      backgroundColor: SahoolTheme.primary,
      foregroundColor: Colors.white,
      elevation: 0,
      actions: [
        // أيقونة الإشعارات
        Stack(
          children: [
            IconButton(
              icon: const Icon(Icons.notifications_outlined, size: 26),
              onPressed: () => context.push('/notifications'),
            ),
            if (unreadCount > 0)
              Positioned(
                right: 8,
                top: 8,
                child: Container(
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    color: Colors.red,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: SahoolTheme.primary, width: 2),
                  ),
                  constraints: const BoxConstraints(
                    minWidth: 20,
                    minHeight: 20,
                  ),
                  child: Text(
                    unreadCount > 9 ? '9+' : '$unreadCount',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              ),
          ],
        ),
        const SizedBox(width: 4),
      ],
    );
  }

  Widget _buildSectionHeader(String title, {VoidCallback? onViewAll}) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 24, 16, 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.grey[800],
                ),
          ),
          if (onViewAll != null)
            TextButton(
              onPressed: onViewAll,
              child: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('عرض الكل'),
                  SizedBox(width: 4),
                  Icon(Icons.arrow_back_ios, size: 14),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildFieldsSection() {
    final fieldsAsync = ref.watch(dashboardFieldsProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 24, 16, 12),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'حقولي',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Colors.grey[800],
                    ),
              ),
              TextButton(
                onPressed: () => context.push('/fields'),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text('عرض الكل'),
                    SizedBox(width: 4),
                    Icon(Icons.arrow_back_ios, size: 14),
                  ],
                ),
              ),
            ],
          ),
        ),
        fieldsAsync.when(
          loading: () => const Padding(
            padding: EdgeInsets.all(32),
            child: Center(child: CircularProgressIndicator()),
          ),
          error: (err, _) => const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16),
            child: Card(
              child: Padding(
                padding: EdgeInsets.all(24),
                child: Center(
                  child: Column(
                    children: [
                      Icon(Icons.error_outline, size: 48, color: Colors.red),
                      SizedBox(height: 12),
                      Text('خطأ في تحميل الحقول'),
                    ],
                  ),
                ),
              ),
            ),
          ),
          data: (fields) {
            if (fields.isEmpty) {
              return const Padding(
                padding: EdgeInsets.symmetric(horizontal: 16),
                child: Card(
                  child: Padding(
                    padding: EdgeInsets.all(24),
                    child: Center(
                      child: Column(
                        children: [
                          Icon(Icons.landscape_outlined, size: 48, color: Colors.grey),
                          SizedBox(height: 12),
                          Text('لا توجد حقول مسجلة'),
                          SizedBox(height: 8),
                          Text(
                            'أضف حقلك الأول من الخريطة',
                            style: TextStyle(color: Colors.grey, fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              );
            }

            return Column(
              children: fields.take(5).map(
                (field) => Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                  child: FieldCard(
                    fieldId: field.id,
                    name: field.name,
                    areaHectares: field.areaHectares,
                    cropType: field.cropType ?? '—',
                    healthScore: field.ndviCurrent ?? 0.0,
                    onTap: () => _navigateToField(field.id),
                  ),
                ),
              ).toList(),
            );
          },
        ),
      ],
    );
  }

  void _navigateToField(String fieldId) {
    Logger.field(
      'Opening field details',
      messageAr: 'فتح تفاصيل الحقل',
      fieldId: fieldId,
      action: 'view',
      actionAr: 'عرض',
    );
    Logger.user(
      'Field card tap',
      actionAr: 'الضغط على بطاقة الحقل',
      screen: 'home',
      targetId: fieldId,
    );
    context.push('/field/$fieldId');
  }
}
