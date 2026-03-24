import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/di/providers.dart';
import '../../../core/iam/iam_providers.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../field/domain/entities/field.dart';
import '../../tasks/domain/entities/task.dart';
import '../../tasks/providers/tasks_provider.dart';
import '../../weather/presentation/providers/weather_provider.dart';

/// SAHOOL Field Dashboard - لوحة القيادة الزراعية
/// تعرض المؤشرات الحيوية بأسلوب عدادات السيارة
class FieldDashboard extends ConsumerStatefulWidget {
  const FieldDashboard({super.key});

  @override
  ConsumerState<FieldDashboard> createState() => _FieldDashboardState();
}

class _FieldDashboardState extends ConsumerState<FieldDashboard> {
  void _navigateTo(BuildContext context, String route, {Map<String, dynamic>? arguments}) {
    Navigator.pushNamed(context, route, arguments: arguments);
  }

  @override
  Widget build(BuildContext context) {
    final tenant = ref.watch(currentTenantProvider);
    final tenantId = tenant?.id ?? 'default';
    final fieldsAsync = ref.watch(fieldsStreamProvider(tenantId));

    return Scaffold(
      backgroundColor: SahoolColors.background,
      appBar: AppBar(
        title: const Text('لوحة القيادة'),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () => _navigateTo(context, '/notifications'),
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.invalidate(fieldsStreamProvider(tenantId));
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('جاري تحديث البيانات...'),
                  duration: Duration(seconds: 1),
                ),
              );
            },
          ),
        ],
      ),
      body: fieldsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, size: 48, color: Colors.grey[400]),
              const SizedBox(height: 16),
              Text('فشل تحميل البيانات', style: TextStyle(color: Colors.grey[600])),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: () => ref.invalidate(fieldsStreamProvider(tenantId)),
                icon: const Icon(Icons.refresh),
                label: const Text('إعادة المحاولة'),
              ),
            ],
          ),
        ),
        data: (fields) => _buildDashboardContent(fields),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _navigateTo(context, '/task-create'),
        icon: const Icon(Icons.add),
        label: const Text('مهمة جديدة'),
      ),
    );
  }

  Widget _buildDashboardContent(List<Field> fields) {
    // Compute aggregate metrics from real field data
    final avgNdvi = fields.isEmpty
        ? 0.0
        : fields.map((f) => f.ndviCurrent ?? 0.0).reduce((a, b) => a + b) / fields.length;
    final avgSoilMoisture = fields.isEmpty ? 0.0 : _estimateAvgSoilMoisture(fields);
    final nitrogenStatus = _getNitrogenStatus(avgNdvi);
    final healthLabel = _getHealthLabel(avgNdvi);
    final healthPercent = (avgNdvi * 100).round();
    final tasksCount = fields.fold<int>(0, (sum, f) => sum + f.pendingTasks);

    return RefreshIndicator(
      onRefresh: () async {
        final tenant = ref.read(currentTenantProvider);
        final tenantId = tenant?.id ?? 'default';
        ref.invalidate(fieldsStreamProvider(tenantId));
      },
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // بطاقة الترحيب
          _buildWelcomeCard(tasksCount),

          const SizedBox(height: 20),

          // بطاقة الحالة الرئيسية (NDVI)
          _buildHealthCard(avgNdvi, healthLabel, healthPercent),

          const SizedBox(height: 20),

          // عنوان المؤشرات
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'المؤشرات الحيوية',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
              ),
              TextButton.icon(
                onPressed: () => _navigateTo(context, '/fields'),
                icon: const Icon(Icons.arrow_forward, size: 18),
                label: const Text('عرض الكل'),
              ),
            ],
          ),

          const SizedBox(height: 12),

          // شبكة العدادات
          _buildMetricsGrid(avgSoilMoisture, nitrogenStatus),

          const SizedBox(height: 20),

          // التنبيهات العاجلة
          _buildAlertsSection(context, fields),

          const SizedBox(height: 20),

          // المهام القادمة
          _buildTasksSection(),

          const SizedBox(height: 20),

          // الطقس الأسبوعي
          _buildWeatherForecast(),

          const SizedBox(height: 100), // مسافة للـ FAB
        ],
      ),
    );
  }

  /// Estimate average soil moisture from NDVI (proxy when no sensor data)
  double _estimateAvgSoilMoisture(List<Field> fields) {
    // Use NDVI as a proxy for soil moisture when direct sensor data is unavailable
    final avgNdvi = fields.map((f) => f.ndviCurrent ?? 0.0).reduce((a, b) => a + b) / fields.length;
    return (avgNdvi * 60).clamp(0, 100); // rough proxy
  }

  String _getNitrogenStatus(double avgNdvi) {
    if (avgNdvi >= 0.6) return 'جيد';
    if (avgNdvi >= 0.4) return 'متوسط';
    return 'منخفض';
  }

  String _getHealthLabel(double avgNdvi) {
    if (avgNdvi >= 0.7) return 'ممتازة';
    if (avgNdvi >= 0.5) return 'جيدة';
    if (avgNdvi >= 0.3) return 'متوسطة';
    return 'ضعيفة';
  }

  /// بطاقة الترحيب
  Widget _buildWelcomeCard(int tasksCount) {
    final hour = DateTime.now().hour;
    String greeting;
    IconData greetingIcon;

    if (hour < 12) {
      greeting = 'صباح الخير';
      greetingIcon = Icons.wb_sunny;
    } else if (hour < 17) {
      greeting = 'مساء الخير';
      greetingIcon = Icons.wb_cloudy;
    } else {
      greeting = 'مساء الخير';
      greetingIcon = Icons.nights_stay;
    }

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: SahoolRadius.largeRadius,
        boxShadow: SahoolShadows.small,
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: SahoolColors.warning.withValues(alpha: 0.2),
              shape: BoxShape.circle,
            ),
            child: Icon(greetingIcon, color: Colors.orange[700], size: 28),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  greeting,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  tasksCount > 0 ? 'لديك $tasksCount مهام اليوم' : 'لا توجد مهام اليوم',
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: SahoolColors.success.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: const BoxDecoration(
                    color: SahoolColors.success,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 6),
                const Text(
                  'متصل',
                  style: TextStyle(
                    color: SahoolColors.success,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// بطاقة صحة المحصول الرئيسية
  Widget _buildHealthCard(double avgNdvi, String healthLabel, int healthPercent) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: SahoolColors.primaryGradient,
        borderRadius: SahoolRadius.xlargeRadius,
        boxShadow: SahoolShadows.colored(SahoolColors.primary),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.eco, color: Colors.white70, size: 20),
                    const SizedBox(width: 8),
                    Text(
                      'صحة المحصول',
                      style: TextStyle(color: Colors.white.withValues(alpha: 0.8), fontSize: 14),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  healthLabel,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.satellite_alt, color: Colors.white, size: 16),
                      const SizedBox(width: 6),
                      Text(
                        'NDVI: ${avgNdvi.toStringAsFixed(2)}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'آخر تحديث: الآن',
                  style: TextStyle(color: Colors.white.withValues(alpha: 0.6), fontSize: 12),
                ),
              ],
            ),
          ),
          // الدائرة التقدمية
          SizedBox(
            height: 100,
            width: 100,
            child: Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  height: 100,
                  width: 100,
                  child: CircularProgressIndicator(
                    value: avgNdvi.clamp(0.0, 1.0),
                    backgroundColor: Colors.white.withValues(alpha: 0.2),
                    valueColor: const AlwaysStoppedAnimation(Colors.white),
                    strokeWidth: 10,
                  ),
                ),
                Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      '$healthPercent%',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const Text(
                      'الصحة',
                      style: TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// شبكة المؤشرات
  Widget _buildMetricsGrid(double soilMoisture, String nitrogenStatus) {
    final showNitrogenWarning = nitrogenStatus == 'منخفض';

    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: 12,
      mainAxisSpacing: 12,
      childAspectRatio: 1.2,
      children: [
        _buildMetricCard(
          'رطوبة التربة',
          '${soilMoisture.round()}%',
          Icons.water_drop,
          SahoolColors.info,
          unit: '%',
        ),
        _buildMetricCard(
          'النيتروجين',
          nitrogenStatus,
          Icons.grass,
          showNitrogenWarning ? SahoolColors.warning : SahoolColors.success,
          showWarning: showNitrogenWarning,
        ),
        _buildMetricCard(
          'الطقس',
          '--',
          Icons.wb_sunny,
          Colors.amber,
          subtitle: 'جاري التحميل',
        ),
        _buildMetricCard(
          'التراكم الحراري',
          '--',
          Icons.thermostat,
          SahoolColors.danger,
          unit: 'GDD',
        ),
      ],
    );
  }

  Widget _buildMetricCard(
    String title,
    String value,
    IconData icon,
    Color color, {
    int? trend,
    String? unit,
    String? subtitle,
    bool showWarning = false,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: SahoolRadius.largeRadius,
        boxShadow: SahoolShadows.small,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, color: color, size: 24),
              ),
              if (showWarning)
                Container(
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    color: SahoolColors.warning.withValues(alpha: 0.2),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.warning_amber,
                    color: SahoolColors.warning,
                    size: 16,
                  ),
                ),
              if (trend != null)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: trend > 0
                        ? SahoolColors.success.withValues(alpha: 0.1)
                        : SahoolColors.danger.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        trend > 0 ? Icons.arrow_upward : Icons.arrow_downward,
                        size: 12,
                        color: trend > 0 ? SahoolColors.success : SahoolColors.danger,
                      ),
                      Text(
                        '${trend.abs()}%',
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          color: trend > 0 ? SahoolColors.success : SahoolColors.danger,
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),
          const Spacer(),
          Row(
            crossAxisAlignment: CrossAxisAlignment.baseline,
            textBaseline: TextBaseline.alphabetic,
            children: [
              Text(
                value,
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              if (unit != null)
                Text(
                  ' $unit',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            subtitle ?? title,
            style: TextStyle(
              color: Colors.grey[600],
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  /// قسم التنبيهات
  Widget _buildAlertsSection(BuildContext context, List<Field> fields) {
    final criticalFields = fields.where((f) => f.needsAttention).toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                const Text(
                  'التنبيهات',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: SahoolColors.danger,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    '${criticalFields.length}',
                    style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            TextButton(onPressed: () => _navigateTo(context, '/alerts'), child: const Text('عرض الكل')),
          ],
        ),
        const SizedBox(height: 12),
        if (criticalFields.isEmpty)
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: SahoolColors.success.withValues(alpha: 0.05),
              borderRadius: SahoolRadius.mediumRadius,
            ),
            child: const Row(
              children: [
                Icon(Icons.check_circle, color: SahoolColors.success),
                SizedBox(width: 12),
                Text('لا توجد تنبيهات حالياً'),
              ],
            ),
          )
        else
          ...criticalFields.take(3).map((field) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: _buildAlertItem(
                  field.name,
                  'NDVI: ${(field.ndviCurrent ?? 0).toStringAsFixed(2)} - يحتاج اهتمام',
                  Icons.eco,
                  field.healthStatus == FieldStatus.critical ? SahoolColors.danger : SahoolColors.warning,
                  'الآن',
                ),
              )),
      ],
    );
  }

  Widget _buildAlertItem(String title, String subtitle, IconData icon, Color color, String time) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: SahoolRadius.mediumRadius,
        border: Border.all(color: color.withValues(alpha: 0.3)),
        boxShadow: SahoolShadows.small,
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text(subtitle, style: TextStyle(color: Colors.grey[600], fontSize: 12)),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(time, style: TextStyle(color: Colors.grey[500], fontSize: 10)),
              const SizedBox(height: 8),
              Icon(Icons.chevron_left, color: Colors.grey[400]),
            ],
          ),
        ],
      ),
    );
  }

  /// قسم المهام - يعرض المهام من مزود المهام الحقيقي
  Widget _buildTasksSection() {
    final tasksAsync = ref.watch(tasksProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'المهام القادمة',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
        ),
        const SizedBox(height: 12),
        tasksAsync.when(
          loading: () => const Center(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
          ),
          error: (_, __) => _buildTaskItem('فشل تحميل المهام', 'اسحب للتحديث', Icons.error_outline, false),
          data: (tasks) {
            if (tasks.isEmpty) {
              return Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: SahoolColors.success.withValues(alpha: 0.05),
                  borderRadius: SahoolRadius.mediumRadius,
                ),
                child: const Row(
                  children: [
                    Icon(Icons.check_circle, color: SahoolColors.success),
                    SizedBox(width: 12),
                    Text('لا توجد مهام قادمة'),
                  ],
                ),
              );
            }
            return Column(
              children: tasks.take(5).map((task) {
                final completed = task.status == TaskStatus.done;
                return _buildTaskItem(
                  task.title,
                  completed ? 'تم' : _formatTaskTime(task.dueDate),
                  _inferTaskIcon(task.title),
                  completed,
                );
              }).toList(),
            );
          },
        ),
      ],
    );
  }

  /// Infer icon from task title keywords
  IconData _inferTaskIcon(String title) {
    final lower = title.toLowerCase();
    if (lower.contains('ري') || lower.contains('irrigation') || lower.contains('water')) return Icons.water_drop;
    if (lower.contains('آفة') || lower.contains('pest') || lower.contains('حشر')) return Icons.bug_report;
    if (lower.contains('سماد') || lower.contains('تسميد') || lower.contains('fertiliz')) return Icons.eco;
    if (lower.contains('حصاد') || lower.contains('harvest')) return Icons.agriculture;
    if (lower.contains('فحص') || lower.contains('inspect')) return Icons.search;
    return Icons.task_alt;
  }

  String _formatTaskTime(DateTime? date) {
    if (date == null) return '';
    final now = DateTime.now();
    final diff = date.difference(now);
    if (diff.isNegative) return 'متأخر';
    if (diff.inDays == 0) return 'اليوم ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
    if (diff.inDays == 1) return 'غداً ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
    return '${date.day}/${date.month}';
  }

  Widget _buildTaskItem(String title, String time, IconData icon, bool completed) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: completed ? SahoolColors.success.withValues(alpha: 0.05) : Colors.white,
        borderRadius: SahoolRadius.mediumRadius,
        boxShadow: SahoolShadows.small,
      ),
      child: Row(
        children: [
          Container(
            width: 24,
            height: 24,
            decoration: BoxDecoration(
              color: completed ? SahoolColors.success : Colors.transparent,
              shape: BoxShape.circle,
              border: Border.all(
                color: completed ? SahoolColors.success : Colors.grey[400]!,
                width: 2,
              ),
            ),
            child: completed ? const Icon(Icons.check, color: Colors.white, size: 16) : null,
          ),
          const SizedBox(width: 12),
          Icon(icon, color: completed ? Colors.grey[400] : SahoolColors.primary, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              title,
              style: TextStyle(
                decoration: completed ? TextDecoration.lineThrough : null,
                color: completed ? Colors.grey[500] : SahoolColors.textDark,
              ),
            ),
          ),
          Text(
            time,
            style: TextStyle(
              color: completed ? Colors.grey[400] : SahoolColors.textSecondary,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  /// توقعات الطقس - يعرض بيانات حقيقية من خدمة الطقس
  Widget _buildWeatherForecast() {
    final weatherState = ref.watch(weatherProvider);
    final forecast = weatherState.data?.daily;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'توقعات الطقس',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: SahoolRadius.largeRadius,
            boxShadow: SahoolShadows.small,
          ),
          child: weatherState.isLoading
              ? const Center(
                  child: Padding(
                    padding: EdgeInsets.all(16),
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                )
              : Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: forecast != null && forecast.isNotEmpty
                      ? forecast.take(5).map((day) {
                          return _buildWeatherDay(
                            day.dayName,
                            _getWeatherIcon(day.condition),
                            '${day.tempMax.round()}°',
                            '${day.tempMin.round()}°',
                          );
                        }).toList()
                      : [
                          _buildWeatherDay('اليوم', Icons.wb_sunny, '--', '--'),
                          _buildWeatherDay('غداً', Icons.wb_cloudy, '--', '--'),
                          _buildWeatherDay('بعد غد', Icons.wb_sunny, '--', '--'),
                        ],
                ),
        ),
      ],
    );
  }

  IconData _getWeatherIcon(String? condition) {
    switch (condition?.toLowerCase()) {
      case 'sunny':
      case 'clear':
        return Icons.wb_sunny;
      case 'cloudy':
      case 'partly_cloudy':
        return Icons.wb_cloudy;
      case 'rain':
      case 'rainy':
        return Icons.grain;
      case 'storm':
      case 'thunderstorm':
        return Icons.thunderstorm;
      default:
        return Icons.wb_sunny;
    }
  }

  Widget _buildWeatherDay(String day, IconData icon, String high, String low) {
    return Column(
      children: [
        Text(day, style: TextStyle(color: Colors.grey[600], fontSize: 12)),
        const SizedBox(height: 8),
        Icon(icon, color: Colors.amber, size: 28),
        const SizedBox(height: 8),
        Text(high, style: const TextStyle(fontWeight: FontWeight.bold)),
        Text(low, style: TextStyle(color: Colors.grey[500], fontSize: 12)),
      ],
    );
  }
}
