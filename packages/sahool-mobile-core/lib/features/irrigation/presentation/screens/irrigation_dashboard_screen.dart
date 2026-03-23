/// Irrigation Dashboard Screen - لوحة تحكم الري
/// Main irrigation management screen with field selector, water balance,
/// scheduling overview, and quick action buttons.
/// الشاشة الرئيسية لإدارة الري مع اختيار الحقل وتوازن المياه والجدولة
library;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/sahool_theme.dart';
import '../../../../core/theme/organic_widgets.dart';
import '../providers/irrigation_provider.dart';
import '../widgets/water_balance_card.dart';
import '../widgets/irrigation_method_selector.dart';
import 'irrigation_schedule_screen.dart';

/// Irrigation Dashboard Screen
/// لوحة تحكم الري الذكي
class IrrigationDashboardScreen extends ConsumerStatefulWidget {
  /// Optional list of field IDs available to this user
  final List<FieldItem> fields;

  const IrrigationDashboardScreen({
    super.key,
    this.fields = const [],
  });

  @override
  ConsumerState<IrrigationDashboardScreen> createState() =>
      _IrrigationDashboardScreenState();
}

/// Field item for field selector
class FieldItem {
  final String id;
  final String nameAr;
  final String nameEn;
  final double areaHectares;
  final String? cropId;

  const FieldItem({
    required this.id,
    required this.nameAr,
    required this.nameEn,
    required this.areaHectares,
    this.cropId,
  });

  String getDisplayName(String locale) =>
      locale == 'ar' ? nameAr : nameEn;
}

class _IrrigationDashboardScreenState
    extends ConsumerState<IrrigationDashboardScreen> {
  @override
  Widget build(BuildContext context) {
    final dashboardAsync = ref.watch(irrigationDashboardProvider);
    final selectedFieldId = ref.watch(selectedFieldIdProvider);
    final isArabic = Directionality.of(context) == TextDirection.rtl;

    return Scaffold(
      backgroundColor: SahoolColors.warmCream,
      body: RefreshIndicator(
        onRefresh: () async {
          ref.read(irrigationControllerProvider.notifier).refreshAll();
        },
        child: CustomScrollView(
          slivers: [
            // SliverAppBar - floating with snap for quick access
            SliverAppBar(
              title: Text(isArabic ? 'الري الذكي' : 'Smart Irrigation'),
              backgroundColor: Colors.white,
              foregroundColor: SahoolColors.forestGreen,
              elevation: 0,
              floating: true,
              snap: true,
              actions: [
                IconButton(
                  icon: const Icon(Icons.history),
                  onPressed: () => _navigateToHistory(context),
                  tooltip: isArabic ? 'سجل الري' : 'Irrigation History',
                ),
                IconButton(
                  icon: const Icon(Icons.refresh),
                  onPressed: () {
                    ref.read(irrigationControllerProvider.notifier).refreshAll();
                  },
                  tooltip: isArabic ? 'تحديث' : 'Refresh',
                ),
              ],
            ),

            // 1. Field Selector - اختيار الحقل
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
                child: _buildFieldSelector(selectedFieldId, isArabic),
              ),
            ),

            // 2. Quick Stats Row - صف الإحصائيات السريعة
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
                child: _buildQuickStats(dashboardAsync, isArabic),
              ),
            ),

            // 3. Water Balance Card - بطاقة توازن المياه
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
                child: _buildWaterBalanceSection(dashboardAsync, isArabic),
              ),
            ),

            // 4. Next Irrigation Countdown - العد التنازلي للري القادم
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
                child: _buildNextIrrigationCard(dashboardAsync, isArabic),
              ),
            ),

            // 5. Quick Actions - إجراءات سريعة
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
                child: _buildQuickActions(isArabic),
              ),
            ),

            // 6. Crop Water Needs Card - بطاقة احتياجات المحصول
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
                child: _buildCropWaterNeedsCard(dashboardAsync, isArabic),
              ),
            ),

            // 7. Scheduling Overview - نظرة عامة على الجدولة
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
                child: _buildSchedulingOverview(dashboardAsync, isArabic),
              ),
            ),

            // Bottom padding
            const SliverPadding(padding: EdgeInsets.only(bottom: 80)),
          ],
        ),
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Field Selector - اختيار الحقل
  // ─────────────────────────────────────────────────────────────────────────────

  Widget _buildFieldSelector(String? selectedFieldId, bool isArabic) {
    if (widget.fields.isEmpty) {
      return OrganicCard(
        color: SahoolColors.paleOlive.withOpacity(0.5),
        child: Row(
          children: [
            const Icon(Icons.info_outline, color: SahoolColors.sageGreen),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                isArabic
                    ? 'لم يتم تحديد حقل. اختر حقلاً لعرض بيانات الري.'
                    : 'No field selected. Choose a field to view irrigation data.',
                style: TextStyle(color: Colors.grey[600], fontSize: 14),
              ),
            ),
          ],
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: SahoolColors.sageGreen.withOpacity(0.3)),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: selectedFieldId,
          isExpanded: true,
          icon: const Icon(Icons.keyboard_arrow_down,
              color: SahoolColors.forestGreen),
          hint: Row(
            children: [
              const Icon(Icons.landscape, color: SahoolColors.sageGreen),
              const SizedBox(width: 12),
              Text(
                isArabic ? 'اختر الحقل' : 'Select Field',
                style: TextStyle(color: Colors.grey[600]),
              ),
            ],
          ),
          items: widget.fields.map((field) {
            return DropdownMenuItem<String>(
              value: field.id,
              child: Row(
                children: [
                  const Icon(Icons.landscape,
                      color: SahoolColors.forestGreen, size: 20),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          field.getDisplayName(isArabic ? 'ar' : 'en'),
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        Text(
                          '${field.areaHectares} ${isArabic ? 'هكتار' : 'ha'}',
                          style:
                              TextStyle(fontSize: 12, color: Colors.grey[500]),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
          onChanged: (value) {
            ref.read(selectedFieldIdProvider.notifier).state = value;
          },
        ),
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Quick Stats - الإحصائيات السريعة
  // ─────────────────────────────────────────────────────────────────────────────

  Widget _buildQuickStats(
    AsyncValue<IrrigationDashboardSummary> dashboardAsync,
    bool isArabic,
  ) {
    return dashboardAsync.when(
      data: (summary) {
        final wb = summary.waterBalance;
        return Row(
          children: [
            Expanded(
              child: _StatCard(
                icon: Icons.water_drop,
                value: wb != null
                    ? '${wb.soilMoisturePercent.toStringAsFixed(0)}%'
                    : '--',
                label: isArabic ? 'رطوبة التربة' : 'Soil Moisture',
                color: _getMoistureColor(wb?.soilMoisturePercent),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _StatCard(
                icon: Icons.thermostat,
                value: wb != null
                    ? '${wb.et0.toStringAsFixed(1)} mm'
                    : '--',
                label: isArabic ? 'التبخر-نتح' : 'ET0',
                color: Colors.blue,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _StatCard(
                icon: Icons.schedule,
                value: summary.hoursUntilNextIrrigation != null
                    ? '${summary.hoursUntilNextIrrigation}h'
                    : '--',
                label: isArabic ? 'الري القادم' : 'Next Irrigation',
                color: SahoolColors.forestGreen,
              ),
            ),
          ],
        );
      },
      loading: () => Row(
        children: [
          Expanded(
            child: _StatCard(
              icon: Icons.water_drop,
              value: '--',
              label: isArabic ? 'رطوبة التربة' : 'Soil Moisture',
              color: Colors.grey,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _StatCard(
              icon: Icons.thermostat,
              value: '--',
              label: isArabic ? 'التبخر-نتح' : 'ET0',
              color: Colors.grey,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _StatCard(
              icon: Icons.schedule,
              value: '--',
              label: isArabic ? 'الري القادم' : 'Next Irrigation',
              color: Colors.grey,
            ),
          ),
        ],
      ),
      error: (_, __) => Center(
        child: Text(
          isArabic ? 'خطأ في تحميل البيانات' : 'Error loading data',
          style: const TextStyle(color: SahoolColors.danger),
        ),
      ),
    );
  }

  Color _getMoistureColor(double? percent) {
    if (percent == null) return Colors.grey;
    if (percent >= 60) return SahoolColors.forestGreen;
    if (percent >= 40) return SahoolColors.harvestGold;
    if (percent >= 20) return Colors.orange;
    return SahoolColors.danger;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Water Balance Section - قسم توازن المياه
  // ─────────────────────────────────────────────────────────────────────────────

  Widget _buildWaterBalanceSection(
    AsyncValue<IrrigationDashboardSummary> dashboardAsync,
    bool isArabic,
  ) {
    return dashboardAsync.when(
      data: (summary) {
        if (summary.waterBalance == null) {
          return OrganicCard(
            child: Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  children: [
                    Icon(Icons.water_drop,
                        size: 48, color: Colors.grey[300]),
                    const SizedBox(height: 12),
                    Text(
                      isArabic
                          ? 'اختر حقلاً لعرض توازن المياه'
                          : 'Select a field to view water balance',
                      style: TextStyle(color: Colors.grey[500]),
                    ),
                  ],
                ),
              ),
            ),
          );
        }

        return WaterBalanceCard(
          waterBalance: summary.waterBalance!,
          isArabic: isArabic,
        );
      },
      loading: () => const OrganicCard(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: Center(
            child: CircularProgressIndicator(
              color: SahoolColors.forestGreen,
            ),
          ),
        ),
      ),
      error: (error, _) => OrganicCard(
        color: SahoolColors.danger.withOpacity(0.05),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              const Icon(Icons.error_outline, color: SahoolColors.danger),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  isArabic
                      ? 'فشل في تحميل توازن المياه'
                      : 'Failed to load water balance',
                  style: const TextStyle(color: SahoolColors.danger),
                ),
              ),
              TextButton(
                onPressed: () => ref.invalidate(irrigationDashboardProvider),
                child: Text(isArabic ? 'إعادة المحاولة' : 'Retry'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Next Irrigation Countdown - العد التنازلي للري القادم
  // ─────────────────────────────────────────────────────────────────────────────

  Widget _buildNextIrrigationCard(
    AsyncValue<IrrigationDashboardSummary> dashboardAsync,
    bool isArabic,
  ) {
    return dashboardAsync.when(
      data: (summary) {
        final nextEvent = summary.nextEvent;
        if (nextEvent == null) {
          return const SizedBox.shrink();
        }

        final now = DateTime.now();
        final diff = nextEvent.scheduledAt.difference(now);
        final hours = diff.inHours;
        final minutes = diff.inMinutes % 60;
        final isUrgent = hours < 6;

        return OrganicCard(
          color: isUrgent
              ? SahoolColors.harvestGold.withOpacity(0.1)
              : SahoolColors.forestGreen.withOpacity(0.05),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: isUrgent
                          ? SahoolColors.harvestGold.withOpacity(0.2)
                          : SahoolColors.forestGreen.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      isUrgent ? Icons.alarm : Icons.schedule,
                      color: isUrgent
                          ? SahoolColors.harvestGold
                          : SahoolColors.forestGreen,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          isArabic ? 'الري القادم' : 'Next Irrigation',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                        Text(
                          isArabic
                              ? 'بعد $hours ساعة و $minutes دقيقة'
                              : 'In $hours hours and $minutes minutes',
                          style: TextStyle(
                            color: isUrgent
                                ? SahoolColors.harvestGold
                                : Colors.grey[600],
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  _InfoChip(
                    icon: Icons.timer,
                    label:
                        '${nextEvent.durationMinutes.toStringAsFixed(0)} ${isArabic ? 'دقيقة' : 'min'}',
                  ),
                  const SizedBox(width: 12),
                  _InfoChip(
                    icon: Icons.water_drop,
                    label:
                        '${nextEvent.waterAmountLiters.toStringAsFixed(0)} ${isArabic ? 'لتر' : 'L'}',
                  ),
                ],
              ),
            ],
          ),
        );
      },
      loading: () => const SizedBox.shrink(),
      error: (_, __) => const SizedBox.shrink(),
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Quick Actions - الإجراءات السريعة
  // ─────────────────────────────────────────────────────────────────────────────

  Widget _buildQuickActions(bool isArabic) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          isArabic ? 'إجراءات سريعة' : 'Quick Actions',
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 18,
            color: SahoolColors.forestGreen,
          ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _ActionButton(
                icon: Icons.play_circle_filled,
                label: isArabic ? 'بدء الري' : 'Start Irrigation',
                color: SahoolColors.forestGreen,
                onTap: () => _showStartIrrigationSheet(context),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _ActionButton(
                icon: Icons.calendar_month,
                label: isArabic ? 'جدولة الري' : 'Schedule',
                color: Colors.blue,
                onTap: () => _navigateToSchedule(context),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _ActionButton(
                icon: Icons.calculate,
                label: isArabic ? 'حاسبة الري' : 'Calculator',
                color: SahoolColors.harvestGold,
                onTap: () => _showCalculatorSheet(context),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _ActionButton(
                icon: Icons.sensors,
                label: isArabic ? 'قراءة مستشعر' : 'Sensor Reading',
                color: Colors.purple,
                onTap: () => _showSensorSheet(context),
              ),
            ),
          ],
        ),
      ],
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Crop Water Needs - احتياجات المحصول المائية
  // ─────────────────────────────────────────────────────────────────────────────

  Widget _buildCropWaterNeedsCard(
    AsyncValue<IrrigationDashboardSummary> dashboardAsync,
    bool isArabic,
  ) {
    return dashboardAsync.when(
      data: (summary) {
        final wb = summary.waterBalance;
        if (wb == null) return const SizedBox.shrink();

        return OrganicCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(Icons.grass, color: Colors.blue),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    isArabic
                        ? 'احتياجات المحصول المائية'
                        : 'Crop Water Needs',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              _CropNeedRow(
                label: isArabic ? 'التبخر-نتح المرجعي (ET0)' : 'Reference ET0',
                value: '${wb.et0.toStringAsFixed(1)} mm/${isArabic ? 'يوم' : 'day'}',
                icon: Icons.thermostat,
                color: Colors.orange,
              ),
              const SizedBox(height: 8),
              _CropNeedRow(
                label: isArabic ? 'التبخر-نتح الفعلي (ETc)' : 'Crop ETc',
                value: '${wb.etc.toStringAsFixed(1)} mm/${isArabic ? 'يوم' : 'day'}',
                icon: Icons.eco,
                color: SahoolColors.forestGreen,
              ),
              const SizedBox(height: 8),
              _CropNeedRow(
                label: isArabic ? 'هطول الأمطار' : 'Rainfall',
                value: '${wb.rainfall.toStringAsFixed(1)} mm',
                icon: Icons.grain,
                color: Colors.blue,
              ),
              const SizedBox(height: 8),
              _CropNeedRow(
                label: isArabic ? 'العجز المائي' : 'Water Deficit',
                value: '${wb.deficit.toStringAsFixed(1)} mm',
                icon: Icons.warning_amber,
                color: wb.deficit > 0 ? SahoolColors.danger : Colors.green,
              ),
              if (wb.needsIrrigation) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: SahoolColors.harvestGold.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.info_outline,
                          color: SahoolColors.harvestGold, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          isArabic
                              ? 'يحتاج الحقل للري. العجز: ${wb.deficit.toStringAsFixed(1)} مم'
                              : 'Field needs irrigation. Deficit: ${wb.deficit.toStringAsFixed(1)} mm',
                          style: const TextStyle(
                            color: SahoolColors.harvestGold,
                            fontSize: 13,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        );
      },
      loading: () => const SizedBox.shrink(),
      error: (_, __) => const SizedBox.shrink(),
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Scheduling Overview - نظرة عامة على الجدولة
  // ─────────────────────────────────────────────────────────────────────────────

  Widget _buildSchedulingOverview(
    AsyncValue<IrrigationDashboardSummary> dashboardAsync,
    bool isArabic,
  ) {
    return dashboardAsync.when(
      data: (summary) {
        final schedule = summary.schedule;
        if (schedule == null || schedule.events.isEmpty) {
          return OrganicCard(
            child: InkWell(
              onTap: () => _navigateToSchedule(context),
              child: Padding(
                padding: const EdgeInsets.all(8),
                child: Row(
                  children: [
                    Icon(Icons.calendar_month,
                        size: 40, color: Colors.grey[300]),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            isArabic
                                ? 'لا يوجد جدول ري'
                                : 'No irrigation schedule',
                            style: TextStyle(
                              color: Colors.grey[600],
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          Text(
                            isArabic
                                ? 'أنشئ جدولاً ذكياً للري'
                                : 'Create a smart irrigation schedule',
                            style: TextStyle(
                              color: Colors.grey[400],
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const Icon(Icons.arrow_forward_ios,
                        size: 16, color: Colors.grey),
                  ],
                ),
              ),
            ),
          );
        }

        // Show upcoming events (max 3)
        final upcoming = schedule.events
            .where((e) => e.scheduledAt.isAfter(DateTime.now()))
            .take(3)
            .toList();

        return OrganicCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: SahoolColors.forestGreen.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(Icons.calendar_month,
                        color: SahoolColors.forestGreen),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      isArabic ? 'جدول الري القادم' : 'Upcoming Schedule',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ),
                  TextButton(
                    onPressed: () => _navigateToSchedule(context),
                    child: Text(
                      isArabic ? 'عرض الكل' : 'View All',
                      style: const TextStyle(color: SahoolColors.forestGreen),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              ...upcoming.map((event) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: _ScheduleEventTile(event: event, isArabic: isArabic),
                );
              }),
            ],
          ),
        );
      },
      loading: () => const SizedBox.shrink(),
      error: (_, __) => const SizedBox.shrink(),
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Navigation & Sheet Helpers
  // ─────────────────────────────────────────────────────────────────────────────

  void _navigateToSchedule(BuildContext context) {
    final fieldId = ref.read(selectedFieldIdProvider);
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => IrrigationScheduleScreen(fieldId: fieldId),
      ),
    );
  }

  void _navigateToHistory(BuildContext context) {
    // Navigate to irrigation history screen (reuse schedule screen for now)
    _navigateToSchedule(context);
  }

  void _showStartIrrigationSheet(BuildContext context) {
    final isArabic = Directionality.of(context) == TextDirection.rtl;
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _StartIrrigationSheet(isArabic: isArabic),
    );
  }

  void _showCalculatorSheet(BuildContext context) {
    final isArabic = Directionality.of(context) == TextDirection.rtl;
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _IrrigationCalculatorSheet(isArabic: isArabic),
    );
  }

  void _showSensorSheet(BuildContext context) {
    final isArabic = Directionality.of(context) == TextDirection.rtl;
    final fieldId = ref.read(selectedFieldIdProvider);
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) =>
          _SensorReadingSheet(fieldId: fieldId, isArabic: isArabic),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Helper Widgets
// ═══════════════════════════════════════════════════════════════════════════════

class _StatCard extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;
  final Color color;

  const _StatCard({
    required this.icon,
    required this.value,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.withOpacity(0.1)),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 22),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 17,
              color: color,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: const TextStyle(fontSize: 11, color: Colors.grey),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _ActionButton({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
        decoration: BoxDecoration(
          color: color.withOpacity(0.08),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.2)),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 22),
            const SizedBox(width: 8),
            Flexible(
              child: Text(
                label,
                style: TextStyle(
                  color: color,
                  fontWeight: FontWeight.w600,
                  fontSize: 13,
                ),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;

  const _InfoChip({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: Colors.grey[600]),
          const SizedBox(width: 4),
          Text(label,
              style: TextStyle(fontSize: 12, color: Colors.grey[700])),
        ],
      ),
    );
  }
}

class _CropNeedRow extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color color;

  const _CropNeedRow({
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 18, color: color),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            label,
            style: TextStyle(fontSize: 13, color: Colors.grey[700]),
          ),
        ),
        Text(
          value,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 13,
            color: color,
          ),
        ),
      ],
    );
  }
}

class _ScheduleEventTile extends StatelessWidget {
  final IrrigationEvent event;
  final bool isArabic;

  const _ScheduleEventTile({
    required this.event,
    required this.isArabic,
  });

  @override
  Widget build(BuildContext context) {
    final dayNames = isArabic
        ? ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت']
        : ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: SahoolColors.paleOlive.withOpacity(0.3),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: SahoolColors.forestGreen.withOpacity(0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  dayNames[event.scheduledAt.weekday % 7],
                  style: const TextStyle(
                    fontSize: 10,
                    color: SahoolColors.forestGreen,
                  ),
                ),
                Text(
                  '${event.scheduledAt.day}',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 15,
                    color: SahoolColors.forestGreen,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${event.scheduledAt.hour.toString().padLeft(2, '0')}:${event.scheduledAt.minute.toString().padLeft(2, '0')}',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(
                  '${event.durationMinutes.toStringAsFixed(0)} ${isArabic ? 'دقيقة' : 'min'} - ${event.waterAmountLiters.toStringAsFixed(0)} ${isArabic ? 'لتر' : 'L'}',
                  style: TextStyle(color: Colors.grey[600], fontSize: 12),
                ),
              ],
            ),
          ),
          _EventStatusBadge(status: event.status, isArabic: isArabic),
        ],
      ),
    );
  }
}

class _EventStatusBadge extends StatelessWidget {
  final String status;
  final bool isArabic;

  const _EventStatusBadge({required this.status, required this.isArabic});

  @override
  Widget build(BuildContext context) {
    Color color;
    String label;

    switch (status) {
      case 'scheduled':
      case 'pending':
        color = Colors.blue;
        label = isArabic ? 'مجدول' : 'Scheduled';
        break;
      case 'active':
        color = SahoolColors.forestGreen;
        label = isArabic ? 'جاري' : 'Active';
        break;
      case 'completed':
        color = Colors.green;
        label = isArabic ? 'مكتمل' : 'Done';
        break;
      case 'skipped':
        color = Colors.grey;
        label = isArabic ? 'تم التخطي' : 'Skipped';
        break;
      default:
        color = Colors.grey;
        label = status;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 10,
          color: color,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Start Irrigation Bottom Sheet
// ═══════════════════════════════════════════════════════════════════════════════

class _StartIrrigationSheet extends ConsumerWidget {
  final bool isArabic;

  const _StartIrrigationSheet({required this.isArabic});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final methodsAsync = ref.watch(irrigationMethodsProvider);

    return Container(
      height: MediaQuery.of(context).size.height * 0.5,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 24),
          Text(
            isArabic ? 'بدء الري' : 'Start Irrigation',
            style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Text(
            isArabic
                ? 'اختر طريقة الري لبدء عملية الري'
                : 'Select irrigation method to begin',
            style: TextStyle(color: Colors.grey[600]),
          ),
          const SizedBox(height: 24),
          Expanded(
            child: methodsAsync.when(
              data: (methods) => IrrigationMethodSelector(
                methods: methods,
                isArabic: isArabic,
                onMethodSelected: (method) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(
                        isArabic
                            ? 'تم بدء الري بطريقة ${method.nameAr}'
                            : 'Started irrigation with ${method.nameEn}',
                      ),
                      backgroundColor: SahoolColors.forestGreen,
                    ),
                  );
                },
              ),
              loading: () => const Center(
                child:
                    CircularProgressIndicator(color: SahoolColors.forestGreen),
              ),
              error: (_, __) => Center(
                child: Text(
                  isArabic
                      ? 'فشل في تحميل طرق الري'
                      : 'Failed to load methods',
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Irrigation Calculator Bottom Sheet
// ═══════════════════════════════════════════════════════════════════════════════

class _IrrigationCalculatorSheet extends ConsumerStatefulWidget {
  final bool isArabic;

  const _IrrigationCalculatorSheet({required this.isArabic});

  @override
  ConsumerState<_IrrigationCalculatorSheet> createState() =>
      _IrrigationCalculatorSheetState();
}

class _IrrigationCalculatorSheetState
    extends ConsumerState<_IrrigationCalculatorSheet> {
  final _areaController = TextEditingController(text: '1.0');
  final _et0Controller = TextEditingController(text: '5.0');
  IrrigationCalculation? _result;
  bool _isCalculating = false;

  @override
  void dispose() {
    _areaController.dispose();
    _et0Controller.dispose();
    super.dispose();
  }

  Future<void> _calculate() async {
    final cropId = ref.read(selectedCropIdProvider);
    final methodId = ref.read(selectedMethodIdProvider);

    if (cropId == null || methodId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            widget.isArabic
                ? 'يرجى اختيار المحصول وطريقة الري'
                : 'Please select crop and irrigation method',
          ),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() => _isCalculating = true);

    final controller = ref.read(irrigationControllerProvider.notifier);
    final result = await controller.calculateNeeds(
      cropId: cropId,
      methodId: methodId,
      areaHectares: double.tryParse(_areaController.text) ?? 1.0,
      et0: double.tryParse(_et0Controller.text) ?? 5.0,
    );

    if (mounted) {
      setState(() {
        _result = result;
        _isCalculating = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final cropsAsync = ref.watch(irrigationCropsProvider);
    final methodsAsync = ref.watch(irrigationMethodsProvider);
    final selectedCropId = ref.watch(selectedCropIdProvider);
    final selectedMethodId = ref.watch(selectedMethodIdProvider);

    return Container(
      height: MediaQuery.of(context).size.height * 0.85,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 24),
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: SahoolColors.harvestGold.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child:
                    const Icon(Icons.calculate, color: SahoolColors.harvestGold),
              ),
              const SizedBox(width: 12),
              Text(
                widget.isArabic ? 'حاسبة الري' : 'Irrigation Calculator',
                style:
                    const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Crop selector
                  cropsAsync.when(
                    data: (crops) => DropdownButtonFormField<String>(
                      value: selectedCropId,
                      decoration: InputDecoration(
                        labelText:
                            widget.isArabic ? 'المحصول' : 'Crop',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        prefixIcon: const Icon(Icons.grass),
                      ),
                      items: crops.map((crop) {
                        return DropdownMenuItem(
                          value: crop.id,
                          child: Text(widget.isArabic
                              ? crop.nameAr
                              : crop.nameEn),
                        );
                      }).toList(),
                      onChanged: (v) =>
                          ref.read(selectedCropIdProvider.notifier).state = v,
                    ),
                    loading: () => const LinearProgressIndicator(),
                    error: (_, __) => const SizedBox.shrink(),
                  ),

                  const SizedBox(height: 16),

                  // Method selector
                  methodsAsync.when(
                    data: (methods) => DropdownButtonFormField<String>(
                      value: selectedMethodId,
                      decoration: InputDecoration(
                        labelText: widget.isArabic
                            ? 'طريقة الري'
                            : 'Irrigation Method',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        prefixIcon: const Icon(Icons.water),
                      ),
                      items: methods.map((m) {
                        return DropdownMenuItem(
                          value: m.id,
                          child: Text(
                            '${widget.isArabic ? m.nameAr : m.nameEn} (${(m.efficiency * 100).toInt()}%)',
                          ),
                        );
                      }).toList(),
                      onChanged: (v) => ref
                          .read(selectedMethodIdProvider.notifier)
                          .state = v,
                    ),
                    loading: () => const LinearProgressIndicator(),
                    error: (_, __) => const SizedBox.shrink(),
                  ),

                  const SizedBox(height: 16),

                  // Area and ET0 inputs
                  Row(
                    children: [
                      Expanded(
                        child: TextFormField(
                          controller: _areaController,
                          keyboardType: TextInputType.number,
                          decoration: InputDecoration(
                            labelText: widget.isArabic
                                ? 'المساحة (هكتار)'
                                : 'Area (ha)',
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: TextFormField(
                          controller: _et0Controller,
                          keyboardType: TextInputType.number,
                          decoration: InputDecoration(
                            labelText: widget.isArabic
                                ? 'ET0 (مم/يوم)'
                                : 'ET0 (mm/day)',
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 24),

                  // Calculate button
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: _isCalculating ? null : _calculate,
                      icon: _isCalculating
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Icon(Icons.calculate),
                      label: Text(
                        widget.isArabic ? 'حساب' : 'Calculate',
                        style: const TextStyle(fontSize: 16),
                      ),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        backgroundColor: SahoolColors.forestGreen,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),

                  // Results
                  if (_result != null) ...[
                    const SizedBox(height: 24),
                    OrganicCard(
                      color: SahoolColors.forestGreen.withOpacity(0.05),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            widget.isArabic ? 'النتيجة' : 'Result',
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                          const Divider(),
                          _ResultRow(
                            label: widget.isArabic
                                ? 'كمية المياه'
                                : 'Water Needed',
                            value:
                                '${_result!.waterNeedMm.toStringAsFixed(1)} mm',
                          ),
                          _ResultRow(
                            label: widget.isArabic ? 'بالليتر' : 'In Liters',
                            value:
                                '${_result!.waterNeedLiters.toStringAsFixed(0)} L',
                          ),
                          _ResultRow(
                            label:
                                widget.isArabic ? 'مدة الري' : 'Duration',
                            value:
                                '${_result!.irrigationDurationMinutes.toStringAsFixed(0)} ${widget.isArabic ? 'دقيقة' : 'min'}',
                          ),
                          const SizedBox(height: 8),
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.blue.withOpacity(0.05),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              widget.isArabic
                                  ? _result!.recommendationAr
                                  : _result!.recommendation,
                              style: TextStyle(
                                color: Colors.blue[800],
                                fontSize: 13,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ResultRow extends StatelessWidget {
  final String label;
  final String value;

  const _ResultRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: Colors.grey[700])),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Sensor Reading Bottom Sheet
// ═══════════════════════════════════════════════════════════════════════════════

class _SensorReadingSheet extends ConsumerStatefulWidget {
  final String? fieldId;
  final bool isArabic;

  const _SensorReadingSheet({this.fieldId, required this.isArabic});

  @override
  ConsumerState<_SensorReadingSheet> createState() =>
      _SensorReadingSheetState();
}

class _SensorReadingSheetState extends ConsumerState<_SensorReadingSheet> {
  final _valueController = TextEditingController();
  String _sensorType = 'soil_moisture';
  String _unit = '%';
  bool _isSubmitting = false;

  @override
  void dispose() {
    _valueController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.6,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 24),
          Text(
            widget.isArabic ? 'تسجيل قراءة مستشعر' : 'Record Sensor Reading',
            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 24),
          DropdownButtonFormField<String>(
            value: _sensorType,
            decoration: InputDecoration(
              labelText:
                  widget.isArabic ? 'نوع المستشعر' : 'Sensor Type',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              prefixIcon: const Icon(Icons.sensors),
            ),
            items: [
              DropdownMenuItem(
                value: 'soil_moisture',
                child: Text(
                    widget.isArabic ? 'رطوبة التربة' : 'Soil Moisture'),
              ),
              DropdownMenuItem(
                value: 'temperature',
                child: Text(
                    widget.isArabic ? 'درجة الحرارة' : 'Temperature'),
              ),
              DropdownMenuItem(
                value: 'humidity',
                child: Text(
                    widget.isArabic ? 'الرطوبة الجوية' : 'Air Humidity'),
              ),
              DropdownMenuItem(
                value: 'ec',
                child: Text(widget.isArabic
                    ? 'التوصيل الكهربائي'
                    : 'Electrical Conductivity'),
              ),
            ],
            onChanged: (value) {
              if (value != null) {
                setState(() {
                  _sensorType = value;
                  _unit = _getUnit(value);
                });
              }
            },
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _valueController,
            keyboardType: TextInputType.number,
            decoration: InputDecoration(
              labelText:
                  '${widget.isArabic ? 'القيمة' : 'Value'} ($_unit)',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              prefixIcon: const Icon(Icons.straighten),
            ),
          ),
          const Spacer(),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _isSubmitting ? null : _submit,
              icon: _isSubmitting
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.save),
              label: Text(
                widget.isArabic ? 'حفظ القراءة' : 'Save Reading',
                style: const TextStyle(fontSize: 16),
              ),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                backgroundColor: SahoolColors.forestGreen,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _getUnit(String sensorType) {
    switch (sensorType) {
      case 'soil_moisture':
        return '%';
      case 'temperature':
        return 'C';
      case 'humidity':
        return '%';
      case 'ec':
        return 'dS/m';
      default:
        return '';
    }
  }

  Future<void> _submit() async {
    final fieldId = widget.fieldId;
    if (fieldId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(widget.isArabic
              ? 'يرجى اختيار حقل أولاً'
              : 'Please select a field first'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    final value = double.tryParse(_valueController.text);
    if (value == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(widget.isArabic
              ? 'يرجى إدخال قيمة صحيحة'
              : 'Please enter a valid value'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() => _isSubmitting = true);

    final controller = ref.read(irrigationControllerProvider.notifier);
    final success = await controller.recordSensorReading(
      fieldId: fieldId,
      sensorType: _sensorType,
      value: value,
      unit: _unit,
    );

    if (mounted) {
      setState(() => _isSubmitting = false);
      if (success) {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(widget.isArabic
                ? 'تم تسجيل القراءة بنجاح'
                : 'Reading recorded successfully'),
            backgroundColor: SahoolColors.forestGreen,
          ),
        );
      }
    }
  }
}
