import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/config/theme.dart';
import '../../../notifications/presentation/providers/notification_provider.dart';
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
    _loadInitialData();
  }

  void _loadInitialData() {
    Future.microtask(() {
      ref.read(notificationsProvider.notifier).loadNotifications();
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
          onRefresh: () async => _loadInitialData(),
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
              color: Colors.white.withOpacity(0.2),
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
              onPressed: () => Navigator.pushNamed(context, '/notifications'),
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
    // Demo fields - في الإنتاج ستكون من API
    final demoFields = [
      {
        'id': 'field_1',
        'name': 'حقل القمح الشمالي',
        'area': 45.5,
        'crop': 'قمح',
        'health': 0.78,
      },
      {
        'id': 'field_2',
        'name': 'حقل الشعير الغربي',
        'area': 32.0,
        'crop': 'شعير',
        'health': 0.85,
      },
      {
        'id': 'field_3',
        'name': 'حقل البرسيم',
        'area': 28.5,
        'crop': 'برسيم',
        'health': 0.65,
      },
    ];

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
                onPressed: () {},
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
        ...demoFields.map(
          (field) => Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: FieldCard(
              fieldId: field['id'] as String,
              name: field['name'] as String,
              areaHectares: field['area'] as double,
              cropType: field['crop'] as String,
              healthScore: field['health'] as double,
              onTap: () => _navigateToField(field['id'] as String),
            ),
          ),
        ),
      ],
    );
  }

  void _navigateToField(String fieldId) {
    Navigator.pushNamed(
      context,
      '/crop-health',
      arguments: {'fieldId': fieldId},
    );
  }
}
