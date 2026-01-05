/// SAHOOL Astronomical Calendar Screen
/// شاشة التقويم الفلكي
///
/// الشاشة الرئيسية للتقويم الفلكي اليمني التقليدي

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/astronomical_providers.dart';
import '../widgets/today_card.dart';
import '../widgets/moon_phase_card.dart';
import '../widgets/lunar_mansion_card.dart';
import '../widgets/weekly_forecast_card.dart';
import '../widgets/proverb_card.dart';
import '../widgets/best_days_card.dart';

/// شاشة التقويم الفلكي الرئيسية
class AstronomicalScreen extends ConsumerWidget {
  const AstronomicalScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedTab = ref.watch(selectedAstronomicalTabProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('التقويم الفلكي'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.info_outline),
            onPressed: () => _showInfoDialog(context),
            tooltip: 'معلومات',
          ),
        ],
      ),
      body: Column(
        children: [
          // التبويبات
          _buildTabBar(ref, selectedTab),
          // المحتوى
          Expanded(
            child: _buildTabContent(selectedTab),
          ),
        ],
      ),
    );
  }

  Widget _buildTabBar(WidgetRef ref, int selectedTab) {
    final tabs = [
      const _TabItem(icon: Icons.today, label: 'اليوم'),
      const _TabItem(icon: Icons.calendar_month, label: 'الأسبوع'),
      const _TabItem(icon: Icons.nightlight_round, label: 'القمر'),
      const _TabItem(icon: Icons.format_quote, label: 'الأمثال'),
      const _TabItem(icon: Icons.star, label: 'أفضل الأيام'),
    ];

    return Container(
      height: 60,
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: tabs.length,
        itemBuilder: (context, index) {
          final isSelected = selectedTab == index;
          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4),
            child: FilterChip(
              selected: isSelected,
              label: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    tabs[index].icon,
                    size: 18,
                    color: isSelected
                        ? Theme.of(context).colorScheme.onPrimary
                        : Theme.of(context).colorScheme.primary,
                  ),
                  const SizedBox(width: 6),
                  Text(tabs[index].label),
                ],
              ),
              onSelected: (_) {
                ref.read(selectedAstronomicalTabProvider.notifier).state = index;
              },
              selectedColor: Theme.of(context).colorScheme.primary,
              labelStyle: TextStyle(
                color: isSelected
                    ? Theme.of(context).colorScheme.onPrimary
                    : Theme.of(context).colorScheme.onSurface,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildTabContent(int selectedTab) {
    switch (selectedTab) {
      case 0:
        return const _TodayTab();
      case 1:
        return const _WeeklyTab();
      case 2:
        return const _MoonTab();
      case 3:
        return const _ProverbsTab();
      case 4:
        return const _BestDaysTab();
      default:
        return const _TodayTab();
    }
  }

  void _showInfoDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.auto_awesome, color: Colors.amber),
            SizedBox(width: 8),
            Text('التقويم الفلكي اليمني'),
          ],
        ),
        content: const SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'التقويم الفلكي اليمني التقليدي يعتمد على:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 12),
              _InfoItem(
                icon: Icons.nightlight_round,
                title: 'المنازل القمرية',
                description: '28 منزلة تحدد أفضل أوقات الزراعة',
              ),
              _InfoItem(
                icon: Icons.brightness_2,
                title: 'أطوار القمر',
                description: 'من المحاق إلى البدر وتأثيرها على النبات',
              ),
              _InfoItem(
                icon: Icons.calendar_today,
                title: 'التاريخ الهجري',
                description: 'التقويم القمري المستخدم في اليمن',
              ),
              _InfoItem(
                icon: Icons.format_quote,
                title: 'الأمثال الزراعية',
                description: 'حكمة الأجداد في الزراعة اليمنية',
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('حسناً'),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// تبويب اليوم - Today Tab
// ═══════════════════════════════════════════════════════════════════════════════

class _TodayTab extends ConsumerWidget {
  const _TodayTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final todayAsync = ref.watch(todayAstronomicalProvider);
    final wisdomAsync = ref.watch(dailyWisdomProvider);

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(todayAstronomicalProvider);
        ref.invalidate(dailyWisdomProvider);
      },
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // بطاقة اليوم
          todayAsync.when(
            data: (data) => TodayCard(data: data),
            loading: () => const _LoadingCard(),
            error: (e, _) => _ErrorCard(message: e.toString()),
          ),
          const SizedBox(height: 16),
          // بطاقة الحكمة
          wisdomAsync.when(
            data: (wisdom) => ProverbCard(
              proverb: wisdom.proverbOfTheDay.text,
              meaning: wisdom.proverbOfTheDay.meaning,
              application: wisdom.proverbOfTheDay.application,
            ),
            loading: () => const _LoadingCard(),
            error: (e, _) => const SizedBox.shrink(),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// تبويب الأسبوع - Weekly Tab
// ═══════════════════════════════════════════════════════════════════════════════

class _WeeklyTab extends ConsumerWidget {
  const _WeeklyTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final forecastAsync = ref.watch(currentWeekForecastProvider);

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(currentWeekForecastProvider);
      },
      child: forecastAsync.when(
        data: (forecast) => WeeklyForecastCard(forecast: forecast),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: _ErrorCard(message: e.toString())),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// تبويب القمر - Moon Tab
// ═══════════════════════════════════════════════════════════════════════════════

class _MoonTab extends ConsumerWidget {
  const _MoonTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final moonPhaseAsync = ref.watch(currentMoonPhaseProvider);
    final lunarMansionAsync = ref.watch(currentLunarMansionProvider);

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(currentMoonPhaseProvider);
        ref.invalidate(currentLunarMansionProvider);
      },
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // بطاقة طور القمر
          moonPhaseAsync.when(
            data: (moonPhase) => MoonPhaseCard(moonPhase: moonPhase),
            loading: () => const _LoadingCard(),
            error: (e, _) => _ErrorCard(message: e.toString()),
          ),
          const SizedBox(height: 16),
          // بطاقة المنزلة القمرية
          lunarMansionAsync.when(
            data: (mansion) => LunarMansionCard(mansion: mansion),
            loading: () => const _LoadingCard(),
            error: (e, _) => _ErrorCard(message: e.toString()),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// تبويب الأمثال - Proverbs Tab
// ═══════════════════════════════════════════════════════════════════════════════

class _ProverbsTab extends ConsumerWidget {
  const _ProverbsTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final proverbsAsync = ref.watch(allProverbsProvider);

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(allProverbsProvider);
      },
      child: proverbsAsync.when(
        data: (proverbs) => ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: proverbs.general.length,
          itemBuilder: (context, index) {
            final proverb = proverbs.general[index];
            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: ProverbCard(
                proverb: proverb.proverb,
                meaning: proverb.meaning,
                application: proverb.application,
              ),
            );
          },
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: _ErrorCard(message: e.toString())),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// تبويب أفضل الأيام - Best Days Tab
// ═══════════════════════════════════════════════════════════════════════════════

class _BestDaysTab extends ConsumerWidget {
  const _BestDaysTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedActivity = ref.watch(selectedActivityProvider);
    final bestDaysAsync = ref.watch(
      bestDaysProvider(BestDaysParams(activity: selectedActivity)),
    );

    return Column(
      children: [
        // اختيار النشاط
        Padding(
          padding: const EdgeInsets.all(16),
          child: _ActivitySelector(
            selectedActivity: selectedActivity,
            onChanged: (activity) {
              ref.read(selectedActivityProvider.notifier).state = activity;
            },
          ),
        ),
        // قائمة أفضل الأيام
        Expanded(
          child: RefreshIndicator(
            onRefresh: () async {
              ref.invalidate(
                bestDaysProvider(BestDaysParams(activity: selectedActivity)),
              );
            },
            child: bestDaysAsync.when(
              data: (result) => BestDaysCard(result: result),
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Center(child: _ErrorCard(message: e.toString())),
            ),
          ),
        ),
      ],
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// مكونات مساعدة - Helper Widgets
// ═══════════════════════════════════════════════════════════════════════════════

class _TabItem {
  final IconData icon;
  final String label;

  const _TabItem({required this.icon, required this.label});
}

class _InfoItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;

  const _InfoItem({
    required this.icon,
    required this.title,
    required this.description,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 24, color: Theme.of(context).colorScheme.primary),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(
                  description,
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _LoadingCard extends StatelessWidget {
  const _LoadingCard();

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Container(
        height: 150,
        alignment: Alignment.center,
        child: const CircularProgressIndicator(),
      ),
    );
  }
}

class _ErrorCard extends StatelessWidget {
  final String message;

  const _ErrorCard({required this.message});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Theme.of(context).colorScheme.errorContainer,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(
              Icons.error_outline,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                'حدث خطأ: $message',
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onErrorContainer,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ActivitySelector extends StatelessWidget {
  final String selectedActivity;
  final ValueChanged<String> onChanged;

  const _ActivitySelector({
    required this.selectedActivity,
    required this.onChanged,
  });

  static const activities = [
    'زراعة',
    'حصاد',
    'ري',
    'تقليم',
    'تسميد',
    'رش',
  ];

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: activities.map((activity) {
        final isSelected = activity == selectedActivity;
        return ChoiceChip(
          label: Text(activity),
          selected: isSelected,
          onSelected: (_) => onChanged(activity),
        );
      }).toList(),
    );
  }
}
