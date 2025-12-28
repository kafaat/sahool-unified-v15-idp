/// GDD Dashboard Screen - شاشة لوحة معلومات درجات النمو الحراري
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../models/gdd_models.dart';
import '../providers/gdd_provider.dart';
import '../widgets/gdd_gauge_widget.dart';
import '../widgets/growth_stage_timeline.dart';
import 'gdd_chart_screen.dart';
import 'gdd_settings_screen.dart';

/// شاشة لوحة معلومات GDD
class GDDDashboardScreen extends ConsumerStatefulWidget {
  final String fieldId;
  final String? fieldName;

  const GDDDashboardScreen({
    super.key,
    required this.fieldId,
    this.fieldName,
  });

  @override
  ConsumerState<GDDDashboardScreen> createState() => _GDDDashboardScreenState();
}

class _GDDDashboardScreenState extends ConsumerState<GDDDashboardScreen> {

  @override
  void initState() {
    super.initState();
    // تعيين الحقل المحدد
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(selectedFieldIdProvider.notifier).state = widget.fieldId;
    });
  }

  @override
  Widget build(BuildContext context) {
    final gddAsync = ref.watch(fieldGDDProvider(widget.fieldId));
    final settingsAsync = ref.watch(gddSettingsProvider(widget.fieldId));

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('درجات النمو الحراري'),
            if (widget.fieldName != null)
              Text(
                widget.fieldName!,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.white70,
                    ),
              ),
          ],
        ),
        actions: [
          // إعدادات GDD
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => GDDSettingsScreen(fieldId: widget.fieldId),
                ),
              );
            },
          ),
          // الرسم البياني
          IconButton(
            icon: const Icon(Icons.show_chart),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => GDDChartScreen(fieldId: widget.fieldId),
                ),
              );
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(fieldGDDProvider);
          ref.invalidate(gddSettingsProvider);
        },
        child: gddAsync.when(
          data: (gdd) => _buildDashboard(context, gdd, settingsAsync.value),
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stack) => _buildErrorState(context, error),
        ),
      ),
    );
  }

  Widget _buildDashboard(
    BuildContext context,
    GDDAccumulation gdd,
    GDDSettings? settings,
  ) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // معلومات الموسم
          _buildSeasonInfo(context, gdd, settings),
          const SizedBox(height: 16),

          // مقياس GDD الدائري
          GDDGaugeWidget(
            currentGDD: gdd.totalGDD,
            totalGDD: gdd.currentStage != null
                ? gdd.currentStage!.gddEnd
                : (settings?.cropType != null ? 2000 : 1500),
            currentStage: gdd.currentStage,
            progressPercent: gdd.progressPercent,
          ),
          const SizedBox(height: 24),

          // بطاقات الإحصائيات السريعة
          _buildQuickStats(context, gdd),
          const SizedBox(height: 24),

          // المخطط الزمني لمراحل النمو
          if (gdd.currentStage != null || gdd.nextStage != null) ...[
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'مراحل النمو',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 16),
                    GrowthStageTimeline(
                      fieldId: widget.fieldId,
                      currentGDD: gdd.totalGDD,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],

          // السجلات اليومية الأخيرة
          _buildRecentRecords(context, gdd),
        ],
      ),
    );
  }

  Widget _buildSeasonInfo(
    BuildContext context,
    GDDAccumulation gdd,
    GDDSettings? settings,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.calendar_today,
                  color: Theme.of(context).primaryColor,
                ),
                const SizedBox(width: 8),
                Text(
                  'معلومات الموسم',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const Divider(height: 24),
            if (settings?.cropType != null) ...[
              _buildInfoRow(
                context,
                'المحصول',
                settings!.cropType.getName('ar'),
                Icons.grass,
              ),
            ],
            _buildInfoRow(
              context,
              'تاريخ الزراعة',
              settings?.plantingDate != null
                  ? DateFormat('dd MMM yyyy', Localizations.localeOf(context).languageCode).format(settings!.plantingDate)
                  : DateFormat('dd MMM yyyy', Localizations.localeOf(context).languageCode).format(gdd.startDate),
              Icons.event,
            ),
            _buildInfoRow(
              context,
              'عدد الأيام',
              '${gdd.daysCount} يوم',
              Icons.today,
            ),
            _buildInfoRow(
              context,
              'متوسط GDD يومياً',
              '${gdd.averageGDDPerDay.toStringAsFixed(1)} درجة',
              Icons.trending_up,
            ),
            _buildInfoRow(
              context,
              'درجة الأساس',
              '${gdd.baseTemperature.toStringAsFixed(1)}°C',
              Icons.thermostat,
            ),
            if (gdd.upperThreshold != null)
              _buildInfoRow(
                context,
                'الحد الأعلى',
                '${gdd.upperThreshold!.toStringAsFixed(1)}°C',
                Icons.thermostat_outlined,
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(
    BuildContext context,
    String label,
    String value,
    IconData icon,
  ) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey.shade600),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey.shade600,
                  ),
            ),
          ),
          Text(
            value,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickStats(BuildContext context, GDDAccumulation gdd) {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            context,
            'GDD المتراكم',
            gdd.totalGDD.toStringAsFixed(0),
            Icons.analytics,
            Colors.blue,
          ),
        ),
        const SizedBox(width: 12),
        if (gdd.daysToNextStage != null)
          Expanded(
            child: _buildStatCard(
              context,
              'أيام حتى المرحلة التالية',
              '${gdd.daysToNextStage}',
              Icons.event_available,
              Colors.green,
            ),
          )
        else
          Expanded(
            child: _buildStatCard(
              context,
              'نسبة التقدم',
              '${(gdd.progressPercent ?? 0).toStringAsFixed(0)}%',
              Icons.pie_chart,
              Colors.orange,
            ),
          ),
      ],
    );
  }

  Widget _buildStatCard(
    BuildContext context,
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey.shade600,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentRecords(BuildContext context, GDDAccumulation gdd) {
    if (gdd.recentRecords.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'السجلات اليومية الأخيرة',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const Divider(height: 24),
            ...gdd.recentRecords.take(5).map((record) {
              final dateFormat = DateFormat('dd MMM yyyy', Localizations.localeOf(context).languageCode);
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: Row(
                  children: [
                    // التاريخ
                    Container(
                      width: 60,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: Theme.of(context).primaryColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Column(
                        children: [
                          Text(
                            dateFormat.format(record.date).split(' ')[0],
                            style: Theme.of(context)
                                .textTheme
                                .titleMedium
                                ?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                          ),
                          Text(
                            dateFormat.format(record.date).split(' ')[1],
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 12),

                    // درجات الحرارة
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                Icons.thermostat,
                                size: 16,
                                color: Colors.red.shade300,
                              ),
                              const SizedBox(width: 4),
                              Text(
                                '${record.tMax.toStringAsFixed(1)}°',
                                style: Theme.of(context).textTheme.bodySmall,
                              ),
                              const SizedBox(width: 8),
                              Icon(
                                Icons.thermostat,
                                size: 16,
                                color: Colors.blue.shade300,
                              ),
                              const SizedBox(width: 4),
                              Text(
                                '${record.tMin.toStringAsFixed(1)}°',
                                style: Theme.of(context).textTheme.bodySmall,
                              ),
                            ],
                          ),
                          Text(
                            'متوسط: ${record.tAvg.toStringAsFixed(1)}°C',
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ],
                      ),
                    ),

                    // قيمة GDD
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            Colors.green.shade400,
                            Colors.green.shade600,
                          ],
                        ),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Column(
                        children: [
                          Text(
                            record.gddValue.toStringAsFixed(1),
                            style: Theme.of(context)
                                .textTheme
                                .titleMedium
                                ?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                          ),
                          Text(
                            'GDD',
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  color: Colors.white,
                                ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
            const SizedBox(height: 8),
            Center(
              child: TextButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => GDDChartScreen(fieldId: widget.fieldId),
                    ),
                  );
                },
                icon: const Icon(Icons.show_chart),
                label: const Text('عرض الرسم البياني الكامل'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState(BuildContext context, Object error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red.shade300,
            ),
            const SizedBox(height: 16),
            Text(
              'فشل في تحميل بيانات GDD',
              style: Theme.of(context).textTheme.titleMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              error.toString(),
              style: Theme.of(context).textTheme.bodySmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () {
                ref.invalidate(fieldGDDProvider);
              },
              icon: const Icon(Icons.refresh),
              label: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      ),
    );
  }
}
