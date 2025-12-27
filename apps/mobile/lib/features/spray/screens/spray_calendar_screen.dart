/// Spray Calendar Screen - شاشة تقويم الرش
/// عرض نوافذ الرش في تقويم شهري
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:table_calendar/table_calendar.dart';

import '../models/spray_models.dart';
import '../providers/spray_provider.dart';
import '../widgets/spray_window_card.dart';

class SprayCalendarScreen extends ConsumerStatefulWidget {
  final String fieldId;

  const SprayCalendarScreen({
    Key? key,
    required this.fieldId,
  }) : super(key: key);

  @override
  ConsumerState<SprayCalendarScreen> createState() => _SprayCalendarScreenState();
}

class _SprayCalendarScreenState extends ConsumerState<SprayCalendarScreen> {
  final String _locale = 'ar'; // TODO: Get from app locale
  DateTime _focusedDay = DateTime.now();
  DateTime? _selectedDay;
  List<SprayWindow> _allWindows = [];

  @override
  void initState() {
    super.initState();
    _selectedDay = _focusedDay;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isArabic = _locale == 'ar';

    // Calculate days from now to end of next month
    final now = DateTime.now();
    final endOfNextMonth = DateTime(now.year, now.month + 2, 0);
    final daysToFetch = endOfNextMonth.difference(now).inDays;

    final windowsAsync = ref.watch(sprayWindowsProvider(
      SprayWindowParams(fieldId: widget.fieldId, days: daysToFetch),
    ));

    return Scaffold(
      appBar: AppBar(
        title: Text(isArabic ? 'تقويم الرش' : 'Spray Calendar'),
        actions: [
          IconButton(
            icon: const Icon(Icons.info_outline),
            onPressed: () => _showLegend(theme, isArabic),
          ),
        ],
      ),
      body: windowsAsync.when(
        data: (windows) {
          _allWindows = windows;
          return Column(
            children: [
              // Calendar
              _buildCalendar(theme, isArabic),
              const Divider(),
              // Selected Day Windows
              Expanded(
                child: _buildSelectedDayWindows(theme, isArabic),
              ),
            ],
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Padding(
            padding: const EdgeInsets.all(32.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.error_outline,
                  size: 64,
                  color: theme.colorScheme.error,
                ),
                const SizedBox(height: 16),
                Text(
                  isArabic ? 'فشل في جلب نوافذ الرش' : 'Failed to load spray windows',
                  style: theme.textTheme.titleMedium,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                Text(
                  error.toString(),
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurface.withOpacity(0.6),
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () => ref.invalidate(sprayWindowsProvider),
                  child: Text(isArabic ? 'إعادة المحاولة' : 'Retry'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildCalendar(ThemeData theme, bool isArabic) {
    return Card(
      margin: const EdgeInsets.all(16),
      child: TableCalendar(
        firstDay: DateTime.now(),
        lastDay: DateTime.now().add(const Duration(days: 90)),
        focusedDay: _focusedDay,
        selectedDayPredicate: (day) => isSameDay(_selectedDay, day),
        calendarFormat: CalendarFormat.month,
        locale: isArabic ? 'ar' : 'en',
        startingDayOfWeek: StartingDayOfWeek.saturday,
        headerStyle: HeaderStyle(
          formatButtonVisible: false,
          titleCentered: true,
          titleTextStyle: theme.textTheme.titleLarge!.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        calendarStyle: CalendarStyle(
          todayDecoration: BoxDecoration(
            color: theme.colorScheme.primary.withOpacity(0.5),
            shape: BoxShape.circle,
          ),
          selectedDecoration: BoxDecoration(
            color: theme.colorScheme.primary,
            shape: BoxShape.circle,
          ),
          markerDecoration: BoxDecoration(
            color: theme.colorScheme.secondary,
            shape: BoxShape.circle,
          ),
          markersMaxCount: 1,
        ),
        onDaySelected: (selectedDay, focusedDay) {
          setState(() {
            _selectedDay = selectedDay;
            _focusedDay = focusedDay;
          });
        },
        onPageChanged: (focusedDay) {
          _focusedDay = focusedDay;
        },
        eventLoader: (day) => _getEventsForDay(day),
        calendarBuilders: CalendarBuilders(
          markerBuilder: (context, date, events) {
            if (events.isEmpty) return null;

            final window = events.first as SprayWindow;
            return Positioned(
              bottom: 1,
              child: Container(
                width: 6,
                height: 6,
                decoration: BoxDecoration(
                  color: _getStatusColor(window.status),
                  shape: BoxShape.circle,
                ),
              ),
            );
          },
          defaultBuilder: (context, date, _) {
            final dayWindows = _getWindowsForDay(date);
            if (dayWindows.isEmpty) return null;

            final bestStatus = _getBestStatus(dayWindows);
            return Container(
              margin: const EdgeInsets.all(4),
              decoration: BoxDecoration(
                color: _getStatusColor(bestStatus).withOpacity(0.1),
                border: Border.all(
                  color: _getStatusColor(bestStatus),
                  width: 1,
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Center(
                child: Text(
                  '${date.day}',
                  style: TextStyle(
                    color: theme.colorScheme.onSurface,
                  ),
                ),
              ),
            );
          },
          selectedBuilder: (context, date, _) {
            final dayWindows = _getWindowsForDay(date);
            final bestStatus = dayWindows.isNotEmpty
                ? _getBestStatus(dayWindows)
                : SprayWindowStatus.caution;

            return Container(
              margin: const EdgeInsets.all(4),
              decoration: BoxDecoration(
                color: _getStatusColor(bestStatus),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Center(
                child: Text(
                  '${date.day}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            );
          },
          todayBuilder: (context, date, _) {
            final dayWindows = _getWindowsForDay(date);
            if (dayWindows.isEmpty) {
              return Container(
                margin: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  border: Border.all(
                    color: theme.colorScheme.primary,
                    width: 2,
                  ),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Center(
                  child: Text(
                    '${date.day}',
                    style: TextStyle(
                      color: theme.colorScheme.primary,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              );
            }

            final bestStatus = _getBestStatus(dayWindows);
            return Container(
              margin: const EdgeInsets.all(4),
              decoration: BoxDecoration(
                color: _getStatusColor(bestStatus).withOpacity(0.2),
                border: Border.all(
                  color: theme.colorScheme.primary,
                  width: 2,
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Center(
                child: Text(
                  '${date.day}',
                  style: TextStyle(
                    color: theme.colorScheme.primary,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildSelectedDayWindows(ThemeData theme, bool isArabic) {
    if (_selectedDay == null) {
      return Center(
        child: Text(
          isArabic ? 'اختر يوماً لعرض نوافذ الرش' : 'Select a day to view spray windows',
          style: theme.textTheme.bodyMedium?.copyWith(
            color: theme.colorScheme.onSurface.withOpacity(0.6),
          ),
        ),
      );
    }

    final dayWindows = _getWindowsForDay(_selectedDay!);

    if (dayWindows.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.event_busy,
              size: 64,
              color: theme.colorScheme.onSurface.withOpacity(0.3),
            ),
            const SizedBox(height: 16),
            Text(
              isArabic ? 'لا توجد نوافذ رش في هذا اليوم' : 'No spray windows for this day',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurface.withOpacity(0.6),
              ),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: dayWindows.length,
      itemBuilder: (context, index) {
        final window = dayWindows[index];
        return SprayWindowTimelineItem(
          window: window,
          locale: _locale,
          onTap: () => _showWindowDetails(window, theme, isArabic),
        );
      },
    );
  }

  List<SprayWindow> _getEventsForDay(DateTime day) {
    return _getWindowsForDay(day);
  }

  List<SprayWindow> _getWindowsForDay(DateTime day) {
    return _allWindows.where((window) {
      final windowDate = DateTime(
        window.startTime.year,
        window.startTime.month,
        window.startTime.day,
      );
      final targetDate = DateTime(day.year, day.month, day.day);
      return isSameDay(windowDate, targetDate);
    }).toList();
  }

  SprayWindowStatus _getBestStatus(List<SprayWindow> windows) {
    if (windows.any((w) => w.status == SprayWindowStatus.optimal)) {
      return SprayWindowStatus.optimal;
    }
    if (windows.any((w) => w.status == SprayWindowStatus.caution)) {
      return SprayWindowStatus.caution;
    }
    return SprayWindowStatus.avoid;
  }

  Color _getStatusColor(SprayWindowStatus status) {
    switch (status) {
      case SprayWindowStatus.optimal:
        return Colors.green;
      case SprayWindowStatus.caution:
        return Colors.orange;
      case SprayWindowStatus.avoid:
        return Colors.red;
    }
  }

  void _showWindowDetails(SprayWindow window, ThemeData theme, bool isArabic) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        minChildSize: 0.5,
        maxChildSize: 0.9,
        expand: false,
        builder: (context, scrollController) => SingleChildScrollView(
          controller: scrollController,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Center(
                  child: Container(
                    width: 40,
                    height: 4,
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.onSurface.withOpacity(0.3),
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
                Text(
                  isArabic ? 'تفاصيل نافذة الرش' : 'Spray Window Details',
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16),
                SprayWindowCard(window: window, locale: _locale),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showLegend(ThemeData theme, bool isArabic) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(isArabic ? 'دليل الألوان' : 'Color Legend'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildLegendItem(
              Colors.green,
              isArabic ? 'مثالي للرش' : 'Optimal for spraying',
            ),
            const SizedBox(height: 12),
            _buildLegendItem(
              Colors.orange,
              isArabic ? 'حذر - تحقق من الظروف' : 'Caution - check conditions',
            ),
            const SizedBox(height: 12),
            _buildLegendItem(
              Colors.red,
              isArabic ? 'تجنب الرش' : 'Avoid spraying',
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(isArabic ? 'إغلاق' : 'Close'),
          ),
        ],
      ),
    );
  }

  Widget _buildLegendItem(Color color, String label) {
    return Row(
      children: [
        Container(
          width: 24,
          height: 24,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(4),
          ),
        ),
        const SizedBox(width: 12),
        Text(label),
      ],
    );
  }
}
