/// Irrigation Schedule Screen - شاشة جدول الري
/// Calendar view of irrigation events with add/edit and smart recommendations
/// عرض تقويمي لأحداث الري مع إضافة/تعديل وتوصيات ذكية
library;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/sahool_theme.dart';
import '../../../../core/theme/organic_widgets.dart';
import '../providers/irrigation_provider.dart';

/// Irrigation Schedule Screen
/// شاشة جدول الري
class IrrigationScheduleScreen extends ConsumerStatefulWidget {
  final String? fieldId;

  const IrrigationScheduleScreen({super.key, this.fieldId});

  @override
  ConsumerState<IrrigationScheduleScreen> createState() =>
      _IrrigationScheduleScreenState();
}

class _IrrigationScheduleScreenState
    extends ConsumerState<IrrigationScheduleScreen> {
  late DateTime _selectedMonth;
  DateTime? _selectedDay;
  int _scheduleDays = 14;

  @override
  void initState() {
    super.initState();
    _selectedMonth = DateTime(DateTime.now().year, DateTime.now().month);
    _selectedDay = DateTime.now();
  }

  @override
  Widget build(BuildContext context) {
    final fieldId = widget.fieldId ?? ref.watch(selectedFieldIdProvider);
    final isArabic = Directionality.of(context) == TextDirection.rtl;

    return Scaffold(
      backgroundColor: SahoolColors.warmCream,
      appBar: AppBar(
        title: Text(isArabic ? 'جدول الري' : 'Irrigation Schedule'),
        backgroundColor: Colors.white,
        foregroundColor: SahoolColors.forestGreen,
        elevation: 0,
        actions: [
          if (fieldId != null)
            IconButton(
              icon: const Icon(Icons.auto_awesome),
              onPressed: () => _showGenerateScheduleSheet(context, isArabic),
              tooltip: isArabic ? 'إنشاء جدول ذكي' : 'Smart Schedule',
            ),
        ],
      ),
      body: fieldId == null
          ? _buildNoFieldSelected(isArabic)
          : _buildScheduleView(fieldId, isArabic),
      floatingActionButton: fieldId != null
          ? FloatingActionButton.extended(
              onPressed: () => _showAddEventSheet(context, isArabic),
              backgroundColor: SahoolColors.forestGreen,
              foregroundColor: Colors.white,
              icon: const Icon(Icons.add),
              label: Text(isArabic ? 'إضافة ري' : 'Add Irrigation'),
            )
          : null,
    );
  }

  Widget _buildNoFieldSelected(bool isArabic) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.landscape, size: 80, color: Colors.grey[300]),
          const SizedBox(height: 16),
          Text(
            isArabic
                ? 'يرجى اختيار حقل من لوحة التحكم'
                : 'Please select a field from the dashboard',
            style: TextStyle(color: Colors.grey[500], fontSize: 16),
          ),
        ],
      ),
    );
  }

  Widget _buildScheduleView(String fieldId, bool isArabic) {
    final scheduleAsync = ref.watch(irrigationScheduleProvider(fieldId));

    return scheduleAsync.when(
      data: (schedule) => RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(irrigationScheduleProvider);
        },
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            // 1. Calendar View - عرض التقويم
            _buildCalendar(schedule, isArabic),

            const SizedBox(height: 20),

            // 2. Smart Recommendation Banner - شريط التوصيات الذكية
            _buildSmartRecommendation(schedule, isArabic),

            const SizedBox(height: 20),

            // 3. Events for selected day - أحداث اليوم المحدد
            _buildDayEvents(schedule, isArabic),

            const SizedBox(height: 20),

            // 4. Summary Statistics - إحصائيات ملخصة
            _buildScheduleSummary(schedule, isArabic),

            const SizedBox(height: 80),
          ],
        ),
      ),
      loading: () => const Center(
        child: CircularProgressIndicator(color: SahoolColors.forestGreen),
      ),
      error: (error, _) => Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 48, color: SahoolColors.danger),
            const SizedBox(height: 16),
            Text(
              error.toString(),
              style: const TextStyle(color: SahoolColors.danger),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () => ref.invalidate(irrigationScheduleProvider),
              icon: const Icon(Icons.refresh),
              label: Text(isArabic ? 'إعادة المحاولة' : 'Retry'),
              style: ElevatedButton.styleFrom(
                backgroundColor: SahoolColors.forestGreen,
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calendar View - عرض التقويم
  // ─────────────────────────────────────────────────────────────────────────────

  Widget _buildCalendar(IrrigationSchedule schedule, bool isArabic) {
    final now = DateTime.now();
    final firstDayOfMonth = DateTime(_selectedMonth.year, _selectedMonth.month, 1);
    final lastDayOfMonth = DateTime(_selectedMonth.year, _selectedMonth.month + 1, 0);
    final startWeekday = firstDayOfMonth.weekday % 7;

    // Build set of days with irrigation events
    final eventDays = <int>{};
    for (final event in schedule.events) {
      if (event.scheduledAt.year == _selectedMonth.year &&
          event.scheduledAt.month == _selectedMonth.month) {
        eventDays.add(event.scheduledAt.day);
      }
    }

    final dayNames = isArabic
        ? ['أحد', 'إثن', 'ثلا', 'أرب', 'خمي', 'جمع', 'سبت']
        : ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    final monthNames = isArabic
        ? [
            'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
            'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
          ]
        : [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
          ];

    return OrganicCard(
      child: Column(
        children: [
          // Month navigation
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              IconButton(
                icon: const Icon(Icons.chevron_left),
                onPressed: () {
                  setState(() {
                    _selectedMonth = DateTime(
                      _selectedMonth.year,
                      _selectedMonth.month - 1,
                    );
                  });
                },
              ),
              Text(
                '${monthNames[_selectedMonth.month - 1]} ${_selectedMonth.year}',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                ),
              ),
              IconButton(
                icon: const Icon(Icons.chevron_right),
                onPressed: () {
                  setState(() {
                    _selectedMonth = DateTime(
                      _selectedMonth.year,
                      _selectedMonth.month + 1,
                    );
                  });
                },
              ),
            ],
          ),
          const SizedBox(height: 8),

          // Day names header
          Row(
            children: dayNames.map((name) {
              return Expanded(
                child: Center(
                  child: Text(
                    name,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 8),

          // Calendar grid
          ...List.generate(
            ((startWeekday + lastDayOfMonth.day - 1) ~/ 7) + 1,
            (weekIndex) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  children: List.generate(7, (dayIndex) {
                    final dayNumber =
                        weekIndex * 7 + dayIndex - startWeekday + 1;

                    if (dayNumber < 1 || dayNumber > lastDayOfMonth.day) {
                      return const Expanded(child: SizedBox(height: 40));
                    }

                    final date = DateTime(
                      _selectedMonth.year,
                      _selectedMonth.month,
                      dayNumber,
                    );
                    final isToday = date.year == now.year &&
                        date.month == now.month &&
                        date.day == now.day;
                    final isSelected = _selectedDay != null &&
                        date.year == _selectedDay!.year &&
                        date.month == _selectedDay!.month &&
                        date.day == _selectedDay!.day;
                    final hasEvent = eventDays.contains(dayNumber);

                    return Expanded(
                      child: GestureDetector(
                        onTap: () => setState(() => _selectedDay = date),
                        child: Container(
                          height: 40,
                          margin: const EdgeInsets.symmetric(horizontal: 2),
                          decoration: BoxDecoration(
                            color: isSelected
                                ? SahoolColors.forestGreen
                                : isToday
                                    ? SahoolColors.forestGreen.withValues(alpha: 0.1)
                                    : null,
                            borderRadius: BorderRadius.circular(10),
                            border: isToday && !isSelected
                                ? Border.all(
                                    color: SahoolColors.forestGreen,
                                    width: 1.5,
                                  )
                                : null,
                          ),
                          child: Stack(
                            alignment: Alignment.center,
                            children: [
                              Text(
                                '$dayNumber',
                                style: TextStyle(
                                  color: isSelected
                                      ? Colors.white
                                      : Colors.black87,
                                  fontWeight: isToday || isSelected
                                      ? FontWeight.bold
                                      : FontWeight.normal,
                                ),
                              ),
                              if (hasEvent)
                                Positioned(
                                  bottom: 4,
                                  child: Container(
                                    width: 6,
                                    height: 6,
                                    decoration: BoxDecoration(
                                      color: isSelected
                                          ? Colors.white
                                          : Colors.blue,
                                      shape: BoxShape.circle,
                                    ),
                                  ),
                                ),
                            ],
                          ),
                        ),
                      ),
                    );
                  }),
                ),
              );
            },
          ),

          // Legend
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: const BoxDecoration(
                  color: Colors.blue,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 6),
              Text(
                isArabic ? 'يوم ري' : 'Irrigation day',
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
              const SizedBox(width: 16),
              Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: SahoolColors.forestGreen.withValues(alpha: 0.3),
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 6),
              Text(
                isArabic ? 'اليوم' : 'Today',
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Smart Recommendation - التوصيات الذكية
  // ─────────────────────────────────────────────────────────────────────────────

  Widget _buildSmartRecommendation(
      IrrigationSchedule schedule, bool isArabic) {
    if (schedule.events.isEmpty) {
      return OrganicCard(
        color: Colors.blue.withValues(alpha: 0.05),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.blue.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.auto_awesome, color: Colors.blue),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isArabic ? 'جدولة ذكية' : 'Smart Scheduling',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Text(
                    isArabic
                        ? 'أنشئ جدول ري ذكي يعتمد على بيانات المحصول والطقس'
                        : 'Create a smart schedule based on crop data and weather',
                    style: TextStyle(color: Colors.grey[600], fontSize: 13),
                  ),
                ],
              ),
            ),
            TextButton(
              onPressed: () => _showGenerateScheduleSheet(context, isArabic),
              child: Text(isArabic ? 'إنشاء' : 'Create'),
            ),
          ],
        ),
      );
    }

    // Show next irrigation info
    final upcoming = schedule.events
        .where((e) => e.scheduledAt.isAfter(DateTime.now()))
        .toList();

    if (upcoming.isEmpty) return const SizedBox.shrink();

    final next = upcoming.first;
    final hoursUntil = next.scheduledAt.difference(DateTime.now()).inHours;

    return OrganicCard(
      color: hoursUntil < 12
          ? SahoolColors.harvestGold.withValues(alpha: 0.1)
          : SahoolColors.forestGreen.withValues(alpha: 0.05),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: hoursUntil < 12
                  ? SahoolColors.harvestGold.withValues(alpha: 0.2)
                  : SahoolColors.forestGreen.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              hoursUntil < 12 ? Icons.alarm : Icons.water_drop,
              color: hoursUntil < 12
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
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(
                  isArabic
                      ? 'بعد $hoursUntil ساعة - ${next.waterAmountLiters.toStringAsFixed(0)} لتر'
                      : 'In $hoursUntil hours - ${next.waterAmountLiters.toStringAsFixed(0)}L',
                  style: TextStyle(color: Colors.grey[600], fontSize: 13),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Day Events - أحداث اليوم
  // ─────────────────────────────────────────────────────────────────────────────

  Widget _buildDayEvents(IrrigationSchedule schedule, bool isArabic) {
    if (_selectedDay == null) return const SizedBox.shrink();

    final dayEvents = schedule.events.where((e) {
      return e.scheduledAt.year == _selectedDay!.year &&
          e.scheduledAt.month == _selectedDay!.month &&
          e.scheduledAt.day == _selectedDay!.day;
    }).toList();

    final dayNames = isArabic
        ? [
            'الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء',
            'الخميس', 'الجمعة', 'السبت'
          ]
        : [
            'Sunday', 'Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday', 'Saturday'
          ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '${dayNames[_selectedDay!.weekday % 7]}, ${_selectedDay!.day}/${_selectedDay!.month}/${_selectedDay!.year}',
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
            color: SahoolColors.forestGreen,
          ),
        ),
        const SizedBox(height: 12),
        if (dayEvents.isEmpty)
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Center(
              child: Column(
                children: [
                  Icon(Icons.event_busy, size: 40, color: Colors.grey[300]),
                  const SizedBox(height: 8),
                  Text(
                    isArabic
                        ? 'لا يوجد ري مجدول لهذا اليوم'
                        : 'No irrigation scheduled for this day',
                    style: TextStyle(color: Colors.grey[500]),
                  ),
                ],
              ),
            ),
          )
        else
          ...dayEvents.map((event) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: _IrrigationEventCard(event: event, isArabic: isArabic),
            );
          }),
      ],
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Schedule Summary - ملخص الجدول
  // ─────────────────────────────────────────────────────────────────────────────

  Widget _buildScheduleSummary(IrrigationSchedule schedule, bool isArabic) {
    if (schedule.events.isEmpty) return const SizedBox.shrink();

    final totalWater = schedule.events.fold<double>(
      0,
      (sum, e) => sum + e.waterAmountLiters,
    );
    final totalDuration = schedule.events.fold<double>(
      0,
      (sum, e) => sum + e.durationMinutes,
    );
    final completedCount =
        schedule.events.where((e) => e.status == 'completed').length;
    final pendingCount =
        schedule.events.where((e) => e.status != 'completed').length;

    return OrganicCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.purple.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.bar_chart, color: Colors.purple),
              ),
              const SizedBox(width: 12),
              Text(
                isArabic ? 'ملخص الجدول' : 'Schedule Summary',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _SummaryItem(
                  label: isArabic ? 'إجمالي المياه' : 'Total Water',
                  value: '${(totalWater / 1000).toStringAsFixed(1)} ${isArabic ? 'م3' : 'm3'}',
                  icon: Icons.water_drop,
                  color: Colors.blue,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _SummaryItem(
                  label: isArabic ? 'إجمالي المدة' : 'Total Duration',
                  value: '${totalDuration.toStringAsFixed(0)} ${isArabic ? 'دقيقة' : 'min'}',
                  icon: Icons.timer,
                  color: Colors.orange,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _SummaryItem(
                  label: isArabic ? 'مكتمل' : 'Completed',
                  value: '$completedCount',
                  icon: Icons.check_circle,
                  color: Colors.green,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _SummaryItem(
                  label: isArabic ? 'معلق' : 'Pending',
                  value: '$pendingCount',
                  icon: Icons.pending,
                  color: SahoolColors.harvestGold,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Generate Schedule Sheet
  // ─────────────────────────────────────────────────────────────────────────────

  void _showGenerateScheduleSheet(BuildContext context, bool isArabic) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => _GenerateScheduleSheet(
        fieldId: widget.fieldId ?? ref.read(selectedFieldIdProvider),
        isArabic: isArabic,
        initialDays: _scheduleDays,
        onGenerated: (days) {
          _scheduleDays = days;
          ref.invalidate(irrigationScheduleProvider);
        },
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Add Event Sheet
  // ─────────────────────────────────────────────────────────────────────────────

  void _showAddEventSheet(BuildContext context, bool isArabic) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => _AddIrrigationEventSheet(
        fieldId: widget.fieldId ?? ref.read(selectedFieldIdProvider),
        initialDate: _selectedDay ?? DateTime.now(),
        isArabic: isArabic,
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Helper Widgets
// ═══════════════════════════════════════════════════════════════════════════════

class _IrrigationEventCard extends StatelessWidget {
  final IrrigationEvent event;
  final bool isArabic;

  const _IrrigationEventCard({required this.event, required this.isArabic});

  @override
  Widget build(BuildContext context) {
    final isPast = event.scheduledAt.isBefore(DateTime.now());
    final isCompleted = event.status == 'completed';

    return OrganicCard(
      color: isCompleted
          ? Colors.green.withValues(alpha: 0.05)
          : isPast
              ? Colors.grey.withValues(alpha: 0.05)
              : Colors.white,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Time indicator
          Container(
            width: 56,
            padding: const EdgeInsets.symmetric(vertical: 8),
            decoration: BoxDecoration(
              color: isCompleted
                  ? Colors.green.withValues(alpha: 0.1)
                  : SahoolColors.forestGreen.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Column(
              children: [
                Icon(
                  isCompleted
                      ? Icons.check_circle
                      : isPast
                          ? Icons.history
                          : Icons.water_drop,
                  color: isCompleted
                      ? Colors.green
                      : SahoolColors.forestGreen,
                  size: 22,
                ),
                const SizedBox(height: 4),
                Text(
                  '${event.scheduledAt.hour.toString().padLeft(2, '0')}:${event.scheduledAt.minute.toString().padLeft(2, '0')}',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          // Event details
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        isArabic ? 'جلسة ري' : 'Irrigation Session',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 15,
                        ),
                      ),
                    ),
                    _StatusBadge(status: event.status, isArabic: isArabic),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(Icons.timer, size: 14, color: Colors.grey[500]),
                    const SizedBox(width: 4),
                    Text(
                      '${event.durationMinutes.toStringAsFixed(0)} ${isArabic ? 'دقيقة' : 'min'}',
                      style: TextStyle(
                          fontSize: 13, color: Colors.grey[700]),
                    ),
                    const SizedBox(width: 16),
                    Icon(Icons.water_drop, size: 14, color: Colors.blue[300]),
                    const SizedBox(width: 4),
                    Text(
                      '${event.waterAmountLiters.toStringAsFixed(0)} ${isArabic ? 'لتر' : 'L'}',
                      style: TextStyle(
                          fontSize: 13, color: Colors.grey[700]),
                    ),
                  ],
                ),
                if (event.notes != null && event.notes!.isNotEmpty) ...[
                  const SizedBox(height: 6),
                  Text(
                    event.notes!,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[500],
                      fontStyle: FontStyle.italic,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _StatusBadge extends StatelessWidget {
  final String status;
  final bool isArabic;

  const _StatusBadge({required this.status, required this.isArabic});

  @override
  Widget build(BuildContext context) {
    Color color;
    String label;

    switch (status) {
      case 'completed':
        color = Colors.green;
        label = isArabic ? 'مكتمل' : 'Done';
        break;
      case 'scheduled':
      case 'pending':
        color = Colors.blue;
        label = isArabic ? 'مجدول' : 'Scheduled';
        break;
      case 'active':
        color = SahoolColors.forestGreen;
        label = isArabic ? 'جاري' : 'Active';
        break;
      case 'skipped':
        color = Colors.grey;
        label = isArabic ? 'تخطي' : 'Skipped';
        break;
      default:
        color = Colors.grey;
        label = status;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 11,
          color: color,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}

class _SummaryItem extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color color;

  const _SummaryItem({
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 15,
                    color: color,
                  ),
                ),
                Text(
                  label,
                  style: TextStyle(fontSize: 11, color: Colors.grey[600]),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Generate Schedule Bottom Sheet
// ═══════════════════════════════════════════════════════════════════════════════

class _GenerateScheduleSheet extends ConsumerStatefulWidget {
  final String? fieldId;
  final bool isArabic;
  final int initialDays;
  final ValueChanged<int> onGenerated;

  const _GenerateScheduleSheet({
    required this.fieldId,
    required this.isArabic,
    required this.initialDays,
    required this.onGenerated,
  });

  @override
  ConsumerState<_GenerateScheduleSheet> createState() =>
      _GenerateScheduleSheetState();
}

class _GenerateScheduleSheetState
    extends ConsumerState<_GenerateScheduleSheet> {
  late int _days;
  bool _isGenerating = false;

  @override
  void initState() {
    super.initState();
    _days = widget.initialDays;
  }

  @override
  Widget build(BuildContext context) {
    final cropsAsync = ref.watch(irrigationCropsProvider);
    final methodsAsync = ref.watch(irrigationMethodsProvider);
    final selectedCropId = ref.watch(selectedCropIdProvider);
    final selectedMethodId = ref.watch(selectedMethodIdProvider);

    return Container(
      height: MediaQuery.of(context).size.height * 0.7,
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
                  color: Colors.blue.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.auto_awesome, color: Colors.blue),
              ),
              const SizedBox(width: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.isArabic ? 'إنشاء جدول ذكي' : 'Generate Smart Schedule',
                    style: const TextStyle(
                        fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  Text(
                    widget.isArabic
                        ? 'يعتمد على بيانات المحصول والطقس'
                        : 'Based on crop data and weather',
                    style: TextStyle(color: Colors.grey[600], fontSize: 13),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 24),
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                children: [
                  // Crop selector
                  cropsAsync.when(
                    data: (crops) => DropdownButtonFormField<String>(
                      value: selectedCropId,
                      decoration: InputDecoration(
                        labelText: widget.isArabic ? 'المحصول' : 'Crop',
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
                          child: Text(widget.isArabic
                              ? m.nameAr
                              : m.nameEn),
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

                  // Days slider
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${widget.isArabic ? 'عدد الأيام:' : 'Number of days:'} $_days',
                        style: const TextStyle(fontWeight: FontWeight.w500),
                      ),
                      Slider(
                        value: _days.toDouble(),
                        min: 7,
                        max: 30,
                        divisions: 23,
                        activeColor: SahoolColors.forestGreen,
                        label: '$_days',
                        onChanged: (v) => setState(() => _days = v.round()),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _isGenerating ? null : _generate,
              icon: _isGenerating
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.auto_awesome),
              label: Text(
                widget.isArabic ? 'إنشاء الجدول' : 'Generate Schedule',
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

  Future<void> _generate() async {
    final fieldId = widget.fieldId;
    final cropId = ref.read(selectedCropIdProvider);
    final methodId = ref.read(selectedMethodIdProvider);

    if (fieldId == null || cropId == null || methodId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            widget.isArabic
                ? 'يرجى تعبئة جميع الحقول'
                : 'Please fill all fields',
          ),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() => _isGenerating = true);

    final controller = ref.read(irrigationControllerProvider.notifier);
    final result = await controller.generateSchedule(
      fieldId: fieldId,
      cropId: cropId,
      methodId: methodId,
      days: _days,
    );

    if (mounted) {
      setState(() => _isGenerating = false);
      if (result != null) {
        widget.onGenerated(_days);
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              widget.isArabic
                  ? 'تم إنشاء جدول الري (${result.events.length} حدث)'
                  : 'Schedule generated (${result.events.length} events)',
            ),
            backgroundColor: SahoolColors.forestGreen,
          ),
        );
      }
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Add Irrigation Event Bottom Sheet
// ═══════════════════════════════════════════════════════════════════════════════

class _AddIrrigationEventSheet extends ConsumerStatefulWidget {
  final String? fieldId;
  final DateTime initialDate;
  final bool isArabic;

  const _AddIrrigationEventSheet({
    required this.fieldId,
    required this.initialDate,
    required this.isArabic,
  });

  @override
  ConsumerState<_AddIrrigationEventSheet> createState() =>
      _AddIrrigationEventSheetState();
}

class _AddIrrigationEventSheetState
    extends ConsumerState<_AddIrrigationEventSheet> {
  late DateTime _date;
  TimeOfDay _time = const TimeOfDay(hour: 6, minute: 0);
  final _durationController = TextEditingController(text: '60');
  final _waterController = TextEditingController(text: '5000');
  final _notesController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _date = widget.initialDate;
  }

  @override
  void dispose() {
    _durationController.dispose();
    _waterController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.75,
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
            widget.isArabic ? 'إضافة حدث ري' : 'Add Irrigation Event',
            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 24),
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                children: [
                  // Date picker
                  InkWell(
                    onTap: () async {
                      final picked = await showDatePicker(
                        context: context,
                        initialDate: _date,
                        firstDate: DateTime.now(),
                        lastDate:
                            DateTime.now().add(const Duration(days: 365)),
                      );
                      if (picked != null) setState(() => _date = picked);
                    },
                    child: InputDecorator(
                      decoration: InputDecoration(
                        labelText:
                            widget.isArabic ? 'التاريخ' : 'Date',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        prefixIcon: const Icon(Icons.calendar_today),
                      ),
                      child: Text('${_date.day}/${_date.month}/${_date.year}'),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Time picker
                  InkWell(
                    onTap: () async {
                      final picked = await showTimePicker(
                        context: context,
                        initialTime: _time,
                      );
                      if (picked != null) setState(() => _time = picked);
                    },
                    child: InputDecorator(
                      decoration: InputDecoration(
                        labelText:
                            widget.isArabic ? 'الوقت' : 'Time',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        prefixIcon: const Icon(Icons.access_time),
                      ),
                      child: Text(_time.format(context)),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Duration and water amount
                  Row(
                    children: [
                      Expanded(
                        child: TextFormField(
                          controller: _durationController,
                          keyboardType: TextInputType.number,
                          decoration: InputDecoration(
                            labelText: widget.isArabic
                                ? 'المدة (دقيقة)'
                                : 'Duration (min)',
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            prefixIcon: const Icon(Icons.timer),
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: TextFormField(
                          controller: _waterController,
                          keyboardType: TextInputType.number,
                          decoration: InputDecoration(
                            labelText: widget.isArabic
                                ? 'المياه (لتر)'
                                : 'Water (L)',
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            prefixIcon: const Icon(Icons.water_drop),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Notes
                  TextFormField(
                    controller: _notesController,
                    maxLines: 2,
                    decoration: InputDecoration(
                      labelText:
                          widget.isArabic ? 'ملاحظات' : 'Notes',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      prefixIcon: const Icon(Icons.note),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(
                      widget.isArabic
                          ? 'تم إضافة حدث الري'
                          : 'Irrigation event added',
                    ),
                    backgroundColor: SahoolColors.forestGreen,
                  ),
                );
              },
              icon: const Icon(Icons.save),
              label: Text(
                widget.isArabic ? 'حفظ' : 'Save',
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
}
