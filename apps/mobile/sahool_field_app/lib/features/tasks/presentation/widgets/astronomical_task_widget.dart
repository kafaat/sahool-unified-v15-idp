/// SAHOOL Astronomical Task Suggestions Widget
/// ويدجت اقتراحات المهام الفلكية
///
/// عرض أفضل الأيام للأنشطة الزراعية بناءً على التقويم الفلكي اليمني
/// مع إمكانية إنشاء مهام مباشرة من الأيام المقترحة

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

import '../../../astronomical/models/astronomical_models.dart';
import '../../../astronomical/providers/astronomical_providers.dart';
import '../../domain/entities/task.dart';
import '../create_task_screen.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// مزودات الحالة - State Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// مزود النشاط المحدد في ويدجت المهام الفلكية
final astronomicalTaskActivityProvider = StateProvider<String>((ref) => 'زراعة');

/// مزود اليوم المحدد
final selectedAstroDayProvider = StateProvider<BestDay?>((ref) => null);

/// مزود عرض التقويم أو القائمة
final astroViewModeProvider = StateProvider<AstroViewMode>((ref) => AstroViewMode.calendar);

/// مزود التخزين المؤقت للبيانات الفلكية
final astronomicalCacheProvider = FutureProvider.family<BestDaysResult?, String>((ref, activity) async {
  try {
    // محاولة جلب من الخادم أولاً
    final result = await ref.watch(
      bestDaysProvider(BestDaysParams(activity: activity, days: 30)),
    ).future;

    // حفظ في التخزين المؤقت
    await _saveToCache(activity, result);
    return result;
  } catch (e) {
    // في حالة الفشل، محاولة القراءة من التخزين المؤقت
    return await _loadFromCache(activity);
  }
});

// ═══════════════════════════════════════════════════════════════════════════════
// دوال التخزين المؤقت - Caching Functions
// ═══════════════════════════════════════════════════════════════════════════════

Future<void> _saveToCache(String activity, BestDaysResult result) async {
  try {
    final prefs = await SharedPreferences.getInstance();
    final key = 'astronomical_data_$activity';
    final data = {
      'result': result.toJson(),
      'timestamp': DateTime.now().toIso8601String(),
    };
    await prefs.setString(key, jsonEncode(data));
  } catch (e) {
    debugPrint('خطأ في حفظ البيانات الفلكية: $e');
  }
}

Future<BestDaysResult?> _loadFromCache(String activity) async {
  try {
    final prefs = await SharedPreferences.getInstance();
    final key = 'astronomical_data_$activity';
    final cached = prefs.getString(key);

    if (cached == null) return null;

    final data = jsonDecode(cached) as Map<String, dynamic>;
    final timestamp = DateTime.parse(data['timestamp'] as String);

    // التحقق من صلاحية البيانات (7 أيام)
    if (DateTime.now().difference(timestamp).inDays > 7) {
      return null;
    }

    return BestDaysResult.fromJson(data['result'] as Map<String, dynamic>);
  } catch (e) {
    debugPrint('خطأ في قراءة البيانات المخزنة: $e');
    return null;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// أنواع العرض - View Modes
// ═══════════════════════════════════════════════════════════════════════════════

enum AstroViewMode {
  calendar('تقويم', Icons.calendar_month),
  list('قائمة', Icons.list);

  final String label;
  final IconData icon;
  const AstroViewMode(this.label, this.icon);
}

// ═══════════════════════════════════════════════════════════════════════════════
// الويدجت الرئيسي - Main Widget
// ═══════════════════════════════════════════════════════════════════════════════

/// ويدجت اقتراحات المهام الفلكية
class AstronomicalTaskWidget extends ConsumerWidget {
  final String? fieldId;
  final String? fieldName;

  const AstronomicalTaskWidget({
    super.key,
    this.fieldId,
    this.fieldName,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedActivity = ref.watch(astronomicalTaskActivityProvider);
    final viewMode = ref.watch(astroViewModeProvider);
    final cacheAsync = ref.watch(astronomicalCacheProvider(selectedActivity));

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Container(
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surface,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // الرأس
            _buildHeader(context, ref, selectedActivity, viewMode),

            // اختيار النشاط
            _buildActivitySelector(context, ref, selectedActivity),

            // المحتوى
            Expanded(
              child: cacheAsync.when(
                data: (result) {
                  if (result == null || result.bestDays.isEmpty) {
                    return _buildEmptyState(context);
                  }

                  return viewMode == AstroViewMode.calendar
                      ? _buildCalendarView(context, ref, result)
                      : _buildListView(context, ref, result);
                },
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (error, stack) => _buildErrorState(context, error.toString()),
              ),
            ),

            // زر إنشاء المهمة
            _buildCreateTaskButton(context, ref),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context, WidgetRef ref, String activity, AstroViewMode viewMode) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            theme.colorScheme.primary,
            theme.colorScheme.primary.withOpacity(0.8),
          ],
        ),
        borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        children: [
          // شريط السحب
          Container(
            width: 40,
            height: 4,
            margin: const EdgeInsets.only(bottom: 12),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.5),
              borderRadius: BorderRadius.circular(2),
            ),
          ),

          // العنوان
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.auto_awesome,
                  color: Colors.white,
                  size: 24,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'التقويم الفلكي للمهام',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      'أفضل أيام $activity حسب المنازل القمرية',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.9),
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ),

              // تبديل العرض
              IconButton(
                onPressed: () {
                  ref.read(astroViewModeProvider.notifier).state =
                      viewMode == AstroViewMode.calendar
                          ? AstroViewMode.list
                          : AstroViewMode.calendar;
                },
                icon: Icon(
                  viewMode == AstroViewMode.calendar
                      ? Icons.list
                      : Icons.calendar_month,
                  color: Colors.white,
                ),
                tooltip: viewMode == AstroViewMode.calendar ? 'عرض القائمة' : 'عرض التقويم',
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildActivitySelector(BuildContext context, WidgetRef ref, String selectedActivity) {
    const activities = [
      {'label': 'زراعة', 'icon': Icons.park},
      {'label': 'ري', 'icon': Icons.water_drop},
      {'label': 'حصاد', 'icon': Icons.agriculture},
      {'label': 'تسميد', 'icon': Icons.eco},
    ];

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: activities.map((activity) {
            final isSelected = activity['label'] == selectedActivity;

            return Padding(
              padding: const EdgeInsets.only(left: 8),
              child: FilterChip(
                selected: isSelected,
                label: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      activity['icon'] as IconData,
                      size: 18,
                      color: isSelected
                          ? Theme.of(context).colorScheme.onPrimary
                          : Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(width: 6),
                    Text(activity['label'] as String),
                  ],
                ),
                onSelected: (_) {
                  ref.read(astronomicalTaskActivityProvider.notifier).state =
                      activity['label'] as String;
                  ref.read(selectedAstroDayProvider.notifier).state = null;
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
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildCalendarView(BuildContext context, WidgetRef ref, BestDaysResult result) {
    final selectedDay = ref.watch(selectedAstroDayProvider);

    return Column(
      children: [
        // التقويم
        Expanded(
          flex: 2,
          child: _CalendarGrid(
            bestDays: result.bestDays,
            selectedDay: selectedDay,
            onDaySelected: (day) {
              ref.read(selectedAstroDayProvider.notifier).state = day;
            },
          ),
        ),

        // تفاصيل اليوم المحدد
        if (selectedDay != null)
          Expanded(
            flex: 1,
            child: _DayDetailsCard(day: selectedDay),
          ),
      ],
    );
  }

  Widget _buildListView(BuildContext context, WidgetRef ref, BestDaysResult result) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: result.bestDays.length,
      itemBuilder: (context, index) {
        final day = result.bestDays[index];
        final isSelected = ref.watch(selectedAstroDayProvider) == day;

        return _DayListTile(
          day: day,
          rank: index + 1,
          isSelected: isSelected,
          onTap: () {
            ref.read(selectedAstroDayProvider.notifier).state = day;
          },
        );
      },
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.event_busy,
              size: 80,
              color: Theme.of(context).colorScheme.onSurfaceVariant.withOpacity(0.5),
            ),
            const SizedBox(height: 16),
            Text(
              'لا توجد أيام مناسبة',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'جرب نشاط آخر أو تحقق من الاتصال بالإنترنت',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState(BuildContext context, String error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.cloud_off,
              size: 80,
              color: Theme.of(context).colorScheme.error.withOpacity(0.5),
            ),
            const SizedBox(height: 16),
            Text(
              'خطأ في تحميل البيانات',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                color: Theme.of(context).colorScheme.error,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'يتم عرض البيانات المخزنة مؤقتاً',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCreateTaskButton(BuildContext context, WidgetRef ref) {
    final selectedDay = ref.watch(selectedAstroDayProvider);
    final selectedActivity = ref.watch(astronomicalTaskActivityProvider);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        top: false,
        child: SizedBox(
          width: double.infinity,
          height: 50,
          child: ElevatedButton.icon(
            onPressed: selectedDay != null
                ? () => _createTaskFromDay(context, ref, selectedDay, selectedActivity)
                : null,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF367C2B),
              disabledBackgroundColor: Colors.grey.shade300,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            icon: const Icon(Icons.add_task, color: Colors.white),
            label: Text(
              selectedDay != null
                  ? 'إنشاء مهمة ${_formatDate(selectedDay.date)}'
                  : 'اختر يوماً لإنشاء المهمة',
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _createTaskFromDay(
    BuildContext context,
    WidgetRef ref,
    BestDay day,
    String activity,
  ) async {
    // تحليل التاريخ
    final DateTime taskDate;
    try {
      taskDate = DateFormat('yyyy-MM-dd').parse(day.date);
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('خطأ في قراءة التاريخ: ${day.date}'),
            backgroundColor: Colors.red,
          ),
        );
      }
      return;
    }

    // الانتقال لشاشة إنشاء المهمة
    if (context.mounted) {
      final result = await Navigator.push<bool>(
        context,
        MaterialPageRoute(
          builder: (context) => CreateTaskScreen(
            fieldId: fieldId,
            fieldName: fieldName,
          ),
        ),
      );

      if (result == true && context.mounted) {
        // إغلاق الويدجت بعد الإنشاء الناجح
        Navigator.pop(context);

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('تم إنشاء مهمة $activity في ${_formatDate(day.date)}'),
            backgroundColor: const Color(0xFF367C2B),
            action: SnackBarAction(
              label: 'عرض',
              textColor: Colors.white,
              onPressed: () {
                // يمكن إضافة التنقل لشاشة المهام هنا
              },
            ),
          ),
        );
      }
    }
  }

  String _formatDate(String dateStr) {
    try {
      final date = DateFormat('yyyy-MM-dd').parse(dateStr);
      return DateFormat('d MMMM', 'ar').format(date);
    } catch (e) {
      return dateStr;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// شبكة التقويم - Calendar Grid
// ═══════════════════════════════════════════════════════════════════════════════

class _CalendarGrid extends StatelessWidget {
  final List<BestDay> bestDays;
  final BestDay? selectedDay;
  final ValueChanged<BestDay> onDaySelected;

  const _CalendarGrid({
    required this.bestDays,
    required this.selectedDay,
    required this.onDaySelected,
  });

  @override
  Widget build(BuildContext context) {
    // تجميع الأيام حسب الأسبوع
    final weeks = _groupByWeeks(bestDays);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // أسماء الأيام
          _buildWeekdayHeaders(context),
          const SizedBox(height: 12),

          // الأسابيع
          ...weeks.map((week) => _buildWeekRow(context, week)),

          // المفتاح
          const SizedBox(height: 16),
          _buildLegend(context),
        ],
      ),
    );
  }

  Widget _buildWeekdayHeaders(BuildContext context) {
    const weekdays = ['أحد', 'اثنين', 'ثلاثاء', 'أربعاء', 'خميس', 'جمعة', 'سبت'];

    return Row(
      children: weekdays.map((day) {
        return Expanded(
          child: Center(
            child: Text(
              day,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildWeekRow(BuildContext context, List<BestDay?> week) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: week.map((day) {
          if (day == null) {
            return const Expanded(child: SizedBox(height: 48));
          }

          final isSelected = selectedDay?.date == day.date;
          final scoreColor = _getScoreColor(day.score);

          return Expanded(
            child: GestureDetector(
              onTap: () => onDaySelected(day),
              child: Container(
                height: 48,
                margin: const EdgeInsets.all(2),
                decoration: BoxDecoration(
                  color: isSelected
                      ? scoreColor
                      : scoreColor.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(8),
                  border: isSelected
                      ? Border.all(color: scoreColor, width: 2)
                      : null,
                ),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        _getDayNumber(day.date),
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: isSelected ? Colors.white : Colors.black87,
                        ),
                      ),
                      Text(
                        '${day.score}',
                        style: TextStyle(
                          fontSize: 10,
                          color: isSelected ? Colors.white : Colors.black54,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildLegend(BuildContext context) {
    return Card(
      elevation: 0,
      color: Theme.of(context).colorScheme.surfaceVariant.withOpacity(0.3),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _buildLegendItem(context, 'ممتاز', _getScoreColor(95)),
            _buildLegendItem(context, 'جيد', _getScoreColor(85)),
            _buildLegendItem(context, 'مقبول', _getScoreColor(75)),
            _buildLegendItem(context, 'متوسط', _getScoreColor(65)),
          ],
        ),
      ),
    );
  }

  Widget _buildLegendItem(BuildContext context, String label, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 16,
          height: 16,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(4),
          ),
        ),
        const SizedBox(width: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }

  List<List<BestDay?>> _groupByWeeks(List<BestDay> days) {
    if (days.isEmpty) return [];

    final weeks = <List<BestDay?>>[];
    var currentWeek = <BestDay?>[];

    // البدء من أول يوم في الشهر
    final firstDay = DateFormat('yyyy-MM-dd').parse(days.first.date);
    final startOfMonth = DateTime(firstDay.year, firstDay.month, 1);
    final firstWeekday = startOfMonth.weekday % 7; // 0 = Sunday

    // ملء الأيام الفارغة في بداية الأسبوع الأول
    for (var i = 0; i < firstWeekday; i++) {
      currentWeek.add(null);
    }

    for (final day in days) {
      final date = DateFormat('yyyy-MM-dd').parse(day.date);
      final weekday = date.weekday % 7;

      if (currentWeek.length == 7) {
        weeks.add(List.from(currentWeek));
        currentWeek.clear();
      }

      currentWeek.add(day);
    }

    // إضافة الأسبوع الأخير
    if (currentWeek.isNotEmpty) {
      while (currentWeek.length < 7) {
        currentWeek.add(null);
      }
      weeks.add(currentWeek);
    }

    return weeks;
  }

  Color _getScoreColor(int score) {
    if (score >= 90) return Colors.green.shade700;
    if (score >= 80) return Colors.green;
    if (score >= 70) return Colors.lightGreen;
    if (score >= 60) return Colors.lime.shade600;
    return Colors.orange;
  }

  String _getDayNumber(String dateStr) {
    try {
      final date = DateFormat('yyyy-MM-dd').parse(dateStr);
      return '${date.day}';
    } catch (e) {
      return '?';
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// بطاقة تفاصيل اليوم - Day Details Card
// ═══════════════════════════════════════════════════════════════════════════════

class _DayDetailsCard extends StatelessWidget {
  final BestDay day;

  const _DayDetailsCard({required this.day});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scoreColor = _getScoreColor(day.score);

    return Container(
      margin: const EdgeInsets.all(16),
      child: Card(
        elevation: 4,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // التاريخ والدرجة
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _formatDate(day.date),
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          day.hijriDate,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: scoreColor.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: scoreColor, width: 2),
                    ),
                    child: Column(
                      children: [
                        Text(
                          '${day.score}',
                          style: TextStyle(
                            color: scoreColor,
                            fontWeight: FontWeight.bold,
                            fontSize: 24,
                          ),
                        ),
                        Text(
                          'درجة',
                          style: TextStyle(
                            color: scoreColor,
                            fontSize: 11,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 16),
              const Divider(),
              const SizedBox(height: 12),

              // تفاصيل فلكية
              _buildDetailRow(
                context,
                Icons.nightlight_round,
                'طور القمر',
                day.moonPhase,
                Colors.amber.shade600,
              ),
              const SizedBox(height: 8),
              _buildDetailRow(
                context,
                Icons.star,
                'المنزلة القمرية',
                day.lunarMansion,
                Colors.purple.shade400,
              ),
              const SizedBox(height: 12),
              const Divider(),
              const SizedBox(height: 12),

              // السبب
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(
                    Icons.info_outline,
                    size: 20,
                    color: theme.colorScheme.primary,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      day.reason,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailRow(
    BuildContext context,
    IconData icon,
    String label,
    String value,
    Color color,
  ) {
    return Row(
      children: [
        Icon(icon, size: 20, color: color),
        const SizedBox(width: 8),
        Text(
          '$label: ',
          style: TextStyle(
            fontSize: 13,
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ],
    );
  }

  Color _getScoreColor(int score) {
    if (score >= 90) return Colors.green.shade700;
    if (score >= 80) return Colors.green;
    if (score >= 70) return Colors.lightGreen;
    if (score >= 60) return Colors.lime.shade600;
    return Colors.orange;
  }

  String _formatDate(String dateStr) {
    try {
      final date = DateFormat('yyyy-MM-dd').parse(dateStr);
      return DateFormat('EEEE، d MMMM yyyy', 'ar').format(date);
    } catch (e) {
      return dateStr;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// عنصر القائمة - List Tile
// ═══════════════════════════════════════════════════════════════════════════════

class _DayListTile extends StatelessWidget {
  final BestDay day;
  final int rank;
  final bool isSelected;
  final VoidCallback onTap;

  const _DayListTile({
    required this.day,
    required this.rank,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scoreColor = _getScoreColor(day.score);
    final rankColor = _getRankColor(rank);

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      elevation: isSelected ? 4 : 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: isSelected
            ? BorderSide(color: scoreColor, width: 2)
            : BorderSide.none,
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              // الترتيب
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: rankColor.withOpacity(0.2),
                  shape: BoxShape.circle,
                  border: Border.all(color: rankColor, width: 2),
                ),
                child: Center(
                  child: Text(
                    '$rank',
                    style: TextStyle(
                      color: rankColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 12),

              // التفاصيل
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          _formatDate(day.date),
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 15,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          day.hijriDate,
                          style: TextStyle(
                            color: theme.colorScheme.onSurfaceVariant,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        Icon(
                          Icons.nightlight_round,
                          size: 14,
                          color: Colors.amber.shade600,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          day.moonPhase,
                          style: theme.textTheme.labelSmall,
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      day.reason,
                      style: TextStyle(
                        color: theme.colorScheme.onSurfaceVariant,
                        fontSize: 12,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),

              // الدرجة
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: scoreColor.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: scoreColor, width: 1.5),
                ),
                child: Column(
                  children: [
                    Text(
                      '${day.score}',
                      style: TextStyle(
                        color: scoreColor,
                        fontWeight: FontWeight.bold,
                        fontSize: 20,
                      ),
                    ),
                    Text(
                      'درجة',
                      style: TextStyle(
                        color: scoreColor,
                        fontSize: 10,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Color _getScoreColor(int score) {
    if (score >= 90) return Colors.green.shade700;
    if (score >= 80) return Colors.green;
    if (score >= 70) return Colors.lightGreen;
    if (score >= 60) return Colors.lime.shade600;
    return Colors.orange;
  }

  Color _getRankColor(int rank) {
    switch (rank) {
      case 1:
        return Colors.amber.shade700;
      case 2:
        return Colors.grey.shade500;
      case 3:
        return Colors.brown.shade400;
      default:
        return Colors.blueGrey;
    }
  }

  String _formatDate(String dateStr) {
    try {
      final date = DateFormat('yyyy-MM-dd').parse(dateStr);
      return DateFormat('d MMM', 'ar').format(date);
    } catch (e) {
      return dateStr;
    }
  }
}
